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
lines = []
for f in F:
    if f['layer'] in ('대지', '인도'):
        lines.append(XF.plan2ctx(np.array(f['ring'])))
        for h in f['holes']:
            if len(h) > 3: lines.append(XF.plan2ctx(np.array(h)))
x0, y0 = c_v3 - np.array([330, 400]); x1, y1 = c_v3 + np.array([330, 400]); RES = 0.5
W = int((x1 - x0) / RES); H = int((y1 - y0) / RES)
img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
for a in lines:
    px = ((a[:, 0] - x0) / RES); py = (H - (a[:, 1] - y0) / RES)
    if len(a) > 200000: continue
    dr.line(list(zip(px.tolist(), py.tolist())), fill=255, width=1)
dist = ndimage.distance_transform_edt(np.array(img) == 0) * RES      # old units
Bp = np.array([U.exterior.interpolate(d).coords[0] for d in np.arange(0, U.exterior.length, 4.0)])
Bc = Bp - c_U
t0 = time.time(); best = []
for rho in np.arange(-6, 6.01, 0.5):
    r = math.radians(rho); R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
    base = (Bc @ R) / 2.0        # relative to the shift
    dxs = np.arange(-200, 200.1, 2.0)
    for dy in np.arange(-200, 200.1, 2.0):
        O = base[None, :, :] - (np.stack([dxs, np.full_like(dxs, dy)], 1)[:, None, :] / 2.0) + c_v3
        ix = np.clip(((O[:, :, 0] - x0) / RES).astype(int), 0, W - 1); iy = np.clip(((H - (O[:, :, 1] - y0) / RES)).astype(int), 0, H - 1)
        d = dist[iy, ix] * 2.0
        frac = (d <= 1.5).mean(1)
        j = int(frac.argmax()); best.append((frac[j], rho, dxs[j], dy))
best.sort(reverse=True)
print('%.1fs' % (time.time() - t0))
for b in best[:12]: print('within1.5m %.1f%%  rho %.1f  dx %.0f dy %.0f' % (b[0] * 100, b[1], b[2], b[3]))
