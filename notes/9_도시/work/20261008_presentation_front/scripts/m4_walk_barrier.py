# -*- coding: utf-8 -*-
"""M4 보행 단절 지도 (S1~S2) — 1800x2400 px, 동서 1,400m x 남북 1,867m, 중심 (219,780 / 360,850).

재현하는 수치(출처 스크립트)
  985 m  : 두 도로 횡단 사이 구간          pipeline/build_extent_diagnosis.py (도로×철도중심선 교차)
  육교   : N3A_A0063321 폭 3.2 m 길이 216.3 m
  601/1,531 m, 2.55배 : A→B 최단경로        pipeline/build_gyeongju_reading.py (map16 '폐선 부지 가로지르기')
  3.5/5.3 : 폐선 양쪽 60 m 지점 간 우회율 50 m 간격 18개 단면(고시 구역 y 범위), 육교 제외
                                          pipeline/build_extent_diagnosis.py (map10 우측 그래프)
  37곳   : 부지로 접근하다 끊기는 도로 끝점  work/20261005_plan_massing/scripts/s1_anchors.py 와 같은 규칙
출력: assets/maps/m4_walk_barrier.png, research/data_series/detour_ratio_18sections.csv,
      research/data_series/m4_metrics_check.csv
실행: export PYTHONUTF8=1 PYTHONIOENCODING=utf-8; python m4_walk_barrier.py
"""
import csv
import heapq
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapkit_analysis as mk
from mapkit_analysis import *  # noqa: F401,F403
from matplotlib.colors import LinearSegmentedColormap
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, dijkstra as sp_dijkstra
from scipy.spatial import cKDTree
from shapely.ops import nearest_points

# ───────────────────────── 1. 분석 (수치 재현) ─────────────────────────
zone = mk.gosi_zone()
plan = mk.plan_boundary()
road = mk.read_ngii("N3L_A0020000")
rail_poly = unary_union([g for g, _ in mk.read_ngii("N3A_A0160024")])
rail_cl = unary_union([g for g, _ in mk.read_ngii("N3L_A0171119")])
overpass = mk.read_ngii("N3A_A0063321")

# (a) 도로×철도중심선 횡단점 → 985 m
pts = []
for g, a in road:
    if g.intersects(rail_cl):
        x = g.intersection(rail_cl)
        for p in getattr(x, "geoms", [x]):
            if p.geom_type == "Point":
                pts.append((p.x, p.y, float(a.get("rvwd") or 0)))
pts.sort(key=lambda t: t[1])
parts = list(getattr(rail_poly, "geoms", [rail_poly]))
pa, pb = nearest_points(parts[0], parts[1])          # 철도 선형이 도로 면으로 끊긴 곳(구역 남단 횡단)
south_x, south_y = (pa.x + pb.x) / 2, (pa.y + pb.y) / 2
zb = zone.bounds
north = min((p for p in pts if p[1] > zb[3]), key=lambda t: t[1])       # 구역 북단 밖 첫 횡단
north_x, north_y, north_w = north
gap_m = north_y - south_y
south_off = zb[1] - south_y
north_off = north_y - zb[3]

# (b) 도로 그래프 (정점 0.5 m 스냅) — build_extent_diagnosis / build_gyeongju_reading 과 같은 방식
key, XY, I, J, Wt = {}, [], [], [], []
ADJ, EDGES = defaultdict(list), []


def nid(p):
    k = (round(p[0] * 2), round(p[1] * 2))
    if k not in key:
        key[k] = len(XY)
        XY.append(p)
    return key[k]


for g, a in road:
    for gg in getattr(g, "geoms", [g]):
        cs = list(gg.coords)
        for p, q in zip(cs[:-1], cs[1:]):
            i, j = nid(p), nid(q)
            if i != j:
                d = math.hypot(p[0] - q[0], p[1] - q[1])
                I += [i, j]; J += [j, i]; Wt += [d, d]
                e = len(EDGES)
                EDGES.append((i, j, d))
                ADJ[i].append(e); ADJ[j].append(e)
XY = np.array(XY)
G = coo_matrix((Wt, (I, J)), shape=(len(XY), len(XY))).tocsr()
_, lab = connected_components(G, directed=False)
keep = np.where(lab == np.bincount(lab).argmax())[0]
tree = cKDTree(XY[keep])

