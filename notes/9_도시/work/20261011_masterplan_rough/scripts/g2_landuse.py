"""G2 토지이용계획도 + 토지이용계획표(16:9) — 참고: Bucha 토지이용계획(용지 색 평면 + 구분·면적·비율 표)"""
from gkit import *
from matplotlib.patches import FancyArrowPatch

pg = Page()
B_ = TOT["boundary"]
pg.header("Masterplan : Land Use", "Land Use Plan", "토지이용계획도 + 토지이용계획표",
          sub="최종 마스터플랜(2026-10-11) 도면 산정 — 구역 %s㎡ · 획지 13 · 근린공원 3 · 보행자전용도로·광장 4 · 도로 3" % f0(B_))
EXT = (-230, 640, -25, 1040)
ax = pg.plan_ax(8, 30, 222, 190, EXT)
context(ax, EXT)
ground(ax, z=1.0, road_fc="#636363")      # 차량 도로 진한 회색 #636363(사용자 요청)
# 획지 번호(이름은 표에서 번호로 찾음 — 10 pt에서는 작은 획지에 용지명이 들어가지 않음)
LB = {}
for l in S["LOTS"]:
    pt = lot_label_pt(l)
    ax.add_patch(Circle((pt.x, pt.y), 10.5, fc="white", ec=INK, lw=0.7, zorder=20))
    ax.text(pt.x, pt.y, str(l["no"]), fontsize=10, ha="center", va="center", fontweight="bold", zorder=21)
from shapely.ops import polylabel
ax.text(250, 905, "북측 근린공원", fontsize=10, ha="center", va="center", zorder=21, color="#2e6b2a", fontweight="bold", path_effects=halo(2.0))
ax.text(150, 496, "동서 선형공원·가로광장", fontsize=10, ha="left", va="center", zorder=21, color="#2e6b2a", fontweight="bold", path_effects=halo(2.0))
# 연결 화살표 — 보행(초록 점선) · 차량(진회색)
def arrow(p, q, c, ls="-", lw=1.4, z=25):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>,head_length=4,head_width=2.4", color=c, lw=lw, ls=ls, zorder=z, mutation_scale=1.0, shrinkA=0, shrinkB=0))
GRN = "#2f8f3a"; CAR = "#4a4a4a"
for p, q in (((104, 496), (-150, 496)), ((406, 496), (590, 496)), ((118, 66), (40, -12)), ((271, 775), (271, 775))):
    if p != q: arrow(p, q, GRN, ls=(0, (3, 2)), lw=1.3)
for p, q in (((104, 778.5), (-40, 778.5)), ((350, 888), (420, 968)), ((104, 343.7), (-40, 343.7)), ((412, 343.7), (560, 343.7)), ((242.4, 56), (242.4, -2))):
    arrow(p, q, CAR, lw=1.5)
ax.text(-150, 512, "원도심 방면", fontsize=10, color=GRN, ha="left", va="bottom", fontweight="bold", path_effects=halo(2.0))
ax.text(590, 512, "동측 생활권", fontsize=10, color=GRN, ha="right", va="bottom", fontweight="bold", path_effects=halo(2.0))
ax.text(30, -8, "관광객 주출입구", fontsize=10, color=GRN, ha="right", va="top", fontweight="bold", path_effects=halo(2.0))
north_scale(ax, -215, 10, fs=9, north_at=(-190, 90))
pg.top()
# 범례(평면 왼쪽 위)
lx, ly = 10, 33
items = [("line", RED, (0, (4, 2)), "구역 경계"), ("arrow", GRN, (0, (3, 2)), "보행 연결"), ("arrow", CAR, "-", "차량 진출입"), ("box", "#636363", None, "차량 도로"), ("box", "#e6e6e3", None, "주변 건축물")]
pg.rect(lx, ly, 46, 4 + len(items) * 5.6, fc="white", ec="#cccccc", lw=0.4, z=30, alpha=0.95)
for i, (k, c, ls, t) in enumerate(items):
    yy = ly + 4.8 + i * 5.6
    if k == "line": pg.line([lx + 3, lx + 11], [yy, yy], c=c, lw=1.0, z=31, ls=ls)
    elif k == "arrow": pg.ax.add_patch(FancyArrowPatch((lx + 3, yy), (lx + 11, yy), arrowstyle="-|>,head_length=2.2,head_width=1.3", color=c, lw=0.9, ls=ls, zorder=31, mutation_scale=1.0))
    else: pg.rect(lx + 3, yy - 1.5, 8, 3.0, fc=c, ec="#cfcfcb", lw=0.3, z=31)
    pg.t(lx + 14, yy, t, fs=10, z=31)

