"""S0c 회전 0°·축척 2.0 고정, 이동량만 넓게 탐색해 U 와 맥락 필지·인도 선의 정합 지형을 본다."""
import json, pickle, numpy as np, math, time
from shapely.geometry import Polygon
from PIL import Image, ImageDraw
from scipy import ndimage
import xf as XF
U = pickle.load(open('../data/U_clean.pkl', 'rb'))['U']
F = json.load(open('../data/ctx_faces.json', encoding='utf-8'))
OB = json.load(open('../data/old_boundaries.json'))
v3 = Polygon(np.array(OB['v3'][0])[:, :2]).buffer(0)
c_v3 = np.array(v3.centroid.coords[0]); c_U = np.array(U.centroid.coords[0])
lines = {'lot': [], 'walk': [], 'curb': [], 'roadhole': []}
for f in F:
    a_ring = XF.plan2ctx(np.array(f['ring'])); holes = [XF.plan2ctx(np.array(h)) for h in f['holes'] if len(h) > 3]
    if f['layer'] == '대지': lines['lot'] += [a_ring] + holes
    elif f['layer'] == '인도': lines['walk'] += [a_ring] + holes
    elif f['layer'] == '경계석': lines['curb'] += [a_ring]
    elif f['layer'] == '도로': lines['roadhole'] += holes
x0, y0 = c_v3 - np.array([260, 330]); x1, y1 = c_v3 + np.array([260, 330]); RES = 0.25
W = int((x1 - x0) / RES); H = int((y1 - y0) / RES)
def raster(keys):
    img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
    for k in keys:
        for a in lines[k]:
            px = ((a[:, 0] - x0) / RES); py = (H - (a[:, 1] - y0) / RES)
            if px.max() < 0 or px.min() > W or py.max() < 0 or py.min() > H or len(a) > 200000: continue
            dr.line(list(zip(px.tolist(), py.tolist())), fill=255, width=1)
    return ndimage.distance_transform_edt(np.array(img) == 0) * RES
Bp = np.array([U.exterior.interpolate(d).coords[0] for d in np.arange(0, U.exterior.length, 1.0)])
def evaluate(dist, dx, dy, rho=0.0):
    r = math.radians(rho); R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
    O = ((Bp - (c_U + np.array([dx, dy]))) @ R) / 2.0 + c_v3
    ix = np.clip(((O[:, 0] - x0) / RES).astype(int), 0, W - 1); iy = np.clip(((H - (O[:, 1] - y0) / RES)).astype(int), 0, H - 1)
    return dist[iy, ix] * 2.0
for name, keys in (('모든 선', ['lot', 'walk', 'curb', 'roadhole']), ('필지(대지)+인도', ['lot', 'walk']), ('인도+경계석', ['walk', 'curb'])):
    dist = raster(keys); best = None; grid = {}
    for dx in np.arange(-90, 90.1, 1.0):
        for dy in np.arange(-90, 90.1, 1.0):
            d = evaluate(dist, dx, dy); v = (d <= 1.0).mean(); m3 = np.minimum(d, 3.0).mean()
            grid[(dx, dy)] = (v, m3)
            if best is None or v > best[0]: best = (v, m3, dx, dy)
    bm = min(grid.items(), key=lambda kv: kv[1][1])
    print('%-14s best within-1m %.1f%% at (%.0f,%.0f) [mean3 %.2f] | best mean3 %.2f at (%.0f,%.0f) [within1 %.1f%%]' % (name, best[0] * 100, best[2], best[3], best[1], bm[1][1], bm[0][0], bm[0][1], bm[1][0] * 100))
    # curvature of landscape: how much better than median?
    vals = np.array([v for v, m in grid.values()]); print('   within-1m: median %.1f%% p95 %.1f%% max %.1f%%' % (np.median(vals) * 100, np.percentile(vals, 95) * 100, vals.max() * 100))
    pickle.dump(grid, open('../data/reg_grid_%d.pkl' % len(keys), 'wb'))
