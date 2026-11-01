"""경주 원도심 조직의 반복 특성 — 모델 범위(연속수치지도 11.06 ㎢) 전체.

묻는 것:
  1. 동(洞)이 달라도 같은 치수가 반복되는가 (필지·건물·교차 간격·골목 폭의 동별 분포)
  2. 가구는 필지 몇 겹 깊이인가 (가로망 면의 짧은 변 ÷ 필지 깊이)
  3. 필지 안의 배치 (필지당 건물 수 = 채 분화, 필지 건폐율 = 마당 비율, 가로에서 물러난 거리)
  4. 건물은 가로를 따르는가, 정남북(방위)을 따르는가 (비스듬한 가로에 면한 건물로 판별)
  5. 반복이 깨지는 곳은 어떤 유형인가 (200 m 격자, 투명한 규칙 분류)

입력: 대지/(B020)연속수치지도_202609132098 (NGII, T2, 5179→5187), V-World 연속지적(T2, 지목 '대'),
      고시 제2026-8호 구역계(T1)
출력: archive/90_derived/fabric_dong_summary_20260928.csv, fabric_cells_20260928.csv,
      work/maps/map12_경주조직_반복특성.png
"""
import csv
import json
import math
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import shapefile
import shapely
from pyproj import Transformer
from shapely.geometry import LineString, Point, box, shape
from shapely.ops import polygonize, transform as shp_transform, unary_union
from shapely.strtree import STRtree

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "대지" / "(B020)연속수치지도_202609132098"
PROC = ROOT / "archive" / "C_data" / "processed"
DER = ROOT / "archive" / "90_derived"
OUT_DONG = DER / "fabric_dong_summary_20260928.csv"
OUT_CELL = DER / "fabric_cells_20260928.csv"
OUT_FIG = ROOT / "work" / "maps" / "map12_경주조직_반복특성.png"
T57 = Transformer.from_crs("EPSG:5179", "EPSG:5187", always_xy=True)
T47 = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True)
CELL = 200.0


def to5187(g, t=T57):
    return shp_transform(lambda x, y, z=None: t.transform(x, y), g)


def read(layer):
    r = shapefile.Reader(str(SRC / layer))
    flds = [f[0] for f in r.fields[1:]]
    return [(to5187(shape(s.shape.__geo_interface__)), dict(zip(flds, s.record))) for s in r.iterShapeRecords()]


def mrr(g):
    """최소외접사각형 → (긴 변, 짧은 변, 긴 변 방위 0–180°)"""
    cs = list(g.minimum_rotated_rectangle.exterior.coords)
    e1 = (cs[1][0] - cs[0][0], cs[1][1] - cs[0][1]); e2 = (cs[2][0] - cs[1][0], cs[2][1] - cs[1][1])
    l1, l2 = math.hypot(*e1), math.hypot(*e2)
    e = e1 if l1 >= l2 else e2
    return max(l1, l2), min(l1, l2), math.degrees(math.atan2(e[1], e[0])) % 180


def d90(a, b):
    """두 방위의 직교 무관 차이 (0–45°): 평행이든 직각이든 '정렬'로 본다"""
    x = abs((a % 90) - (b % 90))
    return min(x, 90 - x)


def pct(a, q):
    a = [v for v in a if v is not None and np.isfinite(v)]
    return float(np.percentile(a, q)) if a else float("nan")


zone = shape(json.load(open(PROC / "gosi2026-8_zone_5187.geojson", encoding="utf-8"))["features"][0]["geometry"]).buffer(0)
ext = to5187(box(*shapefile.Reader(str(SRC / "N3L_A0020000")).bbox).segmentize(20))

# ── 가로 ───────────────────────────────────────────────
pieces, pw = [], []
for g, a in read("N3L_A0020000"):
    for gg in getattr(g, "geoms", [g]):
        pieces.append(gg); pw.append(float(a.get("rvwd") or 0))
ptree = STRtree(pieces)

# 링크(분기점~분기점)와 막다른 링크
key, xy, adj, edges = {}, [], defaultdict(list), []


