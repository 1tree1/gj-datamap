"""구경주역 지구단위계획구역 경계 바깥의 '스케일 프로파일' — 방향(동·서·남·북) × 경계로부터 거리.

무엇을 재나 (부지 안으로 이어받을 기존 경주의 결):
  가로  — 도로폭(길이가중), 교차 간격(분기점~분기점 링크 길이), 막다른 끝점 밀도
  필지  — 대(垈) 필지 면적, 간구(최소외접사각형 짧은 변)·깊이(긴 변) 대리값
  건물  — 바닥면적, 건물 길이(최소외접사각형 긴 변), 층수 구성
  단면  — 중심선에서 좌우로 쏜 선이 처음 만나는 건물 면 사이 거리(W)와 H/W (H = 층수 × 3.5 m)
  밀도  — 순대지(띠 면적 − 도로 면 − 하천 면) 기준 GSI·FSI·L

입력: 대지/(B020)연속수치지도_202609132098 (NGII, EPSG:5179 → 읽자마자 5187)
      archive/C_data/processed/gosi2026-8_zone_5187.geojson (고시 제2026-8호 구역계, T1)
      archive/C_data/processed/parcels_bldg_4326.geojson (V-World 연속지적, 지목은 jibun 끝 글자)
출력: archive/90_derived/edge_scale_profile_20260928.csv  (방향 × 거리띠 요약)
      archive/90_derived/edge_scale_curve_20260928.csv    (방향 × 50 m 단위 곡선)
      work/maps/map11_경계띠_스케일프로파일.png
"""
import csv
import json
import math
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
import shapefile
import shapely
from pyproj import Transformer
from shapely.geometry import LineString, Point, shape
from shapely.ops import transform as shp_transform
from shapely.ops import unary_union
from shapely.strtree import STRtree

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "대지" / "(B020)연속수치지도_202609132098"
PROC = ROOT / "archive" / "C_data" / "processed"
DER = ROOT / "archive" / "90_derived"
OUT_SUM = DER / "edge_scale_profile_20260928.csv"
OUT_CUR = DER / "edge_scale_curve_20260928.csv"
OUT_FIG = ROOT / "work" / "maps" / "map11_경계띠_스케일프로파일.png"

T57 = Transformer.from_crs("EPSG:5179", "EPSG:5187", always_xy=True)
T47 = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True)
FLOOR_H = 3.5          # 층고 가정 (m)
RAY = 30.0             # 가로 단면 탐색 거리 (m)
DMAX = 400.0           # 경계 바깥 분석 폭 (m)
BANDS = [(0, 150, "경계 인접 0–150 m"), (150, 400, "배후 150–400 m")]
BINS = [0, 50, 100, 150, 200, 300, 400]
SIDES = ["서", "동", "북", "남"]


def to5187(g, t=T57):
    return shp_transform(lambda x, y, z=None: t.transform(x, y), g)


def read(layer):
    r = shapefile.Reader(str(SRC / layer))
    flds = [f[0] for f in r.fields[1:]]
    return [(to5187(shape(s.shape.__geo_interface__)), dict(zip(flds, s.record))) for s in r.iterShapeRecords()]


zone = shape(json.load(open(PROC / "gosi2026-8_zone_5187.geojson", encoding="utf-8"))["features"][0]["geometry"]).buffer(0)
bnd = zone.exterior
roi = zone.buffer(DMAX).difference(zone)


def locate(p):
    """구역 밖 점의 (경계거리, 방향). 방향 = 가장 가까운 경계점에서 점으로 향하는 벡터의 방위."""
    d = zone.distance(p)
    if d <= 0 or d > DMAX:
        return None, None
    q = bnd.interpolate(bnd.project(p))
    a = math.degrees(math.atan2(p.y - q.y, p.x - q.x)) % 360
    side = "동" if (a < 45 or a >= 315) else "북" if a < 135 else "서" if a < 225 else "남"
    return d, side


def band_of(d):
    for lo, hi, nm in BANDS:
        if lo <= d < hi:
            return nm
    return None


def bin_of(d):
    for lo, hi in zip(BINS[:-1], BINS[1:]):
        if lo <= d < hi:
            return (lo + hi) / 2
    return None


