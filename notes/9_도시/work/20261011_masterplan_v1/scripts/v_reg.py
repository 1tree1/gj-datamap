import json, pickle, numpy as np, sys, math
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import LineCollection, PatchCollection
import xf as XF
t = np.array([float(sys.argv[1]), float(sys.argv[2])]); out = sys.argv[3]
U = pickle.load(open('../data/U_clean.pkl', 'rb'))['U']
G = pickle.load(open('../data/geo.pkl', 'rb'))
F = json.load(open('../data/ctx_faces.json', encoding='utf-8'))
CB = json.load(open('../data/ctx_buildings_planframe.json'))     # armadillo 맥락(옛 변환 T 좌표)  → 옛 좌표 → 새 변환
def to_new(a):          # T 좌표(plan frame by old T) → old → new
    o = XF.plan2ctx(np.asarray(a)); return 2 * o + t
fig, ax = plt.subplots(figsize=(9, 14))
segs = []
for f in F:
    if f['layer'] in ('대지', '인도', '경계석'):
        a = to_new(f['ring']); segs.append(a)
        for h in f['holes']:
            if len(h) > 3: segs.append(to_new(h))
    elif f['layer'] == '도로':
        for h in f['holes']:
            if 3 < len(h) < 5000: segs.append(to_new(h))
ax.add_collection(LineCollection(segs, colors='#9a9a9a', linewidths=0.4, zorder=1))
pats = []
for b in CB:
    pts = np.array(b['p']); pats.append(MPoly(to_new(pts), closed=True))
ax.add_collection(PatchCollection(pats, fc='#d6d6d6', ec='none', alpha=0.6, zorder=0))
cols = ['#e6550d','#3182bd','#31a354','#756bb1','#d6616b','#e7ba52','#17becf','#8c6d31','#bd9e39','#ce6dbd','#6b6ecf','#9c9ede','#8ca252','#e377c2']
for i, p in enumerate(G['parcels']):
    ax.add_patch(MPoly(np.array(p['g'].exterior.coords), closed=True, fc=cols[i % 14], ec='k', lw=0.4, alpha=0.35, zorder=2))
for w in G['walks']: ax.add_patch(MPoly(np.array(w['g'].exterior.coords), closed=True, fc='none', ec='#cc8800', lw=0.5, zorder=3))
for r in G['roads']: ax.add_patch(MPoly(np.array(r['g'].exterior.coords), closed=True, fc='none', ec='#333', lw=0.5, zorder=3))
x, y = U.exterior.xy; ax.plot(x, y, color='r', lw=1.2, zorder=4)
b = U.bounds; ax.set_xlim(b[0] - 120, b[2] + 120); ax.set_ylim(b[1] - 120, b[3] + 120); ax.set_aspect('equal')
plt.tight_layout(); plt.savefig(out, dpi=85); print(out)
