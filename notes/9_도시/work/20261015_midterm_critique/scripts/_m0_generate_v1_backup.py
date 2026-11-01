"""M0 매스 재작업 v1 — 획지 건폐율 0.50, 같은 연면적을 낮고 넓게(2026-10-15 사용자 확정)
입력: 중간마감 최종 모델(data/model.pkl) — 획지·지정 비움·도로는 그대로, 구 역사는 계획 모델 배치 유지(사용자 결정)
규칙(R3와 같은 값, k0): 획지별 목표 건축면적 = max(지금, min(목표 GSI × 순획지, 연면적 ÷ 평균 층수 하한))
형태(획지별):
  1 공공청사 — 중정형(시민광장 쪽을 원화로로 열어 ㄷ자)       3 생활체육·6 생활문화 — 기단 + 분동
  4 청년주택 — 중정형 블록 2개(가운데 8 m 골목)               5 업무·창업 — 중앙 근린공원을 감싸는 ㄷ자(L)
  7 전통공예 — 골목 매트(공예 중정 유지, 석탑 12 m 이격)       9 구 역사 — 역사·문화원 본동·유리 지붕 유지, 상생동을 통경축·관문 쪽 낮은 동으로
  10 방문자·11 관문상가 — 보행축을 따라 낮은 가로 동           12 근대역사관 — 둘레형(중정 유지)
  13 공유주차 — 라이닝 주차(통경축·보행축 쪽 1층 상가)         2 청사 주차·8 레지던시 — 이미 목표 이상이라 유지
층수: 최고 5층(4 m 층고 20 m — 고도지구 20 m). 동측 경계 30 m 안은 3층까지(황오동 1층 93%). 공공 공간(보행축·선형공원·광장)에 가까운 동부터 층을 올린다.
연면적: 획지별로 맞춘다. 끝수는 한 동의 꼭대기 층을 안으로 물린 부분층(셋백)으로 맞춘다.
출력: ../mass_v1/data/mass_v1.pkl"""
from k0 import *
import copy

OUTD = os.path.join(K0DIR, "..", "mass_v1", "data"); os.makedirs(OUTD, exist_ok=True)
FH = {"주거": 3.0, "주차": 3.2}
def fh(cat): return FH.get(cat, 4.0)
MAXF = 5
EAST = B.exterior.intersection(box(398, 0, 600, 2000))                 # 대지 동측 경계(황오동 쪽)
PUB = unary_union([OP["D"]["g"], OP["E"]["g"], OP["F"]["g"], CORR, TERM, [p["g"] for p in S["PLZ"] if p["name"] == "청사 앞 시민광장"][0]])
PLZN = {p["name"]: p["g"] for p in S["PLZ"]}
T = {r["no"]: r for r in lot_targets()}
OLD = {}
for b in BLD: OLD.setdefault(b["lot"], []).append(b)


# ── 기하 도구 ────────────────────────────────────────────
def clean(g, amin=25.0):
    g = g.buffer(0)
    return unary_union([p for p in polys(g) if p.area >= amin]) if not g.is_empty else g


def chunky(g, amin=60.0, wmin=5.0):
    """면적 60㎡·평균 폭 5 m 미만 조각은 버린다"""
    return unary_union([p for p in polys(g) if p.area >= amin and 2 * p.area / p.length >= wmin]) if not g.is_empty else g


def inset(g, d): return clean(g.buffer(-d, join_style=2, mitre_limit=5.0)) if d > 0 else g
def ring(g, d): return clean(g.difference(g.buffer(-d, join_style=2, mitre_limit=5.0)))
def band(g, line, d): return clean(g.intersection(line.buffer(d, cap_style=2, join_style=2)))


def solve(fun, lo, hi, target, inc=True, it=44):
    """fun(x) 단조 — fun(x) = target인 x"""
    s_ = 1 if inc else -1
    if s_ * fun(lo) >= s_ * target: return lo
    if s_ * fun(hi) <= s_ * target: return hi
    for _ in range(it):
        m = (lo + hi) / 2
        if s_ * fun(m) < s_ * target: lo = m
        else: hi = m
    return (lo + hi) / 2


