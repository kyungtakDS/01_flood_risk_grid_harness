---
name: flood-risk-orchestrator
description: "전국 100m 격자 홍수위험도 평가·예측 에이전트 팀을 조율하는 오케스트레이터. 원시자료 표준격자 표준화 → 지형·수문·노출 인자 → ML(RandomForest·XGBoost·LightGBM·CatBoost·DecisionTree) 위험지수 → 재현주기 예측 → 검증 → 위험지도까지 전 과정을 관리. '홍수위험도 시스템/평가/예측', '전국 홍수위험 격자 만들어줘', '침수 위험지도 제작', '홍수위험도 하네스 실행' 요청 시 이 스킬을 사용. 후속 작업: 홍수위험도 다시 실행/재실행/업데이트/보완/수정, 특정 단계만 다시(표준화만·인자만·모델만·지도만), 재현주기 바꿔서 예측, 새 자료로 갱신, 이전 결과 개선 요청 시에도 반드시 이 스킬을 사용."
---

# Flood Risk Orchestrator — 전국 홍수위험도 팀 오케스트레이터

전국 100m 격자 홍수위험도를 평가·예측하는 에이전트 팀을 조율해 위험지도·리포트를 산출한다.

## 실행 모드: 에이전트 팀 (Phase별 팀 재구성)

세션당 1팀만 활성 가능하므로, Phase 경계에서 `TeamDelete`→`TeamCreate`로 팀을 교체한다. 산출물은 `_workspace/`에 파일로 보존되어 다음 팀이 Read로 이어받는다. 활성 팀은 항상 ≤5명으로 유지한다.

`validation-inspector`는 **증분 QA**로 여러 Phase에 걸쳐 참여한다(각 산출 직후 격자 계약 검증).

## 에이전트 구성

| 팀원 | 에이전트 타입 | 역할 | 스킬 | 출력 |
|------|-------------|------|------|------|
| geo-data-engineer | 커스텀 | 원시자료 → 표준격자 표준화 + 라벨(침수흔적도∪NDMS) 격자화 | geodata-grid-pipeline | `02_grid/*.tif`, `labels.tif` |
| terrain-hazard-analyst | 커스텀 | 지형 재해인자 | terrain-hazard-factors | `03_terrain_*.tif` |
| hydro-hazard-analyst | 커스텀 | 수문 재해인자(재현주기 강우 포함) | hydro-hazard-factors | `03_hydro_*.tif` |
| exposure-vulnerability-analyst | 커스텀 | 노출·취약성 인자 | exposure-vulnerability-factors | `03_expo_*.tif` |
| flood-risk-modeler | 커스텀 | 5개 트리모델 학습·비교 → 위험지수 | flood-risk-index-modeling | `04_risk_index.tif` |
| scenario-forecaster | 커스텀 | 재현주기별 예측 | flood-forecast-scenarios | `04_forecast_{RP}yr.tif` |
| validation-inspector | general-purpose | 격자 계약·모델 검증(증분+최종) | flood-model-validation | `05_validation_report.md` |
| geo-cartographer | 커스텀 | 위험지도·COG·리포트 | flood-risk-cartography | `06_riskmap.*`, 리포트 |

모든 Agent/TeamCreate 호출에 `model: "opus"`를 명시한다.

## 워크플로우

### Phase 0 — 컨텍스트 확인 (후속 작업 지원)
`_workspace/` 존재 여부로 실행 모드 결정:
- **미존재** → 초기 실행. Phase 1로.
- **존재 + 부분 수정 요청**(예: "모델만 다시", "재현주기 200년 추가") → 부분 재실행. 해당 Phase 팀만 재구성, 이전 산출물 경로를 프롬프트에 포함해 개선 반영.
- **존재 + 새 입력** → 새 실행. 기존 `_workspace/`를 `_workspace_{YYYYMMDD_HHMMSS}/`로 이동 후 Phase 1.

### Phase 1 — 준비
1. 입력 분석: 대상 범위(전국/대권역/유역), 원시자료 목록, 재현주기 세트(기본 50/100/200년), 라벨 자료(침수흔적도·NDMS — **원시 또는 이미 격자화된 형태** 모두 가능).
2. 격자 계약 + 유역 규약 로드: `geodata-grid-pipeline/references/grid-standard.md`와 `watershed-units.md`를 읽어 팀 전체 기준으로 삼는다.
3. **유역 파티션 결정**: 전국은 수자원단위지도 **대권역(한강·낙동강·금강·영산강·섬진강)** 단위로 처리하고 **중권역**을 ML 모델링·공간 CV 단위로 삼는다.
4. `_workspace/` 생성, 원시자료를 `_workspace/00_input/`에 배치.

### Phase 2 — 표준화 [팀: data-engineer + validation-inspector]
**활성 팀(2):** `TeamCreate("flood-standardize", [geo-data-engineer, validation-inspector])`
1. `TaskCreate`: 대권역별 마스터 격자 생성 → 입력 형태 판별(원시 vs 이미 격자화) → 유형별 표준화(폴리곤/포인트/라인/래스터/집계/시계열) 또는 격자 제공본 계약 검증 → 라벨(침수흔적도/침수위험지도 폴리곤 ∪ NDMS 포인트) 격자화. 격자 속성에 유역코드(대권역·중권역) 부착.
2. data-engineer가 각 자료 표준화/검증 완료 시 validation-inspector에게 SendMessage → **즉시 계약 검증**(증분 QA). 위반 시 재표준화(1회). 이미 격자화된 입력도 무검증 통과 금지(원점·CRS·NoData 확인).
3. 완료 후 `TeamDelete`. 산출물은 `02_grid/`에 보존.

> **이 관문이 가장 중요하다.** 여기서 막지 못한 격자 어긋남은 이후 전 Phase를 침묵 오염시킨다.

