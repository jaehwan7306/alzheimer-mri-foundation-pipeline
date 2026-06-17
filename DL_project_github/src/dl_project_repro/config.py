from __future__ import annotations

import argparse
import json
from pathlib import Path


def package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_path(value, root: Path) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path
    return root / path


def load_config(path=None):
    root = package_root()
    config_path = Path(path) if path else root / "config.local.json"
    if not config_path.exists():
        config_path = root / "config.example.json"
    with config_path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["_config_path"] = str(config_path)
    cfg["_package_root"] = str(root)
    cfg["project_root"] = str(resolve_path(cfg.get("project_root", "."), root))
    for key in [
        "dataset_dir",
        "outputs_dir",
        "manifest_csv",
        "patient_table_csv",
        "feature_cache_path",
        "checkpoints_dir",
        "results_dir",
        "reports_dir",
        "prompts_dir",
    ]:
        if key in cfg:
            cfg[key] = str(resolve_path(cfg[key], root))
    return cfg


def add_config_arg(parser=None):
    parser = parser or argparse.ArgumentParser()
    parser.add_argument("--config", default=None, help="Path to config JSON. Defaults to config.local.json.")
    return parser
