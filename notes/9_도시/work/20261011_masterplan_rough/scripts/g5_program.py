"""G5 프로그램 구성도(16:9) — 참고: 이주대책 지원형 조감(흰 주변 매스 + 용도색 매스 + 지시선 라벨)
최종본 건축물의 구성 솔리드별·층별 용도 색, 1층 근린생활, 연결 브리지·캐노피, 유리 지붕, 구 역사(모임지붕 근사)
사용: python g5_program.py [render|sheet|all]"""
import sys, math, time, random, pickle, json, os
import numpy as np
import pyvista as pv
from shapely.geometry import Polygon, box, Point, LineString
from shapely.ops import unary_union, polylabel
from shapely import affinity
from PIL import Image, ImageDraw
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import d2_axo as A2
from d2_axo import Acc, Seg, flat, walls, tree_mesh, Cam, rgb, lerp, polys
from geom2 import hip_roof, vault, vault_grid
pv.OFF_SCREEN = True
D = os.path.join(HERE, "..", "data"); SH = os.path.join(HERE, "..", "sheets")
M = pickle.load(open(os.path.join(D, "model.pkl"), "rb"))
S = M["S"]; BLD, LINKS = M["BLD"], M["LINKS"]
B = S["B"]; CATS = S["CATS"]; X0, Y0, XS = S["X0"], S["Y0"], S["XSHIFT"]
FH = {"주거": 3.0, "주차": 3.2, "역사": 4.5}
BG = "#f7f7f5"


def hx(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)


def mix(h1, h2, t):
    c = hx(h1) * (1 - t) + hx(h2) * t; return "#%02x%02x%02x" % tuple(int(round(v)) for v in np.clip(c, 0, 255))


# 조감용 용도색 — 파스텔(CATS)과 평면색의 중간(프로그램이 읽히는 채도)
LOTCOL = {"공공업무": "#6E8FC9", "업무·창업": "#EE8A62", "문화": "#7FC0D6", "창작": "#AE93D6", "판매": "#F09AB0", "생활SOC": "#6FC6AA",
          "주거": "#F1CF7E", "역사": "#B97A4E", "방문자": "#B9C3CD", "주차": "#A3A8AE"}
PCOL = {k: mix(CATS[k][0], LOTCOL[k], 0.55) for k in CATS}


