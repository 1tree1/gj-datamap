"""S5 라이노 3dm — 첨부 파일(최종콘타모델_v2_획지매스_규제미적용v1b.3dm)을 읽기만 하고, 같은 구조의 새 파일로 쓴다(첨부 파일은 수정하지 않는다).
새 파일 = 첨부 파일 전체(주변 건물·도로·고시 도면 등) + 새 안 레이어 '획지매스_TIMESTRATA_수정안v1'(첨부와 같은 번호 체계). 이전 안 레이어는 꺼 둔다.
좌표: 실측(EPSG:5187) → 5179 → 모형((X+Cc)/2, 높이/2). 첨부 파일이 반축척 모형좌표를 쓰기 때문(k11_export 와 같은 식)."""
import pickle, os, math, sys, time
import numpy as np
import rhino3dm as R
import trimesh
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
SRC = r"C:\Users\OFFICE\Desktop\9_도시\최종콘타모델_v2_획지매스_규제미적용v1b.3dm"
DST = r"C:\Users\OFFICE\Desktop\9_도시\최종콘타모델_v2_획지매스_TIMESTRATA_수정안v1.3dm"
assert os.path.abspath(SRC) != os.path.abspath(DST)
P = pickle.load(open(os.path.join(D, "design.pkl"), "rb")); REG = P["REG"]
U, LOTS, PARKS, BUILD, ROADS, COURTS, OPEN, DECKS, RAILS = P["U"], P["LOTS"], P["PARKS"], P["BUILD"], P["ROADS"], P["COURTS"], P["OPEN"], P["DECKS"], P["RAILS"]
Cc = np.array([1155149.0, 1762445.9]); tr = Transformer.from_crs(5187, 5179, always_xy=True)
def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    return [p for x in g.geoms for p in polys(x)] if hasattr(g, "geoms") else []
def M(x, y):                                  # 로컬 실측 m → 모형 좌표
    X, Y = tr.transform(x + REG["tx"], y + REG["ty"]); return ((X + Cc[0]) / 2.0, (Y + Cc[1]) / 2.0)
t0 = time.time(); f = R.File3dm.Read(SRC); print("read %.0fs objects %d layers %d" % (time.time() - t0, len(f.Objects), len(f.Layers)))
names = {i: l.FullPath for i, l in enumerate(f.Layers)}
# 이전 안 레이어는 꺼 둔다(삭제하지 않음)
OLD = "획지매스_규제미적용v1b"
for i, l in enumerate(f.Layers):
    if l.FullPath.startswith(OLD): l.Visible = False
# 기준 높이: 첨부 파일의 획지 면 z
z0 = 0.0
for o in f.Objects:
    if names.get(o.Attributes.LayerIndex, "").endswith("01 획지 면"):
        bb = o.Geometry.GetBoundingBox(); z0 = bb.Min.Z; break
print("지면 z =", z0)
PAR = "획지매스_TIMESTRATA_수정안v1"
SUB = [("00 계획경계(작업 경계 U)", (138, 43, 226)), ("01 획지 면", (221, 221, 221)), ("01 획지 경계", (85, 85, 85)), ("02 공원·광장", (127, 193, 90)),
       ("03 도로 차량·보차공존", (93, 127, 176)), ("03 도로 보행자전용(보행 우선)", (209, 73, 91)), ("04 마당·광장(획지 안)", (236, 231, 222)), ("04 중정·녹지(획지 안)", (207, 232, 179)),
       ("05 매스 상업·업무", (228, 87, 58)), ("05 매스 창조산업", (169, 139, 211)), ("05 매스 문화·교육·공공", (111, 159, 220)), ("05 매스 판매·음식", (244, 160, 194)),
       ("05 매스 여가·오락·체육", (47, 171, 157)), ("05 매스 주거", (241, 210, 71)), ("05 매스 역사유산", (201, 116, 47)), ("05 매스 교통·방문자", (198, 198, 198)),
       ("05 매스 주차전용건축물", (154, 154, 154)), ("05 매스 1층 판매·음식(저층부)", (244, 160, 194)), ("05 들어 올린 지붕(캐노피)", (191, 227, 154)),
       ("06 라벨 획지", (34, 34, 34)), ("08 공중가로·상층 데크", (63, 174, 74)), ("09 철도 흔적", (109, 106, 99))]
lay = {}
pl_ = R.Layer(); pl_.Name = PAR; pl_.Color = (90, 90, 90, 255); par_idx = f.Layers.Add(pl_); par_id = f.Layers[par_idx].Id
for nm, col in SUB:
    l = R.Layer(); l.Name = nm; l.Color = (col[0], col[1], col[2], 255); l.ParentLayerId = par_id; lay[nm] = f.Layers.Add(l)
def attr(name, li):
    a = R.ObjectAttributes(); a.LayerIndex = lay[li]; a.Name = name; return a
def pcurve(ring, z):
    return R.Polyline([R.Point3d(*M(x, y), z) for x, y in ring.coords]).ToPolylineCurve()
def surf(poly, name, li):
    n_ = 0
    for p in polys(poly):
        p = orient(p, 1.0)
        c = pcurve(p.exterior, z0)
        if len(p.interiors) == 0:
            bb = c.GetBoundingBox(); pl = R.Plane(R.Point3d(bb.Min.X, bb.Min.Y, z0), R.Vector3d(1, 0, 0), R.Vector3d(0, 1, 0))
            br = R.Brep.CreateTrimmedPlane(pl, c)
            if br is not None: f.Objects.AddBrep(br, attr(name, li)); n_ += 1; continue
        e = R.Extrusion.Create(c, 0.01, True)
        if e is None: continue
        for h in p.interiors: e.AddInnerProfile(pcurve(h, z0))
        f.Objects.AddExtrusion(e, attr(name, li)); n_ += 1
    return n_
