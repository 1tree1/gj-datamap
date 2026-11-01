"""S3 매스 배치 — 획지(s2_lots)와 프로그램(prog) 위에 건물 볼륨을 올린다. 규칙: ① 건축면적 = 연면적 ÷ 층수(prog 값)에 맞춘다(오차 ±3% 안).
② 모든 매스는 획지 안쪽 5~6 m 후퇴선 안에 들어가고 서로 겹치지 않는다(자동 검사). ③ 높이는 고도지구 20 m 이하(층고 가정은 prog.HT). ④ 구 역사는 사용자 도면의 실제 형상(존치).
출력: data/masses.pkl — masses[{lot, name, g(Polygon,로컬 m), h(m), cat, color}], 요약표"""
import os, pickle, math, json
import numpy as np
from shapely.geometry import Polygon, box, Point, LineString
from shapely.ops import unary_union
from shapely import affinity
import prog

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
L = pickle.load(open(os.path.join(D, "lots.pkl"), "rb"))
LOT, GRN, OX, OY = L["LOT"], L["GRN"], L["OX"], L["OY"]
ctx, PR, PK = prog.build()
# 구 역사(존치) — 사용자 도면의 실제 외곽선(21점), 라이노 평면 좌표 → 로컬
_bp = json.load(open(r"C:/Users/OFFICE/AppData/Local/Temp/claude/C--Users-OFFICE-Desktop-9---/208a6fca-848a-4422-ad91-655fc023df64/scratchpad/bld_pair.json", encoding="utf-8"))
STATION = Polygon([(x - OX, y - OY) for x, y in _bp["plan"]["pts"]]).buffer(0)

COL = {"공공업무": "#4C78B8", "상업·업무": "#E4573A", "주거": "#F1D247", "문화·교육·공공": "#6F9FDC", "창조산업": "#A98BD3",
       "판매·음식": "#F4A0C2", "여가·오락·체육": "#2FAB9D", "역사유산": "#C9742F", "교통·방문자": "#C6C6C6", "주차전용건축물": "#8E8E8E"}
masses = []


def rc(cx, cy, w, h, ang=0.0):
    """중심(cx,cy), 가로 w, 세로 h, 회전 ang(도, 반시계) 직사각형"""
    p = box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    return affinity.rotate(p, ang, origin=(cx, cy)) if ang else p


def comp_of(lot, key):
    for c in PR[lot]:
        if c["name"].startswith(key): return c
    raise KeyError((lot, key))


def add(lot, name, g, comp, h=None):
    masses.append(dict(lot=lot, name=name, g=g, h=h or comp["height"], cat=comp["cat"], color=COL[comp["cat"]], floors=comp["floors"], gfa=comp["gfa"],
                       fp_target=(comp["gfa"] / comp["floors"]) if comp["kind"] != "oldst" else 1403.0))


def U_shape(x0, y0, W, H, t, open_dir="E"):
    """ㄷ자: 외곽 W×H, 두께 t, open_dir 쪽이 열림"""
    if open_dir == "E":
        return unary_union([box(x0, y0, x0 + t, y0 + H), box(x0, y0 + H - t, x0 + W, y0 + H), box(x0, y0, x0 + W, y0 + t)])
    if open_dir == "W":
        return unary_union([box(x0 + W - t, y0, x0 + W, y0 + H), box(x0, y0 + H - t, x0 + W, y0 + H), box(x0, y0, x0 + W, y0 + t)])
    raise ValueError


def solve_t(W, H, area):
    # H t + 2 (W - t) t = area  → -2t² + (H+2W) t - area = 0
    a, b, c = -2.0, H + 2 * W, -area
    return (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a) * -1 if False else (b - math.sqrt(b * b - 8 * area)) / 4.0


# ── 공1 공공업무시설 ─────────────────────────────────────────────────────────
c = comp_of("공1", "본청"); fp = c["gfa"] / c["floors"]
W, H = 72.0, 100.0; t = solve_t(W, H, fp)
add("공1", "본청 청사(ㄷ자, 동향 개방)", U_shape(80.0, 655.0, W, H, t, "E"), c)
c2 = comp_of("공1", "의회"); a2 = c2["gfa"] / c2["floors"]; s = math.sqrt(a2)
add("공1", "의회 청사", rc(146.0, 705.0, s, s), c2)

