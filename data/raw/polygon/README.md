# data/raw/polygon/ — 폴리곤 원시자료

폴리곤(면) 형태의 원시자료를 넣는 공간.

**예시:** 토지피복도, 침수흔적도, 행정경계, 지질도, 토양도.
**형식:** SHP / GeoPackage / GeoJSON. 원본 CRS 무관(메타데이터 확인).
**변환 코드:** `src/standardize/polygon_to_grid.py` (면적가중 집계 / 우세값 majority / 피복률 %).
**담당:** geo-data-engineer → geodata-grid-pipeline 스킬.

> 범주형(토지피복 코드 등)은 majority/nearest로, 연속 속성은 면적가중으로. 셀에 여러 폴리곤이 걸치면 우세값 또는 비율로 처리한다.
