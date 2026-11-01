# -*- coding: utf-8 -*-
"""S7 조립 데이터 v3 — design.json(획지·공원·광장·매스·식재·라벨, 계획 좌표 m)에 사용자 도로·보도(이번 세션 내보내기 sel_plan.json)를 합쳐
data/design_v3.json 을 만든다. 라이노 빌더(rh_build.py)가 이 파일 하나만 읽는다. 좌표는 계획 좌표(실측 m, z=0 기준)."""
import json, os, sys
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\5ac42c4f-b205-49dd-aa7e-de94aecf7727\scratchpad"
des = json.load(open(os.path.join(D, "design.json"), encoding="utf-8"))
sel = json.load(open(os.path.join(SP, "sel_plan.json"), encoding="utf-8"))


def parts_of(r):
    out = []
    for f in r["faces"]:
        outer = [l["pts"] for l in f["loops"] if "Outer" in l["kind"]]
        inner = [l["pts"] for l in f["loops"] if "Inner" in l["kind"]]
        if not outer: continue
        out.append(dict(ext=[[round(p[0], 4), round(p[1], 4)] for p in outer[0]], holes=[[[round(p[0], 4), round(p[1], 4)] for p in h] for h in inner]))
    return out


roads, walks = [], []
for r in sel:
    L = r["layer"].split("::")[-1]
    if r["type"] != "Brep": continue
    if L == "도로": roads.append(dict(id=r["id"], parts=parts_of(r)))
    elif L == "보도": walks.append(dict(id=r["id"], parts=parts_of(r)))


def area(parts):
    return unary_union([Polygon(q["ext"], q["holes"]).buffer(0) for q in parts]).area


# 보행 면 분류: 가장 큰 보도면(32,269㎡)은 남북 보행축 — 보행자전용도로, 나머지는 보도
for w in walks:
    w["area"] = area(w["parts"]); w["kind"] = "보행자전용도로" if w["area"] > 20000 else "보도"
for r in roads:
    r["area"] = area(r["parts"]); r["kind"] = "도로"

# 획지 메타(지구단위계획 용어) — 획지계획표.csv 와 일치
USE = {
    "공1": dict(use="공공청사(업무시설 중 공공업무시설)", allow="근린생활시설(편익), 문화 및 집회시설(회의·전시)", zone="제2종일반주거지역(상향)", layer="공공청사"),
    "주1": dict(use="공동주택(청년·신혼 임대주택)", allow="제1종 근린생활시설, 노유자시설(어린이집), 주민공동시설", zone="제2종일반주거지역(상향)", layer="공동주택"),
    "업1": dict(use="업무시설(청년 창업·공유오피스)", allow="제1·2종 근린생활시설(저층부), 교육연구시설", zone="일반상업지역(상향)", layer="업무시설"),
    "업2": dict(use="업무시설(청년 창업·공유오피스)", allow="제1·2종 근린생활시설(저층부), 교육연구시설", zone="일반상업지역(상향)", layer="업무시설"),
    "문1": dict(use="문화 및 집회시설(공연장)", allow="근린생활시설, 문화 및 집회시설(다목적실)", zone="일반상업지역(상향)", layer="문화및집회시설"),
    "문2": dict(use="문화 및 집회시설(전시장: 근대역사관)+관광휴게시설", allow="교육연구시설, 근린생활시설, 문화 및 집회시설(체험·교육)", zone="일반상업지역(상향)", layer="문화및집회시설"),
    "문3": dict(use="관광휴게시설+제1·2종 근린생활시설·판매시설", allow="문화 및 집회시설(공방·체험)", zone="일반상업지역(상향)", layer="근린생활·판매시설"),
    "문4": dict(use="문화 및 집회시설(창작 레지던시·체험관)", allow="교육연구시설, 제2종 근린생활시설(공방), 작가 체류실(부속)", zone="일반상업지역(상향)", layer="문화및집회시설"),
    "문5": dict(use="문화 및 집회시설(창작 레지던시·체험관)", allow="교육연구시설, 제2종 근린생활시설(공방), 작가 체류실(부속)", zone="일반상업지역(상향)", layer="문화및집회시설"),
    "상1": dict(use="제1·2종 근린생활시설·판매시설(성동시장 연계)", allow="문화 및 집회시설(전시·체험)", zone="일반상업지역(상향)", layer="근린생활·판매시설"),
    "체1": dict(use="운동시설(생활체육시설)", allow="제1종 근린생활시설", zone="일반상업지역(상향)", layer="운동시설"),
    "관1": dict(use="자동차 관련 시설(주차전용건축물)+관광휴게시설(방문자 관문)", allow="근린생활시설(관광안내), 운수시설(소규모 대합실)", zone="일반상업지역(상향)", layer="주차전용·관광휴게"),
}
for l in des["lots"]:
    l.update(USE[l["code"]]); l["area"] = area(l["parts"])
for g in des["greens"]:
    g["area"] = area(g["parts"])
for p in des["plazas"]:
    p["area"] = area(p["parts"])
for m in des["masses"]:
    m["fp"] = area(m["parts"]); m["gfa"] = 2807.0 if m.get("existing") else m["fp"] * m["floors"]

out = dict(frame="plan(EPSG:5179 m, z=0)", boundary=des["boundary"], lots=des["lots"], greens=des["greens"], plazas=des["plazas"], masses=des["masses"],
           pavilions=des["pavilions"], trees=des["trees"], labels=des["labels"], roads=roads, walks=walks)
json.dump(out, open(os.path.join(D, "design_v3.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(out, open(os.path.join(SP, "design_v3.json"), "w", encoding="utf-8"), ensure_ascii=False)
tot = dict(lots=sum(l["area"] for l in des["lots"]), greens=sum(g["area"] for g in des["greens"]), roads=sum(r["area"] for r in roads), walks=sum(w["area"] for w in walks))
tot["sum"] = sum(tot.values()); tot["boundary"] = Polygon(des["boundary"]).area
print({k: round(v, 1) for k, v in tot.items()})
print("walks:", [(w["kind"], round(w["area"])) for w in walks], "roads:", [round(r["area"]) for r in roads])
