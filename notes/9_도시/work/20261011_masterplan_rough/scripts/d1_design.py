"""D1 사용자 러프 배치(2026-10-11, 라이노 aardvark 선택 222개) → 마스터플랜 설계 데이터
- 고정 입력: 러프 선을 면 분할한 결과(d0_faces.py → data/faces.pkl)와 러프 매스 외곽선(rough_sel.json)
- 획지·공원·가로·건축물·식재를 정의하고, 러프 메모를 도시계획·지구단위계획 용어로 옮긴다
- 좌표: 로컬 m = 라이노 러프 프레임 − (X0, Y0). 러프 프레임 = v3 계획 프레임 − (517.0557, 0)
출력: data/design.pkl (shapely), data/design.json (라이노 러프 프레임 좌표)"""
import json, os, pickle, math, random
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
FC = pickle.load(open(os.path.join(D, "faces.pkl"), "rb"))
R = json.load(open(os.path.join(D, "rough_sel.json"), encoding="utf-8"))
B, F, X0, Y0 = FC["B"], FC["faces"], FC["X0"], FC["Y0"]


def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []


def clean(g, a=1.0):
    """면적 a㎡ 미만 조각 제거"""
    ps = [p for p in polys(g.buffer(0)) if p.area >= a]
    return unary_union(ps) if ps else Polygon()


def curve(i):
    return [(p[0] - X0, p[1] - Y0) for p in R["curves"][i]["pts"]]


def poly_of(i):
    return Polygon(curve(i)).buffer(0)


# ── 1. 가로망 ─────────────────────────────────────────────
# v2: 도로·보도는 사용자가 라이노에서 선택한 객체를 그대로 쓴다(data/road_sel.json, 7개 = 도로 면 2·보도 면 3·보도 외곽선 2)
#     선택 객체는 러프 프레임 + (DXR, 0) 위치 — 경계 범위로 맞춘 평행이동량
RS = json.load(open(os.path.join(D, "road_sel.json"), encoding="utf-8"))
DXR = 1080.496306963265


def brep_poly(o):
    outer = [Polygon([(x - X0 - DXR, y - Y0) for x, y, z in pts]).buffer(0) for lt, pts in o["loops"] if "Outer" in lt]
    inner = [Polygon([(x - X0 - DXR, y - Y0) for x, y, z in pts]).buffer(0) for lt, pts in o["loops"] if "Inner" in lt]
    g = unary_union(outer)
    return (g.difference(unary_union(inner)) if inner else g), inner


RD = [brep_poly(o)[0] for o in RS["objs"] if "loops" in o and o["layer"].endswith("::도로")]
WK = [brep_poly(o) for o in RS["objs"] if "loops" in o and o["layer"].endswith("::보도")]
ROAD_N = clean([g for g in RD if g.bounds[1] > 700][0])                    # 북측 진입도로(폭 13 m) — 사용자 객체 그대로
RING = clean([g for g in RD if g.bounds[1] < 700][0])                      # 동서 도로 20 m + 동측·남측 외곽도로 — 사용자 객체 그대로
ROAD_EW = clean(RING.intersection(box(80, 333.7, 392.0, 353.7)))
ROAD_O = clean(RING.difference(ROAD_EW))
ROADS = clean(unary_union([ROAD_N, RING]))
NET = clean(unary_union([g for g, _ in WK]))                              # 보도(보행망) — 사용자 객체 그대로, 아래에서 축·공원으로 나눈다
HOLES = [h for _, hs in WK for h in hs]                                     # 보도 객체의 구멍 = 가구(모서리 모따기 없음)
def hole_like(face):
    return max(HOLES, key=lambda h: h.intersection(face).area)
for k in (11, 12, 13, 14, 15, 2):                                           # 가구 면을 사용자 보도 객체의 구멍으로 교체(모따기 삼각형이 가구로 들어온다)
    F[k] = hole_like(F[k]).buffer(0)
