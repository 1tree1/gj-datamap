"""G4a 전체 면적표(16:9) — 형식: 2026-10-08 '03 면적표'(통영 보고서 p.18 형식: Site Area / Facility Area / Keymap, 영문·한글 이중 열, 소계 음영, 소계만 %)
면적은 최종본(data/model.pkl)에서 직접 산정 — 획지 + 공원 + 도로·보행이 계획 경계에 닫힘(도형 겹침·틈 1㎡ 차)"""
from gkit import *
from shapely.ops import polylabel

LOTN = {1: "공공청사", 2: "청사 부설주차장", 3: "생활체육시설", 4: "청년·신혼 공공임대주택", 5: "공공업무·청년창업", 6: "생활문화·돌봄 복합",
        7: "전통공예 특화", 8: "창작·체험(레지던시)", 9: "구 경주역 어댑티브 리유즈", 10: "관광안내·방문자지원", 11: "관문 가로상가", 12: "근대역사관",
        13: "공유주차장·모빌리티 허브"}
OPN = {o["key"]: o for o in S["OPEN"]}
PK = {p["key"]: p for p in S["PARKS"]}
A_veh = sum(g.area for g in S["ROADS"].values())
A_ped = OPN["E"]["g"].area + OPN["F"]["g"].area + S["PATH8"].area
A_lin = OPN["D"]["g"].area; A_walk = S["WALK"].area
A_road = A_veh + A_ped + A_lin + A_walk
A_park = sum(p["g"].area for p in S["PARKS"])
A_lot = sum(l["g"].area for l in S["LOTS"])
A_sum = A_park + A_road + A_lot
GFA = {}
for b in BLD:
    for k, v in b["gfa_by"].items(): GFA[k] = GFA.get(k, 0.0) + v
G_ = sum(GFA.values())
def fm_(v): return f0(v) + "㎡"
def pc(v, t): return "%d%%" % round(v / t * 100)

pg = Page()
pg.header("Masterplan : Area Summary", "Summary + Site Plan", "개요 + 전체 면적표",
          sub="최종 마스터플랜 — 면적은 도면에서 직접 산정(㎡)하며 합계가 계획 경계에 닫힘 · 규제(고도지구·역사문화환경 허용기준) 미반영")


def table(x, y, widths, rows, hdr, rh=5.6):
    xs = [x]
    for w in widths: xs.append(xs[-1] + w)
    gap = 0.5
    pg.line([x, xs[-1]], [y, y], c="#777777", lw=0.5)
    t_ = pg.t(x + 1.5, y + 5.0, hdr[0], fs=11.5, bold=True); pg.t(x + 1.5 + pg.wmm(t_) + 2.2, y + 5.2, hdr[1], fs=10, c="#444444")
    yy = y + 9.5
    for r in rows:
        sub = r.get("sub", False); span = r.get("span", False)
        cells = [(xs[0], xs[1]), (xs[1], xs[2]), (xs[2], xs[3]), (xs[3], xs[4])]
        if span: cells = [cells[0], cells[1], (xs[2], xs[4])]
        for a, b in cells:
            if sub: pg.rect(a + gap / 2, yy + gap / 2, b - a - gap, rh - gap, fc="#ececec", z=1)
            else: pg.line([a + gap, b - gap], [yy + rh, yy + rh], c="#b5b5b5", lw=0.4)
        pg.t(xs[0] + 1.5, yy + rh / 2, r["en"], fs=10)
        pg.t(xs[1] + 1.5, yy + rh / 2, r["ko"], fs=10, c="#444444")
        if span: pg.t(xs[4] - 1.6, yy + rh / 2, r["val"], fs=10, ha="right")
        else:
            pg.t(xs[3] - 1.6, yy + rh / 2, r["val"], fs=10, ha="right")
            if r.get("pct"): pg.t(xs[4] - 1.6, yy + rh / 2, r["pct"], fs=10, ha="right")
        yy += rh
    return yy


