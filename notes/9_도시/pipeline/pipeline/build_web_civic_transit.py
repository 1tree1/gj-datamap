"""2026-09-21 웹(gj-datamap) 레이어 4종 생성 — 시청 분산 현황 · 철도역·폐선 · 도시재생 PDF 가로망·상권 · 공영주차장.

출력 (archive/C_data/processed/):
  cityhall_sites_4326.geojson   경주시청 본청 부서가 있는 장소 6개소 + 보건소 (시 홈페이지 청사안내 2026-09-02, T1) — V-World 지오코딩
  rail_stations_4326.geojson    구경주역·옛 서경주역(금장)·신 서경주역(하구리)·옛 나원역 (OSM/위키, T4 → 확인 필요)
  rail_lines_4326.geojson       OSM railway=abandoned|disused (폐선) + rail (현행 동해선·중앙선) — 경주 분지 창
  urban_roads_4326.geojson      전략계획(2022) 기초조사 §도심가로망이 이름으로 든 간선·보조간선 → 표준노드링크(nodelink_gj) 링크 선택
  commerce_zones_4326.geojson   전략계획 §상권 분포·중심지 상권 9개 — 도면 없이 서술만 있어 앵커 지점 + 개략 반경(T1 서술, 위치는 근사)
  parking_pub_4326.geojson      전국주차장정보표준데이터(data.go.kr) 경주시 공영·민영 주차장 (T2)
"""
import json, os, ssl, time, urllib.parse, urllib.request, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_env
from shapely.geometry import shape, Point, mapping
from shapely.ops import transform
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'archive/C_data/processed'; RAW = ROOT / 'archive/C_data/raw'
env = load_env(); VK = env.get('VWORLD_KEY'); H = {'Referer': env.get('VWORLD_DOMAIN', ''), 'User-Agent': 'Mozilla/5.0'}
DK = env.get('DATA_GO_KR_KEY')
CTX = ssl.create_default_context()
T4326_5187 = Transformer.from_crs(4326, 5187, always_xy=True).transform
T5187_4326 = Transformer.from_crs(5187, 4326, always_xy=True).transform
fc = lambda feats: {'type': 'FeatureCollection', 'features': feats}
def getj(url, headers=None, data=None, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers or {'User-Agent': 'gjplan/0.1'})
            return json.load(urllib.request.urlopen(req, context=CTX, timeout=120))
        except Exception as e:
            if i == retries - 1: raise
            time.sleep(1.5)
def vgeo(addr):
    import re as _re
    jibun = bool(_re.search(r'[동리읍면]\s+\d', addr)) and not _re.search(r'(로|길)\s*\d', addr)
    for typ in (('PARCEL', 'ROAD') if jibun else ('ROAD', 'PARCEL')):
        try:
            r = getj(f"https://api.vworld.kr/req/address?service=address&request=getcoord&version=2.0&crs=EPSG:4326&type={typ}&address={urllib.parse.quote(addr)}&format=json&key={VK}", H, retries=1)['response']
            if r['status'] == 'OK': return [float(r['result']['point']['x']), float(r['result']['point']['y'])]
        except Exception: pass
    return None

# ---------- 1. 시청 분산 현황 (T1: 시 홈페이지 청사안내 2026-09-02)
SITES = [
    ('시청 본관·신관·별관·증축관', '경주시 양정로 260', '시 소유', '본관(옛 경주군청): 복지정책·총무새마을·노인복지·장애인여성복지·회계·시장실·국장실 6·홍보·디지털정책·문화유산·청렴감사·문화예술·산림경영 / 신관: 건축허가·시민봉사·토지정보·시의회 / 별관: 시금고·세정·징수·식품위생산업·농업유통 / 증축관: 어린이집·정책기획·체육진흥·안전정책·재난상황실·건설·도로·도시계획·교통행정·축산·대외소통·경제정책·환경정책·인구정책·농업정책·알천홀', 30, 'main'),
    ('기린빌딩 2~8층 (민간 임차)', '경주시 양정로 241-1', '민간 임차', '주택과(2F) · 자원순환과·신성장산업과(3F) · 원자력정책과·농촌활력과(4F) · 해양수산과(5F) · 관광컨벤션과(6F) · 철도도심재생과(7F) · 기업투자지원과(8F)', 9, 'lease'),
    ('동원빌딩 2~3층 (민간 임차)', '경주시 소금강로 39', '민간 임차', '전략기획과·미래사업과(2F) · 농촌활력과(3F)', 3, 'lease'),
    ('황룡사 역사문화관 1층', '경주시 임해로 64-19', '시 소유', '왕경조성과', 1, 'branch'),
    ('경주시청소년수련관 1층', '경주시 알천북로 131', '시 소유', '아동청소년과', 1, 'branch'),
    ('경주실내체육관', '경주시 황성공원로 29', '시 소유', '문서고 · 도시공원과 · 경주시 장학회', 1, 'branch'),
    ('경주시보건소 (직속기관, 이전 대상 아님)', '경주시 양정로 300', '시 소유', '보건행정과·건강증진과·지역보건과 — 시청 인접, 시청 이전 시 잔류', 0, 'health'),
]
feats = []
for name, addr, own, depts, n, cls in SITES:
    c = vgeo(addr); print('geocode', name, addr, c)
    if not c: continue
    feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': c},
                  'properties': {'name': name, 'addr': addr, 'own': own, 'depts': depts, 'n_depts': n, 'cls': cls,
                                 'lbl': name.split(' (')[0], 'source': '경주시 홈페이지 청사안내 2026-09-02 (T1) · 좌표 V-World 지오코딩'}})
