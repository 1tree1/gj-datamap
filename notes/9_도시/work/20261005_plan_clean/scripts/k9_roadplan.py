"""K9 도로계획도 + 도로계획표 (A3 가로) — 도로 성격(차량·공유·보행·골목), 폭원, 단면 구성(계획 가정), 기존 가로와의 연결 앵커 → 04_도로계획도_도로계획표.png/pdf"""
import sys, textwrap
from plotkit import *
from k6_helpers import grid_table

RR = TC["road_rows"]; S = TC["site"]; RN = TC["RNAME"]
ANCH = pickle.load(open(SP + r"\anchors.pkl", "rb"))
GCOL = {"차량": "#5d7fb0", "S": "#f19a3e", "보행": "#d1495b", "골목": "#a58bd0"}
def rcol(r): return GCOL["S"] if r["key"] == "S" else GCOL[r["group"]]
SEGCOL = {"차도": "#707070", "공유": "#f19a3e", "식재": "#9ccc65", "보도": "#e6dcc3", "보행": "#e6dcc3"}
def segcol(name):
    if "공유 차도" in name: return SEGCOL["공유"]
    if "차도" in name: return SEGCOL["차도"]
    if "식재" in name and "보행" not in name and "보도" not in name: return SEGCOL["식재"]
    if "식재" in name: return "#c8d9a0"
    return SEGCOL["보도"]

pg = Page()
title_block(pg, "Road Plan : Street Character", "Road Plan + Road Schedule", "도로계획도 + 도로계획표", x=16, y=16,
            sub="폭원·성격은 이 안의 계획값. 단면 구성은 계획 가정(설계 단계에서 확정). 도시·군계획시설 도로 규모별 구분(중로·소로 N류)은 경계값 원문 확인 후 부여한다 [T1, 원문 미확인].")

# ── 도면 ──
x0, y0, x1, y1 = U.buffer(48).bounds
PX, PY, PW, PH = 10, 42, 108, 250
ax = pg.sub(PX, PY, PW, PH); ax.axis("off"); ax.set_aspect("equal")
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; sc = max((x1 - x0) / PW, (y1 - y0) / PH)
ax.set_xlim(cx - PW * sc / 2, cx + PW * sc / 2); ax.set_ylim(cy - PH * sc / 2, cy + PH * sc / 2)
ext = (cx - PW * sc / 2, cy - PH * sc / 2, cx + PW * sc / 2, cy + PH * sc / 2)
ax.add_patch(Rectangle((ext[0], ext[1]), ext[2] - ext[0], ext[3] - ext[1], fc="#f6f6f4", ec="none", zorder=0))
draw_roads_ctx(ax, ext, z=0.4); draw_context(ax, ext, fc="#e3e3df", z=0.8)
fill(ax, U, fc="#f1f1ee", z=2)
for d in PARKS: fill(ax, d["geom"], fc="#d9ecc3", ec="none", z=3)
for d in LOTS: fill(ax, d["geom"], fc="#ffffff", ec="#c9c9c9", lw=0.3, z=3)
for b in BUILD: fill(ax, b["geom"], fc="#dcdcd8", ec="none", z=3.5)
used = []
from shapely.ops import unary_union as UU
roads = {}
for k, v in NET["streets"].items(): roads[k] = v
for k, v in NET["lanes"].items(): roads[k] = v
for r in RR:                                     # 우선순위 순서(RR 순서)로 그려 교차부는 상위 도로 색
    g = roads[r["key"]].difference(UU(used)) if used else roads[r["key"]]
    used.append(roads[r["key"]]); fill(ax, g, fc=rcol(r), ec="white", lw=0.25, z=5)
fill(ax, LP["plaza"], fc="#cfcfcb", z=4.5)
for d in PARKS:
    if d["name"] == "Plaza D": fill(ax, d["geom"], fc="#cfcfcb", z=4.5)
ax.add_patch(PathPatch(path_of(Polygon(U.exterior)), fc="none", ec="#7a2bd6", lw=0.9, ls=(0, (4, 2)), zorder=7))
# 도로 이름·폭
for key, g, w in road_label_points():
    L = g.length; p = g.interpolate(0.5 * L); q = g.interpolate(min(L, 0.5 * L + 4)); a = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
    if a > 90: a -= 180
    if a < -90: a += 180
    if L < 60: continue
    ax.text(p.x, p.y, "%s %gm" % (key if key != "S" else "S", w), fontsize=5.6, rotation=a, rotation_mode="anchor", ha="center", va="center", color="white", fontweight="bold", zorder=9)
