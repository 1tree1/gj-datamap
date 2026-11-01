# -*- coding: utf-8 -*-
"""용도별 색 획지 배분도(Bucha 식): 최종 도로계획 + 프로그램 색 획지 + 면적 라벨, 북쪽 위, 맥락 흑백."""
import json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import PatchCollection, LineCollection
from shapely.geometry import Polygon
from pyproj import Transformer
from diag_palette import *
plt.rcParams['font.family'] = 'Pretendard'; plt.rcParams['axes.unicode_minus'] = False
R = 'C:/Users/OFFICE/Desktop/9_도시'; D = R + '/gj-datamap/public/data'
P = json.load(open('data/road_plan_final_plan.json', encoding='utf-8'))
SHIFT = np.array([-1143015.56 + 1155149.0, -1763242.48 + 1762445.9]); T46_79 = Transformer.from_crs(4326, 5179, always_xy=True)
def gj(n): return json.load(open(f'{D}/{n}.geojson', encoding='utf-8'))['features']
def rings(f):
    g = f['geometry']; return [g['coordinates']] if g['type'] == 'Polygon' else (g['coordinates'] if g['type'] == 'MultiPolygon' else [])
def lines(f):
    g = f['geometry']; return [g['coordinates']] if g['type'] == 'LineString' else (g['coordinates'] if g['type'] == 'MultiLineString' else [])
def toP(coords):
    a = np.array(coords)[:, :2]; x, y = T46_79.transform(a[:, 0], a[:, 1]); return np.column_stack([x + SHIFT[0], y + SHIFT[1]])
Uc = np.array(P['U']); xmin, ymin = Uc.min(0); xmax, ymax = Uc.max(0); xc = (xmin + xmax) / 2; yc = (ymin + ymax) / 2
f = plt.figure(figsize=(7.2, 9.2), dpi=200); ax = f.add_axes([0, 0, 1, 1]); ax.set_aspect('equal'); ax.axis('off')
pats = [MPoly(toP(pg[0]), closed=True) for ft in gj('parcels') for pg in rings(ft)]; ax.add_collection(PatchCollection(pats, facecolor='#ececec', edgecolor='#ffffff', linewidths=0.35, zorder=1))
segs = [toP(ln) for ft in gj('urban_roads') if '간선' in ft['properties']['cls'] for ln in lines(ft)]; ax.add_collection(LineCollection(segs, colors='#8f8f8f', linewidths=1.5, zorder=2))
segs = [toP(ln) for ft in gj('urban_roads') if '간선' not in ft['properties']['cls'] for ln in lines(ft)]; ax.add_collection(LineCollection(segs, colors='#b5b5b5', linewidths=0.9, zorder=2))
ax.add_patch(MPoly(Uc, closed=True, fc='#f4f4f4', ec='none', zorder=3.5))
for w in P['walks']:
    ax.add_patch(MPoly(np.array(w['outer']), closed=True, fc='#e2e2e2', ec='none', zorder=4))
for r in P['roads']: ax.add_patch(MPoly(np.array(r), closed=True, fc='#6e6e6e', ec='none', zorder=5))
for l in P['lots']:
    pr = prog_of(l['layer'])
    if not pr: continue
    g = Polygon(l['outer']); c = g.representative_point()
    ax.add_patch(MPoly(np.array(l['outer']), closed=True, fc=pr[2], ec='white', lw=1.2, zorder=4.5))
    dark = pr[2] in ('#3A3A3A', '#C8102E', '#8A0A1F', '#B5121B', '#D96D7A', '#9A9A9A')
    ax.text(c.x, c.y, f"{SHORT.get(pr[1], pr[1])}\n{l['area']:,.0f}㎡", ha='center', va='center', fontsize=7.5 if l['area'] < 9500 else 8.5, fontweight='bold', color='white' if dark else INK, zorder=8)
ax.add_patch(MPoly(Uc, closed=True, fc='none', ec=RED, lw=2.0, zorder=6))
ax.set_xlim(xc - 560, xc + 560); ax.set_ylim(yc - 720, yc + 720)
ax.plot([xc - 520, xc - 320], [yc - 690, yc - 690], color=INK, lw=2, zorder=9); ax.text(xc - 420, yc - 680, '200 m', ha='center', va='bottom', fontsize=13, color=INK, zorder=9)
ax.annotate('', xy=(xc + 500, yc + 650), xytext=(xc + 500, yc + 600), arrowprops=dict(arrowstyle='-|>', color=INK, lw=1.2), zorder=9); ax.text(xc + 500, yc + 660, 'N', ha='center', va='bottom', fontsize=11, color=INK, fontweight='bold', zorder=9)
f.savefig('assets/landuse_map.png', facecolor='white'); plt.close(f); print('ok landuse_map')
