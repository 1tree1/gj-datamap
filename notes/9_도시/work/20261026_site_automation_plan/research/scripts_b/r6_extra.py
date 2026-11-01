# -*- coding: utf-8 -*-
"""추가 검산: 축 연속성(토지이용별 구간), 진북각, 지형 윗면(격자 최댓값), 앵커 폴리곤 거리"""
import os, json, pickle, math
import numpy as np
import rhino3dm as r3
import shapely
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely import affinity
import pyproj
ROOT = r"C:\Users\OFFICE\Desktop\9_도시"
D = os.path.join(ROOT, r"work\20261011_masterplan_rough\data")
X0, Y0 = 1166600.0, 1761100.0
SH5179 = (11616.38, -796.58)
LOG = open("r6_log.txt", "w", encoding="utf-8")
def log(*a): LOG.write(" ".join(str(x) for x in a) + "\n"); LOG.flush()
def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []
M = pickle.load(open(os.path.join(D, "model.pkl"), "rb")); S = M["S"]
m = r3.File3dm.Read(os.path.join(ROOT, "구경주역_최종대지_대지경계선.3dm"))
bo = [o for o in m.Objects if isinstance(o.Geometry, r3.PolylineCurve)][0].Geometry
BR = Polygon([(bo.Point(i).X, bo.Point(i).Y) for i in range(bo.PointCount)]); BL = affinity.translate(BR, -X0, -Y0)
OP = {o["key"]: o for o in S["OPEN"]}
# 토지이용 분류(L)
CLS = []
for l in S["LOTS"]: CLS.append(("획지%d %s" % (l["no"], l["name"]), l["g"]))
for p in S["PARKS"]: CLS.append(("공원%s %s" % (p["key"], p["name"]), p["g"]))
for k in ("D", "E", "F"): CLS.append(("보행%s %s" % (k, OP[k]["name"]), OP[k]["g"]))
CLS.append(("보행 PATH8(8 m)", S["PATH8"]))
for k, v in S["ROADS"].items(): CLS.append(("도로%s" % k, v))
CLS.append(("외곽 보도 WALK", S["WALK"]))
v3 = np.array([0.5394, 0.842]); n3 = np.array([-0.842, 0.5394]); F0 = np.array([131.2, 59.5]) + n3 * 10.0
ym2 = sum(S["DBAND"]) / 2; YP8 = 639.2; XNS = 270.9; YEW = (333.70 + 353.66) / 2; BIG = 3000
AX = {"① 남북축": LineString([(XNS, -BIG), (XNS, BIG)]), "② 동서축": LineString([(-BIG, ym2), (BIG, ym2)]),
      "③ 역사유적축": LineString([tuple(F0 - BIG * v3), tuple(F0 + BIG * v3)]), "④ 향일문 조망로": LineString([(-BIG, YP8), (BIG, YP8)]),
      "화랑로 연결": LineString([(-BIG, YEW), (BIG, YEW)])}
for nm, ln in AX.items():
    seg = ln.intersection(BL)
    s0 = np.array(seg.coords[0]); u = np.array(seg.coords[-1]) - s0; Ls = np.linalg.norm(u); u /= Ls
    rows = []
    for cname, g in CLS:
        ix = seg.intersection(g)
        for q in (ix.geoms if hasattr(ix, "geoms") else [ix]):
            if q.is_empty or q.length < 0.3: continue
            a = float(np.dot(np.array(q.coords[0]) - s0, u)); b = float(np.dot(np.array(q.coords[-1]) - s0, u))
            rows.append((min(a, b), max(a, b), cname))
    rows.sort()
    cov = sum(b - a for a, b, c in rows)
    log("[축 구간] %s 경계 안 %.1f m (L 시작 %s → 끝 %s), 분류 합 %.1f m" % (nm, Ls, tuple(round(c, 1) for c in seg.coords[0]), tuple(round(c, 1) for c in seg.coords[-1]), cov))
    for a, b, c in rows:
        p = s0 + u * a; q = s0 + u * b
        log("    %6.1f–%6.1f m (%5.1f m) %s  L(%.1f,%.1f)→(%.1f,%.1f)" % (a, b, b - a, c, p[0], p[1], q[0], q[1]))
# 앵커 폴리곤 거리
DS = pickle.load(open(os.path.join(D, "district.pkl"), "rb"))
JR = [h[0] for h in DS["HER"] if "전랑지" in h[1] and "국가지정" in h[2]][0]
log("[앵커] ② 동서축 직선 ↔ 성동리전랑지 국가지정구역 폴리곤 거리 %.1f m (구역 y %.1f–%.1f)" % (AX["② 동서축"].distance(JR), JR.bounds[1], JR.bounds[3]))
for k, gs in DS["AXES"].items():
    pass
