"""K2 깔끔한 매스 — 획지마다 하나의 분명한 유형(ㅁ·ㄷ·ㄱ자, 평행 바, 박스)으로 짓는다. 고도제한·켜 규칙은 적용하지 않는다(규제 무시 안).
층수는 프로그램에서 정하고, 20 m를 넘는 매스는 표시해 두었다가 규제를 적용할 때 줄이도록 한다.
출력: scratch/clean_mass.pkl"""
import pickle, sys, math
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
import os as _os; SP = _os.environ.get("PLAN_SP", r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad")   # 입력 pkl 폴더. 재현 시 PLAN_SP=<work/20261005_plan_clean/data>
PM = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts"
sys.path.insert(0, PM)
from geomkit import polys, clean, rrect, mrr

LP = pickle.load(open(SP + r"\lots.pkl", "rb")); LOTS, PARKS = LP["LOTS"], LP["PARKS"]
C = pickle.load(open(SP + r"\context.pkl", "rb")); U = C["U"]

BY = {d["name"]: d for d in LOTS}
FH = {"주거": 3.2, "업무": 3.8, "공공": 4.0, "문화": 4.5, "판매": 4.2, "체육": 6.5, "주차": 3.0, "역사": 4.5, "교통": 4.2, "창조": 4.2}
BUILD, COURTS, OPEN = [], [], []     # OPEN: 포장 마당·광장(획지 안 공지)

def add(lot, geom, name, use, cat, floors, fh_key, retail_ground=False, role="건물", fh=None, note=""):
    """geom 은 한 건물(여러 조각이면 조각마다 건물). floors·fh 로 높이 결정. retail_ground: 1층을 판매·음식으로."""
    for g in polys(geom):
        if g.area < 30: continue
        f = fh if fh is not None else FH[fh_key]
        BUILD.append(dict(lot=lot["id"], lot_no=lot["no"], name=name, use=use, cat=cat, geom=g, floors=floors, floor_h=f, h=round(floors * f, 2),
                          retail_ground=retail_ground, role=role, area=g.area, note=note))

def ring_court(poly, setback, depth, gate_w=12.0, gate_min_edge=52.0, n_gates=2, min_piece=150):
    """안쪽 오프셋 링(둘레 중정형). 긴 변 중 가장 긴 n_gates 개(≥gate_min_edge)에만 가운데 통경을 하나씩 낸다 → ㅁ·ㄷ자로 읽히게.
    반환 (링 조각들, 중정)"""
    inner = poly.buffer(-setback, join_style=2)
    court = inner.buffer(-depth, join_style=2)
    ring = inner.difference(court)
    edges = []
    for part in polys(inner):
        cs = list(part.exterior.coords)
        for i in range(len(cs) - 1):
            a, b = np.array(cs[i]), np.array(cs[i + 1]); L = np.linalg.norm(b - a)
            if L >= gate_min_edge: edges.append((L, a, b, part))
    for L, a, b, part in sorted(edges, key=lambda e: -e[0])[:n_gates]:
        u = (b - a) / L; n = np.array([-u[1], u[0]]); mid = (a + b) / 2
        if not part.contains(Point(*(mid + n * 2))): n = -n
        c = mid + n * depth / 2
        ring = ring.difference(rrect(c[0], c[1], gate_w, depth + 6, math.degrees(math.atan2(u[1], u[0]))))
    return [g for g in clean(ring, min_piece, depth * 0.55)], court

def parallel_bars(poly, ang, depth, gap, margin=3.0, min_len=22.0, along_trim=0.0):
    """각도 ang 방향으로 긴 평행 바(폭 depth, 바 사이 gap)를 획지 안쪽에 깐다. 바는 획지를 가로지르는 한 덩어리."""
    inner = poly.buffer(-margin, join_style=2)
    if inner.is_empty: return []
    c = inner.centroid
    rot = affinity.rotate(inner, -ang, origin=(c.x, c.y))
    minx, miny, maxx, maxy = rot.bounds
    out = []; y = miny
    while y + depth <= maxy + 1e-6:
        strip = box(minx - 1, y, maxx + 1, y + depth).intersection(rot)
        for p in polys(strip):
            if p.bounds[2] - p.bounds[0] >= min_len and p.area > depth * min_len * 0.8:
                out.append(affinity.rotate(p, ang, origin=(c.x, c.y)))
        y += depth + gap
    return out

def gate_cut(g, cx, cy, w, h, ang=0):
    return g.difference(rrect(cx, cy, w, h, ang))

# ══════════════════════════════════════════════════════════════════════════════
def m_sport():
    L = BY["공공체육·생활시설"]; inner = L["geom"].buffer(-4, join_style=2); c = inner.centroid
    hall = rrect(c.x - 6, c.y - 4, 56, 38, 0).intersection(inner)
    add(L, hall, "공공체육센터", "공공운동·생활시설", "여가·오락·체육", 2, "체육", fh=6.5)
    soc = rrect(c.x + 22, c.y - 38, 38, 14, 0).intersection(inner)
    add(L, soc, "생활SOC 복합동", "공공운동·생활시설", "문화·교육·공공", 3, "공공")
    courts = unary_union([rrect(c.x - 24, c.y + 30, 30, 18, 0), rrect(c.x + 10, c.y + 30, 30, 18, 0)]).intersection(inner)
    OPEN.append((L["id"], "옥외 운동장", courts, "#d98a6a"))

def housing_ring(name, floors, depth, retail=False, cross=False, gate_min=52, n_gates=2):
    L = BY[name]
    ring, court = ring_court(L["geom"], 4.0, depth, gate_min_edge=gate_min, n_gates=n_gates)
    for g in ring: add(L, g, name, "청년주거", "주거", floors, "주거", retail_ground=retail)
    if cross:
        for cp in polys(court):
            Lc, Wc, ang = mrr(cp)
            if Lc > 90:
                bar = rrect(cp.centroid.x, cp.centroid.y, Wc + 4, depth, ang + 90).intersection(L["geom"].buffer(-4, join_style=2)).difference(unary_union(ring).buffer(0.5))
                add(L, bar, name + " 횡동", "청년주거", "주거", floors, "주거")
                court = court.difference(bar.buffer(0.01))
    COURTS.append((L["id"], name + " 중정", court))

def m_housing():
    housing_ring("청년주거 서", 6, 12.5, retail=True, n_gates=2)
    housing_ring("청년주거 북동", 5, 12.5, retail=True, n_gates=1)
    housing_ring("청년주거 동", 4, 12.0, n_gates=1)
    L = BY["청년주거 동남(연립)"]
    for g in parallel_bars(L["geom"], 0, 13.0, 8.0, margin=3.5, min_len=20):
        add(L, gate_cut(g, g.centroid.x, g.centroid.y, 7, 20, 0), "청년주거 동남(연립)", "청년주거", "주거", 3, "주거")
    OPEN.append((L["id"], "골목마당", L["geom"].buffer(-3.5).difference(unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]]).buffer(0.4)), "#cfe6b4"))

