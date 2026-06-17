from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


CLASS_NAMES = ["NonDemented", "VeryMildDemented", "MildDemented", "ModerateDemented"]
DEMENTED_CLASSES = {"VeryMildDemented", "MildDemented", "ModerateDemented"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


def extract_patient_id(path_or_name):
    text = str(path_or_name)
    match = re.search(r"(OAS1_\d+)", text)
    if match:
        return match.group(1)
    return Path(text).stem.split("_MR")[0]


def target_from_class(class_name):
    if class_name == "NonDemented":
        return 0
    if class_name in DEMENTED_CLASSES:
        return 1
    raise ValueError(f"Unknown class name: {class_name}")


def build_manifest(dataset_dir):
    dataset_dir = Path(dataset_dir)
    rows = []
    for class_name in CLASS_NAMES:
        class_dir = dataset_dir / class_name
        if not class_dir.exists():
            print(f"[WARN] missing class folder: {class_dir}")
            continue
        for image_path in class_dir.rglob("*"):
            if image_path.suffix.lower() in IMAGE_SUFFIXES:
                rows.append({
                    "image_path": str(image_path),
                    "class_name": class_name,
                    "target": target_from_class(class_name),
                    "patient_id": extract_patient_id(image_path.name),
                })
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError(f"No image files found under {dataset_dir}")
    return df


def build_patient_table(manifest):
    return (
        manifest.groupby("patient_id")
        .agg(
            class_name=("class_name", "first"),
            target=("target", "first"),
            n_images=("image_path", "count"),
        )
        .reset_index()
    )
