# src/forecast/ — 시나리오 예측 코드

학습 모델 + 재현주기별 확률강우로 시나리오 위험도를 예측하는 코드 자리. 스킬: `flood-forecast-scenarios`, 담당: scenario-forecaster.

| 모듈 | 역할 | 상태 |
|------|------|------|
| `scenarios.py` | 강우 인자만 재현주기(50/100/200년) 값으로 교체·재예측, 시나리오 간 증분, 중권역 모자이크 | ⬜ |

**규약:** 모델을 새로 학습하지 않고 modeler 모델을 재사용(강우만 교체). 같은 마스터 격자·모델·중권역 파티션 사용. 확장(SSP·nowcasting)은 스킬 references 조건부 로드.

> ⬜ 하네스 실행 시 scenario-forecaster가 구현한다.
