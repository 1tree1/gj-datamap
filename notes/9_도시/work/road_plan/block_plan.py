# 구경주역 부지 도로·블록 계획 (규칙 기반) — plan.json/road_result.json/context.json → blocks.json + 토지이용계획표 CSV
# 방향: 정주인구 중점 · 원도심 공동화 극복 · 고도지구(20m/15m) · 지하 소극적(최대 B2, 계획은 B1 한 곳만)
# 프로그램: 경주시청 · 주차장 · 청년주거 · 근린생활 · 역사헤리티지관 · 문화프로그램 · 주민지원시설 · 체육센터
import json, math, csv
import numpy as np
from shapely.geometry import Polygon, LineString, Point, MultiPolygon, shape, mapping
from shapely.ops import unary_union, split, polygonize

WD = r'C:/Users/User/Desktop/9_도시/work/road_plan/'
R = json.load(open(WD + 'road_result.json', encoding='utf8'))
P = json.load(open(WD + 'plan.json', encoding='utf8'))
X = json.load(open(WD + 'context.json', encoding='utf8'))
site = Polygon(P['site'])
AX = np.array(P['axis']); EW = np.array(P['ew'])
c0 = np.array(P['site'][:-1]).mean(0)
def s_of(x, y): return float((np.array([x, y]) - c0) @ AX)      # 장축 좌표(m, 남→북 증가)
def line(a, b): return LineString([a, b])
def ext(ls, d=60):
    """선분을 양끝으로 d 만큼 연장"""
    (x0, y0), (x1, y1) = ls.coords[0], ls.coords[-1]
    v = np.array([x1 - x0, y1 - y0]); v = v / np.linalg.norm(v)
    return LineString([tuple(np.array([x0, y0]) - v * d), tuple(np.array([x1, y1]) + v * d)])

# ---------------- 1. 도로망 ----------------
A = P['A']; B = P['B']
A_ln = line((A['wx'], A['wy']), (A['ex'], A['ey']))
B_ln = line((B['wx'], B['wy']), (B['ex'], B['ey']))
# C: A·B 사이(장축 기준 A+150m ~ B−150m)에서 순위합 최소 조합 — 북성로 선상이 기대값
sA, sB = s_of(*A_ln.interpolate(0.5, normalized=True).coords[0]), s_of(*B_ln.interpolate(0.5, normalized=True).coords[0])
spine_pts = [(x, y) for x, y, w in P['spine']]
spine = LineString(spine_pts)
def yc(p): return (p['wy'] + p['ey']) / 2
# C: 동측에는 양정로98번길(360,792)과 알천남로(361,300) 사이에 접속할 동측 가로가 없다(EW 조합 0건).
# → C 는 원화로에서 종축까지만 관통하는 T자 접속(서측 반 관통)으로 두고, 동측은 보행로(4m)로 황오동 골목에 잇는다.
# v2: 시청을 광장 북측에 두기 위해 C 를 북성로(361,090)에서 원화로309번길 축(361,250)으로 올림 — 시청 블록의 북측 경계·차량 접근
C_y = 361250.0
PLAZA_Y = 360960.0            # 성동시장(219433·361028, 시장 블록 y≈360,900~361,050) 정면 축
wb = site.exterior
cand = [wb.interpolate(t, normalized=True) for t in np.linspace(0, 1, 4000)]
p_w = min([p for p in cand if p.x < c0[0]], key=lambda p: abs(p.y - C_y))
c_end = spine.interpolate(spine.project(Point(p_w.x + 300 * EW[0], p_w.y + 300 * EW[1])))
C_ln = line((p_w.x - 12, p_w.y), (c_end.x, c_end.y))
C = dict(wx=C_ln.coords[0][0], wy=C_ln.coords[0][1], ex=c_end.x, ey=c_end.y, length=C_ln.length, inside=C_ln.intersection(site).length,
         dev=0.0, gain=None, rank_sum=None, wname='북성로', ename='종축(T자)', pareto=None, note='동측 접속 가로 없음 → 서측 반 관통')
