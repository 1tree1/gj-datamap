# front_pages_d — 11 문제 인식 · 12 대응 · 14~15 개발전략 · 부록
import json as _json
from shapely.geometry import shape as _shape, box as _box

# 같은 카메라(통영식 전후 쌍): 11쪽은 흑백+붉은 표식, 12쪽은 컬러+원칙색 표식. 틀은 2025 정사영상 F1(중심 219,780/360,850, 1,200×1,600m)
FR = FR_V
def _fx(X, ix, iw): return ix + (X - (FR["cx"] - FR["W"] / 2)) / FR["W"] * iw
def _fy(Y, iy, ih): return iy + ((FR["cy"] + FR["H"] / 2) - Y) / FR["H"] * ih
_PLAN = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_boundary_check\user_boundary_current_5187.geojson"
_ROADS = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean\gis\roads.geojson"

def _boundary():
    return _shape(_json.load(open(_PLAN, encoding="utf-8"))["features"][0]["geometry"])

def _poly_pts(geom, ix, iy, iw, ih):
    out = []
    gs = list(geom.geoms) if geom.geom_type.startswith("Multi") else [geom]
    for g in gs:
        if g.is_empty or g.geom_type != "Polygon": continue
        out.append([(_fx(x, ix, iw), _fy(y, iy, ih)) for x, y in g.exterior.coords])
    return out

def _base_img(gray):
    src = first(HI + r"\ortho_2025_F1.jpg")
    return vimg(src, gray=gray) if src else None

# 문제 6개(번호·이름·핵심 수치·근거 한 줄)
PROBLEMS = [
    ("도시구조", "동서 보행 단절", "985m", "도로 횡단이 없는 구간. 보행 육교는 1개이고 동서 우회율은 중앙값 3.5배입니다 [T2]"),
    ("사회", "고용·청년 유출", "−23.1%", "사업지 격자 32셀의 종사자 감소율(2018→2023). 황오동 20~39세 인구는 −44%입니다 [T2]"),
    ("사회", "짧은 체류와 차량 중심 방문", "79%", "황오동 방문객 설문의 체류 3시간 미만 비율. 자가용 이용은 76.9%입니다 [T2]"),
    ("사회", "주거·야간 활동의 공백", "0", "결정도의 주거용지. 야간(23~05시) 유동은 3.7~5.5%입니다 [T1·T2]"),
    ("사회", "관광 쏠림과 업종 치환", "+5 / −9", "점포형 업종 중 숙박·체류의 순증(+5)이 가장 크고 생활소매·식품제조의 순감(−9)이 가장 큽니다 [T2]"),
    ("대지 조건", "유산·규제의 제약", "93%", "시굴 대상 비율(고시 구역 대비). 고도 20m 지구 87.5%, 1단계 지하 개발은 불가합니다 [T1·T2]"),
]
MARK = [(219780, 360990), (220130, 360850), (219790, 360580), (219800, 361190), (219400, 361060), (219760, 360700)]   # 표식 위치(EPSG:5187)

