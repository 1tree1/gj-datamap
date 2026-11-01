"""R2 948 m 플랫폼 — 철도의 선을 3구간에서 들어 올린다(2026-10-15 사용자 확정: 3구간부터)
- 평면: 대릉원 방면 사선 보행축 → 남북 보행축 → 북측 근린공원 → 북천. 옛 선로(폐선) 흔적, A안 통경축
  ① 남측 관문 캐노피(사선 보행축 북단) ② 화랑로 게이트(통경축 교차) ③ 교차광장 공중 회랑(선형공원 교차)
  나머지는 지상 레일 정원 — 선은 끊기지 않는다
- 단면: 1:600, 가로 = 세로(수직 과장 없음). 높이는 모두 제안값(†) — 허용기준 ⑤ 평지붕 8 m 아래로 맞춤(적용 구역 확인 필요)"""
from k0 import *

E = OP["E"]["g"]; F = OP["F"]["g"]
SEG1 = unary_union([F.intersection(box(150, 185, 300, 333)).buffer(-3), E.intersection(box(250, 291, 292, 320)).buffer(-4)])
SEG2 = box(258.0, 318.0, 284.0, 370.0)                                   # 26 × 52 m, 통경축(y 333.7–353.7) 위
RING_O = box(244.0, 464.0, 298.0, 528.0); RING_I = box(256.0, 476.0, 286.0, 516.0)
SEG3 = RING_O.difference(RING_I)                                         # 회랑 폭 12 m, 가운데 30 × 40 m 열림(= 교차광장)
L1 = length_of(SEG1); L2 = SEG2.bounds[3] - SEG2.bounds[1]; L3 = RING_O.bounds[3] - RING_O.bounds[1]
A1, A2, A3 = SEG1.area, SEG2.area, SEG3.area
LINE = 948.0
print("seg1 %.0f m %.0f㎡ / seg2 %.0f m %.0f㎡ / seg3 %.0f m %.0f㎡ / deck run %.0f m (%.0f%%)" % (L1, A1, L2, A2, L3, A3, L1 + L2 + L3, (L1 + L2 + L3) / LINE * 100))
RAILG = "#D3DDB4"

pg = Page()
pg.header("Critique Response : Elevated Platform", "948 m Platform", "철도의 선을 세 곳에서 들어 올린다",
          sub="땅을 팔 수 없으니 위로 — 옛 선로 948 m를 지상 레일 정원으로 잇고, 관문·화랑로 교차·선형공원 교차 세 곳에서 판을 들어 올린다")

# ── 왼쪽: 평면 ──
EXT = (40, 470, 30, 1040)
ax = pg.plan_ax(3, 33, 92, 188, EXT)
base(ax)
site(ax, ew_as_road=False, open_alpha=0.0)
fill(ax, OP["D"]["g"], fc=GREEN, alpha=0.55, z=1.3); fill(ax, S["PATH8"], fc=PURP, alpha=0.5, z=1.3)
fill(ax, E, fc=RAILG, z=1.31); fill(ax, F, fc=RAILG, z=1.31)
a_corridor(ax, trees=False, bollards=False)
for g, kind in DS["RAIL"]:                                               # 옛 선로(폐선) — 대지 안만
    gi = g.intersection(B)
    for ln in ([gi] if gi.geom_type == "LineString" else list(getattr(gi, "geoms", []))):
        if ln.geom_type == "LineString" and ln.length > 3:
            xs, ys = ln.xy; ax.plot(xs, ys, color="#8c6d4f", lw=0.35, zorder=1.33, alpha=0.8)
NX = [(271, 772), (262, 860), (249, 940), (241, 1000)]                    # 북측 근린공원을 지나 북천 방면(지상)
ax.plot(*zip(*NX), color="#9db06a", lw=4.0, zorder=1.32, solid_capstyle="round", alpha=0.9)
ax.add_patch(FancyArrowPatch((241, 1000), (246, 1036), arrowstyle="-|>,head_length=4,head_width=3", color="#6f8a3a", lw=1.2, zorder=9, mutation_scale=1.0))
ax.add_patch(FancyArrowPatch((126, 62), (92, 36), arrowstyle="-|>,head_length=4,head_width=3", color="#6f8a3a", lw=1.2, zorder=9, mutation_scale=1.0))
for g in (SEG1, SEG2, SEG3): fill(ax, g, fc=PLATC, ec="white", lw=0.6, z=8, alpha=0.92)
stations(ax); pagoda(ax, label=False)
for (x, y), s_ in (((214, 230), "①"), ((300, 344), "②"), ((318, 496), "③")):
    ax.add_patch(Circle((x, y), 15, fc=PLATC, ec="white", lw=0.8, zorder=12)); ax.text(x, y, s_, fontsize=10, color="white", fontweight="bold", ha="center", va="center", zorder=13)
