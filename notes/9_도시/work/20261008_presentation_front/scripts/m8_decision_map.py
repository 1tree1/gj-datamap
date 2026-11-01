# -*- coding: utf-8 -*-
"""M8 결정도 지도 — 고시 2026-8호 지구단위계획 결정도 블록을 용도별로 칠한다. 1800x2400 px, 틀은 M6 과 같다
(중심 219,740 / 360,940, 동서 900m x 남북 1,200m → 2 px/m).

면적 [T1]: 경주시 고시 제2026-8호(2026-01-22) 결정조서 — 근린공원 55,415, 상업 42,031, 공공청사 24,987, 문화 9,770, 주차장 5,756,
           도로 18,501(총 4노선 852m), 고시 구역 156,460㎡.
지도 도형: archive/C_data/processed/gosi2026-8_blocks_5187.geojson (지형도면고시도 11·12장 채움색 벡터화, 5176→5187),
           gosi2026-8_zone_5187.geojson (쇄선 추출, 158,472㎡). 도형 면적은 조서와 ±수 %로 다르다(research/data_series/m8_blocks_check.csv).
출력: assets/maps/m8_decision_map.png, research/data_series/m8_blocks_check.csv
실행: export PYTHONUTF8=1 PYTHONIOENCODING=utf-8; python m8_decision_map.py
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapkit_analysis as mk
from mapkit_analysis import *  # noqa: F401,F403

W, H = 1800, 2400
CX, CY, WM = 219740.0, 360940.0, 900.0
PLAN, ZONE = plan_boundary(), gosi_zone()
FRAME = box(CX - WM / 2, CY - WM * H / W / 2, CX + WM / 2, CY + WM * H / W / 2)

# 용도별 색 (지시)
USE = [   # (cls, 이름, 색, 조서 면적㎡)
    ("park", "근린공원", C_GREEN, 55415),
    ("commercial", "상업", C_SOUTH, 42031),
    ("civic", "공공청사", C_NORTH, 24987),
    ("culture", "문화", C_CENTER, 9770),
    ("parking", "주차장", C_PARKING, 5756),
]
ZONE_DOC = 156460.0
ROAD_DOC = 18501.0
blocks = gosi_blocks()

# ── 지도 데이터로 재산정한 면적 vs 조서 ──
by = {}
for g, p in blocks:
    by.setdefault(p["cls"], []).append((g, p))
rows = []
for cls, nm, col, doc in USE:
    a_map = sum(g.area for g, p in by[cls])
    a_gosi_blocks = sum(p["gosi_area_m2"] for g, p in by[cls])
    rows.append((nm, doc, a_gosi_blocks, a_map))
blocks_map = sum(g.area for g, p in blocks)
blocks_doc = sum(r[1] for r in rows)
road_map = ZONE.area - blocks_map
road_from_doc = ZONE_DOC - blocks_doc
with open(DATA_SERIES / "m8_blocks_check.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["용도", "문서 면적(㎡) [T1 결정조서]", "문서 비율(%, 고시 구역 156,460㎡ 기준)", "지도 도형 면적(㎡)", "지도 도형 비율(%, 도면 추출 구역 기준)",
                "지도/문서 차(%)", "블록 속성의 조서 면적 합(㎡)", "메모"])
    for nm, doc, ag, am in rows:
        w.writerow([nm, f"{doc:.0f}", f"{100*doc/ZONE_DOC:.2f}", f"{am:.1f}", f"{100*am/ZONE.area:.2f}", f"{100*(am/doc-1):+.1f}", f"{ag:.0f}", ""])
    w.writerow(["도로", f"{ROAD_DOC:.0f}", f"{100*ROAD_DOC/ZONE_DOC:.2f}", f"{road_map:.1f}", f"{100*road_map/ZONE.area:.2f}", f"{100*(road_map/ROAD_DOC-1):+.1f}",
                f"{road_from_doc:.0f}", "문서: 조서 도로 4노선 852m 18,501㎡(= 156,460 − 블록 합 137,959). 지도: 도면 추출 구역 − 블록 도형 합(블록 도형이 작게 뜨고 구역이 크게 떠서 차가 크다)"])
    w.writerow(["블록 합계", f"{blocks_doc:.0f}", f"{100*blocks_doc/ZONE_DOC:.2f}", f"{blocks_map:.1f}", f"{100*blocks_map/ZONE.area:.2f}", f"{100*(blocks_map/blocks_doc-1):+.1f}", "", ""])
    w.writerow(["고시 구역", f"{ZONE_DOC:.0f}", "100.00", f"{ZONE.area:.1f}", "100.00", f"{100*(ZONE.area/ZONE_DOC-1):+.1f}", "", "도면 추출 구역(쇄선) vs 조서 면적"])
    w.writerow(["주거용지", "0 (결정도에 없음)", "0", f"{sum(g.area for g, p in blocks if p['cls'] == 'residential'):.0f}", "0", "", "", "블록 10개 중 주거 용도 없음"])
print("블록 도형 합", round(blocks_map), "조서 합", blocks_doc, "구역 도형", round(ZONE.area), "도로(도형) ", round(road_map), "도로(조서)", ROAD_DOC)
for nm, doc, ag, am in rows:
    print(f"{nm:5s} 조서 {doc:>7,}  도형 {am:>9,.1f} ({100*(am/doc-1):+.1f}%)  비율(조서) {100*doc/ZONE_DOC:.1f}%")

# ── 그림 ──
fr = Frame(W, H, CX, CY, WM, name="m8")
ax, K = fr.ax, fr.K
draw_water(ax, FRAME.buffer(60), z=0.5)
draw_polys_fast(ax, load_buildings(FRAME.buffer(60)), fc=C_BLD, z=1)
draw_poly(ax, ZONE, fc="white", ec="none", z=2)                                  # 구역 안 = 도로 바탕(흰색)
draw_outline(ax, ZONE, "#9A9A9A", fr.pt(0.6), z=3)                              # 도로 가는 회색 외곽
for cls, nm, col, doc in USE:
    for g, p in by[cls]:
        draw_poly(ax, g, fc=col, ec="#8A8A8A", lw=fr.pt(0.7), z=4)
draw_outline(ax, ZONE, INK2, fr.pt(1.2), z=8, ls=(0, (5, 2.6)))                  # 고시 구역 쇄선
draw_outline(ax, PLAN, RED, fr.pt(2.6), z=20)                                    # 본 계획 경계

# 블록 라벨(이름 + 조서 면적)
OFFSET_PX = {"공원1": (26, 24), "공원3": (-14, 14)}      # 좁은 블록은 라벨이 경계선·도로에 걸리지 않게 미세 이동(px, 오른쪽+ 아래+)
for g, p in blocks:
    c = g.representative_point()
    px, py = fr.to_px(c.x, c.y)
    dx, dy = OFFSET_PX.get(p["name"], (0, 0))
    px, py = px + dx * K, py + dy * K
    e = fr.pt(9.0) * DPI / 72
    fr.label_px(px, py - 0.58 * e, p["name"], size=9.5, ha="center", va="center", weight="bold", z=45)
    fr.label_px(px, py + 0.62 * e, f"{p['gosi_area_m2']:,.0f}㎡", size=9.0, ha="center", va="center", z=45)

# 우측 하단 메모 — 주거용지 없음 (축척 막대 위)
bw, bh = 600 * K, 150 * K
x1 = W - 44 * K
x0 = x1 - bw
y1 = H - 44 * K - 110 * K            # 축척 막대 위
y0 = y1 - bh
fr.ov.add_patch(Rectangle((x0, y0), bw, bh, fc="white", ec=LINE, lw=fr.pt(0.9), alpha=0.92, zorder=55))
fr.ov.add_patch(Rectangle((x0, y0), 10 * K, bh, fc=RED, ec="none", zorder=56))
fr.label_px(x0 + 38 * K, y0 + bh * 0.36, "주거용지 없음", size=13, weight="bold", ha="left", va="center", z=58, halo_px=0)
fr.label_px(x0 + 38 * K, y0 + bh * 0.72, "결정도 블록 10개 중 주거 용도 0개", size=9, color=INK2, ha="left", va="center", z=58, halo_px=0)

fr.north_arrow()
fr.scale_bar(200, ticks=2)
items = [dict(t="text", label="용도별 면적·비율\n(고시 구역 156,460㎡ 기준)", bold=True)]
for cls, nm, col, doc in USE:
    n_blk = len(by[cls])
    items.append(dict(t="patch", fc=col, ec="#8A8A8A", label=f"{nm} {n_blk}곳\n{doc:,}㎡ ({100*doc/ZONE_DOC:.1f}%)"))
items.append(dict(t="patch", fc="white", ec="#9A9A9A", label=f"도로 4노선 852m\n{ROAD_DOC:,.0f}㎡ ({100*ROAD_DOC/ZONE_DOC:.1f}%)"))
items.append(dict(t="line", color=INK2, lw=1.2, ls=(0, (5, 2.6)), label="고시 구역"))
items.append(dict(t="line", color=RED, lw=2.6, label="본 계획 경계"))
fr.legend(items)
fr.save(OUT / "m8_decision_map.png")
print("saved", OUT / "m8_decision_map.png")
