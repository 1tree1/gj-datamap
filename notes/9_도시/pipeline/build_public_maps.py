"""일반인용 지도 3장 — 경주시 한눈에(map17) · 원도심 한눈에(map18) · 구경주역 부지 한눈에(map19).

숫자는 archive/90_derived/public_profile_20260928.json (build_public_profile.py)에서만 가져온다 — 그림과 사실표가 어긋나지 않게.
지도 = 왼쪽, 질문별 큰 숫자 = 오른쪽(블록 4개, 문장은 두 줄 안팎). 긴 설명은 사실표·문서에 둔다.
전문 용어 대신 익숙한 단위(축구장·걸어서 몇 분·10채 중 몇 채)를 쓴다. 좌표는 모두 EPSG:5187.
"""
import json
import textwrap
from collections import defaultdict
from pathlib import Path

import numpy as np
import shapefile
from pyproj import Transformer
from shapely.geometry import Point, box, shape
from shapely.ops import transform, unary_union

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Circle, PathPatch, Rectangle
from matplotlib.path import Path as MPath

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "archive" / "C_data" / "raw"
PROC = ROOT / "archive" / "C_data" / "processed"
DER = ROOT / "archive" / "90_derived"
NGII = ROOT / "대지" / "(B020)연속수치지도_202609132098"
MAPS = ROOT / "work" / "maps"
PF = json.load(open(DER / "public_profile_20260928.json", encoding="utf-8"))
F = {f["id"]: f for f in PF["facts"]}

T47 = Transformer.from_crs(4326, 5187, always_xy=True).transform
T57 = Transformer.from_crs(5179, 5187, always_xy=True).transform
F_HEAD, F_BOLD, F_BODY = "NanumSquare_ac ExtraBold", "NanumSquare_ac Bold", "Noto Sans KR"
plt.rcParams.update({"font.family": F_BODY, "axes.unicode_minus": False})
BG, PAPER = "#f6f3ec", "#ece6d8"
INK, INK2, INK3 = "#1d1d1f", "#55524c", "#8a867d"
SITE, BUILT, HER, HER_FILL, WATER = "#d7301f", "#e0914f", "#7e5fb4", "#ddd2ee", "#a9cbe8"
TIER_COL = {"T1": "#1f5e42", "T2": "#2f6db5", "T3": "#6f4fa3", "T4": "#c0392b"}
HALO = [pe.withStroke(linewidth=3.2, foreground="white")]
MAP_BOX = [0.03, 0.055, 0.59, 0.775]        # 지도 축 — 위쪽 0.83까지. 범례 줄은 그 위(0.85)
WALK = PF["walk_m_per_min"]


def gj(p):
    return json.load(open(p, encoding="utf-8"))


def g5187(f, t=T47):
    g = transform(t, shape(f["geometry"]))
    return g.buffer(0) if g.geom_type in ("Polygon", "MultiPolygon") else g


def ngii(layer):
    r = shapefile.Reader(str(NGII / layer))
    fl = [f[0] for f in r.fields[1:]]
    for s in r.iterShapeRecords():
        yield transform(T57, shape(s.shape.__geo_interface__)), dict(zip(fl, s.record))


def parts(g):
    return [g] if g.geom_type in ("Polygon", "LineString", "Point") else list(getattr(g, "geoms", []))


def fill(ax, geom, **kw):
    """구멍 있는 폴리곤까지 한 번에 채운다"""
    verts, codes = [], []
    for p in parts(geom):
        if p.geom_type != "Polygon" or p.is_empty:
            continue
        for ring in [p.exterior, *p.interiors]:
            xy = np.asarray(ring.coords)[:, :2]
            if len(xy) < 4:
                continue
            verts.append(xy); codes.append([MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY])
    if verts:
        ax.add_patch(PathPatch(MPath(np.concatenate(verts), np.concatenate(codes)), **kw))


def lines(ax, geoms, **kw):
    segs = []
    for g in geoms:
        for p in parts(g):
            if p.geom_type == "LineString":
                segs.append(np.asarray(p.coords)[:, :2])
            elif p.geom_type == "Polygon":
                segs.append(np.asarray(p.exterior.coords)[:, :2])
    if segs:
        ax.add_collection(LineCollection(segs, **kw))


def label(ax, x, y, s, size=10, color=INK, weight=F_BOLD, **kw):
    ax.text(x, y, s, fontsize=size, color=color, family=weight, path_effects=HALO, zorder=20, **kw)


def scalebar(ax, x, y, length, text):
    ax.plot([x, x + length], [y, y], color=INK, lw=2.2, solid_capstyle="butt", zorder=21)
    for xx in (x, x + length):
        ax.plot([xx, xx], [y - length * .02, y + length * .02], color=INK, lw=1.2, zorder=21)
    label(ax, x + length / 2, y + length * .05, text, size=9, ha="center", va="bottom")


def north(ax, x, y, h):
    ax.annotate("", xy=(x, y + h), xytext=(x, y), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4), zorder=21)
    label(ax, x, y + h * 1.12, "N", size=9, ha="center", va="bottom")


