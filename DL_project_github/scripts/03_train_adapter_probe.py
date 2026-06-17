from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dl_project_repro.config import add_config_arg, load_config
from dl_project_repro.train_adapter import train_adapter_5fold


parser = add_config_arg()
args = parser.parse_args()
cfg = load_config(args.config)

patient_path = Path(cfg["patient_table_csv"])
cache_path = Path(cfg["feature_cache_path"])
if not patient_path.exists():
    raise FileNotFoundError(f"Run 01_build_manifest.py first: {patient_path}")
if not cache_path.exists():
    raise FileNotFoundError(f"Run 02_extract_biomedclip_features.py first or copy feature cache: {cache_path}")

patient_table = pd.read_csv(patient_path)
cached = torch.load(cache_path, map_location="cpu", weights_only=False)
fold_df, oof, summary = train_adapter_5fold(patient_table, cached, cfg)
print(fold_df)
print(summary)
