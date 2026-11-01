"""순수 파이썬 지오메트리 점검 (pyproj/shapely 없음).
- EPSG:5187 (Korea 2000 / East Belt: lon0=129, lat0=38, k0=1, FE=200000, FN=500000, GRS80) 정변환을 직접 구현
- 사용자 경계(5187)의 면적·범위·중심, 황성공원·대릉원·성동시장·황리단길 등까지의 거리
"""
import json, math, io, sys

A = 6378137.0
F = 1 / 298.257222101
E2 = F * (2 - F)
EP2 = E2 / (1 - E2)
LON0 = math.radians(129.0)
LAT0 = math.radians(38.0)
K0 = 1.0
FE, FN = 200000.0, 600000.0


def mer_arc(phi):
    e2 = E2
    return A * ((1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256) * phi
                - (3 * e2 / 8 + 3 * e2 ** 2 / 32 + 45 * e2 ** 3 / 1024) * math.sin(2 * phi)
                + (15 * e2 ** 2 / 256 + 45 * e2 ** 3 / 1024) * math.sin(4 * phi)
                - (35 * e2 ** 3 / 3072) * math.sin(6 * phi))


M0 = mer_arc(LAT0)


def fwd(lon, lat):
    phi = math.radians(lat)
    lam = math.radians(lon)
    N = A / math.sqrt(1 - E2 * math.sin(phi) ** 2)
    T = math.tan(phi) ** 2
    C = EP2 * math.cos(phi) ** 2
    Aa = (lam - LON0) * math.cos(phi)
    M = mer_arc(phi)
    x = FE + K0 * N * (Aa + (1 - T + C) * Aa ** 3 / 6 + (5 - 18 * T + T ** 2 + 72 * C - 58 * EP2) * Aa ** 5 / 120)
    y = FN + K0 * (M - M0 + N * math.tan(phi) * (Aa ** 2 / 2 + (5 - T + 9 * C + 4 * C ** 2) * Aa ** 4 / 24
                                                   + (61 - 58 * T + T ** 2 + 600 * C - 330 * EP2) * Aa ** 6 / 720))
    return x, y


def area(ring):
    s = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def centroid(ring):
    a = 0.0; cx = 0.0; cy = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        c = x1 * y2 - x2 * y1
        a += c; cx += (x1 + x2) * c; cy += (y1 + y2) * c
    a /= 2
    return cx / (6 * a), cy / (6 * a)


def seg_dist(p, a, b):
    px, py = p; ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    t = 0 if dx == dy == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def dist_to_ring(p, ring):
    return min(seg_dist(p, a, b) for a, b in zip(ring, ring[1:] + ring[:1]))


def inside(p, ring):
    x, y = p; c = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


R = r"C:\Users\OFFICE\Desktop\9_도시"
U = json.load(io.open(R + r"\work\20261005_boundary_check\user_boundary_current_5187.geojson", encoding="utf-8"))
ring = [tuple(p) for p in U["features"][0]["geometry"]["coordinates"][0]][:-1]
cx, cy = centroid(ring)
xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
print("U area(shoelace) = %.0f m2, bbox x %.0f~%.0f (%.0f m) y %.0f~%.0f (%.0f m), centroid (%.0f, %.0f)" % (
    area(ring), min(xs), max(xs), max(xs) - min(xs), min(ys), max(ys), max(ys) - min(ys), cx, cy))
# 폭 프로파일: y 구간별 동서 폭(경계 수평 교차)
def width_at(y):
    xsx = []
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y):
            xsx.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    xsx.sort()
    return sum(xsx[i + 1] - xsx[i] for i in range(0, len(xsx) - 1, 2)) if len(xsx) >= 2 else 0
print("동서 폭(m) y별:", {int(y): round(width_at(y)) for y in range(int(min(ys)) + 20, int(max(ys)), 60)})

# 사이트 중심(데이터맵) 변환 검증
sx, sy = fwd(129.21892, 35.84584)
print("SITE 중심(129.21892,35.84584) -> 5187 (%.0f, %.0f); U centroid 대비 %.0f m" % (sx, sy, math.hypot(sx - cx, sy - cy)))

# 시설 점/폴리곤
def load(p):
    return json.load(io.open(R + p, encoding="utf-8"))

def conv_geom(g):
    t = g["type"]
    if t == "Point":
        return [fwd(*g["coordinates"][:2])]
    if t == "Polygon":
        return [[fwd(*c[:2]) for c in g["coordinates"][0]]]
    if t == "MultiPolygon":
        return [[fwd(*c[:2]) for c in poly[0]] for poly in g["coordinates"]]
    return []

for fn in ["parks_upis_4326", "heritage_pts_4326", "tourism_complex_4326", "rail_stations_4326"]:
    try:
        d = load(r"\archive\C_data\processed\%s.geojson" % fn)
    except Exception as e:
        print(fn, "load fail", e); continue
    print("==", fn, len(d["features"]), "features; props sample:", list(d["features"][0]["properties"].keys())[:12])

