# -*- coding: utf-8 -*-
"""경주 원도심(S2) 도시조직 지표 표본 계산 — 03_경주_도시조직_지표_산출법.md 의 [산정] 수치 근거.

입력
- work/20261011_masterplan_rough/data/ctx_fixed.pkl : 건물 22,621동 (로컬 좌표, h = 층수 x 3.5 m)
- 대지/(B020)연속수치지도_202609132098/ : 국토지리정보원 연속수치지도 (EPSG:5179, T2)
    N3L_A0020000 도로중심선(rvwd 폭) / N3A_A0010000 도로경계 / N3L_A0171119 철도중심선 / N3A_A0160024 철도경계
    N3A_E0010001 하천경계 / N3L_E0020000 하천중심선(name) / N3A_G0110000 법정동 경계 / N3L_A0033320 인도(widt)
    N3A_B0010000 건물(nmly 층수, bjcd) — 교차검증용
- archive/C_data/processed/gosi2026-8_zone_5187.geojson, parks_upis_4326.geojson, facilities_4326.geojson, stores_merged_4326.geojson
- archive/C_data/raw/bldg_title.json : 건축물대장 표제부 (T1)

좌표: 모두 EPSG:5187 로 변환해 계산. 로컬 → 5179 : E = local − (TX − X0, TY − Y0), (TX,TY)=(11616.3843, −796.58), (X0,Y0)=(1166600, 1761100)
       (work/20261011_masterplan_rough/README.md v2 절, real_overlay.pkl·design.pkl 상수). 계획 경계 B 변환 결과가 고시 구역의 99.84%를 포함함을 확인.

출력
- data/fabric_faces_20261024.csv  : 가구(가로망 면) 단위 지표 전체
- data/fabric_summary_20261024.json : 요약 수치
"""
import os, sys, json, math, pickle, collections, statistics as st
import numpy as np
import shapefile, shapely
from shapely.geometry import shape, Point, box, LineString, MultiLineString
from shapely.ops import unary_union, polygonize
from shapely.strtree import STRtree
from shapely import affinity
from pyproj import Transformer

ROOT = r"C:\Users\OFFICE\Desktop\9_도시"
SRC = os.path.join(ROOT, "대지", "(B020)연속수치지도_202609132098")
PROC = os.path.join(ROOT, "archive", "C_data", "processed")
RAW = os.path.join(ROOT, "archive", "C_data", "raw")
OUT = os.path.join(ROOT, "work", "20261024_forma_method", "research", "data")
os.makedirs(OUT, exist_ok=True)

TX, TY, X0, Y0 = 11616.3843, -796.58, 1166600.0, 1761100.0
DX, DY = TX - X0, TY - Y0                     # local = 5179 + (DX, DY)
T79 = Transformer.from_crs("EPSG:5179", "EPSG:5187", always_xy=True)
T26 = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True)
ZONE_C = (219776.9, 360961.0)                 # 고시 구역 중심(5187), public_profile_20260928.json
S2_R = 1000.0
FLOOR_H = 3.5                                 # pkl 높이 = 층수 x 3.5 m (연속수치지도 nmly 와 1:1 대응 확인)
DONG = {"4713010400": "성동동", "4713010500": "황오동", "4713010600": "노동동", "4713010700": "노서동", "4713010800": "성건동",
        "4713010100": "동부동", "4713010200": "서부동", "4713010300": "북부동", "4713010900": "사정동", "4713011000": "황남동",
        "4713011200": "인왕동", "4713012200": "구황동", "4713012400": "황성동", "4713012600": "동천동", "4713012500": "용강동"}
S2_DONGS = ["황오동", "성동동", "노서동", "노동동"]


def tf(g, tr):
    return shapely.transform(g, lambda a: np.column_stack(tr.transform(a[:, 0], a[:, 1])))


def local_to_5187(g):
    return shapely.transform(g, lambda a: np.column_stack(T79.transform(a[:, 0] - DX, a[:, 1] - DY)))


