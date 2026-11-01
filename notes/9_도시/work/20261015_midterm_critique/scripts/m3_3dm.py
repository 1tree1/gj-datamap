"""M3 매스 재작업 v1 → 3dm(rhino3dm) — 사용자 최종 3dm(바탕화면 구경주역_마스터플랜_최종.3dm)과 같은 좌표·단위 표기
로컬 + (X0, Y0) = (1,166,600, 1,761,100) → 최종.3dm 좌표. 단위 표기 mm(값은 m) — 중간마감 d4_3dm과 같다. 가져오기(Import)하면 그대로 겹친다.
원본 3dm은 건드리지 않는다. 출력: ../mass_v1/구경주역_매스재작업_v1.3dm"""
from k0 import *
import rhino3dm as r3
from shapely.geometry.polygon import orient
from geom2 import vault, hip_roof

VAR = os.environ.get("MASSVAR", "v1"); VDIR = {"v1": "mass_v1", "v1b": "mass_v1b"}[VAR]
MV = pickle.load(open(os.path.join(K0DIR, "..", VDIR, "data", "mass_%s.pkl" % VAR), "rb"))
S2 = MV["S"]; X0_, Y0_ = S["X0"], S["Y0"]
OUTF = os.path.join(K0DIR, "..", VDIR, {"v1": "구경주역_매스재작업_v1.3dm", "v1b": "구경주역_매스변형_v1b.3dm"}[VAR])
CORR_ = MV.get("CORR", CORR)


def hexc(h, a=255): return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), a)


f = r3.File3dm()
f.Settings.ModelUnitSystem = r3.UnitSystem.Millimeters
f.Settings.ModelAbsoluteTolerance = 0.001


def layer(name, color, parent=None):
    L = r3.Layer(); L.Name = name; L.Color = hexc(color)
    if parent is not None: L.ParentLayerId = f.Layers[parent].Id
    return f.Layers.Add(L)


ROOT = layer({"v1": "매스재작업_v1(2026-10-15)", "v1b": "매스변형_v1-b_구역사실제위치(2026-10-15)"}[VAR], "#000000")
LY = {k: layer(k, c, ROOT) for k, c in [("00_구역경계", "#d7191c"), ("01_획지", "#555555"), ("02_공원·녹지", "#4caf50"), ("03_보행(보행축·통경축)", "#9ccc65"),
                                         ("04_도로", "#9e9e9e"), ("06_건축물", "#333333"), ("07_판(①②③)", PLATC), ("08_지면요소(광장·중정·코트)", "#c8b58a"),
                                         ("09_식재", "#5a9e3a"), ("12_유리지붕(그레이트 코트)", "#7d98ab")]}
CATN = {k: v[1] for k, v in S["CATS"].items()}
BSUB = {k: layer(CATN[k], S["CATS"][k][0], LY["06_건축물"]) for k in S["CATS"]}


def attr(li, name="", color=None, us=None):
    a = r3.ObjectAttributes(); a.LayerIndex = li; a.Name = name
    if color is not None: a.ObjectColor = hexc(color); a.ColorSource = r3.ObjectColorSource.ColorFromObject
    for k, v in (us or {}).items(): a.SetUserString(str(k), str(v))
    return a


def G(x, y): return (x + X0_, y + Y0_)


def pline(coords, z=0.0):
    pts = r3.Point3dList()
    for x, y in coords: gx, gy = G(x, y); pts.Add(gx, gy, z)
    return r3.PolylineCurve(pts)


def outline(g, li, name="", us=None, z=0.0):
    for p in polys(g):
        for ring_ in [p.exterior] + list(p.interiors):
            f.Objects.AddCurve(pline(list(ring_.coords), z), attr(li, name, None, us))


def extr(p, z0, h):
    p = orient(p.simplify(0.02, preserve_topology=True), 1.0)
    e = r3.Extrusion.Create(pline(list(p.exterior.coords), 0.0), h, True)
    if e is None: return None
    if len(p.interiors):
        xf = r3.Transform.PlaneToPlane(e.GetProfilePlane(0.0), r3.Plane.WorldXY())
        for ring_ in p.interiors:
            c = pline(list(ring_.coords), 0.0); c.Transform(xf)
            e.AddInnerProfile(c)
    bb = e.GetBoundingBox()
    if bb.Min.Z < -1e-6: e.Translate(r3.Vector3d(0, 0, -bb.Min.Z))
    e.Translate(r3.Vector3d(0, 0, z0))
    return e


def solid(g, z0, z1, li, name, color, us):
    n = 0
    for p in polys(g):
        if p.area < 0.5: continue
        e = extr(p, z0, z1 - z0)
        if e is not None: f.Objects.AddExtrusion(e, attr(li, name, color, us)); n += 1
    return n


def mesh(V, F, li, name, color):
    m = r3.Mesh()
    for v in V: x, y = G(v[0], v[1]); m.Vertices.Add(x, y, v[2])
    for t in F: m.Faces.AddFace(int(t[0]), int(t[1]), int(t[2]))
    m.Normals.ComputeNormals(); m.Compact()
    f.Objects.AddMesh(m, attr(li, name, color))


