# road_result.json -> plan.json : 추천 진입점, 동서 연결안(A/B), 종축, 지표 요약 (GH가 읽는 최종 입력)
import json, math
import numpy as np
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union

WD = r'C:/Users/User/Desktop/9_도시/work/road_plan/'
R = json.load(open(WD + 'road_result.json', encoding='utf8'))
site = Polygon(R['site'])
C = R['cands']
ew = np.array(R['ew'])
ax = np.array([ew[1], -ew[0]])  # 장축 방향 (동서와 직교)
if ax[1] < 0: ax = -ax

# --- 진입 후보를 70m 이내 같은 도로 단위로 묶어 군집 승수를 센다
cl = []
for i, c in enumerate(C):
    for g in cl:
        if any(C[j]['road'] == c['road'] and math.hypot(C[j]['x'] - c['x'], C[j]['y'] - c['y']) < 70 for j in g):
            g.append(i); break
    else:
        cl.append([i])
clusters = []
for g in cl:
    xs = [C[i]['x'] for i in g]; ys = [C[i]['y'] for i in g]
    clusters.append(dict(members=g, road=C[g[0]]['road'], x=float(np.mean(xs)), y=float(np.mean(ys)), wins=sum(C[i]['wins'] for i in g),
                         rs=float(np.mean([C[i]['rank_sum_mean'] for i in g])), pareto=any(C[i]['pareto_wd18'] for i in g)))
clusters.sort(key=lambda z: -z['wins'])

# --- 동서 연결
P = R['ew_pairs']
def yc(p): return (p['wy'] + p['ey']) / 2
A = min(P, key=lambda p: p['rank_sum'])
y0_, y1_ = site.bounds[1], site.bounds[3]
# B: A 와 장축 방향으로 200m 이상 떨어진 조합 중 순위합 최소 (북쪽 우선, 없으면 남쪽)
far = [p for p in P if abs(yc(p) - yc(A)) > 200]
north = [p for p in far if yc(p) > yc(A)]
B = min(north or far, key=lambda p: p['rank_sum'])
south = [p for p in P if yc(p) < y0_ + (y1_ - y0_) * 0.15]
S = min(south, key=lambda p: p['rank_sum']) if south else None

# --- 종축 중심선: 장축에 직교하는 절단선의 중점
pts = np.array(R['site'][:-1]); c0 = pts.mean(0)
proj = (pts - c0) @ ax; smin, smax = proj.min(), proj.max()
spine = []
for s in np.arange(smin + 5, smax - 5, 20):
    ctr = c0 + ax * s
    cut = LineString([tuple(ctr - ew * 400), tuple(ctr + ew * 400)]).intersection(site)
    segs = [cut] if cut.geom_type == 'LineString' else [g for g in getattr(cut, 'geoms', []) if g.geom_type == 'LineString']
    if not segs: continue
    g = max(segs, key=lambda z: z.length)
    m = g.interpolate(0.5, normalized=True)
    spine.append((m.x, m.y, g.length))

# --- 동서 관통 간격 (장축 좌표에서 차량 횡단 위치 사이 최대 간격)
def s_of(x, y): return float((np.array([x, y]) - c0) @ ax)
cross_before = sorted([s_of(*[(S['wx'] + S['ex']) / 2, (S['wy'] + S['ey']) / 2]) if S else smin, smin, smax])
def gaps(cs):
    cs = sorted(set(cs)); return [b - a for a, b in zip(cs, cs[1:])]
base = [smin, smax]
ga = gaps(base); gb = gaps(base + [s_of((A['wx'] + A['ex']) / 2, (A['wy'] + A['ey']) / 2)])
gc = gaps(base + [s_of((A['wx'] + A['ex']) / 2, (A['wy'] + A['ey']) / 2), s_of((B['wx'] + B['ex']) / 2, (B['wy'] + B['ey']) / 2)])

