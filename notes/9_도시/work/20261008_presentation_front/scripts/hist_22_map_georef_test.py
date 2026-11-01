# -*- coding: utf-8 -*-
"""1976/1984 1:5000 지도: 내장 지리참조 -> (5176 또는 2096) -> 5187 가설을 벡터 도로 윤곽 겹침으로 검증"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from histvec import *
import rasterio
from pyproj import Transformer
V = get()
key = sys.argv[1]; crs_name = sys.argv[2]
f = 6
a = load_full(key, gray=True)
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
with rasterio.open(SRC[key]) as r:
    T = r.transform
print(key, a.shape, "embedded:", T)
tr = Transformer.from_crs(f"EPSG:{crs_name}", "EPSG:5187", always_xy=True)
# ds px -> 원 px -> (E,N) -> 5187
def px_to_5187(col, row):
    E = T.c + T.a * (col + 0.5) + T.b * (row + 0.5)
    N = T.f + T.d * (col + 0.5) + T.e * (row + 0.5)
    return tr.transform(E, N)
vis = cv2.cvtColor(ds, cv2.COLOR_GRAY2BGR)
# 벡터 -> 지도 ds px : 역변환 (5187 -> E,N -> px)
inv = Transformer.from_crs("EPSG:5187", f"EPSG:{crs_name}", always_xy=True)
Ti = ~T
def geo_to_ds(x, y):
    E, N = inv.transform(x, y)
    col, row = Ti * (E, N)
    return (np.asarray(col) - 0.5) / f, (np.asarray(row) - 0.5) / f
for g, colr in [(V["roadA"], (0, 0, 255)), (V["rail"], (255, 0, 255))]:
    for ln in geom_lines(g):
        u, v = geo_to_ds(ln[:, 0], ln[:, 1])
        p = np.stack([u, v], 1)
        if p[:, 0].max() < 0 or p[:, 0].min() > ds.shape[1] or p[:, 1].max() < 0 or p[:, 1].min() > ds.shape[0]:
            continue
        cv2.polylines(vis, [np.round(p).astype(np.int32)], False, colr, 1, cv2.LINE_AA)
cv2.imwrite(SCR + f"prev/mapgeo_{key}_{crs_name}.png", vis)
print(vis.shape)