ax.plot([445, 445], [54, 1002], color=INK, lw=0.6, zorder=9)
for yy in (54, 1002): ax.plot([438, 452], [yy, yy], color=INK, lw=0.6, zorder=9)
lab(ax, 457, 528, "948 m", INK, rot=90)
lab(ax, 120, 1018, "북천·황성공원", "#6f8a3a", ha="left")
lab(ax, 96, 22, "대릉원", "#6f8a3a", ha="left")
north_scale(ax, 300, 70, label_m=(0, 50, 100), fs=10, north_at=(60, 900))

pg.top()
s = 1000.0 / 600.0                                                       # 1:600 → mm/m
HL = [(8.0, "8 m"), (12.0, "12 m")]


def frame(x0, x1, gy, title, c=PLATC, hl=True, under=True):
    pg.t(x0, gy - 33.0, title, fs=10, bold=True, c=c)
    pg.line([x0, x1], [gy, gy], c=INK, lw=0.8, z=8)
    if under:
        pg.rect(x0, gy, x1 - x0, 2.5 * s, fc="#efe2cf", z=2, hatch="////", ec="#c9a77c", lw=0.0)
    if hl:
        for h, t in HL:
            pg.line([x0, x1], [gy - h * s, gy - h * s], c="#b0b0b0", lw=0.5, z=3, ls=(0, (3, 2)))
            pg.t(x1 + 1.5, gy - h * s, t, fs=10, c=GREY, z=3)


def deck(x0, x1, gy, top, th=1.0, rail=True, fc=PLATC, alpha=1.0, z=9):
    pg.rect(x0, gy - top * s, x1 - x0, th * s, fc=fc, ec="none", z=z, alpha=alpha)
    if rail: pg.line([x0, x1], [gy - (top + 1.2) * s, gy - (top + 1.2) * s], c=fc, lw=0.6, z=z)


def col(x, gy, top):
    pg.rect(x - 0.4 * s, gy - top * s, 0.8 * s, top * s, fc="#5b5b5b", z=8)
    pg.rect(x - 0.9 * s, gy - 0.25 * s, 1.8 * s, 0.5 * s, fc="#5b5b5b", z=8)


def dim(x0, x1, y, t):
    pg.line([x0, x1], [y, y], c=INK, lw=0.5, z=12)
    for x in (x0, x1): pg.line([x, x], [y - 1.2, y + 1.2], c=INK, lw=0.5, z=12)
    pg.t((x0 + x1) / 2, y - 2.6, t, fs=10, ha="center", z=12)


# ② 화랑로 게이트 — 남북 보행축을 따라 자른 단면(서쪽을 본다). 왼쪽 = 남, 오른쪽 = 북
X0 = 102; Y0w, Y1w = 298.0, 390.0; GY = 75.0
px = lambda y: X0 + (y - Y0w) * s
frame(px(Y0w), px(Y1w), GY, "② 화랑로 게이트 — 남북 보행축 단면(서쪽을 본다)")
pg.rect(px(EWB.bounds[1]), GY - 0.25 * s, (EWB.bounds[3] - EWB.bounds[1]) * s, 0.5 * s, fc="#cdbf9f", z=8.5)
for y in (EWB.bounds[1] + 3.0, EWB.bounds[3] - 3.0): tree(pg, px(y), GY, s, c="#d3e6c4")   # 통경축 가로수(판 바깥, 뒤쪽)
deck(px(SEG2.bounds[1]), px(SEG2.bounds[3]), GY, 6.0)
for y in (322.0, 366.0): col(px(y), GY, 5.0)
for ya, yb in ((300.0, 318.0), (388.0, 370.0)):                           # 계단(6 m / 18 m)
    pg.ax.plot([px(ya), px(yb)], [GY, GY - 6.0 * s], color=PLATC, lw=1.2, zorder=9)
