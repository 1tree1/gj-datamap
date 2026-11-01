# -*- coding: utf-8 -*-
"""B 입력 자산·좌표 정합 검산 + site_inputs.geojson(R 프레임 = 대지 3dm 실축척 프레임, m)
원본 3dm·pkl·json은 읽기만 한다. 출력은 work/20261026_site_automation_plan/research/ 와 scratchpad 로그뿐."""
import os, json, pickle, math, collections
import numpy as np
import rhino3dm as r3
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, MultiPoint, box, mapping
from shapely.ops import unary_union, linemerge, nearest_points
from shapely import affinity
import pyproj
import shapely.ops

ROOT = r"C:\Users\OFFICE\Desktop\9_도시"
D = os.path.join(ROOT, r"work\20261011_masterplan_rough\data")
OUTD = os.path.join(ROOT, r"work\20261026_site_automation_plan\research")
LOG = open("r5_log.txt", "w", encoding="utf-8")
def log(*a):
    s = " ".join(str(x) for x in a); LOG.write(s + "\n"); LOG.flush()

X0, Y0 = 1166600.0, 1761100.0           # L → R
XS_PLAN = 517.0557                       # P(v3 계획 프레임) → R
XS_RSEL = 1080.4963                      # road_sel(지구단위계획 2026-8 객체 위치) → R
C_O = (1143532.6157, 1763242.48)         # O(콘타) → R : R = 2·O − C_O
SH5179 = (11616.38, -796.58)             # R → EPSG:5179 : X = R − SH5179
def L2R(g): return affinity.translate(g, X0, Y0)
def R2L(g): return affinity.translate(g, -X0, -Y0)
def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []

# ── 1. 대지 3dm 경계 ───────────────────────────────
m = r3.File3dm.Read(os.path.join(ROOT, "구경주역_최종대지_대지경계선.3dm"))
lname = {m.Layers[i].Index: m.Layers[i].FullPath for i in range(len(m.Layers))}
bo = [o for o in m.Objects if isinstance(o.Geometry, r3.PolylineCurve)][0]
g = bo.Geometry
BP = [(g.Point(i).X, g.Point(i).Y) for i in range(g.PointCount)]
BR = Polygon(BP)
log("[1] 3dm 경계: 이름=%s 점=%d 닫힘=%s valid=%s 면적=%.3f 둘레=%.3f bbox=%s" % (bo.Attributes.Name, len(BP), g.IsClosed, BR.is_valid, BR.area, BR.length, tuple(round(v, 3) for v in BR.bounds)))
segl = [math.dist(BP[i], BP[i + 1]) for i in range(len(BP) - 1)]
log("    변 길이 최소 %.3f 최대 %.3f, 1 m 미만 변 %d개" % (min(segl), max(segl), sum(1 for s in segl if s < 1.0)))
log("    단위 %s, 허용오차 %s" % (m.Settings.ModelUnitSystem, m.Settings.ModelAbsoluteTolerance))

# ── 2. model.pkl / design.pkl / final.pkl / faces.pkl 경계 비교 ───
M = pickle.load(open(os.path.join(D, "model.pkl"), "rb")); S = M["S"]
FN = pickle.load(open(os.path.join(D, "final.pkl"), "rb"))
DG = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
FC = pickle.load(open(os.path.join(D, "faces.pkl"), "rb"))
for nm, Bl in [("model.S.B", S["B"]), ("design.B", DG["B"]), ("final.B", FN["B"]), ("faces.B", FC["B"])]:
    Bt = L2R(Bl)
    sd = BR.symmetric_difference(Bt).area; iou = BR.intersection(Bt).area / BR.union(Bt).area
    log("[2] %s(L→R) 면적 %.3f 점 %d | 3dm 대비 대칭차 %.3f㎡ IoU %.6f Hausdorff %.3f m" % (nm, Bt.area, len(Bl.exterior.coords), sd, iou, BR.hausdorff_distance(Bt)))
fsum = sum(f.area for f in FC["faces"]); log("    faces 18면 합 %.3f (경계 L %.3f)" % (fsum, FC["B"].area))

# ── 3. road_sel.json → R, model ROADS 와 비교 ─────
RS = json.load(open(os.path.join(D, "road_sel.json"), encoding="utf-8"))
rsg = []
for o in RS["objs"]:
    if "loops" in o:
        outer = [l[1] for l in o["loops"] if l[0] == "Outer"][0]; inner = [l[1] for l in o["loops"] if l[0] == "Inner"]
        p = Polygon([(x, y) for x, y, *_ in outer], [[(x, y) for x, y, *_ in h] for h in inner]).buffer(0)
    else:
        p = Polygon([(x, y) for x, y, *_ in o["pts"]]).buffer(0)
    rsg.append((o["layer"], o["type"], affinity.translate(p, -XS_RSEL, 0)))
