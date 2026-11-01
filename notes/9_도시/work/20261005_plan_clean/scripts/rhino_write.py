# -*- coding: utf-8 -*-
"""rhino_write — Rhino(Python 3, run_python 안에서 exec)용. 원본 v2 3dm을 읽어 새 파일로 복사하고 plan_rhino_clean.json 의 레이어·객체를 얹어 쓴다.
원본은 건드리지 않는다(DST 는 새 경로)."""
import json, time, System, Rhino
from Rhino.FileIO import File3dm
from Rhino.Geometry import Point3d, Polyline, Brep, Extrusion, Curve, AreaMassProperties
from Rhino.DocObjects import ObjectAttributes, ObjectColorSource
import System.Drawing as SD
from System.Collections.Generic import List

SRC = r"C:\Users\OFFICE\Desktop\9_도시\최종콘타모델_v2.3dm"
DST = r"C:\Users\OFFICE\Desktop\9_도시\최종콘타모델_v2_획지매스_규제미적용v1b.3dm"      # v1(생성 매스 그대로)은 그대로 두고, Plot 15 구 역사 매스를 기존 건물 형상으로 바꾼 v1b 를 새로 쓴다
JS = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean\model\plan_rhino_clean.json"
U_AREA_REAL = 218478.07          # 계획 경계 U(㎡, 실좌표)
TOL = 0.001
t0 = time.time(); log = []
data = json.load(open(JS, encoding="utf-8"))
f = File3dm.Read(SRC)
log.append("read %.1fs objects %d layers %d" % (time.time() - t0, f.Objects.Count, f.AllLayers.Count))

# ── 원본의 경계선 확인 ──
names = {}
for l in f.AllLayers: names[l.Index] = l.FullPath
bnd = None
for o in f.Objects:
    if names.get(o.Attributes.LayerIndex, "").endswith("내가 하고자하는 경계라인") and isinstance(o.Geometry, Curve): bnd = o.Geometry
if bnd is not None:
    am = AreaMassProperties.Compute(bnd)
    log.append("경계선 면적(모형) %.1f → 실 %.1f㎡ (U %.1f, 차 %.1f)" % (am.Area, am.Area * 4.0, U_AREA_REAL, am.Area * 4.0 - U_AREA_REAL))
else:
    log.append("경계선 레이어를 찾지 못함")

def hexcol(h): return SD.Color.FromArgb(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))
pidx = f.AllLayers.AddLayer(data["parent"], SD.Color.FromArgb(90, 90, 90)); parent = f.AllLayers.FindIndex(pidx)
lay = {}
for name, col in data["layers"].items():
    idx = f.AllLayers.AddLayer(name, hexcol(col)); L = f.AllLayers.FindIndex(idx); L.ParentLayerId = parent.Id; lay[name] = idx

def pcurve(ring):
    pl = Polyline()
    for x, y, z in ring: pl.Add(Point3d(x, y, z))
    return pl.ToPolylineCurve()
def attr_of(it):
    a = ObjectAttributes(); a.Name = it["name"]; a.LayerIndex = lay[it["layer"]]
    for k, v in (it.get("strings") or {}).items(): a.SetUserString(k, v)
    if it.get("color"):
        a.ObjectColor = SD.Color.FromArgb(it["color"][0], it["color"][1], it["color"][2]); a.ColorSource = ObjectColorSource.ColorFromObject
    return a
n = {"surf": 0, "curve": 0, "ext": 0, "dot": 0, "point": 0}; fail = []
for it in data["items"]:
    try:
        k = it["kind"]; a = attr_of(it)
        if k == "surf":
            cs = List[Curve](); cs.Add(pcurve(it["ring"]))
            for h in it.get("holes") or []: cs.Add(pcurve(h))
            bs = Brep.CreatePlanarBreps(cs, TOL)
            if bs is None or len(bs) == 0: fail.append(it["name"]); continue
            for b in bs: f.Objects.AddBrep(b, a)
        elif k == "curve":
            f.Objects.AddCurve(pcurve(it["ring"]), a)
        elif k == "ext":
            e = Extrusion.Create(pcurve(it["ring"]), it["h"], True)
            if e is None: fail.append(it["name"]); continue
            for h in it.get("holes") or []: e.AddInnerProfile(pcurve(h))
            f.Objects.AddBrep(e.ToBrep(True), a)
        elif k == "dot":
            f.Objects.AddTextDot(it["text"], Point3d(*it["pos"]), a)
        elif k == "point":
            f.Objects.AddPoint(Point3d(*it["pos"]), a)
        n[k] += 1
    except Exception as ex:
        fail.append("%s: %s" % (it.get("name"), ex))
log.append("추가: %s  실패 %d %s" % (n, len(fail), fail[:8]))
try: f.Notes.Notes = "획지·매스 규제 미적용 v1b (2026-10-05). Plot 15 구 역사 매스를 기존 건물 형상(NGII 1,404㎡ 2F)으로 교체. 고도제한·용도지역·보존지역 허용기준 미반영 개념안. 레이어 '%s' 아래." % data["parent"]
except Exception: pass
t1 = time.time(); ok = f.Write(DST, 8)
log.append("write %s %.1fs → %s" % (ok, time.time() - t1, DST))
print("\n".join(log))
