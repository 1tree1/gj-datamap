"""S2 면적표·획지계획표·도로계획표 계산 — 모든 합계가 계획 경계에 닫히도록 검증. 입력 data/design.pkl → data/tables.pkl, tables/*.csv"""
import pickle, os, csv, collections, math
import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); OUT = os.path.join(HERE, "..")
os.makedirs(os.path.join(OUT, "tables"), exist_ok=True)
P = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
U, LOTS, PARKS, BUILD, ROADS, COURTS, OPEN, DECKS, ROOFG = P["U"], P["LOTS"], P["PARKS"], P["BUILD"], P["ROADS"], P["COURTS"], P["OPEN"], P["DECKS"], P["ROOFG"]

# ═ 1. 대상지 면적표 ═══════════════════════════════════════════════════════════════
PK = {d["name"]: d for d in PARKS}
road_veh = sum(r["g"].area for r in ROADS.values() if r["grp"] == "차량")
road_ped_pure = sum(r["g"].area for k, r in ROADS.items() if r["grp"] == "보행" and k != "PZ")
plaza = ROADS["PZ"]["g"].area
site = dict(park_A=PK["Park A"]["area"], park_B=PK["Park B"]["area"], park_C=PK["Park C"]["area"], park_D=PK["Park D"]["area"],
            road_veh=road_veh, road_ped=road_ped_pure, plaza=plaza, lots=[(d["no"], d["area"]) for d in LOTS])
site["park_total"] = site["park_A"] + site["park_B"] + site["park_C"] + site["park_D"]
site["road_total"] = road_veh + road_ped_pure + plaza
site["lot_total"] = sum(a for _, a in site["lots"])
site["planned"] = site["park_total"] + site["road_total"] + site["lot_total"]
site["U"] = U.area; site["closure_diff"] = site["planned"] - U.area
print("닫힘 %.1f / %.1f (차 %.3f)" % (site["planned"], U.area, site["closure_diff"]))

# ═ 2. 시설별 연면적 ═══════════════════════════════════════════════════════════════
ROWS = [("office", "Office / Commercial", "업무·상업시설"), ("creative", "Creative Industry", "창조산업시설"), ("civic", "Cultural / Edu / Civic", "문화·교육·공공시설"),
        ("retail", "Retail / F&B", "판매·음식시설"), ("hotel", "Hotel / Hospitality", "숙박시설"), ("leisure", "Leisure / Recreation", "여가·오락·체육시설"),
        ("resi", "Residential", "주거시설"), ("heritage", "Heritage (relocated station)", "역사유산(구 역사 이전)"), ("visitor", "Visitor Support", "관광지원시설"),
        ("parking", "Parking Structure", "주차전용건축물")]
CAT2ROW = {"상업·업무": "office", "창조산업": "creative", "문화·교육·공공": "civic", "판매·음식": "retail", "여가·오락·체육": "leisure", "주거": "resi", "역사유산": "heritage", "교통·방문자": "visitor"}
gfa = collections.defaultdict(float); fp_tot = 0.0
by_lot = collections.defaultdict(lambda: dict(n=0, fp=0.0, gfa=0.0, maxf=0, maxh=0.0, rows=collections.defaultdict(float), names=collections.OrderedDict()))
piece_rows = []
for b in BUILD:
    a, n = b["area"], b["floors"]
    host = "parking" if b["role"] == "주차" else CAT2ROW[b["cat"]]
    parts = [("retail", a), (host, a * (n - 1))] if b["retail_ground"] else [(host, a * n)]
    for r, v in parts: gfa[r] += v
    fp_tot += a
    L = by_lot[b["lot_no"]]; L["n"] += 1; L["fp"] += a; L["gfa"] += a * n; L["maxf"] = max(L["maxf"], n); L["maxh"] = max(L["maxh"], b["h"])
    for r, v in parts: L["rows"][r] += v
    L["names"].setdefault(b["name"], []).append((n, a))
    piece_rows.append(dict(lot_no=b["lot_no"], lot=b["lot"], name=b["name"], use=b["use"], cat=b["cat"], floors=n, floor_h=b["floor_h"], h=b["h"], footprint=round(a, 1), gfa=round(a * n, 1),
                           retail_ground="Y" if b["retail_ground"] else "", lifted_roof="Y" if b.get("lift") else ""))
gfa_total = sum(gfa.values())
fac = dict(rows=[(k, e, kr, gfa.get(k, 0.0)) for k, e, kr in ROWS], total=gfa_total, total_excl_parking=gfa_total - gfa["parking"], far=gfa_total / site["lot_total"],
           far_excl_parking=(gfa_total - gfa["parking"]) / site["lot_total"], coverage=fp_tot / site["lot_total"], footprint=fp_tot)