def build(ctx_flat=False):
    """ctx_flat=True: 주변 건물을 높이 없는 평면 윤곽(옅은 회색 면 + 선)으로 — g5a 조감 호출 시트용"""
    t0 = time.time(); rnd = random.Random(5)
    ground = Acc(); ctx = Acc(); sh = Acc(); bld = Acc(); roofs = Acc(); tr = Acc(); glass = Acc(); lk = Acc()
    rims = Seg(); mull = Seg(); gl = Seg(); ctxl = Seg()
    flat(ground, box(*B.buffer(520).bounds), -0.3, rgb(BG))
    Bb = B.buffer(1.0); n = 0
    CF = pickle.load(open(os.path.join(D, "ctx_fixed.pkl"), "rb"))      # 정합된 주변 건물(로컬)
    for o in CF["B"]:
        pg = o["g"]
        if o["inside"] or pg.area < 8: continue
        d = pg.distance(B)
        if d > 420: continue
        h = max(o["h"], 3.5); t = float(np.clip((d - 80) / 300, 0, 0.8))
        for p in polys(pg):
            if ctx_flat:
                flat(ctx, p, 0.0, lerp("#e9e9e6", "#f3f3f1", float(np.clip((d - 60) / 360, 0, 1))))
                cs = list(p.exterior.coords)
                for i in range(len(cs) - 1): ctxl.add((cs[i][0], cs[i][1], 0.08), (cs[i + 1][0], cs[i + 1][1], 0.08))
            else:
                walls(ctx, p, 0.0, h, lerp("#f4f4f2", "#ececea", t)); flat(ctx, p, h, lerp("#fdfdfc", "#f2f2f0", t))
        n += 1
    flat(ground, B, -0.2, rgb("#f1f0ec"))
    flat(ground, S["WALK"], 0.0, rgb("#ffffff")); flat(ground, S["PATH8"], 0.0, rgb("#ffffff"))
    for r in S["ROADS"].values(): flat(ground, r, 0.02, rgb("#dcdad5"))
    for l in S["LOTS"]: flat(ground, l["g"], 0.05, rgb("#f6f5f1"))
    for p in S["PARKS"]: flat(ground, p["g"], 0.08, rgb("#cde7b2"))
    for o in S["OPEN"]: flat(ground, o["g"], 0.08, rgb("#b9e09a" if o["key"] == "D" else "#e6eedb"))
    for p in S["PLZ"]:
        k = p["kind"]
        flat(ground, p["g"], 0.1, rgb({"광장": "#ece5d4", "코트": "#efe8da", "노외주차": "#d4d4d1", "텃밭": "#d6bb92"}.get(k, "#cde7b2")))
    for (x, y, r) in M["TREES"]: tree_mesh(tr, x, y, min(r, 4.2), lerp("#86c25a", "#a6d47a", rnd.random()))
    # 그림자
    sx, sy = 0.62, -0.42; allp = []
    for b in BLD:
        h = b["h"] + 0.5
        allp.append(unary_union([b["g"], affinity.translate(b["g"], sx * h, sy * h)]).convex_hull.intersection(unary_union([b["g"].buffer(0.1), affinity.translate(b["g"], sx * h, sy * h)]).convex_hull))
    flat(sh, unary_union(allp).difference(unary_union([b["g"] for b in BLD])).intersection(B.buffer(30)), 0.2, rgb("#3a4450"))
    # 건축물 — 구성 솔리드별 층 적층
    for b in BLD:
        for (g, z0, z1, cat) in b["parts"]:
            if b["name"] == "구 경주역사": continue
            fh = FH.get(cat, 4.0); nf = max(1, int(round((z1 - z0) / fh))); fh_ = (z1 - z0) / nf
            c = PCOL[cat]
            for k in range(nf):
                za = z0 + k * fh_
                walls(bld, g, za, za + fh_ - 0.45, rgb(c)); walls(bld, g, za + fh_ - 0.45, za + fh_, rgb(mix(c, "#ffffff", 0.5)))
            flat(roofs, g, z1, rgb(mix(c, "#ffffff", 0.25)))
            for p in polys(g):
                for ring in [p.exterior] + list(p.interiors):
                    cs = list(ring.coords)
                    for i in range(len(cs) - 1): rims.add((cs[i][0], cs[i][1], z1 + 0.08), (cs[i + 1][0], cs[i + 1][1], z1 + 0.08))
                    L = LineString(cs)
                    for dd in np.arange(1.8, L.length, 3.6):
                        q = L.interpolate(dd); mull.add((q.x, q.y, z0 + 0.15), (q.x, q.y, z1 - 0.15))
    # 구 경주역사 — 2층 벽 + 모임지붕(근사)
    st = [b for b in BLD if b["name"] == "구 경주역사"][0]
    walls(bld, st["g"], 0, 4.05, rgb(PCOL["역사"])); walls(bld, st["g"], 4.05, 4.5, rgb("#e8d6c4")); walls(bld, st["g"], 4.5, 8.55, rgb(PCOL["역사"])); walls(bld, st["g"], 8.55, 9.0, rgb("#e8d6c4"))
    rp = st["g"].buffer(0.8, join_style=2); V, Fc = hip_roof(rp, 8.95, 33.0, 0.5, axis=(S["GLASS"]["ua"][0], S["GLASS"]["ua"][1])); roofs.tri(V, Fc, rgb("#6b5a52"))
    # 연결 브리지·캐노피
    for k in LINKS:
        walls(lk, k["g"], k["z0"], k["z1"], rgb("#55595e")); flat(lk, k["g"], k["z1"], rgb("#7b8087")); flat(lk, k["g"], k["z0"], rgb("#55595e"))
    V, Fc = vault(S["GLASS"], 1.5); glass.tri(V, Fc, rgb("#cfe6f3"))
    for p_, q_ in vault_grid(S["GLASS"], 4.0, 0.6): gl.add(p_, q_)
    # (ctx_flat 시트) 동서 선형공원 띠를 사이트 밖으로 연장 — 경계에서 멀어질수록 옅게(d2_axo v2 조감과 같은 방식)
    ext = []
    if ctx_flat:
        y0b, y1b = S["DBAND"]
        xw, _, xe, _ = B.intersection(LineString([(-500, (y0b + y1b) / 2), (900, (y0b + y1b) / 2)])).bounds
        for k in range(12):
            L = 15.0
            for xa, xb in ((xw - (k + 1) * L, xw - k * L), (xe + k * L, xe + (k + 1) * L)):
                g = box(xa, y0b, xb, y1b).difference(B.buffer(0.5))
                if not g.is_empty:
                    a_ = Acc(); flat(a_, g, 0.25, rgb("#7cc865"))
                    if a_.v: ext.append((a_, 0.62 * (1 - k / 12.0) ** 1.4))
    print("scene %.1fs ctx %d" % (time.time() - t0, n))
    return dict(ext=ext, ground=ground, ctx=ctx, shadow=sh, bld=bld, roofs=roofs, trees=tr, glass=glass, links=lk, rims=rims, mull=mull, gl=gl, ctxl=ctxl, ctx_flat=ctx_flat)


