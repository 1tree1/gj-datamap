# -*- coding: utf-8 -*-
"""남북 단면 띠 다이어그램(STATION+CITY 식): 최종 도로계획의 가구·획지를 남(좌)→북(우)으로 펼쳐 프로그램 높이·보행축·차량 횡단을 보인다."""
import json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from shapely.geometry import Polygon
from diag_palette import *
plt.rcParams['font.family'] = 'Pretendard'; plt.rcParams['axes.unicode_minus'] = False
P = json.load(open('data/road_plan_final_plan.json', encoding='utf-8'))
ys = [p[1] for p in P['U']]; ymin, ymax = min(ys), max(ys)
lots = []
for l in P['lots']:
    pr = prog_of(l['layer'])
    if not pr: continue
    g = Polygon(l['outer']); b = g.bounds; cx = g.centroid.x
    lots.append(dict(name=pr[1], col=pr[2], h=pr[3], y0=b[1], y1=b[3], cx=cx, area=l['area'], fl=pr[5]))
# 동서로 나란한 두 획지(서/동 열)는 같은 y 구간에 겹치므로 두 줄(서열 위·동열 아래)로 그린다
west = [l for l in lots if l['cx'] < 1167388]; east = [l for l in lots if l['cx'] >= 1167388]
f = plt.figure(figsize=(16, 6.2), dpi=200); ax = f.add_axes([0.03, 0.08, 0.94, 0.86])
def merge(lots_):
    out = []
    for l in sorted(lots_, key=lambda l: l['y0']):
        if out and out[-1]['name'] == l['name'] and l['y0'] <= out[-1]['y1'] + 15:
            out[-1]['y1'] = max(out[-1]['y1'], l['y1']); out[-1]['area'] += l['area']
        else: out.append(dict(l))
    return out
def row(lots_, base, lab):
    prev_end = -1e9; k = 0
    for l in merge(lots_):
        y0, y1 = l['y0'] - ymin, l['y1'] - ymin; h = l['h'] if l['h'] > 1 else 1.5
        ax.add_patch(Rectangle((y0, base), y1 - y0, h, fc=l['col'], ec='white', lw=1.5, zorder=3))
        name = SHORT.get(l['name'], l['name']) if l['h'] > 1 else '오픈스페이스'
        xm = (y0 + y1) / 2; est = len(name) * 14
        lift = 0
        if xm - est / 2 < prev_end: lift = 5.5 * (k % 2 + 1)
        if l['h'] <= 1: lift = 26.5   # 오픈스페이스: 이웃 매스·라벨 위로 올려 쓴다
        ax.text(xm, base + h + 1.2 + lift, name, ha='center', va='bottom', fontsize=13.5 if l['h'] > 1 else 12, fontweight='bold' if l['h'] > 1 else 'normal', color=INK if l['h'] > 1 else G4, zorder=5)
        prev_end = xm + est / 2; k += 1
    ax.text(-8, base + 2, lab, ha='right', va='bottom', fontsize=13, fontweight='bold', color=G4)
# 보행·차량 횡단 띠 (y 구간)
bands = [(1761576, 1761616, '동서 선형공원 40m', RED), (1761434, 1761459, '화랑로 연결 · 차량 12m', G4), (1761735, 1761743, '', G2), (1761867, 1761890, '', G2), (1761974, 1761984, '', G2)]
for (a, b, t, c) in bands:
    ax.add_patch(Rectangle((a - ymin, -30), b - a, 60, fc=c, ec='none', alpha=0.25 if c != RED else 0.35, zorder=1))
    if t: ax.text((a + b) / 2 - ymin, 55, t, ha='center', va='bottom', fontsize=13, fontweight='bold', color=c if c == RED else INK, rotation=90, zorder=6)
row(west, 30, '서측 열'); row(east, 0, '동측 열')
# 지반선·보행축
ax.add_patch(Rectangle((0, -3), ymax - ymin, 3, fc=INK, ec='none', zorder=2))
ax.add_patch(FancyArrowPatch((-40, -14), (ymax - ymin + 40, -14), arrowstyle='<|-|>', mutation_scale=18, color=RED, lw=3, zorder=4)); ax.text((ymax - ymin) / 2, -24, '남북 보행축 30m · 폐선 노반 948m', ha='center', va='top', fontsize=15, fontweight='bold', color=RED)
ax.text(-10, -3, 'S  대릉원·황리단길', ha='right', va='top', fontsize=15, fontweight='bold', color=INK); ax.text(ymax - ymin + 10, -3, '북천 · 황성공원  N', ha='left', va='top', fontsize=15, fontweight='bold', color=INK)
ax.set_xlim(-200, ymax - ymin + 200); ax.set_ylim(-40, 95); ax.axis('off')
f.savefig('assets/diag_section_strip.png', facecolor='white'); print('ok section strip', len(west), len(east))
