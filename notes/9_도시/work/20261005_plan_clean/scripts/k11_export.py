"""K11 Rhino 내보내기용 JSON — 모형좌표(model = (real5179 + C)/2, z·높이도 1/2), 레이어·색·속성 포함.
출력: model/plan_rhino_clean.json  → rhino_write.py 가 원본 3dm 복사본에 쓴다."""
import pickle, json, sys, os, math, collections
import numpy as np
from pyproj import Transformer
from shapely.geometry import Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from plotkit import *

Cc = np.array([1155149.0, 1762445.9]); tr = Transformer.from_crs(5187, 5179, always_xy=True)
Z_LOT, Z_ROAD, Z_OPEN, Z_BLD = 257.9, 258.0, 258.05, 258.0
os.makedirs(OUT + r"\model", exist_ok=True)
ANCH = pickle.load(open(SP + r"\anchors.pkl", "rb"))
RR = TC["road_rows"]; TR = TC["lot_rows"]; RN = TC["RNAME"]

def to_model(x, y, z): X, Y = tr.transform(x, y); return [round(float((X + Cc[0]) / 2), 4), round(float((Y + Cc[1]) / 2), 4), z]
def ring_of(ring, z, ccw=True):
    p = Polygon(ring.coords); p = orient(p, 1.0 if ccw else -1.0)
    return [to_model(x, y, z) for x, y in p.exterior.coords]
hexrgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]

LAYERS = {"00 계획경계(작업 경계 U)": "#8a2be2",
          "01 획지 면": "#dddddd", "01 획지 경계": "#555555", "02 공원·광장": "#7fc15a",
          "03 도로 차량·보차공존": "#5d7fb0", "03 도로 공유가로 S": "#f19a3e", "03 도로 보행자전용": "#d1495b", "03 도로 보행골목": "#a58bd0", "03 교차부 광장": "#cfcfcb",
          "04 마당·광장(획지 안)": "#ece7de", "04 중정·녹지(획지 안)": "#cfe8b3"}
for cat in CATORDER[:-1]: LAYERS["05 매스 " + cat] = CATCOL[cat]
LAYERS["05 매스 주차전용건축물"] = "#9a9a9a"; LAYERS["05 매스 1층 판매·음식(저층부)"] = CATCOL["판매·음식"]; LAYERS["05 매스 공원시설"] = "#f6bdd4"
LAYERS["06 라벨 획지"] = "#222222"; LAYERS["07 기존 가로 앵커"] = "#c0392b"

items = []
def surf(layer, name, geom, z, color=None, strings=None):
    for k, p in enumerate(polys(geom)):
        if p.area < 1.0: continue
        items.append(dict(kind="surf", layer=layer, name=name + ("" if k == 0 else " (%d)" % (k + 1)), ring=ring_of(p.exterior, z), holes=[ring_of(h, z, False) for h in p.interiors], color=color, strings=strings or {}))
def curve(layer, name, geom, z):
    for p in polys(geom): items.append(dict(kind="curve", layer=layer, name=name, ring=ring_of(p.exterior, z), color=None, strings={}))

# 경계
curve("00 계획경계(작업 경계 U)", "작업 경계 U %s㎡" % format(round(U.area), ","), U, Z_ROAD + 0.1)
# 도로(우선순위 순서 → 교차부는 상위 도로)
roads = dict(NET["streets"]); roads.update(NET["lanes"]); used = []
for r in RR:
    g = roads[r["key"]]; ex = g.difference(unary_union(used)) if used else g; used.append(g)
    layer = "03 도로 공유가로 S" if r["key"] == "S" else {"차량": "03 도로 차량·보차공존", "보행": "03 도로 보행자전용", "골목": "03 도로 보행골목"}[r["group"]]
    surf(layer, "%s %s %gm" % (RN[r["key"]], r["kind"], r["w"]), ex, Z_ROAD, strings={"도로": RN[r["key"]], "성격": r["kind"], "폭원_m": str(r["w"]), "연장_m": str(round(r["L"])), "면적_m2": str(round(r["area_excl"])),
                                                                                 "통행방식": r["mode"], "단면_계획가정": r["cross"], "앵커": r["anchor"]})
