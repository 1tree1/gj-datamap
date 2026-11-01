"""S4 가구별 유형 규칙으로 건물 매스 생성.
층수 = min(프로그램 층수, 경계 켜 규칙(방향별), 고도지구 높이 ÷ 층고). 건물 길이는 켜별 입면 분절 규칙으로 자른다.
입력: scratch/network.pkl, context.pkl, plan_items.pkl   출력: scratch/massing.pkl
"""
import pickle, sys, math, zlib, collections
import numpy as np
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely import wkb, affinity
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
sys.path.insert(0, r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts")
from plan_def import FLOOR_H, HEIGHT_CAP, SIDE_CAP
from geomkit import polys, clean, rrect, mrr, poisson, Envelope

C = pickle.load(open(SP + r"\context.pkl", "rb")); U = C["U"]
NET = pickle.load(open(SP + r"\network.pkl", "rb"))
ENV = Envelope(U, C["G"], SIDE_CAP, FLOOR_H, HEIGHT_CAP)
sketch = {it["id"]: wkb.loads(it["geom"]) for it in pickle.load(open(SP + r"\plan_items.pkl", "rb"))}

CAT = {"공공": "문화·교육·공공", "문화": "문화·교육·공공", "여가": "여가·오락·체육", "업무": "상업·업무", "창조": "창조산업", "주거": "주거",
       "판매": "판매·음식", "교통": "교통·방문자", "역사": "역사유산", "녹지": "오픈스페이스"}

BUILD = []
EXTRA = {"plaza": [], "court": [], "path": [], "surface_parking": [], "heritage_plaza": [], "tree_zone": [], "marker": []}

# 켜별 건물 길이 상한(m)·분절 틈(m) — 경계 스케일전이 규칙 v1 §4.2(켜1: 동 15·서 22·남 17·북 15), 켜2 = 켜1→켜3 로그 보간(d=65 m)
LEN_CAP = {"동": (15.0, 30.0), "서": (22.0, 40.0), "남": (17.0, 32.0), "북": (15.0, 30.0), "수변": (22.0, 40.0)}
GAP_W = {"동": 3.0, "서": 4.0, "남": 3.5, "북": 3.0, "수변": 4.0}

def block_by_probe(x, y):
    p = Point(x, y)
    for b in NET["blocks"]:
        if b["geom"].contains(p): return b
    raise RuntimeError("block not found at %s,%s" % (x, y))

def articulate(g, max_len, gap, depth=0):
    """긴 매스를 장축 방향으로 max_len 이하 모듈로 자르고 gap 만큼 띄운다(입면 분절). ㄱ·ㄷ자는 조각마다 다시 검사해 재귀로 자른다."""
    if g.area < 60 or depth > 4: return [g]
    L, W, ang = mrr(g)
    if L <= max_len * 1.25: return [g]
    n = int(math.ceil((L + gap) / (max_len + gap)))
    seg = (L - gap * (n - 1)) / n
    if seg < 6.0: return [g]
    c = g.centroid
    rot = affinity.rotate(g, -ang, origin=(c.x, c.y))
    minx, miny, maxx, maxy = rot.bounds
    out = []
    for i in range(n):
        x0 = minx + i * (seg + gap)
        for p in clean(box(x0, miny - 1, x0 + seg, maxy + 1).intersection(rot), 30, 3):
            q = affinity.rotate(p, ang, origin=(c.x, c.y))
            out.extend(articulate(q, max_len, gap, depth + 1) if q.area >= 60 else [q])
    return out or [g]

def add(block, geom, prog, cat, use, floors, fh_key, name, exc=None, terrace=True, fh=None, artic=True, vary=False, min_floors=1, role="건물"):
    """footprint → 켜별 분할 → 입면 분절 → 층수·높이 결정 → BUILD 추가. exc: {'caps':(켜1,켜2,켜3)} 로 해당 프로그램 켜 규칙 예외."""
    if geom.is_empty: return
    fhv = fh if fh is not None else FLOOR_H[fh_key]
    parts = ENV.split_bands(geom) if terrace else [(p, ENV.band(p.representative_point())) for p in clean(geom, 30, 2)]
    bid = "%s-%02d" % (block["id"], len({b["bid"] for b in BUILD if b["block"] == block["id"]}) + 1)
    k = 0
    for g0, band in parts:
        side0 = ENV.side(g0.representative_point())
        pieces = articulate(g0, LEN_CAP[side0][band], GAP_W[side0]) if (artic and band < 2) else [g0]
        for g in pieces:
            pt = g.representative_point()
            side = ENV.side(pt); hcap = ENV.height_cap(g)
            sc = (exc["caps"] if exc else SIDE_CAP[side])[band]
            by_h = int(hcap // fhv + 1e-9)
            f = max(1, min(floors, sc, by_h))
            if vary and f > min_floors and (zlib.crc32(("%s-%d" % (bid, k)).encode()) % 3 == 0): f -= 1
            BUILD.append(dict(bid=bid, part=k, block=block["id"], tag=name, prog=prog, cat=cat, use=use, role=role, geom=g, floors=f, floor_h=fhv, h=round(f * fhv, 2),
                              area=g.area, gfa=g.area * f, side=side, band=band + 1, side_cap=sc, h_cap=hcap, by_h=by_h, prog_floors=floors, exc=bool(exc)))
            k += 1

def ring_court(poly, setback=3.5, depth=12.5, gap_w=8.0, gap_every=48.0, corner_keep=14.0):
    """둘레 중정형: 안쪽 오프셋 링 + 긴 변마다 틈(통경). 반환 ([링 조각], 중정 폴리곤)"""
    inner = poly.buffer(-setback, join_style=2)
    court = inner.buffer(-depth, join_style=2)
    ring = inner.difference(court)
    for part in polys(inner):
        cs = list(part.exterior.coords)
        for i in range(len(cs) - 1):
            a, b = np.array(cs[i]), np.array(cs[i + 1]); L = np.linalg.norm(b - a)
            if L < 30: continue
            u = (b - a) / L; n = np.array([-u[1], u[0]]); mid = (a + b) / 2
            if not part.contains(Point(*(mid + n * 2))): n = -n
            avail = L - 2 * corner_keep
            if avail < gap_w + 4: continue
            ng = max(1, int(avail // gap_every))
            for j in range(ng):
                t = corner_keep + avail * (j + 0.5) / ng
                c = a + u * t + n * depth / 2
                ring = ring.difference(rrect(c[0], c[1], gap_w, depth + 4, math.degrees(math.atan2(u[1], u[0]))))
    return clean(ring, 80, 4.5), court

def aligned_grid(poly, ang, bl, bw, gu, gv, margin=3.0, fill=0.8):
    """각도 ang 방향 길이 bl × 폭 bw 상자를 간격(gu 길이방향, gv 폭방향)으로 깐다."""
    inner = poly.buffer(-margin, join_style=2) if margin else poly
    if inner.is_empty: return []
    c = inner.centroid
    rot = affinity.rotate(inner, -ang, origin=(c.x, c.y))
    minx, miny, maxx, maxy = rot.bounds
    out = []; y = miny
    while y + bw <= maxy + 1e-6:
        x = minx
        while x + bl <= maxx + 1e-6:
            r = box(x, y, x + bl, y + bw)
            if rot.contains(r) or r.intersection(rot).area >= fill * r.area:
                out.append(affinity.rotate(r.intersection(rot), ang, origin=(c.x, c.y)))
            x += bl + gu
        y += bw + gv
    return out

def strip_modules(poly, side, depth, mod_len, gap, setback=3.5, min_len=7.0, y_range=None, gap_centers=()):
    """서(west)/동(east) 변에 면한 저층 모듈열(남북 배열). gap_centers = 기존 골목 앵커에 맞출 틈의 y 좌표."""
    inner = poly.buffer(-setback, join_style=2) if setback else poly
    minx, miny, maxx, maxy = inner.bounds
    if y_range: miny, maxy = max(miny, y_range[0]), min(maxy, y_range[1])
    cuts = sorted(c for c in gap_centers if miny + gap < c < maxy - gap)
    spans, start = [], miny
    for c in cuts:
        spans.append((start, c - gap / 2)); start = c + gap / 2
    spans.append((start, maxy))
    out = []
    for (a, b_) in spans:
        L = b_ - a
        if L < min_len: continue
        n = max(1, int(math.ceil((L + gap) / (mod_len + gap))))
        ml = (L - gap * (n - 1)) / n
        for i in range(n):
            y0 = a + i * (ml + gap); y1 = y0 + ml
            x0, x1 = (minx, minx + depth) if side == "west" else (maxx - depth, maxx)
            for g in clean(box(x0, y0, x1, y1).intersection(inner), 30, 3):
                if g.area >= min_len * depth * 0.6: out.append(g)
    return out

def free_area(block, margin=2.0, buf=1.5, ids=None):
    used = unary_union([x["geom"] for x in BUILD if x["block"] == block["id"]]) if BUILD else Polygon()
    return block["geom"].buffer(-margin).difference(used.buffer(buf))

# ══════════════════════════════════════════════════════════════════════════════
# 가구별 유형
# ══════════════════════════════════════════════════════════════════════════════
def gen_city():
    b = block_by_probe(219712, 361167); inner = b["geom"].buffer(-3.5, join_style=2)
    minx, miny, maxx, maxy = inner.bounds        # x 219,645–219,778.5 / y 361,101.5–361,231.5
    # 민원·시민동: 서변 3층 모듈열(원화로 가로벽, 길이 ≤22 m). 틈 6 m 를 서측 기존 골목 앵커(361,160·361,188)에 정렬
    for g in strip_modules(b["geom"], "west", 19, 22, 6, setback=3.5, gap_centers=(361160, 361188)):
        add(b, g, "시청·의회", CAT["공공"], "민원·시민동(저층부 근린 권장용도)", 3, "공공", "시청 민원·시민동", role="저층 가로벽")
    D = 15
    y_s0, y_s1 = miny + 6.5, miny + 6.5 + D
    y_n1, y_n0 = maxy - 6.5, maxy - 6.5 - D
    bx0, bx1 = minx + 27, maxx - 4
    main = unary_union([box(bx0, y_n0, bx1, y_n1), box(bx0, y_s0, bx1, y_s1), box(bx0, y_s0, bx0 + D, y_n1)]).intersection(inner)
    add(b, main, "시청·의회", CAT["공공"], "본청 사무동(ㄷ자, 동측 시민마당)", 5, "공공", "시청 본청", artic=False)
    cx, cy = maxx - 24, (miny + maxy) / 2
    add(b, rrect(cx, cy, 36, 31, 0), "시청·의회", CAT["공공"], "의회동(본회의장)", 3, "문화", "시청 의회동", terrace=False, artic=False)
    court = box(bx0 + D, y_s1, maxx, y_n0).difference(rrect(cx, cy, 36, 31, 0)).intersection(inner)
    EXTRA["court"].append(("시민마당", court)); EXTRA["tree_zone"].append(court.buffer(-3))

def gen_cult():
    b = block_by_probe(219712, 361038); inner = b["geom"].buffer(-3.5, join_style=2)
    minx, miny, maxx, maxy = inner.bounds         # x 219,645–219,778.5 / y 360,992.5–361,082.5
    for g in strip_modules(b["geom"], "west", 16, 20, 6, setback=3.5):
        add(b, g, "복합문화·영화관", CAT["문화"], "문화상점·북카페·갤러리(저층 가로활성)", 3, "상업", "문화 가로상점", role="저층 가로벽")
    L1 = box(minx + 30, maxy - 22, minx + 100, maxy); L2 = box(minx + 30, maxy - 62, minx + 48, maxy)
    add(b, unary_union([L1, L2]).intersection(inner), "복합문화·영화관", CAT["문화"], "복합문화센터(전시·공연·도서)", 4, "문화", "복합문화센터", artic=False)
    add(b, box(maxx - 48, miny + 4, maxx, miny + 38).intersection(inner), "복합문화·영화관", CAT["여가"], "영화관(6개관)", 3, "문화", "영화관", artic=False)
    plz = box(minx + 52, miny + 4, maxx - 52, maxy - 26).intersection(inner)
    EXTRA["plaza"].append(("문화광장", plz)); EXTRA["tree_zone"].append(plz.buffer(-4))

def gen_start():
    b = block_by_probe(219834, 361038)
    ring, court = ring_court(b["geom"], setback=3.5, depth=14, gap_w=10, gap_every=45)
    for g in ring: add(b, g, "청년창업·기업지원", CAT["업무"], "창업지원시설·업무시설(중정형)", 5, "업무", "청년창업·기업지원", vary=True, min_floors=4)
    EXTRA["court"].append(("창업 중정", court)); EXTRA["tree_zone"].append(court.buffer(-2))

def gen_comm():
    b = block_by_probe(219904, 361038); inner = b["geom"].buffer(-3.5, join_style=2)
    keep = aligned_grid(inner, 0, 16, 14, 9, 9, margin=0, fill=0.9)
    for g in keep: add(b, g, "청년주민커뮤니티", CAT["공공"], "주민공동시설·커뮤니티(분산 소동)", 3, "공공", "청년·주민 커뮤니티")
    court = inner.difference(unary_union(keep).buffer(1))
    EXTRA["plaza"].append(("마을마당", court)); EXTRA["tree_zone"].append(court.buffer(-3))

def gen_market():
    b = block_by_probe(219712, 360861); inner = b["geom"].buffer(-3.5, join_style=2)
    minx, miny, maxx, maxy = inner.bounds        # x 219,645–219,778.5 / y 360,807–360,915
    tower = Point(219660, 360816)
    heritage = tower.buffer(22)                  # 삼층석탑 보호 마당(허용기준 미확인 → 보수적 반경 22 m)
    EXTRA["heritage_plaza"].append(("삼층석탑 마당", heritage.intersection(inner)))
    EXTRA["marker"].append(("삼층석탑", tower, 5.0))
    avail = inner.difference(heritage.buffer(3))
    for g in strip_modules(avail, "west", 14, 11, 4, setback=0, y_range=(miny, maxy)):
        add(b, g, "성동시장 연계 판매·체험", CAT["판매"], "시장 연계 근린상점(원화로 가로벽)", 3, "상업", "성동시장 가로상점", role="저층 가로벽")
    zone = box(minx + 20, miny + 3, maxx - 24, maxy - 2).intersection(avail)
    for g in aligned_grid(zone, 0, 38, 10, 7, 6, margin=0, fill=0.9):
        add(b, g, "성동시장 연계 판매·체험", CAT["판매"], "장옥형 마켓 바(1~2층 개방 구조)", 2, "상업", "마켓 장옥")
    for g in strip_modules(b["geom"], "east", 12, 10, 3, setback=3.5):
        add(b, g, "성동시장 연계 판매·체험", CAT["판매"], "체험판매 상점(종축 가로)", 2, "상업", "체험판매 상점", role="저층 가로벽")
    free = inner.difference(unary_union([x["geom"] for x in BUILD if x["block"] == b["id"]]).buffer(0.5)).difference(heritage)
    EXTRA["plaza"].append(("마켓 골목·광장", free))

def residency(tag_xy, name, ang=56.1, bl=22, bw=11, gu=5, gv=6, floors=2):
    b = block_by_probe(*tag_xy)
    for g in aligned_grid(b["geom"], ang, bl, bw, gu, gv, margin=3.5, fill=0.85):
        add(b, g, "아티스트 레지던시·공방", CAT["창조"], "아티스트 레지던시·오픈스튜디오·체험공방", floors, "문화", name, fh=4.2)
    EXTRA["plaza"].append((name + " 공방마당", free_area(b, 3.5, 0.5)))

def gen_plaza():
    b = block_by_probe(219705, 360731)
    st = rrect(219708, 360737, 76, 18.5, 59.7)                   # 구경주역(이전) — 현 건축면적 1,404㎡ 내외
    mu = rrect(219745, 360737, 75, 26, 59.7)                     # 근대역사관·전시장 ≈2,000㎡
    add(b, st.intersection(b["geom"]), "구경주역 이전", CAT["역사"], "구 역사(이전·존치)", 2, "역사", "구경주역(이전)", fh=4.5, terrace=False, artic=False)
    add(b, mu.intersection(b["geom"]), "경주 근대역사관·전시장", CAT["공공"], "전시시설(근대역사관)", 3, "문화", "근대역사관·전시장", terrace=False, artic=False)
    bars = unary_union([st, mu]).buffer(7)
    for (x, y) in ((219672, 360772), (219682, 360690)):       # 광장 매점·카페(막대에서 7 m 이상 띄움)
        k = rrect(x, y, 10, 8, 0).intersection(b["geom"]).difference(bars)
        add(b, k, "경주 근대역사관·전시장", CAT["판매"], "광장 매점·카페", 1, "상업", "광장 매점", terrace=False, artic=False)
    free = free_area(b, 2, 1.5)
    EXTRA["plaza"].append(("역전광장", free))
    EXTRA["tree_zone"].append(free.buffer(-3).difference(b["geom"].buffer(-30)))

def gen_tour():
    b = block_by_probe(219808, 360708)
    z12 = sketch["Z12"].intersection(b["geom"].buffer(-4, join_style=2))
    for g in clean(z12, 120, 6): add(b, g, "경주관광지원시설", CAT["교통"], "관광지원시설(안내·환승라운지·여행자센터)", 2, "문화", "경주관광지원시설", terrace=False, artic=False)
    free = free_area(b, 2, 1.5)
    EXTRA["plaza"].append(("환승 광장(셔틀·관광버스 승강)", free)); EXTRA["tree_zone"].append(free.buffer(-4))

def gen_park():
    b = block_by_probe(219884, 360718); inner = b["geom"].buffer(-3.0, join_style=2)
    minx, miny, maxx, maxy = inner.bounds
    # 주차전용건축물: 서변(S2 쪽)에 길게. 동측 40 m 안은 2층, 안쪽 5층 — 주차 예외 켜규칙 (2,5,9), 추적표에 예외 기록
    P1 = box(minx + 2, miny + 8, minx + 40, maxy - 2).intersection(inner)
    add(b, P1, "주차타워", CAT["교통"], "주차전용건축물 1동(P+R·시청 공유)", 5, "주차", "주차타워 1", exc=dict(caps=(2, 5, 9)), artic=False, role="주차")
    P2 = box(minx + 2, miny + 2, minx + 64, miny + 27).intersection(inner).difference(P1.buffer(0.1))
    add(b, P2, "주차타워", CAT["교통"], "주차전용건축물 2동", 5, "주차", "주차타워 2", exc=dict(caps=(2, 5, 9)), artic=False, role="주차")
    P3 = box(minx + 2, maxy - 27, minx + 64, maxy - 2).intersection(inner).difference(P1.buffer(0.1))
    add(b, P3, "주차타워", CAT["교통"], "주차전용건축물 3동", 5, "주차", "주차타워 3", exc=dict(caps=(2, 5, 9)), artic=False, role="주차")
    for g in aligned_grid(box(minx + 42, miny + 30, maxx, maxy - 30).intersection(inner), 90, 11, 13, 3, 3, margin=1, fill=0.85):
        add(b, g, "주차타워", CAT["판매"], "주차동 라이너(체험판매·공방 2층)", 2, "상업", "주차 라이너", terrace=False)
    used = unary_union([x["geom"] for x in BUILD if x["block"] == b["id"]])
    EXTRA["surface_parking"].append(("1단계 임시 평면주차(3단계 철거)", inner.difference(used.buffer(3))))

def gen_tail():
    for xy, sid in (((219670, 360615), "Z16b"), ((219729, 360574), "Z16a")):
        b = block_by_probe(*xy)
        L = sketch[sid].intersection(b["geom"].buffer(-3.5, join_style=2))
        for g in clean(L, 150, 8):
            add(b, g, "관광객 중심 휴게·판매상가", CAT["판매"], "관광객 휴게·판매상가(카페·식당·기념품관)", 3, "상업", "관광상가")
        free = free_area(b, 2, 1.5)
        EXTRA["plaza"].append(("관광상가 앞마당", free)); EXTRA["tree_zone"].append(free.buffer(-4))

def gen_sport():
    b = block_by_probe(219757, 361302); inner = b["geom"].buffer(-3.5, join_style=2)
    c = inner.centroid
    add(b, rrect(c.x - 5, c.y - 2, 52, 36, 0).intersection(inner), "공공운동·생활시설", CAT["여가"], "공공체육센터(체육관·수영장)", 2, "문화", "공공체육센터", fh=6.5, terrace=False, artic=False)
    add(b, rrect(c.x + 20, c.y - 36, 36, 12, 0).intersection(inner), "공공운동·생활시설", CAT["공공"], "생활SOC(돌봄·도서·주민센터)", 3, "공공", "생활SOC 복합동", terrace=False, artic=False)
    court = unary_union([rrect(c.x - 22, c.y + 32, 30, 16, 0), rrect(c.x + 12, c.y + 32, 30, 16, 0)]).intersection(inner)
    EXTRA["court"].append(("옥외 운동장", court))
    EXTRA["tree_zone"].append(free_area(b, 3.5, 1.5))

def gen_river():
    b = block_by_probe(219802, 361372); g = b["geom"]
    EXTRA["tree_zone"].append(g.buffer(-3))
    for (x, y) in ((219790, 361385), (219825, 361352)):
        add(b, rrect(x, y, 12, 9, 40).intersection(g), "수변 오픈스페이스", CAT["판매"], "수변 쉼터·카페(소규모)", 1, "상업", "수변 쉼터", terrace=False, artic=False)
    EXTRA["path"].append(("수변공원 진입 산책로", LineString([(219826, 361394), (219800, 361350), (219790, 361334)]).buffer(2.0)))

def housing(probe, name, floors, depth=13.0, comb=False):
    b = block_by_probe(*probe)
    if comb:
        lots = aligned_grid(b["geom"], 0, 11, 13.5, 3, 5, margin=3, fill=0.85)
        for g in lots: add(b, g, "청년주거", CAT["주거"], "청년 연립주거(2층, 골목 이어받기)", 3, "주거", name)
        EXTRA["court"].append((name + " 골목마당", free_area(b, 3, 0.5)))
        return
    ring, court = ring_court(b["geom"], setback=3.5, depth=depth, gap_w=9, gap_every=55, corner_keep=12)
    for g in ring: add(b, g, "청년주거", CAT["주거"], "청년주거(중정형 공동주택)", floors, "주거", name, vary=True, min_floors=3)
    for cp in polys(court):
        L, W, ang = mrr(cp)
        if L > 78:    # 긴 중정은 가운데 횡동으로 둘로 나눈다
            ring_u = unary_union(ring)
            bar = rrect(cp.centroid.x, cp.centroid.y, W + 2, depth, ang + 90).intersection(b["geom"].buffer(-3.5, join_style=2)).difference(ring_u.buffer(0.4))
            add(b, bar, "청년주거", CAT["주거"], "청년주거(횡동)", floors, "주거", name + " 횡동")
            court = court.difference(bar.buffer(0.01))
    EXTRA["court"].append((name + " 중정", court)); EXTRA["tree_zone"].append(court.buffer(-2))

def run():
    gen_city(); gen_cult(); gen_start(); gen_comm(); gen_market()
    residency((219835, 360873), "레지던시 A")
    residency((219910, 360881), "레지던시 B", bl=14, bw=9, gu=4, gv=5)
    residency((219891, 360826), "레지던시 C", bl=16, bw=10, gu=4, gv=5)
    gen_plaza(); gen_tour(); gen_park(); gen_tail(); gen_sport(); gen_river()
    housing((219833, 361186), "청년주거 서블록", 5)
    housing((219902, 361258), "청년주거 북동블록", 4)
    housing((219904, 361171), "청년주거 동블록", 4)
    housing((219903, 361116), "청년주거 동남블록", 3, comb=True)

run()

# ── 검증: 겹침·도로 침범·블록 밖 ─────────────────────────────────────────────
geoms = [b["geom"] for b in BUILD]
tree = STRtree(geoms); overlaps = []
for i, g in enumerate(geoms):
    for j in tree.query(g):
        if j <= i: continue
        a = g.intersection(geoms[j]).area
        if a > 0.5: overlaps.append((BUILD[i]["bid"], BUILD[j]["bid"], round(a, 1)))
road = unary_union([NET["road_all"], NET["green_all"]])
intr = [(b["bid"], round(b["geom"].intersection(road).area, 1)) for b in BUILD if b["geom"].intersection(road).area > 0.5]
blk = {x["id"]: x["geom"].buffer(0.05) for x in NET["blocks"]}
outb = [(b["bid"], round(b["geom"].difference(blk[b["block"]]).area, 1)) for b in BUILD if b["geom"].difference(blk[b["block"]]).area > 0.5]
print("검증 — 겹침 %d건, 도로·녹지띠 침범 %d건, 가구 밖 %d건" % (len(overlaps), len(intr), len(outb)))
for t in (overlaps[:6], intr[:6], outb[:6]): print("   ", t)

pickle.dump(dict(BUILD=BUILD, EXTRA=EXTRA), open(SP + r"\massing.pkl", "wb"))
agg = collections.defaultdict(lambda: [0, 0.0, 0.0])
for b in BUILD:
    a = agg[b["prog"]]; a[0] += 1; a[1] += b["area"]; a[2] += b["gfa"]
print("건물 조각 %d개" % len(BUILD))
for k, v in sorted(agg.items(), key=lambda kv: -kv[1][2]): print("  %-22s 조각 %3d  건축면적 %8.0f㎡  연면적 %9.0f㎡" % (k, v[0], v[1], v[2]))
print("합계 건축면적 %.0f㎡ / 연면적 %.0f㎡" % (sum(b["area"] for b in BUILD), sum(b["gfa"] for b in BUILD)))
park = [b for b in BUILD if b["role"] == "주차"]
print("주차전용건축물 GFA %.0f㎡ → 32㎡/면 %.0f면 (조각 %d)" % (sum(b["gfa"] for b in park), sum(b["gfa"] for b in park) / 32, len(park)))
hs = [b for b in BUILD if b["prog"] == "청년주거"]
print("청년주거 GFA %.0f㎡ → 전용률 70%%·36㎡ %.0f세대 / 60㎡ %.0f세대" % (sum(b["gfa"] for b in hs), sum(b["gfa"] for b in hs) * 0.7 / 36, sum(b["gfa"] for b in hs) * 0.7 / 60))
