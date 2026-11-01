"""경주 원도심 층위도 — 인터랙티브 HTML 생성기.

입력: archive/90_derived/palimpsest_layers_20260928.json (가로·철도·읍성·유적, 지역 좌표)
      archive/90_derived/palimpsest_evidence_20260928.json (방위 분포·간격 스펙트럼·표본 외 검정·규칙선)
      archive/90_derived/palimpsest_figureground_20260928.png (건물 도형-바탕)
출력: work/경주_원도심_층위도.html
내용(연표·판정·출처)은 CONTENT 에서 고친다. 좌표는 EPSG:5187 을 원점(218200, 359450) 기준 m 로 옮긴 값.
"""
import base64
import json
from pathlib import Path

from pyproj import Transformer

ROOT = Path(__file__).resolve().parent.parent
DER = ROOT / "archive" / "90_derived"
OUT = ROOT / "work" / "경주_원도심_층위도.html"
L = json.load(open(DER / "palimpsest_layers_20260928.json", encoding="utf-8"))
E = json.load(open(DER / "palimpsest_evidence_20260928.json", encoding="utf-8"))
FG = base64.b64encode((DER / "palimpsest_figureground_20260928.png").read_bytes()).decode()
OX, OY = L["origin"]
VW, VH = L["view_m"]


def flip(c):
    return [round(c[0], 1), round(VH - c[1], 1)]


def path(coords_list, close=False):
    parts = []
    for cs in coords_list:
        if len(cs) < 2:
            continue
        p = [flip(c) for c in cs]
        parts.append("M" + " L".join(f"{x} {y}" for x, y in p) + (" Z" if close else ""))
    return " ".join(parts)


def pt(x5187, y5187):
    return flip([x5187 - OX, y5187 - OY])


# ── 가로: (체계, 폭 등급) 묶음 + 이름 붙은 간선 ────────────────────────
buckets, named = {}, {}
for s in L["streets"]:
    wcls = "major" if s["w"] >= 15 else "mid" if s["w"] >= 6 else "minor"
    buckets.setdefault(f'{s["s"]}_{wcls}', []).append(s["c"])
    if s["n"]:
        named.setdefault(s["n"], []).append(s["c"])
street_paths = {k: path(v) for k, v in buckets.items()}
NAMED_KEEP = ["봉황로", "중앙로", "화랑로", "태종로", "원화로", "원효로", "양정로", "금성로", "북성로", "북문로", "동문로", "동성로", "알천북로", "알천남로", "첨성로"]
named_paths = {k: path(named[k]) for k in NAMED_KEEP if k in named}

herit_keep = ["첨성대", "황룡사지", "반월성", "대릉원일원", "미추왕릉", "성동동전랑지", "황오동고분", "탈해왕릉", "분황사석정", "인왕리고분군"]
herit = [{"p": flip(h["c"]), "n": h["n"].replace("분황사석정", "분황사").replace("대릉원일원", "대릉원").replace("성동동전랑지", "전랑지")}
         for h in L["herit_pt"] if h["n"] in herit_keep]

POI = [  # 5187 좌표 (수치지도 건물명·주기에서 확인)
    {"k": "c1918", "n": "첫 경주역 자리 (1918)", "p": pt(218770, 360172), "note": "현 서라벌문화회관"},
    {"k": "c1936", "n": "옛 경주역사 (1936)", "p": pt(219694, 360935), "note": "현 경주문화관 1918"},
    {"k": "jiph", "n": "집경전지", "p": pt(219178, 361192), "note": "읍성 안 조선 시설"},
    {"k": "gate", "n": "읍성 향일문", "p": pt(219302, 361112), "note": "동문, 복원"},
    {"k": "post", "n": "우체국", "p": pt(219495, 360770), "note": "화랑로 역전가"},
    {"k": "court", "n": "법원", "p": pt(219010, 360900), "note": "화랑로 역전가"},
    {"k": "police", "n": "경찰서", "p": pt(219080, 360950), "note": "화랑로 역전가"},
    {"k": "smkt", "n": "성동시장", "p": pt(219585, 360870), "note": "역 앞 시장"},
    {"k": "cmkt", "n": "중앙시장", "p": pt(218640, 360710), "note": "역전가 시장"},
    {"k": "gwansa", "n": "철도 관사", "p": pt(219865, 360880), "note": "1930년대 관사촌 쪽"},
]

DATA = {
    "view": [VW, VH],
    "streets": street_paths, "named": named_paths,
    "rail": path([r["c"] for r in L["rail"]]), "railpoly": path([r["c"] for r in L["rail_poly"]], close=True),
    "wall": path([w["c"] for w in L["wall"]]), "zone": path([L["zone"]], close=True),
    "water": path([w["c"] for w in L["water"]], close=True),
    "hpoly": path([h["c"] for h in L["herit_poly"]], close=True),
    "herit": herit, "poi": POI,
    "rule_ew": path(E["rule_lines"]["ew"]["lines"]), "rule_ns": path(E["rule_lines"]["ns"]["lines"]),
    "fg": FG,
    "hist": E["orientation_hist_mod180_len_km"],
    "grid_bearing": E["grid_bearing"],
    "wall_bearing": [w["bearing_NxE"] for w in E["wall_segments"]],
    "periods": E["periods_T"][::2],
    "regions": {k: {"ns": v["ns_x"]["spectrum"][::2], "ew": v["ew_y"]["spectrum"][::2],
                    "ns_best": v["ns_x"]["best_T_100_200"], "ew_best": v["ew_y"]["best_T_100_200"],
                    "ns_p": v["ns_x"]["p_null"], "ew_p": v["ew_y"]["p_null"],
                    "ns_R": v["ns_x"]["R_at_module"], "ew_R": v["ew_y"]["R_at_module"]} for k, v in E["regions"].items()},
    "oos": E["out_of_sample"],
    "phase": E["phase_by_region"],
}