def passages(g, width=6.0, min_len=80.0, reach=30.0):
    """긴 변(> min_len) 가운데에서 안쪽으로 폭 6 m·깊이 30 m 통로 — 한쪽 날개만 열어 중정으로 드나드는 문"""
    cuts = []
    from shapely.geometry.polygon import orient
    for p in polys(g):
        cs = list(orient(p, 1.0).exterior.simplify(1.0).coords)          # 반시계 → 왼쪽 법선이 안쪽
        for a, b in zip(cs[:-1], cs[1:]):
            a = np.array(a); b = np.array(b); L = np.linalg.norm(b - a)
            if L < min_len: continue
            m = (a + b) / 2; t = (b - a) / L; n = np.array([-t[1], t[0]])
            cuts.append(Polygon([tuple(m - t * width / 2 - n * 2.0), tuple(m + t * width / 2 - n * 2.0), tuple(m + t * width / 2 + n * reach), tuple(m - t * width / 2 + n * reach)]))
    return unary_union(cuts) if cuts else Polygon()


def cut_every(g, axis, spacing=34.0, gap=5.0):
    """axis(단위벡터) 방향으로 spacing마다 폭 gap의 틈 — 긴 가로 동을 여러 동으로"""
    axis = np.array(axis, float); axis /= np.linalg.norm(axis); n = np.array([-axis[1], axis[0]])
    c = np.array(g.centroid.coords[0]); pr = [np.dot(np.array(q) - c, axis) for p in polys(g) for q in p.exterior.coords]
    cuts = []
    for s_ in np.arange(min(pr) + spacing, max(pr) - spacing * 0.4, spacing):
        m = c + axis * s_
        cuts.append(Polygon([tuple(m - axis * gap / 2 - n * 200), tuple(m + axis * gap / 2 - n * 200), tuple(m + axis * gap / 2 + n * 200), tuple(m - axis * gap / 2 + n * 200)]))
    return chunky(clean(g.difference(unary_union(cuts)))) if cuts else chunky(g)


def grid_mat(g, spacing, alley, origin):
    """격자 골목 매트 — 간격 spacing, 골목 폭 alley"""
    x0, y0, x1, y1 = g.bounds; ox, oy = origin; cuts = []
    for x in np.arange(ox + spacing, x1, spacing): cuts.append(box(x - alley / 2, y0 - 5, x + alley / 2, y1 + 5))
    for y in np.arange(oy + spacing, y1, spacing): cuts.append(box(x0 - 5, y - alley / 2, x1 + 5, y + alley / 2))
    return clean(g.difference(unary_union(cuts)), 30.0)


def longest_edge(g):
    p = max(polys(g), key=lambda q: q.area); cs = list(p.exterior.simplify(0.5).coords)
    a, b = max(zip(cs[:-1], cs[1:]), key=lambda e: np.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]))
    return LineString([a, b])


def edge_near(g, ref):
    """g 외곽선 중 ref 쪽(가까운) 변"""
    p = max(polys(g), key=lambda q: q.area); cs = list(p.exterior.simplify(0.5).coords)
    return min((LineString([a, b]) for a, b in zip(cs[:-1], cs[1:]) if np.hypot(b[0] - a[0], b[1] - a[1]) > 10),
               key=lambda e: e.centroid.distance(ref))


# ── 층수 배분 ────────────────────────────────────────────
def caps_of(segs, cap=MAXF, east_cap=3):
    return [min(cap, east_cap) if s.distance(EAST) < 30.0 else cap for s in segs]


def prio_of(segs):
    return [-s.distance(PUB) + 1e-4 * s.area for s in segs]


