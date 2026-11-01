"""S1 설계 — 사용자 도로·블록(라이노 v1b, 계획 경계 120,547㎡) 위에 배치한다. 규제(고도·용도지역·보존지역 허용기준) 미적용 개념안.
사용자 지시(2026-10-08):
  · 검은 원(이전 안의 북측 시청·청년주거·복합문화·청년창업·커뮤니티 구간)만 중점 수정 — 시청 ∩자 매스, 주거 남향 평행 배열, TIME STRATA(저층 분동·들어 올린 지붕·공중가로·상층 데크).
  · 원 밖(공공체육·성동시장·체험판매·레지던시·구 역사·주차·관광지원·관광상가)은 이전 안의 프로그램·매스 유형을 유지하고, 수정한 도로에 맞춰 약간만 조정.
  · 초록색 = 녹지(늘림). 면적은 경계 안에서 닫히게, 매스는 깔끔하게.
출력: data/design.pkl"""
import pickle, os, math, sys
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
sys.path.insert(0, r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts")
from geomkit import polys, clean, rrect, mrr
SC = 1.339      # 사용자 라이노 모형 1단위 = 1.339 m (새 경계를 이전 경계 U에 맞춘 최적 닮음 비율, 경계 평균 잔차 3.6 m). 설계는 모형 단위로 하고 끝에서 실측 m로 환산한다.
g = pickle.load(open(os.path.join(D, "geo.pkl"), "rb"))
S, ROADS, WEDGE = g["S"], dict(g["ROADS"]), g["WEDGE"]
ROADS["WG"] = dict(g=WEDGE, grp="보행", nm="쐐기 광장", kind="보행 우선 쐐기 광장(수목 식재)", w=42.0)      # 사용자 도면의 빨간 쐐기 서피스 — 도로(보행 우선)로 둔다
C = pickle.load(open(r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean\data\context.pkl", "rb"))
OLD_STATION = [b["geom"] for b in C["B"] if abs(b["geom"].area - 1404.0) < 1.5 and b["floors"] == 2][0]

# ═══ 획지·공원 ═══════════════════════════════════════════════════════════════════════════════════════
LOTS, PARKS = [], []
def lot(name, use, cat, geom, prog, note="", zone="남"):
    ps = [p for p in polys(geom) if p.area > 150]
    if ps: LOTS.append(dict(name=name, use=use, cat=cat, prog=prog, geom=unary_union(ps), note=note, zone=zone))
def park(name, kind, geom, note=""): PARKS.append(dict(name=name, kind=kind, geom=unary_union([p for p in polys(geom) if p.area > 1]), note=note))

NE = g["NE"]; HOUSE_LOT = NE.intersection(box(100, 0, 230, 548)); NE_N = NE.difference(HOUSE_LOT)
CULT = g["CULT"]
CULT_W = CULT.intersection(box(100, 0, 150, 1000)); CULT_M = CULT.intersection(box(150, 0, 185, 1000)); CULT_E = CULT.intersection(box(185, 0, 300, 1000))
STAT = g["STAT"]; STAT_LOT = STAT.intersection(box(48, 100, 110, 215)); STAT_PARK = STAT.difference(STAT_LOT)
# ── 원 안(북측) — 신규 ──
lot("시청·의회 캠퍼스", "공공청사", "문화·교육·공공", g["CITY"], "시청·의회", "∩(ㄷ)자 본청 + 의회동 + 시민 파빌리온", "북")
lot("청년주거(남향 판상)", "주거", "주거", HOUSE_LOT, "청년주거", "남향 평행 4동 6F, 1층 생활상가·커뮤니티, 5층 스카이브리지", "북")
lot("복합문화·영화관", "문화", "문화·교육·공공", CULT_W, "복합문화·영화관", "문화 분동(2~4F) + 영화관 + 들어 올린 지붕", "북")
lot("청년창업·기업지원", "업무(창업지원)", "상업·업무", CULT_M, "청년창업·기업지원", "ㅁ자 5F + 모서리 6F, 1층 판매·지원", "북")
lot("청년·주민 커뮤니티", "공공(주민공동)", "문화·교육·공공", CULT_E, "청년주민커뮤니티", "3층 소동 분산 + 마을마당", "북")
# ── 원 밖 — 이전 안 유지 ──
lot("공공체육·생활시설", "공공(체육·생활SOC)", "여가·오락·체육", g["CREATIVE"], "공공운동·생활시설", "체육센터 2F + 생활SOC 3F + 옥외 운동장")
lot("성동시장 클러스터", "상업(전통시장 연계)", "판매·음식", g["RES_W"], "성동시장 연계 판매·체험", "2층 장옥 바(체험판매 포함) + 서변 3층 가로상점 + 삼층석탑 마당(r=22 m)")
lot("레지던시·공방 A", "창조산업", "창조산업", g["RES_E1"], "아티스트 레지던시·공방", "철도 사선 3층 바")
lot("레지던시·공방 B", "창조산업", "창조산업", g["RES_E2"], "아티스트 레지던시·공방", "철도 사선 3층 바")
lot("구경주역·근대역사관", "문화(역사)", "역사유산", STAT_LOT, "구경주역 이전", "구 역사(이전, 기존 형상 1,404㎡·2F) + 역사 광장")
lot("주차전용건축물", "주차", "교통·방문자", g["PARK_S"], "경주관광지원시설", "주동 5F + 2F 판매 라이너, 1단계 임시 평면주차")
lot("관광지원시설", "교통·관광지원", "교통·방문자", g["TOUR"], "경주관광지원시설", "3층 바(안내·환승 라운지) + 승강장 앞마당")
lot("관광객 휴게·판매상가 W", "상업(관광 휴게·판매)", "판매·음식", g["HALLS"], "경주관광지원시설", "ㄱ자 둘레형 3F")
lot("관광객 휴게·판매상가 E", "상업(관광 휴게·판매)", "판매·음식", g["GARDEN"], "경주관광지원시설", "ㄱ자 둘레형 3F")
LOTS.sort(key=lambda d: (-round(d["geom"].centroid.y / 60), d["geom"].centroid.x))
for i, d in enumerate(LOTS, 1): d["no"] = i; d["id"] = "Plot %d" % i; d["area"] = d["geom"].area
BY = {d["name"]: d for d in LOTS}
park("Park A", "북천 수변공원(북단·북동 녹지)", unary_union([g["TIP_PARK"], NE_N]), "북단 수변 녹지 + 북동 삼각 녹지")
park("Park B", "문화공원(고분 언덕·곡선 녹지띠)", unary_union([g["HILL"], g["SLIVER"]]), "원 안 서측: 고분 언덕 + 곡선 녹지띠(쐐기 광장 옆)")
park("Park C", "역전광장·근린공원", unary_union([STAT_PARK, g["SLV"]]), "구 역사 앞 광장(녹지)")
park("Park D", "종축 녹지띠", g["SPINE_GREEN"], "종축 서변 7 m 녹지띠")
for d in PARKS: d["area"] = d["geom"].area

# ═══ 매스 ════════════════════════════════════════════════════════════════════════════════════════
BUILD, COURTS, OPEN, RAILS, DECKS, ROOFG = [], [], [], [], [], []
FH = {"주거": 3.3, "업무": 3.8, "공공": 4.0, "문화": 4.5, "판매": 4.2, "체육": 6.5, "주차": 3.0, "역사": 4.5, "교통": 4.2, "창조": 4.2}
def add(L, geom, name, use, cat, floors, fh_key, retail_ground=False, role="건물", fh=None, note="", lift=None):
    for p in polys(geom):
        if p.area < 30: continue
        f = fh if fh is not None else FH[fh_key]
        BUILD.append(dict(lot=L["id"], lot_no=L["no"], name=name, use=use, cat=cat, geom=p, floors=floors, floor_h=f, h=round(floors * f, 2), retail_ground=retail_ground, role=role, area=p.area, note=note, lift=lift))
def bars(poly, ang, depth, gap, margin=3.0, min_len=18.0):
    inner = poly.buffer(-margin, join_style=2)
    if inner.is_empty: return []
    c = inner.centroid; rot = affinity.rotate(inner, -ang, origin=(c.x, c.y)); minx, miny, maxx, maxy = rot.bounds; out = []; y = miny
    while y + depth <= maxy + 1e-6:
        for p in polys(box(minx - 1, y, maxx + 1, y + depth).intersection(rot)):
            if p.bounds[2] - p.bounds[0] >= min_len and p.area > depth * min_len * 0.8: out.append(affinity.rotate(p, ang, origin=(c.x, c.y)))
        y += depth + gap
    return out
def canopy(geom, z, th=0.6): return dict(geom=geom, dz=z, th=th)
def ring_court(poly, setback, depth, gate_w=12.0, gate_min_edge=52.0, n_gates=1, min_piece=150):
    inner = poly.buffer(-setback, join_style=2); court = inner.buffer(-depth, join_style=2); ring = inner.difference(court); edges = []
    for part in polys(inner):
        cs = list(part.exterior.coords)
        for i in range(len(cs) - 1):
            a, b = np.array(cs[i]), np.array(cs[i + 1]); Lg = np.linalg.norm(b - a)
            if Lg >= gate_min_edge: edges.append((Lg, a, b, part))
    for Lg, a, b, part in sorted(edges, key=lambda e: -e[0])[:n_gates]:
        u = (b - a) / Lg; n = np.array([-u[1], u[0]]); mid = (a + b) / 2
        if not part.contains(Point(*(mid + n * 2))): n = -n
        c = mid + n * depth / 2; ring = ring.difference(rrect(c[0], c[1], gate_w, depth + 6, math.degrees(math.atan2(u[1], u[0]))))
    return [x for x in clean(ring, min_piece, depth * 0.55)], court

# ═══ 원 안(북측): TIME STRATA ═════════════════════════════════════════════════════════════════════
# 시청 — 사용자 ∩자 형태를 현실 면적(지상 약 25,000㎡)에 맞춰 키운 5층 본청 + 의회동 + 시민 파빌리온
L = BY["시청·의회 캠퍼스"]
cityU = box(24, 459, 80, 529).difference(box(38, 459, 67, 511))      # 사용자 ∩자 그대로(모형 단위)
add(L, cityU, "본청 사무동(∩자)", "시청·의회", "문화·교육·공공", 5, "공공", note="사용자 ∩자 형태 유지. 개구부 남향(시민마당)", lift=canopy(box(24.5, 511.5, 79.5, 528.5), 3.2))
add(L, box(86, 468, 100, 512), "의회동", "시청·의회", "문화·교육·공공", 3, "문화", fh=5.0, note="종축 쪽 의회·시민홀")
add(L, box(42, 468, 63, 486), "시민 파빌리온(민원·카페)", "시청·의회", "문화·교육·공공", 2, "공공", retail_ground=True, note="마당 안 저층 시민동")
COURTS.append((L["id"], "시민마당", box(38, 459, 67, 511).difference(box(42, 468, 63, 486))))
ROOFG += [("city", cityU, 20.0), ("council", box(86, 468, 100, 512), 15.0)]
# 청년주거 — 남향 평행 4동(사용자 배열), 6F, 1층 생활상가, 5층 스카이브리지
L = BY["청년주거(남향 판상)"]; YS = [443.0, 472.5, 502.0, 531.5]; HW = 91.0; HD = 12.0
for i, y in enumerate(YS):
    b = box(119, y, 119 + HW, y + HD)
    lf = canopy(box(119 + HW - 34, y + 0.5, 119 + HW - 0.5, y + HD - 0.5), 3.0) if i % 2 == 0 else canopy(box(120.5, y + 0.5, 154, y + HD - 0.5), 3.0)
    add(L, b, "청년주거 %d동" % (i + 1), "청년주거", "주거", 6, "주거", retail_ground=True, note="남향(장변이 남쪽), 6F, 1층 생활상가·돌봄", lift=lf); ROOFG.append(("house", b, 6 * 3.3))
COURTS.append((L["id"], "주거 사이 마당(남향 정원)", unary_union([box(119, y + HD, 119 + HW, YS[i + 1]) for i, y in enumerate(YS[:-1])])))
OPEN.append((L["id"], "단지 앞 광장", box(114, 436, 218, 443).intersection(L["geom"]), "#ece7de"))
# 복합문화·영화관 — 저층 분동 + 들어 올린 지붕
L = BY["복합문화·영화관"]; inn = L["geom"].buffer(-4, join_style=2); x0, y0, x1, y1 = inn.bounds
for (cx, cy, w, h, fl, key) in ((x0, y0 + 2, 14, 32, 2, "문화"), (x0, y0 + 40, 14, 32, 3, "문화"), (x0 + 18, y0 + 40, 14, 32, 4, "문화")):
    b = box(cx, cy, cx + w, cy + h).intersection(inn)
    add(L, b, "문화 분동(%dF)" % fl, "복합문화·영화관", "문화·교육·공공", fl, key, fh=4.5, lift=canopy(box(cx - 3, cy + 2, cx + w + 3, cy + h - 2).intersection(L["geom"]), 3.0)); ROOFG.append(("culture", b, fl * 4.5))
add(L, box(x0 + 18, y0 + 2, x0 + 32, y0 + 34).intersection(inn), "영화관(6개관)", "복합문화·영화관", "여가·오락·체육", 3, "문화", fh=5.5)
used = unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]]); OPEN.append((L["id"], "문화 마당", L["geom"].buffer(-3).difference(used.buffer(0.5)), "#ece7de"))
# 청년창업·기업지원 — ㅁ자 5F + 모서리 6F
L = BY["청년창업·기업지원"]
ring, court = ring_court(L["geom"], 4.0, 13.0, gate_min_edge=40, n_gates=1)
for p in ring:
    x0_, y0_, x1_, y1_ = p.bounds; corner = box(x0_ - 1, y1_ - 22, x0_ + 22, y1_ + 1).intersection(p)
    add(L, p.difference(corner.buffer(0.01)), "청년창업·기업지원", "청년창업·기업지원", "상업·업무", 5, "업무", retail_ground=True, lift=canopy(p.difference(corner).buffer(-2.0, join_style=2), 3.0))
    add(L, corner, "청년창업·기업지원(모서리 6F)", "청년창업·기업지원", "상업·업무", 6, "업무", retail_ground=True)
