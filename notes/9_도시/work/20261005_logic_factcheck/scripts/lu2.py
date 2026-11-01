import json, io, collections, sys
exec(open("geo_check.py", encoding="utf-8").read().split("# 시설 점/폴리곤")[0])
R = r"C:\Users\OFFICE\Desktop\9_도시"
def polys_of(path, keyfn):
    d = json.load(io.open(path, encoding="utf-8"))
    out = []
    for f in d["features"]:
        g = f["geometry"]; ps = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in ps:
            rings = [[fwd(*c[:2]) for c in r_] for r_ in poly]
            xs_ = [p[0] for p in rings[0]]; ys_ = [p[1] for p in rings[0]]
            out.append((min(xs_), max(xs_), min(ys_), max(ys_), rings, keyfn(f["properties"])))
    return out
def hit(p, polys):
    for a, b, c, d, rings, k in polys:
        if a <= p[0] <= b and c <= p[1] <= d and inside(p, rings[0]) and not any(inside(p, h) for h in rings[1:]):
            return k
    return None
uq = polys_of(R + r"\archive\C_data\raw\vworld_uq111.geojson", lambda p: p.get("uname") or p.get("UNAME") or str(p)[:40])
godo = polys_of(R + r"\archive\C_data\raw\vworld_uq123_godo.geojson", lambda p: (p.get("uname") or p.get("dgm_nm") or str(p)[:60]))
print("UQ111 polys", len(uq), "godo polys", len(godo), "sample godo prop keys", )
gd = json.load(io.open(R + r"\archive\C_data\raw\vworld_uq123_godo.geojson", encoding="utf-8"))["features"][0]["properties"]
print(gd)
STEP = 5.0
cz = collections.Counter(); cg = collections.Counter(); tot = 0
x = min(xs)
while x < max(xs):
    y = min(ys)
    while y < max(ys):
        p = (x + STEP / 2, y + STEP / 2)
        if inside(p, ring):
            tot += 1
            cz[hit(p, uq) or "미분류"] += 1
            cg[hit(p, godo) or "고도지구 밖"] += 1
        y += STEP
    x += STEP
A = STEP * STEP
print("용도지역(UQ111, 현재 경계 218,478㎡):")
for k, v in cz.most_common(): print("  %-14s %8.0f ㎡ %5.1f%%" % (k, v * A, 100 * v / tot))
print("고도지구(UQ123):")
for k, v in cg.most_common(): print("  %-24s %8.0f ㎡ %5.1f%%" % (k, v * A, 100 * v / tot))
