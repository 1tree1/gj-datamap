import pickle, json, math, collections
import numpy as np
from shapely import wkb
from shapely.geometry import Point, Polygon, LineString, MultiPolygon
from shapely.ops import unary_union, nearest_points
from shapely.strtree import STRtree

SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7d42d444-7313-40a1-ac02-6f82986afca6\scratchpad"
d = pickle.load(open(SP + r"\step1.pkl", "rb"))
U = wkb.loads(d["U"]); zone = wkb.loads(d["zone"])
recs = d["recs"]
import re
for r in recs:
    r["geom"] = wkb.loads(r["geom"]); r["area"] = r["geom"].area
    m = re.search(r"([가-힣])$", r["jibun"].strip())
    r["jimok"] = m.group(1) if m else ""
JM = {"철": "철도용지", "대": "대지", "도": "도로", "천": "하천", "구": "구거", "전": "전", "답": "답", "잡": "잡종지", "창": "창고용지", "임": "임야"}
tree = STRtree([r["geom"] for r in recs])
cand = tree.query(U)
rows = []
for i in cand:
    r = recs[i]
    inter = r["geom"].intersection(U).area
    if inter <= 0.01: continue
    rows.append(dict(i=i, share=inter / r["area"], inter=inter, **{k: r[k] for k in ("pnu", "jibun", "jimok", "area", "jiga", "bldg_n", "addr")}))
print("U와 겹치는 필지:", len(rows))

# A. 필지 단위 분류
full = [x for x in rows if x["share"] >= 0.995]
cut = [x for x in rows if x["share"] < 0.995]
print(f"[A] 완전 포함 {len(full)}개 / 선이 가로지르는 필지 {len(cut)}개")
print(f"    가로지르는 필지 총면적 {sum(x['area'] for x in cut):,.0f}㎡ = 안쪽 {sum(x['inter'] for x in cut):,.0f} + 바깥 {sum(x['area']-x['inter'] for x in cut):,.0f}")
bins = [(0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, .9), (.9, .995)]
for lo, hi in bins:
    s = [x for x in cut if lo <= x["share"] < hi]
    print(f"    share {lo:.1f}-{hi:.2f}: {len(s):3d}개, 필지면적 {sum(x['area'] for x in s):9,.0f}㎡, U안 {sum(x['inter'] for x in s):9,.0f}㎡")

# B. 규칙별 매입경계
def build(selected):
    return unary_union([recs[x["i"]]["geom"] for x in selected]).buffer(0)

P_in = build(full)                                      # 100% 안쪽만(내접)
P50 = build([x for x in rows if x["share"] >= 0.5])     # v3 규칙 1
P_out = build(rows)                                     # 조금이라도 걸치면(외접)
def outer(g):
    if isinstance(g, MultiPolygon):
        return MultiPolygon([Polygon(p.exterior) for p in g.geoms])
    return Polygon(g.exterior)

# v3 규칙 2: 폭 8m 이하 막다른 골목(도로·구거) 분할 편입 (근사: closing 4m 으로 홈을 찾고, 도·구 필지와 겹치는 부분만)
def fill_alleys(P1, maxw=8.0):
    closed = P1.buffer(maxw / 2, join_style=2).buffer(-maxw / 2, join_style=2)
    notch = closed.difference(P1)
    road = unary_union([r["geom"] for r in recs if r["jimok"] in ("도", "구")])
    piece = notch.intersection(road)
    piece = piece.buffer(-0.05).buffer(0.05)
    return piece
alley = fill_alleys(P50)
P50a = unary_union([P50, alley]).buffer(0)
P50a = outer(P50a)
print(f"\n[B] 면적: U {U.area:,.0f} | 내접(100%) {P_in.area:,.0f} | v3규칙(50%) {P50.area:,.0f} (+골목 {alley.area:,.0f} → {P50a.area:,.0f}) | 외접(걸치면 전부) {P_out.area:,.0f}")
print(f"    조각 수: 50% {len(P50.geoms) if hasattr(P50,'geoms') else 1}, 골목포함 {len(P50a.geoms) if hasattr(P50a,'geoms') else 1}")

def diff_report(name, P):
    add = P.difference(U); rem = U.difference(P)
    sd = add.area + rem.area
    print(f"    {name}: 늘어난 땅 {add.area:,.0f}㎡ / 빠진 땅 {rem.area:,.0f}㎡ / 순증감 {P.area-U.area:+,.0f}㎡ ({(P.area-U.area)/U.area*100:+.1f}%) / 어긋난 면적 합 {sd:,.0f}㎡ = U의 {sd/U.area*100:.1f}%")
    return add, rem
print("[C] U 대비 차이")
add50, rem50 = diff_report("v3규칙 50%+골목", P50a)
diff_report("50%만", P50)
diff_report("내접", P_in)
diff_report("외접", P_out)

# 편입 필지 요약 (v3규칙)
sel = [x for x in rows if x["share"] >= 0.5]
tot_jiga = sum(x["area"] * x["jiga"] for x in sel) / 1e8
by = collections.defaultdict(lambda: [0, 0.0, 0.0])
for x in sel:
    b = by[x["jimok"]]; b[0] += 1; b[1] += x["area"]; b[2] += x["area"] * x["jiga"] / 1e8
