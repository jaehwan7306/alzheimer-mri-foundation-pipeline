# Safety and Interpretation Notes

This repository is a research project archive. It is not a medical device and must not be used for clinical diagnosis.

## SAM

SAM output is used as a broad brain foreground/context visualization. It is not Alzheimer lesion segmentation.

## Occlusion Heatmap

Occlusion sensitivity shows regions where the classifier output changes when image patches are masked. This is model-derived importance, not a clinical ROI.

## LLM Report

The LLM receives structured model outputs and writes a Korean report-style summary. It does not inspect MRI images directly and does not diagnose.
