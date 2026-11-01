# -*- coding: utf-8 -*-
# 03장 현황 분석 — 그림 제작 스크립트 (발표자료 PDF 잘라내기 + 자산 복사 + 규제 3겹 지도·유산 면적·야간/업종·문제 연쇄 도식)
# 실행: python make_figs_03.py   (venv_plan: pymupdf, PIL, matplotlib, shapely)
import os, json, math, shutil
import numpy as np
import pymupdf
from PIL import Image
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Patch, FancyBboxPatch, FancyArrowPatch
from matplotlib.collections import PatchCollection, LineCollection

R = 'C:/Users/OFFICE/Desktop/9_도시'
REP = R + '/work/20261015_report'
FIG = REP + '/fig'
PDF = 'C:/Users/OFFICE/Desktop/261012_중간마감pt_건축디자인6_b분반_이승규,김민승.pdf'
AS = R + '/work/20261011_midterm_deck/build/assets'
D = R + '/gj-datamap/public/data'
os.makedirs(FIG, exist_ok=True)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
RED = '#c8102e'; DARK = '#8a0a1f'; INK = '#1a1a1a'; G2 = '#d9d9d9'; G3 = '#9a9a9a'; G4 = '#5c5c5c'

# ---------- 1) 발표자료 PDF 잘라내기 (200 dpi) ----------
# 좌표는 pt_pages/pNN.png(2000x1125 px) 기준 픽셀 → pt = px * 0.48
doc = pymupdf.open(PDF)
CROPS = [
    ('03_site_photos', 6, (90, 232, 1095, 1043)),
    ('03_aerial_history', 7, (90, 405, 1912, 1040)),
    ('03_context_aerial', 8, (90, 226, 1065, 717)),
    ('03_asset_distance', 8, (1125, 270, 1910, 860)),
    ('03_field_photos', 9, (90, 232, 1912, 1030)),
    ('03_street_grid_map', 10, (75, 265, 880, 915)),
    ('03_orientation_hist', 10, (1015, 255, 1920, 765)),
    ('03_height_map', 11, (75, 235, 1000, 905)),
    ('03_edge_photos', 11, (1087, 235, 1900, 730)),
    ('03_isovist_points', 12, (75, 265, 925, 910)),
    ('03_isovist_profiles', 12, (1010, 265, 1925, 925)),
    ('03_traffic_weekend', 13, (75, 255, 1900, 910)),
    ('03_northsouth_use', 14, (60, 285, 1860, 880)),
    ('03_ew_footfall', 15, (70, 255, 1900, 895)),
    ('03_pop_change', 16, (70, 255, 1910, 910)),
    ('03_age_ratio', 17, (70, 290, 1910, 830)),
    ('03_youth_netmove', 18, (70, 280, 1910, 850)),
    ('03_tourist_use', 19, (70, 270, 1920, 910)),
    ('03_citizen_needs', 20, (70, 275, 1110, 880)),
    ('03_admin_dispersion', 21, (75, 255, 1925, 905)),
    ('03_regen_diagram', 22, (75, 255, 1925, 885)),
]
SC = 200 / 72.0
for name, pg, (x0, y0, x1, y1) in CROPS:
    page = doc[pg - 1]
    clip = pymupdf.Rect(x0 * 0.48, y0 * 0.48, x1 * 0.48, y1 * 0.48)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(SC, SC), clip=clip)
    pix.save(f'{FIG}/{name}.png')
    print('crop', name, pix.width, pix.height)

# ---------- 2) 자산 복사 ----------
for src, dst in [('rail_axis.png', '03_rail_axis.png'), ('location_base.png', '03_location_map.png'),
                 ('crossing_map.png', '03_crossing_map.png'), ('age_buildings.png', '03_age_map.png')]:
    shutil.copy(f'{AS}/{src}', f'{FIG}/{dst}')
    print('copy', dst)

# ---------- 3) 규제 3겹 지도(범례·비율 표기) ----------
def gj(n):
    return json.load(open(f'{D}/{n}.geojson', encoding='utf-8'))['features']
