"""G3m 도로·보행 계획도 + 도로계획표(16:9) — D2a 도로계획 구상도와 D3 도로·보행 계획도를 한 장으로 합침(사용자 요청 2026-10-12)
- 평면: D2a 위계 색(차량 회색 · 보행 1~3등) + D3 주차(P)·모빌리티 허브(M)·보행 진입 + 사용자 지정 차량 진입 7곳(빨간 삼각형)
- 표: 가로 8개 — 성격·연결 대상·위계(D2a) + 폭·연장·면적·단면(D3), 구분 소계·합계, 가구 면적
- 차량 진입 7곳: 사용자 캡처(라이노 도로 객체 + 빨간 삼각형)의 픽셀 위치를 로컬 좌표로 옮긴 뒤 진입 획지 경계에 맞춤
  픽셀 → 로컬: x = −38.5 + 1.467·px, y = 1035.4 − 1.467·py (동서 도로 띠·선형공원 띠·남북 보행축·북측 차도 꺾임점 4곳으로 맞춤, 오차 수 m)"""
from gkit import *
from matplotlib.patches import FancyArrowPatch, Circle, Polygon as MPoly
from shapely.ops import polylabel, nearest_points

DS = pickle.load(open(os.path.join(D, "district.pkl"), "rb"))
OP = {o["key"]: o for o in S["OPEN"]}
R = S["ROADS"]
RG = unary_union(list(R.values()))
PED = unary_union([o["g"] for o in S["OPEN"]] + [S["PATH8"], S["WALK"]])
BLK = [g for g in polys(B.difference(RG).difference(PED)) if g.area > 200]
LOT = {l["no"]: l for l in S["LOTS"]}
GREEN = "#2f8f3a"; BLUE = "#1f6fbf"; LBLUE = "#7fa6d8"; PURP = "#7a5ab5"; CARC = "#636363"; ENTRY = "#D62828"


def length_of(g):
    """띠 모양 연장 = 면적 ÷ 평균폭(4 × 면 안 점에서 외곽선까지 평균 거리) — g3_roads와 같은 방식"""
    from scipy import ndimage
    import shapely
    x0, y0, x1, y1 = g.bounds; st = 0.5
    X, Y = np.meshgrid(np.arange(x0, x1, st) + st / 2, np.arange(y0, y1, st) + st / 2)
    m = np.pad(shapely.contains_xy(g, X.ravel(), Y.ravel()).reshape(X.shape), 3)
    d = ndimage.distance_transform_edt(m) * st
    return g.area / (4.0 * d[m].mean())


# ── 차량 진입 7곳(사용자 지정) — (픽셀 x, y, 진입 방향, 획지, 진입 도로)
vd = np.array([353.5 - 254.0, 892.2 - 778.5]); vd /= np.linalg.norm(vd)
ENT = [(209.5, 150.0, (-vd[1], vd[0]), 2, "북측 차도(사선 구간)"),
       (300.0, 188.6, (-1, 0), 4, "동측 외곽도로"),
       (95.7, 278.5, (1, 0), 5, "서측 원화로"),
       (300.0, 283.6, (-1, 0), 6, "동측 외곽도로"),
       (293.5, 420.4, (-1, 0), 8, "동측 외곽도로"),
       (170.5, 465.3, (0, 1), 7, "동서 도로"),
       (276.4, 476.1, (0, -1), 13, "동서 도로")]
ENTRIES = []
for px, py, d, no, road in ENT:
    p = np.array([-38.5 + 1.467 * px, 1035.4 - 1.467 * py]); d = np.array(d, float); d /= np.linalg.norm(d)
    ray = LineString([tuple(p - d * 40), tuple(p + d * 60)])
    hit = ray.intersection(LOT[no]["g"].boundary)
    pts_ = [np.array(q.coords[0]) for q in (getattr(hit, "geoms", [hit]))] if not hit.is_empty else [np.array(nearest_points(LOT[no]["g"].boundary, Point(*p))[0].coords[0])]
    q = min(pts_, key=lambda v: np.dot(v - (p - d * 40), d))           # 광선이 획지에 처음 닿는 점
    ENTRIES.append(dict(p=q - d * 5.0, d=d, no=no, road=road, lot=LOT[no]["name"]))

