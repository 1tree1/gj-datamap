import json, pickle, numpy as np, math, time
from shapely.geometry import Polygon, LineString
from shapely import STRtree, affinity
import xf as XF
U = pickle.load(open('../data/U_clean.pkl', 'rb'))['U']
C = json.load(open('../data/ctx_candidates.json', encoding='utf-8'))
F = json.load(open('../data/ctx_faces.json', encoding='utf-8'))
OB = json.load(open('../data/old_boundaries.json'))
t_a = np.array([-1143000.06, -1763303.35])
bl = []
for o in C:
    if o['layer'] != '빌딩' or not o.get('rings'): continue
    a = XF.plan2ctx(np.array(o['rings'][0])); p = Polygon(2 * a + t_a)
    if p.is_valid and p.area > 3: bl.append(p)
tree = STRtree(bl)
# lots / walks faces (top) in the doubled frame
faces = []; flayer = []
for f in F:
    if f['layer'] in ('대지', '인도') and len(f['ring']) < 20000:
        a = XF.plan2ctx(np.array(f['ring'])); p = Polygon(2 * a + t_a)
        if not p.is_valid: p = p.buffer(0)
        if p.area > 5 and p.area < 2e6: faces.append(p); flayer.append(f['layer'])
ftree = STRtree(faces)
ring = U.exterior
v3 = Polygon(2 * np.array(OB['v3'][0])[:, :2] + t_a).buffer(0)
res = []
for dx in np.arange(-24, -6.01, 0.5):
    for dy in np.arange(50, 70.01, 0.5):
        r = affinity.translate(ring, -dx, -dy)
        nb = len(tree.query(r, predicate='intersects'))
        nf = len(ftree.query(r, predicate='intersects'))
        iou = affinity.translate(v3, dx, dy).intersection(U).area / affinity.translate(v3, dx, dy).union(U).area
        res.append((nb, nf, -iou, dx, dy))
res.sort()
print('top by (cut bldgs, cut faces):')
for r in res[:10]: print('  cut bldgs %d  cut lot/walk faces %d  IoU %.3f  shift (%.1f, %.1f)' % (r[0], r[1], -r[2], r[3], r[4]))
nbmin = res[0][0]
cand = [r for r in res if r[0] == nbmin]
print('n shifts with min cut bldgs (%d): %d  → mean shift (%.2f, %.2f)' % (nbmin, len(cand), np.mean([c[3] for c in cand]), np.mean([c[4] for c in cand])))
cf = sorted(res, key=lambda r: (r[1], r[0]))[:5]
for r in cf: print('  by faces: cut faces %d cut bldgs %d shift (%.1f, %.1f)' % (r[1], r[0], r[3], r[4]))
