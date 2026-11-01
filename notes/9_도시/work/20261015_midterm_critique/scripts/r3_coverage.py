"""R3 건폐율 0.50 — 같은 연면적을 낮고 넓게(2026-10-15 사용자 확정)
- 왼쪽: 지금의 바닥 — 건물 / 형태 있는 비움(광장·중정·코트·공원·보행축) / 획지 안 남은 땅
- 가운데: Spacematrix(GSI–FSI) — 획지 13개 현재 → 목표, 주변 경계 띠(서·동·남·북) 기준점, 평균 층수 등치선
  + 형태 전환 5종(슬래브 → 중정형·ㄷ자·기단+분동·라이닝 주차·골목 매트)
- 오른쪽: 획지별 목표표 — 형태 있는 비움은 그대로 두고, 남은 땅(순획지)에만 목표 건폐율을 적용한다(†)
  연면적 192,447㎡는 고정. 목표 건폐율은 제안값이며 매스 재작업에서 다시 잰다"""
from k0 import *

ROWS = lot_targets()                                                     # 규칙 상수는 k0(KEEP·GRP·TGT·LMIN·FORM·SHORT)
SA = sum(r["A"] for r in ROWS); SB0 = sum(r["ba0"] for r in ROWS); SB1 = sum(r["ba1"] for r in ROWS); SG = sum(r["gfa"] for r in ROWS)
SOP = sum(r["opA"] for r in ROWS); SRES = sum(r["res"] for r in ROWS)
print("lots %.0f ba %.0f → %.0f  GSI %.3f → %.3f  gfa %.0f  open %.0f  residual %.0f → %.0f" % (SA, SB0, SB1, SB0 / SA, SB1 / SA, SG, SOP, SRES, SRES - (SB1 - SB0)))

pg = Page()
pg.header("Critique Response : Fill the Ground", "Coverage 0.50", "같은 연면적을 낮고 넓게",
          sub="형태 있는 비움(광장·중정·공원·보행축)은 지키고, 획지 안에 남은 땅을 채운다 — 연면적 %s㎡ 고정, 획지 건폐율 %.2f → %.2f" % (f0(SG), SB0 / SA, SB1 / SA))

# ── 왼쪽: 바닥 지도 ──
EXT = (40, 470, 30, 1040)
ax = pg.plan_ax(3, 33, 92, 188, EXT)
base(ax)
for g in BLK: fill(ax, g, fc="#ececea", ec="none", z=1)
fill(ax, S["WALK"], fc="#e3e3df", z=1.1)
RESC = "#F4B183"; OPC = "#E8D5A8"; FIGC = "#4a4a4a"
for r in ROWS:
    fill(ax, r["g"].difference(r["fp"]).difference(r["op"]), fc=RESC, ec="none", z=1.3)
    fill(ax, r["op"], fc=OPC, z=1.32)
for p in S["PARKS"]: fill(ax, p["g"], fc=tint(PARKC, 0.1), z=1.3)
fill(ax, OP["D"]["g"], fc=tint(PARKC, 0.1), z=1.3)
for k in "EF": fill(ax, OP[k]["g"], fc=tint(BLUE, 0.55), z=1.3)
fill(ax, S["PATH8"], fc=tint(PURP, 0.45), z=1.3)
a_corridor(ax, trees=False, bollards=False)
for g in R.values():
    if g is not EWB: fill(ax, g, fc=CARC, z=1.4)
for r in ROWS: fill(ax, r["fp"], fc=FIGC, ec="white", lw=0.3, z=2)
xs, ys = B.exterior.xy; ax.plot(xs, ys, color=RED, lw=0.9, ls=(0, (4, 2)), zorder=6)
for r in ROWS:
    p = lot_label_pt(dict(g=r["g"]), avoid=r["fp"])
    ax.add_patch(Circle((p.x, p.y), 11, fc="white", ec=INK, lw=0.5, zorder=12)); ax.text(p.x, p.y, str(r["no"]), fontsize=10, ha="center", va="center", zorder=13, color=INK, fontweight="bold")
north_scale(ax, 300, 70, label_m=(0, 50, 100), fs=10, north_at=(60, 900))
pg.top()

# ── 가운데: Spacematrix ──
cx0, cy0, cw, ch = 112, 38, 100, 76
sm = pg.fig.add_axes([cx0 / PW, 1 - (cy0 + ch) / PH, cw / PW, ch / PH])
sm.set_xlim(0, 1.0); sm.set_ylim(0, 4.6)
for L_ in (1, 2, 3, 4, 5, 6):
    gx = np.linspace(0.02, 1.0, 50); sm.plot(gx, L_ * gx, color="#c8c8c8", lw=0.6, ls=(0, (3, 2)), zorder=1)
    xe = min(1.0, 4.6 / L_) * 0.97
    sm.text(xe, L_ * xe + (0.08 if L_ * xe < 4.4 else -0.25), "%d층" % L_, fontsize=10, color="#9a9a9a", ha="right", va="bottom", zorder=2)
