"""S3 조감(축측) 렌더 — TIME STRATA 안. PyVista 오프스크린 평행투영. k4_axo(규제 미적용 v1)를 이 안의 데이터(공중가로·들어 올린 지붕·철도 흔적)에 맞게 고쳤다.
사용: python s3_axo.py [sheet|strip]  → data/axo_sheet.png(+_meta.pkl) / data/axo_strip.png(+_meta.pkl)"""
import pickle, sys, math, time, random, os
import numpy as np
import pyvista as pv
import trimesh
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from PIL import Image, ImageDraw
from scipy import ndimage
pv.OFF_SCREEN = True
sys.path.insert(0, r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts")
from geomkit import polys
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
P = pickle.load(open(os.path.join(D, "design.pkl"), "rb")); REG = pickle.load(open(os.path.join(D, "reg.pkl"), "rb"))
C = pickle.load(open(r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean\data\context.pkl", "rb"))
U, LOTS, PARKS, BUILD, ROADS, COURTS, OPEN, DECKS, RAILS, WEDGE = P["U"], P["LOTS"], P["PARKS"], P["BUILD"], P["ROADS"], P["COURTS"], P["OPEN"], P["DECKS"], P["RAILS"], P["WEDGE"]
ORG = np.array([U.centroid.x, U.centroid.y]); BG = "#eceee8"; SCL = P["SC"]
def shift(g): return affinity.translate(g, -REG["tx"], -REG["ty"])
CTX_B = [dict(geom=shift(b["geom"]), floors=b["floors"]) for b in C["B"]]
CTX_R = [shift(r) for r in C["RP"]]
CATCOL = {"문화·교육·공공": "#6f9fdc", "상업·업무": "#e4573a", "창조산업": "#a98bd3", "여가·오락·체육": "#2fab9d", "주거": "#f1d247", "판매·음식": "#f4a0c2", "교통·방문자": "#c6c6c6", "역사유산": "#c9742f", "오픈스페이스": "#9fd36b"}
GREEN_ROOF = "#a9d577"; DECKCOL = "#3fae4a"
def rgb(h, f=1.0): return np.clip(np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) * f, 0, 255).astype(np.uint8)
def lerp(h1, h2, t):
    a = np.array([int(h1[i:i + 2], 16) for i in (1, 3, 5)], float); b = np.array([int(h2[i:i + 2], 16) for i in (1, 3, 5)], float); return np.clip(a * (1 - t) + b * t, 0, 255).astype(np.uint8)
class Acc:
    def __init__(self): self.v, self.f, self.c = [], [], []; self.n = 0
    def tri(self, V, F, color):
        V = np.asarray(V, float); F = np.asarray(F, int); self.v.append(V); self.f.append(F + self.n); self.c.append(np.tile(color, (len(F), 1))); self.n += len(V)
    def quad(self, p0, p1, p2, p3, color): self.tri(np.array([p0, p1, p2, p3], float), [[0, 1, 2], [0, 2, 3]], color)
    def mesh(self):
        if not self.v: return None
        V = np.vstack(self.v); F = np.vstack(self.f); col = np.vstack(self.c); faces = np.hstack([np.full((len(F), 1), 3), F]).ravel()
        m = pv.PolyData(V, faces); m.cell_data["rgb"] = col.astype(np.uint8); return m
def loc(x, y): return (x - ORG[0], y - ORG[1])
def flat(acc, poly, z, color):
    for p in polys(poly):
        if p.area < 0.3: continue
        try: v, f = trimesh.creation.triangulate_polygon(p, engine="earcut")
        except Exception: continue
        acc.tri(np.column_stack([v[:, 0] - ORG[0], v[:, 1] - ORG[1], np.full(len(v), z)]), f, color)
def walls(acc, poly, z0, z1, color):
    for p in polys(poly):
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)
            for i in range(len(cs) - 1):
                a, b = loc(*cs[i]), loc(*cs[i + 1]); acc.quad((a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1), color)
def tree_mesh(acc, x, y, r, color, z0=0.0):
    s = pv.Sphere(radius=r, center=(x - ORG[0], y - ORG[1], z0 + r * 1.15), theta_resolution=9, phi_resolution=7).triangulate()
    acc.tri(np.asarray(s.points), s.faces.reshape(-1, 4)[:, 1:], color)
    acc.quad((x - ORG[0] - .25, y - ORG[1], z0), (x - ORG[0] + .25, y - ORG[1], z0), (x - ORG[0] + .25, y - ORG[1], z0 + r * .9), (x - ORG[0] - .25, y - ORG[1], z0 + r * .9), rgb("#8b7355"))
def dart(poly, spacing, rnd, margin=2.0, n_try=4000):
    inner = poly.buffer(-margin)
    if inner.is_empty: return []
    x0, y0, x1, y1 = inner.bounds; pts = []
    from shapely.prepared import prep
    pi = prep(inner)
    for _ in range(n_try):
        p = (rnd.uniform(x0, x1), rnd.uniform(y0, y1))
        if not pi.contains(Point(p)): continue
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= spacing ** 2 for q in pts): pts.append(p)
    return pts
