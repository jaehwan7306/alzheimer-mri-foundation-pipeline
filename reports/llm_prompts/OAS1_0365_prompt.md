아래 JSON은 Alzheimer MRI multi-foundation screening pipeline의 한 환자 예시 결과다.
이 정보를 바탕으로 한국어 보고서를 작성하라.

보고서 형식:
1. 입력 및 파이프라인 요약
2. SAM foreground segmentation 결과
3. BiomedCLIP adapter classifier 판단
4. Occlusion sensitivity 해석
5. 통합 해석과 주의점

제약:
- 진단, 확진, 병변 검출이라고 표현하지 말 것
- SAM mask를 병변 위치로 해석하지 말 것
- occlusion heatmap을 임상 ROI로 해석하지 말 것
- ground truth class는 실험 검증용 metadata로만 다룰 것
- MRI에서 관찰되지 않은 의학적 소견을 생성하지 말 것

JSON:
{
  "patient_id": "OAS1_0365",
  "case_type": "threshold 근처의 경계 사례",
  "experimental_ground_truth_class": "NonDemented",
  "sam_model": "SAM vit_b",
  "sam_score": 0.9886,
  "segmentation_scope_note": "wide whole-brain foreground",
  "classifier": "BiomedCLIP frozen image encoder + adapter probe",
  "classifier_input": "original MRI feature cache, patient-level aggregation",
  "task": "Stage 1 binary screening: NonDemented vs Demented",
  "patient_level_probability_demented": 0.3265,
  "representative_slice_probability_demented": 0.9992,
  "representative_slice_selection": "highest positive-evidence slice",
  "threshold": 0.325,
  "prediction": "비정상 의심",
  "confidence_band": "threshold에 매우 가까운 경계 결과",
  "occlusion_target_class": "demented class",
  "max_confidence_drop_by_occlusion": 0.9978,
  "mean_positive_confidence_drop_by_occlusion": 0.4137,
  "sam_mask_interpretation": "SAM 기반 brain foreground mask이며, 알츠하이머 병변 위치나 전문의 annotation이 아님",
  "occlusion_interpretation": "patch를 가렸을 때 classifier 확신이 떨어진 정도를 나타내는 model-derived importance map이며, 임상 병변 ROI가 아님",
  "sam_overlay_path": "C:\\Users\\user\\alzheimer\\sam_occlusion_llm_pipeline\\demo_assets\\OAS1_0365_sam_foreground_overlay.png",
  "occlusion_heatmap_path": "C:\\Users\\user\\alzheimer\\sam_occlusion_llm_pipeline\\demo_assets\\OAS1_0365_occlusion_heatmap_overlay.png",
  "occlusion_top_patch_path": "C:\\Users\\user\\alzheimer\\sam_occlusion_llm_pipeline\\demo_assets\\OAS1_0365_occlusion_top_patches.png"
}