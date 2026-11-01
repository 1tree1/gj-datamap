import cv2, numpy as np, pickle, json
from shapely.geometry import Polygon
from shapely import wkb, affinity
from scipy.optimize import minimize

SP = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad"
OLD = r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7d42d444-7313-40a1-ac02-6f82986afca6\scratchpad"
img = cv2.imread(SP + r"\sketch_rot_ccw.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, (125, 70, 70), (165, 255, 255))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
cv2.imwrite(SP + r"\purple_mask.png", mask)
cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cs, key=cv2.contourArea)
print("contour area px", cv2.contourArea(c), "pts", len(c))
outer = Polygon(c[:, 0, :]).buffer(0)
# 획 두께 추정: 외곽 면적 − 구멍 포함 채움 vs 마스크 면적
filled = np.zeros_like(mask); cv2.drawContours(filled, [c], -1, 255, -1)
stroke_area = (mask > 0).sum(); perim = outer.length
w = stroke_area / perim
print("stroke width ≈ %.1f px" % w)
core = outer.buffer(-w / 2)           # 획 중심선 폴리곤
core = core.simplify(1.0)
print("sketch polygon area px²", round(core.area), "bounds", [round(v) for v in core.bounds])
pickle.dump(core.wkb, open(SP + r"\sketch_core.pkl", "wb"))

# 회전본 픽셀 (rx, ry) → 지도방위 픽셀 (X=-ry [동], Y=-rx [북])
def to_map(poly):
    from shapely.geometry import Polygon as P
    return P([(-y, -x) for x, y in poly.exterior.coords])
S = to_map(core)

s1 = pickle.load(open(OLD + r"\step1.pkl", "rb"))
U = wkb.loads(s1["U"])
print("U area", round(U.area))

def tf(poly, p):
    s, th, tx, ty = p
    q = affinity.scale(poly, s, s, origin=(0, 0))
    q = affinity.rotate(q, th, origin=(0, 0), use_radians=False)
    return affinity.translate(q, tx, ty)
def iou(p):
    q = tf(S, p).buffer(0)
    i = q.intersection(U).area; u = q.union(U).area
    return i / u
best = None
sc0 = (U.area / S.area) ** 0.5
for th0 in (-8, -4, 0, 4, 8):
    q0 = affinity.rotate(affinity.scale(S, sc0, sc0, origin=(0, 0)), th0, origin=(0, 0))
    t0 = (U.centroid.x - q0.centroid.x, U.centroid.y - q0.centroid.y)
    r = minimize(lambda p: -iou(p), [sc0, th0, *t0], method="Nelder-Mead", options=dict(xatol=1e-4, fatol=1e-7, maxiter=3000))
    print("start th", th0, "IoU", round(-r.fun, 4), "params", np.round(r.x, 4))
    if best is None or r.fun < best.fun: best = r
print("BEST similarity: IoU", round(-best.fun, 4), "s(m/px)=%.4f th=%.3f° t=(%.2f, %.2f)" % tuple(best.x))
json.dump(dict(s=best.x[0], th=best.x[1], tx=best.x[2], ty=best.x[3], iou=-best.fun), open(SP + r"\sim_fit.json", "w"))
