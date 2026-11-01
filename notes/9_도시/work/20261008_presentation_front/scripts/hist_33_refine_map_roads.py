# -*- coding: utf-8 -*-
"""종이지도 정밀화: 도곽 기반 초기 변환 -> (도로 중심선+철도) 밀도와 지도 잉크의 타일 NCC -> 아핀 보정
python hist_33_refine_map_roads.py KEY [res_m=2.0] [S0_m=120] [tag_out]"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from histvec import get, geom_lines, to_px
V = get()
key = sys.argv[1]
res = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
S0 = float(sys.argv[3]) if len(sys.argv) > 3 else 120.0
tag_out = sys.argv[4] if len(sys.argv) > 4 else key
x0g, y1g = 217000.0, 363500.0
wg, hg = int(5500 / res), int(6200 / res)
Hg = grid_H(x0g, y1g, res)
cache = SCR + f"vecref_roads_{res}.npy"
if os.path.exists(cache):
    vr = np.load(cache)
else:
    img = np.zeros((hg, wg), np.uint8)
    for ln in geom_lines(V["roadC"]):
        q = to_px(ln, x0g, y1g, res)
        cv2.polylines(img, [np.round(q * 16).astype(np.int32)], False, 200, 1, cv2.LINE_AA, shift=4)
    for ln in geom_lines(V["rail"]):
        q = to_px(ln, x0g, y1g, res)
        cv2.polylines(img, [np.round(q * 16).astype(np.int32)], False, 255, 2, cv2.LINE_AA, shift=4)
    vr = img
    np.save(cache, vr)
vdb = np.clip(cv2.GaussianBlur(vr.astype(np.float32), (0, 0), 6.0 / res), 0, 255).astype(np.uint8)
H0, info0 = load_transform(key)
a = load_full(key, gray=True)
gsd = float(np.sqrt(abs(np.linalg.det(H0[:2, :2]))))
f = max(1, int(round(res / gsd)))
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA) if f > 1 else a
ink = 255 - ds
Hds = H0 @ prescale_matrix(f)
mk = np.ones(ds.shape, np.uint8) * 255
fc = info0.get("corner_px")
if fc is not None:
    # 도곽 안쪽만 사용
    mk[:] = 0
    cp = (np.array(fc) - (f - 1) / 2.0) / f
    cv2.fillPoly(mk, [np.round(cp).astype(np.int32)], 255)
    mk = cv2.erode(mk, np.ones((5, 5), np.uint8))
print(key, "gsd", gsd, "f", f, "ds", ds.shape)
stages = [dict(T=int(500 / res), stride=int(380 / res), S=int(S0 * 1.6 / res), min_score=0.12, thr=18.0 / res, model="affine", iters=3, blur=4.0 / res),
          dict(T=int(420 / res), stride=int(300 / res), S=int(S0 / res), min_score=0.14, thr=10.0 / res, model="affine", iters=3, blur=3.0 / res),
          dict(T=int(360 / res), stride=int(260 / res), S=int(60 / res), min_score=0.16, thr=6.0 / res, model="affine", iters=3, blur=2.0 / res)]
H = Hds; last = None
for st in stages:
    print("  stage", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in st.items()})
    H, r = refine_dense(ink, H, vdb, Hg, iters=st["iters"], model=st["model"], T=st["T"], stride=st["stride"], S=st["S"], min_score=st["min_score"], thr=st["thr"], mask_ds=mk, blur=st["blur"], verbose=True, min_sharp=0.02)
    if r is not None:
        last = r
Hfull = H @ np.linalg.inv(prescale_matrix(f))
gsd2 = float(np.sqrt(abs(np.linalg.det(Hfull[:2, :2]))))
w, h = a.shape[1], a.shape[0]
pts = np.array([[w / 2, h / 2], [w * 0.3, h * 0.3], [w * 0.7, h * 0.3], [w * 0.3, h * 0.7], [w * 0.7, h * 0.7]], float)
d = apply_H(Hfull, pts) - apply_H(H0, pts)
print("shift (refined - neatline) at pts (m):", d.round(1).tolist())
print("gsd", gsd, "->", gsd2, " rms (m)", last and last["rms_px"] * res, " tiles", last and last["inliers"])
info = dict(info0)
info.update(model=info0.get("model", "") + " + dense NCC vs road/rail density", gsd_eff=gsd2, rms_neatline_m=info0.get("rms_m"), rms_m=(last["rms_px"] * res if last else None), n_tiles=(last["inliers"] if last else None), shift_vs_neatline_center_m=d[0].tolist())
save_transform(tag_out, Hfull, info)
