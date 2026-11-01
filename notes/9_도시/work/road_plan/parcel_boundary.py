# -*- coding: utf-8 -*-
"""사용자 경계(v2)를 필지 경계로 맞춘 '매입 경계' v3.

규칙
 1. 필지 단위 편입: 필지 면적의 50% 이상이 v2 경계 안에 들어오면 필지 전체를 편입한다.
 2. 막다른 골목 편입: 1의 합집합 안으로 파고든 폭 8 m 이하 홈 중 도로 필지(지목 '도')에 해당하는
    부분은 함께 편입한다(필지 분할 가정). 구거(지목 '구')도 같다. 편입 필지만 접하는 골목이라 매입 후 내부 통로가 된다.
 3. 최외각 경계 = 1+2 합집합의 외곽선. 내부 구멍은 메운다(구멍 필지는 편입 목록에 추가).

입력  work/road_plan/site_v2_5187.geojson, archive/C_data/processed/parcels_lu_4326.geojson (V-World 연속지적도 2025)
출력  site_v3_parcel_{5187,4326}.geojson, site_v3_parcel_model.csv(v2 모형좌표), site_v3_parcels.csv, 시각화_필지경계_v3.png
"""
import csv, json, re
from pathlib import Path

import pyproj
from shapely.geometry import Polygon, mapping, shape, box
from shapely.ops import transform, unary_union

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SHARE_MIN = 0.5      # 규칙 1 임계
SLIT_W = 4.0         # 규칙 2 closing 반경(m) → 폭 8 m 이하 홈
SLIT_MIN_AREA = 10.0 # 규칙 2 최소 조각 면적(㎡)
SLIT_JM = ('도', '구')  # 규칙 2 대상 지목: 도로·구거
ZONES = ['제1종일반주거지역', '제2종일반주거지역', '제3종일반주거지역', '준주거지역',
         '일반상업지역', '근린상업지역', '자연녹지지역', '생산녹지지역']


def load_union(p):
    g = json.load(open(p, encoding='utf-8'))
    fs = g['features'] if 'features' in g else [g]
    return unary_union([shape(f['geometry']) for f in fs])