HTML = r"""<title>경주 원도심 층위도</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@700;800&family=IBM+Plex+Sans+KR:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --bg:#edf0ec; --surface:#f6f7f4; --ink:#1b2220; --ink2:#4c5652; --ink3:#78827e; --rule:#cfd6d1;
  --street:#27302d; --street2:#9fa9a4; --silla:#a3740c; --joseon:#35589a; --colonial:#7b45a6;
  --rail:#2a2e33; --railbg:#f6f7f4; --postwar:#12806a; --site:#cd3b22; --survey:#c2267a;
  --water:#c9d8df; --herit:#d8c28a; --fg-filter:none; --fg-op:.32; --chip:#e3e8e4;
  --serif:"Nanum Myeongjo","Noto Serif KR","Batang",serif;
  --sans:"IBM Plex Sans KR","Malgun Gothic","Apple SD Gothic Neo",sans-serif;
  --mono:"IBM Plex Mono","Consolas","D2Coding",monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --bg:#111514; --surface:#181d1c; --ink:#e2e7e4; --ink2:#a6b0ac; --ink3:#7c8783; --rule:#2d3533;
    --street:#d8dfdb; --street2:#56605c; --silla:#d8a83a; --joseon:#86a4e6; --colonial:#bb92e6;
    --rail:#d3d8dc; --railbg:#181d1c; --postwar:#3cc19d; --site:#ff6b4e; --survey:#ff62ac;
    --water:#233238; --herit:#5b4d27; --fg-filter:invert(1); --fg-op:.30; --chip:#232a28;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --bg:#111514; --surface:#181d1c; --ink:#e2e7e4; --ink2:#a6b0ac; --ink3:#7c8783; --rule:#2d3533;
  --street:#d8dfdb; --street2:#56605c; --silla:#d8a83a; --joseon:#86a4e6; --colonial:#bb92e6;
  --rail:#d3d8dc; --railbg:#181d1c; --postwar:#3cc19d; --site:#ff6b4e; --survey:#ff62ac;
  --water:#233238; --herit:#5b4d27; --fg-filter:invert(1); --fg-op:.30; --chip:#232a28;
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.62;margin:0}
.wrap{max-width:1260px;margin:0 auto;padding-inline:clamp(16px,3vw,32px);padding-block:28px 56px;display:grid;gap:28px}
h1,h2,h3{font-family:var(--serif);text-wrap:balance;margin:0;letter-spacing:-.01em}
h1{font-size:clamp(1.9rem,3.6vw,2.7rem);font-weight:800;line-height:1.18}
h2{font-size:1.28rem;font-weight:800}
h3{font-size:1.02rem;font-weight:700}
p{margin:0}
.lede{max-width:68ch;color:var(--ink2);font-size:1.02rem}
.meta{font-family:var(--mono);font-size:.76rem;color:var(--ink3);letter-spacing:.02em}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums}
header{display:grid;gap:12px;border-bottom:1px solid var(--rule);padding-bottom:22px}

/* 판정 */
.verdicts{display:grid;grid-template-columns:1fr;gap:14px}
@media (min-width:620px){.verdicts{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (min-width:1100px){.verdicts{grid-template-columns:repeat(4,minmax(0,1fr))}}
.vd{display:grid;gap:8px;align-content:start;padding:14px 16px;background:var(--surface);border:1px solid var(--rule);border-radius:4px}
.chip{justify-self:start;font-size:.74rem;font-weight:600;letter-spacing:.04em;padding:2px 9px;border-radius:999px;border:1.5px solid currentColor}
.chip.ok{color:var(--postwar)} .chip.meas{color:var(--survey)} .chip.no{color:var(--ink3);border-style:dashed} .chip.cut{color:var(--site)}
.vd p{font-size:.9rem;color:var(--ink2)}

/* 지도 + 연표 */
.stage{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(290px,1fr);gap:22px;align-items:start}
@media (max-width:920px){.stage{grid-template-columns:1fr}}
.mapbox{position:relative;background:var(--surface);border:1px solid var(--rule);border-radius:4px;overflow:hidden}
#map{display:block;width:100%;height:auto;aspect-ratio:1/1;touch-action:none;cursor:grab}
#map.drag{cursor:grabbing}
.mapctl{position:absolute;right:10px;top:10px;display:grid;gap:6px}
.mapctl button{width:34px;height:34px;border:1px solid var(--rule);background:var(--surface);color:var(--ink);font:600 1rem var(--mono);border-radius:4px;cursor:pointer}
.mapctl button:focus-visible,.era:focus-visible,.lay input:focus-visible{outline:2px solid var(--site);outline-offset:2px}
.scale{position:absolute;left:12px;bottom:10px;font:.72rem var(--mono);color:var(--ink2);display:grid;gap:3px}
.scale i{display:block;height:5px;border:1.5px solid var(--ink2);border-top:0}
.lays{display:flex;flex-wrap:wrap;gap:6px 14px;padding:10px 12px;border-top:1px solid var(--rule);font-size:.8rem}
.lay{display:flex;align-items:center;gap:6px;cursor:pointer;color:var(--ink2)}
.lay b{display:inline-block;width:18px;height:3px;border-radius:2px}

.timeline{display:grid;gap:0;border-left:1.5px solid var(--rule);margin-left:6px}
.era{all:unset;display:grid;gap:4px;padding:10px 12px 12px 18px;position:relative;cursor:pointer;border-radius:0 4px 4px 0}
.era::before{content:"";position:absolute;left:-7px;top:16px;width:11px;height:11px;border-radius:50%;background:var(--bg);border:2px solid var(--c,var(--ink3))}
.era:hover{background:var(--chip)}
.era[aria-pressed="true"]{background:var(--surface);box-shadow:inset 3px 0 0 var(--c,var(--ink))}
.era .yr{font-family:var(--mono);font-size:.78rem;color:var(--c,var(--ink3));font-weight:500}
.era h3{font-size:.98rem}
.era p{font-size:.84rem;color:var(--ink2)}
.era .src{font-family:var(--mono);font-size:.7rem;color:var(--ink3)}
.allbtn{all:unset;cursor:pointer;font-size:.8rem;color:var(--ink2);text-decoration:underline;text-underline-offset:3px;margin:0 0 8px 18px}

/* 근거 */
.evidence{display:grid;gap:18px}
.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:4px;padding:14px 16px;display:grid;gap:10px}
.card p{font-size:.86rem;color:var(--ink2)}
.chart svg{width:100%;height:auto;display:block}
.tblwrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.82rem}
th,td{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:right;white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{font-weight:600;color:var(--ink2)}
td.hi{color:var(--survey);font-weight:600}
td.lo{color:var(--ink3)}
.sources{font-size:.8rem;color:var(--ink2);display:grid;gap:4px;max-width:90ch}
.sources b{font-family:var(--mono);font-weight:500;color:var(--ink)}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
.dim{opacity:.13;transition:opacity .25s}
.lit{transition:opacity .25s}
</style>

<div class="wrap">
<header>
  <p class="meta">구경주역 지구단위계획 · 조직 분석 · 2026-09-28 · EPSG:5187</p>
  <h1>경주 원도심 층위도</h1>
  <p class="lede">지금 원도심 가로의 어떤 선이 어느 시대에서 왔고 어떤 선이 그것을 끊었는지를, 국토지리정보원 수치지도 실측과 발표·연구 문헌으로 나눠 판정했다. 연표를 누르면 그 시대의 선이 지도에서 떠오른다.</p>
</header>

<section class="verdicts" aria-label="판정">
  <div class="vd"><span class="chip ok">이어졌다 · 실측+문헌</span><h3>방위</h3>
    <p>원도심 도로중심선의 <span class="num">57%</span>, 긴 건물의 <span class="num">66%</span>가 한 축(<span class="num">__GRID__</span>)에 선다. 발굴된 신라 도로도 진북에 정렬하고(황인호 2011), 읍성 동벽 현존 구간도 <span class="num">N0.0–2.3°E</span>다. 1915년 본정통과 1936년 화랑로도 같은 축이라, 방위만으로 시대를 가를 수는 없다.</p></div>
  <div class="vd"><span class="chip meas">있다 · 읍성에서 번졌을 가능성</span><h3>약 150 m 동서선</h3>
    <p>동서 가로가 <span class="num">147.5 m</span> 간격으로 반복되고, 읍성 권역과 성동·황오동의 위상 차가 <span class="num">3 m</span>다. 읍성 사각형(남북 약 <span class="num">600 m</span>) 안 북문로·북성로·화랑로(남벽선)가 이 간격 안팎(±10–16 m)에 놓인다. 읍성의 선이 1936년 역 쪽으로 이어진 층으로 읽힌다.</p></div>
  <div class="vd"><span class="chip no">원도심 전체로는 입증 안 됨</span><h3>신라 방리의 위치 계승</h3>
    <p>신라 모듈(1단계 <span class="num">163.3 m</span>, 2단계 <span class="num">156.2 m</span>)이 원도심 전체에 일관되게 나오지 않는다. 다만 황룡사·인왕동 쪽 남북 가로 간격 <span class="num">161.5 m</span>는 1단계 모듈과 <span class="num">1.1%</span> 차다. 유적 정비로 다시 놓인 길일 수도 있어, 1913년 지적원도로 확인해야 한다.</p></div>
  <div class="vd"><span class="chip cut">끊었다 · 실측+문헌</span><h3>근대의 사선과 장벽</h3>
    <p>축을 벗어난 큰 선은 몇 개뿐이다. 태종로(<span class="num">N79°E</span>, 1909 신작로·1918 협궤선이라는 주장), 철도(1918·1936), 북천 변 알천로, 1980년 산업로에 직교하는 동천동 격자(<span class="num">N47.5°E</span>)다. 폐선 부지를 가로지르는 최단 경로는 직선의 <span class="num">2.55배</span>다.</p></div>
</section>

<section class="stage">
  <div>
    <div class="mapbox">
      <svg id="map" viewBox="0 0 __VW__ __VH__" role="img" aria-label="경주 원도심 가로와 시대별 층위 지도"></svg>
      <div class="mapctl"><button id="zin" aria-label="확대">+</button><button id="zout" aria-label="축소">−</button><button id="zre" aria-label="처음 보기">○</button></div>
      <div class="scale" aria-hidden="true"><span>500 m · Ctrl/⌘ + 휠로 확대, 끌어서 이동</span><i id="sbar"></i></div>
    </div>
    <div class="lays" id="lays"></div>
  </div>
  <div>
    <h2 style="margin:0 0 10px">연표</h2>
    <button class="allbtn" id="allbtn">모든 층 함께 보기</button>
    <div class="timeline" id="timeline"></div>
  </div>
</section>

<section class="evidence">
  <h2>판정 근거</h2>
  <div class="charts">
    <div class="card chart"><h3>가로 방위 분포</h3><div id="c_hist"></div>
      <p>도로중심선 212 km의 방위(길이가중, 1° 간격). 0°·90°에 가까운 두 봉우리가 한 축의 남북·동서 가로다. 사선 A는 동천동 회전 격자, 사선 B는 북천 변 도로.</p></div>
    <div class="card chart"><h3>가로 간격 스펙트럼</h3><div id="c_spec"></div>
      <p>격자 축에 맞춘 가로들의 위치가 어떤 간격으로 되풀이되는지(1이면 완전 주기). 권역을 누르면 선이 바뀐다. 세로선은 문헌의 방 크기와 실측 봉우리.</p>
      <div id="specbtns" style="display:flex;flex-wrap:wrap;gap:6px"></div></div>
  </div>
  <div class="card"><h3>표본 외 위상 검정 — 한 격자가 원도심 전체를 덮는가</h3>
    <p>원도심 중앙 3권역에서 <span class="num">164×140 m</span> 모듈의 위상을 잡고, 그 격자선 ±6 m 안에 드는 가로 길이의 비율을 무작위 기대치와 비교했다. 배율이 1보다 크면 격자선에 붙어 있다는 뜻이다. 중앙 3권역은 위상을 잡은 곳이라 참고값이다.</p>
    <div class="tblwrap"><table id="t_oos"></table></div></div>
  <div class="card"><h3>읽는 법과 한계</h3>
    <p>세 층이 같은 방위를 나눠 가져서 방향만으로는 층을 가를 수 없다. 발굴된 신라 도로, 조선 읍성, 1915·1936년 근대 가로가 모두 같은 방향이다. 가장 그럴듯한 해석은 이렇다. 진북 격자가 경지와 필지선으로 오래 남았고, 읍성이 그 위에 앉았다. 근대 도로는 읍성의 네 변과 십자축을 따라 넓혀지며 역 쪽으로 이어졌다. 신라 방이 제자리에 남았는지는 1913년 지적원도(국가기록원)와 1916년 1:10,000 「경주」 지도, 발굴 도로 좌표를 겹쳐야 판정할 수 있다. 수치지도는 현재 상태여서, 유적 정비로 다시 놓인 길과 원래 길을 구별하지 못한다.</p></div>
  <div class="sources" id="sources"></div>
</section>
</div>

<script>
const D = __DATA__;
const NS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("map");
const VW = D.view[0], VH = D.view[1];
function el(tag, attrs, parent){
  // CSS 변수(var(--…))는 표현 속성 대신 style 로 넣어야 모든 브라우저에서 테마를 따른다
  const e = document.createElementNS(NS, tag); let st = attrs.style || "";
  for (const k in attrs){ if (k === "style") continue; const v = attrs[k];
    if (typeof v === "string" && v.includes("var(")) st += `${k}:${v};`; else e.setAttribute(k, v); }
  if (st) e.setAttribute("style", st);
  (parent||svg).appendChild(e); return e; }
function cssv(n){ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }

// ── 레이어 ───────────────────────────────────────────
const G = {}; const LAB = []; const MARK = [];
function group(id){ G[id] = el("g", {id:"g_"+id, class:"lit"}); return G[id]; }
group("water"); el("path", {d:D.water, fill:"var(--water)", stroke:"none"}, G.water);
group("herit"); el("path", {d:D.hpoly, fill:"var(--herit)", "fill-opacity":.55, stroke:"var(--silla)", "stroke-width":1, "vector-effect":"non-scaling-stroke"}, G.herit);
group("fg"); el("image", {href:"data:image/png;base64,"+D.fg, x:0, y:0, width:VW, height:VH, style:"filter:var(--fg-filter);opacity:var(--fg-op)"}, G.fg);
const SW = {major:2.4, mid:1.3, minor:.7};
group("street_other"); group("street_B"); group("street_A"); group("street_grid");
for (const k in D.streets){
  const [sys, w] = k.split("_");
  const col = sys==="grid" ? "var(--street)" : sys==="A"||sys==="B" ? "var(--postwar)" : "var(--street2)";
  el("path", {d:D.streets[k], fill:"none", stroke:col, "stroke-width":SW[w], "stroke-linecap":"round", "vector-effect":"non-scaling-stroke", "stroke-opacity": sys==="B" ? .75 : 1}, G["street_"+sys]);
}
group("rule");
el("path", {d:D.rule_ew, fill:"none", stroke:"var(--survey)", "stroke-width":1.6, "stroke-dasharray":"2 5", "vector-effect":"non-scaling-stroke"}, G.rule);
el("path", {d:D.rule_ns, fill:"none", stroke:"var(--survey)", "stroke-width":1.6, "stroke-dasharray":"2 5", "vector-effect":"non-scaling-stroke"}, G.rule);
group("rail");
el("path", {d:D.railpoly, fill:"var(--rail)", "fill-opacity":.08, stroke:"none"}, G.rail);
el("path", {d:D.rail, fill:"none", stroke:"var(--rail)", "stroke-width":3.2, "vector-effect":"non-scaling-stroke"}, G.rail);
el("path", {d:D.rail, fill:"none", stroke:"var(--railbg)", "stroke-width":1.4, "stroke-dasharray":"6 6", "vector-effect":"non-scaling-stroke"}, G.rail);
const ROADERA = {"봉황로":"joseon","중앙로":"joseon","북성로":"joseon","북문로":"joseon","동문로":"joseon","금성로":"joseon","화랑로":"colonial","태종로":"colonial","원화로":"colonial","알천북로":"postwar","알천남로":"postwar"};
for (const n in D.named){
  const era = ROADERA[n]; if (!era) continue;
  const g = G["road_"+n] || group("road_"+n);
  el("path", {d:D.named[n], fill:"none", stroke:"var(--"+era+")", "stroke-width":6, "stroke-opacity":.55, "stroke-linecap":"round", "vector-effect":"non-scaling-stroke"}, g);
}
group("wall"); el("path", {d:D.wall, fill:"none", stroke:"var(--joseon)", "stroke-width":7, "stroke-linecap":"round", "vector-effect":"non-scaling-stroke"}, G.wall);
group("zone"); el("path", {d:D.zone, fill:"var(--site)", "fill-opacity":.10, stroke:"var(--site)", "stroke-width":2.6, "vector-effect":"non-scaling-stroke"}, G.zone);
group("heritpt");
for (const h of D.herit){
  const c = el("circle", {cx:h.p[0], cy:h.p[1], r:10, fill:"var(--silla)"}, G.heritpt); MARK.push([c,"c",h.p]);
  const t = el("text", {x:h.p[0]+16, y:h.p[1]+8, "font-size":34, fill:"var(--silla)", "font-family":"var(--sans)", "font-weight":600, "paint-order":"stroke", stroke:"var(--surface)", "stroke-width":7}, G.heritpt); t.textContent = h.n; LAB.push([t,h.p,1]);
}
const POICOL = {c1918:"colonial", c1936:"colonial", jiph:"joseon", gate:"joseon", post:"colonial", court:"colonial", police:"colonial", smkt:"colonial", cmkt:"colonial", gwansa:"colonial"};
group("poi");
for (const p of D.poi){
  const c = "var(--"+(POICOL[p.k]||"ink")+")";
  const r = el("rect", {x:p.p[0]-11, y:p.p[1]-11, width:22, height:22, fill:c, stroke:"var(--surface)", "stroke-width":3, transform:`rotate(45 ${p.p[0]} ${p.p[1]})`}, G.poi); MARK.push([r,"r",p.p]);
  const t = el("text", {x:p.p[0]+18, y:p.p[1]-14, "font-size":34, fill:c, "font-family":"var(--sans)", "font-weight":600, "paint-order":"stroke", stroke:"var(--surface)", "stroke-width":7}, G.poi); t.textContent = p.n; LAB.push([t,p.p,-1]);
}

// ── 레이어 토글 ─────────────────────────────────────────
const LAYERS = [
  ["street_grid","주 격자 가로 (N0.8°E)","var(--street)"], ["street_A","사선 A·B 가로","var(--postwar)"], ["street_other","기타 가로","var(--street2)"],
  ["fg","건물","var(--ink3)"], ["rule","실측 규칙선","var(--survey)"], ["rail","철도(동해남부선)","var(--rail)"],
  ["wall","읍성 성벽 현존","var(--joseon)"], ["herit","유적 구역","var(--silla)"], ["zone","구경주역 지구단위계획구역","var(--site)"]];
const lays = document.getElementById("lays");
for (const [id, label, col] of LAYERS){
  const lab = document.createElement("label"); lab.className = "lay";
  lab.innerHTML = `<input type="checkbox" id="L_${id}" checked><b style="background:${col}"></b>${label}`;
  lays.appendChild(lab);
  lab.querySelector("input").addEventListener("change", e => {
    const on = e.target.checked;
    const ids = id==="street_A" ? ["street_A","street_B"] : [id];
    ids.forEach(i => { if (G[i]) G[i].style.display = on ? "" : "none"; });
  });
}

// ── 연표 ───────────────────────────────────────────────
const ERAS = __ERAS__;
const tl = document.getElementById("timeline");
let current = null;
function focusEra(e){
  const keep = e ? new Set(e.layers) : null;
  for (const id in G){
    const always = ["fg","water","zone"].includes(id);
    G[id].classList.toggle("dim", !!keep && !always && !keep.has(id));
  }
  document.querySelectorAll(".era").forEach(b => b.setAttribute("aria-pressed", e && b.dataset.k===e.k ? "true":"false"));
  current = e ? e.k : null;
}
for (const e of ERAS){
  const b = document.createElement("button"); b.className = "era"; b.dataset.k = e.k; b.style.setProperty("--c", "var(--"+e.c+")");
  b.setAttribute("aria-pressed","false");
  b.innerHTML = `<span class="yr">${e.yr}</span><h3>${e.t}</h3><p>${e.d}</p><span class="src">${e.src}</span>`;
  b.addEventListener("click", () => focusEra(current===e.k ? null : e));
  tl.appendChild(b);
}
document.getElementById("allbtn").addEventListener("click", () => focusEra(null));

// ── 확대·이동 ────────────────────────────────────────────
let vb = [0,0,VW,VH];
function setVB(){ svg.setAttribute("viewBox", vb.join(" ")); const px = svg.clientWidth || 800; document.getElementById("sbar").style.width = (500/vb[2]*px)+"px";
  const k = vb[2]/px;   // 화면 1 px 에 해당하는 m — 라벨 12 px, 마커 5 px 로 유지
  for (const [t,p,dir] of LAB){ t.setAttribute("font-size", 12*k); t.setAttribute("x", p[0]+9*k); t.setAttribute("y", p[1]+(dir>0?4:-6)*k); t.style.strokeWidth = 3*k; }
  for (const [m,kind,p] of MARK){ const r = 5*k; if (kind==="c") m.setAttribute("r", r); else { m.setAttribute("x", p[0]-r); m.setAttribute("y", p[1]-r); m.setAttribute("width", 2*r); m.setAttribute("height", 2*r); m.style.strokeWidth = 1.5*k; } } }
function zoom(f, cx, cy){ const nw = Math.min(VW, Math.max(250, vb[2]*f)); cx = cx ?? vb[0]+vb[2]/2; cy = cy ?? vb[1]+vb[3]/2;
  vb = [cx-(cx-vb[0])*nw/vb[2], cy-(cy-vb[1])*nw/vb[3], nw, nw]; setVB(); }
document.getElementById("zin").onclick = () => zoom(0.7);
document.getElementById("zout").onclick = () => zoom(1/0.7);
document.getElementById("zre").onclick = () => { vb=[0,0,VW,VH]; setVB(); };
svg.addEventListener("wheel", ev => { if (!ev.ctrlKey && !ev.metaKey) return; ev.preventDefault(); const r = svg.getBoundingClientRect();
  const cx = vb[0]+(ev.clientX-r.left)/r.width*vb[2], cy = vb[1]+(ev.clientY-r.top)/r.height*vb[3]; zoom(ev.deltaY>0 ? 1.15 : 1/1.15, cx, cy); }, {passive:false});
let drag = null;
svg.addEventListener("pointerdown", ev => { drag = {x:ev.clientX, y:ev.clientY, vb:[...vb]}; svg.setPointerCapture(ev.pointerId); svg.classList.add("drag"); });
svg.addEventListener("pointermove", ev => { if (!drag) return; const r = svg.getBoundingClientRect();
  vb[0] = drag.vb[0]-(ev.clientX-drag.x)/r.width*vb[2]; vb[1] = drag.vb[1]-(ev.clientY-drag.y)/r.height*vb[3]; setVB(); });
svg.addEventListener("pointerup", () => { drag = null; svg.classList.remove("drag"); });
window.addEventListener("resize", setVB); setVB();

// ── 차트: 방위 분포 ────────────────────────────────────────
function chartHist(){
  const W = 560, H = 230, m = {l:44, r:14, t:14, b:38};
  const box = document.getElementById("c_hist"); box.innerHTML = "";
  const s = document.createElementNS(NS,"svg"); s.setAttribute("viewBox",`0 0 ${W} ${H}`); box.appendChild(s);
  const h = D.hist, mx = Math.max(...h), x = i => m.l + i/180*(W-m.l-m.r), y = v => H-m.b - v/mx*(H-m.t-m.b);
  for (let v=0; v<=mx; v+= Math.ceil(mx/4)){ el("line",{x1:m.l,x2:W-m.r,y1:y(v),y2:y(v),stroke:"var(--rule)"},s);
    const t=el("text",{x:m.l-6,y:y(v)+4,"text-anchor":"end","font-size":11,fill:"var(--ink3)","font-family":"var(--mono)"},s); t.textContent=v; }
  h.forEach((v,i) => el("rect",{x:x(i),y:y(v),width:(W-m.l-m.r)/180,height:H-m.b-y(v),fill:"var(--street)"},s));
  // 동=0° 반시계 기준. 남북 가로 ≈ 89.2°, 동서 가로 ≈ 179.2°/−0.8°
  const marks = [[89.25,"주 격자 남북","var(--street)"],[179.25,"주 격자 동서","var(--street)"],[42,"사선 A","var(--postwar)"],[148,"사선 B","var(--postwar)"],
                 [90-D.wall_bearing[1],"읍성 동벽","var(--joseon)"]];
  marks.forEach(([a,lab,c],k) => { const X = x(a); el("line",{x1:X,x2:X,y1:m.t,y2:H-m.b,stroke:c,"stroke-dasharray":"3 3","stroke-width":1.3},s);
    const t=el("text",{x:Math.min(W-m.r-2,X+3),y:m.t+11+(k%3)*13,"font-size":11,fill:c,"font-family":"var(--sans)","text-anchor":X>W-90?"end":"start"},s); t.textContent=lab; });
  [0,45,90,135,180].forEach(a => { const t=el("text",{x:x(a),y:H-m.b+15,"text-anchor":"middle","font-size":11,fill:"var(--ink3)","font-family":"var(--mono)"},s); t.textContent=a+"°"; });
  const t=el("text",{x:(m.l+W-m.r)/2,y:H-6,"text-anchor":"middle","font-size":11,fill:"var(--ink2)"},s); t.textContent="가로 방위 (동=0°, 반시계, mod 180) · 세로축 km";
}
// ── 차트: 간격 스펙트럼 ─────────────────────────────────────
let specRegion = "읍성 권역(동부·서부·북부동)";
function chartSpec(){
  const W = 560, H = 250, m = {l:40, r:14, t:14, b:38};
  const box = document.getElementById("c_spec"); box.innerHTML = "";
  const s = document.createElementNS(NS,"svg"); s.setAttribute("viewBox",`0 0 ${W} ${H}`); box.appendChild(s);
  const T = D.periods, x = t => m.l + (t-T[0])/(T[T.length-1]-T[0])*(W-m.l-m.r), y = v => H-m.b - v/0.6*(H-m.t-m.b);
  [0,.2,.4,.6].forEach(v => { el("line",{x1:m.l,x2:W-m.r,y1:y(v),y2:y(v),stroke:"var(--rule)"},s);
    const t=el("text",{x:m.l-6,y:y(v)+4,"text-anchor":"end","font-size":11,fill:"var(--ink3)","font-family":"var(--mono)"},s); t.textContent=v.toFixed(1); });
  [[120,"120"],[140,"140"],[147.5,"147.5"],[161.5,"161.5"],[164,"164"]].forEach(([t0,lab],k) => { const X=x(t0);
    el("line",{x1:X,x2:X,y1:m.t,y2:H-m.b,stroke: t0===147.5||t0===161.5 ? "var(--survey)":"var(--silla)","stroke-dasharray":"3 3"},s);
    const tt=el("text",{x:X,y:m.t+10+(k%2)*12,"text-anchor":"middle","font-size":10.5,fill: t0===147.5||t0===161.5 ? "var(--survey)":"var(--silla)","font-family":"var(--mono)"},s); tt.textContent=lab; });
  const r = D.regions[specRegion];
  const line = (arr,c,dash) => { let d=""; arr.forEach((v,i)=>{ d += (i?"L":"M")+x(T[i]).toFixed(1)+" "+y(v).toFixed(1); }); el("path",{d,fill:"none",stroke:c,"stroke-width":2,"stroke-dasharray":dash||""},s); };
  const ctrl = D.regions["동천동(대조군)"];
  line(ctrl.ew,"var(--ink3)","2 3");
  line(r.ns,"var(--joseon)"); line(r.ew,"var(--site)");
  [["남북 가로(동서 간격)","var(--joseon)",""],["동서 가로(남북 간격)","var(--site)",""],["동천동 대조군 동서","var(--ink3)","2 3"]].forEach(([lab,c,dash],k) => {
    el("line",{x1:W-m.r-150,x2:W-m.r-128,y1:m.t+44+k*14,y2:m.t+44+k*14,stroke:c,"stroke-width":2,"stroke-dasharray":dash},s);
    const t=el("text",{x:W-m.r-124,y:m.t+48+k*14,"font-size":10.5,fill:"var(--ink2)"},s); t.textContent=lab; });
  [50,100,150,200,250].forEach(t0 => { const t=el("text",{x:x(t0),y:H-m.b+15,"text-anchor":"middle","font-size":11,fill:"var(--ink3)","font-family":"var(--mono)"},s); t.textContent=t0; });
  const t=el("text",{x:(m.l+W-m.r)/2,y:H-6,"text-anchor":"middle","font-size":11,fill:"var(--ink2)"},s); t.textContent="반복 간격 T (m) · 세로축 주기 강도 R";
}
const sb = document.getElementById("specbtns");
Object.keys(D.regions).forEach(k => { if (k.includes("대조군")) return; const b=document.createElement("button");
  b.textContent=k; b.className="lay"; b.style.cssText="all:unset;cursor:pointer;font-size:.78rem;padding:3px 9px;border:1px solid var(--rule);border-radius:999px;color:var(--ink2)";
  b.addEventListener("click",()=>{ specRegion=k; sb.querySelectorAll("button").forEach(x=>x.style.background=""); b.style.background="var(--chip)"; chartSpec(); });
  if (k===specRegion) b.style.background="var(--chip)"; sb.appendChild(b); });
// ── 표 ────────────────────────────────────────────────
function tableOOS(){
  const t = document.getElementById("t_oos");
  let h = "<tr><th>권역</th><th>남북 가로 격자선 ±6 m</th><th>배율</th><th>동서 가로 격자선 ±6 m</th><th>배율</th><th>비고</th></tr>";
  for (const k in D.oos){ const r = D.oos[k];
    const c = v => v>=1.5 ? "hi" : v<1 ? "lo" : "";
    h += `<tr><td>${k}</td><td class="num">${(r.ns_x.share_within_6m*100).toFixed(1)}%</td><td class="num ${c(r.ns_x.lift)}">×${r.ns_x.lift.toFixed(2)}</td>`+
         `<td class="num">${(r.ew_y.share_within_6m*100).toFixed(1)}%</td><td class="num ${c(r.ew_y.lift)}">×${r.ew_y.lift.toFixed(2)}</td><td>${r.in_sample?"위상 추정 권역":"표본 외"}</td></tr>`; }
  t.innerHTML = h + `<tr><td class="lo">무작위 기대</td><td class="num lo">7.3%</td><td class="num lo">×1.00</td><td class="num lo">8.6%</td><td class="num lo">×1.00</td><td></td></tr>`;
}
document.getElementById("sources").innerHTML = __SOURCES__;
chartHist(); chartSpec(); tableOOS();
</script>
"""

