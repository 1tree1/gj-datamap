# -*- coding: utf-8 -*-
"""1956·1918·2005·2024 도곽 정밀화 + 5187 아핀 지리참조"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
cfg = {
    "m1956": dict(approx=[(725.5, 329.5), (4284.5, 340), (4276, 3258), (715, 3249)], win=7,
                  box=(129 + 10.4 / 3600, 129 + 10.4 / 3600 + 0.25, 35 + 50 / 60, 36.0), crs="EPSG:4162"),
    "m1918": dict(approx=[(1233.8, 695), (8324, 679), (8362.5, 6545), (1235, 6562.5)], win=9,
                  box=(129 + 10.4 / 3600, 129 + 10.4 / 3600 + 0.25, 35 + 50 / 60, 36.0), crs="EPSG:4162"),
    "m2005": dict(approx=[(143.8, 348.5), (5476.8, 338.7), (5488.3, 6885), (151.3, 6895.5)], win=6,
                  box=(129 + 7 / 60 + 38.18 / 3600, 129 + 15 / 60 + 8.22 / 3600, 35 + 44 / 60 + 49.14 / 3600, 35 + 52 / 60 + 19.19 / 3600), crs="EPSG:4326"),
    "m2024": dict(approx=[(727.8, 550.7), (7823, 540.8), (7845.5, 9274.7), (727.7, 9283.3)], win=6,
                  box=(129.0, 129.25, 35.75, 36.0), crs="EPSG:4326"),
}
which = sys.argv[1:] or list(cfg)
res_all = {}
for key in which:
    c = cfg[key]
    g = load_full(key, gray=True)
    corners, info = frame_corners(g, c["approx"], win=c["win"], mode="line")
    print(key, "refined corners TL,TR,BR,BL:", corners.round(1).tolist())
    print("    approx:", c["approx"])
    print("    side fit rms/n:", {k: (round(v[0], 2), v[1]) for k, v in info.items()})
    H, rms, r = georef_from_frame(key, corners, c["box"], c["crs"], "affine")
    print(f"    georef ({c['crs']}): affine 4-corner RMS {rms:.2f} m; px size {np.hypot(H[0,0],H[1,0]):.3f} x {np.hypot(H[0,1],H[1,1]):.3f} m; rot {np.degrees(np.arctan2(H[1,0],H[0,0])):.3f} deg")
