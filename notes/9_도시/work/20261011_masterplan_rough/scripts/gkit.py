"""gkit — 최종 마스터플랜 다이어그램 공통 도구(16:9, 400×225 mm 페이지)
머리글(붉은 소제목 + 굵은 제목 | 한글 제목), 평면 축(북쪽 위, 로컬 m), 주변 건물 바탕, 축척 막대·방위표, 표 그리기
데이터: data/model.pkl(f1_model.py)"""
import os, sys, pickle, json, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import PathPatch, Circle, Rectangle, FancyArrowPatch, Polygon as MPoly, FancyBboxPatch
from matplotlib.path import Path
import matplotlib.patheffects as pe
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); OUTD = os.path.join(HERE, "..", "diagrams")
os.makedirs(OUTD, exist_ok=True)
for f in ("malgun.ttf", "malgunbd.ttf"):
    try: fm.fontManager.addfont(r"C:\Windows\Fonts\%s" % f)
    except Exception: pass
plt.rcParams["font.family"] = "Malgun Gothic"; plt.rcParams["axes.unicode_minus"] = False
import matplotlib.axes as _mpa                                              # 본문 글자 최소 10 pt(사용자 요청 — D1 설명 박스 제목 크기). 더 큰 글자는 그대로
MINFS = 10.0
_orig_text = _mpa.Axes.text
def _text_min(self, x, y, s_, *a, **kw):
    for k in ("fontsize", "size"):
        if k in kw and isinstance(kw[k], (int, float)) and kw[k] < MINFS: kw[k] = MINFS
    return _orig_text(self, x, y, s_, *a, **kw)
_mpa.Axes.text = _text_min
M = pickle.load(open(os.path.join(D, "model.pkl"), "rb"))
S = M["S"]; BLD, LINKS, LOTS, TOT = M["BLD"], M["LINKS"], M["LOTS"], M["TOT"]
B = S["B"]; CATS = S["CATS"]; X0, Y0, XS = S["X0"], S["Y0"], S["XSHIFT"]
INK = "#2b2b2b"; GREY = "#666666"; LGREY = "#9a9a9a"; RED = "#C8102E"; SLATE = "#4F6D8A"
PW, PH = 400.0, 225.0

# 평면용 용지 색(파스텔 팔레트를 한 단계 진하게) — 용지(획지) 범주
LOTCOL = {"공공업무": "#6E8FC9", "업무·창업": "#EE8A62", "문화": "#7FC0D6", "창작": "#AE93D6", "판매": "#F09AB0", "생활SOC": "#6FC6AA",
          "주거": "#F1CF7E", "역사": "#B97A4E", "방문자": "#B9C3CD", "주차": "#A3A8AE"}
PARKC = "#9CCF78"; WALKC = "#CFE8B6"; PLAZAC = "#EEE3CC"; ROADC = "#FFFFFF"; SIDEC = "#EEEEEC"


def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []


def tint(h, t):
    c = np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) * (1 - t) + 255 * t
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)


def shade(h, f):
    c = np.clip(np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) * f, 0, 255)
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)


def path_of(p):
    verts, codes = [], []
    for ring in [p.exterior] + list(p.interiors):
        cs = list(ring.coords); verts += cs; codes += [Path.MOVETO] + [Path.LINETO] * (len(cs) - 2) + [Path.CLOSEPOLY]
    return Path(verts, codes)


def fill(ax, g, fc="none", ec="none", lw=0.0, z=1, alpha=1.0, **kw):
    for p in polys(g):
        if p.is_empty or p.area < 0.01: continue
        ax.add_patch(PathPatch(path_of(p), fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha, **kw))


def halo(w=2.0, c="white"): return [pe.withStroke(linewidth=w, foreground=c)]
def f0(v): return format(int(round(v)), ",")


