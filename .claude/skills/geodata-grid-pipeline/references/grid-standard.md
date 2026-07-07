# 표준격자망 규격 (Grid Contract)

이 문서는 전국 100m 홍수위험도 하네스의 **단일 진실 원천(single source of truth)**이다. 모든 에이전트가 산출하는 래스터·테이블은 이 계약을 준수해야 하며, `validation-inspector`는 이 계약 위반을 런타임 오류의 최상위 원인으로 간주하고 강제 검증한다.

> **왜 계약인가:** 웹 개발에서 API 응답 shape과 프론트 훅 타입이 어긋나면 런타임 크래시가 나듯, 지리공간에서는 CRS·격자 원점·해상도·NoData 규약이 어긋나면 격자들이 물리적으로 겹치지 않아 이후 모든 인자 중첩·모델 학습이 조용히 오염된다. TypeScript 캐스팅이 타입 버그를 숨기듯, `numpy` 배열 연산은 shape만 같으면 좌표가 어긋나도 그냥 계산해 버린다. 그래서 계약을 명문화하고 교차검증한다.

## 목차
1. [마스터 격자 사양](#1-마스터-격자-사양)
2. [격자 ID 체계](#2-격자-id-체계)
3. [NoData·결측 규약](#3-nodata결측-규약)
4. [파일 포맷·명명 규약](#4-파일-포맷명명-규약)
5. [정합성 불변식(invariants)](#5-정합성-불변식invariants)
6. [계약 준수 검증 절차](#6-계약-준수-검증-절차)

---

## 1. 마스터 격자 사양

| 항목 | 값 | 비고 |
|------|-----|------|
| 좌표계(CRS) | **EPSG:5179** (Korea 2000 / Unified CS, UTM-K, GRS80 타원체) | 전국 단일. WGS84/UTM-52N 등 원시자료는 반드시 재투영 |
| 해상도 | **100 m × 100 m** 정사각 | pixel size = (100, -100) |
| 픽셀 정렬 | 좌표가 **100의 배수**에 snap (origin_x % 100 == 0, origin_y % 100 == 0) | 통계청 SGIS 100m 격자 호환 |
| 축 방향 | 북상(north-up). transform = `Affine(100, 0, X0, 0, -100, Y0)` | 회전 없음 |
| 대상 범위 | 전국 육지 + 도서. 해양·국외 = NoData | `grid_master.tif`의 유효셀이 곧 분석 대상 |

**마스터 격자(`grid_master.tif`)**: 데이터 엔지니어가 Phase 2에서 가장 먼저 생성하는 기준 래스터. 이후 모든 인자 래스터는 이 파일의 CRS·transform·shape·범위를 **그대로 복사**해 정렬한다. "격자를 새로 만들지 말고, 마스터에 맞춰라"가 원칙이다.

> **원점 결정:** 전국 처리 시 국가 표준 격자 원점을 사용한다. 부분 지역(유역 단위) 처리 시에도 원점은 국가 격자에 snap된 좌표를 사용해, 나중에 전국 모자이크가 가능하도록 한다. 임의 원점(예: 데이터 bounding box 좌하단)을 쓰면 지역 간 격자가 어긋나므로 금지.

> **유역 기반 파티셔닝:** 전국은 수자원단위지도의 **대권역(한강·낙동강·금강·영산강·섬진강)** 단위로 처리하고, **중권역** 단위로 ML 모델링한다(부하 저감 + 공간 CV 블록). 모든 유역 타일은 국가 원점에 snap된 좌표를 공유해 경계에서 어긋나지 않아야 한다. 위계·파티셔닝·완전유역 처리 규칙은 [`watershed-units.md`](watershed-units.md) 참조.

---

## 2. 격자 ID 체계

각 셀은 join 키가 되는 안정적 ID를 가진다.

- **표준 격자코드**: SW(좌하단) 모서리 좌표를 인코딩. 형식 `{X0}_{Y0}` (예: `958000_1948000`) 또는 통계청 다마 코드 체계.
- 100m 격자의 SW 좌표는 항상 100의 배수이므로 ID가 유일하고 재현 가능하다.
- 인자 테이블(GeoParquet)은 이 ID를 기본키로 사용하며, 래스터 셀의 (row, col)과 결정적으로 상호변환 가능해야 한다:
  - `X0 = transform.c + col * 100`
  - `Y0 = transform.f + (row + 1) * (-100)` (셀 좌하단)

> **왜 좌표 인코딩 ID인가:** 순번 ID(0,1,2…)는 격자 범위가 바뀌면 깨진다. 좌표 기반 ID는 어떤 지역·시점에도 동일 셀이 동일 ID를 가지므로, 시계열·다중 소스 join과 전국 모자이크에서 안전하다.

---

## 3. NoData·결측 규약

| 데이터 성격 | NoData 표현 | 규칙 |
|------------|------------|------|
| 연속형(고도, 강우, 지수) | `NaN`(float32) 또는 `-9999` | 파일에 nodata 태그를 명시. **결측을 0으로 채우지 말 것** |
| 범주형(토지피복 코드 등) | `0` 또는 명시된 nodata 정수 | 유효 코드와 겹치지 않는 값 사용 |
| 마스크(육지=1/해양=0) | uint8, nodata 없음 | 마스터 마스크로 사용 |

**핵심 원칙: 결측 ≠ 0.** 예를 들어 강우량 결측 셀을 0mm로 채우면 "비가 안 왔다"로 오해되어 위험도가 왜곡된다. 결측은 결측으로 전파하고, 모델 단계에서 명시적으로 대치(impute)하거나 제외한다. NoData 처리 방식은 인자별로 기록해 검증자가 추적할 수 있게 한다.

---

## 4. 파일 포맷·명명 규약

- **래스터**: Cloud-Optimized GeoTIFF(COG), 인자당 **단일 밴드**, float32(연속) / uint8·int16(범주). 내부 타일링 + 오버뷰 포함.
- **테이블**: GeoParquet(격자 ID + 인자 컬럼). 인자 통합 스택은 하나의 넓은 테이블로 합류.
- **명명**: `{phase}_{agent}_{factor}.tif` (예: `03_terrain_twi.tif`, `03_hydro_rain_100yr.tif`). 워크스페이스 경로는 오케스트레이터가 `_workspace/` 기준으로 관리.
- **메타데이터**: 각 래스터 태그에 `source`, `standardization_method`, `nodata`, `created_by`, `crs=EPSG:5179`를 기록. 검증·감사 추적에 사용.

---

## 5. 정합성 불변식(invariants)

모든 인자 래스터는 아래 5개 불변식을 **동시에** 만족해야 한다. 하나라도 깨지면 계약 위반.

1. **CRS 일치**: `raster.crs == EPSG:5179`
2. **Transform 일치**: `raster.transform == grid_master.transform` (원점·픽셀크기 완전 일치)
3. **Shape 일치**: `(raster.height, raster.width) == grid_master shape`
4. **셀 정렬**: 임의 셀의 중심 좌표가 마스터의 동일 인덱스 셀 중심과 일치(부동소수 허용오차 ≤ 1e-6 m)
5. **마스크 정합**: 마스터가 NoData인 셀은 인자 래스터에서도 NoData (육지 밖에 값이 새지 않음)

> **왜 5개 전부인가:** shape만 같고 transform이 다르면 배열 연산은 성공하지만 지리적으로 어긋난 셀끼리 곱해진다(가장 위험한 침묵 버그). CRS만 같고 원점이 다르면 100m 절반씩 밀린 채 중첩된다. 5개를 함께 봐야 "물리적으로 같은 셀"임이 보장된다.

---

## 6. 계약 준수 검증 절차

`validation-inspector`가 각 인자 산출 직후(증분 QA) 및 최종 단계에서 실행:

```
for each factor_raster in _workspace:
    assert crs(factor) == EPSG:5179                      # 불변식 1
    assert transform(factor) == transform(grid_master)   # 불변식 2
    assert shape(factor)     == shape(grid_master)        # 불변식 3
    assert cell_center_aligned(factor, grid_master)       # 불변식 4
    assert nodata_within_land_mask(factor, grid_master)   # 불변식 5
    log(factor.tags['standardization_method'])            # 방법 추적
```

`scripts/align_to_master_grid.py`의 `assert_grid_contract()` 함수가 이 검사를 코드로 제공한다. 위반 시 해당 자료를 재표준화(1회 재시도)하고, 재실패 시 검증 리포트에 누락으로 명시한 뒤 진행한다(삭제 금지).