pg = Page()
pg.header("Masterplan : Street Network", "Street Plan + Road Schedule", "도로·보행 계획도 + 도로계획표",
          sub="차량은 외곽 도로와 동서 도로에, 가구 진입은 지정한 7곳으로 — 대지 안쪽은 세 축을 따른 보행 가로, 형상은 사용자 확정 객체 그대로")
EXT = (-150, 640, 18, 1040)
ax = pg.plan_ax(4, 30, 150, 192, EXT)
(ex0, ex1), (ey0, ey1) = ax.get_xlim(), ax.get_ylim()
win = box(ex0, ey0, ex1, ey1)
fill(ax, win, fc="#f7f7f5", z=0.1)
from matplotlib.collections import PatchCollection
ax.add_collection(PatchCollection([PathPatch(path_of(q)) for g, c in DS["PAR"] if g.intersects(win) for q in polys(g)], fc="none", ec="#e2e2de", lw=0.18, zorder=0.3))
for g, c in DS["PAR"]:
    if c == "천" and g.intersects(win): fill(ax, g, fc="#d6e7f2", z=0.35)
context(ax, (ex0, ex1, ey0, ey1), fc="#e2e2df", ec="none", z=0.5)
for nm, gs in DS["ROADS"].items():
    for g in gs:
        if g.intersects(win):
            xs, ys = g.xy; ax.plot(xs, ys, color="#bdbdb8", lw=3.2, zorder=0.6, solid_capstyle="round"); ax.plot(xs, ys, color="white", lw=2.3, zorder=0.61, solid_capstyle="round")
for g in DS["AXES"].get("화랑로", []):
    x0_, y0_, x1_, y1_ = g.bounds
    if g.intersects(win) and (y1_ - y0_) < 0.3 * max(x1_ - x0_, 1):
        xs, ys = g.xy; ax.plot(xs, ys, color="#bdbdb8", lw=3.2, zorder=0.6); ax.plot(xs, ys, color="white", lw=2.3, zorder=0.61)
# 가구·보도
for i, g in enumerate(sorted(BLK, key=lambda g: (-g.centroid.y, g.centroid.x))):
    fill(ax, g, fc="#ececea", ec="#c9c9c5", lw=0.4, z=1)
    p = polylabel(g, 1.0); ax.text(p.x, p.y + (18 if i in (2, 4) else 0), "가구 %d" % (i + 1), fontsize=10, color="#8a8a86", ha="center", va="center", zorder=1.5)
fill(ax, S["WALK"], fc="#dcdcd8", z=1.1)
# 보행 가로(위계 색)
fill(ax, S["PATH8"], fc=PURP, alpha=0.85, z=1.25)
YP8 = (635.2 + 643.2) / 2
ax.add_patch(FancyArrowPatch((103, YP8), (-135, YP8 + 4), arrowstyle="-|>,head_length=5,head_width=3", color=PURP, lw=1.3, ls=(0, (2, 1.6)), zorder=8, mutation_scale=1.0))
ax.text(-140, YP8 + 22, "경주읍성 향일문", fontsize=10, color=PURP, fontweight="bold", ha="left", path_effects=halo(1.6), zorder=14)
fill(ax, OP["D"]["g"], fc=GREEN, alpha=0.85, z=1.3)
fill(ax, OP["E"]["g"], fc=BLUE, alpha=0.70, z=1.3)
fill(ax, OP["F"]["g"], fc=BLUE, alpha=0.45, z=1.3, hatch="////", ec="white", lw=0.0)
for g in R.values(): fill(ax, g, fc=CARC, z=1.6)
xs, ys = B.exterior.xy; ax.plot(xs, ys, color=RED, lw=0.9, ls=(0, (4, 2)), zorder=6)
# 보행 진입(D3) — 선형공원 양끝·관문광장
for p_, q_ in (((30, 496), (102, 496)), ((480, 496), (408, 496)), ((60, 8), (108, 56))):
    ax.add_patch(FancyArrowPatch(p_, q_, arrowstyle="-|>,head_length=4,head_width=2.6", color=GREEN, lw=1.3, ls=(0, (3, 1.6)), zorder=8, mutation_scale=1.0))
