"""G2a 도로계획 구상도(16:9) — 차량 가로와 보행 가로의 역할 분담, 위계(1~3등), 축 → 가로, 실제 접속점
차량 가로·보행공간은 사용자 확정 객체(road_sel.json) 그대로. 접속점 = 실제 도로 필지('도', V-World 연속지적)가 계획 도로와 맞닿는 곳 + 북동 알천남로 접속"""
from gkit import *
from matplotlib.patches import FancyArrowPatch, Circle
from shapely.ops import polylabel
import textwrap

DS = pickle.load(open(os.path.join(D, "district.pkl"), "rb"))
RS = json.load(open(os.path.join(D, "road_sel.json"), encoding="utf-8"))
ACC = pickle.load(open(os.path.join(D, "access_pts.pkl"), "rb"))
OP = {o["key"]: o for o in S["OPEN"]}
RG = unary_union(list(S["ROADS"].values()))
PED = unary_union([o["g"] for o in S["OPEN"]] + [S["PATH8"], S["WALK"]])
BLK = [g for g in polys(B.difference(RG).difference(PED)) if g.area > 200]
# 사용자 북측 보도 객체(향일문 조망로 구간) — road_sel 의 보도 Brep 중 북측(y > 784)
NW = None
for o in RS["objs"]:
    if "loops" in o and o["layer"].endswith("::보도"):
        outer = [Polygon([(x - X0 - 1080.496306963265, y - Y0) for x, y, z in pts]).buffer(0) for lt, pts in o["loops"] if "Outer" in lt]
        inner = [Polygon([(x - X0 - 1080.496306963265, y - Y0) for x, y, z in pts]).buffer(0) for lt, pts in o["loops"] if "Inner" in lt]
        g = unary_union(outer).difference(unary_union(inner)) if inner else unary_union(outer)
        if g.bounds[1] > 780: NW = g
A_N = NW.area if NW is not None else 0.0

pg = Page()
pg.header("Masterplan : Street Concept", "Street Hierarchy", "도로계획 구상도",
          sub="차량은 외곽 순환 가로와 화랑로 연결 횡단 한 곳에 두고, 대지 안쪽은 세 축을 따른 보행 가로로 채운 구성 — 가로 형상은 사용자 확정 객체 그대로")
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
# 가구(9) · 보조 보행
for i, g in enumerate(sorted(BLK, key=lambda g: (-g.centroid.y, g.centroid.x))):
    fill(ax, g, fc="#ececea", ec="#c9c9c5", lw=0.4, z=1)
    p = polylabel(g, 1.0); ax.text(p.x, p.y + (18 if i in (2, 4) else 0), "가구 %d" % (i + 1), fontsize=10, color="#8a8a86", ha="center", va="center", zorder=1.5)
