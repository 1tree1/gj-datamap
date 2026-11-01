# 2025 항공사진(10 cm) 3장 + 2025 정사영상(25 cm)을 모델 좌표(1:1500 mm, 정북) 격자로 모자이크한다.
# 정합: work/20261008_presentation_front/research/hist_transforms/*.json (원본 화소 → EPSG:5187 상대좌표)
# 출력: <scratch>/mosaic/mosaic_015.jpg + mosaic_015.json (격자 정의)
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import tifffile
from pyproj import Transformer

sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).resolve().parents[1]
TR = W.parents[0] / "20261008_presentation_front" / "research" / "hist_transforms"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

RES_M = 0.15                       # 실제 0.15 m / 화소
RES = RES_M * 1000.0 / 1500.0      # 모델 mm / 화소 = 0.1
SOURCES = ["a2025_62", "a2025_64", "a2025_65", "o2025"]   # 정사영상 우선, 없는 곳만 항공사진(천저 거리로 선택)

fr = json.load(open(W / "data" / "model_bnd_frame.json"))["frame"]
X0, X1 = min(p[0] for p in fr), max(p[0] for p in fr)
Y0, Y1 = min(p[1] for p in fr), max(p[1] for p in fr)
NW, NH = int(round((X1 - X0) / RES)), int(round((Y1 - Y0) / RES))
xf = json.load(open(W / "data" / "xf_5179.json"))
s, R, t = xf["s"], np.array(xf["R"]), np.array(xf["t"])
T = Transformer.from_crs(5179, 5187, always_xy=True)


def out2geo(u, v):
    """출력 화소 → EPSG:5187"""
    mx = X0 + (np.asarray(u) + 0.5) * RES
    my = Y1 - (np.asarray(v) + 0.5) * RES
    m = np.stack([mx, my], -1) - t
    x5179 = (R.T @ m.T).T / s
    return np.array(T.transform(x5179[:, 0], x5179[:, 1])).T


def load_tr(k):
    raw = (TR / f"{k}.json").read_bytes()
    try:
        d = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        d = json.loads(raw.decode("cp949"))
    return d


src = {}
gu, gv = np.meshgrid(np.linspace(0, NW, 21), np.linspace(0, NH, 27))
gu, gv = gu.ravel(), gv.ravel()
geo = out2geo(gu, gv)
for k in SOURCES:
    d = load_tr(k)
    H = np.array(d["H_src2geo_rel"]); cx, cy = d["origin"]
    Hi = np.linalg.inv(H)
    g = np.c_[geo[:, 0] - cx, geo[:, 1] - cy, np.ones(len(geo))]
    p = (Hi @ g.T).T; col, row = p[:, 0] / p[:, 2], p[:, 1] / p[:, 2]
    M, _ = cv2.findHomography(np.c_[gu, gv].astype(np.float64), np.c_[col, row].astype(np.float64), 0)
    w, h = d["size_px"]
    # 원본 중심(천저 근사)의 출력 화소 좌표
    Mi = np.linalg.inv(M); c = Mi @ np.array([w / 2, h / 2, 1.0]); c = c[:2] / c[2]
    arr = tifffile.memmap(d["source"])
    src[k] = {"M": M, "arr": arr, "w": w, "h": h, "center": c, "gsd": d.get("gsd_eff", d.get("px_m"))}
    print(k, "gsd", src[k]["gsd"], "center(out px)", np.round(c))

mosaic = np.zeros((NH, NW, 3), np.uint8)
srcmap = np.full((NH, NW), 255, np.uint8)
TILE = 1024
for ty in range(0, NH, TILE):
    for tx in range(0, NW, TILE):
        tw, th = min(TILE, NW - tx), min(TILE, NH - ty)
        best = np.full((th, tw), np.inf, np.float32)
        acc = np.zeros((th, tw, 3), np.uint8)
        idx = np.full((th, tw), 255, np.uint8)
        vv, uu = np.mgrid[ty:ty + th, tx:tx + tw]
        for i, k in enumerate(SOURCES):
            S = src[k]
            corners = np.array([[tx, ty, 1], [tx + tw, ty, 1], [tx + tw, ty + th, 1], [tx, ty + th, 1]], float).T
            q = S["M"] @ corners; q = q[:2] / q[2]
            c0, c1 = int(np.floor(q[0].min())) - 4, int(np.ceil(q[0].max())) + 4
            r0, r1 = int(np.floor(q[1].min())) - 4, int(np.ceil(q[1].max())) + 4
            if c1 < 0 or r1 < 0 or c0 >= S["w"] or r0 >= S["h"]:
                continue
            c0c, r0c = max(c0, 0), max(r0, 0)
            c1c, r1c = min(c1, S["w"]), min(r1, S["h"])
            sub = np.ascontiguousarray(S["arr"][r0c:r1c, c0c:c1c])
            # 출력 타일 화소 → 부분 원본 화소
            Tt = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], float)
            Ts = np.array([[1, 0, -c0c], [0, 1, -r0c], [0, 0, 1]], float)
            Mt = Ts @ S["M"] @ Tt
            img = cv2.warpPerspective(sub, Mt, (tw, th), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                                      borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            msk = cv2.warpPerspective(np.full(sub.shape[:2], 255, np.uint8), Mt, (tw, th),
                                      flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP, borderValue=0)
            msk = cv2.erode(msk, np.ones((5, 5), np.uint8)) > 0
            dist = np.hypot(uu - S["center"][0], vv - S["center"][1]).astype(np.float32)
            if k != "o2025":
                dist += 1e6          # 항공사진은 정사영상이 없을 때만(호모그래피 정합이라 가장자리 오차가 크다)
            take = msk & (dist < best)
            acc[take] = img[take]; best[take] = dist[take]; idx[take] = i
        mosaic[ty:ty + th, tx:tx + tw] = acc
        srcmap[ty:ty + th, tx:tx + tw] = idx
    print("row", ty, "/", NH)
cv2.imwrite(str(OUT / "mosaic_015.jpg"), cv2.cvtColor(mosaic, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 93])
cv2.imwrite(str(OUT / "mosaic_015_src.png"), srcmap)
json.dump({"x0": X0, "y1": Y1, "res_mm": RES, "res_m": RES_M, "w": NW, "h": NH, "sources": SOURCES},
          open(OUT / "mosaic_015.json", "w"))
cov = (srcmap != 255).mean()
print("mosaic", NW, NH, "coverage %.1f%%" % (100 * cov), {k: round(float((srcmap == i).mean() * 100), 1) for i, k in enumerate(SOURCES)})
