# -*- coding: utf-8 -*-
# Rhino 8 run_python 용 — _DIAG 레이어를 축측·평면으로 캡처(전체 / CONNECT / EXCHANGE / SPREAD)하고 월드→픽셀 아핀 기준점을 저장한다.
import Rhino, System, os, json, math
import Rhino.Geometry as rg
doc = __rhino_doc__
OUT = r'C:\Users\OFFICE\Desktop\9_도시\work\20261011_midterm_deck\build\rhino_cap'
st = json.load(open(os.path.join(OUT, 'diag_state.json'), encoding='utf-8'))
view = doc.Views.ActiveView; vp = view.ActiveViewport
RP = json.load(open(r'C:\Users\OFFICE\Desktop\9_도시\work\20261011_midterm_deck\build\data\road_plan_final_plan.json', encoding='utf-8'))
xs = [p[0] for p in RP['U']]; ys = [p[1] for p in RP['U']]
X0, Y0 = min(xs), min(ys)
bb = rg.BoundingBox(min(xs) - 150, min(ys) - 90, 0, max(xs) + 150, max(ys) + 90, 40)
W, H = int(vp.Size.Width) * 2, int(vp.Size.Height) * 2
# 3b 보완: 구 역사가 복사본 프레임에만 있으면 옮겨서 넣는다
if st.get('nstation', 0) == 0:
    li = doc.Layers.FindByFullPath('_DIAG::구 역사', -1)
    if li < 0:
        L = Rhino.DocObjects.Layer(); L.Name = '구 역사'; L.ParentLayerId = doc.Layers[doc.Layers.FindByFullPath('_DIAG', -1)].Id
        L.Color = System.Drawing.Color.FromArgb(0x7A, 0x4A, 0x2A); li = doc.Layers.Add(L)
    n = 0
    for ob in doc.Objects:
        lay = doc.Layers[ob.Attributes.LayerIndex].FullPath
        if lay != '빌딩': continue
        g = ob.Geometry.Duplicate(); b = g.GetBoundingBox(True)
        if b.Min.X > 1167700: g.Translate(rg.Vector3d(-563.4406435338315, 0, 0))
        a = Rhino.DocObjects.ObjectAttributes(); a.LayerIndex = li; a.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromLayer; a.Name = '구 역사'
        doc.Objects.Add(g, a); n += 1
    st['nstation'] = n
def set_mode(name):
    for m in Rhino.Display.DisplayModeDescription.GetDisplayModes():
        if m.EnglishName == name: vp.DisplayMode = m; return True
    return False
def diag_layers():
    return [L for L in doc.Layers if (not L.IsDeleted) and L.FullPath and L.FullPath.startswith('_DIAG::')]
def show_only(pred):
    for L in diag_layers(): L.IsVisible = bool(pred(L.Name))
    doc.Views.Redraw()
def capture(fname, mode='Shaded'):
    set_mode(mode); doc.Views.Redraw(); Rhino.RhinoApp.Wait()
    vc = Rhino.Display.ViewCapture(); vc.Width = W; vc.Height = H; vc.ScaleScreenItems = False; vc.DrawAxes = False; vc.DrawGrid = False; vc.DrawGridAxes = False; vc.TransparentBackground = True
    bmp = vc.CaptureToBitmap(view)
    if bmp: bmp.Save(os.path.join(OUT, fname)); return [bmp.Width, bmp.Height]
    return None
def basis(tag):
    sw, sh = float(vp.Size.Width), float(vp.Size.Height)
    def cl(x, y, z):
        s = vp.WorldToClient(rg.Point3d(x, y, z)); return [s.X / sw * W, s.Y / sh * H]
    o = cl(X0, Y0, 0); ex = cl(X0 + 100, Y0, 0); ey = cl(X0, Y0 + 100, 0); ez = cl(X0, Y0, 100)
    labels = [dict(name=L['name'], col=L['col'], area=L['area'], px=cl(L['x'], L['y'], L['z'])[0], py=cl(L['x'], L['y'], L['z'])[1], x=L['x'], y=L['y'], z=L['z']) for L in st['labels']]
    json.dump(dict(view=tag, size=[W, H], origin=[X0, Y0], o=o, ex=[ex[0] - o[0], ex[1] - o[1]], ey=[ey[0] - o[0], ey[1] - o[1]], ez=[ez[0] - o[0], ez[1] - o[1]], labels=labels),
              open(os.path.join(OUT, 'anchors_' + tag + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
def cam(loc, target, box, up=rg.Vector3d.ZAxis):
    vp.SetProjection(Rhino.Display.DefinedViewportProjection.Perspective, None, True)
    vp.ChangeToParallelProjection(True)
    vp.SetCameraLocations(target, loc); vp.CameraUp = up
    vp.ZoomBoundingBox(box); view.Redraw(); doc.Views.Redraw(); Rhino.RhinoApp.Wait()
CENTRAL = ('M 창작 레지던시·체험', 'M 성동시장 연계', 'M 관광휴게·근대역사관', 'M 공연장', '구 역사')
NORTH = ('M 공공청사·의회', 'M 청년·신혼 주거', 'M 생활편의·체육', 'M 청년 창업·업무')
BASE = ('도로', '보도', '맥락', '바닥', 'M 오픈스페이스')
res = {}
# 축측(남서 상공)
cam(rg.Point3d(bb.Center.X - 1100, bb.Center.Y - 1500, 1000), bb.Center, bb)
SITE = lambda n: n != '맥락'
show_only(lambda n: True); res['axon_sw'] = capture('axon_sw.png'); basis('axon_sw')
show_only(lambda n: n == '맥락'); res['axon_context'] = capture('axon_context.png')
show_only(SITE); res['axon_site'] = capture('axon_site.png')
show_only(lambda n: n in BASE and n != '맥락'); res['axon_connect'] = capture('axon_connect.png')
show_only(lambda n: (n in BASE or n in CENTRAL) and n != '맥락'); res['axon_exchange'] = capture('axon_exchange.png')
show_only(lambda n: (n in BASE or n in NORTH) and n != '맥락'); res['axon_spread'] = capture('axon_spread.png')
# 축측(북서 상공) — 북측 프로그램이 앞에 오는 보조 뷰
cam(rg.Point3d(bb.Center.X - 1100, bb.Center.Y + 1500, 1000), bb.Center, bb)
show_only(lambda n: n == '맥락'); res['axon_nw_context'] = capture('axon_nw_context.png')
show_only(SITE); res['axon_nw'] = capture('axon_nw.png'); basis('axon_nw')
# 평면(북쪽 위)
bb2 = rg.BoundingBox(min(xs) - 120, min(ys) - 80, 0, max(xs) + 120, max(ys) + 80, 40)
cam(rg.Point3d(bb.Center.X, bb.Center.Y, 2000), rg.Point3d(bb.Center.X, bb.Center.Y, 0), bb2, rg.Vector3d.YAxis)
show_only(lambda n: n == '맥락'); res['top_context'] = capture('top_context.png')
show_only(SITE); res['top'] = capture('top.png'); basis('top')
show_only(lambda n: True)
json.dump(st, open(os.path.join(OUT, 'diag_state.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(json.dumps(res))
