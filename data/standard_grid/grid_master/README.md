# data/standard_grid/grid_master/ — 기제작 마스터 격자 제공

이미 만든 **마스터 격자**(100m, EPSG:5179)를 여기 넣는다. 대권역별로 여러 개 가능(`grid_master_한강.tif` 등).

- 넣으면 geo-data-engineer가 새로 만들지 않고 이 격자를 기준으로 삼는다.
- 없으면 하네스가 수자원단위 대권역별로 마스터를 생성한다.
- 사용 전 `src/standardize/verify_grid.py`로 계약(CRS·해상도·원점 snap·NoData) 검증.