def m_city():
    L = BY["시청·의회 캠퍼스"]; inner = L["geom"].buffer(-4.5, join_style=2); x0, y0, x1, y1 = inner.bounds
    D = 15.0
    # 민원·시민동: 서변 연속 4층 바(원화로 가로벽), 서측 골목 앵커(361,160·361,188)에 통경
    pod = box(x0, y0, x0 + 19, y1)
    for gy in (361160, 361188): pod = pod.difference(box(x0 - 1, gy - 6, x0 + 20, gy + 6))
    add(L, pod, "민원·시민동", "시청·의회", "문화·교육·공공", 3, "공공", retail_ground=True)
    bx0, bx1 = x0 + 27, x1 - 3
    north = box(bx0, y1 - 6 - D, bx1, y1 - 6); south = box(bx0, y0 + 6, bx1, y0 + 6 + D); west = box(bx0, y0 + 6, bx0 + D, y1 - 6)
    west = west.difference(unary_union([north, south]).buffer(0.2)); add(L, unary_union([north, south]), "본청 사무동(북·남)", "시청·의회", "문화·교육·공공", 5, "공공")
    add(L, west, "본청 사무동(서 연결)", "시청·의회", "문화·교육·공공", 3, "공공")
    cx, cy = x1 - 26, (y0 + y1) / 2
    add(L, rrect(cx, cy, 36, 31, 0), "의회동", "시청·의회", "문화·교육·공공", 4, "문화")
    court = box(bx0 + D, y0 + 6 + D, x1, y1 - 6 - D).difference(rrect(cx, cy, 36, 31, 0))
    COURTS.append((L["id"], "시민마당", court))

