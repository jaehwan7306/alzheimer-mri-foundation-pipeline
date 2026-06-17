from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def aggregate_patient_predictions(patient_ids, labels, probabilities, threshold=0.5):
    df = pd.DataFrame({
        "patient_id": patient_ids,
        "target": labels,
        "probability": probabilities,
    })
    patient_df = (
        df.groupby("patient_id")
        .agg(target=("target", "first"), probability=("probability", "mean"))
        .reset_index()
    )
    patient_df["pred_label"] = (patient_df["probability"] >= threshold).astype(int)
    return patient_df


def calculate_metrics(y_true, y_prob, threshold=0.5):
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob).astype(float)
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "sensitivity": recall_score(y_true, y_pred, zero_division=0),
        "specificity": tn / max(tn + fp, 1),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "auroc": roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else np.nan,
        "auprc": average_precision_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else np.nan,
    }


def choose_sensitivity_first_threshold(y_true, y_prob, target_sensitivity=0.85):
    rows = []
    for threshold in np.linspace(0.05, 0.95, 181):
        rows.append({"threshold": threshold, **calculate_metrics(y_true, y_prob, threshold)})
    grid = pd.DataFrame(rows)
    candidates = grid[grid["sensitivity"] >= target_sensitivity].copy()
    if len(candidates):
        best = candidates.sort_values(["specificity", "f1"], ascending=False).iloc[0]
    else:
        best = grid.sort_values(["sensitivity", "f1"], ascending=False).iloc[0]
    return float(best["threshold"]), grid