AX_NS = clean(NET.intersection(box(255.9, 291.2, 285.9, 772.1)).difference(ROADS))   # 남북 중앙 보행축(폭 30 m)
CROSS = clean(AX_NS.intersection(box(255.9, 476.3, 285.9, 516.3)))      # 중앙 교차광장
AX_NS = clean(AX_NS.difference(CROSS))
GR_EW = clean(NET.intersection(box(100, 476.3, 420, 516.3)).difference(unary_union([AX_NS, CROSS, ROADS])))  # 동서 보행녹지축(폭 40 m)
PATH8 = clean(NET.intersection(box(100, 635.2, 420, 643.2)).difference(unary_union([AX_NS, ROADS])))        # 보행자전용도로(폭 8 m)
v = np.array([0.5394, 0.842])                                             # 사선 보행축 방향(러프 사선 두 선은 평행, 간격 20.0 m)
A0, A1 = np.array([118.5, 76.7]) - 80 * v, np.array([255.9, 291.2])
B0, B1 = np.array([131.2, 59.5]) - 80 * v, np.array([285.9, 300.9])
PBAND = Polygon([tuple(A0), tuple(A1), (255.9, 333.7), (285.9, 333.7), tuple(B1), tuple(B0)])
GATE = clean(F[8].intersection(Point(116, 60).buffer(30)))              # 관문광장(러프 '관광객 주출입구')
PROM = clean(F[8].intersection(PBAND).difference(unary_union([AX_NS, GATE, ROADS])))
WALK = clean(NET.difference(unary_union([ROADS, AX_NS, CROSS, GR_EW, PATH8, PROM, GATE])), 2.0)  # 외곽 보도

# ── 2. 획지 ───────────────────────────────────────────────
F9_low = F[9].intersection(box(0, 0, 500, 771.1)); F9_top = F[9].difference(box(0, 0, 500, 771.1))
L5 = clean(F[14].intersection(unary_union([box(100, 600, 260, 640), box(222, 500, 260, 640)])))
P_C = clean(F[14].difference(L5))
SW = F[2]; L9 = clean(SW.intersection(box(0, 195, 400, 400))); L10 = clean(SW.difference(box(0, 195, 400, 400)))
L11 = clean(F[16].intersection(box(0, 0, 237.4, 400)))
SE = clean(unary_union([F[16].difference(box(0, 0, 237.4, 400)), F[0]]))


def split_x(y):                                                            # 근대역사관 동측 외벽선에서 11.5 m 띄운 평행선 → 북쪽은 x = 339.9 수직
    return 293.5 + (y - 205.9) / 1.539 if y < 277.3 else 339.9
cut = Polygon([(split_x(150), 150), (split_x(277.3), 277.3), (339.9, 400), (500, 400), (500, 150)])
L13 = clean(SE.intersection(cut)); L12 = clean(SE.difference(cut))