def legend_row(fig, items, y=0.852, x=0.045, gap=0.012):
    """지도 위 한 줄 범례 — items: (색, 글, 테두리색) · 글 길이에 맞춰 옆으로 늘어놓는다"""
    for c, t, ec in items:
        fig.patches.append(Rectangle((x, y), 0.015, 0.016, transform=fig.transFigure, fc=c, ec=ec or "none", lw=.6))
        fig.text(x + 0.019, y + 0.008, t, fontsize=9.5, color=INK2, va="center")
        x += 0.019 + 0.0072 * len(t) + gap
    return x


def panel(fig, blocks, x0=0.655, top=0.845):
    """오른쪽 질문 블록 4개: 질문 / 큰 숫자 + 단위 / 두 줄 안팎 설명 / 등급 + 출처 한 줄"""
    y = top
    for b in blocks:
        fig.text(x0, y, b["q"], fontsize=12, family=F_BOLD, color=INK2, va="top")
        y -= 0.031
        t = fig.text(x0, y, b["big"], fontsize=31, family=F_HEAD, color=b.get("color", INK), va="top")
        fig.canvas.draw()
        bb = t.get_window_extent().transformed(fig.transFigure.inverted())
        fig.text(bb.x1 + 0.005, y - 0.013, b.get("unit", ""), fontsize=13, family=F_BOLD, color=INK2, va="top")
        y -= 0.055
        body = textwrap.fill(b["text"], 35)
        fig.text(x0, y, body, fontsize=10.5, color=INK, va="top", linespacing=1.5)
        y -= 0.0245 * (body.count("\n") + 1) + 0.008
        fig.text(x0, y, b["tier"], fontsize=7.6, family=F_BOLD, color="white", va="top",
                 bbox=dict(boxstyle="round,pad=0.25", fc=TIER_COL.get(b["tier"], INK3), ec="none"))
        src = textwrap.fill(b["src"], 62)
        fig.text(x0 + 0.02, y, src, fontsize=7.6, color=INK3, va="top", linespacing=1.35)
        y -= 0.0165 * (src.count("\n") + 1) + 0.027
    assert y > 0.03, f"오른쪽 블록이 아래로 넘친다 (y={y:.3f})"


def frame(title, sub, foot):
    fig = plt.figure(figsize=(16, 10), dpi=150)
    fig.patch.set_facecolor(BG)
    fig.text(0.035, 0.957, title, fontsize=27, family=F_HEAD, color=INK, va="top")
    fig.text(0.035, 0.907, sub, fontsize=13, family=F_BOLD, color=INK2, va="top")
    fig.text(0.035, 0.018, textwrap.fill(foot, 190), fontsize=7.8, color=INK3, va="bottom", linespacing=1.4)
    fig.add_artist(plt.Line2D([0.635, 0.635], [0.08, 0.86], color="#d8d2c4", lw=1))
    return fig


def blk(q, big, unit, text, fid, color=INK, src=None):
    return {"q": q, "big": big, "unit": unit, "text": text, "src": src or F[fid]["src"], "tier": F[fid]["tier"], "color": color}


zone = shape(gj(PROC / "gosi2026-8_zone_5187.geojson")["features"][0]["geometry"]).buffer(0)
cen = zone.centroid
stx, sty = PF["station_5187"]
NB = {n["name"]: n for n in F["s1_neighbors"]["neighbors"]}
uo = [f for f in gj(RAW / "vworld_uo301_city.geojson")["features"] if f["properties"].get("sigg_name") == "경주시"]
nat = [g5187(f) for f in uo if f["properties"]["uname"] == "국가지정문화재구역"]

# ═══════════════════════════════ map17 경주시 한눈에 ═══════════════════════════════
emd = [(f["properties"]["emd_kor_nm"], g5187(f)) for f in gj(RAW / "vworld_emd_gj.geojson")["features"]]
city = unary_union([g for _, g in emd]).buffer(0)
uq = [f for f in gj(RAW / "vworld_uq111_city.geojson")["features"] if f["properties"].get("sigg_name") == "경주시"]
built = unary_union([g5187(f) for f in uq if any(k in f["properties"]["uname"] for k in ("주거", "상업", "공업"))]).intersection(city)
her = unary_union([g5187(f) for f in uo]).intersection(city)
rail = [g5187(f) for f in gj(PROC / "rail_active_4326.geojson")["features"]]
tour = {f["properties"]["name"].strip(): g5187(f) for f in gj(RAW / "gj_tour_sites.geojson")["features"] if f.get("geometry")}
gw = {f["properties"]["name"]: g5187(f) for f in gj(PROC / "gateways_4326.geojson")["features"]}
A, B_, C_, P_ = F["city_area"], F["city_built"], F["city_heritage"], F["city_pop"]