RO = {k: L2R(v) for k, v in S["ROADS"].items()}
rs_road = unary_union([p for ly, t, p in rsg if ly.endswith("도로")])
mo_road = unary_union(list(RO.values()))
log("[3] road_sel 도로 Brep 2개(−1080.4963) 합 %.3f㎡ vs model ROADS(N+EW+O) 합 %.3f㎡ · 대칭차 %.3f㎡ · Hausdorff %.3f m" % (rs_road.area, mo_road.area, rs_road.symmetric_difference(mo_road).area, rs_road.hausdorff_distance(mo_road)))
rs_walk = unary_union([p for ly, t, p in rsg if ly.endswith("보도") and t == "Brep"])
log("    road_sel 보도 Brep 합 %.3f㎡ (경계 밖 %.3f㎡) · 도로 경계 밖 %.3f㎡" % (rs_walk.area, rs_walk.difference(BR).area, rs_road.difference(BR).area))
for k, v in RO.items(): log("    ROADS[%s] 면적 %.3f 경계 밖 %.4f㎡ 조각 %d" % (k, v.area, v.difference(BR.buffer(0.01)).area, len(polys(v))))

# ── 4. 콘타 O 프레임 ↔ R ───────────────────────────
Omin = (1155117.39, 1762198.11)           # 이전 조사(01 §3) 콘타 모델 '최종 대지경계선' bbox 최소점
Rm = (2 * Omin[0] - C_O[0], 2 * Omin[1] - C_O[1])
log("[4] O bbox 최소점 %s → R %s · 3dm R bbox 최소 %s · 차 (%.3f, %.3f) m" % (Omin, tuple(round(v, 3) for v in Rm), tuple(round(v, 3) for v in BR.bounds[:2]), Rm[0] - BR.bounds[0], Rm[1] - BR.bounds[1]))
CF = pickle.load(open(os.path.join(D, "ctx_fixed.pkl"), "rb")); xf = CF["xf"]
cen = np.array(xf["cen"], float); t = np.array(xf["t"], float); s = float(xf["scale"])
CctxR = 2 * cen - t - np.array([X0, Y0])
log("    ctx_fixed xf: θ=%.2e s=%.6f t=%s cen=%s → R = 2·O − (%.3f, %.3f) | 계획 사슬 C_O = (%.3f, %.3f) | 차 (%.3f, %.3f) m" % (xf["theta"], s, tuple(round(v, 3) for v in t), tuple(round(v, 3) for v in cen), CctxR[0], CctxR[1], C_O[0], C_O[1], CctxR[0] - C_O[0], CctxR[1] - C_O[1]))

# ── 5. R → 5179 → 5187 / 4326, 면적 ─────────────────
t5187 = pyproj.Transformer.from_crs(5179, 5187, always_xy=True)
t4326 = pyproj.Transformer.from_crs(5179, 4326, always_xy=True)
def R2X(g): return affinity.translate(g, -SH5179[0], -SH5179[1])
BX = R2X(BR)
B87 = shapely.transform(BX, lambda a: np.column_stack(t5187.transform(a[:, 0], a[:, 1])))
B43 = shapely.transform(BX, lambda a: np.column_stack(t4326.transform(a[:, 0], a[:, 1])))
geod = pyproj.Geod(ellps="GRS80"); ga, gp = geod.geometry_area_perimeter(B43)
c43 = B43.centroid
log("[5] 면적: R(=5179 격자) %.2f · 5187 격자 %.2f(%+.2f) · 타원체(GRS80) %.2f(%+.2f) ㎡ · 중심 4326 (%.6f, %.6f)" % (BR.area, B87.area, B87.area - BR.area, abs(ga), abs(ga) - BR.area, c43.x, c43.y))
log("    5179 bbox %s · 5187 bbox %s" % (tuple(round(v, 2) for v in BX.bounds), tuple(round(v, 2) for v in B87.bounds)))
P3 = np.array([[BR.bounds[0], BR.bounds[1]], [BR.bounds[2], BR.bounds[1]], [BR.bounds[0], BR.bounds[3]]])
Q3 = np.column_stack(t5187.transform(P3[:, 0] - SH5179[0], P3[:, 1] - SH5179[1]))
sx = math.dist(Q3[0], Q3[1]) / math.dist(P3[0], P3[1]); sy = math.dist(Q3[0], Q3[2]) / math.dist(P3[0], P3[2])
rot = math.degrees(math.atan2(Q3[1][1] - Q3[0][1], Q3[1][0] - Q3[0][0]))
log("    R→5187 국소 축척 x %.7f y %.7f · 회전 %.4f°" % (sx, sy, rot))