print("연면적 %.0f㎡ (주차 제외 %.0f) 건축면적 %.0f FAR %.1f%% BCR %.1f%%" % (gfa_total, fac["total_excl_parking"], fp_tot, fac["far"] * 100, fac["coverage"] * 100))

# ═ 3. 높이 20 m 기준 참고(이 안은 규제 미적용) — 도심 20 m 고도지구 89%·15 m 9.8%는 본 지구 일반값(좌표 미정합) ═══════════════
over = [(b["lot_no"], b["name"], b["floors"], b["h"], b["area"] * b["floors"]) for b in BUILD if b["h"] > 20.0 + 1e-6]
over_gfa = sum(o[4] for o in over); print("높이 20 m 초과(참고) %d동 / %.0f㎡" % (len(over), over_gfa))

# ═ 4. 획지계획표 ═══════════════════════════════════════════════════════════════════
ORDER = ["A", "B", "C", "D", "S", "PZ", "WG", "R10", "R6", "R8", "R9"]
def frontage(geom):
    out = []
    for k in ORDER:
        if geom.buffer(1.5).buffer(0).intersection(ROADS[k]["g"].buffer(0)).area > 8: out.append((k, ROADS[k]["w"]))
    return out
def parkfront(geom): return [p["name"] for p in PARKS if geom.buffer(1.5).buffer(0).intersection(p["geom"].buffer(0)).area > 8]
SHORT = {"공공체육·생활시설": "체육센터 2F + 생활SOC 3F + 옥외 운동장", "시청·의회 캠퍼스": "∩자 본청 5F·의회동 3F·시민 파빌리온 2F·시민마당·들어 올린 지붕",
         "청년주거(남향 판상)": "남향 평행 4동 6F·1층 생활상가·5F 스카이브리지", "복합문화·영화관": "문화 분동 2~4F + 영화관 3F·들어 올린 지붕",
         "청년창업·기업지원": "ㅁ자 5F·모서리 6F·1층 판매·지원", "청년·주민 커뮤니티": "3층 소동 6개·마을마당", "체험판매 거리": "2층 점포 2열·체험 거리",
         "레지던시·공방 A": "철도 사선(58°) 3층 바", "레지던시·공방 B": "철도 사선 3층 바", "성동시장 클러스터": "2층 장옥 바 + 서변 3층 가로상점 + 삼층석탑 마당(r=22 m)",
         "구경주역·근대역사관": "구 역사(이전) 2F(기존 형상 1,404㎡) + 역사 광장", "주차전용건축물": "주동 5F + 2F 판매 라이너, 임시 평면주차",
         "관광지원시설": "3층 바(안내·환승 라운지)·승강장 앞마당", "관광객 휴게·판매상가 E": "ㄱ자 둘레형 3F", "관광객 휴게·판매상가 W": "ㄱ자 둘레형 3F"}
USE = {"공공체육·생활시설": "공공체육·생활SOC", "시청·의회 캠퍼스": "공공청사(시청·의회)", "청년주거(남향 판상)": "청년주거", "복합문화·영화관": "문화시설(복합문화·영화관)",
       "청년창업·기업지원": "업무(청년창업·기업지원)", "청년·주민 커뮤니티": "주민공동시설(커뮤니티)", "체험판매 거리": "근린상업(체험판매)", "레지던시·공방 A": "창작시설(레지던시·공방)",
       "레지던시·공방 B": "창작시설(레지던시·공방)", "성동시장 클러스터": "근린상업(성동시장 연계)", "구경주역·근대역사관": "문화·역사(구 역사·근대역사관)", "주차전용건축물": "주차전용건축물",
       "관광지원시설": "관광지원시설", "관광객 휴게·판매상가 E": "관광 근린상업(휴게·판매)", "관광객 휴게·판매상가 W": "관광 근린상업(휴게·판매)"}
lot_rows = []
for d in LOTS:
    L = by_lot[d["no"]]
    comp = "; ".join("%s %s" % (nm, "/".join("%dF×%.0f㎡" % (n, a) for n, a in v)) for nm, v in L["names"].items())
    lot_rows.append(dict(no=d["no"], id=d["id"], name=d["name"], use=d["use"], cat=d["cat"], area=d["area"], fp=L["fp"], bcr=L["fp"] / d["area"], gfa=L["gfa"], far=L["gfa"] / d["area"],
                         maxf=L["maxf"], maxh=L["maxh"], n_bld=L["n"], frontage=frontage(d["geom"]), parkfront=parkfront(d["geom"]), over_n=len([o for o in over if o[0] == d["no"]]),
                         short=SHORT[d["name"]], use_txt=USE[d["name"]], comp=comp, rows=dict(L["rows"]), note=d["note"]))

