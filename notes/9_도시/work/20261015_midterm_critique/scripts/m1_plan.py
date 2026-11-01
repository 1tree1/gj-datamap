"""M1 매스 평면(16:9) — v1: 지금 · v1 나란히 / v1-b: v1 · v1-b 나란히 + 획지별 결과표
사용: MASSVAR=v1|v1b python m1_plan.py   입력: ../mass_v1(b)/data/mass_v1(b).pkl"""
from k0 import *

VAR = os.environ.get("MASSVAR", "v1")
VDIR = {"v1": "mass_v1", "v1b": "mass_v1b"}


def load(var): return pickle.load(open(os.path.join(K0DIR, "..", VDIR[var], "data", "mass_%s.pkl" % var), "rb"))


MV = load(VAR)
BLD2, RES, DECKS, TT = MV["BLD"], MV["RES"], MV["DECKS"], MV["TOT"]
OUT1 = os.path.join(K0DIR, "..", VDIR[VAR]); os.makedirs(OUT1, exist_ok=True)
MAINC = lambda b: LOTCOL.get(b["main"], "#999999")


def plan(x_mm, blds, mv=None):
    """mv=None: 중간마감(지금). mv: 매스 결과(v1·v1-b)"""
    Sx = mv["S"] if mv else S
    EXT = (95, 420, 40, 1010)
    ax = pg.plan_ax(x_mm, 36, 70, 184, EXT)
    base(ax, parcels=False, ctx_fc="#e7e7e4")
    for g in BLK: fill(ax, g, fc="#f1f1ee", ec="none", z=1)
    fill(ax, Sx["WALK"], fc="#e6e6e2", z=1.1)
    for p in S["PARKS"]: fill(ax, p["g"], fc=tint(PARKC, 0.15), z=1.15)
    fill(ax, OP["D"]["g"], fc=tint(PARKC, 0.15), z=1.2)
    for k in "EF": fill(ax, OP[k]["g"], fc=tint(BLUE, 0.6), z=1.2)
    fill(ax, S["PATH8"], fc=tint(PURP, 0.5), z=1.2)
    for p in (S["PLZ"] if mv is None else Sx["PLZ"]):
        if p["kind"] in ("광장", "코트", "중정"): fill(ax, p["g"], fc="#EDE3CB", z=1.25)
    if mv is not None:
        fill(ax, mv.get("CORR", CORR), fc=AXISC, ec="#cdbf9f", lw=0.4, z=1.7)
        fill(ax, mv.get("TERM", TERM), fc="#E8D5A8", ec="#b89c5e", lw=0.6, z=1.72)
        for g in Sx["ROADS"].values(): fill(ax, g, fc=CARC, z=1.4)
    else:
        for g in R.values(): fill(ax, g, fc=CARC, z=1.4)
    if mv is not None and "LOTS" in Sx and mv.get("VARIANT") == "v1-b":
        for l in Sx["LOTS"]:
            if l["no"] in (7, 9):
                xs, ys = l["g"].exterior.xy; ax.plot(xs, ys, color="#7a4a26", lw=0.9, ls=(0, (3, 1.5)), zorder=3)
    for b in blds:
        fill(ax, b["g"], fc=MAINC(b), ec="white", lw=0.35, z=2)
    if mv is not None:
        for d in mv["DECKS"]:
            for p in polys(d["g"]):
                xs, ys = p.exterior.xy; ax.plot(xs, ys, color=PLATC, lw=1.0, zorder=4)
                for ring_ in p.interiors:
                    xs, ys = ring_.xy; ax.plot(xs, ys, color=PLATC, lw=1.0, zorder=4)
        if "PASS" in mv:
            xs, ys = mv["PASS"].exterior.xy; ax.plot(xs, ys, color="#b07d10", lw=0.9, zorder=5)
    for b in blds:
        if b["g"].area >= 500 and b["name"] != "구 경주역사":
            c = polylabel(max(polys(b["g"]), key=lambda q: q.area), 0.5)
            ax.text(c.x, c.y, str(b["floors"]), fontsize=10, ha="center", va="center", color=INK, zorder=6, path_effects=halo(1.6))
    xs, ys = B.exterior.xy; ax.plot(xs, ys, color=RED, lw=0.8, ls=(0, (4, 2)), zorder=6)
    if mv is not None: pagoda(ax, label=False)
    north_scale(ax, 290, 62, label_m=(0, 50, 100), fs=10, north_at=(118, 930))
    return ax