# ── 토지이용계획표 ──
A = lambda nos: sum(l["area"] for l in S["LOTS"] if l["no"] in nos)
oa = {o["key"]: o["g"].area for o in S["OPEN"]}
pa = {p["key"]: p["g"].area for p in S["PARKS"]}
ra = {k: g.area for k, g in S["ROADS"].items()}
GR = [
    ("공공시설용지", None, [("① 공공청사용지", [1], LOTCOL["공공업무"]), ("② 주차장용지(청사 부설)", [2], LOTCOL["주차"]), ("③ 체육시설용지", [3], LOTCOL["생활SOC"])]),
    ("주거용지", None, [("④ 공동주택용지(청년·신혼 공공임대)", [4], LOTCOL["주거"])]),
    ("업무·상업용지", None, [("⑤ 업무복합용지", [5], LOTCOL["업무·창업"]), ("⑪ 판매시설용지", [11], LOTCOL["판매"])]),
    ("문화·관광시설용지", None, [("⑥ 생활문화복합용지", [6], LOTCOL["문화"]), ("⑦⑧ 문화특화용지(공예·창작)", [7, 8], LOTCOL["창작"]), ("⑨ 역사문화시설용지(구 경주역)", [9], LOTCOL["역사"]),
                          ("⑫ 문화시설용지(근대역사관)", [12], LOTCOL["문화"]), ("⑩ 관광편의시설용지", [10], LOTCOL["방문자"])]),
    ("교통시설용지", None, [("⑬ 주차장·교통시설용지", [13], LOTCOL["주차"])]),
]
rows, chips, subs = [], {}, []
for gname, _, items in GR:
    subs.append(len(rows)); tot = sum(A(n) for _, n, _ in items)
    rows.append([gname, f0(tot), "%.1f" % (tot / B_ * 100)])
    for nm, nos, c in items:
        chips[len(rows)] = c; rows.append(["   " + nm, f0(A(nos)), "%.1f" % (A(nos) / B_ * 100)])
subs.append(len(rows)); pk = sum(pa.values()); rows.append(["공원·녹지", f0(pk), "%.1f" % (pk / B_ * 100)])
for p in S["PARKS"]: chips[len(rows)] = PARKC; rows.append(["   근린공원(%s)" % p["name"], f0(p["g"].area), "%.1f" % (p["g"].area / B_ * 100)])
op = sum(oa.values()) + S["PATH8"].area
subs.append(len(rows)); rows.append(["보행자전용도로·광장", f0(op), "%.1f" % (op / B_ * 100)])
for o in S["OPEN"]: chips[len(rows)] = WALKC; rows.append(["   " + o["name"], f0(o["g"].area), "%.1f" % (o["g"].area / B_ * 100)])
chips[len(rows)] = SIDEC; rows.append(["   향일문 조망로(보행자전용도로, 폭 8m)", f0(S["PATH8"].area), "%.1f" % (S["PATH8"].area / B_ * 100)])
rd = sum(ra.values()) + S["WALK"].area
subs.append(len(rows)); rows.append(["도로·보도", f0(rd), "%.1f" % (rd / B_ * 100)])
for k, nm in (("N", "북측 차도(폭 13m)"), ("EW", "동서 도로(폭 20m)"), ("O", "동측·남측 외곽도로")):
    chips[len(rows)] = "#636363"; rows.append(["   " + nm, f0(ra[k]), "%.1f" % (ra[k] / B_ * 100)])
chips[len(rows)] = SIDEC; rows.append(["   외곽 보도", f0(S["WALK"].area), "%.1f" % (S["WALK"].area / B_ * 100)])
tot_all = sum(l["area"] for l in S["LOTS"]) + pk + op + rd
rows.append(["합계(구역)", f0(B_), "100.0"])
tx, ty = 236, 31.5
yy = table(pg, tx, ty, ["토지이용계획표 · 구분", "면적(㎡)", "비율(%)"], rows, [104, 28, 24], rh=5.25, fs=10, aligns=["left", "right", "right"], sub_rows=subs, bold_rows=[len(rows) - 1], color_chip=chips)
# 개발 규모(참고)
yy += 3.6
kv = [("획지 면적", "%s㎡" % f0(TOT["lot"])), ("건축면적", "%s㎡" % f0(TOT["ba"])), ("연면적(지상)", "%s㎡" % f0(TOT["gfa"])),
      ("건폐율·용적률", "%.1f%% · %.1f%%" % (TOT["bcr"] * 100, TOT["far"] * 100))]
pg.t(tx, yy, "개발 규모(획지 기준) — 연면적 %s㎡ · 건폐율 %.1f%% · 용적률 %.1f%% · 최고 %.0f m" % (f0(TOT["gfa"]), TOT["bcr"] * 100, TOT["far"] * 100,
     max(b["h"] for b in BLD if b["name"] != "구 경주역사")), fs=10, bold=True)
print("closure", round(B_ - tot_all, 2))
pg.save("D2_토지이용계획도")
