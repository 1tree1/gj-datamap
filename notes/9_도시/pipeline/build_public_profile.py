"""일반인용 '경주와 구경주역 한눈에' 사실표 — 지도를 확대하듯 경주시(S3) → 원도심(S2) → 부지(S1) 세 단계로 숫자를 모은다.

원칙
  - 단계마다 숫자를 섞지 않는다(CLAUDE.md §3.3). 경주시 통계로 부지 용도를 주장하지 않는다.
  - 한 항목 = 질문 하나 + 숫자 하나 + 쉬운 문장 + 익숙한 단위로 바꾼 비교 + 출처·등급.
  - 걸어서 몇 분은 시속 4 km(분당 약 67 m) 가정, 축구장 1면은 105 × 68 m = 7,140㎡.
  - 거리는 모두 직선거리다. 길로 걸으면 더 길다(특히 폐선 부지를 가로지를 때).

입력(모두 로컬, 2026-09 수집)
  archive/C_data/raw/vworld_emd_gj.geojson        경주시 56개 동·읍·면 경계 (V-World, T2)
  archive/C_data/raw/molit_jijeok_stats_20251231.csv  국토교통부 지적기본통계(2025-12-31, C-038, T2) — 경주·서울 면적
  archive/C_data/raw/vworld_uq111_city.geojson    경주시 전역 용도지역 (V-World LT_C_UQ111, T1 도형)
  archive/C_data/raw/vworld_uo301_city.geojson    경주시 전역 문화유산 보호 구역 (V-World LT_C_UO301, T1 도형)
  archive/C_data/raw/gj_tour_sites.geojson        경주시 관광지 현황 (경주시 REST + V-World 지오코딩, T2)
  archive/C_data/processed/*.json                 기본계획 전사(T1)·KOSIS(T2)·건축물대장(T1) 등 기존 처리본
  대지/(B020)연속수치지도_202609132098            국토지리정보원 연속수치지도 (T2) — 원도심 건물·도로·지명 주기
  연혁·세계유산·관광객·79,438㎡ — 2026-09-28 원문 대조(archive A-013~A-017, B-008, UNESCO WHC, 경주시 보도자료). 값은 코드 안 표에 출처와 함께 적었다.
출력
  archive/90_derived/public_profile_20260928.json
"""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import shapefile
from pyproj import Transformer
from shapely.geometry import LineString, Point, box, shape
from shapely.ops import transform, unary_union

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "archive" / "C_data" / "raw"
PROC = ROOT / "archive" / "C_data" / "processed"
DER = ROOT / "archive" / "90_derived"
NGII = ROOT / "대지" / "(B020)연속수치지도_202609132098"
OUT = DER / "public_profile_20260928.json"

T47 = Transformer.from_crs(4326, 5187, always_xy=True).transform
T57 = Transformer.from_crs(5179, 5187, always_xy=True).transform
T479 = Transformer.from_crs(4326, 5179, always_xy=True).transform
WALK = 4000 / 60          # m/분 (시속 4 km 가정)
FIELD = 105 * 68          # 축구장 1면 ㎡
S2_R = 1000               # 원도심 = 구역 중심 반경 1 km (CLAUDE.md §3.3 S2의 기하 대용치)


def gj(p):
    return json.load(open(p, encoding="utf-8"))


def g5187(f, t=T47):
    g = transform(t, shape(f["geometry"]))
    return g.buffer(0) if g.geom_type in ("Polygon", "MultiPolygon") else g   # 점에 buffer(0)을 하면 빈 도형이 된다


def walk_min(m):
    return round(m / WALK)


FACTS = []


def fact(fid, scale, q, value, unit, text, src, tier, compare=None, caveat=None, **kw):
    FACTS.append({"id": fid, "scale": scale, "q": q, "value": value, "unit": unit, "text": text, "compare": compare,
                  "src": src, "tier": tier, "caveat": caveat, **kw})


RS = gj(PROC / "report_stats.json")
MS = gj(PROC / "report_map_stats.json")
PE = gj(PROC / "pop_emd_table.json")
YC = gj(PROC / "youth_city.json")
WX = gj(PROC / "web_extras.json")
FR = gj(PROC / "fabric_report.json")

