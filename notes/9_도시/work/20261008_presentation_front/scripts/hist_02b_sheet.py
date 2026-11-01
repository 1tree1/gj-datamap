# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")
import geopandas as gpd
import numpy as np
from pyproj import Transformer
D = "C:/Users/OFFICE/Desktop/9_도시/대지/(B020)연속수치지도_202609132098/"
g = gpd.read_file(D + "N3A_H0010000.shp", encoding="cp949")
print(g.crs)
print(g[["gid", "dycd", "dynm"]])
t = Transformer.from_crs("EPSG:5179", "EPSG:5187", always_xy=True)
t2 = Transformer.from_crs("EPSG:5179", "EPSG:4326", always_xy=True)
for _, r in g.iterrows():
    c = np.array(r.geometry.exterior.coords)
    x, y = t.transform(c[:, 0], c[:, 1])
    lo, la = t2.transform(c[:, 0], c[:, 1])
    print(r.dycd, "5187 corners:", [(round(a, 1), round(b, 1)) for a, b in zip(x, y)][:5])
    print("   lonlat:", [(round(a, 5), round(b, 5)) for a, b in zip(lo, la)][:5])
