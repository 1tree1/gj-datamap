"""V-World 수집 — 구경주역 부지 일원의 필지·용도지역·용도지구.

출력은 EPSG:4326 GeoJSON (웹용). 처리본 5187 변환은 별도 단계.
"""
import os, sys, json, urllib.parse
from _common import load_env, get_json, save, RAW, SITE_LON, SITE_LAT

# 구경주역 지구단위계획구역(156,460㎡)을 넉넉히 덮는 창
# 고시 제2026-8호 지번 11개 지오코딩 결과(2026-09-17)로 확정. 여유 ±450m
BBOX = (129.2128, 35.8370, 129.2252, 35.8538)

LAYERS = [
    ("LP_PA_CBND_BUBUN", "parcel",   "연속지적도(필지)"),
    ("LT_C_UQ111",       "uq111",    "용도지역"),
    ("LT_C_UQ112",       "uq112",    "용도지구"),
    ("LT_C_UQ113",       "uq113",    "용도구역"),
]


def wfs(layer, key, headers, bbox=BBOX, size=1000, cap=12):
    feats, page = [], 1
    geom = f"BOX({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})"
    while page <= cap:
        url = ("https://api.vworld.kr/req/data?service=data&request=GetFeature"
               f"&format=json&data={layer}&key={key}&crs=EPSG:4326"
               f"&geomFilter={urllib.parse.quote(geom)}&size={size}&page={page}")
        j = get_json(url, headers)
        resp = j.get("response", {})
        if resp.get("status") == "NOT_FOUND":
            return feats, 0
        if resp.get("status") != "OK":
            raise RuntimeError(json.dumps(resp.get("error", resp))[:200])
        fc = resp["result"]["featureCollection"]
        feats += fc.get("features", [])
        total = int(resp["record"]["total"])
        if len(feats) >= total:
            break
        page += 1
    return feats, total


def main():
    load_env()
    key = os.environ["VWORLD_KEY"]
    headers = {"Referer": os.environ.get("VWORLD_DOMAIN", ""), "User-Agent": "Mozilla/5.0"}
    print(f"창(BBOX) {BBOX}  ≈ {round((BBOX[2]-BBOX[0])*88.8*1000)}m × {round((BBOX[3]-BBOX[1])*111*1000)}m")
    for layer, slug, name in LAYERS:
        print(f"\n[{name}] {layer}")
        try:
            feats, total = wfs(layer, key, headers)
        except Exception as e:
            print("  실패:", str(e)[:160]); continue
        if not feats:
            print("  해당 창 안에 피처 없음"); continue
        fc = {"type": "FeatureCollection",
              "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
              "features": feats}
        save(fc, RAW / f"vworld_{slug}.geojson", f"서버 총 {total}")
        print("  속성:", list(feats[0]["properties"].keys())[:12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