# ════════════════════════════════════════ S3 경주시 ════════════════════════════════════════
emd = gj(RAW / "vworld_emd_gj.geojson")["features"]
city = unary_union([g5187(f) for f in emd]).buffer(0)
city_km2 = city.area / 1e6
lz = RS["lifezone_density"]["rows"][0]                      # 기본계획 총합계: 행정구역 1,324.53㎢, 시가화 53.4㎢
# 면적 — 국토교통부 지적기본통계(2025-12-31, C-038) 대장·지목 행을 시군구별로 합친다(2026-09-28 조사 에이전트 값과 재계산 일치)
import csv as _csv
import io as _io
_jj = _csv.reader(_io.StringIO((RAW / "molit_jijeok_stats_20251231.csv").read_bytes().decode("cp949")))
next(_jj)
_ar = defaultdict(float)
for _r in _jj:
    if _r[1].startswith("경상북도 경주시"):
        _ar["경주"] += float(_r[7] or 0)
    elif _r[1].startswith("서울특별시"):
        _ar["서울"] += float(_r[7] or 0)
gj_km2, se_km2 = _ar["경주"] / 1e6, _ar["서울"] / 1e6
fact("city_area", "S3", "경주는 얼마나 넓은가", round(gj_km2, 2), "㎢",
     f"경주시는 약 {gj_km2:,.0f}㎢로 서울({se_km2:,.0f}㎢)의 약 {gj_km2 / se_km2:.1f}배 넓이다.",
     "국토교통부 지적기본통계집계 2025-12-31(공공데이터포털 15063997) 시군구 합계 — 서울도 같은 파일", "T2",
     compare=f"서울의 약 {gj_km2 / se_km2:.1f}배", ratio_seoul=round(gj_km2 / se_km2, 2), seoul_km2=round(se_km2, 2), calc_city_km2=round(city_km2, 1),
     caveat=f"같은 기준일의 경주시 누리집 값은 1,324.86㎢로 0.13㎢ 차이가 난다(원인 미상). 2030 도시기본계획(2013년 기준)은 {lz['area_km2']:,.2f}㎢. 지도 계산에 쓴 V-World 경계는 {city_km2:,.1f}㎢다.")

# 용도지역 — 건물이 모이는 땅(주거·상업·공업)은 얼마나 되나
uq = [f for f in gj(RAW / "vworld_uq111_city.geojson")["features"] if f["properties"].get("sigg_name") == "경주시"]
grp = defaultdict(list)
for f in uq:
    n = f["properties"]["uname"]
    k = "주거" if "주거" in n else "상업" if "상업" in n else "공업" if "공업" in n else "녹지" if "녹지" in n else "기타"
    grp[k].append(g5187(f))
zarea = {k: unary_union(v).intersection(city).area / 1e6 for k, v in grp.items()}
built = zarea.get("주거", 0) + zarea.get("상업", 0) + zarea.get("공업", 0)
urban = sum(zarea.values())
fact("city_built", "S3", "그 넓은 땅 가운데 건물이 모인 곳은 얼마나 되나", round(built / city_km2 * 100, 1), "%",
     f"주거·상업·공업지역을 모두 합쳐도 {built:,.1f}㎢, 시 면적의 {built / city_km2 * 100:.1f}%다. 나머지는 산·들·녹지다.",
     "V-World 용도지역(LT_C_UQ111, 2026-09-28 수집) 경주시 폴리곤 1,294개를 시 경계로 잘라 잰 면적", "T1",
     compare=f"100 중 약 {round(built / city_km2 * 100)}", by_zone_km2={k: round(v, 2) for k, v in zarea.items()}, urban_share_pct=round(urban / city_km2 * 100, 1),
     caveat="2030 기본계획의 시가화면적 53.4㎢(2014년 기준, 4.0%)와 같은 크기다. 비도시지역(관리·농림·자연환경보전)은 이 자료에 없다.")
fact("city_commercial", "S3", "가게를 지을 수 있는 상업지역은 얼마나 되나", round(zarea.get("상업", 0) / city_km2 * 100, 2), "%",
     f"상업지역은 {zarea.get('상업', 0):.2f}㎢, 시 면적의 {zarea.get('상업', 0) / city_km2 * 100:.2f}%다.",
     "V-World 용도지역(LT_C_UQ111, 2026-09-28 수집)", "T1", compare=f"약 {round(city_km2 / zarea.get('상업', 1), -1):.0f}분의 1")

