"""M5 매스 변형안 v1-b — 구 경주역사를 실제 위치에(2026-10-15 사용자 요청)
- 구 역사: 콘타 모델 '빌딩'(V-World 연속지적 정합)의 실제 동(88.7 × 24.1 m, 긴 변 남북, 서쪽 정면). 화랑로 축이 정면에 닿는다
- 획지선: 획지 9를 북쪽으로 넓혀(옛 동서 도로·보도 x 114–190, 획지 7 남서 모서리) 역사·역 앞마당·옛 1번 승강장을 한 획지에 담는다. 획지 7은 그만큼 줄인다
- 지정 비움(획지 9): 역 앞마당(원화로–역사, 삼층석탑 포함) · 옛 1번 승강장(캐노피 아래) · 플랫폼 광장. 그레이트 코트·유리 지붕·옛 역전광장은 없앤다
- 화랑로 축: 원화로 → 역 앞마당 → 대합실 관통 통로(폭 8 m, 1층 24시간) → 옛 1번 승강장 → 플랫폼 광장 → ② 게이트 → 통경축 → 황오동
- 판 ①: 사선 보행축 위 캐노피 → 역사 동쪽 옛 1번 승강장 캐노피(폭 14 m, +6.5 m — 역사 7 m보다 낮게)
- 획지 7·9만 다시 짓고 나머지 획지는 v1 그대로. 전체 획지 건폐율 0.50을 맞추도록 획지 9 목표를 정한다(역사 주변 1~2층, 역사 25 m 안 2층까지)
출력: ../mass_v1b/data/mass_v1b.pkl"""
import mg
from mg import *
import copy

OUTD = os.path.join(K0DIR, "..", "mass_v1b", "data"); os.makedirs(OUTD, exist_ok=True)
V1 = pickle.load(open(os.path.join(K0DIR, "..", "mass_v1", "data", "mass_v1.pkl"), "rb"))
LOTG = {l["no"]: l["g"] for l in S["LOTS"]}
OLD = {}
for b in BLD: OLD.setdefault(b["lot"], []).append(b)

# ── 새 획지선 · 지정 공간 ─────────────────────────────────
ST = ST_REAL
NX = box(114.0, 328.0, 190.0, 384.0).intersection(B)                      # 획지 9로 들어오는 땅(옛 동서 도로·보도·획지 7 남서 모서리)
LOT9 = clean(unary_union([LOTG[9], NX]), 1)
LOT7 = clean(LOTG[7].difference(NX), 1)
MOUTH = EWB.intersection(box(0, 0, 114.0, 2000))                         # 원화로 쪽 띠 입구 → 보도
WALKb = unary_union([S["WALK"].difference(NX), MOUTH])
CORRb = EWB.intersection(box(190.0, 0, 2000, 2000))                      # 통경축(옛 1번 승강장 동쪽부터)
FORE = clean(box(114.0, 270.0, ST.bounds[0], 384.0).intersection(LOT9).difference(ST), 1)     # 역 앞마당
PLAT1 = box(ST.bounds[2] + 1.7, 279.0, ST.bounds[2] + 15.7, 376.0).intersection(LOT9)        # 옛 1번 승강장(캐노피 아래 지면) 폭 14 m
PPLZ = box(PLAT1.bounds[2], 296.0, 256.0, 329.0).intersection(LOT9)                          # 플랫폼 광장
PASS = box(ST.bounds[0], HWARANG_Y - 4.0, ST.bounds[2], HWARANG_Y + 4.0)                    # 대합실 관통 통로(역사 1층, 폭 8 m)
OPEN9 = unary_union([FORE, PLAT1, PPLZ])
for nm, g in (("LOT9", LOT9), ("LOT7", LOT7), ("FORE", FORE), ("PLAT1", PLAT1), ("PPLZ", PPLZ), ("CORRb", CORRb), ("MOUTH", MOUTH)):
    print("%-6s %8.1f㎡ %s" % (nm, g.area, [round(v, 1) for v in g.bounds]))

PLZb = [p for p in S["PLZ"] if p["name"] not in ("역전광장", "그레이트 코트(유리 지붕 중정)")]
PLZb += [dict(kind="광장", name="역 앞마당", g=FORE), dict(kind="광장", name="옛 1번 승강장(캐노피 아래)", g=PLAT1), dict(kind="광장", name="플랫폼 광장", g=PPLZ),
         dict(kind="통경축", name="보행 통경축", g=CORRb)]
KEEPb = unary_union([p["g"] for p in PLZb if p["kind"] not in ("노외주차", "통경축")])
mg.PUB = unary_union([OP["D"]["g"], OP["E"]["g"], OP["F"]["g"], CORRb, FORE, PPLZ, PLAT1, [p["g"] for p in S["PLZ"] if p["name"] == "청사 앞 시민광장"][0]])

