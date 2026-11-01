# -*- coding: utf-8 -*-
"""M3 부지 → 원도심 주요 자산까지 직선거리(S1→S2) — 옛 경주역에서 8곳으로 직선 연결선 · 거리 라벨 · 걷기 5·10·15분 점선 원.

출력: assets/maps/m3_site_distance.png (2000×2000 px, 정사각, 300dpi, 흰 배경 불투명)
거리 값은 한눈에_v1 §3.3 표를 그대로 쓴다. 표의 기준점은 OSM '구경주역' 점(219,649.2 / 360,746.0, T4)이다 —
  이 점에서 같은 방식(넓은 유적은 가장 가까운 경계까지)으로 다시 재면 8개 모두 ±0.1% 안에서 표와 같다.
  연속수치지도의 '경주역' 2층 건물(1,404㎡) 중심에서 재면 값이 달라진다(검산표 참고) → 그 기준의 대안 그림은
  `python m3_site_distance.py alt` 로 만든다(m3b_site_distance_station_building.png).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from shapely.geometry import Point, box
from shapely.ops import nearest_points, unary_union
import matplotlib.patheffects as pe

import mapkit_context as mk
from mapkit_context import (C_BLD1, C_HER_CORE, C_WATER, BLUE, GRAY, INK, RED, Frame, draw_outline, draw_poly,
                            draw_polys_fast)

ALT = len(sys.argv) > 1 and sys.argv[1] == "alt"
W = H = 2000
NAME = "m3b_site_distance_station_building.png" if ALT else "m3_site_distance.png"
SX, SY = mk.OLD_STATION_OSM                                     # 표의 기준점(OSM, T4)
BLD_C = (219688.0, 360792.9)                                    # 연속수치지도 '경주역' 2층 건물(1,404㎡) 무게중심
OX, OY = BLD_C if ALT else (SX, SY)
CX, CY, HALF = 219649.2, 360596.0, 1330.0                       # 창: 걷기 15분 원(반경 1,005 m)과 계림(남쪽 1,250 m)이 다 들어오게
WALK = mk.WALK_M_PER_MIN
MAP = "M3b" if ALT else "M3"

win = box(CX - HALF, CY - HALF, CX + HALF, CY + HALF)
f = Frame(W, H, CX, CY, 2 * HALF, name=MAP)
ax, K = f.ax, f.K

plan = mk.plan_boundary()
her = mk.load_heritage()
tour = mk.load_tour()
names = mk.ngii_names()
nat_parts = [g for g, n in her["parts"] if n == "국가지정문화재구역"]


def heritage_area(label):
    """지명 주기 점을 품은(없으면 30 m 안) 국가지정문화유산 구역들의 합집합 — 없으면 점 자체(한눈에_v1 §3.3과 같은 방식)"""
    pts = names[label]
    hit = [g for g in nat_parts if any(g.distance(q) <= 30 for q in pts)]
    return unary_union(hit) if hit else unary_union(pts)


ASSETS = [  # (표시 이름, 도형, 표의 거리 m, 위치 근거)
    ("황오동 고분", heritage_area("황오동고분(사적제512호)"), 345, "지명 주기 + 문화유산 구역 경계"),
    ("성동시장", tour["성동시장"], 355, "관광지 현황"),
    ("경주읍성", tour["경주읍성"], 497, "관광지 현황"),
    ("대릉원", heritage_area("경주대릉원일원(사적제512호)"), 523, "지명 주기 + 문화유산 구역 경계"),
    ("동궁과 월지", heritage_area("경주동궁과월지(사적제18호)"), 920, "지명 주기 + 문화유산 구역 경계"),
    ("황리단길", tour["황리단길"], 994, "관광지 현황"),
    ("첨성대", unary_union(names["첨성대(국보제31호)"]), 1030, "지명 주기"),
    ("계림", unary_union(names["계림(사적제19호)"]), 1250, "지명 주기"),
]
origin = Point(OX, OY)
END = {}
for nm, g, dv, src in ASSETS:
    p = nearest_points(origin, g)[1]                              # 점이면 그 점, 넓은 유적이면 가장 가까운 경계점
    END[nm] = (p.x, p.y, origin.distance(g))

# ── 바탕: 문화유산 → 하천 → 건물(단색) ──
draw_poly(ax, her["all"].intersection(win), fc=C_HER_CORE, alpha=0.85, z=2)
rv = unary_union([g.intersection(win) for g in mk.water_in(win)])
draw_poly(ax, rv, fc=C_WATER, z=2.5)
draw_polys_fast(ax, [g for g, _ in mk.buildings_in(win)], fc=C_BLD1, z=3)

# ── 걷기 5·10·15분 점선 원(분당 67 m) ──
th = np.linspace(0, 2 * np.pi, 361)
RING_LS = (0, (4.5, 3.2))
ring_px = []
for mnt in (5, 10, 15):
    r_ = mnt * 67
    ax.plot(OX + r_ * np.cos(th), OY + r_ * np.sin(th), color=GRAY, lw=f.pt(1.0), ls=RING_LS, zorder=7, dash_capstyle="butt")
    ring_px.append([f.to_px(OX + r_ * np.cos(t), OY + r_ * np.sin(t)) for t in th])

# ── 대상지 계획 경계 ──
draw_outline(ax, plan, color=RED, lw=f.pt(2.6), z=9)
plan_px = [f.to_px(x, y) for x, y in plan.exterior.coords]

# ── 직선 연결선(검정) + 자산 점(파랑) + 기준점 ──
halo = [pe.withStroke(linewidth=f.pt(1.3) + 2 * 3 * 72 / mk.DPI, foreground="white")]
line_px = []
for nm, g, dv, src in ASSETS:
    x, y, d = END[nm]
    ln, = ax.plot([OX, x], [OY, y], color=INK, lw=f.pt(1.3), zorder=12, solid_capstyle="round")
    ln.set_path_effects(halo)
    line_px.append((f.to_px(OX, OY), f.to_px(x, y)))
DOT_MS = 7.5
for nm, g, dv, src in ASSETS:
    x, y, d = END[nm]
    ax.plot(x, y, "o", ms=f.pt(DOT_MS), mfc=BLUE, mec="white", mew=f.pt(1.2), zorder=20)
ax.plot(OX, OY, "D", ms=f.pt(8.0), mfc=INK, mec="white", mew=f.pt(1.3), zorder=22)
dot_r = f.pt(DOT_MS) * mk.DPI / 72 / 2 + f.pt(1.2) * mk.DPI / 72

# ── 범례(단일 열)·방위·축척 — 라벨 배치 전에 놓아 장애물로 쓴다 ──
f.legend([
    {"t": "dot", "color": INK, "marker": "D", "ms": 7, "label": "구 경주역(거리 기준점)" if not ALT else "구 경주역 역사 건물 중심"},
    {"t": "dot", "color": BLUE, "ms": 7.5, "label": "주요 자산(가장 가까운 지점까지)"},
    {"t": "line", "color": GRAY, "lw": 1.0, "ls": RING_LS, "label": "걷기 5·10·15분"},
    {"t": "patch", "fc": C_HER_CORE, "alpha": 0.85, "label": "문화유산 구역·보존지역"},
    {"t": "line", "color": RED, "lw": 2.6, "label": "계획 경계"},
])
f.north_arrow()
f.scale_bar(500, nseg=2, unit="m")

# ── 고정 라벨: 걷기 원(오른쪽 아래 방향) · 기준점 이름 ──
fixed_boxes = []
for mnt in (5, 10, 15):
    r_ = mnt * 67
    a = np.radians(-28)
    t = f.label(OX + r_ * np.cos(a), OY + r_ * np.sin(a), f"{mnt}분\n{r_:,} m", size=9.5, color=GRAY, weight="semibold", ha="left", va="center", dx=10, key=f"ring{mnt}")
    fixed_boxes.append(f.label_box(t))
t = f.label(OX, OY, "구 경주역" if not ALT else "구 경주역 역사", size=10.5, color=INK, weight="bold", dx=-22, ha="right", va="center", key="origin")
fixed_boxes.append(f.label_box(t))

# ── 자산 라벨 자동 배치: 선·점·범례·다른 라벨을 피해 가장 가까운 빈자리 ──
shown = {}
labels = []
for nm, g, dv, src in ASSETS:
    val = dv if not ALT else round(END[nm][2])                    # 대안 그림은 기준점이 바뀌어 다시 잰 값을 쓴다
    shown[nm] = val
    labels.append(dict(key=nm, text=f"{nm}\n{val:,} m", anchor=END[nm][:2], size=10, weight="semibold", linespacing=1.12))
dots = [(*f.to_px(*END[nm][:2]), dot_r) for nm, *_ in ASSETS] + [(*f.to_px(OX, OY), dot_r + 4)]
placed = f.auto_place(labels, lines=line_px, soft_lines=ring_px, mid_lines=[plan_px], dots=dots,
                      boxes=[f.boxes["legend"], f.boxes["north"], f.boxes["scale"], *fixed_boxes], radii=(20, 46, 90, 140), restarts=40)
for lb in labels:
    nm = lb["key"]
    pl = placed[nm]
    x, y = END[nm][:2]
    f.label(x, y, lb["text"], size=10, color=INK, weight="semibold", dx=pl["dx"], dy=pl["dy"], ha=pl["ha"], va=pl["va"], key=nm, linespacing=1.12)
    print(f"  {nm:8s} r={pl['r']:>3} {pl['ha']:>6}/{pl['va']:<6} 벌점 {pl['penalty']:.0f}")
    if pl["leader"]:
        # 점에서 라벨 상자의 가장 가까운 점까지 가는 선
        px, py = f.to_px(x, y)
        bx = pl["box"]
        qx, qy = min(max(px, bx[0] + 5), bx[2] - 5), min(max(py, bx[1] + 5), bx[3] - 5)
        f.ov.plot([px, qx], [py, qy], color=INK, lw=f.pt(0.8), zorder=21)

probs = f.check_layout()

# ── 수치 재산정: 지도에 그린 선분 길이 vs 표 ──
rows = []
for nm, g, dv, src in ASSETS:
    x, y, d = END[nm]
    seg = float(np.hypot(x - OX, y - OY))                         # 그린 선분 길이
    d_osm = Point(SX, SY).distance(g)
    d_bld = Point(*BLD_C).distance(g)
    rows.append(dict(map=MAP, item=f"{nm} 직선거리", doc_value=f"{dv:,} m",
                     recomputed=f"{seg:,.0f} m (그린 선 {seg * f.ppm:,.0f}px)", diff=f"{(seg / dv - 1) * 100:+.1f}%",
                     note=f"그림 기준점에서 잰 값. 참고: OSM점 기준 {d_osm:,.0f} m({(d_osm / dv - 1) * 100:+.1f}%) · 경주역 2층 건물 중심 기준 {d_bld:,.0f} m({(d_bld / dv - 1) * 100:+.1f}%) · 그림 표시값 {shown[nm]:,} m · 위치 근거 {src}"))
for mnt in (5, 10, 15):
    rows.append(dict(map=MAP, item=f"걷기 {mnt}분 원 반지름", doc_value=f"{mnt * 67:,} m", recomputed=f"{mnt * 67:,} m", diff="0",
                     note=f"분당 67 m 가정(시속 약 4 km). 4000/60 = {WALK:.2f} m/분이면 {mnt * WALK:,.0f} m({abs(mnt * 67 - mnt * WALK) / (mnt * WALK) * 100:.1f}% 차이)"))
rows.append(dict(map=MAP, item="기준점 위치 차이(OSM점 ↔ 경주역 2층 건물 중심)", doc_value="—",
                 recomputed=f"{np.hypot(BLD_C[0] - SX, BLD_C[1] - SY):.0f} m", diff="", note=f"OSM점 {SX:,.1f}/{SY:,.1f} · 건물 중심 {BLD_C[0]:,.1f}/{BLD_C[1]:,.1f}(N3A_B0010000 name='경주역', 2층, 1,404㎡)"))
mk.append_checks(rows)
for r in rows:
    print(r["item"], "|", r["doc_value"], "→", r["recomputed"], r["diff"])

out = f.save(mk.OUT / NAME)
gap = np.hypot(BLD_C[0] - SX, BLD_C[1] - SY)
if ALT:
    desc = "M3 대안 — 옛 경주역 역사 건물(연속수치지도 '경주역' 2층 1,404㎡) 중심 기준으로 다시 잰 직선거리(표 값과 다름)"
    note_ = f"대안. 기준점이 OSM점보다 {gap:.0f} m 북동쪽이라 황오동 고분·대릉원·황리단길 값이 표보다 6~16% 큼. 표 값과 함께 쓰지 말 것"
else:
    desc = "M3 부지(S1)→원도심(S2) 주요 자산 8곳까지 직선거리 — 한눈에_v1 §3.3 표 값, 걷기 5·10·15분 점선 원"
    note_ = (f"등급: 거리 값 T2(한눈에_v1 §3.3), 문화유산 구역 T1, 기준점 OSM T4. 기준점 = OSM '구경주역' 점. 이 점에서 8개 거리를 다시 재면 표와 ±0.1% 이내. 연속수치지도 '경주역' 2층 건물 중심은 이 점에서 {gap:.0f} m 북동쪽 — "
             "그 기준이면 황오동 고분 +16%·대릉원 +12%·황리단길 +6%(대안 m3b)")
mk.manifest_rows([dict(file=NAME, 설명=desc,
                       **{"원자료 경로": "archive/90_derived/public_profile_20260928.json(s1_neighbors) · 대지/(B020)연속수치지도_202609132098 N3A_B0010000·N3A_E0010001·N3P_H0040000 · archive/C_data/raw/vworld_uo301_city.geojson · raw/gj_tour_sites.geojson · processed/rail_stations_4326.geojson(OSM 기준점)",
                          "쪽/연도": "수치지도 2026-09-13 · V-World 2026-09", "가로x세로 px": f"{W}x{H}"},
                       비고=note_)])
print("저장", out, "문제", len(probs))