# 문화유산 보호 구역
uo = [f for f in gj(RAW / "vworld_uo301_city.geojson")["features"] if f["properties"].get("sigg_name") == "경주시"]
her_all = unary_union([g5187(f) for f in uo]).intersection(city)
her_nat = unary_union([g5187(f) for f in uo if f["properties"]["uname"] == "국가지정문화재구역"]).intersection(city)
cnt = Counter(f["properties"]["uname"] for f in uo)
fact("city_heritage", "S3", "문화유산 때문에 개발이 제한되는 땅은 얼마나 되나", round(her_all.area / city_km2 / 1e6 * 100, 1), "%",
     f"문화유산 구역과 그 주변 보존지역을 합치면 {her_all.area / 1e6:,.1f}㎢, 시 면적의 {her_all.area / 1e6 / city_km2 * 100:.1f}%다. "
     f"이 가운데 국가지정문화유산 구역만 {her_nat.area / 1e6:,.1f}㎢다.",
     "V-World 문화유산 보호 구역(LT_C_UO301, 2026-09-28 수집) 경주시 폴리곤 합집합", "T1",
     compare=f"건물이 모인 땅({built:,.0f}㎢)보다 {'넓다' if her_all.area / 1e6 > built else '좁다'}", counts=dict(cnt), nat_km2=round(her_nat.area / 1e6, 1),
     caveat="고도지구(높이 제한)는 따로다. V-World에 없는 고도보존육성지구 등 3종은 빠져 있다.")

# 사람
pc = PE["47130"]
pop = RS["pop_actual"]["pop_2026_08"]
fact("city_pop", "S3", "몇 명이 사나, 늘고 있나", pop, "명",
     f"2026년 8월 주민등록 인구는 {pop:,}명이다. 10년 전보다 {abs(pc['chg_10y_pct'])}% 줄었다.",
     "행정안전부 주민등록인구 (KOSIS DT_1B04005N, 2026-08)", "T2",
     compare=f"2030 도시기본계획의 목표 인구 320,000명보다 {320000 - pop:,}명 적다", chg_10y_pct=pc["chg_10y_pct"])
fact("city_age", "S3", "누가 사나", pc["pct_65"], "%",
     f"10명 중 3명이 65세 이상({pc['pct_65']}%)이고, 14세 이하는 {pc['pct_0_14']}%다.",
     "행정안전부 주민등록인구 (KOSIS, 2026-08)", "T2", compare="10명 중 3명", pct_0_14=pc["pct_0_14"], pct_20_39=pc["pct_20_39"])
net = YC["net"]["20-34세"]
fact("city_youth", "S3", "청년은 머무나", sum(net), "명",
     f"20–34세는 2020–2025년 6년 동안 다른 지역으로 {abs(sum(net)):,}명이 더 빠져나갔다(전입 − 전출). 20–24세가 매년 가장 많이 나간다.",
     "통계청 국내인구이동통계 (KOSIS DT_1B26002) 경주시 순이동", "T2", by_year=dict(zip(YC["mig_years"], net)))
ind = dict(YC["industry"])
tot_emp = YC["emp_total_k"]
fact("city_jobs", "S3", "무엇으로 먹고 사나", round(ind["광·제조업(BC)"] / tot_emp * 100), "%",
     f"취업자 {tot_emp:,.1f}천 명 가운데 제조업이 {ind['광·제조업(BC)']:.1f}천 명({ind['광·제조업(BC)'] / tot_emp * 100:.0f}%)으로 가장 많고, "
     f"도소매·숙박음식업이 {ind['도소매·숙박음식업(GI)']:.1f}천 명({ind['도소매·숙박음식업(GI)'] / tot_emp * 100:.0f}%)이다. 관광도시이면서 공업도시다.",
     "통계청 지역별고용조사 2026년 상반기 (KOSIS)", "T2", industry=ind)

# 세계유산·관광 — 2026-09-28 원문 대조(UNESCO WHC 목록, 경주시 보도자료). 숫자는 원문 그대로 적는다.
WH = [("석굴암과 불국사", 1995, "https://whc.unesco.org/en/list/736"), ("경주역사유적지구", 2000, "https://whc.unesco.org/en/list/976"),
      ("한국의 역사마을: 하회와 양동(양동마을)", 2010, "https://whc.unesco.org/en/list/1324"), ("한국의 서원(옥산서원)", 2019, "https://whc.unesco.org/en/list/1498")]
fact("city_world_heritage", "S3", "세계유산은 몇 곳인가", len(WH), "건",
     "경주에는 유네스코 세계유산 " + str(len(WH)) + "건의 구성요소가 있다: " + ", ".join(f"{n}({y})" for n, y, _ in WH) + ".",
     "UNESCO 세계유산센터 목록 736·976·1324·1498(2026-09-28 확인)", "T1", items=[{"name": n, "year": y, "url": u} for n, y, u in WH],
     caveat="흔히 '3건'이라고 쓰지만, 한국의 서원(2019)에 경주 옥산서원이 들어 있다.")
