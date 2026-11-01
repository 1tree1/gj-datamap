# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
vp = json.load(open(SCR + "valid_polys.json"))
key = sys.argv[1]; gsd = float(sys.argv[2]); refres = float(sys.argv[3]); ratio = float(sys.argv[4])
ref1, Hr1 = ref_ortho2025_gray(1.0)
f_ref = refres / 1.0
ref = cv2.resize(ref1, (int(ref1.shape[1] / f_ref), int(ref1.shape[0] / f_ref)), interpolation=cv2.INTER_AREA)
a = load_full(key, gray=True)
f = max(1, int(round(refres / gsd)))
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
mk = None
if key in vp:
    mk = np.zeros(ds.shape, np.uint8)
    cv2.fillPoly(mk, [np.round((np.array(vp[key]) - (f - 1) / 2.0) / f).astype(np.int32)], 255)
print(key, "ds", ds.shape, "f", f, "ref", ref.shape)
for clip in [True]:
    pa, pb = sift_match(ds, ref, nfeat=20000, ratio=ratio, contrast=0.01, mask_a=mk)
    for thr in [4, 8]:
        H1, inl1 = ransac_model(pa, pb, "similarity", thr=thr)
        if H1 is None:
            print("  none"); continue
        sc = np.sqrt(abs(np.linalg.det(H1[:2, :2]))); rot = np.degrees(np.arctan2(H1[1, 0], H1[0, 0]))
        print(f"  thr {thr}: similarity inliers {int(inl1.sum())}/{len(pa)} scale {sc:.4f} (expected ~{gsd*f/refres:.3f}) rot {rot:.2f}")