fig = frame("경주는 어떤 도시인가",
            f"서울의 두 배가 넘는 땅 — 건물이 모인 곳은 {B_['value']}%, 문화유산 구역은 그보다 두 배 넘게 넓고 곳곳에 흩어져 있다",
            "지도: 경주시 경계 V-World(2026-09) · 용도지역 V-World LT_C_UQ111 · 문화유산 보호 구역 V-World LT_C_UO301 · 철도 OSM(T4) · "
            "관광지 위치 경주시 관광지 현황(T2) · KTX역 V-World 장소검색 · 좌표 EPSG:5187 · 2026-09-28 작성")
ax = fig.add_axes(MAP_BOX)
ax.set_facecolor(BG); ax.set_aspect("equal"); ax.axis("off")
fill(ax, city, fc=PAPER, ec="none", zorder=1)
fill(ax, her, fc=HER_FILL, ec="none", zorder=2)
fill(ax, built, fc=BUILT, ec="none", alpha=.92, zorder=3)
fill(ax, her, fc="none", ec=HER, lw=.45, zorder=4)
lines(ax, [g for _, g in emd], colors="white", linewidths=.7, zorder=5)
lines(ax, [city.boundary], colors=INK2, linewidths=1.3, zorder=6)
lines(ax, rail, colors="#2a2e33", linewidths=1.1, linestyles=(0, (4, 2)), zorder=8)
for nm, g in emd:
    if nm.endswith("읍"):
        c = g.representative_point(); label(ax, c.x, c.y, nm, size=10.5, color=INK2, ha="center")
for nm, dx, ha in (("불국사", 800, "left"), ("보문관광단지", 800, "left"), ("양동마을", 800, "left"), ("문무대왕릉", -800, "right")):
    if nm in tour:
        p = tour[nm]; ax.plot(p.x, p.y, "o", ms=5.5, mfc=INK, mec="white", mew=1.2, zorder=22); label(ax, p.x + dx, p.y, nm, size=10, ha=ha, va="center")
k = gw["경주역(KTX, 구 신경주역)"]; ax.plot(k.x, k.y, "s", ms=6, mfc="#2a2e33", mec="white", mew=1.2, zorder=22)
label(ax, k.x - 800, k.y, "경주역(KTX)", size=10, ha="right", va="center")
ax.plot(stx, sty, "*", ms=19, mfc=SITE, mec="white", mew=1.4, zorder=23)
label(ax, stx + 1300, sty + 900, "구경주역 부지\n(원도심)", size=12.5, color=SITE, weight=F_HEAD, ha="left", va="bottom")
b = city.bounds
label(ax, b[2] - 1500, (b[1] + b[3]) / 2 + 6000, "동해", size=13, color="#5b8cc0", ha="right")
ax.set_xlim(b[0] - 1500, b[2] + 1500); ax.set_ylim(b[1] - 1500, b[3] + 1500)
scalebar(ax, b[0] + 1000, b[1] + 1500, 10000, "10 km")
north(ax, b[0] + 2500, b[1] + 5500, 3500)
xe = legend_row(fig, [(PAPER, "산·들·녹지(시가지가 아닌 땅)", "#c9c2b2"), (BUILT, "건물이 모인 땅(주거·상업·공업지역)", None), (HER_FILL, "문화유산 구역과 그 보존지역", HER)])
fig.text(xe + 0.01, 0.86, "╍╍  철도(지금 다니는 선)", fontsize=9.5, color=INK2, va="center")
panel(fig, [
    blk("얼마나 넓은가", f"{A['ratio_seoul']:.1f}", "배 (서울 대비)", f"경주시 약 {A['value']:,.0f}㎢는 서울({A['seoul_km2']:,.0f}㎢)보다 두 배 넘게 넓다.", "city_area",
        src="국토교통부 지적기본통계 2025-12-31 — 경주·서울 같은 파일"),
    blk("그중 건물이 모인 땅은", f"{B_['value']}", "%", f"주거·상업·공업지역을 다 합쳐 {B_['by_zone_km2']['주거'] + B_['by_zone_km2']['상업'] + B_['by_zone_km2']['공업']:.0f}㎢다. 가게를 지을 수 있는 상업지역은 {F['city_commercial']['value']}%뿐이다.",
        "city_built", color=BUILT, src="V-World 용도지역(LT_C_UQ111, 2026-09 수집)을 시 경계로 잘라 잰 면적"),
    blk("문화유산 때문에 개발이 묶인 땅은", f"{C_['value']}", "%", f"문화유산 구역과 보존지역이 {C_['value'] * A['calc_city_km2'] / 100:.0f}㎢로, 건물이 모인 땅의 약 {C_['value'] / B_['value']:.1f}배다.",
        "city_heritage", color=HER, src="V-World 문화유산 보호 구역(LT_C_UO301, 2026-09 수집) 합집합 — 고도지구는 따로"),
    blk("몇 명이 사나", f"{P_['value'] / 10000:.1f}", "만 명", f"10년 새 {abs(P_['chg_10y_pct'])}% 줄었고, 10명 중 3명이 65세 이상이다.",
        "city_pop", src="행정안전부 주민등록인구(KOSIS, 2026-08)"),
])
fig.savefig(MAPS / "map17_경주시_한눈에.png", facecolor=BG)
plt.close(fig)
print("map17")

