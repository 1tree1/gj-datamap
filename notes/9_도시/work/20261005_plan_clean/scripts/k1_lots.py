"""K1 깔끔한 획지(필지) 구획 — 규제(고도제한·용도지역·켜 규칙)를 무시한 안.
앞 단계 가로망(network.pkl)의 가구를 기준으로, 프로그램이 둘 이상 섞인 가구만 직선으로 나눠 획지(Plot)와 공원(Park)을 확정한다.
출력: scratch/lots.pkl  (lots: 번호·용도·다각형 / parks / roads 분류)"""
import pickle, sys, math, csv
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union, split
from shapely import affinity
import os as _os; SP = _os.environ.get("PLAN_SP", r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad")   # 입력 pkl 폴더. 재현 시 PLAN_SP=<work/20261005_plan_clean/data>
PM = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts"
sys.path.insert(0, PM)
from geomkit import polys, mrr

C = pickle.load(open(SP + r"\context.pkl", "rb")); U = C["U"]
NET = pickle.load(open(SP + r"\network.pkl", "rb"))
STREETS, LANES = NET["STREETS"], NET["LANES"]

def blk(x, y):
    p = Point(x, y)
    for b in NET["blocks"]:
        if b["geom"].contains(p): return b["geom"]
    raise RuntimeError((x, y))

# 사선 보행축 R6 (중심선) — 획지 경계를 이 선에 평행하게 자를 때 사용
R6 = LineString(STREETS["R6"][0]); R6_HALF = STREETS["R6"][1] / 2

LOTS, PARKS = [], []
def lot(name, use, cat, geom, prog, note=""):
    for g in polys(geom):
        if g.area >= 400: LOTS.append(dict(name=name, use=use, cat=cat, prog=prog, geom=g, note=note))
def park(name, kind, geom, note=""):
    """공원·광장 한 건. 여러 조각(종축·사선축이 녹지띠를 가로지름)은 한 건의 MultiPolygon 으로 묶는다."""
    parts = [g for g in polys(geom) if g.area >= 1.0]
    if parts: PARKS.append(dict(name=name, kind=kind, geom=unary_union(parts), note=note))

# ── 공원·광장 ────────────────────────────────────────────────────────────────
park("Park A", "북천 수변공원", blk(219802, 361372), "북천 수변 근린공원(연결녹지)")
gs = polys(NET["green_all"])
park("Park B", "동서 그린 보행축", unary_union(gs), "B 가로 양측 녹지띠(북 4조각·남 조각은 종축 S·사선 R6로 나뉨)")

# ── 북단 ─────────────────────────────────────────────────────────────────────
lot("공공체육·생활시설", "공공(체육·생활SOC)", "여가·오락·체육", blk(219757, 361302), "공공운동·생활시설")
lot("청년주거 북동", "주거", "주거", blk(219902, 361258), "청년주거")
lot("청년주거 서", "주거", "주거", blk(219833, 361186), "청년주거")
lot("청년주거 동", "주거", "주거", blk(219904, 361171), "청년주거")
lot("청년주거 동남(연립)", "주거", "주거", blk(219903, 361116), "청년주거")
# ── 중앙 북 ──────────────────────────────────────────────────────────────────
lot("시청·의회 캠퍼스", "공공청사", "문화·교육·공공", blk(219712, 361167), "시청·의회")
lot("복합문화·영화관", "문화", "문화·교육·공공", blk(219712, 361038), "복합문화·영화관")
lot("청년창업·기업지원", "업무(창업지원)", "상업·업무", blk(219834, 361038), "청년창업·기업지원")
lot("청년·주민 커뮤니티", "공공(주민공동)", "문화·교육·공공", blk(219904, 361038), "청년주민커뮤니티")
# ── 중앙 남 (성동시장 / 레지던시) ────────────────────────────────────────────
b13 = blk(219712, 360861)
cut13 = box(b13.bounds[0] - 1, b13.bounds[1] - 1, 219737, b13.bounds[3] + 1)
lot("성동시장 클러스터", "상업(전통시장 연계)", "판매·음식", b13.intersection(cut13), "성동시장 연계 판매·체험")
lot("체험판매 거리", "상업(전통시장 연계)", "판매·음식", b13.difference(cut13), "성동시장 연계 판매·체험")
lot("레지던시·공방 A", "창조산업", "창조산업", blk(219835, 360873), "아티스트 레지던시·공방")
lot("레지던시·공방 B", "창조산업", "창조산업", blk(219910, 360881), "아티스트 레지던시·공방")
lot("레지던시·공방 C", "창조산업", "창조산업", blk(219891, 360826), "아티스트 레지던시·공방")
# ── 역전광장 블록: 구 역사·근대역사관(획지) + 역전광장(Park C) ───────────────
b15 = blk(219705, 360731)
band15 = R6.buffer(R6_HALF + 56, cap_style=2)
lot("구경주역·근대역사관", "문화(역사)", "역사유산", b15.intersection(band15), "구경주역 이전·근대역사관")
park("Park C", "역전광장", b15.difference(band15), "구 역사 앞 역전광장(광장·공원)")
# ── 관광지원시설 블록: 획지 + 환승광장 ──────────────────────────────────────
b16 = blk(219808, 360708)
cut16 = box(219798, b16.bounds[1] - 1, b16.bounds[2] + 1, b16.bounds[3] + 1)
lot("관광지원시설", "교통·관광지원", "교통·방문자", b16.intersection(cut16), "경주관광지원시설")
park("Plaza D", "환승광장", b16.difference(cut16), "셔틀·관광버스 환승 광장")
# ── 남동·남단 ────────────────────────────────────────────────────────────────
lot("주차전용건축물", "주차", "교통·방문자", blk(219884, 360718), "주차타워")
lot("관광객 휴게·판매상가 W", "상업(관광 휴게·판매)", "판매·음식", blk(219670, 360615), "관광객 중심 휴게·판매상가")
lot("관광객 휴게·판매상가 E", "상업(관광 휴게·판매)", "판매·음식", blk(219729, 360574), "관광객 중심 휴게·판매상가")

# 번호: 북→남(60 m 띠), 서→동 순
LOTS.sort(key=lambda d: (-round(d["geom"].centroid.y / 55), d["geom"].centroid.x))
for i, d in enumerate(LOTS, 1): d["no"] = i; d["id"] = "Plot %d" % i
for d in LOTS: d["area"] = d["geom"].area
for d in PARKS: d["area"] = d["geom"].area

# 도로 분류 — 차량(보차공존 포함) / 보행자전용
veh = unary_union([NET["streets"][k] for k in ("A", "B", "C", "D", "S", "S2", "E")])
ped = unary_union([NET["streets"][k] for k in ("R6", "R7", "R8", "R9")]).difference(veh)
lane = unary_union(list(NET["lanes"].values())).difference(veh).difference(ped)
plz = NET["plaza_extra"]
chk = sum(d["area"] for d in LOTS) + sum(d["area"] for d in PARKS) + veh.area + ped.area + lane.area + plz.area
print("획지 %d개, 공원·광장 %d개 | 획지합 %.0f 공원합 %.0f 차량도로 %.0f 보행도로 %.0f 골목 %.0f 교차광장 %.0f" % (len(LOTS), len(PARKS), sum(d["area"] for d in LOTS), sum(d["area"] for d in PARKS), veh.area, ped.area, lane.area, plz.area))
print("합계 검증: %.1f / U %.1f (차 %.2f)" % (chk, U.area, chk - U.area))
for d in LOTS: print("%-8s %-20s %7.0f㎡  (%.0f,%.0f) 채움률 %.2f" % (d["id"], d["name"], d["area"], d["geom"].centroid.x, d["geom"].centroid.y, d["geom"].area / d["geom"].minimum_rotated_rectangle.area))
for d in PARKS: print("%-8s %-20s %7.0f㎡" % (d["name"], d["kind"], d["area"]))
pickle.dump(dict(LOTS=LOTS, PARKS=PARKS, veh=veh, ped=ped, lane=lane, plaza=plz), open(SP + r"\lots.pkl", "wb"))