print(f"\n[D] v3규칙 편입 필지 {len(sel)}개, 필지면적 합 {sum(x['area'] for x in sel):,.0f}㎡, 공시지가액 {tot_jiga:,.1f}억, 건축물 있는 필지 {sum(1 for x in sel if x['bldg_n']>0)}")
for k, v in sorted(by.items(), key=lambda kv: -kv[1][1]):
    print(f"    {k or '?'}: {v[0]}필지 {v[1]:,.0f}㎡ {v[2]:,.1f}억")
zone_in = [x for x in sel if recs[x["i"]]["geom"].intersection(zone).area / x["area"] >= 0.5]
print(f"    고시구역 안 {len(zone_in)}필지 {sum(x['area'] for x in zone_in):,.0f}㎡ / 밖 {len(sel)-len(zone_in)}필지 {sum(x['area'] for x in sel)-sum(x['area'] for x in zone_in):,.0f}㎡")
print(f"    U − 고시구역 = {U.difference(zone).area:,.0f}㎡ ({U.difference(zone).area/U.area*100:.1f}% of U), 고시구역 − U = {zone.difference(U).area:,.0f}㎡")

# D2. 늘어난 땅 / 빠진 땅의 지목 분해
def by_jimok(g, label):
    agg = collections.defaultdict(float)
    for i in tree.query(g):
        a = recs[i]["geom"].intersection(g).area
        if a > 0.01: agg[JM.get(recs[i]["jimok"], recs[i]["jimok"] or "?")] += a
    print(f"    {label} {g.area:,.0f}㎡ →", ", ".join(f"{k} {v:,.0f}" for k, v in sorted(agg.items(), key=lambda kv: -kv[1])))
print("\n[D2] 어긋난 땅의 지목")
by_jimok(add50, "필지에 맞추면 늘어나는 땅")
by_jimok(rem50, "필지에 맞추면 빠지는 땅  ")
# 어긋난 땅의 덩어리(연결 조각) 상위
def top_pieces(g, label, k=8):
    parts = list(g.geoms) if hasattr(g, "geoms") else [g]
    parts = sorted(parts, key=lambda p: -p.area)
    print(f"    {label} 조각 {len(parts)}개, 상위:", ", ".join(f"{p.area:,.0f}㎡@({p.centroid.x:.0f},{p.centroid.y:.0f})" for p in parts[:k]))
top_pieces(add50, "늘어나는 땅"); top_pieces(rem50, "빠지는 땅")

# E. 외곽선 편차: U 외곽선 위 1m 간격 점 → P50a 외곽선까지 거리
ring = U.exterior
Pring = P50a.boundary
n = int(ring.length)
dist = np.array([Pring.distance(ring.interpolate(t)) for t in np.linspace(0, ring.length, n, endpoint=False)])
print(f"\n[E] U 외곽선 {ring.length:,.0f}m 중 필지선(v3규칙)까지 거리:")
for th in (0.5, 1, 2, 3, 5, 10, 20):
    print(f"    ≤{th:>4}m : {np.mean(dist<=th)*100:5.1f}%  ({np.sum(dist<=th)} m)")
print(f"    평균 {dist.mean():.1f}m, 중앙값 {np.median(dist):.1f}m, 최대 {dist.max():.1f}m (Hausdorff 근사)")
pr_d = np.array([ring.distance(Pring.interpolate(t)) for t in np.linspace(0, Pring.length, int(Pring.length), endpoint=False)])
print(f"    반대방향(필지선→U선) 최대 {pr_d.max():.1f}m, 평균 {pr_d.mean():.1f}m")

# F. 변별 편차 (U 의 58점 꼭짓점 사이 구간)
coords = list(ring.coords)
segs = []
for a, b in zip(coords[:-1], coords[1:]):
    s = LineString([a, b]); L = s.length
    if L < 0.5: continue
    k = max(2, int(L))
    ds = np.array([Pring.distance(s.interpolate(t, normalized=True)) for t in np.linspace(0, 1, k)])
    segs.append((a, b, L, ds.max(), ds.mean()))
bad = [s for s in segs if s[3] > 3.0]
print(f"\n[F] 구간 {len(segs)}개 중 필지선에서 3m 넘게 벗어나는 구간 {len(bad)}개")
for a, b, L, mx, me in sorted(bad, key=lambda s: -s[3])[:15]:
    print(f"    ({a[0]:.0f},{a[1]:.0f})→({b[0]:.0f},{b[1]:.0f}) 길이 {L:.0f}m 최대편차 {mx:.1f}m 평균 {me:.1f}m")

# G. 어긋난 면적이 큰 필지 상위 (선이 필지를 가르는 곳)
print("\n[G] 선이 가르는 필지 중 큰 것 (바깥/안쪽 면적 기준 상위 12)")
for x in sorted(cut, key=lambda x: -min(x["inter"], x["area"] - x["inter"]))[:12]:
    print(f"    {x['addr'].replace('경상북도 경주시 ','')} [{x['jimok']}] 필지 {x['area']:,.0f}㎡ 중 U안 {x['inter']:,.0f}㎡ ({x['share']*100:.0f}%) → {'편입' if x['share']>=0.5 else '제외'}")

# 결과 저장 (그림용)
pickle.dump(dict(U=U.wkb, zone=zone.wkb, P50a=P50a.wkb, P_in=P_in.wkb, P_out=P_out.wkb, add=add50.wkb, rem=rem50.wkb,
                 sel=[x["i"] for x in sel], rows=[(x["i"], x["share"]) for x in rows]), open(SP + r"\step2.pkl", "wb"))
