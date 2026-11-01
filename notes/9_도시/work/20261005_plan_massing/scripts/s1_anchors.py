"""S1 앵커 추출 — 경계 U에 닿는 기존 가로(중심선·폭)의 접속점. 변(서·동·북·남)·폭·진입 방향 기록.
출력: scratch/anchors.pkl, scratch/context_fig.png (확인용), 콘솔 표
"""
import pickle, math, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import unary_union, nearest_points
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
fm.fontManager.addfont(r"C:\Windows\Fonts\malgun.ttf"); plt.rcParams["font.family"] = "Malgun Gothic"
C = pickle.load(open(SP + r"\context.pkl", "rb"))
U, R, B = C["U"], C["R"], C["B"]
ring = U.exterior

def side_of(pt, tangent):
    nx, ny = -tangent[1], tangent[0]           # 좌측 법선(경계가 반시계면 안쪽)
    return nx, ny

# U 외곽선 위 모든 중심선 교차·접촉 → 앵커 후보
A = []
tol = 6.0
for r in R:
    g = r["geom"]
    if g.distance(ring) > tol: continue
    # 중심선과 U의 교차(관통) 또는 6 m 이내 끝점
    inter = g.intersection(U.exterior.buffer(0.01))
    ends = [Point(g.coords[0]), Point(g.coords[-1])] if g.geom_type == "LineString" else []
    pts = []
    x = g.intersection(ring)
    if not x.is_empty:
        pts += [p for p in (x.geoms if hasattr(x, "geoms") else [x]) if p.geom_type == "Point"]
    for e in ends:
        if e.distance(ring) <= tol: pts.append(e)
    for p in pts:
        s = ring.project(p); q = ring.interpolate(s)
        t0 = ring.interpolate(max(s - 4, 0)); t1 = ring.interpolate(min(s + 4, ring.length))
        tx, ty = t1.x - t0.x, t1.y - t0.y; L = math.hypot(tx, ty) or 1; tx, ty = tx / L, ty / L
        # 가로 방향(경계 교차점에서 가장 가까운 선분 방향)
        gg = g if g.geom_type == "LineString" else max(g.geoms, key=lambda z: z.length)
        sp = gg.project(q); a0 = gg.interpolate(max(sp - 6, 0)); a1 = gg.interpolate(min(sp + 6, gg.length))
        dx, dy = a1.x - a0.x, a1.y - a0.y; Ld = math.hypot(dx, dy) or 1; dx, dy = dx / Ld, dy / Ld
        ang = abs(math.degrees(math.atan2(abs(tx * dy - ty * dx), abs(tx * dx + ty * dy))))  # 경계 접선과 가로 사이 각(0=평행, 90=직교)
        A.append(dict(x=q.x, y=q.y, w=r["w"], name=r["name"], rddv=r["rddv"], ang=ang, dx=dx, dy=dy, tx=tx, ty=ty, inside=U.contains(Point(q.x + 0.5 * (-ty), q.y + 0.5 * tx))))
# 방향 접선과 거의 직교(ang>45°)인 것만, 같은 위치(10 m 이내) 병합
A = [a for a in A if a["ang"] > 40]
A.sort(key=lambda a: ring.project(Point(a["x"], a["y"])))
merged = []
for a in A:
    if merged and math.hypot(a["x"] - merged[-1]["x"], a["y"] - merged[-1]["y"]) < 8:
        if a["w"] > merged[-1]["w"]: merged[-1] = a
        continue
    merged.append(a)
A = merged
cx = U.centroid.x
for a in A:
    a["side"] = "서" if a["x"] < cx - 20 and abs(a["tx"]) < 0.6 else "동" if a["x"] > cx + 20 and abs(a["tx"]) < 0.6 else "북" if a["y"] > U.centroid.y + 100 else "남"
# 폭 3 m 이상만 표시 (좁은 골목도 포함해 별도 표시)
print("앵커 총 %d (폭≥3 m: %d, ≥6 m: %d, ≥10 m: %d)" % (len(A), sum(a["w"] >= 3 for a in A), sum(a["w"] >= 6 for a in A), sum(a["w"] >= 10 for a in A)))
for side in "서동북남":
    s = [a for a in A if a["side"] == side]
    print(f"[{side}] {len(s)}개: " + ", ".join("y=%.0f(%.0fm)" % (a["y"], a["w"]) if side in "서동" else "x=%.0f(%.0fm)" % (a["x"], a["w"]) for a in s))
pickle.dump(A, open(SP + r"\anchors.pkl", "wb"))

# 확인 그림
fig, ax = plt.subplots(figsize=(11, 17))
for b in B:
    f = b["floors"]; c = {1: "#e8e4dc", 2: "#d4cfc4", 3: "#bdb7aa", 4: "#a39d90"}.get(f, "#7a756a")
    for p in (b["geom"].geoms if hasattr(b["geom"], "geoms") else [b["geom"]]): ax.fill(*p.exterior.xy, fc=c, ec="none", zorder=1)
for r in R:
    if r["w"] >= 3:
        c = "#d9534f" if r["w"] >= 15 else "#f0a030" if r["w"] >= 8 else "#5a8fd8" if r["w"] >= 5 else "#999"
        for l in (r["geom"].geoms if hasattr(r["geom"], "geoms") else [r["geom"]]): ax.plot(*l.xy, color=c, lw=0.6 + r["w"] / 12, zorder=2, alpha=0.8)
ax.plot(*ring.xy, color="#8a2be2", lw=2.0, zorder=5)
for i, a in enumerate(A):
    ax.plot(a["x"], a["y"], "o", color="#222", ms=3, zorder=6)
    if a["w"] >= 5: ax.text(a["x"] + (6 if a["side"] == "동" else -6), a["y"], "%.0f" % a["w"], fontsize=6, ha="left" if a["side"] == "동" else "right", va="center", zorder=7)
minx, miny, maxx, maxy = U.buffer(60).bounds; ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy); ax.set_aspect("equal")
ax.set_title("경계 U와 기존 가로 접속점(앵커) — 선 색: 빨강≥15 m, 주황≥8 m, 파랑≥5 m / 점 옆 숫자=폭(m)")
fig.tight_layout(); fig.savefig(SP + r"\context_fig.png", dpi=100)
