"""S6 가구별 법정 중첩: 현행 용도지역(필지 lu_list) · 고시 2026-8호 구역 · 고도지구 · 역사문화환경보존지역(V-World UO301) · 기존 건축물(NGII).
출력: scratch/overlay.pkl"""
import json, pickle, re, sys, collections
from pyproj import Transformer
from shapely.geometry import shape, Point
from shapely.ops import transform as shp_transform, unary_union
from shapely import wkb
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
ROOT = r"C:\Users\OFFICE\Desktop\9_도시"
T = Transformer.from_crs(4326, 5187, always_xy=True)
to87 = lambda g: shp_transform(lambda x, y, z=None: T.transform(x, y), g)
C = pickle.load(open(SP + r"\context.pkl", "rb")); NET = pickle.load(open(SP + r"\network.pkl", "rb")); U = C["U"]

zone_gosi = shape(json.load(open(ROOT + r"\archive\C_data\processed\gosi2026-8_zone_5187.geojson", encoding="utf-8"))["features"][0]["geometry"]).buffer(0)
her = json.load(open(ROOT + r"\archive\C_data\raw\vworld_uo301_heritage.geojson", encoding="utf-8"))
print("UO301 heritage features:", len(her["features"]), "props:", her["features"][0]["properties"])
her_polys = []
for f in her["features"]:
    g = to87(shape(f["geometry"])).buffer(0)
    if g.intersects(U): her_polys.append((f["properties"].get("uname") or f["properties"].get("dgm_nm") or "", g))
print("U와 겹치는 UO301:", [(n, round(g.intersection(U).area)) for n, g in her_polys])
her_union = unary_union([g for n, g in her_polys if n == "역사문화환경보존지역"]).buffer(0)
print("역사문화환경보존지역(합집합) ∩ U = %.0f㎡ (U의 %.1f%%)" % (her_union.intersection(U).area, her_union.intersection(U).area / U.area * 100))

# 용도지역 토큰
ZN = ("자연녹지지역", "제1종일반주거지역", "제2종일반주거지역", "제3종일반주거지역", "일반상업지역", "근린상업지역", "준주거지역", "생산녹지지역", "보전녹지지역", "준공업지역", "일반공업지역")
parc = []
for p in C["P"]:
    toks = [t.strip() for t in re.split(r"[·,]", p["lu"])]
    z = next((t for t in toks if t in ZN), "미상")
    parc.append((z, p["geom"], p["bldg_n"]))
godo = [(g["godo_nm"], g["h_max"], g["kind"], g["geom"]) for g in C["G"] if g["geom"].intersects(U)]

out = {}
for b in NET["blocks"]:
    g = b["geom"]; A = g.area
    zc = collections.Counter()
    for z, pg, _ in parc:
        a = g.intersection(pg).area
        if a > 0.5: zc[z] += a
    covered = sum(zc.values())
    if A - covered > 1: zc["필지 외(도로·하천 등 미등록)"] += A - covered
    gos = g.intersection(zone_gosi).area
    h20 = sum(g.intersection(gg).area for n, h, k, gg in godo if k == "최고" and h == 20)
    h15 = sum(g.intersection(gg).area for n, h, k, gg in godo if k == "최고" and h == 15)
    hmin = sum(g.intersection(gg).area for n, h, k, gg in godo if k == "최저")
    her_a = g.intersection(her_union).area
    # 기존 건축물(NGII): 중심점이 가구 안
    nb = [bb for bb in C["B"] if g.contains(bb["geom"].representative_point())]
    fl = collections.Counter(min(bb["floors"], 5) for bb in nb)
    out[b["id"]] = dict(area=A, zone=dict(zc), gosi=gos, h20=h20, h15=h15, hmin=hmin, her=her_a, n_exist=len(nb), exist_area=sum(bb["geom"].area for bb in nb), exist_floors=dict(fl),
                        parcels_bldg=sum(1 for z, pg, n in parc if n and g.intersection(pg).area > 0.5 * pg.area))
    print(b["id"], "%6.0f㎡" % A, "고시 %3.0f%%" % (gos / A * 100), "20m %3.0f%% 15m %3.0f%% 최저 %3.0f%%" % (h20 / A * 100, h15 / A * 100, hmin / A * 100), "보존지역 %3.0f%%" % (her_a / A * 100),
          "기존건물 %3d동" % len(nb), {k: round(v / A * 100) for k, v in zc.items() if v / A > 0.02})
pickle.dump(out, open(SP + r"\overlay.pkl", "wb"))