fill(ax, S["WALK"], fc="#dcdcd8", z=1.1)
# 보행 가로(위계 색)
GREEN = "#2f8f3a"; BLUE = "#1f6fbf"; PURP = "#7a5ab5"
fill(ax, S["PATH8"], fc=PURP, alpha=0.85, z=1.25)                          # 향일문 조망로 = 가구 사이 보행자전용도로(폭 8 m)
YP8 = (635.2 + 643.2) / 2
ax.add_patch(FancyArrowPatch((103, YP8), (-135, YP8 + 4), arrowstyle="-|>,head_length=5,head_width=3", color=PURP, lw=1.3, ls=(0, (2, 1.6)), zorder=8, mutation_scale=1.0))
ax.text(-140, YP8 + 22, "경주읍성 향일문", fontsize=10, color=PURP, fontweight="bold", ha="left", path_effects=halo(1.6), zorder=14)
fill(ax, OP["D"]["g"], fc=GREEN, alpha=0.85, z=1.3)
fill(ax, OP["E"]["g"], fc=BLUE, alpha=0.70, z=1.3)
fill(ax, OP["F"]["g"], fc=BLUE, alpha=0.45, z=1.3, hatch="////", ec="white", lw=0.0)
# 차량 가로(검정)
for g in S["ROADS"].values(): fill(ax, g, fc="#636363", z=1.6)
xs, ys = B.exterior.xy; ax.plot(xs, ys, color=RED, lw=0.9, ls=(0, (4, 2)), zorder=6)
# 접속점(차량)
# 접속점 = 실제 도로 필지와 계획 도로의 접촉 면적 50㎡ 이상(access_pts.pkl) + 북동 알천남로
seen = []
for x, y, k, a in ACC:
    seen.append((x, y))
    # 바깥 방향: 경계 무게중심에서 멀어지는 쪽
    c = np.array(B.centroid.coords[0]); d = np.array([x, y]) - c
    if abs(x - 103) < 12 or abs(x - 110) < 6: d = np.array([-1.0, 0.0])
    elif y > 860: d = np.array([0.55, 0.83])
    elif x > 395: d = np.array([1.0, 0.0])
    else: d = np.array([0.0, -1.0])
    d = d / np.linalg.norm(d); p0 = np.array([x, y]) + d * 55
    ax.add_patch(FancyArrowPatch(tuple(p0), (x, y), arrowstyle="-|>,head_length=5,head_width=3", color="#636363", lw=1.3, zorder=8, mutation_scale=1.0))
    ax.add_patch(Circle((x, y), 6.5, fc="white", ec="#636363", lw=0.9, zorder=9))
n_acc = len(seen)
# 위계 번호
def badge(x, y, s, c, r=15):
    ax.add_patch(Circle((x, y), r, fc=c, ec="white", lw=0.8, zorder=12)); ax.text(x, y, s, fontsize=10, color="white", fontweight="bold", ha="center", va="center", zorder=13)
y0b, y1b = S["DBAND"]; ym = (y0b + y1b) / 2
badge(180, ym, "②", GREEN); badge(271, 560, "①", BLUE); badge(150, 120, "③", BLUE); badge(185, 639.2, "④", PURP)
def lab(x, y, s, c, rot=0, ha="center", stroke=None):
    t_ = ax.text(x, y, s, fontsize=10, color=c, fontweight="bold", rotation=rot, ha=ha, va="center", zorder=14, rotation_mode="anchor")
    t_.set_path_effects([pe.withStroke(linewidth=2.0, foreground=stroke)] if stroke else halo(2.2))
lab(345, ym, "선형공원 40 m", "white", stroke=GREEN)
lab(271, 720, "남북 보행축 30 m", "white", rot=90, stroke=BLUE)
lab(222, 175, "사선 보행 가로 20 m", BLUE, rot=57.4)
lab(345, 625, "조망로 8 m", PURP)
lab(170, 362, "횡단 20 m", "#636363"); lab(165, 798, "북측 차도 12.8 m", "#636363")
lab(436, 620, "외곽 순환 가로", "#636363", rot=-90)
for t_, x_, y_, r_ in (("원화로", 70, 560, 90), ("화랑로", -75, 362, 0), ("알천남로", 500, 900, 40)):
    ax.text(x_, y_, t_, fontsize=10, color="#7d7d78", fontweight="bold", rotation=r_, ha="center", va="center", path_effects=halo(2.0), zorder=14)
north_scale(ax, 470, 45, label_m=(0, 50, 100), fs=9, north_at=(600, 130))

pg.top()
# ── 우측: 지표 타일 ──
tx = 160; tw = 232
KP = [("%s㎡" % f0(RG.area), "차량 가로 · %.1f%%" % (RG.area / TOT["boundary"] * 100), "외곽 순환 가로 + 북측 차도", "#636363"),
      ("%s㎡" % f0(PED.area), "보행공간 · %.1f%%" % (PED.area / TOT["boundary"] * 100), "보행 가로 네 개 + 외곽 보도", GREEN),
      ("%s㎡" % f0(sum(g.area for g in BLK)), "가구 %d개 · %.1f%%" % (len(BLK), sum(g.area for g in BLK) / TOT["boundary"] * 100), "건축·오픈스페이스 가구", "#555555")]
