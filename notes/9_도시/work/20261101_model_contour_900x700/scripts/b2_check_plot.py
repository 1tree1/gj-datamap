# plan2d.json 확인용 평면도(전체 + 확대 2곳)
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib import font_manager

sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).resolve().parents[1]
d = json.load(open(W / "data" / "plan2d.json", encoding="utf-8"))
for f in ("Malgun Gothic",):
    if any(f in x.name for x in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = f


def draw(ax, p, **kw):
    ax.add_patch(MPoly(p["ext"], closed=True, **kw))
    for h in p["holes"]:
        ax.add_patch(MPoly(h, closed=True, fc="white", ec=kw.get("ec", "none"), lw=kw.get("lw", 0)))


def plot(fname, box=None, size=(10, 12.6)):
    fig, ax = plt.subplots(figsize=size, dpi=150)
    draw(ax, d["frame"], fc="#d9d4c7", ec="k", lw=0.6)                 # 색지(도로)
    for p in d["river"]: draw(ax, p, fc="#6fa8dc", ec="none")
    for p in d["bridges"]: draw(ax, p, fc="#d9d4c7", ec="#c0392b", lw=0.8)
    for p in d["rail_bridges"] + d["bike_bridges"]: draw(ax, p, fc="#d9d4c7", ec="#8e44ad", lw=0.8)
    for bm in d["bridge_models"]:
        for q in bm["piers"]: draw(ax, q, fc="#555", ec="none")
    for p in d["sidewalk"]: draw(ax, p, fc="#f3e3a0", ec="none")
    for p in d["land"]: draw(ax, p, fc="#9cc58a", ec="none")
    for k, v in d["buildings"].items():
        c = "#c97a50" if k == "bld" else ("#7f8c8d" if k == "thin" else "#d62828")
        for b in v: draw(ax, b["poly"], fc=c, ec="none")
    for l in d["center_lines"]: ax.plot(*zip(*l), color="#e6b800", lw=0.6)
    for l in d["lane_lines"]: ax.plot(*zip(*l), color="white", lw=0.4)
    draw(ax, d["site"], fc="none", ec="#d62828", lw=1.0, ls="--")
    for k, v in d["buildings"].items():
        if k.startswith("key:"):
            xs = [c[0] for b in v for c in b["poly"]["ext"]]; ys = [c[1] for b in v for c in b["poly"]["ext"]]
            ax.annotate(k[4:], (sum(xs) / len(xs), max(ys)), fontsize=7, color="#d62828", ha="center", va="bottom")
    xs = [c[0] for c in d["frame"]["ext"]]; ys = [c[1] for c in d["frame"]["ext"]]
    ax.set_xlim(*(box[0:2] if box else (min(xs) - 5, max(xs) + 5)))
    ax.set_ylim(*(box[2:4] if box else (min(ys) - 5, max(ys) + 5)))
    ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(W / fname, bbox_inches="tight"); plt.close(fig)
    print("saved", fname)


plot("check_plan_all.png")
fx = [c[0] for c in d["frame"]["ext"]]; fy = [c[1] for c in d["frame"]["ext"]]
cx, cy = (min(fx) + max(fx)) / 2, (min(fy) + max(fy)) / 2
plot("check_zoom_center.png", (cx - 130, cx + 170, cy - 220, cy + 160), size=(10, 12.7))
br = d["bridges"][0]["ext"] if d["bridges"] else d["frame"]["ext"]
bx = sum(c[0] for c in br) / len(br); by = sum(c[1] for c in br) / len(br)
plot("check_zoom_bridge.png", (bx - 120, bx + 120, by - 90, by + 90), size=(10, 7.5))
plot("check_zoom_river.png", (1157330, 1157800, 1762540, 1762895), size=(12, 9.1))
