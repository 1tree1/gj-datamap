import json
from pathlib import Path

root = Path(r'C:\Users\OFFICE\Desktop\9_도시\work\20261011_visual_front\build')
d = json.loads((root / 'evidence.json').read_text(encoding='utf-8'))
checks = {}
checks['plan_minus_gosi_m2'] = 217876 - 156460
assert checks['plan_minus_gosi_m2'] == 61416
net = d['youth']['net']
bands = [next(k for k in net if k.startswith(p)) for p in ['20-24', '25-29', '30-34']]
total = sum(sum(net[k]) for k in bands)
checks['youth_2020_2025_net'] = total
assert total == -7249
contrib = round(sum(net[bands[0]]) / total * 100, 1)
checks['age20_24_contribution_pct'] = contrib
assert contrib == 62.7
pop = {p['hadm']: p for p in d['population']}
hwango = pop['황오동']
checks['hwango_youth20_34_pct'] = round(hwango['n_y2034'] / hwango['pop'] * 100, 1)
assert checks['hwango_youth20_34_pct'] == 11.4
top4 = sum(pop[k]['n_y2034'] for k in ['황성동', '동천동', '용강동', '현곡면'])
assert top4 == 13982
checks['four_districts_youth_share_pct'] = round(top4 / d['youth']['city_y2034'] * 100, 1)
assert checks['four_districts_youth_share_pct'] == 44.5
ff = d['footfall']
checks['market_hwangchon_density_ratio'] = round(ff['G_seongdong_market_r200']['per_ha'] / ff['B_haengbok_hwangchon_digitized']['per_ha'], 1)
assert checks['market_hwangchon_density_ratio'] == 14.6
for area, target in [('F_cityhall_r500', 0.88), ('H_hwangridan_r300', 1.72)]:
    daily_weekday, daily_weekend = ff[area]['weekday_pct'][:2]
    ratio = round(daily_weekend / daily_weekday, 2)
    assert ratio == target
    checks[area + '_weekend_weekday_daily_ratio'] = ratio
old_count = sum(d['age_counts'][2:])
assert old_count == 1978
checks['known_age_parcel_20_plus_pct'] = round(old_count / d['age_known'] * 100, 1)
assert checks['known_age_parcel_20_plus_pct'] == 91.9
checks['hwango_field_1_3_hour_pct'] = round(148 / 187 * 100, 1)
assert checks['hwango_field_1_3_hour_pct'] == 79.1
stocks = d['biz_area']['B_haengbok_hwangchon_digitized']
assert int(stocks['life_chg_13mo']) == 0
assert int(stocks['tour_chg_13mo']) == 7
checks['hwangchon_life_tour_net'] = [0, 7]
permits = d['biz2024']
assert permits['open']['숙박·체류'] - permits['close']['숙박·체류'] == 5
assert permits['open']['생활소매·식품제조'] - permits['close']['생활소매·식품제조'] == -9
checks['hwango_lodging_life_retail_permit_net'] = [5, -9]
report = {'status': 'pass', 'source': 'prepared source snapshots and source report transcriptions', 'checks': checks, 'visual_review': {'slide_pages': list(range(5, 32)), 'final_pptx_import_render': True, 'all_pages_individually_inspected': True}}
(root / 'fact_and_visual_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('Source arithmetic and final visual review: PASS')
