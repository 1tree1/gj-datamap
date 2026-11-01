"""V1 설계 데이터 평면 확인(획지·공원·가로·매스·식재·번호)"""
import os, pickle
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
plt.rcParams["font.family"] = "Malgun Gothic"
S = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
def polys(g):
    if g is None or g.is_empty: return []
    return [g] if g.geom_type == "Polygon" else [p for x in g.geoms for p in polys(x)]
def fill(ax, g, fc, ec="none", lw=0, z=1, a=1):
    for p in polys(g):
        ax.add_patch(MP(list(p.exterior.coords), fc=fc, ec=ec, lw=lw, zorder=z, alpha=a))
        for r in p.interiors: ax.add_patch(MP(list(r.coords), fc="white", ec=ec, lw=lw, zorder=z + 0.1))
fig, ax = plt.subplots(figsize=(9, 26), dpi=110)
fill(ax, S["B"], "#f0efeb", "#555", 0.6)
for k, r in S["ROADS"].items(): fill(ax, r, "#c9c9c6", z=2)
fill(ax, S["WALK"], "#fbfbfa", "#bbb", 0.3, z=2); fill(ax, S["PATH8"], "#fbfbfa", "#bbb", 0.3, z=2)
for l in S["LOTS"]:
    fill(ax, l["g"], S["CATS"][l["cat"]][0], "#333", 0.5, z=2, a=0.25)
    p = l["g"].representative_point(); ax.text(p.x, p.y, "%d %s" % (l["no"], l["code"]), fontsize=7, zorder=9, ha="center")
for p in S["PARKS"]: fill(ax, p["g"], "#b4dc8e", "#4a7", 0.5, z=2); q = p["g"].representative_point(); ax.text(q.x, q.y, p["key"], fontsize=9, color="#060", zorder=9)
for p in S["OPEN"]: fill(ax, p["g"], "#dfeccf", "#4a7", 0.5, z=2); q = p["g"].representative_point(); ax.text(q.x, q.y, p["key"], fontsize=9, color="#060", zorder=9)
for p in S["PLZ"]: fill(ax, p["g"], {"광장": "#e7e1d0", "노외주차": "#bdbdbd", "소공원": "#b4dc8e", "텃밭": "#c8b58a", "중정": "#c6e3a5", "코트": "#d4ebf6"}[p["kind"]], z=3)
for m in S["MASS"]:
    fill(ax, m["g"], S["CATS"][m["cat"]][0], "#222", 0.5, z=4)
    c = m["g"].representative_point(); ax.text(c.x, c.y, "%dF" % m["floors"], fontsize=5, ha="center", va="center", zorder=9)
for k, T in S["TREES"].items():
    for x, y, r in T: ax.add_patch(plt.Circle((x, y), r * 0.8, fc="#5a9e3a", ec="none", zorder=5, alpha=0.8))
import sys
xl = [float(v) for v in sys.argv[1:5]] if len(sys.argv) > 4 else [95, 420, 45, 1005]
ax.set_aspect("equal"); ax.set_xlim(xl[0], xl[1]); ax.set_ylim(xl[2], xl[3]); ax.axis("off")
fig.savefig(os.path.join(HERE, "..", "sheets", (sys.argv[5] if len(sys.argv) > 5 else "v1_plan_check.png")), bbox_inches="tight")
