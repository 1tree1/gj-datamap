"""R4 검토 — 구 경주역사를 원래 위치에 둔다면(2026-10-15 사용자 질문, 검토용 — 현재 결정은 계획 모델 배치 유지)
- 왼쪽: 매스 v1(계획 모델 배치) · 오른쪽: 실제 위치(콘타 모델 '빌딩', V-World 연속지적 정합)
- 실제 역사: 88.7 × 24.1 m, 긴 변 남북, 서쪽(원화로) 정면. 화랑로 축(y≈342)이 서쪽 정면에 닿는다
- 겹침·충돌·비는 땅·역 앞마당·옛 승강장 자리를 표시"""
from k0 import *

MV = pickle.load(open(os.path.join(K0DIR, "..", "mass_v1", "data", "mass_v1.pkl"), "rb"))
BLDv = MV["BLD"]
WEDGE = B.exterior.intersection(box(90, 280, 125, 375)).bounds[2]                       # 원화로 쪽 대지 경계 x
FORE = box(WEDGE, ST_REAL.bounds[1], ST_REAL.bounds[0], ST_REAL.bounds[3]).intersection(B).difference(ST_REAL)
CONF = [b for b in BLDv if b["name"] != "구 경주역사" and (ST_REAL.buffer(6).intersection(b["g"]).area > 5 or FORE.intersection(b["g"]).area > 5)]   # 역사 6 m 안 · 역 앞마당 안
PLAT1 = box(ST_REAL.bounds[2] + 2, ST_REAL.bounds[1] - 4, ST_REAL.bounds[2] + 14, ST_REAL.bounds[3] + 4)   # 옛 1번 승강장 자리(역사 동쪽, 선로 x 181–243 앞)
CORR_R = CORR.difference(box(0, 0, ST_REAL.bounds[2] + 3, 2000))
OVL = {"화랑로 끝 광장": ST_REAL.intersection(TERM).area, "역전광장": ST_REAL.intersection(EKI).area, "동서 띠(통경축)": ST_REAL.intersection(EWB).area,
       "획지 9": ST_REAL.intersection([l["g"] for l in S["LOTS"] if l["no"] == 9][0]).area, "획지 7": ST_REAL.intersection([l["g"] for l in S["LOTS"] if l["no"] == 7][0]).area}
shift = Point(ST_REAL.centroid).distance(ST_PLAN.centroid)
print("conflicts", [(b["name"], b["floors"], round(b["g"].area)) for b in CONF], "fore %.0f" % FORE.area, {k: round(v) for k, v in OVL.items()})

pg = Page()
pg.header("Critique Response : Station In Place", "Station In Place", "구 역사를 원래 위치에 둔다면",
          sub="검토안 — 결정은 계획 모델 배치 유지(v1, 2026-10-15). 실제 역사는 화랑로 축 위에 있어, 화랑로가 삼층석탑을 지나 역 정면에서 끝난다(1936년 배치)")
EXT = (55, 335, 180, 485)