class Page:
    def __init__(self, dpi=240):
        self.fig = plt.figure(figsize=(PW / 25.4, PH / 25.4), dpi=dpi, facecolor="white")
        self.ax = self.fig.add_axes([0, 0, 1, 1]); self.ax.set_xlim(0, PW); self.ax.set_ylim(PH, 0); self.ax.axis("off")
    def t(self, x, y, s, fs=8, c=INK, ha="left", va="center", bold=False, z=10, **kw):
        return self.ax.text(x, y, s, fontsize=fs, color=c, ha=ha, va=va, fontweight="bold" if bold else "normal", zorder=z, **kw)
    def line(self, xs, ys, c=INK, lw=0.6, z=8, **kw): self.ax.plot(xs, ys, color=c, lw=lw, zorder=z, solid_capstyle="butt", **kw)
    def rect(self, x, y, w, h, fc="none", ec="none", lw=0.0, z=2, **kw): self.ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z, **kw))
    def wmm(self, t):
        self.fig.canvas.draw(); return t.get_window_extent(self.fig.canvas.get_renderer()).width / self.fig.dpi * 25.4
    def header(self, label, title_en, title_ko, sub=None, x=12, y=11, sub_fs=10.0):
        self.t(x, y, label, fs=10, c=RED)
        tt = self.t(x, y + 8.6, title_en, fs=19, bold=True)
        w = self.wmm(tt)
        self.line([x + w + 3.2, x + w + 3.2], [y + 4.8, y + 12.2], c="#555", lw=0.8)
        self.t(x + w + 6.4, y + 8.9, title_ko, fs=13, c="#444")
        if sub: self.t(x, y + 17.0 + (sub_fs - 7.4) * 0.15, sub, fs=sub_fs, c=GREY)
    def plan_ax(self, x, y, w, h, extent):
        """mm 영역(x,y,w,h)에 북쪽 위 평면 축(로컬 m) — extent=(x0,x1,y0,y1), 같은 축척 유지"""
        ax = self.fig.add_axes([x / PW, 1 - (y + h) / PH, w / PW, h / PH])
        ex0, ex1, ey0, ey1 = extent
        sx = (ex1 - ex0) / w; sy = (ey1 - ey0) / h; s = max(sx, sy)
        cx, cy = (ex0 + ex1) / 2, (ey0 + ey1) / 2
        ax.set_xlim(cx - s * w / 2, cx + s * w / 2); ax.set_ylim(cy - s * h / 2, cy + s * h / 2); ax.set_aspect("equal"); ax.axis("off")
        ax._mm_per_m = 1.0 / s
        return ax
    def top(self):
        """지도 축 위에 그릴 덮개 축(mm 좌표) — 범례·설명 박스가 지도 배경에 가려지지 않게"""
        ov = self.fig.add_axes([0, 0, 1, 1]); ov.set_xlim(0, PW); ov.set_ylim(PH, 0); ov.axis("off"); ov.patch.set_alpha(0.0)
        self.ax = ov; return ov
    def mm_of(self, ax, x, y):
        """데이터 좌표(축 ax) → 페이지 mm 좌표"""
        dx, dy = ax.transData.transform((x, y)); W_, H_ = self.fig.get_size_inches() * self.fig.dpi
        return dx / W_ * PW, PH - dy / H_ * PH
    def save(self, name):
        self.fig.savefig(os.path.join(OUTD, name + ".png"), dpi=240, facecolor="white")
        self.fig.savefig(os.path.join(OUTD, name + ".pdf"), facecolor="white")
        self.fig.savefig(os.path.join(D, "..", "sheets", name + "_preview.png"), dpi=110, facecolor="white")
        plt.close(self.fig); print("saved", name)


CTX = None
def ctx_buildings(include_inside=False):
    """정합된 주변 건물(로컬, data/ctx_fixed.pkl — c0·c1 참고). [(polygon, h)]"""
    CF = pickle.load(open(os.path.join(D, "ctx_fixed.pkl"), "rb"))
    return [(o["g"], o["h"]) for o in CF["B"] if include_inside or not o["inside"]]


