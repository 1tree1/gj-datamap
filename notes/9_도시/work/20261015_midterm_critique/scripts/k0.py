"""k0 — 크리틱 대응 다이어그램 공통(2026-10-15)
- 중간마감 다이어그램 도구(work/20261011_masterplan_rough/scripts/gkit.py)를 그대로 쓴다: 16:9 400×225 mm, 본문 최소 10 pt, 로컬 m 좌표(북쪽 위)
- 배경은 ctx_fixed.pkl(지적 정합)만 쓴다. 옛 planframe json은 34° 회전 오류라 쓰지 않는다
- 저장 위치만 이 폴더(diagrams/)로 바꾼다"""
import os, sys
K0DIR = os.path.dirname(os.path.abspath(__file__))
MR = os.path.abspath(os.path.join(K0DIR, "..", "..", "20261011_masterplan_rough", "scripts"))
sys.path.insert(0, MR)
from gkit import *                      # noqa: F401,F403  (Page·fill·context·table·text_block·wrap_mm·north_scale·S·B·BLD·TOT 등)
from matplotlib.collections import PatchCollection
from shapely.ops import polylabel, nearest_points

OUT = os.path.join(K0DIR, "..", "diagrams"); os.makedirs(OUT, exist_ok=True)
DS = pickle.load(open(os.path.join(D, "district.pkl"), "rb"))
CF = pickle.load(open(os.path.join(D, "ctx_fixed.pkl"), "rb"))
OP = {o["key"]: o for o in S["OPEN"]}
PK = {p["key"]: p for p in S["PARKS"]}
R = S["ROADS"]
LOT = {l["no"]: l for l in S["LOTS"]}
RG = unary_union(list(R.values()))
PED = unary_union([o["g"] for o in S["OPEN"]] + [S["PATH8"], S["WALK"]])
BLK = [g for g in polys(B.difference(RG).difference(PED)) if g.area > 200]

# 구 역사: 계획 모델의 배치(사용자 최종 3dm)와 실제 위치(콘타 모델 '빌딩', V-World 연속지적 정합)
ST_PLAN = [b for b in BLD if b["name"] == "구 경주역사"][0]["g"]
ST_REAL = [o["g"] for o in CF["B"] if o["inside"] and abs(o["g"].area - 1403) < 5][0]
# 황오동 삼층석탑(문화재자료 8호) — 부지 안
PAGODA = [h[0] for h in DS["HER"] if h[1] == "황오동삼층석탑" and h[2] == "문화재"][0].centroid
HWARANG_Y = 342.3                        # 화랑로 축(원화로 교차부, 상·하행 중심선 y 339·345의 가운데)
EWB = R["EW"]                           # 동서 도로 띠 y 333.7–353.7(폭 20 m) = 화랑로 연장선

GREEN = "#2f8f3a"; BLUE = "#1f6fbf"; LBLUE = "#7fa6d8"; PURP = "#7a5ab5"; CARC = "#636363"; ENTRY = "#D62828"
AXISC = "#EFE6D2"; WARM = "#E9A86A"; PLATC = "#D9480F"


def save(pg, name):
    pg.fig.savefig(os.path.join(OUT, name + ".png"), dpi=240, facecolor="white")
    pg.fig.savefig(os.path.join(OUT, name + ".pdf"), facecolor="white")
    plt.close(pg.fig); print("saved", name)


def base(ax, parcels=True, ctx_fc="#e2e2df"):
    """바탕 — 필지 윤곽·북천·주변 건물·간선 도로(흰 선)·화랑로"""
    (ex0, ex1), (ey0, ey1) = ax.get_xlim(), ax.get_ylim()
    win = box(ex0, ey0, ex1, ey1)
    fill(ax, win, fc="#f7f7f5", z=0.1)
    if parcels:
        ax.add_collection(PatchCollection([PathPatch(path_of(q)) for g, c in DS["PAR"] if g.intersects(win) for q in polys(g)],
                                          fc="none", ec="#e2e2de", lw=0.18, zorder=0.3))
    for g, c in DS["PAR"]:
        if c == "천" and g.intersects(win): fill(ax, g, fc="#d6e7f2", z=0.35)
    context(ax, (ex0, ex1, ey0, ey1), fc=ctx_fc, ec="none", z=0.5)
    for nm, gs in DS["ROADS"].items():
        for g in gs:
            if g.intersects(win):
                xs, ys = g.xy; ax.plot(xs, ys, color="#bdbdb8", lw=3.2, zorder=0.6, solid_capstyle="round"); ax.plot(xs, ys, color="white", lw=2.3, zorder=0.61, solid_capstyle="round")
    for g in DS["AXES"].get("화랑로", []):
        x0_, y0_, x1_, y1_ = g.bounds
        if g.intersects(win) and (y1_ - y0_) < 0.3 * max(x1_ - x0_, 1):
            xs, ys = g.xy; ax.plot(xs, ys, color="#bdbdb8", lw=3.2, zorder=0.6); ax.plot(xs, ys, color="white", lw=2.3, zorder=0.61)
    return win


