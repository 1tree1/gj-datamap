"""통계 리포트(report.html)용 데이터 — 2030 기본계획 표(plan2030_tables.json) + 경관계획·417쪽 연구 설문 + KOSIS 실제 + 이번 세션 산출물.

모든 항목에 src(출처·쪽·등급)를 붙인다. 출력: archive/C_data/processed/report_stats.json
"""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'archive/C_data/processed'; DERIV = ROOT / 'archive/90_derived'
T = json.load(open(DERIV / 'plan2030_tables.json', encoding='utf-8'))
def tb(i): return T[i]
def n(s):
    s = str(s).replace('**', '').replace(',', '').strip()
    m = re.match(r'^-?\d+(\.\d+)?', s)
    return float(m.group(0)) if m else None
def pct_in_paren(s):
    m = re.search(r'\(([\d.]+)%?', str(s)); return float(m.group(1)) if m else None
PLAN = '2030 경주도시기본계획(승인, T1)'
def src(i, extra=''): t = tb(i); return f"{PLAN} 인쇄쪽 {t['page']} 「{t['title']}」 {t['source']} {extra}".strip()

R = {}
# ---------- 1. 인구
pop = tb(149); years = [r[0] for r in pop['rows'] if re.match(r'^\d{4}$', r[0])]
R['pop_doc'] = {'years': years, 'total': [n(r[1]) for r in pop['rows'] if r[0] in years], 'foreign': [n(r[5]) for r in pop['rows'] if r[0] in years], 'src': src(149)}
hp = json.load(open(PROC / 'hadm_pop_4326.geojson', encoding='utf-8'))
tot = {}
for f in hp['features']:
    for y, v in (f['properties'].get('yearly') or {}).items(): tot[y] = tot.get(y, 0) + v
R['pop_actual'] = {'years': sorted(tot), 'total': [tot[y] for y in sorted(tot)], 'pop_2026_08': sum(f['properties']['pop'] for f in hp['features']), 'n65_2026_08': sum(f['properties']['n_65'] for f in hp['features']),
                   'src': '행안부 주민등록인구 KOSIS DT_1B04005N, 행정동 합 (T2). 기본계획의 통계연보 값과 기준(외국인 포함 여부·시점)이 달라 2011~13년이 약 1만 명 차이'}
plan = tb(208)
R['pop_plan'] = {'years': ['2013', '2015', '2020', '2025', '2030'], 'total': [n(x) for x in plan['rows'][0][1:]], 'by_lifezone': {r[0]: [n(x) for x in r[1:]] for r in plan['rows'][1:]}, 'src': src(208)}
old = tb(46)
R['aging'] = {'years': old['header'][1:], 'pct65': [n(x) for x in old['rows'][2][1:]], 'n65': [n(x) for x in old['rows'][1][1:]], 'pct65_2026': round(R['pop_actual']['n65_2026_08'] / R['pop_actual']['pop_2026_08'] * 100, 1), 'src': src(46)}
age = tb(173)
R['age_projection'] = {'years': age['header'][1:], 'p0_14': [pct_in_paren(x) for x in age['rows'][0][1:]], 'p15_64': [pct_in_paren(x) for x in age['rows'][2][1:]], 'p65': [pct_in_paren(x) for x in age['rows'][4][1:]],
                       'dependency': [n(x.replace('%', '')) for x in age['rows'][8][1:]], 'src': src(173, '— 자연적증가인구 기준, 외국인 제외')}
pc = tb(172)
R['pop_plan_components'] = {'plan': 320000, 'natural_domestic': 252490, 'natural_foreign': 10000, 'social': {'신경주역세권': 5904, '도시개발사업': 13634, '주택건설사업': 9878, '일반산업단지': 24353}, 'src': src(172)}
dens = tb(206)
R['lifezone_density'] = {'rows': [{'zone': r[0], 'pop': n(r[1]), 'pop_pct': n(r[2]), 'area_km2': n(r[3]), 'urban_km2': n(r[5]), 'gross': n(r[6]), 'net': n(r[7])} for r in dens['rows']], 'src': src(206)}

