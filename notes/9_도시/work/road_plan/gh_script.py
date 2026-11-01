"""구경주역 도로계획 시각화 (GH Python 3)
입력  day(0 평일/1 주말) hour(6~22) wid(연결가로 폭 m) mode(0 = 최종콘타모델_v2 반축척 모형좌표에 겹침 / 1 = EPSG:5187 국소좌표, 미터)
출력  각 출력은 Custom Preview로 색을 입힌다.
"""
import json, math, os
import Rhino.Geometry as rg

WD = r'C:/Users/User/Desktop/9_도시/work/road_plan/'
ORG = (219780.0, 360990.0)

def _load():
    g = globals()
    if '_CACHE' not in g or g['_CACHE'] is None:
        R = json.load(open(WD + 'road_result.json', encoding='utf8'))
        P = json.load(open(WD + 'plan.json', encoding='utf8'))
        D = json.load(open(WD + 'road_data.json', encoding='utf8'))
        T = json.load(open(WD + 'v2_transform.json', encoding='utf8'))
        K = json.load(open(WD + 'blocks.json', encoding='utf8'))
        g['_CACHE'] = (R, P, D, T, K)
    return g['_CACHE']

R, P, D, T, K = _load()
day = 0 if day is None else int(day)
hour = 18 if hour is None else int(hour)
hour = max(6, min(22, hour))
wid = 12.0 if wid is None else float(wid)
mode = 0 if mode is None else int(mode)
dk = 'wd' if day == 0 else 'we'

# 좌표 변환: mode 0 은 v2 모형(= C + 0.5*(5179 - C), 5179 는 5187 의 국소 아핀), z 는 모형 지반(≈256.5) 위
S = 0.5 if mode == 0 else 1.0          # 길이 축척 (반지름·폭·글자에도 적용)
Z0 = 258.0 if mode == 0 else 0.0
def pt(x, y, z=0.0):
    if mode == 0:
        ax, ay, C = T['ax'], T['ay'], T['C']
        X = ax[0] * x + ax[1] * y + ax[2]; Y = ay[0] * x + ay[1] * y + ay[2]
        return rg.Point3d(C[0] + 0.5 * (X - C[0]), C[1] + 0.5 * (Y - C[1]), Z0 + z * S)
    return rg.Point3d(x - ORG[0], y - ORG[1], z)

def pl(coords, closed=False, z=0.0):
    pts = [pt(x, y, z) for x, y in coords]
    if closed and (pts[0].DistanceTo(pts[-1]) > 1e-6): pts.append(pts[0])
    return rg.PolylineCurve(pts)

def disc(x, y, r, z=0.0):
    c = rg.Circle(rg.Plane(pt(x, y, z), rg.Vector3d.ZAxis), r * S).ToNurbsCurve()
    b = rg.Brep.CreatePlanarBreps(c, 0.01)
    return b[0] if b else None

def pp(c, r):
    """곡선을 반지름 r(m)의 파이프로 — 미리보기 굵기용"""
    if c is None: return None
    b = rg.Brep.CreatePipe(c, r * S, False, rg.PipeCapMode.Flat, True, 0.05, 0.05)
    return b[0] if b else None

def pps(cs, r):
    return [x for x in (pp(c, r) for c in cs) if x is not None]

def offset_line(a, b, d):
    v = rg.Vector3d(b.X - a.X, b.Y - a.Y, 0); v.Unitize()
    n = rg.Vector3d(-v.Y, v.X, 0) * d * S
    return rg.Line(a + n, b + n)

# ---------- 배경 / 부지 ----------
site = pps([pl(R['site'], True, 0.3)], 1.6)
bg = [pl(p, True, -0.2) for p in D['road_polys'] if len(p) > 3]

