# 노면표시 검출·작도 결과를 항공사진 모자이크에 겹쳐 확인(qa_*.jpg)
import json
import sys

import cv2
import numpy as np

from c0_common import D, MM, W, Mosaic, imwrite

mos = Mosaic()
mk = json.load(open(D / "markings.json", encoding="utf-8"))
rg = json.load(open(D / "road_graph.json", encoding="utf-8"))
SPOTS = {
    "a_wonhwaro": (1157362, 1762245),
    "b_station_jct": (1157370, 1762330),
    "c_hwangchon": (1157560, 1762095),
    "d_north": (1157430, 1762800),
    "e_west": (1157200, 1762420),
    "f_south": (1157420, 1762060),
}
if len(sys.argv) > 1:
    SPOTS = {k: v for k, v in SPOTS.items() if k in sys.argv[1:]}


def crop(name, cx, cy, half=75, graph=False):
    hm = half * MM
    u0, v0 = mos.to_px([[cx - hm, cy + hm]])[0]; u1, v1 = mos.to_px([[cx + hm, cy - hm]])[0]
    u0, v0, u1, v1 = int(u0), int(v0), int(u1), int(v1)
    img = mos.rgb[v0:v1, u0:u1].copy()
    img = (img * 0.75).astype(np.uint8)

    def pl(pts, col, th=1, closed=False):
        p = np.round(mos.to_px(np.array(pts)) - [u0, v0]).astype(np.int32)
        cv2.polylines(img, [p], closed, col, th, cv2.LINE_AA)
    if graph:
        for L in rg["major"]:
            pl(L["pts"], (0, 160, 255) if L["has_cl"] else (120, 120, 255), 1)
    for c in mk["center_lines"]:
        pl(c["pts"], (255, 220, 0), 2)
    for l in mk["lane_lines"]:
        pl(l["pts"], (255, 255, 255), 1)
    for cw in mk["crosswalks"]:
        pl(cw["outline"], (255, 60, 60), 1, True)
        for s in cw["stripes"]:
            pl(s, (255, 120, 120), 1, True)
    for s in mk["stop_lines"]:
        pl(s, (60, 255, 60), 1, True)
    for a in mk["arrows"]:
        pl(a["pts"], (60, 255, 255), 1, True)
    for i in mk["islands"]:
        pl(i["outline"], (255, 0, 255), 1, True)
        for h in i["hatch"]:
            pl(h, (255, 0, 255), 1)
    imwrite(W / f"qa_{name}.jpg", img)
    cv2.putText(img, name, (10, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 0), 2)
    return img


tiles = []
for k, (x, y) in SPOTS.items():
    tiles.append(crop(k, x, y, graph=True))
if len(tiles) >= 4:
    t = [cv2.resize(x, (500, 500)) for x in tiles[:4]]
    imwrite(W / "qa_grid.jpg", np.vstack([np.hstack(t[:2]), np.hstack(t[2:4])]))
