"""R1 화랑로 A안 — 차는 역전광장에서 멈추고, 동쪽은 폭 20 m 보행 통경축(2026-10-15 사용자 확정)
- 위: 현재(중간마감 D3) — 동서 도로 20 m 차량 관통, 차량 진입 ⑥·⑦이 동서 도로에서
- 아래: A안 — 같은 띠를 보행 통경축으로, 서쪽 끝은 역전광장과 합친 '화랑로 끝 광장', 차량 정지·승하차 베이는 원화로 쪽
  진입 ⑥ → 서측 원화로(획지 7), ⑦ → 동측 외곽도로(획지 13)
- 구 역사는 계획 모델 배치 그대로(2026-10-15 사용자 결정 — 실제 위치 점선·확인 박스는 뺐다)
- 오른쪽: 단면 비교(1:400, 가로 = 세로) · 바뀌는 것 · 근거/반대 근거 · 참고 사례"""
from k0 import *

ENTS = entries_g3m()
# A안 진입 ⑥·⑦ 재배치(제안) — ⑥ 서측 원화로 → 획지 7 서변, ⑦ 동측 외곽도로 → 획지 13 동변
NEW6 = dict(p=entry_on(7, (100, 418), (1, 0)) - np.array([5.0, 0]), d=np.array([1.0, 0]), no=7, road="서측 원화로")
NEW7 = dict(p=entry_on(13, (405, 292), (-1, 0)) + np.array([5.0, 0]), d=np.array([-1.0, 0]), no=13, road="동측 외곽도로")
ENTS_A = [e for e in ENTS] ; ENTS_A[5] = NEW6; ENTS_A[6] = NEW7

# 화랑로 끝 광장 = 역전광장 + 화랑로 띠 서쪽 끝(역전광장 동변까지) + 그 사이 보도
PLZ = {p["name"]: p["g"] for p in S["PLZ"]}
EKI = PLZ["역전광장"]
x_e = EKI.bounds[2]
TERM = unary_union([EKI, EWB.intersection(box(0, 0, x_e, 2000)), box(EKI.bounds[0], EKI.bounds[3], x_e, EWB.bounds[1]).intersection(B)])
CORR = EWB.difference(TERM)
A_TERM = TERM.area
A_EW = EWB.area
CAR_NOW = sum(g.area for g in R.values()); CAR_A = CAR_NOW - A_EW
PED_NOW = sum(OP[k]["g"].area for k in "DEF") + S["PATH8"].area; PED_A = PED_NOW + A_EW
print("term %.0f ew %.0f car %.0f→%.0f ped %.0f→%.0f" % (A_TERM, A_EW, CAR_NOW, CAR_A, PED_NOW, PED_A))

pg = Page()
pg.header("Critique Response : Hwarang-ro", "Hwarang-ro Terminus", "화랑로 A안 — 차는 역전광장에서 멈춘다",
          sub="화랑로는 역으로 가는 길이다 — 부지 안 차량 관통을 없애고, 같은 20 m 띠를 동쪽 황오동까지 이어지는 보행 통경축으로 바꾼다")
EXT = (-110, 470, 228, 472)