# ── 6. 축(L 정의 → R) ─────────────────────────────
DS = pickle.load(open(os.path.join(D, "district.pkl"), "rb")); TOUR = DS["TOUR"]
OP = {o["key"]: o for o in S["OPEN"]}
JR = [h[0] for h in DS["HER"] if "전랑지" in h[1] and "국가지정" in h[2]][0]; JRc = np.array(JR.centroid.coords[0])
PAG = [h[0] for h in DS["HER"] if h[1] == "황오동삼층석탑" and h[2] == "문화재"][0].centroid
v3 = np.array([0.5394, 0.842]); n3 = np.array([-0.842, 0.5394]); F0 = np.array([131.2, 59.5]) + n3 * 10.0
ym2 = sum(S["DBAND"]) / 2; YP8 = (635.2 + 643.2) / 2; XNS = (255.9 + 285.9) / 2; YEW = (333.70 + 353.66) / 2
BIG = 3000.0
AX = []
def axis(key, name, line_L, band_L, width, drawn, anchors, src):
    seg = L2R(line_L).intersection(BR)
    parts = [q for q in (seg.geoms if hasattr(seg, "geoms") else [seg]) if q.length > 0.5]
    AX.append(dict(key=key, name=name, line=line_L, band=band_L, width=width, drawn=drawn, anchors=anchors, src=src, seg=parts))
axis("A1", "① 남북축(대지축) — 대릉원 ↔ 북천·황성공원", LineString([(XNS, -BIG), (XNS, BIG)]), OP["E"]["g"], 30.0,
     [(271.0, -230.0), (271.0, 1290.0)], {"북: 황성공원": TOUR["황성공원"], "남: 대릉원 돌담길": TOUR["대릉원 돌담길"]}, "g0_axes.py arrow_line((271,-230),(271,1290)) · E 띠 x 255.9–285.9")
axis("A2", "② 동서축 — 성동시장 ↔ 성동리 전랑지(폭 40 m 선형공원)", LineString([(-BIG, ym2), (BIG, ym2)]), OP["D"]["g"], 40.0,
     [(TOUR["성동시장"][0] - 10, ym2), (JRc[0] - 70, ym2)], {"서: 성동시장": TOUR["성동시장"], "동: 성동리 전랑지(국가지정 구역 중심)": tuple(JRc)}, "g0_axes.py DBAND 476.3–516.3")
axis("A3", "③ 역사유적축 — 사선 보행축(폭 20 m), 연장선 미추왕릉", LineString([tuple(F0 - BIG * v3), tuple(F0 + BIG * v3)]), OP["F"]["g"], 20.0,
     [tuple(F0 - 690 * v3), tuple(F0 + 1450 * v3)], {"남서: 대릉원 미추왕릉": TOUR["대릉원 미추왕릉"], "남서: 황리단길": TOUR["황리단길"]}, "g0_axes.py F0=(131.2,59.5)+10·n, v=(0.5394,0.842)")
axis("A4", "④ 향일문 조망 보행로(폭 8 m) — 경주읍성 향일문", LineString([(-BIG, YP8), (BIG, YP8)]), S["PATH8"], 8.0,
     [(560.0, YP8), (TOUR["경주읍성"][0] + 16, TOUR["경주읍성"][1])], {"서: 경주읍성(향일문)": TOUR["경주읍성"]}, "g0_axes.py YP8=639.2 · PATH8 y 635.2–643.2")
axis("A5", "화랑로 연결(차량 동서 도로 20 m) — A안: 원화로 교차부에서 차량 정지, 동쪽은 보행 통경축", LineString([(-BIG, YEW), (BIG, YEW)]), S["ROADS"]["EW"], 20.0,
     [(103.0, 343.7), (412.0, 343.7)], {}, "g0_axes.py ax.plot([103,412],[343.7,343.7]) · ROADS.EW y 333.70–353.66 · k0 HWARANG_Y=342.3")
for a in AX:
    segs = a["seg"]; tot = sum(q.length for q in segs)
    ends = [(tuple(round(c, 2) for c in q.coords[0]), tuple(round(c, 2) for c in q.coords[-1])) for q in segs]
    endsL = [(tuple(round(c - o, 1) for c, o in zip(q.coords[0], (X0, Y0))), tuple(round(c - o, 1) for c, o in zip(q.coords[-1], (X0, Y0)))) for q in segs]
    dr = [L2R(Point(p)) for p in a["drawn"]]
    din = ["안" if BR.contains(p) else "밖(경계에서 %.1f m)" % BR.exterior.distance(p) for p in dr]
    band_R = L2R(a["band"]); bands = polys(band_R)
    touch = band_R.buffer(0.5).intersection(BR.exterior).length
    log("[6] %s | 경계 안 구간 %d개 총 %.1f m, 끝점 L=%s | 그림 끝점 L%s → %s | 띠 %d조각 %.1f㎡, 경계선 접촉 %.1f m" % (a["name"], len(segs), tot, endsL, [tuple(round(c, 1) for c in p) for p in a["drawn"]], din, len(bands), band_R.area, touch))
    bb = [tuple(round(v - o, 1) for v, o in zip(q.bounds, (X0, Y0, X0, Y0))) for q in bands]
    log("     띠 조각 bounds(L) %s" % bb)
    for k, p in a["anchors"].items():
        pp = L2R(Point(p)); dperp = L2R(a["line"]).distance(pp); dbd = BR.exterior.distance(pp)
        log("     앵커 %s L%s: 축 직선과의 수직거리 %.1f m · 대지경계까지 %.1f m" % (k, tuple(round(c, 1) for c in p), dperp, dbd))
