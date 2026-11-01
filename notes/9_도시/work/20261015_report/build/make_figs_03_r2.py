# -*- coding: utf-8 -*-
# 03장 현황 분석 2차 수정 — 그림 제작 (답사 사진 묶음 · 지도 복사/합성 · 본문 수치 차트 · 도식)
# 실행: python make_figs_03_r2.py   (venv_plan: PIL, matplotlib, numpy, pymupdf)
import os, math, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon, FancyBboxPatch, Rectangle, FancyArrowPatch
import pymupdf

R = 'C:/Users/OFFICE/Desktop/9_도시'
REP = R + '/work/20261015_report'
FIG = REP + '/fig'
PH = R + '/경주답사'
FD = 'C:/Users/OFFICE/AppData/Local/Microsoft/Windows/Fonts/'
PDF = 'C:/Users/OFFICE/Desktop/261012_중간마감pt_건축디자인6_b분반_이승규,김민승.pdf'
MA = R + '/work/20261011_midterm_deck/build/assets'
PM = R + '/work/20261008_presentation_front/assets/maps'
for w in ('Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold'):
    fm.fontManager.addfont(FD + 'Pretendard-%s.otf' % w)
plt.rcParams['font.family'] = ['Pretendard', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11
RED = '#C8102E'; DK = '#222222'; G1 = '#3c3c3c'; G2 = '#666666'; G3 = '#9a9a9a'; G4 = '#d6d6d2'; G5 = '#efefec'; SOFT = '#F3F5F8'
DPI = 200


def save(fig, name, **kw):
    p = '%s/%s' % (FIG, name)
    fig.savefig(p, dpi=DPI, facecolor='white', **kw)
    plt.close(fig)
    im = Image.open(p); print('saved', name, im.size)


def clean(ax, left=True, bottom=True):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.spines['left'].set_visible(left); ax.spines['bottom'].set_visible(bottom)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(G3)
    ax.tick_params(colors=G1, length=3)


# =====================================================================
# 1) 답사 사진 묶음 (같은 높이로 맞춘 한 줄, 번호 표시)
# =====================================================================
PHOTOS = sorted(f for f in os.listdir(PH) if f.lower().endswith('.jpg'))
BF = ImageFont.truetype(FD + 'Pretendard-Bold.otf', 56)


def load(i, crop=None):
    im = ImageOps.exif_transpose(Image.open('%s/%s' % (PH, PHOTOS[i]))).convert('RGB')
    if crop:  # (x0,y0,x1,y1) 비율
        w, h = im.size; im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    return im


def tile_crop(im, aspect, focus=0.5):
    """aspect(가로/세로)에 맞춰 가운데(가로)·focus(세로 0=위,1=아래) 기준으로 자른다."""
    w, h = im.size
    if w / h > aspect:      # 가로가 넓음 -> 좌우 자름
        nw = int(h * aspect); x0 = (w - nw) // 2
        return im.crop((x0, 0, x0 + nw, h))
    nh = int(w / aspect); y0 = int((h - nh) * focus)
    return im.crop((0, y0, w, y0 + nh))


def bundle(name, items, aspect=1.333, W=2800, gap=16, marks=True):
    """items: [(사진 번호, 세로 초점)] — 같은 크기의 칸으로 맞춘 한 줄(번호 표시)."""
    n = len(items)
    tw = (W - gap * (n - 1)) // n; th = int(tw / aspect)
    row = Image.new('RGB', (W, th), 'white')
    for k, (i, foc) in enumerate(items):
        im = tile_crop(load(i), aspect, foc).resize((tw, th), Image.LANCZOS)
        x = k * (tw + gap); row.paste(im, (x, 0))
        if marks:
            d = ImageDraw.Draw(row, 'RGBA'); r = 40
            d.ellipse((x + 18, 18, x + 18 + 2 * r, 18 + 2 * r), fill=(20, 20, 20, 215))
            d.text((x + 18 + r, 18 + r - 2), str(k + 1), font=BF, fill='white', anchor='mm')
    p = '%s/%s' % (FIG, name); row.save(p, quality=88)
    print('saved', name, row.size, round(os.path.getsize(p) / 1e6, 2), 'MB')


def photos():
    bundle('03_ph_rail.jpg', [(57, .5), (58, .5), (56, .5)], aspect=1.333)
    bundle('03_ph_remains.jpg', [(55, .45), (59, .5), (63, .55)], aspect=1.333)
    bundle('03_ph_roof.jpg', [(64, .5), (65, .42)], aspect=1.9)
    bundle('03_ph_west.jpg', [(0, .5), (1, .42), (2, .45), (3, .55)], aspect=1.0)
    bundle('03_ph_east.jpg', [(60, .62), (61, .55), (62, .6)], aspect=1.25)
    bundle('03_ph_north.jpg', [(39, .5), (40, .5), (42, .5), (43, .5)], aspect=1.333)
    bundle('03_ph_south.jpg', [(46, .5), (47, .5), (52, .62), (53, .5)], aspect=1.0)
    bundle('03_ph_foreign.jpg', [(22, .5), (23, .5), (25, .5), (36, .5)], aspect=1.333)


# =====================================================================
# 2) 지도·도판 복사/합성
# =====================================================================
def maps():
    shutil.copy(PM + '/m2_oldcore_1km.png', FIG + '/03_m2_oldcore.png')
    shutil.copy(PM + '/m4_walk_barrier.png', FIG + '/03_m4_walk_barrier.png')
    # (a) 그림 3-12 대체: 발표자료 p.11 건물 층수 지도 — 「고시구역」 라벨 제거, 「기존 구역 경계」 표기
    doc = pymupdf.open(PDF); pg = doc[10]
    k = 0.48
    clip = pymupdf.Rect(75 * k, 235 * k, 1000 * k, 913 * k)
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(200 / 72 * 1.0, 200 / 72 * 1.0), clip=clip)
    p = FIG + '/03_height_map_r2.png'; pix.save(p)
    im = Image.open(p).convert('RGB'); sc = im.width / (925)  # 원 픽셀(2000폭 기준) 대비 배율
    # 라벨 위치: 페이지 이미지 픽셀 (478~560, 555~610) → 크롭 좌표
    x0, y0, x1, y1 = [int(v * sc) for v in (470 - 75, 553 - 235, 566 - 75, 612 - 235)]
    # 라벨 주변(폴리곤 내부) 색을 표본으로 채움
    fill = im.getpixel((x0 - 8, y0 - 6))
    d = ImageDraw.Draw(im); d.rectangle((x0, y0, x1, y1), fill=fill)
    f = ImageFont.truetype(FD + 'Pretendard-Medium.otf', int(26 * sc))
    cx = (x0 + x1) // 2; cy = (y0 + y1) // 2
    d.text((cx, cy - int(15 * sc)), '기존 구역', font=f, fill=(46, 90, 130), anchor='mm')
    d.text((cx, cy + int(15 * sc)), '경계', font=f, fill=(46, 90, 130), anchor='mm')
    im.save(p); print('saved 03_height_map_r2.png', im.size, 'fill', fill)

    # (b) 인구 65세 이상 / 20~34세 비율 지도 한 쌍 (midterm assets)
    a = Image.open(MA + '/pop_65.png').convert('RGB'); b = Image.open(MA + '/pop_y2034.png').convert('RGB')
    fig, axs = plt.subplots(1, 2, figsize=(15, 6.7))
    for ax, im, t in zip(axs, (a, b), ('65세 이상 비율(%) · 짙을수록 높음', '20~34세 비율(%) · 짙을수록 낮음')):
        ax.imshow(im); ax.axis('off'); ax.set_title(t, fontsize=14, fontweight='bold', loc='left', color=DK)
    fig.subplots_adjust(left=.005, right=.995, top=.93, bottom=.005, wspace=.02)
    save(fig, '03_pop_age_maps.png')

    # (c) 주말 06시·13시·21시 정체 구간 지도 3장
    ims = [Image.open(MA + '/traffic_%s.png' % h).convert('RGB') for h in ('06', '13', '21')]
    cnt = {'06': 79, '13': 100, '21': 81}
    fig, axs = plt.subplots(1, 3, figsize=(15, 6.9))
    for ax, im, h in zip(axs, ims, ('06', '13', '21')):
        ax.imshow(im); ax.axis('off')
        ax.set_title('%s시 · 정체 도로구간 %d개' % (h, cnt[h]), fontsize=14, fontweight='bold', loc='left', color=DK)
    fig.subplots_adjust(left=.005, right=.995, top=.92, bottom=.07, wspace=.03)
    fig.text(.01, .02, '짙은 붉은 선: 정체(도시부 도로 15 km/h 미만)   연한 붉은 선: 서행(25 km/h 미만)   회색 점선: 폐선 부지 일대', fontsize=11.5, color=G1)
    save(fig, '03_traffic3.png')