kw = (tw - 8) / 3
for i, (v, t, d_, c) in enumerate(KP):
    x_ = tx + i * (kw + 4)
    pg.rect(x_, 30, kw, 25, fc="#F3F5F8", z=5); pg.rect(x_, 30, kw, 1.2, fc=c, z=6)
    pg.t(x_ + 4, 37.0, v, fs=14, bold=True, c=c if c != "#555555" else INK, z=6)
    pg.t(x_ + 4, 44.5, t, fs=10, bold=True, z=6)
    pg.t(x_ + 4, 50.3, d_, fs=10, c=GREY, z=6)
# ── 우측: 가로 구성표(10 pt) ──
ty = 60
cols = ["", "가로", "성격", "폭", "연장·면적", "연결 대상", "위계"]
wd = [5, 48, 32, 26, 30, 63, 28]
xs_ = [tx]
for w in wd: xs_.append(xs_[-1] + w)
pg.rect(tx, ty, sum(wd), 6.4, fc="#2b2b2b", z=5)
for i, c in enumerate(cols): pg.t(xs_[i] + wd[i] / 2, ty + 3.2, c, fs=10, c="white", ha="center", bold=True, z=6)
NL = chr(10)
ROWS = [("#636363", "외곽 순환 가로", "차량(보차공존)", "횡단 20" + NL + "외곽 10~12", "약 1,130 m" + NL + "%s㎡" % f0(S["ROADS"]["EW"].area + S["ROADS"]["O"].area), "원화로·화랑로 교차 · 동·남측 생활가로", "접속점"),
        ("#636363", "북측 차도", "차량", "12.8", "약 280 m" + NL + "%s㎡" % f0(S["ROADS"]["N"].area), "원화로 ↔ 알천남로(북천변)", "북측 유입"),
        (GREEN, "동서 선형공원", "보행·공원", "40", "약 300 m" + NL + "%s㎡" % f0(OP["D"]["g"].area), "성동시장 ↔ 성동리 전랑지", "② 1등"),
        (BLUE, "남북 보행축", "보행·녹지", "30", "약 480 m" + NL + "%s㎡" % f0(OP["E"]["g"].area), "대릉원 ↔ 북천·황성공원", "① 2등"),
        ("#7fa6d8", "사선 보행 가로", "보행·관광 진입", "20", "약 290 m" + NL + "%s㎡" % f0(OP["F"]["g"].area), "관문광장 · 황리단길·대릉원", "③ 2등"),
        (PURP, "향일문 조망로", "보행·조망", "8", "약 260 m" + NL + "%s㎡" % f0(S["PATH8"].area), "경주읍성 향일문(약 310 m)", "④ 3등")]
RH = 11.0; yy = ty + 6.4
for r, (c, nm, ch, w, la, conn, axis) in enumerate(ROWS):
    pg.rect(tx, yy, sum(wd), RH, fc="white" if r % 2 == 0 else "#f7f7f5", z=5)
    pg.rect(xs_[0] + 1.0, yy + 1.4, 2.4, RH - 2.8, fc=c, z=6)
    pg.t(xs_[1] + 1.2, yy + RH / 2, nm, fs=10, bold=True, z=6)
    def cell(i, txt, bold_last=False, color=INK):
        L = []
        for part in txt.split(NL): L += wrap_mm(pg, part, wd[i] - 2.4)
        for j, ln in enumerate(L[:2]): pg.t(xs_[i] + 1.2, yy + RH / 2 + (j - (min(len(L), 2) - 1) / 2) * 4.6, ln, fs=10, z=6, c=color, bold=(bold_last and j == len(L) - 1))
    cell(2, ch); cell(3, w); cell(4, la, bold_last=True); cell(5, conn)
    pg.t(xs_[6] + 1.2, yy + RH / 2, axis, fs=10, bold=True, c=c if c != "#636363" else INK, z=6)
    yy += RH
    if r == 1: pg.line([tx, tx + sum(wd)], [yy, yy], c="#888", lw=0.6, z=7)
