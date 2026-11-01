# -*- coding: utf-8 -*-
"""2025 정사영상(35901069) 지리참조 1단계: 건물 윤곽 vs 영상 기울기 상관 → 평행이동 추정"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from histvec import *
import cv2, json, time
V = get()

t0 = time.time()
g = load_full("o2025", gray=True)
print("loaded", g.shape, time.time() - t0)
f = 4
g1 = cv2.resize(g, (g.shape[1] // f, g.shape[0] // f), interpolation=cv2.INTER_AREA)  # 1 m/px
print("ds", g1.shape)
gb = cv2.GaussianBlur(g1.astype(np.float32), (0, 0), 1.0)
gx = cv2.Sobel(gb, cv2.CV_32F, 1, 0, ksize=3)
gy = cv2.Sobel(gb, cv2.CV_32F, 0, 1, ksize=3)
G = np.sqrt(gx ** 2 + gy ** 2)
G = np.minimum(G, np.percentile(G, 99))
G = cv2.GaussianBlur(G, (0, 0), 1.0)

# 건물 윤곽 + 도로 면 윤곽 래스터 (1 m/px), 영역: x 217900-220700, y 358900-361700
X0, Y1 = 217800.0, 361900.0
W, H = 3000, 3500
M = raster_lines([V["bldg"]], X0, Y1, W, H, 1.0, thick=1)
M = cv2.GaussianBlur(M.astype(np.float32), (0, 0), 1.0)
res = cv2.matchTemplate(M, G.astype(np.float32), cv2.TM_CCOEFF_NORMED)
print("res", res.shape, res.min(), res.max())
mi, mx, mnl, mxl = cv2.minMaxLoc(res)
print("peak", mx, mxl, "second-peak check:")
# 두 번째 봉우리(주변 20px 제외)
r2 = res.copy()
x, y = mxl
r2[max(0, y - 20):y + 20, max(0, x - 20):x + 20] = -1
print("  2nd", r2.max(), "mean", res.mean(), "std", res.std())
# 영상 좌상단(0,0) 픽셀의 5187 좌표
ox = X0 + mxl[0] * 1.0
oy = Y1 - mxl[1] * 1.0
print("ortho top-left (5187):", ox, oy, " -> extent x", ox, ox + g1.shape[1], " y", oy - g1.shape[0], oy)
json.dump(dict(top_left_x=ox, top_left_y=oy, px=1.0 * f / f, score=float(mx)), open(SCR + "o2025_init.json", "w"))
