"""경주 예술인 통계 → 웹(리포트 §예술인)용 JSON.

입력: raw/kawf_artists_20260921.json (예술활동증명 대시보드, C-034) · raw/kosis_econcensus_arts_sgg.json (경제총조사 2015·2020, C-035) · raw/kosis_pop_sgg_latest.json
출력: processed/arts_stats.json
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; RAW = ROOT / 'archive/C_data/raw'; PROC = ROOT / 'archive/C_data/processed'
k = json.load(open(RAW / 'kawf_artists_20260921.json', encoding='utf-8'))
E = json.load(open(RAW / 'kosis_econcensus_arts_sgg.json', encoding='utf-8'))
pop = json.load(open(RAW / 'kosis_pop_sgg_latest.json', encoding='utf-8')); n2p = {v[0]: v[1] for v in pop.values()}
NAT_POP = 51_100_000   # 주민등록 2026.08 전국(약). 시군구 합은 시·구 중복이라 쓰지 않음
div = lambda d: {x['ART_DIV_NM']: int(x['CNT']) for x in d}
age = lambda d: {x['CER_AGE']: int(x['CNT']) for x in d}
sido_tot = {'서울': 79538, '경기': 56243, '부산': 11465, '인천': 10283, '경남': 10011, '전북': 6903, '대구': 6559, '대전': 5598, '광주': 5139, '전남': 5099, '강원': 4864, '충남': 4479, '경북': 4297, '충북': 4108, '제주': 3351, '울산': 2792, '세종': 1273}
# 시군구 (8개 도)
sgg = []
for s, lst in k['k2']['zip2'].items():
    for r in lst:
        p = n2p.get(r['ZIP2_NM'])
        sgg.append({'sido': s, 'name': r['ZIP2_NM'], 'n': int(r['CNT']), 'pop': p, 'per10k': round(int(r['CNT']) / p * 1e4, 1) if p else None})
sgg.sort(key=lambda x: -(x['per10k'] or 0))
rank_gj = next(i for i, x in enumerate(sgg, 1) if x['name'] == '경주시')
gb_cities = sorted([x for x in sgg if x['sido'] == '경북' and x['name'].endswith('시')], key=lambda x: -x['per10k'])
cmp_names = ['경주시', '전주시', '강릉시', '공주시', '경산시', '안동시', '통영시', '순천시', '포항시', '구미시']
cmp = [next(x for x in sgg if x['name'] == n) for n in cmp_names]
# 분야·연령
FIELDS = ['미술', '음악', '국악', '문학', '복수', '무용', '연극', '만화', '연예', '사진', '영화', '건축']
gj, gb, al = div(k['k1']['div_gj']), div(k['k1']['div_gb']), div(k['k1']['div_all'])
city_div = {c: div(v) for c, v in k['k2']['div'].items()}
tot = lambda d: sum(d.values())
fields = {'labels': FIELDS, 'gyeongju_n': [gj.get(f, 0) for f in FIELDS],
          'pct': {'경주': [round(gj.get(f, 0) / tot(gj) * 100, 1) for f in FIELDS], '경북': [round(gb.get(f, 0) / tot(gb) * 100, 1) for f in FIELDS], '전국': [round(al.get(f, 0) / tot(al) * 100, 1) for f in FIELDS],
                  **{c.replace('시', ''): [round(d.get(f, 0) / tot(d) * 100, 1) for f in FIELDS] for c, d in city_div.items() if c in ('전주시', '안동시', '공주시')}}}
AGES = ['20대', '30대', '40대', '50대', '60대', '70대', '80대']
ag, aa = age(k['k1']['age_gj']), age(k['k2']['age_all'])
ages = {'labels': AGES, 'gyeongju_n': [ag.get(a, 0) for a in AGES], 'pct': {'경주': [round(ag.get(a, 0) / tot(ag) * 100, 1) for a in AGES], '전국': [round(aa.get(a, 0) / tot(aa) * 100, 1) for a in AGES],
        **{c.replace('시', ''): [round(age(v).get(a, 0) / tot(age(v)) * 100, 1) for a in AGES] for c, v in k['k2']['age'].items() if c in ('전주시', '안동시')}}}
sex = k['k1']['sex_gj'][0]
# 경제총조사
def g(rows, code, ind, itm):
    x = [r for r in rows if r['C1'] == code and r['C2'] == ind and r['ITM_ID'] == itm]; return int(x[0]['DT']) if x and x[0]['DT'].isdigit() else None
codes = {r['C1_NM']: r['C1'] for r in E['2020']}
econ = []
for nm in ['경주시', '전주시', '공주시', '안동시', '경산시', '포항시', '구미시', '강릉시', '서귀포시', '부여군']:
    c = codes.get(nm); p = n2p.get(nm)
    if not c: continue
    row = {'name': nm, 'pop': p}
    for yr in ('2015', '2020'):
        for ind, key in (('901', 'create'), ('902', 'heritage'), ('R', 'r'), ('0', 'all')):
            row[f'{key}_biz_{yr}'] = g(E[yr], c, ind, 'T10'); row[f'{key}_emp_{yr}'] = g(E[yr], c, ind, 'T20')
    row['heritage_per10k_2020'] = round((row['heritage_emp_2020'] or 0) / p * 1e4, 1); row['create_per10k_2020'] = round((row['create_emp_2020'] or 0) / p * 1e4, 1)
    econ.append(row)
# 전국 시군구(인구 5만+) 902 종사자 순위에서 경주 위치
rk = []
for nm, c in codes.items():
    p = n2p.get(nm); e = g(E['2020'], c, '902', 'T20')
    if p and p > 50000 and e is not None and nm not in ('북구', '남구', '동구', '서구', '중구'): rk.append((nm, e / p * 1e4))
rk.sort(key=lambda x: -x[1]); rank_her = next(i for i, x in enumerate(rk, 1) if x[0] == '경주시')
out = {'asof': '2026-09-21', 'gyeongju': {'n': 675, 'pop': n2p['경주시'], 'per10k': round(675 / n2p['경주시'] * 1e4, 1), 'female_pct': float(sex['AFEMALE']), 'male': 271, 'female': 404, 'rank_in_8do': [rank_gj, len(sgg)], 'gb_rank_city': 1, 'valid_gb': {'완료': 2492, '만료': 1703, '특례': 102}},
       'nation': {'n': 222002, 'per10k': round(222002 / NAT_POP * 1e4, 1), 'sido': sido_tot, 'yearly_cum': {'2022': 157414, '2023': 176233, '2024': 191355, '2025': 201692, '2026': 222002}},
       'gb_cities': gb_cities, 'compare': cmp, 'sgg_top': sgg[:15], 'fields': fields, 'ages': ages, 'econ': econ, 'heritage_rank': [rank_her, len(rk)],
       'src': {'kawf': '한국예술인복지재단 예술인경력정보시스템 대시보드 — 2013~2026.09.21 누적 예술활동증명(유효+만료+특례, 신진·장애 포함) (T2). 인구 = 주민등록 2026.08 KOSIS (T2)',
               'econ': '통계청 경제총조사 2015·2020 시군구/산업소분류 (KOSIS DT_1KI1510·DT_2KI2010) — 901 창작·예술관련 서비스업, 902 도서관·사적지·박물관 (T2)'}}
json.dump(out, open(PROC / 'arts_stats.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('arts_stats', out['gyeongju'], 'heritage_rank', out['heritage_rank'], [ (e['name'], e['heritage_emp_2020'], e['create_emp_2020']) for e in econ])
