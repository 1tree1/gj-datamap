"""G4 획지계획도 + 획지계획표(16:9) — 획지별 성격·배치·규모(최종본 건축물 기준)"""
from gkit import *
from shapely.ops import polylabel

CHAR = {1: "행정 거점 · 청사 앞 시민광장", 2: "청사 부설 주차 · 청사 연결 브리지", 3: "생활체육 거점 · 체육공원 접속", 4: "청년·신혼 정주 · 1층 근린생활 연결동",
        5: "공공업무 + 청년창업 · 방문객 노외주차", 6: "생활문화·돌봄 · 소공원·공동체텃밭", 7: "전통공예 생산·전시·판매 · 공예 중정", 8: "작가 레지던시 · 체험 · 제작–거주 브리지",
        9: "구 경주역 어댑티브 리유즈 · 그레이트 코트", 10: "관광 안내 · 방문자 지원", 11: "관문 가로상가 · 관문 가로광장", 12: "근대역사관 · 사선 보행축 상부 연결",
        13: "공유주차 · 모빌리티 허브"}
pg = Page()
pg.header("Masterplan : Plot Plan", "Plot Plan + Plot Schedule", "획지계획도 + 획지계획표",
          sub="획지 13개의 성격·배치·규모 — 층수 = 높이 ÷ 층고(주거 3.0·주차 3.2·그 외 4.0 m)")
EXT = (-10, 460, 30, 1030)
ax = pg.plan_ax(4, 31, 128, 192, EXT)
context(ax, EXT, fc="#f0f0ee", ec="#e2e2df")
for g in S["ROADS"].values(): fill(ax, g, fc="#ffffff", ec="#cfcfcb", lw=0.3, z=1)
fill(ax, S["WALK"], fc="#f2f2f0", z=1); fill(ax, S["PATH8"], fc="#f2f2f0", z=1)
for o in S["OPEN"]: fill(ax, o["g"], fc="#e2f0d4", z=1.1)
for p in S["PARKS"]: fill(ax, p["g"], fc="#cfe6b8", z=1.1)
for l in S["LOTS"]: fill(ax, l["g"], fc=tint(LOTCOL[l["cat"]], 0.62), ec="white", lw=0.8, z=1.2)
for b in BLD:
    c = LOTCOL.get(b["main"], "#bbbbbb")
    fill(ax, b.get("detail_fp", b["g"]) if b["name"] == "구 경주역사" else b["g"], fc=c, ec=shade(c, 0.7), lw=0.35, z=1.4)
for k in LINKS: fill(ax, k["g"], fc="none", ec="#333333", lw=0.5, z=1.5, ls=(0, (2, 1.2)))
xs, ys = B.exterior.xy; ax.plot(xs, ys, color=RED, lw=0.9, ls=(0, (4, 2)), zorder=6)
BU = unary_union([b["g"] for b in BLD])
for l in S["LOTS"]:
    pt = lot_label_pt(l, avoid=BU)
    ax.add_patch(Circle((pt.x, pt.y), 12.5, fc="white", ec=INK, lw=0.7, zorder=20))
    ax.text(pt.x, pt.y, str(l["no"]), fontsize=10, ha="center", va="center", fontweight="bold", zorder=21)
ax.text(250, 905, "북측 근린공원", fontsize=10, ha="center", va="center", color="#2e6b2a", fontweight="bold", zorder=21, path_effects=halo(2.0))
north_scale(ax, 260, 55, fs=9, north_at=(440, 135))

