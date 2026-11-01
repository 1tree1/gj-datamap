# -*- coding: utf-8 -*-
"""발표 슬라이드용 맥락 지도 공통 도구 (M1 경주시 · M2 원도심 · M3 부지~자산 거리 · M7 경계 · M9 철도축).

- 모든 공간 자료는 읽자마자 EPSG:5187(Korea 2000 동부원점)로 옮긴다. 원본은 건드리지 않는다.
- 스타일(다른 분석 지도와 한 덱에 놓임): 흰 바탕 · 건물 단색 · 하천 #BFD7EA · 대상지 경계 #D7191C 2.6pt · Pretendard · 제목 없음 · 출처 줄 없음
  범례 좌하단(반투명 흰 박스) · 방위표 우상단 · 축척 우하단.
- 크기 규칙: 그림 폭 6in로 슬라이드에 놓였을 때 본문 라벨 9pt 이상.
  figsize = (W/300, H/300)in, dpi 300. 글자·선 굵기에 K = W/1800 을 곱한다(슬라이드 pt × K = 그림 안 pt).
  예) W=1800 → 9pt = 그림 안 9pt, W=2000 → 9pt = 그림 안 10pt(라벨 글자 높이 약 30px).
- 실행 전 `export PYTHONUTF8=1 PYTHONIOENCODING=utf-8`. 필요 패키지: numpy · matplotlib · shapely 2.x · pyproj · pyshp(`import shapefile`) · Pillow.
- 무거운 읽기(수치지도·시 전역 용도지역)는 환경변수 MAPKIT_CACHE 폴더에 pickle로 저장해 다시 쓴다(없으면 캐시 안 씀).
- 한꺼번에 다시 만들기: `python run_context_maps.py` (M1·M2·M3·M3 대안·M7·M9, MANIFEST_context.csv, research/context_maps_checks.csv).
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import pickle
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import PathPatch, Polygon as MPoly, Rectangle
from matplotlib.path import Path as MPath

import shapely
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon, box, shape
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points, unary_union
from shapely.strtree import STRtree
from pyproj import Transformer

warnings.filterwarnings("ignore")
import logging
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)     # 글리프 대체 글꼴(Malgun) 가중치 안내문 숨김

# ── 경로 ─────────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
PRJ = HERE.parent                                  # work/20261008_presentation_front
ROOT = PRJ.parent.parent                           # 9_도시
OUT = PRJ / "assets" / "maps"
RESEARCH = PRJ / "research"
PROC = ROOT / "archive" / "C_data" / "processed"
RAW = ROOT / "archive" / "C_data" / "raw"
NGII = ROOT / "대지" / "(B020)연속수치지도_202609132098"
PLAN_BOUNDARY = ROOT / "work" / "20261005_boundary_check" / "user_boundary_current_5187.geojson"
CACHE = Path(os.environ["MAPKIT_CACHE"]) if os.environ.get("MAPKIT_CACHE") else None
for _d in (OUT, RESEARCH):
    _d.mkdir(parents=True, exist_ok=True)
if CACHE:
    CACHE.mkdir(parents=True, exist_ok=True)

# ── 색(지도 공통 스타일) ───────────────────────────────────────────────────────
INK, INK2, GRAY, LINE, TINT = "#231F20", "#4D4D4D", "#6D6E71", "#D1D3D4", "#F5F7FA"
RED, BLUE = "#D7191C", "#1F5AA6"
C_WATER, C_GREEN, C_ROAD = "#BFD7EA", "#CFE3B8", "#C8C8C8"
C_CITY_FILL, C_CITY_LINE = "#F4F4F4", "#BDBDBD"
C_BUILT = "#8C8C8C"                                 # M1 건물이 모인 땅(주거·상업·공업 용도지역)
C_HER_CITY = "#D9CCEA"                              # M1 문화유산 구역·보존지역
C_HER_CORE = "#E1D8F0"                              # M2·M3 문화유산 구역·보존지역(투명도 0.85)
C_RAIL = "#4D4D4D"
C_BLD1 = "#DADADA"                                  # 단색 건물(M3·M7)
C_FLOOR = {"1": "#E6E2D8", "2": "#CFC8B8", "3-4": "#9C9482", "5+": "#4D4D4D"}   # M2 층수 4단계

# ── 글꼴 ─────────────────────────────────────────────────────────────────────
_FONT_DIR = Path("C:/Users/OFFICE/AppData/Local/Microsoft/Windows/Fonts")
FONT_FAMILY = "Malgun Gothic"


def setup_fonts():
    """Pretendard를 등록한다(없으면 Malgun Gothic). ㎡ 같은 기호는 Malgun Gothic으로 대체되도록 목록으로 지정."""
    global FONT_FAMILY
    ok = False
    for w in ("Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold"):
        p = _FONT_DIR / f"Pretendard-{w}.otf"
        if p.exists():
            fm.fontManager.addfont(str(p))
            ok = True
    for p in ("C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/malgunbd.ttf"):
        if os.path.exists(p):
            fm.fontManager.addfont(p)
    FONT_FAMILY = "Pretendard" if ok else "Malgun Gothic"
    plt.rcParams["font.family"] = [FONT_FAMILY, "Malgun Gothic"]
    plt.rcParams["axes.unicode_minus"] = False
    # 글꼴 대체 경고를 숨겼으므로(아래 logging 설정) 실제로 쓰일 파일을 한 번 확인한다
    for wt in (400, 500, 600, 700):
        try:
            fp = fm.findfont(fm.FontProperties(family=FONT_FAMILY, weight=wt), fallback_to_default=False)
            FONT_FILES[wt] = Path(fp).name
        except Exception as e:                      # 글꼴이 없으면 조용히 대체되지 않게 바로 알린다
            raise RuntimeError(f"{FONT_FAMILY} 가중치 {wt} 글꼴을 찾지 못했다: {e}")
    return FONT_FAMILY


FONT_FILES = {}
setup_fonts()

# ── 좌표 변환 ─────────────────────────────────────────────────────────────────
T_5179 = Transformer.from_crs("EPSG:5179", "EPSG:5187", always_xy=True)
T_4326 = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True)


def _tf(T):
    def f(a):
        a = np.asarray(a, float)
        x, y = T.transform(a[:, 0], a[:, 1])
        return np.column_stack([x, y])
    return f


def to5187(geom, T=T_5179):
    """shapely 도형 또는 도형 배열의 좌표를 EPSG:5187로 옮긴다."""
    return shapely.transform(geom, _tf(T), include_z=False)


def ll_to_5187(geom):
    return to5187(geom, T_4326)


def gj(path):
    return json.load(open(path, encoding="utf-8"))


def _clean(g):
    """면 도형은 buffer(0)으로 위상 오류를 정리하고, 점·선은 그대로 둔다."""
    return g.buffer(0) if g.geom_type in ("Polygon", "MultiPolygon") else g


def _cached(key, fn):
    """MAPKIT_CACHE가 있으면 pickle 캐시를 쓴다. key에 원자료 수정시각을 섞어 오래된 캐시를 피한다."""
    if CACHE is None:
        return fn()
    p = CACHE / (hashlib.md5(key.encode("utf-8")).hexdigest() + ".pkl")
    if p.exists():
        return pickle.load(open(p, "rb"))
    v = fn()
    pickle.dump(v, open(p, "wb"), protocol=4)
    return v


# ── 도형 순회·그리기 ───────────────────────────────────────────────────────────
def iter_polys(g):
    if g is None or g.is_empty:
        return
    if g.geom_type == "Polygon":
        yield g
    elif g.geom_type in ("MultiPolygon", "GeometryCollection"):
        for s in g.geoms:
            yield from iter_polys(s)


def iter_lines(g):
    if g is None or g.is_empty:
        return
    if g.geom_type == "LineString":
        yield g
    elif g.geom_type == "LinearRing":
        yield LineString(g.coords)
    elif g.geom_type in ("MultiLineString", "GeometryCollection"):
        for s in g.geoms:
            yield from iter_lines(s)


def _poly_path(p: Polygon) -> MPath:
    p = orient(p, 1.0)
    verts, codes = [], []
    for r in [p.exterior, *p.interiors]:
        c = np.asarray(r.coords)[:, :2]
        if len(c) < 4:
            continue
        verts.append(c)
        codes.append([MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY])
    return MPath(np.concatenate(verts), np.concatenate(codes))


def draw_poly(ax, geom, fc="none", ec="none", lw=0.0, alpha=1.0, z=2, ls="-", **kw):
    """(Multi)Polygon을 구멍까지 정확히 칠한다."""
    for p in iter_polys(geom):
        if p.exterior is None or len(p.exterior.coords) < 4:
            continue
        ax.add_patch(PathPatch(_poly_path(p), facecolor=fc, edgecolor=ec, linewidth=lw, alpha=alpha, zorder=z,
                               linestyle=ls, joinstyle="round", **kw))


def draw_polys_fast(ax, geoms, fc, ec="none", lw=0.0, z=1, alpha=1.0):
    """건물처럼 개수가 많은 도형(바깥 고리만) — PolyCollection."""
    rings = [np.asarray(p.exterior.coords)[:, :2] for g in geoms for p in iter_polys(g)]
    if rings:
        ax.add_collection(PolyCollection(rings, facecolors=fc, edgecolors=ec, linewidths=lw, zorder=z, alpha=alpha,
                                         antialiaseds=True))


def draw_lines(ax, geoms, color, lw, z=2, alpha=1.0, ls="-", cap="butt"):
    segs = [np.asarray(l.coords)[:, :2] for g in geoms for l in iter_lines(g)]
    if segs:
        ax.add_collection(LineCollection(segs, colors=color, linewidths=lw, zorder=z, alpha=alpha, linestyles=ls,
                                         capstyle=cap, joinstyle="round"))


def draw_outline(ax, geom, color, lw, z=5, ls="-", alpha=1.0):
    for p in iter_polys(geom):
        for r in [p.exterior, *p.interiors]:
            x, y = r.xy
            ax.plot(x, y, color=color, lw=lw, zorder=z, ls=ls, alpha=alpha, solid_joinstyle="round",
                    solid_capstyle="round")


def hatch_lines(poly, spacing, angle_deg=45.0):
    """다각형 안을 angle_deg 방향 평행선(간격 spacing, m)으로 채운 선분 모음(해칭)."""
    if poly is None or poly.is_empty:
        return []
    minx, miny, maxx, maxy = poly.bounds
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    R = math.hypot(maxx - minx, maxy - miny) / 2 + spacing
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)          # 선 방향
    nx, ny = -uy, ux                           # 법선(선끼리 벌어지는 방향)
    n = int(R / spacing) + 1
    out = []
    for k in range(-n, n + 1):
        ox, oy = cx + nx * spacing * k, cy + ny * spacing * k
        seg = LineString([(ox - ux * R, oy - uy * R), (ox + ux * R, oy + uy * R)])
        c = poly.intersection(seg)
        out.extend(iter_lines(c))
    return out


# ── 수치지도(NGII) ─────────────────────────────────────────────────────────────
def _fix_text(v):
    """수치지도 DBF 문자열은 cp949 바이트가 latin-1로 읽혀 UTF-8로 저장된 이중 인코딩이다."""
    if isinstance(v, str):
        try:
            return v.encode("latin-1").decode("cp949").strip()
        except Exception:
            return v.strip()
    return v


_NGII_MEM: dict = {}


def read_ngii(layer):
    """NGII 레이어 → [(도형(5187), 속성 dict)]."""
    if layer in _NGII_MEM:
        return _NGII_MEM[layer]

    def _read():
        import shapefile                              # pyshp
        r = shapefile.Reader(str(NGII / layer))
        flds = [f[0] for f in r.fields[1:]]
        geoms, attrs = [], []
        for s in r.iterShapeRecords():
            geoms.append(shape(s.shape.__geo_interface__))
            attrs.append({k: _fix_text(v) for k, v in zip(flds, s.record)})
        g5187 = to5187(np.array(geoms, dtype=object))
        return list(zip(list(g5187), attrs))

    out = _cached(f"ngii:{layer}:{(NGII / (layer + '.shp')).stat().st_mtime}", _read)
    _NGII_MEM[layer] = out
    return out


def floor_class(n):
    n = int(n or 1) or 1
    return "1" if n <= 1 else "2" if n == 2 else "3-4" if n <= 4 else "5+"


def buildings_in(win):
    """win(shapely 사각형) 안에 닿는 건물 [(도형, 층수)]. 층수가 비면 1층으로 센다(기존 분석과 같음)."""
    b = read_ngii("N3A_B0010000")
    geoms = [g for g, _ in b]
    tree = STRtree(geoms)
    idx = sorted(tree.query(win, predicate="intersects"))
    out = []
    for i in idx:
        g, a = b[i]
        try:
            fl = int(a.get("nmly") or 1) or 1
        except Exception:
            fl = 1
        out.append((g, fl))
    return out


def water_in(win):
    """하천 면(N3A_E0010001, 15개)."""
    return [g for g, _ in read_ngii("N3A_E0010001") if g.intersects(win)]


def ngii_names(layer="N3P_H0040000"):
    """지명 주기 점 → {이름: [Point...]}."""
    d = defaultdict(list)
    for g, a in read_ngii(layer):
        d[a.get("name", "")].append(g)
    return d


# ── 경주시 전역 자료(S3) ───────────────────────────────────────────────────────
def load_city():
    """(읍면동 [(이름, 도형)], 시 경계 도형) — V-World 읍면동 56개 합집합."""
    def _r():
        feats = gj(RAW / "vworld_emd_gj.geojson")["features"]
        emd = [(f["properties"]["emd_kor_nm"], _clean(ll_to_5187(shape(f["geometry"])))) for f in feats]
        city = unary_union([g for _, g in emd]).buffer(0)
        return emd, city
    return _cached("city:emd", _r)


def load_zoning():
    """경주시 용도지역(V-World LT_C_UQ111) — 주거·상업·공업·녹지로 묶은 합집합(시 경계로 자름)."""
    def _r():
        emd, city = load_city()
        uq = [f for f in gj(RAW / "vworld_uq111_city.geojson")["features"] if f["properties"].get("sigg_name") == "경주시"]
        grp = defaultdict(list)
        for f in uq:
            n = f["properties"]["uname"]
            k = "주거" if "주거" in n else "상업" if "상업" in n else "공업" if "공업" in n else "녹지" if "녹지" in n else "기타"
            grp[k].append(_clean(ll_to_5187(shape(f["geometry"]))))
        by = {k: unary_union(v).intersection(city) for k, v in grp.items()}
        built = unary_union([by.get("주거"), by.get("상업"), by.get("공업")]).intersection(city)
        return {"by": by, "built": built, "n": len(uq)}
    return _cached("zoning:uq111", _r)


def load_heritage():
    """경주시 문화유산 보호 구역(V-World LT_C_UO301) — 전체 합집합·국가지정 합집합(시 경계로 자름)."""
    def _r():
        emd, city = load_city()
        uo = [f for f in gj(RAW / "vworld_uo301_city.geojson")["features"] if f["properties"].get("sigg_name") == "경주시"]
        allg = [(_clean(ll_to_5187(shape(f["geometry"]))), f["properties"]["uname"]) for f in uo]
        her = unary_union([g for g, _ in allg]).intersection(city)
        nat = unary_union([g for g, n in allg if n == "국가지정문화재구역"]).intersection(city)
        return {"all": her, "nat": nat, "parts": allg, "n": len(uo)}
    return _cached("heritage:uo301", _r)


def load_rails():
    """OSM 철도(T4) — 운행선·폐선 선분, 역 점. 모두 5187."""
    def _r():
        act = [ll_to_5187(shape(f["geometry"])) for f in gj(PROC / "rail_active_4326.geojson")["features"]]
        aban = [(ll_to_5187(shape(f["geometry"])), f["properties"]) for f in gj(PROC / "rail_abandoned_4326.geojson")["features"]]
        act_p = [f["properties"] for f in gj(PROC / "rail_active_4326.geojson")["features"]]
        st = [(ll_to_5187(shape(f["geometry"])), f["properties"]) for f in gj(PROC / "rail_stations_4326.geojson")["features"]]
        gw = {f["properties"]["name"]: ll_to_5187(shape(f["geometry"])) for f in gj(PROC / "gateways_4326.geojson")["features"]}
        return {"active": act, "active_props": act_p, "abandoned": [g for g, _ in aban], "abandoned_props": [p for _, p in aban],
                "stations": st, "gateways": gw}
    return _cached("rails:osm", _r)


def load_tour():
    """경주시 관광지 현황 점 {이름: Point(5187)} (T2, 주소 지오코딩 — 넓은 유적은 빗나감)."""
    return {f["properties"]["name"].strip(): ll_to_5187(shape(f["geometry"]))
            for f in gj(RAW / "gj_tour_sites.geojson")["features"] if f.get("geometry")}


# ── 대상지 자료(S1) ───────────────────────────────────────────────────────────
def plan_boundary():
    """본 계획 경계 218,478㎡(사용자 라이노 경계, EPSG:5187)."""
    return _clean(shape(gj(PLAN_BOUNDARY)["features"][0]["geometry"]))


def gosi_zone():
    """고시 2026-8호 구역 — 지형도면 추출 도형(158,472㎡). 결정조서 면적은 156,460㎡."""
    return _clean(shape(gj(PROC / "gosi2026-8_zone_5187.geojson")["features"][0]["geometry"]))


GOSI_AREA_M2 = 156460                  # 결정조서(T1)
PLAN_AREA_M2 = 218478                  # 본 계획 경계
SIGU_AREA_M2 = 79438                   # 시 구상 면적(범위 미정의, 언론 경유 T4)
OLD_STATION_OSM = (219649.2, 360746.0)  # OSM '구경주역' 점(T4) — 이웃 거리표(한눈에_v1 §3.3)의 기준점
WALK_M_PER_MIN = 4000 / 60             # 걷기 시속 4 km 가정


# ── 그림틀 ───────────────────────────────────────────────────────────────────
DPI = 300
HALO_PX = 3.0
HALF_PAD = 5.0                        # 라벨 상자 여유(px)                          # 글자 흰 외곽 3px


class Frame:
    """W×H px(300dpi) 흰 바탕 그림 + 실좌표 축 + 픽셀 오버레이(좌상단 원점).

    K = W/1800 : 슬라이드 pt(그림 폭 6in 기준) → 그림 안 pt 환산 계수.
    """

    def __init__(self, W, H, cx, cy, w_m, name=""):
        self.W, self.H, self.name = W, H, name
        self.K = W / 1800.0
        self.w_m = w_m
        self.h_m = w_m * H / W
        self.cx, self.cy = cx, cy
        self.fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor="white")
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(cx - self.w_m / 2, cx + self.w_m / 2)
        self.ax.set_ylim(cy - self.h_m / 2, cy + self.h_m / 2)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.ov = self.fig.add_axes([0, 0, 1, 1], facecolor="none")
        self.ov.set_xlim(0, W)
        self.ov.set_ylim(H, 0)
        self.ov.axis("off")
        self.ov.set_zorder(50)
        self.ppm = W / self.w_m                       # px per meter
        self.win = box(cx - self.w_m / 2, cy - self.h_m / 2, cx + self.w_m / 2, cy + self.h_m / 2)
        self.labels = []                              # (key, Text) — 겹침 점검용
        self.boxes = {}                               # 범례·축척·방위표 경계(px, 좌상단 원점)

    # 슬라이드 pt → 그림 안 pt, 슬라이드 px(1800 기준) → 그림 px
    def pt(self, x):
        return x * self.K

    def px(self, x):
        return x * self.K

    def to_px(self, x, y):
        return (x - (self.cx - self.w_m / 2)) * self.ppm, ((self.cy + self.h_m / 2) - y) * self.ppm

    def from_px(self, px, py):
        return (self.cx - self.w_m / 2) + px / self.ppm, (self.cy + self.h_m / 2) - py / self.ppm

    # ── 글자 ──
    def label(self, x, y, s, size=9.5, color=INK, weight="medium", ha="center", va="center", rot=0.0, z=30, halo=True,
              dx=0.0, dy=0.0, key=None, linespacing=1.18, check=True):
        """실좌표 (x,y)에 라벨. dx·dy는 그림 px 오프셋(오른쪽·위가 +). 흰 외곽 3px."""
        pt = 72.0 / DPI
        t = self.ax.annotate(s, xy=(x, y), xytext=(dx * pt, dy * pt), textcoords="offset points",
                             fontsize=self.pt(size), color=color, fontweight=weight, ha=ha, va=va, rotation=rot,
                             multialignment={"left": "left", "right": "right"}.get(ha, "center"),
                             zorder=z, linespacing=linespacing, annotation_clip=False)
        if halo:
            t.set_path_effects([pe.withStroke(linewidth=HALO_PX * 2 * 72 / DPI, foreground="white", capstyle="round",
                                              joinstyle="round")])
        if check:
            self.labels.append((key or s.replace("\n", " "), t))
        return t

    def label_px(self, px, py, s, size=9.5, color=INK, weight="medium", ha="center", va="center", rot=0.0, z=61,
                 halo=True, key=None, check=True):
        """픽셀 오버레이(좌상단 원점) 위치에 라벨."""
        t = self.ov.text(px, py, s, fontsize=self.pt(size), color=color, fontweight=weight, ha=ha, va=va, rotation=rot,
                         zorder=z)
        if halo:
            t.set_path_effects([pe.withStroke(linewidth=HALO_PX * 2 * 72 / DPI, foreground="white", capstyle="round",
                                              joinstyle="round")])
        if check:
            self.labels.append((key or s.replace("\n", " "), t))
        return t

    # ── 방위표(우상단) ──
    def north_arrow(self, margin=46, size=1.0):
        K = self.K
        cxp = self.W - margin * K - 26 * K * size
        top = margin * K + 40 * K * size                 # 'N'이 들어갈 자리를 위에 비운다
        h, wd = 120 * K * size, 46 * K * size
        ov = self.ov
        ov.add_patch(MPoly([[cxp, top], [cxp - wd / 2, top + h], [cxp, top + h * 0.72]], closed=True, fc=INK, ec=INK,
                           lw=self.pt(0.8), zorder=60))
        ov.add_patch(MPoly([[cxp, top], [cxp + wd / 2, top + h], [cxp, top + h * 0.72]], closed=True, fc="white", ec=INK,
                           lw=self.pt(0.8), zorder=60))
        self.label_px(cxp, top - 22 * K * size, "N", size=11, weight="bold", z=61, key="N")
        self.boxes["north"] = (cxp - wd / 2 - 8 * K, margin * K - 4 * K, cxp + wd / 2 + 8 * K, top + h + 4 * K)

    # ── 축척(우하단) ──
    def scale_bar(self, length_m, nseg=2, unit="m", div=1.0, margin=46):
        """우하단 흑백 교대 막대. length_m = 전체 길이, unit/div로 숫자 표기(예: km → div=1000)."""
        K = self.K
        seg = length_m / nseg
        total = length_m * self.ppm
        x1 = self.W - margin * K
        x0 = x1 - total
        yb = self.H - margin * K
        hh = 14 * K
        for i in range(nseg):
            xa = x0 + i * seg * self.ppm
            self.ov.add_patch(Rectangle((xa, yb - hh), seg * self.ppm, hh, fc=(INK if i % 2 == 0 else "white"), ec=INK,
                                        lw=self.pt(0.8), zorder=60))
        for i in range(nseg + 1):
            xa = x0 + i * seg * self.ppm
            v = i * seg / div
            s = (f"{v:g}" if v != int(v) else f"{int(v):,}") + (f" {unit}" if i == nseg else "")
            last = i == nseg
            self.label_px(xa + (4 * K if last else 0), yb - hh - 22 * K, s, size=9.5, z=61, key=f"scale:{s}",
                          ha="right" if last else "center")
        self.boxes["scale"] = (x0 - 30 * K, yb - hh - 48 * K, x1 + 10 * K, yb + 4 * K)

    # ── 범례(좌하단 반투명 흰 박스) ──
    def legend(self, items, margin=46, pad=20, sw_w=66, gap=16, col_gap=44, text_size=9.5, row_gap=0.42, alpha=0.9,
               note=None, note_size=9.0, xy=None):
        """items: dict 목록(위에서 아래로). 목록의 목록이면 열 여러 개로 늘어놓는다.
        - {'t':'patch','fc','ec','lw','alpha','hatch':bool,'hc','label'}  면 견본
        - {'t':'line','color','lw','ls','cap','label'}                    선 견본
        - {'t':'dot','color','ec','ms','marker','label'}                  점 견본
        - {'t':'ramp','items':[(색,글)...],'label':'머리글'}              칸 여러 개(건물 층수) — 칸 아래에 글
        note: 맨 아래 가는 선 아래에 적는 보조 문구.
        박스는 좌하단(좌상단 원점 px)에 놓는다. 반환: (x0,y0,x1,y1)
        """
        K = self.K
        fs = self.pt(text_size)
        em = fs * DPI / 72
        rh = em * (1.0 + row_gap)
        sw, gp, pd = sw_w * K, gap * K, pad * K
        r = self.fig.canvas.get_renderer()

        def tw(s, weight="medium", size=fs):
            t = self.ov.text(0, 0, s, fontsize=size, fontweight=weight)
            w = t.get_window_extent(r).width
            t.remove()
            return w

        def measure(it):
            if it["t"] == "ramp":
                cw = [max(0.95 * em, tw(lb) + 0.5 * em) for _, lb in it["items"]]
                head = rh if it.get("label") else 0
                return head + 0.9 * em + rh * 0.95, max(sum(cw), tw(it.get("label", ""), "semibold") if it.get("label") else 0), cw
            lines = it["label"].split("\n")
            return rh * (1 + 0.8 * (len(lines) - 1)), sw + gp + max(tw(l, it.get("weight", "medium")) for l in lines), None

        cols = items if (items and isinstance(items[0], list)) else [items]
        meas = [[(it, *measure(it)) for it in col] for col in cols]
        cw_ = [max(w for _, _, w, _ in col) for col in meas]
        ch_ = [sum(h for _, h, _, _ in col) for col in meas]
        note_lines = note.split("\n") if note else []
        inner_w = sum(cw_) + col_gap * (len(cols) - 1)
        if note:
            inner_w = max(inner_w, max(tw(l, "regular", self.pt(note_size)) for l in note_lines))
        note_h = (0.5 * em + len(note_lines) * em * 1.18 * (note_size / text_size)) if note else 0
        bw = inner_w + 2 * pd
        bh = max(ch_) + note_h + 2 * pd - rh * row_gap * 0.5
        x0, y0 = (margin * K, self.H - margin * K - bh) if xy is None else xy
        ov = self.ov
        ov.add_patch(Rectangle((x0, y0), bw, bh, fc="white", ec=LINE, lw=self.pt(0.9), alpha=alpha, zorder=55))
        xc = x0 + pd
        for ci, col in enumerate(meas):
            y = y0 + pd
            for it, h, w, cwl in col:
                t = it["t"]
                colr = it.get("color", INK)
                if t == "ramp":
                    yy = y
                    if it.get("label"):
                        ov.text(xc, yy + rh * 0.5, it["label"], fontsize=fs, fontweight="semibold", color=INK, va="center",
                                ha="left", zorder=58)
                        yy += rh
                    xx = xc
                    for (c, lb), cwi in zip(it["items"], cwl):
                        ov.add_patch(Rectangle((xx, yy), cwi, 0.9 * em, fc=c, ec=it.get("ec", "none"), lw=self.pt(0.6), zorder=58))
                        ov.text(xx + cwi / 2, yy + 0.9 * em + rh * 0.5, lb, fontsize=fs, color=INK, va="center", ha="center",
                                zorder=58, fontweight="medium")
                        xx += cwi
                    y += h
                    continue
                lines = it["label"].split("\n")
                cy = y + h * 0.5
                if t == "patch":
                    ph = 0.84 * em
                    if it.get("hatch"):
                        ov.add_patch(Rectangle((xc, cy - ph / 2), sw, ph, fc=it.get("fc", "none"), ec="none",
                                               alpha=it.get("alpha", 1.0), zorder=58))
                        clip = Rectangle((xc, cy - ph / 2), sw, ph, transform=ov.transData)
                        step = 0.26 * em
                        for k in range(-6, int(sw / step) + 8):
                            xa = xc + k * step
                            ln, = ov.plot([xa, xa + ph], [cy + ph / 2, cy - ph / 2], color=it.get("hc", RED), lw=self.pt(0.7),
                                          zorder=59, solid_capstyle="butt")
                            ln.set_clip_path(clip)
                        ov.add_patch(Rectangle((xc, cy - ph / 2), sw, ph, fc="none", ec=it.get("ec", "none"),
                                               lw=self.pt(it.get("lw", 0.7)), zorder=60))
                    else:
                        ov.add_patch(Rectangle((xc, cy - ph / 2), sw, ph, fc=it.get("fc", "white"), ec=it.get("ec", "none"),
                                               lw=self.pt(it.get("lw", 0.7)), alpha=it.get("alpha", 1.0), zorder=58))
                elif t == "line":
                    ov.plot([xc, xc + sw], [cy, cy], color=colr, lw=self.pt(it.get("lw", 1.5)), ls=it.get("ls", "-"),
                            zorder=58, solid_capstyle=it.get("cap", "butt"), dash_capstyle=it.get("cap", "butt"))
                elif t == "dot":
                    ov.plot([xc + sw / 2], [cy], marker=it.get("marker", "o"), ms=self.pt(it.get("ms", 7)), mfc=it.get("fc", colr),
                            mec=it.get("ec", "white"), mew=self.pt(it.get("mew", 0.9)), zorder=58, ls="none")
                for k, l in enumerate(lines):
                    ov.text(xc + sw + gp, cy + (k - (len(lines) - 1) / 2) * em * 1.18, l, fontsize=fs, color=INK, va="center",
                            ha="left", zorder=58, fontweight=it.get("weight", "medium"))
                y += h
            xc += cw_[ci] + col_gap
        if note:
            yn = y0 + pd + max(ch_)
            ov.plot([x0 + pd, x0 + bw - pd], [yn + 0.12 * em, yn + 0.12 * em], color=LINE, lw=self.pt(0.7), zorder=58)
            for k, l in enumerate(note_lines):
                ov.text(x0 + pd, yn + 0.5 * em + (k + 0.5) * em * 1.18 * (note_size / text_size), l, fontsize=self.pt(note_size),
                        color=GRAY, va="center", ha="left", zorder=58, fontweight="regular")
        self.boxes["legend"] = (x0, y0, x0 + bw, y0 + bh)
        return self.boxes["legend"]

    def label_box(self, t, pad=3.0):
        """그려진 라벨의 경계 상자(px, 좌상단 원점)."""
        self.fig.canvas.draw()
        bb = t.get_window_extent(self.fig.canvas.get_renderer())
        return (bb.x0 - pad, self.H - bb.y1 - pad, bb.x1 + pad, self.H - bb.y0 + pad)

    # ── 라벨 자동 배치(점 라벨이 선·점·범례와 겹치지 않게) ──
    def text_size_px(self, s, size=10, weight="semibold", linespacing=1.18):
        """라벨 글상자의 폭·높이(px, 흰 외곽 포함)."""
        r = self.fig.canvas.get_renderer()
        t = self.ov.text(0, 0, s, fontsize=self.pt(size), fontweight=weight, linespacing=linespacing)
        bb = t.get_window_extent(r)
        t.remove()
        return bb.width + 2 * HALF_PAD, bb.height + 2 * HALF_PAD

    def auto_place(self, labels, lines=(), soft_lines=(), mid_lines=(), dots=(), boxes=(), radii=(20, 46, 90), n_dir=16, restarts=24, seed=7,
                   margin=16):
        """점 라벨 자동 배치.
        labels: [dict(key, text, anchor=(x,y) 실좌표, size, weight, linespacing)] — 점(앵커)에서 radii px 떨어진 16방향 후보 중 고른다.
        lines: 라벨이 가리면 안 되는 선분 [((x0,y0),(x1,y1)) px] · mid_lines: 웬만하면 피할 선(대상지 경계) · soft_lines: 가려도 덜 아쉬운 선(원) ·
        dots: 가리면 안 되는 점 [(x,y,반지름px)] · boxes: 들어가면 안 되는 상자 [(x0,y0,x1,y1) px, 좌상단 원점].
        반환: {key: dict(dx, dy, ha, va, box, r, leader)} — dx·dy는 label()에 그대로 넣는 오프셋(px, 위·오른쪽 +).
        """
        import random
        rng = random.Random(seed)
        info = []
        for lb in labels:
            w, h = self.text_size_px(lb["text"], lb.get("size", 10), lb.get("weight", "semibold"), lb.get("linespacing", 1.12))
            ax_, ay_ = self.to_px(*lb["anchor"])
            cands = []
            for r in radii:
                for k in range(n_dir):
                    th = 2 * math.pi * k / n_dir
                    c, sn = math.cos(th), math.sin(th)
                    ha = "left" if c > 0.3 else "right" if c < -0.3 else "center"
                    va = "bottom" if sn > 0.3 else "top" if sn < -0.3 else "center"
                    px_, py_ = ax_ + r * c, ay_ - r * sn
                    x0 = px_ - (0 if ha == "left" else w if ha == "right" else w / 2)
                    y0 = py_ - (h if va == "bottom" else 0 if va == "top" else h / 2)
                    cands.append(dict(dx=r * c, dy=r * sn, ha=ha, va=va, box=(x0, y0, x0 + w, y0 + h), r=r))
            info.append((lb, (ax_, ay_), cands))
        segs = [LineString(s_) for s_ in lines]
        ssegs = [LineString(s_) for s_ in soft_lines]
        msegs = [LineString(s_) for s_ in mid_lines]
        dpoly = [Point(x, y).buffer(rr + 4) for x, y, rr in dots]
        fb = [box(*b) for b in boxes]
        W_, H_ = self.W, self.H

        def pen(i, c, chosen):
            bx = c["box"]
            bb = box(*bx)
            p = 0.45 * c["r"] + (30 if c["r"] > 60 else 0)
            p += (1.5 if c["ha"] == "right" else 3.0 if c["ha"] == "center" else 0.0) + (0.8 if c["va"] != "center" else 0.0)   # 같은 벌점이면 오른쪽·가운데 높이를 먼저
            if bx[0] < margin or bx[1] < margin or bx[2] > W_ - margin or bx[3] > H_ - margin:
                p += 6000
            for g in segs:
                p += 3.0 * g.intersection(bb).length
            for g in ssegs:
                p += 0.25 * g.intersection(bb).length
            for g in msegs:
                p += 1.4 * g.intersection(bb).length
            for g in dpoly:
                if g.intersects(bb):
                    p += 3000
            for g in fb:
                if g.intersects(bb):
                    p += 5000
            for j, cj in chosen.items():
                if j == i:
                    continue
                o = bb.intersection(box(*cj["box"])).area
                if o > 0:
                    p += 4000 + 0.02 * o
            return p

        def total(chosen):
            return sum(pen(i, chosen[i], chosen) for i in chosen)

        best, best_t = None, 1e18
        n = len(info)
        for rs in range(restarts):
            chosen = {i: (info[i][2][rng.randrange(len(info[i][2]))]) for i in range(n)}
            for _ in range(40):
                changed = False
                order = list(range(n))
                rng.shuffle(order)
                for i in order:
                    cur = pen(i, chosen[i], chosen)
                    bc, bp = chosen[i], cur
                    for c in info[i][2]:
                        pc = pen(i, c, chosen)
                        if pc < bp - 1e-9:
                            bc, bp = c, pc
                    if bc is not chosen[i]:
                        chosen[i] = bc
                        changed = True
                if not changed:
                    break
            t = total(chosen)
            if t < best_t:
                best, best_t = dict(chosen), t
        out = {}
        for i, (lb, (ax_, ay_), _) in enumerate(info):
            c = best[i]
            out[lb["key"]] = dict(dx=c["dx"], dy=c["dy"], ha=c["ha"], va=c["va"], box=c["box"], r=c["r"], leader=c["r"] > 50,
                                  penalty=pen(i, c, best))
        return out

    # ── 레이아웃 점검(라벨 겹침·잘림) ──
    def check_layout(self, pad=3.0, verbose=True):
        """라벨끼리, 라벨과 범례·축척·방위표, 라벨과 그림 가장자리가 겹치거나 잘리는지 점검한다. 문제 목록을 돌려준다."""
        self.fig.canvas.draw()
        r = self.fig.canvas.get_renderer()
        boxes = []
        for key, t in self.labels:
            bb = t.get_window_extent(r)
            # 디스플레이 좌표(좌하단 원점) → 좌상단 원점
            boxes.append((key, (bb.x0 - pad, self.H - bb.y1 - pad, bb.x1 + pad, self.H - bb.y0 + pad)))
        probs = []
        for i in range(len(boxes)):
            ki, bi = boxes[i]
            if bi[0] < 0 or bi[1] < 0 or bi[2] > self.W or bi[3] > self.H:
                probs.append(f"잘림: '{ki}' {tuple(round(v) for v in bi)}")
            for j in range(i + 1, len(boxes)):
                kj, bj = boxes[j]
                if not (bi[2] < bj[0] or bj[2] < bi[0] or bi[3] < bj[1] or bj[3] < bi[1]):
                    probs.append(f"겹침: '{ki}' × '{kj}'")
            for nm, bx in self.boxes.items():
                if nm == "legend" and ki.startswith("legend:"):
                    continue
                if not (bi[2] < bx[0] or bx[2] < bi[0] or bi[3] < bx[1] or bx[3] < bi[1]):
                    if nm in ("scale", "north") and (ki.startswith("scale:") or ki == "N"):
                        continue
                    probs.append(f"겹침: '{ki}' × {nm}")
        if verbose:
            print(f"[{self.name}] 라벨 {len(boxes)}개 점검 — " + ("문제 없음" if not probs else f"{len(probs)}건"))
            for p in probs:
                print("   ", p)
        return probs

    def save(self, path):
        """PNG(RGB, 불투명, 300dpi 메타)로 저장하고 W×H를 확인한다."""
        from PIL import Image
        import io
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        buf = io.BytesIO()
        self.fig.savefig(buf, format="png", dpi=DPI, facecolor="white")
        plt.close(self.fig)
        buf.seek(0)
        im = Image.open(buf).convert("RGB")
        assert im.size == (self.W, self.H), f"크기 불일치 {im.size} != {(self.W, self.H)}"
        im.save(path, dpi=(DPI, DPI), optimize=True)
        return path


# ── 기타 ─────────────────────────────────────────────────────────────────────
def raster_area_m2(W, H, cx, cy, w_m, geom):
    """지도와 같은 범위·크기로 도형만 검정으로 그려(안티앨리어싱 켬) 어둡기 합으로 면적(㎡)을 잰다 — 그림 좌표 변환·축척 점검용."""
    from PIL import Image
    import io
    fr = Frame(W, H, cx, cy, w_m, name="px")
    for p in iter_polys(geom):
        fr.ax.add_patch(PathPatch(_poly_path(p), fc="black", ec="none", lw=0, zorder=2))
    buf = io.BytesIO()
    fr.fig.savefig(buf, format="png", dpi=DPI, facecolor="white")
    plt.close(fr.fig)
    a = np.asarray(Image.open(buf).convert("L"), dtype=float)
    return float((255.0 - a).sum() / 255.0) / (fr.ppm ** 2)


def km2(g):
    return g.area / 1e6


def append_checks(rows, path=None):
    """수치 재산정 결과(지도 | 항목 | 문서 값 | 재산정 값 | 차이 | 비고)를 CSV에 덧붙인다(같은 지도·항목은 갈아쓴다)."""
    path = Path(path or (RESEARCH / "context_maps_checks.csv"))
    head = ["map", "item", "doc_value", "recomputed", "diff", "note"]
    old = []
    if path.exists():
        with open(path, encoding="utf-8-sig", newline="") as f:
            old = list(csv.DictReader(f))
    keys = {(r["map"], r["item"]) for r in rows}
    old = [r for r in old if (r["map"], r["item"]) not in keys]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=head)
        w.writeheader()
        for r in old + rows:
            w.writerow({k: r.get(k, "") for k in head})
    return path


def manifest_rows(rows, path=None):
    """MANIFEST_context.csv(file, 설명, 원자료 경로, 쪽/연도, 가로x세로 px, 비고)를 갱신한다(같은 file은 갈아쓴다)."""
    path = Path(path or (OUT / "MANIFEST_context.csv"))
    head = ["file", "설명", "원자료 경로", "쪽/연도", "가로x세로 px", "비고"]
    old = []
    if path.exists():
        with open(path, encoding="utf-8-sig", newline="") as f:
            old = list(csv.DictReader(f))
    keys = {r["file"] for r in rows}
    old = [r for r in old if r["file"] not in keys]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=head)
        w.writeheader()
        for r in old + rows:
            w.writerow({k: r.get(k, "") for k in head})
    return path
