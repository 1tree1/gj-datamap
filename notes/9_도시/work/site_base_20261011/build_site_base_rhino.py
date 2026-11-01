"""Run inside Rhino: create and union native closed Breps, then save one object."""
import json
import os
import time

import Rhino
import System.Drawing
from System.Collections.Generic import List

FOLDER = r"C:\Users\OFFICE\Desktop\9_도시\work\site_base_20261011"
DESKTOP_PATH = r"C:\Users\OFFICE\Desktop\gyeongju_site_base_1_1500_sidewalk_fixed.3dm"
TOL = 0.001
started = time.time()
with open(os.path.join(FOLDER, "prepared_site_profiles.json"), encoding="utf-8") as f:
    data = json.load(f)


def log(message):
    with open(os.path.join(FOLDER, "build_log.txt"), "a", encoding="utf-8") as f:
        f.write(message + "\n")


def volume(brep):
    props = Rhino.Geometry.VolumeMassProperties.Compute(brep)
    assert props is not None
    result = props.Volume
    props.Dispose()
    return result


def make_solid(profile, z0, z1):
    curves = List[Rhino.Geometry.Curve]()
    for ring in [profile["outer"]] + profile["holes"]:
        points = [Rhino.Geometry.Point3d(x, y, z0) for x, y in ring]
        curves.Add(Rhino.Geometry.PolylineCurve(points))
    planar = Rhino.Geometry.Brep.CreatePlanarBreps(curves, TOL)
    assert planar is not None and len(planar) == 1, "Planar region failed: area=" + str(profile["area_mm2"])
    path = Rhino.Geometry.LineCurve(Rhino.Geometry.Point3d(0, 0, z0), Rhino.Geometry.Point3d(0, 0, z1))
    solid = planar[0].Faces[0].CreateExtrusion(path, True)
    assert solid is not None and solid.IsValid and solid.IsSolid
    if solid.SolidOrientation == Rhino.Geometry.BrepSolidOrientation.Inward:
        solid.Flip()
    assert volume(solid) > 0
    return solid


with open(os.path.join(FOLDER, "build_log.txt"), "w", encoding="utf-8") as f:
    f.write("Building native site solids\n")
solids = List[Rhino.Geometry.Brep]()
for group in data["solids"]:
    for profile in group["profiles"]:
        log("Building " + group["category"] + " area=" + str(profile["area_mm2"]))
        solids.Add(make_solid(profile, group["z0"], group["z1"]))
    log("Built " + group["category"])

log("BooleanUnion starting: " + str(solids.Count) + " solids")
joined = Rhino.Geometry.Brep.CreateBooleanUnion(solids, TOL)
assert joined is not None and len(joined) == 1, "BooleanUnion did not produce one solid: " + str(None if joined is None else len(joined))
result = joined[0]
result.MergeCoplanarFaces(TOL, 0.0001)
result.Compact()
if result.SolidOrientation == Rhino.Geometry.BrepSolidOrientation.Inward:
    result.Flip()
assert result.IsValid and result.IsSolid, "Result is not a valid closed solid"
actual_volume = volume(result)
expected_volume = data["expected_volume_mm3"]
assert abs(actual_volume - expected_volume) < expected_volume * 1e-6, "Thickness/volume mismatch: " + str(actual_volume) + " vs " + str(expected_volume)
bb = result.GetBoundingBox(True)
naked_edges = sum(edge.Valence == Rhino.Geometry.EdgeAdjacency.Naked for edge in result.Edges)
nonmanifold_edges = sum(edge.Valence == Rhino.Geometry.EdgeAdjacency.NonManifold for edge in result.Edges)
assert naked_edges == 0 and nonmanifold_edges == 0
log("BooleanUnion verified")

