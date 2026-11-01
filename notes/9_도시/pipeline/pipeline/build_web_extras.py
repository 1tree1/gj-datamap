"""2026-09-20 전수조사·소상공인365 산출물을 웹(gj-datamap)용 GeoJSON(4326)·표 JSON으로.

출력 (archive/C_data/processed/):
  footfall_areas_web_4326.geojson  8구역 폴리곤 + 유동인구·업종 요약 속성
  decline_2022_4326.geojson        행정동 법정 쇠퇴진단(2022 전략계획) — hadm_pop 경계에 조인
  landprice_pts_4326.geojson       황오동 모니터링 공시지가 29필지 2018–2025 (카카오 지오코딩)
  heritage_pts_4326.geojson        구경주역 매장유산 지표조사 유적·기조사 지점
  plan_nodes_4326.geojson          2030 기본계획·417쪽 연구·사용자안의 교통 거점(복합환승센터·터미널·P+R·순환셔틀 정거장)
  plan_routes_4326.geojson         2030 제1순환선 · 417 순환셔틀 (정거장을 잇는 개략선)
  web_extras.json                  사이드바 카드용 표(유동인구·업종·황오 KPI·공시지가 추이·쇠퇴진단·설문·매장유산·계획인구)
"""
import csv, json
from pathlib import Path
from shapely.geometry import Point, mapping, shape, LineString
from shapely.ops import transform
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'archive/C_data/processed'; RAW = ROOT / 'archive/C_data/raw'; DERIV = ROOT / 'archive/90_derived'
T4326_5187 = Transformer.from_crs(4326, 5187, always_xy=True).transform
T5187_4326 = Transformer.from_crs(5187, 4326, always_xy=True).transform
rd = lambda p: list(csv.DictReader((l for l in open(p, encoding='utf-8-sig') if not l.startswith('#'))))
num = lambda s: float(str(s).replace(',', '')) if str(s).strip() not in ('', 'None') else None
fc = lambda feats: {'type': 'FeatureCollection', 'features': feats}
def pt(lon, lat, props): return {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [lon, lat]}, 'properties': props}

# ---------- 1. 유동인구 8구역
LABEL = {'A_hwango_grid32': '황오동 원도심 활성화구역', 'B_haengbok_hwangchon_digitized': '행복황촌 활성화구역(근사)', 'C_zone_buffer300': '구역+300m', 'D_zone': '지구단위계획구역',
         'E_center_r300': '구역 중심 300m', 'F_cityhall_r500': '동천동 시청 500m', 'G_seongdong_market_r200': '성동시장 200m', 'H_hwangridan_r300': '황리단길 300m'}
SHORT = {'A_hwango_grid32': 'A 황오동', 'B_haengbok_hwangchon_digitized': 'B 행복황촌', 'C_zone_buffer300': 'C 구역+300m', 'D_zone': 'D 구역', 'E_center_r300': 'E 중심300m', 'F_cityhall_r500': 'F 시청500m', 'G_seongdong_market_r200': 'G 성동시장', 'H_hwangridan_r300': 'H 황리단길'}
areas5187 = {f['properties']['id']: shape(f['geometry']) for f in json.load(open(PROC / 'footfall_areas_5187.geojson', encoding='utf-8'))['features']}
def circ(lon, lat, r): return Point(T4326_5187(lon, lat)).buffer(r)
areas5187['E_center_r300'] = circ(129.218919, 35.8458367, 300)
areas5187['F_cityhall_r500'] = circ(129.2247816627553, 35.85621665939485, 500)
areas5187['G_seongdong_market_r200'] = circ(129.216354826459, 35.84534371000188, 200)
areas5187['H_hwangridan_r300'] = circ(129.2098, 35.8384, 300)
ffs = {r['area_id']: r for r in rd(DERIV / 'footfall_sbiz365_summary.csv')}
bza = {r['area_id']: r for r in rd(DERIV / 'biz_sbiz365_area_summary.csv')}
raw = json.load(open(RAW / 'sbiz365_footfall_20260920.json', encoding='utf-8'))
feats = []
for k, g in areas5187.items():
    f, b = ffs[k], bza[k]; r = raw[k]
    props = {'id': k, 'name': LABEL[k], 'short': SHORT[k], 'area_ha': round(g.area / 10000, 1),
             'footfall_avg': int(float(f['footfall_13mo_avg'])), 'footfall_2606': int(float(f['footfall_2606'])), 'per_ha': float(f['per_ha']),
             'pct_18_23': float(f['pct_18_23']), 'pct_23_05': float(f['pct_23_05']), 'weekend_ratio': float(f['weekend_to_weekday']), 'pct_60plus': float(f['pct_60plus']),
             'resident': int(float(f['resident_2026H1'])), 'worker': int(float(f['worker_2026H1'])), 'ff_per_rw': float(f['footfall_per_resident_worker']),
             'life_stores': int(b['life_stores_2606']), 'tour_stores': int(b['tour_stores_2606']), 'life_share': float(b['life_share_pct']) if b['life_share_pct'] else None,
             'life_chg': int(b['life_chg_13mo']), 'tour_chg': int(b['tour_chg_13mo']),
             'lbl': f"{SHORT[k]}\n{int(float(f['per_ha'])):,}/ha", 'source': '소상공인365 2025.06~2026.06 (T2)'}
    feats.append({'type': 'Feature', 'geometry': mapping(transform(T5187_4326, g)), 'properties': props})
