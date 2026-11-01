"""S8 Rhino 내보내기용 JSON — 모형좌표(model = (real5179 + C)/2, z·높이도 1/2), 레이어·색·속성 포함.
출력: scratch/plan_rhino.json"""
import pickle, json, sys, math
import numpy as np
from pyproj import Transformer
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
OUT = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing"
sys.path.insert(0, OUT + r"\scripts")
from geomkit import polys
C = pickle.load(open(SP + r"\context.pkl", "rb")); U = C["U"]
NET = pickle.load(open(SP + r"\network.pkl", "rb"))
M = pickle.load(open(SP + r"\massing2.pkl", "rb")); BUILD, EXTRA = M["BUILD"], M["EXTRA"]
T = pickle.load(open(SP + r"\tables.pkl", "rb")); AS = pickle.load(open(SP + r"\anchor_status.pkl", "rb"))
Cc = np.array([1155149.0, 1762445.9]); tr = Transformer.from_crs(5187, 5179, always_xy=True)

Z_BLOCK, Z_ROAD, Z_OPEN, Z_BLD = 257.9, 258.0, 258.05, 258.0     # 모형 z (기존 지구단위계획 면 256.4–257.6 위)

def to_model(x, y, z):
    X, Y = tr.transform(x, y)
    return [round(float((X + Cc[0]) / 2), 4), round(float((Y + Cc[1]) / 2), 4), z]
def ring_of(poly, z):
    p = orient(poly, 1.0)                      # 바깥 링 반시계
    return [to_model(x, y, z) for x, y in p.exterior.coords]

CATCOL = {"문화·교육·공공": "#3d8fd8", "상업·업무": "#e0432d", "창조산업": "#8e4fb8", "여가·오락·체육": "#1f9e92", "주거": "#f6df4a", "판매·음식": "#f08ab4",
          "교통·방문자": "#b9b9b9", "역사유산": "#b8662b", "오픈스페이스": "#6bbd3c"}
MAJOR_COL = {"공원·녹지": "#6bbd3c", "공공(체육·생활SOC)": "#1f9e92", "주거": "#f6df4a", "공공청사": "#3d8fd8", "문화": "#1f9e92", "업무(창업지원)": "#e0432d", "공공(주민공동)": "#8fbfe8",
             "창조산업": "#8e4fb8", "상업(전통시장 연계)": "#f08ab4", "광장·역사문화": "#d9b99b", "교통·관광지원": "#cfcfcf", "주차": "#9a9a9a", "상업(관광 휴게·판매)": "#f6b5d0"}
hexrgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]

LAYERS = {   # 하위 레이어명: 색
    "00 가로(차량·보차공존·공유)": "#333338", "00 보행자전용도로": "#7a6446", "00 보행골목": "#8a8a8a", "00 교차부 광장": "#e8e4da",
    "01 녹지띠(동서 그린 보행축)": "#7fc15a", "01 광장·마당(공개공지)": "#ece7de", "01 삼층석탑 마당": "#e9d9bd", "01 임시 평면주차": "#cfcfcf", "01 산책로": "#f0e9d6",
    "02 가구 경계": "#8a2be2", "02 가구 면": "#dddddd",
    "03 매스 문화·교육·공공": CATCOL["문화·교육·공공"], "03 매스 상업·업무": CATCOL["상업·업무"], "03 매스 창조산업": CATCOL["창조산업"], "03 매스 여가·오락·체육": CATCOL["여가·오락·체육"],
    "03 매스 주거": CATCOL["주거"], "03 매스 판매·음식": CATCOL["판매·음식"], "03 매스 교통·방문자": CATCOL["교통·방문자"], "03 매스 주차전용건축물": "#9a9a9a", "03 매스 역사유산": CATCOL["역사유산"],
    "04 라벨 가구": "#222222", "04 라벨 프로그램 번호": "#c0182d", "05 기존 가로 앵커": "#1a9850",
}
items = []
def surf(layer, name, poly, z, color=None, strings=None):
    for k, p in enumerate(polys(poly)):
        if p.area < 1.0: continue
        items.append(dict(kind="surf", layer=layer, name=name + ("" if k == 0 else " (%d)" % (k + 1)), ring=ring_of(p, z), color=color, strings=strings or {}))
def curve(layer, name, poly, z):
    for p in polys(poly): items.append(dict(kind="curve", layer=layer, name=name, ring=ring_of(p, z), color=None, strings={}))

# 가로
for k, g in NET["streets"].items():
    pts, w, cls, desc, basis = NET["STREETS"][k]
    layer = "00 가로(차량·보차공존·공유)" if k in ("A", "B", "C", "D", "S", "S2", "E") else "00 보행자전용도로"
    surf(layer, "%s %s %.0fm (%s)" % (k, desc.split(" — ")[0], w, cls), g, Z_ROAD, strings={"가로": k, "폭_m": str(w), "구분": cls, "근거": basis})
for k, g in NET["lanes"].items():
    pts, w, desc, basis = NET["LANES"][k]
    surf("00 보행골목", "%s %s %.0fm" % (k, desc, w), g, Z_ROAD, strings={"가로": k, "폭_m": str(w), "근거": basis})
