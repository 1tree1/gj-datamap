"""관광객·시민이 경주에 오는 길과 경주 안의 수단 — 4개 문서(미래구상·전략계획·기본계획·경관계획) 전사 + KOSIS 국민여행조사 + 도로공사 AADT.

결론부터: 4개 문서 어디에도 '경주 방문 관광객의 입경 교통수단 비율' 통계는 없다. 있는 것은
  ① 진입 관문의 위치(경관계획 관문적 경관거점 · 전략계획 광역교통망 서술)          → gateways_4326.geojson (V-World 장소검색 좌표)
  ② 진입축의 차량 통행량(기본계획 2015 교통량표 — report_stats.road_vc에 이미 있음) · 고속도로 AADT 2021–2025(도로공사, C-008)
  ③ 관문 시설의 규모: 고속버스 노선·일 운행횟수(기본계획 p.216, KOBUS) · 철도 승차(기본계획 p.208, 이미 rail 카드)
  ④ 시민의 외부 이동수단 설문(미래구상 p.68, n=49) — 시민이지 관광객이 아님
  ⑤ 경주 안: 행정동별 버스노선 수(전략계획 p.61) · 권역별 수단통행 2019(전략계획 p.64, 부산울산권·대구권) · 수단분담 2007(기본계획, 이미 카드)
  ⑥ 전국 관광여행 지역간 이동수단(국민여행조사, KOSIS DT_113_STBL_1029530, 2023–2025) — 전국 평균, 경주 방문자 아님
출력: processed/arrival_transport.json · processed/gateways_4326.geojson"""
import sys, os, csv, json, urllib.parse, urllib.request
from _common import load_env, get_json, RAW, PROCESSED, save

GATES = [  # (이름, 종류, 검색어, 연결 축·규모 메모, 출처)
    ("경주IC", "고속도로 IC", "경주나들목", "경부고속도로 · 언양JCT~경주IC 45,807대/일(2015) · 활천~경주 54,887대/일(2025 AADT)", "전략계획 p.48 · 경관계획 관문적 경관거점 · 기본계획 p.207"),
    ("건천IC", "고속도로 IC", "건천나들목", "경부고속도로 · 경주IC~건천IC 42,808대/일(2015) · 55,015(2025 AADT)", "전략계획 p.48 · 경관계획 관문적 경관거점"),
    ("남경주IC", "고속도로 IC", "남경주나들목", "동해고속도로(울산~포항) · 범서~남경주 24,744대/일(2025 AADT)", "전략계획 p.48 · 경관계획 관문적 경관거점(추가)"),
    ("동경주IC", "고속도로 IC", "동경주나들목", "동해고속도로 · 남경주~동경주 23,050대/일(2025 AADT)", "전략계획 p.48"),
    ("북경주IC", "고속도로 IC", "북경주나들목", "새만금포항고속도로 · 임고~서포항 36,401대/일(2025 AADT) · 미래구상 p.30의 외곽순환 기점(남포항IC~)", "미래구상 p.9·30"),
    ("경주역(KTX, 구 신경주역)", "고속철도역", "신경주역", "KTX 경부선·동해선 · 2013 승차 1,111,982명 · 원도심에서 약 9km(미래구상 p.30)", "기본계획 p.201·208 · 경관계획 관문적 경관거점"),
    ("서경주역(신)", "일반철도역", "서경주역", "이설 동해선·중앙선 · 미래구상은 원도심의 기능적 관문으로 제안(p.31)", "미래구상 p.31·74 · 경관계획 관문적 경관거점(추가)"),
    ("경주고속버스터미널", "버스터미널", "경주고속버스터미널", "노서동 243-5 · 1일 약 91회(서울 17·부산 40~41·대구 36·광주 2·대전 2, KOBUS 2015)", "기본계획 p.202 · 전략계획 p.52"),
    ("경주시외버스터미널", "버스터미널", "경주시외버스터미널", "노서동 160-2 · 시민 설문에서 외부 이동수단 1위(30/49, 미래구상 p.68) · 실제 이용률 고속터미널보다 높음(현장관찰)", "전략계획 p.52 · 미래구상 p.67–68"),
    ("(옛)경주역", "폐역", None, "2021.12 폐역 · 2013 승차 560,123명 · 대상지", "기본계획 p.208"),
]
KOBUS = [["서울", 17], ["부산", 40.5], ["대구", 36], ["광주", 2], ["대전", 2]]
BUS_ROUTES = {"황오동": 76, "중부동": 75, "황남동": 74, "성건동": 69, "동천동": 41, "황성동": 40, "선도동": 27, "용강동": 25, "월성동": 22, "건천읍": 20, "천북면": 18, "현곡면": 15, "안강읍": 14, "강동면": 14, "불국동": 14, "외동읍": 11, "보덕동": 11, "산내면": 8, "서면": 7, "양남면": 7, "내남면": 7, "문무대왕면": 6, "감포읍": 4}
REGION_MODE = {"modes": ["도보", "승용차", "버스", "철도", "택시", "자전거", "기타"],
               "rows": {"수도권": [23.7, 31.1, 22.5, 13.9, 5.3, 1.6, 1.9], "부산울산권": [28.8, 37.6, 17.3, 5.4, 6.7, 1.4, 2.9], "대구광역권": [27.2, 41.1, 13.0, 4.5, 6.6, 2.2, 5.4], "광주광역권": [27.1, 44.9, 14.9, 1.1, 8.3, 1.2, 2.5], "대전세종충청권": [33.0, 42.5, 11.6, 1.0, 7.6, 1.7, 2.6]}}