for y in (305, 341, 347, 383): person(pg, px(y), GY, s)
for y in (327, 344, 361): person(pg, px(y), GY - 6.0 * s, s)
pg.ax.add_patch(Circle((px(344.0) + 6, GY - 3.2 * s), 1.3, fc="white", ec="#b07d10", lw=0.9, zorder=13))
pg.ax.add_patch(Circle((px(344.0) + 6, GY - 3.2 * s), 0.45, fc="#b07d10", zorder=14))
dim(px(SEG2.bounds[1]), px(SEG2.bounds[3]), GY - 6.0 * s - 6.0, "판 52 m · 데크 +6.0 m")
pg.t(px(EWB.bounds[1]) + (EWB.bounds[3] - EWB.bounds[1]) * s / 2, GY + 7.5, "⊙ 통경축 20 m(시선 → 동쪽) · 아래 순높이 5.0 m", fs=10, ha="center", c="#8a6d2e")
pg.t(px(Y0w) + 1, GY + 7.5, "남", fs=10, c=GREY); pg.t(px(Y1w) - 1, GY + 7.5, "북", fs=10, c=GREY, ha="right")

# ① 남측 관문 캐노피 — 사선 보행축을 가로질러 자른 단면
X1 = 270; GY1 = 75.0; W1 = 52.0
qx = lambda m: X1 + m * s
frame(qx(0), qx(W1), GY1, "① 남측 관문 캐노피 — 사선 보행축 가로 단면", hl=False)
pg.rect(qx(0), GY1 - 14.0 * s, 10.0 * s, 14.0 * s, fc="#eeeeec", ec="#cfcfcb", lw=0.3, z=4)
pg.t(qx(5.0), GY1 - 11.5 * s, "획지 9", fs=10, ha="center", c=GREY, z=5); pg.t(qx(5.0), GY1 - 8.5 * s, "5층", fs=10, ha="center", c=GREY, z=5)
pg.rect(qx(W1 - 10.0), GY1 - 14.0 * s, 10.0 * s, 14.0 * s, fc="#eeeeec", ec="#cfcfcb", lw=0.3, z=4)
pg.t(qx(W1 - 5.0), GY1 - 11.5 * s, "근대", fs=10, ha="center", c=GREY, z=5); pg.t(qx(W1 - 5.0), GY1 - 8.5 * s, "역사관", fs=10, ha="center", c=GREY, z=5)
xx = qx(16.0)
for nm, w, c_ in (("식재", 6, "#9fd67c"), ("보행", 8, "#efe8d6"), ("식재", 6, "#9fd67c")):
    pg.rect(xx, GY1 - 0.25 * s, w * s, 0.5 * s, fc=c_, z=8.5); xx += w * s
pg.rect(qx(19.0), GY1 - 6.5 * s, 14.0 * s, 0.4 * s, fc=PLATC, z=9)
for m in (21.0, 31.0): col(qx(m), GY1, 6.1)
for m in (17.5, 34.5): tree(pg, qx(m), GY1, s, h=8.0, r=2.4)
for m in (24.0, 26.5, 29.0): person(pg, qx(m), GY1, s)
pg.line([qx(10.0), qx(W1 - 10.0)], [GY1 - 7.0 * s, GY1 - 7.0 * s], c="#B97A4E", lw=0.7, z=10, ls=(0, (2.5, 1.5)))
pg.t(qx(W1 / 2), GY1 - 7.0 * s - 2.6, "구 역사 높이 7 m", fs=10, ha="center", c="#B97A4E", z=10)
pg.t(qx(W1 / 2), GY1 + 7.5, "보행축 20 m · 지붕 +6.5 m · 폭 14 m", fs=10, ha="center", c=PLATC)

