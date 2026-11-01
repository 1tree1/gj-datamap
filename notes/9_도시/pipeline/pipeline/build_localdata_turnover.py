"""지방행정인허가데이터(localdata.go.kr) 경주시 전 업종 → 구역별·업종군별 개업/폐업 시계열.

입력: archive/C_data/raw/localdata_gyeongju/*.csv|*.xlsx|*.zip  (localdata '지역별 데이터 받기' 또는 업종별 전체 파일)
      좌표 열 '좌표정보X(EPSG5174)' / '좌표정보Y(EPSG5174)' (구 명칭 '좌표정보(x)'/'좌표정보(y)') — 값 없으면 V-World 지오코딩(.env VWORLD_KEY)
구역: archive/C_data/processed/footfall_areas_5187.geojson (A~D) + 시청500m/성동시장200m/황리단길300m 원 + S2 원도심 창
출력: archive/C_data/processed/localdata_gj_points_5187.geojson (사업장 점, 구역 태그)
      archive/C_data/processed/localdata_turnover_year.csv (구역×업종군×연도 개업·폐업·영업중)
      archive/90_derived/localdata_substitution_summary.csv (치환 판정표)
"""
import csv, io, json, re, sys, zipfile, os, time, urllib.parse
from pathlib import Path
from collections import defaultdict
from shapely.geometry import shape, Point
from shapely.ops import transform
from pyproj import Transformer
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_env, get_json, ROOT, RAW, PROCESSED

SRC = RAW / 'localdata_gyeongju'
DERIV = ROOT / 'archive/90_derived'
T5174_5187 = Transformer.from_crs(5174, 5187, always_xy=True).transform
T4326_5187 = Transformer.from_crs(4326, 5187, always_xy=True).transform
T5187_4326 = Transformer.from_crs(5187, 4326, always_xy=True).transform

# ---------- 업종군 분류 (개방서비스명 + 업태구분명)
TOUR_SVC = {'숙박업', '관광숙박업', '외국인관광도시민박업', '한옥체험업', '관광펜션업', '야영장업', '여행업', '관광사진업', '종합휴양업', '유원시설업', '관광공연장업', '관광유흥음식점업', '휴양콘도미니엄업'}
LIFE_SVC = {'이용업', '미용업', '세탁업', '목욕장업', '식육판매업', '식육포장처리업', '즉석판매제조가공업', '담배소매업', '의원', '치과의원', '한의원', '약국', '안경업', '의료기기판매(임대)업', '의료기기판매업', '공인중개사', '부동산중개업', '건강기능식품일반판매업', '축산물판매업', '유료직업소개소', '방문판매업', '학원', '교습소', '어린이집', '노인복지시설', '동물병원', '동물약국', '안전상비의약품 판매업소', '의료기관', '병원', '유통전문판매업', '식품판매업', '식품소분업', '집단급식소', '집단급식소식품판매업'}
NIGHT_SVC = {'단란주점영업', '유흥주점영업', '노래연습장업', '게임제공업', '인터넷컴퓨터게임시설제공업', '복합유통게임제공업', '청소년게임제공업'}
CAFE_PAT = re.compile(r'커피|카페|다방|찻집|제과|아이스크림|떡카페')

def classify(svc, upt):
    svc = (svc or '').strip(); upt = (upt or '').strip()
    if svc in TOUR_SVC: return '관광체류'
    if svc == '휴게음식점':
        return '카페' if CAFE_PAT.search(upt) else '휴게음식점기타'
    if svc == '일반음식점':
        if re.search(r'호프|소주방|대포|정종|통닭', upt): return '음식점_주류'
        if re.search(r'한식|분식|중국식|일식|경양식|뷔페|식육', upt): return '음식점_식사'
        return '음식점_기타'
    if svc in NIGHT_SVC: return '유흥오락'
    if svc in LIFE_SVC: return '생활'
    if svc == '통신판매업': return '통신판매'
    return '기타'

