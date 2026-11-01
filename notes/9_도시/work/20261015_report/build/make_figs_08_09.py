# -*- coding: utf-8 -*-
# 08·09장 2차 수정 — 그림 제작 (make_figs_07_09.py의 공통 설정을 가져다 쓴다)
# 실행: python make_figs_08_09.py [08|09]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_figs_07_09 import *          # noqa  (R, FIG, ROUGH, PHOTO, 색, fmt, save, clean ...)
from PIL import ImageDraw, ImageFont

FIGDIR = FIG
PF = FD + '/Pretendard-SemiBold.otf'
PR = FD + '/Pretendard-Regular.otf'


# ───────────────────────── 08장 ─────────────────────────
def dcrop(name, box, scale=None):
    """fig/08_D*.png 의 부분 확대. box = 2000 px 폭 기준 표시 좌표(x0, y0, x1, y1)"""
    im = Image.open('%s/%s.png' % (FIG, name)).convert('RGB')
    k = im.width / 2000.0
    return im.crop(tuple(int(round(v * k)) for v in box))


def f08_axo_full():
    im = Image.open(ROUGH + '/sheets/prog7a_axo.png').convert('RGB')
    im = im.resize((3000, int(im.height * 3000 / im.width)), Image.LANCZOS)
    im.save('%s/08_axo_full.png' % FIG, optimize=True)
    print('saved 08_axo_full', im.size)


def f08_axo_crops():
    im = Image.open(ROUGH + '/sheets/prog7a_axo.png').convert('RGB')
    k = im.width / 2000.0
    boxes = [(180, 430, 960, 940), (880, 380, 1400, 820), (1110, 330, 1830, 730)]
    titles = ['북측 존 · 공공청사와 청년·신혼 주거 마을', '중앙 존 · 교차광장과 창작·체험 가구', '남측 존 · 구 경주역 어댑티브 리유즈와 관문']
    crops = [im.crop(tuple(int(v * k) for v in b)) for b in boxes]
    ratios = [c.width / c.height for c in crops]
    fig = plt.figure(figsize=(15, 4.6))
    gs = fig.add_gridspec(1, 3, width_ratios=ratios, left=0.005, right=0.995, top=0.90, bottom=0.01, wspace=0.015)
    for i in range(3):
        ax = fig.add_subplot(gs[i]); ax.imshow(crops[i]); ax.axis('off')
        ax.set_title('%d  %s' % (i + 1, titles[i]), loc='left', fontsize=12, fontweight='bold', color=INK, pad=6)
    save(fig, '08_axo_crops')


def f08_zooms():
    # 대지 축·공간구조·도로·획지 도면의 부분 확대 (표시 좌표 = 2000 px 폭 기준)
    for name, src, box in [('08_zoom_D0', '08_D0_site_axes', (440, 370, 1085, 790)),
                           ('08_zoom_D1', '08_D1_spatial_structure', (400, 540, 960, 910)),
                           ('08_zoom_D3', '08_D3_street_plan', (20, 160, 600, 690)),
                           ('08_zoom_D4', '08_D4_plot_plan', (270, 815, 670, 1100)),
                           ('08_zoom_A', '08_D6_section_ns', (715, 335, 1300, 790)),
                           ('08_zoom_B', '08_D7_section_ew', (780, 335, 1420, 790)),
                           ('08_zoom_C', '08_D8_section_diag', (570, 335, 1250, 790))]:
        im = dcrop(src, box)
        im.save('%s/%s.png' % (FIG, name), optimize=True)
        print('saved', name, im.size)


