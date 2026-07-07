# src/modeling/ — ML 모델링 코드

인자 스택 + 라벨(침수흔적도 ∪ NDMS)을 결합해 격자별 홍수위험지수를 학습·예측하는 코드가 들어가는 자리. 스킬: `flood-risk-index-modeling`, 담당: flood-risk-modeler.

| 모듈 | 역할 | 상태 |
|------|------|------|
| `build_training_table.py` | 인자 래스터 스택 + labels → 격자 학습표(GeoParquet), **중권역 단위** | ⬜ |
| `spatial_cv.py` | **중권역 공간 블록 CV** fold 생성(무작위 k-fold 금지 — 공간 누수 방지) | ⬜ |
| `train_models.py` | **RandomForest·XGBoost·LightGBM·CatBoost·DecisionTree** 학습·비교, 최적/앙상블 선택 | ⬜ |
| `predict_risk.py` | 전 격자 위험지수 예측 + 중요도(SHAP)·불확실성, 중권역 모자이크 | ⬜ |

**모델링 규약:**
- 모델링·CV 단위 = 수자원단위 **중권역**(부하 저감 + 공간 일관성). 라벨 희소 중권역은 대권역 공유 모델로 상향.
- 클래스 불균형: scale_pos_weight/class_weight, 어려운 음성 표본("침수가능 지형의 실제 미침수") 우선.
- 결측을 0으로 채우지 않는다. 범주형은 CatBoost/LightGBM native categorical 활용.
- 사용 라이브러리(flood_risk311 설치 확인): scikit-learn, xgboost, lightgbm, catboost.

> ⬜ 모듈은 하네스 실행 시 flood-risk-modeler가 스킬을 참조해 구현한다(test-first).