### Phase 3 — 인자 분석 [팀: 3 analysts + validation-inspector]
**활성 팀(4):** `TeamCreate("flood-factors", [terrain-hazard-analyst, hydro-hazard-analyst, exposure-vulnerability-analyst, validation-inspector])`
1. `TaskCreate`: 지형/수문/노출 인자 병렬 산출(팬아웃).
2. terrain ↔ hydro가 **흐름누적·하천망·유역·HAND를 SendMessage로 공유**(하천망 정의 합의 — 불일치 시 HAND와 하천거리가 모순).
3. 각 인자 래스터 산출 즉시 validation-inspector가 마스터 정렬 확인(증분 QA).
4. 완료 후 `TeamDelete`. 산출물 `03_*`에 보존.

### Phase 4 — 통합·예측 [팀: modeler + forecaster]
**활성 팀(2):** `TeamCreate("flood-model", [flood-risk-modeler, scenario-forecaster])`
1. modeler: 인자 스택 정합 확인 → **중권역 단위**로 학습표 구성(라벨: 침수흔적도∪NDMS) → **5개 트리모델(RF·XGBoost·LightGBM·CatBoost·DecisionTree) 학습·비교**(중권역=공간 CV 블록) → 최적/앙상블 선택 → 중권역 예측을 국가 원점 정렬로 모자이크 → `04_risk_index.tif` + 중요도 + 불확실성 + 모델카드. 라벨 희소 중권역은 대권역 공유 모델로 상향 조정.
2. forecaster: modeler의 학습 모델 + hydro의 재현주기 강우로 중권역별 시나리오 예측 → 모자이크 `04_forecast_{RP}yr.tif`. 모델러↔예보자 SendMessage 조율(모델 재사용, 강우만 교체).
3. 완료 후 `TeamDelete`.

### Phase 5 — 최종 검증 [단독: validation-inspector]
서브 에이전트로 호출(팀 통신 불필요, 독립 검증). 침수흔적도·NDMS 라벨 대비 성능(ROC/PR-AUC, POD/FAR/CSI), 공간 과적합·라벨 누수, 계약 최종 정합성, 불확실성 → `05_validation_report.md`. 심각한 문제 발견 시 리더에게 보고 후 해당 Phase 부분 재실행.

### Phase 6 — 산출 [단독: geo-cartographer]
서브 에이전트로 호출. 위험지수·시나리오 등급화 → 위험지도(COG)·웹타일·통계·리포트. 검증 리포트의 한계·불확실성을 반영.

### Phase 7 — 정리·진화
1. 활성 팀 정리(TeamDelete). `_workspace/` 보존(감사 추적).
2. 사용자에게 결과 요약 보고 + **피드백 요청**("결과·팀 구성·워크플로우에 개선점이 있나요?").
3. 피드백 반영 시 CLAUDE.md 변경이력에 기록.

## 데이터 흐름

```
00_input(원시) ─engineer→ 02_grid(표준격자)+labels ─┬→ terrain ─┐
                                                      ├→ hydro ──┼→ 인자스택 ─modeler→ 04_risk_index
                                                      └→ expo ───┘        │              │
                                     재현주기강우 ───────────────────────┘   forecaster→ 04_forecast_{RP}
                                                                                          │
        validation(증분/최종) ── 계약검증·성능검증 ────────────→ 05_report   cartographer→ 06_riskmap+리포트
```
격자 계약이 모든 파일 교환의 스키마. 전달: 파일 기반(산출물) + 태스크 기반(조율) + 메시지 기반(실시간 공유).

## 에러 핸들링

| 상황 | 전략 |
|------|------|
| 격자 계약 위반 | 해당 자료 재표준화 1회 재시도 → 실패 시 리포트에 누락 명시하고 진행(삭제 금지) |
| 라벨 부족(침수이력 희소) | modeler가 보조 AHP 가중지수 병행, 리포트에 라벨 한계 명시 |
| 팀원 실패/중지 | 리더가 유휴 알림 감지 → SendMessage 상태 확인 → 재시작/재할당 |
| 상충 자료 | 출처 병기 후 보존, 삭제 금지 |
| 모델 성능 저조 | 인자 보강·표본 재설계 요청, 과적합 여부 검증자와 교차 확인 |
| 타임아웃 | 현재까지 부분 결과로 진행, 미완료 팀원 종료 |

## 테스트 시나리오

### 정상 흐름
1. 사용자가 특정 유역의 DEM·토지피복·하천망·강우·침수흔적도·NDMS 포인트를 `00_input/`에 제공.
2. Phase 2: 마스터 격자 생성, 6종 자료 유형별 표준화, 라벨 격자화 → 증분 검증 통과.
3. Phase 3: 지형·수문·노출 인자 병렬 산출(하천망 합의) → 정렬 검증 통과.
4. Phase 4: 5개 모델 학습·비교 → 최적 모델로 위험지수, 50/100/200년 예측.
5. Phase 5: PR-AUC·POD/FAR 산출, 공간 CV 확인, 계약 최종 통과.
6. Phase 6: 등급화 위험지도·리포트 산출.
7. 예상 결과: `06_riskmap_*.tif` + `06_flood_risk_report.md` 생성.

### 에러 흐름 (계약 관문 검증)
1. Phase 2에서 강우 래스터가 WGS84(EPSG:4326)로 들어와 마스터(EPSG:5179)와 CRS 불일치.
2. validation-inspector 증분 QA가 불변식 1(CRS) 위반 감지 → data-engineer에게 재투영 요청.
3. 재표준화 후 통과 → Phase 3 진행.
4. 만약 재시도도 실패하면 해당 강우 격자를 누락 처리하고 리포트에 명시, 나머지로 진행.
