"""G0 대지 축 구상도(16:9) — 사용자 도출 축(트레이싱 구상도·축 다이어그램)을 실좌표 지구 지도 위에
① 남북축(대지축) 대릉원 ↔ 북천·황성공원 · ② 동서축 성동시장 ↔ 전랑지(폭 40 m 선형공원) · ③ 역사유적축 대릉원·황리단길 ↔ 북동
· 향일문 조망 보행로 → 경주읍성 · 화랑로 연결(차량). 배경은 c2_district.py(지적·간선도로·문화재구역·철도), 주변 건물은 ctx_fixed"""
from gkit import *
from matplotlib.patches import FancyArrowPatch, Circle, Polygon as MPoly
from shapely.ops import polylabel
import textwrap

DS = pickle.load(open(os.path.join(D, "district.pkl"), "rb"))
pg = Page()
pg.header("Masterplan : Site Axes", "Site Axes", "대지 축 구상도",
          sub="구 경주역 대지를 지나는 세 개의 축과 조망 보행로·차량 연결 — 축의 끝점은 실제 위치(관광지·문화재구역 자료)에 맞춤")
EXT = (-820, 1020, -760, 1330)
MX, MY, MW, MH = 4, 30, 240, 192
ax = pg.plan_ax(MX, MY, MW, MH, EXT)
(ex0, ex1), (ey0, ey1) = ax.get_xlim(), ax.get_ylim()
win = box(ex0, ey0, ex1, ey1)
# ── 배경 ──
fill(ax, win, fc="#f7f7f5", z=0.1)
from matplotlib.collections import PatchCollection
pats = [PathPatch(path_of(q)) for g, c in DS["PAR"] if g.intersects(win) for q in polys(g)]
ax.add_collection(PatchCollection(pats, fc="none", ec="#dfdfdb", lw=0.18, zorder=0.3))
for g, c in DS["PAR"]:
    if c == "천" and g.intersects(win): fill(ax, g, fc="#cfe3f0", z=0.35)
for g, rm, un, al in DS["HER"]:
    if "국가지정" in un and g.intersects(win): fill(ax, g, fc="#efe2c9", ec="#d8c39b", lw=0.3, z=0.4, alpha=0.9)
context(ax, (ex0, ex1, ey0, ey1), fc="#e3e3e0", ec="none", z=0.5)
for nm, gs in DS["ROADS"].items():
    for g in gs:
        if g.intersects(win):
            xs, ys = g.xy; ax.plot(xs, ys, color="#c9c9c5", lw=2.6, zorder=0.6, solid_capstyle="round"); ax.plot(xs, ys, color="white", lw=1.8, zorder=0.61, solid_capstyle="round")
for g, c in DS["RAIL"]:
    if g.intersects(win):
        for q in (g.geoms if hasattr(g, "geoms") else [g]):
            xs, ys = q.xy; ax.plot(xs, ys, color="#9a9a96", lw=0.7, ls=(0, (3, 2)), zorder=0.62)
