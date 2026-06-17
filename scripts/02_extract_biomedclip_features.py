from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dl_project_repro.config import add_config_arg, load_config
from dl_project_repro.features import extract_biomedclip_features


parser = add_config_arg()
args = parser.parse_args()
cfg = load_config(args.config)

manifest_path = Path(cfg["manifest_csv"])
if not manifest_path.exists():
    raise FileNotFoundError(f"Run 01_build_manifest.py first: {manifest_path}")
manifest = pd.read_csv(manifest_path)
extract_biomedclip_features(manifest, cfg)
