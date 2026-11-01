# -*- coding: utf-8 -*-
"""M9 철도축(S3) — 경주시 철도: 폐선(2021 이설 후) 점선 강조 · 운행선 실선 · 폐역 · KTX 경주역(건천) · 구 경주역 부지.

출력: assets/maps/m9_rail_axis_S3.png (2000×1500 px, 가로 4:3, 300dpi, 흰 배경 불투명)
자료: OSM 철도(rail_abandoned_4326 · rail_active_4326, T4, 2026-09-21 수집)·역 점(rail_stations_4326, OSM·위키 T4)·KTX 역(gateways_4326, V-World 장소검색).
한계(보고서에 적음): ① 역 점이 4개뿐이라 폐역 17개소(2023.04 폐철도 기본구상, 원문 미확보) 중 위치가 확인되는 것은 3개소다.
  ② OSM 수집 질의 범위(pipeline/build_web_civic_transit.py: 위도 35.74–35.98, 경도 129.08–129.40 — 시 면적의 절반가량)에 걸친 선만 있어
     영천·안강·울산 쪽 끝이 시 경계까지 이어지지 않는다(끝에서 시 경계까지 직선 1.5~3.2 km).
  ③ 선분 길이 합 78.1 km에는 구내 병행선·금장삼각선이 들어 있다(병행선을 겹치면 약 63 km).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from shapely.geometry import LineString, Point, box
from shapely.ops import linemerge, unary_union

import mapkit_context as mk
from mapkit_context import (C_CITY_FILL, C_CITY_LINE, C_RAIL, GRAY, INK, INK2, RED, Frame, draw_lines, draw_outline, draw_poly)

W, H = 2000, 1500
NAME = "m9_rail_axis_S3.png"

emd, city = mk.load_city()
rails = mk.load_rails()
act, aban = rails["active"], rails["abandoned"]
gw = rails["gateways"]
st = {p["name"]: (g, p) for g, p in rails["stations"]}
tour = mk.load_tour()

# ── 범위: 시 경계가 세로를 채우고, 왼쪽에 범례 자리를 비운다 ──
b = city.bounds
h_m = (b[3] - b[1]) + 2 * 1700
w_m = h_m * W / H
xmin = b[0] - 16800
cx, cy = xmin + w_m / 2, (b[1] + b[3]) / 2
f = Frame(W, H, cx, cy, w_m, name="M9")
ax, K = f.ax, f.K

# ── 바탕 ──
draw_poly(ax, city, fc=C_CITY_FILL, z=1)
draw_outline(ax, city, color=C_CITY_LINE, lw=f.pt(1.0), z=2)

# ── 철도: 운행선 실선 · 폐선 점선(굵게) ──
draw_lines(ax, act, C_RAIL, f.pt(1.7), z=8)
ABAN_LS, ABAN_LW = (0, (0.05, 1.55)), 3.4
draw_lines(ax, aban, C_RAIL, f.pt(ABAN_LW), z=9, ls=ABAN_LS, cap="round")

# ── 역·대상지 ──
OPEN_MS = 7.2


def closed_station(g):
    ax.plot(g.x, g.y, "o", ms=f.pt(OPEN_MS), mfc="white", mec=INK, mew=f.pt(1.7), zorder=22)


def active_station(g):
    ax.plot(g.x, g.y, "s", ms=f.pt(7.0), mfc=C_RAIL, mec="white", mew=f.pt(1.2), zorder=22)


g_old, _ = st["옛 서경주역 (금장, 폐역 2021.12)"]
g_bul, _ = st["불국사역 (폐역 2021.12)"]
g_new, _ = st["서경주역 (신, 현곡면 하구리)"]
g_ktx = gw["경주역(KTX, 구 신경주역)"]
closed_station(g_old)
closed_station(g_bul)
active_station(g_new)
active_station(g_ktx)
sx, sy = mk.OLD_STATION_OSM
ax.plot(sx, sy, "o", ms=f.pt(9.0), mfc=RED, mec=INK, mew=f.pt(1.7), zorder=24)      # 구 경주역도 폐역이라 폐역 기호(고리)에 대상지 색(빨강)을 채운다

# ── 지명(읍) ──
emd_d = dict(emd)
zoning = mk.load_zoning()


def cluster_pt(name):
    g = emd_d[name]
    polys = list(mk.iter_polys(zoning["built"].intersection(g)))
    return max(polys, key=lambda p: p.area).representative_point() if polys else g.representative_point()


for nm, dx, dy, ha in (("안강읍", -26, 4, "right"),):             # 건천읍은 'KTX 경주역(건천읍)' 라벨이 대신한다
    p = cluster_pt(nm)
    f.label(p.x, p.y, nm, size=10, color=GRAY, weight="semibold", dx=dx, dy=dy, ha=ha, key=nm)

# ── 폐선 끝 방향(자료가 끝나는 곳) ──
u_ab = unary_union(aban)
ends = {"영천 방면": (204845, 365799), "안강·포항 방면": (220702, 376232), "울산 방면": (228317, 348927)}
END_LAB = {"영천 방면": (-18, 0, "right", "center"), "안강·포항 방면": (20, 8, "left", "bottom"), "울산 방면": (0, -22, "center", "top")}
for nm, (x, y) in ends.items():
    dx, dy, ha, va = END_LAB[nm]
    f.label(x, y, nm, size=9.5, color=INK2, weight="medium", dx=dx, dy=dy, ha=ha, va=va, key=nm)

# ── 범례·방위·축척 ──
f.legend([
    {"t": "line", "color": C_RAIL, "lw": 1.7, "label": "운행선"},
    {"t": "line", "color": C_RAIL, "lw": ABAN_LW, "ls": ABAN_LS, "cap": "round", "label": "폐선(2021.12 이설 이후)"},
    {"t": "dot", "color": "white", "ec": INK, "ms": OPEN_MS, "mew": 1.7, "label": "폐역(위치 확인 3개소)"},
    {"t": "dot", "color": C_RAIL, "marker": "s", "ms": 7.0, "label": "운행 중인 역"},
    {"t": "dot", "color": RED, "ec": INK, "ms": 9.0, "mew": 1.7, "label": "구 경주역 부지(폐역)"},
])
f.north_arrow()
f.scale_bar(10000, nseg=2, unit="km", div=1000)

# ── 역 이름: 자동 배치(선·점·범례를 피해) ──
pt_stations = [("구 경주역 부지", (sx, sy), RED, "bold", 11.0), ("옛 서경주역\n(금장)", (g_old.x, g_old.y), INK, "semibold", 10),
               ("서경주역", (g_new.x, g_new.y), INK, "semibold", 10), ("불국사역", (g_bul.x, g_bul.y), INK, "semibold", 10),
               ("KTX 경주역\n(건천읍)", (g_ktx.x, g_ktx.y), INK, "semibold", 10)]
mrg = linemerge(unary_union(act + aban))
line_px = [[f.to_px(*c) for c in l.coords] for l in (mrg.geoms if mrg.geom_type == "MultiLineString" else [mrg])]
dots = [(*f.to_px(*xy), 16) for _, xy, *_ in pt_stations]
fixed = [f.label_box(t) for _, t in f.labels]
placed = f.auto_place([dict(key=nm, text=nm, anchor=xy, size=sz, weight=w, linespacing=1.12) for nm, xy, c, w, sz in pt_stations],
                      lines=line_px, dots=dots, boxes=[f.boxes["legend"], f.boxes["north"], f.boxes["scale"], *fixed],
                      radii=(22, 50, 90), restarts=30)
for nm, xy, c, w, sz in pt_stations:
    pl = placed[nm]
    f.label(xy[0], xy[1], nm, size=sz, color=c, weight=w, dx=pl["dx"], dy=pl["dy"], ha=pl["ha"], va=pl["va"], key=nm, linespacing=1.12)
    print(f"  {nm.replace(chr(10), ' '):14s} r={pl['r']:>3} {pl['ha']:>6}/{pl['va']:<6} 벌점 {pl['penalty']:.0f}")
    if pl["leader"]:
        px, py = f.to_px(*xy)
        bx = pl["box"]
        qx, qy = min(max(px, bx[0] + 5), bx[2] - 5), min(max(py, bx[1] + 5), bx[3] - 5)
        f.ov.plot([px, qx], [py, qy], color=INK, lw=f.pt(0.8), zorder=21)

probs = f.check_layout()

# ── 수치 재산정: 폐선 길이 · 폐역 수 ──
rows = []
raw = sum(g.length for g in aban)
named = {}
for g, p in zip(aban, rails["abandoned_props"]):
    k = (p["name"] or "(무명)") + "/" + p["railway"]
    named[k] = named.get(k, 0) + g.length
yard = sum(v for k, v in named.items() if k.startswith("(무명)"))
tri = sum(v for k, v in named.items() if k.startswith("금장삼각선"))
eq = {w: unary_union([g.buffer(w / 2, cap_style=2) for g in aban]).area / w for w in (10, 20, 40)}


def components(tol):
    """tol m 이내로 맞닿은 선분을 한 덩어리로 묶었을 때 덩어리별 길이(km, 큰 순)."""
    u = unary_union([g.buffer(tol) for g in aban])
    parts = list(u.geoms) if u.geom_type == "MultiPolygon" else [u]
    return sorted((sum(g.intersection(p.buffer(1)).length for g in aban) / 1000 for p in parts), reverse=True)


c3, c30 = components(3), components(30)
act_len = sum(g.length for g in act)
bd = city.boundary
gap_ends = {k: round(bd.distance(Point(*xy))) for k, xy in ends.items()}
rows += [
    dict(map="M9", item="폐선 길이 — OSM 선분 길이 합", doc_value="80.3 km (폐철도 기본구상 2023.04, T2 원문 미확보)", recomputed=f"{raw / 1000:,.1f} km (선분 {len(aban)}개)", diff=f"{(raw / 80300 - 1) * 100:+.1f}%",
         note="구내 병행선·금장삼각선 포함. 값이 80.3 km에 가까운 것은 병행선 중복(+)과 자료 끝 절단(−)이 맞물린 결과라 검증값으로 쓸 수 없음"),
    dict(map="M9", item="폐선 길이 — 이름 있는 선(동해선·중앙선·구 동해선·금장삼각선)만", doc_value="80.3 km", recomputed=f"{(raw - yard) / 1000:,.1f} km", diff=f"{((raw - yard) / 80300 - 1) * 100:+.1f}%",
         note="이름이 비어 있는 선분 " + f"{yard / 1000:.1f} km(구내선·측선 추정)를 뺀 값. " + " · ".join(f"{k} {v / 1000:.1f}" for k, v in sorted(named.items(), key=lambda kv: -kv[1])) + f" (금장삼각선 {tri / 1000:.1f} km 포함)"),
    dict(map="M9", item="폐선 길이 — 병행선을 겹친 단선 환산", doc_value="80.3 km", recomputed=f"{eq[20] / 1000:.1f} km (폭 20 m 버퍼 합집합 ÷ 20 m · 10 m {eq[10] / 1000:.1f} · 40 m {eq[40] / 1000:.1f})",
         diff=f"{(eq[20] / 80300 - 1) * 100:+.1f}%", note="구내 병행선을 한 줄로 쳤을 때 본선 길이 추정"),
    dict(map="M9", item="폐선 연결 상태", doc_value="—", recomputed=f"3 m 이내로 이어진 덩어리 {len(c3)}개(가장 큰 {c3[0]:.1f} km) → 30 m 이내로 이으면 {len(c30)}개({' + '.join(f'{v:.1f}' for v in c30)} km)",
         diff="", note="OSM 폐선은 사실상 한 줄의 축으로 이어진다(틈 30 m 이하)"),
    dict(map="M9", item="자료가 끝나는 곳에서 시 경계까지 직선거리", doc_value="—", recomputed=" · ".join(f"{k} {v:,} m" for k, v in gap_ends.items()),
         diff="", note=f"OSM 수집 범위(위도 35.74–35.98 등)에서 끊긴 끝이 시 경계 쪽으로 이어진다면 직선으로만 잡아도 {sum(gap_ends.values()) / 1000:.1f} km 이상이 지도에 없다. 그래서 80.3 km와 직접 비교 불가(원문 미확보)"),
    dict(map="M9", item="운행선 길이(OSM, 참고)", doc_value="—", recomputed=f"{act_len / 1000:,.1f} km", diff="", note="경부고속선·동해선·중앙선·건천연결선 등 선분 합"),
    dict(map="M9", item="폐역 수 — 위치가 확인된 곳", doc_value="17개소 (2023.04 폐철도 기본구상, T2 원문 미확보)", recomputed="3개소 (구경주역·옛 서경주역(금장)·불국사역)", diff="-14",
         note="rail_stations_4326.geojson에 역 점 4개(폐역 3 + 운행 서경주역 1). 나머지 14개소 위치·이름은 자료 없음 → 정보공개 청구 대상(gaps.md)"),
]
mk.append_checks(rows)
for r in rows:
    print(r["item"], "|", r["doc_value"], "→", r["recomputed"], r["diff"])

out = f.save(mk.OUT / NAME)
mk.manifest_rows([dict(file=NAME, 설명="M9 철도축(S3) — 경주시 운행선(실선)·폐선(점선)·폐역 3개소·운행역·KTX 경주역(건천읍)·구 경주역 부지",
                       **{"원자료 경로": "archive/C_data/processed/rail_abandoned_4326.geojson · rail_active_4326.geojson · rail_stations_4326.geojson · gateways_4326.geojson · raw/vworld_emd_gj.geojson(시 경계)",
                          "쪽/연도": "OSM Overpass 2026-09-21(T4) · V-World 장소검색", "가로x세로 px": f"{W}x{H}"},
                       비고=f"S3. 폐역 17개소는 자료에 없음(위치 확인 3개소만 표시). 폐선 OSM 선분 합 {raw / 1000:.1f} km(병행선 포함, 단선 환산 {eq[20] / 1000:.0f} km)로 문헌 80.3 km 검증 불가 — 영천·안강·울산 쪽 끝이 OSM 수집 범위에서 끊김(최소 {sum(gap_ends.values()) / 1000:.0f} km 누락 추정). 선로는 T4(OSM)")])
print("저장", out, "문제", len(probs))