outline(B, LY["00_구역경계"], "구역경계", {"면적㎡": round(B.area, 1)})
RES = {r["no"]: r for r in MV["RES"]}
for l in S2["LOTS"]:
    r = RES[l["no"]]
    outline(l["g"], LY["01_획지"], "%d %s" % (l["no"], l["name"]), {"획지번호": l["no"], "획지명": l["name"], "형태": r["form"], "면적㎡": round(r["A"], 1),
            "건축면적_지금㎡": round(r["ba0"], 1), "건축면적_목표㎡": round(r["ba_t"], 1), "건축면적_v1㎡": round(r["ba"], 1),
            "연면적_지금㎡": round(r["gfa0"], 1), "연면적_v1㎡": round(r["gfa"], 1), "건폐율_v1": round(r["ba"] / r["A"], 3), "메모": r["note"]}, 0.02)
for p in S["PARKS"]: outline(p["g"], LY["02_공원·녹지"], p["name"], {"면적㎡": round(p["g"].area, 1)})
for o in S["OPEN"]: outline(o["g"], LY["03_보행(보행축·통경축)"], o["name"], {"면적㎡": round(o["g"].area, 1)})
outline(S["PATH8"], LY["03_보행(보행축·통경축)"], "향일문 조망로 8 m", {"면적㎡": round(S["PATH8"].area, 1)})
outline(CORR_, LY["03_보행(보행축·통경축)"], "보행 통경축 20 m(A안, 옛 동서 도로)", {"면적㎡": round(CORR_.area, 1), "결정": "2026-10-15 A안 — 비상·조업 차량만 시간제"})
if "PASS" in MV: outline(MV["PASS"], LY["03_보행(보행축·통경축)"], "대합실 관통 통로(구 역사 1층, 폭 8 m, 24시간)", {"면적㎡": round(MV["PASS"].area, 1), "메모": "철도기념물(코레일) 1층 개조 — 소유자 협의 필요"})
for k, g in S2["ROADS"].items(): outline(g, LY["04_도로"], {"N": "북측 차도 13 m", "O": "동·남측 외곽도로"}.get(k, k), {"면적㎡": round(g.area, 1)})
for p in S2["PLZ"]:
    if p["kind"] != "통경축": outline(p["g"], LY["08_지면요소(광장·중정·코트)"], p["name"], {"구분": p["kind"], "면적㎡": round(p["g"].area, 1)})
nobj = 0
for b in MV["BLD"]:
    us = {"획지번호": b["lot"], "동명": b["name"], "주용도": CATN.get(b["main"], b["main"]), "층수": b["floors"], "높이m": round(b["h"], 2),
          "건축면적㎡": round(b["g"].area, 1), "연면적㎡": round(b["gfa"], 1), "구분": "v1 생성" if b.get("gen") else "중간마감 유지"}
    if b["name"] == "구 경주역사":
        memo = "계획 모델 배치 유지(2026-10-15). 상세 메쉬는 최종.3dm Layer0" if VAR == "v1" else "실제 위치(콘타 모델 빌딩·V-World 연속지적 정합, 88.7 × 24.1 m). 상세 메쉬는 최종.3dm Layer0을 이 위치로 옮겨 쓸 것"
        nobj += solid(b["g"], 0.0, 9.0, BSUB["역사"], b["name"], S["CATS"]["역사"][0], dict(us, 메모=memo))
        continue
    for (g, z0, z1, cat) in b["parts"]:
        nobj += solid(g, z0, z1, BSUB[cat], b["name"], S["CATS"][cat][0], dict(us, 부분용도=CATN.get(cat, cat), z0=round(z0, 2), z1=round(z1, 2)))
for k in MV["LINKS"]:
    nobj += solid(k["g"], k["z0"], k["z1"], LY["06_건축물"], k.get("kind", "연결 브리지"), "#55595e", {"획지번호": k["lot"]})
for d in MV["DECKS"]:
    nobj += solid(d["g"], d["z0"], d["z1"], LY["07_판(①②③)"], d["name"], PLATC, {"면적㎡": round(d["g"].area, 1), "z0": d["z0"], "z1": d["z1"], "높이": "제안값 — 허용기준 ⑤ 8 m 적용 구역 확인 필요"})
for g, top in MV["COLS"]: nobj += solid(g, 0.0, top, LY["07_판(①②③)"], "판 기둥", "#5b5b5b", {"높이m": top})
if not MV.get("NO_GLASS"):
    V, Fc = vault(S["GLASS"], 1.5); mesh(V, Fc, LY["12_유리지붕(그레이트 코트)"], "그레이트 코트 유리 지붕", "#cfe6f3")
for (x, y, r) in MV["TREES"]:
    gx, gy = G(x, y); f.Objects.AddCircle(r3.Circle(r3.Point3d(gx, gy, 0.05), float(r)), attr(LY["09_식재"], "수목"))
f.Write(OUTF, 7)
print("saved", OUTF, "objects", len(f.Objects), "solids", nobj)