# =====================================================================
# 3) 도식·차트 (본문 수치만 사용)
# =====================================================================
def card(ax, x, y, w, h, fc, ec=None, lw=1.0, r=0.02):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=%g' % r, fc=fc, ec=ec or fc, lw=lw))


def fig_frame():
    fig = plt.figure(figsize=(15, 5.3)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 15); ax.set_ylim(-.55, 4.75); ax.axis('off')
    qs = [('1', '이 땅은\n무엇인가', '면적·소유·역사\n물리 조건', '3.2 · 3.3 · 3.5'),
          ('2', '도시 안에서\n어디에 있고\n무엇을 끊는가', '위치·도시조직\n경계·횡단', '3.4 · 3.8–3.11'),
          ('3', '주변 동네는\n어떤 상태인가', '인구·고용·상권\n노후도', '3.14–3.18 · 3.20'),
          ('4', '누가 오고\n얼마나\n머무는가', '교통·유동\n관광 이용', '3.12 · 3.13 · 3.19'),
          ('5', '무엇을 지을 수\n있는가', '규제 4겹\n매장유산', '3.6 · 3.7'),
          ('6', '시민과 행정은\n무엇을\n요구하는가', '생활 요구\n행정 분산', '3.21 · 3.22')]
    w = 2.3; gap = (15 - .2 - 6 * w) / 5
    for i, (n, q, sub, sec) in enumerate(qs):
        x = 0.1 + i * (w + gap)
        card(ax, x, 1.0, w, 3.7, SOFT, G4)
        ax.add_patch(Rectangle((x, 4.52), w, 0.18, fc=RED, ec=RED))
        ax.text(x + 0.2, 4.05, n, fontsize=28, fontweight='extra bold', color=RED, va='center')
        ax.text(x + 0.2, 3.0, q, fontsize=14, fontweight='bold', color=DK, va='center', linespacing=1.4)
        ax.text(x + 0.2, 1.95, sub, fontsize=11.5, color=G2, va='center', linespacing=1.4)
        ax.text(x + 0.2, 1.3, '절 ' + sec, fontsize=11.5, fontweight='semibold', color=G1, va='center')
    labels = ['질문', '자료', '발견', '한계', '계획 함의']
    bw = 2.7; step = (14.8 - bw) / 4
    for i, t in enumerate(labels):
        x = 0.1 + i * step
        ax.add_patch(Polygon([(x, -.12), (x + bw - .25, -.12), (x + bw, .28), (x + bw - .25, .68), (x, .68), (x + .25, .28)],
                             fc=RED if i == 4 else G1, ec='white', lw=2))
        ax.text(x + bw / 2 - .05, .28, t, color='white', fontsize=13.5, fontweight='bold', ha='center', va='center')
    ax.text(.1, -.42, '스케일 구분: S1 대상지 · S2 원도심 1 km · S3 경주시', fontsize=11.5, color=G1, va='center')
    ax.text(14.9, -.42, '종합: 3.23 성과 지표 · 3.24 문제 종합 · 3.25 재생 방향', fontsize=11.5, color=G1, ha='right', va='center')
    save(fig, '03_frame.png')