surf("03 교차부 광장", "교차부 광장", LP["plaza"], Z_ROAD)
# 공원
for d in PARKS: surf("02 공원·광장", "%s %s" % (d["name"], d["kind"]), d["geom"], Z_ROAD, strings={"공원": d["name"], "종류": d["kind"], "면적_m2": str(round(d["area"]))})
# 획지
LOTC = {c: tint(CATCOL[c], 0.6) for c in CATCOL}
for r in TR:
    d = [l for l in LOTS if l["no"] == r["no"]][0]
    surf("01 획지 면", "Plot %d %s %s㎡" % (r["no"], r["name"], format(round(r["area"]), ",")), d["geom"], Z_LOT, color=hexrgb(LOTC[r["cat"]]),
         strings={"획지": r["id"], "획지명": r["name"], "용도": r["use"], "분류": r["cat"], "획지면적_m2": str(round(r["area"])), "건축면적_m2": str(round(r["fp"])), "건폐율_%": str(round(r["bcr"] * 100, 1)),
                  "연면적_m2": str(round(r["gfa"])), "용적률_%": str(round(r["far"] * 100)), "최고층수": str(r["maxf"]), "최고높이_m": str(round(r["maxh"], 1)), "고도지구_참고": r["godo_txt"],
                  "접도": " ".join("%s(%gm)" % (RN[k], w) for k, w in r["frontage"]), "시설구성": r["comp"], "비고": r["note"]})
    curve("01 획지 경계", "Plot %d" % r["no"], d["geom"], Z_ROAD + 0.02)
    pt = d["geom"].representative_point(); p = to_model(pt.x, pt.y, 262.0)
    items.append(dict(kind="dot", layer="06 라벨 획지", name="라벨 Plot %d" % r["no"], pos=p, text="%d %s\n%s㎡ · %dF" % (r["no"], r["name"], format(round(r["area"]), ","), r["maxf"]), color=None, strings={}))
# 마당
for lid, nm, g in M["COURTS"]: surf("04 중정·녹지(획지 안)", "%s %s" % (lid, nm), g, Z_OPEN)
for lid, nm, g, col in M["OPEN"]: surf("04 마당·광장(획지 안)", "%s %s" % (lid, nm), g, Z_OPEN, color=hexrgb({"#cfe6b4": "#cfe8b3"}.get(col, col)))
# 고도지구(참고)
GODO = [g for g in C["G"] if g["kind"] == "최고"]
def godo_of(geom):
    best = None
    for g in GODO:
        ov = geom.intersection(g["geom"]).area
        if ov > 0 and (best is None or ov > best[0]): best = (ov, g["godo_nm"], g["h_max"])
    return best
# 매스
nholes = 0
def ext(layer, name, p, z0, h_real, strings):
    global nholes
    nholes += len(p.interiors)
    items.append(dict(kind="ext", layer=layer, name=name, ring=ring_of(p.exterior, z0), holes=[ring_of(h, z0, False) for h in p.interiors], h=round(h_real / 2.0, 4), color=None, strings=strings))
for b in sorted(BUILD, key=lambda x: (x["lot_no"], x["name"])):
    g = godo_of(b["geom"]) if b["role"] != "공원시설" else None
    for k, p in enumerate(polys(b["geom"])):
        st = {"획지": b["lot"], "획지번호": str(b["lot_no"]), "건물": b["name"], "용도": b["use"], "범례": b["cat"], "층수": str(b["floors"]), "층고_m": str(b["floor_h"]), "높이_m": str(b["h"]),
              "건축면적_m2": str(round(p.area, 1)), "연면적_m2": str(round(p.area * b["floors"], 1)), "1층 판매·음식": "예" if b["retail_ground"] else "아니오"}
        if g: st["고도지구_참고"] = "%s %sm%s" % (g[1], g[2], " (초과)" if b["h"] > g[2] + 1e-6 else "")
        if b["role"] == "공원시설": layer = "05 매스 공원시설"
        elif b["role"] == "주차": layer = "05 매스 주차전용건축물"
        else: layer = "05 매스 " + b["cat"]
        nm = "P%d.%d %s %dF %.1fm" % (b["lot_no"], k + 1, b["name"], b["floors"], b["h"])
        if b["retail_ground"] and b["floors"] >= 2:
            ext("05 매스 1층 판매·음식(저층부)", nm + " [1층]", p, Z_BLD, b["floor_h"], st)
            ext(layer, nm + " [2층~]", p, Z_BLD + b["floor_h"] / 2.0, b["h"] - b["floor_h"], st)
        else:
            ext(layer, nm, p, Z_BLD, b["h"], st)
# 앵커
for a in ANCH:
    items.append(dict(kind="point", layer="07 기존 가로 앵커", name="앵커 %s %gm" % (a["side"], a["w"]), pos=to_model(a["x"], a["y"], Z_ROAD + 0.1), color=[192, 57, 43], strings={"방향": a["side"], "기존가로폭_m": str(a["w"])}))

json.dump(dict(layers=LAYERS, items=items, parent="획지매스_규제미적용v1b"), open(OUT + r"\model\plan_rhino_clean.json", "w", encoding="utf-8"), ensure_ascii=False)
print("items", len(items), dict(collections.Counter(i["kind"] for i in items)))
print("ext layers:", dict(collections.Counter(i["layer"] for i in items if i["kind"] == "ext")))
print("구멍 있는 매스:", nholes)
