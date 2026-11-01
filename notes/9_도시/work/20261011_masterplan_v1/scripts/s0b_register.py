"""S0b 맥락 ↔ 계획 정합(좌표 변환) 재산정. 이전 변환(구 역사 건물 복사본 기준, −33.79°)은 틀렸다: 사용자가 건물만 따로 돌려 놓았다.
계획 경계 U 는 옛 매입경계 v3(옛 좌표 반축척)를 2배 한 것의 확장판(IoU 0.95)이므로, 맥락의 필지·인도 선과 U 가 가장 잘 겹치는 (회전, 이동)을 찾는다(축척 2.0 고정)."""
import json, pickle, numpy as np, math, time
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from PIL import Image, ImageDraw
from scipy import ndimage
import xf as XF            # 이전 변환(−33.79°) — 옛 좌표 복원용으로만 쓴다

U = pickle.load(open('../data/U_clean.pkl', 'rb'))['U']
F = json.load(open('../data/ctx_faces.json', encoding='utf-8'))
OB = json.load(open('../data/old_boundaries.json'))
v3 = Polygon(np.array(OB['v3'][0])[:, :2]).buffer(0)
c_v3 = np.array(v3.centroid.coords[0]); c_U = np.array(U.centroid.coords[0])
# 옛 좌표 선(필지·인도·경계석·하천 면의 바깥선·구멍선, 도로면의 구멍선)
lines = []
def add(r):
    a = XF.plan2ctx(np.array(r)); 
    if len(a) > 3: lines.append(a)
for f in F:
    if f['layer'] == '도로':
        for h in f['holes']: add(h)
        if len(f['ring']) < 5000: add(f['ring'])
    else:
        add(f['ring']);
        for h in f['holes']: add(h)
print('lines', len(lines))
x0, y0 = c_v3 - np.array([260, 330]); x1, y1 = c_v3 + np.array([260, 330])
RES = 0.25   # 옛 단위(=0.5 m)
W = int((x1 - x0) / RES); H = int((y1 - y0) / RES)
img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
for a in lines:
    px = ((a[:, 0] - x0) / RES); py = (H - (a[:, 1] - y0) / RES)
    if px.max() < 0 or px.min() > W or py.max() < 0 or py.min() > H: continue
    dr.line(list(zip(px.tolist(), py.tolist())), fill=255, width=1)
dist = ndimage.distance_transform_edt(np.array(img) == 0) * RES        # 옛 단위
print('raster', W, H, 'dist max %.1f' % dist.max())
Bp = np.array([U.exterior.interpolate(d).coords[0] for d in np.arange(0, U.exterior.length, 2.0)])
def obj(rho, p0, cap=6.0):
    r = math.radians(rho); R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
    # P = 2 R (O - c_v3) + p0  → O = R^T (P - p0) / 2 + c_v3
    O = ((Bp - p0) @ R) / 2.0 + c_v3
    ix = np.clip(((O[:, 0] - x0) / RES).astype(int), 0, W - 1); iy = np.clip(((H - (O[:, 1] - y0) / RES)).astype(int), 0, H - 1)
    d = dist[iy, ix] * 2.0          # m
    return np.minimum(d, cap).mean(), d
best = (9e9, None)
t0 = time.time()
for rho in np.arange(-6.0, 8.01, 0.25):
    for dx in np.arange(-24, 24.1, 2.0):
        for dy in np.arange(-24, 24.1, 2.0):
            v, _ = obj(rho, c_U + np.array([dx, dy]))
            if v < best[0]: best = (v, (rho, dx, dy))
print('coarse best', best, '%.1fs' % (time.time() - t0))
from scipy.optimize import minimize
r0 = best[1]
res = minimize(lambda p: obj(p[0], c_U + p[1:3])[0], list(r0), method='Nelder-Mead', options=dict(xatol=0.02, fatol=1e-4, maxiter=400))
rho, dx, dy = res.x
v, d = obj(rho, c_U + np.array([dx, dy]))
print('refined: rho %.3f deg  shift (%.2f, %.2f)  mean capped dist %.3f m' % (rho, dx, dy, v))
for t in (0.3, 0.5, 1.0, 2.0, 5.0): print('  U boundary within %.1f m of context edges: %.1f%%' % (t, (d <= t).mean() * 100))
# control: same objective at rho=-33.79 (old transform) 
v0, d0 = obj(0.0, c_U); print('control (rho 0, centroid-aligned): mean %.2f  within 1 m %.1f%%' % (v0, (d0 <= 1).mean() * 100))
pickle.dump(dict(rho=float(rho), p0=(c_U + np.array([dx, dy])).tolist(), o0=c_v3.tolist(), scale=2.0), open('../data/xf_true.pkl', 'wb'))
