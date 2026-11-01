"""공식 소스로 학교·종교시설 레이어 교체.

학교: 공공데이터포털 전국초중등학교위치표준데이터 API(tn_pubr_public_elesch_mskul_lc_api, 한국교육시설안전원, T2) — 전량 수집 후 경주시 필터.
      유치원·대학은 표준데이터에 없어 카카오 로컬(T4) 수집분을 보조로 병합(src 필드로 구분).
종교: 경상북도 경주시_종교시설현황_20250206.csv (경주시, T2) 586건 → V-World 지오코더(도로명→지번), 실패분은 카카오 수집 동명 시설 좌표로 대체(src 표시).
출력: processed/poi_schools_4326.geojson · poi_religion_4326.geojson (기존 카카오 전용 파일을 덮어씀; 카카오 원본은 raw에 보존)
"""
import sys, json, re, csv, time, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_env, get_json, RAW, PROCESSED
env = load_env(); KEY = env['DATA_GO_KR_KEY']; VK = env['VWORLD_KEY']; H = {'Referer': env.get('VWORLD_DOMAIN', ''), 'User-Agent': 'Mozilla/5.0'}
fc = lambda feats: {'type': 'FeatureCollection', 'features': feats}
pt = lambda lon, lat, props: {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [round(lon, 6), round(lat, 6)]}, 'properties': props}
kakao = json.load(open(RAW / 'kakao_poi_school_religion_20260921.json', encoding='utf-8'))

# ---------- 학교 (표준데이터 전량 → 경주시)
url = 'https://api.data.go.kr/openapi/tn_pubr_public_elesch_mskul_lc_api'
rows = []; page = 1
while True:
    j = get_json(f'{url}?serviceKey={KEY}&pageNo={page}&numOfRows=1000&type=json')
    items = j['body']['items']['item'] if j.get('body') and j['body'].get('items') else []
    rows += items
    if len(rows) >= int(j['body']['totalCount']) or not items: break
    page += 1; time.sleep(0.2)
gj = [r for r in rows if '경주시' in (r.get('lnmadr') or '') or '경주시' in (r.get('rdnmadr') or '')]
json.dump(gj, open(RAW / 'schools_std_gyeongju_20260921.json', 'w', encoding='utf-8'), ensure_ascii=False)
SRC_S = '전국초중등학교위치표준데이터 (한국교육시설안전원, 공공데이터포털 API, 기준일 2026-03-20, T2)'
feats = []
for r in gj:
    kind = r['schoolSe']; feats.append(pt(float(r['longitude']), float(r['latitude']), {
        'name': r['schoolNm'], 'kind': kind, 'status': r.get('operSttus'), 'branch': r.get('bnhhSe'), 'found': r.get('fondDate'), 'fond_type': r.get('fondType'),
        'addr': (r.get('lnmadr') or '').replace('경상북도 경주시 ', ''), 'road': r.get('rdnmadr'), 'closed': r.get('operSttus') != '운영',
        'lbl': r['schoolNm'] + ('' if r.get('operSttus') == '운영' else f"({r.get('operSttus')})"), 'src': '표준데이터', 'source': SRC_S}))
n_std = len(feats)
SRC_K = '카카오 로컬 키워드·카테고리 검색 2026-09-21 (T4 민간 POI — 표준데이터에 없는 유치원·대학만 보조)'
for v in kakao['schools'].values():
    if '유치원' in v['c']: kind = '유치원'
    elif '대학교' in v['c']: kind = '대학교'
    else: continue
    closed = '휴원' in v['n']
    feats.append(pt(v['x'], v['y'], {'name': v['n'].replace(' (휴원)', ''), 'kind': kind, 'status': '휴원' if closed else '', 'addr': v['a'].replace('경북 경주시 ', ''), 'road': v['r'], 'closed': closed,
                                     'lbl': v['n'].replace('병설유치원', '병설유').replace(' (휴원)', '(휴원)'), 'src': '카카오', 'source': SRC_K}))
json.dump(fc(feats), open(PROCESSED / 'poi_schools_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
from collections import Counter
print('schools 표준', n_std, Counter(f['properties']['kind'] for f in feats), Counter(f['properties']['status'] for f in feats))

# ---------- 종교시설 (경주시 현황 CSV → 지오코딩)
cache_p = RAW / 'geocode_cache_religion.json'
cache = json.load(open(cache_p, encoding='utf-8')) if cache_p.exists() else {}
def geocode(addr):
    a = re.sub(r'\(.*?\)', '', addr).strip()
    a = re.sub(r'(\d+)\s*길', r'\1길', a)            # '감포로 8길' → '감포로8길'
    if a in cache: return cache[a]
    res = None
    for typ in ('ROAD', 'PARCEL'):
        try:
            r = get_json(f"https://api.vworld.kr/req/address?service=address&request=getcoord&version=2.0&crs=EPSG:4326&type={typ}&address={urllib.parse.quote('경상북도 ' + a)}&format=json&key={VK}", H, retries=1)['response']
            if r['status'] == 'OK': res = [float(r['result']['point']['x']), float(r['result']['point']['y']), typ]; break
        except Exception: pass
        time.sleep(0.05)
    cache[a] = res; return res
kname = {}
for v in kakao['religion'].values(): kname.setdefault(v['n'].replace(' ', ''), v)
GRP = {'개신교': '기독교(개신교)', '개신교기도원': '기도원·수도원', '불교': '불교', '천주교': '천주교', '천도교': '천도교', '천리교': '천리교', '원불교': '원불교'}
rows = list(csv.DictReader(open(RAW / 'C-S3-20250206-경주시-종교시설현황-v1.csv', encoding='utf-8-sig')))
feats = []; n_geo = n_kak = n_miss = 0
SRC_R = '경상북도 경주시 종교시설현황 2025-02-06 (공공데이터포털 파일, T2) · 좌표 V-World 지오코더'
for r in rows:
    name = r['시설명'].strip(); addr = r['소재지(주소)'].strip(); grp = GRP.get(r['구분'].strip(), r['구분'].strip())
    g = geocode(addr); how = ''
    if g: lon, lat, how = g[0], g[1], 'V-World ' + g[2]; n_geo += 1
    else:
        k = kname.get(name.replace(' ', ''))
        if k: lon, lat, how = k['x'], k['y'], '카카오 동명 시설'; n_kak += 1
        else: n_miss += 1; continue
    dong = addr.replace('경주시 ', '').split(' ')[0]
    feats.append(pt(lon, lat, {'name': name, 'religion': grp, 'kind_raw': r['구분'], 'addr': addr.replace('경주시 ', ''), 'dong': dong, 'phone': r['전화번호'], 'geocode': how, 'source': SRC_R}))
json.dump(cache, open(cache_p, 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(fc(feats), open(PROCESSED / 'poi_religion_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
print('religion', len(rows), '지오코딩', n_geo, '카카오대체', n_kak, '누락', n_miss, Counter(f['properties']['religion'] for f in feats))
miss = [r['시설명'] + ' ' + r['소재지(주소)'] for r in rows if not geocode(r['소재지(주소)']) and not kname.get(r['시설명'].replace(' ', ''))]
print('누락 목록:', miss[:40])