# ═ 5. 도로계획표 ══════════════════════════════════════════════════════════════════
CH = {
    "A": dict(mode="보차공존 30 km/h·자전거 포함", cross=[("보도", 4.0), ("식재·자전거", 2.0), ("차도(양방 2차로)", 8.0), ("식재·자전거", 2.0), ("보도", 4.0)],
              role="부지를 동서로 관통하는 차량 주가로. 성동시장·황오동 방향 기존 가로에 접속하고 종축 S·사선 R6과 교차."),
    "B": dict(mode="보차공존·일방", cross=[("보도", 2.5), ("차도(일방)", 5.5), ("보도", 2.5)], role="A가로에서 남쪽 관문(관광지원·주차)으로 내려가는 연결가로."),
    "C": dict(mode="보차공존 30 km/h", cross=[("보도", 3.5), ("차도", 9.0), ("보도", 3.5)], role="북측 시청 블록 북변을 지나 사선 가로 D로 이어지는 연결가로."),
    "D": dict(mode="보차공존 30 km/h", cross=[("보도", 3.5), ("차도", 10.5), ("보도", 3.5)], role="C가로에서 북동 경계로 뻗는 사선 가로. 창작 허브와 주거·체육 블록을 가른다."),
    "S": dict(mode="보행자전용 (상부 공중가로 T)", cross=[("보행·식재", 6.5)], role="폐선 노반 방향의 종축. 지상은 보행 중심가로, 상부에 +4.5~18 m 공중가로 T가 겹친다."),
    "PZ": dict(mode="보행자전용 광장·비상차량", cross=[("보행·광장", 60.0)], role="부지를 서쪽 경계(성동시장 방향)에서 동쪽 경계(황오동 방향)까지 가로지르는 폭 60 m의 동서 중앙 보행가로. 레일 흔적 포장으로 철도 기억을 드러내고 종축 S와 십자로 만난다."),
    "WG": dict(mode="보행자전용(수목 식재 포장)", cross=[("보행·광장", 56.0)], role="시청 블록 남쪽의 쐐기 모양 보행 우선 광장. 수목을 심은 포장 광장이며 곡선 녹지띠·고분 언덕(Park B)과 맞닿는다."),
    "R10": dict(mode="보행자우선", cross=[("보행", 10.5)], role="주거·문화 블록 사이 동서 보행가로."),
    "R6": dict(mode="보행자전용·비상차량 4 m 확보", cross=[("식재", 3.5), ("보행·휴게", 11.5), ("식재", 3.5)], role="철도 사선 방향(남서~북동) 보행축. 구 역사·레지던시·성동시장 사이를 대각선으로 잇는다."),
    "R8": dict(mode="보행자전용", cross=[("식재", 2.5), ("보행·자전거", 5.5)], role="북단 수변공원 둘레 보행로."),
    "R9": dict(mode="보행자전용", cross=[("식재", 2.5), ("보행·자전거", 5.5)], role="동측 경계를 따라 북천 방향으로 열리는 보행로."),
}
road_rows = []
for k in ORDER:
    r = ROADS[k]; c = CH[k]; L = r["g"].area / r["w"]
    touch = r["g"].intersection(U.exterior.buffer(1.0)); n_t = len([p for p in (touch.geoms if touch.geom_type.startswith("Multi") else [touch]) if p.area > 1.0])
    road_rows.append(dict(key=k, name=r["nm"], group=r["grp"], kind=r["kind"], w=r["w"], L=L, area_excl=r["g"].area, mode=c["mode"], cross=" + ".join("%s %.1f" % (a, b) for a, b in c["cross"]),
                          cross_list=c["cross"], role=c["role"], anchor="경계 접속 %d개소(기존 가로 접속은 좌표 정합 후 확정)" % n_t))
print("도로 합 %.1f / %.1f" % (sum(r["area_excl"] for r in road_rows), site["road_total"]))

