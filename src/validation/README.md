# src/validation/ — 검증(QA) 코드

격자 계약 정합성과 모델 성능을 검증하는 코드 자리. 스킬: `flood-model-validation`, 담당: validation-inspector.

| 모듈 | 역할 | 상태 |
|------|------|------|
| `validate.py` | ①격자 계약 강제검증 ②침수흔적도·NDMS 라벨 대비 성능(ROC/PR-AUC, POD/FAR/CSI) ③공간 과적합·라벨 누수 ④산출 품질 | ⬜ |

**규약:** 경계면은 "양쪽 동시 읽기"(생산자·소비자 교차 비교). 격자 계약 검증은 `standardize/verify_grid.py`(assert_grid_contract) 재사용. **증분 검증**(각 산출 직후) + 최종 검증.

> ⬜ 하네스 실행 시 validation-inspector가 구현한다.
