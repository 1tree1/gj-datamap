import json, pickle, sys, csv
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Patch
from shapely.geometry import Polygon, LineString, MultiPolygon, shape
from shapely import wkb, affinity
from shapely.ops import unary_union, transform
from pyproj import Transformer

SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
OLD = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7d42d444-7313-40a1-ac02-6f82986afca6\scratchpad"
ROOT = r"C:\Users\OFFICE\Desktop\9_도시"
OUT = ROOT + r"\work\20261005_plan_sketch"
import os; os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
from layout_def import ROADS, ZONES, GREEN
fm.fontManager.addfont(r"C:\Windows\Fonts\malgun.ttf"); plt.rcParams["font.family"] = "Malgun Gothic"

fit = json.load(open(SP + r"\sim_fit.json")); s, th, tx, ty = fit["s"], fit["th"], fit["tx"], fit["ty"]
def to_world(pts):
    P = Polygon([(-y, -x) for x, y in pts]) if len(pts) > 2 else LineString([(-y, -x) for x, y in pts])
    P = affinity.scale(P, s, s, origin=(0, 0)); P = affinity.rotate(P, th, origin=(0, 0)); return affinity.translate(P, tx, ty)
U = wkb.loads(pickle.load(open(OLD + r"\step1.pkl", "rb"))["U"])

# 레이어(프로그램) 정의: key → (Rhino 레이어명, RGB, 구분)
LAYERS = {
    "화랑로연결도로": ("도로 화랑로 연결도로", (45, 45, 55)),
    "보행주동선": ("도로 보행 주동선", (135, 135, 145)),
    "오픈스페이스": ("공원녹지 오픈스페이스", (140, 190, 90)),
    "청년주거": ("주거 청년주거", (250, 205, 130)),
    "시청·의회": ("공공 시청·의회부지", (225, 80, 95)),
    "공공운동·생활시설": ("공공 공공운동·생활시설", (240, 140, 140)),
    "청년창업·기업지원": ("업무 청년창업·경주기업지원", (110, 165, 225)),
    "청년주민커뮤니티": ("커뮤니티 청년·주민커뮤니티", (150, 215, 235)),
    "복합문화·영화관": ("문화 복합문화공간·영화관", (190, 150, 225)),
    "아티스트레지던시·공방": ("문화 아티스트레지던시·오픈스튜디오·체험공방", (70, 70, 165)),
    "경주 근대역사관·전시장": ("문화 경주근대역사관·전시장", (175, 125, 95)),
    "구경주역 이전": ("역사 구경주역 이전", (120, 80, 60)),
    "체험판매": ("상업 체험판매", (140, 50, 55)),
    "성동시장 활성화 클러스터": ("상업 성동시장 활성화 클러스터시설", (235, 120, 175)),
    "관광객 중심 휴게·판매상가": ("상업 관광객중심 휴게·판매상가", (240, 135, 55)),
    "경주관광지원시설": ("관광 경주관광지원시설", (245, 225, 100)),
    "주차타워": ("주차 주차타워", (200, 200, 130)),
    "주차타워(해석)": ("주차 주차타워(라벨없음·해석)", (215, 215, 160)),
}

# 도로 (U로 자름)
road_polys = {}
for k, (pts, w) in ROADS.items():
    road_polys[k] = to_world(pts).buffer(w * s / 2, cap_style=2, join_style=2)
road_all = unary_union(list(road_polys.values()))
pedestrian = unary_union([p for k, p in road_polys.items() if k != "R1_화랑로연결도로"])
rd1 = road_polys["R1_화랑로연결도로"].difference(U.buffer(0))  # 경계 밖 연장(참고용 확인)
items = []   # (id, 레이어key, polygon, 표시명)
def add(i, key, poly, label):
    poly = poly.intersection(U)
    parts = [g for g in (poly.geoms if hasattr(poly, "geoms") else [poly]) if g.geom_type == "Polygon" and g.area > 25]
    for n, g in enumerate(sorted(parts, key=lambda g: -g.area)):
        items.append(dict(id=i + ("" if n == 0 else f"_{n}"), key=key, geom=g, label=label))
r1 = road_polys["R1_화랑로연결도로"].difference(U.exterior.buffer(0)).intersection(U)
add("R1", "화랑로연결도로", road_polys["R1_화랑로연결도로"], "화랑로 연결도로")
ped = unary_union([p for k, p in road_polys.items() if k != "R1_화랑로연결도로"]).difference(road_polys["R1_화랑로연결도로"])
add("R_ped", "보행주동선", ped, "보행 주동선")
before_after = []
for k, (prog, pts) in ZONES.items():
    raw = to_world(pts); cut = raw.difference(road_all)
    before_after.append((k, raw.area, cut.intersection(U).area))
    add(k.split("_")[0], prog, cut, k.split("_", 1)[1])
for k, pts in GREEN.items():
    raw = to_world(pts); cut = raw.difference(road_all)
    before_after.append((k, raw.area, cut.intersection(U).area))
    add(k.split("_")[0], "오픈스페이스", cut, "녹지띠")

print("%-30s %10s %10s" % ("구역", "그린면적", "도로제외·경계내"))
for k, a, b in before_after: print("%-30s %10.0f %10.0f  %s" % (k, a, b, "  ← 30%이상 감소" if b < a * 0.7 else ""))

