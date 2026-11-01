"""K7 면적표 — 통영 보고서 p.18 형식(Site Area 대상지 면적 / Facility Area 시설별 면적 / Keymap / 우측 이미지 띠) → 03_면적표.png/pdf"""
import sys
from plotkit import *
from matplotlib.image import imread
from shapely import affinity
from shapely.ops import polylabel

S = TC["site"]; F = TC["fac"]; TR = TC["lot_rows"]; PKS = {d["name"]: d for d in PARKS}
SH = "#ececec"; SEP = "#b5b5b5"

def fm(v): return format(int(round(v)), ",") + "㎡"
def pc(v, tot): return "%d%%" % round(v / tot * 100)

def pdf_table(pg, x, y, widths, rows, row_h=7.0, hdr=None, fs_en=8.0, fs_ko=7.0, fs_val=8.0):
    """통영 p.18 표 형식: 칸마다 음영(소계) 또는 하단 얇은 선, 칸 사이 흰 틈. rows: dict(en, ko, val, pct, sub, span)"""
    xs = [x]
    for w in widths: xs.append(xs[-1] + w)
    gap = 0.5
    if hdr:
        pg.line(x, y, xs[-1], y, c="#777", lw=0.5)
        t = pg.t(x + 1.5, y + 5.2, hdr[0], fs=10, bold=True)
        pg.fig.canvas.draw(); wmm = t.get_window_extent(pg.fig.canvas.get_renderer()).width / pg.fig.dpi * 25.4
        pg.t(x + 1.5 + wmm + 2.2, y + 5.4, hdr[1], fs=8, c="#444")
        y += 9.5
    yy = y
    for r in rows:
        sub = r.get("sub", False); span = r.get("span", False)
        cells = [(xs[0], xs[1]), (xs[1], xs[2]), (xs[2], xs[3]), (xs[3], xs[4])]
        if span: cells = [cells[0], cells[1], (xs[2], xs[4])]
        for ci, (a, b) in enumerate(cells):
            if sub: pg.rect(a + gap / 2, yy + gap / 2, b - a - gap, row_h - gap, fc=SH, z=1)
            else: pg.line(a + gap, yy + row_h, b - gap, yy + row_h, c=SEP, lw=0.4)
        two = "\n" in r.get("en", "")
        pg.t(xs[0] + 1.6, yy + row_h / 2, r["en"], fs=fs_en, linespacing=1.15)
        pg.t(xs[1] + 1.6, yy + row_h / 2, r["ko"], fs=fs_ko, c="#444", linespacing=1.15)
        if span:
            pg.t(xs[4] - 1.8, yy + row_h / 2, r["val"], fs=fs_val, ha="right")
        else:
            pg.t(xs[3] - 1.8, yy + row_h / 2, r["val"], fs=fs_val, ha="right")
            if r.get("pct"): pg.t(xs[4] - 1.8, yy + row_h / 2, r["pct"], fs=fs_val, ha="right")
        yy += row_h
    return yy

pg = Page()
# 우측 이미지 띠(조감) — 전폭 블리드
IMX = 283.0
img = imread(SP + r"\axo_v.png")
pg.ax.imshow(img, extent=[IMX, 420, 297, 0], aspect="auto", zorder=0, interpolation="bilinear")
pg.ax.set_xlim(0, 420); pg.ax.set_ylim(297, 0)
title_block(pg, "Overview : Overall Siteplan", "Summary + Site Plan", "개요 + 전체배치도", x=16, y=14,
            sub="규제 미적용 개념안 — 고도제한·용도지역·보존지역 허용기준 미반영. 면적은 도면에서 직접 산정(㎡)하며 합계가 계획 경계에 닫힘")

# ── Table 1 · Site Area ──────────────────────────────────────────────────────
T1X, T1Y = 16, 42
RH = 6.5
W1 = [43, 36, 33, 12]
rows1 = [
    dict(en="Station Site (Announced)", ko="폐역 부지(공고 면적)†", val=fm(79438), sub=True),
    dict(en="Planning Boundary", ko="계획 경계(작업 경계 U)", val=fm(S["U"]), sub=True),
    dict(en="Park A", ko="공원 A · 북천 수변공원", val=fm(S["park_A"])),
    dict(en="Park B", ko="공원 B · 동서 그린 보행축", val=fm(S["park_B"])),
    dict(en="Park C", ko="공원 C · 역전광장·근린공원", val=fm(S["park_C"])),
    dict(en="Other Park Area", ko="기타공원면적(환승·교차광장)", val=fm(S["park_other"])),
    dict(en="Water Area", ko="수공간(해당 없음)", val="-"),
    dict(en="Subtotal of Park", ko="공원면적 소계", val=fm(S["park_total"]), pct=pc(S["park_total"], S["planned"]), sub=True),
    dict(en="Vehicle Road", ko="차량도로(보차공존 포함)", val=fm(S["road_veh"])),
    dict(en="Pedestrian Road", ko="보행자전용도로·보행골목", val=fm(S["road_ped"])),
    dict(en="Subtotal of Road", ko="도로면적 소계", val=fm(S["road_total"]), pct=pc(S["road_total"], S["planned"]), sub=True)]
