# -*- coding: utf-8 -*-
"""M6 규제 4겹 지도 4장 — 각 1200x1600 px, 같은 틀(중심 219,740 / 360,940, 동서 900m x 남북 1,200m).

  m6a_zoning.png   용도지역(V-World UQ111)       — 본 계획 경계 안 면적 비율
  m6b_height.png   고도지구(V-World UQ123 + 경북고시 2020-479 높이) — 도심 20m / 15m 비율
  m6c_heritage.png 문화유산(V-World UO301, 시굴 대상은 발표자료 그림 판독 근사)
  m6d_plan.png     지구단위계획 고시 2026-8호 구역과 결정도 블록
비율은 도형 교차 면적(shapely)으로 다시 쟀다. 결과는 research/data_series/m6_regulation_check.csv 에 남긴다.
실행: export PYTHONUTF8=1 PYTHONIOENCODING=utf-8; python m6_regulation.py [a b c d]   (인자 없으면 전부)
"""
import collections
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapkit_analysis as mk
from mapkit_analysis import *  # noqa: F401,F403
from shapely.ops import nearest_points

W, H = 1200, 1600
CX, CY, WM = 219740.0, 360940.0, 900.0
PLAN = plan_boundary()
ZONE = gosi_zone()
FRAME = box(CX - WM / 2, CY - WM * H / W / 2, CX + WM / 2, CY + WM * H / W / 2)
plt.rcParams["hatch.linewidth"] = 0.55

# ─────────────────── 자료 ───────────────────
UQ111 = collections.defaultdict(list)           # 용도지역
for g, p in load_geojson(RAW / "vworld_uq111.geojson", crs="4326"):
    UQ111[p["uname"]].append(g)
UQ111 = {k: unary_union(v) for k, v in UQ111.items()}

GODO = collections.defaultdict(list)             # 고도지구(높이별)
for g, p in load_geojson(PROC / "godo_5187.geojson"):
    GODO[(p["godo_nm"], p["h_cls"])].append(g)
GODO = {k: unary_union(v) for k, v in GODO.items()}

HERIT = load_geojson(RAW / "vworld_uo301_heritage.geojson", crs="4326")

CHECK = []       # (지도, 항목, 문서 값, 지도 재산정, 기준 면적, 메모)


def base_frame(name):
    fr = Frame(W, H, CX, CY, WM, name=name)
    draw_polys_fast(fr.ax, load_buildings(FRAME.buffer(60)), fc=C_BLD, z=1)
    draw_water(fr.ax, FRAME.buffer(60), z=3.5)         # 하천(북천) — 겹침 칠 위, 윤곽선 아래
    return fr


def pct(a, tot):
    return 100.0 * a / tot


def finish(fr, fname, legend_items, note=None):
    draw_outline(fr.ax, PLAN, RED, fr.pt(2.6), z=20)
    fr.north_arrow()
    fr.scale_bar(200, ticks=2)
    fr.legend(legend_items, note=note)
    return fr.save(OUT / fname)


def leader(fr, p_from, p_to, dot=True, color=INK2):
    """지도 좌표 두 점을 잇는 가는 선 + 끝점 점."""
    fr.ax.plot([p_from[0], p_to[0]], [p_from[1], p_to[1]], color=color, lw=fr.pt(0.8), zorder=40, solid_capstyle="round")
    if dot:
        fr.ax.plot([p_to[0]], [p_to[1]], marker="o", ms=fr.pt(3.6), mfc=color, mec="white", mew=fr.pt(0.7), zorder=41, ls="none")


def two_line(fr, x, y, name, val, ha="center", size=9.5, color=INK, z=45):
    """이름 + 굵은 값 두 줄 라벨(지도 좌표)."""
    px, py = fr.to_px(x, y)
    e = fr.pt(size) * DPI / 72
    fr.label_px(px, py - 0.58 * e, name, size=size, ha=ha, va="center", color=color, z=z)
    fr.label_px(px, py + 0.62 * e, val, size=size + 0.5, ha=ha, va="center", weight="bold", color=color, z=z)


