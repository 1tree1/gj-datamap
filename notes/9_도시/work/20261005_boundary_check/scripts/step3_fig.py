import pickle, json, re, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from shapely import wkb
from shapely.geometry import mapping, MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7d42d444-7313-40a1-ac02-6f82986afca6\scratchpad"
OUT = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_boundary_check"
import os; os.makedirs(OUT, exist_ok=True)
fm.fontManager.addfont(r"C:\Windows\Fonts\malgun.ttf")
plt.rcParams["font.family"] = "Malgun Gothic"; plt.rcParams["axes.unicode_minus"] = False

s1 = pickle.load(open(SP + r"\step1.pkl", "rb")); s2 = pickle.load(open(SP + r"\step2.pkl", "rb"))
U = wkb.loads(s2["U"]); P = wkb.loads(s2["P50a"]); zone = wkb.loads(s2["zone"])
add = wkb.loads(s2["add"]); rem = wkb.loads(s2["rem"])
recs = s1["recs"]
for r in recs:
    r["geom"] = wkb.loads(r["geom"]); r["area"] = r["geom"].area
    m = re.search(r"([가-힣])$", r["jibun"].strip()); r["jimok"] = m.group(1) if m else ""
share = dict(s2["rows"]); sel = set(s2["sel"])

# 황오동 147 확인
for i, r in enumerate(recs):
    if r["addr"].endswith("황오동 147"):
        print("황오동 147:", r["jimok"], round(r["area"]), "㎡, U안 비율", round(share.get(i, 0), 3), "건물", r["bldg_n"], "공시지가", r["jiga"],
              "centroid", round(r["geom"].centroid.x), round(r["geom"].centroid.y), "reg:", )

# 지목 색
COL = {"철": "#d9c29a", "대": "#f0a07a", "전": "#b8e086", "답": "#b8e086", "잡": "#e3e08a", "창": "#c9b3f0", "천": "#9ecae1", "구": "#9ecae1", "도": "#c8c8c8", "임": "#9bd39b"}
LAB = [("철", "철도용지"), ("대", "대지"), ("전", "전·답"), ("잡", "잡종지"), ("창", "창고용지"), ("천", "하천·구거"), ("도", "도로")]
minx, miny, maxx, maxy = U.buffer(60).bounds
fig, axs = plt.subplots(1, 2, figsize=(15, 15 * (maxy - miny) / (maxx - minx) / 2 * 1.0 + 1.2))
def draw_poly(ax, g, **kw):
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.is_empty: continue
        ax.fill(*p.exterior.xy, **kw) if kw.get("fc") or kw.get("color") else None
tr = STRtree([r["geom"] for r in recs])
for ax in axs:
    for i in tr.query(U.buffer(60)):
        r = recs[i]
        for p in (r["geom"].geoms if hasattr(r["geom"], "geoms") else [r["geom"]]):
            near = i in share
            ax.fill(*p.exterior.xy, fc=COL.get(r["jimok"], "#eeeeee") if (ax is axs[0] and near) else "#f4f4f4", ec="#9a9a9a", lw=0.25, zorder=1)
for p in (U.geoms if hasattr(U, "geoms") else [U]):
    axs[0].plot(*p.exterior.xy, color="#1f4fd8", lw=1.6, ls="--", zorder=5)
    axs[1].plot(*p.exterior.xy, color="#1f4fd8", lw=1.0, ls="--", zorder=5)
for p in (P.geoms if hasattr(P, "geoms") else [P]):
    axs[0].plot(*p.exterior.xy, color="#c0182d", lw=1.8, zorder=6)
    axs[1].plot(*p.exterior.xy, color="#c0182d", lw=1.2, zorder=6)
for g, c in ((add, "#d62d20"), (rem, "#2b8cbe")):
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        axs[1].fill(*p.exterior.xy, fc=c, ec=c, lw=0.3, zorder=7)
for ax in axs:
    ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
axs[0].set_title(f"편입 필지 {len(sel)}개 — 지목별 (50% 규칙)", fontsize=13)
axs[1].set_title(f"U 대비 증감  +{add.area:,.0f}㎡ / -{rem.area:,.0f}㎡", fontsize=13)
h = [Patch(fc=COL[k], ec="#888", label=v) for k, v in LAB]
h += [Line2D([0], [0], color="#1f4fd8", ls="--", label=f"현재 파일 사용자 경계 U {U.area:,.0f}㎡"), Line2D([0], [0], color="#c0182d", label=f"필지선 매입 경계 {P.area:,.0f}㎡")]
axs[0].legend(handles=h, loc="lower left", fontsize=9, framealpha=0.95)
axs[1].legend(handles=[Patch(fc="#d62d20", label="필지 때문에 늘어난 땅"), Patch(fc="#2b8cbe", label="필지 때문에 빠진 땅")], loc="lower right", fontsize=9)
fig.suptitle("구경주역 경계 — 최종콘타모델_v2.3dm 현재 선 vs 실제 필지선 (V-World 연속지적도 2025, EPSG:5187)", fontsize=14, y=0.995)
fig.tight_layout()
fig.savefig(OUT + r"\boundary_vs_parcel_current.png", dpi=130)
print("fig saved")

feat = lambda g, n: {"type": "Feature", "properties": {"name": n, "area_m2": round(g.area, 1)}, "geometry": mapping(g)}
crs = {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::5187"}}
json.dump({"type": "FeatureCollection", "crs": crs, "features": [feat(U, "user_boundary_3dm_current")]}, open(OUT + r"\user_boundary_current_5187.geojson", "w"), ensure_ascii=False)
json.dump({"type": "FeatureCollection", "crs": crs, "features": [feat(P, "parcel_aligned_50pct_alley")]}, open(OUT + r"\parcel_aligned_boundary_5187.geojson", "w"), ensure_ascii=False)
print("geojson saved")
