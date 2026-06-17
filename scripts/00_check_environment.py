from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dl_project_repro.config import add_config_arg, load_config


parser = add_config_arg()
args = parser.parse_args()
cfg = load_config(args.config)

print("config:", cfg["_config_path"])
print("python:", sys.executable)
for key in ["dataset_dir", "outputs_dir", "feature_cache_path", "results_dir", "reports_dir"]:
    path = Path(cfg[key])
    print(f"{key}: {path} ->", "OK" if path.exists() else "MISSING")

try:
    import torch
    print("torch:", torch.__version__)
    print("cuda available:", torch.cuda.is_available())
    print("gpu:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "not available")
except Exception as exc:
    print("torch import failed:", repr(exc))
