"""K6 획지 구획도 + 획지계획표 (A3 가로) → 01_획지구획도_획지계획표.png/pdf"""
import sys
from plotkit import *
from shapely.ops import polylabel

TR = TC["lot_rows"]; S = TC["site"]; F = TC["fac"]; RN = TC["RNAME"]
SHORT = {1: "체육센터 2F·생활SOC 3F·옥외 운동장", 2: "ㄷ자 둘레형 5F·1층 근린생활", 3: "ㄷ자 본청 5F·의회동 4F·시민동 3F", 4: "ㅁ자 둘레형 6F·통경 2곳·1층 근생",
         5: "ㄷ자 둘레형 4F", 6: "3층 연립 바 2열·골목마당", 7: "문화센터 4F·영화관 3F·가로상점 3F", 8: "ㅁ자 6F·북서 모서리 8F·1층 판매·지원",
         9: "3층 소규모 동 6개·마을마당", 10: "2층 장옥 바·3층 가로상점·삼층석탑 마당", 11: "2층 점포 2열·체험 거리", 12: "사선(56°) 3층 바 — 레지던시·공방",
         13: "사선 3층 바", 14: "사선 3층 바", 15: "구 역사(이전) 2F·근대역사관 겸용·역사 광장", 16: "주차 5F·4F + 2층 판매·공방 라이너",
         17: "3층 바(안내·환승 라운지)·승강장 앞마당", 18: "ㄱ자 둘레형 3F", 19: "ㄱ자 둘레형 3F"}
USE = {1: "공공체육·생활SOC", 2: "청년주거", 3: "공공청사(시청·의회)", 4: "청년주거", 5: "청년주거", 6: "청년주거(연립)", 7: "문화시설(복합문화·영화관)",
       8: "업무(청년창업·기업지원)", 9: "주민공동시설(커뮤니티)", 10: "근린상업(성동시장 연계)", 11: "근린상업(체험판매)", 12: "창작시설(레지던시·공방)",
       13: "창작시설(레지던시·공방)", 14: "창작시설(레지던시·공방)", 15: "문화·역사(구 역사·근대역사관)", 16: "주차전용건축물", 17: "관광지원시설",
       18: "관광 근린상업(휴게·판매)", 19: "관광 근린상업(휴게·판매)"}

def grid_table(pg, x, y, cols, rows, hdr_h=9.0, row_h=9.5, hdr_fs=6.8, shade_rows=(), line_c="#c8c8c8"):
    """cols: [(제목, 폭mm, 정렬)] rows: [[셀...]] 셀은 str 또는 (str, dict(fs,c,bold)) 또는 list(여러 줄)"""
    xs = [x]
    for _, w, _ in cols: xs.append(xs[-1] + w)
    pg.line(x, y, xs[-1], y, lw=0.9)
    for (title, w, al), x0 in zip(cols, xs[:-1]):
        tx = x0 + (w / 2 if al == "c" else (w - 1.5 if al == "r" else 1.5))
        pg.t(tx, y + hdr_h / 2, title, fs=hdr_fs, bold=True, ha={"c": "center", "r": "right", "l": "left"}[al], linespacing=1.15)
    pg.line(x, y + hdr_h, xs[-1], y + hdr_h, lw=0.5)
    yy = y + hdr_h
    for i, r in enumerate(rows):
        if i in shade_rows: pg.rect(x, yy, xs[-1] - x, row_h, fc=GREY, z=1)
        for (title, w, al), x0, cell in zip(cols, xs[:-1], r):
            lines = cell if isinstance(cell, list) else [cell]
            n = len(lines)
            for j, ln in enumerate(lines):
                sty = {}
                if isinstance(ln, tuple): ln, sty = ln
                fs = sty.get("fs", 7.0); c = sty.get("c", INK); bd = sty.get("bold", False)
                ty = yy + row_h / 2 + (j - (n - 1) / 2) * (row_h * 0.40 if n > 1 else 0)
                tx = x0 + (w / 2 if al == "c" else (w - 1.5 if al == "r" else 1.5))
                pg.t(tx, ty, ln, fs=fs, c=c, bold=bd, ha={"c": "center", "r": "right", "l": "left"}[al])
        yy += row_h
        pg.line(x, yy, xs[-1], yy, c=line_c, lw=0.35)
    pg.line(x, yy, xs[-1], yy, lw=0.9)
    return yy

pg = Page()
title_block(pg, "Lot Plan : Parcel Layout", "Lot Plan + Lot Schedule", "획지 구획도 + 획지계획표", x=16, y=16,
            sub="규제 미적용 개념안 — 고도제한·용도지역·보존지역 허용기준을 적용하지 않았다.  계획 경계 = 작업 경계 U (%s㎡)" % format(round(S["U"]), ","))