# ─────────────────── M6a 용도지역 ───────────────────
def m6a():
    fr = base_frame("m6a")
    ax = fr.ax
    classes = [("자연녹지지역", "#CFE3B8", "자연녹지"), ("제2종일반주거지역", C_YELLOW, "2종일반주거"), ("일반상업지역", C_SOUTH, "일반상업")]
    OTHER_C = "#E3E3E3"
    for name, g in UQ111.items():
        col = {n: c for n, c, _ in classes}.get(name, OTHER_C)
        gg = g.intersection(FRAME)
        draw_poly(ax, gg, fc=col, ec="none", alpha=0.34, z=2)                       # 경계 밖은 옅게
        draw_poly(ax, gg.intersection(PLAN), fc=col, ec="none", alpha=0.95, z=3)      # 경계 안은 진하게
        draw_outline(ax, gg, GRAY, fr.pt(0.5), z=4, alpha=0.7)
    tot = PLAN.area
    res = {n: PLAN.intersection(UQ111[n]).area for n, _, _ in classes}
    doc = {"자연녹지지역": ("77.5%", 169550), "제2종일반주거지역": ("16.3%", 35600), "일반상업지역": ("6.2%", 13575)}
    for n, _, _ in classes:
        CHECK.append(("M6a", f"용도지역 {n}", f"{doc[n][0]} ({doc[n][1]:,}㎡)", f"{pct(res[n], tot):.2f}% ({res[n]:,.0f}㎡)",
                      f"본 계획 경계 {tot:,.0f}㎡", "문서: V-World UQ111 겹침, 5m 격자 표본 ±1%(팩트체크 §2.2). 지도: 폴리곤 정확 교차"))
    zt = ZONE.area
    zdoc = {"자연녹지지역": (151116, "96.6%"), "제2종일반주거지역": (4507, "2.9%"), "일반상업지역": (837, "0.5%")}
    for n, _, _ in classes:
        a = ZONE.intersection(UQ111[n]).area
        CHECK.append(("M6a", f"용도지역 {n} (고시 구역 기준)", f"{zdoc[n][1]} ({zdoc[n][0]:,}㎡)", f"{pct(a, zt):.2f}% ({a:,.0f}㎡)",
                      f"고시 구역 도면 추출 도형 {zt:,.0f}㎡", "문서: 고시 2026-8호 결정조서(T1, 조서 면적 156,460㎡). 지도: V-World ∩ 도면 추출 구역"))
    print("M6a", {n: f"{pct(res[n], tot):.2f}%" for n, _, _ in classes})
    # 라벨: 면적 비율(본 계획 경계 안)
    two_line(fr, 219780.0, 361020.0, "자연녹지", f"{pct(res['자연녹지지역'], tot):.1f}%", size=11)
    two_line(fr, 219858.0, 361290.0, "2종일반주거", f"{pct(res['제2종일반주거지역'], tot):.1f}%", size=9.5)
    # 일반상업: 서쪽 가장자리 얇은 띠 → 경계 밖 왼쪽에 라벨 + 선
    lab = (219420.0, 360985.0)
    two_line(fr, lab[0], lab[1], "일반상업", f"{pct(res['일반상업지역'], tot):.1f}%", size=9.5)
    ptc = PLAN.intersection(UQ111["일반상업지역"])
    anchor = max(getattr(ptc, "geoms", [ptc]), key=lambda g: g.area).representative_point()
    leader(fr, (lab[0] + 50, lab[1]), (anchor.x, anchor.y))
    items = [dict(t="patch", fc=c, ec=GRAY, label=n) for n, c, _ in classes]
    items += [dict(t="patch", fc=OTHER_C, ec=GRAY, label="그 밖의 용도지역"),
              dict(t="line", color=RED, lw=2.6, label="본 계획 경계")]
    return finish(fr, "m6a_zoning.png", items, note="경계 안 면적 비율, 경계 밖은 옅게")


