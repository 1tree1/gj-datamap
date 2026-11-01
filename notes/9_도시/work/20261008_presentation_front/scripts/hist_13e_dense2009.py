import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
vp = json.load(open(SCR + "valid_polys.json"))
key = "a2009"; f = 2
ref1, Hr1 = ref_ortho2025_gray(1.0)
a = load_full(key, gray=True)
H, info = load_transform(key)
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
mk = np.zeros(ds.shape, np.uint8)
cv2.fillPoly(mk, [np.round((np.array(vp[key]) - (f - 1) / 2.0) / f).astype(np.int32)], 255)
H_ds2geo = H @ prescale_matrix(f)
H2, res = refine_dense(ds, H_ds2geo, ref1, Hr1, iters=5, model="homography", T=224, stride=160, S=36, min_score=0.2, thr=3.0, mask_ds=mk, use_edges=False, blur=1.5)
print(res and {k: v for k, v in res.items() if k not in ("disp", "inl")})
Hfull = H2 @ np.linalg.inv(prescale_matrix(f))
px_eff = np.sqrt(abs(np.linalg.det(Hfull[:2, :2])))
rms_m = None
if res:
    rms_m = res["rms_px"] * 1.0  # ref 1 m/px
print("gsd", px_eff, "rms m", rms_m)
save_transform(key, Hfull, dict(kind="photo", source=SRC[key], model="coarse SIFT sim + dense tile NCC homography refinement to o2025", gsd_eff=px_eff, size_px=[a.shape[1], a.shape[0]], rms_m=rms_m, n_tiles=res and res["inliers"]))
print(check_overlay(key, ref1, Hr1, ds, H2, "chk_2009_b", crop=(700, 700, 1500, 1500), scale=0.6))
