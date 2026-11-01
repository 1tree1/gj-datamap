"""S2 단면 조닝 다이어그램 — 일러스트레이터 벡터 시트(참고: 서대구역 '입체적 도시' — 사례 사진 3단 + 강조 문구 + 굵은 용도 블록 단면)
- 위 3칸: 라이노 단면 투시(클리핑 평면, DIAGRAMS 표시 모드, r0_rhino_clip.py) → 포토샵 후처리(p0_ps_panels.py)
- 아래: cuts.pkl(최종본 절단) 기반 용도 블록·지면·나무·사람·붉은 점선 동선·N/S 루프 화살표·지반 띠
JSX를 생성해 Illustrator.Application COM(DoJavaScriptFile)으로 실행 → diagrams/D6~D8_*.ai/.pdf/.png
사용: python s2_ai_sections.py [V|H|Dg ...]"""
import os, sys, json, math, pickle, subprocess, random
import numpy as np
from shapely.geometry import LineString, Point
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); OUTD = os.path.abspath(os.path.join(HERE, "..", "diagrams"))
CL = os.path.abspath(os.path.join(HERE, "..", "sheets", "clip"))
CUTS = pickle.load(open(os.path.join(D, "cuts.pkl"), "rb"))
M = pickle.load(open(os.path.join(D, "model.pkl"), "rb")); BLD = M["BLD"]
CF = pickle.load(open(os.path.join(D, "ctx_fixed.pkl"), "rb"))["B"]
PW, PH = 400.0, 225.0
SALMON = "#E8776A"; RED = "#E0393E"; TEAL = "#1F4E5F"; INK = "#222222"; GREY = "#6b6b6b"
FH = {"주거": 3.0, "주차": 3.2, "역사": 4.5}
CAT = {"판매": "#D93F87", "생활SOC": "#13998B", "창작": "#6B2C91", "역사": "#B5562A", "주차": "#7A7F87", "방문자": "#8FA1B3",
       "공공업무": "#4C6FB5", "업무·창업": "#E46B3A", "문화": "#2B6CB0"}
BCOL = {"실내 체험관": "#1D2F5C", "근대역사관": "#1E9BD7", "복합문화센터": "#2B6CB0", "지역문화원 본동": "#2B6CB0"}
HOUSE = ("#F08A5D", "#F7CF6E")                                              # 주거 그라데이션(위 → 아래)