def pct(a, q):
    a = [v for v in a if v is not None and np.isfinite(v)]
    return float(np.percentile(a, q)) if a else float("nan")


def wpct(vals, wts, q):
    """길이가중 분위수"""
    if not vals:
        return float("nan")
    o = np.argsort(vals); v = np.asarray(vals)[o]; w = np.asarray(wts)[o]
    c = np.cumsum(w) / w.sum()
    return float(v[np.searchsorted(c, q / 100.0)])


def mrr_sides(g):
    r = g.minimum_rotated_rectangle
    cs = list(r.exterior.coords)
    a = math.dist(cs[0], cs[1]); b = math.dist(cs[1], cs[2])
    return max(a, b), min(a, b)


# ── 건물 ───────────────────────────────────────────────
roi_bb = roi.bounds
B = []
for g, a in read("N3A_B0010000"):
    c = g.centroid
    if not (roi_bb[0] - 50 <= c.x <= roi_bb[2] + 50 and roi_bb[1] - 50 <= c.y <= roi_bb[3] + 50):
        continue
    fl = int(a.get("nmly") or 1) or 1
    B.append((g, fl))
btree = STRtree([g for g, _ in B])
brec = []
for g, fl in B:
    d, s = locate(g.centroid)
    if d is None:
        continue
    L, W = mrr_sides(g)
    brec.append(dict(d=d, side=s, fp=g.area, blen=L, bwid=W, fl=fl))

# ── 필지 (지목 '대'만) ────────────────────────────────────
prec = []
for f in json.load(open(PROC / "parcels_bldg_4326.geojson", encoding="utf-8"))["features"]:
    jb = (f["properties"].get("jibun") or "").strip()
    if not jb.endswith("대"):
        continue
    g = to5187(shape(f["geometry"]), T47).buffer(0)
    d, s = locate(g.centroid)
    if d is None:
        continue
    L, W = mrr_sides(g)
    prec.append(dict(d=d, side=s, area=g.area, front=W, depth=L))

# ── 가로: 그래프(분기점~분기점 링크), 5 m 표본, 단면 광선 ──────────────
R = read("N3L_A0020000")
key, xy, adj = {}, [], defaultdict(list)


def nid(p):
    k = (round(p[0] * 2), round(p[1] * 2))
    if k not in key:
        key[k] = len(xy); xy.append(p)
    return key[k]


edges = []  # (i, j, length, width)
for g, a in R:
    w = float(a.get("rvwd") or 0)
    for gg in getattr(g, "geoms", [g]):
        cs = list(gg.coords)
        for p, q in zip(cs[:-1], cs[1:]):
            i, j = nid(p), nid(q)
            if i == j:
                continue
            e = len(edges); edges.append((i, j, math.dist(p, q), w))
            adj[i].append(e); adj[j].append(e)
deg = {n: len(v) for n, v in adj.items()}
# 분기점·끝점 사이 사슬 = 링크
seen = set(); links = []
for n in adj:
    if deg[n] == 2:
        continue
    for e0 in adj[n]:
        if e0 in seen:
            continue
        chain, cur, e = [n], n, e0
        length, wl = 0.0, 0.0
        while True:
            seen.add(e)
            i, j, l, w = edges[e]
            nxt = j if i == cur else i
            length += l; wl += w * l; chain.append(nxt)
            if deg[nxt] != 2:
                break
            e = [x for x in adj[nxt] if x != e][0]
            if e in seen:
                break
            cur = nxt
        pts = [xy[k] for k in chain]
        mid = LineString(pts).interpolate(0.5, normalized=True)
        links.append(dict(mid=mid, length=length, width=wl / length if length else 0))
lrec = []
for lk in links:
    d, s = locate(lk["mid"])
    if d is not None:
        lrec.append(dict(d=d, side=s, length=lk["length"], width=lk["width"]))
drec = []
for n, k in deg.items():
    if k == 1:
        d, s = locate(Point(xy[n]))
        if d is not None:
            drec.append(dict(d=d, side=s))

