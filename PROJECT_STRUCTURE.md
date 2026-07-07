# 프로젝트 구조 — 격자(100m) 전국 홍수위험도

원시자료를 넣는 공간, 이미 만들어진 표준격자망을 넣는 공간, 자료 변환 코드·ML 코드가 들어갈 골격이다. 각 폴더는 하네스의 에이전트/스킬(누가·어떻게)과 1:1로 대응한다.

```
07_meta_harness/
├── data/                         # 【사용자가 자료를 넣는 공간】
│   ├── raw/                      # 원시자료(rawdata) — 형태별 드롭존
│   │   ├── point/               #   포인트: 강우관측소, NDMS 피해, 건물, 시설
│   │   ├── polygon/             #   폴리곤: 토지피복, 침수흔적도, 행정경계, 지질
│   │   ├── raster/              #   래스터: DEM, 레이더강수, 토양(상이 해상도/CRS)
│   │   ├── tabular/             #   집계표: 행정구역 단위 인구·자산·취약계층
│   │   └── timeseries/          #   시계열: 강우·수위 관측
│   ├── standard_grid/           # 【이미 만들어진 표준격자망 제공 공간】
│   │   ├── grid_master/         #   마스터 격자(100m, EPSG:5179) 직접 제공 시
│   │   └── pre_gridded/         #   이미 100m 격자로 제작된 자료(라벨 등) 제공 시
│   ├── labels/                  # 타깃: 침수흔적도·NDMS (원시 또는 격자)
│   └── watershed/               # 수자원단위지도(대권역/중권역/표준유역 경계)
│
├── src/                          # 【코드가 들어갈 골격】 스킬의 절차를 구현
│   ├── standardize/             # 자료 유형별 변환(→ geodata-grid-pipeline 스킬)
│   │   ├── verify_grid.py       #   격자 계약 검증 래퍼
│   │   ├── raster_align.py      #   래스터 재투영·정합
│   │   ├── polygon_to_grid.py   #   폴리곤 → 격자(면적가중/majority/피복률)
│   │   ├── point_to_grid.py     #   포인트 → 격자(밀도/보간)
│   │   ├── line_to_grid.py      #   라인 → 격자(거리변환)
│   │   ├── tabular_dasymetric.py#   집계 → 다이어시메트릭 분배
│   │   ├── timeseries_freq.py   #   시계열 → 빈도분석
│   │   └── labels_build.py      #   침수흔적도 ∪ NDMS → labels
│   ├── factors/                 # 인자 산출
│   │   ├── terrain.py           #   → terrain-hazard-factors 스킬
│   │   ├── hydro.py             #   → hydro-hazard-factors 스킬
│   │   └── exposure.py          #   → exposure-vulnerability-factors 스킬
│   ├── modeling/                # 【ML 모델링 코드】 → flood-risk-index-modeling
│   │   ├── build_training_table.py  # 인자 스택 + 라벨 → 학습표(중권역)
│   │   ├── spatial_cv.py            # 중권역 공간 블록 CV
│   │   ├── train_models.py         # RF/XGB/LGBM/CatBoost/DT 학습·비교
│   │   └── predict_risk.py         # 전 격자 위험지수 예측·모자이크
│   ├── forecast/scenarios.py    # → flood-forecast-scenarios (재현주기)
│   ├── validation/validate.py   # → flood-model-validation (QA)
│   └── cartography/make_maps.py # → flood-risk-cartography (위험지도)
│
├── config/
│   └── grid_config.yaml         # 격자 계약 파라미터(CRS/해상도/원점/NoData/모델)
├── outputs/                     # 최종 산출물(위험지도·리포트)
├── _workspace/                  # 실행 중간 산출물(오케스트레이터가 관리)
├── env.ps1                      # 실행 환경변수 고정(PROJ 충돌 방지) — 실행 전 dot-source
│
├── CLAUDE.md                    # 하네스 포인터
└── .claude/                     # 하네스 본체(에이전트·스킬)
    ├── agents/                  #   누가(전문가 8)
    └── skills/                  #   어떻게(스킬 9 + 격자 계약·유역 규약·자료원)
```

## 자료 → 코드 → 에이전트 대응

| 넣는 자료(data/) | 변환 코드(src/standardize/) | 담당 에이전트 |
|-----------------|---------------------------|-------------|
| raw/point/ | point_to_grid.py | geo-data-engineer |
| raw/polygon/ | polygon_to_grid.py | geo-data-engineer |
| raw/raster/ | raster_align.py | geo-data-engineer |
| raw/tabular/ | tabular_dasymetric.py | geo-data-engineer |
| raw/timeseries/ | timeseries_freq.py | geo-data-engineer(+hydro) |
| standard_grid/pre_gridded/ | verify_grid.py (검증 후 사용) | geo-data-engineer + validation-inspector |
| labels/ | labels_build.py | geo-data-engineer |

## 실행 전 준비
1. `. .\env.ps1` 로 PROJ/GDAL 경로를 conda 환경으로 고정(시스템 PostgreSQL PROJ 충돌 방지).
2. `data/` 아래 해당 폴더에 자료를 넣는다(형태별).
3. 표준격자망을 이미 갖고 있으면 `data/standard_grid/`에 넣는다(없으면 하네스가 대권역별로 생성).
4. 하네스 실행: "낙동강권역 홍수위험도 평가해줘" 등으로 `flood-risk-orchestrator` 트리거.

> 코드(`src/`)는 스킬의 절차를 구현하는 **자리**다. 스킬(`.claude/skills/`)이 방법론(why/how)을, `src/`가 실행 코드를 담는다. 에이전트가 스킬을 참조해 이 코드를 작성·실행한다.
