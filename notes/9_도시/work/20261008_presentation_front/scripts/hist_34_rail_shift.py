# -*- coding: utf-8 -*-
"""철도 선형 기반 위치 점검: 저장 변환으로 지도를 1 m 격자에 렌더링 -> 철도(+선택: 주요 도로) 벡터를 (dx,dy) 평행이동시키며
검은 선 마스크 평균을 구해 최적 평행이동과 첨예도를 보고한다.
python hist_34_rail_shift.py KEY [layers rail|road|both] [thr] [R=40]"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from histvec import get, geom_lines
V = get()

def densify(lines, step=4.0):
    pts = []
    for ln in lines:
        d = np.hypot(*np.diff(ln, axis=0).T)
        s = np.r_[0, np.cumsum(d)]
        if s[-1] < 1:
            continue
        t = np.arange(0, s[-1], step)
        pts.append(np.c_[np.interp(t, s, ln[:, 0]), np.interp(t, s, ln[:, 1])])
    return np.vstack(pts)

def rail_shift(key, layers="rail", thr=100, R=40, region=(219300, 359300, 221200, 362700), res=1.0, color=True, verbose=True, inkmode="black"):
    H, info = load_transform(key)
    gsd = float(np.sqrt(abs(np.linalg.det(H[:2, :2]))))
    a = load_full(key, gray=not color)
    x0, y0, x1, y1 = region
    f = max(1, int(np.floor(res / gsd * 0.999)))
    src = prescale(a, f) if f > 1 else a
    w = int((x1 - x0) / res); h = int((y1 - y0) / res)
    out = warp_to_grid(src, H @ prescale_matrix(f), grid_H(x0, y1, res), (w, h), interp=cv2.INTER_LINEAR)
    if out.ndim == 3:
        dark = (out.max(-1) < thr).astype(np.float32)
    else:
        dark = (out < thr).astype(np.float32)
    dark = cv2.GaussianBlur(dark, (0, 0), 1.5 / res)
    lines = []
    if layers in ("rail", "both"):
        lines += geom_lines(V["rail"])
    if layers in ("road", "both"):
        lines += geom_lines(V["roadC"])
    P = densify(lines, 4.0)
    P = P[(P[:, 0] > x0 + R + 5) & (P[:, 0] < x1 - R - 5) & (P[:, 1] > y0 + R + 5) & (P[:, 1] < y1 - R - 5)]
    u = (P[:, 0] - x0) / res; v = (y1 - P[:, 1]) / res
    Rpx = int(R / res)
    surf = np.zeros((2 * Rpx + 1, 2 * Rpx + 1), np.float32)
    for i, dy in enumerate(range(-Rpx, Rpx + 1)):
        for j, dx in enumerate(range(-Rpx, Rpx + 1)):
            uu = np.clip(np.round(u + dx).astype(int), 0, w - 1); vv = np.clip(np.round(v + dy).astype(int), 0, h - 1)
            surf[i, j] = dark[vv, uu].mean()
    i, j = np.unravel_index(np.argmax(surf), surf.shape)
    # 서브픽셀
    def para(p0, p1, p2):
        d = p0 - 2 * p1 + p2
        return 0.0 if d == 0 else 0.5 * (p0 - p2) / d
    di = para(surf[i - 1, j], surf[i, j], surf[i + 1, j]) if 0 < i < surf.shape[0] - 1 else 0
    dj = para(surf[i, j - 1], surf[i, j], surf[i, j + 1]) if 0 < j < surf.shape[1] - 1 else 0
    # 영상에서 벡터 위치를 (dx,dy) 만큼 옮겨야 선과 맞음 (dx: 동, dy: 영상 아래=남) -> 영상(지도)을 벡터에 맞추려면 지도를 (-dx 동, +dy 북 ... ) 이동
    dx_m = (j + dj - Rpx) * res; dy_m = (i + di - Rpx) * res
    peak = float(surf[i, j]); base = float(surf.mean()); at0 = float(surf[Rpx, Rpx])
    if verbose:
        print(f"{key} [{layers}] n={len(P)} score@0={at0:.3f} best={peak:.3f} (mean {base:.3f}) at vector shift dx={dx_m:+.1f} m(E) dy={dy_m:+.1f} m(row down=S) -> map must move by E {dx_m:+.1f}, N {-dy_m:+.1f}")
    return dict(dx=dx_m, dy_row=dy_m, peak=peak, base=base, at0=at0, n=len(P), surf=surf)

if __name__ == "__main__":
    key = sys.argv[1]
    layers = sys.argv[2] if len(sys.argv) > 2 else "rail"
    thr = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    R = float(sys.argv[4]) if len(sys.argv) > 4 else 40
    gray = key in ("m1984", "m1976")
    rail_shift(key, layers, thr, R, color=not gray)
