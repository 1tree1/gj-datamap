"""K5 면적표·획지계획표·도로계획표 계산 — 모든 합계가 구역 총면적에 닫히도록 검증한다.
입력: lots.pkl · clean_mass.pkl · network.pkl · context.pkl · tables.pkl(앞 단계 도로 정보)
출력: scratch/tables_clean.pkl, work/20261005_plan_clean/tables/*.csv"""
import pickle, sys, csv, os, math, collections
import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union
import os as _os; SP = _os.environ.get("PLAN_SP", r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad")   # 입력 pkl 폴더. 재현 시 PLAN_SP=<work/20261005_plan_clean/data>
PM = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts"
OUT = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean"
sys.path.insert(0, PM)
from geomkit import polys
from plan_meta import PROGRAMS, PROG_BY_KEY

LP = pickle.load(open(SP + r"\lots.pkl", "rb")); M = pickle.load(open(SP + r"\clean_mass.pkl", "rb"))
C = pickle.load(open(SP + r"\context.pkl", "rb")); NET = pickle.load(open(SP + r"\network.pkl", "rb")); T0 = pickle.load(open(SP + r"\tables.pkl", "rb"))
U = C["U"]; LOTS, PARKS = LP["LOTS"], LP["PARKS"]; BUILD = M["BUILD"]
os.makedirs(OUT + r"\tables", exist_ok=True)

# ══ 1. 대상지 면적표 ═══════════════════════════════════════════════════════════
PK = {d["name"]: d for d in PARKS}
other_park = PK["Plaza D"]["area"] + LP["plaza"].area
site = dict(
    park_A=PK["Park A"]["area"], park_B=PK["Park B"]["area"], park_C=PK["Park C"]["area"], park_other=other_park, water=0.0,
    road_veh=LP["veh"].area, road_ped=LP["ped"].area + LP["lane"].area,
    lots=[(d["no"], d["area"]) for d in LOTS])
site["park_total"] = site["park_A"] + site["park_B"] + site["park_C"] + site["park_other"] + site["water"]
site["road_total"] = site["road_veh"] + site["road_ped"]
site["lot_total"] = sum(a for _, a in site["lots"])
site["planned"] = site["park_total"] + site["road_total"] + site["lot_total"]
site["U"] = U.area
site["closure_diff"] = site["planned"] - U.area
print("면적표 닫힘: 계획부지 %.1f / U %.1f (차 %.3f)" % (site["planned"], U.area, site["closure_diff"]))

# ══ 2. 시설별 면적(연면적) ═════════════════════════════════════════════════════
ROWS = [  # key, English, 한글
    ("office", "Office / Commercial", "업무·상업시설"), ("creative", "Creative Industry", "창조산업시설"),
    ("civic", "Cultural / Edu / Civic", "문화·교육·공공시설"), ("retail", "Retail / F&B", "판매·음식시설"),
    ("hotel", "Hotel / Hospitality", "숙박시설"), ("leisure", "Leisure / Recreation", "여가·오락·체육시설"),
    ("resi", "Residential", "주거시설"), ("heritage", "Heritage (relocated station)", "역사유산(구 역사 이전)"),
    ("visitor", "Visitor Support", "관광지원시설"), ("parking", "Parking Structure", "주차전용건축물")]
CAT2ROW = {"상업·업무": "office", "창조산업": "creative", "문화·교육·공공": "civic", "판매·음식": "retail", "여가·오락·체육": "leisure",
           "주거": "resi", "역사유산": "heritage", "교통·방문자": "visitor"}
gfa = collections.defaultdict(float); fp_tot = 0.0; park_fac = collections.OrderedDict()
by_lot = collections.defaultdict(lambda: dict(n=0, fp=0.0, gfa=0.0, maxf=0, maxh=0.0, rows=collections.defaultdict(float), names=collections.OrderedDict()))
piece_rows = []
for b in BUILD:
    a, n = b["area"], b["floors"]
    if b["role"] == "공원시설":
        park_fac.setdefault(b["lot"], 0.0); park_fac[b["lot"]] += a * n; continue
    host = "parking" if b["role"] == "주차" else CAT2ROW[b["cat"]]
    if b["retail_ground"]:
        parts = [("retail", a), (host, a * (n - 1))]
    else:
        parts = [(host, a * n)]
    for r, v in parts: gfa[r] += v
    fp_tot += a
    L = by_lot[b["lot_no"]]
    L["n"] += 1; L["fp"] += a; L["gfa"] += a * n; L["maxf"] = max(L["maxf"], n); L["maxh"] = max(L["maxh"], b["h"])
    for r, v in parts: L["rows"][r] += v
    L["names"].setdefault(b["name"], []).append((n, a))
    piece_rows.append(dict(lot_no=b["lot_no"], lot=b["lot"], name=b["name"], use=b["use"], cat=b["cat"], role=b["role"], floors=n, floor_h=b["floor_h"], h=b["h"],
                           footprint=round(a, 1), gfa=round(a * n, 1), retail_ground="Y" if b["retail_ground"] else ""))
gfa_total = sum(gfa.values()); gfa_excl_parking = gfa_total - gfa["parking"]
park_fac_total = sum(park_fac.values())
fac = dict(rows=[(k, e, kr, gfa.get(k, 0.0)) for k, e, kr in ROWS], total=gfa_total, total_excl_parking=gfa_excl_parking,
           far=gfa_total / site["lot_total"], far_excl_parking=gfa_excl_parking / site["lot_total"], coverage=fp_tot / site["lot_total"], footprint=fp_tot,
           park_fac=park_fac, park_fac_total=park_fac_total, total_incl_park=gfa_total + park_fac_total)
print("연면적 %.0f (주차 제외 %.0f), 건축면적 %.0f, FAR %.1f%%, BCR %.1f%%, 공원시설 %.0f" % (gfa_total, gfa_excl_parking, fp_tot, fac["far"] * 100, fac["coverage"] * 100, park_fac_total))
chk = sum(v for _, _, _, v in fac["rows"]); print("  행 합계 %.1f / 연면적 %.1f (차 %.3f)" % (chk, gfa_total, chk - gfa_total))

# ══ 3. 고도지구(참고) — 건물별 최대 중첩 고도지구의 최고높이 ═══════════════════════
GODO = [g for g in C["G"] if g["kind"] == "최고"]
def godo_of(geom):
    best = None
    for g in GODO:
        ov = geom.intersection(g["geom"]).area
        if ov > 0 and (best is None or ov > best[0]): best = (ov, g["godo_nm"], g["h_max"])
    return best
over = []; gm = {}
for b in BUILD:
    if b["role"] == "공원시설": continue
    g = godo_of(b["geom"])
    if g is None: continue
    b["godo"] = (g[1], g[2])
    if b["h"] > g[2] + 1e-6: over.append((b["lot_no"], b["name"], b["floors"], b["h"], g[1], g[2], b["area"] * b["floors"]))
over_gfa = sum(o[6] for o in over)
print("고도지구 최고높이 초과(참고): %d동 / 연면적 %.0f㎡ (총 %.0f㎡의 %.0f%%)" % (len(over), over_gfa, gfa_total, over_gfa / gfa_total * 100))
godo_lot = {}
for d in LOTS:
    ov = collections.Counter()
    for g in GODO:
        a = d["geom"].intersection(g["geom"]).area
        if a > 1: ov[(g["godo_nm"], g["h_max"])] += a
    tot = sum(ov.values()) or 1
    godo_lot[d["no"]] = sorted([(nm, h, a / tot) for (nm, h), a in ov.items()], key=lambda x: -x[2])

# ══ 4. 획지계획표 ══════════════════════════════════════════════════════════════
roads_raw = {}
for k, v in NET["streets"].items(): roads_raw[k] = v
for k, v in NET["lanes"].items(): roads_raw[k] = v
RNAME = {"A": "A가로", "B": "B가로", "C": "C가로", "D": "D가로", "S": "S축", "S2": "S2가로", "E": "E가로", "R6": "R6축", "R7": "R7", "R8": "R8", "R9": "R9",
         "L_E1": "골목 E1", "L_E2": "골목 E2", "L_N1": "골목 N1", "L_N2": "골목 N2", "L_N3": "골목 N3"}
RW = {k: v[1] for k, v in NET["STREETS"].items()}; RW.update({k: v[1] for k, v in NET["LANES"].items()})
def frontage(geom):
    out = []
    for k, g in roads_raw.items():
        if geom.buffer(1.5).intersection(g).area > 8: out.append((k, RW[k]))
    ords = ["A", "S", "B", "C", "D", "S2", "E", "R6", "R7", "R8", "R9"]
    out.sort(key=lambda t: (ords.index(t[0]) if t[0] in ords else 99, t[0]))
    return out
def parkfront(geom):
    return [p["name"] for p in PARKS if geom.buffer(1.5).intersection(p["geom"]).area > 8]

LOT_NOTE = {
    "공공체육·생활시설": "수변공원과 시청 사이 완충. 체육센터(2F)+생활SOC 복합동, 옥외 운동장",
    "청년주거 북동": "수변공원 남측, ㄷ자 둘레형 5F. 1층 근린생활", "청년주거 서": "종축 S 서변 ㅁ자 둘레형 6F, 두 곳 통경, 1층 근린생활",
    "청년주거 동": "ㄷ자 둘레형 4F", "청년주거 동남(연립)": "3층 연립형 바(골목마당)",
    "시청·의회 캠퍼스": "ㄷ자 본청(북·남 5F, 서 연결 3F) + 의회동 4F + 3F 시민동(원화로 가로벽·통경 2곳), 시민마당",
    "복합문화·영화관": "복합문화센터 4F + 영화관 3F + 서변 가로상점 3F, 문화광장", "청년창업·기업지원": "ㅁ자 6F, 북서 모서리 8F, 1층 판매·지원",
    "청년·주민 커뮤니티": "3층 소규모 동 6개(2×3) + 마을마당", "성동시장 클러스터": "2층 장옥 바 + 서변 3층 가로상점 + 삼층석탑 마당(r=22 m)",
    "체험판매 거리": "2층 점포 2열 + 체험 거리", "레지던시·공방 A": "사선(56°) 3층 바(레지던시·공방)", "레지던시·공방 B": "사선 3층 바", "레지던시·공방 C": "사선 3층 바",
    "구경주역·근대역사관": "구 역사 이전(기존 건물 형상 1,404㎡·2F, 근대역사관·전시장 겸용) + 역사 광장", "주차전용건축물": "주동 5F + 남·북 동 4F + 2F 판매·공방 라이너, 1단계 임시 평면주차",
    "관광지원시설": "3층 바(안내·환승 라운지) + 승강장 앞마당", "관광객 휴게·판매상가 W": "ㄱ자 둘레형 3F", "관광객 휴게·판매상가 E": "ㄱ자 둘레형 3F"}
PROGKEYS = {"구경주역·근대역사관": ["구경주역 이전", "경주 근대역사관·전시장"]}
lot_rows = []
for d in LOTS:
    L = by_lot[d["no"]]; fr = frontage(d["geom"]); pf = parkfront(d["geom"])
    keys = PROGKEYS.get(d["name"], [d["prog"]])
    pm = [PROG_BY_KEY[k] for k in keys if k in PROG_BY_KEY]
    gd = godo_lot[d["no"]]
    gd_txt = " / ".join("%s %.0f%%" % (nm.replace("지구", ""), p * 100) for nm, h, p in gd[:2]) if gd else "-"
    gd_min = min((h for nm, h, p in gd if p >= 0.15), default=None)
    lot_over = [o for o in over if o[0] == d["no"]]
    comp = "; ".join("%s %s" % (nm, "/".join("%dF×%.0f㎡" % (n, a) for n, a in v)) for nm, v in L["names"].items())
    lot_rows.append(dict(no=d["no"], id=d["id"], name=d["name"], use=d["use"], cat=d["cat"], area=d["area"], fp=L["fp"], bcr=L["fp"] / d["area"], gfa=L["gfa"], far=L["gfa"] / d["area"],
                         maxf=L["maxf"], maxh=L["maxh"], n_bld=L["n"], godo_txt=gd_txt, godo_min=gd_min, over_n=len(lot_over), over_gfa=sum(o[6] for o in lot_over),
                         frontage=fr, parkfront=pf, term=" / ".join(p["term"] for p in pm), law_use=" / ".join(p["use"] for p in pm), facility=" / ".join(p["facility"] for p in pm),
                         gosi=" / ".join(p["gosi"] for p in pm), note=LOT_NOTE.get(d["name"], ""), comp=comp, rows=dict(L["rows"])))

# ══ 5. 도로계획표 ═════════════════════════════════════════════════════════════
ORDER = ["A", "S", "B", "C", "D", "S2", "E", "R6", "R7", "R8", "R9", "L_E1", "L_E2", "L_N1", "L_N2", "L_N3"]
ROAD_CHAR = {
    "A": dict(group="차량", kind="보차공존 연결가로", cross=[("보도", 3.0), ("식재·자전거", 1.5), ("차도(양방 2차로)", 6.0), ("식재·자전거", 1.5), ("보도", 3.0)],
              mode="보차공존 30 km/h·자전거 포함", role="화랑로를 부지로 끌어들이는 진입 주가로. 시청 블록 남변과 수변공원 남변을 잇는다."),
    "S": dict(group="차량", kind="종축 공유가로(보행 우선)", cross=[("보행·식재", 5.0), ("공유 차도(셔틀·서비스)", 6.0), ("보행·식재", 5.0)],
              mode="보행 우선·셔틀·서비스·비상 차량만", role="폐선축(x≈219,730)과 평행한 60 m 동편 종축. 성동시장~시청~수변을 잇는 척추."),
    "B": dict(group="차량", kind="동서 그린 보행가로", cross=[("보도", 3.0), ("보차공존 차도", 6.0), ("보도", 3.0)],
              mode="보차공존(서비스·이면)", role="성동시장과 황오동을 잇는 동서 가로. 양측 녹지띠(Park B)로 연결녹지 역할."),
    "C": dict(group="차량", kind="북측 연결가로", cross=[("보도", 3.0), ("보차공존 차도", 6.0), ("보도", 3.0)],
              mode="보차공존", role="북성로 축 서·동 가로를 잇는 연결가로. 시청 블록과 청년주거 블록 사이."),
    "D": dict(group="차량", kind="북서 접속가로", cross=[("보도", 2.0), ("차도", 6.0), ("보도", 2.0)],
              mode="보차공존", role="시청 블록 북변. 북서 기존 골목(7 m·4 m)에 접속."),
    "S2": dict(group="차량", kind="남동 연결가로", cross=[("보도", 2.0), ("차도", 6.0), ("보도", 2.0)],
               mode="보차공존", role="기존 11 m 남북 가로를 연장. 주차전용건축물 진입 접근로."),
    "E": dict(group="차량", kind="남측 연결가로", cross=[("보도", 1.5), ("차도(일방)", 5.0), ("보도", 1.5)],
              mode="보차공존·일방", role="남측 기존 3 m 끊긴 틀선(y≈360,659)을 이어 관광상가 블록과 연결."),
    "R6": dict(group="보행", kind="사선 보행축(보행자전용)", cross=[("식재", 3.0), ("보행·휴게", 8.0), ("식재", 3.0)],
               mode="보행자전용·비상차량 4 m 확보", role="황오동에서 원화로·원효로 코너(고분 방향)로 대각선 관통. 역전광장·관광상가를 지난다."),
    "R7": dict(group="보행", kind="북단 사선 보행로", cross=[("식재", 3.0), ("보행", 8.0), ("식재", 3.0)],
               mode="보행자전용", role="종축에서 수변공원으로 꺾여 올라가는 보행 연결."),
    "R8": dict(group="보행", kind="수변 보행로", cross=[("식재", 2.0), ("보행·자전거", 6.0), ("식재", 2.0)],
               mode="보행자전용·자전거", role="북동 경계 내측을 따라 북천 방향으로 열리는 수변 보행로."),
    "R9": dict(group="보행", kind="북단 보행가로", cross=[("식재", 2.0), ("보행", 6.0), ("식재", 2.0)],
               mode="보행자전용", role="수변공원 남변을 따라 가는 보행가로."),
}
for k in ("L_E1", "L_E2", "L_N1", "L_N2", "L_N3"):
    ROAD_CHAR[k] = dict(group="골목", kind="보행자우선 골목", cross=[("보행·공유", 6.0)], mode="보행자우선·비상차량", role=NET["LANES"][k][2])
ST = T0["st_info"]
order_geoms = []; road_rows = []
for k in ORDER:
    g = roads_raw[k]
    excl = g.difference(unary_union(order_geoms)) if order_geoms else g
    order_geoms.append(g)
    st = ST[k]; rc = ROAD_CHAR[k]
    anchor = NET["STREETS"][k][4] if k in NET["STREETS"] else NET["LANES"][k][3]
    road_rows.append(dict(key=k, name=RNAME[k], group=rc["group"], kind=rc["kind"], w=RW[k], L=st["L"], area_excl=excl.area, area_raw=g.area, mode=rc["mode"],
                          cross=" + ".join("%s %.1f" % (a, b) for a, b in rc["cross"]), cross_list=rc["cross"], role=rc["role"], anchor=anchor.replace("[앵커] ", "앵커: ").replace("[스케치] ", "스케치: ").replace("[폐선] ", "폐선: "),
                          sketch_desc=st["desc"]))
road_excl_sum = sum(r["area_excl"] for r in road_rows)
print("도로 배타면적 합 %.1f / (차량+보행+골목) %.1f (차 %.3f)" % (road_excl_sum, site["road_total"], road_excl_sum - site["road_total"]))
for grp in ("차량", "보행", "골목"):
    print("  %s %.1f" % (grp, sum(r["area_excl"] for r in road_rows if r["group"] == grp)))

# ══ 6. 요약 지표(계획 가정 꼬리표 달아서 보고) ═══════════════════════════════════════
housing_gfa = gfa["resi"]
summary = dict(housing_gfa=housing_gfa, units36=housing_gfa * 0.70 / 36, units60=housing_gfa * 0.70 / 60,
               parking_gfa=gfa["parking"], park_spaces=gfa["parking"] / 32.0,
               open_public=site["park_total"] + sum(g.area for _, _, g in M["COURTS"]) + sum(g.area for _, _, g, c in M["OPEN"] if c in ("#ece7de", "#e9d9bd")),
               n_build=len(piece_rows))
print("주거 연면적 %.0f㎡ → 전용 70%% 가정 시 %.0f세대(36㎡)/%.0f세대(60㎡), 주차전용건축물 %.0f㎡ → %.0f면(32㎡/대 가정)" % (housing_gfa, summary["units36"], summary["units60"], gfa["parking"], summary["park_spaces"]))

pickle.dump(dict(site=site, fac=fac, lot_rows=lot_rows, road_rows=road_rows, piece_rows=piece_rows, over=over, godo_lot=godo_lot, summary=summary, ROWS=ROWS, RNAME=RNAME), open(SP + r"\tables_clean.pkl", "wb"))

# ── CSV ──
def wcsv(name, rows, cols):
    with open(OUT + r"\tables\%s" % name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(cols)
        for r in rows: w.writerow([r.get(c, "") if isinstance(r, dict) else r[i] for i, c in enumerate(cols)] if isinstance(r, dict) else r)
wcsv("lots_clean.csv", [{"번호": r["no"], "획지": r["id"], "획지명": r["name"], "용도": r["use"], "분류": r["cat"], "획지면적_㎡": round(r["area"]), "건축면적_㎡": round(r["fp"]), "건폐율_pct": round(r["bcr"] * 100, 1),
                          "연면적_㎡": round(r["gfa"]), "용적률_pct": round(r["far"] * 100), "최고층수": r["maxf"], "최고높이_m": round(r["maxh"], 1), "접도": " ".join("%s(%gm)" % (RNAME[k], w) for k, w in r["frontage"]),
                          "고도지구_참고": r["godo_txt"], "고도지구초과동수": r["over_n"], "비고": r["note"]} for r in lot_rows],
     ["번호", "획지", "획지명", "용도", "분류", "획지면적_㎡", "건축면적_㎡", "건폐율_pct", "연면적_㎡", "용적률_pct", "최고층수", "최고높이_m", "접도", "고도지구_참고", "고도지구초과동수", "비고"])
wcsv("roads_clean.csv", [{"도로": r["name"], "구분": r["group"], "성격": r["kind"], "폭원_m": r["w"], "연장_m": round(r["L"]), "면적_㎡": round(r["area_excl"]), "통행방식": r["mode"], "단면": r["cross"], "역할": r["role"], "맥락연결": r["anchor"]} for r in road_rows],
     ["도로", "구분", "성격", "폭원_m", "연장_m", "면적_㎡", "통행방식", "단면", "역할", "맥락연결"])
wcsv("buildings_clean.csv", piece_rows, ["lot_no", "lot", "name", "use", "cat", "role", "floors", "floor_h", "h", "footprint", "gfa", "retail_ground"])
wcsv("facility_area.csv", [[kr, e, round(v), "%.1f%%" % (v / gfa_total * 100)] for k, e, kr, v in fac["rows"]] + [["연면적 합계", "Total GFA", round(gfa_total), "100%"]], ["시설", "English", "연면적_㎡", "비율"])
print("saved")

