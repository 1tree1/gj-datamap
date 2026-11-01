"""build_deck — 5주차 보고서·PT 초안을 사용자 계획 방향(규제 미적용 획지·매스안)으로 다시 짠다. 출력: ../5주차_과제_다듬기v2.pptx
원본 deck(36장, 그림 0)은 건드리지 않는다. 서체·크기는 pptkit(CLAUDE.md §11).
문체 규칙(v2): ① 제목·소제목·표 머리글은 명사형(체언형) ② 문장은 통영 보고서와 같은 합니다체, 나열은 명사구 ③ 극적·구어 표현 금지,
용어는 보고서 어휘(조성·연계·확보·거점·관문·정주·근로·방문 등)를 쓴다."""
import os, sys, json, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptkit import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean"
A = ROOT + r"\assets"; CR = A + r"\crops"
OUTFILE = ROOT + r"\5주차_과제_다듬기v3.pptx"
T = pickle.load(open(PLAN + r"\data\tables_clean.pkl", "rb"))
S_, F_, TR, RR, SM, OVER = T["site"], T["fac"], T["lot_rows"], T["road_rows"], T["summary"], T["over"]
LOT = {r["no"]: r for r in TR}
def n(v): return format(int(round(v)), ",")
ZL = {"북": [1, 2, 3, 4, 5, 6], "중": [7, 8, 9, 10, 11, 12, 13, 14], "남": [15, 16, 17, 18, 19]}
ZC_ = {"북": ZN, "중": ZC, "남": ZS}
ZNAME = {"북": "북측", "중": "중앙", "남": "남측"}
ZV = {"북": "근로·정주 거점", "중": "교류·창작 거점", "남": "방문 관문"}
ZSUM = {z: dict(n=len(L), area=sum(LOT[i]["area"] for i in L), gfa=sum(LOT[i]["gfa"] for i in L)) for z, L in ZL.items()}
NAME = {1: "공공체육·생활시설", 2: "청년주거 북동", 3: "시청·의회 캠퍼스", 4: "청년주거 서", 5: "청년주거 동", 6: "청년주거 동남(연립)", 7: "복합문화·영화관", 8: "청년창업·기업지원",
        9: "청년·주민 커뮤니티", 10: "성동시장 클러스터", 11: "체험판매 거리", 12: "레지던시·공방 A", 13: "레지던시·공방 B", 14: "레지던시·공방 C", 15: "구 역사·근대역사관",
        16: "주차전용건축물", 17: "관광지원시설", 18: "관광 상가 서", 19: "관광 상가 동"}
USE = {1: "체육·생활 공공시설", 2: "청년주거", 3: "시청·의회", 4: "청년주거", 5: "청년주거", 6: "청년주거(연립)", 7: "문화시설·영화관", 8: "창업·기업지원 업무", 9: "주민 커뮤니티",
       10: "시장(성동시장 연계)", 11: "체험·판매", 12: "레지던시·공방", 13: "레지던시·공방", 14: "레지던시·공방", 15: "구 역사(이전)·전시", 16: "주차시설", 17: "관광안내·환승",
       18: "관광 상가(카페·상점)", 19: "관광 상가(카페·상점)"}
CATCOL = {"문화·교육·공공": "#6f9fdc", "상업·업무": "#e4573a", "창조산업": "#a98bd3", "여가·오락·체육": "#2fab9d", "주거": "#f1d247", "판매·음식": "#f4a0c2", "교통·방문자": "#c6c6c6", "역사유산": "#c9742f", "오픈스페이스": "#9fd36b"}

ORDER = ["cover", "toc", "hero", "zones", "summary", "principles",
         "div1", "now", "location", "barrier", "tourists", "neighbors", "people3", "metrics", "plans",
         "div2", "boundary", "plan", "north", "center", "south", "roads", "roadtable", "memory", "axo", "day", "phases",
         "div3", "area1", "area2", "lots1", "lots2", "how", "open", "rules",
         "div4", "pop", "ops",
         "before", "after", "sources", "app1", "app2", "app3", "app4"]
PAGE = {k: i + 1 for i, k in enumerate(ORDER)}
SL = {}
def slide(key):
    def deco(fn): SL[key] = fn; return fn
    return deco
def std(d, key, label, title, sub=None):
    s = d.slide(); title_block(s, label, title, sub); page_no(s, PAGE[key]); return s

# ── 공통 부품 ─────────────────────────────────────────────────────────────────
def card(s, x, y, w, h, big, label, desc=None, color=BLUE, fill=TINT, big_size=30, label_size=12):
    rect(s, x, y, w, h, fill=fill, radius=0.1)
    text(s, x + 0.2, y + 0.1, w - 0.4, 0.62, big, size=big_size, bold=True, color=color, tag="kpi")
    text(s, x + 0.2, y + 0.78, w - 0.4, 0.3, label, size=label_size, bold=True, tag="kpi-l")
    if desc: text(s, x + 0.2, y + 1.1, w - 0.4, h - 1.15, desc, size=10.5, color=INK2, tag="kpi-d")

def src(s, x, y, w, h, lines): text(s, x, y, w, h, lines, size=10.5, color=GRAY, tag="src")

def bar_rows(s, x, y, rows, label_w, bar_max, vmax, step=0.5, bar_h=0.3, color=BLUE, fmt=lambda v: n(v), val_size=11, label_size=12, hl=None):
    for i, (lab, v) in enumerate(rows):
        yy = y + i * step
        text(s, x, yy, label_w, bar_h + 0.04, lab, size=label_size, anchor="m", tag="barlab")
        w = max(0.04, bar_max * v / vmax)
        rect(s, x + label_w, yy + 0.02, w, bar_h, fill=(hl or {}).get(i, color))
        text(s, x + label_w + w + 0.06, yy, 1.3, bar_h + 0.04, fmt(v), size=val_size, bold=True, anchor="m", tag="barval")

# ═════════════════════════════════ 표지·목차·개요 ═════════════════════════════════
@slide("cover")
def _(d):
    s = d.slide()
    picture(s, A + r"\hero_after.jpg", 6.5, 0, SW - 6.5, SH, mode="cover", align=(0.6, 0.5))
    rect(s, 0, 0, 6.5, 0.09, fill=RED)
    text(s, 0.7, 0.6, 5.6, 0.3, "5주차 보고서 및 PT 초안  ·  건축디자인6 STUDIO B", size=12, color=RED, bold=True)
    text(s, 0.7, 2.15, 5.7, 1.5, ["구 경주역", "도시재생 마스터플랜"], size=34, bold=True, line=1.08, tag="cover-t")
    text(s, 0.7, 3.85, 5.6, 0.9, ["폐철도 부지의 활용 방향과", "공간구성 계획"], size=16, color=INK2, tag="cover-s")
    rect(s, 0.75, 5.0, 1.2, 0.05, fill=RED)
    text(s, 0.7, 5.95, 5.6, 0.9, ["2019113133 이승규  ·  2021113994 김민승", "김아름 교수님"], size=12, color=INK2, tag="cover-n")

@slide("toc")
def _(d):
    s = std(d, "toc", "목차", "발표 구성")
    rows = [("", "개요", "계획 요약 · 구역 구성 · 계획 원칙", PAGE["hero"]), ("1", "현황과 분석", "대상지 · 위치 · 보행 단절 · 방문 수요 · 주변 지역 · 상위계획", PAGE["div1"]),
            ("2", "마스터플랜", "배치 · 구역 · 가로 · 철도 유산 · 이용 시나리오 · 단계별 추진", PAGE["div2"]),
            ("3", "계획 수치의 근거", "면적표 · 획지계획표 · 산정 방법 · 규제 검토", PAGE["div3"]), ("4", "계획 인구와 운영", "계획 인구 산정 · 운영 체계", PAGE["div4"]), ("", "맺음말", "현황과 제안 · 자료 출처 · 도면 원본", PAGE["before"])]
    for i, (num, ttl, desc, pg) in enumerate(rows):
        y = 1.6 + i * 0.86
        text(s, 0.75, y, 0.9, 0.6, num, size=30, bold=True, color=BLUE, tag="toc-n")
        text(s, 1.85, y + 0.02, 6.5, 0.38, ttl, size=20, bold=True, tag="toc-t")
        text(s, 1.85, y + 0.42, 8.5, 0.3, desc, size=12, color=INK2, tag="toc-d")
        text(s, 11.3, y + 0.05, 1.4, 0.4, "%02d" % pg, size=20, bold=True, color=GRAY, align="r", tag="toc-p")
        line(s, 0.75, y + 0.78, 12.73, y + 0.78, LINE, 0.75)

@slide("hero")
def _(d):
    s = d.slide()
    picture(s, A + r"\hero_after.jpg", 0, 0, SW, SH, mode="cover")
    box_text(s, 0.6, 5.2, 8.6, 1.85, [dict(text="계획 개요", size=12, bold=True, color=RED, space_after=4), dict(text="원도심 생활거점으로의 재생", size=27, bold=True, space_after=3),
                                       dict(text="폐역 부지를 방문·근로·정주 인구가 함께 이용하는 복합 거점으로 조성합니다.", size=12, color=INK),
                                       dict(text="조감도 · 고도제한·용도지역 적용 전 개념안", size=10.5, color=INK2, space_before=4)], fill="#FFFFFF", alpha=0.9, radius=0.1, anchor="m", margin=(0.3, 0.12, 0.3, 0.12), tag="hero")
    page_no(s, PAGE["hero"])
    notes(s, "결론에 해당하는 조감도를 앞부분에 제시한다(통영 보고서 R.p5 구성 참고). 렌더: PyVista 평행투영, work/20261005_plan_clean 의 매스 모델.")

