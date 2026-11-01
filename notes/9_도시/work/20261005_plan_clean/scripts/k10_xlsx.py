"""K10 엑셀 — 면적표(대상지·시설별)·획지계획표·도로계획표·건물표·획지×시설 매트릭스·가정/출처 → 면적표_계획표_규제미적용v1.xlsx"""
import sys
from plotkit import *
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

S = TC["site"]; F = TC["fac"]; TR = TC["lot_rows"]; RR = TC["road_rows"]; PR = TC["piece_rows"]; SM = TC["summary"]; RN = TC["RNAME"]; ROWS = TC["ROWS"]
FONT = "맑은 고딕"
f_norm = Font(name=FONT, size=10); f_bold = Font(name=FONT, size=10, bold=True); f_hdr = Font(name=FONT, size=10, bold=True, color="FFFFFF"); f_small = Font(name=FONT, size=9, color="555555")
f_title = Font(name=FONT, size=14, bold=True); f_red = Font(name=FONT, size=10, bold=True, color="C0392B")
fill_h = PatternFill("solid", fgColor="404040"); fill_sub = PatternFill("solid", fgColor="ECECEC")
thin = Side(style="thin", color="BBBBBB"); b_bot = Border(bottom=thin)
NUM = '#,##0'; AREA = '#,##0"㎡"'; PCT = '0%'; PCT1 = '0.0%'

def hdr(ws, r, vals, c0=1):
    for i, v in enumerate(vals):
        c = ws.cell(r, c0 + i, v); c.font = f_hdr; c.fill = fill_h; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
def put(ws, r, c, v, fmt=None, bold=False, fill=None, align=None, wrap=False, font=None):
    cell = ws.cell(r, c, v); cell.font = font or (f_bold if bold else f_norm); cell.border = b_bot
    if fmt: cell.number_format = fmt
    if fill: cell.fill = fill
    cell.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
    return cell
def widths(ws, ws_w):
    for i, w in enumerate(ws_w, 1): ws.column_dimensions[get_column_letter(i)].width = w

wb = Workbook()
# ══ 1. 면적표 ══
ws = wb.active; ws.title = "면적표"
ws["A1"] = "Summary + Site Plan | 개요 + 전체배치도 — 면적표 (규제 미적용 개념안)"; ws["A1"].font = f_title
ws["A2"] = "합계가 계획 경계(작업 경계 U) 면적에 닫힌다. 값은 도면에서 직접 산정."; ws["A2"].font = f_small
hdr(ws, 4, ["Site Area", "대상지 면적", "면적(㎡)", "비율"]); hdr(ws, 4, ["Facility Area", "시설별 면적", "연면적(㎡)", "비율"], c0=6)
r = 5
def row1(en, ko, v, pct=None, sub=False):
    global r
    fl = fill_sub if sub else None
    put(ws, r, 1, en, bold=sub, fill=fl); put(ws, r, 2, ko, bold=sub, fill=fl); put(ws, r, 3, v, AREA if isinstance(v, (int, float)) else None, bold=sub, fill=fl, align="right"); put(ws, r, 4, pct, PCT1, bold=sub, fill=fl, align="right"); r += 1
row1("Station Site (Announced)", "폐역 부지(공고 면적) † [T4, 원문 미확인]", 79438, sub=True)
row1("Planning Boundary", "계획 경계(작업 경계 U)", round(S["U"], 1), sub=True)
row1("Park A", "공원 A · 북천 수변공원", round(S["park_A"], 1)); row1("Park B", "공원 B · 동서 그린 보행축", round(S["park_B"], 1)); row1("Park C", "공원 C · 역전광장·근린공원", round(S["park_C"], 1))
row1("Other Park Area", "기타공원면적(환승·교차광장)", round(S["park_other"], 1)); row1("Water Area", "수공간(해당 없음)", 0)
row1("Subtotal of Park", "공원면적 소계", round(S["park_total"], 1), S["park_total"] / S["planned"], True)
row1("Vehicle Road", "차량도로(보차공존 포함)", round(S["road_veh"], 1)); row1("Pedestrian Road", "보행자전용도로·보행골목", round(S["road_ped"], 1))
row1("Subtotal of Road", "도로면적 소계", round(S["road_total"], 1), S["road_total"] / S["planned"], True)
for no, a in S["lots"]: row1("Plot %d" % no, "획지 %d" % no, round(a, 1))
row1("Subtotal of Usable Land", "획지면적 소계", round(S["lot_total"], 1), S["lot_total"] / S["planned"], True)
row1("Planned Site Area", "계획부지 면적합계", round(S["planned"], 1), None, True)
r1_end = r
r = 5
def row2(en, ko, v, pct=None, sub=False, fmt=AREA):
    global r
    fl = fill_sub if sub else None
    put(ws, r, 6, en, bold=sub, fill=fl); put(ws, r, 7, ko, bold=sub, fill=fl); put(ws, r, 8, v, fmt if isinstance(v, (int, float)) else None, bold=sub, fill=fl, align="right"); put(ws, r, 9, pct, PCT1, bold=sub, fill=fl, align="right"); r += 1