# 화랑로 실제 축선(동서 토막)과 대지 화랑로 연결 y
hw = [g for g in DS["AXES"].get("화랑로", []) if (g.bounds[3] - g.bounds[1]) < 0.3 * max(g.bounds[2] - g.bounds[0], 1)]
near = [g for g in hw if g.bounds[2] > -150 and g.bounds[0] < 120]
log("[앵커] 화랑로 동서 토막(대지 서측 150 m 안) y 범위 %s" % [(round(g.bounds[0], 1), round(g.bounds[2], 1), round(g.bounds[1], 1), round(g.bounds[3], 1)) for g in near])
# 진북각: R(=5179 격자)에서 진북 방향
t_to = pyproj.Transformer.from_crs(5179, 4326, always_xy=True); t_back = pyproj.Transformer.from_crs(4326, 5179, always_xy=True)
c = BR.centroid; X = (c.x - SH5179[0], c.y - SH5179[1]); lon, lat = t_to.transform(*X)
x2, y2 = t_back.transform(lon, lat + 0.001)
ang = math.degrees(math.atan2(x2 - X[0], y2 - X[1]))
log("[진북] 구역 중심 (%.6f°E, %.6f°N) · R 프레임에서 진북은 +y축에서 %.3f° (양수 = 동쪽으로 기움)" % (lon, lat, ang))
t87 = pyproj.Transformer.from_crs(4326, 5187, always_xy=True); a87 = t87.transform(lon, lat); b87 = t87.transform(lon, lat + 0.001)
log("[진북] EPSG:5187에서 진북은 +y축에서 %.3f°" % math.degrees(math.atan2(b87[0] - a87[0], b87[1] - a87[1])))
# 지형 윗면: 5 m 격자 최댓값(경계 안)
Vs = []
for o in m.Objects:
    gg = o.Geometry
    if isinstance(gg, r3.Mesh) and m.Layers.FindIndex(o.Attributes.LayerIndex).FullPath == "지형_대지":
        V = np.array([(gg.Vertices[i].X, gg.Vertices[i].Y, gg.Vertices[i].Z) for i in range(len(gg.Vertices))]); Vs.append(V)
V = np.vstack(Vs); V = V[shapely.contains_xy(BR, V[:, 0], V[:, 1])]
cell = 5.0
ix = np.floor((V[:, 0] - X0) / cell).astype(int); iy = np.floor((V[:, 1] - Y0) / cell).astype(int)
key = ix * 100000 + iy
order = np.lexsort((V[:, 2], key)); ks = key[order]; zs = V[order, 2]
last = np.r_[ks[1:] != ks[:-1], True]
top = dict(zip(ks[last], zs[last]))
Zc = np.array(list(top.values())); Yc = np.array([(k % 100000) * cell + cell / 2 for k in top.keys()])
log("[지형] 경계 안 메쉬 정점 %d · 5 m 격자 %d칸(경계 안 칸 비율 %.0f%%) · 윗면 z min %.2f p50 %.2f max %.2f" % (len(V), len(top), 100 * len(top) * 25 / BR.area, Zc.min(), np.median(Zc), Zc.max()))
for y0_ in range(0, 1001, 100):
    s = (Yc >= y0_) & (Yc < y0_ + 100)
    if s.sum(): log("    L y %4d–%4d: 칸 %4d 윗면 z p10 %.2f p50 %.2f p90 %.2f" % (y0_, y0_ + 100, s.sum(), np.percentile(Zc[s], 10), np.median(Zc[s]), np.percentile(Zc[s], 90)))
# 메쉬가 덮지 않는 경계 안 면적(브렙만 있는 곳) 대략
cov = unary_union([shapely.box(X0 + (k // 100000) * cell, Y0 + (k % 100000) * cell, X0 + (k // 100000 + 1) * cell, Y0 + (k % 100000 + 1) * cell) for k in top.keys()])
log("[지형] 메쉬 정점이 있는 5 m 칸 합집합이 경계와 겹치는 면적 %.0f㎡ (%.0f%%)" % (cov.intersection(BR).area, 100 * cov.intersection(BR).area / BR.area))
# 지형 브렙: 경계 안에 bbox가 걸리는 객체 수
nb = 0
for o in m.Objects:
    gg = o.Geometry
    if isinstance(gg, r3.Brep):
        b = gg.GetBoundingBox()
        if shapely.box(b.Min.X, b.Min.Y, b.Max.X, b.Max.Y).intersects(BR): nb += 1
log("[지형] 경계와 bbox가 겹치는 Brep %d개(레이어 무관)" % nb)
LOG.close()
