# 구경주역 부지 도로계획 — 진입점·동서연결 분석
# 입력: road_data.json(build_data.py), 표준노드링크 광역(경주 전역), 시간대별 속도 이력
# 산출: road_result.json (GH 시각화 입력)
# 원칙: 가중치를 고정하지 않는다. 기준별 값을 그대로 두고 (1) 파레토 비지배 여부 (2) 34개 시나리오(평일/주말 x 06~22시)에서
#       기준 순위합 1등을 몇 번 하는지(강건성)로 추천한다.
import json, math, warnings
import numpy as np
import shapefile
from collections import defaultdict
from pyproj import Transformer
from shapely.geometry import Polygon, LineString, Point
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

warnings.filterwarnings('ignore')
ROOT = r'C:/Users/User/Desktop/9_도시/'
WD = ROOT + 'work/road_plan/'
SP = r'C:/Users/User/AppData/Local/Temp/claude/C--Users-User-Desktop-9---/37a37839-edd8-483b-a0d8-c2e88f5eb82a/scratchpad/nl/'
D = json.load(open(WD + 'road_data.json', encoding='utf8'))
site = Polygon(D['site'])
t86_87 = Transformer.from_crs(5186, 5187, always_xy=True).transform
inv = Transformer.from_crs(5187, 5186, always_xy=True).transform

def fix(s):
    try: return s.encode('latin-1').decode('cp949')
    except Exception: return s

# ---------- 1. 광역 그래프 (부지 중심 반경 14km) ----------
cx, cy = site.centroid.x, site.centroid.y
X0, Y0 = inv(cx - 14000, cy - 14000); X1, Y1 = inv(cx + 14000, cy + 14000)
rl = shapefile.Reader(SP + 'MOCT_LINK.shp', encoding='latin-1')
hist = {}
H = json.load(open(ROOT + 'archive/C_data/processed/traffic_hist_links_4326.geojson', encoding='utf8'))
for f in H['features']:
    p = f['properties']
    hist[p['LINK_ID']] = dict(wd=[p.get('wd_%02d' % h) for h in range(24)], we=[p.get('we_%02d' % h) for h in range(24)],
                              thr_c=p.get('thr_c'), thr_f=p.get('thr_f'))
links = []
for sr in rl.iterShapeRecords():
    x0, y0, x1, y1 = sr.shape.bbox
    if x1 < X0 or x0 > X1 or y1 < Y0 or y0 > Y1: continue
    r = sr.record.as_dict()
    a = sr.shape.points[0]; b = sr.shape.points[-1]
    links.append(dict(id=r['LINK_ID'], f=r['F_NODE'], t=r['T_NODE'], lanes=r['LANES'], rank=r['ROAD_RANK'], name=fix(r['ROAD_NAME']),
                      spd=r['MAX_SPD'], len=r['LENGTH']))
print('regional links', len(links))
nid = {}
for l in links:
    for k in (l['f'], l['t']):
        if k not in nid: nid[k] = len(nid)
N = len(nid)

def series(l, day):
    """시간대별 속도(km/h) 24개. 이력 없으면 제한속도의 50%(15~40)로 대체하고 imputed 표시."""
    h = hist.get(l['id'])
    fallback = min(max(0.5 * (l['spd'] or 30), 15), 40)
    if h and any(v for v in h[day]):
        v = [x if x else None for x in h[day]]
        m = np.nanmean([x for x in v if x] or [fallback])
        return [x if x else m for x in v], False
    return [fallback] * 24, True

SPD = {}
for day in ('wd', 'we'):
    SPD[day] = np.zeros((len(links), 24));
IMP = np.zeros(len(links), bool)
for i, l in enumerate(links):
    for day in ('wd', 'we'):
        s, imp = series(l, day); SPD[day][i] = s
    IMP[i] = imp