# ---------- 링크: 선택한 시간대 속도로 3단계 ----------
lk_free, lk_slow, lk_jam, lk_nodata, lk_insite = [], [], [], [], []
lk_rows = []
for l in R['disp']:
    c = pl(l['xy'], False, 0.6)
    if l['in_site']:
        lk_insite.append(c); continue
    if l['imputed']:
        lk_nodata.append(c); continue
    ser = l[dk]
    ff = sorted(l['wd'] + l['we'])[int(0.9 * 47)]
    ratio = ser[hour] / ff if ff > 0 else 1.0
    (lk_free if ratio >= 0.80 else lk_slow if ratio >= 0.60 else lk_jam).append(c)
    if l['name'] in ('원화로',) and len(lk_rows) < 1:
        lk_rows.append((l['name'], ser[hour], ff, ratio))

lk_free, lk_slow, lk_jam, lk_nodata, lk_insite = [pps(v, r) for v, r in ((lk_free, 0.9), (lk_slow, 0.9), (lk_jam, 0.9), (lk_nodata, 0.5), (lk_insite, 1.0))]

# ---------- 진입 후보 ----------
cand_par, cand_oth = [], []
for c in R['cands']:
    r = 4.0 + 0.5 * c['wins']
    b = disc(c['x'], c['y'], r, 0.8)
    if b is None: continue
    (cand_par if c['pareto_wd18'] else cand_oth).append(b)
ent_main = [disc(P['R1']['x'], P['R1']['y'], 16, 1.2)]
ent_sub = [disc(P['R2']['x'], P['R2']['y'], 12, 1.2)]

stops = [d for d in (disc(s['x'], s['y'], 3.0, 0.9) for s in R['stops']) if d]
turns = []
for t in R['turns']:
    n = R['nodes'].get(t['node'])
    if n: turns.append(disc(n['x'], n['y'], 3.5, 1.0))
turns = [t for t in turns if t]

# ---------- 동서 연결 ----------
ew_alt = [rg.LineCurve(pt(p['wx'], p['wy'], 0.5), pt(p['ex'], p['ey'], 0.5)) for p in R['ew_pairs'] if p.get('pareto')][:14]
A, B = P['A'], P['B']
ew_A = pps([rg.LineCurve(pt(A['wx'], A['wy'], 1.0), pt(A['ex'], A['ey'], 1.0))], 1.4)
ew_B = pps([rg.LineCurve(pt(B['wx'], B['wy'], 1.0), pt(B['ex'], B['ey'], 1.0))], 1.4)

# ---------- 부지 내 도로계획 (연결가로 A 폭 = wid, B는 wid*0.75, 종축 보행·서비스 6m) ----------
plan_A, plan_B, plan_spine, plan_R2 = [], [], [], []
def edges(a, b, w):
    out = []
    for s in (+1, -1):
        out.append(offset_line(a, b, s * w / 2.0).ToNurbsCurve())
    return out
a0, a1 = pt(A['wx'], A['wy'], 1.5), pt(A['ex'], A['ey'], 1.5)
plan_A += edges(a0, a1, wid) + [rg.LineCurve(a0, a1)]
b0, b1 = pt(B['wx'], B['wy'], 1.5), pt(B['ex'], B['ey'], 1.5)
plan_B += edges(b0, b1, wid * 0.75)
sp = [(x, y) for x, y, w in P['spine']]
plan_spine.append(pl(sp, False, 1.5))
r2 = pt(P['R2']['x'], P['R2']['y'], 1.5)
spN = pt(*sp[-1], 1.5)
plan_R2.append(rg.LineCurve(r2, spN))

plan_A = pps(plan_A, 0.8); plan_B = pps(plan_B, 0.7); plan_spine = pps(plan_spine, 1.8); plan_R2 = pps(plan_R2, 1.6)

# ---------- 블록 계획 (blocks.json) ----------
def geo_rings(gm):
    if gm['type'] == 'Polygon': return [gm['coordinates'][0]]
    if gm['type'] == 'MultiPolygon': return [p[0] for p in gm['coordinates']]
    return []