CITIZEN = {"n_out": 49, "out": [["버스터미널", 30], ["기차역", 22], ["자가용", 19]],
           "n_term": 46, "term_issue": [["시내와 연결성 부족", 12], ["도로 혼잡", 11], ["고속·시외터미널 기능 분리", 9], ["(도보) 대중교통 환승 어려움", 5], ["(자차) 주차장 협소", 5], ["로컬 콘텐츠 부족", 4], ["숙박업소 협소·낙후", 3], ["편의시설 협소", 2]],
           "transit_score": {"전체": 2.7, "청년(27명)": 2.48, "중장년(28명)": 3.03}}
AADT_SEGS = ["활천~경주", "경주~건천", "건천~영천JCT", "범서~남경주", "남경주~동경주", "동경주~남포항"]


def main():
    load_env(); key = os.environ["VWORLD_KEY"]; dom = os.environ["VWORLD_DOMAIN"]; kk = os.environ.get("KOSIS_KEY")
    H = {"Referer": dom, "User-Agent": "Mozilla/5.0"}
    # ① 관문 좌표
    feats = []
    for name, kind, q, note, src in GATES:
        if q is None:
            lon, lat, how = 129.21868, 35.84499, "V-World 장소검색(경주역 철도시설)"
        else:
            r = get_json(f"https://api.vworld.kr/req/search?service=search&request=search&version=2.0&crs=EPSG:4326&size=10&query={urllib.parse.quote(q)}&type=place&bbox=129.0,35.65,129.6,36.05&format=json&key={key}", H, retries=1)["response"]
            items = ((r.get("result") or {}).get("items") or [])
            pick = items[0] if items else None
            if kind == "고속도로 IC": pick = next((i for i in items if i["title"].replace(" ", "") == q and "인공지명" in i.get("category", "")), pick)   # 나들목 지명점(정확) — 정류장·전광판 아님
            if kind == "고속철도역": pick = next((i for i in items if "철도" in i.get("category", "") and "정류장" not in i.get("category", "")), pick)
            if kind == "일반철도역": pick = next((i for i in items if "철도" in i.get("category", "") and "정류장" not in i.get("category", "")), pick)
            if not pick: print("  검색 실패:", q); continue
            lon, lat, how = float(pick["point"]["x"]), float(pick["point"]["y"]), f"V-World 장소검색 '{pick['title']}' ({pick.get('category','')})"
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                      "properties": {"name": name, "kind": kind, "note": note, "src_doc": src, "geocode": how, "lbl": name, "source": "위치 V-World 장소검색(2026-09-21, IC는 나들목 지명점) · 관문 지정·규모 서술은 4개 문서(T1·T2) 전사"}})
        print(f"  {name:<16} {lon:.5f},{lat:.5f}  {how[:60]}")
    save({"type": "FeatureCollection", "features": feats}, PROCESSED / "gateways_4326.geojson")
    # ② AADT
    aadt = {}
    for r in csv.DictReader(open(RAW / "ex_aadt_2021_2025.csv", encoding="utf-8-sig")):
        if r["구간명"] in AADT_SEGS: aadt[r["구간명"]] = {"line": r["노선"], "lanes": int(r["차로"]), "years": ["2021", "2022", "2023", "2024", "2025"], "v": [int(r[y]) for y in ["2021", "2022", "2023", "2024", "2025"]]}
    # ⑥ 국민여행조사 (전국)
    ntl = {}
    if kk:
        url = f"https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey={kk}&itmId=ALL&objL1=ALL&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=113&tblId=DT_113_STBL_1029530"
        rows = get_json(url, {}, retries=1)
        if isinstance(rows, list):
            for x in rows:
                ntl.setdefault(x["PRD_DE"], {}).setdefault(x["C1_NM"], {})[x["ITM_NM"]] = float(x["DT"]) if x["DT"] not in ("", "-") else None
            print("  국민여행조사", sorted(ntl), "그룹", len(next(iter(ntl.values()))))
    out = {"gates_n": len(feats), "kobus_2015": KOBUS, "bus_routes_2022": BUS_ROUTES, "region_mode_2019": REGION_MODE, "citizen_2025": CITIZEN, "aadt": aadt,
           "national_travel": {"tbl": "KOSIS 113 DT_113_STBL_1029530 국민여행조사 관광여행 지역간 주요 이동 수단(1순위), 전국·응답자 특성별, %", "data": ntl},
           "src": {"kobus": "2030 경주도시기본계획 p.202 「경주시 버스터미널 현황」 자료 KOBUS (T1 문서 전사)", "bus_routes": "경주시 도시재생 전략계획(변경) 2022 p.51 「경주시 대중교통 운행노선 현황」 자료 경주시교통정보센터 (T1 전사)",
                   "region_mode": "전략계획 2022 p.54 「권역별 수단통행 분포」 자료 2019 국가교통조사 전국 여객 O/D (T1 전사) — 경주가 속한 부산울산권·대구권 광역 통계",
                   "citizen": "경주시 원도심 미래구상 기획연구 2025.07 p.66–68 시민 설문(n=49·46·54, 복수응답) (T2 전사) — 시민, 관광객 아님",
                   "aadt": "한국도로공사 연평균일교통량 2021–2025 (data.go.kr 15062249, C-008, T2) — 본선 통과 교통량이며 IC 진출입량이 아님",
                   "national": "문화체육관광부 국민여행조사 (KOSIS API, T2) — 전국 평균, 경주 방문자 통계가 아님. 시도별 방문지 교차표는 보고서에만 있고 API 미제공"}}
    save(out, PROCESSED / "arrival_transport.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