# ═════════════════════════ 11 문제 인식 ═════════════════════════
@slide("problem")
def _(d):
    s = std(d, "problem", "설계방향 : 문제 인식과 대응", "문제 인식", "현황 분석에서 확인한 문제는 6개이며, 도시구조·사회·대지 조건의 세 층위로 정리됩니다.", scale=["대상지", "원도심"])
    ix, iy, iw = LM, 1.5, 4.7; ih = iw * 4 / 3
    base = _base_img(True)
    if base: picture(s, base, ix, iy, iw, ih, mode="cover")
    else: rect(s, ix, iy, iw, ih, fill="#D9DBDE"); text(s, ix, iy + ih / 2 - 0.15, iw, 0.3, "[이미지 대기] 2025 정사영상(흑백)", size=9, color=GRAY, align="c", anchor="m")
    bd = _boundary()
    for pts in _poly_pts(bd, ix, iy, iw, ih):
        poly(s, pts, fill="#FFFFFF", alpha=0.15, line=RED, line_w=2.0)
    # ① 동서 단절: 동서 점선 화살표
    y1 = _fy(360860, iy, ih)
    line(s, _fx(219540, ix, iw), y1, _fx(220030, ix, iw), y1, RED, 1.6, dash=True, arrow=True)
    for i, (X, Y) in enumerate(MARK):
        cx, cy = _fx(X, ix, iw), _fy(Y, iy, ih)
        num_chip(s, cx - 0.17, cy - 0.17, 0.34, i + 1, fill=RED, size=10)
    photo_credit(s, ix, iy, iw, ih, "국토지리정보원 2025 정사영상(흑백 처리) · 붉은 선은 본 계획 경계", size=7)
    x0 = 5.4; w = SW - RM - x0
    y = 1.5; rh = 0.86
    groups = {}
    for g, *_ in PROBLEMS: groups[g] = groups.get(g, 0) + 1
    # 행
    for i, (g, nm, big, ev) in enumerate(PROBLEMS):
        yy = y + i * rh
        rect(s, x0, yy, w, rh - 0.07, fill=(TINT if i % 2 == 0 else "#FFFFFF"))
        num_chip(s, x0 + 0.1, yy + (rh - 0.07) / 2 - 0.16, 0.32, i + 1, fill=RED, size=10)
        text(s, x0 + 0.55, yy + 0.02, 3.6, 0.26, nm, size=10.5, bold=True, anchor="m", tag="pr-n")
        text(s, x0 + 0.55, yy + 0.28, 3.55, 0.46, ev, size=8.5, color=INK2, line=1.08, anchor="t", tag="pr-e")
        text(s, x0 + w - 1.55, yy + 0.04, 1.45, 0.4, big, size=17, bold=True, color=RED, align="r", anchor="m", tag="pr-big")
        text(s, x0 + w - 1.55, yy + 0.46, 1.45, 0.2, g, size=8, color=GRAY, align="r", anchor="m", tag="pr-g")
    takeaway(s, x0, y + 6 * rh + 0.06, w, 1.05, "방문 지표는 늘고 있으나 거주·고용·야간 지표는 줄거나 부족하며, 철도 부지가 동서 흐름을 단절하고 있습니다.",
             "문제 ②~⑤는 방문 중심의 개발로는 해결되지 않는 구조이고, ①은 연결, ⑥은 추진 순서의 조건입니다.", bar=RED, lead_size=10, body_size=8.8)
    notes(s, "문제 인식 쪽은 06~07쪽에서 확인한 사실을 6개 문제로 묶은 종합입니다. 표식의 위치는 문제가 나타나는 대표 위치를 가리키는 개념 표시이며 정확한 측정 지점이 아닙니다. 다음 쪽은 같은 사진(컬러)에서 각 문제에 대한 대응을 보입니다. 문제 번호 ①~⑥은 12쪽 대응, 13쪽 목표, 14쪽 전략에서 같은 번호·색으로 이어집니다.")

