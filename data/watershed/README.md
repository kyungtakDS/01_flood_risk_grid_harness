# data/watershed/ — 수자원단위지도(유역 경계)

전국 격자망 파티셔닝과 ML 모델링 단위의 골격이 되는 유역 경계를 넣는 공간.

**자료:** 수자원단위지도(환경부/K-water)의 대권역·중권역·표준유역 경계.
**형식:** 폴리곤 SHP / GeoPackage (유역코드 속성 포함).
**용도:**
- **대권역**(한강·낙동강·금강·영산강·섬진강) = 격자망 처리·완전유역 흐름분석 단위.
- **중권역** = ML 모델링·공간 CV 블록 단위(부하 저감).
- 격자 속성에 `daegwon`·`junggwon`·`std_watershed` 코드로 부착된다.

**담당:** geo-data-engineer(파티셔닝) + hydro-hazard-analyst(유역 기준).
**상세 규약:** `.claude/skills/geodata-grid-pipeline/references/watershed-units.md`.

> 흐름누적·하천망·HAND는 중권역 타일에서 자르면 상류가 끊긴다 → 대권역(완전유역)에서 계산 후 중권역으로 타일링한다.
