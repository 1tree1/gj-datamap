"""G5a 프로그램 구성 조감(16:9) — D5 프로그램 구성도와 같은 내용(최종본 41동·층별 용도 색·용도별 연면적)을
v2 조감 시트(d3_sheet16.py, 여천역 형식) 구성으로: 색 박스 호출 6개 · 번호 마커 · 용지명 · 녹색 띠 이름 · 그레이트 코트 확대 · 하단 범례
입력: sheets/prog7a_axo.png(+_meta.pkl), sheets/prog7a_court.png — g5_program.render(ctx_flat=True)로 만든다(아래 render)
사용: python g5a_program_callout.py [render|sheet|all]"""
import os, sys, math, pickle
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
SH = os.path.join(HERE, "..", "sheets")


def render():
    import g5_program as G
    S = G.S
    o_, ua, vb = np.array(S["GLASS"]["o"]), np.array(S["GLASS"]["ua"]), np.array(S["GLASS"]["vb"])
    gc = o_ + 48.5 * ua + 10.0 * vb
    G.render(os.path.join(SH, "prog7a_axo.png"), ctx_flat=True, fill_w=0.80, cy=0.55)
    G.render(os.path.join(SH, "prog7a_court.png"), W=1640, H=1000, ctx_flat=True, focus=(gc[0], gc[1], 56.0, 8.0), fade=False)