SHEETS = {
    "V": dict(file="D6_단면조닝_남북", tag="A", title="단면 조닝 A–A′ · 남북",
              sub=[("체육관에서 전시관까지, 대지축을 따라 ", None), ("정주 · 생활문화 · 체험 · 전시", SALMON), ("의 입체적 연계", None)],
              panels=[("북측 · 체육관·주거시설", "“생활체육 / 1층 커뮤니티 · 2~5층 주거”"), ("중앙 · 복합문화공간·중앙 인도", "“생활문화 + 동서 선형공원”"),
                      ("남측 · 실내체험관·전시관", "“체험 / 작가 교류 / 전시”")],
              head=[("대지축 위의 생활 단면 ", 17), ("(정주 · 생활문화 · 체험 · 전시의 연속)", 11)],
              ground_cap="대지축 + 원도심 생활권", ends=("N", "S"),
              bld=[("체육관", ["생활체육관·편의시설"]), ("주거시설", ["주거동 1", "주거동 3", "주거동 5", "주거동 7"]), ("복합문화공간", ["복합문화센터"]),
                   ("실내체험관 · 작가 교류·행사실", ["실내 체험관"]), ("전시관", ["근대역사관"])],
              note={"주거시설": "1층 커뮤니티 · 2~5층 주거"}, comm_1f=["주거동 1", "주거동 3", "주거동 5", "주거동 7"],
              gl=[("북측 근린공원", "북측 근린공원"), ("향일문 조망로", "향일문 조망로"), ("중앙 인도", "동서 선형공원·가로광장(폭 40m)"), ("남측 차도", "동서 도로")]),
    "H": dict(file="D7_단면조닝_동서", tag="B", title="단면 조닝 B–B′ · 동서",
              sub=[("휴게공간에서 레지던시까지, 공예·체험 가구가 ", None), ("중앙 남북 인도", SALMON), ("에서 만나는 단면", None)],
              panels=[("서측 · 휴게공간·야외체험관", "“휴게 / 야외 체험 / 공예 마켓”"), ("중앙 · 공방·전시동·중앙 남북 인도", "“공방 / 전시 / 남북 보행”"),
                      ("동측 · 실내체험관·레지던시", "“체험 / 제작 / 거주”")],
              head=[("공예·체험 가구의 동서 연계 ", 17), ("(휴게 · 야외 체험 · 공방 · 실내 체험 · 레지던시)", 11)],
              ground_cap="공예·체험 가구 + 원도심", ends=("W", "E"),
              bld=[("휴게공간", ["공방·판매동"]), ("공방·전시동", ["전통문화 공방·전시·공예마켓동"]), ("실내체험관", ["실내 체험관"]),
                   ("제작동", ["레지던시 제작동 1"]), ("거주동", ["레지던시 거주동 1"])],
              group=("레지던시", ["제작동", "거주동"]), note={}, comm_1f=[],
              gl=[("야외체험관", "공예 중정(근린공원)"), ("중앙 남북 인도", "남북 중앙 보행축(폭 30m)"), ("레지던시 마당", "레지던시 마당")]),
    "Dg": dict(file="D8_단면조닝_사선", tag="C", title="단면 조닝 C–C′ · 사선",
               sub=[("경주회관 앞마당에서 전시관까지, ", None), ("구 경주역사의 어댑티브 리유즈", SALMON), ("와 관광객 동선", None)],
               panels=[("서측 · 경주회관 앞마당·근대역사관", "“역 앞 광장 / 근대역사관”"), ("중앙 · 그레이트 코트·지역문화원", "“유리 지붕 중정 / 지역문화원”"),
                       ("동측 · 남측 관광객 인도·전시관", "“관광객 동선 / 전시관”")],
               head=[("구 경주역 어댑티브 리유즈 단면 ", 17), ("(근대역사관 · 그레이트 코트 · 전시관)", 11)],
               ground_cap="구 경주역 + 관광 동선", ends=("W", "E"),
               bld=[("근대역사관", ["구 경주역사"]), ("지역문화원", ["지역문화원 본동"]), ("전시관", ["근대역사관"])],
               note={"지역문화원": "1층 소상공인 점포 · 2~5층 문화"}, comm_1f=[],
               gl=[("경주회관 앞마당", "역전광장"), ("그레이트 코트", "그레이트 코트(유리 지붕 중정)"), ("남측 관광객 인도", "관문광장·사선 보행축(폭 20m)")]),
}


def js(s): return json.dumps(s, ensure_ascii=True)


