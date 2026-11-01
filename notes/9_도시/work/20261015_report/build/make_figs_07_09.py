# -*- coding: utf-8 -*-
# 07·08·09장 2차 수정 — 그림 제작 스크립트
#  - 07장: 본문 수치로 만든 차트·도식 + 발표자료 p.51 잘라내기
#  - 08장: 최종 마스터플랜 조감·도면의 확대 잘라내기 + 차트
#  - 09장: 단계·선례·성과 지표 도식, 현장 답사 사진 묶음
# 실행: python make_figs_07_09.py [07|08|09]   (venv_plan: pymupdf, PIL, matplotlib, shapely)
# 규칙: 흰 바탕, 붉은색 #C8102E + 회색 계열, 글자 10.5 pt 이상(1:1 표시 기준: wide 15 in = 380 mm, col 7.2 in = 183 mm).
import os, sys, glob, math
import numpy as np
import pymupdf
from PIL import Image, ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Polygon as MPoly, Rectangle, FancyArrowPatch, Circle

R = 'C:/Users/OFFICE/Desktop/9_도시'
REP = R + '/work/20261015_report'
FIG = REP + '/fig'
PDF = 'C:/Users/OFFICE/Desktop/261012_중간마감pt_건축디자인6_b분반_이승규,김민승.pdf'
ROUGH = R + '/work/20261011_masterplan_rough'
PHOTO = R + '/경주답사'
FD = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\Fonts')
for w in ('Regular', 'Medium', 'SemiBold', 'Bold'):
    fm.fontManager.addfont('%s/Pretendard-%s.otf' % (FD, w))
plt.rcParams.update({'font.family': 'Pretendard', 'axes.unicode_minus': False, 'font.size': 11,
                     'axes.edgecolor': '#888888', 'axes.linewidth': 0.8, 'xtick.color': '#444444', 'ytick.color': '#444444'})

RED = '#C8102E'; DRED = '#8c0b20'; PINK = '#E7909C'; LPINK = '#F3CBD1'
INK = '#222222'; G1 = '#3c3c3c'; G2 = '#7a7a7a'; G3 = '#b5b5b5'; G4 = '#e3e3e3'
GROUP = [('북측 공공', G1), ('정주·스포츠·편의', RED), ('생활·문화', PINK), ('창작·체험', G2), ('역사문화·관광', G3)]
GC = dict(GROUP)


def fmt(v, d=0):
    return format(v, ',.%df' % d)


def save(fig, name, dpi=200):
    fig.savefig('%s/%s.png' % (FIG, name), dpi=dpi, facecolor='white')
    plt.close(fig)
    im = Image.open('%s/%s.png' % (FIG, name))
    print('saved', name, im.size)


def clean(ax, left=True, bottom=True, grid=None):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    if not left: ax.spines['left'].set_visible(False)
    if not bottom: ax.spines['bottom'].set_visible(False)
    ax.tick_params(length=0)
    if grid == 'y': ax.yaxis.grid(True, color='#e8e8e8', lw=0.7); ax.set_axisbelow(True)
    if grid == 'x': ax.xaxis.grid(True, color='#e8e8e8', lw=0.7); ax.set_axisbelow(True)


