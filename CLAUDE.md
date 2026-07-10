# CLAUDE.md

## 하네스: 격자(100m) 전국 홍수위험도 평가·예측

**목표:** 이종 원시자료를 전국 100m 표준격자망(EPSG:5179, 수자원단위 대권역/중권역 파티션)에 표준화하고, 지형·수문·노출·취약성 인자를 통합해 ML(RF·XGBoost·LightGBM·CatBoost·DecisionTree)로 격자별 홍수위험도를 평가·예측한다.

**트리거:** 홍수위험도 평가·예측, 원시자료 표준격자 표준화, 위험지도 제작, 재현주기 예측 등 이 도메인 작업 요청 시 `flood-risk-orchestrator` 스킬을 사용하라. 특정 단계만(표준화만·인자만·모델만·지도만) 다시 하거나, 재현주기를 바꿔 예측하거나, 새 자료로 갱신하는 후속 요청도 동일 스킬로 처리한다. 단순 개념 질문은 직접 응답 가능.

**핵심 계약:** 모든 격자 산출물은 `.claude/skills/geodata-grid-pipeline/references/grid-standard.md`의 표준격자망 규격(격자 계약)을 준수한다. `validation-inspector`가 이를 강제 검증한다.

**프로젝트 구조:** 자료 드롭존·코드 골격은 `PROJECT_STRUCTURE.md` 참조. 사용자는 `data/raw/{point,polygon,raster,tabular,timeseries}`에 원시자료를, `data/standard_grid/{grid_master,pre_gridded}`에 기제작 표준격자망을, `data/labels`에 침수흔적도·NDMS를, `data/watershed`에 수자원단위지도를 넣는다. 변환·모델링 코드는 `src/`(스킬별 대응), 설정은 `config/grid_config.yaml`. **실행 전 반드시 `. .\env.ps1`로 PROJ 경로를 conda 환경에 고정**(시스템 PostgreSQL PROJ 충돌 방지 — 미고정 시 재투영 실패).

**실행 모드:** 에이전트 팀(Phase별 재구성, 활성 팀 ≤5, 증분 QA). 모든 에이전트 `model: opus`.

**보조 하네스 — 운영 대시보드:** 하네스 구성·상태·산출물을 한 화면에 요약하는 대시보드 요청("대시보드 만들어줘/갱신", "현황 시각화", "노션/Linear·도넛 차트 대시보드") 시 `dashboard-builder` 스킬을 사용하라(서브 에이전트 모드, 단일 전문가). 실제 파일에서 지표를 추출해 밝은 배경·Chart.js 원형 차트 HTML을 별도 파일(기본 `dashboard_v2.html`)로 출력하며, **기존 `dashboard.html`은 변경하지 않는다.**

**런타임 환경:** Python 코드는 **conda 환경 `flood_risk311`**(Python 3.11, `C:\miniconda3\envs\flood_risk311\python.exe`)에서 실행한다. 설치 확인됨: rasterio·geopandas·shapely·numpy·scikit-learn·xgboost·lightgbm·catboost·rasterstats·rioxarray·xarray·pyproj, 그리고 지형분석 표준 도구 **whitebox(WhiteboxTools)**. **richdem은 사용하지 않는다 — 지형 인자는 WhiteboxTools로 통일.** pyproj의 PROJ DB 경로 경고가 있어 재투영 전 `PROJ_DATA` 확인 권장.

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-07-07 | 초기 구성(에이전트 8 + 스킬 9 + 오케스트레이터) | 전체 | - |
| 2026-07-07 | ML 모델군 5종(RF·XGBoost·LightGBM·CatBoost·DecisionTree) + 타깃(침수흔적도·NDMS 포인트) 반영 | flood-risk-index-modeling, geodata-grid-pipeline | 사용자 요구 |
| 2026-07-07 | 수자원단위 대권역/중권역 파티션 + 중권역 단위 ML 모델링 반영 | grid-standard/watershed-units, 인자·모델·예측·오케스트레이터 스킬 | 사용자 요구(부하 저감·유역 일관성) |
| 2026-07-07 | 라벨의 원시/사전격자 이중 제공 처리(계약 검증 후 사용) 반영 | geodata-grid-pipeline | 사용자 요구 |
| 2026-07-07 | 런타임 환경 `flood_risk311` 지정 기록 + 미설치 패키지 명시 | CLAUDE.md | 사용자 지정, 하네스 검증 |
| 2026-07-07 | 모델·보조 패키지 설치 확인, richdem 제거하고 지형분석을 WhiteboxTools로 통일 | CLAUDE.md, terrain-hazard-factors | 사용자 지정 |
| 2026-07-07 | 낙동강 축소 AOI 테스트 리허설 6/6 통과, PROJ 충돌 발견·해결(env.ps1) | _workspace, env.ps1 | 첫 실행 리허설 |
| 2026-07-07 | 프로젝트 구조 생성(data/raw·standard_grid·labels·watershed 드롭존, src/ 코드 골격, config, outputs) | data/·src/·config/·PROJECT_STRUCTURE.md | 사용자 요구(자료 제공·코드 공간) |
| 2026-07-10 | 보조 하네스 추가: 운영 대시보드(dashboard-builder 에이전트+스킬, 서브 에이전트 모드). 실제 파일 지표 추출 → Notion+Linear·밝은 배경·Chart.js 도넛 대시보드. 기존 dashboard.html 무변경, 별도 `dashboard_v2.html` 출력 | .claude/agents/dashboard-builder.md, .claude/skills/dashboard-builder/, dashboard_v2.html | 사용자 요구(현황 대시보드 제작) |