# 획지 코드: 지구단위계획 용도 구분(용지) / 지정용도(주용도) / 허용용도(권장)
LOTS = [
    dict(no=1, code="공청1", g=F[11], use="공공청사용지", name="공공청사", main="공공청사(도시·군계획시설)", allow="업무시설(공공업무), 문화 및 집회시설(시민홀)", cat="공공업무"),
    dict(no=2, code="주차1", g=F[17], use="주차장용지", name="공공청사 부설주차장", main="주차장(주차전용건축물)", allow="공원 이용자 주차 겸용", cat="주차"),
    dict(no=3, code="체육1", g=clean(unary_union([F[10], F[1]])), use="체육시설용지", name="생활체육시설", main="운동시설(생활체육관)", allow="제1종 근린생활시설(편의시설)", cat="생활SOC"),
    dict(no=4, code="공주1", g=clean(F9_low), use="공동주택용지", name="청년·신혼 공공임대주택", main="공동주택(아파트·연립)", allow="주민공동시설, 제1종 근린생활시설", cat="주거"),
    dict(no=5, code="업무1", g=L5, use="업무복합용지", name="공공업무·청년창업지원", main="업무시설(공공업무), 청년창업지원시설", allow="제2종 근린생활시설, 교육연구시설", cat="업무·창업"),
    dict(no=6, code="생활1", g=F[12], use="생활문화복합용지", name="생활문화·돌봄 복합", main="문화 및 집회시설, 노유자시설", allow="의료시설(보건), 제1·2종 근린생활시설", cat="문화"),
    dict(no=7, code="공예1", g=F[15], use="문화특화용지", name="전통공예 특화", main="공방·체험시설, 전시장", allow="판매시설(공예품), 업무시설(운영)", cat="창작"),
    dict(no=8, code="창작1", g=F[13], use="문화특화용지", name="창작·체험(아티스트 레지던시)", main="창작공간(제작동), 체험시설", allow="숙박형 체류시설(레지던시), 제2종 근린생활시설", cat="창작"),
    dict(no=9, code="역사1", g=L9, use="역사문화시설용지", name="구 경주역 어댑티브 리유즈", main="문화시설(근대문화유산 활용), 지역문화원", allow="제1·2종 근린생활시설(소상공인 상생)", cat="역사"),
    dict(no=10, code="관광1", g=L10, use="관광편의시설용지", name="관광안내·방문자지원", main="관광안내소, 관광편의시설", allow="제1종 근린생활시설", cat="방문자"),
    dict(no=11, code="판매1", g=L11, use="판매시설용지", name="관문 가로상가", main="판매시설, 제1·2종 근린생활시설", allow="문화 및 집회시설(소규모 공연)", cat="판매"),
    dict(no=12, code="문화1", g=L12, use="문화시설용지", name="근대역사관", main="문화시설(전시장·박물관)", allow="문화 및 집회시설(기획전시·팝업)", cat="문화"),
    dict(no=13, code="교통1", g=L13, use="주차장·교통시설용지", name="공유주차장·모빌리티 허브", main="주차장(주차전용건축물), 교통편의시설", allow="공유 모빌리티 대여·환승", cat="주차"),
]
PARKS = [
    dict(key="A", g=F[7], kind="근린공원", name="북측 근린공원"),
    dict(key="B", g=clean(F9_top), kind="근린공원", name="체육공원"),
    dict(key="C", g=P_C, kind="근린공원", name="중앙 근린공원"),
]
OPEN = [
    dict(key="D", g=unary_union([GR_EW, CROSS]), kind="보행자전용도로·광장", name="동서 선형공원·가로광장(폭 40m)"),
    dict(key="E", g=AX_NS, kind="보행자전용도로", name="남북 중앙 보행축(폭 30m)"),
    dict(key="F", g=unary_union([PROM, GATE]), kind="보행자전용도로·광장", name="관문광장·사선 보행축(폭 20m)"),
]

for l in LOTS: l["g"] = clean(l["g"], 25.0)                               # 경계선 오차로 생긴 가는 조각 제거
for p in PARKS + OPEN: p["g"] = clean(p["g"], 25.0)

# ── 3. 건축물 ─────────────────────────────────────────────
CATS = {   # 범례 순서·색 — v2 파스텔 팔레트(참고: 여천역 조감도 — 상업 분홍·주거 베이지·업무 하늘색 계열)
    "공공업무": ("#8EA9D8", "공공청사·공공업무"), "업무·창업": ("#F3A583", "업무·청년창업"), "문화": ("#A8D5E2", "문화·집회"),
    "창작": ("#C7B3E0", "창작·공방"), "판매": ("#F5B7C5", "판매·근린생활"), "생활SOC": ("#9FD8C2", "생활체육·복지"),
    "주거": ("#F3E1B9", "주거"), "역사": ("#C98B5E", "역사유산(구 경주역사)"), "방문자": ("#D8DDE2", "관광·방문자"), "주차": ("#B9BCC0", "주차·교통")}
FH = {"주거": 3.0, "주차": 3.2, "역사": 4.5}                                # 층고(m) — 나머지 4.0


def rect(x0, y0, x1, y1): return box(x0, y0, x1, y1)


MASS = []


def add(lot, name, term, cat, floors, g, src, adj="", retail=False, roof="plain"):
    g = clean(g, 5.0).simplify(0.02, preserve_topology=True)               # 거의 겹친 꼭짓점(길이 0 변) 제거 — 라이노 압출 실패 방지
    fh = FH.get(cat, 4.0)
    MASS.append(dict(lot=lot, name=name, term=term, cat=cat, floors=floors, fh=fh, h=round(floors * fh, 2), g=g, src=src, adj=adj, retail=retail, roof=roof))


