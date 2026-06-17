# DL_project: Alzheimer MRI Multi-Foundation Screening Pipeline

이 문서는 프로젝트 전체 진행 과정을 한 파일로 일반화해서 정리한 참고용 문서이다. 제출용 원본 노트북을 대체하기보다는, 왜 이런 방향으로 설계했고 최종 파이프라인이 어떻게 구성되는지 빠르게 설명하기 위한 로그북이다.

재현용 노트북은 같은 폴더의 `DL_project.ipynb`이다.

## 1. 프로젝트 목적

수업에서 다룬 foundation model 개념을 Alzheimer MRI 분류 문제에 적용했다. 단순히 CNN 성능을 높이는 것이 아니라, 의료 이미지 foundation model인 BiomedCLIP을 중심으로 SAM segmentation foundation model과 LM Studio local LLM을 연결하여 multi-foundation screening pipeline을 구성하는 것이 최종 목표였다.

최종 문제 정의는 Stage 1 screening이다.

- 입력: OASIS 계열 Alzheimer MRI 2D slice 이미지
- 환자 단위 집계: 같은 patient ID의 여러 slice를 하나의 환자 단위로 묶음
- 출력: `NonDemented` vs `Demented`
- Demented 통합 클래스: `VeryMildDemented`, `MildDemented`, `ModerateDemented`

## 2. 핵심 의사결정

초기에는 BiomedCLIP feature caching 기반 분류를 시도했다. 하지만 feature caching 단계에서 학습용 `train_loader`를 그대로 쓰면 `WeightedRandomSampler`, `RandomRotation`, `RandomAffine` augmentation이 함께 들어가 cache feature가 매번 달라지고, 속도도 느려지며, cache의 의미가 불명확해진다. 따라서 feature extraction loader와 training loader를 분리했다.

이후 image-level train/test split이 같은 환자의 slice를 train/test에 동시에 넣을 수 있다는 data leakage 위험을 확인했다. 그래서 patient ID 기준 split으로 바꾸었다.

4-class 분류는 `ModerateDemented` 환자가 2명뿐이라 안정적인 평가가 어려웠다. 따라서 Stage 1 binary screening 문제로 재정의했다.

## 3. 데이터 요약

원본 patient-level class count:

- NonDemented: 266
- VeryMildDemented: 58
- MildDemented: 21
- ModerateDemented: 2

최종 binary task:

- NonDemented: 266
- Demented: 81

## 4. 실험 버전 요약

| Version | Role |
| --- | --- |
| ver1 | BiomedCLIP feature caching 구조 리팩토링, augmentation 분리 출발점 |
| ver2 | group split/class weight 방향으로 수정 |
| ver3 | EfficientNet CNN baseline 실험 |
| ver4-ver8 | patient-level early detection, fine-tuning, threshold calibration 탐색 |
| ver9-ver10 | Stage 1 NonDemented vs Demented 5-fold 및 sensitivity-first threshold |
| ver11 | BiomedCLIP foundation adaptation: zero-shot, linear, adapter 비교 |
| ver12-ver13 | BiomedCLIP LoRA PEFT 실험 및 5-fold 안정화 |
| ver14 | BiomedCLIP internal adapter fold 1 검증 |
| ver15 | 발표용 중간 정리 자료 생성 |
| ver16-ver18 | SAM foreground, occlusion sensitivity, LM Studio LLM 연결 |
| DL_project | 최종 참고 문서와 재현 노트북 |

## 5. 모델 비교 결과

| Method | Category | Folds | Trainable Params | Sensitivity | Specificity | F1 | AUROC | AUPRC | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BiomedCLIP zero-shot | Foundation zero-shot | 5 | 0 | 0.223 | 0.778 | 0.226 | 0.486 | 0.268 | Prompt only |
| BiomedCLIP linear probe | Frozen encoder probe | 5 | 1,026 | 0.839 | 0.790 | 0.662 | 0.898 | 0.687 | Frozen image feature + linear |
| BiomedCLIP adapter probe | Frozen encoder adapter | 5 | 133,762 | 0.887 | 0.823 | 0.718 | 0.901 | 0.695 | Final foundation candidate |
| BiomedCLIP LoRA | Model-internal PEFT | 5 | 74,754 | 0.814 | 0.827 | 0.676 | 0.896 | 0.673 | BiomedCLIP weight frozen, LoRA only |
| BiomedCLIP Internal Adapter | Model-internal adapter | 1 | 199,298 | 0.938 | 0.778 | 0.698 | 0.902 | 0.642 | Fold 1 only |
| EfficientNet CNN baseline | Supervised CNN | 5 | - | 0.776 | 0.857 | 0.690 | 0.912 | 0.734 | Supervised baseline, threshold target 0.85 |

