"""D4 마스터플랜 3dm 작성(rhino3dm) — 사용자 문서와 같은 러프 프레임 좌표·단위 표기(mm, 실제 1단위 = 1 m)
가져오기(Import)하면 aardvark 문서의 러프 배치 위에 그대로 겹친다. 원본 3dm은 건드리지 않는다.
출력: 구경주역_마스터플랜_러프정리_v1.3dm (폴더 루트)"""
import os, json, pickle
import numpy as np
import rhino3dm as r3
import trimesh
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); OUT = os.path.join(HERE, "..")
S = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
B, LOTS, PARKS, OPEN, MASS, PLZ, TREES, CATS = S["B"], S["LOTS"], S["PARKS"], S["OPEN"], S["MASS"], S["PLZ"], S["TREES"], S["CATS"]
X0, Y0, XS = S["X0"], S["Y0"], S["XSHIFT"]
CTXB = json.load(open(os.path.join(HERE, "..", "..", "20261011_masterplan_v1", "data", "ctx_buildings_planframe.json")))


def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []


def hexc(h, a=255):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), a)


f = r3.File3dm()
f.Settings.ModelUnitSystem = r3.UnitSystem.Millimeters                    # 사용자 문서와 같은 단위 표기(값은 m)
f.Settings.ModelAbsoluteTolerance = 0.001


def layer(name, color, parent=None):
    L = r3.Layer(); L.Name = name; L.Color = hexc(color)
    if parent is not None: L.ParentLayerId = f.Layers[parent].Id
    return f.Layers.Add(L)


ROOT = layer("마스터플랜_러프정리_v1", "#000000")
LY = {k: layer(k, c, ROOT) for k, c in [("00_구역경계", "#d7191c"), ("01_획지", "#555555"), ("02_공원·녹지", "#4caf50"), ("03_보행자전용도로·광장", "#9ccc65"),
                                         ("04_도로", "#9e9e9e"), ("05_보도", "#cfcfcf"), ("06_건축물", "#333333"), ("07_옥상녹화·태양광", "#a9d577"),
                                         ("08_지면요소", "#c8b58a"), ("09_식재", "#5a9e3a"), ("10_라벨", "#000000"), ("11_주변건물(참고)", "#d0d0d0")]}
LOT_SUB = {}
for l in LOTS:
    key = l["use"]
    if key not in LOT_SUB: LOT_SUB[key] = layer(key, CATS[l["cat"]][0], LY["01_획지"])
BLD_SUB = {k: layer(v[1], v[0], LY["06_건축물"]) for k, v in CATS.items()}
BLD_SUB["1층가로상점"] = layer("1층 가로상점(근린생활)", CATS["판매"][0], LY["06_건축물"])


def attr(li, name="", color=None, us=None, group=None):
    a = r3.ObjectAttributes(); a.LayerIndex = li; a.Name = name
    if color is not None: a.ObjectColor = hexc(color); a.ColorSource = r3.ObjectColorSource.ColorFromObject
    for k, v in (us or {}).items(): a.SetUserString(str(k), str(v))
    if group is not None: a.AddToGroup(group)
    return a


def G(x, y): return (x + X0, y + Y0)                                       # 로컬 → 러프 프레임


def pline(coords, z=0.0):
    pts = r3.Point3dList()
    for x, y in coords: gx, gy = G(x, y); pts.Add(gx, gy, z)
    return r3.PolylineCurve(pts)


def add_outline(g, li, name="", us=None, z=0.0, color=None):
    for p in polys(g):
        for ring in [p.exterior] + list(p.interiors):
            f.Objects.AddCurve(pline(list(ring.coords), z), attr(li, name, color, us))


def add_face(g, li, z, color, name="", us=None):
    """평면 다각형(구멍 포함) → 두께 2 cm 압출 솔리드(메쉬 삼각형 선이 보이지 않게)"""
    for p in polys(g):
        if p.area < 0.5: continue
        e = extr(p, z, 0.02)
        if e is not None: f.Objects.AddExtrusion(e, attr(li, name, color, us))