p_ped0 = spine.interpolate(spine.project(Point(c0[0], 360996.0)))
C_ped = line((p_w.x, PLAZA_Y), (p_ped0.x, p_ped0.y))                 # 광장 정면(원화로) → 종축 → 육교 desire line(360,996) → 황오동
C_ped = LineString([(p_w.x, PLAZA_Y), (p_ped0.x, p_ped0.y), (site.bounds[2] + 10, 360996.0)])
spine_pts = [(x, y) for x, y, w in P['spine']]
spine = LineString(spine_pts)
R2 = P['R2']
R2_ln = line((R2['x'], R2['y']), spine_pts[-1])
R1 = P['R1']

W = dict(A=12.0, B=9.0, C=12.0, spine=8.0, R2=9.0)          # 차도+보도 폭(m): A·C 보차공존 12(차로 2×3 + 보도 2×3), B·R2 9, 종축 8
GREEN_W = 12.0                                                # 종축 선형공원 폭(도로 8m 별도)
roads = {
    'A': dict(geom=ext(A_ln, 40).buffer(W['A'] / 2, cap_style=2), w=W['A'], name='A 동서연결 ({}↔{})'.format(A['wname'], A['ename']), kind='보차공존 30km/h'),
    'C': dict(geom=ext(C_ln, 40).buffer(W['C'] / 2, cap_style=2), w=W['C'], name='C 동서연결 ({}↔{})'.format(C['wname'], C['ename']), kind='보차공존 30km/h'),
    'B': dict(geom=ext(B_ln, 40).buffer(W['B'] / 2, cap_style=2), w=W['B'], name='B 동서연결 ({}↔{})'.format(B['wname'], B['ename']), kind='보차공존 20km/h'),
    'spine': dict(geom=spine.buffer(W['spine'] / 2, cap_style=2), w=W['spine'], name='종축 서비스가로', kind='보행우선·서비스·비상 8m'),
    'R2': dict(geom=ext(R2_ln, 20).buffer(W['R2'] / 2, cap_style=2), w=W['R2'], name='R2 진입로', kind='9m'),
}
road_union = unary_union([r['geom'] for r in roads.values()]).intersection(site)
green = spine.buffer(W['spine'] / 2 + GREEN_W / 2, cap_style=2).difference(road_union).intersection(site)   # 종축 양측 6m 선형공원

# ---------------- 2. 블록 분할 ----------------
land = site.difference(unary_union([road_union, green]))
faces = [g for g in (land.geoms if land.geom_type == 'MultiPolygon' else [land]) if g.area > 400]

def side(g):
    p = g.representative_point()
    d = spine.project(p); q = spine.interpolate(d)
    return 'E' if (np.array([p.x - q.x, p.y - q.y]) @ EW) > 0 else 'W'

def cut(polys, cutter, only=None):
    """only='E'/'W' 면 그쪽 면만 자른다 (동서 블록의 분할선이 서로 다르므로)"""
    out = []
    for g in polys:
        if only and side(g) != only:
            out.append(g); continue
        parts = split(g, cutter)
        out += [p for p in parts.geoms if p.area > 300]
    return out

# 추가 분할선 (장축 좌표 s 기준 동서 절단): 역사헤리티지관/시청 경계, 문화/주거 경계, 주차빌딩 경계, P+R 경계
def ew_cut_at(s):
    ctr = c0 + AX * s
    return LineString([tuple(ctr - EW * 400), tuple(ctr + EW * 400)])
