"""S2 필지 재구성 — 사용자 도로·보도는 그대로 두고, 14개 원 필지(위치·성격 확정)를 '건축 획지 + 공원·녹지 획지'로 다시 나눈다.
규칙(근거는 문서 §3): ① 건축 획지 면적 = 프로그램 건축면적 ÷ 계획 건폐율(공공업무 ~39%, 업무 38~53%, 주거 31%, 문화 35%, 근린 33%, 운동 25%, 주차전용 73~87%).
② 건축 획지는 중앙 보행가로(x=173~203)에 면하게 붙이고 남는 땅은 바깥쪽(서측·동측·북·남)에서 공원·녹지로 묶는다. ③ 구 역사(존치)는 제 자리에 두고 그 둘레를 획지로 잡는다.
출력: data/lots.pkl (좌표는 라이노 평면 좌표에서 (OX,OY)=(1167200,1761100)을 뺀 로컬 m)"""
import os, pickle, math, json
import numpy as np
from shapely.geometry import Polygon, box, Point, LineString, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
OX, OY = 1167200.0, 1761100.0
G = pickle.load(open(os.path.join(D, "geo.pkl"), "rb"))
order = sorted(range(len(G["parcels"])), key=lambda i: G["parcels"][i]["rep"][1])
OP = {}
for n, i in enumerate(order):
    p = G["parcels"][i]["g"]
    OP[n + 1] = affinity.translate(p, -OX, -OY)
WALKS = [affinity.translate(w["g"], -OX, -OY) for w in G["walks"]]
ROADS = [affinity.translate(r["g"], -OX, -OY) for r in G["roads"]]
U = affinity.translate(pickle.load(open(os.path.join(D, "U_clean.pkl"), "rb"))["U"], -OX, -OY)


def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []


def clean(g, eps=0.02):
    return unary_union(polys(g)).buffer(eps, join_style=2).buffer(-eps, join_style=2)


def solve_box(poly, target, make, lo, hi, it=60):
    """make(t) → box. t 를 이분탐색해 poly∩box 면적이 target 이 되게 한다(면적이 t 에 대해 증가한다고 가정)."""
    for _ in range(it):
        mid = (lo + hi) / 2
        a = poly.intersection(make(mid)).area
        if a < target: lo = mid
        else: hi = mid
    return (lo + hi) / 2


# ── 획지 정의 ────────────────────────────────────────────────────────────────
LOT = {}      # 코드 → dict(g, from=원필지, use=용도)
# 공1: 시청(O10) — 중앙 보행가로(동) 쪽에 붙임
t = solve_box(OP[10], 14000.0, lambda w: box(173.5 - w, 600, 180, 800), 1, 150)
LOT["공1"] = dict(g=OP[10].intersection(box(173.5 - t, 600, 180, 800)), src=10)
# 업1: O8, 동쪽(중앙 보행가로 쪽) 45 m 폭 × 중앙 정렬
def centered(poly, x0, x1, area, yc):
    h = area / (x1 - x0)
    return poly.intersection(box(x0, yc - h / 2, x1, yc + h / 2))
