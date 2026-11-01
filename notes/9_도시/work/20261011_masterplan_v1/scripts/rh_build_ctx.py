# -*- coding: utf-8 -*-
"""라이노 적재 (Rhino 8 Python 3, run_python 안에서 exec). build_ctx.json / build_plan.json 의 요소를 레이어 트리에 넣는다.
전역: JSON, ROOT, PALETTE('color'|'redbw'), CLEAR(True 면 ROOT 아래 기존 객체 삭제), TREES"""
import Rhino, System, json
import Rhino.Geometry as rg
doc = __rhino_doc__
ds = json.load(open(JSON, encoding='utf-8'))

def hexc(h):
    h = h.lstrip('#'); return System.Drawing.Color.FromArgb(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
if PALETTE == 'redbw':
    COL = {'00 계획구역 경계': '#C8102E', '01 획지(건축용지)': '#E6E6E6', '공공청사': '#DADADA', '공동주택': '#E0E0E0', '업무시설': '#DEDEDE', '문화및집회시설': '#F3D5DA', '근린생활·판매시설': '#E8E8E8', '운동시설': '#E3E3E3', '주차전용·관광휴게': '#ECECEC',
           '02 공원·녹지(도시계획시설)': '#D9D9D9', '근린공원': '#D6D6D6', '문화공원': '#DADADA', '역사공원': '#D2D2D2', '경관녹지': '#DCDCDC', '03 광장·공공공지': '#F2F2F2', '광장': '#F2F2F2', '마당': '#F0F0F0', '텃밭': '#E9E9E9',
           '04 도로': '#FFFFFF', '05 보행자전용도로·보도': '#F7F7F7', '보행자전용도로': '#F7F7F7', '보도': '#F4F4F4', '06 건축물(매스)': '#8C8C8C',
           '공공업무': '#4A4A4A', '주거': '#8C8C8C', '상업·업무': '#6E6E6E', '문화·교육·공공': '#C8102E', '창조산업': '#A6A6A6', '판매·음식': '#B5B5B5', '여가·오락·체육': '#7A7A7A', '역사유산(구 역사 존치)': '#8B0A1E', '교통·방문자': '#BEBEBE', '주차전용건축물': '#CFCFCF', '파빌리온': '#D0D0D0',
           '07 식재': '#9A9A9A', '가로수': '#9A9A9A', '공원수': '#8F8F8F', '획지 조경수': '#A3A3A3', '08 라벨': '#111111'}
else:
    COL = {'00 계획구역 경계': '#DC1E3C', '01 획지(건축용지)': '#C8C8C8', '공공청사': '#B7C9E6', '공동주택': '#F8EBA8', '업무시설': '#F4B8A8', '문화및집회시설': '#C3D8F1', '근린생활·판매시설': '#FAD2E3', '운동시설': '#A9DDD6', '주차전용·관광휴게': '#D0D0D0',
           '02 공원·녹지(도시계획시설)': '#78BE5A', '근린공원': '#8FCF7A', '문화공원': '#9AD684', '역사공원': '#7FC66A', '경관녹지': '#A9D98D', '03 광장·공공공지': '#E7E1D0', '광장': '#E7E1D0', '마당': '#EADFC8', '텃밭': '#B7A27A',
           '04 도로': '#696969', '05 보행자전용도로·보도': '#CDCDCD', '보행자전용도로': '#D8D8D8', '보도': '#C4C4C4', '06 건축물(매스)': '#8C8C8C',
           '공공업무': '#4C78B8', '주거': '#F1D247', '상업·업무': '#E4573A', '문화·교육·공공': '#6F9FDC', '창조산업': '#A98BD3', '판매·음식': '#F4A0C2', '여가·오락·체육': '#2FAB9D', '역사유산(구 역사 존치)': '#C9742F', '교통·방문자': '#C6C6C6', '주차전용건축물': '#8E8E8E', '파빌리온': '#B8A98A',
           '07 식재': '#3F8F45', '가로수': '#4E9A51', '공원수': '#3F8F45', '획지 조경수': '#5BA85D', '08 라벨': '#1E1E1E'}
PARENT = {'공공청사': '01 획지(건축용지)', '공동주택': '01 획지(건축용지)', '업무시설': '01 획지(건축용지)', '문화및집회시설': '01 획지(건축용지)', '근린생활·판매시설': '01 획지(건축용지)', '운동시설': '01 획지(건축용지)', '주차전용·관광휴게': '01 획지(건축용지)'}

def layer(path):
    full = ROOT; parent_idx = doc.Layers.FindByFullPath(ROOT, -1)
    if parent_idx < 0:
        l = Rhino.DocObjects.Layer(); l.Name = ROOT; l.Color = hexc('#3C3C3C'); parent_idx = doc.Layers.Add(l)
    parent = doc.Layers[parent_idx]
    for nm in path:
        full = full + '::' + nm
        idx = doc.Layers.FindByFullPath(full, -1)
        if idx < 0:
            l = Rhino.DocObjects.Layer(); l.Name = nm; l.Color = hexc(COL.get(nm, '#B0B0B0')); l.ParentLayerId = parent.Id
            idx = doc.Layers.Add(l)
        else:
            l = doc.Layers[idx]; l.Color = hexc(COL.get(nm, '#B0B0B0')); doc.Layers.Modify(l, idx, True)
        parent = doc.Layers[idx]
    return parent

if CLEAR:
    n = 0
    for l in list(doc.Layers):
        if l.FullPath == ROOT or l.FullPath.startswith(ROOT + '::'):
            for o in doc.Objects.FindByLayer(l):
                if doc.Objects.Delete(o.Id, True): n += 1
    print('cleared', n)

def attr(lay, name=''):
    a = Rhino.DocObjects.ObjectAttributes(); a.LayerIndex = lay.Index; a.Name = name; return a

def ring_area(pts):
    a = 0.0
    for i in range(len(pts) - 1): a += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
    return a / 2.0

def curve_of(pts, z, ccw=True):
    pts = [list(p) for p in pts]
    if pts[0][0] != pts[-1][0] or pts[0][1] != pts[-1][1]: pts.append(pts[0])
    if (ring_area(pts) > 0) != ccw: pts = pts[::-1]
    return rg.PolylineCurve([rg.Point3d(p[0], p[1], z) for p in pts])

cnt = {}
for e in ds['elements']:
    k = e['kind']; d = e['data']; lay = layer(e['layer']); a = attr(lay, e['name'])
    if k == 'mesh':
        m = rg.Mesh()
        for v in d['v']: m.Vertices.Add(v[0], v[1], v[2])
        for f in d['f']: m.Faces.AddFace(f[0], f[1], f[2])
        m.Normals.ComputeNormals(); m.Compact()
        doc.Objects.AddMesh(m, a)
    elif k == 'extrude':
        c = curve_of(d['ext'], d['z0'], True)
        ex = rg.Extrusion.Create(c, d['z1'] - d['z0'], True)
        if ex is None: continue
        for h in d['holes']: ex.AddInnerProfile(curve_of(h, d['z0'], False))
        doc.Objects.AddExtrusion(ex, a)
    elif k == 'tree':
        if not TREES: continue
        x, y, z, r = d
        trunk = rg.Extrusion.Create(rg.Circle(rg.Point3d(x, y, z), r * 0.09).ToNurbsCurve(), r * 1.25, True)
        if trunk is not None: doc.Objects.AddExtrusion(trunk, a)
        doc.Objects.AddSphere(rg.Sphere(rg.Point3d(x, y, z + r * 1.95), r), a)
    elif k == 'dot':
        x, y, z, t = d; td = rg.TextDot(t, rg.Point3d(x, y, z)); td.FontHeight = 11; doc.Objects.AddTextDot(td, a)
    elif k == 'curve':
        doc.Objects.AddCurve(rg.PolylineCurve([rg.Point3d(p[0], p[1], p[2]) for p in d]), a)
    cnt[k] = cnt.get(k, 0) + 1
doc.Views.Redraw()
print('built', ROOT, cnt)