for no, a in S["lots"]: rows1.append(dict(en="Plot %d" % no, ko="획지 %d" % no, val=fm(a)))
rows1 += [dict(en="Subtotal of Usable Land", ko="획지면적 소계", val=fm(S["lot_total"]), pct=pc(S["lot_total"], S["planned"]), sub=True),
          dict(en="Planned Site Area", ko="계획부지 면적합계", val=fm(S["planned"]), sub=True)]
y1 = pdf_table(pg, T1X, T1Y, W1, rows1, row_h=RH, hdr=("Site Area", "대상지 면적"))

# ── Table 2 · Facility Area ─────────────────────────────────────────────────
T2X, T2Y = 150, 42
W2 = [42, 34, 29, 12]
tot = F["total"]
rows2 = []
for k, e, kr, v in F["rows"]:
    kr2 = kr
    rows2.append(dict(en=e, ko=kr2, val=fm(v) if v > 0 else "-", pct=("%d%%" % round(v / tot * 100)) if v > 0 else "0%"))
rows2 += [dict(en="Total GFA", ko="연면적 합계", val=fm(tot), sub=True, span=True),
          dict(en="FAR (Usable Land)", ko="용적률(가용부지기준)", val="%d%%" % round(F["far"] * 100), sub=True, span=True),
          dict(en="Coverage (Usable Land)", ko="건폐율(가용부지기준)", val="%d%%" % round(F["coverage"] * 100), sub=True, span=True)]
pf = F["park_fac"]
rows2 += [dict(en="Park A : Pavilion", ko="공원 A : 수변 쉼터·카페", val=fm(pf.get("Park A", 0)), span=True),
          dict(en="Park B : -", ko="공원 B : 시설 없음(연결녹지)", val="-", span=True),
          dict(en="Park C : Kiosk", ko="공원 C : 광장 매점·카페", val=fm(pf.get("Park C", 0)), span=True),
          dict(en="Other Facilities in the Park", ko="기타공원시설", val="-", span=True),
          dict(en="Subtotal of Park Facilities", ko="공원시설소계", val=fm(F["park_fac_total"]), sub=True, span=True),
          dict(en="Total GFA\n(included Park Facilities)", ko="연면적합계(공원시설포함)", val=fm(F["total_incl_park"]), sub=True, span=True)]
yh = T2Y
y2 = pdf_table(pg, T2X, T2Y, W2, rows2[:-1], row_h=RH, hdr=("Facility Area", "시설별 면적"))
# 마지막 행(두 줄)은 높이를 키운다
y2 = pdf_table(pg, T2X, y2, W2, rows2[-1:], row_h=9.6)
# 주차 제외 참고선
pg.t(T2X + 1.5, y2 + 4.6, "참고 · 주차전용건축물 제외 연면적 %s (용적률 %d%%)" % (fm(F["total_excl_parking"]), round(F["far_excl_parking"] * 100)), fs=6.6, c="#555")

# ── Keymap(북쪽 오른쪽으로 90° 돌려 놓음) ───────────────────────────────────────
KX, KY, KW, KH = 150, 186, 118, 62
rot = lambda g: affinity.affine_transform(g, [0, 1, -1, 0, 0, 0])     # (E,N) → (u=N, v=-E)
ax = pg.sub(KX, KY, KW, KH); ax.axis("off"); ax.set_aspect("equal")
Ur = rot(U); bx0, by0, bx1, by1 = Ur.bounds
sc = max((bx1 - bx0) / (KW - 4), (by1 - by0) / (KH - 4)); cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
ax.set_xlim(cx - KW * sc / 2, cx + KW * sc / 2); ax.set_ylim(cy - KH * sc / 2, cy + KH * sc / 2)
fill(ax, Ur, fc="#a9a9a9", z=1)
for d in LOTS: fill(ax, rot(d["geom"]), fc="#ececec", ec="white", lw=0.3, z=2)
for d in PARKS:
    fc = "#8cc63f" if d["name"] in ("Park A", "Park B", "Park C") else "#b9dc84"
    fill(ax, rot(d["geom"]), fc=fc, ec="white", lw=0.3, z=2)
for d in LOTS:
    p = rot(d["geom"]); pt = polylabel(max(polys(p), key=lambda g: g.area), 1.0)
    ax.text(pt.x, pt.y, str(d["no"]), fontsize=6.4, fontweight="bold", ha="center", va="center", zorder=5)
for d in PARKS:
    p = rot(d["geom"]); pt = polylabel(max(polys(p), key=lambda g: g.area), 1.0)
    ax.text(pt.x, pt.y, d["name"].replace("Plaza D", "Plaza D"), fontsize=5.6, fontweight="bold", ha="center", va="center", zorder=5, color="#1d3b0f")
