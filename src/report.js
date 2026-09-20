import * as echarts from "echarts";

const base = import.meta.env.BASE_URL;
const C = { green: "#1f5e42", green2: "#5f9f7a", green3: "#a8cbb6", orange: "#c7641c", orange2: "#e8a86b", red: "#c0392b", blue: "#2f6db5", blue2: "#8fb4e0", purple: "#6f4fa3", gray: "#9aa0a6", gray2: "#d3d6da", ink: "#1d1d1f", ink2: "#515154", ink3: "#86868b" };
const FONT = getComputedStyle(document.documentElement).getPropertyValue("--font");
echarts.registerTheme("gj", {
  color: [C.green, C.orange, C.blue, C.purple, C.red, C.gray],
  textStyle: { fontFamily: FONT, color: C.ink2 },
  title: { textStyle: { color: C.ink, fontWeight: 600, fontSize: 13 } },
  legend: { textStyle: { color: C.ink2, fontSize: 12 }, itemWidth: 12, itemHeight: 8, icon: "roundRect" },
  tooltip: { backgroundColor: "rgba(255,255,255,.96)", borderColor: "rgba(0,0,0,.1)", borderWidth: 1, textStyle: { color: C.ink, fontSize: 12.5 }, padding: [8, 10], extraCssText: "box-shadow:0 6px 24px rgba(0,0,0,.08);border-radius:10px" },
  categoryAxis: { axisLine: { lineStyle: { color: "rgba(0,0,0,.12)" } }, axisTick: { show: false }, axisLabel: { color: C.ink3, fontSize: 11.5 }, splitLine: { show: false } },
  valueAxis: { axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: C.ink3, fontSize: 11.5 }, splitLine: { lineStyle: { color: "rgba(0,0,0,.06)" } } },
  line: { symbolSize: 5, smooth: false }, bar: { barMaxWidth: 34 },
});
const fmt = (v) => (v == null ? "–" : Number(v).toLocaleString("ko-KR"));
const pct = (v, d = 1) => (v == null ? "–" : Number(v).toFixed(d) + "%");
const charts = [];
const $ = (h) => { const t = document.createElement("template"); t.innerHTML = h.trim(); return t.content.firstElementChild; };
const main = document.getElementById("main"); const toc = document.getElementById("toc");

const TOC = { pop: "인구", land: "토지이용", mobility: "교통", tourism: "관광·경관", economy: "경제·주거·재정", survey15: "시민의식 2015", survey25: "시민 인식 2025", now: "지금 · 2026", hwango: "황오동 모니터링", arts: "예술인", sources: "출처" };
function section(id, eyebrow, title, read) {
  const s = $(`<section class="sec" id="${id}"><div class="eyebrow">${eyebrow}</div><h2>${title}</h2><p class="read">${read}</p></section>`);
  main.appendChild(s); toc.appendChild($(`<a href="#${id}">${TOC[id] || id}</a>`));
  return s;
}
function tiles(host, items) {
  const g = $(`<div class="tiles"></div>`);
  for (const t of items) g.appendChild($(`<div class="tile"><div class="k">${t.k}</div><div class="v">${t.v}${t.u ? `<small>${t.u}</small>` : ""}</div>${t.d ? `<div class="d ${t.cls || ""}">${t.d}</div>` : ""}</div>`));
  host.appendChild(g); return g;
}
function grid(host) { const g = $(`<div class="grid"></div>`); host.appendChild(g); return g; }
function card(host, { title, sub, size = "", h = "", src, tier, note }, opt) {
  const c = $(`<div class="card ${size}"><h3>${title}</h3>${sub ? `<p class="sub">${sub}</p>` : ""}<div class="chart ${h}"></div>${note ? `<p class="note">${note}</p>` : ""}${src ? `<p class="src">${tier ? `<span class="tier ${tier.toLowerCase()}">${tier}</span>` : ""}${src}</p>` : ""}</div>`);
  host.appendChild(c);
  if (opt) { const ch = echarts.init(c.querySelector(".chart"), "gj"); ch.setOption({ animationDuration: matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 500, ...opt }); charts.push(ch); }
  return c;
}
const hbar = (cats, vals, { color = C.green, unit = "", top = 8, max, fmtV } = {}) => ({
  grid: { left: 4, right: 44, top: 4, bottom: 4, containLabel: true },
  tooltip: { trigger: "axis", axisPointer: { type: "none" }, valueFormatter: (v) => (fmtV ? fmtV(v) : fmt(v) + unit) },
  xAxis: { type: "value", show: false, max },
  yAxis: { type: "category", inverse: true, data: cats.slice(0, top), axisLine: { show: false }, axisLabel: { color: C.ink, fontSize: 12, width: 150, overflow: "truncate" } },
  series: [{ type: "bar", data: vals.slice(0, top), itemStyle: { color, borderRadius: [0, 4, 4, 0] }, barCategoryGap: "32%", label: { show: true, position: "right", fontSize: 11.5, color: C.ink2, formatter: (d) => (fmtV ? fmtV(d.value) : fmt(d.value) + unit) } }],
});
const srcLine = (s) => s.replace(/(T[124])\)/, "$1)");

