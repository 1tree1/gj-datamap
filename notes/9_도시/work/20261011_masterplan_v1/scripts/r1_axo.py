"""R1 조감(축측) 렌더 — PyVista 오프스크린 + 투영행렬. 통영 p.32 'Site Anchors' 형식(층별 색 적층, 지면 그림자, 주변 건물 흰 매스, 가장자리 페이드).
입력: data/lots.pkl · masses.pkl · design_extra.pkl · ctx_buildings_planframe.json (좌표는 라이노 평면 좌표에서 (OX,OY)를 뺀 로컬 m)
사용: python r1_axo.py [az] [out.png] [W] [H]  → out.png + out_meta.pkl"""
import os, sys, math, json, pickle, random, time
import numpy as np
import pyvista as pv
import trimesh
from shapely.geometry import Polygon, MultiPolygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
from PIL import Image, ImageDraw
from scipy import ndimage
pv.OFF_SCREEN = True
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); SH = os.path.join(HERE, "..", "sheets")
L = pickle.load(open(os.path.join(D, "lots.pkl"), "rb")); M = pickle.load(open(os.path.join(D, "masses.pkl"), "rb")); X = pickle.load(open(os.path.join(D, "design_extra.pkl"), "rb"))
LOT, GRN, WALKS, ROADS, U, OX, OY = L["LOT"], L["GRN"], L["WALKS"], L["ROADS"], L["U"], L["OX"], L["OY"]
masses = M["masses"]; PLZ, PAV, TREES = X["PLZ"], X["PAV"], X["TREES"]
CTXB = json.load(open(os.path.join(D, "ctx_buildings_planframe.json")))
BG = "#eceee8"
GREEN_ROOF = "#a9d577"


def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []


def rgb(h, f=1.0):
    c = np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) * f
    return np.clip(c, 0, 255).astype(np.uint8)


def lerp(h1, h2, t):
    a = np.array([int(h1[i:i + 2], 16) for i in (1, 3, 5)], float); b = np.array([int(h2[i:i + 2], 16) for i in (1, 3, 5)], float)
    return np.clip(a * (1 - t) + b * t, 0, 255).astype(np.uint8)


def tint(h, t):
    c = np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) * (1 - t) + 255 * t
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)


class Acc:
    def __init__(self): self.v, self.f, self.c = [], [], []; self.n = 0
    def tri(self, V, F, color):
        V = np.asarray(V, float); F = np.asarray(F, int)
        self.v.append(V); self.f.append(F + self.n); self.c.append(np.tile(color, (len(F), 1))); self.n += len(V)
    def quad(self, p0, p1, p2, p3, color): self.tri(np.array([p0, p1, p2, p3], float), [[0, 1, 2], [0, 2, 3]], color)
    def mesh(self):
        if not self.v: return None
        V = np.vstack(self.v); F = np.vstack(self.f); col = np.vstack(self.c)
        m = pv.PolyData(V, np.hstack([np.full((len(F), 1), 3), F]).ravel()); m.cell_data["rgb"] = col.astype(np.uint8); return m


def flat(acc, poly, z, color):
    for p in polys(poly):
        if p.area < 0.3: continue
        try: v, f = trimesh.creation.triangulate_polygon(p, engine="earcut")
        except Exception: continue
        acc.tri(np.column_stack([v[:, 0], v[:, 1], np.full(len(v), z)]), f, color)


def walls(acc, poly, z0, z1, color):
    for p in polys(poly):
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)
            for i in range(len(cs) - 1):
                a, b = cs[i], cs[i + 1]
                acc.quad((a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1), color)


def tree_mesh(acc, x, y, r, color, z0=0.0):
    s = pv.Sphere(radius=r, center=(x, y, z0 + 3.0 + 0.8 * r), theta_resolution=9, phi_resolution=7).triangulate()
    acc.tri(np.asarray(s.points), s.faces.reshape(-1, 4)[:, 1:], color)
    acc.quad((x - .25, y, z0), (x + .25, y, z0), (x + .25, y, z0 + 3.0), (x - .25, y, z0 + 3.0), rgb("#8b7355"))


