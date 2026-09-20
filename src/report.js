// 구경주역 통계 리포트 — 카드뉴스 판 (2026-09-21)
// 구조: ① 목표·이유·근거(hero) ② 그룹 칩 ③ 카드 격자(썸네일 차트 + 한 줄 요지) ④ 클릭 → 상세 다이얼로그(큰 차트 + 읽는 법 + 보이는 것 + 출처)
// 지도 탭 '분석' 카드는 전부 여기에도 있다(같은 데이터 파일). 무거운 GeoJSON은 pipeline/build_report_map_stats.py 가 숫자만 뽑아 map_stats.json 으로 준다.
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
  { id: "site", title: "부지와 규제", read: "156,460㎡에 무엇이 정해져 있고 무엇이 막혀 있나 — 획지·높이·문화유산·노후도." },
  { id: "people", title: "사람", read: "인구는 계획과 반대로 줄고, 늙고, 청년은 매년 빠져나간다. 어디에 누가 사는지." },
  { id: "work", title: "일과 상권", read: "제조업 고용 도시이자 관광 도시. 원도심 200m 안의 15배 낙차와 7년의 회전." },
  { id: "move", title: "이동", read: "버스 36%에서 승용차 40%로 뒤집힌 전제, 99% 부설주차, 정체 시간대." },
  { id: "visit", title: "관광·경관·예술", read: "방문객은 늘지만 시민이 꼽는 경관은 황리단길. 예술인 675명의 특이한 구성." },
  { id: "voice", title: "시민의 목소리", read: "2015 · 2023 · 2025 세 번의 설문과 7년의 모니터링 설문. 숫자 비교 금지, 방향만." },
  { id: "sources", title: "출처", read: "" },
];
const CARDS = []; const byId = {};
function add(c) { c.g = c.g || "site"; CARDS.push(c); byId[c.id] = c; }