def main():
    v2 = load_union(HERE / 'site_v2_5187.geojson')
    to5187 = pyproj.Transformer.from_crs(4326, 5187, always_xy=True).transform
    to4326 = pyproj.Transformer.from_crs(5187, 4326, always_xy=True).transform

    # 필지 읽기 (4326 → 5187 즉시 변환)
    src = json.load(open(ROOT / 'archive/C_data/processed/parcels_lu_4326.geojson', encoding='utf-8'))
    P = []
    for f in src['features']:
        s = transform(to5187, shape(f['geometry']))
        if not s.is_valid:
            s = s.buffer(0)
        if not s.intersects(v2.buffer(60)):
            continue
        p = f['properties']
        ins = s.intersection(v2).area
        zone = next((z for z in ZONES if z in p['lu_list']), '기타')
        P.append(dict(pnu=p['pnu'], addr=p['addr'].replace('경상북도 경주시 ', ''),
                      jm=re.sub(r'[\d\-\s]', '', p['jibun']), geom=s, area=s.area, inside=ins,
                      share=ins / s.area, zone=zone, jiga=float(p['jiga'] or 0), bldg=int(p['bldg_n'] or 0)))

    # 규칙 1
    for p in P:
        p['how'] = '필지전체' if p['share'] >= SHARE_MIN else ''
    base = unary_union([p['geom'] for p in P if p['how']]).buffer(0.05).buffer(-0.05)

    # 규칙 2: closing 으로 생긴 조각 중 도로 필지에 걸린 것만
    closed = base.buffer(SLIT_W, join_style=2).buffer(-SLIT_W, join_style=2)
    gap = closed.difference(base)
    slits = []
    for p in P:
        if p['how'] or p['jm'] not in SLIT_JM:
            continue
        piece = p['geom'].intersection(gap)
        if piece.area >= SLIT_MIN_AREA:
            p['how'] = '골목분할'
            p['piece'] = piece
            slits.append(piece)
            c = piece.centroid
            print(f"  골목분할 {p['addr']} {p['jm']} 조각 {piece.area:.0f}㎡ @({c.x:.0f},{c.y:.0f})")
    merged = unary_union([base] + slits).buffer(0.05).buffer(-0.05)

    # 규칙 3: 외곽선, 구멍 메움
    polys = list(getattr(merged, 'geoms', [merged]))
    polys.sort(key=lambda g: -g.area)
    outer = Polygon(polys[0].exterior).simplify(0.01)
    for p in P:
        if not p['how'] and p['geom'].representative_point().within(outer):
            p['how'] = '구멍메움'

    inc = [p for p in P if p['how']]
    print(f'v2 {v2.area:,.0f}㎡ → v3 {outer.area:,.0f}㎡ (조각 {len(polys)}개, 꼭짓점 {len(outer.exterior.coords)-1})')
    print(f'편입 필지 {len(inc)} (필지전체 {sum(p["how"]=="필지전체" for p in inc)}, '
          f'골목분할 {sum(p["how"]=="골목분할" for p in inc)}, 구멍메움 {sum(p["how"]=="구멍메움" for p in inc)})')
    add = outer.difference(v2).area
    drop = v2.difference(outer).area
    print(f'v2 대비 늘어난 면적 {add:,.0f}㎡ / 빠진 면적 {drop:,.0f}㎡')

    # 저장: 5187 / 4326
    meta = dict(name='구경주역 매입경계 v3 (필지 기준)', area_m2=round(outer.area, 1), n_parcels=len(inc),
                rule=f'필지 {int(SHARE_MIN*100)}% 이상 편입 + 막다른 골목(폭≤{2*SLIT_W:.0f}m) 분할 편입 + 구멍 메움',
                source='V-World 연속지적도(LP_PA_CBND_BUBUN, 2025) — 법적 경계 아님', base='site_v2_5187.geojson')
    fc = lambda g, crs: {'type': 'FeatureCollection',
                         'crs': {'type': 'name', 'properties': {'name': f'urn:ogc:def:crs:EPSG::{crs}'}},
                         'features': [{'type': 'Feature', 'properties': meta, 'geometry': mapping(g)}]}
    json.dump(fc(outer, 5187), open(HERE / 'site_v3_parcel_5187.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(fc(transform(to4326, outer), 4326), open(HERE / 'site_v3_parcel_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)

    # v2 모형좌표 (= C + 0.5*(5179 − C), 5179 = 아핀(5187)), z 는 v2 경계 레이어와 같은 688.9
    t = json.load(open(HERE / 'v2_transform.json'))
    ax, ay, C, S = t['ax'], t['ay'], t['C'], t['scale']
    def to_model(x, y):
        X = ax[0] * x + ax[1] * y + ax[2]
        Y = ay[0] * x + ay[1] * y + ay[2]
        return C[0] + S * (X - C[0]), C[1] + S * (Y - C[1])
    with open(HERE / 'site_v3_parcel_model.csv', 'w', newline='', encoding='utf-8') as fo:
        w = csv.writer(fo)
        for x, y in outer.exterior.coords:
            mx, my = to_model(x, y)
            w.writerow([round(mx, 4), round(my, 4), 688.9])

    # 라이노 가져오기용 3dm: 최종콘타모델_v2 에 Import 하면 그대로 겹친다
    import rhino3dm as r3
    m = r3.File3dm()
    m.Settings.ModelUnitSystem = r3.UnitSystem.Meters
    def add_layer(name, rgb, parent=None):
        L = r3.Layer()
        L.Name = name
        L.Color = (*rgb, 255)
        if parent is not None:
            L.ParentLayerId = m.Layers.FindIndex(parent).Id
        return m.Layers.Add(L)
    top = add_layer('필지기준 매입경계 v3', (200, 16, 46))
    li_b = add_layer('경계', (200, 16, 46), top)
    li_p = add_layer('편입필지', (120, 120, 120), top)
    def add_ring(coords, li, name):
        pl = r3.Polyline([r3.Point3d(*to_model(x, y), 688.9) for x, y in coords])
        a = r3.ObjectAttributes()
        a.LayerIndex = li
        a.Name = name
        m.Objects.AddPolyline(pl, a)
    add_ring(outer.exterior.coords, li_b, f'v3 {outer.area:,.0f}㎡ (실면적)')
    for p in P:
        if not p['how']:
            continue
        g = p['piece'] if p['how'] == '골목분할' else p['geom']
        for poly in getattr(g, 'geoms', [g]):
            if poly.geom_type == 'Polygon':
                add_ring(poly.exterior.coords, li_p, f"{p['addr']} {p['jm']} {p['how']}")
    m.Write(str(HERE / 'site_v3_parcel_model.3dm'), 8)

    # 필지 목록 (편입 + 경계 판단 필지)
    with open(HERE / 'site_v3_parcels.csv', 'w', newline='', encoding='utf-8-sig') as fo:
        w = csv.writer(fo)
        w.writerow(['pnu', '주소', '지목', '필지면적_m2', 'v2안_면적_m2', 'v2안_비율', '편입', '편입면적_m2',
                    '용도지역', '공시지가_원m2', '공시지가액_억원', '건축물'])
        for p in sorted(P, key=lambda p: (not p['how'], p['addr'])):
            if not p['how'] and p['inside'] < 1:
                continue
            a = p['piece'].area if p['how'] == '골목분할' else (p['area'] if p['how'] else 0)
            val = 0 if p['how'] == '골목분할' else a * p['jiga'] / 1e8
            w.writerow([p['pnu'], p['addr'], p['jm'], round(p['area'], 1), round(p['inside'], 1), round(p['share'], 3),
                        p['how'] or '제외', round(a, 1), p['zone'], int(p['jiga']), round(val, 3), p['bldg']])

    # 요약 통계
    def tally(key):
        d = {}
        for p in inc:
            a = p['piece'].area if p['how'] == '골목분할' else p['area']
            d.setdefault(key(p), [0, 0, 0.0])
            d[key(p)][0] += 1
            d[key(p)][1] += a
            d[key(p)][2] += 0 if p['how'] == '골목분할' else a * p['jiga'] / 1e8
        return d
    print('지목별', {k: (n, round(a), round(v, 1)) for k, (n, a, v) in sorted(tally(lambda p: p['jm']).items(), key=lambda kv: -kv[1][1])})
    print('용도지역별', {k: (n, round(a), round(v, 1)) for k, (n, a, v) in sorted(tally(lambda p: p['zone']).items(), key=lambda kv: -kv[1][1])})
    tot = sum(v for _, _, v in tally(lambda p: 1).values())
    print(f'공시지가액 합계 {tot:,.1f}억 원 / 건축물 있는 필지 {sum(p["bldg"] > 0 for p in inc)}')
    border = [p for p in P if 0.3 <= p['share'] < 0.7 and p['inside'] >= 10]
    print('경계 판단 필지 (v2안 비율 0.3–0.7):')
    for p in sorted(border, key=lambda p: -p['share']):
        print(f"  {p['addr']} {p['jm']} {p['area']:.0f}㎡ 안 {p['inside']:.0f}㎡ ({p['share']:.2f}) → {p['how'] or '제외'}")

    # 그림
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    plt.rcParams['font.family'] = 'Malgun Gothic'
    cm = {'철': '#d9c49a', '대': '#f2a07b', '전': '#b8e186', '잡': '#e3e38a', '창': '#cdb4f5', '천': '#9ecae1', '구': '#9ecae1', '도': '#c8c8c8'}
    fig, axs = plt.subplots(1, 2, figsize=(15, 15), gridspec_kw={'width_ratios': [1, 1]})
    b = outer.union(v2).bounds
    for k, axx in enumerate(axs):
        for p in P:
            for poly in getattr(p['geom'], 'geoms', [p['geom']]):
                x, y = poly.exterior.xy
                on = bool(p['how']) and p['how'] != '골목분할'
                axx.fill(x, y, color=cm.get(p['jm'], '#eee') if on else '#f5f5f5', lw=0.25, ec='#777', alpha=1 if on else 0.6)
        for s in slits:
            for poly in getattr(s, 'geoms', [s]):
                if poly.geom_type != 'Polygon':
                    continue
                x, y = poly.exterior.xy
                axx.fill(x, y, color='#888', lw=0)
        if k == 1:
            for g, col in ((outer.difference(v2), '#d7301f'), (v2.difference(outer), '#2b8cbe')):
                for poly in getattr(g, 'geoms', [g]):
                    if poly.geom_type == 'Polygon' and poly.area > 1:
                        x, y = poly.exterior.xy
                        axx.fill(x, y, color=col, alpha=0.75, lw=0)
        x, y = v2.exterior.xy
        axx.plot(x, y, color='#1f4fd1', ls='--', lw=1.3)
        x, y = outer.exterior.xy
        axx.plot(x, y, color='#c8102e', lw=2.2)
        axx.set_xlim(b[0] - 40, b[2] + 40); axx.set_ylim(b[1] - 40, b[3] + 40)
        axx.set_aspect('equal'); axx.set_xticks([]); axx.set_yticks([])
    axs[0].set_title(f'편입 필지 {len(inc)}개 — 지목별', fontsize=13)
    axs[1].set_title(f'v2 대비 증감  +{add:,.0f}㎡ / -{drop:,.0f}㎡', fontsize=13)
    axs[0].legend(handles=[Patch(color=cm[k], label=l) for k, l in
                           (('철', '철도용지'), ('대', '대지'), ('전', '전'), ('잡', '잡종지'), ('창', '창고용지'), ('천', '하천·구거'), ('도', '도로'))]
                  + [Patch(color='#888', label='골목 분할 편입')]
                  + [Line2D([], [], color='#1f4fd1', ls='--', label=f'v2 사용자 경계 {v2.area:,.0f}㎡'),
                     Line2D([], [], color='#c8102e', lw=2, label=f'v3 필지 경계 {outer.area:,.0f}㎡')],
                  loc='lower right', fontsize=9, framealpha=0.95)
    axs[1].legend(handles=[Patch(color='#d7301f', label='필지 때문에 늘어난 땅'), Patch(color='#2b8cbe', label='필지 때문에 빠진 땅')],
                  loc='lower right', fontsize=9, framealpha=0.95)
    plt.rcParams['axes.unicode_minus'] = False
    plt.suptitle('구경주역 매입 경계 v3 — 사용자 경계를 필지선에 맞춤 (V-World 연속지적도 2025, EPSG:5187)', fontsize=14, y=0.995)
    plt.tight_layout()
    plt.savefig(HERE / '시각화_필지경계_v3.png', dpi=130, bbox_inches='tight')


if __name__ == '__main__':
    main()
