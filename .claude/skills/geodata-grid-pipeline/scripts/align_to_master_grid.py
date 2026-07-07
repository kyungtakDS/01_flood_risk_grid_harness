"""
align_to_master_grid.py — 표준격자망(Grid Contract) 정합 유틸리티

원시자료(래스터/벡터/포인트/집계표)를 마스터 격자에 정합시키고,
격자 계약 불변식을 코드로 강제 검증한다. 하네스의 여러 에이전트가
공통으로 작성하게 되는 재투영·snap·정합·검증 로직을 한 곳에 번들링했다.

의존성: rasterio, numpy, geopandas, shapely, rasterstats (필요 함수별)
이 파일은 스텁이자 참조 구현이다. 실데이터 파이프라인에서 임포트해 사용하거나
필요한 함수만 복사해 확장한다.

핵심 원칙
- 격자를 새로 만들지 말고, 마스터 격자에 맞춰라.
- 결측 ≠ 0. NoData는 NoData로 전파하라.
- 범주형에 연속형 리샘플(bilinear/cubic)을 쓰지 마라.

CLI:
    python align_to_master_grid.py check   --master grid_master.tif --factor f.tif
    python align_to_master_grid.py raster  --master grid_master.tif --src dem.tif  --dst dem_100m.tif --resampling bilinear
    python align_to_master_grid.py vector  --master grid_master.tif --src rivers.shp --dst dist_river.tif --mode distance
"""
from __future__ import annotations

import argparse
import sys

MASTER_CRS = "EPSG:5179"
CELL = 100.0
ALIGN_TOL_M = 1e-6  # 셀 정렬 허용오차(미터)


# --------------------------------------------------------------------------- #
# 1. 계약 검증 (validation-inspector 및 각 에이전트의 증분 QA가 호출)
# --------------------------------------------------------------------------- #
def assert_grid_contract(master_path: str, factor_path: str) -> list[str]:
    """격자 계약 5개 불변식을 검사하고 위반 목록을 반환한다(빈 리스트=통과).

    불변식: (1)CRS (2)transform (3)shape (4)셀 정렬 (5)마스크 정합.
    references/grid-standard.md §5 참조.
    """
    import rasterio  # 지연 임포트: CLI 없이 함수만 쓸 때 의존성 최소화

    violations: list[str] = []
    with rasterio.open(master_path) as m, rasterio.open(factor_path) as f:
        # (1) CRS
        if f.crs is None or f.crs.to_string() != MASTER_CRS:
            violations.append(f"CRS 불일치: {f.crs} != {MASTER_CRS}")
        # (2) transform (원점·픽셀크기)
        if not _transforms_equal(f.transform, m.transform):
            violations.append(f"transform 불일치: {f.transform} != {m.transform}")
        # (3) shape
        if (f.height, f.width) != (m.height, m.width):
            violations.append(
                f"shape 불일치: {(f.height, f.width)} != {(m.height, m.width)}"
            )
        # (4) 셀 정렬 — 원점이 100 배수에 snap 되어 있는지 + 마스터와 정렬
        if abs(f.transform.c % CELL) > ALIGN_TOL_M or abs(f.transform.f % CELL) > ALIGN_TOL_M:
            violations.append("원점이 100m 격자에 snap 되지 않음")
        # (5) 마스크 정합 — 마스터 NoData 영역에 값이 새지 않는지
        if (f.height, f.width) == (m.height, m.width):
            import numpy as np
            ma = m.read(1, masked=True)
            fa = f.read(1, masked=True)
            leaked = np.logical_and(ma.mask, ~fa.mask)
            if leaked.any():
                violations.append(
                    f"마스크 정합 위반: 육지밖(마스터 NoData) 셀 {int(leaked.sum())}개에 값 존재"
                )
    return violations


def _transforms_equal(a, b, tol: float = ALIGN_TOL_M) -> bool:
    return all(abs(x - y) <= tol for x, y in zip(tuple(a)[:6], tuple(b)[:6]))