def ext(poly, za, zb, name, li):
    n_ = 0
    for p in polys(poly):
        if p.area < 1.0: continue
        p = orient(p, 1.0); e = R.Extrusion.Create(pcurve(p.exterior, za), zb - za, True)
        if e is None: continue
        for h in p.interiors: e.AddInnerProfile(pcurve(h, za))
        f.Objects.AddExtrusion(e, attr(name, li)); n_ += 1
    return n_
cnt = {}
def cn(k, v): cnt[k] = cnt.get(k, 0) + v
f.Objects.AddCurve(pcurve(U.exterior, z0), attr("계획 경계 U", "00 계획경계(작업 경계 U)")); cn("경계", 1)
for d in LOTS:
    cn("획지면", surf(d["geom"], "%s %s" % (d["id"], d["name"]), "01 획지 면"))
    for p in polys(d["geom"]): f.Objects.AddCurve(pcurve(p.exterior, z0), attr("%s 경계" % d["id"], "01 획지 경계")); cn("획지경계", 1)
for d in PARKS: cn("공원", surf(d["geom"], "%s %s" % (d["name"], d["kind"]), "02 공원·광장"))
for k, r in ROADS.items():
    li = "03 도로 차량·보차공존" if r["grp"] == "차량" else "03 도로 보행자전용(보행 우선)"
    cn("도로", surf(r["g"], "%s %s %gm" % (r["nm"], r["kind"], r["w"]), li))
for lid, nm, g in COURTS: cn("마당", surf(g, "%s %s" % (lid, nm), "04 중정·녹지(획지 안)"))
for lid, nm, g, col in OPEN: cn("마당", surf(g, "%s %s" % (lid, nm), "04 마당·광장(획지 안)"))
Z0 = z0
for b in BUILD:
    nm = "%s | %s | %dF" % (b["lot"], b["name"], b["floors"]); fh = b["floor_h"] / 2.0; H = b["h"] / 2.0
    if b["role"] == "주차": cn("매스", ext(b["geom"], Z0, Z0 + H, nm, "05 매스 주차전용건축물")); continue
    li = "05 매스 " + b["cat"]
    if b["retail_ground"] and b["floors"] > 1:
        cn("매스", ext(b["geom"], Z0, Z0 + fh, nm + " [1층]", "05 매스 1층 판매·음식(저층부)")); cn("매스", ext(b["geom"], Z0 + fh, Z0 + H, nm + " [2층~]", li))
    else: cn("매스", ext(b["geom"], Z0, Z0 + H, nm, li))
    if b.get("lift"):
        for q in polys(b["lift"]["geom"]): cn("캐노피", ext(q, Z0 + H + b["lift"]["dz"] / 2.0, Z0 + H + (b["lift"]["dz"] + b["lift"]["th"]) / 2.0, "들어 올린 지붕 " + b["name"], "05 들어 올린 지붕(캐노피)"))
for d in LOTS:
    c = max(polys(d["geom"]), key=lambda g: g.area).representative_point(); f.Objects.AddTextDot("%d %s" % (d["no"], d["name"]), R.Point3d(*M(c.x, c.y), z0 + 1.0), attr("라벨 " + d["id"], "06 라벨 획지")); cn("라벨", 1)
def slab_mesh(quad, za, zb, th):
    """경사 데크 한 구간(사각, 시작·끝 높이 za→zb)을 닫힌 메시 입체로(모형 단위: 높이 /2)"""
    me = R.Mesh(); top = [(x, y, z) for x, y, z in quad]
    for (x, y, z) in top: mx, my = M(x, y); me.Vertices.Add(mx, my, z / 2.0 + z0)
    for (x, y, z) in top: mx, my = M(x, y); me.Vertices.Add(mx, my, (z - th) / 2.0 + z0)
    me.Faces.AddFace(0, 1, 2, 3); me.Faces.AddFace(7, 6, 5, 4)
    for i in range(4): j = (i + 1) % 4; me.Faces.AddFace(i, j, 4 + j, 4 + i)
    me.Normals.ComputeNormals(); me.Compact(); return me
for dk in DECKS:
    w = dk["w"] / 2
    for (x0, y0, za), (x1, y1, zb) in zip(dk["pts"], dk["pts"][1:]):
        dx, dy = x1 - x0, y1 - y0; Ln = math.hypot(dx, dy) or 1.0; nx, ny = -dy / Ln * w, dx / Ln * w
        quad = [(x0 + nx, y0 + ny, za), (x1 + nx, y1 + ny, zb), (x1 - nx, y1 - ny, zb), (x0 - nx, y0 - ny, za)]
        f.Objects.AddMesh(slab_mesh(quad, za, zb, 0.9), attr(dk["name"], "08 공중가로·상층 데크")); cn("데크", 1)
for r_ in RAILS:
    for ln in (r_.geoms if r_.geom_type.startswith("Multi") else [r_]):
        if ln.geom_type == "LineString" and ln.length > 1:
            f.Objects.AddCurve(R.Polyline([R.Point3d(*M(x, y), z0 + 0.05) for x, y in ln.coords]).ToPolylineCurve(), attr("레일 흔적", "09 철도 흔적")); cn("레일", 1)
print("추가:", cnt)
t1 = time.time(); ok = f.Write(DST, 8); print("write", ok, "%.0fs" % (time.time() - t1), DST, os.path.getsize(DST) if os.path.exists(DST) else None)
