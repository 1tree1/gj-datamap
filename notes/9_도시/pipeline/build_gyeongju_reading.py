"""경주를 읽는 네 가지 방법 — 층 분해 스택 · 교차점 가시 영역 · 걷기 가시 면적 리듬 · 다익스트라 탐색.

레퍼런스(steinforthstudio 도시 비교 그래픽)의 네 기법을 경주 모델링 범위(연속수치지도 11.06 ㎢)에 적용한다.
  map13  층 분해 스택: 지형 / 물길·비움 / 규제 / 가로 방위 체계·철도 / 3D 매싱(고분은 등고선 적층)
  map14  교차점 가시 영역(isovist, 반경 150 m, 광선 720개): 여섯 조직 유형
  map15  걷기 가시 면적 리듬: 화랑로(격자 틀) · 황오동 골목(세립 채움) · 원화로(폐선 가장자리), 2 m 간격
  map16  다익스트라 탐색: 같은 1.4 km 창 · 직선 약 600 m A→B, 탐색 노드 수와 우회율, 폐선부의 끊긴 격자 틀선
가시 영역의 장애물 = 건물(수치지도 B001) + 담장(B002, 0.15 m 버퍼). 철도 부지는 장애물이 아니다(보이지만 건널 수 없다).

입력: 대지/(B020)연속수치지도_202609132098 (NGII, T2, 5179→5187), archive/C_data/processed (구역계 T1, 규제구역 T1·V-World, 공원 UPIS),
      archive/90_derived/palimpsest_evidence_20260928.json (147.5 m 규칙선)
출력: work/maps/map13~16_*.png, archive/90_derived/gj_reading_20260928.json
"""
import heapq
import json
import math
import re
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import shapefile
import shapely
from pyproj import Transformer
from scipy.interpolate import griddata
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box, shape
from shapely.ops import transform as shp_transform, unary_union
from shapely.strtree import STRtree

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Polygon as MPoly

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "대지" / "(B020)연속수치지도_202609132098"
PROC = ROOT / "archive" / "C_data" / "processed"
DER = ROOT / "archive" / "90_derived"
MAPS = ROOT / "work" / "maps"
T57 = Transformer.from_crs("EPSG:5179", "EPSG:5187", always_xy=True)
T47 = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True)
AX = 89.25                    # 주 격자축(선분 방위 mod 90) — build_fabric_patterns / palimpsest_evidence
R_ISO, N_RAY = 150.0, 720

# ── 스타일 (레퍼런스처럼 어두운 판) ─────────────────────────────
BG, BLOCK, STREET, INK, INK2, INK3 = "#0b0f15", "#2a3341", "#121821", "#e8ecf1", "#9aa5b3", "#5d6877"
GOLD, SITE, TEAL, MAG, BLUE, VIOLET, AMBER = "#e3b341", "#ff5b3d", "#39c4a0", "#ff4fa3", "#6fa8ff", "#a88bff", "#f0a53a"
F_HEAD, F_BODY, F_NUM = "NanumSquare_ac ExtraBold", "NanumSquare_ac", "Bahnschrift"
plt.rcParams.update({"font.family": F_BODY, "axes.unicode_minus": False, "figure.facecolor": BG, "savefig.facecolor": BG,
                     "text.color": INK, "axes.edgecolor": INK3, "axes.labelcolor": INK2, "xtick.color": INK3, "ytick.color": INK3})


def to5187(g, t=T57):
    return shp_transform(lambda x, y, z=None: t.transform(x, y), g)


def fix(v):
    if isinstance(v, str):
        try:
            return v.encode("latin-1").decode("cp949").strip()
        except Exception:
            return v.strip()
    return v


def read(layer):
    r = shapefile.Reader(str(SRC / layer))
    flds = [f[0] for f in r.fields[1:]]
    return [(to5187(shape(s.shape.__geo_interface__)), {k: fix(v) for k, v in zip(flds, list(s.record))})
            for s in r.iterShapeRecords()]


# ── 데이터 ───────────────────────────────────────────────
print("load ...")
EXT = to5187(box(*shapefile.Reader(str(SRC / "N3L_A0020000")).bbox))
BLD = [(g, int(a.get("nmly") or 1) or 1, str(a.get("bjcd") or "")[:10]) for g, a in read("N3A_B0010000") if g.area >= 1]
WALL = [g.buffer(0.15) for g, _ in read("N3L_B0020000")]
OBS = np.array([g for g, _, _ in BLD] + WALL, dtype=object)
OBS_TREE = STRtree(OBS)
BTREE_C = STRtree([g.centroid for g, _, _ in BLD])
ZONE = shape(json.load(open(PROC / "gosi2026-8_zone_5187.geojson", encoding="utf-8"))["features"][0]["geometry"]).buffer(0)
RAILCL = [g for g, _ in read("N3L_A0171119")]
RAILPOLY = unary_union([g for g, _ in read("N3A_A0160024")])
WATER = unary_union([g for lay in ("N3A_E0010001", "N3A_E0032111") for g, _ in read(lay)])
HERIT = [(g, a.get("name") or "") for g, a in read("N3A_C0305316")]

# 가로 그래프 (정점 0.5 m 스냅)
pieces = []
for g, a in read("N3L_A0020000"):
    for gg in getattr(g, "geoms", [g]):
        pieces.append((gg, float(a.get("rvwd") or 0)))
key, XY, ADJ, EDGES = {}, [], defaultdict(list), []


def nid(p):
    k = (round(p[0] * 2), round(p[1] * 2))
    if k not in key:
        key[k] = len(XY); XY.append(p)
    return key[k]


for gg, w in pieces:
    cs = list(gg.coords)
    for p, q in zip(cs[:-1], cs[1:]):
        i, j = nid(p), nid(q)
        if i != j:
            e = len(EDGES); EDGES.append((i, j, math.dist(p, q), w)); ADJ[i].append(e); ADJ[j].append(e)