def m_culture():
    L = BY["복합문화·영화관"]; inner = L["geom"].buffer(-4.5, join_style=2); x0, y0, x1, y1 = inner.bounds
    fr = box(x0, y0, x0 + 17, y1)
    for gy in (y0 + (y1 - y0) / 3, y0 + 2 * (y1 - y0) / 3): fr = fr.difference(box(x0 - 1, gy - 6, x0 + 18, gy + 6))
    add(L, fr, "문화 가로상점", "복합문화·영화관", "판매·음식", 3, "판매")
    cc = unary_union([box(x0 + 30, y1 - 22, x0 + 100, y1), box(x0 + 30, y1 - 62, x0 + 48, y1)]).intersection(inner)
    add(L, cc, "복합문화센터", "복합문화·영화관", "문화·교육·공공", 4, "문화", retail_ground=False)
    add(L, box(x1 - 48, y0 + 4, x1, y0 + 38).intersection(inner), "영화관(6개관)", "복합문화·영화관", "여가·오락·체육", 3, "문화", fh=5.5)
    COURTS.append((L["id"], "문화광장", box(x0 + 52, y0 + 4, x1 - 52, y1 - 26).intersection(inner)))

def m_startup():
    L = BY["청년창업·기업지원"]
    ring, court = ring_court(L["geom"], 4.0, 14.0, gate_min_edge=60, n_gates=1)
    # 둘레 6층 + 북서 모서리 한 곳만 8층(주축 S와 B가로가 만나는 모서리 랜드마크)
    for g in ring:
        x0, y0, x1, y1 = g.bounds
        corner = box(x0 - 1, y1 - 30, x0 + 30, y1 + 1).intersection(g)
        add(L, g.difference(corner.buffer(0.01)), "청년창업·기업지원", "청년창업·기업지원", "상업·업무", 6, "업무", retail_ground=True)
        add(L, corner, "청년창업·기업지원(모서리 8층)", "청년창업·기업지원", "상업·업무", 8, "업무", retail_ground=True)
    COURTS.append((L["id"], "창업 중정", court))

def m_comm():
    L = BY["청년·주민 커뮤니티"]; inner = L["geom"].buffer(-4, join_style=2)
    cells = []
    x0, y0, x1, y1 = inner.bounds
    for i in range(2):
        for j in range(3):
            cx = x0 + 18 + i * 28; cy = y0 + 16 + j * 31
            g = rrect(cx, cy, 20, 18, 0)
            if inner.contains(g): cells.append(g)
    for g in cells: add(L, g, "청년·주민 커뮤니티", "청년주민커뮤니티", "문화·교육·공공", 3, "공공")
    OPEN.append((L["id"], "마을마당", inner.difference(unary_union(cells).buffer(1)), "#ece7de"))

def m_market():
    L = BY["성동시장 클러스터"]; inner = L["geom"].buffer(-4, join_style=2)
    tower = Point(219660, 360816); her = tower.buffer(22)
    OPEN.append((L["id"], "삼층석탑 마당", her.intersection(inner), "#e9d9bd"))
    avail = inner.difference(her.buffer(3))
    for g in parallel_bars(avail, 0, 10.0, 6.0, margin=0.5, min_len=30):
        add(L, g, "성동시장 장옥", "성동시장 연계 판매·체험", "판매·음식", 2, "판매")
    # 서변 3층 상점 모듈: 바의 서쪽 끝 14 m를 3층으로 올림(원화로 가로벽)
    # → 별도 건물로 만들면 겹치므로 서변 띠를 바에서 떼어 3층 매스로
    fr = box(inner.bounds[0], inner.bounds[1], inner.bounds[0] + 14, inner.bounds[3]).difference(her.buffer(3)).intersection(inner)
    # 기존 바에서 서변 14 m를 빼고 다시 만든다
    old = [b for b in BUILD if b["lot"] == L["id"]]
    for b in old: BUILD.remove(b)
    for b in old:
        g = b["geom"].difference(box(inner.bounds[0] - 1, inner.bounds[1] - 1, inner.bounds[0] + 14, inner.bounds[3] + 1))
        add(L, g, "성동시장 장옥", "성동시장 연계 판매·체험", "판매·음식", 2, "판매")
    add(L, fr, "성동시장 가로상점(원화로)", "성동시장 연계 판매·체험", "판매·음식", 3, "판매")
    used = unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]])
    OPEN.append((L["id"], "마켓 골목", inner.difference(used.buffer(0.3)).difference(her), "#ece7de"))

def m_experience():
    L = BY["체험판매 거리"]; inner = L["geom"].buffer(-4, join_style=2); x0, y0, x1, y1 = inner.bounds
    w = (x1 - x0 - 12) / 2
    for xs in (x0, x1 - w):
        add(L, box(xs, y0, xs + w, y1), "체험판매 점포", "성동시장 연계 판매·체험", "판매·음식", 2, "판매")
    OPEN.append((L["id"], "체험 거리", box(x0 + w, y0, x1 - w, y1), "#ece7de"))

