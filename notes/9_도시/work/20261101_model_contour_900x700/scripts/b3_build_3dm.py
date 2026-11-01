# 라이노(run_python) 안에서 실행: plan2d.json → 레이어 구분된 모형용 3dm(File3dm, 사용자 문서는 건드리지 않음)
import json
import time
import System
import Rhino
G = Rhino.Geometry

W = r"C:\Users\OFFICE\Desktop\9_도시\work\20261101_model_contour_900x700"
OUT = W + r"\모형용콘타_900x700_v4.3dm"
d = json.load(open(W + r"\data\plan2d.json", encoding="utf-8"))
TOL = 0.001
t0 = time.time()

# ---- 높이(mm)
Z_BASE, Z_FOAM, PAPER_T = 5.0, 7.0, 0.2
Z_PAPER = Z_FOAM + PAPER_T          # 7.2  색지 윗면 = 도로면
Z_SW = Z_PAPER + 0.5                # 7.7  출력 인도 윗면(두께 0.5) — 사용자 지시: 인도·대지 같은 레벨
Z_LAND = Z_SW                       # 7.7  출력 대지 윗면(두께 0.5)
MIN_BLD_VOL = 40.377                # 사용자 지시: 기준 건물(1층, 바닥 약 22 m²)보다 작은 건물 제외
OLD_EMBED = 1.8                     # 기준 부피는 옛 높이(대지 1.8 mm 매몰 포함)로 잰 값
DECK_T = 0.8                        # 다리 상판 두께(색지 밑)

f3 = Rhino.FileIO.File3dm()
f3.Settings.ModelUnitSystem = Rhino.UnitSystem.Millimeters
f3.Settings.ModelAbsoluteTolerance = 0.01
LAY = {}


def layer(path, rgb):
    if path in LAY:
        return LAY[path]
    parts = path.split("::")
    parent = layer("::".join(parts[:-1]), (120, 120, 120)) if len(parts) > 1 else None
    L = Rhino.DocObjects.Layer()
    L.Name = parts[-1]
    L.Color = System.Drawing.Color.FromArgb(*rgb)
    if parent is not None:
        L.ParentLayerId = f3.AllLayers.FindIndex(parent).Id
    f3.AllLayers.Add(L)
    idx = len(list(f3.AllLayers)) - 1
    LAY[path] = idx
    return idx


def attr(path, rgb, name=None):
    a = Rhino.DocObjects.ObjectAttributes()
    a.LayerIndex = layer(path, rgb)
    if name:
        a.Name = name
    return a


def ring(pts, z):
    out = []
    for x, y in pts:
        if out and abs(out[-1][0] - x) < 2e-3 and abs(out[-1][1] - y) < 2e-3:      # 0.002 mm(실제 3 mm) 이내 중복점 제거
            continue
        out.append((x, y))
    while len(out) > 2 and abs(out[0][0] - out[-1][0]) < 2e-3 and abs(out[0][1] - out[-1][1]) < 2e-3:
        out.pop()
    return G.PolylineCurve([G.Point3d(x, y, z) for x, y in out + [out[0]]])


def slab(p, z0, z1):
    fb = G.Brep.CreatePlanarBreps([ring(p["ext"], z0)], TOL)
    if not fb:
        return None
    fb = fb[0]
    for h in p["holes"]:
        fb.Loops.AddPlanarFaceLoop(0, G.BrepLoopType.Inner, [ring(h, z0)])
    fb.Compact()
    s = fb.Faces[0].CreateExtrusion(G.LineCurve(G.Point3d(0, 0, 0), G.Point3d(0, 0, z1 - z0)), True)
    if s is None or not s.IsSolid:
        return None
    if s.SolidOrientation == G.BrepSolidOrientation.Inward:
        s.Flip()
    return s


stat = {}
fail = []


