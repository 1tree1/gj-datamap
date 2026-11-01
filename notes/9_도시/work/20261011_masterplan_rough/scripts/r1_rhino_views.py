# R1 라이노 핵심 장소 투시(run_python 안에서 exec) — 단면선을 지면에 보라색 띠로 올리고, 단면이 지나는 핵심 장소를 가까이서 본 3컷씩
# JOBS = [(key, idx, sa, sb, yaw, elev, lens, off, zt), ...]  s: 단면선 위 거리(m), yaw: 단면 직각 시선(n)에서 회전(도, +반시계), off: 시선 방향으로 목표점 이동(m)
import Rhino, System, json, math, os
import Rhino.Geometry as G
doc = __rhino_doc__
X0, Y0 = 1166600.0, 1761100.0
BASE = r"C:\Users\OFFICE\Desktop\9_도시\work\20261011_masterplan_rough"
OUT = BASE + r"\sheets\clip"
SL = json.load(open(BASE + r"\data\section_lines.json", encoding="utf-8"))
CUT = json.load(open(BASE + r"\data\cut_ranges.json", encoding="utf-8"))
view = None
for v in doc.Views:
    if v.ActiveViewport.Name == "Perspective": view = v
doc.Views.ActiveView = view; vp = view.ActiveViewport
for o in list(doc.Objects):
    if isinstance(o.Geometry, G.ClippingPlaneSurface): doc.Objects.Delete(o.Id, True)
# 단면선 띠(한 번만)
li = doc.Layers.FindByFullPath("98_단면선", -1)
if li < 0:
    L = Rhino.DocObjects.Layer(); L.Name = "98_단면선"; L.Color = System.Drawing.Color.FromArgb(160, 35, 122); li = doc.Layers.Add(L)
    for k in ("V", "H", "Dg"):
        a, b = SL[k]; p0 = G.Point3d(a[0] + X0, a[1] + Y0, 0); p1 = G.Point3d(b[0] + X0, b[1] + Y0, 0)
        u = p1 - p0; u.Unitize(); s0, s1 = CUT[k]
        pl = G.Plane(p0 + u * s0, u, G.Vector3d(-u.Y, u.X, 0))
        bx = G.Box(pl, G.Interval(0, s1 - s0), G.Interval(-1.2, 1.2), G.Interval(0.05, 0.45))
        at = Rhino.DocObjects.ObjectAttributes(); at.LayerIndex = li; at.ObjectColor = System.Drawing.Color.FromArgb(160, 35, 122); at.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
        doc.Objects.AddBox(bx, at)
mode = Rhino.Display.DisplayModeDescription.FindByName(globals().get("MODE", "DIAGRAMS"))
res = []
for key, idx, sa, sb, yaw, elev, lens, off, zt in JOBS:
    a, b = SL[key]; p0 = G.Point3d(a[0] + X0, a[1] + Y0, 0); p1 = G.Point3d(b[0] + X0, b[1] + Y0, 0)
    u = p1 - p0; u.Unitize(); n = G.Vector3d(-u.Y, u.X, 0)
    r = math.radians(yaw); look = G.Vector3d(n.X * math.cos(r) - n.Y * math.sin(r), n.X * math.sin(r) + n.Y * math.cos(r), 0)
    W = sb - sa
    target = p0 + u * ((sa + sb) / 2) + look * off + G.Vector3d(0, 0, zt)
    half = math.atan(18.0 / lens); d = (W / 2) / math.tan(half) * 1.05
    e = math.radians(elev)
    cam = target - look * (d * math.cos(e)) + G.Vector3d(0, 0, d * math.sin(e))
    vp.ChangeToPerspectiveProjection(True, lens)
    vp.SetCameraLocations(target, cam)
    view.Redraw()
    p = OUT + "\\%s_%d.png" % (key, idx)
    view.CaptureToBitmap(System.Drawing.Size(1800, 1190), mode).Save(p, System.Drawing.Imaging.ImageFormat.Png); res.append(p)
print("\n".join(res))
