# -*- coding: utf-8 -*-
"""S8 지형 추종 조립 데이터. design_v3.json(계획 좌표 m, z=0) + terrain_samples.json(aardvark 맥락 좌표, 원본 대지 상단 z 샘플 1.5 단위 격자)
→ build_ctx.json (aardvark, 반축척 맥락 좌표) / build_plan.json (armadillo, 계획 좌표 m).
규칙: 공원·녹지·보행로·도로는 지형을 따라가는 메쉬(6 단위 격자 분할), 건축 획지·광장은 획지별 지형 중앙값으로 평탄화, 모든 바닥 요소에 스커트(기준 바닥 112.22)를 붙여 틈이 없게 한다.
매스는 획지 레벨에서 압출(높이는 좌표계 축척에 맞춤). 사용법: python s8_ctx_build.py"""
import json, os, math
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, box, LineString, Point
from shapely.ops import unary_union
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
import mapbox_earcut as earcut

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\5ac42c4f-b205-49dd-aa7e-de94aecf7727\scratchpad"
des = json.load(open(os.path.join(D, "design_v3.json"), encoding="utf-8"))
S = np.array(json.load(open(os.path.join(SP, "terrain_samples.json"))))
TX, TY = 571507.78, 881621.24          # ctx = 0.5*plan + (TX,TY)
Z_SLAB, Z_BASE = 143.5, 112.22         # armadillo 기준(z'=2(z-143.5)), 맥락 솔리드 바닥
CELL = 6.0
OFF = dict(lot=0.0, plaza=0.02, green=0.0, walk=-0.05, road=-0.25)

lin = LinearNDInterpolator(S[:, :2], S[:, 2]); near = NearestNDInterpolator(S[:, :2], S[:, 2])
def terrain(xy):
    xy = np.asarray(xy, float).reshape(-1, 2); z = lin(xy)
    m = np.isnan(z)
    if m.any(): z[m] = near(xy[m])
    return z

def to_ctx(pts): a = np.asarray(pts, float); return a * 0.5 + [TX, TY]
def poly_ctx(parts):
    return unary_union([Polygon(to_ctx(q["ext"]), [to_ctx(h) for h in q["holes"]]).buffer(0) for q in parts])

def tri_polygon(P):
    """단일 폴리곤(구멍 포함) → (verts Nx2, tris Mx3)"""
    rings = [np.array(P.exterior.coords)[:-1]] + [np.array(h.coords)[:-1] for h in P.interiors]
    verts = np.vstack(rings); ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
    tri = earcut.triangulate_float64(verts, ends)
    return verts, np.asarray(tri, dtype=np.int64).reshape(-1, 3)

def polys(g):
    if g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for p in g.geoms if p.geom_type == "Polygon" and p.area > 1e-6]

def draped_mesh(G, zfun, grid=14.0, edge=4.0):
    """G 를 외곽 조밀화(edge) + 내부 격자(grid) 점으로 Delaunay 삼각화, 무게중심이 G 안인 삼각형만 유지. 정점 z = zfun(xy)"""
    from scipy.spatial import Delaunay
    V, F = [], []
    for P in polys(G):
        pts = []
        for ring in [P.exterior] + list(P.interiors):
            L = ring.length; n = max(3, int(L / edge))
            pts += [ring.interpolate(i * L / n).coords[0] for i in range(n)]
        b = P.bounds
        for x in np.arange(b[0] + grid / 2, b[2], grid):
            for y in np.arange(b[1] + grid / 2, b[3], grid):
                if P.contains(Point(x, y)) and P.exterior.distance(Point(x, y)) > edge * 0.6: pts.append((x, y))
        pts = np.array(pts)
        if len(pts) < 3: continue
        tri = Delaunay(pts).simplices
        keep = [t for t in tri if P.contains(Point(pts[t].mean(axis=0)))]
        if not keep: continue
        z = zfun(pts); base = len(V)
        V += [[float(a), float(b_), float(c_)] for (a, b_), c_ in zip(pts, z)]; F += [[int(i) + base for i in t] for t in keep]
    return V, F