def fit(segs, gfa, cap, prio, base=1):
    """층을 한 단씩 올린다(공공 공간 가까운 동부터). 끝수는 한 동의 꼭대기 셋백 부분층. 반환: n(층수 목록), top(부분층 (i, poly) 또는 None), 부족분"""
    A = [s.area for s in segs]; n = [base] * len(segs); tot = sum(A) * base
    order = sorted(range(len(segs)), key=lambda i: -prio[i])
    for L in range(base + 1, max(cap) + 1):
        for i in order:
            if n[i] == L - 1 and cap[i] >= L and tot + A[i] <= gfa + 1e-6:
                n[i] = L; tot += A[i]
    R = gfa - tot; top = None
    if R > 1.0:
        cand = [i for i in order if n[i] < cap[i] and A[i] > R]
        if cand:
            i = cand[0]
            k = solve(lambda d: inset(segs[i], d).area, 0.0, 60.0, R, inc=False)
            tp = inset(segs[i], k)
            if not tp.is_empty: top = (i, tp); R -= tp.area
    return n, top, R


def make(no, segs, cat, gfa, name, cap=None, gcat=None, gsel=None, base=1, prio=None):
    """segs → 건축물 기록(중간마감 BLD 형식: parts·stack·gfa_by). gcat: 1층 다른 용도(gsel(seg)가 참인 동만)"""
    segs = [s for s in segs if s.area >= 25]
    cap = cap or caps_of(segs); prio = prio or prio_of(segs)
    n, top, short = fit(segs, gfa, cap, prio, base)
    out = []
    for i, s in enumerate(segs):
        g1 = gcat if (gcat and (gsel is None or gsel(s))) else None
        c_s = cat(s) if callable(cat) else cat
        parts = []; stack = []; z = 0.0; by = {}
        for k in range(n[i]):
            c = g1 if (g1 and k == 0) else c_s
            parts.append((s, z, z + fh(c), c)); stack.append((z, z + fh(c), c, s.area)); by[c] = by.get(c, 0) + s.area; z += fh(c)
        if top is not None and top[0] == i:
            parts.append((top[1], z, z + fh(c_s), c_s)); stack.append((z, z + fh(c_s), c_s, top[1].area)); by[c_s] = by.get(c_s, 0) + top[1].area; z += fh(c_s)
        out.append(dict(name="%s %d동" % (name, i + 1), lot=no, g=s, h=z, floors=n[i] + (1 if top is not None and top[0] == i else 0), gfa=sum(by.values()),
                        gfa_by=by, main=c_s, retail=bool(g1), stack=stack, parts=parts, term=name, edited=True, gen=True))
    return out, short


NEW = {}; NOTE = {}; SHORTFALL = {}
lot = {l["no"]: l["g"] for l in S["LOTS"]}

# 1 공공청사 — 중정형, 시민광장 쪽(서측)을 원화로로 열어 ㄷ자. 획지 2(청사 주차)의 목표 부족분을 함께 맡는다
MOVE21 = T[2]["ba1"] - T[2]["ba0"]
T[1] = dict(T[1]); T[1]["ba1"] += MOVE21
t = T[1]; plz = PLZN["청사 앞 시민광장"]
outer = inset(lot[1], 2.0)
openw = box(lot[1].bounds[0] - 5, plz.bounds[1], plz.bounds[0], plz.bounds[3])
f1 = lambda d: chunky(clean(ring(outer, d).difference(plz.buffer(2.0)).difference(openw).difference(passages(outer))))
d1 = solve(lambda d: f1(d).area, 8.0, 45.0, t["ba1"])
NEW[1], SHORTFALL[1] = make(1, polys(f1(d1)), "공공업무", t["gfa"], "공공청사")
NOTE[1] = "둘레 깊이 %.1f m, 시민광장을 원화로 쪽으로 열어 ㄷ자, 긴 변 가운데 통로 6 m · 획지 2 부족분 %s㎡ 포함" % (d1, f0(MOVE21))

# 3 생활체육 — 기단(2층) + 분동(1층)
t = T[3]; bld = inset(lot[3], 2.0)
k3 = solve(lambda d: inset(bld, d).area, 0.0, 30.0, t["ba1"], inc=False); pod = inset(bld, k3)
NEW[3], SHORTFALL[3] = make(3, [pod], "생활SOC", t["gfa"], "생활체육관", cap=[3], base=2)
NOTE[3] = "기단 2층(획지에서 %.1f m 안으로) + 3층 셋백" % (2 + k3)