# ---------- 구역
fc = json.load(open(PROCESSED / 'footfall_areas_5187.geojson', encoding='utf-8'))
AREAS = {f['properties']['id']: shape(f['geometry']) for f in fc['features']}
def circle(lon, lat, r): return Point(T4326_5187(lon, lat)).buffer(r)
AREAS['F_cityhall_r500'] = circle(129.2247816627553, 35.85621665939485, 500)
AREAS['G_seongdong_market_r200'] = circle(129.216354826459, 35.84534371000188, 200)
AREAS['H_hwangridan_r300'] = circle(129.2098, 35.8384, 300)
S2_DONG = {'성동동', '황오동', '노서동', '노동동', '성건동', '동부동', '서부동', '북부동', '중부동', '황남동', '인왕동', '동천동', '황성동', '용강동', '탑동', '교동'}

# ---------- 파일 읽기
def iter_rows():
    files = sorted(SRC.glob('*'))
    if not files: raise SystemExit(f'입력 없음: {SRC} — localdata.go.kr 지역별 데이터(경상북도 경주시) 파일을 여기에 두세요')
    for p in files:
        if p.suffix.lower() == '.zip':
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if n.lower().endswith('.csv'):
                        yield from read_csv(io.TextIOWrapper(z.open(n), encoding='cp949', errors='replace'), n)
                    elif n.lower().endswith('.xlsx'):
                        yield from read_xlsx(io.BytesIO(z.read(n)), n)
        elif p.suffix.lower() == '.csv':
            for enc in ('utf-8-sig', 'cp949'):
                try:
                    yield from read_csv(open(p, encoding=enc, errors='strict'), p.name); break
                except UnicodeDecodeError: continue
        elif p.suffix.lower() == '.xlsx':
            yield from read_xlsx(p, p.name)

def read_csv(f, name):
    r = csv.DictReader(f)
    for row in r: row['_file'] = name; yield row

def read_xlsx(f, name):
    import openpyxl
    wb = openpyxl.load_workbook(f, read_only=True)
    ws = wb.active; rows = ws.iter_rows(values_only=True); hdr = [str(h).strip() for h in next(rows)]
    for vals in rows:
        row = dict(zip(hdr, vals)); row['_file'] = name; yield row

def g(row, *names):
    for n in names:
        for k in row:
            if k and k.replace(' ', '') == n.replace(' ', ''): return row[k]
    return None