def deck_geom(d):
    """데크 중심선(x,y,z) → 구간별 (사각 평면, z) 목록"""
    out = []; w = d["w"] / 2
    pts = d["pts"]
    for (x0, y0, z0), (x1, y1, z1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy) or 1.0; nx, ny = -dy / L * w, dx / L * w
        out.append(((x0 + nx, y0 + ny, z0), (x1 + nx, y1 + ny, z1), (x1 - nx, y1 - ny, z1), (x0 - nx, y0 - ny, z0)))
    return out

def build():
    t0 = time.time(); rnd = random.Random(7)
    ground = Acc(); sh = Acc(); ctx = Acc(); bld = Acc(); roofs = Acc(); tr = Acc(); rims = []; dk = Acc(); lf = Acc()
    bb = U.buffer(330).bounds
    flat(ground, box(*bb), -0.3, rgb("#e3e8dc")); flat(ground, U, -0.2, rgb("#f0efeb"))
    for r in CTX_R: flat(ground, r, -0.1, rgb("#fbfbfa"))
    for k, r in ROADS.items():
        flat(ground, r["g"], 0.0, rgb("#a9b8dc") if r["grp"] == "차량" else rgb("#f1b7ad"))
    flat(ground, ROADS["PZ"]["g"], 0.02, rgb("#ebb0a2"))
    for d in LOTS: flat(ground, d["geom"], 0.05, rgb("#e9e7e2"))
    for d in PARKS: flat(ground, d["geom"], 0.08, rgb("#b4dc8e") if d["name"] in ("Park A", "Park B") else rgb("#c7e3a2"))
    for lid, nm, g in COURTS: flat(ground, g, 0.1, rgb("#cfe8b3"))
    for lid, nm, g, col in OPEN: flat(ground, g, 0.1, rgb({"#cfe6b4": "#cfe8b3"}.get(col, col)))
    for r in RAILS:
        for ln in (r.geoms if r.geom_type.startswith("Multi") else [r]):
            if ln.geom_type == "LineString": flat(ground, ln.buffer(0.32, cap_style=2), 0.14, rgb("#6d6a63"))
    # 나무
    for (x, y) in dart(ROADS['WG']['g'], 12.0, rnd, 3.0): tree_mesh(tr, x, y, rnd.uniform(2.8, 3.8), lerp('#86c056', '#a8d377', rnd.random()))
    for d in PARKS:
        for (x, y) in dart(d["geom"], 14.0, rnd, 3.0): tree_mesh(tr, x, y, rnd.uniform(3.0, 4.2), lerp("#7db84f", "#a3d070", rnd.random()))
    for lid, nm, g in COURTS:
        for (x, y) in dart(g, 17.0, rnd, 4.0, 1500)[:10]: tree_mesh(tr, x, y, rnd.uniform(2.6, 3.4), lerp("#86c056", "#a8d377", rnd.random()))
    ln = LineString([(111.5 * SCL, 224 * SCL), (111.5 * SCL, 540 * SCL)])
    for i in range(1, int(ln.length // 18)):
        pt = ln.interpolate(i * 18.0)
        for sx in (-4.2, 4.2):
            if U.contains(Point(pt.x + sx, pt.y)): tree_mesh(tr, pt.x + sx, pt.y, 2.3, lerp("#7fba52", "#9fcf6e", rnd.random()))
    # 그림자
    sx, sy = 0.62, -0.42; parts_all = []
    for b in BUILD:
        h = b["h"] + 0.8; p = b["geom"]; parts = [p, affinity.translate(p, sx * h, sy * h)]; cs = list(p.exterior.coords)
        for i in range(len(cs) - 1):
            q = Polygon([cs[i], cs[i + 1], (cs[i + 1][0] + sx * h, cs[i + 1][1] + sy * h), (cs[i][0] + sx * h, cs[i][1] + sy * h)])
            if q.is_valid and q.area > 0: parts.append(q)
        parts_all.append(unary_union(parts))
    shadow = unary_union(parts_all).intersection(U.buffer(40)).difference(unary_union([b["geom"] for b in BUILD]))
    flat(sh, shadow, 0.2, rgb("#27303c"))
    # 주변 건물(배경)
    for b in CTX_B:
        if b["geom"].buffer(2).intersects(U): continue
        d = b["geom"].distance(U)
        if d > 300: continue
        h = b["floors"] * 3.5; t = float(np.clip((d - 70) / 230, 0, 0.75)); wc = lerp("#f4f3f0", "#d9ded2", t); rc = lerp("#fbfbfa", "#e3e8dc", t)
        for p in polys(b["geom"]):
            if p.area < 8: continue
            walls(ctx, p, 0.0, h, wc); flat(ctx, p, h, rc)
    # 매스
    SLAB = 0.45
    for b in sorted(BUILD, key=lambda x: x["lot_no"]):
        p = b["geom"]; n = b["floors"]; fh = b["floor_h"]; base = CATCOL[b["cat"]]
        if b["role"] == "주차": base = "#c6c6c6"
        z = 0.0
        for k in range(n):
            fcol = CATCOL["판매·음식"] if (k == 0 and b["retail_ground"]) else base
            walls(bld, p, z, z + fh - SLAB, rgb(fcol, 1.0)); walls(bld, p, z + fh - SLAB, z + fh, rgb(fcol, 1.16)); z += fh
        top = z
        rc = rgb("#a85a1e") if b["cat"] == "역사유산" and "구경주역" in b["name"] else (rgb("#d7d7d7") if b["role"] == "주차" else rgb(base, 1.12))
        flat(roofs, p, top, rc)
        inner = p.buffer(-1.3, join_style=2)
        if not (b["cat"] == "역사유산" and "구경주역" in b["name"]) and b["role"] != "주차" and not inner.is_empty and inner.area > 25: flat(roofs, inner, top + 0.12, rgb(GREEN_ROOF))
        if b["role"] == "주차":
            flat(roofs, p.buffer(-2.5, join_style=2), top + 0.12, rgb(GREEN_ROOF))                     # 주차동 옥상 녹지 데크
        rims.append((p, top))
        # 들어 올린 지붕(캐노피): 기둥 4 + 얇은 슬래브(상면 녹지)
        if b.get("lift"):
            lg = b["lift"]["geom"]; dz = b["lift"]["dz"]; th = b["lift"]["th"]
            for q in polys(lg):
                if q.area < 20: continue
                zc = top + dz
                walls(lf, q, zc, zc + th, rgb("#f1f1ee")); flat(lf, q, zc + th, rgb("#bfe39a"))
                mrr = q.minimum_rotated_rectangle; cs = list(mrr.exterior.coords)[:4]
                for (cx, cy) in cs:
                    c0 = loc(cx + (q.centroid.x - cx) * 0.06, cy + (q.centroid.y - cy) * 0.06)
                    for ddx, ddy in ((-.3, -.3), (.3, -.3), (.3, .3), (-.3, .3)): pass
                    lf.quad((c0[0] - .3, c0[1], top), (c0[0] + .3, c0[1], top), (c0[0] + .3, c0[1], zc), (c0[0] - .3, c0[1], zc), rgb("#8a8a86"))
                    lf.quad((c0[0], c0[1] - .3, top), (c0[0], c0[1] + .3, top), (c0[0], c0[1] + .3, zc), (c0[0], c0[1] - .3, zc), rgb("#8a8a86"))
    # 공중가로·데크
    for d in DECKS:
        col = rgb(DECKCOL) if d["kind"] != "skybridge" else rgb("#e8e8e4")
        for quad in deck_geom(d):
            a, b_, c_, d_ = quad
            dk.quad((a[0] - ORG[0], a[1] - ORG[1], a[2]), (b_[0] - ORG[0], b_[1] - ORG[1], b_[2]), (c_[0] - ORG[0], c_[1] - ORG[1], c_[2]), (d_[0] - ORG[0], d_[1] - ORG[1], d_[2]), col)
            for (p0, p1) in ((a, b_), (d_, c_)):                                            # 측면 보 + 난간
                dk.quad((p0[0] - ORG[0], p0[1] - ORG[1], p0[2]), (p1[0] - ORG[0], p1[1] - ORG[1], p1[2]), (p1[0] - ORG[0], p1[1] - ORG[1], p1[2] - 0.9), (p0[0] - ORG[0], p0[1] - ORG[1], p0[2] - 0.9), rgb("#d9d9d4"))
                dk.quad((p0[0] - ORG[0], p0[1] - ORG[1], p0[2]), (p1[0] - ORG[0], p1[1] - ORG[1], p1[2]), (p1[0] - ORG[0], p1[1] - ORG[1], p1[2] + 1.3), (p0[0] - ORG[0], p0[1] - ORG[1], p0[2] + 1.3), rgb("#2e7d32"))
        # 종축 데크: 기둥(30 m 간격)
        if d["kind"] == "main":
            for (x, y, z) in d["pts"][::3]:
                dk.quad((x - ORG[0] - .35, y - ORG[1], 0), (x - ORG[0] + .35, y - ORG[1], 0), (x - ORG[0] + .35, y - ORG[1], z - 0.9), (x - ORG[0] - .35, y - ORG[1], z - 0.9), rgb("#9b9b97"))
    print("scene built %.1fs" % (time.time() - t0))
    return dict(ground=ground, shadow=sh, ctx=ctx, trees=tr, bld=bld, roofs=roofs, lifts=lf, decks=dk, rims=rims)

class Cam:
    def __init__(self, az_deg, el_deg, W, H, ps, xc, yc):
        a = math.radians(az_deg); e = math.radians(el_deg); self.a, self.e, self.W, self.H, self.ps, self.xc, self.yc = a, e, W, H, ps, xc, yc
        self.r = np.array([-math.sin(a), math.cos(a)]); self.f = np.array([-math.cos(a), -math.sin(a)])
    def XY(self, x, y, z=0.0):
        p = np.array([x - ORG[0], y - ORG[1]]); return float(p @ self.r), float(p @ self.f) * math.sin(self.e) + z * math.cos(self.e)
    def xy(self, x, y, z=0.0):
        X, Y = self.XY(x, y, z); k = self.H / (2 * self.ps); return self.W / 2 + (X - self.xc) * k, self.H / 2 - (Y - self.yc) * k

def render(az_deg=-35.0, el_deg=34.0, out="axo.png", W=3600, Hh=2548, zoom=1.0, shift=(0.0, 0.0)):
    S = build()
    pl = pv.Plotter(off_screen=True, window_size=(W, Hh)); pl.set_background(BG)
    for key, op in (("ground", 1.0), ("shadow", 0.17), ("ctx", 1.0), ("trees", 1.0), ("bld", 1.0), ("roofs", 1.0), ("lifts", 1.0), ("decks", 1.0)):
        m = S[key].mesh()
        if m is None: continue
        fk = key in ("ground", "shadow")
        pl.add_mesh(m, scalars="rgb", rgb=True, lighting=not fk, ambient=(1.0 if fk else 0.60), diffuse=(0.0 if fk else 0.52), specular=0.0, opacity=op, show_scalar_bar=False)
    segs = []
    for p, top in S["rims"]:
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)
            for i in range(len(cs) - 1): segs.append(((cs[i][0] - ORG[0], cs[i][1] - ORG[1], top + 0.28), (cs[i + 1][0] - ORG[0], cs[i + 1][1] - ORG[1], top + 0.28)))
    if segs:
        pts = np.array([s for seg in segs for s in seg]); lines = np.hstack([[2, 2 * i, 2 * i + 1] for i in range(len(segs))])
        pl.add_mesh(pv.PolyData(pts, lines=lines), color="#555b52", line_width=1.1, opacity=0.5, lighting=False)
    a = math.radians(az_deg); e = math.radians(el_deg)
    c = np.array([math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)])
    cam0 = Cam(az_deg, el_deg, W, Hh, 1.0, 0.0, 0.0)
    pts2 = np.array([cam0.XY(x, y, z) for (x, y) in U.exterior.coords for z in (0, 30)])
    xmin, ymin = pts2.min(0); xmax, ymax = pts2.max(0)
    xc, yc = (xmin + xmax) / 2 + shift[0], (ymin + ymax) / 2 + shift[1]
    ps = max((ymax - ymin) / 2 * 1.10, (xmax - xmin) / 2 * 1.05 * Hh / W) / zoom
    Pf = xc * cam0.r + (yc / math.sin(e)) * cam0.f; focal = np.array([Pf[0], Pf[1], 0.0])
    pl.camera.parallel_projection = True
    pl.camera_position = [tuple(focal + 3000 * c), tuple(focal), (0, 0, 1)]
    pl.camera.parallel_scale = ps; pl.camera.clipping_range = (10, 9000)
    pl.remove_all_lights()
    pl.add_light(pv.Light(position=tuple(focal + 2000 * np.array([math.cos(a - 0.95) * 0.7, math.sin(a - 0.95) * 0.7, 0.95])), focal_point=tuple(focal), color="white", intensity=0.95, light_type="scene light"))
    pl.add_light(pv.Light(position=tuple(focal + 2000 * np.array([math.cos(a + 2.3) * 0.6, math.sin(a + 2.3) * 0.6, 0.5])), focal_point=tuple(focal), color="white", intensity=0.32, light_type="scene light"))
    pl.enable_anti_aliasing("ssaa")
    img = pl.screenshot(None, return_img=True).astype(float)
    cam = Cam(az_deg, el_deg, W, Hh, ps, xc, yc)
    m = Image.new("L", (W, Hh), 0); dr = ImageDraw.Draw(m)
    for p in polys(U): dr.polygon([cam.xy(x, y, 0) for (x, y) in p.exterior.coords], fill=255)
    mask = np.array(m) > 0; dist = ndimage.distance_transform_edt(~mask); d0, d1 = 0.10 * W, 0.30 * W
    al = np.clip((dist - d0) / (d1 - d0), 0, 1) ** 1.3 * 0.92
    bgc = np.array([int(BG[i:i + 2], 16) for i in (1, 3, 5)], float); img = img * (1 - al[..., None]) + bgc * al[..., None]
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out)
    pickle.dump(dict(az=az_deg, el=el_deg, W=W, H=Hh, ps=ps, xc=xc, yc=yc), open(os.path.splitext(out)[0] + "_meta.pkl", "wb"))
    return out

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "sheet"
    t0 = time.time()
    if which == "sheet": print(render(-35.0, 34.0, os.path.join(D, "axo_sheet.png"), 3600, 2548, zoom=1.0, shift=(0, 0)))
    else: print(render(-84.0, 38.0, os.path.join(D, "axo_strip.png"), 1700, 3685, zoom=1.0))
    print("%.1fs" % (time.time() - t0))