# ---------- 2. 토지
lu = tb(223)
cols = ['주거', '상업', '공업', '녹지', '미지정', '계획관리', '생산관리', '보전관리', '농림', '자연환경보전']
vals = lu['rows'][0]; pcts = lu['rows'][1]
idx = [3, 4, 5, 6, 7, 9, 10, 11, 12, 13]
R['landuse'] = {'items': [{'name': c, 'km2': n(vals[i]), 'pct': n(pcts[i])} for c, i in zip(cols, idx)], 'total_km2': n(vals[1]), 'src': src(223)}
lp = tb(289)
R['landuse_plan'] = {'rows': [{'name': r[0].replace('**', '').replace('— ', ''), 'before': n(r[1]), 'after': n(r[4]), 'before_pct': n(r[2]), 'after_pct': n(r[5])} for r in lp['rows']], 'src': src(289)}
cz = tb(273)
R['commercial_plan'] = {'rows': [{'zone': r[0], 'before': n(r[1]), 'after': n(r[3])} for r in cz['rows']], 'src': src(273)}

# ---------- 3. 교통
ms = tb(315)
share_row = [r for r in ms['rows'] if r[0].startswith('수단분담률(도보포함)') and '계' in r[1]][0]
R['mode_share_2007'] = {'modes': ['도보', '승용차', '택시', '버스', '철도', '기타'], 'pct': [n(x) for x in share_row[2:8]], 'total_trips': n([r for r in ms['rows'] if '계' in r[1]][0][8]), 'src': src(315, '(경주시 도시교통정비 기본계획 2007.06 기준)')}
by_purpose = {r[1]: [n(x) for x in r[2:8]] for r in ms['rows'] if r[0].startswith('수단분담률(도보포함)') and '계' not in r[1]}
R['mode_share_2007']['by_purpose'] = by_purpose
mp = tb(331)
R['mode_forecast'] = {'modes': [r[0].replace('**', '') for r in mp['rows'][:-1]], 'years': ['2015', '2020', '2025', '2030'],
                      'pct': {r[0]: [n(r[2]), n(r[4]), n(r[6]), n(r[8])] for r in mp['rows'][:-1]}, 'trips': {r[0]: [n(r[1]), n(r[3]), n(r[5]), n(r[7])] for r in mp['rows'][:-1]}, 'src': src(331)}
car = tb(310)
R['cars'] = {'years': [h.replace('년', '') for h in car['header'][2:7]], 'per_1000_total': [n(x) for x in car['rows'][10][2:7]], 'per_1000_car': [n(x) for x in car['rows'][6][2:7]], 'cars_total': [n(x) for x in car['rows'][5][2:7]], 'src': src(310)}
rail = tb(313)
R['rail'] = {'years': [r[0] for r in rail['rows']], 'ktx_board': [n(r[1]) for r in rail['rows']], 'gj_board': [n(r[4]) for r in rail['rows']], 'src': src(313, '— 경주역은 2021.12 폐역, 신경주역이 현 경주역')}
bus = tb(314)
R['bus'] = {'years': [r[0] for r in bus['rows']], 'city_pax': [n(r[2]) for r in bus['rows']], 'charter_pax': [n(r[4]) for r in bus['rows']], 'fleet': [n(r[1]) for r in bus['rows']], 'src': src(314)}
pk = tb(306)
R['parking'] = {'rows': [{'kind': r[0].replace('**', ''), 'sites': n(r[1]), 'spaces': n(r[2])} for r in pk['rows']], 'src': src(306)}
vc = tb(312)
R['road_vc'] = {'rows': [{'road': r[0], 'seg': r[1], 'lanes': n(r[2]), 'aadt': n(r[3]), 'vc': n(r[4])} for r in vc['rows'] if n(r[4]) is not None], 'src': src(312)}

