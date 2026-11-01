"""G4b 개발규모 산정표(16:9) — 과제 요구 '정비(개발)규모 산정 및 프로그램 구성' 대응
 - 주요 도입기능별 면적 및 구성비 · 대지면적 · 건축면적 · 연면적 · 건폐율 · 용적률 · 건축물 높이(층수)
 - 표 1: 도입기능별 개발규모 산정표(획지 13 → 기능 묶음 소계 → 건축대지 소계 → 기반시설(공원·도로) → 계획대상지 합계)
 - 표 2: 도입기능(용도)별 연면적 및 구성비
수치는 최종본(data/model.pkl) — 연면적 = 동별 바닥면적 × 층수(지상), 층수·높이는 동별 모델값"""
from gkit import *

GROUPS = [("공공행정·업무", "#6E8FC9", [1, 2, 5]), ("정주·생활SOC", "#E9B949", [3, 4, 6]), ("창작·체험", "#AE93D6", [7, 8]),
          ("역사·문화·관광", "#B97A4E", [9, 10, 11, 12]), ("교통·모빌리티", "#8E949B", [13])]
LOTN = {1: "공공청사", 2: "청사 부설주차장", 3: "생활체육시설", 4: "청년·신혼 공공임대주택", 5: "공공업무·청년창업", 6: "생활문화·돌봄 복합",
        7: "전통공예 특화", 8: "창작·체험(레지던시)", 9: "구 경주역 어댑티브 리유즈", 10: "관광안내·방문자지원", 11: "관문 가로상가", 12: "근대역사관",
        13: "공유주차장·모빌리티 허브"}
FAC = {1: "공공청사 본관(7층) · 민원·시민홀동(5층)", 2: "직원 주차장동(5층, 청사 연결 브리지) · 별동(4층)", 3: "생활체육관·편의시설(4층)",
       4: "공공임대주택 판상 8동(5층) · 근린생활 연결동 4개(1층)", 5: "공공기관 업무동(5층) · 청년창업지원센터(4층)", 6: "복합문화센터(4층) · 건강·돌봄센터(3층)",
       7: "공방·전시·공예마켓동(3층) · 공방·판매동(2층)", 8: "실내 체험관(4층) · 레지던시 제작동 3(3층)·거주동 3(5층) · 가로상가(4층)",
       9: "구 경주역사(2층, 존치) · 지역문화원 본동·소상공인 상생동 2(5층)", 10: "관광지원센터(2층)", 11: "관문 가로상가 2동(2층)", 12: "근대역사관(4층)",
       13: "공유주차장(5층) · 모빌리티 허브(4층)"}
L = {l["no"]: l for l in LOTS}
SITE = TOT["boundary"]; GFA_T = TOT["gfa"]
A_park = sum(p["g"].area for p in S["PARKS"])
A_road = sum(g.area for g in S["ROADS"].values()) + sum(o["g"].area for o in S["OPEN"]) + S["PATH8"].area + S["WALK"].area
def pct(v, t): return "%.1f%%" % (v / t * 100)

pg = Page()
pg.header("Masterplan : Development Scale", "Development Scale + Program", "개발규모 산정 및 프로그램 구성",
          sub="계획대상지 %s㎡ · 건축대지(획지 13) %s㎡ · 건축면적 %s㎡ · 연면적 %s㎡ · 건폐율 %.1f%% · 용적률 %.1f%% · 최고 7층(28 m) · 건축물 %d동"
          % (f0(SITE), f0(TOT["lot"]), f0(TOT["ba"]), f0(GFA_T), TOT["bcr"] * 100, TOT["far"] * 100, len(BLD)))

# ── 표 1 ──
X0 = 12.0
W = [32, 8, 50, 130, 22, 14, 22, 24, 14, 15, 15, 30]                 # 합 376
xs = [X0]
for w in W: xs.append(xs[-1] + w)
TWD = xs[-1] - X0
y = 33.5
pg.t(X0, y + 2.2, "표 1  도입기능별 개발규모 산정표", fs=11, bold=True)
y += 6.0
H1, H2 = 5.2, 5.0                                                   # 2단 머리글
pg.rect(X0, y, TWD, H1 + H2, fc="#3c3c3c", z=5)
def hc(i0, i1, yy, h, s):
    pg.t((xs[i0] + xs[i1]) / 2, yy + h / 2, s, fs=10, c="white", bold=True, ha="center", z=6)