json.dump(fc(feats), open(PROC / 'footfall_areas_web_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)

# ---------- 2. 쇠퇴진단 2022 → 행정동 경계
dec = {r['행정구역'].replace(' ', ''): r for r in rd(DERIV / 'gj_decline_diagnosis_2022_by_dong.csv')}
hp = json.load(open(PROC / 'hadm_pop_4326.geojson', encoding='utf-8'))
def cnt_met(r):
    pop = '감소' in r['인구_과거대비'] and float(r['인구_과거대비'].split('%')[0]) >= 20 or '3년' in r['인구_최근5년'] or '4년' in r['인구_최근5년'] or '5년' in r['인구_최근5년']
    biz = '감소' in r['사업체_과거대비'] and r['사업체_과거대비'] != '' and float(r['사업체_과거대비'].split('%')[0]) >= 5 or ('3년' in r['사업체_최근5년'] or '2년' in r['사업체_최근5년'])
    old = float(r['노후건축물비율(20년↑)'].rstrip('%')) >= 50
    return int(pop) + int(biz) + int(old), pop, biz, old
out = []
for f in hp['features']:
    name = f['properties']['hadm']; r = dec.get(name)
    if not r: continue
    n, pop_, biz_, old_ = cnt_met(r)
    props = {'hadm': name, 'pop_chg': r['인구_과거대비'], 'pop_5y': r['인구_최근5년'], 'biz_chg': r['사업체_과거대비'], 'biz_5y': r['사업체_최근5년'], 'old_pct': float(r['노후건축물비율(20년↑)'].rstrip('%')),
             'met': r['법정기준충족'], 'n_criteria': n, 'crit_pop': pop_, 'crit_biz': biz_, 'crit_old': old_,
             'lbl': f"{name}\n노후 {r['노후건축물비율(20년↑)']}", 'source': '경주시 도시재생전략계획(변경) 2022.01 인쇄쪽 251 (T1), 기준연도 미기재'}
    if name == '황오동': props['note'] = '2025 중부동 흡수 이전 값. 중부동: 인구 −26.7%·노후 84.5%·충족'
    out.append({'type': 'Feature', 'geometry': f['geometry'], 'properties': props})
json.dump(fc(out), open(PROC / 'decline_2022_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)

# ---------- 3. 공시지가 29필지 (카카오 주소검색 좌표, 2026-09-21)
GEO = {'원화로281번길 9-7': (129.216410228231, 35.8456244439158), '원화로281번길 11': (129.216311960953, 35.8453940583343), '화랑로 139-8': (129.216248008075, 35.8446947671706), '화랑로 139-2': (129.216238086161, 35.8445967364973), '화랑로 141-1': (129.21637318404, 35.8446156884795), '화랑로 139-28': (129.216323411403, 35.8448512386518), '화랑로 139-64': (129.216398892915, 35.8451059223748), '화랑로 139-32': (129.216388410687, 35.8449360888962), '화랑로 139-14': (129.216379076312, 35.8447796597792), '화랑로 141-20': (129.216547424466, 35.8447765531561), '화랑로 143-4': (129.216753372524, 35.8446333609355), '화랑로 143-6': (129.216756538824, 35.8446834906198), '성동동 51-4': (129.216686007799, 35.84505584202), '화랑로 141-38': (129.216673332111, 35.8449304704938), '화랑로 141-62': (129.21659724046, 35.8450593724168), '화랑로 143-20': (129.216772429749, 35.8450515438952), '성동동 57-3': (129.216758221079, 35.8453322108447), '원화로281번길 3-11': (129.216823070296, 35.8455587076126), '성동동 57-35': (129.2167322008, 35.8455622769278), '성동동 57-34': (129.216732850684, 35.8456134441963), '성동동 57-27': (129.21674050959, 35.8457295374349), '성동동 57-38': (129.216280807037, 35.8455470897543), '성동동 399-10': (129.216265926496, 35.845111890018), '성동동 307-1': (129.215977743466, 35.8464994079122), '성동동 81-2': (129.217012255465, 35.8467172010843), '원화로 248-7': (129.217837854593, 35.8427642196515), '북정로 25': (129.215229321211, 35.8432070140781), '화랑로 140-1': (129.216236604632, 35.8442612151969), '동성로 152-1': (129.217078677642, 35.8429700673343)}
yrs = [str(y) for y in range(2018, 2026)]
lp = rd(DERIV / 'hwango_land_price_29parcels_2018_2025.csv'); feats = []; avg = {y: [] for y in yrs}
for r in lp:
    a = r['주소(도로명/지번)'].replace('원화로281번길', '원화로281번길').replace('원화로 281번길', '원화로281번길')
    key = next((k for k in GEO if k.replace(' ', '') == a.replace(' ', '')), None)
    if not key: print('좌표 없음', a); continue
    ser = {y: num(r[y]) for y in yrs}
    for y in yrs: avg[y].append(ser[y])
    chg = round((ser['2025'] / ser['2018'] - 1) * 100, 1)
    feats.append(pt(*GEO[key], {'addr': r['주소(도로명/지번)'], 'jiga_2018': ser['2018'], 'jiga_2022': ser['2022'], 'jiga_2025': ser['2025'], 'chg_18_25_pct': chg, 'chg_21_22_pct': round((ser['2022'] / ser['2021'] - 1) * 100, 1),
                                'series': json.dumps(ser, ensure_ascii=False), 'lbl': f"{chg:+.0f}%", 'source': '황오동 원도심 모니터링 2025.09 인쇄쪽 60 (토지이음 개별공시지가, T2 전사) · 좌표 카카오 주소검색',
                                'note': '2022 급등(587,500→4,380,000) — 지목·용도 변경 의심' if '140-1' in a else ''}))
json.dump(fc(feats), open(PROC / 'landprice_pts_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
lp_avg = {y: round(sum(avg[y]) / len(avg[y])) for y in yrs}

# ---------- 4. 매장유산 지점
her = [
    pt(129.219757438425, 35.8476828736293, {'name': '성동동 대구기관차승무분소 휴게실 신축부지 유적', 'kind': '발굴(정밀)', 'year': '2002', 'area_m2': 540, 'finds': '통일신라 유물포함층, 주혈 6', 'addr': '성동동 114 일원'}),
    pt(129.21940, 35.84720, {'name': '성동동 경주차량분소 기관차검수고 신축부지 유적', 'kind': '시굴', 'year': '2003', 'area_m2': 2331, 'finds': '통일신라 적심석군 4·수혈 1·석열 1', 'addr': '성동동 117·118 (지오코딩 불가 → 114 인근 근사)'}),
    pt(129.21930, 35.84700, {'name': '성동동 경주차량분소 부지내 유적', 'kind': '발굴(정밀)', 'year': '2004', 'area_m2': 525, 'finds': '통일신라 건물지 1·우물 1·수혈 2·석열 1, 유물 8', 'addr': '성동동 118 (근사)'}),
    pt(129.21762483532, 35.8445327562747, {'name': '경주 황오동 삼층석탑 (도 문화유산자료)', 'kind': '지정유산', 'year': '1936 이건', 'area_m2': None, 'finds': '통일신라 말 양식, 남산 장창곡 사자사지 탑재 이건', 'addr': '성동동 40 (역전 광장 북)'}),
    pt(129.217825940584, 35.8450382225689, {'name': '경주 성동동사지 Ⅱ (비지정, 유존지역)', 'kind': '유존지역', 'year': '2022 지표조사', 'area_m2': 40882, 'finds': '건물지 담장열·적심·석조유구 — 시굴 필요', 'addr': '성동동 40 일원 (구역 내)'}),
]
for f in her: f['properties']['source'] = '김권일(2026.02.27) 혁신포럼 발표자료 · 2022 성림문화재연구원 지표조사 (T2)'
json.dump(fc(her), open(PROC / 'heritage_pts_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)

# ---------- 5. 계획 거점 (2030 기본계획 T1 · 417쪽 연구 T2 · 사용자안)
N = {'구경주역': (129.21793175706665, 35.84442707332487), '시외버스터미널': (129.2024687469408, 35.83980000855561), '고속버스터미널': (129.203673502641, 35.8388282090558),
     '신경주역(KTX)': (129.1389994195668, 35.798377252282435), '서경주역': (129.1803471762241, 35.88474149744894), '팔우정삼거리': (129.217248009246, 35.8408562467448),
     '황성공원': (129.214242363291, 35.8589974318489), '시립도서관': (129.219191998787, 35.8597818801442), '경주시청': (129.2247816627553, 35.85621665939485),
     '성동시장': (129.216354826459, 35.84534371000188), '서라벌문화회관': (129.207857365891, 35.838863109853), '중앙시장': (129.20674378595027, 35.843961867137544),
     '동국대병원': (129.1966953295423, 35.85840061588908), '경주세무서·경주교': (129.2172, 35.8515), '성건동주민센터·흥무초 수변': (129.2057, 35.8503), '대릉원 주차장': (129.215677947036, 35.8351762005644)}
nodes = [
    ('구경주역', '복합환승센터', '2030 도시기본계획 §교통 — 복합환승센터 3개소', 'T1'), ('시외버스터미널', '복합환승센터', '2030 도시기본계획 — 복합환승센터 3개소', 'T1'), ('신경주역(KTX)', '복합환승센터·종합터미널 계획입지', '2030 도시기본계획 — 종합터미널(교통센터) 적정입지 = 고속철도 역세권', 'T1'),
    ('고속버스터미널', '통합 재개발(현 위치)', '417쪽 연구 목표 3a — 서천교 관문 재정의·터미널 통합', 'T2'), ('구경주역', '교통거점 부활 + 복합문화상업', '417쪽 연구 목표 3b', 'T2'),
    ('성건동주민센터·흥무초 수변', 'P+R 제안', '417쪽 연구 — 순환 대중교통 거점 4곳', 'T2'), ('경주세무서·경주교', 'P+R 제안', '417쪽 연구 — 순환 대중교통 거점 4곳', 'T2'), ('고속버스터미널', 'P+R 제안', '417쪽 연구 — 순환 대중교통 거점 4곳', 'T2'), ('팔우정삼거리', 'P+R 제안', '417쪽 연구 — 순환 대중교통 거점 4곳', 'T2'),
    ('서경주역', '원도심 관문(셔틀 기점)', '417쪽 연구 시나리오 B — 서경주역을 원도심 기능적 관문으로', 'T2'), ('대릉원 주차장', '미술관·인포센터 제안', '417쪽 연구 시나리오 B·C', 'T2'),
    ('구경주역', '시청 본청 + 터미널 + 트램 기점(사용자안)', '2026-09-20 계획 방향 — 상위계획 2건과 터미널 입지 불일치', '방향'),
]
feats = [pt(*N[n], {'name': n, 'role': role, 'source': src, 'tier': t, 'lbl': f"{n}\n{role}"}) for n, role, src, t in nodes]
json.dump(fc(feats), open(PROC / 'plan_nodes_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
routes = [
    ('2030 기본계획 제1순환선(생활)', 'T1', ['고속버스터미널', '중앙시장', '성건동주민센터·흥무초 수변', '황성공원', '경주세무서·경주교', '구경주역', '성동시장', '팔우정삼거리', '대릉원 주차장', '서라벌문화회관', '고속버스터미널'], '터미널→성건동→황성공원→경주역(성동시장)→중앙시장→대릉원→터미널 (정거장 순서는 개략)'),
    ('417쪽 연구 순환 셔틀(무인)', 'T2', ['서경주역', '동국대병원', '황성공원', '시립도서관', '경주시청', '경주세무서·경주교', '구경주역', '성동시장', '팔우정삼거리', '서라벌문화회관', '고속버스터미널', '중앙시장', '동국대병원'], '서경주역–황성공원–시청–(옛)경주역/성동시장–서라벌문화회관–터미널–동국대병원 (개략)'),
]
feats = [{'type': 'Feature', 'geometry': mapping(LineString([N[n] for n in stops])), 'properties': {'name': nm, 'tier': t, 'note': note, 'stops': ' → '.join(stops)}} for nm, t, stops, note in routes]
json.dump(fc(feats), open(PROC / 'plan_routes_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)

# ---------- 6. 사이드바 표
months = raw['A_hwango_grid32']['monthly']['months']
ff = {k: {'short': SHORT[k], 'name': LABEL[k], 'monthly': [num(x) for x in raw[k]['monthly']['sel']], 'hourly': [num(x) for x in raw[k]['hourly']['sel']], 'hourly_pct': [num(x) for x in raw[k]['hourly']['sel_pct']],
          'weekday_pct': [num(x) for x in raw[k]['weekday']['sel_pct']], 'sexage_pct': [num(x) for x in raw[k]['daily_sex_age']['sel_pct']], 'per_ha': float(ffs[k]['per_ha']), 'avg': int(float(ffs[k]['footfall_13mo_avg'])),
          'resident': int(float(ffs[k]['resident_2026H1'])), 'worker': int(float(ffs[k]['worker_2026H1'])), 'area_ha': round(areas5187[k].area / 10000, 1)} for k in LABEL}
bz = rd(DERIV / 'biz_sbiz365_summary.csv')
biz = {}
for r in bz:
    biz.setdefault(r['area_id'], {})[r['tpbiz']] = {'n': int(r['stores_2606']), 'chg': int(r['stores_chg_13mo']), 'sales': num(r['sales_per_store_avg']), 'subst': r['substituted']}
kpi = rd(DERIV / 'hwango_kpi_2018_2024.csv'); sc = rd(DERIV / 'hwango_startup_closure_2018_2024.csv')
extras = {
    'months': months, 'footfall': ff, 'biz': biz, 'biz_area': bza,
    'hwango_kpi': {r['지표']: {y: num(r[y]) for y in ['2018', '2019', '2020', '2021', '2022', '2023', '2024']} for r in kpi},
    'startup_closure': {f"{r['구분']}|{r['지표']}": {y: num(r[y]) for y in ['2018', '2019', '2020', '2021', '2022', '2023', '2024']} for r in sc},
    'landprice_avg': lp_avg, 'landprice_hwangchon44': {'2021': 442934, '2022': 485880, '2023': 516904, '2024': 488003, '2025': 486217},
    'decline': [{'hadm': r['행정구역'], 'pop': r['인구_과거대비'], 'pop5': r['인구_최근5년'], 'biz': r['사업체_과거대비'], 'biz5': r['사업체_최근5년'], 'old': r['노후건축물비율(20년↑)'], 'met': r['법정기준충족']} for r in dec.values()],
    'surveys': [{'survey': r['조사'], 'when': r['시점'], 'n': r['표본'], 'q': r['문항'], 'a': r['응답'], 'v': r['값'], 'src': r['출처']} for r in rd(DERIV / 'citizen_preference_surveys_station_site.csv')],
    'heritage': [{'k': r['항목'], 'v': r['값'], 'u': r['단위'], 'note': r['비고']} for r in rd(DERIV / 'site_heritage_survey_2022.csv')],
    'plan_pop': {'plan_2030': 320000, 'actual_2026_08': 242512, 'src': '2030 경주도시기본계획 §4.2 계획인구 (T1) / 주민등록 2026-08 KOSIS (T2)'},
    'haengbok_footfall_report': {'2019': 1096, '2020': 1284, '2021': 1524, '2022': 1167, '2023': 1544, '2024/25(보고서 표기 불일치)': 5431},
    'sources': {'footfall': '소상공인365(bigdata.sbiz.or.kr) 상권분석 리포트 — 통신사 추정 유동인구 월별 일평균, 2025.06~2026.06 (T2). 구역 정의는 work/20260920_소상공인365_유동인구_재추출.md',
                'biz': '소상공인365 업종분석·매출분석 11개 업종 (T2). 업소≤3 매출은 행정동 평균 대체(subst=Y)',
                'hwango': '2024년 황오동 원도심 도시재생뉴딜 성과지표·모니터링 결과보고서(공공도시, 2025.09) 전사 (T2)',
                'decline': '경주시 도시재생 전략계획(변경) 최종보고서 2022.01 인쇄쪽 251 (T1)',
                'heritage': '김권일 2026.02.27 도시재생혁신포럼 발표자료 / 구)경주역일원 매장유산 시굴조사 추진계획 (T2)'},
}
json.dump(extras, open(PROC / 'web_extras.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('done', {k: len(v['features']) if isinstance(v, dict) and 'features' in v else '' for k, v in {}.items()})
for n in ['footfall_areas_web_4326', 'decline_2022_4326', 'landprice_pts_4326', 'heritage_pts_4326', 'plan_nodes_4326', 'plan_routes_4326']:
    print(n, len(json.load(open(PROC / f'{n}.geojson', encoding='utf-8'))['features']))