rows = np.array([nid[l['f']] for l in links]); cols = np.array([nid[l['t']] for l in links])
LEN = np.array([max(l['len'], 1.0) for l in links])
LIDX = {l['id']: i for i, l in enumerate(links)}

# 경계 안은 비어 있다고 본다: 부지 내부 기존 링크(양정로 소로 등)는 모든 그래프에서 제거
in_site = {l['id'] for l in D['links'] if LineString(l['xy']).intersection(site).length > 0.5 * l['len']}
IN_SITE_IDX = [LIDX[i] for i in in_site if i in LIDX]
print('interior links removed', len(IN_SITE_IDX))

def graph(day, h, drop=None):
    t = LEN / (SPD[day][:, h] / 3.6)
    m = np.ones(len(links), bool)
    m[IN_SITE_IDX] = False
    if drop is not None: m[drop] = False
    g = csr_matrix((t[m], (rows[m], cols[m])), shape=(N, N))
    return (g + g.T) if False else g.maximum(g.T)   # 양방향(방향 자료 없음)

# 노드 좌표 (광역 노드는 D['nodes'] 범위 밖도 필요 -> 링크 첫/끝점으로 채움)
NXY = np.zeros((N, 2))
for sr in rl.iterShapeRecords():
    pass
# 위 순회는 무거우므로 필요 시에만: 링크 형상을 다시 읽어 노드 좌표를 채운다
rl2 = shapefile.Reader(SP + 'MOCT_LINK.shp', encoding='latin-1')
seen = set()
for sr in rl2.iterShapeRecords():
    x0, y0, x1, y1 = sr.shape.bbox
    if x1 < X0 or x0 > X1 or y1 < Y0 or y0 > Y1: continue
    r = sr.record.as_dict()
    for k, pt in ((r['F_NODE'], sr.shape.points[0]), (r['T_NODE'], sr.shape.points[-1])):
        if k in nid and k not in seen:
            NXY[nid[k]] = t86_87(*pt); seen.add(k)
print('nodes', N)

# ---------- 2. 목적지 그룹 ----------
dest = D['dest']
groups = {
    '황리단길': ['황리단길'],
    '신경주역(KTX)': ['신경주역(KTX)'],
    '보문관광단지': ['보문관광단지(대표점)'],
    '핵심문화재': ['대릉원', '첨성대', '월정교', '황룡사지', '국립경주박물관', '동궁과 월지'],
    '터미널': ['시외버스터미널', '고속버스터미널'],
    '경주IC': ['경주IC'],
}
def snap(x, y):
    d = np.hypot(NXY[:, 0] - x, NXY[:, 1] - y); i = int(np.argmin(d)); return i, float(d[i])
dnode = {}
for g, names in groups.items():
    for n in names:
        if n in dest:
            i, dd = snap(dest[n]['x'], dest[n]['y']); dnode[n] = (i, dd)
print({k: round(v[1]) for k, v in dnode.items()})

# ---------- 3. 후보 진입점 ----------
# 3-1. 경계 표본: 연결(링크) 근접 (링크 중심선에서 도로 반폭 + 10m 이내)
Dl = {l['id']: l for l in D['links']}
near = [l for l in D['links'] if l['dist_site'] <= 40 and l['id'] not in in_site]   # 내부 링크는 접도 후보에서 제외
geoms = {l['id']: LineString(l['xy']) for l in near}
bd = site.exterior
samples = []
step = 20.0
for s in np.arange(0, bd.length, step):
    p = bd.interpolate(s)
    best = None
    for l in near:
        d = geoms[l['id']].distance(p)
        hw = (l['width'] or (3.0 * l['lanes'] * (2 if l['lanes'] > 1 else 1)) ) / 2.0
        if d <= hw + 10 and (best is None or d < best[0]): best = (d, l)
    if best: samples.append((p, best[1]))
print('boundary samples with road frontage', len(samples))

# 3-2. 교차로 노드 (차수 3+)
deg = defaultdict(int)
for l in D['links']:
    deg[l['f']] += 1; deg[l['t']] += 1