fact("city_visitors", "S3", "관광객은 얼마나 오나", 5020, "만 명(연인원)",
     "2025년 경주를 찾은 외지인 방문객은 연인원 약 5,020만 명으로, 2024년(약 4,709만 명)보다 늘었다. 외국인은 약 138만 명이다.",
     "경주시 보도자료 2026-01-12(한국관광 데이터랩 이동통신 추정) · 데이터랩 지역별 관광 현황 정의", "T2",
     compare=f"하루 평균 약 {5020e4 / 365 / 1e4:.0f}만 명 — 경주 인구의 절반을 조금 넘는 사람이 매일 오가는 셈",
     caveat="같은 사람이 여러 날 오면 날마다 따로 센 '연인원'이다. 데이터랩은 이 값을 관광객 총량으로 쓰지 말라고 적는다. 외국인 수치는 산출 원천이 적혀 있지 않다.")

# ════════════════════════════════════════ S2 원도심 ════════════════════════════════════════
zone = shape(gj(PROC / "gosi2026-8_zone_5187.geojson")["features"][0]["geometry"]).buffer(0)
cen = zone.centroid
S2 = cen.buffer(S2_R)


def ngii(layer):
    r = shapefile.Reader(str(NGII / layer))
    fl = [f[0] for f in r.fields[1:]]
    for s in r.iterShapeRecords():
        yield transform(T57, shape(s.shape.__geo_interface__)), dict(zip(fl, s.record))


fl_cnt = Counter()
for g, a in ngii("N3A_B0010000"):
    if S2.contains(g.centroid) and not zone.contains(g.centroid):
        fl_cnt[int(a.get("nmly") or 1) or 1] += 1
nb = sum(fl_cnt.values())
f1 = fl_cnt[1] / nb
f2 = fl_cnt[2] / nb
f3 = sum(v for k, v in fl_cnt.items() if k >= 3) / nb
fact("s2_low", "S2", "원도심은 얼마나 낮은가", round(f1 * 100), "%",
     f"부지 중심 1 km 안 건물 {nb:,}동 가운데 1층이 {f1 * 100:.0f}%, 2층이 {f2 * 100:.0f}%다. 3층 이상은 {f3 * 100:.0f}%뿐이다.",
     "국토지리정보원 연속수치지도 건물(2026-09-13 취득) 층수 — 부지 안 건물 제외", "T2",
     compare=f"10채 중 {round(f1 * 10)}채가 1층", floors={str(k): v for k, v in sorted(fl_cnt.items())}, max_floor=max(fl_cnt))

rl = Counter()
for g, a in ngii("N3L_A0020000"):
    c = g.intersection(S2)
    if c.is_empty:
        continue
    w = float(a.get("rvwd") or 0)
    rl["lt4" if 0 < w < 4 else "unk" if w <= 0 else "ge4"] += c.length
rtot = sum(rl.values())
fact("s2_alley", "S2", "길은 얼마나 좁은가", round(rl["lt4"] / rtot * 100), "%",
     f"반경 1 km 안 길 {rtot / 1000:.0f} km 가운데 폭 4 m가 안 되는 골목이 {rl['lt4'] / 1000:.0f} km({rl['lt4'] / rtot * 100:.0f}%)다. 교차로는 30–45 m마다 나온다.",
     "국토지리정보원 연속수치지도 도로중심선 폭(rvwd) · 교차 간격은 모델 범위 동별 중앙값", "T2",
     compare=f"길 10개 중 {round(rl['lt4'] / rtot * 10)}개꼴이 차 한 대 지나기 빠듯한 골목", km={k: round(v / 1000, 1) for k, v in rl.items()})

P = FR["fabric"]["parcels"]
fact("s2_lot", "S2", "집 한 채의 땅은 얼마나 되나", P["area_p50"], "㎡",
     f"대지 한 필지의 중앙값은 {P['area_p50']}㎡(약 {P['area_p50'] / 3.3058:.0f}평), 폭 약 {P['front_p50']:.0f} m × 깊이 약 {P['depth_p50']:.0f} m다. 필지의 {P['share_2plus_bldg'] * 100:.0f}%에는 건물이 두 채 이상 있다.",
     f"V-World 연속지적 지목 ‘대’ {P['n']:,}필지(부지 주변 동서 약 2.1 km)", "T2",
     compare=f"약 {P['area_p50'] / 3.3058:.0f}평 — 부지 구역(156,460㎡)이면 이런 필지가 약 {round(156460 / P['area_p50']):,}개 들어간다")

