"""Reopen the delivered 3dm and check the union mesh against all thickness regions."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "print_1500_20261011" / "vendor"))
import numpy as np
import rhino3dm
import trimesh
from shapely.geometry import Point, shape

data = json.loads((HERE / "prepared_site_profiles.json").read_text(encoding="utf-8"))
raw = json.loads((HERE / "union_mesh.json").read_text(encoding="utf-8"))
native = json.loads((HERE / "native_validation.json").read_text(encoding="utf-8"))
model = rhino3dm.File3dm.Read(native["saved_desktop"])
assert model is not None and len(model.Objects) == 1
brep = model.Objects[0].Geometry
assert isinstance(brep, rhino3dm.Brep) and brep.IsSolid and brep.IsValid
assert model.Settings.ModelUnitSystem == rhino3dm.UnitSystem.Millimeters
mesh = trimesh.Trimesh(raw["vertices"], raw["faces"], process=True)
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
components = mesh.split(only_watertight=False)
assert len(components) == 1
regions = {k: shape(v) for k, v in data["regions"].items()}
heights = data["thickness_mm"]
up_triangles = mesh.triangles[mesh.face_normals[:, 2] > 0.9]
polys = np.array(up_triangles[:, :, :2])
ab = polys[:, 1] - polys[:, 0]
ac = polys[:, 2] - polys[:, 0]
det = ab[:, 0] * ac[:, 1] - ab[:, 1] * ac[:, 0]
usable = np.abs(det) > 1e-9
polys = polys[usable]
up_triangles = up_triangles[usable]
ab, ac, det = ab[usable], ac[usable], det[usable]


def measured_top(x, y):
    ap = np.array([x, y]) - polys[:, 0]
    u = (ap[:, 0] * ac[:, 1] - ap[:, 1] * ac[:, 0]) / det
    v = (ab[:, 0] * ap[:, 1] - ab[:, 1] * ap[:, 0]) / det
    inside = (u >= -1e-8) & (v >= -1e-8) & (u + v <= 1 + 1e-8)
    assert inside.any(), (x, y, "No top surface")
    return float(np.max(up_triangles[inside, 0, 2]))


rng = np.random.default_rng(1500)
counts = dict.fromkeys(heights, 0)
samples = []
for category, region in regions.items():
    if category not in heights:
        continue
    minx, miny, maxx, maxy = region.bounds
    candidates = [region.representative_point()]
    while len(candidates) < 100:
        p = Point(rng.uniform(minx, maxx), rng.uniform(miny, maxy))
        if region.contains(p) and region.boundary.distance(p) > 0.02:
            candidates.append(p)
    for p in candidates:
        z = measured_top(p.x, p.y)
        assert abs(z - heights[category]) < 1e-5, (category, p.x, p.y, z)
        counts[category] += 1
        samples.append({"category": category, "xy_mm": [p.x, p.y], "measured_top_mm": z})

checks = {
    "delivered_file": native["saved_desktop"],
    "file_bytes": Path(native["saved_desktop"]).stat().st_size,
    "reopened_objects": len(model.Objects),
    "native_valid_closed_brep": True,
    "units": "Millimeters",
    "watertight": bool(mesh.is_watertight),
    "winding_consistent": bool(mesh.is_winding_consistent),
    "connected_components": len(components),
    "mesh_volume_mm3": float(mesh.volume),
    "dimensions_mm": mesh.extents.tolist(),
    "thickness_samples_passed": counts,
    "selection_scope": "Selected masterplan_v2 site boundary; road, sidewalk and green extrusion profiles in the same masterplan",
}
(HERE / "final_validation.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
(HERE / "thickness_samples.json").write_text(json.dumps(samples, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(checks, ensure_ascii=False))

# A plan preview shows the delivered footprint and the four exact top heights.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path as PlotPath
from matplotlib.patches import Patch
from shapely.geometry.polygon import orient
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


def fill_polygon(ax, polygon, color):
    parts = [polygon] if polygon.geom_type == "Polygon" else polygon.geoms
    for poly in parts:
        poly = orient(poly, sign=1)
        vertices, codes = [], []
        for ring in [poly.exterior] + list(poly.interiors):
            points = list(ring.coords)
            vertices.extend(points)
            codes.extend([PlotPath.MOVETO] + [PlotPath.LINETO] * (len(points) - 2) + [PlotPath.CLOSEPOLY])
        ax.add_patch(PathPatch(PlotPath(vertices, codes), facecolor=color, edgecolor="#68726f", linewidth=0.6))


colors = {"general": "#d8cdb1", "road": "#9ca7ad", "sidewalk": "#c4d8e1", "green": "#83b49b"}
fig = plt.figure(figsize=(10, 11), facecolor="#f4f5f2")
ax = fig.add_axes([0.04, 0.075, 0.47, 0.78])
for category in heights:
    fill_polygon(ax, regions[category], colors[category])
ax.set_aspect("equal")
ax.set_xlim(-20, 225)
ax.set_ylim(-20, 650)
ax.axis("off")
ax.annotate("", xy=(0, -10), xytext=(207.383, -10), arrowprops={"arrowstyle": "|-|", "color": "#45575e"})
ax.text(103.6915, -18, "207.383 mm", ha="center", va="top", fontsize=11)
fig.text(0.08, 0.93, "구 경주역 대지 · 1:1500", fontsize=24, weight="bold", color="#263d45")
fig.text(0.08, 0.885, "출력 단위 mm  |  하나의 닫힌 솔리드", fontsize=13, color="#55686b")
fig.text(0.54, 0.77, "바닥 z = 0으로 통일", fontsize=17, weight="bold", color="#263d45")
legend_ax = fig.add_axes([0.54, 0.55, 0.42, 0.19])
legend_ax.axis("off")
legend_ax.legend(handles=[Patch(facecolor=colors[k], label=f"{label}    {heights[k]:g} mm") for k, label in [("general", "일반 대지"), ("road", "도로"), ("sidewalk", "보도"), ("green", "공원·녹지")]], loc="upper left", frameon=False, fontsize=15, labelspacing=1.2)
fig.text(0.54, 0.52, "전체 크기", fontsize=13, weight="bold", color="#263d45")
fig.text(0.54, 0.482, "207.383 × 631.954 × 3.5 mm", fontsize=13, color="#45575e")
fig.text(0.54, 0.4, "검증 완료", fontsize=13, weight="bold", color="#263d45")
fig.text(0.54, 0.36, "닫힌 Brep 1개 · 연결된 형상 1개\n열린 모서리 0개\n구역별 두께 400지점 확인", fontsize=13, color="#45575e", linespacing=1.8, va="top")
fig.text(0.54, 0.22, "공원 내부 주차장 구멍 유지\n원본 파일 보존", fontsize=12, color="#687a7b", linespacing=1.8, va="top")
fig.text(0.08, 0.025, Path(native["saved_desktop"]).name, fontsize=10, color="#7a898c")
fig.savefig(HERE / "site_base_preview.png", dpi=160, facecolor=fig.get_facecolor())
plt.close(fig)
