"""S4 설계 데이터 마무리 — 광장·마당·텃밭, 가로수·공원수, 라벨을 더하고 라이노 조립용 JSON(design.json, 평면 좌표)과 집계(design.pkl)를 쓴다."""
import os, pickle, json, math, random
import numpy as np
from shapely.geometry import Polygon, box, Point, LineString, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
L = pickle.load(open(os.path.join(D, "lots.pkl"), "rb")); M = pickle.load(open(os.path.join(D, "masses.pkl"), "rb"))
LOT, GRN, OP, WALKS, ROADS, U, OX, OY = L["LOT"], L["GRN"], L["OP"], L["WALKS"], L["ROADS"], L["U"], L["OX"], L["OY"]
masses = M["masses"]; STATION = M["STATION"]


def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []


MASS_ALL = unary_union([m["g"] for m in masses])

# ── 광장·마당·텃밭(획지·공원 안의 포장·이용 공간. 면적 합은 v2 야외 프로그램 값에 맞춘다) ──────────────────────────
PLZ = []   # dict(name, g, host, kind)
def plaza(name, host, g, kind="광장", clip=None, buf=2.0):
    base = clip if clip is not None else (LOT[host]["g"] if host in LOT else GRN[host]["g"])
    g = g.intersection(base).difference(MASS_ALL.buffer(buf))
    g = unary_union(polys(g)).buffer(0.01).buffer(-0.01)
    PLZ.append(dict(name=name, g=g, host=host, kind=kind, area=g.area))

plaza("구 역사 전면 문화광장", "문2", box(33, 224, 64.5, 327))
plaza("야외 전시·행사마당", "문2", box(45, 207, 100, 230), kind="마당")
plaza("본청 전면 광장(공개공지)", "공1", box(100, 677, 173.5, 733), buf=1.5)
plaza("시장 연계 광장", "공원3", box(56, 380, 99, 456), kind="광장")
plaza("오픈스튜디오 마당", "공원5", box(251, 384, 292, 448), kind="마당")
plaza("공동텃밭", "공원4", box(262, 530, 300.5, 546), kind="텃밭", buf=0.0)
PLZ_ALL = unary_union([p["g"] for p in PLZ])

# 공원 안 그늘쉼터 파빌리온(3동 × 30㎡, 단층 3.6 m — 2파트 v2 B권역 파빌리온 90㎡)
PAV = [box(78, 570, 83.5, 575.5), box(58, 540, 63.5, 545.5), box(90, 602, 95.5, 607.5)]

# ── 식재 ────────────────────────────────────────────────────────────────────
rnd = random.Random(20261011)
def darts(poly, rmin, n_try, avoid, existing=None, jitter=(2.6, 4.4)):
    pts = list(existing or [])
    minx, miny, maxx, maxy = poly.bounds
    out = []
    for _ in range(n_try):
        x, y = rnd.uniform(minx, maxx), rnd.uniform(miny, maxy)
        p = Point(x, y)
        if not poly.contains(p) or avoid.contains(p): continue
        if any((x - a) ** 2 + (y - b) ** 2 < rmin * rmin for a, b, _ in pts): continue
        t = (x, y, rnd.uniform(*jitter)); pts.append(t); out.append(t)
    return out

TREES = dict(park=[], lot=[], street=[])
for k, v in GRN.items():
    inner = unary_union(polys(v["g"])).buffer(-3.0)
    TREES["park"] += darts(inner, 11.0, 4000, PLZ_ALL.buffer(1.5).union(MASS_ALL.buffer(6.0)), TREES["park"])
for k, v in LOT.items():
    inner = unary_union(polys(v["g"])).buffer(-3.5)
    TREES["lot"] += darts(inner, 12.0, 1500, PLZ_ALL.buffer(1.5).union(MASS_ALL.buffer(5.0)), TREES["lot"], (2.4, 3.8))
