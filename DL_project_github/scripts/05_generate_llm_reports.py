from __future__ import annotations

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dl_project_repro.config import add_config_arg, load_config


parser = add_config_arg()
args = parser.parse_args()
cfg = load_config(args.config)

prompt_dir = Path(cfg["prompts_dir"])
report_dir = Path(cfg["reports_dir"])
report_dir.mkdir(parents=True, exist_ok=True)

base_url = cfg.get("lmstudio_base_url", "http://127.0.0.1:1234/v1")
model_id = cfg.get("lmstudio_model_id", "google/gemma-4-e4b")

for prompt_path in sorted(prompt_dir.glob("*_prompt.md")):
    prompt_text = prompt_path.read_text(encoding="utf-8")
    response = requests.post(
        f"{base_url}/chat/completions",
        json={
            "model": model_id,
            "messages": [
                {"role": "system", "content": "You summarize research screening outputs in Korean. Do not diagnose."},
                {"role": "user", "content": prompt_text},
            ],
            "temperature": 0.2,
        },
        timeout=120,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    out_path = report_dir / prompt_path.name.replace("_prompt.md", "_llm_report.md")
    out_path.write_text(content, encoding="utf-8")
    print("saved:", out_path)
