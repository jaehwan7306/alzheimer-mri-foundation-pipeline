# Reproducibility Guide

## Minimal Check

```powershell
python scripts\04_evaluate_saved_results.py --config config.local.json
```

## Full Reproduction From Dataset

```powershell
python scripts\01_build_manifest.py --config config.local.json
python scripts\02_extract_biomedclip_features.py --config config.local.json
python scripts\03_train_adapter_probe.py --config config.local.json
```

## LLM Report Regeneration

1. Open LM Studio.
2. Load a local chat model.
3. Start the OpenAI-compatible local server.
4. Update `lmstudio_model_id` in `config.local.json`.
5. Run:

```powershell
python scripts\05_generate_llm_reports.py --config config.local.json
```

## Notes

The feature cache is intentionally not included in the repository. It can be large and should be regenerated locally.
