import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf8')
r=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/nexus_v13_audit_20261011')
j=json.loads((r/'rhino_measurements.json').read_text('utf8'));print(j['records'][0]);p=json.loads((r/'placement-model-plan.json').read_text('utf8')); rr={x['id']:x for x in j['records']}
for x in p['checks']:
 if not x['dimensions_match']:print('DISCREPANCY',x,rr[x['id']]['object_name'])
print('GFA',sum(x['target'] or 0 for x in json.loads((r/'facility_comparison.json').read_text('utf8'))))