pg = Page()
if VAR == "v1":
    pg.header("Critique Response : Massing v1", "Massing v1 · Coverage 0.50", "매스 재작업 v1 — 같은 연면적을 낮고 넓게",
              sub="형태 있는 비움은 그대로 두고 획지 안 남은 땅을 채운다 — 획지 건폐율 %.2f → %.2f · 평균 %.1f → %.1f층 · 최고 5층(20 m) · 숫자 = 층수"
              % (TT["ba0"] / TT["lot"], TT["ba"] / TT["lot"], TT["gfa0"] / TT["ba0"], TT["gfa"] / TT["ba"]))
    plan(2, BLD, None); plan(72, BLD2, MV)
    pg.top(); tag(pg, 4, 37, "지금 · 중간마감", fc="#555555"); tag(pg, 74, 37, "v1 · 건폐율 0.50", fc=RED)
else:
    V1 = load("v1")
    pg.header("Critique Response : Massing v1-b · 검토안", "Massing v1-b · Station In Place", "검토안 — 구 역사를 실제 위치에 둔 경우",
              sub="화랑로 → 역 앞마당·삼층석탑 → 대합실 관통 통로 → 옛 1번 승강장 → 플랫폼 광장 — 획지 7·9와 획지선을 다시, 획지 건폐율 %.2f · 평균 %.1f층 · 숫자 = 층수"
              % (TT["ba"] / TT["lot"], TT["gfa"] / TT["ba"]))
    plan(2, V1["BLD"], V1); plan(72, BLD2, MV)
    pg.top(); tag(pg, 4, 37, "v1 · 계획 모델 역사", fc="#555555"); tag(pg, 74, 37, "v1-b · 실제 위치", fc="#7a4a26")

# ── 획지별 결과표 ──
TX = 146
cols = ["획지", "형태", "동", "건축면적㎡", "GSI", "연면적㎡", "평균 층", "최고"]
wd = [30, 34, 15, 41, 25, 44, 18, 44]
rows = []; chips = {}
for i, r in enumerate(RES):
    A0 = r.get("A0", r["A"])
    rows.append(["%d %s" % (r["no"], SHORT[r["no"]]), r["form"] if r["no"] not in (2, 8) else "유지", "%d→%d" % (r["n0"], r["n"]),
                 "%s → %s" % (f0(r["ba0"]), f0(r["ba"])), "%.2f→%.2f" % (r["ba0"] / A0, r["ba"] / r["A"]),
                 "%s → %s" % (f0(r["gfa0"]), f0(r["gfa"])), "%.1f" % (r["gfa"] / r["ba"]), "%d→%d층 · %.0f m" % (r["f0max"], r["fmax"], r["hmax"])])
    chips[i] = LOTCOL[[l for l in S["LOTS"] if l["no"] == r["no"]][0]["cat"]]
nB0 = sum(r["n0"] for r in RES); nB = sum(r["n"] for r in RES)
f0max = max(r["f0max"] for r in RES); fmax = max(r["fmax"] for r in RES); hmax = max(r["hmax"] for r in RES)
rows.append(["합계", "", "%d→%d" % (nB0, nB), "%s → %s" % (f0(TT["ba0"]), f0(TT["ba"])), "%.2f→%.2f" % (TT["ba0"] / TOT["lot"], TT["ba"] / TT["lot"]),
             "%s → %s" % (f0(TT["gfa0"]), f0(TT["gfa"])), "%.1f" % (TT["gfa"] / TT["ba"]), "%d→%d층 · %.0f m" % (f0max, fmax, hmax)])
yy = table(pg, TX, 36.0, cols, rows, wd, rh=5.9, fs=10, aligns=["left", "left", "center", "right", "center", "right", "center", "left"],
           sub_rows=(len(rows) - 1,), color_chip=chips)
pk = sum(p["g"].area for p in S["PARKS"])
pg.t(TX, yy + 4.2, "획지 합 %s㎡ (구역 %s㎡ 중 공원 %s㎡ · 도로·보행 %s㎡ 제외) · 연면적 차 %+d㎡ = 라이닝 상가(획지 13) 신설" % (
    f0(TT["lot"]), f0(TOT["boundary"]), f0(pk), f0(TOT["boundary"] - TT["lot"] - pk), round(TT["gfa"] - TT["gfa0"])), fs=10, c=GREY)