inter_nodes = [(k, v) for k, v in D['nodes'].items() if deg[k] >= 3]
INX = np.array([[v['x'], v['y']] for k, v in inter_nodes]) if inter_nodes else np.zeros((0, 2))

stops = D['stops']
SX = np.array([[s['x'], s['y']] for s in stops])
turn_nodes = defaultdict(list)
for t in D['turns']: turn_nodes[t['node']].append(t['type'])

dgroup_nodes = {g: [dnode[n][0] for n in names if n in dnode] for g, names in groups.items()}

# 시나리오
HOURS = list(range(6, 23))
SCEN = [(day, h) for day in ('wd', 'we') for h in HOURS]
# 그룹별 목적지에서의 최단시간 (SCEN x 그룹 x N)  — 무거운 부분
DIST = {}
for (day, h) in SCEN:
    G = graph(day, h)
    for g, nodes_ in dgroup_nodes.items():
        dd = dijkstra(G, directed=False, indices=nodes_, min_only=False)
        DIST[(day, h, g)] = dd.mean(axis=0) if dd.ndim > 1 else dd
print('dijkstra done')

cands = []
for p, l in samples:
    li = LIDX[l['id']]
    ends = [(nid[l['f']], NXY[nid[l['f']]]), (nid[l['t']], NXY[nid[l['t']]])]
    # 후보를 링크 끝점(노드)에서 나온 거리로 근사: 표본점 -> 양 끝 노드 직선거리
    dA = float(np.hypot(p.x - ends[0][1][0], p.y - ends[0][1][1])); dB = float(np.hypot(p.x - ends[1][1][0], p.y - ends[1][1][1]))
    crit = {}
    for (day, h) in SCEN:
        v = SPD[day][li, h] / 3.6
        acc = {}
        for g in groups:
            arr = DIST[(day, h, g)]
            acc[g] = float(min(arr[ends[0][0]] + dA / v, arr[ends[1][0]] + dB / v))
        crit[(day, h)] = acc
    ff = float(np.percentile(np.concatenate([SPD['wd'][li], SPD['we'][li]]), 90))
    dn = float(np.min(np.hypot(INX[:, 0] - p.x, INX[:, 1] - p.y))) if len(INX) else 999.0
    nb = int(np.sum(np.hypot(SX[:, 0] - p.x, SX[:, 1] - p.y) <= 150)) if len(SX) else 0
    tp = []
    for k, v in inter_nodes:
        if math.hypot(v['x'] - p.x, v['y'] - p.y) <= 40: tp += turn_nodes.get(k, [])
    cands.append(dict(x=p.x, y=p.y, link=l['id'], road=l['name'], rank=l['rank'], lanes=l['lanes'], width=l['width'],
                      dnode=dn, bus=nb, turns=tp, ff=ff, imputed=bool(IMP[li]), crit=crit, li=li))
print('candidates', len(cands))

# 시나리오별 순위합 -> 1등 횟수
def scen_scores(day, h):
    ks = list(groups)
    M = np.array([[c['crit'][(day, h)][g] for g in ks] for c in cands])  # 작을수록 좋음 (시간)
    acc = M.mean(axis=1)
    spd = np.array([SPD[day][c['li'], h] / max(c['ff'], 1e-6) for c in cands])   # 클수록 좋음(여유)
    cap = np.array([c['lanes'] * (c['width'] or 8) for c in cands])
    dn = np.array([c['dnode'] for c in cands])
    bus = np.array([c['bus'] for c in cands])
    tr = np.array([len(c['turns']) for c in cands])
    def rk(a, asc=True):
        o = np.argsort(a if asc else -a); r = np.empty(len(a)); r[o] = np.arange(len(a)); return r
    return acc, spd, cap, dn, bus, tr, rk(acc) + rk(spd, False) + rk(cap, False) + rk(dn) + rk(bus, False) + rk(tr)

