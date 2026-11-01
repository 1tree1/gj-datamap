import json, sys
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon, shape, mapping
from shapely.ops import transform as shp_transform, unary_union
from shapely.validation import make_valid

SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7d42d444-7313-40a1-ac02-6f82986afca6\scratchpad"
ROOT = r"C:\Users\OFFICE\Desktop\9_도시"
C = (1155149.0, 1762445.9)  # 전체기록 §v2: 실좌표(5179) = 2×모형 − C

t_5179_5187 = Transformer.from_crs(5179, 5187, always_xy=True)
t_4326_5187 = Transformer.from_crs(4326, 5187, always_xy=True)

def model_to_5187(pts):
    xy = np.array(pts)[:, :2]
    real = 2 * xy - np.array(C)
    x, y = t_5179_5187.transform(real[:, 0], real[:, 1])
    return list(zip(x, y))

L = json.load(open(SP + r"\layers_boundary_zone.json", encoding="utf-8"))
zone_pts = L["지구단위계획 2026-8::구역경계"][0]["pts"]
user_pts = L["지구단위계획 2026-8::내가 하고자하는 경계라인"][0]["pts"]
print("model coord sample:", zone_pts[0], user_pts[0])

zone = make_valid(Polygon(model_to_5187(zone_pts)))
U = make_valid(Polygon(model_to_5187(user_pts)))
print("zone(3dm→5187) area:", round(zone.area), "  user boundary area:", round(U.area))

# 검증 1: 아카이브 고시 구역(5187)과 3dm 구역경계가 겹치는가
gz = json.load(open(ROOT + r"\archive\C_data\processed\gosi2026-8_zone_5187.geojson", encoding="utf-8"))
zs = unary_union([make_valid(shape(f["geometry"])) for f in gz["features"]])
iou = zone.intersection(zs).area / zone.union(zs).area
print("gosi zone(archive) area:", round(zs.area), " IoU(3dm 구역경계 vs archive):", round(iou, 4))

# 필지
gp = json.load(open(ROOT + r"\archive\C_data\processed\parcels_lu_4326.geojson", encoding="utf-8"))
feats = gp["features"]
print("parcels in file:", len(feats))
recs = []
for f in feats:
    g = shape(f["geometry"])
    g = shp_transform(lambda x, y, z=None: t_4326_5187.transform(x, y), g)
    g = make_valid(g)
    p = f["properties"]
    jib = p.get("jibun", "")
    jimok = jib.split()[-1] if " " in jib else ""
    recs.append(dict(pnu=p["pnu"], jibun=jib, jimok=jimok, addr=p.get("addr", ""), jiga=float(p.get("jiga") or 0),
                     bldg_n=p.get("bldg_n", 0), geom=g))
allp = unary_union([r["geom"] for r in recs])
print("parcel union bounds:", [round(v) for v in allp.bounds], " user bounds:", [round(v) for v in U.bounds])
print("user area covered by parcel polygons:", round(U.intersection(allp).area), "of", round(U.area),
      "→ 필지 없는 면적(미등록·도면공백):", round(U.difference(allp).area))
import pickle
pickle.dump(dict(U=U.wkb, zone=zone.wkb, recs=[{**r, "geom": r["geom"].wkb} for r in recs]), open(SP + r"\step1.pkl", "wb"))