@slide("zones")
def _(d):
    s = std(d, "zones", "개요 : 구역 구성", "남북 3개 구역의 기능 구성")
    fr = json.load(open(A + r"\zone_bands.json"))
    ix, iy, ih = 0.6, 1.5, 5.4; iw = ih * 3.0 / 6.1
    picture(s, A + r"\plan_zones.png", ix, iy, iw, ih, mode="contain")
    info = {"북": ("시청·의회  ·  청년주거  ·  공공체육  ·  수변공원", "근로자와 거주자가 상주하는 업무·주거 중심 구역입니다."),
            "중": ("성동시장 클러스터  ·  체험판매  ·  공방·레지던시  ·  문화  ·  창업", "방문객과 주민이 교류하며 성동시장·황오동으로 연계되는 구역입니다."),
            "남": ("구 역사(이전)·근대역사관  ·  관광지원  ·  관광 상가  ·  주차", "방문객이 처음 도착하는 관문 구역입니다.")}
    for z in ("북", "중", "남"):
        t0, t1 = fr[z]; y = iy + t0 * ih + 0.07; h = (t1 - t0) * ih - 0.14
        rect(s, 3.55, y, 9.18, h, fill=tint(ZC_[z], 0.82), radius=0.08); rect(s, 3.55, y, 0.12, h, fill=ZC_[z])
        text(s, 3.9, y + 0.08, 4.6, 0.46, "%s  ·  %s" % (ZNAME[z], ZV[z]), size=20, bold=True, tag="zone-h")
        text(s, 8.2, y + 0.16, 4.4, 0.3, "획지 %d개 · 면적 %s㎡ · 연면적 %s㎡" % (ZSUM[z]["n"], n(ZSUM[z]["area"]), n(ZSUM[z]["gfa"])), size=10.5, color=INK2, align="r", tag="zone-3")
        text(s, 3.9, y + 0.58, 8.7, 0.32, info[z][1], size=12, tag="zone-1")
        text(s, 3.9, y + 0.95, 8.7, 0.32, info[z][0], size=12, bold=True, tag="zone-2")
    notes(s, "구역 경계: 북측 = C가로(y=361,092) 위, 중앙 = A가로(y=360,796)~C가로, 남측 = A가로 아래. 획지 번호는 면적표와 같다. 면적 = 획지 면적 합(공원·도로 제외).")

@slide("summary")
def _(d):
    s = std(d, "summary", "개요 : 요약", "계획 요약")
    items = [("01", "계획 배경", "구 경주역은 경주 원도심의 중심부, 황리단길·대릉원과 성동시장·황오동 사이에 위치합니다. 철도 이설 이후 남북으로 긴 공백지가 되었습니다."),
             ("02", "이용자 구성", "관광객 중심의 개발만으로는 원도심의 활력을 회복하기 어렵습니다. 방문객·근로자·거주자가 함께 이용하는 복합 거점을 계획합니다."),
             ("03", "공간 구성", "남측은 방문객의 관문, 중앙은 교류 거점, 북측은 근로·정주 거점으로 구성하고, 활력을 성동시장과 황오동으로 확산시킵니다.")]
    for i, (num, ttl, body) in enumerate(items):
        x = 0.6 + i * 4.1
        rect(s, x, 1.65, 3.93, 3.1, fill=TINT, radius=0.1)
        text(s, x + 0.25, 1.78, 1.4, 0.65, num, size=28, bold=True, color=BLUE, tag="sum-n")
        text(s, x + 0.25, 2.5, 3.45, 0.4, ttl, size=18, bold=True, tag="sum-t")
        text(s, x + 0.25, 3.05, 3.45, 1.6, body, size=12, color=INK, line=1.25, tag="sum-b")
    flow = [("유입", "남측", ZS), ("교류", "중앙", ZC), ("체류", "북측", ZN), ("확산", "성동시장·황오동", GRAY)]
    for i, (verb, where, col) in enumerate(flow):
        x = 0.6 + i * 3.1
        box_text(s, x, 5.2, 2.65, 1.35, [dict(text=verb, size=22, bold=True, color="#FFFFFF" if col != ZS else INK, align="c"), dict(text=where, size=12, color="#FFFFFF" if col != ZS else INK, align="c")], fill=col, radius=0.12, anchor="m", tag="flow")
        if i < 3: arrow_right(s, x + 2.72, 5.7, 0.33, 0.35, GRAY)

@slide("principles")
def _(d):
    s = std(d, "principles", "개요 : 계획 원칙", "5대 계획 원칙")
    cols = [("1", "연결", "기존 가로망과의 접속", "기존 가로 끝 37곳에 접속하는 가로 16개", BLUE),
            ("2", "관문", "방문객의 첫 도착 공간 조성", "근대역사관, 관광지원시설, 관광 상가, 구 역사 이전", ZS),
            ("3", "근로", "주간 근로 인구의 확보", "시청·의회, 청년창업·기업지원", ZN),
            ("4", "정주", "야간 정주 인구의 확보", "청년주거 4개 획지 (약 540~900세대, 가정)", YEL),
            ("5", "확산", "주변 지역으로의 활력 파급", "성동시장 클러스터, 동서 그린 보행축", ZC)]
    for i, (num, verb, meaning, plan, col) in enumerate(cols):
        x = 0.6 + i * 2.45; w = 2.3
        rect(s, x, 1.65, w, 5.2, fill=TINT, radius=0.1); rect(s, x, 1.65, w, 0.14, fill=col)
        oval(s, x + 0.2, 2.0, 0.55, col, num, size=16, color=INK if col in (YEL, ZS) else "#FFFFFF")
        text(s, x + 0.2, 2.75, w - 0.4, 0.5, verb, size=22, bold=True, tag="pr-v")
        text(s, x + 0.2, 3.35, w - 0.4, 1.2, meaning, size=12, line=1.2, tag="pr-m")
        line(s, x + 0.2, 4.6, x + w - 0.2, 4.6, LINE, 0.75)
        text(s, x + 0.2, 4.7, w - 0.4, 0.3, "계획 반영", size=10.5, color=GRAY, bold=True)
        text(s, x + 0.2, 5.02, w - 0.4, 1.7, plan, size=12, line=1.2, tag="pr-p")

# ═════════════════════════════════ 1 현황과 분석 ═════════════════════════════════
def divider(d, key, num, title, desc, col):
    s = d.slide(TINT)
    rect(s, 0, 0, 0.35, SH, fill=col)
    text(s, 1.2, 2.2, 3.0, 1.6, num, size=88, bold=True, color=col, tag="div-n")
    text(s, 1.2, 4.0, 11, 0.8, title, size=32, bold=True, tag="div-t")
    text(s, 1.2, 4.9, 11, 0.5, desc, size=14, color=INK2, tag="div-d")
    page_no(s, PAGE[key]); return s

@slide("div1")
def _(d): divider(d, "div1", "1", "현황과 분석", "대상지 · 위치 · 보행 단절 · 방문 수요 · 주변 지역 · 상위계획", BLUE)

@slide("now")
def _(d):
    s = std(d, "now", "현황과 분석 : 대상지", "철도 폐역 부지의 현황")
    picture(s, CR + r"\A_p64_aerial.png", 0.6, 1.55, 6.7, 3.75, mode="cover")
    picture(s, CR + r"\A_p105_photo3.png", 0.6, 5.4, 3.3, 1.55, mode="cover", align=(0.5, 0.45))
    picture(s, CR + r"\A_p105_photo2.png", 4.0, 5.4, 3.3, 1.55, mode="cover", align=(0.5, 0.55))
    facts = [("148,770㎡", "철도 부지 규모", "국가철도공단·한국철도공사 등이 소유한 부지로, 도심 중앙에 남북 방향으로 길게 놓여 있습니다. [T1]"),
             ("2021년 12월", "폐역 시점", "동해선 이설로 역 기능이 종료되었습니다. [T4, 원문 확인 필요]"),
             ("1918년", "구 역사 개업", "구 역사(1,404㎡)는 현재 사용되지 않으며, 코레일 철도기념물(2013)이고 등록문화유산은 아닙니다. [T1]")]
    for i, (big, ttl, desc) in enumerate(facts):
        y = 1.55 + i * 1.8
        rect(s, 7.6, y, 5.13, 1.65, fill=TINT, radius=0.1)
        text(s, 7.8, y + 0.1, 4.8, 0.5, big, size=24, bold=True, color=BLUE, tag="fact-b")
        text(s, 7.8, y + 0.66, 4.8, 0.3, ttl, size=12, bold=True, tag="fact-t")
        text(s, 7.8, y + 0.98, 4.8, 0.62, desc, size=10.5, color=INK2, line=1.15, tag="fact-d")
    photo_credit(s, 0.6, 1.55, 6.7, 3.75, "사진: 경주시 원도심 미래구상 기획연구(2025) · 전홍표")
    notes(s, "A_p64_aerial / A_p105_photo2·3 = 417쪽 연구 p.63, p.104 사진(전홍표 2025). 148,770㎡ = 전략계획 p.138 표(철도공단 69,790 + 철도공사 78,864 + 기재부 116, 자료: 경주시 주요업무계획 2021). 구 역사 지위: 코레일 철도기념물 2013(원문 대조 완료).")

@slide("location")
def _(d):
    s = std(d, "location", "현황과 분석 : 위치", "원도심 내 위치와 주변 자산")
    picture(s, CR + r"\B_p393_aerial.png", 0.6, 1.5, 6.5, 3.28, mode="cover")
    picture(s, CR + r"\B_p300_assets_strip.png", 0.6, 4.9, 6.5, 2.18, mode="cover")
    photo_credit(s, 0.6, 1.5, 6.5, 3.28, "사진: 경주시 도시재생 전략계획(변경, 2022)")
    photo_credit(s, 0.6, 4.9, 6.5, 2.18, "사진: 경주시 도시재생 전략계획(변경, 2022) — 경주역전지구 주요 지역자산")
    text(s, 7.5, 1.5, 5.2, 0.3, "구 역사 기준 주요 자산까지의 직선거리", size=14, bold=True, tag="loc-h")
    rows = [("황오동 고분", 345), ("성동시장", 355), ("경주읍성", 497), ("대릉원", 523), ("황리단길", 994), ("첨성대", 1030)]
    bar_rows(s, 7.5, 2.0, rows, 1.35, 2.9, 1030, step=0.56, bar_h=0.32, fmt=lambda v: "%sm" % n(v), hl={0: BLUE, 1: BLUE, 2: tint(BLUE, 0.35), 3: tint(BLUE, 0.35), 4: tint(BLUE, 0.35), 5: tint(BLUE, 0.35)})
    xl = 7.5 + 1.35 + 2.9 * 400 / 1030
    line(s, xl, 1.95, xl, 5.4, INK2, 1.0, dash=True)
    text(s, xl - 0.9, 5.42, 1.8, 0.28, "보행 5분 (약 400m)", size=10.5, color=INK2, align="c", tag="loc-5")
    box_text(s, 7.5, 5.95, 5.23, 1.0, "대상지의 남측에는 황리단길·대릉원, 서측에는 성동시장, 동측에는 황오동, 북측에는 북천이 위치합니다. 대상지는 이들 자산을 연결할 수 있는 거점입니다.", fill=TINT, radius=0.1, size=12, line_sp=1.15, tag="loc-b")
    notes(s, "거리: 구 역사 앞 직선거리(20260928_경주와_구경주역_한눈에_v1, T2). 항공사진·지역자산 사진: 경주시 도시재생 전략계획(변경, 2022) PDF p.383, p.290(경주역전지구 일원 주요 지역자산).")