srec = []   # 5 m 표본: 폭 분포, 도로 연장
hrec = []   # 10 m 표본: 건물 간 폭, H/W
for g, a in R:
    w = float(a.get("rvwd") or 0)
    for gg in getattr(g, "geoms", [g]):
        if not gg.intersects(roi):
            continue
        n5 = max(1, int(gg.length // 5))
        for k in range(n5):
            s0 = (k + 0.5) * gg.length / n5
            p = gg.interpolate(s0)
            d, sd = locate(p)
            if d is None:
                continue
            srec.append(dict(d=d, side=sd, width=w, len=gg.length / n5))
            if k % 2:
                continue
            p1 = gg.interpolate(min(gg.length, s0 + 1.0)); p0 = gg.interpolate(max(0.0, s0 - 1.0))
            tx, ty = p1.x - p0.x, p1.y - p0.y; tl = math.hypot(tx, ty) or 1.0
            nx, ny = -ty / tl, tx / tl
            hit = []
            for sgn in (1, -1):
                ray = LineString([(p.x, p.y), (p.x + sgn * nx * RAY, p.y + sgn * ny * RAY)])
                best = None
                for bi in btree.query(ray, predicate="intersects"):
                    bg, bfl = B[bi]
                    dd = p.distance(ray.intersection(bg))
                    if dd > 0.3 and (best is None or dd < best[0]):
                        best = (dd, bfl)
                hit.append(best)
            if hit[0] and hit[1]:
                Wbb = hit[0][0] + hit[1][0]
                H = (hit[0][1] + hit[1][1]) / 2 * FLOOR_H
                hrec.append(dict(d=d, side=sd, Wbb=Wbb, HW=H / Wbb, enclosed=2))
            else:
                hrec.append(dict(d=d, side=sd, Wbb=None, HW=None, enclosed=int(bool(hit[0])) + int(bool(hit[1]))))

# ── 면적: 5 m 격자로 방향×거리띠 총면적·순대지(도로 면·하천 면 제외) ───────────
roads_poly = unary_union([g for g, _ in read("N3A_A0010000") if g.intersects(roi)])
water = unary_union([g for lay in ("N3A_E0010001", "N3A_E0032111") for g, _ in read(lay) if g.intersects(roi)])
gx = np.arange(roi_bb[0], roi_bb[2], 5.0) + 2.5
gy = np.arange(roi_bb[1], roi_bb[3], 5.0) + 2.5
GX, GY = np.meshgrid(gx, gy); GX = GX.ravel(); GY = GY.ravel()
inroi = shapely.contains_xy(roi, GX, GY)
GX, GY = GX[inroi], GY[inroi]
isroad = shapely.contains_xy(roads_poly, GX, GY) | shapely.contains_xy(water, GX, GY)
area = defaultdict(lambda: [0.0, 0.0])  # (side, band) -> [총면적, 순대지]
for x, y, rd in zip(GX, GY, isroad):
    d, s = locate(Point(x, y))
    if d is None:
        continue
    b = band_of(d)
    area[(s, b)][0] += 25.0
    if not rd:
        area[(s, b)][1] += 25.0


# ── 요약 ─────────────────────────────────────────────
def sel(recs, side, lo, hi):
    return [r for r in recs if r["side"] == side and lo <= r["d"] < hi]


rows = []
for side in SIDES:
    for lo, hi, bn in BANDS:
        b = sel(brec, side, lo, hi); p = sel(prec, side, lo, hi); l = sel(lrec, side, lo, hi)
        s = sel(srec, side, lo, hi); h = sel(hrec, side, lo, hi); dd = sel(drec, side, lo, hi)
        tot, net = area[(side, bn)]
        fp = sum(r["fp"] for r in b); gfa = sum(r["fp"] * r["fl"] for r in b)
        slen = sum(r["len"] for r in s)
        ws = [r["width"] for r in s]; wl = [r["len"] for r in s]
        fls = [r["fl"] for r in b]
        hh = [r for r in h if r["HW"] is not None]
        rows.append({
            "방향": side, "거리띠": bn, "총면적_ha": round(tot / 1e4, 2), "순대지_ha": round(net / 1e4, 2),
            "건물수": len(b), "건물밀도_동per순ha": round(len(b) / (net / 1e4), 1) if net else None,
            "바닥면적_p25": round(pct([r["fp"] for r in b], 25)), "바닥면적_p50": round(pct([r["fp"] for r in b], 50)),
            "바닥면적_p75": round(pct([r["fp"] for r in b], 75)), "바닥면적_p90": round(pct([r["fp"] for r in b], 90)),
            "건물길이_p50": round(pct([r["blen"] for r in b], 50), 1), "건물길이_p90": round(pct([r["blen"] for r in b], 90), 1),
            "1층비율": round(np.mean([f == 1 for f in fls]), 3) if fls else None,
            "2층비율": round(np.mean([f == 2 for f in fls]), 3) if fls else None,
            "3층이상비율": round(np.mean([f >= 3 for f in fls]), 3) if fls else None,
            "층수_p90": pct(fls, 90), "층수_max": max(fls) if fls else None,
            "GSI": round(fp / net, 3) if net else None, "FSI": round(gfa / net, 3) if net else None,
            "L": round(gfa / fp, 2) if fp else None,
            "도로연장_m_per_ha": round(slen / (tot / 1e4)) if tot else None,
            "도로폭_p25": round(wpct(ws, wl, 25), 1), "도로폭_p50": round(wpct(ws, wl, 50), 1), "도로폭_p75": round(wpct(ws, wl, 75), 1),
            "폭4m미만_연장비": round(sum(x for w, x in zip(ws, wl) if w < 4) / slen, 3) if slen else None,
            "폭4_8m_연장비": round(sum(x for w, x in zip(ws, wl) if 4 <= w < 8) / slen, 3) if slen else None,
            "폭8_20m_연장비": round(sum(x for w, x in zip(ws, wl) if 8 <= w < 20) / slen, 3) if slen else None,
            "폭20m이상_연장비": round(sum(x for w, x in zip(ws, wl) if w >= 20) / slen, 3) if slen else None,
            "교차간격_p50": round(pct([r["length"] for r in l], 50), 1), "교차간격_p75": round(pct([r["length"] for r in l], 75), 1),
            "막다른끝점_per_ha": round(len(dd) / (tot / 1e4), 2) if tot else None,
            "대지필지수": len(p),
            "필지면적_p25": round(pct([r["area"] for r in p], 25)), "필지면적_p50": round(pct([r["area"] for r in p], 50)),
            "필지면적_p75": round(pct([r["area"] for r in p], 75)), "필지면적_p90": round(pct([r["area"] for r in p], 90)),
            "간구_p50": round(pct([r["front"] for r in p], 50), 1), "깊이_p50": round(pct([r["depth"] for r in p], 50), 1),
            "건물간폭W_p50": round(pct([r["Wbb"] for r in hh], 50), 1), "HW_p25": round(pct([r["HW"] for r in hh], 25), 2),
            "HW_p50": round(pct([r["HW"] for r in hh], 50), 2), "HW_p75": round(pct([r["HW"] for r in hh], 75), 2),
            "양측위요비율": round(np.mean([r["enclosed"] == 2 for r in h]), 3) if h else None,
        })
DER.mkdir(parents=True, exist_ok=True)
with open(OUT_SUM, "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.DictWriter(fo, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

curve = []
for side in SIDES:
    for lo, hi in zip(BINS[:-1], BINS[1:]):
        b = sel(brec, side, lo, hi); p = sel(prec, side, lo, hi); l = sel(lrec, side, lo, hi)
        s = sel(srec, side, lo, hi); h = [r for r in sel(hrec, side, lo, hi) if r["HW"] is not None]
        curve.append({
            "방향": side, "거리_중앙": (lo + hi) / 2, "건물수": len(b),
            "바닥면적_p50": pct([r["fp"] for r in b], 50), "층수_평균": float(np.mean([r["fl"] for r in b])) if b else float("nan"),
            "3층이상비율": float(np.mean([r["fl"] >= 3 for r in b])) if b else float("nan"),
            "도로폭_p50": wpct([r["width"] for r in s], [r["len"] for r in s], 50),
            "교차간격_p50": pct([r["length"] for r in l], 50),
            "필지면적_p50": pct([r["area"] for r in p], 50), "필지수": len(p),
            "HW_p50": pct([r["HW"] for r in h], 50),
        })
with open(OUT_CUR, "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.DictWriter(fo, fieldnames=list(curve[0].keys())); w.writeheader(); w.writerows(curve)

# ── 그림 ─────────────────────────────────────────────
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
COL = {"서": "#1565c0", "동": "#c62828", "북": "#2e7d32", "남": "#6a1b9a"}
fig = plt.figure(figsize=(18, 10.5), dpi=140)
axm = fig.add_axes([0.01, 0.05, 0.36, 0.88])
fc = {1: "#d7d7d7", 2: "#a9a9a9", 3: "#6f6f6f"}
polys, cols = [], []
for g, fl in B:
    if not g.intersects(zone.buffer(DMAX + 30)):
        continue
    for gg in getattr(g, "geoms", [g]):
        polys.append(np.asarray(gg.exterior.coords)); cols.append(fc[min(fl, 3)] if fl < 4 else "#262626")
axm.add_collection(PolyCollection(polys, facecolors=cols, edgecolors="none", zorder=1))
for g, _ in R:
    for gg in getattr(g, "geoms", [g]):
        if gg.intersects(zone.buffer(DMAX + 30)):
            axm.plot(*gg.xy, color="#bdbdbd", lw=0.3, zorder=0)
for lo, hi, _ in BANDS:
    axm.plot(*zone.buffer(hi).exterior.xy, color="#424242", lw=0.9, ls="--", zorder=3)
axm.plot(*zone.exterior.xy, color="#0d47a1", lw=2.2, zorder=4)
c = zone.centroid
for side, (dx, dy) in {"서": (-260, 0), "동": (260, 0), "북": (0, 560), "남": (0, -560)}.items():
    axm.text(c.x + dx, c.y + dy, side, color=COL[side], fontsize=16, fontweight="bold", ha="center", va="center", zorder=5,
             bbox=dict(facecolor="white", edgecolor=COL[side], pad=2, alpha=0.9))
bb = zone.buffer(DMAX + 20).bounds
axm.set_xlim(bb[0], bb[2]); axm.set_ylim(bb[1], bb[3]); axm.set_aspect("equal"); axm.axis("off")
axm.set_title("구역 경계 바깥 0–150 m / 150–400 m 띠\n건물 명도 = 층수 (연회색 1층 → 검정 4층 이상)", fontsize=11, loc="left")

panels = [("바닥면적_p50", "건물 바닥면적 중앙값 (㎡)"), ("3층이상비율", "3층 이상 건물 비율"),
          ("도로폭_p50", "도로폭 중앙값 (m, 길이가중)"), ("교차간격_p50", "교차 간격 중앙값 (m)"),
          ("필지면적_p50", "대(垈) 필지 면적 중앙값 (㎡)"), ("HW_p50", "가로 단면 H/W 중앙값")]
for k, (col, title) in enumerate(panels):
    ax = fig.add_axes([0.41 + (k % 3) * 0.2, 0.55 - (k // 3) * 0.47, 0.17, 0.36])
    for side in SIDES:
        xs = [r["거리_중앙"] for r in curve if r["방향"] == side]
        ys = [r[col] for r in curve if r["방향"] == side]
        ax.plot(xs, ys, marker="o", ms=4, lw=1.8, color=COL[side], label=side)
    if col == "필지면적_p50":
        ax.axhspan(1000, 2500, color="#ffb300", alpha=0.18)
        ax.text(395, 1750, "v2 획지안\n1,000–2,500㎡", ha="right", va="center", fontsize=8, color="#8d6e00")
    ax.axvspan(0, 150, color="#eceff1", zorder=0)
    ax.set_title(title, fontsize=10.5)
    ax.set_xlabel("구역 경계로부터 거리 (m, 바깥쪽)", fontsize=8.5)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=0.3)
    if k == 0:
        ax.legend(fontsize=8.5, ncol=4, loc="upper right")
fig.text(0.41, 0.012, "출처: 국토지리정보원 연속수치지도(T2), V-World 연속지적(T2), 경주시 고시 제2026-8호 구역계(T1). 2026-09-28 자체 계산.\n"
         "층고 3.5 m 가정 · 간구 = 필지 최소외접사각형 짧은 변(대리값) · 방향 = 가장 가까운 경계점 기준 · 회색 바탕 = 경계 인접 0–150 m",
         fontsize=8, linespacing=1.4)
OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_FIG)
print("saved", OUT_SUM, OUT_CUR, OUT_FIG)
for r in rows:
    print(r)
