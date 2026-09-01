# Research Decision Log

This document records **why the project changed direction over time**, not only which model or notebook was used. The final pipeline was shaped by evaluation reliability, the screening objective, project scope, and limited experiment time.

The entries below combine decisions explicitly reflected in the experiment notebooks with retrospective project rationale. Experiments that were incomplete at the original project cutoff are described as **deferred** at that point in time. If a deferred question was later revisited, the follow-up is recorded separately rather than rewriting the original chronology.

## Decision Summary

| Stage | Decision | Rationale | Outcome |
|---|---|---|---|
| ver1–2 | Separate augmentation from deterministic feature caching | Make the BiomedCLIP feature pipeline reproducible and prevent augmented variants of one source image from being split inconsistently | Stable cache-based experimentation |
| ver3 | Add a supervised CNN baseline | Avoid evaluating the foundation-model approach without a conventional reference model | EfficientNet baseline retained throughout the project |
| ver4 | Replace image-level splitting with patient-level splitting | Multiple slices from one patient can leak patient-specific information across train/test boundaries | All major later evaluations use patient-level splits |
| ver4–8 | Focus first on early-detection-style binary tasks | Alzheimer screening is more useful when the question is whether a patient should be flagged, rather than predicting a detailed severity label from a small dataset | `NonDemented vs VeryMildDemented` used as an intermediate task |
| ver7–11 | Calibrate thresholds on validation patients and prioritize sensitivity | A screening system should reduce false negatives rather than optimize accuracy alone | Sensitivity-first operating-point selection |
| ver9–10 | Redefine the final task as `NonDemented vs Demented` | The project objective became Alzheimer screening rather than severity grading; the very small `ModerateDemented` patient count also made stable multi-class evaluation difficult | Final binary Stage 1 screening task |
| ver11 | Move from pure zero-shot use to lightweight task adaptation | Zero-shot BiomedCLIP did not provide a useful dataset-specific decision boundary | Linear probe and adapter probe became the main foundation-model candidates |
| ver12–14 | Explore model-internal PEFT with LoRA and an internal adapter | Test whether limited encoder-internal adaptation could improve on frozen-feature probes | LoRA received full 5-fold evaluation; internal adapter remained a Fold-1 pilot at project cutoff |
| ver14–15 | Stop further classifier-specific optimization and select the adapter probe for the final pipeline | Project time was limited, and the primary objective was a **multi-foundation system**, not exhaustive optimization of one classifier | Adapter probe selected as the practical final classifier |
| ver16–18 | Integrate screening, visual context, and report generation | Demonstrate how multiple foundation-model components can work together in one workflow | BiomedCLIP + SAM + occlusion + local LLM pipeline |
| ver19 follow-up | Complete the deferred Internal Adapter 5-fold validation without changing the original ver14 configuration | Test whether the strong Fold-1 result generalizes across patient-level folds | AUROC stayed comparable, but sensitivity was lower on average and substantially more variable; adapter probe retained |

## 1. Stabilize the BiomedCLIP Experiment Pipeline

### Problem

The first stage was less about maximizing accuracy and more about building a reproducible way to experiment with BiomedCLIP features and MRI augmentation.

### Decision

- Separate feature extraction/caching from classifier training.
- Apply rotation, shift, and zoom as separate augmentation variants rather than one combined transformation.
- Keep augmented variants derived from the same source image on the same side of the train/validation split.

### Why

This made it easier to distinguish improvements caused by the classifier from changes caused by data handling or augmentation.

### Impact

The cache-based pipeline became a stable experimentation base, but this still did **not** solve patient-level leakage. That larger issue was addressed later in ver4.

## 2. Replace Image-Level Evaluation with Patient-Level Evaluation

### Problem

The dataset contains many 2D MRI slices per patient. With image-level splitting, slices from one patient can appear in both training and evaluation sets.

### Decision

