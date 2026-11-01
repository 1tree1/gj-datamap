"""최종콘타모델_v2 모델링 범위 진단도 — 분석 신뢰 반경(가장자리 효과) + 폐선 횡단 현황 + 동서 우회율.

입력: 대지/(B020)연속수치지도_202609132098 (NGII, EPSG:5179) — 3dm 솔리드는 1:2000 축소 제작본이라 쓰지 않는다.
      archive/C_data/processed/gosi2026-8_zone_5187.geojson (고시 제2026-8호 구역계)
출력: work/maps/map10_모델범위_분석신뢰반경_철도횡단.png
처리 좌표계: 읽자마자 EPSG:5187 로 변환 (CLAUDE.md §1).
"""
import json
import math
import os
import warnings
from pathlib import Path

import numpy as np
import shapefile  # pyshp
from pyproj import Transformer
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point, box, shape
from shapely.ops import nearest_points
from shapely.ops import transform as shp_transform
from shapely.ops import unary_union

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "대지" / "(B020)연속수치지도_202609132098"
ZONE = ROOT / "archive" / "C_data" / "processed" / "gosi2026-8_zone_5187.geojson"
OUT = ROOT / "work" / "maps" / "map10_모델범위_분석신뢰반경_철도횡단.png"

T57 = Transformer.from_crs("EPSG:5179", "EPSG:5187", always_xy=True)


def to5187(g):
    return shp_transform(lambda x, y, z=None: T57.transform(x, y), g)


def fix_text(v):
    """수치지도 DBF 문자열은 cp949 바이트가 latin-1 로 읽힌 뒤 UTF-8 로 저장된 이중 인코딩."""
    if isinstance(v, str):
        try:
            return v.encode("latin-1").decode("cp949").strip()
        except Exception:
            return v.strip()
    return v


def read(layer):
    r = shapefile.Reader(str(SRC / layer))
    flds = [f[0] for f in r.fields[1:]]
    return [(to5187(shape(s.shape.__geo_interface__)), {k: fix_text(v) for k, v in zip(flds, s.record)})
            for s in r.iterShapeRecords()]


# ── 입력 ─────────────────────────────────────────────
zone = shape(json.load(open(ZONE, encoding="utf-8"))["features"][0]["geometry"])  # 이미 5187
bldg = read("N3A_B0010000")
road = read("N3L_A0020000")
rail_poly = unary_union([g for g, _ in read("N3A_A0160024")])
rail_cl = unary_union([g for g, _ in read("N3L_A0171119")])
overpass = read("N3A_A0063321")
landmarks = [(g, a) for g, a in read("N3P_H0040000") if a.get("type") == "PNT010"]

# 연속수치지도 범위는 5179 축정렬 사각형 → 5187 에서는 약 0.9° 회전한 사각형 (모서리 최대 ~50 m 차이)
_r = shapefile.Reader(str(SRC / "N3L_A0020000")).bbox
ext_box = to5187(box(*_r).segmentize(20))
cz = zone.centroid
s2 = cz.buffer(1000)

# ── 도로×철도 횡단 지점 ────────────────────────────────
pts = []
for g, a in road:
    if g.intersects(rail_cl):
        x = g.intersection(rail_cl)
        for p in getattr(x, "geoms", [x]):
            if p.geom_type == "Point":
                pts.append((p.x, p.y, float(a.get("rvwd") or 0)))
pts.sort(key=lambda t: t[1])
xings = []
for p in pts:
    if xings and abs(p[1] - xings[-1][-1][1]) < 30 and abs(p[0] - xings[-1][-1][0]) < 60:
        xings[-1].append(p)
    else:
        xings.append([p])
xings = [(np.mean([p[0] for p in g]), np.mean([p[1] for p in g]), max(p[2] for p in g)) for g in xings]
# 철도 선형이 끊긴 구간(도로 면에 의해 절단된 건널목) — 구역 남단
parts = list(getattr(rail_poly, "geoms", [rail_poly]))

# ── 동서 우회율 (도로중심선 그래프, 육교 미포함) ─────────────
key, xy, I, J, W = {}, [], [], [], []


def nid(p):
    k = (round(p[0] * 2), round(p[1] * 2))
    if k not in key:
        key[k] = len(xy)
        xy.append(p)
    return key[k]


for g, _ in road:
    for gg in getattr(g, "geoms", [g]):
        cs = list(gg.coords)
        for p, q in zip(cs[:-1], cs[1:]):
            i, j = nid(p), nid(q)
            if i != j:
                d = math.hypot(p[0] - q[0], p[1] - q[1])
                I += [i, j]; J += [j, i]; W += [d, d]
