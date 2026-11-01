"""F1 최종 마스터플랜 건축물 모델 — 다이어그램 공통 데이터
- 지면(획지·공원·보행축·도로·보도·광장)은 v2 설계 데이터(design.pkl) 그대로(최종본과 형상 차이 0㎡)
- 건축물은 최종본 추출(final_export.json): 객체 표시 색 → 용도, 평면이 겹치는 솔리드 → 한 동, 층별 용도 적층 기록
- 검정 얇은 객체(두께 < 2.5 m, 지상에서 떠 있음) = 연결 브리지·캐노피
출력: data/model.pkl"""
import json, os, pickle, re, math
import numpy as np
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
import sys; sys.path.insert(0, HERE)
from f0_parse_final import outline_poly, polys
S = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
F = pickle.load(open(os.path.join(D, "final.pkl"), "rb"))
E = json.load(open(os.path.join(D, "final_export.json"), encoding="utf-8"))
X0, Y0 = S["X0"], S["Y0"]
CATS = S["CATS"]
CHEX = {k: v[0].lower() for k, v in CATS.items()}
FH = {"주거": 3.0, "주차": 3.2, "역사": 4.5}


def cat_of_color(rgb):
    h = "#%02x%02x%02x" % tuple(rgb)
    if max(rgb) < 40: return "연결"
    best = min(CHEX, key=lambda k: sum((int(CHEX[k][i:i + 2], 16) - int(h[i:i + 2], 16)) ** 2 for i in (1, 3, 5)))
    return best


OBJ = []
for r in E["recs"]:
    if r["type"] not in ("Extrusion", "Brep"): continue
    ly = r["layer"]
    if any(k in ly for k in ("02_", "03_", "04_", "05_", "07_", "08_", "12_")): continue
    zr = r["bb"][5] - r["bb"][2]
    if zr <= 1.0: continue
    g = outline_poly(r)
    if g.is_empty or g.area < 5: continue
    OBJ.append(dict(g=g, z0=max(r["bb"][2], 0.0), z1=r["bb"][5], cat=cat_of_color(r["color"]), us=r.get("us", {}), name=r["name"], layer=ly, brep=r["type"] == "Brep"))
LINK = [o for o in OBJ if o["cat"] == "연결"]
SOL = [o for o in OBJ if o["cat"] != "연결"]

