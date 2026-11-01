"""S0 맥락 데이터 추출 — 경계 U 주변(반경 300 m)의 건물(층수)·도로(중심선·폭)·고도지구·필지를 EPSG:5187로 모아 pickle 저장.
입력: 대지/(B020)연속수치지도_202609132098 (NGII, EPSG:5179 → 읽자마자 5187), archive/C_data/processed/{godo_5187, parcels_lu_4326}.geojson,
      3dm 경계 U (work/20261005_boundary_check/user_boundary_current_5187.geojson)
출력: scratch/context.pkl
"""
import json, pickle, re, sys, warnings
import numpy as np
import shapefile
from pyproj import Transformer
from shapely.geometry import shape, Polygon, LineString, Point, MultiPolygon
from shapely.ops import transform as shp_transform, unary_union
from shapely.strtree import STRtree
warnings.filterwarnings("ignore")

ROOT = r"C:\Users\OFFICE\Desktop\9_도시"
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
SRC = ROOT + r"\대지\(B020)연속수치지도_202609132098"
T79 = Transformer.from_crs(5179, 5187, always_xy=True)
T46 = Transformer.from_crs(4326, 5187, always_xy=True)
to87 = lambda g, t=T79: shp_transform(lambda x, y, z=None: t.transform(x, y), g)

U = shape(json.load(open(ROOT + r"\work\20261005_boundary_check\user_boundary_current_5187.geojson", encoding="utf-8"))["features"][0]["geometry"]).buffer(0)
roi = U.buffer(300)

def read(layer):
    r = shapefile.Reader(SRC + "\\" + layer, encoding="utf-8")
    fl = [f[0] for f in r.fields[1:]]
    for sr in r.iterShapeRecords():
        yield sr.shape.__geo_interface__, dict(zip(fl, sr.record))

# 건물 (층수 nmly)
B = []
for gi, a in read("N3A_B0010000"):
    g = to87(shape(gi))
    if g.intersects(roi): B.append(dict(geom=g, floors=a["nmly"] or 1, kind=a["kind"]))
# 도로 중심선 (폭 rvwd)
R = []
for gi, a in read("N3L_A0020000"):
    g = to87(shape(gi))
    if g.intersects(roi): R.append(dict(geom=g, w=a["rvwd"], rddv=a["rddv"], name=a["name"] or a["rdnm"], lanes=a["rdln"]))
# 도로면
RP = [to87(shape(gi)) for gi, a in read("N3A_A0010000") if to87(shape(gi)).intersects(roi)]
WATER = []
for lay in ("N3A_E0010001", "N3A_E0032111"):
    for gi, a in read(lay):
        g = to87(shape(gi))
        if g.intersects(roi): WATER.append(g)
print("건물", len(B), "도로중심선", len(R), "도로면", len(RP), "하천", len(WATER))

# 고도지구
G = []
for f in json.load(open(ROOT + r"\archive\C_data\processed\godo_5187.geojson", encoding="utf-8"))["features"]:
    g = shape(f["geometry"]).buffer(0)
    if g.intersects(roi): G.append(dict(geom=g, **{k: f["properties"].get(k) for k in ("godo_nm", "h_max", "kind")}))
for x in G: print("고도지구:", x["godo_nm"], x["h_max"], x["kind"], "U 교차 %.0f ㎡" % x["geom"].intersection(U).area)

# 필지(지목·용도지역·건물수)
P = []
for f in json.load(open(ROOT + r"\archive\C_data\processed\parcels_lu_4326.geojson", encoding="utf-8"))["features"]:
    g = to87(shape(f["geometry"]), T46)
    if g.intersects(roi):
        p = f["properties"]; m = re.search(r"([가-힣])$", p["jibun"].strip())
        P.append(dict(geom=g, pnu=p["pnu"], addr=p["addr"], jimok=m.group(1) if m else "", lu=p.get("lu_list", ""), bldg_n=p.get("bldg_n", 0), jiga=float(p.get("jiga") or 0)))
print("필지", len(P))
pickle.dump(dict(U=U, B=B, R=R, RP=RP, WATER=WATER, G=G, P=P), open(SP + r"\context.pkl", "wb"))
print("saved")
