# Results

The final selected model is the BiomedCLIP adapter probe.

See:

- `results/final_model_comparison_table.csv`
- `results/adapter_probe_oof_metrics.json`
- `results/adapter_probe_oof_patient_predictions.csv`

The final model balances sensitivity and specificity better than zero-shot and remains more stable than heavier model-internal adaptation attempts on the available dataset.

CNN baseline is included as a supervised reference, but the project objective is foundation-model adaptation rather than pure CNN optimization.
