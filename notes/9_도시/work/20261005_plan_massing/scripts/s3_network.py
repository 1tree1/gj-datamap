"""S3 가로망 → 가구(블록) 구획. 경계 U 안을 도로·골목·녹지띠로 빈틈없이 나누고, 각 가구에 스케치 프로그램을 배정한다.
출력: scratch/network.pkl, scratch/network_fig.png
"""
import pickle, sys, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from shapely.geometry import LineString, Polygon, MultiPolygon, Point
from shapely.ops import unary_union
from shapely import wkb
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
sys.path.insert(0, r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts")
from plan_def import STREETS, LANES, PATHS, GREEN_STRIPS
from geomkit import polys
fm.fontManager.addfont(r"C:\Windows\Fonts\malgun.ttf"); plt.rcParams["font.family"] = "Malgun Gothic"

C = pickle.load(open(SP + r"\context.pkl", "rb")); U = C["U"]
sketch = pickle.load(open(SP + r"\plan_items.pkl", "rb"))
sk = [(it["key"], wkb.loads(it["geom"])) for it in sketch if it["key"] not in ("화랑로연결도로", "보행주동선")]

def street_poly(pts, w):
    return LineString(pts).buffer(w / 2, cap_style=2, join_style=2)

streets = {k: street_poly(v[0], v[1]).intersection(U) for k, v in STREETS.items()}
lanes = {k: street_poly(v[0], v[1]).intersection(U) for k, v in LANES.items()}
greens = {k: Polygon(v[0]).intersection(U) for k, v in GREEN_STRIPS.items()}

# 수변 보행로 R8: 북동 경계를 따라 내측 10 m
ne = LineString([(219940.0, 361291.7), (219898.7, 361328.4), (219866.3, 361357.1), (219840.4, 361379.3), (219828.5, 361389.0), (219822.6, 361399.5), (219816.4, 361412.4), (219813.9, 361416.5), (219788.2, 361442.9)])
streets["R8"] = ne.buffer(10, cap_style=2, join_style=2).intersection(U)
STREETS["R8"] = ([(219940, 361292), (219788, 361443)], 10, "보행자전용도로", "수변 보행로 — 북천 방향, 북동 경계 내측 10m", "[스케치] R8 / 북천·알천남로")

road_all = unary_union(list(streets.values()) + list(lanes.values()))
green_all = unary_union(list(greens.values())).difference(road_all)
blocks_geom = U.difference(unary_union([road_all, green_all]))
faces = polys(blocks_geom)
small = [g for g in faces if g.area < 600]            # 교차부 자투리 → 광장(포장)
faces = [g for g in faces if g.area >= 600]
plaza_extra = unary_union(small) if small else Polygon()
faces.sort(key=lambda g: (-round(g.centroid.y / 60), g.centroid.x))      # 북→남, 서→동 순서

rows = []
for i, f in enumerate(faces):
    ov = {}
    for key, g in sk:
        a = f.intersection(g).area
        if a > 1: ov[key] = ov.get(key, 0) + a
    top = sorted(ov.items(), key=lambda kv: -kv[1])
    rows.append(dict(id="B%02d" % (i + 1), geom=f, area=f.area, prog=top[0][0] if top else "미배정", ov=top[:3]))
print("가구 %d개 / 자투리 %d개(%.0f㎡) / 도로·골목 %.0f㎡ / 녹지띠 %.0f㎡ / U %.0f㎡" % (len(rows), len(small), plaza_extra.area, road_all.area, green_all.area, U.area))
for r in rows: print("%s  %7.0f㎡  (%.0f, %.0f)  %s   %s" % (r["id"], r["area"], r["geom"].centroid.x, r["geom"].centroid.y, r["prog"], [(k, round(v)) for k, v in r["ov"]]))
chk = sum(r["area"] for r in rows) + road_all.area + green_all.area + plaza_extra.area
print("면적 합 검증: 가구+도로+녹지+자투리 = %.0f / U %.0f (차 %.1f)" % (chk, U.area, chk - U.area))
pickle.dump(dict(streets=streets, lanes=lanes, greens=greens, green_all=green_all, road_all=road_all, plaza_extra=plaza_extra, blocks=rows, STREETS=STREETS, LANES=LANES, PATHS=PATHS), open(SP + r"\network.pkl", "wb"))

fig, ax = plt.subplots(figsize=(10, 15.5))
for b in C["B"]:
    for p in polys(b["geom"]): ax.fill(*p.exterior.xy, fc="#ece8df", ec="none", zorder=1)
COLS = {"청년주거": "#f7e04a", "시청·의회": "#4f9bd9", "공공운동·생활시설": "#46b5a8", "복합문화·영화관": "#46b5a8", "청년창업·기업지원": "#9b6bc4", "청년주민커뮤니티": "#4f9bd9",
        "아티스트레지던시·공방": "#9b6bc4", "체험판매": "#f08cb4", "성동시장 활성화 클러스터": "#f08cb4", "관광객 중심 휴게·판매상가": "#f08cb4", "경주관광지원시설": "#4f9bd9",
        "경주 근대역사관·전시장": "#4f9bd9", "구경주역 이전": "#b9732e", "주차타워": "#bdbdbd", "주차타워(해석)": "#bdbdbd", "오픈스페이스": "#8fcf5a", "미배정": "#ffffff"}
for r in rows:
    for p in polys(r["geom"]): ax.fill(*p.exterior.xy, fc=COLS.get(r["prog"], "#ddd"), ec="#444", lw=0.5, zorder=3)
    ax.text(r["geom"].centroid.x, r["geom"].centroid.y, "%s\n%.0f㎡" % (r["id"], r["area"]), fontsize=6, ha="center", va="center", zorder=9)
for p in polys(green_all): ax.fill(*p.exterior.xy, fc="#9ad36a", ec="#4a8a2a", lw=0.4, zorder=3)
for k, g in list(streets.items()) + list(lanes.items()):
    for p in polys(g): ax.fill(*p.exterior.xy, fc="#fafafa", ec="#888", lw=0.4, zorder=4)
for p in polys(plaza_extra): ax.fill(*p.exterior.xy, fc="#fafafa", ec="#888", lw=0.4, zorder=4)
ax.plot(*U.exterior.xy, color="#8a2be2", lw=2, zorder=8)
minx, miny, maxx, maxy = U.buffer(30).bounds; ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy); ax.set_aspect("equal")
fig.tight_layout(); fig.savefig(SP + r"\network_fig.png", dpi=105)
