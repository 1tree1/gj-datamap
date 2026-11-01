# -*- coding: utf-8 -*-
"""S5 라이노 조립(Rhino 8 Python, run_python 으로 실행). data/design.json 을 읽어 armadillo 문서(맥락 + 사용자 원본이 이미 들어 있음)에 마스터플랜을 얹는다.
- 사용자 도로·보도 Brep 은 복제하지 않고 레이어만 옮긴다(형상 그대로).  - 원 획지 14개는 숨김 레이어로 보존.
- 새 획지·공원·광장은 z=0 평면 서피스, 매스는 닫힌 Extrusion."""
import Rhino, System, json, math, time
import Rhino.Geometry as rg
doc = __rhino_doc__
D = r'C:\Users\OFFICE\Desktop\9_도시\work\20261011_masterplan_v1\data\design.json'
ds = json.load(open(D, encoding='utf-8'))
TOL = 0.01
t0 = time.time()

def hex2c(h, mix=0.0):
    h = h.lstrip('#'); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = int(r + (255 - r) * mix); g = int(g + (255 - g) * mix); b = int(b + (255 - b) * mix)
    return System.Drawing.Color.FromArgb(r, g, b)

def add_layer(name, color, parent=None, visible=True):
    full = name if parent is None else parent.FullPath + '::' + name
    idx = doc.Layers.FindByFullPath(full, -1)
    if idx >= 0:
        l = doc.Layers[idx]; l.Color = color; doc.Layers.Modify(l, idx, True); return doc.Layers[idx]
    l = Rhino.DocObjects.Layer(); l.Name = name; l.Color = color
    if parent is not None: l.ParentLayerId = parent.Id
    idx = doc.Layers.Add(l)
    l = doc.Layers[idx]
    l.IsVisible = visible; doc.Layers.Modify(l, idx, True)
    return doc.Layers[idx]

def attr(layer, name=''):
    a = Rhino.DocObjects.ObjectAttributes(); a.LayerIndex = layer.Index; a.Name = name; return a

def ring_area(pts):
    a = 0.0
    for i in range(len(pts) - 1):
        a += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
    return a / 2.0

def curve_of(pts, z, ccw=True):
    pts = [list(p) for p in pts]
    if (ring_area(pts) > 0) != ccw: pts = pts[::-1]
    return rg.PolylineCurve([rg.Point3d(p[0], p[1], z) for p in pts])

def planar(part, z=0.0):
    crvs = [curve_of(part['ext'], z, True)] + [curve_of(h, z, False) for h in part['holes']]
    bs = rg.Brep.CreatePlanarBreps(crvs, TOL)
    return list(bs) if bs else []

def extrude(part, z0, z1):
    c = curve_of(part['ext'], z0, True)
    e = rg.Extrusion.Create(c, z1 - z0, True)
    if e is None: return None
    for h in part['holes']:
        e.AddInnerProfile(curve_of(h, z0, False))
    return e

# ── 레이어 ───────────────────────────────────────────────────────────────────
root = add_layer('마스터플랜_v1', System.Drawing.Color.FromArgb(60, 60, 60))
L0 = add_layer('00 계획 경계', System.Drawing.Color.FromArgb(220, 30, 60), root)
L1 = add_layer('01 건축 획지(지구단위계획 용도)', System.Drawing.Color.FromArgb(200, 200, 200), root)
LOTL = {}
for nm, col in (('공공업무시설', '#4C78B8'), ('업무시설', '#E4573A'), ('공동주택', '#F1D247'), ('문화 및 집회시설', '#6F9FDC'), ('근린생활·판매시설', '#F4A0C2'),
                ('운동시설', '#2FAB9D'), ('관광휴게·주차전용', '#8E8E8E')):
    LOTL[nm] = add_layer(nm, hex2c(col, 0.35), L1)
L2 = add_layer('02 공원·녹지·광장', System.Drawing.Color.FromArgb(120, 190, 90), root)
GRNL = {'근린공원': add_layer('근린공원', hex2c('#8FCF7A'), L2), '문화공원': add_layer('문화공원', hex2c('#9AD684'), L2), '역사공원': add_layer('역사공원', hex2c('#7FC66A'), L2),
        '경관녹지': add_layer('경관녹지', hex2c('#A9D98D'), L2)}
