"""K4 조감(축측) 렌더 — PyVista 오프스크린 + 투영행렬. 참고: 통영 보고서 p.32 'Site Anchors'.
층별 색 적층(1층 판매 띠 + 용도색, 슬래브 띠) + 옥상 녹지, 주변 건물은 흰 매스, 지면 그림자, 가장자리 페이드.
사용: python k4_axo.py [az_deg] [out.png]   → out.png + out_meta.pkl(투영 정보)"""
import pickle, sys, math, time, random
import numpy as np
import pyvista as pv
import trimesh
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from PIL import Image, ImageDraw
from scipy import ndimage
pv.OFF_SCREEN = True
import os as _os; SP = _os.environ.get("PLAN_SP", r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad")   # 입력 pkl 폴더. 재현 시 PLAN_SP=<work/20261005_plan_clean/data>
PM = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts"
sys.path.insert(0, PM)
from geomkit import polys

LP = pickle.load(open(SP + r"\lots.pkl", "rb")); M = pickle.load(open(SP + r"\clean_mass.pkl", "rb"))
C = pickle.load(open(SP + r"\context.pkl", "rb")); NET = pickle.load(open(SP + r"\network.pkl", "rb")); U = C["U"]
ORG = np.array([219790.0, 360990.0])        # 렌더용 국소 좌표 원점
BG = "#eceee8"

CATCOL = {"문화·교육·공공": "#6f9fdc", "상업·업무": "#e4573a", "창조산업": "#a98bd3", "여가·오락·체육": "#2fab9d", "주거": "#f1d247",
          "판매·음식": "#f4a0c2", "교통·방문자": "#c6c6c6", "역사유산": "#c9742f", "오픈스페이스": "#9fd36b"}
GREEN_ROOF = "#a9d577"
def rgb(h, f=1.0):
    c = np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) * f
    return np.clip(c, 0, 255).astype(np.uint8)
def lerp(h1, h2, t):
    a = np.array([int(h1[i:i + 2], 16) for i in (1, 3, 5)], float); b = np.array([int(h2[i:i + 2], 16) for i in (1, 3, 5)], float)
    return np.clip(a * (1 - t) + b * t, 0, 255).astype(np.uint8)

class Acc:
    """셀마다 색이 다른 큰 메시를 만들기 위한 누적기"""
    def __init__(self): self.v, self.f, self.c = [], [], []; self.n = 0
    def tri(self, V, F, color):
        V = np.asarray(V, float); F = np.asarray(F, int)
        self.v.append(V); self.f.append(F + self.n); self.c.append(np.tile(color, (len(F), 1))); self.n += len(V)
    def quad(self, p0, p1, p2, p3, color):
        self.tri(np.array([p0, p1, p2, p3], float), [[0, 1, 2], [0, 2, 3]], color)
    def mesh(self):
        if not self.v: return None
        V = np.vstack(self.v); F = np.vstack(self.f); col = np.vstack(self.c)
        faces = np.hstack([np.full((len(F), 1), 3), F]).ravel()
        m = pv.PolyData(V, faces); m.cell_data["rgb"] = col.astype(np.uint8); return m

def loc(x, y): return (x - ORG[0], y - ORG[1])
def flat(acc, poly, z, color):
    for p in polys(poly):
        if p.area < 0.5: continue
        try: v, f = trimesh.creation.triangulate_polygon(p, engine="earcut")
        except Exception: continue
        acc.tri(np.column_stack([v[:, 0] - ORG[0], v[:, 1] - ORG[1], np.full(len(v), z)]), f, color)
def walls(acc, poly, z0, z1, color):
    for p in polys(poly):
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)
            for i in range(len(cs) - 1):
                a, b = loc(*cs[i]), loc(*cs[i + 1])
                acc.quad((a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1), color)

def tree_mesh(acc, x, y, r, color, z0=0.0):
    s = pv.Sphere(radius=r, center=(x - ORG[0], y - ORG[1], z0 + r * 1.15), theta_resolution=9, phi_resolution=7).triangulate()
    F = s.faces.reshape(-1, 4)[:, 1:]; acc.tri(np.asarray(s.points), F, color)
    acc.quad((x - ORG[0] - .25, y - ORG[1], z0), (x - ORG[0] + .25, y - ORG[1], z0), (x - ORG[0] + .25, y - ORG[1], z0 + r * .9), (x - ORG[0] - .25, y - ORG[1], z0 + r * .9), rgb("#8b7355"))

def dart(poly, spacing, rnd, margin=2.0, n_try=4000):
    """다각형 안 포아송 디스크(단순 다트 던지기)"""
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

