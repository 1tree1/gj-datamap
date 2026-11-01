"""F0 사용자 최종 마스터플랜(바탕화면 '구경주역_마스터플랜_최종.3dm', 라이노 axolotl 슬롯) 추출본 → 다이어그램용 구조 데이터
입력: data/final_export.json(객체별 레이어·윤곽·높이·속성), data/station_pts.json(구 역사 상세 메쉬 정점 표본)
출력: data/final.pkl — 로컬 좌표(러프 프레임 − X0,Y0)"""
import json, os, pickle, re
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPoint, Point, LineString
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
E = json.load(open(os.path.join(D, "final_export.json"), encoding="utf-8"))
X0, Y0 = 1166600.0, 1761100.0


def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []


def P(pts): return [(x - X0, y - Y0) for x, y, *_ in pts]


def outline_poly(r):
    """메쉬 윤곽선들 → 다각형(가장 큰 것이 외곽, 그 안에 든 것은 구멍)"""
    rings = [Polygon(P(o)).buffer(0) for o in r.get("outl", []) if len(o) >= 4]
    rings = [g for g in rings if not g.is_empty and g.area > 0.5]
    if not rings: return Polygon()
    rings.sort(key=lambda g: -g.area)
    g = rings[0]
    for h in rings[1:]:
        if g.symmetric_difference(h).area < 0.02 * g.area: continue          # 같은 링(위·아래 윤곽 중복)
        if g.buffer(0.05).contains(h): g = g.difference(h)                  # 안쪽 링 = 중정
        else: g = g.union(h)
    return g.buffer(0)


LOTS, OPEN, ROADS, WALKS, PLZ, BLDO, ROOF, GLASS, DOTS, TREES = [], [], [], [], [], [], [], [], [], []
B = None
for r in E["recs"]:
    ly = r["layer"]; t = r["type"]; us = r.get("us", {})
    if t == "tree": TREES.append((r["c"][0] - X0, r["c"][1] - Y0, r["r"])); continue
    if "TextDot" == t: DOTS.append(dict(text=r["text"], x=r["pt"][0] - X0, y=r["pt"][1] - Y0, z=r["pt"][2])); continue
    zr = r["bb"][5] - r["bb"][2]
    if "00_구역경계" in ly and "pts" in r: B = Polygon(P(r["pts"])).buffer(0); continue
    if "pts" in r:                                                     # 윤곽선(획지·공원·도로 등) — 면적·속성은 같은 이름의 면 객체와 같다
        g = Polygon(P(r["pts"])).buffer(0) if r.get("closed") and len(r["pts"]) > 3 else None
        rec = dict(layer=ly, name=r["name"], us=us, g=g, line=LineString(P(r["pts"])) if len(r["pts"]) > 1 else None)
        if "01_획지" in ly: LOTS.append(rec)
        elif "02_공원" in ly or "03_보행자" in ly: OPEN.append(rec)
        elif "04_도로" in ly: ROADS.append(rec)
        elif "05_보도" in ly: WALKS.append(rec)
        elif "08_지면" in ly: PLZ.append(rec)
        elif "12_유리" in ly: GLASS.append(rec)
        continue
    if t in ("Extrusion", "Brep", "Mesh"):
        g = outline_poly(r)
        rec = dict(layer=ly, name=r["name"], us=us, g=g, z0=r["bb"][2], z1=r["bb"][5], color=r["color"], type=t)
        if "12_유리" in ly: GLASS.append(rec)
        elif "07_지붕" in ly: ROOF.append(rec)
        elif zr > 1.0: BLDO.append(rec)                                    # 높이 1 m 넘는 솔리드 = 건축물(획지 레이어에 새로 그린 매스 포함)
print("lots", len(LOTS), "open", len(OPEN), "roads", len(ROADS), "walks", len(WALKS), "plz", len(PLZ), "bld objs", len(BLDO), "roof", len(ROOF), "glass", len(GLASS), "dots", len(DOTS), "trees", len(TREES))