def skirt(G, zfun, zbot=Z_BASE, step=2.0):
    V, F = [], []
    for P in polys(G):
        for ring in [P.exterior] + list(P.interiors):
            L = ring.length; n = max(4, int(L / step))
            pts = np.array([ring.interpolate(i * L / n).coords[0] for i in range(n + 1)])
            z = zfun(pts)
            for i in range(n):
                a, b_ = pts[i], pts[i + 1]; za, zb = float(z[i]), float(z[i + 1])
                k = len(V); V += [[a[0], a[1], za], [b_[0], b_[1], zb], [b_[0], b_[1], zbot], [a[0], a[1], zbot]]
                F += [[k, k + 1, k + 2], [k, k + 2, k + 3]]
    return V, F

def merge(*mv):
    V, F = [], []
    for v, f in mv:
        k = len(V); V += v; F += [[i + k for i in t] for t in f]
    return V, F

def flat_z_of(G):
    b = G.bounds; xs = np.arange(b[0], b[2], 1.5); ys = np.arange(b[1], b[3], 1.5)
    pts = np.array([(x, y) for x in xs for y in ys]) if len(xs) and len(ys) else np.array([[G.centroid.x, G.centroid.y]])
    inside = [p for p in pts if G.contains(Point(p))] or [[G.centroid.x, G.centroid.y]]
    return float(np.median(terrain(np.array(inside))))

E = []   # elements
def add(layer, name, kind, data): E.append(dict(layer=layer, name=name, kind=kind, data=data))

# ── 획지(평탄) ──────────────────────────────────────────────────────────────
LOTZ = {}
for l in des["lots"]:
    G = poly_ctx(l["parts"]); z = flat_z_of(G); LOTZ[l["code"]] = z
    for P in polys(G):
        add(["01 획지(건축용지)", l["layer"]], "%s %s | 지반 z=%.2f" % (l["code"], l["use"], z), "extrude",
            dict(ext=np.array(P.exterior.coords).tolist(), holes=[np.array(h.coords).tolist() for h in P.interiors], z0=Z_BASE, z1=z + OFF["lot"]))
    add(["01 획지(건축용지)", l["layer"]], "%s 획지 경계" % l["code"], "curve", [[float(x), float(y), z + 0.03] for x, y in np.array(G.exterior.coords)])
# ── 광장·마당(호스트 획지 레벨 또는 지형) ──────────────────────────────────
for p in des["plazas"]:
    G = poly_ctx(p["parts"])
    if p["host"] in LOTZ:
        z = LOTZ[p["host"]] + OFF["plaza"]
        for P in polys(G):
            add(["03 광장·공공공지", p["kind"]], "%s(%s)" % (p["name"], p["host"]), "extrude",
                dict(ext=np.array(P.exterior.coords).tolist(), holes=[np.array(h.coords).tolist() for h in P.interiors], z0=Z_BASE, z1=z))
        continue
    zf = lambda xy: terrain(xy) + OFF["plaza"]; V, F = merge(draped_mesh(G, zf), skirt(G, zf))
    add(["03 광장·공공공지", p["kind"]], "%s(%s)" % (p["name"], p["host"]), "mesh", dict(v=V, f=F))
# ── 공원·녹지 / 보행 / 도로 (지형 추종) ──────────────────────────────────────
for g in des["greens"]:
    G = poly_ctx(g["parts"]); zf = lambda xy: terrain(xy) + OFF["green"]
    V, F = merge(draped_mesh(G, zf), skirt(G, zf))
    add(["02 공원·녹지(도시계획시설)", g["kind"]], "%s %s %s" % (g["code"], g["kind"], g["name"]), "mesh", dict(v=V, f=F))
for w in des["walks"]:
    G = poly_ctx(w["parts"]); zf = lambda xy: terrain(xy) + OFF["walk"]
    V, F = merge(draped_mesh(G, zf), skirt(G, zf))
    add(["05 보행자전용도로·보도", w["kind"]], w["kind"], "mesh", dict(v=V, f=F))