def site(ax, ew_as_road=True, bld=True, open_alpha=0.55):
    """대지 — 가구·보도·보행 가로(위계 색, 옅게)·공원·계획 건물 윤곽·도로"""
    for g in BLK: fill(ax, g, fc="#ececea", ec="#c9c9c5", lw=0.4, z=1)
    fill(ax, S["WALK"], fc="#dcdcd8", z=1.1)
    for p in S["PARKS"]: fill(ax, p["g"], fc=tint(PARKC, 0.25), z=1.15)
    fill(ax, S["PATH8"], fc=PURP, alpha=open_alpha, z=1.25)
    fill(ax, OP["D"]["g"], fc=GREEN, alpha=open_alpha, z=1.3)
    fill(ax, OP["E"]["g"], fc=BLUE, alpha=open_alpha * 0.8, z=1.3)
    fill(ax, OP["F"]["g"], fc=BLUE, alpha=open_alpha * 0.55, z=1.3)
    if bld:
        for b in BLD:
            if b["name"] == "구 경주역사": continue
            fill(ax, b["g"], fc="#c4c4bf", ec="white", lw=0.4, z=1.4)
    for k, g in R.items():
        if k == "EW" and not ew_as_road: continue
        fill(ax, g, fc=CARC, z=1.6)
    xs, ys = B.exterior.xy; ax.plot(xs, ys, color=RED, lw=0.9, ls=(0, (4, 2)), zorder=6)


def stations(ax, real=False, plan_fc="#B97A4E"):
    """구 역사 — 계획 모델 배치(2026-10-15 사용자 결정: 이 배치 유지). real=True면 실제 위치(콘타 모델)를 붉은 점선으로 겹친다(검토용)"""
    fill(ax, ST_PLAN, fc=plan_fc, ec="white", lw=0.5, z=3)
    if real:
        xs, ys = ST_REAL.exterior.xy
        ax.plot(xs, ys, color=RED, lw=1.1, ls=(0, (2.2, 1.4)), zorder=7)


def pagoda(ax, label=True, dx=-6, dy=14):
    ax.add_patch(MPoly([(PAGODA.x, PAGODA.y + 7), (PAGODA.x - 5.5, PAGODA.y - 4), (PAGODA.x + 5.5, PAGODA.y - 4)], closed=True, fc="#5a4632", ec="white", lw=0.5, zorder=9))
    if label:
        ax.text(PAGODA.x + dx, PAGODA.y + dy, "삼층석탑", fontsize=10, color="#5a4632", fontweight="bold", ha="right", va="center", path_effects=halo(2.0), zorder=14)


def tri(ax, c, d, L_=15.0, col=ENTRY, z=17):
    d = np.array(d, float); d /= np.linalg.norm(d); n_ = np.array([-d[1], d[0]]); c = np.array(c, float)
    ax.add_patch(MPoly([tuple(c + d * L_ * 0.62), tuple(c - d * L_ * 0.38 + n_ * L_ * 0.5), tuple(c - d * L_ * 0.38 - n_ * L_ * 0.5)],
                       closed=True, fc=col, ec="white", lw=0.6, zorder=z))


def entries_g3m():
    """중간마감 D3의 차량 진입 7곳(사용자 지정 빨간 삼각형) — g3m_street_plan.py와 같은 계산"""
    vd = np.array([353.5 - 254.0, 892.2 - 778.5]); vd /= np.linalg.norm(vd)
    ENT = [(209.5, 150.0, (-vd[1], vd[0]), 2, "북측 차도(사선 구간)"), (300.0, 188.6, (-1, 0), 4, "동측 외곽도로"),
           (95.7, 278.5, (1, 0), 5, "서측 원화로"), (300.0, 283.6, (-1, 0), 6, "동측 외곽도로"),
           (293.5, 420.4, (-1, 0), 8, "동측 외곽도로"), (170.5, 465.3, (0, 1), 7, "동서 도로"), (276.4, 476.1, (0, -1), 13, "동서 도로")]
    out = []
    for px, py, d, no, road in ENT:
        p = np.array([-38.5 + 1.467 * px, 1035.4 - 1.467 * py]); d = np.array(d, float); d /= np.linalg.norm(d)
        q = entry_on(no, p, d)
        out.append(dict(p=q - d * 5.0, d=d, no=no, road=road, lot=LOT[no]["name"]))
    return out


