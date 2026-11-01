"""C0 맥락 건물 재정합 — 배경이 맞지 않던 원인과 수정
원인: ① 사용자 콘타 모델(최종콘타모델_v2) 좌표 O는 실제의 1/2 축척(정북 방향, EPSG:5179 근처 값)
      ② ctx_buildings_planframe.json 은 이전 세션이 사용자 구 역사 복사본에 맞춘 변환(2배·−33.79° 회전)으로 만든 것 → 배경이 34° 돌아감
기준: V-World 연속지적(2025.01, raw/vworld_parcel.geojson) — 계획 경계 B는 이동만으로 지적·고시 구역과 일치(로컬 = 5179 + (TX − X0, TY − Y0))
수정: O = 회전 변환의 역(정확), 로컬 = s·R(θ)·(O − c) + t 를 지적에 맞춘다(건물 표본점이 도로·철도·하천 필지에 떨어지는 비율 최소)
출력: data/ctx_registered.pkl, sheets/c0_register_check.png"""
import os, json, pickle, math, time
import numpy as np
import shapely
from shapely.geometry import Polygon
from shapely import affinity
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); SH = os.path.join(HERE, "..", "sheets")
V1 = os.path.join(HERE, "..", "..", "20261011_masterplan_v1", "data")
R = pickle.load(open(os.path.join(D, "real_overlay.pkl"), "rb"))
S = pickle.load(open(os.path.join(D, "design.pkl"), "rb")); B = S["B"]
xr = json.load(open(os.path.join(V1, "xf_ctx_to_plan.json"))); Rm = np.array(xr["R"]); s0 = xr["s"]; t0_ = np.array(xr["t"])
xf = json.load(open(os.path.join(V1, "xf_final.json"), encoding="utf-8"))
C = json.load(open(os.path.join(V1, "ctx_buildings_planframe.json")))
TX, TY, X0, Y0 = R["TX"], R["TY"], S["X0"], S["Y0"]

OB = []
for b in C:
    O = ((np.array(b["p"]) - t0_) / s0) @ Rm                     # 회전 변환의 역 → 콘타 모델 원좌표
    g = Polygon(O).buffer(0)
    if not g.is_empty and g.area > 1: OB.append((g, b["h"], b.get("z0", 0.0)))
cen = np.mean([g.centroid.coords[0] for g, h, z in OB], axis=0)
print("buildings", len(OB), "centroid O", cen.round(1))

X_0, Y_0, W, H = -900.0, -800.0, 2600, 2800
img = Image.new("F", (W, H), 0.6); dr = ImageDraw.Draw(img)
BAD = set("도철천구제유")
# 도로·철도 필지는 구멍(가구)이 있는 큰 다각형이 많다 → 나쁜 필지를 먼저 칠하고 대지류 필지를 위에 덮는다
for bad_pass in (True, False):
    for g, p in R["PAR"]:
        cat = p["jibun"].strip()[-1]
        if (cat in BAD) != bad_pass: continue
        for q in (g.geoms if hasattr(g, "geoms") else [g]):
            dr.polygon([(x - X_0, H - (y - Y_0)) for x, y in q.exterior.coords], fill=1.0 if cat in BAD else 0.0)
            if cat in BAD:
                for ring in q.interiors: dr.polygon([(x - X_0, H - (y - Y_0)) for x, y in ring.coords], fill=0.6)
RAS = np.array(img)
rng = np.random.default_rng(3); SP = []
for g, h, z in OB:
    n = int(min(10, max(2, g.area / 6)))
    x0, y0, x1, y1 = g.bounds; got = 0
    for _ in range(n * 6):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        if g.contains(shapely.Point(x, y)): SP.append((x, y)); got += 1
        if got >= n: break
SP = np.array(SP) - cen


def score(theta, s, tx, ty):
    c, sn = math.cos(math.radians(theta)), math.sin(math.radians(theta))
    X = s * (c * SP[:, 0] - sn * SP[:, 1]) + tx; Y = s * (sn * SP[:, 0] + c * SP[:, 1]) + ty
    ix = np.clip((X - X_0).astype(int), 0, W - 1); iy = np.clip((H - (Y - Y_0)).astype(int), 0, H - 1)
    return float(RAS[iy, ix].mean())


