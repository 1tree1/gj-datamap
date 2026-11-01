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
G = pickle.load(open(os.path.join(D, 'geo.pkl'), 'rb'))
bp = json.load(open(os.path.join(D, '..', '..', '..', '..', 'AppData','Local','Temp','claude','C--Users-OFFICE-Desktop-9---','208a6fca-848a-4422-ad91-655fc023df64','scratchpad','bld_pair.json'))) if False else None
OX, OY = 1167200.0, 1761100.0
fig, ax = plt.subplots(figsize=(10, 15))
for w in G['walks']:
    ax.add_patch(MPoly(np.array(w['g'].exterior.coords) - [OX, OY], closed=True, fc='#efe8d6', ec='#aaa', lw=0.3))
    for r in w['g'].interiors:
        ax.add_patch(MPoly(np.array(r.coords) - [OX, OY], closed=True, fc='white', ec='#aaa', lw=0.3))
for r_ in G['roads']:
    ax.add_patch(MPoly(np.array(r_['g'].exterior.coords) - [OX, OY], closed=True, fc='#9a9a9a', ec='#666', lw=0.3))
    for r in r_['g'].interiors:
        ax.add_patch(MPoly(np.array(r.coords) - [OX, OY], closed=True, fc='white', ec='#666', lw=0.3))
cols = ['#e6550d','#3182bd','#31a354','#756bb1','#d6616b','#e7ba52','#17becf','#8c6d31','#bd9e39','#ce6dbd','#6b6ecf','#9c9ede','#8ca252','#e377c2']
order = sorted(range(len(G['parcels'])), key=lambda i: (G['parcels'][i]['rep'][1]))
for n, i in enumerate(order):
    p = G['parcels'][i]
    ax.add_patch(MPoly(np.array(p['g'].exterior.coords) - [OX, OY], closed=True, fc=cols[n % len(cols)], ec='k', lw=0.6, alpha=0.55))
    c = np.array(p['g'].representative_point().coords[0]) - [OX, OY]
    ax.text(c[0], c[1], '%d\n%s\n%.0f' % (n + 1, p['layer'][:9], p['area']), ha='center', va='center', fontsize=7)
ax.set_aspect('equal'); ax.set_xlim(0, 340); ax.set_ylim(40, 1010)
ax.set_xticks(range(0, 341, 50)); ax.set_yticks(range(50, 1011, 50)); ax.grid(True, lw=0.3, alpha=0.6)
plt.tight_layout(); plt.savefig(os.path.join(D, '..', 'sheets', 'plan_labeled.png'), dpi=95)
# print parcel table sorted south->north with index
for n, i in enumerate(order):
    p = G['parcels'][i]; b = p['g'].bounds
    print(n + 1, p['layer'][:20], round(p['area'], 1), 'bbox', [round(v - o) for v, o in zip(b, [OX, OY, OX, OY])], 'verts', len(p['g'].exterior.coords))