# 모형좌표 변환 (model = (real5179 + C)/2) → JSON
C = np.array([1155149.0, 1762445.9]); t = Transformer.from_crs(5187, 5179, always_xy=True)
Z = 258.0
def to_model(coords):
    a = np.array(coords)[:, :2]; x, y = t.transform(a[:, 0], a[:, 1])
    m = (np.column_stack([x, y]) + C) / 2
    return [[round(float(p[0]), 4), round(float(p[1]), 4), Z] for p in m]
out = []
for it in items:
    g = it["geom"]
    rp = g.representative_point()
    out.append(dict(id=it["id"], key=it["key"], layer=LAYERS[it["key"]][0], rgb=LAYERS[it["key"]][1], label=it["label"],
                    area_m2=round(g.area, 1), ring=to_model(g.exterior.coords), label_pt=to_model([(rp.x, rp.y)])[0]))
json.dump(out, open(SP + r"\plan_model.json", "w", encoding="utf-8"), ensure_ascii=False)
pickle.dump([{**{k: v for k, v in it.items() if k != "geom"}, "geom": it["geom"].wkb} for it in items], open(SP + r"\plan_items.pkl", "wb"))

# 면적표 (5187 도형 면적)
agg = {}
for it in items:
    a = agg.setdefault(it["key"], [0, 0.0]); a[0] += 1; a[1] += it["geom"].area
tot = U.area
rows = [(LAYERS[k][0], n, ar) for k, (n, ar) in agg.items()]
with open(OUT + r"\area_table.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["레이어", "조각수", "면적㎡(EPSG:5187)", "경계 대비 %"])
    for nm, n, ar in sorted(rows, key=lambda r: -r[2]): w.writerow([nm, n, round(ar), round(ar / tot * 100, 1)])
    w.writerow(["합계(배치된 면적)", "", round(sum(r[2] for r in rows)), round(sum(r[2] for r in rows) / tot * 100, 1)])
    w.writerow(["경계 U 면적", "", round(tot), 100.0])
print("\n면적표:")
for nm, n, ar in sorted(rows, key=lambda r: -r[2]): print("  %-34s %2d조각 %9.0f㎡ %5.1f%%" % (nm, n, ar, ar / tot * 100))
print("  배치 합계 %.0f㎡ / 경계 %.0f㎡ = %.1f%%" % (sum(r[2] for r in rows), tot, sum(r[2] for r in rows) / tot * 100))

# 미리보기 PNG
recs = pickle.load(open(OLD + r"\step1.pkl", "rb"))["recs"]
fig, ax = plt.subplots(figsize=(11, 17))
for r in recs:
    g = wkb.loads(r["geom"])
    if g.intersects(U.buffer(40)):
        for p in (g.geoms if hasattr(g, "geoms") else [g]): ax.plot(*p.exterior.xy, color="#ccc", lw=0.35, zorder=1)
for it in items:
    c = np.array(LAYERS[it["key"]][1]) / 255
    ax.fill(*it["geom"].exterior.xy, fc=c, ec="#333", lw=0.5, alpha=0.9, zorder=3)
ax.plot(*U.exterior.xy, color="#8a2be2", lw=2.2, zorder=6)
SHORT = {"화랑로연결도로": "화랑로 연결도로", "보행주동선": "", "오픈스페이스": "오픈스페이스", "청년주거": "청년주거\nzone", "시청·의회": "시청·의회\n부지",
         "공공운동·생활시설": "공공운동·\n생활시설", "청년창업·기업지원": "청년창업·\n기업지원", "청년주민커뮤니티": "청년·주민\n커뮤니티", "복합문화·영화관": "복합문화\n·영화관",
         "아티스트레지던시·공방": "아티스트레지던시\n오픈스튜디오·공방", "경주 근대역사관·전시장": "근대역사관\n·전시장", "구경주역 이전": "구경주역\n이전", "체험판매": "체험판매",
         "성동시장 활성화 클러스터": "성동시장\n활성화 클러스터", "관광객 중심 휴게·판매상가": "관광객 휴게\n·판매상가", "경주관광지원시설": "관광\n지원", "주차타워": "주차타워", "주차타워(해석)": "주차타워?"}
done = set()
for it in items:
    if it["key"] in ("보행주동선",) or (it["key"] in ("오픈스페이스",) and it["geom"].area < 400): continue
    if it["key"] in done and it["key"] in ("체험판매", "관광객 중심 휴게·판매상가", "오픈스페이스") and it["geom"].area < 3000: continue
    p = it["geom"].representative_point(); fs = 7.5 if it["geom"].area > 2500 else 6
    tcol = "w" if it["key"] in ("화랑로연결도로", "아티스트레지던시·공방", "체험판매", "구경주역 이전") else "#111"
    ax.text(p.x, p.y, SHORT[it["key"]], fontsize=fs, ha="center", va="center", color=tcol, zorder=8, rotation=90 if it["key"] == "화랑로연결도로" and False else 0)
    done.add(it["key"])
ax.set_aspect("equal"); minx, miny, maxx, maxy = U.buffer(30).bounds; ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy)
ax.set_xticks([]); ax.set_yticks([])
ax.set_title("구경주역 도시계획안 스케치 (손그림 → 실좌표 EPSG:5187)  보라 선 = 3dm 경계 218,478㎡", fontsize=12)
fig.tight_layout(); fig.savefig(OUT + r"\plan_sketch_v1.png", dpi=120)
print("png saved")