ROOFG.append(("startup", unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]]), 20.0)); COURTS.append((L["id"], "창업 중정", court))
# 청년·주민 커뮤니티 — 3층 소동 분산
L = BY["청년·주민 커뮤니티"]; inn = L["geom"].buffer(-4, join_style=2); x0, y0, x1, y1 = inn.bounds
for i in range(2):
    for j in range(3):
        b = box(x0 + 3 + i * 15, y0 + 4 + j * 26, x0 + 3 + i * 15 + 11, y0 + 4 + j * 26 + 20).intersection(inn)
        if b.area > 90: add(L, b, "청년·주민 커뮤니티 소동", "청년주민커뮤니티", "문화·교육·공공", 3, "공공", fh=4.0)
used = unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]]); OPEN.append((L["id"], "마을마당", inn.difference(used.buffer(1)), "#cfe6b4"))

# ═══ 원 밖: 이전 안(k2) 매스 유형 유지 ══════════════════════════════════════════════════════════════
L = BY["공공체육·생활시설"]; inner = L["geom"].buffer(-4, join_style=2); c = inner.centroid
ang = 49.5
hall = rrect(c.x, c.y, 44, 26, ang).intersection(inner); add(L, hall, "공공체육센터", "공공운동·생활시설", "여가·오락·체육", 2, "체육", fh=6.5)
soc = rrect(c.x + 20 * math.cos(math.radians(ang + 90)), c.y + 20 * math.sin(math.radians(ang + 90)), 30, 12, ang).intersection(inner).difference(hall.buffer(1)); add(L, soc, "생활SOC 복합동", "공공운동·생활시설", "문화·교육·공공", 3, "공공")
used = unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]]); OPEN.append((L["id"], "옥외 운동장", L["geom"].buffer(-3).difference(used.buffer(2)), "#d98a6a"))
L = BY["성동시장 클러스터"]; inn = L["geom"].buffer(-3.5, join_style=2)
tower = Point(52, 262).buffer(22 / SC); OPEN.append((L["id"], "삼층석탑 마당", tower.intersection(inn), "#e9d9bd"))
fr = box(inn.bounds[0], inn.bounds[1], inn.bounds[0] + 14, inn.bounds[3]).intersection(inn).difference(tower.buffer(3))
add(L, fr, "성동시장 가로상점(서변)", "성동시장 연계 판매·체험", "판매·음식", 3, "판매")
for p in bars(inn.difference(fr.buffer(6)).difference(tower.buffer(3)), 0, 10.0, 6.0, margin=0.5, min_len=24): add(L, p, "성동시장 장옥", "성동시장 연계 판매·체험", "판매·음식", 2, "판매")
used = unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]]); OPEN.append((L["id"], "마켓 골목", inn.difference(used.buffer(0.3)).difference(tower), "#ece7de"))
for nm in ("레지던시·공방 A", "레지던시·공방 B"):
    L = BY[nm]
    for p in bars(L["geom"], 58.4, 10.0, 5.0, margin=3.5, min_len=22): add(L, p, nm, "아티스트 레지던시·공방", "창조산업", 3, "창조")
    used = unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]]) if any(b["lot"] == L["id"] for b in BUILD) else Polygon()
    OPEN.append((L["id"], "공방 마당", L["geom"].buffer(-3.0).difference(used.buffer(0.4)), "#ece7de"))