def rings(f):
    g = f['geometry']
    if g['type'] == 'Polygon': return [g['coordinates']]
    if g['type'] == 'MultiPolygon': return g['coordinates']
    return []
def lines(f):
    g = f['geometry']
    if g['type'] == 'LineString': return [g['coordinates']]
    if g['type'] == 'MultiLineString': return g['coordinates']
    return []
zone = json.load(open(R + '/work/20261011_midterm_deck/build/data/plan_boundary_4326_min.geojson', encoding='utf-8'))['features'][0]['geometry']['coordinates'][0]
lon0 = sum(p[0] for p in zone) / len(zone); lat0 = sum(p[1] for p in zone) / len(zone)
KX = math.cos(math.radians(lat0)) * 111320; KY = 110574
def xy(p): return ((p[0] - lon0) * KX, (p[1] - lat0) * KY)
ZX = [xy(p)[0] for p in zone]; ZY = [xy(p)[1] for p in zone]
xc = (min(ZX) + max(ZX)) / 2; yc = (min(ZY) + max(ZY)) / 2
PARCELS = gj('parcels'); ROADS = gj('urban_roads'); RAILA = gj('rail_abandoned'); RAILX = gj('rail_active'); PARKS = gj('parks_upis')
GODO = gj('godo'); LU = gj('landuse'); RA = gj('reg_areas')
def add_polys(ax, feats, fc, ec, lw, z, alpha=1.0):
    pats = [MPoly([xy(p) for p in pg[0]], closed=True) for f in feats for pg in rings(f)]
    if pats: ax.add_collection(PatchCollection(pats, facecolor=fc, edgecolor=ec, linewidths=lw, zorder=z, alpha=alpha))
def add_lines(ax, feats, color, lw, z, ls='solid'):
    segs = [[xy(p) for p in ln] for f in feats for ln in lines(f)]
    if segs: ax.add_collection(LineCollection(segs, colors=color, linewidths=lw, zorder=z, linestyles=ls, capstyle='round'))
def base(ax, cx, cy, hw, hh):
    add_polys(ax, PARCELS, '#f1f1f1', '#ffffff', 0.3, 1)
    add_lines(ax, [f for f in ROADS if '간선' in f['properties']['cls']], '#8f8f8f', 1.2, 2)
    add_lines(ax, [f for f in ROADS if '간선' not in f['properties']['cls']], '#bdbdbd', 0.7, 2)
    add_lines(ax, RAILA, '#444444', 0.9, 3, ls=(0, (3, 2)))
    ax.set_xlim(cx - hw, cx + hw); ax.set_ylim(cy - hh, cy + hh)
def red_ramp(t):
    t = max(0, min(1, t)); c0 = np.array([255, 255, 255]); c1 = np.array([200, 16, 46]); c2 = np.array([110, 0, 20])
    c = c0 + (c1 - c0) * (t / 0.75) if t < 0.75 else c1 + (c2 - c1) * ((t - 0.75) / 0.25)
    return '#%02x%02x%02x' % tuple(int(x) for x in c)

fig, axes = plt.subplots(1, 3, figsize=(14.9, 7.7), dpi=200)
HW, HH = 480, 690
for ax in axes:
    ax.set_aspect('equal'); ax.axis('off')
# ① 용도지역
ax = axes[0]; base(ax, xc, yc, HW, HH)
lu_col = {'자연녹지지역': '#cfcfcf', '보전녹지지역': '#b5b5b5', '제1종일반주거지역': '#f3c6cc', '제2종일반주거지역': '#e9909c', '일반상업지역': RED}
for f in LU:
    c = lu_col.get(f['properties']['uname'], '#f6f6f6')
    for pg in rings(f): ax.add_patch(MPoly([xy(p) for p in pg[0]], closed=True, fc=c, ec='#ffffff', lw=0.6, zorder=5, alpha=0.92))