# ── 도면 ──
x0, y0, x1, y1 = U.buffer(48).bounds
PX, PY, PW, PH = 10, 42, 108, 250
ax = pg.sub(PX, PY, PW, PH); ax.axis("off"); ax.set_aspect("equal")
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; sc = max((x1 - x0) / PW, (y1 - y0) / PH)       # m per mm
ax.set_xlim(cx - PW * sc / 2, cx + PW * sc / 2); ax.set_ylim(cy - PH * sc / 2, cy + PH * sc / 2)
ext = (cx - PW * sc / 2, cy - PH * sc / 2, cx + PW * sc / 2, cy + PH * sc / 2)
ax.add_patch(Rectangle((ext[0], ext[1]), ext[2] - ext[0], ext[3] - ext[1], fc="#f6f6f4", ec="none", zorder=0))
draw_roads_ctx(ax, ext, z=0.4); draw_context(ax, ext, fc="#dcdcd8", z=0.8)
fill(ax, U, fc="#cfcfcb", z=2)                                                     # 도로(가로·광장)
for d in PARKS: fill(ax, d["geom"], fc="#c3e3a4", ec="#6aa84f", lw=0.35, z=3)
for d in LOTS:
    fill(ax, d["geom"], fc=tint(CATCOL[d["cat"]], 0.62), ec="#555", lw=0.45, z=3)
for lid, nm, g in M["COURTS"]: fill(ax, g, fc="#e1f0cf", z=3.5)
for lid, nm, g, col in M["OPEN"]: fill(ax, g, fc={"#cfe6b4": "#e1f0cf", "#d98a6a": "#e2a58a", "#cfcfcf": "#dddddd"}.get(col, col), z=3.5)
for b in BUILD: fill(ax, b["geom"], fc=CATCOL[b["cat"]], ec="#3a3a3a", lw=0.3, z=4)
ax.add_patch(PathPatch(path_of(Polygon(U.exterior)), fc="none", ec="#7a2bd6", lw=1.0, ls=(0, (4, 2)), zorder=6))
# 도로 이름
for key, g, w in road_label_points():
    L = g.length; p = g.interpolate(0.5 * L); q = g.interpolate(min(L, 0.5 * L + 4)); a = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
    if a > 90: a -= 180
    if a < -90: a += 180
    if L < 70: continue
    ax.text(p.x, p.y, "%s %gm" % (RN[key], w), fontsize=4.6, rotation=a, rotation_mode="anchor", ha="center", va="center", color="#333", zorder=8, path_effects=halo(1.6, "#cfcfcb"))
# 획지 번호 · 공원 이름
for d in LOTS:
    bl = unary_union([b["geom"] for b in BUILD if b["lot_no"] == d["no"]]).buffer(2.0)
    free = d["geom"].difference(bl); free = max(polys(free), key=lambda g: g.area) if not free.is_empty else d["geom"]
    pt = polylabel(free, 1.0) if free.area > 60 else d["geom"].representative_point()
    num_circle(ax, pt.x, pt.y, str(d["no"]), r=9.0, fs=6.8, z=10)
for d in PARKS:
    pt = polylabel(max(polys(d["geom"]), key=lambda g: g.area), 1.0)
    nm = {"Park A": "Park A", "Park B": "Park B", "Park C": "Park C", "Plaza D": "Plaza D"}[d["name"]]
    ax.text(pt.x, pt.y, nm, fontsize=5.8, ha="center", va="center", color="#2d5a1b", fontweight="bold", zorder=9, path_effects=halo(1.6, "#c3e3a4"))
# 방위·축척
nx, ny = ext[2] - 22 * sc / 1.0 * 0.5, ext[3] - 12 * sc
ax.annotate("", xy=(ext[0] + 14 * sc, ext[3] - 6 * sc), xytext=(ext[0] + 14 * sc, ext[3] - 20 * sc), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8), zorder=12)
ax.text(ext[0] + 14 * sc, ext[3] - 4 * sc, "N", fontsize=7, ha="center", va="top", fontweight="bold", zorder=12)
sb0 = ext[0] + 30 * sc; sby = ext[1] + 8 * sc
for i in range(2): ax.add_patch(Rectangle((sb0 + i * 50, sby), 50, 5, fc=INK if i == 0 else "white", ec=INK, lw=0.5, zorder=12))
for dx, s in ((0, "0"), (50, "50"), (100, "100 m")): ax.text(sb0 + dx, sby + 7, s, fontsize=5.5, ha="center", va="bottom", zorder=12)
pg.t(PX, PY - 2.5, "획지 구획도 (북쪽 위, 1:%s @A3)" % format(int(round(sc * 1000 / 100) * 100), ","), fs=7, c="#555")

