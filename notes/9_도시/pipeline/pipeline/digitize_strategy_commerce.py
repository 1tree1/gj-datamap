"""경주시 도시재생전략계획(변경, 2022.01) 인쇄쪽 42 「경주 중심지 상권 분석도」 — 항공사진 위 상권 4개 폴리곤을 디지타이징.
방법: 페이지 300dpi 렌더 → 그림 영역 자동 크롭 → 라벨 핀(흰 점) 6개 픽셀 검출 ↔ V-World 장소검색 좌표로 아핀 최소제곱(EPSG:5187)
      → 색상 마스크(빨강·파랑·보라·초록) 최대 성분 외곽 → 좌표 변환 → 4326.
정확도: GCP 잔차 20~65m (그림 자체가 개략도). 법정 경계가 아니라 계획서의 분석 구역이다.
출력: processed/commerce_strat_4326.geojson · scratch 검증 이미지"""
import sys, json
import numpy as np, cv2, fitz
from shapely.geometry import Polygon, mapping
from shapely.geometry.polygon import orient
from pyproj import Transformer
from _common import ROOT, PROCESSED, save

PDF = ROOT / "22-0124) 경주시 도시재생전략계획 최종보고서.pdf"
PAGE = 51  # 0-based → 인쇄쪽 42
# 라벨 핀 픽셀(그림 크롭 기준, 300dpi) ↔ 실좌표 (V-World 장소검색 2026-09-21)
GCP = {"성동시장": ((956, 692), (129.21677, 35.84500)), "중앙시장": ((631, 758), (129.20627, 35.84408)), "고속버스터미널": ((541, 966), (129.20360, 35.83868)),
       "황남시장": ((777, 1086), (129.2105, 35.8362)), "황리단길": ((751, 1015), (129.2099, 35.8374)), "문화의거리": ((829, 798), (129.21352, 35.84254))}
ZONES = {
    "red":    ("① 경주중심상권", "center", (700, 850), "경주시 원도심에 형성된 최대 규모 상권. 시민 주거생활용 시내 상권과 관광객 유치용 도심 관광인프라가 복합된 상업지역", "경주역·전통시장·봉황로 문화의거리·경주역 일원"),
    "purple": ("② 관광상권", "tour", (720, 1130), "관광객이 가장 많이 이용하는 황리단길 중심 상권. 젊은 층 선호, 음식점업과 게스트하우스 등 숙박시설 밀집", "황리단길·황남시장·쌈밥거리 일원"),
    "blue":   ("③ 도심배후상권", "back", (600, 300), "동국대 구(舊)대학로 거리의 도심 배후상권, 근린생활권. 기존 주민 유출로 외국인 근로자 이용이 높은 지역", "상권 형성지역 일원(성건동)"),
    "green":  ("④ 동천근린상권", "nbhd", (1190, 300), "경주시청·주변 업무시설 근로자와 인근 거주민이 이용하는 근린상업지역. 음식점업·모텔 중심 숙박업 비중 높음", "동천시장"),
}
SRC = "경주시 도시재생 전략계획(변경) 2022.01 기초조사 인쇄쪽 42 「경주 중심지 상권 분석도」 디지타이징 (T1 도면, 개략도 · GCP 잔차 ≤65m)"


def crop_figure(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY); dark = gray < 225
    rows = np.where(dark.mean(1) > 0.3)[0]; segs = []; s = prev = rows[0]
    for r in rows[1:]:
        if r > prev + 3: segs.append((s, prev)); s = r
        prev = r
    segs.append((s, prev)); y1, y2 = max(segs, key=lambda t: t[1] - t[0])
    cols = np.where(dark[y1:y2].mean(0) > 0.3)[0]; x1, x2 = cols.min(), cols.max()
    return img[y1:y2 + 1, x1:x2 + 1].copy(), (x1, y1)