# ───────────────────────── 07장 ─────────────────────────
def f07_flow():
    fig = plt.figure(figsize=(15, 3.85))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 150); ax.set_ylim(-1.5, 37); ax.axis('off')
    steps = [('1', '이용 규모 확정', ['정원 · 세대 수', '회차 × 이용률'], ['청사 1,000석', '주거 256세대', '체험 190명/회']),
             ('2', '단위 면적 적용', ['석 · 세대 · 면당', '면적 원단위'], ['8㎡/석', '전용 22~58㎡', '32㎡/면']),
             ('3', '시설별 면적 합산', ['실별 면적', '+ 공용 · 지원 · 설비'], ['청사 26,500㎡', '주거 19,200㎡', '주차장동 32,160㎡']),
             ('4', '동 · 층수 배분', ['층별 바닥면적', '× 층수 × 동 수'], ['주거 480㎡', '× 4개 층 × 8동', '= 15,360㎡']),
             ('5', '모델 대조', ['라이노 모델', '측정 연면적'], ['목표 105,560㎡', '모델 176,661㎡', '차이 +67.4%'])]
    w = 28.0; gap = 2.4; x0 = 1.5
    for i, (n, t, inp, out) in enumerate(steps):
        x = x0 + i * (w + gap); y0, h = 28.0, 8.0
        col = RED if i == 4 else G1
        pts = [(x, y0), (x + w - 3, y0), (x + w, y0 + h / 2), (x + w - 3, y0 + h), (x, y0 + h)]
        if i > 0: pts.append((x + 3, y0 + h / 2))
        ax.add_patch(MPoly(pts, closed=True, fc=col, ec='none'))
        ax.text(x + (5.2 if i > 0 else 3.0), y0 + h / 2, n, color='white', fontsize=17, fontweight='bold', va='center')
        ax.text(x + (9.6 if i > 0 else 7.4), y0 + h / 2, t, color='white', fontsize=12.5, fontweight='bold', va='center')
        ax.text(x + 1.0, 24.6, '입력', color=G2, fontsize=10.5, va='center')
        for j, s in enumerate(inp):
            ax.text(x + 1.0, 21.2 - j * 3.3, s, color=INK, fontsize=11.5, va='center')
        ax.plot([x + 1.0, x + w - 3.5], [14.0, 14.0], color=G3, lw=0.8)
        ax.text(x + 1.0, 11.8, '적용 · 결과 예', color=G2, fontsize=10.5, va='center')
        for j, s in enumerate(out):
            ax.text(x + 1.0, 8.2 - j * 3.4, s, color=RED if i == 4 else INK, fontsize=12.5, fontweight='bold', va='center')
    save(fig, '07_flow_steps')


def f07_groups():
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.5), gridspec_kw={'width_ratios': [3, 5, 5], 'wspace': 0.16})
    fig.subplots_adjust(left=0.035, right=0.995, top=0.80, bottom=0.24)
    specs = [
        ('근로 · 활동', '1,100명 + 20명', ['청사\n업무석(석)', '기관 활동\n(명, 약)', '작가 입주\n(명, 별도)'], [1000, 100, 20], [G1, G1, G3], 0),
        ('정주', '464명 + 20명', ['22㎡', '33㎡', '44㎡', '58㎡', '작가 숙소\n(별도)'], [64.0, 83.2, 220.8, 96.0, 20], [RED, RED, RED, RED, G3], 1),
        ('방문 (체험수업 8실)', '190명/회', ['도자', '금속', '목공', '섬유', '한지·탁본'], [50, 30, 30, 40, 40], [G2] * 5, 0)]
    for ax, (h1, h2, labs, vals, cols, dec) in zip(axs, specs):
        ax.bar(range(len(vals)), vals, color=cols, width=0.62)
        ax.set_xticks(range(len(vals))); ax.set_xticklabels(labs, fontsize=11)
        ax.set_yticks([]); clean(ax, left=False)
        top = max(vals)
        for i, v in enumerate(vals):
            ax.text(i, v + top * 0.03, fmt(v, 1 if (isinstance(v, float) and v != int(v)) or (dec and i < 4) else 0), ha='center', va='bottom', fontsize=12, fontweight='bold', color=INK)
        ax.set_ylim(0, top * 1.16)
        ax.set_title('%s   %s' % (h1, h2), loc='left', fontsize=13, fontweight='bold', color=INK, pad=12)
    fig.text(0.035, 0.03, '세 값은 단위(석·명·명/회)가 달라 하나의 총인구로 합산하지 않습니다.', fontsize=11, color=G1)
    save(fig, '07_population_groups')


def f07_office():
    items = [('행정 업무 (1,000석 × 8㎡)', 8000), ('공용·설비', 6000), ('회의·전산·행정지원', 3000), ('시의회', 3000),
             ('기록·재난·시민행정 지원', 3000), ('민원·상담', 2000), ('직원 편의', 1500)]
    fig, ax = plt.subplots(figsize=(7.2, 3.7)); fig.subplots_adjust(left=0.40, right=0.97, top=0.88, bottom=0.04)
    ys = np.arange(len(items))[::-1]
    for y, (n, v) in zip(ys, items):
        ax.barh(y, v, color=RED if v == 8000 else G2, height=0.64)
        ax.text(v + 150, y, '%s (%.1f%%)' % (fmt(v), v / 26500 * 100), va='center', fontsize=11, color=INK)
    ax.set_yticks(ys); ax.set_yticklabels([n for n, _ in items], fontsize=11)
    ax.set_xlim(0, 12800); ax.set_xticks([]); clean(ax, bottom=False, left=False)
    ax.set_title('청사 연면적 26,500㎡의 구성', loc='left', fontsize=12.5, fontweight='bold', x=-0.64, pad=8)
    save(fig, '07_office_composition', 250)