def context(ax, extent, fc="#e6e6e3", ec="#d4d4d0", lw=0.25, z=0.5, alpha=1.0):
    """주변 건물 평면 — 콘타 모델 맥락을 V-World 연속지적에 재정합한 것(2배·회전 0)"""
    global CTX
    if CTX is None:
        CTX = [g for g, h in ctx_buildings()]
    win = box(extent[0], extent[2], extent[1], extent[3])
    from matplotlib.collections import PatchCollection
    pats = [PathPatch(path_of(p)) for g in CTX if g.intersects(win) for p in polys(g)]
    ax.add_collection(PatchCollection(pats, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha))


def ground(ax, z=1.0, lots=True, lotcol=None, lot_alpha=1.0, parks=True, open_=True, roads=True, walks=True, plazas=False, bound=True, road_fc=None):
    """지면 기본 — 도로·보도·보행축·공원·획지"""
    if roads:
        for g in S["ROADS"].values(): fill(ax, g, fc=road_fc or ROADC, ec="#bdbdb8" if road_fc is None else "none", lw=0.3, z=z + (0.4 if road_fc else 0))
    if walks:
        fill(ax, S["WALK"], fc=SIDEC, ec="none", z=z); fill(ax, S["PATH8"], fc=SIDEC, z=z)
    if open_:
        for o in S["OPEN"]: fill(ax, o["g"], fc=WALKC, z=z + 0.1)
    if parks:
        for p in S["PARKS"]: fill(ax, p["g"], fc=PARKC, z=z + 0.1)
    if lots:
        for l in S["LOTS"]:
            c = (lotcol or {}).get(l["no"], LOTCOL[l["cat"]])
            fill(ax, l["g"], fc=c, ec="white", lw=0.6, z=z + 0.2, alpha=lot_alpha)
    if plazas:
        for p in S["PLZ"]:
            if p["kind"] in ("광장", "코트"): fill(ax, p["g"], fc=PLAZAC, z=z + 0.3)
    if bound:
        xs, ys = B.exterior.xy; ax.plot(xs, ys, color=RED, lw=1.0, ls=(0, (4, 2)), zorder=z + 5)


def north_scale(ax, x, y, mm_len=None, label_m=(0, 100, 250), fs=6, north_at=None):
    """평면 축 데이터 좌표(x,y)에 방위표와 축척 막대(0·100·250 m)"""
    L = label_m[-1]
    for i, (a, b) in enumerate(zip(label_m, label_m[1:])):
        ax.add_patch(Rectangle((x + a, y), b - a, 6, fc=INK if i % 2 == 0 else "white", ec=INK, lw=0.5, zorder=30))
    for v in label_m: ax.text(x + v, y + 10, "%d" % v, fontsize=fs, ha="center", va="bottom", zorder=30, color=INK)
    ax.text(x + L + 12, y + 3, "m", fontsize=fs, va="center", zorder=30, color=INK)
    nx, ny = (x + L + 60, y - 4) if north_at is None else north_at
    ax.add_patch(MPoly([(nx, ny + 46), (nx - 11, ny), (nx, ny + 9), (nx + 11, ny)], closed=True, fc=INK, ec=INK, lw=0.5, zorder=30))
    ax.text(nx, ny + 52, "N", fontsize=fs + 1.5, ha="center", va="bottom", fontweight="bold", zorder=30, color=INK)


def lot_label_pt(l, avoid=None):
    from shapely.ops import polylabel
    g = l["g"]
    if avoid is not None:
        fr = g.difference(avoid.buffer(2.0))
        if not fr.is_empty and fr.area > 0.25 * g.area: g = max(polys(fr), key=lambda p: p.area)
    return polylabel(max(polys(g), key=lambda p: p.area), 1.0)


