# [연구용] MRI 스크리닝 모델 분석 보고서

**환자 ID:** OAS1\_0365
**분석 목적:** Alzheimer MRI Multi-Foundation Screening Pipeline을 통한 연구용 초기 스크리닝 결과 정리
***
**⚠️ 중요 고지 사항 (Disclaimer)**
본 보고서는 인공지능(AI) 기반의 **연구용 스크리닝 모델**이 계산한 통계적 결과를 사람이 이해하기 쉽도록 재구성한 것입니다. 여기에 제시된 모든 수치와 해석은 의학적인 진단, 확진, 또는 임상적 결론을 대체할 수 없습니다. 최종 판단과 치료 계획은 반드시 전문 의료진의 종합적인 임상 검토를 거쳐야 합니다.
***

## 1. 입력 및 파이프라인 요약 (Input and Pipeline Summary)

| 항목 | 내용 | 설명 |
| :--- | :--- | :--- |
| **환자 ID** | OAS1\_0365 | 분석 대상 환자의 식별 번호입니다. |
| **케이스 유형** | Threshold 근처의 경계 사례 (Borderline Case) | 모델이 판단 기준(Threshold)에 매우 가까운 애매한 결과를 보인 경우로 분류됩니다. |
| **실험 검증용 메타데이터** | NonDemented | 이 값은 본 분석을 위해 사용된 실험적 비교군 정보일 뿐, 임상 진단으로 해석되어서는 안 됩니다. |
| **스크리닝 목표 (Task)** | Stage 1 binary screening: NonDemented vs Demented | 비치매성(NonDemented)과 치매성(Demented) 두 상태 중 어느 쪽에 가까운지 이진 분류를 수행하는 것이 목표입니다. |

## 2. SAM Foreground Segmentation 결과 (SAM Mask Visualization)

**사용 모델:** SAM vit\_b
**분석 범위:** Wide whole-brain foreground
**모델 점수 (SAM Score):** 0.9886

*   **결과 해석:** 본 분석에 사용된 SAM(Segment Anything Model)은 **뇌 전경부(Brain Foreground)**를 보조적으로 시각화하는 마스크를 생성했습니다. 이 마스크는 알츠하이머 병변의 위치나 전문의가 직접 표시한 해부학적 영역을 나타내는 것이 아니며, 단순히 뇌 구조물의 경계를 파악하기 위한 **보조적인 시각화 자료**로 활용되었습니다.
*   **활용 경로:** `OAS1_0365_sam_foreground_overlay.png`

## 3. BiomedCLIP Adapter Classifier 판단 (Classification Judgment)

| 항목 | 값 | 해석 |
| :--- | :--- | :--- |
| **분류기 모델** | BiomedCLIP frozen image encoder + adapter probe | MRI 특징 캐시와 환자 수준의 정보를 종합하여 분류를 수행했습니다. |
| **환자 수준 확률 (Demented)** | 0.3265 | 전체적인 데이터를 기반으로 치매성 상태일 확률은 약 32.65%로 계산되었습니다. |
| **대표 슬라이스 확률 (Demented)** | 0.9992 | 모델이 가장 높은 증거를 발견했다고 판단한 특정 단면(Representative Slice)에서는 치매성 상태일 확률이 매우 높게 나타났습니다. |
| **판단 기준 (Threshold)** | 0.325 | 분류가 이루어진 임계값입니다. |
| **최종 예측** | 비정상 의심 (Suspicious) | 환자 수준의 확률(0.3265)이 설정된 임계값(0.325)에 매우 근접하여, 모델은 경계선상의 결과를 보인 것으로 판단했습니다. |

## 4. Occlusion Sensitivity 해석 (Model-Derived Importance Map Analysis)

**분석 목표:** 분류기(Classifier)가 특정 영역의 정보를 얼마나 중요하게 사용하는지 파악합니다.
**결과 유형:** Model-derived importance map (모델 기반 중요도 지도)

*   **개념 설명:** 이 히트맵은 MRI 이미지의 일부 패치(Patch)를 가렸을 때, 분류기의 확신도가 얼마나 떨어지는지를 보여주는 **모델이 계산한 중요 영역 맵**입니다. 이는 임상적으로 의미 있는 병변 위치(ROI)가 아닙니다.
*   **분석 결과:**
    *   **최대 신뢰도 하락 (Max Confidence Drop):** 0.9978
    *   **평균 양성 신뢰도 하락 (Mean Positive Confidence Drop):** 0.4137
*   **해석:** 모델은 이미지의 특정 영역(Top Patch)을 가렸을 때, 분류기의 확신도가 매우 크게 떨어지는 경향을 보였습니다. 이는 해당 영역이 모델의 판단에 중요한 영향을 미치는 **모델 기반 중요 영역**임을 시사합니다.
*   **활용 경로:** `OAS1_0365_occlusion_heatmap_overlay.png`

## 5. 통합 해석과 주의점 (Integrated Interpretation and Caveats)

### 종합 요약
본 스크리닝 파이프라인은 환자 OAS1\_0365의 MRI 데이터를 분석한 결과, 전반적인 확률(0.3265)은 설정된 임계값에 근접하는 **경계성**을 보였습니다. 그러나 모델이 가장 높은 증거를 발견했다고 판단한 특정 단면에서는 치매성 상태일 가능성이 매우 높게 나타났습니다 (0.9992). 또한, Occlusion Sensitivity 분석 결과는 이미지의 특정 영역이 분류기의 최종 결정에 중요한 역할을 하는 **모델 기반 중요 영역**임을 보여줍니다.

### 🚨 재차 강조하는 주의점
1.  **진단 불가:** 본 보고서의 모든 내용은 AI 모델의 통계적 계산 결과일 뿐이며, 어떠한 의학적 진단이나 확정적인 결론으로도 해석될 수 없습니다.
2.  **시각화 자료의 한계:** SAM 마스크는 뇌 전경부 보조 시각화이며, Occlusion Heatmap은 모델이 중요하다고 판단한 가상의 영역일 뿐입니다. 이들은 임상적 병변이나 해부학적 경계를 직접적으로 나타내지 않습니다.
3.  **연구 목적:** 본 결과는 오직 연구 및 개발 목적으로만 사용되어야 하며, 실제 환자 치료 결정에 활용되어서는 안 됩니다.