# (c) 동서 우회율 단면 (폐선 양쪽 60 m 지점, 50 m 간격, 육교 미포함)
sections = []
for y in np.arange(zb[1] - 250, zb[3] + 250.1, 50):
    seg = LineString([(zb[0] - 900, y), (zb[2] + 900, y)]).intersection(rail_poly)
    if seg.is_empty:
        continue
    xs = [c[0] for s in getattr(seg, "geoms", [seg]) for c in s.coords]
    _, iw = tree.query((min(xs) - 60, y))
    _, ie = tree.query((max(xs) + 60, y))
    a, b = keep[iw], keep[ie]
    net = float(sp_dijkstra(G, indices=a)[b])
    eu = float(np.hypot(*(XY[a] - XY[b])))
    sections.append(dict(y=float(y), x_w=min(xs), x_e=max(xs), a=XY[a].copy(), b=XY[b].copy(), net=net, eu=eu,
                         ratio=net / eu))
secs = [s for s in sections if zb[1] <= s["y"] <= zb[3]]          # 고시 구역 y 범위 안 18개
ratios = np.array([s["ratio"] for s in secs])
r_med, r_max, r_min, r_mean = float(np.median(ratios)), float(ratios.max()), float(ratios.min()), float(ratios.mean())


# (d) A→B 최단경로 (직선 약 600 m) — map16 '폐선 부지 가로지르기'
def dijkstra_path(src, dst):
    dist = {src: 0.0}; prev = {}; pq = [(0.0, src)]; done = set(); order = []
    while pq:
        dd, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u); order.append(u)
        if u == dst:
            break
        for e in ADJ[u]:
            i, j, l = EDGES[e]
            v = j if i == u else i
            nd = dd + l
            if nd < dist.get(v, 1e18):
                dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    return dist[dst], path[::-1], len(order)


NTREE = STRtree(shapely.points(XY))


def pick_node(target, rmax):
    best, bd = None, 1e18
    for n in NTREE.query(Point(target).buffer(rmax)):
        if len(ADJ[n]) >= 2:
            d = math.dist(XY[n], target)
            if d < bd:
                best, bd = n, d
    return best


A_TARGET, B_TARGET = (219470.0, 360990.0), (220070.0, 360990.0)
nA = pick_node(A_TARGET, 250)
u = np.array(B_TARGET) - np.array(A_TARGET)
u /= np.linalg.norm(u)
nB = pick_node(tuple(XY[nA] + 600.0 * u), 120)
net_m, path_nodes, n_explored = dijkstra_path(nA, nB)
straight_m = math.dist(XY[nA], XY[nB])
path_xy = np.array([XY[n] for n in path_nodes])
detour_ab = net_m / straight_m

# (e) 부지로 접근하다 끊기는 도로 끝점 (경계 6 m 이내 접촉·관통, 경계와 직교에 가까운 것, 8 m 병합) — s1_anchors.py 와 같은 규칙
ring = plan.exterior
anc = []
for g, a in road:
    if g.distance(ring) > 6.0:
        continue
    cand = []
    xx = g.intersection(ring)
    if not xx.is_empty:
        cand += [p for p in getattr(xx, "geoms", [xx]) if p.geom_type == "Point"]
    for e in ([Point(g.coords[0]), Point(g.coords[-1])] if g.geom_type == "LineString" else []):
        if e.distance(ring) <= 6.0:
            cand.append(e)
    for p in cand:
        s = ring.project(p); q = ring.interpolate(s)
        t0 = ring.interpolate(max(s - 4, 0)); t1 = ring.interpolate(min(s + 4, ring.length))
        tx, ty = t1.x - t0.x, t1.y - t0.y
        L = math.hypot(tx, ty) or 1; tx, ty = tx / L, ty / L
        gg = g if g.geom_type == "LineString" else max(g.geoms, key=lambda z: z.length)
        sp_ = gg.project(q); a0 = gg.interpolate(max(sp_ - 6, 0)); a1 = gg.interpolate(min(sp_ + 6, gg.length))
        dx, dy = a1.x - a0.x, a1.y - a0.y
        Ld = math.hypot(dx, dy) or 1; dx, dy = dx / Ld, dy / Ld
        ang = abs(math.degrees(math.atan2(abs(tx * dy - ty * dx), abs(tx * dx + ty * dy))))
        anc.append(dict(x=q.x, y=q.y, w=float(a.get("rvwd") or 0), ang=ang, tx=tx, ty=ty))