wins = np.zeros(len(cands)); rs_all = np.zeros(len(cands))
for (day, h) in SCEN:
    *_, rs = scen_scores(day, h)
    wins[int(np.argmin(rs))] += 1; rs_all += rs
rs_mean = rs_all / len(SCEN)

# 파레토 (대표 시나리오: 평일 18시)
acc, spd, cap, dn, bus, tr, _ = scen_scores('wd', 18)
Y = np.stack([acc, -spd, -cap, dn, -bus, tr], 1)
nd = []
for i in range(len(cands)):
    dom = np.any(np.all(Y <= Y[i], axis=1) & np.any(Y < Y[i], axis=1))
    nd.append(not dom)

# ---------- 4. 동서 연결 후보 ----------
# 부지 장축 방향(장축 각) 계산
pts = np.array(D['site'][:-1]); u, s_, vt = np.linalg.svd(pts - pts.mean(0)); axis = vt[0]   # 장축
ang_axis = math.atan2(axis[1], axis[0])
ew = np.array([-axis[1], axis[0]]); ew = ew if ew[0] > 0 else -ew   # 동서(장축 직교) 방향
# 각 노드가 부지의 서/동 어느 쪽인지, 부지로부터 거리
W = []; E = []
for k, v in D['nodes'].items():
    p = Point(v['x'], v['y'])
    dsite = p.distance(site)
    if dsite > 140 or site.contains(p): continue
    c = np.array([v['x'] - cx, v['y'] - cy])
    side = float(c @ ew)
    (E if side > 0 else W).append((k, v, dsite))
print('W', len(W), 'E', len(E))
# 링크 방위(노드에서 부지로 향하는 링크가 있는지)
adj = defaultdict(list)
for l in D['links']:
    adj[l['f']].append(l); adj[l['t']].append(l)
def leg_bearing(node, l):
    xy = l['xy']
    a, b = (xy[0], xy[1]) if l['f'] == node else (xy[-1], xy[-2])
    return math.atan2(b[1] - a[1], b[0] - a[0])

def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi
pairs = []
Gx = graph('wd', 18)   # 내부 링크는 graph()가 항상 제거
for kw, vw, dw in W:
    for ke, ve, de in E:
        seg = LineString([(vw['x'], vw['y']), (ve['x'], ve['y'])])
        inside = seg.intersection(site).length
        if inside < 60: continue
        ang = math.atan2(ve['y'] - vw['y'], ve['x'] - vw['x'])
        dev = abs(wrap(ang - math.atan2(ew[1], ew[0])))
        dev = min(dev, math.pi - dev) * 180 / math.pi
        if dev > 30: continue
        # 각 끝의 기존 가로 방위와 정렬 (연결선과 가장 가까운 다리)
        def align(node, sign):
            """연결 방향과 가장 잘 맞는 기존 가로(내부 링크 제외)의 편차각과 이름"""
            legs = [l for l in adj.get(node, []) if l['id'] not in in_site]
            if not legs: return 90.0, ''
            best = min(legs, key=lambda l: abs(math.degrees(wrap(leg_bearing(node, l) - (ang if sign > 0 else ang + math.pi)))))
            return abs(math.degrees(wrap(leg_bearing(node, best) - (ang if sign > 0 else ang + math.pi)))), best['name']
        (aw, wname), (ae, ename) = align(kw, +1), align(ke, -1)
        if kw not in nid or ke not in nid: continue
        t_old = dijkstra(Gx, directed=False, indices=nid[kw])[nid[ke]]
        L = seg.length
        t_new = L / (30 / 3.6)
        gain = (t_old - t_new) if np.isfinite(t_old) else 1e4
        pairs.append(dict(w=kw, e=ke, wx=vw['x'], wy=vw['y'], ex=ve['x'], ey=ve['y'], length=L, inside=inside, dev=dev, align_w=aw, align_e=ae,
                          t_old=float(t_old) if np.isfinite(t_old) else None, t_new=t_new, gain=float(gain),
                          detour_old=float(t_old * 30 / 3.6 / L) if np.isfinite(t_old) else None,
                          wname=wname, ename=ename))