xi = L2R(AX[0]["line"]).intersection(L2R(AX[2]["line"])); log("    ①·③ 교점 L(%.2f, %.2f)" % (xi.x - X0, xi.y - Y0))
def band_width(gL, axis_dir):
    n = np.array([-axis_dir[1], axis_dir[0]]); pr = [float(np.dot(np.array(c), n)) for p in polys(gL) for c in p.exterior.coords]
    return max(pr) - min(pr)
log("    띠 폭 실측(축 직교 투영 범위): E %.2f · D %.2f · F %.2f · PATH8 %.2f · EW도로 %.2f m" % (band_width(OP["E"]["g"], (0, 1)), band_width(OP["D"]["g"], (1, 0)), band_width(OP["F"]["g"], v3), band_width(S["PATH8"], (1, 0)), band_width(S["ROADS"]["EW"], (1, 0))))

# ── 7. 도로 중심선(보로노이 골격) · 폭 ─────────────────
def merge(gs):
    u = unary_union(gs)
    if u.geom_type == "LineString": return [u]
    ml = linemerge(u)
    return list(ml.geoms) if hasattr(ml, "geoms") else [ml]
def skeleton(poly, step=1.0, prune=15.0):
    pts = []
    for ring in [poly.exterior] + list(poly.interiors):
        L = ring.length; k = max(int(L / step), 8)
        pts += [ring.interpolate(i * L / k).coords[0] for i in range(k)]
    ed = shapely.voronoi_polygons(MultiPoint(pts), only_edges=True)
    inner = poly.buffer(-0.05)
    keep = [e for e in ed.geoms if inner.contains(e)]
    lines = merge(keep)
    for _ in range(40):
        ends = {}
        for i, l in enumerate(lines):
            for c in (l.coords[0], l.coords[-1]): ends.setdefault((round(c[0], 3), round(c[1], 3)), []).append(i)
        rm = set()
        for i, l in enumerate(lines):
            a, b = (round(l.coords[0][0], 3), round(l.coords[0][1], 3)), (round(l.coords[-1][0], 3), round(l.coords[-1][1], 3))
            if l.length < prune and (len(ends[a]) == 1 or len(ends[b]) == 1) and len(lines) > 1: rm.add(i)
        if not rm: break
        lines = [l for i, l in enumerate(lines) if i not in rm]
        lines = merge(lines)
    cl = unary_union(lines).simplify(0.3)
    samp = []
    for l in (cl.geoms if hasattr(cl, "geoms") else [cl]):
        for d in np.arange(0, l.length, 2.0): samp.append(2 * poly.exterior.distance(l.interpolate(d)))
    w = np.array(samp)
    return cl, dict(p10=float(np.percentile(w, 10)), p50=float(np.median(w)), p90=float(np.percentile(w, 90)), n=len(w), length=float(cl.length))
RD = {}
for k, nm, wdes in [("N", "북측 차도", "13(폴리곤 12.8)"), ("EW", "동서 도로(화랑로 연결 횡단)", "20"), ("O", "동·남측 외곽도로", "10~12")]:
    pR = RO[k]
    pp = max(polys(pR), key=lambda q: q.area)
    cl, w = skeleton(pp)
    RD[k] = dict(name=nm, poly=pR, cl=cl, w=w, wdes=wdes)
    log("[7] %s(%s): 폴리곤 %d조각 %.1f㎡ · 중심선 %s %.1f m · 폭 p10/p50/p90 = %.1f/%.1f/%.1f m (설계 표기 %s m) · 면적/중심선 = %.1f m" % (k, nm, len(polys(pR)), pR.area, cl.geom_type, w["length"], w["p10"], w["p50"], w["p90"], wdes, pR.area / max(w["length"], 1)))

# ── 8. 획지 13 · 진입 7 · 구 역사 · 석탑 ─────────────
LOT = {l["no"]: l for l in S["LOTS"]}; MLOT = {l["no"]: l for l in M["LOTS"]}
lot_sum = sum(l["g"].area for l in S["LOTS"])
log("[8] 획지 13개 합 %.1f㎡ · model.TOT %s" % (lot_sum, {k: round(v, 3) for k, v in M["TOT"].items()}))
for no in sorted(LOT):
    l = LOT[no]; ml = MLOT[no]
    log("    획지 %2d %s %s %s %.1f㎡ ba %.0f gfa %.0f bcr %.2f far %.2f 최고 %d층 %.1f m 동 %d" % (no, l["code"], l["use"], l["name"], l["g"].area, ml["ba"], ml["gfa"], ml["bcr"], ml["far"], ml["maxf"], ml["maxh"], ml["n_bld"]))
