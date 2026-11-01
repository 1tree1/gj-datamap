"""지방행정인허가(localdata) 경주시 숙박 3업종 → 구역별 인허가·폐업·재고 시계열.

입력: archive/C_data/raw/localdata_gyeongju/localdata_{svc}_5050000_YYYYMMDD.csv
      (file.localdata.go.kr/file/download/{svc}/info?orgCode=5050000, cp949, 좌표 EPSG:5174)
      svc = foreigner_city_homestays(외국인관광 도시민박업) / hanok_experience(한옥체험업) / lodgings(숙박업)
구역: archive/C_data/processed/footfall_areas_5187.geojson (A~E) + 시청500m/성동시장200m/황리단길300m 원
      — build_localdata_turnover.py, 소상공인365 재추출(C-027~029)과 같은 정의
대조: B-007 행복황촌 협동조합 발표자료 p.16 숙소 21개 명단 / 소진공 상가 2026.03(C-006)
출력: archive/C_data/processed/lodging_permits_5187.geojson   (사업장 점, 구역 태그)
      archive/90_derived/lodging_permits_stock.csv              (구역×업종×기준일 영업중 재고·누적 인허가·폐업)
      archive/90_derived/lodging_permits_yearly.csv             (구역×업종×연도 인허가·폐업)
      archive/90_derived/hwangchon_homestay_list.csv            (행복황촌 구역 사업장 명단 + 대조 표시)
      archive/C_data/processed/lodging_permits_web_4326.geojson (웹 전용: S2 창 도시민박업·한옥체험업 → gj-datamap 레이어)
      archive/C_data/processed/lodging_report.json              (웹 전용: 리포트 카드 수치 → gj-datamap/scripts/sync_lodging.py)
"""
import csv, io, json, re, sys, calendar
from pathlib import Path
from collections import defaultdict, Counter
from shapely.geometry import shape, Point
from pyproj import Transformer
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, RAW, PROCESSED, S2_BBOX

SRC = RAW / 'localdata_gyeongju'
DERIV = ROOT / 'archive/90_derived'
SNAP = '20261001'
SVCS = {'foreigner_city_homestays': '외국인관광도시민박업', 'hanok_experience': '한옥체험업', 'lodgings': '숙박업'}
T5174_5187 = Transformer.from_crs(5174, 5187, always_xy=True).transform
T4326_5187 = Transformer.from_crs(4326, 5187, always_xy=True).transform

# ---------- 구역 (build_localdata_turnover.py와 동일 정의)
fc = json.load(open(PROCESSED / 'footfall_areas_5187.geojson', encoding='utf-8'))
AREAS = {f['properties']['id']: shape(f['geometry']) for f in fc['features']}
def circle(lon, lat, r): return Point(T4326_5187(lon, lat)).buffer(r)
AREAS['F_cityhall_r500'] = circle(129.2247816627553, 35.85621665939485, 500)
AREAS['G_seongdong_market_r200'] = circle(129.216354826459, 35.84534371000188, 200)
AREAS['H_hwangridan_r300'] = circle(129.2098, 35.8384, 300)
B_ID = 'B_haengbok_hwangchon_digitized'
# B 경계는 위치도 디지타이징 근사(±20m, C-028) → 경계 민감도용 ±20m 버퍼
B_IN, B_OUT = AREAS[B_ID].buffer(-20), AREAS[B_ID].buffer(20)

# ---------- 대조 명단
# B-007 p.16 「행복황촌 마을호텔 숙소 현황」 25년 10월 현재 21개 (공백 제거 후 비교)
B007 = ['행복꿈자리', '게스트하우스희', '경주호가', '넥스트도어', '모모이황촌', '블루플래닛', '스테이경주182-6', '스테이마음', '스테이시in',
        '스테이황촌', '호경가', '호텔프프', '황오다락', '황오여관', '스테이류', '스테이눕', '소여정', '여진여몽', '황오아담', '달스테이인황촌', '해야스테이']
def norm(s): return re.sub(r'[\s,\.()]', '', (s or '')).replace('스테이희', '게스트하우스희').replace('스테이여진여몽', '여진여몽')

def read(svc):
    p = SRC / f'localdata_{svc}_5050000_{SNAP}.csv'
    return list(csv.DictReader(io.StringIO(p.read_bytes().decode('cp949'))))

def ymd(s):
    s = (s or '').strip()[:10]
    return s if re.match(r'\d{4}-\d{2}-\d{2}', s) else ''

