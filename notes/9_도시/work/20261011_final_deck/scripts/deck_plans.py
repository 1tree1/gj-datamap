# -*- coding: utf-8 -*-
"""계획 도면 6종 (적색+흑백) — design_v3.json(계획 좌표 m) + 맥락(ctx_near.json → 계획 좌표 변환).
출력: assets/plans/*.png  (토지이용계획도·획지계획도·도로보행계획도·공원녹지계획도·건축물배치도·단계별계획도·주변연계도)"""
import json, os, sys, math
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, box
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, Rectangle, FancyArrow
from matplotlib.collections import PatchCollection
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck_style import *

ROOT = r"C:\Users\OFFICE\Desktop\9_도시\work"
D = json.load(open(ROOT + r"\20261011_masterplan_v1\data\design_v3.json", encoding="utf-8"))
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\5ac42c4f-b205-49dd-aa7e-de94aecf7727\scratchpad"
C = json.load(open(SP + r"\ctx_near.json", encoding="utf-8"))
OUT = ROOT + r"\20261011_final_deck\assets\plans"; os.makedirs(OUT, exist_ok=True)
TX, TY = 571507.78, 881621.24
def c2p(a): a = np.asarray(a, float); return 2.0 * (a - [TX, TY])

def P(parts): return unary_union([Polygon(q["ext"], q["holes"]).buffer(0) for q in parts])
B = Polygon(D["boundary"]); bx = B.bounds
lots = [(l, P(l["parts"])) for l in D["lots"]]; greens = [(g, P(g["parts"])) for g in D["greens"]]; plazas = [(p, P(p["parts"])) for p in D["plazas"]]
roads = [P(r["parts"]) for r in D["roads"]]; walks = [(w, P(w["parts"])) for w in D["walks"]]; masses = [(m, P(m["parts"])) for m in D["masses"]]
# 맥락(계획 좌표)
ctx_bld = []; ctx_ground = []
for r in C:
    if r["layer"] == "빌딩" and r.get("pts"):
        pg = Polygon(c2p([(p[0], p[1]) for p in r["pts"]])).buffer(0)
        if not pg.is_empty and pg.area > 2: ctx_bld.append((pg, r["bbox"][5] - r["bbox"][2]))
    elif r["layer"] in ("대지", "인도") and "faces" in r:
        for f in r["faces"]:
            if f["n"][2] > 0.9:
                outer = [l["pts"] for l in f["loops"] if "Outer" in l["kind"]]
                if outer:
                    pg = Polygon(c2p([(p[0], p[1]) for p in outer[0]])).buffer(0)
                    if not pg.is_empty: ctx_ground.append(pg)
ctx_bld_in = [(g, h) for g, h in ctx_bld if not B.contains(g.representative_point())]

def polys(g):
    if g.is_empty: return []
    return [g] if g.geom_type == "Polygon" else [x for x in g.geoms if x.geom_type == "Polygon"]
def fill(ax, g, fc, ec="none", lw=0.0, z=1, alpha=1.0, hatch=None):
    for p in polys(g):
        path_pts = list(p.exterior.coords)
        patch = MPoly(path_pts, closed=True, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha, hatch=hatch)
        ax.add_patch(patch)
        for h in p.interiors:
            ax.add_patch(MPoly(list(h.coords), closed=True, fc=WHITE, ec=ec, lw=lw, zorder=z + 0.01))
def outline(ax, g, ec, lw, z=5, ls="-"):
    for p in polys(g):
        xs, ys = p.exterior.xy; ax.plot(xs, ys, color=ec, lw=lw, zorder=z, ls=ls, solid_joinstyle="miter")
        for h in p.interiors: hx, hy = h.xy; ax.plot(hx, hy, color=ec, lw=lw, zorder=z, ls=ls)

def base_fig(wide=False, context=True):
    if wide: x0, y0, x1, y1 = bx[0] - 260, bx[1] - 140, bx[2] + 260, bx[3] + 140
    else: x0, y0, x1, y1 = bx[0] - 70, bx[1] - 40, bx[2] + 70, bx[3] + 40
    W = x1 - x0; H = y1 - y0; fig = plt.figure(figsize=(8 * W / H * 1.0 if W / H > 0.5 else 6.0, 8 if W / H > 0.5 else 12))
    fig = plt.figure(figsize=(7.2 * W / H + 0.01, 7.2)) if W / H > 0.9 else plt.figure(figsize=(9.5 * W / H, 9.5))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((x0, y0), W, H, fc=WHITE, ec="none", zorder=0))
    if context:
        for g in ctx_ground: fill(ax, g, CTX_GROUND, z=0.5)
        for g, h in ctx_bld_in: fill(ax, g, CTX_BLD, ec=CTX_BLD_EDGE, lw=0.25, z=0.8)
    return fig, ax