def fig_area_bars():
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    names = ['시 구상 1단계 범위\n(102필지)', '철도 부지', '본 계획 경계']
    vals = [79438, 148770, 228025]
    cols = [G3, G1, RED]
    y = np.arange(3)[::-1]
    ax.barh(y, vals, color=cols, height=.58)
    for yy, v in zip(y, vals):
        ax.text(v + 4000, yy, '{:,}㎡'.format(v), va='center', fontsize=12.5, fontweight='bold', color=DK)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=11.5)
    ax.set_xlim(0, 285000); ax.set_xticks([0, 100000, 200000]); ax.set_xticklabels(['0', '10만', '20만'], fontsize=11)
    ax.text(0.0, -0.33, '세 기준은 범위가 달라 섞어 쓰지 않음', transform=ax.transAxes, fontsize=11, color=G2)
    clean(ax, left=False)
    fig.tight_layout()
    save(fig, '03_area_bars.png')


def fig_timeline():
    fig = plt.figure(figsize=(15, 3.9)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 15); ax.set_ylim(-2.2, 2.2); ax.axis('off')
    xs = [1.2, 3.6, 5.2, 9.2, 12.0, 13.9]
    ev = [('1918.12', '서악~경주 구간 개업\n첫 역은 사정동', 1), ('1936.12', '현 위치(성동동 일원)로\n이전, 표준궤 개량', -1), ('1939.06', '노선 변경\n현재의 선형 확정', 1),
          ('2010.11', 'KTX 신경주역 개통\n(건천읍)', -1), ('2021.12', '구 경주역 폐역\n동해선 이설', 1), ('2023.12', '신경주역이\n「경주역」으로 개명', -1)]
    ax.plot([.5, 14.6], [0, 0], color=G3, lw=2, zorder=1)
    ax.plot([xs[1], xs[4]], [0, 0], color=RED, lw=8, solid_capstyle='butt', zorder=2)
    for k, (x, (d, t, s_)) in enumerate(zip(xs, ev)):
        ax.plot([x, x], [0, s_ * .62], color=G2, lw=1.2, zorder=1)
        ax.scatter([x], [0], s=110, color='white', edgecolor=RED if 1 <= k <= 4 else G1, lw=2.6, zorder=3)
        ax.text(x, s_ * .72, d, fontsize=15, fontweight='bold', color=RED if d in ('1936.12', '1939.06', '2021.12') else G1, ha='center', va='bottom' if s_ > 0 else 'top')
        ax.text(x, s_ * .72 + (.5 if s_ > 0 else -.5), t, fontsize=12.5, color=DK, ha='center', va='bottom' if s_ > 0 else 'top', linespacing=1.35)
    gaps = [(0, 1, '18년'), (1, 2, '약 2.5년'), (2, 3, '약 71년'), (3, 4, '약 11년'), (4, 5, '2년')]
    for a, b, t in gaps:
        ax.text((xs[a] + xs[b]) / 2, -.2, t, fontsize=11, color=G2, ha='center', va='top')
    ax.text((xs[1] + xs[4]) / 2, .22, '현 위치에서 운영된 기간 1936.12–2021.12 (85년)', fontsize=12.5, fontweight='semibold', color=RED, ha='center', va='bottom')
    save(fig, '03_timeline.png')