for r in des["roads"]:
    G = poly_ctx(r["parts"]); zf = lambda xy: terrain(xy) + OFF["road"]
    V, F = merge(draped_mesh(G, zf), skirt(G, zf))
    add(["04 도로"], "도로", "mesh", dict(v=V, f=F))
# ── 매스(획지 레벨, 높이 축척 1/2) ───────────────────────────────────────────
for m in des["masses"]:
    z0 = LOTZ[m["lot"]]
    for q in m["parts"]:
        add(["06 건축물(매스)", m["cat"] if m["cat"] != "역사유산" else "역사유산(구 역사 존치)"], "%s %s" % (m["lot"], m["name"]), "extrude",
            dict(ext=to_ctx(q["ext"]).tolist(), holes=[to_ctx(h).tolist() for h in q["holes"]], z0=z0, z1=z0 + m["h"] * 0.5))
for pv in des["pavilions"]:
    for q in pv["parts"]:
        c = Polygon(to_ctx(q["ext"])).centroid; z0 = float(terrain([[c.x, c.y]])[0])
        add(["06 건축물(매스)", "파빌리온"], "공원 파빌리온", "extrude", dict(ext=to_ctx(q["ext"]).tolist(), holes=[], z0=z0, z1=z0 + 2.25))
# ── 식재 ───────────────────────────────────────────────────────────────────
lotpolys = {l["code"]: poly_ctx(l["parts"]) for l in des["lots"]}
for kind, pts in des["trees"].items():
    lay = {"street": "가로수", "park": "공원수", "lot": "획지 조경수"}[kind]; r = {"street": 1.3, "park": 1.7, "lot": 1.2}[kind]
    P = to_ctx(np.asarray(pts, float)[:, :2]); z = terrain(P)
    for (x, y), zz in zip(P, z):
        zz = float(zz)
        if kind == "lot":
            for code, G in lotpolys.items():
                if G.contains(Point(x, y)): zz = LOTZ[code]; break
        add(["07 식재", lay], "", "tree", [float(x), float(y), zz, r])
# ── 경계·라벨 ──────────────────────────────────────────────────────────────
B = to_ctx(des["boundary"]); zb = terrain(B) + 0.12
add(["00 계획구역 경계"], "계획구역 경계", "curve", [[float(x), float(y), float(z)] for (x, y), z in zip(B, zb)])
for lb in des["labels"]:
    x, y = to_ctx([[lb["x"], lb["y"]]])[0]; z = float(terrain([[x, y]])[0]) + 0.3
    add(["08 라벨"], lb["text"], "dot", [float(x), float(y), z, lb["text"]])

json.dump(dict(frame="ctx", elements=E), open(os.path.join(D, "build_ctx.json"), "w", encoding="utf-8"), ensure_ascii=False)
# armadillo 용(계획 좌표): ctx → plan: xy = 2(ctx - T), z = 2(z - Z_SLAB)
def tp(x, y, z): return [2 * (x - TX), 2 * (y - TY), 2 * (z - Z_SLAB)]
E2 = []
for e in E:
    k, d = e["kind"], e["data"]
    if k == "mesh": d2 = dict(v=[tp(*v) for v in d["v"]], f=d["f"])
    elif k == "extrude": d2 = dict(ext=[[2 * (x - TX), 2 * (y - TY)] for x, y in d["ext"]], holes=[[[2 * (x - TX), 2 * (y - TY)] for x, y in h] for h in d["holes"]], z0=2 * (d["z0"] - Z_SLAB), z1=2 * (d["z1"] - Z_SLAB))
    elif k == "tree": d2 = tp(d[0], d[1], d[2]) + [d[3] * 2]
    elif k == "dot": d2 = tp(d[0], d[1], d[2]) + [d[3]]
    elif k == "curve": d2 = [tp(*p) for p in d]
    E2.append(dict(layer=e["layer"], name=e["name"], kind=k, data=d2))
json.dump(dict(frame="plan", elements=E2), open(os.path.join(D, "build_plan.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("lot levels(ctx z):", {k: round(v, 2) for k, v in LOTZ.items()})
print("elements", len(E), "mesh faces", sum(len(e["data"]["f"]) for e in E if e["kind"] == "mesh"))