def plan(x_mm, mode):
    ax = pg.plan_ax(x_mm, 34, 96, 106, EXT)
    base(ax, parcels=True)
    site(ax, ew_as_road=False, bld=False, open_alpha=0.5)
    if mode == "now":
        a_corridor(ax, trees=True, bollards=False)
        for b in BLDv:
            if b["name"] == "구 경주역사": continue
            fill(ax, b["g"], fc=LOTCOL.get(b["main"], "#999"), ec="white", lw=0.35, z=2)
        fill(ax, ST_PLAN, fc="#B97A4E", ec="white", lw=0.5, z=3)
        for d in MV["DECKS"][:2]:
            for p in polys(d["g"]): xs, ys = p.exterior.xy; ax.plot(xs, ys, color=PLATC, lw=1.1, zorder=4)
        ax.add_patch(FancyArrowPatch((EXT[0] + 4, HWARANG_Y), (EKI.bounds[2] - 2, HWARANG_Y), arrowstyle="-|>,head_length=4,head_width=2.6", color="#b07d10", lw=1.4, zorder=9, mutation_scale=1.0))
        lab(ax, 175, 266, "구 역사(계획 모델)", "#7a4a26")
        lab(ax, 150, 300, "화랑로 끝 광장", "#6b5320", stroke="#E8D5A8")
        lab(ax, 236, 252, "① 캐노피", PLATC, rot=57.4)
    else:
        fill(ax, CORR_R, fc=AXISC, ec="#cdbf9f", lw=0.4, z=1.7)
        fill(ax, FORE, fc="#E8D5A8", ec="#b89c5e", lw=0.6, z=1.72)
        fill(ax, EKI.difference(ST_REAL), fc="#F1E8D2", ec="#cdbf9f", lw=0.4, z=1.71)
        for b in BLDv:
            if b["name"] == "구 경주역사": continue
            bad = b in CONF
            fill(ax, b["g"], fc=LOTCOL.get(b["main"], "#999"), ec=RED if bad else "white", lw=1.0 if bad else 0.35, z=2, alpha=0.45 if bad else 1.0)
            if bad: fill(ax, b["g"], fc="none", ec=RED, lw=0.0, z=2.1, hatch="////")
        xs, ys = ST_PLAN.exterior.xy; ax.plot(xs, ys, color="#2f8f3a", lw=1.1, ls=(0, (2.2, 1.4)), zorder=5)
        fill(ax, ST_REAL, fc="#B97A4E", ec="white", lw=0.6, z=3)
        xs, ys = PLAT1.exterior.xy; ax.plot(xs, ys, color=PLATC, lw=1.2, ls=(0, (3, 1.6)), zorder=5)
        ax.add_patch(FancyArrowPatch((EXT[0] + 4, HWARANG_Y), (ST_REAL.bounds[0] - 1, HWARANG_Y), arrowstyle="-|>,head_length=4,head_width=2.6", color="#b07d10", lw=1.4, zorder=9, mutation_scale=1.0))
        ax.plot([ST_REAL.bounds[0], ST_REAL.bounds[2] + 16], [HWARANG_Y, HWARANG_Y], color="#b07d10", lw=1.0, ls=(0, (2, 1.5)), zorder=9)
        lab(ax, 180, 298, "구 역사(실제 위치)", "#7a4a26", ha="left")
        ax.plot([171, 179], [300, 298], color="#7a4a26", lw=0.6, zorder=9)
        lab(ax, 128, 300, "역 앞마당", "#6b5320", rot=90, stroke="#E8D5A8")
        lab(ax, 205, 250, "비는 땅", "#2f8f3a")
        lab(ax, 208, 330, "옛 1번 승강장", PLATC, ha="left")
        lab(ax, 226, 344, "통로", "#8a6d2e", stroke=AXISC)
        cc = unary_union([b["g"] for b in CONF]); lab(ax, cc.centroid.x, cc.bounds[3] + 9, "충돌", RED)
    pagoda(ax, label=(mode != "now"), dx=-4, dy=14)
    lab(ax, 75, HWARANG_Y + 12, "화랑로", "#7d7d78")
    north_scale(ax, 240, 192, label_m=(0, 25, 50), fs=10, north_at=(318, 205))
    return ax


plan(2, "now"); plan(101, "real")
pg.top()
tag(pg, 4, 35, "지금 · 매스 v1", fc="#555555")
tag(pg, 103, 35, "원위치 검토", fc="#7a4a26")

# 범례
LG = [("fill", "#B97A4E", "구 역사"), ("dash", "#2f8f3a", "계획 모델 역사 자리 — 비는 땅"), ("fill", "#E8D5A8", "역 앞마당 · 화랑로 끝 광장"),
      ("fill", AXISC, "보행 통경축(A안)"), ("hatch", RED, "역사 6 m 안 · 역 앞마당 안 v1 동"), ("dashO", PLATC, "판 · 옛 1번 승강장 캐노피(제안)"),
      ("pag", "#5a4632", "황오동 삼층석탑(문화재자료 8호)"), ("arr", "#b07d10", "화랑로 축")]
for i, (k, c, t) in enumerate(LG):
    col, row = divmod(i, 4)
    x_ = 6 + col * 98; y_ = 147 + row * 5.6
    if k == "fill": pg.rect(x_, y_ - 1.6, 7, 3.2, fc=c, ec="#bbbbbb", lw=0.2, z=31)
    elif k == "dash": pg.line([x_, x_ + 7], [y_, y_], c=c, lw=1.0, z=31, ls=(0, (2, 1.2)))
    elif k == "dashO": pg.line([x_, x_ + 7], [y_, y_], c=c, lw=1.2, z=31, ls=(0, (3, 1.4)))
    elif k == "hatch": pg.rect(x_, y_ - 1.6, 7, 3.2, fc="white", ec=c, lw=0.8, z=31, hatch="////")
    elif k == "pag": pg.ax.add_patch(MPoly([(x_ + 3.5, y_ - 1.8), (x_ + 1.4, y_ + 1.6), (x_ + 5.6, y_ + 1.6)], closed=True, fc=c, zorder=31))
    elif k == "arr": pg.ax.add_patch(FancyArrowPatch((x_, y_), (x_ + 7, y_), arrowstyle="-|>,head_length=1.6,head_width=1.0", color=c, lw=1.0, zorder=31, mutation_scale=1.0))
    pg.t(x_ + 9.5, y_, t, fs=10, z=31)