pg.line([tx, tx + sum(wd)], [yy, yy], c="#2b2b2b", lw=0.8, z=7)
yy = text_block(pg, tx, yy + 4.2, "폭(m) · 보행공간 %s㎡ = 보행 가로 네 개 + 외곽 보도 %s㎡ · 연장은 근사값" % (f0(PED.area), f0(S["WALK"].area)), tw, c=GREY, z=6)
# ── 원칙 박스 3 ──
yy += 2.0
BOX = [("차량은 외곽과 횡단 한 곳", "차량 가로는 외곽 순환 가로와 화랑로 연결 횡단(20 m)에만 둡니다. 실제 가로 접속점 %d곳." % n_acc, "#636363"),
       ("안쪽은 축을 따른 보행 가로", "대지 축 세 개가 선형공원·남북 보행축·사선 보행 가로가 되어 교차광장과 관문광장에서 만납니다.", GREEN),
       ("위계는 연결 대상의 크기로", "동서축 1등, 대지축과 황리단길 진입 사선 2등, 향일문 조망로 3등.", BLUE)]
bw_ = (tw - 8) / 3; bh = 13.0 + max(block_h(pg, d_, bw_ - 7) for t, d_, c in BOX) + 3.0
for i, (t, d_, c) in enumerate(BOX):
    bx = tx + i * (bw_ + 4)
    pg.rect(bx, yy, bw_, bh, fc="#F3F5F8", z=5); pg.rect(bx, yy, 1.4, bh, fc=c, z=6)
    pg.t(bx + 4, yy + 5.0, t, fs=10, bold=True, c=c if c != "#636363" else INK, z=6)
    text_block(pg, bx + 4, yy + 11.0, d_, bw_ - 7, c=INK, z=6)
# 위계 도식(원칙 박스 아래 남는 자리) — 접속점 7곳의 실제 가로
yy2 = yy + bh + 6.0
pg.t(tx, yy2, "차량 접속점 %d곳 — 실제 도로 필지와 맞닿는 곳" % n_acc, fs=10, bold=True, z=6)
ACC_TXT = ["서측 원화로 2곳(북측 차도 · 화랑로 연결 횡단)", "북동 알천남로(북천변) 1곳(북측 차도)", "동측 생활가로 2곳(외곽 순환 가로)", "남측 생활가로 2곳(외곽 순환 가로 · 모빌리티 허브)"]
for j, t_ in enumerate(ACC_TXT):
    c_, r_ = divmod(j, 2)
    pg.t(tx + c_ * 118, yy2 + 6.4 + r_ * 5.2, "· " + t_, fs=10, c=INK, z=6)
# 범례(지도 위)
lx, ly0 = 6, 160
LG = [("#636363", 1.0, "차량 가로"), (GREEN, 0.85, "보행 가로 1등"), (BLUE, 0.7, "보행 가로 2등"), (PURP, 0.55, "보행 가로 3등"), ("#d5d5d1", 1.0, "외곽 보도"), ("#ececea", 1.0, "가구")]
pg.rect(lx, ly0, 42, 4 + (len(LG) + 2) * 5.4, fc="white", ec="#cccccc", lw=0.4, z=30, alpha=0.95)
for i, (c, a, t) in enumerate(LG):
    y_ = ly0 + 4.6 + i * 5.4
    pg.rect(lx + 2.5, y_ - 1.5, 7, 3.0, fc=c, alpha=a, ec="#bbbbbb", lw=0.2, z=31); pg.t(lx + 12, y_, t, fs=10, z=31)
y_ = ly0 + 4.6 + len(LG) * 5.4
pg.ax.add_patch(Circle((lx + 6, y_), 1.5, fc="white", ec="#636363", lw=0.7, zorder=31)); pg.t(lx + 12, y_, "차량 접속점", fs=10, z=31)
y_ += 5.4; pg.line([lx + 2.5, lx + 9.5], [y_, y_], c=RED, lw=0.8, z=31, ls=(0, (3, 1.5))); pg.t(lx + 12, y_, "구역 경계", fs=10, z=31)
pg.save("D2a_도로계획구상도")
