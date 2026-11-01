"""S7 도면 — ① 주 도면(사선 매스+패널) ② 맥락 접속도 ③ 구획·조닝도 ④ 층수·높이도 ⑤ 동서 단면 입면.
출력: work/20261005_plan_massing/*.png"""
import pickle, sys, math, json, collections, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, Circle, Patch, Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D
from shapely.geometry import Polygon, LineString, Point, box, shape
from shapely.ops import unary_union
from shapely import wkb
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
OUT = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing"
sys.path.insert(0, OUT + r"\scripts")
import s5_render as R
from s5_render import CATCOL, LEG_ORDER, shade, extrude_draw, shadow, tree, bcolor
from geomkit import polys, poisson
from plan_meta import PROGRAMS
fm.fontManager.addfont(r"C:\Windows\Fonts\malgun.ttf"); plt.rcParams["font.family"] = "Malgun Gothic"

C, NET, M = R.load(); U = C["U"]
T = pickle.load(open(SP + r"\tables.pkl", "rb")); AS = pickle.load(open(SP + r"\anchor_status.pkl", "rb"))
H = pickle.load(open(SP + r"\heritage_rail.pkl", "rb"))
S = T["summary"]

CIRC = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
# 번호 → (제목, 위치, 설명 생성키)
CALL = [
    (1, "시청·의회 캠퍼스", (219712, 361167)),
    (2, "복합문화·영화관", (219712, 361038)),
    (3, "청년창업·기업지원", (219834, 361038)),
    (4, "청년·주민 커뮤니티", (219904, 361038)),
    (5, "청년주거(중정형·연립)", (219833, 361186)),
    (6, "공공운동·생활시설", (219757, 361302)),
    (7, "북천 수변공원", (219802, 361372)),
    (8, "성동시장 연계 판매·체험", (219712, 360861)),
    (9, "삼층석탑 마당", (219660, 360816)),
    (10, "아티스트 레지던시·공방", (219835, 360873)),
    (11, "역전광장·구경주역(이전)", (219708, 360737)),
    (12, "근대역사관·전시장", (219745, 360737)),
    (13, "관광지원시설·환승광장", (219808, 360708)),
    (14, "주차타워", (219866, 360725)),
    (15, "관광객 휴게·판매상가", (219700, 360598)),
    (16, "동서 그린 보행축", (219720, 360968)),
]

def prog_stat(keys):
    fp = sum(b["area"] for b in M["BUILD"] if b["prog"] in keys); gfa = sum(b["gfa"] for b in M["BUILD"] if b["prog"] in keys)
    mf = max([b["floors"] for b in M["BUILD"] if b["prog"] in keys], default=0); mh = max([b["h"] for b in M["BUILD"] if b["prog"] in keys], default=0)
    return fp, gfa, mf, mh

