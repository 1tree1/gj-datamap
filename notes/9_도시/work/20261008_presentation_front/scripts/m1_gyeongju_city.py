# -*- coding: utf-8 -*-
"""M1 경주시(S3) — 건물이 모인 땅(주거·상업·공업 용도지역) · 문화유산 구역·보존지역 · 철도 · 구 경주역 부지.

출력: assets/maps/m1_gyeongju_city.png (1800×2250 px, 세로 4:5, 300dpi, 흰 배경 불투명)
수치 재산정(건물이 모인 땅 4.4%, 문화유산 구역·보존지역 10.5%)은 같은 도형으로 다시 잰다 → research/context_maps_checks.csv
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from shapely.geometry import Point

import mapkit_context as mk
from mapkit_context import (C_BUILT, C_CITY_FILL, C_CITY_LINE, C_HER_CITY, C_RAIL, INK, INK2, RED, Frame, draw_lines,
                            draw_outline, draw_poly)

W, H = 1800, 2250
NAME = "m1_gyeongju_city.png"

emd, city = mk.load_city()
zoning = mk.load_zoning()
her = mk.load_heritage()
rails = mk.load_rails()
tour = mk.load_tour()
built, heritage = zoning["built"], her["all"]

# ── 범위: 시 경계가 가로를 채우고, 위는 조금 띄우고 아래는 범례·축척 자리로 비운다 ──
b = city.bounds
w_m = (b[2] - b[0]) * 1.06
h_m = w_m * H / W
cx = (b[0] + b[2]) / 2
cy = (b[3] + 0.045 * h_m) - h_m / 2
f = Frame(W, H, cx, cy, w_m, name="M1")
ax, K = f.ax, f.K

# ── 바탕 ──
draw_poly(ax, city, fc=C_CITY_FILL, z=1)
draw_poly(ax, heritage, fc=C_HER_CITY, z=2)
draw_poly(ax, built, fc=C_BUILT, z=3)
draw_outline(ax, heritage, color="#B9A6DB", lw=f.pt(0.35), z=4)            # 건물이 모인 땅과 겹친 곳에서도 구역이 보이게 가는 윤곽
draw_outline(ax, city, color=C_CITY_LINE, lw=f.pt(1.0), z=5)

# ── 철도: 운행선 실선 · 폐선 점선 ──
draw_lines(ax, rails["active"], C_RAIL, f.pt(1.5), z=8)
draw_lines(ax, rails["abandoned"], C_RAIL, f.pt(2.2), z=9, ls=(0, (0.05, 1.9)), cap="round")

# ── 지명 ──
emd_d = dict(emd)


def cluster_pt(name):
    """읍·면 안에서 건물이 모인 땅 가운데 가장 큰 덩어리의 대표점(없으면 읍·면 대표점)."""
    g = emd_d[name]
    bb = built.intersection(g)
    polys = list(mk.iter_polys(bb))
    if not polys:
        return g.representative_point()
    return max(polys, key=lambda p: p.area).representative_point()


def dot(x, y, ms=6.0, c=INK):
    ax.plot(x, y, "o", ms=f.pt(ms), mfc=c, mec="white", mew=f.pt(1.0), zorder=22)


# 읍·면 — 건물이 모인 덩어리 곁에 이름을 둔다
for nm, dx, dy, ha in (("안강읍", 0, 34, "center"), ("외동읍", 0, 34, "center"), ("감포읍", -26, 6, "right"), ("양남면", -26, 6, "right")):
    p = cluster_pt(nm)
    f.label(p.x, p.y, nm, size=10, color=INK2, weight="semibold", dx=dx, dy=dy, ha=ha)

# 불국사·보문 — 관광지 점
for nm, key, dx, dy, ha in (("불국사", "불국사", 20, 0, "left"), ("보문", "보문관광단지", 20, 0, "left")):
    p = tour[key]
    dot(p.x, p.y)
    f.label(p.x, p.y, nm, size=10, color=INK, weight="semibold", dx=dx, dy=dy, ha=ha)

# KTX 경주역(건천읍)
k = rails["gateways"]["경주역(KTX, 구 신경주역)"]
ax.plot(k.x, k.y, "s", ms=f.pt(7.0), mfc=C_RAIL, mec="white", mew=f.pt(1.0), zorder=22)
f.label(k.x, k.y, "KTX 경주역\n(건천읍)", size=10, color=INK, weight="semibold", dx=-24, dy=0, ha="right")

# 대상지 — 구 경주역 부지(빨강 점 + 라벨)
sx, sy = mk.OLD_STATION_OSM
ax.plot(sx, sy, "o", ms=f.pt(8.5), mfc=RED, mec="white", mew=f.pt(1.4), zorder=24)
f.label(sx, sy, "구 경주역 부지", size=11.5, color=RED, weight="bold", dx=-24, dy=34, ha="right", va="bottom")

# ── 범례·방위·축척 ──
f.legend([
    {"t": "patch", "fc": C_BUILT, "label": "건물이 모인 땅\n(주거·상업·공업 용도지역)"},
    {"t": "patch", "fc": C_HER_CITY, "ec": "#B9A6DB", "lw": 0.5, "label": "문화유산 구역·보존지역"},
    {"t": "line", "color": C_RAIL, "lw": 1.6, "label": "철도(운행선)"},
    {"t": "line", "color": C_RAIL, "lw": 2.2, "ls": (0, (0.05, 1.9)), "cap": "round", "label": "폐선"},
])
f.north_arrow()
f.scale_bar(10000, nseg=2, unit="km", div=1000)

probs = f.check_layout()

# ── 수치 재산정(같은 도형) ──
city_km2 = mk.km2(city)
rows = []
bk, hk = mk.km2(built), mk.km2(heritage)
rows.append(dict(map="M1", item="건물이 모인 땅(주거·상업·공업) 비율", doc_value="4.4% (58.1㎢)", recomputed=f"{bk / city_km2 * 100:.2f}% ({bk:.2f}㎢)",
                 diff=f"{bk / city_km2 * 100 - 4.4:+.2f}%p", note=f"시 경계 {city_km2:,.2f}㎢(V-World 읍면동 합집합) 대비. 공식 면적 1,324.99㎢ 대비는 {bk / 1324.99 * 100:.2f}%"))
rows.append(dict(map="M1", item="문화유산 구역·보존지역 비율", doc_value="10.5% (138.4㎢)", recomputed=f"{hk / city_km2 * 100:.2f}% ({hk:.2f}㎢)",
                 diff=f"{hk / city_km2 * 100 - 10.5:+.2f}%p", note=f"공식 면적 대비 {hk / 1324.99 * 100:.2f}%"))
rows.append(dict(map="M1", item="국가지정문화유산 구역 면적", doc_value="34.8㎢", recomputed=f"{mk.km2(her['nat']):.2f}㎢", diff=f"{mk.km2(her['nat']) - 34.8:+.2f}㎢", note=""))
rows.append(dict(map="M1", item="문화유산 구역 ÷ 건물이 모인 땅", doc_value="약 2.4배", recomputed=f"{hk / bk:.2f}배", diff=f"{hk / bk - 2.4:+.2f}", note=""))
ov = built.intersection(heritage)
rows.append(dict(map="M1", item="(참고) 건물이 모인 땅 중 문화유산 구역과 겹친 면적", doc_value="—", recomputed=f"{mk.km2(ov):.2f}㎢ ({mk.km2(ov) / bk * 100:.1f}%)", diff="", note="지도에서 겹친 곳은 회색이 위에 그려진다"))

# 픽셀로도 잰다 — 같은 범위·같은 크기로 도형만 검정으로 그려 면적을 센다(그림의 좌표 변환·축척 점검)
a_city = mk.raster_area_m2(W, H, cx, cy, w_m, city) / 1e6
a_built = mk.raster_area_m2(W, H, cx, cy, w_m, built) / 1e6
a_her = mk.raster_area_m2(W, H, cx, cy, w_m, heritage) / 1e6
rows.append(dict(map="M1", item="지도 픽셀 재산정: 시 경계 면적", doc_value=f"{city_km2:,.2f}㎢(도형)", recomputed=f"{a_city:,.2f}㎢", diff=f"{(a_city / city_km2 - 1) * 100:+.2f}%",
                 note=f"{W}×{H}px, {1 / f.ppm:.1f}m/px, 안티앨리어싱 켠 검정 렌더의 어둡기 합"))
rows.append(dict(map="M1", item="지도 픽셀 재산정: 건물이 모인 땅 / 시 경계", doc_value="4.4%", recomputed=f"{a_built / a_city * 100:.2f}% ({a_built:.2f}㎢)", diff=f"{a_built / a_city * 100 - 4.4:+.2f}%p", note="같은 렌더"))
rows.append(dict(map="M1", item="지도 픽셀 재산정: 문화유산 구역·보존지역 / 시 경계", doc_value="10.5%", recomputed=f"{a_her / a_city * 100:.2f}% ({a_her:.2f}㎢)", diff=f"{a_her / a_city * 100 - 10.5:+.2f}%p", note="같은 렌더"))
mk.append_checks(rows)
for r in rows:
    print(r["item"], "|", r["doc_value"], "→", r["recomputed"], r["diff"])

out = f.save(mk.OUT / NAME)
mk.manifest_rows([dict(file=NAME, 설명="M1 경주시(S3) 맥락 — 건물이 모인 땅·문화유산 구역·보존지역·철도(운행선/폐선)·구 경주역 부지",
                       **{"원자료 경로": "archive/C_data/raw/vworld_emd_gj.geojson(시 경계) · vworld_uq111_city.geojson(용도지역) · vworld_uo301_city.geojson(문화유산) · archive/C_data/processed/rail_active_4326·rail_abandoned_4326·gateways_4326.geojson · raw/gj_tour_sites.geojson",
                          "쪽/연도": "V-World 2026-09 수집 · OSM 철도 2026-09-21(T4)", "가로x세로 px": f"{W}x{H}"},
                       비고="S3. 등급: 용도지역·문화유산 구역 T1(V-World 도형, 도시지역만 — 관리·농림·자연환경보전 제외), 시 경계·관광지 위치 T2, 철도·KTX역 T4(OSM·V-World 장소검색). 건물이 모인 땅 4.4%·문화유산 10.5%는 같은 도형으로 재산정해 일치. 출처 줄은 슬라이드에서 따로")])
print("저장", out, "문제", len(probs))