# 1 공공청사 — ㄱ자: 동측 본관 7층 + 북측 민원동 5층(러프 사각형 2개 그대로)
add(1, "공공청사 본관", "공공청사", "공공업무", 7, rect(227.1, 653.6, 252.1, 753.6), "러프 #101 25×100", "최고 7층 적용")
add(1, "공공청사 민원·시민홀동", "공공청사(민원실·시민홀)", "공공업무", 5, rect(118.5, 733.6, 227.1, 753.6), "러프 #10 108.6×20", "5층, 1층 민원실")
# 2 부설주차장 — 오각형 획지에서 4 m 후퇴, 옥상 녹화
add(2, "공공청사·기관 직원 주차장동", "주차전용건축물", "주차", 4, F[17].buffer(-4.0, join_style=2), "러프 #137 '공공청사, 기관 직원 주차장동'", "획지 경계 4 m 후퇴, 4층(3.2 m)")
# 3 생활체육시설
add(3, "생활체육관·편의시설", "운동시설(생활체육관)·근린생활시설", "생활SOC", 4, rect(300.2, 779.0, 350.2, 809.0), "러프 #18 50×30 '체육,생활,편의시설'", "4층")
# 4 공동주택 — 판상 8동, 인동간격 24 m, 5층
for i, (x0, y0) in enumerate([(286.5, 746.2), (346.4, 746.2), (286.5, 712.2), (346.4, 712.2), (286.5, 678.2), (346.4, 678.2), (286.5, 644.2), (346.4, 644.2)]):
    add(4, "주거동 %d" % (i + 1), "공동주택(청년·신혼 공공임대)", "주거", 5, rect(x0, y0, x0 + 48, y0 + 10), "러프 48×10 판상(32세대·총5층·인동간격 24m)", "그대로", retail=(y0 < 650))
# 5 공공업무·청년창업지원 — ㄱ자 분절: 북측 유관기관 업무 5층 + 동측 청년창업지원센터 4층
add(5, "공공기관 업무동", "업무시설(공공업무)", "공공업무", 5, rect(172.4, 605.3, 251.8, 629.9), "러프 #111 북측 날개 '공공기관 업무'", "5층")
add(5, "청년창업지원센터", "청년창업지원시설(업무시설)", "업무·창업", 4, rect(226.9, 538.6, 251.8, 605.3), "러프 #111 동측 날개 '청년지원 클러스터'", "4층, 1층 공유 라운지", retail=True)
# 6 생활문화·돌봄 복합
add(6, "복합문화센터", "문화 및 집회시설", "문화", 4, poly_of(109), "러프 #109 '복합문화시설 1층 1200·2층 800'", "러프 2층 → 4층(지침 4~5층)")
add(6, "건강·돌봄센터", "노유자시설·의료시설(보건)", "생활SOC", 4, rect(338.5, 619.1, 378.5, 634.1), "러프 #113 '건강, 돌봄센터 2F' 40×15", "러프 2층 → 4층")
add(6, "생활가로 상가", "제1·2종 근린생활시설", "판매", 4, rect(320.7, 517.4, 387.5, 527.4), "러프 #20 '상업' 67×10", "4층, 1층 가로상점", retail=True)
# 7 전통공예 특화 — ㄷ자 중정(근린공원)을 세 동이 감싼다
add(7, "공방동", "공방(제2종 근린생활시설)", "창작", 4, rect(120.7, 363.3, 136.9, 440.8), "러프 #0 16×77(메모 없음)", "공방동으로 해석, 4층")
add(7, "전통문화 공방·체험·전시동", "공방·체험시설·전시장", "창작", 4, rect(228.2, 390.9, 253.1, 459.6), "러프 '전통 문화, 문화재 제작 공방, 체험, 전문전시실'", "4층")
add(7, "실내 공예마켓·운영동", "판매시설(공예품)·업무시설(운영·작품관리)", "판매", 4, rect(161.9, 362.5, 253.1, 383.2), "러프 '실내 공예마켓 / 운영·작품관리' 91×21", "4층, 1층 마켓", retail=True)
# 8 창작·체험(아티스트 레지던시)
add(8, "작가 교류·행사동", "문화 및 집회시설(집회장)", "문화", 4, Polygon([(318, 425.7), (318, 474.2), (305.5, 474.2), (288, 456.8), (288, 425.7)]), "러프 #140 '작가 교류·행사실'", "4층")
add(8, "레지던시 가로상가", "제2종 근린생활시설", "판매", 4, rect(321.4, 463.7, 385.6, 473.7), "러프 #1 '상업' 64×10", "4층, 1층 가로상점", retail=True)
add(8, "실내 체험관", "체험시설(문화 및 집회시설)", "문화", 4, rect(288, 359.8, 318, 418.7), "러프 #141 '실내 체험관 3200×3층 80×40'(도면 30×59)", "도면 외곽 유지, 3층 → 4층")
for i, (x0, y0) in enumerate([(332.8, 433.1), (332.9, 397.2), (332.9, 364.1)]):
    add(8, "레지던시 제작동 %d" % (i + 1), "창작공간(공방)", "창작", 4, rect(x0, y0, x0 + 15, y0 + 25), "러프 '제작동 2층 25×15'", "러프 2층 → 4층")
