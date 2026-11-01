# -*- coding: utf-8 -*-
"""2차 수정 — 00·01·02 도식·차트 (matplotlib). 수치는 본문 표·문장에 있는 값만 쓴다.
실행: python figs_rev2_b.py [이름...]   (이름 생략 시 전부)"""
import os, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon
sys.stdout.reconfigure(encoding='utf-8')

OUT = 'C:/Users/OFFICE/Desktop/9_도시/work/20261015_report/fig/'
FD = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Windows', 'Fonts')
for w in ['Regular', 'Medium', 'SemiBold', 'Bold']:
    fm.fontManager.addfont(FD + '/Pretendard-%s.otf' % w)
plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

RED = '#C8102E'; INK = '#222222'; G1 = '#F3F5F8'; G2 = '#D9D9D6'; G3 = '#9A9A9A'; G4 = '#5C5C5C'; G5 = '#3C3C3C'
PINK = '#E9A3AD'; PINK2 = '#F4D3D8'


def canvas(w, h, xmax=100.0):
    fig = plt.figure(figsize=(w, h), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, xmax); ax.set_ylim(0, xmax * h / w); ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, fc='white', ec=G5, lw=1.4, r=0.6, z=2):
    p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=%s' % r, fc=fc, ec=ec, lw=lw, zorder=z)
    ax.add_patch(p); return p


def txt(ax, x, y, s, size=12, c=INK, w='regular', ha='left', va='center', ls=1.35, z=5, **k):
    return ax.text(x, y, s, fontsize=size, color=c, fontweight=w, ha=ha, va=va, linespacing=ls, zorder=z, **k)


def arrow(ax, x0, y0, x1, y1, c=G4, lw=2.2, ms=16, style='-|>', ls='-', z=3):
    a = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=ms, color=c, lw=lw, linestyle=ls, zorder=z,
                        shrinkA=0, shrinkB=0)
    ax.add_patch(a)


def save(fig, name):
    fig.savefig(OUT + name, dpi=200, facecolor='white'); plt.close(fig); print('saved', name)


# ------------------------------------------------------------------ 00 구성 차트
def f00_composition():
    W, H = 15, 4.4
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    rows = [
        (2.2, '계획대상지 228,022㎡의 구성', [('건축대지', 138089, 60.6, RED, 'w'), ('도로·보행', 64677, 28.4, G4, 'w'), ('공원·녹지', 25257, 11.1, G2, 'k')]),
        (14.6, '지상 연면적 192,447㎡의 기능별 구성', [('공공행정·업무', 65473, 34.0, RED, 'w'), ('정주·생활SOC', 40154, 20.9, '#DE5A6B', 'w'),
                                                  ('창작·체험', 33693, 17.5, G3, 'w'), ('역사·문화·관광', 28611, 14.9, G4, 'w'), ('교통·모빌리티', 24515, 12.7, G5, 'w')]),
    ]
    X0, X1 = 3, 97
    for t0, title, segs in rows:
        txt(ax, X0, T(t0), title, 14, INK, 'bold')
        x = X0; tot = sum(s[2] for s in segs); yb = T(t0 + 9.2)
        for nm, v, p, col, tc in segs:
            w = (X1 - X0) * p / tot
            ax.add_patch(Rectangle((x, yb), w, 7.0, fc=col, ec='white', lw=2.2, zorder=2))
            c = 'white' if tc == 'w' else INK
            txt(ax, x + w / 2, yb + 4.6, nm, 12.5, c, 'bold', 'center')
            txt(ax, x + w / 2, yb + 2.1, '{:,}㎡ · {}%'.format(v, p), 11.5, c, 'regular', 'center')
            x += w
    txt(ax, X0, T(27.4), '출처: [산정] 설계팀 최종 마스터플랜 개발규모 산정표(2026.10.12). 비율은 반올림으로 합계와 차이가 날 수 있음', 10.5, G4)
    save(fig, '00_composition.png')


