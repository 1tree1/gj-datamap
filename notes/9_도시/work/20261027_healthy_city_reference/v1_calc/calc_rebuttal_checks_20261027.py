# -*- coding: utf-8 -*-
"""
v1 반박 검토 재산정 (2026-10-27) — 「건강한도시_후보와_판정지표_v1.md」 v1.1 개정의 [산정] 근거.

입력(읽기만)
  - research/B_data/raw_mois/emd_201512·202012·202512·202609.csv  행정안전부 주민등록 인구통계 [T2]
  - v1_calc/cbs_buurt_gm_nl_20261027.csv  CBS 「Kerncijfers wijken en buurten」 83220NED·84286NED·84799NED·85318NED·86165NED
      OData 재조회 사본(2026-10-27) [T2] https://opendata.cbs.nl/ODataApi/odata/86165NED
  - research/data/cbs_binnenstad_pop_20261027.csv  (레이던 wijk) [T2]
  - research/data/bologna_centro_storico_pop_20261027.csv  Comune di Bologna [T2]
  - 교토 값은 아래 K·KH·JP 상수(출처 URL 병기, 2026-10-27 열람) [T2]
사용: python -I calc_rebuttal_checks_20261027.py <폴더 = 20261027_healthy_city_reference> <출력 csv>
"""
import csv
import os
import re
import sys

BASE, OUT = sys.argv[1], sys.argv[2]
RAW = os.path.join(BASE, 'research', 'B_data', 'raw_mois')
res = []


def put(item, value, unit, grade, note=''):
    res.append([item, value, unit, grade, note])


def g(a, b):
    return (b / a - 1) * 100


def load_emd(fn):
    out = {}
    with open(os.path.join(RAW, fn), encoding='cp949', newline='') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            m = re.match(r'(.*?)\s*\((\d{10})\)', row[0].strip())
            if not m:
                continue
            v = []
            for x in row[1:]:
                x = x.replace(',', '').strip()
                v.append(int(x) if x.isdigit() else 0)
            out[m.group(2)] = v
    return out


E = {y: load_emd(f'emd_{y}.csv') for y in ('201512', '202012', '202512', '202609')}


def k(code, y):  # 강원·전북 특별자치도 코드 변경 전 연도
    if y < '202312' and code[:2] == '51':
        return '42' + code[2:]
    if y < '202401' and code[:2] == '52':
        return '45' + code[2:]
    return code


def P(y, c):
    return E[y][k(c, y)][0]


def H(y, c):
    return E[y][k(c, y)][1]


# 1) 전주 중앙동(K1) 5211151000, 노송동 5211160500
J, N = '5211151000', '5211160500'
p15, p20, p25, p269 = P('201512', J), P('202012', J), P('202512', J), P('202609', J)
put('K1 인구 2015.12/2020.12/2025.12/2026.09', f'{p15}/{p20}/{p25}/{p269}', '명', 'T2')
put('K1 R1 2015→2020', round(g(p15, p20), 1), '%', 'T2→산정')
put('K1 R1 2020→2025', round(g(p20, p25), 1), '%', 'T2→산정')
put('K1 2025.12→2026.09', round(g(p25, p269), 1), '%', 'T2→산정')
put('K1 세대 2020→2025 증감', H('202512', J) - H('202012', J), '세대', 'T2→산정')
put('노송동 인구 2020→2025 증감', P('202512', N) - P('202012', N), '명', 'T2→산정', f"{P('202012', N)}→{P('202512', N)}")
put('노송동 세대 2020→2025 증감', H('202512', N) - H('202012', N), '세대', 'T2→산정')
NEW = 1319  # 전주 태평 아이파크 세대수 [T4, 건축물대장 대조 대기]
for h in (1.98, 1.5, 2.0, 2.5):
    put(f'K1 E1 R1p (N_new {NEW}, h {h}, 분모 P(t0))', round(g(p15, p25 - NEW * h), 1), '%', '산정', 'h 1.98 = S2 세대당 인구(2025.12)')
for h in (1.5, 1.98, 2.5):
    d0 = p20  # 분모 P(t0) − P_철거(t0), P_철거 대리 = 2015→2020 감소분 전체 [가정, 상한]
    put(f'K1 E1 R1p (h {h}, 분모 P(t0)−P_철거, P_철거 = 2015→2020 감소분 {p15 - p20}명 [가정])', round(g(d0, p25 - NEW * h), 1), '%', '산정·가정')

