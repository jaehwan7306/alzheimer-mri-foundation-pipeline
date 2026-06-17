from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import StratifiedKFold, train_test_split
from torch.utils.data import DataLoader

from .metrics import aggregate_patient_predictions, calculate_metrics, choose_sensitivity_first_threshold
from .models import AdapterProbe, CachedFeatureDataset, indices_for_patient_ids


def seed_everything(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def evaluate_model(model, loader, device):
    model.eval()
    patient_ids, labels_all, probs_all = [], [], []
    with torch.inference_mode():
        for features, labels, batch_patient_ids in loader:
            features = features.to(device, non_blocking=True)
            logits = model(features)
            probs = logits.softmax(dim=1)[:, 1].detach().cpu().numpy()
            patient_ids.extend(list(batch_patient_ids))
            labels_all.extend(labels.numpy().tolist())
            probs_all.extend(probs.tolist())
    return aggregate_patient_predictions(patient_ids, labels_all, probs_all, threshold=0.5)


def train_adapter_5fold(patient_table, cached, cfg):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed = int(cfg.get("seed", 42))
    n_splits = int(cfg.get("n_splits", 5))
    feature_dim = int(cached["features"].shape[1])
    output_dir = Path(cfg["outputs_dir"])
    checkpoint_dir = Path(cfg["checkpoints_dir"])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    all_oof_rows, fold_results = [], []
    outer_cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    patient_df = patient_table.reset_index(drop=True).copy()

    for fold, (train_idx, test_idx) in enumerate(outer_cv.split(patient_df["patient_id"], patient_df["target"]), start=1):
        seed_everything(seed + fold)
        outer_train = patient_df.iloc[train_idx].copy()
        outer_test = patient_df.iloc[test_idx].copy()
        inner_train, inner_val = train_test_split(
            outer_train,
            test_size=float(cfg.get("inner_val_ratio", 0.15)),
            random_state=seed + fold,
            stratify=outer_train["target"],
        )

        loaders = {}
        for name, patients, shuffle in [
            ("train", inner_train, True),
            ("val", inner_val, False),
            ("test", outer_test, False),
        ]:
            indices = indices_for_patient_ids(cached, patients["patient_id"])
            loaders[name] = DataLoader(
                CachedFeatureDataset(cached, indices),
                batch_size=int(cfg.get("probe_batch_size", 512)),
                shuffle=shuffle,
                num_workers=int(cfg.get("num_workers", 0)),
                pin_memory=True,
            )

        model = AdapterProbe(
            feature_dim,
            hidden_dim=int(cfg.get("adapter_hidden_dim", 128)),
            dropout=float(cfg.get("adapter_dropout", 0.2)),
        ).to(device)
        class_counts = inner_train["target"].value_counts().reindex([0, 1]).fillna(1).to_numpy()
        class_weight = torch.tensor(class_counts.sum() / (2 * class_counts), dtype=torch.float32).to(device)
        criterion = nn.CrossEntropyLoss(weight=class_weight)
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=float(cfg.get("probe_lr", 1e-3)),
            weight_decay=float(cfg.get("probe_weight_decay", 1e-4)),
        )

        best_state = None
        best_val = -np.inf
        early = 0
        epochs = int(cfg.get("probe_epochs", 20))
        patience = int(cfg.get("probe_patience", 4))

        print(f"\nfold {fold}: train={len(inner_train)}, val={len(inner_val)}, test={len(outer_test)}")
        for epoch in range(1, epochs + 1):
            model.train()
            loss_sum, total = 0.0, 0
            for features, labels, _ in loaders["train"]:
                features = features.to(device, non_blocking=True)
                labels = labels.to(device, non_blocking=True)
                logits = model(features)
                loss = criterion(logits, labels)
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
                loss_sum += loss.item() * labels.size(0)
                total += labels.size(0)

            val_pred = evaluate_model(model, loaders["val"], device)
            val_metrics = calculate_metrics(val_pred["target"], val_pred["probability"], threshold=0.5)
            score = val_metrics["auroc"]
            print(f"Epoch {epoch:02d}/{epochs} | loss {loss_sum/max(total,1):.4f} | val AUROC {score:.4f} AUPRC {val_metrics['auprc']:.4f}")

            if score > best_val + 1e-4:
                best_val = score
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                early = 0
            else:
                early += 1
                if early >= patience:
                    print("early stopping")
                    break

        model.load_state_dict(best_state)
        model = model.to(device)
        val_pred = evaluate_model(model, loaders["val"], device)
        threshold, _ = choose_sensitivity_first_threshold(
            val_pred["target"],
            val_pred["probability"],
            target_sensitivity=float(cfg.get("target_sensitivity", 0.85)),
        )
        test_pred = evaluate_model(model, loaders["test"], device)
        test_pred["fold"] = fold
        test_pred["threshold"] = threshold
        test_pred["pred_label"] = (test_pred["probability"] >= threshold).astype(int)
        all_oof_rows.append(test_pred)

        metrics = calculate_metrics(test_pred["target"], test_pred["probability"], threshold=threshold)
        fold_results.append({"fold": fold, "threshold": threshold, **metrics})
        torch.save(
            {"model_state_dict": best_state, "feature_dim": feature_dim, "threshold": threshold},
            checkpoint_dir / f"adapter_probe_fold{fold}.pt",
        )

    oof = pd.concat(all_oof_rows, ignore_index=True)
    fold_df = pd.DataFrame(fold_results)
    output_dir.mkdir(parents=True, exist_ok=True)
    oof.to_csv(output_dir / "adapter_probe_oof_predictions.csv", index=False, encoding="utf-8-sig")
    fold_df.to_csv(output_dir / "adapter_probe_fold_results.csv", index=False, encoding="utf-8-sig")
    summary = calculate_metrics(oof["target"], oof["probability"], threshold=float(oof["threshold"].median()))
    (output_dir / "adapter_probe_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return fold_df, oof, summary