def f08_landuse():
    items = [('문화·관광시설용지', 70221, RED), ('공공시설용지', 27806, G1), ('업무·상업용지', 16779, '#7a7a7a'), ('주거용지', 14045, PINK),
             ('교통시설용지', 9239, G3), ('공원·녹지', 25257, '#7fa579'), ('보행자전용도로·광장', 31778, '#bcd8b4'), ('도로·보도', 32899, '#e3e3e3')]
    fig = plt.figure(figsize=(7.2, 4.6))
    a1 = fig.add_axes([0.0, 0.05, 0.50, 0.90])
    vals = [v for _, v, _ in items]
    a1.pie(vals, startangle=90, counterclock=False, colors=[c for _, _, c in items], wedgeprops=dict(width=0.36, edgecolor='white', linewidth=1.2))
    a1.text(0, 0.07, '228,022㎡', ha='center', va='center', fontsize=14, fontweight='bold', color=INK)
    a1.text(0, -0.15, '계획 구역', ha='center', va='center', fontsize=10.5, color=G2)
    a1.set_aspect('equal')
    ax = fig.add_axes([0.50, 0.04, 0.50, 0.92]); ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    for i, (l, v, c) in enumerate(items):
        y = 9.3 - i * 1.24
        ax.add_patch(Rectangle((0, y - 0.28), 0.55, 0.56, fc=c, ec=G3, lw=0.5))
        ax.text(0.85, y, l, fontsize=10.5, va='center', color=INK)
        ax.text(9.95, y, '%s · %.1f%%' % (fmt(v), v / 228022 * 100), fontsize=10.5, va='center', ha='right', fontweight='bold', color=INK)
    save(fig, '08_landuse_donut', 250)


def f08_lots():
    cbr = [29.1, 88.3, 36.5, 34.2, 45.5, 28.5, 30.1, 48.4, 21.6, 13.9, 13.6, 43.2, 57.7]
    far = [163.1, 350.4, 145.9, 149.2, 206.6, 104.2, 68.5, 185.0, 81.8, 27.7, 27.2, 143.2, 265.3]
    zc = [G1] * 5 + [G2] * 3 + [RED] * 5
    fig, axs = plt.subplots(1, 2, figsize=(15, 4.4), gridspec_kw={'wspace': 0.08})
    fig.subplots_adjust(left=0.03, right=0.995, top=0.82, bottom=0.12)
    for ax, vals, avg, t, top in ((axs[0], cbr, 35.3, '건폐율 (%)', 105), (axs[1], far, 139.4, '용적률 (%)', 420)):
        ax.bar(range(13), vals, color=zc, width=0.62)
        for i, v in enumerate(vals):
            ax.text(i, v + top * 0.015, '%.1f' % v, ha='center', va='bottom', fontsize=10.5, color=INK)
        ax.axhline(avg, color=INK, lw=1.0, ls=(0, (4, 3)))
        ax.set_xticks(range(13)); ax.set_xticklabels([str(i + 1) for i in range(13)], fontsize=11.5)
        ax.set_yticks([]); ax.set_ylim(0, top); clean(ax, left=False)
        ax.set_title('%s   점선 = 획지 기준 합계 %.1f' % (t, avg), loc='left', fontsize=13, fontweight='bold', pad=10)
        ax.set_xlabel('획지 번호', fontsize=10.5, color=G2, loc='right')
    for k, (lab, c) in enumerate((('북측 존 (획지 1~5)', G1), ('중앙 존 (6~8)', G2), ('남측 존 (9~13)', RED))):
        fig.patches.append(Rectangle((0.03 + k * 0.17, 0.925), 0.011, 0.03, transform=fig.transFigure, fc=c, ec='none'))
        fig.text(0.045 + k * 0.17, 0.94, lab, fontsize=11, va='center')
    save(fig, '08_lots_chart')


