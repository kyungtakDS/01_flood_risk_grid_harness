# outputs/ — 최종 산출물

하네스 실행의 최종 결과물이 저장되는 공간(위험지도·리포트).

- `riskmap_current.tif`, `riskmap_{RP}yr.tif` — 등급화 위험지도(COG)
- `risk_stats.{csv,geojson}` — 지역·유역별 위험 통계
- `flood_risk_report.md` — 방재 시사점 리포트

> 중간 산출물은 `_workspace/`에 보존된다(감사 추적). outputs/는 사용자 대면 최종본만 둔다.