# 구 경주역(이전): 기존 형상 그대로, 장축을 남북(철도 방향)으로
L = BY["구경주역·근대역사관"]
cs = list(OLD_STATION.minimum_rotated_rectangle.exterior.coords); k = max(range(2), key=lambda j: math.dist(cs[j], cs[j + 1]))
st_ang = math.degrees(math.atan2(cs[k + 1][1] - cs[k][1], cs[k + 1][0] - cs[k][0])) % 180
base = affinity.rotate(OLD_STATION, 90 - st_ang, origin=OLD_STATION.centroid); base = affinity.translate(base, -base.centroid.x, -base.centroid.y); base = affinity.scale(base, 1 / SC, 1 / SC, origin=(0, 0))
best = (-1, None); inn = L["geom"].buffer(-0.01)
for x in np.arange(48, 110, 1.0):
    for y in np.arange(110, 210, 1.0):
        gg = affinity.translate(base, x, y)
        if inn.contains(gg):
            dd = L["geom"].exterior.distance(gg)
            if dd > best[0]: best = (dd, (x, y))
ST = affinity.translate(base, *best[1])
add(L, ST, "구경주역(이전)·근대역사관", "구경주역 이전", "역사유산", 2, "역사", note="기존 건물 형상 그대로(NGII 1,404㎡·2F). 근대역사관·전시장 겸용")
used = ST; OPEN.append((L["id"], "역사 광장", L["geom"].buffer(-2).difference(used.buffer(1.5)), "#ece7de"))
L = BY["관광지원시설"]; inn = L["geom"].buffer(-3.5, join_style=2)
b = box(118, 112, 136, 198).intersection(inn); add(L, b, "경주관광지원시설(안내·환승)", "경주관광지원시설", "교통·방문자", 3, "교통"); OPEN.append((L["id"], "승강장 앞마당", inn.difference(b.buffer(1)), "#ece7de"))
L = BY["주차전용건축물"]; inn = L["geom"].buffer(-3.0, join_style=2)
P1 = box(163, 106, 205, 202).intersection(inn); add(L, P1, "주차전용건축물(주동)", "주차타워", "교통·방문자", 5, "주차", role="주차")
add(L, box(205, 130, 211, 190).intersection(inn), "주차동 라이너(판매·공방)", "주차타워", "판매·음식", 2, "판매", fh=4.2)
used = unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]]); OPEN.append((L["id"], "1단계 임시 평면주차", inn.difference(used.buffer(2)), "#cfcfcf"))
for nm in ("관광객 휴게·판매상가 W", "관광객 휴게·판매상가 E"):
    L = BY[nm]; ring, court = ring_court(L["geom"], 3.5, 12.0, gate_min_edge=45, n_gates=1, min_piece=200)
    for p in ring: add(L, p, nm, "관광객 중심 휴게·판매상가", "판매·음식", 3, "판매")
    COURTS.append((L["id"], "관광상가 앞마당", court))