# 4 청년주택 — 중정형 블록 2개, 가운데 동서 골목 8 m
t = T[4]; bld = inset(lot[4], 2.0); ym = (lot[4].bounds[1] + lot[4].bounds[3]) / 2
blocks = polys(clean(bld.difference(box(0, ym - 4, 2000, ym + 4))))
f4 = lambda d: chunky(clean(unary_union([ring(b_, d).difference(passages(b_)) for b_ in blocks])))
d4 = solve(lambda d: f4(d).area, 6.0, 40.0, t["ba1"])
NEW[4], SHORTFALL[4] = make(4, polys(f4(d4)), "주거", t["gfa"], "청년주택", gcat="판매", gsel=lambda s: s.distance(OP["E"]["g"]) < 25 or abs(s.centroid.y - ym) < 25)
NOTE[4] = "중정형 블록 2개(골목 8 m), 둘레 깊이 %.1f m, 남북 보행축·골목 쪽 1층 근린생활·커뮤니티" % d4

# 5 업무·창업 — 중앙 근린공원을 감싸는 ㄷ자(L)
t = T[5]; bld = inset(lot[5], 2.0)
f5 = lambda d: chunky(clean(ring(bld, d).difference(passages(bld, min_len=60))))
d5 = solve(lambda d: f5(d).area, 6.0, 40.0, t["ba1"])
segs5 = polys(f5(d5))
NEW[5], SHORTFALL[5] = make(5, segs5, lambda s: "공공업무" if s.centroid.y > 600 else "업무·창업", t["gfa"], "공공기관 업무·청년창업")
NOTE[5] = "중앙 근린공원을 감싸는 L(ㄷ자), 깊이 %.1f m, 북쪽 = 공공기관 업무 · 동쪽 = 청년창업" % d5

# 6 생활문화·돌봄 — 기단(2층) + 남북 보행축 쪽 분동
t = T[6]; bld = clean(inset(lot[6], 2.0).difference(t["op"].buffer(2.0)))
cut6 = passages(bld, min_len=60)
k6 = solve(lambda d: chunky(inset(bld, d).difference(cut6)).area, 0.0, 30.0, t["ba1"], inc=False); pod = chunky(inset(bld, k6).difference(cut6))
R6 = t["gfa"] - 2 * pod.area; e6 = edge_near(pod, OP["E"]["g"])
nb = 2; bar = band(pod, e6, solve(lambda d: band(pod, e6, d).area, 2.0, 60.0, R6 / nb))
NEW[6] = [dict(name="복합문화·돌봄센터 기단", lot=6, g=pod, h=8.0 + 4.0 * nb, floors=2 + nb, gfa=2 * pod.area + nb * bar.area,
               gfa_by={"문화": 2 * pod.area + nb * bar.area}, main="문화", retail=False,
               stack=[(0, 4, "생활SOC", pod.area), (4, 8, "문화", pod.area)] + [(8 + 4 * k, 12 + 4 * k, "문화", bar.area) for k in range(nb)],
               parts=[(pod, 0, 4, "생활SOC"), (pod, 4, 8, "문화"), (bar, 8, 8 + 4 * nb, "문화")], term="복합문화센터", edited=True, gen=True)]
NEW[6][0]["gfa_by"] = {"생활SOC": pod.area, "문화": pod.area + nb * bar.area}
SHORTFALL[6] = t["gfa"] - NEW[6][0]["gfa"]
NOTE[6] = "기단 2층(1층 건강·돌봄) + 보행축 쪽 분동 %d층, 소공원·텃밭 유지" % nb

# 7 전통공예 — 골목 매트(공예 중정 유지, 석탑 12 m 이격)
t = T[7]; bld = clean(inset(lot[7], 1.5).difference(t["op"].buffer(2.0)).difference(PAGODA.buffer(12.0)))
org = (lot[7].bounds[0] + 1.5, lot[7].bounds[1] + 1.5)
a7 = solve(lambda a: grid_mat(bld, 26.0, a, org).area, 3.0, 12.0, t["ba1"], inc=False)
mat = grid_mat(bld, 26.0, a7, org)
segs7 = polys(mat)
cap7 = [3 if (s.distance(CORR) < 15 or s.distance(box(100, 0, 118, 2000)) < 12) else 2 for s in segs7]
NEW[7], SHORTFALL[7] = make(7, segs7, "창작", t["gfa"], "공방", cap=cap7, gcat="판매", gsel=lambda s: s.distance(CORR) < 15 or s.distance(TERM) < 15)
NOTE[7] = "격자 26 m · 골목 %.1f m 매트, 공예 중정 유지, 삼층석탑 12 m 이격, 통경축·원화로 쪽 1층 판매" % a7