# 이전 세션 xf_final(2배·회전 0) 위치의 무게중심(로컬)
c_fin = 2 * cen + np.array(xf["t"]) - np.array([517.0557 + X0, Y0])
print("xf_final(2x, θ0) centroid local", c_fin.round(1), "penalty", round(score(0, 2.0, *c_fin), 4))
t0 = time.time(); res = []
for s in (2.0,):
    for tx in np.arange(c_fin[0] - 150, c_fin[0] + 151, 3.0):
        for ty in np.arange(c_fin[1] - 150, c_fin[1] + 151, 3.0):
            res.append((score(0.0, s, tx, ty), 0.0, s, tx, ty))
res.sort(); print("coarse %.1fs" % (time.time() - t0)); [print("  ", tuple(round(float(v), 3) for v in r)) for r in res[:5]]
best = res[0]
fine = []
for sc, th0, s_, tx0, ty0 in res[:4]:
    for th in np.arange(-1.5, 1.51, 0.25):
        for s in np.arange(s_ * 0.97, s_ * 1.031, s_ * 0.01):
            for tx in np.arange(tx0 - 6, tx0 + 6.1, 1.0):
                for ty in np.arange(ty0 - 6, ty0 + 6.1, 1.0):
                    fine.append((score(th, s, tx, ty), th, s, tx, ty))
fine.sort(); [print("  fine", tuple(round(float(v), 3) for v in r)) for r in fine[:4]]
sc, th, s, tx, ty = fine[0]
for th_ in np.arange(th - 0.25, th + 0.26, 0.05):
    for s_ in np.arange(s - 0.01, s + 0.0101, 0.0025):
        for tx_ in np.arange(tx - 1.0, tx + 1.01, 0.25):
            for ty_ in np.arange(ty - 1.0, ty + 1.01, 0.25):
                v = score(th_, s_, tx_, ty_)
                if v < sc: sc, th, s, tx, ty = v, th_, s_, tx_, ty_
print("BEST θ %.2f°  s %.4f  t(%.2f, %.2f)  벌점 %.4f   (xf_final 위치 벌점 %.4f)" % (th, s, tx, ty, sc, score(0, 2.0, *c_fin)))


def apply(g):
    g2 = affinity.translate(g, -cen[0], -cen[1]); g2 = affinity.rotate(g2, th, origin=(0, 0)); g2 = affinity.scale(g2, s, s, origin=(0, 0))
    return affinity.translate(g2, tx, ty)


CTX = [(apply(g), h * s / 2.0 * 2.0 if False else h, z) for g, h, z in OB]
pickle.dump(dict(CTX=CTX, theta=th, scale=s, t=(tx, ty), cen=cen.tolist(), penalty=sc, base_penalty=score(0, 2.0, *c_fin),
                 note="로컬 = s·R(θ)·(O − cen) + t, O = 콘타 모델 원좌표(1/2 축척). 기준 = V-World 연속지적(2025.01). 높이 h는 planframe 값(이미 2배 환산) 그대로"),
            open(os.path.join(D, "ctx_registered.pkl"), "wb"))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(30, 14), dpi=80)
for ax, ext in zip(axs, [(-500, 900, -400, 1400), (-120, 200, 300, 620), (60, 320, 150, 420)]):
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath
    for g, p in R["PAR"]:
        cat = p["jibun"].strip()[-1]
        for q in (g.geoms if hasattr(g, "geoms") else [g]):
            if cat in BAD:
                vs, cs_ = [], []
                for ring in [q.exterior] + list(q.interiors):
                    c_ = list(ring.coords); vs += c_; cs_ += [MPath.MOVETO] + [MPath.LINETO] * (len(c_) - 2) + [MPath.CLOSEPOLY]
                ax.add_patch(PathPatch(MPath(vs, cs_), fc="#f6d5e4", lw=0))
            xs, ys = q.exterior.xy; ax.plot(xs, ys, color="#c06", lw=0.3)
    for g, h, z in CTX:
        for q in (g.geoms if hasattr(g, "geoms") else [g]):
            xs, ys = q.exterior.xy; ax.fill(xs, ys, color="#333", alpha=0.55, lw=0)
    xs, ys = B.exterior.xy; ax.plot(xs, ys, "b-", lw=1.5)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal")
fig.savefig(os.path.join(SH, "c0_register_check.png"), bbox_inches="tight")
