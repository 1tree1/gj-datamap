# -*- coding: utf-8 -*-
"""항공사진 -> 참조(5187 기준 gray 영상) SIFT 정합.
python hist_13_reg_photo.py KEY F REF [model] [ratio]
REF: o2025 (2025 정사영상 1 m/px) 또는 임의 저장된 참조 npy 이름(ref_<name>.npy + ref_<name>.json)
"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *

def get_ref(name):
    if name == "o2025":
        return ref_ortho2025_gray(1.0)
    g = np.load(SCR + f"ref_{name}.npy")
    d = json.load(open(SCR + f"ref_{name}.json"))
    return g, np.array(d["H"])

def run(key, f, refname, model="homography", ratio=0.8, thr_sim=6.0, thr_fin=3.5, valid=None, nfeat=40000, save=True, tag=None):
    ref, Hr = get_ref(refname)
    a = load_full(key, gray=True)
    ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
    mask = None
    vp = None
    if valid is not None:
        vp = np.array(valid)
        mk = np.zeros(ds.shape, np.uint8)
        cv2.fillPoly(mk, [np.round((vp - (f - 1) / 2.0) / f).astype(np.int32)], 255)
        mask = mk
    print(key, a.shape, "ds", ds.shape, "ref", ref.shape)
    pa, pb = sift_match(ds, ref, nfeat=nfeat, ratio=ratio, mask_a=mask)
    H1, inl1 = ransac_model(pa, pb, "similarity", thr=thr_sim)
    if H1 is None:
        print("  FAIL similarity"); return None
    print("  similarity inliers", int(inl1.sum()), "of", len(pa), "scale", np.sqrt(abs(np.linalg.det(H1[:2, :2]))), "rot", np.degrees(np.arctan2(H1[1, 0], H1[0, 0])))
    pa1, pb1 = pa[inl1], pb[inl1]
    H2, inl2 = ransac_model(pa1, pb1, model, thr=thr_fin)
    if H2 is None:
        print("  FAIL final model"); return None
    pa2, pb2 = pa1[inl2], pb1[inl2]
    print("  final", model, "inliers", int(inl2.sum()))
    # 변환 합성: ds px -> ref px -> geo ; full px -> ds px
    Hds2geo = Hr @ H2
    Hfull = Hds2geo @ np.linalg.inv(prescale_matrix(f))
    src_full = pa2 * f + (f - 1) / 2
    geo_ref = apply_H(Hr, pb2) + np.array([CX, CY])
    rms, r = residuals(Hfull, src_full, geo_ref)
    px_eff = np.sqrt(abs(np.linalg.det(Hfull[:2, :2])))
    print(f"  effective gsd {px_eff:.3f} m, RMS {rms:.2f} m, median {np.median(r):.2f}, n {len(r)}")
    if save:
        save_transform(tag or key, Hfull, dict(kind="photo", source=SRC[key], model=f"sim->{model} via SIFT to {refname}", n_inliers=int(inl2.sum()), n_matches=int(len(pa)), rms_m=rms,
                                               gsd_eff=px_eff, size_px=[a.shape[1], a.shape[0]], ds=f))
        np.save(SCR + f"gcp_{tag or key}.npy", np.c_[src_full, geo_ref])
    return Hfull, rms, len(r)

if __name__ == "__main__":
    key = sys.argv[1]; f = int(sys.argv[2]); ref = sys.argv[3]
    model = sys.argv[4] if len(sys.argv) > 4 else "homography"
    ratio = float(sys.argv[5]) if len(sys.argv) > 5 else 0.8
    vp = json.load(open(SCR + "valid_polys.json")).get(key)
    run(key, f, ref, model, ratio, valid=vp)