# ─────────────────── M6b 고도지구 ───────────────────
def m6b():
    fr = base_frame("m6b")
    ax = fr.ax
    focus = {"20m": ("#6F9FDC", "도심 20m 지구"), "15m": (C_CENTER, "도심 15m 지구")}
    OTHER_C = "#E3E3E3"
    groups = collections.defaultdict(list)
    for (nm, hc), g in GODO.items():
        if hc == "최저고도":
            continue
        groups[hc if hc in focus else "기타"].append(g)
    groups = {k: unary_union(v) for k, v in groups.items()}
    for k, g in groups.items():
        col = focus[k][0] if k in focus else OTHER_C
        gg = g.intersection(FRAME)
        draw_poly(ax, gg, fc=col, ec="none", alpha=0.34, z=2)
        draw_poly(ax, gg.intersection(PLAN), fc=col, ec="none", alpha=0.95, z=3)
        draw_outline(ax, gg, GRAY, fr.pt(0.5), z=4, alpha=0.7)
    # 비율
    tot = PLAN.area
    a20 = PLAN.intersection(groups["20m"]).area
    a15 = PLAN.intersection(groups["15m"]).area
    none_ = PLAN.difference(unary_union([groups["20m"], groups["15m"], groups.get("기타", Polygon())])).area
    low = PLAN.intersection(GODO[("최저고도지구", "최저고도")]).area
    CHECK.append(("M6b", "고도지구 도심 20m 지구", "89.0% (184,348㎡)", f"{pct(a20, tot):.2f}% ({a20:,.0f}㎡)", f"본 계획 경계 {tot:,.0f}㎡",
                  "문서(전체기록 §1.4·§6)의 분모는 이전 경계 v2 207,205㎡(184,348÷0.89≈207,100). 현재 경계로 다시 자르면 값이 달라진다. 지도: V-World UQ123 폴리곤 + 경북고시 2020-479 높이 ∩ 경계"))
    CHECK.append(("M6b", "고도지구 도심 15m 지구", "9.8% (20,248㎡, 동측 x>219,892 띠)", f"{pct(a15, tot):.2f}% ({a15:,.0f}㎡)", f"본 계획 경계 {tot:,.0f}㎡",
                  "같은 이유. 현재 경계가 동쪽으로 넓어져 15m 띠가 4,362㎡ 늘었다"))
    CHECK.append(("M6b", "고도지구 폴리곤이 없는 부분", "(문서 없음)", f"{pct(none_, tot):.2f}% ({none_:,.0f}㎡)", f"본 계획 경계 {tot:,.0f}㎡", "20m·15m·기타 높이 폴리곤 어디에도 속하지 않는 면적"))
    CHECK.append(("M6b", "최저고도지구(별도 규제, 위 값과 겹침)", "3.8% (8,366㎡, 팩트체크 §2.2·전체기록)", f"{pct(low, tot):.2f}% ({low:,.0f}㎡)", f"본 계획 경계 {tot:,.0f}㎡", "문서와 면적이 일치(8,366 ≈ 8,367) — 같은 V-World 폴리곤을 쓴 증거. 최고높이가 아니라 최저높이 규제라 20m·15m 와 별개로 센다"))
    zt = ZONE.area
    for hc, (c20, c15) in (("20m", (145364, "92.9%")), ("15m", (11143, "7.1%"))):
        a = ZONE.intersection(groups[hc]).area
        CHECK.append(("M6b", f"고도지구 도심 {hc} 지구 (고시 구역 기준)", f"{c20:,}㎡ = {c15} (조서 156,460㎡ 대비, T1)", f"{pct(a, zt):.2f}% ({a:,.0f}㎡)",
                      f"고시 구역 도면 추출 도형 {zt:,.0f}㎡", "문서: 고시 2026-8호 결정조서 용도지구 괄호값. 지도: V-World ∩ 도면 추출 구역"))
    print("M6b", f"20m {pct(a20, tot):.2f}%  15m {pct(a15, tot):.2f}%  폴리곤 밖 {pct(none_, tot):.2f}%  최저고도 {pct(low, tot):.2f}%")
    # 라벨
    p15 = PLAN.intersection(groups["15m"])
    two_line(fr, 219780.0, 361020.0, "도심 20m 지구", f"{pct(a20, tot):.1f}%", size=11, color=INK)
    big15 = max(getattr(p15, "geoms", [p15]), key=lambda g: g.area)
    rp = big15.representative_point()
    lab = (220075.0, 361210.0)
    two_line(fr, lab[0], lab[1], "도심 15m 지구", f"{pct(a15, tot):.1f}%", size=9.5)
    leader(fr, (lab[0] - 70, lab[1] - 18), (rp.x + 6, rp.y + 80))
    items = [dict(t="patch", fc=focus["20m"][0], ec=GRAY, label="도심 20m 지구"),
             dict(t="patch", fc=focus["15m"][0], ec=GRAY, label="도심 15m 지구"),
             dict(t="patch", fc=OTHER_C, ec=GRAY, label="그 밖의 높이 구역"),
             dict(t="line", color=RED, lw=2.6, label="본 계획 경계")]
    return finish(fr, "m6b_height.png", items, note="경계 안 면적 비율, 경계 밖은 옅게")