print('EW pairs', len(pairs))

def rk(a, asc=True):
    a = np.asarray(a, float); o = np.argsort(a if asc else -a); r = np.empty(len(a)); r[o] = np.arange(len(a)); return r
if pairs:
    rs = (rk([p['gain'] for p in pairs], False) + rk([p['dev'] for p in pairs]) + rk([p['align_w'] + p['align_e'] for p in pairs]) + rk([p['inside'] for p in pairs]))
    for p, r_ in zip(pairs, rs): p['rank_sum'] = float(r_)
    Yp = np.array([[-p['gain'], p['dev'], p['align_w'] + p['align_e'], p['inside']] for p in pairs])
    for i, p in enumerate(pairs):
        p['pareto'] = bool(not np.any(np.all(Yp <= Yp[i], axis=1) & np.any(Yp < Yp[i], axis=1)))

# ---------- 5. 표시용 링크 (500m) ----------
disp = []
for l in D['links']:
    if l['dist_site'] > 500: continue
    li = LIDX.get(l['id'])
    if li is None: continue
    disp.append(dict(id=l['id'], name=l['name'], rank=l['rank'], lanes=l['lanes'], width=l['width'], spd=l['spd'], xy=l['xy'],
                     wd=[round(float(v), 1) for v in SPD['wd'][li]], we=[round(float(v), 1) for v in SPD['we'][li]], imputed=bool(IMP[li]),
                     in_site=l['id'] in in_site))

out = dict(site=D['site'], axis_deg=math.degrees(ang_axis), ew=list(ew), disp=disp, stops=stops, dest=dest, turns=D['turns'], nodes=D['nodes'],
           groups=list(groups), scen=[list(s) for s in SCEN],
           cands=[dict(x=c['x'], y=c['y'], road=c['road'], rank=c['rank'], lanes=c['lanes'], width=c['width'], dnode=c['dnode'], bus=c['bus'],
                       turns=c['turns'], imputed=c['imputed'], wins=int(wins[i]), rank_sum_mean=float(rs_mean[i]), pareto_wd18=bool(nd[i]),
                       acc={f'{d}{h:02d}': {g: round(c['crit'][(d, h)][g], 1) for g in groups} for (d, h) in SCEN if h in (8, 12, 18)},
                       spd={f'{d}{h:02d}': round(float(SPD[d][c['li'], h]), 1) for (d, h) in SCEN}) for i, c in enumerate(cands)],
           ew_pairs=sorted(pairs, key=lambda p: p.get('rank_sum', 1e9))[:120],
           n_hist_links=int(sum(1 for l in disp if not l['imputed'])), n_links=len(disp))
json.dump(out, open(WD + 'road_result.json', 'w', encoding='utf8'), ensure_ascii=False)
print('wrote road_result.json')
# 요약 출력
o = np.argsort(-wins)[:8]
print('--- 진입 후보 강건성 상위 (34개 시나리오 중 1등 횟수) ---')
for i in o:
    c = cands[i]; print(i, c['road'], c['rank'], 'lanes', c['lanes'], 'w', c['width'], 'wins', int(wins[i]), 'rs', round(rs_mean[i], 1), 'dnode', round(c['dnode']), 'bus', c['bus'], 'turns', c['turns'], 'pareto', nd[i], 'xy', round(c['x']), round(c['y']))
print('--- 동서 연결 상위 ---')
for p in sorted(pairs, key=lambda p: p.get('rank_sum', 1e9))[:8]:
    print(p['wname'], '->', p['ename'], 'len', round(p['length']), 'inside', round(p['inside']), 'dev', round(p['dev']), 'gain(s)', round(p['gain']), 'detour_old', p['detour_old'] and round(p['detour_old'], 2), 'pareto', p['pareto'])
