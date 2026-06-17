# Results

The final selected model is the **BiomedCLIP adapter probe**.

This result page follows the same reporting basis as `results/final_model_comparison_table.csv`.

## Final Selected Model

| Metric | Value |
|---|---:|
| Sensitivity | 0.887 |
| Specificity | 0.823 |
| Precision | 0.604 |
| F1 | 0.718 |
| Macro F1 | 0.802 |
| AUROC | 0.901 |
| AUPRC | 0.695 |

The selected threshold emphasizes sensitivity because the target use case is screening. Missing a likely `Demented` patient is considered more costly than sending a false positive case to a follow-up review.

## Interpretation

Zero-shot BiomedCLIP had low sensitivity and weak AUROC/AUPRC because prompt-image similarity alone was not enough to separate subtle MRI differences in a small and imbalanced dataset.

Probe-based adaptation was needed to learn a dataset-specific decision boundary on top of frozen BiomedCLIP features.

The adapter probe was selected because it offered a stronger sensitivity/F1 balance than zero-shot or linear probing while remaining more stable than heavier fine-tuning attempts on the available dataset.

## CNN Baseline Caveat

The EfficientNet CNN baseline had higher AUROC/AUPRC in the comparison table. Therefore, the conclusion is not that the foundation model dominates CNN across all metrics.

The intended conclusion is narrower:

> BiomedCLIP adapter probe is the final model because it fits the foundation-model adaptation objective and sensitivity-first screening design, while CNN remains a strong supervised baseline.

## Precision Caveat

Precision is moderate, so false positives remain meaningful. The model should be interpreted as a screening assistant, not a diagnostic system.

## Files

- `results/final_model_comparison_table.csv`: final comparison table used by the README and result summary
- `results/adapter_probe_oof_metrics.json`: raw audit artifact from recalculated OOF outputs
- `results/adapter_probe_oof_patient_predictions.csv`: patient-level prediction artifact
