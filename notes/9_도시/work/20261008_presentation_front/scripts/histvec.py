# -*- coding: utf-8 -*-
"""위치 기준 벡터(EPSG:5187) 로더 + 래스터화. 연속수치지도(B020, EPSG:5179) → 5187 변환."""
import os, pickle, warnings
warnings.filterwarnings("ignore")
import numpy as np
import geopandas as gpd
from shapely.geometry import box
from shapely import affinity
import cv2

ROOT = "C:/Users/OFFICE/Desktop/9_도시/"
B020 = ROOT + "대지/(B020)연속수치지도_202609132098/"
SCR = "C:/Users/OFFICE/AppData/Local/Temp/claude/C--Users-OFFICE-Desktop-9---/b98333f0-4ddf-4213-a0db-66cb837b3d35/scratchpad/"
CACHE = SCR + "vec_cache.pkl"

# 틀 정의 (EPSG:5187)
CX, CY = 219780.0, 360850.0
FRAMES = {
    "F1": dict(x0=CX - 600, x1=CX + 600, y0=CY - 800, y1=CY + 800, w=1800, h=2400),
    "F2": dict(x0=CX - 1500, x1=CX + 1500, y0=CY - 2000, y1=CY + 2000, w=1500, h=2000),
}

def _load():
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    # 넓은 범위 (F2 + 여유)
    bb = box(CX - 3000, CY - 3500, CX + 3000, CY + 3500)
    out = {}
    layers = {
        "bldg": "N3A_B0010000.shp",
        "roadA": "N3A_A0010000.shp",
        "roadC": "N3L_A0020000.shp",
        "rail": "N3L_A0171119.shp",
        "river": "N3L_E0020000.shp",
        "heritage": "N3A_C0305316.shp",
        "riverA": "N3A_E0010001.shp",
        "sheet": "N3A_H0010000.shp",
    }
    for k, fn in layers.items():
        g = gpd.read_file(B020 + fn, encoding="cp949")
        g = g.set_crs(5179, allow_override=True).to_crs(5187)
        g = g[g.intersects(bb)].copy()
        out[k] = g
    # 사용자 경계 / 고시 구역
    out["plan"] = gpd.read_file(ROOT + "work/20261005_boundary_check/user_boundary_current_5187.geojson").to_crs(5187)
    out["gosi"] = gpd.read_file(ROOT + "archive/C_data/processed/gosi2026-8_zone_5187.geojson").to_crs(5187)
    with open(CACHE, "wb") as f:
        pickle.dump(out, f)
    return out

V = None
def get():
    global V
    if V is None:
        V = _load()
    return V

def geom_lines(g):
    """shapely → list of Nx2 arrays (exterior/line)"""
    res = []
    for geom in g.geometry:
        if geom is None or geom.is_empty:
            continue
        gt = geom.geom_type
        if gt == "Polygon":
            res.append(np.asarray(geom.exterior.coords)[:, :2])
            for r in geom.interiors:
                res.append(np.asarray(r.coords)[:, :2])
        elif gt == "MultiPolygon":
            for p in geom.geoms:
                res.append(np.asarray(p.exterior.coords)[:, :2])
        elif gt == "LineString":
            res.append(np.asarray(geom.coords)[:, :2])
        elif gt == "MultiLineString":
            for p in geom.geoms:
                res.append(np.asarray(p.coords)[:, :2])
    return res

def to_px(pts, x0, y1, s):
    """5187 좌표 → 틀 픽셀 (x0=서쪽, y1=북쪽, s=m/px)"""
    return np.stack([(pts[:, 0] - x0) / s, (y1 - pts[:, 1]) / s], axis=1)

def raster_lines(layers, x0, y1, w, h, s, thick=1, color=255):
    img = np.zeros((h, w), np.uint8)
    for g in layers:
        for ln in geom_lines(g):
            p = to_px(ln, x0, y1, s)
            cv2.polylines(img, [np.round(p * 16).astype(np.int32)], False, color, thick, cv2.LINE_AA, shift=4)
    return img