# ── 표 ──
cols = [("획지", 9, "c"), ("획지명 / 시설 구성", 60, "l"), ("용도(계획)", 34, "l"), ("획지면적\n(㎡)", 16, "r"), ("건축면적\n(㎡)", 16, "r"), ("건폐율\n(%)", 11, "r"),
        ("연면적\n(㎡)", 16, "r"), ("용적률\n(%)", 11, "r"), ("층수 /\n높이", 15, "c"), ("접도(면한 도로)", 38, "l"), ("고도지구\n(참고)", 17, "c")]
rows = []; shade = []
for r in TR:
    no = r["no"]
    fr = " · ".join("%s %g" % (RN[k].replace("가로", "").replace("축", ""), w) for k, w in r["frontage"][:4])
    if r["parkfront"]: fr += " · " + "/".join(p.replace("Plaza ", "Pz ").replace("Park ", "Pk ") for p in r["parkfront"])
    gd = ("%g m" % r["godo_min"]) if r["godo_min"] else "-"
    gtxt = (gd, dict(fs=6.4)) if not r["over_n"] else ([gd, ("초과 %d동" % r["over_n"], dict(fs=5.8, c=RED, bold=True))])
    rows.append([(str(no), dict(fs=8, bold=True)), [(r["name"], dict(fs=7.2, bold=True)), (SHORT[no], dict(fs=5.8, c="#666"))], (USE[no], dict(fs=6.4)),
                 format(round(r["area"]), ","), format(round(r["fp"]), ","), "%.0f" % (r["bcr"] * 100), format(round(r["gfa"]), ","), "%.0f" % (r["far"] * 100),
                 [("%dF" % r["maxf"], dict(fs=6.6)), ("%.1f m" % r["maxh"], dict(fs=5.8, c="#666"))], (fr, dict(fs=5.8)), gtxt])
tot_fp = sum(r["fp"] for r in TR); tot_g = sum(r["gfa"] for r in TR); tot_a = sum(r["area"] for r in TR)
rows.append([("", {}), ("합계 (획지 19개)", dict(fs=7.4, bold=True)), "", (format(round(tot_a), ","), dict(bold=True)), (format(round(tot_fp), ","), dict(bold=True)), ("%.1f" % (tot_fp / tot_a * 100), dict(bold=True)),
             (format(round(tot_g), ","), dict(bold=True)), ("%.1f" % (tot_g / tot_a * 100), dict(bold=True)), "", ("건폐율·용적률 = 획지면적(가용지) 기준", dict(fs=5.8, c="#666")), ""])
shade.append(len(rows) - 1)
TX = 124
yend = grid_table(pg, TX, 44, cols, rows, hdr_h=9.5, row_h=10.3, shade_rows=shade)
# 용도 색 칩(번호 옆)
for i, r in enumerate(TR):
    yy = 44 + 9.5 + i * 10.3
    pg.rect(TX + 0.9, yy + 2.2, 1.6, 5.9, fc=CATCOL[r["cat"]], z=4)
# 범례
lx, ly = TX, yend + 6
pg.t(lx, ly, "범례", fs=7, bold=True)
ex = lx + 11
for cat in CATORDER[:-1]:
    pg.rect(ex, ly - 2, 5, 4, fc=CATCOL[cat], ec="#555", lw=0.25); pg.t(ex + 6.2, ly, cat, fs=6.2); ex += 6.2 + len(cat) * 2.15 + 5
pg.rect(ex, ly - 2, 5, 4, fc="#c3e3a4", ec="#6aa84f", lw=0.25); pg.t(ex + 6.2, ly, "공원·광장", fs=6.2)
notes = ["· 건폐율·용적률은 획지면적(가용지) 기준. 연면적은 지상층 기준 단순 합산(지하층·주차장 별도 산정 전). 1층을 판매·음식으로 쓰는 매스는 면적표(03)에서 판매·음식 행으로 옮겨 집계.",
         "· 고도지구(참고): 획지와 가장 많이 겹치는 도심 N m 지구의 최고높이. 이 안은 규제를 적용하지 않았으므로 초과 동(Plot 2·8)은 규제 적용 단계에서 층수를 낮춘다. 공간 데이터 기반 참고값 [고시 원문 대조 전].",
         "· 청년주거(Plot 2·4·5·6)는 2026.1 결정도 공고에 주거용지가 없으므로 신규 용도 — 용도지역 변경 또는 허용용도 협의가 필요하다 [T1 고시 대조 필요].",
         "· 높이는 층수 × 층고(주거 3.2 m, 업무 3.8 m, 공공 4.0 m, 문화 4.5 m, 판매 4.2 m, 체육 6.5 m, 주차 3.0 m) — 계획 가정."]
for i, s in enumerate(notes): pg.t(TX, ly + 8 + i * 4.6, s, fs=5.9, c="#444")
pg.t(412, 291, "01", fs=8, c="#666", ha="right")
pg.save(OUT + r"\01_획지구획도_획지계획표.png", dpi=170, pdf=OUT + r"\01_획지구획도_획지계획표.pdf")
pg.save(SP + r"\p01.png", dpi=110)
print("saved p01")
