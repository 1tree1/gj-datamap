# -*- coding: utf-8 -*-
"""맥락 정리 (Rhino 8 Python 3, run_python 안에서 exec). 계획구역 경계(문서 좌표, 닫힌 폴리라인 점열 BND) 안의 맥락 객체를 지우거나 잘라낸다.
전역: BND=[[x,y],...] 문서 좌표 / LAYERS_DEL=['빌딩'] 안이면 지움(걸치면 50% 기준) / LAYERS_TRIM=['대지','인도','경계석'] 안이면 지우고 걸치면 불리언 차집합
      ZCUT=(z0,z1) 커터 높이 범위 / DRY=True 면 집계만"""
import Rhino, System
import Rhino.Geometry as rg
doc = __rhino_doc__
TOL = doc.ModelAbsoluteTolerance
pts = [rg.Point3d(p[0], p[1], 0.0) for p in BND]
if pts[0].DistanceTo(pts[-1]) > TOL: pts.append(pts[0])
bcrv = rg.PolylineCurve(pts)
bb = bcrv.GetBoundingBox(True)
cutter = rg.Extrusion.Create(rg.PolylineCurve([rg.Point3d(p.X, p.Y, ZCUT[0]) for p in pts]), ZCUT[1] - ZCUT[0], True).ToBrep()
if not cutter.IsSolid: print('cutter not solid!')
# 안쪽 방향이 커터 '내부'가 되도록
if cutter.SolidOrientation == rg.BrepSolidOrientation.Inward: cutter.Flip()

def frac_inside(geo):
    g = geo.ToBrep() if isinstance(geo, rg.Extrusion) else geo
    vs = []
    if isinstance(g, rg.Brep):
        vs = [v.Location for v in g.Vertices]
    elif isinstance(g, rg.Curve):
        ok, pl = g.TryGetPolyline(); vs = list(pl) if ok else [g.PointAt(t) for t in g.DivideByCount(20, True)]
    elif isinstance(g, rg.Mesh):
        vs = list(g.Vertices.ToPoint3dArray())
    if not vs: return 0.0, 0
    n = 0
    for v in vs:
        if bcrv.Contains(rg.Point3d(v.X, v.Y, 0), rg.Plane.WorldXY, TOL) == rg.PointContainment.Inside: n += 1
    return n / float(len(vs)), len(vs)

stats = {}
todo = []
objs = []
for L in list(LAYERS_DEL) + list(LAYERS_TRIM):
    li = doc.Layers.FindByFullPath(L, -1)
    if li < 0: print('layer not found', L); continue
    lay = doc.Layers[li]
    if lay.IsLocked: lay.IsLocked = False; doc.Layers.Modify(lay, li, True)
    for o in doc.Objects.FindByLayer(lay): objs.append((o, L))
for o, L in objs:
    ob = o.Geometry.GetBoundingBox(True)
    if ob.Max.X < bb.Min.X or ob.Min.X > bb.Max.X or ob.Max.Y < bb.Min.Y or ob.Min.Y > bb.Max.Y: continue
    f, nv = frac_inside(o.Geometry)
    if f <= 0.0: continue
    todo.append((o, L, f, nv))
for o, L, f, nv in todo:
    s = stats.setdefault(L, dict(delete=0, trim=0, trim_fail=0, keep=0))
    if L in LAYERS_DEL:
        if f >= 0.5:
            s['delete'] += 1
            if not DRY: doc.Objects.Delete(o, True)
        else: s['keep'] += 1
        continue
    if f >= 0.999:
        s['delete'] += 1
        if not DRY: doc.Objects.Delete(o, True)
        continue
    # 걸침 → 불리언 차집합
    if DRY: s['trim'] += 1; continue
    g = o.Geometry
    b = g.ToBrep() if isinstance(g, rg.Extrusion) else g.Duplicate()
    res = None
    if isinstance(b, rg.Brep) and b.IsSolid:
        res = rg.Brep.CreateBooleanDifference(b, cutter, TOL)
    if res is None or len(res) == 0:
        # 대안: 분할 후 바깥 조각만 유지
        try:
            pieces = b.Split(cutter, TOL)
        except Exception:
            pieces = None
        if pieces:
            keep = []
            for p in pieces:
                am = rg.AreaMassProperties.Compute(p)
                c = am.Centroid if am else p.GetBoundingBox(True).Center
                if bcrv.Contains(rg.Point3d(c.X, c.Y, 0), rg.Plane.WorldXY, TOL) != rg.PointContainment.Inside: keep.append(p)
            res = keep
    if res:
        a = o.Attributes.Duplicate()
        for p in res: doc.Objects.AddBrep(p, a)
        doc.Objects.Delete(o, True); s['trim'] += 1
    else:
        s['trim_fail'] += 1
doc.Views.Redraw()
print('cleanup', 'DRY' if DRY else 'APPLIED', stats)