def m_residency():
    for nm, ang, bd, gp in (("레지던시·공방 A", 56.1, 11.0, 6.0), ("레지던시·공방 B", 56.1, 10.0, 5.0), ("레지던시·공방 C", 56.1, 10.0, 5.0)):
        L = BY[nm]
        for g in parallel_bars(L["geom"], ang, bd, gp, margin=3.5, min_len=26):
            add(L, g, nm, "아티스트 레지던시·공방", "창조산업", 3, "창조")
        used = unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]]) if any(b["lot"] == L["id"] for b in BUILD) else Polygon()
        OPEN.append((L["id"], "공방 마당", L["geom"].buffer(-3.5).difference(used.buffer(0.4)), "#ece7de"))

def m_heritage():
    """구 경주역: 기존 건물(국토지리정보원 연속수치지도 폴리곤, 1,404㎡·22꼭짓점·2F)을 형상 그대로 이전한다(사용자 지시 2026-10-05).
    형상은 건드리지 않고 장축만 획지 장축에 맞춰 회전, 획지 안 최대 이격 위치에 놓는다. 근대역사관·전시장은 이 건물이 겸한다(별동 없음)."""
    L = BY["구경주역·근대역사관"]
    src = [b["geom"] for b in C["B"] if abs(b["geom"].area - 1404.0) < 1.5 and b["floors"] == 2 and b["geom"].intersects(U)]
    assert len(src) == 1, "구 경주역 기존 건물 폴리곤을 찾지 못함"
    g0 = src[0]
    cs = list(L["geom"].exterior.coords)
    i = max(range(len(cs) - 1), key=lambda k: math.dist(cs[k], cs[k + 1]))
    lot_ang = math.degrees(math.atan2(cs[i + 1][1] - cs[i][1], cs[i + 1][0] - cs[i][0])) % 180              # 획지 장축(≈56.06°)
    xs, ys = g0.minimum_rotated_rectangle.exterior.coords.xy
    k = max(range(2), key=lambda j: math.dist((xs[j], ys[j]), (xs[j + 1], ys[j + 1])))
    st_ang = math.degrees(math.atan2(ys[k + 1] - ys[k], xs[k + 1] - xs[k])) % 180                           # 건물 장축(≈89.3°, 남북)
    rot = (lot_ang - st_ang + 90) % 180 - 90
    base = affinity.rotate(g0, rot, origin=g0.centroid); base = affinity.translate(base, -base.centroid.x, -base.centroid.y)
    c0 = L["geom"].centroid; best = (-1.0, None); inner = L["geom"].buffer(-0.01)
    for dx in np.arange(-40, 40.1, 1.0):
        for dy in np.arange(-40, 40.1, 1.0):
            g = affinity.translate(base, c0.x + dx, c0.y + dy)
            if inner.contains(g):
                d = L["geom"].exterior.distance(g)
                if d > best[0]: best = (d, (c0.x + dx, c0.y + dy))
    st = affinity.translate(base, *best[1])
    print("구 경주역 이전: 원형 %.0f㎡ 회전 %.2f° 획지 이격 %.1f m, 중심 (%.1f, %.1f)" % (st.area, rot, best[0], best[1][0], best[1][1]))
    add(L, st, "구경주역(이전)·근대역사관", "구경주역 이전", "역사유산", 2, "역사", note="기존 건물 형상 그대로(NGII 1,404㎡), 장축을 획지에 맞춰 %.1f° 회전해 이전. 근대역사관·전시장 겸용" % rot)
    OPEN.append((L["id"], "역사 광장", L["geom"].buffer(-2).difference(st.buffer(1.5)), "#ece7de"))

def m_tour():
    L = BY["관광지원시설"]; inner = L["geom"].buffer(-4, join_style=2); x0, y0, x1, y1 = inner.bounds
    bar = box(x0 + 6, y0 + 8, x0 + 26, y1 - 14).intersection(inner)
    add(L, bar, "경주관광지원시설", "경주관광지원시설", "교통·방문자", 3, "교통")
    OPEN.append((L["id"], "승강장 앞마당", inner.difference(bar.buffer(1)), "#ece7de"))