# ── Site Area ──
W1 = [47, 58, 24, 11]
rows1 = [dict(en="Station Site (Announced)", ko="폐역 부지(공고 면적)†", val=fm_(79438), sub=True),
         dict(en="Planning Boundary", ko="계획 경계(최종 마스터플랜)", val=fm_(B.area), sub=True),
         dict(en="Park A", ko="공원 A · 북측 근린공원", val=fm_(PK["A"]["g"].area)),
         dict(en="Park B", ko="공원 B · 체육공원", val=fm_(PK["B"]["g"].area)),
         dict(en="Park C", ko="공원 C · 중앙 근린공원", val=fm_(PK["C"]["g"].area)),
         dict(en="Water Area", ko="수공간(해당 없음)", val="-"),
         dict(en="Subtotal of Park", ko="공원면적 소계", val=fm_(A_park), pct=pc(A_park, A_sum), sub=True),
         dict(en="Vehicle Road", ko="차량도로(북측 차도·동서 도로·외곽)", val=fm_(A_veh)),
         dict(en="Pedestrian Road", ko="보행자전용(남북·사선 보행축, 조망로)", val=fm_(A_ped)),
         dict(en="E-W Linear Park", ko="동서 선형공원·가로광장(40 m)", val=fm_(A_lin)),
         dict(en="Sidewalk", ko="외곽 보도", val=fm_(A_walk)),
         dict(en="Subtotal of Road", ko="도로면적 소계", val=fm_(A_road), pct=pc(A_road, A_sum), sub=True)]
for l in sorted(S["LOTS"], key=lambda l: l["no"]):
    ko = LOTN[l["no"]]                                                    # 획지 번호는 영문 열(Plot n)에
    rows1.append(dict(en="Plot %d" % l["no"], ko=ko, val=fm_(l["g"].area)))
rows1 += [dict(en="Subtotal of Usable Land", ko="획지면적 소계", val=fm_(A_lot), pct=pc(A_lot, A_sum), sub=True),
          dict(en="Planned Site Area", ko="계획부지 면적합계", val=fm_(A_sum), sub=True)]
y1 = table(12, 33, W1, rows1, ("Site Area", "대상지 면적"))

# ── Facility Area ──
W2 = [47, 52, 26, 11]
FROWS = [("공공업무", "Public Office / Civic", "공공청사·공공업무"), ("업무·창업", "Office / Start-up", "업무·청년창업"), ("문화", "Cultural / Assembly", "문화·집회"),
         ("창작", "Creative Industry", "창작·공방"), ("판매", "Retail / F&B", "판매·근린생활"), (None, "Hotel / Hospitality", "숙박시설"),
         ("생활SOC", "Leisure / Welfare", "생활체육·복지"), ("주거", "Residential", "주거"), ("역사", "Heritage (former station)", "역사유산(구 경주역사)"),
         ("방문자", "Visitor Support", "관광·방문자"), ("주차", "Parking & Mobility", "주차·교통(모빌리티 허브 포함)")]
rows2 = []
for k, en, ko in FROWS:
    v = GFA.get(k, 0.0) if k else 0.0
    rows2.append(dict(en=en, ko=ko, val=fm_(v) if v > 0 else "-", pct=pc(v, G_) if v > 0 else "0%"))
LK = sum(k["g"].area for k in LINKS)
GL = S["GLASS"]; A_gl = (GL["a1"] - GL["a0"]) * (GL["b1"] - GL["b0"])
rows2 += [dict(en="Total GFA", ko="연면적 합계(지상)", val=fm_(G_), sub=True, span=True),
          dict(en="FAR (Usable Land)", ko="용적률(가용부지 기준)", val="%d%%" % round(TOT["far"] * 100), sub=True, span=True),
          dict(en="Coverage (Usable Land)", ko="건폐율(가용부지 기준)", val="%d%%" % round(TOT["bcr"] * 100), sub=True, span=True),
          dict(en="Buildings", ko="건축물 동수", val="%d동" % len(BLD), span=True),
          dict(en="Bridges & Canopies", ko="연결 브리지·캐노피(연면적 제외)", val="%d곳 · %s" % (len(LINKS), fm_(LK)), span=True),
          dict(en="Glass Roof Court", ko="유리 지붕 중정(연면적 제외)", val="약 " + fm_(round(A_gl, -1)), span=True)]