def plan(y_mm, mode):
    ax = pg.plan_ax(4, y_mm, 156, 64, EXT)
    base(ax)
    site(ax, ew_as_road=(mode == "now"))
    stations(ax)
    pagoda(ax, label=(mode == "A"))
    if mode == "now":
        # 동서 도로 강조 + 보행 2등 축 이음매(남북축 남단 × 동서 도로 × 사선축 북단)
        fill(ax, EWB, fc="#3f3f3f", z=1.7)
        lab(ax, 340, 374, "동서 도로 20 m — 차량 관통", "#3f3f3f")
        ax.add_patch(Circle((271, 343), 26, fc="none", ec=RED, lw=1.3, ls=(0, (3, 1.6)), zorder=9))
        lab(ax, 249, 432, "보행축 이음매 단절", RED, ha="right"); ax.plot([250, 258], [426, 366], color=RED, lw=0.6, zorder=9)
        lab(ax, 271, 455, "남북 보행축", BLUE, rot=0)
        lab(ax, 236, 262, "사선 보행축", BLUE, rot=57.4)
        entries = ENTS
    else:
        fill(ax, CORR, fc=AXISC, ec="#cdbf9f", lw=0.4, z=1.7)
        fill(ax, TERM, fc="#E8D5A8", ec="#b89c5e", lw=0.6, z=1.72)
        for yy in (EWB.bounds[1] + 3.0, EWB.bounds[3] - 3.0):                 # 가로수 2열(8 m 간격)
            for x in np.arange(x_e + 6, 388, 8.0):
                if not (GATE_X[0] < x < GATE_X[1]): ax.add_patch(Circle((x, yy), 2.3, fc="#7dbb5c", ec="white", lw=0.3, zorder=1.8))
        for x in (x_e + 1.5, 389.5):                                         # 볼라드(일반 차량 차단)
            for yy in np.linspace(EWB.bounds[1] + 2, EWB.bounds[3] - 2, 5): ax.add_patch(Circle((x, yy), 1.1, fc=INK, zorder=1.9))
        # 차량 정지선(화랑로 × 원화로) · 승하차·관광버스 베이
        ax.plot([104.5, 104.5], [EWB.bounds[1] - 1, EWB.bounds[3] + 1], color=RED, lw=3.0, zorder=9, solid_capstyle="butt")
        bay = box(108.2, 262, 115.6, 326).intersection(B.buffer(1.5))
        fill(ax, bay, fc="#8d8d88", ec="white", lw=0.4, z=8.5)
        # 통경축 시선(서 → 동)
        ax.add_patch(MPoly([(-95, HWARANG_Y), (470, HWARANG_Y - 21), (470, HWARANG_Y + 21)], closed=True, fc="#F2C14E", ec="none", alpha=0.20, zorder=1.75))
        ax.add_patch(FancyArrowPatch((395, HWARANG_Y), (466, HWARANG_Y), arrowstyle="-|>,head_length=5,head_width=3", color="#b07d10", lw=1.4, zorder=9, mutation_scale=1.0))
        lab(ax, 300, HWARANG_Y, "보행 통경축 20 m", "#6b5320", stroke=AXISC)
        lab(ax, 432, HWARANG_Y + 13, "황오동", "#6b5320")
        lab(ax, 150, 270, "화랑로 끝 광장", "#6b5320", stroke="#E8D5A8")
        lab(ax, 96, HWARANG_Y + 15, "차량 정지", RED, ha="right")
        lab(ax, 98, 290, "승하차·버스 베이", "#555", ha="right")
        lab(ax, 236, 262, "사선 보행축", BLUE, rot=57.4)
        lab(ax, 271, 455, "남북 보행축", BLUE)
        entries = ENTS_A
    lab(ax, -70, HWARANG_Y + 13, "화랑로", "#7d7d78")
    lab(ax, 92, 450, "원화로", "#7d7d78", rot=90)
    for i, e in enumerate(entries):
        c = e["p"]
        if not (EXT[0] < c[0] < EXT[1] and EXT[2] < c[1] < EXT[3]): continue
        hi = i in (5, 6)
        tri(ax, c, e["d"], col=ENTRY if (hi or mode == "A") else tint(ENTRY, 0.45))
        tp = c - e["d"] * 20.0 + (np.array([0, -14.0]) if abs(e["d"][0]) > 0.9 else np.array([16.0, 0]))
        lab(ax, tp[0], tp[1], str(i + 1), ENTRY if hi or mode == "A" else tint(ENTRY, 0.45))
    north_scale(ax, -100, 238, label_m=(0, 50, 100), fs=10, north_at=(450, 248))
    return ax


ax1 = plan(34, "now")
ax2 = plan(103, "A")
pg.top()
tag(pg, 6, 35, "현재 · 중간마감안", fc="#555555")
tag(pg, 6, 104, "A안 · 차는 역에서 멈춘다", fc="#8a6d2e")

