"""소상공인365 유동인구 원자료(JSON) → 정리표 CSV + 밀도 비교.

입력: archive/C_data/raw/sbiz365_footfall_20260920.json
출력: archive/C_data/processed/footfall_sbiz365_{monthly,hourly,weekday,sexage,resident_worker}.csv
      archive/90_derived/footfall_sbiz365_summary.csv (면적·밀도·비교)
"""
import json, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'archive/C_data/raw/sbiz365_footfall_20260920.json'
PROC = ROOT / 'archive/C_data/processed'
DERIV = ROOT / 'archive/90_derived'
AREAS = json.load(open(ROOT / 'archive/90_derived/footfall_areas_5181.json', encoding='utf-8'))
AREA_M2 = {k: v['area_m2'] for k, v in AREAS.items()}
AREA_M2['E_center_r300'] = 282743
AREA_M2['F_cityhall_r500'] = 785398
AREA_M2['G_seongdong_market_r200'] = 125664
AREA_M2['H_hwangridan_r300'] = 282743
LABEL = {
    'A_hwango_grid32': '황오동 원도심 활성화구역(격자32)',
    'B_haengbok_hwangchon_digitized': '경주역동편 행복황촌 활성화구역(근사)',
    'C_zone_buffer300': '지구단위계획구역+300m',
    'D_zone': '지구단위계획구역',
    'E_center_r300': '구역 중심 반경 300m',
    'F_cityhall_r500': '동천동 시청 반경 500m',
    'G_seongdong_market_r200': '성동시장 반경 200m',
    'H_hwangridan_r300': '황리단길 반경 300m',
}
d = json.load(open(RAW, encoding='utf-8'))
n = lambda s: float(str(s).replace(',', '')) if s not in ('', '-') else None
areas = [k for k in d if not k.startswith('_')]

def w(name, header, rows):
    with open(name, 'w', newline='', encoding='utf-8-sig') as f:
        c = csv.writer(f); c.writerow(header); c.writerows(rows)

# 월별 (long)
rows = []
for k in areas:
    m = d[k]['monthly']
    for mo, v in zip(m['months'], m['sel']):
        rows.append([k, LABEL[k], '20' + mo.replace('.', '-'), n(v), round(n(v) / AREA_M2[k] * 10000, 1)])
w(PROC / 'footfall_sbiz365_monthly.csv', ['area_id', 'area', 'month', 'footfall_daily_avg', 'per_ha'], rows)

# 시간대
rows = []
for k in areas:
    h = d[k]['hourly']
    for c, v, p in zip(h['cols'], h['sel'], h['sel_pct']):
        rows.append([k, LABEL[k], c, n(v), n(p)])
w(PROC / 'footfall_sbiz365_hourly.csv', ['area_id', 'area', 'band', 'footfall', 'pct'], rows)

# 요일
rows = []
for k in areas:
    wd = d[k]['weekday']
    for c, v, p in zip(wd['cols'], wd['sel'], wd['sel_pct']):
        rows.append([k, LABEL[k], c, n(v), n(p)])
w(PROC / 'footfall_sbiz365_weekday.csv', ['area_id', 'area', 'day', 'footfall', 'pct'], rows)

# 성·연령
rows = []
for k in areas:
    s = d[k]['daily_sex_age']
    cols = ['일일', '남', '여', '10대', '20대', '30대', '40대', '50대', '60대+']
    pct = [100.0] + [n(x) for x in s['sel_pct']]
    for c, v, p in zip(cols, s['sel'], pct):
        rows.append([k, LABEL[k], c, n(v), p])
w(PROC / 'footfall_sbiz365_sexage.csv', ['area_id', 'area', 'group', 'footfall', 'pct'], rows)

# 주거·직장인구
rows = []
for k in areas:
    r = d[k]['resident']; wk = d[k]['worker']
    for c, v in zip(['2025H1', '2025H2', '2026H1'], r['sel']): rows.append([k, LABEL[k], '주거인구', c, n(v)])
    for c, v in zip(['2025H1', '2025H2', '2026H1'], wk['sel']): rows.append([k, LABEL[k], '직장인구', c, n(v)])
w(PROC / 'footfall_sbiz365_resident_worker.csv', ['area_id', 'area', 'kind', 'half', 'value'], rows)

# 요약
rows = []
for k in areas:
    m = d[k]['monthly']; vals = [n(v) for v in m['sel']]
    avg = sum(vals) / len(vals); last = vals[-1]
    h = d[k]['hourly']; hv = [n(x) for x in h['sel']]
    wd = d[k]['weekday']; wv = [n(x) for x in wd['sel']]
    r = n(d[k]['resident']['sel'][-1]); wk = n(d[k]['worker']['sel'][-1])
    sa = [n(x) for x in d[k]['daily_sex_age']['sel']]
    rows.append([k, LABEL[k], AREA_M2[k], round(avg), last, round(avg / AREA_M2[k] * 10000, 1),
                 round(hv[4] / sum(hv) * 100, 1), round(hv[5] / sum(hv) * 100, 1), round(wv[1] / wv[0], 2),
                 round(sa[8] / sa[0] * 100, 1), r, wk, round(avg / max(r + wk, 1), 1)])
w(DERIV / 'footfall_sbiz365_summary.csv',
  ['area_id', 'area', 'area_m2', 'footfall_13mo_avg', 'footfall_2606', 'per_ha', 'pct_18_23', 'pct_23_05',
   'weekend_to_weekday', 'pct_60plus', 'resident_2026H1', 'worker_2026H1', 'footfall_per_resident_worker'], rows)
for r in rows: print(r)