From ver4 onward, patient IDs were reconstructed from filenames and train/validation/test partitions were created at the **patient level**. Slice predictions were aggregated into patient-level predictions for evaluation.

### Why

The model should be evaluated on patients it did not see during training. Otherwise, patient-specific visual information can make performance appear better than it really is.

### Impact

This became a non-negotiable evaluation rule for the rest of the project and is more important than the headline performance of the earlier image-level experiments.

## 3. Redefine the Problem Around Screening Instead of Severity Grading

### Initial direction

The project initially explored multiple severity labels and then an early-detection-style task such as:

```text
NonDemented vs VeryMildDemented
```

A hierarchical design was also considered:

```text
Stage 1: NonDemented vs Demented
Stage 2: VeryMildDemented vs Mild/ModerateDemented
```

### Decision

The final project intentionally stopped at Stage 1:

```text
NonDemented
vs
Demented = VeryMildDemented + MildDemented + ModerateDemented
```

### Why

The project objective was interpreted as **early screening for possible Alzheimer-related dementia**, not precise grading of disease severity. From that perspective, distinguishing whether a patient should be flagged was more relevant than separating later severity stages.

The dataset also contains only a very small number of `ModerateDemented` patients, which further weakens the case for presenting severity classification as a stable final task.

### Impact

The simplified binary task is less clinically granular, but it better matches the screening-oriented research question and supports more reliable patient-level evaluation.

## 4. Use a Sensitivity-First Operating Point

### Problem

A default decision threshold of `0.5` is not necessarily appropriate for a screening problem.

### Decision

Thresholds were selected using validation-patient predictions, with sensitivity treated as the primary criterion and specificity used as a constraint/tradeoff metric.

### Why

In a screening setting, a false negative means a positive patient is not flagged. The project therefore prioritized reducing missed positive cases, while explicitly accepting more false-positive screening flags.

### Impact

The final classifier should not be interpreted only by accuracy, AUROC, or the default threshold. Its operating point is intentionally chosen for a sensitivity-first use case.

## 5. Move Beyond Zero-Shot BiomedCLIP, but Keep Adaptation Lightweight

### Problem

Pure zero-shot image-text similarity was not sufficient for this MRI screening task.

### Decision path

```text
Zero-shot
   ↓
Linear probe
   ↓
Adapter probe
   ↓
Model-internal PEFT experiments (LoRA / internal adapter)
```

### Why

The project was not designed to maximize performance through unrestricted end-to-end fine-tuning. Its broader objective was to examine how pretrained foundation-model capabilities could be adapted efficiently and then combined with other foundation-model components.

For that reason, frozen encoders and parameter-efficient adaptation were preferred when they already produced useful screening performance.

### Important clarification

This does **not** mean that a deeply fine-tuned foundation model stops being a foundation-model-based system. The decision was a **project-scope choice**: preserve more of the pretrained representation, limit task-specific optimization, and spend the remaining effort on multi-foundation integration rather than exhaustive classifier tuning.

## 6. LoRA Was Fully Validated; the Internal Adapter Was Initially a Promising Pilot

### LoRA

The LoRA experiment was first tested on Fold 1 and then expanded to all five patient-level folds. This closed the pilot-to-validation loop and allowed it to be compared with the fully evaluated adapter probe.

### Internal Adapter at the original project cutoff

The model-internal bottleneck adapter was introduced as a pilot experiment. On Fold 1 it produced:

| Metric | Fold-1 Internal Adapter |
|---|---:|
| Sensitivity | **0.9375** |
| Specificity | 0.7778 |
| F1 | 0.6977 |
| Macro F1 | 0.7818 |
| AUROC | **0.9016** |
| AUPRC | 0.6419 |

The result was promising, especially for sensitivity, and the notebook explicitly treated a later 5-fold extension as the appropriate next step.

### Why 5-fold validation was not completed during the original project