def fig_reg_stack():
    fig = plt.figure(figsize=(7.2, 6.6)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 10); ax.set_ylim(0, 11); ax.axis('off')
    ax.text(.3, 10.55, '규제 4겹의 중첩', fontsize=14, fontweight='bold', color=DK, va='center')
    ax.text(.3, 10.0, '+ 신라왕경 특별법 · 세계유산 완충구역 · 고도보존육성지구(확인 대기)', fontsize=10.2, color=G2, va='center')
    layers = [('4', '지구단위계획', '본 계획이 새로\n정하는 층', RED),
              ('3', '역사문화환경 보존지역', '중첩 63.7%\n현상변경 허가 선행', '#8E8E8A'),
              ('2', '고도지구', '20 m 지구 84.5%\n15 m 지구 12.7%', '#6B6B68'),
              ('1', '용도지역', '자연녹지 74.7%\n제2종일반주거 18.0%\n일반상업 7.3%', G1)]
    y0 = 2.75; dy = 1.7; hh = 1.15
    for i, (n, t, sdesc, c) in enumerate(layers[::-1]):
        y = y0 + i * dy
        ax.add_patch(Polygon([(.3, y), (5.7, y), (6.7, y + hh), (1.3, y + hh)], fc=c, ec='white', lw=2.5))
        ax.scatter([1.15], [y + hh / 2], s=330, color='white', zorder=3)
        ax.text(1.15, y + hh / 2 - .02, n, color=DK, fontsize=12, fontweight='bold', ha='center', va='center', zorder=4)
        ax.text(3.75, y + hh / 2, t, color='white', fontsize=12.5, fontweight='bold', ha='center', va='center')
        ax.text(6.95, y + hh / 2, sdesc, fontsize=10.5, color=DK, va='center', linespacing=1.35)
    ax.add_patch(FancyBboxPatch((.3, 1.0), 6.4, .95, boxstyle='round,pad=0,rounding_size=.12', fc=SOFT, ec=RED, lw=2))
    ax.text(3.5, 1.48, '네 겹의 교집합 = 실제 건축 가능 볼륨', fontsize=13, fontweight='bold', color=DK, ha='center', va='center')
    ax.text(3.5, .45, '규제가 허용하지 않는 영역은 감점이 아니라 불가능으로 처리', fontsize=10.8, color=RED, fontweight='semibold', ha='center', va='center')
    save(fig, '03_reg_stack.png')