for i, s in ((0, "구분(도입기능)"), (1, "No."), (2, "획지명"), (3, "주요 시설(층수)"), (6, "건축면적(㎡)"), (9, "건폐율"), (10, "용적률"), (11, "최고 층수(높이)")):
    hc(i, i + 1, y, H1 + H2, s)
hc(4, 6, y, H1, "대지"); hc(7, 9, y, H1, "연면적")
for i, s in ((4, "면적(㎡)"), (5, "구성비"), (7, "면적(㎡)"), (8, "구성비")): hc(i, i + 1, y + H1, H2, s)
for a in (4, 7): pg.line([xs[a] + 1, xs[a + 2] - 1], [y + H1, y + H1], c="#8a8a8a", lw=0.4, z=6)
y += H1 + H2
RH, SH = 6.6, 6.0
def num(i, s, yy, h, bold=False, c=INK):
    pg.t(xs[i + 1] - 1.2, yy + h / 2, s, fs=10, ha="right", bold=bold, c=c, z=6)
def row_vals(yy, h, area, ba, gfa, maxf, maxh, bold=False, site_ratio=True, far_base=None):
    num(4, f0(area), yy, h, bold); num(5, pct(area, SITE), yy, h, bold, GREY if not bold else INK)
    num(6, f0(ba), yy, h, bold); num(7, f0(gfa), yy, h, bold); num(8, pct(gfa, GFA_T), yy, h, bold, GREY if not bold else INK)
    base = far_base or area
    num(9, "%.1f%%" % (ba / base * 100), yy, h, bold); num(10, "%.1f%%" % (gfa / base * 100), yy, h, bold)
    pg.t((xs[11] + xs[12]) / 2, yy + h / 2, "%d층(%.0f m)" % (maxf, maxh), fs=10, ha="center", bold=bold, z=6)
for gname, gc, nos in GROUPS:
    g_y0 = y
    for no in nos:
        l = L[no]
        lines = wrap_mm(pg, FAC[no], W[3] - 2.4)
        h = RH if len(lines) == 1 else 9.4
        pg.rect(xs[1], y, TWD - W[0], h, fc="white", z=5); pg.line([xs[1], xs[-1]], [y + h, y + h], c="#dedede", lw=0.4, z=6)
        pg.ax.add_patch(Circle((xs[1] + W[1] / 2, y + h / 2), 2.5, fc="white", ec=INK, lw=0.5, zorder=7)); pg.t(xs[1] + W[1] / 2, y + h / 2 + 0.1, str(no), fs=10, bold=True, ha="center", z=8)
        pg.t(xs[2] + 1.2, y + h / 2, LOTN[no], fs=10, bold=True, z=6)
        for j, ln in enumerate(lines[:2]): pg.t(xs[3] + 1.2, y + h / 2 + (j - (len(lines[:2]) - 1) / 2) * 4.4, ln, fs=10, z=6)
        row_vals(y, h, l["area"], l["ba"], l["gfa"], l["maxf"], l["maxh"])
        y += h
    if len(nos) > 1:                                                  # 기능 묶음 소계
        a_ = sum(L[n]["area"] for n in nos); b_ = sum(L[n]["ba"] for n in nos); g_ = sum(L[n]["gfa"] for n in nos)
        mf = max(L[n]["maxf"] for n in nos); mh = max(L[n]["maxh"] for n in nos)
        pg.rect(xs[1], y, TWD - W[0], SH, fc="#f1f1ef", z=5)
        pg.t(xs[2] + 1.2, y + SH / 2, "소계", fs=10, bold=True, z=6)
        row_vals(y, SH, a_, b_, g_, mf, mh, bold=True)
        y += SH
    # 구분 칸(세로 병합)
    pg.rect(X0, g_y0, W[0], y - g_y0, fc="#f7f7f5", z=5); pg.rect(X0, g_y0, 1.6, y - g_y0, fc=gc, z=6)
    for j, ln in enumerate(wrap_mm(pg, gname, W[0] - 4)):
        n_ = len(wrap_mm(pg, gname, W[0] - 4))
        pg.t(X0 + 3.0, (g_y0 + y) / 2 + (j - (n_ - 1) / 2) * 4.6, ln, fs=10, bold=True, z=6)
    pg.line([X0, xs[-1]], [y, y], c="#9a9a9a", lw=0.6, z=7)
# 건축대지 소계 → 기반시설 → 계획대상지 합계
def band_row(label, h, fc, vals=None, bold=True, note=None):
    global y
    pg.rect(X0, y, TWD, h, fc=fc, z=5)
    pg.t(X0 + 3.0, y + h / 2, label, fs=10, bold=bold, z=6)
    if note: pg.t(xs[3] + 1.2, y + h / 2, note, fs=10, c=GREY, z=6)
    if vals: vals(y, h)
    y += h
