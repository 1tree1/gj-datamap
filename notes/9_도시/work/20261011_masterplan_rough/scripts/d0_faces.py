"""D0 러프 배치 선(지구단위계획 레이어·0 레이어)을 노드화·면 분할해 가구·가로 면을 얻는다 → data/faces.pkl + sheets/d0_faces.png"""
import json, os, pickle
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union, polygonize, snap
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); SH = os.path.join(HERE, "..", "sheets")
plt.rcParams["font.family"] = "Malgun Gothic"
d = json.load(open(os.path.join(D, "rough_sel.json"), encoding="utf-8"))
X0, Y0 = 1166600.0, 1761100.0
lines = []
for i, c in enumerate(d["curves"]):
    if c["layer"] == "B0014112": continue          # 매스 외곽선은 제외(가구·가로 선만)
    if "::" in c["layer"] and c["closed"] and i != 97: continue   # 빨간 레이어 닫힌 도형(매스 성격)은 제외
    P = [(p[0] - X0, p[1] - Y0) for p in c["pts"]]
    if len(P) >= 2: lines.append(LineString(P))
B = Polygon([(p[0] - X0, p[1] - Y0) for p in d["curves"][97]["pts"]]).buffer(0)
# 끝점이 살짝 떨어진 선을 붙이기: 각 선 끝점을 0.6 m 연장
import numpy as np
def extend(ls, e=0.8):
    cs = np.array(ls.coords)
    if len(cs) < 2: return ls
    a = cs[0] + (cs[0] - cs[1]) / (np.linalg.norm(cs[0] - cs[1]) + 1e-9) * e
    b = cs[-1] + (cs[-1] - cs[-2]) / (np.linalg.norm(cs[-1] - cs[-2]) + 1e-9) * e
    return LineString([tuple(a)] + [tuple(p) for p in cs] + [tuple(b)])
L = unary_union([extend(l) for l in lines] + [B.exterior])
faces = [f for f in polygonize(L) if f.area > 20 and B.buffer(0.5).contains(f.representative_point())]
print("faces", len(faces), "sum", round(sum(f.area for f in faces)), "B", round(B.area))
pickle.dump(dict(B=B, faces=faces, X0=X0, Y0=Y0), open(os.path.join(D, "faces.pkl"), "wb"))
fig, ax = plt.subplots(figsize=(10, 30), dpi=100)
import random; rnd = random.Random(3)
for k, f in enumerate(faces):
    xs, ys = f.exterior.xy
    ax.fill(xs, ys, color=(rnd.random() * .6 + .4, rnd.random() * .6 + .4, rnd.random() * .6 + .4), lw=0.4, ec="k")
    p = f.representative_point(); ax.text(p.x, p.y, "%d\n%d" % (k, f.area), fontsize=6, ha="center", va="center")
ax.set_aspect("equal"); ax.set_xlim(95, 420); ax.set_ylim(45, 1005)
fig.savefig(os.path.join(SH, "d0_faces.png"), bbox_inches="tight")
