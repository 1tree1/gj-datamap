"""소상공인365 유동인구 재추출용 분석 구역 3개(+구역 자체) 생성.

A. 황오동 원도심 활성화구역 — 2024 모니터링(공공도시 2025.09)이 쓴 SGIS 100m 격자 32셀(국가지점번호 '마마' 블록, EPSG:5179)
B. 경주역동편(행복황촌) 활성화구역 — 2020 활성화계획 위치도(그림 1.4)를 통제점 5개로 어파인 좌표등록해 디지타이징 (근사)
C. 지구단위계획구역(고시 2026-8호) + 300m 버퍼
D. 지구단위계획구역 자체 (기준선)

출력: archive/C_data/processed/footfall_areas_{5187,4326}.geojson, 90_derived/footfall_areas_5181.json (소상공인365 입력용)
"""
import json, numpy as np
from pathlib import Path
from shapely.geometry import Polygon, shape, mapping
from shapely.ops import unary_union, transform
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'archive/C_data/processed'
DERIV = ROOT / 'archive/90_derived'

T5179_5187 = Transformer.from_crs(5179, 5187, always_xy=True).transform
T4326_5187 = Transformer.from_crs(4326, 5187, always_xy=True).transform
T5187_4326 = Transformer.from_crs(5187, 4326, always_xy=True).transform
T5187_5181 = Transformer.from_crs(5187, 5181, always_xy=True).transform

# ---------- A. 황오동 격자 32셀 (마마 블록: X 1,100,000~ / Y 1,700,000~, 셀 100m)
codes = ['마마548622','마마548623','마마548624','마마548625','마마548626','마마549618','마마549619','마마549620','마마549621',
         '마마549622','마마549623','마마549624','마마549625','마마549626','마마550618','마마550619','마마550620','마마550621',
         '마마550622','마마550623','마마550624','마마550625','마마550626','마마551618','마마551619','마마551620','마마551621',
         '마마551622','마마551623','마마551624','마마551625','마마551626']
cells = []
for c in codes:
    ex, ny = int(c[2:5]), int(c[5:8])
    x0, y0 = 1_100_000 + ex * 100, 1_700_000 + ny * 100
    cells.append(Polygon([(x0, y0), (x0 + 100, y0), (x0 + 100, y0 + 100), (x0, y0 + 100)]))
A = transform(T5179_5187, unary_union(cells))

# ---------- B. 행복황촌 — 이미지 픽셀 → 5187 어파인 (통제점: 카카오 로컬 키워드 검색 좌표)
ctrl_px = np.array([[143, 15], [218, 393], [106, 407], [356, 547]], float)  # 황오동행정복지센터 제외(2025 이전으로 위치 불일치)
ctrl_ll = [(129.2166944688556, 35.8507058566913),
           (129.21793175706665, 35.84442707332487), (129.2157617760532, 35.84419500875021),
           (129.220657906986, 35.8418636933392)]
ctrl_xy = np.array([T4326_5187(*p) for p in ctrl_ll])
Amat = np.c_[ctrl_px, np.ones(len(ctrl_px))]
coef_x, *_ = np.linalg.lstsq(Amat, ctrl_xy[:, 0], rcond=None)
coef_y, *_ = np.linalg.lstsq(Amat, ctrl_xy[:, 1], rcond=None)
res = np.c_[Amat @ coef_x - ctrl_xy[:, 0], Amat @ coef_y - ctrl_xy[:, 1]]
rmse = float(np.sqrt((res ** 2).sum(1).mean()))
verts_px = [(257, 58), (292, 58), (441, 188), (437, 345), (437, 400), (405, 400), (405, 440), (430, 440), (430, 520),
            (433, 520), (433, 560), (392, 560), (392, 622), (248, 622), (250, 556), (260, 478), (345, 478), (348, 280),
            (338, 205), (338, 140), (262, 140)]
P = np.c_[np.array(verts_px, float), np.ones(len(verts_px))]
B_raw = Polygon(np.c_[P @ coef_x, P @ coef_y])
# 고시면적 164,500㎡에 맞춰 내측 오프셋 보정(선 두께·외곽 디지타이징 편향 제거)
lo, hi = 0.0, 40.0
for _ in range(40):
    d = (lo + hi) / 2
    if B_raw.buffer(-d, join_style='mitre').area > 164_500: lo = d
    else: hi = d
B_inset = (lo + hi) / 2
B = B_raw.buffer(-B_inset, join_style='mitre').simplify(1)

# ---------- C/D. 구역 + 300m
zone = shape(json.load(open(PROC / 'gosi2026-8_zone_5187.geojson', encoding='utf-8'))['features'][0]['geometry'])
D = zone.simplify(2)
C = zone.buffer(300, join_style='round').simplify(3)

areas = {
    'A_hwango_grid32': A, 'B_haengbok_hwangchon_digitized': B, 'C_zone_buffer300': C, 'D_zone': D,
}
meta = {
    'A_hwango_grid32': 'SGIS 100m 격자 32셀 (2024 황오동 모니터링 보고서 인쇄쪽 9), 국가지점번호 마마 블록 → EPSG:5179',
    'B_haengbok_hwangchon_digitized': f'2020 활성화계획 그림1.4 디지타이징, 통제점 4(카카오 로컬), RMSE {rmse:.1f} m, 원 디지타이징 {B_raw.area:,.0f}㎡ → 고시면적 164,500㎡에 맞춰 {B_inset:.1f} m 내측 오프셋',
    'C_zone_buffer300': '고시 2026-8호 구역(C-004) + 300m (건물에너지 C-011과 같은 정의)',
    'D_zone': '고시 2026-8호 구역(C-004) 자체',
}
print(f'B 통제점 RMSE {rmse:.1f} m, 잔차(m): {np.round(res,1).tolist()}')
for k, g in areas.items():
    print(f'{k}: {g.area:,.0f} ㎡, vertices {len(mapping(g)["coordinates"][0]) if g.geom_type=="Polygon" else "multi"}')

def fc(tr):
    feats = []
    for k, g in areas.items():
        gg = transform(tr, g) if tr else g
        feats.append({'type': 'Feature', 'properties': {'id': k, 'area_m2': round(g.area), 'note': meta[k]}, 'geometry': mapping(gg)})
    return {'type': 'FeatureCollection', 'features': feats}

json.dump(fc(None), open(PROC / 'footfall_areas_5187.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(fc(T5187_4326), open(PROC / 'footfall_areas_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)

# 소상공인365 입력: 5181 정수 좌표 + 위경도 + 중심
out = {}
for k, g in areas.items():
    if g.geom_type != 'Polygon':
        g = max(g.geoms, key=lambda p: p.area)
    ring = list(g.exterior.coords)
    p5181 = [tuple(int(round(v)) for v in T5187_5181(x, y)) for x, y in ring]
    ll = [T5187_4326(x, y) for x, y in ring]
    cx, cy = g.centroid.x, g.centroid.y
    out[k] = {'area_m2': round(g.area), 'note': meta[k], 'path5181': p5181, 'lonlat': ll,
              'center_lonlat': T5187_4326(cx, cy), 'center5181': [int(round(v)) for v in T5187_5181(cx, cy)]}
json.dump(out, open(DERIV / 'footfall_areas_5181.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('written')
