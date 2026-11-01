# road_result/plan/blocks/road_data/context → web/viz_data.js (국소 좌표, 미터). 웹 근거 페이지 입력.
import json, math, os
import numpy as np
from shapely.geometry import Polygon, LineString, Point, shape
from collections import defaultdict

WD = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.sep
R = json.load(open(WD + 'road_result.json', encoding='utf8')); P = json.load(open(WD + 'plan.json', encoding='utf8'))
K = json.load(open(WD + 'blocks.json', encoding='utf8')); D = json.load(open(WD + 'road_data.json', encoding='utf8')); X = json.load(open(WD + 'context.json', encoding='utf8'))
ORG = (219780.0, 360990.0)
def L(x, y): return [round(x - ORG[0], 1), round(y - ORG[1], 1)]
def LL(coords): return [L(c[0], c[1]) for c in coords]
site = Polygon(P['site'])
out = {'org': ORG, 'site': LL(P['site'])}

bg = []
for p in D['road_polys']:
    g = Polygon(p)
    if g.distance(site) > 480: continue
    g = g.simplify(1.0)
    bg.append(LL(list(g.exterior.coords)))
out['bg'] = bg

links = []
for l in R['disp']:
    ser = sorted(l['wd'] + l['we']); ff = ser[int(0.9 * 47)]
    links.append(dict(id=l['id'], name=l['name'], rank=l['rank'], lanes=l['lanes'], width=l['width'], imputed=l['imputed'], in_site=l['in_site'], ff=round(ff, 1),
                      wd=[round(v, 1) for v in l['wd']], we=[round(v, 1) for v in l['we']], xy=LL(l['xy'])))
out['links'] = links

cands = []
for i, c in enumerate(R['cands']):
    p = L(c['x'], c['y'])
    cands.append(dict(i=i, x=p[0], y=p[1], road=c['road'], rank=c['rank'], lanes=c['lanes'], width=c['width'], dnode=round(c['dnode']), bus=c['bus'], turns=len(c['turns']),
                      wins=c['wins'], rs=round(c['rank_sum_mean'], 1), pareto=c['pareto_wd18'],
                      acc={k: {g: round(v / 60, 1) for g, v in a.items()} for k, a in c['acc'].items()},
                      spd={k: c['spd'][k] for k in ('wd08', 'wd12', 'wd18', 'we12') if k in c['spd']}))
out['cands'] = cands
out['groups'] = R['groups']

pairs = []
for p in R['ew_pairs']:
    pairs.append(dict(w=L(p['wx'], p['wy']), e=L(p['ex'], p['ey']), length=round(p['length']), inside=round(p['inside']), dev=round(p['dev'], 1), align_w=round(p['align_w']), align_e=round(p['align_e']),
                      gain=round(p['gain']), detour=round(p['detour_old'], 2) if p['detour_old'] else None, wname=p['wname'], ename=p['ename'], rs=p['rank_sum'], pareto=p['pareto'], yc=round((p['wy'] + p['ey']) / 2 - ORG[1])))
out['pairs'] = pairs

A, B = P['A'], P['B']; C = K['C']
def pr(p, keys):
    return dict(w=L(p['wx'], p['wy']), e=L(p['ex'], p['ey']), length=round(p['length']), inside=round(p['inside']), dev=round(p['dev'], 1), align=[round(p['align_w']), round(p['align_e'])],
                gain=round(p['gain']), detour=round(p['detour_old'], 1), names=[p['wname'], p['ename']], rs=p['rank_sum'])
out['plan'] = dict(
    A=pr(A, None), B=pr(B, None),
    C=dict(w=L(C['wx'], C['wy']), e=L(C['ex'], C['ey']), length=round(C['length']), inside=round(C['inside']), names=[C['wname'], C['ename']], note=C['note']),
    spine=[L(x, y) for x, y, w in P['spine']], spine_w=[round(w) for x, y, w in P['spine']],
    R1=dict(p=L(P['R1']['x'], P['R1']['y']), raw=L(*P['R1']['moved_from']), road=P['R1']['road'], wins=P['R1']['wins'], n=P['R1']['n_scen'], snap=P['R1'].get('snap_node', ''), moved=round(P['R1']['moved_m'])),
    R2=dict(p=L(P['R2']['x'], P['R2']['y']), road=P['R2']['road'], pareto=P['R2'].get('pareto')),
    gaps=P['gaps'], axis_len=round(P['axis_len']),
    ped=[LL(p['line']) for p in K.get('ped', [])],
    cw_new=[dict(p=L(c['x'], c['y']), road=c['road'], kind=c['kind'], why=c['why']) for c in K['cw_new']],
    stops_new=[dict(p=L(s['x'], s['y']), road=s['road'], why=s['why']) for s in K['stops_new']],
)
out['stops'] = [dict(p=L(s['x'], s['y']), name=s['name']) for s in R['stops'] if Point(s['x'], s['y']).distance(site) < 450]

