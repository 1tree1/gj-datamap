"""경주 원도심 '시간 층위' 시각화용 레이어 내보내기.

현재 가로를 방위 체계(주 격자 N0.8°E / 사선 A 동천동 / 사선 B 북천 변 / 기타)로 나누고,
철도(동해남부선)·읍성 성벽 현존 구간·구역계·유적 주기·건물 도형-바탕과 함께 한 파일로 묶는다.
좌표는 EPSG:5187 을 원점(ORIGIN) 기준 m 로 옮긴 지역 좌표(정수 0.5 m 반올림) — 웹 SVG 용.

입력: 연속수치지도(NGII, T2, 5179→5187), 고시 제2026-8호 구역계(T1), 상가업소 도로명주소(T2, 간선 이름 부여)
출력: archive/90_derived/palimpsest_layers_20260928.json, archive/90_derived/palimpsest_figureground_20260928.png
"""
import json
import math
import re
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import shapefile
from pyproj import Transformer
from shapely.geometry import Point, box, shape
from shapely.ops import transform as shp_transform
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
OUT = DER / "palimpsest_layers_20260928.json"
OUT_FG = DER / "palimpsest_figureground_20260928.png"
T57 = Transformer.from_crs("EPSG:5179", "EPSG:5187", always_xy=True)
T47 = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True)
VIEW = (218200.0, 359450.0, 221300.0, 362550.0)   # 시각화 창 (5187): 원도심 + 부지 + 월성·황룡사지
ORIGIN = (VIEW[0], VIEW[1])
AX = 89.2          # 주 격자축(선분 방위, 동=0° 반시계, mod 90) — build_fabric_patterns 실측
AXA, AXB = 42.0, 148.0   # 사선 A·B (mod 180)
FG_RES = 1.5       # 도형-바탕 래스터 해상도 (m/px)


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


def loc(coords):
    return [[round((x - ORIGIN[0]) * 2) / 2, round((y - ORIGIN[1]) * 2) / 2] for x, y in coords]


def d90(a, b):
    x = abs((a % 90) - (b % 90))
    return min(x, 90 - x)


def d180(a, b):
    x = abs(a - b) % 180
    return min(x, 180 - x)


vbox = box(*VIEW)

# ── 가로: 조각별 방위 체계 + 간선 이름(상가업소 도로명주소 다수결) ─────────────
pieces = []
for g, a in read("N3L_A0020000"):
    for gg in getattr(g, "geoms", [g]):
        if gg.intersects(vbox.buffer(50)):
            pieces.append((gg, float(a.get("rvwd") or 0)))
ptree = STRtree([p for p, _ in pieces])
vote = defaultdict(Counter)
for f in json.load(open(PROC / "stores_merged_4326.geojson", encoding="utf-8"))["features"]:
    m = re.search(r"경주시\s+(\S+로)\s", (f["properties"].get("rdnmAdr") or "") + " ")
    if not m:
        continue
    pt = Point(*T47.transform(*f["geometry"]["coordinates"][:2]))
    i = int(ptree.nearest(pt))
    if pieces[i][0].distance(pt) <= 30 and pieces[i][1] >= 6:
        vote[i][m.group(1)] += 1
streets = []
for i, (gg, w) in enumerate(pieces):
    cs = list(gg.coords)
    L = gg.length
    if L < 1:
        continue
    # 길이가중 방위 → 체계
    acc = Counter()
    for p, q in zip(cs[:-1], cs[1:]):
        th = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 180
        k = "grid" if d90(th, AX) <= 7.5 else "A" if d180(th, AXA) <= 7.5 else "B" if d180(th, AXB) <= 7.5 else "other"
        acc[k] += math.dist(p, q)
    sysk = acc.most_common(1)[0][0]
    simp = gg.simplify(0.75, preserve_topology=False)
    streets.append({"c": loc(simp.coords), "w": round(w, 1), "s": sysk,
                    "n": vote[i].most_common(1)[0][0] if vote.get(i) else None})

# ── 철도·읍성·구역·유적·물 ─────────────────────────────────────
rail = [{"c": loc(gg.coords), "n": a.get("name")} for g, a in read("N3L_A0171119") for gg in getattr(g, "geoms", [g])]
rail_poly = [{"c": loc(g.exterior.coords)} for g, _ in read("N3A_A0160024")]
wall = [{"c": loc(gg.coords), "n": a.get("name")} for g, a in read("N3L_C0325315") for gg in getattr(g, "geoms", [g])]
zone = shape(json.load(open(PROC / "gosi2026-8_zone_5187.geojson", encoding="utf-8"))["features"][0]["geometry"]).buffer(0)
herit_poly = [{"c": loc(g.exterior.coords), "n": a.get("name")} for g, a in read("N3A_C0305316")
              if g.intersects(vbox) and g.geom_type == "Polygon"]
herit_pt = []
seen = set()
for g, a in read("N3P_H0040000"):
    nm = (a.get("name") or "").split("(")[0].replace("경주", "").strip()
    if a.get("type") == "PNT010" and vbox.contains(g) and nm and nm not in seen:
        seen.add(nm); herit_pt.append({"c": loc([(g.x, g.y)])[0], "n": nm})
station = [{"c": loc(g.exterior.coords)} for g, a in read("N3A_A0191221")]
water = []
for lay in ("N3A_E0010001", "N3A_E0032111"):
    for g, _ in read(lay):
        gi = g.intersection(vbox)
        for gg in getattr(gi, "geoms", [gi]):
            if gg.geom_type == "Polygon" and gg.area > 200:
                water.append({"c": loc(gg.simplify(1.0).exterior.coords)})

# ── 도형-바탕 래스터 (건물) ─────────────────────────────────────
W_px = int((VIEW[2] - VIEW[0]) / FG_RES); H_px = int((VIEW[3] - VIEW[1]) / FG_RES)
fig = plt.figure(figsize=(W_px / 100, H_px / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
polys = []
for g, _ in read("N3A_B0010000"):
    if g.intersects(vbox):
        for gg in getattr(g, "geoms", [g]):
            polys.append(np.asarray(gg.exterior.coords))
ax.add_collection(PolyCollection(polys, facecolors="#000000", edgecolors="none"))
ax.set_xlim(VIEW[0], VIEW[2]); ax.set_ylim(VIEW[1], VIEW[3])
fig.savefig(OUT_FG, dpi=100, transparent=True)
plt.close(fig)

out = {
    "crs": "EPSG:5187", "origin": ORIGIN, "view_m": [VIEW[2] - VIEW[0], VIEW[3] - VIEW[1]],
    "grid_axis_bearing": "N0.8°E", "diag_A": "N47.5°E", "diag_B": "N57.5°W",
    "streets": streets, "rail": rail, "rail_poly": rail_poly, "wall": wall,
    "zone": loc(zone.exterior.coords), "herit_poly": herit_poly, "herit_pt": herit_pt,
    "station": station, "water": water,
    "source": "국토지리정보원 연속수치지도(2026-09-13 취득, T2); 경주시 고시 제2026-8호 구역계(T1); 소상공인시장진흥공단 상가업소 도로명주소(T2, 간선 이름)",
}
DER.mkdir(parents=True, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("streets", len(streets), Counter(s["s"] for s in streets), "named", sum(1 for s in streets if s["n"]))
print("rail", len(rail), "wall", len(wall), "herit_pt", len(herit_pt), "water", len(water), "->", OUT, OUT.stat().st_size // 1024, "KB")
print("figure-ground", OUT_FG, W_px, "x", H_px)