# 철도 흔적(궤간 1,435 mm 두 줄 × 4벌) — 플랫폼 광장(원 아래 경계)만
pz = ROADS["PZ"]["g"]
for xr in (18, 38, 58, 78, 130, 148, 166, 184):
    for dx in (0, 1.435 / SC): RAILS.append(LineString([(xr + dx, 300), (xr + dx, 357)]).intersection(pz))
RAILS = [r for r in RAILS if not r.is_empty and r.length > 2]

# ═══ 공중가로·상층 데크 — 원 안(N 351~546) 종축 위 완만한 경사 데크(+4.5 → 16.5 m, 1:16) + 가지·스카이브리지 ═════════════════════════
def zr(n): return 4.5 + (n - 351.0) * (12.0 / 195.0)
MAIN = [(111.5, n, zr(n)) for n in list(np.arange(351, 546, 9.75)) + [546]]
DECKS.append(dict(name="공중가로 T(종축 경사 데크)", kind="main", w=5.0, pts=MAIN, note="종축 위 +4.5~16.5 m, 기울기 1:16(무장애)"))
def flat(name, p0, p1, z, w=4.0, kind="branch", note=""): DECKS.append(dict(name=name, kind=kind, w=w, pts=[(p0[0], p0[1], z), (p1[0], p1[1], z)], note=note))
flat("가지 E1(문화·창업 지붕 연결)", (111.5, 392), (206, 392), zr(392), 4.0, note="문화 분동·창업·커뮤니티 위 상층 데크")
flat("가지 W1(쐐기 녹지 위)", (111.5, 392), (62, 392), zr(392), 4.0, note="문화공원 위 산책 데크")
flat("가지 W2(시청 브리지)", (111.5, 490), (100, 490), zr(490), 3.5, note="시청 의회동 연결")
flat("가지 N(주거 4동 연결)", (111.5, 538), (122, 538), zr(538), 3.5, note="종축 → 주거 4동 5F")
for i, (n0, n1) in enumerate(zip(YS[:-1], YS[1:])):
    for xx in (128, 200): flat("스카이브리지 %d-%d" % (i + 1, i + 2), (xx, n0 + HD), (xx, n1), 16.5, 3.0, kind="skybridge", note="주거동 5F 연결")