for key in ("L_N3",):
    pass
# 기존 가로 끝(앵커) 표시 — 폭 8 m 이상만 숫자
for a in ANCH:
    ax.add_patch(Circle((a["x"], a["y"]), 4.0, fc="white", ec="#c0392b", lw=0.8, zorder=10))
    if a["w"] >= 8: ax.text(a["x"] + (7 if a["side"] == "동" else -7), a["y"], "%gm" % a["w"], fontsize=4.6, color="#c0392b", ha="left" if a["side"] == "동" else "right", va="center", zorder=11, fontweight="bold", path_effects=halo(1.4, "#f6f6f4"))
for d in LOTS:
    pt = d["geom"].representative_point(); ax.text(pt.x, pt.y, str(d["no"]), fontsize=5.4, color="#8a8a8a", ha="center", va="center", zorder=6)
ax.annotate("", xy=(ext[0] + 14 * sc, ext[3] - 6 * sc), xytext=(ext[0] + 14 * sc, ext[3] - 20 * sc), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8), zorder=12)
ax.text(ext[0] + 14 * sc, ext[3] - 4 * sc, "N", fontsize=7, ha="center", va="top", fontweight="bold", zorder=12)
sb0 = ext[0] + 30 * sc; sby = ext[1] + 8 * sc
for i in range(2): ax.add_patch(Rectangle((sb0 + i * 50, sby), 50, 5, fc=INK if i == 0 else "white", ec=INK, lw=0.5, zorder=12))
for dx, s in ((0, "0"), (50, "50"), (100, "100 m")): ax.text(sb0 + dx, sby + 7, s, fontsize=5.5, ha="center", va="bottom", zorder=12)
pg.t(PX, PY - 2.5, "도로계획도 (북쪽 위, 1:%s @A3)" % format(int(round(sc * 1000 / 100) * 100), ","), fs=7, c="#555")

# ── 범례(도면 아래) ──
lg = [(GCOL["차량"], "차량·보차공존 가로"), (GCOL["S"], "공유가로 S(보행 우선)"), (GCOL["보행"], "보행자전용"), (GCOL["골목"], "보행자우선 골목(6 m)")]
lx, ly = 12, 296 - 0.0
# ── 표 ──
cols = [("", 3.5, "c"), ("도로", 17, "l"), ("도로 성격", 31, "l"), ("폭원\n(m)", 9, "r"), ("연장\n(m)", 9, "r"), ("면적\n(㎡)", 12, "r"), ("통행 방식", 31, "l"), ("단면 구성 (m, 축척 약 2.4 mm/m)", 44, "l"), ("역할 · 기존 가로와의 연결(앵커)", 100, "l")]
rows = []; shade = []
for r in RR:
    role = textwrap.wrap(r["role"].replace("≈", "~"), 46)[:2]
    anc = textwrap.wrap(r["anchor"].replace("≈", "~"), 52)[:1]
    cell_role = [(role[0], dict(fs=5.8))] + ([(role[1], dict(fs=5.8))] if len(role) > 1 else []) + ([(anc[0] + ("…" if len(r["anchor"]) > 52 else ""), dict(fs=5.2, c="#777"))] if anc else [])
    mode = [(s, dict(fs=5.9)) for s in textwrap.wrap(r["mode"], 17)[:2]]
    rows.append(["", (RN[r["key"]], dict(fs=7.0, bold=True)), (r["kind"], dict(fs=6.4)), "%g" % r["w"], format(round(r["L"]), ","), format(round(r["area_excl"]), ","), mode, "", cell_role])
tg = {g: sum(r["area_excl"] for r in RR if r["group"] == g) for g in ("차량", "보행", "골목")}
for lab, val in (("차량 도로 소계 (A·S·B·C·D·S2·E)", tg["차량"]), ("보행자전용 소계 (R6~R9)", tg["보행"]), ("보행 골목 소계 (골목 5개)", tg["골목"]), ("도로 합계", S["road_total"])):
    rows.append(["", (lab, dict(fs=6.8, bold=True)), "", "", "", (format(round(val), ","), dict(bold=True)), "", "", ("면적표 Vehicle Road %s㎡ + Pedestrian Road %s㎡ = %s㎡" % (format(round(S["road_veh"]), ","), format(round(S["road_ped"]), ","), format(round(S["road_total"]), ",")) if lab == "도로 합계" else "", dict(fs=5.8, c="#555"))])
    shade.append(len(rows) - 1)