def entry_on(no, p, d):
    p = np.array(p, float); d = np.array(d, float); d /= np.linalg.norm(d)
    ray = LineString([tuple(p - d * 40), tuple(p + d * 60)]); hit = ray.intersection(LOT[no]["g"].boundary)
    pts_ = [np.array(q.coords[0]) for q in (getattr(hit, "geoms", [hit]))] if not hit.is_empty else [np.array(nearest_points(LOT[no]["g"].boundary, Point(*p))[0].coords[0])]
    return min(pts_, key=lambda v: np.dot(v - (p - d * 40), d))
vd = np.array([353.5 - 254.0, 892.2 - 778.5]); vd /= np.linalg.norm(vd)
ENT = [(209.5, 150.0, (-vd[1], vd[0]), 2, "북측 차도(사선 구간)", "N"), (300.0, 188.6, (-1, 0), 4, "동측 외곽도로", "O"),
       (95.7, 278.5, (1, 0), 5, "서측 원화로", None), (300.0, 283.6, (-1, 0), 6, "동측 외곽도로", "O"),
       (293.5, 420.4, (-1, 0), 8, "동측 외곽도로", "O"), (170.5, 465.3, (0, 1), 7, "동서 도로", "EW"), (276.4, 476.1, (0, -1), 13, "동서 도로", "EW")]
ENTRIES = []
for i, (px, py, d, no, road, rk) in enumerate(ENT):
    p = np.array([-38.5 + 1.467 * px, 1035.4 - 1.467 * py]); d = np.array(d, float); d /= np.linalg.norm(d)
    q = entry_on(no, p, d); e = q - d * 5.0
    eR = L2R(Point(e)); dr = RO[rk].distance(eR) if rk else None
    ENTRIES.append(dict(i=i + 1, pL=e, d=d, no=no, road=road, rk=rk, status="중간마감 D3 사용자 지정"))
    log("    진입 %d: 픽셀(%.1f,%.1f)→L(%.1f, %.1f) 방향(%.2f, %.2f) → 획지 %d %s | %s 까지 %s m · 경계 안=%s (경계까지 %.1f m)" % (i + 1, px, py, e[0], e[1], d[0], d[1], no, LOT[no]["name"], road, ("%.2f" % dr) if dr is not None else "—(구역 밖 원화로)", BR.contains(eR), BR.exterior.distance(eR)))
q6 = entry_on(7, (100, 418), (1, 0)) - np.array([5.0, 0]); q7 = entry_on(13, (405, 292), (-1, 0)) + np.array([5.0, 0])
ENTRIES.append(dict(i=6, pL=q6, d=np.array([1.0, 0]), no=7, road="서측 원화로", rk=None, status="A안 재배치 제안(2026-10-15, 확정 여부 확인 대기)"))
ENTRIES.append(dict(i=7, pL=q7, d=np.array([-1.0, 0]), no=13, road="동측 외곽도로", rk="O", status="A안 재배치 제안(2026-10-15, 확정 여부 확인 대기)"))
log("    A안 제안 ⑥ L(%.1f, %.1f) → 획지 7 · ⑦ L(%.1f, %.1f) → 획지 13 (외곽도로까지 %.2f m)" % (q6[0], q6[1], q7[0], q7[1], RO["O"].distance(L2R(Point(q7)))))
BLD = M["BLD"]; stb = [b for b in BLD if b["name"] == "구 경주역사"][0]
ST_PLAN = stb["g"]; ST_FP = M["ST_FP"]
ST_REAL = [o for o in CF["B"] if o["inside"] and abs(o["g"].area - 1403) < 5][0]
def mrr_info(gL):
    mr = gL.minimum_rotated_rectangle; cs = list(mr.exterior.coords)
    e = [(np.hypot(cs[i + 1][0] - cs[i][0], cs[i + 1][1] - cs[i][1]), math.degrees(math.atan2(cs[i + 1][1] - cs[i][1], cs[i + 1][0] - cs[i][0])) % 180) for i in range(4)]
    L_, ang = max(e); W_ = min(x[0] for x in e); return L_, W_, ang
