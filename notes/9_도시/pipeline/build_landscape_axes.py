"""2030 경주시 경관계획 재정비(2025.04, T1) §4.3 경관축 5종을 지도 벡터로 재구성.

축의 정의(어느 도로·하천·산·철도인가)는 경관계획 원문(pp.186~212)에서, 선형은 OSM(도로·하천·해안·철도·산 정상)에서 가져온다.
경관계획 도면(위치도)은 좌표가 없는 개념도라 직접 벡터화하지 않았다 — 선형은 '해당 자원의 실제 선형'이지 도면의 굵은 화살표가 아니다.

출력 (archive/C_data/processed/):
  landscape_axes_lines_4326.geojson   수변·도로·통경·역사조망·폐철도녹지 축 (LineString)
  landscape_axes_green_4326.geojson   산 녹지경관축 5개 (정상점 2km 완충, 개략)
"""
import json, ssl, sys, io, time, urllib.parse, urllib.request
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from shapely.geometry import shape, Point, mapping, LineString
from shapely.ops import transform
from pyproj import Transformer
ROOT = Path(__file__).resolve().parents[1]; PROC = ROOT / 'archive/C_data/processed'
T4326_5187 = Transformer.from_crs(4326, 5187, always_xy=True).transform
T5187_4326 = Transformer.from_crs(5187, 4326, always_xy=True).transform
CTX = ssl.create_default_context()
BBOX = '35.62,128.95,36.06,129.57'  # 경주시 전역
SRC = '2030 경주시 경관계획 재정비 (2025.04) §4.3 경관축 (T1) — 선형은 OSM (T4)'

def overpass(q):
    for i in range(3):
        try:
            req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=urllib.parse.urlencode({'data': q}).encode(), headers={'User-Agent': 'gjplan/0.1'})
            return json.load(urllib.request.urlopen(req, context=CTX, timeout=180))
        except Exception as e:
            print('overpass retry', i, e); time.sleep(5)
    raise RuntimeError('overpass failed')

def ways(d, keep):
    out = []
    for e in d['elements']:
        if e['type'] != 'way' or not e.get('geometry'): continue
        t = e.get('tags', {}); k = keep(t)
        if k: out.append((k, [[p['lon'], p['lat']] for p in e['geometry']], t))
    return out

feats = []
def add(coords, axis, sub, new, note=''):
    feats.append({'type': 'Feature', 'geometry': {'type': 'LineString', 'coordinates': coords},
                  'properties': {'axis': axis, 'sub': sub, 'new': new, 'lbl': sub, 'note': note, 'source': SRC}})

# ---------- 1. 수변경관축: 형산강·북천·남천·칠평천·대천 + 동해안(해안선)
RIVERS = {'형산강': '형산강 수변경관축', '북천': '북천 수변경관축', '남천': '남천 수변경관축', '칠평천': '칠평천 수변경관축', '대천': '대천 수변경관축'}
d = overpass(f'[out:json][timeout:180];(way["waterway"~"^(river|stream|canal)$"]["name"~"^(형산강|북천|남천|칠평천|대천)$"]({BBOX});way["natural"="coastline"]({BBOX}););out tags geom;')
n = 0
for t, coords, tags in ways(d, lambda t: t.get('name') if t.get('waterway') else ('coast' if t.get('natural') == 'coastline' else None)):
    if t == 'coast': add(coords, '수변경관축', '동해안 수변경관축', False, '해안선(natural=coastline)'); n += 1
    elif t in RIVERS: add(coords, '수변경관축', RIVERS[t], t in ('남천', '대천'), f'OSM waterway {t}'); n += 1
print('수변', n)

# ---------- 2. 도로경관축: 국도 4·7·20·28, 지방도 291(→OSM ref 없을 수 있음), 경부·울산포항(동해)고속도로, 경감로(동해바다로), 형산로(상생로드), 고속철도
d = overpass(f'[out:json][timeout:180];(way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]["ref"~"(^|;)(1|65|4|7|20|28|291)(;|$)"]({BBOX});way["highway"]["name"~"^(경감로|형산로)$"]({BBOX});way["railway"="rail"]["name"~"경부고속"]({BBOX}););out tags geom;')
REFN = {'1': '경부고속도로 경관축', '65': '울산-포항고속도로 경관축', '4': '국도 4호선 경관축', '7': '국도 7호선 경관축', '20': '국도 20호선 경관축', '28': '국도 28호선 경관축', '291': '지방도 291호선 경관축'}
n = 0
for t, coords, tags in ways(d, lambda t: t):
    if tags.get('railway') == 'rail': add(coords, '도로경관축', '고속철도 경관축', True, 'OSM 경부고속선'); n += 1; continue
    nm = tags.get('name', '')
    if nm == '경감로': add(coords, '도로경관축', '동해바다로(경감로) 자전거도로 경관축', False, '자전거도로 경관축'); n += 1; continue
    if nm == '형산로': add(coords, '도로경관축', '상생로드(형산로) 자전거도로 경관축', False, '자전거도로 경관축'); n += 1; continue
    refs = [r.strip() for r in tags.get('ref', '').split(';')]
    hit = next((r for r in refs if r in REFN), None)
    if hit:
        # 고속도로는 motorway만, 국도는 motorway 제외
        if hit in ('1', '65') and tags.get('highway') != 'motorway': continue
        if hit not in ('1', '65') and tags.get('highway') == 'motorway': continue
        add(coords, '도로경관축', REFN[hit], hit == '1' and False, f"OSM ref {tags.get('ref')} {tags.get('highway')}"); n += 1