def f07_housing():
    fig = plt.figure(figsize=(15, 3.9))
    a1 = fig.add_axes([0.04, 0.17, 0.42, 0.62]); a2 = fig.add_axes([0.56, 0.45, 0.43, 0.26])
    types = ['22㎡', '33㎡', '44㎡', '58㎡']; hh = [64, 64, 96, 32]; pp = [64.0, 83.2, 220.8, 96.0]
    a1.bar(range(4), hh, color=RED, width=0.58)
    for i in range(4):
        a1.text(i, hh[i] + 3, '%d세대' % hh[i], ha='center', fontsize=12.5, fontweight='bold')
        a1.text(i, -17, '거주자 %.1f명' % pp[i], ha='center', fontsize=11, color=G1)
    a1.set_xticks(range(4)); a1.set_xticklabels(types, fontsize=12.5); a1.tick_params(axis='x', pad=3)
    a1.set_yticks([]); a1.set_ylim(0, 118); clean(a1, left=False)
    fig.text(0.04, 0.92, '전용 유형별 세대 수 (합계 256세대, 거주자 464.0명)', fontsize=13, fontweight='bold')
    segs = [('전용', 9600, RED), ('복도 · 코어 · 벽체', 5760, G1), ('출입 · 관리 · 설비 (1층)', 2240, G3), ('주민 커뮤니티 (1층)', 1600, PINK)]
    a2.remove(); a2 = fig.add_axes([0.70, 0.17, 0.29, 0.62])
    for k, (n, v, c) in enumerate(segs):
        y = len(segs) - 1 - k
        a2.barh(y, v, color=c, height=0.62)
        a2.text(v + 250, y, '%s (%.1f%%)' % (fmt(v), v / 192), va='center', fontsize=12, fontweight='bold', color=INK)
    a2.set_yticks(range(len(segs))[::-1]); a2.set_yticklabels([n for n, _, _ in segs], fontsize=11.5)
    a2.set_xlim(0, 15500); a2.set_xticks([]); clean(a2, left=False, bottom=False)
    fig.text(0.52, 0.92, '주거 연면적 19,200㎡의 구성 (2~5층 15,360 + 1층 3,840)', fontsize=13, fontweight='bold')
    save(fig, '07_housing_mix')


def f07_program():
    data = [('북측 공공', [('공공청사 · 의회', 26500), ('북측 주차장동', 22560), ('공공기관 클러스터', 2200)]),
            ('정주·스포츠·편의', [('주거 · 1층 주민시설', 19200), ('스포츠 · 생활편의', 5300)]),
            ('생활·문화', [('복합문화시설', 2000), ('건강 · 돌봄센터', 1200), ('도시농업 지원실', 200)]),
            ('창작·체험', [('실내 체험관', 3000), ('공예전시 · 실내마켓', 2700), ('작가 레지던시', 2500), ('작가 교류 · 행사', 300)]),
            ('역사문화·관광', [('남측 공유주차장', 9600), ('박물관 · 수장고 · 기획전시', 5500), ('관광지원센터', 1500), ('기록 · 해석 · 사업화 지원', 1300)])]
    rows = []
    for g, its in data:
        rows.append(('H', g, sum(v for _, v in its)))
        for n, v in its: rows.append(('I', n, v, g))
    fig, ax = plt.subplots(figsize=(15, 6.4)); fig.subplots_adjust(left=0.20, right=0.975, top=0.985, bottom=0.015)
    n = len(rows)
    for i, r in enumerate(rows):
        y = n - 1 - i
        if r[0] == 'H':
            ax.text(-0.012, y, r[1], transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=12.5, fontweight='bold', color=GC[r[1]] if r[1] != '역사문화·관광' else G2)
            ax.text(0.0, y, '소계 %s㎡' % fmt(r[2]), ha='left', va='center', fontsize=12, fontweight='bold', color=GC[r[1]] if r[1] != '역사문화·관광' else G2, transform=ax.get_yaxis_transform())
            ax.plot([0, 30000], [y - 0.5, y - 0.5], color=G4, lw=0.8) if False else None
        else:
            ax.barh(y, r[2], color=GC[r[3]], height=0.66)
            ax.text(-0.012, y, r[1], transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=11.5, color=INK)
            ax.text(r[2] + 250, y, fmt(r[2]), va='center', fontsize=11.5, color=INK)
    ax.set_ylim(-0.7, n - 0.3); ax.set_xlim(0, 30000); ax.set_yticks([]); ax.set_xticks([]); clean(ax, left=False, bottom=False)
    ax.spines['left'].set_visible(False)
    ax.text(29900, 0.2, '프로그램 연면적 105,560㎡\n= 비주차 건물 73,400 + 주차장동 32,160', ha='right', va='bottom', fontsize=12.5, fontweight='bold', color=INK)
    save(fig, '07_program_area')