def base_plan(ax, crop, show_buildings=True, flat_context=False, tilt=0.62, trees=True, rails=True, show_new=True, new_alpha=1.0):
    """공통 바탕: 맥락(도로면·건물) + 부지(도로·녹지·광장·마당) + (선택)신규 매스·수목"""
    x0, y0, x1, y1 = crop
    ax.set_facecolor("#efeeea")
    for r in C["RP"]:
        for p in polys(r): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#ffffff", ec="none", zorder=1))
    for p in polys(U): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#f7f6f3", ec="none", zorder=2))
    road_all = unary_union([NET["road_all"], NET["plaza_extra"]])
    for p in polys(road_all): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#ffffff", ec="#d9d6cf", lw=0.4, zorder=3))
    for p in polys(NET["green_all"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#a6d982", ec="#6aa84a", lw=0.5, zorder=3))
    for nm, g in M["EXTRA"]["plaza"]:
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#ece7de", ec="none", zorder=3.2))
    for nm, g in M["EXTRA"]["court"]:
        fc = "#d98a6a" if "운동장" in nm else "#cfe6b4"
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc=fc, ec="#ffffff" if "운동장" in nm else "#9cc77a", lw=0.8 if "운동장" in nm else 0.3, zorder=3.3))
    for nm, g in M["EXTRA"]["surface_parking"]:
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#cfcfcf", ec="#9a9a9a", lw=0.3, hatch="////", zorder=3.3))
    for nm, g in M["EXTRA"]["heritage_plaza"]:
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#e9d9bd", ec="#b8662b", lw=0.8, zorder=3.4))
    for nm, g in M["EXTRA"]["path"]:
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#f0e9d6", ec="none", zorder=3.4))
    if rails:   # 폐선 흔적: 열린 공간(도로·녹지·광장·마당) 위에만
        openu = unary_union([road_all, NET["green_all"]] + [g for nm, g in M["EXTRA"]["plaza"]] + [g for nm, g in M["EXTRA"]["court"] if "운동장" not in nm]).buffer(0)
        for p, g in H["rail_abandoned_4326"]:
            for l in (g.geoms if hasattr(g, "geoms") else [g]):
                if l.geom_type != "LineString": continue
                seg = l.intersection(openu)
                for s in (seg.geoms if hasattr(seg, "geoms") else [seg]):
                    if s.geom_type == "LineString" and s.length > 4: ax.plot(*s.xy, color="#a86a3c", lw=0.5, alpha=0.75, zorder=3.6, ls=(0, (4, 2)))
    cb = [b for b in C["B"] if not U.contains(b["geom"].representative_point())]
    cb.sort(key=lambda b: -b["geom"].centroid.y)
    for b in cb:
        if not (x0 - 25 < b["geom"].centroid.x < x1 + 25 and y0 - 25 < b["geom"].centroid.y < y1 + 25): continue
        h = b["floors"] * 3.5
        col = "#d8d3c8" if b["floors"] <= 2 else "#cbc5b8" if b["floors"] <= 4 else "#b9b2a4"
        if flat_context:
            for p in polys(b["geom"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc=col, ec="#b5afa2", lw=0.2, zorder=6))
        else:
            shadow(ax, b["geom"], h, zorder=4, alpha=0.10); extrude_draw(ax, b["geom"], h, col, tilt=tilt, zorder=6)
    bl = sorted(M["BUILD"], key=lambda b: -b["geom"].centroid.y)
    if show_new:
        for b in bl: shadow(ax, b["geom"], b["h"], zorder=5)
        for b in bl: extrude_draw(ax, b["geom"], b["h"], bcolor(b), tilt=tilt, zorder=10 + (1000 - b["geom"].centroid.y % 1000) * 0.0001, alpha=new_alpha)
    if trees:
        rng = np.random.default_rng(3)
        for nm, g in [("g", NET["green_all"])] + [("z", z) for z in M["EXTRA"]["tree_zone"]]:
            for p in polys(g):
                for q in poisson(p.buffer(-1.5), 11.0 if nm == "g" else 9.5, seed=int(p.area) % 97 + 1):
                    r = rng.uniform(2.6, 4.2)
                    if all(not bb["geom"].buffer(1.0).contains(q) for bb in bl if abs(bb["geom"].centroid.x - q.x) < 80 and abs(bb["geom"].centroid.y - q.y) < 80):
                        tree(ax, q.x, q.y, r)
        for k, (pts, w, *_r) in NET["STREETS"].items():
            if w < 12 and k not in ("S",): continue
            ln = LineString(pts)
            for side in (-1, 1):
                off = ln.parallel_offset(w / 2 - 1.6, "left" if side > 0 else "right")
                if off.is_empty: continue
                for seg in (off.geoms if hasattr(off, "geoms") else [off]):
                    n = int(seg.length // 14)
                    for i in range(n):
                        q = seg.interpolate((i + 0.5) / n, normalized=True)
                        if U.contains(q) and NET["road_all"].contains(q): tree(ax, q.x, q.y, 2.2, c="#6fb34a", zorder=8.5)
    for p, g in H["heritage_pts_4326"]:
        if "삼층석탑" in p["name"]: ax.plot(g.x, g.y, marker="*", color="#b8662b", ms=11, mec="white", mew=0.6, zorder=45)
    ax.plot(*U.exterior.xy, color="#8a2be2", lw=1.5, zorder=40, ls=(0, (6, 3)))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")

def north_scale(ax, crop, x=None, y=None, L=100):
    x0, y0, x1, y1 = crop
    x = x1 - 55 if x is None else x; y = y0 + 38 if y is None else y
    ax.add_patch(Rectangle((x - 62, y - 10), 70, 62, fc="white", ec="none", alpha=0.85, zorder=90))
    ax.plot([x - 55, x - 55 + L / 2.0 * 0 + L * 0.0], [y, y], color="k", lw=0)  # placeholder
    ax.plot([x - 56, x - 56 + L * 0.5], [y, y], color="k", lw=3, zorder=91, solid_capstyle="butt"); ax.plot([x - 56 + L * 0.5, x - 56 + L], [y, y], color="#999", lw=3, zorder=91, solid_capstyle="butt")
    ax.text(x - 56, y + 4, "0", fontsize=7, zorder=91); ax.text(x - 56 + L * 0.5, y + 4, "%d" % (L // 2), fontsize=7, ha="center", zorder=91); ax.text(x - 56 + L, y + 4, "%d m" % L, fontsize=7, ha="right", zorder=91)
    ax.annotate("", xy=(x - 28, y + 40), xytext=(x - 28, y + 17), arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2), zorder=91)
    ax.text(x - 28, y + 43, "N", ha="center", fontsize=9, fontweight="bold", zorder=91)

def callout_marks(ax, dy=6):
    for no, nm, (x, y) in CALL:
        ax.add_patch(Circle((x, y + dy), 7.2, fc="white", ec="#111", lw=1.2, zorder=80))
        ax.text(x, y + dy, str(no), ha="center", va="center", fontsize=8.5, fontweight="bold", zorder=81)

def street_tags(ax):
    tags = {"A": (219786, 360796, 90), "B": (219672, 360953, 0), "C": (219672, 361092, 0), "D": (219672, 361240, 0), "S": (219790, 361150, 90), "R6": (219786, 360690, 56), "S2": (219843, 360725, 90),
            "E": (219672, 360659, 0), "R7": (219836, 361290, 45), "R9": (219790, 361340, 313), "R8": (219893, 361325, 318)}
    for k, (x, y, rot) in tags.items():
        w = NET["STREETS"][k][1]
        ax.text(x, y, "%s %.0fm" % (k, w), fontsize=6.5, ha="center", va="center", rotation=rot if rot <= 90 else rot - 360, color="#222", zorder=70,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#888", lw=0.4, alpha=0.9))

# ══════════════════════════════════════════════════════════════════════════════
def fig_main(path):
    x0, y0, x1, y1 = U.buffer(30).bounds
    aspect = (y1 - y0) / (x1 - x0); pw = 8.2
    ph = pw * aspect
    fig = plt.figure(figsize=(pw + 5.3, ph + 0.2)); fig.patch.set_facecolor("#ffffff")
    axp = fig.add_axes([5.2 / (pw + 5.3), 0.1 / (ph + 0.2), pw / (pw + 5.3), ph / (ph + 0.2)])
    base_plan(axp, (x0, y0, x1, y1))
    callout_marks(axp); street_tags(axp); north_scale(axp, (x0, y0, x1, y1))
    # 패널
    ax = fig.add_axes([0.005, 0.0, 5.1 / (pw + 5.3), 1.0]); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 100)
    y = 99.2
    ax.text(0, y, "구경주역 도시계획안", fontsize=19, fontweight="bold", va="top"); y -= 2.3
    ax.text(0, y, "구획·매스 마스터플랜 v1  (손그림 → 가로망 구획 → 매스)", fontsize=10, va="top", color="#444"); y -= 1.7
    ax.text(0, y, "경계 %s㎡ (최종콘타모델_v2.3dm 현재선) · EPSG:5187" % format(round(S["U"]), ","), fontsize=8.5, va="top", color="#666"); y -= 2.4
    ax.text(0, y, "범례", fontsize=11, fontweight="bold", va="top"); y -= 1.6
    used = {b["cat"] for b in M["BUILD"]} | {"오픈스페이스"}
    for k in LEG_ORDER:
        if k not in used: continue
        ax.add_patch(Rectangle((0, y - 0.55), 0.9, 0.9, fc=CATCOL[k], ec="#555", lw=0.5)); ax.text(1.2, y - 0.1, k, fontsize=8.5, va="center"); y -= 1.15
    ax.add_patch(Rectangle((0, y - 0.55), 0.9, 0.9, fc="#9a9a9a", ec="#555", lw=0.5)); ax.text(1.2, y - 0.1, "주차전용건축물(교통·방문자 중 진한 회색)", fontsize=8.5, va="center"); y -= 1.15
    ax.plot([0, 0.9], [y - 0.1, y - 0.1], color="#a86a3c", lw=1, ls=(0, (4, 2))); ax.text(1.2, y - 0.1, "폐선 흔적(OSM 폐선 선형, 열린 공간 위에만)", fontsize=8.5, va="center"); y -= 1.15
    ax.plot([0.45], [y - 0.1], marker="*", color="#b8662b", ms=9); ax.text(1.2, y - 0.1, "황오동 삼층석탑(지정유산) — 반경 22 m 마당 비움", fontsize=8.5, va="center"); y -= 2.0
    ax.text(0, y, "프로그램 (번호 = 도면 표시)", fontsize=11, fontweight="bold", va="top"); y -= 1.7
    PK = {1: ["시청·의회"], 2: ["복합문화·영화관"], 3: ["청년창업·기업지원"], 4: ["청년주민커뮤니티"], 5: ["청년주거"], 6: ["공공운동·생활시설"], 7: ["수변 오픈스페이스"], 8: ["성동시장 연계 판매·체험"],
          9: [], 10: ["아티스트 레지던시·공방"], 11: ["구경주역 이전"], 12: ["경주 근대역사관·전시장"], 13: ["경주관광지원시설"], 14: ["주차타워"], 15: ["관광객 중심 휴게·판매상가"], 16: []}
    for no, nm, _ in CALL:
        fp, gfa, mf, mh = prog_stat(PK[no])
        ax.scatter([0.45], [y - 0.15], s=210, facecolors="white", edgecolors="#111", linewidths=1.1, zorder=5); ax.text(0.45, y - 0.15, str(no), ha="center", va="center", fontsize=8, fontweight="bold", zorder=6)
        ax.text(1.4, y + 0.25, nm, fontsize=9, fontweight="bold", va="center")
        if no == 9: sub = "원화로변·성동동사지Ⅱ 유존지역 — 지정유산 보호 마당(허용기준 미확인 → 보수적 반경)"
        elif no == 16: sub = "B 가로 12 m + 양측 녹지 → 약 70 m 폭, 원화로 ↔ 황오동 연결"
        elif no == 7: sub = "공원 8,537㎡ · 산책로 · 소규모 쉼터"
        elif no == 12: sub = "연면적 %s㎡ · 최고 %d층 %.1f m (구 역사 이전 구와 한 쌍)" % (format(round(gfa), ","), mf, mh)
        elif no == 11: sub = "역전광장 10,417㎡ · 구 역사 이전(1,406㎡)"
        elif no == 14: sub = "연면적 %s㎡ · 최고 %d층 · 약 %d면(32㎡/면) · 라이너 2층" % (format(round(sum(b['gfa'] for b in M['BUILD'] if b.get('role') == '주차')), ","), mf, round(S["park_spaces"]))
        elif no == 5: sub = "연면적 %s㎡ · 최고 %d층 · 약 %d세대(전용 36㎡ 기준)" % (format(round(gfa), ","), mf, round(S["units36"]))
        else: sub = "연면적 %s㎡ · 최고 %d층 %.1f m" % (format(round(gfa), ","), mf, mh)
        ax.text(1.4, y - 0.62, sub, fontsize=7.4, va="center", color="#555"); y -= 1.95
    y -= 0.4
    ax.text(0, y, "가로 (폭 m)", fontsize=11, fontweight="bold", va="top"); y -= 1.6
    for k in ("A", "B", "C", "D", "S", "R6", "R7", "R8", "R9", "S2", "E"):
        d = T["st_info"][k]
        ax.text(0, y, "%s  %s · %.0f m" % (k, d["desc"].split(" — ")[0], d["w"]), fontsize=8, va="center"); ax.text(10, y, "%s" % d["cls"].split("(")[0], fontsize=7.5, va="center", ha="right", color="#666"); y -= 1.05
    y -= 0.6
    ax.text(0, y, "총괄", fontsize=11, fontweight="bold", va="top"); y -= 1.7
    lines = [("경계(구역) 면적", "%s㎡" % format(round(S["U"]), ",")), ("건물 매스(조각) / 건축면적", "%d개 / %s㎡" % (S["n_pieces"], format(round(S["bld_fp"]), ","))), ("지상 연면적", "%s㎡" % format(round(S["bld_gfa"]), ",")),
             ("청년주거(전용 36㎡/60㎡)", "약 %d / %d세대" % (round(S["units36"]), round(S["units60"]))), ("시청·의회 연면적", "%s㎡ (목표 25,400)" % format(round(S["city_gfa"]), ",")),
             ("주차전용건축물", "약 %d면 (+임시 평면 %d면)" % (round(S["park_spaces"]), round(S["sp_spaces"]))), ("도로·골목 면적(교차부 광장 포함)", "%s㎡ (%.1f%%)" % (format(round(S["road_total"]), ","), S["road_total"] / S["U"] * 100)),
             ("공원·녹지·광장(공공)", "%s㎡ (%.1f%%)" % (format(round(T["open_public"]["녹지띠"] + T["open_public"]["수변공원"] + T["open_public"]["광장_역전광장"] + T["open_public"]["광장_환승"] + T["open_public"]["교차부광장"]), ","),
                                                 (T["open_public"]["녹지띠"] + T["open_public"]["수변공원"] + T["open_public"]["광장_역전광장"] + T["open_public"]["광장_환승"] + T["open_public"]["교차부광장"]) / S["U"] * 100)),
             ("공개공지·마당 포함", "%s㎡ (%.1f%%)" % (format(round(S["open_public"]), ","), S["open_public"] / S["U"] * 100))]
    for k, v in lines:
        ax.text(0, y, k, fontsize=8.2, va="center"); ax.text(10, y, v, fontsize=8.2, va="center", ha="right", fontweight="bold"); y -= 1.05
    y -= 0.7
    ax.text(0, y, "※ 높이 = min(고도지구 20 m·15 m, 경계 켜 규칙, 프로그램 층수). 법정 수치는 원문 대조 전 가정.", fontsize=7, va="top", color="#777")
    fig.savefig(path, dpi=150, facecolor="#ffffff"); plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
def fig_context(path):
    x0, y0, x1, y1 = U.buffer(95).bounds
    aspect = (y1 - y0) / (x1 - x0); pw = 8.6; lw_ = 3.6
    fig = plt.figure(figsize=(pw + lw_, pw * aspect + 0.5)); ax = fig.add_axes([lw_ / (pw + lw_), 0.01, pw / (pw + lw_), 0.95])
    base_plan(ax, (x0, y0, x1, y1), flat_context=True, trees=False, rails=False, show_new=False)
    # 원화로 횡단 제안(서측 앵커 폭 ≥3 m 지점) — 원화로 폭 30 m(NGII)
    for yy in (360659, 360796, 360957, 361100, 361245):
        ax.plot([219611, 219641], [yy, yy], color="#111", lw=3.2, ls=(0, (1.2, 1.0)), zorder=30, solid_capstyle="butt")
    ax.text(219590, 360900, "원화로 횡단보도(제안)\n서측 앵커 5곳", fontsize=7, ha="right", va="center", color="#111", zorder=60, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#111", lw=0.5, alpha=0.9))
    # 켜 띠
    b1 = U.difference(U.buffer(-40)); b2 = U.buffer(-40).difference(U.buffer(-90)); b3 = U.buffer(-90)
    for g, c, a in ((b1, "#e4572e", 0.22), (b2, "#f2a93b", 0.20), (b3, "#76b041", 0.20)):
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc=c, ec="none", alpha=a, zorder=3.5))
    # 기존 가로(NGII, 폭 3 m↑)
    for r in C["R"]:
        if r["w"] >= 3 and r["geom"].distance(U) < 95:
            col = "#c0392b" if r["w"] >= 15 else "#e08a00" if r["w"] >= 8 else "#2f6fba" if r["w"] >= 5 else "#7a8aa0"
            for l in (r["geom"].geoms if hasattr(r["geom"], "geoms") else [r["geom"]]):
                ax.plot(*l.xy, color=col, lw=0.6 + r["w"] / 9, alpha=0.9, zorder=7, solid_capstyle="round")
    # 신규 가로
    for k, g in NET["streets"].items():
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#2b2b2b" if k in ("A", "B", "C", "D", "S", "S2", "E") else "#6d5a3c", ec="white", lw=0.6, alpha=0.85, zorder=8))
    for k, g in NET["lanes"].items():
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#8a8a8a", ec="white", lw=0.4, alpha=0.9, zorder=8))
    for p in polys(NET["green_all"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#7fc15a", ec="#4a8a2a", lw=0.5, alpha=0.9, zorder=8))
    for nm, g in M["EXTRA"]["path"]:
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#8a8a8a", ec="none", zorder=8))
    # 기존 정류장
    try:
        bs = json.load(open(r"C:\Users\OFFICE\Desktop\9_도시\archive\C_data\raw\busstops_gj.geojson", encoding="utf-8"))
        from pyproj import Transformer
        tt = Transformer.from_crs(4326, 5187, always_xy=True)
        nb = 0
        for f in bs["features"]:
            gx, gy = f["geometry"]["coordinates"][:2]; px, py = tt.transform(gx, gy)
            if x0 < px < x1 and y0 < py < y1 and Point(px, py).distance(U) < 120:
                ax.plot(px, py, "s", color="#1f77b4", ms=4.5, mec="white", mew=0.5, zorder=20); nb += 1
    except Exception as e:
        nb = 0
    # 앵커 화살표
    col = {"도로·골목 연결": "#1a9850", "열린 통로(광장·마당)": "#f0a000", "막힘(건물)": "#d62728"}
    for r in AS["after"]:
        dx, dy = r["inward"] if r.get("inward") else (0, 0)
        c = col.get(r["status"], "#999")
        ax.annotate("", xy=(r["x"] + dx * 24, r["y"] + dy * 24), xytext=(r["x"] - dx * 10, r["y"] - dy * 10), arrowprops=dict(arrowstyle="-|>", color=c, lw=1.6 if r["w"] >= 3 else 0.9, mutation_scale=9), zorder=25)
        ax.plot(r["x"], r["y"], "o", color=c, ms=4.2 if r["w"] >= 3 else 2.8, mec="white", mew=0.5, zorder=26)
        if r["w"] >= 5: ax.text(r["x"] + (-8 if r["side"] == "서" else 8), r["y"] + 4, "%.0fm" % r["w"], fontsize=6.5, ha="right" if r["side"] == "서" else "left", zorder=27, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))
    ax.plot(*U.exterior.xy, color="#8a2be2", lw=2.0, zorder=40)
    # 변별 규칙 라벨
    rules = {"서": "서측 · 원화로 가로벽\n켜1 ≤3층·길이 ≤22 m\n최저고도지구 띠(원화로변)",
             "동": "동측 · 황오동 1~2층 골목 조직\n켜1 ≤2층·길이 ≤15 m\n골목 폭 4 m·교차 간격 31 m"}
    ax.text(U.bounds[0] - 62, 361120, rules["서"], fontsize=8.5, ha="center", va="center", rotation=90, color="#a0261a", fontweight="bold", zorder=60, bbox=dict(boxstyle="round", fc="white", ec="#a0261a", alpha=0.9))
    ax.text(U.bounds[2] + 62, 361000, rules["동"], fontsize=8.5, ha="center", va="center", rotation=90, color="#a0261a", fontweight="bold", zorder=60, bbox=dict(boxstyle="round", fc="white", ec="#a0261a", alpha=0.9))
    ax.text(219745, U.bounds[1] - 38, "남측 · 원효로·고분 방향\n켜1 ≤2층·길이 ≤17 m", fontsize=8, ha="center", va="center", color="#a0261a", fontweight="bold", zorder=60, bbox=dict(boxstyle="round", fc="white", ec="#a0261a", alpha=0.9))
    ax.text(219845, 361465, "북측 · 북천 수변", fontsize=8, ha="center", va="center", color="#a0261a", fontweight="bold", zorder=60, bbox=dict(boxstyle="round", fc="white", ec="#a0261a", alpha=0.9))
    h = [Line2D([0], [0], color="#c0392b", lw=3, label="기존 가로 폭 ≥15 m (원화로·알천남로)"), Line2D([0], [0], color="#e08a00", lw=2.4, label="기존 가로 폭 8~15 m"), Line2D([0], [0], color="#2f6fba", lw=1.6, label="기존 가로 폭 5~8 m"), Line2D([0], [0], color="#7a8aa0", lw=1.0, label="기존 가로·골목 3~5 m"),
         Patch(fc="#2b2b2b", ec="white", label="신규 차량·보차공존·공유 가로(A,B,C,D,S,S2,E)"), Patch(fc="#6d5a3c", ec="white", label="신규 보행자전용도로(R6,R7,R8,R9)"), Patch(fc="#8a8a8a", ec="white", label="신규 보행골목(켜1 이어받기)"), Patch(fc="#7fc15a", label="녹지띠"),
         Line2D([0], [0], marker="s", color="w", markerfacecolor="#1f77b4", markersize=6, label="기존 버스정류장(BIS 2025-10)"),
         Line2D([0], [0], marker=">", color="#1a9850", lw=1.6, label="앵커 → 도로·골목으로 연결"), Line2D([0], [0], marker=">", color="#f0a000", lw=1.6, label="앵커 → 열린 통로(광장·마당)"), Line2D([0], [0], marker=">", color="#d62728", lw=1.6, label="앵커 → 건물에 막힘(폭 2 m대, 선택 보정)"),
         Patch(fc="#e4572e", alpha=0.35, label="켜1 경계 0~40 m(이어받기)"), Patch(fc="#f2a93b", alpha=0.35, label="켜2 40~90 m(전이)"), Patch(fc="#76b041", alpha=0.35, label="켜3 90 m 이상(대형 프로그램)")]
    h.append(Line2D([0], [0], color="#111", lw=3, ls=(0, (1.2, 1.0)), label="원화로 횡단보도(제안)"))
    fig.legend(handles=h, loc="upper left", fontsize=8, framealpha=0.95, bbox_to_anchor=(0.005, 0.985), title="맥락 접속도\n기존 가로(NGII 연속수치지도)와 신규 가로망", title_fontsize=8.5)
    st = collections.Counter(r["status"] for r in AS["after"])
    s5 = [r for r in AS["after"] if r["w"] >= 5]; s3 = [r for r in AS["after"] if 3 <= r["w"] < 5]; s2 = [r for r in AS["after"] if r["w"] < 3]
    ok = lambda L: sum(r["status"] != "막힘(건물)" for r in L)
    ax.text(0.5, 0.985, "구경주역 도시계획안 — 주변 가로 접속·경계 켜 구분", transform=ax.transAxes, ha="center", va="top", fontsize=13, fontweight="bold", zorder=100)
    ax.text(0.5, 0.962, "경계에 닿는 기존 가로 %d개 중 폭 5 m↑ %d/%d · 3~5 m %d/%d · 2~3 m %d/%d 연결 (관통 통로 %d개 보정)" % (len(AS["after"]), ok(s5), len(s5), ok(s3), len(s3), ok(s2), len(s2), len(AS["carved"])),
            transform=ax.transAxes, ha="center", va="top", fontsize=8.5, color="#333", zorder=100)
    fig.savefig(path, dpi=140); plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
def fig_zoning(path):
    x0, y0, x1, y1 = U.buffer(30).bounds
    aspect = (y1 - y0) / (x1 - x0); pw = 9.0
    fig = plt.figure(figsize=(pw, pw * aspect + 0.5)); ax = fig.add_axes([0.01, 0.01, 0.98, 0.95]); ax.set_facecolor("#efeeea")
    for b in C["B"]:
        if not U.contains(b["geom"].representative_point()):
            for p in polys(b["geom"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#e6e2d8", ec="none", zorder=1))
    COL = {"공원·녹지": CATCOL["오픈스페이스"], "공공(체육·생활SOC)": CATCOL["여가·오락·체육"], "주거": CATCOL["주거"], "공공청사": CATCOL["문화·교육·공공"], "문화": CATCOL["여가·오락·체육"],
           "업무(창업지원)": CATCOL["상업·업무"], "공공(주민공동)": "#8fbfe8", "창조산업": CATCOL["창조산업"], "상업(전통시장 연계)": CATCOL["판매·음식"], "광장·역사문화": "#d9b99b",
           "교통·관광지원": "#cfcfcf", "주차": "#9a9a9a", "상업(관광 휴게·판매)": "#f6b5d0"}
    for b in NET["blocks"]:
        info = T["blk_info"][b["id"]]
        for p in polys(b["geom"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc=COL.get(info["major"], "#ddd"), ec="#333", lw=0.8, alpha=0.85, zorder=3))
    for p in polys(NET["green_all"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc=CATCOL["오픈스페이스"], ec="#4a8a2a", lw=0.6, alpha=0.8, zorder=3))
    for k, g in list(NET["streets"].items()) + list(NET["lanes"].items()):
        for p in polys(g): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#ffffff", ec="#888", lw=0.5, zorder=4))
    for p in polys(NET["plaza_extra"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#ffffff", ec="#888", lw=0.4, zorder=4))
    for b in M["BUILD"]:
        for p in polys(b["geom"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="white", ec="#555", lw=0.25, alpha=0.55, zorder=5))
    for b in NET["blocks"]:
        info = T["blk_info"][b["id"]]; c = b["geom"].representative_point()
        ax.text(c.x, c.y, "%s\n%s\n%s㎡" % (b["id"], info["label"], format(round(b["area"]), ",")), fontsize=6.3, ha="center", va="center", zorder=10, linespacing=1.15,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#555", lw=0.4, alpha=0.88))
    for k, (pts, w, cls, desc, basis) in NET["STREETS"].items():
        ln = LineString(pts).intersection(U)
        if ln.is_empty: continue
        mid = ln.interpolate(0.5, normalized=True)
        ax.text(mid.x, mid.y, "%s %.0fm" % (k, w), fontsize=6, ha="center", va="center", zorder=12, bbox=dict(boxstyle="round,pad=0.12", fc="#fff6cc", ec="#aa8", lw=0.4))
    ax.plot(*U.exterior.xy, color="#8a2be2", lw=2, zorder=20)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")
    ax.text(0.5, 0.985, "구경주역 도시계획안 — 가구(블록) 구획·조닝도", transform=ax.transAxes, ha="center", va="top", fontsize=13, fontweight="bold", zorder=30)
    ax.text(0.5, 0.962, "가구 19개 · 도로·골목 %s㎡ · 녹지띠 %s㎡ · 합계 = 경계 %s㎡ (오차 0)" % (format(round(NET["road_all"].area), ","), format(round(NET["green_all"].area), ","), format(round(U.area), ",")),
            transform=ax.transAxes, ha="center", va="top", fontsize=8.5, zorder=30)
    h = [Patch(fc=v, ec="#333", label=k) for k, v in COL.items()]
    lg = ax.legend(handles=h, loc="lower left", fontsize=6.8, framealpha=0.95, bbox_to_anchor=(0.005, 0.005), title="가구 대분류", title_fontsize=7.5); lg.set_zorder(100)
    fig.savefig(path, dpi=140); plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
def fig_height(path):
    x0, y0, x1, y1 = U.buffer(30).bounds
    aspect = (y1 - y0) / (x1 - x0); pw = 8.0
    fig = plt.figure(figsize=(pw, pw * aspect + 0.5)); ax = fig.add_axes([0.01, 0.01, 0.98, 0.95]); ax.set_facecolor("#efeeea")
    for b in C["B"]:
        if not U.contains(b["geom"].representative_point()):
            col = "#d8d3c8" if b["floors"] <= 2 else "#cbc5b8" if b["floors"] <= 4 else "#b9b2a4"
            for p in polys(b["geom"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc=col, ec="#b5afa2", lw=0.2, zorder=2))
    for p in polys(U): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#ffffff", ec="none", zorder=1))
    # 도심15m 지구
    for g in C["G"]:
        if g["h_max"] == 15 and g["kind"] == "최고":
            for p in polys(g["geom"].intersection(U)): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#fff0c8", ec="#e0a000", lw=0.6, hatch="\\\\\\\\", alpha=0.7, zorder=2.5))
        if g["kind"] == "최저":
            for p in polys(g["geom"].intersection(U)): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#e3d3f5", ec="#8a4fb8", lw=0.6, alpha=0.6, zorder=2.5))
    for p in polys(unary_union([NET["road_all"], NET["plaza_extra"]])): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#f0efe9", ec="none", zorder=2.8))
    for p in polys(NET["green_all"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc="#cfe6b4", ec="none", zorder=2.8))
    PAL = {1: "#fde9a8", 2: "#f9c46b", 3: "#f19a4a", 4: "#d9622f", 5: "#a4322b"}
    for b in M["BUILD"]:
        for p in polys(b["geom"]): ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc=PAL[min(b["floors"], 5)], ec="#d62728" if b["exc"] else "#7a5a3a", lw=1.4 if b["exc"] else 0.25, zorder=6))
    for d, ls, lab in ((40, (0, (6, 3)), "경계 40 m"), (90, (0, (2, 2)), "경계 90 m")):
        g = U.buffer(-d)
        for p in polys(g): ax.plot(*p.exterior.xy, color="#444", lw=0.9, ls=ls, zorder=7)
    ax.plot(*U.exterior.xy, color="#8a2be2", lw=1.8, zorder=8)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")
    ax.text(0.5, 0.985, "층수·높이 — min(고도지구, 경계 켜 규칙, 프로그램)", transform=ax.transAxes, ha="center", va="top", fontsize=12.5, fontweight="bold")
    fl = collections.Counter(min(b["floors"], 5) for b in M["BUILD"])
    ax.text(0.5, 0.963, "높이 상한 초과 %d건 · 켜 규칙 층수 초과 %d건(예외 %d건 = 주차전용건축물, 적색 윤곽) · 조각 %d개" % (T["chk"]["n_over_height"], T["chk"]["n_over_sidecap"], T["chk"]["n_exception"], len(M["BUILD"])), transform=ax.transAxes, ha="center", va="top", fontsize=8.2)
    h = [Patch(fc=PAL[i], ec="#7a5a3a", label="%d층 (%d조각)" % (i, fl.get(i, 0))) for i in range(1, 6)]
    h += [Patch(fc="#fff0c8", ec="#e0a000", hatch="\\\\\\\\", label="도심15m 고도지구(최고 15 m)"), Patch(fc="#e3d3f5", ec="#8a4fb8", label="최저고도지구(원화로변, 최저 높이 미확인)"),
          Line2D([0], [0], color="#444", ls=(0, (6, 3)), label="경계에서 40 m"), Line2D([0], [0], color="#444", ls=(0, (2, 2)), label="경계에서 90 m"), Patch(fc="white", ec="#d62728", lw=1.4, label="켜 규칙 예외")]
    lg = ax.legend(handles=h, loc="lower left", fontsize=7, framealpha=0.95, bbox_to_anchor=(0.005, 0.005)); lg.set_zorder(100)
    fig.savefig(path, dpi=140); plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
def fig_sections(path):
    cuts = [("① y=361,167 시청·의회 ↔ 청년주거", 361167), ("② y=361,038 복합문화·영화관 ↔ 창업·커뮤니티", 361038), ("③ y=360,870 성동시장 연계 ↔ 레지던시·공방", 360870), ("④ y=360,725 역전광장 ↔ 관광지원 ↔ 주차타워", 360725)]
    xmin, xmax = 219570, 220010
    fig, axs = plt.subplots(len(cuts), 1, figsize=(13, 2.4 * len(cuts) + 0.9)); fig.suptitle("동서 단면 입면 — 원화로(서) → 황오동(동): 3층 → 5층 → 2층 스케일 전이  (수직 2배 과장)", fontsize=12.5, fontweight="bold", y=0.995)
    VE = 2.0
    for ax, (title, y0) in zip(axs, cuts):
        w = 28
        band = box(xmin - 50, y0 - w, xmax + 50, y0 + w)
        items = []
        for b in C["B"]:
            if b["geom"].intersects(band) and not U.contains(b["geom"].representative_point()): items.append((b["geom"].intersection(band), b["floors"] * 3.5, "#c9c3b6", abs(b["geom"].centroid.y - y0), False))
        for b in M["BUILD"]:
            if b["geom"].intersects(band): items.append((b["geom"].intersection(band), b["h"], bcolor(b), abs(b["geom"].centroid.y - y0), b["geom"].intersects(LineString([(xmin - 50, y0), (xmax + 50, y0)]))))
        items.sort(key=lambda t: -t[3])
        for g, h, col, dist, cut in items:
            for p in polys(g):
                x_a, _, x_b, _ = p.bounds
                f = 0.78 + 0.22 * max(0, 1 - dist / 34)
                ax.add_patch(Rectangle((x_a, 0), x_b - x_a, h * VE, fc=shade(col, f), ec="#444" if cut else "#999", lw=0.8 if cut else 0.25, zorder=3 + (2 if cut else 0)))
        # 경계·켜
        line = LineString([(xmin - 50, y0), (xmax + 50, y0)]).intersection(U)
        xs = [g.bounds for g in (line.geoms if hasattr(line, "geoms") else [line])]
        wx, ex = min(b[0] for b in xs), max(b[2] for b in xs)
        for a, b_, c in ((wx, wx + 40, "#e4572e"), (wx + 40, wx + 90, "#f2a93b"), (ex - 90, ex - 40, "#f2a93b"), (ex - 40, ex, "#e4572e")):
            ax.add_patch(Rectangle((a, -3.5), b_ - a, 3, fc=c, ec="none", alpha=0.7, zorder=2))
        ax.add_patch(Rectangle((wx + 90, -3.5), ex - 90 - (wx + 90), 3, fc="#76b041", ec="none", alpha=0.7, zorder=2))
        ax.axvline(wx, color="#8a2be2", lw=1.2, ls="--", zorder=1); ax.axvline(ex, color="#8a2be2", lw=1.2, ls="--", zorder=1)
        # 고도 상한선(20 m, 동측 15 m 띠)
        ax.plot([xmin, xmax], [20 * VE] * 2, color="#d62728", lw=0.9, ls=(0, (5, 3)), zorder=1)
        ax.text(xmin + 2, 20 * VE + 1.2, "고도지구 20 m", fontsize=7, color="#d62728")
        ax.plot([xmin, xmax], [0, 0], color="#333", lw=1.2, zorder=6)
        ax.set_xlim(xmin, xmax); ax.set_ylim(-4.5, 24 * VE); ax.set_aspect("equal"); ax.set_yticks([0, 10 * VE, 20 * VE]); ax.set_yticklabels(["0", "10 m", "20 m"], fontsize=7)
        ax.set_xticks([wx + d for d in (0, 50, 100, 150, 200, 250, 300) if wx + d <= xmax]); ax.set_xticklabels(["%d m" % d for d in (0, 50, 100, 150, 200, 250, 300) if wx + d <= xmax], fontsize=6.5)
        ax.tick_params(axis="x", length=2, pad=1); ax.set_title(title, fontsize=9, loc="left", pad=2)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
        ax.text(wx - 6, 2.5, "원화로", fontsize=7.5, ha="right", color="#555"); ax.text(ex + 6, 2.5, "황오동", fontsize=7.5, ha="left", color="#555")
    used = {b["cat"] for b in M["BUILD"]}
    h = [Patch(fc=CATCOL[k], ec="#555", label=k) for k in LEG_ORDER if k in used] + [Patch(fc="#c9c3b6", ec="#999", label="기존 건물(NGII 층수×3.5 m)"), Patch(fc="#e4572e", alpha=0.7, label="켜1 0~40 m"), Patch(fc="#f2a93b", alpha=0.7, label="켜2 40~90 m"), Patch(fc="#76b041", alpha=0.7, label="켜3 90 m↑")]
    fig.legend(handles=h, loc="lower center", ncol=7, fontsize=7.5, frameon=False)
    fig.tight_layout(rect=[0, 0.05, 1, 0.97]); fig.savefig(path, dpi=140); plt.close(fig)

def fig_urban(path):
    """도시 스케일 조감: 원도심(반경 ~280 m) 안에서 본 부지."""
    x0, y0, x1, y1 = U.buffer(240).bounds
    aspect = (y1 - y0) / (x1 - x0); pw = 11.0
    fig = plt.figure(figsize=(pw, pw * aspect + 0.4)); ax = fig.add_axes([0.005, 0.005, 0.99, 0.965])
    base_plan(ax, (x0, y0, x1, y1), tilt=0.5, trees=True, rails=False)
    ax.text(0.5, 0.995, "구경주역 도시계획안 — 원도심 속 도시 스케일 (회색=기존 건물, 층수×3.5 m)", transform=ax.transAxes, ha="center", va="top", fontsize=13, fontweight="bold", zorder=100,
            bbox=dict(boxstyle="round", fc="white", ec="none", alpha=0.85))
    north_scale(ax, (x0, y0, x1, y1), L=200)
    fig.savefig(path, dpi=110); plt.close(fig)

if __name__ == "__main__":
    which = sys.argv[1:] or ["main", "context", "zoning", "height", "sections", "urban"]
    fn = {"main": ("01_도시계획안_매스_마스터플랜.png", fig_main), "context": ("02_맥락_접속도.png", fig_context), "zoning": ("03_가구구획_조닝도.png", fig_zoning),
          "height": ("04_층수_높이도.png", fig_height), "sections": ("05_동서_단면입면.png", fig_sections), "urban": ("06_도시스케일_조감.png", fig_urban)}
    for k in which:
        name, f = fn[k]; f(OUT + "\\" + name); print("saved", name)