def main():
    env = load_env(); vk = env.get('VWORLD_KEY'); h = {'Referer': env.get('VWORLD_DOMAIN', ''), 'User-Agent': 'Mozilla/5.0'}
    cache_p = SRC.parent / 'localdata_geocode_cache.json'
    cache = json.load(open(cache_p, encoding='utf-8')) if cache_p.exists() else {}
    feats, n_all, n_gj, n_xy, n_geo, n_miss = [], 0, 0, 0, 0, 0
    for row in iter_rows():
        n_all += 1
        addr = (g(row, '소재지전체주소', '소재지주소') or ''); raddr = (g(row, '도로명전체주소', '도로명주소') or '')
        if '경주시' not in addr and '경주시' not in raddr: continue
        n_gj += 1
        x = g(row, '좌표정보X(EPSG5174)', '좌표정보x(epsg5174)', '좌표정보(x)', '좌표정보(X)'); y = g(row, '좌표정보Y(EPSG5174)', '좌표정보y(epsg5174)', '좌표정보(y)', '좌표정보(Y)')
        pt = None
        try:
            if x not in (None, '') and y not in (None, ''):
                pt = Point(T5174_5187(float(x), float(y))); n_xy += 1
        except Exception: pt = None
        if pt is None:
            a = re.sub(r'\(.*?\)', '', raddr or addr).strip()
            dong = next((d for d in S2_DONG if d in addr), None)
            if not a or not dong:  # 원도심 밖이면 지오코딩 생략
                n_miss += 1; continue
            if a in cache: c = cache[a]
            else:
                c = None
                if vk:
                    for typ in ('ROAD', 'PARCEL'):
                        try:
                            r = get_json(f"https://api.vworld.kr/req/address?service=address&request=getcoord&version=2.0&crs=EPSG:4326&type={typ}&address={urllib.parse.quote(a)}&format=json&key={vk}", h, retries=1)['response']
                            if r['status'] == 'OK': c = [float(r['result']['point']['x']), float(r['result']['point']['y'])]; break
                        except Exception: pass
                    time.sleep(0.05)
                cache[a] = c
            if not c: n_miss += 1; continue
            pt = Point(T4326_5187(*c)); n_geo += 1
        svc = g(row, '개방서비스명'); upt = g(row, '업태구분명', '위생업태명') or ''
        opened = str(g(row, '인허가일자') or '')[:10]; closed = str(g(row, '폐업일자') or '')[:10]
        status = g(row, '영업상태명') or g(row, '상세영업상태명') or ''
        tags = [k for k, a in AREAS.items() if a.contains(pt)]
        dong = next((d for d in S2_DONG if d in addr), '')
        feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [round(pt.x, 1), round(pt.y, 1)]},
                      'properties': {'svc': svc, 'upt': upt, 'grp': classify(svc, upt), 'name': g(row, '사업장명'), 'opened': opened, 'closed': closed,
                                     'status': status, 'dong': dong, 'areas': ';'.join(tags), 'addr': addr[:60]}})
    json.dump(cache, open(cache_p, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(PROCESSED / 'localdata_gj_points_5187.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'rows {n_all}, 경주시 {n_gj}, 좌표 {n_xy}, 지오코딩 {n_geo}, 누락 {n_miss}, 저장 {len(feats)}')

    # ---------- 연도별 개업·폐업·영업중 (구역×업종군)
    years = list(range(2010, 2027))
    def yr(s):
        m = re.match(r'(\d{4})', s or ''); return int(m.group(1)) if m else None
    keys = list(AREAS) + ['S2_원도심동']
    opened_c = defaultdict(int); closed_c = defaultdict(int); stock = defaultdict(int)
    for f in feats:
        p = f['properties']; grp = p['grp']
        tags = p['areas'].split(';') if p['areas'] else []
        if p['dong'] in S2_DONG: tags.append('S2_원도심동')
        oy, cy = yr(p['opened']), yr(p['closed'])
        for k in tags:
            if oy: opened_c[(k, grp, oy)] += 1
            if cy: closed_c[(k, grp, cy)] += 1
            for y in years:  # 연말 영업중 재고
                if oy and oy <= y and (not cy or cy > y): stock[(k, grp, y)] += 1
    rows = []
    grps = sorted({f['properties']['grp'] for f in feats})
    for k in keys:
        for grp in grps:
            for y in years:
                rows.append([k, grp, y, opened_c[(k, grp, y)], closed_c[(k, grp, y)], stock[(k, grp, y)]])
    with open(PROCESSED / 'localdata_turnover_year.csv', 'w', newline='', encoding='utf-8-sig') as f:
        c = csv.writer(f); c.writerow(['area_id', 'group', 'year', 'opened', 'closed', 'stock_yearend']); c.writerows(rows)

    # ---------- 치환 판정: 2019~2025 순증(개업−폐업)과 재고 변화, 생활 vs 관광체류·카페
    out = []
    for k in keys:
        rec = {'area_id': k}
        for grp in grps:
            o = sum(opened_c[(k, grp, y)] for y in range(2019, 2026)); c_ = sum(closed_c[(k, grp, y)] for y in range(2019, 2026))
            s18, s25 = stock[(k, grp, 2018)], stock[(k, grp, 2025)]
            rec[f'{grp}_open19_25'] = o; rec[f'{grp}_close19_25'] = c_; rec[f'{grp}_stock18'] = s18; rec[f'{grp}_stock25'] = s25
            rec[f'{grp}_chg_pct'] = round((s25 / s18 - 1) * 100, 1) if s18 else None
        out.append(rec)
    cols = ['area_id'] + [c for c in out[0] if c != 'area_id']
    with open(DERIV / 'localdata_substitution_summary.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
    for r in out:
        print(r['area_id'], {g_: (r.get(f'{g_}_stock18'), r.get(f'{g_}_stock25'), r.get(f'{g_}_chg_pct')) for g_ in ('생활', '관광체류', '카페', '음식점_식사', '음식점_주류')})

if __name__ == '__main__':
    main()
