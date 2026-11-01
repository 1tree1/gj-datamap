# -*- coding: utf-8 -*-
"""2025 정사영상: 변환 저장 + F1/F2 크롭 + outline"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *

OX, OY, PX = 217997.8, 361492.5, 0.25
H = ortho_H(OX, OY, PX)
save_transform("o2025", H, dict(kind="ortho", source=SRC["o2025"], model="translation+scale (north-up)", px_m=PX,
    top_left_5187=[OX, OY], size_px=[9696, 11700],
    note="건물 윤곽(연속수치지도 2025) 상관 + 개별 건물 국소정합 중앙값 보정. 잔차 MAD 약 2.6 m(건물 기울기 포함), 편향 <0.5 m"))

a = load_full("o2025")
res = {}
for fr in ["F1", "F2"]:
    p = pick_prescale(PX, fr)
    src = prescale(a, p)
    out, mask = warp_to_frame(src, H, fr, PX, prescaled=p)
    cov = float(mask.mean())
    res[fr] = cov
    out2 = fill_nodata(out, mask)
    save_jpg(HIST + f"ortho_2025_{fr}.jpg", out2)
    save_jpg(HIST + f"ortho_2025_{fr}_outline.jpg", draw_outline(out2, fr))
    print(fr, out2.shape, "prescale", p, "coverage", round(cov, 3))
json.dump(res, open(SCR + "cov_o2025.json", "w"))