The project schedule did not leave enough time to run the full internal-adapter validation. At that point, a fully evaluated adapter probe already provided a usable classifier, while the larger project still needed the SAM, occlusion, and LLM components to be integrated.

Therefore, the remaining time was allocated to **multi-foundation integration rather than further classifier-specific optimization**.

At that point in the chronology, the correct interpretation was:

> **Promising pilot; full patient-level 5-fold validation deferred.**

This was not evidence that the Internal Adapter was worse. It was evidence that the experiment was incomplete.

## 7. Post-Project Follow-Up: Complete the Internal Adapter 5-Fold Validation

After the original multi-foundation pipeline was complete, the deferred Internal Adapter branch was reopened as **ver19**. The goal was not to tune new hyperparameters or maximize performance. The experiment intentionally kept the original ver14 configuration fixed and asked one question:

> Does the high Fold-1 sensitivity generalize across all five patient-level folds?

### Fixed follow-up protocol

- Same binary task: `NonDemented` vs `Demented`.
- Same patient-level 5-fold split logic and seed `42`.
- Same 15% inner validation split.
- Same BiomedCLIP pretrained weights frozen.
- Same bottleneck adapters inserted into the last 2 visual blocks.
- Same adapter hidden dimension `64` and dropout `0.1`.
- Same training hyperparameters.
- No augmentation (`TRAIN_AUG_MODE = "original"`).
- Fold-specific threshold selected only on inner-validation patients.

The follow-up evaluated **347 unique patients**, with each patient appearing exactly once in the pooled OOF predictions.

### Fold-level result

| Fold | Sensitivity | Specificity | Macro F1 | AUROC | AUPRC | Selected threshold |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.9375 | 0.7778 | 0.7818 | 0.9016 | 0.6419 | 0.325 |
| 2 | 1.0000 | 0.8113 | 0.8343 | 0.9567 | 0.7934 | 0.250 |
| 3 | 0.5625 | 0.9057 | 0.7444 | 0.8868 | 0.6239 | 0.650 |
| 4 | 0.8125 | 0.8113 | 0.7677 | 0.8785 | 0.6689 | 0.425 |
| 5 | 0.7500 | 0.8113 | 0.7458 | 0.8833 | 0.6690 | 0.500 |

The main pattern is not that Fold 1 alone was anomalous. Fold 2 was also exceptionally strong. The important result is that the model was **highly split-sensitive**: sensitivity ranged from `0.5625` to `1.0000`, and the selected validation threshold ranged from `0.250` to `0.650`.

### 5-fold comparison with the Adapter Probe

| Metric | Adapter Probe | Internal Adapter follow-up |
|---|---:|---:|
| Trainable params | **133,762** | 199,298 |
| Trainable ratio | **0.0683%** | 0.1016% |
| Sensitivity mean | **0.8875** | 0.8125 |
| Sensitivity SD | **0.1118** | 0.1712 |
| Specificity mean | 0.8233 | 0.8235 |
| Specificity SD | **0.0218** | 0.0482 |
| Precision mean | **0.6040** | 0.5877 |
| F1 mean | **0.7176** | 0.6737 |
| Macro F1 mean | **0.8021** | 0.7748 |
| AUROC mean | 0.9010 | **0.9014** |
| AUPRC mean | **0.6947** | 0.6794 |

The AUROC difference (`0.9010` vs `0.9014`) is too small to support a meaningful claim of Internal Adapter superiority. In contrast, the sensitivity difference and its larger standard deviation are directly relevant to the screening objective.

### Pooled OOF audit

Across all 347 held-out patient predictions, the Internal Adapter follow-up produced:

| Metric | Pooled OOF |
|---|---:|
| Sensitivity | 0.8148 |
| Specificity | 0.8233 |
| Precision | 0.5841 |
| F1 | 0.6804 |
| Macro F1 | 0.7782 |
| AUROC | 0.8975 |
| AUPRC | 0.6397 |

Confusion matrix: `TN=219`, `FP=47`, `FN=15`, `TP=66`.