def f08_function_mix():
    fig = plt.figure(figsize=(15, 5.0))
    a1 = fig.add_axes([0.10, 0.12, 0.34, 0.74]); a2 = fig.add_axes([0.66, 0.12, 0.33, 0.74])
    groups = ['공공행정·업무\n(획지 1·2·5)', '정주·생활SOC\n(획지 3·4·6)', '창작·체험\n(획지 7·8)', '역사·문화·관광\n(획지 9~12)', '교통·모빌리티\n(획지 13)']
    land = [31632, 30818, 28780, 37621, 9239]; gfa = [65473, 40154, 33693, 28611, 24515]
    ls = [v / 138089 * 100 for v in land]; gs = [v / 192447 * 100 for v in gfa]
    ys = np.arange(5)[::-1]
    a1.barh(ys + 0.18, ls, height=0.34, color=G3); a1.barh(ys - 0.18, gs, height=0.34, color=RED)
    for y, l, g in zip(ys, ls, gs):
        a1.text(l + 0.6, y + 0.18, '%.1f' % l, va='center', fontsize=10.5, color=G1)
        a1.text(g + 0.6, y - 0.18, '%.1f' % g, va='center', fontsize=10.5, color=RED, fontweight='bold')
    a1.set_yticks(ys); a1.set_yticklabels(groups, fontsize=11); a1.set_xlim(0, 42); a1.set_ylim(-0.6, 5.0)
    a1.set_xticks([]); clean(a1, left=False, bottom=False)
    a1.add_patch(Rectangle((19, 4.62), 1.2, 0.26, fc=G3, ec='none')); a1.text(21, 4.75, '대지 구성비', va='center', fontsize=10.5)
    a1.add_patch(Rectangle((30, 4.62), 1.2, 0.26, fc=RED, ec='none')); a1.text(32, 4.75, '연면적 구성비', va='center', fontsize=10.5)
    fig.text(0.01, 0.93, '도입기능 5묶음의 대지 · 연면적 구성비 (건축대지 138,089㎡ · 연면적 192,447㎡ 대비, %)', fontsize=12.5, fontweight='bold')
    uses = [('주차·교통', 44036), ('문화·집회', 37737), ('공공청사·업무', 35414), ('판매·근린생활', 23588), ('주거', 21990), ('업무·청년창업', 8881),
            ('창작·공방', 8589), ('생활체육·복지', 8143), ('역사유산', 2806), ('관광·방문자', 1262), ('숙박', 0)]
    ys = np.arange(len(uses))[::-1]
    for y, (n, v) in zip(ys, uses):
        a2.barh(y, v, color=RED if n == '숙박' else G2, height=0.62)
        a2.text(v + 500, y, '%s (%.1f%%)' % (fmt(v), v / 1924.47), va='center', fontsize=10.5, color=RED if n == '숙박' else INK, fontweight='bold' if n == '숙박' else 'normal')
    a2.set_yticks(ys); a2.set_yticklabels([n for n, _ in uses], fontsize=11); a2.set_xlim(0, 60000); a2.set_xticks([]); clean(a2, left=False, bottom=False)
    fig.text(0.58, 0.93, '용도별 지상 연면적 (㎡, 합계 192,447㎡)', fontsize=12.5, fontweight='bold')
    save(fig, '08_function_mix')


def f08_target_final():
    labs = ['북측 공공', '정주·스포츠\n·편의', '생활·문화', '창작·체험', '역사문화·관광', '목표 외 항목']
    tgt = [51260, 24500, 3400, 8500, 17900, 0]; v13 = [59457, 26160, 9611, 27305, 39322, 14806]; fin = [65473, 26960, 13194, 31123, 42208, 13488]
    fig, ax = plt.subplots(figsize=(15, 4.8)); fig.subplots_adjust(left=0.01, right=0.995, top=0.84, bottom=0.14)
    x = np.arange(6); w = 0.26
    ax.bar(x - w, tgt, w, color=G3); ax.bar(x, v13, w, color=G2); ax.bar(x + w, fin, w, color=RED)
    for i in range(6):
        for dx, v, c, b in ((-w, tgt[i], G1, False), (0, v13[i], G1, False), (w, fin[i], RED, True)):
            ax.text(i + dx, v + 900, fmt(v) if v else '미배정', ha='center', va='bottom', fontsize=10.5, color=c, fontweight='bold' if b else 'normal')
    ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=11.5); ax.set_yticks([]); ax.set_ylim(0, 78000); clean(ax, left=False)
    for k, (lab, c) in enumerate((('프로그램 목표 v13  105,560', G3), ('v13 모델 측정  176,661', G2), ('최종 마스터플랜  192,447', RED))):
        fig.patches.append(Rectangle((0.012 + k * 0.2, 0.915), 0.01, 0.04, transform=fig.transFigure, fc=c, ec='none'))
        fig.text(0.027 + k * 0.2, 0.935, lab, fontsize=11.5, va='center', fontweight='bold' if k == 2 else 'normal')
    save(fig, '08_target_final')