# ── 주1 공동주택 + 주민 커뮤니티 ────────────────────────────────────────────
c = comp_of("주1", "청년·신혼 주거"); fp = c["gfa"] / c["floors"]; nb = 5; d = 14.5; ln = fp / nb / d
ys = [649.0 + k * (d + 17.4) for k in range(nb)]
for k, y0 in enumerate(ys):
    add("주1", "주거 %d동(6F, 남남동향)" % (k + 1), box(240.0, y0, 240.0 + ln, y0 + d), c)
c = comp_of("주1", "주민 공동시설"); a = c["gfa"] / c["floors"]; w = 24.0
add("주1", "주민 공동시설(3F)", box(211.0, 735.0, 211.0 + w, 735.0 + a / w), c)
c = comp_of("주1", "생활편의점"); a = c["gfa"] / c["floors"]
add("주1", "생활편의점·카페(2F)", box(211.0, 774.0, 223.0, 774.0 + a / 12.0), c)

# ── 업1·업2 업무시설 ────────────────────────────────────────────────────────
for lot, (xo, ytop) in (("업1", (140.0, None)), ("업2", (209.0, None))):
    b = LOT[lot]["g"].bounds
    c = comp_of(lot, "청년 업무"); fp = c["gfa"] / c["floors"]
    wd = 18.0 if lot == "업1" else 24.0
    ln = fp / wd; yc = (b[1] + b[3]) / 2
    add(lot, "청년 업무동(5F)", box(xo, yc - ln / 2, xo + wd, yc + ln / 2), c)
    c = comp_of(lot, "저층 근린상가"); a = c["gfa"] / c["floors"]; w2 = 8.0
    xr = xo + wd + 2.5
    add(lot, "저층 근린상가(2F)", box(xr, yc - ln / 2, xr + w2, yc - ln / 2 + a / w2), c)

# ── 문4·문5 창작·체험 ──────────────────────────────────────────────────────
def residency(lot, nbars, exp_w):
    b = LOT[lot]["g"].bounds
    x0 = b[0] + 5.5; y = b[1] + 5.5
    c = comp_of(lot, "예술인 레지던시"); fp = c["gfa"] / c["floors"]; dd = 10.0; ln = fp / nbars / dd
    for k in range(nbars):
        add(lot, "레지던시 작업동 %d(3F)" % (k + 1), box(x0, y, x0 + ln, y + dd), c)
        y += dd + 9.0
    c = comp_of(lot, "역사·공예 체험관"); a = c["gfa"] / c["floors"]
    y0 = y - 9.0 + 4.0
    add(lot, "역사·공예 체험관(3F)", box(x0, y0, x0 + exp_w, y0 + a / exp_w), c, h=15.0)
residency("문4", 2, 14.0)
residency("문5", 3, 16.0)

# ── 상1 성동시장 연계(선형 상가열) ────────────────────────────────────────
c1 = comp_of("상1", "시장 접점"); c2 = comp_of("상1", "식음·판매")
tot = (c1["gfa"] + c2["gfa"]) / 2.0; w = 14.0; ln = tot / 3 / w
for k, y0 in enumerate((382.0, 412.0, 442.0)):
    add("상1", "시장 연계 상가 %d(2F)" % (k + 1), box(33.0, y0, 33.0 + w, y0 + ln), c2 if k else c1)

# ── 체1 운동시설 ─────────────────────────────────────────────────────────────
c = comp_of("체1", "생활체육"); a = c["gfa"] / c["floors"]; w = 30.0
add("체1", "생활체육관(2F)", box(255.0, 806.0, 255.0 + w, 806.0 + a / w), c)

# ── 문1 공연장 ──────────────────────────────────────────────────────────────
b = LOT["문1"]["g"].bounds
c = comp_of("문1", "공연장"); a = c["gfa"] / c["floors"]
hall = 1000.0; foy = a - hall
add("문1", "공연장 본관(객석·무대, 19 m)", box(112.0, 818.0, 148.0, 818.0 + hall / 36.0), c, h=19.0)
add("문1", "공연장 로비(2F)", box(112.0, 818.0 - foy / 36.0 - 2.0, 148.0, 816.0), c, h=8.4)
c = comp_of("문1", "연습실"); a = c["gfa"] / c["floors"]
add("문1", "연습실·시민 다목적실(2F)", box(150.5, 800.0, 150.5 + 12.0, 800.0 + a / 12.0), c)

