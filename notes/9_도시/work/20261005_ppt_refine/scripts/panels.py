"""슬라이드용 평면 도판(획지·구역·길) — plan_clean 의 plotkit 을 재사용해 PNG 로 낸다. 출력: assets/plan_*.png (+ 구역 띠 위치 JSON)"""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PLAN_SP", r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean\data")
sys.path.insert(0, r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean\scripts")
from plotkit import *            # noqa
from shapely.ops import polylabel
import pickle
ASSETS = os.path.join(ROOT, "assets"); os.makedirs(ASSETS, exist_ok=True)

ANCH = pickle.load(open(SP + r"\anchors.pkl", "rb"))
RN = TC["RNAME"]; RR = TC["road_rows"]
# 구역 경계: 북 y>361,092(C가로) / 중 360,796~361,092 / 남 y<360,796(A가로)
ZONES = [("북", 361092, 1e9, "#6F9FDC"), ("중", 360796, 361092, "#A98BD3"), ("남", -1e9, 360796, "#F4A0C2")]
ZLOTS = {"북": [1, 2, 3, 4, 5, 6], "중": [7, 8, 9, 10, 11, 12, 13, 14], "남": [15, 16, 17, 18, 19]}
ZPARKS = {"북": ["Park A"], "중": ["Park B"], "남": ["Park C", "Plaza D"]}
GCOL = {"차량": "#5d7fb0", "S": "#f19a3e", "보행": "#d1495b", "골목": "#a58bd0"}
def rcol(r): return GCOL["S"] if r["key"] == "S" else GCOL[r["group"]]

def plan_panel(out, ext, size, hl_lots=None, hl_parks=None, show_numbers=True, bands=False, roads_mode=False, dpi=220, name_parks=True, scalebar=True):
    fig = plt.figure(figsize=size, dpi=dpi, facecolor="white"); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    x0, y0, x1, y1 = ext; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; w, h = x1 - x0, y1 - y0
    asp = size[0] / size[1]
    if w / h < asp: w = h * asp
    else: h = w / asp
    ax.set_xlim(cx - w / 2, cx + w / 2); ax.set_ylim(cy - h / 2, cy + h / 2); ax.set_aspect("equal")
    e2 = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    ax.add_patch(Rectangle((e2[0], e2[1]), w, h, fc="#f6f6f4", ec="none", zorder=0))
    draw_roads_ctx(ax, e2, z=0.4); draw_context(ax, e2, fc="#dededa", z=0.8)
    fill(ax, U, fc="#cfcfcb", z=2)
    lots_hl = set(hl_lots) if hl_lots else {d["no"] for d in LOTS}
    parks_hl = set(hl_parks) if hl_parks else {d["name"] for d in PARKS}
    if roads_mode:
        for d in PARKS: fill(ax, d["geom"], fc="#dcecc9", z=3)
        for d in LOTS: fill(ax, d["geom"], fc="#ffffff", ec="#c9c9c9", lw=0.4, z=3)
        for b in BUILD: fill(ax, b["geom"], fc="#e1e1de", z=3.5)
        roads = dict(NET["streets"]); roads.update(NET["lanes"]); used = []
        for r in RR:
            g = roads[r["key"]].difference(unary_union(used)) if used else roads[r["key"]]
            used.append(roads[r["key"]]); fill(ax, g, fc=rcol(r), ec="white", lw=0.35, z=5)
        fill(ax, LP["plaza"], fc="#cfcfcb", z=4.5)
        for d in PARKS:
            if d["name"] == "Plaza D": fill(ax, d["geom"], fc="#cfcfcb", z=4.5)
        for key, g, wd in road_label_points():
            L = g.length
            if L < 60: continue
            p = g.interpolate(0.5 * L); q = g.interpolate(min(L, 0.5 * L + 4)); a = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
            if a > 90: a -= 180
            if a < -90: a += 180
            ax.text(p.x, p.y, "%s %gm" % (key, wd), fontsize=7.5, rotation=a, rotation_mode="anchor", ha="center", va="center", color="white", fontweight="bold", zorder=9)
        for a in ANCH: ax.add_patch(Circle((a["x"], a["y"]), 4.2, fc="white", ec="#c0392b", lw=1.1, zorder=10))
    else:
        for d in PARKS: fill(ax, d["geom"], fc="#c3e3a4" if d["name"] in parks_hl else "#e4eedd", ec="#6aa84f" if d["name"] in parks_hl else "#cfdcc8", lw=0.5, z=3)
        for d in LOTS:
            on = d["no"] in lots_hl
            fill(ax, d["geom"], fc=tint(CATCOL[d["cat"]], 0.62) if on else "#efefed", ec="#555" if on else "#d3d3d0", lw=0.6 if on else 0.4, z=3)
        for lid, nm, g in M["COURTS"]:
            no = int(lid.split()[-1]) if lid.split()[-1].isdigit() else None
            fill(ax, g, fc="#e1f0cf" if (no is None or no in lots_hl) else "#f2f4ef", z=3.5)
        for lid, nm, g, col in M["OPEN"]:
            no = int(lid.split()[-1]) if lid.split()[-1].isdigit() else None
            fill(ax, g, fc={"#cfe6b4": "#e1f0cf", "#d98a6a": "#e2a58a", "#cfcfcf": "#dddddd"}.get(col, col) if (no is None or no in lots_hl) else "#f0f0ee", z=3.5)
        for b in BUILD:
            on = (b["lot_no"] in lots_hl) or (b["lot_no"] == 0 and (not hl_lots))
            fill(ax, b["geom"], fc=CATCOL[b["cat"]] if on else "#dcdcd8", ec="#3a3a3a" if on else "none", lw=0.35, z=4)
        if show_numbers:
            for d in LOTS:
                if d["no"] not in lots_hl: continue
                bl = unary_union([b["geom"] for b in BUILD if b["lot_no"] == d["no"]]).buffer(2.0); free = d["geom"].difference(bl)
                free = max(polys(free), key=lambda g: g.area) if not free.is_empty else d["geom"]
                pt = polylabel(free, 1.0) if free.area > 60 else d["geom"].representative_point()
                num_circle(ax, pt.x, pt.y, str(d["no"]), r=max(w, h) / 62.0, fs=max(6.5, 9.5 * size[1] / 6.0), z=10)
        if name_parks:
            for d in PARKS:
                if d["name"] not in parks_hl: continue
                pt = polylabel(max(polys(d["geom"]), key=lambda g: g.area), 1.0)
                ax.text(pt.x, pt.y, d["name"], fontsize=max(6.5, 8 * size[1] / 6.0), ha="center", va="center", color="#2d5a1b", fontweight="bold", zorder=9, path_effects=halo(1.8, "#c3e3a4"))
    if bands:
        fr = {}
        for nm, ya, yb, col in ZONES:
            band = box(e2[0], max(ya, e2[1] - 1), e2[2], min(yb, e2[3] + 1)).intersection(U)
            fill(ax, band, fc=col, alpha=0.30, z=6)
            ys = (max(ya, e2[1]), min(yb, e2[3])); fr[nm] = ((e2[3] - ys[1]) / h, (e2[3] - ys[0]) / h)     # 위에서부터의 비율(상단, 하단)
        for ya in (361092, 360796):
            ax.plot([e2[0], e2[2]], [ya, ya], color="#555", lw=0.8, ls=(0, (4, 3)), zorder=7)
        json.dump(fr, open(os.path.join(ASSETS, "zone_bands.json"), "w"))
    ax.add_patch(PathPatch(path_of(Polygon(U.exterior)), fc="none", ec="#7a2bd6", lw=1.0, ls=(0, (4, 2)), zorder=8))
    if scalebar:
        sb0 = e2[0] + 0.04 * w; sby = e2[1] + 0.03 * h
        for i in range(2): ax.add_patch(Rectangle((sb0 + i * 50, sby), 50, h * 0.008, fc=INK if i == 0 else "white", ec=INK, lw=0.5, zorder=12))
        ax.text(sb0 + 100 + 6, sby, "100 m", fontsize=7, ha="left", va="bottom", zorder=12)
        ax.annotate("", xy=(e2[2] - 0.05 * w, e2[1] + 0.10 * h), xytext=(e2[2] - 0.05 * w, e2[1] + 0.04 * h), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0), zorder=12)
        ax.text(e2[2] - 0.05 * w, e2[1] + 0.105 * h, "N", fontsize=8, ha="center", va="bottom", fontweight="bold", zorder=12)
    fig.savefig(out, dpi=dpi, facecolor="white"); plt.close(fig)
    return out

if __name__ == "__main__":
    X0, X1 = U.bounds[0], U.bounds[2]
    pad = 55
    full = (X0 - pad, U.bounds[1] - pad, X1 + pad, U.bounds[3] + pad)
    print(plan_panel(os.path.join(ASSETS, "plan_lots.png"), full, (3.0, 6.1), show_numbers=True))
    print(plan_panel(os.path.join(ASSETS, "plan_zones.png"), full, (3.0, 6.1), show_numbers=False, bands=True, name_parks=False))
    zb = {"북": (X0 - pad, 361092 - 25, X1 + pad, U.bounds[3] + 25), "중": (X0 - pad, 360796 - 25, X1 + pad, 361092 + 25), "남": (X0 - pad, U.bounds[1] - 25, X1 + pad, 360796 + 25)}
    for k, e in zb.items():
        nm = {"북": "north", "중": "center", "남": "south"}[k]
        print(plan_panel(os.path.join(ASSETS, "plan_%s.png" % nm), e, (5.2, 5.3), hl_lots=ZLOTS[k], hl_parks=ZPARKS[k]))
    print(plan_panel(os.path.join(ASSETS, "plan_roads.png"), full, (3.0, 6.1), roads_mode=True, scalebar=True))
