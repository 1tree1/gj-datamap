# -*- coding: utf-8 -*-
"""M2 원도심(S2) — 구 경주역 부지 중심 반경 1,200 m: 건물 층수 4단계 · 문화유산 구역·보존지역 · 북천 · 500 m·1,000 m 보행 반경 · 계획 경계.

출력: assets/maps/m2_oldcore_1km.png (2000×2000 px, 정사각, 300dpi, 흰 배경 불투명)
수치 재산정(1층 79% · 문화유산 69% · 고도지구 20 m 이하 49%)은 원도심 문서(한눈에_v1 §3.2)와 같은 방식으로, 두 가지 중심점에서 다시 잰다.
  ① 문서가 쓴 중심 = 고시 구역 도형의 무게중심 (219,776.9 / 360,961.0)
  ② 이 지도의 중심 = 사용자 지정 부지 중심 (219,780 / 360,850)
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from shapely.geometry import LineString, Point, box, shape
from shapely.ops import polylabel, unary_union

import mapkit_context as mk
from mapkit_context import (C_FLOOR, C_HER_CORE, C_WATER, GRAY, INK, INK2, RED, Frame, draw_outline, draw_poly,
                            draw_polys_fast)

W = H = 2000
NAME = "m2_oldcore_1km.png"
CX, CY = 219780.0, 360850.0           # 사용자 지정 부지 중심(EPSG:5187)
HALF = 1200.0                          # 반경 1,200 m 범위(정사각 창)

win = box(CX - HALF, CY - HALF, CX + HALF, CY + HALF)
f = Frame(W, H, CX, CY, 2 * HALF, name="M2")
ax, K = f.ax, f.K

PF = json.load(open(mk.ROOT / "archive/90_derived/public_profile_20260928.json", encoding="utf-8"))
NB = {n["name"]: n for n in next(x for x in PF["facts"] if x["id"] == "s1_neighbors")["neighbors"]}
plan = mk.plan_boundary()
her = mk.load_heritage()["all"]
emd, city = mk.load_city()
emd_d = dict(emd)

# ── 바탕: 문화유산 → 하천 → 건물(층수) — 하천이 보존지역 색에 덮이지 않게 하천을 위에 둔다 ──
draw_poly(ax, her.intersection(win), fc=C_HER_CORE, alpha=0.85, z=2)
rv = unary_union([g.intersection(win) for g in mk.water_in(win)])
draw_poly(ax, rv, fc=C_WATER, z=2.5)
bl = mk.buildings_in(win)
by = {k: [] for k in C_FLOOR}
for g, fl in bl:
    by[mk.floor_class(fl)].append(g)
for k in ("1", "2", "3-4", "5+"):
    draw_polys_fast(ax, by[k], fc=C_FLOOR[k], z=3)

# ── 보행 반경 500 m · 1,000 m (직선) ──
th = np.linspace(0, 2 * np.pi, 361)
RING_LS = (0, (4.5, 3.2))
for r_ in (500, 1000):
    ax.plot(CX + r_ * np.cos(th), CY + r_ * np.sin(th), color=GRAY, lw=f.pt(0.8), ls=RING_LS, zorder=7, dash_capstyle="butt")

# ── 대상지 계획 경계(빨강 2.6pt) ──
draw_outline(ax, plan, color=RED, lw=f.pt(2.6), z=9)


def dot(x, y, ms=5.2):
    ax.plot(x, y, "o", ms=f.pt(ms), mfc=INK, mec="white", mew=f.pt(1.0), zorder=22)


# ── 라벨 ──
xy = {k: tuple(v["xy"]) for k, v in NB.items()}
school = next(x for x in json.load(open(mk.PROC / "poi_schools_4326.geojson", encoding="utf-8"))["features"] if x["properties"]["name"] == "경주고등학교")
sx, sy = mk.ll_to_5187(shape(school["geometry"])).coords[0]
# 점형 장소: 점 + 이름
for nm, (x, y), dx, dy, ha, va in (("성동시장", xy["성동시장"], 0, -14, "center", "top"), ("경주읍성", xy["경주읍성"], 0, 14, "center", "bottom"),
                                    ("황리단길", xy["황리단길"], -16, 0, "right", "center"), ("경주고", (sx, sy), 16, 0, "left", "center")):
    dot(x, y)
    f.label(x, y, nm, size=10, color=INK, weight="semibold", dx=dx, dy=dy, ha=ha, va=va)


# 면형 장소(구역 안쪽 가장 넓은 곳에 이름만): 국가지정문화유산 구역 도형의 polylabel
def zone_label_pt(name_key):
    pts = mk.ngii_names()[name_key]
    nat = [g for g, n in mk.load_heritage()["parts"] if n == "국가지정문화재구역"]
    hit = [g for g in nat if any(g.distance(q) <= 30 for q in pts)]
    u = unary_union(hit)
    big = max(mk.iter_polys(u), key=lambda p: p.area)
    return polylabel(big, 5)


p_tomb = zone_label_pt("황오동고분(사적제512호)")
p_dae = zone_label_pt("경주대릉원일원(사적제512호)")
f.label(p_tomb.x, p_tomb.y, "황오동 고분군", size=10, color=INK, weight="semibold")
f.label(p_dae.x, p_dae.y, "대릉원", size=10, color=INK, weight="semibold")

# 성건동 — 창 안 읍면동 도형의 polylabel
sg = emd_d["성건동"].intersection(win)
p_sg = polylabel(max(mk.iter_polys(sg), key=lambda p: p.area), 5)
f.label(p_sg.x, p_sg.y, "성건동", size=10, color=INK2, weight="semibold")


# 북천 — 하천 중심선(세로 절편의 가운데)을 따라 돌려서
def river_mid(x):
    seg = rv.intersection(LineString([(x, CY - HALF), (x, CY + HALF)]))
    ys = [c[1] for s in mk.iter_lines(seg) for c in s.coords]
    return (min(ys) + max(ys)) / 2


RX = 219560.0
ang = float(np.degrees(np.arctan2(river_mid(RX + 150) - river_mid(RX - 150), 300.0)))
f.label(RX, river_mid(RX), "북천", size=10.5, color="#3D6FA3", weight="semibold", rot=ang)
print("북천 각도", round(ang, 1), "라벨", round(RX), round(river_mid(RX)))

# 반경 라벨 — 오른쪽 아래 40° 방향, 원 바깥쪽에 두 줄
for r_, txt in ((500, "500 m\n걸어서 약 7분"), (1000, "1,000 m\n걸어서 약 15분")):
    a = np.radians(-40)
    f.label(CX + r_ * np.cos(a), CY + r_ * np.sin(a), txt, size=9.5, color=GRAY, weight="semibold", ha="left", va="center", dx=12, dy=-8)

# 대상지 라벨
f.label(219941, 360980, "구 경주역\n부지", size=11.5, color=RED, weight="bold", ha="left", va="center", dx=22)

# ── 범례·방위·축척 ──
f.legend([
    [{"t": "ramp", "label": "건물 층수", "items": [(C_FLOOR["1"], "1층"), (C_FLOOR["2"], "2층"), (C_FLOOR["3-4"], "3~4층"), (C_FLOOR["5+"], "5층 이상")]}],
    [{"t": "patch", "fc": C_HER_CORE, "alpha": 0.85, "label": "문화유산 구역·보존지역"},
     {"t": "line", "color": RED, "lw": 2.6, "label": "계획 경계"},
     {"t": "line", "color": GRAY, "lw": 0.8, "ls": RING_LS, "label": "보행 반경(직선)"}],
])
f.north_arrow()
f.scale_bar(500, nseg=2, unit="m")
probs = f.check_layout()

# ── 수치 재산정 ──
godo = json.load(open(mk.PROC / "godo_5187.geojson", encoding="utf-8"))["features"]
g_le20 = unary_union([shape(x["geometry"]).buffer(0) for x in godo if x["properties"].get("h_max") not in (None, "None") and float(x["properties"]["h_max"]) <= 20])
zone = mk.gosi_zone()
allb = mk.read_ngii("N3A_B0010000")


def stats(cx, cy, R=1000, excl=zone, quad=16):
    """원도심 문서와 같은 방식: 원(중심·반경) 안에 무게중심이 든 건물, excl 안 건물은 뺀다. quad는 원을 근사하는 변 수(문서는 shapely 기본 16)."""
    S2 = Point(cx, cy).buffer(R, quad)
    fl = Counter()
    for g, a in allb:
        c = g.centroid
        if S2.contains(c) and not excl.contains(c):
            try:
                fl[int(a.get("nmly") or 1) or 1] += 1
            except Exception:
                fl[1] += 1
    n = sum(fl.values())
    return dict(n=n, f1=fl[1] / n, f2=fl[2] / n, f3=sum(v for k, v in fl.items() if k >= 3) / n,
                her=her.intersection(S2).area / S2.area, godo=g_le20.intersection(S2).area / S2.area)


zc = zone.centroid
A = stats(zc.x, zc.y)                                  # 문서와 같은 중심·같은 제외·같은 원 근사
B = stats(CX, CY)                                      # 이 지도의 중심
C = stats(CX, CY, excl=plan)                           # 이 지도의 중심, 계획 경계 안 건물 제외
D = stats(CX, CY, excl=Point(0, 0).buffer(0.001))      # 이 지도의 중심, 건물 전부
rows = []
tag_A = f"문서와 같은 방식(중심 = 고시구역 무게중심 {zc.x:,.0f}/{zc.y:,.0f}, 고시구역 안 건물 제외)"
tag_B = f"이 지도 중심 {CX:,.0f}/{CY:,.0f}(고시구역 안 건물 제외) — 문서 중심에서 남쪽 {zc.y - CY:,.0f}m"
for key, label, doc in (("n", "반경 1 km 건물 수", "10,051동"), ("f1", "1층 비율", "79%"), ("f2", "2층 비율", "10%"), ("f3", "3층 이상 비율", "11%"),
                        ("her", "원 안 문화유산 구역·보존지역 비율", "69%"), ("godo", "원 안 고도지구 20 m 이하 비율", "49%")):
    fmt = (lambda v: f"{v:,}동") if key == "n" else (lambda v: f"{v * 100:.1f}%")
    dv = int(doc.replace(",", "").replace("동", "")) if key == "n" else float(doc.strip("%")) / 100
    rows.append(dict(map="M2", item=label + " [문서 방식]", doc_value=doc, recomputed=fmt(A[key]),
                     diff=(f"{A[key] - dv:+,}" if key == "n" else f"{(A[key] - dv) * 100:+.1f}%p"), note=tag_A))
    rows.append(dict(map="M2", item=label + " [이 지도 중심]", doc_value=doc, recomputed=fmt(B[key]),
                     diff=(f"{B[key] - dv:+,}" if key == "n" else f"{(B[key] - dv) * 100:+.1f}%p"), note=tag_B))
rows.append(dict(map="M2", item="(참고) 1층 비율 — 이 지도 중심, 계획 경계 안 건물 제외", doc_value="79%", recomputed=f"{C['f1'] * 100:.1f}% (n={C['n']:,})", diff="", note="이 지도 중심"))
rows.append(dict(map="M2", item="(참고) 1층 비율 — 이 지도 중심, 건물 전부", doc_value="79%", recomputed=f"{D['f1'] * 100:.1f}% (n={D['n']:,})", diff="", note="이 지도 중심"))
cnt = Counter(mk.floor_class(fl) for _, fl in bl)
rows.append(dict(map="M2", item="그림에 그려진 건물(창 2.4×2.4 km, 걸친 것 포함)", doc_value="—", recomputed=f"{len(bl):,}동: 1층 {cnt['1']:,} · 2층 {cnt['2']:,} · 3~4층 {cnt['3-4']:,} · 5층+ {cnt['5+']:,}", diff="", note=f"1층 {cnt['1'] / len(bl) * 100:.1f}%"))
rows.append(dict(map="M2", item="지도 픽셀 재산정: 1,000 m 원 면적", doc_value="π·1000² = 3.142㎢", recomputed=f"{mk.raster_area_m2(W, H, CX, CY, 2 * HALF, Point(CX, CY).buffer(1000, 256)) / 1e6:.3f}㎢",
                 diff="", note=f"{W}×{H}px, {1 / f.ppm:.2f}m/px — 그림 축척 점검"))
mk.append_checks(rows)
for r in rows:
    print(r["item"], "|", r["doc_value"], "→", r["recomputed"], r["diff"])

out = f.save(mk.OUT / NAME)
mk.manifest_rows([dict(file=NAME, 설명="M2 원도심(S2) 맥락 — 부지 중심 반경 1,200 m: 건물 층수 4단계·문화유산 구역·보존지역·북천·500 m/1,000 m 보행 반경·계획 경계(218,478㎡)",
                       **{"원자료 경로": "대지/(B020)연속수치지도_202609132098 N3A_B0010000(건물 층수 nmly)·N3A_E0010001(하천) · archive/C_data/raw/vworld_uo301_city.geojson · work/20261005_boundary_check/user_boundary_current_5187.geojson · archive/90_derived/public_profile_20260928.json(지명 위치)",
                          "쪽/연도": "수치지도 2026-09-13 취득 · V-World 2026-09", "가로x세로 px": f"{W}x{H}"},
                       비고=f"S2. 등급: 건물·하천 T2(수치지도), 문화유산 구역 T1(V-World), 지명 위치 T2, 계획 경계=사용자 라이노 경계. 중심 {CX:,.0f}/{CY:,.0f}(EPSG:5187) — 한눈에_v1 §3.2 수치는 고시구역 무게중심({zc.x:,.0f}/{zc.y:,.0f}) 기준이라 이 원에서는 문화유산 {B['her'] * 100:.0f}%·1층 {B['f1'] * 100:.0f}%·고도지구 {B['godo'] * 100:.0f}%로 달라짐. 원은 직선거리(걷기 시속 4 km 가정)")])
print("저장", out, "문제", len(probs))
