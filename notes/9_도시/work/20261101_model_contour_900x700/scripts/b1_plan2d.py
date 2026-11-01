# 모형용 콘타 900x700(1:1500, mm) 2D 정리
# 입력: data/frame_src.json(라이노 평지콘타에서 뽑은 바닥 윤곽·높이, 출력 좌표로 이동 완료)
#       data/model_bnd_frame.json(사용자 선택 프레임·최종 대지경계선), data/xf_5179.json(EPSG:5179 → 모델)
#       data/eupseong_model.json(OSM 경주읍성 성벽·향일문, 모델 좌표)
# 출력: data/plan2d.json — 층별 폴리곤·각인선·건물 목록
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import shapely
from pyproj import Transformer
from shapely.geometry import LineString, MultiLineString, MultiPoint, Point, Polygon
from shapely.ops import linemerge, substring, unary_union

sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).resolve().parents[1]
D = W / "data"
ARC = W.parents[1] / "archive" / "C_data" / "processed"

SC = 1500.0                  # 축척
MM = 1000.0 / SC             # 실제 1 m = 0.6667 mm
SIMP = 0.005                 # 일직선 꼭짓점 정리 허용오차(mm)
MIN_PART = 0.05              # 버리는 조각 면적(mm²)
NOZZLE_MIN_W = 0.8           # 출력 최소 폭(mm) — 이보다 좁은 건물은 확인용 레이어로

src = json.load(open(D / "frame_src.json", encoding="utf-8"))
fb = json.load(open(D / "model_bnd_frame.json"))
F = Polygon(fb["frame"])
S = Polygon(fb["boundary"])
xf = json.load(open(D / "xf_5179.json"))
_s, _R, _t = xf["s"], np.array(xf["R"]), np.array(xf["t"])
_T = Transformer.from_crs(4326, 5179, always_xy=True)


def ll2m(lon, lat):
    return tuple((_s * (_R @ np.array(_T.transform(lon, lat))) + _t).tolist())