# 좋아지는 것 · 다시 해야 하는 것(왼쪽 아래)
by = 172.0; bw = 95
box_note(pg, 3, by, bw, "좋아지는 것", [
    "화랑로 → 삼층석탑 → 역 정면: A안의 끝이 실제 건물이 된다(1936년 배치)",
    "옮기지 않으니 새 기초 굴착이 없다. 1단계 시굴도 구 역사 본관·전면 광장·플랫폼을 뺐다 [T2 · B-002]",
    "① 캐노피가 옛 1번 승강장 자리에 선다"], c="#2f8f3a", bullets=True)
box_note(pg, 101, by, bw, "다시 해야 하는 것", [
    "획지 9: 그레이트 코트·지역문화원 ㄷ자·상생동을 역사 위치에 맞춰 다시",
    "통경축 서쪽 끝: 대합실 관통 통로(9월 안 E-W2) 또는 남·북 우회",
    "v1 동 %d개 옮김(%s), 획지선(7·9·보도) 다시, 면적표 재산정" % (len(CONF), " · ".join(b["name"] for b in CONF))], c=RED, bullets=True)

# ── 오른쪽: 달라지는 것 ──
TX = 202
cols = ["항목", "지금 · 계획 모델", "원위치"]; wd = [36, 74, 85]
rows = [["역사 위치", "실제보다 남쪽 %d m · 34° 회전" % round(shift), "콘타 모델 · 지적 정합 위치"],
        ["화랑로 축의 끝", "화랑로 끝 광장(빈 땅)", "역사 서쪽 정면 · 앞에 석탑"],
        ["역 앞마당", "역전광장 %s㎡(역 남서쪽)" % f0(EKI.area), "원화로–역사 사이 %d m · %s㎡" % (round(ST_REAL.bounds[0] - WEDGE), f0(FORE.area))],
        ["삼층석탑과 역사", "%d m" % round(ST_PLAN.distance(PAGODA)), "%d m — 역 앞마당 안" % round(ST_REAL.distance(PAGODA))],
        ["통경축 서쪽", "원화로까지 이어짐", "역사에서 끊김 → 통로 필요"],
        ["① 캐노피", "사선 보행축 위(역사에서 %d m)" % round(ST_REAL.distance(MV["DECKS"][0]["g"])), "역사 동쪽 옛 승강장 자리"],
        ["겹치는 지정 공간", "-", "끝 광장 %s · 역전광장 %s㎡" % (f0(OVL["화랑로 끝 광장"]), f0(OVL["역전광장"]))],
        ["걸치는 획지", "획지 9 안", "획지 9 %s · 획지 7 %s㎡ · 보도" % (f0(OVL["획지 9"]), f0(OVL["획지 7"]))],
        ["v1 동 충돌", "-", " · ".join(b["name"] for b in CONF)],
        ["비는 땅(획지 9)", "-", "%s㎡ — 건폐율 맞추기 쉬워짐" % f0(ST_PLAN.area)]]
yy = table(pg, TX, 36.0, cols, rows, wd, rh=6.2, fs=10, aligns=["left", "left", "left"])
box_note(pg, TX, yy + 5.0, sum(wd), "근거", [
    "역 정면에서 끝나는 화랑로: 1936년 역 이전과 함께 읍성 남벽 자리에 낸 길 [T3 · 김신재 2013]",
    "전략계획: 역사와 전면 오픈스페이스 보존, 화랑로 조망축 보존 [T1 · A-006 p.119]",
    "2023 기본계획안은 화랑로 차량 연장 때문에 역사 이전을 전제했다 [T2] — A안에서는 그 이유가 없다",
    "9월 지구단위계획안 E-W2: 화랑로 → 구 역사(대합실 = 통로) → 플랫폼광장 → 황오동 [자체 · 2026-09-21]"], c=SLATE, bullets=True)
save(pg, "R4_구역사원위치검토")