def fix(s):
    try:
        return s.encode("latin-1").decode("cp949")
    except Exception:
        return s


def read(layer, want=None):
    r = shapefile.Reader(os.path.join(SRC, layer), encoding="utf-8")
    f = [x[0] for x in r.fields[1:]]
    out = []
    for sr in r.iterShapeRecords():
        g = shape(sr.shape.__geo_interface__)
        if g.is_empty:
            continue
        g = tf(g, T79)
        rec = {k: fix(str(v)) for k, v in zip(f, sr.record)} if want is None else {k: fix(str(sr.record[f.index(k)])) for k in want}
        out.append((g, rec))
    return out


def q(a, p):
    a = sorted(a)
    if not a:
        return None
    k = (len(a) - 1) * p / 100.0
    i = int(math.floor(k)); j = min(i + 1, len(a) - 1)
    return a[i] + (a[j] - a[i]) * (k - i)


def mrr_sides(g):
    r = g.minimum_rotated_rectangle
    c = list(r.exterior.coords)
    d = sorted([math.dist(c[0], c[1]), math.dist(c[1], c[2])])
    return d[0], d[1]


S = {}
# ---------------------------------------------------------------- 1. 건물 (pkl)
d = pickle.load(open(os.path.join(ROOT, "work", "20261011_masterplan_rough", "data", "ctx_fixed.pkl"), "rb"))
B = []
for b in d["B"]:
    g = local_to_5187(b["g"]).buffer(0)
    if g.is_empty:
        continue
    fl = int(round(b["h"] / FLOOR_H))
    B.append(dict(g=g, h=b["h"], fl=max(fl, 1), area=g.area, inside=bool(b["inside"]), id=b["id"]))
S["pkl_n"] = len(B)
S["pkl_floor_hist"] = dict(sorted(collections.Counter(b["fl"] for b in B).items()))
S["pkl_h_is_multiple_of_3p5"] = sum(1 for b in d["B"] if abs(b["h"] / FLOOR_H - round(b["h"] / FLOOR_H)) < 1e-6) / len(d["B"])
print("buildings", len(B), "floor hist", S["pkl_floor_hist"])

# ---------------------------------------------------------------- 2. 수치지도 레이어
roads = read("N3L_A0020000", ["rvwd", "rddv", "rdnm", "name"])
road_poly = [g for g, _ in read("N3A_A0010000")]
rail_c = [g for g, _ in read("N3L_A0171119")]
rail_poly = [g for g, _ in read("N3A_A0160024")]
river_poly = [g for g, _ in read("N3A_E0010001")]
river_c = read("N3L_E0020000", ["name", "type"])
walk = read("N3L_A0033320", ["widt", "kind"])
dong_poly = [(g, r) for g, r in read("N3A_G0110000", ["bjcd", "name"]) if r["bjcd"].startswith("47130")]
shp_b = read("N3A_B0010000", ["nmly", "bjcd"])
ext = box(*unary_union([g for g, _ in roads]).bounds)
S["extent_km2"] = round(ext.area / 1e6, 2)
S["shp_floor_hist"] = dict(sorted(collections.Counter(int(r["nmly"]) for _, r in shp_b if r["nmly"].isdigit()).items()))
S["river_names"] = sorted(set(r["name"] for _, r in river_c if r["name"]))
print("roads", len(roads), "road_poly", len(road_poly), "river", len(river_poly), S["river_names"], "dong", len(dong_poly))

