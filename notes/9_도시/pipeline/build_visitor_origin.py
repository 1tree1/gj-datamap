"""한국관광 데이터랩 '지역별 관광 현황 › 유입·유출 지역 › 유입도시 유형 분류' — 경주시 유입 시군구별 방문자 수·지출금액을 전국 시군구 경계에 조인.

입력: archive/C_data/raw/datalab_visitor_origin_gyeongju_202509_202608.json  (브라우저 DOM 전사, 2026-09-21)
      archive/C_data/raw/vworld_sigg_kr.geojson (V-World LT_C_ADSIGG_INFO 256개)
출력: archive/C_data/processed/visitor_origin_sigg_4326.geojson
"""
import json, sys, io, re
from shapely.geometry import shape, mapping
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]; RAW = ROOT / 'archive/C_data/raw'; PROC = ROOT / 'archive/C_data/processed'
rows = json.load(open(RAW / 'datalab_visitor_origin_gyeongju_202509_202608.json', encoding='utf-8'))
SIDO = {'서울': '서울특별시', '부산': '부산광역시', '대구': '대구광역시', '인천': '인천광역시', '대전': '대전광역시', '울산': '울산광역시', '세종': '세종특별자치시', '경기': '경기도', '강원': '강원특별자치도',
        '충북': '충청북도', '충남': '충청남도', '전북': '전북특별자치도', '전남광주': '전남광주통합특별시', '경북': '경상북도', '경남': '경상남도', '제주': '제주특별자치도'}
TYPE = {0: ('Platinum Class', '방문 많음·지출 많음'), 1: ('High Loyalty', '방문 적음·지출 많음'), 2: ('More Promotion', '방문 많음·지출 적음'), 3: ('Invest', '방문 적음·지출 적음')}
def full(name):
    if name == '세종': return '세종특별자치시'
    p = name.split(' ', 1); return f"{SIDO.get(p[0], p[0])} {p[1]}" if len(p) > 1 else SIDO.get(p[0], p[0])
data = {}
for dist, ti, rank, name, vis, spend in rows:
    data[full(name)] = {'origin': name, 'dist': dist.replace(' 유형', ''), 'type': TYPE[ti][0], 'type_kr': TYPE[ti][1], 'rank_in_type': int(rank),
                        'visitors': int(vis.replace(',', '')), 'spend_krw': int(spend.replace(',', ''))}
g = json.load(open(RAW / 'vworld_sigg_kr.geojson', encoding='utf-8'))
tot_v = sum(d['visitors'] for d in data.values()); tot_s = sum(d['spend_krw'] for d in data.values())
feats = []; hit = set()
for f in g['features']:
    nm = f['properties']['full_nm']; d = data.get(nm)
    if d: hit.add(nm)
    p = {'full_nm': nm, 'sig_cd': f['properties']['sig_cd'], 'lbl': f['properties']['sig_kor_nm']}
    if d:
        p |= d; p['share_pct'] = round(d['visitors'] / tot_v * 100, 2); p['spend_per_visitor'] = round(d['spend_krw'] / d['visitors'])
        p['lbl'] = f"{f['properties']['sig_kor_nm']}\n{d['visitors']:,}"
    else:
        p |= {'visitors': None, 'spend_krw': None, 'share_pct': None, 'type': None, 'dist': None}
    p['source'] = '한국관광 데이터랩 지역별 관광 현황 › 유입·유출 지역 › 유입도시 유형 분류, 경상북도 경주시, 조회기간 2025.09~2026.08 (T2, 통신·내비·카드 융합 추정치 — 총량 아닌 구성비로만 사용). 경계 V-World LT_C_ADSIGG_INFO'
    geom = mapping(shape(f['geometry']).simplify(0.0008, preserve_topology=True))  # ≈80m — 전국 축척용, 원본은 raw/vworld_sigg_kr.geojson
    feats.append({'type': 'Feature', 'geometry': geom, 'properties': p})
miss = [k for k in data if k not in hit]
print('rows', len(data), 'matched', len(hit), 'unmatched', miss)
print('total visitors', tot_v, 'spend', tot_s)
top = sorted(data.items(), key=lambda kv: -kv[1]['visitors'])[:10]
for k, v in top: print(f"{k:24s} {v['visitors']:>9,} {v['visitors']/tot_v*100:5.1f}% {v['type']}")
json.dump({'type': 'FeatureCollection', 'features': feats}, open(PROC / 'visitor_origin_sigg_4326.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
# 시도 집계
sd = {}
for k, v in data.items():
    s = k.split()[0]; sd.setdefault(s, [0, 0]); sd[s][0] += v['visitors']; sd[s][1] += v['spend_krw']
json.dump({'period': '2025.09~2026.08', 'total_visitors': tot_v, 'total_spend': tot_s, 'by_sido': {k: {'visitors': a, 'spend': b, 'share_pct': round(a / tot_v * 100, 1)} for k, (a, b) in sorted(sd.items(), key=lambda x: -x[1][0])},
           'top10': [{'sigg': k, **v, 'share_pct': round(v['visitors'] / tot_v * 100, 2)} for k, v in top]},
          open(PROC / 'visitor_origin_summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, (a, b) in sorted(sd.items(), key=lambda x: -x[1][0]): print(f"{k:12s} {a:>10,} {a/tot_v*100:5.1f}%")
