# src/cartography/ — 위험지도·리포트 제작 코드

위험지수·시나리오를 등급화 지도·통계·리포트로 만드는 코드 자리. 스킬: `flood-risk-cartography`, 담당: geo-cartographer.

| 모듈 | 역할 | 상태 |
|------|------|------|
| `make_maps.py` | 위험등급 분류(Jenks/분위), COG·웹타일, 노출 교차 통계, 방재 리포트 | ⬜ |

**규약:** 시나리오 간 비교는 동일 분류 기준. 불확실성 레이어로 과신 방지. 최종 산출은 `outputs/`, 리포트에 검증 한계 반영.

> ⬜ 하네스 실행 시 geo-cartographer가 구현한다.
