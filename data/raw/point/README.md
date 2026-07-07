# data/raw/point/ — 포인트 원시자료

포인트 형태의 원시자료를 넣는 공간.

**예시:** 강우관측소(ASOS/AWS), NDMS 피해지점, 건물 대표점, 주요시설(학교·병원).
**형식:** SHP / GeoPackage / GeoJSON / CSV(좌표 컬럼) 등. 원본 CRS 무관(무단 가정 금지 — 메타데이터 확인).
**변환 코드:** `src/standardize/point_to_grid.py` (밀도·개수 집계 또는 IDW/Kriging 보간).
**담당:** geo-data-engineer → geodata-grid-pipeline 스킬.

> 강우처럼 연속장은 보간, 시설처럼 개별객체는 밀도로 격자화한다. 표준화 후 마스터 격자 정합을 검증한다.
