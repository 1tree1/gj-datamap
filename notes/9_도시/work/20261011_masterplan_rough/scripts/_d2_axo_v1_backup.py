"""D2 조감(축측) 렌더 — PyVista 오프스크린 평행투영. 통영 p.32 'Site Anchors' 형식
(층별 색 적층·슬래브 띠, 1층 가로상점 띠, 옥상 녹화, 지면 그림자, 주변 건물 흰 매스, 가장자리 페이드)
입력: data/design.pkl, ../20261011_masterplan_v1/data/ctx_buildings_planframe.json(v3 계획 프레임 → x−517.0557)
사용: python d2_axo.py [az] [out.png] [W] [H] → out.png + out_meta.pkl"""
import os, sys, math, json, pickle, random, time
import numpy as np
import pyvista as pv
import trimesh
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
from shapely import affinity
from PIL import Image, ImageDraw
from scipy import ndimage
pv.OFF_SCREEN = True
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); SH = os.path.join(HERE, "..", "sheets")
S = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
B, LOTS, PARKS, OPEN, MASS, PLZ, TREES, CATS = S["B"], S["LOTS"], S["PARKS"], S["OPEN"], S["MASS"], S["PLZ"], S["TREES"], S["CATS"]
X0, Y0, XS = S["X0"], S["Y0"], S["XSHIFT"]
CTXB = json.load(open(os.path.join(HERE, "..", "..", "20261011_masterplan_v1", "data", "ctx_buildings_planframe.json")))
BG = "#eceee8"; GREEN_ROOF = "#a9d577"; RETAIL = CATS["판매"][0]


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


SPH = pv.Sphere(radius=1.0, theta_resolution=9, phi_resolution=7).triangulate()
SPV, SPF = np.asarray(SPH.points), SPH.faces.reshape(-1, 4)[:, 1:]


def tree_mesh(acc, x, y, r, color, z0=0.0):
    acc.tri(SPV * r + np.array([x, y, z0 + 3.0 + 0.8 * r]), SPF, color)
    acc.quad((x - .25, y, z0), (x + .25, y, z0), (x + .25, y, z0 + 3.0), (x - .25, y, z0 + 3.0), rgb("#8b7355"))


def stripes(acc, poly, z, step, ang, w, color):
    """노외주차 구획선·텃밭 이랑 — poly 안에 평행선 띠"""
    c = poly.centroid; g = affinity.rotate(poly, -ang, origin=c)
    x0, y0, x1, y1 = g.bounds; xs = np.arange(x0 + step / 2, x1, step)
    bands = [box(x - w / 2, y0, x + w / 2, y1) for x in xs]
    flat(acc, affinity.rotate(unary_union(bands), ang, origin=c).intersection(poly), z, color)


