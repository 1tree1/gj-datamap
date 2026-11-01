import json, pickle, numpy as np, math
from PIL import Image, ImageDraw
from scipy import ndimage
import xf as XF
U = pickle.load(open('../data/U_clean.pkl', 'rb'))['U']
F = json.load(open('../data/ctx_faces.json', encoding='utf-8'))
t_a = np.array([-1143000.06, -1763303.35])
lines = []
for f in F:
    if f['layer'] in ('대지', '인도', '경계석'):
        lines.append(XF.plan2ctx(np.array(f['ring'])))
        for h in f['holes']:
            if len(h) > 3: lines.append(XF.plan2ctx(np.array(h)))
    elif f['layer'] == '도로':
        for h in f['holes']:
            if 3 < len(h) < 5000: lines.append(XF.plan2ctx(np.array(h)))
# raster in doubled(plan-like) coordinates for clarity: coordinates P = 2 O + t_a
allp = np.vstack([2 * a + t_a for a in lines]); x0, y0 = U.bounds[0] - 300, U.bounds[1] - 300; x1, y1 = U.bounds[2] + 300, U.bounds[3] + 300
RES = 0.5; W = int((x1 - x0) / RES); H = int((y1 - y0) / RES)
img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
for a in lines:
    p = 2 * a + t_a; px = (p[:, 0] - x0) / RES; py = H - (p[:, 1] - y0) / RES
    if px.max() < 0 or px.min() > W or py.max() < 0 or py.min() > H or len(a) > 200000: continue
    dr.line(list(zip(px.tolist(), py.tolist())), fill=255, width=1)
dist = ndimage.distance_transform_edt(np.array(img) == 0) * RES      # meters (plan units)
Bp = np.array([U.exterior.interpolate(d).coords[0] for d in np.arange(0, U.exterior.length, 1.0)])
def frac(shift):
    P = Bp - np.asarray(shift)       # moving the context by +shift  == moving U by -shift
    ix = np.clip(((P[:, 0] - x0) / RES).astype(int), 0, W - 1); iy = np.clip(((H - (P[:, 1] - y0) / RES)).astype(int), 0, H - 1)
    d = dist[iy, ix]; return [(d <= t).mean() * 100 for t in (0.5, 1, 2, 3)], np.median(d)
for name, sh in (('t_a (station anchor)', (0, 0)), ('t_a + (-13.2, 61.8) [IoU]', (-13.2, 61.8)), ('t_a + (3.4, -217.4) [vote]', (3.4, -217.4))):
    f, m = frac(sh); print('%-30s within 0.5/1/2/3 m: %s %%  median %.1f m' % (name, ' / '.join('%.0f' % v for v in f), m))
# local search around t_a for sanity (+-30 m): is t_a at a local optimum for within-2m?
best = None
for dx in np.arange(-30, 30.1, 1.0):
    for dy in np.arange(-30, 30.1, 1.0):
        f, m = frac((dx, dy))
        if best is None or f[2] > best[0]: best = (f[2], dx, dy, f)
print('best within-2m near t_a: %.1f%% at shift (%.0f, %.0f)  all: %s' % (best[0], best[1], best[2], ['%.0f' % v for v in best[3]]))
f0, _ = frac((0, 0)); print('at t_a exactly within 2m: %.1f%%' % f0[2])
