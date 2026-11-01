import pickle, numpy as np, os, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib import font_manager
for f in font_manager.findSystemFonts():
    if 'malgun' in f.lower(): font_manager.fontManager.addfont(f)
plt.rcParams['font.family'] = 'Malgun Gothic'
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
L = pickle.load(open(os.path.join(D, 'lots.pkl'), 'rb'))
masses = None
mp = os.path.join(D, 'masses.pkl')
if os.path.exists(mp): masses = pickle.load(open(mp, 'rb'))
def polys(g):
    if g.is_empty: return []
    return [g] if g.geom_type == 'Polygon' else [p for x in g.geoms for p in polys(x)]
fig, ax = plt.subplots(figsize=(10, 15))
def draw(g, fc, ec='k', lw=0.4, alpha=1.0, z=1):
    for p in polys(g):
        ax.add_patch(MPoly(np.array(p.exterior.coords), closed=True, fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=z))
        for r in p.interiors:
            ax.add_patch(MPoly(np.array(r.coords), closed=True, fc='white', ec=ec, lw=lw, zorder=z))
for w in L['WALKS']: draw(w, '#efe8d6', '#bbb', 0.3)
for r in L['ROADS']: draw(r, '#9a9a9a', '#666', 0.3)
cm = {'공1': '#6F9FDC', '업1': '#E4573A', '업2': '#E4573A', '주1': '#F1D247', '문1': '#8fb3e8', '문2': '#C9742F', '문3': '#F4A0C2', '문4': '#A98BD3', '문5': '#A98BD3', '상1': '#F4A0C2', '체1': '#2FAB9D', '관1': '#C6C6C6'}
for k, v in L['LOT'].items():
    draw(v['g'], cm.get(k, '#ccc'), 'k', 0.6, 0.55, 2)
    c = v['g'].representative_point()
    ax.text(c.x, c.y, '%s\n%.0f' % (k, v['area']), ha='center', va='center', fontsize=7, zorder=5)
gc = {'근린공원': '#9bd17a', '경관녹지': '#b7dd96', '문화공원': '#a8d98a', '역사공원': '#8fcf7a'}
for k, v in L['GRN'].items():
    draw(v['g'], gc.get(v['kind'], '#9bd17a'), '#4a7a30', 0.6, 0.8, 2)
    c = v['g'].representative_point()
    ax.text(c.x, c.y, '%s\n%s\n%.0f' % (k, v['kind'], v['area']), ha='center', va='center', fontsize=7, zorder=5)
if masses:
    for m in masses['masses']:
        draw(m['g'], m['color'], '#222', 0.5, 0.95, 4)
ax.set_aspect('equal'); ax.set_xlim(0, 340); ax.set_ylim(40, 1010)
ax.set_xticks(range(0, 341, 50)); ax.set_yticks(range(50, 1011, 50)); ax.grid(True, lw=0.3, alpha=0.5)
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, '..', 'sheets', 'lots_check.png')
plt.tight_layout(); plt.savefig(out, dpi=90); print(out)