for (gx_, fy_, t_, dx_, dy_, ha_) in ((0.57, 1.35, "서측 띠", 0.025, -0.12, "left"), (0.41, 0.57, "", 0, 0, "left"), (0.40, 0.64, "동·남측 띠", 0.025, -0.16, "left"), (0.20, 0.22, "북측 띠", -0.03, 0.30, "right")):
    sm.add_patch(Rectangle((gx_ - 0.012, fy_ - 0.05), 0.024, 0.10, fc="#888888", ec="none", zorder=4))
    if t_: sm.text(gx_ + dx_, fy_ + dy_, t_, fontsize=10, color="#777", va="center", ha=ha_, zorder=5)
for r in ROWS:
    c = LOTCOL[r["cat"]]; fsi = r["gfa"] / r["A"]; g0 = r["ba0"] / r["A"]; g1 = r["ba1"] / r["A"]
    if g1 - g0 > 0.01:
        sm.add_patch(FancyArrowPatch((g0, fsi), (g1, fsi), arrowstyle="-|>,head_length=3,head_width=2", color=shade(c, 0.75), lw=0.8, zorder=5, mutation_scale=1.0))
    sm.add_patch(Circle((g0, fsi), 0.016, fc="white", ec=shade(c, 0.75), lw=0.9, zorder=6, transform=sm.transData))
    sm.plot([g1], [fsi], "o", ms=5.0, mfc=c, mec=shade(c, 0.7), mew=0.6, zorder=7)
    dy_ = {10: 0.10, 11: -0.30, 3: -0.28}.get(r["no"], 0.03)
    sm.text(g1 + 0.018, fsi + dy_, str(r["no"]), fontsize=10, color=INK, va="bottom", zorder=8)
G0, G1, FS = SB0 / SA, SB1 / SA, SG / SA
sm.annotate("", xy=(G1, FS), xytext=(G0, FS), arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.4), zorder=9)
sm.plot([G0], [FS], marker="*", ms=11, mfc="white", mec=RED, mew=1.0, zorder=10); sm.plot([G1], [FS], marker="*", ms=12, mfc=RED, mec="white", mew=0.6, zorder=10)
sm.text(G0 - 0.02, FS + 0.28, "현재 %.2f · %.1f층" % (G0, FS / G0), fontsize=10, color=RED, ha="right", fontweight="bold", zorder=11)
sm.text(G1 + 0.02, FS - 0.42, "목표 %.2f · %.1f층" % (G1, FS / G1), fontsize=10, color=RED, ha="left", fontweight="bold", zorder=11)
sm.set_xlabel("건폐율 GSI (획지 기준)", fontsize=10); sm.set_ylabel("용적률 FSI", fontsize=10)
sm.tick_params(labelsize=10, length=2)
for sp in ("top", "right"): sm.spines[sp].set_visible(False)
pg.t(cx0 - 10, 34.5, "Spacematrix — 획지 13개, ○ 현재 → ● 목표 · ■ 경계 밖 0–150 m 띠(순대지)", fs=10, bold=True)

# ── 가운데 아래: 형태 전환 5종 ──
ty0 = 130.0
pg.t(cx0 - 10, ty0, "형태 전환 — 점선 = 지금의 판상 동, 채움 = 바꾼 바닥", fs=10, bold=True)
IW, IH = 36.0, 25.0


def icon(ix, iy, kind, title, lots):
    pg.rect(ix, iy, IW, IH, fc="#f7f7f5", ec="#dddddd", lw=0.4, z=4)
    for k in range(2):
        pg.rect(ix + 7 + k * 13, iy + 5, 6, 15, fc="none", ec="#999", lw=0.6, z=6, ls=(0, (2, 1.2)))
    X, Y = ix + 4, iy + 3.5; W_, H_ = IW - 8, IH - 7
    if kind == "court":
        pg.rect(X, Y, W_, H_, fc=FIGC, z=5); pg.rect(X + 6, Y + 5, W_ - 12, H_ - 10, fc=OPC, z=5.5)
    elif kind == "u":
        pg.rect(X, Y, W_, H_, fc=FIGC, z=5); pg.rect(X + 7, Y, W_ - 14, H_ - 6, fc=OPC, z=5.5)
    elif kind == "podium":
        pg.rect(X, Y, W_, H_, fc="#8a8a8a", z=5); pg.rect(X + 3, Y + 3, 8, H_ - 6, fc=FIGC, z=5.5); pg.rect(X + W_ - 11, Y + 3, 8, H_ - 6, fc=FIGC, z=5.5)
    elif kind == "lined":
        pg.rect(X, Y, W_, H_, fc="#F09AB0", z=5); pg.rect(X + 3.2, Y + 3.2, W_ - 3.2, H_ - 3.2, fc="#A3A8AE", z=5.5)
        pg.t(X + W_ / 2 + 1.6, Y + H_ / 2 + 1.6, "P", fs=10, c="white", bold=True, ha="center", z=6.5)
    elif kind == "mat":
        for i_ in range(4):
            for j_ in range(3):
                if (i_, j_) == (1, 1): continue
                pg.rect(X + i_ * 7.2, Y + j_ * 6.2, 6.0, 5.0, fc=FIGC, z=5)
        pg.rect(X + 7.2, Y + 6.2, 6.0, 5.0, fc=OPC, z=5)
    pg.t(ix, iy + IH + 3.6, title, fs=10, bold=True, z=6)
    pg.t(ix, iy + IH + 8.4, lots, fs=10, c=GREY, z=6)


