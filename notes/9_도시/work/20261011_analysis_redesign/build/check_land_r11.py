import json,sys
from pathlib import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union
sys.stdout.reconfigure(encoding='utf8')
r=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/nexus_v13_audit_20261011')
p=json.loads((r/'placement-model-plan.json').read_text('utf8'))
f=[x for x in p['features'] if x['building'] is None]
def poly(x):
 return unary_union([Polygon(a).buffer(0) for a in x['rings'] if len(a)>=4])
b=unary_union([poly(x) for x in f if '00_구역' in x['layer']])
print('BOUNDARY',b.area,b.bounds)
gs={}
for key,part in [('plots','01_획지'),('parks','02_공원'),('walk','03_보행')]:
 rows=[x for x in f if part in x['layer']];g=unary_union([poly(x) for x in rows]);gs[key]=g.intersection(b)
 print(key,'rows',len(rows),'sum',sum(poly(x).area for x in rows),'union',g.area,'clip',g.intersection(b).area)
for k,g in gs.items():
 for k2,h in gs.items():
  if k2>k:print('OVERLAP',k,k2,g.intersection(h).area)
print('UNASSIGNED',b.difference(unary_union(list(gs.values()))).area)
for x in f:
 if '01_획지' in x['layer'] or '02_공원' in x['layer']: print(x['name'],round(poly(x).area,2))
print('missing_measurements', [x['id'] for x in p['checks'] if not x['found']]);