# ═══════════════════════════════ map18 원도심 한눈에 ═══════════════════════════════
R = 1250
win = box(cen.x - R, cen.y - R, cen.x + R, cen.y + R)
fig = frame("원도심은 어떤 동네인가",
            "낮고, 촘촘하고, 고분과 함께 산다 — 구경주역 부지 중심에서 반경 1 km",
            "지도: 건물·도로·하천 국토지리정보원 연속수치지도(2026-09-13, T2) · 문화유산 구역 V-World LT_C_UO301 · 부지 경주시 고시 제2026-8호(T1) · "
            "명소 위치 연속수치지도 지명 주기·경주시 관광지 현황 · 원은 직선거리(시속 4 km 걷기 가정 — 실제 길로는 더 멀다) · EPSG:5187 · 2026-09-28 작성")
ax = fig.add_axes(MAP_BOX)
ax.set_facecolor(BG); ax.set_aspect("equal"); ax.axis("off")
for g, a in ngii("N3A_E0010001"):
    if g.intersects(win):
        fill(ax, g.intersection(win), fc=WATER, ec="none", zorder=1)
fill(ax, unary_union([g for g in nat if g.intersects(win)]).intersection(win), fc=HER_FILL, ec=HER, lw=.6, zorder=2)
lines(ax, [g for g, a in ngii("N3L_A0020000") if g.intersects(win)], colors="#d9d3c6", linewidths=.5, zorder=3)
FLC = [(1, 1, "#d6cfbf", "1층"), (2, 2, "#ab9f88", "2층"), (3, 4, "#76694f", "3–4층"), (5, 99, "#2f281c", "5층 이상")]
bys = defaultdict(list)
for g, a in ngii("N3A_B0010000"):
    if not win.contains(g.centroid):
        continue
    fl = int(a.get("nmly") or 1) or 1
    for lo, hi, col, _ in FLC:
        if lo <= fl <= hi:
            bys[col].extend(np.asarray(p.exterior.coords)[:, :2] for p in parts(g) if p.geom_type == "Polygon")
for _, _, col, _ in FLC:
    ax.add_collection(PolyCollection(bys[col], facecolors=col, edgecolors="none", zorder=4))
fill(ax, zone, fc=SITE, alpha=.14, ec="none", zorder=5)
fill(ax, zone, fc="none", ec=SITE, lw=2.2, zorder=6)
for r_ in (500, 1000):
    ax.add_patch(Circle((cen.x, cen.y), r_, fc="none", ec=INK2, lw=1.1, ls=(0, (5, 4)), zorder=7))
    label(ax, cen.x + r_ * .72, cen.y - r_ * .72, f"{r_:,} m · 걸어서 약 {round(r_ / WALK)}분", size=9.5, color=INK2, ha="left", va="top")
label(ax, zone.bounds[2] + 30, cen.y + 330, "구경주역\n부지", size=13, color=SITE, weight=F_HEAD, ha="left", va="center")
for nm in ("성동시장", "경주읍성", "황오동 고분", "대릉원", "황리단길", "첨성대", "계림", "동궁과 월지"):
    if nm in NB:
        x, y = NB[nm]["xy"]
        if win.buffer(-60).contains(Point(x, y)):
            ax.plot(x, y, "o", ms=5, mfc=INK, mec="white", mew=1.1, zorder=22)
            label(ax, x - 30, y + 40, nm, size=10.5, ha="right", va="bottom")
label(ax, cen.x - 330, cen.y + 860, "북천", size=11, color="#3d6fa3", ha="center")
ax.set_xlim(win.bounds[0], win.bounds[2]); ax.set_ylim(win.bounds[1], win.bounds[3])
scalebar(ax, win.bounds[0] + 80, win.bounds[1] + 90, 500, "500 m")
north(ax, win.bounds[0] + 150, win.bounds[1] + 260, 180)
legend_row(fig, [(c, t, None) for _, _, c, t in FLC] + [(HER_FILL, "국가지정문화유산 구역", HER), (WATER, "하천", None), ("#f6d5cf", "구경주역 부지", SITE)])
L, AL, LOT, TB, HI, OD, PP = (F[k] for k in ("s2_low", "s2_alley", "s2_lot", "s2_tombs", "s2_height", "s2_old", "s2_people"))
panel(fig, [
    blk("얼마나 낮은가 — 1층 건물", f"{round(L['value'] / 10)}", "채 / 10채", f"반경 1 km 건물 {sum(L['floors'].values()):,}동 가운데 {L['value']}%가 1층이다. 3층 이상은 {100 - L['value'] - round(L['floors']['2'] / sum(L['floors'].values()) * 100)}%뿐이다.",
        "s2_low", color="#76694f", src="국토지리정보원 연속수치지도 건물 층수(2026-09-13 취득)"),
    blk("길은 얼마나 좁은가 — 폭 4 m 미만 골목", f"{AL['value']}", "%", f"길 {sum(AL['km'].values()):.0f} km 가운데 {AL['km']['lt4']:.0f} km가 골목이다. 집 한 필지는 약 {LOT['value'] / 3.3058:.0f}평({LOT['value']}㎡)이다.",
        "s2_alley", src="연속수치지도 도로 폭 · V-World 연속지적 대지 4,581필지"),
    blk("고분과 얼마나 붙어 사나", f"{TB['value']}", "%", f"원 안 땅의 {TB['value']}%가 문화유산 구역·보존지역이고, {HI['value']}%는 높이 20 m 이하로 묶여 있다.",
        "s2_tombs", color=HER, src="V-World 문화유산 보호 구역 · 고도지구(경상북도 고시 제2020-479호 높이)"),
    blk("사람은 줄고 있나 — 황오동 10년", f"{abs(PP['value'])}", "% 감소", f"부지 동쪽 황오동 인구가 10년 새 3분의 1 줄었다. 건물은 30년 넘은 필지가 {OD['value']:.0f}%다.",
        "s2_people", color=SITE, src="행정안전부 주민등록인구(2026-08, 옛 중부동 합산) · 건축물대장(5개 동)"),
])
fig.savefig(MAPS / "map18_원도심_한눈에.png", facecolor=BG)
plt.close(fig)
print("map18")

