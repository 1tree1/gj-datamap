"""문화·여가 시설 지점 — 도서관·박물관·미술관·공원 (V-World 장소검색) + 공원 폴리곤(V-World UPIS UQ153, S2 창).
장소검색은 POI 카테고리 문자열로 거른다(진출입시설·버스정류장·사무소·묘원 등 제외). 같은 이름이 50m 안에 여러 건이면 1건만.
출력: processed/facilities_4326.geojson (kind: 도서관·박물관·미술관·공원), processed/parks_upis_4326.geojson
등급 T2 (V-World POI, 공식 시설 목록 아님) — 표준데이터 API(도서관·박물관미술관·도시공원) 활용신청 후 교체 권장."""
import sys, os, json, urllib.parse, urllib.request, re
from shapely.geometry import Point, shape, mapping
from shapely.geometry.polygon import orient
from pyproj import Transformer
from _common import load_env, save, PROCESSED, RAW, S2_BBOX
from collect_vworld import wfs

BBOX = "129.05,35.65,129.55,36.0"   # 경주시 외접
# kind: (검색어들, 채택 카테고리 정규식(카테고리 문자열 기준), 제외 정규식(제목+카테고리))
QUERIES = {
    "도서관": (["도서관", "작은도서관"], r"^(공공도서관|도서관|작은도서관|전문도서관)$|대학도서관|교육부", r"진출입|정류장|입구|청소|용역"),
    "박물관": (["박물관", "전시관", "기념관"], r"박물관|전시관|기념관|공연시설운영업|관광휴게시설", r"진출입|정류장|입구|편의점|카페|공동주택|주차|음식|소매|박물관회|박물관점|카페"),
    "미술관": (["미술관", "갤러리"], r"미술관|화랑|관광휴게시설|공연시설운영업", r"진출입|정류장|입구|호프|펜션|모텔|학원|교습|가구|웨딩|소매업|주차"),
    "공원": (["공원", "근린공원", "어린이공원", "소공원", "체육공원", "문화공원", "역사공원", "수변공원"], r"^공원 > (?!국립공원)", r"사무소|분소|묘원|묘지|정류장|진출입|입구|주차|화장터|화장장|추모|납골|관측소|감포정"),
}


def search(q, key, dom, page=1):
    url = f"https://api.vworld.kr/req/search?service=search&request=search&version=2.0&crs=EPSG:4326&size=100&page={page}&query={urllib.parse.quote(q)}&type=place&bbox={BBOX}&format=json&errorformat=json&key={key}"
    r = urllib.request.urlopen(urllib.request.Request(url, headers={"Referer": dom, "User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8")
    res = json.loads(r).get("response", {}); items = (res.get("result", {}) or {}).get("items", []) or []
    tot = int((res.get("record") or {}).get("total", 0) or 0)
    return items, tot


def main():
    load_env(); key = os.environ["VWORLD_KEY"]; dom = os.environ["VWORLD_DOMAIN"]
    t87 = Transformer.from_crs(4326, 5187, always_xy=True).transform
    feats = []; seen = []
    for kind, (qs, inc, exc) in QUERIES.items():
        n0 = len(feats)
        for q in qs:
            page = 1
            while True:
                items, tot = search(q, key, dom, page)
                for it in items:
                    title = it.get("title", ""); cat = it.get("category", "") or ""; addr = (it.get("address") or {}); a = addr.get("road") or addr.get("parcel") or ""
                    if "경주시" not in a: continue
                    if not re.search(inc, cat): continue
                    if kind != "공원" and kind not in title and not re.search(r"뮤지엄|갤러리|전시관|기념관|문화관|도서마당", title): continue
                    if re.search(exc, title + " " + cat): continue
                    x, y = float(it["point"]["x"]), float(it["point"]["y"]); X, Y = t87(x, y)
                    nm = re.sub(r"\(.*?\)|\s|/", "", title)
                    if any(s[0] == nm and abs(s[1] - X) < 80 and abs(s[2] - Y) < 80 for s in seen): continue
                    seen.append((nm, X, Y))
                    feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [x, y]}, "properties": {"name": title, "kind": kind, "category": cat, "addr": a, "lbl": title, "source": "V-World 장소검색 (2026-09-21, T2 POI) — 공식 시설 목록 아님"}})
                if page * 100 >= tot or page >= 8: break
                page += 1
        print(f"  {kind}: {len(feats) - n0}건")
    save({"type": "FeatureCollection", "features": feats}, PROCESSED / "facilities_4326.geojson")
    # 공원 폴리곤 (UPIS 공간시설: 공원·광장·녹지) — S2 창을 4분할해 INVALID_RANGE 회피
    h = {"Referer": dom, "User-Agent": "Mozilla/5.0"}; x0, y0, x1, y1 = S2_BBOX; polys = []; ids = set()
    for bx in (x0, (x0 + x1) / 2):
        for by in (y0, (y0 + y1) / 2):
            bb = (bx, by, bx + (x1 - x0) / 2, by + (y1 - y0) / 2)
            try: fs, _ = wfs("LT_C_UPISUQ153", key, h, bbox=bb)
            except Exception as e: print("  UQ153", bb, str(e)[:60]); continue
            for f in fs:
                k = f["properties"].get("present_sn") or json.dumps(f["geometry"])[:80]
                if k in ids: continue
                ids.add(k); f["properties"]["lbl"] = f["properties"].get("dgm_nm") or f["properties"].get("lcl_nam")
                g = shape(f["geometry"]); g = orient(g, 1.0) if g.geom_type == "Polygon" else type(g)([orient(q, 1.0) for q in g.geoms]) if g.geom_type == "MultiPolygon" else g
                f["geometry"] = mapping(g); polys.append(f)
    import collections
    print("  UPIS 공간시설", len(polys), collections.Counter(p["properties"].get("lcl_nam") for p in polys).most_common(8))
    save({"type": "FeatureCollection", "features": polys}, PROCESSED / "parks_upis_4326.geojson")
    return 0


if __name__ == "__main__":
    sys.exit(main())