PRE = r"""
var K = 72 / 25.4;
function rgb(h) { var c = new RGBColor(); c.red = parseInt(h.substr(1, 2), 16); c.green = parseInt(h.substr(3, 2), 16); c.blue = parseInt(h.substr(5, 2), 16); return c; }
var doc = app.documents.add(DocumentColorSpace.RGB, %(W)f * K, %(H)f * K);
doc.artboards[0].artboardRect = [0, 0, %(W)f * K, -%(H)f * K];
var LY = {};
function layer(n) { if (!LY[n]) { LY[n] = doc.layers.add(); LY[n].name = n; } doc.activeLayer = LY[n]; }
function sty(it, fill, stroke, sw, op) {
  if (fill) { it.filled = true; it.fillColor = rgb(fill); } else it.filled = false;
  if (stroke) { it.stroked = true; it.strokeColor = rgb(stroke); it.strokeWidth = sw || 0.5; } else it.stroked = false;
  if (op != null) it.opacity = op; return it; }
function R(x, y, w, h, fill, stroke, sw, op) { return sty(doc.pathItems.rectangle(-y * K, x * K, w * K, h * K), fill, stroke, sw, op); }
function RR(x, y, w, h, r, fill) { return sty(doc.pathItems.roundedRectangle(-y * K, x * K, w * K, h * K, r * K, r * K), fill, null); }
function E(cx, cy, rx, ry, fill, stroke, sw, op) { return sty(doc.pathItems.ellipse(-(cy - ry) * K, (cx - rx) * K, 2 * rx * K, 2 * ry * K), fill, stroke, sw, op); }
function P(pts, closed, fill, stroke, sw, dash, op) {
  var p = doc.pathItems.add(); var a = [];
  for (var i = 0; i < pts.length; i++) a.push([pts[i][0] * K, -pts[i][1] * K]);
  p.setEntirePath(a); p.closed = closed; sty(p, fill, stroke, sw, op);
  if (dash) p.strokeDashes = dash; p.strokeCap = StrokeCap.ROUNDENDCAP; return p; }
function GR(x, y, w, h, top, bot) {
  var r = R(x, y, w, h, "#ffffff"); var g = doc.gradients.add(); g.type = GradientType.LINEAR;
  g.gradientStops[0].color = rgb(bot); g.gradientStops[1].color = rgb(top);
  var gc = new GradientColor(); gc.gradient = g; r.fillColor = gc; r.rotate(90, false, false, true, false); return r; }
function mk(s, size, font, col, track) {
  var t = doc.textFrames.add(); t.contents = (s && s.length) ? s : " "; var a = t.textRange.characterAttributes;
  try { a.size = size; a.textFont = app.textFonts.getByName(font); a.fillColor = rgb(col); if (track) a.tracking = track; }
  catch (e) { throw new Error("mk fail [" + s + "] size=" + size + " font=" + font + " col=" + col + " : " + e); }
  return t; }
function bnd(t) { var b = t.geometricBounds; return [b[0] / K, -b[1] / K, b[2] / K, -b[3] / K]; }
function place(t, x, y, al) {   // x: 왼/가운데/오른 기준, y: 글자 상자 세로 가운데(mm)
  var b = bnd(t); var w = b[2] - b[0], h = b[3] - b[1];
  var dx = (al == "c") ? x - (b[0] + w / 2) : (al == "r" ? x - b[2] : x - b[0]);
  var dy = y - (b[1] + h / 2); t.translate(dx * K, -dy * K); return t; }
function T(x, y, s, size, font, col, al, rot, track) { var t = mk(s, size, font, col, track); if (rot) t.rotate(rot); return place(t, x, y, al || "l"); }
function W(t) { var b = bnd(t); return b[2] - b[0]; }
function seq(cx, y, parts) {  // [[s, size, font, col], ...] 가운데 정렬 한 줄
  var ts = [], tot = 0; for (var i = 0; i < parts.length; i++) { var t = mk(parts[i][0], parts[i][1], parts[i][2], parts[i][3]); ts.push(t); tot += W(t); }
  var x = cx - tot / 2; for (var j = 0; j < ts.length; j++) { place(ts[j], x, y, "l"); x += W(ts[j]); } return tot; }
function IMG(path, x, y, w, h) { var p = doc.placedItems.add(); p.file = new File(path); p.width = w * K; p.height = h * K; p.position = [x * K, -y * K]; p.embed(); }
function labelIn(x0, x1, yt, yb, s, col, maxSize) {
  var w = x1 - x0, h = yb - yt;
  for (var sz = maxSize; sz >= 10; sz -= 1) {
    var t = mk(s, sz, "Pretendard-ExtraBold", col); var b = bnd(t); var tw = b[2] - b[0], th = b[3] - b[1];
    if (tw + 3 <= w && th + 2.4 <= h) { place(t, (x0 + x1) / 2, yt + th / 2 + 1.8, "c"); return "h"; }
    if (th + 1.4 <= w && tw + 3.2 <= h) { t.rotate(90); place(t, (x0 + x1) / 2, yb - tw / 2 - 2.2, "c"); return "v"; }
    t.remove();
  }
  return ""; }
function person(x, y, h, col, pose) {   // y = 발 위치(mm)
  var s = h / 5.6; var hy = y - h + 0.75 * s;
  E(x, hy, 0.62 * s, 0.62 * s, col, null);
  P([[x - 0.75 * s, y - h + 1.6 * s], [x + 0.75 * s, y - h + 1.6 * s], [x + 0.62 * s, y - 2.3 * s], [x - 0.62 * s, y - 2.3 * s]], true, col, null);
  var lw = 0.85 * s * K / 2.83;
  P([[x - 0.32 * s, y - 2.4 * s], [x - 0.5 * s - pose * 0.5 * s, y]], false, null, col, 1.2 * s);
  P([[x + 0.32 * s, y - 2.4 * s], [x + 0.5 * s + pose * 0.5 * s, y]], false, null, col, 1.2 * s);
  P([[x - 0.7 * s, y - h + 1.8 * s], [x - 1.1 * s - pose * 0.4 * s, y - 2.9 * s]], false, null, col, 0.9 * s);
  P([[x + 0.7 * s, y - h + 1.8 * s], [x + 1.1 * s + pose * 0.4 * s, y - 2.9 * s]], false, null, col, 0.9 * s); }
function tree(x, gy, r, col) { P([[x, gy], [x, gy - 2.6 - r]], false, null, "#8b7355", 0.6); E(x, gy - 2.6 - r * 1.6, r, r * 1.1, col, null); }
function dot(x, y) { E(x, y, 0.95, 0.95, "#E0393E", "#ffffff", 0.5); }
"""