pg.top()
# ── 획지계획표(10 pt) — 획지명·용지 / 성격 두 줄, 수치는 한 줄 ──
tx, ty = 140, 31
cols = ["", "획지명 · 용지", "성격", "획지㎡", "건축㎡", "건폐율", "연면적㎡", "용적률", "최고"]
wd = [9, 64, 66, 20, 18, 17, 22, 17, 13]
xs_ = [tx]
for w in wd: xs_.append(xs_[-1] + w)
RH = 13.0
pg.rect(tx, ty, sum(wd), 6.4, fc="#3c3c3c", z=5)
for i, c in enumerate(cols): pg.t(xs_[i] + wd[i] / 2, ty + 3.2, c, fs=10, c="white", ha="center", bold=True, z=6)
yy = ty + 6.4
for r, l in enumerate(sorted(LOTS, key=lambda l: l["no"])):
    pg.rect(tx, yy, sum(wd), RH, fc="white" if r % 2 == 0 else "#f7f7f5", z=5)
    c = LOTCOL[l["cat"]]
    pg.rect(xs_[0], yy, 1.6, RH, fc=c, z=6)
    pg.ax.add_patch(Circle((xs_[0] + 5.6, yy + RH / 2), 3.0, fc="white", ec=INK, lw=0.5, zorder=7)); pg.t(xs_[0] + 5.6, yy + RH / 2 + 0.1, str(l["no"]), fs=10, ha="center", bold=True, z=8)
    pg.t(xs_[1] + 1.2, yy + 3.6, l["name"], fs=10, bold=True, z=6)
    pg.t(xs_[1] + 1.2, yy + 9.0, l["use"], fs=10, c=GREY, z=6)
    L = wrap_mm(pg, CHAR[l["no"]], wd[2] - 2.4)
    for j, ln in enumerate(L[:2]): pg.t(xs_[2] + 1.2, yy + RH / 2 + (j - (min(len(L), 2) - 1) / 2) * 5.0, ln, fs=10, z=6)
    pg.t(xs_[4] - 1.2, yy + RH / 2, f0(l["area"]), fs=10, ha="right", z=6)
    pg.t(xs_[5] - 1.2, yy + RH / 2, f0(l["ba"]), fs=10, ha="right", z=6)
    pg.t(xs_[6] - 1.2, yy + RH / 2, "%.0f%%" % (l["bcr"] * 100), fs=10, ha="right", bold=True, z=6)
    pg.t(xs_[7] - 1.2, yy + RH / 2, f0(l["gfa"]), fs=10, ha="right", z=6)
    pg.t(xs_[8] - 1.2, yy + RH / 2, "%.0f%%" % (l["far"] * 100), fs=10, ha="right", bold=True, z=6)
    pg.t(xs_[8] + wd[8] / 2, yy + 3.8, "%d층" % l["maxf"], fs=10, ha="center", bold=True, z=6)
    pg.t(xs_[8] + wd[8] / 2, yy + 9.0, "%.0f m" % l["maxh"], fs=10, ha="center", c=GREY, z=6)
    yy += RH
pg.rect(tx, yy, sum(wd), 6.6, fc="#d9d9d5", z=5)
pg.t(xs_[1] + 1.2, yy + 3.3, "합계 · 획지 13", fs=10, bold=True, z=6)
for k_, v in ((4, f0(TOT["lot"])), (5, f0(TOT["ba"])), (6, "%.1f%%" % (TOT["bcr"] * 100)), (7, f0(TOT["gfa"])), (8, "%.1f%%" % (TOT["far"] * 100))):
    pg.t(xs_[k_] - 1.2, yy + 3.3, v, fs=10, bold=True, ha="right", z=6)
yy += 6.6
pg.line([tx, tx + sum(wd)], [yy, yy], c="#3c3c3c", lw=0.8, z=7)
# 범례(지도 왼쪽 아래)
LEG = ["공공업무", "업무·창업", "문화", "창작", "판매", "생활SOC", "주거", "역사", "방문자", "주차"]
lx, ly = 4, 32
pg.rect(lx, ly, 46, 4 + (len(LEG) + 1) * 5.0, fc="white", ec="#cccccc", lw=0.4, z=30, alpha=0.95)
for i, key in enumerate(LEG):
    y_ = ly + 4.4 + i * 5.0
    pg.rect(lx + 2.5, y_ - 1.4, 4.0, 2.8, fc=LOTCOL[key], z=31); pg.t(lx + 8.5, y_, CATS[key][1], fs=10, z=31)
y_ = ly + 4.4 + len(LEG) * 5.0
pg.line([lx + 2.5, lx + 6.5], [y_, y_], c="#333", lw=0.6, z=31, ls=(0, (2, 1.2))); pg.t(lx + 8.5, y_, "브리지·캐노피", fs=10, z=31)
pg.save("D4_획지계획도")
