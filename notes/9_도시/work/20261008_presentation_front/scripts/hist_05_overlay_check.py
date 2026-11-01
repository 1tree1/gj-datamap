# -*- coding: utf-8 -*-
"""2025 정사영상 + 벡터 겹침 확인 (임시 정합값 사용)"""
import sys, json
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from histvec import *
import cv2
V = get()
init = json.load(open(SCR + "o2025_init.json"))
ox, oy = init["top_left_x"], init["top_left_y"]
a = load_full("o2025")
H, W = a.shape[:2]
px = 0.25
print("ortho", W, H)

def crop_overlay(cx, cy, size_m, out_px, name, extra=None):
    x0, x1 = cx - size_m / 2, cx + size_m / 2
    y0, y1 = cy - size_m / 2, cy + size_m / 2
    s = size_m / out_px
    # 소스 픽셀 윈도
    c0 = int((x0 - ox) / px); c1 = int((x1 - ox) / px)
    r0 = int((oy - y1) / px); r1 = int((oy - y0) / px)
    sub = a[max(r0, 0):r1, max(c0, 0):c1]
    canvas = np.zeros((r1 - r0, c1 - c0, 3), np.uint8)
    canvas[max(0, -r0):max(0, -r0) + sub.shape[0], max(0, -c0):max(0, -c0) + sub.shape[1]] = sub
    img = cv2.resize(canvas, (out_px, out_px), interpolation=cv2.INTER_AREA)
    img = np.ascontiguousarray(img[..., ::-1])  # BGR
    for key, col in [("bldg", (255, 255, 0)), ("roadA", (0, 200, 255)), ("rail", (255, 0, 255))]:
        for ln in geom_lines(V[key]):
            p = to_px(ln, x0, y1, s)
            if p[:, 0].max() < 0 or p[:, 0].min() > out_px or p[:, 1].max() < 0 or p[:, 1].min() > out_px:
                continue
            cv2.polylines(img, [np.round(p * 16).astype(np.int32)], False, col, 1, cv2.LINE_AA, shift=4)
    # 격자 100 m
    for gx_ in range(int(np.ceil(x0 / 100) * 100), int(x1) + 1, 100):
        u = int((gx_ - x0) / s)
        cv2.line(img, (u, 0), (u, 12), (0, 0, 255), 1)
        cv2.putText(img, str(gx_ % 10000), (u + 2, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)
    for gy_ in range(int(np.ceil(y0 / 100) * 100), int(y1) + 1, 100):
        v = int((y1 - gy_) / s)
        cv2.line(img, (0, v), (12, v), (0, 0, 255), 1)
        cv2.putText(img, str(gy_ % 10000), (14, v + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.imwrite(SCR + f"prev/chk_{name}.png", img)
    print("saved", name)

crop_overlay(219780, 360850, 500, 1100, "o25_center")
crop_overlay(218600, 359800, 500, 1100, "o25_sw")
crop_overlay(220000, 361200, 500, 1100, "o25_ne")
