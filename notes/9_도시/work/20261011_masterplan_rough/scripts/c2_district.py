"""C2 지구 규모(S2) 배경 — 대지 축 구상도용. 모든 원자료는 실좌표(EPSG:4326/5187) → 5179 → 로컬(계획 경계 B와 같은 프레임)
- 지적(V-World 연속지적 2025.01): 필지 윤곽, 하천('천')·철도('철') 필지
- 간선도로(도시재생전략계획 2022 기초조사 도로망, T2), 경관축(화랑로 주통경축·북천 수변경관축)
- 국가지정문화재구역·보호구역(V-World UO301), 철도(OSM, T4), 기준점(관광지 점 자료·문화재구역 무게중심)
출력: data/district.pkl"""
import os, json, pickle
import numpy as np
from pyproj import Transformer
import shapely
from shapely.geometry import shape, box, Point
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); A = os.path.join(HERE, "..", "..", "..", "archive", "C_data")
R = pickle.load(open(os.path.join(D, "real_overlay.pkl"), "rb")); S = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
TX, TY, X0, Y0 = R["TX"], R["TY"], S["X0"], S["Y0"]
T4 = Transformer.from_crs(4326, 5179, always_xy=True)
EXT = box(-1300, -1300, 1600, 2300)


def loc(g, src=4326):
    def f(x, y):
        X, Y = T4.transform(x, y); return X + TX - X0, Y + TY - Y0
    return shapely.ops.transform(lambda x, y, z=None: f(x, y), g)


def feats(path): return json.load(open(os.path.join(A, path), encoding="utf-8"))["features"]


PAR = []
for ft in feats("raw/vworld_parcel.geojson"):
    g = loc(shape(ft["geometry"]))
    if g.intersects(EXT): PAR.append((g, ft["properties"]["jibun"].strip()[-1]))
print("parcels", len(PAR))
ROADS = {}
for ft in feats("processed/urban_roads_4326.geojson"):
    g = loc(shape(ft["geometry"]))
    if g.intersects(EXT): ROADS.setdefault(ft["properties"]["name"], []).append(g)
AXES = {}
for ft in feats("processed/landscape_axes_lines_4326.geojson"):
    nm = ft["properties"].get("name") or ft["properties"].get("sub") or ""
    if not any(k in nm for k in ("화랑로", "북천", "동문로", "계림로", "북문로", "태종로", "금성로")): continue
    g = loc(shape(ft["geometry"]))
    if g.intersects(EXT): AXES.setdefault(nm.replace("주통경축 (", "").replace(")", ""), []).append(g)
HER = []
for ft in feats("raw/vworld_uo301_heritage.geojson"):
    g = loc(shape(ft["geometry"]))
    if g.intersects(EXT): HER.append((g, ft["properties"].get("remark") or "", ft["properties"].get("uname") or "", ft["properties"].get("alias") or ""))
RAIL = []
for f in ("processed/rail_abandoned_4326.geojson", "processed/rail_active_4326.geojson"):
    for ft in feats(f):
        g = loc(shape(ft["geometry"]))
        if g.intersects(EXT): RAIL.append((g, ft["properties"].get("cls", "")))
TOUR = {}
for ft in feats("raw/gj_tour_sites.geojson"):
    nm = ft["properties"].get("name") or ft["properties"].get("title") or ""
    g = loc(shape(ft["geometry"]))
    if g.intersects(EXT): TOUR[nm] = (g.x, g.y)
print("roads", {k: len(v) for k, v in ROADS.items()}, "axes", list(AXES), "heritage", len(HER), "rail", len(RAIL), "tour", len(TOUR))
for g, rm, un, al in HER:
    if g.area > 3000: print("   heritage", rm, un, al, round(g.area), [round(v) for v in g.centroid.coords[0]])
pickle.dump(dict(PAR=PAR, ROADS=ROADS, AXES=AXES, HER=HER, RAIL=RAIL, TOUR=TOUR, EXT=EXT.bounds), open(os.path.join(D, "district.pkl"), "wb"))
