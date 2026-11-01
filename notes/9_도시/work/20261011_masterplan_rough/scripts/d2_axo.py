"""D2 조감(축측) 렌더 v2 — PyVista 오프스크린 평행투영. 참고 스타일: 여천역 조감도(파스텔 매스·흰 바탕·녹색 띠)
- 매스: 파스텔 용도색, 층 띠·창 멀리언 선, 1층 가로상점 띠, 옥상녹화 없음(지붕 = 용도색)
- 구 경주역사: 모임지붕(geom2.hip_roof), 그레이트 코트: 유리 볼트 + 사선 격자(geom2.vault)
- 동서 선형공원: 잔디 띠 + 중앙 가로광장 포장 + 가로수 4열, 주변: 평면 건물 윤곽(흰 바탕)
입력: data/design.pkl, data/ctx_fixed.pkl(주변 건물 — V-World 연속지적에 재정합, c0·c1)
사용: python d2_axo.py [az] [out.png] [W] [H] [fill_w] [cy] → out.png + out_meta.pkl"""
import os, sys, math, json, pickle, random, time
import numpy as np
import pyvista as pv
import trimesh
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
from shapely import affinity
from PIL import Image, ImageDraw
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from geom2 import hip_roof, vault, vault_grid
pv.OFF_SCREEN = True
D = os.path.join(HERE, "..", "data"); SH = os.path.join(HERE, "..", "sheets")
S = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
B, LOTS, PARKS, OPEN, MASS, PLZ, TREES, CATS = S["B"], S["LOTS"], S["PARKS"], S["OPEN"], S["MASS"], S["PLZ"], S["TREES"], S["CATS"]
X0, Y0, XS, GL = S["X0"], S["Y0"], S["XSHIFT"], S["GLASS"]
BG = "#f8f8f6"; RETAIL = CATS["판매"][0]


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


class Seg:
    def __init__(self): self.s = []
    def add(self, p, q): self.s.append((p, q))
    def mesh(self):
        if not self.s: return None
        pts = np.array([x for sg in self.s for x in sg], float); n = len(self.s)
        return pv.PolyData(pts, lines=np.hstack([[2, 2 * i, 2 * i + 1] for i in range(n)]))


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


SPH = pv.Sphere(radius=1.0, theta_resolution=10, phi_resolution=8).triangulate()
SPV, SPF = np.asarray(SPH.points), SPH.faces.reshape(-1, 4)[:, 1:]


def tree_mesh(acc, x, y, r, color, z0=0.0, trunk=3.0):
    acc.tri(SPV * np.array([r, r, r * 0.92]) + np.array([x, y, z0 + trunk + 0.8 * r]), SPF, color)
    acc.quad((x - .22, y, z0), (x + .22, y, z0), (x + .22, y, z0 + trunk), (x - .22, y, z0 + trunk), rgb("#9a8a72"))


def stripes(acc, poly, z, step, ang, w, color):
    c = poly.centroid; g = affinity.rotate(poly, -ang, origin=c)
    x0, y0, x1, y1 = g.bounds; xs = np.arange(x0 + step / 2, x1, step)
    bands = [box(x - w / 2, y0, x + w / 2, y1) for x in xs]
    flat(acc, affinity.rotate(unary_union(bands), ang, origin=c).intersection(poly), z, color)


