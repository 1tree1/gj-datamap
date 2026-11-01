# -*- coding: utf-8 -*-
"""build_midterm — 중간마감 발표자료 v2. 5주차 덱(work/20261005_ppt_refine)의 pptkit 스타일을 그대로 쓰고,
5주차 현황분석 장(대상지·위치·보행·방문·주변 지역·이용자·성과 지표·상위계획·수치 근거·확인 사항·운영)과
새 분석(동서·남북·인구·청년·야간·업종·규제·유산·조직·노후 → 문제 6개 → 목표 3개 → 컨셉·프로그램·인구·규모)을 합친다.
색: 레드 + 흑백(5주차의 파랑을 빨강으로). 출력: ../output/구경주역_중간마감_v2.pptx"""
import os, sys, json
KIT = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_ppt_refine\scripts"
sys.path.insert(0, KIT)
import pptkit as K
from pptkit import *
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.util import Inches, Pt

R = r"C:\Users\OFFICE\Desktop\9_도시"
A5 = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_ppt_refine\assets"; CR = A5 + r"\crops"
HERE = os.path.dirname(os.path.abspath(__file__)); MA = HERE + r"\assets"
PH = R + r"\work\20261008_presentation_front\assets\photos"; AZ = R + r"\work\20261011_azimuth_white\azimuth_distribution_white.png"
OUT = os.path.join(HERE, "..", "output", "구경주역_중간마감_v2.pptx")
EV = json.load(open(R + r"\work\20261011_visual_front\build\evidence.json", encoding="utf-8"))

# ── 색: 레드 + 흑백 ─────────────────────────────────────────────────────────
ACC = "#C8102E"; DARK = "#8A0A1F"; LIGHT = "#E9909C"; PALE = "#F7D9DD"; G3 = "#9A9A9A"; G4 = "#5C5C5C"
ZN, ZC, ZS = DARK, ACC, LIGHT          # 북·중·남
def n(v): return format(int(round(v)), ",")

ORDER = ["cover", "toc", "hero", "summary", "principles",
         "div1", "now", "history", "location", "field", "barrier", "ewgap", "northsouth", "tourists", "neighbors", "popmap", "ageyouth", "migration", "nightbiz", "people3",
         "rules4", "heritage", "fabric", "oldbld", "metrics", "plans", "problems", "chain",
         "div2", "concept", "strategy", "strategy3", "linkage", "cases",
         "div3", "axes", "axes_basis", "roadsketch", "roadplan", "roadtable", "blocks",
         "div4", "matrix", "anchor1", "anchor2", "others", "zones", "axon_program", "section_strip", "programs",
         "div5", "pop", "visitors", "workres", "how", "landuse", "volume", "scale", "rules", "open", "ops",
         "before", "sources"]
PAGE = {k: i + 1 for i, k in enumerate(ORDER)}
SL = {}
def slide(key):
    def deco(fn): SL[key] = fn; return fn
    return deco
def std(d, key, label, title, sub=None):
    s = d.slide(); title_block(s, label, title, sub); page_no(s, PAGE[key]); return s

# ── 공통 부품(5주차 build_deck 과 동일, 색만 변경) ─────────────────────────────
def card(s, x, y, w, h, big, label, desc=None, color=ACC, fill=TINT, big_size=30, label_size=12):
    rect(s, x, y, w, h, fill=fill, radius=0.1)
    text(s, x + 0.2, y + 0.1, w - 0.4, 0.62, big, size=big_size, bold=True, color=color, tag="kpi")
    text(s, x + 0.2, y + 0.78, w - 0.4, 0.3, label, size=label_size, bold=True, tag="kpi-l")
    if desc: text(s, x + 0.2, y + 1.1, w - 0.4, h - 1.15, desc, size=10.5, color=INK2, tag="kpi-d")
def src(s, x, y, w, h, lines): text(s, x, y, w, h, lines, size=10.5, color=GRAY, tag="src")
def bar_rows(s, x, y, rows, label_w, bar_max, vmax, step=0.5, bar_h=0.3, color=ACC, fmt=lambda v: n(v), val_size=11, label_size=12, hl=None):
    for i, (lab, v) in enumerate(rows):
        yy = y + i * step
        text(s, x, yy, label_w, bar_h + 0.04, lab, size=label_size, anchor="m", tag="barlab")
        w = max(0.04, bar_max * abs(v) / vmax)
        rect(s, x + label_w, yy + 0.02, w, bar_h, fill=(hl or {}).get(i, color))
        text(s, x + label_w + w + 0.06, yy, 1.5, bar_h + 0.04, fmt(v), size=val_size, bold=True, anchor="m", tag="barval")
def divider(d, key, num, title, desc, col=ACC):
    s = d.slide(TINT)
    rect(s, 0, 0, 0.35, SH, fill=col)
    text(s, 1.2, 2.2, 3.0, 1.6, num, size=88, bold=True, color=col, tag="div-n")
    text(s, 1.2, 4.0, 11, 0.8, title, size=32, bold=True, tag="div-t")
    text(s, 1.2, 4.9, 11, 0.5, desc, size=14, color=INK2, tag="div-d")
    page_no(s, PAGE[key]); return s
def head(s, x, y, w, t, size=14): text(s, x, y, w, 0.32, t, size=size, bold=True, tag="head")
def note_box(s, x, y, w, h, title, body, line_c=ACC, fill="#FFFFFF", tsize=12, bsize=12):
    box_text(s, x, y, w, h, [dict(text=title, size=tsize, bold=True, color=RED, space_after=2), dict(text=body, size=bsize, line=1.2)], fill=fill, line=line_c, line_w=1.5, radius=0.1, anchor="m", margin=(0.25, 0.1, 0.25, 0.1), tag="note")
def _chart_font(ch, size=10):
    ch.font.name = EN; ch.font.size = Pt(size); ch.font.color.rgb = rgb(INK2)
def line_chart(s, x, y, w, h, cats, series, colors, ymin=None, ymax=None, unit=None, legend=True, fmt=None):
    cd = CategoryChartData(); cd.categories = cats
    for name, vals in series: cd.add_series(name, vals)
    gf = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(x), Inches(y), Inches(w), Inches(h), cd); ch = gf.chart
    _chart_font(ch, 10); ch.has_title = False; ch.has_legend = legend
    if legend: ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False; ch.legend.font.size = Pt(10)
    va = ch.value_axis; va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = rgb("#E6E6E6"); va.format.line.fill.background()
    if ymin is not None: va.minimum_scale = ymin
    if ymax is not None: va.maximum_scale = ymax
    if unit: va.major_unit = unit
    if fmt: va.tick_labels.number_format = fmt; va.tick_labels.number_format_is_linked = False
    ch.category_axis.format.line.color.rgb = rgb(LINE); ch.category_axis.tick_labels.font.size = Pt(10)
    for i, ser in enumerate(ch.plots[0].series):
        ser.format.line.color.rgb = rgb(colors[i]); ser.format.line.width = Pt(2.25); ser.smooth = False
        ser.marker.style = 8; ser.marker.size = 5; ser.marker.format.fill.solid(); ser.marker.format.fill.fore_color.rgb = rgb(colors[i]); ser.marker.format.line.color.rgb = rgb(colors[i])
    return ch
def col_chart(s, x, y, w, h, cats, series, colors, ymax=None, labels=True):
    cd = CategoryChartData(); cd.categories = cats
    for name, vals in series: cd.add_series(name, vals)
    gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd); ch = gf.chart
    _chart_font(ch, 10); ch.has_title = False; ch.has_legend = True; ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False; ch.legend.font.size = Pt(10)
    va = ch.value_axis; va.visible = False; va.has_major_gridlines = False
    if ymax: va.maximum_scale = ymax
    va.minimum_scale = 0
    ch.category_axis.format.line.color.rgb = rgb(LINE); ch.category_axis.tick_labels.font.size = Pt(10.5)
    pl = ch.plots[0]; pl.gap_width = 60; pl.overlap = -10
    if labels:
        pl.has_data_labels = True; dl = pl.data_labels; dl.number_format = "#,##0"; dl.number_format_is_linked = False; dl.font.size = Pt(9); dl.position = XL_LABEL_POSITION.OUTSIDE_END
    for i, ser in enumerate(pl.series): ser.format.fill.solid(); ser.format.fill.fore_color.rgb = rgb(colors[i])
    return ch
def donut(s, x, y, size, labels, vals, colors, hole=62):
    cd = CategoryChartData(); cd.categories = labels; cd.add_series("면적", vals)
    gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(x), Inches(y), Inches(size), Inches(size), cd); ch = gf.chart
    ch.has_legend = False; ch.has_title = False; pl = ch.plots[0]; pl.has_data_labels = False
    for i, col in enumerate(colors):
        pt = pl.series[0].points[i]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = rgb(col); pt.format.line.color.rgb = rgb("#FFFFFF"); pt.format.line.width = Pt(2)
    dn = ch._chartSpace.find(".//" + qn("c:doughnutChart")); hs = dn.find(qn("c:holeSize"))
    if hs is None: hs = etree.SubElement(dn, qn("c:holeSize"))
    hs.set("val", str(hole)); return ch

# ═════════════════════════════════ 표지·목차·개요 ═════════════════════════════════
@slide("cover")
def _(d):
    s = d.slide()
    picture(s, MA + r"\cover_outline.png", 6.5, 0, SW - 6.5, SH, mode="cover", align=(0.5, 0.5))
    rect(s, 0, 0, 6.5, 0.09, fill=RED)
    text(s, 0.7, 0.6, 5.6, 0.3, "중간마감 보고서 및 PT  ·  건축디자인6 STUDIO B  ·  2026.10.12", size=12, color=RED, bold=True)
    text(s, 0.7, 2.15, 5.7, 1.5, ["구 경주역", "도시재생 마스터플랜"], size=34, bold=True, line=1.08, tag="cover-t")
    text(s, 0.7, 3.85, 5.6, 0.9, ["폐철도 부지의 현황 분석과 재생 방향,", "프로그램·규모 계획"], size=16, color=INK2, tag="cover-s")
    rect(s, 0.75, 5.0, 1.2, 0.05, fill=RED)
    text(s, 0.7, 5.95, 5.6, 0.9, ["2019113133 이승규  ·  2021113994 김민승", "김아름 교수님"], size=12, color=INK2, tag="cover-n")
    photo_credit(s, 6.5, 0, SW - 6.5, SH, "정사영상 2025(국토지리정보원) · 붉은 선 = 본 계획 경계(최종)")

@slide("toc")
def _(d):
    s = std(d, "toc", "목차", "발표 구성")
    rows = [("", "개요", "계획 요약 · 계획 원칙", PAGE["hero"]),
            ("1", "현황과 분석", "대상지 · 위치 · 보행 단절 · 유동 격차 · 남북 관계 · 방문 · 주변 지역 · 인구 · 청년 · 야간·업종 · 규제·유산 · 조직 · 성과 지표 · 상위계획 · 문제 종합", PAGE["div1"]),
            ("2", "해결 컨셉", "컨셉 위계 · 전략의 공간 배치 · 전략 공간 다이어그램 · 관광–정주 성립 조건 · 선례", PAGE["div2"]),
            ("3", "도시축과 도로계획", "도시축 구상 · 기준축의 근거 · 도로망 구상 · 최종 도로계획도 · 도로계획표 · 가구와 획지", PAGE["div3"]),
            ("4", "프로그램", "선정 방법 · 앵커 ①② · 기타 프로그램 · 권역 · 배치 구상(축측) · 남북 단면 · 세부 프로그램", PAGE["div4"]),
            ("5", "계획 인구와 규모", "계획 인구 · 방문·근로·정주 산정 · 산정 방법 · 토지이용 · 건축 규모 · 산정표 · 규제 검토 · 확인 사항 · 운영", PAGE["div5"]),
            ("", "맺음말", "현황 · 자료 출처  (배치 구상안 · 단면 조닝 · 3D 볼륨은 별도 작성)", PAGE["before"])]
    for i, (num, ttl, desc, pg) in enumerate(rows):
        y = 1.55 + i * 0.78
        text(s, 0.75, y, 0.9, 0.55, num, size=26, bold=True, color=ACC, tag="toc-n")
        text(s, 1.85, y + 0.0, 6.5, 0.36, ttl, size=18, bold=True, tag="toc-t")
        text(s, 1.85, y + 0.36, 9.3, 0.36, desc, size=10.5, color=INK2, tag="toc-d")
        text(s, 11.3, y + 0.02, 1.4, 0.4, "%02d" % pg, size=18, bold=True, color=GRAY, align="r", tag="toc-p")
        line(s, 0.75, y + 0.72, 12.73, y + 0.72, LINE, 0.75)

@slide("hero")
def _(d):
    s = d.slide()
    picture(s, MA + r"\cover_outline.png", 0, 0, SW, SH, mode="cover", align=(0.5, 0.45))
    box_text(s, 0.6, 5.1, 9.2, 1.95, [dict(text="계획 개요", size=12, bold=True, color=RED, space_after=4), dict(text="NEXUS 1918 — 원도심을 다시 연결하는 생활거점", size=27, bold=True, space_after=3),
                                       dict(text="단절된 원도심을 다시 연결하고, 문화·유적 강점을 체류와 소득으로 이어 가되, 그 소득과 일자리가 주민(특히 청년)에게 남도록 일자리·주거·생활 기반을 함께 갖추는 재생을 방향으로 합니다.", size=12, color=INK, line=1.2),
                                       dict(text="1918 = 경주역 개업 연도 [T1] · 사진: 정사영상 2025와 본 계획 경계 228,025㎡", size=10.5, color=INK2, space_before=4)], fill="#FFFFFF", alpha=0.92, radius=0.1, anchor="m", margin=(0.3, 0.12, 0.3, 0.12), tag="hero")
    page_no(s, PAGE["hero"])

@slide("summary")
def _(d):
    s = std(d, "summary", "개요 : 요약", "계획 요약")
    items = [("01", "계획 배경", "구 경주역은 경주 원도심의 중심부, 황리단길·대릉원과 성동시장·황오동 사이에 위치합니다. 철도 이설 이후 남북으로 긴 공백지가 되었고, 동서 가로는 985m에 걸쳐 끊겨 있습니다."),
             ("02", "이용자 구성", "관광객 중심의 개발만으로는 원도심의 활력을 회복하기 어렵습니다. 방문객·근로자·거주자가 함께 이용하는 복합 거점을 계획하며, 방문 지표와 정주 지표를 함께 평가합니다."),
             ("03", "공간 구성", "남측은 방문객의 관문(역사문화예술), 중앙은 교류 거점(창작·체험·시장 접점), 북측은 근로·정주 거점(청년 업무·주거·공공청사)으로 구성하고, 활력을 성동시장과 행복황촌으로 확산시킵니다.")]
    for i, (num, ttl, body) in enumerate(items):
        x = 0.6 + i * 4.1
        rect(s, x, 1.65, 3.93, 3.1, fill=TINT, radius=0.1)
        text(s, x + 0.25, 1.78, 1.4, 0.65, num, size=28, bold=True, color=ACC, tag="sum-n")
        text(s, x + 0.25, 2.5, 3.45, 0.4, ttl, size=18, bold=True, tag="sum-t")
        text(s, x + 0.25, 3.05, 3.45, 1.6, body, size=12, color=INK, line=1.25, tag="sum-b")
    flow = [("유입", "남측 · CONNECT", ZS), ("교류", "중앙 · EXCHANGE", ZC), ("체류", "북측 · SPREAD", ZN), ("확산", "성동시장 · 행복황촌", GRAY)]
    for i, (verb, where, col) in enumerate(flow):
        x = 0.6 + i * 3.1
        box_text(s, x, 5.2, 2.65, 1.35, [dict(text=verb, size=22, bold=True, color="#FFFFFF" if col != ZS else INK, align="c"), dict(text=where, size=12, color="#FFFFFF" if col != ZS else INK, align="c")], fill=col, radius=0.12, anchor="m", tag="flow")
        if i < 3: arrow_right(s, x + 2.72, 5.7, 0.33, 0.35, GRAY)

@slide("principles")
def _(d):
    s = std(d, "principles", "개요 : 계획 원칙", "5대 계획 원칙과 세 전략")
    cols = [("1", "연결", "기존 가로망과의 접속, 동서·남북 보행축", "접속점 37곳에 정렬한 동서 횡단 가로 · 폐선 노반의 남북 보행축", ACC, "CONNECT"),
            ("2", "관문", "방문객의 첫 도착 공간 조성", "구 역사·철도기억관, 근대역사 전시관, 공연장, 방문자 관문", LIGHT, "EXCHANGE"),
            ("3", "근로", "주간 근로 인구의 확보", "청년창업·기업지원, 공유 오피스, 공공청사·의회", DARK, "SPREAD"),
            ("4", "정주", "야간 정주 인구의 확보", "청년·신혼 주거 600세대 (450~750, 가정) · 주민 공동시설", INK2, "SPREAD"),
            ("5", "확산", "주변 지역으로의 활력 파급", "성동시장 접점(쇼케이스·픽업 거점), 행복황촌 연결 안내", GRAY, "SPREAD")]
    for i, (num, verb, meaning, plan, col, strat) in enumerate(cols):
        x = 0.6 + i * 2.45; w = 2.3
        rect(s, x, 1.65, w, 5.2, fill=TINT, radius=0.1); rect(s, x, 1.65, w, 0.14, fill=col)
        oval(s, x + 0.2, 2.0, 0.55, col, num, size=16, color=INK if col == LIGHT else "#FFFFFF")
        text(s, x + 0.95, 2.1, w - 1.1, 0.35, strat, size=10.5, bold=True, color=col if col != LIGHT else ACC, tag="pr-s")
        text(s, x + 0.2, 2.75, w - 0.4, 0.5, verb, size=22, bold=True, tag="pr-v")
        text(s, x + 0.2, 3.35, w - 0.4, 1.2, meaning, size=12, line=1.2, tag="pr-m")
        line(s, x + 0.2, 4.6, x + w - 0.2, 4.6, LINE, 0.75)
        text(s, x + 0.2, 4.7, w - 0.4, 0.3, "계획 반영", size=10.5, color=GRAY, bold=True)
        text(s, x + 0.2, 5.02, w - 0.4, 1.7, plan, size=12, line=1.2, tag="pr-p")
    notes(s, "5대 원칙은 5주차 안을 유지하고 NEXUS 1918의 세 전략(CONNECT·EXCHANGE·SPREAD)에 대응시켰다. 관문은 EXCHANGE(교차·전환), 근로·정주·확산은 SPREAD에 속한다.")

# ═════════════════════════════════ 1 현황과 분석 ═════════════════════════════════
@slide("div1")
def _(d): divider(d, "div1", "1", "현황과 분석", "대상지 · 위치 · 보행 단절 · 유동 격차 · 남북 관계 · 방문 · 주변 지역 · 인구 · 청년 · 야간·업종 · 규제·유산 · 조직 · 성과 지표 · 상위계획 · 문제 종합")