godo = gj(PROC / "godo_5187.geojson")["features"]
g_le20 = unary_union([shape(f["geometry"]).buffer(0) for f in godo if f["properties"].get("h_max") not in (None, "None") and float(f["properties"]["h_max"]) <= 20]).intersection(S2)
fact("s2_height", "S2", "높이는 얼마까지 지을 수 있나", round(g_le20.area / S2.area * 100), "%",
     f"반경 1 km 원의 {g_le20.area / S2.area * 100:.0f}%가 건물 높이를 20 m 이하로 묶은 고도지구다. 부지도 20 m 이하다(일부 15 m).",
     "V-World 용도지구(LT_C_UQ123) × 경상북도 고시 제2020-479호 고도지구 높이 · 부지 높이는 고시 제2026-8호", "T1",
     compare="대략 아파트 6–7층 높이", caveat="높이가 확인된 고도지구만 셌다(높이 미확인 폴리곤 제외). 문화유산 주변 허용기준 등 다른 높이 규제는 따로다.")

her2 = her_all.intersection(S2)
nat2 = [f for f in uo if f["properties"]["uname"] == "국가지정문화재구역" and g5187(f).intersects(S2)]
fact("s2_tombs", "S2", "고분·유적은 얼마나 가까이 있나", round(her2.area / S2.area * 100), "%",
     f"반경 1 km 원의 {her2.area / S2.area * 100:.0f}%가 문화유산 구역이나 그 보존지역이다(국가지정문화유산 구역 {len(nat2)}곳이 걸친다). 원도심 땅에서 언덕처럼 솟은 곳은 대부분 건물이 아니라 고분이다.",
     "V-World 문화유산 보호 구역(LT_C_UO301) · 솟은 지형은 연속수치지도 닫힌 등고선 고리 67개 중 60개가 문화유산 구역 안(모델 범위)", "T1",
     compare="신라 왕릉과 고분이 동네 사이사이에 있다", n_national=len(nat2))

BA = MS["bldg_age"]
fact("s2_old", "S2", "건물은 얼마나 오래됐나", BA["pct30"], "%",
     f"건축물대장이 있는 {BA['n']:,}필지 가운데 30년 넘은 건물이 선 필지가 {BA['pct30']}%, 40년 넘은 필지만 {BA['bins'][-1][1]:,}필지다.",
     "국토교통부 건축HUB 건축물대장 표제부(성동·황오·노서·노동·성건동) × 연속지적 PNU", "T1",
     compare=f"10필지 중 {round(BA['pct30'] / 10)}필지", caveat="동천·인왕동 대장은 아직 받지 않았다. 필지 안에서 가장 오래된 건물 기준이다.")

od = {PE[c]["name"]: PE[c] for c in PE if c != "47130"}
fact("s2_people", "S2", "원도심에 사람이 줄고 있나", od["황오동"]["chg_10y_pct"], "%",
     f"부지 동쪽 황오동은 10년 사이 인구가 {abs(od['황오동']['chg_10y_pct'])}% 줄었고, 65세 이상이 {od['황오동']['pct_65']}%다. 대릉원 쪽 황남동은 {abs(od['황남동']['chg_10y_pct'])}% 줄었다.",
     "행정안전부 주민등록인구 (KOSIS, 2026-08, 행정동) — 황오동은 옛 중부동 합산", "T2",
     compare="10년 새 3명 중 1명이 줄었다", dongs={k: {"chg_10y_pct": od[k].get("chg_10y_pct"), "pct_65": od[k]["pct_65"]} for k in ("황오동", "성건동", "황남동", "월성동") if k in od})

ff = WX["footfall"]
fact("s2_crowd", "S2", "사람들은 어디에 모이나", round(ff["G_seongdong_market_r200"]["per_ha"] / ff["D_zone"]["per_ha"]), "배",
     f"하루 유동인구를 1ha당으로 보면 성동시장 주변 200 m가 {ff['G_seongdong_market_r200']['per_ha']:,.0f}명, 폐역 부지 구역은 {ff['D_zone']['per_ha']:,.0f}명이다. 길 하나 건너 약 {ff['G_seongdong_market_r200']['per_ha'] / ff['D_zone']['per_ha']:.0f}배 차이다.",
     "소상공인시장진흥공단 소상공인365 상권분석(통신사 추정 유동인구, 2025.06–2026.06 일평균)", "T2",
     caveat="통신사 체류 추정치이지 걸어서 지나간 사람 수가 아니다.")

