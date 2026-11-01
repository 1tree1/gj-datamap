"""경주시 관광지 현황 / 게스트하우스 현황 — 경주시 REST(apis.data.go.kr/5050000/...) + V-World 지오코딩.

주의: data.go.kr 페이지의 uddi는 odcloud 경로가 아니다. 실제 host는 swaggerJson.host (2026-09-17 확인).
"""
import os, sys, json, re, urllib.parse
from _common import load_env, get_json, save, RAW

SVCS = [  # (host, path, slug, 이름필드, 추가필드)
    ("apis.data.go.kr/5050000/touristDestinationService", "/getTouristDestination", "tour_sites", "TRRSRT", ["TURSM_DSTRCT", "TELNO"]),
    ("apis.data.go.kr/5050000/guestHouseService", "/getGuestHouse", "guesthouse", "BSSH_NM", ["HMPG_NM", "TELNO"]),
]


def fetch(host, path, key):
    rows, page = [], 1
    while True:
        j = get_json(f"https://{host}{path}?serviceKey={key}&pageNo={page}&numOfRows=500&type=json")
        body = j["response"]["body"]; items = (body.get("items") or {}).get("item") or []
        items = [items] if isinstance(items, dict) else items; rows += items
        if len(rows) >= int(body.get("totalCount") or 0) or not items: break
        page += 1
    return rows


def geocode(addr, vk, h):
    a = re.sub(r"\(.*?\)", "", addr or "").strip()   # 괄호 주기 제거
    for typ in ("ROAD", "PARCEL"):
        try:
            r = get_json(f"https://api.vworld.kr/req/address?service=address&request=getcoord&version=2.0&crs=EPSG:4326&type={typ}&address={urllib.parse.quote(a)}&format=json&key={vk}", h, retries=1)["response"]
            if r["status"] == "OK": return float(r["result"]["point"]["x"]), float(r["result"]["point"]["y"]), typ
        except Exception: pass
    return None


def main():
    load_env(); key = os.environ["DATA_GO_KR_KEY"]; vk = os.environ["VWORLD_KEY"]
    h = {"Referer": os.environ["VWORLD_DOMAIN"], "User-Agent": "Mozilla/5.0"}
    for host, path, slug, nk, extra in SVCS:
        rows = fetch(host, path, key); json.dump(rows, open(RAW / f"gj_{slug}.json", "w", encoding="utf-8"), ensure_ascii=False)
        feats, miss = [], []
        for r in rows:
            g = geocode(r.get("ADRES"), vk, h)
            if not g: miss.append(r.get(nk)); continue
            feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [g[0], g[1]]},
                          "properties": {"name": r.get(nk), "addr": r.get("ADRES"), "geocode": g[2], **{k: r.get(k) for k in extra}}})
        save({"type": "FeatureCollection", "features": feats}, RAW / f"gj_{slug}.geojson", f"{len(rows)}건 중 지오코딩 {len(feats)}")
        if miss: print("   지오코딩 실패:", miss)
    return 0


if __name__ == "__main__":
    sys.exit(main())
