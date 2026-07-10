---
name: dashboard-builder
description: 프로젝트 폴더의 실제 파일(README·CLAUDE.md·config·.claude/agents·.claude/skills·_workspace·docs)에서 지표를 추출해 Notion+Linear 스타일·밝은 배경·Chart.js 원형(도넛) 차트로 된 자체완결 HTML 대시보드를 만드는 스킬. '대시보드 만들어줘', '현황 대시보드', '하네스 대시보드', '노션/Linear 스타일 대시보드', '원형/도넛 차트 대시보드', 'Chart.js 대시보드', '프로젝트 현황 시각화' 요청 시 이 스킬을 사용. 후속: '대시보드 갱신/업데이트/수정', '대시보드에 차트/섹션 추가', '수치 다시 계산', '대시보드 다시 만들어' 요청 시에도 반드시 이 스킬을 사용. 기존 dashboard.html은 변경하지 않고 별도 파일로 출력한다.
---

# Dashboard Builder — 하네스 운영 대시보드 제작

프로젝트 파일에서 실제 지표를 추출하여, 하네스의 구성·상태·산출물을 한 화면에 요약한 **자체완결 HTML 대시보드**를 만든다. 스타일: Notion(카드·정보 밀도·여백) + Linear(절제된 인디고 크롬·타이포·얇은 경계선), 밝은 배경, 핵심 시각화는 Chart.js 도넛(원형) 차트.

**왜 이렇게 하는가:** 대시보드의 가치는 "정확한 수치 + 한눈에 읽히는 구조"다. 숫자를 지어내면 관리 도구로서 신뢰를 잃고, 스타일이 산만하면 보기 불편하다. 그래서 (1) 모든 수치를 파일에서 추출하고, (2) 검증된 단일 디자인 시스템을 재사용한다.

## 워크플로우

```
1. 소스 수집   → 검증: 아래 근거 파일들을 읽었는가
2. 지표 추출   → 검증: 모든 숫자가 파일로 역추적되는가 (references/data-extraction.md)
3. 렌더링      → 검증: 디자인 시스템 토큰·도넛 차트 규격 준수 (references/design-system.md)
4. 자기검증    → 검증: 단일 HTML로 열림·Chart.js 로드·수치 대조·dashboard.html 무변경
```

### 1. 소스 수집
다음 파일을 읽어 근거를 확보한다. 상세 매핑은 `references/data-extraction.md` 참조.
- `README.md`, `CLAUDE.md`, `PROJECT_STRUCTURE.md`
- `config/grid_config.yaml`
- `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, `.claude/skills/*/references/*.md`, `.claude/skills/*/scripts/*`
- `_workspace/`(리허설 산출물), `docs/`(이미지)
- 기존 `dashboard.html`(스타일·지표 대조용 — **읽기만**)

### 2. 지표 추출
`references/data-extraction.md`의 소스→지표 매핑을 그대로 따른다. 핵심 규칙:
- 개수형 지표(에이전트·스킬·자산·드롭존)는 **실제 파일/디렉토리 개수**로 계산한다.
- 계약형 지표(CRS·해상도·NoData·파티션·모델·재현주기)는 `config/grid_config.yaml`에서 읽는다.
- 상태형 지표(리허설 6/6·자료 준비 현황)는 README/워크스페이스에서 읽는다.
- 근거가 없는 숫자는 만들지 않는다. 비우거나 "미확정"으로 둔다.

### 3. 렌더링
`references/design-system.md`의 토큰·컴포넌트·차트 규격으로 단일 HTML을 조립한다. 필수 구성:
- **사이드바 레일 + 메인** 2단 레이아웃(모바일에서 접힘)
- **KPI 그리드** — 핵심 수치 카드(좌측 컬러 바)
- **도넛 차트 그리드** — 각 카드에 원형 차트 + 커스텀 레전드(값 표기). 최소 4개.
- **파이프라인 플로우 / 에이전트 그리드 / 격자 계약 스펙 / 리허설 / 자료 드롭존** 섹션(데이터가 있을 때)
- 하단 **footer에 출처(근거 파일)** 명기

### 4. 자기검증
- 단일 HTML 파일로 브라우저에서 열리는가(외부 의존성은 Chart.js CDN 하나뿐)
- 각 `<canvas>`에 대응하는 Chart 인스턴스가 생성되고 레전드 값이 채워지는가
- 표시된 수치가 2단계 추출값과 일치하는가
- **기존 `dashboard.html`이 그대로인가**(diff 없음), 출력은 별도 파일인가

## 출력 규칙
- 기본 출력 경로: `dashboard_v2.html`(프로젝트 루트). 사용자가 경로를 지정하면 그 경로.
- 기존 `dashboard.html`을 덮어쓰지 않는다. 이미 대상 파일이 있으면 갱신(변경분만).

## 자세히
- 디자인 토큰·레이아웃·Chart.js 도넛 레시피·반응형 규칙: `references/design-system.md`
- 소스→지표 매핑·개수 계산법·상충 처리: `references/data-extraction.md`
