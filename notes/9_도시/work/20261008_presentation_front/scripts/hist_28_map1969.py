# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from pyproj import Transformer
key = "m1969"
a = load_full(key, gray=True)
nl = refine_neatline(a, (325, 525, 3887, 4906), win=14, sec=0.6)
print("neatline px:", {k: (round(v, 2) if not isinstance(v, tuple) else tuple(round(x, 1) for x in v)) for k, v in nl.items()})
# 모서리 위경도 (Korean 1985 / Bessel 지리좌표 가정) -> 5187
t = Transformer.from_crs("EPSG:4162", "EPSG:5187", always_xy=True)
lon0, lon1, lat0, lat1 = 129 + 7.5 / 60, 129 + 15 / 60, 35 + 45 / 60, 35 + 52.5 / 60
geo = np.array([t.transform(lon0, lat1), t.transform(lon1, lat1), t.transform(lon1, lat0), t.transform(lon0, lat0)])
px = np.array([[nl["L"], nl["T"]], [nl["R"], nl["T"]], [nl["R"], nl["B"]], [nl["L"], nl["B"]]])
print("geo corners 5187:", geo.round(1).tolist())
H, rms, r = corners_to_H(px, geo, "affine")
print("affine RMS (m):", rms, "resid", r.round(2).tolist(), "px size", np.hypot(H[0, 0], H[1, 0]), np.hypot(H[0, 1], H[1, 1]))
save_transform(key, H, dict(kind="map", source=SRC[key], model="neatline corners (lat/lon, Korean 1985 -> 5187) affine", gsd_eff=float(np.sqrt(abs(np.linalg.det(H[:2, :2])))), size_px=[a.shape[1], a.shape[0]], rms_m=rms))
