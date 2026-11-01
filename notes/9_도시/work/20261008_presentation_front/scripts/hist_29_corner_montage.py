# -*- coding: utf-8 -*-
"""도곽 모서리 4곳을 한 장으로: python hist_29_corner_montage.py KEY cx0 cy0 cx1 cy1 [half=260] [scale=2]
(cx0,cy0)=좌상 근사, (cx1,cy1)=우하 근사 (원본 픽셀)"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
key = sys.argv[1]
x0, y0, x1, y1 = [int(float(v)) for v in sys.argv[2:6]]
half = int(sys.argv[6]) if len(sys.argv) > 6 else 260
sc = float(sys.argv[7]) if len(sys.argv) > 7 else 2.0
a = load_full(key)
H, W = a.shape[:2]
def crop(cx, cy):
    xa, ya = max(0, cx - half), max(0, cy - half)
    xb, yb = min(W, cx + half), min(H, cy + half)
    sub = np.zeros((2 * half, 2 * half) + ((3,) if a.ndim == 3 else ()), np.uint8) + 255
    s = a[ya:yb, xa:xb]
    sub[(ya - (cy - half)):(ya - (cy - half)) + s.shape[0], (xa - (cx - half)):(xa - (cx - half)) + s.shape[1]] = s
    im = cv2.resize(sub, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    im = np.ascontiguousarray(im if im.ndim == 3 else np.stack([im] * 3, -1))
    # 십자 눈금(중심)과 100 px 격자
    for g in range(-half, half + 1, 100):
        u = int((g + half) * sc)
        cv2.line(im, (u, 0), (u, 8), (255, 0, 0), 1); cv2.line(im, (0, u), (8, u), (255, 0, 0), 1)
        cv2.putText(im, str(cx + g), (u + 2, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(im, str(cy + g), (10, u + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 0, 0), 1, cv2.LINE_AA)
    return im
tl, tr, br, bl = crop(x0, y0), crop(x1, y0), crop(x1, y1), crop(x0, y1)
m = np.concatenate([np.concatenate([tl, tr], 1), np.concatenate([bl, br], 1)], 0)
Image.fromarray(m).save(SCR + f"prev/corn_{key}.png")
print(m.shape)
