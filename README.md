# 격자(100m) 전국 홍수위험도 평가·예측 하네스

이종 원시자료를 전국 100m 표준격자망(EPSG:5179, 수자원단위 대권역/중권역)에 표준화하고, 지형·수문·노출·취약성 인자를 통합해 머신러닝으로 격자별 홍수위험도를 평가·예측하는 **에이전트 하네스**.

## 무엇이 들어 있나
- **`.claude/agents/`** — 전문가 에이전트 8 (데이터 엔지니어·지형·수문·노출취약성·모델러·예측·검증·지도).
- **`.claude/skills/`** — 스킬 9 (표준화 파이프라인, 인자 산출, ML 모델링, 예측, 검증, 지도) + 오케스트레이터. 표준격자망 **격자 계약**·수자원단위 규약·전국 자료원 참조 포함.
- **`src/`** — 자료 유형별 변환 코드와 ML 모델링 코드가 들어가는 골격.
- **`data/`** — 원시자료(point/polygon/raster/tabular/timeseries)·기제작 표준격자망·라벨·유역 드롭존.
- **`config/grid_config.yaml`**, **`env.ps1`**, **`PROJECT_STRUCTURE.md`**.

## 핵심 설계
- **표준격자 계약**: 모든 산출물이 CRS·해상도·원점·NoData·셀정렬 불변식을 준수(`assert_grid_contract`가 강제).
- **ML**: RandomForest·XGBoost·LightGBM·CatBoost·DecisionTree를 침수흔적도 ∪ NDMS 라벨로 학습, **중권역 단위 + 공간 CV**.
- **예측**: 확률강우 재현주기(50/100/200년) 시나리오.
- **QA 우선**: 경계면(좌표계·격자 정합) 불일치를 증분 검증으로 차단.

## 시작
1. `. .\env.ps1` — 실행 환경(PROJ/GDAL/UTF-8) 고정. (conda 환경 `flood_risk311` 기준)
2. `data/` 아래 형태별 폴더에 자료를 넣는다 → `PROJECT_STRUCTURE.md` 참조.
3. Claude Code에서 "낙동강권역 홍수위험도 평가해줘" 등으로 `flood-risk-orchestrator` 트리거.

상세 구조·워크플로우는 [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)와 [`CLAUDE.md`](CLAUDE.md) 참조.