def build():
    t0 = time.time(); rnd = random.Random(7)
    ground = Acc(); sh = Acc(); ctx = Acc(); bld = Acc(); roofs = Acc(); tr = Acc(); glass = Acc()
    rims = Seg(); mull = Seg(); ctxl = Seg(); gl = Seg()
    bb = B.buffer(480).bounds
    flat(ground, box(*bb), -0.3, rgb(BG))
    # 주변: 평면 건물 윤곽(흰 바탕 위 옅은 회색 면 + 선)
    Bb = B.buffer(1.0); nctx = 0
    for o in pickle.load(open(os.path.join(D, "ctx_fixed.pkl"), "rb"))["B"]:   # 정합된 주변 건물(로컬)
        pg = o["g"]
        if o["inside"] or pg.area < 8: continue
        d = pg.distance(B)
        if d > 460: continue
        t = float(np.clip((d - 60) / 360, 0, 1))
        for p in polys(pg):
            flat(ctx, p, 0.0, lerp("#e9e9e6", "#f3f3f1", t))
            cs = list(p.exterior.coords)
            for i in range(len(cs) - 1): ctxl.add((cs[i][0], cs[i][1], 0.08), (cs[i + 1][0], cs[i + 1][1], 0.08))
        nctx += 1
    flat(ground, B, -0.2, rgb("#f1f0ec"))
    flat(ground, S["WALK"], 0.0, rgb("#ffffff")); flat(ground, S["PATH8"], 0.0, rgb("#ffffff"))
    for r in S["ROADS"].values(): flat(ground, r, 0.02, rgb("#dedcd7"))
    for key, ln in (("EW", LineString([(100, 343.7), (420, 343.7)])), ("N", LineString([(100, 778.5), (254.5, 778.5), (348.5, 888.0), (390, 936)]))):
        flat(ground, ln.buffer(0.3).intersection(S["ROADS"][key]), 0.04, rgb("#ffffff"))
    for l in LOTS: flat(ground, l["g"], 0.05, rgb(tint(CATS[l["cat"]][0], 0.80)))
    for p in PARKS: flat(ground, p["g"], 0.08, rgb("#cfe9b4"))
    y0b, y1b = S["DBAND"]
    for o in OPEN:
        if o["key"] == "D":
            g = o["g"]
            flat(ground, g, 0.08, rgb("#f6f2e8"))                                                   # 중앙 가로광장 포장
            lawn = unary_union([box(80, y0b, 440, y0b + 11.5), box(80, y1b - 11.5, 440, y1b)]).intersection(g).difference(box(255.9, 0, 285.9, 1000))
            flat(ground, lawn, 0.10, rgb("#9fd67c"))                                                # 남·북 잔디 띠(가로수 2열씩)
            for yy in (y0b + 11.5, y1b - 11.5):
                flat(ground, LineString([(80, yy), (440, yy)]).buffer(0.35).intersection(g), 0.12, rgb("#d9cfb6"))
            flat(ground, LineString([(80, (y0b + y1b) / 2), (440, (y0b + y1b) / 2)]).buffer(0.6).intersection(g).difference(box(255.9, 0, 285.9, 1000)), 0.12, rgb("#a9d3e6"))  # 실개천 선
            sq = box(255.9, y0b, 285.9, y1b).intersection(g)
            stripes(ground, sq, 0.11, 3.0, 0, 0.12, rgb("#e2dccd")); stripes(ground, sq, 0.11, 3.0, 90, 0.12, rgb("#e2dccd"))
        else:
            flat(ground, o["g"], 0.08, rgb("#efebe1"))
    for p in PLZ:
        k = p["kind"]
        if k == "광장": flat(ground, p["g"], 0.1, rgb("#ede7d8"))
        elif k == "코트": flat(ground, p["g"], 0.1, rgb("#f1ebdf")); stripes(ground, p["g"], 0.12, 4.0, 0, 0.1, rgb("#ddd4c2"))
        elif k == "노외주차": flat(ground, p["g"], 0.1, rgb("#d3d3d0")); stripes(ground, p["g"], 0.12, 2.5, 0, 0.18, rgb("#ffffff"))
        elif k == "텃밭": flat(ground, p["g"], 0.1, rgb("#d6bb92")); stripes(ground, p["g"].buffer(-1.2), 0.12, 3.0, 90, 1.6, rgb("#9fcc6c"))
        else: flat(ground, p["g"], 0.1, rgb("#cfe9b4"))
    for kind, col, trunk in (("park", ("#7fbf55", "#a6d47a"), 3.0), ("axis", ("#86c25a", "#9fd06f"), 3.0), ("lot", ("#8cc560", "#a9d67d"), 2.8),
                             ("street", ("#86c25a", "#9fd06f"), 2.8), ("linear", ("#5fb44a", "#6fbe55"), 3.4)):
        for (x, y, r) in TREES.get(kind, []): tree_mesh(tr, x, y, r, lerp(col[0], col[1], rnd.random()), trunk=trunk)
    # 그림자(지면 투영)
    sx, sy = 0.62, -0.42
    allp = []
    for m in MASS:
        h = m["h"] + (5.0 if m["roof"] == "hip" else 0.8); p = m["g"]; parts = [p, affinity.translate(p, sx * h, sy * h)]
        for pg in polys(p):
            for ring in [pg.exterior] + list(pg.interiors):
                cs = list(ring.coords)
                for i in range(len(cs) - 1):
                    q = Polygon([cs[i], cs[i + 1], (cs[i + 1][0] + sx * h, cs[i + 1][1] + sy * h), (cs[i][0] + sx * h, cs[i][1] + sy * h)])
                    if q.is_valid and q.area > 0: parts.append(q)
        allp.append(unary_union(parts))
    shadow = unary_union(allp).intersection(B.buffer(40)).difference(unary_union([m["g"] for m in MASS]))
    flat(sh, shadow, 0.2, rgb("#3a4450"))
    # 신규 매스 — 층 띠·멀리언, 지붕 = 용도색
    SLAB = 0.5
    for m in MASS:
        p = m["g"]; n = m["floors"]; fh = m["fh"]; base = CATS[m["cat"]][0]
        z = 0.0
        for k in range(n):
            c = RETAIL if (k == 0 and m["retail"] and m["cat"] != "판매") else base
            walls(bld, p, z, z + fh - SLAB, rgb(c, 1.0)); walls(bld, p, z + fh - SLAB, z + fh, rgb(tint(c, 0.45))); z += fh
        top = z
        # 창 멀리언(외벽 3.6 m 간격 세로선)
        wc = rgb(base, 0.80)
        for pg in polys(p):
            for ring in [pg.exterior] + list(pg.interiors):
                L = LineString(ring.coords)
                for dd in np.arange(1.8, L.length, 3.6):
                    q = L.interpolate(dd); mull.add((q.x, q.y, 0.15), (q.x, q.y, top - 0.15))
        if m["roof"] == "hip":
            rp = p.buffer(0.8, join_style=2)
            walls(bld, rp.difference(p.buffer(0.01)), top - 0.35, top - 0.05, rgb("#7a5a46"))
            V, F = hip_roof(rp, top - 0.05, 33.0, 0.5, axis=(GL["ua"][0], GL["ua"][1]))
            roofs.tri(V, F, rgb("#6b5a52"))
        elif m["roof"] == "solar":
            flat(roofs, p, top, rgb(tint(base, 0.25)))
            inner = p.buffer(-2.0, join_style=2)
            if not inner.is_empty: stripes(roofs, inner, top + 0.1, 4.2, 0, 3.0, rgb("#9fb0c4"))
        else:
            flat(roofs, p, top, rgb(tint(base, 0.18)))
            inner = p.buffer(-0.9, join_style=2)
            if not inner.is_empty and inner.area > 25: flat(roofs, inner, top + 0.06, rgb(tint(base, 0.32)))   # 옥상 파라펫 안쪽(옅은 용도색)
        for pg in polys(p):
            for ring in [pg.exterior] + list(pg.interiors):
                cs = list(ring.coords)
                for i in range(len(cs) - 1): rims.add((cs[i][0], cs[i][1], top + 0.1), (cs[i + 1][0], cs[i + 1][1], top + 0.1))
    # 그레이트 코트 유리 볼트
    V, F = vault(GL, 1.5); glass.tri(V, F, rgb("#cfe6f3"))
    for p_, q_ in vault_grid(GL, 4.0, 0.6): gl.add(p_, q_)
    # 동서 선형공원 띠를 사이트 밖(서측 원도심 방면·동측)으로 연장 — 경계에서 멀어질수록 옅게(12단)
    ext = []
    xw, _, xe, _ = B.intersection(LineString([(-500, (y0b + y1b) / 2), (900, (y0b + y1b) / 2)])).bounds
    for k in range(12):
        L = 15.0
        for xa, xb in ((xw - (k + 1) * L, xw - k * L), (xe + k * L, xe + (k + 1) * L)):
            g = box(xa, y0b, xb, y1b).difference(B.buffer(0.5))
            if not g.is_empty:
                a_ = Acc(); flat(a_, g, 0.25, rgb("#7cc865"))
                if a_.v: ext.append((a_, 0.62 * (1 - k / 12.0) ** 1.4))
    a_ = Acc(); flat(a_, [o for o in OPEN if o["key"] == "D"][0]["g"], 0.25, rgb("#7cc865")); ext.append((a_, 0.28))   # 사이트 안 선형공원도 같은 녹색 한 겹
    print("scene %.1fs  trees %d  ctx %d" % (time.time() - t0, sum(len(v) for v in TREES.values()), nctx))
    return dict(ground=ground, shadow=sh, ctx=ctx, bld=bld, roofs=roofs, trees=tr, glass=glass, rims=rims, mull=mull, ctxl=ctxl, gl=gl, ext=ext)


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
    cam0 = Cam(az, el, W, H, 1.0, 0.0, 0.0)
    pts2 = np.array([cam0.XY(x, y, z) for (x, y) in B.exterior.coords for z in (0, 30)])
    xmin, ymin = pts2.min(0); xmax, ymax = pts2.max(0)
    ps = (xmax - xmin) / 2 / fill_w * H / W
    k = H / (2 * ps)
    xc = (xmin + xmax) / 2; yc = (ymin + ymax) / 2 + (cy - 0.5) * H / k
    return ps, xc, yc