def poly_brep(ring, z):
    c = pl([(q[0], q[1]) for q in ring], True, z)
    b = rg.Brep.CreatePlanarBreps(c, 0.05)
    return b[0] if b else None
use_out = {'공공청사': [], '주차장': [], '주거': [], '근린생활': [], '문화': [], '공공시설': [], '광장': []}
blk_tag_pt, blk_tag_txt = [], []
for b in K['blocks']:
    for ring in geo_rings(b['geom']):
        br = poly_brep(ring, 0.2)
        if br is not None and b['use'] in use_out: use_out[b['use']].append(br)
    if b['area'] >= 1500:
        extra = ' {}세대'.format(b['units']) if b.get('units') else (' {}면'.format(b['spaces']) if b.get('spaces') else '')
        blk_tag_pt.append(pt(b['cx'], b['cy'], 25)); blk_tag_txt.append('{}\n{:,}㎡ {}F/{}m{}'.format(b['prog'], b['area'], b['floors'], b['h_max'], extra))
blk_civic, blk_park, blk_house, blk_retail, blk_culture, blk_public, blk_plaza = (use_out[k] for k in ('공공청사', '주차장', '주거', '근린생활', '문화', '공공시설', '광장'))
rd_plan = [x for x in (poly_brep(ring, 0.28) for v in K['roads'].values() for ring in geo_rings(v['geom'])) if x is not None]
grn = [x for x in (poly_brep(ring, 0.24) for ring in geo_rings(K['green'])) if x is not None]
ped_plan = pps([pl([(q[0], q[1]) for q in p['line']], False, 0.6) for p in K.get('ped', [])], 2.0)
plaza = [x for x in (poly_brep(ring, 0.3) for ring in geo_rings(K['plaza'])) if x is not None] if K.get('plaza') else []
station_new = [x for x in (poly_brep(ring, 0.35) for ring in geo_rings(K['station_new'])) if x is not None] if K.get('station_new') else []
if K.get('plaza'):
    ring = geo_rings(K['plaza'])[0]; cxp = sum(q[0] for q in ring) / len(ring); cyp = sum(q[1] for q in ring) / len(ring)
    blk_tag_pt.append(pt(cxp, cyp, 26)); blk_tag_txt.append('역전광장 (성동시장 정면)')
if K.get('station_new'):
    ring = geo_rings(K['station_new'])[0]; cxs = sum(q[0] for q in ring) / len(ring); cys = sum(q[1] for q in ring) / len(ring)
    blk_tag_pt.append(pt(cxs, cys, 26)); blk_tag_txt.append('구 역사 이축')
cw_new = [d for d in (disc(c['x'], c['y'], 5.0, 1.3) for c in K['cw_new']) if d]
stop_new = [d for d in (disc(s['x'], s['y'], 4.5, 1.3) for s in K['stops_new']) if d]
blk_tag_pl = [rg.Plane(p, rg.Vector3d.ZAxis) for p in blk_tag_pt]

# ---------- 라벨 ----------
tag_pt, tag_txt = [], []
def tag(x, y, s, z=30.0):
    tag_pt.append(pt(x, y, z)); tag_txt.append(s)
