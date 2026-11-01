"""C3 정합된 주변 건물 → 3dm(러프 프레임 = 사용자 최종본 '구경주역_마스터플랜_최종.3dm'과 같은 좌표, 단위 표기 mm·실제 1단위 = 1 m)
가져오기(Import)하면 최종본의 기존 '11_주변건물(참고)'(34° 돌아간 잘못된 배경) 대신 쓸 수 있다.
콘타 모델(최종콘타모델_v2) 자체를 맞추려면: 원점(0,0,0) 기준 2배 축척 → 이동 (DX, DY) — 값은 아래에서 출력"""
import os, pickle
import numpy as np
import rhino3dm as r3
from shapely.geometry.polygon import orient
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); OUT = os.path.join(HERE, "..")
CF = pickle.load(open(os.path.join(D, "ctx_fixed.pkl"), "rb")); S = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
X0, Y0 = S["X0"], S["Y0"]
xf = CF["xf"]; cen = np.array(xf["cen"]); t = np.array(xf["t"]); s = xf["scale"]
DX, DY = -s * cen[0] + t[0] + X0, -s * cen[1] + t[1] + Y0
print("콘타 모델 → 최종본 프레임: 원점 기준 %.4f배 축척, 회전 %.2f°, 이동 (%.2f, %.2f)" % (s, xf["theta"], DX, DY))
f = r3.File3dm(); f.Settings.ModelUnitSystem = r3.UnitSystem.Millimeters
L = r3.Layer(); L.Name = "11_주변건물(정합)"; L.Color = (200, 200, 200, 255); li = f.Layers.Add(L)
L2 = r3.Layer(); L2.Name = "11_주변건물(정합)_구역안(철거)"; L2.Color = (235, 190, 190, 255); li2 = f.Layers.Add(L2)


def pl(cs):
    pts = r3.Point3dList()
    for x, y in cs: pts.Add(x + X0, y + Y0, 0.0)
    return r3.PolylineCurve(pts)


n = 0
for o in CF["B"]:
    p = orient(o["g"].simplify(0.05), 1.0)
    e = r3.Extrusion.Create(pl(list(p.exterior.coords)), max(o["h"], 3.5), True)
    if e is None: continue
    bb = e.GetBoundingBox()
    if bb.Min.Z < -1e-6: e.Translate(r3.Vector3d(0, 0, -bb.Min.Z))
    a = r3.ObjectAttributes(); a.LayerIndex = li2 if o["inside"] else li; a.Name = "주변건물"
    a.SetUserString("높이m", "%.1f" % max(o["h"], 3.5)); a.SetUserString("출처", "최종콘타모델_v2 빌딩 → 2배·이동, V-World 연속지적(2025.01)에 정합")
    f.Objects.AddExtrusion(e, a); n += 1
path = os.path.join(OUT, "주변건물_정합_v1.3dm")
print("write", f.Write(path, 8), path, n)