# ════════════════════════════════════════ S1 부지 ════════════════════════════════════════
GOSI = 156460
ys = np.arange(zone.bounds[1] + 1, zone.bounds[3], 2.0)
wid = [zone.intersection(LineString([(zone.bounds[0] - 5, y), (zone.bounds[2] + 5, y)])).length for y in ys]
ns = zone.bounds[3] - zone.bounds[1]
fact("s1_size", "S1", "부지는 얼마나 큰가", GOSI, "㎡",
     f"지구단위계획구역은 {GOSI:,}㎡로 축구장 약 {GOSI / FIELD:.0f}개 넓이다. 남북으로 {ns:,.0f} m(걸어서 약 {walk_min(ns)}분), 동서는 가장 넓은 곳이 {max(wid):,.0f} m다.",
     "경주시 고시 제2026-8호(2026-01-22) 결정조서 · 길이·폭은 고시 도면을 좌표에 맞춘 구역계에서 잰 값", "T1",
     compare=f"축구장 약 {GOSI / FIELD:.0f}개", ns_m=round(ns), ew_max_m=round(max(wid)), ew_median_m=round(float(np.median(wid))),
     caveat="경주시 보도자료(2025-12-18·2026-01-02, T2)의 ‘옛 경주역 일원 7만 9,438㎡’는 범위가 정의돼 있지 않다. 같은 사업의 시굴조사 추진계획은 156,460㎡로 적는다. 79,438㎡는 이 구역의 51%로, 알려진 하위 면적(특별계획구역 82,544·철도공단+코레일 소유 58,381) 어느 것과도 맞지 않는다.")

DT = FR["detour"]
dj = [d for d in FR["reading"]["dijkstra"] if "폐선" in d["case"]][0]
fact("s1_wall", "S1", "왜 동네를 가르나", DT["no_road_gap_m"], "m",
     f"옛 선로를 따라 {DT['no_road_gap_m']:,} m 동안 차가 건널 길이 없다. 부지 양쪽의 두 점(직선 {dj['straight_m']} m)을 길로 이으면 {dj['network_m']:,} m, 약 {dj['detour']}배를 돌아가야 한다.",
     "국토지리정보원 연속수치지도 도로중심선·철도중심선(T2), 2026-09-28 자체 계산", "T2",
     compare=f"걸어서 {walk_min(dj['straight_m'])}분 거리를 {walk_min(dj['network_m'])}분 돌아간다", overpass=DT["overpass"],
     straight_m=dj["straight_m"], network_m=dj["network_m"], detour=dj["detour"],
     caveat="차가 다니는 길 기준이다. 폭 3.2 m 육교가 하나 있지만 지금 열려 있는지 현장 확인 전이다.")

H = {h["k"]: h for h in WX["heritage"]}
sg = float(H["시굴조사 필요 면적"]["v"])
fact("s1_underground", "S1", "땅 밑에는 무엇이 있나", round(sg / GOSI * 100), "%",
     f"구역의 약 {sg / GOSI * 100:.0f}%({sg:,.0f}㎡)가 유물이 묻혀 있을 수 있어 시굴조사를 해야 하는 땅이다. 발굴까지 가면 비용 63–80억 원, 630–700일로 추정됐다.",
     "김권일(2026.02.27) 도시재생혁신포럼 발표 · 구)경주역일원 매장유산 시굴조사 추진계획", "T2",
     compare="10 중 9", caveat="시굴 결과가 나오기 전에는 무엇을 어디에 지을 수 있는지 확정할 수 없다.")

cls_kr = {"park": "근린공원", "commercial": "상업", "civic": "공공청사", "culture": "문화시설", "parking": "주차장"}
comp = defaultdict(int)
for r in MS["blocks"]["rows"]:
    comp[cls_kr[r[1]]] += r[3]
comp["도로"] = GOSI - sum(comp.values())
comp = dict(sorted(comp.items(), key=lambda kv: -kv[1]))
fact("s1_plan", "S1", "지금 무엇이 정해져 있나", round(comp["근린공원"] / GOSI * 100), "%",
     "2026년 1월 고시된 계획은 " + ", ".join(f"{k} {v / GOSI * 100:.0f}%" for k, v in comp.items()) + "로 나눴다. 주거용지는 없다.",
     "경주시 고시 제2026-8호(2026-01-22) 결정조서", "T1", composition_m2=comp,
     caveat="‘주거용지’라는 획지는 없지만, 동측 문화시설용지(문화1·특별계획구역5, 9,770㎡)의 허용용도가 ‘제2종일반주거지역에 건축할 수 있는 건축물’이라 공동주택도 지을 수 있다(고시 계획지침). 고시된 계획도 공모·변경 과정에서 바뀔 수 있다. 이 프로젝트는 구역 경계만 고정하고 나머지는 대안으로 비교한다.")