def nid(p):
    k = (round(p[0] * 2), round(p[1] * 2))
    if k not in key:
        key[k] = len(xy); xy.append(p)
    return key[k]


for gg, w in zip(pieces, pw):
    cs = list(gg.coords)
    for p, q in zip(cs[:-1], cs[1:]):
        i, j = nid(p), nid(q)
        if i != j:
            e = len(edges); edges.append((i, j, math.dist(p, q), w)); adj[i].append(e); adj[j].append(e)
deg = {n: len(v) for n, v in adj.items()}
seen, links = set(), []
for n in adj:
    if deg[n] == 2:
        continue
    for e0 in adj[n]:
        if e0 in seen:
            continue
        cur, e, L, WL, chain = n, e0, 0.0, 0.0, [n]
        while True:
            seen.add(e); i, j, l, w = edges[e]
            nxt = j if i == cur else i
            L += l; WL += w * l; chain.append(nxt)
            if deg[nxt] != 2:
                break
            e = [x for x in adj[nxt] if x != e][0]
            if e in seen:
                break
            cur = nxt
        mid = LineString([xy[k] for k in chain]).interpolate(0.5, normalized=True)
        links.append(dict(mid=mid, length=L, width=WL / L if L else 0, dead=(deg[chain[0]] == 1 or deg[chain[-1]] == 1)))

# ── 건물 ───────────────────────────────────────────────
B = []
for g, a in read("N3A_B0010000"):
    if g.is_empty or g.area < 1:
        continue
    L, W, th = mrr(g)
    B.append(dict(g=g, c=g.centroid, fp=g.area, blen=L, bwid=W, th=th,
                  fl=int(a.get("nmly") or 1) or 1, dong=str(a.get("bjcd") or "")[:10]))
bc = shapely.points([(b["c"].x, b["c"].y) for b in B])
near = ptree.query_nearest([b["g"] for b in B], return_distance=True, all_matches=False)
for (bi, pi), dist in zip(near[0].T, near[1]):
    b, gg = B[bi], pieces[pi]
    s = gg.project(b["c"])
    p1, p0 = gg.interpolate(min(gg.length, s + 1.5)), gg.interpolate(max(0.0, s - 1.5))
    b["sth"] = math.degrees(math.atan2(p1.y - p0.y, p1.x - p0.x)) % 180
    b["sw"] = pw[pi]
    b["setback"] = max(0.0, dist - pw[pi] / 2)   # 도로 중심선까지 거리 − 도로 반폭 = 도로 가장자리에서 물러난 거리(대리값)
btree = STRtree([b["c"] for b in B])

# 링크의 동 = 중점에서 가장 가까운 건물의 법정동
li = btree.query_nearest([lk["mid"] for lk in links], all_matches=False)
for k, bi in zip(li[0], li[1]):
    links[k]["dong"] = B[bi]["dong"]

# ── 필지(지목 대) ─────────────────────────────────────────
P, dong_name = [], {}
for f in json.load(open(PROC / "parcels_bldg_4326.geojson", encoding="utf-8"))["features"]:
    pr = f["properties"]; pnu = str(pr.get("pnu") or "")
    toks = (pr.get("addr") or "").split()
    nm = next((t for t in toks if t.endswith("동")), None)
    if nm and len(pnu) >= 10:
        dong_name.setdefault(pnu[:10], nm)
    if not (pr.get("jibun") or "").strip().endswith("대"):
        continue
    g = to5187(shape(f["geometry"]), T47).buffer(0)
    if g.is_empty:
        continue
    L, W, th = mrr(g)
    P.append(dict(g=g, area=g.area, depth=L, front=W, th=th, dong=pnu[:10], nb=0, fpsum=0.0))
ptree_parcel = STRtree([p["g"] for p in P])
pairs = ptree_parcel.query(bc, predicate="within")
for bi, pi in zip(pairs[0], pairs[1]):
    P[pi]["nb"] += 1; P[pi]["fpsum"] += B[bi]["fp"]