def build():
    t0 = time.time(); rnd = random.Random(7)
    ground = Acc(); sh = Acc(); ctx = Acc(); bld = Acc(); roofs = Acc(); tr = Acc(); rims = []
    bb = U.buffer(300).bounds
    flat(ground, box(*bb), -0.3, rgb("#e3e8dc"))
    flat(ground, U, -0.2, rgb("#f0efeb"))
    for w in WALKS: flat(ground, w, 0.0, rgb("#fbfbfa"))
    for r in ROADS: flat(ground, r, 0.02, rgb("#d9d9d6"))
    cm = {"공공업무": "#4C78B8", "상업·업무": "#E4573A", "주거": "#F1D247", "문화·교육·공공": "#6F9FDC", "창조산업": "#A98BD3", "판매·음식": "#F4A0C2", "여가·오락·체육": "#2FAB9D", "역사유산": "#C9742F", "교통·방문자": "#C6C6C6", "주차전용건축물": "#8E8E8E"}
    lot_cat = {"공1": "공공업무", "업1": "상업·업무", "업2": "상업·업무", "주1": "주거", "문1": "문화·교육·공공", "문2": "역사유산", "문3": "판매·음식", "문4": "창조산업", "문5": "창조산업", "상1": "판매·음식", "체1": "여가·오락·체육", "관1": "주차전용건축물"}
    for k, v in LOT.items(): flat(ground, v["g"], 0.05, rgb(tint(cm[lot_cat[k]], 0.86)))
    for k, v in GRN.items():
        flat(ground, v["g"], 0.08, rgb("#b4dc8e" if v["kind"] != "경관녹지" else "#a9d68a"))
    for p in PLZ: flat(ground, p["g"], 0.1, rgb("#c8b58a" if p["kind"] == "텃밭" else "#e7e1d0"))
    for kind, col in (("park", ("#7db84f", "#a3d070")), ("lot", ("#86c056", "#a8d377")), ("street", ("#7fba52", "#9fcf6e"))):
        for (x, y, r) in TREES[kind]: tree_mesh(tr, x, y, r, lerp(col[0], col[1], rnd.random()))
    # 그림자
    sx, sy = 0.62, -0.42
    allp = []
    for m in masses:
        h = m["h"] + 0.8; p = m["g"]; parts = [p, affinity.translate(p, sx * h, sy * h)]
        for pg in polys(p):
            cs = list(pg.exterior.coords)
            for i in range(len(cs) - 1):
                q = Polygon([cs[i], cs[i + 1], (cs[i + 1][0] + sx * h, cs[i + 1][1] + sy * h), (cs[i][0] + sx * h, cs[i][1] + sy * h)])
                if q.is_valid and q.area > 0: parts.append(q)
        allp.append(unary_union(parts))
    shadow = unary_union(allp).intersection(U.buffer(40)).difference(unary_union([m["g"] for m in masses]))
    flat(sh, shadow, 0.2, rgb("#27303c"))
    # 주변 건물(흰 매스)
    for b in CTXB:
        pts = [(x - OX, y - OY) for x, y in b["p"]]
        try: pg = Polygon(pts).buffer(0)
        except Exception: continue
        if pg.is_empty or pg.area < 8: continue
        d = pg.distance(U)
        if d > 290: continue
        h = max(b["h"], 3.5); t = float(np.clip((d - 70) / 220, 0, 0.75))
        wc = lerp("#f4f3f0", "#d9ded2", t); rc = lerp("#fbfbfa", "#e3e8dc", t)
        for p in polys(pg): walls(ctx, p, 0.0, h, wc); flat(ctx, p, h, rc)
    # 신규 매스(층별 색 적층)
    SLAB = 0.45
    for m in masses:
        p = m["g"]; n = m["floors"]; H = m["h"]; fh = H / n; base = m["color"]
        z = 0.0
        for k in range(n):
            walls(bld, p, z, z + fh - SLAB, rgb(base, 1.0)); walls(bld, p, z + fh - SLAB, z + fh, rgb(base, 1.16)); z += fh
        top = z
        rc = rgb("#a85a1e") if m["cat"] == "역사유산" else (rgb("#d7d7d7") if m["cat"] == "주차전용건축물" else rgb(base, 1.12))
        flat(roofs, p, top, rc)
        inner = p.buffer(-1.3, join_style=2)
        if m["cat"] not in ("역사유산", "주차전용건축물") and not inner.is_empty and inner.area > 25: flat(roofs, inner, top + 0.12, rgb(GREEN_ROOF))
        rims.append((p, top))
    for p in PAV:
        walls(bld, p, 0, 3.6, rgb("#B8A98A")); flat(roofs, p, 3.6, rgb("#d9cfb8"))
    print("scene built %.1fs  trees %d  ctx %d" % (time.time() - t0, sum(len(v) for v in TREES.values()), len(CTXB)))
    return dict(ground=ground, shadow=sh, ctx=ctx, bld=bld, roofs=roofs, trees=tr, rims=rims)


class Cam:
    def __init__(self, az_deg, el_deg, W, H, ps, xc, yc):
        a = math.radians(az_deg); e = math.radians(el_deg)
        self.a, self.e, self.W, self.H, self.ps, self.xc, self.yc = a, e, W, H, ps, xc, yc
        self.r = np.array([-math.sin(a), math.cos(a)]); self.f = np.array([-math.cos(a), -math.sin(a)])
    def XY(self, x, y, z=0.0):
        p = np.array([x, y]); return float(p @ self.r), float(p @ self.f) * math.sin(self.e) + z * math.cos(self.e)
    def xy(self, x, y, z=0.0):
        X_, Y_ = self.XY(x, y, z); k = self.H / (2 * self.ps)
        return self.W / 2 + (X_ - self.xc) * k, self.H / 2 - (Y_ - self.yc) * k


