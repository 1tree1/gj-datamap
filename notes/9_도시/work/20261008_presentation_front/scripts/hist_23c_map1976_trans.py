# -*- coding: utf-8 -*-
"""1976 지도: 내장 지리참조 + 평행이동 보정(타일 변위 중앙값). 1984 보정과 비교."""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from histvec import get, geom_lines, to_px
V = get()
key = sys.argv[1] if len(sys.argv) > 1 else "m1976"
res = 1.0
x0g, y1g = 217300.0, 362400.0
wg, hg = 3300, 5000
Hg = grid_H(x0g, y1g, res)
img = np.zeros((hg, wg), np.uint8)
for geom in V["roadA"].geometry:
    gs = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    for p in gs:
        q = to_px(np.asarray(p.exterior.coords)[:, :2], x0g, y1g, res)
        cv2.fillPoly(img, [np.round(q).astype(np.int32)], 160)
for ln in geom_lines(V["bldg"]):
    q = to_px(ln, x0g, y1g, res)
    cv2.polylines(img, [np.round(q * 16).astype(np.int32)], True, 255, 1, cv2.LINE_AA, shift=4)
vdb = np.clip(cv2.GaussianBlur(img.astype(np.float32), (0, 0), 2.0), 0, 255).astype(np.uint8)
H0, err = embedded_map_H(key)
a = load_full(key, gray=True)
f = 2
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
ink = 255 - ds
h0, w0 = ds.shape
mk = np.zeros(ds.shape, np.uint8); mk[int(0.075 * h0):int(0.835 * h0), int(0.065 * w0):int(0.945 * w0)] = 255
H = H0 @ prescale_matrix(f)
Wm = warp_to_grid(ink, H, Hg, (wg, hg))
Mk = (warp_to_grid(mk, H, Hg, (wg, hg), interp=cv2.INTER_NEAREST) > 127).astype(np.float32)
for S, T, minsc in [(70, 300, 0.1), (30, 260, 0.12)]:
    d = tile_displacements(Wm, vdb, T=T, stride=220, S=S, min_score=minsc, mask=Mk, blur=2.0)
    print("S", S, "tiles", len(d))
    if len(d) == 0: break
    ds_ = d[d[:, 5] > 0.03] if (d[:, 5] > 0.03).sum() > 5 else d
    # 군집: 최빈 변위
    mx, my = np.median(ds_[:, 2]), np.median(ds_[:, 3])
    near = ds_[np.hypot(ds_[:, 2] - mx, ds_[:, 3] - my) < 6]
    print("   median shift px", mx, my, " n near", len(near), " near median", np.median(near[:, 2]), np.median(near[:, 3]), "std", near[:, 2].std(), near[:, 3].std())
    tx, ty = np.median(near[:, 2]), np.median(near[:, 3])
    # 적용: 격자 픽셀에서 ref 위치 = Wm 위치 + (tx,ty)  -> 변환 갱신
    Tm = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], float)
    H = Hg @ Tm @ np.linalg.inv(Hg) @ H
    Wm = warp_to_grid(ink, H, Hg, (wg, hg))
Hfull = H @ np.linalg.inv(prescale_matrix(f))
gsd = float(np.sqrt(abs(np.linalg.det(Hfull[:2, :2]))))
print("gsd", gsd)
save_transform(key, Hfull, dict(kind="map", source=SRC[key], model="embedded georef (EPSG:5176->5187) + translation correction (tile NCC median vs vector density)", gsd_eff=gsd, size_px=[a.shape[1], a.shape[0]], rms_m=None))
H1, _ = load_transform(key)
w, h = a.shape[1], a.shape[0]
d = apply_H(H1, [[w / 2, h / 2]]) - apply_H(embedded_map_H(key)[0], [[w / 2, h / 2]])
print("shift vs embedded at center", d)