# 법정동 이름은 상가업소(소상공인시장진흥공단, T2)의 법정동명을 그 점을 품은 건물의 bjcd 와 맞춰 다수결로 정한다
votes = defaultdict(Counter)
st = json.load(open(PROC / "stores_merged_4326.geojson", encoding="utf-8"))["features"]
spts = [Point(*T47.transform(*f["geometry"]["coordinates"][:2])) for f in st]
btree_poly = STRtree([b["g"] for b in B])
qq = btree_poly.query(spts, predicate="within")
for si, bi in zip(qq[0], qq[1]):
    nm = st[si]["properties"].get("ldongNm")
    if nm:
        votes[B[bi]["dong"]][nm] += 1
store_name = {k: v.most_common(1)[0][0] for k, v in votes.items() if v}
name_check = {k: (store_name.get(k), dong_name.get(k)) for k in set(store_name) | set(dong_name)}
dong_name = {**dong_name, **store_name}

# ── 가로망 면(가구) = 도로중심선 망의 면 ─────────────────────────
faces = [f for f in polygonize(unary_union(pieces)) if f.area >= 300]
ftree = STRtree(faces)
fpar = defaultdict(list)
pc = shapely.points([(p["g"].representative_point().x, p["g"].representative_point().y) for p in P])
fp_pairs = ftree.query(pc, predicate="within")
for pi, fi in zip(fp_pairs[0], fp_pairs[1]):
    fpar[fi].append(pi)
face_rows = []
for fi, f in enumerate(faces):
    L, W, _ = mrr(f)
    ps = fpar.get(fi, [])
    dep = np.median([P[k]["depth"] for k in ps]) if len(ps) >= 4 else float("nan")
    face_rows.append(dict(area=f.area, long=L, short=W, n_parcel=len(ps), rows=W / dep if dep == dep else float("nan")))

# ── 동별 요약 ─────────────────────────────────────────────
bydong = defaultdict(list)
for b in B:
    bydong[b["dong"]].append(b)
pdong = defaultdict(list)
for p in P:
    pdong[p["dong"]].append(p)
ldong = defaultdict(list)
for lk in links:
    ldong[lk.get("dong", "")].append(lk)
drows = []
for dg, bs in sorted(bydong.items(), key=lambda kv: -len(kv[1])):
    if len(bs) < 300:
        continue
    ps = pdong.get(dg, []); ls = ldong.get(dg, [])
    lane = [b for b in bs if b["sw"] < 4]
    drows.append({
        "법정동코드": dg, "동": dong_name.get(dg, dg), "건물수": len(bs),
        "1층비율": round(np.mean([b["fl"] == 1 for b in bs]), 3),
        "바닥면적_p50": round(pct([b["fp"] for b in bs], 50)), "바닥면적_p75": round(pct([b["fp"] for b in bs], 75)),
        "건물길이_p50": round(pct([b["blen"] for b in bs], 50), 1), "건물길이_p90": round(pct([b["blen"] for b in bs], 90), 1),
        "대필지수": len(ps),
        "필지면적_p25": round(pct([p["area"] for p in ps], 25)) if len(ps) >= 50 else None,
        "필지면적_p50": round(pct([p["area"] for p in ps], 50)) if len(ps) >= 50 else None,
        "필지면적_p75": round(pct([p["area"] for p in ps], 75)) if len(ps) >= 50 else None,
        "간구_p50": round(pct([p["front"] for p in ps], 50), 1) if len(ps) >= 50 else None,
        "깊이_p50": round(pct([p["depth"] for p in ps], 50), 1) if len(ps) >= 50 else None,
        "필지당건물2동이상": round(np.mean([p["nb"] >= 2 for p in ps if p["nb"] >= 1]), 3) if len(ps) >= 50 else None,
        "필지건폐율_p50": round(pct([p["fpsum"] / p["area"] for p in ps if p["nb"] >= 1], 50), 2) if len(ps) >= 50 else None,
        "교차간격_p50": round(pct([lk["length"] for lk in ls], 50), 1),
        "막다른링크비율": round(np.mean([lk["dead"] for lk in ls]), 3) if ls else None,
        "골목면건물_물러난거리_p50": round(pct([b["setback"] for b in lane], 50), 1),
        "간선면건물_물러난거리_p50": round(pct([b["setback"] for b in bs if b["sw"] >= 15], 50), 1),
    })