def main():
    # 소진공 상가 2026.03 상호 (구역 B 안 숙박) — 대조용
    sbiz = json.load(open(PROCESSED / 'stores_merged_4326.geojson', encoding='utf-8'))
    T4326 = Transformer.from_crs(4326, 5187, always_xy=True).transform
    sbiz_b = {norm(f['properties']['bizesNm']) for f in sbiz['features']
              if f['geometry'] and f['properties'].get('indsLclsNm') == '숙박'
              and AREAS[B_ID].contains(Point(T4326(*f['geometry']['coordinates'])))}

    feats, n_noxy = [], defaultdict(int)
    for svc, label in SVCS.items():
        for r in read(svc):
            x, y = (r.get('좌표정보(X)') or '').strip(), (r.get('좌표정보(Y)') or '').strip()
            addr = (r.get('도로명주소') or '').strip() or (r.get('지번주소') or '').strip()
            dong = (re.search(r'\((\S+동)', r.get('도로명주소') or '') or re.search(r'경주시 (\S+[동읍면])', r.get('지번주소') or '') or [None, ''])[1]
            props = {'svc': label, 'mng_no': r['관리번호'], 'name': (r.get('사업장명') or '').strip(), 'opened': ymd(r.get('인허가일자')),
                     'closed': ymd(r.get('폐업일자')) or ymd(r.get('인허가취소일자')), 'status': r.get('영업상태명', ''),
                     'detail': r.get('상세영업상태명', ''), 'rooms': (r.get('객실수') or '').strip(),
                     'upt': (r.get('업태구분명') or '').strip(), 'bldg_use': (r.get('건물용도명') or '').strip(),
                     'dong': dong, 'addr': addr[:70], 'areas': '', 'b_edge': ''}
            # 폐업·취소인데 날짜가 없으면 최종수정시점으로 대체하지 않는다 — 재고 계산에서 제외 표시
            if props['status'] != '영업/정상' and not props['closed']: props['closed'] = 'unknown'
            if not x or not y:
                n_noxy[label] += 1; geom = None
            else:
                pt = Point(T5174_5187(float(x), float(y)))
                geom = {'type': 'Point', 'coordinates': [round(pt.x, 1), round(pt.y, 1)]}
                props['areas'] = ';'.join(k for k, a in AREAS.items() if a.contains(pt))
                if B_OUT.contains(pt) and not B_IN.contains(pt): props['b_edge'] = 'Y'
            feats.append({'type': 'Feature', 'geometry': geom, 'properties': props})
    json.dump({'type': 'FeatureCollection', 'name': 'lodging_permits_5187',
               'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:EPSG::5187'}}, 'features': feats},
              open(PROCESSED / 'lodging_permits_5187.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
    print('좌표 없음', dict(n_noxy), '/ 저장', len(feats))

    # ---------- 재고 시계열
    keys = list(AREAS) + ['황오동', '성동동', '황남동', 'GJ_경주시']
    def tags(p):
        t = p['areas'].split(';') if p['areas'] else []
        if p['dong'] in ('황오동', '성동동', '황남동'): t.append(p['dong'])
        return t + ['GJ_경주시']
    dates = ['2015-12-31', '2018-12-31', '2020-12-31', '2021-12-31', '2022-12-31', '2023-12-31',
             '2024-03-11', '2024-12-31', '2025-10-31', '2025-12-31', '2026-06-30', '2026-09-30']
    stock_rows, yearly = [], defaultdict(lambda: [0, 0])
    for k in keys:
        for label in SVCS.values():
            fs = [f['properties'] for f in feats if f['properties']['svc'] == label and k in tags(f['properties'])]
            for d in dates:
                live = [p for p in fs if p['opened'] and p['opened'] <= d and (not p['closed'] or (p['closed'] != 'unknown' and p['closed'] > d))]
                unk = sum(1 for p in fs if p['closed'] == 'unknown' and p['opened'] and p['opened'] <= d)
                stock_rows.append([k, label, d, len(live), sum(1 for p in fs if p['opened'] and p['opened'] <= d),
                                   sum(1 for p in fs if p['closed'] and p['closed'] != 'unknown' and p['closed'] <= d), unk])
            for p in fs:
                if p['opened']: yearly[(k, label, int(p['opened'][:4]))][0] += 1
                if p['closed'] and p['closed'] != 'unknown': yearly[(k, label, int(p['closed'][:4]))][1] += 1
    with open(DERIV / 'lodging_permits_stock.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['area_id', 'svc', 'date', 'stock_open', 'cum_permits', 'cum_closed', 'closed_date_unknown']); w.writerows(stock_rows)
    with open(DERIV / 'lodging_permits_yearly.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['area_id', 'svc', 'year', 'permits', 'closures'])
        for (k, label, y), (o, c) in sorted(yearly.items()): w.writerow([k, label, y, o, c])

    # ---------- 행복황촌 명단 + 대조
    b007_seen = set()
    with open(DERIV / 'hwangchon_homestay_list.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['svc', 'name', 'opened', 'closed', 'status', 'rooms', 'addr', 'b_edge_20m', 'in_b007_list', 'in_sbiz_202603'])
        rows = [f_['properties'] for f_ in feats if B_ID in f_['properties']['areas'].split(';') and f_['properties']['svc'] != '숙박업']
        for p in sorted(rows, key=lambda p: (p['opened'], p['name'])):
            n = norm(p['name']); hit = next((b for b in B007 if norm(b) == n), '')
            if hit: b007_seen.add(hit)
            w.writerow([p['svc'], p['name'], p['opened'], p['closed'], p['status'], p['rooms'], p['addr'], p['b_edge'], 'Y' if hit else '', 'Y' if n in sbiz_b else ''])
    print('B-007 명단 중 localdata 구역 B에서 못 찾은 것:', [b for b in B007 if b not in b007_seen])

    for k in [B_ID, 'A_hwango_grid32', 'C_zone_buffer300', 'H_hwangridan_r300', 'GJ_경주시']:
        print(k, {lab: [r[3] for r in stock_rows if r[0] == k and r[1] == lab] for lab in SVCS.values()})
    print('dates', dates)
    web_outputs(feats)

def web_outputs(feats):
    """웹 전용 출력 (EPSG:4326) — 처리본은 위의 5187 파일이 정본."""
    T5187_4326 = Transformer.from_crs(5187, 4326, always_xy=True).transform
    HS = ('외국인관광도시민박업', '한옥체험업')
    def live(p, d): return bool(p['opened']) and p['opened'] <= d and (not p['closed'] or p['closed'] > d)
    def in_b(f, poly=AREAS[B_ID]): return f['geometry'] is not None and poly.contains(Point(f['geometry']['coordinates']))
    pts = []
    for f in feats:
        p = f['properties']
        if p['svc'] not in HS or not f['geometry']: continue
        lon, lat = T5187_4326(*f['geometry']['coordinates'])
        if not (S2_BBOX[0] <= lon <= S2_BBOX[2] and S2_BBOX[1] <= lat <= S2_BBOX[3]): continue
        period = '폐업' if p['closed'] else ('2023년 이전' if p['opened'] < '2024' else p['opened'][:4])
        pts.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [round(lon, 6), round(lat, 6)]},
                    'properties': {'사업장명': p['name'], '업종': '도시민박업' if p['svc'] == HS[0] else '한옥체험업', '인허가 시기': period,
                                   '인허가일': p['opened'], '폐업일': p['closed'], '객실': p['rooms'], '주소': p['addr'],
                                   '행복황촌 구역': '안' if B_ID in p['areas'].split(';') else '밖'}})
    json.dump({'type': 'FeatureCollection', 'features': pts}, open(PROCESSED / 'lodging_permits_web_4326.geojson', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    # 리포트 카드 수치: 행복황촌 월말 재고, 연도별 신규, 동별 분포
    last = f'{SNAP[:4]}-{int(SNAP[4:6]) - 1:02d}' if SNAP[4:6] != '01' else f'{int(SNAP[:4]) - 1}-12'
    monthly = []
    for y in range(2019, int(last[:4]) + 1):
        for m in range(1, 13):
            ym = f'{y}-{m:02d}'
            if ym > last: break
            d = f'{ym}-{calendar.monthrange(y, m)[1]:02d}'
            monthly.append([ym] + [sum(1 for f in feats if f['properties']['svc'] == s and in_b(f) and live(f['properties'], d)) for s in HS])
    d_last = monthly[-1][0] + f'-{calendar.monthrange(int(last[:4]), int(last[5:]))[1]:02d}'
    homestay = [f for f in feats if f['properties']['svc'] == HS[0]]
    permits = []
    for y in range(2016, int(last[:4]) + 1):
        b = sum(1 for f in homestay if f['properties']['opened'][:4] == str(y) and in_b(f))
        permits.append([str(y), b, sum(1 for f in homestay if f['properties']['opened'][:4] == str(y)) - b])
    dong = Counter(f['properties']['dong'] or '미상' for f in homestay if live(f['properties'], d_last))
    rep = {'src': f'행정안전부 지방행정인허가 개방자료(외국인관광 도시민박업·한옥체험업, 경주시), {SNAP[:4]}-{SNAP[4:6]}-{SNAP[6:]} 내려받음 (T1)',
           'asof': d_last, 'monthly': monthly, 'permits': permits,
           'b_now': monthly[-1][1], 'b_now_hanok': monthly[-1][2],
           'b_now_inner20': sum(1 for f in homestay if in_b(f, B_IN) and live(f['properties'], d_last)),
           'b_new_last_year': permits[-1][1], 'gj_new_last_year': permits[-1][1] + permits[-1][2],
           'gj_now': sum(dong.values()), 'dong': dong.most_common(10)}
    json.dump(rep, open(PROCESSED / 'lodging_report.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('웹 점', len(pts), '/ 리포트', {k: rep[k] for k in ('asof', 'b_now', 'b_now_hanok', 'b_now_inner20', 'b_new_last_year', 'gj_new_last_year', 'gj_now')})

if __name__ == '__main__':
    main()