# ═══════════════════════════════ map19 부지 한눈에 ═══════════════════════════════
zb = zone.bounds
win = box(zb[0] - 360, zb[1] - 170, zb[2] + 360, zb[3] + 150)
fig = frame("구경주역 부지는 어떤 땅인가",
            f"축구장 {round(156460 / PF['field_m2'])}개 크기 — 1 km 가까이 동네를 가르는 옛 선로 자리",
            "지도: 구역·획지 경주시 고시 제2026-8호(2026-01-22) 도면 좌표등록(T1) · 건물·도로·하천·철도·육교 국토지리정보원 연속수치지도(T2) · "
            "문화유산 구역 V-World · 횡단 판독 2026-09-28 자체 계산(현장 확인 전) · 옛 역사 위치 OSM(T4) · EPSG:5187")
ax = fig.add_axes(MAP_BOX)
ax.set_facecolor(BG); ax.set_aspect("equal"); ax.axis("off")
for g, a in ngii("N3A_E0010001"):
    if g.intersects(win):
        fill(ax, g.intersection(win), fc=WATER, ec="none", zorder=1)
fill(ax, unary_union([g for g in nat if g.intersects(win)]).intersection(win), fc=HER_FILL, ec=HER, lw=.6, zorder=2)
lines(ax, [g for g, a in ngii("N3L_A0020000") if g.intersects(win)], colors="#d9d3c6", linewidths=.6, zorder=3)
bl = []
for g, a in ngii("N3A_B0010000"):
    if win.contains(g.centroid) and not zone.contains(g.centroid):
        bl.extend(np.asarray(p.exterior.coords)[:, :2] for p in parts(g) if p.geom_type == "Polygon")
ax.add_collection(PolyCollection(bl, facecolors="#cfc7b6", edgecolors="none", zorder=4))
PLAN = {"park": ("#9cc58a", "근린공원"), "commercial": ("#f0a868", "상업"), "civic": ("#7ea6d8", "공공청사"), "culture": ("#b39ddb", "문화시설"), "parking": ("#b8b8b8", "주차장")}
fill(ax, zone, fc="#f4efe6", ec="none", zorder=5)                      # 블록 사이 = 도로
for f in gj(PROC / "gosi2026-8_blocks_5187.geojson")["features"]:
    fill(ax, shape(f["geometry"]).buffer(0), fc=PLAN[f["properties"]["cls"]][0], ec="white", lw=.8, alpha=.9, zorder=6)
rl = [g.intersection(win) for g, a in ngii("N3L_A0171119") if g.intersects(win)]   # 철도중심선 — 역 구내 여러 가닥이라 옅게
lines(ax, rl, colors="#5d5a53", linewidths=.55, alpha=.55, zorder=7)
fill(ax, zone, fc="none", ec=SITE, lw=2.4, zorder=8)
for g, a in ngii("N3A_A0063321"):                                         # 육교
    if g.intersects(win):
        fill(ax, g, fc="#2a2e33", ec="none", zorder=9)
DT = gj(PROC / "fabric_report.json")["detour"]
z0, z1 = DT["zone_y"]
nx = min((c for c in DT["crossings"] if c["y"] > z1), key=lambda c: c["y"])
xs = zb[2] + 60
ax.annotate("", xy=(xs, DT["rail_gap"]["y"]), xytext=(xs, nx["y"]), arrowprops=dict(arrowstyle="<->", color=SITE, lw=1.8), zorder=21)
label(ax, xs + 25, (DT["rail_gap"]["y"] + nx["y"]) / 2 + 60, f"{F['s1_wall']['value']:,} m 동안\n차가 건널 길이 없다", size=12, color=SITE, weight=F_HEAD, ha="left", va="center")
for c in (DT["rail_gap"], nx):
    ax.plot(c["x"], c["y"], "o", ms=10, mfc="white", mec=SITE, mew=2.4, zorder=22)
