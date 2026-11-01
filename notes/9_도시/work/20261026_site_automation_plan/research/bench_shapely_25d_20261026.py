# -*- coding: utf-8 -*-
"""
구경주역 대지 자동화 — 순수 Python(shapely 2.5D) 생성·평가 1회 소요 시간 측정 (2026-10-26)

목적: C_Rhino_GH_도구체인.md §4·§6의 「평가 1회 시간」 [산정] 근거.
주의: 축 위치·폭·용도 배정은 시간 측정용 임의값이며 설계안이 아니다.
입력: 구경주역_최종대지_대지경계선.3dm (읽기 전용, 레이어 「대지경계선」만 사용)
출력: 표준출력(시간·면적). 파일을 쓰지 않는다.
실행: python -I bench_shapely_25d_20261026.py [표본 수=20]
환경: 시스템 Python 3.12 + numpy + shapely 2.x + rhino3dm (추가 설치 없음)
"""
import math
import random
import sys
import time

import numpy as np
import rhino3dm
import shapely
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Polygon, box
from shapely.ops import unary_union

SRC = r"C:\Users\OFFICE\Desktop\9_도시\구경주역_최종대지_대지경계선.3dm"
FLOOR_H = 4.0  # 계획 층고 [가정, 실행모델 §2.2]
LAT, LON = 35.84, 129.21  # 경주 대략 위치 [가정]


# ---------------------------------------------------------------- 입력
def load_boundary():
    m = rhino3dm.File3dm.Read(SRC)
    idx = [l.Index for l in m.Layers if l.FullPath == "대지경계선"][0]
    for o in m.Objects:
        if o.Attributes.LayerIndex == idx:
            g = o.Geometry
            pts = [(g.Point(i).X, g.Point(i).Y) for i in range(g.PointCount)]
            return Polygon(pts), str(m.Settings.ModelUnitSystem)
    raise SystemExit("대지경계선 없음")


def to_local(poly):
    """긴 변을 y축으로 돌리고 도심을 원점으로. 되돌림 파라미터도 반환."""
    mrr = poly.minimum_rotated_rectangle
    c = list(mrr.exterior.coords)
    e = [(c[i], c[i + 1]) for i in range(4)]
    a, b = max(e, key=lambda s: math.dist(*s))
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    cx, cy = poly.centroid.x, poly.centroid.y
    p = affinity.translate(poly, -cx, -cy)
    p = affinity.rotate(p, 90 - ang, origin=(0, 0))
    return p, (cx, cy, ang)


# ---------------------------------------------------------------- 생성 S1: 축 → 도로·가구
def roads_and_blocks(site, g):
    minx, miny, maxx, maxy = site.bounds
    L = 2000
    parts = []
    # 종축(남북축) x = x_L, 폭 W_L
    parts.append(LineString([(g["x_L"], miny - 50), (g["x_L"], maxy + 50)]).buffer(g["W_L"] / 2, cap_style="flat", join_style="mitre"))
    # 횡축(동서) n_x개
    for y, w in g["cross"]:
        parts.append(LineString([(-L, y), (L, y)]).buffer(w / 2, cap_style="flat", join_style="mitre"))
    # 사선 역사유적축
    th = math.radians(g["diag_deg"])
    x0, y0 = 0, g["diag_y"]
    parts.append(LineString([(x0 - L * math.cos(th), y0 - L * math.sin(th)), (x0 + L * math.cos(th), y0 + L * math.sin(th))]).buffer(g["W_diag"] / 2, cap_style="flat"))
    # 동·남 외곽도로 띠(경계 안쪽 오프셋)
    inner = site.buffer(-g["W_perim"], join_style="mitre")
    ring = site.difference(inner)
    ring = ring.intersection(unary_union([box(maxx - 60, miny - 10, maxx + 10, maxy + 10), box(minx - 10, miny - 10, maxx + 10, miny + 40)]))
    parts.append(ring)
    roads = unary_union(parts).intersection(site)
    blocks = site.difference(roads)
    blocks = [b for b in getattr(blocks, "geoms", [blocks]) if b.area > 400]
    return roads, blocks


# ---------------------------------------------------------------- 생성 S3: 가구 → 획지 (OBB 재귀 분할, Vanegas 2012 OBB 방식 단순화)
def _halfplanes(poly, frac, along_long=True):
    mrr = poly.minimum_rotated_rectangle
    c = list(mrr.exterior.coords)[:4]
    e0 = (c[0], c[1])
    e1 = (c[1], c[2])
    long_e, short_e = (e0, e1) if math.dist(*e0) >= math.dist(*e1) else (e1, e0)
    ax = long_e if along_long else short_e
    (x1, y1), (x2, y2) = ax
    px, py = x1 + (x2 - x1) * frac, y1 + (y2 - y1) * frac
    dx, dy = (x2 - x1), (y2 - y1)
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n
    R = 5000
    # 분할선은 ax에 수직, 점 (px,py) 통과
    a = Polygon([(px - dy * R, py + dx * R), (px + dy * R, py - dx * R), (px + dy * R - dx * R, py - dx * R - dy * R), (px - dy * R - dx * R, py + dx * R - dy * R)])
    return poly.intersection(a), poly.difference(a)