ICONS = [("court", "중정형 · 둘레형", "획지 1·4·12"), ("u", "ㄷ자", "획지 5·9"), ("podium", "기단 + 분동", "획지 3·6·10"),
         ("lined", "라이닝 주차", "획지 2·13 (가로변 상가)"), ("mat", "골목 매트", "획지 7·8 · 관문상가 11")]
for i, (k, t_, l_) in enumerate(ICONS):
    r_, c_ = divmod(i, 3)
    icon(cx0 - 10 + c_ * (IW + 4.5), ty0 + 4.5 + r_ * (IH + 12.5), k, t_, l_)

# ── 오른쪽: 획지별 목표표 ──
TX = 230
cols = ["획지", "면적", "지정 비움", "GSI 지금", "GSI 목표", "증가", "평균 층수", "형태 전환"]
wd = [30, 16, 18, 17, 17, 16, 21, 32]
rows = []
for r in ROWS:
    rows.append(["%d %s" % (r["no"], SHORT[r["no"]]), f0(r["A"]), f0(r["opA"]) if r["opA"] > 1 else "-", "%.2f" % (r["ba0"] / r["A"]), "%.2f" % (r["ba1"] / r["A"]),
                 ("+" + f0(r["ba1"] - r["ba0"])) if r["ba1"] - r["ba0"] > 1 else "-", "%.1f → %.1f" % (r["gfa"] / r["ba0"], r["gfa"] / r["ba1"]), FORM[r["no"]]])
rows.append(["획지 합계", f0(SA), f0(SOP), "%.2f" % (SB0 / SA), "%.2f" % (SB1 / SA), "+" + f0(SB1 - SB0), "%.1f → %.1f" % (SG / SB0, SG / SB1), "연면적 고정"])
chips = {i: LOTCOL[r["cat"]] for i, r in enumerate(ROWS)}
yy = table(pg, TX, 35.0, cols, rows, wd, rh=5.9, fs=10, aligns=["left", "right", "right", "right", "right", "right", "center", "left"],
           sub_rows=(len(rows) - 1,), color_chip=chips)
yy = text_block(pg, TX, yy + 4.2, "† 목표 건폐율은 순획지(획지에서 지정 비움을 뺀 땅) 기준 — 서측·중앙 %.2f · 동측 %.2f · 주차 %.2f · 구 역사 %.2f. 지금 값이 더 크면 유지하고, 연면적이 고정이므로 평균 층수는 2층(골목 매트·기단 확장 1.5층, 관문상가·방문자 1층) 아래로 내리지 않는다. GSI·층수는 동 바닥 합집합 기준이라 중간마감 표(건축면적 48,741㎡)와 조금 다르다." % (TGT["W"], TGT["E"], TGT["P"], TGT["H"]), sum(wd), c=GREY) - 5.0

# 숫자 요약 + 원칙
by = yy + 4.5
items = [("획지 안 남은 땅", "%s㎡ → 약 %s㎡" % (f0(SRES), f0(round(SRES - (SB1 - SB0), -2)))),
         ("평균 층수", "%.1f층 → %.1f층 (최고 7층은 4~5층으로)" % (SG / SB0, SG / SB1)),
         ("지정 비움(지킴)", "%s㎡ — 시민광장·역전광장·그레이트 코트·중정·마당" % f0(SOP))]
pg.rect(TX, by, sum(wd), 22.0, fc="#F3F5F8", z=5); pg.rect(TX, by, 1.4, 22.0, fc=RED, z=6)
for i, (k_, v_) in enumerate(items):
    pg.t(TX + 4, by + 5.0 + i * 6.0, k_, fs=10, bold=True, c=RED if i == 0 else INK, z=6); pg.t(TX + 38, by + 5.0 + i * 6.0, v_, fs=10, z=6)
# 범례
ly = by + 27.0
LG = [(FIGC, "건물"), (OPC, "형태 있는 비움(광장·중정·코트)"), (RESC, "획지 안 남은 땅 — 채울 곳"), (tint(PARKC, 0.1), "공원·선형공원"), (tint(BLUE, 0.55), "보행축"), (AXISC, "통경축(A안)")]
for i, (c, t_) in enumerate(LG):
    col_, row_ = divmod(i, 3)
    x_ = TX + col_ * 84; y_ = ly + row_ * 5.6
    pg.rect(x_, y_ - 1.6, 7, 3.2, fc=c, ec="#bbbbbb", lw=0.2, z=31); pg.t(x_ + 9.5, y_, t_, fs=10, z=31)
save(pg, "R3_건폐율050")
