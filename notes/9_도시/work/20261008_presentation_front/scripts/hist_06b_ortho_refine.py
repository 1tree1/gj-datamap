# -*- coding: utf-8 -*-
"""정사영상 정합 정밀화(큰 창): 800 m 창 × 겹침, 탐색 ±10 m, 서브픽셀"""
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
gb = cv2.GaussianBlur(g1.astype(np.float32), (0, 0), 1.0)
Gx = cv2.Sobel(gb, cv2.CV_32F, 1, 0, ksize=3); Gy = cv2.Sobel(gb, cv2.CV_32F, 0, 1, ksize=3)
G = np.sqrt(Gx ** 2 + Gy ** 2)
G = np.minimum(G, np.percentile(G, 99)); G = cv2.GaussianBlur(G, (0, 0), 1.0)
h1, w1 = G.shape
M = raster_lines([V["bldg"], V["roadA"]], ox, oy, w1, h1, s, thick=1)
M = cv2.GaussianBlur(M.astype(np.float32), (0, 0), 1.0)
win = 1600  # px = 800 m
step = 800
m = 20
out = []
for r0 in range(0, h1 - win + 1, step):
    for c0 in range(0, w1 - win + 1, step):
        sub = M[r0:r0 + win, c0:c0 + win]
        t = G[r0 + m:r0 + win - m, c0 + m:c0 + win - m]
        if sub.sum() < 2e4:
            continue
        r_ = cv2.matchTemplate(sub, t, cv2.TM_CCOEFF_NORMED)
        mi, mx, mnl, mxl = cv2.minMaxLoc(r_)
        dx, dy = mxl
        def para(a, b, c):
            d = a - 2 * b + c
            return 0 if d == 0 else 0.5 * (a - c) / d
        px_ = dx + (para(r_[dy, dx - 1], r_[dy, dx], r_[dy, dx + 1]) if 0 < dx < r_.shape[1] - 1 else 0)
        py_ = dy + (para(r_[dy - 1, dx], r_[dy, dx], r_[dy + 1, dx]) if 0 < dy < r_.shape[0] - 1 else 0)
        shx = (px_ - m) * s; shy = (py_ - m) * s
        cx = ox + (c0 + win / 2) * s; cy = oy - (r0 + win / 2) * s
        out.append((cx, cy, shx, shy, mx))
        print(f"win r{r0} c{c0}: center=({cx:.0f},{cy:.0f}) shift E {shx:+.2f} m, S {shy:+.2f} m, score {mx:.3f}")
out = np.array(out)
print("mean E", out[:, 2].mean(), "S", out[:, 3].mean(), "std", out[:, 2].std(), out[:, 3].std())
np.save(SCR + f"{key}_wins.npy", out)
