# data/standard_grid/pre_gridded/ — 이미 100m 격자로 제작된 자료 제공

원시자료 대신 **이미 표준격자망에 맞춰 제작된 100m 격자자료**를 여기 넣는다(예: 격자화된 침수위험지도·NDMS, 격자 인구·인자).

- **무검증 사용 금지.** `src/standardize/verify_grid.py`(→ `assert_grid_contract`)로 마스터 정합을 먼저 검증한다.
- 통과 → 재표준화 없이 그대로 사용(불필요한 리샘플로 값 훼손 방지).
- 위반(원점 밀림·CRS 상이·NoData 규약 차이) → 마스터에 재정합.

> 남이 만든 100m 격자는 원점·CRS 변형·NoData가 다를 수 있어 셀 join을 조용히 어긋나게 한다. 검증은 값싸고 오염 전파는 비싸다.
