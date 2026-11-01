# -*- coding: utf-8 -*-
"""도곽 정밀 추정: auto content frame -> fit_side -> 4 모서리 (원본 픽셀)  저장 (scratch json)"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
out = {}
for key in sys.argv[1:]:
    g = load_full(key, gray=True)
    x0, y0, x1, y1 = auto_content_frame(g)
    approx = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    # 모서리는 안쪽 얇은 선 -> mode line, win 넉넉히
    for win in (30,):
        c, info = frame_corners(g, approx, win=win, mode="line")
    print(key, "approx", (x0, y0, x1, y1))
    print("   refined corners TL,TR,BR,BL:", c.round(1).tolist())
    print("   side fit rms/n:", {k: (round(v[0], 2), v[1]) for k, v in info.items()})
    out[key] = c.tolist()
json.dump(out, open(SCR + "frames_" + "_".join(sys.argv[1:]) + ".json", "w"))
