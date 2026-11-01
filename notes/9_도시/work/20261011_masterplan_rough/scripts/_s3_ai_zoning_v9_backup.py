"""S3 단면 조닝 v2 — 설계 의도가 읽히는 단면(일러스트레이터 벡터)
원칙(사용자 지적 반영 2026-10-12)
 ① 가로·세로 같은 축척, 세 장 모두 1:800(1.25 mm/m) — 수직 과장 없음
 ② B–B′·C–C′는 전 구간 실제 치수, A–A′(735 m)만 긴 건물·공원·주거동 반복을 축약(끊김 표시 + 실제 치수 표기)
 ③ 가로·광장·보행축은 실제 폭 — 중앙 인도 40 m가 단면에서 가장 넓은 외부공간
 ④ 층 선·층별 용도, 위에는 요소마다 설계 의도 문구
 ⑤ 위 3컷은 단면이 지나는 핵심 장소 투시(라이노 r1_rhino_views.py → 포토샵 p0_ps_panels.py)
치수 출처: data/cuts.pkl(최종본 절단, s0_cuts.py) — 아래 SEQ의 폭·높이는 그 값을 옮긴 것
사용: python s3_ai_zoning.py [V|H|Dg ...]"""
import os, sys, json, math, subprocess, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import s2_ai_sections as S2
from s2_ai_sections import PRE, js, CL, OUTD, PW, PH, SALMON, INK
from PIL import ImageFont
FONT = {w: ImageFont.truetype(os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts", "Pretendard-%s.otf" % w), 100) for w in ("ExtraBold", "Medium")}
def tw(t, pt, w="ExtraBold"): return FONT[w].getlength(t) / 100.0 * pt * 25.4 / 72.0

SC = 1.25                     # mm per m, 1:800 — 가로·세로 공통, 세 장 공통
DROP = 1.1                    # 차도 노면을 대지 레벨보다 낮게(도면 mm, 단차 과장 — 실제 연석 0.15~0.2 m는 1:800에서 0.2 mm라 안 보인다)
GY, ZY = 148.0, 67.0          # 지반선 y, 조닝 띠 위 y (위 3컷 삭제 후 배치, 2026-10-12)
RED = "#E0393E"; ROAD = "#636363"
COL = {"판매": "#D93F87", "커뮤니티": "#D93F87", "생활SOC": "#13998B", "창작": "#6B2C91", "역사": "#B5562A", "문화": "#2B6CB0",
       "체험": "#1D2F5C", "전시": "#1E9BD7", "주거": ("#F08A5D", "#F7CF6E")}
USE = {"판매": "근린생활", "커뮤니티": "커뮤니티", "생활SOC": "생활체육", "창작": "공방·제작", "역사": "근대역사관", "문화": "문화", "체험": "체험", "전시": "전시", "주거": "주거"}
LEG = {"판매": "근린생활·커뮤니티", "커뮤니티": "근린생활·커뮤니티", "생활SOC": "생활체육", "창작": "공방·제작", "역사": "근대역사관(구 경주역사)",
       "문화": "생활문화·지역문화", "체험": "체험·작가 교류", "전시": "전시", "주거": "주거"}
FH = {"주거": 3.0, "커뮤니티": 3.0, "역사": 4.5}
GC = {"공원": "#86C85F", "선형": "#9ED67A", "보행": "#E9E4D6", "도로": ROAD, "보도": "#d9d9d6", "광장": "#E7D9BC", "마당": "#E7D9BC", "포장": "#E3E0D8"}


def B_(name, w, rects, **kw): return dict(t="bld", name=name, w=w, rects=rects, **kw)
def O_(name, w, kind, **kw): return dict(t="open", name=name, w=w, kind=kind, **kw)
_g = [0]
def G_(w, **kw): _g[0] += 1; return dict(t="gap", name="_gap%d" % _g[0], w=w, **kw)
def SW(w=3): _g[0] += 1; return O_("_보도%d" % _g[0], w, "보도")


HOUSE = [(0, 10, 0, 3, "커뮤니티"), (0, 10, 3, 15, "주거")]
SEQ = {
    # A–A′ 남북(실제 735 m → 도면 300 m): 공원·복합문화·실내체험관·전시관 앞마당·주거동 반복만 축약
    "V": [O_("북측 근린공원", 7, "공원", real=58, trees=(2.2, 5.2)), SW(), O_("북측 진입도로", 13, "도로"), SW(), G_(4),
          B_("체육관", 30, [(0, 30, 0, 16, "생활SOC")]), G_(5),
          B_("주거동0", 10, HOUSE), O_("주동 사이 마당", 24, "마당", trees=(12,)), B_("주거동1", 10, HOUSE), G_(6, brk=True),
          O_("향일문 조망로", 8, "보행"), G_(4),
          B_("복합문화공간", 26, [(0, 26, 0, 4, "판매"), (0, 26, 4, 12, "문화"), (0, 19, 12, 16, "문화")], real=96), G_(5),
          O_("중앙 인도", 40, "선형", trees=(3, 9, 31, 37), center=(12, 28), hero=True), G_(2.3),
          B_("실내체험관", 30, [(0, 12, 0, 8, "체험"), (18, 30, 0, 8, "체험"), (0, 30, 8, 12, "체험"), (0, 12, 12, 16, "체험"), (18, 30, 12, 16, "체험")], real=114, labrect=(0, 12, 0, 8, "체험")),
          SW(5), O_("남측 차도", 20, "도로"), O_("전시관 앞마당", 6, "포장", real=41),
          B_("전시관", 38, [(0, 16.8, 0, 16, "전시"), (25.2, 38, 0, 16, "전시")], court=(16.8, 25.2))],
    # B–B′ 동서 — 전 구간 실제 치수(77.4~373.0 m)
    "H": [SW(4.5), G_(7.5, pave=True),
          B_("휴게공간", 16.1, [(0, 16.1, 0, 8, "판매")], canopy=(-2.7, 18.7, 8.0, 9.1), use={"판매": "공방·판매"}), G_(5.1),
          O_("야외체험관", 80, "공원", trees=(6, 15, 24, 33, 47, 56, 65, 74)), G_(6.3),
          B_("공방·전시동", 24.9, [(0, 24.9, 0, 12, "창작")], use={"창작": "공방·전시"}), G_(2.8),
          O_("중앙 남북 인도", 29.9, "선형", trees=(3.6, 26.3), center=(8, 22), hero=True), G_(2.1),
          B_("실내체험관", 30, [(0, 30, 0, 16, "체험")]), G_(14.8, pave=True),
          B_("제작동", 15, [(0, 15, 0, 15, "창작")], floors=(5.5, 11.0), use={"창작": "제작"}),
          O_("레지던시 마당", 18.6, "마당", trees=(4.5,), bridge=(0, 18.6, 8.0, 9.5)),
          B_("거주동", 10, [(0, 10, 0, 15, "주거")], use={"주거": "거주"}), G_(11.8, pave=True), SW(5), O_("외곽도로", 11.2, "도로")],
    # C–C′ 사선 — 전 구간 실제 치수(37.0~298.1 m, 단면선 방향 길이)
    "Dg": [SW(4.5), O_("광장 진입부", 19.1, "포장"),
           O_("경주회관 앞마당", 43, "광장", trees=(5, 13, 30, 38), key=True), G_(7.5, pave=True),
           B_("근대역사관", 19.6, [(0, 19.6, 0, 9, "역사")], hip=15.0),
           O_("그레이트 코트", 27.9, "광장", glass=True),
           B_("지역문화원", 14, [(0, 14, 0, 4, "판매"), (0, 14, 4, 20, "문화")]), G_(4.5, pave=True),
           O_("남측 관광객 인도", 19.9, "선형", trees=(3.6, 16.3), key=True), G_(7.7, pave=True),
           B_("전시관", 40.3, [(0, 14, 0, 16, "전시"), (26.4, 40.3, 0, 16, "전시")], court=(14, 26.4)),
           O_("공유주차장·모빌리티 허브", 34.3, "포장"), O_("외곽도로", 18.8, "도로")],
}
# 설계 의도 — (대상 요소 이름 또는 목록, 제목, 의도)
INTENT = {
    "V": [("북측 근린공원", "북측 근린공원", "북측 생활권과 맞닿는 녹지"), ("체육관", "체육관", "생활체육 4층 · 주민 공유 거점"),
          (["주거동0", "주동 사이 마당", "주거동1"], "주거시설", "1층 커뮤니티 · 2~5층 주거 · 4개 동, 인동간격 24 m"),
          ("향일문 조망로", "향일문 조망로", "향일문 방향 조망 보행로"),
          ("복합문화공간", "복합문화공간", "1층 근린생활 · 2~4층 생활문화"), ("중앙 인도", "중앙 인도 40 m", "선형공원 · 가로수 4열 · 대지의 중심 가로"),
          ("실내체험관", "실내체험관 · 작가 교류·행사실", "두 동을 3층에서 연결 · 1층 통로 개방"), ("남측 차도", "남측 차도 20 m", "동서 차량 가로"),
          ("전시관", "전시관", "중정형 4층 전시")],
    "H": [("휴게공간", "휴게공간", "공방·판매 2층 · 옥상 캐노피"), ("야외체험관", "야외체험관 80 m", "공예 중정 · 야외 체험 마당"),
          ("공방·전시동", "공방·전시동", "전통공예 공방·전시 3층"), ("중앙 남북 인도", "중앙 남북 인도 30 m", "두 가구가 만나는 남북 보행축"),
          ("실내체험관", "실내체험관", "체험 4층"), (["제작동", "레지던시 마당", "거주동"], "레지던시", "제작동 3층 · 거주동 5층 · 브리지 연결"),
          ("외곽도로", "외곽도로", "동측 생활권 접속")],
    "Dg": [("경주회관 앞마당", "경주회관 앞마당 43 m", "역 정면 광장"), ("근대역사관", "근대역사관", "구 경주역사 존치 · 전시 공간으로 전환"),
           ("그레이트 코트", "그레이트 코트", "역사와 지역문화원 사이 유리 지붕 중정"), ("지역문화원", "지역문화원", "1층 소상공인 점포 · 2~5층 문화"),
           ("남측 관광객 인도", "남측 관광객 인도 20 m", "관문광장에서 이어지는 사선 보행축"), ("전시관", "전시관", "중정형 4층 전시"),
           ("공유주차장·모빌리티 허브", "공유주차장·모빌리티 허브", "관광 차량 수용 · 보행 전환")],
}
DIM = {"V": {"북측 진입도로": "13", "주동 사이 마당": "24", "향일문 조망로": "8", "중앙 인도": "40", "남측 차도": "20"},
       "H": {"야외체험관": "80", "중앙 남북 인도": "30", "레지던시 마당": "18.6", "외곽도로": "11.2"},
       "Dg": {"경주회관 앞마당": "43", "그레이트 코트": "27.9", "남측 관광객 인도": "20", "외곽도로": "18.8"}}
PANELS = {
    "V": [("북측 · 체육관·주거시설", "“생활체육 / 1층 커뮤니티 · 2~5층 주거”"), ("중앙 · 중앙 인도 40 m", "“가로수 4열 선형공원, 서측 원도심 방향”"),
          ("남측 · 실내체험관·전시관", "“체험 · 작가 교류 · 중정형 전시”")],
    "H": [("서측 · 휴게공간·야외체험관", "“캐노피 아래 휴게 / 야외 체험 마당”"), ("중앙 · 중앙 남북 인도 30 m", "“공방·전시동과 실내체험관 사이 남북 보행축”"),
          ("동측 · 실내체험관·레지던시", "“체험 / 제작 / 거주”")],
    "Dg": [("서측 · 경주회관 앞마당·근대역사관", "“역 정면 광장에서 본 구 경주역사”"), ("중앙 · 그레이트 코트·지역문화원", "“역사와 지역문화원을 잇는 유리 지붕 중정”"),
           ("동측 · 남측 관광객 인도·전시관", "“사선 보행축과 중정형 전시관”")],
}
NOTE = {"V": "가로·세로 같은 축척 1:800 · 가로·광장은 실제 폭, 긴 건물·공원·주거동 반복은 축약(끊김 표시, 회색 치수가 실제 길이) · 차도는 대지 레벨보다 낮게(단차 과장)",
        "H": "가로·세로 같은 축척 1:800 · 전 구간 실제 치수 · 차도는 대지 레벨보다 낮게(단차 과장)", "Dg": "가로·세로 같은 축척 1:800 · 전 구간 실제 치수(단면선 방향 길이) · 차도는 대지 레벨보다 낮게(단차 과장)"}

# 조닝 띠 — (영역 이름, 시작 요소, 끝 요소, 색)
ZONES = {
    "V": [("북측 접속", "북측 근린공원", "북측 진입도로", "#8a8a8a"), ("정주 · 생활체육", "체육관", "주거동1", "#E9824F"),
          ("생활문화", "향일문 조망로", "복합문화공간", "#2B6CB0"), ("공공 가로", "중앙 인도", "중앙 인도", "#4FA83D"),
          ("체험 · 작가 교류", "실내체험관", "실내체험관", "#1D2F5C"), ("전시", "전시관 앞마당", "전시관", "#1E9BD7")],
    "H": [("공예 가구 · 휴게 · 야외 체험 · 공방", "휴게공간", "공방·전시동", "#6B2C91"), ("남북 보행축", "중앙 남북 인도", "중앙 남북 인도", "#4FA83D"),
          ("체험·창작 가구 · 실내 체험 · 레지던시", "실내체험관", "거주동", "#1D2F5C")],
    "Dg": [("역 앞 광장", "광장 진입부", "경주회관 앞마당", "#C08A3E"), ("구 경주역 어댑티브 리유즈", "근대역사관", "지역문화원", "#B5562A"),
           ("관광객 동선", "남측 관광객 인도", "남측 관광객 인도", "#4FA83D"), ("전시", "전시관", "전시관", "#1E9BD7"),
           ("모빌리티", "공유주차장·모빌리티 허브", "외곽도로", "#7A7F87")],
}

JS_EXTRA = r"""
function tree2(x, gy, r, col) { P([[x, gy], [x, gy - r * 1.2]], false, null, "#8b7355", 0.7); E(x, gy - r * 2.1, r, r, col, null); }
function band(x0, x1, yt, yb, s, col, maxSize) {   // 층 띠 안 라벨: 가로 → 세로, 안 들어가면 생략
  var w = x1 - x0, h = yb - yt;
  for (var sz = maxSize; sz >= 10; sz -= 1) {
    var t = mk(s, sz, "Pretendard-Bold", col); var b = bnd(t); var tw = b[2] - b[0], th = b[3] - b[1];
    if (tw + 2.4 <= w && th + 0.4 <= h) { place(t, (x0 + x1) / 2, (yt + yb) / 2, "c"); return "h"; }
    if (th + 0.8 <= w && tw + 2.0 <= h) { t.rotate(90); place(t, (x0 + x1) / 2, (yt + yb) / 2, "c"); return "v"; }
    t.remove(); }
  return ""; }
"""


def build(key):
    cfg = S2.SHEETS[key]; seq = SEQ[key]
    total = sum(e["w"] for e in seq)
    assert total * SC <= 380, (key, total)
    x0 = PW / 2 - total * SC / 2; gy = GY
    Y = lambda z: gy - z * SC
    pos = {}; x = x0
    for e in seq: e["x0"] = x; e["x1"] = x + e["w"] * SC; pos[e["name"]] = e; x = e["x1"]
    xa, xb = seq[0]["x0"], seq[-1]["x1"]
    rnd = random.Random(7)
    o = [PRE % dict(W=PW, H=PH), JS_EXTRA]; add = o.append
    # ── 머리글
    add('layer("머리글");')
    add('var tt = T(%f, 7.2, %s, 15, "Pretendard-Bold", "%s", "c");' % (PW / 2, js(cfg["title"]), INK))
    add('var bb = bnd(tt); P([[bb[0] - 2, 11.6], [bb[2] + 2, 11.6]], false, null, "#333333", 0.6);')
    add("seq(%f, 15.8, %s);" % (PW / 2, js([[s, 10, "Pretendard-Medium", c or "#444444"] for s, c in cfg["sub"]])))
    # 위 3컷(핵심 장소 투시)은 사용자 요청으로 뺐다(2026-10-12). 이미지는 sheets/clip/*_ps.jpg에 남아 있다.
    add('layer("강조 문구");')
    add("seq(%f, %f, %s);" % (PW / 2, ZY - 11.0, js([[s, sz, "Pretendard-Bold" if sz > 12 else "Pretendard-SemiBold", SALMON] for s, sz in cfg["head"]])))
    # ── 지반 띠
    add('layer("지반");')
    add('GR(0, %f, %f, 42.0, "#a3a3a0", "#ffffff");' % (gy, PW))          # 지반 띠: 지반선 아래 42 mm에서 흰색으로
    add('T(%f, %f, %s, 14, "Pretendard-SemiBold", "#2b2b2b", "c", 0, 20);' % (PW / 2, gy + 26.0, js(cfg["ground_cap"])))
    # ── 주변 건물(양끝 여백이 있을 때만, 2~4층 표현)
    add('layer("주변 건물");')
    for side in (0, 1):
        room = (xa - 4) if side == 0 else (PW - 4 - xb)
        xx = (xa - 2) if side == 0 else (xb + 2)
        for w_, h_ in ((9, 10), (8, 7), (10, 13)):
            if room < w_ * SC + 2: break
            bx = xx - w_ * SC if side == 0 else xx
            add('R(%f, %f, %f, %f, "#ffffff", "#bdbdba", 0.5);' % (bx, Y(h_), w_ * SC, h_ * SC))
            xx = bx - 2.5 if side == 0 else bx + w_ * SC + 2.5; room -= w_ * SC + 2.5
    # ── 외부공간
    add('layer("외부공간");')
    for zname, ea, eb, zc in ZONES[key]:        # 영역 기둥(옅은 색) — 조닝 띠와 단면을 잇는다
        za, zb = pos[ea]["x0"] + 0.5, pos[eb]["x1"] - 0.5
        add('R(%f, %f, %f, %f, "%s", null, 0, 7);' % (za, ZY + 7.6, zb - za, gy - ZY - 7.6, zc))
    for e in seq:
        if e.get("hero"):
            add('R(%f, %f, %f, %f, "#B9E39A", null, 0, 32);' % (e["x0"], Y(27), e["x1"] - e["x0"], 27 * SC))
    roads = []
    for e in seq:
        if e["t"] == "gap":
            if e.get("pave"): add('R(%f, %f, %f, 1.2, "%s");' % (e["x0"], gy, e["x1"] - e["x0"], GC["포장"]))
            if e.get("brk"):
                xm = (e["x0"] + e["x1"]) / 2
                add('P([[%f, %f], [%f, %f], [%f, %f], [%f, %f]], false, null, "#555555", 0.7);' % (xm - 2.2, gy - 2.0, xm - 0.6, gy - 5.0, xm + 0.6, gy + 1.0, xm + 2.2, gy - 2.0))
            continue
        if e["t"] != "open": continue
        c = GC[e["kind"]]
        if e["kind"] == "도로":        # 차도: 대지 레벨보다 DROP 낮은 노면(위는 비움)
            roads.append((e["x0"], e["x1"]))
            add('R(%f, %f, %f, %f, "#ffffff");' % (e["x0"], gy, e["x1"] - e["x0"], DROP))
            add('R(%f, %f, %f, 1.2, "%s");' % (e["x0"], gy + DROP, e["x1"] - e["x0"], ROAD))
            add('P([[%f, %f], [%f, %f]], false, null, "#ffffff", 0.5, [2.0, 1.6]);' % (e["x0"] + 1.2, gy + DROP + 0.6, e["x1"] - 1.2, gy + DROP + 0.6))
        elif e.get("center"):
            c0, c1 = e["center"]
            add('R(%f, %f, %f, 1.2, "#86C85F"); R(%f, %f, %f, 1.2, "#E9E4D6"); R(%f, %f, %f, 1.2, "#86C85F");' % (
                e["x0"], gy, c0 * SC, e["x0"] + c0 * SC, gy, (c1 - c0) * SC, e["x0"] + c1 * SC, gy, (e["w"] - c1) * SC))
        else:
            add('R(%f, %f, %f, 1.2, "%s");' % (e["x0"], gy, e["x1"] - e["x0"], c))
        for tx in e.get("trees", ()):
            add('tree2(%f, %f, %f, "%s");' % (e["x0"] + tx * SC, gy, 2.6 * SC, rnd.choice(["#6DBE4B", "#5FB043", "#74C352"])))
        if e.get("real"):
            xm = (e["x0"] + e["x1"]) / 2
            add('P([[%f, %f], [%f, %f], [%f, %f], [%f, %f]], false, null, "#555555", 0.7);' % (xm - 2.0, gy - 2.0, xm - 0.6, gy - 5.0, xm + 0.6, gy + 1.0, xm + 2.0, gy - 2.0))
    # 지반 윤곽선 — 대지 레벨, 차도 구간만 DROP 아래로 꺾인다
    add('layer("지반선");')
    prof = [(0.0, gy)]
    for r0, r1 in sorted(roads):
        prof += [(r0, gy), (r0, gy + DROP), (r1, gy + DROP), (r1, gy)]
    prof.append((PW, gy))
    add('P(%s, false, null, "#1a1a1a", 1.1);' % js(prof))
    # ── 건축물
    add('layer("건축물");')
    tops = {}; used = []
    for e in seq:
        if e["t"] != "bld": continue
        X0 = e["x0"]; top = 0.0
        for (a, b, z0, z1, cat) in e["rects"]:
            c = COL[cat]; xa_, xb_ = X0 + a * SC, X0 + b * SC
            if isinstance(c, tuple): add('GR(%f, %f, %f, %f, "%s", "%s");' % (xa_, Y(z1), xb_ - xa_, (z1 - z0) * SC, c[0], c[1]))
            else: add('R(%f, %f, %f, %f, "%s");' % (xa_, Y(z1), xb_ - xa_, (z1 - z0) * SC, c))
            fl = [f for f in e.get("floors", ()) if z0 < f < z1] if e.get("floors") else list(np.arange(z0 + FH.get(cat, 4.0), z1 - 0.3, FH.get(cat, 4.0)))
            for zz in fl:
                add('P([[%f, %f], [%f, %f]], false, null, "#ffffff", 0.5, null, 75);' % (xa_ + 0.4, Y(zz), xb_ - 0.4, Y(zz)))
            top = max(top, z1)
            if LEG[cat] not in [u[1] for u in used]: used.append((c, LEG[cat]))
        if e.get("hip"):
            w_ = e["w"]; pk = e["hip"]
            add('P([[%f, %f], [%f, %f], [%f, %f]], true, "#6E4A3A", null);' % (X0 - 0.9 * SC, Y(9.0), X0 + w_ / 2 * SC, Y(pk), X0 + (w_ + 0.9) * SC, Y(9.0)))
            top = pk
        if e.get("canopy"):
            a, b, z0, z1 = e["canopy"]; add('R(%f, %f, %f, %f, "#5F656D");' % (X0 + a * SC, Y(z1), (b - a) * SC, (z1 - z0) * SC))
            top = max(top, z1)
        if e.get("court"):
            a, b = e["court"]; add('R(%f, %f, %f, 1.2, "#9ED67A");' % (X0 + a * SC, gy, (b - a) * SC))
            add('tree2(%f, %f, %f, "#6DBE4B");' % (X0 + (a + b) / 2 * SC, gy, 2.4 * SC))
        if e.get("real"):          # 축약 끊김(흰 이중 사선)
            xm = e["x0"] + (e["x1"] - e["x0"]) * 0.72; zt = max(r[3] for r in e["rects"])
            for d in (-1.0, 1.0):
                add('P([[%f, %f], [%f, %f]], false, null, "#ffffff", 1.6);' % (xm + d - 1.6, gy - 0.2, xm + d + 1.6, Y(zt) + 0.2))
        tops[e["name"]] = top
    for e in seq:
        if e.get("bridge"):
            a, b, z0, z1 = e["bridge"]; add('R(%f, %f, %f, %f, "#5F656D");' % (e["x0"] + a * SC, Y(z1), (b - a) * SC, (z1 - z0) * SC))
    # 그레이트 코트 유리 지붕 — 절단 실측(s, z): 역사 용마루 14.5 m → 18.6 m → 지역문화원 벽 17.0 m
    for i_, e in enumerate(seq):
        if not e.get("glass"): continue
        st = seq[i_ - 1]
        GL = [(120.5, 14.5), (123.5, 15.4), (126.5, 16.2), (129.5, 17.0), (132.5, 17.6), (135.5, 18.1), (138.5, 18.4), (141.5, 18.6), (144.5, 18.6),
              (147.5, 18.5), (150.5, 18.2), (153.5, 17.8), (156.5, 17.3), (158.6, 17.0)]
        X = lambda s: st["x0"] + (s - 111.1) * SC
        pts = [(X(s), Y(z)) for s, z in GL]
        under = [(X(130.7), gy), (X(130.7), Y(17.2))] + [p for (s, z), p in zip(GL, pts) if s > 130.7] + [(X(158.6), gy)]
        add("P(%s, true, \"#CDEBF7\", null, 0, null, 60);" % js(under))
        add("P(%s, false, null, \"#4A9CC4\", 1.8);" % js(pts))
        for s in np.arange(123, 158, 3.0):
            z = float(np.interp(s, [g[0] for g in GL], [g[1] for g in GL]))
            add('P([[%f, %f], [%f, %f]], false, null, "#4A9CC4", 0.5);' % (X(s), Y(z), X(s), Y(z) + 1.4))
        tops[e["name"]] = 18.6
        used.append(("#CDEBF7", "유리 지붕"))
    if any(e.get("canopy") or e.get("bridge") for e in seq): used.append(("#5F656D", "브리지·캐노피"))
    # ── 동선(붉은 점선)
    add('layer("동선");')
    yr = gy - 2.2
    add('P([[%f, %f], [%f, %f]], false, null, "%s", 0.9, [2.8, 2.0]);' % (xa + 1.5, yr, xb - 1.5, yr, RED))
    for e in seq:
        if e["t"] != "bld": continue
        a0 = min(r[0] for r in e["rects"]); cur = 0.0
        for r in sorted([r for r in e["rects"] if r[0] == a0], key=lambda r: r[2]):
            if r[2] <= cur + 0.6: cur = max(cur, r[3])
        xv = e["x0"] + a0 * SC + 2.0
        add('P([[%f, %f], [%f, %f]], false, null, "%s", 0.9, [2.8, 2.0]); dot(%f, %f); dot(%f, %f);' % (xv, yr, xv, Y(cur) + 2.2, RED, xv, yr, xv, Y(cur) + 2.2))
    for e in seq:
        if e.get("bridge"):
            a, b, z0, z1 = e["bridge"]; ym = Y((z0 + z1) / 2)
            add('P([[%f, %f], [%f, %f]], false, null, "%s", 0.9, [2.8, 2.0]); dot(%f, %f); dot(%f, %f);' % (e["x0"] - 0.8, ym, e["x1"] + 0.8, ym, RED, e["x0"] - 0.8, ym, e["x1"] + 0.8, ym))
    if key == "V":
        e = pos["실내체험관"]; ym = Y(10)
        add('P([[%f, %f], [%f, %f]], false, null, "%s", 0.9, [2.8, 2.0]); dot(%f, %f); dot(%f, %f);' % (e["x0"] + 4, ym, e["x1"] - 4, ym, RED, e["x0"] + 4, ym, e["x1"] - 4, ym))
    # ── 층별 용도 라벨(블록 안, 같은 용도는 한 번)
    add('layer("용도 라벨");')
    for e in seq:
        if e["t"] != "bld": continue
        done = set(); amin = min(r[0] for r in e["rects"])
        order = sorted(e["rects"], key=lambda r: -(r[1] - r[0]) * (r[3] - r[2]))
        if e.get("labrect"): order = [e["labrect"]] + order
        for (a, b, z0, z1, cat) in order:
            if cat in done: continue
            xl = e["x0"] + a * SC + (3.6 if a == amin else 0.6); xr = e["x0"] + b * SC - 0.6
            if e.get("real"): xr = min(xr, e["x0"] + (e["x1"] - e["x0"]) * 0.72 - 3.0)      # 끊김 표시 왼쪽
            col = "#7a3b12" if cat == "주거" else "#ffffff"
            fl = [f for f in e.get("floors", ()) if z0 < f < z1] if e.get("floors") else list(np.arange(z0 + FH.get(cat, 4.0), z1 - 0.3, FH.get(cat, 4.0)))
            bd = [z0] + [float(f) for f in fl] + [z1]; zc = (z0 + z1) / 2
            fz = sorted([(bd[i], bd[i + 1]) for i in range(len(bd) - 1) if (bd[i + 1] - bd[i]) * SC >= 4.6], key=lambda q: abs((q[0] + q[1]) / 2 - zc))
            if fz and len(bd) > 2:
                add('if (!band(%f, %f, %f, %f, %s, "%s", 12)) band(%f, %f, %f, %f, %s, "%s", 12);' % (xl, xr, Y(fz[0][1]) + 0.3, Y(fz[0][0]) - 0.3, js(e.get("use", {}).get(cat, USE[cat])), col, xl, xr, Y(z1), Y(z0), js(e.get("use", {}).get(cat, USE[cat])), col))
            else:
                add('band(%f, %f, %f, %f, %s, "%s", 12);' % (xl, xr, Y(z1), Y(z0), js(e.get("use", {}).get(cat, USE[cat])), col))
            done.add(cat)
    # ── 사람
    add('layer("사람");')
    PC = ["#4a4a4a", "#5a5a5a", "#E8776A", "#2D6CB0", "#3d3d3d"]
    for e in seq:
        if e["t"] == "open" and e["kind"] in ("선형", "광장", "공원", "마당", "보행"):
            n = 4 if e.get("hero") else (3 if e["w"] > 35 else (2 if e["w"] > 15 else 1))
            span = e["x1"] - e["x0"]
            for j in range(n):
                xp = e["x0"] + span * (j + 0.5) / n + rnd.uniform(-1.0, 1.0)
                add('person(%f, %f, %f, "%s", %f);' % (xp, gy, rnd.uniform(3.3, 3.8), rnd.choice(PC), rnd.uniform(-0.4, 0.6)))
    # ── 치수(지반 띠): 외부공간 실제 폭, 건물 폭, 축약 요소는 실제 길이(회색)
    add('layer("치수");')
    yd = gy + 5.0
    for e in seq:
        hero = e.get("hero")
        if e["name"] in DIM[key]: txt = DIM[key][e["name"]] + " m"; col = "#1f6b2a" if hero else "#2b2b2b"; fw = "ExtraBold" if hero else "Bold"
        elif e.get("real"): txt = "실제 %d m" % e["real"]; col = "#7a7a7a"; fw = "Medium"
        elif e["t"] == "bld": txt = ("%.1f" % e["w"]).rstrip("0").rstrip(".") + " m"; col = "#4a4a4a"; fw = "Medium"
        else: continue
        sz = 13 if hero else 10
        if tw(txt, sz) > e["x1"] - e["x0"] + 2:
            if e.get("real"): txt = "%d m" % e["real"]
            if tw(txt, sz) > e["x1"] - e["x0"] + 6: continue
        add('P([[%f, %f], [%f, %f]], false, null, "#555555", 0.45); P([[%f, %f], [%f, %f]], false, null, "#555555", 0.45); P([[%f, %f], [%f, %f]], false, null, "#555555", 0.45);' % (
            e["x0"] + 0.25, yd, e["x1"] - 0.25, yd, e["x0"] + 0.25, yd - 1.0, e["x0"] + 0.25, yd + 1.0, e["x1"] - 0.25, yd - 1.0, e["x1"] - 0.25, yd + 1.0))
        add('T(%f, %f, %s, %d, "Pretendard-%s", "%s", "c");' % ((e["x0"] + e["x1"]) / 2, yd + (4.4 if hero else 3.4), js(txt), sz, fw, col))
    # ── 조닝 띠: 요소 묶음 = 영역(강조 문구 아래, 단면과 같은 x 범위)
    add('layer("조닝 띠");')
    for zname, ea, eb, zc in ZONES[key]:
        za, zb = pos[ea]["x0"] + 0.5, pos[eb]["x1"] - 0.5
        add('R(%f, %f, %f, 7.6, "%s");' % (za, ZY, zb - za, zc))
        add('P([[%f, %f], [%f, %f]], false, null, "%s", 0.6); P([[%f, %f], [%f, %f]], false, null, "%s", 0.6);' % (za + 0.3, ZY + 7.6, za + 0.3, ZY + 10.4, zc, zb - 0.3, ZY + 7.6, zb - 0.3, ZY + 10.4, zc))
        add('band(%f, %f, %f, %f, %s, "#ffffff", 12);' % (za, zb, ZY, ZY + 7.6, js(zname)))
    # ── 설계 의도 문구(위, 층 배치)
    add('layer("설계 의도");')
    ytop = gy - max(tops.values()) * SC
    items = []
    for names, ttl, desc in INTENT[key]:
        names = names if isinstance(names, list) else [names]
        es = [pos[n] for n in names if n in pos]
        assert es, names
        xa_, xb_ = min(e["x0"] for e in es), max(e["x1"] for e in es)
        hero = any(e.get("hero") for e in es); keyf = hero or any(e.get("key") for e in es)
        zt = max(tops.get(e["name"], 0.0) for e in es)
        if zt > 0: ay = Y(zt) - 1.0
        elif any(e.get("trees") for e in es): ay = gy - 3.1 * 2.6 * SC - 1.2
        else: ay = gy - 6.0
        b0 = es[0]
        if b0["t"] == "bld":
            c = COL[max(b0["rects"], key=lambda r: (r[1] - r[0]) * (r[3] - r[2]))[4]]; col = c[0] if isinstance(c, tuple) else c
        else: col = {"도로": "#4a4a4a", "포장": "#6b6b6b"}.get(b0["kind"], "#2f8f3a")
        tsz = 14 if hero else (12.5 if keyf else 12)
        w_ = max(tw(ttl, tsz), tw(desc, 10, "Medium")) + 3
        items.append(dict(cx=(xa_ + xb_) / 2, xa=xa_, xb=xb_, w=w_, ttl=ttl, desc=desc, tsz=tsz, ay=ay, group=len(es) > 1, col=col))
    tiers = []
    for it in sorted(items, key=lambda d: d["cx"]):
        lft = min(max(it["cx"] - it["w"] / 2, 5), PW - 5 - it["w"]); rgt = lft + it["w"]
        t_ = 0
        while True:
            if t_ >= len(tiers): tiers.append([])
            if all(rgt + 2.5 < a or lft - 2.5 > b for a, b in tiers[t_]): break
            t_ += 1
        tiers[t_].append((lft, rgt)); it["tier"] = t_; it["tx"] = (lft + rgt) / 2
    ntier = len(tiers); step = min(19.0, (ytop - 8.5 - (ZY + 23.0)) / max(1, ntier - 1)) if ntier > 1 else 12.5
    print(key, "tiers", ntier, "step %.1f" % step)
    for it in items:
        ty = ytop - 8.5 - it["tier"] * step
        if it["group"]:
            add('P([[%f, %f], [%f, %f], [%f, %f], [%f, %f]], false, null, "#333333", 0.6);' % (it["xa"] + 0.3, it["ay"], it["xa"] + 0.3, it["ay"] - 1.6, it["xb"] - 0.3, it["ay"] - 1.6, it["xb"] - 0.3, it["ay"]))
            ay = it["ay"] - 1.6
        else: ay = it["ay"]
        lx = it["cx"]; yb_ = ty + 6.4
        if abs(it["tx"] - lx) > 0.5:
            add('P([[%f, %f], [%f, %f], [%f, %f]], false, null, "#555555", 0.45);' % (lx, ay, lx, yb_ + 1.2, it["tx"], yb_))
        else:
            add('P([[%f, %f], [%f, %f]], false, null, "#555555", 0.45);' % (lx, ay, lx, yb_))
        add('E(%f, %f, 0.7, 0.7, "#555555", null);' % (lx, ay))
        add('T(%f, %f, %s, %f, "Pretendard-ExtraBold", "%s", "c");' % (it["tx"], ty - 1.4, js(it["ttl"]), it["tsz"], it["col"]))
        add('T(%f, %f, %s, 10, "Pretendard-Medium", "#4a4a4a", "c");' % (it["tx"], ty + 3.6, js(it["desc"])))
    # ── 방위·단면 기호
    add('layer("방위");')
    e0, e1 = cfg["ends"]; t = cfg["tag"]
    for side, xe, d in ((0, xa, 1), (1, xb, -1)):
        xc = xe + d * 3.4
        add('P([[%f, %f], [%f, %f]], false, null, "#A0237A", 0.6, [1.6, 1.2]);' % (xe, gy - 6.0, xe, gy + 11.0))
        add('E(%f, %f, 3.0, 3.0, "#A0237A", "#ffffff", 0.6); T(%f, %f, %s, 11, "Pretendard-Bold", "#ffffff", "c");' % (xc, gy + 14.6, xc, gy + 14.7, js(t + ("" if side == 0 else "′"))))
        add('T(%f, %f, %s, 15, "Pretendard-Light", "#5b5b5b", "%s");' % (xc + d * 4.6, gy + 14.6, js(e0 if side == 0 else e1), "l" if side == 0 else "r"))
    # ── 범례
    add('layer("범례");')
    add("var lx = 12;")
    for c, lab in used:
        if isinstance(c, tuple): add('GR(lx, 217.6, 4.2, 3.4, "%s", "%s");' % c)
        else: add('R(lx, 217.6, 4.2, 3.4, "%s");' % c)
        add('var tl = T(lx + 5.4, 219.3, %s, 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 4.2;' % js(lab))
    add('P([[lx, 219.3], [lx + 7, 219.3]], false, null, "%s", 0.9, [2.8, 2.0]); dot(lx + 7, 219.3); var tl = T(lx + 9.5, 219.3, %s, 10, "Pretendard-Medium", "#333333", "l"); lx += 9.5 + W(tl) + 4.2;' % (RED, js("보행·수직 동선")))
    lw = 12 + sum(5.4 + tw(lab, 10, "Medium") + 4.2 for c, lab in used) + 9.5 + tw("보행·수직 동선", 10, "Medium") + 4.2
    yn = 219.3 if lw + 6 + tw(NOTE[key], 10, "Medium") < PW - 12 else 213.6
    add('T(%f, %f, %s, 10, "Pretendard-Regular", "#555555", "r");' % (PW - 12, yn, js(NOTE[key])))
    # ── 저장
    ai = os.path.join(OUTD, cfg["file"] + ".ai").replace("\\", "/"); pdf = os.path.join(OUTD, cfg["file"] + ".pdf").replace("\\", "/"); png = os.path.join(OUTD, cfg["file"] + ".png").replace("\\", "/")
    add(r"""
var o = new ExportOptionsPNG24(); o.artBoardClipping = true; o.horizontalScale = 333.333; o.verticalScale = 333.333; o.antiAliasing = true; o.transparency = false;
doc.exportFile(new File(%s), ExportType.PNG24, o);
doc.saveAs(new File(%s), new IllustratorSaveOptions());
var po = new PDFSaveOptions(); po.preserveEditability = false; po.compatibility = PDFCompatibility.ACROBAT7;
doc.saveAs(new File(%s), po);
doc.close(SaveOptions.DONOTSAVECHANGES);
"saved " + %s;""" % (js(png), js(ai), js(pdf), js(cfg["file"])))
    print(key, "total %.1f m -> %.0f mm, x %.1f-%.1f" % (total, total * SC, xa, xb))
    return "\n".join(o)


def run(key):
    src = build(key)
    jsx = os.path.join(CL, "s3_%s.jsx" % key)
    open(jsx, "w", encoding="utf-8-sig").write(src)
    ps = "$app = New-Object -ComObject 'Illustrator.Application'; $app.UserInteractionLevel = -1; $app.DoJavaScriptFile('%s')" % jsx.replace("'", "''")
    r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1200)
    print(key, r.stdout.strip()[-200:], r.stderr.strip()[:1500])


if __name__ == "__main__":
    for k in (sys.argv[1:] or ["V", "H", "Dg"]): run(k)