for i, (x0, y0) in enumerate([(366.4, 434.0), (366.4, 399.0), (366.4, 365.9)]):
    add(8, "레지던시 거주동 %d" % (i + 1), "숙박형 체류시설(작가 레지던시)", "주거", 5, rect(x0, y0, x0 + 10, y0 + 25), "러프 '거주동 2층 25×10'", "러프 2층 → 5층(3.0 m)")
# 9 구 경주역 어댑티브 리유즈(유리 지붕 중정 = 그레이트 코트)(참고: 도쿄역 마루노우치 역사 복원, 대영박물관 그레이트 코트)
#   역사 장축 좌표(a: 북동 방향 장축, b: 남동 방향 = 역사 배면 쪽). 역사 a 0~88.4, b −16.1(정면 중앙 현관)~8.1(배면)
ST = poly_of(8)
o = np.array([150.5, 228.2]); ua = np.array([48.1, 74.1]) / 88.35; vb = np.array([39.9, -25.9]) / 47.57
def ab(a, b): p = o + a * ua + b * vb; return (float(p[0]), float(p[1]))
def quad(a0, a1, b0, b1): return Polygon([ab(a0, b0), ab(a1, b0), ab(a1, b1), ab(a0, b1)])
bst = max(float(np.dot(np.array(c) - o, vb)) for c in ST.exterior.coords)    # 역사 배면 b
AC = 48.5                                                                      # 정면 중앙 현관(a 42~55)의 중심 = 구성 대칭축
add(9, "구 경주역사", "근대문화유산 활용 문화시설(존치·복원)", "역사", 2, ST, "러프 #8 기존 역사 외곽(1,403㎡)", "외곽 존치·복원, 2층(층고 4.5 m) + 모임지붕(경사 33°)", roof="hip")
add(9, "지역문화원 본동", "문화시설(지역문화원)·제1·2종 근린생활시설", "문화", 5, quad(-3, 100, 36, 50),
    "러프 #9 '경주문화원 위치 이동 및 지역 소상공인, 성동시장연계 클러스터' 88×48", "역사 배후 ㄷ자 중 본동(폭 14 m·길이 103 m), 5층, 1층 소상공인 점포", retail=True)
add(9, "소상공인 상생동(남)", "제1·2종 근린생활시설(성동시장 연계 점포·공방)", "판매", 5, quad(-3, 9, 12, 36.6), "러프 #9 동상", "ㄷ자 남측 날개(12×24 m), 5층, 역사 끝과 8 m 이격")
add(9, "소상공인 상생동(북)", "제1·2종 근린생활시설(성동시장 연계 점포·공방)", "판매", 5, quad(88, 100, 12, 36.6), "러프 #9 동상", "ㄷ자 북측 날개(12×24 m), 5층, 대칭축(현관 중심) 기준 대칭")
# 유리 지붕(그레이트 코트): 날개 사이 a 9~88, 역사 용마루(b ≈ −2.5)에서 본동 벽면(b 36)까지 볼트
GLASS = dict(a0=9.0, a1=88.0, b0=-2.5, b1=36.0, z0=14.4, z1=17.0, rise=2.8, o=o.tolist(), ua=ua.tolist(), vb=vb.tolist())
COURT = quad(9, 88, -2.5, 36).difference(ST.buffer(0.3))

# 10 관광안내
add(10, "관광지원센터", "관광안내소·관광편의시설", "방문자", 4, poly_of(6), "러프 #6 '관광지원센터 45×20 900 600'", "러프 2층 → 4층")
# 11 관문 가로상가
add(11, "관문 가로상가", "판매시설·제1종 근린생활시설", "판매", 4, poly_of(3), "러프 #3 '상업' 66×10", "4층, 1층 가로상점", retail=True)
# 12 근대역사관 — 평행사변형 외곽 유지, 폭 14 m 둘레형 + 중정
HALL = poly_of(5) if poly_of(5).area > 100 else F[0]
HALL = F[0]
add(12, "근대역사관", "문화시설(전시장·박물관)", "문화", 4, HALL.difference(HALL.buffer(-14.0, join_style=2)), "러프 #5 '근대역사관·지역예술인 전시장·상설전시장·기획전시·팝업'",
    "외곽 유지, 둘레형(폭 14 m)+중정, 4층")
