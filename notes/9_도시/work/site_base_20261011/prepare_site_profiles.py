"""Partition the selected site boundary into print thickness regions."""
import json
from pathlib import Path

from shapely import make_valid, set_precision
from shapely.geometry import Polygon, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
SOURCE = json.loads((HERE / "source_profiles.json").read_text(encoding="utf-8"))
SCALE = SOURCE["scale_xy_to_print_mm"]
GRID = 0.001


def polygon_parts(shape):
    if shape.is_empty:
        return []
    if shape.geom_type == "Polygon":
        return [shape]
    return [p for child in shape.geoms for p in polygon_parts(child)] if hasattr(shape, "geoms") else []


def clean(shape):
    # Snap sub-micron intersection fragments to the documented print precision.
    return unary_union(polygon_parts(set_precision(make_valid(shape), GRID)))


def source_polygon(rings):
    scaled = [[(x * SCALE, y * SCALE) for x, y in ring] for ring in rings]
    return clean(set_precision(make_valid(Polygon(scaled[0], scaled[1:])), GRID))


def profiles(shape):
    return [
        {
            "outer": list(orient(p, sign=1.0).exterior.coords),
            "holes": [list(r.coords) for r in orient(p, sign=1.0).interiors],
            "area_mm2": p.area,
        }
        for p in polygon_parts(shape)
    ]


boundary_raw = Polygon([(x * SCALE, y * SCALE) for x, y in SOURCE["boundary"]])
domain = clean(set_precision(make_valid(boundary_raw), GRID))
roads = clean(unary_union([source_polygon(o["rings"]) for o in SOURCE["objects"] if o["category"] == "road"]).intersection(domain))
sidewalks = clean(unary_union([source_polygon(o["rings"]) for o in SOURCE["objects"] if o["category"] == "sidewalk"]).intersection(domain).difference(roads))
greens = clean(unary_union([source_polygon(o["rings"]) for o in SOURCE["objects"] if o["category"] == "green"]).intersection(domain).difference(roads).difference(sidewalks))
raised = clean(domain.difference(roads))
above_sidewalk = clean(raised.difference(sidewalks))
general = clean(above_sidewalk.difference(greens))
assert len(polygon_parts(domain)) == 1, "The site boundary must be connected"
print("Partition area difference:", domain.area - roads.area - sidewalks.area - greens.area - general.area)
partition_area_error = domain.area - roads.area - sidewalks.area - greens.area - general.area
assert abs(partition_area_error) < domain.area * 1e-6
report = {
    "source": SOURCE["source"],
    "source_origin": SOURCE["source_origin"],
    "scale": "1:1500",
    "xy_multiplier": SCALE,
    "precision_mm": GRID,
    "thickness_mm": {"general": 3.0, "road": 2.0, "sidewalk": 2.6, "green": 3.5},
    "region_area_mm2": {"general": general.area, "road": roads.area, "sidewalk": sidewalks.area, "green": greens.area},
    "expected_volume_mm3": 2 * domain.area + 0.6 * raised.area + 0.4 * above_sidewalk.area + 0.5 * greens.area,
    "partition_area_roundoff_mm2": partition_area_error,
    "bounds_mm": list(domain.bounds),
    "boundary_area_change_mm2": domain.area - boundary_raw.area,
    "boundary_hausdorff_mm": domain.hausdorff_distance(boundary_raw),
    "source_object_count": len(SOURCE["objects"]),
    "classification": "04_도로=2mm; 05_보도 and 03_보행자전용도로·광장 pedestrian network=2.6mm; 02_공원·녹지=3.5mm; remaining site=3mm; precedence road > sidewalk > green > general; extrusion inner profiles retained",
    "solids": [
        {"category": "common_base", "z0": 0.0, "z1": 2.0, "profiles": profiles(domain)},
        {"category": "raised_to_sidewalk", "z0": 1.99, "z1": 2.6, "profiles": profiles(raised)},
        {"category": "raised_general", "z0": 2.59, "z1": 3.0, "profiles": profiles(above_sidewalk)},
        {"category": "raised_green", "z0": 2.99, "z1": 3.5, "profiles": profiles(greens)},
    ],
    "regions": {k: mapping(v) for k, v in {"domain": domain, "general": general, "road": roads, "sidewalk": sidewalks, "green": greens}.items()},
}
(HERE / "prepared_site_profiles.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: report[k] for k in ["region_area_mm2", "expected_volume_mm3", "bounds_mm", "boundary_area_change_mm2", "boundary_hausdorff_mm"]}, ensure_ascii=False))
print("Solid profiles:", [(r["category"], len(r["profiles"]), sum(len(p["outer"]) + sum(map(len, p["holes"])) for p in r["profiles"])) for r in report["solids"]])