# ---------------------------------------------------------------- 3. 가구(면) = 도로중심선 + 철도중심선 + 하천경계 + 범위 로 polygonize
pieces = [g for g, _ in roads] + rail_c + [p.exterior for p in river_poly] + [ext.exterior]
net = unary_union(pieces)
faces = [f for f in polygonize(net) if f.area >= 50]
print("faces", len(faces))
rp_tree = STRtree(road_poly)
rail_u = unary_union(rail_poly)
river_u = unary_union(river_poly)
dong_tree = STRtree([g for g, _ in dong_poly])
zone = shape(json.load(open(os.path.join(PROC, "gosi2026-8_zone_5187.geojson"), encoding="utf-8"))["features"][0]["geometry"]).buffer(0)
s2_circle = Point(*ZONE_C).buffer(S2_R, 128)
ext_in = ext.buffer(-5)

F = []
for i, f in enumerate(faces):
    rp = f.representative_point()
    # island = face − 도로면 − 철도 − 하천
    sub = [road_poly[j] for j in rp_tree.query(f, predicate="intersects")]
    isl = f.difference(unary_union(sub)) if sub else f
    if isl.intersects(rail_u):
        isl = isl.difference(rail_u)
    if isl.intersects(river_u):
        isl = isl.difference(river_u)
    dj = dong_tree.query(rp, predicate="within")
    dcode = dong_poly[dj[0]][1]["bjcd"] if len(dj) else ""
    F.append(dict(fid=i, g=f, isl=isl, area=f.area, isl_area=max(isl.area, 0.0), rp=rp, dong=DONG.get(dcode, dcode),
                  dist_c=rp.distance(Point(*ZONE_C)), in_s2=(rp.distance(Point(*ZONE_C)) <= S2_R), edge=(not f.within(ext_in)),
                  touch_zone=f.intersects(zone), n=0, fp=0.0, fa=0.0, fls=[], fp_in_zone=0.0))

face_tree = STRtree([x["g"] for x in F])
unmatched = 0
for b in B:
    j = face_tree.query(b["g"].representative_point(), predicate="within")
    if len(j) == 0:
        unmatched += 1
        continue
    x = F[j[0]]
    x["n"] += 1; x["fp"] += b["area"]; x["fa"] += b["area"] * b["fl"]; x["fls"].append(b["fl"])
    b["fid"] = x["fid"]
S["pkl_unmatched_to_face"] = unmatched

for x in F:
    a, ia = x["area"], x["isl_area"]
    x["gsi_f"] = x["fp"] / a
    x["fsi_f"] = x["fa"] / a
    x["gsi_i"] = x["fp"] / ia if ia > 1 else None
    x["fsi_i"] = x["fa"] / ia if ia > 1 else None
    x["L"] = x["fa"] / x["fp"] if x["fp"] > 0 else None
    x["osr_f"] = (1 - x["gsi_f"]) / x["fsi_f"] if x["fsi_f"] > 0 else None
    x["tare"] = 1 - ia / a if a > 0 else None
    x["fl_p50"] = st.median(x["fls"]) if x["fls"] else None
    x["fl_max"] = max(x["fls"]) if x["fls"] else None
    x["share_1f"] = (sum(1 for v in x["fls"] if v == 1) / x["n"]) if x["n"] else None
    s, l = mrr_sides(x["g"]) if x["area"] > 0 else (None, None)
    x["mrr_short"], x["mrr_long"] = s, l
    x["dist_river"] = x["rp"].distance(river_u)