ax.add_patch(MPoly([xy(p) for p in zone], closed=True, fc='none', ec=INK, lw=1.8, zorder=8))
ax.set_title('① 용도지역', fontsize=14, fontweight='bold', loc='left')
ax.legend(handles=[Patch(fc='#cfcfcf', ec=G3, label='자연녹지지역 74.7%'), Patch(fc='#e9909c', ec=G3, label='제2종일반주거지역 18.0%'),
                   Patch(fc=RED, ec=G3, label='일반상업지역 7.3%')], loc='upper center', bbox_to_anchor=(0.5, -0.01), fontsize=11, frameon=False, ncol=1)
# ② 고도지구
ax = axes[1]; base(ax, xc, yc, HW, HH)
for f in GODO:
    h = f['properties'].get('h_max')
    try: h = float(h)
    except Exception: h = None
    c = '#f6f6f6' if h is None else red_ramp(max(0, min(1, (36 - h) / 26)) * 0.85)
    for pg in rings(f): ax.add_patch(MPoly([xy(p) for p in pg[0]], closed=True, fc=c, ec='#ffffff', lw=0.6, zorder=5, alpha=0.92))
ax.add_patch(MPoly([xy(p) for p in zone], closed=True, fc='none', ec=INK, lw=1.8, zorder=8))
ax.set_title('② 고도지구', fontsize=14, fontweight='bold', loc='left')
ax.legend(handles=[Patch(fc=red_ramp((36 - 20) / 26 * 0.85), ec=G3, label='도심 20 m 지구 84.5%'), Patch(fc=red_ramp((36 - 15) / 26 * 0.85), ec=G3, label='도심 15 m 지구 12.7%'),
                   Patch(fc='#f6f6f6', ec=G3, label='최저고도지구 3.7% (지구 중첩, 합 101%)')], loc='upper center', bbox_to_anchor=(0.5, -0.01), fontsize=11, frameon=False, ncol=1)
# ③ 역사문화환경 보존지역
ax = axes[2]; base(ax, xc, yc, HW, HH)
for f in RA:
    n = f['properties'].get('reg') or f['properties'].get('name') or ''
    if '국가지정문화유산구역' in n or '문화유산 보호구역' in n: fc, ht = RED, None
    elif '역사문화환경보존지역' in n: fc, ht = '#e9909c', None
    elif '특별보존' in n or '보존육성' in n: fc, ht = '#f3c6cc', '//'
    else: continue
    for pg in rings(f): ax.add_patch(MPoly([xy(p) for p in pg[0]], closed=True, fc=fc, ec='#ffffff', lw=0.5, zorder=5, alpha=0.8, hatch=ht))
ax.add_patch(MPoly([xy(p) for p in zone], closed=True, fc='none', ec=INK, lw=1.8, zorder=8))
ax.set_title('③ 역사문화환경 보존지역', fontsize=14, fontweight='bold', loc='left')
ax.legend(handles=[Patch(fc='#e9909c', ec=G3, label='역사문화환경 보존지역 63.7%'), Patch(fc=RED, ec=G3, label='문화유산 구역·보호구역 (주변 표시)'),
                   Patch(fc='#f3c6cc', ec=G3, hatch='//', label='특별보존·보존육성지구 (근사 경계)')], loc='upper center', bbox_to_anchor=(0.5, -0.01), fontsize=11, frameon=False, ncol=1)
fig.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.12, wspace=0.04)
fig.savefig(f'{FIG}/03_reg_layers.png', facecolor='white'); plt.close(fig); print('ok reg layers')

# ---------- 4) 매장유산 면적 구성 ----------
fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=200)
rows = [('지표조사 범위\n(2022)', [(148770, '#8a8a8a', '148,770')]),
        ('시굴조사 필요\n(유물산포지+사지Ⅱ)', [(104997, RED, '성동동 유물산포지 104,997'), (40882, DARK, '성동동사지Ⅱ 40,882')]),
        ('시굴 1단계(안)', [(43886, '#5c5c5c', '철도공단 43,886'), (14495, '#9a9a9a', '코레일 14,495')]),
        ('기조사\n(2002~2004)', [(3396, '#cfcfcf', '3,396')])]