ERAS = [
    {"k": "silla", "yr": "6–8세기", "t": "신라 왕경 방리", "c": "silla", "layers": ["herit", "heritpt", "rule"],
     "d": "진북에 정렬한 격자다. 모듈은 1단계 460척(163.3 m), 2단계 440척(156.2 m), 3단계 450×350척이다. 서부동 19번지·북문로·전랑지 서측에서 통일신라 도로가 발굴됐다. 자홍 점선은 실측 규칙선이며 신라선으로 확정된 것이 아니다.",
     "src": "황인호 2009·2011 [T3] · 발굴보고서 원문 미확보 [T2] · 채미옥 2026 [T4]"},
    {"k": "joseon", "yr": "1012 · 1378 · 1746", "t": "경주읍성, 네 변이 길이 되다", "c": "joseon", "layers": ["wall", "road_봉황로", "road_북성로", "road_북문로", "road_동문로", "road_화랑로", "road_금성로", "poi"],
     "d": "성곽 사각형은 북문로(북)·동문로(동)·화랑로(남벽선)·금성로(서쪽 해자)로 남았을 가능성이 높다. 네 도로 둘레 약 2.44 km로, 확인된 석축 둘레 2,412 m와 맞는다. 성 안 십자축은 봉황로(남북)와 북성로(동서)다.",
     "src": "한국민족문화대백과 [T3] · 도로-성벽 대응은 T4+좌표 대조"},
    {"k": "c1912", "yr": "1912 · 1915", "t": "남문 철거와 본정통", "c": "colonial", "layers": ["road_봉황로", "wall"],
     "d": "1912년 남문 징례문을 헐었다. 1915년 성벽을 뚫고 봉황로 남쪽 직선 구간(본정통)을 냈다. 새 길은 사선이 아니라 기존 남북축 위에 놓였다.",
     "src": "김신재 2009 재인용 [T3] · 박정호 2026 [T4]"},
    {"k": "c1918", "yr": "1909 · 1918", "t": "신작로·협궤와 첫 경주역", "c": "colonial", "layers": ["rail", "road_태종로", "poi"],
     "d": "사정리(현 서라벌문화회관)에 첫 경주역이 섰다. 역은 태종로 남쪽에 붙어 있다. 태종로가 1909년 대구–경주 신작로이자 1918–36년 협궤선이었다는 주장이 있다(T4). 실측 방위 N79°E로 격자를 비스듬히 가른다.",
     "src": "경주시 2025 원도심 연구 p22 [T2] · 경북매일 [T4] · 실측"},
    {"k": "c1936", "yr": "1936.12.1", "t": "역 이전, 남벽이 화랑로가 되다", "c": "colonial", "layers": ["rail", "road_화랑로", "road_원화로", "poi", "zone"],
     "d": "표준궤 개량과 함께 역이 성동리로 옮겨 왔다. 역 이전 때 낸 도로로 읍성 남벽이 완전히 헐렸고, 그 선이 화랑로로 보인다. 화랑로를 따라 우체국·법원·경찰서·시장이 섰다.",
     "src": "김신재 2013 초록 [T3] · 관보 고시 제640호(T4 경유) · 경주시 2025 [T2]"},
    {"k": "postwar", "yr": "1952 · 1980", "t": "하천 변 도로와 회전 격자", "c": "postwar", "layers": ["street_A", "street_B", "road_알천북로", "road_알천남로"],
     "d": "1952년 경주도시계획결정안에 토지구획정리지구가 들었다(목록만 확인). 동천동 회전 격자(N47.5–50°E)는 1980년 산업로(N40°W)와 직교한다. 산업로를 기준선으로 구획정리했다는 가설은 아직 미확인이다. 알천남·북로는 북천 물길(N55°W)을 따른다.",
     "src": "박병주 아카이브 목록 [T4] · 실측 · 사업 연대 확인 필요"},
    {"k": "y2021", "yr": "2021", "t": "폐선, 끊긴 자리가 부지가 되다", "c": "site", "layers": ["zone", "rail", "rule"],
     "d": "구역 남북 985 m 사이에 도로 횡단이 없다. 147.5 m 동서선 가운데 셋(화랑로 포함)은 부지 양쪽에 같은 선의 가로가 있어, 끊긴 틀선이다. 폐선 부지를 가로지르는 최단 경로는 직선의 2.55배다.",
     "src": "실측(수치지도 2026-09-13 취득) · map16"},
]
SOURCES = ("<p><b>실측</b> 국토지리정보원 연속수치지도(2026-09-13 취득, T2): 도로중심선 10,617개·건물 23,579동·성곽 주기, EPSG:5179→5187.</p>"
           "<p><b>T3</b> 황인호(2011) 「新羅王京の整備における基準線と尺度」 奈良文化財研究所学報 87, pp.23–51 · Hwang In-ho(2009) Changes in the Silla Capital's Road and Urban Structure, IJKH 14 · 小澤毅(2011) 学報 87 · 김신재(2011·2013) 『신라문화』 38·41 · 박훈(2012) 대한건축학회연합논문집 14(1) · 장승엽(2020) 『신라문화』 57 · 강봉원(2008) 『대구사학』 90(격자 회의론). 논문 대부분은 초록·요약 기준이다.</p>"
           "<p><b>T2</b> 경주시(2025) 「경주시 원도심 미래구상 기획 연구」 p18–28 · 국가유산청(2026) 신라왕경 핵심유적 복원·정비 종합계획. 발굴보고서(서부동 19번지, 북문로, 전랑지, 『慶州邑城』)는 원문을 아직 확보하지 못했다.</p>"
           "<p><b>T4</b> 채미옥(2026.9.12) LOWCA 워크숍 발표 · 박정호(2026) 도시재생 강연 · 도로–성벽 대응(위키·나무위키·언론)과 좌표 대조. 박정호 슬라이드의 옛 역 풍경은 생성 이미지라 근거에서 뺐다.</p>"
           "<p><b>방법</b> 간격 스펙트럼 R(T)=|Σw·e<sup>2πix/T</sup>|/Σw, 가로 선 길이 가중, 무작위 흔들기 500회 귀무. 권역은 가로 선분에서 가장 가까운 건물의 법정동. 스크립트 pipeline/build_palimpsest_evidence.py.</p>")

page = (HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
        .replace("__ERAS__", json.dumps(ERAS, ensure_ascii=False))
        .replace("__SOURCES__", json.dumps(SOURCES, ensure_ascii=False))
        .replace("__VW__", str(VW)).replace("__VH__", str(VH))
        .replace("__GRID__", DATA["grid_bearing"]))
OUT.write_text(page, encoding="utf-8")
print("saved", OUT, round(OUT.stat().st_size / 1024), "KB")