def sheet():
    import gkit as K
    from gkit import Page, f0, halo, INK, GREY, PW, PH, Circle, Rectangle
    from shapely.ops import unary_union, polylabel
    from matplotlib.image import imread
    from d2_axo import Cam, polys
    import g5_program as G
    M = G.M; S = G.S; BLD = G.BLD; CATS = S["CATS"]
    meta = pickle.load(open(os.path.join(SH, "prog7a_axo_meta.pkl"), "rb"))
    cam = Cam(meta["az"], meta["el"], meta["W"], meta["H"], meta["ps"], meta["xc"], meta["yc"])
    def mm(x, y, z=0.0):
        px, py = cam.xy(x, y, z); return px * PW / meta["W"], py * PH / meta["H"]
    pg = Page()
    pg.ax.imshow(imread(os.path.join(SH, "prog7a_axo.png")), extent=[0, PW, PH, 0], aspect="auto", zorder=0, interpolation="bilinear")
    pg.ax.set_xlim(0, PW); pg.ax.set_ylim(PH, 0)
    byname = {}
    for b in BLD: byname.setdefault(b["name"], []).append(b)
    def bld_top(name, dz=3.0):
        b = max(byname[name], key=lambda b: b["g"].area); c = polylabel(max(polys(b["g"]), key=lambda g: g.area), 0.5)
        return mm(c.x, c.y, b["h"] + dz)
    y0b, y1b = S["DBAND"]; ym = (y0b + y1b) / 2
    o_, ua, vb = np.array(S["GLASS"]["o"]), np.array(S["GLASS"]["ua"]), np.array(S["GLASS"]["vb"])
    st = o_ + 48.5 * ua + (-30.0) * vb                                   # 역전광장(역사 정면 앞)
    COL = {1: "#3DA24B", 2: "#C2643A", 3: "#3A74C0", 4: "#C99A16", 5: "#EE7A2B", 6: "#8E6CC7"}
    MK = {1: mm(271.0, ym, 1.0), 2: mm(st[0], st[1], 2.0), 3: bld_top("공공청사 본관"), 4: bld_top("주거동 4"),
          5: mm(150.0, 95.0, 1.0), 6: bld_top("실내 체험관")}
    R = 3.1
    # ── 호출 내용(최종본 모델 수치: data/model.pkl — 층수 = 높이 ÷ 층고)
    glass_a = (S["GLASS"]["a1"] - S["GLASS"]["a0"]) * (S["GLASS"]["b1"] - S["GLASS"]["b0"])
    N = "\u00a0"                                                           # 줄바꿈 안 되는 공백(숫자–단위)
    CO = {
        4: ("정주 + 생활", "청년·신혼 주거 마을", ["청년·신혼 공공임대주택 판상 8동·5층", "1층 근린생활 연결동 4개, 생활체육관 4층", "북측 근린공원·체육공원과 접속"]),
        1: ("가로광장 + 선형공원", "동서 선형공원", ["폭 40%sm·연장 약 290%sm, 가로수 4열·중앙 가로광장" % (N, N), "남북 중앙 보행축(폭 30%sm)과 교차광장에서 만남" % N]),
        6: ("생활문화 + 창작", "공예·체험·레지던시 가구", ["복합문화센터 4층·건강·돌봄센터 3층", "공방·전시·공예마켓동 3층·실내 체험관 4층", "레지던시 제작동·거주동 각 3동, 브리지 연결"]),
        5: ("관문 + 모빌리티", "남측 관문·모빌리티 허브", ["관문광장에서 사선 보행축(폭 20%sm)으로 진입" % N, "공유주차장 5층·모빌리티 허브 4층", "관광지원센터·관문 가로상가 2층"]),
        3: ("공공 + 업무", "공공청사·청년창업 거점", ["공공청사 본관 7층·민원·시민홀동 5층, 청사 앞 시민광장", "직원 주차장동 5층(청사 연결 브리지)", "공공기관 업무동 5층·청년창업지원센터 4층"]),
        2: ("어댑티브 리유즈 + 유리 지붕 중정", "구 경주역 그레이트 코트", ["구 경주역사(2층·모임지붕) 존치, 정면 역전광장", "지역문화원 본동·소상공인 상생동 5층",
            "유리 지붕 중정 약 %s㎡, 근대역사관 4층" % f0(round(glass_a, -1))]),
    }
    placed = []
    def callout(k, x, y, w):
        sub, title, desc = CO[k]; c = COL[k]
        pg.t(x, y, sub, fs=10.5, c=c, bold=True, va="bottom", z=14)
        pg.rect(x, y + 1.2, w, 10.0, fc=c, z=13)
        pg.t(x + w / 2, y + 6.3, title, fs=14.5, c="white", bold=True, ha="center", z=14)
        ly = y + 15.6
        for d in desc:
            for ln in K.wrap_mm(pg, d, w):
                pg.t(x, ly, ln, fs=10, c="#555555", z=14, path_effects=halo(2.0)); ly += 4.6
        placed.append((x - 1, y - 5, w + 2, ly - y + 4))
        return ly - 2.4                                                  # 설명 아래 끝
    def lead(k, pts):
        c = COL[k]; xs, ys = zip(*pts); pg.line(list(xs), list(ys), c=c, lw=0.8, z=12)
        pg.ax.add_patch(Circle(pts[0], 0.6, fc=c, ec="none", zorder=12))
    # 위 4개(왼→오른)
    TW, GAPX, XL, XR = 88.0, 6.0, 12.0, 388.0
    ORD = (4, 1, 6, 5); TX = [MK[k][0] - TW / 2 for k in ORD]
    for i in range(len(TX)): TX[i] = max(TX[i], XL if i == 0 else TX[i - 1] + TW + GAPX)
    for i in reversed(range(len(TX))): TX[i] = min(TX[i], XR - TW if i == len(TX) - 1 else TX[i + 1] - TW - GAPX)
    print("top boxes", [round(v, 1) for v in TX], "markers", [round(MK[k][0], 1) for k in ORD])
    for k, x in zip(ORD, TX):
        yb = callout(k, x, 14.0, TW)
        mx, my = MK[k]
        if x <= mx <= x + TW: lead(k, [(mx, yb + 1.0), (mx, my - R)])
        else:
            xs_ = x + TW - 6 if mx > x + TW else x + 6
            ymid = yb + 6.0
            lead(k, [(xs_, yb + 1.0), (xs_, ymid), (mx, ymid), (mx, my - R)])
    # 아래 왼쪽 ③, 아래 오른쪽 ②(위에 그레이트 코트 확대)
    yb = callout(3, 12.0, 178.0, 96.0); mx, my = MK[3]; lead(3, [(108.0, 184.2), (mx, 184.2), (mx, my + R)])
    BX, BY, BW = 296.0, 186.0, 96.0
    yb = callout(2, BX, BY, BW); mx, my = MK[2]; lead(2, [(BX, BY + 6.2), (mx, BY + 6.2), (mx, my + R)])
    img = imread(os.path.join(SH, "prog7a_court.png")); IW = 76.0; IX = PW - 8.0 - IW; ih = IW * img.shape[0] / img.shape[1]
    iy = BY - 9.5 - ih
    pg.rect(IX - 1.0, iy - 1.0, IW + 2.0, ih + 2.0, fc="white", ec="#c9c9c9", lw=0.6, z=13)
    pg.ax.imshow(img, extent=[IX, IX + IW, iy + ih, iy], aspect="auto", zorder=14, interpolation="bilinear"); pg.ax.set_xlim(0, PW); pg.ax.set_ylim(PH, 0)
    pg.t(IX + IW, iy - 3.4, "그레이트 코트 확대", fs=10, c=GREY, ha="right", z=14, path_effects=halo(2.0))
    print("inset y %.1f–%.1f" % (iy, iy + ih))
    placed.append((IX - 2, iy - 6, IW + 4, ih + 7))
    # ── 번호 마커
    for k, (x, y) in MK.items():
        pg.ax.add_patch(Circle((x, y), R, fc=COL[k], ec="white", lw=1.1, zorder=15)); pg.t(x, y + 0.15, str(k), fs=10, c="white", bold=True, ha="center", z=16)
        placed.append((x - R - 1, y - R - 1, 2 * R + 2, 2 * R + 2))
    # ── 녹색 띠 이름(띠 방향으로 회전)
    def band_text(p0, p1, s, fs, at=0.5):
        a = mm(*p0, 0.0); b = mm(*p1, 0.0)
        ang = -math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        x = a[0] + (b[0] - a[0]) * at; y = a[1] + (b[1] - a[1]) * at
        pg.t(x, y, s, fs=fs, c="#2f8f3a", ha="center", bold=True, rotation=ang, rotation_mode="anchor", style="italic", path_effects=halo(2.6), z=13)
    band_text((-80, ym), (60, ym), "동서 선형공원 · 가로광장", 13.5)
    band_text((470, ym), (600, ym), "도시로 이어지는 녹색 띠", 10.5)
    # ── 용지명(획지 위 빈 땅, 흰 테두리 글씨) — 호출·마커·확대도와 겹치면 생략
    BU = unary_union([b["g"] for b in BLD])
    def free(x, y, w, h):
        for q in placed:
            if not (x + w < q[0] or q[0] + q[2] < x or y + h < q[1] or q[1] + q[3] < y): return False
        return True
    for l in M["LOTS"]:
        if l["no"] == 9: continue                                         # ② 호출이 설명
        fr = l["g"].difference(BU.buffer(3.0))
        fp = max(polys(fr), key=lambda g: g.area) if not fr.is_empty else l["g"]
        pt = polylabel(fp, 1.0) if fp.area > 60 else l["g"].representative_point()
        x, y = mm(pt.x, pt.y, 0.5); w = K.text_w(pg, l["use"], 10) + 1.0
        if not free(x - w / 2, y - 2.2, w, 4.4): print("  skip", l["use"]); continue
        pg.t(x, y, l["use"], fs=10, c="#3a3a3a", ha="center", path_effects=halo(2.0), z=12); placed.append((x - w / 2, y - 2.2, w, 4.4))
    for p in S["PARKS"]:
        pt = polylabel(max(polys(p["g"]), key=lambda g: g.area), 1.0); x, y = mm(pt.x, pt.y, 0.5)
        w = K.text_w(pg, "근린공원", 10) + 1.0
        if free(x - w / 2, y - 2.2, w, 4.4): pg.t(x, y, "근린공원", fs=10, c="#2e6b2a", ha="center", path_effects=halo(2.0), z=12); placed.append((x - w / 2, y - 2.2, w, 4.4))
    # ── 범례(하단 띠) — 용도 색 + 지상 연면적 비율, 브리지·캐노피, 유리 지붕, 합계
    tot = {}
    for b in BLD:
        for k, v in b["gfa_by"].items(): tot[k] = tot.get(k, 0) + v
    T_ = sum(tot.values())
    ly = 219.5
    pg.rect(0, ly - 3.8, PW, 7.6, fc="white", alpha=0.92, z=13)
    SHORT = {"공공업무": "공공업무", "업무·창업": "업무·창업", "문화": "문화·집회", "창작": "창작·공방", "판매": "근린생활", "생활SOC": "체육·복지", "주거": "주거",
             "역사": "역사유산", "방문자": "관광", "주차": "주차·교통"}
    ex = 6.0
    for k in ["공공업무", "업무·창업", "문화", "창작", "판매", "생활SOC", "주거", "역사", "방문자", "주차"]:
        pg.rect(ex, ly - 1.7, 3.4, 3.4, fc=G.PCOL[k], ec="#9a9a9a", lw=0.25, z=14)
        t_ = pg.t(ex + 4.3, ly, SHORT[k], fs=10, z=14); ex += 4.3 + pg.wmm(t_) + 0.5
        t_ = pg.t(ex, ly, "%.1f%%" % (tot.get(k, 0) / T_ * 100), fs=10, c=GREY, z=14); ex += pg.wmm(t_) + 1.9
    pg.rect(ex, ly - 1.7, 3.4, 3.4, fc="#6b7076", z=14); t_ = pg.t(ex + 4.3, ly, "브리지·캐노피", fs=10, z=14); ex += 4.3 + pg.wmm(t_) + 1.9
    pg.rect(ex, ly - 1.7, 3.4, 3.4, fc="#cfe6f3", ec="#7d98ab", lw=0.4, z=14); t_ = pg.t(ex + 4.3, ly, "유리 지붕", fs=10, z=14); ex += 4.3 + pg.wmm(t_) + 1.9
    t_ = pg.t(PW - 8, ly, "지상 연면적 %s㎡ · %d동" % (f0(T_), len(BLD)), fs=10, bold=True, ha="right", z=14)
    print("legend end %.1f mm, total starts %.1f mm" % (ex, PW - 8 - pg.wmm(t_)))
    pg.save("D5a_프로그램구성조감")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("render", "all"): render()
    if mode in ("sheet", "all"): sheet()
