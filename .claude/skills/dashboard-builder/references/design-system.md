# 디자인 시스템 — Notion + Linear · 밝은 배경 · Chart.js 도넛

이 프로젝트의 검증된 대시보드 디자인 시스템. `dashboard.html`에서 이미 사용·검증된 팔레트/레이아웃을 표준으로 재사용한다(dataviz 색 규약 준수: 채도·명도 밸런스, 밝은 배경에서 구분 가능한 범주 색). 새 대시보드는 이 토큰을 그대로 쓴다 — 일관성이 관리 편의의 핵심이다.

## 1. CSS 토큰 (`:root`)

```css
--plane:#f7f7f8;      /* 페이지 배경(밝음) */
--surface:#ffffff;    /* 카드 표면 */
--surface-2:#fcfcfb;
--ink:#0b0b0b;        /* 본문 */
--sub:#52514e;        /* 보조 텍스트 */
--muted:#8a8984;      /* 라벨/축 */
--line:rgba(11,11,11,0.08);
--line-2:rgba(11,11,11,0.06);
--accent:#5b5bd6;     /* Linear 인디고 — 크롬(강조)에만 */
--accent-soft:#eeeefb;
/* 검증된 범주 색 슬롯 (도넛/레전드) */
--s1:#2a78d6; --s2:#1baf7a; --s3:#eda100; --s4:#008300; --s5:#4a3aa7;
--s6:#e34948; --s7:#e87ba4; --s8:#eb6834;
--good:#0ca30c; --critical:#d03b3b; --warn:#fab219;
--shadow:0 1px 2px rgba(11,11,11,.04), 0 4px 16px rgba(11,11,11,.04);
--radius:14px;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,"Malgun Gothic",sans-serif;
```

**색 사용 규칙:** accent(인디고)는 로고·네비·강조 크롬에만. 데이터 계열은 `--s1..s8`을 순서대로. 상태는 good/critical/warn. 밝은 배경 고정 — 다크 분기 없음.

## 2. 레이아웃 골격

- `.app{display:grid; grid-template-columns:248px 1fr; min-height:100vh}` — 좌측 레일 + 메인
- **레일**: sticky, 브랜드 마크(그라디언트 사각), 네비(섹션 앵커), 하단 상태 도트
- **메인**: `padding:30px 34px 60px; max-width:1180px`
- 섹션: `.sec-head`(제목 + 우측 hint) + 콘텐츠

카드 공통:
```css
.card{background:var(--surface);border:1px solid var(--line);
  border-radius:var(--radius);padding:18px;box-shadow:var(--shadow)}
```

## 3. 컴포넌트

- **KPI 카드**: 좌측 3px 컬러 바(`::before`), `k-label`(대문자 소형) / `k-val`(26px 700) / `k-sub`. 6개 그리드.
- **도넛 카드**: `.chart-body{display:grid;grid-template-columns:170px 1fr;gap:14px}` — 좌 캔버스(170px 정사각) + 우 커스텀 레전드. 레전드 행 = 점 + 라벨 + 값(우측 tabular-nums).
- **파이프라인 플로우**: `repeat(7,1fr)` 스테이지 카드, 상단 3px 컬러 보더(`--st`), 번호/제목/담당(에이전트·스킬).
- **에이전트 그리드**: `repeat(4,1fr)` 카드 — 배지(이모지) + 이름(국문) + `a-en`(모노 영문 id) + 설명 + 태그(역할/opus).
- **스펙 그리드**: `repeat(4,1fr)` — s-key/s-val/s-note. 격자 계약용.
- **드롭존 테이블**: `.zrow{grid-template-columns:170px 1fr 110px}` — 경로(모노)/설명/상태 pill(대기·준비완료).

## 4. Chart.js 도넛 레시피 (핵심)

CDN: `<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>` (이 하나만 외부 의존).

중앙 텍스트 플러그인 + 도넛 헬퍼:
```js
Chart.register({ id:'centerText', afterDraw(chart){
  const o=chart.options.plugins.centerText; if(!o) return;
  const {ctx,chartArea:{left,right,top,bottom}}=chart;
  const cx=(left+right)/2, cy=(top+bottom)/2;
  ctx.save(); ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillStyle='#0b0b0b'; ctx.font='700 25px system-ui,"Segoe UI",sans-serif';
  ctx.fillText(o.line1, cx, cy-8);
  ctx.fillStyle='#52514e'; ctx.font='500 11.5px system-ui,"Segoe UI",sans-serif';
  ctx.fillText(o.line2, cx, cy+13); ctx.restore();
}});

function doughnut(id, data, colors, center){
  return new Chart(document.getElementById(id), {
    type:'doughnut',
    data:{ labels:data.map(d=>d.label), datasets:[{
      data:data.map(d=>d.value), backgroundColor:colors,
      borderColor:'#fff', borderWidth:3, borderRadius:5, spacing:2, hoverOffset:6 }]},
    options:{ cutout:'70%', responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false}, centerText:center,
        tooltip:{ backgroundColor:'#141413', padding:10, cornerRadius:8,
          callbacks:{ label:(c)=>` ${c.label}: ${c.raw}` } } },
      animation:{ animateScale:true, duration:700, easing:'easeOutQuart' } }
  });
}
```
- `cutout:'70%'`로 얇은 링(원형/도넛). 조각 사이 흰 테두리(`borderWidth:3`)로 분리.
- 중앙에 요약값(line1 큰 값 + line2 설명).
- 커스텀 레전드는 별도 `legend(id,data,colors)`로 HTML 주입(값 표기 tabular-nums).
- 캔버스는 `.canvas-wrap{position:relative;height:170px}` 안에 둔다(반응형 높이 고정).

**도넛을 언제 쓰나:** 부분/전체 비율(리허설 통과율·자료 준비율), 범주 구성(자산 구성·모델 포트폴리오·파이프라인 단계 분포). 시계열/추세는 도넛 부적합 — 이 대시보드는 구성·상태 요약이라 도넛이 적합하다.

## 5. 반응형

```css
@media (max-width:1080px){ .kpi-grid{grid-template-columns:repeat(3,1fr)}
  .flow{grid-template-columns:repeat(4,1fr)} .agent-grid,.spec-grid{grid-template-columns:repeat(2,1fr)} }
@media (max-width:860px){ .app{grid-template-columns:1fr}
  .rail{position:static;height:auto;flex-direction:row;flex-wrap:wrap}
  .chart-grid{grid-template-columns:1fr} }
@media (max-width:620px){ .kpi-grid{grid-template-columns:repeat(2,1fr)}
  .chart-body{grid-template-columns:1fr} .canvas-wrap{max-width:220px;margin:0 auto} }
```

가로 스크롤 금지 — 넓은 표/플로우는 컬럼 수를 줄여 접는다.