xy = np.array(xy)
G = coo_matrix((W, (I, J)), shape=(len(xy), len(xy))).tocsr()
_, lab = connected_components(G, directed=False)
keep = np.where(lab == np.bincount(lab).argmax())[0]
tree = cKDTree(xy[keep])
zb = zone.bounds
prof = []
for y in np.arange(zb[1] - 250, zb[3] + 250.1, 50):
    seg = LineString([(zb[0] - 900, y), (zb[2] + 900, y)]).intersection(rail_poly)
    if seg.is_empty:
        continue
    xs = [c[0] for s in getattr(seg, "geoms", [seg]) for c in s.coords]
    _, iw = tree.query((min(xs) - 60, y))
    _, ie = tree.query((max(xs) + 60, y))
    a, b = keep[iw], keep[ie]
    net = dijkstra(G, indices=a)[b]
    eu = float(np.hypot(*(xy[a] - xy[b])))
    prof.append((y, net / eu))

# ── 그림 ─────────────────────────────────────────────
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
fig = plt.figure(figsize=(16, 11), dpi=150)
ax = fig.add_axes([0.02, 0.04, 0.66, 0.9])
ax2 = fig.add_axes([0.745, 0.47, 0.23, 0.43])

polys = []
for g, _ in bldg:
    for gg in getattr(g, "geoms", [g]):
        polys.append(np.asarray(gg.exterior.coords))
ax.add_collection(PolyCollection(polys, facecolor="#bdbdbd", edgecolor="none", zorder=1))
segs = [np.asarray(gg.coords) for g, _ in road for gg in getattr(g, "geoms", [g])]
ax.add_collection(LineCollection(segs, colors="#9e9e9e", linewidths=0.25, zorder=2))
for p in parts:
    ax.fill(*p.exterior.xy, facecolor="#e53935", alpha=0.35, edgecolor="#b71c1c", lw=0.6, zorder=3)
ax.plot(*zone.exterior.xy, color="#0d47a1", lw=2.0, zorder=5)
ax.plot(*s2.exterior.xy, color="#0d47a1", lw=1.0, ls=(0, (6, 3)), zorder=5)

# 가장자리 효과: 범위를 R 만큼 안으로 줄인 영역 = 반경 R 지표를 믿을 수 있는 계산점 영역
for R, c in ((400, "#2e7d32"), (800, "#f9a825"), (1200, "#6a1b9a")):
    core = ext_box.buffer(-R, join_style=2)
    if not core.is_empty:
        ax.plot(*core.exterior.xy, color=c, lw=1.4, ls="--", zorder=6)
        bx = core.bounds
        ax.text(bx[0] + 25, bx[3] - 25, f"R{R} 신뢰 경계", color=c, fontsize=9, fontweight="bold", va="top", zorder=7,
                bbox=dict(facecolor="white", edgecolor=c, lw=0.6, pad=1.5))
ax.plot(*ext_box.exterior.xy, color="#212121", lw=1.2, zorder=6)

for x, y, w in xings:
    ax.plot(x, y, marker="o", ms=6 + w / 4, mfc="white", mec="#b71c1c", mew=1.6, zorder=8)
if len(parts) >= 2:
    pa, pb = nearest_points(parts[0], parts[1])
    gx, gy = (pa.x + pb.x) / 2, (pa.y + pb.y) / 2
    ax.plot(gx, gy, marker="s", ms=10, mfc="white", mec="#b71c1c", mew=1.8, zorder=8)
    ax.annotate("철도 선형 단절 = 도로 횡단\n(구역 남단, 원효로 추정)", (gx, gy), xytext=(14, -18), textcoords="offset points",
                fontsize=8, zorder=9, bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1))
for g, a in overpass:
    c = g.centroid
    ax.plot(c.x, c.y, marker="^", ms=9, mfc="#ffeb3b", mec="#212121", zorder=9)
    ax.annotate(f"육교 폭 {a.get('widt')} m", (c.x, c.y), xytext=(12, -4), textcoords="offset points", fontsize=8.5, zorder=9)
seen = set()
for g, a in landmarks:
    nm = (a.get("name") or "").split("(")[0]
    if nm in seen:
        continue
    seen.add(nm)
    if any(k in nm for k in ("첨성대", "대릉원", "미추왕릉", "황룡사지", "탈해왕릉", "전랑지", "황오동고분", "황성동고분")):
        ax.plot(g.x, g.y, marker="*", ms=8, color="#4e342e", zorder=8)
        ax.annotate(nm.replace("경주", ""), (g.x, g.y), xytext=(5, 3), textcoords="offset points", fontsize=7.5, color="#4e342e", zorder=8)

