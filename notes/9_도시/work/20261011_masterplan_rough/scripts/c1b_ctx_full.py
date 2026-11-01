"""C1b 주변 건물 전체 재구성 — 라이노 aardvark(최종콘타모델_v2_v3경계.3dm) '빌딩' 23,178동 바닥 윤곽(data/ctxO_all.json, 콘타 좌표 O)
+ 이전 세션이 지운 건물(ctx_candidates.json, 삭제 전 추출, 회전 변환 좌표 → 역변환으로 O) 복원
→ V-World 연속지적에 정합(2배·회전·이동 미세 조정, c0 결과 근처) → data/ctx_fixed.pkl(c1과 같은 형식) + sheets/c1b_coverage.png
높이 = 2 × (z1 − z0)(콘타 모델 1/2 축척)"""
import os, json, pickle, math
import numpy as np
import shapely
from shapely.geometry import Polygon, box
from shapely import affinity
from shapely.ops import unary_union
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); SH = os.path.join(HERE, "..", "sheets")
V1 = os.path.join(HERE, "..", "..", "20261011_masterplan_v1", "data")
S = pickle.load(open(os.path.join(D, "design.pkl"), "rb")); B = S["B"]
DS = pickle.load(open(os.path.join(D, "district.pkl"), "rb"))
REG = pickle.load(open(os.path.join(D, "ctx_registered.pkl"), "rb"))
xr = json.load(open(os.path.join(V1, "xf_ctx_to_plan.json"))); Rm = np.array(xr["R"]); s0 = xr["s"]; t0_ = np.array(xr["t"])

# 1) aardvark 전체
A = json.load(open(os.path.join(D, "ctxO_all.json")))
OB, ids = [], set()
for o in A:
    P = np.array(o["p"])
    if P[:, 0].max() > 1160000: continue                     # 계획 프레임 객체(사용자 역사 복사본 등) 제외
    g = Polygon(P).buffer(0)
    if g.is_empty or g.area < 0.5: continue
    OB.append((g, 2.0 * (o["z1"] - o["z0"]), o["id"])); ids.add(o["id"])
print("aardvark buildings (O frame)", len(OB))
# 2) 지워진 건물 복원
cand = [o for o in json.load(open(os.path.join(V1, "ctx_candidates.json"), encoding="utf-8")) if o["layer"] == "빌딩"]
add = 0
for o in cand:
    if o["id"] in ids: continue
    rings = json.loads(o["rings"]) if isinstance(o["rings"], str) else o["rings"]
    if not rings: continue
    P = ((np.array(rings[0])[:, :2] - t0_) / s0) @ Rm
    g = Polygon(P).buffer(0)
    bb = json.loads(o["bbox"]) if isinstance(o["bbox"], str) else o["bbox"]
    if g.is_empty or g.area < 0.5: continue
    OB.append((g, 2.0 * (bb[5] - bb[2]), o["id"])); add += 1
print("restored (deleted earlier)", add, "total", len(OB))

# 3) 정합 미세 조정(지적 벌점 래스터)
cen = np.array(REG["cen"]); th0, sc0, (tx0, ty0) = REG["theta"], REG["scale"], REG["t"]
X_0, Y_0, W, H = -1400.0, -1400.0, 3200, 3900
img = Image.new("F", (W, H), 0.6); dr = ImageDraw.Draw(img)
BAD = set("도철천구제유")
for bad_pass in (True, False):
    for g, c in DS["PAR"]:
        if (c in BAD) != bad_pass: continue
        for q in (g.geoms if hasattr(g, "geoms") else [g]):
            dr.polygon([(x - X_0, H - (y - Y_0)) for x, y in q.exterior.coords], fill=1.0 if c in BAD else 0.0)
            if c in BAD:
                for ring in q.interiors: dr.polygon([(x - X_0, H - (y - Y_0)) for x, y in ring.coords], fill=0.6)
RAS = np.array(img)
rng = np.random.default_rng(5); SP = []
for g, h, i in OB:
    n = int(min(6, max(1, g.area / 8))); got = 0
    x0, y0, x1, y1 = g.bounds
    for _ in range(n * 6):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        if g.contains(shapely.Point(x, y)): SP.append((x, y)); got += 1
        if got >= n: break
SP = np.array(SP) - cen
def score(th, s, tx, ty):
    c, sn = math.cos(math.radians(th)), math.sin(math.radians(th))
    X = s * (c * SP[:, 0] - sn * SP[:, 1]) + tx; Y = s * (sn * SP[:, 0] + c * SP[:, 1]) + ty
    ix = np.clip((X - X_0).astype(int), 0, W - 1); iy = np.clip((H - (Y - Y_0)).astype(int), 0, H - 1)
    v = RAS[iy, ix]; m = np.abs(v - 0.6) > 0.05                      # 지적이 있는 곳만으로 평가(지적 밖 0.6 제외)
    return float(v[m].mean()) if m.any() else 1.0, float(m.mean())