# ── 범례(평면 아래) ──
LG = [("fill", CARC, "차량 가로"), ("fill", AXISC, "보행 통경축(A안)"), ("fill", "#E8D5A8", "화랑로 끝 광장(A안)"),
      ("fill", tint(BLUE, 0.35), "보행 가로(2등)"), ("fill", "#c4c4bf", "계획 건물"), ("fill", "#B97A4E", "구 역사(존치)"),
      ("tri", ENTRY, "차량 진입(번호 = D3)"), ("bar", RED, "차량 정지 · ● 볼라드"),
      ("pag", "#5a4632", "황오동 삼층석탑(문화재자료 8호)"), ("bnd", RED, "구역 경계")]
lx, ly = 6, 175
for i, (k, c, t) in enumerate(LG):
    col, row = divmod(i, 6)
    x_ = lx + col * 80; y_ = ly + row * 5.6
    if k == "fill": pg.rect(x_, y_ - 1.6, 7, 3.2, fc=c, ec="#bbbbbb", lw=0.2, z=31)
    elif k == "dash": pg.line([x_, x_ + 7], [y_, y_], c=c, lw=1.0, z=31, ls=(0, (2, 1.2)))
    elif k == "tri": pg.ax.add_patch(MPoly([(x_ + 1.7, y_ + 1.6), (x_ + 5.3, y_ + 1.6), (x_ + 3.5, y_ - 1.7)], closed=True, fc=c, zorder=31))
    elif k == "bar": pg.rect(x_ + 2.6, y_ - 2.0, 1.8, 4.0, fc=c, z=31)
    elif k == "pag": pg.ax.add_patch(MPoly([(x_ + 3.5, y_ - 1.8), (x_ + 1.4, y_ + 1.6), (x_ + 5.6, y_ + 1.6)], closed=True, fc=c, zorder=31))
    elif k == "bnd": pg.line([x_, x_ + 7], [y_, y_], c=c, lw=0.8, z=31, ls=(0, (3, 1.5)))
    pg.t(x_ + 9.5, y_, t, fs=10, z=31)

# ── 오른쪽 1: 단면 비교 ──
RX = 168
pg.t(RX, 37, "단면 비교 — 1:400, 가로 = 세로 (획지선 사이 30 m)", fs=10, bold=True)
s = 2.5; GY = 79.0


def section(x0, elems, title, c):
    pg.t(x0, 44.5, title, fs=10, bold=True, c=c)
    xx = x0
    for nm, w, kind in elems:
        pg.rect(xx, GY, w * s, 1.6, fc=SECC.get(kind, "#ddd"), ec="white", lw=0.4, z=6)
        cx = xx + w * s / 2
        pg.t(cx, GY + 5.0, nm, fs=10, ha="center", z=7); pg.t(cx, GY + 10.0, "%g" % w, fs=10, ha="center", z=7, c=GREY)
        xx += w * s
    pg.line([x0 - 3, xx + 3], [GY, GY], c=INK, lw=0.8, z=8)
    return xx


x_end = section(RX, [("보도", 5, "보도"), ("차도", 20, "차도"), ("보도", 5, "보도")], "현재 · 동서 도로", INK)
for dx in (3.5, 8.5, 12.5, 17.0): car(pg, RX + (5 + dx) * s, GY, s)
for dx in (2.0, 3.6): person(pg, RX + dx * s, GY, s)
person(pg, RX + 27.5 * s, GY, s)
pg.ax.add_patch(FancyArrowPatch((x_end + 5, GY - 10), (x_end + 22, GY - 10), arrowstyle="-|>,head_length=2.2,head_width=1.4", color=INK, lw=1.1, zorder=8, mutation_scale=1.0))
X2 = x_end + 27
x_end2 = section(X2, [("보행", 5, "보도"), ("식재", 4, "식재"), ("보행·비상", 12, "통경축"), ("식재", 4, "식재"), ("보행", 5, "보도")], "A안 · 보행 통경축", "#8a6d2e")
for dx in (7.0, 23.0): tree(pg, X2 + dx * s, GY, s)
for dx in (1.6, 10.5, 12.2, 15.0, 19.0, 28.0): person(pg, X2 + dx * s, GY, s)
pg.ax.add_patch(FancyBboxPatch((X2 + 13.6 * s, GY - 2.6 * s), 6.0 * s, 2.3 * s, boxstyle="round,pad=0,rounding_size=0.6", fc="none", ec=RED, lw=0.7, ls=(0, (2, 1)), zorder=11))
pg.t(X2 + 9.0 * s, GY - 27.5, "비상·조업 차량만(시간제)", fs=10, c=RED, z=12)
pg.line([X2 + 16.6 * s, X2 + 16.6 * s], [GY - 25.2, GY - 2.8 * s], c=RED, lw=0.5, z=11)