# ------------------------------------------------------------------ 01 재생 방향·계획 목표·두 축
def f01_goal_axes():
    W, H = 15, 6.45
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    txt(ax, 2, T(2.5), '재생 방향과 네 가지 계획 목표', 14.5, INK, 'bold')
    box(ax, 2, T(14), 56, 9, fc=RED, ec=RED)
    txt(ax, 30, T(9.5), '단절된 원도심을 다시 연결하고, 문화·유적 강점을 체류와 소득으로 이어\n그 소득과 일자리가 주민(특히 청년)에게 남도록 일자리·주거·생활 기반을 함께 갖추는 재생',
        12, 'white', 'semibold', 'center')
    goals = [('01', '동서·남북 생활권 연계 강화', '5·8장'), ('02', '원도심 중심기능 회복', '6·7장'),
             ('03', '지역경제 활성화', '6·9장'), ('04', '청년 정주기반 확충', '6·7·9장')]
    arrow(ax, 30, T(14), 30, T(16.4), c=RED, lw=2.4, ms=14)
    for i, (no, nm, ch) in enumerate(goals):
        top = 16.8 + i * 6.5
        y = T(top + 5.3)
        box(ax, 2, y, 56, 5.3, fc=G1, ec=G3, lw=1.2, r=0.3)
        ax.add_patch(Rectangle((2, y), 6.2, 5.3, fc=G5, ec=G5, zorder=3))
        txt(ax, 5.1, y + 2.65, no, 15, 'white', 'bold', 'center')
        txt(ax, 10, y + 2.65, nm, 14, INK, 'bold')
        txt(ax, 56.5, y + 2.65, '대응 ' + ch, 12, RED, 'semibold', 'right')
    txt(ax, 64, T(2.5), '성과 판단의 두 축', 14.5, INK, 'bold')
    for k, (ttl, items, col) in enumerate([('방문·체류 축', ['방문객', '체류시간'], G5), ('거주·생활 축', ['거주인구', '생활업종 비율', '야간 활동'], RED)]):
        x = 64 + k * 18.6
        box(ax, x, T(33), 17.2, 28, fc='white', ec=col, lw=2.2, r=0.3)
        ax.add_patch(Rectangle((x, T(11)), 17.2, 6, fc=col, ec=col, zorder=3))
        txt(ax, x + 8.6, T(8), ttl, 14, 'white', 'bold', 'center')
        ys = [19, 26] if len(items) == 2 else [17, 22.5, 28]
        for it, yy in zip(items, ys):
            txt(ax, x + 8.6, T(yy), it, 13, INK, 'medium', 'center')
    box(ax, 64, T(42.5), 35.8, 7, fc=PINK2, ec=RED, lw=1.4, r=0.3)
    txt(ax, 81.9, T(39), '관광 업종 증가 + 생활 업종 감소\n= 회복이 아니라 치환일 수 있음', 12.5, INK, 'semibold', 'center')
    save(fig, '01_goal_axes.png')


# ------------------------------------------------------------------ 01 보고서 구성
def f01_report_flow():
    W, H = 15, 4.5
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    groups = [
        ('문제 규정', '1~3장', RED, [('01', '계획의 개요', '배경 · 목적 · 범위\n과업 · 경위'), ('02', '상위·관련계획 검토', '조건과 방향의\n구분'),
                           ('03', '현황 분석', '대상지 · 도시조직 · 교통\n인구 · 규제 → 문제 종합')]),
        ('계획 구상', '4~7장', G5, [('04', '계획 구상', '컨셉 위계 · 전략의\n공간 배치 · 선례'), ('05', '도시축과 도로계획', '도시축 · 도로망\n가구와 획지'),
                           ('06', '프로그램 계획', '네 앵커 · 선정 근거\n세부 프로그램'), ('07', '계획인구와 개발규모', '방문·근로·정주 인구\n→ 면적 · 주차 · 산정표')]),
        ('계획안 제시', '8~9장', RED, [('08', '마스터플랜', '공간구조 · 토지이용 · 획지\n조감 · 단면'), ('09', '실행 및 운영 방향', '단계별 추진 · 운영 주체\n성과 지표')]),
    ]
    cw, gap, x0 = 19.0, 1.2, 19.2
    for r, (gt, rng, col, cards) in enumerate(groups):
        top = 1.8 + r * 9.0
        y = T(top + 8.0)
        ax.add_patch(Rectangle((2, y), 16.0, 8.0, fc=col, ec='none', zorder=3))
        txt(ax, 3.2, y + 5.2, gt, 14, 'white', 'bold')
        txt(ax, 3.2, y + 2.3, rng, 12, 'white', 'medium')
        for i, (no, nm, sub) in enumerate(cards):
            x = x0 + i * (cw + gap)
            box(ax, x, y, cw, 8.0, fc=G1, ec=G3, lw=1.2, r=0.3)
            txt(ax, x + 1.0, y + 6.0, no, 15, RED, 'bold')
            txt(ax, x + 4.4, y + 6.0, nm, 12, INK, 'bold')
            txt(ax, x + 1.0, y + 2.5, sub, 10.6, G4, va='center', ls=1.25)
        if r < 2:
            arrow(ax, 10, y - 0.15, 10, y - 0.95, c=RED, lw=2.6, ms=16)
    save(fig, '01_report_flow.png')