pi = mrr_info(ST_PLAN); ri = mrr_info(ST_REAL["g"])
cp = np.array(ST_PLAN.centroid.coords[0]); cr = np.array(ST_REAL["g"].centroid.coords[0])
log("    구 역사 계획 배치: 면적 %.1f㎡ 중심 L(%.1f, %.1f) 외접사각 %.1f×%.1f 긴변 각(x축 기준) %.1f° 높이 %.2f | 상세 메쉬 바닥 ST_FP %.1f㎡ z %s" % (ST_PLAN.area, cp[0], cp[1], pi[0], pi[1], pi[2], stb["h"], ST_FP.area, FN["ST_Z"]))
log("    구 역사 실제 위치(ctx_fixed): 면적 %.1f㎡ 중심 L(%.1f, %.1f) 외접사각 %.1f×%.1f 긴변 각 %.1f° h %.1f | 중심 차 (%.1f, %.1f) = %.1f m · 각도 차 %.1f°" % (ST_REAL["g"].area, cr[0], cr[1], ri[0], ri[1], ri[2], ST_REAL["h"], cr[0] - cp[0], cr[1] - cp[1], np.hypot(*(cr - cp)), ri[2] - pi[2]))
log("    황오동 삼층석탑 L(%.2f, %.2f) 경계 안=%s" % (PAG.x, PAG.y, BR.contains(L2R(PAG))))
SP_ = json.load(open(os.path.join(D, "station_pts.json"), encoding="utf-8"))
spa = np.array(SP_); log("    station_pts.json: 점 %d, R 프레임 x %.1f–%.1f y %.1f–%.1f z %.2f–%.2f" % (len(spa), spa[:, 0].min(), spa[:, 0].max(), spa[:, 1].min(), spa[:, 1].max(), spa[:, 2].min(), spa[:, 2].max()))
spL = MultiPoint([(x - X0, y - Y0) for x, y, z in spa[::7]]).convex_hull
log("    station_pts 볼록껍질(L) 면적 %.1f㎡ · 계획 배치와 겹침 %.1f㎡ · 실제 위치와 겹침 %.1f㎡" % (spL.area, spL.intersection(ST_PLAN).area, spL.intersection(ST_REAL["g"]).area))
# 구역 안 기존 건물(철거 대상) 수
log("    ctx_fixed 구역 안 표시 %d동 · 22,621동 중 3dm 경계 안 중심 %d동" % (sum(1 for o in CF["B"] if o["inside"]), sum(1 for o in CF["B"] if BR.contains(L2R(o["g"].centroid)))))

# ── 9. 지형(3dm 메쉬) z ─────────────────────────────
zs = []; nin = 0; ntot = 0
for o in m.Objects:
    gg = o.Geometry
    if isinstance(gg, r3.Mesh) and lname[o.Attributes.LayerIndex] == "지형_대지":
        V = np.array([(gg.Vertices[i].X, gg.Vertices[i].Y, gg.Vertices[i].Z) for i in range(len(gg.Vertices))])
        top = V[V[:, 2] > -60.0]; ntot += len(top)
        inside = shapely.contains_xy(BR, top[:, 0], top[:, 1]); nin += int(inside.sum())
        zs.append(top[inside])
Z = np.vstack(zs)
log("[9] 지형_대지 메쉬 윗면 정점 %d 중 경계 안 %d · z min %.2f p10 %.2f p50 %.2f p90 %.2f max %.2f" % (ntot, nin, Z[:, 2].min(), *np.percentile(Z[:, 2], [10, 50, 90]), Z[:, 2].max()))
yb = Z[:, 1] - Y0
for y0_ in range(0, 1001, 100):
    sel = (yb >= y0_) & (yb < y0_ + 100)
    if sel.sum(): log("    L y %4d–%4d: 정점 %6d z p50 %.2f (p10 %.2f · p90 %.2f)" % (y0_, y0_ + 100, sel.sum(), np.median(Z[sel, 2]), np.percentile(Z[sel, 2], 10), np.percentile(Z[sel, 2], 90)))
bz = sorted(set(round(o.Geometry.GetBoundingBox().Min.Z, 3) for o in m.Objects if not isinstance(o.Geometry, r3.PolylineCurve)))
log("    지형 객체 바닥 z 값 종류: %s" % bz)
# 레이어별 범위(경계 bbox 대비 여유)
for li, nm in lname.items():
    objs = [o for o in m.Objects if o.Attributes.LayerIndex == li]
    if not objs: continue
    bbs = [o.Geometry.GetBoundingBox() for o in objs]
    x0_ = min(b.Min.X for b in bbs); x1_ = max(b.Max.X for b in bbs); y0b = min(b.Min.Y for b in bbs); y1b = max(b.Max.Y for b in bbs)
    log("    %s: 서 %.1f · 동 %.1f · 남 %.1f · 북 %.1f m (경계 bbox 바깥 여유)" % (nm, BR.bounds[0] - x0_, x1_ - BR.bounds[2], BR.bounds[1] - y0b, y1b - BR.bounds[3]))