for k, e, kr, v in F["rows"]: row2(e, kr, round(v, 1), v / F["total"] if v else 0)
row2("Total GFA", "연면적 합계", round(F["total"], 1), 1.0, True)
row2("Building Footprint", "건축면적 합계(지상)", round(F["footprint"], 1))
row2("FAR (Usable Land)", "용적률(가용부지기준)", F["far"], None, True, PCT1); row2("Coverage (Usable Land)", "건폐율(가용부지기준)", F["coverage"], None, True, PCT1)
pf = F["park_fac"]
row2("Park A : Pavilion", "공원 A : 수변 쉼터·카페", round(pf.get("Park A", 0), 1)); row2("Park B : -", "공원 B : 시설 없음(연결녹지)", 0); row2("Park C : Kiosk", "공원 C : 광장 매점·카페", round(pf.get("Park C", 0), 1)); row2("Other Facilities in the Park", "기타공원시설", 0)
row2("Subtotal of Park Facilities", "공원시설소계", round(F["park_fac_total"], 1), None, True)
row2("Total GFA (included Park Facilities)", "연면적합계(공원시설포함)", round(F["total_incl_park"], 1), None, True)
row2("(참고) Total GFA excl. Parking", "주차전용건축물 제외 연면적", round(F["total_excl_parking"], 1)); row2("(참고) FAR excl. Parking", "주차 제외 용적률", F["far_excl_parking"], None, False, PCT1)
rr = max(r1_end, r) + 2
ws.cell(rr, 1, "검증(수식)").font = f_bold
ws.cell(rr + 1, 1, "공원+도로+획지 = 계획부지?"); ws.cell(rr + 1, 3, "=IF(ABS(C%d+C%d+C%d-C%d)<0.5,\"OK\",\"차이\")" % (12, 15, 16 + len(S["lots"]) , 17 + len(S["lots"]) + 1 - 1))
ws.cell(rr + 2, 1, "연면적 행 합 = Total GFA?"); ws.cell(rr + 2, 3, "=IF(ABS(SUM(H5:H%d)-H%d)<0.5,\"OK\",\"차이\")" % (4 + len(F["rows"]), 5 + len(F["rows"])))
notes = ["† 경주시 공개 구상(2026.02) 기준 면적 — 언론 경유 [T4, 원문 미확인]. 계획 경계 U는 작업 경계(v3 규칙)이며 폐역 부지 공고 면적과 직접 비교하지 않는다.",
         "연면적 = 지상층 건축면적 × 층수의 단순 합. 1층을 판매·음식으로 쓰는 매스는 해당 1층만 Retail / F&B 행에 집계(총합 불변). 용적률·건폐율은 획지면적(가용지) 기준.",
         "숙박(Hotel)은 사용자 스케치에 없어 0 — 구상 프로그램 'STAY' 미반영(결정 필요). 주차전용건축물 연면적의 용적률 산입 여부는 건축법 시행령 제119조 해석 필요 [T1, 원문 미확인]."]
for i, t in enumerate(notes): ws.cell(rr + 4 + i, 1, t).font = f_small
widths(ws, [30, 34, 16, 9, 3, 34, 34, 16, 9]); ws.freeze_panes = "A5"

# ══ 2. 획지계획표 ══
ws = wb.create_sheet("획지계획표")
cols = ["번호", "획지", "획지명", "용도(분류)", "시설 구성", "획지면적(㎡)", "건축면적(㎡)", "건폐율", "연면적(㎡)", "용적률", "최고층수", "최고높이(m)", "접도(면한 도로)", "인접 공원", "고도지구(참고, 면적비)", "고도 초과 동수", "초과 연면적(㎡)",
        "계획 용어", "건축물 용도(건축법 시행령 별표1)", "도시·군계획시설", "고시 2026-8호 대응 [T1, 원문 대조 전]", "비고"]
