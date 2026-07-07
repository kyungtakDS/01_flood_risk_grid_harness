"""격자 계약 검증 래퍼.

data/standard_grid/pre_gridded 의 사전 격자자료, 그리고 표준화 산출물이
마스터 격자 계약(CRS·transform·shape·셀정렬·마스크)을 지키는지 검증한다.
번들 함수 assert_grid_contract 를 프로젝트 경로 규약으로 감싼 실동작 코드다.

스킬: geodata-grid-pipeline, flood-model-validation
담당: geo-data-engineer, validation-inspector
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "geodata-grid-pipeline" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
from align_to_master_grid import assert_grid_contract  # noqa: E402


def verify(master_path: str, factor_path: str) -> list[str]:
    """5개 불변식을 검사하고 위반 목록을 반환한다(빈 리스트 = 통과)."""
    return assert_grid_contract(str(master_path), str(factor_path))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="격자 계약 검증")
    ap.add_argument("--master", required=True)
    ap.add_argument("--factor", required=True)
    args = ap.parse_args()
    violations = verify(args.master, args.factor)
    if violations:
        print("FAIL")
        for m in violations:
            print(f"  - {m}")
        raise SystemExit(1)
    print("PASS")
