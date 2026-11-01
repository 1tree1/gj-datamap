# -*- coding: utf-8 -*-
"""사진 vs 참조(다른 사진을 5187 격자에 렌더링) SIFT 거친 정합 시도
python hist_17c_sift_photo2photo.py KEY F_DS REFNAME ref_res_m [ratio] [thr]
"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
key = sys.argv[1]; f = int(sys.argv[2]); refname = sys.argv[3]; rres = float(sys.argv[4])
ratio = float(sys.argv[5]) if len(sys.argv) > 5 else 0.85
thr = float(sys.argv[6]) if len(sys.argv) > 6 else 5.0
vp = json.load(open(SCR + "valid_polys.json")).get(key)
ref = np.load(SCR + f"ref_{refname}.npy"); rinfo = json.load(open(SCR + f"ref_{refname}.json"))
rmask = np.load(SCR + f"refmask_{refname}.npy")
Hg = np.array(rinfo["H"]); res0 = rinfo["res"]
d = int(round(rres / res0))
if d > 1:
    ref = cv2.resize(ref, (ref.shape[1] // d, ref.shape[0] // d), interpolation=cv2.INTER_AREA)
    rmask = cv2.resize(rmask.astype(np.uint8), (ref.shape[1], ref.shape[0]), interpolation=cv2.INTER_NEAREST)
    Hg = Hg @ prescale_matrix(d)
rmask = cv2.erode((rmask > 0).astype(np.uint8), np.ones((15, 15), np.uint8)) * 255
a = load_full(key, gray=True)
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
mk = None
if vp is not None:
    mk = np.zeros(ds.shape, np.uint8)
    cv2.fillPoly(mk, [np.round((np.array(vp) - (f - 1) / 2.0) / f).astype(np.int32)], 255)
    mk = cv2.erode(mk, np.ones((9, 9), np.uint8))
print(key, ds.shape, ref.shape)
best = None
for contrast in [0.01, 0.005]:
    pa, pb = sift_match(ds, ref, nfeat=30000, ratio=ratio, contrast=contrast, mask_a=mk, mask_b=rmask)
    for model in ["similarity"]:
        H1, inl = ransac_model(pa, pb, model, thr=thr)
        if H1 is None:
            print("   none"); continue
        sc = np.sqrt(abs(np.linalg.det(H1[:2, :2]))); rot = np.degrees(np.arctan2(H1[1, 0], H1[0, 0]))
        print(f"   contrast {contrast}: inliers {int(inl.sum())}/{len(pa)} scale {sc:.4f} rot {rot:.2f}  -> ds px {sc*rres:.2f} m")
        if best is None or inl.sum() > best[0]:
            best = (int(inl.sum()), H1, pa[inl], pb[inl])
if best:
    np.save(SCR + f"sift_{key}_{refname}.npy", np.c_[best[2], best[3]])
    np.save(SCR + f"siftH_{key}_{refname}.npy", best[1])
    H_ds2geo = Hg @ best[1]
    np.save(SCR + f"coarse_{key}.npy", H_ds2geo)
