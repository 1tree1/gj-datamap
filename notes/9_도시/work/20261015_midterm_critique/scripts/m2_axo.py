"""M2 매스 재작업 v1 조감(16:9) — 중간마감 조감 렌더러(g5_program.build)에 새 매스·판(①②③)·A안 통경축을 넣는다
스타일: 여천역 조감 형식(흰 바탕·옅은 주변 평면·파스텔 용도색·층 띠), 옥상녹화 없음, 시점 서북서 az 152°·el 38°(구 역사 정면)
사용: python m2_axo.py [render|sheet|all]"""
from k0 import *
import math
from matplotlib.image import imread

VAR = os.environ.get("MASSVAR", "v1"); VDIR = {"v1": "mass_v1", "v1b": "mass_v1b"}[VAR]
MV = pickle.load(open(os.path.join(K0DIR, "..", VDIR, "data", "mass_%s.pkl" % VAR), "rb"))
OUT1 = os.path.join(K0DIR, "..", VDIR); IMG = os.path.join(OUT1, "_m2_axo.png")
CORR_, TERM_ = MV.get("CORR", CORR), MV.get("TERM", TERM)
S3 = dict(MV["S"]); S3["PLZ"] = [dict(p, kind=("광장" if p["kind"] == "통경축" else p["kind"])) for p in MV["S"]["PLZ"]]


def render(az=152.0, el=38.0, W=3840, H=2160, fill_w=0.80, cy=0.55):
    import g5_program as G
    import d2_axo as A2
    import pyvista as pv
    from d2_axo import Acc, flat, walls, Cam, rgb
    from PIL import Image, ImageDraw
    from scipy import ndimage
    G.M = dict(G.M, S=S3, BLD=MV["BLD"], LINKS=MV["LINKS"], TREES=MV["TREES"]); G.S = S3; G.BLD = MV["BLD"]; G.LINKS = MV["LINKS"]
    if MV.get("NO_GLASS"):                                                # v1-b: 유리 지붕 없음(퇴화 삼각형 1개로 대신)
        G.vault = lambda *a, **k: (np.array([[0.0, 0.0, -50.0], [0.01, 0.0, -50.0], [0.0, 0.01, -50.0]]), np.array([[0, 1, 2]]))
        G.vault_grid = lambda *a, **k: []
    S_ = G.build(ctx_flat=True)
    flat(S_["ground"], CORR_, 0.12, rgb("#efe6d2")); flat(S_["ground"], TERM_, 0.12, rgb("#eadcb8"))
    if "PLAT1" in MV: flat(S_["ground"], MV["PLAT1"], 0.12, rgb("#e3d8c2")); flat(S_["ground"], MV["PPLZ"], 0.12, rgb("#efe6d2"))
    dk = Acc(); cl = Acc()
    for d in MV["DECKS"]:
        walls(dk, d["g"], d["z0"], d["z1"], rgb(PLATC)); flat(dk, d["g"], d["z1"], rgb(G.mix(PLATC, "#ffffff", 0.35))); flat(dk, d["g"], d["z0"], rgb(G.mix(PLATC, "#000000", 0.25)))
    for g, top in MV["COLS"]: walls(cl, g, 0.0, top, rgb("#5b5b5b"))
    pl = pv.Plotter(off_screen=True, window_size=(W, H)); pl.set_background(G.BG)
    for key, op in (("ground", 1.0), ("shadow", 0.10), ("ctx", 1.0), ("trees", 1.0), ("bld", 1.0), ("roofs", 1.0), ("links", 1.0)):
        m = S_[key].mesh()
        if m is None: continue
        flatk = key in ("ground", "shadow", "ctx")
        pl.add_mesh(m, scalars="rgb", rgb=True, lighting=not flatk, ambient=(1.0 if flatk else 0.68), diffuse=(0.0 if flatk else 0.45), specular=0.0, opacity=op, show_scalar_bar=False)
    for a_ in (dk, cl):
        m = a_.mesh()
        if m is not None: pl.add_mesh(m, scalars="rgb", rgb=True, lighting=True, ambient=0.72, diffuse=0.40, specular=0.0, show_scalar_bar=False)
    for a_, op in S_["ext"]:
        pl.add_mesh(a_.mesh(), scalars="rgb", rgb=True, lighting=False, opacity=op, show_scalar_bar=False)
    for key, col, lw, op in (("ctxl", "#d4d4d0", 0.8, 0.9), ("mull", "#3c3c3c", 0.7, 0.14), ("rims", "#5f5f5a", 1.1, 0.6)):
        m = S_[key].mesh()
        if m is not None: pl.add_mesh(m, color=col, line_width=lw, opacity=op, lighting=False)
    if not MV.get("NO_GLASS"):
        pl.add_mesh(S_["glass"].mesh(), scalars="rgb", rgb=True, opacity=0.42, ambient=0.85, diffuse=0.35, show_scalar_bar=False)
        pl.add_mesh(S_["gl"].mesh(), color="#7d98ab", line_width=1.0, opacity=0.85, lighting=False)
    a = math.radians(az); e = math.radians(el)
    c = np.array([math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)])
    ps, xc, yc = A2.frame(az, el, W, H, fill_w, cy)
    cam0 = Cam(az, el, W, H, 1.0, 0.0, 0.0)
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
    al = np.clip((dist - 0.08 * W) / (0.30 * W), 0, 1) ** 1.2 * 0.85
    img = img * (1 - al[..., None]) + G.hx(G.BG) * al[..., None]
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(IMG)
    pickle.dump(dict(az=az, el=el, W=W, H=H, ps=ps, xc=xc, yc=yc), open(os.path.splitext(IMG)[0] + "_meta.pkl", "wb"))
    print("saved", IMG)


