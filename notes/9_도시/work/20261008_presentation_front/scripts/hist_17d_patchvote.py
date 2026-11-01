# -*- coding: utf-8 -*-
"""패치 투표 거친 정합.  python hist_17d_patchvote.py KEY F_DS REFNAME ref_res ds_gsd_lo ds_gsd_hi n_scales ang_lo ang_hi ang_step [patch] [stride]"""
import sys, time
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
key = sys.argv[1]; f = int(sys.argv[2]); refname = sys.argv[3]; rres = float(sys.argv[4])
g0, g1, ns = float(sys.argv[5]), float(sys.argv[6]), int(sys.argv[7])
a0, a1, as_ = float(sys.argv[8]), float(sys.argv[9]), float(sys.argv[10])
patch = int(sys.argv[11]) if len(sys.argv) > 11 else 112
stride = int(sys.argv[12]) if len(sys.argv) > 12 else 96
vp = json.load(open(SCR + "valid_polys.json")).get(key)
if refname == "o2025":
    ref0, Hr0 = ref_ortho2025_gray(1.0); rmask0 = np.ones(ref0.shape, np.uint8) * 255; res0 = 1.0
else:
    ref0 = np.load(SCR + f"ref_{refname}.npy"); rinfo = json.load(open(SCR + f"ref_{refname}.json"))
    rmask0 = np.load(SCR + f"refmask_{refname}.npy").astype(np.uint8) * 255; Hr0 = np.array(rinfo["H"]); res0 = rinfo["res"]
d = int(round(rres / res0))
ref = cv2.resize(ref0, (ref0.shape[1] // d, ref0.shape[0] // d), interpolation=cv2.INTER_AREA) if d > 1 else ref0
rmask = cv2.resize(rmask0, (ref.shape[1], ref.shape[0]), interpolation=cv2.INTER_NEAREST) if d > 1 else rmask0
rmask = cv2.erode(rmask, np.ones((9, 9), np.uint8))
Hg = Hr0 @ prescale_matrix(d) if d > 1 else Hr0
a = load_full(key, gray=True)
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
mk = None
if vp is not None:
    mk = np.zeros(ds.shape, np.uint8)
    cv2.fillPoly(mk, [np.round((np.array(vp) - (f - 1) / 2.0) / f).astype(np.int32)], 255)
    mk = cv2.erode(mk, np.ones((9, 9), np.uint8))
# 선택: 영역 제한 --rows=a,b --cols=a,b (비율)
for arg in sys.argv:
    if arg.startswith("--rows=") or arg.startswith("--cols="):
        lo, hi = [float(v) for v in arg.split("=")[1].split(",")]
        if mk is None:
            mk = np.ones(ds.shape, np.uint8) * 255
        if arg.startswith("--rows="):
            mk[:int(lo * ds.shape[0])] = 0; mk[int(hi * ds.shape[0]):] = 0
        else:
            mk[:, :int(lo * ds.shape[1])] = 0; mk[:, int(hi * ds.shape[1]):] = 0
print(key, "ds", ds.shape, "ref", ref.shape, "ref res", rres)
scales = np.linspace(g0, g1, ns) / rres     # ds 화소(m) -> ref 화소 배율
angles = np.arange(a0, a1 + 1e-9, as_)
t0 = time.time()
cands, npatch, c0 = patch_vote(ds, mk, ref, rmask, angles, scales, patch=patch, stride=stride)
print("time", time.time() - t0)
best = cands[0]
cnt, ssum, ang, s, tm, cs, ts, scs = best
th = np.radians(ang)
R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]) * s
Aref = np.vstack([np.hstack([R, (tm - R @ c0)[:, None]]), [0, 0, 1]])   # ds px -> ref px
H_ds2geo = Hg @ Aref
np.save(SCR + f"coarse_{key}.npy", H_ds2geo)
# 대응점 (ds px -> ref px) 저장
ref_pts = (R @ (cs - c0).T).T + tm
np.save(SCR + f"vote_{key}.npy", np.c_[cs, ref_pts])
print("best: count", cnt, "of", npatch, "angle", ang, "scale", s, "-> ds-px size (m)", s * rres, "GSD", s * rres / f)