# ═ 6. 요약 지표 ══════════════════════════════════════════════════════════════════
hg = sum(b["area"] * (b["floors"] - (1 if b["retail_ground"] else 0)) for b in BUILD if b["cat"] == "주거")   # 주거 층만
house_foot = sum(b["area"] for b in BUILD if b["cat"] == "주거")
deck_len = {d["name"]: sum(math.dist(p[:2], q[:2]) for p, q in zip(d["pts"], d["pts"][1:])) for d in DECKS}
deck_area = sum(l * d["w"] for l, d in zip(deck_len.values(), DECKS))
roofg_area = sum(g.area for _, g, _ in ROOFG)
open_pub = site["park_total"] + sum(g.area for _, _, g in COURTS) + sum(g.area for _, _, g, c in OPEN if c in ("#ece7de", "#e4dccb", "#cfe6b4"))
summary = dict(housing_gfa=hg, units_P=hg * 0.70 / 33.6, units_Q=hg * 0.70 / 38.4, units36=hg * 0.70 / 36, units60=hg * 0.70 / 60,
               parking_gfa=gfa["parking"], park_spaces=gfa["parking"] / 32.0, city_gfa=sum(b["area"] * b["floors"] for b in BUILD if b["lot_no"] == [d for d in LOTS if d["name"] == "시청·의회 캠퍼스"][0]["no"]),
               deck_len=sum(deck_len.values()), deck_area=deck_area, roofg_area=roofg_area, open_pub=open_pub, n_build=len(piece_rows), n_lift=len([b for b in BUILD if b.get("lift")]), over_gfa=over_gfa)
print("주거 층 연면적 %.0f → 전용 70%%: P %.0f / Q %.0f / 36㎡ %.0f / 60㎡ %.0f세대 | 시청 %.0f㎡ | 주차 %.0f㎡→%.0f면 | 공중가로·데크 연장 %.0f m 면적 %.0f㎡ | 옥상 녹지 %.0f㎡ | 들어 올린 지붕 %d동" % (
    hg, summary["units_P"], summary["units_Q"], summary["units36"], summary["units60"], summary["city_gfa"], gfa["parking"], summary["park_spaces"], summary["deck_len"], deck_area, roofg_area, summary["n_lift"]))
pickle.dump(dict(site=site, fac=fac, lot_rows=lot_rows, road_rows=road_rows, piece_rows=piece_rows, over=over, summary=summary, ROWS=ROWS, deck_len=deck_len), open(os.path.join(D, "tables.pkl"), "wb"))

def wcsv(name, rows, cols):
    with open(os.path.join(OUT, "tables", name), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(cols)
        for r in rows: w.writerow([r.get(c, "") for c in cols])
wcsv("lots.csv", [{"번호": r["no"], "획지명": r["name"], "용도": r["use_txt"], "분류": r["cat"], "획지면적_㎡": round(r["area"]), "건축면적_㎡": round(r["fp"]), "건폐율_pct": round(r["bcr"] * 100, 1), "연면적_㎡": round(r["gfa"]),
                    "용적률_pct": round(r["far"] * 100), "최고층수": r["maxf"], "최고높이_m": round(r["maxh"], 1), "접도": " ".join("%s(%gm)" % (ROADS[k]["nm"], w) for k, w in r["frontage"]), "구성": r["short"]} for r in lot_rows],
     ["번호", "획지명", "용도", "분류", "획지면적_㎡", "건축면적_㎡", "건폐율_pct", "연면적_㎡", "용적률_pct", "최고층수", "최고높이_m", "접도", "구성"])
wcsv("roads.csv", [{"도로": r["name"], "구분": r["group"], "성격": r["kind"], "폭원_m": r["w"], "연장_m": round(r["L"]), "면적_㎡": round(r["area_excl"]), "통행방식": r["mode"], "단면": r["cross"], "역할": r["role"]} for r in road_rows],
     ["도로", "구분", "성격", "폭원_m", "연장_m", "면적_㎡", "통행방식", "단면", "역할"])
wcsv("buildings.csv", piece_rows, ["lot_no", "lot", "name", "use", "cat", "floors", "floor_h", "h", "footprint", "gfa", "retail_ground", "lifted_roof"])
wcsv("facility_area.csv", [{"시설": kr, "English": e, "연면적_㎡": round(v), "비율": "%.1f%%" % (v / gfa_total * 100)} for k, e, kr, v in fac["rows"]] + [{"시설": "연면적 합계", "English": "Total GFA", "연면적_㎡": round(gfa_total), "비율": "100%"}],
     ["시설", "English", "연면적_㎡", "비율"])
wcsv("decks.csv", [{"명칭": d["name"], "구분": d["kind"], "폭_m": d["w"], "연장_m": round(deck_len[d["name"]]), "높이_m": "%.1f~%.1f" % (min(p[2] for p in d["pts"]), max(p[2] for p in d["pts"])), "비고": d["note"]} for d in DECKS],
     ["명칭", "구분", "폭_m", "연장_m", "높이_m", "비고"])
print("saved")
