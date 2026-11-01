# -*- coding: utf-8 -*-
"""발표 슬라이드용 분석 지도 공통 도구 (M4·M5·M6a~d·M8).

- 모든 공간 자료는 읽자마자 EPSG:5187 (Korea 2000 동부원점)로 변환한다. 원본은 건드리지 않는다.
- 스타일: 흰 바탕, 건물 #DADADA, 하천 #BFD7EA, 녹지 #CFE3B8, 도로 #C8C8C8 0.5pt, 대상지 경계 #D7191C 2.6pt, Pretendard.
- 크기 규칙: 그림 폭 6in로 슬라이드에 놓였을 때 본문 라벨 9pt 이상.
  figsize = (W/300, H/300) in, dpi = 300 이고, 글자·선 굵기는 K = W/1800 배로 환산한다
  (슬라이드 pt × K = 그림 안 pt). 예) W=1800 → 9pt 글자 = 그림 안 9pt, W=1200 → 6pt, W=2000 → 10pt.
- 실행 전 `export PYTHONUTF8=1 PYTHONIOENCODING=utf-8`.
"""
from __future__ import annotations

import json
import math
import os
import warnings
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import PathPatch, Polygon as MPoly, Rectangle, FancyArrowPatch
from matplotlib.path import Path as MPath

import shapely
import shapely.affinity
from shapely.geometry import (LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon, box,
                              shape)
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely.strtree import STRtree
from pyproj import Transformer

warnings.filterwarnings("ignore")

# ── 경로 ─────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
PRJ = HERE.parent                                   # work/20261008_presentation_front
ROOT = PRJ.parent.parent                            # 9_도시
OUT = PRJ / "assets" / "maps"
DATA_SERIES = PRJ / "research" / "data_series"
PROC = ROOT / "archive" / "C_data" / "processed"
RAW = ROOT / "archive" / "C_data" / "raw"
DERIVED = ROOT / "archive" / "90_derived"
NGII = ROOT / "대지" / "(B020)연속수치지도_202609132098"
PLAN_BOUNDARY = ROOT / "work" / "20261005_boundary_check" / "user_boundary_current_5187.geojson"
for _d in (OUT, DATA_SERIES):
    _d.mkdir(parents=True, exist_ok=True)

# ── 색 (지도 공통 스타일) ───────────────────────────────────────────
INK, INK2, GRAY, LINE, TINT = "#231F20", "#4D4D4D", "#6D6E71", "#D1D3D4", "#F5F7FA"
RED, BLUE = "#D7191C", "#1F5AA6"
C_BLD, C_WATER, C_GREEN, C_ROAD = "#DADADA", "#BFD7EA", "#CFE3B8", "#C8C8C8"
C_BLD4 = ["#E6E2D8", "#CFC8B8", "#9C9482", "#4D4D4D"]
# 용도 범주(덱 공통): 북측·중앙·남측
C_NORTH, C_CENTER, C_SOUTH = "#6F9FDC", "#A98BD3", "#F4A0C2"
C_PARKING, C_YELLOW = "#C6C6C6", "#F1D247"

# ── 글꼴 ─────────────────────────────────────────────────────────────
_FONT_DIR = Path("C:/Users/OFFICE/AppData/Local/Microsoft/Windows/Fonts")
FONT_FAMILY = "Malgun Gothic"


def setup_fonts():
    """Pretendard 를 등록한다(없으면 Malgun Gothic)."""
    global FONT_FAMILY
    ok = False
    for w in ("Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold"):
        p = _FONT_DIR / f"Pretendard-{w}.otf"
        if p.exists():
            fm.fontManager.addfont(str(p))
            ok = True
    if ok:
        FONT_FAMILY = "Pretendard"
    else:
        FONT_FAMILY = "Malgun Gothic"
    for p in ("C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/malgunbd.ttf"):
        if os.path.exists(p):
            fm.fontManager.addfont(p)
    plt.rcParams["font.family"] = [FONT_FAMILY, "Malgun Gothic"]          # ㎡·로마숫자 등 빠진 글리프는 맑은 고딕으로
    plt.rcParams["axes.unicode_minus"] = False
    import logging
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    return FONT_FAMILY


setup_fonts()

# ── 좌표 변환 ───────────────────────────────────────────────────────
T_5179_5187 = Transformer.from_crs("EPSG:5179", "EPSG:5187", always_xy=True)
T_4326_5187 = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True)