anc = [a for a in anc if a["ang"] > 40]
anc.sort(key=lambda a: ring.project(Point(a["x"], a["y"])))
merged = []
for a in anc:
    if merged and math.hypot(a["x"] - merged[-1]["x"], a["y"] - merged[-1]["y"]) < 8:
        if a["w"] > merged[-1]["w"]:
            merged[-1] = a
        continue
    merged.append(a)
anc = merged
_cx, _cy = plan.centroid.x, plan.centroid.y
for a in anc:        # s1_anchors.py 와 같은 변 구분
    a["side"] = ("서" if a["x"] < _cx - 20 and abs(a["tx"]) < 0.6 else "동" if a["x"] > _cx + 20 and abs(a["tx"]) < 0.6
                 else "북" if a["y"] > _cy + 100 else "남")
side_n = {k: sum(a["side"] == k for a in anc) for k in "서동남북"}

# (f) 육교
ov_g, ov_a = overpass[0]
ov_c = ov_g.centroid

# ── 수치 요약 ──
print(f"985m 구간: 남 횡단 y={south_y:.1f}, 북 횡단 y={north_y:.1f} → {gap_m:.1f} m (구역 남단 밖 {south_off:.1f}, 북단 밖 {north_off:.1f}, 구역 {zb[3]-zb[1]:.1f})")
print(f"육교: 폭 {ov_a.get('widt')} m, 길이 {ov_a.get('leng'):.1f} m, 중심 ({ov_c.x:.0f},{ov_c.y:.0f})")
print(f"A→B: 망 {net_m:.1f} m / 직선 {straight_m:.1f} m = {detour_ab:.3f}  (탐색 노드 {n_explored:,})")
print(f"단면 {len(secs)}개: 중앙값 {r_med:.3f}, 최대 {r_max:.3f}, 최소 {r_min:.3f}, 평균 {r_mean:.3f}")
print(f"끊기는 도로 끝점 {len(anc)}곳 {side_n}")

# ───────────────────────── 2. CSV ─────────────────────────
with open(DATA_SERIES / "detour_ratio_18sections.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["단면번호(남→북)", "y_EPSG5187(m)", "폐선 경계 서단 x(m)", "폐선 경계 동단 x(m)", "폐선 폭(m)",
                "서측 지점(경계-60m 최근접 도로 노드) x", "서측 y", "동측 지점(경계+60m 최근접 도로 노드) x", "동측 y",
                "직선거리(m)", "도로망 거리(m)", "우회율(도로망/직선)"])
    for k, s in enumerate(secs, 1):
        w.writerow([k, f"{s['y']:.1f}", f"{s['x_w']:.1f}", f"{s['x_e']:.1f}", f"{s['x_e']-s['x_w']:.1f}",
                    f"{s['a'][0]:.1f}", f"{s['a'][1]:.1f}", f"{s['b'][0]:.1f}", f"{s['b'][1]:.1f}",
                    f"{s['eu']:.1f}", f"{s['net']:.1f}", f"{s['ratio']:.3f}"])