label(ax, DT["rail_gap"]["x"] + 30, DT["rail_gap"]["y"] - 20, "건너는 길(남쪽)", size=9.5, ha="left", va="top")
label(ax, nx["x"] + 30, nx["y"] + 15, f"건너는 길(북쪽, 폭 {nx['width_m']:.0f} m)", size=9.5, ha="left", va="bottom")
o = DT["overpass"][0]
label(ax, o["x"] + 150, o["y"] + 25, f"육교 폭 {o['width_m']} m\n(열려 있는지 확인 전)", size=9, ha="left", va="bottom")
xd = zb[0] - 95
ax.annotate("", xy=(xd, z0), xytext=(xd, z1), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3), zorder=21)
label(ax, xd - 18, z0 + (z1 - z0) * .86, f"남북 {F['s1_size']['ns_m']} m\n걸어서 약 {round(F['s1_size']['ns_m'] / WALK)}분", size=10.5, ha="right", va="center")
ax.plot(stx, sty, "D", ms=8, mfc=INK, mec="white", mew=1.3, zorder=23)
label(ax, stx - 25, sty - 30, "옛 경주역 역사", size=10, ha="right", va="top")
x, y = NB["성동시장"]["xy"]; ax.plot(x, y, "o", ms=5, mfc=INK, mec="white", mew=1.1, zorder=22); label(ax, x - 20, y + 25, "성동시장", size=10.5, ha="right", va="bottom")
x, y = NB["황오동 고분"]["xy"]
if win.contains(Point(x, y)):
    ax.plot(x, y, "o", ms=5, mfc=INK, mec="white", mew=1.1, zorder=22); label(ax, x + 25, y - 10, "황오동 고분", size=10.5, ha="left", va="top")
label(ax, zb[2] + 200, zb[1] + 330, "황오동\n(1층 골목 동네)", size=11, color=INK2, ha="center")
label(ax, (zb[0] + zb[2]) / 2 + 60, zb[3] + 90, "북천", size=11, color="#3d6fa3", ha="center")
fx, fy = win.bounds[0] + 45, win.bounds[1] + 45                            # 같은 축척의 축구장 1면
ax.add_patch(Rectangle((fx - 12, fy - 12), 105 + 24 + 150, 68 + 24, fc="white", ec="#d8d2c4", lw=.8, zorder=20))
ax.add_patch(Rectangle((fx, fy), 105, 68, fc="#e9f2e1", ec="#3c7a3a", lw=1.2, zorder=21))
ax.plot([fx + 52.5, fx + 52.5], [fy, fy + 68], color="#3c7a3a", lw=.8, zorder=22)
ax.text(fx + 118, fy + 34, f"축구장 1면\n(105 × 68 m)\n같은 축척\n구역은 약 {round(156460 / PF['field_m2'])}면", fontsize=8.5, color=INK2, va="center", zorder=22)
ax.set_xlim(win.bounds[0], win.bounds[2]); ax.set_ylim(win.bounds[1], win.bounds[3])
scalebar(ax, win.bounds[2] - 280, win.bounds[1] + 50, 200, "200 m")
north(ax, win.bounds[2] - 50, win.bounds[1] + 130, 90)
legend_row(fig, [(c, t, "white") for c, t in PLAN.values()] + [("#f4efe6", "도로", "#c9c2b2")])
fig.text(0.47, 0.86, "← 2026년 1월 고시된 계획 · 주거용지 없음", fontsize=9.5, color=INK2, va="center")
SZ, WL, UG, PL = F["s1_size"], F["s1_wall"], F["s1_underground"], F["s1_plan"]
comp = PL["composition_m2"]
panel(fig, [
    blk("얼마나 큰가 — 축구장으로", f"{round(SZ['value'] / PF['field_m2'])}", "면", f"구역 {SZ['value']:,}㎡, 남북 {SZ['ns_m']} m다. 시 보도자료의 ‘79,438㎡’는 범위가 적혀 있지 않다.",
        "s1_size", color=SITE, src="경주시 고시 제2026-8호(2026-01-22) 결정조서 · 79,438㎡는 경주시 보도자료 2025-12-18(T2)"),
    blk("왜 동네를 가르나", f"{WL['value']:,}", "m", f"선로를 따라 이만큼 차가 건널 길이 없다. 직선 {WL['straight_m']} m 떨어진 양쪽을 길로 가면 {WL['network_m']:,} m, 약 {WL['detour']}배를 돌아간다.",
        "s1_wall", color=SITE, src="연속수치지도 도로·철도, 2026-09-28 자체 계산 — 차 다니는 길 기준, 육교 제외, 현장 확인 전"),
    blk("땅 밑에는 무엇이 있나", f"{UG['value']}", "%", "구역 대부분이 유물이 묻혀 있을 수 있어 시굴조사를 해야 하는 땅이다.",
        "s1_underground", color=HER, src="구)경주역일원 매장유산 시굴조사 추진계획(2026.02 포럼 발표)"),
    blk("2026년 1월 고시된 계획에서 주거용지는", "0", "%", "2026.1 고시: " + " · ".join(f"{k} {v / SZ['value'] * 100:.0f}" for k, v in comp.items()) + "%. 주거용지는 없다.",
        "s1_plan", src="경주시 고시 제2026-8호 결정조서 — 공모·변경 과정에서 바뀔 수 있다"),
])
fig.savefig(MAPS / "map19_구경주역부지_한눈에.png", facecolor=BG)
plt.close(fig)
print("map19")

