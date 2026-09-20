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
    "processed/traffic_hist_links_4326.geojson": "traffic_hist.geojson",
    "processed/reg_areas_4326.geojson":        "reg_areas.geojson",
    "raw/vworld_emd_gj.geojson":                "emd.geojson",
    "processed/godo_4326.geojson":            "godo.geojson",
    "processed/hadm_pop_4326.geojson":         "hadm_pop.geojson",
    "raw/sbiz_zones.geojson":                   "sbiz_zones.geojson",
    "raw/vworld_uq111.geojson":                 "landuse.geojson",
    # 2026-09-20 전수조사·소상공인365 (pipeline/build_web_extras.py)
    "processed/footfall_areas_web_4326.geojson": "footfall_areas.geojson",
    "processed/decline_2022_4326.geojson":      "decline_2022.geojson",
    "processed/landprice_pts_4326.geojson":     "landprice_pts.geojson",
    "processed/poi_schools_4326.geojson":       "schools.geojson",
    "processed/poi_religion_4326.geojson":      "religion.geojson",
    "processed/lifezone_4326.geojson":          "lifezone.geojson",
    # 2026-09-21 시청 분산·철도·가로망·상권·주차장 (pipeline/build_web_civic_transit.py)
    "processed/cityhall_sites_4326.geojson":    "cityhall_sites.geojson",
    "processed/rail_abandoned_4326.geojson":    "rail_abandoned.geojson",
    "processed/rail_active_4326.geojson":       "rail_active.geojson",
    "processed/rail_stations_4326.geojson":     "rail_stations.geojson",
    "processed/urban_roads_4326.geojson":       "urban_roads.geojson",
    "processed/commerce_zones_4326.geojson":    "commerce_zones.geojson",
    "processed/parking_pub_4326.geojson":       "parking_pub.geojson",
}
DST.mkdir(exist_ok=True)
# 비공간 표(사이드바용)
for s_, d_ in {"raw/visitors_gyeongju_daily.json": "visitors.json", "processed/traffic_hourly.json": "traffic_hourly.json", "processed/traffic_congested.json": "traffic_congested.json", "processed/traffic_hist_summary.json": "traffic_hist_summary.json", "raw/kosis_nationality_gj.json": "nationality.json", "processed/youth_city.json": "youth.json", "processed/web_extras.json": "web_extras.json", "processed/report_stats.json": "report_stats.json", "processed/hwango_report.json": "hwango_report.json", "processed/arts_stats.json": "arts_stats.json"}.items():
    if (SRC / s_).exists(): shutil.copy(SRC / s_, DST / d_); print(f"{d_:18s} (표)")
for s, d in FILES.items():
    src = SRC / s
    if not src.exists():
        print("없음:", src); continue
    fc = json.load(open(src, encoding="utf-8"))
    fc.pop("crs", None)  # RFC7946: 4326만, crs 멤버 제거
    json.dump(fc, open(DST / d, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{d:18s} {len(fc['features']):6d} features  {(DST/d).stat().st_size/1e6:.1f} MB")
