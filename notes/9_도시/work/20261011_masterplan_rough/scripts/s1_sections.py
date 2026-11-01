"""S1 단면 조닝 다이어그램 3장(16:9) — 사용자 평면 캡처의 보라색 세 선 · 손스케치 조닝(N–S, W–E, 사선 W–E)
참고 형식: 서대구역 '환승 랜드마크 앵커'(용도색 블록 + 하단 구역 띠), '입체적 도시'(블록 안 라벨·붉은 점선 동선·양끝 방향 화살표·지면 띠)
입력: data/cuts.pkl(s0_cuts.py), model.pkl, ctx_fixed.pkl, design.pkl  출력: diagrams/D6~D8_단면조닝_*.png/pdf
사용: python s1_sections.py [V|H|Dg|all]"""
import sys, math
from gkit import *
from matplotlib.patches import FancyArrowPatch, Circle, Ellipse, Polygon as MPoly, FancyBboxPatch
from shapely.geometry import LineString

CUTS = pickle.load(open(os.path.join(D, "cuts.pkl"), "rb"))
CF = pickle.load(open(os.path.join(D, "ctx_fixed.pkl"), "rb"))["B"]
SLJ = json.load(open(os.path.join(D, "section_lines.json"), encoding="utf-8"))
FH = {"주거": 3.0, "주차": 3.2, "역사": 4.5}
PURPLE = "#A0237A"; ROUTE = "#D7263D"; TEAL = "#1F4E5F"
COMM = LOTCOL["판매"]                                                    # 1층 커뮤니티·근린생활

SHEETS = {
    "V": dict(file="D6_단면조닝_남북", tag="A", title_en="Section Zoning A–A′", title_ko="남북 단면 조닝",
              sub="체육관에서 전시관까지 — 대지축(남북)을 따라 정주·생활문화·체험·전시가 이어지는 단면",
              ends=("N", "S"), end_txt=("북천·황성공원", "대릉원 방면"),
              bld=[("체육관", ["생활체육관·편의시설"], None), ("주거시설", ["주거동 1", "주거동 3", "주거동 5", "주거동 7"], "above"),
                   ("복합문화공간", ["복합문화센터"], None), ("실내체험관 · 작가 교류·행사실", ["실내 체험관"], None), ("전시관", ["근대역사관"], "above")],
              comm_1f=["주거동 1", "주거동 3", "주거동 5", "주거동 7"],
              ground=[("북측 근린공원", "북측 근린공원"), ("북측 진입도로", "북측 진입도로"), ("향일문 조망로", "향일문 조망로"),
                      ("중앙 인도", "동서 선형공원·가로광장(폭 40m)"), ("남측 차도", "동서 도로"), ("외곽도로", "외곽도로")],
              boxes=[("북측 근린공원", "공원", "북측 근린공원과 북측 진입도로(폭 13 m)"),
                     ("체육관", "생활SOC", "생활체육관·편의시설 4층"),
                     ("주거시설", "주거", "청년·신혼 공공임대 판상동 · 1층 커뮤니티 · 2~5층 주거"),
                     ("복합문화공간", "문화", "1층 근린생활 · 2~4층 문화"),
                     ("중앙 인도", "선형", "동서 선형공원 폭 40 m · 가로수 4열"),
                     ("실내체험관 · 작가 교류", "문화", "체험관과 작가 교류·행사실 4층"),
                     ("남측 차도", "도로", "동서 도로 폭 20 m(화랑로 연결)"),
                     ("전시관", "문화", "중정형 4층 · 사선 보행축 상부 연결")]),
    "H": dict(file="D7_단면조닝_동서", tag="B", title_en="Section Zoning B–B′", title_ko="동서 단면 조닝",
              sub="휴게공간에서 레지던시까지 — 공예·체험 가구를 동서로 자른 단면, 중앙 남북 인도에서 두 가구가 만남",
              ends=("W", "E"), end_txt=("원화로·원도심", "동측 생활권"),
              bld=[("휴게공간", ["공방·판매동"], None), ("공방·전시동", ["전통문화 공방·전시·공예마켓동"], None), ("실내체험관", ["실내 체험관"], None),
                   ("제작동", ["레지던시 제작동 1"], "above"), ("거주동", ["레지던시 거주동 1"], "above")],
              group=("레지던시", ["제작동", "거주동"]),
              ground=[("야외체험관", "공예 중정(근린공원)"), ("중앙 남북 인도", "남북 중앙 보행축(폭 30m)"), ("레지던시 마당", "레지던시 마당"), ("외곽도로", "외곽도로")],
              boxes=[("휴게공간", "판매", "공방·판매동 2층과 캐노피"),
                     ("야외체험관", "공원", "공예 중정 · 야외 체험 마당"),
                     ("공방·전시동", "창작", "전통공예 공방·전시·공예마켓 3층"),
                     ("중앙 남북 인도", "선형", "남북 중앙 보행축 폭 30 m"),
                     ("실내체험관", "문화", "실내 체험관 4층"),
                     ("레지던시", "창작", "제작동 3층 · 거주동 5층 · 레지던시 마당")]),
    "Dg": dict(file="D8_단면조닝_사선", tag="C", title_en="Section Zoning C–C′", title_ko="사선 단면 조닝",
               sub="경주회관 앞마당에서 전시관까지 — 구 경주역사(근대역사관)와 유리 지붕 코트를 지나 남측 관광객 인도로 이어지는 단면",
               ends=("W", "E"), end_txt=("원화로 방면", "동측 생활권"),
               bld=[("근대역사관", ["구 경주역사"], None), ("지역문화원", ["지역문화원 본동"], None), ("전시관", ["근대역사관"], "above")],
               ground=[("경주회관 앞마당", "역전광장"), ("그레이트 코트", "그레이트 코트(유리 지붕 중정)"), ("남측 관광객 인도", "관문광장·사선 보행축(폭 20m)"),
                       ("전시관 중정", "근대역사관 중정"), ("외곽도로", "외곽도로")],
               boxes=[("경주회관 앞마당", "광장", "역 정면 광장 · 현관 축 가로수"),
                      ("근대역사관", "역사", "구 경주역사 존치·복원 2층 · 모임지붕"),
                      ("그레이트 코트", "유리", "역사와 지역문화원 사이 유리 지붕 중정"),
                      ("지역문화원", "문화", "1층 소상공인 점포 · 2~5층 문화"),
                      ("남측 관광객 인도", "선형", "관문광장에서 이어지는 사선 보행축 폭 20 m"),
                      ("전시관", "문화", "중정형 4층(양 날개)")]),
}
BOXCOL = dict(LOTCOL, 공원="#7DBE5B", 선형="#3DA24B", 도로="#636363", 광장="#C9B48A", 유리="#7FB3CF")


