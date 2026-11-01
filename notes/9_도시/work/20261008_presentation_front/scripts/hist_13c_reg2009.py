# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
vp = json.load(open(SCR + "valid_polys.json"))
key = "a2009"; gsd = 0.42
ref1, Hr1 = ref_ortho2025_gray(1.0)
# 1) 거친 유사변환: 3 m 격자
refres = 3.0
ref3 = cv2.resize(ref1, (int(ref1.shape[1] / 3), int(ref1.shape[0] / 3)), interpolation=cv2.INTER_AREA)
a = load_full(key, gray=True)
f = 7
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
mk = np.zeros(ds.shape, np.uint8)
cv2.fillPoly(mk, [np.round((np.array(vp[key]) - (f - 1) / 2.0) / f).astype(np.int32)], 255)
pa, pb = sift_match(ds, ref3, nfeat=20000, ratio=0.85, contrast=0.01, mask_a=mk)
H1, inl1 = ransac_model(pa, pb, "similarity", thr=4)
print("coarse inliers", int(inl1.sum()), "scale", np.sqrt(abs(np.linalg.det(H1[:2, :2]))), "rot", np.degrees(np.arctan2(H1[1, 0], H1[0, 0])))
# ref3 px -> ref1 px : p1 = 3*p3 + 1  (픽셀 중심 관례: (3-1)/2 = 1)
S3 = prescale_matrix(3)
Hds_to_ref1 = S3 @ H1
H_ds2geo = Hr1 @ Hds_to_ref1        # ds px -> geo
# 2) 반복 정밀화 (ds 해상도 f=2: 약 0.9 m/px 로 재구성)
f2 = 2
ds2 = cv2.resize(a, (a.shape[1] // f2, a.shape[0] // f2), interpolation=cv2.INTER_AREA)
mk2 = np.zeros(ds2.shape, np.uint8)
cv2.fillPoly(mk2, [np.round((np.array(vp[key]) - (f2 - 1) / 2.0) / f2).astype(np.int32)], 255)
# H: ds(f=7) px -> geo  ==> ds2(f=2) px -> geo : ds2 px -> full -> ds7 px
full_from_ds2 = prescale_matrix(f2)
ds7_from_full = np.linalg.inv(prescale_matrix(f))
Hds2_2geo = H_ds2geo @ ds7_from_full @ full_from_ds2
H, last = refine_register(ds2, Hds2_2geo, ref1, Hr1, iters=4, maxdisp_px=80, ratio=0.85, model="similarity", thr=4.0, mask_ds=mk2)
H, last = refine_register(ds2, H, ref1, Hr1, iters=4, maxdisp_px=40, ratio=0.85, model="homography", thr=3.0, mask_ds=mk2)
Hfull = H @ np.linalg.inv(full_from_ds2)
px_eff = np.sqrt(abs(np.linalg.det(Hfull[:2, :2])))
print("effective gsd", px_eff, "last", last)
save_transform(key, Hfull, dict(kind="photo", source=SRC[key], model="coarse sim + iterative SIFT homography to o2025", gsd_eff=px_eff, size_px=[a.shape[1], a.shape[0]]))
