"""소상공인 상가(상권)정보 API — S2 창 내 업소 점 + 상권영역 폴리곤. 출력 4326 GeoJSON."""
import os, sys, json, urllib.parse, re
from _common import load_env, get_json, save, RAW
from _common import S2_BBOX as BBOX

API = "http://apis.data.go.kr/B553077/api/open/sdsc2"


def stores(key):
    feats, page = [], 1
    while True:
        u = (f"{API}/storeListInRectangle?serviceKey={key}&minx={BBOX[0]}&miny={BBOX[1]}&maxx={BBOX[2]}&maxy={BBOX[3]}"
             f"&numOfRows=1000&pageNo={page}&type=json")
        j = get_json(u)
        h = j.get("header", {}); items = j.get("body", {}).get("items") or []
        if page == 1: print("  header:", h.get("resultMsg"), "| totalCount", j.get("body", {}).get("totalCount"))
        for it in items:
            try: lon, lat = float(it["lon"]), float(it["lat"])
            except: continue
            feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]},
                          "properties": {k: it.get(k) for k in ("bizesId", "bizesNm", "indsLclsCd", "indsLclsNm", "indsMclsNm", "indsSclsNm",
                                                                 "ldongNm", "lnoAdr", "rdnmAdr", "bldNm", "flrNo")}})
        total = int(j.get("body", {}).get("totalCount") or 0)
        if len(feats) >= total or not items: break
        page += 1
    return feats


def zones(key):
    u = f"{API}/storeZoneInRectangle?serviceKey={key}&minx={BBOX[0]}&miny={BBOX[1]}&maxx={BBOX[2]}&maxy={BBOX[3]}&type=json"
    j = get_json(u); items = j.get("body", {}).get("items") or []
    feats = []
    for it in items:
        wkt = it.get("coords") or ""
        m = re.findall(r"[-\d.]+\s+[-\d.]+", wkt)
        if not m: continue
        ring = [[float(a), float(b)] for a, b in (p.split() for p in m)]
        if ring[0] != ring[-1]: ring.append(ring[0])
        feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                      "properties": {k: it.get(k) for k in ("trarNo", "mainTrarNm", "ctprvnNm", "signguNm", "trarArea", "coordNum", "stdrDt")}})
    print("  상권영역", len(feats), "개", [f["properties"]["mainTrarNm"] for f in feats][:8])
    return feats


def main():
    load_env(); key = os.environ["DATA_GO_KR_KEY"]
    print("[상가 업소]"); st = stores(key)
    save({"type": "FeatureCollection", "features": st}, RAW / "sbiz_stores.geojson")
    import collections
    print("  대분류:", collections.Counter(f["properties"]["indsLclsNm"] for f in st).most_common(10))
    print("[상권영역]"); zn = zones(key)
    save({"type": "FeatureCollection", "features": zn}, RAW / "sbiz_zones.geojson")
    return 0


if __name__ == "__main__":
    sys.exit(main())
