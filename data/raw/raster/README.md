# data/raw/raster/ — 래스터 원시자료

래스터(격자 영상) 형태의 원시자료를 넣는 공간. 해상도·CRS가 제각각이어도 된다.

**예시:** DEM(5m/30m), 레이더 강수(HSR), 토양 래스터, 위성 침수관측.
**형식:** GeoTIFF / IMG 등. 원본 CRS·해상도 무관.
**변환 코드:** `src/standardize/raster_align.py` (재투영 → 마스터격자 정합 → 리샘플).
**담당:** geo-data-engineer → geodata-grid-pipeline 스킬.

> 연속형(고도·강우)은 bilinear/cubic, 범주형(토지피복 코드)은 nearest/majority. **범주형에 bilinear 금지**(없는 코드가 보간으로 생성됨). 100m로 낮출 때 목적 반영(저지대 강조는 min pooling 고려).
