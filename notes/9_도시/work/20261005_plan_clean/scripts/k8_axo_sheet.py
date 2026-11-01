"""K8 조감도 시트 'Site Anchors' (A3 가로) — 렌더 이미지 위에 획지 번호·호출선·범례·획지 목록을 얹는다 → 02_조감도_SiteAnchors.png/pdf"""
import sys, pickle, textwrap
from plotkit import *
import k4_axo as K
from matplotlib.image import imread
from shapely.ops import polylabel

TR = TC["lot_rows"]; S = TC["site"]; F = TC["fac"]; SM = TC["summary"]
IMG = SP + r"\axo_sheet.png"; META = pickle.load(open(SP + r"\axo_sheet_meta.pkl", "rb"))
cam = K.Cam(META["az"], META["el"], META["W"], META["H"], META["ps"], META["xc"], META["yc"])
def mm(x, y, z=0.0):
    px, py = cam.xy(x, y, z); return px * 420.0 / META["W"], py * 297.0 / META["H"]

pg = Page()
pg.ax.imshow(imread(IMG), extent=[0, 420, 297, 0], aspect="auto", zorder=0, interpolation="bilinear"); pg.ax.set_xlim(0, 420); pg.ax.set_ylim(297, 0)
title_block(pg, "Masterplan : Site Anchors", "Site Anchors", "획지별 앵커·용도 구성", x=16, y=14,
            sub="규제 미적용 개념안 — 획지 구획·용도·층수만 정리한 매스 (고도제한·용도지역·보존지역 허용기준 미반영, 참고용)")
pg.t(16, 38.5, "연면적 %s㎡ · 용적률 %d%% · 건폐율 %d%% (획지 %s㎡ 기준) · 공원·녹지·광장 %s㎡(%.1f%%) · 도로 %s㎡(%.1f%%)" % (
    format(round(F["total"]), ","), round(F["far"] * 100), round(F["coverage"] * 100), format(round(S["lot_total"]), ","), format(round(S["park_total"]), ","),
    S["park_total"] / S["planned"] * 100, format(round(S["road_total"]), ","), S["road_total"] / S["planned"] * 100), fs=7.2, c="#444")

# ── 획지 번호 마커 ──
mk = {}
for r in TR:
    d = [l for l in LOTS if l["no"] == r["no"]][0]
    bl = unary_union([b["geom"] for b in BUILD if b["lot_no"] == d["no"]]).buffer(2.0); free = d["geom"].difference(bl)
    free = max(polys(free), key=lambda g: g.area) if not free.is_empty else d["geom"]
    pt = polylabel(free, 1.0) if free.area > 60 else d["geom"].representative_point()
    x, y = mm(pt.x, pt.y, r["maxh"] * 0.0 + 6.0 + r["maxh"] * 0.55)
    if r["no"] == 15:                                   # 구 역사 한 동뿐인 획지 — 번호 마커를 건물 위에 둔다(광장 가장자리가 아니라)
        c15 = unary_union([b["geom"] for b in BUILD if b["lot_no"] == 15]).centroid
        x, y = mm(c15.x, c15.y, r["maxh"] + 8.0)
    mk[r["no"]] = (x, y)
for r in TR:
    x, y = mk[r["no"]]
    pg.ax.add_patch(Circle((x, y), 3.0, fc="white", ec=INK, lw=0.7, zorder=8)); pg.t(x, y + 0.1, str(r["no"]), fs=7.4, bold=True, ha="center", z=9)
pmk = {}
for d in PARKS:
    pt = polylabel(max(polys(d["geom"]), key=lambda g: g.area), 1.0); x, y = mm(pt.x, pt.y, 8.0); lab = d["name"].replace("Park ", "").replace("Plaza ", "")
    pmk[d["name"]] = (x, y)
    pg.ax.add_patch(Circle((x, y), 3.0, fc="#2e7d32", ec="white", lw=0.8, zorder=8)); pg.t(x, y + 0.1, lab, fs=7.4, bold=True, c="white", ha="center", z=9)

# ── 호출선(통영 p.32 형식: 마커에서 수직으로 내려 L자로 꺾어 글에 닿음) ──
CALL = [
    (18, "관광상가 · Plot 18·19", "남단 관문. 3층 ㄱ자 둘레형(카페·식당·기념품)이 사선 보행축 R6의 끝을 받는다."),
    (15, "구 역사 이전 · Plot 15", "기존 역사 건물(1,404㎡·2층)을 형상 그대로 역전광장 앞으로 옮겨 근대역사관·전시장으로 쓴다."),
    (10, "성동시장 · Plot 10", "2층 장옥 바 6열 + 삼층석탑 마당(반경 22 m). 서변은 3층 가로상점."),
    ("B", "동서 그린 보행축 · Park B", "B가로 양측 녹지띠 %s㎡. 종축 S와 십자로 만나는 연결녹지." % format(round(S["park_B"]), ",")),
    (8, "청년창업 · Plot 8", "둘레 6층, 북서 모서리 8층 랜드마크. 1층은 판매·지원 시설."),
    (4, "청년주거 · Plot 2·4·5·6", "둘레형 4~6층, 1층 근린생활. 약 %d~%d세대(전용 70%%·36~60㎡ 가정)." % (round(SM["units60"], -1), round(SM["units36"], -1)))]