def build():
    t0 = time.time(); rnd = random.Random(7)
    ground = Acc(); sh = Acc(); ctx = Acc(); bld = Acc(); roofs = Acc(); tr = Acc(); rims = []
    bb = B.buffer(420).bounds
    flat(ground, box(*bb), -0.3, rgb("#e3e8dc"))
    flat(ground, B, -0.2, rgb("#f0efeb"))
    flat(ground, S["WALK"], 0.0, rgb("#fbfbfa")); flat(ground, S["PATH8"], 0.0, rgb("#fbfbfa"))
    for r in S["ROADS"].values(): flat(ground, r, 0.02, rgb("#d6d6d3"))
    # 도로 중앙선(점선 대신 얇은 흰 선)
    for key, ln in (("EW", LineString([(100, 343.7), (420, 343.7)])), ("N", LineString([(100, 778.5), (254.5, 778.5), (348.5, 888.0), (390, 936)]))):
        flat(ground, ln.buffer(0.35).intersection(S["ROADS"][key]), 0.04, rgb("#f6f6f4"))
    for l in LOTS: flat(ground, l["g"], 0.05, rgb(tint(CATS[l["cat"]][0], 0.86)))
    for p in PARKS: flat(ground, p["g"], 0.08, rgb("#b4dc8e"))
    for o in OPEN:
        if o["key"] == "D": flat(ground, o["g"], 0.08, rgb("#bfe09b"))
        else: flat(ground, o["g"], 0.08, rgb("#ece7da"))
    for p in PLZ:
        k = p["kind"]
        if k == "광장": flat(ground, p["g"], 0.1, rgb("#e9e3d3"))
        elif k == "노외주차": flat(ground, p["g"], 0.1, rgb("#c9c9c6")); stripes(ground, p["g"], 0.12, 2.5, 0, 0.18, rgb("#f4f4f2"))
        elif k == "텃밭": flat(ground, p["g"], 0.1, rgb("#c8a878")); stripes(ground, p["g"].buffer(-1.2), 0.12, 3.0, 90, 1.6, rgb("#8fbf5a"))
        else: flat(ground, p["g"], 0.1, rgb("#bfe09b"))
    for kind, col in (("park", ("#78b44a", "#a3d070")), ("axis", ("#7fba52", "#9fcf6e")), ("lot", ("#86c056", "#a8d377")), ("street", ("#7fba52", "#9fcf6e"))):
        for (x, y, r) in TREES[kind]: tree_mesh(tr, x, y, r, lerp(col[0], col[1], rnd.random()))
    # 그림자(지면 투영)
    sx, sy = 0.62, -0.42
    allp = []
    for m in MASS:
        h = m["h"] + 0.8; p = m["g"]; parts = [p, affinity.translate(p, sx * h, sy * h)]
        for pg in polys(p):
            for ring in [pg.exterior] + list(pg.interiors):
                cs = list(ring.coords)
                for i in range(len(cs) - 1):
                    q = Polygon([cs[i], cs[i + 1], (cs[i + 1][0] + sx * h, cs[i + 1][1] + sy * h), (cs[i][0] + sx * h, cs[i][1] + sy * h)])
                    if q.is_valid and q.area > 0: parts.append(q)
        allp.append(unary_union(parts))
    shadow = unary_union(allp).intersection(B.buffer(40)).difference(unary_union([m["g"] for m in MASS]))
    flat(sh, shadow, 0.2, rgb("#27303c"))
    # 주변 건물(흰 매스) — 경계 안(철거 대상)은 제외
    Bb = B.buffer(1.0); nctx = 0
    for b in CTXB:
        pts = [(x - XS - X0, y - Y0) for x, y in b["p"]]
        try: pg = Polygon(pts).buffer(0)
        except Exception: continue
        if pg.is_empty or pg.area < 8: continue
        if Bb.contains(pg.representative_point()): continue
        d = pg.distance(B)
        if d > 400: continue
        h = max(b["h"], 3.5); t = float(np.clip((d - 80) / 260, 0, 0.75))
        wc = lerp("#f4f3f0", "#d9ded2", t); rc = lerp("#fbfbfa", "#e3e8dc", t)
        for p in polys(pg): walls(ctx, p, 0.0, h, wc); flat(ctx, p, h, rc)
        nctx += 1
    # 신규 매스(층별 색 적층 + 1층 가로상점 띠)
    SLAB = 0.45
    for m in MASS:
        p = m["g"]; n = m["floors"]; fh = m["fh"]; base = CATS[m["cat"]][0]
        z = 0.0
        for k in range(n):
            c = RETAIL if (k == 0 and m["retail"] and m["cat"] != "판매") else base
            if m["cat"] == "역사": c = base
            walls(bld, p, z, z + fh - SLAB, rgb(c, 1.0)); walls(bld, p, z + fh - SLAB, z + fh, rgb(c, 1.16)); z += fh
        top = z
        if m["roof"] == "heritage":
            flat(roofs, p, top, rgb("#a85a1e"))
        elif m["roof"] == "solar":
            flat(roofs, p, top, rgb("#d7d7d7"))
            inner = p.buffer(-2.0, join_style=2)
            if not inner.is_empty: stripes(roofs, inner, top + 0.12, 4.2, 0, 3.2, rgb("#5d6b80"))
        else:
            flat(roofs, p, top, rgb(base, 1.12))
            inner = p.buffer(-1.3, join_style=2)
            if m["cat"] not in ("주차",) and not inner.is_empty and inner.area > 25: flat(roofs, inner, top + 0.12, rgb(GREEN_ROOF))
            elif m["cat"] == "주차" and not inner.is_empty: flat(roofs, inner, top + 0.12, rgb(GREEN_ROOF))
        rims.append((p, top))
    print("scene %.1fs  trees %d  ctx %d" % (time.time() - t0, sum(len(v) for v in TREES.values()), nctx))
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