# 주차(P)·모빌리티 허브(M) — D3와 같은 자리
for x, y in ((238, 832), (365, 290), (145, 621)):
    ax.add_patch(Rectangle((x - 10, y - 10), 20, 20, fc="#2F5F9E", ec="white", lw=0.6, zorder=15)); ax.text(x, y, "P", fontsize=10, color="white", ha="center", va="center", fontweight="bold", zorder=16)
ax.add_patch(Circle((353, 221), 12, fc="#F0A030", ec="white", lw=0.6, zorder=15)); ax.text(353, 221, "M", fontsize=10, color="white", ha="center", va="center", fontweight="bold", zorder=16)
# 차량 진입 7곳(빨간 삼각형 + 번호)
for i, e in enumerate(ENTRIES):
    c = e["p"]; d = e["d"]; n_ = np.array([-d[1], d[0]]); L_ = 15.0
    tri = [tuple(c + d * L_ * 0.62), tuple(c - d * L_ * 0.38 + n_ * L_ * 0.5), tuple(c - d * L_ * 0.38 - n_ * L_ * 0.5)]
    ax.add_patch(MPoly(tri, closed=True, fc=ENTRY, ec="white", lw=0.6, zorder=17))
    tp = c - d * 20.0 + n_ * (0 if abs(d[1]) < 0.5 else 0)
    if abs(d[0]) > 0.9: tp = c - d * 22.0 + np.array([0, -14.0])
    else: tp = c - d * 4.0 + np.array([16.0, 0])
    ax.text(tp[0], tp[1], str(i + 1), fontsize=10, color=ENTRY, fontweight="bold", ha="center", va="center", path_effects=halo(2.2), zorder=18)
# 위계 번호·이름
def badge(x, y, s, c, r=15):
    ax.add_patch(Circle((x, y), r, fc=c, ec="white", lw=0.8, zorder=12)); ax.text(x, y, s, fontsize=10, color="white", fontweight="bold", ha="center", va="center", zorder=13)
y0b, y1b = S["DBAND"]; ym = (y0b + y1b) / 2
badge(180, ym, "②", GREEN); badge(271, 560, "①", BLUE); badge(150, 120, "③", BLUE); badge(185, 639.2, "④", PURP)
def lab(x, y, s, c, rot=0, ha="center", stroke=None):
    t_ = ax.text(x, y, s, fontsize=10, color=c, fontweight="bold", rotation=rot, ha=ha, va="center", zorder=14, rotation_mode="anchor")
    t_.set_path_effects([pe.withStroke(linewidth=2.0, foreground=stroke)] if stroke else halo(2.2))
lab(345, ym, "선형공원 40 m", "white", stroke=GREEN)
lab(271, 720, "남북 보행축 30 m", "white", rot=90, stroke=BLUE)
lab(222, 175, "사선 보행축 20 m", BLUE, rot=57.4)
lab(345, 655, "조망로 8 m", PURP)
lab(170, 321, "동서 도로 20 m", CARC); lab(165, 798, "북측 차도 13 m", CARC)
lab(441, 612, "동·남측 외곽도로", CARC, rot=-90)
for t_, x_, y_, r_ in (("원화로", 70, 560, 90), ("화랑로", -75, 362, 0), ("알천남로", 500, 900, 40)):
    ax.text(x_, y_, t_, fontsize=10, color="#7d7d78", fontweight="bold", rotation=r_, ha="center", va="center", path_effects=halo(2.0), zorder=14)
north_scale(ax, 470, 45, label_m=(0, 50, 100), fs=9, north_at=(600, 130))