# ── 10. mass_v1.pkl 개요 ───────────────────────────
MV = pickle.load(open(os.path.join(ROOT, r"work\20261015_midterm_critique\mass_v1\data\mass_v1.pkl"), "rb"))
log("[10] mass_v1.pkl keys %s · 동 %d · TOT %s · DECKS %d" % (list(MV.keys()), len(MV["BLD"]), {k: round(v, 1) for k, v in MV["TOT"].items()}, len(MV["DECKS"])))
log("     BLD[0] keys %s" % list(MV["BLD"][0].keys()))
log("     S2 LOTS 합 %.1f · 원 LOTS와 같은 형상 %s" % (sum(l["g"].area for l in MV["S"]["LOTS"]), all(MV["S"]["LOTS"][i]["g"].equals(S["LOTS"][i]["g"]) for i in range(13))))
cats = collections.Counter(b["main"] for b in MV["BLD"]); log("     용도별 동 수 %s · 최고 층 %d · 최고 높이 %.1f" % (dict(cats), max(b["floors"] for b in MV["BLD"]), max(b["h"] for b in MV["BLD"])))

# ── 11. GeoJSON(R 프레임) ──────────────────────────
F = []
def feat(geom, **props):
    F.append({"type": "Feature", "properties": props, "geometry": mapping(geom)})
def rnd(g, nd=3):
    h = shapely.transform(g, lambda a: np.round(a, nd))
    if h.geom_type in ("Polygon", "MultiPolygon") and not h.is_valid:
        h2 = h.buffer(0); log("     rnd: 반올림 후 무효 → buffer(0) 면적 차 %.4f㎡" % (h2.area - g.area)); h = h2
    return h
feat(rnd(BR), layer="boundary", name="대지경계선 228,025㎡", source="구경주역_최종대지_대지경계선.3dm 레이어 대지경계선(PolylineCurve 126점)",
     area_R_m2=round(BR.area, 2), area_5187_m2=round(B87.area, 2), area_geodesic_m2=round(abs(ga), 2), perimeter_m=round(BR.length, 2), fixed=True, grade="[산정]")
CLS = [("획지%d" % l["no"], L2R(l["g"])) for l in S["LOTS"]] + [("공원%s" % p_["key"], L2R(p_["g"])) for p_ in S["PARKS"]] +       [("보행%s" % k_, L2R(OP[k_]["g"])) for k_ in ("D", "E", "F")] + [("보행PATH8", L2R(S["PATH8"]))] + [("도로%s" % k_, v_) for k_, v_ in RO.items()] + [("보도WALK", L2R(S["WALK"]))]
BLDR = [(b["name"], b["lot"], L2R(b["g"])) for b in M["BLD"]]
def breakdown(q):
    s0 = np.array(q.coords[0]); u = np.array(q.coords[-1]) - s0; u /= np.linalg.norm(u); rows = []
    for c_, g_ in CLS:
        ix_ = q.intersection(g_)
        for w_ in (ix_.geoms if hasattr(ix_, "geoms") else [ix_]):
            if w_.is_empty or w_.length < 0.3: continue
            a_ = float(np.dot(np.array(w_.coords[0]) - s0, u)); b_ = float(np.dot(np.array(w_.coords[-1]) - s0, u))
            rows.append([round(min(a_, b_), 1), round(max(a_, b_), 1), c_])
    rows.sort(); return rows
def blocked(q):
    out = []
    for nm_, lot_, g_ in BLDR:
        ix_ = q.intersection(g_)
        if not ix_.is_empty and ix_.length > 0.3: out.append([nm_, lot_, round(ix_.length, 1)])
    return out
for a in AX:
    segs = a["seg"]
    if a["key"] == "A3":                      # ①과 만나는 점에서 자른다: 앞은 사선 보행축(고정), 뒤는 D0 화살표 연장(획지 8 관통)
        jn = L2R(AX[0]["line"]).intersection(L2R(a["line"]))
        q = segs[0]; d_ = q.project(jn)
        segs = [shapely.ops.substring(q, 0, d_), shapely.ops.substring(q, d_, q.length)]
    for j, q in enumerate(segs):
        fx = not (a["key"] == "A3" and j == 1)
        feat(rnd(q), layer="axis_centerline_in_site" if fx else "axis_extension_in_site", key=a["key"], name=a["name"] + ("" if fx else " — ① 교점 북동쪽 연장(D0 화살표)"), width_m=a["width"], part=j, length_m=round(q.length, 1),
             landuse=breakdown(q), blocked_by_buildings_V0=blocked(q), source=a["src"], fixed=fx, grade="[산정]")
    feat(rnd(L2R(LineString(a["drawn"]))), layer="axis_extension_drawn", key=a["key"], name=a["name"] + " (D0 그림 화살표 끝점)", source=a["src"], fixed=False, grade="[판단] 다이어그램 표현값")
    feat(rnd(L2R(a["band"])), layer="axis_band", key=a["key"], name=a["name"] + " 띠", width_m=a["width"], area_m2=round(L2R(a["band"]).area, 1), source="model.pkl S(중간마감 최종본)", fixed=True, grade="[산정]")
    for k, p in a["anchors"].items():
        feat(rnd(L2R(Point(p))), layer="axis_anchor", key=a["key"], name=k, source="district.pkl TOUR/HER", grade="[T2] 관광지·문화재 위치 자료(district.pkl)")