sS_tip, sN_tip = min(s_of(*p) for p in P['site'][:-1]), max(s_of(*p) for p in P['site'][:-1])
sC = s_of(*C_ln.interpolate(0.5, normalized=True).coords[0])
cuts = {
    'S_park': sS_tip + 75,           # 남단 꼬리 75m = 주차빌딩1 (좁은 꼬리 활용, 목표 600면)
    'M_heritage': s_of(c0[0], 361020.0),   # 서측: A 북측 ~361,020 까지 = 헤리티지관(석탑 마당) + 역전광장 + 이축 구 역사 (성동시장 정면). 시청은 그 북측
    'M_culture': sA + 170,           # 동측: A 북측 170m = 문화프로그램 (육교 desire line 포함)
    'N_pr': sB - 110,                # 동측: B 남측 110m = P+R 주차빌딩2
}
faces = cut(faces, ew_cut_at(cuts['S_park']))
faces = cut(faces, ew_cut_at(cuts['M_heritage']), only='W')
faces = cut(faces, ew_cut_at(cuts['M_culture']), only='E')
faces = cut(faces, ew_cut_at(cuts['N_pr']), only='E')
# 도심15m지구(동측 띠)는 별도 블록으로 잘라 4층 띠(타운하우스형)로 둔다 — 황오동 저층 주거와 높이 전이
godo15 = [shape(g['geom']) for g in X['godo'] if g['h_max'] == 15]
for gp in godo15:
    gp = gp.buffer(0)
    for ring in ([gp.exterior] if gp.geom_type == 'Polygon' else [q.exterior for q in gp.geoms]):
        faces = cut(faces, LineString(ring.coords))

def zone(g):
    s = s_of(*g.representative_point().coords[0])
    if s < sA: return 'S'
    if s < sC: return 'M'
    if s < sB: return 'N'
    return 'T'

# ---------------- 3. 프로그램 배정 규칙 ----------------
def assign(g):
    z, sd = zone(g), side(g); s = s_of(*g.representative_point().coords[0])
    if z == 'S' and sd == 'W' and s < cuts['S_park']: return '주차장(남·주차빌딩1)'
    if z == 'S' and sd == 'E' and s < cuts['S_park']: return '광장·녹지(남단 진입 R1)'
    if z == 'S' and sd == 'W': return '근린생활(성동시장 대면 마켓홀)'
    if z == 'S' and sd == 'E': return '청년주거 S'
    if z == 'M' and sd == 'W' and s < cuts['M_heritage']: return '역전광장·구 역사(이축)·역사헤리티지관'
    if z == 'M' and sd == 'W': return '경주시청'
    if z == 'M' and sd == 'E' and s < cuts['M_culture']: return '문화프로그램'
    if z == 'M' and sd == 'E': return '청년주거 M'
    if z == 'N' and sd == 'W': return '체육센터·주민지원시설'      # C(361,250)~B: 북측으로 좁아지는 서측 잔여 전체
    if z == 'N' and sd == 'E' and s >= cuts['N_pr']: return '주차장(북·P+R 주차빌딩2)'
    if z == 'N' and sd == 'E': return '청년주거 N'
    return '광장·녹지(북단 회차)'

# 규모 가정 (블록별): 건폐율, 층수 상한(고도지구로 다시 자름), 층고, 지하
RULE = {
    '경주시청':                  dict(bcr=0.35, fl=5, fh=4.0, base=1, use='공공청사', color=(200, 60, 60)),
    '주차장(남·주차빌딩1)':       dict(bcr=0.60, fl=5, fh=3.3, base=0, use='주차장', color=(120, 120, 120)),
    '주차장(북·P+R 주차빌딩2)':   dict(bcr=0.70, fl=5, fh=3.3, base=0, use='주차장', color=(90, 90, 90)),
    '청년주거 S':                dict(bcr=0.40, fl=5, fh=3.3, base=0, use='주거', color=(240, 190, 60)),
    '청년주거 W(원화로변)':        dict(bcr=0.45, fl=5, fh=3.3, base=0, use='주거', color=(235, 180, 50)),
    '청년주거 M':                dict(bcr=0.40, fl=5, fh=3.3, base=0, use='주거', color=(245, 200, 80)),
    '청년주거 N':                dict(bcr=0.40, fl=5, fh=3.3, base=0, use='주거', color=(250, 210, 100)),
    '근린생활(성동시장 대면 마켓홀)': dict(bcr=0.60, fl=2, fh=4.5, base=0, use='근린생활', color=(230, 120, 40)),
    '역전광장·구 역사(이축)·역사헤리티지관': dict(bcr=0.25, fl=3, fh=5.0, base=0, use='문화', color=(150, 90, 160)),
    '문화프로그램':               dict(bcr=0.40, fl=3, fh=4.5, base=0, use='문화', color=(170, 120, 200)),
    '체육센터·주민지원시설':       dict(bcr=0.50, fl=4, fh=4.5, base=1, use='공공시설', color=(60, 150, 200)),
    '광장·녹지(남단 진입 R1)':     dict(bcr=0.0, fl=0, fh=0, base=0, use='광장', color=(180, 220, 170)),
    '광장·녹지(북단 회차)':        dict(bcr=0.0, fl=0, fh=0, base=0, use='광장', color=(180, 220, 170)),
}
godo = [(g['name'], g['h_max'], shape(g['geom'])) for g in X['godo']]
def h_limit(g):
    hs = [h for n, h, gg in godo if h and gg.intersects(g) and gg.intersection(g).area > 0.05 * g.area]
    minh = [n for n, h, gg in godo if h is None and gg.intersects(g)]
    return (min(hs) if hs else 20), bool(minh)

