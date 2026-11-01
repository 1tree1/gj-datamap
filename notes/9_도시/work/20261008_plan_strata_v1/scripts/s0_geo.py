"""S0 사용자 도면(라이노 v1b: 경계·차량도로(파랑)·보행우선도로(빨강)) → 로컬 좌표(E,N m, 부지 남서 모서리 원점) 기하 정리.
입력: data/local_geo.pkl (경계 S, 도로 서피스 V1·V2·P1~P4 — 라이노에서 서피스별 DXF로 내보내 읽은 것)
출력: data/geo.pkl — 도로 명칭 분할, 블록(셀) 분할, 선(곡선·분할선)"""
import pickle, os, math
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union, split
from shapely import affinity

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
G = pickle.load(open(os.path.join(D, "local_geo.pkl"), "rb")); S = G["S"]; RD = G["roads"]
def parts(g): return list(g.geoms) if g.geom_type.startswith("Multi") else [g]
def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []

# ── 도로(사용자 서피스) 이름 붙이기 ──────────────────────────────────────────────
V1, V2 = RD["V1"], RD["V2"]
P1, P2, P3, P4 = RD["P1"], RD["P2"], RD["P3"], RD["P4"]
p3 = sorted(parts(P3), key=lambda p: -p.area); P3main, WEDGE = p3[0], p3[1]       # 종축+플랫폼 광장+동서 골목 / 쐐기(곡선 삼각)
def clip(g, b): return g.intersection(b)
ROADS = {}
# 차량(파랑)
ROADS["A"] = dict(g=clip(V1, box(-5, 207, 220, 224)), grp="차량", nm="A가로", kind="동서 관통 차량가로(보차공존)", w=15.0)
ROADS["B"] = dict(g=clip(V1, box(148, 90, 158, 208.01)).difference(box(-5, 207.9, 220, 224)), grp="차량", nm="B가로", kind="남측 연결가로(일방)", w=8.0)
ROADS["C"] = dict(g=clip(V2, box(50, 545, 116, 560)), grp="차량", nm="C가로", kind="북측 연결가로(보차공존)", w=12.0)
ROADS["D"] = dict(g=V2.difference(box(50, 545, 116, 560)), grp="차량", nm="D가로", kind="북동 사선 차량가로", w=13.0)
# 보행 우선(빨강)
spine = clip(P3main, box(108.9, 222, 114.05, 547))
plaza = clip(P3main, box(114.0, 305.9, 216, 351.1))
street = clip(P3main, box(114.0, 429.9, 216, 438.1))
rest3 = P3main.difference(unary_union([spine, plaza, street])).buffer(0)
ROADS["S"] = dict(g=spine, grp="보행", nm="S축", kind="종축 보행 중심가로(공중가로 하부)", w=5.0)
ROADS["PZ"] = dict(g=plaza, grp="보행", nm="플랫폼 광장", kind="철도 흔적 지상광장(보행 우선)", w=45.0)
ROADS["R10"] = dict(g=street, grp="보행", nm="R10", kind="동서 보행가로", w=8.0)
ROADS["R6"] = dict(g=unary_union([rest3, P4]), grp="보행", nm="R6축", kind="사선 보행축(철도 사선)", w=14.0)
ROADS["R8"] = dict(g=P2, grp="보행", nm="R8", kind="북단 수변 보행로", w=6.0)
ROADS["R9"] = dict(g=P1, grp="보행", nm="R9", kind="동측 경계 보행로", w=6.0)
_used = WEDGE
for k in ("A", "B", "C", "D", "S", "PZ", "R10", "R6", "R8", "R9"):            # 교차부는 앞선 도로 소유 — 도로끼리 겹치지 않게
    g = unary_union(polys(ROADS[k]["g"])).difference(_used)
    ROADS[k]["g"] = unary_union([p for p in polys(g) if p.area > 0.5]); _used = unary_union([_used, ROADS[k]["g"]])

R_ALL = unary_union([r["g"] for r in ROADS.values()])
R_ALL_W = unary_union([r["g"] for k, r in ROADS.items()] + [WEDGE])
cells = [c for c in polys(S.difference(R_ALL_W)) if c.area > 100]

# ── 분할선(사용자 도면의 곡선·분할선) ─────────────────────────────────────────────
CURVE = LineString([(3, 428), (25, 404), (48, 384), (70, 367), (93, 350)])          # 쐐기 아래 곡선 분할선
LINE_N438 = LineString([(-5, 440.5), (102.5, 438.0)])                                  # 시청 블록 남변
LINE_N350 = LineString([(-5, 350.5), (93, 350.0)])
LINE_N306 = LineString([(-5, 306.0), (110, 306.0)])
# 북단 분할선: 사선 보행로 R8 내변 연장 (72,648)-(141,596)
LINE_TIP = LineString([(66, 653), (146, 591)])

def cell_at(x, y):
    p = Point(x, y)
    for c in cells:
        if c.contains(p): return c
    raise RuntimeError((x, y))