def refine_marker(fig, x, y, r=45):
    hsv = cv2.cvtColor(fig[y - r:y + r, x - r:x + r], cv2.COLOR_RGB2HSV)
    white = ((hsv[:, :, 1] < 60) & (hsv[:, :, 2] > 215)).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(white, 8); best = None
    for i in range(1, n):
        bx, by, bw, bh, a = st[i]
        if 25 < a < 500 and 0.6 < bw / max(bh, 1) < 1.6:
            d = np.hypot(cen[i][0] - r, cen[i][1] - r)
            if best is None or d < best[0]: best = (d, cen[i][0] + x - r, cen[i][1] + y - r)
    return (best[1], best[2]) if best else (x, y)


def main():
    doc = fitz.open(PDF); pix = doc[PAGE].get_pixmap(dpi=300)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3].copy()
    fig, off = crop_figure(img); print("그림", fig.shape, "오프셋", off)
    to87 = Transformer.from_crs(4326, 5187, always_xy=True).transform; to26 = Transformer.from_crs(5187, 4326, always_xy=True).transform
    A, b = [], []; pts = {}
    for nm, ((px, py), (lon, lat)) in GCP.items():
        px, py = refine_marker(fig, px, py); pts[nm] = (px, py); X, Y = to87(lon, lat)
        A += [[px, py, 1, 0, 0, 0], [0, 0, 0, px, py, 1]]; b += [X, Y]
    M = np.linalg.lstsq(np.array(A, float), np.array(b, float), rcond=None)[0]
    tf = lambda px, py: (M[0] * px + M[1] * py + M[2], M[3] * px + M[4] * py + M[5])
    res = {nm: round(float(np.hypot(*(np.array(tf(*pts[nm])) - np.array(to87(*GCP[nm][1]))))), 1) for nm in GCP}
    print("GCP 잔차(m):", res, "| 축척 m/px", round(float(np.hypot(M[0], M[3])), 3))
    hsv = cv2.cvtColor(fig, cv2.COLOR_RGB2HSV); Hh, S, V = [hsv[:, :, i].astype(int) for i in range(3)]
    masks = {"red": ((Hh <= 14) | (Hh >= 172)) & (S > 70) & (V > 60), "blue": (Hh >= 92) & (Hh <= 108) & (S > 35) & (V > 150),
             "purple": (Hh >= 118) & (Hh <= 140) & (S > 25) & (V > 50) & (V < 200), "green": (Hh >= 62) & (Hh <= 88) & (S > 80) & (V > 90)}
    feats = []; vis = fig.copy()
    for key, (name, cls, seed, desc, anchors) in ZONES.items():
        m = masks[key].astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)); m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((11, 11), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8); li = lab[seed[1], seed[0]] or (1 + int(np.argmax(st[1:, 4])))
        comp = cv2.morphologyEx((lab == li).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
        cs, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = cv2.approxPolyDP(max(cs, key=cv2.contourArea), 2.5, True)
        cv2.polylines(vis, [c], True, (255, 255, 0), 3)
        poly = Polygon([tf(float(x), float(y)) for x, y in c.reshape(-1, 2)]).buffer(0).simplify(3)
        g26 = orient(Polygon([to26(x, y) for x, y in poly.exterior.coords]), 1.0)
        feats.append({"type": "Feature", "geometry": mapping(g26), "properties": {"name": name, "cls": cls, "desc": desc, "anchors": anchors, "area_ha": round(poly.area / 1e4, 1), "lbl": name, "source": SRC, "gcp_resid_m": max(res.values())}})
        print(f"  {name:<10} {poly.area/1e4:6.1f}ha  꼭짓점 {len(c)}")
    save({"type": "FeatureCollection", "features": feats}, PROCESSED / "commerce_strat_4326.geojson")
    ok, buf = cv2.imencode(".png", cv2.cvtColor(cv2.resize(vis, None, fx=0.6, fy=0.6), cv2.COLOR_RGB2BGR))
    (PROCESSED / "commerce_strat_check.png").write_bytes(buf.tobytes())
    return 0


if __name__ == "__main__":
    sys.exit(main())
