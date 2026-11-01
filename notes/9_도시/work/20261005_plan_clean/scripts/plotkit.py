"""plotkit — 획지 계획 도면 공통 도구(데이터 로드·색·패치·표 그리기). A3 가로(420×297 mm) 페이지는 mm 좌표계 축으로 그린다."""
import pickle, sys, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle, Rectangle, Polygon as MPoly
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as pe
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import unary_union

import os as _os; SP = _os.environ.get("PLAN_SP", r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad")   # 입력 pkl 폴더. 재현 시 PLAN_SP=<work/20261005_plan_clean/data>
PM = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts"
OUT = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean"
sys.path.insert(0, PM)
from geomkit import polys

for f in ("malgun.ttf", "malgunbd.ttf"):
    try: fm.fontManager.addfont(r"C:\Windows\Fonts\%s" % f)
    except Exception: pass
plt.rcParams["font.family"] = "Malgun Gothic"; plt.rcParams["axes.unicode_minus"] = False

LP = pickle.load(open(SP + r"\lots.pkl", "rb")); M = pickle.load(open(SP + r"\clean_mass.pkl", "rb"))
C = pickle.load(open(SP + r"\context.pkl", "rb")); NET = pickle.load(open(SP + r"\network.pkl", "rb")); TC = pickle.load(open(SP + r"\tables_clean.pkl", "rb"))
U = C["U"]; LOTS, PARKS, BUILD = LP["LOTS"], LP["PARKS"], M["BUILD"]

# 용도 색 — 조감도(k4_axo)와 같은 팔레트
CATCOL = {"문화·교육·공공": "#6f9fdc", "상업·업무": "#e4573a", "창조산업": "#a98bd3", "여가·오락·체육": "#2fab9d", "주거": "#f1d247",
          "판매·음식": "#f4a0c2", "교통·방문자": "#c6c6c6", "역사유산": "#c9742f", "오픈스페이스": "#9fd36b"}
CATEN = {"문화·교육·공공": "Cultural / Edu / Civic", "상업·업무": "Office / Commercial", "창조산업": "Creative Industry", "여가·오락·체육": "Leisure / Recreation",
         "주거": "Residential", "판매·음식": "Retail / F&B", "교통·방문자": "Mobility / Visitor", "역사유산": "Heritage", "오픈스페이스": "Open Space"}
CATORDER = ["상업·업무", "창조산업", "문화·교육·공공", "판매·음식", "여가·오락·체육", "주거", "역사유산", "교통·방문자", "오픈스페이스"]
INK = "#222222"; GREY = "#ececec"; LINE = "#9a9a9a"; RED = "#d7191c"

def tint(h, t):
    """색을 흰색 쪽으로 t(0~1) 만큼 옅게"""
    c = np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float); c = c * (1 - t) + 255 * t
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)

def path_of(p):
    """구멍 있는 shapely Polygon → matplotlib Path"""
    verts, codes = [], []
    for ring in [p.exterior] + list(p.interiors):
        cs = list(ring.coords); verts += cs; codes += [Path.MOVETO] + [Path.LINETO] * (len(cs) - 2) + [Path.CLOSEPOLY]
    return Path(verts, codes)
def fill(ax, geom, fc="none", ec="none", lw=0.0, z=1, alpha=1.0, **kw):
    for p in polys(geom):
        if p.is_empty: continue
        ax.add_patch(PathPatch(path_of(p), fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha, **kw))

def halo(w=2.2, c="white"): return [pe.withStroke(linewidth=w, foreground=c)]

def num_circle(ax, x, y, s, r=None, fs=8, fc="white", ec=INK, tc=INK, z=20, lw=0.8, bold=True):
    """번호 원(데이터 좌표) — r 은 데이터 단위 반지름"""
    if r is None: r = 9.0
    ax.add_patch(Circle((x, y), r, fc=fc, ec=ec, lw=lw, zorder=z))
    ax.text(x, y, s, fontsize=fs, ha="center", va="center", color=tc, zorder=z + 1, fontweight="bold" if bold else "normal")