def lum(h):
    c = [int(h[i:i + 2], 16) for i in (1, 3, 5)]; return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def person(ax_, x, y, h=5.2, c="#3b3b3b"):
    ax_.add_patch(Circle((x, y - h + 0.9), 0.85, fc=c, ec="none", zorder=18))
    ax_.add_patch(FancyBboxPatch((x - 0.75, y - h + 1.9), 1.5, h - 1.9, boxstyle="round,pad=0,rounding_size=0.6", fc=c, ec="none", zorder=18))


def keyplan(pg, x, y, h, key):
    """오른쪽 위 위치도 — 세 단면선, 현재 선 강조"""
    bx0, by0, bx1, by1 = B.bounds; s = h / (by1 - by0); w = (bx1 - bx0) * s
    def P(px, py): return x + (px - bx0) * s, y + (by1 - py) * s
    from matplotlib.path import Path as MP_
    for l in S["LOTS"]:
        for p in polys(l["g"]): pg.ax.add_patch(MPoly([P(*c) for c in p.exterior.coords], closed=True, fc=tint(LOTCOL[l["cat"]], 0.55), ec="white", lw=0.3, zorder=20))
    for g in S["ROADS"].values():
        for p in polys(g): pg.ax.add_patch(MPoly([P(*c) for c in p.exterior.coords], closed=True, fc="#636363", ec="none", zorder=20))
    pg.ax.add_patch(MPoly([P(*c) for c in B.exterior.coords], closed=True, fc="none", ec=RED, lw=0.6, ls=(0, (2, 1)), zorder=21))
    for k, (a, b) in ((k, SLJ[k]) for k in ("V", "H", "Dg")):
        A_, B_ = P(*a), P(*b)
        pg.line([A_[0], B_[0]], [A_[1], B_[1]], c=PURPLE if k == key else "#b9b9b9", lw=1.6 if k == key else 0.6, z=22)
        if k == key:
            t = SHEETS[k]["tag"]
            for q, lab in ((A_, t), (B_, t + "′")):
                pg.ax.add_patch(Circle(q, 2.4, fc=PURPLE, ec="white", lw=0.5, zorder=23)); pg.t(q[0], q[1] + 0.1, lab, fs=10, c="white", bold=True, ha="center", z=24)
    pg.t(x + w / 2, y + h + 4.0, "위치도", fs=10, c=GREY, ha="center", z=24)