def render(az_deg=-35.0, el_deg=34.0, out=None, W=1710, Hh=3700, zoom=1.0, shift=(0.0, 0.0)):
    S = build()
    pl = pv.Plotter(off_screen=True, window_size=(W, Hh)); pl.set_background(BG)
    for key, op in (("ground", 1.0), ("shadow", 0.17), ("ctx", 1.0), ("trees", 1.0), ("bld", 1.0), ("roofs", 1.0)):
        m = S[key].mesh()
        if m is None: continue
        flatkey = key in ("ground", "shadow")
        pl.add_mesh(m, scalars="rgb", rgb=True, lighting=not flatkey, ambient=(1.0 if flatkey else 0.60), diffuse=(0.0 if flatkey else 0.52), specular=0.0, opacity=op, show_scalar_bar=False)
    segs = []
    for p, top in S["rims"]:
        for pg in polys(p):
            for ring in [pg.exterior] + list(pg.interiors):
                cs = list(ring.coords)
                for i in range(len(cs) - 1): segs.append(((cs[i][0], cs[i][1], top + 0.28), (cs[i + 1][0], cs[i + 1][1], top + 0.28)))
    if segs:
        pts = np.array([s for seg in segs for s in seg]); lines = np.hstack([[2, 2 * i, 2 * i + 1] for i in range(len(segs))])
        pl.add_mesh(pv.PolyData(pts, lines=lines), color="#555b52", line_width=1.1, opacity=0.5, lighting=False)
    a = math.radians(az_deg); e = math.radians(el_deg)
    c = np.array([math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)])
    cam0 = Cam(az_deg, el_deg, W, Hh, 1.0, 0.0, 0.0)
    pts2 = np.array([cam0.XY(x, y, z) for (x, y) in U.exterior.coords for z in (0, 34)])
    xmin, ymin = pts2.min(0); xmax, ymax = pts2.max(0)
    xc, yc = (xmin + xmax) / 2 + shift[0], (ymin + ymax) / 2 + shift[1]
    ps = max((ymax - ymin) / 2 * 1.10, (xmax - xmin) / 2 * 1.05 * Hh / W) / zoom
    Pf = xc * cam0.r + (yc / math.sin(e)) * cam0.f
    focal = np.array([Pf[0], Pf[1], 0.0])
    pl.camera.parallel_projection = True
    pl.camera_position = [tuple(focal + 3000 * c), tuple(focal), (0, 0, 1)]
    pl.camera.parallel_scale = ps; pl.camera.clipping_range = (10, 9000)
    pl.remove_all_lights()
    key = pv.Light(position=tuple(focal + 2000 * np.array([math.cos(a - 0.95) * 0.7, math.sin(a - 0.95) * 0.7, 0.95])), focal_point=tuple(focal), color="white", intensity=0.95, light_type="scene light")
    fill = pv.Light(position=tuple(focal + 2000 * np.array([math.cos(a + 2.3) * 0.6, math.sin(a + 2.3) * 0.6, 0.5])), focal_point=tuple(focal), color="white", intensity=0.32, light_type="scene light")
    pl.add_light(key); pl.add_light(fill); pl.enable_anti_aliasing("ssaa")
    img = pl.screenshot(None, return_img=True).astype(float)
    cam = Cam(az_deg, el_deg, W, Hh, ps, xc, yc)
    m = Image.new("L", (W, Hh), 0); dr = ImageDraw.Draw(m)
    for p in polys(U): dr.polygon([cam.xy(x, y, 0) for (x, y) in p.exterior.coords], fill=255)
    mask = np.array(m) > 0
    dist = ndimage.distance_transform_edt(~mask)
    d0, d1 = 0.10 * W, 0.34 * W
    al = np.clip((dist - d0) / (d1 - d0), 0, 1) ** 1.3 * 0.92
    bgc = np.array([int(BG[i:i + 2], 16) for i in (1, 3, 5)], float)
    img = img * (1 - al[..., None]) + bgc * al[..., None]
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); im.save(out)
    pickle.dump(dict(az=az_deg, el=el_deg, W=W, H=Hh, ps=ps, xc=xc, yc=yc), open(os.path.splitext(out)[0] + "_meta.pkl", "wb"))
    return out


if __name__ == "__main__":
    az = float(sys.argv[1]) if len(sys.argv) > 1 else -35.0
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(SH, "axo_v.png")
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 1710; H = int(sys.argv[4]) if len(sys.argv) > 4 else 3700
    t0 = time.time(); print("saved", render(az, out=out, W=W, Hh=H), "%.1fs" % (time.time() - t0))