base = score(th0, sc0, tx0, ty0); print("previous transform: penalty(on cadastre) %.4f, coverage %.3f" % base)
best = (base[0], th0, sc0, tx0, ty0)
for th in np.arange(th0 - 1.0, th0 + 1.01, 0.25):
    for s in np.arange(sc0 - 0.03, sc0 + 0.0301, 0.01):
        for tx in np.arange(tx0 - 12, tx0 + 12.1, 2.0):
            for ty in np.arange(ty0 - 12, ty0 + 12.1, 2.0):
                v = score(th, s, tx, ty)[0]
                if v < best[0]: best = (v, th, s, tx, ty)
v, th, s, tx, ty = best
for th_ in np.arange(th - 0.2, th + 0.21, 0.05):
    for s_ in np.arange(s - 0.006, s + 0.0061, 0.002):
        for tx_ in np.arange(tx - 1.5, tx + 1.51, 0.5):
            for ty_ in np.arange(ty - 1.5, ty + 1.51, 0.5):
                w = score(th_, s_, tx_, ty_)[0]
                if w < v: v, th, s, tx, ty = w, th_, s_, tx_, ty_
print("BEST θ %.2f° s %.4f t(%.2f, %.2f) penalty %.4f" % (th, s, tx, ty, v))


def apply(g):
    g2 = affinity.translate(g, -cen[0], -cen[1]); g2 = affinity.rotate(g2, th, origin=(0, 0)); g2 = affinity.scale(g2, s, s, origin=(0, 0))
    return affinity.translate(g2, tx, ty)


# 4) 정리: 찌꺼기 제거·중복(복원분과 겹침) 제거·구역 안 표시
out, drop = [], 0
Bb = B.buffer(1.0)
for g, h, i in OB:
    ga = apply(g)
    for q in (ga.geoms if hasattr(ga, "geoms") else [ga]):
        if q.area < 4: continue
        mrr = q.minimum_rotated_rectangle.area
        if (mrr > 0 and q.area / mrr < 0.45 and q.area > 80): drop += 1; continue
        out.append(dict(g=q, h=float(max(h, 3.0)), z0=0.0, inside=bool(Bb.contains(q.representative_point())), id=i))
# 중복 제거(같은 자리 두 번)
from shapely.strtree import STRtree
T = STRtree([o["g"] for o in out]); keep = [True] * len(out)
for k, o in enumerate(out):
    if not keep[k]: continue
    for j in T.query(o["g"]):
        if j <= k or not keep[j]: continue
        a = o["g"].intersection(out[j]["g"]).area
        if a > 0.8 * min(o["g"].area, out[j]["g"].area): keep[j] = False
out = [o for o, kp in zip(out, keep) if kp]
print("final", len(out), "dropped junk", drop, "inside boundary", sum(o["inside"] for o in out))
pickle.dump(dict(B=out, xf=dict(theta=th, scale=s, t=(tx, ty), cen=cen.tolist()), note="콘타 모델 '빌딩' 전체(aardvark 23,178 + 삭제분 복원) → V-World 연속지적(2025.01) 정합. 로컬 = s·R(θ)·(O − cen) + t"),
            open(os.path.join(D, "ctx_fixed.pkl"), "wb"))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 2, figsize=(26, 16), dpi=70)
for ax, ext in zip(axs, [(-1300, 1600, -1300, 2300), (-250, 150, 500, 1000)]):
    for g, c in DS["PAR"]:
        if g.bounds[2] < ext[0] or g.bounds[0] > ext[1] or g.bounds[3] < ext[2] or g.bounds[1] > ext[3]: continue
        for q in (g.geoms if hasattr(g, "geoms") else [g]):
            if c == "대": ax.fill(*q.exterior.xy, color="#f3c9d6", lw=0)
            ax.plot(*q.exterior.xy, color="#c06", lw=0.2)
    for o in out:
        if o["g"].bounds[2] < ext[0] or o["g"].bounds[0] > ext[1] or o["g"].bounds[3] < ext[2] or o["g"].bounds[1] > ext[3]: continue
        ax.fill(*o["g"].exterior.xy, color="#c33" if o["inside"] else "#333", lw=0)
    ax.plot(*B.exterior.xy, "g-", lw=2)
    for e_, c_ in (((-820, 1020, -760, 1330), "orange"), ((-330, 740, -60, 1110), "purple"), ((-230, 640, 20, 1040), "red")):
        ax.plot([e_[0], e_[1], e_[1], e_[0], e_[0]], [e_[2], e_[2], e_[3], e_[3], e_[2]], color=c_, lw=1.5)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal")
fig.savefig(os.path.join(SH, "c1b_coverage.png"), bbox_inches="tight")