def render(key):
    C = CUTS[key]; cfg = SHEETS[key]
    p0 = np.array(C["p0"]); u = np.array(C["u"]); L = C["L"]
    sB0, sB1 = C["inB"][0]
    MARG = 0.075 * (sB1 - sB0) + 14
    sA, sZ = sB0 - MARG, sB1 + MARG
    X0m, X1m = 14.0, 386.0
    hs = (X1m - X0m) / (sZ - sA); vs = 4.6; gy = 158.0
    def X(s): return X0m + (s - sA) * hs
    def Y(z): return gy - z * vs
    pg = Page()
    pg.header("Masterplan : Section Zoning", cfg["title_en"], cfg["title_ko"], sub=cfg["sub"] + " · 수직 %.1f배 과장" % (vs / hs))
    keyplan(pg, 372, 5.5, 50, key)
    # ── 주변 건물(구역 밖, 선 연장) ──
    ext = LineString([tuple(p0 - u * 200), tuple(p0 + u * (L + 200))])
    for o in CF:
        if o["inside"]: continue
        x = ext.intersection(o["g"])
        for seg in ([x] if x.geom_type == "LineString" else list(getattr(x, "geoms", []))):
            if seg.geom_type != "LineString" or seg.length < 0.5: continue
            ss = sorted(float(np.dot(np.array(c) - p0, u)) for c in seg.coords)
            a, b = max(ss[0], sA), min(ss[-1], sZ)
            if b - a < 0.5 or (a > sB0 and b < sB1): continue
            h = max(o["h"], 3.5)
            pg.rect(X(a), Y(h), (b - a) * hs, h * vs, fc="#f1f1ef", ec="#c9c9c5", lw=0.4, z=3)
    # ── 지면 ──
    grad = np.linspace(0, 1, 50)[:, None] * np.ones((1, 2))
    pg.ax.imshow(grad, extent=[X0m - 6, X1m + 6, gy + 10, gy], cmap=matplotlib.colors.LinearSegmentedColormap.from_list("g", ["#b8b8b5", "#6f6f6c"]), aspect="auto", zorder=2)
    pg.ax.set_xlim(0, PW); pg.ax.set_ylim(PH, 0)
    pg.line([X0m - 6, X1m + 6], [gy, gy], c="#2b2b2b", lw=1.0, z=8)
    GC = {"도로": "#636363", "공원": "#9fd67c", "보행": "#bfe39e", "보도": "#d8d8d4", "광장": "#e9e1cc", "중정": "#cfe9b4"}
    TREES = []
    for s0, s1, kind, nm in C["ground"]:
        if kind not in GC: continue
        a, b = max(s0, sA), min(s1, sZ)
        if b <= a: continue
        pg.rect(X(a), gy - 1.3, (b - a) * hs, 1.3, fc=GC[kind], ec="none", z=7)
        if kind in ("공원", "중정") or (kind == "보행" and "조망" not in nm):
            step = 9.0 if kind != "보행" else 8.0
            for s_ in np.arange(a + step / 2, b, step): TREES.append(s_)
        if kind == "광장" and "역전" in nm:
            for s_ in np.arange(a + 6, b, 9.0): TREES.append(s_)
    # 건물 영역과 겹치는 나무 제거
    bspans = [(r[0], r[1]) for r in C["bld"]]
    for s_ in TREES:
        if any(a - 2 < s_ < b + 2 for a, b in bspans): continue
        cx = X(s_); dia = min(max(6.0 * hs, 3.0), 6.5)
        pg.line([cx, cx], [gy - 1.3, gy - 3.6 * vs], c="#8b7355", lw=0.6, z=9)
        pg.ax.add_patch(Ellipse((cx, gy - 3.6 * vs - dia * 0.45), dia, dia * 1.05, fc="#86c25a", ec="#5f9a3e", lw=0.3, zorder=9))
    # ── 건축물(층별 용도) ──
    comm = set(cfg.get("comm_1f", []))
    names = {}
    for s0, s1, z0, z1, cat, nm, lot in C["bld"]:
        fh = FH.get(cat, 4.0); nf = max(1, int(round((z1 - z0) / fh))); fh_ = (z1 - z0) / nf
        for k in range(nf):
            za = z0 + k * fh_
            c = COMM if (nm in comm and za < 0.5) else LOTCOL[cat]
            pg.rect(X(s0), Y(za + fh_), (s1 - s0) * hs, fh_ * vs, fc=c, ec="white", lw=0.5, z=10)
        pg.rect(X(s0), Y(z1), (s1 - s0) * hs, (z1 - z0) * vs, fc="none", ec=shade(LOTCOL[cat], 0.55), lw=0.6, z=11)
        n_ = names.setdefault(nm, [1e9, -1e9, 0.0, cat]); n_[0] = min(n_[0], s0); n_[1] = max(n_[1], s1); n_[2] = max(n_[2], z1)
    # 구 역사 지붕(모임지붕, 경사 33°) — 처마 9 m
    if "구 경주역사" in names:
        stg = [b for b in BLD if b["name"] == "구 경주역사"][0]["g"].buffer(0.8, join_style=2)
        pts = []
        for s_ in np.arange(names["구 경주역사"][0] - 0.8, names["구 경주역사"][1] + 0.81, 0.4):
            q = Point(*(p0 + u * s_))
            if stg.contains(q): pts.append((X(s_), Y(9.0 + math.tan(math.radians(33)) * stg.boundary.distance(q))))
        if pts:
            poly = [(pts[0][0], Y(9.0))] + pts + [(pts[-1][0], Y(9.0))]
            pg.ax.add_patch(MPoly(poly, closed=True, fc="#6b5a52", ec="#4a3c35", lw=0.5, zorder=11))
            names["구 경주역사"][2] = max(names["구 경주역사"][2], (gy - min(p[1] for p in pts)) / vs)
    # 유리 지붕(그레이트 코트)
    if C["glass"]:
        gs = np.array(C["glass"])
        up = [(X(s), Y(z + 0.35)) for s, z in gs]; dn = [(X(s), Y(z - 0.35)) for s, z in gs[::-1]]
        pg.ax.add_patch(MPoly([(X(gs[0, 0]), Y(0)), *[(X(s), Y(z)) for s, z in gs], (X(gs[-1, 0]), Y(0))], closed=True, fc="#dcefF8", ec="none", alpha=0.35, zorder=5))
        pg.ax.add_patch(MPoly(up + dn, closed=True, fc="#9cc9df", ec="#5f8fa8", lw=0.5, alpha=0.9, zorder=12))
        for s_ in np.arange(gs[0, 0], gs[-1, 0], 3.0):
            z_ = np.interp(s_, gs[:, 0], gs[:, 1]); pg.line([X(s_), X(s_)], [Y(z_ - 0.35), Y(z_ + 0.35)], c="#5f8fa8", lw=0.4, z=13)
    # 브리지·캐노피
    for s0, s1, z0, z1, kind in C["links"]:
        pg.rect(X(s0), Y(z1), (s1 - s0) * hs, (z1 - z0) * vs, fc="#6b7076", ec="none", z=12)
    # ── 보행 동선(붉은 점선, 1층 높이) ──
    yr = Y(1.4)
    pg.ax.add_patch(FancyArrowPatch((X(sB0) + 1, yr), (X(sB1) - 1, yr), arrowstyle="<|-|>,head_length=2.4,head_width=1.4", color=ROUTE, lw=1.1, ls=(0, (3, 2)), zorder=16, mutation_scale=1.0))
    # 사람
    for s0, s1, kind, nm in C["ground"]:
        if kind in ("보행", "광장", "중정", "공원") and s1 - s0 > 12:
            m_ = (max(s0, sA) + min(s1, sZ)) / 2
            for d_ in ((-2.5, 2.0) if s1 - s0 > 25 else (0.0,)):
                person(pg.ax, X(m_) + d_, gy - 1.3)
    # ── 건물 라벨 ──
    placed = []
    def free(x, y, w, h):
        return all(x + w < a - 1 or a + c < x - 1 or y + h < b - 0.6 or b + d < y - 0.6 for a, b, c, d in placed)
    groups = {}
    for lab, nms, mode in cfg["bld"]:
        ss = [names[n] for n in nms if n in names]
        if not ss: print("  ! 단면에 없음", lab, nms); continue
        s0 = min(v[0] for v in ss); s1 = max(v[1] for v in ss); top = max(v[2] for v in ss); cat = ss[0][3]
        top = max([top] + [z1 for a, b, z0, z1, k in C["links"] if a < s1 and b > s0])   # 캐노피·브리지 위로
        ptops = [r[3] for r in C["bld"] if r[5] in nms and r[2] < 0.5]                  # 1층부터 올라간 부분의 지붕 높이
        low = min(ptops) if ptops else top
        groups[lab] = (s0, s1, top, cat)
        w = text_w(pg, lab, 10, True); x0, x1 = X(s0), X(s1)
        inner_h = top * vs
        if mode != "above" and x1 - x0 >= w + 3 and inner_h >= 9:
            c = "white" if lum(LOTCOL[cat]) < 150 else INK
            pg.t((x0 + x1) / 2, Y(low) + 4.4, lab, fs=10, bold=True, c=c, ha="center", z=15)
        else:
            y = Y(top) - 5.0
            x = (x0 + x1) / 2 - w / 2
            while not free(x, y - 3, w, 6): y -= 6.5
            placed.append((x, y - 3, w, 6))
            pg.t((x0 + x1) / 2, y, lab, fs=10, bold=True, c=INK, ha="center", z=15)
            if x1 - x0 > 6: pg.line([x0 + 0.5, x0 + 0.5, x1 - 0.5, x1 - 0.5], [Y(top) - 1.2, Y(top) - 2.2, Y(top) - 2.2, Y(top) - 1.2], c="#555", lw=0.5, z=15)
    if cfg.get("group"):
        gl, members = cfg["group"]
        ss = [groups[m] for m in members if m in groups]
        if ss:
            s0 = min(v[0] for v in ss); s1 = max(v[1] for v in ss); top = max(v[2] for v in ss)
            y = min(p[1] for p in placed if True) - 4.5 if placed else Y(top) - 12
            y = Y(top) - 15.5
            pg.line([X(s0), X(s0), X(s1), X(s1)], [y + 3.0, y + 1.6, y + 1.6, y + 3.0], c=INK, lw=0.6, z=15)
            pg.t((X(s0) + X(s1)) / 2, y - 1.6, gl, fs=10.5, bold=True, ha="center", z=15)
    # 1층 커뮤니티 표시(주거)
    if comm and "주거시설" in groups:
        s0, s1, top, cat = groups["주거시설"]
        pg.t((X(s0) + X(s1)) / 2, Y(top) - 11.0, "1층 커뮤니티 · 2~5층 주거", fs=10, c=GREY, ha="center", z=15)
    # ── 지면 라벨(↑ 화살표) ──
    gplaced = []
    for lab, gname in cfg["ground"]:
        segs = [(a, b) for a, b, kind, nm in C["ground"] if nm == gname and b > sA and a < sZ]
        if not segs: print("  ! 지면 없음", lab); continue
        a, b = max(segs, key=lambda t: t[1] - t[0]); m_ = X((max(a, sA) + min(b, sZ)) / 2)
        w = text_w(pg, lab, 10, True); row = 0
        while any(abs(m_ - q) < (w + ww) / 2 + 2 and r == row for q, ww, r in gplaced): row += 1
        gplaced.append((m_, w, row))
        ty = gy + 15.0 + row * 5.4
        pg.ax.add_patch(FancyArrowPatch((m_, ty - 3.0), (m_, gy + 0.6), arrowstyle="-|>,head_length=1.8,head_width=1.0", color="#333", lw=0.7, zorder=16, mutation_scale=1.0))
        pg.t(m_, ty, lab, fs=10, bold=True, c=INK, ha="center", z=16)
    # ── 양끝: 방향 화살표 + 단면 기호 ──
    t = cfg["tag"]
    for side in (0, 1):
        xe = X(sB0) if side == 0 else X(sB1)
        pg.line([xe, xe], [Y(17.5), gy + 9], c=PURPLE, lw=0.6, z=6, ls=(0, (3, 2)))
        pg.ax.add_patch(Circle((xe, Y(17.5) - 3.4), 3.4, fc=PURPLE, ec="white", lw=0.6, zorder=17))
        pg.t(xe, Y(17.5) - 3.3, t + ("" if side == 0 else "′"), fs=11, bold=True, c="white", ha="center", z=18)
        lx = X0m - 3 if side == 0 else X1m + 3
        pg.t(lx, gy + 5.0, cfg["ends"][side], fs=14, bold=True, c="white", ha="left" if side == 0 else "right", z=17)
        # 지면 위 방향 화살표(구역 밖으로)
        xa, xb = (X(sB0) - 2, X0m + 4) if side == 0 else (X(sB1) + 2, X1m - 4)
        pg.ax.add_patch(FancyArrowPatch((xa, Y(4.2)), (xb, Y(4.2)), arrowstyle="-|>,head_length=3.0,head_width=1.8", color=TEAL, lw=1.6, zorder=17, mutation_scale=1.0))
        pg.t((xa + xb) / 2, Y(4.2) - 3.6, cfg["end_txt"][side], fs=10, c=TEAL, bold=True, ha="center", z=17)
    # 높이 눈금
    for zz in (0, 10, 20):
        pg.line([3.0, 5.0], [Y(zz), Y(zz)], c="#777", lw=0.5, z=6)
    pg.line([3.0, 3.0], [Y(0), Y(20)], c="#777", lw=0.5, z=6)
    pg.t(3.0, Y(20) - 3.0, "20 m", fs=10, c=GREY, z=6)
    # ── 범례(하늘 영역 왼쪽) ──
    used = sorted({r[4] for r in C["bld"]}, key=lambda k: list(LOTCOL).index(k))
    items = [(LOTCOL[k], CATS[k][1] if not (comm and k == "판매") else "1층 커뮤니티·근린생활") for k in used]
    if comm and "판매" not in used: items.insert(0, (COMM, "1층 커뮤니티·근린생활"))
    if C["glass"]: items.append(("#9cc9df", "유리 지붕"))
    if C["links"]: items.append(("#6b7076", "브리지·캐노피"))
    items += [("#f1f1ef", "주변 건축물")]
    ex, ey = 12.0, 37.5
    for c, lab in items:
        w = text_w(pg, lab, 10)
        if ex + w + 9 > 350: ex = 12.0; ey += 5.4
        pg.rect(ex, ey - 1.6, 4.2, 3.2, fc=c, ec="#9a9a9a", lw=0.25, z=14); pg.t(ex + 5.4, ey, lab, fs=10, z=14); ex += 5.4 + w + 5.0
    pg.line([ex, ex + 7], [ey, ey], c=ROUTE, lw=1.1, z=14, ls=(0, (3, 2))); pg.t(ex + 8.5, ey, "보행 동선(1층 개방)", fs=10, z=14)
    # ── 하단 구역 띠(서대구역 레퍼런스 형식) ──
    bxs = cfg["boxes"]; n = len(bxs); gap = 2.0; bw = (X1m - X0m + 8 - gap * (n - 1)) / n; by = 190.0
    for i, (ttl, ck, desc) in enumerate(bxs):
        x = X0m - 4 + i * (bw + gap); c = BOXCOL[ck]
        pg.rect(x, by, bw, 7.4, fc=c, z=6)
        tc = "white" if lum(c) < 165 else INK
        tl = wrap_mm(pg, ttl, bw - 2, 10, True)
        pg.t(x + bw / 2, by + 3.7, tl[0], fs=10, bold=True, c=tc, ha="center", z=7)
        pg.rect(x, by + 7.4, bw, 219 - by - 7.4, fc="#F5F6F7", z=5)
        text_block(pg, x + 2.2, by + 12.4, desc, bw - 4.0, c=INK, z=7)
    pg.save(cfg["file"])


if __name__ == "__main__":
    ks = sys.argv[1:] or ["V", "H", "Dg"]
    if ks == ["all"]: ks = ["V", "H", "Dg"]
    for k in ks: render(k)