sx, sy = ext_box.bounds[0] + 120, ext_box.bounds[1] + 110
ax.plot([sx, sx + 500], [sy, sy], color="#212121", lw=3, zorder=9)
ax.text(sx + 250, sy + 30, "500 m", ha="center", fontsize=8.5, zorder=9)
ax.set_xlim(ext_box.bounds[0] - 60, ext_box.bounds[2] + 60)
ax.set_ylim(ext_box.bounds[1] - 60, ext_box.bounds[3] + 60)
ax.set_aspect("equal")
ax.tick_params(labelsize=7)
ax.set_title("최종콘타모델_v2 모델링 범위(실좌표 3,427×3,226 m, 11.06㎢) — 분석 신뢰 반경과 폐선 횡단 현황  [EPSG:5187]", fontsize=11.5, loc="left")

ys = [p[0] for p in prof]
ax2.plot([p[1] for p in prof], ys, color="#b71c1c", lw=1.6, marker="o", ms=3)
ax2.axhspan(zb[1], zb[3], color="#0d47a1", alpha=0.08)
ax2.axvline(1.0, color="#616161", lw=0.8)
for x, y, w in xings:
    if zb[1] - 260 <= y <= zb[3] + 260:
        ax2.axhline(y, color="#b71c1c", lw=0.6, ls=":")
for g, _ in overpass:
    ax2.axhline(g.centroid.y, color="#f9a825", lw=1.0, ls="--")
ax2.set_xlabel("동서 우회율 (도로망 거리 / 직선거리)", fontsize=9)
ax2.set_ylabel("북좌표 y (m, EPSG:5187)", fontsize=9)
ax2.set_title("폐선부 양측 60 m 지점 간 우회율\n(도로중심선 기준, 육교 미포함)", fontsize=9.5)
ax2.tick_params(labelsize=7.5)
ax2.set_ylim(zb[1] - 280, zb[3] + 280)

note = ("회색 = 건물 23,579동\n"
        "선 = 도로중심선 10,617개(212.4 km)\n"
        "빨강 면 = 철도경계(동해남부선)\n"
        "흰 원 = 도로×철도중심선 교차(원 크기 ∝ 도로폭)\n"
        "흰 네모 = 철도 선형이 끊긴 도로 횡단\n"
        "노란 삼각 = 육교(A006)\n"
        "파란 실선 = 고시 제2026-8호 지구단위계획구역\n"
        "파란 점선 = 구역 중심 반경 1 km (S2)\n"
        "색 점선 사각형 = 범위를 R 만큼 안으로 줄인 영역.\n"
        "  이 안의 계산점만 반경 R 지표를\n"
        "  가장자리 효과 없이 계산할 수 있다.\n\n"
        "출처: 국토지리정보원 연속수치지도\n"
        "(2026-09-13 취득, T2), 경주시 고시 제2026-8호(T1).\n"
        "우회율은 예비치(육교·건널목 현장 확인 전).")
fig.text(0.745, 0.03, note, fontsize=8, va="bottom", linespacing=1.45)
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=150)
# 리포트 카드용 수치 (gj-datamap '도시 조직' 그룹)
_zb = zone.bounds
_ext_c = ext_box.exterior
json.dump({
    "zone_y": [round(_zb[1]), round(_zb[3])],
    "crossings": [{"x": round(x), "y": round(y), "width_m": w} for x, y, w in xings],
    "rail_gap": ({"x": round((nearest_points(parts[0], parts[1])[0].x + nearest_points(parts[0], parts[1])[1].x) / 2),
                  "y": round((nearest_points(parts[0], parts[1])[0].y + nearest_points(parts[0], parts[1])[1].y) / 2)} if len(parts) >= 2 else None),
    "overpass": [{"x": round(g.centroid.x), "y": round(g.centroid.y), "width_m": a.get("widt"), "length_m": a.get("leng")} for g, a in overpass],
    "detour_profile": [{"y": round(float(y)), "ratio": round(float(r), 2)} for y, r in prof],
    "margin_zone_to_extent_m": round(min(_ext_c.distance(Point(p)) for p in zone.exterior.coords)),
    "margin_s2_to_extent_m": round(_ext_c.distance(cz) - 1000),
}, open(ROOT / "archive" / "90_derived" / "extent_diagnosis_20260928.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
print("횡단 지점(5187):", [(round(x), round(y), w) for x, y, w in xings])
print("우회율:", [(round(y), round(r, 2)) for y, r in prof])
