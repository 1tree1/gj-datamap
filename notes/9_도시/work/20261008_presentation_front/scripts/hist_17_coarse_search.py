# -*- coding: utf-8 -*-
"""거친 전역 탐색(회전·축척 격자 + NCC 평행이동)으로 옛 항공사진의 초기 변환 추정.
python hist_17_coarse_search.py KEY F_DS REFNAME ref_down gsd_lo gsd_hi gsd_step ang_lo ang_hi ang_step
"""
import sys, time
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
key = sys.argv[1]; f_ds = int(sys.argv[2]); refname = sys.argv[3]; ref_down = int(sys.argv[4])
g0, g1, gs = float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7])
a0, a1, as_ = float(sys.argv[8]), float(sys.argv[9]), float(sys.argv[10])
vp = json.load(open(SCR + "valid_polys.json")).get(key)
ref = np.load(SCR + f"ref_{refname}.npy"); rinfo = json.load(open(SCR + f"ref_{refname}.json"))
rmask = np.load(SCR + f"refmask_{refname}.npy")
res = rinfo["res"]; Hg = np.array(rinfo["H"])
if ref_down > 1:
    ref = cv2.resize(ref, (ref.shape[1] // ref_down, ref.shape[0] // ref_down), interpolation=cv2.INTER_AREA)
    rmask = cv2.resize(rmask.astype(np.uint8), (ref.shape[1], ref.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
    res = res * ref_down
    # 새 격자 H: 픽셀 -> geo (원 격자 중심 관례 보정)
    Hg = Hg @ prescale_matrix(ref_down)
a = load_full(key, gray=True)
ds = cv2.resize(a, (a.shape[1] // f_ds, a.shape[0] // f_ds), interpolation=cv2.INTER_AREA)
mk = None
if vp is not None:
    mk = np.zeros(ds.shape, np.uint8)
    cv2.fillPoly(mk, [np.round((np.array(vp) - (f_ds - 1) / 2.0) / f_ds).astype(np.int32)], 255)
print(key, "ds", ds.shape, "ref", ref.shape, "res", res)
gsds = np.arange(g0, g1 + 1e-9, gs)   # ds 화소 크기 후보(m)
angles = np.arange(a0, a1 + 1e-9, as_)
t0 = time.time()
cands = coarse_search(ds, None, mk, ref, rmask, res, Hg, angles, gsds, topk=8)
print("time", time.time() - t0)
best = cands[0]
np.save(SCR + f"coarse_{key}.npy", best[3])
json.dump([dict(score=c[0], angle=c[1], dspx=c[2], H=c[3].tolist()) for c in cands], open(SCR + f"coarse_cands_{key}.json", "w"))
print("best: score", best[0], "angle", best[1], "ds px (m)", best[2], "-> GSD", best[2] / f_ds)
