"""geom2 — v2 공통 형상: 구 역사 모임지붕(거리장 지붕), 그레이트 코트 유리 볼트·격자선"""
import math
import numpy as np
import shapely
from shapely.geometry import Point, LineString
from scipy.spatial import Delaunay


def hip_roof(poly, z0, slope_deg=33.0, step=0.5, axis=(1.0, 0.0)):
    """다각형 위 모임지붕 메쉬 — 높이 = z0 + tan(경사) × 외곽선까지 거리(곧은 뼈대 지붕의 근사)
    axis: 표본 격자 방향(건물 장축) — 용마루가 계단지지 않게 장축에 맞춘다. 반환 (V[n,3], F[m,3])"""
    k = math.tan(math.radians(slope_deg))
    pts = []
    for ring in [poly.exterior] + list(poly.interiors):
        L = ring.length; n = max(int(L / (step * 0.8)), 8)
        pts += [ring.interpolate(i * L / n).coords[0] for i in range(n)]
    ux, uy = axis; nrm = math.hypot(ux, uy); ux, uy = ux / nrm, uy / nrm; vx, vy = -uy, ux
    c = poly.centroid; R = max(poly.bounds[2] - poly.bounds[0], poly.bounds[3] - poly.bounds[1])
    aa = np.arange(-R, R, step); bb = np.arange(-R, R, step)
    A, Bm = np.meshgrid(aa, bb); X = c.x + A * ux + Bm * vx; Y = c.y + A * uy + Bm * vy
    inner = poly.buffer(-step * 0.35)
    m = shapely.contains_xy(inner, X.ravel(), Y.ravel())
    pts += list(zip(X.ravel()[m], Y.ravel()[m]))
    P = np.array(pts)
    tri = Delaunay(P).simplices
    cen = P[tri].mean(1)
    keep = shapely.contains_xy(poly, cen[:, 0], cen[:, 1])
    bnd = poly.boundary
    d = shapely.distance(shapely.points(P[:, 0], P[:, 1]), bnd)
    V = np.c_[P, z0 + k * d]
    return V, tri[keep]


def vault(G, step=1.5):
    """그레이트 코트 유리 볼트 메쉬 — 장축 좌표(a,b) 격자, z = z0 + (z1−z0)t + rise·sin(πt)"""
    o, ua, vb = np.array(G["o"]), np.array(G["ua"]), np.array(G["vb"])
    a = np.linspace(G["a0"], G["a1"], max(int((G["a1"] - G["a0"]) / step), 2) + 1)
    b = np.linspace(G["b0"], G["b1"], max(int((G["b1"] - G["b0"]) / step), 2) + 1)
    V = []
    for bj in b:
        t = (bj - G["b0"]) / (G["b1"] - G["b0"]); z = G["z0"] + (G["z1"] - G["z0"]) * t + G["rise"] * math.sin(math.pi * t)
        for ai in a:
            p = o + ai * ua + bj * vb; V.append((p[0], p[1], z))
    V = np.array(V); na = len(a); F = []
    for j in range(len(b) - 1):
        for i in range(na - 1):
            q0 = j * na + i; q1 = q0 + 1; q2 = q0 + na + 1; q3 = q0 + na
            F += [(q0, q1, q2), (q0, q2, q3)]
    return V, np.array(F)


def vault_z(G, bj):
    t = (bj - G["b0"]) / (G["b1"] - G["b0"]); return G["z0"] + (G["z1"] - G["z0"]) * t + G["rise"] * math.sin(math.pi * t)


def vault_grid(G, pitch=4.0, ds=0.6):
    """유리 지붕 사선 격자(두 방향 대각선) — 선분 목록 [(p,q), ...] (3D)"""
    o, ua, vb = np.array(G["o"]), np.array(G["ua"]), np.array(G["vb"])
    segs = []
    W = G["a1"] - G["a0"]; Hh = G["b1"] - G["b0"]
    for sgn in (1, -1):
        for c in np.arange(-Hh, W + Hh, pitch):
            pts = []
            for bj in np.arange(G["b0"], G["b1"] + 1e-6, ds):
                ai = G["a0"] + c + sgn * (bj - G["b0"]) if sgn > 0 else G["a0"] + c - (bj - G["b0"])
                if G["a0"] <= ai <= G["a1"]:
                    p = o + ai * ua + bj * vb; pts.append((p[0], p[1], vault_z(G, bj) + 0.05))
                elif pts:
                    break
            for p, q in zip(pts, pts[1:]): segs.append((p, q))
    # 테두리·용마루 방향 띠(장축 방향 선)
    for bj in (G["b0"], G["b1"]) + tuple(np.linspace(G["b0"], G["b1"], 7)[1:-1]):
        z = vault_z(G, bj) + 0.05
        p = o + G["a0"] * ua + bj * vb; q = o + G["a1"] * ua + bj * vb
        segs.append(((p[0], p[1], z), (q[0], q[1], z)))
    for ai in (G["a0"], G["a1"]):
        prev = None
        for bj in np.arange(G["b0"], G["b1"] + 1e-6, ds):
            p = o + ai * ua + bj * vb; cur = (p[0], p[1], vault_z(G, bj) + 0.05)
            if prev: segs.append((prev, cur))
            prev = cur
    return segs