hdr(ws, 1, cols); ws.row_dimensions[1].height = 32
for i, x in enumerate(TR, 2):
    fr = " · ".join("%s %gm" % (RN[k], w) for k, w in x["frontage"])
    vals = [x["no"], x["id"], x["name"], x["cat"], x["comp"], round(x["area"], 1), round(x["fp"], 1), x["bcr"], round(x["gfa"], 1), x["far"], x["maxf"], round(x["maxh"], 1), fr, " / ".join(x["parkfront"]), x["godo_txt"],
            x["over_n"], round(x["over_gfa"], 1), x["term"], x["law_use"], x["facility"], x["gosi"], x["note"]]
    fm_ = {6: NUM, 7: NUM, 8: PCT1, 9: NUM, 10: PCT, 12: '0.0', 17: NUM}
    for j, v in enumerate(vals, 1): put(ws, i, j, v, fm_.get(j), wrap=(j in (5, 13, 18, 19, 21, 22)))
n = len(TR) + 2
put(ws, n, 3, "합계", bold=True, fill=fill_sub)
for j in range(1, 23):
    if j != 3: put(ws, n, j, None, fill=fill_sub)
put(ws, n, 6, "=SUM(F2:F%d)" % (n - 1), NUM, True, fill_sub); put(ws, n, 7, "=SUM(G2:G%d)" % (n - 1), NUM, True, fill_sub); put(ws, n, 8, "=G%d/F%d" % (n, n), PCT1, True, fill_sub)
put(ws, n, 9, "=SUM(I2:I%d)" % (n - 1), NUM, True, fill_sub); put(ws, n, 10, "=I%d/F%d" % (n, n), PCT, True, fill_sub); put(ws, n, 17, "=SUM(Q2:Q%d)" % (n - 1), NUM, True, fill_sub)
widths(ws, [5, 8, 20, 14, 46, 12, 12, 8, 12, 8, 8, 9, 34, 12, 26, 8, 12, 34, 34, 22, 26, 40]); ws.freeze_panes = "D2"

# ══ 3. 도로계획표 ══
ws = wb.create_sheet("도로계획표")
cols = ["도로", "구분", "도로 성격", "폭원(m)", "연장(m)", "면적(㎡, 교차부 중복 제외)", "면적(㎡, 원형)", "통행 방식", "단면 구성 [계획 가정]", "역할", "기존 가로와의 연결(앵커)", "스케치 메모"]
hdr(ws, 1, cols); ws.row_dimensions[1].height = 32
for i, x in enumerate(RR, 2):
    vals = [RN[x["key"]], x["group"], x["kind"], x["w"], round(x["L"], 1), round(x["area_excl"], 1), round(x["area_raw"], 1), x["mode"], x["cross"], x["role"], x["anchor"], x["sketch_desc"]]
    for j, v in enumerate(vals, 1): put(ws, i, j, v, {5: '#,##0', 6: NUM, 7: NUM}.get(j), wrap=(j in (8, 9, 10, 11, 12)))
n = len(RR) + 2
for lab, grp in (("차량 소계", "차량"), ("보행자전용 소계", "보행"), ("골목 소계", "골목")):
    n += 0
    put(ws, n, 1, lab, bold=True, fill=fill_sub)
    for j in range(2, 13): put(ws, n, j, None, fill=fill_sub)
    put(ws, n, 6, "=SUMIF(B2:B%d,\"%s\",F2:F%d)" % (len(RR) + 1, grp, len(RR) + 1), NUM, True, fill_sub); n += 1
put(ws, n, 1, "도로 합계", bold=True, fill=fill_sub)
for j in range(2, 13): put(ws, n, j, None, fill=fill_sub)
put(ws, n, 6, "=SUM(F2:F%d)" % (len(RR) + 1), NUM, True, fill_sub)
ws.cell(n + 2, 1, "도시·군계획시설 도로 규모별 구분(중로·소로 N류)은 폭 경계값(이상/미만) 원문 확인 후 부여 [T1, 원문 미확인]. 단면 구성은 이 안의 계획 가정.").font = f_small
widths(ws, [10, 8, 24, 8, 8, 16, 12, 28, 52, 50, 56, 40]); ws.freeze_panes = "B2"