# ─────────────────── M6c 문화유산 ───────────────────
def m6c():
    import siguel_digitize as sd
    fr = base_frame("m6c")
    ax = fr.ax
    ORANGE, LAV = "#C9742F", C_CENTER
    sg = sd.build()
    s = sg["stats"]
    # 1) 역사문화환경 보존지역(UOC800) — 연보라
    u800, desig = [], []
    for g, p in HERIT:
        if not g.intersects(FRAME):
            continue
        if p["uname"] == "역사문화환경보존지역":
            u800.append((g, p))
        else:
            desig.append((g, p))
    for g, p in u800:
        gg = g.intersection(FRAME)
        focus = abs(g.area - 179238) < 50                      # 황오동 삼층석탑 보존지역
        draw_poly(ax, gg, fc=LAV, ec="none", alpha=0.30 if focus else 0.15, z=2)
        draw_outline(ax, gg, LAV, fr.pt(1.1 if focus else 0.7), z=6, ls="-" if focus else (0, (4, 2.5)))
    # 2) 국가지정·시도지정·보호구역 — 주황 실면
    for g, p in desig:
        gg = g.intersection(FRAME)
        draw_poly(ax, gg, fc=ORANGE, ec=ORANGE, lw=fr.pt(0.6), alpha=0.62, z=5)
    # 3) 시굴 대상(그림 판독 근사): 유물산포지 //// , 사지Ⅱ xxxx — 주황 빗금, 건물 3동은 비움
    draw_poly(ax, sg["yumul"], fc=(0.79, 0.45, 0.18, 0.13), ec=ORANGE, lw=fr.pt(1.1), hatch="//////", z=7)
    draw_poly(ax, sg["saji2"], fc=(0.79, 0.45, 0.18, 0.22), ec=ORANGE, lw=fr.pt(1.1), hatch="xxxxxx", z=8)
    draw_outline(ax, sg["boxes"], ORANGE, fr.pt(0.9), z=9)
    # 4) 삼층석탑 (V-World 문화재 UOC200 폴리곤 중심)
    tower = None
    for g, p in HERIT:
        if p["uname"] == "문화재" and g.intersects(FRAME):
            tower = g.centroid
    ax.plot([tower.x], [tower.y], marker="*", ms=fr.pt(10.5), mfc=INK, mec="white", mew=fr.pt(1.0), zorder=30, ls="none")
    # 지정 유산 지점(사적) 표시 — NGII 지명 주기 위치
    named = {}
    for g, a in mk.read_ngii("N3P_C0310000"):
        if g.within(FRAME) and "삼층석탑" not in (a.get("name") or ""):
            named[a.get("name")] = g
    # 수치 재산정
    tot, zt = PLAN.area, ZONE.area
    uu = unary_union([g for g, p in u800])
    a_u = PLAN.intersection(uu).area
    a_t = PLAN.intersection(sg["target"]).area
    CHECK.append(("M6c", "시굴 대상 면적(㎡)", "145,879㎡ (2022 지표조사·김권일 2026, T2)", f"{sg['target'].area:,.0f}㎡ (그림 판독 근사, 문서 대비 {100*(sg['target'].area/145879-1):+.1f}%)",
                  "p.23 그림 판독", "도형 자료가 없어 발표자료 그림을 맞춘 근사. 위치 오차 ±10m 안팎"))
    CHECK.append(("M6c", "시굴 대상 = 유물산포지 + 사지Ⅱ", "104,997 + 40,882 = 145,879㎡", f"{sg['yumul'].area:,.0f} + {sg['saji2'].area:,.0f} = {sg['target'].area:,.0f}㎡",
                  "p.23 그림 판독", "3구역(사지Ⅱ) 경계 판독 오차로 유물산포지 +3.7%, 사지Ⅱ −6.7%. 합은 +0.8%"))
    CHECK.append(("M6c", "시굴 대상 / 고시 구역 비율", "93% (145,879 ÷ 156,460 = 93.2%)", f"{pct(145879, 156460):.1f}% (문서 두 값의 나눗셈) / 판독 도형 ∩ 고시 구역 {pct(sg['target'].intersection(ZONE).area, 156460):.1f}% (조서 면적 기준), {pct(sg['target'].intersection(ZONE).area, ZONE.area):.1f}% (도면 추출 구역 기준)",
                  "고시 구역 156,460㎡(T1)", "93%는 두 문서 값의 비. 판독 도형으로는 91~92% (판독 오차 범위)"))
    CHECK.append(("M6c", "시굴 대상 중 고시 구역 안에 든 비율", "(문서 없음)", f"{pct(sg['target'].intersection(ZONE).area, sg['target'].area):.1f}% ({sg['target'].intersection(ZONE).area:,.0f}㎡)", "판독 도형", "조사지역은 고시 구역과 거의 같은 필지선을 따른다(IoU %.3f)" % s["iou"]))
    CHECK.append(("M6c", "역사문화환경 보존지역 ∩ 본 계획 경계", "(문서) 고시 구역 내 109,608㎡(삼층석탑 보존지역) + 16,066㎡(도심 광역)", f"{a_u:,.0f}㎡ = {pct(a_u, tot):.1f}% (본 계획 경계), 고시 구역 기준 {pct(ZONE.intersection(uu).area, zt):.1f}%",
                  f"본 계획 경계 {tot:,.0f}㎡", "삼층석탑 보존지역 ∩ 도면 추출 구역 = 109,608㎡로 문서와 일치. 김권일(2026): 허용기준 3구역이 사업대상지의 약 2/3(T2)"))
    print("M6c 시굴 판독:", {k: f"{v:,.0f}" for k, v in s.items() if k in ("survey", "yumul", "saji2", "boxes", "target")}, "IoU", round(s["iou"], 3))
    # 라벨
    lab = (219545.0, 361300.0)
    two_line(fr, lab[0], lab[1], "성동동 유물산포지", "104,997㎡", size=9.5)
    leader(fr, (lab[0] + 82, lab[1] - 6), (219748.0, 361262.0))
    lab = (220030.0, 360700.0)
    two_line(fr, lab[0], lab[1], "성동동사지Ⅱ", "40,882㎡", size=9.5)
    rp2 = sg["saji2"].representative_point()
    leader(fr, (lab[0] - 62, lab[1] + 8), (rp2.x + 30, rp2.y - 40))
    lab = (219420.0, 360770.0)
    two_line(fr, lab[0], lab[1], "황오동 삼층석탑", "경북 문화재자료 제8호", size=9.0)
    leader(fr, (lab[0] + 84, lab[1] + 4), (tower.x, tower.y))
    # 보존지역(허용기준 적용) 라벨 — 원 안쪽 서쪽
    px, py = fr.to_px(219523.0, 360935.0)
    e = fr.pt(9.0) * DPI / 72
    fr.label_px(px, py - 0.58 * e, "역사문화환경 보존지역", size=9.0, ha="center", va="center", color="#6B4FA0", weight="bold", z=45)
    fr.label_px(px, py + 0.62 * e, "현상변경 허용기준 적용", size=9.0, ha="center", va="center", color="#6B4FA0", z=45)
    # 주변 사적(고분 등) — NGII 지명 주기
    def named_pt(key):
        for nm, g in named.items():
            if key in (nm or ""):
                return g
    pj = named_pt("전랑지")
    if pj is not None:
        two_line(fr, 220120.0, 361048.0, "성동동 전랑지", "사적 제88호", size=9.0, color="#8A4A14")
    pn = named_pt("남고루")
    if pn is not None:
        px, py = fr.to_px(pn.x - 62, pn.y + 6)
        e = fr.pt(9.0) * DPI / 72
        fr.label_px(px, py - 0.58 * e, "경주 남고루", size=9.0, ha="right", va="center", color="#8A4A14", z=45)
        fr.label_px(px, py + 0.62 * e, "사적 제17호", size=9.0, ha="right", va="center", weight="bold", color="#8A4A14", z=45)
    two_line(fr, 219700.0, 360382.0, "대릉원 일원", "사적 제512호", size=9.0, color="#8A4A14")
    items = [dict(t="text", label="시굴 대상 145,879㎡\n(고시 구역의 93%)", bold=True),
             dict(t="patch", fc=(0.79, 0.45, 0.18, 0.16), ec=ORANGE, hatch="//////", label="성동동 유물산포지"),
             dict(t="patch", fc=(0.79, 0.45, 0.18, 0.26), ec=ORANGE, hatch="xxxxxx", label="성동동사지Ⅱ(비지정)"),
             dict(t="patch", fc=ORANGE, ec=ORANGE, label="문화재 지정·보호구역\n(주변 고분·사적)"),
             dict(t="patch", fc=(0.66, 0.55, 0.83, 0.30), ec=LAV, label="역사문화환경 보존지역"),
             dict(t="dot", fc=INK, ec="white", marker="*", ms=8.0, label="황오동 삼층석탑"),
             dict(t="line", color=RED, lw=2.6, label="본 계획 경계")]
    return finish(fr, "m6c_heritage.png", items, note="시굴 대상 도형은 그림 판독 근사")


