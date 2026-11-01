"""S1b 최종 정합 변환으로 건물 분류(안/걸침/밖). ctx_candidates.json 은 옛 변환 T(xf_old) 좌표라 옛 좌표로 되돌린 뒤 새 변환을 적용한다."""
import json, pickle, numpy as np, collections
from shapely.geometry import Polygon
from shapely.prepared import prep
import xf as XF, xf_old as XO
U = pickle.load(open('../data/U_clean.pkl', 'rb'))['U']; PU = prep(U)
C = json.load(open('../data/ctx_candidates.json', encoding='utf-8'))
full, cut, keep = [], [], 0
stats = collections.Counter(); ratios = []
for o in C:
    if o['layer'] != '빌딩' or not o.get('rings'): continue
    best = None
    a = XF.ctx2plan(XO.plan2ctx(np.array(o['rings'][0])))
    p = Polygon(a)
    if not p.is_valid: p = p.buffer(0)
    if p.is_empty or p.area <= 0: continue
    r = p.intersection(U).area / p.area
    if r >= 0.999: full.append(o['id'][:8]); stats['in'] += 1
    elif r > 0.001: cut.append(o['id'][:8]); stats['cut'] += 1; ratios.append(r)
    else: stats['out'] += 1
print(dict(stats), 'cut ratios: min %.2f max %.2f' % (min(ratios or [0]), max(ratios or [0])))
json.dump(dict(full=full, cut=cut), open('../data/bld_plan2.json', 'w'))
json.dump(dict(full=full, cut=cut), open(r'C:/Users/OFFICE/AppData/Local/Temp/claude/C--Users-OFFICE-Desktop-9---/208a6fca-848a-4422-ad91-655fc023df64/scratchpad/bld_plan2.json', 'w'))
