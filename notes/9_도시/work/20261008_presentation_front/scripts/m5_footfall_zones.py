# -*- coding: utf-8 -*-
"""M5 유동 낙차 지도 (S2) — 2000x2000 px, 소상공인365 분석 구역 8곳을 ha당 일평균 유동인구로 단계 채색.

구역 도형
  A~D : archive/C_data/processed/footfall_areas_5187.geojson (SGIS 격자 32셀 · 행복황촌 근사 · 구역+300m · 구역)
  E~H : 같은 파일에 없다. 원(반경) 구역이라 중심 좌표와 반경으로 다시 만든다
        (pipeline/build_web_extras.py 와 같은 값; footfall_areas_web_4326.geojson 과 도형이 일치함을 확인).
값
  archive/C_data/raw/sbiz365_footfall_20260920.json 의 월별 일평균 13개월(2025.06~2026.06)을 평균하고,
  면적(archive/90_derived/footfall_sbiz365_summary.csv 의 area_m2)으로 나눈다.
출력: assets/maps/m5_footfall_zones.png, research/data_series/footfall_8zones.csv
실행: export PYTHONUTF8=1 PYTHONIOENCODING=utf-8; python m5_footfall_zones.py
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapkit_analysis as mk
from mapkit_analysis import *  # noqa: F401,F403

# ───────────────────────── 1. 구역·값 ─────────────────────────
raw = json.load(open(RAW / "sbiz365_footfall_20260920.json", encoding="utf-8"))
summ = {r["area_id"]: r for r in csv.DictReader(open(DERIVED / "footfall_sbiz365_summary.csv", encoding="utf-8-sig"))}
poly5187 = {p["id"]: g for g, p in load_geojson(PROC / "footfall_areas_5187.geojson")}

CIRCLES = {   # 중심(경도, 위도), 반경 m — build_web_extras.py
    "E_center_r300": (129.218919, 35.8458367, 300),
    "F_cityhall_r500": (129.2247816627553, 35.85621665939485, 500),
    "G_seongdong_market_r200": (129.216354826459, 35.84534371000188, 200),
    "H_hwangridan_r300": (129.2098, 35.8384, 300),
}


def circ(lon, lat, r):
    x, y = T_4326_5187.transform(lon, lat)
    return Point(x, y).buffer(r), (x, y)


META = {   # id: (지도 라벨 이름, 문서상 정의)
    "A_hwango_grid32": ("황오동 원도심", "황오동 원도심 활성화구역 — SGIS 100m 격자 32셀(2024 황오동 모니터링 보고서 쪽 9, 국가지점번호 '마마' 블록)"),
    "B_haengbok_hwangchon_digitized": ("행복황촌", "경주역동편(행복황촌) 활성화구역 — 2020 활성화계획 그림 1.4 디지타이징, 근사 ±20m"),
    "C_zone_buffer300": ("구역+300m", "고시 2026-8호 지구단위계획구역 + 300m 버퍼"),
    "D_zone": ("폐역 구역", "고시 2026-8호 지구단위계획구역 자체(도면 추출 도형)"),
    "E_center_r300": ("구역 중심 300m", "지구단위계획구역 중심 반경 300m 원"),
    "F_cityhall_r500": ("시청 500m", "경주시청(동천동 800) 중심 반경 500m 원"),
    "G_seongdong_market_r200": ("성동시장 200m", "경주성동시장(성동동 51-1) 중심 반경 200m 원"),
    "H_hwangridan_r300": ("황리단길 300m", "황리단길 중심 반경 300m 원"),
}
ORDER_IDS = list(META)
THRESH = [100, 500, 700, 1000]
CLASS_LABEL = ["100 미만", "100~500", "500~700", "700~1,000", "1,000 이상"]
RAMP = rgb_ramp("#DCE6F5", BLUE, 5)

zones = []
for zid in ORDER_IDS:
    if zid in CIRCLES:
        lon, lat, r = CIRCLES[zid]
        g, c = circ(lon, lat, r)
        center, radius = (lon, lat), r
    else:
        g, center, radius = poly5187[zid], None, None
    monthly = [float(str(x).replace(",", "")) for x in raw[zid]["monthly"]["sel"]]
    avg13 = float(np.mean(monthly))
    area_doc = float(summ[zid]["area_m2"])
    per_ha = avg13 / (area_doc / 1e4)
    per_ha_map = avg13 / (g.area / 1e4)
    cls = int(sum(per_ha >= t for t in THRESH))
    zones.append(dict(id=zid, letter=zid[0], name=META[zid][0], definition=META[zid][1], geom=g, center=center,
                      radius=radius, avg13=avg13, area_doc=area_doc, area_map=g.area, per_ha=per_ha,
                      per_ha_map=per_ha_map, cls=cls, months=raw[zid]["monthly"]["months"], analy=raw[zid].get("analyNo")))
Z = {z["letter"]: z for z in zones}
for z in zones:
    print(f"{z['letter']} {z['name']:<10} 13개월 일평균 {z['avg13']:>9,.1f}  문서면적 {z['area_doc']:>10,.0f}㎡ 지도면적 {z['area_map']:>10,.0f}㎡  "
          f"{z['per_ha']:>8,.1f}명/ha (지도면적 {z['per_ha_map']:,.1f})  단계 {z['cls'] + 1}")
ratio_GD = Z["G"]["per_ha"] / Z["D"]["per_ha"]
print(f"성동시장 200m / 폐역 구역 = {Z['G']['per_ha']:.1f} / {Z['D']['per_ha']:.1f} = {ratio_GD:.2f}배")

# ───────────────────────── 2. CSV ─────────────────────────
DOC_VAL = {"A": 715, "B": 80, "C": 350, "D": 79, "E": 390, "F": 596, "G": 1175, "H": 757}   # work/20260920_소상공인365_8구역_*.md §1 표
with open(DATA_SERIES / "footfall_8zones.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["구역", "지도 라벨", "구역 정의(문서)", "형태", "반경(m)", "중심 경도", "중심 위도", "면적(㎡)·문서",
                "면적(㎡)·지도 도형", "집계 기간", "13개월 일평균 유동(명)", "명/ha(문서 면적 기준)", "명/ha(지도 도형 면적 기준)",
                "문서 8구역표 값(명/ha)", "일치", "색 단계(명/ha)", "소상공인365 analyNo", "등급·출처", "비고"])
    for z in zones:
        notes = []
        if z["id"] == "D_zone":
            notes.append("고시 조서 면적 156,460㎡ 대비 도형 +1.4%(158,721㎡). 156,460㎡로 나누면 약 80명/ha")
        if z["id"] == "B_haengbok_hwangchon_digitized":
            notes.append("경계는 근사(±20m). 보고서의 5,431명(+396%)은 재현되지 않아 사용 금지")
        if z["radius"]:
            notes.append("원 도형은 64각형 근사라 지도 면적이 원 면적보다 0.16% 작다")
        w.writerow([z["letter"], z["name"], z["definition"], "원" if z["radius"] else "다각형", z["radius"] or "",
                    f"{z['center'][0]:.6f}" if z["center"] else "", f"{z['center'][1]:.6f}" if z["center"] else "",
                    f"{z['area_doc']:.0f}", f"{z['area_map']:.0f}", "2025.06~2026.06 (월별 일평균 13개월 평균)",
                    f"{z['avg13']:.1f}", f"{z['per_ha']:.1f}", f"{z['per_ha_map']:.1f}", DOC_VAL[z["letter"]],
                    "일치" if round(z["per_ha"]) == DOC_VAL[z["letter"]] else "불일치",
                    CLASS_LABEL[z["cls"]], z["analy"] or "",
                    "T2 (소상공인시장진흥공단 소상공인365 상권분석, 통신사 휴대전화 통화량 기반 50m 셀 추정)", " / ".join(notes)])

# ───────────────────────── 3. 그림 ─────────────────────────
W = H = 2000
CX, CY, WM = 219730.0, 361010.0, 3300.0
fr = Frame(W, H, CX, CY, WM, name="m5")
ax, K = fr.ax, fr.K
win = fr.win.buffer(80)
em = fr.pt(10.0) * DPI / 72          # 라벨 글자 크기(px)

draw_polys_fast(ax, load_buildings(win), fc=C_BLD, z=1)

plan = plan_boundary()
draw_order = sorted(zones, key=lambda z: -z["area_doc"])         # 큰 구역부터, 작은 구역이 위
for k, z in enumerate(draw_order):
    draw_poly(ax, z["geom"], fc=RAMP[z["cls"]], ec="none", lw=0, alpha=0.84, z=2 + k * 0.1)
for k, z in enumerate(draw_order):
    ls = (0, (3.2, 2.2)) if z["radius"] else "-"
    draw_outline(ax, z["geom"], GRAY, fr.pt(0.8), z=12 + k * 0.01, ls=ls, joinstyle="round")
draw_outline(ax, plan, RED, fr.pt(2.6), z=14)


def zlabel(x, y, z, ha, size=10.0, leader_to=None, anchor_dot=True):
    """x,y(지도 좌표)에 구역명+값 두 줄 라벨. leader_to 가 있으면 라벨 가장자리에서 구역 안 한 점까지 가는 선."""
    px, py = fr.to_px(x, y)
    e = fr.pt(size) * DPI / 72
    val = f"{z['per_ha']:,.0f}명/ha"
    fr.label_px(px, py - 0.58 * e, z["name"], size=size, ha=ha, va="center", weight="normal", z=52)
    fr.label_px(px, py + 0.62 * e, val, size=size + 0.5, ha=ha, va="center", weight="bold", z=52)
    if leader_to is not None:
        ax_, ay_ = fr.to_px(*leader_to)
        gap = 0.45 * e
        sx = px + gap if ha == "right" else px - gap
        fr.ov.plot([sx, ax_], [py, ay_], color=INK2, lw=fr.pt(0.9), zorder=45, solid_capstyle="round")
        if anchor_dot:
            fr.ov.plot([ax_], [ay_], marker="o", ms=fr.pt(4.4), mfc=INK2, mec="white", mew=fr.pt(0.9), zorder=46, ls="none")


XL, XR = 219290.0, 220290.0                          # 왼쪽·오른쪽 라벨 단 가장자리
# 왼쪽 단 (위→아래): 폐역 구역, 구역 중심 300m, 황오동 원도심, 성동시장 200m
zlabel(XL, 361610.0, Z["D"], "right", leader_to=(219770.0, 361390.0))
zlabel(XL, 361340.0, Z["E"], "right", leader_to=(219624.0, 361162.0))
zlabel(XL, 361050.0, Z["A"], "right", leader_to=(219372.0, 361050.0))
zlabel(XL, 360780.0, Z["G"], "right", leader_to=(219385.0, 360880.0))
# 오른쪽 단: 행복황촌, 구역+300m
zlabel(XR, 361150.0, Z["B"], "left", leader_to=(220050.0, 361100.0))
zlabel(XR, 360560.0, Z["C"], "left", leader_to=(220120.0, 360585.0))
# 시청 500m: 원 안쪽 가운데, 황리단길 300m: 원 서쪽 옆
cF = Z["F"]["geom"].centroid
zlabel(cF.x, cF.y, Z["F"], "center")
cH = Z["H"]["geom"].centroid
zlabel(Z["H"]["geom"].bounds[0] - 25.0, cH.y, Z["H"], "right")

# 방위·축척·범례
fr.north_arrow()
fr.scale_bar(500, ticks=2, ends_only=True)
fr.legend([
    [dict(t="ramp", colors=RAMP, tick_labels=["100", "500", "700", "1,000"], seg_w=112,
          label="일평균 유동인구 (명/ha)")],
    [dict(t="line", color=RED, lw=2.6, label="본 계획 경계"),
     dict(t="text", label="통신사 추정, 2025.06~2026.06 일평균", color=INK)],
])
fr.save(OUT / "m5_footfall_zones.png")
print("saved", OUT / "m5_footfall_zones.png")