pg.top()
# ── 우측: 도로계획표(위계 + 단면) ──
tx = 160
cols = ["", "가로", "성격", "연결 대상", "위계", "폭", "연장", "면적㎡", "단면(m, 도면 기준)"]
wd = [3, 33, 29, 46, 15, 11, 12, 17, 66]
xs_ = [tx]
for w in wd: xs_.append(xs_[-1] + w)
TWD = sum(wd)
ty = 33
pg.rect(tx, ty, TWD, 6.4, fc="#2b2b2b", z=5)
for i, c in enumerate(cols): pg.t(xs_[i] + wd[i] / 2, ty + 3.2, c, fs=10, c="white", ha="center", bold=True, z=6)
NET = [  # 구분, 가로, 성격, 연결 대상, 위계, 폭, geom, 색, 단면
    ("차량", "북측 차도", "진입 차도", "원화로 ↔ 알천남로(북천변), 청사 주차장동 진입", "차량", "13", R["N"], CARC, [("보도", 5, "#d9d9d6"), ("차도", 13, "#636363"), ("보도", 5, "#d9d9d6")]),
    ("차량", "동서 도로", "화랑로 연결 횡단", "화랑로(원화로 교차) ↔ 동측 생활가로", "차량", "20", R["EW"], CARC, [("보도", 5, "#d9d9d6"), ("차도", 20, "#636363"), ("보도", 5, "#d9d9d6")]),
    ("차량", "동·남측 외곽도로", "외곽 순환·서비스", "동·남측 생활가로, 공유주차장·모빌리티 허브", "차량", "10~12", R["O"], CARC, [("보도", 8, "#d9d9d6"), ("차도", 10, "#636363")]),
    ("보행", "동서 선형공원", "보행자전용(선형공원)", "성동시장 ↔ 성동리 전랑지", "② 1등", "40", OP["D"]["g"], GREEN, [("식재", 12, "#9fd67c"), ("광장", 16, "#efe8d6"), ("식재", 12, "#9fd67c")]),
    ("보행", "남북 중앙 보행축", "보행자전용", "대릉원 ↔ 북천·황성공원", "① 2등", "30", OP["E"]["g"], BLUE, [("식재", 7, "#9fd67c"), ("보행", 16, "#efe8d6"), ("식재", 7, "#9fd67c")]),
    ("보행", "관문광장·사선 보행축", "보행자전용·광장", "관문광장 · 황리단길·대릉원", "③ 2등", "20", OP["F"]["g"], LBLUE, [("식재", 6, "#9fd67c"), ("보행", 8, "#efe8d6"), ("식재", 6, "#9fd67c")]),
    ("보행", "향일문 조망로", "보행자전용(조망)", "경주읍성 향일문(약 310 m)", "④ 3등", "8", S["PATH8"], PURP, [("보행", 8, "#efe8d6")]),
    ("보도", "외곽 보도", "보도", "구역 외곽·가구 둘레", "-", "가변", S["WALK"], "#BDBDBD", [("보도", 5, "#d9d9d6")]),
]
RH = 10.0; yy = ty + 6.4
sums = {"차량": 0.0, "보행": 0.0, "보도": 0.0}
def cell(i, txt, y_, bold=False, color=INK, ha="left"):
    L = wrap_mm(pg, txt, wd[i] - 2.0)
    for j, ln in enumerate(L[:2]):
        x_ = xs_[i] + 1.0 if ha == "left" else xs_[i + 1] - 1.0
        pg.t(x_, y_ + RH / 2 + (j - (min(len(L), 2) - 1) / 2) * 4.4, ln, fs=10, z=6, c=color, bold=bold, ha=ha)
