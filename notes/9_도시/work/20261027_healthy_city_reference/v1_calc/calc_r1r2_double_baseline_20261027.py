# -*- coding: utf-8 -*-
"""
국내 후보 R1·R2 이중 기준선 판정 (2026-10-27) — 「건강한 도시 후보와 판정지표 v1」 §1·§2의 [산정] 근거.

입력: research/B_data/raw_mois/ 의 행정안전부 주민등록 인구통계 읍면동 CSV [T2] (B 문서가 2026-10-27 내려받은 사본, 읽기만)
  emd_201512.csv·emd_202512.csv (총인구·세대), age_201512.csv·age_202512.csv (10세 구간)
규칙(A 문서 §3.1): 통과 = S2 ≥ 시 나머지 그리고 S2 ≥ 국가 / 보류 = 하나만 넘음 / 실패 = 둘 다 못 넘음.
  - S2 = 원도심 행정동 묶음(대리 범위, B 문서와 같은 묶음), 시 나머지 = 비교 시군 − S2, 국가 = 17개 시도 합.
  - R1 = 총인구 수 변화율(2015.12→2025.12), R2(대리) = 20~39세 인구 수 변화율(10세 구간 제약, 정의 20~34세와 다름).
  - 주민등록 인구는 전수 등록이라 신뢰구간을 붙이지 않음(A §3.1).
사용: python -I calc_r1r2_double_baseline_20261027.py <raw_mois 폴더> <출력 csv>
"""
import csv, os, re, sys

RAW, OUT = sys.argv[1], sys.argv[2]


def load(fn):
    out = {}
    with open(os.path.join(RAW, fn), encoding='cp949', newline='') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            m = re.match(r'(.*?)\s*\((\d{10})\)', row[0].strip())
            if not m:
                continue
            vals = []
            for x in row[1:]:
                x = x.replace(',', '').strip()
                vals.append(int(x) if x.isdigit() else 0)
            out[m.group(2)] = vals
    return out


Y0, Y1 = '201512', '202512'
EMD = {y: load(f'emd_{y}.csv') for y in (Y0, Y1)}
AGE = {y: load(f'age_{y}.csv') for y in (Y0, Y1)}


def key(code, y):
    if y < '202312' and code[:2] == '51':
        return '42' + code[2:]
    if y < '202401' and code[:2] == '52':
        return '45' + code[2:]
    return code


def total(y, codes):
    return sum(EMD[y].get(key(c, y), [0])[0] for c in codes)


def hh(y, codes):
    return sum(EMD[y].get(key(c, y), [0, 0])[1] for c in codes)


def young(y, codes):
    s = 0
    for c in codes:
        v = AGE[y].get(key(c, y))
        if v:
            s += v[4] + v[5]   # 20~29, 30~39
    return s


def nation(tab, y, f):
    codes = [c for c in tab[y] if c.endswith('00000000') and c != '0000000000']
    return f(y, codes), len(codes)


def g(a, b):
    return (b / a - 1) * 100 if a else float('nan')


def judge(s2, rest, nat):
    k = (s2 >= rest) + (s2 >= nat)
    return {2: '통과', 1: '보류', 0: '실패'}[k]


SETS = [  # B 문서 b_candidate_pop_20261027.py 와 같은 묶음
    ('공주 원도심', ['4415051000', '4415056000'], ['4415000000']),
    ('순천 원도심', ['4615051500', '4615062000'], ['4615000000']),
    ('강릉 중앙동', ['5115052000'], ['5115000000']),
    ('군산 원도심', ['5213053000', '5213051500', '5213060500'], ['5213000000']),
    ('목포 원도심', ['4611065500', '4611066000'], ['4611000000']),
    ('안동 원도심', ['4717051000', '4717052000'], ['4717000000']),
    ('수원 행궁동', ['4111574000'], ['4111000000']),
    ('전주 풍남동(한옥마을)', ['5211153000'], ['5211000000']),
    ('전주 중앙동(객사)', ['5211151000'], ['5211000000']),
    ('대구 성내1·2·3+동인+삼덕', ['2711056500', '2711057500', '2711058500', '2711051700', '2711054500'], ['2700000000']),
    ('청주 원도심', ['4311152500', '4311154500'], ['4311000000']),
    ('부산 초량1·2·6동', ['2617051000', '2617052000', '2617055000'], ['2600000000']),
    ('부산 초량3동', ['2617053000'], ['2600000000']),
    ('부산 영도 원도심', ['2620053000', '2620054000', '2620055000', '2620058500', '2620059000', '2620060500'], ['2600000000']),
    ('통영 원도심', ['4822055000', '4822059000', '4822053000'], ['4822000000']),
    ('진주 원도심', ['4817056500', '4817055500'], ['4817000000']),
    ('경주 황남동(황리단길)', ['4713057000'], ['4713000000']),
    ('경주 기준선(황오+옛 중부)', ['4713053000', '4713051500'], ['4713000000']),
    ('부여읍', ['4476025000'], ['4476000000']),
    ('영주1동', ['4721055000'], ['4721000000']),
    ('논산 강경읍', ['4423025000'], ['4423000000']),
    ('서울 북촌(가회+삼청)', ['1111060000', '1111054000'], ['1100000000']),
    ('서울 서촌(청운효자+사직)', ['1111051500', '1111053000'], ['1100000000']),
]

(n0, k0), (n1, k1) = nation(EMD, Y0, total), nation(EMD, Y1, total)
(ny0, _), (ny1, _) = nation(AGE, Y0, young), nation(AGE, Y1, young)
gN, gNY = g(n0, n1), g(ny0, ny1)
print(f'국가 총인구 {n0:,} -> {n1:,} ({gN:+.2f}%), 시도 {k0}/{k1}개; 20~39세 {ny0:,} -> {ny1:,} ({gNY:+.2f}%)')

hdr = ['후보', 'S2_2015', 'S2_2025', 'R1_S2(%)', 'R1_시나머지(%)', 'R1_국가(%)', 'R1_판정',
       'R1_시나머지와의차(pp)', 'Y_S2_2015', 'Y_S2_2025', 'R2대리_S2(%)', 'R2대리_시나머지(%)', 'R2대리_국가(%)', 'R2_판정',
       '세대_S2(%)', '세대_시나머지(%)']
rows = []
for name, s2, city in SETS:
    a0, a1 = total(Y0, s2), total(Y1, s2)
    c0, c1 = total(Y0, city), total(Y1, city)
    r0, r1 = c0 - a0, c1 - a1
    y0, y1 = young(Y0, s2), young(Y1, s2)
    cy0, cy1 = young(Y0, city), young(Y1, city)
    h0, h1 = hh(Y0, s2), hh(Y1, s2)
    ch0, ch1 = hh(Y0, city), hh(Y1, city)
    gS, gR = g(a0, a1), g(r0, r1)
    gYS, gYR = g(y0, y1), g(cy0 - y0, cy1 - y1)
    rows.append([name, a0, a1, round(gS, 1), round(gR, 1), round(gN, 1), judge(gS, gR, gN), round(gS - gR, 1),
                 y0, y1, round(gYS, 1), round(gYR, 1), round(gNY, 1), judge(gYS, gYR, gNY),
                 round(g(h0, h1), 1), round(g(ch0 - h0, ch1 - h1), 1)])
with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(hdr)
    w.writerows(rows)
for r in rows:
    print(r)
