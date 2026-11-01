import json, pickle, numpy as np, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib import font_manager
from shapely.geometry import Polygon
for f in font_manager.findSystemFonts():
    if 'malgun' in f.lower(): font_manager.fontManager.addfont(f)
plt.rcParams['font.family'] = 'Malgun Gothic'
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, '..', 'data')
U = pickle.load(open(os.path.join(D, 'U_clean.pkl'), 'rb'))['U']
C = json.load(open(os.path.join(D, 'ctx_candidates.json'), encoding='utf-8'))
G = pickle.load(open(os.path.join(D, 'geo.pkl'), 'rb'))
col = {'대지': '#cfe3b0', '인도': '#eadfc0', '경계석': '#bdbdbd', '하천': '#9cc7e8', '빌딩': '#8a8a8a', '도로': '#f2f2f2'}
fig, ax = plt.subplots(figsize=(13, 17))
order = ['도로', '하천', '대지', '인도', '경계석', '빌딩']
for L in order:
    for o in C:
        if o['layer'] != L: continue
        rings = o.get('rings', [])
        if not rings: continue
        # draw only first ring (top); skip huge roads
        r = rings[0]
        if L == '도로' and len(r) > 5000: continue
        ax.add_patch(MPoly(np.array(r), closed=True, fc=col[L], ec='#555555', lw=0.2, alpha=0.9 if L != '대지' else 0.7))
# plan tiles light
for p in G['parcels']:
    ax.add_patch(MPoly(np.array(p['g'].exterior.coords), closed=True, fc='none', ec='#1f77b4', lw=0.6))
x, y = U.exterior.xy
ax.plot(x, y, color='r', lw=1.4)
for o in C:
    if o['layer'] == '철도경계' and 'pts' in o:
        ax.plot(*np.array(o['pts']).T, color='m', lw=1.0)
b = U.bounds
ax.set_xlim(b[0] - 80, b[2] + 80); ax.set_ylim(b[1] - 80, b[3] + 80); ax.set_aspect('equal')
plt.tight_layout(); plt.savefig(os.path.join(D, '..', 'sheets', 'ctx_vs_boundary.png'), dpi=100)
print('ok')
