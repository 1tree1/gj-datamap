"""K3 평면 확인도 — 획지 번호·용도 + 매스 윤곽(깔끔함 점검용)"""
import pickle, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
from shapely.ops import unary_union
import os as _os; SP = _os.environ.get("PLAN_SP", r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad")   # 입력 pkl 폴더. 재현 시 PLAN_SP=<work/20261005_plan_clean/data>
PM = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts"
sys.path.insert(0, PM)
from geomkit import polys
fm.fontManager.addfont(r"C:\Windows\Fonts\malgun.ttf"); plt.rcParams["font.family"] = "Malgun Gothic"
LP = pickle.load(open(SP + r"\lots.pkl", "rb")); M = pickle.load(open(SP + r"\clean_mass.pkl", "rb"))
C = pickle.load(open(SP + r"\context.pkl", "rb")); U = C["U"]
CATCOL = {"문화·교육·공공": "#3d8fd8", "상업·업무": "#e0432d", "창조산업": "#8e4fb8", "여가·오락·체육": "#1f9e92", "주거": "#f6df4a", "판매·음식": "#f08ab4", "교통·방문자": "#b9b9b9", "역사유산": "#b8662b"}
fig, ax = plt.subplots(figsize=(8.5, 15))
for p in polys(U): ax.fill(*p.exterior.xy, fc="#bfbfbf", ec="none")
for d in LP["LOTS"]:
    for p in polys(d["geom"]): ax.fill(*p.exterior.xy, fc="white", ec="#555", lw=0.6)
for d in LP["PARKS"]:
    for p in polys(d["geom"]): ax.fill(*p.exterior.xy, fc="#a9d985", ec="#4a8a2a", lw=0.5)
for lid, nm, g in M["COURTS"]:
    for p in polys(g): ax.fill(*p.exterior.xy, fc="#d7ecc0", ec="none")
for lid, nm, g, col in M["OPEN"]:
    for p in polys(g): ax.fill(*p.exterior.xy, fc=col, ec="none", alpha=0.9)
for b in M["BUILD"]:
    for p in polys(b["geom"]): ax.fill(*p.exterior.xy, fc=CATCOL[b["cat"]], ec="#333", lw=0.4)
for d in LP["LOTS"]:
    c = d["geom"].representative_point(); ax.text(c.x, c.y, str(d["no"]), fontsize=9, fontweight="bold", ha="center", va="center", bbox=dict(boxstyle="circle,pad=0.2", fc="white", ec="#222", lw=0.6))
for d in LP["PARKS"]:
    c = d["geom"].representative_point(); ax.text(c.x, c.y, d["name"], fontsize=7, ha="center", va="center")
ax.plot(*U.exterior.xy, color="#8a2be2", lw=1.2)
ax.set_aspect("equal"); ax.axis("off"); minx, miny, maxx, maxy = U.buffer(10).bounds; ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy)
fig.tight_layout(); fig.savefig(SP + r"\k3_flat.png", dpi=110)
print("ok")

