from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dl_project_repro.config import add_config_arg, load_config


parser = add_config_arg()
args = parser.parse_args()
cfg = load_config(args.config)

results_dir = Path(cfg["results_dir"])
for path in [
    results_dir / "final_model_comparison_table.csv",
    results_dir / "adapter_probe_oof_metrics.json",
    results_dir / "adapter_probe_oof_patient_predictions.csv",
    results_dir / "sam_occlusion_llm_report_index.csv",
]:
    print("\n===", path.name, "===")
    if not path.exists():
        print("MISSING:", path)
        continue
    if path.suffix == ".json":
        print(json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=2, ensure_ascii=False))
    else:
        df = pd.read_csv(path)
        print(df.head())
        print("shape:", df.shape)
