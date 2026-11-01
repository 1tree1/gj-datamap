# -*- coding: utf-8 -*-
"""항공사진 4장(1954·1968·1982·2009)의 유효 영역 다각형 계산 + 미리보기"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
res = {}
for key, ds, er in [("a1954", 8, 20), ("a1968", 8, 20), ("a1982", 6, 20), ("a2009", 6, 20)]:
    g = load_full(key, gray=True)
    gd = cv2.resize(g, (g.shape[1] // ds, g.shape[0] // ds), interpolation=cv2.INTER_AREA)
    m, poly = valid_polygon_photo(gd, ds, erode_px=er, thr=22)
    print(key, g.shape, "poly pts", None if poly is None else len(poly))
    res[key] = poly.tolist()
    vis = cv2.cvtColor(gd, cv2.COLOR_GRAY2BGR)
    pp = (poly / ds).astype(np.int32)
    cv2.polylines(vis, [pp], True, (0, 0, 255), 3)
    cv2.imwrite(SCR + f"prev/valid_{key}.png", vis)
json.dump(res, open(SCR + "valid_polys.json", "w"))
