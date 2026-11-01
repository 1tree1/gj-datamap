# -*- coding: utf-8 -*-
"""시굴조사 대상 범위 도형 추출 — 김권일(2026.02.27) 발표자료 p.23 '시굴조사 대상범위' 그림을 판독해 EPSG:5187 로 맞춘다.

자료에 시굴·유존지역의 도형(shp/geojson)이 없고 면적 숫자만 있어서(archive/00_meta/gaps.md), 발표자료 그림을 판독한다.
  그림 안 표기: 조사지역 148,770㎡ = 성동동 유물산포지 104,997㎡(1·2구역) + 성동동사지Ⅱ 중 40,882㎡(3구역) + 건물 3동(갈색) 2,891㎡
  시굴 대상 범위 145,879㎡ = 조사지역 − 갈색 건물 3동
절차
  1) PDF p.23 에 들어 있는 원본 그림(840x1197 px)을 꺼낸다.
  2) 색으로 조사지역(주황+보라 외곽선) · 3구역(분홍+빨강 외곽선) · 건물 3동(갈색+검정 외곽선)을 분리해 도형으로 만든다.
  3) 그림 축척은 축척 막대(200 m = 216 px, 약 1.08 px/m), 방위는 위쪽이 북(5187 좌표축과 거의 일치)이다.
     회전 0°로 두고 (축척, 이동) 을 고시 2026-8호 구역(gosi2026-8_zone_5187.geojson)과의 IoU 가 최대가 되도록 맞춘다
     (조사지역 ⊂ 고시 구역에 가깝고, 둘 다 같은 필지선을 따라 그려진 경계라 IoU 0.93 이상에서 수렴한다).
  4) 외곽선 두께의 절반(약 2 px)만큼 안으로 줄인다.
정확도: 맞춤 IoU, 건물 3동 중 작은 동의 위치 오차(약 3 m)로 보아 위치 오차는 대략 ±10 m, 면적은 문서값 대비 ±3% 이내로 본다.
        근사 도형이므로 지도에는 '그림 판독' 으로 밝힌다. 등급 T2(발표자료) + 판독.
출력: research/data_series/siguel_digitized_5187.geojson (재생성 가능)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapkit_analysis as mk
import shapely
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

PDF = mk.ROOT / "04 김권일 학예연구실장_발표자료 (구경주역 매장유산 현황 및 도시재생 관련 제언).pdf"
PAGE = 22                       # 0부터, 인쇄쪽 23
DOC = dict(survey=148770.0, yumul=104997.0, saji2=40882.0, boxes=2891.0, target=145879.0)


def _extract_figure():
    import pymupdf
    doc = pymupdf.open(str(PDF))
    page = doc[PAGE]
    for img in page.get_images(full=True):
        d = doc.extract_image(img[0])
        if (d["width"], d["height"]) == (840, 1197):
            from PIL import Image
            import io
            return np.asarray(Image.open(io.BytesIO(d["image"])).convert("RGB")).astype(int)
    raise RuntimeError("p.23 그림(840x1197)을 찾지 못함")


def _near(a, c, tol):
    return np.abs(a - np.array(c)).max(axis=2) <= tol


def _vectorize(mask, simplify=0.8):
    from rasterio import features
    from rasterio.transform import Affine
    out = []
    for geom, val in features.shapes(mask.astype(np.uint8), mask=mask, transform=Affine.identity()):
        if val == 1:
            out.append(shape(geom))
    out.sort(key=lambda g: -g.area)
    return [g.simplify(simplify) for g in out]


def build():
    from scipy import ndimage as ndi
    a = _extract_figure()
    orange = _near(a, (228, 172, 108), 16)
    pink = _near(a, (251, 180, 136), 14)
    brown = _near(a, (164, 114, 81), 22)
    purple = (a[:, :, 0] > 110) & (a[:, :, 0] < 205) & (a[:, :, 1] < 80) & (a[:, :, 2] > 50) & (a[:, :, 2] < 150)
    red = (a[:, :, 0] > 205) & (a[:, :, 1] < 90) & (a[:, :, 2] < 90)
    black = a.sum(axis=2) < 120

    def fill(mask, it=2, k=5):
        m = ndi.binary_closing(mask, structure=np.ones((k, k)), iterations=it)
        return ndi.binary_fill_holes(m)

    def biggest(mask):
        lab, n = ndi.label(mask)
        sizes = ndi.sum(mask, lab, range(1, n + 1))
        return lab == (int(np.argmax(sizes)) + 1)

    survey = biggest(fill(orange | pink | brown | purple))
    # 3구역: 분홍 칸 + 둘레 빨강선(분홍에 붙은 것만)
    pink_big = biggest(fill(pink))
    red_near = red & ndi.binary_dilation(pink_big, structure=np.ones((9, 9)))
    zone3 = biggest(fill(pink_big | red_near, it=2, k=5))
    # 건물 3동: 갈색 + 둘레 검정선(갈색에 붙은 것만)
    brown_f = fill(brown, it=1, k=3)
    black_near = black & ndi.binary_dilation(brown_f, structure=np.ones((7, 7)))
    boxes = fill(brown_f | black_near, it=1, k=3)
    lab, n = ndi.label(boxes)
    sizes = ndi.sum(boxes, lab, range(1, n + 1))
    keep = np.argsort(sizes)[-3:] + 1
    boxes = np.isin(lab, keep)

    P = _vectorize(survey)[0]
    Z3 = _vectorize(zone3)[0]
    BX = [g for g in _vectorize(boxes, 0.5)][:3]
    cu, cv = P.centroid.x, P.centroid.y

    def tf(poly, ppm, tx, ty):
        def f(c):
            c = np.asarray(c, float)
            return np.column_stack([tx + (c[:, 0] - cu) / ppm, ty - (c[:, 1] - cv) / ppm])
        return shapely.transform(poly, f)

    D = mk.gosi_zone()
    from scipy.optimize import minimize

    def neg_iou(p):
        g = tf(P, p[0], p[1], p[2])
        if not g.is_valid:
            g = g.buffer(0)
        return -g.intersection(D).area / g.union(D).area

    r = minimize(neg_iou, [1.082, 219773.0, 360965.0], method="Nelder-Mead",
                 options=dict(xatol=0.02, fatol=1e-8, maxiter=800))
    ppm, tx, ty = [float(v) for v in r.x]
    iou = float(-r.fun)

    inset = 2.0 / ppm          # 외곽선 두께의 절반(약 2 px)
    survey_m = tf(P, ppm, tx, ty).buffer(-inset)
    zone3_m = tf(Z3, ppm, tx, ty).buffer(-0.5 * 2.0 / ppm)
    boxes_m = unary_union([tf(b, ppm, tx, ty).buffer(-0.5 * 2.0 / ppm) for b in BX])
    zone3_m = zone3_m.intersection(survey_m)
    saji2 = zone3_m.difference(boxes_m)
    yumul = survey_m.difference(zone3_m).difference(boxes_m)
    target = survey_m.difference(boxes_m)
    stats = dict(ppm=ppm, tx=tx, ty=ty, iou=iou,
                 survey=survey_m.area, zone3=zone3_m.area, boxes=boxes_m.area, saji2=saji2.area,
                 yumul=yumul.area, target=target.area)
    return dict(survey=survey_m, zone3=zone3_m, boxes=boxes_m, saji2=saji2, yumul=yumul, target=target,
                stats=stats, box_list=[tf(b, ppm, tx, ty) for b in BX])


def save_geojson(res, path):
    feats = []
    desc = {"survey": "조사지역(그림 판독, 문서 148,770㎡)", "yumul": "성동동 유물산포지 1·2구역(그림 판독, 문서 104,997㎡)",
            "saji2": "성동동사지Ⅱ 3구역 중 조사지역 안(그림 판독, 문서 40,882㎡)", "boxes": "제외 건물 3동(그림 판독, 문서 2,891㎡)",
            "target": "시굴조사 대상 범위 = 조사지역 − 건물 3동(그림 판독, 문서 145,879㎡)"}
    for k in ("survey", "yumul", "saji2", "boxes", "target"):
        feats.append({"type": "Feature", "properties": {"id": k, "desc": desc[k], "area_m2": round(res[k].area, 1),
                                                       "doc_area_m2": DOC[k], "src": "김권일(2026.02.27) 발표자료 p.23 그림 판독, T2 근사"},
                      "geometry": mapping(res[k])})
    json.dump({"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::5187"}},
               "features": feats}, open(path, "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    res = build()
    s = res["stats"]
    print(f"맞춤: ppm {s['ppm']:.4f} px/m, 이동 ({s['tx']:.1f}, {s['ty']:.1f}), IoU(고시 구역) {s['iou']:.4f}")
    for k in ("survey", "yumul", "saji2", "boxes", "target"):
        print(f"{k:7s} 지도 {s[k]:>10,.0f}㎡  문서 {DOC[k]:>10,.0f}㎡  차 {100*(s[k]/DOC[k]-1):+.1f}%")
    D = mk.gosi_zone()
    print("시굴 대상 ∩ 고시 구역(도면 추출)", f"{res['target'].intersection(D).area:,.0f}㎡", f"= 고시 구역의 {100*res['target'].intersection(D).area/D.area:.1f}%")
    save_geojson(res, mk.DATA_SERIES / "siguel_digitized_5187.geojson")
