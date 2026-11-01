from pathlib import Path
import json,hashlib
from shapely.geometry import shape,box,Point
from shapely.ops import transform
from pyproj import Transformer
B=Path(__file__).parent;R=B.parents[2];T=Transformer.from_crs(4326,5187,always_xy=True)
bb=[218000,359700,222000,362500];roi=box(*bb)
# Reuse the inspected NGII drawing and the actual projected street geometries.
base=json.loads((B/'cityhall_geometry.json').read_text(encoding='utf8'))[0]
items=[]
for i in base['items']:
 if i.get('fill')=='#D5E3EE' or i.get('line')=='#235D82':continue
 if not all(bb[0]-500<=p[0]<=bb[2]+500 and bb[1]-500<=p[1]<=bb[3]+500 for p in i['points']):continue
 q=dict(i)
 if q.get('fill'):q['fill']='#F0F1F2' if q['fill']!='#D5E3E9' else '#E1EBEF'
 if q.get('line'):q['line']='#DFE3E6';q['lw']=.45
 items.append(q)
data=json.loads((B/'live_traffic_hist.geojson').read_text(encoding='utf8'))
features=[]
for f in data['features']:
 g=transform(T.transform,shape(f['geometry']))
 if not g.intersects(roi):continue
 features.append((g,f['properties']))
counts=[]
for hour in [6,13,21]:
 key=f'we_{hour:02d}';valid=[p for g,p in features if key in p];counts.append({'hour':hour,'n_links':len(valid),'congested_links':sum(p[key]<p.get('thr_c',15) for p in valid),'slow_links':sum(p.get('thr_c',15)<=p[key]<p.get('thr_f',25) for p in valid)})
def addline(g,c,w):
 if g.geom_type=='LineString':items.append({'points':list(map(list,g.coords)),'fill':None,'line':c,'lw':w,'closed':False})
 elif hasattr(g,'geoms'):
  for q in g.geoms:addline(q,c,w)
for state in [0,1,2]:
 for g,p in features:
  v=p.get('we_13');s=2 if v is not None and v<p.get('thr_c',15) else 1 if v is not None and v<p.get('thr_f',25) else 0
  if s!=state:continue
  addline(g.intersection(roi),['#B8C2CA','#D8AA82','#B6662E'][s],[1.4,2,2.8][s])
zone=transform(T.transform,shape(json.loads((R/'work/20261011_midterm_deck/build/data/plan_boundary_4326_min.geojson').read_text(encoding='utf8'))['features'][0]['geometry']))
items.append({'points':list(map(list,zone.exterior.coords)),'fill':'#DEEAF2','line':'#235D82','lw':2.1,'closed':True})
places={'west':[219545.38,360905.98],'east':[219944.39,360822.97],'south':[218954.87,360134.24],'north':[220303.89,362114.12],'site':list(zone.centroid.coords)[0]}
areas=[]
for k,p0 in places.items():
 if k=='site':continue
 region=Point(p0).buffer(200);valid=[p for g,p in features if g.intersects(region) and 'we_13' in p]
 areas.append({'area':k,'radius_m':200,'n_links':len(valid),'congested':sum(p['we_13']<p.get('thr_c',15) for p in valid)})
m={'name':'traffic_weekend13','bounds':bb,'w':1200,'h':840,'items':items,'centers':places}
(B/'traffic_revision6_geometry.json').write_text(json.dumps([m],ensure_ascii=False,separators=(',',':')),encoding='utf8')
summary=json.loads((B/'live_traffic_hist_summary.json').read_text(encoding='utf8'))
e={'sources':['https://1tree1.github.io/gj-datamap/data/traffic_hist.geojson','https://1tree1.github.io/gj-datamap/data/traffic_hist_summary.json'],'metric':'ITS link mean speed, not vehicle volume','weekend_dates':summary['days']['we'],'bounds_5187':bb,'selection':'links intersecting displayed map extent; both directional links kept, each once','hours':counts,'local_check_only':areas,'map':m['name'],'geometry':str(B/'traffic_revision6_geometry.json'),'sourceSha256':hashlib.sha256((B/'live_traffic_hist.geojson').read_bytes()).hexdigest()}
(B/'traffic_revision6_evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'hours':counts,'areas':areas,'paths':len(items)},ensure_ascii=False))