# 대지
fill(ax, B, fc="#dbe8f4", ec="#2a5d9f", lw=1.0, z=2)
for g in S["ROADS"].values(): fill(ax, g, fc="#c7d3df", z=2.1)
# ── 축 ──
BLUE = "#1f6fbf"; GREEN = "#2f8f3a"; CAR = "#555555"; HRED = "#D62828"          # HRED = ③ 역사유적축(사용자 요청 빨강)
def arrow_line(p, q, c, lw=2.2, ls="-", z=12, both=True, hw=4.5):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=("<|-|>" if both else "-|>") + ",head_length=%g,head_width=%g" % (hw, hw * 0.55), color=c, lw=lw, ls=ls, zorder=z, mutation_scale=1.0, shrinkA=0, shrinkB=0))
y0b, y1b = S["DBAND"]; ym = (y0b + y1b) / 2
v = np.array([0.5394, 0.842]); F0 = np.array([131.2, 59.5]) + np.array([-0.842, 0.5394]) * 10.0
TOUR = DS["TOUR"]
MICHU = np.array(TOUR.get("대릉원 미추왕릉", (-221.1, -526.7))); HRD = np.array(TOUR.get("황리단길", (-546.9, -449.2)))
SDM = np.array(TOUR.get("성동시장", (-97.5, 564.0))); EUP = np.array(TOUR.get("경주읍성", (-211.1, 654.1)))
JR = [g for g, rm, un, al in DS["HER"] if "전랑지" in rm and "국가지정" in un][0]; JRc = np.array(JR.centroid.coords[0])
# ② 동서축 — 폭 40 m 띠 + 화살표(성동시장 ↔ 전랑지)
fill(ax, box(-60, y0b, 640, y1b).difference(B), fc=GREEN, alpha=0.18, z=3)
fill(ax, box(102, y0b, 414, y1b).intersection(B), fc=GREEN, alpha=0.55, z=3.1)
arrow_line((SDM[0] - 10, ym), (JRc[0] - 70, ym), GREEN, lw=2.4)
# ① 남북축 — 대지축(구 철도 노반)
arrow_line((271, -230), (271, 1290), BLUE, lw=2.4)
fill(ax, box(256, 291, 286, 772), fc=BLUE, alpha=0.30, z=3.2)
# ③ 역사유적축 — 사선(대릉원 미추왕릉 ↔ 북동)
p3a = F0 - 690 * v; p3b = F0 + 1450 * v
arrow_line(tuple(p3a), tuple(p3b), HRED, lw=2.0, ls=(0, (5, 3)))
# 향일문 조망 보행로 → 경주읍성
YP8 = (635.2 + 643.2) / 2                                                   # 가구 사이 보행자전용도로(폭 8 m) 중심선 — 사용자 수정(트레이싱 파란 화살표)
fill(ax, S["PATH8"], fc="#7a5ab5", alpha=0.85, z=3.3)
arrow_line((560, YP8), tuple(EUP + np.array([16, 0])), "#7a5ab5", lw=1.8, ls=(0, (2, 2)), both=False, hw=3.8)
# 화랑로 연결(차량) — 실제 화랑로 주통경축 + 대지 횡단 도로
for g in DS["AXES"].get("화랑로", []):
    x0_, y0_, x1_, y1_ = g.bounds
    if g.intersects(win) and (y1_ - y0_) < 0.3 * max(x1_ - x0_, 1): xs, ys = g.xy; ax.plot(xs, ys, color=CAR, lw=2.4, zorder=11, solid_capstyle="butt")   # 동서 방향 토막만
ax.plot([103, 412], [343.7, 343.7], color=CAR, lw=2.4, zorder=11)
# ── 축 이름(그림 위) ──
def lab(x, y, s, c, fs=6.4, rot=0, ha="left"):
    ax.text(x, y, s, fontsize=fs, color=c, fontweight="bold", rotation=rot, ha=ha, va="center", path_effects=halo(2.2), zorder=20, rotation_mode="anchor")
lab(282, 1230, "① 남북축(대지축)", BLUE)
lab(470, 525, "② 동서축 · 폭 40 m 선형공원", GREEN)
q = F0 + 1080 * v; lab(q[0] + 14, q[1] - 6, "③ 역사유적축", HRED, rot=57.4)
lab(425, YP8 + 26, "④ 향일문 조망 보행로", "#7a5ab5", fs=5.8)
lab(-560, 372, "화랑로", CAR, fs=6.0); lab(420, 330, "화랑로 연결(차량)", CAR, fs=5.6)
# ── 기준점 ──
NODES = [("성동시장", SDM, GREEN), ("전랑지(사적 88호)", JRc, GREEN), ("경주읍성(향일문)", EUP, "#7a5ab5"),
         ("대릉원(미추왕릉)", MICHU, HRED), ("황리단길", HRD, HRED), ("구 경주역사", np.array([175.0, 268.0]), "#b5651d")]
for nm, p, c in NODES:
    ax.add_patch(Circle(tuple(p), 15, fc="white", ec=c, lw=1.2, zorder=21)); ax.add_patch(Circle(tuple(p), 6.5, fc=c, ec="none", zorder=22))
    dx = 24
    ax.text(p[0] + dx, p[1] + 18, nm, fontsize=6.0, fontweight="bold", color=INK, ha="left" if dx > 0 else "right", va="bottom", path_effects=halo(2.2), zorder=23)
ax.text(300, 1300, "↑ 북천 · 황성공원(약 1 km)", fontsize=6.0, color=BLUE, fontweight="bold", va="top", path_effects=halo(2.0), zorder=23)
for g in DS["AXES"].get("북천 수변경관축", []):
    if g.intersects(win): xs, ys = g.xy; ax.plot(xs, ys, color="#5c9fd0", lw=1.2, ls=(0, (1, 1.5)), zorder=0.7)
bc = [g for g in DS["AXES"].get("북천 수변경관축", []) if g.intersects(win)]
if bc:
    pt = unary_union(bc).intersection(box(560, ey0, 860, ey1)).representative_point()
    ax.text(pt.x, pt.y + 30, "북천", fontsize=6.4, color="#2f74a8", fontweight="bold", style="italic", ha="center", path_effects=halo(2.0), zorder=23)
north_scale(ax, -330, -735, label_m=(0, 250, 500), north_at=(260, -690))