def extr(p, z0, h):
    """구멍 있는 다각형 → 캡 닫힌 압출체(z0에서 높이 h)"""
    p = orient(p.simplify(0.02, preserve_topology=True), 1.0)
    e = r3.Extrusion.Create(pline(list(p.exterior.coords), 0.0), h, True)
    if e is None: return None
    if len(p.interiors):
        xf = r3.Transform.PlaneToPlane(e.GetProfilePlane(0.0), r3.Plane.WorldXY())   # 안쪽 단면은 단면 평면 로컬 좌표로 넣어야 한다
        for ring in p.interiors:
            c = pline(list(ring.coords), 0.0); c.Transform(xf)
            if not e.AddInnerProfile(c): print("  ! 중정 구멍 추가 실패")
    bb = e.GetBoundingBox()
    if bb.Min.Z < -1e-6: e.Translate(r3.Vector3d(0, 0, -bb.Min.Z))      # 법선이 아래로 향한 경우 보정
    e.Translate(r3.Vector3d(0, 0, z0))
    return e


# 00 경계
add_outline(B, LY["00_구역경계"], "구역경계", {"면적㎡": round(B.area, 1)})
# 01 획지(경계선 + 옅은 용도면)
for l in LOTS:
    us = {"획지번호": l["no"], "획지코드": l["code"], "용지": l["use"], "획지명": l["name"], "지정용도": l["main"], "권장용도": l["allow"],
          "면적㎡": round(l["area"], 1), "건축면적㎡": round(l["ba"], 1), "연면적㎡": round(l["gfa"], 1), "최고층": l["maxf"], "최고높이m": l["maxh"]}
    add_outline(l["g"], LOT_SUB[l["use"]], "%d %s" % (l["no"], l["name"]), us, 0.02)
    c = np.array(hexc(CATS[l["cat"]][0])[:3], float) * 0.14 + 255 * 0.86
    add_face(l["g"], LOT_SUB[l["use"]], 0.0, "#%02x%02x%02x" % tuple(int(v) for v in c), "%d %s 용도면" % (l["no"], l["name"]), us)
# 02 공원 · 03 보행자전용도로·광장
for p in PARKS:
    us = {"구분": p["kind"], "명칭": p["name"], "면적㎡": round(p["area"], 1)}
    add_outline(p["g"], LY["02_공원·녹지"], "%s %s" % (p["key"], p["name"]), us, 0.02); add_face(p["g"], LY["02_공원·녹지"], 0.05, "#b4dc8e", p["name"], us)
for o in OPEN:
    us = {"구분": o["kind"], "명칭": o["name"], "면적㎡": round(o["area"], 1)}
    add_outline(o["g"], LY["03_보행자전용도로·광장"], "%s %s" % (o["key"], o["name"]), us, 0.02)
    add_face(o["g"], LY["03_보행자전용도로·광장"], 0.05, "#bfe09b" if o["key"] == "D" else "#ece7da", o["name"], us)
# 04 도로 · 05 보도
for k, g in S["ROADS"].items():
    nm = {"N": "북측 진입도로(폭 13m)", "EW": "동서 도로(폭 20m)"}[k]
    add_outline(g, LY["04_도로"], nm, {"면적㎡": round(g.area, 1)}, 0.02); add_face(g, LY["04_도로"], 0.0, "#d6d6d3", nm)
for g, nm in ((S["WALK"], "외곽 보도"), (S["PATH8"], "보행자전용도로(폭 8m)")):
    add_outline(g, LY["05_보도"], nm, {"면적㎡": round(g.area, 1)}, 0.02); add_face(g, LY["05_보도"], 0.0, "#fbfbfa", nm)
# 08 지면요소
PC = {"광장": "#e9e3d3", "노외주차": "#c9c9c6", "소공원": "#b4dc8e", "텃밭": "#c8a878", "중정": "#bfe09b"}
for p in PLZ:
    add_outline(p["g"], LY["08_지면요소"], p["name"], {"구분": p["kind"], "면적㎡": round(p["g"].area, 1)}, 0.12)
    add_face(p["g"], LY["08_지면요소"], 0.1, PC[p["kind"]], p["name"])
