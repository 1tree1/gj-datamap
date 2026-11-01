import json
from pathlib import Path
from shapely.geometry import shape,box
from shapely.ops import transform
from pyproj import Transformer
B=Path(__file__).parent;R=Path(r'C:\Users\OFFICE\Desktop\9_도시')
fc=json.loads((R/'work/20261011_visual_front/build/web_data/hadm_pop.geojson').read_text(encoding='utf8'))
T=Transformer.from_crs(4326,5187,always_xy=True)
bb=[214500,357500,224700,368500];roi=box(*bb)
its=[];centers={}
for f in fc['features']:
 n=f['properties']['hadm'];g=transform(T.transform,shape(f['geometry'])).intersection(roi).simplify(12,preserve_topology=True)
 if g.is_empty:continue
 color='#DEE3E6'
 if n in ['황남동','황오동','성건동','월성동']:color='#82A9C0'
 if n in ['용강동','현곡면']:color='#D7AA84'
 parts=[g] if g.geom_type=='Polygon' else list(g.geoms)
 for p in parts:
  if p.geom_type=='Polygon':its.append({'points':list(map(list,p.exterior.coords)),'fill':color,'line':'#FFFFFF','lw':2,'closed':True})
 if n in ['용강동','현곡면','황오동']:centers[n]=list(g.representative_point().coords)[0]
z=json.loads((R/'work/20261011_midterm_deck/build/data/plan_boundary_4326_min.geojson').read_text(encoding='utf8'))['features'][0]['geometry'];g=transform(T.transform,shape(z))
its.append({'points':list(map(list,g.exterior.coords)),'fill':None,'line':'#235D82','lw':4,'closed':True})
m={'name':'population_map','bounds':bb,'w':1200,'h':1000,'items':its,'centers':centers}
(B/'population_geometry.json').write_text(json.dumps([m],ensure_ascii=False),encoding='utf8')
maps=json.loads((B/'geometry.json').read_text(encoding='utf8'));maps=[m0 for m0 in maps if m0['name']!='population_map'];maps.append(m)
(B/'geometry.json').write_text(json.dumps(maps,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('population',centers,len(its))