# ── 규칙 · 확인할 것 ──
by = yy + 9.5; bw = (sum(wd) - 4) / 2
if VAR == "v1":
    R_ = ["층수는 최고 5층(20 m, 고도지구 20 m). 동측 경계 30 m 안은 3층까지(황오동 1층 93%)",
          "공공 공간(보행축·선형공원·광장)에 가까운 동부터 층을 올린다",
          "연면적은 획지별로 맞추고, 끝수는 한 동의 꼭대기 층을 안으로 물려 맞춘다",
          "지정 비움(광장·중정·코트·마당)과 삼층석탑 둘레 12 m는 비운다"]
    C_ = ["획지 1 공공청사 둘레 깊이 28 m — 아트리움을 두거나 두 줄 동으로 나눌지",
          "획지 2는 남은 땅이 좁은 띠라 유지, 목표와의 차 335㎡는 획지 1로 옮김",
          "획지 9 상생동을 통경축·관문 쪽 1~2층으로 옮김 — 역사 주변 높이 검토",
          "판(①②③) 높이와 허용기준 ⑤ 8 m의 적용 구역"]
else:
    r9 = [r for r in RES if r["no"] == 9][0]; r7 = [r for r in RES if r["no"] == 7][0]
    R_ = ["구 역사는 실제 위치 그대로, 1층 대합실을 폭 8 m 24시간 통로로",
          "역 앞마당·옛 1번 승강장·플랫폼 광장을 획지 9의 지정 비움으로",
          "역사 25 m 안은 2층, 그 밖은 3층까지 — 역사보다 낮은 바탕",
          "획지 7·9만 다시 짓고 나머지 획지는 v1 그대로"]
    C_ = ["획지선: 획지 9 %s → %s㎡, 획지 7 %s → %s㎡" % (f0(r9["A0"]), f0(r9["A"]), f0(r7["A0"]), f0(r7["A"])),
          "획지 9 순획지 건폐율 %.2f — 전체 0.50을 맞추려고 역사 주변을 1~3층으로 채움" % (r9["ba"] / (r9["A"] - r9["opA"])),
          "대합실 관통은 철도기념물(코레일) 1층 개조 — 소유자 협의",
          "그레이트 코트·유리 지붕은 없앰 · 판 높이와 허용기준 ⑤ 8 m"]
h1 = box_note(pg, TX, by, bw, "매스 규칙" if VAR == "v1" else "v1-b에서 바꾼 것", R_, c=SLATE, bullets=True)
h2 = box_note(pg, TX + bw + 4, by, bw, "확인할 것", C_, c=RED, bullets=True)
ly = by + max(h1, h2) + 5.0
LG = [("공공업무", "공공업무"), ("업무·창업", "업무·창업"), ("문화", "문화·집회"), ("창작", "창작·공방"), ("판매", "근린생활"), ("생활SOC", "체육·복지"),
      ("주거", "주거"), ("역사", "역사유산"), ("방문자", "관광"), ("주차", "주차·교통")]
ex = TX
for k, t_ in LG:
    pg.rect(ex, ly - 1.6, 4.0, 3.2, fc=LOTCOL[k], ec="#9a9a9a", lw=0.2, z=14); tt_ = pg.t(ex + 5.2, ly, t_, fs=10, z=14); ex += 5.2 + pg.wmm(tt_) + 3.2
ly += 6.0
pg.line([TX, TX + 6], [ly, ly], c=PLATC, lw=1.2, z=14); pg.t(TX + 8, ly, "판(①②③) 윤곽", fs=10, z=14)
pg.rect(TX + 40, ly - 1.6, 6, 3.2, fc=AXISC, ec="#cdbf9f", lw=0.3, z=14); pg.t(TX + 48, ly, "통경축(A안)", fs=10, z=14)
pg.rect(TX + 78, ly - 1.6, 6, 3.2, fc="#EDE3CB", z=14); pg.t(TX + 86, ly, "광장·중정·코트", fs=10, z=14)
if VAR == "v1b":
    pg.line([TX + 120, TX + 126], [ly, ly], c="#7a4a26", lw=1.0, z=14, ls=(0, (3, 1.5))); pg.t(TX + 128, ly, "새 획지선(7·9)", fs=10, z=14)
    pg.line([TX + 165, TX + 171], [ly, ly], c="#b07d10", lw=1.0, z=14); pg.t(TX + 173, ly, "대합실 통로", fs=10, z=14)
NAME = {"v1": "M1_매스재작업_평면", "v1b": "M1b_매스변형v1b_평면"}[VAR]
pg.fig.savefig(os.path.join(OUT1, NAME + ".png"), dpi=240, facecolor="white")
pg.fig.savefig(os.path.join(OUT1, NAME + ".pdf"), facecolor="white"); plt.close(pg.fig); print("saved", NAME)