# 2) 대구 군위군 편입 보정 — 대구 성내 묶음 시 나머지
S2D = ['2711056500', '2711057500', '2711058500', '2711051700', '2711054500']
a0 = sum(P('201512', c) for c in S2D)
a1 = sum(P('202512', c) for c in S2D)
c0, c1 = E['201512']['2700000000'][0], E['202512']['2700000000'][0]
gun25, gun15 = E['202512']['2772000000'][0], E['201512']['4772000000'][0]
put('대구 시 나머지 R1(군위 혼입, v1 값)', round(g(c0 - a0, c1 - a1), 1), '%', 'T2→산정')
put('대구 시 나머지 R1(군위 제외 보정)', round(g(c0 - a0, c1 - gun25 - a1), 1), '%', 'T2→산정', f'군위 2025.12 {gun25}명, 2015.12 {gun15}명(경북 4772000000)')


def load_age(fn):  # v[4] = 20~29세, v[5] = 30~39세 (calc_r1r2_double_baseline 과 같은 열)
    return load_emd(fn)


A0, A1 = load_age('age_201512.csv'), load_age('age_202512.csv')


def yy(A, code):
    return A[code][4] + A[code][5]


ys0, ys1 = sum(yy(A0, cc) for cc in S2D), sum(yy(A1, cc) for cc in S2D)
yc0, yc1, yg1 = yy(A0, '2700000000'), yy(A1, '2700000000'), yy(A1, '2772000000')
put('대구 시 나머지 R2 대리(군위 혼입 / 보정)', f'{round(g(yc0 - ys0, yc1 - ys1), 1)} / {round(g(yc0 - ys0, yc1 - yg1 - ys1), 1)}', '%', 'T2→산정', f'군위 20~39세 2025.12 {yg1}명')