for grp in ("차량", "보행", "보도"):
    for kind, nm, ch, conn, rank, w, g, c, sec in [n for n in NET if n[0] == grp]:
        A_ = g.area; sums[kind] += A_
        pg.rect(tx, yy, TWD, RH, fc="white", z=5); pg.line([tx, tx + TWD], [yy + RH, yy + RH], c="#dedede", lw=0.4, z=6)
        pg.rect(xs_[0] + 0.4, yy + 1.2, 1.8, RH - 2.4, fc=c, z=6)
        cell(1, nm, yy, bold=True); cell(2, ch, yy); cell(3, conn, yy)
        pg.t(xs_[4] + 1.0, yy + RH / 2, rank, fs=10, bold=True, c=(c if kind == "보행" else INK), z=6)
        pg.t(xs_[6] - 1.0, yy + RH / 2, w, fs=10, ha="right", z=6)
        pg.t(xs_[7] - 1.0, yy + RH / 2, f0(length_of(g)) if kind != "보도" else "-", fs=10, ha="right", z=6)
        pg.t(xs_[8] - 1.0, yy + RH / 2, f0(A_), fs=10, ha="right", z=6)
        tw_ = sum(s_[1] for s_ in sec); bx = xs_[8] + 1.5; bw = wd[8] - 3.0; sc = bw / 44.0
        cx_ = bx + (bw - tw_ * sc) / 2
        for lab_, sw, scol in sec:
            pg.rect(cx_, yy + 2.0, sw * sc, RH - 4.0, fc=scol, ec="white", lw=0.5, z=6)
            pg.t(cx_ + sw * sc / 2, yy + RH / 2, ("%s %g" % (lab_, sw)) if sw * sc > 15 else "%g" % sw, fs=10, ha="center", z=7, c="white" if scol == "#636363" else INK)
            cx_ += sw * sc
        yy += RH
    pg.rect(tx, yy, TWD, 6.0, fc="#ebebe8", z=5)
    pg.t(xs_[1] + 1.0, yy + 3.0, {"차량": "차량 도로 소계", "보행": "보행자전용도로·광장 소계", "보도": "보도 소계"}[grp], fs=10, bold=True, z=6)
    pg.t(xs_[8] - 1.0, yy + 3.0, f0(sums[grp]), fs=10, bold=True, ha="right", z=6)
    pg.t(xs_[8] + 1.5, yy + 3.0, "구역의 %.1f%%" % (sums[grp] / TOT["boundary"] * 100), fs=10, c=GREY, z=6)
    yy += 6.0
tot = sum(sums.values())
pg.rect(tx, yy, TWD, 6.4, fc="#d9d9d5", z=5)
pg.t(xs_[1] + 1.0, yy + 3.2, "도로·보행 합계", fs=10, bold=True, z=6); pg.t(xs_[8] - 1.0, yy + 3.2, f0(tot), fs=10, bold=True, ha="right", z=6)
pg.t(xs_[8] + 1.5, yy + 3.2, "구역의 %.1f%%" % (tot / TOT["boundary"] * 100), fs=10, c=GREY, z=6)
yy += 6.4
pg.line([tx, tx + TWD], [yy, yy], c="#2b2b2b", lw=0.8, z=7)
BA = sum(g.area for g in BLK)
yy += 4.0
pg.t(tx, yy, "가구 %d개 %s㎡ · 구역의 %.1f%%(건축·오픈스페이스) · 연장은 면적 ÷ 평균폭 근사 · 폭은 도면에서 읽은 값" % (len(BLK), f0(BA), BA / TOT["boundary"] * 100), fs=10, c=GREY, z=6)
# ── 원칙 박스 3 ──
yy += 5.0
pk = sum(b["gfa"] for b in BLD if b["main"] == "주차" and "허브" not in b["name"])
BOX = [("차량은 외곽과 횡단에서", "차량 도로는 북측 차도·동서 도로·동·남측 외곽도로에만 둡니다. 가구 진입은 지정한 7곳(▲)으로 한정합니다.", CARC),
       ("보행은 대지 축을 따라", "선형공원(40 m)·남북 보행축(30 m)·사선 보행축(20 m)이 교차광장·관문광장에서 만납니다. 위계는 연결 대상의 크기 순.", GREEN),
       ("주차는 건축물로 집약", "주차전용건축물 %s㎡(약 %s대, 32㎡/대 가정)로 지상 주차를 줄입니다." % (f0(pk), f0(round(pk / 32, -1))), "#2F5F9E")]