# ------------------------------------------------------------------ 01 과업 일정
def f01_course_flow():
    W, H = 15, 5.0
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    wk = [('2주차', '09/07 · 09/10', '대상지 읽어내기\n관련 계획·법규 분석', '2·3장'),
          ('3~4주차', '09/14 ~ 09/21', '주제·계획 방향\n도입 기능 프로그램', '3장 후반 · 4·6장'),
          ('5주차', '09/28 · 10/01', '마스터플랜 1\n조닝·필지·가로 체계', '5장'),
          ('6주차', '10/08', '마스터플랜 2\n용도·건폐율·용적률\n매싱', '7·8장'),
          ('7주차', '10/12 · 10/15', '마스터플랜 3\n차량 동선·외관\n외부공간', '8장'),
          ('8주차', '10/19', '중간마감\n결정도·가이드라인', '기준 시점은 10/12')]
    n = len(wk); cw = 15.0; g = (96 - n * cw) / (n - 1)
    txt(ax, 2, T(2.0), '건축디자인6 주차별 강의계획과 본 보고서의 대응', 14.5, INK, 'bold')
    for i, (w_, d, body, ch) in enumerate(wk):
        x = 2 + i * (cw + g); last = i == n - 1
        t0, t1 = 4.6, 12.0
        pts = [(x, T(t0)), (x + cw - 1.6, T(t0)), (x + cw + 0.6, T((t0 + t1) / 2)), (x + cw - 1.6, T(t1)), (x, T(t1))]
        ax.add_patch(Polygon(pts, closed=True, fc=RED if last else G5, ec='none', zorder=3))
        txt(ax, x + 1.4, T(7.0), w_, 14.5, 'white', 'bold')
        txt(ax, x + 1.4, T(10.0), d, 11.5, 'white', 'medium')
        box(ax, x, T(23.5), cw, 9.5, fc=G1, ec=G3, lw=1.2, r=0.3)
        txt(ax, x + 1.0, T(18.7), body, 11.3, INK, 'medium')
        box(ax, x, T(30.5), cw, 5.5, fc='white', ec=RED, lw=1.6, r=0.3)
        txt(ax, x + cw / 2, T(27.7), ch, 11.5, RED, 'bold', 'center')
    txt(ax, 2, 1.0, '출처: [과제 요구] 건축디자인6 오리엔테이션(2026.09.03). 보고서의 기준 시점은 발표자료 표지 일자(2026.10.12)입니다.', 10.5, G4)
    save(fig, '01_course_flow.png')


# ------------------------------------------------------------------ 01 연표
def f01_timeline():
    W, H = 15, 6.45
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t

    def row(t0, title, items, col):
        txt(ax, 2, T(t0), title, 14, col, 'bold')
        n = len(items); cw = 96 / n
        for i, (dt, ev) in enumerate(items):
            x = 2 + i * cw
            ya, yb = T(t0 + 3.0), T(t0 + 8.6)
            pts = [(x, ya), (x + cw - 1.2, ya), (x + cw + 0.4, (ya + yb) / 2), (x + cw - 1.2, yb), (x, yb)] + ([(x + 1.6, (ya + yb) / 2)] if i else [])
            ax.add_patch(Polygon(pts, closed=True, fc=col, ec='none', zorder=3))
            txt(ax, x + (2.8 if i else 1.2), (ya + yb) / 2, dt, 12.5, 'white', 'bold')
            txt(ax, x + 0.4, T(t0 + 10.4), ev, 11.3, INK, 'regular', va='top')

    row(2.5, '철도 운영기 (1918~2021)', [
        ('1918.12.28', '서악~경주 구간\n운수 개시 인가\n(경주역 개업, 사정동)'),
        ('1936.12.01', '현 위치(성동동)로\n이전, 울산~경주\n표준궤 개축'),
        ('2010.11.01', 'KTX 신경주역\n개통'),
        ('2013', '구 역사 코레일\n철도기념물 지정\n(지정 근거 확인 대기)'),
        ('2021.11.17', '중앙선 종점 변경\n(경주역 제외)\n고시 제2021-1234호'),
        ('2021.12.28', '동남권 신선\n정식 운행\n= 폐역일')], G5)
    row(23.5, '폐역 이후 (2022~2026)', [
        ('2022.01', '도시재생 전략계획\n(변경) 최종보고서'),
        ('2023.04', '폐철도 기본구상\n최종보고회\n(폐역 17곳 · 80.3 km)'),
        ('2025.07', '원도심 미래구상\n기획 연구'),
        ('2025.12.18', '국가시범지구(혁신지구)\n후보지 선정\n시 구상 공개'),
        ('2025.12.30', '경주시–국가철도\n공단 업무협약\n(MOU)'),
        ('2026.02.06', '2026 상반기 혁신지구\n공모 가이드라인\n배포')], RED)
    txt(ax, 2, 1.2, '※ 축척 없음. 하반기 공모와 경주시 신청 여부는 확인 대기. 출처: 표 1-5·표 1-6의 [T1]~[T2] 자료', 10.5, G4)
    save(fig, '01_timeline.png')