def run08():
    f08_axo_full(); f08_axo_crops(); f08_zooms(); f08_landuse(); f08_lots(); f08_function_mix(); f08_target_final()


# ───────────────────────── 09장 ─────────────────────────
def f09_phase_flow():
    fig = plt.figure(figsize=(15, 5.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 150); ax.set_ylim(0, 54); ax.axis('off')
    cols = ['#F3CBD1', PINK, RED, DRED]; tc = [INK, INK, 'white', 'white']
    names = ['1단계', '2단계', '3단계', '4단계']
    kinds = ['연결 · 기반 · 보행', '공공 · 생활 앵커', '문화 · 창작 · 역사', '관문 · 교통 · 상업']
    items = [['보행축 4개 · 외곽 보도', '도로 기반 · 근린공원 3개소', '구 역사 보수', '획지 2·13 지상 임시 주차'],
             ['공공청사 · 부설주차장', '청년·신혼 공공임대주택', '생활체육 · 생활문화·돌봄', '공공업무 · 청년창업지원'],
             ['구 경주역 어댑티브 리유즈', '근대역사관', '실내 체험관 · 레지던시', '전통공예 특화'],
             ['관광지원센터', '관문 가로상가', '공유주차장 · 모빌리티 허브', '숙박 (결정 시)']]
    cond = ['지하 굴착·기초 없는 공종\n성토 2m 미만 등 발굴 유예 조건', '시굴·발굴이 끝난 획지부터\n주택은 동 단위로 나눠 착수', '운영 조직 확정 후 규모 확정\n구 역사 협의', '1~3단계 이용 실적 확인\n민간 제안·민간자본']
    ref = ['구 안동역 1단계 · 우메코지 공원', '부산 분산 삽입 · 전주', '우메코지 철도유산의 프로그램화', '우메코지 민간 제안 · 전용 역']
    irr = ['낮음', '중간', '높음', '높음']
    w = 35.2; gap = 2.4; x0 = 1.0
    for i in range(4):
        x = x0 + i * (w + gap); y0, h = 44.0, 8.5
        pts = [(x, y0), (x + w - 3, y0), (x + w, y0 + h / 2), (x + w - 3, y0 + h), (x, y0 + h)]
        if i > 0: pts.append((x + 3, y0 + h / 2))
        ax.add_patch(MPoly(pts, closed=True, fc=cols[i], ec='none'))
        ax.text(x + (5.0 if i else 2.4), y0 + h / 2, names[i], color=tc[i], fontsize=14, fontweight='bold', va='center')
        ax.text(x + (5.0 if i else 2.4) + 9.4, y0 + h / 2, kinds[i], color=tc[i], fontsize=11.5, fontweight='bold', va='center')
        for j, s in enumerate(items[i]):
            ax.text(x + 1.0, 40.2 - j * 3.6, '· ' + s, fontsize=11.5, color=INK, va='center')
        ax.plot([x + 1, x + w - 3.5], [25.2, 25.2], color=G3, lw=0.8)
        ax.text(x + 1.0, 23.0, '조건 · 의존', fontsize=10.5, color=G2, va='center')
        ax.text(x + 1.0, 18.6, cond[i], fontsize=11, color=INK, va='center', linespacing=1.5)
        ax.text(x + 1.0, 12.4, '참고 선례', fontsize=10.5, color=G2, va='center')
        ax.text(x + 1.0, 9.6, ref[i], fontsize=11, color=INK, va='center')
    # 비가역성 띠
    for i in range(4):
        x = x0 + i * (w + gap)
        ax.add_patch(Rectangle((x, 2.4), w - 3.0, 3.4, fc=cols[i], ec='none'))
        ax.text(x + (w - 3.0) / 2, 4.1, '비가역성  ' + irr[i], ha='center', va='center', fontsize=11, fontweight='bold', color=tc[i])
    ax.text(18.5, 4.4, '', fontsize=1)
    save(fig, '09_phase_flow')


def f09_phase_map():
    gk = os.path.join(ROUGH, 'scripts'); sys.path.insert(0, gk)
    import gkit as G
    plt.rcParams['font.family'] = 'Pretendard'
    import matplotlib.axes as _mpa
    _mpa.Axes.text = G._orig_text                          # gkit 의 최소 글자 보정 해제
    S, LOTS = G.S, G.LOTS
    ph = {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 12: 3, 10: 4, 11: 4, 13: 4}
    pc = {1: '#F3CBD1', 2: PINK, 3: RED, 4: DRED}
    fig = plt.figure(figsize=(7.2, 6.6))
    ax = fig.add_axes([0.0, 0.0, 0.52, 1.0])
    EXT = (-40, 400, 30, 1030)
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect('equal'); ax.axis('off')
    G.context(ax, (*ax.get_xlim(), *ax.get_ylim()), fc='#efefed', ec='#e2e2df')
    for g in S['ROADS'].values(): G.fill(ax, g, fc='#c9c9c9', ec='white', lw=0.3, z=1)
    G.fill(ax, S['WALK'], fc='#F3CBD1', z=1.1); G.fill(ax, S['PATH8'], fc='#F3CBD1', z=1.1)
    for o in S['OPEN']: G.fill(ax, o['g'], fc='#F3CBD1', ec='white', lw=0.3, z=1.1)
    for p in S['PARKS']: G.fill(ax, p['g'], fc='#F3CBD1', ec='white', lw=0.3, z=1.1)
    for l in LOTS:
        c = pc[ph[l['no']]]
        G.fill(ax, l['g'], fc=c, ec='white', lw=0.9, z=1.2)
        if l['no'] in (2, 13):
            G.fill(ax, l['g'], fc='none', ec='#F3CBD1', lw=0.0, z=1.3, hatch='////')
    xs, ys = S['B'].exterior.xy; ax.plot(xs, ys, color=RED, lw=0.9, ls=(0, (4, 2)), zorder=6)
    BU = G.unary_union([b['g'] for b in G.BLD])
    for l in LOTS:
        pt = G.lot_label_pt(l, avoid=BU)
        ax.add_patch(Circle((pt.x, pt.y), 13, fc='white', ec=INK, lw=0.7, zorder=20))
        ax.text(pt.x, pt.y, str(l['no']), fontsize=10.5, ha='center', va='center', fontweight='bold', zorder=21)
    ax.annotate('', xy=(70, 1005), xytext=(70, 960), arrowprops=dict(arrowstyle='-|>', color=INK, lw=1.2))
    ax.text(70, 940, 'N', fontsize=11, ha='center', va='center', fontweight='bold')
    # 오른쪽 설명
    rx = fig.add_axes([0.53, 0.02, 0.47, 0.96]); rx.axis('off'); rx.set_xlim(0, 10); rx.set_ylim(0, 20)
    rows = [('#F3CBD1', '1단계', '연결 · 기반 · 보행', '보행축 4개 · 보도 · 근린공원 3개소\n도로 기반 · 구 역사 보수'),
            (PINK, '2단계', '공공 · 생활 앵커', '획지 1 · 2 · 3 · 4 · 5 · 6'),
            (RED, '3단계', '문화 · 창작 · 역사', '획지 7 · 8 · 9 · 12'),
            (DRED, '4단계', '관문 · 교통 · 상업', '획지 10 · 11 · 13')]
    for i, (c, a, b, d) in enumerate(rows):
        y = 18.3 - i * 3.9
        rx.add_patch(Rectangle((0, y - 0.7), 0.9, 1.4, fc=c, ec=G3, lw=0.5))
        rx.text(1.4, y + 0.55, '%s  %s' % (a, b), fontsize=11.5, fontweight='bold', va='center')
        rx.text(1.4, y - 0.95, d, fontsize=10.5, va='top', color=G1, linespacing=1.4)
    rx.add_patch(Rectangle((0, 2.0), 0.9, 1.4, fc='white', ec=G3, lw=0.5, hatch='////'))
    rx.text(1.4, 2.7, '획지 2 · 13 : 1단계에는\n지상 임시 주차', fontsize=10.5, va='center', color=G1, linespacing=1.4)
    rx.text(0, 0.6, '단계 배분은 정성적 제안 (phasing 미실행)', fontsize=10.5, color=G2, va='center')
    save(fig, '09_phase_map', 250)


def _photo(i):
    fs = sorted(__import__('glob').glob(PHOTO + '/*.jpg'))
    return ImageOps.exif_transpose(Image.open(fs[i])).convert('RGB')


def _photo_grid(name, picks, tile_w=1000, tile_h=750):
    """picks = [(사진 번호, 라벨)] 2열 격자. 라벨은 사진 아래 띠(글자 42 px = 출력 10.5 pt)"""
    f = ImageFont.truetype(PF, 42)
    strip = 70
    cols = 2; rows = (len(picks) + 1) // 2
    W = cols * tile_w + (cols + 1) * 12; H = rows * (tile_h + strip) + (rows + 1) * 12
    sh = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(sh)
    for k, (idx, lab) in enumerate(picks):
        im = _photo(idx)
        im = ImageOps.fit(im, (tile_w, tile_h), method=Image.LANCZOS, centering=(0.5, 0.5))
        x = 12 + (k % cols) * (tile_w + 12); y = 12 + (k // cols) * (tile_h + strip + 12)
        sh.paste(im, (x, y))
        d.rectangle([x, y + tile_h, x + tile_w, y + tile_h + strip], fill=(60, 60, 60))
        d.text((x + 18, y + tile_h + 12), lab, fill='white', font=f)
    sh.save('%s/%s.jpg' % (FIG, name), quality=88)
    print('saved', name, sh.size)


def f09_photos():
    _photo_grid('09_phase1_photos', [(56, '육교 보행로'), (57, '남측 철로 노반'), (58, '북측 철로 노반'), (62, '동측 포장 골목')])
    _photo_grid('09_edge_photos', [(0, '서측 원화로 보행로'), (2, '서측 코너 건물'), (40, '북측 골목'), (61, '동측 도로')])


def f09_precedents():
    fig = plt.figure(figsize=(15, 4.6))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 150); ax.set_ylim(0, 46); ax.axis('off')
    # 1) 안동
    ax.text(1.0, 42.2, '구 안동역', fontsize=13, fontweight='bold', va='center')
    ax.text(14.0, 42.2, '1단계 = 연결 · 기반 · 보행 세 가지', fontsize=11.5, color=G1, va='center')
    parts = [('남북 연결 도로', '왕복 4차로 220 m'), ('지하 공영주차장', '257면'), ('산책로', '790 m')]
    for i, (a, b) in enumerate(parts):
        x = 1.0 + i * 31.0
        ax.add_patch(Rectangle((x, 31.4), 29.0, 8.0, fc=[RED, G1, G2][i], ec='none'))
        ax.text(x + 14.5, 36.9, a, ha='center', va='center', color='white', fontsize=11.5, fontweight='bold')
        ax.text(x + 14.5, 33.5, b, ha='center', va='center', color='white', fontsize=11.5)
    ax.text(96.0, 38.5, '총사업비 407억 원 · 2025-12-26 착공 · 2027 단계적 완공 예정', fontsize=11, va='center', color=G1)
    ax.text(96.0, 34.4, '경주는 매장유산 때문에 지하주차 대신 지상 임시 주차', fontsize=11, va='center', color=RED, fontweight='bold')
    ax.plot([1, 149], [28.2, 28.2], color=G4, lw=1)
    # 2) 우메코지
    ax.text(1.0, 24.6, '교토 우메코지', fontsize=13, fontweight='bold', va='center')
    ax.text(14.0, 24.6, '순서: 공원이 먼저, 민간자본은 13년 뒤', fontsize=11.5, color=G1, va='center')
    yrs = [(1995, '공원 개원'), (2012, '수족관\n(민간 제안)'), (2016, '철도박물관'), (2019, '전용 역')]
    def X(y): return 8.0 + (y - 1995) / (2019 - 1995) * 120.0
    ax.plot([X(1995), X(2019)], [16.6, 16.6], color=G2, lw=2)
    for y, t in yrs:
        ax.add_patch(Circle((X(y), 16.6), 1.0, fc=RED if y == 1995 else G1, ec='white', lw=1, zorder=5))
        ax.text(X(y), 19.6, str(y), ha='center', va='center', fontsize=11.5, fontweight='bold')
        ax.text(X(y), 12.3, t, ha='center', va='center', fontsize=11, linespacing=1.3)
    ax.annotate('', xy=(X(2012), 21.8), xytext=(X(1995), 21.8), arrowprops=dict(arrowstyle='<->', color=RED, lw=1.2))
    ax.text((X(1995) + X(2012)) / 2, 23.2, '13년', color=RED, fontsize=11.5, fontweight='bold', ha='center', va='bottom')
    ax.text(133.0, 16.6, '빌릴 것은 29년의 기간이 아니라 순서', fontsize=11, color=RED, fontweight='bold', va='center', ha='center', wrap=True) if False else None
    ax.plot([1, 149], [7.0, 7.0], color=G4, lw=1)
    # 3) 푸른길
    ax.text(1.0, 3.6, '광주 푸른길', fontsize=13, fontweight='bold', va='center')
    ax.text(26.0, 3.6, '시민운동 조직이 해산하지 않고 상설 법인으로 전환  →  준공 후 운영 조직이 프로그램을 계속 붙임', fontsize=11.5, color=G1, va='center')
    save(fig, '09_precedents')


def f09_two_axes():
    fig = plt.figure(figsize=(15, 5.2))
    ax = fig.add_axes([0.07, 0.10, 0.40, 0.80]); ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.axis('off')
    quad = [((0, 1), '관광이 아닌\n생활권 중심 회복', '#eeeeee', INK), ((1, 1), '정주를 동반한\n회복 후보', LPINK, INK),
            ((0, 0), '쇠퇴', '#d4d4d4', INK), ((1, 0), '치환 경보', RED, 'white')]
    for (qx, qy), t, c, tcol in quad:
        ax.add_patch(Rectangle((qx + 0.02, qy + 0.02), 0.96, 0.96, fc=c, ec='none'))
        ax.text(qx + 0.5, qy + 0.5, t, ha='center', va='center', fontsize=14, fontweight='bold', color=tcol, linespacing=1.4)
    ax.annotate('', xy=(2.0, -0.12), xytext=(0.0, -0.12), arrowprops=dict(arrowstyle='-|>', color=G1, lw=1.4), annotation_clip=False)
    ax.text(1.0, -0.20, 'A축  방문 · 체류  (감소 → 증가)', ha='center', va='top', fontsize=12.5, fontweight='bold')
    ax.annotate('', xy=(-0.06, 2.0), xytext=(-0.06, 0.0), arrowprops=dict(arrowstyle='-|>', color=G1, lw=1.4), annotation_clip=False)
    ax.text(-0.12, 1.0, 'B축  거주 · 생활업종 · 야간활동  (감소 → 증가)', ha='right', va='center', fontsize=12.5, fontweight='bold', rotation=90)
    ax.set_xlim(-0.05, 2.0); ax.set_ylim(-0.1, 2.0)
    # 가운데: 지표
    mx = fig.add_axes([0.51, 0.10, 0.22, 0.80]); mx.axis('off'); mx.set_xlim(0, 10); mx.set_ylim(0, 10)
    mx.text(0, 9.4, 'A축 지표', fontsize=12.5, fontweight='bold', va='center', color=RED)
    for j, s in enumerate(['방문자 수 (S1)', '체험시설 이용 건수 (S1)', '체류시간 · 숙박 연계 (S3)']):
        mx.text(0.2, 8.3 - j * 1.1, '· ' + s, fontsize=11.5, va='center')
    mx.text(0, 4.6, 'B축 지표', fontsize=12.5, fontweight='bold', va='center', color=RED)
    for j, s in enumerate(['거주 인구 · 입주율 (S1 · S2)', '생활업종 비율 · 사업체 · 종사자 (S2)', '야간활동, 18~23시 유동 (S1 · S2)']):
        mx.text(0.2, 3.5 - j * 1.1, '· ' + s, fontsize=11.5, va='center')
    # 오른쪽: 기준값(S2)
    bx = fig.add_axes([0.80, 0.22, 0.19, 0.56])
    cats = ['성동시장\n200m', '황오동\n격자', '황리단길\n300m']; vals = [87.8, 73.7, 41.4]
    bx.bar(range(3), vals, color=[G1, G2, G3], width=0.6)
    for i, v in enumerate(vals): bx.text(i, v + 2.5, '%.1f' % v, ha='center', fontsize=12, fontweight='bold')
    bx.set_xticks(range(3)); bx.set_xticklabels(cats, fontsize=11); bx.set_yticks([]); bx.set_ylim(0, 108); clean(bx, left=False)
    fig.text(0.74, 0.88, '생활업종 비율 (%, S2 현황)', fontsize=12.5, fontweight='bold')
    fig.text(0.74, 0.10, '11개 업종 표본 · 2026-06', fontsize=10.5, color=G2)
    save(fig, '09_two_axes')


def f09_candidates():
    items = [('가로상가\n(획지 8 · 11)', 4973), ('레지던시 거주동 3동\n(획지 8)', 3750), ('소상공인 상생동\n(획지 9)', 2952), ('공방 · 판매동\n(획지 7)', 2499)]
    fig, ax = plt.subplots(figsize=(7.2, 3.7)); fig.subplots_adjust(left=0.38, right=0.97, top=0.82, bottom=0.04)
    ys = np.arange(4)[::-1]
    for y, (n, v) in zip(ys, items):
        ax.barh(y, v, color=G2, height=0.62); ax.text(v + 90, y, fmt(v), va='center', fontsize=11.5, fontweight='bold')
    ax.set_yticks(ys); ax.set_yticklabels([n for n, _ in items], fontsize=11); ax.set_xlim(0, 6600); ax.set_xticks([]); clean(ax, left=False, bottom=False)
    ax.set_title('분산 삽입 후보 합계 14,174㎡ (연면적의 7.4%)', loc='left', fontsize=12.5, fontweight='bold', x=-0.62, pad=10)
    save(fig, '09_candidates', 250)


def run09():
    f09_phase_flow(); f09_phase_map(); f09_photos(); f09_precedents(); f09_two_axes(); f09_candidates()


if __name__ == '__main__':
    which = sys.argv[1:] or ['08', '09']
    if '08' in which: run08()
    if '09' in which: run09()
