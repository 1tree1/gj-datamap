# 구경주역 부지 도로계획 — 입력 데이터 패키지 생성
# 산출: road_data.json (EPSG:5187, 미터). 부지 경계는 사용자가 그린 파란선(캡처 2.png)을 수치지도에 정합한 것.
import json, sys
import numpy as np
import shapefile
from pyproj import Transformer
from shapely.geometry import shape, Point, LineString, Polygon, box, mapping
from shapely.ops import transform, unary_union
from shapely.strtree import STRtree

ROOT = r'C:/Users/User/Desktop/9_도시/'
SP = r'C:/Users/User/AppData/Local/Temp/claude/C--Users-User-Desktop-9---/37a37839-edd8-483b-a0d8-c2e88f5eb82a/scratchpad/'
OUT = ROOT + 'work/road_plan/road_data.json'
R = 800.0   # 부지 경계에서 이 반경 안의 링크만 취급 (요청은 500m, 여유를 두고 뽑은 뒤 500m로 자름)

t86_87 = Transformer.from_crs(5186, 5187, always_xy=True).transform
t79_87 = Transformer.from_crs(5179, 5187, always_xy=True).transform
t84_87 = Transformer.from_crs(4326, 5187, always_xy=True).transform

SITE = ROOT + 'work/road_plan/site_v2_5187.geojson'   # 라이노 v2 '내가 하고자하는 경계라인' 레이어 → EPSG:5187 (벡터라 굵기 보정 없음)
site = shape(json.load(open(SITE, encoding='utf8'))['geometry'])
site = max(site.geoms, key=lambda g: g.area) if site.geom_type == 'MultiPolygon' else site
win = site.buffer(R)
print('site area', round(site.area), 'bounds', [round(v) for v in site.bounds])

# ---- 표준노드링크 (5186) ----
def fix(s):
    try: return s.encode('latin-1').decode('cp949')
    except Exception: return s
NL = SP + 'nl/'
rl = shapefile.Reader(NL + 'MOCT_LINK.shp', encoding='latin-1')
links = []
minx, miny, maxx, maxy = win.bounds
inv = Transformer.from_crs(5187, 5186, always_xy=True).transform
wx0, wy0 = inv(minx, miny); wx1, wy1 = inv(maxx, maxy)
for sr in rl.iterShapeRecords():
    x0, y0, x1, y1 = sr.shape.bbox
    if x1 < wx0 - 50 or x0 > wx1 + 50 or y1 < wy0 - 50 or y0 > wy1 + 50: continue
    pts = [t86_87(x, y) for x, y in sr.shape.points]
    ls = LineString(pts)
    if not ls.intersects(win): continue
    rec = sr.record.as_dict()
    links.append(dict(id=rec['LINK_ID'], f=rec['F_NODE'], t=rec['T_NODE'], lanes=rec['LANES'], rank=rec['ROAD_RANK'],
                      name=fix(rec['ROAD_NAME']), spd=rec['MAX_SPD'], len=ls.length, geom=ls,
                      use=rec['ROAD_USE'], connect=rec['CONNECT']))
print('links', len(links))

# ---- 노드 (이름, 회전제한 플래그) ----
rn = shapefile.Reader(NL + 'MOCT_NODE.shp', encoding='latin-1')
need = set(l['f'] for l in links) | set(l['t'] for l in links)
nodes = {}
for sr in rn.iterShapeRecords():
    rec = sr.record.as_dict()
    if rec['NODE_ID'] in need:
        x, y = t86_87(*sr.shape.points[0])
        nodes[rec['NODE_ID']] = dict(x=x, y=y, type=rec['NODE_TYPE'], name=fix(rec['NODE_NAME']), turn_p=rec['TURN_P'])
print('nodes', len(nodes))

rt = shapefile.Reader(NL + 'TURNINFO.dbf', encoding='latin-1')
turns = []
for rec in rt.iterRecords():
    d = rec.as_dict()
    if d['NODE_ID'] in nodes:
        turns.append(dict(node=d['NODE_ID'], st=d['ST_LINK'], ed=d['ED_LINK'], type=d['TURN_TYPE'], oper=d['TURN_OPER']))
print('turns', len(turns))

# ---- 시간대별 속도 (2024–2025 평일/주말 이력) ----
H = json.load(open(ROOT + 'archive/C_data/processed/traffic_hist_links_4326.geojson', encoding='utf8'))
hist = {}
for f in H['features']:
    p = f['properties']
    hist[p['LINK_ID']] = dict(wd=[p.get('wd_%02d' % h) for h in range(24)], we=[p.get('we_%02d' % h) for h in range(24)],
                              n=p.get('n_obs_hist'), thr_c=p.get('thr_c'), thr_f=p.get('thr_f'))

# ---- 도로폭: 수치지도 도로면(N3A_A0010000)에서 링크 직각 절단 ----
ra = shapefile.Reader(ROOT + '대지/(B020)연속수치지도_202609132098/N3A_A0010000.shp')
polys = []
for s in ra.shapes():
    pts = [t79_87(x, y) for x, y in s.points]
    parts = list(s.parts) + [len(pts)]
    rings = [pts[a:b] for a, b in zip(parts, parts[1:]) if b - a >= 4]
    if not rings: continue
    g = Polygon(rings[0])
    if g.is_valid and g.intersects(win): polys.append(g)
    elif not g.is_valid:
        g = g.buffer(0)
        if g.intersects(win): polys.append(g)