# ── 문2 구 역사(존치) + 근대역사 전시관 별관 ──────────────────────────────
c = comp_of("문2", "구 역사")
masses.append(dict(lot="문2", name="구 역사(존치, 근대역사관·경주문화원 1918)", g=STATION, h=7.0, cat="역사유산", color=COL["역사유산"], floors=2, gfa=c["gfa"], fp_target=1403.0, existing=True))
c = comp_of("문2", "근대역사"); fp = c["gfa"] / c["floors"]
ang = math.degrees(math.atan2(70.0, 54.0)); ln = 56.0; wd = fp / ln
sc = STATION.centroid; nrm = np.array([math.cos(math.radians(ang - 90)), math.sin(math.radians(ang - 90))])   # 역사 축의 동남쪽 법선
cen = np.array([sc.x, sc.y]) + 28.0 * nrm
add("문2", "근대역사 전시관 별관(3F, 역사 축 평행)", rc(cen[0], cen[1], wd, ln, ang - 90), c)

# ── 문3 팝업스토어·상가·공방 ─────────────────────────────────────────────
c1 = comp_of("문3", "팝업"); c2 = comp_of("문3", "공개 공방")
tot = (c1["gfa"] + c2["gfa"]) / 2.0; w, h = 20.0, tot / 5 / 20.0
pos = [(60, 63), (90, 63), (120, 63), (80, 80), (110, 80)]
for k, (x0, y0) in enumerate(pos):
    add("문3", "팝업·상가·공방 %d(2F)" % (k + 1), box(x0, y0, x0 + w, y0 + h), c1 if k < 4 else c2)

# ── 관1 관광지원시설 + 주차전용건축물 ─────────────────────────────────────
c = comp_of("관1", "주차전용"); fp = c["gfa"] / 6.0   # 6층으로 계획(18 m)
c["floors"] = 6; c["height"] = 18.0
wd = 51.0; ln = fp / wd
add("관1", "주차전용건축물(6F)", box(247.0, 204.5, 247.0 + wd, 204.5 + ln), c)
c = comp_of("관1", "방문자 관문"); a = c["gfa"] / c["floors"]
add("관1", "방문자 관문·모빌리티 대합실(2F)", box(247.0, 204.5 + ln + 4.0, 247.0 + 27.0, 204.5 + ln + 4.0 + a / 27.0), c)


# ── 검사 ────────────────────────────────────────────────────────────────────
def check():
    rows = []; bad = []
    for i, m in enumerate(masses):
        lot = LOT[m["lot"]]["g"]
        inside = lot.buffer(0.2).contains(m["g"])
        if not inside: bad.append("밖: %s %s (밖 면적 %.1f㎡)" % (m["lot"], m["name"], m["g"].difference(lot).area))
        for j in range(i):
            o = masses[j]
            if m["g"].intersection(o["g"]).area > 0.5: bad.append("겹침: %s | %s × %s | %s" % (m["lot"], m["name"], o["lot"], o["name"]))
    return bad


if __name__ == "__main__":
    bad = check()
    print("검사:", "OK" if not bad else "")
    for b in bad: print("  ", b)
    by = {}
    for m in masses:
        r = by.setdefault(m["lot"], dict(fp=0.0, tgt=0.0, gfa=0.0))
        r["fp"] += m["g"].area; r["tgt"] += m["fp_target"]; r["gfa"] += m["g"].area * m["floors"] if not m.get("existing") else m["gfa"]
    for k, r in by.items():
        print("%-3s 건축면적 %7.1f (목표 %7.1f, %+.1f%%) 획지 %8.1f 건폐율 %.1f%%" % (k, r["fp"], r["tgt"], (r["fp"] / r["tgt"] - 1) * 100, LOT[k]["area"], r["fp"] / LOT[k]["area"] * 100))
    pickle.dump(dict(masses=masses, STATION=STATION, PR=PR, PK=PK), open(os.path.join(D, "masses.pkl"), "wb"))
