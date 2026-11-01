# -*- coding: utf-8 -*-
"""뷰 캡처 (Rhino 8 Python 3, run_python 안에서 exec). 전역 SHOTS=[dict(name, loc=[x,y,z], target=[x,y,z], box=[x0,y0,z0,x1,y1,z1], scale=3, mode='Shaded', parallel=True, up=[0,0,1])], OUTDIR
뷰포트 종횡비 그대로 scale 배로 캡처하고, box 의 투영 범위를 crop.json 에 기록한다(크롭은 밖에서 PIL 로)."""
import Rhino, System, json, os
import Rhino.Geometry as rg
doc = __rhino_doc__
v = doc.Views.ActiveView; vp = v.ActiveViewport
info = {}
for s in SHOTS:
    dm = Rhino.Display.DisplayModeDescription.FindByName(s.get('mode', 'Shaded'))
    if dm: vp.DisplayMode = dm
    if s.get('parallel', True): vp.ChangeToParallelProjection(True)
    else: vp.ChangeToPerspectiveProjection(True, s.get('lens', 35.0))
    loc = rg.Point3d(*s['loc']); tgt = rg.Point3d(*s['target'])
    vp.SetCameraLocations(tgt, loc)
    up = s.get('up', [0, 0, 1]); vp.CameraUp = rg.Vector3d(up[0], up[1], up[2])
    b = s['box']; box = rg.BoundingBox(b[0], b[1], b[2], b[3], b[4], b[5])
    vp.ZoomBoundingBox(box); v.Redraw()
    port = vp.Bounds; W, H = port.Width, port.Height; k = s.get('scale', 3)
    xs = []; ys = []
    for c in box.GetCorners():
        p = vp.WorldToClient(c); xs.append(p.X); ys.append(p.Y)
    bmp = v.CaptureToBitmap(System.Drawing.Size(W * k, H * k))
    path = os.path.join(OUTDIR, s['name'] + '.png'); bmp.Save(path)
    info[s['name']] = dict(path=path, W=W * k, H=H * k, crop=[min(xs) * k, min(ys) * k, max(xs) * k, max(ys) * k], camdir=[vp.CameraDirection.X, vp.CameraDirection.Y, vp.CameraDirection.Z])
json.dump(info, open(os.path.join(OUTDIR, 'crop.json'), 'w'))
print('captured', {k: (v_['W'], v_['H'], [round(c) for c in v_['crop']], [round(c, 2) for c in v_['camdir']]) for k, v_ in info.items()})