def _tf(T):
    def f(a):
        a = np.asarray(a, float)
        x, y = T.transform(a[:, 0], a[:, 1])
        return np.column_stack([x, y])
    return f


def to5187(geom, T=T_5179_5187):
    """shapely 도형(들) 좌표 변환. 단일 도형 또는 배열 모두 가능."""
    return shapely.transform(geom, _tf(T), include_z=False)


def ll_to_5187(geom):
    return to5187(geom, T_4326_5187)


# ── NGII 연속수치지도 ───────────────────────────────────────────────
def _fix_text(v):
    """수치지도 DBF 문자열은 cp949 바이트가 latin-1 로 읽힌 뒤 UTF-8 로 저장된 이중 인코딩."""
    if isinstance(v, str):
        try:
            return v.encode("latin-1").decode("cp949").strip()
        except Exception:
            return v.strip()
    return v


_NGII_CACHE: dict = {}


def read_ngii(layer: str):
    """NGII 레이어 → [(shapely 도형(5187), 속성 dict)]. 같은 프로세스 안에서는 캐시."""
    import shapefile  # pyshp
    if layer in _NGII_CACHE:
        return _NGII_CACHE[layer]
    r = shapefile.Reader(str(NGII / layer))
    flds = [f[0] for f in r.fields[1:]]
    geoms, attrs = [], []
    for s in r.iterShapeRecords():
        geoms.append(shape(s.shape.__geo_interface__))
        attrs.append({k: _fix_text(v) for k, v in zip(flds, s.record)})
    g5187 = to5187(np.array(geoms, dtype=object))
    out = list(zip(list(g5187), attrs))
    _NGII_CACHE[layer] = out
    return out


def ngii_bbox_5187():
    """연속수치지도 범위(5179 축정렬 사각형)를 5187 로 옮긴 사각형."""
    import shapefile
    r = shapefile.Reader(str(NGII / "N3L_A0020000")).bbox
    return to5187(box(*r).segmentize(20))


# ── 대상지·고시 자료 ───────────────────────────────────────────────
def load_geojson(path, crs="5187"):
    d = json.load(open(path, encoding="utf-8"))
    feats = []
    for f in d["features"]:
        g = shape(f["geometry"])
        if crs == "4326":
            g = ll_to_5187(g)
        feats.append((g, f["properties"]))
    return feats


def plan_boundary():
    """본 계획 경계 218,478㎡ (사용자 라이노 경계, EPSG:5187)."""
    return load_geojson(PLAN_BOUNDARY)[0][0]


def gosi_zone():
    """고시 2026-8호 구역(도면 추출 158,472㎡, 조서 156,460㎡)."""
    return load_geojson(PROC / "gosi2026-8_zone_5187.geojson")[0][0]


def gosi_blocks():
    return load_geojson(PROC / "gosi2026-8_blocks_5187.geojson")


# ── 도형 → 그리기 ──────────────────────────────────────────────────
def _poly_path(poly: Polygon) -> MPath:
    poly = orient(poly, 1.0)
    rings = [poly.exterior] + list(poly.interiors)
    verts, codes = [], []
    for r in rings:
        c = np.asarray(r.coords)
        verts.extend(c)
        codes.extend([MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY])
    return MPath(np.array(verts), codes)


def iter_polys(geom):
    if geom is None or geom.is_empty:
        return
    if geom.geom_type == "Polygon":
        yield geom
    elif geom.geom_type in ("MultiPolygon", "GeometryCollection"):
        for g in geom.geoms:
            yield from iter_polys(g)


def iter_lines(geom):
    if geom is None or geom.is_empty:
        return
    if geom.geom_type == "LineString":
        yield geom
    elif geom.geom_type == "LinearRing":
        yield LineString(geom.coords)
    elif geom.geom_type in ("MultiLineString", "GeometryCollection"):
        for g in geom.geoms:
            yield from iter_lines(g)


def draw_poly(ax, geom, fc="none", ec="none", lw=0.0, alpha=None, z=2, ls="-", hatch=None, **kw):
    """(Multi)Polygon 을 구멍까지 정확히 칠한다. 한 도형 = 하나의 PathPatch. alpha 를 주지 않으면 fc 의 RGBA 알파를 그대로 쓴다."""
    for p in iter_polys(geom):
        ax.add_patch(PathPatch(_poly_path(p), facecolor=fc, edgecolor=ec, linewidth=lw, alpha=alpha,
                               zorder=z, linestyle=ls, hatch=hatch, **kw))