for k, rd in RD.items():
    feat(rnd(rd["poly"]), layer="road_polygon", key=k, name=rd["name"], area_m2=round(rd["poly"].area, 1), width_design_m=rd["wdes"], source="model.pkl S.ROADS = road_sel.json 사용자 선택 객체 −1080.4963", fixed=True, grade="[산정]")
    feat(rnd(rd["cl"], 2), layer="road_centerline", key=k, name=rd["name"] + " 중심선(보로노이 골격, 근사)", width_p10_m=round(rd["w"]["p10"], 1), width_p50_m=round(rd["w"]["p50"], 1), width_p90_m=round(rd["w"]["p90"], 1), length_m=round(rd["w"]["length"], 1), width_design_m=rd["wdes"], source="r5_assemble.py 골격 추출", grade="[산정] 근사")
for no in sorted(LOT):
    l = LOT[no]; ml = MLOT[no]
    feat(rnd(L2R(l["g"])), layer="lot_reference_V0", no=no, code=l["code"], use=l["use"], name=l["name"], cat=l["cat"], area_m2=round(l["g"].area, 1), ba_m2=round(ml["ba"], 1), gfa_m2=round(ml["gfa"], 1), bcr=round(ml["bcr"], 3), far=round(ml["far"], 3), maxf=ml["maxf"], maxh_m=round(ml["maxh"], 1),
         source="model.pkl LOTS(중간마감 최종본)", fixed=False, note="비교안 V0 — 엔진이 다시 나눌 대상(고정 입력 아님)", grade="[산정]")
for e in ENTRIES:
    feat(rnd(L2R(Point(e["pL"]))), layer="vehicle_entry", no=e["i"], lot=e["no"], road=e["road"], dir=[round(float(e["d"][0]), 3), round(float(e["d"][1]), 3)], status=e["status"], source="g3m_street_plan.py ENT(픽셀→L) · r1_hwarangro.py(A안)", grade="[판단] 사용자 지정(캡처 픽셀 변환, 오차 수 m)")
feat(rnd(L2R(ST_PLAN)), layer="station", name="구 경주역사 — 계획 모델 배치(사용자 결정 2026-10-15 유지)", area_m2=round(ST_PLAN.area, 1), h_m=round(stb["h"], 2), fixed=True, source="model.pkl BLD '구 경주역사'", grade="[산정]")
feat(rnd(L2R(ST_FP)), layer="station", name="구 경주역사 — 계획 모델 상세 메쉬 바닥(ST_FP)", area_m2=round(ST_FP.area, 1), z_range=list(FN["ST_Z"]), fixed=True, source="model.pkl ST_FP / final.pkl ST", grade="[산정]")
feat(rnd(L2R(ST_REAL["g"])), layer="station", name="구 경주역사 — 실제 위치(콘타 모델 빌딩, 지적 정합)", area_m2=round(ST_REAL["g"].area, 1), h_m=ST_REAL["h"], fixed=False, source="ctx_fixed.pkl(검토안 v1-b 기준)", grade="[산정] 정합 오차 수 m")
feat(rnd(L2R(PAG)), layer="heritage", name="황오동 삼층석탑(문화재자료 8호)", buffer_note="크리틱 v1 규칙: 둘레 12 m 비움", source="district.pkl HER", grade="[T2]")
meta = {"frame": "R(대지 3dm 실축척 프레임) — 구경주역_최종대지_대지경계선.3dm 과 같은 좌표, 단위 m(3dm 단위 표기는 mm지만 1단위 = 1 m)",
        "to_L": "L = R − (1166600, 1761100)", "to_EPSG5179": "X = R − (11616.38, −796.58)", "to_EPSG5187": "5179 → 5187 pyproj(always_xy)",
        "from_O_contour": "R = 2·O − (1143532.6157, 1763242.48)", "from_P_plan_v3": "R = P − (517.0557, 0)", "from_road_sel": "R = road_sel − (1080.4963, 0)",
        "made": "2026-10-26 r5_assemble.py(읽기 전용 검산)", "note": "RFC 7946은 WGS84를 요구하므로 이 파일은 로컬 프레임 교환용이다. Forma 반입 전 4326으로 바꾼다."}
GJ = {"type": "FeatureCollection", "name": "site_inputs_R_frame", "crs_note": meta, "features": F}
json.dump(GJ, open(os.path.join(OUTD, "site_inputs.geojson"), "w", encoding="utf-8"), ensure_ascii=False)
log("[11] GeoJSON 피처 %d개 저장" % len(F))
log("     레이어별 %s" % dict(collections.Counter(f["properties"]["layer"] for f in F)))
LOG.close()
