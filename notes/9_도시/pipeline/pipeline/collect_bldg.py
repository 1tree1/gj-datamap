"""건축HUB 건축물대장 표제부 → 원도심 5개 동 전량 → PNU 조인으로 필지별 노후도.

출력: raw/bldg_title.json (원자료), processed/parcels_bldg_4326.geojson (필지 + 건물 속성)
proxy_for: 노후건축물 비율(사용승인 20년·30년↑) — 도시재생 쇠퇴진단 물리환경 지표
"""
import os, sys, json, re, datetime
from _common import load_env, get_json, save, RAW, PROCESSED, SIGUNGU, DONGS

API = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
KEEP = ("mgmBldrgstPk", "platPlc", "bldNm", "mainPurpsCdNm", "etcPurps", "strctCdNm", "useAprDay", "grndFlrCnt", "ugrndFlrCnt",
        "totArea", "archArea", "platArea", "bcRat", "vlRat", "hhldCnt", "heit", "regstrKindCdNm")


def fetch_dong(key, bj):
    rows, page = [], 1
    while True:
        j = get_json(f"{API}?serviceKey={key}&sigunguCd={SIGUNGU}&bjdongCd={bj}&numOfRows=100&pageNo={page}&_type=json")
        b = j["response"]["body"]; items = (b.get("items") or {}).get("item") or []
        if isinstance(items, dict): items = [items]
        rows += items
        if len(rows) >= int(b["totalCount"]) or not items: break
        page += 1
    return rows


def pnu(r):
    # PNU 11번째 자리: 1=일반(대지) 2=산 / 건축물대장 platGbCd: 0=대지 1=산 2=블록
    gb = {"0": "1", "1": "2"}.get(str(r.get("platGbCd")), "1")
    return f"{r['sigunguCd']}{r['bjdongCd']}{gb}{r['bun']}{r['ji']}"


def year(s):
    m = re.match(r"(\d{4})", (s or "").strip()); return int(m.group(1)) if m else None


def main():
    load_env(); key = os.environ["DATA_GO_KR_KEY"]
    allrows = []
    for nm, bj in DONGS.items():
        rows = fetch_dong(key, bj); allrows += rows
        print(f"  {nm}({bj}) {len(rows)}동")
    json.dump(allrows, open(RAW / "bldg_title.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"  총 {len(allrows)}건 저장 raw/bldg_title.json")
    # PNU별 집계: 대표(최대 연면적) 건물 + 최고령 사용승인
    by = {}
    for r in allrows:
        k = pnu(r); d = by.setdefault(k, {"n": 0, "totArea": 0.0, "oldest": None, "rep": None})
        d["n"] += 1; d["totArea"] += float(r.get("totArea") or 0)
        y = year(r.get("useAprDay"))
        if y and (d["oldest"] is None or y < d["oldest"]): d["oldest"] = y
        if d["rep"] is None or float(r.get("totArea") or 0) > float(d["rep"].get("totArea") or 0): d["rep"] = r
    # 필지에 조인
    fc = json.load(open(RAW / "vworld_parcel.geojson", encoding="utf-8"))
    now = datetime.date.today().year; hit = 0
    for f in fc["features"]:
        p = f["properties"]; d = by.get(p.get("pnu"))
        if not d: p.update(bldg_n=0); continue
        hit += 1; rep = d["rep"]
        p.update(bldg_n=d["n"], bldg_totArea=round(d["totArea"], 1), bldg_oldest=d["oldest"],
                 bldg_age=(now - d["oldest"]) if d["oldest"] else None,
                 bldg_purps=rep.get("mainPurpsCdNm"), bldg_strct=rep.get("strctCdNm"), bldg_flr=rep.get("grndFlrCnt"),
                 bldg_name=(rep.get("bldNm") or "").strip())
    fc.pop("crs", None)
    save(fc, PROCESSED / "parcels_bldg_4326.geojson", f"건물 조인 {hit}/{len(fc['features'])} 필지")
    ages = [f["properties"]["bldg_age"] for f in fc["features"] if f["properties"].get("bldg_age")]
    if ages: print(f"  사용승인 연도 보유 {len(ages)}필지 | 20년↑ {sum(a>=20 for a in ages)/len(ages)*100:.1f}% | 30년↑ {sum(a>=30 for a in ages)/len(ages)*100:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