bw_ = (TWD - 8) / 3; bh = 11.5 + max(block_h(pg, d_, bw_ - 7) for t, d_, c in BOX) + 2.5
for i, (t, d_, c) in enumerate(BOX):
    bx = tx + i * (bw_ + 4)
    pg.rect(bx, yy, bw_, bh, fc="#F3F5F8", z=5); pg.rect(bx, yy, 1.4, bh, fc=c, z=6)
    pg.t(bx + 4, yy + 5.0, t, fs=10, bold=True, c=c if c != CARC else INK, z=6)
    text_block(pg, bx + 4, yy + 10.8, d_, bw_ - 7, c=INK, z=6)
yy += bh + 6.0
# ── 차량 진입 7곳 ──
pg.ax.add_patch(MPoly([(tx, yy + 1.6), (tx + 3.2, yy + 1.6), (tx + 1.6, yy - 1.4)], closed=True, fc=ENTRY, zorder=6))
pg.t(tx + 5.0, yy, "차량 진입 7곳 — 진입 도로 → 진입 획지", fs=10, bold=True, z=6)
for i, e in enumerate(ENTRIES):
    c_, r_ = divmod(i, 4)
    x_ = tx + c_ * 118; y_ = yy + 6.2 + r_ * 5.0
    pg.t(x_, y_, str(i + 1), fs=10, bold=True, c=ENTRY, z=6)
    pg.t(x_ + 4.0, y_, "%s → %d %s" % (e["road"], e["no"], e["lot"]), fs=10, c=INK, z=6)
# ── 범례(지도 왼쪽 아래) ──
lx, ly0 = 6, 150
LG = [(CARC, 1.0, "차량 가로"), (GREEN, 0.85, "보행 가로 1등"), (BLUE, 0.7, "보행 가로 2등"), (PURP, 0.55, "보행 가로 3등"), ("#d5d5d1", 1.0, "외곽 보도"), ("#ececea", 1.0, "가구")]
EXTRA = ["entry", "walk", "P", "M", "bound"]
pg.rect(lx, ly0, 42, 4 + (len(LG) + len(EXTRA)) * 5.4, fc="white", ec="#cccccc", lw=0.4, z=30, alpha=0.95)
for i, (c, a, t) in enumerate(LG):
    y_ = ly0 + 4.6 + i * 5.4
    pg.rect(lx + 2.5, y_ - 1.5, 7, 3.0, fc=c, alpha=a, ec="#bbbbbb", lw=0.2, z=31); pg.t(lx + 12, y_, t, fs=10, z=31)
y_ = ly0 + 4.6 + len(LG) * 5.4
pg.ax.add_patch(MPoly([(lx + 4.2, y_ + 1.5), (lx + 7.8, y_ + 1.5), (lx + 6.0, y_ - 1.7)], closed=True, fc=ENTRY, zorder=31)); pg.t(lx + 12, y_, "차량 진입(가구)", fs=10, z=31); y_ += 5.4
pg.ax.add_patch(FancyArrowPatch((lx + 2.5, y_), (lx + 9.5, y_), arrowstyle="-|>,head_length=1.6,head_width=1.0", color=GREEN, lw=0.9, ls=(0, (2, 1.2)), zorder=31, mutation_scale=1.0)); pg.t(lx + 12, y_, "보행 진입", fs=10, z=31); y_ += 5.4
pg.rect(lx + 4.4, y_ - 1.6, 3.2, 3.2, fc="#2F5F9E", z=31); pg.t(lx + 12, y_, "주차", fs=10, z=31); y_ += 5.4
pg.ax.add_patch(Circle((lx + 6.0, y_), 1.7, fc="#F0A030", zorder=31)); pg.t(lx + 12, y_, "모빌리티 허브", fs=10, z=31); y_ += 5.4
pg.line([lx + 2.5, lx + 9.5], [y_, y_], c=RED, lw=0.8, z=31, ls=(0, (3, 1.5))); pg.t(lx + 12, y_, "구역 경계", fs=10, z=31)
pg.save("D3_도로보행계획도")
for e in ENTRIES: print("entry", [round(v, 1) for v in e["p"]], e["road"], "→", e["no"], e["lot"])