model = Rhino.FileIO.File3dm()
model.Settings.ModelUnitSystem = Rhino.UnitSystem.Millimeters
model.Settings.ModelAbsoluteTolerance = TOL
model.Settings.ModelAngleToleranceRadians = 0.001
layer = Rhino.DocObjects.Layer()
layer.Name = "site_base_print_mm"
layer.Color = System.Drawing.Color.FromArgb(205, 191, 158)
model.Layers.Add(layer)
layer_index = model.Layers.Count - 1
attrs = Rhino.DocObjects.ObjectAttributes()
attrs.LayerIndex = layer_index
attrs.Name = "site_base_1_1500_general3_road2_sidewalk2_6_green3_5"
attrs.SetUserString("Scale", "1:1500; actual millimeters")
attrs.SetUserString("Thickness_mm", "general=3; road=2; sidewalk=2.6; green=3.5; common bottom z=0")
attrs.SetUserString("Source_file", data["source"])
attrs.SetUserString("Source_origin_xy", json.dumps(data["source_origin"]))
attrs.SetUserString("Source_numeric_units", "1 source coordinate unit = 1 real meter")
attrs.SetUserString("Road_layer", "마스터플랜_v2::04_도로")
attrs.SetUserString("Sidewalk_layer", "마스터플랜_v2::05_보도")
attrs.SetUserString("Pedestrian_network_layer", "마스터플랜_v2::03_보행자전용도로·광장")
attrs.SetUserString("Sidewalk_revision", "Connected perimeter, central, cross-site and diagonal pedestrian network per reference image")
attrs.SetUserString("Green_layer", "마스터플랜_v2::02_공원·녹지")
model.Objects.AddBrep(result, attrs)
workspace_path = os.path.join(FOLDER, "gyeongju_site_base_1_1500.3dm")
assert model.Write(workspace_path, 8)
assert model.Write(DESKTOP_PATH, 8)

mesh_parameters = Rhino.Geometry.MeshingParameters()
mesh_parameters.Tolerance = 0.001
mesh_parameters.MinimumEdgeLength = 0.0001
mesh_parameters.MaximumEdgeLength = 20
mesh_parameters.RefineGrid = True
meshes = Rhino.Geometry.Mesh.CreateFromBrep(result, mesh_parameters)
mesh = Rhino.Geometry.Mesh()
for piece in meshes:
    mesh.Append(piece)
mesh.Faces.ConvertQuadsToTriangles()
mesh.Vertices.CombineIdentical(True, True)
mesh.Weld(3.141592653589793)
mesh.UnifyNormals()
mesh.Normals.ComputeNormals()
mesh.Compact()
mesh_data = {
    "vertices": [[p.X, p.Y, p.Z] for p in mesh.Vertices],
    "faces": [[f.A, f.B, f.C] for f in mesh.Faces],
}
with open(os.path.join(FOLDER, "union_mesh.json"), "w", encoding="utf-8") as f:
    json.dump(mesh_data, f)
checks = {
    "saved_desktop": DESKTOP_PATH,
    "saved_workspace": workspace_path,
    "native_object_count": 1,
    "input_solids": solids.Count,
    "valid": result.IsValid,
    "closed_solid": result.IsSolid,
    "orientation": str(result.SolidOrientation),
    "naked_edges": naked_edges,
    "nonmanifold_edges": nonmanifold_edges,
    "volume_mm3": actual_volume,
    "expected_volume_mm3": expected_volume,
    "volume_difference_mm3": actual_volume - expected_volume,
    "bounds_mm": [[bb.Min.X, bb.Min.Y, bb.Min.Z], [bb.Max.X, bb.Max.Y, bb.Max.Z]],
    "faces": result.Faces.Count,
    "mesh_closed": mesh.IsClosed,
    "elapsed_seconds": time.time() - started,
}
with open(os.path.join(FOLDER, "native_validation.json"), "w", encoding="utf-8") as f:
    json.dump(checks, f, ensure_ascii=False, indent=2)
log("Saved " + DESKTOP_PATH)
print(json.dumps(checks, ensure_ascii=False))