# ---------------------------------------------------------------- 4. 집계 함수
def agg(sel, label):
    sel = list(sel)
    A = sum(x["area"] for x in sel); IA = sum(x["isl_area"] for x in sel)
    FP = sum(x["fp"] for x in sel); FA = sum(x["fa"] for x in sel)
    fls = [v for x in sel for v in x["fls"]]
    urb = [x for x in sel if x["n"] >= 3 and 1000 <= x["area"] <= 50000]      # 시가지 가구(필터)
    out = dict(label=label, n_faces=len(sel), n_urban_faces=len(urb), area_ha=round(A / 1e4, 1), island_ha=round(IA / 1e4, 1),
               tare=round(1 - IA / A, 3) if A else None, n_bldg=len(fls), footprint_ha=round(FP / 1e4, 2), floor_area_ha=round(FA / 1e4, 2),
               GSI_fabric=round(FP / A, 3) if A else None, FSI_fabric=round(FA / A, 3) if A else None,
               GSI_island=round(FP / IA, 3) if IA else None, FSI_island=round(FA / IA, 3) if IA else None,
               L=round(FA / FP, 2) if FP else None, OSR_fabric=round((1 - FP / A) / (FA / A), 2) if FA else None,
               floors_p50=st.median(fls) if fls else None, floors_mean=round(st.mean(fls), 2) if fls else None,
               share_1f=round(sum(1 for v in fls if v == 1) / len(fls), 3) if fls else None,
               share_le2f=round(sum(1 for v in fls if v <= 2) / len(fls), 3) if fls else None,
               share_ge5f=round(sum(1 for v in fls if v >= 5) / len(fls), 3) if fls else None,
               floors_max=max(fls) if fls else None, floor_hist=dict(sorted(collections.Counter(fls).items())))
    if urb:
        for k, key in [("gsi_f", "GSI_fabric"), ("gsi_i", "GSI_island"), ("fsi_f", "FSI_fabric"), ("fsi_i", "FSI_island"), ("L", "L"), ("osr_f", "OSR_fabric")]:
            v = [x[k] for x in urb if x[k] is not None]
            out["urban_" + key + "_p25_p50_p75"] = [round(q(v, 25), 3), round(q(v, 50), 3), round(q(v, 75), 3)]
        out["urban_face_area_p25_p50_p75"] = [round(q([x["area"] for x in urb], p)) for p in (25, 50, 75)]
        out["urban_island_area_p50"] = round(q([x["isl_area"] for x in urb], 50))
        out["urban_mrr_short_p50"] = round(q([x["mrr_short"] for x in urb], 50), 1)
        out["urban_mrr_long_p50"] = round(q([x["mrr_long"] for x in urb], 50), 1)
        out["urban_tare_p50"] = round(q([x["tare"] for x in urb], 50), 3)
        out["urban_share_1f_p50"] = round(q([x["share_1f"] for x in urb], 50), 3)
        out["urban_fl_max_p50"] = q([x["fl_max"] for x in urb], 50)
        out["urban_dist_river_p50"] = round(q([x["dist_river"] for x in urb], 50))
        out["urban_share_within_300m_river"] = round(sum(1 for x in urb if x["dist_river"] <= 300) / len(urb), 3)
        out["urban_share_within_500m_river"] = round(sum(1 for x in urb if x["dist_river"] <= 500) / len(urb), 3)
        # GSI 구간 분포 (시가지 가구, 면적 가중 없음)
        bins = [0, 0.2, 0.3, 0.4, 0.5, 0.6, 1.01]
        cnt = collections.Counter()
        for x in urb:
            for lo, hi in zip(bins[:-1], bins[1:]):
                if lo <= (x["gsi_i"] or 0) < hi:
                    cnt[f"{lo:.1f}-{hi if hi < 1 else 1.0:.1f}"] += 1
        out["urban_GSI_island_bins"] = dict(cnt)
    return out


S["extent_all"] = agg(F, "모델 범위 전체(가장자리 포함)")
S["s2_circle"] = agg([x for x in F if x["in_s2"] and not x["edge"]], "S2 구역중심 반경 1 km (대표점 기준)")
S["s2_circle_excl_zone"] = agg([x for x in F if x["in_s2"] and not x["edge"] and not x["touch_zone"]], "S2 1 km, 구역 접촉 가구 제외")
S["by_dong"] = {dn: agg([x for x in F if x["dong"] == dn and not x["edge"]], dn) for dn in
                ["황오동", "성동동", "노서동", "노동동", "성건동", "동부동", "서부동", "북부동", "사정동", "황남동", "인왕동", "동천동", "황성동", "구황동"]}
S["s2_four_dongs"] = agg([x for x in F if x["dong"] in S2_DONGS and not x["edge"]], "황오·성동·노서·노동 4개 동 합")