# ③ 교차광장 공중 회랑 — 남북 보행축 단면(서쪽을 본다)
X3 = 102; Y0c, Y1c = 440.0, 552.0; GY3 = 133.0
rx = lambda y: X3 + (y - Y0c) * s
frame(rx(Y0c), rx(Y1c), GY3, "③ 교차광장 공중 회랑 — 남북 보행축 단면(서쪽을 본다)")
pg.rect(rx(Y0c), GY3 - 12.0 * s, (459.6 - Y0c) * s, 12.0 * s, fc="#eeeeec", ec="#cfcfcb", lw=0.3, z=4)
pg.t(rx(Y0c) + 1.2, GY3 - 13.6 * s, "공방동 3층", fs=10, c=GREY, z=5)
pg.rect(rx(538.6), GY3 - 16.0 * s, (Y1c - 538.6) * s, 16.0 * s, fc="#eeeeec", ec="#cfcfcb", lw=0.3, z=4)
pg.t(rx(Y1c) - 1.2, GY3 - 17.6 * s, "창업센터 4층", fs=10, c=GREY, z=5, ha="right")
deck(rx(464.0), rx(528.0), GY3, 4.0, rail=False, fc=tint(PLATC, 0.55), z=5)       # 뒤쪽 서측 회랑(입면)
deck(rx(464.0), rx(476.0), GY3, 4.0); deck(rx(516.0), rx(528.0), GY3, 4.0)          # 잘린 남·북 회랑
for y in (466.0, 474.0, 518.0, 526.0): col(rx(y), GY3, 3.0)
pg.ax.plot([rx(459.6), rx(464.0)], [GY3 - 4.0 * s, GY3 - 4.0 * s], color=PLATC, lw=1.4, zorder=9)
pg.ax.plot([rx(528.0), rx(538.6)], [GY3 - 4.0 * s, GY3 - 4.0 * s], color=PLATC, lw=1.4, zorder=9)
pg.rect(rx(476.0), GY3 - 0.25 * s, 40.0 * s, 0.5 * s, fc="#9fd67c", z=8.5)
for y in (479.0, 485.0, 507.0, 513.0): tree(pg, rx(y), GY3, s)
for y in (445, 492, 498, 548): person(pg, rx(y), GY3, s)
for y in (468, 471, 521, 525): person(pg, rx(y), GY3 - 4.0 * s, s)
dim(rx(476.0), rx(516.0), GY3 - 12.5 * s, "열린 가운데 40 m")
pg.t(rx(470.0), GY3 + 7.5, "회랑 12 m", fs=10, ha="center", c=PLATC); pg.t(rx(522.0), GY3 + 7.5, "회랑 12 m", fs=10, ha="center", c=PLATC)
pg.t(rx(496.0), GY3 + 7.5, "선형공원 — 나무가 가운데로 자란다", fs=10, ha="center", c=GREEN)
pg.t(rx(Y0c) + 1, GY3 + 13.0, "데크 +4.0 m = 2층 바닥 · 공방동·창업센터 2층과 연결", fs=10, c=INK)
pg.t(rx(Y0c) + 1, GY3 + 18.5, "단면 1:600, 가로 = 세로 · 점선 = 높이 검토 기준선(8 m 허용기준 ⑤ 평지붕, 12 m 경사지붕)", fs=10, c=GREY)

# 판의 규칙
bx = 300; by = 101.0; bw = 96
box_note(pg, bx, by, bw, "판의 규칙", [
    "땅을 파지 않는다 — 지면에 닿는 것은 기둥 기초뿐, 위치는 시굴 결과(유구)를 피해 정한다",
    "모든 판은 8 m 아래 — 허용기준 ⑤ 평지붕(검토 기준)",
    "구 역사 가까이에서는 역사(7 m)보다 낮게",
    "판이 없는 구간은 지상 레일 정원 — 948 m 선은 끊기지 않는다"], c=PLATC, bullets=True)

# 구간표
ty = 160.0
cols = ["구간", "크기", "높이 †", "잇는 곳", "레퍼런스"]; wd = [44, 58, 50, 80, 62]
rows = [["① 남측 관문 캐노피", "약 %d m × 14 m · %s㎡" % (round(L1, -1), f0(A1)), "지붕 +6.5 m", "관문광장 ↔ 남북축 · 근대역사관", "mAAch ecute · Coal Drops Yard"],
        ["② 화랑로 게이트", "52 × 26 m · %s㎡" % f0(A2), "데크 +6.0 m", "남북축 양 끝 계단 · 위에서 역사·동쪽 조망", "MASP(들어 올려 조망 보존)"],
        ["③ 교차광장 공중 회랑", "54 × 64 m, 폭 12 m · %s㎡" % f0(A3), "데크 +4.0 m", "획지 5·6·7·8 2층", "서울로7017 · Kolumba"],
        ["지상 레일 정원", "나머지 약 %d m" % round(LINE - L1 - L2 - L3, -1), "지면", "대릉원 ↔ 북천 · 레일 존치 · 발굴 창", "Gleisdreieck · 경춘선숲길"]]
yy = table(pg, 102, ty, cols, rows, wd, rh=6.2, fs=10, aligns=["left"] * 5, color_chip={0: PLATC, 1: PLATC, 2: PLATC, 3: RAILG})
pg.t(102, yy + 4.5, "판 %s㎡ · 948 m 중 판 구간 약 %d m(%d%%) · † 제안값 — 높이 겹(고도지구 20/15 m, 황오동 도로 인접 3층·15 m, 허용기준 ⑤ 8/12 m)의 적용 구역 확인 필요"
     % (f0(A1 + A2 + A3), round(L1 + L2 + L3, -1), round((L1 + L2 + L3) / LINE * 100)), fs=10, c=GREY)
save(pg, "R2_948m플랫폼")
