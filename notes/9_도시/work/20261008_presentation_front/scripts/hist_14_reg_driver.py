# -*- coding: utf-8 -*-
"""사진(항공) -> 참조 격자 정합: 거친 SIFT 유사변환 -> 조밀 타일 NCC 정밀화.
python hist_14_reg_driver.py KEY F_DS REF [coarse_res] [skip_dense]
REF: o2025 | 저장된 참조 이름
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

def coarse(key, a, f_ds, ref1, Hr1, valid=None, coarse_res=3.0, ratio=0.85, thr=4.0, nfeat=20000, contrast=0.01, verbose=True):
    f_ref = coarse_res
    refc = cv2.resize(ref1, (int(ref1.shape[1] / f_ref), int(ref1.shape[0] / f_ref)), interpolation=cv2.INTER_AREA)
    ds = cv2.resize(a, (a.shape[1] // f_ds, a.shape[0] // f_ds), interpolation=cv2.INTER_AREA)
    mk = None
    if valid is not None:
        mk = np.zeros(ds.shape, np.uint8)
        cv2.fillPoly(mk, [np.round((np.array(valid) - (f_ds - 1) / 2.0) / f_ds).astype(np.int32)], 255)
    pa, pb = sift_match(ds, refc, nfeat=nfeat, ratio=ratio, contrast=contrast, mask_a=mk, verbose=verbose)
    H1, inl = ransac_model(pa, pb, "similarity", thr=thr)
    if H1 is None:
        return None
    sc = np.sqrt(abs(np.linalg.det(H1[:2, :2]))); rot = np.degrees(np.arctan2(H1[1, 0], H1[0, 0]))
    if verbose:
        print(f"  coarse: inliers {int(inl.sum())}/{len(pa)} scale(ds->refc) {sc:.4f} rot {rot:.2f} deg -> ds px size {sc*f_ref:.3f} m ; GSD {sc*f_ref/f_ds:.4f} m")
    # refc px -> ref1 px
    S = prescale_matrix(int(round(f_ref))) if abs(f_ref - round(f_ref)) < 1e-6 else np.array([[f_ref, 0, (f_ref - 1) / 2], [0, f_ref, (f_ref - 1) / 2], [0, 0, 1]])
    H_ds2geo = Hr1 @ S @ H1
    return H_ds2geo, int(inl.sum()), len(pa), sc * f_ref / f_ds, ds, mk

def dense_stage(ds, H_ds2geo, ref1, Hr1, mk, stages=None, verbose=True):
    stages = stages or [dict(T=256, stride=192, S=60, min_score=0.2, thr=6.0, model="affine", iters=3, blur=2.0),
                        dict(T=224, stride=160, S=36, min_score=0.2, thr=3.0, model="homography", iters=4, blur=1.5)]
    H = H_ds2geo; res = None
    for st in stages:
        if verbose: print("  dense stage", st)
        H, r = refine_dense(ds, H, ref1, Hr1, iters=st["iters"], model=st["model"], T=st["T"], stride=st["stride"], S=st["S"], min_score=st["min_score"], thr=st["thr"], mask_ds=mk, blur=st["blur"], verbose=verbose)
        if r is not None:
            res = r
    return H, res

if __name__ == "__main__":
    key = sys.argv[1]; f_ds = int(sys.argv[2]); refname = sys.argv[3]
    coarse_res = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0
    vp = json.load(open(SCR + "valid_polys.json")).get(key)
    ref1, Hr1 = get_ref(refname)
    a = load_full(key, gray=True)
    out = coarse(key, a, f_ds, ref1, Hr1, valid=vp, coarse_res=coarse_res)
    if out is None:
        print("COARSE FAIL"); sys.exit(1)
    H_ds2geo, ninl, nmat, gsd, ds, mk = out
    np.save(SCR + f"coarse_{key}.npy", H_ds2geo)
    if "--coarse-only" in sys.argv:
        sys.exit(0)
    H2, res = dense_stage(ds, H_ds2geo, ref1, Hr1, mk)
    Hfull = H2 @ np.linalg.inv(prescale_matrix(f_ds))
    px_eff = np.sqrt(abs(np.linalg.det(Hfull[:2, :2])))
    rms = res["rms_px"] if res else None
    print("final gsd", px_eff, "rms (ref px)", rms, "tiles", res and res["inliers"])
    save_transform(key, Hfull, dict(kind="photo", source=SRC[key], model=f"coarse SIFT sim + dense tile NCC to {refname}", gsd_eff=px_eff, size_px=[a.shape[1], a.shape[0]], rms_m=rms, n_tiles=res and res["inliers"], coarse_inliers=ninl))
