# -*- coding: utf-8 -*-
# OSM 건물 높이 태그 채움률 산정 — 후보 도시 원도심 중심 반경 1 km 원(S2 대응)
# 원천: ohsome API (HeiGIT, OSM 전체 이력 기반 집계; 데이터 시점은 응답 메타데이터의 toTimestamp)
#   Overpass 공개 서버가 2026-10-27 조회 시 「capacity 초과(502)」로 응답하지 않아 ohsome로 바꿨다.
# 대상: building=* 이고 면(geometry:polygon: 닫힌 way + multipolygon relation)
# 출력: research/data/osm_height_fill_20261027.csv
import csv, json, pathlib, urllib.parse, urllib.request

CENTERS = [
    # (id, 이름, 중심점 설명, lat, lon) — 중심점은 [가정]: 원도심의 역사적 중심 하나(A 문서 §2.1 규칙에 맞춰 2차에서 재지정)
    ("kyoto", "교토 中京·下京", "四条烏丸 교차점", 35.0037, 135.7596),
    ("kyoto_higashiyama", "교토 東山(대조)", "八坂神社 서문 앞 四条通", 35.0037, 135.7781),
    ("kanazawa", "가나자와 まちなか", "香林坊 교차점", 36.5617, 136.6534),
    ("nara", "나라 ならまち", "元興寺", 34.6771, 135.8306),
    ("kurashiki", "구라시키 美観地区", "大原美術館", 34.5960, 133.7710),
    ("takayama", "다카야마 三町", "上三之町", 36.1400, 137.2610),
    ("regensburg", "레겐스부르크 Altstadt", "Dom St. Peter", 49.0195, 12.0976),
    ("bamberg", "밤베르크 Weltkulturerbe", "Altes Rathaus", 49.8916, 10.8868),
    ("denbosch", "'s-Hertogenbosch binnenstad", "Markt", 51.6886, 5.3036),
    ("delft", "델프트 binnenstad", "Markt", 52.0116, 4.3594),
    ("leiden", "레이던 binnenstad", "Burcht", 52.1588, 4.4930),
    ("bologna", "볼로냐 centro storico", "Piazza Maggiore", 44.4938, 11.3426),
    ("freiburg", "프라이부르크 Altstadt", "Münster", 47.9956, 7.8522),
    ("edinburgh", "에든버러 Old Town", "St Giles' Cathedral", 55.9495, -3.1909),
    ("gyeongju", "경주 원도심(참고)", "구 경주역 부근", 35.8424, 129.2163),
]
BASE = "building=* and geometry:polygon"
FILTERS = {
    "n_building": BASE,
    "n_height": BASE + " and height=*",
    "n_height_or_levels": BASE + " and (height=* or building:levels=*)",
}
URL = "https://api.ohsome.org/v1/elements/count"
META = json.load(urllib.request.urlopen("https://api.ohsome.org/v1/metadata", timeout=60))
T = META["extractRegion"]["temporalExtent"]["toTimestamp"]
res = {cid: {} for cid, *_ in CENTERS}
# 원 하나·필터 하나씩 요청(한 번에 여러 원을 보내면 600 s 시간 초과). 동시 4개.
from concurrent.futures import ThreadPoolExecutor
def one(job):
    cid, lat, lon, key, flt = job
    data = urllib.parse.urlencode({"bcircles": f"{lon},{lat},1000", "filter": flt, "time": T}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(URL, data=data, headers={"User-Agent": "research-script/1.0"})
            js = json.load(urllib.request.urlopen(req, timeout=300))
            return cid, key, int(js["result"][0]["value"])
        except Exception as e:
            print("retry", cid, key, e, flush=True)
    return cid, key, None
jobs = [(cid, lat, lon, k, f) for cid, _, _, lat, lon in CENTERS for k, f in FILTERS.items()]
with ThreadPoolExecutor(max_workers=4) as ex:
    for cid, key, v in ex.map(one, jobs):
        res[cid][key] = v; print(cid, key, v, flush=True)
out = pathlib.Path(__file__).parent / "data" / "osm_height_fill_20261027.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "center", "lat", "lon", "radius_m", "n_building", "n_height",
                "n_height_or_levels", "pct_height", "pct_height_or_levels", "osm_data_time"])
    for cid, name, desc, lat, lon in CENTERS:
        r = res[cid]; n = r.get("n_building", 0)
        pct = lambda k: round(r[k] / n * 100, 1) if n and r.get(k) is not None else ""
        row = [cid, name, desc, lat, lon, 1000, n, r.get("n_height"), r.get("n_height_or_levels"),
               pct("n_height"), pct("n_height_or_levels"), T]
        w.writerow(row); print(row)
print("saved", out)