PLZL = {'광장': add_layer('광장', hex2c('#E7E1D0'), L2), '마당': add_layer('마당', hex2c('#EADFC8'), L2), '텃밭': add_layer('텃밭', hex2c('#B7A27A'), L2)}
L5 = add_layer('05 매스', System.Drawing.Color.FromArgb(150, 150, 150), root)
MASL = {}
for nm, col in (('공공업무', '#4C78B8'), ('상업·업무', '#E4573A'), ('주거', '#F1D247'), ('문화·교육·공공', '#6F9FDC'), ('창조산업', '#A98BD3'), ('판매·음식', '#F4A0C2'),
                ('여가·오락·체육', '#2FAB9D'), ('역사유산', '#C9742F'), ('교통·방문자', '#C6C6C6'), ('주차전용건축물', '#8E8E8E')):
    MASL[nm] = add_layer(nm, hex2c(col), L5)
LPAV = add_layer('공원 파빌리온', hex2c('#B8A98A'), L5)
L7 = add_layer('07 식재', System.Drawing.Color.FromArgb(60, 140, 60), root)
TREEL = {'street': add_layer('가로수', hex2c('#4E9A51'), L7), 'park': add_layer('공원수', hex2c('#3F8F45'), L7), 'lot': add_layer('획지수', hex2c('#5BA85D'), L7)}
L8 = add_layer('08 라벨', System.Drawing.Color.FromArgb(30, 30, 30), root)
L99 = add_layer('99 원본 획지(사용자 14개, 숨김)', System.Drawing.Color.FromArgb(255, 127, 0), root, visible=False)
L03 = add_layer('03 보도(사용자 원본 4개)', System.Drawing.Color.FromArgb(205, 205, 205), root)
L04 = add_layer('04 도로(사용자 원본 2개)', System.Drawing.Color.FromArgb(105, 105, 105), root)
L06 = add_layer('06 구 역사(존치, 사용자 원본)', hex2c('#C9742F'), root)
L99.IsVisible = False; doc.Layers.Modify(L99, L99.Index, True)

# 맥락 루트 이름 정리
idx = doc.Layers.FindByFullPath('맥락_원본(×2·회전 변환)', -1)
if idx >= 0:
    l = doc.Layers[idx]; l.Name = '90 맥락(주변, 계획 경계로 뚫음)'; doc.Layers.Modify(l, idx, True)

# ── 사용자 원본 객체를 새 레이어로 이동(형상은 그대로) ────────────────────────
moved = {'도로': 0, '보도': 0, '획지': 0, '구역사': 0}
for o in list(doc.Objects):
    lay = doc.Layers[o.Attributes.LayerIndex].FullPath
    if not lay.startswith('계획_원본(사용자 도면)'): continue
    sub = lay.split('::')[-1]
    a = o.Attributes.Duplicate()
    if sub == '도로': a.LayerIndex = L04.Index; moved['도로'] += 1
    elif sub == '보도': a.LayerIndex = L03.Index; moved['보도'] += 1
    elif sub.startswith('획지'): a.LayerIndex = L99.Index; moved['획지'] += 1
    elif sub == '구 역사': a.LayerIndex = L06.Index; moved['구역사'] += 1
    else: continue
    doc.Objects.ModifyAttributes(o, a, True)
print('moved', moved, round(time.time() - t0, 1))

# ── 계획 경계 ───────────────────────────────────────────────────────────────
doc.Objects.AddCurve(curve_of(ds['boundary'], 0.0, True), attr(L0, '계획 경계 228,025㎡'))

# ── 건축 획지 ───────────────────────────────────────────────────────────────
LOTMAP = {'공1': '공공업무시설', '업1': '업무시설', '업2': '업무시설', '주1': '공동주택', '문1': '문화 및 집회시설', '문2': '문화 및 집회시설', '문3': '근린생활·판매시설',
          '문4': '문화 및 집회시설', '문5': '문화 및 집회시설', '상1': '근린생활·판매시설', '체1': '운동시설', '관1': '관광휴게·주차전용'}
