"""S7 표 산출 — 가로표·가구표·프로그램표·건물표·규제 점검·앵커표·토지이용 요약. CSV(UTF-8 BOM)와 pickle(tables.pkl) 저장."""
import pickle, sys, math, csv, collections, os
import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
OUT = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing"
sys.path.insert(0, OUT + r"\scripts")
from plan_def import FLOOR_H, SIDE_CAP
from plan_meta import PROGRAMS, PROG_BY_KEY
from geomkit import polys, mrr
os.makedirs(OUT + r"\tables", exist_ok=True)

C = pickle.load(open(SP + r"\context.pkl", "rb")); U = C["U"]
NET = pickle.load(open(SP + r"\network.pkl", "rb"))
M = pickle.load(open(SP + r"\massing2.pkl", "rb")); BUILD, EXTRA = M["BUILD"], M["EXTRA"]
OV = pickle.load(open(SP + r"\overlay.pkl", "rb"))
AS = pickle.load(open(SP + r"\anchor_status.pkl", "rb"))

def wcsv(name, header, rows):
    with open(OUT + rf"\tables\{name}.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

# ── 가구 라벨 ────────────────────────────────────────────────────────────────
BLK = {  # probe → (라벨, 대분류, 주 프로그램키)
    (219802, 361372): ("북천 수변공원", "공원·녹지", "수변 오픈스페이스"),
    (219757, 361302): ("공공운동·생활시설", "공공(체육·생활SOC)", "공공운동·생활시설"),
    (219902, 361258): ("청년주거 북동블록", "주거", "청년주거"),
    (219833, 361186): ("청년주거 서블록", "주거", "청년주거"),
    (219904, 361171): ("청년주거 동블록", "주거", "청년주거"),
    (219712, 361167): ("시청·의회 캠퍼스", "공공청사", "시청·의회"),
    (219903, 361116): ("청년주거 동남블록(연립)", "주거", "청년주거"),
    (219712, 361038): ("복합문화·영화관", "문화", "복합문화·영화관"),
    (219834, 361038): ("청년창업·기업지원", "업무(창업지원)", "청년창업·기업지원"),
    (219904, 361038): ("청년·주민 커뮤니티", "공공(주민공동)", "청년주민커뮤니티"),
    (219835, 360873): ("레지던시·공방 A", "창조산업", "아티스트 레지던시·공방"),
    (219910, 360881): ("레지던시·공방 B", "창조산업", "아티스트 레지던시·공방"),
    (219712, 360861): ("성동시장 연계 판매·체험", "상업(전통시장 연계)", "성동시장 연계 판매·체험"),
    (219891, 360826): ("레지던시·공방 C", "창조산업", "아티스트 레지던시·공방"),
    (219705, 360731): ("역전광장·구경주역(이전)·근대역사관", "광장·역사문화", "구경주역 이전"),
    (219808, 360708): ("관광지원시설·환승광장", "교통·관광지원", "경주관광지원시설"),
    (219884, 360718): ("주차타워·임시 평면주차", "주차", "주차타워"),
    (219670, 360615): ("관광객 휴게·판매상가(서)", "상업(관광 휴게·판매)", "관광객 중심 휴게·판매상가"),
    (219729, 360574): ("관광객 휴게·판매상가(동)", "상업(관광 휴게·판매)", "관광객 중심 휴게·판매상가"),
}
def blk_label(b):
    for (x, y), v in BLK.items():
        if b["geom"].contains(Point(x, y)): return v
    return ("미정", "미정", "")

# ── 1) 가구표 ────────────────────────────────────────────────────────────────
blk_rows, blk_info = [], {}
for b in NET["blocks"]:
    lab, major, pk = blk_label(b)
    bl = [x for x in BUILD if x["block"] == b["id"]]
    fp = sum(x["area"] for x in bl); gfa = sum(x["gfa"] for x in bl); A = b["area"]
    nbld = len({x["bid"] for x in bl})
    maxf = max((x["floors"] for x in bl), default=0); maxh = max((x["h"] for x in bl), default=0)
    ov = OV[b["id"]]
    zn = ", ".join("%s %.0f%%" % (k.replace("지역", ""), v / A * 100) for k, v in sorted(ov["zone"].items(), key=lambda kv: -kv[1]) if v / A >= 0.03)
    blk_info[b["id"]] = dict(label=lab, major=major, area=A, fp=fp, gfa=gfa, nbld=nbld, maxf=maxf, maxh=maxh, ov=ov, zn=zn, prog=pk)
    blk_rows.append([b["id"], lab, major, round(A), nbld, round(fp), round(fp / A * 100, 1), round(gfa), round(gfa / A * 100, 1), maxf, maxh,
                     zn, round(ov["gosi"] / A * 100), "도심20m %d%% / 도심15m %d%%" % (round(ov["h20"] / A * 100), round(ov["h15"] / A * 100)) + (" / 최저고도 %d%%" % round(ov["hmin"] / A * 100) if ov["hmin"] > 1 else ""),
                     round(min(ov["her"] / A, 1) * 100), ov["n_exist"], round(ov["exist_area"])])
wcsv("blocks", ["가구", "계획 용도", "대분류", "가구면적㎡", "건축물 동수", "건축면적㎡", "건폐율%", "연면적㎡", "용적률%", "최고층", "최고높이m", "현행 용도지역(30㎡ 이상 3%↑)", "고시 2026-8호 구역 내 %", "고도지구", "역사문화환경보존지역 %", "기존 건축물 수(NGII)", "기존 건축면적㎡"], blk_rows)

# ── 2) 프로그램 요약 ─────────────────────────────────────────────────────────
agg = collections.defaultdict(lambda: dict(n=0, fp=0.0, gfa=0.0, maxf=0, maxh=0.0))
for x in BUILD:
    a = agg[x["prog"]]; a["fp"] += x["area"]; a["gfa"] += x["gfa"]; a["maxf"] = max(a["maxf"], x["floors"]); a["maxh"] = max(a["maxh"], x["h"])
for k in agg: agg[k]["n"] = len({x["bid"] for x in BUILD if x["prog"] == k})
prog_rows = []
for p in PROGRAMS:
    a = agg.get(p["key"])
    if not a: continue
    prog_rows.append([p["no"], p["sketch"], p["term"], p["use"], p["facility"], p["zoning"], p["gosi"], a["n"], round(a["fp"]), round(a["gfa"]), a["maxf"], round(a["maxh"], 1)])
wcsv("programs", ["번호", "스케치 용어", "계획 용어(조닝)", "건축물 용도(건축법 시행령 별표 1)", "도시·군계획시설", "제안 용도지역·지정", "고시 2026-8호 대응", "건축물 수", "건축면적㎡", "연면적㎡", "최고층", "최고높이m"], prog_rows)

# ── 3) 가로표 ────────────────────────────────────────────────────────────────
XS = {  # 폭원 구성 가정(m): 보도·식재·차로 등 — 도로의 구조·시설 기준에 관한 규칙 대조 필요
    "A": "보도 3.0 + 식재·자전거 1.5 + 차로 2×3.0 + 식재·자전거 1.5 + 보도 3.0 = 15.0",
    "B": "보도 2.5 + 식재 1.0 + 보차공존 차로 5.0 + 식재 1.0 + 보도 2.5 = 12.0 (양측 녹지띠와 합쳐 약 70 m 그린 보행축)",
    "C": "보도 2.5 + 식재 1.0 + 보차공존 차로 5.0 + 식재 1.0 + 보도 2.5 = 12.0",
    "D": "보도 2.0 + 식재 0.75 + 보차공존 차로 4.5 + 식재 0.75 + 보도 2.0 = 10.0",
    "S": "보행·식재 4.5 + 공유 노면(셔틀·서비스·비상) 7.0 + 보행·식재 4.5 = 16.0",
    "R6": "보행 전용 10.0 + 식재 2×2.0 = 14.0",
    "R7": "보행 전용 10.0 + 식재 2×2.0 = 14.0",
    "R8": "산책로 6.0 + 식재·자전거 4.0 = 10.0 (북천 수변)",
    "R9": "보행 전용 8.0 + 식재 2×1.0 = 10.0",
    "S2": "보도 2.0 + 보차공존 차로 6.0 + 보도 2.0 = 10.0 (기존 11 m 남북 가로 연장)",
    "E": "보도 1.5 + 보차공존 차로 5.0 + 보도 1.5 = 8.0",
}
st_rows, st_info = [], {}
anchors_conn = collections.defaultdict(list)
for r in AS["after"]:
    best = None
    for k, g in list(NET["streets"].items()) + list(NET["lanes"].items()):
        d = g.distance(Point(r["x"], r["y"]))
        if d < 8 and (best is None or d < best[1]): best = (k, d)
    if best and r["status"] == "도로·골목 연결": anchors_conn[best[0]].append(r)
for k, (pts, w, cls, desc, basis) in NET["STREETS"].items():
    g = NET["streets"][k]
    ln = LineString(pts).intersection(U); L = ln.length if not ln.is_empty else 0
    if k == "R8": L = g.area / w            # 북동 경계를 따르는 띠 — 자리표시 선분 대신 면적/폭으로 연장 환산
    anc = ", ".join("%s %.0fm(%.0f,%.0f)" % (r["side"], r["w"], r["x"], r["y"]) for r in anchors_conn.get(k, []))
    st_rows.append([k, desc, cls, w, round(L), round(g.area), XS.get(k, ""), anc or "-", basis]); st_info[k] = dict(desc=desc, cls=cls, w=w, L=L, area=g.area)
for k, (pts, w, desc, basis) in NET["LANES"].items():
    g = NET["lanes"][k]; ln = LineString(pts).intersection(U); L = ln.length if not ln.is_empty else 0
    anc = ", ".join("%s %.0fm(%.0f,%.0f)" % (r["side"], r["w"], r["x"], r["y"]) for r in anchors_conn.get(k, []))
    st_rows.append([k, desc, "보행골목(소방 4 m 이상 확보)", w, round(L), round(g.area), "보행 4.0 + 식재·설비 2.0 = 6.0", anc or "-", basis]); st_info[k] = dict(desc=desc, cls="골목", w=w, L=L, area=g.area)
wcsv("streets", ["가로", "기능", "도로 구분", "폭m", "부지 내 연장m", "면적㎡", "폭원 구성(가정)", "접속한 기존 가로(앵커)", "근거"], st_rows)

# ── 4) 앵커표 ────────────────────────────────────────────────────────────────
an_rows = []
before = {(round(r["x"]), round(r["y"])): r["status"] for r in AS["before"]}
for r in sorted(AS["after"], key=lambda r: (r["side"], r["y"], r["x"])):
    an_rows.append([r["side"], round(r["x"]), round(r["y"]), r["w"], before.get((round(r["x"]), round(r["y"])), ""), r["status"]])
wcsv("anchors", ["방향", "x(5187)", "y(5187)", "기존 가로 폭m", "보정 전", "보정 후"], an_rows)

# ── 5) 건물표 ────────────────────────────────────────────────────────────────
bd_rows = []
for x in sorted(BUILD, key=lambda b: (b["block"], b["bid"], b["part"])):
    L, W, ang = mrr(x["geom"])
    bd_rows.append(["%s.%d" % (x["bid"], x["part"]), x["block"], x["prog"], x["tag"], x["use"], x["cat"], round(x["area"]), x["floors"], x["floor_h"], x["h"], round(x["gfa"]), x["side"], x["band"], x["side_cap"], x["h_cap"],
                    round(L, 1), "예외" if x["exc"] else ""])
wcsv("buildings", ["건물조각", "가구", "프로그램", "명칭", "용도", "범례 분류", "건축면적㎡", "층수", "층고m", "높이m", "연면적㎡", "경계 방향", "켜(1~3)", "켜 규칙 상한층", "고도지구 상한m", "장변 길이m", "켜 규칙 예외"], bd_rows)

# ── 6) 규제 점검 ─────────────────────────────────────────────────────────────
viol_h = [x for x in BUILD if x["h"] > x["h_cap"] + 1e-6]
viol_f = [x for x in BUILD if x["floors"] > x["side_cap"] and not x["exc"]]
exc = [x for x in BUILD if x["exc"] and x["floors"] > SIDE_CAP[x["side"]][x["band"] - 1]]
LEN_CAP = {"동": (15.0, 30.0), "서": (22.0, 40.0), "남": (17.0, 32.0), "북": (15.0, 30.0), "수변": (22.0, 40.0)}
lenv = []
for x in BUILD:
    if x["band"] <= 2 and x["area"] >= 60:
        L, W, ang = mrr(x["geom"])
        if L > LEN_CAP[x["side"]][x["band"] - 1] * 1.25: lenv.append((x, L))
chk = dict(n_build=len(BUILD), n_over_height=len(viol_h), n_over_sidecap=len(viol_f), n_exception=len(exc), exc_area=sum(x["area"] for x in exc), exc_gfa=sum(x["gfa"] for x in exc),
           n_len_over=len(lenv), len_over=[(x["tag"], x["block"], round(L), x["side"], x["band"]) for x, L in lenv])
print("규제 점검:", {k: v for k, v in chk.items() if k != "len_over"})
print("길이 초과(켜1·2에서 상한×1.25 초과):", chk["len_over"][:12])

# ── 6b) 방향×켜 규칙 준수 현황 ───────────────────────────────────────────────
sb_rows = []
for side in ("서", "동", "남", "북", "수변"):
    for band in (1, 2, 3):
        sel = [x for x in BUILD if x["side"] == side and x["band"] == band]
        if not sel: continue
        Ls = [mrr(x["geom"])[0] for x in sel]
        cap_len = LEN_CAP[side][band - 1] if band <= 2 else None
        n_ok = sum(1 for L_ in Ls if cap_len is None or L_ <= cap_len * 1.25)
        gfa_ = sum(x["gfa"] for x in sel); fp_ = sum(x["area"] for x in sel)
        sb_rows.append([side, band, len(sel), round(fp_), round(gfa_), max(x["floors"] for x in sel), round(gfa_ / fp_, 2), SIDE_CAP[side][band - 1] if band <= 2 else "규제 상한까지",
                        cap_len if cap_len else "-", round(float(np.median(Ls)), 1), "%d/%d" % (n_ok, len(sel))])
wcsv("scale_rule_check", ["경계 방향", "켜", "매스 조각", "건축면적㎡", "연면적㎡", "최고층", "평균층수(연면적/건축면적)", "켜 규칙 층수 상한", "건물 길이 상한m", "장변 중앙값m", "길이 규칙 충족(상한×1.25)"], sb_rows)

# ── 7) 토지이용 요약 ─────────────────────────────────────────────────────────
Utot = U.area
veh_u = unary_union([NET["streets"][k] for k in ("A", "B", "C", "D", "S", "S2", "E")])
ped_u = unary_union([NET["streets"][k] for k in ("R6", "R7", "R8", "R9")]).difference(veh_u)
lane_u = unary_union(list(NET["lanes"].values())).difference(veh_u).difference(ped_u)
road_veh, road_ped, lanes_a = veh_u.area, ped_u.area, lane_u.area       # 교차부 중복을 빼고 합집합 기준으로 면적을 센다
junction = NET["plaza_extra"].area
green_a = NET["green_all"].area
road_union = unary_union(list(NET["streets"].values()) + list(NET["lanes"].values()))
lu = collections.OrderedDict()
lu["도로(중로·소로·보행우선가로)"] = road_veh
lu["보행자전용도로·수변 산책로"] = road_ped
lu["보행골목(켜1 이어받기)"] = lanes_a
lu["교차부 광장(자투리)"] = junction
lu["녹지(동서 그린 보행축)"] = green_a
major_area = collections.OrderedDict()
for b in NET["blocks"]:
    m = blk_info[b["id"]]["major"]; major_area[m] = major_area.get(m, 0) + b["area"]
for m, a in major_area.items(): lu["가구 — " + m] = a
chk_sum = sum(lu.values())
print("토지이용 합계 %.0f / U %.0f (차 %.1f)" % (chk_sum, Utot, chk_sum - Utot))
lu_rows = [[k, round(v), round(v / Utot * 100, 1)] for k, v in lu.items()] + [["합계", round(chk_sum), round(chk_sum / Utot * 100, 1)]]
wcsv("landuse", ["구분", "면적㎡", "구성비%(경계 218,478㎡ 대비)"], lu_rows)

# 공개 오픈스페이스 지표: 공원·녹지·광장·공개공지
def area_of(lst): return sum(g.area for nm, g in lst)
open_public = dict(
    녹지띠=green_a, 수변공원=blk_info[[b["id"] for b in NET["blocks"] if blk_info[b["id"]]["label"] == "북천 수변공원"][0]]["area"],
    광장_역전광장=sum(g.area for nm, g in EXTRA["plaza"] if nm == "역전광장"), 광장_환승=sum(g.area for nm, g in EXTRA["plaza"] if nm.startswith("환승")),
    교차부광장=junction, 문화광장=sum(g.area for nm, g in EXTRA["plaza"] if nm == "문화광장"), 시민마당=sum(g.area for nm, g in EXTRA["court"] if nm == "시민마당"),
    삼층석탑마당=sum(g.area for nm, g in EXTRA["heritage_plaza"]))
print("공개 오픈스페이스:", {k: round(v) for k, v in open_public.items()}, "합 %.0f (%.1f%%)" % (sum(open_public.values()), sum(open_public.values()) / Utot * 100))

# 세대·주차
hs = [x for x in BUILD if x["prog"] == "청년주거"]; gfa_h = sum(x["gfa"] for x in hs)
park = [x for x in BUILD if x["role"] == "주차"]; gfa_p = sum(x["gfa"] for x in park)
sp_area = sum(g.area for nm, g in EXTRA["surface_parking"])
summary = dict(U=Utot, bld_fp=sum(x["area"] for x in BUILD), bld_gfa=sum(x["gfa"] for x in BUILD), n_build=len({x["bid"] for x in BUILD}), n_pieces=len(BUILD),
               housing_gfa=gfa_h, units36=gfa_h * 0.7 / 36, units60=gfa_h * 0.7 / 60, park_gfa=gfa_p, park_spaces=gfa_p / 32, sp_area=sp_area, sp_spaces=sp_area / 25,
               city_gfa=sum(x["gfa"] for x in BUILD if x["prog"] == "시청·의회"), exist_n=sum(v["n_exist"] for v in OV.values()), exist_fp=sum(v["exist_area"] for v in OV.values()),
               road_total=road_union.area + junction, open_public=sum(open_public.values()))
for k, v in summary.items(): print("  %-12s %s" % (k, round(v, 1)))
pickle.dump(dict(blk_info=blk_info, st_info=st_info, chk=chk, lu=lu, open_public=open_public, summary=summary, prog_agg=dict(agg), BLK=BLK,
                 viol_h=len(viol_h), exc=[(x["tag"], x["block"], x["floors"], x["band"], x["side"], round(x["area"])) for x in exc]), open(SP + r"\tables.pkl", "wb"))
print("tables saved")