def polys(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [p for h in getattr(g, "geoms", []) for p in polys(h)]


def lines(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type == "LinearRing":
        return [LineString(g.coords)]
    return [p for h in getattr(g, "geoms", []) for p in lines(h)]


def pinched(q):
    """외곽선·구멍이 한 점에서 자기 자신과 맞닿는가(라이노에서 길이 0인 변이 된다)"""
    for r in [q.exterior] + list(q.interiors):
        c = [tuple(np.round(x, 4)) for x in r.coords[:-1]]
        if len(c) != len(set(c)):
            return True
    return False


def clean(p):
    p = p.buffer(0).simplify(SIMP, preserve_topology=True)
    out = []
    for q in polys(p):
        if pinched(q):        # 맞닿은 점을 0.002 mm 벌려 분리
            q = q.buffer(-0.003, join_style="mitre").buffer(0.002, join_style="mitre")
        out += [x for x in polys(q) if x.area >= MIN_PART]
    return out


def pj(p):
    return {"ext": [list(c) for c in p.exterior.coords[:-1]],
            "holes": [[list(c) for c in r.coords[:-1]] for r in p.interiors],
            "area": p.area}


# ---------------------------------------------------------------- 원본 조각
cat = defaultdict(list)
blds = []
for it in src["items"]:
    outer = [l[1] for l in it["loops"] if l[0]][0]
    holes = [l[1] for l in it["loops"] if not l[0]]
    g = Polygon(outer, holes)
    if not g.is_valid:
        g = shapely.make_valid(g)
    if it["cat"] == "빌딩":
        blds.append({"id": it["id"], "g": g, "h": it["h"]})
    else:
        cat[it["cat"]].append(g)

river_all = unary_union(cat["하천"])
river_pieces = [p for p in polys(river_all)]
R = river_all.intersection(F)
L_all = unary_union(cat["대지"])
# 인도는 원래 인도 라인만 쓴다. 경계석(폭 약 18 cm 띠)을 합치면 띠와 인도 사이 수 cm 틈이
# 가는 균열(구멍 118개)로 남아 출력·라이싱지 재단선이 갈라졌다 → 경계석은 쓰지 않는다.
SW_all = unary_union(cat["인도"])
# 인도 안의 구멍 중 대지로 채워지지 않은 것(나무 둘레 등)은 메운다
_sw = []
for p in polys(SW_all):
    keep = [h for h in p.interiors if Polygon(h).intersection(L_all).area > 0.5 * Polygon(h).area]
    _sw.append(Polygon(p.exterior, keep))
SW_all = unary_union(_sw)
ROAD_all = unary_union(cat["도로"])

# ---------------------------------------------------------------- 다리·철교
# 하천 조각 사이를 잇는 비하천 영역 = 다리. 닫힘(closing)으로 하천 회랑을 메운 뒤 하천을 뺀다.
corr = river_all.buffer(25.0).buffer(-25.0)
gap = corr.difference(river_all).buffer(-0.3).buffer(0.3)
rail = json.load(open(ARC / "rail_lines_4326.geojson", encoding="utf-8"))
rail_m = unary_union([LineString([ll2m(*c) for c in f["geometry"]["coordinates"]])
                      for f in rail["features"] if f["geometry"]["type"] == "LineString"])
# 북천 위 다리 3개(사용자 지정): 경주교(원화로) · 동해선 철교(폐선) · 북천 자전거길 다리.
# 원본 콘타에는 다리 상판이 없거나(철교·자전거교) 보도 띠만 있다(경주교) → OSM 중심선으로 다시 만든다.
# 범위는 사용자 사진처럼 둔치를 건너 제방 도로(알천남로 ↔ 알천북로)까지. 폭·교각은 일반형 가정.
ob = json.load(open(D / "osm_bridges_model.json", encoding="utf-8"))
osm_axis = {e["id"]: LineString(e["pts"]) for e in ob if "bridge" in e["tags"]}
nl0 = json.load(open(ARC / "nodelink_gj_4326.geojson", encoding="utf-8"))
embank = unary_union([LineString([ll2m(*c) for c in f["geometry"]["coordinates"]]) for f in nl0["features"]
                      if f["properties"].get("ROAD_NAME") in ("알천북로", "알천남로")])


def span_between_embankments(axis, over=6.0 * MM):
    """축을 양방향으로 길게 늘려 하천 양쪽의 제방 도로와 만나는 점 사이(+여유)를 돌려준다."""
    c = np.array(axis.coords); v = c[-1] - c[0]; v /= np.linalg.norm(v)
    mid = np.array(axis.interpolate(0.5, normalized=True).coords[0])
    long = LineString([mid - v * 400, mid + v * 400])
    t_mid = long.project(Point(mid))
    x = long.intersection(embank)
    ts = sorted(long.project(q) for q in getattr(x, "geoms", [x]) if q.geom_type == "Point")
    lo = max([x for x in ts if x < t_mid], default=t_mid - axis.length / 2)
    hi = min([x for x in ts if x > t_mid], default=t_mid + axis.length / 2)
    return substring(long, lo - over, hi + over)


def mid_line(a, b):
    b2 = b if Point(a.coords[0]).distance(Point(b.coords[0])) < Point(a.coords[0]).distance(Point(b.coords[-1])) else LineString(list(b.coords)[::-1])
    return LineString([((p.x + q.x) / 2, (p.y + q.y) / 2) for p, q in
                       ((a.interpolate(t, normalized=True), b2.interpolate(t, normalized=True)) for t in np.linspace(0, 1, 20))])


rail_axis = max([l for l in lines(rail_m) if l.distance(osm_axis[177849860]) < 1.0] or [osm_axis[177849860]],
                key=lambda l: l.intersection(osm_axis[177849860].buffer(1.0)).length)
BRIDGE_SPEC = [  # 이름, 축, 폭(m), 교각 간격(m), 교각 두께(m)
    ("경주교", mid_line(osm_axis[42409266], osm_axis[1165014304]), 28.0, 20.0, 1.5),
    ("동해선 철교(폐선)", osm_axis[177849860], 6.0, 20.0, 2.0),
    ("북천 자전거길 다리", osm_axis[557116343], 5.0, 25.0, 1.0),
]
bridge_models, bridges, rail_bridges, bike_bridges = [], [], [], []
for name, axis, width, span, pt in BRIDGE_SPEC:
    A = span_between_embankments(axis)
    P_full = unary_union(clean(A.buffer(width * MM / 2, cap_style="flat").intersection(F).difference(S)))
    if P_full.is_empty:
        continue
    P_ch = unary_union(clean(P_full.intersection(river_all.buffer(1.0 * MM))))   # 물길 위 구간(색지만 걸침)
    piers = []
    dd = span * MM / 2
    while dd <= A.length:
        p = A.interpolate(dd)
        if river_all.buffer(-1.0).contains(p) and F.contains(p):
            a0, a1 = A.interpolate(max(dd - 0.5, 0)), A.interpolate(min(dd + 0.5, A.length))
            v = np.array([a1.x - a0.x, a1.y - a0.y]); v /= np.linalg.norm(v); n = np.array([-v[1], v[0]])
            c = np.array([p.x, p.y]); hl = pt * MM / 2; hw = (width - 2.0) * MM / 2
            piers += clean(Polygon([c - v * hl - n * hw, c + v * hl - n * hw, c + v * hl + n * hw, c - v * hl + n * hw]).intersection(P_full))
        dd += span * MM
    bridge_models.append({"name": name, "width_m": width, "span_m": span,
                          "plan": [pj(q) for q in polys(P_full)], "deck": [pj(q) for q in polys(P_ch)],
                          "piers": [pj(q) for q in piers], "axis": list(map(list, A.coords))})
    {"경주교": bridges, "동해선 철교(폐선)": rail_bridges}.get(name, bike_bridges).extend(polys(P_full))
    print("bridge", name, "span %.0f m" % (A.length / MM), "in frame plan %.0f m2" % (P_full.area / MM / MM), "piers", len(piers))
BR = unary_union(bridges + rail_bridges + bike_bridges)
BR_CH = unary_union([q for b in bridge_models for q in [Polygon(d["ext"], d["holes"]) for d in b["deck"]]])

# ---------------------------------------------------------------- 층별 영역
L = L_all.intersection(F).difference(S).difference(BR)    # 둔치 위를 지나는 다리 자리는 출력에서 뺀다
SW = SW_all.intersection(F).difference(S).difference(BR)
# 대지와 인도 사이에 끼어 있던 경계석 자리(폭 약 18 cm + 수 cm 틈)를 비워 두면 출력물 사이 가는 홈이 된다
# → 닫힘(30 cm)으로 생기는 대지·인도 사이 틈 가운데 경계석 자리와 겹치는 것만 인도에 붙인다(도로 쪽은 색지)
_cb = unary_union(cat["경계석"])
_U = unary_union([L, SW])
_cl = _U.buffer(0.15 * MM, join_style="mitre").buffer(-0.15 * MM, join_style="mitre")
_fill = [g for g in polys(_cl.difference(_U)) if g.intersects(_cb) and g.buffer(0.02 * MM).intersects(SW)]
SW = unary_union([SW] + _fill)
# 합칠 때 생긴 1 m² 미만 바늘구멍은 없앤다
SW = unary_union([Polygon(p.exterior, [h for h in p.interiors if Polygon(h).area >= 1.0 * MM * MM]) for p in polys(SW)])
print("대지·인도 사이 경계석 자리 메움: %d곳, %.1f m2" % (len(_fill), sum(g.area for g in _fill) / MM / MM))
foam2_cut = unary_union([R, BR_CH.intersection(F)])       # 2t: 하천 + 다리 밑(물길 연속)
paper_cut = R.difference(BR)                               # 색지: 하천만(다리 상판은 남김)
R = paper_cut
FOAM2 = F.difference(foam2_cut)
PAPER = F.difference(paper_cut)
PRINT_FOOT = unary_union([L, SW])                          # 3D 출력 바닥 윤곽 = 대지선 각인

# ---------------------------------------------------------------- 중요거점
KEY = {
    "황오커뮤니티센터": ["1a422389"],
    "경주시청년센터 청년고도": ["aa5b7489"],
    "성동시장": ["9960860a"],
    "경주농협 농산물공판장": ["0b6b0315", "d5770cd2"],
    "황촌마을활력소": ["be634301"],
    "황촌상권활력소": ["cefcb711"],
}
key_of = {k8: name for name, ks in KEY.items() for k8 in ks}

bld_out = defaultdict(list)
stat = Counter()
for b in blds:
    g = b["g"].intersection(F).difference(S)
    parts = clean(g)
    if not parts:
        stat["outside_or_site"] += 1
        continue
    k = key_of.get(b["id"][:8])
    for p in parts:
        thin = p.buffer(-NOZZLE_MIN_W / 2).is_empty
        layer = ("key:" + k) if k else ("thin" if thin else "bld")
        bld_out[layer].append({"id": b["id"], "h": b["h"], "poly": pj(p)})
        stat[layer if not k else "key"] += 1

# 경주읍성 성벽·향일문(OSM 위치, 치수 가정)
eu = json.load(open(D / "eupseong_model.json", encoding="utf-8"))
WALL_W, WALL_H = 7.0 * MM, 5.0 * MM            # 성벽 폭 7 m, 높이 5 m (가정)
GATE_L, GATE_D, GATE_H = 14.0 * MM, 10.0 * MM, 9.0 * MM   # 향일문 문루 14x10 m, 9 m (가정)
walls = unary_union([LineString(v["pts"]) for v in eu.values() if v["tags"].get("barrier") == "city_wall"])
gate_pt = Point([v["pts"][0] for v in eu.values() if v["tags"].get("historic") == "city_gate"][0])
wall_poly = walls.buffer(WALL_W / 2, cap_style="flat", join_style="mitre").intersection(F).difference(S)
# 문루 방향 = 가장 가까운 성벽 선분 방향
near = min(lines(walls), key=lambda l: l.distance(gate_pt))
dpos = near.project(gate_pt)
a, b2 = near.interpolate(max(dpos - 1, 0)), near.interpolate(min(dpos + 1, near.length))
v = np.array([b2.x - a.x, b2.y - a.y]); v /= np.linalg.norm(v); n = np.array([-v[1], v[0]])
gp = np.array(near.interpolate(dpos).coords[0])
gate = Polygon([gp - v * GATE_L / 2 - n * GATE_D / 2, gp + v * GATE_L / 2 - n * GATE_D / 2,
                gp + v * GATE_L / 2 + n * GATE_D / 2, gp - v * GATE_L / 2 + n * GATE_D / 2])
wall_poly = wall_poly.difference(gate)
for p in clean(wall_poly):
    bld_out["key:경주읍성 향일문"].append({"id": "osm_city_wall", "h": WALL_H, "poly": pj(p)})
bld_out["key:경주읍성 향일문"].append({"id": "osm_city_gate", "h": GATE_H, "poly": pj(gate)})
# 성벽·문루와 겹치는 일반 건물은 확인 대상으로 표시
eu_g = unary_union([wall_poly, gate])
overlap_ids = [x["id"] for x in bld_out["bld"] if Polygon(x["poly"]["ext"]).intersects(eu_g)]

# ---------------------------------------------------------------- 도로 중앙선·차선
road = ROAD_all.intersection(F).difference(S)
road_pts = []
for p in polys(road):
    for ring in [p.exterior] + list(p.interiors):
        road_pts += list(shapely.segmentize(LineString(ring.coords), 0.6).coords)
vor = shapely.voronoi_polygons(MultiPoint(road_pts), only_edges=True)
from shapely.prepared import prep
road_in = prep(road.buffer(-0.05))
bnd = road.boundary
edges = []
for e in lines(vor):
    if not road_in.contains(e):
        continue
    hw = bnd.distance(e.centroid)
    if hw >= 2.4:                     # 반폭 2.4 mm(3.6 m) 이상 = 폭 7.2 m 이상 도로
        edges.append((e, hw))
# 그래프 정리: 짧은 가지 제거
def key(p):
    return (round(p[0], 3), round(p[1], 3))
adj = defaultdict(list)
for i, (e, hw) in enumerate(edges):
    c = list(e.coords)
    adj[key(c[0])].append(i); adj[key(c[-1])].append(i)
alive = set(range(len(edges)))
for _ in range(60):
    deg = {k: len([i for i in v if i in alive]) for k, v in adj.items()}
    removed = 0
    for i in list(alive):
        c = list(edges[i][0].coords)
        if (deg[key(c[0])] == 1 or deg[key(c[-1])] == 1) and edges[i][0].length < 3.0:
            alive.discard(i); removed += 1
    if not removed:
        break
skel = linemerge(MultiLineString([edges[i][0] for i in alive]))
# 교차부(차수 3 이상) 주변은 중앙선을 끊는다(횡단보도·교차로 구간)
deg = Counter()
for i in alive:
    c = list(edges[i][0].coords); deg[key(c[0])] += 1; deg[key(c[-1])] += 1
junc = [Point(k) for k, d in deg.items() if d >= 3]
jzone = unary_union([j.buffer(bnd.distance(j) * 1.3 + 2.0) for j in junc]) if junc else Polygon()
center = []
for l in lines(skel):
    l = l.simplify(0.25)
    for q in lines(l.difference(jzone)):
        if q.length >= 6.0:
            center.append(q)
# 표준노드링크(방향별 차로수) → 차선(백색 점선)
nl = json.load(open(ARC / "nodelink_gj_4326.geojson", encoding="utf-8"))
links = []
for f in nl["features"]:
    g = LineString([ll2m(*c) for c in f["geometry"]["coordinates"]])
    if g.intersects(F):
        links.append((g, int(f["properties"].get("LANES") or 1)))
ltree = shapely.STRtree([g for g, _ in links])
lane_lines, center_kept = [], []
DASH, GAP = 10.0 * MM, 10.0 * MM
for c in center:
    idx = ltree.query(c.buffer(6.0))
    if len(idx) == 0:
        continue                                   # 노드링크가 없는 넓은 공터·주차장은 제외
    lanes = max(links[i][1] for i in idx)
    center_kept.append(c)
    if lanes < 2:
        continue
    hw = float(np.median([bnd.distance(c.interpolate(t, normalized=True)) for t in np.linspace(0.1, 0.9, 7)]))
    for k in range(1, lanes):
        off = hw * k / lanes
        for side in (1, -1):
            ol = c.offset_curve(side * off)
            for q in lines(ol):
                dd = 0.0
                while dd < q.length:
                    seg = substring(q, dd, min(dd + DASH, q.length))
                    if seg.length > 0.5 and road.buffer(-0.2).contains(seg):
                        lane_lines.append(seg)
                    dd += DASH + GAP

out = {
    "scale": SC, "frame": pj(F), "site": pj(S),
    "foam2": [pj(p) for p in polys(FOAM2)],
    "paper": [pj(p) for p in polys(PAPER)],
    "river": [pj(p) for p in clean(R)],
    "land": [pj(p) for p in clean(L)],
    "sidewalk": [pj(p) for p in clean(SW)],
    "print_outline": [pj(p) for p in clean(PRINT_FOOT)],
    "bridges": [pj(p) for p in bridges],
    "rail_bridges": [pj(p) for p in rail_bridges],
    "bike_bridges": [pj(p) for p in bike_bridges],
    "bridge_models": bridge_models,
    "center_lines": [list(map(list, l.coords)) for l in center_kept],
    "lane_lines": [list(map(list, l.coords)) for l in lane_lines],
    "buildings": bld_out,
    "eupseong_overlap_bld": overlap_ids,
}
json.dump(out, open(D / "plan2d.json", "w", encoding="utf-8"), ensure_ascii=False)
print("frame %.1f x %.1f mm" % (F.bounds[2] - F.bounds[0], F.bounds[3] - F.bounds[1]))
print("river parts", len(out["river"]), "area %.0f" % R.area, "| bridges", len(bridges), "rail bridges", len(rail_bridges))
print("land", len(out["land"]), "sidewalk", len(out["sidewalk"]), "holes in biggest sidewalk", max((len(p["holes"]) for p in out["sidewalk"]), default=0))
print("buildings", {k: len(v) for k, v in bld_out.items()}, dict(stat))
print("center lines", len(center_kept), "total %.0f mm" % sum(l.length for l in center_kept), "| lane dashes", len(lane_lines))
print("eupseong overlaps general buildings:", overlap_ids)
