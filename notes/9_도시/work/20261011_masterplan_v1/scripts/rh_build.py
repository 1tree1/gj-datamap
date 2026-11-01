# -*- coding: utf-8 -*-
"""라이노 빌더 (Rhino 8 Python 3, run_python 안에서 exec). design_v3.json 을 읽어 지구단위계획 마스터플랜 레이어 트리를 만든다.
PARAMS(호출측 전역):
  JSON   : design_v3.json 경로
  ROOT   : 루트 레이어 이름
  M      : 계획 좌표(m, z=0) → 문서 좌표 변환 (Rhino.Geometry.Transform). 항등이면 None
  Z      : dict(lot=0, green=0, plaza=0, walk=0, road=0, base=None)  계획 좌표계 기준 상단 z 와 바닥 z(base=None 이면 평면 서피스)
  PALETTE: 'color' | 'redbw'
  TREES  : True/False
"""
import Rhino, System, json, math
import Rhino.Geometry as rg
doc = __rhino_doc__
TOL = 0.01
ds = json.load(open(JSON, encoding='utf-8'))
MX = M if M is not None else rg.Transform.Identity

def hexc(h):
    h = h.lstrip('#'); return System.Drawing.Color.FromArgb(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

if PALETTE == 'redbw':
    C = dict(bound='#C8102E', lot='#E6E6E6', green='#D9D9D9', plaza='#F2F2F2', walk='#F7F7F7', road='#FFFFFF', tree='#9A9A9A', label='#111111',
             mass={'공공업무': '#4A4A4A', '주거': '#8C8C8C', '상업·업무': '#6E6E6E', '문화·교육·공공': '#C8102E', '창조산업': '#A6A6A6', '판매·음식': '#B5B5B5',
                   '여가·오락·체육': '#7A7A7A', '역사유산': '#8B0A1E', '교통·방문자': '#BEBEBE', '주차전용건축물': '#CFCFCF', '파빌리온': '#D0D0D0'},
             lots={'공공청사': '#DADADA', '공동주택': '#E0E0E0', '업무시설': '#DEDEDE', '문화및집회시설': '#F3D5DA', '근린생활·판매시설': '#E8E8E8', '운동시설': '#E3E3E3', '주차전용·관광휴게': '#ECECEC'},
             greens={'근린공원': '#D6D6D6', '문화공원': '#DADADA', '역사공원': '#D2D2D2', '경관녹지': '#DCDCDC'})
else:
    C = dict(bound='#DC1E3C', lot='#C8C8C8', green='#78BE5A', plaza='#E7E1D0', walk='#CDCDCD', road='#696969', tree='#3F8F45', label='#1E1E1E',
             mass={'공공업무': '#4C78B8', '주거': '#F1D247', '상업·업무': '#E4573A', '문화·교육·공공': '#6F9FDC', '창조산업': '#A98BD3', '판매·음식': '#F4A0C2',
                   '여가·오락·체육': '#2FAB9D', '역사유산': '#C9742F', '교통·방문자': '#C6C6C6', '주차전용건축물': '#8E8E8E', '파빌리온': '#B8A98A'},
             lots={'공공청사': '#B7C9E6', '공동주택': '#F8EBA8', '업무시설': '#F4B8A8', '문화및집회시설': '#C3D8F1', '근린생활·판매시설': '#FAD2E3', '운동시설': '#A9DDD6', '주차전용·관광휴게': '#D0D0D0'},
             greens={'근린공원': '#8FCF7A', '문화공원': '#9AD684', '역사공원': '#7FC66A', '경관녹지': '#A9D98D'})

def add_layer(name, color, parent=None):
    full = name if parent is None else parent.FullPath + '::' + name
    idx = doc.Layers.FindByFullPath(full, -1)
    if idx >= 0:
        l = doc.Layers[idx]; l.Color = hexc(color); doc.Layers.Modify(l, idx, True); return doc.Layers[idx]
    l = Rhino.DocObjects.Layer(); l.Name = name; l.Color = hexc(color)
    if parent is not None: l.ParentLayerId = parent.Id
    idx = doc.Layers.Add(l); return doc.Layers[idx]

def attr(layer, name=''):
    a = Rhino.DocObjects.ObjectAttributes(); a.LayerIndex = layer.Index; a.Name = name; return a

def ring_area(pts):
    a = 0.0
    for i in range(len(pts) - 1): a += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
    return a / 2.0

def curve_of(pts, z, ccw=True):
    pts = [list(p) for p in pts]
    if pts[0][0] != pts[-1][0] or pts[0][1] != pts[-1][1]: pts.append(pts[0])
    if (ring_area(pts) > 0) != ccw: pts = pts[::-1]
    return rg.PolylineCurve([rg.Point3d(p[0], p[1], z) for p in pts])

def planar(part, z):
    crvs = [curve_of(part['ext'], z, True)] + [curve_of(h, z, False) for h in part['holes']]
    bs = rg.Brep.CreatePlanarBreps(crvs, TOL)
    return list(bs) if bs else []

def extrude(part, z0, z1):
    c = curve_of(part['ext'], z0, True)
    e = rg.Extrusion.Create(c, z1 - z0, True)
    if e is None: return None
    for h in part['holes']: e.AddInnerProfile(curve_of(h, z0, False))
    return e

def put(geo, layer, name=''):
    if geo is None: return None
    g = geo.Duplicate() if hasattr(geo, 'Duplicate') else geo
    g.Transform(MX)
    if isinstance(g, rg.Curve): return doc.Objects.AddCurve(g, attr(layer, name))
    if isinstance(g, rg.Extrusion): return doc.Objects.AddExtrusion(g, attr(layer, name))
    if isinstance(g, rg.Brep): return doc.Objects.AddBrep(g, attr(layer, name))
    if isinstance(g, rg.TextDot): return doc.Objects.AddTextDot(g, attr(layer, name))
    if isinstance(g, rg.Sphere): return doc.Objects.AddSphere(g, attr(layer, name))
    return doc.Objects.Add(g, attr(layer, name))

def slab(parts, layer, ztop, name=''):
    n = 0
    for part in parts:
        if Z.get('base') is None:
            for b in planar(part, ztop): put(b, layer, name); n += 1
        else:
            e = extrude(part, Z['base'], ztop)
            if e is not None: put(e, layer, name); n += 1
            else:
                for b in planar(part, ztop): put(b, layer, name); n += 1
    return n

root = add_layer(ROOT, '#3C3C3C')
L00 = add_layer('00 계획구역 경계', C['bound'], root)
L01 = add_layer('01 획지(건축용지)', C['lot'], root)
LOTL = {k: add_layer(k, v, L01) for k, v in C['lots'].items()}
L02 = add_layer('02 공원·녹지(도시계획시설)', C['green'], root)
GRNL = {k: add_layer(k, v, L02) for k, v in C['greens'].items()}
L03 = add_layer('03 광장·공공공지', C['plaza'], root)
PLZL = {k: add_layer(k, C['plaza'], L03) for k in ('광장', '마당', '텃밭')}
L04 = add_layer('04 도로', C['road'], root)
L05 = add_layer('05 보행자전용도로·보도', C['walk'], root)
WLKL = {k: add_layer(k, C['walk'], L05) for k in ('보행자전용도로', '보도')}
L06 = add_layer('06 건축물(매스)', '#8C8C8C', root)
MASL = {k: add_layer(k if k != '역사유산' else '역사유산(구 역사 존치)', v, L06) for k, v in C['mass'].items()}
L07 = add_layer('07 식재', C['tree'], root)
TREEL = {'street': add_layer('가로수', C['tree'], L07), 'park': add_layer('공원수', C['tree'], L07), 'lot': add_layer('획지 조경수', C['tree'], L07)}
L08 = add_layer('08 라벨', C['label'], root)

cnt = {}
# 경계
put(curve_of(ds['boundary'], Z['lot'] + 0.05, True), L00, '계획구역 경계'); cnt['boundary'] = 1
# 획지
cnt['lots'] = sum(slab(l['parts'], LOTL[l['layer']], Z['lot'], '%s %s' % (l['code'], l['use'])) for l in ds['lots'])
cnt['greens'] = sum(slab(g['parts'], GRNL[g['kind']], Z['green'], '%s %s %s' % (g['code'], g['kind'], g['name'])) for g in ds['greens'])
cnt['plazas'] = sum(slab(p['parts'], PLZL.get(p['kind'], L03), Z['plaza'] + 0.02, '%s(%s)' % (p['name'], p['host'])) for p in ds['plazas'])
cnt['roads'] = sum(slab(r['parts'], L04, Z['road'], '도로') for r in ds['roads'])
cnt['walks'] = sum(slab(w['parts'], WLKL[w['kind']], Z['walk'], w['kind']) for w in ds['walks'])
# 매스
n = 0
for m in ds['masses']:
    lay = MASL[m['cat']]
    for part in m['parts']:
        e = extrude(part, Z['lot'], Z['lot'] + m['h'])
        if e is not None: put(e, lay, '%s %s' % (m['lot'], m['name'])); n += 1
for pv in ds['pavilions']:
    for part in pv['parts']:
        e = extrude(part, Z['green'], Z['green'] + 4.5)
        if e is not None: put(e, MASL['파빌리온'], '공원 파빌리온'); n += 1
cnt['masses'] = n
# 식재
if TREES:
    n = 0
    for kind, pts in ds['trees'].items():
        lay = TREEL[kind]; r = {'street': 2.6, 'park': 3.4, 'lot': 2.4}[kind]; zb = {'street': Z['walk'], 'park': Z['green'], 'lot': Z['lot']}[kind]
        for p in pts:
            x, y = p[0], p[1]
            trunk = rg.Extrusion.Create(rg.Circle(rg.Point3d(x, y, zb), 0.22).ToNurbsCurve(), r * 1.25, True)
            if trunk is not None: put(trunk, lay);
            sph = rg.Sphere(rg.Point3d(x, y, zb + r * 1.25 + r * 0.7), r)
            put(sph.ToBrep(), lay); n += 1
    cnt['trees'] = n
# 라벨
for lb in ds['labels']:
    d = rg.TextDot(lb['text'], rg.Point3d(lb['x'], lb['y'], Z['lot'] + 0.1)); d.FontHeight = 11
    put(d, L08)
cnt['labels'] = len(ds['labels'])
doc.Views.Redraw()
print('built', ROOT, cnt)