sb = K.get('station')
out['ctx'] = dict(
    station_bbox=[L(sb['bounds'][0], sb['bounds'][1]), L(sb['bounds'][2], sb['bounds'][3])] if sb else None,
    footbridge=LL(X['footbridge'][0]['xy']) if X.get('footbridge') else None,
    godo15=[LL(shape(g['geom']).exterior.coords) for g in X['godo'] if g['h_max'] == 15 and shape(g['geom']).geom_type == 'Polygon'],
    market=L(X['seongdong_market']['x'], X['seongdong_market']['y']) if X.get('seongdong_market') else None,
    heritage=[dict(p=L(h['x'], h['y']), name=h['name']) for h in X.get('heritage', []) if h['dist_site'] < 50],
)

adj = defaultdict(list)
for l in D['links']:
    if l['dist_site'] <= 15 and LineString(l['xy']).intersection(site).length <= 0.5 * l['len']:
        adj[(l['name'], l['rank'])].append(l)
fr = []
for k, v in sorted(adj.items(), key=lambda kv: -sum(x['len'] for x in kv[1])):
    ws = [x['width'] for x in v if x['width']]
    fr.append(dict(name=k[0], rank=k[1], links=len(v), length=round(sum(x['len'] for x in v)), lanes=sorted(set(x['lanes'] for x in v)),
                   width=round(float(np.median(ws)), 1) if ws else None, spd=sorted(set(x['spd'] for x in v)), hist=sum(1 for x in v if x['hist'])))
out['frontage'] = fr

EW = np.array(P['ew']); c0 = np.array(P['site'][:-1]).mean(0)
nodes = D['nodes']; legs = defaultdict(list)
for l in D['links']:
    legs[l['f']].append(l); legs[l['t']].append(l)
def brg(node, l):
    xy = l['xy']; a, b = (xy[0], xy[1]) if l['f'] == node else (xy[-1], xy[-2]); return math.atan2(b[1] - a[1], b[0] - a[0])
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
ewang = math.atan2(EW[1], EW[0])
wst = {}
for k, v in nodes.items():
    p = Point(v['x'], v['y'])
    if p.distance(site) > 60 or site.contains(p): continue
    side = (np.array([v['x'] - c0[0], v['y'] - c0[1]]) @ EW)
    for l in legs[k]:
        if l['name'] in ('원화로', '-'): continue
        b = brg(k, l); dev = min(abs(math.degrees(wrap(b - ewang))), abs(math.degrees(wrap(b - ewang - math.pi))))
        if dev < 25:
            key = ('W' if side < 0 else 'E', l['name'], round(v['y'] / 40))
            wst[key] = dict(side=key[0], name=l['name'], y=round(v['y'] - ORG[1]), x=round(v['x'] - ORG[0]))
out['side_streets'] = sorted(wst.values(), key=lambda d: (d['side'], d['y']))
out['dest'] = {k: dict(x=round(v['x'] - ORG[0]), y=round(v['y'] - ORG[1]), kind=v['kind']) for k, v in R['dest'].items()}
out['meta'] = dict(n_links=len(links), n_hist=sum(1 for l in links if not l['imputed']), n_scen=len(R['scen']), n_cands=len(cands), n_pairs=len(pairs), site_area=round(site.area))
s = 'window.VIZ=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';'
open(os.path.join(WD, 'web', 'viz_data.js'), 'w', encoding='utf8').write(s)
print('bytes', len(s.encode('utf8')), 'bg', len(bg), 'links', len(links))
print('side streets', out['side_streets'])
print('frontage', [(f['name'], f['length'], f['lanes'], f['width']) for f in fr])
print('gaps', out['plan']['gaps'], 'axis', out['plan']['axis_len'])
print('A', out['plan']['A']); print('B', out['plan']['B']); print('C', out['plan']['C'])
print('R1', out['plan']['R1'], 'R2', out['plan']['R2'])
print('top cands', sorted([(c['wins'], c['road'], c['x'], c['y']) for c in cands], reverse=True)[:5])