# ═══ 모형 단위 → 실측 m 환산(평면만 SC배, 높이·층고는 실측 그대로) ═══════════════════════════════════════════════
import shapely
def Z(g_):
    r = affinity.scale(g_, SC, SC, origin=(0, 0))
    if r.geom_type in ("Polygon", "MultiPolygon"):
        if not r.is_valid: r = shapely.make_valid(r)
        r = unary_union([q for q in polys(r) if q.area > 1e-6]) if not r.is_empty else r
        r = shapely.set_precision(r, 0.0005)
    return r
S = Z(S); WEDGE = Z(WEDGE)
for d in LOTS: d["geom"] = Z(d["geom"]); d["area"] = d["geom"].area
for d in PARKS: d["geom"] = Z(d["geom"]); d["area"] = d["geom"].area
for k, r in ROADS.items(): r["g"] = Z(r["g"]); r["w"] = round(r["w"] * SC * 2) / 2.0
for b in BUILD:
    b["geom"] = Z(b["geom"]); b["area"] = b["geom"].area
    if b.get("lift"): b["lift"] = dict(geom=Z(b["lift"]["geom"]), dz=b["lift"]["dz"], th=b["lift"]["th"])
COURTS = [(a_, n_, Z(g_)) for a_, n_, g_ in COURTS]; OPEN = [(a_, n_, Z(g_), c_) for a_, n_, g_, c_ in OPEN]
RAILS = [Z(r_) for r_ in RAILS]; ROOFG = [(k_, Z(g_), z_) for k_, g_, z_ in ROOFG]
for dk in DECKS: dk["pts"] = [(x * SC, y * SC, z) for x, y, z in dk["pts"]]
cu = C["U"].centroid; REG = dict(tx=cu.x - S.centroid.x, ty=cu.y - S.centroid.y)
pickle.dump(REG, open(os.path.join(D, "reg.pkl"), "wb"))
out = dict(U=S, LOTS=LOTS, PARKS=PARKS, BUILD=BUILD, COURTS=COURTS, OPEN=OPEN, RAILS=RAILS, DECKS=DECKS, ROOFG=ROOFG, ROADS=ROADS, WEDGE=WEDGE, SC=SC, REG=REG)
pickle.dump(out, open(os.path.join(D, "design.pkl"), "wb"))
from shapely.strtree import STRtree
gs = [b["geom"] for b in BUILD]; tr = STRtree(gs); ov = []
for i, gg in enumerate(gs):
    for j in tr.query(gg):
        if j > i and gg.intersection(gs[j]).area > 0.5: ov.append((BUILD[i]["name"], BUILD[j]["name"], round(gg.intersection(gs[j]).area, 1)))