# ── 목표 — 전체 0.50 ─────────────────────────────────────
LOTSb = []
for l in S["LOTS"]:
    l2 = dict(l)
    if l["no"] == 9: l2["g"] = LOT9; l2["area"] = LOT9.area
    if l["no"] == 7: l2["g"] = LOT7; l2["area"] = LOT7.area
    LOTSb.append(l2)
TA = sum(l["g"].area for l in LOTSb)
R1 = {r["no"]: r for r in V1["RES"]}
BA_OTH = sum(R1[n]["ba"] for n in R1 if n not in (7, 9))
gfa7 = sum(b["gfa"] for b in OLD[7]); gfa9 = sum(b["gfa"] for b in OLD[9])
op7 = KEEPb.intersection(LOT7).area; op9 = KEEPb.intersection(LOT9).area
ba7 = min(TGT["W"] * (LOT7.area - op7), gfa7 / LMIN[7])
need9 = 0.50 * TA - BA_OTH - ba7
LMIN9 = 1.5
ba9 = min(need9, gfa9 / LMIN9)
print("획지 합 %.0f · 다른 획지 %.0f · 목표 획지 7 %.0f · 획지 9 %.0f(순획지 건폐율 %.2f, 평균 %.2f층)" % (TA, BA_OTH, ba7, ba9, ba9 / (LOT9.area - op9), gfa9 / ba9))

NEW = {n: [copy.deepcopy(b) for b in V1["BLD"] if b["lot"] == n] for n in R1 if n not in (7, 9)}
NOTE = dict(V1["NOTE"]); SHORTFALL = {}

# 7 전통공예 — 골목 매트(공예 중정 유지, 석탑 12 m 이격), 남서 모서리는 획지 9로
cj = [p["g"] for p in S["PLZ"] if p["name"] == "공예 중정(근린공원)"][0]
bld = clean(inset(LOT7, 1.5).difference(cj.buffer(2.0)).difference(PAGODA.buffer(12.0)))
org = (LOT7.bounds[0] + 1.5, LOT7.bounds[1] + 1.5)
a7 = solve(lambda a: grid_mat(bld, 26.0, a, org).area, 3.0, 12.0, ba7, inc=False)
segs7 = polys(grid_mat(bld, 26.0, a7, org))
cap7 = [3 if (s.distance(CORRb) < 15 or s.distance(box(100, 0, 118, 2000)) < 12) else 2 for s in segs7]
NEW[7], SHORTFALL[7] = make(7, segs7, "창작", gfa7, "공방", cap=cap7, gcat="판매", gsel=lambda s: s.distance(CORRb) < 15 or s.distance(PPLZ) < 15)
NOTE[7] = "격자 26 m · 골목 %.1f m 매트, 공예 중정 유지, 남서 모서리(%s㎡)는 획지 9로" % (a7, f0(LOTG[7].area - LOT7.area))

# 9 구 역사 — 실제 위치 존치 + 역 앞마당·옛 1번 승강장·플랫폼 광장. 지역문화원·상생동은 플랫폼 광장으로 열린 ㄷ자 1~2층(역사 25 m 안 2층)
st0 = [b for b in OLD[9] if b["name"] == "구 경주역사"][0]
st = copy.deepcopy(st0); st["g"] = ST; st["parts"] = [(ST, z0, z1, c) for (_, z0, z1, c) in st0["parts"]] if st0.get("parts") else []
st["name"] = "구 경주역사"; st["gen"] = False
bld9 = clean(inset(LOT9, 1.5).difference(OPEN9.buffer(1.5, join_style=2)).difference(ST.envelope.buffer(6.0, join_style=2)), 200)   # 역사 둘레 6 m(직각)
ytop = max(p.bounds[3] for p in polys(bld9)); xc = PPLZ.centroid.x
opening = box(xc - 22, ytop - 60, xc + 22, ytop + 5)
f9 = lambda d: chunky(clean(ring(bld9, d).difference(opening).difference(passages(bld9, min_len=60))))
d9 = solve(lambda d: f9(d).area, 4.0, 45.0, ba9 - ST.area)
segs9 = polys(f9(d9))
cap9 = [2 if s.distance(ST) < 25 else 3 for s in segs9]
w9, SHORTFALL[9] = make(9, segs9, lambda s: "판매" if s.distance(OPEN9) < 12 else "문화", gfa9 - st["gfa"], "지역문화원·상생", cap=cap9)
NEW[9] = [st] + w9
NOTE[9] = "구 역사 실제 위치 존치(대합실 관통 통로 8 m) · 역 앞마당 %s㎡ · 옛 1번 승강장 %s㎡ · 플랫폼 광장 %s㎡ · 지역문화원·상생동은 플랫폼 광장으로 열린 ㄷ자(깊이 %.1f m, 역사 25 m 안 2층·그 밖 3층)" % (
    f0(FORE.area), f0(PLAT1.area), f0(PPLZ.area), d9)

BLDb = [b for n in sorted(NEW) for b in NEW[n]]
LINKSb = list(V1["LINKS"])