def fig_reg_bars():
    fig, ax = plt.subplots(figsize=(7.2, 3.6)); ax.set_xlim(0, 101); ax.set_ylim(-.6, 3.0)
    rows = [('용도지역', [('자연녹지', 74.7, G1), ('제2종일반주거', 18.0, G3), ('일반상업', 7.3, G4)]),
            ('고도지구', [('20 m 지구', 84.5, G1), ('15 m 지구', 12.7, G3), ('최저고도', 3.7, G4)]),
            ('역사문화환경\n보존지역', [('중첩', 63.7, RED), ('비중첩', 36.3, G4)])]
    for i, (nm, segs) in enumerate(rows):
        y = 2 - i; x = 0
        for lab, v, c in segs:
            ax.barh(y, v, left=x, color=c, height=.56, edgecolor='white')
            if v > 11:
                ax.text(x + v / 2, y, '%s\n%.1f%%' % (lab, v), ha='center', va='center', fontsize=10.5, fontweight='semibold',
                        color='white' if c in (G1, RED, G3) else DK, linespacing=1.25)
            elif v > 3:
                ax.text(x + v, y + .40, '%s %.1f%%' % (lab, v), ha='right', va='bottom', fontsize=9.8, color=G1)
            x += v
        ax.text(-1.5, y, nm, ha='right', va='center', fontsize=11.5, fontweight='semibold', color=DK, linespacing=1.25)
    ax.text(100, -.55, '고도지구는 지구 중첩으로 합 101%  ·  삼층석탑 보존지역 54.9%(보존지역 중)', fontsize=10, color=G2, ha='right')
    ax.set_xticks([]); ax.set_yticks([]); clean(ax, left=False, bottom=False)
    fig.subplots_adjust(left=.2, right=.99, top=.98, bottom=.04)
    save(fig, '03_reg_bars.png')


def fig_dig_cost():
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.4))
    ax = axs[0]
    ax.bar([0], [3.06], color=G1, width=.55); ax.text(0, 3.06 + 2, '3.06억', ha='center', fontsize=11.5, fontweight='bold')
    ax.bar([1], [80 - 63], bottom=[63], color=RED, width=.55); ax.text(1, 80 + 2, '63~80억', ha='center', fontsize=11.5, fontweight='bold', color=RED)
    ax.set_xticks([0, 1]); ax.set_xticklabels(['시굴', '정밀발굴\n(필요 시·추정)'], fontsize=10.5); ax.set_ylim(0, 95)
    ax.set_title('비용(억 원)', fontsize=12, fontweight='bold', loc='left'); clean(ax)
    ax = axs[1]
    ax.bar([0], [54], color=G1, width=.55); ax.text(0, 54 + 25, '54일', ha='center', fontsize=11.5, fontweight='bold')
    ax.bar([1], [700 - 630], bottom=[630], color=RED, width=.55); ax.text(1, 700 + 25, '630~700일', ha='center', fontsize=11.5, fontweight='bold', color=RED)
    ax.set_xticks([0, 1]); ax.set_xticklabels(['시굴', '정밀발굴\n(필요 시·추정)'], fontsize=10.5); ax.set_ylim(0, 820)
    ax.set_title('현장 기간(일)', fontsize=12, fontweight='bold', loc='left'); clean(ax)
    fig.tight_layout()
    save(fig, '03_dig_cost.png')


def fig_detour():
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    names = ['부지 동서 횡단\n(18개 단면 중앙값)', '황오동 세립 조직', '동천동 회전 격자', '성건동 격자']
    v = [3.5, 1.47, 1.32, 1.24]
    y = np.arange(4)[::-1]
    ax.barh(y, v, color=[RED, G3, G3, G3], height=.58)
    ax.plot([1.5, 5.4], [y[0], y[0]], color=DK, lw=2.2); ax.plot([1.5, 1.5], [y[0] - .14, y[0] + .14], color=DK, lw=2.2); ax.plot([5.4, 5.4], [y[0] - .14, y[0] + .14], color=DK, lw=2.2)
    ax.text(5.55, y[0], '범위 1.5~5.4', fontsize=10.5, va='center', color=G1)
    for yy, vv in zip(y, v):
        ax.text(.1 if yy == y[0] else vv + .08, yy, '%.2f' % vv if yy != y[0] else '3.5', va='center', ha='left',
                fontsize=12.5, fontweight='bold', color='white' if yy == y[0] else DK)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=11); ax.set_xlim(0, 7.2); ax.set_xlabel('우회율 = 도로 경로 ÷ 직선거리', fontsize=10.5, color=G2)
    clean(ax, left=False); fig.tight_layout()
    save(fig, '03_detour.png')


