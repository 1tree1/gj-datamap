"""S1 맥락 객체(면 단위)를 계획 경계 U에 대해 안/밖/걸침으로 분류. 입력: data/ctx_candidates.json(라이노 export, 계획 좌표계 footprint)"""
import json, pickle, collections, time, sys
from shapely.geometry import Polygon, LineString
from shapely.prepared import prep
import os
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
t0 = time.time()
U = pickle.load(open(os.path.join(D, "U_clean.pkl"), "rb"))["U"]; PU = prep(U)
C = json.load(open(os.path.join(D, "ctx_candidates.json"), encoding="utf-8"))
res = collections.defaultdict(collections.Counter)
obj_state = {}
partial_faces = []
for o in C:
    L = o["layer"]
    if "pts" in o:
        if len(o["pts"]) < 2: continue
        ls = LineString(o["pts"]); inter = ls.intersection(U).length / max(ls.length, 1e-9)
        k = "in" if inter > 0.999 else ("out" if inter < 0.001 else "partial")
        res[L]["curve_" + k] += 1; obj_state[o["id"]] = (k, inter); continue
    st = collections.Counter(); areas = 0.0; ain = 0.0
    for r in o.get("rings", []):
        if len(r) < 3: continue
        p = Polygon(r)
        if not p.is_valid: p = p.buffer(0)
        if p.is_empty or p.area <= 0: continue
        if PU.contains(p): k = "in"; ain += p.area
        elif not PU.intersects(p): k = "out"
        else:
            k = "partial"; ia = p.intersection(U).area; ain += ia
            partial_faces.append((L, o["id"][:8], round(ia / p.area, 3), round(p.area, 1)))
        st[k] += 1; areas += p.area
    for k, v in st.items(): res[L][k] += v
    obj_state[o["id"]] = (dict(st), ain / areas if areas else 0)
print("time %.1fs" % (time.time() - t0))
for L, c in res.items(): print("%-14s %s" % (L, dict(c)))
print("partial faces by layer:", collections.Counter(p[0] for p in partial_faces))
print("sample partial non-building:", [p for p in partial_faces if p[0] != "빌딩"][:25])
bl = [(oid, s) for oid, s in obj_state.items() if isinstance(s[0], dict)]
print("building partial objs", len([1 for o in C if o["layer"] == "빌딩" and isinstance(obj_state.get(o["id"], (None,))[0], dict) and obj_state[o["id"]][0].get("partial")]))
pickle.dump(dict(obj_state=obj_state, partial_faces=partial_faces), open(os.path.join(D, "ctx_classify.pkl"), "wb"))