# S1: 구역(계획 경계 안 건물 = inside 플래그) 현황
ins = [b for b in B if b["inside"]]
S["s1_zone"] = dict(area_m2_plan_boundary=228022, n_bldg_inside=len(ins), footprint_m2=round(sum(b["area"] for b in ins)),
                    floor_area_m2=round(sum(b["area"] * b["fl"] for b in ins)), GSI=round(sum(b["area"] for b in ins) / 228022, 4),
                    FSI=round(sum(b["area"] * b["fl"] for b in ins) / 228022, 4),
                    floor_hist=dict(sorted(collections.Counter(b["fl"] for b in ins).items())))

# ---------------------------------------------------------------- 5. 도로 지표 (S2 원 안)
def clip_len(items, poly):
    out = []
    for g, r in items:
        if g.intersects(poly):
            c = g.intersection(poly)
            if c.length > 0:
                out.append((c.length, r))
    return out


rl = clip_len(roads, s2_circle)
Ltot = sum(l for l, _ in rl)
wcls = [("<4 m", 0, 4), ("4-6 m", 4, 6), ("6-8 m", 6, 8), ("8-12 m", 8, 12), ("12-20 m", 12, 20), (">=20 m", 20, 999)]
wd = collections.OrderedDict()
for lab, lo, hi in wcls:
    wd[lab] = round(sum(l for l, r in rl if lo <= float(r["rvwd"]) < hi) / Ltot, 3)
ws = sorted(((float(r["rvwd"]), l) for l, r in rl))
cum = 0; wmed = None
for w, l in ws:
    cum += l
    if cum >= Ltot / 2:
        wmed = w; break
S["roads_s2"] = dict(centerline_km=round(Ltot / 1000, 2), circle_ha=round(s2_circle.area / 1e4, 1),
                     network_density_km_per_km2=round(Ltot / 1000 / (s2_circle.area / 1e6), 2),
                     width_share_by_length=wd, width_median_length_weighted=wmed,
                     road_area_ha=round(unary_union([p.intersection(s2_circle) for p in road_poly if p.intersects(s2_circle)]).area / 1e4, 1))
S["roads_s2"]["road_area_ratio"] = round(S["roads_s2"]["road_area_ha"] / S["roads_s2"]["circle_ha"], 3)
S["roads_s2"]["rail_area_ha"] = round(rail_u.intersection(s2_circle).area / 1e4, 1)
S["roads_s2"]["river_area_ha"] = round(river_u.intersection(s2_circle).area / 1e4, 1)

# 교차점 밀도·막다른 길: 중심선 끝점 그래프(0.5 m 스냅)
def key(p):
    return (round(p[0] * 2) / 2, round(p[1] * 2) / 2)


deg = collections.Counter()
links_in = [g for g, _ in roads if g.representative_point().within(s2_circle)]
for g in links_in:
    geoms = g.geoms if hasattr(g, "geoms") else [g]
    for ln in geoms:
        c = list(ln.coords)
        deg[key(c[0])] += 1; deg[key(c[-1])] += 1
nodes3 = sum(1 for k, v in deg.items() if v >= 3)
nodes1 = sum(1 for k, v in deg.items() if v == 1)
dead_links = 0
for g in links_in:
    geoms = g.geoms if hasattr(g, "geoms") else [g]
    for ln in geoms:
        c = list(ln.coords)
        if deg[key(c[0])] == 1 or deg[key(c[-1])] == 1:
            dead_links += 1
S["roads_s2"].update(n_links=len(links_in), link_len_p50=round(q([g.length for g in links_in], 50), 1),
                     intersections_deg3plus=nodes3, intersection_density_per_km2=round(nodes3 / (s2_circle.area / 1e6), 1),
                     dead_end_nodes=nodes1, dead_end_link_share=round(dead_links / len(links_in), 3))