pg.top()
# ── 우측 설명 박스 ──
def dist(a, b): return float(np.hypot(*(np.asarray(a) - np.asarray(b))))
BOX = [("②", "위계 1등", "동서축 — 성동시장 ↔ 전랑지", GREEN,
        ["대지 중앙을 가로지르는 폭 40 m 선형공원·가로광장(약 300 m)", "서측 끝 → 성동시장 약 %d m · 동측 끝 → 성동리 전랑지 약 %d m" % (round(dist((104, ym), SDM), -1), round(dist((406, ym), JRc), -1))]),
       ("①", "위계 2등", "남북축(대지축) — 대릉원 ↔ 북천·황성공원", BLUE,
        ["구 철도 노반을 따라 대지를 종단하는 폭 30 m 남북 중앙 보행축", "북측 끝에서 북천을 지나 황성공원(약 1 km)과 연결"]),
       ("③", "위계 2등", "역사유적축 — 대릉원·황리단길 ↔ 북동", HRED,
        ["폭 20 m 사선 보행축 — 연장선이 미추왕릉(약 %d m)에 닿음" % round(dist(F0, MICHU), -1), "황리단길 관광객을 대지 안으로 끌어들이는 진입 동선"]),
       ("④", "위계 3등", "향일문 조망 보행로 · 화랑로 연결", "#7a5ab5",
        ["가구 사이 보행자전용도로(폭 8 m)를 서쪽으로 곧게 이어 경주읍성 향일문을 바라봄(서측 끝에서 약 %d m)" % round(dist((103, YP8), EUP), -1), "차량은 화랑로를 대지 안으로 이은 횡단 가로(폭 20 m) 한 곳으로 연결"])]
bx, bw = 252, 142
TW = bw - 14
CH = []
for no, rank, ttl, c, bl in BOX:
    h_ = 15.0 + sum(block_h(pg, b_, TW, bullet=True) for b_ in bl) + 1.6 * (len(bl) - 1) + 3.0
    CH.append(h_)
TOP, BOT, GAP = 32.0, 219.0, 3.5
extra = (BOT - TOP - GAP * (len(BOX) - 1) - sum(CH)) / len(BOX)
yy = TOP
for (no, rank, ttl, c, bl), ch in zip(BOX, CH):
    h = ch + extra; y0 = yy + extra / 2
    pg.rect(bx, yy, bw, h, fc="#F3F5F8", z=10); pg.rect(bx, yy, 2.0, h, fc=c, z=11)
    pg.ax.add_patch(Circle((bx + 9, y0 + 6.5), 4.2, fc=c, ec="white", lw=0.6, zorder=12)); pg.t(bx + 9, y0 + 6.6, no, fs=10, c="white", bold=True, ha="center", z=13)
    pg.t(bx + 16, y0 + 4.0, rank, fs=10, c=c, bold=True, z=12)
    pg.t(bx + 16, y0 + 9.2, ttl, fs=10, bold=True, z=12)
    ly = y0 + 15.5
    for b_ in bl:
        ly = text_block(pg, bx + 7, ly, b_, TW, c=INK, z=12, bullet=True) + 1.6
    yy += h + GAP
# 범례(지도 왼쪽 아래)
lx, ly0 = 8, 168
ly0 = 33
pg.rect(lx, ly0, 56, 12 + 7 * 5.6, fc="white", ec="#cccccc", lw=0.4, z=30, alpha=0.95)
pg.t(lx + 3, ly0 + 4, "범례", fs=6.6, bold=True, z=31)
LG = [("arrow", BLUE, "-", "대지 축"), ("arrow", HRED, (0, (4, 2.5)), "역사유적축"), ("arrow", GREEN, "-", "동서축(선형공원)"), ("arrow", "#7a5ab5", (0, (2, 2)), "조망 보행로"),
      ("line", CAR, "-", "차량 연결(화랑로)"), ("box", "#efe2c9", None, "국가지정문화재구역"), ("box", "#dbe8f4", None, "계획 구역")]
for i, (k, c, ls, t) in enumerate(LG):
    y_ = ly0 + 10.5 + i * 5.6
    if k == "arrow": pg.ax.add_patch(FancyArrowPatch((lx + 3, y_), (lx + 12, y_), arrowstyle="-|>,head_length=2.0,head_width=1.2", color=c, lw=1.1, ls=ls, zorder=31, mutation_scale=1.0))
    elif k == "line": pg.line([lx + 3, lx + 12], [y_, y_], c=c, lw=1.6, z=31)
    else: pg.rect(lx + 3, y_ - 1.6, 9, 3.2, fc=c, ec="#bbbbbb", lw=0.3, z=31)
    pg.t(lx + 15, y_, t, fs=6.0, z=31)
pg.save("D0_대지축구상도")
