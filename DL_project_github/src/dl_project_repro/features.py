from __future__ import annotations

import time
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset


class FoundationImageDataset(Dataset):
    def __init__(self, dataframe, preprocess):
        self.df = dataframe.reset_index(drop=True).copy()
        self.preprocess = preprocess

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        row = self.df.iloc[index]
        image = Image.open(row["image_path"]).convert("RGB")
        image = self.preprocess(image)
        return image, torch.tensor(int(row["target"]), dtype=torch.long), row["patient_id"], row["image_path"], row["class_name"]


def extract_biomedclip_features(manifest, cfg):
    import open_clip

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_name = cfg["model_name"]
    print("Loading BiomedCLIP:", model_name)
    model, preprocess = open_clip.create_model_from_pretrained(model_name)
    model = model.to(device)
    model.eval()
    assert next(model.parameters()).device.type == device.type

    dataset = FoundationImageDataset(manifest, preprocess)
    loader = DataLoader(
        dataset,
        batch_size=int(cfg.get("feature_batch_size", 128)),
        shuffle=False,
        sampler=None,
        num_workers=int(cfg.get("num_workers", 0)),
        pin_memory=True,
    )

    features, labels = [], []
    patient_ids, image_paths, class_names = [], [], []
    start = time.time()
    seen = 0
    use_amp = bool(cfg.get("use_amp", True))

    with torch.inference_mode():
        for batch_idx, batch in enumerate(loader, start=1):
            images, batch_labels, batch_patient_ids, batch_image_paths, batch_class_names = batch
            images = images.to(device, non_blocking=True)
            with torch.amp.autocast("cuda", enabled=(use_amp and torch.cuda.is_available())):
                batch_features = model.encode_image(images)
                batch_features = F.normalize(batch_features.float(), dim=-1)

            features.append(batch_features.cpu())
            labels.append(batch_labels.cpu())
            patient_ids.extend(list(batch_patient_ids))
            image_paths.extend(list(batch_image_paths))
            class_names.extend(list(batch_class_names))

            seen += images.size(0)
            elapsed = max(time.time() - start, 1e-6)
            speed = seen / elapsed
            eta_min = (len(dataset) - seen) / max(speed, 1e-6) / 60
            if batch_idx == 1 or batch_idx % 20 == 0 or seen == len(dataset):
                print(f"{seen:,}/{len(dataset):,} images | {speed:.1f} images/s | ETA {eta_min:.1f} min")

    cached = {
        "features": torch.cat(features, dim=0),
        "labels": torch.cat(labels, dim=0),
        "patient_ids": patient_ids,
        "image_paths": image_paths,
        "class_names": class_names,
        "model_name": model_name,
        "normalized": True,
    }
    out_path = Path(cfg["feature_cache_path"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(cached, out_path)
    print("Saved feature cache:", out_path)
    return cached