# ═══════════════════════════════ map20 부지의 시간 ═══════════════════════════════
# 연표는 원문 대조한 날짜만 쓴다(s1_history.events). 사건이 몰린 2005년 이후를 넓혀 그린다(축 끊김 표시).
H = F["s1_history"]; EV = H["events"]
fig = plt.figure(figsize=(16, 10), dpi=150)
fig.patch.set_facecolor(BG)
fig.text(0.035, 0.957, "옛 경주역이 지나온 시간", fontsize=27, family=F_HEAD, color=INK, va="top")
fig.text(0.035, 0.907, "1918년 협궤 기차역으로 문을 열어 103년, 그중 85년을 지금 자리에서 — 2021년 문을 닫고 2026년 새 계획이 고시됐다",
         fontsize=13, family=F_BOLD, color=INK2, va="top")
fig.text(0.035, 0.018, textwrap.fill("날짜 출처: 조선총독부 관보 제1872·1924·2955호, 국토교통부고시 제2021-1234·2023-45호, 경주시 고시 제2026-8호(T1) · 한국철도공사 공사연혁, "
         "국토교통부 보도참고자료 2021-12-27, 경주시 보도자료·시정뉴스(T2) · 김신재(2013) 『신라문화』 41, 387쪽(T3) · 2026-09-28 원문 대조", 190),
         fontsize=7.8, color=INK3, va="bottom", linespacing=1.4)
tl = fig.add_axes([0.035, 0.47, 0.93, 0.40]); tl.set_xlim(0, 1); tl.set_ylim(0, 1); tl.axis("off")


def xt(y):
    """1910–2005는 앞쪽 45%, 2005–2027은 뒤쪽 45%에 — 최근 사건이 겹치지 않게"""
    return 0.03 + (y - 1910) / 95 * 0.45 if y <= 2005 else 0.48 + (y - 2005) / 22 * 0.49


def yr(d):
    y, m, dd = (int(v) for v in d.split("-"))
    return y + (m - 1) / 12 + (dd - 1) / 365


AX_Y = 0.46
tl.plot([xt(1910), xt(2004.3)], [AX_Y, AX_Y], color=INK2, lw=2, solid_capstyle="butt")
tl.plot([xt(2005.7), xt(2027)], [AX_Y, AX_Y], color=INK2, lw=2, solid_capstyle="butt")
tl.text(xt(2005), AX_Y, "//", fontsize=13, color=INK2, ha="center", va="center", family=F_BOLD)
for y in (1920, 1940, 1960, 1980, 2000, 2010, 2015, 2020, 2025):
    tl.plot([xt(y), xt(y)], [AX_Y - .012, AX_Y + .012], color=INK2, lw=1)
    tl.text(xt(y), AX_Y - .03, str(y), fontsize=9, color=INK3, ha="center", va="top")
tl.add_patch(Rectangle((xt(yr("1918-12-28")), AX_Y + .018), xt(yr("2021-12-28")) - xt(yr("1918-12-28")), .02, fc="#9a948a", ec="none"))
tl.add_patch(Rectangle((xt(yr("1936-12-01")), AX_Y + .018), xt(yr("2021-12-28")) - xt(yr("1936-12-01")), .02, fc=SITE, ec="none"))
tl.text(xt(1927), AX_Y + .05, "역이 있던 103년", fontsize=9.5, color=INK2, family=F_BOLD, ha="center", va="bottom")
tl.text(xt(1975), AX_Y + .05, "지금 자리에서 85년", fontsize=9.5, color=SITE, family=F_BOLD, ha="center", va="bottom")
tl.text(xt(1910), AX_Y - .09, "그 전 — 땅 밑에는\n통일신라 시대의 흔적이\n있다(부지 안 발굴 3곳,\n유물포함층 · 김권일\n2026, T2)", fontsize=8.8, color=INK3, ha="left", va="top", linespacing=1.4)
SLOT = [(0.035, "up"), (0.16, "down"), (0.40, "up"), (0.525, "down"), (0.655, "up"), (0.775, "down"), (0.84, "up")]
for e, (cx, side) in zip(EV, SLOT):
    x = xt(yr(e["date"]))
    tl.plot(x, AX_Y, "o", ms=9, mfc="white", mec=SITE if "닫다" in e["title"] or "옮기다" in e["title"] else INK, mew=2.2, zorder=5)
    top = side == "up"
    y0 = 0.98 if top else 0.36
    tl.plot([x, x, cx + 0.004], [AX_Y + (0.03 if top else -0.03), (y0 - 0.245) if top else (y0 + 0.012), (y0 - 0.245) if top else (y0 + 0.012)],
            color="#c9c2b2", lw=.9, zorder=1)
    y = y0
    tl.text(cx, y, e["date"].replace("-", ". ") + ".", fontsize=10, color=INK3, family=F_BOLD, va="top")
    tl.text(cx, y - .045, e["title"], fontsize=13.5, color=INK, family=F_HEAD, va="top")
    body = textwrap.fill(e["text"], 25)
    tl.text(cx, y - .105, body, fontsize=9.3, color=INK2, va="top", linespacing=1.45)
    tl.text(cx, y - .105 - .052 * (body.count("\n") + 1) - .01, e["tier"], fontsize=7, family=F_BOLD, color="white", va="top",
            bbox=dict(boxstyle="round,pad=0.2", fc=TIER_COL.get(e["tier"], INK3), ec="none"))
