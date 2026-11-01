"""v3 규칙 경계·편입 필지(EPSG:5187)를 모형좌표로 변환해 JSON 저장. 변환: model = (real5179 + C) / 2"""
import pickle, json
import numpy as np
from pyproj import Transformer
from shapely import wkb

SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7d42d444-7313-40a1-ac02-6f82986afca6\scratchpad"
C = np.array([1155149.0, 1762445.9])
t = Transformer.from_crs(5187, 5179, always_xy=True)
s1 = pickle.load(open(SP + r"\step1.pkl", "rb")); s2 = pickle.load(open(SP + r"\step2.pkl", "rb"))
Z = json.load(open(SP + r"\user_boundary_from_3dm.json", encoding="utf-8"))[0]["pts"][0][2]

def to_model(coords):
    a = np.array(coords)[:, :2]
    x, y = t.transform(a[:, 0], a[:, 1])
    m = (np.column_stack([x, y]) + C) / 2
    return [[float(p[0]), float(p[1]), Z] for p in m]

P = wkb.loads(s2["P50a"])
bnd = [to_model(p.exterior.coords) for p in (P.geoms if hasattr(P, "geoms") else [P])]
parcels = []
for i in s2["sel"]:
    g = wkb.loads(s1["recs"][i]["geom"])
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        parcels.append(to_model(p.exterior.coords))
json.dump({"z": Z, "boundary": bnd, "parcels": parcels}, open(SP + r"\v3_model_coords.json", "w"))
print("Z", Z, "boundary rings", len(bnd), "pts", [len(b) for b in bnd], "parcel rings", len(parcels))
# 역검증: 모형좌표 → 5187 면적
from pyproj import Transformer as T
back = T.from_crs(5179, 5187, always_xy=True)
from shapely.geometry import Polygon
a = np.array(bnd[0])[:, :2] * 2 - C
x, y = back.transform(a[:, 0], a[:, 1])
print("round-trip area", round(Polygon(zip(x, y)).area), "vs", round(P.area))
