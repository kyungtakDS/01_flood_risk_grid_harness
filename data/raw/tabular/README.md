# data/raw/tabular/ — 집계표 원시자료 (행정구역 단위)

행정구역(읍면동 등) 단위로 집계된 통계표를 넣는 공간.

**예시:** 인구·세대·자산, 사회취약계층(고령·독거·저소득).
**형식:** CSV / XLSX + 행정경계 join 키(행정동 코드). 또는 행정경계 SHP에 속성으로 포함.
**변환 코드:** `src/standardize/tabular_dasymetric.py` (다이어시메트릭 분배 — 건물/불투수면 가중 하향식, 질량 보존).
**담당:** exposure-vulnerability-analyst(설계) + geo-data-engineer(분배) → exposure-vulnerability-factors 스킬.

> 균등분배 금지(논·산에 인구를 뿌림). 사람·자산이 실제 있는 곳(건물/주거지)에 가중해 배분하고, 행정단위 내 합계를 보존한다.
