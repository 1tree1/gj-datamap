# 모자이크 재정합(아핀): 원본별 영역에서 60 m 창마다 '사진 경계선(그래디언트)' ↔ '모델 도로 경계선'을 상관해
# 대응점을 모으고 RANSAC 아핀으로 맞춘다. (기존 정사영상 정합은 평행이동+축척만이라 회전 오차가 남아 있었다)
# 출력: <scratch>/mosaic/mosaic_015_aligned.jpg, mosaic_015_aligned_src.png, align_affine.json
import json

import cv2
import numpy as np
from shapely.geometry import Polygon

from c0_common import D, MOS, Mosaic

mos = Mosaic(aligned=False)
src = json.load(open(D / "frame_src.json", encoding="utf-8"))
polys = [Polygon([l[1] for l in it["loops"] if l[0]][0], [l[1] for l in it["loops"] if not l[0]]).buffer(0)
         for it in src["items"] if it["cat"] == "도로"]
edge = np.zeros((mos.h, mos.w), np.uint8)
for g in polys:
    for p in getattr(g, "geoms", [g]):
        for ring in [p.exterior] + list(p.interiors):
            cv2.polylines(edge, [np.round(mos.to_px(np.array(ring.coords))).astype(np.int32)], True, 255, 2)
gray = cv2.cvtColor(mos.rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
gm = np.sqrt(gx * gx + gy * gy); gm = np.minimum(gm, np.percentile(gm, 98))
gmb = cv2.GaussianBlur(gm, (0, 0), 2.5); eb = cv2.GaussianBlur(edge.astype(np.float32), (0, 0), 2.5)
srcmap = cv2.imread(str(MOS / "mosaic_015_src.png"), cv2.IMREAD_GRAYSCALE)
meta = json.load(open(MOS / "mosaic_015.json"))

T, STEPW, MARG = 400, 150, 110            # 창 60 m, 간격 22.5 m, 탐색 ±16.5 m
result = {}
out = mos.rgb.copy()
outsrc = srcmap.copy()
uu, vv = np.meshgrid(np.arange(mos.w, dtype=np.float32), np.arange(mos.h, dtype=np.float32))
ORDER = ["o2025"] + [n for n in meta["sources"] if n != "o2025"]
M_ref = None
for name in ORDER:
    si = meta["sources"].index(name)
    region = srcmap == si
    if region.mean() < 0.01:
        continue
    A, B, S = [], [], []
    for y in range(MARG, mos.h - T - MARG, STEPW):
        for x in range(MARG, mos.w - T - MARG, STEPW):
            if region[y:y + T, x:x + T].mean() < 0.9:
                continue
            t = eb[y:y + T, x:x + T]
            if (t > 0.2 * t.max()).mean() < 0.04:
                continue
            s = gmb[y - MARG:y + T + MARG, x - MARG:x + T + MARG]
            r = cv2.matchTemplate(s, t, cv2.TM_CCOEFF_NORMED)
            _, mx, _, loc = cv2.minMaxLoc(r)
            if mx < 0.12:
                continue
            A.append((x + T / 2, y + T / 2)); B.append((x + T / 2 + loc[0] - MARG, y + T / 2 + loc[1] - MARG)); S.append(mx)
    A, B = np.array(A, np.float64), np.array(B, np.float64)
    if name != "o2025" and M_ref is not None:
        M = M_ref; inl = np.ones(len(A), np.uint8)
        print(name, "→ 정사영상 보정 적용(항공사진은 정사영상 기준 정합)")
    elif len(A) < 12:
        print(name, "too few windows", len(A)); continue
    else:
        M = None
    if M is None:
      M, inl = cv2.estimateAffinePartial2D(A, B, method=cv2.RANSAC, ransacReprojThreshold=8.0, maxIters=20000, confidence=0.999)
    if name == "o2025":
        M_ref = M
    inl = np.asarray(inl).ravel().astype(bool)
    res = np.linalg.norm((A[inl] @ M[:, :2].T + M[:, 2]) - B[inl], axis=1)
    ang = np.degrees(np.arctan2(M[1, 0], M[0, 0])); sc = np.sqrt(abs(np.linalg.det(M[:, :2])))
    shift = np.linalg.norm((A @ M[:, :2].T + M[:, 2]) - A, axis=1) * 0.15
    print("%s windows %d inliers %d  rot %.3f deg  scale %.4f  resid px med %.1f  corr shift m: min %.1f max %.1f"
          % (name, len(A), inl.sum(), ang, sc, np.median(res), shift.min(), shift.max()))
    result[name] = {"M": M.tolist(), "n": int(len(A)), "inliers": int(inl.sum()), "rot_deg": float(ang), "scale": float(sc),
                    "resid_px_med": float(np.median(res))}
    # 출력(u,v)의 값 = 원 모자이크(M·(u,v))   — 이 원본 영역만 교체
    mapx = (M[0, 0] * uu + M[0, 1] * vv + M[0, 2]).astype(np.float32)
    mapy = (M[1, 0] * uu + M[1, 1] * vv + M[1, 2]).astype(np.float32)
    warped = cv2.remap(mos.rgb, mapx, mapy, cv2.INTER_LINEAR)
    wsrc = cv2.remap(srcmap, mapx, mapy, cv2.INTER_NEAREST, borderValue=255)
    take = wsrc == si
    out[take] = warped[take]; outsrc[take] = si
    # 원래 이 원본이던 자리 중 이제 비는 곳
    gone = (srcmap == si) & ~take
    outsrc[gone & (outsrc == si)] = 255
cv2.imwrite(str(MOS / "mosaic_015_aligned.jpg"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 93])
cv2.imwrite(str(MOS / "mosaic_015_aligned_src.png"), outsrc)
json.dump(result, open(MOS / "align_affine.json", "w"), indent=1)
print("coverage after %.1f%%" % (100 * (outsrc != 255).mean()))