def fig_ew_density():
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.6), gridspec_kw={'width_ratios': [1.5, 1]}, sharey=True)
    names = ['성동시장 200 m', '황리단길 300 m', '황오동 원도심', '시청 500 m', '행복황촌', '폐역 구역']
    dens = [1175, 757, 715, 596, 80, 79]; life = [87.8, 41.4, 73.7, 78.6, 34.1, None]
    y = np.arange(6)[::-1]
    ax = axs[0]
    ax.barh(y, dens, color=[G1, G1, G1, G1, RED, RED], height=.6)
    for yy, d in zip(y, dens):
        ax.text(d + 25, yy, '{:,}'.format(d), va='center', fontsize=11.5, fontweight='bold', color=DK)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=11); ax.set_xlim(0, 1480)
    ax.set_title('추정 유동 밀도(명/ha)', fontsize=11.5, fontweight='bold', loc='left'); clean(ax, left=False)
    ax.set_xticks([0, 500, 1000])
    ax = axs[1]
    for yy, l in zip(y, life):
        if l is None:
            ax.text(2, yy, '집계 제외', va='center', fontsize=10.5, color=G2)
        else:
            ax.barh(yy, l, color=G3 if l < 50 else G4, height=.6, edgecolor=G3, lw=.6)
            ax.text(l + 2, yy, '%.1f' % l, va='center', fontsize=11.5, fontweight='bold', color=DK)
    ax.set_xlim(0, 125); ax.set_title('생활업종 비중(%)', fontsize=11.5, fontweight='bold', loc='left'); clean(ax, left=False)
    ax.set_xticks([0, 50, 100]); ax.tick_params(axis='y', length=0)
    fig.tight_layout(); fig.subplots_adjust(wspace=.08)
    save(fig, '03_ew_density.png')


def fig_pop_trend():
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.6), gridspec_kw={'width_ratios': [1.6, 1]})
    ax = axs[0]
    yrs = ['2015', '2020', '2021', '2025']; v = [27673, 22579, 21724, 18528]
    ax.bar(range(4), v, color=[G3, G3, RED, G1], width=.6)
    for i, vv in enumerate(v):
        ax.text(i, vv + 450, '{:,}'.format(vv), ha='center', fontsize=11, fontweight='bold')
    ax.set_xticks(range(4)); ax.set_xticklabels(yrs, fontsize=11); ax.set_ylim(0, 39000)
    ax.annotate('', xy=(1, 33500), xytext=(0, 33500), arrowprops=dict(arrowstyle='->', color=DK, lw=1.2))
    ax.text(.5, 34400, '−18.4%', ha='center', fontsize=11, fontweight='bold')
    ax.annotate('', xy=(3, 33500), xytext=(1, 33500), arrowprops=dict(arrowstyle='->', color=DK, lw=1.2))
    ax.text(2, 34400, '−17.9%', ha='center', fontsize=11, fontweight='bold')
    ax.text(2, 9000, '폐역\n2021.12', ha='center', fontsize=10, color='white', fontweight='semibold')
    ax.set_title('옛 원도심 4개 동 인구(명)', fontsize=11.5, fontweight='bold', loc='left'); clean(ax); ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax = axs[1]
    ax.bar([0, 1], [59.8, 27.4], color=[RED, G3], width=.55)
    ax.text(0, 59.8 + 2, '−59.8%', ha='center', va='bottom', fontsize=11.5, fontweight='bold', color=RED)
    ax.text(1, 27.4 + 2, '−27.4%', ha='center', va='bottom', fontsize=11.5, fontweight='bold')
    ax.set_ylim(0, 78); ax.set_xticks([0, 1]); ax.set_xticklabels(['옛 원도심\n4개 동', '경주시'], fontsize=10.5)
    ax.set_title('20~39세 감소율\n(2015→2025)', fontsize=11.5, fontweight='bold', loc='left')
    clean(ax); ax.set_yticks([]); ax.spines['left'].set_visible(False)
    fig.tight_layout(); fig.subplots_adjust(wspace=.12)
    save(fig, '03_pop_trend.png')