def halfplane(line, side_pt):
    """직선(연장) 기준 side_pt 쪽 반평면(큰 박스 분할)"""
    (x0, y0), (x1, y1) = list(line.coords)[0], list(line.coords)[-1]
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    big = 2000
    poly = Polygon([(x0 - ux * big, y0 - uy * big), (x1 + ux * big, y1 + uy * big), (x1 + ux * big + nx * big, y1 + uy * big + ny * big), (x0 - ux * big + nx * big, y0 - uy * big + ny * big)])
    if not poly.contains(Point(*side_pt)): poly = affinity.scale(poly, xfact=1, yfact=1)
    if not poly.contains(Point(*side_pt)):
        poly = Polygon([(x0 - ux * big, y0 - uy * big), (x1 + ux * big, y1 + uy * big), (x1 + ux * big - nx * big, y1 + uy * big - ny * big), (x0 - ux * big - nx * big, y0 - uy * big - ny * big)])
    return poly

# 북단: 수변공원(위) / 창작시설 블록(아래)
C1 = cell_at(110, 672)
tip_half = halfplane(LINE_TIP, (110, 672))
TIP_PARK = unary_union(polys(C1.intersection(tip_half)))
CREATIVE = unary_union(polys(C1.difference(tip_half)))
# 서측 큰 셀: 종축 서변 녹지띠(E 102~109) 분리
CW = cell_at(50, 500)
SPINE_GREEN = unary_union(polys(CW.intersection(box(102.0, 0, 110, 1000))))
CWm = CW.difference(box(102.0, 0, 110, 1000))
CITY = unary_union(polys(CWm.intersection(halfplane(LINE_N438, (50, 500)))))
below = CWm.difference(halfplane(LINE_N438, (50, 500)))
RES_W = unary_union(polys(below.intersection(halfplane(LINE_N306, (50, 260)))))                  # N<306: 성동시장 클러스터 후보
mid = below.difference(halfplane(LINE_N306, (50, 260)))
EXP_W = unary_union(polys(mid.intersection(halfplane(LINE_N350, (50, 330)))))                    # N 306~350: 체험판매
upper = mid.difference(halfplane(LINE_N350, (50, 330)))                                          # N 350~쐐기: 녹지 언덕 + 곡선 띠
curve_side = halfplane(CURVE, (20, 360))
HILL = unary_union(polys(upper.intersection(curve_side)))
SLIVER = unary_union(polys(upper.difference(curve_side)))

# 중앙 동서 보행 가로: 동측 플랫폼 광장(45 m 띠)을 서쪽 경계까지 연장(종축 S 교차) — 체험판매 블록 자리
band_w = box(-5, 306.0, 109.0, 351.1)
PZW = unary_union([EXP_W, upper.intersection(band_w), SPINE_GREEN.intersection(band_w)])
EXP_W = Polygon(); HILL = HILL.difference(band_w); SLIVER = SLIVER.difference(band_w); SPINE_GREEN = SPINE_GREEN.difference(band_w)
ROADS["PZ"]["g"] = unary_union([ROADS["PZ"]["g"], PZW]); ROADS["PZ"]["nm"] = "중앙 보행가로"; ROADS["PZ"]["kind"] = "동서 중앙 보행가로(철도 흔적 광장)"
# 동측
NE = cell_at(160, 500)
CULT = cell_at(160, 390)
RES_E1 = cell_at(150, 265); RES_E2 = cell_at(200, 270)
# 남측
STAT = cell_at(50, 160); GARDEN = cell_at(30, 60); HALLS = cell_at(55, 50) if cell_at(55, 50) is not GARDEN else None
TOUR = cell_at(130, 150); PARK_S = cell_at(185, 150); SLV = cell_at(120, 200)
HALLS = cell_at(60, 40); GARDEN = cell_at(30, 80)
NE_BARS = box(118, 440, 212, 548)

out = dict(S=S, ROADS=ROADS, WEDGE=WEDGE, cells=cells, TIP_PARK=TIP_PARK, CREATIVE=CREATIVE, SPINE_GREEN=SPINE_GREEN, CITY=CITY, RES_W=RES_W, EXP_W=EXP_W, HILL=HILL, SLIVER=SLIVER,
           NE=NE, CULT=CULT, RES_E1=RES_E1, RES_E2=RES_E2, STAT=STAT, GARDEN=GARDEN, HALLS=HALLS, TOUR=TOUR, PARK_S=PARK_S, SLV=SLV, CURVE=CURVE)
pickle.dump(out, open(os.path.join(D, "geo.pkl"), "wb"))
if __name__ == "__main__":
    for k in ("TIP_PARK", "CREATIVE", "SPINE_GREEN", "CITY", "RES_W", "EXP_W", "HILL", "SLIVER", "NE", "CULT", "RES_E1", "RES_E2", "STAT", "GARDEN", "HALLS", "TOUR", "PARK_S", "SLV"):
        print("%-12s %7.0f㎡" % (k, out[k].area))
    for k, r in ROADS.items(): print("road %-4s %-8s %7.0f㎡" % (k, r["nm"], r["g"].area))
    print("wedge %.0f" % WEDGE.area)
    tot = sum(out[k].area for k in ("TIP_PARK", "CREATIVE", "SPINE_GREEN", "CITY", "RES_W", "EXP_W", "HILL", "SLIVER", "NE", "CULT", "RES_E1", "RES_E2", "STAT", "GARDEN", "HALLS", "TOUR", "PARK_S", "SLV"))
    tot += sum(r["g"].area for r in ROADS.values()) + WEDGE.area
    print("합계 %.1f / S %.1f (차 %.2f)" % (tot, S.area, tot - S.area))