DER.mkdir(parents=True, exist_ok=True)
with open(OUT_DONG, "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.DictWriter(fo, fieldnames=list(drows[0].keys())); w.writeheader(); w.writerows(drows)

# ── 방향: 비스듬한 가로(방위와 20° 이상 틀어짐)에 15 m 안으로 면한 건물은 무엇을 따르나 ─────
obl = [b for b in B if d90(b["sth"], 0) >= 20 and b["setback"] <= 15 and b["blen"] / max(b["bwid"], 0.1) >= 1.2]
to_street = np.mean([d90(b["th"], b["sth"]) <= 10 for b in obl])
to_card = np.mean([d90(b["th"], 0) <= 10 for b in obl])
allb = [b for b in B if b["blen"] / max(b["bwid"], 0.1) >= 1.2]

# ── 방위 체계: 주 격자축(mod 90) + 사선 체계 2개(mod 180) ─────────────────
seg = []
for gg in pieces:
    cs = list(gg.coords)
    for p_, q_ in zip(cs[:-1], cs[1:]):
        l = math.dist(p_, q_)
        if l >= 0.5:
            seg.append(((p_[0] + q_[0]) / 2, (p_[1] + q_[1]) / 2,
                        math.degrees(math.atan2(q_[1] - p_[1], q_[0] - p_[0])) % 180, l, (p_, q_)))
sx = np.array([t[0] for t in seg]); sy = np.array([t[1] for t in seg])
s180 = np.array([t[2] for t in seg]); slen = np.array([t[3] for t in seg])
h90, e90 = np.histogram(s180 % 90, bins=180, range=(0, 90), weights=slen)
ax0 = float((e90[h90.argmax()] + e90[h90.argmax() + 1]) / 2)
is_grid = np.array([d90(t, ax0) <= 7.5 for t in s180])
rest = np.array([d90(t, ax0) >= 20 for t in s180])
h180, e180 = np.histogram(s180[rest], bins=180, range=(0, 180), weights=slen[rest])
hs = np.convolve(np.r_[h180[-3:], h180, h180[:3]], np.ones(7) / 7, mode="same")[3:-3]
i1 = int(hs.argmax())
hs2 = hs.copy()
for k in range(-20, 21):
    hs2[(i1 + k) % 180] = 0
i2 = int(hs2.argmax())
axA, axB = float((e180[i1] + e180[i1 + 1]) / 2), float((e180[i2] + e180[i2 + 1]) / 2)


def d180(a, b):
    x = abs(a - b) % 180
    return min(x, 180 - x)


isA = np.array([d180(t, axA) <= 7.5 for t in s180])
isB = np.array([d180(t, axB) <= 7.5 for t in s180])
cls = np.where(is_grid, 0, np.where(isA, 1, np.where(isB, 2, 3)))
share = {k: float(slen[cls == k].sum() / slen.sum()) for k in range(4)}
nbr = btree.query_nearest(shapely.points(np.c_[sx, sy]), all_matches=False)
seg_dong = np.empty(len(seg), dtype=object)
seg_dong[nbr[0]] = [B[i]["dong"] for i in nbr[1]]
for r in drows:
    m = seg_dong == r["법정동코드"]
    tot = slen[m].sum()
    r["주격자_가로비율"] = round(float(slen[m & (cls == 0)].sum() / tot), 3) if tot else None
    r["사선A_가로비율"] = round(float(slen[m & (cls == 1)].sum() / tot), 3) if tot else None
    r["사선B_가로비율"] = round(float(slen[m & (cls == 2)].sum() / tot), 3) if tot else None
with open(OUT_DONG, "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.DictWriter(fo, fieldnames=list(drows[0].keys())); w.writeheader(); w.writerows(drows)
bgrid = np.mean([d90(b["th"], ax0) <= 7.5 for b in allb])


def bearing_txt(theta):
    """x축(동) 기준 반시계 각 → 가로 방향의 나침반 방위 표기"""
    brg = (90 - theta) % 180
    return f"N{brg:.1f}°E" if brg <= 90 else f"N{180 - brg:.1f}°W"


# ── 200 m 격자 유형 (투명한 규칙) ───────────────────────────────
roads = unary_union([g for g, _ in read("N3A_A0010000")])
x0, y0, x1, y1 = ext.bounds
cells = []
for cx in np.arange(x0, x1, CELL):
    for cy in np.arange(y0, y1, CELL):
        cb = box(cx, cy, cx + CELL, cy + CELL)
        if not ext.contains(cb.centroid):
            continue
        ids = btree.query(cb, predicate="contains")
        bs = [B[i] for i in ids]
        land = cb.area - cb.intersection(roads).area
        ls = [lk for lk in links if cb.contains(lk["mid"])]
        m = (sx >= cx) & (sx < cx + CELL) & (sy >= cy) & (sy < cy + CELL)
        rec = dict(x=cx, y=cy, n=len(bs), gsi=sum(b["fp"] for b in bs) / land if land > 0 else 0,
                   f1=np.mean([b["fl"] == 1 for b in bs]) if bs else float("nan"),
                   flm=np.mean([b["fl"] for b in bs]) if bs else float("nan"),
                   bl90=pct([b["blen"] for b in bs], 90), link=pct([lk["length"] for lk in ls], 50),
                   grid=float(slen[m & (cls == 0)].sum() / slen[m].sum()) if m.any() else float("nan"),
                   inzone=cb.intersection(zone).area / cb.area)
        # 규칙: 위에서부터 첫 번째로 맞는 유형. 경계값은 경계띠 실측(map11)과 동별 분포에서 가져온 판단값
        if rec["n"] < 15 or rec["gsi"] < 0.10:
            t = "비움(고분·유적·녹지·농지·철도)"
        elif rec["flm"] >= 3.0:
            t = "공동주택·중층 단지"
        elif rec["bl90"] > 20:
            t = "가로 상업·대형 건물"
        elif rec["f1"] >= 0.75 and rec["bl90"] <= 17 and (rec["link"] != rec["link"] or rec["link"] <= 45):
            t = "세립 저층 골목 조직"
        elif rec["f1"] < 0.75:
            t = "다세대·중저층 주거"
        else:
            t = "혼합·전이"
        rec["type"] = t
        cells.append(rec)
with open(OUT_CELL, "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.DictWriter(fo, fieldnames=list(cells[0].keys())); w.writeheader(); w.writerows(cells)

# ── 출력 ─────────────────────────────────────────────
tc = Counter(c["type"] for c in cells)
print("동 이름 대조(상가업소, 필지주소):", name_check)
print("격자 유형:", tc.most_common())
print(f"주 격자축 {ax0:.1f}° (mod 90) → 가로 {bearing_txt(ax0)} / {bearing_txt(ax0 + 90)}; 주격자 {share[0]:.2f}, "
      f"사선A {axA:.0f}° ({bearing_txt(axA)}) {share[1]:.2f}, 사선B {axB:.0f}° ({bearing_txt(axB)}) {share[2]:.2f}, 기타 {share[3]:.2f}; 건물 주격자 정렬 {bgrid:.2f}")
print(f"비스듬한 가로에 면한 건물 n={len(obl)}: 가로 정렬 {to_street:.2f}, 방위 정렬 {to_card:.2f}")
fr = [r for r in face_rows if r["n_parcel"] >= 4]
print(f"가구(가로망 면, 대지 필지 4개 이상 n={len(fr)}): 짧은 변 p25/p50/p75 {pct([r['short'] for r in fr],25):.0f}/{pct([r['short'] for r in fr],50):.0f}/{pct([r['short'] for r in fr],75):.0f} m, "
      f"긴 변 p50 {pct([r['long'] for r in fr],50):.0f} m, 면적 p50 {pct([r['area'] for r in fr],50):.0f} ㎡, 필지 수 p50 {pct([r['n_parcel'] for r in fr],50):.0f}, "
      f"겹수 p25/p50/p75 {pct([r['rows'] for r in fr],25):.2f}/{pct([r['rows'] for r in fr],50):.2f}/{pct([r['rows'] for r in fr],75):.2f}")
print(f"필지(대) n={len(P)}: 면적 p50 {pct([p['area'] for p in P],50):.0f}, 간구 {pct([p['front'] for p in P],50):.1f}, 깊이 {pct([p['depth'] for p in P],50):.1f}, "
      f"깊이/간구 p50 {pct([p['depth']/p['front'] for p in P],50):.2f}, 건물 2동 이상 {np.mean([p['nb']>=2 for p in P if p['nb']>=1]):.2f}, "
      f"필지건폐율 p50 {pct([p['fpsum']/p['area'] for p in P if p['nb']>=1],50):.2f}, 건물 없는 대지 필지 {np.mean([p['nb']==0 for p in P]):.2f}")
print(f"링크 n={len(links)}: 막다른 비율 {np.mean([lk['dead'] for lk in links]):.2f}, 막다른 링크 길이 p50 {pct([lk['length'] for lk in links if lk['dead']],50):.1f} m, "
      f"통과 링크 p50 {pct([lk['length'] for lk in links if not lk['dead']],50):.1f} m")
for r in drows:
    print({k: r[k] for k in ("동", "법정동코드", "건물수", "1층비율", "건물길이_p90", "필지면적_p50", "간구_p50", "깊이_p50",
                             "교차간격_p50", "막다른링크비율", "주격자_가로비율", "사선A_가로비율", "사선B_가로비율")})
# 리포트 카드용 전역 요약 (gj-datamap '도시 조직' 그룹)
_pp = [p for p in P if p["nb"] >= 1]
json.dump({
    "parcels": {"n": len(P), "area_p50": round(pct([p["area"] for p in P], 50)), "front_p50": round(pct([p["front"] for p in P], 50), 1),
                "depth_p50": round(pct([p["depth"] for p in P], 50), 1), "depth_front_p50": round(pct([p["depth"] / p["front"] for p in P], 50), 2),
                "share_2plus_bldg": round(float(np.mean([p["nb"] >= 2 for p in _pp])), 3), "lot_gsi_p50": round(pct([p["fpsum"] / p["area"] for p in _pp], 50), 2)},
    "blocks": {"n": len(fr), "short_p25": round(pct([r["short"] for r in fr], 25)), "short_p50": round(pct([r["short"] for r in fr], 50)),
               "short_p75": round(pct([r["short"] for r in fr], 75)), "long_p50": round(pct([r["long"] for r in fr], 50)),
               "area_p50": round(pct([r["area"] for r in fr], 50)), "parcels_p50": round(pct([r["n_parcel"] for r in fr], 50)),
               "rows_p25": round(pct([r["rows"] for r in fr], 25), 2), "rows_p50": round(pct([r["rows"] for r in fr], 50), 2), "rows_p75": round(pct([r["rows"] for r in fr], 75), 2)},
    "links": {"n": len(links), "dead_share": round(float(np.mean([lk["dead"] for lk in links])), 3),
              "dead_len_p50": round(pct([lk["length"] for lk in links if lk["dead"]], 50), 1), "through_len_p50": round(pct([lk["length"] for lk in links if not lk["dead"]], 50), 1)},
    "orientation": {"grid_axis_mod90": ax0, "grid_bearing": bearing_txt(ax0), "diagA_bearing": bearing_txt(axA), "diagB_bearing": bearing_txt(axB),
                    "street_share": {"grid": round(share[0], 3), "diagA": round(share[1], 3), "diagB": round(share[2], 3), "other": round(share[3], 3)},
                    "building_grid_share": round(float(bgrid), 3), "oblique_n": len(obl), "oblique_to_street": round(float(to_street), 3), "oblique_to_cardinal": round(float(to_card), 3)},
    "cell_types": dict(tc.most_common()),
    "dongs": [{k: (float(v) if isinstance(v, (np.floating,)) else v) for k, v in r.items()} for r in drows],
}, open(DER / "fabric_global_20260928.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ── 그림 ─────────────────────────────────────────────
from matplotlib.collections import LineCollection
plt.rcParams["font.family"] = "Malgun Gothic"; plt.rcParams["axes.unicode_minus"] = False
TCOL = {"세립 저층 골목 조직": "#f4a261", "다세대·중저층 주거": "#b56576", "혼합·전이": "#e9c46a",
        "가로 상업·대형 건물": "#e63946", "공동주택·중층 단지": "#457b9d", "비움(고분·유적·녹지·농지·철도)": "#8ab17d"}
OCOL = {0: "#c1121f", 1: "#1d4ed8", 2: "#15803d", 3: "#c7c7c7"}
fig = plt.figure(figsize=(21, 12.5), dpi=130)
bpolys = [np.asarray(gg.exterior.coords) for b in B for gg in getattr(b["g"], "geoms", [b["g"]])]

axA_ = fig.add_axes([0.005, 0.30, 0.325, 0.64])
for c in cells:
    axA_.add_patch(plt.Rectangle((c["x"], c["y"]), CELL, CELL, facecolor=TCOL[c["type"]], alpha=0.5,
                                 edgecolor="white", lw=0.6, zorder=0))
axA_.add_collection(PolyCollection(bpolys, facecolors="#222222", edgecolors="none", zorder=1))
axA_.plot(*zone.exterior.xy, color="#0d47a1", lw=2, zorder=3)
axA_.set_xlim(x0, x1); axA_.set_ylim(y0, y1); axA_.set_aspect("equal"); axA_.axis("off")
axA_.legend(handles=[Patch(facecolor=TCOL[k], alpha=0.7, label=f"{k}  {tc.get(k, 0)}칸") for k in TCOL],
            loc="upper left", bbox_to_anchor=(0.0, -0.01), ncol=2, fontsize=8.5, framealpha=0.95)
axA_.set_title("① 200 m 격자 조직 유형 (규칙 분류)", fontsize=12, loc="left")

axB_ = fig.add_axes([0.335, 0.30, 0.325, 0.64])
for k in (3, 2, 1, 0):
    segs = [seg[i][4] for i in np.where(cls == k)[0]]
    axB_.add_collection(LineCollection(segs, colors=OCOL[k], linewidths=0.5 if k == 3 else 0.9, zorder=1 + (3 - k)))
axB_.plot(*zone.exterior.xy, color="#111111", lw=2, zorder=6)
axB_.set_xlim(x0, x1); axB_.set_ylim(y0, y1); axB_.set_aspect("equal"); axB_.axis("off")
axB_.legend(handles=[Patch(facecolor=OCOL[0], label=f"주 격자 {bearing_txt(ax0 + 90)}·{bearing_txt(ax0)}  {share[0]:.0%}"),
                     Patch(facecolor=OCOL[1], label=f"사선 A {bearing_txt(axA)}  {share[1]:.0%}"),
                     Patch(facecolor=OCOL[2], label=f"사선 B {bearing_txt(axB)}  {share[2]:.0%}"),
                     Patch(facecolor=OCOL[3], label=f"기타  {share[3]:.0%}")],
            loc="upper left", bbox_to_anchor=(0.0, -0.01), ncol=2, fontsize=8.5, framealpha=0.95)
axB_.set_title("② 가로 방위 체계 (도로중심선 길이 비율, ±7.5°)", fontsize=12, loc="left")

names = [r["동"] for r in drows]
ypos = np.arange(len(drows))[::-1]
specs = [("필지면적", "대(垈) 필지 ㎡\n(p25–p50–p75)"), ("건물길이", "건물 길이 m\n(p50 ● · p90 ■)"),
         ("교차간격_p50", "교차 간격\n중앙값 m"), ("1층비율", "1층 건물\n비율"), ("주격자_가로비율", "주 격자 정렬\n가로 비율")]
for k, (col, title) in enumerate(specs):
    a2 = fig.add_axes([0.715 + k * 0.057, 0.47, 0.048, 0.45])
    if col == "필지면적":
        for yv, r in zip(ypos, drows):
            if r["필지면적_p50"]:
                a2.plot([r["필지면적_p25"], r["필지면적_p75"]], [yv, yv], color="#555", lw=2)
                a2.plot(r["필지면적_p50"], yv, "o", color="#e76f51", ms=4)
    elif col == "건물길이":
        a2.plot([r["건물길이_p50"] for r in drows], ypos, "o", color="#e76f51", ms=4)
        a2.plot([r["건물길이_p90"] for r in drows], ypos, "s", color="#264653", ms=4)
    else:
        a2.plot([r[col] if r[col] is not None else np.nan for r in drows], ypos, "o", color="#e76f51", ms=4)
    a2.set_yticks(ypos); a2.set_yticklabels(names if k == 0 else [], fontsize=8.5)
    a2.set_title(title, fontsize=8.5); a2.tick_params(axis="x", labelsize=7); a2.grid(alpha=0.3)

a3 = fig.add_axes([0.715, 0.08, 0.13, 0.28])
a3.hist(s180, bins=90, range=(0, 180), weights=slen / 1000, color="#264653")
for axv, cc in ((ax0, OCOL[0]), ((ax0 + 90) % 180, OCOL[0]), (axA, OCOL[1]), (axB, OCOL[2])):
    a3.axvline(axv, color=cc, lw=1.4, ls="--")
a3.set_xlabel("가로 선분 방위 (동=0°, 반시계, mod 180)", fontsize=8.5); a3.set_ylabel("연장 km", fontsize=8.5)
a3.set_title("가로 방위 분포", fontsize=9.5); a3.tick_params(labelsize=7.5)
a4 = fig.add_axes([0.865, 0.08, 0.05, 0.28])
a4.bar(["가로", "방위"], [to_street, to_card], color=["#264653", "#e76f51"])
a4.set_ylim(0, 1); a4.set_title(f"비스듬한 가로 면\n건물 {len(obl):,}동의 정렬", fontsize=8.5); a4.tick_params(labelsize=7.5)
for i, v in enumerate([to_street, to_card]):
    a4.text(i, v + 0.02, f"{v:.0%}", ha="center", fontsize=9)
a5 = fig.add_axes([0.935, 0.08, 0.058, 0.28])
rows_ = [r["rows"] for r in fr if r["rows"] == r["rows"] and r["rows"] < 8]
a5.hist(rows_, bins=np.arange(0, 8.01, 0.5), color="#2a9d8f", orientation="horizontal")
a5.set_ylabel("가구 짧은 변 ÷ 필지 깊이", fontsize=8); a5.set_title(f"가구 깊이\n(필지 겹, n={len(fr)})", fontsize=8.5)
a5.tick_params(labelsize=7.5)
fig.text(0.005, 0.03,
         "출처: 국토지리정보원 연속수치지도(T2), V-World 연속지적(T2, 지목 '대', 부지 주변 동서 약 2.1 km만 덮음), 소상공인시장진흥공단 상가업소(T2, 법정동명 대조), "
         "경주시 고시 제2026-8호(T1). 2026-09-28 자체 계산.\n"
         "유형 규칙(위에서부터 첫 일치): 건물 15동 미만 또는 순건폐율 0.10 미만 = 비움 / 평균층수 3 이상 = 공동주택 / 건물 길이 p90 20 m 초과 = 가로 상업·대형 / "
         "1층 75% 이상·길이 p90 17 m 이하·교차 간격 45 m 이하 = 세립 저층 골목 / 1층 75% 미만 = 다세대 / 나머지 = 혼합. 경계값은 경계띠 실측(map11)과 동별 분포에서 정한 판단값.",
         fontsize=8, linespacing=1.5)
OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_FIG)
print("saved", OUT_DONG, OUT_CELL, OUT_FIG)
