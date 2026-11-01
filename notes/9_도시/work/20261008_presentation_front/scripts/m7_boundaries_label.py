# -*- coding: utf-8 -*-
"""M7 경계(S1) — 고시 구역 156,460㎡(파랑) · 본 계획 경계 218,478㎡(빨강) · 고시 구역 밖 계획 경계(빗금) · 면적·길이·폭 라벨.

출력: assets/maps/m7_boundaries.png (1800×2400 px, 세로 3:4, 300dpi, 흰 배경 불투명)
79,438㎡(시 구상 면적)는 범위가 정의돼 있지 않아 그리지 않고, 범례 아래에 문구로만 적는다.
도형: 고시 구역 = 지형도면 추출 도형(archive/C_data/processed/gosi2026-8_zone_5187.geojson, 도형 면적 158,472㎡ · 결정조서 156,460㎡)
      본 계획 경계 = work/20261005_boundary_check/user_boundary_current_5187.geojson (218,478㎡)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from shapely.geometry import LineString, box
from shapely.ops import unary_union
from matplotlib.collections import LineCollection

import mapkit_context as mk
from mapkit_context import BLUE, C_BLD1, C_WATER, GRAY, INK, RED, Frame, draw_outline, draw_poly, draw_polys_fast

W, H = 1800, 2400
NAME = "m7_boundaries.png"
HALF_W = 1012.5 / 2                         # 동서 약 1,000 m — 3:4 비율에 맞춰 1,012.5 m
CX, CY = 219731.0, 360987.0                  # 두 경계를 합친 범위의 가운데(동서는 범례 자리를 위해 서쪽으로 60 m 치우침)
f = Frame(W, H, CX, CY, 2 * HALF_W, name="M7")
ax, K = f.ax, f.K
win = f.win

zone = mk.gosi_zone()
plan = mk.plan_boundary()
out_zone = plan.difference(zone)            # 고시 구역 밖 계획 경계
pieces = sorted([p for p in mk.iter_polys(out_zone) if p.area >= 100], key=lambda p: -p.area)

# ── 바탕: 하천 · 건물(단색) ──
rv = unary_union([g.intersection(win) for g in mk.water_in(win)])
draw_poly(ax, rv, fc=C_WATER, z=1)
draw_polys_fast(ax, [g for g, _ in mk.buildings_in(win)], fc=C_BLD1, z=3)

# ── 고시 구역: 파랑 선 2.4pt, 채움 투명 10% ──
draw_poly(ax, zone, fc=BLUE, alpha=0.10, z=5)
draw_outline(ax, zone, color=BLUE, lw=f.pt(2.4), z=8)

# ── 고시 구역 밖 계획 경계: 연한 빨강 해칭(45°, 간격 7 m) + 아주 옅은 채움 ──
for p in pieces:
    draw_poly(ax, p, fc=RED, alpha=0.06, z=5.5)
segs = [np.asarray(l.coords)[:, :2] for p in pieces for l in mk.hatch_lines(p, 7.0, 45.0)]
ax.add_collection(LineCollection(segs, colors=RED, linewidths=f.pt(0.7), alpha=0.45, zorder=6, capstyle="butt"))

# ── 본 계획 경계: 빨강 선 2.8pt, 채움 없음 ──
draw_outline(ax, plan, color=RED, lw=f.pt(2.8), z=9)

# ── 치수선 ──
zb, pb = zone.bounds, plan.bounds                      # (xmin, ymin, xmax, ymax)


def widest_chord(g):
    best = (0.0, None)
    for y in np.arange(g.bounds[1] + 1, g.bounds[3], 1.0):
        seg = g.intersection(LineString([(g.bounds[0] - 5, y), (g.bounds[2] + 5, y)]))
        if seg.length > best[0]:
            xs = [c[0] for s in mk.iter_lines(seg) for c in s.coords]
            best = (seg.length, (y, min(xs), max(xs)))
    return best


zw, (zy, zx0, zx1) = widest_chord(zone)
pw, (py_, px0, px1) = widest_chord(plan)
ns_zone, ns_plan = zb[3] - zb[1], pb[3] - pb[1]


def dim(p0, p1, color, text, rot=0, dx=0, dy=0, ha="center", va="center", size=10, key=None, tick=11, frac=0.5):
    """치수선: 양쪽 화살표 + 끝 눈금 + 라벨(흰 외곽). frac = 라벨을 선의 어디(0~1)에 둘지."""
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="<->,head_length=0.35,head_width=0.18", color=color, lw=f.pt(1.3), shrinkA=0, shrinkB=0), zorder=15)
    t = (p1[0] - p0[0], p1[1] - p0[1])
    n = np.hypot(*t)
    nx, ny = -t[1] / n, t[0] / n                        # 선에 수직 방향
    for q in (p0, p1):
        ax.plot([q[0] - nx * tick / f.ppm, q[0] + nx * tick / f.ppm], [q[1] - ny * tick / f.ppm, q[1] + ny * tick / f.ppm], color=color, lw=f.pt(1.3), zorder=15, solid_capstyle="butt")
    mx, my = p0[0] + t[0] * frac, p0[1] + t[1] * frac
    return f.label(mx, my, text, size=size, color=color, weight="bold", rot=rot, dx=dx, dy=dy, ha=ha, va=va, key=key or text, z=30)


# 남북: 서쪽에 나란히(바깥 = 계획 경계, 안쪽 = 고시 구역), 라벨은 선 왼쪽
XZ, XP = zb[0] - 22, zb[0] - 62
dim((XZ, zb[1]), (XZ, zb[3]), BLUE, f"남북 {ns_zone:,.0f} m", rot=90, dx=-12, ha="right", key="zone-ns")
dim((XP, pb[1]), (XP, pb[3]), RED, f"남북 {ns_plan:,.0f} m", rot=90, dx=-12, ha="right", key="plan-ns")
# 동서: 고시 구역 최대 폭(273 m)과 계획 경계 최대 폭(300 m)
dim((zx0, zy), (zx1, zy), BLUE, f"동서 최대 {zw:,.0f} m", dy=24, va="bottom", key="zone-ew")
dim((px0, py_), (px1, py_), RED, f"동서 {pw:,.0f} m", dy=24, va="bottom", key="plan-ew", frac=0.75)    # 고시 구역 좁은 목(파랑 선)을 피해 오른쪽 해칭 위에

# ── 면적 라벨 ──
# 고시 구역: 구역 안 넓은 곳(남북 가운데)에
zc = zone.intersection(box(zb[0] - 1, 360640, zb[2] + 1, 361200))
zlab = max(mk.iter_polys(zc), key=lambda p: p.area).representative_point()
f.label(zlab.x - 8, zlab.y + 40, f"고시 구역\n{mk.GOSI_AREA_M2:,}㎡", size=11.5, color=BLUE, weight="bold", key="zone-area", linespacing=1.15)
# 본 계획 경계 · 고시 구역 밖: 오른쪽 바깥에 두고 가는 선으로 잇는다


def leader(x0, y0, x1, y1, color=RED):
    """(x0,y0)=가리키는 점(점 찍음) → (x1,y1)=라벨 쪽 끝."""
    ax.plot([x0, x1], [y0, y1], color=color, lw=f.pt(0.9), zorder=14, solid_capstyle="round")
    ax.plot(x0, y0, "o", ms=f.pt(4.5), mfc=color, mec="white", mew=f.pt(0.8), zorder=16)


big = pieces[0]                                         # 가장 큰 해칭 조각(동쪽 띠 + 북동 삼각 + 남동 블록)
out_area = out_zone.area
LX = pb[2] + 46                                         # 라벨 왼쪽 끝(계획 경계 동쪽 가장자리에서 46 m)
# 본 계획 경계 라벨 — 동쪽 가장자리의 한 점을 가리킨다
PY = 361130
pe_ = plan.boundary.intersection(LineString([(pb[2] - 80, PY), (pb[2] + 20, PY)]))
pex = max(g.x for g in getattr(pe_, "geoms", [pe_]) if g.geom_type == "Point")        # 가로선과 경계의 교점(맨 오른쪽)
f.label(LX, PY, f"분석 범위\n{mk.PLAN_AREA_M2:,}㎡", size=11.5, color=RED, weight="bold", ha="left", va="center", key="plan-area", linespacing=1.15, dx=6)
leader(pex, PY, LX - 4, PY)
# 고시 구역 밖 라벨 — 남동 해칭 블록 안의 한 점을 가리킨다
HY = 360700
tgt = big.intersection(box(pb[2] - 120, HY - 25, pb[2] + 5, HY + 25))
tp = tgt.representative_point()
f.label(LX, HY, f"고시 구역 밖\n약 {out_area:,.0f}㎡", size=10.5, color=RED, weight="bold", ha="left", va="center", key="hatch-area", linespacing=1.15, dx=6)
leader(tp.x, tp.y, LX - 4, HY)

# ── 범례·방위·축척 ──
f.legend([
    {"t": "patch", "fc": BLUE, "alpha": 0.10, "ec": BLUE, "lw": 2.4, "label": f"고시 구역 {mk.GOSI_AREA_M2:,}㎡"},
    {"t": "line", "color": RED, "lw": 2.8, "label": f"분석 범위 {mk.PLAN_AREA_M2:,}㎡"},
    {"t": "patch", "fc": RED, "alpha": 0.06, "hatch": True, "hc": "#E98A8C", "ec": "none", "label": f"고시 구역 밖 분석 범위 약 {out_area:,.0f}㎡"},
], note=f"시 구상 면적 {mk.SIGU_AREA_M2:,}㎡ — 범위 미정의")
f.north_arrow()
f.scale_bar(200, nseg=2, unit="m")
probs = f.check_layout()

# ── 수치 재산정 ──
rows = []
a_zone, a_plan, a_out = zone.area, plan.area, out_zone.area
px_zone = mk.raster_area_m2(W, H, CX, CY, 2 * HALF_W, zone)
px_plan = mk.raster_area_m2(W, H, CX, CY, 2 * HALF_W, plan)
px_out = mk.raster_area_m2(W, H, CX, CY, 2 * HALF_W, unary_union(pieces))
rows += [
    dict(map="M7", item="고시 구역 면적", doc_value="156,460㎡ (결정조서 T1)", recomputed=f"{a_zone:,.0f}㎡ (지형도면 추출 도형)", diff=f"{(a_zone / 156460 - 1) * 100:+.2f}%",
         note=f"도면을 좌표에 맞춰 뽑은 도형이 결정조서보다 {a_zone - 156460:,.0f}㎡ 큼. 라벨은 결정조서 값. 지도 픽셀 렌더로 잰 값 {px_zone:,.0f}㎡"),
    dict(map="M7", item="본 계획 경계 면적", doc_value="218,478㎡", recomputed=f"{a_plan:,.1f}㎡", diff=f"{a_plan - 218478:+.1f}㎡", note=f"지도 픽셀 렌더로 잰 값 {px_plan:,.0f}㎡({(px_plan / a_plan - 1) * 100:+.2f}%)"),
    dict(map="M7", item="고시 구역 밖 계획 경계 면적", doc_value="≈60,498㎡", recomputed=f"{a_out:,.0f}㎡ (조각 {len(pieces)}개 ≥100㎡: " + " · ".join(f"{p.area:,.0f}" for p in pieces) + ")",
         diff=f"{a_out - 60498:+,.0f}㎡", note=f"계획 경계 − 고시 구역 도형. 결정조서 면적(156,460㎡) 기준으로 보정하면 약 {a_plan - 156460 + (zone.difference(plan).area):,.0f}㎡. 지도 픽셀 렌더 {px_out:,.0f}㎡. 고시 구역 도형 중 계획 경계 밖 {zone.difference(plan).area:,.0f}㎡"),
    dict(map="M7", item="고시 구역 남북 길이", doc_value="약 923 m", recomputed=f"{ns_zone:,.1f} m", diff=f"{ns_zone - 923:+.1f} m", note="도형 바운딩박스 높이"),
    dict(map="M7", item="고시 구역 동서 최대 폭", doc_value="약 273 m", recomputed=f"{zw:,.1f} m (y={zy:,.0f})", diff=f"{zw - 273:+.1f} m", note="가로 절단선 1 m 간격 중 최대"),
    dict(map="M7", item="계획 경계 남북 길이", doc_value="약 945 m", recomputed=f"{ns_plan:,.1f} m", diff=f"{ns_plan - 945:+.1f} m", note="도형 바운딩박스 높이"),
    dict(map="M7", item="계획 경계 동서 폭", doc_value="약 300 m", recomputed=f"{pw:,.1f} m (y={py_:,.0f}) · 바운딩박스 {pb[2] - pb[0]:,.1f} m", diff=f"{pw - 300:+.1f} m", note="가로 절단선 최대 폭"),
    dict(map="M7", item="지도 안 치수선 길이(그린 화살표)", doc_value="—", recomputed=f"고시 남북 {ns_zone * f.ppm:,.0f}px · 계획 남북 {ns_plan * f.ppm:,.0f}px · 고시 동서 {zw * f.ppm:,.0f}px · 계획 동서 {pw * f.ppm:,.0f}px",
         diff="", note=f"{W}×{H}px, {1 / f.ppm:.3f} m/px"),
    dict(map="M7", item="(참고) 79,438㎡ ÷ 고시 구역", doc_value="51%", recomputed=f"{mk.SIGU_AREA_M2 / 156460 * 100:.1f}%", diff="", note="79,438㎡는 범위 미정의라 그리지 않음"),
]
mk.append_checks(rows)
for r in rows:
    print(r["item"], "|", r["doc_value"], "→", r["recomputed"], r["diff"])

out = f.save(mk.OUT / NAME)
mk.manifest_rows([dict(file=NAME, 설명="M7 경계(S1) — 고시 구역 156,460㎡(파랑)·본 계획 경계 218,478㎡(빨강)·고시 구역 밖 약 60,498㎡(해칭)·남북·동서 치수",
                       **{"원자료 경로": "archive/C_data/processed/gosi2026-8_zone_5187.geojson · work/20261005_boundary_check/user_boundary_current_5187.geojson · 대지/(B020)연속수치지도_202609132098 N3A_B0010000·N3A_E0010001",
                          "쪽/연도": "고시 제2026-8호(2026-01-22) 도면 좌표등록 · 수치지도 2026-09-13", "가로x세로 px": f"{W}x{H}"},
                       비고=f"S1. 등급: 고시 구역 T1(고시 제2026-8호 도면 좌표등록·결정조서 면적), 계획 경계=사용자 라이노 경계, 건물·하천 T2. 고시 구역 도형은 도면 추출(158,472㎡)이라 결정조서 156,460㎡보다 {a_zone - 156460:,.0f}㎡(+{(a_zone / 156460 - 1) * 100:.1f}%) 큼. 계획 경계 밖 고시 구역 {zone.difference(plan).area:,.0f}㎡. 79,438㎡는 범위 미정의로 미표시")])
print("저장", out, "문제", len(probs))