@slide("now")
def _(d):
    s = std(d, "now", "현황과 분석 : 대상지", "철도 폐역 부지의 현황")
    picture(s, CR + r"\A_p64_aerial.png", 0.6, 1.55, 6.7, 3.75, mode="cover")
    picture(s, CR + r"\A_p105_photo3.png", 0.6, 5.4, 3.3, 1.55, mode="cover", align=(0.5, 0.45))
    picture(s, CR + r"\A_p105_photo2.png", 4.0, 5.4, 3.3, 1.55, mode="cover", align=(0.5, 0.55))
    facts = [("228,025㎡", "본 계획 경계 (남북 948m × 동서 311m)", "라이노 계획의 획지·도로·보도 합집합으로 측정한 최종 경계입니다. 철도 부지 148,770㎡[T1]와 인접 시가지 접속 구간을 포함합니다."),
             ("2021년 12월", "폐역 시점", "동해선 이설로 역 기능이 종료되었습니다. 국가철도공단·한국철도공사 등이 소유합니다(코레일 53.0% · 공단 46.9%, 2021 보고). [T1·T4]"),
             ("1918년", "경주역 개업 · 구 역사 1936년 이전", "구 역사(1,404㎡ × 2층)는 현재 사용되지 않으며 코레일 철도기념물(2013)이고 등록문화유산은 아닙니다. [T1]")]
    for i, (big, ttl, desc) in enumerate(facts):
        y = 1.55 + i * 1.8
        rect(s, 7.6, y, 5.13, 1.65, fill=TINT, radius=0.1)
        text(s, 7.8, y + 0.1, 4.8, 0.5, big, size=24, bold=True, color=ACC, tag="fact-b")
        text(s, 7.8, y + 0.66, 4.8, 0.3, ttl, size=12, bold=True, tag="fact-t")
        text(s, 7.8, y + 0.98, 4.8, 0.62, desc, size=10.5, color=INK2, line=1.15, tag="fact-d")
    photo_credit(s, 0.6, 1.55, 6.7, 3.75, "사진: 경주시 원도심 미래구상 기획연구(2025) · 전홍표")
    notes(s, "A_p64_aerial / A_p105_photo2·3 = 417쪽 연구 p.63, p.104 사진(전홍표 2025). 148,770㎡ = 전략계획 p.138 표. 228,025㎡ = 라이노 aardvark 슬롯 계획 프레임 합집합(2026-10-11). 소유 비율은 2021년 보고 기준이며 최신 등기자료 아님.")

@slide("history")
def _(d):
    s = std(d, "history", "현황과 분석 : 역사", "철도의 역사와 부지의 변화")
    ev = [("1918", "사정동 개업 [T1]"), ("1936", "성동동 현 위치 이전 [T1]"), ("1939", "노선 변경 [T3]"), ("2010", "KTX 신경주역 개통 [T1]"), ("2021", "구 경주역 폐역 [T1]")]
    for i, (y_, t) in enumerate(ev):
        x = 0.6 + i * 2.45
        text(s, x, 1.55, 2.3, 0.5, y_, size=24, bold=True, color=ACC, tag="hist-y"); line(s, x, 2.1, x + 2.25, 2.1, INK, 1.0)
        text(s, x, 2.15, 2.3, 0.35, t, size=11, tag="hist-t")
    for i, (f, t) in enumerate([("aerial_1954", "1954  철도 운영기 (근사 정합)"), ("aerial_2009", "2009  KTX 개통 전"), ("aerial_2025", "2025  폐역 이후")]):
        x = 0.6 + i * 4.1
        picture(s, MA + "\\%s.jpg" % f, x, 2.7, 3.93, 3.93, mode="cover"); text(s, x, 6.68, 3.93, 0.3, t, size=12, bold=True, tag="hist-c")
    notes(s, "1918.12.28 사정동 개업(관보). 1936.12.01 현 위치 이전. 1939.06 노선 변경(김신재 2013 pp.387–388). 2010.11.01 KTX 신경주역. 2021.12.28 폐역. 항공사진 국토지리정보원, 1954는 가로 교차점 기준 근사 정합.")

@slide("location")
def _(d):
    s = std(d, "location", "현황과 분석 : 위치", "원도심 내 위치와 주변 자산")
    picture(s, CR + r"\B_p393_aerial.png", 0.6, 1.5, 6.5, 3.28, mode="cover")
    picture(s, CR + r"\B_p300_assets_strip.png", 0.6, 4.9, 6.5, 2.18, mode="cover")
    photo_credit(s, 0.6, 1.5, 6.5, 3.28, "사진: 경주시 도시재생 전략계획(변경, 2022)")
    photo_credit(s, 0.6, 4.9, 6.5, 2.18, "사진: 경주시 도시재생 전략계획(변경, 2022) — 경주역전지구 주요 지역자산")
    head(s, 7.5, 1.5, 5.2, "구 역사 기준 주요 자산까지의 직선거리 [T2]")
    rows = [("황오동 고분", 345), ("성동시장", 355), ("경주읍성", 497), ("대릉원", 523), ("동궁과 월지", 920), ("황리단길", 994), ("첨성대", 1030)]
    bar_rows(s, 7.5, 1.95, rows, 1.35, 2.9, 1030, step=0.5, bar_h=0.3, fmt=lambda v: "%sm" % n(v), hl={0: ACC, 1: ACC, 2: LIGHT, 3: LIGHT, 4: LIGHT, 5: LIGHT, 6: LIGHT})
    xl = 7.5 + 1.35 + 2.9 * 400 / 1030
    line(s, xl, 1.9, xl, 5.45, INK2, 1.0, dash=True)
    text(s, xl - 0.9, 5.47, 1.8, 0.28, "보행 5분 (약 400m)", size=10.5, color=INK2, align="c", tag="loc-5")
    box_text(s, 7.5, 5.95, 5.23, 1.1, "남측에는 대릉원·황리단길·첨성대·동궁과 월지, 서측에는 성동시장과 원화로 상업가로, 동측에는 행복황촌의 저층 주거 골목, 북측에는 북천과 황성공원(약 509m)·성건동 생활권이 있습니다. 대상지는 이들을 잇는 거점입니다.", fill=TINT, radius=0.1, size=11, line_sp=1.15, tag="loc-b")
    notes(s, "거리: OSM 구 경주역 점 기준 직선(건물 중심 기준이면 6~16% 길어짐). 항공사진·지역자산 사진: 전략계획(변경, 2022) PDF p.383, p.290.")