XY = np.array(XY)
DEG = {n: len(v) for n, v in ADJ.items()}
NTREE = STRtree(shapely.points(XY))
nb = BTREE_C.query_nearest(shapely.points(XY), all_matches=False)
NODE_DONG = np.empty(len(XY), dtype=object); NODE_DONG[nb[0]] = [BLD[i][2] for i in nb[1]]


def node_widths(n):
    return [EDGES[e][3] for e in ADJ[n]]


def edge_theta(e):
    i, j = EDGES[e][0], EDGES[e][1]
    return math.degrees(math.atan2(XY[j][1] - XY[i][1], XY[j][0] - XY[i][0])) % 180


def d90(a, b):
    x = abs((a % 90) - (b % 90))
    return min(x, 90 - x)


def pick_node(target, cond, region=None, rmax=600):
    n = _pick(target, cond, region, rmax)
    if n is None:   # 조건을 못 채우면 반경을 넓히고, 그래도 없으면 조건 없이
        n = _pick(target, cond, region, rmax * 3)
    if n is None:
        n = _pick(target, lambda m: DEG[m] >= 2, None, rmax * 3)
        print(f"   ! {target} 조건 불충족 → 가까운 교차점")
    return n


def _pick(target, cond, region, rmax):
    best, bd = None, 1e18
    for n in NTREE.query(Point(target).buffer(rmax)):
        if region and NODE_DONG[n] not in region:
            continue
        if cond(n):
            d = math.dist(XY[n], target)
            if d < bd:
                best, bd = n, d
    return best


# ── 가시 영역 ─────────────────────────────────────────────
ANG = np.linspace(0, 2 * np.pi, N_RAY, endpoint=False)
COS, SIN = np.cos(ANG), np.sin(ANG)


def isovist(p, R=R_ISO):
    px, py = p
    rays = shapely.linestrings(np.stack([np.c_[np.full(N_RAY, px), np.full(N_RAY, py)], np.c_[px + R * COS, py + R * SIN]], axis=1))
    d = np.full(N_RAY, R)
    idx = OBS_TREE.query(rays, predicate="intersects")
    if idx.size:
        inter = shapely.intersection(rays[idx[0]], OBS[idx[1]])
        dist = shapely.distance(shapely.points(px, py), inter)
        np.minimum.at(d, idx[0], np.nan_to_num(dist, nan=R))
    d = np.maximum(d, 0.3)
    poly = Polygon(np.c_[px + d * COS, py + d * SIN]).buffer(0)
    A, P = poly.area, poly.length
    return poly, {"area": A, "open": A / (math.pi * R * R), "comp": 4 * math.pi * A / (P * P) if P else 0,
                  "maxsight": float(d.max()), "meansight": float(d.mean())}