for i, (lab, segs) in enumerate(rows[::-1]):
    left = 0
    for v, c, t in segs:
        ax.barh(i, v, left=left, color=c, edgecolor='white', height=0.58)
        txtc = 'white' if c in (RED, DARK, '#5c5c5c', '#8a8a8a') else INK
        if v > 30000: ax.text(left + v / 2, i, t, ha='center', va='center', color=txtc, fontsize=9)
        elif v > 10000: ax.text(left + v / 2, i - 0.42, t, ha='center', va='center', color=INK, fontsize=8.5)
        else: ax.text(left + v + 2500, i, t, ha='left', va='center', color=INK, fontsize=9)
        left += v
    ax.text(left + 2500 if segs[-1][0] > 10000 else left + 22000, i, f'합 {left:,}㎡', ha='left', va='center', color=INK, fontsize=9.5, fontweight='bold')
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=10)
ax.set_xlim(0, 200000); ax.set_xlabel('면적 (㎡)', fontsize=9.5)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{int(v):,}'))
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.tick_params(axis='x', labelsize=9)
fig.tight_layout(); fig.savefig(f'{FIG}/03_heritage_areas.png', facecolor='white'); plt.close(fig); print('ok heritage areas')

# ---------- 5) 야간 활동·업종 변화 (3 패널) ----------
fig, axs = plt.subplots(1, 3, figsize=(14.9, 4.9), dpi=200, gridspec_kw={'width_ratios': [1.25, 0.9, 1.1]})
# (a) 시간대별 비중
ax = axs[0]
zn = ['폐역 구역', '행복황촌', '황오동 원도심', '성동시장 200 m', '황리단길 300 m', '시청 500 m']
ev = [19.5, 23.1, 21.4, 21.2, 21.0, 27.2]; nt = [3.7, 4.4, 4.9, 5.0, 5.5, 6.1]
y = np.arange(len(zn))[::-1]
ax.barh(y + 0.19, ev, height=0.36, color='#9a9a9a', label='18~23시')
ax.barh(y - 0.19, nt, height=0.36, color=RED, label='23~05시')
for yy, a, b in zip(y, ev, nt):
    ax.text(a + 0.4, yy + 0.19, f'{a:.1f}', va='center', fontsize=8.5, color=G4); ax.text(b + 0.4, yy - 0.19, f'{b:.1f}', va='center', fontsize=8.5, color=RED)
ax.set_yticks(y); ax.set_yticklabels(zn, fontsize=10.5); ax.set_xlim(0, 32)
ax.set_title('시간대별 추정 유동 비중 (%)', fontsize=12, fontweight='bold', loc='left'); ax.legend(fontsize=10, frameon=False, loc='lower right')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
# (b) 행복황촌 업종
ax = axs[1]
x = np.arange(2); w = 0.34
ax.bar(x - w / 2, [15, 22], w, color='#9a9a9a', label='2025.06'); ax.bar(x + w / 2, [15, 29], w, color=RED, label='2026.06')
for xi, a, b in zip(x, [15, 22], [15, 29]):
    ax.text(xi - w / 2, a + 0.6, str(a), ha='center', fontsize=9.5); ax.text(xi + w / 2, b + 0.6, str(b), ha='center', fontsize=9.5, color=RED)