road_area = unary_union(polys)
print('road polys', len(polys))

def width_at(ls, frac):
    p = ls.interpolate(frac, normalized=True)
    q1 = ls.interpolate(max(frac - 0.02, 0), normalized=True); q2 = ls.interpolate(min(frac + 0.02, 1), normalized=True)
    dx, dy = q2.x - q1.x, q2.y - q1.y
    n = (dx * dx + dy * dy) ** 0.5
    if n < 1e-6: return None
    nx, ny = -dy / n, dx / n
    cut = LineString([(p.x - nx * 25, p.y - ny * 25), (p.x + nx * 25, p.y + ny * 25)])
    inter = road_area.intersection(cut)
    segs = [inter] if inter.geom_type == 'LineString' else [g for g in getattr(inter, 'geoms', []) if g.geom_type == 'LineString']
    best = None
    for sg in segs:
        if sg.distance(p) < 1.5:
            best = sg.length if best is None else max(best, sg.length)
    return best

for l in links:
    ws = [w for w in (width_at(l['geom'], f) for f in (0.25, 0.5, 0.75)) if w]
    l['width'] = float(np.median(ws)) if ws else None
    h = hist.get(l['id'])
    l['hist'] = h

# ---- 정류장 ----
B = json.load(open(ROOT + 'archive/C_data/raw/busstops_gj.geojson', encoding='utf8'))
stops = []
for f in B['features']:
    x, y = t84_87(*f['geometry']['coordinates'])
    if Point(x, y).distance(site) <= 700:
        stops.append(dict(x=x, y=y, name=f['properties']['name'], no=f['properties'].get('short_no')))
print('stops', len(stops))

# ---- 목적지 ----
tour = json.load(open(ROOT + 'archive/C_data/raw/gj_tour_sites.geojson', encoding='utf8'))
want = ['황리단길', '대릉원', '첨성대', '월정교', '동궁과 월지', '황룡사지', '황룡사역사문화관', '국립경주박물관', '교촌마을', '봉황대',
        '천마총', '성동시장', '노서동 고분군', '경주 월성', '경주 계림', '경주읍성', '중앙시장 야시장', '오릉', '분황사']
dest = {}
for f in tour['features']:
    n = f['properties']['name'].strip()
    if n in want:
        dest[n] = dict(x=t84_87(*f['geometry']['coordinates'])[0], y=t84_87(*f['geometry']['coordinates'])[1], kind='관광·유적')
pn = json.load(open(ROOT + 'archive/C_data/processed/plan_nodes_4326.geojson', encoding='utf8'))
for f in pn['features']:
    n = f['properties']['name']
    if n in ('시외버스터미널', '신경주역(KTX)', '고속버스터미널', '서경주역', '팔우정삼거리'):
        dest[n] = dict(x=t84_87(*f['geometry']['coordinates'])[0], y=t84_87(*f['geometry']['coordinates'])[1], kind='교통결절')
tc = json.load(open(ROOT + 'archive/C_data/processed/tourism_complex_4326.geojson', encoding='utf8'))
for f in tc['features']:
    if f['properties']['name'] == '보문관광단지':
        g = transform(t84_87, shape(f['geometry']))
        c = g.representative_point()
        dest['보문관광단지(대표점)'] = dict(x=c.x, y=c.y, kind='관광단지')
        dest['보문관광단지(대표점)']['note'] = '다각형 850ha의 대표점. 실제 진입 게이트는 미확정'
gate = json.load(open(ROOT + 'archive/C_data/processed/gateways_4326.geojson', encoding='utf8'))
for f in gate['features']:
    if f['properties']['name'] in ('경주IC', '건천IC'):
        dest[f['properties']['name']] = dict(x=t84_87(*f['geometry']['coordinates'])[0], y=t84_87(*f['geometry']['coordinates'])[1], kind='고속도로 IC')

def ser(l):
    return dict(id=l['id'], f=l['f'], t=l['t'], lanes=l['lanes'], rank=l['rank'], name=l['name'], spd=l['spd'], len=round(l['len'], 1),
                width=None if l['width'] is None else round(l['width'], 1), hist=l['hist'],
                dist_site=round(l['geom'].distance(site), 1), xy=[[round(x, 2), round(y, 2)] for x, y in l['geom'].coords])
out = dict(site=[[round(x, 2), round(y, 2)] for x, y in site.exterior.coords],
           site_area=site.area,
           links=[ser(l) for l in links], nodes=nodes, turns=turns, stops=stops, dest=dest,
           road_polys=[[[round(x, 1), round(y, 1)] for x, y in g.exterior.coords] for g in polys if g.distance(site) < 600 and g.area > 30])
json.dump(out, open(OUT, 'w', encoding='utf8'), ensure_ascii=False)
print('wrote', OUT, len(out['links']), 'links', len(out['road_polys']), 'road polys')
