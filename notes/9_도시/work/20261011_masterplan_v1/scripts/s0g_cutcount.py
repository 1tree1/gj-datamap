"""등록 후보 탐색: 경계 U 를 (맥락×2)에 얹었을 때 경계선이 건물·획지(대지)·인도 면을 몇 개나 가르는지 센다. 진짜 정합이라면(경계를 필지·인도에 맞췄다면) 가르는 개수가 뚜렷한 최소가 된다."""
import json, pickle, numpy as np, math, time
from shapely.geometry import Polygon, LineString, box
from shapely import STRtree, affinity
import xf as XF
U = pickle.load(open('../data/U_clean.pkl', 'rb'))['U']
C = json.load(open('../data/ctx_candidates.json', encoding='utf-8'))      # T 좌표계 건물 footprint(옛 변환 T)
t_a = np.array([-1143000.06, -1763303.35])
bl = []
for o in C:
    if o['layer'] != '빌딩' or not o.get('rings'): continue
    a = XF.plan2ctx(np.array(o['rings'][0])); 
    p = Polygon(2 * a + t_a)
    if p.is_valid and p.area > 3: bl.append(p)
print('buildings', len(bl))
tree = STRtree(bl)
ring = U.exterior
def count(shift):
    r = affinity.translate(ring, -shift[0], -shift[1])      # 맥락을 +shift 이동 ≡ U 를 −shift 이동
    idx = tree.query(r, predicate='intersects'); return len(idx)
t0 = time.time(); res = []
for dx in np.arange(-300, 300.1, 3.0):
    for dy in np.arange(-300, 300.1, 3.0):
        res.append((count((dx, dy)), dx, dy))
res.sort()
print('%.1fs' % (time.time() - t0))
print('baseline at t_a: %d | median over grid %d | min %d' % (count((0, 0)), int(np.median([r[0] for r in res])), res[0][0]))
for r in res[:12]: print('cut buildings %d at shift (%.0f, %.0f)' % r)