def draw_base(ax, win, alpha=1.0):
    """레퍼런스식 도형-바탕: 판 = 가로색, 건물 = 블록색"""
    ax.set_facecolor(STREET)
    polys = []
    for i in BTREE_C.query(win.buffer(40)):
        g = BLD[i][0]
        for gg in getattr(g, "geoms", [g]):
            polys.append(np.asarray(gg.exterior.coords))
    ax.add_collection(PolyCollection(polys, facecolors=BLOCK, edgecolors="none", alpha=alpha, zorder=1))
    w = [np.asarray(g.exterior.coords) for g in WALL if g.intersects(win)]
    ax.add_collection(PolyCollection(w, facecolors="#3b4657", edgecolors="none", alpha=alpha, zorder=1))
    b = win.bounds
    ax.set_xlim(b[0], b[2]); ax.set_ylim(b[1], b[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#1d2530")


OUT = {}

# ════════════════════════════════════════════════════════
# map14 — 여섯 조직 유형의 교차점 가시 영역
# ════════════════════════════════════════════════════════
print("isovists ...")
HW, SG, SD = {"4713010500"}, {"4713010800"}, {"4713010400", "4713010600", "4713010700"}
grid_ok = lambda n: all(d90(edge_theta(e), AX) <= 8 for e in ADJ[n])
daereung = [g for g, nm in HERIT if "대릉원" in nm]
dr = max(daereung, key=lambda g: g.area) if daereung else None
P6 = [
    ("원도심 격자 틀", "화랑로 × 중앙로 · 147.5 m 틀선 위", pick_node((219119, 360818), lambda n: DEG[n] >= 4 and max(node_widths(n)) >= 8), GOLD),
    ("성건동 격자", "필지 모듈을 유지한 채 층만 오른 다세대 지구", pick_node((218620, 361520), lambda n: DEG[n] >= 4 and grid_ok(n) and 5 <= max(node_widths(n)) <= 12, SG), BLUE),
    ("황오동 골목", "폭 4 m 미만 골목의 세 갈래·네 갈래", pick_node((220080, 360930), lambda n: DEG[n] >= 3 and max(node_widths(n)) < 4, HW), TEAL),
    ("막다른 골목", "가구 안쪽 필지로 드는 27 m 안팎의 끝", pick_node((220080, 360930), lambda n: DEG[n] == 1 and max(node_widths(n)) < 4, HW), VIOLET),
    ("대릉원 가장자리", "고분이 만드는 큰 비움", pick_node((dr.bounds[2], (dr.bounds[1] + dr.bounds[3]) / 2) if dr else (219300, 359900),
                                          lambda n: DEG[n] >= 2, None, 300), AMBER),
    ("폐선 부지 안", "옛 선로 위 · 지금은 담장 안", None, SITE),
]
_rl = unary_union(RAILCL)
_rp = _rl.interpolate(_rl.project(Point(219790, 361000)))
iso6 = []
for name, sub, n, col in P6:
    p = tuple(XY[n]) if n is not None else (_rp.x, _rp.y)
    poly, m = isovist(p)
    iso6.append((name, sub, p, poly, m, col))
    print(f"  {name}: node {n} {tuple(round(v) for v in p)} widths {node_widths(n) if n is not None else '-'} → area {m['area']:.0f} open {m['open']:.2f} comp {m['comp']:.2f} maxsight {m['maxsight']:.0f}")
OUT["isovists"] = [{"type": nm, "x": round(p[0], 1), "y": round(p[1], 1), **{k: round(v, 3) for k, v in m.items()}} for nm, _, p, _, m, _ in iso6]

fig = plt.figure(figsize=(12, 17.2), dpi=150)
for k, (name, sub, p, poly, m, col) in enumerate(iso6):
    ax = fig.add_axes([0.04 + (k % 2) * 0.49, 0.705 - (k // 2) * 0.31, 0.43, 0.215])
    win = box(p[0] - 160, p[1] - 125, p[0] + 160, p[1] + 125)
    draw_base(ax, win)
    ax.add_patch(plt.Circle(p, R_ISO, fill=False, ls=(0, (3, 4)), lw=0.8, color=INK3, zorder=2))
    for gg in getattr(poly, "geoms", [poly]):
        ax.add_patch(MPoly(np.asarray(gg.exterior.coords), closed=True, facecolor=col, edgecolor=col, alpha=0.62, lw=1.2, zorder=3))
    if name == "폐선 부지 안":
        ax.add_patch(MPoly(np.asarray(ZONE.exterior.coords), closed=True, fill=False, ls=(0, (4, 3)), ec=SITE, lw=1.1, zorder=2))
    ax.plot(*p, "o", ms=6.5, mfc="white", mec=BG, mew=1.2, zorder=5)
    fx0 = 0.04 + (k % 2) * 0.49 + 0.215
    fy0 = 0.705 - (k // 2) * 0.31
    fig.text(fx0, fy0 - 0.018, name, ha="center", fontsize=17, family=F_HEAD, color=INK)
    fig.text(fx0, fy0 - 0.036, f"{m['area']:,.0f} ㎡", ha="center", fontsize=17, family=F_HEAD, color=col)
    fig.text(fx0, fy0 - 0.050, f"개방 {m['open']*100:.0f}%  ·  원형도 {m['comp']:.2f}  ·  최장 시선 {m['maxsight']:.0f} m", ha="center",
             fontsize=9.5, family=F_BODY, color=INK2)
    fig.text(fx0, fy0 - 0.063, sub, ha="center", fontsize=9, family=F_BODY, color=INK3)
fig.text(0.04, 0.975, "경주에서 한 점이 보는 땅", fontsize=24, family=F_HEAD, color=INK)
fig.text(0.04, 0.957, "교차점 가시 영역 · 반경 150 m · 광선 720개 · 장애물 = 건물 + 담장 · 같은 축척(창 320 × 250 m)", fontsize=10.5, color=INK2)
fig.text(0.04, 0.012, "개방 = 가시 면적 ÷ 반경 150 m 원 면적 · 원형도 = 4πA/P² (1이면 원, 십자형일수록 0에 가까움) · "
         "출처: 국토지리정보원 연속수치지도(T2), 2026-09-28 자체 계산", fontsize=8.5, color=INK3)
MAPS.mkdir(parents=True, exist_ok=True)
fig.savefig(MAPS / "map14_경주_가시영역_6유형.png"); plt.close(fig)

# ════════════════════════════════════════════════════════
# map15 — 걷기 가시 면적 리듬
# ════════════════════════════════════════════════════════
print("routes ...")


def dijkstra(src, dst=None, allow=None, cost=None):
    dist = {src: 0.0}; prev = {}; order = []; pq = [(0.0, src)]; done = set()
    while pq:
        dd, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u); order.append(u)
        if u == dst:
            break
        for e in ADJ[u]:
            i, j, l, w = EDGES[e]
            if allow and not allow(e):
                continue
            v = j if i == u else i
            nd = dd + (cost(e) if cost else l)
            if nd < dist.get(v, 1e18):
                dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    return dist, prev, order


def path_nodes(prev, src, dst):
    out = [dst]
    while out[-1] != src:
        out.append(prev[out[-1]])
    return out[::-1]


def route_line(a_xy, b_xy, allow=None, region=None):
    """allow 를 만족하는 가로를 선호(비용 1), 아니면 비용 8 — 선호 가로가 끊겨도 최소한만 벗어난다"""
    ok = (lambda n: all(allow(e) for e in ADJ[n])) if allow else (lambda n: True)
    a = pick_node(a_xy, ok, region, 250); b = pick_node(b_xy, ok, region, 250)
    cost = (lambda e: EDGES[e][2] * (1.0 if allow(e) else 8.0)) if allow else None
    dist, prev, _ = dijkstra(a, b, None, cost)
    ln = LineString([XY[n] for n in path_nodes(prev, a, b)])
    return ln


# 화랑로(격자 틀): 폭 12 m 이상 동서 가로를 따라 서→동
R1 = route_line((218640, 360818), (219560, 360818), allow=lambda e: EDGES[e][3] >= 12)
# 황오동 골목: 폭 6 m 미만 가로만으로 남서→북동
BOX2 = box(219930, 360470, 220270, 360890)   # 부지 바로 동쪽, 빈 필지가 적은 황오동 남부 골목


def _mid(e):
    return Point((XY[EDGES[e][0]] + XY[EDGES[e][1]]) / 2)


R2 = route_line((219960, 360500), (220240, 360860), allow=lambda e: EDGES[e][3] < 5 and BOX2.contains(_mid(e)), region=HW)
# 원화로(폐선 가장자리): 구역 서측 간선을 남→북
_zc = ZONE.centroid.x
R3 = route_line((219950, 360600), (219950, 361200),
                allow=lambda e: (lambda m: m.x > _zc and 0 < ZONE.exterior.distance(m) <= 45 and not ZONE.contains(m))(_mid(e)))
ROUTES = [("화랑로 — 원도심 격자 틀", R1, GOLD), ("황오동 골목 — 세립 채움", R2, TEAL), ("부지 동쪽 가장자리 — 폐선과 황오동 사이", R3, SITE)]
series = []
for name, ln, col in ROUTES:
    L = ln.length
    ss = np.arange(0, L, 2.0)
    vals, polys = [], []
    for s in ss:
        p = ln.interpolate(s)
        poly, m = isovist((p.x, p.y))
        vals.append(m["area"]); polys.append(poly)
    v = np.array(vals)
    # 봉우리 = 교차점에서 시야가 옆으로 열리는 순간: 돌출도 ≥ max(300 ㎡, 중앙값의 30%), 간격 ≥ 8 m
    from scipy.signal import find_peaks
    pk, _ = find_peaks(v, prominence=max(250.0, 0.08 * float(np.median(v))), distance=4)
    pk = list(pk)
    gaps = np.diff(ss[pk]) if len(pk) > 1 else np.array([np.nan])
    lag = float(np.median(gaps))
    series.append(dict(name=name, line=ln, col=col, s=ss, v=v, polys=polys, peaks=pk, lag=lag, acmax=float(np.percentile(gaps, 75)) if len(pk) > 2 else float("nan")))
    print(f"  {name}: 길이 {L:.0f} m, 평균 {v.mean():.0f} ㎡ (중앙값 {np.median(v):.0f}), CV {v.std()/v.mean():.2f}, 봉우리 {len(pk)}개 ({len(pk)/L*100:.1f}/100 m), 봉우리 간격 중앙값 {lag:.0f} m")
OUT["routes"] = [{"route": s["name"], "length_m": round(s["line"].length), "mean_area": round(float(s["v"].mean())),
                  "median_area": round(float(np.median(s["v"]))),
                  "cv": round(float(s["v"].std() / s["v"].mean()), 3), "peaks": len(s["peaks"]),
                  "peaks_per_100m": round(len(s["peaks"]) / s["line"].length * 100, 2), "peak_gap_median_m": s["lag"], "peak_gap_p75_m": s["acmax"]}
                 for s in series]

fig = plt.figure(figsize=(14, 16), dpi=140)
YMAX = max(float(s_["v"].max()) for s_ in series) * 1.06
for k, s in enumerate(series):
    y0 = 0.66 - k * 0.315
    ax = fig.add_axes([0.03, y0, 0.44, 0.27])
    b = s["line"].bounds
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    half = max(b[2] - b[0], b[3] - b[1]) / 2 + 130
    win = box(cx - half, cy - half * 0.72, cx + half, cy + half * 0.72)
    draw_base(ax, win)
    if k == 2:
        ax.add_patch(MPoly(np.asarray(ZONE.exterior.coords), closed=True, fill=False, ls=(0, (4, 3)), ec=SITE, lw=1, zorder=2))
    if k == 1:
        ax.add_patch(MPoly(np.asarray(BOX2.exterior.coords), closed=True, fill=False, ls=(0, (2, 3)), ec=INK3, lw=0.8, zorder=2))
    i_max = int(np.argmax(s["v"]))
    for gg in getattr(s["polys"][i_max], "geoms", [s["polys"][i_max]]):
        ax.add_patch(MPoly(np.asarray(gg.exterior.coords), closed=True, fc=s["col"], ec=s["col"], alpha=0.55, lw=1, zorder=3))
    ax.plot(*s["line"].xy, color=s["col"], lw=2.2, zorder=4)
    for i in s["peaks"]:
        p = s["line"].interpolate(s["s"][i]); ax.plot(p.x, p.y, "o", ms=3.2, color="white", zorder=5)
    p = s["line"].interpolate(s["s"][i_max]); ax.plot(p.x, p.y, "o", ms=7, mfc="white", mec=BG, zorder=6)
    fig.text(0.50, y0 + 0.245, s["name"], fontsize=17, family=F_HEAD)
    fig.text(0.50, y0 + 0.222, f"평균 가시 면적 {s['v'].mean():,.0f} ㎡  ·  변동계수 {s['v'].std()/s['v'].mean():.2f}  ·  "
             f"봉우리 {len(s['peaks'])/s['line'].length*100:.1f}개/100 m  ·  봉우리 간격 중앙값 {s['lag']:.0f} m  ·  중앙값 {np.median(s['v']):,.0f} ㎡", fontsize=10.5, color=INK2)
    a2 = fig.add_axes([0.50, y0 + 0.02, 0.47, 0.18])
    a2.set_facecolor(BG)
    a2.fill_between(s["s"], s["v"], color=s["col"], alpha=0.28, lw=0)
    a2.plot(s["s"], s["v"], color=s["col"], lw=1.4)
    for i in s["peaks"]:
        a2.plot(s["s"][i], s["v"][i], "o", ms=3, color="white")
    a2.set_xlim(0, s["s"][-1]); a2.set_ylim(0, YMAX)
    a2.set_xlabel("걸은 거리 (m)", fontsize=9.5); a2.set_ylabel("가시 면적 (㎡)", fontsize=9.5)
    a2.grid(color="#1d2530", lw=0.6); a2.tick_params(labelsize=8.5)
    for sp in a2.spines.values():
        sp.set_color("#1d2530")
fig.text(0.03, 0.972, "걸으며 보는 땅의 리듬", fontsize=24, family=F_HEAD)
fig.text(0.03, 0.953, "2 m마다 가시 영역(반경 150 m)을 잰 값 · 세 그래프 같은 세로 축 · 흰 점 = 봉우리(시야가 옆으로 열리는 순간: 돌출도 250 ㎡ 또는 중앙값 8% 이상, 간격 8 m 이상)",
         fontsize=10.5, color=INK2)
fig.text(0.03, 0.01, "지도의 채운 면 = 그 경로에서 가시 면적이 가장 큰 지점의 가시 영역 · 출처: 국토지리정보원 연속수치지도(T2), 2026-09-28 자체 계산",
         fontsize=8.5, color=INK3)
fig.savefig(MAPS / "map15_경주_걷기_가시면적_리듬.png"); plt.close(fig)

# ════════════════════════════════════════════════════════
# map16 — 같은 축척 다익스트라 탐색 + 폐선부의 끊긴 격자 틀선
# ════════════════════════════════════════════════════════
print("dijkstra ...")
DJ = [("성건동 격자", (218450, 361300), (218900, 361700), SG, BLUE),
      ("황오동 세립 조직", (220060, 360480), (220060, 361080), HW, TEAL),
      ("동천동 회전 격자", (220400, 362000), (220850, 362400), {"4713012600"}, VIOLET),
      ("폐선 부지 가로지르기", (219470, 360990), (220070, 360990), None, SITE)]
E = json.load(open(DER / "palimpsest_evidence_20260928.json", encoding="utf-8"))
OX, OY = 218200.0, 359450.0
frame = [np.array(l) + [OX, OY] for l in E["rule_lines"]["ew"]["lines"]]
djres = []
fig = plt.figure(figsize=(14, 15.4), dpi=140)
for k, (name, a_xy, b_xy, reg, col) in enumerate(DJ):
    a = pick_node(a_xy, lambda n: DEG[n] >= 2, reg, 250)
    uvec = np.array(b_xy, float) - np.array(a_xy, float); uvec /= np.linalg.norm(uvec)
    b = pick_node(tuple(XY[a] + 600.0 * uvec), lambda n: DEG[n] >= 2, None, 120)
    dist, prev, order = dijkstra(a, b)
    settled = set(order)
    d_ab = dist[b]; eu = math.dist(XY[a], XY[b])
    pth = path_nodes(prev, a, b)
    djres.append({"case": name, "nodes_explored": len(order), "network_m": round(d_ab), "straight_m": round(eu), "detour": round(d_ab / eu, 2)})
    print(f"  {name}: 노드 {len(order)}, 망거리 {d_ab:.0f} / 직선 {eu:.0f} = {d_ab/eu:.2f}")
    mid = (XY[a] + XY[b]) / 2
    win = box(mid[0] - 700, mid[1] - 700, mid[0] + 700, mid[1] + 700)
    ax = fig.add_axes([0.03 + (k % 2) * 0.485, 0.505 - (k // 2) * 0.465, 0.455, 0.415])
    ax.set_facecolor(BG)
    segs_all, segs_exp, segs_front = [], [], []
    thr = d_ab * 0.9
    for i, j, l, w in EDGES:
        pi_, pj = XY[i], XY[j]
        if not (win.bounds[0] - 50 <= pi_[0] <= win.bounds[2] + 50 and win.bounds[1] - 50 <= pi_[1] <= win.bounds[3] + 50):
            continue
        seg = [pi_, pj]
        if i in settled and j in settled:
            (segs_front if max(dist[i], dist[j]) >= thr else segs_exp).append(seg)
        else:
            segs_all.append(seg)
    ax.add_collection(LineCollection(segs_all, colors="#2b3442", linewidths=0.55))
    ax.add_collection(LineCollection(segs_exp, colors="#8795a8", linewidths=0.8))
    ax.add_collection(LineCollection(segs_front, colors="white", linewidths=2.2))
    if name == "폐선 부지 가로지르기":
        ax.add_patch(MPoly(np.asarray(ZONE.exterior.coords), closed=True, fc=SITE, alpha=0.10, ec=SITE, lw=1.2, ls=(0, (4, 3))))
        for fl in frame:
            ax.plot(fl[:, 0], fl[:, 1], color=MAG, lw=1.0, ls=(0, (1.5, 3)), zorder=4)
    ax.plot([XY[n][0] for n in pth], [XY[n][1] for n in pth], color=col, lw=2.6, zorder=5)
    for lab, n in (("A", a), ("B", b)):
        ax.plot(*XY[n], "o", ms=15, mfc=BG, mec=col, mew=2, zorder=6)
        ax.text(*XY[n], lab, ha="center", va="center", fontsize=9, family=F_HEAD, color=col, zorder=7)
    b_ = win.bounds
    ax.set_xlim(b_[0], b_[2]); ax.set_ylim(b_[1], b_[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color("#1d2530")
    ax.text(0.03, 0.965, name, transform=ax.transAxes, fontsize=16, family=F_HEAD, va="top")
    ax.text(0.03, 0.905, f"{len(order):,} 노드 탐색", transform=ax.transAxes, fontsize=15, family=F_HEAD, color=col, va="top")
    ax.text(0.03, 0.85, f"망거리 {d_ab:,.0f} m ÷ 직선 {eu:,.0f} m = 우회 {d_ab/eu:.2f}배", transform=ax.transAxes, fontsize=9.5, color=INK2, va="top")
OUT["dijkstra"] = djres
fig.text(0.03, 0.972, "같은 거리, 다른 탐색", fontsize=24, family=F_HEAD)
fig.text(0.03, 0.953, "다익스트라 · A에서 모든 방향으로 번지다가 B에 닿으면 멈춤 · 같은 1.4 km 창 · A–B 직선 약 600 m · 흰 선 = 마지막 10% 탐색 전선 · 색 선 = 최단 경로",
         fontsize=10.5, color=INK2)
fig.text(0.03, 0.012, "자홍 점선(오른쪽 아래) = 동서 가로의 147.5 m 실측 규칙선 · 출처: 국토지리정보원 연속수치지도(T2), 2026-09-28 자체 계산",
         fontsize=8.5, color=INK3)
fig.savefig(MAPS / "map16_경주_다익스트라_탐색.png"); plt.close(fig)

# 폐선부에서 끊긴 틀선: 규칙선 중 구역을 지나는 선의 서·동 양쪽에 같은 선을 따르는 동서 가로가 있는가
rot = math.radians(90 - AX)
c, s_ = math.cos(rot), math.sin(rot)
ph, T = E["rule_lines"]["ew"]["phase_m"], E["rule_lines"]["ew"]["T"]
zb = ZONE.bounds
broken = []
for kk in range(-4000, 4000):
    v = ph + kk * T
    ymid = (v - ((zb[0] + zb[2]) / 2) * s_) / c
    if not (zb[1] - 20 <= ymid <= zb[3] + 20):
        continue
    ln = LineString([(zb[0] - 300, (v - (zb[0] - 300) * s_) / c), (zb[2] + 300, (v - (zb[2] + 300) * s_) / c)])
    band = ln.buffer(6)
    west = east = 0.0
    for gg, w in pieces:
        if gg.intersects(band):
            th = math.degrees(math.atan2(gg.coords[-1][1] - gg.coords[0][1], gg.coords[-1][0] - gg.coords[0][0])) % 180
            if d90(th, AX + 90) > 8 and d90(th, AX) > 8:
                continue
            part = gg.intersection(band)
            if part.is_empty:
                continue
            if part.centroid.x < zb[0] + 20:
                west += part.length
            elif part.centroid.x > zb[2] - 20:
                east += part.length
    inside = ln.intersection(ZONE).length
    broken.append({"y_5187": round(ymid), "street_len_west_m": round(west), "street_len_east_m": round(east), "len_inside_zone_m": round(inside)})
OUT["frame_lines_at_site"] = broken
print("틀선:", broken)

# ════════════════════════════════════════════════════════
# map13 — 층 분해 스택
# ════════════════════════════════════════════════════════
print("stack ...")
xb0, yb0, xb1, yb1 = EXT.bounds
WX, WY = xb1 - xb0, yb1 - yb0
S = 1 / 1000.0                       # km 단위로


def iso(x, y, z=0.0):
    u, v = (x - xb0) * S, (y - yb0) * S
    return (u - v) * math.cos(math.radians(IA)), (u + v) * math.sin(math.radians(IA)) + z


def iso_arr(a, z=0.0):
    u, v = (a[:, 0] - xb0) * S, (a[:, 1] - yb0) * S
    return np.c_[(u - v) * math.cos(math.radians(IA)), (u + v) * math.sin(math.radians(IA)) + z]


IA = 20.0     # 투영각 — 판이 겹치지 않게 평평하게
GAP = 2.75
PLATES = ["지형", "물길 + 비움", "규제", "가로 체계", "3D 매싱"]
ZL = {nm: i * GAP for i, nm in enumerate(PLATES)}
fig = plt.figure(figsize=(12.5, 16.5), dpi=150)
ax = fig.add_axes([0.0, 0.02, 0.66, 0.95]); ax.set_facecolor(BG); ax.axis("off")


def plate(z, face="#141a22"):
    corners = np.array([[xb0, yb0], [xb1, yb0], [xb1, yb1], [xb0, yb1]])
    top = iso_arr(corners, z)
    th = 0.09
    for a_, b_ in ((0, 1), (1, 2)):   # 앞쪽 두 옆면 (x+ / y− 방향)
        pass
    left = np.array([top[0], top[1], top[1] - [0, th], top[0] - [0, th]])
    right = np.array([top[1], top[2], top[2] - [0, th], top[1] - [0, th]])
    front = np.array([top[3], top[0], top[0] - [0, th], top[3] - [0, th]])
    for side, cc in ((left, "#1c232d"), (front, "#232b36")):
        ax.add_patch(MPoly(side, closed=True, fc=cc, ec="none", zorder=z * 10 + 0.5))
    ax.add_patch(MPoly(top, closed=True, fc=face, ec="#2a3340", lw=0.6, zorder=z * 10 + 1))
    return top


def draw_polys(geoms, z, fc, ec="none", lw=0.0, alpha=1.0, zo=2):
    pp = []
    for g in geoms:
        g = g.intersection(EXT)
        for gg in getattr(g, "geoms", [g]):
            if gg.geom_type == "Polygon" and not gg.is_empty:
                pp.append(iso_arr(np.asarray(gg.exterior.coords), z))
    ax.add_collection(PolyCollection(pp, facecolors=fc, edgecolors=ec, linewidths=lw, alpha=alpha, zorder=z * 10 + zo))


def draw_lines(lines, z, col, lw, alpha=1.0, zo=3):
    ll = [iso_arr(np.asarray(l), z) for l in lines]
    ax.add_collection(LineCollection(ll, colors=col, linewidths=lw, alpha=alpha, zorder=z * 10 + zo))


# 1 지형: 등고선·표고점 → 격자 보간 → 음영
pts, zs = [], []
for g, a in read("N3L_F0010000"):
    zc = float(a.get("cont") or 0)
    for gg in getattr(g, "geoms", [g]):
        L = gg.length
        for sdist in np.arange(0, L, 12.0):
            p = gg.interpolate(sdist); pts.append((p.x, p.y)); zs.append(zc)
for g, a in read("N3P_F0020000"):
    pts.append((g.x, g.y)); zs.append(float(a.get("nume") or 0))
pts, zs = np.array(pts), np.array(zs)
GX, GYY = np.meshgrid(np.arange(xb0, xb1, 15.0), np.arange(yb0, yb1, 15.0))
DEM = griddata(pts, zs, (GX, GYY), method="linear")
DEM = np.where(np.isnan(DEM), griddata(pts, zs, (GX, GYY), method="nearest"), DEM)
dzdy, dzdx = np.gradient(DEM, 15.0)
shade = np.clip(0.5 + (dzdx * -0.7 + dzdy * 0.7) * 0.8, 0, 1)
z0 = ZL["지형"]; plate(z0)
lo, hi = np.nanpercentile(DEM, 2), np.nanpercentile(DEM, 99)
cells = []
cols = []
cm_lo, cm_hi = np.array([0.93, 0.91, 0.72]), np.array([0.55, 0.33, 0.20])
step = 2
for i in range(0, DEM.shape[0] - step, step):
    for j in range(0, DEM.shape[1] - step, step):
        x0_, y0_ = GX[i, j], GYY[i, j]; x1_, y1_ = GX[i, j + step], GYY[i + step, j]
        t = np.clip((DEM[i, j] - lo) / (hi - lo), 0, 1)
        c_ = (cm_lo * (1 - t) + cm_hi * t) * (0.72 + 0.28 * shade[i, j])
        cells.append(iso_arr(np.array([[x0_, y0_], [x1_, y0_], [x1_, y1_], [x0_, y1_]]), z0)); cols.append(np.clip(c_, 0, 1))
ax.add_collection(PolyCollection(cells, facecolors=cols, edgecolors=cols, linewidths=0.35, antialiased=False, zorder=z0 * 10 + 2))
draw_polys([WATER], z0, "#8fb4d6", zo=3)

# 2 물길 + 비움: 하천·공원·유적 구역
z1 = ZL["물길 + 비움"]; plate(z1)
draw_polys([WATER], z1, "#4f8fcf", zo=2)
parks = [to5187(shape(f["geometry"]), T47) for f in json.load(open(PROC / "parks_upis_4326.geojson", encoding="utf-8"))["features"] if f["geometry"]]
draw_polys(parks, z1, "#2f6b4f", zo=2)
draw_polys([g for g, _ in HERIT], z1, GOLD, alpha=0.85, zo=3)

# 3 규제: V-World 법정 경계
z2 = ZL["규제"]; plate(z2)
REGC = {"국가지정문화유산구역": GOLD, "문화유산 보호구역": "#b98a2e", "역사문화환경보존지역": "#7d5a2a",
        "고도지구": VIOLET, "역사문화환경보호지구": "#c26ca3", "지구단위계획구역": BLUE}
regs = defaultdict(list)
for f in json.load(open(PROC / "reg_areas_4326.geojson", encoding="utf-8"))["features"]:
    r_ = f["properties"].get("reg")
    if r_ in REGC and f["geometry"]:
        regs[r_].append(to5187(shape(f["geometry"]), T47).buffer(0))
for r_ in ["역사문화환경보존지역", "고도지구", "역사문화환경보호지구", "지구단위계획구역", "문화유산 보호구역", "국가지정문화유산구역"]:
    alpha = 0.55 if r_ in ("역사문화환경보존지역", "고도지구", "역사문화환경보호지구") else 0.9
    if r_ == "지구단위계획구역":
        draw_polys(regs[r_], z2, "none", ec=BLUE, lw=0.6, zo=4)
    else:
        draw_polys(regs[r_], z2, REGC[r_], alpha=alpha, zo=3)

# 4 가로 체계 + 철도 + 부지
z3 = ZL["가로 체계"]; plate(z3)
lines_by = defaultdict(list)
for gg, w in pieces:
    cs = np.asarray(gg.coords)
    th = math.degrees(math.atan2(cs[-1][1] - cs[0][1], cs[-1][0] - cs[0][0])) % 180
    sysk = "grid" if d90(th, AX) <= 7.5 else "diag" if (abs(((th - 42) + 90) % 180 - 90) <= 7.5 or abs(((th - 148) + 90) % 180 - 90) <= 7.5) else "other"
    lines_by[(sysk, "major" if w >= 15 else "minor")].append(cs)
draw_lines(lines_by[("other", "minor")] + lines_by[("other", "major")], z3, "#5b6675", 0.35)
draw_lines(lines_by[("diag", "minor")], z3, TEAL, 0.45); draw_lines(lines_by[("diag", "major")], z3, TEAL, 1.1)
draw_lines(lines_by[("grid", "minor")], z3, "#cfd6df", 0.45); draw_lines(lines_by[("grid", "major")], z3, "white", 1.2)
draw_lines([np.asarray(g.coords) for g in RAILCL for g in getattr(g, "geoms", [g])], z3, SITE, 1.3, zo=4)
draw_polys([ZONE], z3, "none", ec=SITE, lw=1.4, zo=5)

# 5 3D 매싱: 건물(층수×3.5 m, 수직 3배 과장) + 고분(닫힌 등고선 적층)
z4 = ZL["3D 매싱"]; plate(z4)
VEX = 3.0 * S
recs = []
for g, fl, _ in BLD:
    for gg in getattr(g, "geoms", [g]):
        if gg.is_empty:
            continue
        base = np.asarray(gg.exterior.coords)
        cz = (base[:, 0].mean() - xb0) + (base[:, 1].mean() - yb0)
        recs.append((cz, base, fl))
recs.sort(key=lambda t: -t[0])   # 뒤(멀리)부터
walls_, roofs_, rcol = [], [], []
for cz, base, fl in recs:
    h = fl * 3.5 * VEX
    b2 = iso_arr(base, z4); r2 = b2 + [0, h]
    hull = MultiPolygon([Polygon(b2), Polygon(r2)]).convex_hull if len(b2) >= 4 else None
    if hull is not None and hull.geom_type == "Polygon":
        walls_.append(np.asarray(hull.exterior.coords))
        roofs_.append(r2)
        rcol.append("#f4f6f8" if fl >= 6 else "#b8c1cc" if fl >= 3 else "#6f7a88")
# 고분: 원도심 45–60 m 닫힌 등고선 중 작은 고리(면적 150–20,000 ㎡)
rings = []
for g, a in read("N3L_F0010000"):
    zc = float(a.get("cont") or 0)
    for gg in getattr(g, "geoms", [g]):
        if gg.is_ring and 40 <= zc <= 70:
            pg = Polygon(gg.coords)
            if 150 <= pg.area <= 20000:
                rings.append((zc, pg))
mounds = []
for zc, pg in rings:
    inner = [z_ for z_, p2 in rings if p2.within(pg) and z_ > zc]
    base_z = zc - 5
    mounds.append((zc, pg, base_z))
outer_rings = [pg for zc, pg, _ in mounds if not any(pg.within(p2) for z2_, p2, _ in mounds if p2 is not pg)]
tumuli_n = len(outer_rings)
_hz = unary_union([g for g, _ in HERIT] + [to5187(shape(f["geometry"]), T47).buffer(0) for f in json.load(open(PROC / "reg_areas_4326.geojson", encoding="utf-8"))["features"]
                   if f["geometry"] and f["properties"].get("reg") in ("국가지정문화유산구역", "문화유산 보호구역")])
tumuli_in_herit = sum(1 for pg in outer_rings if pg.representative_point().within(_hz))
print(f"  닫힌 등고선 고리 {tumuli_n}개 중 사적·문화유산구역 안 {tumuli_in_herit}개")
ax.add_collection(PolyCollection(walls_, facecolors="#3a4452", edgecolors="none", zorder=z4 * 10 + 2))
ax.add_collection(PolyCollection(roofs_, facecolors=rcol, edgecolors="none", zorder=z4 * 10 + 3))
# 고분: 가장 바깥 고리의 기준 표고부터 각 고리를 (표고−기준)×과장만큼 올려 쌓기
outer = {}
for zc, pg, _ in mounds:
    owner = min([(p2.area, p2, z2_) for z2_, p2, _ in mounds if pg.within(p2) or p2 is pg], key=lambda t: -t[0])
    outer.setdefault(id(owner[1]), (owner[2], []))[1].append((zc, pg))
for base_z, lst in outer.values():
    for zc, pg in sorted(lst, key=lambda t: t[0]):
        lift = (zc - base_z + 5) * VEX
        pp = iso_arr(np.asarray(pg.exterior.coords), z4) + [0, lift]
        ax.add_patch(MPoly(pp, closed=True, fc=GOLD, ec="#7a5b16", lw=0.4, alpha=0.95, zorder=z4 * 10 + 4))

# 점선 연결선 + 범례
corners = np.array([[xb0, yb0], [xb1, yb0], [xb1, yb1], [xb0, yb1]])
for c_ in corners[[0, 1, 3]]:
    p0 = iso(*c_, ZL["지형"]); p1 = iso(*c_, ZL["3D 매싱"])
    ax.plot([p0[0], p1[0]], [p0[1] - 0.09, p1[1]], color="#9aa5b3", lw=0.8, ls=(0, (3, 3)), zorder=0)
allc = np.vstack([iso_arr(corners, z) for z in ZL.values()])
ax.set_xlim(allc[:, 0].min() - 0.15, allc[:, 0].max() + 0.15); ax.set_ylim(allc[:, 1].min() - 0.3, allc[:, 1].max() + 0.9)
ax.set_aspect("equal")
LEG = {
    "3D 매싱": [("#6f7a88", "1–2층 (87%)"), ("#b8c1cc", "3–5층"), ("#f4f6f8", "6층 이상"), (GOLD, "고분 · 닫힌 등고선 적층")],
    "가로 체계": [("white", "주 격자 N0.8°E (연장 57%)"), (TEAL, "사선 체계 (동천동·북천 변)"), ("#5b6675", "기타"), (SITE, "철도 · 구경주역 구역")],
    "규제": [(GOLD, "국가지정문화유산구역"), ("#b98a2e", "문화유산 보호구역"), ("#7d5a2a", "역사문화환경 보존지역"), (VIOLET, "고도지구"), (BLUE, "지구단위계획구역(선)")],
    "물길 + 비움": [("#4f8fcf", "하천 (북천·서천·남천)"), ("#2f6b4f", "도시계획 공원·녹지"), (GOLD, "사적·유적 구역")],
    "지형": [(tuple(cm_lo), f"낮은 땅 {lo:.0f} m"), (tuple(cm_hi), f"높은 땅 {hi:.0f} m"), ("#8fb4d6", "물")],
}
TITLES = {"3D 매싱": "3D 매싱", "가로 체계": "가로 방위 체계", "규제": "규제 — 땅의 쓰임을 정하는 것", "물길 + 비움": "물길 + 비움", "지형": "지형"}
for nm, z in ZL.items():
    yfig = 0.075 + (z / (GAP * (len(PLATES) - 1))) * 0.80
    fig.text(0.67, yfig + 0.06, TITLES[nm], fontsize=15, family=F_HEAD, color=INK)
    for i, (cc, lab) in enumerate(LEG[nm]):
        fig.patches.append(plt.Rectangle((0.67, yfig + 0.038 - i * 0.02), 0.014, 0.011, transform=fig.transFigure, fc=cc, ec="none"))
        fig.text(0.69, yfig + 0.039 - i * 0.02, lab, fontsize=10.5, color=INK2, va="bottom")
fig.text(0.03, 0.975, "경주 원도심, 다섯 겹", fontsize=24, family=F_HEAD)
fig.text(0.03, 0.958, f"모델링 범위 {WX/1000:.2f} × {WY/1000:.2f} km · 평행 투영 · 매싱 수직 3배 과장 · 닫힌 등고선 고리 {tumuli_n}개(그중 {tumuli_in_herit}개가 사적·문화유산구역 안)", fontsize=10.5, color=INK2)
fig.text(0.03, 0.012, "출처: 국토지리정보원 연속수치지도(T2) · V-World 법정 규제 경계(T1) · UPIS 공원(T1) · 2026-09-28 자체 계산", fontsize=8.5, color=INK3)
fig.savefig(MAPS / "map13_경주_층위스택.png"); plt.close(fig)
OUT["stack"] = {"extent_km": [round(WX / 1000, 2), round(WY / 1000, 2)], "dem_p2_p99_m": [round(float(lo), 1), round(float(hi), 1)],
               "closed_contour_rings": tumuli_n, "rings_in_heritage": tumuli_in_herit}

json.dump(OUT, open(DER / "gj_reading_20260928.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved maps 13–16 and", DER / "gj_reading_20260928.json")
