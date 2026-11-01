# -*- coding: utf-8 -*-
"""2021·2015 정사영상 -> 2025 정사영상에 SIFT 정합 (유사변환), 변환 저장"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
ref, Hr = ref_ortho2025_gray(1.0)       # 1 m/px
print("ref", ref.shape)
for key, gsd_guess in [("o2021", 0.25), ("o2015", 0.5)]:
    a = load_full(key, gray=True)
    f = int(round(1.0 / gsd_guess))
    ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
    print(key, a.shape, "ds", ds.shape)
    pa, pb = sift_match(ds, ref, nfeat=40000, ratio=0.8)
    H, inl = ransac_model(pa, pb, "similarity", thr=3.0)
    print("  inliers", int(inl.sum()), "of", len(pa))
    if H is None:
        print("  FAIL"); continue
    sc = np.sqrt(abs(np.linalg.det(H[:2, :2])))
    rot = np.degrees(np.arctan2(H[1, 0], H[0, 0]))
    print("  scale (ds px -> ref px)", sc, "rot deg", rot)
    # affine refine on inliers
    H2, inl2 = ransac_model(pa[inl], pb[inl], "affine", thr=2.0)
    print("  affine inliers", int(inl2.sum()), "sing", np.linalg.svd(H2[:2, :2])[1])
    # src(ds px)->ref(px)->geo
    Hs = Hr @ H2 @ prescale_matrix(1)  # ds 좌표계 -> geo
    # ds px -> full px : full = f*ds + (f-1)/2
    Hfull = Hs @ np.linalg.inv(prescale_matrix(f))
    # 잔차: 대응점 inlier들의 geo 좌표
    src_full = (pa[inl][inl2]) * f + (f - 1) / 2
    geo_ref = apply_H(Hr, pb[inl][inl2]) + np.array([CX, CY])
    rms, r = residuals(Hfull, src_full, geo_ref)
    px_eff = np.sqrt(abs(np.linalg.det(Hfull[:2, :2])))
    print("  effective px (m):", px_eff, " RMS vs ref feats (m):", rms, " n:", len(r))
    # 좌상단 모서리 5187
    tl = apply_H(Hfull, [[-0.5, -0.5]])[0] + np.array([CX, CY])
    print("  top-left corner 5187", tl)
    save_transform(key, Hfull, dict(kind="ortho", source=SRC[key], model="similarity->affine via SIFT to o2025", n_inliers=int(inl2.sum()), rms_m=rms,
                                      px_eff=px_eff, rot_deg=float(rot), size_px=[a.shape[1], a.shape[0]]))
