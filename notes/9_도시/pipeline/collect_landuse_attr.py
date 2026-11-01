"""V-World 토지이용계획 속성(getLandUseAttr) — 필지별 지역·지구·구역 목록. 토지이음 팝업과 동일 내용.
출력: processed/parcels_lu_4326.geojson (parcels_bldg 기반 + lu_* 속성)"""
import os, sys, json, time, urllib.parse
from _common import load_env, get_json, save, RAW, PROCESSED


def main():
    load_env(); key = os.environ["VWORLD_KEY"]; dom = urllib.parse.quote(os.environ["VWORLD_DOMAIN"], safe="")
    h = {"Referer": os.environ["VWORLD_DOMAIN"], "User-Agent": "Mozilla/5.0"}
    src = PROCESSED / "parcels_bldg_4326.geojson"
    fc = json.load(open(src, encoding="utf-8"))
    cache_p = RAW / "vworld_landuse_attr.json"
    cache = json.load(open(cache_p, encoding="utf-8")) if cache_p.exists() else {}
    todo = [f["properties"]["pnu"] for f in fc["features"] if f["properties"].get("pnu") and f["properties"]["pnu"] not in cache]
    print(f"필지 {len(fc['features'])}  캐시 {len(cache)}  조회 대상 {len(todo)}")
    t0 = time.time(); err = 0
    for i, pnu in enumerate(todo):
        try:
            j = get_json(f"https://api.vworld.kr/ned/data/getLandUseAttr?key={key}&domain={dom}&pnu={pnu}&format=json&numOfRows=50&pageNo=1", h, retries=2)
            rows = (j.get("landUses") or {}).get("field") or []
            cache[pnu] = [{"nm": r.get("prposAreaDstrcCodeNm"), "cnf": r.get("cnflcAtNm"), "reg": r.get("regstrSeCodeNm"), "upd": r.get("lastUpdtDt")} for r in rows]
        except Exception as e:
            err += 1; cache[pnu] = None
        if (i + 1) % 500 == 0:
            json.dump(cache, open(cache_p, "w", encoding="utf-8"), ensure_ascii=False)
            print(f"  {i+1}/{len(todo)}  {time.time()-t0:.0f}s  오류 {err}")
    json.dump(cache, open(cache_p, "w", encoding="utf-8"), ensure_ascii=False)
    # 조인
    import collections; cnt = collections.Counter()
    for f in fc["features"]:
        p = f["properties"]; rows = cache.get(p.get("pnu"))
        if not rows: p["lu_list"] = ""; continue
        incl = [r["nm"] for r in rows if r["cnf"] != "저촉"]; touch = [r["nm"] for r in rows if r["cnf"] == "저촉"]
        p["lu_list"] = " · ".join(dict.fromkeys(incl)); p["lu_touch"] = " · ".join(dict.fromkeys(touch)); p["lu_n"] = len(rows)
        for r in incl: cnt[r] += 1
    save(fc, PROCESSED / "parcels_lu_4326.geojson", f"토지이용계획 조인")
    print("  포함 지역지구 상위:", cnt.most_common(14))
    return 0


if __name__ == "__main__":
    sys.exit(main())
