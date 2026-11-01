"""맥락 모형(반축척, 원좌표) ↔ 라이노 계획 좌표 변환. 구 역사 건물 외곽선 21점 대응으로 구한 닮음변환(오차 5e-10 m).
plan = s·R·ctx + t,  z_plan = 2·(z_ctx − Z0).  회전 −33.79°(시계방향), 축척 2.0."""
import json, os, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_d = json.load(open(os.path.join(HERE, "..", "data", "xf_ctx_to_plan.json")))
S = float(_d["s"]); R = np.array(_d["R"]); T = np.array(_d["t"]); Z0 = 256.4088604986632
Rinv = R.T
def ctx2plan(xy):
    xy = np.asarray(xy, float); return (S * (R @ xy.T)).T + T if xy.ndim == 2 else S * (R @ xy) + T
def plan2ctx(xy):
    xy = np.asarray(xy, float); return (Rinv @ ((xy - T).T / S)).T if xy.ndim == 2 else Rinv @ ((xy - T) / S)
def z_ctx2plan(z): return 2.0 * (np.asarray(z, float) - Z0)
if __name__ == "__main__":
    print("S", S, "theta", math.degrees(math.atan2(R[1, 0], R[0, 0])), "T", T)
    p = np.array([[1155150.0595, 1762346.0498499374]]); print(ctx2plan(p), plan2ctx(ctx2plan(p)))