# 판: ① 옛 1번 승강장 캐노피 · ②③ v1 그대로
DECKS = [dict(name="① 옛 1번 승강장 캐노피", g=PLAT1, z0=6.1, z1=6.5)] + [d for d in V1["DECKS"] if not d["name"].startswith("①")]
COLS = [(g, top) for (g, top) in V1["COLS"] if not g.intersects(V1["DECKS"][0]["g"].buffer(1.0))]
for y in np.arange(PLAT1.bounds[1] + 4, PLAT1.bounds[3] - 2, 12.0):
    for x in (PLAT1.bounds[0] + 2.0, PLAT1.bounds[2] - 2.0):
        if not PASS.buffer(1.0).contains(Point(x, y)) and not CORRb.buffer(0.5).contains(Point(x, y)):
            COLS.append((box(x - 0.4, y - 0.4, x + 0.4, y + 0.4), 6.1))

# 식재 — 새 동·역사·승강장 위는 빼고, 역 앞마당 대칭 2열(화랑로 축·석탑 둘레 제외) · 통경축 가로수
FOOT = unary_union([b["g"] for b in BLDb]).buffer(1.5)
NOTREE = unary_union([FOOT, EWB, PLAT1, ST.buffer(3), DECKS[1]["g"], DECKS[2]["g"], FORE])
TREESb = [(x, y, r) for (x, y, r) in M["TREES"] if not NOTREE.contains(Point(x, y))]
for x in (120.0, 128.0):
    for y in np.arange(274.0, 382.0, 8.0):
        if abs(y - HWARANG_Y) < 9 or Point(x, y).distance(PAGODA) < 10: continue
        TREESb.append((x, float(y), 3.0))
for yy in (EWB.bounds[1] + 3.0, EWB.bounds[3] - 3.0):
    for x in np.arange(196.0, 388, 8.0):
        if not (GATE_X[0] < x < GATE_X[1]): TREESb.append((float(x), float(yy), 3.2))

# 지면
Sb = dict(S); Sb["ROADS"] = {k: v for k, v in S["ROADS"].items() if k != "EW"}; Sb["LOTS"] = LOTSb; Sb["WALK"] = WALKb; Sb["PLZ"] = PLZb
Sb["GLASS"] = dict(S["GLASS"], ua=[0.0, 1.0], vb=[1.0, 0.0], none=True)    # 유리 지붕 없음 · 역사 모임지붕 용마루 = 남북

# 결과
RES = []
for l in LOTSb:
    no = l["no"]; g = l["g"]; bl = NEW[no]
    fp = unary_union([b["g"] for b in bl]).intersection(g)
    gfa = sum(b["gfa"] for b in bl)
    r0 = R1[no]
    RES.append(dict(no=no, A=g.area, A0=LOTG[no].area, ba0=r0["ba0"], ba_t={7: ba7, 9: ba9}.get(no, r0["ba_t"]), ba=fp.area, gfa0=r0["gfa0"], gfa=gfa, n=len(bl), n0=r0["n0"],
                    fmax=max(b["floors"] for b in bl if b["name"] != "구 경주역사"), f0max=r0["f0max"], hmax=max(b["h"] for b in bl if b["name"] != "구 경주역사"), note=NOTE[no], short=SHORTFALL.get(no, r0["short"]), form=r0["form"],
                    opA=KEEPb.intersection(g).area))
for r in RES:
    if r["no"] in (7, 9):
        print("%2d %-6s 면적 %6.0f → %6.0f  ba %6.0f (목표 %6.0f) GSI %.2f  gfa %6.0f → %6.0f  동 %d  최고 %d층 %.0f m  부족 %.0f | %s" % (
            r["no"], SHORT[r["no"]], r["A0"], r["A"], r["ba"], r["ba_t"], r["ba"] / r["A"], r["gfa0"], r["gfa"], r["n"], r["fmax"], r["hmax"], r["short"], r["note"]))
TB = sum(r["ba"] for r in RES); TG = sum(r["gfa"] for r in RES); TB0 = V1["TOT"]["ba0"]; TG0 = V1["TOT"]["gfa0"]
print("합계 획지 %.0f · 건축면적 %.0f → %.0f · GSI %.3f · 연면적 %.0f → %.0f (%+.0f) · 동 %d · 평균 %.2f층" % (TA, TB0, TB, TB / TA, TG0, TG, TG - TG0, len(BLDb), TG / TB))
pickle.dump(dict(S=Sb, BLD=BLDb, LINKS=LINKSb, TREES=TREESb, ST_FP=ST, DECKS=DECKS, COLS=COLS, RES=RES, NOTE=NOTE, CORR=CORRb, TERM=FORE, PASS=PASS, PLAT1=PLAT1, PPLZ=PPLZ,
                 KEEP=KEEPb, NO_GLASS=True, VARIANT="v1-b",
                 TOT=dict(boundary=TOT["boundary"], lot=TA, ba=TB, gfa=TG, ba0=TB0, gfa0=TG0)), open(os.path.join(OUTD, "mass_v1b.pkl"), "wb"))
print("saved mass_v1b.pkl")
