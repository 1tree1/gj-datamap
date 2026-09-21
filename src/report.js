// 구경주역 통계 리포트 — 카드뉴스 판 (2026-09-21)
// 구조: ① 목표·이유·근거(hero) ② 그룹 칩 ③ 카드 격자(썸네일 차트 + 한 줄 요지) ④ 클릭 → 상세 다이얼로그(큰 차트 + 읽는 법 + 보이는 것 + 출처)
// 문장 원칙: 사실 → 수치 → 출처. 비유·수사 없이 쓴다. 전문용어는 처음 나올 때 괄호로 풀어 쓴다.
// 무거운 GeoJSON은 pipeline/build_report_map_stats.py 가 숫자만 뽑아 map_stats.json 으로 준다.
import * as echarts from "echarts";

const base = import.meta.env.BASE_URL;
const C = { green: "#1f5e42", green2: "#5f9f7a", green3: "#a8cbb6", orange: "#c7641c", orange2: "#e8a86b", red: "#c0392b", blue: "#2f6db5", blue2: "#8fb4e0", purple: "#6f4fa3", purple2: "#b39ddb", gray: "#9aa0a6", gray2: "#d3d6da", ink: "#1d1d1f", ink2: "#515154", ink3: "#86868b" };
const FONT = getComputedStyle(document.documentElement).getPropertyValue("--font");
echarts.registerTheme("gj", {
  color: [C.green, C.orange, C.blue, C.purple, C.red, C.gray],
  textStyle: { fontFamily: FONT, color: C.ink2 },
  legend: { textStyle: { color: C.ink2, fontSize: 12 }, itemWidth: 12, itemHeight: 8, icon: "roundRect" },
  tooltip: { backgroundColor: "rgba(255,255,255,.96)", borderColor: "rgba(0,0,0,.1)", borderWidth: 1, textStyle: { color: C.ink, fontSize: 12.5 }, padding: [8, 10], extraCssText: "box-shadow:0 6px 24px rgba(0,0,0,.08);border-radius:10px" },
  categoryAxis: { axisLine: { lineStyle: { color: "rgba(0,0,0,.12)" } }, axisTick: { show: false }, axisLabel: { color: C.ink3, fontSize: 11.5 }, splitLine: { show: false } },
  valueAxis: { axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: C.ink3, fontSize: 11.5 }, splitLine: { lineStyle: { color: "rgba(0,0,0,.06)" } } },
  line: { symbolSize: 5, smooth: false }, bar: { barMaxWidth: 34 },
});
const fmt = (v) => (v == null ? "–" : Number(v).toLocaleString("ko-KR"));
const pct = (v, d = 1) => (v == null ? "–" : Number(v).toFixed(d) + "%");
const sgn = (v) => (v > 0 ? "+" : "") + fmt(v);
const $ = (h) => { const t = document.createElement("template"); t.innerHTML = h.trim(); return t.content.firstElementChild; };
const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
const hbar = (cats, vals, { color = C.green, unit = "", top = 8, max, fmtV, colors } = {}) => ({
  grid: { left: 4, right: 48, top: 4, bottom: 4, containLabel: true },
  tooltip: { trigger: "axis", axisPointer: { type: "none" }, valueFormatter: (v) => (fmtV ? fmtV(v) : fmt(v) + unit) },
  xAxis: { type: "value", show: false, max },
  yAxis: { type: "category", inverse: true, data: cats.slice(0, top), axisLine: { show: false }, axisLabel: { color: C.ink, fontSize: 12, width: 150, overflow: "truncate" } },
  series: [{ type: "bar", data: vals.slice(0, top).map((v, i) => (colors ? { value: v, itemStyle: { color: colors[i] } } : v)), itemStyle: { color, borderRadius: [0, 4, 4, 0] }, barCategoryGap: "32%", label: { show: true, position: "right", fontSize: 11.5, color: C.ink2, formatter: (d) => (fmtV ? fmtV(d.value) : fmt(d.value) + unit) } }],
});
const TIER = (t) => (t ? `<span class="tier ${t.toLowerCase()}">${t}</span>` : "");

// ---------------------------------------------------------------- 카드 레지스트리
const GROUPS = [
  { id: "site", title: "부지와 규제", read: "부지 156,460㎡에 이미 정해져 있는 것(획지·높이 제한·문화유산 보호구역)과 건물 노후 상태, 현재 시청 건물의 상황." },
  { id: "people", title: "사람", read: "인구는 계획과 달리 줄고 있고 고령 비율은 높다. 청년이 어디 살고 몇 명이 빠져나가는지, 외국인 주민은 어떤 사람들인지." },
  { id: "work", title: "일과 상권", read: "경주는 제조업 고용 비중이 높은 도시이면서 관광 도시다. 원도심의 유동인구, 가게 수 변화, 땅값." },
  { id: "move", title: "이동", read: "통행 수단 비율의 변화, 주차장 구성, 버스 이용, 시간대별 도로 속도." },
  { id: "visit", title: "관광·경관·예술", read: "관광객 수, 시민과 관광객이 생각하는 대표 경관, 경주 예술인의 수와 구성." },
  { id: "voice", title: "시민의 목소리", read: "2015년·2023년·2025년의 설문과 2020~2024년 모니터링 설문. 조사 방법이 서로 달라 수치를 직접 비교하지 않고 방향만 읽는다." },
  { id: "data", title: "데이터 출처와 처리", read: "카드 1장이 자료 1건이다. 어디서 났고, 어떻게 가져왔고(API·파일·손 전사·도면 디지타이징·웹 열람), 무엇을 계산했고, 어느 레이어와 카드에 그렸는지, 무엇이 한계인지 적었다. 손으로 옮겨 적은 표와 내가 근사한 경계는 그렇다고 썼다." },
];
const CARDS = []; const byId = {};
function add(c) { c.g = c.g || "site"; CARDS.push(c); byId[c.id] = c; }