yc8 = (516.3 + 635.2) / 2
LOT["업1"] = dict(g=centered(OP[8], 128.0, 173.5, 2400.0, yc8), src=8)
LOT["업2"] = dict(g=centered(OP[7], 202.5, 247.0, 2550.0, yc8), src=7)
yc4 = (358.7 + 476.3) / 2
LOT["문4"] = dict(g=centered(OP[4], 128.0, 173.5, 2700.0, yc4), src=4)
LOT["문5"] = dict(g=centered(OP[6], 202.5, 248.0, 3700.0, yc4), src=6)
# 상1: O5 서쪽 가장자리(성동시장 쪽)에 선형 상가열
LOT["상1"] = dict(g=OP[5].intersection(box(29, 372, 52.5, 463)), src=5)
# 관1, 주1, 체1: 원 필지 전체
LOT["관1"] = dict(g=OP[3], src=3)
LOT["주1"] = dict(g=OP[11], src=11)
LOT["체1"] = dict(g=OP[12], src=12)
# 문1: 공연장 — O13 남쪽(중앙가로 쪽)
t = solve_box(OP[13], 6000.0, lambda y1: box(90, 780, 230, y1), 790, 915)
LOT["문1"] = dict(g=OP[13].intersection(box(90, 780, 230, t)), src=13)
# 문2: 구 역사 둘레 — 대각선(철도 흔적) 가장자리에서 8 m 떨어진 선의 서북쪽, y>=205(역 전면 광장·정원 포함)
_A = np.array([173.0, 291.2]); _B = np.array([35.5, 76.7]); _d = (_A - _B) / np.linalg.norm(_A - _B); _n = np.array([-_d[1], _d[0]])
def _half(delta, ymin):
    P0 = _A + delta * _n; far = 2000
    return Polygon([tuple(P0 - _d * far), tuple(P0 + _d * far), tuple(P0 + _d * far + _n * far), tuple(P0 - _d * far + _n * far)]).intersection(box(0, ymin, 400, 400))
LOT["문2"] = dict(g=OP[2].intersection(_half(8.0, 205.0)), src=2)
# 문3: O1 남쪽(도시 쪽) 가장자리 팝업·상가
LOT["문3"] = dict(g=OP[1].intersection(box(40, 50, 160, 93)), src=1)
for k, v in LOT.items(): v["g"] = clean(v["g"]); v["area"] = v["g"].area

# ── 공원·녹지 획지 ───────────────────────────────────────────────────────────
def rest(src_ids, lot_codes):
    base = unary_union([OP[i] for i in src_ids])
    cut = unary_union([LOT[c]["g"] for c in lot_codes]) if lot_codes else Polygon()
    return clean(base.difference(cut), 0.02)

GRN = {}
GRN["공원1"] = dict(g=rest([14, 13], ["문1"]), kind="근린공원", name="북측 근린공원")
GRN["공원2"] = dict(g=rest([9, 8], ["업1"]), kind="근린공원", name="서측 중앙 근린공원")
GRN["공원3"] = dict(g=rest([5, 4], ["상1", "문4"]), kind="근린공원", name="서측 시장 연계 근린공원")
GRN["녹지1"] = dict(g=rest([10], ["공1"]), kind="경관녹지", name="서측 경관녹지")
GRN["공원4"] = dict(g=rest([7], ["업2"]), kind="근린공원", name="동측 근린공원")
GRN["공원5"] = dict(g=rest([6], ["문5"]), kind="문화공원", name="레지던시 문화공원")
GRN["공원6"] = dict(g=rest([2, 1], ["문2", "문3"]), kind="역사공원", name="구 역사 역사공원")
for k, v in GRN.items(): v["area"] = v["g"].area

if __name__ == "__main__":
    tot_lot = sum(v["area"] for v in LOT.values()); tot_grn = sum(v["area"] for v in GRN.values())
    parc = sum(p.area for p in OP.values())
    print("원 필지 합 %.1f | 건축 획지 %.1f | 공원·녹지 %.1f | 합 %.1f (차 %.2f)" % (parc, tot_lot, tot_grn, tot_lot + tot_grn, parc - tot_lot - tot_grn))
    for k, v in LOT.items(): print("%-3s %8.1f  src O%d  parts %d" % (k, v["area"], v["src"], len(polys(v["g"]))))
    for k, v in GRN.items(): print("%-4s %8.1f  %-6s %s parts %d" % (k, v["area"], v["kind"], v["name"], len(polys(v["g"]))))
    pickle.dump(dict(LOT=LOT, GRN=GRN, OP=OP, WALKS=WALKS, ROADS=ROADS, U=U, OX=OX, OY=OY), open(os.path.join(D, "lots.pkl"), "wb"))