def render(out, az=152.0, el=38.0, W=3840, H=2160, fill_w=0.80, cy=0.55, ctx_flat=False, focus=None, fade=True):
    """focus=(x, y, 반높이 m, z): 그 점을 화면 가운데에 두는 확대 렌더(fade 끔 권장)"""
    S_ = build(ctx_flat)
    pl = pv.Plotter(off_screen=True, window_size=(W, H)); pl.set_background(BG)
    for key, op in (("ground", 1.0), ("shadow", 0.10), ("ctx", 1.0), ("trees", 1.0), ("bld", 1.0), ("roofs", 1.0), ("links", 1.0)):
        m = S_[key].mesh()
        if m is None: continue
        flatk = key in ("ground", "shadow") or (key == "ctx" and S_["ctx_flat"])
        pl.add_mesh(m, scalars="rgb", rgb=True, lighting=not flatk, ambient=(1.0 if flatk else 0.68), diffuse=(0.0 if flatk else 0.45), specular=0.0, opacity=op, show_scalar_bar=False)
    for a_, op in S_["ext"]:
        pl.add_mesh(a_.mesh(), scalars="rgb", rgb=True, lighting=False, opacity=op, show_scalar_bar=False)
    for key, col, lw, op in (("ctxl", "#d4d4d0", 0.8, 0.9), ("mull", "#3c3c3c", 0.7, 0.14), ("rims", "#5f5f5a", 1.1, 0.6)):
        m = S_[key].mesh()
        if m is not None: pl.add_mesh(m, color=col, line_width=lw, opacity=op, lighting=False)
    pl.add_mesh(S_["glass"].mesh(), scalars="rgb", rgb=True, opacity=0.42, ambient=0.85, diffuse=0.35, show_scalar_bar=False)
    pl.add_mesh(S_["gl"].mesh(), color="#7d98ab", line_width=1.0, opacity=0.85, lighting=False)
    a = math.radians(az); e = math.radians(el)
    c = np.array([math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)])
    ps, xc, yc = A2.frame(az, el, W, H, fill_w, cy)
    cam0 = Cam(az, el, W, H, 1.0, 0.0, 0.0)
    if focus is not None:
        xc, yc = cam0.XY(focus[0], focus[1], focus[3] if len(focus) > 3 else 8.0); ps = focus[2]
    Pf = xc * cam0.r + (yc / math.sin(e)) * cam0.f; focal = np.array([Pf[0], Pf[1], 0.0])
    pl.camera.parallel_projection = True; pl.camera_position = [tuple(focal + 3000 * c), tuple(focal), (0, 0, 1)]
    pl.camera.parallel_scale = ps; pl.camera.clipping_range = (10, 9000)
    pl.remove_all_lights()
    pl.add_light(pv.Light(position=tuple(focal + 2000 * np.array([math.cos(a - 0.95) * 0.7, math.sin(a - 0.95) * 0.7, 0.95])), focal_point=tuple(focal), color="white", intensity=0.95, light_type="scene light"))
    pl.add_light(pv.Light(position=tuple(focal + 2000 * np.array([math.cos(a + 2.3) * 0.6, math.sin(a + 2.3) * 0.6, 0.5])), focal_point=tuple(focal), color="white", intensity=0.35, light_type="scene light"))
    pl.enable_anti_aliasing("ssaa")
    img = pl.screenshot(None, return_img=True).astype(float)
    cam = Cam(az, el, W, H, ps, xc, yc)
    m = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(m)
    dr.polygon([cam.xy(x, y, 0) for (x, y) in B.exterior.coords], fill=255)
    dist = ndimage.distance_transform_edt(~(np.array(m) > 0))
    al = np.clip((dist - 0.08 * W) / (0.30 * W), 0, 1) ** 1.2 * 0.85 * (1.0 if fade else 0.0)
    img = img * (1 - al[..., None]) + hx(BG) * al[..., None]
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out)
    pickle.dump(dict(az=az, el=el, W=W, H=H, ps=ps, xc=xc, yc=yc), open(os.path.splitext(out)[0] + "_meta.pkl", "wb"))
    print("saved", out)