# ─────────────────── M6d 지구단위계획 ───────────────────
def m6d():
    fr = base_frame("m6d")
    ax = fr.ax
    blocks = gosi_blocks()
    SPECIAL = {"상1": "특계1", "주1": "특계1", "상2": "특계2", "상3": "특계3", "공청1": "특계4", "공청2": "특계4", "문화1": "특계5"}
    SP_C, PARK_C = C_NORTH, C_GREEN
    draw_poly(ax, ZONE, fc="white", ec="none", alpha=0.85, z=2)
    for g, p in blocks:
        col = PARK_C if p["cls"] == "park" else SP_C
        draw_poly(ax, g, fc=col, ec=GRAY, lw=fr.pt(0.7), alpha=0.88, z=3)
    draw_outline(ax, ZONE, INK2, fr.pt(1.5), z=8, ls=(0, (5, 2.4)))
    # 블록 라벨 (이름 + 특별계획구역 번호)
    for g, p in blocks:
        c = g.representative_point()
        nm = p["name"]
        if nm in SPECIAL:
            two_line(fr, c.x, c.y, nm, SPECIAL[nm], size=9.0)
        else:
            fr.label(c.x, c.y, nm, size=9.0, ha="center", va="center", z=45)
    print("M6d 블록", len(blocks), "고시 구역 도면 추출", round(ZONE.area))
    items = [dict(t="patch", fc=SP_C, ec=GRAY, label="특별계획구역 5곳\n82,544㎡"),
             dict(t="patch", fc=PARK_C, ec=GRAY, label="근린공원 3곳\n55,415㎡"),
             dict(t="line", color=INK2, lw=1.5, ls=(0, (5, 2.4)), label="고시 구역 156,460㎡"),
             dict(t="line", color=RED, lw=2.6, label="본 계획 경계"),
             dict(t="text", label="주거용지 없음", bold=True, color=INK)]
    return finish(fr, "m6d_plan.png", items)


if __name__ == "__main__":
    which = sys.argv[1:] or ["a", "b", "c", "d"]
    for k, fn in (("a", m6a), ("b", m6b), ("c", m6c), ("d", m6d)):
        if k in which:
            fn()
    if CHECK:
        with open(DATA_SERIES / "m6_regulation_check.csv", "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["지도", "항목", "문서 값", "지도 데이터 재산정", "기준 면적", "메모"])
            w.writerows(CHECK)