def entry_on(no, p, d):
    p = np.array(p, float); d = np.array(d, float); d /= np.linalg.norm(d)
    ray = LineString([tuple(p - d * 40), tuple(p + d * 60)])
    hit = ray.intersection(LOT[no]["g"].boundary)
    pts_ = [np.array(q.coords[0]) for q in (getattr(hit, "geoms", [hit]))] if not hit.is_empty else [np.array(nearest_points(LOT[no]["g"].boundary, Point(*p))[0].coords[0])]
    return min(pts_, key=lambda v: np.dot(v - (p - d * 40), d))


def lab(ax, x, y, s, c, rot=0, ha="center", stroke=None, fs=10, bold=True, z=14):
    t_ = ax.text(x, y, s, fontsize=fs, color=c, fontweight="bold" if bold else "normal", rotation=rot, ha=ha, va="center", zorder=z, rotation_mode="anchor")
    t_.set_path_effects([pe.withStroke(linewidth=2.0, foreground=stroke)] if stroke else halo(2.2))
    return t_


def tag(pg, x, y, s, fc=INK):
    w = text_w(pg, s, 10, True) + 5
    pg.rect(x, y, w, 6.2, fc=fc, z=40); pg.t(x + 2.5, y + 3.1, s, fs=10, c="white", bold=True, z=41)
    return w


def box_note(pg, x, y, w, title, body, c=SLATE, bullets=False, fc="#F3F5F8"):
    """밝은 설명 박스(#F3F5F8 + 왼쪽 색 띠) — 중간마감 D1과 같은 형식. 반환: 박스 높이"""
    items = body if isinstance(body, (list, tuple)) else [body]
    h = 10.6 + sum(block_h(pg, it, w - 7, bullet=bullets) for it in items) + 1.6 * (len(items) - 1) + 2.2
    pg.rect(x, y, w, h, fc=fc, z=5); pg.rect(x, y, 1.4, h, fc=c, z=6)
    pg.t(x + 4, y + 5.0, title, fs=10, bold=True, c=c, z=6)
    yy = y + 10.8
    for it in items:
        yy = text_block(pg, x + 4, yy, it, w - 7, c=INK, z=6, bullet=bullets) + 1.6
    return h


# ── 단면 그리기(가로 = 세로 같은 축척) ─────────────────────────
SECC = {"보도": "#d9d9d6", "차도": "#636363", "식재": "#9fd67c", "보행": "#efe8d6", "광장": "#efe8d6", "통경축": "#efe8d6"}


def person(pg, x, gy, s, c="#555"):
    """사람 1.7 m — x: mm, gy: 지면 mm, s: mm/m"""
    pg.ax.add_patch(Circle((x, gy - 1.55 * s), 0.13 * s, fc=c, ec="none", zorder=12))
    pg.line([x, x], [gy - 1.42 * s, gy - 0.75 * s], c=c, lw=0.9, z=12)
    pg.line([x, x - 0.18 * s], [gy - 0.75 * s, gy], c=c, lw=0.8, z=12); pg.line([x, x + 0.18 * s], [gy - 0.75 * s, gy], c=c, lw=0.8, z=12)


def tree(pg, x, gy, s, h=9.0, r=2.6, c="#7dbb5c"):
    pg.line([x, x], [gy, gy - (h - r) * s], c="#7a6a55", lw=0.9, z=10)
    pg.ax.add_patch(Circle((x, gy - (h - r) * s), r * s, fc=c, ec="white", lw=0.4, zorder=11, alpha=0.95))


def car(pg, x, gy, s, c="#8a8a86"):
    pg.ax.add_patch(FancyBboxPatch((x - 2.2 * s, gy - 1.5 * s), 4.4 * s, 1.15 * s, boxstyle="round,pad=0,rounding_size=%.2f" % (0.3 * s), fc=c, ec="none", zorder=11))
    for dx in (-1.3, 1.3): pg.ax.add_patch(Circle((x + dx * s, gy - 0.32 * s), 0.32 * s, fc="#444", zorder=12))


# ── A안(2026-10-15 확정): 화랑로 띠 = 보행 통경축, 서쪽 끝 = 화랑로 끝 광장 ─────────────
_PLZ = {p["name"]: p["g"] for p in S["PLZ"]}
EKI = _PLZ["역전광장"]
TERM = unary_union([EKI, EWB.intersection(box(0, 0, EKI.bounds[2], 2000)),
                    box(EKI.bounds[0], EKI.bounds[3], EKI.bounds[2], EWB.bounds[1]).intersection(B)])