BW = 41.0; YT = 264.0
pg.rect(0, YT - 3.2, 420, 29.0, fc="white", ec="none", z=5, alpha=0.66)       # 호출선 글 아래 반투명 띠 — 주변 건물 위에서도 읽히게
# 글 시작 x: 마커 x를 따르되 이웃 글과 겹치지 않도록 최소 간격(BW+1.5)을 둔다(왼→오른쪽으로 밀고, 오른쪽 끝을 넘으면 되돌려 민다)
order = sorted(range(len(CALL)), key=lambda i: (pmk["Park B"] if CALL[i][0] == "B" else mk[CALL[i][0]])[0])
XS = {}
for i in order: XS[i] = min(max((pmk["Park B"] if CALL[i][0] == "B" else mk[CALL[i][0]])[0], 12.0), 420 - BW - 6)
for a, b in zip(order, order[1:]): XS[b] = max(XS[b], XS[a] + BW + 1.5)
lim = 420 - BW - 6
for a, b in zip(order[::-1], order[::-1][1:]):
    if XS[a] > lim: XS[a] = lim
    XS[b] = min(XS[b], XS[a] - BW - 1.5)
for ci, (key, ttl, desc) in enumerate(CALL):
    x, y = pmk["Park B"] if key == "B" else mk[key]
    xs = XS[ci]
    # 호출선: 마커에서 수직으로 내려 연결선(YT)에서 꺾고, 글은 연결선 아래에 둔다 → 이웃 호출선이 글을 가로지르지 않는다
    pg.line(x, y + 3.0, x, YT, c="#333", lw=0.6, z=6); pg.line(x, YT, xs + 2.6, YT, c="#333", lw=0.6, z=6); pg.line(xs + 2.6, YT, xs + 2.6, YT + 2.4, c="#333", lw=0.6, z=6)
    pg.ax.add_patch(Circle((x, YT), 0.55, fc="#333", ec="none", zorder=7))
    pg.t(xs + 4.0, YT + 3.6, ttl, fs=7.4, bold=True, va="center", path_effects=halo(1.8, "white"))
    for j, ln in enumerate(textwrap.wrap(desc, 17)): pg.t(xs + 4.0, YT + 7.9 + j * 3.5, ln, fs=6.3, c="#333", va="center", path_effects=halo(1.6, "white"))

# ── 획지 목록 패널(좌상) ──
px0, py0 = 12, 44.5
pg.rect(px0, py0, 282, 29.5, fc="white", ec="none", z=6, alpha=0.80)
ent = [(str(r["no"]), r["name"], "%s㎡ · %dF" % (format(round(r["area"]), ","), r["maxf"]), CATCOL[r["cat"]]) for r in TR]
ent += [(d["name"].replace("Park ", "").replace("Plaza ", ""), {"Park A": "북천 수변공원", "Park B": "동서 그린 보행축", "Park C": "역전광장·근린공원", "Plaza D": "환승광장"}[d["name"]],
         "%s㎡" % format(round(d["area"]), ","), "#2e7d32") for d in PARKS]
for i, (n, nm, ar, col) in enumerate(ent):
    c, rr = divmod(i, 6); x = px0 + 3 + c * 70; y = py0 + 3.5 + rr * 4.4
    pg.ax.add_patch(Circle((x + 2.0, y), 1.75, fc=col if n.isalpha() else "white", ec=INK if not n.isalpha() else "white", lw=0.45, zorder=8))
    pg.t(x + 2.0, y + 0.1, n, fs=5.6, bold=True, ha="center", c="white" if n.isalpha() else INK, z=9)
    if not n.isalpha(): pg.rect(x + 4.6, y - 1.6, 1.3, 3.2, fc=col, z=8)
    pg.t(x + 7.0, y, nm, fs=6.1, z=9); pg.t(x + 69 - 2.5, y, ar, fs=5.6, c="#555", ha="right", z=9)

# ── 범례 ──
ly = 292.0
pg.rect(0, ly - 4.2, 420, 8.4, fc="white", ec="none", z=6, alpha=0.86)
pg.t(16, ly, "범례", fs=7, bold=True, z=9)
ex = 28
for cat in CATORDER[:-1]:
    pg.rect(ex, ly - 2, 5, 4, fc=CATCOL[cat], ec="#555", lw=0.25, z=9); pg.t(ex + 6.5, ly, cat, fs=6.5, z=9); ex += 6.5 + len(cat) * 2.3 + 6
pg.rect(ex, ly - 2, 5, 4, fc="#9fd36b", ec="#555", lw=0.25, z=9); pg.t(ex + 6.5, ly, "옥상녹화·공원", fs=6.5, z=9)
pg.t(404, ly, "02", fs=8, c="#666", ha="right", z=9)
pg.save(OUT + r"\02_조감도_SiteAnchors.png", dpi=170, pdf=OUT + r"\02_조감도_SiteAnchors.pdf")
pg.save(SP + r"\p02.png", dpi=110)
print("saved p02")
