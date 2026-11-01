# -*- coding: utf-8 -*-
"""정사영상 정합 정밀화: 타일별 평행이동 잔차 → 전체 아핀 추정"""
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
print(key, W, H, "px", px)
s = 0.5  # 작업 해상도 m/px
f = int(round(s / px))
g1 = cv2.resize(g, (W // f, H // f), interpolation=cv2.INTER_AREA)
gb = cv2.GaussianBlur(g1.astype(np.float32), (0, 0), 1.2)
Gx = cv2.Sobel(gb, cv2.CV_32F, 1, 0, ksize=3); Gy = cv2.Sobel(gb, cv2.CV_32F, 0, 1, ksize=3)
G = np.sqrt(Gx ** 2 + Gy ** 2)
G = np.minimum(G, np.percentile(G, 99)); G = cv2.GaussianBlur(G, (0, 0), 1.0)
# 벡터 래스터: 영상 틀(= ox,oy 기준) 위에 직접 그린다 → 픽셀 (i,j) 가 같은 위치
h1, w1 = G.shape
M = raster_lines([V["bldg"], V["roadA"]], ox, oy, w1, h1, s, thick=1)
M = cv2.GaussianBlur(M.astype(np.float32), (0, 0), 1.0)
# 타일별
tile = 700  # px (=350m)
res = []
for r0 in range(0, h1 - tile + 1, tile):
    for c0 in range(0, w1 - tile + 1, tile):
        t = G[r0:r0 + tile, c0:c0 + tile]
        # 템플릿 = 중앙 (tile-2*m), 탐색 ±m
        m = 24  # ±12 m
        tt = t[m:-m, m:-m]
        sub = M[r0:r0 + tile, c0:c0 + tile]
        if sub.max() <= 0 or M[r0:r0 + tile, c0:c0 + tile].sum() < 500:
            continue
        r_ = cv2.matchTemplate(sub, tt, cv2.TM_CCOEFF_NORMED)
        mi, mx, mnl, mxl = cv2.minMaxLoc(r_)
        # 서브픽셀 포물선 보간
        dx, dy = mxl
        def para(a, b, c):
            d = a - 2 * b + c
            return 0 if d == 0 else 0.5 * (a - c) / d
        px_ = dx + (para(r_[dy, dx - 1], r_[dy, dx], r_[dy, dx + 1]) if 0 < dx < r_.shape[1] - 1 else 0)
        py_ = dy + (para(r_[dy - 1, dx], r_[dy, dx], r_[dy + 1, dx]) if 0 < dy < r_.shape[0] - 1 else 0)
        # 영상 템플릿을 (m,m) 위치에서 벡터 위의 (px_,py_) 에 놓을 때 최적 → 이동량 = (px_-m, py_-m) px
        shx = (px_ - m) * s; shy = (py_ - m) * s  # 영상 내용이 벡터 대비 (+x=동, +y=남[행 증가]) 이동해야 할 양
        cx = ox + (c0 + tile / 2) * s; cy = oy - (r0 + tile / 2) * s
        res.append((cx, cy, shx, shy, mx))
        print(f"tile r{r0} c{c0}: center=({cx:.0f},{cy:.0f}) shift(px→ x:{shx:+.1f} m, rows:{shy:+.1f} m) score {mx:.2f}")
res = np.array(res)
good = res[res[:, 4] > 0.15]
print("n tiles", len(res), "good", len(good))
print("mean shift x", good[:, 2].mean(), "row", good[:, 3].mean(), "std", good[:, 2].std(), good[:, 3].std())
np.save(SCR + f"{key}_tiles.npy", res)