# ------------------------------------------------------------------ 01 NEXUS 흐름
def f01_nexus_flow():
    W, H = 15, 5.7
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    cols = [('유입', '남측', 'CONNECT 접속', G5, ['동서 횡단 가로를 여러 곳에 두어\n횡단 간격을 줄임', '가장 좁은 지점의 통과 폭 확보', '폐선 노반을 남북 보행축으로 사용'],
             '측정 근거 있음\n무횡단 985 m · 육교 1개소(3.2 m)'),
            ('교류', '중앙', 'EXCHANGE 교차·전환', G5, ['구 역사 · 문화광장', '창작 스튜디오 · 체험관', '시장 접점'], '가설\n준공 이후 지표로 확인'),
            ('체류', '북측', 'SPREAD 확산', G5, ['청년 업무 · 청년 주거', '공공청사', '저녁 이후에도 사람이 남는 곳'], '가설\n준공 이후 지표로 확인'),
            ('확산', '부지 밖', '성동시장 · 행복황촌', RED, ['활동을 부지 밖으로 내보내는\n동선과 안내 설계'], '가설\n준공 이후 지표로 확인')]
    cw = 21.8; g = 3.0
    for i, (st, sp, strat, col, items, ev) in enumerate(cols):
        x = 2 + i * (cw + g)
        ax.add_patch(Rectangle((x, T(10.5)), cw, 8.5, fc=col, ec='none', zorder=3))
        txt(ax, x + 1.4, T(5.0), st, 18, 'white', 'bold')
        txt(ax, x + 7.2, T(5.0), sp, 13, 'white', 'medium')
        txt(ax, x + 1.4, T(8.6), strat, 11.5, 'white', 'medium')
        box(ax, x, T(28), cw, 16, fc=G1, ec=G3, lw=1.2, r=0.3)
        yy = 14.4
        for it in items:
            nl = it.count('\n') + 1
            txt(ax, x + 1.3, T(yy), '· ' + it.replace('\n', '\n  '), 11.5, INK, 'regular', va='top')
            yy += 1.0 + 1.75 * nl + 1.2
        box(ax, x, T(36), cw, 6.5, fc='white', ec=RED if i == 0 else G3, lw=1.6 if i == 0 else 1.2, r=0.3)
        txt(ax, x + cw / 2, T(32.8), ev, 10.8, RED if i == 0 else G4, 'semibold', 'center')
        if i < 3:
            arrow(ax, x + cw + 0.2, T(6.2), x + cw + g - 0.2, T(6.2), c=RED, lw=3, ms=20)
    save(fig, '01_nexus_flow.png')


# ------------------------------------------------------------------ 02 규제 면적 비율
def f02_reg_ratio():
    W, H = 15, 5.8
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    lx = 2; bx0 = 34; bw = 54
    rows = [
        ('용도지역', [('자연녹지 74.7%', 74.7, RED, 'w'), ('2종일반주거\n18.0%', 18.0, G4, 'w'), ('일반상업 7.3%', 7.3, G2, 'k')]),
        ('고도지구 — 도심 20 m', [('84.5%', 84.5, RED, 'w')]),
        ('고도지구 — 도심 15 m', [('12.7%', 12.7, RED, 'w')]),
        ('고도지구 — 최저고도', [('3.7%', 3.7, RED, 'w')]),
        ('역사문화환경 보존지역', [('63.7%', 63.7, G5, 'w')]),
        ('중점경관관리구역', [('99.99%', 99.99, G5, 'w')]),
        ('특별보존·보존육성지구(근사)', [('각 0.3%', 0.3, G3, 'k')]),
    ]
    txt(ax, lx, T(2.2), '계획 경계(228,022㎡) 대비 규제 구역의 면적 비율', 14, INK, 'bold')
    for p in (0, 50, 100):
        ax.plot([bx0 + bw * p / 100] * 2, [T(8.2 + 6 * 4.3 + 2.4), T(6.6)], color=G2, lw=0.9, ls=(0, (3, 3)), zorder=1)
        txt(ax, bx0 + bw * p / 100, T(5.4), '%d%%' % p, 10.5, G4, ha='center')
    for i, (nm, segs) in enumerate(rows):
        y = T(9.4 + i * 4.3)
        txt(ax, lx, y, nm, 12.5, INK, 'medium')
        x = bx0
        for lab, v, col, tc in segs:
            w = bw * v / 100
            ax.add_patch(Rectangle((x, y - 1.55), w, 3.1, fc=col, ec='white', lw=1.5, zorder=3))
            if w > 12:
                txt(ax, x + w / 2, y, lab, 11.5, 'white' if tc == 'w' else INK, 'bold', 'center', ls=1.05)
            elif w > 8:
                txt(ax, x + w / 2, y, lab, 10.5, 'white' if tc == 'w' else INK, 'bold', 'center', ls=1.05)
            else:
                txt(ax, x + w + 0.8, y, lab, 12, INK, 'bold')
            x += w
        if i in (0, 3, 5):
            ax.plot([lx, 97], [y - 2.15, y - 2.15], color=G2, lw=1.0, zorder=1)
    txt(ax, 2, 1.0, '고도지구는 지구가 중첩되어 합이 100%를 넘음. 출처: [산정] V-World 폴리곤 × 계획 경계', 10.5, G4)
    save(fig, '02_reg_ratio.png')