def build(before=False):
    """before=True: 현황(계획 이전) — 경계 안 기존 건물만 남기고 신규 가로·획지·매스·나무를 모두 뺀다."""
    t0 = time.time(); rnd = random.Random(7)
    ground = Acc(); sh = Acc(); ctx = Acc(); bld = Acc(); roofs = Acc(); tr = Acc(); rims = []
    bb = U.buffer(330).bounds
    g_out, g_u, g_rp = ("#cdcdcb", "#a9a9a6", "#f1f1ef") if before else ("#e3e8dc", "#f0efeb", "#fbfbfa")     # 현황: 빈 띠가 읽히도록 어둡게
    flat(ground, box(*bb), -0.3, rgb(g_out))
    flat(ground, U, -0.2, rgb(g_u))
    for r in C["RP"]: flat(ground, r, -0.1, rgb(g_rp))
    park_pts = []
    if not before:
        road_all = unary_union([NET["road_all"], NET["plaza_extra"]])
        flat(ground, road_all, 0.0, rgb("#ffffff"))
        for d in LP["LOTS"]: flat(ground, d["geom"], 0.05, rgb("#e9e7e2"))
        for d in LP["PARKS"]:
            flat(ground, d["geom"], 0.08, rgb("#b4dc8e") if d["name"] in ("Park A", "Park B") else rgb("#c7e3a2"))
        for lid, nm, g in M["COURTS"]: flat(ground, g, 0.1, rgb("#cfe8b3"))
        for lid, nm, g, col in M["OPEN"]:
            flat(ground, g, 0.1, rgb({"#cfe6b4": "#cfe8b3"}.get(col, col)))
        # ── 가로수·공원수 ──
        for d in LP["PARKS"]:
            sp = 15.0 if d["name"] in ("Park A", "Park C") else 13.0
            for (x, y) in dart(d["geom"], sp, rnd, 3.0): park_pts.append((x, y, rnd.uniform(3.0, 4.2)))
        for (x, y, r) in park_pts: tree_mesh(tr, x, y, r, lerp("#7db84f", "#a3d070", rnd.random()))
        for lid, nm, g in M["COURTS"]:
            for (x, y) in dart(g, 17.0, rnd, 4.0, 1500)[:14]: tree_mesh(tr, x, y, rnd.uniform(2.6, 3.4), lerp("#86c056", "#a8d377", rnd.random()))
        for key in ("B", "S"):
            ln = LineString(NET["STREETS"][key][0]); half = NET["STREETS"][key][1] / 2
            n = int(ln.length // 17)
            for i in range(1, n):
                pt = ln.interpolate(i * 17.0); q = ln.interpolate(i * 17.0 + 1.0)
                dx, dy = q.x - pt.x, q.y - pt.y; L = math.hypot(dx, dy) or 1.0; nx, ny = -dy / L, dx / L
                for sgn in (-1, 1):
                    x, y = pt.x + sgn * nx * (half - 1.8), pt.y + sgn * ny * (half - 1.8)
                    if U.contains(Point(x, y)): tree_mesh(tr, x, y, 2.5, lerp("#7fba52", "#9fcf6e", rnd.random()))
        # ── 그림자(지면 투영) ──
        sx, sy = 0.62, -0.42
        parts_all = []
        for b in M["BUILD"]:
            h = b["h"] + 0.8; p = b["geom"]; parts = [p, affinity.translate(p, sx * h, sy * h)]
            cs = list(p.exterior.coords)
            for i in range(len(cs) - 1):
                q = Polygon([cs[i], cs[i + 1], (cs[i + 1][0] + sx * h, cs[i + 1][1] + sy * h), (cs[i][0] + sx * h, cs[i][1] + sy * h)])
                if q.is_valid and q.area > 0: parts.append(q)
            parts_all.append(unary_union(parts))
        shadow = unary_union(parts_all).intersection(U.buffer(40)).difference(unary_union([b["geom"] for b in M["BUILD"]]))
        flat(sh, shadow, 0.2, rgb("#27303c"))
    # ── 주변 건물 ──
    for b in C["B"]:
        d = b["geom"].distance(U)
        if d > 300 or (U.contains(b["geom"].representative_point()) and not before): continue
        h = b["floors"] * 3.5; t = float(np.clip((d - 70) / 230, 0, 0.75))
        wc = lerp("#f4f3f0", "#d9ded2", t); rc = lerp("#fbfbfa", "#e3e8dc", t)
        for p in polys(b["geom"]):
            if p.area < 8: continue
            walls(ctx, p, 0.0, h, wc); flat(ctx, p, h, rc)
    # ── 신규 매스 ──
    SLAB = 0.45
    for b in ([] if before else sorted(M["BUILD"], key=lambda x: x["lot_no"])):
        p = b["geom"]; n = b["floors"]; fh = b["floor_h"]
        base = CATCOL[b["cat"]]
        if b["role"] == "주차": base = "#c6c6c6"
        z = 0.0
        for k in range(n):
            fcol = base
            if k == 0 and b["retail_ground"]: fcol = CATCOL["판매·음식"]
            walls(bld, p, z, z + fh - SLAB, rgb(fcol, 1.0))
            walls(bld, p, z + fh - SLAB, z + fh, rgb(fcol, 1.16))     # 슬래브 띠
            z += fh
        top = z
        if b["role"] == "공원시설": rc = rgb("#f6bdd4")
        elif b["cat"] == "역사유산": rc = rgb("#a85a1e")
        elif b["role"] == "주차": rc = rgb("#d7d7d7")
        else: rc = rgb(base, 1.12)
        flat(roofs, p, top, rc)
        inner = p.buffer(-1.3, join_style=2)
        if b["cat"] != "역사유산" and b["role"] != "주차" and not inner.is_empty and inner.area > 25:
            flat(roofs, inner, top + 0.12, rgb(GREEN_ROOF))
        rims.append((p, top))
    print("scene built %.1fs  (나무 %d)" % (time.time() - t0, len(park_pts)))
    return dict(ground=ground, shadow=sh, ctx=ctx, bld=bld, roofs=roofs, trees=tr, rims=rims)

class Cam:
    """평행투영 카메라의 월드→화면 매핑(이미지 픽셀). 렌더와 주석 배치에서 같은 식을 쓴다."""
    def __init__(self, az_deg, el_deg, W, H, ps, xc, yc):
        a = math.radians(az_deg); e = math.radians(el_deg)
        self.a, self.e, self.W, self.H, self.ps, self.xc, self.yc = a, e, W, H, ps, xc, yc
        self.r = np.array([-math.sin(a), math.cos(a)]); self.f = np.array([-math.cos(a), -math.sin(a)])
    def XY(self, x, y, z=0.0):
        p = np.array([x - ORG[0], y - ORG[1]])
        return float(p @ self.r), float(p @ self.f) * math.sin(self.e) + z * math.cos(self.e)
    def xy(self, x, y, z=0.0):
        X, Y = self.XY(x, y, z); k = self.H / (2 * self.ps)
        return self.W / 2 + (X - self.xc) * k, self.H / 2 - (Y - self.yc) * k

def render(az_deg=-35.0, el_deg=34.0, out=SP + r"\axo.png", W=3600, Hh=1900, zoom=1.0, shift=(0.0, 0.0), before=False):
    S = build(before)
    pl = pv.Plotter(off_screen=True, window_size=(W, Hh)); pl.set_background("#dcdcdb" if before else BG)
    for key, op in (("ground", 1.0), ("shadow", 0.17), ("ctx", 1.0), ("trees", 1.0), ("bld", 1.0), ("roofs", 1.0)):
        m = S[key].mesh()
        if m is None: continue
        flatkey = key in ("ground", "shadow")
        pl.add_mesh(m, scalars="rgb", rgb=True, lighting=not flatkey, ambient=(1.0 if flatkey else 0.60), diffuse=(0.0 if flatkey else 0.52), specular=0.0, opacity=op, show_scalar_bar=False)
    segs = []
    for p, top in S["rims"]:
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)
            for i in range(len(cs) - 1): segs.append(((cs[i][0] - ORG[0], cs[i][1] - ORG[1], top + 0.28), (cs[i + 1][0] - ORG[0], cs[i + 1][1] - ORG[1], top + 0.28)))
    if segs:
        pts = np.array([s for seg in segs for s in seg]); lines = np.hstack([[2, 2 * i, 2 * i + 1] for i in range(len(segs))])
        pl.add_mesh(pv.PolyData(pts, lines=lines), color="#555b52", line_width=1.1, opacity=0.5, lighting=False)
    # 카메라
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
    pl.add_light(key); pl.add_light(fill)
    pl.enable_anti_aliasing("ssaa")
    img = pl.screenshot(None, return_img=True).astype(float)
    cam = Cam(az_deg, el_deg, W, Hh, ps, xc, yc)
    # ── 가장자리 페이드: 부지 투영 마스크로부터의 화면 거리 ──
    m = Image.new("L", (W, Hh), 0); dr = ImageDraw.Draw(m)
    for p in polys(U):
        dr.polygon([cam.xy(x, y, 0) for (x, y) in p.exterior.coords], fill=255)
    mask = np.array(m) > 0
    dist = ndimage.distance_transform_edt(~mask)
    d0, d1 = 0.10 * W, 0.30 * W
    al = np.clip((dist - d0) / (d1 - d0), 0, 1) ** 1.3 * 0.92
    BGX = "#dcdcdb" if before else BG
    bgc = np.array([int(BGX[i:i + 2], 16) for i in (1, 3, 5)], float)
    img = img * (1 - al[..., None]) + bgc * al[..., None]
    if before:                                      # 현황은 흑백(통영 Before 형식): 채도 제거 + 약한 대비
        g = img @ np.array([0.299, 0.587, 0.114]); g = np.clip((g - 128) * 1.06 + 128, 0, 255)
        img = np.stack([g, g, g], axis=-1)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    if out.lower().endswith((".jpg", ".jpeg")): im.save(out, quality=93)
    else: im.save(out)
    meta = dict(az=az_deg, el=el_deg, W=W, H=Hh, ps=ps, xc=xc, yc=yc)
    pickle.dump(meta, open(_os.path.splitext(out)[0] + "_meta.pkl", "wb"))
    return out, meta

if __name__ == "__main__":
    az = float(sys.argv[1]) if len(sys.argv) > 1 else -35.0
    out = sys.argv[2] if len(sys.argv) > 2 else SP + r"\axo.png"
    t0 = time.time(); o, m = render(az, out=out); print("saved", o, "%.1fs" % (time.time() - t0))