# ══ 4. 획지×시설 매트릭스 ══
ws = wb.create_sheet("획지×시설 연면적")
cols = ["획지", "획지명"] + ["%s %s" % (kr, e) for k, e, kr in ROWS] + ["연면적 합계"]
hdr(ws, 1, cols); ws.row_dimensions[1].height = 44
for i, x in enumerate(TR, 2):
    put(ws, i, 1, x["no"]); put(ws, i, 2, x["name"])
    for j, (k, e, kr) in enumerate(ROWS, 3): put(ws, i, j, round(x["rows"].get(k, 0.0), 1) or None, NUM)
    put(ws, i, 3 + len(ROWS), "=SUM(C%d:%s%d)" % (i, get_column_letter(2 + len(ROWS)), i), NUM, True)
n = len(TR) + 2
put(ws, n, 2, "합계", bold=True, fill=fill_sub)
for j in range(3, 4 + len(ROWS)): put(ws, n, j, "=SUM(%s2:%s%d)" % (get_column_letter(j), get_column_letter(j), n - 1), NUM, True, fill_sub)
put(ws, n, 1, None, fill=fill_sub)
widths(ws, [6, 24] + [14] * (len(ROWS) + 1)); ws.freeze_panes = "C2"

# ══ 5. 건물표 ══
ws = wb.create_sheet("건물표")
cols = ["획지번호", "획지", "건물", "용도", "분류", "역할", "층수", "층고(m)", "높이(m)", "건축면적(㎡)", "연면적(㎡)", "1층 판매·음식"]
hdr(ws, 1, cols)
for i, p in enumerate(PR, 2):
    vals = [p["lot_no"], p["lot"], p["name"], p["use"], p["cat"], p["role"], p["floors"], p["floor_h"], p["h"], p["footprint"], p["gfa"], p["retail_ground"]]
    for j, v in enumerate(vals, 1): put(ws, i, j, v, {10: NUM, 11: NUM}.get(j))
widths(ws, [8, 10, 30, 26, 14, 8, 6, 8, 8, 12, 12, 10]); ws.freeze_panes = "A2"

# ══ 6. 가정·출처 ══
ws = wb.create_sheet("가정·출처")
hdr(ws, 1, ["구분", "내용", "등급 / 상태"])
AS = [
    ("고정 입력", "구역 경계선 하나(작업 경계 U, v3 규칙, 218,478㎡). 획지·가구·용도는 전량 변경 가능.", "사용자 확정"),
    ("규제", "고도제한·용도지역·보존지역 허용기준·켜 규칙을 적용하지 않음(사용자 지시). 고도지구는 '참고' 열로만 병기.", "미적용"),
    ("층고", "주거 3.2 m, 업무 3.8 m, 공공 4.0 m, 문화 4.5 m, 판매 4.2 m, 체육 6.5 m, 주차 3.0 m, 역사 4.5 m, 교통 4.2 m, 창조 4.2 m", "계획 가정"),
    ("세대수", "주거 연면적 × 전용 70%% ÷ 36㎡(또는 60㎡) → %d~%d세대" % (round(SM["units60"]), round(SM["units36"])), "계획 가정"),
    ("주차", "주차전용건축물 연면적 ÷ 32㎡/대 → 약 %d면" % round(SM["park_spaces"]), "계획 가정 — 법정 주차대수 산정 아님"),
    ("도로", "폭원·성격은 계획값, 단면 구성은 계획 가정. 규모별 구분(중로·소로 N류)은 원문 확인 후.", "T1 원문 미확인"),
    ("폐역 부지 면적", "79,438㎡ — 경주시 공개 구상(2026.02) 인용", "T4, 원문 미확인"),
    ("건축법 시행령 제119조", "주차전용건축물 연면적의 용적률 산입 여부", "T1, 원문 미확인"),
    ("고시 2026-8호 대응", "결정도 공고(2026.01) 용도 대응 열 — 법정 문서 대조 전", "T1, 원문 대조 전"),
    ("고도지구", "V-World 용도지구 공간 데이터(도심 10/15/20/25/36 m 등) 기반 참고값 — 고시 원문 대조 전", "T2, 대조 전"),
    ("주변 건물", "NGII 연속수치지도 건물(층수 nmly) — 조감도 배경", "T2"),
    ("호텔·숙박", "사용자 스케치에 숙박 없음 → 0. 구상 프로그램 'STAY'와 불일치 — 결정 필요", "공백")]
for i, (a, b, c) in enumerate(AS, 2):
    put(ws, i, 1, a, bold=True); put(ws, i, 2, b, wrap=True); put(ws, i, 3, c, wrap=True)
widths(ws, [22, 100, 30])
path = OUT + r"\면적표_계획표_규제미적용v1.xlsx"
wb.save(path); print("saved", path)