@slide("field")
def _(d):
    s = std(d, "field", "현황과 분석 : 현장", "현장 답사 기록 (2026.09)")
    ph = [("ph57_site_tracks_south", "폐선로 남측 · 노반과 잔존 선로"), ("ph58_site_tracks_north", "폐선로 북측 · 수목이 덮은 노반"), ("ph56_site_overpass", "보행 육교 · 폭 3.2m, 유일한 횡단 시설"),
          ("ph63_site_fence_structure", "부지 경계 울타리 · 가로에서 차단"), ("ph00_west_wonhwaro_walk", "서측 원화로 · 상업가로"), ("ph62_east_lane_paved", "동측 행복황촌 골목 · 저층 주거")]
    for i, (f, t) in enumerate(ph):
        x = 0.6 + (i % 3) * 4.1; y = 1.55 + (i // 3) * 2.75
        picture(s, PH + "\\%s.jpg" % f, x, y, 3.93, 2.3, mode="cover"); text(s, x, y + 2.33, 3.93, 0.3, t, size=11, tag="field-c")
    notes(s, "현장 사진 2026.09. 육교 개방 여부와 울타리 개구부는 현장 재확인 필요.")

@slide("barrier")
def _(d):
    s = std(d, "barrier", "현황과 분석 : 보행", "동서 보행 단절 현황")
    picture(s, CR + r"\A_p106_walk_map.png", 0.6, 1.5, 5.4, 5.4, mode="contain")
    photo_credit(s, 0.6, 1.5, 5.4, 5.4, "지도: 경주시 원도심 미래구상 기획연구(2025)")
    card(s, 6.4, 1.55, 6.33, 1.5, "985m", "도로 횡단 부재 구간", "철도 부지를 따라 횡단 가능한 도로가 없습니다. 부지에 닿는 도로 끝은 37곳(서 9·동 18·남 7·북 3)입니다. [자체 분석, T2]", big_size=28)
    card(s, 6.4, 3.2, 3.05, 1.85, "1개", "보행 육교", "폭 3.2m, 길이 216m의 육교가 유일한 횡단 시설입니다. [T2]", big_size=28)
    card(s, 9.68, 3.2, 3.05, 1.85, "3.5배", "보행 우회율", "동서 이동 시 보행 경로가 직선거리 대비 중앙값 3.5배입니다. [T2]", big_size=28)
    box_text(s, 6.4, 5.25, 6.33, 1.55, "기존 연구도 같은 진단을 제시합니다. 철도 부지가 '경계공백지대'처럼 작동하여 보행 흐름을 단절하고 인접 지역의 쇠퇴를 초래한다고 봅니다. [원도심 미래구상 기획연구, 2025, T2] 2030 기본계획도 기존 시가지가 철도와 사적지구로 동서·남북 분리되어 있다고 진단합니다. [T1, 인쇄쪽 285]", fill="#FFFFFF", line=LINE, radius=0.1, size=11, line_sp=1.2, tag="bar-b")
    notes(s, "985m·우회율 3.5(폐선 양쪽 60m 지점, 육교 제외)·접속점 37곳은 이전 분석 경계(218,478㎡) 기준이며 최종 경계 재산정 전.")

@slide("ewgap")
def _(d):
    s = std(d, "ewgap", "현황과 분석 : 동서 격차", "동서 유동인구와 생활업종의 격차")
    picture(s, MA + r"\footfall_density.png", 0.6, 1.5, 6.2, 5.0, mode="contain", align=(0, 0))
    src(s, 0.6, 6.55, 6.2, 0.5, "원 면적 ∝ 명/ha · 소상공인365 2025.06–2026.06 월평균 · 통신 기반 추정 유동으로 보행량이 아니며 구역 면적이 다릅니다")
    card(s, 7.1, 1.55, 5.63, 1.55, "14.6배", "성동시장과 행복황촌의 유동 밀도 차이", "성동시장 반경 200m 1,175명/ha, 행복황촌 80명/ha, 폐역 구역 79명/ha입니다. [T2]", big_size=28)
    head(s, 7.1, 3.3, 5.6, "생활업종 비율 (11개 업종 표본, 2026.06) [T2]", 12)
    bar_rows(s, 7.1, 3.65, [("성동시장 (72/82개)", 87.8), ("행복황촌 (15/44개)", 34.1), ("황오동 원도심", 73.7)], 1.9, 2.6, 100, step=0.5, bar_h=0.3, fmt=lambda v: "%.1f%%" % v, hl={1: LIGHT, 2: LIGHT})
    box_text(s, 7.1, 5.3, 5.63, 1.5, "서측 시장 상권과 동측 체류·생활권은 역할이 다릅니다. 동서 연결은 각 역할을 유지한 채 이어지는 방식이어야 하며, 동측에서는 2021년부터 도시재생으로 숙소가 늘었으나 유동은 2019~2023년 수준(1,321명/일)입니다. [T2]", fill=TINT, radius=0.1, size=11, line_sp=1.2, tag="ew-b")

@slide("northsouth")
def _(d):
    s = std(d, "northsouth", "현황과 분석 : 남북 관계", "관광 집중과 북측 생활권")
    picture(s, MA + r"\northsouth_v.png", 0.6, 1.5, 4.6, 5.5, mode="contain", align=(0, 0))
    card(s, 5.5, 1.55, 3.5, 1.9, "757명/ha", "황리단길 반경 300m 일평균 유동", "21,403명/일이며 주말이 주중의 1.72배입니다. 시청(동천동) 500m는 0.88배입니다. [T2]", big_size=26)
    card(s, 9.23, 1.55, 3.5, 1.9, "29.6%", "관광객 불편 1위 교통혼잡·주차", "경주시 관광실태조사(n=3,009) [T2]. 주말 13시·21시에 중심 가로의 정체가 늘어납니다. [ITS, T2]", big_size=26)
    head(s, 5.5, 3.65, 7.2, "북측 공원·생활권")
    text(s, 5.5, 4.0, 7.2, 1.6, [dict(text="북천이 경계 북단에 접하고 황성공원은 북단에서 약 509m, 성건동 생활권이 북서측에 접합니다.", bullet=True, space_after=4),
                                 dict(text="전략계획은 선로로 단절된 도시공간을 잇는 매개공간을 제시하고 [T1, 인쇄쪽 161], 폐선축 동천~황성 2.5km의 도시숲을 응답자 65.3%가 선호했습니다. [T2]", bullet=True, space_after=4),
                                 dict(text="황성·용강·동천은 북측 신도시권으로 쇠퇴가 두드러지지 않으며, 북측 = 성건동으로 한정합니다.", bullet=True)], size=11, line=1.2, tag="ns-b")
    box_text(s, 5.5, 5.7, 7.23, 1.1, "관광은 남측에 집중되고 북측 공원·생활권과 이어지지 않습니다. 폐선 노반이 남북을 잇는 보행축이 됩니다.", fill="#FFFFFF", line=ACC, line_w=1.5, radius=0.1, size=13, bold=True, anchor="m", margin=(0.25, 0.1, 0.25, 0.1), tag="ns-n")

@slide("tourists")
def _(d):
    s = std(d, "tourists", "현황과 분석 : 방문", "방문객 규모와 체류 특성")
    kp = [("872만 명", "2025년 황리단길·대릉원 방문객", "경주시 보도 인용으로 원문 확인이 필요합니다. [T4]"),
          ("79%", "체류 시간 3시간 미만 방문객", "황오동 방문객 설문(2024, n=187) [T2]. 축제 현장 표본이라 일반화하지 않습니다."),
          ("2.7%", "10만 원 이상 소비한 방문객", "동일 설문 [T2]. 5만 원 미만이 75%입니다.")]
    for i, (big, ttl, sub) in enumerate(kp): card(s, 0.6 + i * 4.1, 1.55, 3.93, 2.1, big, ttl, sub, big_size=34)
    kp2 = [("55.3%", "내국인 숙박 방문 · 평균 1.8일", "경주시 제5차 관광실태조사(n=3,009) [T2]. 수도권 86.5%, 대경권 28.7%로 권역별 차이가 큽니다."),
           ("76.9%", "내국인 방문객의 자가용 이용", "KTX 경주역(건천읍)과 구 경주역(원도심)은 위치가 다릅니다. [T2]"),
           ("27명", "폐역 구역의 상시 거주 인구 (직장 117명)", "통신 추정 [T2]. 23–05시 유동 비중은 3.7%로 가장 낮습니다.")]
    for i, (big, ttl, sub) in enumerate(kp2): card(s, 0.6 + i * 4.1, 3.8, 3.93, 1.75, big, ttl, sub, big_size=24, color=INK)
    text(s, 0.6, 5.75, 12.1, 0.5, "과제는 방문객 수가 아니라 체류 시간의 확대입니다. 따라서 '유입 확대'보다 '체류 유도'를 목표로 계획합니다.", size=18, bold=True, tag="tour-1")
    box_text(s, 0.6, 6.35, 12.13, 0.6, "872만 명은 경주 전체(S3)의 방문 규모이며 대상지(S1)의 시설 규모 산정에는 사용하지 않습니다.", fill=TINT, radius=0.1, size=11, color=INK2, anchor="m", tag="tour-3")
    notes(s, "872만: 한국관광데이터랩 인용 보도(2026-01, T4). 79%·2.7%: 황오동 방문객 설문 2024(T2) — 2.7%는 '10만 원 이상'(이전 표기 '1만 원'은 오류). 관광실태조사 2024–25 내국인 3,009명.")

@slide("neighbors")
def _(d):
    s = std(d, "neighbors", "현황과 분석 : 주변 지역", "주변 지역 쇠퇴 현황과 시민 요구")
    head(s, 0.6, 1.5, 5.8, "황오동 쇠퇴 지표")
    kp = [("−32.7%", "최근 10년 인구 증감(2015→2025) [T2]"), ("−44%", "20~39세 인구 증감(2018→2025) [T2]"), ("43.8%", "65세 이상 인구 비율(2026.08) [T2]"), ("87.9%", "노후건축물 비율 · 법정 쇠퇴진단 3지표 충족 [T1]")]
    for i, (big, lab) in enumerate(kp):
        x = 0.6 + (i % 2) * 2.95; y = 1.9 + (i // 2) * 1.55
        rect(s, x, y, 2.8, 1.4, fill=TINT, radius=0.1)
        text(s, x + 0.15, y + 0.12, 2.5, 0.6, big, size=26, bold=True, color=ACC, tag="nb-b")
        text(s, x + 0.15, y + 0.85, 2.5, 0.5, lab, size=11, tag="nb-l")
    head(s, 6.9, 1.5, 5.8, "구 경주역 부지에 대한 시민 요구 (응답 58건) [T2]")
    rows = [("문화·쇼핑", 37), ("교통 거점", 16), ("지식·기술센터", 3), ("공공기관", 3), ("주거", 1)]
    bar_rows(s, 6.9, 2.0, rows, 1.55, 3.2, 37, step=0.56, bar_h=0.32, fmt=lambda v: "%d" % v, hl={4: INK})
    text(s, 6.9, 4.85, 5.8, 0.3, "응답자 55명(청년 27명, 중장년 28명) · 응답자 수가 작아 방향 참고용", size=10.5, color=INK2, tag="nb-n")
    note_box(s, 0.6, 5.2, 12.13, 1.5, "계획 대응", "시민이 요구한 문화·판매 기능과 교통 기능을 반영합니다. 시민 응답에는 없었으나 야간 활동 인구를 확보하기 위해 청년·신혼 주거를 추가하며, 이는 자체 판단입니다. 황오동·성건동은 법정 쇠퇴진단(인구·사업체·노후) 기준을 충족하여 혁신지구 공모 자격 요건에 해당합니다.", bsize=13)
    notes(s, "황오동 수치: KOSIS·황오동 모니터링 보고서(2025.09). 쇠퇴진단: 전략계획(2022) — 황오동 인구 −43.0%(5년 연속)·사업체 −2.7%(2년 연속)·노후 87.9%. 시민 응답: 원도심 미래구상 기획연구(2025) p.63~64.")

@slide("popmap")
def _(d):
    s = std(d, "popmap", "현황과 분석 : 인구", "인구 변화의 공간 분포")
    picture(s, MA + r"\pop_change.png", 0.6, 1.5, 6.3, 5.05, mode="contain", align=(0, 0))
    src(s, 0.6, 6.6, 6.3, 0.4, "KOSIS 주민등록인구 2015→2025 · 붉은 농도 = 감소율, 회색 = 증가 [T2]")
    head(s, 7.2, 1.5, 5.5, "인구 지수 (2015 = 100) [T2 KOSIS]")
    Y = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    def idx(nm):
        p = next(p for p in EV["population"] if p["hadm"] == nm); b = p["yearly"]["2015"]; return [round(p["yearly"][y] / b * 100, 1) for y in Y]
    city = [255301, 254667, 253480, 252329, 250956, 249175, 251889, 249607, 247489, 244769, 244055]
    line_chart(s, 7.2, 1.85, 5.5, 2.9, Y, [("황남동", idx("황남동")), ("황오동", idx("황오동")), ("성건동", idx("성건동")), ("월성동", idx("월성동")), ("경주시", [round(v / city[0] * 100, 1) for v in city])], [ACC, DARK, LIGHT, G4, G3], ymin=50, ymax=105, unit=10)
    kp = [("황남동", "−44.8%"), ("황오동", "−32.7%"), ("성건동", "−29.0%"), ("월성동", "−22.3%"), ("용강동", "+32.8%"), ("현곡면", "+33.3%")]
    for i, (lab, v) in enumerate(kp):
        x = 7.2 + (i % 3) * 1.85; y = 4.9 + (i // 3) * 0.75
        text(s, x, y, 1.8, 0.25, lab, size=10.5, color=INK2, tag="pm-l"); text(s, x, y + 0.22, 1.8, 0.45, v, size=18, bold=True, color=ACC if i < 4 else G4, tag="pm-v")
    box_text(s, 7.2, 6.4, 5.53, 0.65, "원도심 4개 동 인구는 10년간 33.0% 줄고 20~39세는 59.8% 줄었습니다. 감소는 폐역(2021.12) 이전부터 이어졌습니다.", fill=TINT, radius=0.1, size=11, bold=True, anchor="m", tag="pm-n")

@slide("ageyouth")
def _(d):
    s = std(d, "ageyouth", "현황과 분석 : 고령·청년", "고령화와 청년 인구의 분포")
    head(s, 0.6, 1.5, 4.0, "65세 이상 비율", 12); picture(s, MA + r"\pop_65.png", 0.6, 1.85, 4.1, 3.3, mode="contain", align=(0, 0))
    head(s, 4.9, 1.5, 4.0, "20~34세 비율 (붉을수록 낮음)", 12); picture(s, MA + r"\pop_y2034.png", 4.9, 1.85, 4.1, 3.3, mode="contain", align=(0, 0))
    head(s, 9.3, 1.5, 3.4, "65세 이상 비율 (%) [T2]", 12)
    bar_rows(s, 9.3, 1.9, [("황남동", 50.1), ("황오동", 43.8), ("월성동", 39.0), ("성건동", 36.7), ("경주시", 30.0)], 1.0, 1.7, 62, step=0.5, bar_h=0.3, fmt=lambda v: "%.1f" % v, hl={4: G3})
    kp = [("11.4%", "황오동 20~34세 비율 · 경주시 평균 12.9%"), ("44.5%", "황성·동천·용강·현곡의 20~34세 비중 (13,982 / 31,387명)"), ("−41.0%", "성건동 20~39세 절대 수 변화(2015→2025) · 외국인주민 3,481 → 7,170명")]
    for i, (big, lab) in enumerate(kp):
        x = 0.6 + i * 4.1; rect(s, x, 5.35, 3.93, 1.0, fill=TINT, radius=0.1)
        text(s, x + 0.15, 5.4, 1.5, 0.5, big, size=22, bold=True, color=ACC if i == 0 else INK, tag="ay-b"); text(s, x + 1.7, 5.42, 2.15, 0.9, lab, size=10.5, color=INK2, line=1.15, tag="ay-l")
    text(s, 0.6, 6.5, 12.1, 0.45, "원도심은 생활 편의·돌봄 수요가 크고, 청년은 북측 신도시권에 모여 있습니다. 주거·고용·생활 편의의 결합이 청년 정주의 조건입니다.", size=12, bold=True, tag="ay-n")
    notes(s, "행정안전부·KOSIS 주민등록 2026.08, 5세 구간 합. 성건동 청년 비율(23.7%)은 대학가 영향이라 비율 비교 대신 절대 수 변화를 쓴다.")

@slide("migration")
def _(d):
    s = std(d, "migration", "현황과 분석 : 청년 유출", "청년 순이동과 쇠퇴의 요인")
    head(s, 0.6, 1.5, 6.5, "연령별 연간 순이동 (명) [T2 KOSIS]")
    mg = EV["youth"]["net"]
    line_chart(s, 0.6, 1.85, 6.5, 3.2, EV["youth"]["mig_years"], [("20–24세", mg["20-24세"]), ("25–29세", mg["25-29세"]), ("30–34세", mg["30-34세"])], [ACC, DARK, LIGHT], ymin=-1100, ymax=200, unit=200)
    card(s, 0.6, 5.2, 3.15, 1.6, "−7,249명", "20~34세 순이동 누계 (2020–2025)", "62.7%가 20~24세에 집중됩니다. [T2]", big_size=24)
    card(s, 3.95, 5.2, 3.15, 1.6, "1,208명/년", "연평균 순유출 · 전출 사유 직업·교육", "2025년에는 −349명으로 둔화되었습니다. [T2]", big_size=24, color=INK)
    head(s, 7.5, 1.5, 5.2, "쇠퇴의 요인 (계획서 진단)")
    q = [("종합 쇠퇴원인 1번", "청년 경제활동과 주거안정을 위한 지역기반 부재 [T1, 도시재생 전략계획 인쇄쪽 150]"),
         ("외연 확장", "시청 이전·주거단지 확장·KTX 역세권 개발이 인구 유출과 중심권 약화의 한 요인(인구구조 변화·개발 규제와 함께) [T1, 인쇄쪽 15–16]"),
         ("순유출 사유", "20~34세 전출 사유는 직업·교육 [T2, 통계청 전입신고 사유]"),
         ("시의 방향", "주민의 힘으로 이끌어가는 삶터 · 관광객 중심에서 주민 거주 중심으로 [T1 전략계획 · T2 2026.08 지역재생지원센터]")]
    for i, (t, b) in enumerate(q):
        y = 1.9 + i * 1.0; rect(s, 7.5, y, 5.23, 0.9, fill=TINT, radius=0.08); rect(s, 7.5, y, 0.12, 0.9, fill=ACC if i == 0 else G3)
        text(s, 7.75, y + 0.06, 4.9, 0.3, t, size=12, bold=True, tag="mg-t"); text(s, 7.75, y + 0.36, 4.9, 0.55, b, size=10.5, color=INK2, line=1.15, tag="mg-b")
    box_text(s, 7.5, 5.95, 5.23, 0.85, "청년 정주 방안은 문화생활 증진만으로 충분하지 않으며 일자리와 주거 기반을 포함해야 합니다.", fill="#FFFFFF", line=ACC, line_w=1.5, radius=0.1, size=12, bold=True, anchor="m", margin=(0.2, 0.05, 0.2, 0.05), tag="mg-n")

@slide("nightbiz")
def _(d):
    s = std(d, "nightbiz", "현황과 분석 : 야간·업종", "야간 활동의 공백과 업종 치환의 징후")
    head(s, 0.6, 1.5, 5.5, "23–05시 추정 유동 비중 (%) [T2]")
    bar_rows(s, 0.6, 1.9, [("폐역 구역", 3.7), ("행복황촌", 4.4), ("성동시장", 5.0), ("황리단길", 5.5)], 1.3, 3.2, 7, step=0.5, bar_h=0.3, fmt=lambda v: "%.1f%%" % v, hl={1: LIGHT, 2: LIGHT, 3: LIGHT})
    text(s, 0.6, 4.0, 5.5, 0.5, "상시 거주·숙박 인구와 구분되는 야간 활동 지표이며 폐역 구역이 가장 낮습니다. 주거와 야간 기능이 없는 구역은 저녁 6시 이후 비게 됩니다.", size=10.5, color=INK2, line=1.15, tag="nb-1")
    head(s, 6.7, 1.5, 6.0, "황오동 점포형 업종군 순증감 (건, 2024 인허가) [T2]")
    rows = [("숙박·체류", 5), ("생활서비스·의료", 1), ("카페·휴게음식", 0), ("음식점·제과", -1), ("유흥·오락", -2), ("생활소매·식품제조", -9)]
    bar_rows(s, 6.7, 1.9, rows, 1.7, 3.0, 9, step=0.46, bar_h=0.28, fmt=lambda v: "%+d" % v if v else "0", hl={0: ACC, 1: LIGHT, 2: G3, 3: G3, 4: G3, 5: INK})
    card(s, 0.6, 4.7, 2.95, 1.6, "+7개", "행복황촌 관광·체류 업종 순증", "13개월(2025.06→2026.06) · 생활 업종 순증은 0입니다. [T2]", big_size=22)
    card(s, 3.7, 4.7, 2.95, 1.6, "2→21곳", "외국인관광도시민박업 증가", "2021→2025 · 시 발표, 정의 미확인 [T2]", big_size=22, color=INK)
    note_box(s, 6.7, 4.7, 6.03, 1.55, "관광 업종이 늘고 생활 업종이 주는 것은 회복이 아니라 치환입니다.", "동측에서는 숙소가 늘었으나 구역 유동은 2019~2023년 수준이며 생활 업종은 늘지 않았습니다. 본 계획의 성과지표는 방문 지표와 정주 지표를 항상 나란히 봅니다.", bsize=11)
    text(s, 0.6, 6.4, 12.1, 0.5, "출처: 소상공인365 2026.06 시간대별 추정 유동 · 황오동 모니터링 결과보고서(2024) pp.82–86 · 경주시 발표", size=10.5, color=GRAY, tag="src")

@slide("people3")
def _(d):
    s = std(d, "people3", "현황과 분석 : 이용자", "방문·근로·정주 인구의 시간대별 이용", "개념도: 통계가 아닌 계획 의도를 도식화한 것입니다. 점의 수는 해당 시간대의 이용 비중을 나타냅니다.")
    heads = ["평일 낮", "주말 낮", "저녁", "밤"]
    rows = [("방문 인구", ZS, [2, 3, 1, 0], "남측 관문 · 중앙 창작·체험·시장 접점"), ("근로 인구", ZN, [3, 0, 2, 0], "북측 공공청사 · 청년 업무권"), ("정주 인구", INK2, [1, 2, 3, 3], "북측 청년·신혼 주거 · 생활편의")]
    x0, y0 = 3.2, 1.9
    for j, h in enumerate(heads): text(s, x0 + j * 1.55, y0, 1.4, 0.35, h, size=12, bold=True, align="c", tag="p3-h")
    text(s, 9.55, y0, 3.2, 0.35, "계획 반영", size=12, bold=True, tag="p3-h2")
    for i, (lab, col, lv, where) in enumerate(rows):
        y = y0 + 0.55 + i * 1.35
        rect(s, 0.6, y, 12.13, 1.2, fill=TINT, radius=0.1)
        box_text(s, 0.75, y + 0.2, 2.2, 0.8, lab, fill=col, radius=0.1, size=14, bold=True, color=INK if col == ZS else "#FFFFFF", align="c", tag="p3-l")
        for j, k in enumerate(lv):
            for m in range(3):
                oval(s, x0 + j * 1.55 + 0.27 + m * 0.3, y + 0.45, 0.24, col if m < k else "#FFFFFF", line=col)
        text(s, 9.55, y + 0.3, 3.1, 0.6, where, size=12, tag="p3-w")
    text(s, 0.6, 6.4, 12.1, 0.5, "세 인구가 중첩되는 시간대가 길수록 가로의 활력이 지속됩니다.", size=14, bold=True, tag="p3-n")

@slide("rules4")
def _(d):
    s = std(d, "rules4", "현황과 분석 : 규제", "규제 4겹의 중첩 (최종 경계 228,025㎡ 기준)")
    pan = [("reg_landuse", "① 용도지역", "자연녹지 74.7% · 제2종일반주거 18.0% · 일반상업 7.3%", "경주시 도시관리계획 · V-World [T1]"),
           ("reg_godo", "② 고도지구", "도심 20m 지구 84.5% · 15m 지구 12.7% · 최저고도 3.7%", "경북 고시 제2020-479호 [T1]"),
           ("reg_heritage", "③ 역사문화환경 보존지역", "전역이 보존지역 · 삼층석탑 등 지정문화유산 주변 허용기준 적용", "문화유산법 · 경북 허용기준 [T1]"),
           ("reg_plan", "④ 지구단위계획 (본 계획 수립)", "본 계획이 경계·획지·용도·밀도·높이를 새로 정함 · 현 용도지역과의 정합은 용도지역 변경 전제", "본 계획 획지(라이노 최종)")]
    for i, (f, t, b, c) in enumerate(pan):
        x = 0.6 + i * 3.08
        text(s, x, 1.5, 2.95, 0.3, t, size=12, bold=True, tag="r4-t"); picture(s, MA + "\\%s.png" % f, x, 1.85, 2.95, 3.3, mode="contain", align=(0, 0))
        text(s, x, 5.2, 2.95, 0.8, b, size=10.5, line=1.2, tag="r4-b"); text(s, x, 6.0, 2.95, 0.3, c, size=10.5, color=GRAY, tag="r4-c")
    box_text(s, 0.6, 6.4, 12.13, 0.55, "+ 신라왕경 핵심유적 복원·정비 특별법 · 세계유산 완충구역 · 고도 보존 및 육성에 관한 특별법 — 규제 위반은 페널티가 아니라 건축 불가 조건으로 둡니다.", fill=TINT, radius=0.1, size=11, anchor="m", tag="r4-n")
    notes(s, "비율은 최종 경계 기준 2026-10-11 재산정(boundary_update.py). 고도지구 합 101%는 지구 중첩. ④는 기존 결정이 아니라 본 계획이 새로 수립하는 지구단위계획.")

@slide("heritage")
def _(d):
    s = std(d, "heritage", "현황과 분석 : 매장유산", "매장유산과 단계별 이용 조건")
    picture(s, MA + r"\heritage.png", 0.6, 1.5, 3.6, 5.45, mode="contain", align=(0, 0))
    picture(s, PH + r"\ph59_site_remnants_ne.jpg", 4.4, 1.5, 3.6, 2.5, mode="cover"); photo_credit(s, 4.4, 1.5, 3.6, 2.5, "철도 잔존 시설과 성토 노반(2026.09)")
    card(s, 8.3, 1.5, 4.43, 1.7, "145,879㎡", "시굴조사 필요 면적", "2022년 지표조사 범위 148,770㎡의 98.1%입니다. [T2, 김권일 2026]", big_size=26)
    head(s, 8.3, 3.4, 4.4, "1단계 설계 원칙")
    text(s, 8.3, 3.75, 4.43, 2.4, [dict(text="조사 전 지하 개발을 제외합니다. 주차는 지상 주차전용건축물로 둡니다.", bullet=True, space_after=4),
                                   dict(text="기초를 최소화하는 저층 분동과 되돌릴 수 있는 가로·광장·보행 정비를 1단계로 둡니다.", bullet=True, space_after=4),
                                   dict(text="시굴 결과와 유산 영향에 따라 배치·이용 단계를 다시 검토합니다.", bullet=True, space_after=4),
                                   dict(text="토양오염 가능성, 양산단층대(2016 경주지진 M5.8)는 층수·사업비 하한의 조건입니다.", bullet=True)], size=11, line=1.2, tag="hr-b")
    box_text(s, 4.4, 4.2, 3.6, 2.75, [dict(text="지하 0 · 성토 2m 미만 · 보호·전시 전용 부분은 건축면적·바닥면적 불산입 [T1]", size=10.5, color=INK2, space_after=6), dict(text="구 안동역 1단계의 지하주차 257면은 경주에 이식할 수 없습니다. 매장유산이 1단계 구성을 바꿉니다.", size=11, bold=True)], fill=TINT, radius=0.1, anchor="m", margin=(0.2, 0.1, 0.2, 0.1), tag="hr-n")
    notes(s, "김권일 학예연구실장 발표자료(2026) pp.8·22 · 구경주역 일원 시굴조사 계획 · 매장유산법.")

@slide("fabric")
def _(d):
    s = std(d, "fabric", "현황과 분석 : 도시조직", "접속 조건과 기존 도시조직")
    picture(s, MA + r"\anchors.png", 0.6, 1.5, 3.0, 3.7, mode="contain", align=(0, 0)); text(s, 0.6, 5.25, 3.0, 0.3, "도로 끝 접속점 37곳", size=11, bold=True, tag="fb-c")
    picture(s, MA + r"\street_orientation.png", 3.9, 1.5, 4.0, 3.7, mode="contain", align=(0, 0)); text(s, 3.9, 5.25, 4.0, 0.3, "가로 방위 분석 · 남북 격자와 북천 변 사선 격자", size=11, bold=True, tag="fb-c")
    picture(s, AZ, 8.2, 1.5, 4.5, 3.7, mode="contain", align=(0, 0)); text(s, 8.2, 5.25, 4.5, 0.3, "가로 방위 분포 (도로중심선 212km, 길이 가중)", size=11, bold=True, tag="fb-c")
    kp = [("37곳", "접속점(서 9 · 동 18 · 남 7 · 북 3)"), ("69.4%", "서측 인접 1층 건물 · 3층 이상 16.4%"), ("93.3%", "동측 인접 1층 건물 · 저층 골목"), ("약 150m", "현재 격자 규모 · 공통 방위 가로 57%")]
    for i, (big, lab) in enumerate(kp):
        x = 0.6 + i * 3.08; rect(s, x, 5.7, 2.95, 1.25, fill=TINT, radius=0.1)
        text(s, x + 0.15, 5.75, 2.7, 0.5, big, size=22, bold=True, color=ACC if i == 0 else INK, tag="fb-b"); text(s, x + 0.15, 6.3, 2.7, 0.6, lab, size=10.5, color=INK2, line=1.15, tag="fb-l")
    notes(s, "NGII 연속수치지도 · 기존 접속점 조사 · 도시조직 분석(2026.09). 1층 비율은 경계 인접 0–150m 건물. 가로 57%는 공통 방위(N0.8°E ±7.5°) 정렬 비율. 약 150m는 현재 격자(동서 147.5 / 남북 161.5m).")

@slide("oldbld")
def _(d):
    s = std(d, "oldbld", "현황과 분석 : 노후·쇠퇴", "건축물 노후도와 법정 쇠퇴진단")
    picture(s, MA + r"\age_buildings.png", 0.6, 1.5, 6.3, 4.6, mode="contain", align=(0, 0))
    head(s, 7.2, 1.5, 5.5, "건축물 경과연수 분포 (필지 수) [T2 건축물대장 × 연속지적]")
    bar_rows(s, 7.2, 1.9, [("10년 미만", 60), ("10–20년", 114), ("20–30년", 174), ("30–40년", 324), ("40년 이상", 1480)], 1.2, 3.0, 1480, step=0.46, bar_h=0.28, fmt=lambda v: n(v), hl={0: G3, 1: G3, 2: LIGHT, 3: LIGHT})
    card(s, 7.2, 4.3, 2.65, 1.35, "91.9%", "20년 이상 건물이 있는 필지", "1,978 / 2,152필지 [T2]", big_size=24)
    card(s, 10.08, 4.3, 2.65, 1.35, "83.8%", "30년 이상 건물이 있는 필지", "원자료 수집 범위 기준", big_size=24, color=INK)
    rows = [["행정동", "인구", "사업체", "노후", "판정"], ["황오동", "−43.0% (5년 연속)", "−2.7% (2년 연속)", "87.9%", {"text": "3지표 충족", "color": RED, "bold": True}], ["성건동", "−29.0% (5년 연속)", "+2.2% (1년 감소)", "72.4%", "2지표 충족"]]
    table(s, 7.2, 5.8, [0.85, 1.55, 1.5, 0.7, 0.93], rows, row_h=0.3, size=9.5, hdr_h=0.3, align=["l", "l", "l", "r", "c"], tag="old-t")
    text(s, 0.6, 6.25, 6.3, 0.7, "도시재생 혁신지구 공모 자격(쇠퇴 3지표 중 2개)을 대상지 주변 행정동이 충족합니다. [T1 전략계획 2022 쇠퇴진단]", size=12, bold=True, line=1.2, tag="old-n")

@slide("metrics")
def _(d):
    s = std(d, "metrics", "현황과 분석 : 성과 지표", "방문·정주 이중 성과 지표")
    box_text(s, 0.6, 1.65, 3.95, 3.2, [dict(text="방문 지표", size=20, bold=True, space_after=8), dict(text="방문객 수", size=13, bullet=True, space_after=4), dict(text="체류 시간 · 숙박 비율", size=13, bullet=True, space_after=4), dict(text="소비 금액", size=13, bullet=True)],
             fill=PALE, radius=0.1, anchor="m", margin=(0.4, 0.2, 0.3, 0.2), tag="m1")
    box_text(s, 4.69, 1.65, 3.95, 3.2, [dict(text="정주 지표", size=20, bold=True, space_after=8), dict(text="25~39세 거주 인구", size=13, bullet=True, space_after=4), dict(text="생활 업종 비율(식료품·세탁·의원 등)", size=13, bullet=True, space_after=4), dict(text="야간 활동(18시 이후 · 23–05시)", size=13, bullet=True)],
             fill="#E6E6E6", radius=0.1, anchor="m", margin=(0.4, 0.2, 0.3, 0.2), tag="m2")
    box_text(s, 8.78, 1.65, 3.95, 3.2, [dict(text="소득 환류 지표", size=20, bold=True, color="#FFFFFF", space_after=8), dict(text="지역 사업체 매출 비중", size=13, color="#FFFFFF", bullet=True, space_after=4), dict(text="청년 정규 일자리 수", size=13, color="#FFFFFF", bullet=True, space_after=4), dict(text="임대료 · 도시민박 등록 수", size=13, color="#FFFFFF", bullet=True)],
             fill=ACC, radius=0.1, anchor="m", margin=(0.4, 0.2, 0.3, 0.2), tag="m3")
    text(s, 0.6, 5.1, 12.1, 0.5, "세 지표를 항상 병기하여 평가합니다.", size=20, bold=True, tag="m-3")
    text(s, 0.6, 5.7, 12.1, 1.1, ["관광 업종은 증가하고 생활 업종이 감소하는 경우, 회복이 아니라 업종의 치환으로 판단합니다. (사례: 전주)", "보조 지표로 인접 건물 주 출입구의 대상지 방향 전환 여부를 항공사진·로드뷰 시계열로 확인합니다. (사례: 광주 푸른길)", "관광 소득이 주민에게 남아 정주로 이어지는가는 조건부 가설이므로 환류 지표를 따로 둡니다."], size=12, color=INK2, line=1.2, tag="m-4")
    notes(s, "성과지표 두 축: CLAUDE.md §5 교훈 6·7. 환류 축: 20261010 방향 근거 정리 §2.4.")

@slide("plans")
def _(d):
    s = std(d, "plans", "현황과 분석 : 상위계획", "상위계획 검토")
    picture(s, CR + r"\B_p148_table.png", 0.6, 1.55, 5.5, 1.86, mode="contain", align=(0, 0), border=LINE)
    text(s, 0.6, 3.55, 5.5, 0.3, "경주시 도시재생 전략계획(변경, 2022) [T1]", size=10.5, color=GRAY, tag="pl-cap")
    text(s, 0.6, 3.95, 5.5, 3.0, [dict(text="'경주역부지 개발'이 상위계획에 반영되어 있습니다.", size=14, bold=True, space_after=6),
                                  dict(text="면적 148,770㎡, 2019~2028년", bullet=True, space_after=4), dict(text="공공청사·상징광장·문화·복합상업·커뮤니티시설", bullet=True, space_after=4),
                                  dict(text="복합환승센터를 경주역에 설치(2030 도시기본계획)", bullet=True, space_after=4), dict(text="폐선로 공공공간 조성 및 신교통 도입 검토", bullet=True, space_after=4),
                                  dict(text="경주시 구상(2026.02): K-헤리티지 복합거점 · 미래모빌리티 통합허브 · 경주 STAY, 사업비 3,822억(국비 250억) [T2·T4]", bullet=True)], size=12, line=1.15, tag="pl-b")
    rows = [["상위계획 내용", "본 계획 반영"],
            ["공공청사", "공공청사·의회 (권역 A, 시 구상 2단계)"], ["상징광장 · 문화·공원시설", "구 역사 전면 문화광장 · 근대역사 전시관 · 공연장 (권역 E)"], ["복합상업시설 · 커뮤니티시설", "시장 접점(쇼케이스·공예품 판매) · 주민 커뮤니티홀·작은도서관 (권역 D·B)"],
            ["복합환승센터(경주역)", "주차전용건축물 · 방문자 관문 · 모빌리티 대합실(선택 제안)"], ["청년창업 · 산업 콘텐츠", "청년 창업 입주사무실·공유 오피스 (권역 C) · 창작 레지던시 (권역 D)"], ["폐선로의 공공공간, 도시 숲", "철도 흔적 보행길 · 생활공원 · 북천 방면 남북 보행축"],
            [{"text": "주거 (상위계획에 없음)", "color": RED, "bold": True}, {"text": "청년·신혼 주거 600세대: 본 계획이 추가하는 용도 (용도지역 변경 전제)", "color": RED, "bold": True}]]
    table(s, 6.35, 1.55, [2.7, 3.68], rows, row_h=0.62, size=11, hdr_h=0.4, tag="plans-t")
    notes(s, "전략계획 PDF p.122(복합환승센터), p.148(경주역부지 개발), p.186, p.392~393. 본 계획은 기존 지구단위계획 결정과 무관하게 수립한다(사용자 지시 2026-10-11).")

@slide("problems")
def _(d):
    s = std(d, "problems", "현황과 분석 : 문제 종합", "문제 종합 : 여섯 과제")
    cards = [("①", "동서 단절", "crossing_map", "985m 무횡단 · 육교 1 · 우회율 3.5 · 유동 밀도 14.6배 격차 · 접속점 37곳"), ("②", "남북 불균형", "northsouth_v", "황리단길 757명/ha · 주말 1.72배 · 북측 공원·생활권과 미연계"),
             ("③", "원도심 쇠퇴와 청년 유출", "pop_change", "4개 동 −33.0% · 20~34세 −7,249명 · 쇠퇴원인 1번 일자리·주거 기반 부재"), ("④", "짧은 체류와 차량 중심 방문", "arrival", "현장 체류 1~3시간 79.1% · 자가용 76.9% · 불편 1위 교통혼잡·주차 29.6%"),
             ("⑤", "정주 공백과 치환 위험", "footfall_density", "상시 거주 27명 · 야간 유동 3.7% · 관광·체류 +7 · 생활 0 · 생활소매 −9"), ("⑥", "유산·규제 제약", "reg_heritage", "시굴 대상 98.1% · 20m 지구 84.5% · 1단계 지하 개발 불가 · 4겹 규제")]
    for i, (num, ttl, f, body) in enumerate(cards):
        x = 0.6 + (i % 3) * 4.1; y = 1.55 + (i // 3) * 2.7
        rect(s, x, y, 3.93, 2.5, fill=TINT, radius=0.1); picture(s, MA + "\\%s.png" % f, x + 0.15, y + 0.15, 1.5, 2.2, mode="cover")
        text(s, x + 1.8, y + 0.15, 0.5, 0.5, num, size=20, bold=True, color=ACC, tag="pb-n"); text(s, x + 2.25, y + 0.2, 1.6, 0.65, ttl, size=12.5, bold=True, line=1.1, tag="pb-t")
        text(s, x + 1.8, y + 0.95, 2.0, 1.5, body, size=10.5, line=1.25, tag="pb-b")

@slide("chain")
def _(d):
    s = std(d, "chain", "현황과 분석 : 목표", "문제의 연쇄와 계획 목표")
    rowsC = [["철도 장벽 (1936~)", "경계공백지대", "동서 활력 격차 ①②", "목표 ①  연결"], ["남측 관광 집중", "짧은 체류 · 차량 도착 ④", "생활 업종 치환 ⑤", "목표 ②  문화·유적과 체류"], ["외연 확장 · 시청 이전", "원도심 인구·청년 유출 ③", "주거·야간 공백 ⑤⑥", "목표 ③  주민 생활과 청년 정주"]]
    for i, r in enumerate(rowsC):
        y = 1.6 + i * 1.15
        for j, c in enumerate(r):
            x = 0.6 + j * 2.2; goal = j == 3
            box_text(s, x, y, 2.6 if goal else 1.9, 0.8, c, fill=ACC if goal else TINT, radius=0.08, size=12 if goal else 11, bold=goal, color="#FFFFFF" if goal else INK, align="c", anchor="m", margin=(0.08, 0.04, 0.08, 0.04), tag="ch")
            if j < 3: arrow_right(s, x + 1.93, y + 0.25, 0.24, 0.3, G3)
    head(s, 0.6, 5.15, 8.5, "성과지표 (세 축을 나란히 보고)")
    ax = [("방문 축", "체류시간 · 숙박 비율 · 소비"), ("정주 축", "25~39세 거주 인구 · 생활업종 비율 · 야간 활동"), ("환류 축", "지역 사업체 매출 비중 · 청년 정규 일자리 · 임대료 · 도시민박 등록 수")]
    for i, (a, b) in enumerate(ax):
        x = 0.6 + i * 2.95; text(s, x, 5.5, 2.8, 0.3, a, size=12, bold=True, color=ACC if i == 2 else INK, tag="ax"); text(s, x, 5.8, 2.85, 0.9, b, size=10.5, color=INK2, line=1.2, tag="ax-b")
    box_text(s, 9.6, 1.6, 3.13, 5.2, [dict(text="설계 조건", size=12, bold=True, color=RED, space_after=6),
                                     dict(text="되돌릴 수 있는 순서로 투자합니다. 1단계는 가로·광장·보행 정비입니다.", bullet=True, space_after=5), dict(text="관광 수익이 주민에게 환류되도록 소유·운영 구조를 설계합니다.", bullet=True, space_after=5),
                                     dict(text="연결은 횡단 개소 수가 아니라 연속성과 최약 지점의 통과 폭으로 측정합니다.", bullet=True, space_after=5), dict(text="성공 지표는 경계 인접 필지의 주 출입구 방향이 부지 쪽으로 바뀌는가입니다(광주 푸른길).", bullet=True)], fill=TINT, radius=0.1, size=10.5, line_sp=1.2, anchor="t", margin=(0.25, 0.2, 0.2, 0.2), tag="ch-n")

# ═════════════════════════════════ 2 해결 컨셉과 프로그램 ═════════════════════════════════
@slide("div2")
def _(d): divider(d, "div2", "2", "해결 컨셉", "컨셉 위계 · 전략의 공간 배치 · 관광–정주 성립 조건 · 선례", DARK)

@slide("concept")
def _(d):
    s = std(d, "concept", "해결 컨셉 : 위계", "컨셉의 위계")
    lv = [("프로젝트", "NEXUS 1918", "멈춘 역, 경주를 다시 연결하는 중심 · 1918 = 경주역 개업 연도 [T1]", ACC), ("설계 컨셉", "CULTURAL INTERCHANGE", "도시의 흐름을 바꾸는 문화환승 · 방문 동선과 주민 생활이 교차하는 환승점", INK),
          ("전략", "CONNECT  ·  EXCHANGE  ·  SPREAD", "접속(동서·남북 연결)  ·  교차·전환(관광과 일상, 문화·창작의 접점)  ·  확산(성동시장·원도심으로 활동 확산, 일자리·주거)", INK2),
          ("건축 표현", "ELEVATED CULTURAL PLATFORM", "저층 1~3층 분동 문화시설 + 중앙 오픈스페이스 + 공중광장·상층 녹지산책로 · 매장유산 조건에 맞는 지상 구성", GRAY)]
    for i, (lab, big, desc, col) in enumerate(lv):
        y = 1.6 + i * 1.0
        box_text(s, 0.6, y, 1.5, 0.85, lab, fill=col, radius=0.08, size=11, bold=True, color="#FFFFFF", align="c", anchor="m", tag="cv-l")
        text(s, 2.3, y + 0.05, 10.4, 0.42, big, size=18, bold=True, color=ACC if i == 0 else INK, tag="cv-b"); text(s, 2.3, y + 0.47, 10.4, 0.38, desc, size=10.5, color=INK2, tag="cv-d")
        if i < 3: line(s, 1.35, y + 0.85, 1.35, y + 1.0, INK, 1.0, arrow=True)
    line(s, 0.6, 5.65, 12.73, 5.65, LINE, 0.75)
    mp = [("목표 ①  연결", "CONNECT", "문제 ①②"), ("목표 ②  문화·유적과 체류", "EXCHANGE", "문제 ②④"), ("목표 ③  주민 생활과 청년 정주", "SPREAD", "문제 ③⑤")]
    for i, (a, b, c) in enumerate(mp):
        x = 0.6 + i * 4.1; text(s, x, 5.78, 2.4, 0.3, a, size=11, bold=True, tag="cv-m"); text(s, x + 2.4, 5.78, 1.0, 0.3, b, size=11, bold=True, color=ACC, tag="cv-m2"); text(s, x + 3.35, 5.78, 0.75, 0.3, c, size=10.5, color=INK2, tag="cv-m3")
    box_text(s, 0.6, 6.2, 12.13, 0.75, "단절된 원도심을 다시 연결하고, 문화·유적 강점을 체류와 소득으로 이어 가되, 그 소득과 일자리가 주민(특히 청년)에게 남도록 일자리·주거·생활 기반을 함께 갖추는 지속가능한 재생을 방향으로 합니다.", fill=TINT, radius=0.1, size=11.5, bold=True, anchor="m", tag="cv-n")

@slide("strategy")
def _(d):
    s = std(d, "strategy", "해결 컨셉 : 전략", "전략의 공간 배치")
    picture(s, MA + r"\strategy_map.png", 0.6, 1.5, 6.3, 5.45, mode="contain", align=(0, 0))
    strat = [("CONNECT", "접속", ["동서 횡단 가로를 여러 곳에 두어 횡단 간격을 줄이고 최약 지점의 통과 폭을 확보합니다.", "폐선 노반을 대릉원 ↔ 북천·황성공원을 잇는 남북 보행축으로 씁니다.", "접속점 37곳과 기존 가로의 폭·방향에 새 가로를 정렬합니다."]),
             ("EXCHANGE", "교차·전환", ["중앙에 구 역사·문화광장·창작 스튜디오·체험관·시장 접점을 모아 방문객과 주민이 만나는 자리를 만듭니다.", "방문 지출이 상인·공예인·예술인의 소득으로 이어지는 접점 장치입니다."]),
             ("SPREAD", "확산", ["북측에 청년 업무·청년주거·공공청사를 두어 저녁 이후에도 사람이 남게 합니다.", "활동을 성동시장과 행복황촌으로 내보내는 방향으로 동선과 안내를 설계합니다."])]
    for i, (a, b, items) in enumerate(strat):
        y = 1.55 + i * 1.8
        text(s, 7.2, y, 2.0, 0.35, a, size=16, bold=True, color=ACC if i < 2 else INK, tag="st-a"); text(s, 9.2, y + 0.07, 1.5, 0.3, b, size=11, color=INK2, tag="st-b")
        text(s, 7.2, y + 0.4, 5.5, 1.35, [dict(text=t, bullet=True, space_after=2) for t in items], size=10.5, line=1.2, tag="st-i")
    src(s, 0.6, 6.95, 6.3, 0.3, "전략 배치도: 최종 계획 경계(붉은 면) · NGII 도로·UPIS 공원·OSM 폐선")

@slide("strategy3")
def _(d):
    s = std(d, "strategy3", "해결 컨셉 : 전략의 공간 표현", "세 전략의 공간 다이어그램")
    items = [("connect", "CONNECT  접속", "동서 선형공원 40m · 화랑로 연결 · 남북 보행축 30m로 끊긴 도시조직을 잇습니다", [("5곳", "동서 횡단 · 간격 약 150m (현재 985m 무횡단)"), ("948m", "남북 보행축 · 대릉원 ↔ 북천")]),
             ("exchange", "EXCHANGE  교차·전환", "구 역사·광장·창작·체험·시장 접점이 모인 중앙에서 방문객과 주민이 만납니다", [("15,791㎡", "창작·체험(D) 6,225 + 역사문화예술(E) 9,566 (기준안)"), ("11,067명/일", "방문 유동(기준) · 피크 1시간 1,147명")]),
             ("spread", "SPREAD  확산", "북측 청사·업무·주거가 저녁 이후 사람을 남기고 활동을 성동시장·행복황촌으로 내보냅니다", [("798명", "정주 인구 · 청년·신혼 600세대"), ("906명", "청년 일자리 + 공공청사 약 900명")])]
    for i, (k, t, b, kp) in enumerate(items):
        x = 0.6 + i * 4.1
        picture(s, MA + "\diag_strategy_" + k + ".png", x, 1.45, 3.93, 2.3, mode="contain", align=(0.5, 0))
        rect(s, x, 3.85, 3.93, 1.0, fill=TINT, radius=0.08)
        text(s, x + 0.15, 3.9, 3.65, 0.3, t, size=12, bold=True, color=ACC if i < 2 else INK, tag="s3-t"); text(s, x + 0.15, 4.2, 3.65, 0.62, b, size=10, color=INK2, line=1.15, tag="s3-b")
        for j, (big, lab) in enumerate(kp):
            y = 5.05 + j * 0.95
            text(s, x + 0.15, y, 3.65, 0.5, big, size=24, bold=True, color=ACC if i < 2 else INK, tag="s3-k"); text(s, x + 0.15, y + 0.5, 3.65, 0.4, lab, size=9.5, color=INK2, line=1.15, tag="s3-l")
    notes(s, "라이노 _DIAG 임시 레이어(프로그램 매스·도로·보도·맥락 건물 4,457동)를 남서 상공 평행투영으로 캡처(build/rhino_diagram_build.py · rhino_diagram_capture.py)하고 build/compose_diagrams.py로 화살표·라벨을 얹었다. 매스 높이는 프로그램별 가정. 횡단 5곳은 최종 도로계획의 가구 사이 동서 띠(y 1,761,434–459 / 576–616 / 735–743 / 867–890 / 974–984).")

@slide("linkage")
def _(d):
    s = std(d, "linkage", "해결 컨셉 : 가설", "관광과 정주 연계의 성립 조건")
    chain = [("A", "관광 확대 → 지역 소득·일자리", "찬성 [T3]", "유럽 179개 지역에서 관광이 1인당 GDP 성장에 양(+) · 경주 사적지 1개소당 생산유발 148억 원"),
             ("B", "소득이 주민에게 남는가", "조건부 [T3]", "지역 소유 소기업 밀도가 소득 성장에 양(+), 비지역 대기업은 음(−) · 잔류 지출은 체류일수만이 예측"),
             ("C", "주민 소득·일자리 → 정주 인구", "직접 검증 없음 [T3·T2]", "체류인구는 늘어도 정주 순유입은 늘지 않은 평가 3건 · 황남동(관광 중심) 인구 −44.8%")]
    for i, (a, b, c, dsc) in enumerate(chain):
        x = 0.6 + i * 4.1; rect(s, x, 1.55, 3.93, 1.8, fill=TINT, radius=0.1)
        text(s, x + 0.15, 1.6, 0.6, 0.5, a, size=22, bold=True, color=ACC, tag="lk-a"); text(s, x + 0.75, 1.65, 3.0, 0.5, b, size=11, bold=True, line=1.15, tag="lk-b")
        text(s, x + 0.15, 2.15, 3.6, 0.3, c, size=10.5, bold=True, color=INK if i == 0 else RED, tag="lk-c"); text(s, x + 0.15, 2.45, 3.6, 0.85, dsc, size=10, color=INK2, line=1.2, tag="lk-d")
        if i < 2: arrow_right(s, x + 3.95, 2.3, 0.15, 0.3, INK)
    head(s, 0.6, 3.55, 6, "성립 조건 5개 (설계 요구사항)")
    cond = [("01", "소득의 지역 잔류", "성동시장 클러스터 임대료 하향 · 상인회·협동조합 공동 운영"), ("02", "일자리의 질", "관광 밖 일자리(청년 창업·기업지원·공공청사)를 함께 둡니다"), ("03", "주거 공급과 관광 수요의 비경합", "도시민박 등록 수·월세를 감시 지표로 둡니다"),
            ("04", "관광 구역과 생활권의 완충", "남측 방문 관문과 북측 근로·정주를 분리·완충합니다"), ("05", "규모의 한계", "목표는 관광 규모가 아니라 체류·소득 환류·정주입니다")]
    for i, (a, b, c) in enumerate(cond):
        y = 3.95 + i * 0.58; text(s, 0.6, y, 0.6, 0.4, a, size=14, bold=True, color=ACC, tag="cd-a"); text(s, 1.2, y + 0.04, 3.7, 0.35, b, size=11.5, bold=True, tag="cd-b"); text(s, 5.0, y + 0.06, 7.7, 0.35, c, size=10.5, color=INK2, tag="cd-c")
    src(s, 0.6, 6.9, 12.1, 0.3, "문헌 종합(20261010_final_direction_evidence_v1 §2.4) · KCI·Crossref·OpenAlex 검색 · 개별 논문의 결론이 아닌 종합 해석")

@slide("cases")
def _(d):
    s = std(d, "cases", "해결 컨셉 : 선례", "선례에서 빌리는 것")
    cs = [("구 안동역", "1단계 = 연결도로 220m · 지하주차 257면 · 산책로 790m", "어떤 프로그램에도 필요하고 되돌릴 필요가 없는 연결·기반·보행을 먼저 합니다. 지하주차만 경주에 이식할 수 없습니다."),
          ("교토 우메코지", "공원 1995 → 수족관 2012 → 철도박물관 2016 → 전용역 2019", "비가역 투자는 뒤로 둡니다. 민간자본은 공원 개원 13년 후에 들어왔습니다. 빌릴 것은 기간이 아니라 순서입니다."),
          ("광주 푸른길", "(사)푸른길이 운영 · 레일을 등지던 건물들이 푸른길 쪽으로 출입문을 냄", "조성 조직이 아니라 운영 조직을 설계합니다. 성공 지표는 인접 건물의 출입구 방향 전환입니다."),
          ("부산 혁신도시", "93.5만㎡를 4개로 쪼개 기존 도심에 삽입 · 정주만족 1위 61.6%", "단일 대형이 아니라 분산 삽입을 대안 시나리오로 함께 냅니다.")]
    for i, (a, b, c) in enumerate(cs):
        x = 0.6 + (i % 2) * 6.25; y = 1.55 + (i // 2) * 2.45
        rect(s, x, y, 6.05, 2.25, fill=TINT, radius=0.1); text(s, x + 0.2, y + 0.15, 5.6, 0.35, a, size=14, bold=True, color=ACC, tag="cs-a")
        text(s, x + 0.2, y + 0.55, 5.6, 0.5, b, size=10.5, color=INK2, line=1.2, tag="cs-b"); text(s, x + 0.2, y + 1.1, 5.6, 1.05, c, size=11, line=1.3, tag="cs-c")
    box_text(s, 0.6, 6.45, 12.13, 0.5, "회피 사례  울산 우정혁신도시(단일 대형, 도심 속 외딴 섬) · 트렌토 Le Albere · 발렌시아 예술과학도시 · 전주 한옥마을(관광 치환) — 검토했음을 심의에서 증명합니다.", fill=INK, radius=0.08, size=10.5, color="#FFFFFF", anchor="m", tag="cs-n")
    src(s, 0.6, 7.0, 12.1, 0.3, "docs/20_cases 사례 데이터베이스 · 원문 교차검증 전 [T3·T4]")

# ═════════════════════════════════ 3 도시축과 도로계획 ═════════════════════════════════
@slide("div3")
def _(d): divider(d, "div3", "3", "도시축과 도로계획", "도시축 구상 · 기준축의 근거 · 도로망 구상 · 최종 도로계획도 · 도로계획표 · 도로가 나눈 가구와 획지", ACC)

@slide("axes")
def _(d):
    s = std(d, "axes", "도시축과 도로계획 : 도시축 구상", "계획 경계와 세 기준축, 두 연결")
    picture(s, MA + r"\sketch_axes.jpg", 0.6, 1.5, 3.75, 5.45, mode="cover", align=(0.5, 0.5))
    photo_credit(s, 0.6, 1.5, 3.75, 5.45, "수작업 구상도 · 기존 도시조직 지도 위 · 북쪽 위")
    picture(s, MA + r"\axes_map.png", 4.5, 1.5, 4.3, 5.45, mode="contain", align=(0, 0))
    items = [("검은 굵은 선", "계획 경계", "라이노 최종 경계 228,025㎡를 옮긴 계획 범위. 경계 안 건물의 전면 철거를 뜻하지 않습니다.", INK),
             ("빨간 선 ①", "남북축 (대지축)", "폐선 노반을 따르는 부지의 긴 축. 남북 도시구조와 보행축의 기준입니다.", ACC),
             ("빨간 선 ②", "동서축 (성동시장 ↔ 전랑지)", "부지를 가로질러 서측 시장과 동측 생활권을 잇는 축. 폭 40m 선형공원으로 구상.", ACC),
             ("빨간 선 ③", "역사유적축 (황리단길)", "직교 격자와 다른 방향의 사선축. 대릉원·황리단길 방면 방문 동선의 기준.", ACC),
             ("파란 띠", "화랑로 연결", "기존 화랑로를 부지 안으로 이어 동서 차량 통행을 회복하는 연결 구간.", "#1F5AA6"),
             ("파란 원", "경주읍성 향일문", "서측 읍성 향일문 방향의 조망·보행 연결 거점.", "#1F5AA6")]
    for i, (sym, ttl, desc, col) in enumerate(items):
        y = 1.5 + i * 0.92
        rect(s, 9.05, y, 3.68, 0.84, fill=TINT, radius=0.08); rect(s, 9.05, y, 0.1, 0.84, fill=col)
        text(s, 9.28, y + 0.04, 3.4, 0.25, sym, size=10, color=GRAY, bold=True, tag="ax-s")
        text(s, 9.28, y + 0.26, 3.4, 0.26, ttl, size=11.5, bold=True, tag="ax-t")
        text(s, 9.28, y + 0.52, 3.4, 0.32, desc, size=9, color=INK2, line=1.12, tag="ax-d")
    notes(s, "구상도 손글씨: ①남북축(대지축) / ②동서축(성동시장) → 폭 40m 선형공원 / ③역사유적축(황리단길) / 화랑로 연결 / 경주읍성 향일문. 축의 폭·차로·통행 방향은 이 단계에서 정하지 않으며 교차점이 곧 교차로·광장은 아니다. 지도의 축 위치는 라이노 최종 가구 가장자리에서 읽었고, ③은 부지 중심에서 황리단길 반경 300m 중심을 향한 방위다.")

@slide("axes_basis")
def _(d):
    s = std(d, "axes_basis", "도시축과 도로계획 : 근거", "기준축의 근거 : 문제와 데이터에서 축으로")
    rows = [["축", "위계", "잇는 대상", "문제 · 데이터 근거", "계획 반영"],
            ["② 동서축", {"text": "1등", "bold": True, "color": RED}, "성동시장(서) ↔ 전랑지·행복황촌(동)", "문제 ① 동서 단절: 985m 무횡단 · 육교 1 · 우회율 3.5 · 유동 밀도 14.6배 격차 · 성동시장 355m, 생활업종 87.8% [T2] · 기본계획 '철도로 동서 분리' [T1]", "폭 40m 선형공원(보행·녹지) + 화랑로 연결(차량). 가장 약한 지점의 통과 폭을 확보"],
            ["① 남북축", {"text": "2등", "bold": True}, "대릉원·황리단길(남) ↔ 북천·황성공원(북)", "문제 ② 남북 불균형: 황리단길 757명/ha, 주말 1.72배 · 북측 공원과 미연계 [T2] · 전략계획 '선로로 단절된 공간을 잇는 매개공간' [T1 인쇄쪽 161] · 2030 경관계획 폐철도 녹지경관축 [T1] · 도시숲 선호 65.3% [T2]", "폭 30m 남북 보행축(대지축). 폐선 노반 948m를 보행·녹지로"],
            ["③ 역사유적축", {"text": "2등", "bold": True}, "부지 중앙 ↔ 황리단길·대릉원(남서)", "문제 ④ 짧은 체류·차량 방문: 체류 1~3시간 79.1% · 자가용 76.9% [T2] · 대릉원 523m · 황리단길 994m [T2] · 2030 경관계획 역사유적 조망축(첨성로) [T1]", "사선 보행 가로. 관광객을 부지 안으로 끌어들이고 체류 장치로 잇는 방향"],
            ["향일문 조망로", {"text": "3등", "bold": True}, "부지 북측 ↔ 경주읍성 향일문(서)", "경주읍성 497m [T2] · 역사문화환경 보존지역 · 2030 경관계획 중심시가지 통경축 체계 [T1]", "보행 조망 가로. 읍성 방향 시야를 열고 서측 접속"],
            ["화랑로 연결", "차량", "동측 화랑로 ↔ 서측 원화로", "접속점 37곳(동 18·서 9) [T2] · 2030 경관계획 주통경축(화랑로) [T1] · 관광객 불편 1위 교통혼잡·주차 29.6% [T2]", "폭 12m 차량 가로. 주차전용건축물·공공청사 접근"],
            ["북천 유입", "차량·보행", "부지 북단 ↔ 북천 변 기존 가로", "북천이 경계 북단에 접함 · 황성공원 509m [T2] · 접속점 북 3곳", "북측 접속 가로 12m · 선형공원으로 주민 유입"]]
    table(s, 0.6, 1.55, [1.35, 0.6, 2.35, 5.1, 2.73], rows, row_h=0.72, size=9.5, hdr_h=0.38, align=["l", "c", "l", "l", "l"], bold_cols=(0,), tag="axb", valign="m")
    box_text(s, 0.6, 6.15, 12.13, 0.75, "축은 설계자의 취향이 아니라 1부에서 측정한 문제(①②④)와 상위계획·경관계획의 축 체계에서 나왔습니다. 위계는 손글씨 구상(위계 1~3등)을 그대로 옮겼습니다.", fill="#FFFFFF", line=ACC, line_w=1.5, radius=0.1, size=12, bold=True, anchor="m", margin=(0.3, 0.05, 0.3, 0.05), tag="axb-n")
    notes(s, "위계 1~3등은 도로망 구상도의 손글씨(<위계1등> 성동시장 연계·전랑지, <위계2등> 구경주역 대지축 / 관광객 끌어들임, <위계3등> 향일문 조망도로(보행) 경주읍성으로). 2030 경주시 경관계획 재정비(2025.04) §4.3 경관축: 폐철도 녹지경관축, 주통경축(화랑로·태종로·포석로 등), 역사유적 조망축(첨성로).")

@slide("roadsketch")
def _(d):
    s = std(d, "roadsketch", "도시축과 도로계획 : 도로망 구상", "차량 가로와 보행 가로의 역할 분담")
    picture(s, MA + r"\sketch_roads.jpg", 0.6, 1.5, 3.75, 5.45, mode="cover", align=(0.5, 0.5))
    photo_credit(s, 0.6, 1.5, 3.75, 5.45, "트레이싱지 구상도 · 검은 선 = 차량, 회색 띠 = 보행")
    rows = [["표시", "의미", "계획적 역할"],
            [{"text": "검은 굵은 선", "bold": True}, "차량 중심 동선", "외곽 가로 · 화랑로 연결 · 북측 접속. 자동차 접근과 주차·하역·비상차량"],
            [{"text": "회색 넓은 띠", "bold": True}, "보행 중심 동선", "남북 대지축 · 동서 선형공원 · 사선 가로. 보행 이동과 체류, 건물 출입구 연결"],
            [{"text": "적갈색 메모", "bold": True}, "계획 의도", "위계 1~3등, 성동시장 연계, 전랑지, 관광객 끌어들임, 향일문 조망"],
            [{"text": "희미한 빨간 선", "bold": True}, "이전 단계의 기준축", "①②③ 축 — 도로망의 방향과 교차 위치의 기준"]]
    table(s, 4.6, 1.55, [1.5, 1.7, 4.93], rows, row_h=0.5, size=10, hdr_h=0.36, align=["l", "l", "l"], tag="rs-t", valign="m")
    head(s, 4.6, 4.15, 8.1, "구상도의 손글씨 (그대로 옮김)")
    text(s, 4.6, 4.5, 8.13, 1.3, [dict(text="<위계 1등> 성동시장 연계 · 전랑지  —  동서 보행축", bullet=True, space_after=3), dict(text="<위계 2등> 구 경주역 대지축  —  남북 보행축  ·  <위계 2등> 관광객 끌어들임  —  사선 가로", bullet=True, space_after=3),
                                   dict(text="<위계 3등> 향일문 조망도로(보행) 경주읍성으로  ·  화랑로 연결  ·  북천 이동 유입 · 선형공원 주민 유입", bullet=True)], size=10.5, line=1.2, tag="rs-h")
    box_text(s, 4.6, 5.9, 8.13, 1.0, [dict(text="원칙", size=11, bold=True, color=RED, space_after=2), dict(text="모든 동선을 차량도로로 만들지 않습니다. 차량은 외곽과 횡단 한 곳에 두고, 부지 안쪽은 보행 중심 가로로 채워 보행 흐름이 차량도로 때문에 끊기지 않게 합니다. 회색 띠가 보행자전용인지 보행자우선인지는 다음 단계에서 정합니다.", size=10.5, line=1.2)], fill=TINT, radius=0.1, anchor="m", margin=(0.25, 0.08, 0.25, 0.08), tag="rs-n")

@slide("roadplan")
def _(d):
    s = std(d, "roadplan", "도시축과 도로계획 : 최종 도로계획도", "최종 도로계획도 (라이노 계획, 2026.10.11)")
    picture(s, MA + r"\road_plan_map.png", 0.6, 1.5, 4.3, 5.45, mode="contain", align=(0, 0))
    kp = [("19,257㎡", "차량 가로 · 8.4%", "외곽 순환 가로와 화랑로 연결 횡단 15,468㎡ + 북측 접속 가로 3,789㎡. 폭 약 12.6m · 연장 약 1,520m"),
          ("45,420㎡", "보행공간 · 19.9%", "남북 보행축·동서 선형공원 32,269㎡ + 남측 보행공간 9,267㎡ + 북측 3,884㎡"),
          ("163,347㎡", "가구 9개 · 71.6%", "도로와 보행공간이 나눈 건축·오픈스페이스 가구. 다음 쪽에서 획지 15개로 나눕니다")]
    for i, (big, ttl, desc) in enumerate(kp):
        x = 5.2 + i * 2.55
        rect(s, x, 1.55, 2.4, 2.05, fill=TINT, radius=0.1)
        text(s, x + 0.15, 1.62, 2.1, 0.5, big, size=20, bold=True, color=ACC if i < 2 else INK, tag="rp-b"); text(s, x + 0.15, 2.12, 2.1, 0.3, ttl, size=11, bold=True, tag="rp-t")
        text(s, x + 0.15, 2.45, 2.1, 1.1, desc, size=9.5, color=INK2, line=1.15, tag="rp-d")
    head(s, 5.2, 3.8, 7.5, "축이 도로가 된 방식")
    text(s, 5.2, 4.15, 7.53, 1.75, [dict(text="① 남북축 → 두 열의 가구 사이 30m 보행축(연장 530m). 폐선 노반 위에 두어 대릉원과 북천 방면을 잇습니다.", bullet=True, space_after=3),
                                     dict(text="② 동서축 → 40m 선형공원이 부지 폭 300m를 가로질러 성동시장과 동측 생활권을 잇습니다. 화랑로 연결은 그 남쪽 12m 차량 가로로 분리했습니다.", bullet=True, space_after=3),
                                     dict(text="③ 역사유적축 → 남측 가구의 사선 보행 가로로 황리단길·대릉원 방면 동선을 받습니다.", bullet=True, space_after=3),
                                     dict(text="차량은 외곽 가로를 돌고 횡단은 한 곳(화랑로 연결)에 두어, 안쪽 보행공간이 차량에 끊기지 않습니다.", bullet=True)], size=10.5, line=1.2, tag="rp-h")
    box_text(s, 5.2, 6.0, 7.53, 0.9, "폭·연장은 라이노 폴리곤의 면적과 중심선 길이에서 계산한 근사값입니다. 차로 수·단면 구성·통행 방향은 다음 단계(배치 구상안)에서 정합니다.", fill="#FFFFFF", line=LINE, radius=0.1, size=10.5, color=INK2, anchor="m", margin=(0.25, 0.05, 0.25, 0.05), tag="rp-n")
    notes(s, "라이노 aardvark 슬롯에서 사용자가 선택한 최종 도로 객체(동측 복사본, x +563.4m)를 계획 프레임으로 되돌려 읽었다. 도로 폭 = 면적 ÷ (둘레/2 − 폭) 반복 근사. 가구 = 경계 − 도로 − 보도. 계산: build/road_plan.py.")

@slide("roadtable")
def _(d):
    s = std(d, "roadtable", "도시축과 도로계획 : 도로계획표", "도로계획표")
    picture(s, MA + r"\road_plan_solo.png", 0.6, 1.5, 2.1, 5.45, mode="contain", align=(0, 0))
    rows = [["구분", "성격", "폭", "연장 · 면적", "연결 대상", "기준 축"],
            [{"text": "외곽 순환 가로", "bold": True}, "차량 중심(보차공존)", "약 12.6m", "약 1,225m · 15,468㎡", "동측 화랑로 · 서측 원화로 가로망 · 주차전용건축물", "화랑로 연결 · 접속점"],
            [{"text": "북측 접속 가로", "bold": True}, "차량", "약 12.8m", "약 296m · 3,789㎡", "북천 변 기존 가로(북 접속점 3곳)", "① · 북천 유입"],
            [{"text": "남북 보행축(대지축)", "bold": True}, "보행 중심 · 녹지", "30m", "약 530m", "대릉원 ↔ 북천·황성공원", "① 위계 2등"],
            [{"text": "동서 선형공원", "bold": True}, "보행 · 공원", "40m", "약 300m", "성동시장 ↔ 전랑지·행복황촌", "② 위계 1등"],
            [{"text": "사선 보행 가로", "bold": True}, "보행", "가구 내", "남측 보행공간 9,267㎡", "황리단길·대릉원 방면", "③ 위계 2등"],
            [{"text": "향일문 조망로", "bold": True}, "보행 · 조망", "가구 사이", "북측 보행공간 3,884㎡ 포함", "경주읍성 향일문 방면", "위계 3등"]]
    table(s, 2.95, 1.55, [1.85, 1.5, 0.85, 1.9, 2.45, 1.23], rows, row_h=0.58, size=10, hdr_h=0.38, align=["l", "l", "c", "l", "l", "l"], tag="rt", valign="m")
    box_text(s, 2.95, 5.75, 9.78, 1.15, [dict(text="도로율", size=11, bold=True, color=RED, space_after=2), dict(text="차량 가로 8.4% + 보행공간 19.9% = 28.3%. 5주차 안(도로 20.4%·공원 16.5%)보다 차량 가로는 줄고 보행공간은 늘었습니다. 보행자전용·보행자우선·일반도로의 구분과 단면은 다음 단계에서 정합니다.", size=11, line=1.2)], fill=TINT, radius=0.1, anchor="m", margin=(0.25, 0.08, 0.25, 0.08), tag="rt-n")
    notes(s, "연장은 면적 ÷ 근사 폭. 남북 보행축 연장은 가구 가장자리 y 1,761,454~1,761,984(계획 좌표) = 530m, 동서 선형공원은 부지 폭 약 300m. 5주차 안 수치: 획지 15개 76,159㎡·공원 16.5%·도로 20.4%(strata v1, 경계 120,547㎡ 기준).")

@slide("blocks")
def _(d):
    s = std(d, "blocks", "도시축과 도로계획 : 가구와 획지", "도로가 나눈 가구 9개와 획지 15개")
    picture(s, MA + r"\blocks_map.png", 0.6, 1.5, 4.3, 5.45, mode="contain", align=(0, 0))
    rows = [["가구", "면적(㎡)", "획지(용도) 구성"],
            ["1", "17,762", "공연장 9,143 · 북측 오픈스페이스 8,619"], ["2", "22,022", "청년·신혼 주거 16,999 · 생활편의 체육 5,023"], ["3", "18,123", "공공청사·의회 18,123"],
            ["4", "12,661", "청년 업무·근린 12,661"], ["5", "17,139", "청년 업무·근린 8,624 · 중앙 오픈스페이스 8,515"], ["6", "11,998", "창작 레지던시·체험 11,998"],
            ["7", "16,781", "창작 레지던시·체험 8,396 · 성동시장 연계 8,386"], ["8", "20,419", "관광휴게·문화 + 근대역사관(구 역사 리유즈) 20,419"], ["9", "26,442", "관광휴게·문화 8,852 · 관광지원·주차전용 7,850 · 미배정 9,739"],
            [{"text": "합계", "bold": True}, {"text": "163,347", "bold": True}, {"text": "건축 획지 13개 136,473 · 오픈스페이스 2개 17,135 · 미배정 9,739", "bold": True}]]
    table(s, 5.2, 1.55, [0.6, 1.1, 5.83], rows, row_h=0.36, size=10, hdr_h=0.36, align=["c", "r", "l"], tag="bl-t", valign="m")
    box_text(s, 5.2, 5.6, 7.53, 1.3, [dict(text="가구 → 획지", size=11, bold=True, color=RED, space_after=2), dict(text="가구는 도로와 보행공간이 나눈 땅이고, 획지는 가구를 용도별로 다시 나눈 것입니다(점선). 가구 9의 9,739㎡는 최종 도로계획에서 보행공간이 줄며 생긴 땅으로, 관광휴게 획지 확대 또는 광장으로 배정할지 결정이 필요합니다. 건폐율·용적률의 분모는 건축 획지 136,473㎡입니다.", size=10.5, line=1.2)], fill=TINT, radius=0.1, anchor="m", margin=(0.25, 0.08, 0.25, 0.08), tag="bl-n")
    notes(s, "가구 = 경계 228,025 − 차량 가로 19,257 − 보행공간 45,420 = 163,347㎡(9개). 획지 면적은 라이노 프로그램 레이어 폴리곤. 가구 1·5·7은 오픈스페이스 또는 두 용도가 보행공간 없이 한 가구를 이룬다.")

@slide("div4")
def _(d): divider(d, "div4", "4", "프로그램", "선정 방법과 후보 평가 · 앵커 ①② · 기타 프로그램과 비교안 · 권역 구성 · 세부 프로그램", DARK)

@slide("matrix")
def _(d):
    s = std(d, "matrix", "프로그램 : 선정 방법", "프로그램 선정 방법과 후보 평가")
    flow = ["문제 6개", "필요 기능", "후보 7개", "평가 기준 5개", "앵커 3 · 보조 1 · 기타"]
    for i, f in enumerate(flow):
        x = 0.6 + i * 2.5; box_text(s, x, 1.55, 2.2, 0.5, f, fill=ACC if i == 4 else TINT, radius=0.08, size=11, bold=True, color="#FFFFFF" if i == 4 else INK, align="c", anchor="m", margin=(0.05, 0.02, 0.05, 0.02), tag="mx-f")
        if i < 4: arrow_right(s, x + 2.22, 1.67, 0.25, 0.26, G3)
    hdr = ["후보", "문제 대응", "시 구상 정합", "혁신지구 요건", "규제 적합", "운영·수요 근거", "판정"]
    rows = [["청년창업·기업지원(청년오피스복합타운)", "●", "●", "●", "●", "◐", {"text": "앵커", "bold": True, "color": RED}], ["청년·신혼 주거", "●", "●", "●", "◐", "○", {"text": "앵커(정주)", "bold": True, "color": RED}],
            ["K-헤리티지·역사문화예술", "●", "●", "◐", "●", "◐", {"text": "앵커", "bold": True, "color": RED}], ["창작 스튜디오·공방", "◐", "○", "◐", "●", "○", "보조 앵커"],
            ["공공청사·의회", "●", "◐", "○", "◐", "◐", "확산 거점 · 시 구상 2단계"], ["모빌리티 허브", "◐", "●", "◐", "●", "○", "기타(필수 기능) · 선택 제안"], ["성동시장 연계 상업 · 소규모 숙박", "◐", "●", "○", "●", "○", "선택 제안 · 치환 위험 관리"]]
    table(s, 0.6, 2.25, [3.6, 1.3, 1.3, 1.3, 1.3, 1.4, 1.93], [hdr] + rows, row_h=0.4, size=10.5, hdr_h=0.4, align=["l", "c", "c", "c", "c", "c", "l"], tag="mx-t")
    text(s, 0.6, 5.55, 12.1, 0.5, "● 강함  ◐ 중간  ○ 약함 · 판단 근거: 전략계획 쇠퇴원인 1번 [T1] · 시 구상 3-1·1-1·1-2·2-1 [T2] · 혁신지구 가이드라인(기능 집적, 국비 대상) [T2] · 고도지구·매장유산 [T1] · 수요 자료 유무", size=10.5, color=GRAY, line=1.2, tag="mx-s")
    box_text(s, 0.6, 6.15, 12.13, 0.75, "앵커는 문제에 직접 대응하고 시 구상과 공모 요건에 맞으며 규제 안에서 지을 수 있는 기능으로 정했습니다. 수요·운영 근거가 약한 항목은 단계 공급과 입주 확약으로 보완합니다.", fill=TINT, radius=0.1, size=11.5, bold=True, anchor="m", tag="mx-n")

@slide("anchor1")
def _(d):
    s = std(d, "anchor1", "프로그램 : 앵커 ①", "앵커 ①  청년 일자리와 청년주거")
    for i, (ttl, sub, kp, bl) in enumerate([
        ("청년창업·기업지원", "청년오피스복합타운 · 공유 오피스 · 상담·교육·협업실", [("1,208명/년", "20~34세 연평균 순유출(7,249 ÷ 6) · 전출 사유 직업·교육 [T2]"), ("1번", "전략계획 종합 쇠퇴원인: 청년 경제활동·주거안정 기반 부재 [T1]")],
         ["시 구상 3-1 청년오피스복합타운, 시굴조사 계획서의 \"직주근접·젊은 층 정착\" [T2]", "혁신지구는 지자체 운영 기업지원센터를 국비 보조 대상으로 둡니다 [T2 가이드라인]", "관광 밖 일자리를 두어 소득 환류 조건 02(일자리의 질)를 충족합니다", "부족한 것: 입주 기업 수요 · 운영 주체 · 입주확약(공모 평가 항목)"]),
        ("청년·신혼 주거", "1~2인 세대 중심 공공임대 · 주민 공동시설 · 1층 생활편의", [("27명", "폐역 구역 상시 거주 인구 · 야간 유동 비중 3.7% [T2]"), ("14 / 17곳", "혁신지구 선정지 중 주거 포함 [T2] · 경주 1~2인 가구 73.8%(원도심 82.6%)")],
         ["시 구상 1단계에서 준주거 20,262㎡(25.5%)가 건축 가능 용지 중 가장 큽니다 [T2]", "가구주 20~39세 18,052가구(1~2인 14,122) · 신혼부부 3,801쌍(2024) [T2]", "부족한 것: 현재 자연녹지지역이라 용도지역 변경 전제 · 경주 입주율·수요 실측 없음", "대응: 기준 600세대를 약 200세대씩 3단계로 공급하고 입주율을 확인한 뒤 다음 단계를 진행합니다"])]):
        x = 0.6 + i * 6.25; rect(s, x, 1.55, 6.05, 5.35, fill=TINT, radius=0.1)
        text(s, x + 0.25, 1.68, 5.6, 0.4, ttl, size=16, bold=True, color=ACC, tag="a1-t"); text(s, x + 0.25, 2.08, 5.6, 0.3, sub, size=10.5, color=INK2, tag="a1-s")
        for j, (big, lab) in enumerate(kp):
            xx = x + 0.25 + j * 2.9; text(s, xx, 2.5, 2.7, 0.55, big, size=22, bold=True, color=ACC if j == 0 else INK, tag="a1-b"); text(s, xx, 3.05, 2.7, 0.75, lab, size=10, color=INK2, line=1.15, tag="a1-l")
        text(s, x + 0.25, 3.95, 5.6, 2.85, [dict(text=t, bullet=True, space_after=4) for t in bl], size=10.5, line=1.2, tag="a1-bl")
    notes(s, "경주시 도시재생 전략계획(2022) · 김권일 발표자료(2026) · 도시재생 혁신지구 가이드라인 · KOSIS 인구총조사 2025.")

@slide("anchor2")
def _(d):
    s = std(d, "anchor2", "프로그램 : 앵커 ②", "앵커 ②  역사문화예술과 창작")
    picture(s, PH + r"\ph58_site_tracks_north.jpg", 0.6, 1.55, 4.2, 2.6, mode="cover"); photo_credit(s, 0.6, 1.55, 4.2, 2.6, "폐선로와 노반 · 철도 흔적 보행길의 소재")
    picture(s, PH + r"\ph60_site_remnants_e.jpg", 0.6, 4.3, 4.2, 2.6, mode="cover"); photo_credit(s, 0.6, 4.3, 4.2, 2.6, "철도 잔존 시설 · 전시·체험의 소재(2026.09)")
    for i, (ttl, sub, kp, bl, col) in enumerate([
        ("K-헤리티지 · 역사문화예술", "구 역사·철도기억관 · 근대역사 전시관 · 공연장 · 문화유산 창작·교육 · 방문자 관문", [("2,807㎡", "구 역사 1,404㎡ × 2층 실측 · 철도기념물(2013)"), ("79.1%", "현장 체류 1~3시간 → 전시·체험·공연·교육의 체류 장치")],
         ["시 구상 1-1·1-2 K-헤리티지 복합거점에 직접 대응합니다 [T2]", "저층 1~3층 분동·지상 구성으로 고도·매장유산 규제 적합성이 가장 높습니다", "부족한 것: 이용자 원단위(교토철도박물관 원단위로 대체) · 운영 주체·재원"], ACC),
        ("창작 스튜디오 · 공방 (보조 앵커)", "창작 레지던시 · 역사·공예 체험관 · 시장 접점", [("675명", "경주 예술인 수 · 경북 시 1위, 전국 평균 이하 [T2]"), ("5.2명", "창작예술업 종사자(인구 1만 명당) [T2]")],
         ["방문객과 주민이 만나는 접점 장치(공개 공방·오픈스튜디오·시장 쇼케이스)입니다", "방문 지출이 공예인·예술인 소득으로 이어지는 자리입니다(조건 01)", "부족한 것: 임대 수요·입주 의향 → 예술인의 6/12/20% 입주를 3개 안으로 둡니다"], INK)]):
        x = 5.05 + i * 3.95; rect(s, x, 1.55, 3.75, 5.35, fill=TINT, radius=0.1)
        text(s, x + 0.2, 1.65, 3.4, 0.4, ttl, size=13, bold=True, color=col, tag="a2-t"); text(s, x + 0.2, 2.05, 3.4, 0.55, sub, size=10, color=INK2, line=1.15, tag="a2-s")
        for j, (big, lab) in enumerate(kp):
            yy = 2.65 + j * 1.1; text(s, x + 0.2, yy, 3.4, 0.5, big, size=22, bold=True, color=col, tag="a2-b"); text(s, x + 0.2, yy + 0.5, 3.4, 0.55, lab, size=10, color=INK2, line=1.15, tag="a2-l")
        text(s, x + 0.2, 4.9, 3.4, 1.95, [dict(text=t, bullet=True, space_after=3) for t in bl], size=10, line=1.2, tag="a2-bl")

@slide("others")
def _(d):
    s = std(d, "others", "프로그램 : 기타", "기타 프로그램과 비교안")
    rows = [["항목", "본 계획의 위치", "근거와 판단", "위험·대응"],
            [{"text": "공공청사·의회", "bold": True}, "포함 · 북측 확산 거점(SPREAD)", "상위계획 반영 · 시 구상은 2단계 민자유치(시청 이전 포함) · 국비 대상 제외 [T2]", "단일 대형·저녁 공동화(울산형) → 저층 분동, 정원 상충(850~960) → 법정 상한 24,276㎡"],
            [{"text": "모빌리티 허브", "bold": True}, "선택 제안(모빌리티 대합실)", "시 구상 3대 전략 중 하나 · 시민 요구 교통거점 2위(16건) [T2]", "면적 소요가 작아 단독 앵커 아님 · 환승 수요·운영 미확인"],
            [{"text": "성동시장 연계 상업·식음", "bold": True}, "선택 제안", "시 구상 3-3 K-F&C 마켓 · 생활업종 87.8% 자산 [T2]", "성동시장·중앙상가 250억 사업과 중복(치환 위험) → 시장 보정 20~45%"],
            [{"text": "소규모 숙박(경주 STAY)", "bold": True}, "선택 제안", "시 구상 경주 STAY · 도시민박 2→21곳 증가 [T2]", "주거 수요와 경합 → 도시민박 등록 수·월세 감시"]]
    table(s, 0.6, 1.55, [2.0, 2.6, 4.1, 3.43], rows, row_h=0.8, size=10.5, hdr_h=0.4, tag="ot-t", valign="m")
    note_box(s, 0.6, 5.7, 12.13, 1.25, "선택 제안 3개를 더하면", "기준안 총 연면적은 110,852㎡에서 118,931㎡로 늘고 건폐율 17.7% → 19.3%, 용적률 81.2% → 87.1%가 됩니다. 빼도 나머지 면적표는 유지됩니다. 시청·의회 이전은 시의 의사결정 문서가 없으므로 1·2단계를 구분해 표기하고, 분산 삽입형 대안 시나리오를 함께 냅니다.", bsize=11.5)

@slide("zones")
def _(d):
    s = std(d, "zones", "프로그램 : 권역", "권역 구성과 프로그램의 역할")
    picture(s, MA + r"\landuse_map.png", 0.6, 1.45, 4.3, 5.5, mode="contain", align=(0, 0))
    rows = [["권역", "주요 프로그램", "전략", "문제 · 목표"], [{"text": "A  공공청사·의회", "bold": True}, "본청·의회 청사", "SPREAD", "③ · 목표 ③"], [{"text": "B  일상생활", "bold": True}, "청년·신혼 주거 600세대 · 생활편의 · 주민 공동시설 · 생활체육", "SPREAD", "⑤ · 목표 ③"],
            [{"text": "C  청년 업무권", "bold": True}, "창업 입주사무실 · 공유 오피스 · 교육·협업실", "SPREAD · EXCHANGE", "③ · 목표 ③"], [{"text": "D  창작·체험권", "bold": True}, "창작 레지던시 · 역사·공예 체험관 · 시장 접점", "EXCHANGE", "④ · 목표 ②"],
            [{"text": "E  역사문화예술권", "bold": True}, "구 역사·철도기억관 · 근대역사 전시관 · 공연장 · 창작·교육 · 방문자 관문", "EXCHANGE", "① ④ · 목표 ① ②"], [{"text": "야외·공공공간", "bold": True}, "문화광장 · 철도 흔적 보행길 · 정원 · 생활공원 · 텃밭", "CONNECT", "① ② · 목표 ①"]]
    table(s, 5.1, 1.55, [1.7, 3.3, 1.4, 1.23], rows, row_h=0.46, size=10, hdr_h=0.38, tag="zn-t", valign="m")
    head(s, 5.1, 4.9, 6, "프로그램의 네 부류")
    kinds = [("연결 장치", "문화광장 · 철도 흔적 보행길 · 방문자 관문 · 연결 안내 — CONNECT, 동선을 부지 밖으로 내보냅니다"), ("접점 장치", "시장 접점 · 공개 공방 · 체험관 · 오픈스튜디오 · 기획전시 — EXCHANGE, 방문 지출이 주민 소득으로"),
             ("정주·성장 장치", "청년·신혼 주거 · 보육·커뮤니티 · 청년 업무권 · 공공청사 — SPREAD, 저녁 이후 사람이 남고 청년 일자리"), ("기반 장치", "수장고 · 운영실 · 보존·복원 작업실 · 주차전용건축물 — 전시·보존·운영의 전제")]
    for i, (a, b) in enumerate(kinds):
        x = 5.1 + (i % 2) * 3.85; y = 5.25 + (i // 2) * 0.85
        rect(s, x, y, 0.1, 0.72, fill=ACC if i < 3 else G3); text(s, x + 0.22, y, 3.5, 0.25, a, size=11, bold=True, tag="zk-a"); text(s, x + 0.22, y + 0.25, 3.55, 0.5, b, size=9, color=INK2, line=1.15, tag="zk-b")
    src(s, 0.6, 7.0, 4.3, 0.3, "최종 도로계획 + 용도별 획지(라이노) · 회색 띠 = 보행공간, 진회색 = 차량 가로")

@slide("axon_program")
def _(d):
    s = std(d, "axon_program", "프로그램 : 배치 구상", "프로그램 배치 구상 (축측 · 남서 상공)")
    picture(s, MA + r"\diag_axon_program.png", 0.6, 1.45, 12.13, 5.1, mode="contain", align=(0.5, 0))
    picture(s, MA + r"\diag_legend.png", 0.6, 6.5, 3.4, 0.5, mode="contain", align=(0, 0.5)) if False else None
    text(s, 0.6, 6.6, 12.1, 0.4, "매스는 프로그램별 층수 가정(공공청사 5F 20m · 주거 6F 18m · 업무 5F 19.5m · 문화 3F 12m · 공연장 3F 15m · 주차 5F 15m)으로 획지 안쪽 5m를 띄워 올린 볼륨이며, 건축 배치안이 아니라 규모와 위치의 개념도입니다. 맥락 건물은 건축물대장 층수 기준입니다.", size=10, color=INK2, line=1.2, tag="ax-n")
    notes(s, "라이노 캡처 + 라벨 합성(compose_diagrams.py). 라벨 면적은 같은 프로그램 획지의 합.")

@slide("section_strip")
def _(d):
    s = std(d, "section_strip", "프로그램 : 남북 단면", "남북 단면 띠 : 프로그램의 배열과 높이")
    picture(s, MA + r"\diag_section_strip.png", 0.6, 1.5, 12.13, 4.6, mode="contain", align=(0.5, 0))
    items = [("남", "방문 관문", "관광휴게·근대역사관(구 역사) · 관광지원·주차 — 대릉원·황리단길에서 들어오는 방문객을 받습니다"), ("중앙", "교차·전환", "창작 레지던시·체험 · 시장 연계 — 동서 선형공원 40m와 남북 보행축이 교차하는 접점"), ("북", "근로·정주", "청년 창업·업무 · 공공청사·의회 · 청년·신혼 주거 · 생활편의 · 공연장 — 북천·황성공원 방면")]
    for i, (a, b, c) in enumerate(items):
        x = 0.6 + i * 4.1; rect(s, x, 6.15, 3.93, 0.8, fill=TINT, radius=0.08)
        text(s, x + 0.15, 6.2, 0.6, 0.3, a, size=12, bold=True, color=ACC, tag="ss-a"); text(s, x + 0.7, 6.2, 3.1, 0.3, b, size=11, bold=True, tag="ss-b"); text(s, x + 0.15, 6.48, 3.65, 0.45, c, size=9, color=INK2, line=1.15, tag="ss-c")
    notes(s, "section_strip.py: 최종 도로계획 획지의 남북 범위와 프로그램 높이 가정으로 그린 개념 단면. 서측 열·동측 열을 두 줄로 펼쳤다.")

@slide("programs")
def _(d):
    s = std(d, "programs", "프로그램 : 세부", "세부 프로그램 구성 (기준안, ㎡)")
    cols = [("A  공공청사·의회", "24,276", "본청·의회 청사 24,276\n(법정 상한 21,110 + 편의·법정시설 가산 15%)\n\n시 구상 2단계 사안 · 1·2단계 구분 표기", DARK),
            ("B  일상생활", "30,394", "청년·신혼 주거 600세대 28,182\n생활편의점 72 · 카페 200\n주민 커뮤니티홀 450 · 작은도서관 120\n공동부엌 52 · 보육실 300 · 생활관리실 100\n그늘쉼터 파빌리온 90\n법정 주민공동시설 보충 828", ACC),
            ("C  청년 업무권", "9,670", "청년 창업 입주사무실 5,285\n공유 오피스 3,523\n창업 상담·멘토링실 90\n직무교육실 266 · 공동회의실 160\n분야별 협업실(건축·디자인·관광·문화유산) 266\n공동작업 쉼터 80", ACC),
            ("D  창작·체험권", "6,225", "창작 레지던시 4,501\n개인 작업실 2,673 · 작가 체류실 707 · 공동 제작공방 405 · 오픈스튜디오 150 · 교류실 80 · 보관실 486\n역사·공예 체험관 1,465\n체험전시 815 · 전통공예 200 · 디지털 기록 100 · 어린이·가족 200 · 결과물 전시 150\n시장 접점 260\n쇼케이스 80 · 공예품 판매 120 · 픽업 거점 60", LIGHT),
            ("E  역사문화예술권", "9,566", "구 역사·철도기억관 3,087\n구 역사 2,807 · 아카이브 160 · 복원 작업실 120\n근대역사 전시관 1,435\n상설 900 · 기획 231 · 지역 예술가 150 · 공용 154\n공연·시민문화 3,448\n공연장 350석 3,003 · 연습실 160 · 다목적실 285\n문화유산 창작·교육 984 · 방문자 관문 338 · 수장고·운영실 274", INK2)]
    for i, (t, a, body, col) in enumerate(cols):
        x = 0.6 + i * 2.45
        rect(s, x, 1.55, 2.35, 0.75, fill=col); text(s, x + 0.12, 1.6, 2.15, 0.35, t, size=11, bold=True, color="#FFFFFF" if col != LIGHT else INK, tag="pg-t"); text(s, x + 0.12, 1.94, 2.15, 0.3, a + " ㎡", size=12, bold=True, color="#FFFFFF" if col != LIGHT else INK, tag="pg-a")
        rect(s, x, 2.3, 2.35, 4.05, fill=TINT); text(s, x + 0.12, 2.4, 2.15, 3.9, body, size=9, line=1.25, tag="pg-b")
    box_text(s, 0.6, 6.45, 12.13, 0.5, "야외·공공공간(연면적 아님) 17,464㎡  문화광장 3,000 · 야외 전시마당 1,200 · 역사 정원 2,000 · 철도 흔적 보행길 5,664(944m × 6m) · 생활공원·그늘쉼터 5,000 · 공동텃밭 600  —  프로그램 연면적 합(주차 제외) 80,132㎡", fill=INK, radius=0.08, size=9.5, color="#FFFFFF", anchor="m", tag="pg-n")
    src(s, 0.6, 7.0, 12.1, 0.3, "20261011 프로그램 면적표 v2 §3.2·§4 기준안 · 보수/적극 값과 가정 표시는 산정표 참조")

# ═════════════════════════════════ 3 계획 인구와 규모 ═════════════════════════════════
@slide("div5")
def _(d): divider(d, "div5", "5", "계획 인구와 규모", "계획 인구 · 방문·근로·정주 산정 · 산정 방법 · 토지이용 · 건축 규모 · 개발규모 산정표 · 규제 검토 · 확인 사항 · 운영", INK2)

@slide("pop")
def _(d):
    s = std(d, "pop", "계획 인구와 규모 : 계획 인구", "계획 인구 산정 (가정)")
    rows = [["구분", "계획 규모 (기준 · 보수~적극)", "산정 방법", "상태"],
            ["방문 인구", "11,067명/일 (8,265 ~ 14,849)", "외지인 일평균 140,085명 × 대상지 포획률 7.9%(5.9 ~ 10.6%) · 설계일 ×1.48 · 피크 1시간 7.0% [T2 관광데이터랩·소상공인365]", "가정"],
            ["근로 인구", "906명 (604 ~ 1,208) + 공공청사 약 850~960명", "청년 일자리 = 20~34세 연평균 순유출 1,208명의 75%(50 ~ 100%, 정책 가정) · 공공청사·의회 정원은 문서마다 달라 면적은 법정 상한으로 산정 [T2·T1]", "가정"],
            ["정주 인구", "798명 · 600세대 (450 ~ 750세대)", "청년 80% × 1.0인/호 + 신혼 20% × 2.65인/호 [T1 주택공급규칙] · 세대수는 원도심 청년 격차·신혼 저량·면적 용량·시설 임계의 겹침", "가정"]]
    table(s, 0.6, 1.6, [1.7, 3.4, 6.1, 0.93], rows, row_h=1.0, size=11, hdr_h=0.45, align=["l", "l", "l", "c"], bold_cols=(0,), tag="pop", valign="m")
    rows2 = [["항목", "보수", "기준", "적극"], ["방문 유동(평균일 / 설계일, 명)", "8,265 / 12,232", "11,067 / 16,379", "14,849 / 24,501"], ["피크 1시간 도착(명)", "795", "1,147", "1,911"], ["청년 일자리(명)", "604", "906", "1,208"], ["거주 세대 / 거주 인구(명)", "450 / 598", "600 / 798", "750 / 998"]]
    table(s, 0.6, 5.2, [3.4, 1.6, 1.6, 1.6], rows2, row_h=0.3, size=10.5, hdr_h=0.3, align=["l", "r", "r", "r"], tag="pop2")
    box_text(s, 9.0, 5.2, 3.73, 1.5, [dict(text="인근 주민 (S2)", size=11, bold=True, color=RED, space_after=3), dict(text="황오·황남·성건·월성 4개 동 30,261명(2026.08) · 65세 이상 40.9% [T2]. 부지 주민만으로 상업을 지탱하지 못하므로 방문·S2 인구를 합산합니다.", size=10.5, color=INK2, line=1.15)], fill=TINT, radius=0.1, anchor="m", margin=(0.2, 0.08, 0.2, 0.08), tag="pop-s2")
    text(s, 0.6, 6.8, 8.2, 0.3, "본 수치는 예측값이 아닌 계획 가정이며, 가정 항목은 보수·적극 열로 민감도를 둡니다.", size=11, bold=True, tag="pop-n")

@slide("visitors")
def _(d):
    s = std(d, "visitors", "계획 인구와 규모 : 방문", "방문 인구의 산정")
    steps = [("외지인 일평균 방문", "140,085명", "13개월 평균 · 통신 추정 [T2]"), ("× 대상지 포획률", "5.9 / 7.9 / 10.6%", "가정 · 현재 폐역 구역 0.9%, 구역 중심 300m 7.9%, 성동시장급 10.6%, 황리단길급 15.3%(상한 참조)"),
             ("= 평균일 방문 유동", "8,265 / 11,067 / 14,849명", "보수 / 기준 / 적극"), ("× 설계일 계수", "1.48 / 1.48 / 1.65", "일별 P90 · P95 직접 계산 [T2]"), ("= 설계일 방문", "12,232 / 16,379 / 24,501명", ""),
             ("× 피크 1시간 비율", "6.5 / 7.0 / 7.8%", "시간대별 분포 [T2]"), ("= 피크 1시간 도착", "795 / 1,147 / 1,911명", "방문자 관문·광장·체험관 동시 수용의 기준")]
    for i, (a, b, c) in enumerate(steps):
        y = 1.55 + i * 0.76; w = 7.6 - i * 0.45; res = a.startswith("=")
        rect(s, 0.6, y, w, 0.62, fill=TINT if i % 2 == 0 else "#FFFFFF", line=None if i % 2 == 0 else LINE, radius=0.06)
        text(s, 0.75, y, 2.6, 0.62, a, size=11.5, bold=res, anchor="m", tag="vs-a"); text(s, 3.4, y, w - 3.0, 0.62, b, size=13, bold=True, color=ACC if res else INK, anchor="m", tag="vs-b")
        text(s, 8.5, y + 0.08, 4.2, 0.5, c, size=10, color=INK2, line=1.2, tag="vs-c")
    src(s, 0.6, 6.95, 12.1, 0.3, "관광데이터랩(경주시 보고서 인용) · 소상공인365 로컬 계산 · 포획률·피크 비율은 가정, 보수/적극 열이 민감도")

@slide("workres")
def _(d):
    s = std(d, "workres", "계획 인구와 규모 : 근로·정주", "근로·정주 인구의 산정")
    head(s, 0.6, 1.5, 5.3, "청년 일자리 (정책목표형)")
    js = [("20~34세 순유출 누계", "7,249명 (2020–2025)"), ("÷ 6년", "1,208명/년"), ("× 회수 목표 50 / 75 / 100%", "604 / 906 / 1,208명"), ("× 1인당 7.2㎡ × 공용·지원 가산", "청년 업무 6,050 / 9,670 / 13,664㎡")]
    for i, (a, b) in enumerate(js):
        y = 1.9 + i * 0.72; rect(s, 0.6, y, 5.3, 0.6, fill=ACC if i == 3 else TINT, radius=0.06)
        text(s, 0.75, y, 2.6, 0.6, a, size=10.5, color="#FFFFFF" if i == 3 else INK, anchor="m", tag="wr-a"); text(s, 3.35, y, 2.5, 0.6, b, size=11, bold=True, color="#FFFFFF" if i == 3 else INK, anchor="m", tag="wr-b")
    text(s, 0.6, 4.85, 5.3, 0.9, "공공청사·의회 정원은 문서마다 850 · 942 · 약 960명으로 달라 인원이 아니라 법정 상한(공유재산법 시행령)으로 면적을 정했습니다.", size=10.5, color=INK2, line=1.2, tag="wr-n")
    head(s, 6.3, 1.5, 6.4, "청년·신혼 주거 600세대 — 여러 렌즈의 겹침")
    lo, hi, X0, X1 = 300, 1150, 6.3, 12.6; px = lambda v: X0 + (v - lo) / (hi - lo) * (X1 - X0)
    for v in (300, 450, 600, 750, 900, 1100):
        line(s, px(v), 1.95, px(v), 5.0, LINE, 0.5, dash=True); text(s, px(v) - 0.3, 5.02, 0.6, 0.25, str(v), size=9, color=GRAY, align="c", tag="wr-ax")
    lens = [("① 원도심 청년 격차 회복", 360, 590), ("② 신혼 저량·유량(몫 5~10%)", 215, 430), ("③ 면적 용량(36㎡ 기준)", 634, 634), ("⑤ 시설 임계(어린이집 300 · 공동시설 500)", 300, 500), ("⑧ 서울 철도부지 승인 밀도 적용", 469, 1112)]
    for i, (lab, a, b) in enumerate(lens):
        y = 2.05 + i * 0.55; text(s, X0, y - 0.22, 3.8, 0.22, lab, size=9, color=INK2, tag="wr-l")
        aa, bb = max(a, lo), min(b, hi)
        if a == b: rect(s, px(aa) - 0.03, y, 0.06, 0.2, fill=INK)
        else: rect(s, px(aa), y, px(bb) - px(aa), 0.2, fill=G3 if i == 4 else INK)
    rect(s, px(450), 4.75, px(750) - px(450), 0.2, fill=PALE); rect(s, px(600) - 0.04, 4.68, 0.08, 0.34, fill=ACC)
    text(s, px(600) - 1.1, 4.42, 2.2, 0.25, "기준 600 (450~750) · 예비 900", size=10, bold=True, color=ACC, align="c", tag="wr-k")
    text(s, 6.3, 5.4, 6.4, 1.5, [dict(text="⑩ 공실 위험(지방 소형 임대의 공가·계약률)에 따라 약 200세대씩 3단계로 공급하고 입주율을 확인한 뒤 다음 단계로 갑니다.", bullet=True, space_after=3),
                                 dict(text="청년 80% × 1.0인 + 신혼 20% × 2.65인 = 798명(450세대 598 · 750세대 998). 전용 26.58 / 36㎡ ÷ 전용률 0.606 → 주거 연면적 28,182㎡.", bullet=True)], size=10.5, line=1.2, tag="wr-b2")
    src(s, 0.6, 6.95, 12.1, 0.3, "KOSIS 국내인구이동통계 · 주민등록 2026.08 · 혼인·신혼부부 통계 · 주택공급규칙 · 20261008 청년·신혼 주거 규모 산정 v1")

@slide("how")
def _(d):
    s = std(d, "how", "계획 인구와 규모 : 산정 방법", "수치 산정 방법과 근거 구분", "측정값: 도면·통계에서 직접 산출  ·  산정: 법정 기준·원단위 적용  ·  가정: 본 계획에서 설정, 변경 가능  ·  원문 확인 전: 원문 대조 필요")
    G = "#1a7f37"; O = "#b45309"
    rows = [["항목", "의미", "산정 방법", "구분"],
            ["계획 경계 · 도로 · 대지면적", "경계 / 차량·보행 가로 / 건축 획지 합", "라이노 합집합 228,025㎡ / 도로 19,257 + 보행 45,420㎡ / 획지 합 136,473㎡(59.9%)", {"text": "측정값", "color": G, "bold": True}],
            ["방문 인구", "대상지 일평균 방문 유동", "외지인 일평균 140,085 × 포획률 5.9~10.6% × 설계일 계수", {"text": "산정 + 가정", "color": O, "bold": True}],
            ["청년 일자리 · 세대수", "정책 목표 인원 / 거주 세대", "순유출 1,208명/년 × 50~100% / 600세대(450~750)", {"text": "가정", "color": O, "bold": True}],
            ["공공청사 · 주차 · 주민공동시설", "법정 상한·소요", "공유재산법 시행령 상한 / 주차장 조례 / 주택건설기준", {"text": "산정(법정)", "color": G, "bold": True}],
            ["문화·체험·관문 면적", "이용자 → 면적", "이용 비율(5~12%) × 동시 체류 × 밀도 1.9/3.33/4.6㎡/인 · 사례 원단위", {"text": "산정 + 가정", "color": O, "bold": True}],
            ["건축면적 · 연면적 · 높이", "건물 규모", "연면적 ÷ 층수(공공청사 5F·주거 6F·문화 3F·주차 5F) · 층고 가정", {"text": "산정 + 가정", "color": O, "bold": True}],
            ["규제 비율", "용도지역·고도지구 비율", "최종 경계로 재산정 / 접속점·우회율·시굴 비율은 이전 경계·철도 부지 기준", {"text": "일부 재산정 전", "color": RED, "bold": True}]]
    table(s, 0.6, 1.8, [2.5, 2.6, 5.6, 1.43], rows, row_h=0.6, size=10.5, hdr_h=0.42, align=["l", "l", "l", "c"], bold_cols=(0,), tag="how")

@slide("landuse")
def _(d):
    s = std(d, "landuse", "계획 인구와 규모 : 토지이용", "토지이용 면적 구성 (라이노 계획)")
    vals = [("건축 획지", 136473, ACC, "건물이 서는 획지 13개 (권역 A~E + 주차)"), ("보행공간", 45420, G4, "남북 보행축 · 동서 선형공원 · 남북측 보행공간"), ("차량 가로", 19257, G3, "외곽 순환 가로 · 화랑로 연결 · 북측 접속"), ("오픈스페이스", 17135, LINE, "중앙·북측 오픈스페이스 2개"), ("미배정(가구 9)", 9739, "#F0A0AD", "남측 가구의 여유분 · 배정 결정 대기")]
    donut(s, 0.6, 1.6, 4.7, [v[0] for v in vals], [v[1] for v in vals], [v[2] for v in vals])
    text(s, 1.45, 3.45, 3.0, 0.5, "228,025㎡", size=20, bold=True, align="c", tag="dn-c"); text(s, 1.45, 3.95, 3.0, 0.3, "계획 경계 전체", size=10.5, color=INK2, align="c", tag="dn-c2")
    for i, (lab, v, col, desc) in enumerate(vals):
        y = 1.6 + i * 0.86
        rect(s, 5.8, y, 6.93, 0.78, fill=TINT, radius=0.1); rect(s, 5.8, y, 0.14, 0.78, fill=col)
        text(s, 6.15, y + 0.05, 2.9, 0.36, lab, size=14, bold=True, tag="lu-l"); text(s, 6.15, y + 0.42, 5.0, 0.32, desc, size=10, color=INK2, tag="lu-d")
        text(s, 9.1, y + 0.05, 2.0, 0.4, "%s㎡" % n(v), size=14, bold=True, align="r", tag="lu-v"); text(s, 11.2, y + 0.05, 1.4, 0.4, "%.1f%%" % (v / 228025 * 100), size=14, bold=True, color=ACC, align="r", tag="lu-p")
    note_box(s, 5.8, 5.95, 6.93, 1.0, "다섯 항목의 합계는 계획 경계 면적과 일치합니다.", "합계 228,024㎡(최종 도로계획 기준). 대지면적(건축 획지 합) 136,473㎡가 건폐율·용적률의 분모입니다.", bsize=11)
    notes(s, "최종 도로계획(사용자 선택 객체) 기준: 보행공간 45,420 / 차량 가로 19,257 / 가구 163,347 = 건축 획지 136,473 + 오픈스페이스 17,135 + 미배정 9,739. 합 = 합집합 U 228,024.8㎡. 이전 계획 프레임 값(보도 54,044 / 도로 20,372)은 대체됨.")

@slide("volume")
def _(d):
    s = std(d, "volume", "계획 인구와 규모 : 건축 규모", "건축 규모 : 프로그램 연면적 80,132㎡ · 총 연면적 110,852㎡ (기준안)")
    rows = [("B 일상생활", 30394, ACC), ("A 공공청사·의회", 24276, DARK), ("C 청년 업무권", 9670, LIGHT), ("E 역사문화예술권", 9566, G4), ("D 창작·체험권", 6225, G3), ("주차전용건축물", 30720, LINE)]
    for i, (lab, v, col) in enumerate(rows):
        y = 1.6 + i * 0.62; text(s, 0.6, y, 2.1, 0.4, lab, size=11.5, anchor="m", tag="vo-l")
        w = max(0.03, 3.0 * v / 30720); rect(s, 2.75, y + 0.05, w, 0.3, fill=col); text(s, 2.75 + w + 0.08, y, 2.4, 0.4, "%s㎡  (%.1f%%)" % (n(v), v / 110852 * 100), size=11, bold=True, anchor="m", tag="vo-v")
    text(s, 0.6, 5.4, 6.9, 0.3, "구성비는 총 연면적 110,852㎡(주차 포함) 기준 · 권역별 보수/적극 값은 산정표 참조", size=10.5, color=GRAY, tag="vo-s")
    defs = [("연면적", "지상 각 층 바닥면적의 합계 (주차전용건축물 포함)", "110,852㎡"), ("건폐율", "대지면적(건축 획지 136,473㎡) 대비 건축면적 24,108㎡", "17.7%"), ("용적률", "대지면적 대비 연면적 (주차 제외 58.7%)", "81.2%")]
    for i, (k, mean, val) in enumerate(defs):
        y = 1.6 + i * 1.05; rect(s, 7.6, y, 5.13, 0.95, fill=TINT, radius=0.1)
        text(s, 7.8, y + 0.08, 1.7, 0.4, k, size=14, bold=True, tag="vo-k"); text(s, 7.8, y + 0.5, 3.4, 0.4, mean, size=10, color=INK2, tag="vo-m"); text(s, 11.0, y + 0.18, 1.6, 0.6, val, size=20, bold=True, color=ACC, align="r", tag="vo-val")
    box_text(s, 7.6, 4.85, 5.13, 2.1, [dict(text="일상생활(주거)과 공공청사가 전체의 절반입니다.", size=12, bold=True, space_after=2), dict(text="방문 증가가 목표인 창작·체험(D)과 역사문화예술(E)은 프로그램 연면적의 20%에 그칩니다. 포획률(적극 10.6%)과 체험관 이용 비율을 올리면 커집니다.", size=10.5, color=INK2, space_after=6),
                                        dict(text="숙박·식음·모빌리티는 선택 제안입니다.", size=12, bold=True, space_after=2), dict(text="포함 시 총 연면적 118,931㎡ · 건폐율 19.3% · 용적률 87.1%로 늘어나며, 반영 여부의 결정이 필요합니다.", size=10.5, color=INK2)], fill="#FFFFFF", line=RED, radius=0.1, anchor="m", margin=(0.25, 0.1, 0.25, 0.1), tag="vo-n")
    text(s, 0.6, 5.8, 6.9, 1.1, "산정 유형: ① 정책목표형(청년 일자리·주거) ② 수요추정형(문화·체험·관문·레지던시) ③ 법정·기준형(공공청사 상한·주차 조례·주민공동시설). 밀도 기준 소방 1.9 / 교습소 3.33 / 집회 4.6㎡/인 [T1]", size=10.5, color=INK2, line=1.2, tag="vo-t")

@slide("scale")
def _(d):
    s = std(d, "scale", "계획 인구와 규모 : 산정표", "개발규모 산정표")
    rows = [["항목", "보수", "기준", "적극"], ["계획 경계(㎡)", "228,025", "228,025", "228,025"], ["대지면적(㎡, 건축 획지 합)", "136,473", "136,473", "136,473"], ["건축면적(㎡)", "15,999", "24,108", "35,070"],
            ["프로그램 연면적(주차 제외, ㎡)", "52,247", "80,132", "116,476"], ["주차 소요(대, 경주시 조례)", "686", "960", "1,258"], ["주차전용건축물(㎡, 지상 5층)", "20,588", "30,720", "44,037"],
            [{"text": "총 연면적(주차 포함, ㎡)", "bold": True}, {"text": "72,836", "bold": True}, {"text": "110,852", "bold": True, "color": RED}, {"text": "160,513", "bold": True}],
            [{"text": "건폐율(%)", "bold": True}, "11.7", {"text": "17.7", "bold": True, "color": RED}, "25.7"], [{"text": "용적률(%, 주차 포함)", "bold": True}, "53.4", {"text": "81.2", "bold": True, "color": RED}, "117.6"], ["용적률(%, 주차 제외)", "38.3", "58.7", "85.3"],
            ["최고 높이 · 층수", "20.0m · 5층", "20.0m · 5층", "20.0m · 5층"]]
    table(s, 0.6, 1.6, [3.6, 1.7, 1.7, 1.7], rows, row_h=0.38, size=11, hdr_h=0.4, align=["l", "r", "r", "r"], tag="sc-t")
    head(s, 9.5, 1.55, 3.2, "주요 도입기능별 면적·구성비 (기준)")
    rows2 = [["권역", "㎡", "비율"], ["A 공공청사·의회", "24,276", "30.3%"], ["B 일상생활", "30,394", "37.9%"], ["C 청년 업무", "9,670", "12.1%"], ["D 창작·체험", "6,225", "7.8%"], ["E 역사문화예술", "9,566", "11.9%"], [{"text": "합계(주차 제외)", "bold": True}, {"text": "80,132", "bold": True}, "100%"]]
    table(s, 9.5, 1.95, [1.6, 0.9, 0.73], rows2, row_h=0.34, size=10.5, hdr_h=0.34, align=["l", "r", "r"], tag="sc-t2")
    text(s, 9.5, 4.5, 3.23, 2.4, [dict(text="층수 가정: 공공청사 5F(20m) · 주거 6F(18m) · 문화·창작 3F · 주차전용 5F(15m)", bullet=True, space_after=4), dict(text="주차: 문화·판매·업무 100㎡/대, 근생·숙박 200㎡/대, 주거 0.7대/세대 [T1 경주시 조례]", bullet=True, space_after=4), dict(text="선택 제안 3개 포함 시(기준): 총 연면적 118,931㎡ · 건폐율 19.3% · 용적률 87.1%", bullet=True)], size=10, line=1.2, tag="sc-n")
    text(s, 0.6, 6.25, 8.7, 0.7, "지침의 개발규모 산정표 형식(대지면적·건축면적·연면적·건폐율·용적률·높이·층수)으로 작성했으며, 최종 경계 228,025㎡와 라이노 획지 합을 반영했습니다(calc/part2_model_final.py, 2026.10.11).", size=10.5, color=INK2, line=1.2, tag="sc-s")

@slide("rules")
def _(d):
    s = std(d, "rules", "계획 인구와 규모 : 규제", "규제 4겹 검토 (기준안)")
    cards = [("1", "용도지역", "자연녹지 74.7% · 2종일반주거 18.0% · 일반상업 7.3% — 건폐율 17.7%·용적률 81.2%는 자연녹지 한도(20%·100%) 안이나, 주거·업무 용도는 용도지역 변경(특별계획구역·세부개발계획) 전제"),
             ("2", "고도지구", "도심 20m 지구 84.5% · 15m 지구 12.7% · 최저고도 3.7% — 최고 20.0m는 20m 지구와 같아 여유가 없고 15m 지구·최저고도는 필지별 확인"),
             ("3", "보존지역 허용기준 · 매장유산", "삼층석탑 등 유적 주변 건축 제한 · 지하 0, 성토 2m 미만 · 시굴 후 배치 재검토 · 주차 960대는 지상 주차전용건축물"),
             ("4", "지구단위계획 (본 계획 수립)", "본 계획이 획지·용도·밀도·높이를 정함 · 공개공지 문화·판매 10%, 업무 5% → 용적률·높이 1.2배 완화 경로 [T1 경주시 건축 조례]")]
    for i, (num, ttl, body) in enumerate(cards):
        y = 1.6 + i * 1.3
        rect(s, 0.6, y, 6.9, 1.18, fill=TINT, radius=0.1); oval(s, 0.8, y + 0.3, 0.55, ACC, num, size=16)
        text(s, 1.55, y + 0.08, 5.8, 0.35, ttl, size=13, bold=True, tag="ru-t"); text(s, 1.55, y + 0.45, 5.8, 0.7, body, size=10, color=INK2, line=1.15, tag="ru-b")
    box_text(s, 7.85, 1.6, 4.88, 2.45, [dict(text="본 안 검토 결과(기준안)", size=12, bold=True, color=RED, space_after=4), dict(text="높이·건폐율·용적률 적합 (조건부)", size=18, bold=True, space_after=2),
                                        dict(text="용도지역 변경 전제이며 15m 지구·최저고도 구간은 필지별 확인이 필요합니다. 주차는 지하 불가로 지상 주차전용건축물(건폐율 90%·용적률 1,500% 허용)로 둡니다.", size=11, color=INK2, line=1.15)], fill="#FFFFFF", line=RED, radius=0.1, anchor="m", margin=(0.25, 0.1, 0.25, 0.1), tag="ru-r")
    box_text(s, 7.85, 4.25, 4.88, 2.55, [dict(text="가정이 큰 곳 (민감도 열 참조)", size=12, bold=True, color=ACC, space_after=4), dict(text="포획률 5.9~10.6% · 체험관 이용 5~12% · 청년 일자리 목표 50~100% · 레지던시 입주 6~20% · 공연장 350석 수요 · 야외공간 규모 · 공공청사 1·2단계 · 구 역사 이전 여부 · 데크·공중광장 기초 규제", size=11, line=1.2)],
             fill=TINT, radius=0.1, anchor="m", margin=(0.25, 0.1, 0.25, 0.1), tag="ru-n")
    notes(s, "비율은 최종 경계 228,025㎡ 기준 재산정(2026.10.11). 접속점·우회율은 이전 분석 경계, 시굴 비율은 철도 부지 148,770㎡ 기준이며 다음 단계에서 재산정.")

@slide("open")
def _(d):
    s = std(d, "open", "계획 인구와 규모 : 향후 과제", "확인 사항과 결정 사항")
    box_text(s, 0.6, 1.6, 5.95, 4.05, [dict(text="확인 사항", size=18, bold=True, space_after=8),
                                      dict(text="시 구상 면적 79,438㎡·사업비 3,822억·방문객 872만 명은 언론 인용값 [T4]", bullet=True, space_after=6), dict(text="접속점 37곳·우회율 3.5·시굴 비율의 최종 경계 재산정", bullet=True, space_after=6),
                                      dict(text="구 역사 이전 가능 여부(코레일 협의) · 한 연구는 현 위치 보존을 제안", bullet=True, space_after=6), dict(text="삼층석탑 주변 허용기준 · 데크·공중광장의 높이·기초 규제", bullet=True, space_after=6),
                                      dict(text="공공청사 정원·청사 대장, 경주 행복주택 입주율, 공연장 수요 근거", bullet=True)], fill=TINT, radius=0.1, size=12, line_sp=1.15, anchor="t", margin=(0.35, 0.25, 0.3, 0.2), tag="op1")
    box_text(s, 6.78, 1.6, 5.95, 4.05, [dict(text="결정 사항", size=18, bold=True, space_after=8),
                                       dict(text="공공청사·의회의 1·2단계 구분 (시 구상은 2단계 민자)", bullet=True, space_after=6), dict(text="선택 제안 3개(식음·판매, 소규모 숙박, 모빌리티 대합실) 반영 여부", bullet=True, space_after=6),
                                       dict(text="포획률 기준값 7.9% vs 성동시장급 10.6%", bullet=True, space_after=6), dict(text="청년주거 600세대의 공급 주체(행복주택 · 시 직영 · 공공지원 민간임대)", bullet=True, space_after=6),
                                       dict(text="집약형 안과 분산 삽입형 안의 비교 여부", bullet=True)], fill=PALE, radius=0.1, size=12, line_sp=1.15, anchor="t", margin=(0.35, 0.25, 0.3, 0.2), tag="op2")
    box_text(s, 0.6, 5.85, 12.13, 0.95, "확인 사항은 원문 대조로 확정하고, 결정 사항은 대안 비교로 판단합니다. 다음 단계는 배치 구상안(도로·필지·건물·공공공간) → 긴 방향 단면 조닝 → 3D 볼륨입니다.", fill="#FFFFFF", line=ACC, line_w=1.5, radius=0.1, size=14, bold=True, anchor="m", margin=(0.3, 0.05, 0.3, 0.05), tag="op-b")

@slide("ops")
def _(d):
    s = std(d, "ops", "계획 인구와 규모 : 운영", "운영 주체와 재원 계획")
    rows = [("가로·광장·보행길", "시가 관리하고 시민 참여형 운영 협의체를 구성합니다.", "사례: 광주 푸른길은 (사)푸른길이 운영"), ("시장 접점 · 공개 공방", "임대료를 낮추어 상인·공예인에게 공급하고 상인회·협동조합과 공동 운영합니다.", "소득의 지역 잔류(조건 01)"),
            ("주차전용건축물", "주차 수입으로 셔틀·광장 운영비의 일부를 충당합니다.", "차량 방문객의 보행 진입 유도"), ("구 역사 · 전시관 · 공연장", "공공이 소유하고 운영 주체·재원을 다음 단계에서 확정합니다.", "운영 주체 명시는 혁신지구 계획서 필수 항목"),
            ("청년·신혼 주거 · 청년 업무권", "공공임대 또는 공공지원 민간임대로 공급하고 입주확약을 확보합니다.", "주거 비율 유지 · 입주확약은 공모 평가 항목")]
    for i, (what, how, why) in enumerate(rows):
        y = 1.6 + i * 1.0
        rect(s, 0.6, y, 12.13, 0.9, fill=TINT, radius=0.08)
        text(s, 0.8, y + 0.05, 2.8, 0.8, what, size=13, bold=True, anchor="m", tag="ops-w"); text(s, 3.7, y + 0.05, 5.2, 0.8, how, size=12, anchor="m", line=1.15, tag="ops-h"); text(s, 9.1, y + 0.05, 3.5, 0.8, why, size=10.5, color=INK2, anchor="m", line=1.15, tag="ops-y")
    box_text(s, 0.6, 6.6, 12.13, 0.45, "위 내용은 모두 가정이며, 운영 주체와 재원은 다음 단계에서 확정합니다.", fill="#FFFFFF", line=RED, radius=0.08, size=12, bold=True, color=RED, align="c", anchor="m", margin=(0.2, 0.02, 0.2, 0.02), tag="ops-n")

# ═════════════════════════════════ 맺음말 ═════════════════════════════════
@slide("before")
def _(d):
    s = d.slide("#FFFFFF")
    picture(s, A5 + r"\hero_before.jpg", 0, 0, SW, SH, mode="cover")
    box_text(s, 0.6, 5.55, 9.0, 1.45, [dict(text="현황", size=12, bold=True, color=RED, space_after=2), dict(text="폐역 부지의 현재 모습", size=27, bold=True, space_after=2), dict(text="도심 중앙의 남북 방향 공백지가 동서 간 보행 연결을 단절하고 있습니다. 마스터플랜 배치·단면·볼륨은 다음 파트에서 제시합니다.", size=12, color=INK2)], fill="#FFFFFF", alpha=0.9, radius=0.1, anchor="m", margin=(0.3, 0.1, 0.3, 0.1), tag="before")
    page_no(s, PAGE["before"]); notes(s, "경계 안 기존 건물(NGII 연속수치지도)만 남긴 흑백 현황 렌더(5주차).")

@slide("sources")
def _(d):
    s = std(d, "sources", "자료 : 출처", "자료 출처와 확인 상태")
    rows = [["등급", "자료", "활용 내용"],
            ["T1 법정·승인 문서", "2030 경주도시기본계획 / 경주시 도시재생 전략계획(변경, 2022) / 경북 고시 제2020-479호(고도지구) / 공유재산법 시행령·주택공급규칙·주차장 조례·건축 조례", "철도 부지 148,770㎡, 상위계획, 쇠퇴진단, 고도지구, 법정 상한·소요"],
            ["T2 공공 발간·통계", "원도심 미래구상 기획연구(2025) / 황오동 모니터링(2024·2025) / 관광실태조사(2024–25) / KOSIS·주민등록 / 소상공인365 / ITS / NGII·V-World / 관광데이터랩 / 김권일 발표자료(2026)", "시민 응답, 방문객 설문, 인구·순이동, 유동·업종, 소통, 가로·건물, 규제 비율, 매장유산, 시 구상"],
            ["T3 학술", "관광–소득–정주 연계 문헌(KCI·Crossref·OpenAlex) / 김신재(2013)", "성립 조건 5개, 철도 연혁"],
            ["T4 언론·2차", "시 구상 면적 79,438㎡·사업비 3,822억, 방문객 872만 명, 폐역 시기, MOU — 원문 확인 필요", "배경 설명에만 활용하고 규모 산정에는 사용하지 않음"],
            ["자체 산출", "라이노 계획 경계·획지 면적 / 포획률·일자리·세대·면적 산정(calc/part2_model_final.py) / 지도(gj-datamap GeoJSON)", "면적표, 산정표, 지도·다이어그램"]]
    table(s, 0.6, 1.6, [2.1, 6.9, 3.13], rows, row_h=0.92, size=10.5, hdr_h=0.4, align=["l", "l", "l"], bold_cols=(0,), tag="src", valign="m")
    text(s, 0.6, 6.35, 12.1, 0.6, "사진·지도 중 5주차 발췌분은 원도심 미래구상 기획연구(2025)와 도시재생 전략계획(변경, 2022)에서 가져왔고, 그 밖의 지도·다이어그램·사진은 본 계획에서 작성·촬영하였습니다.", size=11, color=INK2, line=1.2, tag="src-n")

if __name__ == "__main__":
    d = Deck()
    for k in ORDER: SL[k](d)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    d.save(OUT)
    print("saved", OUT, "slides", d.n)
    for w in K.WARN: print(w)
