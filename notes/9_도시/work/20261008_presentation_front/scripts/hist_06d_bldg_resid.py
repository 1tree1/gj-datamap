# -*- coding: utf-8 -*-
"""정사영상: 큰 건물 윤곽 개별 국소정합 → 평행이동 잔차의 중앙값/분포 (벡터 윤곽 기준)"""
import sys, json
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from histvec import *
import cv2
from shapely.geometry import Polygon
V = get()
key = sys.argv[1] if len(sys.argv) > 1 else "o2025"
init = json.load(open(SCR + f"{key}_init.json"))
ox, oy = init["top_left_x"], init["top_left_y"]
px = float(init.get("px_m", 0.25))
g = load_full(key, gray=True)
H, W = g.shape
f = max(1, int(round(0.25 / px)))
s = px * f
if f > 1:
    g = cv2.resize(g, (W // f, H // f), interpolation=cv2.INTER_AREA)
    H, W = g.shape
gb = cv2.GaussianBlur(g.astype(np.float32), (0, 0), 0.8)
Gx = cv2.Sobel(gb, cv2.CV_32F, 1, 0, ksize=3); Gy = cv2.Sobel(gb, cv2.CV_32F, 0, 1, ksize=3)
G = np.sqrt(Gx ** 2 + Gy ** 2)
G = np.minimum(G, np.percentile(G, 99.5))
G = cv2.GaussianBlur(G, (0, 0), 0.7)
bl = V["bldg"].copy()
bl["area"] = bl.geometry.area
bl = bl[(bl.area > 250) & (bl.area < 8000)]
rows = []
R = int(6.0 / s)  # ±6 m
for geom in bl.geometry:
    if geom.geom_type != "Polygon":
        continue
    mrr = geom.minimum_rotated_rectangle
    if geom.area / mrr.area < 0.85:
        continue
    minx, miny, maxx, maxy = geom.bounds
    # 영상 픽셀 창
    c0 = int((minx - ox) / s) - R - 3; c1 = int((maxx - ox) / s) + R + 3
    r0 = int((oy - maxy) / s) - R - 3; r1 = int((oy - miny) / s) + R + 3
    if c0 < 0 or r0 < 0 or c1 > W or r1 > H:
        continue
    ring = np.asarray(geom.exterior.coords)[:, :2]
    pts = np.stack([(ring[:, 0] - ox) / s - c0, (oy - ring[:, 1]) / s - r0], 1)
    mask = np.zeros((r1 - r0, c1 - c0), np.uint8)
    cv2.polylines(mask, [np.round(pts * 16).astype(np.int32)], True, 255, 1, cv2.LINE_AA, shift=4)
    ys, xs = np.nonzero(mask > 100)
    if len(ys) < 20:
        continue
    Gw = G[r0:r1, c0:c1]
    Gw = Gw / (G.mean())
    surf = np.zeros((2 * R + 1, 2 * R + 1), np.float32)
    for i, dy in enumerate(range(-R, R + 1)):
        for j, dx in enumerate(range(-R, R + 1)):
            yy = ys + dy; xx = xs + dx
            ok = (yy >= 0) & (yy < Gw.shape[0]) & (xx >= 0) & (xx < Gw.shape[1])
            surf[i, j] = Gw[yy[ok], xx[ok]].mean() if ok.sum() > 0.8 * len(ys) else 0
    i, j = np.unravel_index(np.argmax(surf), surf.shape)
    sharp = (surf[i, j] - np.median(surf)) / (surf.std() + 1e-6)
    cx = (minx + maxx) / 2; cy = (miny + maxy) / 2
    rows.append((cx, cy, (j - R) * s, (i - R) * s, sharp, surf[i, j], geom.area))
rows = np.array(rows)
print("n buildings", len(rows))
good = rows[(rows[:, 4] > 3.0) & (np.abs(rows[:, 2]) < 5.5) & (np.abs(rows[:, 3]) < 5.5)]
print("good", len(good))
print("median vector shift E", np.median(good[:, 2]), "S(rows)", np.median(good[:, 3]), "MAD", np.median(np.abs(good[:, 2] - np.median(good[:, 2]))), np.median(np.abs(good[:, 3] - np.median(good[:, 3]))))
np.save(SCR + f"{key}_bldgres.npy", rows)
# 영역별
for nm, cond in [("N", good[:, 1] > 360700), ("S", good[:, 1] <= 360700), ("W", good[:, 0] < 219200), ("E", good[:, 0] >= 219200)]:
    gg = good[cond]
    if len(gg) > 5:
        print(nm, len(gg), "medE", round(np.median(gg[:, 2]), 2), "medS", round(np.median(gg[:, 3]), 2))
# 선형 추세 (위치 의존: 회전/축척)
if len(good) > 20:
    A = np.c_[good[:, 0] - 219200, good[:, 1] - 360300, np.ones(len(good))]
    cx_, *_ = np.linalg.lstsq(A, good[:, 2], rcond=None)
    cy_, *_ = np.linalg.lstsq(A, good[:, 3], rcond=None)
    print("shiftE = %.2e*dx + %.2e*dy + %.2f" % tuple(cx_))
    print("shiftS = %.2e*dx + %.2e*dy + %.2f" % tuple(cy_))
