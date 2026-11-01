# -*- coding: utf-8 -*-
"""1976/1984 1:5000 지도 정합: 내장 지리참조 초기값 -> 벡터 밀도(도로 면 + 건물 윤곽)와 잉크 밀도 타일 NCC 정밀화"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from histvec import get, geom_lines, to_px
V = get()
key = sys.argv[1]
res = 1.0
x0g, y1g = 217300.0, 362400.0
wg, hg = 3300, 5000
Hg = grid_H(x0g, y1g, res)
# 벡터 밀도
def vec_density():
    img = np.zeros((hg, wg), np.uint8)
    for geom in V["roadA"].geometry:
        gs = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        for p in gs:
            ext = np.asarray(p.exterior.coords)[:, :2]
            q = to_px(ext, x0g, y1g, res)
            cv2.fillPoly(img, [np.round(q).astype(np.int32)], 160)
    for ln in geom_lines(V["bldg"]):
        q = to_px(ln, x0g, y1g, res)
        cv2.polylines(img, [np.round(q * 16).astype(np.int32)], True, 255, 1, cv2.LINE_AA, shift=4)
    return img
vd = vec_density()
Image.fromarray(vd).save(SCR + "prev/vecdens.png")
vdb = cv2.GaussianBlur(vd.astype(np.float32), (0, 0), 2.0)
vdb = (np.clip(vdb, 0, 255)).astype(np.uint8)
# 지도
H0, err = embedded_map_H(key)
print("embedded affine approx err (m)", err)
a = load_full(key, gray=True)
f = 2
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
ink = 255 - ds
Hds = H0 @ prescale_matrix(f)
mk = np.ones(ds.shape, np.uint8) * 255
# 지도 내부(도곽 안)만 사용: 전체 영상에서 제목/범례 영역을 제외하기 위해 도곽 추정 (영상 크기 비율)
h0, w0 = ds.shape
mk[:] = 0
mk[int(0.075 * h0):int(0.835 * h0), int(0.065 * w0):int(0.945 * w0)] = 255
# 반복 정밀화
inkw = lambda H: warp_to_grid(ink, H, Hg, (wg, hg))
Hcur = Hds
for stage in [dict(T=300, stride=220, S=70, min_score=0.15, thr=8.0, model="affine", iters=3, blur=2.0),
              dict(T=260, stride=180, S=36, min_score=0.2, thr=4.0, model="affine", iters=3, blur=1.5),
              dict(T=240, stride=160, S=20, min_score=0.22, thr=2.5, model="affine", iters=3, blur=1.0)]:
    print("stage", stage)
    Hcur, r = refine_dense(ink, Hcur, vdb, Hg, iters=stage["iters"], model=stage["model"], T=stage["T"], stride=stage["stride"], S=stage["S"], min_score=stage["min_score"], thr=stage["thr"], mask_ds=mk, blur=stage["blur"], verbose=True)
Hfull = Hcur @ np.linalg.inv(prescale_matrix(f))
gsd = float(np.sqrt(abs(np.linalg.det(Hfull[:2, :2]))))
print("final gsd", gsd, "rms", r and r["rms_px"], "tiles", r and r["inliers"])
save_transform(key, Hfull, dict(kind="map", source=SRC[key], model="embedded georef (EPSG:5176->5187) + dense NCC vs vector density", gsd_eff=gsd, size_px=[a.shape[1], a.shape[0]], rms_m=r and r["rms_px"] * res, n_tiles=r and r["inliers"]))