tag(P['R1']['x'], P['R1']['y'], 'R1 주진입 ({})'.format(P['R1']['road']), 40)
tag(P['R2']['x'], P['R2']['y'], 'R2 보조진입 ({})'.format(P['R2']['road']), 40)
tag((A['wx'] + A['ex']) / 2, (A['wy'] + A['ey']) / 2, 'A 동서연결: {}↔{} ({:.0f}m)'.format(A['wname'], A['ename'], A['length']), 40)
tag((B['wx'] + B['ex']) / 2, (B['wy'] + B['ey']) / 2, 'B 동서연결: {}↔{} ({:.0f}m)'.format(B['wname'], B['ename'], B['length']), 40)
seen = set()
for l in R['disp']:
    if l['name'] in ('원화로', '알천남로', '화랑로', '원효로', '북성로', '동성로', '양정로', '북문로', '양정로98번길', '태종로', '동문로', '계림로', '북정로') and l['name'] not in seen and not l['in_site']:
        xy = l['xy'][len(l['xy']) // 2]
        seen.add(l['name']); tag(xy[0], xy[1], l['name'], 15)
tag_pl = [rg.Plane(p, rg.Vector3d.ZAxis) for p in tag_pt]

# ---------- 보고서 ----------
bucket = 'wd08' if hour < 10 else 'wd12' if hour < 15 else 'wd18'
if day == 1: bucket = bucket.replace('wd', 'we')
c1 = min(R['cands'], key=lambda c: math.hypot(c['x'] - P['R1']['x'], c['y'] - P['R1']['y']))
c2 = min(R['cands'], key=lambda c: math.hypot(c['x'] - P['R2']['x'], c['y'] - P['R2']['y']))
def acc_txt(c):
    a = c['acc'].get(bucket)
    return ' / '.join('{} {:.1f}분'.format(k, v / 60.0) for k, v in a.items()) if a else '-'
lines = []
lines.append('시나리오: {} {:02d}시  (표시 속도: 2024-25 표준노드링크 시간대 속도 이력)'.format('평일' if day == 0 else '주말', hour))
lines.append('')
rank_nm = {'101': '고속도로', '102': '도시고속', '103': '국도', '104': '특별광역시도', '105': '국가지원지방도', '106': '지방도', '107': '시군도'}
lines.append('[R1 주진입] {} ({} {}, {}차로, 폭 {}m). {}개 시나리오 중 {}회 1위 · 최근접 교차로 "{}"로 {:.0f}m 스냅 · A 서단과 {:.0f}m'.format(
    P['R1']['road'], rank_nm.get(c1['rank'], c1['rank']), c1['rank'], c1['lanes'], c1['width'], P['R1']['n_scen'], P['R1']['wins'], P['R1'].get('snap_node', ''), P['R1']['moved_m'], P['R1'].get('dist_to_A_west', 0)))
lines.append('  이 시각 링크 속도 {:.0f} km/h · 150m 내 정류장 {}곳 · 최근접 교차로 {:.0f}m · 회전제한 기록 {}'.format(c1['spd'].get('{}{:02d}'.format(dk, hour), 0), c1['bus'], c1['dnode'], c1['turns'] or '없음'))
if '지하' in (P['R1'].get('snap_node') or ''):
    lines.append('  ⚠ 스냅된 노드가 지하차도 접속부("{}"). 램프·옹벽과 상충 가능 → 실제 진입구는 A 서단(화랑로 교차로)으로 두고 이 지점은 보행·비상 진입으로 낮추는 안을 병기'.format(P['R1']['snap_node']))
lines.append('  접근시간(부지 진입점까지): ' + acc_txt(c1))
lines.append('[R2 보조진입] {} ({} {}, {}차로, 폭 {}m). {}'.format(P['R2']['road'], rank_nm.get(c2['rank'], c2['rank']), c2['rank'], c2['lanes'], c2['width'],
    '기준 6개 중 파레토 비지배' if P['R2'].get('pareto') else '파레토 지배됨 — 위치 대안 필요'))
lines.append('  이 시각 링크 속도 {:.0f} km/h · 접근시간: {}'.format(c2['spd'].get('{}{:02d}'.format(dk, hour), 0), acc_txt(c2)))
lines.append('')
lines.append('[A 동서연결] {}↔{}  길이 {:.0f}m (부지 내 {:.0f}m) · 양측 가로와 편차 {:.0f}°/{:.0f}° · 현재 우회 대비 {:.1f}배 · 단축 {:.0f}초'.format(A['wname'], A['ename'], A['length'], A['inside'], A['align_w'], A['align_e'], A['detour_old'] or 0, A['gain']))
lines.append('[B 동서연결] {}↔{}  길이 {:.0f}m (부지 내 {:.0f}m) · 편차 {:.0f}°/{:.0f}° · 우회 {:.1f}배 · 단축 {:.0f}초'.format(B['wname'], B['ename'], B['length'], B['inside'], B['align_w'], B['align_e'], B['detour_old'] or 0, B['gain']))
g = P['gaps']
lines.append('차량 횡단 간격(부지 장축 {:.0f}m): 현재 {} → A {} → A+B {}'.format(P['axis_len'], [round(v) for v in g['before']], [round(v) for v in g['with_A']], [round(v) for v in g['with_A_B']]))
lines.append('※ 경계 안은 비어 있다고 보고 계산했다 (내부 기존 소로는 그래프·접도 후보에서 제거).')
lines.append('')
lines.append('[블록 계획 — 토지이용 (부지 {:,}㎡)]'.format(K['site_area']))
for k, t in K['table'].items():
    ex = ' · {}세대'.format(t['units']) if t['units'] else (' · {}면'.format(t['spaces']) if t['spaces'] else '')
    lines.append('  {:<22s} {:>7,}㎡ {:>5.1f}%  {}F/{}m  연면적 {:>7,}{}'.format(k, t['area'], 100.0 * t['area'] / K['site_area'], t['floors'], t['h_max'], t['gfa'], ex))
lines.append('  {:<22s} {:>7,}㎡ {:>5.1f}%'.format('도로(A·B·C·종축·R2)', K['road_area'], 100.0 * K['road_area'] / K['site_area']))
lines.append('  {:<22s} {:>7,}㎡ {:>5.1f}%   합계 {:,}㎡ (= 부지)'.format('선형공원(종축 양측)', K['green_area'], 100.0 * K['green_area'] / K['site_area'], K['total']))
lines.append('  C 동서연결: {} — {}'.format(K['C']['ename'], K['C'].get('note', '')))
if K.get('station'): lines.append('  구 역사: ' + K['station']['note'])
lines.append('[횡단보도 신설 {}곳 — 자료 없음(수치지도 A004 미포함)이라 교차로·정류장·광장축에서 도출]'.format(len(K['cw_new'])))
for c in K['cw_new']: lines.append('  · {} [{}] {}'.format(c['road'], c['kind'], c['why']))
lines.append('[정류장] 기존 {}곳 유지(BIS) + 신설 {}곳'.format(len(K['stops_keep']), len(K['stops_new'])))
for s in K['stops_new']: lines.append('  · {}: {}'.format(s['road'], s['why']))
lines.append('[가정] ' + ' / '.join(K['assumptions']))
lines.append('')
lines.append('범례  링크: 초록=원활(자체 90분위 속도의 80%+) · 주황=서행(60~80%) · 빨강=지체(<60%) · 회색=속도 이력 없음 · 보라 굵은선=부지 내 기존 소로(양정로)')
lines.append('      점: 주황=R1 · 노랑=R2 · 청록=비지배 후보 · 연분홍=지배 후보 · 자주=버스정류장 · 노랑작은점=회전제한 기록')
lines.append('      선: 초록=A(추천 동서연결) · 하늘=B · 연초록 얇은선=그 밖의 비지배 조합 · 파랑=부지 경계')
lines.append('')
lines.append('※ 시내도로 교통량(대/시), 차종별·방향별 통행량, 버스 노선 방향, U턴·좌우회전 허용 위치는 자료 없음. 속도만 있고 회전제한은 표준노드링크 TURNINFO 41건(코드 의미 미확인).')
lines.append('※ 링크 방향 정보 없음 → 무방향 그래프. 이력 속도가 없는 링크는 제한속도의 50%로 대체(회색 점선).')
lines.append('※ 매장문화재 유존 범위 미반영 — 계획선 위치는 시굴조사 전 가안.')
report = '\n'.join(lines)