# 3) CBS buurt·wijk·gemeente·국가
C = {}
with open(os.path.join(BASE, 'v1_calc', 'cbs_buurt_gm_nl_20261027.csv'), encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        C[(r['year'], r['code'])] = {kk: (int(float(r[kk])) if r[kk] not in ('', 'None') else None)
                                    for kk in ('inwoners', 'woningvoorraad', 'age15_24')}


def c(y, code, fld='inwoners'):
    return C[(y, code)][fld]


def bsum(y, pre, fld='inwoners', excl=()):
    return sum(v[fld] or 0 for (yy, code), v in C.items() if yy == y and code.startswith(pre) and code not in excl)


def occ_change(p0_, w0_, p1_, w1_):
    """대칭 E1 하한: R1p = (P1 − ΔW·P1/W1)/P0 − 1 = 주택당 인구 변화율(재고 순증 전량을 신축으로 둔 하한)."""
    return g(p0_ / w0_, p1_ / w1_)


# 델프트 WK050311, 2015→2025
y0, y1 = '2015', '2025'
d0w, d1w = c(y0, 'WK050311'), c(y1, 'WK050311')
st0, st1 = c(y0, 'BU05031105'), c(y1, 'BU05031105')
put('델프트 Stationsbuurt BU05031105 인구 2015/2022/2025', f"{st0}/{c('2022', 'BU05031105')}/{st1}", '명', 'T2')
put('델프트 Stationsbuurt 주택 2015→2025', f"{c(y0, 'BU05031105', 'woningvoorraad')}→{c(y1, 'BU05031105', 'woningvoorraad')}", '호', 'T2')
put('델프트 증가분 중 Stationsbuurt 몫', round((st1 - st0) / (d1w - d0w) * 100, 1), '%', 'T2→산정')
put('델프트 R1(Stationsbuurt 제외)', round(g(d0w - st0, d1w - st1), 1), '%', 'T2→산정', f'{d0w - st0}→{d1w - st1}')
a150, a151 = c(y0, 'WK050311', 'age15_24'), c(y1, 'WK050311', 'age15_24')
put('델프트 15~24세 2015→2025, 증가분 대비', f'{a150}→{a151}, {round((a151 - a150) / (d1w - d0w) * 100, 1)}%', '명·%', 'T2→산정')
stud = sorted(code for (yy, code), v in C.items()
              if yy == y1 and code.startswith('BU050311') and v['inwoners'] and v['age15_24'] / v['inwoners'] >= 0.35)
put('델프트 P5 제외 buurt(2025 15~24세 ≥ 35% [가정])', ' '.join(stud), '', '산정·가정')
q0, q1 = bsum(y0, 'BU050311', excl=stud), bsum(y1, 'BU050311', excl=stud)
put('델프트 R1(P5 buurt 제외)', round(g(q0, q1), 1), '%', 'T2→산정', f'{q0}→{q1}')
put('델프트 R1 2015→2020 / 2020→2025', f"{round(g(d0w, c('2020', 'WK050311')), 1)} / {round(g(c('2020', 'WK050311'), d1w), 1)}", '%', 'T2→산정')
gm0, gm1 = c(y0, 'GM0503'), c(y1, 'GM0503')
put('델프트 R1 S2 / 시 나머지 / 국가', f"{round(g(d0w, d1w), 2)} / {round(g(gm0 - d0w, gm1 - d1w), 2)} / {round(g(c(y0, 'NL00'), c(y1, 'NL00')), 2)}", '%', 'T2→산정')
put('델프트 S2와 시 나머지 차', round(g(d0w, d1w) - g(gm0 - d0w, gm1 - d1w), 2), '%p', '산정')
dw0, dw1 = c(y0, 'WK050311', 'woningvoorraad'), c(y1, 'WK050311', 'woningvoorraad')
gw0, gw1 = c(y0, 'GM0503', 'woningvoorraad'), c(y1, 'GM0503', 'woningvoorraad')
nw0, nw1 = c(y0, 'NL00', 'woningvoorraad'), c(y1, 'NL00', 'woningvoorraad')
put('델프트 E1 비대칭(재고 순증 전량 신축, h 1.4)', round(g(d0w, d1w - (dw1 - dw0) * 1.4), 1), '%', 'T2→산정', f'재고 {dw0}→{dw1}')
put('델프트 E1 대칭(주택당 인구 변화) S2 / 시 나머지 / 국가',
    f"{round(occ_change(d0w, dw0, d1w, dw1), 2)} / {round(occ_change(gm0 - d0w, gw0 - dw0, gm1 - d1w, gw1 - dw1), 2)} / "
    f"{round(occ_change(c(y0, 'NL00'), nw0, c(y1, 'NL00'), nw1), 2)}", '%', 'T2→산정', '재고 순증 전량을 신축으로 둔 하한')

# 's-Hertogenbosch WK079601, 2018→2025
y0, y1 = '2018', '2025'
s0, s1 = c(y0, 'WK079601'), c(y1, 'WK079601')
ce0, ce1 = c(y0, 'BU07960101'), c(y1, 'BU07960101')
put("'s-H 증가분 중 Binnenstad centrum(BU07960101) 몫", round((ce1 - ce0) / (s1 - s0) * 100, 1), '%', 'T2→산정', f'{ce0}→{ce1}')
put("'s-H centrum 주택 2018→2025", f"{c(y0, 'BU07960101', 'woningvoorraad')}→{c(y1, 'BU07960101', 'woningvoorraad')}", '호', 'T2')
put("'s-H 나머지 5개 buurt R1", round(g(bsum(y0, 'BU079601', excl=['BU07960101']), bsum(y1, 'BU079601', excl=['BU07960101'])), 1), '%', 'T2→산정')
sw0, sw1 = c(y0, 'WK079601', 'woningvoorraad'), c(y1, 'WK079601', 'woningvoorraad')
put("'s-H 주택당 인구 2018→2025", f'{s0 / sw0:.3f}→{s1 / sw1:.3f}', '명/호', 'T2→산정')
for h in (1.5, round(s1 / sw1, 3)):
    put(f"'s-H E1 비대칭(재고 순증 {sw1 - sw0}호 전량 신축, h {h})", round(g(s0, s1 - (sw1 - sw0) * h), 1), '%', 'T2→산정')
gm0, gm1 = c(y0, 'GM0796'), c(y1, 'GM0796')
gw0, gw1 = c(y0, 'GM0796', 'woningvoorraad'), c(y1, 'GM0796', 'woningvoorraad')
nw0, nw1 = c(y0, 'NL00', 'woningvoorraad'), c(y1, 'NL00', 'woningvoorraad')
put("'s-H E1 대칭(주택당 인구 변화) S2 / 시 나머지 / 국가, 2018→2025",
    f"{round(occ_change(s0, sw0, s1, sw1), 2)} / {round(occ_change(gm0 - s0, gw0 - sw0, gm1 - s1, gw1 - sw1), 2)} / "
    f"{round(occ_change(c(y0, 'NL00'), nw0, c(y1, 'NL00'), nw1), 2)}", '%', 'T2→산정')
z0 = '2020'
s20, sw20 = c(z0, 'WK079601'), c(z0, 'WK079601', 'woningvoorraad')
gm20, gw20 = c(z0, 'GM0796'), c(z0, 'GM0796', 'woningvoorraad')
put("'s-H R1 2020→2025 S2 / 시 나머지 / 국가", f"{round(g(s20, s1), 1)} / {round(g(gm20 - s20, gm1 - s1), 1)} / {round(g(c(z0, 'NL00'), c(y1, 'NL00')), 1)}",
    '%', 'T2→산정', '2020~ 육지 190 ha 같은 표기')
put("'s-H E1 대칭 2020→2025 S2 / 시 나머지 / 국가",
    f"{round(occ_change(s20, sw20, s1, sw1), 2)} / {round(occ_change(gm20 - s20, gw20 - sw20, gm1 - s1, gw1 - sw1), 2)} / "
    f"{round(occ_change(c(z0, 'NL00'), c(z0, 'NL00', 'woningvoorraad'), c(y1, 'NL00'), nw1), 2)}", '%', 'T2→산정')
put("'s-H 2025→2026 S2", round(g(s1, 13780), 1), '%', 'T2→산정', 'CBS 86358NED 2026 = 13,780명(research/data 사본)')
cw0, cw1 = c(y0, 'BU07960101', 'woningvoorraad'), c(y1, 'BU07960101', 'woningvoorraad')
put("'s-H centrum 주택당 인구 변화 2018→2025", round(occ_change(ce0, cw0, ce1, cw1), 1), '%', 'T2→산정', f'{ce0 / cw0:.3f}→{ce1 / cw1:.3f}')
rp0, rp1 = bsum(y0, 'BU079601', excl=['BU07960101']), bsum(y1, 'BU079601', excl=['BU07960101'])
rw0 = bsum(y0, 'BU079601', 'woningvoorraad', excl=['BU07960101'])
rw1 = bsum(y1, 'BU079601', 'woningvoorraad', excl=['BU07960101'])
put("'s-H 나머지 5개 buurt 주택당 인구 변화 2018→2025", round(occ_change(rp0, rw0, rp1, rw1), 1), '%', 'T2→산정')
dp0, dp1 = bsum('2015', 'BU050311', excl=['BU05031105']), bsum('2025', 'BU050311', excl=['BU05031105'])
dq0 = bsum('2015', 'BU050311', 'woningvoorraad', excl=['BU05031105'])
dq1 = bsum('2025', 'BU050311', 'woningvoorraad', excl=['BU05031105'])
put('델프트 Stationsbuurt 밖 buurt 주택당 인구 변화 2015→2025', round(occ_change(dp0, dq0, dp1, dq1), 1), '%', 'T2→산정', f'인구 {dp0}→{dp1}, 주택 {dq0}→{dq1}')

# 레이던 주택당 인구 (research/data 사본)
L = {}
with open(os.path.join(BASE, 'research', 'data', 'cbs_binnenstad_pop_20261027.csv'), encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        if r['table_year'] in ('2015', '2025') and r['wijk'][:8] in ('WK054600', 'WK054601'):
            a = L.setdefault(r['table_year'], [0, 0])
            a[0] += int(r['inwoners'])
            a[1] += int(r['woningvoorraad'])
put('레이던 주택당 인구 2015→2025', f"{L['2015'][0] / L['2015'][1]:.3f}→{L['2025'][0] / L['2025'][1]:.3f} ({round(occ_change(*L['2015'], *L['2025']), 1)}%)", '명/호', 'T2→산정')

# 4) 교토 — 国勢調査 [T2]
#  1995·2010·2015 구별: https://www.city.kyoto.lg.jp/templates/shingikai_kekka/cmsfiles/contents/0000259/259919/09siryou5.pdf
#  2020·2025 구별·세대(確報, 2026-09-29): https://www.city.kyoto.lg.jp/sogo/cmsfiles/contents/0000358/358071/siryo.pdf
#  국가 2015·2025: 埼玉県 보도자료 경유 https://www.pref.saitama.lg.jp/a0206/news/page/news2026092901.html (総務省 원문 미대조)
K = {'1995': (91062, 70662, 48241, 1463822), '2010': (105306, 79287, 40528, 1474015), '2015': (109341, 82668, 39044, 1475183),
     '2020': (110488, 82784, 36602, 1463723), '2025': (111231, 84410, 35127, 1430062)}  # 中京, 下京, 東山, 시 전체
KH = {'2020': (60634, 48309, 729524), '2025': (64523, 51720, 757287)}  # 中京, 下京, 시 전체 세대
JP = {'2015': 127094745, '2025': 122972528}


def ky(y0_, y1_):
    a, b = K[y0_], K[y1_]
    s0_, s1_ = a[0] + a[1], b[0] + b[1]
    return s0_, s1_, g(s0_, s1_), g(a[3] - s0_, b[3] - s1_), g(a[2], b[2]), g(a[3] - a[2], b[3] - b[2])


for y0_, y1_ in (('2015', '2025'), ('2010', '2020'), ('1995', '2020')):
    s0_, s1_, gs, gr, ge, ger = ky(y0_, y1_)
    put(f'교토 中京+下京 {y0_}→{y1_}: S2 / 시 나머지', f'{s0_}→{s1_}: {gs:+.1f} / {gr:+.1f}', '명·%', 'T2→산정')
    put(f'교토 東山 {y0_}→{y1_}: S2 / 시 나머지(시−東山)', f'{ge:+.1f} / {ger:+.1f}', '%', 'T2→산정')
put('일본 국가 2015→2025', round(g(JP['2015'], JP['2025']), 1), '%', 'T2(埼玉県 경유)→산정')
sh0 = (K['2020'][0] + K['2020'][1]) / (KH['2020'][0] + KH['2020'][1])
sh1 = (K['2025'][0] + K['2025'][1]) / (KH['2025'][0] + KH['2025'][1])
rh0 = (K['2020'][3] - K['2020'][0] - K['2020'][1]) / (KH['2020'][2] - KH['2020'][0] - KH['2020'][1])
rh1 = (K['2025'][3] - K['2025'][0] - K['2025'][1]) / (KH['2025'][2] - KH['2025'][0] - KH['2025'][1])
put('교토 세대당 인구 2020→2025 S2 / 시 나머지', f'{sh0:.3f}→{sh1:.3f} ({g(sh0, sh1):+.1f}%) / {rh0:.3f}→{rh1:.3f} ({g(rh0, rh1):+.1f}%)', '명/세대', 'T2→산정')
for lab, a, b in (('뒤 값', (360, 488), (471, 738)), ('앞 값', (360, 488), (463, 726))):
    put(f'교토 簡易宿所 中京+下京 H29→R7년도 1월 말({lab})', f'{sum(a)}→{sum(b)} ({g(sum(a), sum(b)):+.1f}%)', '곳', 'T2 표 판독→산정',
        'minjpakunogenjyoutokadaitou.pdf p.8, R7 행이 두 겹으로 추출됨')

# 5) 볼로냐 2021→2024
B = {}
with open(os.path.join(BASE, 'research', 'data', 'bologna_centro_storico_pop_20261027.csv'), encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        B[r['anno']] = (int(r['centro_storico']), int(r['zone_periferiche']))
put('볼로냐 centro 2021→2024 / 시 나머지(주거 부정 제외)', f"{g(B['2021'][0], B['2024'][0]):+.1f} / {g(B['2021'][1], B['2024'][1]):+.1f}", '%', 'T2→산정')

with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['항목', '값', '단위', '등급', '비고'])
    w.writerows(res)
print(len(res), 'rows')
