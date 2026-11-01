# -*- coding: utf-8 -*-
"""정사영상: 영역별 점수면(벡터 윤곽을 평행이동시키며 영상 기울기 평균) — 정합 평행이동과 영역별 차이 확인"""
import sys, json
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from histvec import *
import cv2
V = get()
key = sys.argv[1] if len(sys.argv) > 1 else "o2025"
init = json.load(open(SCR + f"{key}_init.json"))
ox, oy = init["top_left_x"], init["top_left_y"]
px = float(init.get("px_m", 0.25))
g = load_full(key, gray=True)
H, W = g.shape
s = 0.5
f = int(round(s / px))
g1 = cv2.resize(g, (W // f, H // f), interpolation=cv2.INTER_AREA)
gb = cv2.GaussianBlur(g1.astype(np.float32), (0, 0), 0.8)
Gx = cv2.Sobel(gb, cv2.CV_32F, 1, 0, ksize=3); Gy = cv2.Sobel(gb, cv2.CV_32F, 0, 1, ksize=3)
G = np.sqrt(Gx ** 2 + Gy ** 2)
G = np.minimum(G, np.percentile(G, 99.5))
G = cv2.GaussianBlur(G, (0, 0), 0.8)
Gn = G / G.mean()
h1, w1 = G.shape
which = sys.argv[2] if len(sys.argv) > 2 else "bldg"
layers = {"bldg": [V["bldg"]], "road": [V["roadA"]], "both": [V["bldg"], V["roadA"]]}[which]
M = raster_lines(layers, ox, oy, w1, h1, s, thick=1) > 0
R = 24
regions = {"all": (0, h1, 0, w1)}
# 사분할 (벡터가 있는 y>359371 → 영상 행 < (oy-359371)/s)
rmax = int((oy - 359500) / s)
regions.update({"NW": (0, rmax // 2, 0, w1 // 2), "NE": (0, rmax // 2, w1 // 2, w1),
                "SW": (rmax // 2, rmax, 0, w1 // 2), "SE": (rmax // 2, rmax, w1 // 2, w1)})
for name, (r0, r1, c0, c1) in regions.items():
    best = None
    surf = np.zeros((2 * R + 1, 2 * R + 1), np.float32)
    ys, xs = np.nonzero(M[r0:r1, c0:c1])
    ys = ys + r0; xs = xs + c0
    for i, dy in enumerate(range(-R, R + 1)):
        for j, dx in enumerate(range(-R, R + 1)):
            yy = ys + dy; xx = xs + dx
            ok = (yy >= 0) & (yy < h1) & (xx >= 0) & (xx < w1)
            surf[i, j] = Gn[yy[ok], xx[ok]].mean()
    i, j = np.unravel_index(np.argmax(surf), surf.shape)
    # 서브픽셀
    def para(a, b, c):
        d = a - 2 * b + c
        return 0 if d == 0 else 0.5 * (a - c) / d
    di = para(surf[i - 1, j], surf[i, j], surf[i + 1, j]) if 0 < i < surf.shape[0] - 1 else 0
    dj = para(surf[i, j - 1], surf[i, j], surf[i, j + 1]) if 0 < j < surf.shape[1] - 1 else 0
    # 벡터 윤곽을 (dx,dy) 픽셀 이동하면 영상과 맞음 → 영상 좌상단 좌표는 (-dx,+dy)*s 만큼 이동해야 함
    bdx = (j + dj - R) * s; bdy = (i + di - R) * s
    print(f"{name:3s}: n={len(ys)}  score@0={surf[R, R]:.3f}  best={surf[i, j]:.3f} at vector shift dx={bdx:+.2f} m (E), dy={bdy:+.2f} m (rows↓=S)  [맞추려면 벡터를 동쪽으로 {bdx:+.2f}, 남쪽으로 {bdy:+.2f}]")
