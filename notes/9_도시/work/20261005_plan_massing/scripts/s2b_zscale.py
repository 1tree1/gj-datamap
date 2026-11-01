"""모형(3dm) 건물의 높이 단위 확인: 3dm 건물 bbox ↔ NGII 건물(층수) 중심점 매칭 → 층수당 모형 높이, 대지 기준 z."""
import json, pickle
import numpy as np
from pyproj import Transformer
from shapely.geometry import Point
from shapely.strtree import STRtree
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
C0 = np.array([1155149.0, 1762445.9]); T = Transformer.from_crs(5179, 5187, always_xy=True)
D = np.array(json.load(open(SP + r"\bld_3dm.json")))
real = 2 * D[:, :2] - C0
x, y = T.transform(real[:, 0], real[:, 1]); D = np.column_stack([x, y, D[:, 2:]])
B = pickle.load(open(SP + r"\context.pkl", "rb"))["B"]
cent = [Point(b["geom"].centroid) for b in B]
tree = STRtree(cent)
rows = []
for (cx, cy, z0, z1, a) in D:
    p = Point(cx, cy)
    i = tree.nearest(p)
    d = p.distance(cent[i])
    if d < 2.5:
        areaR = B[i]["geom"].area
        if abs(areaR / (a * 4) - 1) < 0.15:
            rows.append((B[i]["floors"], z1 - z0, z0, d))
rows = np.array(rows)
print("매칭", len(rows), "/", len(D))
for f in range(1, 7):
    s = rows[rows[:, 0] == f]
    if len(s): print("층수 %d: n=%d  모형높이 dz 중앙값 %.3f (층당 %.3f), z0 중앙값 %.2f" % (f, len(s), np.median(s[:, 1]), np.median(s[:, 1]) / f, np.median(s[:, 2])))
print("전체 z0 사분위:", np.percentile(rows[:, 2], [5, 25, 50, 75, 95]))
