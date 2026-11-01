import json, pickle, numpy as np, math
from shapely.geometry import Polygon, LineString
from shapely import STRtree, affinity
from shapely.ops import unary_union
import xf as XF
U = pickle.load(open('../data/U_clean.pkl', 'rb'))['U']
C = json.load(open('../data/ctx_candidates.json', encoding='utf-8'))
t_a = np.array([-1143000.06, -1763303.35])
bl = []
for o in C:
    if o['layer'] != '빌딩' or not o.get('rings'): continue
    a = XF.plan2ctx(np.array(o['rings'][0])); p = Polygon(2 * a + t_a)
    if p.is_valid and p.area > 3: bl.append(p)
B = unary_union(bl)
ring = U.exterior
res = []
for dx in np.arange(-18, -12.01, 0.25):
    for dy in np.arange(58, 64.01, 0.25):
        r = affinity.translate(ring, -dx, -dy)
        L = r.intersection(B).length
        res.append((L, dx, dy))
res.sort()
print('min boundary length inside buildings:')
for r in res[:8]: print('  %.2f m at shift (%.2f, %.2f)' % r)
Ls = np.array([r[0] for r in res]); print('median %.1f m  min %.2f m' % (np.median(Ls), Ls.min()))
good = [r for r in res if r[0] <= res[0][0] + 0.5]
cx = np.mean([g[1] for g in good]); cy = np.mean([g[2] for g in good]); print('plateau (<= min+0.5 m): n=%d  center shift (%.2f, %.2f)' % (len(good), cx, cy))
print('t_b = t_a + shift =', (t_a + [cx, cy]).round(2))
pickle.dump(dict(t=(t_a + [cx, cy]).tolist(), shift=(cx, cy)), open('../data/xf_true.pkl', 'wb'))