# 평면 겹침으로 동 묶기(합집합-찾기)
n = len(SOL); par = list(range(n))
def find(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i
for i in range(n):
    for j in range(i + 1, n):
        a, b = SOL[i]["g"], SOL[j]["g"]
        if not a.intersects(b): continue
        ia = a.intersection(b).area
        if ia > 0.25 * min(a.area, b.area): par[find(i)] = find(j)
comp = {}
for i in range(n): comp.setdefault(find(i), []).append(SOL[i])

LOTG = {l["no"]: l["g"] for l in S["LOTS"]}
def lot_of(g):
    c = g.representative_point()
    best = max(LOTG, key=lambda k: LOTG[k].intersection(g).area)
    return best


BLD = []
for objs in comp.values():
    g = unary_union([o["g"] for o in objs]).buffer(0)
    names = [o["us"].get("건축물") or re.sub(r"\s*\d+F$", "", o["name"] or "") for o in objs]
    names = [x for x in names if x]
    nm = max(set(names), key=names.count) if names else ""
    stack = sorted([(round(o["z0"], 2), round(o["z1"], 2), o["cat"], o["g"].area) for o in objs])
    gfa = {}; fl_levels = set()
    for z0, z1, c, a in stack:
        fh = FH.get(c, 4.0); nf = max(1, int(round((z1 - z0) / fh)))
        gfa[c] = gfa.get(c, 0.0) + a * nf
        for k in range(nf): fl_levels.add(round(z0 + k * fh, 1))
    main = max(gfa, key=gfa.get)
    h = max(o["z1"] for o in objs)
    base = [c for z0, z1, c, a in stack if z0 < 0.5]
    retail = ("판매" in base) and main != "판매"
    lot = lot_of(g)
    BLD.append(dict(name=nm, lot=lot, g=g, h=h, floors=len(fl_levels), gfa=sum(gfa.values()), gfa_by=gfa, main=main, retail=retail, stack=stack,
                    parts=[(o["g"], o["z0"], o["z1"], o["cat"]) for o in objs],
                    term=next((o["us"].get("용어(지구단위계획)") for o in objs if o["us"].get("용어(지구단위계획)")), ""), edited=any(o["brep"] for o in objs)))
# 구 경주역사(상세 모델) — 평면은 러프 원본 외곽(1,403㎡), 2층(처마 9 m), 지붕 최고 높이는 상세 모델
ST = [m for m in S["MASS"] if m["name"] == "구 경주역사"][0]
BLD.append(dict(name="구 경주역사", lot=9, g=ST["g"], h=F["ST_Z"][1], floors=2, gfa=ST["g"].area * 2, gfa_by={"역사": ST["g"].area * 2}, main="역사", retail=False,
                stack=[(0.0, 9.0, "역사", ST["g"].area)], parts=[(ST["g"], 0.0, 9.0, "역사")], term=ST["term"], edited=True, detail_fp=F["ST"]))
# 연결 브리지·캐노피
LINKS = []
for o in LINK:
    LINKS.append(dict(g=o["g"], z0=o["z0"], z1=o["z1"], lot=lot_of(o["g"]), kind="캐노피" if o["g"].area > 1000 else "연결 브리지"))

# 이름 정리(최종본에서 형태가 바뀌거나 합쳐진 동)
RN = S["ROADS"]["N"]
k8 = 0
for b in sorted(BLD, key=lambda b: -b["g"].centroid.y):
    if not b["name"]: b["name"] = {"주차": "모빌리티 허브 증축부"}.get(b["main"], "건축물")
    if b["lot"] == 4 and b["main"] == "판매": b["name"] = "근린생활 연결동"; b["term"] = "제1·2종 근린생활시설(주민공동시설)"
    if b["lot"] == 7 and b["main"] == "창작": b["name"] = "전통문화 공방·전시·공예마켓동"
    if b["lot"] == 7 and b["name"] == "공방동": b["name"] = "공방·판매동"
    if b["lot"] == 8 and b["name"].startswith("레지던시 제작동"): k8 += 1; b["name"] = "레지던시 제작동 %d" % k8
    if b["lot"] == 2 and not b["g"].intersects(RN.buffer(-0.5)): b["name"] = "직원 주차장동 별동"
    if b["lot"] == 2 and b["g"].intersects(RN.buffer(-0.5)): b["name"] = "공공청사·기관 직원 주차장동(청사 연결 브리지 포함)"
BLD.sort(key=lambda b: (b["lot"], -b["h"]))
print("buildings", len(BLD), "links", len(LINKS))
for b in BLD:
    print("  %2d %-22s %-6s 건축 %6.0f 연면적 %7.0f 높이 %5.1f %dF 1층상가 %s 구성 %s" % (b["lot"], b["name"][:22], b["main"], b["g"].area, b["gfa"], b["h"], b["floors"], b["retail"],
          {k: round(v) for k, v in b["gfa_by"].items()}))
for l in LINKS: print("  link", l["kind"], l["lot"], round(l["g"].area), round(l["z0"], 1), round(l["z1"], 1))

# 획지별 집계
LOTS = []
for l in S["LOTS"]:
    bs = [b for b in BLD if b["lot"] == l["no"]]
    ba = unary_union([b["g"] for b in bs]).area if bs else 0.0
    gfa = sum(b["gfa"] for b in bs)
    LOTS.append(dict(l, ba=ba, gfa=gfa, bcr=ba / l["area"], far=gfa / l["area"], maxf=max([b["floors"] for b in bs] or [0]), maxh=max([b["h"] for b in bs] or [0]),
                     n_bld=len(bs), names=[b["name"] for b in bs]))
for l in LOTS: print("  lot %2d %-24s %7.0f 건축 %6.0f(%.0f%%) 연면적 %7.0f(%.0f%%) %dF %.1fm" % (l["no"], l["name"], l["area"], l["ba"], l["bcr"] * 100, l["gfa"], l["far"] * 100, l["maxf"], l["maxh"]))
TOT = dict(boundary=S["B"].area, lot=sum(l["area"] for l in LOTS), ba=sum(l["ba"] for l in LOTS), gfa=sum(l["gfa"] for l in LOTS))
TOT["bcr"] = TOT["ba"] / TOT["lot"]; TOT["far"] = TOT["gfa"] / TOT["lot"]
print("TOTAL", {k: round(v, 3) for k, v in TOT.items()})
pickle.dump(dict(S=S, BLD=BLD, LINKS=LINKS, LOTS=LOTS, TOT=TOT, ST_FP=F["ST"], TREES=F["TREES"]), open(os.path.join(D, "model.pkl"), "wb"))