def add_slab(p, z0, z1, path, rgb, name=None):
    s = slab(p, z0, z1)
    if s is None:
        fail.append((path, name)); return
    f3.Objects.AddBrep(s, attr(path, rgb, name))
    stat[path] = stat.get(path, 0) + 1


def add_outline(p, z, path, rgb, name=None):
    for r in [p["ext"]] + p["holes"]:
        f3.Objects.AddCurve(ring(r, z), attr(path, rgb, name))
    stat[path] = stat.get(path, 0) + 1


def add_line(pts, z, path, rgb):
    f3.Objects.AddCurve(G.PolylineCurve([G.Point3d(x, y, z) for x, y in pts]), attr(path, rgb))
    stat[path] = stat.get(path, 0) + 1


# ---- 00 기준
C_REF = (200, 30, 30)
add_outline(d["frame"], 0.0, u"00_기준::프레임_700x900", (0, 0, 0))
add_outline(d["site"], Z_PAPER, u"00_기준::최종대지경계선", C_REF)
# ---- 01 우드락 5t
add_slab(d["frame"], 0.0, Z_BASE, u"01_우드락5t_바닥", (235, 235, 230))
add_outline(d["frame"], Z_BASE, u"01_우드락5t_바닥::재단선", (0, 0, 0))
# ---- 02 우드락 2t (하천 + 다리 밑 따냄)
for p in d["foam2"]:
    add_slab(p, Z_BASE, Z_FOAM, u"02_우드락2t_하천따냄", (210, 210, 205))
    add_outline(p, Z_FOAM, u"02_우드락2t_하천따냄::재단선", (0, 0, 0))
# ---- 03 색지 (하천 따냄, 다리 상판은 남김) + 각인
for p in d["paper"]:
    add_slab(p, Z_FOAM, Z_PAPER, u"03_색지_하천따냄", (190, 185, 175))
    add_outline(p, Z_PAPER, u"03_색지_하천따냄::재단선", (0, 0, 0))
C_ENG = (60, 60, 60)
for p in d["print_outline"]:
    add_outline(p, Z_PAPER, u"03_색지_하천따냄::각인_대지선(출력 배치선)", C_ENG)
for b in d["bridge_models"]:
    path = u"03_색지_하천따냄::각인_철교" if u"철교" in b["name"] else u"03_색지_하천따냄::각인_다리"
    for p in b["plan"]:
        add_outline(p, Z_PAPER, path, C_ENG, b["name"])
mk = json.load(open(W + r"\data\markings.json", encoding="utf-8"))
E = u"03_색지_하천따냄::"
for c in mk["center_lines"]:
    add_line(c["pts"], Z_PAPER, E + u"각인_도로중앙선(황색)", (230, 180, 0))
for l in mk["lane_lines"]:
    add_line(l["pts"], Z_PAPER, E + (u"각인_차선(백색 실선)" if l["solid"] else u"각인_차선(백색 점선 3-5m)"), (255, 255, 255))
for cw in mk["crosswalks"]:
    path = E + (u"각인_횡단보도(항공사진 확인)" if cw["how"] == u"영상 확인" else u"각인_횡단보도(규칙 배치)")
    for st in cw["stripes"]:
        f3.Objects.AddCurve(ring(st[:-1], Z_PAPER), attr(path, (255, 255, 255)))
    stat[path] = stat.get(path, 0) + 1
for sp in mk["stop_lines"]:
    f3.Objects.AddCurve(ring(sp[:-1], Z_PAPER), attr(E + u"각인_정지선", (255, 255, 255)))
    stat[E + u"각인_정지선"] = stat.get(E + u"각인_정지선", 0) + 1
for a in mk["arrows"]:
    f3.Objects.AddCurve(ring(a["pts"][:-1], Z_PAPER), attr(E + u"각인_진행방향 화살표(규칙 배치)", (255, 255, 255), a["kind"]))
    stat[E + u"각인_진행방향 화살표(규칙 배치)"] = stat.get(E + u"각인_진행방향 화살표(규칙 배치)", 0) + 1
