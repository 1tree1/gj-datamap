"""관광단지(관광진흥법) 경계 — V-World LT_C_UO601. 속성에 이름이 없어 dyear/dnum(마지막 고시)을 토지이음 고시정보로 역추적해 이름을 붙인다.
출력: processed/tourism_complex_4326.geojson"""
import sys, json
from shapely.geometry import shape, mapping
from shapely.geometry.polygon import orient
from shapely.ops import transform
from pyproj import Transformer
from _common import RAW, PROCESSED, save

NAMES = {  # (dyear, dnum) → (이름, 근거 고시)
    ("2008", "0128"): ("보문관광단지", "경상북도 고시 제2008-128호 관광단지 지정 및 조성계획(변경) 지형도면 등 고시 (2008-03-20)"),
    ("2021", "0172"): ("감포해양관광단지", "경상북도 고시 제2021-172호 감포해양관광단지 지정(변경)·조성계획(변경) 승인 및 지형도면 등 고시 (2021-05-27)"),
    ("2021", "0233"): ("북경주 웰니스 관광단지", "경상북도 고시 제2021-233호 북경주 웰니스 관광단지 지정 및 지형도면 승인 고시 (2021-07-15)"),
    ("2026", "0202"): ("마우나오션 관광단지", "경상북도 고시 제2026-202호 「마우나오션 관광단지」 조성계획(변경) 승인 고시 (2026-05-28)"),
}


def main():
    src = json.load(open(RAW / "vworld_uo601_tourism_complex.geojson", encoding="utf-8"))
    t = Transformer.from_crs(4326, 5187, always_xy=True).transform
    out = []
    for f in src["features"]:
        p = f["properties"]
        if p.get("sigg_name") != "경주시": continue
        nm, basis = NAMES.get((p["dyear"], p["dnum"]), (f"관광단지 (고시 {p['dyear']}-{p['dnum']}, 이름 미확인)", "V-World 속성에 이름 없음"))
        g = shape(f["geometry"]); area = transform(t, g).area
        g = type(g)([orient(q, 1.0) for q in g.geoms]) if g.geom_type == "MultiPolygon" else orient(g, 1.0)
        out.append({"type": "Feature", "geometry": mapping(g),
                    "properties": {"name": nm, "area_ha": round(area / 1e4, 1), "gosi": f"{p['dyear']}-{p['dnum']}", "basis": basis,
                                   "lbl": f"{nm}\n{area/1e4:,.0f}ha", "src": "V-World LT_C_UO601 (관광진흥법 관광단지) · 이름은 고시번호로 토지이음 고시정보 대조"}})
        print(f"  {nm:<16} {area/1e4:8,.1f}ha  고시 {p['dyear']}-{p['dnum']}")
    save({"type": "FeatureCollection", "features": out}, PROCESSED / "tourism_complex_4326.geojson")
    return 0


if __name__ == "__main__":
    sys.exit(main())