def table(pg, x, y, cols, rows, widths, rh=5.2, fs=6.4, head_fc="#3c3c3c", head_c="white", zebra="#f5f5f3", sub_fc="#e7e7e4", aligns=None, bold_rows=(), sub_rows=(), color_chip=None):
    """mm 좌표 표. rows: list of lists, color_chip: {row_index: hex}(첫 칸 왼쪽 색 칩)"""
    W = sum(widths); xs = [x]
    for w in widths: xs.append(xs[-1] + w)
    pg.rect(x, y, W, rh + 0.6, fc=head_fc, z=5)
    for i, c in enumerate(cols):
        pg.t(xs[i] + widths[i] / 2, y + (rh + 0.6) / 2, c, fs=fs, c=head_c, ha="center", bold=True, z=6)
    yy = y + rh + 0.6
    for r, row in enumerate(rows):
        fc = sub_fc if r in sub_rows else (zebra if r % 2 else "white")
        pg.rect(x, yy, W, rh, fc=fc, z=5)
        for i, v in enumerate(row):
            a = (aligns or ["left"] * len(cols))[i]
            tx = xs[i] + 1.2 if a == "left" else (xs[i + 1] - 1.2 if a == "right" else xs[i] + widths[i] / 2)
            off = 0.0
            if i == 0 and color_chip and r in color_chip:
                pg.rect(xs[0] + 1.0, yy + 1.1, 2.6, rh - 2.2, fc=color_chip[r], ec="#999", lw=0.2, z=6); off = 3.4
            pg.t(tx + off, yy + rh / 2, str(v), fs=fs, ha="left" if a == "left" else a, bold=(r in bold_rows or r in sub_rows), z=6, c=INK)
        yy += rh
    pg.line([x, x + W], [yy, yy], c="#3c3c3c", lw=0.8, z=7)
    return yy


# ── 10 pt 배치 도구 ─────────────────────────────────────────
_WCACHE = {}
def text_w(pg, s, fs=10.0, bold=False):
    """글자열의 실제 폭(mm)"""
    k = (s, fs, bold)
    if k not in _WCACHE:
        t_ = pg.ax.text(0, 0, s, fontsize=fs, fontweight="bold" if bold else "normal"); _WCACHE[k] = pg.wmm(t_); t_.remove()
    return _WCACHE[k]


def wrap_mm(pg, text, width, fs=10.0, bold=False):
    """어절 단위로 실제 폭(mm)에 맞춰 줄 나눔(어절이 폭보다 길면 글자 단위)"""
    lines = []
    for para in str(text).split("\n"):
        cur = ""
        for w_ in para.split(" "):
            cand = (cur + " " + w_).strip()
            if text_w(pg, cand, fs, bold) <= width or not cur:
                if text_w(pg, cand, fs, bold) > width and not cur:          # 한 어절이 너무 길면 글자 단위
                    piece = ""
                    for ch in cand:
                        if text_w(pg, piece + ch, fs, bold) > width and piece: lines.append(piece); piece = ch
                        else: piece += ch
                    cur = piece
                else: cur = cand
            else:
                lines.append(cur); cur = w_
        lines.append(cur)
    return lines


def text_block(pg, x, y, text, width, fs=10.0, lh=None, c=INK, bold=False, z=6, bullet=False):
    """줄 나눔 글 블록 — 첫 줄 중심 y. 반환: 마지막 줄 다음 y"""
    lh = lh or fs * 0.50
    L = wrap_mm(pg, text, width - (3.6 if bullet else 0), fs, bold)
    if bullet: pg.t(x, y, "•", fs=fs, c=c, z=z)
    for j, ln in enumerate(L): pg.t(x + (3.6 if bullet else 0), y + j * lh, ln, fs=fs, c=c, bold=bold, z=z)
    return y + len(L) * lh


def block_h(pg, text, width, fs=10.0, lh=None, bold=False, bullet=False):
    lh = lh or fs * 0.50
    return len(wrap_mm(pg, text, width - (3.6 if bullet else 0), fs, bold)) * lh