@slide("barrier")
def _(d):
    s = std(d, "barrier", "현황과 분석 : 보행", "동서 보행 단절 현황")
    picture(s, CR + r"\A_p106_walk_map.png", 0.6, 1.5, 5.4, 5.4, mode="contain")
    photo_credit(s, 0.6, 1.5, 5.4, 5.4, "지도: 경주시 원도심 미래구상 기획연구(2025)")
    card(s, 6.4, 1.55, 6.33, 1.5, "985m", "도로 횡단 부재 구간", "철도 부지를 따라 횡단 가능한 도로가 없습니다. [자체 분석, T2]", big_size=28)
    card(s, 6.4, 3.2, 3.05, 1.85, "1개", "보행 육교", "폭 3.2m의 육교가 유일한 횡단 시설입니다. [T2]", big_size=28)
    card(s, 9.68, 3.2, 3.05, 1.85, "3.5배", "보행 우회율", "동서 이동 시 보행 경로가 직선거리 대비 중앙값 3.5배입니다. [T2]", big_size=28)
    box_text(s, 6.4, 5.25, 6.33, 1.55, "기존 연구도 같은 진단을 제시합니다. 철도 부지가 '경계공백지대'처럼 작동하여 보행 흐름을 단절하고 인접 지역의 쇠퇴를 초래한다고 봅니다. [원도심 미래구상 기획연구, 2025, T2]", fill="#FFFFFF", line=LINE, radius=0.1, size=12, line_sp=1.2, tag="bar-b")

@slide("tourists")
def _(d):
    s = std(d, "tourists", "현황과 분석 : 방문", "방문객 규모와 체류 특성")
    kp = [("872만 명", "2025년 황리단길·대릉원 방문객", "경주시 보도 인용으로 원문 확인이 필요합니다. [T4]"),
          ("79%", "체류 시간 3시간 미만 방문객", "황오동 방문객 설문(2024) [T2]. 응답자의 56%가 경주 시민입니다."),
          ("2.7%", "1만 원 이상 소비한 방문객", "동일 설문 [T2]")]
    for i, (big, ttl, sub) in enumerate(kp): card(s, 0.6 + i * 4.1, 1.65, 3.93, 2.25, big, ttl, sub, big_size=34)
    text(s, 0.6, 4.25, 12.1, 0.55, "과제는 방문객 수가 아니라 체류 시간의 확대입니다.", size=22, bold=True, tag="tour-1")
    text(s, 0.6, 4.9, 12.1, 0.45, "따라서 대상지는 '유입 확대'보다 '체류 유도'를 목표로 계획합니다.", size=14, tag="tour-2")
    box_text(s, 0.6, 5.65, 12.13, 1.0, "872만 명은 경주 전체(S3)의 방문 규모를 나타내는 수치이며, 대상지(S1)의 시설 규모 산정에는 사용하지 않습니다.", fill=TINT, radius=0.1, size=12, color=INK2, line_sp=1.2, tag="tour-3")
    notes(s, "872만: 한국관광데이터랩 인용 보도(2026-01, T4). 79%·2.7%: 황오동 방문객 설문 2024(공공도시 B-001, 2025.09, T2). 초안의 '5~8% 유입 가정'은 근거가 없어 규모 산정에 쓰지 않는다(팩트체크 문서 §4.1).")