# 인도
wl = clip_len(walk, s2_circle)
wtot = sum(l for l, r in wl if float(r["widt"]) > 0)
S["walk_s2"] = dict(sidewalk_km=round(sum(l for l, _ in wl) / 1000, 2), with_width_km=round(wtot / 1000, 2),
                    width_share={lab: round(sum(l for l, r in wl if float(r["widt"]) > 0 and lo <= float(r["widt"]) < hi) / wtot, 3) for lab, lo, hi in
                                 [("<1.5 m", 0.01, 1.5), ("1.5-2 m", 1.5, 2), ("2-3 m", 2, 3), ("3-5 m", 3, 5), (">=5 m", 5, 99)]} if wtot else {})

# ---------------------------------------------------------------- 6. 공원·녹지 (UPIS), 시설, 상가 (S2 원)
def read_geojson(name):
    d = json.load(open(os.path.join(PROC, name), encoding="utf-8"))
    out = []
    for f in d["features"]:
        if f["geometry"] is None:
            continue
        g = shape(f["geometry"])
        g = tf(g, T26) if "4326" in name else g
        out.append((g, f["properties"]))
    return out


parks = read_geojson("parks_upis_4326.geojson")
pk = collections.defaultdict(float)
for g, p in parks:
    if g.intersects(s2_circle):
        a = g.intersection(s2_circle).area
        pk[(p.get("lcl_nam", ""), p.get("exc_nam", ""))] += a
S["parks_s2"] = {f"{k[0]}|{k[1]}": round(v / 1e4, 2) for k, v in pk.items()}
S["parks_s2"]["합계_ha"] = round(sum(pk.values()) / 1e4, 2)
S["parks_s2"]["공원녹지율_전체"] = round(sum(pk.values()) / s2_circle.area, 4)
S["parks_s2"]["공원녹지율_집행"] = round(sum(v for k, v in pk.items() if k[1] == "집행") / s2_circle.area, 4)

fac = read_geojson("facilities_4326.geojson")
S["facilities_s2"] = dict(collections.Counter(p.get("kind", "") for g, p in fac if g.within(s2_circle)).most_common())

stores = read_geojson("stores_merged_4326.geojson")
st_in = [(g, p) for g, p in stores if g.within(s2_circle)]
S["stores_s2"] = dict(n=len(st_in), by_lcls=dict(collections.Counter(p.get("indsLclsNm", "") for g, p in st_in).most_common()),
                      share_flr1=round(sum(1 for g, p in st_in if str(p.get("flrNo", "")).strip() == "1") / max(1, sum(1 for g, p in st_in if str(p.get("flrNo", "")).strip() != "")), 3))
# 가구별 업종 혼합 (Shannon, 대분류)
mix = []
for x in F:
    x["n_store"] = 0; x["mix_H"] = None
cnt_face = collections.defaultdict(collections.Counter)
for g, p in st_in:
    j = face_tree.query(g, predicate="within")
    if len(j):
        cnt_face[F[j[0]]["fid"]][p.get("indsLclsNm", "")] += 1
for fid, c in cnt_face.items():
    n = sum(c.values()); F[fid]["n_store"] = n
    if n >= 10:
        ps = [v / n for v in c.values()]
        H = -sum(p * math.log(p) for p in ps) / math.log(len(c)) if len(c) > 1 else 0.0
        F[fid]["mix_H"] = round(H, 3); mix.append(H)
S["stores_s2"]["faces_with_10plus_stores"] = len(mix)
S["stores_s2"]["mix_H_p25_p50_p75"] = [round(q(mix, p), 3) for p in (25, 50, 75)] if mix else None
S["stores_s2"]["stores_per_ha_island_s2"] = round(len(st_in) / (S["s2_circle"]["island_ha"]), 2)

# ---------------------------------------------------------------- 7. 건축물대장 표제부 (법정 건폐율·용적률)
reg = json.load(open(os.path.join(RAW, "bldg_title.json"), encoding="utf-8"))
def fnum(x):
    try:
        return float(x)
    except Exception:
        return None