async function main_() {
  const R = await fetch(`${base}data/report_stats.json`, { cache: "no-cache" }).then((r) => r.json());
  const HW = await fetch(`${base}data/hwango_report.json`, { cache: "no-cache" }).then((r) => r.json()).catch(() => null);
  const AR = await fetch(`${base}data/arts_stats.json`, { cache: "no-cache" }).then((r) => r.json()).catch(() => null);
  const X = R.extras;
  // ---------- 히어로 타일
  const p26 = R.pop_actual.pop_2026_08; const gap = (p26 / 320000 - 1) * 100;
  tiles(document.getElementById("hero-tiles"), [
    { k: "2030 계획인구 (T1)", v: fmt(320000), u: "명", d: "자연증가 262,490 + 사회적증가 53,769" },
    { k: "실제 주민등록 2026.08 (T2)", v: fmt(p26), u: "명", d: `계획 대비 ${gap.toFixed(0)}%`, cls: "down" },
    { k: "65세 이상", v: pct(R.aging.pct65_2026), d: `2013년 ${pct(R.aging.pct65.at(-1))} → 계획의 2030 전망 ${pct(R.age_projection.p65.at(-1))}을 이미 근접`, cls: "down" },
    { k: "폐역 구역 유동인구", v: fmt(X.footfall.D_zone.per_ha), u: "/ha", d: `성동시장 200m ${fmt(X.footfall.G_seongdong_market_r200.per_ha)}/ha의 1/15` },
  ]);

  // ---------- 1. 인구
  let s = section("pop", "인구 · 2030 기본계획 vs 주민등록", "계획된 성장과 실제 감소 — 한 그래프에", "기본계획은 2013년 270,493명에서 2030년 320,000명으로 <b>+18%</b>를 그렸다. 주민등록 인구는 같은 기간 계속 줄어 2026년 8월 242,512명이다. 두 통계는 기준(통계연보 vs 주민등록·외국인 포함 여부)이 달라 2011~13년에 약 1만 명 차이가 나므로 <b>수준이 아니라 방향</b>을 읽는다.");
  let g = grid(s);
  const yrsAll = [...new Set([...R.pop_doc.years, ...R.pop_actual.years, ...R.pop_plan.years, "2026"])].sort();
  const ser = (yrs, vals) => yrsAll.map((y) => { const i = yrs.indexOf(y); return i < 0 ? null : vals[i]; });
  card(g, { title: "경주시 인구 — 통계연보(2003–13) · 주민등록(2011–25) · 계획인구(2013→2030)", sub: "명. 계획인구는 2015·2020·2025·2030 단계 목표", size: "", h: "tall", tier: "T1", src: `${R.pop_doc.src} / ${R.pop_actual.src}` }, {
    grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" },
    xAxis: { type: "category", data: yrsAll, axisLabel: { interval: 2 } }, yAxis: { type: "value", min: 230000, max: 330000, axisLabel: { formatter: (v) => v / 1000 + "k" } },
    series: [
      { name: "통계연보 (기본계획 수록)", type: "line", data: ser(R.pop_doc.years, R.pop_doc.total), color: C.gray, lineStyle: { width: 2 }, connectNulls: true },
      { name: "주민등록 KOSIS", type: "line", data: ser(R.pop_actual.years, R.pop_actual.total), color: C.ink, lineStyle: { width: 2.5 }, connectNulls: true, endLabel: { show: true, formatter: (d) => fmt(d.value), fontSize: 11, color: C.ink } },
      { name: "2030 계획인구", type: "line", data: ser(R.pop_plan.years, R.pop_plan.total), color: C.green, lineStyle: { width: 2, type: "dashed" }, symbolSize: 7, connectNulls: true, endLabel: { show: true, formatter: (d) => fmt(d.value), fontSize: 11, color: C.green } },
      { name: "2026.08", type: "scatter", data: [[String(2026), p26]], color: C.red, symbolSize: 10, label: { show: true, position: "right", formatter: fmt(p26), fontSize: 11, color: C.red } },
    ],
  });
  card(g, { title: "고령화 — 65세 이상 비율", sub: "2004–2013 통계연보 · 2026.08 주민등록 · 계획의 자연증가 전망(2015–2030)", size: "half", tier: "T1", src: `${R.aging.src} / ${R.age_projection.src}` }, {
    grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
    xAxis: { type: "category", data: [...R.aging.years, "2015", "2020", "2025", "2026", "2030"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" }, max: 40 },
    series: [{ name: "실적", type: "line", data: [...R.aging.pct65, null, null, null, R.aging.pct65_2026, null], color: C.ink, lineStyle: { width: 2.5 }, connectNulls: true },
             { name: "계획 전망", type: "line", data: [...Array(9).fill(null), R.age_projection.p65[0], ...R.age_projection.p65.slice(1, 4), null, R.age_projection.p65[4]], color: C.green, lineStyle: { type: "dashed" }, connectNulls: true },
             { name: "2026.08 실제", type: "scatter", data: [["2026", R.aging.pct65_2026]], color: C.red, symbolSize: 10, label: { show: true, position: "top", formatter: pct(R.aging.pct65_2026), color: C.red, fontSize: 11 } }],
  });
  card(g, { title: "연령구조 전망(자연증가 기준) — 부양률 42% → 83%", sub: "0–14 / 15–64 / 65+ 구성비(%)와 부양률 [(0–14 + 65+)/15–64]", size: "half", tier: "T1", src: R.age_projection.src }, {
    grid: { left: 8, right: 40, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: R.age_projection.years }, yAxis: [{ type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } }, { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" }, splitLine: { show: false } }],
    series: [{ name: "0–14", type: "bar", stack: "a", data: R.age_projection.p0_14, color: C.blue2 }, { name: "15–64", type: "bar", stack: "a", data: R.age_projection.p15_64, color: C.green3 }, { name: "65+", type: "bar", stack: "a", data: R.age_projection.p65, color: C.orange },
             { name: "부양률", type: "line", yAxisIndex: 1, data: R.age_projection.dependency, color: C.ink, lineStyle: { width: 2 }, label: { show: true, position: "top", formatter: (d) => d.value + "%", fontSize: 11 } }],
  });
  const lz = Object.keys(R.pop_plan.by_lifezone);
  card(g, { title: "생활권별 인구배분계획 — 중심생활권 178,973 → 200,000", sub: "2013 현재 vs 2030 목표(명). 중심생활권 순밀도 116인/ha(시가화용지 기준)", size: "half", tier: "T1", src: `${R.pop_plan.src} / ${R.lifezone_density.src}` }, {
    grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" },
    xAxis: { type: "category", data: lz }, yAxis: { type: "value", axisLabel: { formatter: (v) => v / 1000 + "k" } },
    series: [{ name: "2013", type: "bar", data: lz.map((z) => R.pop_plan.by_lifezone[z][0]), color: C.gray2 }, { name: "2030 계획", type: "bar", data: lz.map((z) => R.pop_plan.by_lifezone[z][4]), color: C.green, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => (d.value / 1000).toFixed(0) + "k" } }],
  });
  const sc = R.pop_plan_components.social;
  card(g, { title: "계획인구 320,000의 구성 — 사회적증가 53,769명은 어디서 오나", sub: "자연증가 262,490(내국인 252,490 + 외국인 10,000) + 사회적증가(신규사업)", size: "half", tier: "T1", src: R.pop_plan_components.src },
    hbar(["자연증가(내국인)", "일반산업단지", "도시개발사업", "주택건설사업", "신경주역세권", "자연증가(외국인)"], [252490, sc["일반산업단지"], sc["도시개발사업"], sc["주택건설사업"], sc["신경주역세권"], 10000], { unit: "명", color: C.green2 }));

  // ---------- 2. 토지
  s = section("land", "토지이용 · 용도지역", "1,325㎢ 중 시가지는 5%, 상업지역은 0.22%", "경주시 전체의 <b>42%가 농림지역, 31%가 녹지지역</b>이고 주거·상업·공업을 합친 시가지는 46.96㎢(3.5%)다. 2030 계획은 시가화용지를 44.67→67.36㎢로 늘리는데 그 절반 이상(+11.73㎢)이 <b>공업용지</b>다. 상업용지 증가 0.28㎢는 전부 중심생활권.");
  g = grid(s);
  card(g, { title: "용도지역 구성 (2014 통계연보)", sub: "면적 ㎢ · 비율 %", size: "half", tier: "T1", src: R.landuse.src }, {
    tooltip: { trigger: "item", formatter: (d) => `${d.name} ${fmt(d.value)}㎢ · ${d.percent}%` },
    series: [{ type: "pie", radius: ["48%", "78%"], center: ["50%", "50%"], data: R.landuse.items.map((i) => ({ name: i.name, value: i.km2 })), color: [C.orange, C.red, C.purple, C.green3, C.gray2, C.blue2, C.blue, C.gray, C.green, C.green2],
               label: { fontSize: 11.5, color: C.ink2, formatter: (d) => (d.percent >= 2 ? `${d.name} ${d.percent}%` : "") }, labelLine: { length: 8, length2: 6 }, itemStyle: { borderColor: "#fff", borderWidth: 2 } }],
  });
  const lpr = R.landuse_plan.rows.filter((r) => !/계|미지정|보전용지/.test(r.name));
  card(g, { title: "2030 토지이용계획 — 기정 → 변경 (㎢)", sub: "시가화용지·시가화예정용지 내역. 공업 +11.73, 관리용지 +9.45, 지구단위계획 +7.92", size: "half", tier: "T1", src: R.landuse_plan.src }, {
    grid: { left: 4, right: 40, top: 30, bottom: 4, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "㎢" },
    xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: lpr.map((r) => r.name), axisLabel: { color: C.ink, fontSize: 12 } },
    series: [{ name: "기정", type: "bar", data: lpr.map((r) => r.before), color: C.gray2, barGap: "-55%", barCategoryGap: "35%" }, { name: "변경", type: "bar", data: lpr.map((r) => r.after), color: C.green, label: { show: true, position: "right", fontSize: 11, color: C.ink2, formatter: (d) => d.value } }],
  });

  // ---------- 3. 교통
  s = section("mobility", "교통 · 수단분담 · 자동차", "2007년 통행의 36%가 버스였다. 계획은 2015년부터 승용차 40%를 전제한다", "기본계획이 인용한 2007년 조사에서 버스 36.2%·승용차 26.5%·도보 15.1%였던 분담률이, 같은 계획의 2015~2030 예측표에서는 <b>승용차 40%·버스 15.6%</b>로 뒤집힌다. 천 명당 차량은 2009 403대 → 2013 449대(+2.8%/년). 주차 51,880면의 <b>99%가 부설주차장</b>이고, 시내버스 수송은 5년간 1,500만 명 수준에서 정체.");
  g = grid(s);
  const modes2007 = R.mode_share_2007.modes; const f = R.mode_forecast;
  card(g, { title: "수단분담률 — 2007 조사 vs 2015·2030 계획 예측", sub: "% · 예측표는 도보와 자전거를 합산", size: "half", tier: "T1", src: `${R.mode_share_2007.src} / ${f.src}` }, {
    grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
    xAxis: { type: "category", data: ["도보(·자전거)", "승용차", "택시", "버스", "철도", "기타"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" }, max: 45 },
    series: [{ name: "2007 조사", type: "bar", data: R.mode_share_2007.pct, color: C.gray }, { name: "2015 예측", type: "bar", data: ["도보/자전거", "승용차", "택시", "버스", "철도", "기타"].map((m) => f.pct[m][0]), color: C.green2 }, { name: "2030 예측", type: "bar", data: ["도보/자전거", "승용차", "택시", "버스", "철도", "기타"].map((m) => f.pct[m][3]), color: C.green, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => d.value } }],
  });
  card(g, { title: "목적별 수단분담 (2007) — 등교의 52%는 버스, 업무의 50%는 승용차", sub: "%", size: "half", tier: "T1", src: R.mode_share_2007.src }, {
    grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
    xAxis: { type: "category", data: Object.keys(R.mode_share_2007.by_purpose) }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } },
    series: modes2007.map((m, i) => ({ name: m, type: "bar", stack: "s", data: Object.values(R.mode_share_2007.by_purpose).map((v) => v[i]), color: [C.green3, C.orange, C.orange2, C.green, C.purple, C.gray2][i] })),
  });
  card(g, { title: "인구 천 명당 차량 등록", sub: "대/천 명 · 2009–2013", size: "third", tier: "T1", src: R.cars.src }, {
    grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: R.cars.years }, yAxis: { type: "value", min: 250, max: 470 },
    series: [{ name: "전체", type: "line", data: R.cars.per_1000_total, color: C.ink, lineStyle: { width: 2.5 }, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => d.value.toFixed(0) } }, { name: "승용차", type: "line", data: R.cars.per_1000_car, color: C.orange }],
  });
  card(g, { title: "철도 승차 — 신경주역(KTX) vs 경주역(일반)", sub: "명/년 · 경주역은 2021.12 폐역", size: "third", tier: "T1", src: R.rail.src }, {
    grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" },
    xAxis: { type: "category", data: R.rail.years }, yAxis: { type: "value", axisLabel: { formatter: (v) => v / 1e6 + "M" } },
    series: [{ name: "신경주역", type: "bar", data: R.rail.ktx_board, color: C.green }, { name: "구 경주역", type: "bar", data: R.rail.gj_board, color: C.orange }],
  });
  card(g, { title: "주차시설 51,880면 — 부설 99%", sub: "면수 · 개소", size: "third", tier: "T1", src: R.parking.src },
    hbar(R.parking.rows.filter((r) => r.kind !== "합계").map((r) => `${r.kind} (${fmt(r.sites)}개소)`), R.parking.rows.filter((r) => r.kind !== "합계").map((r) => r.spaces), { unit: "면", color: C.gray }));
  card(g, { title: "시내버스 수송인원 — 5년간 정체", sub: "명/년 · 등록대수 163→169", size: "half", tier: "T1", src: R.bus.src }, {
    grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" },
    xAxis: { type: "category", data: R.bus.years }, yAxis: { type: "value", min: 0, axisLabel: { formatter: (v) => v / 1e6 + "M" } },
    series: [{ name: "시내버스", type: "line", data: R.bus.city_pax, color: C.green, areaStyle: { opacity: .12 }, lineStyle: { width: 2.5 } }, { name: "전세버스", type: "line", data: R.bus.charter_pax, color: C.orange }],
  });
  const vcs = R.road_vc.rows.filter((r) => /국도7|국도4|국도35|국도20|지방도/.test(r.road) || r.vc >= 0.6).sort((a, b) => b.vc - a.vc).slice(0, 10);
  card(g, { title: "주요 도로 V/C — 용량 대비 교통량 상위", sub: "V/C (1.0 = 용량 도달) · 국도 위주 상위 10구간", size: "half", tier: "T1", src: R.road_vc.src },
    hbar(vcs.map((r) => `${r.road} ${r.seg}`), vcs.map((r) => r.vc), { color: C.orange, top: 10, max: 1, fmtV: (v) => v.toFixed(2) }));

  // ---------- 4. 관광·경관
  s = section("tourism", "관광 · 경관 인식", "지정관광지 방문객 889만(2013). 시민이 꼽는 대표 경관은 불국사가 아니라 황리단길", "기본계획의 관광객 통계는 보문·양남·감포 <b>지정관광지 입장객</b>만 센다(2013년 889만, 외국인 19만). 관광데이터랩의 2026년 8월 순방문자(18일간 626만)는 정의가 달라 합칠 수 없다. 2030 경관계획 의식조사에서 시민 36.4%가 대표 경관으로 <b>황리단길</b>을 꼽았고(불국사 24.2%), 관광객은 여전히 불국사 53.3%. 2025년 417쪽 연구에서도 상징적 중심 1위는 황리단길(59명 중 25).");
  g = grid(s);
  card(g, { title: "지정(법정) 관광지 방문객", sub: "명/년 · 내국인 + 외국인 · 보문·양남·감포만", size: "half", tier: "T1", src: R.tourists.src, note: `참고: 관광데이터랩 2026.08.01~18 순방문자 현지인 ${fmt(R.visitors_2026.sum_local)} · 외지인 ${fmt(R.visitors_2026.sum_ext)} · 외국인 ${fmt(R.visitors_2026.sum_foreign)} (KT, 시군구, T2) — 정의가 다르므로 위 그래프와 비교 금지` }, {
    grid: { left: 8, right: 40, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" },
    xAxis: { type: "category", data: R.tourists.years }, yAxis: [{ type: "value", axisLabel: { formatter: (v) => v / 1e6 + "M" } }, { type: "value", axisLabel: { formatter: (v) => v / 1e3 + "k" }, splitLine: { show: false } }],
    series: [{ name: "합계", type: "bar", data: R.tourists.total, color: C.green }, { name: "외국인(우축)", type: "line", yAxisIndex: 1, data: R.tourists.foreign, color: C.orange, lineStyle: { width: 2 } }],
  });
  const ls = R.landscape_survey;
  card(g, { title: "경주의 대표 경관은? — 시민·공무원·관광객", sub: "% · 2030 경관계획 재정비 경관의식조사 (시민 330·관광객 60·공무원 168)", size: "half", tier: "T1", src: ls.src }, {
    grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
    xAxis: { type: "category", data: ["시민", "공무원", "관광객"] }, yAxis: { type: "value", max: 60, axisLabel: { formatter: (v) => v + "%" } },
    series: [{ name: "황리단길", type: "bar", data: ["시민", "공무원", "관광객"].map((k) => ls.representative["황리단길"][k]), color: C.orange, label: { show: true, position: "top", fontSize: 11, formatter: (d) => d.value } }, { name: "불국사", type: "bar", data: ["시민", "공무원", "관광객"].map((k) => ls.representative["불국사"][k]), color: C.green, label: { show: true, position: "top", fontSize: 11, formatter: (d) => d.value } }],
  });
  const pp = ls.priority_projects;
  card(g, { title: "우선 경관사업 — 시민 vs 공무원 (복수응답)", sub: "%", size: "half", tier: "T1", src: ls.src, note: `가장 개선이 필요한 경관: 옥외광고물(시민 ${ls.worst_ad["시민"]}% · 공무원 ${ls.worst_ad["공무원"]}%), 장소로는 황리단길(시민 ${ls.worst_hwangridan["시민"]}%). 정체성은 "신라왕경을 품은 역사도시" 시민 ${ls.identity_silla["시민"]}%.` }, {
    grid: { left: 4, right: 40, top: 30, bottom: 4, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
    xAxis: { type: "value", show: false, max: 70 }, yAxis: { type: "category", inverse: true, data: Object.keys(pp), axisLabel: { color: C.ink, fontSize: 12, width: 190, overflow: "break" } },
    series: [{ name: "시민", type: "bar", data: Object.values(pp).map((v) => v["시민"]), color: C.green, barCategoryGap: "35%" }, { name: "공무원", type: "bar", data: Object.values(pp).map((v) => v["공무원"]), color: C.gray, label: { show: true, position: "right", fontSize: 11, color: C.ink2 } }],
  });
  const s25 = R.survey_2025;
  card(g, { title: "2025 시민이 그린 경주의 중심 (417쪽 연구, n=59)", sub: "상징적 중심부 3곳 응답 수 — 황리단길 25 · 첨성대 16 · 보문 12 · 불국사 12", size: "half", tier: "T2", src: s25.meta, note: `교류 중심: ${Object.entries(s25.social_center).map(([k, v]) => `${k} ${v}`).join(" · ")} / 쇼핑 중심: ${Object.entries(s25.shopping_center).map(([k, v]) => `${k} ${v}`).join(" · ")} / 친한 도시: ${Object.entries(s25.friendly_cities).map(([k, v]) => `${k} ${v}`).join(" · ")}` },
    hbar(Object.keys(s25.symbolic_center), Object.values(s25.symbolic_center), { unit: "명", color: C.orange }));

  // ---------- 5. 경제·주거·재정
  s = section("economy", "경제 · 주거 · 재정", "사업체의 84%가 3차산업이지만 종사자의 42%는 2차산업", "2009→2013 사업체 19,454→21,841(+12%), 종사자 94,917→110,882(+17%). 종사자 기준 2차산업 41.8%는 경북 평균(38.0%)보다 높다 — 경주는 관광도시이면서 <b>제조업 고용 도시</b>다. 전력의 48%가 산업용. 주택보급률은 2013년 114.8%, 단독주택 60%. 일반회계 세입은 2006 6,571억 → 2013 1조 309억 → 2025 예산 2조 2,500억.");
  g = grid(s);
  card(g, { title: "사업체·종사자 추이", sub: "개 · 명", size: "third", tier: "T1", src: R.business.src }, {
    grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) },
    xAxis: { type: "category", data: R.business.years }, yAxis: [{ type: "value", min: 18000, axisLabel: { formatter: (v) => v / 1000 + "k" } }, { type: "value", min: 90000, axisLabel: { formatter: (v) => v / 1000 + "k" }, splitLine: { show: false } }],
    series: [{ name: "사업체", type: "bar", data: R.business.firms, color: C.green3 }, { name: "종사자(우축)", type: "line", yAxisIndex: 1, data: R.business.workers, color: C.ink, lineStyle: { width: 2.5 } }],
  });
  const ind = R.industry_2013;
  card(g, { title: "산업구조 2013 — 사업체 vs 종사자 vs 경북 종사자", sub: "%", size: "third", tier: "T1", src: ind.src }, {
    grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
    xAxis: { type: "category", data: ["경주 사업체", "경주 종사자", "경북 종사자"] }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } },
    series: ["1차", "2차", "3차"].map((k, i) => ({ name: k + "산업", type: "bar", stack: "s", data: [ind.firms_pct[k], ind.workers_pct[k], ind.gb_workers_pct[k]], color: [C.green3, C.orange, C.blue2][i], label: { show: i > 0, position: "inside", fontSize: 10.5, color: "#fff", formatter: (d) => d.value.toFixed(0) } })),
  });
  card(g, { title: "용도별 전력사용 — 산업용 48%", sub: "MWh · 2013", size: "third", tier: "T1", src: R.electricity.src }, {
    tooltip: { trigger: "item", formatter: (d) => `${d.name} ${fmt(d.value)} MWh · ${d.percent}%` },
    series: [{ type: "pie", radius: ["50%", "78%"], data: [{ name: "산업용", value: R.electricity.industry.at(-1) }, { name: "서비스업", value: R.electricity.service.at(-1) }, { name: "가정용", value: R.electricity.home.at(-1) }, { name: "공공용", value: R.electricity.total.at(-1) - R.electricity.industry.at(-1) - R.electricity.service.at(-1) - R.electricity.home.at(-1) }], color: [C.orange, C.green, C.blue, C.gray2], label: { fontSize: 11.5, color: C.ink2, formatter: "{b} {d}%" }, itemStyle: { borderColor: "#fff", borderWidth: 2 } }],
  });
  card(g, { title: "주택보급률과 주택 유형", sub: "% · 2013 유형 구성: 단독 60.3 · 아파트 33.0 · 다세대 4.8 · 연립 1.8", size: "half", tier: "T1", src: R.housing.src }, {
    grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: R.housing.years }, yAxis: [{ type: "value", min: 90000, axisLabel: { formatter: (v) => v / 1000 + "k" } }, { type: "value", min: 100, max: 120, axisLabel: { formatter: (v) => v + "%" }, splitLine: { show: false } }],
    series: [{ name: "가구", type: "bar", data: R.housing.households, color: C.gray2 }, { name: "주택", type: "bar", data: R.housing.units, color: C.green3 }, { name: "보급률(우축)", type: "line", yAxisIndex: 1, data: R.housing.supply_rate, color: C.ink, lineStyle: { width: 2.5 }, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => d.value + "%" } }],
  });
  card(g, { title: "일반회계 세입 결산 → 2025 예산", sub: "억원 · 2006–2013 결산(기본계획) · 2025 예산(417쪽 연구 인용)", size: "half", tier: "T1", src: R.finance.src }, {
    grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "억" },
    xAxis: { type: "category", data: [...R.finance.years, "2025(예산)"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => (v / 10000).toFixed(1) + "조" } },
    series: [{ type: "bar", data: [...R.finance.general_revenue.map((v) => Math.round(v / 100)), { value: R.finance.budget_2025_100M, itemStyle: { color: C.orange } }], color: C.green, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => (d.value / 10000).toFixed(2) + "조" } }],
  });

  // ---------- 6. 시민의식 2015
  s = section("survey15", "시민의식 · 2015 (기본계획 설문, n=1,408)", "시민이 꼽은 문제 1위는 편익시설 부족, 교통 1위는 주차, 경주역 부지는 복합위락 44.5%", `${R.survey_2015.meta}. 문항별 1순위만이 아니라 분포 전체를 둔다 — 2위와의 격차가 논거의 세기다. "무응답·기타"는 제외.`);
  const sm = $(`<div class="sm"></div>`); s.appendChild(sm);
  for (const q of R.survey_2015.questions) card(sm, { title: q.q, sub: `인쇄쪽 ${q.page}`, size: "" }, hbar(q.items.map((i) => i.a), q.items.map((i) => i.v), { unit: "%", top: 6, color: q.q.includes("경주역") ? C.orange : C.green }));

  // ---------- 7. 2025 설문
  s = section("survey25", "시민 인식 · 2025 (원도심 미래구상 연구 설문, n=63)", "대중교통 2.7점, 원하는 것은 자율주행 무료버스와 걷는 길", `${R.survey_2025.meta}. 표본이 작아(63명) 비율이 아니라 <b>응답 수</b>로 둔다. 2023년 폐철도 기본구상 설문(3,151명)의 '시청 이전 63.7%·도시숲 65.3%'는 언론 경유(T4)라 원문 확보 전까지 참고만.`);
  const sm2 = $(`<div class="sm"></div>`); s.appendChild(sm2);
  for (const [k, t] of [["transit_alt", "대중교통 대안 선호 (명)"], ["future_image", "경주의 미래상 (명)"], ["needed_facility", "원도심에 필요한 시설 (명)"], ["friendly_cities", "경주와 친한 도시 (명, n=56)"]])
    card(sm2, { title: t, size: "" }, hbar(Object.keys(s25[k]), Object.values(s25[k]), { unit: "", top: 9, color: C.purple }));

  // ---------- 8. 지금 (2026)
  s = section("now", "지금 · 2026 (소상공인365 · 모니터링 전사)", "폐역 구역 79/ha, 성동시장 200m 1,175/ha — 낙차 15배가 200m 안에 있다", "통신사 추정 유동인구를 <b>같은 정의</b>로 8구역에서 재추출했다(2025.06~2026.06 일평균). 행복황촌은 폐선 부지만큼 비어 있고(80/ha), 시청 500m는 저녁 18–23시 비율 27%로 유일하게 저녁이 긴 생활권이다. 황오동 원도심의 유동은 2020→2026 −14%. 지도에서 구역을 클릭하면 시간대 프로필을 볼 수 있다.");
  g = grid(s);
  const FF = ["A_hwango_grid32", "B_haengbok_hwangchon_digitized", "C_zone_buffer300", "D_zone", "E_center_r300", "F_cityhall_r500", "G_seongdong_market_r200", "H_hwangridan_r300"];
  const AC = { A_hwango_grid32: C.green, B_haengbok_hwangchon_digitized: C.gray, C_zone_buffer300: C.green2, D_zone: C.red, E_center_r300: C.green3, F_cityhall_r500: "#0f3d34", G_seongdong_market_r200: C.orange, H_hwangridan_r300: C.purple };
  card(g, { title: "유동인구 8구역 — ha당 일평균", sub: "13개월 평균 ÷ 면적 · 클릭·상세는 지도", size: "half", tier: "T2", src: X.sources.footfall },
    hbar(FF.map((k) => X.footfall[k].short), FF.map((k) => X.footfall[k].per_ha), { unit: "/ha", top: 8, color: C.green }));
  card(g, { title: "시간대 프로필 — 시청 500m만 저녁이 길다", sub: "6개 시간대 비율 %", size: "half", tier: "T2", src: X.sources.footfall }, {
    grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
    xAxis: { type: "category", data: ["05–09", "09–12", "12–14", "14–18", "18–23", "23–05"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" } },
    series: ["A_hwango_grid32", "D_zone", "F_cityhall_r500", "G_seongdong_market_r200", "H_hwangridan_r300"].map((k) => ({ name: X.footfall[k].short, type: "line", data: X.footfall[k].hourly_pct, color: AC[k], lineStyle: { width: k === "F_cityhall_r500" ? 3 : 1.8 } })),
  });
  card(g, { title: "업종 지문 — 생활 vs 관광·체류 업소수 (11개 업종)", sub: "2026.06 · 13개월 변화는 툴팁", size: "half", tier: "T2", src: X.sources.biz }, {
    grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", formatter: (ps) => { const b = X.biz_area[FF[ps[0].dataIndex]]; return `${X.footfall[FF[ps[0].dataIndex]].name}<br>생활 ${b.life_stores_2606} (${b.life_chg_13mo >= 0 ? "+" : ""}${b.life_chg_13mo}) · 관광·체류 ${b.tour_stores_2606} (${b.tour_chg_13mo >= 0 ? "+" : ""}${b.tour_chg_13mo})`; } },
    xAxis: { type: "category", data: FF.map((k) => X.footfall[k].short), axisLabel: { fontSize: 10.5 } }, yAxis: { type: "value" },
    series: [{ name: "생활", type: "bar", stack: "s", data: FF.map((k) => +X.biz_area[k].life_stores_2606), color: C.green }, { name: "관광·체류", type: "bar", stack: "s", data: FF.map((k) => +X.biz_area[k].tour_stores_2606), color: C.orange }],
  });
  const yrs7 = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]; const kp = X.hwango_kpi["주요 상권 유동인구(명, 소상공인365 통신사 추정)"] || {}; const o = X.startup_closure["황오동 사업대상지|창업 건수"] || {}; const c_ = X.startup_closure["황오동 사업대상지|폐업 건수"] || {};
  card(g, { title: "황오동 원도심 2018–2024 — 유동인구 −15%, 창업·폐업은 회전 가속", sub: "건 · 명/일", size: "half", tier: "T2", src: X.sources.hwango }, {
    grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: yrs7 }, yAxis: [{ type: "value" }, { type: "value", scale: true, axisLabel: { formatter: (v) => v / 1000 + "k" }, splitLine: { show: false } }],
    series: [{ name: "창업", type: "bar", data: yrs7.map((y) => o[y]), color: C.green2 }, { name: "폐업", type: "bar", data: yrs7.map((y) => c_[y]), color: C.red }, { name: "유동인구(우축)", type: "line", yAxisIndex: 1, data: yrs7.map((y) => kp[y] ?? null), color: C.ink, lineStyle: { width: 2.5 }, connectNulls: true }],
  });
  const ly = Object.keys(X.landprice_avg);
  card(g, { title: "공시지가 — 원도심 29필지 평균, 2022 피크 후 하락", sub: "원/㎡ · 매년 1.1 · 행복황촌 44개소는 우축", size: "half", tier: "T2", src: X.sources.hwango }, {
    grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => (v == null ? "–" : fmt(v) + "원") },
    xAxis: { type: "category", data: ly }, yAxis: [{ type: "value", scale: true, axisLabel: { formatter: (v) => (v / 1e6).toFixed(1) + "M" } }, { type: "value", scale: true, axisLabel: { formatter: (v) => (v / 1e4).toFixed(0) + "만" }, splitLine: { show: false } }],
    series: [{ name: "원도심 29필지", type: "line", data: ly.map((y) => X.landprice_avg[y]), color: C.green, lineStyle: { width: 2.5 } }, { name: "행복황촌 44개소(우축)", type: "line", yAxisIndex: 1, data: ly.map((y) => X.landprice_hwangchon44[y] ?? null), color: C.purple, lineStyle: { type: "dashed" } }],
  });
  const H = Object.fromEntries(X.heritage.map((h) => [h.k, h]));
  const tl = tiles(s, [
    { k: "매장유산 시굴 필요", v: fmt(H["시굴조사 필요 면적"].v), u: "㎡", d: "지표조사 148,770㎡ 중 · 기조사 3,396㎡ 제외" },
    { k: "시굴 비용·기간 (추정)", v: "3.06", u: "억", d: "현장 54일 · 정밀발굴 63~80억 · 630~700일" },
    { k: "발굴 유예 조건", v: "2m", u: "미만 성토", d: "성토 후 공원·주차장 → 발굴 유예 (규정)" },
    { k: "문화재 지정 건수 (2014)", v: fmt(R.heritage_count.total.at(-1)), u: "건", d: `국가지정 ${fmt(R.heritage_count.national.at(-1))} · 2004년 ${fmt(R.heritage_count.total[0])}건에서 증가` },
    { k: "도시공원 (2015)", v: fmt(R.parks.total_count), u: "개소", d: `${(R.parks.total_k_m2 / 1000).toFixed(2)}㎢ · 1인당 ${(R.parks.total_k_m2 * 1000 / p26).toFixed(1)}㎡` },
  ]);
  tl.style.marginTop = "14px";
  s.appendChild($(`<p class="src" style="margin-top:8px"><span class="tier t2">T2</span>${X.sources.heritage} · <span class="tier t1">T1</span>${R.heritage_count.src} · ${R.parks.src}</p>`));


  // ---------- 8b. 황오동 모니터링 보고서 (2025.09)
  if (HW) {
    const B = HW.biz2024, P = HW.pop_hwango, SR = HW.survey_res, SV = HW.survey_vis, K = HW.kpi, T = HW.tenure, SS = HW.sales;
    s = section("hwango", "황오동 도시재생뉴딜 성과 모니터링 (공공도시, 2025.09 · 수정중)", "‘창업 +45.8%’의 27건은 폐역 부지 축제 임시영업이었다", "2018 선정·2019–2025 시행, 215,000㎡. 보고서의 결론은 ‘인지도·소속감 상승, 창업·고용 증가, 유동인구 감소는 폐역 탓’이다. 원자료(인쇄쪽 77–86)를 다시 읽으면 세 가지가 다르게 보인다. ① 창업 70건 중 <b>27건이 구 경주역 부지(성동동 40)·성동시장 상인회에서 2~23일 만에 폐업한 임시영업</b>이고 같은 27건이 폐업 66건에도 들어 있다 — 빼면 창업 43·폐업 39, 2018(48건)보다 적다. ② 격자 32셀에서 <b>종사자 −23%</b>가 인구 −14%보다 크고, 성동시장 셀은 사업체 264→160. ③ 거점공간 만족도는 준공 후 <b>9.6→6.7→4.4</b>로 매년 떨어졌다. 황오동 20–39세는 7년 새 −44%.");
    tiles(s, [
      { k: "황오동 주민등록 2018→2025.07", v: fmt(P.total.at(-1)), u: "명", d: `${fmt(P.total[0])} → −${(100 - P.total.at(-1) / P.total[0] * 100).toFixed(0)}% · 20–39세 −${(100 - P.n_20_39.at(-1) / P.n_20_39[0] * 100).toFixed(0)}%`, cls: "down" },
      { k: "65세 이상 비율 (황오동)", v: pct(P.share_65.at(-1)), d: `2018 ${pct(P.share_65[0])} → 75세+ ${fmt(P.n_75.at(-1))}명`, cls: "down" },
      { k: "2024 창업 — 보고서 / 실질", v: `${B.open.n} / ${B.open.real}`, u: "건", d: `임시영업 ${B.open.popup}건 제외 · 점포형 ${B.open_real_storefront.length}건 · 2018년 48건`, cls: "down" },
      { k: "2024 폐업 — 보고서 / 실질", v: `${B.close.n} / ${B.close.real}`, u: "건", d: `업력 30년+ ${B.closure_age_bins["30년+"]}곳 · 10년+ ${B.closure_age_bins["30년+"] + B.closure_age_bins["10–30년"]}곳` },
      { k: "격자 32셀 종사자 2018→2023", v: fmt(K ? HW.series.site.emp.at(-1) : 0), u: "명", d: `${fmt(HW.series.site.emp[0])} → −${(100 - HW.series.site.emp.at(-1) / HW.series.site.emp[0] * 100).toFixed(0)}% · 인구 −14% · 사업체 −3%`, cls: "down" },
      { k: "거점공간 만족도 (청년창업센터·도서관)", v: "4.4", u: "/10", d: "2022 9.6 → 2023 6.7 → 2024 4.4 · 준공 3년", cls: "down" },
    ]);
    g = grid(s); g.style.marginTop = "14px";
    // 1. 창업·폐업 실질
    const grp = ["숙박·체류", "카페·휴게음식", "음식점·제과", "생활소매·식품제조", "생활서비스·의료", "유흥·오락", "통신판매(무점포)"];
    card(g, { title: "2024 창업·폐업 — 임시영업 27건을 걷어낸 업종군별 실질", sub: "위 창업 · 아래 폐업 (건)", size: "half", tier: "T2", src: B.src + " · 임시영업 = 2024 인허가 후 30일 내 폐업 + 성동동 40·396-4·43-5", note: `구 경주역 부지 ${B.open.popup_by_site["구 경주역 부지(성동동 40)"]}건은 5·6·9·11월 축제 기간(${Object.keys(B.popup_windows).slice(0, 3).join(", ")} …). 실질 순증은 숙박·체류만 +${(B.open.by_group["숙박·체류"] || 0) - (B.close.by_group["숙박·체류"] || 0)}; 생활소매·식품제조 ${(B.open.by_group["생활소매·식품제조"] || 0) - (B.close.by_group["생활소매·식품제조"] || 0)}, 음식점 ${(B.open.by_group["음식점·제과"] || 0) - (B.close.by_group["음식점·제과"] || 0)}.` }, {
      grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => Math.abs(v) + "건" },
      xAxis: { type: "category", data: grp, axisLabel: { fontSize: 10.5, interval: 0, rotate: 24 } }, yAxis: { type: "value", axisLabel: { formatter: (v) => Math.abs(v) } },
      series: [{ name: "창업(실질)", type: "bar", stack: "a", data: grp.map((k) => B.open.by_group[k] || 0), color: C.green }, { name: "폐업(실질)", type: "bar", stack: "a", data: grp.map((k) => -(B.close.by_group[k] || 0)), color: C.red },
        { name: "임시영업(창업·폐업 중복)", type: "bar", stack: "a", data: grp.map((k) => (B.open.by_group_all[k] || 0) - (B.open.by_group[k] || 0)), color: C.gray2 }],
    });
    // 2. 폐업 업력
    const ab = B.closure_age_bins;
    card(g, { title: "2024 실질 폐업 39건의 업력 — 30년 넘은 가게 4곳", sub: "인허가일 → 폐업일", size: "half", tier: "T2", src: B.src, note: `30년+: ${B.closed_over30.map((r) => `${r[0]}(${r[1]}, ${r[2]}~)`).join(" · ")}. 1961년 계림여인숙, 1980년 대원슈퍼, 1982년 고도삼계탕, 1984년 이화순미용실 — 생활업종의 세대 교체 없는 소멸.` },
      hbar(Object.keys(ab), Object.values(ab), { unit: "건", top: 5, color: C.red }));
    // 3. 격자 합계 vs 황오동 (2018=100)
    const yrs6 = HW.series.years; const idx = (a) => a.map((v) => +(v / a[0] * 100).toFixed(1));
    card(g, { title: "사업구역(격자 32셀) 5지표 — 종사자가 가장 빨리 빠진다", sub: "2018=100 · 점선은 황오동 전체 인구", size: "half", h: "tall", tier: "T2", src: HW.series.src, note: "2020 사업체 +11%는 전국사업체조사 모집단 확대(보고서 각주). 종사자 3,357→2,580: KT 블록(548622) 816→649, 성동시장 셀(549623) 394→194. 지도 ‘황오동 모니터링’ 그룹에서 셀별로 볼 수 있다." }, {
      grid: { left: 8, right: 16, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: yrs6 }, yAxis: { type: "value", scale: true, min: 70 },
      series: [...Object.entries({ pop: "인구", hh: "가구", biz: "사업체", emp: "종사자", house: "주택" }).map(([k, t], i) => ({ name: t, type: "line", data: idx(HW.series.site[k]), color: [C.green, C.green2, C.orange, C.blue, C.purple][i], lineStyle: { width: k === "emp" ? 3 : 1.8 } })),
        { name: "황오동 인구", type: "line", data: idx(HW.series.dong.pop), color: C.gray, lineStyle: { type: "dashed" } }],
    });
    // 4. 황오동 연령구조 2018 vs 2025
    const bands = Object.keys(P.age);
    card(g, { title: "황오동 연령구조 2018 → 2025.07 — 20대·50대가 비고 75세+만 는다", sub: "주민등록 5세 계급 (명)", size: "half", h: "tall", tier: "T2", src: P.src, note: `0–14세 ${pct(P.share_0_14[0])}→${pct(P.share_0_14.at(-1))}, 15–64세 ${pct(P.share_15_64[0])}→${pct(P.share_15_64.at(-1))}, 65세+ ${pct(P.share_65[0])}→${pct(P.share_65.at(-1))}. 25–29세 407→230, 55–59세 798→508, 80–84세 232→376.` }, {
      grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: bands, axisLabel: { fontSize: 10, interval: 1, rotate: 40 } }, yAxis: { type: "value" },
      series: [{ name: "2018", type: "bar", data: bands.map((b) => P.age[b]["2018"]), color: C.gray2 }, { name: "2025.07", type: "bar", data: bands.map((b) => P.age[b]["2025.07"]), color: C.green }],
    });
    // 5. 월매출
    card(g, { title: "대표 5업종 월매출 합계 2023.09–2025.04 — 2024.10 점프는 의원이 만든다", sub: "만 원/월 · 슈퍼마켓·백반/한정식·미용실·여관/모텔·피부/비뇨기과의원", size: "half", tier: "T2", src: SS.src, note: SS.note + `. 2024.01–2025.04 평균 ${fmt(Object.values(SS.by_upjong_2024_01_2025_04).reduce((a, b) => a + b, 0))}만 원 중 의원 ${fmt(SS.by_upjong_2024_01_2025_04["피부/비뇨기과의원"])}(${(SS.by_upjong_2024_01_2025_04["피부/비뇨기과의원"] / 15544 * 100).toFixed(0)}%) · 슈퍼마켓 ${fmt(SS.by_upjong_2024_01_2025_04["슈퍼마켓"])}.` }, {
      grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "만 원" },
      xAxis: { type: "category", data: SS.months, axisLabel: { fontSize: 10, formatter: (v) => (v.endsWith("-01") || v === "2023-09" ? v : v.slice(5)) } }, yAxis: { type: "value", scale: true, axisLabel: { formatter: (v) => (v / 10000).toFixed(1) + "억" } },
      series: [{ type: "line", data: SS.total_manwon, color: C.orange, areaStyle: { opacity: .12 }, lineStyle: { width: 2.5 }, markLine: { silent: true, symbol: "none", lineStyle: { type: "dashed", color: C.ink3 }, data: [{ xAxis: "2024-10", label: { formatter: "2024.10" } }] } }],
    });
    // 6. 업종별 매출 구성
    const bu = SS.by_upjong_2024_01_2025_04;
    card(g, { title: "5업종 월평균 매출 구성 (2024.01–2025.04)", sub: "만 원/월", size: "half", tier: "T2", src: SS.src, note: "‘상권 매출 +15%’는 이 5개 대표업종 합계다. 피부/비뇨기과의원 한 업종이 57%를 차지해 소매·음식 상권의 지표로는 약하다." },
      hbar(Object.keys(bu), Object.values(bu), { unit: "만 원", top: 5, color: C.orange }));
    // 7. 설문 — 인지도·만족도·소속감
    card(g, { title: "주민·상인 설문 2020–2024 — 인지도·소속감은 오르고 보행환경은 내려간다", sub: "10점 척도 · 인지도는 %", size: "half", tier: "T2", src: SR.src, note: SR.note }, {
      grid: { left: 8, right: 44, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: SR.years }, yAxis: [{ type: "value", min: 0, max: 10 }, { type: "value", min: 0, max: 100, axisLabel: { formatter: (v) => v + "%" }, splitLine: { show: false } }],
      series: [{ name: "전반 만족도", type: "line", data: SR.overall_satis, color: C.green, lineStyle: { width: 2.5 } }, { name: "주거환경", type: "line", data: SR.housing_env, color: C.green2 }, { name: "보행환경", type: "line", data: SR.walk_env, color: C.red }, { name: "소속감(황오동)", type: "line", data: SR.belonging["황오동"], color: C.purple }, { name: "공공기관 신뢰", type: "line", data: SR.trust["공공기관"], color: C.blue }, { name: "인지도(우축)", type: "bar", yAxisIndex: 1, data: SR.awareness, color: "rgba(31,94,66,.18)" }],
    });
    // 8. 거점공간 만족도 하락 + 기대
    const hubs = Object.keys(SR.hub_expect_2024);
    card(g, { title: "거점공간 — 준공된 곳은 만족도가 매년 하락, 미준공은 보행사업만 기대 7점대", sub: "10점 척도", size: "half", h: "tall", tier: "T2", src: SR.src, note: `청년창업거점센터·작은도서관(2021.03 준공) 9.6→6.7→4.4, 오픈스튜디오 6.6→4.3, 어울림마당 6.7→4.6. 2024 프로그램 만족도도 창업 인큐베이터 4.4·상권 활성화 4.5 vs 안전한 골목길 8.2. 이용자 수는 청년센터·도서관 2,870(2022)→9,697(2023).` }, {
      grid: { left: 8, right: 16, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: [...Object.keys(SR.hub_satis), ...hubs], axisLabel: { fontSize: 10, interval: 0, rotate: 24 } }, yAxis: { type: "value", min: 0, max: 10 },
      series: [{ name: "2022 만족", type: "bar", data: [...Object.values(SR.hub_satis).map((a) => a[2]), ...hubs.map(() => null)], color: C.gray2 }, { name: "2023 만족", type: "bar", data: [...Object.values(SR.hub_satis).map((a) => a[3]), ...hubs.map(() => null)], color: C.gray },
        { name: "2024 만족", type: "bar", data: [...Object.values(SR.hub_satis).map((a) => a[4]), ...hubs.map(() => null)], color: C.red }, { name: "2024 기대(미준공)", type: "bar", data: [...Object.keys(SR.hub_satis).map(() => null), ...hubs.map((h) => SR.hub_expect_2024[h])], color: C.green }],
    });
    // 9. 방문객 이전 방문지
    const pp = SV.prev_place;
    card(g, { title: "방문객 ‘직전 방문지’ 2020–2024 — 황리단길 54%→12%, 성동시장 9%→48%", sub: "% · 표본·조사장소가 매년 다름(2024는 축제 현장)", size: "half", tier: "T2", src: SV.src, note: SV.note }, {
      grid: { left: 8, right: 16, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
      xAxis: { type: "category", data: SV.years }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } },
      series: Object.entries(pp).map(([k, a], i) => ({ name: k, type: "bar", stack: "p", data: a.map((v) => v ?? 0), color: [C.orange, C.green2, C.blue2, C.purple, C.blue, C.gray, C.gray2][i] })),
    });
    // 10. 방문 계기·체류
    card(g, { title: "방문 계기 — 2024는 축제 50%, 체류 3시간 미만 79%, 1만 원 이상 지출 2.7%", sub: "%", size: "half", tier: "T2", src: SV.src, note: `방문객 인지도 26.8→66.0%, 만족도 7.4→7.9. 오후 방문 ${SV.time_pm.at(-1)}%. 경주시민 비율 ${pct(SV.resident_gj_2024, 1)} — ‘관광객’ 지표가 아니라 주민 행사 지표에 가깝다.` }, {
      grid: { left: 8, right: 16, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
      xAxis: { type: "category", data: SV.years }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } },
      series: [...Object.entries(SV.motive).map(([k, a], i) => ({ name: k, type: "bar", stack: "m", data: a.map((v) => v ?? 0), color: [C.green, C.blue, C.purple, C.green2, C.orange, C.gray2][i] })), { name: "1만 원 이상 지출", type: "line", data: SV.spend_over_10, color: C.red, lineStyle: { width: 2.5 } }],
    });
    // 11. 업력 10년+
    card(g, { title: "업력 10년 이상 311곳의 업종 — 방앗간·참기름·식육·여인숙·다방", sub: "영업 중 628곳 (2025.05) 중 · 세부업종별 곳", size: "half", h: "tall", tier: "T2", src: T.src, note: `최장 ${T.oldest.slice(0, 5).map((r) => `${r[0]} ${r[1]}년`).join(" · ")}. 2018 이후 폐업 상위: 한식 44·즉석판매 36·다방 17·휴게음식 16.` },
      hbar(Object.keys(T.over10y_by_upjong), Object.values(T.over10y_by_upjong), { unit: "곳", top: 12, color: C.green }));
    // 12. 창업·폐업 비교군 (대상지/황오동/경주시/경북 2018=100)
    const cmpk = ["대상지", "황오동", "경주시", "경상북도"]; const cmpv = { 대상지: { startups: K.startups, closures: K.closures }, ...K.compare };
    card(g, { title: "폐업 건수 지수 — 대상지·황오동·경주시·경북 (2018=100)", sub: "지방행정인허가 전 업종 · 대상지 2024 = 194(임시영업 포함)", size: "half", tier: "T2", src: K.src, note: "경북 폐업은 2020부터 6년 연속 증가(+29%). 대상지 2024의 급등(+83%)은 임시영업 27건이 만든 것으로, 실질 39건은 2021년(57건)보다 적다." }, {
      grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: K.years }, yAxis: { type: "value", scale: true },
      series: cmpk.map((k, i) => ({ name: k, type: "line", data: idx(cmpv[k].closures), color: [C.red, C.orange, C.blue, C.gray][i], lineStyle: { width: k === "대상지" ? 3 : 1.8 } })),
    });
  }


  // ---------- 8c. 예술인
  if (AR) {
    const G = AR.gyeongju, F = AR.fields, A = AR.ages;
    const fi = (n) => F.labels.indexOf(n);
    s = section("arts", "경주의 예술인 — 예술활동증명 675명 · 경제총조사 (2026.09)", "예술인이 많은 도시가 아니라, 구성이 특이한 도시다", `한국예술인복지재단에 예술활동증명을 마친 경주 예술인은 <b>${fmt(G.n)}명</b>, 인구 1만 명당 ${G.per10k}명이다. 경북의 시 가운데 1위지만 전국 평균(약 ${AR.nation.per10k})보다 낮고, 8개 도 122개 시군구 중 ${G.rank_in_8do[0]}위다. 대신 구성이 다르다. <b>국악 ${F.pct["경주"][fi("국악")]}%</b>(전국 ${F.pct["전국"][fi("국악")]}%), 미술 ${F.pct["경주"][fi("미술")]}%, 연극·영화·연예는 합쳐 ${(F.pct["경주"][fi("연극")] + F.pct["경주"][fi("영화")] + F.pct["경주"][fi("연예")]).toFixed(1)}%뿐이다. 50–60대가 ${(A.pct["경주"][3] + A.pct["경주"][4]).toFixed(1)}%로 전국(${(A.pct["전국"][3] + A.pct["전국"][4]).toFixed(1)}%)보다 훨씬 늙었다. 사업체 통계로 보면 창작업 종사자는 ${AR.econ[0].create_emp_2020}명인데 <b>사적지·박물관·도서관 종사자는 ${AR.econ[0].heritage_emp_2020}명</b> — 경주의 예술 고용은 창작이 아니라 유산 관리에 있다.`);
    tiles(s, [
      { k: "예술활동증명 누적 (2026.09)", v: fmt(G.n), u: "명", d: `여 ${G.female}·남 ${G.male} · 경북 4,297의 15.7%` },
      { k: "인구 1만 명당", v: G.per10k, u: "명", d: `경북 시 1위 · 전국 약 ${AR.nation.per10k} · 전주 ${AR.compare[1].per10k} · 공주 ${AR.compare[3].per10k}`, cls: "down" },
      { k: "국악 비중", v: pct(F.pct["경주"][fi("국악")]), d: `전국 ${pct(F.pct["전국"][fi("국악")])}의 3.3배 · ${F.gyeongju_n[fi("국악")]}명`, cls: "up" },
      { k: "50–60대 비중", v: pct(A.pct["경주"][3] + A.pct["경주"][4]), d: `전국 ${pct(A.pct["전국"][3] + A.pct["전국"][4])} · 30대는 ${pct(A.pct["경주"][1])} (전국 ${pct(A.pct["전국"][1])})`, cls: "down" },
      { k: "사적지·박물관·도서관 종사자 (2020)", v: fmt(AR.econ[0].heritage_emp_2020), u: "명", d: `1만 명당 ${AR.econ[0].heritage_per10k_2020} · 인구 5만↑ ${AR.heritage_rank[1]}곳 중 ${AR.heritage_rank[0]}위 · 창작업은 ${AR.econ[0].create_emp_2020}명` },
    ]);
    g = grid(s); g.style.marginTop = "14px";
    const hl = (names, key, base_) => names.map((n) => ({ value: key(n), itemStyle: { color: n.name === "경주시" ? C.red : base_ } }));
    card(g, { title: "인구 1만 명당 예술인 — 비교 도시 10곳", sub: "예술활동증명 누적 ÷ 주민등록 2026.08", size: "half", tier: "T2", src: AR.src.kawf, note: "전주(한옥마을·소리문화, 국립무형유산원)와 강릉·공주는 30 후반~60. 경주는 역사도시 가운데 낮은 편이다. 예술활동증명은 복지사업 신청용 등록이라 등록하지 않은 공예인·귀촌 작가는 빠진다." },
      { ...hbar(AR.compare.map((x) => x.name), AR.compare.map((x) => x.per10k), { unit: "명", top: 10, color: C.green }), series: [{ type: "bar", data: hl(AR.compare, (x) => x.per10k, C.green), barCategoryGap: "32%", label: { show: true, position: "right", fontSize: 11.5, color: C.ink2, formatter: (d) => d.value } }] });
    card(g, { title: "경북 10개 시 — 1만 명당 예술인", sub: "절대 수는 포항 764 > 경주 675 > 경산 654", size: "half", tier: "T2", src: AR.src.kawf, note: `경북 전체 4,297명 중 경주 15.7%. 포항은 인구가 2배라 1만 명당 ${AR.gb_cities.find((x) => x.name === "포항시").per10k}에 그친다. 경산(대학 도시)이 근소한 2위.` },
      { ...hbar(AR.gb_cities.map((x) => x.name), AR.gb_cities.map((x) => x.per10k), { unit: "명", top: 10, color: C.green2 }), series: [{ type: "bar", data: hl(AR.gb_cities, (x) => x.per10k, C.green2), barCategoryGap: "32%", label: { show: true, position: "right", fontSize: 11.5, color: C.ink2, formatter: (d) => d.value } }] });
    card(g, { title: "분야 구성 — 국악·미술·문학이 크고, 연극·영화·연예가 없다", sub: "각 지역 예술인 중 비율 %", size: "half", h: "tall", tier: "T2", src: AR.src.kawf, note: `경주 국악 ${F.gyeongju_n[fi("국악")]}명은 전주(판소리, ${F.pct["전주"][fi("국악")]}%)보다 비중이 높다. 1991년부터 35년째 이어진 경주국악여행(2025년 19개 팀)·경주시립신라고취대·신라문화제가 만든 제도적 수요. 연극·영화·연예 합 ${(F.pct["경주"][fi("연극")] + F.pct["경주"][fi("영화")] + F.pct["경주"][fi("연예")]).toFixed(1)}%(전국 ${(F.pct["전국"][fi("연극")] + F.pct["전국"][fi("영화")] + F.pct["전국"][fi("연예")]).toFixed(1)}%)는 공연장·제작 산업이 없는 도시의 전형.` }, {
      grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
      xAxis: { type: "category", data: F.labels.slice(0, 11), axisLabel: { fontSize: 11, interval: 0 } }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" } },
      series: [{ name: "경주", type: "bar", data: F.pct["경주"].slice(0, 11), color: C.red }, { name: "전주", type: "bar", data: F.pct["전주"].slice(0, 11), color: C.orange2 }, { name: "전국", type: "bar", data: F.pct["전국"].slice(0, 11), color: C.gray2 }],
    });
    card(g, { title: "연령 구성 — 경주는 50–60대, 전국은 30대", sub: "각 지역 예술인 중 비율 %", size: "half", h: "tall", tier: "T2", src: AR.src.kawf, note: `경주 30대 ${A.gyeongju_n[1]}명(${A.pct["경주"][1]}%)이 황리단길·황남동 공방 세대에 해당하지만 임대료 상승으로 이탈이 보도되는 층이다. 50–60대 ${A.gyeongju_n[3] + A.gyeongju_n[4]}명은 1946 경주예술학교 계보와 남산 예술인 마을 세대 — 10년 안에 절반이 은퇴한다.` }, {
      grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
      xAxis: { type: "category", data: A.labels }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" } },
      series: [{ name: "경주", type: "line", data: A.pct["경주"], color: C.red, lineStyle: { width: 3 }, areaStyle: { opacity: .08 } }, { name: "전주", type: "line", data: A.pct["전주"], color: C.orange2 }, { name: "안동", type: "line", data: A.pct["안동"], color: C.green2 }, { name: "전국", type: "line", data: A.pct["전국"], color: C.ink, lineStyle: { type: "dashed" } }],
    });
    const ec = AR.econ;
    card(g, { title: "사업체 통계로 본 ‘예술 고용’ — 창작업 vs 유산 관리업 종사자", sub: "경제총조사 2020 · 인구 1만 명당 종사자", size: "half", h: "tall", tier: "T2", src: AR.src.econ, note: `경주 901 창작·예술업은 44개소 ${ec[0].create_emp_2020}명(2015년 13개소 ${ec[0].create_emp_2015}명), 902 사적지·박물관·도서관은 81개소 ${ec[0].heritage_emp_2020}명. 국립경주박물관·국립경주문화유산연구소·발굴법인·문화재수리업체가 여기에 있다. 석공·와공·단청·보존과학 기능인이 ‘예술인’으로 등록되는 경로이기도 하다.` }, {
      grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: ec.map((x) => x.name.replace("시", "").replace("군", "")), axisLabel: { fontSize: 11, interval: 0 } }, yAxis: { type: "value" },
      series: [{ name: "902 사적지·박물관·도서관", type: "bar", data: ec.map((x) => x.heritage_per10k_2020), color: C.green }, { name: "901 창작·예술", type: "bar", data: ec.map((x) => x.create_per10k_2020), color: C.orange }],
    });
    const sd = Object.entries(AR.nation.sido);
    card(g, { title: "시도별 예술활동증명 — 서울·경기가 61%", sub: "명 · 전국 222,002 (2026.09)", size: "half", h: "tall", tier: "T2", src: AR.src.kawf, note: `경북 4,297명(1.9%)은 17개 시도 중 13위. 누적 증명은 2022년 157,414 → 2026년 222,002로 4년 새 41% 늘었다(신진예술인 특례 확대).` },
      hbar(sd.map((x) => x[0]), sd.map((x) => x[1]), { unit: "명", top: 17, color: C.gray }));
    // 왜 — 다섯 겹
    const why = $(`<div class="card"><h3>왜 경주에 있나 — 다섯 겹</h3><p class="sub">수치(T2)와 달리 ‘이유’는 언론·연재 기사(T4)에 기댄다. 계획 문서에 쓰기 전 1차 자료가 필요하다.</p>
      <table class="t"><tr><th>겹</th><th>무엇이</th><th>근거·등급</th></tr>
      <tr><td>① 유산이 소재이자 일자리</td><td>남산동 예술인 마을(석장 윤만걸·도예 권은희·백성일 등)은 “터의 기운과 불적(佛蹟)” 때문에 자발적으로 모였고, 박대성은 2005년 삼릉에 정착. 발굴연구소·박물관·수리업체 종사자 540명</td><td><span class="tier t4">T4</span> 서울신문 2016 · 경주시 관광 / <span class="tier t2">T2</span> 경제총조사</td></tr>
      <tr><td>② 국악은 제도가 만든 수요</td><td>경주국악여행 1991년~(2025년 19개 팀), 경주시립신라고취대·시립예술단 인큐베이팅, 신라문화제(1962~)</td><td><span class="tier t4">T4</span> 경북일보 2026 · 경주문화재단</td></tr>
      <tr><td>③ 1946 경주예술학교</td><td>남한 최초 예술전문학교. 최부자·수봉재단 후원, 손일봉(초대 교장)·김만술·윤경렬 교수진, 전국에서 100여 명. <b>교사(校舍)는 옛 경주역사와 철도기관고</b> — 폐역 부지를 예술 교육으로 쓴 선례가 경주 안에 있다</td><td><span class="tier t4">T4</span> 서라벌신문 2017 연재(최용대·경주미술사연구회)</td></tr>
      <tr><td>④ 문학의 고향</td><td>김동리·박목월 → 동리목월문학관(2006). 문학 ${F.pct["경주"][fi("문학")]}% (전국 ${F.pct["전국"][fi("문학")]}%)</td><td><span class="tier t4">T4</span></td></tr>
      <tr><td>⑤ 최근 유입과 이탈</td><td>2016년 이후 황리단길·황남동에 도예·금속공방·독립서점 창업자(30대) 유입, 임대료 상승으로 이탈 중. 동국대 WISE캠퍼스 불교미술 전공이 교육 공급</td><td><span class="tier t4">T4</span> 오마이뉴스 · 한국AI부동산신문</td></tr>
      </table>
      <p class="note">계획에 쓰는 법: 부지 프로그램은 공연장(연극·영화)이 아니라 공방·작업실·국악 연습실·수리기능 공방 쪽이 지역 예술인 구성과 맞는다. 50–60대 40%와 30대 이탈을 감안하면 부지 내 저가 작업공간의 공급·운영 주체를 명시해야 한다. 성과지표 후보: 예술활동증명 시군구 수(연 1회) + 902 종사자(5년).</p></div>`);
    s.appendChild(why); why.style.marginTop = "14px";
  }

  // ---------- 9. 데이터 카탈로그
  s = section("sources", "출처", "이 페이지가 쓴 문서와 등급", "숫자를 인용할 때는 여기 적힌 쪽과 등급을 그대로 옮긴다. 전사본(모니터링 보고서 표를 손으로 옮긴 것)은 원문 대조 전 인용 금지.");
  const tbl = $(`<div class="card"><table class="t"><tr><th>등급</th><th>문서</th><th>쓰인 곳</th></tr></table></div>`);
  const rows = [["T1", "2030 경주도시기본계획 (승인, 475쪽 → 45절 마크다운, 표 697)", "인구·토지·교통·관광·경제·주거·재정·시민의식 2015"], ["T1", "2030 경주시 경관계획 재정비 (2025.04)", "경관의식조사"], ["T1", "경주시 도시재생 전략계획(변경) (2022.01)", "쇠퇴진단 — 지도"], ["T1", "경주시 고시 제2026-8호 지구단위계획 · 경북 고시 2020-479호 고도지구", "지도 레이어"],
    ["T2", "경주시 원도심 미래구상 기획연구 (동국대·가천대, 2025.07, 417쪽)", "시민설문 2025 · 인지지도 · 2025 예산"], ["T2", "황오동 원도심·행복황촌 도시재생 성과지표 모니터링 (2025.09 / 2025.12)", "유동인구 2020–24 · 창업폐업 · 공시지가 · 격자 32셀 · 연령구조 · 설문 2020–24 · 2024 창업·폐업 목록"], ["T2", "소상공인365 (소진공) 상권분석 리포트", "유동인구 8구역 · 업종·매출"], ["T2", "한국예술인복지재단 예술활동증명 대시보드 (2026.09) · 통계청 경제총조사 2015·2020", "예술인 수·분야·연령 · 창작/유산관리 종사자"], ["T2", "KOSIS 주민등록 · 관광데이터랩 · ITS · 건축HUB · V-World", "지도 현황 레이어"], ["T2", "김권일(신라문화유산연구원) 2026.02 혁신포럼 · 시굴조사 추진계획", "매장유산"], ["T4", "2023 폐철도 기본구상 설문 (언론 경유)", "시청 이전 63.7% — 원문 미확보"]];
  for (const [t, d, u] of rows) tbl.querySelector("table").appendChild($(`<tr><td><span class="tier ${t.toLowerCase()}">${t}</span></td><td>${d}</td><td>${u}</td></tr>`));
  s.appendChild(tbl);

  // TOC 하이라이트
  const links = [...toc.querySelectorAll("a")]; const secs = [...document.querySelectorAll("section.sec")];
  const io = new IntersectionObserver((es) => { for (const e of es) if (e.isIntersecting) links.forEach((a) => a.classList.toggle("on", a.getAttribute("href") === "#" + e.target.id)); }, { rootMargin: "-20% 0px -70% 0px" });
  secs.forEach((x) => io.observe(x));
  window.addEventListener("resize", () => charts.forEach((c) => c.resize()));
}
main_();
