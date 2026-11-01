# -*- coding: utf-8 -*-
# Rhino 8 run_python 용 — 임시 다이어그램 레이어(_DIAG)에 프로그램 매스·맥락 건물·도로·보도를 만들고 축측/평면을 파일로 캡처한다. 원본 객체는 수정하지 않는다.
import Rhino, System, os, json, math
import Rhino.Geometry as rg
from System.Drawing import Color
doc = __rhino_doc__
OUT = r'C:\Users\OFFICE\Desktop\9_도시\work\20261011_midterm_deck\build\rhino_cap'
if not os.path.exists(OUT): os.makedirs(OUT)
CTX = r'C:\Users\OFFICE\Desktop\9_도시\work\20261011_masterplan_v1\data\ctx_buildings_planframe.json'
ROADS = r'C:\Users\OFFICE\Desktop\9_도시\work\20261011_midterm_deck\build\data\road_plan_final_plan.json'
TOL = doc.ModelAbsoluteTolerance
def hexc(h): h = h.lstrip('#'); return Color.FromArgb(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
# 프로그램별 색·높이·표시명 (레이어 이름 접두어로 판정)
PROG = [('시청', '공공청사·의회', '#3A3A3A', 20.0), ('청년주거', '청년·신혼 주거', '#C8102E', 18.0), ('생활편의', '생활편의·체육', '#E8808F', 8.0),
        ('청년 오피스', '청년 창업·업무', '#8A0A1F', 19.5), ('예술인', '창작 레지던시·체험', '#F0A0AD', 12.0), ('성동시장', '성동시장 연계', '#F4B8C1', 8.0),
        ('관광휴게', '관광휴게·근대역사관', '#D96D7A', 12.0), ('공연장', '공연장', '#B5121B', 15.0), ('관광지원', '관광지원·주차전용', '#9A9A9A', 15.0), ('오픈스페이스', '오픈스페이스', '#C9D3C2', 0.3)]
def prog_of(layer):
    for key, name, col, h in PROG:
        if layer.startswith(key): return (name, col, h)
    return None
# 0) 정리: 이전 임시 레이어 삭제
def purge_layer(name):
    idx = doc.Layers.FindByFullPath(name, -1)
    if idx >= 0:
        for ob in list(doc.Objects.FindByLayer(doc.Layers[idx]) or []): doc.Objects.Delete(ob, True)
        for ch in list(doc.Layers[idx].GetChildren() or []):
            for ob in list(doc.Objects.FindByLayer(ch) or []): doc.Objects.Delete(ob, True)
            doc.Layers.Delete(ch.Index, True)
        doc.Layers.Delete(idx, True)
purge_layer('_DIAG')
_st = os.path.join(OUT, 'diag_state.json')
if os.path.exists(_st):
    try:
        for name in json.load(open(_st, encoding='utf-8')).get('hidden', []):
            i = doc.Layers.FindByFullPath(name, -1)
            if i >= 0: doc.Layers[i].IsVisible = True
        os.remove(_st)
    except Exception: pass
root = doc.Layers.Add('_DIAG', Color.Black); rootL = doc.Layers[root]
def sub(name, col):
    full = '_DIAG::' + name; idx = doc.Layers.FindByFullPath(full, -1)
    if idx >= 0: return idx
    L = Rhino.DocObjects.Layer(); L.Name = name; L.ParentLayerId = rootL.Id; L.Color = hexc(col); L.PlotColor = hexc(col)
    return doc.Layers.Add(L)
def attrs(layer_idx, name=None):
    a = Rhino.DocObjects.ObjectAttributes(); a.LayerIndex = layer_idx; a.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromLayer
    if name: a.Name = name
    return a
def extrude(curve, z0, h):
    c = curve.DuplicateCurve(); c.Translate(rg.Vector3d(0, 0, z0 - c.PointAtStart.Z))
    if c.ClosedCurveOrientation(rg.Plane.WorldXY) == rg.CurveOrientation.Clockwise: c.Reverse()
    ex = rg.Extrusion.Create(c, h, True)
    if ex is None: return None
    b = ex.ToBrep(); bb = b.GetBoundingBox(True)
    if bb.Max.Z < z0 + h * 0.5:   # 아래로 돌출된 경우 위로 뒤집기
        c.Reverse(); ex = rg.Extrusion.Create(c, h, True); b = ex.ToBrep() if ex else None
    return b
labels = []
# 1) 프로그램 매스: 계획 프레임의 프로그램 레이어 브렙 외곽 → 안쪽 5 m 오프셋 → 높이만큼 돌출. 획지면은 같은 색 바닥.
lots = []
for ob in doc.Objects:
    lay = doc.Layers[ob.Attributes.LayerIndex].FullPath
    if not lay.startswith('지구단위계획 2026-8::'): continue
    g = ob.Geometry; bb = g.GetBoundingBox(True)
    if bb.Min.X < 1166900 or bb.Max.X > 1167900: continue
    if not isinstance(g, rg.Brep): continue
    p = prog_of(lay.split('::')[-1])
    if not p: continue
    lots.append((p, g))
for (name, col, h), brep in lots:
    li = sub('M ' + name, col)
    for f in brep.Faces:
        outer = None
        for lp in f.Loops:
            if lp.LoopType == rg.BrepLoopType.Outer: outer = lp.To3dCurve()
        if outer is None: continue
        amp = rg.AreaMassProperties.Compute(outer); c0 = amp.Centroid
        # 바닥(획지면)
        g2 = extrude(outer, 0.2, 0.3)
        if g2: doc.Objects.AddBrep(g2, attrs(li))
        if h > 1.0:
            offs = outer.Offset(rg.Plane.WorldXY, -5.0, TOL, rg.CurveOffsetCornerStyle.Sharp)
            cv = offs[0] if offs and len(offs) == 1 and offs[0].IsClosed else outer
            m = extrude(cv, 0.5, h)
            if m: doc.Objects.AddBrep(m, attrs(li, name))
        labels.append(dict(name=name, col=col, x=c0.X, y=c0.Y, z=h + 0.5, area=amp.Area))
# 2) 도로·보도 (최종 도로계획 json, 계획 좌표)
RP = json.load(open(ROADS, encoding='utf-8'))
lr = sub('도로', '#6E6E6E'); lw = sub('보도', '#E2E2E2')
def poly_from(pts, z):
    pl = rg.Polyline([rg.Point3d(p[0], p[1], z) for p in pts])
    if pl[0].DistanceTo(pl[len(pl) - 1]) > TOL: pl.Add(pl[0])
    return pl.ToNurbsCurve()
for r in RP['roads']:
    b = rg.Brep.CreatePlanarBreps(poly_from(r, 0.1), TOL)
    if b:
        for bb_ in b: doc.Objects.AddBrep(bb_, attrs(lr))
for w in RP['walks']:
    crvs = [poly_from(w['outer'], 0.12)] + [poly_from(i, 0.12) for i in w['inner']]
    b = rg.Brep.CreatePlanarBreps(crvs, TOL)
    if b:
        for bb_ in b: doc.Objects.AddBrep(bb_, attrs(lw))
# 3) 맥락 건물 (ctx_buildings_planframe.json: p, z0, h) — 흰 매스
lc = sub('맥락', '#F4F4F4')
C = json.load(open(CTX, encoding='utf-8'))
nctx = 0
for b in C:
    try:
        pl = rg.Polyline([rg.Point3d(p[0], p[1], 0.0) for p in b['p']])
        if pl[0].DistanceTo(pl[len(pl) - 1]) > TOL: pl.Add(pl[0])
        if pl.Count < 4: continue
        ex = rg.Extrusion.Create(pl.ToNurbsCurve(), max(float(b['h']), 3.0), True)
        if ex: doc.Objects.AddBrep(ex.ToBrep(), attrs(lc)); nctx += 1
    except Exception as e: pass
# 3b) 구 역사(빌딩 레이어, 계획 프레임 안) 복사
ls_ = sub('구 역사', '#7A4A2A'); nst = 0
for ob in doc.Objects:
    lay = doc.Layers[ob.Attributes.LayerIndex].FullPath
    if lay != '빌딩': continue
    bb = ob.Geometry.GetBoundingBox(True)
    if bb.Min.X < 1166900 or bb.Max.X > 1167900: continue
    doc.Objects.Add(ob.Geometry.Duplicate(), attrs(ls_, '구 역사')); nst += 1
# 4) 바닥판
lg = sub('바닥', '#FFFFFF')
Ub = rg.Polyline([rg.Point3d(p[0], p[1], 0.0) for p in RP['U']]);
pb = rg.Brep.CreatePlanarBreps(Ub.ToNurbsCurve(), TOL)
if pb:
    for bb_ in pb: doc.Objects.AddBrep(bb_, attrs(lg))
doc.Views.Redraw()
# 5) _DIAG 외 모든 레이어 숨김(복원용 목록 저장)
hidden = []
for L in doc.Layers:
    fp = L.FullPath
    if L.IsDeleted or not fp or fp.startswith('_DIAG'): continue
    if L.IsVisible: L.IsVisible = False; hidden.append(fp)
doc.Views.Redraw()
json.dump(dict(hidden=hidden, labels=labels, nctx=nctx, nstation=nst), open(os.path.join(OUT, 'diag_state.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('lots', len(lots), 'ctx', nctx, 'station', nst, 'hidden', len(hidden))