# ------------------------------------------------------------------ 02 매장유산 시굴
def f02_excavation():
    W, H = 15, 4.4
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    txt(ax, 2, T(2.4), '지표조사 범위와 시굴 필요 면적 (㎡)', 14, INK, 'bold')
    sx = 2; sw = 44.0; tot = 148770.0

    def bar(t0, segs, label):
        x = sx
        txt(ax, sx, T(t0), label, 12.5, INK, 'medium')
        for nm, v, col, tc in segs:
            w = sw * v / tot
            ax.add_patch(Rectangle((x, T(t0 + 6.2)), w, 4.8, fc=col, ec='white', lw=1.5, zorder=3))
            if w > 12:
                txt(ax, x + w / 2, T(t0 + 3.8), nm, 11.3, 'white' if tc == 'w' else INK, 'bold', 'center', ls=1.15)
            x += w
    bar(6, [('148,770', 148770, G3, 'k')], '철도 용지(지표조사 범위)')
    bar(16, [('성동동 유물산포지\n104,997', 104997, RED, 'w'), ('성동동사지Ⅱ\n40,882', 40882, '#8A0A1F', 'w')], '시굴 필요 145,879 = 철도 용지의 98.1% [산정]')
    txt(ax, 2, T(25.2), '이미 조사된 3,396㎡는 시굴 필요 면적에서 제외', 11, G4)
    ax.plot([51.5, 51.5], [4, T(3)], color=G2, lw=1.2)
    txt(ax, 54, T(2.4), '시굴과 정밀발굴의 현장 일수·비용', 14, INK, 'bold')
    ox, ow, dmax = 54.0, 34.0, 750.0
    for k, (nm, d0, d1, cost) in enumerate([('시굴', 54, 54, '3.06억 원'), ('정밀발굴', 630, 700, '63~80억 원')]):
        t0 = 6 + k * 10
        txt(ax, ox, T(t0), nm, 12.5, INK, 'medium')
        yb = T(t0 + 6.2)
        ax.add_patch(Rectangle((ox, yb), ow * d0 / dmax, 4.8, fc=RED, ec='none', zorder=3))
        if d1 > d0:
            ax.add_patch(Rectangle((ox + ow * d0 / dmax, yb), ow * (d1 - d0) / dmax, 4.8, fc=PINK, ec='none', zorder=3))
        lab = '%d일' % d0 if d0 == d1 else '%d~%d일' % (d0, d1)
        txt(ax, ox + ow * d1 / dmax + 1.0, yb + 2.4, '%s · %s' % (lab, cost), 12, INK, 'bold')
    txt(ax, ox, T(25.2), '현장 일수(일). 시 구상의 사업 기간은 2027.6~2032.6(5년)', 10.5, G4)
    txt(ax, 2, 1.0, '출처: [T2] 김권일 발표자료(2026.02.27), 구)경주역일원 매장유산 시굴조사 추진계획. 지표조사 보고서 원문은 확인 대기', 10.5, G4)
    save(fig, '02_excavation.png')