def render(az_deg=-28.0, el_deg=36.0, out=None, W=3840, Hh=2160, fill_w=0.86, cy=0.56, focus=None, fade=True):
    S_ = build()
    pl = pv.Plotter(off_screen=True, window_size=(W, Hh)); pl.set_background(BG)
    for key, op in (("ground", 1.0), ("ctx", 1.0), ("shadow", 0.11), ("trees", 1.0), ("bld", 1.0), ("roofs", 1.0)):
        m = S_[key].mesh()
        if m is None: continue
        flatkey = key in ("ground", "shadow", "ctx")
        pl.add_mesh(m, scalars="rgb", rgb=True, lighting=not flatkey, ambient=(1.0 if flatkey else 0.70), diffuse=(0.0 if flatkey else 0.42), specular=0.0, opacity=op, show_scalar_bar=False)
    for a_, op in S_["ext"]:
        pl.add_mesh(a_.mesh(), scalars="rgb", rgb=True, lighting=False, opacity=op, show_scalar_bar=False)
    for key, col, lw, op in (("ctxl", "#d4d4d0", 0.8, 0.9), ("mull", "#3c3c3c", 0.7, 0.16), ("rims", "#6d6d68", 1.1, 0.55)):
        m = S_[key].mesh()
        if m is not None: pl.add_mesh(m, color=col, line_width=lw, opacity=op, lighting=False)
    gm = S_["glass"].mesh()
    pl.add_mesh(gm, scalars="rgb", rgb=True, opacity=0.42, ambient=0.85, diffuse=0.35, specular=0.4, show_scalar_bar=False)
    pl.add_mesh(S_["gl"].mesh(), color="#7d98ab", line_width=1.0, opacity=0.85, lighting=False)
    a = math.radians(az_deg); e = math.radians(el_deg)
    c = np.array([math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)])
    ps, xc, yc = frame(az_deg, el_deg, W, Hh, fill_w, cy)
    cam0 = Cam(az_deg, el_deg, W, Hh, 1.0, 0.0, 0.0)
    if focus is not None:
        xc, yc = cam0.XY(focus[0], focus[1], focus[3] if len(focus) > 3 else 8.0); ps = focus[2]
    Pf = xc * cam0.r + (yc / math.sin(e)) * cam0.f
    focal = np.array([Pf[0], Pf[1], 0.0])
    pl.camera.parallel_projection = True
    pl.camera_position = [tuple(focal + 3000 * c), tuple(focal), (0, 0, 1)]
    pl.camera.parallel_scale = ps; pl.camera.clipping_range = (10, 9000)
    pl.remove_all_lights()
    key = pv.Light(position=tuple(focal + 2000 * np.array([math.cos(a - 0.95) * 0.7, math.sin(a - 0.95) * 0.7, 0.95])), focal_point=tuple(focal), color="white", intensity=0.95, light_type="scene light")
    fill = pv.Light(position=tuple(focal + 2000 * np.array([math.cos(a + 2.3) * 0.6, math.sin(a + 2.3) * 0.6, 0.5])), focal_point=tuple(focal), color="white", intensity=0.35, light_type="scene light")
    pl.add_light(key); pl.add_light(fill); pl.enable_anti_aliasing("ssaa")
    img = pl.screenshot(None, return_img=True).astype(float)
    cam = Cam(az_deg, el_deg, W, Hh, ps, xc, yc)
    m = Image.new("L", (W, Hh), 0); dr = ImageDraw.Draw(m)
    for p in polys(B): dr.polygon([cam.xy(x, y, 0) for (x, y) in p.exterior.coords], fill=255)
    mask = np.array(m) > 0
    dist = ndimage.distance_transform_edt(~mask)
    d0, d1 = 0.10 * W, 0.36 * W
    al = np.clip((dist - d0) / (d1 - d0), 0, 1) ** 1.2 * 0.92 * (1.0 if fade else 0.0)
    bgc = np.array([int(BG[i:i + 2], 16) for i in (1, 3, 5)], float)
    img = img * (1 - al[..., None]) + bgc * al[..., None]
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); im.save(out)
    pickle.dump(dict(az=az_deg, el=el_deg, W=W, H=Hh, ps=ps, xc=xc, yc=yc), open(os.path.splitext(out)[0] + "_meta.pkl", "wb"))
    return out


if __name__ == "__main__":
    az = float(sys.argv[1]) if len(sys.argv) > 1 else -28.0
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(SH, "axo_v2.png")
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 3840; H = int(sys.argv[4]) if len(sys.argv) > 4 else 2160
    fw = float(sys.argv[5]) if len(sys.argv) > 5 else 0.86; cy = float(sys.argv[6]) if len(sys.argv) > 6 else 0.56
    foc = [float(v) for v in sys.argv[7].split(",")] if len(sys.argv) > 7 else None
    t0 = time.time(); print("saved", render(az, out=out, W=W, Hh=H, fill_w=fw, cy=cy, focus=foc, fade=foc is None), "%.1fs" % (time.time() - t0))