# 아래: 두 개의 '경주역'
mp = fig.add_axes([0.035, 0.055, 0.40, 0.36]); mp.set_aspect("equal"); mp.axis("off")
fill(mp, city, fc=PAPER, ec="none", zorder=1)
fill(mp, built, fc=BUILT, ec="none", alpha=.85, zorder=2)
lines(mp, [city.boundary], colors=INK2, linewidths=1, zorder=3)
lines(mp, rail, colors="#2a2e33", linewidths=.9, linestyles=(0, (4, 2)), zorder=4)
k = gw["경주역(KTX, 구 신경주역)"]
mp.plot([stx, k.x], [sty, k.y], color=INK, lw=1.2, ls=(0, (2, 2)), zorder=5)
mp.plot(stx, sty, "*", ms=17, mfc=SITE, mec="white", mew=1.3, zorder=6)
mp.plot(k.x, k.y, "s", ms=9, mfc="#2a2e33", mec="white", mew=1.3, zorder=6)
label(mp, stx + 900, sty + 700, "옛 경주역(원도심)\n2021년 문 닫음", size=10, color=SITE, weight=F_HEAD, ha="left", va="bottom")
label(mp, k.x - 900, k.y - 600, "지금의 ‘경주역’(KTX)\n옛 신경주역 · 건천읍", size=10, ha="right", va="top")
dkm = Point(stx, sty).distance(k) / 1000
label(mp, (stx + k.x) / 2, (sty + k.y) / 2 + 700, f"직선 {dkm:.1f} km", size=10.5, weight=F_HEAD, ha="center", va="bottom")
cb = city.bounds; pad = 3000
mp.set_xlim(k.x - 14000, stx + 16000); mp.set_ylim(k.y - 12000, sty + 12000)
fig.text(0.035, 0.425, "지금 ‘경주역’이라고 하면 어디인가", fontsize=13, family=F_BOLD, color=INK2, va="bottom")
bx = 0.50
fig.text(bx, 0.405, "숫자로 보면", fontsize=13, family=F_BOLD, color=INK2, va="top")
for i, (n, u, t) in enumerate([("103", "년", "경주역이 문을 연 1918년 12월 28일부터 닫은 2021년 12월 28일까지"),
                               ("85", "년", "지금 자리(1936년 12월 새 정거장)에서 보낸 시간"),
                               (f"{dkm:.1f}", "km", "옛 경주역과 지금의 KTX ‘경주역’ 사이 직선거리")]):
    yy = 0.36 - i * 0.078
    t_ = fig.text(bx, yy, n, fontsize=30, family=F_HEAD, color=SITE if i < 2 else INK, va="top")
    fig.canvas.draw(); bb = t_.get_window_extent().transformed(fig.transFigure.inverted())
    fig.text(bb.x1 + 0.005, yy - 0.012, u, fontsize=13, family=F_BOLD, color=INK2, va="top")
    fig.text(bx + 0.13, yy - 0.012, textwrap.fill(t, 34), fontsize=10.3, color=INK, va="top", linespacing=1.45)
fig.text(bx, 0.128, textwrap.fill("바로잡은 날짜 — 흔히 쓰는 ‘1918년 11월 1일 개업’은 금호~서악 구간이 열린 날이고(관보 제1872호), 경주까지는 12월 28일에 열렸다(관보 제1924호). "
         "신경주역이 ‘경주역’이 된 것은 2021년이 아니라 2023년 12월 28일이다. 옛 역사는 등록문화유산이 아니고 코레일 철도기념물(2013)이다.", 70),
         fontsize=9.3, color=INK2, va="top", linespacing=1.5,
         bbox=dict(boxstyle="round,pad=0.6", fc="white", ec="#d8d2c4"))
fig.savefig(MAPS / "map20_옛경주역_시간.png", facecolor=BG)
plt.close(fig)
print("map20")