# ---------- 4. 관광·경관·문화재
tv = tb(635)
R['tourists'] = {'years': [r[0].replace('년', '') for r in tv['rows']], 'total': [n(r[1]) for r in tv['rows']], 'foreign': [n(r[3]) for r in tv['rows']], 'src': src(635, '— 지정(법정)관광지 보문·양남·감포 방문객만')}
vis = json.load(open(ROOT / 'archive/C_data/raw/visitors_gyeongju_daily.json', encoding='utf-8'))
days = sorted(k for k in vis if vis[k].get('현지인') is not None)
R['visitors_2026'] = {'days': len(days), 'from': days[0], 'to': days[-1], 'sum_local': round(sum(vis[d]['현지인'] for d in days)), 'sum_ext': round(sum(vis[d]['외지인'] for d in days)), 'sum_foreign': round(sum(vis[d].get('외국인', 0) or 0 for d in days)),
                     'src': '한국관광공사 관광데이터랩 DataLabService (KT 이동통신 순방문자, 시군구, T2) — 기본계획의 지정관광지 입장객과 정의가 다름'}
ch = tb(49); ch2 = tb(50)
R['heritage_count'] = {'years': [r[0] for r in ch['rows']], 'total': [n(r[1]) for r in ch['rows']], 'national': [n(r[2]) for r in ch['rows']], 'treasure': [n(r[4]) for r in ch['rows']], 'historic': [n(r[5]) for r in ch['rows']], 'src': src(49)}
pk2 = tb(53)
R['parks'] = {'kinds': pk2['header'][2:], 'count': [n(x) for x in pk2['rows'][0][2:]], 'area_k_m2': [n(x) for x in pk2['rows'][1][2:]], 'total_count': n(pk2['rows'][0][1]), 'total_k_m2': n(pk2['rows'][1][1]), 'src': src(53)}
R['landscape_survey'] = {'n': {'시민': 330, '관광객': 60, '공무원': 168}, 'when': '2024~25 (2030 경관계획 재정비 경관의식조사)',
    'representative': {'불국사': {'시민': 24.2, '공무원': 28.6, '관광객': 53.3}, '황리단길': {'시민': 36.4, '공무원': 31.0, '관광객': 38.3}},
    'identity_silla': {'시민': 67.6, '공무원': 78.6, '관광객': 71.7}, 'worst_ad': {'시민': 44.1, '공무원': 71.4, '관광객': 45.0}, 'worst_hwangridan': {'시민': 52.9, '공무원': 54.8, '관광객': 51.7},
    'priority_projects': {'녹지네트워크·생태경관': {'시민': 38.2, '공무원': 54.8}, '관광지 주변 건축물 색채정비': {'시민': 52.9, '공무원': 52.4}, '주요도로변 가로환경 정비': {'시민': 50.0, '공무원': 47.6}, '건물 색상·디자인 규격화(경관협정)': {'시민': 45.5, '공무원': 59.8}},
    'src': '2030 경주시 경관계획 재정비(2025.04, T1) ch.2.5 경관의식조사 인쇄쪽 100~108'}

# ---------- 5. 경제·산업·주거·재정·에너지
bz = tb(630)
R['business'] = {'years': [r[0] for r in bz['rows']], 'firms': [n(r[1]) for r in bz['rows']], 'workers': [n(r[2]) for r in bz['rows']], 'src': src(630)}
ind = tb(183)
last_b = [r for r in ind['rows'] if r[0] == '2013' and r[1] == '사업체'][0]; last_w = [r for r in ind['rows'] if r[0] == '2013' and r[1] == '종사자'][0]
R['industry_2013'] = {'firms_pct': {'1차': pct_in_paren(last_b[7]), '2차': pct_in_paren(last_b[8]), '3차': pct_in_paren(last_b[9])}, 'workers_pct': {'1차': pct_in_paren(last_w[7]), '2차': pct_in_paren(last_w[8]), '3차': pct_in_paren(last_w[9])},
                     'gb_workers_pct': {'1차': pct_in_paren(last_w[3]), '2차': pct_in_paren(last_w[4]), '3차': pct_in_paren(last_w[5])}, 'src': src(183)}
hs = tb(440); ht = tb(441)
R['housing'] = {'years': [r[0] for r in hs['rows']], 'households': [n(r[1]) for r in hs['rows']], 'units': [n(r[2]) for r in hs['rows']], 'supply_rate': [n(r[3]) for r in hs['rows']],
                'type_2013': {'단독': n(ht['rows'][4][2]), '연립': n(ht['rows'][4][4]), '다세대': n(ht['rows'][4][5]), '아파트': n(ht['rows'][4][6])}, 'src': src(440) + ' / ' + src(441)}