def draw_polys_fast(ax, geoms, fc, ec="none", lw=0.0, z=1, alpha=1.0):
    """건물처럼 개수가 많은 도형(외곽선만) — PolyCollection."""
    rings = []
    for g in geoms:
        for p in iter_polys(g):
            rings.append(np.asarray(p.exterior.coords))
    ax.add_collection(PolyCollection(rings, facecolors=fc, edgecolors=ec, linewidths=lw, zorder=z, alpha=alpha))


def draw_lines(ax, geoms, color, lw, z=2, alpha=1.0, ls="-", capstyle="butt"):
    segs = []
    for g in geoms:
        for l in iter_lines(g):
            segs.append(np.asarray(l.coords))
    ax.add_collection(LineCollection(segs, colors=color, linewidths=lw, zorder=z, alpha=alpha, linestyles=ls,
                                     capstyle=capstyle))


def draw_outline(ax, geom, color, lw, z=5, ls="-", alpha=1.0, joinstyle="round"):
    for p in iter_polys(geom):
        for r in [p.exterior] + list(p.interiors):
            x, y = r.xy
            ax.plot(x, y, color=color, lw=lw, zorder=z, ls=ls, alpha=alpha, solid_joinstyle=joinstyle,
                    solid_capstyle="round")


# ── 도로·건물 공통 배경 ─────────────────────────────────────────────
def load_buildings(win=None):
    """건물 폴리곤(5187). win 이 주어지면 그 안(교차)만."""
    b = read_ngii("N3A_B0010000")
    geoms = [g for g, a in b if g.area >= 1.0]
    if win is not None:
        tree = STRtree(geoms)
        idx = tree.query(win, predicate="intersects")
        geoms = [geoms[i] for i in sorted(idx)]
    return geoms


def load_building_floors(win=None):
    b = read_ngii("N3A_B0010000")
    out = []
    for g, a in b:
        if g.area < 1.0:
            continue
        if win is not None and not g.intersects(win):
            continue
        try:
            fl = int(a.get("nmly") or 1) or 1
        except Exception:
            fl = 1
        out.append((g, fl))
    return out


def load_roads(win=None):
    r = read_ngii("N3L_A0020000")
    geoms = [g for g, a in r]
    attrs = [a for g, a in r]
    if win is not None:
        tree = STRtree(geoms)
        idx = sorted(tree.query(win, predicate="intersects"))
        geoms = [geoms[i] for i in idx]
        attrs = [attrs[i] for i in idx]
    return geoms, attrs


def load_water(win=None):
    """하천·호소 면(N3A_E0010001 하천, N3A_E0032111 호소)."""
    geoms = []
    for lay in ("N3A_E0010001", "N3A_E0032111"):
        geoms += [g for g, a in read_ngii(lay)]
    geoms = [g for g in geoms if win is None or g.intersects(win)]
    return geoms


def draw_water(ax, win, z=0.5):
    """하천 면(N3A_E0010001)을 맥락 지도와 같은 #BFD7EA 로 칠한다."""
    g = unary_union([g for g in load_water_river(win)])
    if not g.is_empty:
        draw_poly(ax, g.intersection(win), fc=C_WATER, ec="none", z=z)


def load_water_river(win=None):
    """하천 면 N3A_E0010001 (맥락 지도 mapkit_context.water_in 과 같은 레이어)."""
    return [g for g, a in read_ngii("N3A_E0010001") if win is None or g.intersects(win)]


# ── 그림틀 ──────────────────────────────────────────────────────────
DPI = 300