surf("00 교차부 광장", "교차부 광장(자투리)", NET["plaza_extra"], Z_ROAD)
surf("01 녹지띠(동서 그린 보행축)", "녹지띠 G1·G2", NET["green_all"], Z_ROAD)
for nm, g in EXTRA["plaza"]: surf("01 광장·마당(공개공지)", nm, g, Z_OPEN)
for nm, g in EXTRA["court"]: surf("01 광장·마당(공개공지)", nm, g, Z_OPEN)
for nm, g in EXTRA["heritage_plaza"]: surf("01 삼층석탑 마당", nm + " (반경 22 m, 허용기준 미확인 → 보수적)", g, Z_OPEN)
for nm, g in EXTRA["surface_parking"]: surf("01 임시 평면주차", nm, g, Z_OPEN)
for nm, g in EXTRA["path"]: surf("01 산책로", nm, g, Z_OPEN)

# 가구
for b in NET["blocks"]:
    info = T["blk_info"][b["id"]]
    surf("02 가구 면", "%s %s %s㎡" % (b["id"], info["label"], format(round(b["area"]), ",")), b["geom"], Z_BLOCK, color=hexrgb(MAJOR_COL.get(info["major"], "#dddddd")),
         strings={"가구": b["id"], "계획용도": info["label"], "대분류": info["major"], "면적_m2": str(round(b["area"])), "건폐율_%": str(round(info["fp"] / b["area"] * 100, 1)), "용적률_%": str(round(info["gfa"] / b["area"] * 100, 1)),
                  "현행용도지역": info["zn"]})
    curve("02 가구 경계", "%s %s" % (b["id"], info["label"]), b["geom"], Z_ROAD)
    c = b["geom"].representative_point(); p = to_model(c.x, c.y, 259.2)
    items.append(dict(kind="dot", layer="04 라벨 가구", name="라벨 " + b["id"], pos=p, text="%s %s\n%s㎡" % (b["id"], info["label"], format(round(b["area"]), ",")), color=None, strings={}))

# 건물 매스
def layer_of(b):
    if b.get("role") == "주차": return "03 매스 주차전용건축물"
    return "03 매스 " + b["cat"]
for b in sorted(BUILD, key=lambda x: (x["block"], x["bid"], x["part"])):
    for p in polys(b["geom"]):
        items.append(dict(kind="ext", layer=layer_of(b), name="%s.%d %s %dF %.1fm" % (b["bid"], b["part"], b["tag"], b["floors"], b["h"]), ring=ring_of(p, Z_BLD), h=round(b["h"] / 2.0, 4), color=None,
                          strings={"가구": b["block"], "프로그램": b["prog"], "명칭": b["tag"], "용도": b["use"], "범례": b["cat"], "층수": str(b["floors"]), "층고_m": str(b["floor_h"]), "높이_m": str(b["h"]),
                                   "건축면적_m2": str(round(p.area, 1)), "연면적_m2": str(round(p.area * b["floors"], 1)), "경계방향": b["side"], "켜": str(b["band"]), "켜규칙_상한층": str(b["side_cap"]),
                                   "고도지구_상한_m": str(b["h_cap"]), "켜규칙_예외": "예" if b["exc"] else "아니오"}))
for nm, pt, hh in EXTRA["marker"]:
    circ = pt.buffer(1.4, resolution=8)
    items.append(dict(kind="ext", layer="03 매스 역사유산", name=nm + " (위치 표지)", ring=ring_of(circ, Z_BLD), h=round(hh / 2.0, 4), color=None, strings={"비고": "지정유산(도 문화유산자료) — 위치 표시용 단순 입체"}))

# 프로그램 번호 라벨
sys.path.insert(0, OUT + r"\scripts")
from plan_calls import CALL
for no, nm, (x, y) in CALL:
    items.append(dict(kind="dot", layer="04 라벨 프로그램 번호", name="번호 %d" % no, pos=to_model(x, y, 260.5), text="%d %s" % (no, nm), color=None, strings={}))

# 앵커 점
for r in AS["after"]:
    items.append(dict(kind="point", layer="05 기존 가로 앵커", name="앵커 %s %.0fm %s" % (r["side"], r["w"], r["status"]), pos=to_model(r["x"], r["y"], Z_ROAD + 0.1), color={"도로·골목 연결": [26, 152, 80], "열린 통로(광장·마당)": [240, 160, 0], "막힘(건물)": [214, 39, 40]}[r["status"]],
                  strings={"방향": r["side"], "기존가로폭_m": str(r["w"]), "상태": r["status"]}))

json.dump(dict(layers=LAYERS, items=items), open(SP + r"\plan_rhino.json", "w", encoding="utf-8"), ensure_ascii=False)
import collections
print("items", len(items), dict(collections.Counter(i["kind"] for i in items)))
print("ext layers:", dict(collections.Counter(i["layer"] for i in items if i["kind"] == "ext")))
holes = sum(1 for b in BUILD for p in polys(b["geom"]) if len(p.interiors) > 0)
print("구멍 있는 매스:", holes)