# ── 오른쪽 2: 바뀌는 것 ──
ty = 96.0
cols = ["항목", "현재", "A안"]; wd = [74, 76, 78]
rows = [["차량 도로 면적", "%s㎡ (구역의 %.1f%%)" % (f0(CAR_NOW), CAR_NOW / TOT["boundary"] * 100), "%s㎡ (%.1f%%)" % (f0(CAR_A), CAR_A / TOT["boundary"] * 100)],
        ["보행자전용도로·광장", "%s㎡ (%.1f%%)" % (f0(PED_NOW), PED_NOW / TOT["boundary"] * 100), "%s㎡ (%.1f%%)" % (f0(PED_A), PED_A / TOT["boundary"] * 100)],
        ["부지 안 화랑로 차량 연장", "274 m", "0 m"],
        ["보행 2등 축과 차도 교차", "1곳 (남북축·사선축 이음매)", "0곳"],
        ["차량 진입 ⑥ · ⑦", "동서 도로 → 획지 7 · 13", "원화로 → 7 · 동측 외곽 → 13"],
        ["화랑로 끝 광장", "역전광장 %s㎡" % f0(EKI.area), "약 %s㎡ (역전광장 포함)" % f0(round(A_TERM, -1))]]
yy = table(pg, RX, ty, cols, rows, wd, rh=6.0, fs=10, aligns=["left", "left", "left"])

# ── 오른쪽 3: 근거 / 반대 근거 ──
by = yy + 4.5; bw = (sum(wd) - 4) / 2
h1 = box_note(pg, RX, by, bw, "보이는 축이 필요하다는 근거", [
    "경관계획: 화랑로 통경축은 폐 경주역 부지 개발 시 반드시 반영 [T1 · A-009 p.206]",
    "전략계획: 역사·전면 오픈스페이스, 화랑로 조망축 보존 [T1 · A-006 p.119]",
    "1936년 역 이전 때 읍성 남벽 자리에 낸 길 — 역과 한 쌍 [T3 · 김신재 2013]"], c="#8a6d2e", bullets=True)
h2 = box_note(pg, RX + bw + 4, by, bw, "차량 관통에 반대하는 근거", [
    "발주 연구: 화랑로 차량 통행이 원도심 중심부를 분리 [T2 · 417쪽 연구 인쇄쪽 51]",
    "주말 낮/심야 속도비 0.74 — 비교한 8개 도로 중 가장 낮음 [자체 산출 · 표본 16일]",
    "2023 기본계획안: 화랑로 연장에는 구 역사 이전 필요 [T2 · 김성주 p.26]"], c=CARC, bullets=True)
cy = by + max(h1, h2) + 3.5
box_note(pg, RX, cy, sum(wd), "참고 — 도쿄역 마루노우치 역전광장", [
    "황궁에서 오는 교코도리(1926 완성) 축이 복원된 역사 정면에서 끝나고, 역 앞 약 6,500㎡는 보행 전용 광장이다(2017.12 준공). 차는 광장 옆에서 멈춘다 [T4 · Wikipedia·수상관저]."], c="#8a6d2e")
save(pg, "R1_화랑로A안")