def frame_common(ax, title=None):
    outline(ax, B, RED, 1.6, z=9)
    # 북 화살표·축척
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); W = x1 - x0
    sx = x1 - W * 0.06 - 100; sy = y0 + (y1 - y0) * 0.03
    ax.plot([sx, sx + 100], [sy, sy], color=INK, lw=1.2, zorder=20); ax.plot([sx, sx], [sy - 3, sy + 3], color=INK, lw=1.0, zorder=20); ax.plot([sx + 100, sx + 100], [sy - 3, sy + 3], color=INK, lw=1.0, zorder=20)
    ax.text(sx + 50, sy + 6, "100 m", ha="center", va="bottom", fontsize=7, color=INK, zorder=20)
    nx = x1 - W * 0.06; ny = y1 - (y1 - y0) * 0.03
    ax.annotate("", xy=(nx, ny), xytext=(nx, ny - 36), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0), zorder=20); ax.text(nx, ny - 48, "N", ha="center", va="top", fontsize=8, color=INK, zorder=20)

def label(ax, g, text, size=6.5, color=INK, weight="bold", z=12, dx=0, dy=0, bg=True):
    c = g.representative_point()
    ax.text(c.x + dx, c.y + dy, text, ha="center", va="center", fontsize=size, color=color, fontweight=weight, zorder=z,
            bbox=dict(boxstyle="round,pad=0.18", fc=WHITE, ec="none", alpha=0.85) if bg else None)

def draw_streets(ax, z=2):
    for r in roads: fill(ax, r, ROAD_FILL, ec=G3, lw=0.5, z=z)
    for w, g in walks: fill(ax, g, PEDWAY_FILL if w["kind"] == "보행자전용도로" else WALK_FILL, ec=G4, lw=0.3, z=z)

# ── 1 토지이용계획도 ───────────────────────────────────────────────────────
def plan_landuse():
    fig, ax = base_fig()
    draw_streets(ax)
    for g, gg in greens: fill(ax, gg, GREEN_FILL[g["kind"]], ec=G3, lw=0.4, z=3, hatch="..." if False else None)
    for l, g in lots: fill(ax, g, USE_FILL[l["layer"]], ec=G1, lw=0.5, z=4)
    for p, g in plazas: fill(ax, g, PLAZA_FILL, ec=G3, lw=0.3, z=4.5)
    for l, g in lots: label(ax, g, "%s" % l["code"], size=7.5)
    for g, gg in greens: label(ax, gg, g["code"], size=6.5, color=G1, weight="normal")
    frame_common(ax)
    fig.savefig(OUT + r"\01_landuse.png"); plt.close(fig)

# ── 2 획지계획도(코드·면적) ─────────────────────────────────────────────────
def plan_lots():
    fig, ax = base_fig()
    draw_streets(ax)
    for g, gg in greens: fill(ax, gg, G6, ec=G3, lw=0.4, z=3)
    for l, g in lots: fill(ax, g, WHITE, ec=INK, lw=0.7, z=4)
    for p, g in plazas: outline(ax, g, G3, 0.3, z=4.5, ls=(0, (2, 2)))
    for l, g in lots: label(ax, g, "%s\n%s㎡" % (l["code"], format(round(l["area"]), ",")), size=6.2, bg=False)
    for g, gg in greens: label(ax, gg, "%s\n%s㎡" % (g["code"], format(round(g["area"]), ",")), size=5.6, color=G2, weight="normal", bg=False)
    frame_common(ax)
    fig.savefig(OUT + r"\02_lots.png"); plt.close(fig)

# ── 3 도로·보행계획도 ─────────────────────────────────────────────────────
def plan_streets():
    fig, ax = base_fig()
    for g, gg in greens: fill(ax, gg, G6, z=1)
    for l, g in lots: fill(ax, g, G5, ec="none", z=1)
    for r in roads: fill(ax, r, G1, ec="none", z=3)
    for w, g in walks: fill(ax, g, RED if w["kind"] == "보행자전용도로" else G3, ec="none", z=3.5, alpha=0.9 if w["kind"] == "보행자전용도로" else 1)
    for m, g in masses: outline(ax, g, G2, 0.3, z=4)
    frame_common(ax)
    fig.savefig(OUT + r"\03_streets.png"); plt.close(fig)