band_row("건축대지 소계(획지 13)", 6.4, "#e4e4e1",
         lambda yy, h: row_vals(yy, h, TOT["lot"], TOT["ba"], GFA_T, 7, 28.0, bold=True), note="건폐율·용적률은 건축대지(획지) 기준")
def infra(area):
    return lambda yy, h: (num(4, f0(area), yy, h), num(5, pct(area, SITE), yy, h, c=GREY))
band_row("기반시설 · 공원·녹지", 6.0, "#ffffff", infra(A_park), bold=False, note="근린공원 3개소(북측 근린공원 · 체육공원 · 중앙 근린공원)")
band_row("기반시설 · 도로·보행", 6.0, "#ffffff", infra(A_road), bold=False, note="차량도로 · 보행자전용도로(선형공원 40 m 포함) · 외곽 보도")
band_row("계획대상지 합계", 6.6, "#d6d6d2",
         lambda yy, h: row_vals(yy, h, SITE, TOT["ba"], GFA_T, 7, 28.0, bold=True, far_base=SITE), note="건폐율·용적률은 계획대상지 전체 기준(참고)")
pg.line([X0, xs[-1]], [y, y], c="#3c3c3c", lw=0.8, z=7)
print("table1 end %.1f" % y)

# ── 표 2: 도입기능(용도)별 연면적 및 구성비 ──
y += 5.0
pg.t(X0, y + 2.2, "표 2  도입기능(용도)별 연면적 및 구성비", fs=11, bold=True)
y += 6.0
GFA = {}
for b in BLD:
    for k, v in b["gfa_by"].items(): GFA[k] = GFA.get(k, 0.0) + v
CATS2 = [("공공업무", "공공청사·업무"), ("업무·창업", "업무·청년창업"), ("문화", "문화·집회"), ("창작", "창작·공방"), ("판매", "판매·근린생활"), (None, "숙박"),
         ("생활SOC", "생활체육·복지"), ("주거", "주거"), ("역사", "역사유산"), ("방문자", "관광·방문자"), ("주차", "주차·교통")]
W2 = [28] + [29] * 11 + [29]                                        # 합 376
x2 = [X0]
for w in W2: x2.append(x2[-1] + w)
pg.rect(X0, y, sum(W2), 6.0, fc="#3c3c3c", z=5)
pg.t(X0 + W2[0] / 2, y + 3.0, "구분", fs=10, c="white", bold=True, ha="center", z=6)
for i, (k, lab) in enumerate(CATS2):
    pg.t((x2[i + 1] + x2[i + 2]) / 2, y + 3.0, lab, fs=10, c="white", bold=True, ha="center", z=6)
pg.t((x2[-2] + x2[-1]) / 2, y + 3.0, "합계", fs=10, c="white", bold=True, ha="center", z=6)
y += 6.0
for r, (lab, fn) in enumerate((("연면적(㎡)", lambda v: f0(v) if v > 0 else "-"), ("구성비", lambda v: ("%.1f%%" % (v / GFA_T * 100)) if v > 0 else "0.0%"))):
    pg.rect(X0, y, sum(W2), 6.0, fc="white" if r == 0 else "#f7f7f5", z=5); pg.line([X0, x2[-1]], [y + 6.0, y + 6.0], c="#dedede", lw=0.4, z=6)
    pg.t(X0 + 2.0, y + 3.0, lab, fs=10, bold=True, z=6)
    for i, (k, _) in enumerate(CATS2):
        v = GFA.get(k, 0.0) if k else 0.0
        pg.t(x2[i + 2] - 1.6, y + 3.0, fn(v), fs=10, ha="right", z=6)
    pg.t(x2[-1] - 1.6, y + 3.0, f0(GFA_T) if r == 0 else "100.0%", fs=10, ha="right", bold=True, z=6)
    y += 6.0
pg.line([X0, x2[-1]], [y, y], c="#3c3c3c", lw=0.8, z=7)
y += 4.2
pg.t(X0, y, "※ 연면적 지상 기준(동별 바닥면적 × 층수) · 연결 브리지·캐노피와 유리 지붕 중정은 연면적 제외 · 고도지구·역사문화환경 허용기준 미반영 · 숙박 0(구상 'STAY' 미반영, 결정 필요)", fs=10, c=GREY, z=6)
print("end %.1f" % y)
pg.save("D4a_개발규모산정표")
