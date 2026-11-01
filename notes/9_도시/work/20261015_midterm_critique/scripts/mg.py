"""mg — 매스 생성 도구(m0 v1 · m5 v1-b 공통). 기하(링·띠·통로·매트)와 층수 배분(fit·make)
PUB(층을 먼저 올릴 공공 공간)·EAST(동측 경계)는 모듈 변수 — 변형안은 mg.PUB를 바꿔 쓴다"""
from k0 import *

FH = {"주거": 3.0, "주차": 3.2}
def fh(cat): return FH.get(cat, 4.0)
MAXF = 5
EAST = B.exterior.intersection(box(398, 0, 600, 2000))                 # 대지 동측 경계(황오동 쪽)
PUB = unary_union([OP["D"]["g"], OP["E"]["g"], OP["F"]["g"], CORR, TERM, [p["g"] for p in S["PLZ"] if p["name"] == "청사 앞 시민광장"][0]])


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


