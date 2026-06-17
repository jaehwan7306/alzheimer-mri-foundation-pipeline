## 🧠 Alzheimer MRI 다중 기반 스크리닝 모델 분석 보고서

**환자 ID:** OAS1\_0223
**분석 목적:** 첨단 AI 모델을 활용한 초기 연구용 스크리닝 결과 정리 및 해석 보조 자료 제공.

---

### 1. 입력 및 파이프라인 요약 (Input and Pipeline Summary)

본 분석은 환자 ID `OAS1_0223`의 MRI 데이터를 기반으로 진행된 다중 기반(Multi-foundation) 스크리닝 파이프라인의 결과입니다. 이 모델은 초기 단계에서 정상군과 치매 의심군을 구분하는 2진 분류(Binary Screening)를 목표로 합니다.

*   **사례 유형:** 비정상적으로 높은 위험도를 보인 사례 (High-risk misclassification case).
*   **실험 검증용 메타데이터:** 해당 환자는 실험 설계 상 'MildDemented' 클래스로 지정된 metadata가 존재합니다. (이는 모델의 진단적 판단 근거가 아닌, 연구 목적으로 제공된 분류 정보입니다.)
*   **분석 파이프라인 구성:** SAM 기반 구조 분석 $\rightarrow$ BiomedCLIP 어댑터 분류기 적용 $\rightarrow$ Occlusion Sensitivity 분석 순으로 진행되었습니다.

### 2. SAM Foreground Segmentation 결과 (SAM Segmentation Result)

SAM(Segment Anything Model)은 MRI 이미지에서 전반적인 뇌 영역을 시각화하는 데 사용되었습니다.

*   **사용 모델:** SAM vit\_b
*   **분석 점수 (Score):** 0.9922로 매우 높은 일관성을 보였습니다.
*   **시각화 범위:** 이 마스크는 **광범위한 전뇌 영역(wide whole-brain foreground)**을 포괄하는 구조적 시각화 결과입니다.
*   **주의사항:** SAM이 생성한 마스크는 알츠하이머 병변의 위치를 나타내거나 전문의가 직접 주석을 단 임상적인 의미를 가지지 않는, **뇌 전경(brain foreground) 보조 시각화 자료**로 해석해야 합니다.

### 3. BiomedCLIP Adapter Classifier 판단 (BiomedCLIP Classification Judgment)

SAM으로 구조적 영역이 정의된 후, BiomedCLIP 어댑터 분류기가 원본 MRI 특징 캐시를 활용하여 환자 수준의 위험도를 평가했습니다.

*   **분석 방식:** 원본 MRI 특징과 환자 전체 데이터를 종합적으로 고려한 단계 1 이진 스크리닝을 수행했습니다.
*   **판단 결과 (Demented Class):**
    *   환자 레벨 확률: 0.9003
    *   대표 슬라이스(Representative Slice) 확률: 1.0
*   **예측:** 모델은 해당 환자를 **'비정상 의심'**으로 분류했습니다.
*   **신뢰도:** 예측 결과는 상대적으로 명확한 높은 신뢰도를 보였습니다.

### 4. Occlusion Sensitivity 해석 (Occlusion Sensitivity Interpretation)

이 분석은 이미지의 특정 영역(패치)을 가렸을 때, 모델의 확신도가 얼마나 떨어지는지를 측정하는 **모델 기반 중요도 지도(model-derived importance map)**를 생성합니다. 이는 임상적으로 정의된 병변 영역(ROI)과는 무관한 개념입니다.

*   **분석 목표:** 'demented class'에 대한 분류기의 민감도를 테스트했습니다.
*   **결과 해석:**
    *   최대 확신도 하락 폭 (Max Confidence Drop): 0.0034
    *   평균 확신도 하락 폭 (Mean Positive Confidence Drop): 0.0003
*   **의미:** 패치를 가렸을 때 분류기의 전반적인 확신도가 비교적 낮은 수준으로 떨어졌음을 보여줍니다.

### 5. 통합 해석과 주의점 (Integrated Interpretation and Caution)

#### 종합 요약
본 스크리닝 파이프라인은 SAM 기반 구조 분석 및 BiomedCLIP 분류기를 통해 해당 환자에게서 'Demented' 클래스에 대한 높은 확률(0.9003)을 포착했습니다. Occlusion Sensitivity 분석 결과는 모델의 전반적인 판단 근거가 특정 영역에 과도하게 의존하지 않음을 시사합니다.

#### ⚠️ 중요 주의사항 (Disclaimer)
**본 보고서는 인공지능 모델이 수행한 연구용 스크리닝(Screening) 결과일 뿐이며, 어떠한 경우에도 최종적인 의료 진단이나 확정적 판단으로 사용될 수 없습니다.**

1.  **진단 불가:** 이 분석은 의학적 진단을 대체할 수 없으며, 반드시 숙련된 신경과 전문의의 임상적 검토와 종합적인 판독이 필요합니다.
2.  **모델 해석 제한:** SAM 마스크는 뇌 전경 시각화 자료이며, Occlusion Heatmap은 모델 내부의 중요도 지표일 뿐입니다. 이 결과들을 병변 위치나 임상 ROI로 오해해서는 안 됩니다.
3.  **연구 목적 한정:** 본 보고서에 제시된 모든 수치와 해석은 **연구 및 개발 목적으로만 활용되어야 합니다.**