def road_label_points():
    """도로 이름 라벨 위치·각도(중심선 따라) — 부지 안쪽에 들어오는 구간의 중앙"""
    out = []
    for key, (coords, w, *_rest) in NET["STREETS"].items():
        ln = LineString(coords).intersection(U.buffer(-2))
        if ln.is_empty: continue
        segs = [g for g in ([ln] if ln.geom_type == "LineString" else list(ln.geoms)) if g.geom_type == "LineString" and not g.is_empty]
        if not segs: continue
        g = max(segs, key=lambda s: s.length)
        out.append((key, g, w))
    return out

class Page:
    """mm 좌표(0~420, 0~297, y 아래로 증가)로 그리는 A3 가로 페이지"""
    def __init__(self, W=420.0, H=297.0, dpi=150, bg="white"):
        self.W, self.H = W, H
        self.fig = plt.figure(figsize=(W / 25.4, H / 25.4), dpi=dpi, facecolor=bg)
        self.ax = self.fig.add_axes([0, 0, 1, 1]); self.ax.set_xlim(0, W); self.ax.set_ylim(H, 0); self.ax.axis("off")
    def t(self, x, y, s, fs=8, c=INK, ha="left", va="center", bold=False, z=5, **kw):
        return self.ax.text(x, y, s, fontsize=fs, color=c, ha=ha, va=va, fontweight="bold" if bold else "normal", zorder=z, **kw)
    def line(self, x0, y0, x1, y1, c=INK, lw=0.6, z=3, **kw): self.ax.plot([x0, x1], [y0, y1], color=c, lw=lw, zorder=z, solid_capstyle="butt", **kw)
    def rect(self, x, y, w, h, fc="none", ec="none", lw=0.0, z=2, **kw): self.ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z, **kw))
    def sub(self, x, y, w, h, **kw):
        """mm 좌표의 사각형 영역에 새 축 생성(도면 삽입용). 데이터 좌표는 호출자가 설정."""
        ax = self.fig.add_axes([x / self.W, 1 - (y + h) / self.H, w / self.W, h / self.H], **kw); return ax
    def save(self, path, dpi=None, pdf=None):
        self.fig.savefig(path, dpi=dpi or self.fig.dpi, facecolor=self.fig.get_facecolor())
        if pdf: self.fig.savefig(pdf, facecolor=self.fig.get_facecolor())

def title_block(pg, label, title_en, title_ko, x=16, y=20, sub=None):
    """통영 보고서 p.18 머리글 형식 — 붉은 소제목 + 굵은 제목 | 한글 제목"""
    pg.t(x, y, label, fs=11, c=RED)
    t = pg.t(x, y + 9.5, title_en, fs=21, bold=True)
    pg.fig.canvas.draw(); bb = t.get_window_extent(pg.fig.canvas.get_renderer()); wmm = bb.width / pg.fig.dpi * 25.4
    pg.line(x + wmm + 3.5, y + 5.5, x + wmm + 3.5, y + 13.5, c="#555", lw=0.8)
    pg.t(x + wmm + 7, y + 9.8, title_ko, fs=14, c="#444")
    if sub: pg.t(x, y + 19, sub, fs=8.2, c="#555")
    return wmm

def draw_context(ax, extent, fc="#e4e4e2", ec="none", z=1):
    """주변 건물 윤곽(연회색)"""
    x0, y0, x1, y1 = extent; win = box(x0, y0, x1, y1); pats = []
    for b in C["B"]:
        g = b["geom"]
        if not g.intersects(win): continue
        for p in polys(g): pats.append(PathPatch(path_of(p)))
    pc = PatchCollection(pats, fc=fc, ec=ec, lw=0, zorder=z); ax.add_collection(pc)

def draw_roads_ctx(ax, extent, z=0.5):
    x0, y0, x1, y1 = extent; win = box(x0, y0, x1, y1)
    for r in C["RP"]:
        if r.intersects(win): fill(ax, r, fc="#ffffff", z=z)

