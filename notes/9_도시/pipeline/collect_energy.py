"""건축HUB 건물에너지(전기·가스) — 필지 단위 호출. 개발계정 1,000회/일 → 구역 경계 300m 이내 건물 필지만.
proxy_for: 공실 (월 전기 사용량 0 또는 극소). 단독주택·200세대 미만 공동주택은 제공 제외 → 주거 필지엔 무효."""
import os, sys, json, time
from shapely.geometry import shape
from shapely.ops import transform as stf
from pyproj import Transformer
from _common import load_env, get_json, RAW, PROCESSED

USE_YM = sys.argv[1] if len(sys.argv) > 1 else "202606"
BUDGET = int(sys.argv[2]) if len(sys.argv) > 2 else 900


def main():
    load_env(); key = os.environ["DATA_GO_KR_KEY"]
    t = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True).transform
    zone = stf(t, shape(json.load(open(PROCESSED / "gosi2026-8_zone_4326.geojson", encoding="utf-8"))["features"][0]["geometry"])).buffer(300)
    fc = json.load(open(PROCESSED / "parcels_bldg_4326.geojson", encoding="utf-8"))
    cand = []
    for f in fc["features"]:
        p = f["properties"]
        if not p.get("bldg_n"): continue
        g = stf(t, shape(f["geometry"]))
        if g.intersects(zone): cand.append((g.distance(zone.exterior), p["pnu"]))
    cand.sort(); pnus = [p for _, p in cand][:BUDGET]
    print(f"구역 300m 내 건물 필지 {len(cand)} → 조회 {len(pnus)}  (useYm {USE_YM})")
    cache_p = RAW / f"bldg_energy_{USE_YM}.json"
    cache = json.load(open(cache_p, encoding="utf-8")) if cache_p.exists() else {}
    t0 = time.time(); err = 0
    for i, pnu in enumerate(pnus):
        if pnu in cache: continue
        sig, bj, gb, bun, ji = pnu[:5], pnu[5:10], pnu[10], pnu[11:15], pnu[15:19]
        gbcd = {"1": "0", "2": "1"}.get(gb, "0")
        rec = {}
        for svc, k in (("getBeElctyUsgInfo", "elec"), ("getBeGasUsgInfo", "gas")):
            try:
                j = get_json(f"https://apis.data.go.kr/1613000/BldEngyHubService/{svc}?serviceKey={key}&sigunguCd={sig}&bjdongCd={bj}&platGbCd={gbcd}&bun={bun}&ji={ji}&useYm={USE_YM}&numOfRows=10&pageNo=1&_type=json", retries=1)
                items = ((j.get("response") or {}).get("body") or {}).get("items") or {}
                items = items.get("item") or []; items = [items] if isinstance(items, dict) else items
                rec[k] = sum(float(x.get("useQty") or 0) for x in items); rec[k + "_n"] = len(items)
            except Exception as e:
                err += 1; rec[k] = None
        cache[pnu] = rec
        if (i + 1) % 100 == 0:
            json.dump(cache, open(cache_p, "w", encoding="utf-8")); print(f"  {i+1}/{len(pnus)} {time.time()-t0:.0f}s 오류 {err}")
    json.dump(cache, open(cache_p, "w", encoding="utf-8"))
    vals = [v["elec"] for v in cache.values() if v.get("elec") is not None]
    print(f"완료 {len(cache)}필지 | 전기 데이터 있음 {sum(1 for v in vals if v>0)} | 0 kWh {sum(1 for v in vals if v==0)} | 자료없음 {sum(1 for v in cache.values() if v.get('elec_n')==0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
