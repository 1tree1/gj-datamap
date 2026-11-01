"""카카오 로컬 POI(학교·유치원·종교시설) GeoJSON + 2030 기본계획 생활권 조인 레이어.

입력: archive/C_data/raw/kakao_poi_school_religion_20260921.json (브라우저 카카오 SDK 수집, T4 민간 POI)
      archive/C_data/processed/hadm_pop_4326.geojson (행정동 경계) + 90_derived/plan2030_tables.json (생활권별 표)
출력: processed/poi_schools_4326.geojson · poi_religion_4326.geojson · lifezone_4326.geojson
"""
import json, re
from pathlib import Path
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'archive/C_data/raw'; PROC = ROOT / 'archive/C_data/processed'; DERIV = ROOT / 'archive/90_derived'
d = json.load(open(RAW / 'kakao_poi_school_religion_20260921.json', encoding='utf-8'))
fc = lambda feats: {'type': 'FeatureCollection', 'features': feats}
pt = lambda v, props: {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [v['x'], v['y']]}, 'properties': props}
SRC = '카카오 로컬(Places) 키워드·카테고리 검색, 2026-09-21 수집 (T4 민간 POI — 공식 시설대장 아님, 누락·폐업 미반영 가능)'

# ---------- 학교
KIND = [('유치원', '유치원'), ('초등학교', '초등학교'), ('중학교', '중학교'), ('특성화고', '고등학교(특성화·특목)'), ('특목고', '고등학교(특성화·특목)'), ('고등학교', '고등학교'), ('대학교', '대학교'), ('학교부속', '기타')]
feats = []
for id_, v in d['schools'].items():
    kind = next((k for pat, k in KIND if pat in v['c']), '기타')
    if kind == '기타': continue
    closed = '휴원' in v['n'] or '폐교' in v['n']
    feats.append(pt(v, {'name': v['n'].replace(' (휴원)', ''), 'kind': kind, 'addr': v['a'].replace('경북 경주시 ', ''), 'road': v['r'], 'closed': closed, 'lbl': v['n'].replace('병설유치원', '병설유').replace(' (휴원)', '(휴원)'), 'source': SRC}))
json.dump(fc(feats), open(PROC / 'poi_schools_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
from collections import Counter
print('schools', len(feats), Counter(f['properties']['kind'] for f in feats))

# ---------- 종교 (사찰 부속 전각·요사 중복 제거)
def group(c, n):
    if '원불교' in c or '원불교' in n: return '원불교'
    if '불교' in c: return '불교'
    if '천주교' in c: return '천주교'
    if '기독교' in c: return '기독교(개신교)'
    if '원불교' in c: return '원불교'
    if '천도교' in c: return '천도교'
    if '이슬람' in c: return '이슬람'
    if '통일교' in c: return '통일교'
    if '기도원' in c or '수도원' in c: return '기도원·수도원'
    if '정교회' in n: return '정교회'
    if '용담정' in n: return '천도교'
    if re.search(r'사$|암$|선원$|법당|심인당|정사$', n): return '불교'
    if '교회' in n: return '기독교(개신교)'
    return '기타'
names = {v['n'] for v in d['religion'].values()}
feats = []; dropped = 0
for id_, v in d['religion'].items():
    n = v['n']
    parent = n.split(' ')[0]
    if ' ' in n and parent in names and parent != n and re.search(r'전$|문$|당$|원$|동$|관$|선원$|법당$', n.split(' ')[-1]): dropped += 1; continue
    g = group(v['c'], n)
    feats.append(pt(v, {'name': n, 'religion': g, 'kakao_cat': v['c'].replace('문화,예술 > 종교', '종교'), 'addr': v['a'].replace('경북 경주시 ', ''), 'dong': v['a'].replace('경북 경주시 ', '').split(' ')[0], 'source': SRC}))
json.dump(fc(feats), open(PROC / 'poi_religion_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
cnt = Counter(f['properties']['religion'] for f in feats)
print('religion', len(feats), 'dropped', dropped, cnt)

# ---------- 생활권 (읍면동 → 생활권 근사 조인)
LZ = {'중심생활권': ['황남동', '성건동', '황오동', '월성동', '선도동', '황성동', '용강동', '동천동', '불국동', '보덕동', '현곡면', '천북면'],
      '북부생활권': ['강동면', '안강읍'], '동부생활권': ['감포읍', '양남면', '문무대왕면'], '서부생활권': ['서면', '산내면', '건천읍'], '남부생활권': ['외동읍', '내남면']}
T = json.load(open(DERIV / 'plan2030_tables.json', encoding='utf-8'))
num = lambda s: float(str(s).replace('**', '').replace(',', '').split('(')[0].split('[')[0].strip()) if re.search(r'\d', str(s)) else None
dens = {r[0]: r for r in T[206]['rows']}; plan = {r[0]: r for r in T[208]['rows']}; res = {r[0]: r for r in T[245]['rows']}; park = {r[0].replace('**', ''): r for r in T[547]['rows']}
unpark = {('%s생활권' % r[1]): r for r in T[535]['rows'] if r[0] == '미조성공원' and r[1] != '소계'}
hp = json.load(open(PROC / 'hadm_pop_4326.geojson', encoding='utf-8'))
geoms = {f['properties']['hadm']: shape(f['geometry']) for f in hp['features']}
pops = {f['properties']['hadm']: f['properties']['pop'] for f in hp['features']}
feats = []
for lz, dongs in LZ.items():
    g = unary_union([geoms[x] for x in dongs if x in geoms]).simplify(0.0003)
    p26 = sum(pops[x] for x in dongs if x in pops)
    up = unpark.get(lz)
    props = {'name': lz, 'dongs': '·'.join(dongs), 'pop_2013': num(dens[lz][1]), 'pop_2030_plan': num(plan[lz][5]), 'pop_2026_actual': p26,
             'gap_pct': round((p26 / num(plan[lz][5]) - 1) * 100, 1), 'net_density_2013': num(dens[lz][7]), 'res_land_km2': num(res[lz][5]), 'res_density': num(res[lz][6]),
             'park_plan_count': num(park[lz][2]), 'park_plan_km2': num(park[lz][3]), 'park_per_capita_plan': num(park[lz][4]),
             'unbuilt_park_count': num(up[2]) if up else None, 'unbuilt_park_km2': num(up[3]) if up else None,
             'lbl': f"{lz}\n2030 {int(num(plan[lz][5])):,} / 실제 {p26:,}", 'source': '2030 경주도시기본계획 인쇄쪽 140~142·167·350·355 (T1) · 실제 = 주민등록 2026.08 행정동 합(T2). 생활권 경계는 읍면동 전체로 근사(계획은 "일부" 포함)'}
    feats.append({'type': 'Feature', 'geometry': mapping(g), 'properties': props})
json.dump(fc(feats), open(PROC / 'lifezone_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
for f in feats: print(f['properties']['name'], f['properties']['pop_2030_plan'], f['properties']['pop_2026_actual'], f['properties']['gap_pct'])