def m_parking():
    L = BY["주차전용건축물"]; inner = L["geom"].buffer(-3.0, join_style=2); x0, y0, x1, y1 = inner.bounds
    P1 = box(x0 + 2, y0 + 8, x0 + 36, y1 - 2).intersection(inner)
    P2 = box(x0 + 2, y0 + 2, x0 + 66, y0 + 28).intersection(inner).difference(P1.buffer(0.1))
    P3 = box(x0 + 2, y1 - 28, x0 + 66, y1 - 2).intersection(inner).difference(P1.buffer(0.1))
    add(L, P1, "주차전용건축물(주동)", "주차타워", "교통·방문자", 5, "주차", role="주차")
    add(L, unary_union([P2, P3]), "주차전용건축물(남·북 동)", "주차타워", "교통·방문자", 4, "주차", role="주차")
    liner = box(x1 - 16, y0 + 30, x1, y1 - 30).intersection(inner)
    liner = liner.difference(box(x1 - 17, (y0 + y1) / 2 - 6, x1 + 1, (y0 + y1) / 2 + 6))
    add(L, liner, "주차동 라이너(판매·공방)", "주차타워", "판매·음식", 2, "판매")
    used = unary_union([b["geom"] for b in BUILD if b["lot"] == L["id"]])
    OPEN.append((L["id"], "1단계 임시 평면주차", inner.difference(used.buffer(3)), "#cfcfcf"))

def m_tail():
    for nm in ("관광객 휴게·판매상가 W", "관광객 휴게·판매상가 E"):
        L = BY[nm]
        ring, court = ring_court(L["geom"], 4.0, 13.0, gate_min_edge=60, n_gates=1, min_piece=250)
        for g in ring: add(L, g, nm, "관광객 중심 휴게·판매상가", "판매·음식", 3, "판매")
        COURTS.append((L["id"], "관광상가 앞마당", court))

def m_park():
    P = [p for p in PARKS if p["name"] == "Park A"][0]
    for (x, y) in ((219790, 361385), (219825, 361352)):
        g = rrect(x, y, 12, 9, 40).intersection(P["geom"])
        BUILD.append(dict(lot="Park A", lot_no=0, name="수변 쉼터·카페", use="공원 시설", cat="판매·음식", geom=g, floors=1, floor_h=4.0, h=4.0, retail_ground=False, role="공원시설", area=g.area, note=""))
    P = [p for p in PARKS if p["name"] == "Park C"][0]
    for (x, y) in ((219672, 360772), (219682, 360690)):
        g = rrect(x, y, 10, 8, 0).intersection(P["geom"])
        if not g.is_empty: BUILD.append(dict(lot="Park C", lot_no=0, name="광장 매점·카페", use="공원 시설", cat="판매·음식", geom=g, floors=1, floor_h=4.0, h=4.0, retail_ground=False, role="공원시설", area=g.area, note=""))

for f in (m_sport, m_housing, m_city, m_culture, m_startup, m_comm, m_market, m_experience, m_residency, m_heritage, m_tour, m_parking, m_tail, m_park): f()

# ── 검증 ─────────────────────────────────────────────────────────────────────
from shapely.strtree import STRtree
gs = [b["geom"] for b in BUILD]; tr = STRtree(gs); ov = []
for i, g in enumerate(gs):
    for j in tr.query(g):
        if j > i and g.intersection(gs[j]).area > 0.5: ov.append((BUILD[i]["name"], BUILD[j]["name"], round(g.intersection(gs[j]).area, 1)))
lotgeom = {d["id"]: d["geom"].buffer(0.05) for d in LOTS}
out = [(b["name"], b["lot"], round(b["geom"].difference(lotgeom[b["lot"]]).area, 1)) for b in BUILD if b["lot"] in lotgeom and b["geom"].difference(lotgeom[b["lot"]]).area > 0.5]
print("매스 %d개, 겹침 %d건, 획지 밖 %d건" % (len(BUILD), len(ov), len(out))); print(ov[:5], out[:5])
tall = [b for b in BUILD if b["h"] > 20.0]
print("높이 20 m 초과 %d개 (%.0f㎡ 건축면적, 연면적 %.0f㎡)" % (len(tall), sum(b["area"] for b in tall), sum(b["area"] * b["floors"] for b in tall)))
for b in tall[:12]: print("   ", b["lot"], b["name"], "%dF %.1f m" % (b["floors"], b["h"]))
tot = sum(b["area"] * b["floors"] for b in BUILD if b["role"] != "공원시설")
print("연면적(공원시설 제외) %.0f㎡, 건축면적 %.0f㎡" % (tot, sum(b["area"] for b in BUILD if b["role"] != "공원시설")))
pickle.dump(dict(BUILD=BUILD, COURTS=COURTS, OPEN=OPEN), open(SP + r"\clean_mass.pkl", "wb"))


