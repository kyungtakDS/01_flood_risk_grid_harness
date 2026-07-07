---
name: terrain-hazard-factors
description: "표준화된 DEM에서 홍수 재해와 관련된 지형(geomorphometry) 인자를 100m 격자로 산출하는 스킬. 경사(slope), 저지대/상대고도, 지형습윤지수(TWI), HAND(하천수면 상대고도), 곡률(curvature), 흐름누적(flow accumulation), 지형위치지수(TPI)를 계산. '지형 인자', 'TWI', 'HAND', '저지대 추출', '경사도 래스터', '흐름누적/흐름방향', 'DEM 기반 홍수 지형분석' 요청 시 이 스킬을 사용. 마스터 격자에 정렬된 지형 인자 래스터가 필요할 때 사용."
---

# Terrain Hazard Factors — 지형 재해인자 산출

표준화된 DEM에서 "물이 어디로 모이고 어디가 잠기기 쉬운가"를 나타내는 지형 인자를 산출한다. 이 인자들은 홍수 재해(hazard)의 지형적 소인(素因)이다.

## 전제
- 입력 DEM은 이미 `geodata-grid-pipeline`이 마스터 격자로 표준화한 `_workspace/02_grid/dem.tif`.
- 모든 산출은 마스터 격자에 정렬한다. 작업 전 `references`의 격자 계약(`../geodata-grid-pipeline/references/grid-standard.md` 또는 리더가 제공하는 경로)을 확인한다.

## DEM 전처리 (필수 선행)
지형 흐름 분석 전 DEM의 **함몰지(sink/depression)를 채운다**(fill 또는 breach). 채우지 않으면 흐름누적이 함몰지에서 끊겨 하천망이 조각난다. 단, 실제 저류지·호수는 과도한 fill로 왜곡되지 않도록 breach-first 후 최소 fill을 권장한다.

## 흐름기반 인자는 완전유역 위에서 계산 (중요)
흐름누적·하천망·HAND·유역경계 같은 **흐름기반 인자는 수자원단위지도 대권역(완전 유역) 단위로 계산**한 뒤 중권역으로 잘라 쓴다. 중권역 타일 경계에서 흐름누적을 자르면 상류 집수가 잘려 물길이 조각나기 때문이다(치명적 오류). 경사·곡률 같은 국지 인자는 타일 단위 계산도 무방. 상세는 `../geodata-grid-pipeline/references/watershed-units.md` §3 참조.

## 핵심 인자와 산출 방법

| 인자 | 의미 | 산출 | 홍수 해석 |
|------|------|------|----------|
| 경사(slope) | 지표 기울기(도/비율) | DEM 1차 미분 | 완경사일수록 물이 정체·집적, 위험↑ |
| 흐름방향/흐름누적 | 상류 집수 셀 수 | D8/D-infinity | 누적 큼 = 물길, 범람 잠재 |
| TWI(지형습윤지수) | ln(집수면적/tanβ) | 흐름누적·경사 조합 | 높을수록 포화·습윤, 침수 소인 |
| HAND | 가장 가까운 하천수면 대비 상대고도 | 하천망 기준 배수 정규화 | 낮을수록 하천 범람 시 침수 |
| 상대고도/저지대 | 국지 최소값 대비 높이 | 국지 통계·TPI | 주변보다 낮은 셀 = 저류·침수 |
| 곡률(curvature) | 오목/볼록 | DEM 2차 미분 | 오목부는 물 집적 |
| TPI/TRI | 지형위치·거칠기 | 이웃 창 통계 | 저지·평탄 판별 보조 |

> HAND와 하천망은 수문 인자와 강하게 얽힌다. 하천망 정의(차수·기준 집수임계)는 `hydro-hazard-analyst`와 **반드시 합의**한다. 서로 다른 하천망을 쓰면 HAND(지형)와 하천거리(수문)가 모순된다.

## 도구
- **`whitebox`(WhiteboxTools)를 지형·지형수문 분석의 표준 도구로 사용한다.** 함몰처리(breach/fill), 흐름방향·흐름누적, 경사·곡률, TWI, HAND, wetness 등 대부분의 지형 인자를 한 도구로 일관되게 산출한다(도구 혼용에 따른 알고리즘 불일치를 피한다).
- `rasterio`/`numpy`/`scipy.ndimage`: whitebox가 직접 제공하지 않는 국지 통계·창 연산(TPI·상대고도 등) 보조.
- 항상 마스터 격자 정렬을 유지: 산출 후 `assert_grid_contract`로 셀프체크.

## 왜 정규화가 필요한가
인자마다 스케일이 다르다(경사 0~90도, TWI 음수~20+, HAND 0~수백m). 모델러가 결합하기 쉽도록 원값 래스터를 산출하되, 필요 시 0~1 정규화 버전도 함께 제공한다. 정규화 방식(min-max, 백분위 클리핑)은 태그에 기록한다. 극단 이상치는 상하위 백분위 클리핑으로 완화한다.

## 출력
- `_workspace/03_terrain_slope.tif`, `_terrain_twi.tif`, `_terrain_hand.tif`, `_terrain_flowacc.tif`, `_terrain_lowland.tif`, `_terrain_curvature.tif` 등 (단일밴드 COG, 마스터 정렬)
- 각 파일 태그: `standardization_method`, 원천 DEM 해상도, 정규화 여부

## 팀 협업 요점
- `hydro-hazard-analyst`에게: 흐름누적·하천망·유역경계를 SendMessage로 공유(수문 인자가 이를 재사용).
- `hydro`로부터 하천망 정의를 받으면 HAND를 그 기준으로 산출.
- `flood-risk-modeler`에게: 산출 인자 목록과 스케일/정규화 정보 전달.

## 이전 산출물이 있을 때 (재호출)
`_workspace/03_terrain_*`가 존재하면 사용자 피드백이 지정한 인자만 재산출한다. DEM이 갱신된 경우에만 전 인자를 재계산하고, 그 사실을 hydro/modeler에게 알린다.
