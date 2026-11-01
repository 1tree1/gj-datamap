# R0 라이노 단면 투시 캡처(run_python 안에서 exec) — 단면선마다 클리핑 평면을 세우고, 잘린 쪽에서 단면을 바라보는 투시 3장
# 방향: 진행 방향 u(A→A′)가 화면 오른쪽이 되도록 보는 방향 n = rot90(u). 클리핑 평면 법선 = n(법선 쪽이 남음)
import Rhino, System, json, math
import Rhino.Geometry as G
doc = __rhino_doc__
X0, Y0 = 1166600.0, 1761100.0
OUT = r"C:\Users\OFFICE\Desktop\9_도시\work\20261011_masterplan_rough\sheets\clip"
import os
if not os.path.isdir(OUT): os.makedirs(OUT)
SL = json.load(open(r"C:\Users\OFFICE\Desktop\9_도시\work\20261011_masterplan_rough\data\section_lines.json", encoding="utf-8"))
CUT = json.load(open(r"C:\Users\OFFICE\Desktop\9_도시\work\20261011_masterplan_rough\data\cut_ranges.json", encoding="utf-8"))
JOBS = globals().get("JOBS", None)
view = None
for v in doc.Views:
    if v.ActiveViewport.Name == "Perspective": view = v
doc.Views.ActiveView = view; vp = view.ActiveViewport
# 기존 클리핑 평면 제거
for o in list(doc.Objects):
    if isinstance(o.Geometry, G.ClippingPlaneSurface): doc.Objects.Delete(o.Id, True)
mode = Rhino.Display.DisplayModeDescription.FindByName(globals().get("MODE", "Rendered"))
vp.DisplayMode = mode
res = []
for key, segs in JOBS:
    a, b = SL[key]
    p0 = G.Point3d(a[0] + X0, a[1] + Y0, 0); p1 = G.Point3d(b[0] + X0, b[1] + Y0, 0)
    u = p1 - p0; L = u.Length; u.Unitize()
    n = G.Vector3d(-u.Y, u.X, 0)
    s0, s1 = CUT[key]
    far = p0 + u * (s1 + 3000)                                   # 평면 사각형은 화면 밖에(클리핑은 무한 평면)
    cid = doc.Objects.AddClippingPlane(G.Plane(far, n), 1, 1, vp.Id)
    for i, (t0, t1, elev, lens, zt) in enumerate(segs):
        sa = s0 + (s1 - s0) * t0; sb = s0 + (s1 - s0) * t1; W = sb - sa
        target = p0 + u * ((sa + sb) / 2) + n * (W * 0.32) + G.Vector3d(0, 0, zt)
        half = math.atan(18.0 / lens)
        d = (W / 2) / math.tan(half) * 1.02
        e = math.radians(elev)
        cam = target - n * (d * math.cos(e)) + G.Vector3d(0, 0, d * math.sin(e))
        vp.ChangeToPerspectiveProjection(True, lens)
        vp.SetCameraLocations(target, cam)
        view.Redraw()
        p = OUT + "\%s_%d.png" % (key, i + 1)
        bmp = view.CaptureToBitmap(System.Drawing.Size(1800, 1190), mode)      # 표시 모드를 직접 지정(ViewCapture는 모드를 무시)
        bmp.Save(p, System.Drawing.Imaging.ImageFormat.Png); res.append(p)
    doc.Objects.Delete(cid, True)
print("\n".join(res))
