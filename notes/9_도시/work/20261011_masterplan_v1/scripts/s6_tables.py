"""S6 면적표·법정 녹지 검토표 — 모든 수치는 lots.pkl · masses.pkl · design_extra.pkl 에서 계산한다. 출력: tables/*.csv, tables/summary.json, tables/마스터플랜_v1_면적표.xlsx"""
import os, pickle, json, csv, math
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); T = os.path.join(HERE, "..", "tables")
os.makedirs(T, exist_ok=True)
L = pickle.load(open(os.path.join(D, "lots.pkl"), "rb")); M = pickle.load(open(os.path.join(D, "masses.pkl"), "rb")); X = pickle.load(open(os.path.join(D, "design_extra.pkl"), "rb"))
LOT, GRN, OP, WALKS, ROADS, U = L["LOT"], L["GRN"], L["OP"], L["WALKS"], L["ROADS"], L["U"]
masses, PR, PK = M["masses"], M["PR"], M["PK"]
PLZ, PAV, USE = X["PLZ"], X["PAV"], X["USE"]

def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []

S = {}
S["boundary"] = U.area
S["parcels_orig"] = sum(p.area for p in OP.values())
S["walk"] = sum(w.area for w in WALKS); S["road"] = sum(r.area for r in ROADS)
S["lots_total"] = sum(v["area"] for v in LOT.values()); S["green_total"] = sum(v["area"] for v in GRN.values())
S["close"] = S["boundary"] - (S["lots_total"] + S["green_total"] + S["walk"] + S["road"])

# 획지별
ZONE = {"공1": "제2종일반주거지역(특계4 상향 가정)", "주1": "제2종일반주거지역(상향 가정)"}
STD = {"공1": "업무시설 중 공공업무시설(공공청사)", "업1": "업무시설(일반업무시설)", "업2": "업무시설(일반업무시설)", "주1": "공동주택(청년·신혼 임대주택)",
       "문1": "문화 및 집회시설(공연장)", "문2": "문화 및 집회시설(전시장: 근대역사관)+관광 휴게시설", "문3": "관광 휴게시설+제1·2종 근린생활시설·판매시설",
       "문4": "문화 및 집회시설(창작스튜디오·체험관)", "문5": "문화 및 집회시설(창작스튜디오·체험관)", "상1": "제1·2종 근린생활시설·판매시설",
       "체1": "운동시설(생활체육시설)", "관1": "자동차 관련 시설(주차전용건축물)+관광 휴게시설"}
OKY = {"공1": "근린생활시설(편익시설), 문화 및 집회시설(회의·전시)", "업1": "제1·2종 근린생활시설(저층부 가로활성), 교육연구시설(직무교육)", "업2": "제1·2종 근린생활시설(저층부 가로활성), 교육연구시설(직무교육)",
       "주1": "제1종 근린생활시설, 노유자시설(어린이집), 주민공동시설", "문1": "근린생활시설, 문화 및 집회시설(다목적실)", "문2": "교육연구시설, 근린생활시설, 문화 및 집회시설(체험·교육)",
       "문3": "문화 및 집회시설(공방·체험)", "문4": "교육연구시설, 제2종 근린생활시설(공방), 작가 체류실(부속)", "문5": "교육연구시설, 제2종 근린생활시설(공방), 작가 체류실(부속)",
       "상1": "문화 및 집회시설(전시·체험)", "체1": "제1종 근린생활시설", "관1": "근린생활시설(관광안내), 운수시설(소규모 대합실)"}
rows = []
CAT = {}
for lot, comps in PR.items():
    mm = [m for m in masses if m["lot"] == lot]
    fp = sum(m["g"].area for m in mm)
    gfa = sum(c["gfa"] for c in comps)
    fl = max((m["floors"] for m in mm), default=0); hh = max((m["h"] for m in mm), default=0)
    a = LOT[lot]["area"]
    ratio = 0.10 if gfa >= 2000 else (0.07 if gfa >= 1000 else 0.05)
    lands_req = a * ratio
    pk_exempt = (lot == "관1")
    og_ratio = {"공1": 0.05, "문2": 0.10}.get(lot, 0.0)         # 공개공지: 업무 5%, 문화·집회·관광휴게 10% (연면적 5,000㎡ 이상 건축물)
    og_req = a * og_ratio
    plz = sum(p["area"] for p in PLZ if p["host"] == lot)
    open_area = a - fp
    rows.append(dict(code=lot, use_std=STD[lot], use_ok=OKY[lot], zone=ZONE.get(lot, "일반상업지역(상향 가정)"), area=a, fp=fp, bcr=fp / a, gfa=gfa, far=gfa / a, floors=fl, height=hh,
                     land_ratio=ratio, land_req=lands_req, og_ratio=og_ratio, og_req=og_req, open_area=open_area, plaza=plz, land_avail=open_area - plz, src=LOT[lot]["src"], pk_exempt=pk_exempt))
    for c in comps:
        CAT[c["cat"]] = CAT.get(c["cat"], 0.0) + c["gfa"]
