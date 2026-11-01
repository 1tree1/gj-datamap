"""S0 단면 조닝용 절단 — 사용자 평면 캡처의 보라색 세 선(data/section_lines.json, 캡처→로컬 변환은 선형공원 띠·중앙 보행축 윤곽으로 맞춤, 0.723 px/m)
을 최종본 건축물(model.pkl: 동별 구성 솔리드·층 용도)·브리지·구 역사·유리 지붕·지면(도로·보도·보행축·공원·획지·광장)과 교차
출력: data/cuts.pkl — 선별 {L(길이), p0, u(방향), bld[(s0,s1,z0,z1,cat,name,lot)], links, glass[(s,z)], ground[(s0,s1,kind,name)]}"""
import os, json, pickle, math
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
M = pickle.load(open(os.path.join(D, "model.pkl"), "rb")); S = M["S"]
SL = json.load(open(os.path.join(D, "section_lines.json"), encoding="utf-8"))
# 방향: 세로 = 북→남, 가로 = 서→동, 대각선 = 북서→남동(사용자 스케치 W→E)
LINES = {"V": (SL["V"][0], SL["V"][1]), "H": (SL["H"][0], SL["H"][1]), "Dg": (SL["Dg"][0], SL["Dg"][1])}


def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []


def intervals(line, g, p0, u):
    out = []
    x = line.intersection(g)
    for seg in ([x] if x.geom_type == "LineString" else list(getattr(x, "geoms", []))):
        if seg.geom_type != "LineString" or seg.length < 0.3: continue
        ss = [float(np.dot(np.array(c) - p0, u)) for c in seg.coords]
        out.append((min(ss), max(ss)))
    return out


def vault_z(G, bj):
    t = (bj - G["b0"]) / (G["b1"] - G["b0"]); return G["z0"] + (G["z1"] - G["z0"]) * t + G["rise"] * math.sin(math.pi * t)


CUTS = {}
for key, (a, b) in LINES.items():
    p0 = np.array(a, float); p1 = np.array(b, float); L = float(np.linalg.norm(p1 - p0)); u = (p1 - p0) / L
    line = LineString([tuple(p0), tuple(p1)])
    bld = []
    for bb in M["BLD"]:
        for (g, z0, z1, cat) in bb["parts"]:
            for s0, s1 in intervals(line, g, p0, u):
                bld.append((s0, s1, max(z0, 0.0), z1, cat, bb["name"], bb["lot"]))
    links = [(s0, s1, k["z0"], k["z1"], k["kind"]) for k in M["LINKS"] for s0, s1 in intervals(line, k["g"], p0, u)]
    # 유리 볼트: 장축 좌표(a, b)로 표본
    G = S["GLASS"]; o, ua, vb = np.array(G["o"]), np.array(G["ua"]), np.array(G["vb"])
    glass = []
    for s in np.arange(0, L, 0.5):
        q = p0 + u * s; aa = float(np.dot(q - o, ua)); bj = float(np.dot(q - o, vb))
        if G["a0"] <= aa <= G["a1"] and G["b0"] <= bj <= G["b1"]: glass.append((s, vault_z(G, bj)))
    ground = []
    for k, g in S["ROADS"].items():
        for s0, s1 in intervals(line, g, p0, u): ground.append((s0, s1, "도로", {"N": "북측 진입도로", "EW": "동서 도로", "O": "외곽도로"}[k]))
    for o_ in S["OPEN"]:
        for s0, s1 in intervals(line, o_["g"], p0, u): ground.append((s0, s1, "보행", o_["name"]))
    for p_ in S["PARKS"]:
        for s0, s1 in intervals(line, p_["g"], p0, u): ground.append((s0, s1, "공원", p_["name"]))
    for s0, s1 in intervals(line, S["PATH8"], p0, u): ground.append((s0, s1, "보행", "향일문 조망로"))
    for s0, s1 in intervals(line, S["WALK"], p0, u): ground.append((s0, s1, "보도", "보도"))
    for l in S["LOTS"]:
        for s0, s1 in intervals(line, l["g"], p0, u): ground.append((s0, s1, "획지", "%d %s" % (l["no"], l["name"])))
    for p_ in S["PLZ"]:
        for s0, s1 in intervals(line, p_["g"], p0, u): ground.append((s0, s1, "광장" if p_["kind"] in ("광장", "코트") else p_["kind"], p_["name"]))
    sB = intervals(line, S["B"], p0, u)
    CUTS[key] = dict(L=L, p0=p0.tolist(), u=u.tolist(), bld=sorted(bld), links=sorted(links), glass=glass, ground=sorted(ground), inB=sB)
    print("==", key, "길이 %.0f m" % L, "구역 안", [(round(x), round(y)) for x, y in sB])
    for r in sorted(ground):
        if r[2] in ("획지",): continue
        print("   지면 %6.1f–%6.1f  %-4s %s" % (r[0], r[1], r[2], r[3]))
    seen = []
    for r in sorted(bld):
        k_ = (r[5], round(r[0]))
        print("   건물 %6.1f–%6.1f  z %4.1f–%4.1f  %-6s %s (획지 %s)" % (r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
    for r in links: print("   브리지 %6.1f–%6.1f z %.1f–%.1f %s" % r)
    if glass: print("   유리 지붕 s %.1f–%.1f" % (glass[0][0], glass[-1][0]))
pickle.dump(CUTS, open(os.path.join(D, "cuts.pkl"), "wb"))