def fig_youth_age():
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    yrs = [2020, 2021, 2022, 2023, 2024, 2025]
    a = np.array([-975, -791, -922, -637, -789, -429]); b = np.array([-803, -495, -521, -217, -288, 4]); c = np.array([-173, -32, -5, -122, -130, 76])
    tot = a + b + c
    x = np.arange(6)
    neg = np.zeros(6); pos = np.zeros(6)
    for arr, col, lab in ((a, G1, '20~24세'), (b, G3, '25~29세'), (c, RED, '30~34세')):
        bot = np.where(arr < 0, neg, pos)
        ax.bar(x, arr, bottom=bot, color=col, width=.62, label=lab, edgecolor='white', lw=.6)
        neg = np.where(arr < 0, neg + arr, neg); pos = np.where(arr >= 0, pos + arr, pos)
    for xi, t, n in zip(x, tot, neg):
        ax.text(xi, n - 60, '{:,}'.format(t).replace('-', '−'), ha='center', va='top', fontsize=11.5, fontweight='bold', color=DK)
    ax.axhline(0, color=G1, lw=1); ax.set_xticks(x); ax.set_xticklabels(yrs, fontsize=11); ax.set_ylim(-2350, 250); ax.set_yticks([-2000, -1000, 0]); ax.set_yticklabels(['−2,000', '−1,000', '0'], fontsize=10.5)
    ax.legend(loc='lower right', fontsize=10.5, frameon=False, ncol=1)
    ax.set_title('경주시 20~34세 순이동(명, 전입−전출) · 6년 누계 −7,249명', fontsize=11.5, fontweight='bold', loc='left'); clean(ax)
    fig.tight_layout()
    save(fig, '03_youth_age.png')


def fig_move_reason():
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    names = ['주택', '가족', '주거환경', '직업', '교육']; v = [1027, 635, -183, -283, -625]
    y = np.arange(5)[::-1]
    ax.barh(y, v, color=[G1 if t > 0 else RED for t in v], height=.58)
    for yy, t in zip(y, v):
        ax.text(t + (25 if t > 0 else -25), yy, ('+' if t > 0 else '−') + '{:,}'.format(abs(t)), ha='left' if t > 0 else 'right', va='center', fontsize=12, fontweight='bold')
    ax.axvline(0, color=G1, lw=1); ax.set_yticks(y); ax.set_yticklabels(names, fontsize=11.5); ax.set_xlim(-900, 1300)
    ax.set_xticks([]); ax.set_ylim(-.6, 4.9); clean(ax, left=False, bottom=False)
    ax.set_title('2025 경주시 순이동 사유(전 연령, 명)', fontsize=11.5, fontweight='bold', loc='left')
    ax.text(1280, 4.55, '순유입 →', ha='right', fontsize=10.5, color=G1); ax.text(-880, 4.55, '← 순유출', ha='left', fontsize=10.5, color=RED)
    fig.tight_layout()
    save(fig, '03_move_reason.png')


def fig_age_dist():
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    cats = ['10년\n미만', '10~20년', '20~30년', '30~40년', '40년\n이상']; v = [60, 114, 174, 324, 1480]
    ax.bar(range(5), v, color=[G4, G4, G3, G1, RED], width=.64)
    for i, vv in enumerate(v):
        ax.text(i, vv + 35, '{:,}'.format(vv), ha='center', fontsize=11.5, fontweight='bold')
    ax.set_xticks(range(5)); ax.set_xticklabels(cats, fontsize=10.5); ax.set_ylim(0, 1800); ax.set_yticks([])
    ax.text(.02, .93, '필지 2,152 중\n20년 이상 1,978 (91.9%)\n30년 이상 1,804 (83.8%)\n40년 이상 1,480 (68.8%)', transform=ax.transAxes, fontsize=11, va='top', color=DK, linespacing=1.45)
    ax.set_title('필지 내 최고 경과연수 구간별 필지 수', fontsize=11.5, fontweight='bold', loc='left'); clean(ax); ax.spines['left'].set_visible(False)
    fig.tight_layout()
    save(fig, '03_age_dist.png')


def fig_tourist_stay():
    fig, axs = plt.subplots(1, 2, figsize=(15, 3.9), gridspec_kw={'width_ratios': [1, 1]})
    ax = axs[0]
    yrs = [2013, 2014, 2017, 2021, 2024]; v = [60.0, 64.3, 74.6, 84.2, 76.9]
    ax.plot(range(5), v, color=RED, lw=2.8, marker='o', ms=9)
    for i, vv in enumerate(v):
        ax.text(i, vv + 3.2, '%.1f' % vv, ha='center', fontsize=12.5, fontweight='bold')
    ax.set_xticks(range(5)); ax.set_xticklabels(yrs, fontsize=12); ax.set_ylim(40, 95); ax.set_yticks([])
    ax.set_title('경주까지 자가용 이용 비율(%, 내국인 관광실태조사)', fontsize=13, fontweight='bold', loc='left'); clean(ax); ax.spines['left'].set_visible(False)
    ax = axs[1]
    cats = ['1~3시간', '3~6시간', '6~9시간', '24시간 이상']; v = [79.1, 15.0, 3.2, 2.7]
    ax.barh(range(4)[::-1], v, color=[RED, G1, G3, G3], height=.58)
    for yy, vv in zip(range(4)[::-1], v):
        ax.text(vv + 1.5, yy, '%.1f%%' % vv, va='center', fontsize=12.5, fontweight='bold')
    ax.set_yticks(range(4)[::-1]); ax.set_yticklabels(cats, fontsize=12); ax.set_xlim(0, 100); ax.set_xticks([])
    ax.set_title('황오동 현장 방문객 체류시간(n=187, 축제 현장 표본)', fontsize=13, fontweight='bold', loc='left'); clean(ax, left=False, bottom=False)
    fig.tight_layout(); fig.subplots_adjust(wspace=.2)
    save(fig, '03_tourist_stay.png')


