"""9_도시 파이프라인 산출물(EPSG:4326 GeoJSON)을 web/data 로 복사. 처리본(5187)은 복사하지 않는다."""
import shutil, json, sys
from pathlib import Path
SRC = Path(r"C:\Users\User\Desktop\9_도시\archive\C_data")
DST = Path(__file__).resolve().parent.parent / "public" / "data"   # Vite: public/ 은 그대로 dist/ 로 복사
FILES = {
    "processed/gosi2026-8_zone_4326.geojson":   "zone.geojson",
    "processed/gosi2026-8_blocks_4326.geojson": "blocks.geojson",
    "processed/parcels_lu_4326.geojson":       "parcels.geojson",   # 필지 + 건축물대장 + 토지이용계획 속성
    "processed/stores_merged_4326.geojson":     "stores.geojson",   # 소진공 + 경주시 게스트하우스 병합
    "raw/busstops_gj.geojson":                  "busstops.geojson",
    "raw/vworld_upis.geojson":                  "upis.geojson",
    "processed/parcels_energy_4326.geojson":   "energy.geojson",
    "raw/gj_tour_sites.geojson":                "tour_sites.geojson",
    "processed/traffic_links_4326.geojson":    "traffic.geojson",
    "processed/reg_areas_4326.geojson":        "reg_areas.geojson",
    "raw/sbiz_zones.geojson":                   "sbiz_zones.geojson",
    "raw/vworld_uq111.geojson":                 "landuse.geojson",
}
DST.mkdir(exist_ok=True)
# 비공간 표(사이드바용)
for s_, d_ in {"raw/visitors_gyeongju_daily.json": "visitors.json", "processed/traffic_hourly.json": "traffic_hourly.json", "processed/traffic_congested.json": "traffic_congested.json"}.items():
    if (SRC / s_).exists(): shutil.copy(SRC / s_, DST / d_); print(f"{d_:18s} (표)")
for s, d in FILES.items():
    src = SRC / s
    if not src.exists():
        print("없음:", src); continue
    fc = json.load(open(src, encoding="utf-8"))
    fc.pop("crs", None)  # RFC7946: 4326만, crs 멤버 제거
    json.dump(fc, open(DST / d, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{d:18s} {len(fc['features']):6d} features  {(DST/d).stat().st_size/1e6:.1f} MB")