# 9 구 역사 — 역사·문화원 본동·유리 지붕 유지, 상생동(5층 2동)을 통경축·관문 쪽 낮은 동으로
t = T[9]; keep9 = [b for b in OLD[9] if b["name"] in ("구 경주역사", "지역문화원 본동")]
gfa9 = t["gfa"] - sum(b["gfa"] for b in keep9); ba9 = t["ba1"] - unary_union([b["g"] for b in keep9]).area
zone = clean(inset(lot[9], 1.5).difference(unary_union([PLZN["역전광장"].buffer(1.0), PLZN["그레이트 코트(유리 지붕 중정)"].buffer(2.0)] + [b["g"].buffer(4.0) for b in keep9])))
xs9 = lot[9].bounds
north9 = LineString([(xs9[0], xs9[3]), (xs9[2], xs9[3])]); south9 = LineString([(xs9[0], xs9[1]), (xs9[2], xs9[1])])
f9 = lambda d: cut_every(clean(unary_union([band(zone, north9, d), band(zone, south9, d)])), (1, 0), 30.0, 5.0)
d9 = solve(lambda d: f9(d).area, 3.0, 40.0, ba9)
w9, SHORTFALL[9] = make(9, polys(f9(d9)), "판매", gfa9, "소상공인 상생", cap=[2] * len(polys(f9(d9))))
NEW[9] = [copy.deepcopy(b) for b in keep9] + w9
NOTE[9] = "구 역사·지역문화원 본동·유리 지붕 유지. 상생동 5층 2동 → 통경축·관문 쪽 1~2층 가로 동(깊이 %.1f m)" % d9

# 10 방문자 — 사선 보행축을 따라 1층 가로 동
t = T[10]; bld = inset(lot[10], 1.5); e10 = edge_near(bld, OP["F"]["g"])
f10 = lambda d: band(bld, e10, d)
d10 = solve(lambda d: f10(d).area, 2.0, 40.0, t["ba1"])
NEW[10], SHORTFALL[10] = make(10, polys(f10(d10)), "방문자", t["gfa"], "관광지원센터", cap=[1] * len(polys(f10(d10))))
NOTE[10] = "사선 보행축을 따라 1층 파빌리온(깊이 %.1f m)" % d10

# 11 관문상가 — 관문 가로광장을 따라 1층 가로 상가, 34 m마다 틈 5 m
t = T[11]; plz11 = KEEPG.intersection(lot[11]); bld = clean(inset(lot[11], 1.5).difference(plz11.buffer(0.5)))   # 관문 가로광장 전체를 비운다
ax11 = np.array(longest_edge(plz11).coords[1]) - np.array(longest_edge(plz11).coords[0])
f11 = lambda d: cut_every(band(bld, plz11.exterior, d), ax11, 34.0, 5.0)
d11 = solve(lambda d: f11(d).area, 2.0, 40.0, t["ba1"])
NEW[11], SHORTFALL[11] = make(11, polys(f11(d11)), "판매", t["gfa"], "관문 가로상가", cap=[1] * len(polys(f11(d11))))
NOTE[11] = "관문 가로광장을 따라 1층 가로 상가(깊이 %.1f m), 34 m마다 틈 5 m" % d11

# 12 근대역사관 — 둘레형(중정 유지)
t = T[12]; bld = clean(inset(lot[12], 2.0).difference(t["op"].buffer(1.0)), 200)
f12 = lambda d: chunky(clean(ring(bld, d).difference(passages(bld, min_len=50))))
d12 = solve(lambda d: f12(d).area, 6.0, 40.0, t["ba1"])
NEW[12], SHORTFALL[12] = make(12, polys(f12(d12)), "문화", t["gfa"], "근대역사관", cap=[4] * len(polys(f12(d12))))
NOTE[12] = "둘레형, 깊이 %.1f m, 중정 유지, 최고 4층" % d12

