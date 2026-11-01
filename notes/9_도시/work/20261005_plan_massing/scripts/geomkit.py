"""기하 도구 + 층수 상한 포락(고도지구 × 경계 켜 규칙). 모든 좌표 EPSG:5187 m."""
import math, pickle
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely import affinity
from shapely.ops import unary_union
from shapely.strtree import STRtree

def polys(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    if g.geom_type in ("MultiPolygon", "GeometryCollection"): return [p for x in g.geoms for p in polys(x)]
    return []

def clean(g, min_area=25.0, min_w=2.0):
    """얇은 조각 제거(열림 연산) 후 면적 하한."""
    if g.is_empty: return []
    h = g.buffer(-min_w / 2, join_style=2).buffer(min_w / 2, join_style=2)
    return [p for p in polys(h) if p.area >= min_area]

def rrect(cx, cy, L, W, ang_deg=0.0):
    """중심 (cx,cy), 길이 L(ang 방향) × 폭 W 의 회전 사각형."""
    r = box(-L / 2, -W / 2, L / 2, W / 2)
    r = affinity.rotate(r, ang_deg, origin=(0, 0))
    return affinity.translate(r, cx, cy)

def mrr(poly):
    """최소 외접 사각형 (L≥W, 각도 deg)."""
    r = poly.minimum_rotated_rectangle
    cs = list(r.exterior.coords)[:4]
    e = [(cs[i + 1][0] - cs[i][0], cs[i + 1][1] - cs[i][1]) for i in range(3)]
    l0, l1 = math.hypot(*e[0]), math.hypot(*e[1])
    if l0 >= l1: ang = math.degrees(math.atan2(e[0][1], e[0][0])); L, W = l0, l1
    else: ang = math.degrees(math.atan2(e[1][1], e[1][0])); L, W = l1, l0
    return L, W, ang % 180

def seg_dir(poly):
    return mrr(poly)[2]

def poisson(poly, r, seed=1, k=18):
    """폴리곤 안 푸아송 디스크 점(가로수·공원수 배치)."""
    if poly is None or poly.is_empty: return []
    rng = np.random.default_rng(seed)
    minx, miny, maxx, maxy = poly.bounds
    pts = []
    for _ in range(int(poly.area / (r * r) * 2.2) + 20):
        p = Point(rng.uniform(minx, maxx), rng.uniform(miny, maxy))
        if not poly.contains(p): continue
        if all((p.x - q.x) ** 2 + (p.y - q.y) ** 2 >= r * r for q in pts): pts.append(p)
    return pts

class Envelope:
    """층수·높이 상한 포락. cap(point or geom) → dict(floors_cap_by_side, height_cap)."""
    def __init__(self, U, godo, SIDE_CAP, FLOOR_H, HEIGHT_CAP):
        self.U = U; self.ring = U.exterior; self.SIDE_CAP = SIDE_CAP
        self.b1 = U.difference(U.buffer(-40))
        self.b2 = U.buffer(-40).difference(U.buffer(-90))
        self.b3 = U.buffer(-90)
        self.godo = [(g["geom"], g["h_max"], g["kind"]) for g in godo if g["geom"].intersects(U)]
        self.FLOOR_H = FLOOR_H
        cs = list(self.ring.coords)
        self.segs = [(LineString([cs[i], cs[i + 1]]), cs[i], cs[i + 1]) for i in range(len(cs) - 1)]
        self.seg_geoms = [s[0] for s in self.segs]
        self.tree = STRtree(self.seg_geoms)

    def side(self, p):
        """가장 가까운 경계 변의 바깥 법선 방향으로 서·동·남·북·수변을 정한다. (U 는 시계방향 링 → 바깥 = 진행방향의 왼쪽)"""
        pt = p if p.geom_type == "Point" else p.centroid
        i = self.tree.nearest(pt)
        (_, a, b) = self.segs[i]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L                       # 바깥 법선
        ang = math.degrees(math.atan2(ny, nx))         # 동=0, 북=90, 서=180, 남=-90
        q = self.ring.interpolate(self.ring.project(pt))
        if q.y > 361280 and 15 <= ang <= 80: return "수변"           # 북동 사선(북천 방향)
        if -45 <= ang < 45: return "동"
        if 45 <= ang < 135: return "북"
        if -135 <= ang < -45: return "남"
        return "서"

    def band(self, pt):
        if self.b3.contains(pt): return 2
        if self.b2.contains(pt): return 1
        return 0

    def height_cap(self, g):
        """바닥 전체에서 가장 낮은 고도지구 최고높이(m). 점이면 포함 여부, 면이면 1㎡ 이상 걸치는 구역을 모두 반영(보수적)."""
        h = 20.0
        for gg, hm, kind in self.godo:
            if kind == "최고" and hm:
                hit = gg.contains(g) if g.geom_type == "Point" else gg.intersection(g).area > 1.0
                if hit: h = min(h, float(hm))
        return h

    def floors_cap(self, geom, floor_h, program_max):
        pt = geom.representative_point() if geom.geom_type != "Point" else geom
        s = self.side(pt); b = self.band(pt)
        sc = self.SIDE_CAP[s][b]
        hcap = self.height_cap(pt)
        by_h = int(hcap // floor_h)
        f = min(program_max, sc, by_h)
        return max(f, 1), dict(side=s, band=b + 1, side_cap=sc, h_cap=hcap, by_height=by_h)

    def split_bands(self, g):
        """footprint 를 켜 구간으로 나눠 [(piece, band_idx)] 반환."""
        out = []
        for i, b in enumerate((self.b1, self.b2, self.b3)):
            for p in clean(g.intersection(b), min_area=40, min_w=3):
                out.append((p, i))
        return out