# ------------------------------------------------------------------ 02 인접 활성화계획과 역할
def f02_role_division():
    W, H = 15, 7.1
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    cards = [
        (2, 30, '서측 경주역전지구', '중심시가지형 · 2018 선정 · 215,000㎡', '총사업비 281.69억 · 마중물 250억', G5,
         ['황오 프론티어 밸리(청년창업거점센터)', '성동시장 오픈 스튜디오', '상생협력상가', '글로벌 어울림 광장', '황오 커뮤니티센터']),
        (35, 30, '본 계획 구역', '228,022㎡ [산정]', '도시재생 활성화지역 밖', RED,
         ['북측 공공청사 · 청년 공공임대주택', '북측 생활체육', '중앙 공공업무·청년창업 · 생활문화', '중앙 전통공예 · 작가 레지던시', '남측 구 경주역 활용 · 관문 가로상가']),
        (68, 30, '동측 행복황촌', '일반근린형 · 2020 선정 · 164,500㎡', '총사업비 254.47억 · 마중물 127.28억', G5,
         ['황촌상권활력소 · 마을활력소', '마을부엌 · 게스트하우스', '황촌나들이길 · 빈집 정비', '양정로 개설 126억(도로 개설)']),
    ]
    for x, w, t1, t2, t3, col, items in cards:
        ax.add_patch(Rectangle((x, T(12)), w, 10, fc=col, ec='none', zorder=3))
        txt(ax, x + 1.4, T(4.4), t1, 15, 'white', 'bold')
        txt(ax, x + 1.4, T(7.5), t2, 11, 'white', 'medium')
        txt(ax, x + 1.4, T(10.2), t3, 11, 'white', 'medium')
        box(ax, x, T(34), w, 21, fc=G1, ec=G3, lw=1.2, r=0.3)
        for j, it in enumerate(items):
            txt(ax, x + 1.3, T(16.4 + j * 3.9), '· ' + it, 11.2, INK, 'regular')
    arrow(ax, 32.3, T(24), 34.7, T(24), c=RED, lw=2.4, ms=14, style='<|-|>')
    arrow(ax, 65.3, T(24), 67.7, T(24), c=RED, lw=2.4, ms=14, style='<|-|>')
    box(ax, 2, T(43.5), 30, 7.5, fc='white', ec=RED, lw=1.4, r=0.3)
    txt(ax, 17, T(39.7), '청년창업·상생협력상가·커뮤니티센터\n기능 중복 회피, 성동시장 연계', 11.2, INK, 'semibold', 'center')
    box(ax, 68, T(43.5), 30, 7.5, fc='white', ec=RED, lw=1.4, r=0.3)
    txt(ax, 83, T(39.7), '동측 접속은 저층 주거 골목과\n맞닿는 가로 폭·높이를 고려', 11.2, INK, 'semibold', 'center')
    box(ax, 35, T(43.5), 30, 7.5, fc=PINK2, ec=RED, lw=1.4, r=0.3)
    txt(ax, 50, T(39.7), '역할 분담표는 확인 대기\n(2.6절 쟁점 5)', 11.2, INK, 'semibold', 'center')
    txt(ax, 2, 1.0, '출처: [T1] 도시재생활성화계획(변경) 경주역전지구·행복황촌(2025.12), 도시재생 전략계획. 각 계획의 주요 사업만 발췌', 10.5, G4)
    save(fig, '02_role_division.png')


# ------------------------------------------------------------------ 02 시 구상 1단계 구성
def f02_city_plan_mix():
    W, H = 15, 5.1
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    txt(ax, 2, T(2.4), '시 구상 1단계 79,438㎡의 구성(혁신지구 토지이용계획표 합계, 102필지)', 14, INK, 'bold')
    X0, X1 = 2, 98

    def bar(t0, segs, title):
        txt(ax, X0, T(t0), title, 12.5, INK, 'medium')
        x = X0; tot = sum(s[1] for s in segs); yb = T(t0 + 8.0)
        for nm, v, col, tc, sub in segs:
            w = (X1 - X0) * v / tot
            ax.add_patch(Rectangle((x, yb), w, 6.6, fc=col, ec='white', lw=2, zorder=3))
            c = 'white' if tc == 'w' else INK
            txt(ax, x + w / 2, yb + 4.4, nm, 12.5, c, 'bold', 'center')
            txt(ax, x + w / 2, yb + 1.9, sub, 11.2, c, 'regular', 'center')
            x += w
    bar(6.2, [('준주거', 25.5, G4, 'w', '20,262㎡ · 25.5%'), ('상업', 22.4, G3, 'w', '17,819㎡ · 22.4%'), ('문화시설', 15.4, G2, 'k', '12,260㎡ · 15.4%'),
              ('공공시설', 36.7, RED, 'w', '29,097㎡ · 36.7%')], '용도 구성')
    bar(17.4, [('국유', 70.5, G5, 'w', '70.5%'), ('사유', 29.5, G3, 'w', '29.5%')], '소유 구성')
    txt(ax, 2, 4.0, '공공시설 29,097㎡ = 도로 19,643㎡ + 공원 9,454㎡. 시 구상 범위와 본 계획 경계(228,022㎡)는 정의가 달라 비교하지 않음', 11, G4)
    txt(ax, 2, 1.0, '출처: [T2] 경주시 보도자료(2025.12.18), 김권일 발표자료 슬라이드 11·23(이미지 판독)', 10.5, G4)
    save(fig, '02_city_plan_mix.png')