best=max(range(len(C)),key=lambda i:C[i]['wins'])
R1c = dict(x=C[best]['x'],y=C[best]['y'],road=C[best]['road'],wins=C[best]['wins'])
R1_raw = dict(R1c)
# R1 은 강건성 1위 후보를 60m 안의 가장 가까운 교차로(차수 3+, 부지 밖)로 스냅한다. 멀면 후보 위치 그대로.
Dd = json.load(open(WD + 'road_data.json', encoding='utf8'))
deg = {}
for l in Dd['links']:
    deg[l['f']] = deg.get(l['f'], 0) + 1; deg[l['t']] = deg.get(l['t'], 0) + 1
snap = None
for k, v in R['nodes'].items():
    if deg.get(k, 0) < 3 or site.contains(Point(v['x'], v['y'])): continue
    dd = math.hypot(v['x'] - R1c['x'], v['y'] - R1c['y'])
    if dd <= 60 and (snap is None or dd < snap[0]): snap = (dd, v['x'], v['y'], v.get('name', ''))
if snap:
    R1c['x'], R1c['y'] = snap[1], snap[2]
dR1_A = snap[0] if snap else 0.0
R1_snap_name = snap[3] if snap else ''
dA_west = math.hypot(R1c['x'] - A['wx'], R1c['y'] - A['wy'])
# R2: R1 과 다른 도로, 파레토 비지배, 부지 북쪽 1/3 안에서 가장 북쪽 후보
ymid = (site.bounds[1] + site.bounds[3]) / 2
north_i = [i for i in range(len(C)) if C[i]['road'] != R1c['road'] and C[i]['pareto_wd18'] and C[i]['y'] > ymid]
if not north_i:
    north_i = [i for i in range(len(C)) if C[i]['road'] != R1c['road'] and C[i]['y'] > ymid] or list(range(len(C)))
j = max(north_i, key=lambda i: C[i]['y'])
R2c = dict(x=C[j]['x'], y=C[j]['y'], road=C[j]['road'], wins=C[j]['wins'], pareto=C[j]['pareto_wd18'])

out = dict(
    site=R['site'], axis=list(ax), ew=list(ew),
    R1=dict(x=R1c['x'], y=R1c['y'], road=R1c['road'], wins=R1c['wins'], n_scen=len(R['scen']), moved_from=[R1_raw['x'], R1_raw['y']], moved_m=dR1_A,
            snap_node=R1_snap_name, dist_to_A_west=dA_west),
    R2=dict(x=R2c['x'], y=R2c['y'], road=R2c['road'], wins=R2c['wins'], pareto=R2c['pareto']) if R2c else None,
    clusters=[dict(x=z['x'], y=z['y'], road=z['road'], wins=z['wins'], rs=z['rs'], pareto=z['pareto']) for z in clusters],
    A=A, B=B, S=S, spine=spine, axis_len=float(smax - smin),
    gaps=dict(before=ga, with_A=gb, with_A_B=gc),
)
json.dump(out, open(WD + 'plan.json', 'w', encoding='utf8'), ensure_ascii=False)
print('R1', out['R1']); print('R2', out['R2'])
print('A', {k: (round(v, 1) if isinstance(v, float) else v) for k, v in A.items() if k in ('wname', 'ename', 'wx', 'wy', 'ex', 'ey', 'length', 'inside', 'dev', 'gain', 'detour_old', 'rank_sum', 'pareto')})
print('B', {k: (round(v, 1) if isinstance(v, float) else v) for k, v in B.items() if k in ('wname', 'ename', 'wx', 'wy', 'ex', 'ey', 'length', 'inside', 'dev', 'gain', 'detour_old', 'rank_sum', 'pareto')})
print('axis len', smax - smin, 'gaps before/A/A+B', [round(g) for g in ga], [round(g) for g in gb], [round(g) for g in gc])
print('clusters top', [(z['road'], round(z['x']), round(z['y']), z['wins'], z['pareto']) for z in clusters[:6]])
print('spine pts', len(spine), 'width min/max', round(min(s[2] for s in spine)), round(max(s[2] for s in spine)))