json.dump(fc(feats), open(PROC / 'cityhall_sites_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)

# ---------- 2. 철도역
ST = [
    ('구경주역 (폐역 2021.12)', 129.2175, 35.8439, '등록문화유산 역사 존치. 원화로 266', 'closed'),
    ('옛 서경주역 (금장, 폐역 2021.12)', 129.2012, 35.8688, '중앙선·동해남부선 분기점. 폐선 트램 북측 종점 후보', 'closed'),
    ('서경주역 (신, 현곡면 하구리)', 129.1809, 35.8847, '2021.12.28 이전 개통. 무궁화 7회·ITX-마음 1왕복·누리로. 일평균 173명(2024)→309명(2025) [T4 나무위키, 철도통계연보로 치환 필요]. 폐선과 2.3~2.7km 이격', 'active'),
    ('불국사역 (폐역 2021.12)', 129.3153, 35.7970, '폐선 트램 남측 종점 후보 (위치 개략)', 'closed'),
]
json.dump(fc([{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [x, y]}, 'properties': {'name': n, 'note': note, 'status': s, 'lbl': n.split(' (')[0], 'source': 'OSM·위키 (T4)'}} for n, x, y, note, s in ST]),
          open(PROC / 'rail_stations_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)

# ---------- 3. 폐선·현행 철도 (OSM Overpass)
q = """[out:json][timeout:120];
(way["railway"~"^(abandoned|disused|razed)$"](35.74,129.08,35.98,129.40);
 way["railway"="rail"](35.74,129.08,35.98,129.40););
out tags geom;"""
d = getj('https://overpass-api.de/api/interpreter', {'User-Agent': 'gjplan/0.1'}, urllib.parse.urlencode({'data': q}).encode())
rf = []
for e in d['elements']:
    if e['type'] != 'way' or not e.get('geometry'): continue
    t = e.get('tags', {}); rw = t.get('railway')
    cls = 'active' if rw == 'rail' else 'abandoned'
    rf.append({'type': 'Feature', 'geometry': {'type': 'LineString', 'coordinates': [[p['lon'], p['lat']] for p in e['geometry']]},
               'properties': {'osm_id': e['id'], 'railway': rw, 'name': t.get('name', ''), 'cls': cls, 'source': 'OSM Overpass 2026-09-21 (T4) — 지형도면 1~10·13~15장 벡터화로 T1 치환 예정'}})
json.dump(fc(rf), open(PROC / 'rail_lines_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
print('rail lines', len(rf), 'abandoned', sum(1 for f in rf if f['properties']['cls'] == 'abandoned'))

# ---------- 4. 전략계획 §도심가로망 간선·보조간선 → nodelink
ROADS = {'간선(동서)': ['태종로'], '간선(남북)': ['원화로', '강변로', '서라벌대로', '산업로'], '보조간선': ['포석로', '일정로', '용당로', '알천남로', '알천북로']}
nl = json.load(open(PROC / 'nodelink_gj_4326.geojson', encoding='utf-8'))
uf = []
for f in nl['features']:
    nm = (f['properties'].get('ROAD_NAME') or '').strip()
    for cls, names in ROADS.items():
        if nm in names:
            uf.append({'type': 'Feature', 'geometry': f['geometry'], 'properties': {'name': nm, 'cls': cls, 'lanes': f['properties'].get('LANES'), 'road_no': f['properties'].get('ROAD_NO'),
                                                                                  'source': '경주시 도시재생전략계획(변경, 2022) 기초조사 §2) 도심 가로망 서술(T1) — 도로명으로 표준노드링크 선택. 국도4호선(건천~도심~보문)은 노선번호로 별도 표시 없음'}})
json.dump(fc(uf), open(PROC / 'urban_roads_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
print('urban roads', len(uf), {c: sum(1 for f in uf if f['properties']['cls'] == c) for c in ROADS})

# ---------- 5. 상권 (전략계획 §3 상권 분포 + 중심지 상권분석 — 서술 기반 앵커)
CZ = [
    ('전통상권 (역전중심·성동시장)', '경주시 원화로 281번길 11-11', 250, '경주역 앞 자연발생 역전중심상권. 전통시장 중심 주민 자족 경제활동', 'trad'),
    ('경주중심상권 (원도심 최대)', '경주시 금성로 295', 400, '시내 상권+도심 관광인프라 복합. 경주역·전통시장·봉황로 문화의거리', 'center'),
    ('시청주변 상권 (동천동)', '경주시 양정로 260', 350, '시청사 이전으로 급속 형성. 저녁 혼잡, 상권안정성 낮고 출점 경쟁 높은 과밀 경쟁', 'cityhall'),
    ('첨성로 일대 관광상권', '경주시 첨성로 125', 300, '관광지 중심. 문화관광명소 따라 발달, 관광객 대상 음식점 특화', 'tour'),
    ('관광상권 (황리단길·황남시장·쌈밥거리)', '경주시 포석로 1080', 300, '관광객 최다 이용. 젊은 층 선호, 음식점·게스트하우스 밀집', 'tour'),
    ('도심배후상권 (구 대학로)', '경주시 동대로 123', 300, '동국대 구 대학로. 기존 주민 유출로 외국인 근로자 이용 높음', 'back'),
    ('동천근린상권', '경주시 백률로 53번길 27', 250, '중심지 상권분석 ④ (원문 서술 부족 — 위치 근사)', 'nbhd'),
    ('황성동 근린상권', '경주시 황성로 62', 300, '공동주택 중심. 개폐업 빈도 낮은 안정 상권. 도로·주차장 협소', 'nbhd'),
    ('용강동 근린상권', '경주시 용담로 90', 300, '아파트 밀집 근린상권. 도로 폭 좁고 주차장 부족', 'nbhd'),
]
cf = []
for name, addr, r, note, cls in CZ:
    c = vgeo(addr); print('geocode', name, c)
    if not c: continue
    g = transform(T5187_4326, Point(T4326_5187(*c)).buffer(r))
    cf.append({'type': 'Feature', 'geometry': mapping(g), 'properties': {'name': name, 'cls': cls, 'r_m': r, 'note': note, 'lbl': name.split(' (')[0],
                                                                        'source': '전략계획(2022) 기초조사 §3 상권 분포·중심지 상권분석 서술(T1). 도면 없음 → 앵커 주소 지오코딩 + 개략 반경 (경계는 근사)'}})
json.dump(fc(cf), open(PROC / 'commerce_zones_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)

# ---------- 6. 공영주차장 (경주시시설관리공단 교통운영 시설안내, 2026-09-21 열람, T2) + 시청사공영주차장(시 홈페이지)
PK = [
    ('제1공영주차장', '경주시 노동동 183', 198, 5590, '09:00~20:00'),
    ('제2공영주차장', '경주시 원효로 145-3', 78, 1944, '09:00~20:00'),
    ('성동시장공영주차장', '경주시 성동동 396-4', 221, 5902, '07:00~21:00 (첫째·셋째 일요일 휴무)'),
    ('중심상가공영주차장', '경주시 황오동 244', 209, 3515, '09:00~21:00'),
    ('시청사공영주차장', '경주시 양정로 260', None, None, '09:00~19:00 (주말 무료)'),
    ('경주역공영주차장 (신경주역)', '경주시 건천읍 화천리 1354-1', 566, 28623, '07:00~24:00'),
    ('성건동 공영주차장', '경주시 성건동 374-40', 25, 804, '09:00~18:00'),
    ('터미널옆공영주차장', '경주시 태종로685번길 9', 15, 1184, '24시간'),
    ('동천동 공영주차장 (보건소 뒤)', '경주시 백률로 53번길 27', 240, 5438, '평일 09:00~20:00 (주말 휴무)'),
    ('대릉원(황남지구)공영주차장', '경주시 황남동 165-5', 181, 7348, '09:00~20:00'),
    ('중앙시장 제1공영주차장', '경주시 금성로 295', 30, 1198, '08:00~21:00'),
    ('중앙시장 제2공영주차장', '경주시 화랑로 38번길 9', 63, 2149, '08:00~21:00'),
    ('봉황대공영주차장', '경주시 노동동 12', 95, 3001, '09:00~21:00'),
    ('포석로 공영주차장', '경주시 포석로 1080', 14, 1072, '10:00~18:00'),
    ('황남생활문화센터 공영주차장', '경주시 첨성로 81번길 23', 34, 1419, '10:00~18:00'),
    ('숭문대공영주차장', '경주시 놋전2길 24-43', 69, 2177, '09:00~20:00'),
    ('쪽샘지구임시공영주차장', '경주시 원화로 189-2', 496, 18370, '임시'),
    ('국립경주박물관공영주차장', '경주시 구황동 619', 264, 14000, '09:00~18:00 (임시 무료)'),
]
pf = []
for name, addr, n, a, hrs in PK:
    c = vgeo(addr); print('geocode', name, c)
    if not c: continue
    pf.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': c},
               'properties': {'name': name, 'addr': addr, 'spaces': n, 'area_m2': a, 'hours': hrs, 'lbl': (name.split(' (')[0] + chr(10) + str(n) + '면') if n else name,
                              'source': '경주시시설관리공단 교통운영 시설안내 (gjfmc.or.kr, 2026-09-21 열람, T2) · 좌표 V-World 지오코딩. 노상주차장·민영 제외'}})
json.dump(fc(pf), open(PROC / 'parking_pub_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
print('parking', len(pf), 'spaces', sum(p['properties']['spaces'] or 0 for p in pf))
