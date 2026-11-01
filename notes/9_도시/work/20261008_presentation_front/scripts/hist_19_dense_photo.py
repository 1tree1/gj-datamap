# -*- coding: utf-8 -*-
"""거친 변환(coarse_KEY.npy; ds 배율 F0 기준) -> 조밀 타일 NCC 정밀화 -> 변환 저장
python hist_19_dense_photo.py KEY F0 REFNAME [F_DENSE=4] [save_name]"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
key = sys.argv[1]; f0 = int(sys.argv[2]); refname = sys.argv[3]
fd = int(sys.argv[4]) if len(sys.argv) > 4 else 4
vp = json.load(open(SCR + "valid_polys.json")).get(key)
if refname == "o2025":
    ref, Hr = ref_ortho2025_gray(1.0); refm = None
else:
    ref = np.load(SCR + f"ref_{refname}.npy"); rinfo = json.load(open(SCR + f"ref_{refname}.json")); Hr = np.array(rinfo["H"])
H0 = np.load(SCR + f"coarse_{key}.npy")          # ds(f0) px -> geo
Hfull = H0 @ np.linalg.inv(prescale_matrix(f0))
a = load_full(key, gray=True)
ds = cv2.resize(a, (a.shape[1] // fd, a.shape[0] // fd), interpolation=cv2.INTER_AREA)
mk = None
if vp is not None:
    mk = np.zeros(ds.shape, np.uint8)
    cv2.fillPoly(mk, [np.round((np.array(vp) - (fd - 1) / 2.0) / fd).astype(np.int32)], 255)
Hds = Hfull @ prescale_matrix(fd)
res_m = float(Hr[0, 0])
print(key, "ds", ds.shape, "ref", ref.shape, "ref res", res_m, "gsd", float(np.sqrt(abs(np.linalg.det(Hfull[:2, :2])))))
stages = [dict(T=int(360 / res_m), stride=int(260 / res_m), S=int(160 / res_m), min_score=0.18, thr=6.0 / res_m, model="affine", iters=3, blur=2.0 / res_m),
          dict(T=int(300 / res_m), stride=int(220 / res_m), S=int(90 / res_m), min_score=0.2, thr=4.0 / res_m, model="affine", iters=3, blur=1.5 / res_m),
          dict(T=int(260 / res_m), stride=int(180 / res_m), S=int(50 / res_m), min_score=0.22, thr=3.0 / res_m, model="homography", iters=4, blur=1.2 / res_m)]
H = Hds; res = None
for st in stages:
    print("  stage", st)
    H, r = refine_dense(ds, H, ref, Hr, iters=st["iters"], model=st["model"], T=st["T"], stride=st["stride"], S=st["S"], min_score=st["min_score"], thr=st["thr"], mask_ds=mk, blur=st["blur"], verbose=True)
    if r is not None:
        res = r
Hfull2 = H @ np.linalg.inv(prescale_matrix(fd))
px_eff = float(np.sqrt(abs(np.linalg.det(Hfull2[:2, :2]))))
rms_m = res["rms_px"] * res_m if res else None
print("final gsd", px_eff, "rms (m)", rms_m, "tiles", res and res["inliers"])
name = sys.argv[5] if len(sys.argv) > 5 else key
save_transform(name, Hfull2, dict(kind="photo", source=SRC[key], model=f"patch-vote coarse + dense tile NCC to {refname}", gsd_eff=px_eff, size_px=[a.shape[1], a.shape[0]], rms_m=rms_m, n_tiles=res and res["inliers"]))
if res is not None:
    np.save(SCR + f"tiles_{name}.npy", res["disp"][res["inl"]])
