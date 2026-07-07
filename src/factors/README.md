# src/factors/ — 인자 산출 코드

표준화된 격자자료(_workspace/02_grid)에서 홍수위험 인자를 산출하는 코드가 들어가는 자리.

| 모듈 | 산출 인자 | 스킬 / 담당 | 상태 |
|------|----------|------------|------|
| `terrain.py` | 경사·TWI·HAND·저지대·곡률·흐름누적 | terrain-hazard-factors / terrain-hazard-analyst | ⬜ |
| `hydro.py` | 확률강우(재현주기)·CN·하천거리·범람·배수 | hydro-hazard-factors / hydro-hazard-analyst | ⬜ |
| `exposure.py` | 인구·자산·건물·취약계층·방재인프라 | exposure-vulnerability-factors / exposure-vulnerability-analyst | ⬜ |

**공통 규약:**
- 흐름기반 인자(terrain·hydro 일부)는 대권역(완전유역)에서 계산 후 중권역 타일링.
- 지형분석은 **WhiteboxTools(whitebox)**로 통일(richdem 미사용).
- 산출 직후 `standardize/verify_grid.py`로 마스터 정합 자체검증.
- 인자별 방향(±)·정규화·스케일을 래스터 태그에 기록.

> ⬜ 모듈은 하네스 실행 시 각 분석가 에이전트가 해당 스킬을 참조해 구현한다.