n_lot = 0; a_lot = 0.0
for lo in ds['lots']:
    ly = LOTL[LOTMAP[lo['code']]]
    for part in lo['parts']:
        for b in planar(part, 0.0):
            doc.Objects.AddBrep(b, attr(ly, '%s 획지 | %s | %.0f㎡' % (lo['code'], lo['use'], lo['area']))); n_lot += 1
            a_lot += rg.AreaMassProperties.Compute(b).Area
# ── 공원·녹지 ───────────────────────────────────────────────────────────────
n_g = 0; a_g = 0.0
for g in ds['greens']:
    ly = GRNL[g['kind']]
    for part in g['parts']:
        for b in planar(part, 0.0):
            doc.Objects.AddBrep(b, attr(ly, '%s %s | %s | %.0f㎡' % (g['code'], g['kind'], g['name'], g['area']))); n_g += 1
            a_g += rg.AreaMassProperties.Compute(b).Area
# ── 광장·마당·텃밭(획지·공원 위 0.05 m) ─────────────────────────────────────
n_p = 0
for p in ds['plazas']:
    ly = PLZL[p['kind']]
    for part in p['parts']:
        for b in planar(part, 0.05):
            doc.Objects.AddBrep(b, attr(ly, '%s (%s) | %.0f㎡' % (p['name'], p['host'], p['area']))); n_p += 1
print('surfaces: lots', n_lot, round(a_lot, 1), 'greens', n_g, round(a_g, 1), 'plazas', n_p, round(time.time() - t0, 1))

# ── 매스 ────────────────────────────────────────────────────────────────────
n_m = 0
for m in ds['masses']:
    if m.get('existing'): continue
    ly = MASL[m['cat']]
    for part in m['parts']:
        e = extrude(part, 0.0, m['h'])
        if e is None: continue
        doc.Objects.AddExtrusion(e, attr(ly, '%s | %s | %dF %.1fm' % (m['lot'], m['name'], m['floors'], m['h']))); n_m += 1
for pv in ds['pavilions']:
    for part in pv['parts']:
        e = extrude(part, 0.0, 3.6)
        if e: doc.Objects.AddExtrusion(e, attr(LPAV, '공원 그늘쉼터 파빌리온 30㎡')); n_m += 1
print('masses', n_m, round(time.time() - t0, 1))

# ── 식재(메시) ──────────────────────────────────────────────────────────────
def tree_mesh(pts):
    big = rg.Mesh()
    for x, y, r in pts:
        trunk = rg.Mesh.CreateFromCylinder(rg.Cylinder(rg.Circle(rg.Plane(rg.Point3d(x, y, 0.0), rg.Vector3d.ZAxis), 0.28), 3.0), 1, 6, True, True)
        crown = rg.Mesh.CreateIcoSphere(rg.Sphere(rg.Point3d(x, y, 3.0 + 0.8 * r), r), 1)
        if trunk: big.Append(trunk)
        if crown: big.Append(crown)
    big.Normals.ComputeNormals(); big.Compact()
    return big
nt = 0
for k, pts in ds['trees'].items():
    # 레이어당 메시 1개씩(너무 크지 않게 250그루씩 나눔)
    for i in range(0, len(pts), 250):
        mm = tree_mesh(pts[i:i + 250])
        doc.Objects.AddMesh(mm, attr(TREEL[k], '식재 %s %d' % (k, i // 250))); nt += len(pts[i:i + 250])
print('trees', nt, round(time.time() - t0, 1))

# ── 라벨 ────────────────────────────────────────────────────────────────────
for lb in ds['labels']:
    doc.Objects.AddTextDot(lb['text'], rg.Point3d(lb['x'], lb['y'], 22.0 if lb['kind'] == 'lot' else 6.0), attr(L8, lb['text']))
doc.Views.Redraw()
print('done', round(time.time() - t0, 1), 'objects', doc.Objects.Count)