R = collections.defaultdict(list)
for r in reg:
    if r.get("mainAtchGbCdNm", "").strip() != "주건축물":
        continue
    R[DONG.get("47130" + r["bjdongCd"], r["bjdongCd"])].append(r)
S["register"] = {}
allrows = []
for dn, rows in R.items():
    bc = [fnum(r["bcRat"]) for r in rows if fnum(r["bcRat"]) and 0 < fnum(r["bcRat"]) <= 100]
    vl = [fnum(r["vlRat"]) for r in rows if fnum(r["vlRat"]) and 0 < fnum(r["vlRat"]) <= 1500]
    ok = [r for r in rows if fnum(r["platArea"]) and fnum(r["platArea"]) > 0 and fnum(r["archArea"]) and fnum(r["totArea"])]
    PA = sum(fnum(r["platArea"]) for r in ok); AA = sum(fnum(r["archArea"]) for r in ok); TA = sum(fnum(r["totArea"]) for r in ok)
    yrs = [int(str(r["useAprDay"]).strip()[:4]) for r in rows if str(r["useAprDay"]).strip()[:4].isdigit() and 1800 < int(str(r["useAprDay"]).strip()[:4]) < 2027]
    fl = [fnum(r["grndFlrCnt"]) for r in rows if fnum(r["grndFlrCnt"]) and fnum(r["grndFlrCnt"]) > 0]
    pur = collections.Counter(r["mainPurpsCdNm"].strip() for r in rows)
    S["register"][dn] = dict(n_main=len(rows), bcRat_n=len(bc), bcRat_p25_p50_p75=[round(q(bc, p), 1) for p in (25, 50, 75)],
                             vlRat_n=len(vl), vlRat_p25_p50_p75=[round(q(vl, p), 1) for p in (25, 50, 75)],
                             lot_weighted_BCR=round(AA / PA, 3) if PA else None, lot_weighted_FAR=round(TA / PA, 3) if PA else None,
                             floors_mean=round(st.mean(fl), 2) if fl else None, floors_p50=st.median(fl) if fl else None,
                             useApr_p50=int(st.median(yrs)) if yrs else None, share_30y_plus=round(sum(1 for y in yrs if y <= 1996) / len(yrs), 3) if yrs else None,
                             share_20y_plus=round(sum(1 for y in yrs if y <= 2006) / len(yrs), 3) if yrs else None,
                             purpose_share={k: round(v / len(rows), 3) for k, v in pur.most_common(6)})
    allrows += ok
PA = sum(fnum(r["platArea"]) for r in allrows); AA = sum(fnum(r["archArea"]) for r in allrows); TA = sum(fnum(r["totArea"]) for r in allrows)
S["register"]["5개동 합"] = dict(n=len(allrows), lot_weighted_BCR=round(AA / PA, 3), lot_weighted_FAR=round(TA / PA, 3), platArea_sum_ha=round(PA / 1e4, 1))

# ---------------------------------------------------------------- 8. 저장
cols = ["fid", "dong", "area", "isl_area", "tare", "n", "fp", "fa", "gsi_f", "gsi_i", "fsi_f", "fsi_i", "L", "osr_f", "fl_p50", "fl_max", "share_1f",
        "mrr_short", "mrr_long", "dist_river", "dist_c", "in_s2", "edge", "touch_zone", "n_store", "mix_H"]
import csv
with open(os.path.join(OUT, "fabric_faces_20261024.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh); w.writerow(cols + ["rp_x_5187", "rp_y_5187"])
    for x in F:
        w.writerow([(round(x[c], 4) if isinstance(x[c], float) else x[c]) for c in cols] + [round(x["rp"].x, 1), round(x["rp"].y, 1)])
json.dump(S, open(os.path.join(OUT, "fabric_summary_20261024.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(S, ensure_ascii=False, indent=1, default=str))
