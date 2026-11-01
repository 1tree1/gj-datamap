"""S5 렌더 — 참고 이미지(색 구분 매스 마스터플랜) 스타일: 사선 압출 + 그림자 + 수목 + 범례.
사용: render(path, ...)  /  단독 실행하면 plan_massing_v1.png 생성"""
import pickle, sys, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, Circle, Patch
from matplotlib.collections import PolyCollection
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
from shapely import wkb
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
sys.path.insert(0, r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts")
from geomkit import polys, poisson
fm.fontManager.addfont(r"C:\Windows\Fonts\malgun.ttf"); plt.rcParams["font.family"] = "Malgun Gothic"

CATCOL = {"문화·교육·공공": "#3d8fd8", "상업·업무": "#e0432d", "창조산업": "#8e4fb8", "여가·오락·체육": "#1f9e92", "주거": "#f6df4a",
          "판매·음식": "#f08ab4", "교통·방문자": "#b9b9b9", "역사유산": "#b8662b", "오픈스페이스": "#6bbd3c"}
LEG_ORDER = ["문화·교육·공공", "상업·업무", "창조산업", "여가·오락·체육", "주거", "판매·음식", "교통·방문자", "역사유산", "오픈스페이스"]

def shade(hexc, f):
    c = np.array(matplotlib.colors.to_rgb(hexc)); return tuple(np.clip(c * f, 0, 1))

def load():
    import os
    C = pickle.load(open(SP + r"\context.pkl", "rb")); NET = pickle.load(open(SP + r"\network.pkl", "rb"))
    M = pickle.load(open(SP + (r"\massing2.pkl" if os.path.exists(SP + r"\massing2.pkl") else r"\massing.pkl"), "rb"))
    return C, NET, M

def bcolor(b):
    """건물 색: 범례 분류색. 주차는 어두운 회색으로 구분."""
    return "#9a9a9a" if b.get("role") == "주차" else CATCOL[b["cat"]]

def extrude_draw(ax, geom, h, color, zbase=0, tilt=0.62, light_az=135, lw=0.25, alpha=1.0, zorder=10):
    """사선 압출: 지붕을 (0, +h*tilt) 만큼 올려 그린다(남쪽에서 본 시점). 벽은 방위별 명도."""
    for p in polys(geom):
        cs = list(p.exterior.coords)
        off = np.array([0.0, h * tilt])
        # 벽: 모든 변을 그리되, 시점(남쪽)에서 보이는 변만 (바깥 법선의 y 성분이 음수)
        for i in range(len(cs) - 1):
            a = np.array(cs[i]); b = np.array(cs[i + 1])
            d = b - a
            n = np.array([d[1], -d[0]]) if p.exterior.is_ccw is False else np.array([-d[1], d[0]])   # 바깥 법선(ccw 면은 오른쪽)
            n = np.array([d[1], -d[0]])
            if not p.exterior.is_ccw: n = -n
            if n[1] > 0.05 * np.linalg.norm(n) and h > 0.5: continue   # 북향 벽은 지붕에 가려짐
            ang = math.degrees(math.atan2(n[1], n[0]))
            f = 0.72 if abs(n[0]) > abs(n[1]) else 0.86
            if n[0] > 0: f *= 0.92
            quad = [a, b, b + off, a + off]
            ax.add_patch(MPoly(quad, closed=True, fc=shade(color, f), ec=shade(color, 0.55), lw=lw * 0.8, zorder=zorder, alpha=alpha))
        roof = [np.array(c) + off for c in cs]
        ax.add_patch(MPoly(roof, closed=True, fc=shade(color, 1.0), ec=shade(color, 0.6), lw=lw, zorder=zorder + 0.1, alpha=alpha))

def shadow(ax, geom, h, zorder=5, dx=0.55, dy=-0.38, alpha=0.20):
    for p in polys(geom):
        a = p; b = Polygon([(x + h * dx, y + h * dy) for x, y in p.exterior.coords])
        hull = unary_union([a, b]).convex_hull if h > 0.5 else a
        # 볼록하지 않은 건물(ㄷ,ㄱ자)은 변 단위 평행사변형 합집합이 정확
        parts = [a, b]
        cs = list(p.exterior.coords)
        for i in range(len(cs) - 1):
            q = Polygon([cs[i], cs[i + 1], (cs[i + 1][0] + h * dx, cs[i + 1][1] + h * dy), (cs[i][0] + h * dx, cs[i][1] + h * dy)])
            if q.is_valid and q.area > 0: parts.append(q)
        sh = unary_union(parts)
        for s in polys(sh): ax.add_patch(MPoly(list(s.exterior.coords), closed=True, fc="#1b1b1b", ec="none", alpha=alpha, zorder=zorder))

def tree(ax, x, y, r, c="#5aa63a", zorder=8):
    ax.add_patch(Circle((x + r * 0.5, y - r * 0.35), r, fc="#1b1b1b", ec="none", alpha=0.16, zorder=zorder - 0.3))
    ax.add_patch(Circle((x, y), r, fc=c, ec="#3f7f28", lw=0.3, zorder=zorder))
    ax.add_patch(Circle((x - r * 0.25, y + r * 0.25), r * 0.55, fc="#7ccb52", ec="none", alpha=0.8, zorder=zorder + 0.05))

def render(path, title="", figw=11.0, dpi=150, crop=None, callouts=True, show_context=True, trees=True, legend=True, tilt=0.62, extra_title=None, numbering=None):
    C, NET, M = load(); U = C["U"]
    x0, y0, x1, y1 = (U.buffer(28).bounds if crop is None else crop)
    aspect = (y1 - y0) / (x1 - x0)
    fig = plt.figure(figsize=(figw, figw * aspect + 0.9)); ax = fig.add_axes([0.01, 0.01, 0.98, 0.93 if title else 0.98])
    ax.set_facecolor("#efeeea"); fig.patch.set_facecolor("#efeeea")
    # 맥락: 도로면(흰색) + 건물(회색 압출)
    for r in C["RP"]:
        for p in polys(r): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#ffffff", ec="none", zorder=1))
    # 부지 안: 가구 지반(밝은 회), 도로(흰색), 녹지
    box = Polygon([(x0 - 50, y0 - 50), (x1 + 50, y0 - 50), (x1 + 50, y1 + 50), (x0 - 50, y1 + 50)])
    for p in polys(U): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#f7f6f3", ec="none", zorder=2))
    road_all = unary_union([NET["road_all"], NET["plaza_extra"]])
    for p in polys(road_all): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#ffffff", ec="#d9d6cf", lw=0.4, zorder=3))
    for p in polys(NET["green_all"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#a6d982", ec="#6aa84a", lw=0.5, zorder=3))
    # 광장·마당·주차 포장
    for nm, g in M["EXTRA"]["plaza"]:
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#ece7de", ec="none", zorder=3.2))
    for nm, g in M["EXTRA"]["court"]:
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#cfe6b4", ec="#9cc77a", lw=0.3, zorder=3.3))
    for nm, g in M["EXTRA"]["surface_parking"]:
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#cfcfcf", ec="#9a9a9a", lw=0.3, hatch="////", zorder=3.3))
    for nm, g in M["EXTRA"]["heritage_plaza"]:
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#e9d9bd", ec="#b8662b", lw=0.8, zorder=3.4))
    for nm, g in M["EXTRA"]["path"]:
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#f0e9d6", ec="none", zorder=3.4))
    for nm, g in M["EXTRA"]["court"]:
        if "운동장" in nm:
            for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#d98a6a", ec="#ffffff", lw=0.8, zorder=3.5))
    # 맥락 건물 (층수×3.5 m)
    if show_context:
        cb = [b for b in C["B"] if not U.contains(b["geom"].representative_point())]
        cb.sort(key=lambda b: -b["geom"].centroid.y)
        for b in cb:
            if not (x0 - 20 < b["geom"].centroid.x < x1 + 20 and y0 - 20 < b["geom"].centroid.y < y1 + 20): continue
            h = b["floors"] * 3.5
            col = "#d8d3c8" if b["floors"] <= 2 else "#cbc5b8" if b["floors"] <= 4 else "#b9b2a4"
            shadow(ax, b["geom"], h, zorder=4, alpha=0.10)
            extrude_draw(ax, b["geom"], h, col, tilt=tilt, zorder=6)
    # 부지 건물
    bl = sorted(M["BUILD"], key=lambda b: -b["geom"].centroid.y)
    for b in bl: shadow(ax, b["geom"], b["h"], zorder=5)
    for b in bl: extrude_draw(ax, b["geom"], b["h"], bcolor(b), tilt=tilt, zorder=10 + (1000 - b["geom"].centroid.y % 1000) * 0.0001)
    # 수목
    if trees:
        rng = np.random.default_rng(3)
        for nm, g in [("g", NET["green_all"])] + [("z", z) for z in M["EXTRA"]["tree_zone"]]:
            for p in polys(g):
                for q in poisson(p.buffer(-1.5), 9.0 if nm == "g" else 8.0, seed=int(p.area) % 97 + 1):
                    r = rng.uniform(2.6, 4.2)
                    if all(not bb["geom"].buffer(1.0).contains(q) for bb in bl if abs(bb["geom"].centroid.x - q.x) < 80 and abs(bb["geom"].centroid.y - q.y) < 80):
                        tree(ax, q.x, q.y, r)
        # 가로수
        for k, (pts, w, *_r) in NET["STREETS"].items():
            if w < 10: continue
            ln = LineString(pts)
            for side in (-1, 1):
                off = ln.parallel_offset(w / 2 - 1.5, "left" if side > 0 else "right")
                if off.is_empty: continue
                for seg in (off.geoms if hasattr(off, "geoms") else [off]):
                    n = int(seg.length // 11)
                    for i in range(n):
                        q = seg.interpolate((i + 0.5) / n, normalized=True)
                        if U.contains(q) and NET["road_all"].contains(q): tree(ax, q.x, q.y, 2.4, c="#6fb34a", zorder=8.5)
    ax.plot(*U.exterior.xy, color="#8a2be2", lw=1.6, zorder=40, ls=(0, (6, 3)))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")
    if title: fig.text(0.5, 0.975, title, ha="center", va="top", fontsize=13, fontweight="bold")
    if legend:
        used = {b["cat"] for b in M["BUILD"]} | {"오픈스페이스"}
        h = [Patch(fc=CATCOL[k], ec="#555", label=k) for k in LEG_ORDER if k in used]
        lg = ax.legend(handles=h, loc="lower left", fontsize=8, title="범례", title_fontsize=9, framealpha=0.95, bbox_to_anchor=(0.01, 0.01))
        lg.set_zorder(100)
    fig.savefig(path, dpi=dpi, facecolor=fig.get_facecolor()); plt.close(fig)
    return path

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else SP + r"\massing_preview.png"
    render(out, title="구경주역 도시계획안 — 매스 미리보기", figw=9.0, dpi=130)
    print("saved", out)