# 13 공유주차 — 라이닝 주차(통경축·보행축 쪽 1층 상가)
t = T[13]; bld = inset(lot[13], 1.5)
k13 = solve(lambda d: inset(bld, d).area, 0.0, 30.0, t["ba1"], inc=False); foot = inset(bld, k13)
liner = clean(ring(foot, 8.0).intersection(unary_union([CORR, OP["E"]["g"], OP["F"]["g"], TERM]).buffer(24.0)))
core = clean(foot.difference(liner))
c13, SHORTFALL[13] = make(13, [core], "주차", t["gfa"], "공유주차장·모빌리티 허브", cap=[MAXF])
l13 = [dict(name="라이닝 상가", lot=13, g=g, h=4.0, floors=1, gfa=g.area, gfa_by={"판매": g.area}, main="판매", retail=True,
            stack=[(0, 4, "판매", g.area)], parts=[(g, 0, 4, "판매")], term="라이닝 상가", edited=True, gen=True) for g in polys(liner)]
NEW[13] = c13 + l13
NOTE[13] = "주차 연면적 유지(%s㎡), 통경축·보행축 쪽 깊이 8 m 1층 라이닝 상가 %s㎡ 신설(연면적 증가)" % (f0(t["gfa"]), f0(liner.area))

# 8 레지던시 — 유지(순획지 건폐율이 이미 목표 이상)
NEW[8] = [copy.deepcopy(b) for b in OLD[8]]; SHORTFALL[8] = 0.0
NOTE[8] = "유지 — 순획지 건폐율이 이미 목표 이상(%.2f)" % (T[8]["ba0"] / (T[8]["A"] - T[8]["opA"]))

# 2 청사 주차 — 유지. 남은 땅이 주차장동 둘레의 좁은 띠라 동을 둘 수 없다 → 부족분(목표 − 지금)은 획지 1(공공청사)로 옮겼다
NEW[2] = [copy.deepcopy(b) for b in OLD[2]]; SHORTFALL[2] = 0.0
NOTE[2] = "유지 — 남은 땅이 좁은 띠라 동을 둘 수 없음. 목표와의 차 %s㎡는 획지 1로 옮김" % f0(T[2]["ba1"] - T[2]["ba0"])

BLD2 = [b for no in sorted(NEW) for b in NEW[no]]
LINKS2 = [k for k in M["LINKS"] if k["lot"] == 8]

# 플랫폼(R2와 같은 판) — 판·기둥
E_ = OP["E"]["g"]; F_ = OP["F"]["g"]
SEG1 = unary_union([F_.intersection(box(150, 185, 300, 333)).buffer(-3), E_.intersection(box(250, 291, 292, 320)).buffer(-4)])
SEG2 = box(258.0, 318.0, 284.0, 370.0)
SEG3 = box(244.0, 464.0, 298.0, 528.0).difference(box(256.0, 476.0, 286.0, 516.0))
DECKS = [dict(name="① 남측 관문 캐노피", g=SEG1, z0=6.1, z1=6.5), dict(name="② 화랑로 게이트", g=SEG2, z0=5.0, z1=6.0), dict(name="③ 교차광장 공중 회랑", g=SEG3, z0=3.0, z1=4.0)]
COLS = []
c1 = LineString([(200, 196), (262, 296), (271, 318)])                     # 캐노피 중심선(근사) — 12 m마다 기둥 2열
for s_ in np.arange(6, c1.length, 12.0):
    p = c1.interpolate(s_); q = c1.interpolate(min(s_ + 1, c1.length)); t_ = np.array([q.x - p.x, q.y - p.y]); t_ /= (np.linalg.norm(t_) + 1e-9); n_ = np.array([-t_[1], t_[0]])
    for o_ in (-5.0, 5.0):
        c = np.array([p.x, p.y]) + n_ * o_
        if SEG1.buffer(0.5).contains(Point(*c)): COLS.append((box(c[0] - 0.4, c[1] - 0.4, c[0] + 0.4, c[1] + 0.4), 6.1))
