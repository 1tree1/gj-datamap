import json, pickle, numpy as np, math, time
import xf as XF
U = pickle.load(open('../data/U_clean.pkl', 'rb'))['U']
F = json.load(open('../data/ctx_faces.json', encoding='utf-8'))
G = pickle.load(open('../data/geo.pkl', 'rb'))
# U 정점(직선 구간 모서리만): shapely 단순화
Us = U.simplify(0.05)
uv = np.array(Us.exterior.coords)[:-1]
print('U vertices', len(uv))
# 맥락 정점(옛 좌표) — 대지·인도·경계석 면의 외곽·구멍, 도로면 구멍
V = []
for f in F:
    if f['layer'] == '도로':
        for h in f['holes']:
            if 3 < len(h) < 5000: V.append(XF.plan2ctx(np.array(h)))
    else:
        V.append(XF.plan2ctx(np.array(f['ring'])))
        for h in f['holes']:
            if len(h) > 3: V.append(XF.plan2ctx(np.array(h)))
# 정점만 추리기: 각 링에서 각도 변화가 큰 점
def corners(a, tol=8.0):
    if len(a) < 4: return a
    p = a[:-1] if np.allclose(a[0], a[-1]) else a
    d1 = p - np.roll(p, 1, axis=0); d2 = np.roll(p, -1, axis=0) - p
    ang = np.degrees(np.abs(np.arctan2(d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0], (d1*d2).sum(1))))
    return p[ang > tol]
C = np.vstack([corners(a) for a in V if len(a) < 200000])
print('context corner points', len(C))
# 투표: t = u - 2*R*c (R = rot by rho)
t_a = np.array([-1143000.06, -1763303.35])
res = []
t0 = time.time()
for rho in np.arange(-4.0, 4.01, 0.5):
    r = math.radians(rho); R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
    C2 = 2 * (C @ R.T)
    # 후보 t 범위: t_a ± 500 m
    D = uv[:, None, :] - C2[None, :, :]                 # (nU, nC, 2)
    D = D.reshape(-1, 2)
    sel = (np.abs(D[:, 0] - t_a[0]) < 500) & (np.abs(D[:, 1] - t_a[1]) < 500)
    D = D[sel]
    bins = 0.6
    ix = np.floor((D[:, 0] - (t_a[0] - 500)) / bins).astype(int); iy = np.floor((D[:, 1] - (t_a[1] - 500)) / bins).astype(int)
    nb = int(1000 / bins) + 1
    H = np.zeros((nb, nb), int); np.add.at(H, (ix, iy), 1)
    # 3x3 합(0.6~1.8 m 허용)
    from scipy.ndimage import uniform_filter
    Hs = uniform_filter(H.astype(float), size=3) * 9
    k = np.unravel_index(Hs.argmax(), Hs.shape)
    res.append((Hs.max(), rho, t_a[0] - 500 + k[0] * bins, t_a[1] - 500 + k[1] * bins, np.median(Hs)))
res.sort(reverse=True)
print('%.1fs' % (time.time() - t0))
for r in res[:8]: print('votes %.0f (median %.1f)  rho %.1f  t = (%.1f, %.1f)   shift from t_a = (%.1f, %.1f)' % (r[0], r[4], r[1], r[2], r[3], r[2] - t_a[0], r[3] - t_a[1]))

# ---- 후보 변환별 일치 정점 수(허용 1.2 m) ----
from scipy.spatial import cKDTree
tree = cKDTree(2 * C)
def matches(t, tol=1.2):
    d, j = tree.query(uv - t); return int((d <= tol).sum()), d, j
cands = {'t_a (station centroid anchor)': t_a, 't_IoU (v3x2 ~ U)': t_a + [-13.2, 61.8], 't_vote (peak)': res[0][2:4] and np.array([res[0][2], res[0][3]])}
for k, t in cands.items():
    n, d, j = matches(np.asarray(t, float))
    print('%-32s t=(%.1f, %.1f)  U vertices within 1.2 m of a context corner: %d / %d' % (k, t[0], t[1], n, len(uv)))
# refine the peak with fine grid
tv = np.array([res[0][2], res[0][3]])
best = (0, tv)
for dx in np.arange(-3, 3.01, 0.1):
    for dy in np.arange(-3, 3.01, 0.1):
        n, d, j = matches(tv + [dx, dy], 0.5)
        if n > best[0]: best = (n, tv + [dx, dy])
print('refined peak: t=(%.2f, %.2f) vertices within 0.5 m: %d' % (best[1][0], best[1][1], best[0]))
n, d, j = matches(best[1], 0.5)
idx = np.where(d <= 0.5)[0]
print('matched U vertex local coords (x-1167200, y-1761100):', [(round(uv[i][0] - 1167200, 1), round(uv[i][1] - 1761100, 1)) for i in idx][:50])
pickle.dump(dict(t=best[1].tolist(), n=n), open('../data/xf_vote.pkl', 'wb'))