# ------------------------------------------------------------------ 02 높이·밀도 상한 후보
def f02_limits_compare():
    W, H = 15, 6.1
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    txt(ax, 2, T(2.4), '높이 상한 후보와 본 계획 최고 높이 (m)', 14, INK, 'bold')
    hs = [('허용기준 3구역 · 평슬라브', 8, 'ghost', '8 (확인 대기)'), ('허용기준 3구역 · 경사지붕', 12, 'ghost', '12 (확인 대기)'),
          ('고도지구 도심 15 m', 15, G3, '15'), ('황오동 도로 인접 가이드(3층)', 15, G3, '15'),
          ('고도지구 도심 20 m', 20, G5, '20'), ('본 계획 최고(공공청사 본관 7층)', 28, RED, '28')]
    lx, bx, bw, dmax = 2, 29, 21, 30.0
    for i, (nm, v, col, lab) in enumerate(hs):
        y = T(8.4 + i * 4.5)
        txt(ax, lx, y, nm, 11.8, INK, 'medium')
        w = bw * v / dmax
        if col == 'ghost':
            ax.add_patch(Rectangle((bx, y - 1.6), w, 3.2, fc='white', ec=G4, lw=1.6, hatch='////', zorder=3))
        else:
            ax.add_patch(Rectangle((bx, y - 1.6), w, 3.2, fc=col, ec='none', zorder=3))
        txt(ax, bx + w + 0.8, y, lab, 12, RED if col == RED else INK, 'bold')
    ax.plot([54, 54], [4, T(3)], color=G2, lw=1.2)
    txt(ax, 57, T(2.4), '건폐율·용적률 (%)', 14, INK, 'bold')
    dx0, dw, dmax2 = 57, 34, 150.0
    for t0, nm in [(6.4, '건폐율'), (19.4, '용적률')]:
        txt(ax, 57, T(t0), nm, 12.5, INK, 'medium')
    rng = [(9.8, (0, 20), '자연녹지 한도 20 이하'), (14.4, None, ('본 계획 35.3', 35.3)),
           (22.8, (50, 100), '자연녹지 한도 50~100'), (27.4, None, ('본 계획 139.4', 139.4))]
    for t0, r, lab in rng:
        y = T(t0)
        if r:
            x0 = dx0 + dw * r[0] / dmax2; w = dw * (r[1] - r[0]) / dmax2
            ax.add_patch(Rectangle((x0, y - 1.6), w, 3.2, fc='white', ec=G4, lw=1.6, hatch='////', zorder=3))
            txt(ax, dx0 + dw * r[1] / dmax2 + 0.8, y, lab, 11.8, INK, 'bold')
        else:
            w = dw * lab[1] / dmax2
            ax.add_patch(Rectangle((dx0, y - 1.6), w, 3.2, fc=RED, ec='none', zorder=3))
            txt(ax, dx0 + w + 0.8, y, lab[0], 11.8, RED, 'bold')
    txt(ax, 2, 4.0, '빗금은 확인 대기 또는 일반 서술값(조문 재확인 대기). 적합 여부를 판정한 그림이 아니라 쟁점 1·2의 비교입니다', 10.8, G4)
    txt(ax, 2, 1.0, '출처: [T1] 경상북도 고시 제2020-479호, 경관가이드라인 · [T2] 김권일 발표자료 · [산정] 마스터플랜 개발규모 산정표', 10.5, G4)
    save(fig, '02_limits_compare.png')