def f07_parking():
    fig, ax = plt.subplots(figsize=(15, 3.9)); fig.subplots_adjust(left=0.14, right=0.985, top=0.96, bottom=0.12)
    ax.set_xlim(0, 1300); ax.set_ylim(-0.7, 2.7)
    def stack(y, parts, h=0.56):
        left = 0
        for lab, v, c, tc in parts:
            ax.barh(y, v, left=left, color=c, height=h)
            if v < 60:
                ax.text(left + v / 2, y + h / 2 + 0.05, '%s %s' % (lab, fmt(v)), ha='center', va='bottom', fontsize=11, fontweight='bold', color=INK)
            else:
                ax.text(left + v / 2, y, '%s\n%s' % (lab, fmt(v, 1) if v != int(v) else fmt(v)), ha='center', va='center', fontsize=11, fontweight='bold', color=tc)
            left += v
        return left
    e = stack(2, [('직원·입주자', 518.6, G1, 'white'), ('민원·방문', 100.0, G2, 'white'), ('업무용', 30, G3, INK)])
    ax.text(e + 14, 1.93, '합계 648.6대 × 여유율 1.10 = 713.4대 → 공공용 720면', va='center', fontsize=12, fontweight='bold', color=RED)
    stack(1, [('공공청사·기관 (주차장동 705 + 옥외 15)', 720, RED, 'white'), ('관광·상권 공유', 300, PINK, INK), ('주거', 180, G3, INK)])
    ax.text(1200 + 8, 1.0, '합계 1,200면', va='center', fontsize=12, fontweight='bold', color=INK)
    ax.barh(0, 722 - 451, left=451, color=G4, edgecolor=G2, height=0.56, lw=1.0)
    ax.text(586.5, 0, '조례 환산 참고 범위 451~722대', ha='center', va='center', fontsize=11.5, fontweight='bold', color=INK)
    ax.plot([1200, 1200], [-0.45, 1.5], color=INK, lw=1.0, ls=(0, (4, 3)))
    ax.set_yticks([2, 1, 0]); ax.set_yticklabels(['공공용 주차 수요\n(산정식)', '주차 공급\n(설계안)', '법정 부설주차\n(참고 환산)'], fontsize=12)
    ax.set_xlabel('대 · 면', fontsize=11, color=G2, loc='right')
    clean(ax, left=False, grid='x')
    save(fig, '07_parking')