el = tb(494)
R['electricity'] = {'years': [h.replace('년', '') for h in el['header'][1:]], 'total': [n(x) for x in el['rows'][0][1:]], 'home': [n(x) for x in el['rows'][1][1:]], 'service': [n(x) for x in el['rows'][3][1:]], 'industry': [n(x) for x in el['rows'][4][1:]], 'src': src(494)}
fin = tb(673)
R['finance'] = {'years': [r[0].replace('**', '') for r in fin['rows']], 'general_revenue': [n(r[4]) for r in fin['rows']], 'budget_2025_100M': 22500, 'src': src(673, '— 일반회계 세입 결산(백만원). 2025 예산 2조 2,500억은 417쪽 미래구상 연구(2025.07, T2) 인용')}
med = tb(649)
R['medical'] = {'years': med['header'][2:], 'hospitals': [n(x) for x in med['rows'][0][2:]], 'beds': [n(x) for x in med['rows'][1][2:]], 'src': src(649)}

# ---------- 6. 시민의식 설문 2015 (기본계획) — 문항별 분포
Q = {102: '경주시 도시특성(이미지)', 103: '경주시 문제점', 104: '우선 개선사항', 105: '개발 중심축', 106: '경주역 부지 활용', 107: '교통 개선사항', 108: '주거환경 문제점', 109: '주거환경 개선', 110: '선호 주거유형', 111: '경관관리 방안', 112: '공원·녹지 문제점', 113: '복지시설 문제점', 114: '필요 복지시설', 115: '중점 육성산업', 116: '관광 발전방안', 117: '발전 잠재력', 118: '2030 미래상 키워드(복수)'}
R['survey_2015'] = {'meta': '2030 기본계획 시민의식 설문, 2015.9.18~10.17, 배포 1,970 / 회수 1,408 (71.5%), 신뢰수준 95% ±3.1% — 인쇄쪽 72~83 (T1 부속)',
                    'questions': [{'q': q, 'page': tb(i)['page'], 'items': [{'a': r[1], 'v': n(r[2])} for r in tb(i)['rows'] if r[1] not in ('무응답', '기타')]} for i, q in Q.items()]}

# ---------- 7. 417쪽 연구 설문(2025) + 2023 폐철도 설문(T4)
R['survey_2025'] = {'meta': '경주시 원도심 미래구상 기획연구(동국대·가천대, 2025.07, T2) §2.2 — 시민 설문 65명(유효 63)·인지지도 27명, 2025.3·4월',
    'symbolic_center': {'황리단길': 25, '첨성대': 16, '보문': 12, '불국사': 12}, 'social_center': {'황리단길': 16, '황성동': 9, '동천동': 8}, 'shopping_center': {'홈플러스·성동시장': 16, '탑마트·중앙시장': 13, '하나로마트': 8},
    'friendly_cities': {'울산': 40, '포항': 40, '대구': 32, '부산': 11}, 'transit_score': 2.7, 'transit_alt': {'자율주행 무료버스': 18, '보행공간 개선': 13, '옛철도 재개통': 10, '트램': 8, '버스전용차선': 1},
    'future_image': {'관광도시': 35, '힐링도시': 28, '역사도시': 23, '시민을 위한 도시': 11}, 'needed_facility': {'쇼핑여가': 26, '대중교통': 24, '문화예술': 24, '의료보건': 8, '하천': 6, '학교': 5, '관광시설': 2, '편의': 1, '주차': 1}}
R['survey_2023'] = {'meta': '경주시 폐철도 기본구상 설문 2023.04, 3,151명 — 언론 경유 T4, 원문 미확보', 'items': {'시청 이전': 63.7, '도시숲': 65.3}}

# ---------- 8. 이번 세션 산출물 (web_extras 재사용)
R['extras'] = json.load(open(PROC / 'web_extras.json', encoding='utf-8'))
json.dump(R, open(PROC / 'report_stats.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ok', list(R))