# ------------------------------------------------------------------ 02 상위·관련계획 체계도(2차 수정: 글자 11 pt 이상으로 다시 그림)
def f02_plan_system():
    W, H = 15, 6.27
    fig, ax = canvas(W, H); yt = H / W * 100; T = lambda t: yt - t
    txt(ax, 2, T(2.0), '상위계획·관련계획의 체계와 본 계획의 위치', 15, INK, 'bold')
    txt(ax, 2, T(4.7),'실선 = 허가·상한·재원 등 본 계획이 따라야 하는 조건   ·   점선 = 방향·수요를 참조하는 계획', 11.2, G4)
    rows = [
        ('① 도시계획 — 용도·밀도·높이를 정함', False, [
            ('국토계획법 체계', '기본계획 → 관리계획 → 지구단위계획', '[T1]'),
            ('2030 경주도시기본계획', "부지는 '멀티복합타운', 면적·밀도 수치 없음", '[T1]'),
            ('용도지역 · 고도지구', '자연녹지 74.7% · 도심 20 m·15 m 지구', '[T1]')]),
        ('② 도시재생 — 사업 유형·재원·특례를 정함', False, [
            ('도시재생특별법', '활성화지역·혁신지구 지정, 특례, 통합심의', '[T1]'),
            ('도시재생 전략계획(변경)', '2022.01, 성동지구 해제, 재반영 검토', '[T1]'),
            ('활성화계획 · 공모 가이드라인', '2025.12 변경 계획, 2026.02 가이드라인', '[T1]')]),
        ('③ 문화유산·경관 — 조사·허가·경관을 정함', False, [
            ('문화유산법 · 고도 특별법', '보존지역 현상변경 허가, 지표조사·시굴', '[T1] 일부 확인 대기'),
            ('허용기준 · 시굴', '3구역(대상지 약 2/3), 시굴 필요 145,879㎡', '[T2]'),
            ('2030 경관계획 재정비', '황오동 중점경관관리구역, 도로 인접 3층·15 m', '[T1]')]),
        ('④ 시 구상·연구 — 방향과 수요를 참조', True, [
            ('폐철도 기본구상', '2023.04, 폐역 17개소 · 폐선 80.3 km', '[T2] 최종보고서 미확인'),
            ('원도심 미래구상 기획 연구', '2025.07, 제안 24건, 법정 계획이 아님', '[T2]'),
            ('시 구상 · MOU · 공모 추진', '79,438㎡ · 2027~2032 · MOU 2025.12.30', '[T2] · 사업비 [T4, 원문 미확인]')]),
    ]
    cw, ch, gx = 23.8, 6.4, 2.9
    x0 = 2.0
    for r, (lab, dashed, cards) in enumerate(rows):
        t0 = 6.6 + r * 8.9
        txt(ax, x0, T(t0), lab, 12.5, RED, 'bold')
        for c, (ttl, sub, tag) in enumerate(cards):
            x = x0 + c * (cw + gx)
            y = T(t0 + 1.3 + ch)
            box(ax, x, y, cw, ch, fc=G1, ec=G3, lw=1.2, r=0.4)
            txt(ax, x + 0.9, y + ch - 1.4, ttl, 12.2, INK, 'bold')
            txt(ax, x + 0.9, y + ch - 3.4, sub, 10.6, G5, 'regular', va='center')
            txt(ax, x + 0.9, y + 1.0, tag, 10.5, RED, 'bold')
            if c < 2:
                arrow(ax, x + cw + 0.15, y + ch / 2, x + cw + gx - 0.15, y + ch / 2, c=G5, lw=1.8, ms=13, ls=(0, (3, 2)) if dashed else '-')
        xe = x0 + 2 * (cw + gx) + cw
        arrow(ax, xe + 0.15, T(t0 + 1.3 + ch / 2), xe + gx + 0.2, T(t0 + 1.3 + ch / 2), c=RED, lw=2.2, ms=15, ls=(0, (3, 2)) if dashed else '-')
    bx = x0 + 3 * (cw + gx) - gx + gx + 0.6
    bw = 100 - bx - 1.2
    box(ax, bx, T(41.0), bw, 34.1, fc=RED, ec=RED, r=0.6)
    txt(ax, bx + 1.2, T(8.6), '본 계획', 13.5, 'white', 'bold')
    txt(ax, bx + 1.2, T(11.6), 'NEXUS 1918', 15, 'white', 'bold')
    txt(ax, bx + 1.2, T(13.3), '구 경주역 도시재생\n마스터플랜', 10.8, 'white', 'medium', va='top')
    txt(ax, bx + 1.2, T(18.6), '따르는 조건', 11.8, 'white', 'bold')
    txt(ax, bx + 1.2, T(20.1), '· 용도·고도 상한\n· 현상변경 허가\n· 매장유산 조사 선행\n· 활성화지역 특례 여부', 10.6, 'white', 'regular', va='top')
    txt(ax, bx + 1.2, T(28.1), '참조하는 방향', 11.8, 'white', 'bold')
    txt(ax, bx + 1.2, T(29.7), '· 단절 회복·생활거점\n· 청년 정주 기반\n· 폐선축 연계', 10.6, 'white', 'regular', va='top')
    txt(ax, bx + 1.2, T(35.9), '독립 수립', 11.8, 'white', 'bold')
    txt(ax, bx + 1.2, T(37.4), '관련 결정(2026.01 고시)과\n별개로 구성', 10.6, 'white', 'regular', va='top')
    save(fig, '02_plan_system.png')


ALL = {k[1:]: v for k, v in globals().items() if k.startswith('f0') and callable(v)}
if __name__ == '__main__':
    sel = sys.argv[1:] or list(ALL)
    for s in sel:
        ALL[s]()
