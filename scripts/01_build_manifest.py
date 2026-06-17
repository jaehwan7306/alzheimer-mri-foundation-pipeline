from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dl_project_repro.config import add_config_arg, load_config
from dl_project_repro.data import build_manifest, build_patient_table


parser = add_config_arg()
args = parser.parse_args()
cfg = load_config(args.config)

manifest = build_manifest(cfg["dataset_dir"])
patient_table = build_patient_table(manifest)

manifest_path = Path(cfg["manifest_csv"])
patient_path = Path(cfg["patient_table_csv"])
manifest_path.parent.mkdir(parents=True, exist_ok=True)
patient_path.parent.mkdir(parents=True, exist_ok=True)
manifest.to_csv(manifest_path, index=False, encoding="utf-8-sig")
patient_table.to_csv(patient_path, index=False, encoding="utf-8-sig")

print("manifest:", manifest.shape, manifest_path)
print("patient_table:", patient_table.shape, patient_path)
print(patient_table["class_name"].value_counts())
print(patient_table["target"].value_counts())
