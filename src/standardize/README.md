# src/standardize/ — 자료 유형별 변환 코드

원시자료(data/raw/*)와 사전 격자자료(data/standard_grid/pre_gridded)를 마스터 격자로 표준화하는 코드가 들어가는 자리. 방법론은 `geodata-grid-pipeline` 스킬, 담당은 geo-data-engineer.

| 모듈 | 대상 자료 | 방법 | 상태 |
|------|----------|------|------|
| `verify_grid.py` | 모든 산출물 / pre_gridded | 격자 계약 5개 불변식 검증(assert_grid_contract 래퍼) | ✅ 구현(예시) |
| `raster_align.py` | data/raw/raster | 재투영 → 정합 → 리샘플(연속 bilinear / 범주 nearest) | ⬜ |
| `polygon_to_grid.py` | data/raw/polygon | 면적가중 / majority / 피복률 | ⬜ |
| `point_to_grid.py` | data/raw/point | 밀도·개수 / IDW·Kriging 보간 | ⬜ |
| `line_to_grid.py` | 하천·도로 라인 | 거리변환(distance-to) / 라인밀도 | ⬜ |
| `tabular_dasymetric.py` | data/raw/tabular | 다이어시메트릭 분배(가중 하향식, 질량 보존) | ⬜ |
| `timeseries_freq.py` | data/raw/timeseries | 빈도분석(Gumbel/GEV) → 재현주기 격자 | ⬜ |
| `labels_build.py` | data/labels | 침수흔적도 ∪ NDMS → labels.tif | ⬜ |

**공통 규약:** 모든 모듈은 산출 직후 `verify_grid.verify(master, out)`로 계약을 자체검증한다. 번들 참조 구현: `.claude/skills/geodata-grid-pipeline/scripts/align_to_master_grid.py`.

> ⬜ 모듈은 하네스 실행 시 geo-data-engineer가 스킬을 참조해 구현한다(이 환경은 test-first 훅이 있어 `tests/`에 실패 테스트를 먼저 작성).