def f07_landuse():
    # 왼쪽: 발표자료 p.46 지도 잘라낸 것(범례·글자 제외), 오른쪽: 도넛
    src = Image.open('%s/07_landuse_map.png' % FIG).convert('RGB')
    mp = src.crop((196, 4, 500, 850))
    arr = np.array(mp).astype(int)
    out = arr.copy()
    for srcc, dst in (((34, 93, 130), G1), ((193, 210, 223), RED), ((225, 231, 234), PINK), ((244, 245, 246), G4)):
        d = np.abs(arr - np.array(srcc)).sum(axis=2)
        m = d < 14
        out[m] = [int(dst[i:i + 2], 16) for i in (1, 3, 5)]
    mp = Image.fromarray(out.astype('uint8'))
    fig = plt.figure(figsize=(15, 5.5))
    a0 = fig.add_axes([0.02, 0.04, 0.22, 0.92]); a0.imshow(mp); a0.axis('off')
    a1 = fig.add_axes([0.27, 0.06, 0.34, 0.88])
    vals = [138089.4, 29671.8, 25257.3, 35003.7]; labs = ['건축 획지 (13개)', '보행축 · 광장', '공원 · 녹지', '차량 가로 · 잔여 공간']
    cols = ['#215e82', '#bfd2de', '#dfe5ea', '#f1f3f5']
    cols = [G1, RED, PINK, G4]
    w, _ = a1.pie(vals, startangle=90, counterclock=False, colors=cols, wedgeprops=dict(width=0.34, edgecolor='white', linewidth=1.5))
    a1.text(0, 0.06, '228,022㎡', ha='center', va='center', fontsize=17, fontweight='bold', color=INK)
    a1.text(0, -0.17, '계획 경계', ha='center', va='center', fontsize=11.5, color=G2)
    a1.set_aspect('equal')
    ax = fig.add_axes([0.64, 0.12, 0.35, 0.78]); ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    for i, (l, v, c) in enumerate(zip(labs, vals, cols)):
        y = 8.6 - i * 2.4
        ax.add_patch(Rectangle((0, y - 0.35), 0.7, 0.7, fc=c, ec=G3, lw=0.6))
        ax.text(1.1, y + 0.3, l, fontsize=12.5, fontweight='bold', va='center')
        ax.text(1.1, y - 0.5, '%s㎡ · %.1f%%' % (fmt(v, 1), v / 228022.2 * 100), fontsize=12, va='center', color=G1)
    save(fig, '07_landuse_combo')


def f07_gap():
    items = [('역사문화·관광', 21422), ('창작·체험', 18805), ('모델 별도 항목', 14806), ('북측 공공', 8197), ('생활·문화', 6211), ('정주·스포츠·편의', 1660)]
    fig, ax = plt.subplots(figsize=(7.2, 3.7)); fig.subplots_adjust(left=0.30, right=0.97, top=0.86, bottom=0.04)
    ys = np.arange(len(items))[::-1]
    for y, (n, v) in zip(ys, items):
        ax.barh(y, v, color=RED if y >= 4 else G2, height=0.64)
        ax.text(v + 400, y, '+%s (%.1f%%)' % (fmt(v), v / 71101 * 100), va='center', fontsize=11, color=INK)
    ax.set_yticks(ys); ax.set_yticklabels([n for n, _ in items], fontsize=11.5)
    ax.set_xlim(0, 36500); ax.set_xticks([]); clean(ax, left=False, bottom=False)
    ax.set_title('모델 측정 − 프로그램 목표 = +71,101㎡ (+67.4%)', loc='left', fontsize=12.5, fontweight='bold', x=-0.48, pad=8)
    save(fig, '07_gap_stack', 250)


