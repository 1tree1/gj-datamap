"""11·12장 모자이크 → 빨간 쇄선(지구단위계획구역 경계) → 폴리곤. 고시 면적 156,460㎡ 대조."""
import json, sys
import numpy as np, cv2
from PIL import Image
from shapely.geometry import Polygon, mapping
from shapely.ops import transform as stf
from shapely.geometry.polygon import orient
from pyproj import Transformer
from _common import PROCESSED

GOSI_AREA = 156460


def load(slug):
    a, d, b, e, c, f = [float(x) for x in open(PROCESSED / f"gosi2026-8_{slug}_5187.pgw").read().split()]
    px, py = a, -e; ox, oy = c - px / 2, f + py / 2
    im = np.asarray(Image.open(PROCESSED / f"gosi2026-8_{slug}_5187.png").convert("RGB"))
    return im, px, py, ox, oy


def mosaic():
    sheets = [load("jdp_n"), load("jdp_s")]
    px, py = sheets[0][1], sheets[0][2]
    X0 = min(s[3] for s in sheets); Y1 = max(s[4] for s in sheets)
    X1 = max(s[3] + s[0].shape[1] * s[1] for s in sheets); Y0 = min(s[4] - s[0].shape[0] * s[2] for s in sheets)
    W = int(round((X1 - X0) / px)) + 2; H = int(round((Y1 - Y0) / py)) + 2
    can = np.full((H, W, 3), 255, np.uint8)
    for im, _, _, ox, oy in sheets[::-1]:  # 남쪽 먼저, 북쪽을 위에
        u = int(round((ox - X0) / px)); v = int(round((Y1 - oy) / py))
        h, w = im.shape[:2]
        can[v:v + h, u:u + w] = im[:H - v, :W - u]
    return can, px, py, X0, Y1


def main():
    can, px, py, ox, oy = mosaic()
    print(f"모자이크 {can.shape[1]}x{can.shape[0]}px  원점 ({ox:.2f},{oy:.2f})")
    Image.fromarray(can[::4, ::4]).save(PROCESSED / "gosi2026-8_jdp_mosaic_q.jpg", quality=80)
    r, g, b = [can[..., i].astype(int) for i in range(3)]
    red = ((r > 190) & (g < 90) & (b < 90)).astype(np.uint8)
    # 구역 경계는 빨강·파랑 교대 쇄선 → 굵은 파랑(쇄선)만 벽에 포함, 가는 파랑 지적선은 OPEN으로 제거
    blue = ((b > 170) & (r < 110) & (g < 110)).astype(np.uint8)
    blue_thick = cv2.morphologyEx(blue, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
    wall = np.maximum(red, blue_thick)
    # 쇄선 봉합: 대시 간격 + 시트 이음새(2m 공백 + 도곽선) → 55px 닫힘
    red = cv2.morphologyEx(wall, cv2.MORPH_CLOSE, np.ones((55, 55), np.uint8))
    # 외부에서 flood fill → 채워지지 않은(둘러싸인) 영역 = 내부 조각들(도로선·라벨로 분할됨)
    ff = red.copy(); h, w = ff.shape
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, mask, (0, 0), 1)
    inside = (ff == 0).astype(np.uint8)
    # 내부 조각을 크게 팽창해 이음새·도로선 너머로 잇고, 가장 큰 덩어리를 구역으로
    K = 61
    grown = cv2.dilate(inside, np.ones((K, K), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(grown, 8)
    cands = sorted([(stats[i, cv2.CC_STAT_AREA] * px * py, i) for i in range(1, n)], reverse=True)
    print("덩어리(팽창 상태, ㎡):", [round(a) for a, _ in cands[:4]])
    comp = (lab == cands[0][1]).astype(np.uint8)
    comp = cv2.erode(comp, np.ones((K, K), np.uint8))
    # CLOSE(55)로 벽이 양쪽 ~22px 두꺼워졌고 원래 선 반폭 ~5px → 내부를 27px 팽창하면 선 중심선
    comp = cv2.dilate(comp, np.ones((27, 27), np.uint8))
    comp = cv2.morphologyEx(comp, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))  # 이음새 잔여 봉합
    cs, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea).reshape(-1, 2)
    poly = Polygon([(ox + (u + .5) * px, oy - (v + .5) * py) for u, v in c]).buffer(0).simplify(0.3)
    print(f"지구단위계획구역 폴리곤: {poly.area:,.0f}㎡  (고시 {GOSI_AREA:,}  차이 {(poly.area-GOSI_AREA)/GOSI_AREA*100:+.2f}%)  꼭짓점 {len(poly.exterior.coords)}")
    t = Transformer.from_crs("EPSG:5187", "EPSG:4326", always_xy=True).transform
    for crs, tf, fn in [("5187", None, "gosi2026-8_zone_5187.geojson"), ("4326", t, "gosi2026-8_zone_4326.geojson")]:
        fc = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": dict(
            name="구경주역 지구단위계획구역", no=27, area_m2=round(poly.area, 1), gosi_area_m2=GOSI_AREA,
            source="경주시 고시 제2026-8호 지형도면고시도 11·12장 쇄선 추출"), "geometry": mapping(orient(stf(tf, poly) if tf else poly, 1.0))}]}
        if crs == "5187": fc["crs"] = {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::5187"}}
        (PROCESSED / fn).write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
    print("저장 gosi2026-8_zone_{5187,4326}.geojson")
    return 0


if __name__ == "__main__":
    sys.exit(main())