x2 = 162
y2 = table(x2, 33, W2, rows2, ("Facility Area", "시설별 면적"))
pkb = sum(b["gfa"] for b in BLD if b["main"] == "주차" and "허브" not in b["name"])
TW2 = sum(W2)
yy = y2 + 4.6
for s_ in ["참고 · 주차·교통 제외 연면적 %s (용적률 %d%%)" % (fm_(G_ - GFA["주차"]), round((G_ - GFA["주차"]) / A_lot * 100)),
           "참고 · 주차장동 %s → 약 %s면(32㎡/대 가정), 모빌리티 허브 %s 별도" % (fm_(pkb), f0(round(pkb / 32, -1)), fm_(GFA["주차"] - pkb))]:
    yy = text_block(pg, x2 + 1.5, yy, s_, TW2 - 2, c="#555555") + 0.6
# ── 주석(가운데 아래) ──
yy += 4.0
FOOT = ["† 경주시 공개 구상(2026.02) 기준 면적 — 언론 경유 [T4, 원문 미확인]. 계획 경계는 최종 마스터플랜 경계로, 고시 구역·시 구상 면적과 직접 비교하지 않는다.",
        "· 면적 합계 %s는 경계 %s와 %d㎡ 차(도형 겹침·틈). 동서 선형공원(40 m)은 보행자전용도로로 집계했다(공원으로 보면 공원율 %d%%)." % (fm_(A_sum), fm_(B.area), round(abs(A_sum - B.area)), round((A_park + A_lin) / A_sum * 100)),
        "· 연면적 = 동별 바닥면적 × 층수(층고 주거 3.0·주차 3.2·그 외 4.0 m)의 지상 합. 1층 근린생활은 Retail 행에 집계. 용적률·건폐율은 획지면적 기준.",
        "· 숙박은 최종본에 없어 0 — 구상 프로그램의 'STAY'는 미반영(결정 필요)."]
for s_ in FOOT:
    yy = text_block(pg, x2 + 1.5, yy, s_, TW2 - 2, c="#555555") + 0.8
print("site table end %.1f, facility end %.1f, foot end %.1f" % (y1, y2, yy))

# ── Keymap(오른쪽, 북쪽 위) ──
KX, KY, KW, KH = 304, 36, 88, 174
bx0, by0, bx1, by1 = B.bounds
ax = pg.plan_ax(KX, KY, KW, KH, (bx0 - 6, bx1 + 6, by0 - 6, by1 + 6))
fill(ax, B, fc="#a9a9a9", z=1)
for g in S["ROADS"].values(): fill(ax, g, fc="#a9a9a9", z=1.5)
for g in [o["g"] for o in S["OPEN"]] + [S["PATH8"], S["WALK"]]: fill(ax, g, fc="#cdcdcd", z=1.6)
for l in S["LOTS"]: fill(ax, l["g"], fc="#ececec", ec="white", lw=0.5, z=2)
for p in S["PARKS"]: fill(ax, p["g"], fc="#8cc63f", ec="white", lw=0.5, z=2)
for l in S["LOTS"]:
    pt = polylabel(max(polys(l["g"]), key=lambda g: g.area), 1.0)
    ax.text(pt.x, pt.y, str(l["no"]), fontsize=10, fontweight="bold", ha="center", va="center", zorder=5, color=INK)
for p in S["PARKS"]:
    pt = polylabel(max(polys(p["g"]), key=lambda g: g.area), 1.0)
    ax.text(pt.x, pt.y, "Park " + p["key"], fontsize=10, fontweight="bold", ha="center", va="center", zorder=5, color="#1d3b0f")
pg.top()
pg.t(KX + KW, KY + KH + 4.0, "Keymap", fs=11, bold=True, ha="right")
pg.ax.annotate("", xy=(KX + 4, KY + 2), xytext=(KX + 4, KY + 14), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8), zorder=7)
pg.t(KX + 4, KY - 1.2, "N", fs=10, bold=True, ha="center")
pg.save("D4a_전체면적표")
print("sum %.1f boundary %.1f park %.1f road %.1f lot %.1f gfa %.1f" % (A_sum, B.area, A_park, A_road, A_lot, G_))