# 13 공유주차장·모빌리티 허브
add(13, "공유주차장", "주차전용건축물", "주차", 5, rect(345.5, 251.7, 385.5, 331.7), "러프 #19 '공유 주차장 3200×3층 80×40'", "러프 3층 → 5층(3.2 m)", roof="solar")
add(13, "모빌리티 허브", "교통편의시설(공유 모빌리티 대여·환승)", "주차", 4, rect(321.0, 204.6, 386.2, 237.2), "러프 #4 '스쿠터, 4인용 탈것 대여소'", "4층, 1층 대여·환승", retail=False, roof="solar")

# 정합 확인: 건물은 자기 획지 안
LOTG = {l["no"]: l["g"] for l in LOTS}
for m in MASS:
    out = m["g"].difference(LOTG[m["lot"]].buffer(0.6)).area
    if out > 1.0: print("  ! 획지 밖 %.1f㎡ : %s" % (out, m["name"]))

# ── 4. 지면 요소(광장·텃밭·노외주차·중정) ─────────────────────
BLD0 = unary_union([m["g"] for m in MASS])
PLZ = [
    dict(kind="광장", name="청사 앞 시민광장", g=rect(150, 676, 222, 728)),
    dict(kind="노외주차", name="공공기관 방문객 노외주차장", g=rect(123.7, 614.2, 165.7, 628.2)),
    dict(kind="소공원", name="생활 소공원", g=rect(333.7, 577.3, 384.2, 610.1)),
    dict(kind="텃밭", name="공동체텃밭", g=rect(333.7, 535.7, 384.2, 568.4)),
    dict(kind="중정", name="공예 중정(근린공원)", g=rect(142, 390, 222, 455)),
    dict(kind="코트", name="그레이트 코트(유리 지붕 중정)", g=clean(COURT.difference(BLD0.buffer(0.3)))),
    dict(kind="광장", name="역전광장", g=clean(LOTG[9].buffer(-3.0).intersection(unary_union([quad(-12, 110, -62, -19), quad(40, 57, -120, -19)])).difference(ST.buffer(0.5)))),
    dict(kind="중정", name="근대역사관 중정", g=HALL.buffer(-14.0, join_style=2)),
    dict(kind="광장", name="레지던시 마당", g=rect(348.5, 362.5, 365.0, 460.0)),
    dict(kind="광장", name="관문 가로광장", g=clean(L11.intersection(Polygon([tuple(np.array([131.2, 59.5]) + 0 * v), tuple(np.array([131.2, 59.5]) + 196.8 * v),
         tuple(np.array([131.2, 59.5]) + 196.8 * v + np.array([0.842, -0.5394]) * 24), tuple(np.array([131.2, 59.5]) + np.array([0.842, -0.5394]) * 24)])).difference(BLD0.buffer(1.5)))),
]

# ── 5. 식재(포아송 원판 표본) ─────────────────────────────────
rnd = random.Random(11)
BLD = unary_union([m["g"] for m in MASS])
HARD = unary_union([BLD.buffer(3.0)] + [p["g"] for p in PLZ if p["kind"] in ("노외주차", "텃밭")])


def scatter(poly, gap, r=(3.0, 4.6), tries=4000, keep_out=None):
    poly = poly.difference(keep_out) if keep_out is not None else poly
    pts = []; mnx, mny, mxx, mxy = poly.bounds
    if poly.is_empty: return pts
    for _ in range(tries):
        x, y = rnd.uniform(mnx, mxx), rnd.uniform(mny, mxy)
        if not poly.contains(Point(x, y)): continue
        if any((x - a) ** 2 + (y - b) ** 2 < gap * gap for a, b, _ in pts): continue
        pts.append((x, y, rnd.uniform(*r)))
    return pts


