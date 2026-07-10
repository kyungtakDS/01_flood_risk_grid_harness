# 데이터 추출 규약 — 소스 → 지표 매핑

대시보드의 모든 숫자는 아래 매핑으로 **파일에서 계산/추출**한다. 지어내지 않는다. 재생성 시 이 규약을 그대로 따라야 수치가 일관된다.

## 범위 규칙 (중요)
이 대시보드는 **홍수위험 도메인 하네스(제품)**를 보고한다. `dashboard-builder` 에이전트/스킬은 대시보드를 "만드는 도구(인프라)"이므로 도메인 지표 카운트에서 **제외**한다. 이렇게 해야 README 배지(`agents-8`, `skills-9`)·config·기존 dashboard.html과 수치가 일치한다.
- 도메인 에이전트 = `.claude/agents/` 중 `dashboard-builder.md`를 뺀 나머지 → **8**
- 도메인 스킬 = `.claude/skills/` 중 `dashboard-builder/`를 뺀 나머지(오케스트레이터 포함) → **9**
- 향후 도메인 에이전트/스킬이 실제로 추가되면 그 수를 반영하고, 필요 시 README 배지 불일치를 사용자에게 보고한다.

## 개수형 지표
| 지표 | 계산법 | 현재값 |
|------|--------|:-----:|
| 에이전트 | `.claude/agents/*.md` 개수 − 인프라(dashboard-builder) | 8 |
| 스킬 | `.claude/skills/*/SKILL.md` 개수 − 인프라(dashboard-builder) | 9 |
| 참조 문서 | 도메인 스킬의 `references/*.md` 개수 | 5 |
| 번들 스크립트 | 도메인 스킬의 `scripts/*` 개수 | 1 |
| 정의 파일 합계 | 위 (도메인 에이전트+스킬+참조+스크립트) 파일 수 | 23 |
| 파이프라인 단계 | 오케스트레이터/기존 대시보드의 처리 스테이지 | 7 |
| 자료 드롭존 | `data/` 하위 투입 폴더 종류 | 8 |

> 개수는 실제 `find`/디렉토리 나열로 재확인한다. 인프라 제외 규칙을 잊지 말 것.

## 계약형 지표 (`config/grid_config.yaml`)
| 지표 | 키 | 값 |
|------|----|----|
| CRS | `crs` | EPSG:5179 |
| 해상도 | `resolution_m` | 100 m |
| NoData | `nodata` | −9999 |
| 원점 snap | `snap_origin` | true |
| 파일 포맷 | `file_format` / `table_format` | COG / GeoParquet |
| 격자 ID | `grid_id` | sw_corner |
| 처리 파티션 | `watershed.partition_by` | 대권역(daegwon) |
| 모델 단위 | `watershed.model_unit` | 중권역(junggwon) |
| ML 모델 | `modeling.models` | 5종 (RF·XGB·LGBM·CatBoost·DT) |
| 라벨 | `modeling.labels` | 침수흔적도 ∪ NDMS |
| CV | `modeling.cv` | spatial_block |
| 재현주기 | `forecast.return_periods` | 50·100·200년 (3) |

## 상태형 지표
| 지표 | 소스 | 값 |
|------|------|----|
| 리허설 결과 | README "리허설 결과" 표 / CLAUDE.md 변경 이력 | 6/6 통과 |
| 리허설 항목 | README 표의 각 행 | 마스터격자·DEM·토지피복·강우·라벨·불일치차단·경사(지형) |
| 자료 준비 현황 | `data/**` 실제 자료 유무(README.md만 있으면 대기) | 드롭존 8종 대기, `_workspace` 검증완료 |
| 런타임 | CLAUDE.md | Python 3.11 · conda `flood_risk311` |
| 리허설 이미지 | `docs/rehearsal_result.png` | 상대경로로 삽입 |

## 도넛 차트 구성 (권장 4+)
1. **리허설 검증**: 통과 6 / 실패 0 — 중앙 "100% · 6/6". 색 good/critical.
2. **하네스 자산 구성**: 에이전트 8 / 스킬 9 / 참조 5 / 스크립트 1 — 중앙 "23 · 정의 파일". 색 s1..s4.
3. **ML 모델 포트폴리오**: RF·XGB·LGBM·CatBoost·DT 각 1 — 중앙 "5 · 모델 비교". 색 s1..s5. 레전드 값은 "●"(로스터).
4. **자료 준비 현황**: 투입 대기 8 / 준비 완료 0 — 중앙 "0/8 · 드롭존". 색 muted/good.

추가 가능(데이터 있으면): **파이프라인 단계 분포**(재해/노출/모델/예측/지도 그룹), **재현주기**(50/100/200).

## 상충 처리
- README 배지와 실제 파일 개수가 다르면 **실제 파일 개수를 표시**하고, footer 또는 보고에 불일치를 명기한다.
- 값을 못 읽으면 그 지표는 비우거나 "미확정"으로 두고 임의값 금지.

## footer 출처(필수)
표시 수치의 근거를 밝힌다: `README.md · CLAUDE.md · config/grid_config.yaml · .claude/agents · .claude/skills · _workspace`.