최종 선택 모델은 `BiomedCLIP adapter probe`이다. 최종 OOF patient-level 성능은 다음과 같다.

Sensitivity 0.889, Specificity 0.823, F1 0.720, Macro F1 0.803, AUROC 0.899, AUPRC 0.665

선택 이유:

- zero-shot은 Alzheimer MRI screening에 충분하지 않았다.
- linear probe는 강한 baseline이었지만 adapter probe가 sensitivity와 F1 측면에서 더 나았다.
- LoRA와 internal adapter는 PEFT 관점에서 의미가 있지만, 작은 데이터에서는 adapter probe가 더 안정적인 선택이었다.
- CNN baseline은 supervised 기준으로 유용했지만, 프로젝트의 궁극적 목표가 foundation model adaptation이므로 최종 classifier는 BiomedCLIP 기반으로 정리했다.

## 6. 최종 Multi-Foundation Pipeline

최종 흐름:

`MRI 2D slices -> patient-level grouping -> BiomedCLIP image encoder -> slice-level feature vectors -> adapter classifier -> patient-level probability -> representative slice selection -> SAM foreground segmentation -> occlusion sensitivity -> structured JSON -> LM Studio local LLM -> Korean screening report`

각 모델의 역할:

- BiomedCLIP: MRI slice를 image feature vector로 변환하는 의료 이미지 foundation model
- Adapter classifier: frozen BiomedCLIP feature 위에서 작은 trainable head를 학습하는 parameter-efficient adaptation
- SAM ViT-B: representative slice에서 brain foreground/context mask 생성
- Occlusion sensitivity: 모델 예측이 민감하게 반응하는 영역을 model-derived heatmap으로 시각화
- LM Studio local LLM: classifier/SAM/occlusion 결과를 structured JSON으로 받아 한국어 screening report 생성

주의:

- SAM mask는 Alzheimer 병변 segmentation이 아니다.
- Occlusion heatmap은 임상 ROI가 아니라 모델이 민감하게 반응한 영역이다.
- LLM report는 의료 진단이 아니라 이미 계산된 모델 출력의 요약이다.

## 7. 주요 산출물 위치

- 재현 노트북: `C:\Users\user\alzheimer\DL_project.ipynb`
- 발표용 asset 노트북: `C:\Users\user\alzheimer\final_ppt_visual_assets.ipynb`
- PPT 시각화 자료: `C:\Users\user\alzheimer\final_ppt_assets`
- LLM 보고서: `C:\Users\user\alzheimer\sam_occlusion_llm_pipeline\llm_reports`
- LLM prompt: `C:\Users\user\alzheimer\sam_occlusion_llm_pipeline\llm_prompts`
- SAM/Occlusion demo assets: `C:\Users\user\alzheimer\sam_occlusion_llm_pipeline\demo_assets`
- 최종 결과 index: `C:\Users\user\alzheimer\sam_occlusion_llm_pipeline\sam_occlusion_llm_report_index.csv`

## 8. 재현 방법

`DL_project.ipynb`를 위에서 아래로 실행하면 기본적으로 기존 결과 파일을 로드한다. 재학습이나 LLM 재생성을 원할 때만 노트북 상단의 flag를 `True`로 바꾼다.

기본 권장 flag:

```python
RUN_FEATURE_CACHE = False
RUN_TRAIN_ADAPTER = False
RUN_SAM_OCCLUSION = False
RUN_LLM_REPORT = False
```

이 기본값은 빠르게 결과를 재확인하기 위한 설정이다. 완전 재현을 원하면 feature cache부터 순서대로 다시 켜서 실행할 수 있다.

## 9. 결론

이 프로젝트는 단순 분류 모델 비교에서 출발했지만, 최종적으로는 patient-level split, binary screening task, BiomedCLIP adapter adaptation, SAM 기반 visual context, occlusion 설명, LLM report까지 연결한 multi-foundation pipeline으로 확장되었다. 성능만 보는 프로젝트가 아니라, foundation model을 실제 문제에 적용할 때 필요한 데이터 분할, task 재정의, parameter-efficient adaptation, 설명가능성, 보고서 생성까지의 전체 과정을 정리한 프로젝트이다.