def rows(line, step, off, r=3.2):
    out = []
    L = LineString(line); n = int(L.length // step)
    for k in range(n + 1):
        p = L.interpolate(k * step + (L.length - n * step) / 2)
        out.append((p.x + off[0], p.y + off[1], r))
    return out


TREES = {"park": [], "axis": [], "lot": [], "street": [], "linear": []}
for p in PARKS: TREES["park"] += scatter(p["g"].buffer(-2.5), 9.5, keep_out=HARD)
# 동서 선형공원(D): 남·북 각 2열(y 479.3·485.3 / 507.3·513.3), x 8 m 격자 — 경계에서 경계까지 같은 x열, 교차광장(x 255.9~285.9)은 비움
DG = [o_ for o_ in OPEN if o_["key"] == "D"][0]["g"]
for yy in (479.3, 485.3, 507.3, 513.3):
    for xx in np.arange(118.0, 404.0, 8.0):
        if 252.0 < xx < 290.0: continue
        pt = Point(xx, yy)
        if DG.buffer(-1.0).contains(pt): TREES["linear"].append((float(xx), yy, 3.3))
for x in (259.5, 282.3): TREES["axis"] += rows([(x, 360), (x, 470)], 9.0, (0, 0)) + rows([(x, 522), (x, 630)], 9.0, (0, 0)) + rows([(x, 648), (x, 765)], 9.0, (0, 0))
for x in (259.5, 282.3): TREES["axis"] += rows([(x, 296), (x, 330)], 9.0, (0, 0))
# 사선 보행축 양측 열식
for s_ in (3.6, 16.4):
    pa = np.array([131.2, 59.5]) + np.array([-0.842, 0.5394]) * s_
    TREES["axis"] += rows([tuple(pa + 25 * v), tuple(pa + 190 * v)], 10.0, (0, 0))
# 역전광장: 중앙 축(a 40~57) 양측 가로수 + 좌우 대칭 격자 식재
PZ = [p_ for p_ in PLZ if p_["name"] == "역전광장"][0]["g"]
for aa in (38.0, 59.0):
    for bb in np.arange(-24.0, -130.0, -8.0): TREES["axis"].append(ab(aa, bb) + (3.0,))
for aa in list(np.arange(-6.0, 31.0, 8.0)) + list(2 * AC - np.arange(-6.0, 31.0, 8.0)):
    for bb in (-27.0, -35.0, -43.0, -51.0): TREES["axis"].append(ab(aa, bb) + (3.0,))
TREES["axis"] = [t for t in TREES["axis"] if not HARD.contains(Point(t[0], t[1])) and B.contains(Point(t[0], t[1]))
                 and (not LOTG[9].contains(Point(t[0], t[1])) or PZ.buffer(-1.5).contains(Point(t[0], t[1])))]
# 획지 안 녹지(건물·광장 제외 여백)
for l in LOTS:
    if l["no"] in (2, 13): continue
    free = l["g"].buffer(-2.0).difference(HARD).difference(unary_union([p["g"] for p in PLZ if p["kind"] in ("광장", "코트")]))
    if l["no"] == 9: free = free.difference(quad(-20, 110, -70, 40))
    TREES["lot"] += scatter(free, 13.0, r=(2.6, 3.8), tries=900)
TREES["lot"] += scatter(unary_union([p["g"] for p in PLZ if p["kind"] in ("중정", "소공원")]).buffer(-2.5), 9.0, r=(2.6, 3.8), tries=900)
# 가로수 — 도로에 접한 보도·보행망 가장자리(도로 경계에서 3 m 안쪽)와 경계 안쪽 3.2 m 선을 따라 11 m 간격
cand = []
for ln in polys(ROADS.buffer(3.0, join_style=2)):
    for ring in [ln.exterior] + list(ln.interiors): cand.append(ring)
cand.append(B.buffer(-3.2).exterior)
WALKISH = unary_union([WALK, PATH8, AX_NS, PROM]).buffer(0.01)
seen = []
for L in cand:
    n = int(L.length // 11)
    for k in range(n):
        p = L.interpolate(k * 11.0)
        if not WALK.contains(p) or HARD.contains(p) or ROADS.buffer(1.5).contains(p): continue
        if any((p.x - a) ** 2 + (p.y - b) ** 2 < 49 for a, b in seen): continue
        seen.append((p.x, p.y)); TREES["street"].append((p.x, p.y, 2.8))

# ── 6. 면적 집계 ─────────────────────────────────────────────
def A(g): return float(g.area)
lot_total = sum(A(l["g"]) for l in LOTS); park_total = sum(A(p["g"]) for p in PARKS)
open_total = sum(A(o["g"]) for o in OPEN); road_total = A(ROADS); walk_total = A(WALK) + A(PATH8)
GFA = sum(A(m["g"]) * m["floors"] for m in MASS); BA = sum(A(m["g"]) for m in MASS)
SUM = dict(boundary=A(B), lot_total=lot_total, park_total=park_total, open_total=open_total, road_total=road_total, walk_total=walk_total,
           closure=A(B) - (lot_total + park_total + open_total + road_total + walk_total), gfa=GFA, ba=BA, bcr=BA / lot_total, far=GFA / lot_total,
           hmax=max(m["h"] for m in MASS), n_mass=len(MASS), trees=sum(len(v) for v in TREES.values()))
for l in LOTS:
    ms = [m for m in MASS if m["lot"] == l["no"]]
    l["area"] = A(l["g"]); l["ba"] = sum(A(m["g"]) for m in ms); l["gfa"] = sum(A(m["g"]) * m["floors"] for m in ms)
    l["maxf"] = max(m["floors"] for m in ms); l["maxh"] = max(m["h"] for m in ms)
for p in PARKS + OPEN: p["area"] = A(p["g"])
print("경계 %.0f / 획지 %.0f · 공원 %.0f · 보행녹지·광장 %.0f · 도로 %.0f · 보도 %.0f / 닫힘 %.2f" % (SUM["boundary"], lot_total, park_total, open_total, road_total, walk_total, SUM["closure"]))
print("건축물 %d동 · 건축면적 %.0f · 연면적 %.0f · 건폐율 %.1f%% · 용적률 %.1f%% · 최고 %.1fm · 수목 %d" % (len(MASS), BA, GFA, SUM["bcr"] * 100, SUM["far"] * 100, SUM["hmax"], SUM["trees"]))
for l in LOTS: print("  %2d %-5s %-26s %8.0f㎡  건축 %6.0f  연면적 %7.0f  %dF" % (l["no"], l["code"], l["name"], l["area"], l["ba"], l["gfa"], l["maxf"]))
for p in PARKS + OPEN: print("  %s %-22s %8.0f㎡" % (p["key"], p["name"], p["area"]))

pickle.dump(dict(B=B, LOTS=LOTS, PARKS=PARKS, OPEN=OPEN, ROADS=dict(N=ROAD_N, EW=ROAD_EW, O=ROAD_O), WALK=WALK, PATH8=PATH8, MASS=MASS, PLZ=PLZ, TREES=TREES,
                 CATS=CATS, SUM=SUM, X0=X0, Y0=Y0, XSHIFT=517.0557, GLASS=GLASS, DBAND=(476.3, 516.3)), open(os.path.join(D, "design.pkl"), "wb"))


def gj(g):
    return [dict(ext=[(x + X0, y + Y0) for x, y in p.exterior.coords], holes=[[(x + X0, y + Y0) for x, y in r.coords] for r in p.interiors]) for p in polys(g)]
J = dict(frame="라이노 러프 프레임(사용자 문서 '최종콘타모델_v2_v3경계.3dm' aardvark, 단위 표기 mm·실제 1단위=1m). v3 계획 프레임 = 러프 + (517.0557, 0)",
         boundary=gj(B), lots=[dict({k: v for k, v in l.items() if k != "g"}, parts=gj(l["g"])) for l in LOTS],
         parks=[dict({k: v for k, v in p.items() if k != "g"}, parts=gj(p["g"])) for p in PARKS + OPEN],
         roads=dict(N=gj(ROAD_N), EW=gj(ROAD_EW), O=gj(ROAD_O)), walks=gj(WALK), path8=gj(PATH8),
         masses=[dict({k: v for k, v in m.items() if k != "g"}, parts=gj(m["g"])) for m in MASS],
         plazas=[dict(kind=p["kind"], name=p["name"], parts=gj(p["g"])) for p in PLZ],
         trees={k: [(x + X0, y + Y0, r) for x, y, r in v] for k, v in TREES.items()}, summary=SUM)
json.dump(J, open(os.path.join(D, "design.json"), "w", encoding="utf-8"), ensure_ascii=False)