@slide("neighbors")
def _(d):
    s = std(d, "neighbors", "현황과 분석 : 주변 지역", "주변 지역 쇠퇴 현황과 시민 요구")
    text(s, 0.6, 1.5, 5.8, 0.3, "황오동 쇠퇴 지표", size=14, bold=True)
    kp = [("−32.7%", "최근 10년 인구 증감 [T2]"), ("−44%", "20~39세 인구 증감(2018→2025) [T2]"), ("43.8%", "65세 이상 인구 비율 [T2]"), ("약 590개", "성동시장 점포 수(2024) [T2]")]
    for i, (big, lab) in enumerate(kp):
        x = 0.6 + (i % 2) * 2.95; y = 1.9 + (i // 2) * 1.55
        rect(s, x, y, 2.8, 1.4, fill=TINT, radius=0.1)
        text(s, x + 0.15, y + 0.12, 2.5, 0.6, big, size=26, bold=True, color=BLUE, tag="nb-b")
        text(s, x + 0.15, y + 0.85, 2.5, 0.5, lab, size=12, tag="nb-l")
    text(s, 6.9, 1.5, 5.8, 0.3, "구 경주역 부지에 대한 시민 요구 (응답 58건) [T2]", size=14, bold=True)
    rows = [("문화·쇼핑", 37), ("교통 거점", 16), ("지식·기술센터", 3), ("공공기관", 3), ("주거", 1)]
    bar_rows(s, 6.9, 2.0, rows, 1.55, 3.2, 37, step=0.56, bar_h=0.32, fmt=lambda v: "%d" % v, hl={4: ZC})
    text(s, 6.9, 4.85, 5.8, 0.3, "응답자 55명(청년 27명, 중장년 28명)", size=10.5, color=INK2, tag="nb-n")
    box_text(s, 0.6, 5.2, 12.13, 1.4, [dict(text="계획 대응", size=12, bold=True, color=RED, space_after=2), dict(text="시민이 요구한 문화·판매 기능과 교통 기능을 반영합니다. 시민 응답에는 없었으나 야간 활동 인구를 확보하기 위해 청년주거를 추가하며, 이는 자체 판단입니다.", size=14, line=1.2)],
             fill="#FFFFFF", line=BLUE, line_w=1.5, radius=0.1, anchor="m", margin=(0.25, 0.1, 0.25, 0.1), tag="nb-ans")
    notes(s, "출처: 황오동 수치 — 황오동 모니터링 보고서(공공도시, 2025.09)·KOSIS [T2] / 성동시장 점포 — 소진공 2024.11 [T2] / 시민 응답 — 경주시 원도심 미래구상 기획연구(2025) p.63~64 [T2]. "
             "청년 응답자 27명은 문화쇼핑 16·교통거점 12·주거 1, 중장년 28명은 문화쇼핑 21·교통거점 4·지식기술센터 3·공공기관 3. 응답자 수가 작아 방향 참고용으로만 쓴다.")

@slide("people3")
def _(d):
    s = std(d, "people3", "현황과 분석 : 이용자", "방문·근로·정주 인구의 시간대별 이용", "개념도: 통계가 아닌 계획 의도를 도식화한 것입니다. 점의 수는 해당 시간대의 이용 비중을 나타냅니다.")
    heads = ["평일 낮", "주말 낮", "저녁", "밤"]
    rows = [("방문 인구", ZS, [2, 3, 1, 0], "남측 관문 · 중앙 시장"), ("근로 인구", ZN, [3, 0, 2, 0], "북측 시청 · 중앙 창업"), ("정주 인구", YEL, [1, 2, 3, 3], "북측 청년주거 · 생활 상가")]
    x0, y0 = 3.2, 1.9
    for j, h in enumerate(heads): text(s, x0 + j * 1.55, y0, 1.4, 0.35, h, size=12, bold=True, align="c", tag="p3-h")
    text(s, 9.55, y0, 3.2, 0.35, "계획 반영", size=12, bold=True, tag="p3-h2")
    for i, (lab, col, lv, where) in enumerate(rows):
        y = y0 + 0.55 + i * 1.35
        rect(s, 0.6, y, 12.13, 1.2, fill=TINT, radius=0.1)
        box_text(s, 0.75, y + 0.2, 2.2, 0.8, lab, fill=col, radius=0.1, size=14, bold=True, color=INK if col in (YEL, ZS) else "#FFFFFF", align="c", tag="p3-l")
        for j, k in enumerate(lv):
            for m in range(3):
                oval(s, x0 + j * 1.55 + 0.27 + m * 0.3, y + 0.45, 0.24, col if m < k else "#FFFFFF", line=col)
        text(s, 9.55, y + 0.3, 3.1, 0.6, where, size=12, tag="p3-w")
    text(s, 0.6, 6.4, 12.1, 0.5, "세 인구가 중첩되는 시간대가 길수록 가로의 활력이 지속됩니다.", size=14, bold=True, tag="p3-n")

@slide("metrics")
def _(d):
    s = std(d, "metrics", "현황과 분석 : 성과 지표", "방문·정주 이중 성과 지표")
    box_text(s, 0.6, 1.65, 5.95, 3.4, [dict(text="방문 지표", size=22, bold=True, color=INK, space_after=8), dict(text="방문객 수", size=14, bullet=True, space_after=4), dict(text="체류 시간", size=14, bullet=True, space_after=4), dict(text="소비 금액", size=14, bullet=True)],
             fill=tint(ZS, 0.7), radius=0.1, anchor="m", margin=(0.4, 0.2, 0.3, 0.2), tag="m1")
    box_text(s, 6.78, 1.65, 5.95, 3.4, [dict(text="정주 지표", size=22, bold=True, space_after=8), dict(text="거주 인구", size=14, bullet=True, space_after=4), dict(text="생활 업종 비율(식료품·세탁·의원 등)", size=14, bullet=True, space_after=4), dict(text="야간 활동(18시 이후)", size=14, bullet=True)],
             fill=tint(YEL, 0.6), radius=0.1, anchor="m", margin=(0.4, 0.2, 0.3, 0.2), tag="m2")
    text(s, 0.6, 5.3, 12.1, 0.5, "두 지표를 항상 병기하여 평가합니다.", size=20, bold=True, tag="m-3")
    text(s, 0.6, 5.9, 12.1, 0.9, ["관광 업종은 증가하고 생활 업종이 감소하는 경우, 회복이 아니라 업종의 치환으로 판단합니다. (사례: 전주)", "보조 지표로 인접 건물 주 출입구의 대상지 방향 전환 여부를 확인합니다. (사례: 광주 푸른길)"], size=12, color=INK2, line=1.2, tag="m-4")
    notes(s, "성과지표 두 축: CLAUDE.md §5 교훈 6·7. 전주·광주 푸른길 사례는 docs/20_cases 참고.")

@slide("plans")
def _(d):
    s = std(d, "plans", "현황과 분석 : 상위계획", "상위계획 검토")
    picture(s, CR + r"\B_p148_table.png", 0.6, 1.55, 5.5, 1.86, mode="contain", align=(0, 0), border=LINE)
    text(s, 0.6, 3.55, 5.5, 0.3, "경주시 도시재생 전략계획(변경, 2022) [T1]", size=10.5, color=GRAY, tag="pl-cap")
    text(s, 0.6, 3.95, 5.5, 2.95, [dict(text="'경주역부지 개발'이 상위계획에 반영되어 있습니다.", size=14, bold=True, space_after=6),
                                  dict(text="면적 148,770㎡, 2019~2028년", bullet=True, space_after=4), dict(text="공공청사·상징광장·문화·복합상업·커뮤니티시설", bullet=True, space_after=4),
                                  dict(text="복합환승센터를 경주역에 설치(2030 도시기본계획)", bullet=True, space_after=4), dict(text="폐선로 공공공간 조성 및 신교통 도입 검토", bullet=True)], size=12, line=1.15, tag="pl-b")
    rows = [["상위계획 내용", "본 계획 반영"],
            ["공공청사", "시청·의회 캠퍼스 (3번)"], ["상징광장 · 문화·공원시설", "역전광장 · 복합문화(7번) · 근대역사관(15번)"], ["복합상업시설 · 커뮤니티시설", "성동시장 클러스터(10·11), 관광 상가(18·19), 주민 커뮤니티(9)"],
            ["복합환승센터(경주역)", "주차전용건축물(16번), 관광지원시설(17번)"], ["청년창업 · 산업 콘텐츠", "청년창업·기업지원(8번), 레지던시·공방(12~14번)"], ["폐선로의 공공공간, 도시 숲", "종축 S, 사선 보행축 R6, 수변공원"],
            [{"text": "고시 2026-8호: 주거용지 없음 [T1, 원문 대조 필요]", "color": RED, "bold": True}, {"text": "청년주거(2·4·5·6번): 본 계획이 추가하는 용도", "color": RED, "bold": True}]]
    table(s, 6.35, 1.55, [2.7, 3.68], rows, row_h=0.62, size=11, hdr_h=0.4, tag="plans-t")
    notes(s, "전략계획 PDF p.122(복합환승센터는 경주역·시외버스터미널·KTX역), p.148(경주역부지 개발), p.186(기본방향: 경주역부지 복합거점개발 및 폐선예정지역 기능재편), p.392~393(복합환승센터·경주역 부지). 고시 2026-8호: 구역 156,460㎡, 근린공원 55,415 / 상업 42,031 / 공공청사 24,987 / 문화 9,770 / 주차장 5,756㎡, 주거 없음(T1).")

# ═════════════════════════════════ 2 마스터플랜 ═════════════════════════════════
@slide("div2")
def _(d): divider(d, "div2", "2", "마스터플랜", "배치 · 구역 · 가로 · 철도 유산 · 이용 시나리오 · 단계별 추진", ZC)

@slide("boundary")
def _(d):
    s = std(d, "boundary", "마스터플랜 : 계획 경계", "계획 경계와 면적 기준")
    rows = [("시 구상 면적", 79438, "#C9D1D9", "언론 인용 [T4], 원문 확인 필요"), ("고시 구역", 156460, "#8FA9C4", "지구단위계획 고시 2026-8호 [T1]"), ("본 계획 경계", 218478, BLUE, "계획에서 설정한 경계 (약 300m × 945m)")]
    for i, (lab, v, col, note) in enumerate(rows):
        y = 1.6 + i * 1.18
        text(s, 0.6, y, 8.0, 0.36, "%s   %s㎡" % (lab, n(v)), size=14, bold=True, tag="bd-l")
        rect(s, 0.6, y + 0.4, 8.3 * v / 218478, 0.36, fill=col)
        text(s, 0.6, y + 0.8, 8.3, 0.28, note, size=10.5, color=INK2, tag="bd-n")
    text(s, 0.6, 5.2, 8.4, 1.7, [dict(text="철도 부지와 인접 시가지가 접하는 구간까지 포함하여, 기존 가로와의 접속이 가능하도록 설정하였습니다.", bullet=True, space_after=5),
                                 dict(text="고시 구역과 경계가 달라 모든 면적을 본 계획 경계 기준으로 재산정하였습니다. 고시 구역 밖은 60,498㎡(27.7%)입니다.", bullet=True, space_after=5),
                                 dict(text="본 자료의 모든 면적은 218,478㎡를 기준으로 합니다.", bullet=True, bold=True)], size=12, line=1.15, tag="bd-b")
    picture(s, A + r"\plan_lots.png", 10.0, 1.55, 2.73, 5.4, mode="contain")
    notes(s, "경계: 최종콘타모델_v2.3dm '내가 하고자하는 경계라인'(2026-10-05 저장), 218,478㎡·58점. 고시 구역 밖 60,498㎡(27.7%): work/20261005_boundary_check. 79,438㎡는 정의 불명(고시 구역의 50.8%)이라 직접 비교하지 않는다.")

@slide("plan")
def _(d):
    s = std(d, "plan", "마스터플랜 : 전체 배치", "전체 배치 계획")
    picture(s, A + r"\plan_lots.png", 0.6, 1.5, 2.66, 5.4, mode="contain")
    for i, (big, lab) in enumerate([("16", "가로"), ("19", "획지"), ("4", "공원·광장")]):
        x = 3.7 + i * 3.1
        rect(s, x, 1.55, 2.95, 1.25, fill=TINT, radius=0.1)
        text(s, x + 0.2, 1.6, 1.4, 0.9, big, size=40, bold=True, color=BLUE, tag="pl-b")
        text(s, x + 1.5, 1.95, 1.4, 0.4, lab, size=18, bold=True, tag="pl-l")
    by = {}
    for r in TR: by.setdefault(r["cat"], []).append(r["no"])
    leg = [("주거", "주거"), ("문화·교육·공공", "문화·교육·공공"), ("상업·업무", "업무"), ("창조산업", "창조(공방·레지던시)"), ("판매·음식", "판매·음식"), ("여가·오락·체육", "체육·여가"), ("역사유산", "역사"), ("교통·방문자", "주차·관광지원")]
    for i, (cat, lab) in enumerate(leg):
        x = 3.7 + (i % 2) * 4.65; y = 3.05 + (i // 2) * 0.6
        rect(s, x, y + 0.06, 0.32, 0.32, fill=CATCOL[cat])
        text(s, x + 0.42, y, 2.2, 0.42, lab, size=12, anchor="m", tag="pl-leg")
        text(s, x + 2.2, y, 2.3, 0.42, "·".join(str(k) for k in by[cat]) + "번", size=12, color=INK2, anchor="m", tag="pl-no")
    rect(s, 3.7, 5.5, 0.32, 0.32, fill="#9fd36b"); text(s, 4.12, 5.44, 2.2, 0.42, "공원·광장", size=12, anchor="m"); text(s, 6.2, 5.44, 3.0, 0.42, "A · B · C · D", size=12, color=INK2, anchor="m")
    box_text(s, 3.7, 6.05, 9.03, 0.85, "획지는 건축이 가능한 하나의 땅 단위이며, 도면의 번호는 면적표·획지계획표의 번호와 동일합니다.", fill="#FFFFFF", line=LINE, radius=0.1, size=12, tag="pl-n")

def zone_slide(d, key, z, title, sub, bullets, lots, parks_note):
    s = std(d, key, "마스터플랜 : 구역 계획", title)
    pic = {"북": "plan_north", "중": "plan_center", "남": "plan_south"}[z]
    picture(s, A + "\\%s.png" % pic, 0.6, 1.55, 5.2, 5.3, mode="contain")
    rows = [["번호", "획지명", "용도", "면적(㎡)", "층수"]]
    for no in lots: rows.append([str(no), NAME[no], USE[no], n(LOT[no]["area"]), "%dF" % LOT[no]["maxf"]])
    zs = ZSUM[z]
    rows.append([{"text": "", "fill": tint(ZC_[z], 0.75)}, {"text": "%s 합계 (획지 %d개)" % (ZNAME[z], zs["n"]), "bold": True, "fill": tint(ZC_[z], 0.75)}, {"text": "", "fill": tint(ZC_[z], 0.75)}, {"text": n(zs["area"]), "bold": True, "fill": tint(ZC_[z], 0.75), "align": "r"}, {"text": "", "fill": tint(ZC_[z], 0.75)}])
    rh = 0.4 if len(lots) <= 5 else 0.34                      # 획지가 많은 구역은 행을 줄여 아래 문장 자리를 확보
    table(s, 6.1, 1.55, [0.6, 2.35, 2.2, 0.95, 0.53], rows, row_h=rh, size=11, hdr_h=0.4, align=["c", "l", "l", "r", "c"], tag="zt")
    yb = 1.55 + 0.4 + rh * (len(rows) - 1) + 0.15
    text(s, 6.1, yb, 6.6, 0.3, parks_note, size=10.5, color=INK2, tag="zpark")
    text(s, 6.1, yb + 0.42, 6.6, 6.95 - yb - 0.42, [dict(text=b, bullet=True, space_after=5) for b in bullets], size=12, line=1.15, tag="zb")
    return s

@slide("north")
def _(d):
    s = zone_slide(d, "north", "북", "북측 구역 : %s" % ZV["북"], "", [
        "시청·의회(3번)는 고시 결정도의 공공청사(24,987㎡)와 같은 용도 유형입니다 [T1]. 이전 여부는 정책 결정 사항이므로 '이전 유·무'를 비교 대안으로 둡니다(가정).",
        "청년주거 4개 획지(2·4·5·6번)는 결정도에 없는 신규 용도로, 용도 변경 협의가 필요합니다 [T1, 원문 대조 필요].",
        "북천 수변공원을 북측 경계에 조성하며, 북천 건너 황성공원과의 연계는 다음 단계에서 검토합니다."], ZL["북"], "공원: Park A 북천 수변공원 %s㎡" % n(S_["park_A"]))
    notes(s, "북측 합계 = 획지 1~6번. 시청 인원·면적은 20261001 시청 면적표 참고(법정 상한 21,110㎡, 지상 25,400㎡ 가정).")

@slide("center")
def _(d):
    s = zone_slide(d, "center", "중", "중앙 구역 : %s" % ZV["중"], "", [
        "동서 그린 보행축(Park B)으로 성동시장과 황오동을 연결합니다.",
        "삼층석탑 반경 22m는 비움 공간으로 계획합니다(허용기준 원문 확인 전, 보수적 가정).",
        "시장·체험·공방을 선형으로 배치하여 방문객의 보행 체류를 유도합니다."], ZL["중"], "공원: Park B 동서 그린 보행축 %s㎡" % n(S_["park_B"]))
    notes(s, "중앙 = 획지 7~14번. 성동시장 클러스터(10)는 2층 장옥 바 + 서변 3층 가로상점. 체험판매(11)는 2층 점포 두 줄.")

@slide("south")
def _(d):
    s = zone_slide(d, "south", "남", "남측 구역 : %s" % ZV["남"], "", [
        "구 역사(기존 건물 형상 1,404㎡, 2층)를 역전광장 전면으로 이전하고(가정), 근대역사관·전시장으로 재사용합니다.",
        "차량 방문객은 주차전용건축물(16번)에 주차한 후 보행으로 진입합니다.",
        "지하주차는 매장문화재 조사 여건상 1단계에 포함하지 않습니다 [T2, 김권일 2026.02]."], ZL["남"], "공원: Park C 역전광장 %s㎡ · Plaza D 환승광장 %s㎡" % (n(S_["park_C"]), n(1932)))
    notes(s, "남측 = 획지 15~19번. 구 역사 이전은 초기 스케치('구경주역 옮김')를 반영한 가정이며 코레일 협의가 필요하다.")

@slide("roads")
def _(d):
    s = std(d, "roads", "마스터플랜 : 가로", "도시 가로 계획")
    picture(s, A + r"\plan_roads.png", 0.6, 1.5, 2.66, 5.4, mode="contain")
    types = [("차량 통행 가로", "#5d7fb0", "폭 8~15m", "차량과 보행자가 공존합니다(30km/h 이하). A·B·C·D·S2·E 가로", "A가로(15m)는 화랑로를 대상지 내부로 연결합니다."),
             ("공유가로 S", "#f19a3e", "폭 16m · 길이 501m", "보행자 우선 가로로, 셔틀·서비스·비상 차량만 통행합니다.", "폐선 노반과 나란한 종축으로 시장·시청·수변을 연결합니다."),
             ("보행 전용 가로", "#d1495b", "폭 10~14m", "보행자 전용입니다. 사선 R6(513m), R7, R8, R9", "R6은 황오동에서 원효로 방향으로 대각 연결됩니다."),
             ("보행 골목", "#a58bd0", "폭 6m · 5개소", "보행자 우선이며 비상 차량 통행이 가능합니다.", "동측 기존 골목(3m·4m)을 계승합니다.")]
    for i, (ttl, col, w_, how, eg) in enumerate(types):
        x = 3.65 + (i % 2) * 4.6; y = 1.55 + (i // 2) * 2.45
        rect(s, x, y, 4.45, 2.32, fill=TINT, radius=0.1); rect(s, x, y, 4.45, 0.14, fill=col)
        text(s, x + 0.2, y + 0.22, 4.0, 0.4, ttl, size=18, bold=True, tag="rd-t")
        text(s, x + 0.2, y + 0.68, 4.0, 0.3, w_, size=12, bold=True, color=INK2, tag="rd-w")
        text(s, x + 0.2, y + 1.02, 4.05, 0.7, how, size=12, line=1.15, tag="rd-h")
        text(s, x + 0.2, y + 1.7, 4.05, 0.6, eg, size=10.5, color=INK2, line=1.15, tag="rd-e")
    box_text(s, 3.65, 6.42, 9.05, 0.55, [dict(runs=[("빨간 원", dict(color="#c0392b", bold=True)), (" = 기존 가로 접속 지점(37개소). 접속부 폭은 기존 가로 폭에 맞추었습니다.", {})])], fill="#FFFFFF", line=LINE, radius=0.1, size=12, tag="rd-n")

@slide("roadtable")
def _(d):
    s = std(d, "roadtable", "마스터플랜 : 가로", "가로 계획표", "합계 %s㎡ (차량 통행 가로 %s㎡ + 보행 가로·골목 %s㎡)  ·  단면(차도·보도·식재 폭)은 계획 가정" % (n(S_["road_total"]), n(S_["road_veh"]), n(S_["road_ped"])))
    rows = [["가로", "폭(m)", "연장(m)", "성격", "통행 방식", "연결 대상"],
            ["A가로", "15", "282", "연결가로", "차량·보행 공존(30km/h)", "화랑로에서 진입하는 주 출입 가로"],
            ["S축", "16", "501", "종축 공유가로", "보행자 우선, 셔틀·서비스 차량 한정", "폐선 노반과 평행, 시장~시청~수변 연결"],
            ["B가로", "12", "288", "동서 그린 보행가로", "차량·보행 공존", "성동시장 ↔ 황오동, 양측 녹지대"],
            ["C가로", "12", "295", "북측 연결가로", "차량·보행 공존", "북성로 축의 서·동 가로 연결"],
            ["D가로", "10", "149", "북서 접속가로", "차량·보행 공존", "시청 북측, 기존 골목에 접속"],
            ["S2가로", "10", "148", "남동 연결가로", "차량·보행 공존", "기존 11m 남북 가로의 연장"],
            ["E가로", "8", "201", "남측 연결가로", "일방통행 차량 + 보행", "남측 기존 골목과 연속"],
            ["R6축", "14", "513", "사선 보행축", "보행 전용(비상 차량 4m 확보)", "황오동 ↔ 원효로 코너(고분 방향)"],
            ["R7", "14", "136", "북단 사선 보행로", "보행 전용", "종축에서 수변공원으로 연결"],
            ["R8", "10", "216", "수변 보행로", "보행·자전거", "북동 경계를 따라 북천 방향으로 연결"],
            ["R9", "10", "137", "북단 보행가로", "보행 전용", "수변공원 남측 경계"],
            ["골목 5개소", "6", "합 546", "보행자 우선 골목", "보행 우선, 비상 차량 통행 가능", "동측 기존 골목(3m·4m) 계승"]]
    table(s, 0.6, 1.8, [1.25, 0.75, 0.95, 2.2, 3.4, 3.58], rows, row_h=0.38, size=10.5, hdr_h=0.4, align=["l", "c", "c", "l", "l", "l"], bold_cols=(0,), tag="rt")

@slide("memory")
def _(d):
    s = std(d, "memory", "마스터플랜 : 철도 유산", "철도 유산의 계승")
    picture(s, CR + r"\B_p97_station_photo.png", 0.6, 1.55, 6.4, 1.56, mode="cover", align=(0.5, 0.5))
    picture(s, CR + r"\A_p105_photo3.png", 0.6, 3.2, 6.4, 3.7, mode="cover", align=(0.5, 0.5))
    photo_credit(s, 0.6, 3.2, 6.4, 3.7, "사진: 경주시 도시재생 전략계획(2022) · 원도심 미래구상 기획연구(2025, 전홍표)")
    cards = [("1", "종축 S", "폐선 노반과 평행한 폭 16m의 보행 중심 가로입니다. 철도가 지나던 선형 축이 시장·시청·수변을 연결하는 가로로 계승됩니다."), ("2", "구 역사", "기존 건물 형상(1,404㎡, 2층)을 그대로 역전광장 전면으로 이전하여 근대역사관·전시장으로 재사용합니다."), ("3", "삼층석탑 마당", "석탑 반경 22m를 비움 공간으로 조성합니다. 시장 중심부의 휴게 공간으로 활용됩니다.")]
    for i, (num, ttl, body) in enumerate(cards):
        y = 1.55 + i * 1.5
        rect(s, 7.35, y, 5.38, 1.38, fill=TINT, radius=0.1); oval(s, 7.5, y + 0.15, 0.5, BLUE, num, size=14)
        text(s, 8.15, y + 0.1, 4.4, 0.35, ttl, size=14, bold=True, tag="mem-t"); text(s, 8.15, y + 0.5, 4.45, 0.85, body, size=10.5, color=INK2, line=1.15, tag="mem-b")
    box_text(s, 7.35, 6.1, 5.38, 0.85, "대안 의견: 한 연구는 구 역사의 현 위치 보존을 제안합니다. 본 계획은 이전하되 동일한 광장 축에 배치합니다. (가정, 협의 필요)", fill="#FFFFFF", line=RED, radius=0.1, size=10.5, line_sp=1.15, tag="mem-o")

@slide("axo")
def _(d):
    s = d.slide(TINT)
    picture(s, PLAN + r"\02_조감도_SiteAnchors.png", 0, 0, SW, SH, mode="contain")
    page_no(s, PAGE["axo"])
    notes(s, "02 조감도(Site Anchors, 통영 보고서 p.32 형식). 번호 = 획지, A~D = 공원·광장. 규제 미적용 개념안.")

@slide("day")
def _(d):
    s = std(d, "day", "마스터플랜 : 이용 시나리오", "이용자별 하루 시나리오", "시나리오는 계획 의도를 설명하기 위한 가정입니다.")
    lanes = [("방문 인구", "가족 · 주말", ZS, [("10:30", "주차전용건축물 주차"), ("11:00", "구 역사·근대역사관 관람"), ("12:30", "성동시장 점심 식사"), ("14:30", "공방 체험"), ("16:30", "그린 보행축 이동, 황오동 카페 이용")]),
             ("근로 인구", "시청 직원 · 평일", ZN, [("08:50", "시청·의회 출근"), ("12:10", "성동시장 점심 식사"), ("15:00", "창업지원센터 회의"), ("18:20", "1층 상가 경유 퇴근"), ("19:00", "황오동 저녁 식사")]),
             ("정주 인구", "청년 주민 · 일상", YEL, [("07:40", "청년주거에서 출근"), ("18:30", "퇴근 후 1층 생활 상가 이용"), ("20:00", "체육시설·영화관 이용"), ("21:30", "골목을 통한 귀가"), ("야간", "주거 창의 조명으로 가로 안전감 확보")])]
    for i, (who, sub, col, steps) in enumerate(lanes):
        x = 0.6 + i * 4.1
        box_text(s, x, 1.75, 3.93, 0.8, [dict(text=who, size=16, bold=True, color=INK if col in (YEL, ZS) else "#FFFFFF"), dict(text=sub, size=10.5, color=INK if col in (YEL, ZS) else "#FFFFFF")], fill=col, radius=0.1, anchor="m", margin=(0.2, 0.05, 0.2, 0.05), tag="day-h")
        for k, (tm, tx) in enumerate(steps):
            y = 2.7 + k * 0.82
            rect(s, x, y, 3.93, 0.72, fill=TINT, radius=0.08)
            text(s, x + 0.12, y + 0.05, 0.85, 0.6, tm, size=12, bold=True, color=BLUE, anchor="m", tag="day-t")
            text(s, x + 1.0, y + 0.05, 2.85, 0.62, tx, size=12, anchor="m", line=1.1, tag="day-x")

@slide("phases")
def _(d):
    s = std(d, "phases", "마스터플랜 : 단계", "단계별 추진 계획")
    ph = [("1단계", "가로·광장", "A가로·종축·사선 보행축, 그린 보행축·역전광장, 임시 평면주차. 구 역사 이전 준비.", "되돌릴 수 있는 투자, 즉각적 효과", BLUE),
          ("2단계", "핵심 시설", "시굴 조사 후 시청·의회, 주차전용건축물, 성동시장 클러스터, 근대역사관.", "매장문화재 조사 선행", ZN),
          ("3단계", "생활 시설", "청년주거, 문화·창업·커뮤니티, 레지던시·공방, 공공체육.", "정주·근로 인구 확대", ZC),
          ("4단계", "완성", "관광지원시설, 관광 상가, 수변공원 완성.", "수요 확인 후 추진", ZS)]
    for i, (p, ttl, items, why, col) in enumerate(ph):
        x = 0.6 + i * 3.1
        box_text(s, x, 1.65, 2.95, 0.7, [dict(runs=[(p + "  ", dict(size=14, bold=True)), (ttl, dict(size=16, bold=True))])], fill=col, radius=0.1, color=INK if col in (ZS,) else "#FFFFFF", anchor="m", margin=(0.2, 0.05, 0.2, 0.05), tag="ph-h")
        rect(s, x, 2.45, 2.95, 2.75, fill=TINT, radius=0.1)
        text(s, x + 0.15, 2.58, 2.65, 1.7, items, size=12, line=1.2, tag="ph-i")
        line(s, x + 0.15, 4.35, x + 2.8, 4.35, LINE, 0.75)
        text(s, x + 0.15, 4.45, 2.65, 0.7, why, size=10.5, color=INK2, line=1.15, tag="ph-w")
        if i < 3: arrow_right(s, x + 2.98, 3.7, 0.12, 0.3, GRAY)
    box_text(s, 0.6, 5.5, 12.13, 1.3, [dict(text="단계 설정 원칙: 되돌리기 어려운 대규모 투자는 후순위로 배치합니다.", size=14, bold=True, space_after=3), dict(text="참고 사례: 안동역은 연결도로·산책로·주차를 먼저 조성하였고, 교토 우메코지는 공원(1995)을 먼저 개원한 뒤 29년에 걸쳐 시설을 추가하였습니다. 단계 순서는 계산으로 확정하지 않은 초안입니다.", size=10.5, color=INK2, line=1.15)],
             fill="#FFFFFF", line=LINE, radius=0.1, anchor="m", margin=(0.25, 0.08, 0.25, 0.08), tag="ph-b")

# ═════════════════════════════════ 3 계획 수치의 근거 ═════════════════════════════════
@slide("div3")
def _(d): divider(d, "div3", "3", "계획 수치의 근거", "면적표 · 획지계획표 · 산정 방법 · 규제 검토", ZN)

@slide("area1")
def _(d):
    s = std(d, "area1", "계획 수치의 근거 : 면적표 ①", "토지이용 면적 구성")
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE
    cd = CategoryChartData(); cd.categories = ["공원·광장", "도로", "획지"]; cd.add_series("면적", [S_["park_total"], S_["road_total"], S_["lot_total"]])
    gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(0.6), Inches(1.6), Inches(4.7), Inches(4.7), cd); ch = gf.chart
    ch.has_legend = False; ch.has_title = False
    pl = ch.plots[0]; pl.has_data_labels = False
    for i, col in enumerate(["#9fd36b", "#b9b9b6", BLUE]):
        pt = pl.series[0].points[i]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = rgb(col); pt.format.line.color.rgb = rgb("#FFFFFF"); pt.format.line.width = Pt(2)
    dn = ch._chartSpace.find(".//" + qn("c:doughnutChart")); hs = dn.find(qn("c:holeSize"))
    if hs is None: hs = etree.SubElement(dn, qn("c:holeSize"))
    hs.set("val", "62")
    text(s, 1.45, 3.45, 3.0, 0.5, "218,478㎡", size=20, bold=True, align="c", tag="dn-c")
    text(s, 1.45, 3.95, 3.0, 0.3, "계획 경계 전체", size=10.5, color=INK2, align="c", tag="dn-c2")
    rows = [("#9fd36b", "공원·광장", S_["park_total"], "북천 수변공원, 동서 그린 보행축, 역전광장, 환승광장"), ("#b9b9b6", "도로", S_["road_total"], "차량 통행 가로 %s㎡ + 보행 가로·골목 %s㎡" % (n(S_["road_veh"]), n(S_["road_ped"]))), (BLUE, "획지", S_["lot_total"], "건축 가능 획지 19개")]
    for i, (col, lab, v, desc) in enumerate(rows):
        y = 1.65 + i * 1.3
        rect(s, 5.8, y, 6.93, 1.18, fill=TINT, radius=0.1); rect(s, 5.8, y, 0.14, 1.18, fill=col)
        text(s, 6.15, y + 0.08, 2.4, 0.4, lab, size=16, bold=True, tag="a1-l")
        text(s, 6.15, y + 0.52, 6.4, 0.55, desc, size=12, color=INK2, tag="a1-d")
        text(s, 9.1, y + 0.08, 2.0, 0.45, "%s㎡" % n(v), size=16, bold=True, align="r", tag="a1-v")
        text(s, 11.2, y + 0.08, 1.4, 0.45, "%.1f%%" % (v / S_["planned"] * 100), size=16, bold=True, color=BLUE, align="r", tag="a1-p")
    box_text(s, 5.8, 5.6, 6.93, 1.3, [dict(text="세 항목의 합계는 계획 경계 면적과 일치합니다.", size=14, bold=True, space_after=4), dict(text="합계 218,478㎡, 차이 0㎡. 공원·광장 비율 %.1f%%의 확대 여부는 추가 결정이 필요합니다." % (S_["park_total"] / S_["planned"] * 100), size=12, color=INK2)], fill="#FFFFFF", line=BLUE, line_w=1.5, radius=0.1, anchor="m", margin=(0.25, 0.1, 0.25, 0.1), tag="a1-n")
    notes(s, "03_면적표 Site Area 표와 같은 값. 합계 검증: 공원 + 도로 + 획지 = 계획부지 = U 면적(차 0.000㎡).")

@slide("area2")
def _(d):
    s = std(d, "area2", "계획 수치의 근거 : 면적표 ②", "건축 규모 : 연면적 %s㎡ · 용적률 %d%%" % (n(F_["total"]), round(F_["far"] * 100)))
    rows = [("판매·음식", F_["rows"][3][3], "#f4a0c2"), ("문화·교육·공공", F_["rows"][2][3], "#6f9fdc"), ("주거", F_["rows"][6][3], "#f1d247"), ("주차전용건축물", F_["rows"][9][3], "#c6c6c6"), ("창조산업", F_["rows"][1][3], "#a98bd3"),
            ("업무·상업", F_["rows"][0][3], "#e4573a"), ("여가·오락·체육", F_["rows"][5][3], "#2fab9d"), ("관광지원", F_["rows"][8][3], "#c6c6c6"), ("역사유산", F_["rows"][7][3], "#c9742f"), ("숙박", 0, "#c9742f")]
    for i, (lab, v, col) in enumerate(rows):
        y = 1.6 + i * 0.52
        text(s, 0.6, y, 1.9, 0.4, lab, size=12, anchor="m", tag="a2-l")
        w = max(0.03, 2.85 * v / F_["rows"][3][3]); rect(s, 2.55, y + 0.05, w, 0.3, fill=col)
        text(s, 2.55 + w + 0.08, y, 2.1, 0.4, ("%s㎡  (%.1f%%)" % (n(v), v / F_["total"] * 100)) if v else "0  (미반영)", size=11, bold=True, anchor="m", tag="a2-v")
    defs = [("연면적", "지상 각 층 바닥면적의 합계", "%s㎡" % n(F_["total"])), ("건폐율", "획지 면적 대비 건물이 덮는 바닥면적의 비율", "%d%%" % round(F_["coverage"] * 100)), ("용적률", "획지 면적 대비 연면적의 비율", "%d%%" % round(F_["far"] * 100))]
    for i, (k, mean, val) in enumerate(defs):
        y = 1.6 + i * 1.05
        rect(s, 7.6, y, 5.13, 0.95, fill=TINT, radius=0.1)
        text(s, 7.8, y + 0.08, 1.7, 0.4, k, size=14, bold=True, tag="a2-k"); text(s, 7.8, y + 0.5, 3.4, 0.4, mean, size=10.5, color=INK2, tag="a2-m")
        text(s, 11.0, y + 0.18, 1.6, 0.6, val, size=20, bold=True, color=BLUE, align="r", tag="a2-val")
    box_text(s, 7.6, 4.85, 5.13, 2.05, [dict(text="판매·음식 비중이 가장 큽니다.", size=12, bold=True, space_after=2), dict(text="성동시장·체험판매·관광 상가 세 프로그램의 합이며, 방문객 중심으로 편중될 수 있습니다.", size=10.5, color=INK2, space_after=6),
                                        dict(text="숙박 면적은 0㎡입니다.", size=12, bold=True, space_after=2), dict(text="스케치에 포함되지 않았으며 시 구상의 '경주 STAY'와 차이가 있어, 반영 여부의 결정이 필요합니다.", size=10.5, color=INK2)], fill="#FFFFFF", line=RED, radius=0.1, anchor="m", margin=(0.25, 0.1, 0.25, 0.1), tag="a2-n")

def lot_table(d, key, lots, label, title):
    s = std(d, key, label, title, "건폐율 = 건축면적 ÷ 획지 면적  ·  용적률 = 연면적 ÷ 획지 면적  ·  높이 = 층수 × 층고(가정)")
    rows = [["번호", "획지명", "용도", "면적(㎡)", "건폐율", "용적률", "층수", "높이"]]
    for no in lots:
        r = LOT[no]; rows.append([str(no), NAME[no], USE[no], n(r["area"]), "%d%%" % round(r["bcr"] * 100), "%d%%" % round(r["far"] * 100), "%dF" % r["maxf"], "%.1fm" % r["maxh"]])
    table(s, 0.6, 1.8, [0.6, 3.0, 2.9, 1.15, 1.0, 1.0, 0.8, 1.0], rows, row_h=0.43, size=11, hdr_h=0.42, align=["c", "l", "l", "r", "r", "r", "c", "r"], tag=key)
    return s

@slide("lots1")
def _(d): lot_table(d, "lots1", list(range(1, 11)), "계획 수치의 근거 : 획지계획표 ①", "획지계획표 ① 북측·중앙 (1~10번)")

@slide("lots2")
def _(d):
    s = lot_table(d, "lots2", list(range(11, 20)), "계획 수치의 근거 : 획지계획표 ②", "획지계획표 ② 중앙·남측 (11~19번)")
    tot = sum(LOT[i]["area"] for i in LOT); gf = sum(LOT[i]["gfa"] for i in LOT)
    box_text(s, 0.6, 6.3, 12.13, 0.55, "19개 획지 합계 : 면적 %s㎡ · 연면적 %s㎡ · 건폐율 %.1f%% · 용적률 %.1f%%" % (n(tot), n(gf), sum(LOT[i]["fp"] for i in LOT) / tot * 100, gf / tot * 100), fill=TINT, radius=0.1, size=14, bold=True, anchor="m", margin=(0.3, 0.05, 0.3, 0.05), tag="lots2-tot")

@slide("how")
def _(d):
    s = std(d, "how", "계획 수치의 근거 : 산정 방법", "수치 산정 방법과 근거 구분", "측정값: 도면에서 직접 산출  ·  가정: 본 계획에서 설정, 변경 가능  ·  원문 확인 전: 법령·고시 원문 대조 필요")
    rows = [["항목", "의미", "산정 방법", "구분"],
            ["획지 면적", "도면상 획지의 크기", "계획 도면의 폴리곤 면적", {"text": "측정값", "color": "#1a7f37", "bold": True}],
            ["건축면적 · 연면적", "건물 1층 바닥면적 / 전 층 바닥면적 합계", "건축면적 × 층수 (층수는 본 계획에서 설정)", {"text": "산정 + 가정", "color": "#b45309", "bold": True}],
            ["건폐율 · 용적률", "획지 면적 대비 건축 규모의 비율", "건축면적 ÷ 획지 면적, 연면적 ÷ 획지 면적", {"text": "산정", "color": "#1a7f37", "bold": True}],
            ["높이", "건물의 높이", "층수 × 층고 (주거 3.2m, 업무 3.8m, 판매 4.2m 등)", {"text": "가정", "color": "#b45309", "bold": True}],
            ["세대 수", "청년주거 세대 수", "주거 연면적의 70%% ÷ 36~60㎡ → %d~%d세대" % (round(SM["units60"]), round(SM["units36"])), {"text": "가정", "color": "#b45309", "bold": True}],
            ["주차 면수", "주차 가능 대수", "주차전용건축물 연면적 ÷ 32㎡ → 약 %d면" % round(SM["park_spaces"]), {"text": "가정", "color": "#b45309", "bold": True}],
            ["가로 폭", "가로의 너비", "기존 가로 접속부 폭 계승(단면 구성은 본 계획에서 설정)", {"text": "일부 확인", "color": "#b45309", "bold": True}],
            ["높이 제한", "법정 높이 한도", "도심 10~36m 고도지구를 참고 비교(미적용)", {"text": "원문 확인 전", "color": RED, "bold": True}]]
    table(s, 0.6, 1.8, [2.2, 2.9, 5.5, 1.53], rows, row_h=0.58, size=11, hdr_h=0.42, align=["l", "l", "l", "c"], bold_cols=(0,), tag="how")

@slide("open")
def _(d):
    s = std(d, "open", "계획 수치의 근거 : 향후 과제", "확인 사항과 결정 사항")
    box_text(s, 0.6, 5.85, 12.13, 0.95, "확인 사항은 원문 대조로 확정하고, 결정 사항은 대안 비교로 판단합니다. 다음 단계는 '규제 적용'과 '대안 비교'입니다.", fill="#FFFFFF", line=BLUE, line_w=1.5, radius=0.1, size=14, bold=True, anchor="m", margin=(0.3, 0.05, 0.3, 0.05), tag="op-b")
    box_text(s, 0.6, 1.6, 5.95, 4.05, [dict(text="확인 사항", size=18, bold=True, space_after=8),
                                      dict(text="시 구상 면적 79,438㎡는 언론 인용값 [T4]", bullet=True, space_after=6), dict(text="도로 규모 구분(중로·소로)의 폭 기준 [T1 원문 미확인]", bullet=True, space_after=6),
                                      dict(text="고도지구 높이 기준 및 고시 2026-8호 원문 대조", bullet=True, space_after=6), dict(text="구 역사 이전 가능 여부(코레일 협의). 한 연구는 현 위치 보존을 제안", bullet=True, space_after=6),
                                      dict(text="삼층석탑 주변 허용기준(반경 22m는 보수적 가정)", bullet=True)], fill=TINT, radius=0.1, size=12, line_sp=1.15, anchor="t", margin=(0.35, 0.25, 0.3, 0.2), tag="op1")
    box_text(s, 6.78, 1.6, 5.95, 4.05, [dict(text="결정 사항", size=18, bold=True, space_after=8),
                                       dict(text="숙박(STAY) 반영 여부 — 현재 0㎡", bullet=True, space_after=6), dict(text="판매·음식 비중(%.1f%%)의 조정 여부" % (F_["rows"][3][3] / F_["total"] * 100), bullet=True, space_after=6),
                                       dict(text="공원·광장 비율(%.1f%%)의 확대 여부" % (S_["park_total"] / S_["planned"] * 100), bullet=True, space_after=6), dict(text="집약형 안과 분산 삽입형 안의 비교 여부", bullet=True, space_after=6),
                                       dict(text="종축의 위치 — 폐선 노반 위 또는 현 위치(60m 동측)", bullet=True)], fill=tint(YEL, 0.7), radius=0.1, size=12, line_sp=1.15, anchor="t", margin=(0.35, 0.25, 0.3, 0.2), tag="op2")

@slide("rules")
def _(d):
    s = std(d, "rules", "계획 수치의 근거 : 규제", "규제 4겹 검토")
    cards = [("1", "용도지역", "자연녹지 77.5% · 2종일반주거 16.3% · 일반상업 6.2%"), ("2", "고도지구", "도심 20m 지구 89% · 15m 지구 9.8%"), ("3", "보존지역 허용기준", "삼층석탑 등 유적 주변의 건축 제한"), ("4", "지구단위계획(고시 2026-8호)", "공원·상업·공공청사·문화·주차. 주거 없음")]
    for i, (num, ttl, body) in enumerate(cards):
        y = 1.6 + i * 1.3
        rect(s, 0.6, y, 6.9, 1.18, fill=TINT, radius=0.1); oval(s, 0.8, y + 0.3, 0.55, BLUE, num, size=16)
        text(s, 1.55, y + 0.1, 5.8, 0.4, ttl, size=14, bold=True, tag="ru-t"); text(s, 1.55, y + 0.55, 5.8, 0.55, body, size=11, color=INK2, tag="ru-b")
    box_text(s, 7.85, 1.6, 4.88, 2.45, [dict(text="본 안 검토 결과(참고)", size=12, bold=True, color=RED, space_after=4), dict(text="높이 기준 초과 건물 %d동" % len(OVER), size=20, bold=True, space_after=2),
                                        dict(text="연면적 %s㎡ (%.1f%%). 5층(16.0m) 1개소, 6~8층(22.8~30.4m) 2개소입니다." % (n(sum(o[6] for o in OVER)), sum(o[6] for o in OVER) / F_["total"] * 100), size=12, color=INK2, line=1.15)], fill="#FFFFFF", line=RED, radius=0.1, anchor="m", margin=(0.25, 0.1, 0.25, 0.1), tag="ru-r")
    box_text(s, 7.85, 4.25, 4.88, 2.55, [dict(text="다음 단계", size=12, bold=True, color=BLUE, space_after=4), dict(text="규제 4겹을 적용하여 층수를 조정하고 수치를 재산정합니다.", size=14, bold=True, space_after=6), dict(text="규제를 선적용한 기존 안의 연면적은 157,059㎡, 본 안은 %s㎡입니다. 두 값의 차이는 규제에 따른 볼륨 감소 규모를 가늠하는 참고값입니다(두 안의 구획이 달라 직접 비교는 불가)." % n(F_["total"]), size=10.5, color=INK2, line=1.15)],
             fill=TINT, radius=0.1, anchor="m", margin=(0.25, 0.1, 0.25, 0.1), tag="ru-n")
    notes(s, "용도지역 비율: V-World UQ111 겹침, 5m 격자 표본 ±1%(팩트체크 문서 §2.2, T2). 고도지구: V-World UQ123 + 경북고시 2020-479(전체기록 §1.4). 고도지구 값은 고시 원문 대조 전.")

# ═════════════════════════════════ 4 계획 인구와 운영 ═════════════════════════════════
@slide("div4")
def _(d): divider(d, "div4", "4", "계획 인구와 운영", "계획 인구 산정 · 운영 체계", YEL)

@slide("pop")
def _(d):
    s = std(d, "pop", "계획 인구와 운영 : 계획 인구", "계획 인구 산정 (가정)")
    r_h = F_["rows"][6][3]
    rows = [["구분", "계획 규모 (가정)", "산정 방법", "상태"],
            ["정주 인구", "약 %s~%s명 (%d~%d세대)" % (n(SM["units60"] * 1.3), n(SM["units36"] * 1.3), round(SM["units60"]), round(SM["units36"])), "청년주거 연면적 %s㎡ × 70%% ÷ 36~60㎡, 1세대 1.3명" % n(r_h), "가정"],
            ["근로 인구", "약 %s명" % n(960 + F_["rows"][0][3] / 16), "시청 약 960명(유사 도시 청사 사례 참고) + 업무 연면적 %s㎡ ÷ 16㎡" % n(F_["rows"][0][3]), "가정"],
            ["방문 인구", "다음 단계에서 산정", "방문 시설 연면적 ÷ 1인 이용면적 × 회전율 (경주 전체 방문객 872만 명은 적용하지 않음)", "미정"]]
    table(s, 0.6, 1.6, [2.0, 3.2, 5.6, 1.33], rows, row_h=0.95, size=12, hdr_h=0.45, align=["l", "l", "l", "c"], bold_cols=(0,), tag="pop", valign="m")
    box_text(s, 0.6, 5.5, 12.13, 1.35, [dict(text="본 수치는 예측값이 아닌 '계획 가정'입니다.", size=14, bold=True, space_after=3), dict(text="공식 통계는 대상지 규모 산정에 사용하지 않으며, 시설 면적으로부터 이용 인구를 역산합니다.", size=12, color=INK2)],
             fill=TINT, radius=0.1, anchor="m", margin=(0.3, 0.1, 0.3, 0.1), tag="pop-n")
    notes(s, "근로 인구: 시청 본청 약 900명 + 의원 22 + 사무국 40 ≈ 960명(전체기록 §3.4, 벤치마크 순천 960·익산 950), 업무 1인 16㎡(전체기록 4.5c). 이 합산은 시청과 업무시설을 이중 계산하지 않는다(시청은 업무 면적에 들어 있지 않음).")

@slide("ops")
def _(d):
    s = std(d, "ops", "계획 인구와 운영 : 운영", "운영 주체와 재원 계획")
    rows = [("가로·광장·공원", "시가 관리하고 시민 참여형 운영 협의체를 구성합니다.", "사례: 광주 푸른길은 (사)푸른길이 운영"), ("성동시장 클러스터", "임대료를 낮추어 상인에게 공급하고 시장 상인회와 공동 운영합니다.", "기존 시장과의 경쟁을 피하고 연계를 유지"),
            ("주차전용건축물", "주차 수입으로 셔틀·광장 운영비의 일부를 충당합니다.", "차량 방문객의 보행 진입 유도"), ("시청 저층부·광장", "임대 수입으로 공공공간을 관리합니다.", "주간 이용자의 상가 이용 연계"), ("청년주거", "공공임대 또는 기숙사 형태로 공공기관이 운영합니다.", "주거 비율 유지 장치")]
    for i, (what, how, why) in enumerate(rows):
        y = 1.6 + i * 1.0
        rect(s, 0.6, y, 12.13, 0.9, fill=TINT, radius=0.08)
        text(s, 0.8, y + 0.05, 2.6, 0.8, what, size=14, bold=True, anchor="m", tag="ops-w")
        text(s, 3.5, y + 0.05, 5.4, 0.8, how, size=12, anchor="m", line=1.15, tag="ops-h")
        text(s, 9.1, y + 0.05, 3.5, 0.8, why, size=10.5, color=INK2, anchor="m", line=1.15, tag="ops-y")
    box_text(s, 0.6, 6.6, 12.13, 0.45, "위 내용은 모두 가정이며, 운영 주체와 재원은 다음 단계에서 확정합니다.", fill="#FFFFFF", line=RED, radius=0.08, size=12, bold=True, color=RED, align="c", anchor="m", margin=(0.2, 0.02, 0.2, 0.02), tag="ops-n")

# ═════════════════════════════════ 맺음말 ═════════════════════════════════
@slide("before")
def _(d):
    s = d.slide("#FFFFFF")
    picture(s, A + r"\hero_before.jpg", 0, 0, SW, SH, mode="cover")
    box_text(s, 0.6, 5.55, 8.4, 1.45, [dict(text="현황", size=12, bold=True, color=RED, space_after=2), dict(text="폐역 부지의 현재 모습", size=27, bold=True, space_after=2), dict(text="도심 중앙의 남북 방향 공백지가 동서 간 보행 연결을 단절하고 있습니다.", size=12, color=INK2)], fill="#FFFFFF", alpha=0.9, radius=0.1, anchor="m", margin=(0.3, 0.1, 0.3, 0.1), tag="before")
    page_no(s, PAGE["before"]); notes(s, "다음 장과 같은 카메라의 흑백 현황. 경계 안 기존 건물(NGII 연속수치지도)만 남긴 렌더.")

@slide("after")
def _(d):
    s = d.slide("#FFFFFF")
    picture(s, A + r"\hero_after.jpg", 0, 0, SW, SH, mode="cover")
    box_text(s, 0.6, 5.55, 9.4, 1.45, [dict(text="제안", size=12, bold=True, color=RED, space_after=2), dict(text="원도심 복합 생활거점", size=27, bold=True, space_after=2), dict(text="남측 관문, 중앙 교류, 북측 근로·정주 구역으로 구성하며 활력은 성동시장·황오동으로 확산됩니다.", size=12, color=INK2)], fill="#FFFFFF", alpha=0.9, radius=0.1, anchor="m", margin=(0.3, 0.1, 0.3, 0.1), tag="after")
    page_no(s, PAGE["after"])

@slide("sources")
def _(d):
    s = std(d, "sources", "자료 : 출처", "자료 출처와 확인 상태")
    rows = [["등급", "자료", "활용 내용"],
            ["T1 법정·승인 문서", "경주시 도시재생 전략계획(변경, 2022) / 고시 제2026-8호(원문 대조 필요) / 2030 경주 도시기본계획", "철도 부지 148,770㎡, 상위계획, 고시 용도"],
            ["T2 공공 발간·통계", "경주시 원도심 미래구상 기획연구(2025) / 황오동 모니터링 보고서(2025.09) / 연속수치지도(NGII) / V-World 용도지역·고도지구 / KOSIS", "시민 응답, 방문객 설문, 황오동 인구, 가로·건물, 규제 비율"],
            ["T4 언론·2차", "시 구상 면적 79,438㎡, 방문객 872만 명, 폐역 시기 — 원문 확인 필요", "배경 설명에만 활용하고 규모 산정에는 사용하지 않음"],
            ["자체 산출", "계획 도면 기준 면적, 연면적, 건폐율·용적률 / 세대·주차·인구 가정", "면적표, 획지계획표, 가로계획표"]]
    table(s, 0.6, 1.6, [2.3, 6.4, 3.43], rows, row_h=1.0, size=11, hdr_h=0.42, align=["l", "l", "l"], bold_cols=(0,), tag="src", valign="m")
    text(s, 0.6, 6.2, 12.1, 0.7, "사진·지도 이미지는 경주시 원도심 미래구상 기획연구(2025)와 도시재생 전략계획(변경, 2022)에서 발췌하였으며, 도면(획지·가로·조감도)은 본 계획에서 작성하였습니다.", size=12, color=INK2, line=1.2, tag="src-n")

def appendix(d, key, fname, label):
    s = d.slide(TINT); picture(s, PLAN + "\\" + fname, 0, 0, SW, SH, mode="contain"); page_no(s, PAGE[key]); notes(s, label); return s
@slide("app1")
def _(d): appendix(d, "app1", "01_획지구획도_획지계획표.png", "부록 1 · 획지 구획도 + 획지계획표 (A3 원본)")
@slide("app2")
def _(d): appendix(d, "app2", "03_면적표.png", "부록 2 · 면적표 (통영 보고서 p.18 형식, A3 원본)")
@slide("app3")
def _(d): appendix(d, "app3", "04_도로계획도_도로계획표.png", "부록 3 · 도로계획도 + 도로계획표 (A3 원본)")
@slide("app4")
def _(d): appendix(d, "app4", "02_조감도_SiteAnchors.png", "부록 4 · 조감도 Site Anchors (A3 원본)")

if __name__ == "__main__":
    d = Deck()
    for k in ORDER: SL[k](d)
    d.save(OUTFILE)
    print("saved", OUTFILE, "slides", d.n)
    for w in WARN: print(w)
