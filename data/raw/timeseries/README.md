# data/raw/timeseries/ — 시계열 원시자료

지점별 시계열 관측을 넣는 공간.

**예시:** 강우 시계열(분/시/일), 하천 수위·유량.
**형식:** CSV(지점ID·시각·값) + 지점 좌표(point와 연계). NetCDF도 가능.
**변환 코드:** `src/standardize/timeseries_freq.py` (연최대치 추출 → 빈도분석(Gumbel/GEV) → 재현주기 확률강우 → 격자화).
**담당:** hydro-hazard-analyst → hydro-hazard-factors 스킬.

> 원시 시계열을 바로 격자화하지 않는다 — 빈도분석으로 재현주기(50/100/200년) 개념을 보존한 뒤 격자화한다. 결측을 0으로 채우지 않는다.