# 부지의 시간 — 2026-09-28 원문 대조(조선총독부 관보·국토교통부 고시 T1, 경주시·국토부 보도 T2, 김신재 2013 T3). 흔한 통념과 다른 날짜는 원문을 따른다.
HIST = [
    ("1918-12-28", "경주역 문을 열다", "서악~경주 1.2마일 협궤선 운수 개시. 첫 역은 지금 자리가 아니다(사정리, 김신재 2013 T3).", "조선총독부 관보 제1924호(1919-01-09)", "T1"),
    ("1936-12-01", "지금 자리로 옮기다", "울산~경주 구간을 표준궤로 바꾸며 새 경주 정거장을 열었다(관보 소재지 '경주읍 황오리', 김신재 2013 '사정리에서 성동리로').", "조선총독부고시 제640호(관보 제2955호) · 김신재(2013) 387쪽", "T1"),
    ("2010-11-01", "KTX 신경주역 개통", "경부고속철도 2단계 개통. 원도심에서 서쪽으로 직선 약 8.6 km 떨어진 건천읍에 섰다.", "한국철도공사 공사연혁", "T2"),
    ("2021-12-28", "경주역 문을 닫다", "영천~신경주·울산~포항 복선전철 개통으로 선로가 옮겨졌다. 마지막 열차는 12월 27일 밤 11시 16분 무궁화호.", "국토교통부고시 제2021-1234호 · 국토부 보도참고자료 2021-12-27 · 경주시 시정뉴스 2021-12-29", "T1"),
    ("2023-12-28", "'경주역' 이름이 KTX역으로", "신경주역이 경주역으로 이름을 바꿨다(고시 2023-02-06). 지금 '경주역'이라고 하면 건천읍의 KTX역이다.", "국토교통부고시 제2023-45호 · 경주시 보도자료 2023-12-28", "T1"),
    ("2025-12-18", "국가시범지구 후보", "옛 경주역 일원이 도시재생 국가시범지구 후보로 선정됐다.", "경주시 보도자료 2025-12-18", "T2"),
    ("2026-01-22", "지구단위계획 결정 고시", "구역 156,460㎡의 획지·용도·높이를 정했다(주거용지 없음).", "경주시 고시 제2026-8호", "T1"),
]
fact("s1_history", "S1", "이 땅은 어떤 시간을 지나왔나", 103, "년",
     "경주역은 1918년 12월 28일 문을 열어 2021년 12월 28일 닫기까지 103년 동안, 그중 85년(1936–2021)은 지금 자리에서 경주의 관문이었다.",
     "조선총독부 관보·국토교통부 고시(T1) · 코레일·경주시·국토부 발표(T2) · 김신재(2013, T3)", "T1",
     compare="103년 역, 85년 이 자리", events=[{"date": d, "title": t, "text": x, "src": s, "tier": tr} for d, t, x, s, tr in HIST],
     caveat="흔히 인용되는 '1918년 11월 1일'은 금호~서악 구간 개통일이다(관보 제1872호). 역사 건물의 준공일, 관보의 '황오리'와 김신재의 '성동리' 표기 차이는 아직 풀지 못했다.")
fact("s1_station", "S1", "옛 역사 건물은 문화유산인가", 0, "건",
     "옛 경주역 역사는 국가유산청 목록에 등록문화유산으로 올라 있지 않다. 코레일이 2013년 ‘철도기념물’로 지정했다.",
     "국가유산청 지정·등록 목록 OpenAPI(2026-09-28 조회 0건, T1) · 경주시 웹진 「매거진 경주」 150호(T2)", "T1",
     caveat="철도기념물은 문화유산법에 따른 지정이 아니다. 역사를 남길지는 법이 아니라 계획이 정할 문제다. 지정일 2013-10-01은 위키(T4)에만 있다.")

# 이웃 — 옛 역사 앞에서 직선거리
#   원도심 문화유산은 연속수치지도 지명 주기(N3P_H0040000, T2) 위치를 쓰고, 넓은 유적은 그 점을 품은 국가지정문화유산 구역의 가장 가까운 경계까지 잰다.
#   경주시 관광지 현황의 주소 지오코딩(ROAD)은 대릉원(2.7 km로 나옴)·계림처럼 넓은 유적에서 1–2 km 빗나갔다(2026-09-28 대조) → 원도심 유적에는 쓰지 않는다.
def fixenc(v):
    try:
        return v.encode("latin-1").decode("cp949")
    except Exception:
        return v


NAMES = defaultdict(list)
_r = shapefile.Reader(str(NGII / "N3P_H0040000"))
_fl = [f[0] for f in _r.fields[1:]]
for _s in _r.iterShapeRecords():
    _rec = dict(zip(_fl, _s.record))
    NAMES[fixenc(_rec["name"]).strip()].append(transform(T57, shape(_s.shape.__geo_interface__)))
NATP = [g5187(f) for f in uo if f["properties"]["uname"] == "국가지정문화재구역"]


