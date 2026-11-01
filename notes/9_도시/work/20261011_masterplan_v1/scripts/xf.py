"""맥락(옛 반축척 좌표) ↔ 계획 좌표 변환 — 최종 정합(2026-10-11 재산정). P = 2·O + t (회전 0°), z' = 2(z − Z).
정합 근거: ① 계획 경계 U 는 옛 매입경계 v3 의 2배와 IoU 0.945 ② U 를 맥락에 얹었을 때 경계선이 건물 안을 지나는 길이가 최소(6 m, 중앙값 104 m) ③ 가르는 건물 2동(중앙값 47동).
이전 변환(구 역사 복사본 기준 −33.79° 회전)은 틀렸다 — 사용자가 구 역사 복사본만 따로 돌리고 옮겼다."""
import json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_d = json.load(open(os.path.join(HERE, "..", "data", "xf_final.json"), encoding="utf-8"))
S = float(_d["s"]); R = np.array(_d["R"]); T = np.array(_d["t"]); Z_SLAB = float(_d["Z_SLAB"]); Z_BLD = float(_d["Z_BLD"]); Z0 = Z_SLAB
def ctx2plan(xy):
    xy = np.asarray(xy, float); return (S * (R @ xy.T)).T + T if xy.ndim == 2 else S * (R @ xy) + T
def plan2ctx(xy):
    xy = np.asarray(xy, float); return (R.T @ ((xy - T).T / S)).T if xy.ndim == 2 else R.T @ ((xy - T) / S)
def z_slab(z): return 2.0 * (np.asarray(z, float) - Z_SLAB)
def z_bld(z): return 2.0 * (np.asarray(z, float) - Z_BLD)