# ═════════════════════════ 12 대응 ═════════════════════════
@slide("response")
def _(d):
    s = std(d, "response", "설계방향 : 문제 인식과 대응", "문제 대응", "문제 6개는 5개 계획 원칙(연결·관문·근로·정주·확산)과 되돌릴 수 있는 추진 순서로 대응합니다.", scale=["대상지", "원도심"])
    ix, iy, iw = LM, 1.5, 4.7; ih = iw * 4 / 3
    base = _base_img(False)
    if base: picture(s, base, ix, iy, iw, ih, mode="cover")
    else: rect(s, ix, iy, iw, ih, fill="#CFE0C4"); text(s, ix, iy + ih / 2 - 0.15, iw, 0.3, "[이미지 대기] 2025 정사영상(컬러)", size=9, color=GRAY, align="c", anchor="m")
    bd = _boundary()
    bands = [("남", 360000, 360796, ZS), ("중", 360796, 361092, ZC), ("북", 361092, 362000, ZN)]
    for nm, y0, y1_, col in bands:
        part = bd.intersection(_box(219000, y0, 221000, y1_))
        for pts in _poly_pts(part, ix, iy, iw, ih):
            poly(s, pts, fill=col, alpha=0.42, line=None)
    for pts in _poly_pts(bd, ix, iy, iw, ih):
        poly(s, pts, fill=None, line="#FFFFFF", line_w=2.2)
    # 연결: 동서 연결 가로 5개와 종축
    for Y in (360659, 360796, 360953, 361092, 361240):
        xa = 219641; xb = 219930 if Y in (360796, 360953, 361092) else (219838 if Y == 360659 else 219790)
        line(s, _fx(xa, ix, iw), _fy(Y, iy, ih), _fx(xb, ix, iw), _fy(Y, iy, ih), BLUE, 2.2)
    line(s, _fx(219790, ix, iw), _fy(360740, iy, ih), _fx(219790, ix, iw), _fy(361240, iy, ih), BLUE, 3.2)
    # 확산: 성동시장·황오동 방향 화살표
    line(s, _fx(219641, ix, iw), _fy(360953, iy, ih) - 0.12, _fx(219430, ix, iw), _fy(361040, iy, ih), "#FFFFFF", 2.4, arrow=True)
    line(s, _fx(219930, ix, iw), _fy(360953, iy, ih) - 0.12, _fx(220140, ix, iw), _fy(360900, iy, ih), "#FFFFFF", 2.4, arrow=True)
    labs = [("북측 근로·정주", 361290, ZN), ("중앙 교류·창작", 360940, ZC), ("남측 방문 관문", 360620, ZS)]
    for t, Y, col in labs:
        box_text(s, ix + iw / 2 - 0.62, _fy(Y, iy, ih) - 0.13, 1.24, 0.26, t, fill="#FFFFFF", alpha=0.88, radius=0.06, size=8.5, bold=True, color=INK, align="c", anchor="m", margin=(0.02, 0, 0.02, 0), tag="rs-z")
    photo_credit(s, ix, iy, iw, ih, "구역 구성과 파랑 선(동서 연결 가로·종축)은 개념 표시", size=7)
    # 대응 표
    x0 = 5.4; w = SW - RM - x0
    cols = [("문제", 1.32), ("대응 방향", 2.1), ("계획 반영", w - 1.32 - 2.1)]
    rows = [("연결", "동서 보행 단절", "기존 가로에 접속하고 폐선 노반을 보행 중심 종축으로 계승", "기존 가로 끝 37곳에 접속하는 가로망, 폐선 노반을 계승하는 종축과 동서 보행축"),
            ("근로", "고용·청년 유출", "주간 근로 인구를 부지에 확보", "시청·의회 캠퍼스, 청년창업·기업지원"),
            ("관문", "짧은 체류와 차량 중심 방문", "차량은 남측에서 보행으로 전환하고, 체험으로 체류를 연장", "구 역사 이전·근대역사관, 관광지원, 주차전용건축물, 체험판매·공방"),
            ("정주", "주거·야간 활동의 공백", "정주 인구와 1층 생활 상가를 확보", "북측 청년주거와 1층 생활 상가, 청년·주민 커뮤니티"),
            ("확산", "관광 쏠림과 업종 치환", "성동시장과 경쟁하지 않고 연계하며, 방문·정주 지표를 병기", "성동시장 클러스터, 동서 보행축과 녹지"),
            ("조건", "유산·규제의 제약", "되돌릴 수 있는 것부터 추진하고 규제 4겹을 적용", "1단계 가로·광장·임시 평면주차, 시굴 후 핵심 시설")]
    x = x0; y = 1.5
    for name, cwid in cols:
        rect(s, x, y, cwid, 0.27, fill=INK); text(s, x + 0.08, y, cwid - 0.1, 0.27, name, size=9.5, bold=True, color="#FFFFFF", anchor="m", tag="rs-h"); x += cwid
    rh = 0.84; y += 0.3
    order = [0, 1, 2, 3, 4, 5]
    for i, (pr, nm, resp, plan) in enumerate(rows):
        yy = y + i * rh
        rect(s, x0, yy, w, rh - 0.06, fill=(TINT if i % 2 == 0 else "#FFFFFF"))
        num_chip(s, x0 + 0.08, yy + (rh - 0.06) / 2 - 0.14, 0.28, i + 1, fill=RED, size=9)
        text(s, x0 + 0.42, yy + 0.02, cols[0][1] - 0.46, rh - 0.1, nm, size=9.5, bold=True, anchor="m", line=1.06, tag="rs-n")
        text(s, x0 + cols[0][1] + 0.06, yy + 0.02, cols[1][1] - 0.12, rh - 0.1, resp, size=9, color=INK, anchor="m", line=1.08, tag="rs-r")
        px = x0 + cols[0][1] + cols[1][1] + 0.06
        col = PC.get(pr, "#8F8F8F"); tc = PCT.get(pr, "#FFFFFF")
        box_text(s, px, yy + 0.06, 0.5, 0.22, pr, fill=col, radius=0.08, size=8.5, bold=True, color=tc, align="c", anchor="m", margin=(0.01, 0, 0.01, 0), tag="rs-chip")
        text(s, px, yy + 0.3, cols[2][1] - 0.1, rh - 0.38, plan, size=8.3, color=INK2, anchor="t", line=1.06, tag="rs-p")
    takeaway(s, x0, y + 6 * rh + 0.04, w, 0.98, "다섯 원칙은 서로 다른 인구(방문·근로·정주)를 하나의 보행망 위에서 겹치게 하는 방식으로 짜입니다.",
             "시민 요구(설문 응답자 55명, 복수응답)는 문화·쇼핑 37, 교통 거점 16이었고 주거는 1건이었습니다. 문화·교통 요구는 남측·중앙에 반영하고, 정주 기능은 가구 구조와 야간 활동 자료를 근거로 추가합니다 [T2]. 원칙의 색은 13쪽 목표, 14쪽 전략으로 이어집니다.", bar=BLUE, lead_size=10, body_size=8.5)
    notes(s, "11쪽과 같은 사진·같은 틀을 컬러로 바꾸고, 문제마다 대응 원칙을 보입니다. 구역 구성(남측 방문 관문 / 중앙 교류·창작 / 북측 근로·정주)과 동서 연결 가로 5개는 본 계획 도면의 개념 표시이며, 상세 도면은 마스터플랜 장에서 설명합니다. 이 쪽의 구역·가로 표시는 개념 표시이며, 계획 반영의 상세 수치는 마스터플랜 장의 수정안(경계 120,547㎡)을 따릅니다. 규제 4겹 적용과 대안 비교 후 바뀔 수 있습니다.")
