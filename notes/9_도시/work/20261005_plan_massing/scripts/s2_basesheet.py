"""S2 설계 기준 시트 — 경계·앵커·스케치 도로/구역·폐선·문화유산을 50 m 격자와 함께 북/남 두 장으로 그린다 (도로망 좌표 확정용)."""
import pickle, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from shapely import wkb
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
OLD = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
fm.fontManager.addfont(r"C:\Windows\Fonts\malgun.ttf"); plt.rcParams["font.family"] = "Malgun Gothic"
C = pickle.load(open(SP + r"\context.pkl", "rb")); U = C["U"]
A = pickle.load(open(SP + r"\anchors.pkl", "rb"))
H = pickle.load(open(SP + r"\heritage_rail.pkl", "rb"))
items = pickle.load(open(SP + r"\plan_items.pkl", "rb"))   # 스케치 v1 구역 (EPSG:5187)
COL = {"화랑로연결도로": "#333", "보행주동선": "#999"}
def draw(ax, ymin, ymax):
    for b in C["B"]:
        for p in (b["geom"].geoms if hasattr(b["geom"], "geoms") else [b["geom"]]):
            ax.fill(*p.exterior.xy, fc="#e9e4da" if U.contains(p.centroid) is False else "#f4d9d9", ec="none", zorder=1)
    for r in C["R"]:
        if r["w"] >= 3:
            for l in (r["geom"].geoms if hasattr(r["geom"], "geoms") else [r["geom"]]):
                ax.plot(*l.xy, color="#6a8fd0" if r["w"] < 8 else "#e08a00", lw=0.5 + r["w"] / 10, alpha=0.7, zorder=2)
    for it in items:
        g = wkb.loads(it["geom"])
        ax.fill(*g.exterior.xy, fc=("#555" if it["key"] in COL else "#f6b0a0"), alpha=0.35, ec="r" if it["key"] not in COL else "none", lw=0.4, zorder=3)
    for nm, col in (("rail_abandoned_4326", "#d62728"),):
        for p, g in H[nm]:
            for l in (g.geoms if hasattr(g, "geoms") else [g]):
                if l.geom_type == "LineString": ax.plot(*l.xy, color=col, lw=0.8, zorder=4)
    for p, g in H["heritage_pts_4326"]: ax.plot(g.x, g.y, "k*", ms=11, zorder=7)
    for p, g in H["rail_stations_4326"]: ax.plot(g.x, g.y, "rs", ms=8, zorder=7)
    ax.plot(*U.exterior.xy, color="#8a2be2", lw=1.8, zorder=6)
    for a in A:
        ax.plot(a["x"], a["y"], "o", color="k", ms=4, zorder=8)
        if a["w"] >= 3: ax.annotate("%.0fm" % a["w"], (a["x"], a["y"]), xytext=(-18 if a["side"] == "서" else 6, 3), textcoords="offset points", fontsize=7, zorder=9)
    for x in range(219600, 220001, 50):
        ax.axvline(x, color="#0a6", lw=0.4, zorder=0); ax.text(x, ymin + 3, str(x), fontsize=7, color="#0a6", ha="center")
    for y in range((int(ymin) // 50) * 50, int(ymax), 50):
        ax.axhline(y, color="#c60", lw=0.4, zorder=0); ax.text(219590, y + 2, str(y), fontsize=7, color="#c60")
    ax.set_xlim(219580, 219990); ax.set_ylim(ymin, ymax); ax.set_aspect("equal")
for name, (y0, y1) in {"N": (360980, 361470), "S": (360490, 361000)}.items():
    fig, ax = plt.subplots(figsize=(8.2, (y1 - y0) / 410 * 8.2)); draw(ax, y0, y1)
    ax.set_title("기준 시트 %s — 파랑/주황=기존 가로(폭), 점=앵커, 분홍=스케치 v1 구역, 빨강선=폐선, ★=문화유산, ■=구 역사" % name, fontsize=8)
    fig.tight_layout(); fig.savefig(SP + rf"\base_{name}.png", dpi=125); plt.close(fig)
print("ok")
