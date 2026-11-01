from pathlib import Path
import json,sys
sys.stdout.reconfigure(encoding='utf8')
r=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/nexus_v13_audit_20261011')
g=json.loads((r/'comparison_groups.json').read_text('utf8'))
print('SUMS',{k:v for k,v in g.items() if k not in ['volume_checks','group_floors','site_rows']})
print('SITE ROWS')
for x in g['site_rows']: print(x['name'],x['layer'].split('::')[-1],round(x['area'],3))
m=json.loads((r/'rhino_measurements.json').read_text('utf8'));print('MEASUREMETA',{k:v for k,v in m.items() if k not in ['records','floors','buildings','global_floors']});print('BEXAMPLE',str(m['buildings'])[:3500]);print('GLOBALEXAMPLE',str(m['global_floors'])[:1000])
p=json.loads((r/'placement-model-plan.json').read_text('utf8'))
print('CHECKS',len(p['checks']),sum(x['dimensions_match'] for x in p['checks']))
print('CHECKKEY',p['checks'][:1]);print('FEATUREEXAMPLE',str(p['features'][0])[:1000])