def sheet():
    import g5_program as G
    from d2_axo import Cam
    meta = pickle.load(open(os.path.splitext(IMG)[0] + "_meta.pkl", "rb"))
    cam = Cam(meta["az"], meta["el"], meta["W"], meta["H"], meta["ps"], meta["xc"], meta["yc"])
    def mm(x, y, z=0.0):
        px, py = cam.xy(x, y, z); return px * PW / meta["W"], py * PH / meta["H"]
    pg = Page()
    pg.ax.imshow(imread(IMG), extent=[0, PW, PH, 0], aspect="auto", zorder=0, interpolation="bilinear"); pg.ax.set_xlim(0, PW); pg.ax.set_ylim(PH, 0)
    TT = MV["TOT"]
    if VAR == "v1":
        pg.header("Critique Response : Massing v1", "Massing v1 · Bird's-eye", "매스 재작업 v1 조감",
                  sub="획지 건폐율 %.2f → %.2f · 평균 %.1f → %.1f층 · 최고 5층 · 판 ①②③ · 화랑로 A안 통경축 — 서북서에서 본 구 역사 정면" % (TT["ba0"] / TOT["lot"], TT["ba"] / TT["lot"], TT["gfa0"] / TT["ba0"], TT["gfa"] / TT["ba"]))
    else:
        pg.header("Critique Response : Massing v1-b · 검토안", "Massing v1-b · Bird's-eye", "검토안 조감 — 구 역사를 실제 위치에 둔 경우",
                  sub="화랑로 → 역 앞마당·삼층석탑 → 대합실 관통 통로 → 옛 1번 승강장 캐노피 → 플랫폼 광장 · 획지 건폐율 %.2f · 평균 %.1f층 — 서북서 시점" % (TT["ba"] / TT["lot"], TT["gfa"] / TT["ba"]))
    D_ = {d["name"]: d for d in MV["DECKS"]}
    k1 = [k for k in D_ if k.startswith("①")][0]; c1 = D_[k1]["g"].centroid; c2 = D_["② 화랑로 게이트"]["g"].centroid
    CALLS = [(c1.x, c1.y, 6.5, k1, PLATC), (c2.x, c2.y, 6.0, "② 화랑로 게이트", PLATC), (271, 496, 4.0, "③ 교차광장 공중 회랑", PLATC),
             (360, EWB.centroid.y, 0.5, "보행 통경축 20 m(A안)", "#8a6d2e")]
    if VAR == "v1": CALLS += [(135, 300, 0.5, "화랑로 끝 광장", "#8a6d2e")]
    else: CALLS += [(126, 320, 0.5, "역 앞마당 · 삼층석탑", "#8a6d2e"), (158, HWARANG_Y, 3.0, "대합실 관통 통로", "#b07d10"), (220, 312, 0.5, "플랫폼 광장", "#8a6d2e")]
    CALLS += [
             (185, 705, 16.0, "공공청사 · 중정형 4층", LOTCOL["공공업무"]), (340, 707, 12.0, "청년주택 · 중정형 블록", LOTCOL["주거"]),
             (200, 430, 8.0, "전통공예 · 골목 매트", LOTCOL["창작"]), (365, 270, 13.0, "공유주차 · 라이닝 주차", LOTCOL["주차"]),
             (240, 575, 20.0, "업무·창업 · ㄷ자", LOTCOL["업무·창업"]), (300, 255, 12.0, "근대역사관 · 둘레형", LOTCOL["문화"])]
    if VAR == "v1b": CALLS = [c for c in CALLS if not c[3].startswith("업무")]
    anchors = [mm(x, y, z) for x, y, z, t_, c_ in CALLS]
    EXCL = [(0, 0, 220, 34), (0, 212, PW, 13)] + [(ax_ - 1.5, ay_ - 1.5, 3.0, 3.0) for ax_, ay_ in anchors]
    placed = []
    def free(x, y, w, h):
        if x < 3 or x + w > PW - 3 or y < 36 or y + h > 211: return False
        for q in placed + EXCL:
            if not (x + w < q[0] - 1.2 or q[0] + q[2] < x - 1.2 or y + h < q[1] - 1.2 or q[1] + q[3] < y - 1.2): return False
        return True
    for (x, y, z, title, col), (ax_, ay_) in sorted(zip(CALLS, anchors), key=lambda t: t[1][1]):
        w = text_w(pg, title, 10, True) + 5.0; h = 6.2; got = None
        for dy in (-14, -22, 8, 16, -30, 24, -38, 32):
            for dx in (8, -w - 8, 18, -w - 18, -w / 2, 30, -w - 30):
                if free(ax_ + dx, ay_ + dy, w, h): got = (ax_ + dx, ay_ + dy); break
            if got: break
        if got is None: got = (ax_ + 8, ay_ - 14); print("  ! 자리 없음", title)
        bx, by = got; placed.append((bx, by, w, h))
        tx_ = min(max(ax_, bx), bx + w); ty_ = by + h if by + h < ay_ else (by if by > ay_ else by + h / 2)
        pg.line([ax_, tx_], [ay_, ty_], c="#444", lw=0.5, z=11)
        pg.ax.add_patch(Circle((ax_, ay_), 0.8, fc="#444", ec="white", lw=0.4, zorder=12))
        pg.rect(bx, by, w, h, fc="white", ec=col, lw=0.6, z=12, alpha=0.95); pg.rect(bx, by, 1.4, h, fc=col, z=13)
        pg.t(bx + 3.0, by + h / 2, title, fs=10, bold=True, z=14)
    ly = 219.0; ex = 6
    pg.rect(0, ly - 4.0, PW, 8.0, fc="white", ec="none", alpha=0.92, z=13)
    for k, lab_ in (("공공업무", "공공업무"), ("업무·창업", "업무·창업"), ("문화", "문화·집회"), ("창작", "창작·공방"), ("판매", "근린생활"), ("생활SOC", "체육·복지"),
                    ("주거", "주거"), ("역사", "역사유산"), ("방문자", "관광"), ("주차", "주차·교통")):
        pg.rect(ex, ly - 1.7, 4.0, 3.4, fc=G.PCOL[k], ec="#9a9a9a", lw=0.25, z=14); t_ = pg.t(ex + 5.2, ly, lab_, fs=10, z=14); ex += 5.2 + pg.wmm(t_) + 3.6
    pg.rect(ex, ly - 1.7, 4.0, 3.4, fc=PLATC, z=14); t_ = pg.t(ex + 5.2, ly, "판 ①②③", fs=10, z=14); ex += 5.2 + pg.wmm(t_) + 3.6
    pg.rect(ex, ly - 1.7, 4.0, 3.4, fc="#efe6d2", ec="#cdbf9f", lw=0.3, z=14); t_ = pg.t(ex + 5.2, ly, "통경축", fs=10, z=14); ex += 5.2 + pg.wmm(t_) + 3.6
    if not MV.get("NO_GLASS"): pg.rect(ex, ly - 1.7, 4.0, 3.4, fc="#cfe6f3", ec="#7d98ab", lw=0.4, z=14); pg.t(ex + 5.2, ly, "유리 지붕", fs=10, z=14)
    NAME = {"v1": "M2_매스재작업_조감", "v1b": "M2b_매스변형v1b_조감"}[VAR]
    pg.fig.savefig(os.path.join(OUT1, NAME + ".png"), dpi=240, facecolor="white")
    pg.fig.savefig(os.path.join(OUT1, NAME + ".pdf"), facecolor="white"); plt.close(pg.fig); print("saved", NAME)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("render", "all"): render()
    if mode in ("sheet", "all"): sheet()