def fig_minbak():
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    cats = ['2020.12', '2022.12', '2023.12', '2024.12', '2025.10', '2026.06', '2026.09']
    mb = [1, 2, 3, 13, 21, 27, 33]; hn = [1, 2, 2, 3, 3, 3, 3]
    ax.bar(range(7), mb, color=[G3] * 3 + [G1] * 1 + [RED] * 3, width=.62)
    for i, v in enumerate(mb):
        ax.text(i, v + .8, str(v), ha='center', fontsize=12, fontweight='bold')
    ax.plot(range(7), hn, color=DK, lw=1.6, marker='s', ms=5, ls='--', label='한옥체험업')
    ax.set_xticks(range(7)); ax.set_xticklabels(cats, fontsize=10.2); ax.set_ylim(0, 40); ax.set_yticks([])
    ax.legend(handles=[Rectangle((0, 0), 1, 1, fc=RED, label='도시민박업(영업 중, 월말 재고)'), plt.Line2D([0], [0], color=DK, lw=1.6, ls='--', marker='s', ms=5, label='한옥체험업')],
              loc='upper left', fontsize=10.5, frameon=False)
    ax.set_title('행복황촌 구역 외국인관광 숙박업(곳)', fontsize=11.5, fontweight='bold', loc='left'); clean(ax); ax.spines['left'].set_visible(False)
    fig.tight_layout()
    save(fig, '03_minbak.png')


def fig_quadrant():
    fig, ax = plt.subplots(figsize=(7.2, 5.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    Q = [(5, 5, '방문↑ 정주↑', '회복', '#fbeaec', RED), (0, 5, '방문↓ 정주↑', '생활권 유지', SOFT, G1),
         (5, 0, '방문↑ 정주↓', '치환(방문 지표만 오름)', '#f3d2d6', RED), (0, 0, '방문↓ 정주↓', '쇠퇴', G5, G1)]
    for x, y, a, b, fc, tc in Q:
        ax.add_patch(Rectangle((x + .05, y + .05), 4.9, 4.9, fc=fc, ec='white', lw=3))
        ax.text(x + 2.5, y + 3.6, a, ha='center', fontsize=12, color=G2, fontweight='semibold')
        ax.text(x + 2.5, y + 2.6, b, ha='center', fontsize=14.5, color=tc, fontweight='bold')
    ax.annotate('', xy=(9.9, 0.0), xytext=(0.1, 0.0), arrowprops=dict(arrowstyle='->', color=DK, lw=1.4))
    ax.annotate('', xy=(0.0, 9.9), xytext=(0.0, 0.1), arrowprops=dict(arrowstyle='->', color=DK, lw=1.4))
    ax.text(5, -.7, '방문 축: 체류시간 · 숙박 비율 · 소비', ha='center', fontsize=11.5, fontweight='semibold')
    ax.text(-.45, 5, '정주 축: 거주 인구 · 생활업종 · 야간 활동', rotation=90, va='center', fontsize=11.5, fontweight='semibold')
    ax.scatter([6.0], [1.5], s=140, color=RED, zorder=4)
    ax.text(6.3, 1.5, '황남동 — 관광 활발 · 인구 −44.8%', ha='left', va='center', fontsize=10, color=DK)
    ax.text(5, 10.35, '성과 지표의 두 축 — 위치는 정성적 표시', ha='center', fontsize=11, color=G2)
    save(fig, '03_quadrant.png', bbox_inches='tight', pad_inches=.1)


if __name__ == '__main__':
    import sys
    which = sys.argv[1:] or ['photos', 'maps', 'charts']
    if 'photos' in which: photos()
    if 'maps' in which: maps()
    if 'charts' in which:
        for f in (fig_frame, fig_area_bars, fig_timeline, fig_reg_stack, fig_reg_bars, fig_dig_cost, fig_detour, fig_ew_density, fig_pop_trend,
                  fig_youth_age, fig_move_reason, fig_age_dist, fig_tourist_stay, fig_minbak, fig_quadrant):
            f()