for y in (322.0, 366.0):
    for x in (262.0, 280.0): COLS.append((box(x - 0.4, y - 0.4, x + 0.4, y + 0.4), 5.0))
for x, y in ((246, 466), (254, 474), (288, 474), (296, 466), (246, 526), (254, 518), (288, 518), (296, 526)): COLS.append((box(x - 0.4, y - 0.4, x + 0.4, y + 0.4), 3.0))

# 식재 — 새 동·판 위 나무는 빼고, 통경축 가로수 2열(게이트 구간 제외)
FOOT = unary_union([b["g"] for b in BLD2]).buffer(1.5)
NOTREE = unary_union([FOOT, EWB, SEG1, SEG2, SEG3])
TREES2 = [(x, y, r) for (x, y, r) in M["TREES"] if not NOTREE.contains(Point(x, y))]
for yy in (EWB.bounds[1] + 3.0, EWB.bounds[3] - 3.0):
    for x in np.arange(EKI.bounds[2] + 6, 388, 8.0):
        if not (GATE_X[0] < x < GATE_X[1]): TREES2.append((float(x), float(yy), 3.2))

# 지면 — A안: 동서 도로 → 통경축 · 화랑로 끝 광장
S2 = dict(S); S2["ROADS"] = {k: v for k, v in S["ROADS"].items() if k != "EW"}
S2["PLZ"] = list(S["PLZ"]) + [dict(kind="광장", name="화랑로 끝 광장", g=TERM.difference(EKI)), dict(kind="통경축", name="보행 통경축", g=CORR)]

# 결과 집계
RES = []
for no in sorted(NEW):
    bl = NEW[no]; g = lot[no]
    fp = unary_union([b["g"] for b in bl]).intersection(g)
    gfa = sum(b["gfa"] for b in bl)
    RES.append(dict(no=no, A=g.area, ba0=T[no]["ba0"], ba_t=T[no]["ba1"], ba=fp.area, gfa0=T[no]["gfa"], gfa=gfa, n=len(bl), n0=len(OLD[no]),
                    fmax=max(b["floors"] for b in bl), f0max=T[no]["f0"], hmax=max(b["h"] for b in bl), note=NOTE[no], short=SHORTFALL[no], form=FORM[no]))
TA = sum(r["A"] for r in RES); TB = sum(r["ba"] for r in RES); TG = sum(r["gfa"] for r in RES); TB0 = sum(r["ba0"] for r in RES); TG0 = sum(r["gfa0"] for r in RES)
for r in RES:
    print("%2d %-8s ba %6.0f → %6.0f (목표 %6.0f) GSI %.2f→%.2f  gfa %6.0f → %6.0f  동 %2d→%2d  최고 %d→%d층 %.0f m  부족 %.0f  | %s" % (
        r["no"], SHORT[r["no"]], r["ba0"], r["ba"], r["ba_t"], r["ba0"] / r["A"], r["ba"] / r["A"], r["gfa0"], r["gfa"], r["n0"], r["n"], r["f0max"], r["fmax"], r["hmax"], r["short"], r["note"]))
print("합계 획지 %.0f · 건축면적 %.0f → %.0f · GSI %.3f → %.3f · 연면적 %.0f → %.0f (%+.0f) · 동 %d · 평균 %.2f층" % (TA, TB0, TB, TB0 / TA, TB / TA, TG0, TG, TG - TG0, len(BLD2), TG / TB))
pickle.dump(dict(S=S2, BLD=BLD2, LINKS=LINKS2, TREES=TREES2, ST_FP=M["ST_FP"], DECKS=DECKS, COLS=COLS, RES=RES, NOTE=NOTE,
                 TOT=dict(boundary=TOT["boundary"], lot=TA, ba=TB, gfa=TG, ba0=TB0, gfa0=TG0)), open(os.path.join(OUTD, "mass_v1.pkl"), "wb"))
print("saved mass_v1.pkl")