S["lots"] = rows
S["cat_gfa"] = CAT
S["gfa_total"] = sum(CAT.values()); S["gfa_excl_parking"] = S["gfa_total"] - CAT.get("주차전용건축물", 0.0)
S["fp_total"] = sum(r["fp"] for r in rows)
S["far"] = S["gfa_total"] / S["lots_total"]; S["far_excl"] = S["gfa_excl_parking"] / S["lots_total"]; S["bcr"] = S["fp_total"] / S["lots_total"]
S["pav_area"] = sum(p.area for p in PAV)
# 공원·녹지
grows = []
for k, v in GRN.items():
    for i, pg in enumerate(polys(v["g"])):
        grows.append(dict(code=k if len(polys(v["g"])) == 1 else "%s-%d" % (k, i + 1), kind=v["kind"], name=v["name"], area=pg.area, width=None))
S["greens"] = grows
S["plazas"] = [dict(name=p["name"], host=p["host"], kind=p["kind"], area=p["area"]) for p in PLZ]
# 법정 기준(REG_green_ratio.md, 경주시 건축 조례 제22조·제29조, 도시공원법 시행규칙 별표 2, 지구단위계획수립지침 4-2-7·4-2-8)
B = S["boundary"]
S["legal"] = dict(
    landscape_min=sum(r["land_req"] for r in rows if not r["pk_exempt"]),       # 조경(조례 제22조): 획지 10%/7%, 주차전용건축물은 시장 인정 시 면제(관1 제외)
    landscape_all=sum(r["land_req"] for r in rows),
    open_space_min=sum(r["og_req"] for r in rows),                              # 공개공지(조례 제29조) — 조경으로 흡수 가능
    park_5pct=0.05 * B, park_15pct=0.15 * B, park_3m2=2400.0,
    planned_green=S["green_total"], planned_green_pct=S["green_total"] / B,
    recommended=sum(r["land_req"] for r in rows) + 0.05 * B)
S["legal"]["recommended_pct"] = S["legal"]["recommended"] / B
json.dump(S, open(os.path.join(T, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)

def w(name, header, data):
    with open(os.path.join(T, name), "w", encoding="utf-8-sig", newline="") as f:
        cw = csv.writer(f); cw.writerow(header); cw.writerows(data)
w("획지계획표.csv", ["획지", "지정용도(건축법 시행령 별표 1)", "허용·권장용도", "용도지역(상향 가정)", "대지면적㎡", "건축면적㎡", "건폐율%", "연면적㎡", "용적률%", "최고층수", "최고높이m", "조경 의무율", "조경 의무면적㎡", "공개공지 율", "공개공지㎡", "획지 내 공지㎡", "그중 광장·마당㎡", "원 필지"],
  [[r["code"], r["use_std"], r["use_ok"], r["zone"], round(r["area"], 1), round(r["fp"], 1), round(r["bcr"] * 100, 1), round(r["gfa"]), round(r["far"] * 100, 1), r["floors"], r["height"], "%d%%" % round(r["land_ratio"] * 100), round(r["land_req"], 1), ("%d%%" % round(r["og_ratio"] * 100)) if r["og_ratio"] else "-", round(r["og_req"], 1), round(r["open_area"], 1), round(r["plaza"], 1), "O%d" % r["src"]] for r in rows])
w("공원녹지계획표.csv", ["코드", "도시계획시설 종류", "명칭", "면적㎡"], [[g["code"], g["kind"], g["name"], round(g["area"], 1)] for g in grows])
print(json.dumps({k: (round(v, 1) if isinstance(v, float) else v) for k, v in S.items() if not isinstance(v, (list, dict))}, ensure_ascii=False, indent=1))
print({k: round(v, 1) if isinstance(v, float) else v for k, v in S["legal"].items()})
for r in rows: print(r["code"], round(r["area"]), round(r["fp"]), "%.1f%%" % (r["bcr"] * 100), round(r["gfa"]), "%.0f%%" % (r["far"] * 100), r["floors"], r["height"], round(r["land_req"]), round(r["land_avail"]))
print({k: round(v) for k, v in CAT.items()})