def heritage_area(label):
    """지명 주기 점을 품은(없으면 30 m 안) 국가지정문화유산 구역들의 합집합 — 없으면 점 자체"""
    pts = NAMES[label]
    hit = [g for g in NATP if any(g.distance(q) <= 30 for q in pts)]
    return unary_union(hit) if hit else unary_union(pts)


st = [f for f in gj(PROC / "rail_stations_4326.geojson")["features"] if f["properties"]["lbl"] == "구경주역"][0]
stp = g5187(st)
tour = {f["properties"]["name"].strip(): g5187(f) for f in gj(RAW / "gj_tour_sites.geojson")["features"] if f.get("geometry")}
ch = [f for f in gj(PROC / "cityhall_sites_4326.geojson")["features"] if f["properties"]["cls"] == "main"][0]
gw = {f["properties"]["name"]: g5187(f) for f in gj(PROC / "gateways_4326.geojson")["features"]}
NB = [("성동시장", tour["성동시장"], "관광지 현황"), ("경주읍성", tour["경주읍성"], "관광지 현황"),
      ("황오동 고분", heritage_area("황오동고분(사적제512호)"), "지명 주기 + 문화유산 구역 경계"),
      ("대릉원", heritage_area("경주대릉원일원(사적제512호)"), "지명 주기 + 문화유산 구역 경계"),
      ("황리단길", tour["황리단길"], "관광지 현황"), ("첨성대", unary_union(NAMES["첨성대(국보제31호)"]), "지명 주기"),
      ("계림", unary_union(NAMES["계림(사적제19호)"]), "지명 주기"), ("동궁과 월지", heritage_area("경주동궁과월지(사적제18호)"), "지명 주기 + 문화유산 구역 경계"),
      ("경주 월성", tour["경주 월성"], "관광지 현황"), ("국립경주박물관", tour["국립경주박물관"], "관광지 현황"),
      ("경주시청(현 청사)", g5187(ch), "시 청사안내"), ("경주시외버스터미널", gw["경주시외버스터미널"], "V-World 장소검색"),
      ("경주역(KTX, 옛 신경주역)", gw["경주역(KTX, 구 신경주역)"], "V-World 장소검색"), ("보문관광단지", tour["보문관광단지"], "관광지 현황"),
      ("불국사", tour["불국사"], "관광지 현황")]
def label_pt(name, g):
    """지도에 이름을 붙일 점 — 지명 주기가 있으면 그 평균, 아니면 도형의 대표점"""
    key = {"황오동 고분": "황오동고분(사적제512호)", "대릉원": "경주대릉원일원(사적제512호)", "첨성대": "첨성대(국보제31호)",
           "계림": "계림(사적제19호)", "동궁과 월지": "경주동궁과월지(사적제18호)"}.get(name)
    if key and NAMES[key]:
        return [round(float(np.mean([q.x for q in NAMES[key]])), 1), round(float(np.mean([q.y for q in NAMES[key]])), 1)]
    q = g if g.geom_type == "Point" else g.representative_point()
    return [round(q.x, 1), round(q.y, 1)]


near = [{"name": n, "m": round(stp.distance(p)), "walk_min": walk_min(stp.distance(p)), "loc_src": src, "xy": label_pt(n, p)} for n, p, src in NB]
near.sort(key=lambda r: r["m"])
close = [r for r in near if r["walk_min"] <= 20]
fact("s1_neighbors", "S1", "옛 역사 앞에서 무엇이 가까운가", near[0]["m"], "m",
     "옛 경주역 역사 앞에서 직선으로 " + ", ".join(f"{r['name']} {r['m']:,} m(걸어서 약 {r['walk_min']}분)" for r in close) + ". 시장과 읍성, 고분이 걸어서 5–15분 거리다.",
     "위치: 연속수치지도 지명 주기(T2) · 국가지정문화유산 구역(V-World, T1) · 경주시 관광지 현황(T2) · 시 청사안내(T1) · V-World 장소검색 · 옛 역사 점은 OSM(T4)", "T2",
     neighbors=near, caveat="직선거리이고 넓은 유적은 가장 가까운 경계까지다. 부지 동쪽으로 갈 때는 선로 때문에 길이 더 길다.")

# 좌표·도형 요약(그림용)
out = {"made": "2026-09-28", "walk_m_per_min": round(WALK, 1), "field_m2": FIELD, "s2_radius_m": S2_R,
       "zone_centroid_5187": [round(cen.x, 1), round(cen.y, 1)], "station_5187": [round(stp.x, 1), round(stp.y, 1)],
       "city_km2_calc": round(city_km2, 2), "facts": FACTS}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for f in FACTS:
    print(f"[{f['scale']}] {f['id']:15s} {f['value']} {f['unit']:3s} | {f['text'][:120]}")
print("→", OUT)