CORR = EWB.difference(TERM)
GATE_X = (250.0, 292.0)                 # 남북 보행축(x 255.9–285.9)과 겹치는 게이트 구간 — 판 아래라 가로수를 두지 않는다


def a_corridor(ax, trees=True, bollards=True):
    fill(ax, CORR, fc=AXISC, ec="#cdbf9f", lw=0.4, z=1.7)
    fill(ax, TERM, fc="#E8D5A8", ec="#b89c5e", lw=0.6, z=1.72)
    if trees:
        for yy in (EWB.bounds[1] + 3.0, EWB.bounds[3] - 3.0):
            for x in np.arange(EKI.bounds[2] + 6, 388, 8.0):
                if GATE_X[0] < x < GATE_X[1]: continue
                ax.add_patch(Circle((x, yy), 2.3, fc="#7dbb5c", ec="white", lw=0.3, zorder=1.8))
    if bollards:
        for x in (EKI.bounds[2] + 1.5, 389.5):
            for yy in np.linspace(EWB.bounds[1] + 2, EWB.bounds[3] - 2, 5): ax.add_patch(Circle((x, yy), 1.1, fc=INK, zorder=1.9))


def length_of(g):
    """띠 모양 연장 = 면적 ÷ 평균폭(4 × 면 안 점에서 외곽선까지 평균 거리) — 중간마감 g3m과 같은 방식"""
    from scipy import ndimage
    import shapely
    x0, y0, x1, y1 = g.bounds; st = 0.5
    X, Y = np.meshgrid(np.arange(x0, x1, st) + st / 2, np.arange(y0, y1, st) + st / 2)
    m = np.pad(shapely.contains_xy(g, X.ravel(), Y.ravel()).reshape(X.shape), 3)
    d = ndimage.distance_transform_edt(m) * st
    return g.area / (4.0 * d[m].mean())


# ── R3 건폐율 0.50 규칙(2026-10-15 사용자 확정) — R3 시트와 매스 재작업(m0)이 같은 값을 쓴다 ──
KEEP = [p for p in S["PLZ"] if p["kind"] != "노외주차"]                  # 지정 비움(형태 있는 비움). 지상 노외주차(588㎡)는 남은 땅으로 본다
KEEPG = unary_union([p["g"] for p in KEEP])
SHORT = {1: "공공청사", 2: "청사 주차", 3: "생활체육", 4: "청년주택", 5: "업무·창업", 6: "생활문화", 7: "전통공예", 8: "레지던시",
         9: "구 역사", 10: "방문자", 11: "관문상가", 12: "근대역사관", 13: "공유주차"}
GRP = {1: "W", 5: "W", 7: "W", 10: "W", 11: "W", 12: "W", 3: "E", 4: "E", 6: "E", 8: "E", 2: "P", 13: "P", 9: "H"}
TGT = {"W": 0.65, "E": 0.55, "P": 0.85, "H": 0.50}                    # 순획지 기준 목표 건폐율 † — 서측 띠 0.57 · 동측 띠 0.41 사이
LMIN = {7: 1.5, 8: 1.5, 3: 1.5, 10: 1.0, 11: 1.0}                     # 연면적 고정 → 평균 층수 하한(그 외 2층)
FORM = {1: "중정형", 2: "라이닝 주차", 3: "기단 확장", 4: "중정형 블록 2~3", 5: "ㄷ자", 6: "기단+분동", 7: "골목 매트", 8: "골목 매트",
        9: "역사 존치 · ㄷ자", 10: "기단 확장", 11: "가로 연속 상가", 12: "둘레형", 13: "라이닝 주차"}


def lot_targets():
    """획지별 현재 바닥(동 합집합)·지정 비움·연면적·목표 건축면적"""
    out = []
    for l in S["LOTS"]:
        g = l["g"]; bl = [b for b in BLD if b["lot"] == l["no"]]
        fp = unary_union([b["g"] for b in bl]).intersection(g)
        op = KEEPG.intersection(g).difference(fp)
        gfa = sum(b["gfa"] for b in bl); net = g.area - op.area
        ba1 = max(fp.area, min(TGT[GRP[l["no"]]] * net, gfa / LMIN.get(l["no"], 2.0)))
        out.append(dict(no=l["no"], g=g, fp=fp, op=op, A=g.area, ba0=fp.area, opA=op.area, res=g.area - fp.area - op.area, gfa=gfa, ba1=ba1,
                        f0=max(b["floors"] for b in bl), cat=l["cat"]))
    return out