# ── 건축물: 같은 용도 레이어에서 평면이 겹치는 층별 솔리드를 한 동으로 묶는다 ──
def cat_of(ly):
    leaf = ly.split("::")[-1]
    return leaf
groups = []
for o in BLDO:
    if o["g"].is_empty: continue
    placed = False
    for gr in groups:
        if gr["cat"] == cat_of(o["layer"]) and gr["g"].buffer(-0.3).intersects(o["g"].buffer(-0.3)) and gr["g"].intersection(o["g"]).area > 0.5 * min(gr["g"].area, o["g"].area):
            gr["objs"].append(o); gr["g"] = unary_union([gr["g"], o["g"]]); gr["z1"] = max(gr["z1"], o["z1"]); gr["z0"] = min(gr["z0"], o["z0"]); placed = True; break
    if not placed: groups.append(dict(cat=cat_of(o["layer"]), objs=[o], g=o["g"], z0=o["z0"], z1=o["z1"]))
# 1층 가로상점 띠는 위층 동에 합친다(평면이 겹치는 다른 용도 동)
shops = [g for g in groups if g["cat"].startswith("1층")]
main = [g for g in groups if not g["cat"].startswith("1층")]
for sgp in shops:
    host = max(main, key=lambda m: m["g"].intersection(sgp["g"]).area, default=None)
    if host is not None and host["g"].intersection(sgp["g"]).area > 0.5 * sgp["g"].area:
        host["objs"] += sgp["objs"]; host["retail"] = True; host["z0"] = min(host["z0"], sgp["z0"])
    else:
        sgp["cat"] = "판매·근린생활"; main.append(sgp)
BLD = []
for gr in main:
    names = [o["us"].get("건축물") or re.sub(r"\s*\d+F$", "", o["name"] or "") for o in gr["objs"]]
    names = [n for n in names if n]
    nm = max(set(names), key=names.count) if names else ""
    fl = [int(o["us"]["층수"]) for o in gr["objs"] if o["us"].get("층수", "").isdigit()]
    term = next((o["us"].get("용어(지구단위계획)") for o in gr["objs"] if o["us"].get("용어(지구단위계획)")), "")
    lot = next((o["us"].get("획지번호") for o in gr["objs"] if o["us"].get("획지번호")), "")
    BLD.append(dict(cat=gr["cat"], name=nm, term=term, lot=lot, g=gr["g"].buffer(0), z0=gr["z0"], z1=gr["z1"], h=gr["z1"] - max(gr["z0"], 0.0),
                    floors=max(fl) if fl else None, retail=gr.get("retail", False), n_obj=len(gr["objs"]), edited=any(o["type"] == "Brep" for o in gr["objs"])))
print("buildings", len(BLD))
for b in sorted(BLD, key=lambda b: (b["cat"], -b["g"].area)):
    print("  %-18s %-24s 면적 %7.0f  높이 %5.1f  층 %s  객체 %d  수정 %s  lot %s" % (b["cat"][:18], b["name"][:24], b["g"].area, b["h"], b["floors"], b["n_obj"], b["edited"], b["lot"]))

# ── 구 역사 상세 모델 평면 윤곽(정점 표본의 오목 껍질) ──
SP = np.array(json.load(open(os.path.join(D, "station_pts.json"))))
mp = shapely.points(SP[:, 0] - X0, SP[:, 1] - Y0)
ST = shapely.concave_hull(shapely.multipoints(mp), ratio=0.08).buffer(0.3).buffer(-0.3)
print("station footprint", round(ST.area), [round(v, 1) for v in ST.bounds], "z", SP[:, 2].min(), SP[:, 2].max())

pickle.dump(dict(B=B, LOTS=LOTS, OPEN=OPEN, ROADS=ROADS, WALKS=WALKS, PLZ=PLZ, BLD=BLD, ROOF=ROOF, GLASS=GLASS, DOTS=DOTS, TREES=TREES, ST=ST,
                 ST_Z=(float(SP[:, 2].min()), float(SP[:, 2].max())), X0=X0, Y0=Y0), open(os.path.join(D, "final.pkl"), "wb"))