# 가로수: 필지·공원 경계를 따라 보도 쪽 바깥으로 3 m 띄워 10 m 간격
WALK_U = unary_union(WALKS)
def along(line, step, off_poly, off):
    pts = []; Ls = line.length; d = step / 2
    while d < Ls:
        p = line.interpolate(d); pts.append(p); d += step
    return pts
street = []
for g in [v["g"] for v in LOT.values()] + [v["g"] for v in GRN.values()]:
    for pg in polys(g):
        ring = pg.buffer(3.2, join_style=2).exterior       # 3.2 m 바깥 둘레선
        for p in along(ring, 10.0, None, None):
            if WALK_U.buffer(-1.0).contains(p) and not any((p.x - a) ** 2 + (p.y - b) ** 2 < 36 for a, b, _ in street):
                street.append((p.x, p.y, rnd.uniform(2.6, 3.8)))
TREES["street"] = street

# ── 라벨 ───────────────────────────────────────────────────────────────────
USE = {"공1": "공공업무시설", "업1": "업무시설", "업2": "업무시설", "주1": "공동주택", "문1": "문화 및 집회시설(공연장)", "문2": "문화 및 집회시설(전시장)·관광휴게시설",
       "문3": "관광휴게시설·근린생활·판매시설", "문4": "문화 및 집회시설(창작·체험)", "문5": "문화 및 집회시설(창작·체험)", "상1": "근린생활·판매시설",
       "체1": "운동시설", "관1": "자동차 관련 시설(주차전용건축물)·관광휴게시설"}
LABELS = []
for k, v in LOT.items():
    c = max(polys(v["g"]), key=lambda g: g.area).representative_point(); LABELS.append(dict(text="%s %s" % (k, USE[k].split("(")[0]), x=c.x, y=c.y, kind="lot"))
for k, v in GRN.items():
    c = max(polys(v["g"]), key=lambda g: g.area).representative_point(); LABELS.append(dict(text="%s %s" % (k, v["kind"]), x=c.x, y=c.y, kind="green"))

def ring_list(poly):
    return dict(ext=[[x + OX, y + OY] for x, y in poly.exterior.coords], holes=[[[x + OX, y + OY] for x, y in r.coords] for r in poly.interiors])
def poly_parts(g):
    return [ring_list(p) for p in polys(g)]

ex = dict(OX=OX, OY=OY,
          boundary=[[x + OX, y + OY] for x, y in U.exterior.coords],
          lots=[dict(code=k, use=USE[k], area=v["area"], parts=poly_parts(v["g"])) for k, v in LOT.items()],
          greens=[dict(code=k, kind=v["kind"], name=v["name"], area=v["area"], parts=poly_parts(v["g"])) for k, v in GRN.items()],
          plazas=[dict(name=p["name"], host=p["host"], kind=p["kind"], area=p["area"], parts=poly_parts(p["g"])) for p in PLZ],
          masses=[dict(lot=m["lot"], name=m["name"], cat=m["cat"], color=m["color"], h=m["h"], floors=m["floors"], parts=poly_parts(m["g"]), existing=bool(m.get("existing"))) for m in masses],
          pavilions=[dict(parts=poly_parts(p)) for p in PAV],
          trees={k: [[x + OX, y + OY, r] for x, y, r in v] for k, v in TREES.items()},
          labels=[dict(text=l["text"], x=l["x"] + OX, y=l["y"] + OY, kind=l["kind"]) for l in LABELS])
json.dump(ex, open(os.path.join(D, "design.json"), "w", encoding="utf-8"), ensure_ascii=False)
pickle.dump(dict(PLZ=PLZ, PAV=PAV, TREES=TREES, LABELS=LABELS, USE=USE), open(os.path.join(D, "design_extra.pkl"), "wb"))
if __name__ == "__main__":
    print("plazas:", [(p["name"], round(p["area"])) for p in PLZ], "sum %.0f" % sum(p["area"] for p in PLZ))
    print("trees:", {k: len(v) for k, v in TREES.items()})
    print("masses", len(masses), "labels", len(LABELS))
