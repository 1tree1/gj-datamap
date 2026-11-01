# -*- coding: utf-8 -*-
"""4 모서리를 각각 확대(8x)해서 2x2 한 장으로: python hist_36_corner_zoom4.py KEY tlx tly trx try brx bry blx bly [half_w=80 half_h=55]"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
key = sys.argv[1]
v = [float(x) for x in sys.argv[2:10]]
hw = int(sys.argv[10]) if len(sys.argv) > 10 else 80
hh = int(sys.argv[11]) if len(sys.argv) > 11 else 55
sc = 6
a = load_full(key)
H, W = a.shape[:2]
def crop(cx, cy):
    cx, cy = int(cx), int(cy)
    xa, ya, xb, yb = max(0, cx - hw), max(0, cy - hh), min(W, cx + hw), min(H, cy + hh)
    sub = np.full((2 * hh, 2 * hw) + ((3,) if a.ndim == 3 else ()), 255, np.uint8)
    s = a[ya:yb, xa:xb]
    sub[(ya - (cy - hh)):(ya - (cy - hh)) + s.shape[0], (xa - (cx - hw)):(xa - (cx - hw)) + s.shape[1]] = s
    im = cv2.resize(sub, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    im = np.ascontiguousarray(im if im.ndim == 3 else np.stack([im] * 3, -1))
    for g in range(-hw, hw + 1, 20):
        u = int((g + hw) * sc); cv2.line(im, (u, 0), (u, im.shape[0]), (255, 0, 0), 1)
        cv2.putText(im, str(cx + g), (u + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1, cv2.LINE_AA)
    for g in range(-hh, hh + 1, 20):
        u = int((g + hh) * sc); cv2.line(im, (0, u), (im.shape[1], u), (255, 0, 0), 1)
        cv2.putText(im, str(cy + g), (2, u - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1, cv2.LINE_AA)
    return im
tl, tr, br, bl = crop(v[0], v[1]), crop(v[2], v[3]), crop(v[4], v[5]), crop(v[6], v[7])
m = np.concatenate([np.concatenate([tl, tr], 1), np.concatenate([bl, br], 1)], 0)
Image.fromarray(m).save(SCR + f"prev/z4_{key}.png")
print(m.shape)