pg.t(KX + KW + 1, KY + KH - 3, "Keymap", fs=8.5, bold=True, ha="right", va="bottom")
# 방위(키맵은 북쪽이 오른쪽)
pg.ax.annotate("", xy=(KX + KW - 4, KY + 4), xytext=(KX + KW - 18, KY + 4), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8)); pg.t(KX + KW - 2, KY + 4, "N", fs=7, bold=True)

# ── 각주 ─────────────────────────────────────────────────────────────────────
fy = y1 + 5
foot = ["† 경주시 공개 구상(2026.02) 기준 면적 — 언론 경유 [T4, 원문 미확인]. 계획 경계 U는 작업 경계(v3 규칙)이며 폐역 부지 공고 면적과 직접 비교하지 않는다.",
        "· 연면적 = 지상층 건축면적 × 층수의 단순 합. 1층을 판매·음식으로 쓰는 매스는 해당 1층만 Retail / F&B 행에 집계(총합 불변). 용적률·건폐율은 획지면적(가용지) 기준.",
        "· 숙박(Hotel)은 사용자 스케치에 없어 0 — 구상 프로그램의 'STAY'는 미반영(결정 필요).  주차전용건축물 연면적의 용적률 산입 여부는 건축법 시행령 제119조 해석 필요 [T1, 원문 미확인].",
        "· 공원면적 비율은 %d%% — 참고 보고서(통영, 30%%)보다 낮다. 대상지 여건이 달라 단순 비교는 하지 않는다." % round(S["park_total"] / S["planned"] * 100)]
for i, s in enumerate(foot): pg.t(T1X, fy + i * 4.2, s, fs=5.8, c="#555")

# ── 우측 띠 위 획지 번호(조감도 카메라 투영) ──────────────────────────────────────
import pickle as _pk
import k4_axo as K
meta = _pk.load(open(SP + r"\axo_v_meta.pkl", "rb"))
cam = K.Cam(meta["az"], meta["el"], meta["W"], meta["H"], meta["ps"], meta["xc"], meta["yc"])
def mm_of(px, py): return IMX + px * (420 - IMX) / meta["W"], py * 297.0 / meta["H"]
for r in TR:
    d = [l for l in LOTS if l["no"] == r["no"]][0]
    bl = unary_union([b["geom"] for b in BUILD if b["lot_no"] == d["no"]]).buffer(2.0); free = d["geom"].difference(bl)
    free = max(polys(free), key=lambda g: g.area) if not free.is_empty else d["geom"]
    pt = polylabel(free, 1.0) if free.area > 60 else d["geom"].representative_point()
    xm, ym = mm_of(*cam.xy(pt.x, pt.y, 1.0 if r["maxf"] > 3 else 0.5))
    pg.ax.add_patch(Circle((xm, ym), 2.6, fc="white", ec=INK, lw=0.6, zorder=8)); pg.t(xm, ym + 0.1, str(r["no"]), fs=6.2, bold=True, ha="center", z=9)
for d in PARKS:
    pt = polylabel(max(polys(d["geom"]), key=lambda g: g.area), 1.0)
    xm, ym = mm_of(*cam.xy(pt.x, pt.y, 1.0)); lab = d["name"].replace("Park ", "").replace("Plaza ", "")
    pg.ax.add_patch(Circle((xm, ym), 2.6, fc="#2e7d32", ec="white", lw=0.6, zorder=8)); pg.t(xm, ym + 0.1, lab, fs=6.2, bold=True, c="white", ha="center", z=9)

# ── 우측 띠 위 범례 ──────────────────────────────────────────────────────────
lgx, lgy = IMX + 6, 262
pg.rect(lgx - 3, lgy - 5.5, 137 - 6 + 0.0, 38, fc="white", ec="none", z=6, alpha=0.78)
for i, cat in enumerate(CATORDER[:-1]):
    cx0 = lgx + (i % 2) * 64; cy0 = lgy + (i // 2) * 6.6
    pg.rect(cx0, cy0 - 2, 5, 4, fc=CATCOL[cat], ec="#555", lw=0.25, z=7); pg.t(cx0 + 6.5, cy0, "%s" % cat, fs=6.6, z=7)
    pg.t(cx0 + 6.5 + len(cat) * 2.25 + 1, cy0, CATEN[cat], fs=5.0, c="#666", z=7)
pg.ax.annotate("", xy=(412, 24), xytext=(412, 38), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0), zorder=7)
pg.t(412, 21, "N", fs=8, bold=True, ha="center", z=7)
pg.t(IMX - 6, 291, "03", fs=8, c="#666", ha="right")
pg.save(OUT + r"\03_면적표.png", dpi=170, pdf=OUT + r"\03_면적표.pdf")
pg.save(SP + r"\p03.png", dpi=110)
print("saved p03; table1 end y=%.1f  table2 end y=%.1f" % (y1, y2))