# --------------------------------------------------------------------------- #
# 2. 래스터 → 마스터 정합 (재투영 + snap + 리샘플)
# --------------------------------------------------------------------------- #
def align_raster(src_path: str, master_path: str, dst_path: str,
                 resampling: str = "bilinear") -> str:
    """연속/범주 래스터를 마스터 격자에 재투영·정합한다.

    resampling: 연속형은 'bilinear'/'cubic', 범주형은 'nearest'/'mode'.
    범주형에 bilinear를 쓰면 존재하지 않는 코드가 보간으로 생겨나므로 금지.
    """
    import rasterio
    from rasterio.warp import reproject, Resampling

    rs = getattr(Resampling, resampling)
    with rasterio.open(master_path) as m:
        dst_profile = m.profile.copy()
        with rasterio.open(src_path) as src:
            dst_profile.update(count=src.count, dtype="float32")
            import numpy as np
            with rasterio.open(dst_path, "w", **dst_profile) as dst:
                for b in range(1, src.count + 1):
                    out = np.empty((m.height, m.width), dtype="float32")
                    reproject(
                        source=rasterio.band(src, b),
                        destination=out,
                        src_transform=src.transform, src_crs=src.crs,
                        dst_transform=m.transform, dst_crs=m.crs,
                        resampling=rs,
                    )
                    dst.write(out, b)
                dst.update_tags(standardization_method=f"reproject+{resampling}",
                                crs=MASTER_CRS)
    return dst_path


# --------------------------------------------------------------------------- #
# 3. 벡터 → 마스터 정합 (거리변환/래스터화/집계)
# --------------------------------------------------------------------------- #
def align_vector(src_path: str, master_path: str, dst_path: str,
                 mode: str = "distance", value_field: str | None = None) -> str:
    """벡터를 마스터 격자로 표준화한다.

    mode:
      'distance' — 라인/폴리곤까지의 거리변환 (하천 근접 등)
      'rasterize'— value_field 값을 셀에 래스터화 (범주 폴리곤)
      'coverage' — 폴리곤의 셀 내 피복률(%) (면적가중)
    이 함수는 인터페이스 스텁이다. 실제 구현은 목적에 맞춰 확장한다.
    """
    import geopandas as gpd

    gdf = gpd.read_file(src_path)
    if gdf.crs is None:
        raise ValueError("원본 CRS가 없음 — 반드시 확인 후 지정하라(무단 가정 금지)")
    gdf = gdf.to_crs(MASTER_CRS)  # 마스터 CRS로 재투영
    # 이하 mode별 구현: rasterize / 거리변환 / rasterstats coverage
    # (스텁) 실제 산출은 rasterio.features.rasterize + scipy.ndimage.distance_transform_edt 등 사용
    _ = (gdf, master_path, dst_path, mode, value_field)
    return dst_path


def dasymetric_disaggregate(admin_path: str, value_field: str,
                            weight_raster: str, master_path: str, dst_path: str) -> str:
    """행정구역 단위 통계값을 가중 래스터(건물/불투수면 등)로 하향식 분배한다.

    각 행정단위 총량을 가중치 비율에 따라 격자에 배분하되, 단위 내 합이
    원래 총량과 보존되도록 한다(질량 보존). 인구·자산 격자화의 표준 기법.
    """
    _ = (admin_path, value_field, weight_raster, master_path, dst_path)  # 스텁
    return dst_path


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="표준격자망 정합 유틸리티")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="격자 계약 검증")
    c.add_argument("--master", required=True)
    c.add_argument("--factor", required=True)

    r = sub.add_parser("raster", help="래스터 정합")
    r.add_argument("--master", required=True)
    r.add_argument("--src", required=True)
    r.add_argument("--dst", required=True)
    r.add_argument("--resampling", default="bilinear")

    v = sub.add_parser("vector", help="벡터 정합")
    v.add_argument("--master", required=True)
    v.add_argument("--src", required=True)
    v.add_argument("--dst", required=True)
    v.add_argument("--mode", default="distance")
    v.add_argument("--value-field", default=None)

    args = p.parse_args(argv)

    if args.cmd == "check":
        violations = assert_grid_contract(args.master, args.factor)
        if violations:
            print("계약 위반:")
            for msg in violations:
                print(f"  - {msg}")
            return 1
        print("계약 통과: 5개 불변식 만족")
        return 0
    if args.cmd == "raster":
        print(align_raster(args.src, args.master, args.dst, args.resampling))
        return 0
    if args.cmd == "vector":
        print(align_vector(args.src, args.master, args.dst, args.mode, args.value_field))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
