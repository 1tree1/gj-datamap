import json
from pathlib import Path
from shapely.geometry import box,shape
from shapely.ops import transform
from pyproj import Transformer
B=Path(__file__).parent;R=Path(r'C:\Users\OFFICE\Desktop\9_도시')
prefix=(B/'prepare_geometry.py').read_text(encoding='utf8').split("bld=read(")[0]
exec(prefix)
bb=[217300,359650,223300,362750];roi=box(*bb);its=[]
def add(g,fill=None,line=None,lw=.8):
 if g.is_empty:return
 if g.geom_type=='Polygon':its.append({'points':list(map(list,g.exterior.coords)),'fill':fill,'line':line,'lw':lw,'closed':True})
 elif g.geom_type=='LineString':its.append({'points':list(map(list,g.coords)),'fill':None,'line':line,'lw':lw,'closed':False})
 elif hasattr(g,'geoms'):
  for q in g.geoms:add(q,fill,line,lw)
for name,c,l in [('N3A_E0010001','#D5E3E9',None),('N3A_B0010000','#E4E7E9',None),('N3L_A0020000',None,'#C3C9CE')]:
 for g in read(name):
  if g.intersects(roi):add(g.intersection(roi),c,l,.7)
for f in json.loads((R/'gj-datamap/public/data/parks_upis.geojson').read_text(encoding='utf8'))['features']:
 g=transform(T4.transform,shape(f['geometry'])).intersection(roi)
 add(g,'#F0F1EC')
zone=transform(T4.transform,shape(json.loads((R/'work/20261011_midterm_deck/build/data/plan_boundary_4326_min.geojson').read_text(encoding='utf8'))['features'][0]['geometry']))
add(zone,'#D5E3EE','#235D82',2)
sites=json.loads((R/'gj-datamap/public/data/cityhall_sites.geojson').read_text(encoding='utf8'))['features'][:6]
centers=[list(T4.transform(*f['geometry']['coordinates'])) for f in sites]
m={'name':'cityhall_map','bounds':bb,'w':1600,'h':827,'items':its,'centers':centers}
(B/'cityhall_geometry.json').write_text(json.dumps([m],ensure_ascii=False),encoding='utf8')
gs=json.loads((B/'geometry.json').read_text(encoding='utf8'));gs=[g for g in gs if g['name']!='cityhall_map']+[m]
(B/'geometry.json').write_text(json.dumps(gs,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('Map paths:',len(its),'verified address points:',len(centers))