def f07_plan_model():
    rows = [('공공청사 · 의회', 26500, 29545), ('공공기관 클러스터', 2200, 12503), ('북측 주차장동', 22560, 17409), ('주거 · 1층 주민시설', 19200, 20160),
            ('스포츠 · 생활편의', 5300, 6000), ('복합문화시설', 2000, 7471), ('건강 · 돌봄센터', 1200, 2141), ('도시농업 지원실', 200, None),
            ('공예전시 · 실내마켓', 2700, 8994), ('작가 교류 · 행사', 300, 2606), ('작가 레지던시', 2500, 7125), ('실내 체험관', 3000, 8581),
            ('박물관·수장·기록 (묶음)', 6800, 22062), ('관광지원센터', 1500, 1260), ('남측 공유주차장', 9600, 16000)]
    fig, ax = plt.subplots(figsize=(15, 6.3)); fig.subplots_adjust(left=0.16, right=0.985, top=0.99, bottom=0.02)
    n = len(rows)
    for i, (nm, p, m) in enumerate(rows):
        y = n - 1 - i
        ax.barh(y + 0.19, p, height=0.34, color=G3)
        ax.text(p + 220, y + 0.19, fmt(p), va='center', fontsize=10.5, color=G1)
        if m is None:
            ax.text(220, y - 0.19, '미식별', va='center', fontsize=10.5, color=RED, fontweight='bold')
        else:
            ax.barh(y - 0.19, m, height=0.34, color=RED)
            ax.text(m + 220, y - 0.19, fmt(m), va='center', fontsize=10.5, color=RED, fontweight='bold')
    ax.set_yticks(range(n)[::-1]); ax.set_yticklabels([r[0] for r in rows], fontsize=11.5)
    ax.set_xlim(0, 32000); ax.set_xticks([]); clean(ax, left=False, bottom=False)
    ax.set_ylim(-0.7, n + 0.9)
    ax.add_patch(Rectangle((300, n + 0.25), 700, 0.4, fc=G3, ec='none')); ax.text(1300, n + 0.45, '프로그램 계획(v13)', va='center', fontsize=11.5)
    ax.add_patch(Rectangle((5200, n + 0.25), 700, 0.4, fc=RED, ec='none')); ax.text(6200, n + 0.45, '라이노 모델 측정(선택 매스 157개)', va='center', fontsize=11.5)
    ax.text(31800, 0.2, '단위 ㎡', ha='right', fontsize=10.5, color=G2)
    save(fig, '07_plan_vs_model')


def f07_alt():
    fig, axs = plt.subplots(1, 4, figsize=(15, 4.1), gridspec_kw={'wspace': 0.30})
    fig.subplots_adjust(left=0.02, right=0.995, top=0.80, bottom=0.28)
    panels = [
        ('체험시설 이용 (건 · 명/일)', ['본 계획\n(공급 용량)\n시나리오 228~608', '수요 기반\n(참고값)\n범위 413~1,782'], [399, 885], [None, None], [RED, G3], 1100, ['399', '885']),
        ('정주 규모 (세대)', ['본 계획\n(배치 기준)', '수요 기반\n(참고값)\n범위 450~750'], [256, 600], [None, None], [RED, G3], 720, ['256', '600']),
        ('청사 연면적 (㎡)', ['본 계획', '법정 상한', '가산 15%\n포함'], [26500, 21110, 24276], [None] * 3, [RED, G3, G3], 31500, ['26,500', '21,110', '24,276']),
        ('주차 (대 · 면)', ['본 계획\n(공급)', '조례 환산\n(참고 범위)'], [1200, 722], [None, 451], [RED, G3], 1450, ['1,200', '451~722'])]
    for ax, (t, labs, vals, bot, cols, top, texts) in zip(axs, panels):
        for i, v in enumerate(vals):
            b0 = bot[i] or 0
            ax.bar(i, v - b0, bottom=b0, color=cols[i], width=0.56)
            ax.text(i, v + top * 0.02, texts[i], ha='center', va='bottom', fontsize=12.5, fontweight='bold', color=INK)
        ax.set_xticks(range(len(vals))); ax.set_xticklabels(labs, fontsize=11)
        ax.set_yticks([]); ax.set_ylim(0, top * 1.1); clean(ax, left=False)
        ax.set_title(t, loc='left', fontsize=12.5, fontweight='bold', pad=12)
    fig.text(0.02, 0.03, '네 패널은 단위가 달라 서로 비교하지 않으며, 참고값은 본 계획의 근거로 쓰지 않았습니다.', fontsize=11, color=G1)
    save(fig, '07_alt_methods')


def f07_adjust_crop():
    doc = pymupdf.open(PDF)
    page = doc[50]
    clip = pymupdf.Rect(60 * 0.48, 262 * 0.48, 1965 * 0.48, 890 * 0.48)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(200 / 72, 200 / 72), clip=clip)
    pix.save('%s/07_adjust_items.png' % FIG)
    print('crop 07_adjust_items', pix.width, pix.height)


def run07():
    f07_flow(); f07_groups(); f07_office(); f07_housing(); f07_program(); f07_parking(); f07_landuse(); f07_gap(); f07_plan_model(); f07_alt(); f07_adjust_crop()


if __name__ == '__main__':
    run07()       # 08·09장은 make_figs_08_09.py
