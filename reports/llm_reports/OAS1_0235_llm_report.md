## Alzheimer MRI 다중 기반 스크리닝 모델 분석 보고서

**환자 ID:** OAS1\_0235
**분석 목적:** 초기 1단계 이진 분류(NonDemented vs Demented)를 위한 연구용 스크리닝 결과 정리.

---

### 1. 입력 및 파이프라인 요약 (Input & Pipeline Summary)

본 분석은 MRI 데이터를 기반으로 설계된 다중 모달리티 스크리닝 파이프라인을 통해 수행되었습니다. 해당 환자는 임상적으로 '정상으로 맞힌 낮은 위험도 사례'로 분류되었으며, 모델의 실험적 검증용 메타데이터(experimental ground truth class)는 **NonDemented**입니다.

*   **분석 목표:** NonDemented와 Demented 간의 이진 스크리닝 (Stage 1 binary screening).
*   **사용 데이터:** 원본 MRI 특징 캐시 및 환자 수준 집계(patient-level aggregation)를 활용했습니다.
*   **모델 구성:** SAM 기반 전처리 및 BiomedCLIP 어댑터 분류기 조합을 사용하였습니다.

### 2. SAM Foreground Segmentation 결과 (SAM Mask Visualization)

Segmentation 모델로 **SAM vit\_b**가 사용되었으며, 전체적인 스코어는 0.9889를 기록했습니다.

*   **시각화 범위:** 광범위한 전뇌 영역(wide whole-brain foreground)을 포괄하는 마스크가 생성되었습니다.
*   **해석 주의점:** 이 SAM 마스크는 알츠하이머 병변의 위치나 전문의의 임상적 주석(annotation)이 아닙니다. 이는 모델 기반의 **전체 뇌 구조물 전경(brain foreground)**을 시각화한 보조적인 역할을 수행합니다.

### 3. BiomedCLIP Adapter Classifier 판단 (Classification Result)

BiomedCLIP frozen image encoder와 어댑터 프로브를 활용하여 분류가 진행되었습니다.

*   **분류 예측:** 모델은 해당 환자에 대해 **'정상 가능성'**을 예측했습니다.
*   **확신도 및 임계값:** 설정된 임계값(threshold) 0.375 대비, Demented 클래스에 대한 환자 수준 확률과 대표 슬라이스 확률 모두 0.0으로 매우 낮게 측정되었습니다.
*   **결론 신뢰도:** 전반적인 결과는 **상대적으로 명확한 결과**로 판단됩니다.

### 4. Occlusion Sensitivity 해석 (Model-Derived Importance Map)

모델의 안정성을 평가하기 위해 가려짐(Occlusion) 민감도 분석이 수행되었습니다. 이 분석은 'non-demented class'를 기준으로 진행되었습니다.

*   **민감도 지표:** 패치를 가렸을 때 분류기의 확신도가 떨어진 정도를 나타내는 **모델 기반 중요 영역 맵(model-derived importance map)**이 생성되었습니다.
*   **결과 분석:** 최대 신뢰도 하락 폭(max\_confidence\_drop) 및 평균 양성 신뢰도 하락 폭(mean\_positive\_confidence\_drop) 모두 **0.0**을 기록했습니다.
*   **해석 주의점:** 이 맵은 임상적으로 의미 있는 병변 영역(ROI)이 아니며, 모델의 예측에 기여하는 중요도를 나타내는 지표입니다.

### 5. 통합 해석과 주의점 (Integrated Interpretation and Caveats)

종합적으로 볼 때, OAS1\_0235 환자는 스크리닝 파이프라인을 통해 **낮은 위험도(NonDemented)**의 경향성을 보였습니다. SAM 마스크는 전반적인 뇌 구조물 영역을 시각화하며, 분류기는 높은 확신도를 바탕으로 정상 가능성을 제시했습니다. 또한, 가려짐 민감도 분석 결과가 매우 안정적이라는 점은 모델 예측의 견고함을 뒷받침합니다.

**🚨 중요 고지 사항:**
본 보고서는 MRI 데이터를 활용하여 설계된 **연구용 스크리닝(screening)** 결과를 정리한 것입니다. 여기에 제시된 모든 수치와 해석은 인공지능 모델의 계산 결과에 기반하며, 이는 어떠한 경우에도 의학적 진단, 확진 또는 임상적 결론으로 간주되어서는 안 됩니다. 최종적인 의료 판단은 반드시 전문 의료진의 직접적인 검토를 거쳐야 합니다.