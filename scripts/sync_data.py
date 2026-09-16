"""9_도시 파이프라인 산출물(EPSG:4326 GeoJSON)을 web/data 로 복사. 처리본(5187)은 복사하지 않는다."""
import shutil, json, sys
from pathlib import Path
SRC = Path(r"C:\Users\User\Desktop\9_도시\archive\C_data")
DST = Path(__file__).resolve().parent.parent / "public" / "data"   # Vite: public/ 은 그대로 dist/ 로 복사
FILES = {
    "processed/gosi2026-8_zone_4326.geojson":   "zone.geojson",
    "processed/gosi2026-8_blocks_4326.geojson": "blocks.geojson",
    "processed/parcels_bldg_4326.geojson":     "parcels.geojson",   # 필지 + 건축물대장 조인(노후도)
    "raw/sbiz_stores.geojson":                  "stores.geojson",
    "raw/sbiz_zones.geojson":                   "sbiz_zones.geojson",
    "raw/vworld_uq111.geojson":                 "landuse.geojson",
}
DST.mkdir(exist_ok=True)
for s, d in FILES.items():
    src = SRC / s
    if not src.exists():
        print("없음:", src); continue
    fc = json.load(open(src, encoding="utf-8"))
    fc.pop("crs", None)  # RFC7946: 4326만, crs 멤버 제거
    json.dump(fc, open(DST / d, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{d:18s} {len(fc['features']):6d} features  {(DST/d).stat().st_size/1e6:.1f} MB")
