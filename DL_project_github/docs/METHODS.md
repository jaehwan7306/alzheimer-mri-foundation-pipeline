# Methods

## Data Split

The final experimental unit is a patient, not an individual image slice. Patient ID is extracted from OAS-style filenames such as `OAS1_XXXX`.

The project uses stratified patient-level 5-fold evaluation. This avoids the leakage risk where slices from the same patient appear in both train and test sets.

## Task Definition

Original classes:

- NonDemented
- VeryMildDemented
- MildDemented
- ModerateDemented

Final Stage 1 task:

- class 0: NonDemented
- class 1: Demented = VeryMildDemented + MildDemented + ModerateDemented

The 4-class task was not used as the final target because the `ModerateDemented` group had too few patients for stable cross-validation.

## Feature Cache

BiomedCLIP image encoder is used as a frozen feature extractor. Feature extraction uses only the original image preprocessing required by BiomedCLIP.

The feature extraction loader must not use:

- `WeightedRandomSampler`
- random augmentation
- shuffle

Reason: a feature cache should represent deterministic features for original images. Augmentation and class balancing are training-time choices, not feature extraction choices.

## Adapter Probe

The final classifier is an adapter probe:

```text
BiomedCLIP feature -> LayerNorm -> small adapter MLP + residual -> Linear classifier
```

This keeps the foundation model frozen and trains only a small classifier/adaptation head.