// ---------------------------------------------------------------- 데이터
async function j(p) { try { return await fetch(`${base}data/${p}`, { cache: "no-cache" }).then((r) => (r.ok ? r.json() : null)); } catch { return null; } }
async function main_() {
  const [R, HW, AR, Y, NAT, VIS, TH, TC, MS] = await Promise.all(["report_stats.json", "hwango_report.json", "arts_stats.json", "youth.json", "nationality.json", "visitors.json", "traffic_hist_summary.json", "traffic_congested.json", "map_stats.json"].map(j));
  const X = R.extras; const p26 = R.pop_actual.pop_2026_08;
  const FF = ["A_hwango_grid32", "B_haengbok_hwangchon_digitized", "C_zone_buffer300", "D_zone", "E_center_r300", "F_cityhall_r500", "G_seongdong_market_r200", "H_hwangridan_r300"];
  const AC = { A_hwango_grid32: C.green, B_haengbok_hwangchon_digitized: C.gray, C_zone_buffer300: C.green2, D_zone: C.red, E_center_r300: C.green3, F_cityhall_r500: "#0f3d34", G_seongdong_market_r200: C.orange, H_hwangridan_r300: C.purple };
  const lo = (k) => parseInt(String(k).replace("+", "").split("-")[0]);

  // ======================= 부지와 규제
  if (MS?.blocks) add({ id: "blocks", g: "site", t: "지구단위계획 획지 — 도면에서 잰 면적과 고시문", take: "결정도를 벡터로 옮겨 잰 면적이 고시문과 ±4% 안에서 맞는다 → 좌표 변환이 맞았다는 증거.", size: "m", tier: "T1", src: MS.blocks.src,
    lead: "고시 제2026-8호 지형도면을 좌표등록하고 채움색으로 획지를 잘라낸 뒤 면적을 쟀다. 회색이 고시문 수치, 초록이 도면에서 잰 값이다.",
    note: "상1~3(상업)·공청1~2(공공청사)·문화1·주1(주차장)·근린공원 3곳. 공청1+공청2 = 24,987㎡가 결정도가 잡아둔 청사 자리다. 시청 본청은 연면적 38,000~45,000㎡가 필요해 이 획지로는 모자란다(§시청 구성).",
    opt: { grid: { left: 4, right: 60, top: 26, bottom: 4, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "㎡" }, xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: MS.blocks.rows.map((r) => r[0]), axisLabel: { color: C.ink, fontSize: 12 } },
      series: [{ name: "고시문", type: "bar", data: MS.blocks.rows.map((r) => r[3]), color: C.gray2, barGap: "-55%", barCategoryGap: "35%" }, { name: "도면 추출", type: "bar", data: MS.blocks.rows.map((r) => r[2]), color: C.green, label: { show: true, position: "right", fontSize: 11, color: C.ink2, formatter: (d) => fmt(d.value) } }] }, map: "blocks" });
  if (MS?.godo) add({ id: "godo", g: "site", t: "고도지구 — 높이 상한별 면적", take: "부지는 도심20m지구 146,489㎡ + 15m지구 11,729㎡. 20m는 황오동삼층석탑 현상변경허용기준 수용값이라 청사도 예외가 없다.", tier: "T1", src: MS.godo.src,
    lead: "경주 도심·구정 고도지구 폴리곤(V-World)에 경북고시 2020-479호의 지구명·높이를 붙여 높이별 면적(ha)을 합쳤다. ‘미확인’은 2020년 도면 범위 밖이라 높이를 못 붙인 폴리곤이다.",
    note: "도심36m(1,006ha)·도심10m(1,082ha)·도심20m(834ha)가 대부분이고, 원도심 핵심은 20m 이하. 랜드마크를 높이로 만들 수 없는 땅이라는 뜻이다.",
    opt: hbar(MS.godo.rows.map((r) => r[0]), MS.godo.rows.map((r) => r[1]), { unit: "ha", top: 9, colors: MS.godo.rows.map((r) => ({ "36m": "#7f0000", "25m": "#b30000", "20m": "#d7301f", "15m": "#ef6548", "12m": "#fc8d59", "10m": "#fdbb84", "7.5m": "#fdd49e", "최저고도": "#2c7bb6" }[r[0]] || "#bdbdbd")) }), map: "godo" });
  if (MS?.reg_areas) add({ id: "regareas", g: "site", t: "규제 영역 13종 — 법정 경계 폴리곤", take: "역사문화환경보존지역 6,892ha·국가지정문화유산구역 3,940ha·보호지구 1,253ha. 3종만 필지 근사.", tier: "T1", src: MS.reg_areas.src,
    lead: "V-World 토지이용규제 원본 폴리곤에서 종류별 개수와 면적(ha)을 합쳤다. 회색 막대는 V-World에 레이어가 없어 필지 외곽으로 근사한 3종(특별보존·보존육성·중점경관).",
    note: "부지에 직접 걸리는 것은 역사문화환경보존지역(도심 2,514ha 폴리곤 + 황오동삼층석탑 보존지역 17.9ha)이고, 황오동삼층석탑(문화재자료 8호) 자체가 구역 안에 있다. 문화유산구역·보호지구·방화지구는 구역 안에 없다.",
    opt: hbar(MS.reg_areas.rows.map((r) => r[0]), MS.reg_areas.rows.map((r) => r[2]), { unit: "ha", top: 13, colors: MS.reg_areas.rows.map((r) => (r[3].startsWith("법정") ? C.orange : C.gray2)) }), map: "reg_areas" });
  if (MS?.reg_layers) add({ id: "reglayers", g: "site", t: "규제 겹 수 — 필지 7,616개", take: "2겹이 4,019필지로 가장 많고, 4겹(고도보존+문화유산+지구단위 전부)은 148필지.", tier: "T1", src: MS.reg_layers.src,
    lead: "필지마다 토지이용계획 항목을 읽어 CLAUDE 4겹(①용도지역·지구 ②고도보존육성지구 ③문화유산법 보존지역·지정구역 ④지구단위계획)을 셌다. ‘접함’은 규제가 아니라 제외했다.",
    note: `개별 항목 필지 수: 고도지구 ${fmt(MS.reg_layers.flags.reg_godo)} · 보존지역 ${fmt(MS.reg_layers.flags.reg_heritage)} · 특별보존 ${fmt(MS.reg_layers.flags.reg_special)} · 보존육성 ${fmt(MS.reg_layers.flags.reg_boyuk)} · 문화유산구역 ${fmt(MS.reg_layers.flags.reg_cult)} · 지구단위 ${fmt(MS.reg_layers.flags.reg_jdp)}. 이전 버전(접함 포함)은 3겹 이상이 4,496필지로 과대였다.`,
    opt: { grid: { left: 8, right: 16, top: 8, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "필지" }, xAxis: { type: "category", data: MS.reg_layers.dist.map((d) => d[0] + "겹") }, yAxis: { type: "value" },
      series: [{ type: "bar", data: MS.reg_layers.dist.map((d, i) => ({ value: d[1], itemStyle: { color: ["#e9f0ec", "#b7d7c2", "#e3a857", "#b23a2c"][i] } })), label: { show: true, position: "top", formatter: (d) => fmt(d.value) } }] }, map: "reg" });
  if (MS?.bldg_age) add({ id: "bldgage", g: "site", t: "건물 노후도 — 사용승인 경과연수", take: `건축물대장이 있는 ${fmt(MS.bldg_age.n)}필지 중 20년 이상이 ${MS.bldg_age.pct20}%, 30년 이상 ${MS.bldg_age.pct30}%. 쇠퇴진단 기준(20년↑ 50%)을 크게 넘는다.`, tier: "T1", src: MS.bldg_age.src,
    lead: "성동·황오·노서·노동·성건 5개 법정동의 건축물대장을 필지에 붙여 사용승인 경과연수를 셌다. 동천동·인왕동은 아직 대장을 못 받아 빠져 있다.",
    note: `사용승인일이 없는 대장 ${MS.bldg_age.n_unknown}필지(옛 역사·철도시설)는 제외. 도시재생 활성화지역 지정 요건은 ‘20년 이상 노후건축물 50% 이상’이다.`,
    opt: hbar(MS.bldg_age.bins.map((b) => b[0]), MS.bldg_age.bins.map((b) => b[1]), { unit: "필지", top: 5, colors: ["#e8f3e6", "#c7e0bd", "#f6d68a", "#e9975a", "#c8452b"] }), map: "parcels" });
  {
    const H = Object.fromEntries(X.heritage.map((h) => [h.k, h]));
    add({ id: "heritage", g: "site", t: "땅속 — 매장문화재 시굴 145,879㎡", take: "지표조사 148,770㎡ 중 145,879㎡가 시굴 대상. 시굴 3.06억·54일, 정밀발굴은 63~80억·630~700일. 2m 미만 성토 공원·주차장은 발굴 유예.", size: "m", tier: "T2", src: X.sources.heritage,
      lead: "2022년 지표조사와 2026년 혁신포럼의 시굴조사 추진계획에서 옮긴 수치다. 부지 거의 전부가 유존지역(성동동사지Ⅱ 40,882 + 유물산포지 104,997㎡)이다.",
      note: "지하 주차장·지하층 계획의 상한을 정하는 숫자다. 1단계에 지하 구조물을 넣을 수 없고, 청사 위치는 시굴 뒤에 확정해야 한다. 성토 2m 미만 공원·주차장은 발굴을 유예할 수 있어 1단계는 지상 광장·공원·노반 활용이 합리적이다.",
      html: `<div class="tiles">${[["시굴조사 필요 면적", fmt(H["시굴조사 필요 면적"].v), "㎡", H["시굴조사 필요 면적"].note], ["기조사 면적", fmt(H["기조사 면적(2002~2004 발굴·시굴)"].v), "㎡", "2002~2004 발굴·시굴"], ["시굴 1단계(안)", fmt(H["시굴조사 1단계(안) 면적"].v), "㎡", H["시굴조사 1단계(안) 면적"].note], ["시굴 비용", "3.06", "억", "현장 54일"], ["정밀발굴 비용", "63~80", "억", "현장 630~700일"], ["발굴 유예", "2m", "미만 성토", "공원·주차장"]].map(([k, v, u, d]) => `<div class="tile"><div class="k">${k}</div><div class="v">${v}<small>${u}</small></div><div class="d">${d}</div></div>`).join("")}</div>` });
  }
  if (MS?.cityhall) add({ id: "cityhall", g: "site", t: "지금의 시청 — 45개 과 중 15개 과가 청사 밖", take: "본관은 1995년 통합 전 옛 경주군청. 9개 과는 기린빌딩, 3개 과는 동원빌딩 임차. 문서고는 실내체육관.", size: "m", tier: "T1", src: MS.cityhall.src,
    lead: "경주시 홈페이지 청사안내(2026-09-02)에서 본청 과가 실제로 어디 있는지 세었다. 막대는 장소별 과 수, 빨강은 민간 임차.",
    note: "행안부 공유재산 운영기준상 임차면적은 청사 기준면적에 산입되고 전세권 설정이 의무다. 즉 ‘임시 청사’가 아니라 ‘청사 부족을 임차로 메우는 상태’이며, 이것이 이전의 T1 근거다. 본청+의회 800~950명(가정) × 30~35㎡ = 28,000~33,000㎡ + 법정의무·주민편의 = 38,000~45,000㎡.",
    opt: hbar(MS.cityhall.rows.map((r) => r.name), MS.cityhall.rows.map((r) => r.n_depts), { unit: "개 과", top: 8, colors: MS.cityhall.rows.map((r) => (/임차/.test(r.own) ? C.red : r.cls === "main" ? C.green : C.gray)) }), map: "cityhall_sites" });
  if (MS?.parking_pub) add({ id: "parkpub", g: "site", t: `공영주차장 ${MS.parking_pub.rows.length}곳 ${fmt(MS.parking_pub.total)}면`, take: "원도심 공영주차 총량. 전체 주차 51,880면의 99%가 부설이라 공영은 1% 남짓이다.", tier: "T2", src: MS.parking_pub.src,
    lead: "경주시시설관리공단이 운영하는 공영주차장(노상·민영 제외)의 면수다.", note: "모빌리티 허브의 P+R 규모를 정할 때 ‘지금 원도심이 공영으로 얼마를 가지고 있나’의 기준선. 2015 설문의 교통 문제 1위는 ‘대규모 주차시설 확충’ 38.8%였다.",
    opt: hbar(MS.parking_pub.rows.map((r) => r[0]), MS.parking_pub.rows.map((r) => r[1]), { unit: "면", top: 10, color: C.gray }), map: "parking_pub" });
  if (MS?.tourism_complex) add({ id: "tcomplex", g: "site", t: "관광단지 4곳 — 보문 850ha가 원도심 밖에 있다", take: "보문·마우나오션·감포해양·북경주 웰니스. 관광 숙박 수요는 원도심 밖 단지가 받고, 원도심은 통과 동선이 됐다.", tier: "T1", src: "V-World LT_C_UO601 · 이름은 경북 고시번호로 토지이음 대조",
    lead: "관광진흥법 관광단지 지정 경계의 면적(ha). 이름은 V-World 속성에 없어 마지막 고시번호를 토지이음 고시정보로 대조해 확정했다.",
    opt: hbar(MS.tourism_complex.map((r) => r[0]), MS.tourism_complex.map((r) => r[1]), { unit: "ha", top: 4, color: "#0e8a7a" }) });

  // ======================= 사람
  {
    const yrsAll = [...new Set([...R.pop_doc.years, ...R.pop_actual.years, ...R.pop_plan.years, "2026"])].sort();
    const ser = (yrs, vals) => yrsAll.map((y) => { const i = yrs.indexOf(y); return i < 0 ? null : vals[i]; });
    add({ id: "popplan", g: "people", t: "계획은 320,000명을 그렸고, 도시는 242,512명이다", take: "2030 기본계획 +18% 성장선과 실제 주민등록 감소선을 한 그래프에. 차이는 −24%.", size: "l", tier: "T1", src: `${R.pop_doc.src} / ${R.pop_actual.src}`,
      lead: "회색은 기본계획이 수록한 통계연보(2003–13), 검정은 주민등록(2011–25), 초록 점선은 계획인구 단계 목표, 빨강 점은 2026년 8월 실제. 두 통계는 기준이 달라 2011~13년에 약 1만 명 차이가 나므로 수준이 아니라 방향을 읽는다.",
      note: "계획인구는 자연증가 262,490 + 사회적증가 53,769(산업단지·도시개발·주택·신경주역세권)로 짜였다. 사회적증가의 전제였던 사업들이 인구를 만들지 못했다.",
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: yrsAll, axisLabel: { interval: 2 } }, yAxis: { type: "value", min: 230000, max: 330000, axisLabel: { formatter: (v) => v / 1000 + "k" } },
        series: [{ name: "통계연보", type: "line", data: ser(R.pop_doc.years, R.pop_doc.total), color: C.gray, connectNulls: true }, { name: "주민등록", type: "line", data: ser(R.pop_actual.years, R.pop_actual.total), color: C.ink, lineStyle: { width: 2.5 }, connectNulls: true }, { name: "2030 계획인구", type: "line", data: ser(R.pop_plan.years, R.pop_plan.total), color: C.green, lineStyle: { width: 2, type: "dashed" }, symbolSize: 7, connectNulls: true }, { name: "2026.08", type: "scatter", data: [["2026", p26]], color: C.red, symbolSize: 10, label: { show: true, position: "right", formatter: fmt(p26), fontSize: 11, color: C.red } }] } });
    add({ id: "aging", g: "people", t: "고령화 — 65세 이상 30.0%", take: "계획이 2030년에나 올 것으로 본 고령화율에 2026년에 이미 도달했다.", tier: "T1", src: `${R.aging.src} / ${R.age_projection.src}`,
      lead: "검정은 통계연보 실적과 2026년 주민등록, 초록 점선은 기본계획의 자연증가 전망.",
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: [...R.aging.years, "2015", "2020", "2025", "2026", "2030"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" }, max: 40 },
        series: [{ name: "실적", type: "line", data: [...R.aging.pct65, null, null, null, R.aging.pct65_2026, null], color: C.ink, lineStyle: { width: 2.5 }, connectNulls: true }, { name: "계획 전망", type: "line", data: [...Array(9).fill(null), R.age_projection.p65[0], ...R.age_projection.p65.slice(1, 4), null, R.age_projection.p65[4]], color: C.green, lineStyle: { type: "dashed" }, connectNulls: true }, { name: "2026.08", type: "scatter", data: [["2026", R.aging.pct65_2026]], color: C.red, symbolSize: 10, label: { show: true, position: "top", formatter: pct(R.aging.pct65_2026), color: C.red, fontSize: 11 } }] } });
    add({ id: "ageproj", g: "people", t: "연령구조 전망 — 부양률 42% → 83%", take: "기본계획 자체의 자연증가 전망에서도 2030년 부양률은 83%다.", tier: "T1", src: R.age_projection.src, lead: "0–14 / 15–64 / 65+ 구성비(%)와 부양률 [(0–14 + 65+)/15–64].",
      opt: { grid: { left: 8, right: 40, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: R.age_projection.years }, yAxis: [{ type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } }, { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" }, splitLine: { show: false } }],
        series: [{ name: "0–14", type: "bar", stack: "a", data: R.age_projection.p0_14, color: C.blue2 }, { name: "15–64", type: "bar", stack: "a", data: R.age_projection.p15_64, color: C.green3 }, { name: "65+", type: "bar", stack: "a", data: R.age_projection.p65, color: C.orange }, { name: "부양률", type: "line", yAxisIndex: 1, data: R.age_projection.dependency, color: C.ink, lineStyle: { width: 2 }, label: { show: true, position: "top", formatter: (d) => d.value + "%", fontSize: 11 } }] } });
    const lzn = Object.keys(R.pop_plan.by_lifezone);
    add({ id: "lifezone", g: "people", t: "생활권별 계획인구 vs 실제", take: `중심생활권 2030 목표 200,000명, 2026 실제 ${fmt(MS?.lifezone?.rows?.[0]?.pop_2026_actual)}명 (${MS?.lifezone?.rows?.[0]?.gap_pct}%).`, tier: "T1", src: `${R.pop_plan.src} / 주민등록 2026-08`,
      lead: "회색 2013 · 초록 2030 계획 · 빨강 2026 실제(행정동 합). 중심생활권 = 황남·성건·황오·월성·선도·황성·용강·동천·불국·보덕·현곡·천북.",
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: lzn }, yAxis: { type: "value", axisLabel: { formatter: (v) => v / 1000 + "k" } },
        series: [{ name: "2013", type: "bar", data: lzn.map((z) => R.pop_plan.by_lifezone[z][0]), color: C.gray2 }, { name: "2030 계획", type: "bar", data: lzn.map((z) => R.pop_plan.by_lifezone[z][4]), color: C.green }, { name: "2026 실제", type: "bar", data: lzn.map((z) => MS?.lifezone?.rows?.find((r) => r.name === z)?.pop_2026_actual ?? null), color: C.red, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => (d.value ? (d.value / 1000).toFixed(0) + "k" : "") } }] }, map: "lifezone" });
    const sc = R.pop_plan_components.social;
    add({ id: "popcomp", g: "people", t: "320,000의 구성 — 사회적증가 53,769명은 어디서 오나", take: "산업단지·도시개발·주택건설·신경주역세권이 5만 명을 데려온다는 가정이었다.", tier: "T1", src: R.pop_plan_components.src,
      opt: hbar(["자연증가(내국인)", "일반산업단지", "도시개발사업", "주택건설사업", "신경주역세권", "자연증가(외국인)"], [252490, sc["일반산업단지"], sc["도시개발사업"], sc["주택건설사업"], sc["신경주역세권"], 10000], { unit: "명", color: C.green2 }) });
  }
  if (MS?.hadm) {
    const age = MS.hadm.city_age, keys = Object.keys(age).sort((a, b) => lo(a) - lo(b)), tot = keys.reduce((s, k) => s + age[k], 0), o65 = keys.filter((k) => lo(k) >= 65).reduce((s, k) => s + age[k], 0);
    add({ id: "pyramid", g: "people", t: "경주시 연령 피라미드 — 2026.08", take: `${fmt(tot)}명, 65세 이상 ${pct(o65 / tot * 100)}. 50–60대가 가장 두껍고 20대 아래로 급히 얇아진다.`, tier: "T2", src: MS.hadm.src, lead: "5세 계급 주민등록 인구. 주황 = 65세 이상, 파랑 = 0–14세. 지도에서는 행정동을 클릭하면 그 동으로 바뀐다.",
      opt: { grid: { left: 8, right: 40, top: 4, bottom: 4, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "value", show: false }, yAxis: { type: "category", data: keys.map((k) => k.replace(" - ", "–").replace("세", "")), axisLabel: { fontSize: 10 } },
        series: [{ type: "bar", data: keys.map((k) => ({ value: age[k], itemStyle: { color: lo(k) >= 65 ? C.orange : lo(k) <= 10 ? C.blue2 : C.green } })), barCategoryGap: "20%" }] }, map: "pop_total" });
    const yy = Object.keys(MS.hadm.city_yearly);
    add({ id: "yearly", g: "people", t: "행정동 합 인구 2011–2025", take: "22개 행정동 합계. 2015년 이후 해마다 줄어 10년 −6.1%.", tier: "T2", src: MS.hadm.src,
      opt: { grid: { left: 8, right: 16, top: 8, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: yy }, yAxis: { type: "value", scale: true, axisLabel: { formatter: (v) => v / 1000 + "k" } }, series: [{ type: "line", data: yy.map((y) => MS.hadm.city_yearly[y]), color: C.green, areaStyle: { opacity: .12 }, lineStyle: { width: 2.5 } }] } });
    const rows = MS.hadm.rows.filter((r) => r.pop);
    const by65 = [...rows].sort((a, b) => b.pct_65 - a.pct_65);
    add({ id: "hadm65", g: "people", t: "행정동별 65세 이상 비율", take: `황남동 ${pct(by65[0].pct_65)}로 1위, 원도심 4개 동이 모두 상위. 황성동 ${pct(rows.find((r) => r.hadm === "황성동")?.pct_65)}.`, tier: "T2", src: MS.hadm.src, lead: "진한 색 = 부지가 속한 원도심 4개 동(황오·성건·황남·월성).",
      opt: hbar(by65.map((r) => r.hadm), by65.map((r) => r.pct_65), { unit: "%", top: 22, fmtV: (v) => pct(v), colors: by65.map((r) => (["황오동", "성건동", "황남동", "월성동"].includes(r.hadm) ? C.red : C.orange2)) }), map: "pop_65" });
    add({ id: "hadmchg", g: "people", t: "행정동별 10년 인구변화 2015→2025", take: "용강동 +32.8%만 늘고 원도심은 −22~−45%. 황오동은 중부동 합산 후 −32.7%.", tier: "T2", src: MS.hadm.src, lead: "2025년 폐지된 중부동은 2011~2024 시계열을 황오동에 합산해 계산했다(합산 전에는 +20.1%라는 아티팩트가 나온다).",
      opt: (() => { const s = [...rows].sort((a, b) => a.chg_10y_pct - b.chg_10y_pct); return hbar(s.map((r) => r.hadm), s.map((r) => r.chg_10y_pct), { top: 22, fmtV: (v) => (v > 0 ? "+" : "") + pct(v), colors: s.map((r) => (r.chg_10y_pct > 0 ? C.green : ["황오동", "성건동", "황남동", "월성동"].includes(r.hadm) ? C.red : C.orange2)) }); })(), map: "pop_chg" });
    const FRK = [["fr_worker", "외국인근로자"], ["fr_marriage", "결혼이민자"], ["fr_student", "유학생"], ["fr_diaspora", "외국국적동포"], ["fr_other", "기타외국인"], ["fr_naturalized", "귀화자"], ["fr_children", "자녀"]];
    const frv = FRK.map(([k]) => rows.reduce((s, r) => s + (+r[k] || 0), 0)); const frt = frv.reduce((a, b) => a + b, 0);
    add({ id: "foreign", g: "people", t: `외국인주민 ${fmt(frt)}명 — 유형별`, take: "성건동 7,170명(37.5%, 동포·유학생), 외동읍 6,100명(근로자). 원도심에서는 성건동만 두드러진다.", tier: "T2", src: "행안부 지방자치단체 외국인주민 현황 2024.11 (KOSIS DT_110025_A033_A, 읍면동)",
      lead: "행안부 외국인주민 현황(2024.11) 읍면동 합. 근로자·결혼이민·유학생·외국국적동포·기타 + 귀화 + 자녀.",
      opt: hbar(FRK.map((k) => k[1]), frv, { unit: "명", top: 7, color: "#980043" }), map: "fr_pct" });
    if (NAT) { const nr = Object.entries(NAT.nationality).filter(([k]) => k !== "계").sort((a, b) => b[1] - a[1]).slice(0, 12);
      add({ id: "nation", g: "people", t: `국적별 등록외국인 ${fmt(NAT.nationality["계"])}명`, take: "베트남 3,437 · 중국 1,393 · 우즈베키스탄 1,148 · 카자흐스탄 1,129. 시군구 단위만 공표.", tier: "T2", src: `법무부 등록외국인 통계 ${NAT.prd} (KOSIS DT_1B040A9C)`, lead: "상위 12개국. 읍면동 단위 국적 통계는 공개되지 않는다. 행안부 22,467과 법무부 15,621은 정의(귀화·자녀 포함 여부)가 달라 합치면 안 된다.",
        opt: hbar(nr.map((r) => r[0].replace("(연방)", "")), nr.map((r) => r[1]), { unit: "명", top: 12, color: C.purple }) }); }
  }
  if (Y) {
    const dong = Y.dong.slice(0, 12); const core = ["황오동", "성건동", "황남동", "월성동"];
    add({ id: "ydong", g: "people", t: "청년(20–34세)은 어디 사나", take: `경주시 ${fmt(Y.city_y2034)}명(${Y.city_pct}%). 황성·동천·용강·현곡 4곳에 45%. 원도심 4개 동은 4,255명, 그중 59%가 대학이 있는 성건동.`, size: "m", tier: "T2", src: Y.dong_src, lead: "행정동별 20–34세 주민 수(막대)와 비율(숫자). 진한 색은 부지가 속한 원도심 4개 동.",
      note: "황남동은 7.0%로 시 평균의 절반 — 관광객이 가장 많이 걷는 동에 청년이 가장 적게 산다. ‘관광 업종 증가 ≠ 정주’의 실물 증거.",
      opt: { ...hbar(dong.map((x) => x.hadm), dong.map((x) => x.n), { top: 12 }), series: [{ type: "bar", data: dong.map((x) => ({ value: x.n, itemStyle: { color: core.includes(x.hadm) ? "#6e016b" : "#9ebcda" } })), barCategoryGap: "28%", label: { show: true, position: "right", fontSize: 11, color: C.ink2, formatter: (p) => `${fmt(p.value)} · ${dong[p.dataIndex].pct}%` } }] }, map: "pop_y2034" });
    const a = Object.fromEntries(Y.age_emp), r = Object.fromEntries(Y.age_rate);
    add({ id: "yemp", g: "work", t: "경주시 취업자 145.1천명 — 산업·직업 (전 연령)", take: `15–29세 취업자 ${a["15 - 29세"]}천명, 고용률 ${r["15 - 29세"]}% (30–49세 ${r["30 - 49세"]}%). 청년만의 산업 구성은 시군구 단위로 공표되지 않는다.`, size: "m", tier: "T2", src: Y.emp_src,
      lead: "지역별고용조사 2026 상반기. 왼쪽 산업 6대, 오른쪽 직업 6대(천명). 청년×산업 교차는 통계청 MDIS 마이크로데이터 신청이 필요하다.",
      note: "농림어업 17.5천명은 65세 이상 취업자 30.9천명이 있는 구조라 대부분 고령층으로 추정되고, 제조업(외동·건천 공단)과 숙박음식(관광)이 청년 흡수처일 가능성이 크다 — 이는 추정이다.",
      opt: (() => { const ind = Y.industry.map(([k, v]) => [k.replace(/\s*\(.*?\)\s*/g, "").replace("사업·개인·공공서비스 및 기타", "사업·개인·공공서비스"), v]); const occ = Y.occupation.map(([k, v]) => [k.replace(" 및 관련종사자", "").replace(" 종사자", "").replace("기능·기계조작·조립", "기능·기계조작"), v]);
        return { grid: [{ left: 8, right: "56%", top: 26, bottom: 4, containLabel: true }, { left: "56%", right: 40, top: 26, bottom: 4, containLabel: true }], title: [{ text: "산업 (천명)", left: 0, top: 0, textStyle: { fontSize: 11.5, color: C.ink3, fontWeight: 500 } }, { text: "직업 (천명)", left: "54%", top: 0, textStyle: { fontSize: 11.5, color: C.ink3, fontWeight: 500 } }], tooltip: { trigger: "axis", valueFormatter: (v) => v + "천명" },
          xAxis: [{ type: "value", show: false, gridIndex: 0 }, { type: "value", show: false, gridIndex: 1 }], yAxis: [{ type: "category", inverse: true, gridIndex: 0, data: ind.map((x) => x[0]), axisLabel: { fontSize: 11, color: C.ink } }, { type: "category", inverse: true, gridIndex: 1, data: occ.map((x) => x[0]), axisLabel: { fontSize: 11, color: C.ink } }],
          series: [{ type: "bar", xAxisIndex: 0, yAxisIndex: 0, data: ind.map((x) => x[1]), color: C.green, label: { show: true, position: "right", fontSize: 11 }, barCategoryGap: "30%" }, { type: "bar", xAxisIndex: 1, yAxisIndex: 1, data: occ.map((x) => x[1]), color: C.gray, label: { show: true, position: "right", fontSize: 11 }, barCategoryGap: "30%" }] }; })() });
    const bands = ["20-24세", "25-29세", "30-34세", "35-39세"]; const col = { "20-24세": "#980043", "25-29세": "#dd1c77", "30-34세": "#df65b0", "35-39세": "#9ebcda" };
    add({ id: "ymig", g: "people", t: "청년은 남아 있나 — 연령대별 순이동 2020–2025", take: `20–34세는 매년 순유출(${Y.net["20-34세"].map(fmt).join(" / ")}명). 20–24세가 가장 크다. 2025 전체 +860은 30대 이상 유입.`, size: "m", tier: "T2", src: Y.mig_src, lead: "해마다 경주로 들어온 사람에서 나간 사람을 뺀 값. 선은 연령대, 회색 막대는 전체.",
      opt: { grid: { left: 8, right: 12, top: 30, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => sgn(v) + "명" }, legend: { top: 0, left: 0 }, xAxis: { type: "category", data: Y.mig_years }, yAxis: { type: "value" },
        series: [...bands.map((b) => ({ name: b, type: "line", data: Y.net[b], lineStyle: { width: 2, color: col[b] }, itemStyle: { color: col[b] } })), { name: "전체", type: "bar", data: Y.net["계"], itemStyle: { color: "rgba(120,130,125,.25)" }, barWidth: "40%" }] } });
  }
  if (MS?.decline) {
    const d = MS.decline.rows.filter((r) => r.old_pct != null).sort((a, b) => b.old_pct - a.old_pct);
    add({ id: "decline", g: "people", t: "쇠퇴진단 2022 — 행정동별 노후건축물 비율", take: `22개 행정동 중 ${MS.decline.rows.filter((r) => r.met === "충족").length}곳이 쇠퇴기준 2개 이상 충족. 황남동 노후 82.0%.`, tier: "T1", src: MS.decline.src, lead: "도시재생 전략계획(2022)의 3지표(인구 감소·사업체 감소·노후건축물 20년↑ 비율). 막대는 노후 비율, 빨강은 ‘충족’.",
      opt: hbar(d.map((r) => r.hadm), d.map((r) => r.old_pct), { top: 22, fmtV: (v) => pct(v), colors: d.map((r) => (r.met === "충족" ? C.red : C.gray2)) }), map: "decline" });
  }
  if (MS?.schools) add({ id: "schools", g: "people", t: `학교 ${MS.schools.rows.reduce((s, r) => s + r[1], 0)}곳 — 유형별`, take: `운영 중 학교·유치원 수. 폐교 ${MS.schools.closed}곳.`, tier: "T2", src: MS.schools.src, opt: hbar(MS.schools.rows.map((r) => r[0]), MS.schools.rows.map((r) => r[1]), { unit: "곳", top: 8, color: C.blue }), map: "schools" });
  if (MS?.religion) add({ id: "religion", g: "people", t: `종교시설 ${fmt(MS.religion.n)}곳 — 종교별`, take: `${MS.religion.rows.slice(0, 3).map((r) => `${r[0]} ${r[1]}`).join(" · ")}. 이슬람 시설은 공식 현황에 별도 항목이 없다.`, tier: "T2", src: MS.religion.src, lead: "경주시 종교시설현황(2025-02) 파일. 오른쪽 숫자는 시설 수. 외국인주민 22,467명 중 이슬람권 국적(우즈벡·카자흐·인도네시아·방글라데시·파키스탄 등) 3,000명 이상이 있지만 종교시설 현황엔 항목이 없다.",
    opt: hbar(MS.religion.rows.map((r) => r[0]), MS.religion.rows.map((r) => r[1]), { unit: "곳", top: 8, color: C.purple2 }), map: "religion" });

  // ======================= 일과 상권
  add({ id: "business", g: "work", t: "사업체·종사자 2009–2013", take: "사업체 +12%, 종사자 +17%. 종사자 기준 2차산업 41.8%는 경북 평균 38.0%보다 높다.", tier: "T1", src: R.business.src,
    opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) }, xAxis: { type: "category", data: R.business.years }, yAxis: [{ type: "value", min: 18000, axisLabel: { formatter: (v) => v / 1000 + "k" } }, { type: "value", min: 90000, axisLabel: { formatter: (v) => v / 1000 + "k" }, splitLine: { show: false } }],
      series: [{ name: "사업체", type: "bar", data: R.business.firms, color: C.green3 }, { name: "종사자(우축)", type: "line", yAxisIndex: 1, data: R.business.workers, color: C.ink, lineStyle: { width: 2.5 } }] } });
  { const ind = R.industry_2013;
    add({ id: "industry13", g: "work", t: "산업구조 2013 — 사업체의 84%가 3차, 종사자의 42%는 2차", take: "경주는 관광도시이면서 제조업 고용 도시다.", tier: "T1", src: ind.src,
      opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: ["경주 사업체", "경주 종사자", "경북 종사자"] }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } },
        series: ["1차", "2차", "3차"].map((k, i) => ({ name: k + "산업", type: "bar", stack: "s", data: [ind.firms_pct[k], ind.workers_pct[k], ind.gb_workers_pct[k]], color: [C.green3, C.orange, C.blue2][i], label: { show: i > 0, position: "inside", fontSize: 10.5, color: "#fff", formatter: (d) => d.value.toFixed(0) } })) } }); }
  if (MS?.stores) add({ id: "stores", g: "work", t: `상가 업소 ${fmt(MS.stores.n)}개 — 대분류`, take: `${MS.stores.rows.slice(0, 3).map((r) => `${r[0]} ${fmt(r[1])}`).join(" · ")}. 폐업은 포함되지 않은 영업중 스냅샷.`, tier: "T2", src: MS.stores.src, lead: "소진공 상가업소(2026-03, S2 창) 대분류별 업소 수. 지도에서는 화면 안 업소만 집계된다.",
    opt: hbar(MS.stores.rows.map((r) => r[0]), MS.stores.rows.map((r) => r[1]), { unit: "개", top: 10, color: C.orange }), map: "stores" });
  add({ id: "footfall", g: "work", t: "유동인구 8구역 — ha당 하루 평균", take: "성동시장 200m 1,175/ha vs 폐역 구역 79/ha — 15배 낙차가 200m 안에 있다.", size: "m", tier: "T2", src: X.sources.footfall, lead: "통신사 추정 유동인구(2025.06~2026.06 일평균)를 같은 정의로 8구역에서 재추출해 넓이(ha)로 나눴다. 빨강이 폐역 구역.",
    note: "행복황촌(B)도 폐선 부지만큼 비어 있다(80/ha). 부지는 지금 ‘비어 있는 땅’이 아니라 ‘사람이 지나가지 않는 땅’이다.",
    opt: hbar(FF.map((k) => X.footfall[k].short), FF.map((k) => X.footfall[k].per_ha), { unit: "/ha", top: 8, colors: FF.map((k) => AC[k]) }), map: "footfall_areas" });
  add({ id: "ffhour", g: "work", t: "하루 중 언제 붐비나 — 시청 500m만 저녁이 길다", take: "어느 구역이든 14–18시가 최고. 시청 주변(F)만 18–23시 비중 27%로 저녁까지 사람이 남는다.", size: "m", tier: "T2", src: X.sources.footfall, lead: "6개 시간대에 전체 유동의 몇 %가 다니는지. 구역 간 차이는 ‘언제’가 아니라 ‘몇 명’에서 난다.",
    note: "시청이 만든 자연실험이다. 시청 500m는 주거 9,145·직장 8,374로 유일한 직주 균형 구역이고, 60대 이상 32%로 가장 젊다(전략계획: “시청주변 상권은 시청사 이전으로 급속하게 형성”).",
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: ["05–09", "09–12", "12–14", "14–18", "18–23", "23–05"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" } },
      series: ["A_hwango_grid32", "D_zone", "F_cityhall_r500", "G_seongdong_market_r200", "H_hwangridan_r300"].map((k) => ({ name: X.footfall[k].short, type: "line", data: X.footfall[k].hourly_pct, color: AC[k], lineStyle: { width: k === "F_cityhall_r500" ? 3 : 1.8 } })) } });
  add({ id: "bizprint", g: "work", t: "동네 가게와 관광객 가게 — 업소 수", take: "폐역 주변(C) 펜션 32→45곳(13개월), 황리단길(H) 카페 51→40곳. 생활 업종은 거의 그대로.", tier: "T2", src: X.sources.biz, lead: "슈퍼·미용실·정육점·약국·백반 같은 생활 업종과 카페·여관·호텔·펜션 같은 관광·체류 업종의 개수를 구역별로 셌다. 대표 11개 업종만이라 상권 전체는 아니다.",
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: FF.map((k) => X.footfall[k].short), axisLabel: { fontSize: 10.5 } }, yAxis: { type: "value" },
      series: [{ name: "생활", type: "bar", stack: "s", data: FF.map((k) => +X.biz_area[k].life_stores_2606), color: C.green }, { name: "관광·체류", type: "bar", stack: "s", data: FF.map((k) => +X.biz_area[k].tour_stores_2606), color: C.orange }] } });
  { const yrs7 = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]; const kp = X.hwango_kpi["주요 상권 유동인구(명, 소상공인365 통신사 추정)"] || {}; const o = X.startup_closure["황오동 사업대상지|창업 건수"] || {}; const c_ = X.startup_closure["황오동 사업대상지|폐업 건수"] || {};
    add({ id: "hwkpi", g: "work", t: "황오동 원도심 7년 — 유동은 줄고 가게는 자주 바뀐다", take: "유동인구 2020 26,536 → 2024 22,646명(−15%). 창업·폐업 회전은 빨라졌다.", tier: "T2", src: X.sources.hwango,
      opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: yrs7 }, yAxis: [{ type: "value" }, { type: "value", scale: true, axisLabel: { formatter: (v) => v / 1000 + "k" }, splitLine: { show: false } }],
        series: [{ name: "창업", type: "bar", data: yrs7.map((y) => o[y]), color: C.green2 }, { name: "폐업", type: "bar", data: yrs7.map((y) => c_[y]), color: C.red }, { name: "유동인구(우축)", type: "line", yAxisIndex: 1, data: yrs7.map((y) => kp[y] ?? null), color: C.ink, lineStyle: { width: 2.5 }, connectNulls: true }] } }); }
  { const ly = Object.keys(X.landprice_avg);
    add({ id: "landprice", g: "work", t: "공시지가 — 2022년까지 오르다 꺾였다", take: "원도심 29필지 평균 2018 대비 2022 +18.7% → 2025 +10.8%. 행복황촌 44곳은 2023 −5.6%.", tier: "T2", src: X.sources.hwango,
      opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => (v == null ? "–" : fmt(v) + "원") }, xAxis: { type: "category", data: ly }, yAxis: [{ type: "value", scale: true, axisLabel: { formatter: (v) => (v / 1e6).toFixed(1) + "M" } }, { type: "value", scale: true, axisLabel: { formatter: (v) => (v / 1e4).toFixed(0) + "만" }, splitLine: { show: false } }],
        series: [{ name: "원도심 29필지", type: "line", data: ly.map((y) => X.landprice_avg[y]), color: C.green, lineStyle: { width: 2.5 } }, { name: "행복황촌 44개소(우축)", type: "line", yAxisIndex: 1, data: ly.map((y) => X.landprice_hwangchon44[y] ?? null), color: C.purple, lineStyle: { type: "dashed" } }] }, map: "landprice_pts" }); }
  add({ id: "elec", g: "work", t: "용도별 전력사용 — 산업용 48%", take: "2013년 전력의 절반이 산업용. 관광도시의 에너지 지문은 공장이다.", tier: "T1", src: R.electricity.src,
    opt: { tooltip: { trigger: "item", formatter: (d) => `${d.name} ${fmt(d.value)} MWh · ${d.percent}%` }, series: [{ type: "pie", radius: ["50%", "78%"], data: [{ name: "산업용", value: R.electricity.industry.at(-1) }, { name: "서비스업", value: R.electricity.service.at(-1) }, { name: "가정용", value: R.electricity.home.at(-1) }, { name: "공공용", value: R.electricity.total.at(-1) - R.electricity.industry.at(-1) - R.electricity.service.at(-1) - R.electricity.home.at(-1) }], color: [C.orange, C.green, C.blue, C.gray2], label: { fontSize: 11.5, color: C.ink2, formatter: "{b} {d}%" }, itemStyle: { borderColor: "#fff", borderWidth: 2 } }] } });
  add({ id: "housing", g: "work", t: "주택보급률 114.8% — 단독주택 60%", take: "집은 남고 사람은 준다. 원도심에 필요한 것은 ‘주택’이 아니라 청년이 살 ‘유형’이다.", tier: "T1", src: R.housing.src,
    opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: R.housing.years }, yAxis: [{ type: "value", min: 90000, axisLabel: { formatter: (v) => v / 1000 + "k" } }, { type: "value", min: 100, max: 120, axisLabel: { formatter: (v) => v + "%" }, splitLine: { show: false } }],
      series: [{ name: "가구", type: "bar", data: R.housing.households, color: C.gray2 }, { name: "주택", type: "bar", data: R.housing.units, color: C.green3 }, { name: "보급률(우축)", type: "line", yAxisIndex: 1, data: R.housing.supply_rate, color: C.ink, lineStyle: { width: 2.5 } }] } });
  add({ id: "finance", g: "work", t: "일반회계 세입 → 2025 예산 2조 2,500억", take: "2006 6,571억 → 2013 1조 309억 → 2025 예산 2.25조. 3,822억 사업은 연 예산의 17%다.", tier: "T1", src: R.finance.src,
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "억" }, xAxis: { type: "category", data: [...R.finance.years, "2025(예산)"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => (v / 10000).toFixed(1) + "조" } },
      series: [{ type: "bar", data: [...R.finance.general_revenue.map((v) => Math.round(v / 100)), { value: R.finance.budget_2025_100M, itemStyle: { color: C.orange } }], color: C.green, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => (d.value / 10000).toFixed(2) + "조" } }] } });
  add({ id: "medical", g: "work", t: "의료기관 239개 · 병상 4,376", take: "2009→2013 병상 +43%. 시청 이전 시 보건소는 동천동에 남긴다(입지 논리가 다름).", tier: "T1", src: R.medical.src,
    opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: R.medical.years }, yAxis: [{ type: "value", min: 200 }, { type: "value", min: 2500, splitLine: { show: false } }], series: [{ name: "의료기관", type: "bar", data: R.medical.hospitals, color: C.green3 }, { name: "병상(우축)", type: "line", yAxisIndex: 1, data: R.medical.beds, color: C.ink, lineStyle: { width: 2.5 } }] } });
  if (HW) {
    const B = HW.biz2024, P = HW.pop_hwango, SR = HW.survey_res, SV = HW.survey_vis, K = HW.kpi, T = HW.tenure, SS = HW.sales;
    const grp = ["숙박·체류", "카페·휴게음식", "음식점·제과", "생활소매·식품제조", "생활서비스·의료", "유흥·오락", "통신판매(무점포)"];
    add({ id: "hwbiz24", g: "work", t: "2024 창업·폐업 — 축제용 임시 가게 27건을 빼고 보면", take: "보고서 ‘창업 70건’ 중 27건은 폐역 부지 축제 임시영업. 실질 창업 43·폐업 39 — 2018(48건)보다 적다.", size: "m", tier: "T2", src: B.src, lead: "위(초록)가 실질 창업, 아래(빨강)가 실질 폐업, 회색이 창업·폐업 양쪽에 중복된 임시영업.",
      note: `구 경주역 부지 ${B.open.popup_by_site["구 경주역 부지(성동동 40)"]}건은 5·6·9·11월 축제 기간. 실질 순증은 숙박·체류만 +${(B.open.by_group["숙박·체류"] || 0) - (B.close.by_group["숙박·체류"] || 0)}. 생활소매·식품제조 ${(B.open.by_group["생활소매·식품제조"] || 0) - (B.close.by_group["생활소매·식품제조"] || 0)}, 음식점 ${(B.open.by_group["음식점·제과"] || 0) - (B.close.by_group["음식점·제과"] || 0)}.`,
      opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => Math.abs(v) + "건" }, xAxis: { type: "category", data: grp, axisLabel: { fontSize: 10.5, interval: 0, rotate: 24 } }, yAxis: { type: "value", axisLabel: { formatter: (v) => Math.abs(v) } },
        series: [{ name: "창업(실질)", type: "bar", stack: "a", data: grp.map((k) => B.open.by_group[k] || 0), color: C.green }, { name: "폐업(실질)", type: "bar", stack: "a", data: grp.map((k) => -(B.close.by_group[k] || 0)), color: C.red }, { name: "임시영업", type: "bar", stack: "a", data: grp.map((k) => (B.open.by_group_all[k] || 0) - (B.open.by_group[k] || 0)), color: C.gray2 }] } });
    add({ id: "hwclose", g: "work", t: "2024 실질 폐업 39건의 업력", take: "30년 넘은 가게 4곳 — 1961 계림여인숙, 1980 대원슈퍼, 1982 고도삼계탕, 1984 이화순미용실. 생활업종의 세대 교체 없는 소멸.", tier: "T2", src: B.src,
      opt: hbar(Object.keys(B.closure_age_bins), Object.values(B.closure_age_bins), { unit: "건", top: 5, color: C.red }) });
    const yrs6 = HW.series.years; const idx = (a) => a.map((v) => +(v / a[0] * 100).toFixed(1));
    add({ id: "hwgrid", g: "work", t: "사업구역 격자 32칸 — 종사자가 가장 빨리 빠진다", take: "2018=100. 종사자 −23%, 인구 −14%, 사업체 −3%. 성동시장 셀 사업체 264→160.", size: "m", tier: "T2", src: HW.series.src, lead: "도시재생 사업구역 100m 격자 32칸의 통계청 자료. 선이 100 아래면 줄어든 것. 점선은 황오동 전체 인구.",
      opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: yrs6 }, yAxis: { type: "value", scale: true, min: 70 },
        series: [...Object.entries({ pop: "인구", hh: "가구", biz: "사업체", emp: "종사자", house: "주택" }).map(([k, t], i) => ({ name: t, type: "line", data: idx(HW.series.site[k]), color: [C.green, C.green2, C.orange, C.blue, C.purple][i], lineStyle: { width: k === "emp" ? 3 : 1.8 } })), { name: "황오동 인구", type: "line", data: idx(HW.series.dong.pop), color: C.gray, lineStyle: { type: "dashed" } }] } });
    const bands = Object.keys(P.age);
    add({ id: "hwage", g: "people", t: "황오동 연령구조 2018 → 2025.07", take: `20대·50대가 비고 75세+만 는다. 20–39세 −${(100 - P.n_20_39.at(-1) / P.n_20_39[0] * 100).toFixed(0)}%, 65세+ ${pct(P.share_65.at(-1))}.`, size: "m", tier: "T2", src: P.src,
      opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: bands, axisLabel: { fontSize: 10, interval: 1, rotate: 40 } }, yAxis: { type: "value" }, series: [{ name: "2018", type: "bar", data: bands.map((b) => P.age[b]["2018"]), color: C.gray2 }, { name: "2025.07", type: "bar", data: bands.map((b) => P.age[b]["2025.07"]), color: C.green }] } });
    add({ id: "hwsales", g: "work", t: "대표 5업종 월매출 — 2024.10 점프는 의원이 만든다", take: "‘상권 매출 +15%’는 5개 대표업종 합계이고 피부/비뇨기과의원 한 업종이 57%다.", tier: "T2", src: SS.src, note: SS.note,
      opt: { grid: { left: 8, right: 16, top: 12, bottom: 8, containLabel: true }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "만 원" }, xAxis: { type: "category", data: SS.months, axisLabel: { fontSize: 10, formatter: (v) => (v.endsWith("-01") || v === "2023-09" ? v : v.slice(5)) } }, yAxis: { type: "value", scale: true, axisLabel: { formatter: (v) => (v / 10000).toFixed(1) + "억" } }, series: [{ type: "line", data: SS.total_manwon, color: C.orange, areaStyle: { opacity: .12 }, lineStyle: { width: 2.5 } }] } });
    add({ id: "hwtenure", g: "work", t: "업력 10년 이상 311곳의 업종", take: "방앗간·참기름·식육·여인숙·다방. 2018 이후 폐업 상위는 한식 44·즉석판매 36·다방 17.", tier: "T2", src: T.src, opt: hbar(Object.keys(T.over10y_by_upjong), Object.values(T.over10y_by_upjong), { unit: "곳", top: 12, color: C.green }) });
    const cmpk = ["대상지", "황오동", "경주시", "경상북도"]; const cmpv = { 대상지: { closures: K.closures }, ...K.compare };
    add({ id: "hwcmp", g: "work", t: "폐업 건수 지수 — 대상지·황오동·경주시·경북", take: "경북 폐업은 2020부터 6년 연속 증가(+29%). 대상지 2024 급등은 임시영업 27건이 만든 것.", tier: "T2", src: K.src,
      opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: K.years }, yAxis: { type: "value", scale: true }, series: cmpk.map((k, i) => ({ name: k, type: "line", data: idx(cmpv[k].closures), color: [C.red, C.orange, C.blue, C.gray][i], lineStyle: { width: k === "대상지" ? 3 : 1.8 } })) } });
    // 설문(모니터링) → voice
    add({ id: "hwsurvey", g: "voice", t: "주민·상인 설문 2020–2024 — 인지도·소속감은 오르고 보행환경은 내려간다", take: "전반 만족도는 유지, 보행환경 점수는 하락. 인지도(막대)만 꾸준히 올랐다.", size: "m", tier: "T2", src: SR.src, note: SR.note,
      opt: { grid: { left: 8, right: 44, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: SR.years }, yAxis: [{ type: "value", min: 0, max: 10 }, { type: "value", min: 0, max: 100, axisLabel: { formatter: (v) => v + "%" }, splitLine: { show: false } }],
        series: [{ name: "전반 만족도", type: "line", data: SR.overall_satis, color: C.green, lineStyle: { width: 2.5 } }, { name: "주거환경", type: "line", data: SR.housing_env, color: C.green2 }, { name: "보행환경", type: "line", data: SR.walk_env, color: C.red }, { name: "소속감", type: "line", data: SR.belonging["황오동"], color: C.purple }, { name: "공공기관 신뢰", type: "line", data: SR.trust["공공기관"], color: C.blue }, { name: "인지도(우축)", type: "bar", yAxisIndex: 1, data: SR.awareness, color: "rgba(31,94,66,.18)" }] } });
    const hubs = Object.keys(SR.hub_expect_2024);
    add({ id: "hwhub", g: "voice", t: "거점공간 — 준공된 곳은 만족도가 매년 하락", take: "청년창업센터·도서관 9.6 → 6.7 → 4.4. 미준공 중에는 보행사업만 기대 7점대.", size: "m", tier: "T2", src: SR.src,
      opt: { grid: { left: 8, right: 16, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: [...Object.keys(SR.hub_satis), ...hubs], axisLabel: { fontSize: 10, interval: 0, rotate: 24 } }, yAxis: { type: "value", min: 0, max: 10 },
        series: [{ name: "2022", type: "bar", data: [...Object.values(SR.hub_satis).map((a) => a[2]), ...hubs.map(() => null)], color: C.gray2 }, { name: "2023", type: "bar", data: [...Object.values(SR.hub_satis).map((a) => a[3]), ...hubs.map(() => null)], color: C.gray }, { name: "2024", type: "bar", data: [...Object.values(SR.hub_satis).map((a) => a[4]), ...hubs.map(() => null)], color: C.red }, { name: "2024 기대(미준공)", type: "bar", data: [...Object.keys(SR.hub_satis).map(() => null), ...hubs.map((h) => SR.hub_expect_2024[h])], color: C.green }] } });
    add({ id: "hwvisit", g: "voice", t: "방문객 ‘직전 방문지’ — 황리단길 54%→12%, 성동시장 9%→48%", take: "표본·조사 장소가 매년 달라(2024는 축제 현장) 추세가 아니라 조사 조건의 변화로 읽어야 한다.", tier: "T2", src: SV.src, note: SV.note,
      opt: { grid: { left: 8, right: 16, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: SV.years }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } }, series: Object.entries(SV.prev_place).map(([k, a], i) => ({ name: k, type: "bar", stack: "p", data: a.map((v) => v ?? 0), color: [C.orange, C.green2, C.blue2, C.purple, C.blue, C.gray, C.gray2][i] })) } });
    add({ id: "hwmotive", g: "voice", t: "방문 계기 — 2024는 축제 50%, 체류 3시간 미만 79%", take: `1만 원 이상 지출 2.7%. 경주시민 비율 ${pct(SV.resident_gj_2024, 1)} — ‘관광객’ 지표가 아니라 주민 행사 지표에 가깝다.`, tier: "T2", src: SV.src,
      opt: { grid: { left: 8, right: 16, top: 56, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: SV.years }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } }, series: [...Object.entries(SV.motive).map(([k, a], i) => ({ name: k, type: "bar", stack: "m", data: a.map((v) => v ?? 0), color: [C.green, C.blue, C.purple, C.green2, C.orange, C.gray2][i] })), { name: "1만 원 이상 지출", type: "line", data: SV.spend_over_10, color: C.red, lineStyle: { width: 2.5 } }] } });
  }

  // ======================= 이동
  { const f = R.mode_forecast; const M6 = ["도보/자전거", "승용차", "택시", "버스", "철도", "기타"];
    add({ id: "modeshare", g: "move", t: "수단분담률 — 2007년 버스 36%에서 계획은 승용차 40%를 전제한다", take: "기본계획이 인용한 2007 조사에서 버스 36.2%·승용차 26.5%. 같은 계획의 2015~2030 예측표는 승용차 40%·버스 15.6%로 뒤집힌다.", size: "m", tier: "T1", src: `${R.mode_share_2007.src} / ${f.src}`,
      lead: "회색 2007 조사, 연초록 2015 예측, 초록 2030 예측(%). 예측표는 도보와 자전거를 합산했다.", note: "허브가 되돌리려는 것은 이 전제다. 신교통(원도심 경유 트램·셔틀)이 없는 계획은 승용차 40%를 받아들인 계획이다.",
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: ["도보(·자전거)", "승용차", "택시", "버스", "철도", "기타"] }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" }, max: 45 },
        series: [{ name: "2007 조사", type: "bar", data: R.mode_share_2007.pct, color: C.gray }, { name: "2015 예측", type: "bar", data: M6.map((m) => f.pct[m][0]), color: C.green2 }, { name: "2030 예측", type: "bar", data: M6.map((m) => f.pct[m][3]), color: C.green, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => d.value } }] } });
    add({ id: "modepurpose", g: "move", t: "목적별 수단분담 2007 — 등교 52% 버스, 업무 50% 승용차", take: "버스는 학생의 교통이고 승용차는 직장인의 교통이었다. 시청 8,000~9,000명의 통근이 어느 쪽에 실리느냐가 허브의 성패.", tier: "T1", src: R.mode_share_2007.src,
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: Object.keys(R.mode_share_2007.by_purpose) }, yAxis: { type: "value", max: 100, axisLabel: { formatter: (v) => v + "%" } }, series: R.mode_share_2007.modes.map((m, i) => ({ name: m, type: "bar", stack: "s", data: Object.values(R.mode_share_2007.by_purpose).map((v) => v[i]), color: [C.green3, C.orange, C.orange2, C.green, C.purple, C.gray2][i] })) } }); }
  add({ id: "cars", g: "move", t: "천 명당 차량 403 → 449대", take: "2009–2013 연 +2.8%. 주차 수요는 인구가 줄어도 늘었다.", tier: "T1", src: R.cars.src,
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: R.cars.years }, yAxis: { type: "value", min: 250, max: 470 }, series: [{ name: "전체", type: "line", data: R.cars.per_1000_total, color: C.ink, lineStyle: { width: 2.5 }, label: { show: true, position: "top", fontSize: 10.5, formatter: (d) => d.value.toFixed(0) } }, { name: "승용차", type: "line", data: R.cars.per_1000_car, color: C.orange }] } });
  add({ id: "rail", g: "move", t: "철도 승차 — 신경주역(KTX) vs 경주역(일반)", take: "경주역은 2021.12 폐역. 원도심의 철도 접근이 사라졌고 KTX는 건천읍 신경주역에 있다.", tier: "T1", src: R.rail.src,
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: R.rail.years }, yAxis: { type: "value", axisLabel: { formatter: (v) => v / 1e6 + "M" } }, series: [{ name: "신경주역", type: "bar", data: R.rail.ktx_board, color: C.green }, { name: "구 경주역", type: "bar", data: R.rail.gj_board, color: C.orange }] } });
  add({ id: "parking", g: "move", t: "주차시설 51,880면 — 부설 99%", take: "공영·노상은 1%. 도심 주차는 건물 부설에 맡겨져 있고 시민 불만 1위(38.8%)가 주차였다.", tier: "T1", src: R.parking.src,
    opt: hbar(R.parking.rows.filter((r) => r.kind !== "합계").map((r) => `${r.kind} (${fmt(r.sites)}개소)`), R.parking.rows.filter((r) => r.kind !== "합계").map((r) => r.spaces), { unit: "면", color: C.gray }) });
  add({ id: "bus", g: "move", t: "시내버스 수송 — 5년간 정체", take: "연 1,500만 명 수준에서 멈춤. 등록대수 163→169. 전세버스(관광)는 별도 선.", tier: "T1", src: R.bus.src,
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: R.bus.years }, yAxis: { type: "value", min: 0, axisLabel: { formatter: (v) => v / 1e6 + "M" } }, series: [{ name: "시내버스", type: "line", data: R.bus.city_pax, color: C.green, areaStyle: { opacity: .12 }, lineStyle: { width: 2.5 } }, { name: "전세버스", type: "line", data: R.bus.charter_pax, color: C.orange }] } });
  { const vcs = R.road_vc.rows.filter((r) => /국도7|국도4|국도35|국도20|지방도/.test(r.road) || r.vc >= 0.6).sort((a, b) => b.vc - a.vc).slice(0, 10);
    add({ id: "roadvc", g: "move", t: "주요 도로 V/C 상위 10구간", take: "1.0 = 용량 도달. 국도 위주 상위 구간. 경부축 버스가 원도심을 관통하면 안 되는 이유.", tier: "T1", src: R.road_vc.src, opt: hbar(vcs.map((r) => `${r.road} ${r.seg}`), vcs.map((r) => r.vc), { color: C.orange, top: 10, max: 1, fmtV: (v) => v.toFixed(2) }) }); }
  if (TH) { const hrs = [...Array(24).keys()];
    add({ id: "speedhour", g: "move", t: "도로 속도 — 하루 중 언제 막히나 (ITS 이력 표본)", take: `평일 ${TH.days.wd.length}일·주말 ${TH.days.we.length}일 표본. 평일 아침·저녁 첨두에 평균속도가 낮아지고 정체 구간 비율이 오른다.`, size: "m", tier: "T2", src: `국가교통정보센터 ITS 5분 이력 표본(매월 둘째 화·토) × 표준노드링크 · 링크 ${fmt(TH.links)}개 · 정체 = 도로등급별 임계(도시부 15 / 도시고속 30 / 고속 40 km/h)`,
      lead: "선은 시간대별 평균속도(km/h), 점선은 정체 임계 아래로 떨어진 구간의 비율(%). 표본일 설계라 명절·행사일은 반영되지 않는다.",
      opt: { grid: { left: 8, right: 44, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: hrs.map((h) => h + "시"), axisLabel: { interval: 2 } }, yAxis: [{ type: "value", name: "km/h", scale: true }, { type: "value", name: "정체%", max: 100, splitLine: { show: false } }],
        series: [{ name: "평일 평균속도", type: "line", data: TH.hourly.wd.map((r) => r.speed_avg), color: C.green, lineStyle: { width: 2.5 } }, { name: "주말 평균속도", type: "line", data: TH.hourly.we.map((r) => r.speed_avg), color: C.purple, lineStyle: { width: 2 } }, { name: "평일 정체 %", type: "line", yAxisIndex: 1, data: TH.hourly.wd.map((r) => r.congested_pct), color: C.red, lineStyle: { type: "dashed" } }] }, map: "traffic_hist" }); }
  if (TC) add({ id: "congtop", g: "move", t: "정체 빈도 상위 구간 (실시간 스냅샷)", take: `${TC[0]?.road} 등 — 5분 스냅샷 중 정체로 판정된 비율. 관측이 적은 구간은 제외.`, tier: "T2", src: "국가교통정보센터 trafficInfo 5분 스냅샷 누적 (2026-09-17~) · 관측 6회 이상",
    opt: hbar(TC.slice(0, 10).map((t) => `${t.road || "(무명)"} · ${t.speed_avg}km/h`), TC.slice(0, 10).map((t) => t.congested_pct), { unit: "%", top: 10, color: C.red, max: 100 }), map: "traffic_hist" });

  // ======================= 관광·경관·예술
  add({ id: "tourists", g: "visit", t: "지정관광지 방문객 — 보문·양남·감포만", take: `2013년 889만(외국인 19만). 관광데이터랩 2026.08 순방문자(18일 626만)는 정의가 달라 합칠 수 없다.`, tier: "T1", src: R.tourists.src,
    opt: { grid: { left: 8, right: 40, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: R.tourists.years }, yAxis: [{ type: "value", axisLabel: { formatter: (v) => v / 1e6 + "M" } }, { type: "value", axisLabel: { formatter: (v) => v / 1e3 + "k" }, splitLine: { show: false } }], series: [{ name: "합계", type: "bar", data: R.tourists.total, color: C.green }, { name: "외국인(우축)", type: "line", yAxisIndex: 1, data: R.tourists.foreign, color: C.orange, lineStyle: { width: 2 } }] } });
  if (VIS) { const days = Object.keys(VIS).sort().filter((k) => VIS[k]["현지인"] != null);
    if (days.length) add({ id: "visitors", g: "visit", t: "경주시 하루 방문자 — 휴대전화 기반 (2026.08)", take: `${days[0].slice(4, 6)}/${days[0].slice(6)}~${days.at(-1).slice(4, 6)}/${days.at(-1).slice(6)}. 시 전체 숫자라 부지 하나의 근거로는 쓰지 않는다.`, size: "m", tier: "T2", src: "한국관광데이터랩 DataLabService (KT 이동통신, 시군구)",
      opt: { grid: { left: 8, right: 8, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => fmt(v) + "명" }, xAxis: { type: "category", data: days.map((x) => x.slice(4, 6) + "/" + x.slice(6)) }, yAxis: { type: "value", axisLabel: { formatter: (v) => v / 1000 + "k" } },
        series: [["현지인", C.gray], ["외지인", C.green], ["외국인", C.orange]].map(([k, c]) => ({ name: k, type: "line", stack: "v", areaStyle: { opacity: .5 }, showSymbol: false, lineStyle: { width: 1 }, itemStyle: { color: c }, data: days.map((x) => Math.round(VIS[x][k] || 0)) })) } }); }
  { const ls = R.landscape_survey;
    add({ id: "landscape", g: "visit", t: "경주의 대표 경관은? — 시민 36% 황리단길, 관광객 53% 불국사", take: "시민과 관광객의 ‘경주’가 다르다. 2025 연구의 상징적 중심 1위도 황리단길(59명 중 25).", tier: "T1", src: ls.src,
      opt: { grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: ["시민", "공무원", "관광객"] }, yAxis: { type: "value", max: 60, axisLabel: { formatter: (v) => v + "%" } }, series: [{ name: "황리단길", type: "bar", data: ["시민", "공무원", "관광객"].map((k) => ls.representative["황리단길"][k]), color: C.orange, label: { show: true, position: "top", fontSize: 11 } }, { name: "불국사", type: "bar", data: ["시민", "공무원", "관광객"].map((k) => ls.representative["불국사"][k]), color: C.green, label: { show: true, position: "top", fontSize: 11 } }] } });
    const pp = ls.priority_projects;
    add({ id: "landprio", g: "visit", t: "우선 경관사업 — 시민 vs 공무원", take: `가장 개선이 필요한 경관은 옥외광고물(시민 ${ls.worst_ad["시민"]}%). 정체성은 ‘신라왕경을 품은 역사도시’ ${ls.identity_silla["시민"]}%.`, tier: "T1", src: ls.src,
      opt: { grid: { left: 4, right: 40, top: 30, bottom: 4, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "value", show: false, max: 70 }, yAxis: { type: "category", inverse: true, data: Object.keys(pp), axisLabel: { color: C.ink, fontSize: 12, width: 190, overflow: "break" } }, series: [{ name: "시민", type: "bar", data: Object.values(pp).map((v) => v["시민"]), color: C.green, barCategoryGap: "35%" }, { name: "공무원", type: "bar", data: Object.values(pp).map((v) => v["공무원"]), color: C.gray, label: { show: true, position: "right", fontSize: 11, color: C.ink2 } }] } }); }
  add({ id: "heritagecount", g: "visit", t: "문화재 지정 건수 300 → 326 (2004–2014)", take: `국가지정 ${fmt(R.heritage_count.national.at(-1))}건. 지정이 늘수록 규제 4겹의 ③층은 두꺼워진다.`, tier: "T1", src: R.heritage_count.src,
    opt: { grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: R.heritage_count.years }, yAxis: { type: "value", min: 180 }, series: [{ name: "전체", type: "line", data: R.heritage_count.total, color: C.ink, lineStyle: { width: 2.5 } }, { name: "국가지정", type: "line", data: R.heritage_count.national, color: C.green }, { name: "보물", type: "line", data: R.heritage_count.treasure, color: C.orange }, { name: "사적", type: "line", data: R.heritage_count.historic, color: C.purple }] } });
  add({ id: "parks", g: "visit", t: `도시공원 ${fmt(R.parks.total_count)}개소 · 1인당 ${(R.parks.total_k_m2 * 1000 / p26).toFixed(1)}㎡`, take: "근린공원 29곳이 면적의 92%. 결정도의 근린공원 55,415㎡는 이 목록에 3곳을 더한다.", tier: "T1", src: R.parks.src,
    opt: hbar(R.parks.kinds, R.parks.area_k_m2.map((v) => Math.round(v / 10)), { unit: "ha", top: 7, color: C.green2 }) });
  if (AR) { const G = AR.gyeongju, F = AR.fields, A = AR.ages; const fi = (n) => F.labels.indexOf(n); const hl = (names, key, b) => names.map((n) => ({ value: key(n), itemStyle: { color: n.name === "경주시" ? C.red : b } }));
    add({ id: "arts10k", g: "visit", t: `예술인 ${fmt(G.n)}명 — 인구 1만 명당 ${G.per10k}명`, take: `경북 시 1위지만 전국 평균(약 ${AR.nation.per10k})보다 낮고 8개 도 122개 시군구 중 ${G.rank_in_8do[0]}위. 전주·강릉·공주는 30 후반~60.`, tier: "T2", src: AR.src.kawf, lead: "한국예술인복지재단 예술활동증명 누적 ÷ 주민등록 2026.08. 복지사업 신청용 등록이라 등록하지 않은 공예인·귀촌 작가는 빠진다.",
      opt: { ...hbar(AR.compare.map((x) => x.name), AR.compare.map((x) => x.per10k), { unit: "명", top: 10 }), series: [{ type: "bar", data: hl(AR.compare, (x) => x.per10k, C.green), barCategoryGap: "32%", label: { show: true, position: "right", fontSize: 11.5, color: C.ink2, formatter: (d) => d.value } }] } });
    add({ id: "artsfield", g: "visit", t: "예술 분야 구성 — 국악·미술·문학이 크고 연극·영화·연예가 없다", take: `국악 ${pct(F.pct["경주"][fi("국악")])}(전국 ${pct(F.pct["전국"][fi("국악")])}). 공연장·제작 산업이 없는 도시의 전형.`, size: "m", tier: "T2", src: AR.src.kawf,
      note: "부지 프로그램은 공연장이 아니라 공방·작업실·국악 연습실·수리기능 공방 쪽이 지역 예술인 구성과 맞는다. 1946 경주예술학교의 교사(校舍)가 옛 경주역사와 철도기관고였다 — 폐역을 예술 교육으로 쓴 선례가 경주 안에 있다(T4).",
      opt: { grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: F.labels.slice(0, 11), axisLabel: { fontSize: 11, interval: 0 } }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" } }, series: [{ name: "경주", type: "bar", data: F.pct["경주"].slice(0, 11), color: C.red }, { name: "전주", type: "bar", data: F.pct["전주"].slice(0, 11), color: C.orange2 }, { name: "전국", type: "bar", data: F.pct["전국"].slice(0, 11), color: C.gray2 }] } });
    add({ id: "artsage", g: "visit", t: "예술인 연령 — 경주는 50–60대, 전국은 30대", take: `50–60대 ${pct(A.pct["경주"][3] + A.pct["경주"][4])}(전국 ${pct(A.pct["전국"][3] + A.pct["전국"][4])}). 10년 안에 절반이 은퇴한다.`, tier: "T2", src: AR.src.kawf,
      opt: { grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis", valueFormatter: (v) => pct(v) }, xAxis: { type: "category", data: A.labels }, yAxis: { type: "value", axisLabel: { formatter: (v) => v + "%" } }, series: [{ name: "경주", type: "line", data: A.pct["경주"], color: C.red, lineStyle: { width: 3 }, areaStyle: { opacity: .08 } }, { name: "전주", type: "line", data: A.pct["전주"], color: C.orange2 }, { name: "안동", type: "line", data: A.pct["안동"], color: C.green2 }, { name: "전국", type: "line", data: A.pct["전국"], color: C.ink, lineStyle: { type: "dashed" } }] } });
    const ec = AR.econ;
    add({ id: "artsecon", g: "visit", t: "예술 고용 — 창작업 vs 유산 관리업", take: `경주 902 사적지·박물관·도서관 종사자 ${fmt(ec[0].heritage_emp_2020)}명, 901 창작·예술 ${ec[0].create_emp_2020}명. 예술 고용은 창작이 아니라 유산 관리에 있다.`, tier: "T2", src: AR.src.econ,
      opt: { grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true }, legend: { top: 0, left: 0 }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: ec.map((x) => x.name.replace("시", "").replace("군", "")), axisLabel: { fontSize: 11, interval: 0 } }, yAxis: { type: "value" }, series: [{ name: "902 사적지·박물관·도서관", type: "bar", data: ec.map((x) => x.heritage_per10k_2020), color: C.green }, { name: "901 창작·예술", type: "bar", data: ec.map((x) => x.create_per10k_2020), color: C.orange }] } });
    add({ id: "artsgb", g: "visit", t: "경북 10개 시 — 1만 명당 예술인", take: `절대 수는 포항 764 > 경주 675 > 경산 654. 1만 명당은 경주 1위, 경산(대학 도시) 2위.`, tier: "T2", src: AR.src.kawf,
      opt: { ...hbar(AR.gb_cities.map((x) => x.name), AR.gb_cities.map((x) => x.per10k), { unit: "명", top: 10 }), series: [{ type: "bar", data: hl(AR.gb_cities, (x) => x.per10k, C.green2), barCategoryGap: "32%", label: { show: true, position: "right", fontSize: 11.5, color: C.ink2, formatter: (d) => d.value } }] } }); }

  // ======================= 시민의 목소리
  { const sv = X.surveys.filter((r) => /부지|경주역 활용|미래상/.test(r.q) && /\d/.test(r.v)); const rows = [];
    for (const r of sv) { const vals = r.v.split("/").map((t) => parseFloat(t)); const labs = r.a.split("/").map((t) => t.trim()); if (vals.length > 1) labs.forEach((l, i) => rows.push([`${r.when.slice(0, 4)} ${l}`, vals[i], r.survey])); else rows.push([`${r.when.slice(0, 4)} ${r.a}`, vals[0], r.survey]); }
    add({ id: "survey3", g: "voice", t: "시민들은 옛 경주역 부지에 무엇을 원했나 — 설문 3번", take: "2015 복합위락 44.5% · 행정복합타운 26.2% → 2023 시청 이전 63.7%(T4) → 2025 문화·쇼핑 거점과 교통 거점. 갈수록 ‘공공청사·교통 기점’ 쪽으로 기울었다.", size: "m", tier: "T1", src: "2030 기본계획 설문(T1) · 2023 폐철도 기본구상 설문(T4, 원문 미확보) · 2025 미래구상 연구 설문(T2)",
      lead: "서로 다른 기관이 다른 방식으로 물은 결과라 숫자를 직접 비교하면 안 되고 ‘어느 쪽으로 기울었나’만 읽는다. 초록 2015, 회색 2023, 보라 2025.",
      opt: { grid: { left: 4, right: 40, top: 4, bottom: 4, containLabel: true }, tooltip: { trigger: "axis", formatter: (ps) => `${rows[ps[0].dataIndex][0]}<br>${ps[0].value}<br>${rows[ps[0].dataIndex][2]}` }, xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: rows.map((r) => r[0]), axisLabel: { color: C.ink, fontSize: 11.5, width: 170, overflow: "truncate" } }, series: [{ type: "bar", data: rows.map((r) => ({ value: r[1], itemStyle: { color: /2030/.test(r[2]) ? C.green : /폐철도/.test(r[2]) ? C.gray : C.purple } })), label: { show: true, position: "right", fontSize: 11 }, barCategoryGap: "30%" }] } }); }
  for (const q of R.survey_2015.questions) add({ id: "s15_" + q.page + "_" + q.q.slice(0, 6), g: "voice", t: `2015 · ${q.q}`, take: `1위 ${q.items[0].a} ${q.items[0].v}% · 2위 ${q.items[1]?.a} ${q.items[1]?.v}% — 격차가 논거의 세기.`, tier: "T1", src: `${R.survey_2015.meta} · 인쇄쪽 ${q.page}`, opt: hbar(q.items.map((i) => i.a), q.items.map((i) => i.v), { unit: "%", top: 6, color: q.q.includes("경주역") ? C.orange : C.green }) });
  { const s25 = R.survey_2025; for (const [k, t, tk] of [["transit_alt", "2025 · 대중교통 대안 선호", "대중교통 평가 2.7/5. 자율주행 무료버스 18 > 보행 13 > 옛철도 재개통 10 > 트램 8."], ["future_image", "2025 · 경주의 미래상", "관광도시 35 · 힐링 28 · 역사 23."], ["needed_facility", "2025 · 원도심에 필요한 시설", "표본 63명 — 비율이 아니라 응답 수."], ["friendly_cities", "2025 · 경주와 친한 도시", "울산 40 · 포항 40 · 대구 32 — 동해축 도시가 먼저다."]])
    add({ id: "s25_" + k, g: "voice", t, take: tk, tier: "T2", src: s25.meta, opt: hbar(Object.keys(s25[k]), Object.values(s25[k]), { unit: "명", top: 9, color: C.purple }) }); }

  // ======================= 출처 (표)
  add({ id: "srcs", g: "sources", t: "이 페이지가 쓴 문서와 등급", take: "숫자를 인용할 때는 여기 적힌 쪽과 등급을 그대로 옮긴다.", size: "l", html: `<table class="t"><tr><th>등급</th><th>문서</th><th>쓰인 곳</th></tr>${[["T1", "2030 경주도시기본계획 (승인, 475쪽)", "인구·토지·교통·관광·경제·주거·재정·시민의식 2015"], ["T1", "2030 경주시 경관계획 재정비 (2025.04)", "경관의식조사"], ["T1", "경주시 도시재생 전략계획(변경) (2022.01)", "쇠퇴진단·원도심 쇠퇴 원인"], ["T1", "경주시 고시 제2026-8호 지구단위계획 · 경북 고시 2020-479호 고도지구 · V-World 토지이용규제", "획지·고도·규제 영역"], ["T1", "경주시 홈페이지 청사안내 (2026-09-02) · 행안부 공유재산 운영기준", "시청 분산 실태·청사 규모"], ["T2", "경주시 원도심 미래구상 기획연구 (2025.07, 417쪽)", "시민설문 2025 · 교통거점 부활 목표"], ["T2", "황오동 원도심·행복황촌 도시재생 성과지표 모니터링 (2025.09 / 2025.12)", "유동인구·창업폐업·공시지가·격자·연령·설문"], ["T2", "소상공인365 상권분석", "유동인구 8구역 · 업종"], ["T2", "KOSIS (주민등록·외국인주민·국적·지역별고용조사·인구이동) · 관광데이터랩 · ITS · 건축HUB · 소진공 · 경주시 공공데이터", "인구·청년·외국인·취업·교통·노후도·상가·학교·종교"], ["T2", "한국예술인복지재단 · 경제총조사 2015·2020 · 시굴조사 추진계획(2026.02)", "예술인 · 매장유산"], ["T4", "2023 폐철도 기본구상 설문 (언론 경유)", "시청 이전 63.7% — 원문 미확보"]].map(([t, d, u]) => `<tr><td>${TIER(t)}</td><td>${d}</td><td>${u}</td></tr>`).join("")}</table>` });

  render(R, X, MS, Y);
}

// ---------------------------------------------------------------- 렌더
const charts = [];
function chartInto(el, opt, small) {
  const ch = echarts.init(el, "gj");
  ch.setOption({ animationDuration: reduced ? 0 : 500, ...opt, ...(small ? { legend: opt.legend ? { ...opt.legend, textStyle: { fontSize: 10.5 } } : undefined } : {}) });
  charts.push(ch); return ch;
}
function render(R, X, MS, Y) {
  const main = document.getElementById("main"); const chips = document.getElementById("chips");
  // 히어로 타일 + 근거
  const p26 = R.pop_actual.pop_2026_08;
  const tiles = document.getElementById("hero-tiles");
  for (const t of [
    { k: "폐역 구역 유동인구", v: fmt(X.footfall.D_zone.per_ha), u: "/ha", d: `성동시장 200m ${fmt(X.footfall.G_seongdong_market_r200.per_ha)}/ha의 1/15`, c: "footfall" },
    { k: "시청 밖에 있는 본청 과", v: "15", u: "/45개", d: "12개 과 민간 빌딩 임차 · 문서고는 체육관", c: "cityhall" },
    { k: "시청 500m 저녁(18–23시) 비중", v: pct(X.footfall.F_cityhall_r500.hourly_pct[4]), d: "8구역 중 유일하게 저녁이 긴 생활권", c: "ffhour" },
    { k: "주민등록 2026.08", v: fmt(p26), u: "명", d: `계획 320,000 대비 ${((p26 / 320000 - 1) * 100).toFixed(0)}% · 65세↑ 30.0%`, c: "popplan" },
    { k: "20–34세 순유출 2020–25", v: fmt(Y ? Y.net["20-34세"].reduce((a, b) => a + b, 0) : null), u: "명", d: "20–24세가 매년 가장 크다", c: "ymig" },
    { k: "높이 상한", v: "20", u: "m", d: "도심20m지구 146,489㎡ · 문화유산 허용기준 수용값", c: "godo" },
  ]) tiles.appendChild($(`<div class="tile" data-card="${t.c}" role="button" tabindex="0"><div class="k">${t.k}</div><div class="v">${t.v}${t.u ? `<small>${t.u}</small>` : ""}</div><div class="d">${t.d}</div></div>`));
  const ev = (id, label, tier) => `<span class="ev" data-card="${id}">${label}${TIER(tier)}</span>`;
  document.getElementById("why").innerHTML = `
    <div class="col"><h3>왜 시청인가 — 기능을 되돌린다</h3><p class="sub">원도심 쇠퇴의 1번 원인이 시청 이전이었다면, 처방은 되돌리는 것이다.</p><ol>
      <li><b>12년간 5단계 계획이 같은 말을 했다.</b> 2030 기본계획 “경주역 이전적지 멀티복합타운(행정·문화)” → 경관계획 “행정복합타운 중점경관관리구역” → 전략계획·활성화계획 “분산된 행정기능 통합 2019~2028” → 고시 2026-8호 “행정복합타운 공공청사 24,987㎡”. ${ev("blocks", "공청1·2 24,987㎡", "T1")}</li>
      <li><b>쇠퇴 원인의 반전.</b> 전략계획은 원도심 쇠퇴 원인으로 “시청 이전과 외연 확장 → 다핵구조 → 기존 도심 약화”를 세 번 반복해 적었다. ${ev("hadmchg", "원도심 10년 −22~−45%", "T2")} ${ev("hwgrid", "격자 종사자 −23%", "T2")}</li>
      <li><b>지금 시청은 이미 한 곳에 없다.</b> 본관은 옛 경주군청, 45개 과 중 15개 과가 5개 외부 장소, 12개 과가 민간 빌딩 임차. ‘신축’이 아니라 ‘임차 해소’다. ${ev("cityhall", "15/45개 과", "T1")}</li>
      <li><b>청사 효과의 자연실험.</b> 현 시청 500m는 원도심 8구역 중 유일하게 저녁(18–23시) 비중이 27%이고, 주거 9,145·직장 8,374로 유일한 직주 균형 구역이다. ${ev("ffhour", "18–23시 27%", "T2")} ${ev("footfall", "8구역 ha당", "T2")}</li>
      <li><b>평일 축.</b> 시청은 주 5일·연 250일 8,000~9,000명(직원 850~950 + 민원)을 변동 없이 데려온다. 관광은 주말·계절 변동이 크다. ${ev("visitors", "일별 방문자", "T2")} ${ev("hwmotive", "체류 3시간 미만 79%", "T2")}</li>
      <li><b>시민 선호.</b> 행정복합타운 26.2%(2015, 2위) → 시청 이전 63.7%(2023, T4 원문 미확보) → 2025 ‘문화·쇼핑 거점 + 교통 거점’. ${ev("survey3", "설문 3번", "T1")}</li>
    </ol></div>
    <div class="col"><h3>왜 모빌리티 허브인가 — 연결을 되살린다</h3><p class="sub">여객터미널 이전이 아니라 교통광장형 허브: 트램·셔틀·동해축 버스·자전거·PM·택시 환승 + P+R.</p><ol>
      <li><b>계획이 이미 여기에 환승센터를 그렸다.</b> 2030 교통계획 “복합환승센터는 도심의 경주역·시외버스터미널·KTX역”, “신경주역~보문 신교통을 원도심 경유로”, 제1순환선 경주역(성동시장). 미래구상 목표 3b “(옛)경주역 교통거점 기능의 부활”. ${ev("rail", "경주역 폐역 2021.12", "T1")}</li>
      <li><b>승용차 40%의 전제를 되돌린다.</b> 2007년 버스 36%였던 분담률을 계획은 승용차 40%·버스 15.6%로 뒤집어 예측했다. 신교통 없는 계획은 그 전제를 받아들인 계획이다. ${ev("modeshare", "버스 36%→15.6%", "T1")} ${ev("modepurpose", "업무통행 승용차 50%", "T1")}</li>
      <li><b>주차는 99%가 부설이고, 불만 1위였다.</b> 51,880면 중 공영·노상 1%. 2015 교통 문제 1위 ‘대규모 주차시설 확충’ 38.8%. 허브의 P+R이 관광지 쏠림과 원도심 주차난을 함께 받는다. ${ev("parking", "부설 99%", "T1")} ${ev("parkpub", "공영주차장 면수", "T2")} ${ev("cars", "천 명당 449대", "T1")}</li>
      <li><b>정체는 시간대의 문제다.</b> 평일 첨두에 정체 구간 비율이 오르고 주말은 다르다 — 허브는 첨두 분산(시청 통근 + 관광 도착)을 한 곳에서 다룬다. ${ev("speedhour", "시간대별 속도", "T2")} ${ev("roadvc", "V/C 상위", "T1")}</li>
      <li><b>폐선 노반 3.5km는 경주 유일의 무교차 통로다.</b> 구경주역–황성–석장(동국대)–금장. 자율주행·트램이 쉬운 유일한 선형이며, 시민 대안 선호 1위가 ‘자율주행 무료버스’(18/63)였다. ${ev("s25_transit_alt", "대안 선호", "T2")} ${ev("bus", "시내버스 5년 정체", "T1")}</li>
      <li><b>친한 도시는 울산·포항이다.</b> 동해축(포항·울산·감포) 시외버스만 받고 경부축은 노서동 존치 — 원도심 관통을 막는다. ${ev("s25_friendly_cities", "울산 40 · 포항 40", "T2")}</li>
    </ol></div>`;
  document.getElementById("counter-body").innerHTML = `<table class="t"><tr><th>반대·불확실</th><th>대응·상태</th></tr>
    <tr><td>동천동 제로섬 — 시청 주변 상권의 2차 공동화</td><td>인정. 보건소 잔류·확장, 옛 군청 본관은 동천동 주민시설·공공임대로, 임차 해지분은 시장 흡수. 전략계획이 동천동을 “폐선부지와 연계한 시청 일원 활성화” 대상으로 잡아 둔 것이 근거.</td></tr>
    <tr><td>시청은 낮의 시설 — 야간 공백</td><td>인정. 청년주거·STAY가 같은 부지에 있어야 한다. 시청 단독안은 없다. 청년 20–34세 순유출과 황남동 청년 7%가 그 수요의 크기다.</td></tr>
    <tr><td>설문 1위(복합위락 44.5%)가 아니다</td><td>인정. 쇼핑 수요는 마켓홀·리테일, 위락은 STAY·야시장으로 받는다. 시청은 그 수요를 만드는 배후 인구다.</td></tr>
    <tr><td>공공청사로 높이를 회피한 랜드마크</td><td>불가. 20m는 문화유산 허용기준 수용값이라 청사도 면제 없음. 랜드마크는 광장·구 역사·수장고로.</td></tr>
    <tr><td>인구 감소 도시의 청사 신축</td><td>행안부 별표1 기준면적 안에서만, 초과분은 주민편의로 전환 의무. 임차 해소이지 증설이 아니다.</td></tr>
    <tr><td><b>확정되지 않은 것</b></td><td>‘시청 이전 63.7%’(2023 설문)는 언론 경유 T4로 원문 미확보 · 본청 인원 800~950명은 가정(인사통계 REQ-004) · 폐선 노반 선형은 OSM(T4, 지형도면 벡터화로 T1 치환 예정) · 매장문화재 시굴 전에는 청사 위치를 확정할 수 없음 · 시청 이전은 S3 정치 결정이라 S1 부지 데이터로 정당화하지 않고, 대안 비교에서 ‘시청 유/무’를 이진 파라미터로 둔다.</td></tr></table>`;
  // 그룹 칩 + 섹션
  for (const G of GROUPS) {
    const cs = CARDS.filter((c) => c.g === G.id); if (!cs.length) continue;
    chips.appendChild($(`<a href="#g-${G.id}" data-g="${G.id}">${G.title}<small>${cs.length}</small></a>`));
    const sec = $(`<section class="sec" id="g-${G.id}"><div class="eyebrow">${cs.length}장</div><h2>${G.title}</h2>${G.read ? `<p class="read">${G.read}</p>` : ""}<div class="cn-grid"></div></section>`);
    const grid = sec.querySelector(".cn-grid");
    for (const c of cs) {
      const art = $(`<article class="cn ${c.size || ""}" data-card="${c.id}" tabindex="0" role="button"><div class="k">${TIER(c.tier)}${G.title}</div><h3>${c.t}</h3><p class="take">${c.take || ""}</p><div class="thumb ${c.html && !c.opt ? "htm" : ""}"></div><p class="more">자세히 보기 →</p></article>`);
      grid.appendChild(art);
      const th = art.querySelector(".thumb");
      if (c.opt) chartInto(th, c.opt, true); else if (c.html) th.innerHTML = c.html;
    }
    main.appendChild(sec);
  }
  // 칩 하이라이트
  const links = [...chips.querySelectorAll("a")]; const secs = [...document.querySelectorAll("section.sec")];
  const io = new IntersectionObserver((es) => { for (const e of es) if (e.isIntersecting) links.forEach((a) => a.classList.toggle("on", a.getAttribute("href") === "#" + e.target.id)); }, { rootMargin: "-25% 0px -65% 0px" });
  secs.forEach((x) => io.observe(x));
  // 클릭 → 상세
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
  const links = document.getElementById("dlg-links"); links.innerHTML = c.map ? `<a href="./index.html#layer=${c.map}">지도에서 이 레이어 보기 →</a>` : "";
  const ch = document.getElementById("dlg-chart"), hh = document.getElementById("dlg-html");
  if (dlgChart) { dlgChart.dispose(); dlgChart = null; } ch.innerHTML = ""; hh.innerHTML = c.html && !c.opt ? c.html : "";
  if (!dlg.open) dlg.showModal();
  dlg.scrollTop = 0;
  if (c.opt) { dlgChart = echarts.init(ch, "gj"); dlgChart.setOption({ animationDuration: reduced ? 0 : 400, ...c.opt }); }
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
