"""지형도면고시도(11·12장) 채움색 → 획지/공원/주차장/청사/문화 폴리곤 (EPSG:5187 + 4326).

검증: 고시 제2026-8호 결정조서 면적과 대조.
"""
import json, sys
import numpy as np, cv2
from PIL import Image
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union, transform as stf
from shapely.geometry.polygon import orient
from pyproj import Transformer
from _common import PROCESSED, ROOT

CLASSES = {  # 이름: (RGB 중심, 허용오차)
    "commercial": ((255, 230, 255), 10),   # 상업시설용지 (특계1~3 / 상1~3)
    "civic":      ((206, 242, 255), 10),   # 공공청사용지 (공청1·2)  ※ 교통광장(폐지)도 같은 색 — 위치로 제외
    "culture":    ((255, 242, 205), 8),    # 문화시설용지 (문화1)
    "park":       ((116, 231, 76), 28),    # 근린공원
    "parking":    ((220, 220, 220), 8),    # 주차장용지 (주1)
}
MIN_AREA_M2 = 300
OUTLINE_HALF_M = 0.95   # 획지 외곽선(굵은 보라선 ≈1.9m)의 절반 — 채움은 선 안쪽에서 끝나므로 중심선까지 확장
# 고시 결정조서 (㎡)
GOSI = {"상1": 14503, "상2": 14083, "상3": 13445, "공청1": 11583, "공청2": 13404, "문화1": 9770, "주1": 5756,
        "공원1": 17395, "공원2": 20150, "공원3": 17870}


def load_pgw(p):
    a, d, b, e, c, f = [float(x) for x in open(p).read().split()]
    return a, -e, c - a / 2, f + (-e) / 2


def zone_mask(shape_hw, px, py, ox, oy):
    """지구단위계획구역(extract_boundary.py 산출) 래스터 마스크 — 바깥 채움색 배제."""
    z = json.load(open(PROCESSED / "gosi2026-8_zone_5187.geojson", encoding="utf-8"))["features"][0]["geometry"]
    ring = np.array([[(x - ox) / px, (oy - y) / py] for x, y in z["coordinates"][0]], np.int32)
    m = np.zeros(shape_hw, np.uint8); cv2.fillPoly(m, [ring], 1)
    return cv2.dilate(m, np.ones((9, 9), np.uint8))   # 경계선 폭 여유


def sheet_polys(slug):
    png = PROCESSED / f"gosi2026-8_{slug}_5187.png"
    px, py, ox, oy = load_pgw(PROCESSED / f"gosi2026-8_{slug}_5187.pgw")
    im = np.asarray(Image.open(png).convert("RGB")).astype(int)
    zm = zone_mask(im.shape[:2], px, py, ox, oy)
    out = {}
    minpx = int(MIN_AREA_M2 / (px * py))
    for cls, (rgb, tol) in CLASSES.items():
        m = np.all(np.abs(im - np.array(rgb)) <= tol, axis=2).astype(np.uint8) & zm
        if cls == "parking":  # 회색: R=G=B 조건 추가
            m &= (np.abs(im[..., 0] - im[..., 1]) <= 3) & (np.abs(im[..., 1] - im[..., 2]) <= 3)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((17, 17), np.uint8))   # 관통선·글자 메우기 (~3m)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((25, 25), np.uint8))    # 도로 건너 가는 연결(<4.8m) 끊기 — 상2/상3 분리
        # 획지에 실제 구멍은 없다 → 외곽선만 취하고 내부(라벨 박스 등)는 채운다
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        polys = []
        to_map = lambda arr: [(ox + (u + .5) * px, oy - (v + .5) * py) for u, v in arr]
        for c in cs:
            if cv2.contourArea(c) < minpx: continue
            ext = c.reshape(-1, 2)
            if len(ext) < 3: continue
            poly = Polygon(to_map(ext)).buffer(0)
            if not poly.is_empty: polys.append(poly.simplify(0.3))
        out[cls] = polys
        print(f"  [{slug}] {cls:10s} 폴리곤 {len(polys)}개  면적 {[round(p.area) for p in polys]}")
    return out