class Frame:
    """W×H px(300dpi) 흰 바탕 그림 + 실좌표 축(equal) + 픽셀 좌표 오버레이.

    K = W/1800 : 슬라이드 pt(그림 폭 6in 기준) → 그림 안 pt 환산 계수.
    """

    def __init__(self, W, H, cx, cy, w_m, h_m=None, name=""):
        self.W, self.H = W, H
        self.K = W / 1800.0
        self.name = name
        self.w_m = w_m
        self.h_m = h_m if h_m is not None else w_m * H / W
        self.cx, self.cy = cx, cy
        self.fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor="white")
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(cx - self.w_m / 2, cx + self.w_m / 2)
        self.ax.set_ylim(cy - self.h_m / 2, cy + self.h_m / 2)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.ax.set_facecolor("white")
        # 픽셀 오버레이 (원점 좌상단, y 아래로)
        self.ov = self.fig.add_axes([0, 0, 1, 1], facecolor="none")
        self.ov.set_xlim(0, W)
        self.ov.set_ylim(H, 0)
        self.ov.axis("off")
        self.ov.set_zorder(50)
        self.ppm = W / self.w_m            # px per meter
        self.win = box(cx - self.w_m / 2, cy - self.h_m / 2, cx + self.w_m / 2, cy + self.h_m / 2)

    # 슬라이드 pt → 그림 안 pt
    def pt(self, x):
        return x * self.K

    # 실좌표 ↔ 픽셀(좌상단 원점)
    def to_px(self, x, y):
        px = (x - (self.cx - self.w_m / 2)) * self.ppm
        py = ((self.cy + self.h_m / 2) - y) * self.ppm
        return px, py

    def from_px(self, px, py):
        x = (self.cx - self.w_m / 2) + px / self.ppm
        y = (self.cy + self.h_m / 2) - py / self.ppm
        return x, y

    # ── 글자 ──
    def label(self, x, y, s, size=9.5, color=INK, weight="medium", ha="center", va="center", rot=0.0, z=30,
              halo_px=3.0, ax=None, linespacing=1.18, **kw):
        """실좌표(x,y)에 라벨. 흰색 외곽(halo 3px). size 는 슬라이드 pt(그림 폭 6in 기준).
        맥락 지도(mapkit_context)와 같게 기본 글자 굵기는 medium."""
        ax = ax or self.ax
        t = ax.text(x, y, s, fontsize=self.pt(size), color=color, fontweight=weight, ha=ha, va=va, rotation=rot,
                    zorder=z, linespacing=linespacing, **kw)
        if halo_px:
            t.set_path_effects([pe.withStroke(linewidth=halo_px * 2 * 72 / DPI, foreground="white", capstyle="round",
                                              joinstyle="round")])
        return t

    def label_px(self, px, py, s, **kw):
        """픽셀 오버레이(좌상단 원점) 위치에 라벨."""
        return self.label(px, py, s, ax=self.ov, **kw)

    def text_extent_px(self, t):
        """텍스트 아티스트의 픽셀 경계(좌상단 원점) (x0,y0,x1,y1)."""
        r = self.fig.canvas.get_renderer()
        bb = t.get_window_extent(r)
        # figure 픽셀(좌하단 원점) → 좌상단 원점
        return bb.x0, self.H - bb.y1, bb.x1, self.H - bb.y0

    # ── 방위·축척 ──
    def north_arrow(self, margin=46, size=1.0):
        """우상단 방위표 — 맥락 지도(mapkit_context)와 같은 모양: 위에 N, 아래에 반흑반백 화살."""
        K = self.K
        cxp = self.W - margin * K - 26 * K * size
        top = margin * K + 40 * K * size                 # 'N' 자리를 위에 비운다
        h, wd = 120 * K * size, 46 * K * size
        ov = self.ov
        ov.add_patch(MPoly([[cxp, top], [cxp - wd / 2, top + h], [cxp, top + h * 0.72]], closed=True, fc=INK, ec=INK,
                           lw=self.pt(0.8), zorder=60))
        ov.add_patch(MPoly([[cxp, top], [cxp + wd / 2, top + h], [cxp, top + h * 0.72]], closed=True, fc="white",
                           ec=INK, lw=self.pt(0.8), zorder=60))
        self.label_px(cxp, top - 22 * K * size, "N", size=11, weight="bold", z=61)

    def scale_bar(self, length_m, ticks=None, margin=46, ends_only=False):
        """우하단 축척(흑백 교대 막대) — 맥락 지도와 같은 모양. length_m 은 전체 길이, ticks 는 분할 수.
        마지막 눈금 글자('… m')는 오른쪽 정렬이라, 분할 간격이 글자 폭보다 충분히 넓어야 겹치지 않는다."""
        K = self.K
        n = ticks or 2
        seg = length_m / n
        total_px = length_m * self.ppm
        x1 = self.W - margin * K
        x0 = x1 - total_px
        y_b = self.H - margin * K
        hh = 14 * K
        ov = self.ov
        for i in range(n):
            xa = x0 + i * seg * self.ppm
            ov.add_patch(Rectangle((xa, y_b - hh), seg * self.ppm, hh, fc=(INK if i % 2 == 0 else "white"), ec=INK,
                                   lw=self.pt(0.8), zorder=60))
        for i in range(n + 1):
            xa = x0 + i * seg * self.ppm
            s = f"{int(round(i * seg)):,}"
            last = i == n
            if last:
                s += " m"
            if ends_only and 0 < i < n:                  # 막대가 짧아 가운데 눈금 글자가 겹칠 때 양 끝 글자만
                continue
            self.label_px(xa + (4 * K if last else 0), y_b - hh - 22 * K, s, size=9.5, z=61, va="center",
                          ha="right" if last else "center")
        return (x0, y_b - hh - 48 * K, x1, y_b)

    # ── 범례(좌하단 반투명 흰 박스) ──
    def legend(self, items, title=None, margin=46, pad=20, sw_w=66, gap=16, loc="bl", alpha=0.9, text_size=9.5,
               xy=None, min_inner_w=0, col_gap=34, note=None, note_size=9.0):
        """items: dict 목록(위에서 아래로). 목록의 목록을 주면 왼쪽에서 오른쪽으로 단을 나눈다.
        - {'t':'patch','fc':..,'ec':..,'label':..,'lw':..,'hatch':..}
        - {'t':'line','color':..,'lw':..,'ls':..,'label':..}
        - {'t':'dot','color':..,'ec':..,'ms':..,'label':..}
        - {'t':'text','label':.., 'bold':bool, 'color':..}
        - {'t':'ramp','colors':[..],'labels':[..],'label':..,'note':..,'seg_w':..,'tick_labels':[..]}
              이산 단계 막대. tick_labels 를 주면 단계 경계(len = n-1)에 글자를 붙이고, 아니면 각 칸 아래 가운데에 labels.
        - {'t':'cbar','cmap':..., 'vmin','vmax','ticks':[..],'fmt':..,'label':..,'note':..,'bar_w':..}
        label 의 줄바꿈은 줄바꿈 문자. note: 맨 아래 가는 선 아래에 적는 보조 문구(회색, 맥락 지도와 같은 방식).
        글자 굵기는 맥락 지도와 같게 medium(머리글 semibold). 반환: 박스(px) 경계 (x0,y0,x1,y1).
        """
        K = self.K
        fs = self.pt(text_size)
        em = fs * DPI / 72                    # 글자 크기(px)
        lg = 1.14                             # 줄 간격(em)
        vpad = 0.46 * em                      # 항목 사이 여백
        sw_w_px, gap_px, pad_px = sw_w * K, gap * K, pad * K
        r = self.fig.canvas.get_renderer()

        def tw(s, bold=False):
            t = self.ov.text(0, 0, s, fontsize=fs, fontweight=("semibold" if bold else "medium"))
            bb = t.get_window_extent(r)
            t.remove()
            return bb.width

        def th(n):                            # n줄 글자 블록 높이
            return em * (1 + lg * (n - 1))

        def measure(col_items):
            rows = []                         # (item, height, width)
            for it in col_items:
                lines = it["label"].split("\n") if it.get("label") else []
                n = max(len(lines), 1)
                lw_ = max([tw(l, it.get("bold", False)) for l in lines] or [0])
                t = it["t"]
                if t in ("patch", "line", "dot"):
                    rows.append((it, max(th(n), 0.9 * em) + vpad, sw_w_px + gap_px + lw_))
                elif t == "text":
                    rows.append((it, th(n) + vpad, lw_))
                elif t in ("ramp", "cbar"):
                    note = it["note"].split("\n") if it.get("note") else []
                    h = th(len(lines)) + 0.4 * em + 0.8 * em + 0.35 * em + 1.0 * em + vpad
                    if note:
                        h += 0.2 * em + th(len(note))
                    if t == "ramp":
                        seg = it.get("seg_w", max(sw_w * 0.62, 52)) * K
                        bar_w = len(it["colors"]) * seg
                        if it.get("tick_labels"):
                            bar_w = max(bar_w, bar_w + 0.5 * tw(it["tick_labels"][-1]))
                    else:
                        bar_w = it.get("bar_w", 300) * K
                    wn = max([tw(l) for l in note] or [0])
                    rows.append((it, h, max(lw_, bar_w, wn)))
            return rows

        cols_items = items if (items and isinstance(items[0], list)) else [items]
        cols = [measure(c) for c in cols_items]
        col_w = [max([w for _, _, w in rows] + [0]) for rows in cols]
        col_h = [sum(h for _, h, _ in rows) for rows in cols]
        if len(cols) == 1:
            col_w[0] = max(col_w[0], min_inner_w * K)
        inner_w = sum(col_w) + col_gap * K * (len(cols) - 1)
        ttl_h = 0.0
        if title:
            ttl_h = th(1) + vpad
            inner_w = max(inner_w, tw(title, True))
        note_lines = note.split("\n") if note else []
        if note:
            inner_w = max(inner_w, max(tw(l) * note_size / text_size for l in note_lines))
        note_h = (0.5 * em + len(note_lines) * em * 1.18 * (note_size / text_size)) if note else 0.0
        bw = inner_w + 2 * pad_px
        bh = max(col_h) + ttl_h + note_h + 2 * pad_px - vpad * 0.6
        if xy is not None:
            x0, y0 = xy
        elif loc == "bl":
            x0, y0 = margin * K, self.H - margin * K - bh
        elif loc == "br":
            x0, y0 = self.W - margin * K - bw, self.H - margin * K - bh
        elif loc == "tl":
            x0, y0 = margin * K, margin * K
        else:
            x0, y0 = self.W - margin * K - bw, margin * K
        ov = self.ov
        ov.add_patch(Rectangle((x0, y0), bw, bh, fc="white", ec=LINE, lw=self.pt(0.9), alpha=alpha, zorder=55))
        if title:
            ov.text(x0 + pad_px, y0 + pad_px + em * 0.5, title, fontsize=fs, fontweight="semibold", color=INK,
                    va="center", ha="left", zorder=58)
        xcol = x0 + pad_px
        for ci, rows in enumerate(cols):
            y = y0 + pad_px + ttl_h
            for it, h, w in rows:
                t = it["t"]
                col = it.get("color", INK)
                lines = it["label"].split("\n") if it.get("label") else []
                bold = "semibold" if it.get("bold") else "medium"
                if t in ("patch", "line", "dot"):
                    cy = y + (h - vpad) / 2
                    x_sw = xcol
                    if t == "patch":
                        ov.add_patch(Rectangle((x_sw, cy - 0.42 * em), sw_w_px, 0.84 * em, fc=it.get("fc", "white"),
                                               ec=it.get("ec", INK2), lw=self.pt(it.get("lw", 0.7)),
                                               hatch=it.get("hatch"), ls=it.get("ls", "-"), zorder=58))
                    elif t == "line":
                        ov.plot([x_sw, x_sw + sw_w_px], [cy, cy], color=col, lw=self.pt(it.get("lw", 1.5)),
                                ls=it.get("ls", "-"), zorder=58, solid_capstyle=it.get("cap", "butt"),
                                dash_capstyle="butt")
                    else:
                        ov.plot([x_sw + sw_w_px / 2], [cy], marker=it.get("marker", "o"), ms=self.pt(it.get("ms", 6)),
                                mfc=it.get("fc", col), mec=it.get("ec", "white"), mew=self.pt(it.get("mew", 0.8)),
                                zorder=58, ls="none")
                    tx = x_sw + sw_w_px + gap_px
                    for k, l in enumerate(lines):
                        ov.text(tx, cy + (k - (len(lines) - 1) / 2) * em * lg, l, fontsize=fs, color=INK, va="center",
                                ha="left", zorder=58, fontweight=bold)
                elif t == "text":
                    cy = y + (h - vpad) / 2
                    for k, l in enumerate(lines):
                        ov.text(xcol, cy + (k - (len(lines) - 1) / 2) * em * lg, l, fontsize=fs,
                                color=it.get("color", INK), va="center", ha="left", zorder=58, fontweight=bold)
                else:  # ramp / cbar
                    xx0 = xcol
                    yy = y
                    for k, l in enumerate(lines):
                        ov.text(xx0, yy + em * 0.5 + k * em * lg, l, fontsize=fs, color=INK, va="center", ha="left",
                                zorder=58, fontweight=bold)
                    yy += th(len(lines)) + 0.4 * em
                    bar_h = 0.8 * em
                    if t == "cbar":
                        bar_w = it.get("bar_w", 300) * K
                        grad = np.linspace(0, 1, 256)[None, :]
                        ov.imshow(grad, extent=(xx0, xx0 + bar_w, yy + bar_h, yy), cmap=it["cmap"], aspect="auto",
                                  zorder=58, interpolation="bilinear")
                        ov.set_xlim(0, self.W)
                        ov.set_ylim(self.H, 0)
                        for tv in it["ticks"]:
                            fx = (tv - it["vmin"]) / (it["vmax"] - it["vmin"])
                            xt = xx0 + fx * bar_w
                            ov.plot([xt, xt], [yy + bar_h, yy + bar_h + 0.22 * em], color=INK2, lw=self.pt(0.7),
                                    zorder=59)
                            ov.text(xt, yy + bar_h + 0.35 * em + 0.5 * em, it.get("fmt", "{:g}").format(tv),
                                    fontsize=fs, color=INK, va="center", ha="center", zorder=58, fontweight="medium")
                    else:
                        cols_, labs = it["colors"], it.get("labels", [])
                        seg_w = it.get("seg_w", max(sw_w * 0.62, 52)) * K
                        for k, c in enumerate(cols_):
                            xx = xx0 + k * seg_w
                            ov.add_patch(Rectangle((xx, yy), seg_w, bar_h, fc=c, ec="white", lw=self.pt(0.8),
                                                   zorder=58))
                            if labs and not it.get("tick_labels"):
                                ov.text(xx + seg_w / 2, yy + bar_h + 0.35 * em + 0.5 * em, labs[k], fontsize=fs,
                                        color=INK, va="center", ha="center", zorder=58, fontweight="medium")
                        if it.get("tick_labels"):
                            for k, lb in enumerate(it["tick_labels"]):
                                xb = xx0 + (k + 1) * seg_w
                                ov.plot([xb, xb], [yy + bar_h, yy + bar_h + 0.22 * em], color=INK2, lw=self.pt(0.7),
                                        zorder=59)
                                ov.text(xb, yy + bar_h + 0.35 * em + 0.5 * em, lb, fontsize=fs, color=INK,
                                        va="center", ha="center", zorder=58, fontweight="medium")
                    yy += bar_h + 0.35 * em + 1.0 * em
                    if it.get("note"):
                        nl = it["note"].split("\n")
                        yy += 0.2 * em
                        for k, l in enumerate(nl):
                            ov.text(xx0, yy + em * 0.5 + k * em * lg, l, fontsize=fs,
                                    color=it.get("note_color", INK2), va="center", ha="left", zorder=58, fontweight="medium")
                y += h
            xcol += col_w[ci] + col_gap * K
        if note:
            yn = y0 + pad_px + ttl_h + max(col_h) - vpad * 0.3
            ov.plot([x0 + pad_px, x0 + bw - pad_px], [yn + 0.12 * em, yn + 0.12 * em], color=LINE, lw=self.pt(0.7),
                    zorder=58)
            for k, l in enumerate(note_lines):
                ov.text(x0 + pad_px, yn + 0.5 * em + (k + 0.5) * em * 1.18 * (note_size / text_size), l,
                        fontsize=self.pt(note_size), color=GRAY, va="center", ha="left", zorder=58, fontweight="regular")
        return (x0, y0, x0 + bw, y0 + bh)

    def save(self, path):
        """PNG 저장. 흰 바탕 불투명(RGB, 알파 없음), 300dpi 메타데이터."""
        from PIL import Image
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.fig.savefig(path, dpi=DPI, facecolor="white")
        plt.close(self.fig)
        im = Image.open(path)
        if im.size != (self.W, self.H):
            raise RuntimeError(f"크기 불일치 {im.size} != {(self.W, self.H)}")
        im.convert("RGB").save(path, dpi=(DPI, DPI), optimize=True)
        return path


# ── 기타 도구 ───────────────────────────────────────────────────────
def rgb_ramp(c0, c1, n):
    """sRGB 두 색 사이를 RGB 에서 등간격 n 단계로 보간한 16진 색 목록."""
    a = np.array([int(c0[i:i + 2], 16) for i in (1, 3, 5)], float)
    b = np.array([int(c1[i:i + 2], 16) for i in (1, 3, 5)], float)
    return ["#" + "".join(f"{int(round(v)):02X}" for v in (a + (b - a) * t)) for t in np.linspace(0, 1, n)]


def fmt_int(v):
    return f"{int(round(v)):,}"