ax.set_xticks(x); ax.set_xticklabels(['생활 업종', '관광·체류 업종'], fontsize=11); ax.set_ylim(0, 34)
ax.set_title('행복황촌 11개 업종 표본 업소 수', fontsize=12, fontweight='bold', loc='left'); ax.legend(fontsize=10, frameon=False, loc='upper left')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
# (c) 황오동 점포형 업종군 순증감
ax = axs[2]
cats = ['숙박·체류', '생활서비스·의료', '카페·휴게음식', '음식점·제과', '유흥·오락', '생활소매·식품제조']; vals = [5, 1, 0, -1, -2, -9]
yy = np.arange(len(cats))[::-1]
ax.barh(yy, vals, color=[RED if v > 0 else ('#9a9a9a' if v == 0 else '#5c5c5c') for v in vals], height=0.6)
for a, v in zip(yy, vals): ax.text(v + (0.4 if v >= 0 else -0.4), a, f'{v:+d}', va='center', ha='left' if v >= 0 else 'right', fontsize=9.5)
ax.axvline(0, color=INK, lw=0.8); ax.set_yticks(yy); ax.set_yticklabels(cats, fontsize=10.5); ax.set_xlim(-12, 8)
ax.set_title('황오동 점포형 업종군 순증감 (2024 인허가, 건)', fontsize=12, fontweight='bold', loc='left')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f'{FIG}/03_night_industry.png', facecolor='white'); plt.close(fig); print('ok night industry')

# ---------- 6) 문제의 연쇄와 계획 목표 도식 ----------
fig = plt.figure(figsize=(14.9, 6.6), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 144); ax.set_ylim(0, 64); ax.axis('off')
def box(x, y, w, h, t, fc='white', ec=INK, tc=INK, fs=12, lw=1.2, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.0,rounding_size=1.0', fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=fs, color=tc, fontweight='bold' if bold else 'normal', linespacing=1.45)
def arrow(x0, x1, y):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle='-|>', mutation_scale=14, color=G4, lw=1.4))
rows = [
    ('철도 장벽\n(1936~)', '경계공백지대\n(폐역 이후 유휴 부지)', '동서 활력 격차\n① 동서 단절 · ② 남북 불균형', '목표 ①  연결'),
    ('남측 관광 집중', '짧은 체류 · 차량 도착\n④', '생활 업종 치환 위험\n⑤', '목표 ②  문화·유적과 체류'),
    ('외연 확장 · 시청 이전 등\n(요인의 하나)', '원도심 인구·청년 유출\n③', '주거·야간 공백\n⑤', '목표 ③  주민 생활과 청년 정주'),
]
ys = [46, 29, 12]
xs = [3, 38, 73, 112]; ws = [29, 30, 33, 29]
for (a, b, c, d), y0 in zip(rows, ys):
    box(xs[0], y0, ws[0], 11, a, fc='#f2f2f2'); box(xs[1], y0, ws[1], 11, b); box(xs[2], y0, ws[2], 11, c)
    box(xs[3], y0, ws[3], 11, d, fc=RED, ec=RED, tc='white', bold=True, fs=12.5)
    arrow(xs[0] + ws[0] + 0.5, xs[1] - 0.5, y0 + 5.5); arrow(xs[1] + ws[1] + 0.5, xs[2] - 0.5, y0 + 5.5); arrow(xs[2] + ws[2] + 0.5, xs[3] - 0.5, y0 + 5.5)
ax.text(3, 61, '원인·요인', fontsize=11.5, color=G4, fontweight='bold'); ax.text(38, 61, '현상', fontsize=11.5, color=G4, fontweight='bold')
ax.text(73, 61, '결과', fontsize=11.5, color=G4, fontweight='bold'); ax.text(112, 61, '계획 목표', fontsize=11.5, color=RED, fontweight='bold')
ax.add_patch(plt.Rectangle((3, 1.2), 138, 7.4, fc='#f2f2f2', ec='none'))
ax.text(4.5, 4.9, '설계 조건  ⑥ 유산·규제 제약', fontsize=11, fontweight='bold', va='center', color=INK)
ax.text(40, 4.9, '되돌릴 수 있는 순서로 투자  ·  관광 수익의 주민 환류  ·  연결은 연속성과 최약 지점 통과 폭으로 측정  ·  성공 지표는 인접 건물 출입구 방향', fontsize=10, va='center', color=INK)
fig.savefig(f'{FIG}/03_problem_chain.png', facecolor='white'); plt.close(fig); print('ok chain')
print('done')