# ── 4 공원·녹지·오픈스페이스 계획도 ─────────────────────────────────────────
def plan_green():
    fig, ax = base_fig()
    draw_streets(ax)
    for l, g in lots: fill(ax, g, WHITE, ec=G4, lw=0.4, z=2)
    for g, gg in greens: fill(ax, gg, {"근린공원": "#CFCFCF", "문화공원": "#DADADA", "역사공원": RED_LT, "경관녹지": "#E6E6E6"}[g["kind"]], ec=G2, lw=0.5, z=3)
    for p, g in plazas: fill(ax, g, "#EFEFEF", ec=G2, lw=0.4, z=3.5, hatch="////")
    for kind, pts in D["trees"].items():
        a = np.array(pts)[:, :2]; ax.scatter(a[:, 0], a[:, 1], s=4.5 if kind == "park" else 3, c=G1 if kind != "lot" else G3, lw=0, zorder=6)
    for m, g in masses: fill(ax, g, "#BDBDBD", ec="none", z=5)
    for g, gg in greens: label(ax, gg, g["code"], size=6.5, color=INK)
    frame_common(ax)
    fig.savefig(OUT + r"\04_green.png"); plt.close(fig)

# ── 5 건축물 배치·높이 계획도 ────────────────────────────────────────────────
def plan_massing():
    fig, ax = base_fig()
    draw_streets(ax)
    for g, gg in greens: fill(ax, gg, G6, z=1)
    for l, g in lots: fill(ax, g, WHITE, ec=G4, lw=0.4, z=2)
    for p, g in plazas: fill(ax, g, "#F7F7F7", ec=G4, lw=0.3, z=2.5)
    for m, g in masses:
        fill(ax, g, MASS_FILL[m["cat"]], ec=INK, lw=0.35, z=5)
        if g.area > 450: label(ax, g, "%dF" % m["floors"], size=5.2, color=WHITE if m["cat"] in ("공공업무", "상업·업무", "문화·교육·공공", "역사유산", "여가·오락·체육") else INK, bg=False, z=6)
    for l, g in lots: label(ax, g, l["code"], size=6, color=G2, weight="normal", dx=0, dy=0, bg=False, z=4) if False else None
    frame_common(ax)
    fig.savefig(OUT + r"\05_massing.png"); plt.close(fig)

# ── 6 단계별 계획도 ──────────────────────────────────────────────────────────
PHASE = {1: ["공원1", "공원2", "녹지1", "공원3"], 2: ["문2", "문1", "관1", "상1", "문3", "공원6"], 3: ["주1", "업1", "업2", "문4", "문5", "체1", "공원4", "공원5"], 4: ["공1"]}
PHASE_FILL = {1: "#D6D6D6", 2: RED, 3: "#8A8A8A", 4: "#4A4A4A"}
def plan_phase():
    fig, ax = base_fig()
    for r in roads: fill(ax, r, "#DADADA", ec="none", z=3)
    for w, g in walks: fill(ax, g, "#E6E6E6", ec="none", z=3)
    code2 = {l["code"]: g for l, g in lots}; code2.update({g["code"]: gg for g, gg in greens})
    for ph, codes in PHASE.items():
        for c in codes:
            g = code2[c]; fill(ax, g, PHASE_FILL[ph], ec=WHITE, lw=0.6, z=4, alpha=0.95 if ph != 2 else 0.85)
            label(ax, g, "%d" % ph, size=8, color=WHITE if ph in (2, 3, 4) else INK, bg=False, z=6)
    for m, g in masses: outline(ax, g, WHITE, 0.3, z=5)
    frame_common(ax)
    fig.savefig(OUT + r"\06_phase.png"); plt.close(fig)

# ── 7 주변 연계도(넓은 범위) ───────────────────────────────────────────────
def plan_wide():
    fig, ax = base_fig(wide=True)
    draw_streets(ax)
    for g, gg in greens: fill(ax, gg, G6, ec=G4, lw=0.3, z=3)
    for l, g in lots: fill(ax, g, "#EDEDED", ec=G4, lw=0.3, z=3)
    for m, g in masses: fill(ax, g, MASS_FILL[m["cat"]], ec="none", z=5)
    # 동서 횡단축(계획 도로·보행축 중심선 표시)
    for w, g in walks:
        if w["kind"] == "보행자전용도로": fill(ax, g, RED_LT, ec="none", z=3.6)
    frame_common(ax)
    fig.savefig(OUT + r"\07_wide.png"); plt.close(fig)

if __name__ == "__main__":
    plan_landuse(); plan_lots(); plan_streets(); plan_green(); plan_massing(); plan_phase(); plan_wide()
    print("plans ok ->", OUT)