def sheet():
    import gkit as K
    from gkit import Page, f0, halo, INK, GREY, SLATE, PW, PH
    import textwrap
    meta = pickle.load(open(os.path.join(SH, "prog_axo_meta.pkl"), "rb"))
    cam = Cam(meta["az"], meta["el"], meta["W"], meta["H"], meta["ps"], meta["xc"], meta["yc"])
    def mm(x, y, z=0.0):
        px, py = cam.xy(x, y, z); return px * PW / meta["W"], py * PH / meta["H"]
    pg = Page()
    from matplotlib.image import imread
    pg.ax.imshow(imread(os.path.join(SH, "prog_axo.png")), extent=[0, PW, PH, 0], aspect="auto", zorder=0, interpolation="bilinear"); pg.ax.set_xlim(0, PW); pg.ax.set_ylim(PH, 0)
    pg.header("Masterplan : Program", "Program Composition", "프로그램 구성도", sub="건축물 41동 · 층별 용도 색 — 1층 근린생활, 상부 연결 브리지, 유리 지붕 중정 포함")
    byname = {}
    for b in BLD: byname.setdefault(b["name"], []).append(b)
    NMC = {"판매": "근린생활", "공공업무": "공공업무", "업무·창업": "업무·창업", "문화": "문화", "창작": "창작·공방", "생활SOC": "생활SOC", "주거": "주거", "주차": "주차", "방문자": "관광안내", "역사": "역사"}
    def floors_txt(b):
        rng = {}
        for (g, z0, z1, cat) in b["parts"]:
            fh = FH.get(cat, 4.0); a_ = int(round(z0 / fh)) + 1; c_ = max(a_, int(round(z1 / fh)))
            lo, hi = rng.get(cat, (99, 0)); rng[cat] = (min(lo, a_), max(hi, c_))
        return " · ".join(("%dF %s" % (lo, NMC[k])) if lo == hi else ("%d–%dF %s" % (lo, hi, NMC[k])) for k, (lo, hi) in sorted(rng.items(), key=lambda kv: kv[1]))
    # 라벨 대상(앵커 동, 10 pt 짧은 이름) — 층별 용도는 색으로 읽고, 라벨은 이름만
    LBL = [("공공청사 본관", "공공청사"), ("공공청사·기관 직원 주차장동(청사 연결 브리지 포함)", "직원 주차장동"), ("생활체육관·편의시설", "생활체육관"),
           ("주거동 4", "청년·신혼 공공임대주택"), ("공공기관 업무동", "공공기관 업무동"), ("청년창업지원센터", "청년창업지원센터"), ("복합문화센터", "복합문화센터"),
           ("건강·돌봄센터", "건강·돌봄센터"), ("전통문화 공방·전시·공예마켓동", "공방·전시·공예마켓"), ("공방·판매동", "공방·판매동"), ("실내 체험관", "실내 체험관"),
           ("레지던시 제작동 2", "아티스트 레지던시"), ("구 경주역사", "구 경주역사"), ("지역문화원 본동", "지역문화원·상생동"), ("근대역사관", "근대역사관"),
           ("관광지원센터", "관광지원센터"), ("관문 가로상가", "관문 가로상가"), ("공유주차장", "공유주차장"), ("모빌리티 허브", "모빌리티 허브")]
    pts = []
    for key, title in LBL:
        bs = byname.get(key)
        if not bs: print("  ! no", key); continue
        b = max(bs, key=lambda b: b["g"].area)
        c = polylabel(max(polys(b["g"]), key=lambda g: g.area), 0.5)
        ax_, ay_ = mm(c.x, c.y, b["h"])
        pts.append((ax_, ay_, title, K.LOTCOL.get(b["main"], "#999")))
    # 표·범례 자리(오른쪽 아래 막대표, 아래 띠, 머리글)
    px, py = 288, 132
    EXCL = [(0, 0, 175, 34), (px - 3, py - 7, PW - px + 3, 214 - py + 7), (0, 212, PW, 13)]
    placed = []
    def free(x, y, w, h):
        if x < 3 or x + w > PW - 3 or y < 3 or y + h > 211: return False
        for q in placed + EXCL:
            if not (x + w < q[0] - 1.0 or q[0] + q[2] < x - 1.0 or y + h < q[1] - 1.0 or q[1] + q[3] < y - 1.0): return False
        return True
    for ax_, ay_, title, col in sorted(pts, key=lambda p: p[1]):
        w = K.text_w(pg, title, 10, True) + 5.0; h = 6.0
        cands = []
        for dy in (-10, -17, -24, -31, 5, 12, -38):
            for dx in (-w / 2, 4, -w - 4, 12, -w - 12):
                cands.append((dx, dy - h if dy < 0 else dy))
        x = y = None
        for dx, dy in cands:
            if free(ax_ + dx, ay_ + dy, w, h): x, y = ax_ + dx, ay_ + dy; break
        if x is None: x, y = ax_ - w / 2, ay_ - 10 - h; print("  ! overlap", title)
        placed.append((x, y, w, h))
        ty_ = y + h if y + h < ay_ else y
        tx_ = min(max(ax_, x + 2), x + w - 2)
        pg.line([ax_, tx_], [ay_, ty_], c="#444", lw=0.5, z=11)
        pg.ax.add_patch(K.Circle((ax_, ay_), 0.8, fc="#444", ec="white", lw=0.4, zorder=12))
        pg.rect(x, y, w, h, fc="white", ec=col, lw=0.6, z=12, alpha=0.94)
        pg.rect(x, y, 1.4, h, fc=col, z=13)
        pg.t(x + 3.0, y + h / 2, title, fs=10, bold=True, z=14)
    # 녹지·보행 라벨
    for xx, yy_, s_ in ((150, 496, "동서 선형공원"), (271, 600, "남북 중앙 보행축"), (160, 128, "관문광장·사선 보행축"), (250, 900, "북측 근린공원")):
        x, y = mm(xx, yy_, 0.5)
        if any(not (x + 20 < q[0] or q[0] + q[2] < x - 20 or y + 3 < q[1] or q[1] + q[3] < y - 3) for q in placed): y += 6
        pg.t(x, y, s_, fs=10, c="#2f8f3a", bold=True, ha="center", style="italic", path_effects=halo(2.4), z=12)
    # 용도별 연면적(오른쪽 아래)
    tot = {}
    for b in BLD:
        for k, v in b["gfa_by"].items(): tot[k] = tot.get(k, 0) + v
    order = sorted(tot, key=lambda k: -tot[k]); T_ = sum(tot.values())
    pg.rect(px - 3, py - 7, PW - px + 1, 214 - py + 5, fc="white", ec="#dddddd", lw=0.4, z=12, alpha=0.95)
    pg.t(px, py - 2.4, "용도별 연면적(지상)", fs=10, bold=True, z=13)
    LW = max(K.text_w(pg, CATS[k][1], 10) for k in order) + 2.0
    for i, k in enumerate(order):
        yy = py + 4.0 + i * 6.2; v = tot[k]
        pg.t(px, yy, CATS[k][1], fs=10, z=13)
        bw = 34 * v / tot[order[0]]
        pg.rect(px + LW, yy - 1.8, bw, 3.6, fc=K.LOTCOL[k], z=13)
        pg.t(px + LW + bw + 1.2, yy, "%.1f%%" % (v / T_ * 100), fs=10, c=GREY, z=13)
    pg.t(px, py + 4.0 + len(order) * 6.2 + 0.4, "합계 %s㎡ · %d동" % (f0(T_), len(BLD)), fs=10, bold=True, z=13)
    # 범례(아래 띠)
    ly = 219.0; ex = 6
    pg.rect(0, ly - 4.0, PW, 8.0, fc="white", ec="none", alpha=0.92, z=13)
    for k in ["공공업무", "업무·창업", "문화", "창작", "판매", "생활SOC", "주거", "역사", "방문자", "주차"]:
        lab = {"공공업무": "공공업무", "업무·창업": "업무·창업", "문화": "문화·집회", "창작": "창작·공방", "판매": "근린생활", "생활SOC": "체육·복지", "주거": "주거",
               "역사": "역사유산", "방문자": "관광", "주차": "주차·교통"}[k]
        pg.rect(ex, ly - 1.7, 4.0, 3.4, fc=PCOL[k], ec="#9a9a9a", lw=0.25, z=14); t_ = pg.t(ex + 5.2, ly, lab, fs=10, z=14); ex += 5.2 + pg.wmm(t_) + 3.6
    pg.rect(ex, ly - 1.7, 4.0, 3.4, fc="#6b7076", z=14); t_ = pg.t(ex + 5.2, ly, "브리지·캐노피", fs=10, z=14); ex += 5.2 + pg.wmm(t_) + 3.6
    pg.rect(ex, ly - 1.7, 4.0, 3.4, fc="#cfe6f3", ec="#7d98ab", lw=0.4, z=14); pg.t(ex + 5.2, ly, "유리 지붕", fs=10, z=14)
    pg.save("D5_프로그램구성도")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("render", "all"): render(os.path.join(SH, "prog_axo.png"))
    if mode in ("sheet", "all"): sheet()