def frame(az, el, W, H, fill_w=0.90, cy=0.60):
    """경계가 화면 폭의 fill_w를 차지하고, 중심이 화면 위에서 cy 비율에 오도록 (ps, xc, yc)"""
    cam0 = Cam(az, el, W, H, 1.0, 0.0, 0.0)
    pts2 = np.array([cam0.XY(x, y, z) for (x, y) in B.exterior.coords for z in (0, 30)])
    xmin, ymin = pts2.min(0); xmax, ymax = pts2.max(0)
    ps = (xmax - xmin) / 2 / fill_w * H / W
    k = H / (2 * ps)
    xc = (xmin + xmax) / 2; yc = (ymin + ymax) / 2 + (cy - 0.5) * H / k
    return ps, xc, yc


def render(az_deg=-28.0, el_deg=34.0, out=None, W=3600, Hh=2546, fill_w=0.90, cy=0.60):
    S_ = build()
    pl = pv.Plotter(off_screen=True, window_size=(W, Hh)); pl.set_background(BG)
    for key, op in (("ground", 1.0), ("shadow", 0.17), ("ctx", 1.0), ("trees", 1.0), ("bld", 1.0), ("roofs", 1.0)):
        m = S_[key].mesh()
        if m is None: continue
        flatkey = key in ("ground", "shadow")
        pl.add_mesh(m, scalars="rgb", rgb=True, lighting=not flatkey, ambient=(1.0 if flatkey else 0.60), diffuse=(0.0 if flatkey else 0.52), specular=0.0, opacity=op, show_scalar_bar=False)
    segs = []
    for p, top in S_["rims"]:
        for pg in polys(p):
            for ring in [pg.exterior] + list(pg.interiors):
                cs = list(ring.coords)
                for i in range(len(cs) - 1): segs.append(((cs[i][0], cs[i][1], top + 0.28), (cs[i + 1][0], cs[i + 1][1], top + 0.28)))
    if segs:
        pts = np.array([s for seg in segs for s in seg]); lines = np.hstack([[2, 2 * i, 2 * i + 1] for i in range(len(segs))])
        pl.add_mesh(pv.PolyData(pts, lines=lines), color="#555b52", line_width=1.1, opacity=0.5, lighting=False)
    a = math.radians(az_deg); e = math.radians(el_deg)
    c = np.array([math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)])
    ps, xc, yc = frame(az_deg, el_deg, W, Hh, fill_w, cy)
    cam0 = Cam(az_deg, el_deg, W, Hh, 1.0, 0.0, 0.0)
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
    for p in polys(B): dr.polygon([cam.xy(x, y, 0) for (x, y) in p.exterior.coords], fill=255)
    mask = np.array(m) > 0
    dist = ndimage.distance_transform_edt(~mask)
    d0, d1 = 0.08 * W, 0.30 * W
    al = np.clip((dist - d0) / (d1 - d0), 0, 1) ** 1.3 * 0.90
    bgc = np.array([int(BG[i:i + 2], 16) for i in (1, 3, 5)], float)
    img = img * (1 - al[..., None]) + bgc * al[..., None]
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); im.save(out)
    pickle.dump(dict(az=az_deg, el=el_deg, W=W, H=Hh, ps=ps, xc=xc, yc=yc), open(os.path.splitext(out)[0] + "_meta.pkl", "wb"))
    return out


if __name__ == "__main__":
    az = float(sys.argv[1]) if len(sys.argv) > 1 else -28.0
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(SH, "axo.png")
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 3600; H = int(sys.argv[4]) if len(sys.argv) > 4 else 2546
    t0 = time.time(); print("saved", render(az, out=out, W=W, Hh=H), "%.1fs" % (time.time() - t0))