def main():
    per = {s: sheet_polys(s) for s in ("jdp_n", "jdp_s")}
    merged = {}
    for cls in CLASSES:
        u = unary_union(per["jdp_n"][cls] + per["jdp_s"][cls]).buffer(1.2).buffer(-1.2)  # 시트 이음새(≈2m 오프셋)·관통선 봉합
        u = u.buffer(OUTLINE_HALF_M, join_style=2)   # 외곽선 중심선까지
        geoms = list(u.geoms) if isinstance(u, MultiPolygon) else [u]
        merged[cls] = [g for g in geoms if g.area >= MIN_AREA_M2]
    # 블록 명명
    feats = []
    com = sorted(merged["commercial"], key=lambda g: -g.area)[:3]
    civ = sorted(merged["civic"], key=lambda g: -g.area)[:2]
    cul = sorted(merged["culture"], key=lambda g: -g.area)[:1]
    prk = sorted(merged["parking"], key=lambda g: -g.area)[:1]
    if len(com) == 3:
        w = min(com, key=lambda g: g.centroid.x); rest = sorted([g for g in com if g is not w], key=lambda g: -g.centroid.y)
        feats += [dict(cls="commercial", name="상1", geom=w), dict(cls="commercial", name="상2", geom=rest[0]), dict(cls="commercial", name="상3", geom=rest[1])]
    civ = sorted(civ, key=lambda g: -g.centroid.y)
    feats += [dict(cls="civic", name=f"공청{i+1}", geom=g) for i, g in enumerate(civ)]
    feats += [dict(cls="culture", name="문화1", geom=g) for g in cul]
    # 주1: 도면 채움이 획지선 안쪽 ~3m에서 끝남(남·동측 흰 띠, 2026-09-17 육안 확인) → 획지선까지 확장. 속성에 명시
    feats += [dict(cls="parking", name="주1", geom=g.buffer(2.9, join_style=2), note="채움 인셋 보정 +2.9m (도면 채움 4,829㎡)") for g in prk]
    # 공원: 상업블록 상단보다 북 = 공원1, 공공청사 하단보다 남 = 공원3, 그 사이 = 공원2 (도로로 쪼개진 조각 합침)
    y_top = max(g.bounds[3] for g in com) if com else None
    y_bot = min(g.bounds[1] for g in civ) if civ else None
    bands = {"공원1": [], "공원2": [], "공원3": []}
    for g in merged["park"]:
        cy = g.centroid.y
        if y_top and cy > y_top - 5: bands["공원1"].append(g)
        elif y_bot and cy < y_bot + 5: bands["공원3"].append(g)
        else: bands["공원2"].append(g)
    for nm, gs in bands.items():
        if gs: feats.append(dict(cls="park", name=nm, geom=unary_union(gs), pieces=len(gs)))

    print("\n=== 고시 면적 대조 ===")
    print(f"{'블록':6s} {'추출㎡':>9s} {'고시㎡':>9s} {'차이':>7s}")
    for f in feats:
        g_ = GOSI.get(f["name"]); a = f["geom"].area
        d = f"{(a - g_) / g_ * 100:+.1f}%" if g_ else "-"
        print(f"{f['name']:6s} {a:9,.0f} {g_ if g_ else '':>9} {d:>7}  {('조각 '+str(f['pieces'])) if f.get('pieces',1)>1 else ''}")
    t = Transformer.from_crs("EPSG:5187", "EPSG:4326", always_xy=True).transform
    for crs, tf, fn in [("5187", None, "gosi2026-8_blocks_5187.geojson"), ("4326", t, "gosi2026-8_blocks_4326.geojson")]:
        fc = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": dict(name=f["name"], cls=f["cls"], area_m2=round(f["geom"].area, 1),
                                                   gosi_area_m2=GOSI.get(f["name"]), note=f.get("note", ""),
                                                   source="경주시 고시 제2026-8호 지형도면고시도 11·12장 채움색 벡터화 (EPSG:5176 도곽좌표 → 5187)"),
             "geometry": mapping(orient(stf(tf, f["geom"]) if tf else f["geom"], 1.0))} for f in feats]}   # RFC7946: 외곽 반시계
        if crs == "5187": fc["crs"] = {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::5187"}}
        p = PROCESSED / fn; p.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8"); print("저장", p.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