lotgeom = {d["id"]: d["geom"].buffer(0.05) for d in LOTS}
outl = [(b["name"], b["lot"], round(b["geom"].difference(lotgeom[b["lot"]]).area, 1)) for b in BUILD if b["geom"].difference(lotgeom[b["lot"]]).area > 0.5]
print("획지 %d개 공원 %d개 | 매스 %d개, 겹침 %d건 %s, 획지 밖 %d건 %s" % (len(LOTS), len(PARKS), len(BUILD), len(ov), ov[:4], len(outl), outl[:4]))
for d in LOTS: print("%2d %-22s %7.0f㎡ %s" % (d["no"], d["name"], d["area"], d["zone"]))
for d in PARKS: print("   %-8s %-26s %7.0f㎡" % (d["name"], d["kind"], d["area"]))
roadsum = sum(r["g"].area for r in ROADS.values()); chk = sum(d["area"] for d in LOTS) + sum(d["area"] for d in PARKS) + roadsum
print("닫힘: 획지 %.0f + 공원 %.0f + 도로 %.0f = %.1f / 경계 %.1f (차 %.2f)" % (sum(d["area"] for d in LOTS), sum(d["area"] for d in PARKS), roadsum, chk, S.area, chk - S.area))
gfa = sum(b["area"] * b["floors"] for b in BUILD)
print("연면적 %.0f㎡ | 시청 지상 %.0f㎡ | 청년주거 %.0f㎡" % (gfa, sum(b["area"] * b["floors"] for b in BUILD if b["lot"] == BY["시청·의회 캠퍼스"]["id"]), sum(b["area"] * b["floors"] for b in BUILD if b["lot"] == BY["청년주거(남향 판상)"]["id"])))