for isl in mk["islands"]:
    f3.Objects.AddCurve(ring(isl["outline"][:-1], Z_PAPER), attr(E + u"각인_교통섬(도류화 빗금)", (255, 255, 255)))
    for h in isl["hatch"]:
        add_line(h, Z_PAPER, E + u"각인_교통섬(도류화 빗금)", (255, 255, 255))
add_outline(d["site"], Z_PAPER, u"03_색지_하천따냄::각인_최종대지경계", C_REF)
# ---- 04 3D 출력(일괄): 대지·인도 0.5(같은 레벨) + 건물(대지 속까지 묻어 한 덩어리로 출력)
def ring_area(pts):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2.0


def old_volume(b):
    a = ring_area(b["poly"]["ext"]) - sum(ring_area(h) for h in b["poly"]["holes"])
    return a * (OLD_EMBED + b["h"])


for p in d["land"]:
    add_slab(p, Z_PAPER, Z_LAND, u"04_3D출력_일괄::대지(0.5mm)", (120, 170, 90))
for p in d["sidewalk"]:
    add_slab(p, Z_PAPER, Z_SW, u"04_3D출력_일괄::인도(0.5mm)", (220, 190, 90))
for b in d["buildings"]["bld"] + d["buildings"]["thin"]:
    if old_volume(b) < MIN_BLD_VOL:
        stat[u"작은 건물 제외"] = stat.get(u"작은 건물 제외", 0) + 1
        continue
    add_slab(b["poly"], Z_PAPER, Z_LAND + b["h"], u"04_3D출력_일괄::건물", (200, 120, 80))
# ---- 06 중요거점(별도 출력, 대지 윗면에 올림)
for k, v in d["buildings"].items():
    if not k.startswith("key:"):
        continue
    name = k[4:]
    for b in v:
        add_slab(b["poly"], Z_LAND, Z_LAND + b["h"], u"06_중요거점::" + name, (214, 40, 40), name)
# ---- 07 다리(상판은 색지 밑, 교각은 하천 바닥까지)
for b in d["bridge_models"]:
    path = u"07_다리::" + b["name"]
    for p in b["deck"]:
        add_slab(p, Z_FOAM - DECK_T, Z_FOAM, path, (160, 160, 165), b["name"] + u" 상판")
    for p in b["piers"]:
        add_slab(p, Z_BASE, Z_FOAM - DECK_T, path, (110, 110, 115), b["name"] + u" 교각")
# ---- 99 참고
for p in d["river"]:
    add_outline(p, Z_BASE, u"99_참고::하천 윤곽", (60, 130, 220))

f3.Notes.Notes = (u"모형용 콘타 900x700(실제 700x900 세로), 1:1500, 단위 mm\n"
                  u"높이: 우드락5t 0-5 / 우드락2t 5-7(하천·다리밑 따냄) / 색지 7-7.2(하천 따냄) / "
                  u"출력 대지·인도 7.2-7.7(같은 레벨, 두께 0.5, 인도는 경계석 없이 원래 라인) / 건물 7.2-(7.7+높이), 기준 부피 40.377 미만 제외 / 중요거점 7.7-(7.7+높이)\n"
                  u"다리 상판 6.2-7.0(색지 밑), 교각 5.0-6.2. 다리 폭·교각 간격·성벽 치수는 가정값.\n"
                  u"노면표시: 수치지형도 2025 도로중심선 속성 + 2025 정사영상·항공사진 검출(c2_markings.py). 규칙 배치 레이어는 영상 미확인.\n"
                  u"스크립트: work/20261101_model_contour_900x700/scripts")
ok = f3.Write(OUT, 8)
print("write", ok, OUT, "%.1fs" % (time.time() - t0))
for k in sorted(stat):
    print(k, stat[k])
print("fail", len(fail), fail[:10])