with open(DATA_SERIES / "m4_metrics_check.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["지표", "문서 값", "지도 데이터 재산정", "일치 여부", "정의·메모", "재현 스크립트"])
    w.writerow(["도로 횡단 없는 구간(m)", "985", f"{gap_m:.1f}",
                "일치(반올림 차 0.6m)",
                f"남쪽 횡단(철도 선형이 도로 면으로 끊긴 곳) y={south_y:.1f} ~ 북쪽 횡단(폭 {north_w:.0f}m) y={north_y:.1f}. "
                f"구역 남북 {zb[3]-zb[1]:.1f}m + 남단 밖 {south_off:.1f}m + 북단 밖 {north_off:.1f}m. 문서의 985는 각 항을 정수로 반올림해 더한 값(923+32+30)",
                "pipeline/build_extent_diagnosis.py"])
    w.writerow(["보행 육교 폭(m)", "3.2", f"{ov_a.get('widt')}", "일치", "N3A_A0063321 1개, 높이 4.5m", "pipeline/build_extent_diagnosis.py"])
    w.writerow(["보행 육교 길이(m)", "약 216", f"{ov_a.get('leng'):.1f}", "일치", "속성 leng", "pipeline/build_extent_diagnosis.py"])
    w.writerow(["철도 횡단 최단경로 직선거리(m)", "601", f"{straight_m:.1f}", "일치(반올림)", f"A=({XY[nA][0]:.0f},{XY[nA][1]:.0f}) B=({XY[nB][0]:.0f},{XY[nB][1]:.0f})", "pipeline/build_gyeongju_reading.py (map16)"])
    w.writerow(["철도 횡단 최단경로 도로망 거리(m)", "1,531", f"{net_m:.1f}", "일치(반올림)", f"탐색 노드 {n_explored:,}개", "pipeline/build_gyeongju_reading.py (map16)"])
    w.writerow(["철도 횡단 최단경로/직선", "2.55", f"{detour_ab:.3f}", "일치", "한 쌍(A,B)의 값. 아래 18단면 중앙값 3.5와 정의가 다르다", "pipeline/build_gyeongju_reading.py (map16)"])
    w.writerow(["폐선 양쪽 60m 지점 간 우회율 중앙값(18단면)", "3.5", f"{r_med:.3f}", "일치", "고시 구역 y 범위(360,513~361,436) 안 50m 간격 단면, 육교 제외", "pipeline/build_extent_diagnosis.py"])
    w.writerow(["폐선 양쪽 60m 지점 간 우회율 최대(18단면)", "약 5.3", f"{r_max:.3f}", "일치(5.349)", f"y={secs[int(np.argmax(ratios))]['y']:.0f} 단면. 5.349를 소수 첫째 자리로 반올림하면 5.3. 자료 JSON의 5.35는 둘째 자리 반올림값이라 이를 다시 반올림하면 5.4가 되므로 이중 반올림 주의", "pipeline/build_extent_diagnosis.py"])
    w.writerow(["부지로 접근하다 끊기는 도로 끝점(곳)", "37", f"{len(anc)}", "일치", f"경계 6m 이내 접촉·관통, 경계와 직교에 가까운 것(>40°), 8m 이내 병합. 서 {side_n['서']} · 동 {side_n['동']} · 남 {side_n['남']} · 북 {side_n['북']}", "work/20261005_plan_massing/scripts/s1_anchors.py"])

# ───────────────────────── 3. 그림 ─────────────────────────
W, H = 1800, 2400
CX, CY, WM = 219780.0, 360850.0, 1400.0
fr = Frame(W, H, CX, CY, WM, name="m4")
ax, K = fr.ax, fr.K
win = fr.win.buffer(60)

# 배경: 하천, 건물, 도로 중심선
draw_water(ax, win, z=0.5)
draw_polys_fast(ax, load_buildings(win), fc=C_BLD, z=1)
r_geoms, _ = load_roads(win)
draw_lines(ax, r_geoms, color=C_ROAD, lw=fr.pt(0.5), z=2)

# A→B 최단경로(파랑 실선) — 경계선 아래에 깔아, 경계와 겹치는 구간에서도 가장자리가 보이도록 굵게. 직선은 점선.
ax.plot(path_xy[:, 0], path_xy[:, 1], color=BLUE, lw=fr.pt(4.4), zorder=4, solid_capstyle="round", solid_joinstyle="round")
ax.plot([XY[nA][0], XY[nB][0]], [XY[nA][1], XY[nB][1]], color=BLUE, lw=fr.pt(1.9), ls=(0, (2.0, 2.4)), zorder=4)

# 본 계획 경계(철도 부지 = 폐선)
draw_outline(ax, plan, RED, fr.pt(2.6), z=6)

# 985 m 구간: 두 횡단점(철도 중심선 위)과 양방향 화살표
AX_X = zb[0] - 70.0
for (xx, yy) in ((south_x, south_y), (north_x, north_y)):
    ax.plot([AX_X, xx], [yy, yy], color=RED, lw=fr.pt(1.3), ls=(0, (3, 2)), zorder=7)
    ax.plot([xx], [yy], marker="o", ms=fr.pt(7.0), mfc="white", mec=RED, mew=fr.pt(2.0), zorder=15, ls="none")
ax.add_patch(FancyArrowPatch((AX_X, south_y), (AX_X, north_y), arrowstyle="<|-|>", mutation_scale=fr.pt(22),
                             color=RED, lw=fr.pt(2.4), zorder=14, shrinkA=0, shrinkB=0))

# 끊기는 도로 끝점 37곳 — 작은 회색 점
ax.scatter([a["x"] for a in anc], [a["y"] for a in anc], s=(fr.pt(3.9)) ** 2, c=GRAY, edgecolors="white",
           linewidths=fr.pt(0.7), zorder=9)

# 단면별 우회율 — 옅은 파랑 → 진한 파랑 (흰 고리 + 파랑 테두리로 옅은 색도 보이게)
cmap = LinearSegmentedColormap.from_list("blues_rgb", rgb_ramp("#DCE6F5", BLUE, 9))
V0, V1 = 1.5, 5.4
for s in secs:
    xc = (s["x_w"] + s["x_e"]) / 2
    c = cmap((s["ratio"] - V0) / (V1 - V0))
    ax.plot([xc], [s["y"]], marker="o", ms=fr.pt(9.6), mfc="white", mec="white", mew=0, zorder=10, ls="none")
    ax.plot([xc], [s["y"]], marker="o", ms=fr.pt(8.0), mfc=c, mec=BLUE, mew=fr.pt(0.9), zorder=11, ls="none")

# A, B 두 지점
for n in (nA, nB):
    ax.plot([XY[n][0]], [XY[n][1]], marker="o", ms=fr.pt(8.4), mfc="white", mec=BLUE, mew=fr.pt(2.4), zorder=12, ls="none")

# 육교 — 도형 + 점(대각 구간 중간)
draw_poly(ax, ov_g, fc=INK, ec=INK, lw=fr.pt(0.6), z=10)
p0 = np.array([219752.9, 361084.5]); p1 = np.array([219847.0, 360996.4])
ov_pt = nearest_points(ov_g, Point((p0 + p1) / 2))[0]
ax.plot([ov_pt.x], [ov_pt.y], marker="o", ms=fr.pt(7.2), mfc=INK, mec="white", mew=fr.pt(1.4), zorder=13, ls="none")

# ── 라벨 ──
fr.label(AX_X - 24, 361230.0, "도로 횡단 없는 구간 985m", size=10.5, color=RED, weight="bold", rot=90,
         ha="right", va="center", z=40)
# 육교 라벨(동쪽 이웃 위에, 선으로 연결)
lab_x, lab_y = zb[2] + 70.0, ov_pt.y + 4
ax.plot([ov_pt.x, lab_x - 6], [ov_pt.y, lab_y], color=INK2, lw=fr.pt(0.9), zorder=30)
fr.label(lab_x, lab_y, "보행 육교\n폭 3.2m·길이 약 216m", size=9.5, color=INK, weight="bold", ha="left", va="center", z=40)
# 최단경로 라벨 (부지 남쪽 끝 아래, 선으로 연결)
ly = 360395.0
bot = path_xy[np.argmin(path_xy[:, 1])]
ax.plot([bot[0] + 30, bot[0] + 30], [bot[1] - 6, ly + 46], color=BLUE, lw=fr.pt(0.9), zorder=30)
fr.label(bot[0] + 30, ly, "철도 횡단 최단경로 1,531m\n(직선 601m의 약 2.55배)", size=10.0, color=BLUE, weight="bold",
         ha="center", va="center", z=40)

# 방위·축척·범례
fr.north_arrow()
fr.scale_bar(500, ticks=2)
fr.legend([
    dict(t="line", color=RED, lw=2.6, label="본 계획 경계\n(철도 폐선 부지)"),
    dict(t="dot", color=GRAY, ms=4.4, label="부지 앞에서 끊기는\n도로 끝점 37곳"),
    dict(t="dot", color=INK, ms=6.0, label="보행 육교"),
    dict(t="dot", fc="white", ec=RED, ms=6.0, mew=2.0, label="985m 구간 양 끝의\n도로 횡단"),
    dict(t="line", color=BLUE, lw=3.0, label="최단경로 1,531m"),
    dict(t="line", color=BLUE, lw=1.9, ls=(0, (2.0, 2.4)), label="두 지점 직선 601m"),
    dict(t="cbar", cmap=cmap, vmin=V0, vmax=V1, ticks=[2, 3, 4, 5], fmt="{:g}배", bar_w=330,
         label="폐선 양쪽 60m 지점 간 우회율\n(18개 단면, 육교 제외)", note="중앙값 3.5 · 최대 약 5.3"),
])
fr.save(OUT / "m4_walk_barrier.png")
print("saved", OUT / "m4_walk_barrier.png")