blocks = []
for i, g in enumerate(faces):
    prog = assign(g)
    r = RULE[prog]
    hmax, minflag = h_limit(g)
    fl = min(r['fl'], int(hmax // r['fh'])) if r['fh'] else 0
    foot = g.area * r['bcr']; gfa = foot * fl
    d = dict(id=i, prog=prog, use=r['use'], zone=zone(g), side=side(g), area=round(g.area), h_max=hmax, min_h_zone=minflag,
             bcr=r['bcr'], floors=fl, gfa=round(gfa), basement=r['base'], color=r['color'], geom=mapping(g),
             cx=g.representative_point().x, cy=g.representative_point().y)
    if r['use'] == '주거':
        d['units'] = int(gfa * 0.70 / 36)          # 전용률 70%, 청년 1~2인 평균 전용 36㎡ (가정)
    if r['use'] == '주차장':
        d['spaces'] = int(gfa / 32)                # 주차 1면당 32㎡(통로 포함) (가정)
    if r['base']:
        d['spaces_b1'] = int(foot / 32)            # B1 한 층만 (지하 소극적)
    blocks.append(d)

# 광장·이축 구 역사 (헤리티지 블록 안): 광장 = 원화로변 폭 48m × 성동시장 정면 100m, 구 역사(24×88, 원 footprint 치수) 는 광장 동변에 남북 장축으로
st_src = next((b for b in X['buildings_in_site'] if b['area'] == 1404), None)
st_w, st_l = 24.0, 88.0
if st_src:
    sb = Polygon(st_src['xy']).bounds; st_w, st_l = sb[2] - sb[0], sb[3] - sb[1]
her = [b for b in blocks if b['prog'].startswith('역전광장')]
plaza = station_new = None
if her:
    hb = unary_union([shape(b['geom']) for b in her])
    x0 = hb.bounds[0]
    plaza = Polygon([(x0, PLAZA_Y - 50), (x0 + 48, PLAZA_Y - 50), (x0 + 48, PLAZA_Y + 50), (x0, PLAZA_Y + 50)]).intersection(hb)
    station_new = Polygon([(x0 + 50, PLAZA_Y - st_l / 2), (x0 + 50 + st_w, PLAZA_Y - st_l / 2), (x0 + 50 + st_w, PLAZA_Y + st_l / 2), (x0 + 50, PLAZA_Y + st_l / 2)]).intersection(hb)
    for b in her:
        b['plaza_area'] = round(plaza.area); b['station_area'] = round(station_new.area)
        b['note'] = '광장 {:,}㎡(원화로변 48m×100m, 성동시장 정면) + 구 역사 이축 {:,}㎡(광장 동변) + 남측 = 헤리티지관·삼층석탑 마당'.format(round(plaza.area), round(station_new.area))

# 같은 프로그램이 여러 조각이면 합산 표
from collections import OrderedDict
tab = OrderedDict()
for b in blocks:
    t = tab.setdefault(b['prog'], dict(use=b['use'], area=0, gfa=0, units=0, spaces=0, n=0, floors=b['floors'], h_max=b['h_max']))
    t['area'] += b['area']; t['gfa'] += b['gfa']; t['units'] += b.get('units', 0); t['spaces'] += b.get('spaces', 0) + b.get('spaces_b1', 0); t['n'] += 1
road_area = round(road_union.area); green_area = round(green.area)
resid = round(site.area) - (sum(t['area'] for t in tab.values()) + road_area + green_area)   # 300㎡ 미만 슬리버(도로 모서리) → 도로에 귀속
road_area += resid
tot = sum(t['area'] for t in tab.values()) + road_area + green_area
print('블록 합계 %d + 도로 %d + 선형공원 %d = %d / 부지 %d (차 %d㎡)' % (sum(t['area'] for t in tab.values()), road_area, green_area, tot, round(site.area), round(site.area) - tot))

# ---------------- 4. 횡단보도·정류장 ----------------
# 자료 없음(수치지도 A004 미포함) → 신설 교차로·정류장·광장 축에서 도출. 기존 정류장(BIS)은 유지, 신설 2쌍.
def pt_on(ln, t): p = ln.interpolate(t, normalized=True); return (p.x, p.y)
cw_new = [
    dict(x=A['wx'] + 6, y=A['wy'], road='원화로', why='A 서단 신호교차로(화랑로) — 우체국 정류장·마켓홀', kind='신호'),
    dict(x=A['wx'] + 6, y=PLAZA_Y, road='원화로', why='역전광장 정면 — 성동시장 입구 축, 성동시장 동편 정류장(360,933·360,978) 사이. 광장↔시장을 잇는 핵심 횡단', kind='신호(중간블록)'),
    dict(x=C['wx'] + 6, y=C['wy'], road='원화로', why='C 서단 교차로(원화로309번길) — 시청 북측 차량 진입·체육센터', kind='신호'),
    dict(x=B['wx'] + 20, y=B['wy'], road='원화로', why='B 서단(북문로) — 세무서·큰마디병원 정류장(361,310)과 85m', kind='신호 또는 고원식'),
    dict(x=R1['x'], y=R1['y'] + 30, road='원화로', why='남단 R1(경고지하도 정류장 360,553~582 옆) — 주차빌딩1·마켓홀 보행 진입', kind='신호'),
    dict(x=C_ped.coords[-1][0] - 6, y=C_ped.coords[-1][1], road='동측 경계(황오동 골목)', why='C 보행로 동단 — 기존 육교(216m) desire line 승계, 황오동에서 청년주거 M·문화프로그램', kind='보행로 접속'),
    dict(x=B['ex'] - 6, y=B['ey'], road='알천남로', why='B 동단·R2 — 환경복지회관 정류장(361,296~311) 바로 앞, P+R 보행 출입', kind='신호'),
    dict(x=A['ex'] - 6, y=A['ey'], road='양정로', why='A 동단 — 황오동 서측 주거지에서 문화프로그램·역전광장', kind='고원식'),
]
# 종축과 A·C·B 교차부는 고원식 횡단(보행 연속) — 좌표
for k, ln in (('A', A_ln), ('C', C_ln), ('B', B_ln)):
    ip = ln.intersection(spine)
    if not ip.is_empty:
        p = ip if ip.geom_type == 'Point' else list(ip.geoms)[0]
        cw_new.append(dict(x=p.x, y=p.y, road='종축×' + k, why='종축 보행 연속 — 고원식 교차부(차량 감속)', kind='고원식'))
stops_new = [
    dict(x=A['wx'] + 14, y=A['wy'] - 45, road='원화로', why='A 교차로 남측 버스베이 — 마켓홀·주차빌딩1. (광장 앞은 기존 성동시장 동편 정류장 2곳이 그대로 광장 정류장이 됨)'),
    dict(x=p_ped0.x, y=p_ped0.y, road='종축', why='순환셔틀·트램 정거장(2030 기본계획 제1순환선 "구경주역" 정차) — 역전광장·구 역사 바로 동측, 육교 desire line 교점'),
    dict(x=(R2['x'] + spine_pts[-1][0]) / 2, y=(R2['y'] + spine_pts[-1][1]) / 2, road='R2', why='P+R 환승 셔틀 정거장 — 주차빌딩2 도보 2분 이내'),
]
# 기존 정류장 중 부지 120m 이내
stops_keep = [s for s in X['stops'] if Point(s['x'], s['y']).distance(site) < 120]

# 구 역사 건물과 A 의 관계 (사용자 지시로 기존 건물 무시하되 판단 근거로 기록)
st = next((b for b in X['buildings_in_site'] if b['area'] == 1404), None)
st_note = None
if st:
    sp = Polygon(st['xy'])
    st_note = dict(area=st['area'], bounds=[round(v) for v in sp.bounds], crosses_A=bool(sp.intersects(roads['A']['geom'])),
                   note='구 경주역사(1,404㎡, 현 위치 y 360,745~360,833)가 A 노선폭에 걸침 → v2: A 북측 역전광장 동변(y≈%.0f)으로 이축. 이축 거리 약 %.0fm 북' % (PLAZA_Y, PLAZA_Y - (sp.bounds[1] + sp.bounds[3]) / 2))

out = dict(site=P['site'], roads={k: dict(name=v['name'], kind=v['kind'], w=v['w'], geom=mapping(v['geom'].intersection(site)), line=list(map(list, (A_ln if k == 'A' else C_ln if k == 'C' else B_ln if k == 'B' else spine if k == 'spine' else R2_ln).coords))) for k, v in roads.items()},
           ped=[dict(name='광장–종축–황오동 보행축(육교 desire line)', w=4.0, line=list(map(list, C_ped.coords)))],
           plaza=mapping(plaza) if plaza is not None else None, station_new=mapping(station_new) if station_new is not None else None,
           green=mapping(green), road_area=road_area, green_area=green_area, blocks=blocks, table=tab, total=tot, site_area=round(site.area),
           cw_new=cw_new, stops_new=stops_new, stops_keep=stops_keep, C=C, station=st_note, cuts=cuts,
           assumptions=['건폐율·층수·층고는 블록별 가정(RULE)', '청년주거 세대 = 연면적×전용률70%÷36㎡', '주차 1면 32㎡', '고도지구: 도심20m→5층(주거 층고 3.3), 도심15m(동측 띠)→4층',
                        '지하: 시청·체육센터 B1 한 층만(시굴 후), 그 외 지하 없음 — 매장문화재 발굴 유예 조건(2m 미만 성토·공원/주차) 준수', '횡단보도 위치 자료 없음(수치지도 A004 미포함) → 교차로·정류장·광장축에서 도출'])
json.dump(out, open(WD + 'blocks.json', 'w', encoding='utf8'), ensure_ascii=False)
with open(WD + '20260930_구경주역_토지이용계획표_v7.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(['구분', '용도', '면적_m2', '비율_pct', '층수', '고도상한_m', '연면적_m2', '세대', '주차면', '블록수'])
    for k, t in tab.items():
        w.writerow([k, t['use'], t['area'], round(100 * t['area'] / site.area, 1), t['floors'], t['h_max'], t['gfa'], t['units'] or '', t['spaces'] or '', t['n']])
    w.writerow(['도로(A·B·C·종축·R2, 슬리버 %d㎡ 포함)' % resid, '도로', road_area, round(100 * road_area / site.area, 1), '', '', '', '', '', ''])
    w.writerow(['선형공원(종축 양측)', '공원', green_area, round(100 * green_area / site.area, 1), '', '', '', '', '', ''])
    w.writerow(['합계', '', tot, round(100 * tot / site.area, 1), '', '', sum(t['gfa'] for t in tab.values()), sum(t['units'] for t in tab.values()), sum(t['spaces'] for t in tab.values()), len(blocks)])
for k, t in tab.items():
    print('%-22s %7d㎡ %5.1f%%  %d층/%dm  연면적 %7d  세대 %4s  주차 %4s  (%d)' % (k, t['area'], 100 * t['area'] / site.area, t['floors'], t['h_max'], t['gfa'], t['units'] or '-', t['spaces'] or '-', t['n']))
print('C =', C['wname'], '->', C['ename'], round(C['length']), 'm inside', round(C['inside']), C['note'])
print('station', st_note)
print('blocks', len(blocks), 'units total', sum(t['units'] for t in tab.values()), 'spaces total', sum(t['spaces'] for t in tab.values()))
