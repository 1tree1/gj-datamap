"""S4b 맥락 접속 검사·보정 — 경계 U에 닿는 기존 가로(앵커) 하나하나가 부지 안으로 막힘 없이 이어지는지 본다.
  판정: 앵커에서 안쪽으로 30 m 직선 + 1 m 폭 띠가 건물에 닿지 않으면 '연결', 닿으면 '막힘'
  보정: 폭 ≥3 m 막힘 앵커는 건물을 4~6 m 폭으로 관통하는 통로를 낸다 (켜1 이어받기 규칙: 경계에 닿는 가로·골목은 켜1 안까지 연장)
출력: scratch/massing2.pkl, scratch/anchor_status.pkl"""
import pickle, math, sys, collections
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely import affinity
SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
sys.path.insert(0, r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts")
from geomkit import polys, clean
C = pickle.load(open(SP + r"\context.pkl", "rb")); U = C["U"]
NET = pickle.load(open(SP + r"\network.pkl", "rb"))
M = pickle.load(open(SP + r"\massing.pkl", "rb")); BUILD = M["BUILD"]; EXTRA = M["EXTRA"]
A = pickle.load(open(SP + r"\anchors.pkl", "rb"))

streets_all = unary_union(list(NET["streets"].values()) + list(NET["lanes"].values()))

def status(a, blds):
    p = Point(a["x"], a["y"])
    dx, dy = a["dx"], a["dy"]
    # 안쪽 방향
    if not U.contains(Point(p.x + dx * 3, p.y + dy * 3)): dx, dy = -dx, -dy
    if not U.contains(Point(p.x + dx * 3, p.y + dy * 3)): return None, (dx, dy), None
    line = LineString([(p.x, p.y), (p.x + dx * 30, p.y + dy * 30)])
    band = line.buffer(max(1.0, a["w"] / 2 - 0.5), cap_style=2)
    on_street = streets_all.buffer(1.0).intersects(Point(p.x + dx * 2, p.y + dy * 2)) or streets_all.buffer(3).distance(p) < 6
    hit = [b for b in blds if b["geom"].intersects(band) and b["geom"].intersection(band).area > 1.0]
    if on_street and not hit: return "도로·골목 연결", (dx, dy), []
    if on_street and hit: return "도로·골목 연결", (dx, dy), []
    if not hit: return "열린 통로(광장·마당)", (dx, dy), []
    return "막힘(건물)", (dx, dy), hit

rows = []
for a in A:
    if a["w"] < 2.0: continue
    s, d, hit = status(a, BUILD)
    rows.append(dict(a, status=s, inward=d, nhit=len(hit) if hit else 0))

blocked = [r for r in rows if r["status"] == "막힘(건물)"]
print("앵커 %d개(폭≥2 m): " % len(rows) + ", ".join("%s %d" % (k, v) for k, v in collections.Counter(r["status"] for r in rows).items()))
for r in blocked: print("   막힘: %s (%.0f, %.0f) 폭 %.0f m  건물 %d" % (r["side"], r["x"], r["y"], r["w"], r["nhit"]))

# 보정: 폭 ≥3 m 막힘 앵커에 통로
carved = []
for r in blocked:
    if r["w"] < 3.0: continue
    dx, dy = r["inward"]; wc = max(4.0, min(6.0, r["w"] + 1.0))
    line = LineString([(r["x"], r["y"]), (r["x"] + dx * 45, r["y"] + dy * 45)])
    cut = line.buffer(wc / 2, cap_style=2)
    n_cut = 0
    for b in list(BUILD):
        if b["geom"].intersection(cut).area > 0.5:
            new = b["geom"].difference(cut)
            parts = [p for p in polys(new) if p.area >= 30]
            BUILD.remove(b)
            for k, p in enumerate(parts):
                nb = dict(b); nb["geom"] = p; nb["area"] = p.area; nb["gfa"] = p.area * b["floors"]
                BUILD.append(nb)
            n_cut += 1
    carved.append((r["side"], round(r["x"]), round(r["y"]), r["w"], wc, n_cut))
    EXTRA["path"].append(("앵커 관통 통로 %.0fm" % wc, cut.intersection(U)))
print("관통 통로 %d개:" % len(carved)); [print("   ", c) for c in carved]

# 관통 통로로 쪼개진 조각의 번호를 건물군(bid)별로 다시 매긴다
_pc = collections.defaultdict(int)
for b in BUILD:
    b["part"] = _pc[b["bid"]]; _pc[b["bid"]] += 1

rows2 = []
for a in A:
    if a["w"] < 2.0: continue
    s, d, hit = status(a, BUILD)
    rows2.append(dict(a, status=s, inward=d))
print("보정 후: " + ", ".join("%s %d" % (k, v) for k, v in collections.Counter(r["status"] for r in rows2).items()))
for w0, w1, nm in ((5, 99, "폭 5 m 이상"), (3, 5, "폭 3~5 m"), (2, 3, "폭 2~3 m")):
    s = [r for r in rows2 if w0 <= r["w"] < w1]
    ok = [r for r in s if r["status"] != "막힘(건물)"]
    print("  %s: %d개 중 연결 %d개" % (nm, len(s), len(ok)))
pickle.dump(dict(BUILD=BUILD, EXTRA=EXTRA), open(SP + r"\massing2.pkl", "wb"))
pickle.dump(dict(before=rows, after=rows2, carved=carved), open(SP + r"\anchor_status.pkl", "wb"))