These pooled metrics are audit artifacts and are kept separate from the equal-weight 5-fold mean values used in the main model-comparison table.

### Follow-up interpretation

The completed evidence supports a more precise conclusion than the original Fold-1 pilot allowed:

> **The Internal Adapter can perform very strongly on some patient splits, but its sensitivity and operating threshold are less stable across folds. Its mean ranking performance remains competitive, yet it does not provide a more reliable sensitivity-first screening model than the Adapter Probe.**

The follow-up therefore **supports retaining the Adapter Probe**. This does not retroactively make the original decision “correct by luck”; the original selection was based on the evidence available at the time, while ver19 closes the previously unresolved comparison with additional evidence.

## 8. Why the Adapter Probe Was Selected and Retained

The final adapter probe uses a frozen BiomedCLIP image encoder with a small nonlinear task-specific adapter. Across five patient-level folds it achieved:

| Metric | 5-fold mean |
|---|---:|
| Sensitivity | **0.8875** |
| Specificity | 0.8233 |
| F1 | 0.7176 |
| Macro F1 | **0.8021** |
| AUROC | **0.9010** |
| AUPRC | 0.6947 |

The original selection was based on:

1. **Fully cross-validated evidence** rather than a single-fold result.
2. **Sensitivity-first screening performance**.
3. **Parameter efficiency** with the BiomedCLIP encoder kept frozen.
4. **Project-scope alignment** with a multi-foundation pipeline.
5. **Time available for the remaining integration work**.

The later ver19 follow-up adds a sixth reason:

6. **The deeper Internal Adapter did not improve mean sensitivity and showed greater fold-to-fold instability**, despite a nearly identical mean AUROC.

The adapter probe therefore remains the project's **practical final classifier**. This is still not a claim that it is the theoretically best possible classifier under every optimization strategy.

## 9. Prioritize the Multi-Foundation Pipeline

Once a stable screening classifier had been selected, the original project shifted from classifier optimization to system integration.

The final direction became:

```text
MRI slices
   ↓
BiomedCLIP adapter screening
   ↓
SAM foreground/context
   +
Occlusion-based model sensitivity
   ↓
Structured screening evidence
   ↓
Local LLM report generation
```

The LLM does not directly classify MRI images, and SAM is not used as an Alzheimer lesion detector. Each component has a deliberately limited role.

The later Internal Adapter follow-up did **not** change this system architecture because it did not provide a stronger basis for replacing the selected adapter probe.

## Deferred, Resolved, or Intentionally Dropped Branches

### Internal Adapter 5-Fold Validation — Deferred at project cutoff, resolved in ver19

**Original reason for deferral:** time constraint and prioritization of multi-foundation integration.

**Follow-up outcome:** completed with the original ver14 configuration. The 5-fold experiment showed lower mean sensitivity and substantially greater sensitivity/threshold variability than the Adapter Probe, while mean AUROC was essentially unchanged.

**Status:** resolved. Adapter Probe remains the final classifier.

### Stage 2 Severity Classification — Intentionally Dropped

**Reason:** the project was reframed around Alzheimer screening/early detection rather than severity grading. The small advanced-dementia sample size also made Stage 2 less attractive as a final evaluation target.

### Deeper Plain BiomedCLIP Fine-Tuning — Deprioritized

**Reason:** the project goal was not exhaustive optimization of a single classifier. Frozen and parameter-efficient adaptation better matched the intended multi-foundation narrative, and the remaining development time was used for integration.

## Final Decision Principle

The project ultimately followed this rule:

> **Establish trustworthy patient-level evaluation, choose a sufficiently strong and efficient screening model, and then prioritize integration of complementary foundation-model components over exhaustive optimization of a single classifier.**

The ver19 follow-up adds an important methodological lesson: **a strong single-fold result should be treated as a hypothesis-generating pilot until patient-level cross-validation establishes its stability.**