print('도로', n)

# ---------- 3. 중심시가지 통경축(주통경축) + 역사조망축 — 원도심 도로명
VIEW = ['경감로', '강변로', '임정로', '금성로', '보불로', '계림로', '태종로', '화랑로', '북문로', '동문로', '포석로', '서라벌대로']
HIST = {'양정로': '신라옛길 조망축 (양정로)', '첨성로': '역사유적 조망축 (첨성로)'}
names = '|'.join(VIEW + list(HIST))
d = overpass(f'[out:json][timeout:180];way["highway"]["name"~"^({names})$"](35.76,129.16,35.90,129.37);out tags geom;')
n = 0
for t, coords, tags in ways(d, lambda t: t.get('name')):
    if t in HIST: add(coords, '역사조망축', HIST[t], True, '신라왕경 360방 복원도 기반 통경축 → 역사조망축(신규)'); n += 1
    elif t in VIEW: add(coords, '중심시가지 통경축', f'주통경축 ({t})', False, '주요 경관자원으로의 통경축'); n += 1
print('통경·역사조망', n)
# 북천~보문호(금장대~보문호) 통경축: 북천 선형으로 대표 (금장대 129.196,35.858 → 보문호 129.29,35.85) — 북천 waterway가 이미 수변축이므로 개략 직선
add([[129.196, 35.858], [129.288, 35.851]], '중심시가지 통경축', '금장대~보문호 통경·조망축', False, '개략 직선 — 원문 "금장대~보문호로 이어지는 통경축 및 조망축 보전"')

# ---------- 4. 폐철도 녹지경관축 (무열왕릉~형산강철교~경주역~선덕여고~사천왕사지) — OSM 폐선 중 해당 창
ra = json.load(open(PROC / 'rail_abandoned_4326.geojson', encoding='utf-8'))
n = 0
for f in ra['features']:
    cs = f['geometry']['coordinates']
    if all(129.175 <= x <= 129.245 and 35.815 <= y <= 35.873 for x, y in cs):
        add(cs, '녹지경관축', '폐철도 녹지경관축', True, '무열왕릉~형산강철교~경주역~선덕여고~사천왕사지 (계획 확정구간)'); n += 1
print('폐철도 녹지축', n)

json.dump({'type': 'FeatureCollection', 'features': feats}, open(PROC / 'landscape_axes_lines_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
print('lines total', len(feats))

# ---------- 5. 산 녹지경관축 — 정상점 + 2km 완충(개략)
PEAKS = [('단석산', 129.052, 35.771, False), ('토함산', 129.343, 35.799, False), ('남산 (금오봉)', 129.223, 35.788, False), ('소금강산', 129.229, 35.866, True), ('선도산', 129.181, 35.836, True)]
d = overpass(f'[out:json][timeout:120];node["natural"="peak"]["name"~"^(단석산|토함산|금오봉|고위봉|소금강산|선도산)$"]({BBOX});out;')
got = {e['tags']['name']: (e['lon'], e['lat']) for e in d['elements'] if e['type'] == 'node'}
print('peaks osm', got)
gf = []
for nm, x, y, new in PEAKS:
    key = '금오봉' if nm.startswith('남산') else nm
    if key in got and abs(got[key][0]-x) < 0.05 and abs(got[key][1]-y) < 0.05: x, y = got[key]  # 동명이산(선도산 등) 방지: 3km 이내만 채택
    g = transform(T5187_4326, Point(T4326_5187(x, y)).buffer(2000))
    gf.append({'type': 'Feature', 'geometry': mapping(g), 'properties': {'axis': '녹지경관축', 'sub': f'{nm} 녹지경관축', 'new': new, 'lbl': f'{nm} 녹지축', 'peak': [x, y],
                                                                        'note': '정상점 기준 반경 2km 개략 — 경관계획 위치도는 능선을 따르는 개념 화살표', 'source': SRC + ' · 정상점 OSM natural=peak'}})
json.dump({'type': 'FeatureCollection', 'features': gf}, open(PROC / 'landscape_axes_green_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
print('green', len(gf))