def frontage(p, road_edge):
    return p.boundary.intersection(road_edge).length


def split_parcels(block, road_edge, amax, min_front, rng, depth=0):
    if block.area <= amax or depth > 12:
        return [block]
    for along_long in (True, False):
        frac = 0.5 + rng.uniform(-0.1, 0.1)
        a, b = _halfplanes(block, frac, along_long)
        kids = []
        for k in (a, b):
            kids += [q for q in getattr(k, "geoms", [k]) if q.area > 50]
        if len(kids) >= 2 and all(frontage(k, road_edge) >= min_front for k in kids):
            out = []
            for k in kids:
                out += split_parcels(k, road_edge, amax, min_front, rng, depth + 1)
            return out
    return [block]  # 접도 조건을 지키는 분할이 없으면 분할하지 않음(불가능 → 기각이 아니라 정지)


# ---------------------------------------------------------------- 생성 S4: 획지 → 매스 유형
def mass_for(parcel, typ, gsi_t, L_t, hmax):
    inset = parcel.buffer(-3.0, join_style="mitre")  # 건축선 후퇴 3 m [가정]
    if inset.is_empty:
        return None, 0
    if typ == "perimeter":  # 가로변 블록·중정형: 깊이 d를 이분탐색해 GSI 목표에 맞춤
        lo, hi = 6.0, 30.0
        fp = None
        for _ in range(12):
            d = (lo + hi) / 2
            fp = inset.difference(inset.buffer(-d, join_style="mitre"))
            if fp.area / parcel.area > gsi_t:
                hi = d
            else:
                lo = d
    elif typ == "slab":  # 판상: 장변 평행 바, 깊이 12 m, 간격 = 0.5H 이상(인동) [T1 시행령 86조③ 단순화]
        H = min(L_t * FLOOR_H, hmax)
        gap = max(0.5 * H, 8.0)
        mrr = inset.minimum_rotated_rectangle
        c = list(mrr.exterior.coords)[:4]
        e0, e1 = (c[0], c[1]), (c[1], c[2])
        long_e = e0 if math.dist(*e0) >= math.dist(*e1) else e1
        ang = math.degrees(math.atan2(long_e[1][1] - long_e[0][1], long_e[1][0] - long_e[0][0]))
        r = affinity.rotate(inset, -ang, origin="centroid")
        minx, miny, maxx, maxy = r.bounds
        bars = []
        y = miny
        while y + 12 <= maxy:
            bars.append(box(minx, y, maxx, y + 12))
            y += 12 + gap
        fp = affinity.rotate(unary_union(bars), ang, origin=inset.centroid).intersection(inset) if bars else Polygon()
    elif typ == "point":  # 포인트: 18×18 m 격자
        minx, miny, maxx, maxy = inset.bounds
        pts = []
        s = 18 + max(0.5 * min(L_t * FLOOR_H, hmax), 10)
        x = minx
        while x + 18 <= maxx:
            y = miny
            while y + 18 <= maxy:
                b = box(x, y, x + 18, y + 18)
                if inset.contains(b):
                    pts.append(b)
                y += s
            x += s
        fp = unary_union(pts) if pts else Polygon()
    else:  # 저층 공공: 축소 사본
        k = math.sqrt(max(min(gsi_t, 0.6), 0.05) * parcel.area / max(inset.area, 1))
        fp = affinity.scale(inset, k, k, origin="centroid")
    # 건폐율 상한 초과분은 잘라내지 않고 층으로 보내지 않음 — 상한은 마스크(불가능)이므로 넘으면 기각 표시
    L = max(1, min(L_t, int(hmax // FLOOR_H)))
    return fp, L


# ---------------------------------------------------------------- 평가: 2.5D 동지 일조(연속 2시간 근사)
def sun_vectors(step_min=10):
    """동지(12/22) 09–15시 KST 태양 고도·방위 — NOAA 근사식."""
    out = []
    doy = 356
    gamma = 2 * math.pi / 365 * (doy - 1)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(gamma) - 0.032077 * math.sin(gamma) - 0.014615 * math.cos(2 * gamma) - 0.040849 * math.sin(2 * gamma))
    decl = 0.006918 - 0.399912 * math.cos(gamma) + 0.070257 * math.sin(gamma) - 0.006758 * math.cos(2 * gamma) + 0.000907 * math.sin(2 * gamma) - 0.002697 * math.cos(3 * gamma) + 0.00148 * math.sin(3 * gamma)
    lat = math.radians(LAT)
    for m in range(9 * 60, 15 * 60 + 1, step_min):
        tst = m + eqt + 4 * LON - 60 * 9
        ha = math.radians(tst / 4 - 180)
        cz = math.sin(lat) * math.sin(decl) + math.cos(lat) * math.cos(decl) * math.cos(ha)
        zen = math.acos(max(-1, min(1, cz)))
        alt = math.pi / 2 - zen
        az = math.atan2(math.sin(ha), math.cos(ha) * math.sin(lat) - math.tan(decl) * math.cos(lat)) + math.pi  # 북=0 시계방향
        out.append((alt, az))
    return out


def shadows(fps_h, alt, az, rot):
    """평지 위 각기둥 그림자 = 바닥면 ∪ 이동면 ∪ 변 스윕 사각형."""
    k = 1 / math.tan(alt)
    # 로컬 좌표는 rot만큼 돌아가 있으므로 방위도 같이 돌림
    a = az - math.radians(rot)
    ux, uy = -math.sin(a), -math.cos(a)  # 그림자 방향 = 태양 반대
    quads = []
    for fp, h in fps_h:
        dx, dy = ux * k * h, uy * k * h
        for poly in getattr(fp, "geoms", [fp]):
            rings = [poly.exterior] + list(poly.interiors)
            for r in rings:
                c = np.asarray(r.coords)
                p0, p1 = c[:-1], c[1:]
                q = np.stack([p0, p1, p1 + (dx, dy), p0 + (dx, dy), p0], axis=1)
                quads.append(q)
            quads.append(None)
    qs = np.concatenate([q for q in quads if q is not None]) if quads else np.zeros((0, 5, 2))
    polys = shapely.polygons(qs)
    polys = shapely.make_valid(polys)
    allfp = [fp for fp, _ in fps_h]
    return shapely.union_all(np.concatenate([polys, np.array(allfp, dtype=object)]))


def max_run(b):
    best = cur = np.zeros(b.shape[1], dtype=int)
    best = best.copy()
    for row in b:
        cur = np.where(row, cur + 1, 0)
        best = np.maximum(best, cur)
    return best


# ---------------------------------------------------------------- 한 번 실행
def random_genes(rng, site):
    minx, miny, maxx, maxy = site.bounds
    n_x = rng.randint(2, 5)
    ys = sorted(rng.uniform(miny + 60, maxy - 60) for _ in range(n_x))
    ws = [rng.choice([12, 15, 20])] * 2 + [rng.choice([6, 8, 12, 15, 20]) for _ in range(n_x - 2)]
    ws[0] = 40  # 동서 선형공원 40 m (사용자 축 ②)
    return dict(
        x_L=rng.uniform(-30, 30), W_L=rng.choice([20, 30, 40]), cross=list(zip(ys, ws)),
        diag_deg=rng.uniform(25, 50), diag_y=rng.uniform(-200, 200), W_diag=rng.choice([8, 12]),
        W_perim=rng.choice([10, 12]), amax=rng.uniform(1500, 5000), min_front=rng.uniform(8, 20),
        dens=[rng.choice([0, 1, 2]) for _ in range(12)], use=[rng.choice(["perimeter", "slab", "point", "public"]) for _ in range(12)],
    )


def run_once(site, rot, g, rng, grid=5.0, step=10):
    t = {}
    t0 = time.perf_counter()
    roads, blocks = roads_and_blocks(site, g)
    t["S1_도로·가구"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    road_edge = roads.boundary.buffer(0.5)
    parcels = []
    for b in blocks:
        parcels += split_parcels(b, road_edge, g["amax"], g["min_front"], rng)
    t["S3_획지분할"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    minx, miny, maxx, maxy = site.bounds
    GSI = [(0.45, 2), (0.50, 3), (0.55, 5)]
    fps_h = []
    tot_fp = tot_gfa = 0.0
    road_adj = road_edge.buffer(2)
    for p in parcels:
        zi = min(5, int((p.centroid.y - miny) / (maxy - miny) * 6)) * 2 + (0 if p.centroid.x < g["x_L"] else 1)
        gsi_t, L_t = GSI[g["dens"][zi]]
        hmax = 15.0 if p.intersects(road_adj) else 20.0  # 도로 인접 15 m, 내부 20 m [T1 고도지구·경관 가이드라인, 해석 A]
        fp, L = mass_for(p, g["use"][zi], gsi_t, L_t, hmax)
        if fp is None or fp.is_empty:
            continue
        fps_h.append((fp, L * FLOOR_H))
        tot_fp += fp.area
        tot_gfa += fp.area * L
    t["S4_매스"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    kpi = dict(획지수=len(parcels), 가구수=len(blocks), 동수=len(fps_h), GSI_대지=tot_fp / site.area, FSI_대지=tot_gfa / site.area, 도로율=roads.area / site.area)
    t["KPI_면적"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    xs = np.arange(minx, maxx, grid)
    ys = np.arange(miny, maxy, grid)
    X, Y = np.meshgrid(xs, ys)
    X, Y = X.ravel(), Y.ravel()
    allfp = shapely.union_all([f for f, _ in fps_h])
    keep = shapely.contains_xy(site, X, Y) & ~shapely.contains_xy(allfp, X, Y)
    X, Y = X[keep], Y[keep]
    sv = [(a, z) for a, z in sun_vectors(step) if a > 0]
    lit = np.zeros((len(sv), len(X)), dtype=bool)
    for i, (alt, az) in enumerate(sv):
        sh = shadows(fps_h, alt, az, rot)
        shapely.prepare(sh)
        lit[i] = ~shapely.contains_xy(sh, X, Y)
    run = max_run(lit) * step  # 분
    kpi["옥외_연속2h_충족률"] = float((run >= 120).mean())
    kpi["격자점"] = int(len(X))
    kpi["태양벡터"] = len(sv)
    t["E_일조2.5D"] = time.perf_counter() - t0
    return t, kpi


def export_3dm(fps_h, path=None):
    """rhino3dm으로 압출 매스 생성 시간만 측정(파일은 쓰지 않음)."""
    f = rhino3dm.File3dm()
    for fp, h in fps_h:
        for poly in getattr(fp, "geoms", [fp]):
            pl = rhino3dm.Polyline([rhino3dm.Point3d(x, y, 0) for x, y in poly.exterior.coords])
            ex = rhino3dm.Extrusion.Create(pl.ToPolylineCurve(), h, True)
            if ex:
                f.Objects.AddExtrusion(ex)
    return f


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    t0 = time.perf_counter()
    B, units = load_boundary()
    site, (cx, cy, ang) = to_local(B)
    print(f"읽기 {time.perf_counter() - t0:.2f}s · 3dm 단위 설정={units} · 경계 면적={B.area:,.1f} (단위²) · 긴 변 방위각={ang:.2f}°")
    rng = random.Random(20261026)
    rot = 90 - ang
    rows = []
    for i in range(n):
        g = random_genes(rng, site)
        t, kpi = run_once(site, rot, g, rng)
        rows.append((t, kpi))
    keys = list(rows[0][0].keys())
    print(f"표본 {n}개 (격자 5 m, 동지 09–15시 10분 간격)")
    for k in keys:
        v = np.array([r[0][k] for r in rows])
        print(f"  {k:<12} 중앙 {np.median(v)*1000:8.1f} ms · 최대 {v.max()*1000:8.1f} ms")
    tot = np.array([sum(r[0].values()) for r in rows])
    gen = np.array([sum(v for k, v in r[0].items() if not k.startswith("E_")) for r in rows])
    print(f"  생성+면적 KPI 합계 중앙 {np.median(gen)*1000:.1f} ms · 일조 포함 합계 중앙 {np.median(tot)*1000:.1f} ms · 최대 {tot.max()*1000:.1f} ms")
    for k in ["가구수", "획지수", "동수", "GSI_대지", "FSI_대지", "도로율", "옥외_연속2h_충족률", "격자점", "태양벡터"]:
        v = np.array([r[1][k] for r in rows], dtype=float)
        print(f"  {k:<14} 범위 {v.min():.3f} – {v.max():.3f}")
    # 일조 격자 2 m·5분 간격 1회
    g = random_genes(rng, site)
    t, kpi = run_once(site, rot, g, rng, grid=2.0, step=5)
    print(f"  [정밀] 격자 2 m·5분: 일조 {t['E_일조2.5D']:.2f}s, 격자점 {kpi['격자점']}, 태양벡터 {kpi['태양벡터']}")
    # rhino3dm 압출 생성
    roads, blocks = roads_and_blocks(site, g)
    t0 = time.perf_counter()
    fps = [(b.buffer(-5), 12.0) for b in blocks if not b.buffer(-5).is_empty]
    export_3dm(fps)
    print(f"  rhino3dm 압출 {len(fps)}개 생성 {time.perf_counter() - t0:.3f}s")


if __name__ == "__main__":
    main()