print("\n--- 거리 점검 (5187, FN=600000) ---")
cx2, cy2 = cx, cy
def report(name, geoms):
    best = None
    for g in geoms:
        if len(g) == 1 and not isinstance(g[0][0], tuple):  # point
            pass
    return

parks = load(r"\archive\C_data\processed\parks_upis_4326.geojson")["features"]
names = sorted({(f["properties"].get("dgm_nm") or "") for f in parks})
print("공원 이름 샘플:", [n for n in names if n][:60])
for f in parks:
    nm = f["properties"].get("dgm_nm") or ""
    if "황성" in nm or "북천" in nm or "봉황" in nm or "대릉" in nm or "월성" in nm:
        polys = conv_geom(f["geometry"])
        for r_ in polys:
            if len(r_) < 3: continue
            d_edge = dist_to_ring(r_[0], ring)  # 임시
            # 경계 간 최소거리(꼭짓점 기준 근사)
            dmin = min(min(dist_to_ring(p, ring) for p in r_), min(dist_to_ring(p, r_) for p in ring))
            print("  %s: 면적 %.0f㎡ (%s) 중심거리 %.0f m | 사용자경계까지 최소거리(근사) %.0f m" % (nm, area(r_), f["properties"].get("dgm_ar"), math.hypot(centroid(r_)[0]-cx, centroid(r_)[1]-cy), dmin))
her = load(r"\archive\C_data\processed\heritage_pts_4326.geojson")["features"]
for f in her:
    x, y = fwd(*f["geometry"]["coordinates"][:2])
    p = (x, y)
    print("  유적점 %s (%s): 경계 %s, 경계까지 %.0f m" % (f["properties"]["name"], f["properties"]["kind"], "안" if inside(p, ring) else "밖", dist_to_ring(p, ring)))
tc = load(r"\archive\C_data\processed\tourism_complex_4326.geojson")["features"]
print("  관광단지:", [(f["properties"]["name"], f["properties"]["area_ha"]) for f in tc])

print("\n--- 공원 폴리곤 (사용자 경계까지 최소거리 순, 상위 + 큰 면적) ---")
rows = []
for f in parks:
    p = f["properties"]
    for r_ in conv_geom(f["geometry"]):
        if len(r_) < 3: continue
        dmin = min(min(dist_to_ring(q, ring) for q in r_), min(dist_to_ring(q, r_) for q in ring))
        c = centroid(r_)
        rows.append((dmin, p.get("dgm_nm"), p.get("dgm_ar"), area(r_), p.get("mls_nam") or p.get("lcl_nam"), c))
rows.sort()
for r_ in rows[:14]:
    print("  d=%5.0f m  %s  고시면적 %s  도형 %.0f㎡  %s  중심(%.0f,%.0f)" % (r_[0], r_[1], r_[2], r_[3], r_[4], r_[5][0], r_[5][1]))
big = [r_ for r_ in rows if r_[3] > 400000]
print("대형(>40만㎡):", [(r_[1], round(r_[3]), "d=%.0f" % r_[0], "중심(%.0f,%.0f)" % r_[5]) for r_ in big])

print("\n--- 3구역(31.5/37.1/31.5%)을 실제 경계에 비례 적용 ---")
step = 1.0
ycur = min(ys); cum = 0.0; cuts = {}
targets = {"S|C": 0.3147 * area(ring), "C|N": (0.3147 + 0.3706) * area(ring)}
total = area(ring)
prev_w = 0
y = min(ys)
while y < max(ys):
    w = width_at(y + step / 2)
    cum += w * step
    for k, t in targets.items():
        if k not in cuts and cum >= t:
            cuts[k] = y + step
    y += step
print("누적 면적 %.0f (경계 %.0f)" % (cum, total))
print("컷 y: ", {k: round(v) for k, v in cuts.items()}, " → 남 %.0fm / 중 %.0fm / 북 %.0fm (남북 길이)" % (cuts["S|C"] - min(ys), cuts["C|N"] - cuts["S|C"], max(ys) - cuts["C|N"]))
print("비례 적용 면적: 남 %.0f / 중 %.0f / 북 %.0f ㎡ (합 %.0f)" % (0.3147 * total, 0.3706 * total, 0.3147 * total, total))
# 구 경주역·화랑로·광장·육교·시청 y 위치
for nm, yy in [("구 역사(현위치) y 360,745~360,833", 360789), ("화랑로 y 360,806", 360806), ("육교 y 360,996", 360996), ("v2 광장 y 360,910~361,010", 360960), ("v2 시청 y 361,020~361,244", 361132), ("C축(원화로309번길) y 361,250", 361250)]:
    zone = "남" if yy < cuts["S|C"] else ("중" if yy < cuts["C|N"] else "북")
    print("  %-34s → %s구역" % (nm, zone))
# 반경 내 지표: 부지 중심에서 성동시장/황리단길 방향은 기록값 사용
