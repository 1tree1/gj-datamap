# -*- coding: utf-8 -*-
"""원본 영상의 일부를 잘라 픽셀 격자와 함께 보기: python hist_27_crop_view.py KEY x0 y0 x1 y1 out_w OUT [grid_px]"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
key = sys.argv[1]
x0, y0, x1, y1 = [int(float(v)) for v in sys.argv[2:6]]
out_w = int(sys.argv[6]); out = sys.argv[7]
grid = int(sys.argv[8]) if len(sys.argv) > 8 else 0
a = load_full(key)
sub = a[y0:y1, x0:x1]
s = out_w / sub.shape[1]
im = cv2.resize(sub, (out_w, int(sub.shape[0] * s)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
im = np.ascontiguousarray(im if im.ndim == 3 else np.stack([im] * 3, -1))
if grid:
    for gx in range((x0 // grid + 1) * grid, x1, grid):
        u = int((gx - x0) * s)
        cv2.line(im, (u, 0), (u, im.shape[0]), (255, 0, 0), 1)
        cv2.putText(im, str(gx), (u + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1, cv2.LINE_AA)
    for gy in range((y0 // grid + 1) * grid, y1, grid):
        v = int((gy - y0) * s)
        cv2.line(im, (0, v), (im.shape[1], v), (255, 0, 0), 1)
        cv2.putText(im, str(gy), (2, v - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1, cv2.LINE_AA)
Image.fromarray(im).save(SCR + "prev/" + out)
print(im.shape, "scale", s)
