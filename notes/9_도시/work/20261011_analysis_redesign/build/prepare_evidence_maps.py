import json
from pathlib import Path
from shapely.geometry import shape,box
from shapely.ops import transform
from pyproj import Transformer
B=Path(__file__).parent;R=Path(r'C:\Users\OFFICE\Desktop\9_도시');T=Transformer.from_crs(4326,5187,always_xy=True)
data=R/'gj-datamap/public/data'
zone=transform(T.transform,shape(json.loads((R/'work/20261011_midterm_deck/build/data/plan_boundary_4326_min.geojson').read_text(encoding='utf8'))['features'][0]['geometry']))
maps=[]
for name,src,bb,w,h in [('age_map','parcels',[218250,359850,220650,362050],1400,1050),('height_map','godo',[219200,360250,220300,361700],900,1200)]:
 roi=box(*bb);its=[]
 for f in json.loads((data/(src+'.geojson')).read_text(encoding='utf8'))['features']:
  g=transform(T.transform,shape(f['geometry'])).intersection(roi)
  if g.is_empty:continue
  p=f['properties']
  if src=='parcels':
   age=p.get('bldg_age');c='#DEE2E5' if age is None else '#82A9C0' if age>=20 else '#D7AA84'
  else:c='#82A9C0' if p.get('h_max')==20 else '#E4E7E9'
  for pg in [g] if g.geom_type=='Polygon' else list(g.geoms):
   if pg.geom_type=='Polygon':its.append({'points':list(map(list,pg.exterior.coords)),'fill':c,'line':'#FFFFFF','lw':.75 if src=='parcels' else 1.5,'closed':True})
 its.append({'points':list(map(list,zone.exterior.coords)),'fill':None,'line':'#20272E','lw':2,'closed':True})
 maps.append({'name':name,'bounds':bb,'w':w,'h':h,'items':its})
(B/'evidence_geometry.json').write_text(json.dumps(maps,ensure_ascii=False),encoding='utf8')
allmaps=json.loads((B/'geometry.json').read_text(encoding='utf8'));allmaps=[m for m in allmaps if m['name'] not in ['age_map','height_map']]+maps
(B/'geometry.json').write_text(json.dumps(allmaps,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print([(m['name'],len(m['items'])) for m in maps])