# 06 건축물 — 층별 솔리드(동마다 그룹), 07 옥상
nobj = 0
for i, m in enumerate(MASS):
    gr = r3.Group(); gr.Name = "%02d %s" % (i + 1, m["name"]); f.Groups.Add(gr); gi = len(f.Groups) - 1
    us = {"획지번호": m["lot"], "건축물": m["name"], "용어(지구단위계획)": m["term"], "용도분류": CATS[m["cat"]][1], "층수": m["floors"], "층고m": m["fh"],
          "높이m": m["h"], "건축면적㎡": round(m["g"].area, 1), "연면적㎡": round(m["g"].area * m["floors"], 1), "러프원본": m["src"], "조정내역": m["adj"]}
    for k in range(m["floors"]):
        z0 = k * m["fh"]
        retail = (k == 0 and m["retail"] and m["cat"] != "판매")
        li = BLD_SUB["1층가로상점"] if retail else BLD_SUB[m["cat"]]
        col = CATS["판매"][0] if retail else CATS[m["cat"]][0]
        for p in polys(m["g"]):
            e = extr(p, z0, m["fh"])
            if e is None: continue
            a = attr(li, "%s %dF" % (m["name"], k + 1), col, dict(us, 층=k + 1))
            a.AddToGroup(gi)
            f.Objects.AddExtrusion(e, a); nobj += 1
    top = m["h"]
    if m["roof"] == "solar":
        add_face(m["g"].buffer(-2.0, join_style=2), LY["07_옥상녹화·태양광"], top + 0.1, "#5d6b80", m["name"] + " 옥상 태양광")
    elif m["roof"] != "heritage":
        add_face(m["g"].buffer(-1.3, join_style=2), LY["07_옥상녹화·태양광"], top + 0.1, "#a9d577", m["name"] + " 옥상녹화")
# 09 식재 — 수관 구(球)
for kind, T in TREES.items():
    for x, y, rr in T:
        gx, gy = G(x, y)
        s = r3.Sphere(r3.Point3d(gx, gy, 3.0 + 0.8 * rr), rr).ToBrep()
        f.Objects.AddBrep(s, attr(LY["09_식재"], "수목(%s)" % kind))
        f.Objects.AddCurve(r3.LineCurve(r3.Point3d(gx, gy, 0), r3.Point3d(gx, gy, 3.0)), attr(LY["09_식재"], "수간"))
# 10 라벨
from shapely.ops import polylabel
for l in LOTS:
    pt = polylabel(l["g"], 1.0); gx, gy = G(pt.x, pt.y)
    f.Objects.AddTextDot("%d %s" % (l["no"], l["name"]), r3.Point3d(gx, gy, l["maxh"] + 6), attr(LY["10_라벨"], "획지 %d" % l["no"]))
for p in PARKS + OPEN:
    pt = polylabel(max(polys(p["g"]), key=lambda g: g.area), 1.0); gx, gy = G(pt.x, pt.y)
    f.Objects.AddTextDot("%s %s" % (p["key"], p["name"]), r3.Point3d(gx, gy, 6), attr(LY["10_라벨"], p["name"]))
# 11 주변 건물(참고, v3 계획 프레임 → 러프 프레임)
Bb = B.buffer(1.0); nctx = 0
for b in CTXB:
    pts = [(x - XS - X0, y - Y0) for x, y in b["p"]]
    try: pg = Polygon(pts).buffer(0)
    except Exception: continue
    if pg.is_empty or pg.area < 8 or Bb.contains(pg.representative_point()) or pg.distance(B) > 400: continue
    for p in polys(pg):
        e = extr(p.simplify(0.05), 0.0, max(b["h"], 3.5))
        if e is not None: f.Objects.AddExtrusion(e, attr(LY["11_주변건물(참고)"], "주변건물", us={"높이m": max(b["h"], 3.5)})); nctx += 1
path = os.path.join(OUT, "구경주역_마스터플랜_러프정리_v1.3dm")
ok = f.Write(path, 8)
print("write", ok, path, "buildings(floor solids)", nobj, "ctx", nctx, "objects", len(f.Objects))