// ---------------------------------------------------------------- 데이터
async function j(p) { try { return await fetch(`${base}data/${p}`, { cache: "no-cache" }).then((r) => (r.ok ? r.json() : null)); } catch { return null; } }
async function main_() {
  const [R, HW, AR, Y, NAT, VIS, TH, TC, MS, AT] = await Promise.all(["report_stats.json", "hwango_report.json", "arts_stats.json", "youth.json", "nationality.json", "visitors.json", "traffic_hist_summary.json", "traffic_congested.json", "map_stats.json", "arrival_transport.json"].map(j));
  const X = R.extras; const p26 = R.pop_actual.pop_2026_08;
  const FF = ["A_hwango_grid32", "B_haengbok_hwangchon_digitized", "C_zone_buffer300", "D_zone", "E_center_r300", "F_cityhall_r500", "G_seongdong_market_r200", "H_hwangridan_r300"];
  const AC = { A_hwango_grid32: C.green, B_haengbok_hwangchon_digitized: C.gray, C_zone_buffer300: C.green2, D_zone: C.red, E_center_r300: C.green3, F_cityhall_r500: "#0f3d34", G_seongdong_market_r200: C.orange, H_hwangridan_r300: C.purple };
  const lo = (k) => parseInt(String(k).replace("+", "").split("-")[0]);

  // ======================= 부지와 규제
  if (MS?.blocks) add({ id: "blocks", g: "site", t: "지구단위계획 획지 면적 — 도면에서 잰 값과 고시문 수치", take: "고시 도면을 좌표에 맞춰 잰 획지 면적은 고시문 수치와 ±4% 안에서 일치한다. 좌표 변환이 맞다는 확인이다.", size: "m", tier: "T1", src: MS.blocks.src,
    lead: "고시 제2026-8호 지형도면을 좌표에 맞추고 획지별로 면적을 쟀다. 회색은 고시문에 적힌 면적, 초록은 도면에서 잰 면적이다.",
    note: "상1~3은 상업용지, 공청1·2는 공공청사용지, 문화1은 문화시설용지, 주1은 주차장, 근린공원은 3곳이다. 공청1+공청2는 24,987㎡다. 시청 본청에 필요한 연면적은 38,000~45,000㎡로 추정되므로(§시청 구성) 이 획지만으로는 부족하다.",
    opt: { grid: { left: 4, right: 60, top: 26, bottom: 4, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "㎡" }, xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: MS.blocks.rows.map((r) => r[0]), axisLabel: { color: C.ink, fontSize: 12 } },
      series: [{ name: "고시문", type: "bar", data: MS.blocks.rows.map((r) => r[3]), color: C.gray2, barGap: "-55%", barCategoryGap: "35%" }, { name: "도면 측정", type: "bar", data: MS.blocks.rows.map((r) => r[2]), color: C.green, label: { show: true, position: "right", fontSize: 11, color: C.ink2, formatter: (d) => fmt(d.value) } }] }, map: "blocks" });
  if (MS?.godo) add({ id: "godo", g: "site", t: "높이 제한 구역(고도지구) — 높이 상한별 면적", take: "부지는 20m 이하 구역 146,489㎡와 15m 이하 구역 11,729㎡에 속한다. 20m는 황오동 삼층석탑 주변의 문화유산 높이 기준을 그대로 받은 값이라 공공청사도 예외가 없다.", tier: "T1", src: MS.godo.src,
    lead: "고도지구는 건물 높이의 상한을 정한 구역이다. 경주 도심과 구정동의 고도지구 폴리곤(V-World)에 경북고시 2020-479호의 구역 이름과 높이를 붙여 높이별 면적(ha)을 합쳤다. ‘미확인’은 2020년 도면 범위 밖이라 높이를 붙이지 못한 구역이다.",
    note: "36m 이하 1,006ha, 10m 이하 1,082ha, 20m 이하 834ha가 대부분이다. 원도심 중심부는 20m 이하다.",
    opt: hbar(MS.godo.rows.map((r) => r[0]), MS.godo.rows.map((r) => r[1]), { unit: "ha", top: 9, colors: MS.godo.rows.map((r) => ({ "36m": "#7f0000", "25m": "#b30000", "20m": "#d7301f", "15m": "#ef6548", "12m": "#fc8d59", "10m": "#fdbb84", "7.5m": "#fdd49e", "최저고도": "#2c7bb6" }[r[0]] || "#bdbdbd")) }), map: "godo" });
  if (MS?.reg_areas) add({ id: "regareas", g: "site", t: "규제 구역 13종 — 종류별 면적", take: "역사문화환경보존지역 6,892ha, 국가지정문화유산구역 3,940ha, 역사문화환경보호지구 1,253ha. 이 중 3종은 법정 경계 자료가 없어 필지 경계로 근사했다.", tier: "T1", src: MS.reg_areas.src,
    lead: "V-World의 토지이용규제 폴리곤에서 종류별 개수와 면적(ha)을 합쳤다. 회색 막대는 V-World에 자료가 없어 필지 경계로 근사한 3종(특별보존지구·보존육성지구·중점경관관리구역)이다.",
    note: "부지에 직접 걸리는 규제는 역사문화환경보존지역(도심 2,514ha 폴리곤과 황오동 삼층석탑 주변 17.9ha)이다. 황오동 삼층석탑(문화재자료 8호)은 구역 안에 있다. 문화유산구역·보호지구·방화지구는 구역 안에 없다.",
    opt: hbar(MS.reg_areas.rows.map((r) => r[0]), MS.reg_areas.rows.map((r) => r[2]), { unit: "ha", top: 13, colors: MS.reg_areas.rows.map((r) => (r[3].startsWith("법정") ? C.orange : C.gray2)) }), map: "reg_areas" });
  if (MS?.reg_layers) add({ id: "reglayers", g: "site", t: "필지별 규제 겹 수 — 7,616필지", take: "규제가 2겹 겹친 필지가 4,019개로 가장 많다. 4겹(고도보존·문화유산·지구단위계획 모두 해당)은 148필지다.", tier: "T1", src: MS.reg_layers.src,
    lead: "필지마다 토지이용계획 항목을 읽어 4겹(①용도지역·지구 ②고도보존육성지구 ③문화유산법 보존지역·지정구역 ④지구단위계획)을 셌다. 경계에 닿기만 한 ‘접함’은 규제가 아니므로 제외했다.",
    note: `항목별 필지 수: 고도지구 ${fmt(MS.reg_layers.flags.reg_godo)} · 역사문화환경보존지역 ${fmt(MS.reg_layers.flags.reg_heritage)} · 특별보존지구 ${fmt(MS.reg_layers.flags.reg_special)} · 보존육성지구 ${fmt(MS.reg_layers.flags.reg_boyuk)} · 문화유산구역 ${fmt(MS.reg_layers.flags.reg_cult)} · 지구단위계획구역 ${fmt(MS.reg_layers.flags.reg_jdp)}. 접함을 포함했던 이전 계산에서는 3겹 이상이 4,496필지로 과대 집계됐다.`,
    opt: { grid: { left: 8, right: 16, top: 8, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "필지" }, xAxis: { type: "category", data: MS.reg_layers.dist.map((d) => d[0] + "겹") }, yAxis: { type: "value" },
      series: [{ type: "bar", data: MS.reg_layers.dist.map((d, i) => ({ value: d[1], itemStyle: { color: ["#e9f0ec", "#b7d7c2", "#e3a857", "#b23a2c"][i] } })), label: { show: true, position: "top", formatter: (d) => fmt(d.value) } }] }, map: "reg" });
  if (MS?.bldg_age) add({ id: "bldgage", g: "site", t: "건물 노후 정도 — 사용승인 후 경과 연수", take: `건축물대장이 있는 ${fmt(MS.bldg_age.n)}필지 중 20년 이상이 ${MS.bldg_age.pct20}%, 30년 이상이 ${MS.bldg_age.pct30}%다. 도시재생 쇠퇴 기준(20년 이상 50%)을 넘는다.`, tier: "T1", src: MS.bldg_age.src,
    lead: "성동·황오·노서·노동·성건 5개 법정동의 건축물대장을 필지에 연결해 사용승인일부터 지금까지의 연수를 셌다. 동천동·인왕동은 아직 대장을 받지 못해 빠져 있다.",
    note: `사용승인일이 없는 대장 ${MS.bldg_age.n_unknown}필지(옛 역사·철도시설)는 제외했다. 도시재생 활성화지역 지정 요건은 ‘20년 이상 된 건물이 50% 이상’이다.`,
    opt: hbar(MS.bldg_age.bins.map((b) => b[0]), MS.bldg_age.bins.map((b) => b[1]), { unit: "필지", top: 5, colors: ["#e8f3e6", "#c7e0bd", "#f6d68a", "#e9975a", "#c8452b"] }), map: "parcels" });
  {
    const H = Object.fromEntries(X.heritage.map((h) => [h.k, h]));
    add({ id: "heritage", g: "site", t: "매장문화재 — 시굴조사 대상 145,879㎡", take: "지표조사 148,770㎡ 중 145,879㎡가 시굴조사 대상이다. 시굴은 약 3.06억 원·54일, 정밀발굴은 63~80억 원·630~700일로 추정됐다. 성토 2m 미만의 공원·주차장은 발굴을 미룰 수 있다.", size: "m", tier: "T2", src: X.sources.heritage,
      lead: "2022년 지표조사와 2026년 혁신포럼 시굴조사 추진계획의 수치다. 부지 대부분이 유물이 묻혀 있을 가능성이 있는 구역(성동동사지Ⅱ 40,882㎡ + 유물산포지 104,997㎡)이다.",
      note: "이 수치가 지하층·지하주차장 계획의 상한을 정한다. 1단계에 지하 구조물을 넣기 어렵고, 청사 위치는 시굴 결과가 나온 뒤 확정하는 것이 맞다. 1단계는 지상 광장·공원·기존 철도 노반 활용이 현실적이다.",
      html: `<div class="tiles">${[["시굴조사 대상 면적", fmt(H["시굴조사 필요 면적"].v), "㎡", H["시굴조사 필요 면적"].note], ["기존 조사 면적", fmt(H["기조사 면적(2002~2004 발굴·시굴)"].v), "㎡", "2002~2004 발굴·시굴"], ["시굴 1단계(안)", fmt(H["시굴조사 1단계(안) 면적"].v), "㎡", H["시굴조사 1단계(안) 면적"].note], ["시굴 비용", "3.06", "억 원", "현장 54일"], ["정밀발굴 비용", "63~80", "억 원", "현장 630~700일"], ["발굴 유예 조건", "2m", "미만 성토", "공원·주차장"]].map(([k, v, u, d]) => `<div class="tile"><div class="k">${k}</div><div class="v">${v}<small>${u}</small></div><div class="d">${d}</div></div>`).join("")}</div>` });
  }
  add({ id: "axes", g: "site", t: "경주 도시 축의 변천사 — 인터랙티브 도판 (원본 그대로)", size: "l", tier: "T2", src: "「경주 도시 축의 변천사」 인터랙티브 HTML(2026-09). 배경도 = 경주시 원도심 미래구상 기획연구(2025.07) Figure 3d · 축 서술 p.17–23, 77–109(T2) · 동지 일출 가설축은 다큐 요약(T4)",
    take: "왕경 남북축(신라) → 읍성 행정축(고려·조선) → 철도·역세권축(1918–) → 도로·관광축(1950–) → 외곽 관문축(KTX, 2010–) → 폐철도 재연결축(2021–). 6개 시대 버튼과 ‘전체 축 중첩’으로 축의 이동을 비교하는 도판이다. 클릭하면 원본이 그대로 열린다.",
    lead: "원본 HTML을 수정 없이 넣었다(← → 키로 시대 이동). 선은 도판 저자가 재구성한 도시설계적 개념축이지 지적선·고고학 확정선이 아니며, 배경도 위 위치도 개략 표시다. 좌표가 없는 그림이라 지도 레이어로는 올리지 않았다.",
    html: `<img class="axes-thumb" src="${base}urban_axes_thumb.jpg" alt="경주 도시 축의 변천사 도판">`,
    dlg_html: `<iframe class="axes-frame" src="${base}urban_axes.html" title="경주 도시 축의 변천사" loading="lazy"></iframe><p class="sub"><a href="${base}urban_axes.html" target="_blank" rel="noopener">새 창에서 크게 보기 ↗</a></p>` });
  if (MS?.cityhall) add({ id: "cityhall", g: "site", t: "현재 경주시청 — 본청 45개 과 중 15개 과가 청사 밖에 있다", take: "본관은 1995년 시·군 통합 전의 옛 경주군청 건물이다. 9개 과는 기린빌딩, 3개 과는 동원빌딩을 임차해 쓰고 있다. 문서고는 실내체육관에 있다.", size: "m", tier: "T1", src: MS.cityhall.src,
    lead: "경주시 홈페이지 청사안내(2026-09-02)에서 본청 각 과의 위치를 세었다. 막대는 장소별 과 수, 빨강은 민간 건물 임차다.",
    note: "행정안전부 공유재산 운영기준에 따르면 임차 면적도 청사 기준면적에 포함되고 전세권을 설정해야 한다. 즉 지금은 청사가 부족해 임차로 메우는 상태다. 본청+의회 인원을 800~950명으로 가정하고 1인당 30~35㎡를 적용하면 28,000~33,000㎡, 법정 의무공간과 주민 이용 공간을 더하면 38,000~45,000㎡가 필요하다.",
    opt: hbar(MS.cityhall.rows.map((r) => r.name), MS.cityhall.rows.map((r) => r.n_depts), { unit: "개 과", top: 8, colors: MS.cityhall.rows.map((r) => (/임차/.test(r.own) ? C.red : r.cls === "main" ? C.green : C.gray)) }), map: "cityhall_sites" });
  if (MS?.parking_pub) add({ id: "parkpub", g: "site", t: `공영주차장 ${MS.parking_pub.rows.length}곳, ${fmt(MS.parking_pub.total)}면`, take: "시설관리공단이 운영하는 공영주차장 면수다. 경주시 전체 주차면 51,880면의 99%는 건물 부설주차장이고 공영은 1% 정도다.", tier: "T2", src: MS.parking_pub.src,
    lead: "노상주차장과 민영주차장은 제외한 수치다.", note: "모빌리티 허브의 환승주차장(P+R) 규모를 정할 때 기준이 되는 현재 공영주차 총량이다. 2015년 설문에서 교통 분야 문제 1위는 ‘대규모 주차시설 확충’(38.8%)이었다.",
    opt: hbar(MS.parking_pub.rows.map((r) => r[0]), MS.parking_pub.rows.map((r) => r[1]), { unit: "면", top: 10, color: C.gray }), map: "parking_pub" });
  if (MS?.tourism_complex) add({ id: "tcomplex", g: "site", t: "관광단지 4곳 — 지정 면적", take: "보문(850ha)·마우나오션·감포해양·북경주 웰니스. 모두 원도심 밖에 있다. 관광 숙박 수요는 이 단지들이 받고 있다.", tier: "T1", src: "V-World LT_C_UO601 · 이름은 경북 고시번호를 토지이음 고시정보와 대조해 확인",
    lead: "관광진흥법에 따른 관광단지 지정 경계의 면적(ha)이다. V-World 자료에는 이름이 없어 마지막 고시번호로 확인했다.",
    opt: hbar(MS.tourism_complex.map((r) => r[0]), MS.tourism_complex.map((r) => r[1]), { unit: "ha", top: 4, color: "#0e8a7a" }) });

  // ======================= 사람
  {
    const yrsAll = [...new Set([...R.pop_doc.years, ...R.pop_actual.years, ...R.pop_plan.years, "2026"])].sort();
    const ser = (yrs, vals) => yrsAll.map((y) => { const i = yrs.indexOf(y); return i < 0 ? null : vals[i]; });
    add({ id: "popplan", g: "people", t: "인구 — 2030 계획인구 320,000명, 2026년 실제 242,512명", take: "2030 도시기본계획은 2013년 270,493명에서 2030년 320,000명으로 18% 증가를 예상했다. 실제 주민등록 인구는 계속 줄어 2026년 8월 242,512명이다. 계획보다 24% 적다.", size: "l", tier: "T1", src: `${R.pop_doc.src} / ${R.pop_actual.src}`,
      lead: "회색은 기본계획에 실린 통계연보 수치(2003–13), 검정은 주민등록 인구(2011–25), 초록 점선은 계획인구의 단계별 목표, 빨간 점은 2026년 8월 실제 값이다. 두 통계는 집계 기준이 달라 2011~13년에 약 1만 명 차이가 나므로, 수준이 아니라 증감 방향을 비교한다.",
      note: "계획인구 320,000명은 자연증가 262,490명과 사회적증가 53,769명(산업단지·도시개발·주택건설·신경주역세권 개발로 인한 유입 가정)으로 구성됐다. 가정했던 유입은 일어나지 않았다.",
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: yrsAll, axisLabel: { interval: 2 } }, yAxis: { type: "value", min: 230000, max: 330000, axisLabel: { formatter: (v) => v / 1000 + "k" } },
        series: [{ name: "통계연보", type: "line", data: ser(R.pop_doc.years, R.pop_doc.total), color: C.gray, connectNulls: true }, { name: "주민등록", type: "line", data: ser(R.pop_actual.years, R.pop_actual.total), color: C.ink, lineStyle: { width: 2.5 }, connectNulls: true }, { name: "2030 계획인구", type: "line", data: ser(R.pop_plan.years, R.pop_plan.total), color: C.green, lineStyle: { width: 2, type: "dashed" }, symbolSize: 7, connectNulls: true }, { name: "2026.08", type: "scatter", data: [["2026", p26]], color: C.red, symbolSize: 10, label: { show: true, position: "right", formatter: fmt(p26), fontSize: 11, color: C.red } }] } });
    add({ id: "aging", g: "people", t: "65세 이상 인구 비율 — 2026년 30.0%", take: "기본계획이 2030년에 도달할 것으로 예상한 고령 비율에 2026년에 이미 도달했다.", tier: "T1", src: `${R.aging.src} / ${R.age_projection.src}`,
      lead: "검정은 통계연보 실적과 2026년 주민등록 값, 초록 점선은 기본계획의 예상치다.",
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: [...R.aging.years, "2015", "2020", "2025", "2026", "2030"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" }, max: 40 },
        series: [{ name: "실적", type: "line", data: [...R.aging.pct65, null, null, null, R.aging.pct65_2026, null], color: C.ink, lineStyle: { width: 2.5 }, connectNulls: true }, { name: "계획 예상", type: "line", data: [...Array(9).fill(null), R.age_projection.p65[0], ...R.age_projection.p65.slice(1, 4), null, R.age_projection.p65[4]], color: C.green, lineStyle: { type: "dashed" }, connectNulls: true }, { name: "2026.08", type: "scatter", data: [["2026", R.aging.pct65_2026]], color: C.red, symbolSize: 10, label: { show: true, position: "top", formatter: pct(R.aging.pct65_2026), color: C.red, fontSize: 11 } }] } });
    add({ id: "ageproj", g: "people", t: "연령 구성 예상 — 부양 비율 42% → 83%", take: "기본계획의 예상에서도 2030년에는 일하는 나이(15–64세) 인구 100명이 유소년과 고령 인구 83명을 부양하게 된다.", tier: "T1", src: R.age_projection.src, lead: "0–14세 / 15–64세 / 65세 이상 구성비(%)와 부양 비율[(0–14세 + 65세 이상) ÷ 15–64세]이다.",
      opt: { grid: { left: 8, right: 40, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: R.age_projection.years }, yAxis: [{ type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } }, { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" }, splitLine: { show: false } }],
        series: [{ name: "0–14", type: "bar", stack: "a", data: R.age_projection.p0_14, color: C.blue2 }, { name: "15–64", type: "bar", stack: "a", data: R.age_projection.p15_64, color: C.green3 }, { name: "65+", type: "bar", stack: "a", data: R.age_projection.p65, color: C.orange }, { name: "부양 비율", type: "line", yAxisIndex: 1, data: R.age_projection.dependency, color: C.ink, lineStyle: { width: 2 }, label: { show: true, position: "top", formatter: (d) => d.value + "%", fontSize: 11 } }] } });
    const lzn = Object.keys(R.pop_plan.by_lifezone);
    add({ id: "lifezone", g: "people", t: "생활권별 계획인구와 실제 인구", take: `중심생활권의 2030년 목표는 200,000명이고 2026년 실제는 ${fmt(MS?.lifezone?.rows?.[0]?.pop_2026_actual)}명이다(${MS?.lifezone?.rows?.[0]?.gap_pct}%).`, tier: "T1", src: `${R.pop_plan.src} / 주민등록 2026-08`,
      lead: "회색은 2013년, 초록은 2030년 계획, 빨강은 2026년 실제(행정동 합계)다. 중심생활권은 황남·성건·황오·월성·선도·황성·용강·동천·불국·보덕동과 현곡·천북면이다.",
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: lzn }, yAxis: { type: "value", axisLabel: { formatter: (v) => v / 1000 + "k" } },
        series: [{ name: "2013", type: "bar", data: lzn.map((z) => R.pop_plan.by_lifezone[z][0]), color: C.gray2 }, { name: "2030 계획", type: "bar", data: lzn.map((z) => R.pop_plan.by_lifezone[z][4]), color: C.green }, { name: "2026 실제", type: "bar", data: lzn.map((z) => MS?.lifezone?.rows?.find((r) => r.name === z)?.pop_2026_actual ?? null), color: C.red, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => (d.value ? (d.value / 1000).toFixed(0) + "k" : "") } }] }, map: "lifezone" });
    const sc = R.pop_plan_components.social;
    add({ id: "popcomp", g: "people", t: "계획인구 320,000명의 구성", take: "자연증가 262,490명에 산업단지·도시개발·주택건설·신경주역세권 개발로 53,769명이 유입된다는 가정이 더해졌다.", tier: "T1", src: R.pop_plan_components.src,
      opt: hbar(["자연증가(내국인)", "일반산업단지", "도시개발사업", "주택건설사업", "신경주역세권", "자연증가(외국인)"], [252490, sc["일반산업단지"], sc["도시개발사업"], sc["주택건설사업"], sc["신경주역세권"], 10000], { unit: "명", color: C.green2 }) });
  }
  if (MS?.hadm) {
    const age = MS.hadm.city_age, keys = Object.keys(age).sort((a, b) => lo(a) - lo(b)), tot = keys.reduce((s, k) => s + age[k], 0), o65 = keys.filter((k) => lo(k) >= 65).reduce((s, k) => s + age[k], 0);
    add({ id: "pyramid", g: "people", t: "경주시 연령별 인구 — 2026년 8월", take: `${fmt(tot)}명이고 65세 이상이 ${pct(o65 / tot * 100)}다. 50~60대가 가장 많고 20대 이하로 갈수록 적다.`, tier: "T2", src: MS.hadm.src, lead: "5세 단위 주민등록 인구다. 주황은 65세 이상, 파랑은 0–14세다. 지도에서는 행정동을 클릭하면 그 동의 값으로 바뀐다.",
      opt: { grid: { left: 8, right: 40, top: 4, bottom: 4, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "value", show: false }, yAxis: { type: "category", data: keys.map((k) => k.replace(" - ", "–").replace("세", "")), axisLabel: { fontSize: 10 } },
        series: [{ type: "bar", data: keys.map((k) => ({ value: age[k], itemStyle: { color: lo(k) >= 65 ? C.orange : lo(k) <= 10 ? C.blue2 : C.green } })), barCategoryGap: "20%" }] }, map: "pop_total" });
    const yy = Object.keys(MS.hadm.city_yearly);
    add({ id: "yearly", g: "people", t: "행정동 합계 인구 2011–2025", take: "22개 행정동 합계다. 2015년 이후 매년 줄어 10년 동안 6.1% 감소했다.", tier: "T2", src: MS.hadm.src,
      opt: { grid: { left: 8, right: 16, top: 8, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: yy }, yAxis: { type: "value", scale: true, axisLabel: { formatter: (v) => v / 1000 + "k" } }, series: [{ type: "line", data: yy.map((y) => MS.hadm.city_yearly[y]), color: C.green, areaStyle: { opacity: .12 }, lineStyle: { width: 2.5 } }] } });
    const rows = MS.hadm.rows.filter((r) => r.pop);
    const by65 = [...rows].sort((a, b) => b.pct_65 - a.pct_65);
    add({ id: "hadm65", g: "people", t: "행정동별 65세 이상 비율", take: `황남동이 ${pct(by65[0].pct_65)}로 가장 높다. 부지 주변 원도심 4개 동이 모두 상위에 있다. 황성동은 ${pct(rows.find((r) => r.hadm === "황성동")?.pct_65)}다.`, tier: "T2", src: MS.hadm.src, lead: "진한 색은 부지가 속한 원도심 4개 동(황오·성건·황남·월성동)이다.",
      opt: hbar(by65.map((r) => r.hadm), by65.map((r) => r.pct_65), { unit: "%", top: 22, fmtV: (v) => pct(v), colors: by65.map((r) => (["황오동", "성건동", "황남동", "월성동"].includes(r.hadm) ? C.red : C.orange2)) }), map: "pop_65" });
    add({ id: "hadmchg", g: "people", t: "행정동별 10년 인구 변화 2015→2025", take: "용강동만 32.8% 늘었고 원도심 4개 동은 22~45% 줄었다. 황오동은 2025년에 합쳐진 중부동을 포함해 계산하면 32.7% 감소다.", tier: "T2", src: MS.hadm.src, lead: "2025년에 폐지된 중부동은 2011~2024년 인구를 황오동에 더해 계산했다. 더하지 않으면 황오동이 20.1% 증가한 것처럼 보이는데, 이는 행정구역 통합 때문이지 실제 증가가 아니다.",
      opt: (() => { const s = [...rows].sort((a, b) => a.chg_10y_pct - b.chg_10y_pct); return hbar(s.map((r) => r.hadm), s.map((r) => r.chg_10y_pct), { top: 22, fmtV: (v) => (v > 0 ? "+" : "") + pct(v), colors: s.map((r) => (r.chg_10y_pct > 0 ? C.green : ["황오동", "성건동", "황남동", "월성동"].includes(r.hadm) ? C.red : C.orange2)) }); })(), map: "pop_chg" });
    const FRK = [["fr_worker", "외국인근로자"], ["fr_marriage", "결혼이민자"], ["fr_student", "유학생"], ["fr_diaspora", "외국국적동포"], ["fr_other", "기타외국인"], ["fr_naturalized", "귀화자"], ["fr_children", "자녀"]];
    const frv = FRK.map(([k]) => rows.reduce((s, r) => s + (+r[k] || 0), 0)); const frt = frv.reduce((a, b) => a + b, 0);
    add({ id: "foreign", g: "people", t: `외국인주민 ${fmt(frt)}명 — 유형별`, take: "성건동 7,170명(주민의 37.5%, 외국국적동포와 유학생이 많음), 외동읍 6,100명(근로자가 많음). 원도심 4개 동 중에서는 성건동만 많다.", tier: "T2", src: "행정안전부 지방자치단체 외국인주민 현황 2024.11 (KOSIS DT_110025_A033_A, 읍면동)",
      lead: "행정안전부 외국인주민 현황(2024.11)의 읍면동 합계다. 외국인근로자·결혼이민자·유학생·외국국적동포·기타에 귀화자와 자녀를 더한 값이다.",
      opt: hbar(FRK.map((k) => k[1]), frv, { unit: "명", top: 7, color: "#980043" }), map: "fr_pct" });
    if (NAT) { const nr = Object.entries(NAT.nationality).filter(([k]) => k !== "계").sort((a, b) => b[1] - a[1]).slice(0, 12);
      add({ id: "nation", g: "people", t: `국적별 등록외국인 ${fmt(NAT.nationality["계"])}명`, take: "베트남 3,437명, 중국 1,393명, 우즈베키스탄 1,148명, 카자흐스탄 1,129명 순이다. 시 단위로만 공표된다.", tier: "T2", src: `법무부 등록외국인 통계 ${NAT.prd} (KOSIS DT_1B040A9C)`, lead: "상위 12개국이다. 읍면동별 국적 통계는 공개되지 않는다. 행정안전부의 외국인주민 22,467명과 법무부의 등록외국인 15,621명은 집계 기준(귀화자·자녀 포함 여부)이 달라 합칠 수 없다.",
        opt: hbar(nr.map((r) => r[0].replace("(연방)", "")), nr.map((r) => r[1]), { unit: "명", top: 12, color: C.purple }) }); }
  }
  if (Y) {
    const dong = Y.dong.slice(0, 12); const core = ["황오동", "성건동", "황남동", "월성동"];
    add({ id: "ydong", g: "people", t: "20–34세 청년이 사는 곳 — 행정동별", take: `경주시 20–34세는 ${fmt(Y.city_y2034)}명(인구의 ${Y.city_pct}%)이다. 황성·동천·용강동과 현곡면에 45%가 산다. 원도심 4개 동에는 4,255명이 살고, 그중 59%가 대학이 있는 성건동이다.`, size: "m", tier: "T2", src: Y.dong_src, lead: "행정동별 20–34세 주민 수(막대)와 비율(숫자)이다. 진한 색은 부지가 속한 원도심 4개 동이다.",
      note: "황남동의 청년 비율은 7.0%로 시 평균의 절반이다. 관광객이 가장 많이 다니는 동에 청년 거주는 가장 적다.",
      opt: { ...hbar(dong.map((x) => x.hadm), dong.map((x) => x.n), { top: 12 }), series: [{ type: "bar", data: dong.map((x) => ({ value: x.n, itemStyle: { color: core.includes(x.hadm) ? "#6e016b" : "#9ebcda" } })), barCategoryGap: "28%", label: { show: true, position: "right", fontSize: 11, color: C.ink2, formatter: (p) => `${fmt(p.value)} · ${dong[p.dataIndex].pct}%` } }] }, map: "pop_y2034" });
    const a = Object.fromEntries(Y.age_emp), r = Object.fromEntries(Y.age_rate);
    add({ id: "yemp", g: "work", t: "경주시 취업자 145.1천 명 — 산업별·직업별 (전 연령)", take: `15–29세 취업자는 ${a["15 - 29세"]}천 명, 고용률 ${r["15 - 29세"]}%다(30–49세는 ${r["30 - 49세"]}%). 청년만 따로 낸 산업별 통계는 시군구 단위로 공표되지 않는다.`, size: "m", tier: "T2", src: Y.emp_src,
      lead: "지역별고용조사 2026년 상반기 값이다. 왼쪽은 산업 6개 분류, 오른쪽은 직업 6개 분류(천 명)다. 청년의 산업별 분포는 통계청 마이크로데이터(MDIS)를 신청해야 알 수 있다.",
      note: "농림어업 취업자 17.5천 명은 65세 이상 취업자가 30.9천 명인 구조로 볼 때 대부분 고령층으로 보이며, 청년은 제조업(외동·건천 공단)과 숙박음식업(관광)에 더 많을 것으로 추정된다. 이 부분은 추정이다.",
      opt: (() => { const ind = Y.industry.map(([k, v]) => [k.replace(/\s*\(.*?\)\s*/g, "").replace("사업·개인·공공서비스 및 기타", "사업·개인·공공서비스"), v]); const occ = Y.occupation.map(([k, v]) => [k.replace(" 및 관련종사자", "").replace(" 종사자", "").replace("기능·기계조작·조립", "기능·기계조작"), v]);
        return { grid: [{ left: 8, right: "56%", top: 26, bottom: 4, containLabel: true }, { left: "56%", right: 40, top: 26, bottom: 4, containLabel: true }], title: [{ text: "산업 (천 명)", left: 0, top: 0, textStyle: { fontSize: 11.5, color: C.ink3, fontWeight: 500 } }, { text: "직업 (천 명)", left: "54%", top: 0, textStyle: { fontSize: 11.5, color: C.ink3, fontWeight: 500 } }], tooltip: { trigger: "axis", valueFormatter: (v) => v + "천 명" },
          xAxis: [{ type: "value", show: false, gridIndex: 0 }, { type: "value", show: false, gridIndex: 1 }], yAxis: [{ type: "category", inverse: true, gridIndex: 0, data: ind.map((x) => x[0]), axisLabel: { fontSize: 11, color: C.ink } }, { type: "category", inverse: true, gridIndex: 1, data: occ.map((x) => x[0]), axisLabel: { fontSize: 11, color: C.ink } }],
          series: [{ type: "bar", xAxisIndex: 0, yAxisIndex: 0, data: ind.map((x) => x[1]), color: C.green, label: { show: true, position: "right", fontSize: 11 }, barCategoryGap: "30%" }, { type: "bar", xAxisIndex: 1, yAxisIndex: 1, data: occ.map((x) => x[1]), color: C.gray, label: { show: true, position: "right", fontSize: 11 }, barCategoryGap: "30%" }] }; })() });
    const bands = ["20-24세", "25-29세", "30-34세", "35-39세"]; const col = { "20-24세": "#980043", "25-29세": "#dd1c77", "30-34세": "#df65b0", "35-39세": "#9ebcda" };
    add({ id: "ymig", g: "people", t: "연령대별 순이동(전입−전출) 2020–2025", take: `20–34세는 매년 전출이 전입보다 많다(${Y.net["20-34세"].map(fmt).join(" / ")}명). 20–24세가 가장 많이 빠져나간다. 2025년 전체가 +860명이 된 것은 30대 이상이 들어왔기 때문이다.`, size: "m", tier: "T2", src: Y.mig_src, lead: "해마다 경주로 들어온 사람 수에서 나간 사람 수를 뺀 값이다. 선은 연령대별, 회색 막대는 전체다.",
      opt: { grid: { left: 8, right: 12, top: 30, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => sgn(v) + "명" }, legend: { top: 0, left: 0 }, xAxis: { type: "category", data: Y.mig_years }, yAxis: { type: "value" },
        series: [...bands.map((b) => ({ name: b, type: "line", data: Y.net[b], lineStyle: { width: 2, color: col[b] }, itemStyle: { color: col[b] } })), { name: "전체", type: "bar", data: Y.net["계"], itemStyle: { color: "rgba(120,130,125,.25)" }, barWidth: "40%" }] } });
  }
  if (MS?.decline) {
    const d = MS.decline.rows.filter((r) => r.old_pct != null).sort((a, b) => b.old_pct - a.old_pct);
    add({ id: "decline", g: "people", t: "쇠퇴 진단 2022 — 행정동별 노후 건물 비율", take: `22개 행정동 중 ${MS.decline.rows.filter((r) => r.met === "충족").length}곳이 쇠퇴 기준 3개 중 2개 이상에 해당한다. 황남동은 노후 건물 비율이 82.0%다.`, tier: "T1", src: MS.decline.src, lead: "도시재생 전략계획(2022)의 3개 지표(인구 감소, 사업체 감소, 20년 이상 건물 비율)다. 막대는 노후 건물 비율이고 빨강은 기준을 충족한 동이다.",
      opt: hbar(d.map((r) => r.hadm), d.map((r) => r.old_pct), { top: 22, fmtV: (v) => pct(v), colors: d.map((r) => (r.met === "충족" ? C.red : C.gray2)) }), map: "decline" });
  }
  if (MS?.schools) add({ id: "schools", g: "people", t: `학교 ${MS.schools.rows.reduce((s, r) => s + r[1], 0)}곳 — 유형별`, take: `운영 중인 학교·유치원 수다. 폐교는 ${MS.schools.closed}곳이다.`, tier: "T2", src: MS.schools.src, opt: hbar(MS.schools.rows.map((r) => r[0]), MS.schools.rows.map((r) => r[1]), { unit: "곳", top: 8, color: C.blue }), map: "schools" });
  if (MS?.religion) add({ id: "religion", g: "people", t: `종교시설 ${fmt(MS.religion.n)}곳 — 종교별`, take: `${MS.religion.rows.slice(0, 3).map((r) => `${r[0]} ${r[1]}곳`).join(", ")}. 이슬람 시설은 시의 현황 자료에 항목이 없어 경주이슬람센터 1곳을 따로 추가했다.`, tier: "T2", src: MS.religion.src, lead: "경주시 종교시설현황(2025.02) 파일이다. 외국인주민 22,467명 중 이슬람권 국적(우즈베키스탄·카자흐스탄·인도네시아·방글라데시·파키스탄 등)이 3,000명 이상이지만, 이 자료에는 이슬람 시설 항목이 없다. 경주이슬람센터(성건동 원화로281번길 22)는 수동으로 추가했다(시설 존재 T4, 좌표 지오코딩).",
    opt: hbar(MS.religion.rows.map((r) => r[0]), MS.religion.rows.map((r) => r[1]), { unit: "곳", top: 8, color: C.purple2 }), map: "religion" });

  // ======================= 일과 상권
  add({ id: "business", g: "work", t: "사업체 수와 종사자 수 2009–2013", take: "사업체는 12%, 종사자는 17% 늘었다. 종사자 기준 2차산업 비중 41.8%는 경북 평균 38.0%보다 높다.", tier: "T1", src: R.business.src,
    opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) }, xAxis: { type: "category", data: R.business.years }, yAxis: [{ type: "value", min: 18000, axisLabel: { formatter: (v) => v / 1000 + "k" } }, { type: "value", min: 90000, axisLabel: { formatter: (v) => v / 1000 + "k" }, splitLine: { show: false } }],
      series: [{ name: "사업체", type: "bar", data: R.business.firms, color: C.green3 }, { name: "종사자(우축)", type: "line", yAxisIndex: 1, data: R.business.workers, color: C.ink, lineStyle: { width: 2.5 } }] } });
  { const ind = R.industry_2013;
    add({ id: "industry13", g: "work", t: "산업 구성 2013 — 사업체 수와 종사자 수", take: "사업체 수로는 3차산업이 84%지만 종사자 수로는 2차산업이 42%다. 경주는 관광 도시이면서 제조업 고용 비중이 높은 도시다.", tier: "T1", src: ind.src,
      opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: ["경주 사업체", "경주 종사자", "경북 종사자"] }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } },
        series: ["1차", "2차", "3차"].map((k, i) => ({ name: k + "산업", type: "bar", stack: "s", data: [ind.firms_pct[k], ind.workers_pct[k], ind.gb_workers_pct[k]], color: [C.green3, C.orange, C.blue2][i], label: { show: i > 0, position: "inside", fontSize: 10.5, color: "#fff", formatter: (d) => d.value.toFixed(0) } })) } }); }
  if (MS?.stores) add({ id: "stores", g: "work", t: `상가 업소 ${fmt(MS.stores.n)}개 — 업종 대분류`, take: `${MS.stores.rows.slice(0, 3).map((r) => `${r[0]} ${fmt(r[1])}개`).join(", ")}. 영업 중인 업소만 있고 폐업한 업소는 포함되지 않는다.`, tier: "T2", src: MS.stores.src, lead: "소상공인시장진흥공단 상가업소 자료(2026-03, 원도심 일대)의 대분류별 업소 수다.",
    opt: hbar(MS.stores.rows.map((r) => r[0]), MS.stores.rows.map((r) => r[1]), { unit: "개", top: 10, color: C.orange }), map: "stores" });
  add({ id: "footfall", g: "work", t: "유동인구 8개 구역 — 1ha당 하루 평균", take: "성동시장 주변 200m는 1ha당 하루 1,175명, 폐역 구역은 79명이다. 200m 거리에서 15배 차이가 난다.", size: "m", tier: "T2", src: X.sources.footfall, lead: "통신사 기반 추정 유동인구(2025.06~2026.06 하루 평균)를 8개 구역에서 같은 방법으로 뽑아 구역 넓이(ha)로 나눴다. 빨강이 폐역 구역이다.",
    note: "행복황촌(B)도 폐역 구역과 비슷하게 적다(80명/ha). 부지는 비어 있을 뿐 아니라 사람이 지나가지 않는 상태다.",
    opt: hbar(FF.map((k) => X.footfall[k].short), FF.map((k) => X.footfall[k].per_ha), { unit: "/ha", top: 8, colors: FF.map((k) => AC[k]) }), map: "footfall_areas" });
  add({ id: "ffhour", g: "work", t: "시간대별 유동인구 비율 — 시청 주변만 저녁 비중이 높다", take: "모든 구역에서 14–18시가 가장 많다. 시청 주변 500m(F)만 18–23시 비중이 27%로 저녁까지 사람이 남는다.", size: "m", tier: "T2", src: X.sources.footfall, lead: "하루를 6개 시간대로 나눠 각 시간대에 전체 유동인구의 몇 %가 다니는지 보여준다. 구역 사이의 차이는 시간대 분포보다 절대 인원에서 크다.",
    note: "시청 주변 500m는 거주 9,145명·직장 8,374명으로 8개 구역 중 유일하게 거주와 직장이 비슷하고, 60세 이상 비율이 32%로 가장 낮다. 전략계획(2022)은 “시청 주변 상권은 시청사 이전으로 급속하게 형성됐다”고 적었다.",
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: ["05–09", "09–12", "12–14", "14–18", "18–23", "23–05"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" } },
      series: ["A_hwango_grid32", "D_zone", "F_cityhall_r500", "G_seongdong_market_r200", "H_hwangridan_r300"].map((k) => ({ name: X.footfall[k].short, type: "line", data: X.footfall[k].hourly_pct, color: AC[k], lineStyle: { width: k === "F_cityhall_r500" ? 3 : 1.8 } })) } });
  add({ id: "bizprint", g: "work", t: "생활 업종과 관광 업종 — 구역별 업소 수", take: "폐역 주변(C)에서 13개월 사이 펜션이 32곳에서 45곳으로 늘었다. 황리단길(H)은 카페가 51곳에서 40곳으로 줄었다. 생활 업종 수는 거의 변하지 않았다.", tier: "T2", src: X.sources.biz, lead: "슈퍼·미용실·정육점·약국·백반집 같은 주민 이용 업종과 카페·여관·호텔·펜션 같은 관광객 이용 업종의 수를 구역별로 셌다. 대표 11개 업종만 센 것이라 상권 전체는 아니다.",
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: FF.map((k) => X.footfall[k].short), axisLabel: { fontSize: 10.5 } }, yAxis: { type: "value" },
      series: [{ name: "생활", type: "bar", stack: "s", data: FF.map((k) => +X.biz_area[k].life_stores_2606), color: C.green }, { name: "관광·체류", type: "bar", stack: "s", data: FF.map((k) => +X.biz_area[k].tour_stores_2606), color: C.orange }] } });
  { const yrs7 = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]; const kp = X.hwango_kpi["주요 상권 유동인구(명, 소상공인365 통신사 추정)"] || {}; const o = X.startup_closure["황오동 사업대상지|창업 건수"] || {}; const c_ = X.startup_closure["황오동 사업대상지|폐업 건수"] || {};
    add({ id: "hwkpi", g: "work", t: "황오동 원도심 2018–2024 — 유동인구, 창업, 폐업", take: "하루 유동인구는 2020년 26,536명에서 2024년 22,646명으로 15% 줄었다. 같은 기간 창업과 폐업 건수는 모두 늘었다.", tier: "T2", src: X.sources.hwango,
      opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: yrs7 }, yAxis: [{ type: "value" }, { type: "value", scale: true, axisLabel: { formatter: (v) => v / 1000 + "k" }, splitLine: { show: false } }],
        series: [{ name: "창업", type: "bar", data: yrs7.map((y) => o[y]), color: C.green2 }, { name: "폐업", type: "bar", data: yrs7.map((y) => c_[y]), color: C.red }, { name: "유동인구(우축)", type: "line", yAxisIndex: 1, data: yrs7.map((y) => kp[y] ?? null), color: C.ink, lineStyle: { width: 2.5 }, connectNulls: true }] } }); }
  { const ly = Object.keys(X.landprice_avg);
    add({ id: "landprice", g: "work", t: "공시지가 — 2022년까지 오르고 이후 내렸다", take: "원도심 29필지 평균은 2018년 대비 2022년 +18.7%였다가 2025년 +10.8%로 내려왔다. 행복황촌 44곳은 2023년 −5.6%였다.", tier: "T2", src: X.sources.hwango,
      opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => (v == null ? "–" : fmt(v) + "원") }, xAxis: { type: "category", data: ly }, yAxis: [{ type: "value", scale: true, axisLabel: { formatter: (v) => (v / 1e6).toFixed(1) + "M" } }, { type: "value", scale: true, axisLabel: { formatter: (v) => (v / 1e4).toFixed(0) + "만" }, splitLine: { show: false } }],
        series: [{ name: "원도심 29필지", type: "line", data: ly.map((y) => X.landprice_avg[y]), color: C.green, lineStyle: { width: 2.5 } }, { name: "행복황촌 44개소(우축)", type: "line", yAxisIndex: 1, data: ly.map((y) => X.landprice_hwangchon44[y] ?? null), color: C.purple, lineStyle: { type: "dashed" } }] }, map: "landprice_pts" }); }
  add({ id: "elec", g: "work", t: "용도별 전력 사용량 — 산업용 48% (2013)", take: "2013년 전력 사용량의 48%가 산업용이다.", tier: "T1", src: R.electricity.src,
    opt: { tooltip: { trigger: "item", formatter: (d) => `${d.name} ${fmt(d.value)} MWh · ${d.percent}%` }, series: [{ type: "pie", radius: ["50%", "78%"], data: [{ name: "산업용", value: R.electricity.industry.at(-1) }, { name: "서비스업", value: R.electricity.service.at(-1) }, { name: "가정용", value: R.electricity.home.at(-1) }, { name: "공공용", value: R.electricity.total.at(-1) - R.electricity.industry.at(-1) - R.electricity.service.at(-1) - R.electricity.home.at(-1) }], color: [C.orange, C.green, C.blue, C.gray2], label: { fontSize: 11.5, color: C.ink2, formatter: "{b} {d}%" }, itemStyle: { borderColor: "#fff", borderWidth: 2 } }] } });
  add({ id: "housing", g: "work", t: "주택보급률 114.8%, 단독주택 60% (2013)", take: "주택 수는 가구 수보다 많다. 원도심에 부족한 것은 주택 수가 아니라 청년이 살 만한 유형의 주택이다.", tier: "T1", src: R.housing.src,
    opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: R.housing.years }, yAxis: [{ type: "value", min: 90000, axisLabel: { formatter: (v) => v / 1000 + "k" } }, { type: "value", min: 100, max: 120, axisLabel: { formatter: (v) => v + "%" }, splitLine: { show: false } }],
      series: [{ name: "가구", type: "bar", data: R.housing.households, color: C.gray2 }, { name: "주택", type: "bar", data: R.housing.units, color: C.green3 }, { name: "보급률(우축)", type: "line", yAxisIndex: 1, data: R.housing.supply_rate, color: C.ink, lineStyle: { width: 2.5 } }] } });
  add({ id: "finance", g: "work", t: "일반회계 세입과 2025년 예산", take: "2006년 6,571억 원, 2013년 1조 309억 원, 2025년 예산 2조 2,500억 원이다. 이 부지 사업비 3,822억 원은 연간 예산의 17%에 해당한다.", tier: "T1", src: R.finance.src,
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "억" }, xAxis: { type: "category", data: [...R.finance.years, "2025(예산)"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => (v / 10000).toFixed(1) + "조" } },
      series: [{ type: "bar", data: [...R.finance.general_revenue.map((v) => Math.round(v / 100)), { value: R.finance.budget_2025_100M, itemStyle: { color: C.orange } }], color: C.green, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => (d.value / 10000).toFixed(2) + "조" } }] } });
  add({ id: "medical", g: "work", t: "의료기관 239곳, 병상 4,376개 (2013)", take: "2009년에서 2013년 사이 병상 수가 43% 늘었다. 시청이 이전해도 보건소는 동천동에 남기는 것으로 계획한다(입지 조건이 다르기 때문).", tier: "T1", src: R.medical.src,
    opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: R.medical.years }, yAxis: [{ type: "value", min: 200 }, { type: "value", min: 2500, splitLine: { show: false } }], series: [{ name: "의료기관", type: "bar", data: R.medical.hospitals, color: C.green3 }, { name: "병상(우축)", type: "line", yAxisIndex: 1, data: R.medical.beds, color: C.ink, lineStyle: { width: 2.5 } }] } });
  if (HW) {
    const B = HW.biz2024, P = HW.pop_hwango, SR = HW.survey_res, SV = HW.survey_vis, K = HW.kpi, T = HW.tenure, SS = HW.sales;
    const grp = ["숙박·체류", "카페·휴게음식", "음식점·제과", "생활소매·식품제조", "생활서비스·의료", "유흥·오락", "통신판매(무점포)"];
    add({ id: "hwbiz24", g: "work", t: "2024년 창업·폐업 — 축제 기간 임시 가게 27건을 뺀 실제 수", take: "보고서의 ‘창업 70건’ 중 27건은 폐역 부지 축제 기간에 며칠만 열었다 닫은 임시 가게다. 이를 빼면 창업 43건, 폐업 39건으로 2018년(48건)보다 적다.", size: "m", tier: "T2", src: B.src, lead: "위(초록)는 실제 창업, 아래(빨강)는 실제 폐업, 회색은 창업과 폐업 양쪽에 모두 들어 있는 임시 가게다.",
      note: `구 경주역 부지의 ${B.open.popup_by_site["구 경주역 부지(성동동 40)"]}건은 5·6·9·11월 축제 기간에 등록됐다. 업종별 실제 순증가는 숙박·체류만 +${(B.open.by_group["숙박·체류"] || 0) - (B.close.by_group["숙박·체류"] || 0)}이고, 생활소매·식품제조 ${(B.open.by_group["생활소매·식품제조"] || 0) - (B.close.by_group["생활소매·식품제조"] || 0)}, 음식점 ${(B.open.by_group["음식점·제과"] || 0) - (B.close.by_group["음식점·제과"] || 0)}이다.`,
      opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => Math.abs(v) + "건" }, xAxis: { type: "category", data: grp, axisLabel: { fontSize: 10.5, interval: 0, rotate: 24 } }, yAxis: { type: "value", axisLabel: { formatter: (v) => Math.abs(v) } },
        series: [{ name: "창업(실제)", type: "bar", stack: "a", data: grp.map((k) => B.open.by_group[k] || 0), color: C.green }, { name: "폐업(실제)", type: "bar", stack: "a", data: grp.map((k) => -(B.close.by_group[k] || 0)), color: C.red }, { name: "임시 가게", type: "bar", stack: "a", data: grp.map((k) => (B.open.by_group_all[k] || 0) - (B.open.by_group[k] || 0)), color: C.gray2 }] } });
    add({ id: "hwclose", g: "work", t: "2024년 실제 폐업 39건 — 영업 기간별", take: "30년 넘게 영업한 가게 4곳이 문을 닫았다. 1961년 계림여인숙, 1980년 대원슈퍼, 1982년 고도삼계탕, 1984년 이화순미용실이다.", tier: "T2", src: B.src,
      opt: hbar(Object.keys(B.closure_age_bins), Object.values(B.closure_age_bins), { unit: "건", top: 5, color: C.red }) });
    const yrs6 = HW.series.years; const idx = (a) => a.map((v) => +(v / a[0] * 100).toFixed(1));
    add({ id: "hwgrid", g: "work", t: "사업구역 격자 32칸 — 인구·가구·사업체·종사자·주택 변화 (2018=100)", take: "종사자 −23%, 인구 −14%, 사업체 −3%다. 종사자 감소가 가장 크다. 성동시장 칸의 사업체는 264개에서 160개로 줄었다.", size: "m", tier: "T2", src: HW.series.src, lead: "도시재생 사업구역을 100m×100m 격자 32칸으로 나눈 통계청 자료다. 2018년을 100으로 놓았고 선이 100 아래면 줄어든 것이다. 점선은 황오동 전체 인구다.",
      opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: yrs6 }, yAxis: { type: "value", scale: true, min: 70 },
        series: [...Object.entries({ pop: "인구", hh: "가구", biz: "사업체", emp: "종사자", house: "주택" }).map(([k, t], i) => ({ name: t, type: "line", data: idx(HW.series.site[k]), color: [C.green, C.green2, C.orange, C.blue, C.purple][i], lineStyle: { width: k === "emp" ? 3 : 1.8 } })), { name: "황오동 인구", type: "line", data: idx(HW.series.dong.pop), color: C.gray, lineStyle: { type: "dashed" } }] } });
    const bands = Object.keys(P.age);
    add({ id: "hwage", g: "people", t: "황오동 연령별 인구 2018년과 2025년 7월", take: `20대와 50대가 줄고 75세 이상만 늘었다. 20–39세는 ${(100 - P.n_20_39.at(-1) / P.n_20_39[0] * 100).toFixed(0)}% 줄었고 65세 이상 비율은 ${pct(P.share_65.at(-1))}다.`, size: "m", tier: "T2", src: P.src,
      opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: bands, axisLabel: { fontSize: 10, interval: 1, rotate: 40 } }, yAxis: { type: "value" }, series: [{ name: "2018", type: "bar", data: bands.map((b) => P.age[b]["2018"]), color: C.gray2 }, { name: "2025.07", type: "bar", data: bands.map((b) => P.age[b]["2025.07"]), color: C.green }] } });
    add({ id: "hwsales", g: "work", t: "대표 5개 업종 월매출 합계 2023.09–2025.04", take: "보고서의 ‘상권 매출 +15%’는 5개 대표 업종 합계이고, 그중 피부/비뇨기과의원 한 업종이 57%를 차지한다. 2024년 10월의 증가도 의원 매출 때문이다.", tier: "T2", src: SS.src, note: SS.note,
      opt: { grid: { left: 8, right: 16, top: 12, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "만 원" }, xAxis: { type: "category", data: SS.months, axisLabel: { fontSize: 10, formatter: (v) => (v.endsWith("-01") || v === "2023-09" ? v : v.slice(5)) } }, yAxis: { type: "value", scale: true, axisLabel: { formatter: (v) => (v / 10000).toFixed(1) + "억" } }, series: [{ type: "line", data: SS.total_manwon, color: C.orange, areaStyle: { opacity: .12 }, lineStyle: { width: 2.5 } }] } });
    add({ id: "hwtenure", g: "work", t: "영업 10년 이상 311곳 — 업종별", take: "방앗간·참기름집·정육점·여인숙·다방이 많다. 2018년 이후 폐업이 많은 업종은 한식 44건, 즉석판매 36건, 다방 17건이다.", tier: "T2", src: T.src, opt: hbar(Object.keys(T.over10y_by_upjong), Object.values(T.over10y_by_upjong), { unit: "곳", top: 12, color: C.green }) });
    const cmpk = ["대상지", "황오동", "경주시", "경상북도"]; const cmpv = { 대상지: { closures: K.closures }, ...K.compare };
    add({ id: "hwcmp", g: "work", t: "폐업 건수 지수 — 대상지·황오동·경주시·경북 (2018=100)", take: "경북 전체 폐업은 2020년부터 6년 연속 늘어 29% 증가했다. 대상지의 2024년 급증은 임시 가게 27건 때문이다.", tier: "T2", src: K.src,
      opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: K.years }, yAxis: { type: "value", scale: true }, series: cmpk.map((k, i) => ({ name: k, type: "line", data: idx(cmpv[k].closures), color: [C.red, C.orange, C.blue, C.gray][i], lineStyle: { width: k === "대상지" ? 3 : 1.8 } })) } });
    add({ id: "hwsurvey", g: "voice", t: "주민·상인 설문 2020–2024 — 인지도·만족도·소속감", take: "사업 인지도(막대)는 계속 올랐다. 전반 만족도는 비슷하고 보행환경 점수는 내려갔다.", size: "m", tier: "T2", src: SR.src, note: SR.note,
      opt: { grid: { left: 8, right: 44, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: SR.years }, yAxis: [{ type: "value", min: 0, max: 10 }, { type: "value", min: 0, max: 100, axisLabel: { formatter: (v) => v + "%" }, splitLine: { show: false } }],
        series: [{ name: "전반 만족도", type: "line", data: SR.overall_satis, color: C.green, lineStyle: { width: 2.5 } }, { name: "주거환경", type: "line", data: SR.housing_env, color: C.green2 }, { name: "보행환경", type: "line", data: SR.walk_env, color: C.red }, { name: "소속감", type: "line", data: SR.belonging["황오동"], color: C.purple }, { name: "공공기관 신뢰", type: "line", data: SR.trust["공공기관"], color: C.blue }, { name: "인지도(우축)", type: "bar", yAxisIndex: 1, data: SR.awareness, color: "rgba(31,94,66,.18)" }] } });
    const hubs = Object.keys(SR.hub_expect_2024);
    add({ id: "hwhub", g: "voice", t: "거점 시설 만족도 — 준공 후 매년 하락", take: "청년창업센터·작은도서관 만족도가 2022년 9.6점, 2023년 6.7점, 2024년 4.4점이다. 아직 준공되지 않은 시설 중에는 보행환경 사업만 기대 점수가 7점대다.", size: "m", tier: "T2", src: SR.src,
      opt: { grid: { left: 8, right: 16, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: [...Object.keys(SR.hub_satis), ...hubs], axisLabel: { fontSize: 10, interval: 0, rotate: 24 } }, yAxis: { type: "value", min: 0, max: 10 },
        series: [{ name: "2022", type: "bar", data: [...Object.values(SR.hub_satis).map((a) => a[2]), ...hubs.map(() => null)], color: C.gray2 }, { name: "2023", type: "bar", data: [...Object.values(SR.hub_satis).map((a) => a[3]), ...hubs.map(() => null)], color: C.gray }, { name: "2024", type: "bar", data: [...Object.values(SR.hub_satis).map((a) => a[4]), ...hubs.map(() => null)], color: C.red }, { name: "2024 기대(미준공)", type: "bar", data: [...Object.keys(SR.hub_satis).map(() => null), ...hubs.map((h) => SR.hub_expect_2024[h])], color: C.green }] } });
    add({ id: "hwvisit", g: "voice", t: "방문객이 직전에 들른 곳 2020–2024", take: "황리단길이 54%에서 12%로, 성동시장이 9%에서 48%로 바뀌었다. 표본과 조사 장소가 해마다 달라(2024년은 축제 현장) 추세가 아니라 조사 조건의 변화로 봐야 한다.", tier: "T2", src: SV.src, note: SV.note,
      opt: { grid: { left: 8, right: 16, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: SV.years }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } }, series: Object.entries(SV.prev_place).map(([k, a], i) => ({ name: k, type: "bar", stack: "p", data: a.map((v) => v ?? 0), color: [C.orange, C.green2, C.blue2, C.purple, C.blue, C.gray, C.gray2][i] })) } });
    add({ id: "hwmotive", g: "voice", t: "방문 계기와 지출 — 2024년은 축제 방문이 50%", take: `2024년 방문객의 79%가 3시간 미만 머물렀고 1만 원 이상 쓴 비율은 2.7%였다. 경주시민 비율이 ${pct(SV.resident_gj_2024, 1)}라 관광객 조사라기보다 주민 행사 조사에 가깝다.`, tier: "T2", src: SV.src,
      opt: { grid: { left: 8, right: 16, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: SV.years }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } }, series: [...Object.entries(SV.motive).map(([k, a], i) => ({ name: k, type: "bar", stack: "m", data: a.map((v) => v ?? 0), color: [C.green, C.blue, C.purple, C.green2, C.orange, C.gray2][i] })), { name: "1만 원 이상 지출", type: "line", data: SV.spend_over_10, color: C.red, lineStyle: { width: 2.5 } }] } });
  }

  // ======================= 이동
  { const f = R.mode_forecast; const M6 = ["도보/자전거", "승용차", "택시", "버스", "철도", "기타"];
    add({ id: "modeshare", g: "move", t: "통행 수단 비율 — 2007년 조사와 계획의 예측", take: "2007년 조사에서는 버스 36.2%, 승용차 26.5%였다. 같은 기본계획의 2015~2030년 예측표에서는 승용차 40%, 버스 15.6%로 바뀐다.", size: "m", tier: "T1", src: `${R.mode_share_2007.src} / ${f.src}`,
      lead: "회색은 2007년 조사, 연초록은 2015년 예측, 초록은 2030년 예측(%)이다. 예측표는 도보와 자전거를 합쳐 적었다.", note: "모빌리티 허브는 이 예측(승용차 40%)을 전제로 하지 않고, 원도심을 지나는 트램·셔틀로 대중교통 비율을 유지하려는 계획이다.",
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: ["도보(·자전거)", "승용차", "택시", "버스", "철도", "기타"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" }, max: 45 },
        series: [{ name: "2007 조사", type: "bar", data: R.mode_share_2007.pct, color: C.gray }, { name: "2015 예측", type: "bar", data: M6.map((m) => f.pct[m][0]), color: C.green2 }, { name: "2030 예측", type: "bar", data: M6.map((m) => f.pct[m][3]), color: C.green, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => d.value } }] } });
    add({ id: "modepurpose", g: "move", t: "통행 목적별 수단 비율 (2007)", take: "등교 통행의 52%는 버스, 업무 통행의 50%는 승용차였다. 시청 직원과 민원인 8,000~9,000명의 출퇴근이 어느 수단으로 이루어지느냐가 허브 이용량을 좌우한다.", tier: "T1", src: R.mode_share_2007.src,
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: Object.keys(R.mode_share_2007.by_purpose) }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } }, series: R.mode_share_2007.modes.map((m, i) => ({ name: m, type: "bar", stack: "s", data: Object.values(R.mode_share_2007.by_purpose).map((v) => v[i]), color: [C.green3, C.orange, C.orange2, C.green, C.purple, C.gray2][i] })) } }); }
  add({ id: "cars", g: "move", t: "인구 1,000명당 차량 등록 대수 — 403대 → 449대", take: "2009년에서 2013년 사이 매년 2.8%씩 늘었다. 인구가 줄어도 차량과 주차 수요는 늘었다.", tier: "T1", src: R.cars.src,
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: R.cars.years }, yAxis: { type: "value", min: 250, max: 470 }, series: [{ name: "전체", type: "line", data: R.cars.per_1000_total, color: C.ink, lineStyle: { width: 2.5 }, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => d.value.toFixed(0) } }, { name: "승용차", type: "line", data: R.cars.per_1000_car, color: C.orange }] } });
  add({ id: "rail", g: "move", t: "철도 승차 인원 — 신경주역(KTX)과 경주역(일반열차)", take: "경주역은 2021년 12월에 문을 닫았다. 원도심에서 철도를 탈 수 있는 곳이 없어졌고, KTX는 건천읍의 신경주역에 있다.", tier: "T1", src: R.rail.src,
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: R.rail.years }, yAxis: { type: "value", axisLabel: { formatter: (v) => v / 1e6 + "M" } }, series: [{ name: "신경주역", type: "bar", data: R.rail.ktx_board, color: C.green }, { name: "구 경주역", type: "bar", data: R.rail.gj_board, color: C.orange }] } });
  add({ id: "parking", g: "move", t: "주차장 51,880면 — 종류별", take: "99%가 건물에 딸린 부설주차장이고 공영·노상주차장은 1%다. 2015년 설문에서 교통 분야 불만 1위(38.8%)가 주차였다.", tier: "T1", src: R.parking.src,
    opt: hbar(R.parking.rows.filter((r) => r.kind !== "합계").map((r) => `${r.kind} (${fmt(r.sites)}개소)`), R.parking.rows.filter((r) => r.kind !== "합계").map((r) => r.spaces), { unit: "면", color: C.gray }) });
  add({ id: "bus", g: "move", t: "시내버스 연간 이용 인원 — 5년간 변화 없음", take: "연 1,500만 명 수준에서 늘지 않았다. 버스 등록 대수는 163대에서 169대로 늘었다. 전세버스(관광용)는 별도 선이다.", tier: "T1", src: R.bus.src,
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: R.bus.years }, yAxis: { type: "value", min: 0, axisLabel: { formatter: (v) => v / 1e6 + "M" } }, series: [{ name: "시내버스", type: "line", data: R.bus.city_pax, color: C.green, areaStyle: { opacity: .12 }, lineStyle: { width: 2.5 } }, { name: "전세버스", type: "line", data: R.bus.charter_pax, color: C.orange }] } });
  { const vcs = R.road_vc.rows.filter((r) => /국도7|국도4|국도35|국도20|지방도/.test(r.road) || r.vc >= 0.6).sort((a, b) => b.vc - a.vc).slice(0, 10);
    add({ id: "roadvc", g: "move", t: "주요 도로의 교통량/용량 비율 상위 10구간", take: "1.0이면 도로 용량에 도달한 것이다. 국도 구간이 상위에 있다. 경부축 시외버스를 원도심 안으로 끌어들이면 안 되는 근거다.", tier: "T1", src: R.road_vc.src, opt: hbar(vcs.map((r) => `${r.road} ${r.seg}`), vcs.map((r) => r.vc), { color: C.orange, top: 10, max: 1, fmtV: (v) => v.toFixed(2) }) }); }
  if (TH) { const hrs = [...Array(24).keys()];
    add({ id: "speedhour", g: "move", t: "시간대별 도로 평균 속도 (교통정보 이력 표본)", take: `평일 ${TH.days.wd.length}일, 주말 ${TH.days.we.length}일 표본이다. 평일 아침과 저녁 출퇴근 시간에 평균 속도가 낮아지고 정체 구간 비율이 올라간다.`, size: "m", tier: "T2", src: `국가교통정보센터 ITS 5분 이력 표본(매월 둘째 화·토) × 표준노드링크 · 도로 구간 ${fmt(TH.links)}개 · 정체 기준은 도로 등급별(도시부 15 / 도시고속 30 / 고속 40 km/h 미만)`,
      lead: "선은 시간대별 평균 속도(km/h), 점선은 정체 기준 아래로 떨어진 구간의 비율(%)이다. 표본일을 정해 받은 자료라 명절이나 행사일은 들어 있지 않다.",
      opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: hrs.map((h) => h + "시"), axisLabel: { interval: 2 } }, yAxis: [{ type: "value", name: "km/h", scale: true }, { type: "value", name: "정체%", max: 100, splitLine: { show: false } }],
        series: [{ name: "평일 평균속도", type: "line", data: TH.hourly.wd.map((r) => r.speed_avg), color: C.green, lineStyle: { width: 2.5 } }, { name: "주말 평균속도", type: "line", data: TH.hourly.we.map((r) => r.speed_avg), color: C.purple, lineStyle: { width: 2 } }, { name: "평일 정체 %", type: "line", yAxisIndex: 1, data: TH.hourly.wd.map((r) => r.congested_pct), color: C.red, lineStyle: { type: "dashed" } }] }, map: "traffic_hist" }); }
  if (TC) add({ id: "congtop", g: "move", t: "정체 판정 비율이 높은 도로 구간 (실시간 자료)", take: `${TC[0]?.road} 등이다. 5분 간격 자료 중 정체로 판정된 비율이며, 관측 횟수가 적은 구간은 뺐다.`, tier: "T2", src: "국가교통정보센터 trafficInfo 5분 스냅샷 누적 (2026-09-17~) · 관측 6회 이상",
    opt: hbar(TC.slice(0, 10).map((t) => `${t.road || "(무명)"} · ${t.speed_avg}km/h`), TC.slice(0, 10).map((t) => t.congested_pct), { unit: "%", top: 10, color: C.red, max: 100 }), map: "traffic_hist" });


  // ======================= 경주에 오는 길 (관광객 입경 수단은 4개 문서에 통계가 없다 — 있는 것만)
  if (AT) {
    add({ id: "arrive_none", g: "move", t: "관광객은 어떤 교통수단으로 경주에 오나 — 4개 문서에는 직접 통계가 없다", size: "l", tier: "T2", src: "미래구상 2025 · 전략계획 2022 · 2030 기본계획 · 2030 경관계획 전수 검색(‘교통수단·이용교통·자가용·KTX·고속버스·관광버스·유입경로’) 2026-09-21",
      take: "네 문서 어디에도 ‘경주 방문 관광객의 입경 교통수단 비율’은 없다. 대신 관문의 위치(경관계획), 진입축의 차량 통행량(기본계획 2015·도로공사 2025), 고속버스 운행횟수(KOBUS 2015), 철도 승차(2013), 시민 설문(2025)이 있고, 전국 평균은 국민여행조사(KOSIS)로 볼 수 있다. 아래 카드가 그 전부다.",
      lead: "무엇이 있고 무엇이 없는지를 먼저 적는다. 경주만의 입경 수단 비율을 얻으려면 경주시 관광객 실태조사(경북문화관광공사) 원문이나 국민여행조사의 시도별 방문지 교차표(보고서 PDF, API 미제공)가 필요하다 — gaps.md에 기록.",
      html: `<table class="t"><tr><th>질문</th><th>있는 자료</th><th>없는 자료</th></tr>
        <tr><td>관광객이 <b>무엇을 타고</b> 오나</td><td>전국 평균: 국민여행조사 2025 관광여행 지역간 이동수단 — 자가용 84.5%(T2, KOSIS) · 방문자 거주지 분포(관광데이터랩, 다른 카드)</td><td>경주 방문자 한정 입경 수단 비율 · 국민여행조사 시도별 교차표(API 미제공)</td></tr>
        <tr><td><b>어디로</b> 들어오나</td><td>관문 10곳 위치(경관계획 관문적 경관거점 T1 · IC 5·역 2·터미널 2·폐역) · 진입축 통행량 2015(기본계획 p.207 T1) · 고속도로 AADT 2021–25(도로공사 T2) · 지도 ‘진입 관문’ 레이어</td><td>IC 진출입 교통량(영업소별) · 신경주역 연도별 승하차(2014 이후) · 터미널 이용객 수</td></tr>
        <tr><td>경주 <b>안에서</b> 무엇을 타나</td><td>수단분담 2007(기본계획, 버스 36%·승용차 27%) · 권역별 수단통행 2019(전략계획, 승용차 38~41%) · 행정동별 버스노선 수(전략계획) · 시내버스 이용 2009–13 · 차량 등록 · 주차장 · 시민 설문 2025(대중교통 2.7/5점)</td><td>2007 이후 경주시 자체 수단분담 조사 · 관광객의 시내 이동 수단(렌터카·관광버스·택시 비율)</td></tr></table>`, map: "gateways" });
    const nt = AT.national_travel?.data; const yrs = nt ? Object.keys(nt).sort() : [];
    if (yrs.length) { const y = yrs.at(-1); const all = nt[y]["전체"]; const modes = Object.entries(all).filter(([k, v]) => v != null).sort((a, b) => b[1] - a[1]).slice(0, 8);
      add({ id: "arrive_nat", g: "move", t: `관광여행 갈 때 주로 타는 것 — 전국 평균 ${y}, 자가용 ${all["자가용"]}%`, size: "m", tier: "T2", src: AT.src.national,
        take: `전국 관광여행(지역 간)의 1순위 이동수단은 자가용 ${all["자가용"]}%다. 20대는 자가용 ${nt[y]["20대"]["자가용"]}%, 버스 ${nt[y]["20대"]["고속/시외/시내버스"]}%, 철도 ${nt[y]["20대"]["철도"]}%로 대중교통 비중이 가장 높다. 경주 방문자만의 값이 아니라 전국 값이다.`,
        lead: "문화체육관광부 국민여행조사(KOSIS API)의 ‘관광여행 지역간 주요 이동수단(1순위)’. 왼쪽 막대는 전체, 오른쪽 선은 연령대별 자가용 비율이다. 경주는 KTX역이 원도심에서 9km 떨어져 있고 공항이 없어 자가용 비중이 전국보다 낮을 이유가 없다 — 다만 이것은 추정이다.",
        note: `${yrs.join("·")} 3개년. 시도별 방문지 교차표는 API로 제공되지 않아 경주(경북) 값은 알 수 없다.`,
        opt: { grid: [{ left: 8, right: "50%", top: 30, bottom: 4, containLabel: true }, { left: "56%", right: 16, top: 30, bottom: 4, containLabel: true }], title: [{ text: `${y} 전체 (%)`, left: 0, top: 0, textStyle: { fontSize: 11.5, color: C.ink3, fontWeight: 500 } }, { text: "연령대별 자가용 %", left: "56%", top: 0, textStyle: { fontSize: 11.5, color: C.ink3, fontWeight: 500 } }], tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) },
          xAxis: [{ type: "value", show: false, gridIndex: 0 }, { type: "category", gridIndex: 1, data: ["20대", "30대", "40대", "50대", "60대", "70세 이상"], axisLabel: { fontSize: 10.5 } }], yAxis: [{ type: "category", inverse: true, gridIndex: 0, data: modes.map((m) => m[0].replace("고속/시외/시내버스", "버스").replace("전세/관광버스", "관광버스")), axisLabel: { fontSize: 11, color: C.ink } }, { type: "value", gridIndex: 1, min: 60, max: 100, axisLabel: { formatter: (v) => v + "%" } }],
          series: [{ type: "bar", xAxisIndex: 0, yAxisIndex: 0, data: modes.map((m) => m[1]), color: C.orange, label: { show: true, position: "right", fontSize: 11, formatter: (d) => d.value + "%" }, barCategoryGap: "30%" }, ...yrs.map((yy, i) => ({ name: yy, type: "line", xAxisIndex: 1, yAxisIndex: 1, data: ["20대", "30대", "40대", "50대", "60대", "70세 이상"].map((g) => nt[yy][g]?.["자가용"] ?? null), color: [C.gray2, C.gray, C.ink][i], lineStyle: { width: yy === y ? 2.5 : 1.5 } }))], legend: { top: 0, right: 0, textStyle: { fontSize: 10.5 } } } }); }
    { const rows = R.road_vc.rows.filter((r) => /경부고속|국도7|국도4호|국도20|국도35|국도14/.test(r.road) && r.aadt >= 9000).sort((a, b) => b.aadt - a.aadt).slice(0, 12);
      add({ id: "arrive_axis", g: "move", t: "경주로 들어오는 도로 — 진입축별 하루 교통량 (2015)", size: "m", tier: "T1", src: R.road_vc.src,
        take: "경부고속도로 언양JCT~경주IC 45,807대/일, 국도7호 경주~울산 39,592, 외동~경주 37,589, 경주~포항 31,548. 남쪽(울산)과 서쪽(경부고속)에서 들어오는 차량이 가장 많고, 동쪽(감포) 국도4호는 7,612대다.",
        lead: "기본계획 교통량표(2015)에서 시 경계를 넘어 들어오는 축만 골랐다. 관광객과 통근·화물이 섞인 값이며 방향 구분은 없다. 지도 ‘진입 관문’ 레이어의 IC·역 팝업에 같은 수치를 붙였다.",
        note: "고속도로 본선은 2021→2025년에 경부 활천~경주 47,116→54,887대(+16%), 경주~건천 49,212→55,015대(+12%)로 늘었다(도로공사 AADT, 다음 카드). 통과 교통이 포함되므로 ‘경주 진입 차량 증가’로 읽지 않는다.",
        opt: hbar(rows.map((r) => `${r.road.replace("호선", "")} ${r.seg}`), rows.map((r) => r.aadt), { unit: "대/일", top: 12, colors: rows.map((r) => (/경부/.test(r.road) ? "#8d6e63" : /국도7/.test(r.road) ? C.orange : C.green2)) }), map: "gateways" }); }
    if (AT.aadt && Object.keys(AT.aadt).length) { const segs = Object.keys(AT.aadt); const yrs2 = AT.aadt[segs[0]].years;
      add({ id: "arrive_aadt", g: "move", t: "고속도로 연평균 일교통량 2021–2025 — 경부선 3구간 · 동해선 3구간", tier: "T2", src: AT.src.aadt,
        take: "경주를 지나는 경부선 구간은 5년간 12~16% 늘어 5.5만 대/일이고, 동해고속도로(울산~포항) 경주 구간은 2.3~2.5만 대/일로 정체다.",
        lead: "한국도로공사 구간별 AADT(대/일). 본선 통과량이며 경주IC·건천IC로 나가는 차량 수(영업소 진출입량)가 아니다 — 그 자료는 못 받았다.",
        opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 10.5 } }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "대" }, xAxis: { type: "category", data: yrs2 }, yAxis: { type: "value", axisLabel: { formatter: (v) => v / 1000 + "k" } },
          series: segs.map((sg, i) => ({ name: `${AT.aadt[sg].line} ${sg}`, type: "line", data: AT.aadt[sg].v, color: ["#5d4037", "#8d6e63", "#bcaaa4", "#1565c0", "#4589ff", "#8fb4e0"][i], lineStyle: { width: 2 } })) } }); }
    add({ id: "arrive_kobus", g: "move", t: "고속버스 — 하루 약 91회, 부산 40~41회 · 대구 36회 · 서울 17회 (2015)", tier: "T1", src: AT.src.kobus,
      take: "노서동 고속버스터미널의 노선은 5개다. 부산·대구가 전체의 84%를 차지하고 서울은 17회다. 시외버스(포항·울산·대구 등)는 운행횟수 표가 문서에 없다.",
      lead: "2030 기본계획 p.202 표(KOBUS). 시외버스터미널은 위치만 있고 운행 통계가 없다 — 미래구상 연구의 현장 관찰(p.68)은 ‘시외터미널 이용률이 고속터미널보다 단연 높다’고 적었다.",
      opt: hbar(AT.kobus_2015.map((r) => "경주 ↔ " + r[0]), AT.kobus_2015.map((r) => r[1]), { unit: "회/일", top: 5, color: C.orange }), map: "gateways" });
    add({ id: "arrive_citizen", g: "move", t: "시민이 다른 도시로 갈 때 — 버스터미널 30 · 기차역 22 · 자가용 19 (2025, n=49)", size: "m", tier: "T2", src: AT.src.citizen,
      take: "원도심 시민 49명(복수응답)은 외부로 갈 때 버스터미널을 가장 많이 꼽았다. 터미널의 불편은 시내 연결성 부족(12)·도로 혼잡(11)·고속·시외 기능 분리(9)순이다. 원도심 대중교통 평가는 5점 만점에 2.7점(청년 2.48·중장년 3.03)이다.",
      lead: "경주시 원도심 미래구상 기획연구(2025) 시민 설문. 왼쪽은 외부 이동수단(n=49), 오른쪽은 버스터미널 불편 사항(n=46). 시민 응답이지 관광객 응답이 아니다. 표본이 작아 비율이 아니라 응답 수로 표시했다.",
      note: "연구는 ‘가까운 도시(포항·울산)까지 이동 시간과 기차역(신경주역)까지 이동 시간이 모두 약 30분이라 기차는 장거리, 자가용은 단거리에 쓰인다’고 해석했다(p.68).",
      opt: { grid: [{ left: 8, right: "58%", top: 26, bottom: 4, containLabel: true }, { left: "48%", right: 40, top: 26, bottom: 4, containLabel: true }], title: [{ text: "외부 이동수단 (n=49)", left: 0, top: 0, textStyle: { fontSize: 11.5, color: C.ink3, fontWeight: 500 } }, { text: "버스터미널 불편 (n=46)", left: "48%", top: 0, textStyle: { fontSize: 11.5, color: C.ink3, fontWeight: 500 } }], tooltip: { trigger: "axis", valueFormatter: (v) => v + "명" },
        xAxis: [{ type: "value", show: false, gridIndex: 0 }, { type: "value", show: false, gridIndex: 1 }], yAxis: [{ type: "category", inverse: true, gridIndex: 0, data: AT.citizen_2025.out.map((r) => r[0]), axisLabel: { fontSize: 11.5, color: C.ink } }, { type: "category", inverse: true, gridIndex: 1, data: AT.citizen_2025.term_issue.map((r) => r[0]), axisLabel: { fontSize: 10.5, color: C.ink, width: 150, overflow: "truncate" } }],
        series: [{ type: "bar", xAxisIndex: 0, yAxisIndex: 0, data: AT.citizen_2025.out.map((r) => r[1]), color: C.purple, label: { show: true, position: "right", fontSize: 11 }, barCategoryGap: "30%" }, { type: "bar", xAxisIndex: 1, yAxisIndex: 1, data: AT.citizen_2025.term_issue.map((r) => r[1]), color: C.gray, label: { show: true, position: "right", fontSize: 11 }, barCategoryGap: "30%" }] } });
    { const rm = AT.region_mode_2019; const regs = ["부산울산권", "대구광역권", "수도권", "대전세종충청권", "광주광역권"];
      add({ id: "inside_region", g: "move", t: "권역별 통행 수단 비율 2019 — 경주가 속한 부산울산권은 승용차 38%, 도보 29%, 버스 17%", tier: "T1", src: AT.src.region_mode,
        take: "부산울산권·대구권 모두 승용차가 1위(38~41%)이고 철도는 5% 안팎이다. 수도권(철도 14%)과의 차이가 경주 대중교통 여건의 배경이다. 권역 통계라 경주시 값은 아니다.",
        lead: "전략계획 2022가 인용한 2019 국가교통조사 여객 O/D. 경주만 뽑은 수단분담은 2007년 조사(‘통행 수단 비율’ 카드)가 마지막이다.",
        opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 10.5 } }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: regs, axisLabel: { fontSize: 10.5 } }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } },
          series: rm.modes.map((m, i) => ({ name: m, type: "bar", stack: "s", data: regs.map((r) => rm.rows[r][i]), color: [C.green3, C.orange, C.green, C.purple, C.orange2, C.blue2, C.gray2][i], label: { show: i < 3, position: "inside", fontSize: 10, color: "#fff", formatter: (d) => d.value.toFixed(0) } })) } }); }
    { const br = Object.entries(AT.bus_routes_2022).sort((a, b) => b[1] - a[1]);
      add({ id: "inside_busroutes", g: "move", t: "행정동별 시내버스 운행 노선 수 — 황오동 76 · 중부동 75 · 황남동 74 · 성건동 69", tier: "T1", src: AT.src.bus_routes,
        take: "원도심 4개 동을 지나는 노선이 70개 안팎으로 압도적이고 감포읍 4, 문무대왕면 6, 내남·양남·서면 7이다. 노선은 원도심에 모이는데 원도심 시민의 대중교통 만족도는 2.7점이다 — 문제는 노선 수가 아니라 배차 간격(미래구상 p.66)이다.",
        lead: "경주시교통정보센터 자료를 전략계획(2022)이 표로 실은 것. 2025년 중부동이 황오동에 통합되기 전 값이다.",
        opt: hbar(br.map((r) => r[0]), br.map((r) => r[1]), { unit: "개", top: 23, colors: br.map((r) => (["황오동", "중부동", "황남동", "성건동"].includes(r[0]) ? C.red : C.blue2)) }), map: "busstops" }); }
  }
  // ======================= 관광·경관·예술
  add({ id: "tourists", g: "visit", t: "지정관광지 입장객 — 보문·양남·감포", take: `2013년 889만 명(외국인 19만 명)이다. 관광데이터랩의 2026년 8월 방문자(18일간 626만 명)는 집계 기준이 달라 합칠 수 없다.`, tier: "T1", src: R.tourists.src,
    opt: { grid: { left: 8, right: 40, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: R.tourists.years }, yAxis: [{ type: "value", axisLabel: { formatter: (v) => v / 1e6 + "M" } }, { type: "value", axisLabel: { formatter: (v) => v / 1e3 + "k" }, splitLine: { show: false } }], series: [{ name: "합계", type: "bar", data: R.tourists.total, color: C.green }, { name: "외국인(우축)", type: "line", yAxisIndex: 1, data: R.tourists.foreign, color: C.orange, lineStyle: { width: 2 } }] } });
  if (VIS) { const days = Object.keys(VIS).sort().filter((k) => VIS[k]["현지인"] != null);
    if (days.length) add({ id: "visitors", g: "visit", t: "경주시 하루 방문자 — 휴대전화 기반 (2026년 8월)", take: `${days[0].slice(4, 6)}/${days[0].slice(6)}~${days.at(-1).slice(4, 6)}/${days.at(-1).slice(6)} 기간이다. 경주시 전체 수치이므로 부지 하나의 계획 근거로는 쓰지 않는다.`, size: "m", tier: "T2", src: "한국관광데이터랩 DataLabService (KT 이동통신, 시군구)",
      opt: { grid: { left: 8, right: 8, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: days.map((x) => x.slice(4, 6) + "/" + x.slice(6)) }, yAxis: { type: "value", axisLabel: { formatter: (v) => v / 1000 + "k" } },
        series: [["현지인", C.gray], ["외지인", C.green], ["외국인", C.orange]].map(([k, c]) => ({ name: k, type: "line", stack: "v", areaStyle: { opacity: .5 }, showSymbol: false, lineStyle: { width: 1 }, itemStyle: { color: c }, data: days.map((x) => Math.round(VIS[x][k] || 0)) })) } }); }
  { const ls = R.landscape_survey;
    add({ id: "landscape", g: "visit", t: "경주의 대표 경관 — 시민·공무원·관광객 응답", take: "시민의 36%는 황리단길을, 관광객의 53%는 불국사를 꼽았다. 2025년 연구에서도 시민이 꼽은 상징적 중심 1위는 황리단길(59명 중 25명)이었다.", tier: "T1", src: ls.src,
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: ["시민", "공무원", "관광객"] }, yAxis: { type: "value", max: 60, axisLabel: { formatter: (v) => v + "%" } }, series: [{ name: "황리단길", type: "bar", data: ["시민", "공무원", "관광객"].map((k) => ls.representative["황리단길"][k]), color: C.orange, label: { show: true, position: "top", fontSize: 11 } }, { name: "불국사", type: "bar", data: ["시민", "공무원", "관광객"].map((k) => ls.representative["불국사"][k]), color: C.green, label: { show: true, position: "top", fontSize: 11 } }] } });
    const pp = ls.priority_projects;
    add({ id: "landprio", g: "visit", t: "우선해야 할 경관 사업 — 시민과 공무원 응답", take: `가장 개선이 필요한 경관 요소는 옥외광고물(시민 ${ls.worst_ad["시민"]}%)이다. 도시 정체성으로는 ‘신라왕경을 품은 역사도시’가 시민 ${ls.identity_silla["시민"]}%였다.`, tier: "T1", src: ls.src,
      opt: { grid: { left: 4, right: 40, top: 30, bottom: 4, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "value", show: false, max: 70 }, yAxis: { type: "category", inverse: true, data: Object.keys(pp), axisLabel: { color: C.ink, fontSize: 12, width: 190, overflow: "break" } }, series: [{ name: "시민", type: "bar", data: Object.values(pp).map((v) => v["시민"]), color: C.green, barCategoryGap: "35%" }, { name: "공무원", type: "bar", data: Object.values(pp).map((v) => v["공무원"]), color: C.gray, label: { show: true, position: "right", fontSize: 11, color: C.ink2 } }] } }); }
  add({ id: "heritagecount", g: "visit", t: "지정 문화재 수 300건 → 326건 (2004–2014)", take: `국가지정 ${fmt(R.heritage_count.national.at(-1))}건이다. 지정이 늘수록 문화유산 보호구역에 따른 건축 제한 범위도 넓어진다.`, tier: "T1", src: R.heritage_count.src,
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: R.heritage_count.years }, yAxis: { type: "value", min: 180 }, series: [{ name: "전체", type: "line", data: R.heritage_count.total, color: C.ink, lineStyle: { width: 2.5 } }, { name: "국가지정", type: "line", data: R.heritage_count.national, color: C.green }, { name: "보물", type: "line", data: R.heritage_count.treasure, color: C.orange }, { name: "사적", type: "line", data: R.heritage_count.historic, color: C.purple }] } });
  add({ id: "parks", g: "visit", t: `도시공원 ${fmt(R.parks.total_count)}곳, 1인당 ${(R.parks.total_k_m2 * 1000 / p26).toFixed(1)}㎡ (2015)`, take: "근린공원 29곳이 전체 공원 면적의 92%다. 고시 2026-8호는 여기에 근린공원 3곳(55,415㎡)을 더한다.", tier: "T1", src: R.parks.src,
    opt: hbar(R.parks.kinds, R.parks.area_k_m2.map((v) => Math.round(v / 10)), { unit: "ha", top: 7, color: C.green2 }) });
  if (AR) { const G = AR.gyeongju, F = AR.fields, A = AR.ages; const fi = (n) => F.labels.indexOf(n); const hl = (names, key, b) => names.map((n) => ({ value: key(n), itemStyle: { color: n.name === "경주시" ? C.red : b } }));
    add({ id: "arts10k", g: "visit", t: `등록 예술인 ${fmt(G.n)}명 — 인구 1만 명당 ${G.per10k}명`, take: `경북의 시 중에서는 1위지만 전국 평균(약 ${AR.nation.per10k}명)보다 낮고, 8개 도 122개 시군구 중 ${G.rank_in_8do[0]}위다. 전주·강릉·공주는 30명대 후반~60명이다.`, tier: "T2", src: AR.src.kawf, lead: "한국예술인복지재단 예술활동증명 누적 인원을 주민등록 인구(2026.08)로 나눴다. 복지사업 신청용 등록이라 등록하지 않은 공예인·귀촌 작가는 들어 있지 않다.",
      opt: { ...hbar(AR.compare.map((x) => x.name), AR.compare.map((x) => x.per10k), { unit: "명", top: 10 }), series: [{ type: "bar", data: hl(AR.compare, (x) => x.per10k, C.green), barCategoryGap: "32%", label: { show: true, position: "right", fontSize: 11.5, color: C.ink2, formatter: (d) => d.value } }] } });
    add({ id: "artsfield", g: "visit", t: "예술인 분야 구성 — 경주·전주·전국", take: `경주는 국악 ${pct(F.pct["경주"][fi("국악")])}(전국 ${pct(F.pct["전국"][fi("국악")])}), 미술·문학 비중이 높고 연극·영화·연예 비중은 매우 낮다. 공연장과 제작 산업이 없는 도시의 일반적인 구성이다.`, size: "m", tier: "T2", src: AR.src.kawf,
      note: "이 구성에 맞는 부지 프로그램은 공연장보다 공방·작업실·국악 연습실·문화재 수리기능 공방 쪽이다. 참고로 1946년 경주예술학교의 교사(校舍)는 옛 경주역사와 철도기관고였다(T4, 언론 연재).",
      opt: { grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: F.labels.slice(0, 11), axisLabel: { fontSize: 11, interval: 0 } }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" } }, series: [{ name: "경주", type: "bar", data: F.pct["경주"].slice(0, 11), color: C.red }, { name: "전주", type: "bar", data: F.pct["전주"].slice(0, 11), color: C.orange2 }, { name: "전국", type: "bar", data: F.pct["전국"].slice(0, 11), color: C.gray2 }] } });
    add({ id: "artsage", g: "visit", t: "예술인 연령 구성 — 경주는 50~60대, 전국은 30대가 많다", take: `경주 예술인의 50~60대 비율은 ${pct(A.pct["경주"][3] + A.pct["경주"][4])}(전국 ${pct(A.pct["전국"][3] + A.pct["전국"][4])})다. 10년 안에 절반 정도가 은퇴 연령에 든다.`, tier: "T2", src: AR.src.kawf,
      opt: { grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: A.labels }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" } }, series: [{ name: "경주", type: "line", data: A.pct["경주"], color: C.red, lineStyle: { width: 3 }, areaStyle: { opacity: .08 } }, { name: "전주", type: "line", data: A.pct["전주"], color: C.orange2 }, { name: "안동", type: "line", data: A.pct["안동"], color: C.green2 }, { name: "전국", type: "line", data: A.pct["전국"], color: C.ink, lineStyle: { type: "dashed" } }] } });
    const ec = AR.econ;
    add({ id: "artsecon", g: "visit", t: "예술 관련 고용 — 창작업과 유산 관리업 종사자", take: `경주의 사적지·박물관·도서관 종사자는 ${fmt(ec[0].heritage_emp_2020)}명, 창작·예술업 종사자는 ${ec[0].create_emp_2020}명이다(2020). 경주의 예술 관련 고용은 창작보다 유산 관리 쪽에 있다.`, tier: "T2", src: AR.src.econ,
      opt: { grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: ec.map((x) => x.name.replace("시", "").replace("군", "")), axisLabel: { fontSize: 11, interval: 0 } }, yAxis: { type: "value" }, series: [{ name: "902 사적지·박물관·도서관", type: "bar", data: ec.map((x) => x.heritage_per10k_2020), color: C.green }, { name: "901 창작·예술", type: "bar", data: ec.map((x) => x.create_per10k_2020), color: C.orange }] } });
    add({ id: "artsgb", g: "visit", t: "경북 10개 시 — 인구 1만 명당 예술인", take: `절대 수는 포항 764명, 경주 675명, 경산 654명 순이다. 인구 대비로는 경주가 1위, 경산이 2위다.`, tier: "T2", src: AR.src.kawf,
      opt: { ...hbar(AR.gb_cities.map((x) => x.name), AR.gb_cities.map((x) => x.per10k), { unit: "명", top: 10 }), series: [{ type: "bar", data: hl(AR.gb_cities, (x) => x.per10k, C.green2), barCategoryGap: "32%", label: { show: true, position: "right", fontSize: 11.5, color: C.ink2, formatter: (d) => d.value } }] } }); }

  // ======================= 시민의 목소리
  { const sv = X.surveys.filter((r) => /부지|경주역 활용|미래상/.test(r.q) && /\d/.test(r.v)); const rows = [];
    for (const r of sv) { const vals = r.v.split("/").map((t) => parseFloat(t)); const labs = r.a.split("/").map((t) => t.trim()); if (vals.length > 1) labs.forEach((l, i) => rows.push([`${r.when.slice(0, 4)} ${l}`, vals[i], r.survey])); else rows.push([`${r.when.slice(0, 4)} ${r.a}`, vals[0], r.survey]); }
    add({ id: "survey3", g: "voice", t: "옛 경주역 부지 활용에 대한 시민 응답 — 설문 3회", take: "2015년에는 복합위락시설 44.5%, 행정복합타운 26.2%였다. 2023년 설문은 시청 이전 63.7%로 보도됐다(원문 미확보). 2025년 설문은 문화·쇼핑 거점과 교통 거점을 꼽았다. 시간이 갈수록 공공청사와 교통 기능 쪽 응답이 늘었다.", size: "m", tier: "T1", src: "2030 기본계획 설문(T1) · 2023 폐철도 기본구상 설문(T4, 원문 미확보) · 2025 미래구상 연구 설문(T2)",
      lead: "서로 다른 기관이 다른 방법으로 물은 결과이므로 수치를 직접 비교하지 않는다. 초록은 2015년, 회색은 2023년, 보라는 2025년이다.",
      opt: { grid: { left: 4, right: 40, top: 4, bottom: 4, containLabel: true }, tooltip: { trigger: "axis", formatter: (ps) => `${rows[ps[0].dataIndex][0]}<br>${ps[0].value}<br>${rows[ps[0].dataIndex][2]}` }, xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: rows.map((r) => r[0]), axisLabel: { color: C.ink, fontSize: 11.5, width: 170, overflow: "truncate" } }, series: [{ type: "bar", data: rows.map((r) => ({ value: r[1], itemStyle: { color: /2030/.test(r[2]) ? C.green : /폐철도/.test(r[2]) ? C.gray : C.purple } })), label: { show: true, position: "right", fontSize: 11 }, barCategoryGap: "30%" }] } }); }
  for (const q of R.survey_2015.questions) add({ id: "s15_" + q.page + "_" + q.q.slice(0, 6), g: "voice", t: `2015년 설문 · ${q.q}`, take: `1위 ${q.items[0].a} ${q.items[0].v}%, 2위 ${q.items[1]?.a} ${q.items[1]?.v}%. 1위와 2위의 차이가 클수록 응답이 한쪽으로 모인 것이다.`, tier: "T1", src: `${R.survey_2015.meta} · 인쇄쪽 ${q.page}`, opt: hbar(q.items.map((i) => i.a), q.items.map((i) => i.v), { unit: "%", top: 6, color: q.q.includes("경주역") ? C.orange : C.green }) });
  { const s25 = R.survey_2025; for (const [k, t, tk] of [["transit_alt", "2025년 설문 · 대중교통 대안 선호", "현재 대중교통 평가는 5점 만점에 2.7점이다. 대안으로 자율주행 무료버스 18명, 보행공간 개선 13명, 옛 철도 재개통 10명, 트램 8명이 응답했다."], ["future_image", "2025년 설문 · 경주의 미래상", "관광도시 35명, 힐링도시 28명, 역사도시 23명이다."], ["needed_facility", "2025년 설문 · 원도심에 필요한 시설", "표본이 63명이라 비율이 아니라 응답 수로 표시한다."], ["friendly_cities", "2025년 설문 · 경주와 교류가 많은 도시", "울산 40명, 포항 40명, 대구 32명이다. 동해안 도시가 먼저 꼽혔다."]])
    add({ id: "s25_" + k, g: "voice", t, take: tk, tier: "T2", src: s25.meta, opt: hbar(Object.keys(s25[k]), Object.values(s25[k]), { unit: "명", top: 9, color: C.purple }) }); }

  // ======================= 출처 (표)
  add({ id: "srcs", g: "data", t: "이 페이지가 사용한 문서와 자료 등급", take: "수치를 인용할 때는 여기 적힌 문서명과 등급을 함께 적는다.", size: "l", html: `<table class="t"><tr><th>등급</th><th>문서</th><th>쓰인 곳</th></tr>${[["T1", "2030 경주도시기본계획 (승인, 475쪽)", "인구·토지·교통·관광·경제·주거·재정·시민의식 2015"], ["T1", "2030 경주시 경관계획 재정비 (2025.04)", "경관의식조사"], ["T1", "경주시 도시재생 전략계획(변경) (2022.01)", "쇠퇴진단·원도심 쇠퇴 원인·상권 분석도"], ["T1", "경주시 고시 제2026-8호 지구단위계획 · 경북 고시 2020-479호 고도지구 · V-World 토지이용규제", "획지·높이 제한·규제 구역"], ["T1", "경주시 홈페이지 청사안내 (2026-09-02) · 행안부 공유재산 운영기준", "시청 분산 현황·청사 규모"], ["T2", "경주시 원도심 미래구상 기획연구 (2025.07, 417쪽)", "시민설문 2025 · 교통거점 목표"], ["T2", "황오동 원도심·행복황촌 도시재생 성과지표 모니터링 (2025.09 / 2025.12)", "유동인구·창업폐업·공시지가·격자·연령·설문"], ["T2", "소상공인365 상권분석", "유동인구 8구역 · 업종"], ["T2", "KOSIS (주민등록·외국인주민·국적·지역별고용조사·인구이동) · 관광데이터랩 · ITS · 건축HUB · 소진공 · 경주시 공공데이터", "인구·청년·외국인·취업·교통·노후도·상가·학교·종교"], ["T2", "한국예술인복지재단 · 경제총조사 2015·2020 · 시굴조사 추진계획(2026.02)", "예술인 · 매장문화재"], ["T4", "2023 폐철도 기본구상 설문 (언론 경유)", "시청 이전 63.7% — 원문 미확보"]].map(([t, d, u]) => `<tr><td>${TIER(t)}</td><td>${d}</td><td>${u}</td></tr>`).join("")}</table>` });

  // ======================= 데이터 출처와 처리 — 카드 1장 = 자료 1건. 원천 → 어떻게 가져왔나 → 무엇을 했나 → 어디에 그렸나 → 한계
  const prov = (o) => `<div class="prov">${[["원천", o.from], ["가져온 방법", o.how], ["처리", o.proc], ["그린 곳", o.viz], ["한계", o.lim]].filter((r) => r[1]).map(([k, v]) => `<div class="pk">${k}</div><div class="pv">${v}</div>`).join("")}</div>`;
  const P = (id, t, tier, o, extra = {}) => add({ id: "d_" + id, g: "data", t, tier, take: o.take, size: o.size || "m", src: o.src || o.from, lead: o.take, note: "", html: prov(o), ...extra });
  P("gosi", "지구단위계획 구역·획지 — 고시 도면을 좌표에 맞춰 벡터로 만들었다", "T1", { take: "고시 원본은 좌표가 없는 PDF 도면이다. 좌표에 맞춘 것과 선을 딴 것은 내가 한 작업이고 오차는 구역 +1.3%, 획지 ±4%다.",
    from: "경주시 고시 제2026-8호(2026-01-22) 고시문·결정조서, 지형도면고시도 15매, 결정도 5매", how: "토지이음(eum.go.kr) 고시정보에서 첨부 다운로드(파일명 EUC-KR). API 아님", proc: "지형도면 11·12장의 안쪽 도곽선을 검출하고 도곽 좌표를 EPSG:5176(동경측지계)으로 가정해 좌표등록 → 색 마스크로 구역 쇄선·획지 경계 추출 → EPSG:5187 → 웹 4326. 결정도(1:1,500 래스터)는 좌표가 없어 육안 확인만", viz: "지도 ‘지구단위계획구역’·‘획지·공원·주차장’ 레이어, 카드 ‘획지 면적’", lim: "추출 구역 158,472㎡ vs 고시 156,460㎡(+1.3%), 획지별 ±4%. 법정 경계가 필요한 곳에는 고시문 수치를 쓴다" }, { map: "blocks" });
  P("godo", "높이 제한 구역(고도지구) — 경계는 V-World, 높이는 2020년 경북 고시 도면의 라벨", "T1", { take: "V-World 폴리곤에는 높이가 없다. 경북고시 2020-479호 도면의 지구명 라벨을 폴리곤 위치에 맞춰 붙였고, 도면 밖 20개는 ‘미확인’으로 남겼다.",
    from: "V-World LT_C_UQ123(용도지구) 49개 폴리곤 · 경상북도 고시 제2020-479호(2020-12-28) 조서와 지형도면 33매(벡터 PDF, 도곽 좌표 내장)", how: "V-World 2D 데이터 API 호출 · 고시 파일은 토지이음에서 다운로드", proc: "도면 총괄도의 라벨 좌표 → 폴리곤 배정. 신뢰도 4단계(label 도면 라벨 7 / zone 2026-8호 조서 교차 2 / area 조서 면적합 ±1% 4 / approx 추정 5) + 미확인 20", viz: "지도 ‘고도지구’ 레이어(높이별 색, 하위 토글), 카드 ‘높이 제한 구역’", lim: "2023-449호(최신 변경 고시)는 받지 않았다 → 2020년 이후 변경분 미반영 가능. 도심 밖(황성·동천·보문)은 도면 범위 밖" }, { map: "godo" });
  P("regareas", "규제 구역 13종 — 10종은 법정 경계, 3종은 필지 외곽으로 근사", "T1", { take: "역사문화환경보존지역·문화유산구역·보호지구·방화지구·고도지구·지구단위구역은 V-World 법정 폴리곤이다. 특별보존지구·보존육성지구·중점경관관리구역은 V-World에 없어 해당 필지들의 외곽선으로 그렸다.",
    from: "V-World LT_C_UO301(문화유산 관련 272건) · UQ126 역사문화환경보호지구 88 · UQ124 방화지구 8 · UQ123 · UQ141 / 근사 3종은 필지 토지이용계획 속성", how: "V-World 2D 데이터 API(S2 창 분할 호출)", proc: "종류별 dissolve, 면적(ha) 계산. 근사 3종은 ‘포함·저촉’ 필지 합집합 — 수집 창(부지 주변) 안에서만", viz: "지도 ‘규제 영역’ 레이어(종류 토글), 카드 ‘규제 구역 13종’", lim: "근사 3종은 법정 경계가 아니다(범례에 회색 표시). 2026-09-17 오전의 v1은 전부 필지 근사였다" }, { map: "reg_areas" });
  P("landuse", "필지별 토지이용계획 → 규제 겹 수", "T1", { take: "토지이음 확인서와 같은 원천을 7,616필지에 대해 API로 받아 4겹 정의로 셌다. ‘접함’은 규제가 아니므로 뺐다.",
    from: "V-World NED getLandUseAttr(필지별 지역·지구 항목) 7,616필지", how: "필지마다 1회 호출(한도 3만/일)", proc: "겹 = ①용도지역·지구(항상 1) + ②고도보존육성지구(특별보존∨보존육성) + ③문화유산법(보존지역∨지정구역) + ④지구단위계획구역. ‘포함·저촉’만 인정, ‘접함’은 lu_touch 필드에 따로 기록", viz: "지도 ‘규제 중첩’ 레이어(필지 클릭 시 항목 목록), 카드 ‘필지별 규제 겹 수’", lim: "수집 창은 부지 주변(129.2128–129.2252 / 35.8370–35.8538)뿐. 접함을 포함했던 이전 계산은 3겹 이상 4,496필지로 과대" }, { map: "reg" });
  P("parcels", "연속지적 + 건축물대장 → 건물 노후도", "T1", { take: "지적 7,616필지에 건축물대장 6,828동을 PNU로 붙여 2,164필지의 사용승인일을 얻었다. 동천동·인왕동 대장은 아직 받지 않았다.",
    from: "V-World LP_PA_CBND_BUBUN(연속지적, 공시지가 포함) · 국토부 건축HUB BldRgstHubService 표제부(성동·황오·노서·노동·성건, 2026-09)", how: "V-World 2D API · 건축HUB는 공공데이터포털 키로 법정동별 전량 호출", proc: "PNU 19자리 조인, 필지 안 최고령 건물의 경과연수. 사용승인일 없는 12필지(철도시설·옛 역사)는 ‘미상’ 회색", viz: "지도 ‘필지·건축물 노후도’ 레이어, 카드 ‘건물 노후 정도’, KPI ‘노후 20년↑’", lim: "동천·인왕 미수집. 공시지가 기준연월 미확인. 20년↑ 비율은 창 안 필지 기준이지 행정동 통계가 아니다" }, { map: "parcels" });
  P("energy", "건물 전기 사용량 — 공실의 대리변수로 받았지만 0 kWh가 곧 공실은 아니다", "T2", { take: "구역 300m 안 450필지 중 154필지만 기록이 있다. 단독주택·소규모 공동주택은 제공 대상이 아니다.",
    from: "건축HUB BldEngyHubService(건물 전기·가스, 2026-05)", how: "공공데이터포털 키, 한도 1,000건/일", proc: "필지당 kWh/㎡", viz: "지도 ‘건물 전기사용’ 레이어", lim: "미계량·미제공·신축·공실을 구분할 수 없다. 리포트 카드로는 쓰지 않았다" }, { map: "energy" });
  P("vworld_plan", "용도지역·도시계획시설·공원녹지·법정동 경계", "T1", { take: "모두 V-World 2D 데이터 레이어를 그대로 받은 것이다. 고시 2026-8호(신설 근린공원 3개 등) 반영 여부는 대조하지 않았다.",
    from: "V-World LT_C_UQ111(용도지역) · UPIS UQ151/152/153/155/161(도시계획시설) · UQ153(공원·녹지·광장 124) · LT_C_ADEMD_INFO(법정동 56)", how: "V-World 2D API, S2 창 4분할(INVALID_RANGE 회피)", proc: "좌표 5187 변환, 공원 폴리곤은 MapLibre용 CCW 방향 정렬", viz: "지도 ‘용도지역’·‘도시계획시설’·‘공원·녹지·광장’·‘법정동’ 레이어", lim: "용도지역 dyear가 2007~2024 혼재. 결정 폴리곤이라 집행·미집행이 섞여 있다(exc_nam 참조)" }, { map: "upis" });
  P("hadm", "행정동 인구 — 통계는 KOSIS, 행정동 경계는 내가 근사한 것", "T2", { take: "주민등록 5세별 인구는 KOSIS API로 받았다. 행정동 경계 파일이 없어 법정동을 합치고 지오코딩으로 43개를 배정, 임야 13개는 손으로 배정했다. 2025년 폐지된 중부동은 황오동에 합산했다.",
    from: "행정안전부 주민등록 인구 (KOSIS 101 DT_1B04005N) 2026-08 5세별, 2011–2025 연도별 · 법정동 경계 V-World", how: "KOSIS 파라미터 API(objL1=ALL은 행 수 제한으로 연도별 1회씩 호출)", proc: "법정동 합집합 → 행정동 22개 근사. 밀도·면적은 EPSG:5187로 계산. 급간은 분포를 보고 손으로 정함(분위수 아님)", viz: "지도 ‘총인구·밀도·65세↑·청년·10년 변화’ 레이어, 카드 ‘연령별 인구·행정동 합계·65세 이상 비율·10년 변화·청년이 사는 곳’", lim: "경계가 근사라 밀도·면적은 참고치. 황오동을 합산 없이 보면 +20%로 보인다(통합 효과)" }, { map: "pop_total" });
  P("foreign", "외국인주민·다문화가구·국적", "T2", { take: "외국인주민(읍면동)과 다문화가구(읍면동)는 행정안전부, 국적(시군구)은 법무부 통계다. 집계 기준이 달라 셋을 합칠 수 없다.",
    from: "KOSIS 110 DT_110025_A033_A(외국인주민 유형) · A045_A(다문화가구) 2024.11 · 111 DT_1B040A9C(등록외국인 국적) 2025", how: "KOSIS 파라미터 API", proc: "읍면동 → 행정동 근사 경계 조인. 비율 분모 = 주민등록 2026-08 + 국적미취득 외국인(시점 차이 있음)", viz: "지도 ‘외국인주민·다문화가구’ 레이어, 카드 ‘외국인주민 유형·국적별’", lim: "동별 국적은 공개되지 않는다. 외국인주민 22,467명(행안부) ≠ 등록외국인 15,621명(법무부)" }, { map: "fr_pct" });
  P("youth", "청년 — 취업 구조와 순이동", "T2", { take: "산업별 취업자는 전 연령 통계다. 청년만의 산업별 분포는 시군구 단위로 공표되지 않아 카드의 청년 산업 추정은 추정이다.",
    from: "통계청 지역별고용조사 (KOSIS DT_1ES3A30S·A31S·A03_A01S, 2026 상반기) · 국내인구이동통계 (DT_1B26002, 2020–2025) · 주민등록 5세별", how: "KOSIS 파라미터 API", proc: "20–34세 = 5세 구간 합. 순이동 = 전입 − 전출, 연령대별", viz: "지도 ‘청년 20–34세’ 레이어, 카드 ‘청년이 사는 곳·취업자·순이동’", lim: "연령×산업 교차는 통계청 MDIS 신청 필요. 인구주택총조사 표(DT_1PC2009 등)는 API가 err 30을 반환해 못 받았다" }, { map: "pop_y2034" });
  P("plan2030", "2030 경주도시기본계획 — 475쪽 PDF의 표를 손으로 옮겨 적었다", "T1", { take: "인구·고령·부양·생활권·사업체·전력·주택·재정·의료·수단 분담·차량·철도·주차·버스·도로 V/C·관광객·문화재·공원·2015년 설문이 모두 이 문서의 표를 전사한 값이다. 전사 오류 가능성이 있으므로 인용 전 원문 쪽수와 대조해야 한다.",
    from: "2030 경주도시기본계획(승인본, 475쪽). 표마다 인쇄쪽을 기록(예: 계획인구 p.142, 수단분담 p.206, 설문 p.72–83)", how: "PDF 열람 후 수기 전사 → report_stats.json (pipeline/build_report_stats.py)", proc: "단위 통일, 계획인구는 주민등록 실제와 같은 축에 배치(집계 기준이 달라 2011~13년에 약 1만 명 차이)", viz: "‘사람’·‘일과 상권’·‘이동’·‘관광’·‘시민의 목소리’ 그룹의 T1 카드 대부분, 지도 ‘생활권’ 레이어", lim: "기초 통계가 2013~2015년으로 오래됐다. 손 전사이므로 공모 문서에는 원문 대조 후 사용" });
  P("strategy", "도시재생 전략계획 2022 — 표 전사 1건, 서술 기반 1건, 도면 디지타이징 1건", "T1", { take: "쇠퇴진단 표(p.251)는 전사, 도심 가로망은 문장에 나온 도로명으로 표준노드링크에서 골라 그린 것, 상권 4구역은 항공사진 위 개략도를 좌표에 맞춰 딴 것이다. 셋의 정확도가 다르다.",
    from: "경주시 도시재생 전략계획(변경) 최종보고서 2022.01 — 쇠퇴진단 p.251 · 가로망 서술 §2 · 「중심지 상권 분석도」 p.42", how: "PDF 전사 / 서술 해석 / 300dpi 렌더 후 라벨 핀 6개 ↔ V-World 장소 좌표로 아핀 변환 → 색상 마스크 → 폴리곤", proc: "상권 GCP 잔차 24~64m. 가로망은 원문에 도면이 없어 도로명 → 링크 선택", viz: "지도 ‘쇠퇴진단’·‘도심 가로망’·‘상권 4구역’ 레이어, 카드 ‘쇠퇴 진단’", lim: "쇠퇴진단은 기준연도 미기재 → 2026 공모용은 재산출 필요. 상권 경계는 ±50m로 읽을 것" }, { map: "commerce_zones" });
  P("hwango", "황오동 도시재생 모니터링 보고서 2025.09 — 전사 + 재분류", "T2", { take: "유동인구 시계열·창업폐업·공시지가·격자 32칸·연령·설문·매출을 보고서 표에서 옮겨 적었다. ‘창업 70건 중 임시 가게 27건’ 분리는 내가 인허가 명세를 다시 읽어 한 재분류다.",
    from: "2024년 황오동 원도심 도시재생뉴딜사업 성과지표 및 모니터링 용역 결과보고서(수정중), 공공도시, 2025.09. 표별 인쇄쪽 기록(p.10–12, 25–70, 81–86 등)", how: "PDF 전사 → hwango_report.json · 공시지가 29필지 좌표는 카카오 주소검색", proc: "창업 명세에서 축제 기간 며칠만 등록된 업소를 ‘임시 가게’로 재분류. 격자·연령은 2018=100 지수화", viz: "‘일과 상권’ 그룹의 hw 카드 8장, 지도 ‘공시지가 지점’ 레이어", lim: "보고서 자체에 2021=2023 복사 오류·연도 라벨 불일치가 있다. 행복황촌 보고서의 유동인구 +396%는 재현되지 않아 쓰지 않았다" }, { map: "landprice_pts" });
  P("footfall", "유동인구 8구역 — 소상공인365를 같은 정의로 다시 뽑았다", "T2", { take: "두 모니터링 보고서가 서로 다른 값을 보여 같은 플랫폼·같은 기간으로 8개 구역을 직접 재추출했다. 플랫폼이 공개하는 최근 13개월만이다.",
    from: "소상공인365(bigdata.sbiz.or.kr) 상권분석 리포트 — 통신사 통화량 기반 50m 격자 추정 유동인구, 월별 일평균, 2025.06~2026.06", how: "로그인 없이 브라우저 페이지 컨텍스트에서 폴리곤 8개(EPSG:5181)를 전송해 받은 JSON을 저장. 순수 requests로는 미검증(세션·좌표변환이 페이지에 묶임)", proc: "ha당 = 일평균 ÷ 면적. 구역 정의: A 보고서 격자 32셀 / B 위치도 디지타이징(근사) / C·D 고시 구역 / E~H 반경 원", viz: "지도 ‘유동인구 8구역’ 레이어(클릭 항목 설명은 레이어 i), 카드 ‘유동인구 8개 구역·시간대별·생활/관광 업종’", lim: "보행량이 아니고 통과교통이 섞인다. 2020~2024 시계열은 보고서 전사값에 의존. 매월 재추출해 시계열을 쌓아야 한다" }, { map: "footfall_areas" });
  P("sbiz", "상가 업소·소진공 상권영역·게스트하우스", "T2", { take: "영업 중인 업소의 스냅샷이다. 폐업한 업소는 들어 있지 않아 ‘몇 개가 사라졌나’는 이 자료로 알 수 없다.",
    from: "소상공인시장진흥공단 상가(상권)정보 API B553077 sdsc2 — storeListInRectangle 10,314 · storeZoneInRectangle 7 (2026-03) · 경주시 게스트하우스 현황 API 24", how: "공공데이터포털 키, 사각형 창 분할 호출", proc: "대분류별 색, 상권명은 소진공 mainTrarNm(대표 시설명)", viz: "지도 ‘상가 업소’(업종 토글)·‘상권영역’ 레이어, 카드 ‘상가 업소 업종’, KPI ‘업소(화면)’", lim: "폐업 이력 없음. 관광지 6곳은 지오코딩 실패" }, { map: "stores" });
  P("landscape", "경관계획 2025 경관의식조사 · 미래구상 연구 2025 설문 · 2023 폐철도 설문", "T2", { take: "경관의식조사는 T1 문서의 표 전사, 2025 설문은 표본 63명의 응답 수, 2023 설문(시청 이전 63.7%)은 언론 보도만 있고 원문을 확보하지 못했다(T4).",
    from: "2030 경주시 경관계획 재정비(2025.04) p.100–108 · 경주시 원도심 미래구상 기획연구(동국대·가천대, 2025.07, 417쪽) §2.2 · 경주시 폐철도 기본구상 설문 2023.04(n=3,151, 언론 경유)", how: "PDF 전사 / 언론 기사", proc: "설문 3회는 기관·방법이 달라 수치를 직접 비교하지 않고 같은 카드에 색만 달리 표시", viz: "카드 ‘대표 경관·우선 경관 사업·부지 활용 응답 3회·2025년 설문 4장’", lim: "2023 설문은 원문 미확보 → 공모 문서에는 쓰지 않는다. 2025 설문은 n=63이라 비율 대신 응답 수로 표시" });
  P("heritage", "매장문화재 — 지표조사와 시굴조사 추진계획 수치", "T2", { take: "면적·비용·기간은 2022년 지표조사와 2026년 혁신포럼 발표자료의 수치를 옮긴 것이다. 지도에는 아직 시굴 구역 폴리곤을 올리지 않았다.",
    from: "성림문화재연구원 지표조사 2022.05(148,770㎡) · 구)경주역일원 매장유산 시굴조사 추진계획, 2026.02.27 도시재생혁신포럼 발표자료", how: "문서 수치 전사", viz: "카드 ‘매장문화재’", lim: "시굴 구역 도면의 좌표등록은 미착수. 시굴 전에는 청사 위치를 확정할 수 없다" });
  P("cityhall", "시청 분산 현황·공영주차장 — 홈페이지를 읽고 손으로 정리", "T1", { take: "API가 아니라 시청 청사안내 페이지와 시설관리공단 페이지를 열람해 표로 만들고 주소를 지오코딩했다. 본청+의회 인원 800~950명은 가정이다.",
    from: "경주시 홈페이지 청사안내(2026-09-02 갱신) · 경주시시설관리공단 교통운영 시설안내(2026-09-21 열람) · 행정안전부 공유재산 운영기준", how: "웹 열람 수기 정리 → V-World 지오코더(건물 대표점)", proc: "과 수를 장소별로 집계, 임차 여부 표시. 주차장은 노상·민영·읍면 제외", viz: "지도 ‘시청 분산 현황’·‘공영주차장’ 레이어, 카드 ‘현재 경주시청’·‘공영주차장’", lim: "인사통계(정원)는 미공개라 인원은 가정. 시청사공영주차장은 면수 미공개" }, { map: "cityhall_sites" });
  P("facilities", "학교·종교시설·도서관·박물관·미술관·공원 지점·관광단지", "T2", { take: "학교는 표준데이터 API, 종교시설은 시 공개 파일을 지오코딩, 도서관·박물관·미술관·공원은 V-World 장소검색 POI다. 마지막 것은 공식 목록이 아니라 누락·중복이 있을 수 있다.",
    from: "전국초중등학교위치표준데이터(한국교육시설안전원, 2026-03-20) 83곳 + 유치원·대학은 카카오 로컬(T4) · 경주시 종교시설현황 2025-02-06 파일 586건 + 경주이슬람센터 1건(공식 현황에 없어 별도 추가, 주소 원화로281번길 22) · V-World 장소검색(bbox 경주시, 카테고리 정규식 필터) 160건 · 관광단지는 V-World UO601 + 토지이음 고시번호로 이름 확인", how: "공공데이터포털 API / 파일 → V-World 지오코더 541 + 카카오 23 / V-World 검색 API(80m 안 동명 중복 제거)", proc: "종교시설 22건은 좌표 미확인", viz: "지도 ‘학교’·‘종교시설’·‘도서관·박물관·미술관·공원’·‘관광단지’ 레이어, 카드 ‘학교·종교시설·관광단지’", lim: "도서관·박물관미술관·도시공원 표준데이터 API는 활용신청 대기 중 → 승인되면 교체. 시 공식 종교시설 현황에는 이슬람 항목이 없다" }, { map: "facilities" });
  P("axes", "도시축 변천 인터랙티브 도판 — 원본 HTML을 그대로 넣었다", "T2", { take: "「경주 도시 축의 변천사」 HTML을 수정 없이 리포트 안에 iframe으로 넣었다. 좌표가 없는 개념도라 지도 레이어로는 올리지 않았다(좌표등록 시도는 거점 점이 실제와 100~200 m 어긋나 철회).",
    from: "경주_도시축_변천사_인터랙티브_수정.html (2026-09, 배경 = 미래구상 연구 2025 Figure 3d 원도 + 시대별 원도판 4장 내장) · 축 서술 원문 미래구상 연구 p.17–23·77–109(T2), 동지 일출 가설축은 다큐 요약(T4)", how: "파일 복사(public/urban_axes.html), 썸네일은 내장 배경 PNG 축소", proc: "없음(원본 그대로)", viz: "카드 ‘경주 도시 축의 변천사’(부지와 규제) — 클릭하면 도판이 열리고 새 창 링크 제공", lim: "선은 도판 저자의 개념축, 위치는 개략. 시대 구분과 해석은 도판 저자의 것이며 이 사이트가 검증한 사실이 아니다" });
  P("rail", "철도역·폐선·현행선 — 지금은 OSM", "T4", { take: "폐선 3.5km와 현행선은 OpenStreetMap에서 받은 선이다. T4이므로 지형도면 벡터화로 바꿀 예정이고, 그 전에는 위치 참고용이다.",
    from: "OSM railway=abandoned/disused/rail (Overpass, 2026-09-21) · 역 위치 OSM·위키", how: "Overpass API", proc: "구경주역→황성→석장→금장 노반 연속 구간 확인", viz: "지도 ‘폐선’·‘현행 철도’·‘철도역’ 레이어", lim: "신 서경주역 이용객 수치는 나무위키 전재 → 철도통계연보로 치환 필요" }, { map: "rail_abandoned" });
  P("traffic", "도로 속도 — 표준노드링크 + ITS 실시간 스냅샷 + ITS 이력 표본일", "T2", { take: "속도는 있지만 교통량(대수)은 없다. 정체 판정 기준은 도로 등급별 관행값이며 공식 고시 원문은 확인하지 못했다.",
    from: "국가교통정보센터 표준노드링크(2026-09-14, 경주 창 4,594링크) · ITS trafficInfo API 5분 스냅샷(2026-09-17~) · ITS 교통소통 이력 파일(일별 5분, 1일 741MB → 경주 1~2MB, 매월 둘째 화·토 표본)", how: "zip 다운로드 / 공공데이터포털 키 API / 세션 쿠키 파일 다운로드 배치", proc: "링크 매칭, 시간대·평일/주말 평균. 임계: 고속국도 40/80, 도시고속 30/50, 그 외 15/25 km/h. 12시대 결측", viz: "지도 ‘시간대별 소통’ 레이어(시간 슬라이더·재생), 카드 ‘시간대별 속도·정체 상위 구간’", lim: "표본일에 명절·행사일 없음. VDS 교통량은 못 받음. 기본계획의 V/C 표는 별도 전사값" }, { map: "traffic_hist" });
  P("arrive", "경주에 오는 길 — 4개 문서 전수 검색 + KOSIS 국민여행조사 + 도로공사 AADT", "T2", { take: "‘관광객 입경 교통수단’은 4개 문서에 없다. 있는 것만 모았다: 관문 위치(경관계획·전략계획 서술 → V-World 좌표), 진입축 교통량(기본계획 표 전사), 고속버스 운행횟수(기본계획 표), 시민 설문(미래구상 전사), 권역별 수단통행·버스노선 수(전략계획 표 전사), 전국 평균(KOSIS API), 고속도로 AADT(도로공사 CSV).",
    from: "미래구상 2025 p.30–31·66–68 · 전략계획 2022 p.48·51–54 · 2030 기본계획 p.199–208 · 2030 경관계획 관문적 경관거점 · KOSIS 113 DT_113_STBL_1029530(국민여행조사, 2023–2025) · 한국도로공사 AADT 2021–2025 CSV(C-008)", how: "PDF 4권 전문 텍스트 추출 후 정규식 검색(교통수단·이용교통·자가용·KTX·고속버스·관광버스·유입경로·관문·IC) → 해당 쪽 육안 확인·전사 / KOSIS 파라미터 API / CSV 파싱 / 관문 좌표 V-World 장소검색", proc: "pipeline/build_arrival_transport.py → arrival_transport.json · gateways_4326.geojson. IC 좌표는 인접 정류장·전광판 지점(±300m)", viz: "지도 ‘진입 관문’ 레이어(시청·교통거점), 카드 ‘관광객은 어떤 교통수단으로…’ 외 7장(이동 그룹)", lim: "경주 방문자 한정 입경 수단 비율 없음 · 국민여행조사 시도별 교차표 API 미제공 · IC 진출입량·터미널 이용객·2014 이후 신경주역 승하차 미수집 → gaps.md" });
  P("bus", "버스정류장·시내버스 이용", "T2", { take: "정류장 위치는 국토부 파일이고 노선·승하차는 없다. 경주시 버스 API는 발급받았지만 서버가 504를 반환해 못 썼다.",
    from: "국토교통부 전국 버스정류장 위치정보 파일(2025-10-31) 경주시 1,951개 · 시내버스 이용 인원은 기본계획 표(p.208) 전사", how: "파일 다운로드", viz: "지도 ‘버스정류장’ 레이어, 카드 ‘시내버스 연간 이용 인원’", lim: "승하차·노선 없음" }, { map: "busstops" });
  P("visitors", "관광 방문자 — 관광데이터랩(시군구) · 지정관광지 입장객(기본계획)", "T2", { take: "관광데이터랩 방문자는 경주시 전체(S3) 수치이므로 부지(S1) 계획의 근거로는 쓰지 않는다. 기본계획의 입장객과는 정의가 다르다.",
    from: "한국관광공사 관광데이터랩 DataLabService(KT 이동통신, 시군구, 2026-08 31일) · 2030 기본계획 지정관광지 입장객 표", how: "공공데이터포털 키 API / PDF 전사", proc: "현지인·외지인·외국인 일별 적층", viz: "카드 ‘하루 방문자·지정관광지 입장객’", lim: "S3 통계로 S1을 정당화하지 않는다는 규칙에 따라 체류·규모 참고로만" });
  P("arts", "예술인 — 예술활동증명 대시보드 열람 + 경제총조사", "T2", { take: "예술인 수는 한국예술인복지재단 대시보드 화면을 읽어 옮긴 값이고, 고용은 KOSIS 경제총조사다. 등록 기반이라 미등록 공예인·귀촌 작가는 빠진다.",
    from: "한국예술인복지재단 예술인경력정보시스템 대시보드(2013~2026.09.21 누적 예술활동증명) · 통계청 경제총조사 2015·2020 (KOSIS DT_1KI1510·DT_2KI2010, 산업소분류 901·902)", how: "대시보드 열람 수기 / KOSIS API", proc: "1만 명당 = 인원 ÷ 주민등록 2026-08. 비교 도시 10곳", viz: "카드 ‘등록 예술인·분야·연령·예술 관련 고용·경북 10개 시’", lim: "복지사업 신청용 등록이라 과소. 1946년 경주예술학교 관련 서술은 언론 연재(T4)" });
  P("meta", "이 사이트가 하는 일과 하지 않는 일", "T2", { size: "l", take: "모든 처리본은 EPSG:5187, 웹 출력만 4326. 색 구간은 전부 임의 설정. API 키는 .env에만 있고 공개 사이트에는 V-World 키를 넣지 않아 배경지도가 OSM이다. 같은 저장소에서 다른 작업 세션이 병행해 일부 레이어(학교·종교·쇠퇴진단·생활권·시청·주차장)는 그쪽이 만들었다.",
    from: "사용한 키: V-World(도메인 바인딩) · 공공데이터포털 2종 · KOSIS · 법령정보. 키 없이: 토지이음·ITS 파일·국토부 파일·OSM·소상공인365(브라우저)", how: "파이프라인 9_도시/pipeline/*.py → archive/C_data/processed → scripts/sync_data.py → public/data", proc: "아카이브 index.csv에 자료 ID(A-001~, C-001~), sources.yaml에 원천, gaps.md에 못 구한 것 기록", viz: "지도 37개 레이어 · 리포트 카드 92장 + 이 출처 카드", lim: "못 받은 것: 경북고시 2023-449호(보류) · 경주시 버스 API(504) · SGIS 키 · 상가 폐업 이력 · 동별 국적 · ITS VDS 교통량 · 2023 설문 원문 · 표준데이터 API 3종(활용신청 대기) · 동천·인왕동 건축물대장. 아직 지도에 없는 것: 시굴조사 구역 도면, 폐선 지형도면 벡터, 세계유산 완충구역" });

  render(R, X, MS, Y);
}

// ---------------------------------------------------------------- 렌더
const charts = [];
function chartInto(el, opt, small) {
  const ch = echarts.init(el, "gj");
  ch.setOption({ animationDuration: reduced ? 0 : 500, ...opt, ...(small ? { legend: opt.legend ? { ...opt.legend, textStyle: { fontSize: 10.5 } } : undefined } : {}) });
  charts.push(ch); return ch;
}
// 썸네일 차트는 카드가 문서에 붙고 화면 근처에 왔을 때 만든다 — 붙기 전에 init하면 0×0 캔버스가 되고, 92장을 한 번에 그리면 첫 화면이 느리다
const lazy = new IntersectionObserver((es) => { for (const e of es) if (e.isIntersecting && e.target._opt) { chartInto(e.target, e.target._opt, true); e.target._opt = null; lazy.unobserve(e.target); } }, { rootMargin: "600px 0px" });
function render(R, X, MS, Y) {
  const main = document.getElementById("main"); const chips = document.getElementById("chips");
  const p26 = R.pop_actual.pop_2026_08;
  const tiles = document.getElementById("hero-tiles");
  for (const t of [
    { k: "폐역 구역 유동인구 (1ha당 하루)", v: fmt(X.footfall.D_zone.per_ha), u: "명", d: `성동시장 주변 200m는 ${fmt(X.footfall.G_seongdong_market_r200.per_ha)}명 — 15배 차이`, c: "footfall" },
    { k: "청사 밖에 있는 본청 과", v: "15", u: "/45개", d: "12개 과는 민간 건물 임차, 문서고는 체육관", c: "cityhall" },
    { k: "시청 주변 500m의 저녁(18–23시) 비중", v: pct(X.footfall.F_cityhall_r500.hourly_pct[4]), d: "8개 구역 중 유일하게 저녁까지 사람이 남는 곳", c: "ffhour" },
    { k: "주민등록 인구 2026.08", v: fmt(p26), u: "명", d: `계획인구 320,000명보다 ${Math.abs((p26 / 320000 - 1) * 100).toFixed(0)}% 적음 · 65세 이상 30.0%`, c: "popplan" },
    { k: "20–34세 순유출 2020–25 합계", v: fmt(Y ? Y.net["20-34세"].reduce((a, b) => a + b, 0) : null), u: "명", d: "20–24세가 매년 가장 많이 나감", c: "ymig" },
    { k: "건물 높이 상한", v: "20", u: "m", d: "도심20m지구 146,489㎡ · 문화유산 주변 높이 기준 적용", c: "godo" },
  ]) tiles.appendChild($(`<div class="tile" data-card="${t.c}" role="button" tabindex="0"><div class="k">${t.k}</div><div class="v">${t.v}${t.u ? `<small>${t.u}</small>` : ""}</div><div class="d">${t.d}</div></div>`));
  document.getElementById("plan").innerHTML = `<h3>부지 구성 — 토지이용계획(안) v5 · 구역 156,460㎡(고시 2026-8호)</h3>
    <table class="t plan-t"><tr><th>용도</th><th>면적(㎡)</th><th>비율</th><th>위치 · 내용</th><th>고시안</th></tr>
    ${[["시청·의회","15,000","9.6%","북측(양정로~북천). 본청 42과·의회·법정의무시설. 5층, 연면적 상한 37,500㎡. 매장문화재 시굴 후 위치 확정. 황오동 방향 출입구","24,987 (2개소)"],
       ["공공시설","12,000","7.7%","광장 동변, 시청 맞은편. 대강당·소전시(알천홀 승계)·원도심 건강생활지원센터·가족/외국인주민센터·공공어린이집·도시재생지원센터. 수장고는 두지 않는다 — 발굴 유물은 국가귀속으로 국립경주박물관 영남권수장고가 보관하고, 현상보존 유구는 광장·공원의 노출창으로 보여준다","9,770"],
       ["모빌리티 허브","12,500","8.0%","남측(원효로변) 교통광장. 트램·자율셔틀 정거장 2면, 순환셔틀 4베이, 동해안 방향 시외버스 6베이, 관광버스 6베이, 주차동 150면(3층 이하), 공영자전거·PM·카셰어링(외곽 방향 전용)","주차장 5,756"],
       ["광장","14,000","8.9%","옛 역사 동측, 동서 보행 주축의 경첩. 광장형 공유주차 200면(평일 시청·주말 관광, 수목 격자·투수 포장). 유구 노출창","—"],
       ["청년 주거","30,000","19.2%","중부. 청년·산업단지 근로자 주거(기숙사형 포함). 5층, 약 600~750세대. 밤을 책임지는 유일한 용도","—"],
       ["공동캠퍼스","12,000","7.7%","청년 주거 남측. 지역대학 공동캠퍼스, 중부동과 나누어 배치. 대학 협약 전에는 3단계 유보지","—"],
       ["근린시설","7,960","5.1%","원화로변, 성동시장 맞은편. 저층 소매·음식·생활서비스. 판매시설은 획지당 1,000㎡ 이하, 시장 상인회 우선 입점","42,031 (상업 3개소)"],
       ["공원녹지","38,000","24.3%","북천 수변 12,000 · 남측 근린 11,000 · 옛 철로 선형공원 15,000(트램 3.5m + 산책로 4m 병존)","55,415"],
       ["도로","15,000","9.6%","기정 결정 유지. 양정로 부지 통과 구간은 보차공존·30km/h","18,501"],
       ["<b>합계</b>","<b>156,460</b>","<b>100%</b>","공원녹지+광장 52,000㎡(33.2%) · 주거 신설 · 상업 42,031→7,960","156,460"]]
      .map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`).join("")}</table>
    <p class="sub">배치는 북에서 남으로 북천 수변공원 → 시청·의회 → 광장(옛 역사) + 공공시설 + 근린시설 → 청년 주거 → 공동캠퍼스 → 모빌리티 허브 → 남측 근린공원이다. 허브에서 옛 역사까지 약 250m, 옛 역사에서 시청까지 약 250m. 순서는 1단계 시굴·횡단축·광장·셔틀(되돌릴 수 있는 것) → 2단계 시청·공공시설 → 3단계 주거·캠퍼스·근린시설이다.</p>`;
  const ev = (id, label, tier) => `<span class="ev" data-card="${id}">${label}${TIER(tier)}</span>`;
  document.getElementById("why").innerHTML = `
    <div class="col"><h3>시청 본청을 옮기는 이유</h3><p class="sub">전략계획이 지목한 원도심 쇠퇴 원인은 시청 이전이었다. 그 원인을 거꾸로 되돌리는 것이 첫 번째 목표다.</p><ol>
      <li><b>12년 동안 5개 계획이 같은 방향을 적었다.</b> 2030 기본계획 “경주역 이전 부지에 행정·문화 복합타운” → 2025 경관계획 “행정복합타운 중점경관관리구역” → 도시재생 전략계획·활성화계획 “분산된 행정기능 통합(2019~2028)” → 고시 2026-8호 “행정복합타운 공공청사 24,987㎡”. ${ev("blocks", "공청1·2 24,987㎡", "T1")}</li>
      <li><b>쇠퇴 원인을 되돌린다.</b> 전략계획은 원도심 쇠퇴 원인으로 “시청 이전과 도시 외연 확장 → 다핵 구조 → 기존 도심 약화”를 세 번 적었다. ${ev("hadmchg", "원도심 10년 −22~−45%", "T2")} ${ev("hwgrid", "격자 종사자 −23%", "T2")}</li>
      <li><b>현재 시청은 이미 한 곳에 있지 않다.</b> 본관은 옛 경주군청 건물이고, 45개 과 중 15개 과가 5개 외부 장소에 있으며 12개 과는 민간 건물을 임차하고 있다. 새로 짓는 것이 아니라 임차를 해소하는 것이다. ${ev("cityhall", "15/45개 과", "T1")}</li>
      <li><b>시청 주변은 저녁까지 사람이 남는 유일한 구역이다.</b> 현재 시청 주변 500m는 원도심 8개 구역 중 유일하게 저녁(18–23시) 비중이 27%이고, 거주 9,145명·직장 8,374명으로 거주와 직장이 비슷하다. ${ev("ffhour", "18–23시 27%", "T2")} ${ev("footfall", "8구역 1ha당", "T2")}</li>
      <li><b>평일 수요를 만든다.</b> 시청은 주 5일, 연 250일 동안 직원 850~950명과 민원인을 합쳐 하루 8,000~9,000명을 계절과 관계없이 데려온다. 관광 수요는 주말과 계절에 따라 크게 변한다. ${ev("visitors", "일별 방문자", "T2")} ${ev("hwmotive", "체류 3시간 미만 79%", "T2")}</li>
      <li><b>시민 응답도 이 방향으로 움직였다.</b> 행정복합타운 26.2%(2015, 2위) → 시청 이전 63.7%(2023, 언론 보도·원문 미확보) → 2025년 ‘문화·쇼핑 거점과 교통 거점’. ${ev("survey3", "설문 3회", "T1")}</li>
    </ol></div>
    <div class="col"><h3>모빌리티 허브를 두는 이유</h3><p class="sub">여객터미널을 옮기는 것이 아니라, 트램·셔틀·동해안 방향 시외버스·자전거·개인형 이동수단·택시를 갈아타는 교통광장을 만들고 환승주차장(P+R)을 붙인다.</p><ol>
      <li><b>기존 계획이 이미 이 자리에 환승센터를 두었다.</b> 2030 교통계획: “복합환승센터는 도심의 경주역·시외버스터미널·KTX역에 설치”, “신경주역~보문 신교통을 원도심 경유로”, 제1순환선 경주역(성동시장). 2025 미래구상 연구 목표 3b: “(옛)경주역 교통거점 기능의 부활”. ${ev("rail", "경주역 폐역 2021.12", "T1")}</li>
      <li><b>승용차 40%라는 전제를 바꾼다.</b> 2007년 조사에서 버스 36%였던 수단 비율을 기본계획은 2030년 승용차 40%·버스 15.6%로 예측했다. 원도심을 지나는 신교통이 없으면 이 예측대로 간다. ${ev("modeshare", "버스 36%→15.6%", "T1")} ${ev("modepurpose", "업무 통행 승용차 50%", "T1")}</li>
      <li><b>주차의 99%가 부설주차장이고 시민 불만 1위가 주차였다.</b> 51,880면 중 공영·노상은 1%다. 2015년 설문 교통 문제 1위는 ‘대규모 주차시설 확충’ 38.8%였다. 허브의 환승주차장이 관광지 주차 집중과 원도심 주차난을 함께 받는다. ${ev("parking", "부설 99%", "T1")} ${ev("parkpub", "공영주차장 면수", "T2")} ${ev("cars", "1,000명당 449대", "T1")}</li>
      <li><b>정체는 특정 시간대에 집중된다.</b> 평일 출퇴근 시간에 정체 구간 비율이 오르고 주말은 다르다. 시청 출퇴근과 관광객 도착을 한 곳에서 분산시킬 수 있다. ${ev("speedhour", "시간대별 속도", "T2")} ${ev("roadvc", "교통량/용량 상위", "T1")}</li>
      <li><b>옛 철도 부지 3.5km는 경주에서 유일하게 교차로가 없는 통로다.</b> 구경주역–황성–석장(동국대)–금장 구간이다. 자율주행 셔틀이나 트램을 놓기 가장 쉬운 선형이고, 2025년 설문의 대안 선호 1위가 ‘자율주행 무료버스’(18/63명)였다. ${ev("s25_transit_alt", "대안 선호", "T2")} ${ev("bus", "시내버스 5년간 정체", "T1")}</li>
      <li><b>교류가 많은 도시는 울산·포항이다.</b> 동해안 방향(포항·울산·감포) 시외버스만 이곳에서 받고, 경부 방향은 노서동 터미널에 남긴다. 그래야 시외버스가 원도심을 관통하지 않는다. ${ev("s25_friendly_cities", "울산 40 · 포항 40", "T2")}</li>
    </ol></div>`;
  document.getElementById("counter-body").innerHTML = `<table class="t"><tr><th>반대 의견 · 불확실한 점</th><th>대응 · 현재 상태</th></tr>
    <tr><td>동천동 상권이 비게 된다</td><td>맞는 지적이다. 보건소는 동천동에 남기고 확장하며, 옛 군청 본관은 동천동 주민시설과 공공임대주택으로 쓴다. 임차 해지분은 시장에 흡수된다. 전략계획도 동천동을 “폐선부지와 연계한 시청 일원 활성화” 대상으로 잡아 두었다.</td></tr>
    <tr><td>시청은 낮에만 사람이 있어 밤에는 빈다</td><td>맞는 지적이다. 이 구성에서 밤을 책임지는 용도는 청년 주거 하나뿐이다(숙박은 넣지 않았다). 그래서 약 600~750세대를 600세대 아래로 줄이지 않는 것이 조건이다. 20–34세 순유출과 황남동 청년 비율 7%가 그 수요의 크기를 보여준다.</td></tr>
    <tr><td>2015년 설문 1위는 복합위락시설(44.5%)이었다</td><td>맞는 지적이다. 이 안은 그 수요를 정면으로 받지 않는다. 쇼핑은 근린시설 7,960㎡(성동시장 매장면적의 약 2배, 판매시설 획지당 1,000㎡ 이하)로 제한한다. 백화점·대형 판매시설은 인구 24만 감소 도시에서 유치 사례가 없고, 성동시장을 흡수하며, 주차를 지상으로 밀어내기 때문에 넣지 않았다.</td></tr>
    <tr><td>공공청사라면 높이 제한을 피해 상징 건물을 지을 수 있지 않나</td><td>불가능하다. 20m 상한은 문화유산 주변 높이 기준을 받은 값이라 공공청사도 예외가 없다. 상징성은 광장, 옛 역사(등록문화유산), 발굴 유구 노출창으로 만든다.</td></tr>
    <tr><td>발굴 유물을 보관·전시할 수장고가 왜 없나</td><td>3km 옆에 국립경주박물관 영남권수장고(2019, 9,242㎡, 60만 점, 관람형 전시수장고 포함)가 이미 있고, 발굴 유물은 법적으로 국가귀속이라 시가 가질 소장품이 없다. 시립 수장고는 중복이다. 시가 가질 수 있는 것은 그 자리의 유구뿐이므로, 현상보존 결정이 나면 광장·공원의 노출창으로 보여주고 필요하면 대여 전시한다.</td></tr>
    <tr><td>인구가 줄어드는 도시가 청사를 새로 짓는다</td><td>행정안전부 기준면적(인구 기준) 안에서만 짓고 초과분은 주민 이용 공간으로 돌려야 한다. 증설이 아니라 임차 해소다.</td></tr>
    <tr><td><b>아직 확인되지 않은 것</b></td><td>‘시청 이전 63.7%’(2023 설문)는 언론 보도만 있고 원문을 확보하지 못했다(T4). 본청+의회 인원 800~950명은 가정이다(인사통계 미공개). 옛 철도 부지의 선형은 OSM 자료(T4)이며 지형도면으로 바꿀 예정이다. 매장문화재 시굴 전에는 청사 위치를 확정할 수 없다. 시청 이전은 시 전체 차원의 정치적 결정이므로 부지 데이터만으로 정당화하지 않고, 대안 비교에서 ‘시청 있음/없음’ 두 경우를 모두 계산해 비교한다.</td></tr></table>`;
  for (const G of GROUPS) {
    const cs = CARDS.filter((c) => c.g === G.id); if (!cs.length) continue;
    chips.appendChild($(`<a href="#g-${G.id}" data-g="${G.id}">${G.title}<small>${cs.length}</small></a>`));
    const sec = $(`<section class="sec" id="g-${G.id}"><div class="eyebrow">${cs.length}장</div><h2>${G.title}</h2>${G.read ? `<p class="read">${G.read}</p>` : ""}<div class="cn-grid"></div></section>`);
    const grid = sec.querySelector(".cn-grid");
    for (const c of cs) {
      const art = $(`<article class="cn ${c.size || ""}" data-card="${c.id}" tabindex="0" role="button"><div class="k">${TIER(c.tier)}${G.title}</div><h3>${c.t}</h3><p class="take">${c.take || ""}</p><div class="thumb ${c.html && !c.opt ? "htm" : ""}"></div><p class="more">자세히 보기 →</p></article>`);
      grid.appendChild(art);
      const th = art.querySelector(".thumb");
      if (c.opt) { th._opt = c.opt; lazy.observe(th); } else if (c.html) th.innerHTML = c.html;
    }
    main.appendChild(sec);
  }
  const links = [...chips.querySelectorAll("a")]; const secs = [...document.querySelectorAll("section.sec")];
  const io = new IntersectionObserver((es) => { for (const e of es) if (e.isIntersecting) links.forEach((a) => a.classList.toggle("on", a.getAttribute("href") === "#" + e.target.id)); }, { rootMargin: "-25% 0px -65% 0px" });
  secs.forEach((x) => io.observe(x));
  document.addEventListener("click", (e) => { const t = e.target.closest("[data-card]"); if (t) { e.preventDefault(); open(t.dataset.card); } });
  document.addEventListener("keydown", (e) => { if (e.key === "Enter" && e.target.matches("[data-card]")) open(e.target.dataset.card); });
  window.addEventListener("resize", () => charts.forEach((c) => c.resize()));
}

// ---------------------------------------------------------------- 상세 다이얼로그
const dlg = document.getElementById("dlg"); let dlgChart = null; let cur = null;
function open(id) {
  const c = byId[id]; if (!c) return; cur = id;
  const G = GROUPS.find((g) => g.id === c.g);
  document.getElementById("dlg-group").innerHTML = `${TIER(c.tier)}${G?.title || ""}`;
  document.getElementById("dlg-title").textContent = c.t;
  document.getElementById("dlg-lead").textContent = c.lead || c.take || "";
  document.getElementById("dlg-note").textContent = c.note || (c.lead ? c.take : "");
  document.getElementById("dlg-src").innerHTML = c.src ? `${TIER(c.tier)}${c.src}` : "";
  const links = document.getElementById("dlg-links"); links.innerHTML = c.map ? `<a href="./index.html#layer=${c.map}">지도에서 이 자료 보기 →</a>` : "";
  const ch = document.getElementById("dlg-chart"), hh = document.getElementById("dlg-html");
  if (dlgChart) { dlgChart.dispose(); dlgChart = null; } ch.innerHTML = ""; hh.innerHTML = c.dlg_html || (c.html && !c.opt ? c.html : "");
  if (!dlg.open) dlg.showModal();
  dlg.scrollTop = 0;
  if (c.opt) { dlgChart = echarts.init(ch, "gj"); dlgChart.setOption({ animationDuration: reduced ? 0 : 400, ...c.opt });
    // showModal 직후에는 컨테이너 폭이 0으로 읽혀 캔버스 폭이 0이 된다 → 레이아웃 뒤 한 번 더 크기 맞춤(rAF는 숨은 창에서 멈추므로 setTimeout 병행)
    const fix = () => { if (dlgChart && dlgChart.getWidth() === 0) dlgChart.resize(); }; requestAnimationFrame(fix); setTimeout(fix, 30); setTimeout(fix, 300); }
}
const step = (d) => { const i = CARDS.findIndex((c) => c.id === cur); const n = CARDS[(i + d + CARDS.length) % CARDS.length]; open(n.id); };
document.getElementById("dlg-prev").onclick = () => step(-1);
document.getElementById("dlg-next").onclick = () => step(1);
document.getElementById("dlg-close").onclick = () => dlg.close();
dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); });
dlg.addEventListener("close", () => { if (dlgChart) { dlgChart.dispose(); dlgChart = null; } });
window.addEventListener("keydown", (e) => { if (!dlg.open) return; if (e.key === "ArrowRight") step(1); if (e.key === "ArrowLeft") step(-1); });
window.addEventListener("resize", () => dlgChart && dlgChart.resize());

main_();