def build(key):
    cfg = SHEETS[key]; C = CUTS[key]
    p0 = np.array(C["p0"]); u = np.array(C["u"]); L = C["L"]
    sB0, sB1 = C["inB"][0]
    MARG = 0.06 * (sB1 - sB0) + 10
    sA, sZ = sB0 - MARG, sB1 + MARG
    X0m, X1m = 22.0, 378.0
    hs = (X1m - X0m) / (sZ - sA); gy = 197.0
    ztop = max([r[3] for r in C["bld"]] + [z for s_, z in C["glass"]] + [0.0])
    if any(r[5] == "구 경주역사" for r in C["bld"]): ztop = max(ztop, 18.6)
    vs = min(5.2, (gy - 104.0 - 16.0) / ztop)
    X = lambda s: X0m + (s - sA) * hs
    Y = lambda z: gy - z * vs
    o = [PRE % dict(W=PW, H=PH)]
    add = o.append
    rnd = random.Random(7)
    # ── 머리글(가운데) ──
    add('layer("머리글");')
    add('var tt = T(%f, 7.2, %s, 15, "Pretendard-Bold", "%s", "c");' % (PW / 2, js(cfg["title"]), INK))
    add('var bb = bnd(tt); P([[bb[0] - 2, 11.6], [bb[2] + 2, 11.6]], false, null, "#333333", 0.6);')
    add("seq(%f, 15.8, %s);" % (PW / 2, js([[s, 10, "Pretendard-Medium", c or "#444444"] for s, c in cfg["sub"]])))
    # ── 사례 대신: 라이노 단면 투시 3칸 ──
    add('layer("투시 3칸");')
    pw, gap, px0, py = 120.67, 7.0, 12.0, 20.0
    for i, (ttl, cap) in enumerate(cfg["panels"]):
        x = px0 + i * (pw + gap)
        img = os.path.join(CL, "%s_%d_ps.jpg" % (key, i + 1)).replace("\\", "/")
        add('RR(%f, %f, %f, 8.2, 1.4, "%s"); R(%f, %f, %f, 3, "%s");' % (x, py, pw, SALMON, x, py + 5.2, pw, SALMON))
        add('T(%f, %f, %s, 11.5, "Pretendard-SemiBold", "#ffffff", "c");' % (x + pw / 2, py + 4.1, js(ttl)))
        add("IMG(%s, %f, %f, %f, 50);" % (js(img), x, py + 8.2, pw))
        add('R(%f, %f, %f, 8.2, "#FCECE9");' % (x, py + 58.2, pw))
        add('T(%f, %f, %s, 10.5, "Pretendard-Medium", "#333333", "c");' % (x + pw / 2, py + 62.3, js(cap)))
    # ── 강조 문구 ──
    add('layer("강조 문구");')
    add("seq(%f, 94.5, %s);" % (PW / 2, js([[s, sz, "Pretendard-Bold" if sz > 12 else "Pretendard-SemiBold", SALMON] for s, sz in cfg["head"]])))
    # ── 지반 띠 ──
    add('layer("지반");')
    add('GR(0, %f, %f, %f, "#9b9b98", "#ffffff");' % (gy, PW, PH - gy))
    add('P([[0, %f], [%f, %f]], false, null, "#1a1a1a", 1.1);' % (gy, PW, gy))
    add('T(%f, %f, %s, 14, "Pretendard-SemiBold", "#2b2b2b", "c", 0, 20);' % (PW / 2, gy + 11.5, js(cfg["ground_cap"])))
    # ── 주변 건물(구역 밖) ──
    add('layer("주변 건물");')
    ext = LineString([tuple(p0 - u * 300), tuple(p0 + u * (L + 300))])
    for ob in CF:
        if ob["inside"]: continue
        x_ = ext.intersection(ob["g"])
        for seg in ([x_] if x_.geom_type == "LineString" else list(getattr(x_, "geoms", []))):
            if seg.geom_type != "LineString" or seg.length < 0.5: continue
            ss = sorted(float(np.dot(np.array(c) - p0, u)) for c in seg.coords)
            a, b = max(ss[0], sA), min(ss[-1], sZ)
            if b - a < 0.5 or (a > sB0 - 1 and b < sB1 + 1): continue
            h = max(ob["h"], 3.5)
            add('R(%f, %f, %f, %f, "#ffffff", "#c9c9c6", 0.4);' % (X(a), Y(h), (b - a) * hs, h * vs))
    # ── 지면 요소 ──
    add('layer("지면");')
    GC = {"도로": "#5b5b5b", "공원": "#7FC35A", "보행": "#B5DD8C", "광장": "#E7D9BC", "중정": "#9ED07A"}
    trees = []
    for s0, s1, kind, nm in C["ground"]:
        if kind not in GC: continue
        a, b = max(s0, sA), min(s1, sZ)
        if b <= a: continue
        add('R(%f, %f, %f, 1.3, "%s");' % (X(a), gy - 1.3, (b - a) * hs, GC[kind]))
        if kind in ("공원", "중정") or (kind == "보행" and "조망" not in nm) or (kind == "광장" and "역전" in nm):
            step = max(9.0, 6.0 / hs)
            for s_ in np.arange(a + step / 2, b, step): trees.append(s_)
    bsp = [(r[0], r[1]) for r in C["bld"]]
    for s_ in trees:
        if any(a - 3 < s_ < b + 3 for a, b in bsp): continue
        add('tree(%f, %f, %f, "%s");' % (X(s_), gy - 1.3, rnd.uniform(1.9, 2.4), rnd.choice(["#6DBE4B", "#5FB043", "#7CC85A"])))
    # ── 건축물 블록 ──
    add('layer("건축물");')
    comm = set(cfg.get("comm_1f", []))
    names = {}
    for s0, s1, z0, z1, cat, nm, lot in C["bld"]:
        n_ = names.setdefault(nm, [1e9, -1e9, 0.0, cat, []]); n_[0] = min(n_[0], s0); n_[1] = max(n_[1], s1); n_[2] = max(n_[2], z1); n_[4].append((s0, s1, z0, z1, cat))
    for nm, (a, b, top, cat0, parts) in names.items():
        for s0, s1, z0, z1, cat in parts:
            if cat == "주거" and nm in comm:
                add('R(%f, %f, %f, %f, "%s");' % (X(s0), Y(min(z1, 3.0)), (s1 - s0) * hs, (min(z1, 3.0) - z0) * vs, CAT["판매"]))
                if z1 > 3.0: add('GR(%f, %f, %f, %f, "%s", "%s");' % (X(s0), Y(z1), (s1 - s0) * hs, (z1 - 3.0) * vs, HOUSE[0], HOUSE[1]))
            elif cat == "주거":
                add('GR(%f, %f, %f, %f, "%s", "%s");' % (X(s0), Y(z1), (s1 - s0) * hs, (z1 - z0) * vs, HOUSE[0], HOUSE[1]))
            else:
                c = CAT["판매"] if cat == "판매" else BCOL.get(nm, CAT.get(cat, "#888888"))
                add('R(%f, %f, %f, %f, "%s");' % (X(s0), Y(z1), (s1 - s0) * hs, (z1 - z0) * vs, c))
    # 구 역사 모임지붕
    if "구 경주역사" in names:
        stg = [b for b in BLD if b["name"] == "구 경주역사"][0]["g"].buffer(0.8, join_style=2)
        pts = []
        for s_ in np.arange(names["구 경주역사"][0] - 0.8, names["구 경주역사"][1] + 0.81, 0.4):
            q = Point(*(p0 + u * s_))
            if stg.contains(q): pts.append((X(s_), Y(9.0 + math.tan(math.radians(33)) * stg.boundary.distance(q))))
        if pts:
            poly = [(pts[0][0], Y(9.0))] + pts + [(pts[-1][0], Y(9.0))]
            add("P(%s, true, \"#6E4A3A\", null);" % js(poly))
            names["구 경주역사"][2] = max(names["구 경주역사"][2], (gy - min(p[1] for p in pts)) / vs)
    # 유리 지붕
    if C["glass"]:
        gs = np.array(C["glass"])
        arc = [(X(s), Y(z)) for s, z in gs[::3]]
        add("P(%s, true, \"#CDEBF7\", null, 0, null, 55);" % js([(X(gs[0, 0]), Y(0))] + arc + [(X(gs[-1, 0]), Y(0))]))
        add("P(%s, false, null, \"#4A9CC4\", 1.6);" % js(arc))
        for s_ in np.arange(gs[0, 0], gs[-1, 0], 3.0):
            z_ = float(np.interp(s_, gs[:, 0], gs[:, 1])); add('P([[%f, %f], [%f, %f]], false, null, "#4A9CC4", 0.5);' % (X(s_), Y(z_), X(s_), Y(z_) + 2.0))
    # 브리지·캐노피
    for s0, s1, z0, z1, kind in C["links"]:
        add('R(%f, %f, %f, %f, "#5F656D");' % (X(s0), Y(z1), (s1 - s0) * hs, (z1 - z0) * vs))
    # ── 붉은 점선 동선 ──
    add('layer("동선");')
    yr = gy - 1.9
    add('P([[%f, %f], [%f, %f]], false, null, "%s", 0.9, [2.8, 2.0]);' % (X(sB0), yr, X(sB1), yr, RED))
    for s0, s1, z0, z1, kind in C["links"]:
        zm = (z0 + z1) / 2
        add('P([[%f, %f], [%f, %f]], false, null, "%s", 0.9, [2.8, 2.0]); dot(%f, %f); dot(%f, %f);' % (X(s0) - 3, Y(zm), X(s1) + 3, Y(zm), RED, X(s0) - 3, Y(zm), X(s1) + 3, Y(zm)))
    # ── 블록 라벨(블록 안 흰 글씨, 안 들어가면 위에 괄호) ──
    add('layer("라벨");')
    groups = {}
    above = []
    for lab, nms in cfg["bld"]:
        ss = [names[n] for n in nms if n in names]
        if not ss: print("  ! 단면에 없음", lab); continue
        a = min(v[0] for v in ss); b = max(v[1] for v in ss); top = max(v[2] for v in ss)
        def chain(parts, sa, sb):
            cur = 0.0; xa, xb = sa, sb
            for q in sorted([q for q in parts if q[0] < sb - 0.5 and q[1] > sa + 0.5], key=lambda q: q[2]):
                if q[2] <= cur + 0.6:
                    cur = max(cur, q[3]); xa, xb = max(xa, q[0]), min(xb, q[1])   # 위로 갈수록 좁아지는 부분까지 들어가는 폭
            return cur, xa, xb
        spans0 = sorted([(q[0], q[1]) for v in ss for q in v[4] if q[2] < 0.5], key=lambda t: -(t[1] - t[0]))
        sa0, sb0 = spans0[0] if spans0 else (a, b)
        low, la_, lb_ = chain([q for v in ss for q in v[4]], sa0, sb0)
        low = low or top
        groups[lab] = (a, b, top)
        # 블록 안: 1층부터 이어진 가장 낮은 지붕 아래 영역
        multi = len(nms) > 1
        wmm = (lb_ - la_) * hs
        cx = X(la_) + (min(2.6, wmm * 0.22) if wmm > 7 else wmm / 2)          # 수직 동선은 블록 왼쪽 가장자리 가까이(라벨과 겹치지 않게)
        # 수직 동선 + 점
        add('P([[%f, %f], [%f, %f]], false, null, "%s", 0.9, [2.8, 2.0]); dot(%f, %f); dot(%f, %f);' % (cx, yr, cx, Y(low) + 3.2, RED, cx, yr, cx, Y(low) + 3.2))
        if multi:
            above.append((lab, a, b, top))
        else:
            # 가장 넓은 1층 구간 기준
            sa, sb = la_, lb_
            pad = 4.2 / hs if (lb_ - la_) * hs > 12 else 0.0                    # 왼쪽 수직 동선 자리 비움
            sa = sa + pad
            col = "#ffffff"
            add('var r_ = labelIn(%f, %f, %f, %f, %s, "%s", 16); if (r_ == "") { ABOVE.push([%s, %f, %f, %f]); }'
                % (X(sa), X(sb), Y(low), gy - 2.6, js(lab), col, js(lab), X(a), X(b), Y(top)))
    add("var ABOVE = [];") if False else None
    # ABOVE 배열은 위에서 쓰기 전에 선언되어야 함 → 맨 앞에 선언
    o.insert(1, "var ABOVE = [];")
    for lab, a, b, top in above:
        add("ABOVE.push([%s, %f, %f, %f]);" % (js(lab), X(a), X(b), Y(top)))
    add(r"""
for (var i = 0; i < ABOVE.length; i++) {
  var q = ABOVE[i]; var cx = (q[1] + q[2]) / 2; var yt = q[3];
  P([[q[1] + 0.4, yt - 1.4], [q[1] + 0.4, yt - 2.6], [q[2] - 0.4, yt - 2.6], [q[2] - 0.4, yt - 1.4]], false, null, "#333333", 0.6);
  T(cx, yt - 5.6, q[0], 12, "Pretendard-ExtraBold", "#222222", "c");
}""")
    for lab, txt in cfg["note"].items():
        if lab in groups:
            a, b, top = groups[lab]
            yy = Y(top) - (10.5 if any(l == lab for l, *_ in above) else 4.0)
            add('T(%f, %f, %s, 10, "Pretendard-Medium", "#555555", "c");' % ((X(a) + X(b)) / 2, yy, js(txt)))
    if cfg.get("group"):
        gl, mem = cfg["group"]
        ss = [groups[m] for m in mem if m in groups]
        if ss:
            a = min(v[0] for v in ss); b = max(v[1] for v in ss); top = max(v[2] for v in ss)
            yt = Y(top) - 13.0
            add('P([[%f, %f], [%f, %f], [%f, %f], [%f, %f]], false, null, "#222222", 0.7);' % (X(a), yt + 2.6, X(a), yt + 1.2, X(b), yt + 1.2, X(b), yt + 2.6))
            add('T(%f, %f, %s, 13, "Pretendard-ExtraBold", "#222222", "c");' % ((X(a) + X(b)) / 2, yt - 2.6, js(gl)))
    # 지면 라벨(회색 굵은 글씨, 'UAM' 형식) — 건물과 겹치면 지반 띠 안으로
    from PIL import ImageFont
    FX = ImageFont.truetype(os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts", "Pretendard-ExtraBold.otf"), 100)   # 사용자 설치 글꼴
    def tw(t, pt, track=0): return FX.getlength(t) / 100.0 * pt * 25.4 / 72.0 * (1 + track / 1000.0)
    spans_mm = sorted([(X(r[0]), X(r[1]), Y(r[3])) for r in C["bld"]] + [(X(l[0]), X(l[1]), Y(l[3])) for l in C["links"]])
    for lab, gname in cfg["gl"]:
        segs = [(a, b) for a, b, kind, nm in C["ground"] if nm == gname and b > sA and a < sZ]
        if not segs: print("  ! 지면 없음", lab); continue
        a, b = max(segs, key=lambda t: t[1] - t[0]); m_ = X((max(a, sA) + min(b, sZ)) / 2)
        w_ = tw(lab, 12, 30); yl = gy - 15.5
        hit = any(x0 < m_ + w_ / 2 + 1 and x1 > m_ - w_ / 2 - 1 and yt < yl + 3 for x0, x1, yt in spans_mm)
        if not hit:
            add('T(%f, %f, %s, 12, "Pretendard-ExtraBold", "#9a9a9a", "c", 0, 30);' % (m_, yl, js(lab)))
        else:
            add('P([[%f, %f], [%f, %f]], false, null, "#555555", 0.6); T(%f, %f, %s, 10.5, "Pretendard-Bold", "#3a3a3a", "c");' % (m_, gy + 0.6, m_, gy + 2.2, m_, gy + 4.6, js(lab)))
    # 사람
    add('layer("사람");')
    PC = ["#4a4a4a", "#5a5a5a", "#E8776A", "#2D6CB0", "#4a4a4a"]
    for s0, s1, kind, nm in C["ground"]:
        if kind in ("보행", "광장", "중정", "공원") and (s1 - s0) * hs > 7:
            m_ = (max(s0, sA) + min(s1, sZ)) / 2
            n = 1 if (s1 - s0) * hs < 14 else 2
            for j in range(n):
                add('person(%f, %f, %f, "%s", %f);' % (X(m_) + (j - (n - 1) / 2) * 3.6, gy - 1.3, rnd.uniform(5.2, 6.0), rnd.choice(PC), rnd.uniform(-0.4, 0.6)))
    # ── 양끝: N/S 루프 화살표 · 단면 기호 ──
    add('layer("방위");')
    e0, e1 = cfg["ends"]
    add('T(10, %f, %s, 20, "Pretendard-Light", "#8a8a8a", "c");' % (gy - 4.0, js(e0)))
    add('T(%f, %f, %s, 20, "Pretendard-Light", "#8a8a8a", "c");' % (PW - 10, gy - 4.0, js(e1)))
    xl0, xl1 = 17.0, X(sB0) - 3; xr0, xr1 = X(sB1) + 3, PW - 17.0
    def loop(x_far, x_turn, x_head, sgn):
        pts = [(x_far, gy - 3.0), (x_turn, gy - 3.0)]
        for t in np.linspace(math.pi / 2, -math.pi / 2, 9):
            pts.append((x_turn + sgn * 2.4 * math.cos(t), gy - 5.4 - 2.4 * math.sin(t) * -1))
        pts.append((x_head, gy - 7.8))
        add('P(%s, false, null, "%s", 1.5);' % (js(pts), TEAL))
        d = -sgn
        add('P([[%f, %f], [%f, %f], [%f, %f]], true, "%s", null);' % (x_head + d * 2.6, gy - 7.8, x_head, gy - 9.2, x_head, gy - 6.4, TEAL))
    if xl1 - xl0 > 24: loop(xl0, xl1, xl0 + (xl1 - xl0) * 0.45, 1)
    if xr1 - xr0 > 24: loop(xr1, xr0, xr1 - (xr1 - xr0) * 0.45, -1)
    t = SHEETS[key]["tag"]
    for side, s_ in ((0, sB0), (1, sB1)):
        xe = X(s_)
        add('P([[%f, %f], [%f, %f]], false, null, "#A0237A", 0.6, [2.0, 1.6]);' % (xe, Y(20) + 3.6, xe, gy + 4))
        add('E(%f, %f, 3.3, 3.3, "#A0237A", "#ffffff", 0.6); T(%f, %f, %s, 11, "Pretendard-Bold", "#ffffff", "c");' % (xe, Y(20), xe, Y(20) + 0.1, js(t + ("" if side == 0 else "′"))))
    # ── 범례(맨 아래) ──
    add('layer("범례");')
    used = []
    for nm, (a, b, top, cat0, parts) in names.items():
        for p in parts:
            k_ = ("주거" if p[4] == "주거" else ("판매" if p[4] == "판매" or (nm in comm and p[2] < 0.5) else (nm if nm in BCOL else p[4])))
            if k_ not in used: used.append(k_)
    LBL = {"주거": "주거", "판매": "근린생활·커뮤니티", "생활SOC": "생활체육", "창작": "창작·공방", "역사": "근대역사관(구 경주역사)", "실내 체험관": "체험·교류",
           "근대역사관": "전시", "복합문화센터": "생활문화", "지역문화원 본동": "지역문화", "문화": "문화"}
    items = [(HOUSE if k_ == "주거" else (BCOL.get(k_) or CAT.get(k_, "#888")), LBL.get(k_, k_)) for k_ in used]
    if C["links"]: items.append(("#5F656D", "브리지·캐노피"))
    if C["glass"]: items.append(("#CDEBF7", "유리 지붕"))
    add("var lx = 12;")
    for c, lab in items:
        if isinstance(c, tuple): add('GR(lx, 217.6, 4.2, 3.4, "%s", "%s");' % c)
        else: add('R(lx, 217.6, 4.2, 3.4, "%s");' % c)
        add('var tl = T(lx + 5.4, 219.3, %s, 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;' % js(lab))
    add('P([[lx, 219.3], [lx + 7, 219.3]], false, null, "%s", 0.9, [2.8, 2.0]); dot(lx + 7, 219.3); var tl = T(lx + 9.5, 219.3, "\\ubcf4\\ud589 \\ub3d9\\uc120 \\u00b7 \\uc218\\uc9c1 \\ub3d9\\uc120", 10, "Pretendard-Medium", "#333333", "l");' % RED)
    add('T(%f, 219.3, %s, 10, "Pretendard-Regular", "#777777", "r");' % (PW - 12, js("수직 %.1f배 과장 · 위 3칸은 라이노 단면 투시(최종 모델)" % (vs / hs))))
    # ── 저장·내보내기 ──
    ai = os.path.join(OUTD, cfg["file"] + ".ai").replace("\\", "/")
    pdf = os.path.join(OUTD, cfg["file"] + ".pdf").replace("\\", "/")
    png = os.path.join(OUTD, cfg["file"] + ".png").replace("\\", "/")
    add(r"""
var o = new ExportOptionsPNG24(); o.artBoardClipping = true; o.horizontalScale = 333.333; o.verticalScale = 333.333; o.antiAliasing = true; o.transparency = false;
doc.exportFile(new File(%s), ExportType.PNG24, o);
doc.saveAs(new File(%s), new IllustratorSaveOptions());
var po = new PDFSaveOptions(); po.preserveEditability = false; po.compatibility = PDFCompatibility.ACROBAT7;
doc.saveAs(new File(%s), po);
doc.close(SaveOptions.DONOTSAVECHANGES);
"saved " + %s;""" % (js(png), js(ai), js(pdf), js(cfg["file"])))
    return "\n".join(x for x in o if x)


def run(key):
    src = build(key)
    jsx = os.path.join(CL, "s2_%s.jsx" % key)
    open(jsx, "w", encoding="utf-8-sig").write(src)
    ps = "$app = New-Object -ComObject 'Illustrator.Application'; $app.UserInteractionLevel = -1; $app.DoJavaScriptFile('%s')" % jsx.replace("'", "''")
    r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1200)
    print(key, r.stdout.strip()[-300:], r.stderr.strip()[:1500])


if __name__ == "__main__":
    for k in (sys.argv[1:] or ["V", "H", "Dg"]): run(k)