TX = 124; RH = 11.2; HH = 9.5; TY = 44
yend = grid_table(pg, TX, TY, cols, rows, hdr_h=HH, row_h=[RH] * len(RR) + [6.4] * (len(rows) - len(RR)), shade_rows=shade)
# 소계행은 낮게: 위 함수는 행 높이 고정 — 다시 덮어쓰지 않고 그대로 둔다(행 높이 동일)
# 칩·단면 도식
xs = [TX]
for _, w, _ in cols: xs.append(xs[-1] + w)
for i, r in enumerate(RR):
    yy = TY + HH + i * RH
    pg.rect(TX + 0.8, yy + 1.6, 1.9, RH - 3.2, fc=rcol(r), z=4)
    # 단면
    k = 2.4; sx = xs[7] + 1.5; sy = yy + RH / 2 - 2.4
    for name, wd in r["cross_list"]:
        pg.rect(sx, sy, wd * k, 4.8, fc=segcol(name), ec="white", lw=0.3, z=4)
        if wd * k >= 5: pg.t(sx + wd * k / 2, sy + 2.45, "%g" % wd, fs=4.6, c="#222" if segcol(name) not in ("#707070", "#f19a3e") else "white", ha="center", z=5)
        sx += wd * k
    short = " · ".join(n.replace("(양방 2차로)", "").replace("(셔틀·서비스)", "").replace("(일방)", "") for n, _ in r["cross_list"][:5])
    pg.t(xs[7] + 1.5, sy + 7.6, short if len(short) < 38 else short[:36] + "…", fs=4.3, c="#666")
# 범례(표 아래)
ly = yend + 6
pg.t(TX, ly, "범례", fs=7, bold=True)
ex = TX + 11
for c, s in lg:
    pg.rect(ex, ly - 2, 5, 4, fc=c, ec="#555", lw=0.25); pg.t(ex + 6.5, ly, s, fs=6.2); ex += 6.5 + len(s) * 2.2 + 5
pg.ax.add_patch(Circle((ex + 2, ly), 1.9, fc="white", ec="#c0392b", lw=0.8)); pg.t(ex + 5.5, ly, "기존 가로 끝(앵커) %d개 — 숫자는 기존 폭" % len(ANCH), fs=6.2)
ex2 = ex + 5.5 + 62
for k, (n, c) in enumerate((("보도·보행", "#e6dcc3"), ("식재·자전거", "#9ccc65"), ("차도", "#707070"), ("공유 차도", "#f19a3e"))):
    pg.rect(ex2, ly - 2, 5, 4, fc=c, ec="#555", lw=0.25); pg.t(ex2 + 6.5, ly, n, fs=6.2); ex2 += 6.5 + len(n) * 2.2 + 4
notes = ["· 차량 도로는 보차공존(30 km/h) — A가로가 화랑로(원화로 접속)를 부지 안으로 연결하고, S축은 폐선축과 나란한 60 m 동편 종축으로 셔틀·서비스·비상 차량만 통행하는 보행 우선 공유가로.",
         "· 기존 가로 끝(앵커)은 연속수치지도 도로 중심선(NGII, T2)에서 추출. 폭은 'rvwd' 속성값이며 현황 확인 전. 단면 구성(차도·보도·식재 폭)은 이 안의 계획 가정이다.",
         "· 사선 보행축 R6(14 m)은 황오동에서 원화로·원효로 코너(고분 방향)로 대각선 관통 — 부지를 폐선축(80.3 km)과 분리하지 않고 시 전체 보행축에 잇는 역할(S3 해석)."]
for i, s in enumerate(notes): pg.t(TX, ly + 8 + i * 4.4, s, fs=5.9, c="#444")
pg.t(412, 291, "04", fs=8, c="#666", ha="right")
pg.save(OUT + r"\04_도로계획도_도로계획표.png", dpi=170, pdf=OUT + r"\04_도로계획도_도로계획표.pdf")
pg.save(SP + r"\p04.png", dpi=110)
print("saved p04")
