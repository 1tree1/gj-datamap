import json,math
from pathlib import Path
from shapely.geometry import shape,box,mapping
from shapely.ops import transform
R=Path(r'C:\Users\OFFICE\Desktop\9_도시');B=Path(__file__).parent;D=R/'gj-datamap/public/data'
def gj(n):return json.loads((D/(n+'.geojson')).read_text(encoding='utf8'))['features']
zone=json.loads((R/'work/20261011_midterm_deck/build/data/plan_boundary_4326_min.geojson').read_text(encoding='utf8'))['features'][0]['geometry']['coordinates'][0]
lon0=sum(p[0] for p in zone)/len(zone);lat0=sum(p[1] for p in zone)/len(zone)
kx=math.cos(math.radians(lat0))*111320;ky=110574
def xy(p):return [(p[0]-lon0)*kx,(p[1]-lat0)*ky]
def tx(x,y,z=None):return ((x-lon0)*kx,(y-lat0)*ky)
zp=[xy(p) for p in zone];xs,ys=zip(*zp);bounds=[min(xs),min(ys),max(xs),max(ys)]
centers={}
for f in gj('footfall_areas'):
 if f['properties']['id'] not in ['G_seongdong_market_r200','B_haengbok_hwangchon_digitized','H_hwangridan_r300']:continue
 g=f['geometry'];rings=[g['coordinates']] if g['type']=='Polygon' else g['coordinates'];ring=max([p[0] for p in rings],key=len)
 centers[f['properties']['id']]=xy([sum(p[0] for p in ring)/len(ring),sum(p[1] for p in ring)/len(ring)])
# Expand the true geographic extent to include the southern destination and all labels.
extent=[-1200,-1160,1200,840];clip=box(*extent);items=[]
def add(g,fill,line,lw):
 if g.is_empty:return
 if g.geom_type=='Polygon':items.append(dict(points=list(g.exterior.coords),closed=True,fill=fill,line=line,lw=lw))
 elif g.geom_type=='LineString':items.append(dict(points=list(g.coords),closed=False,fill=None,line=line,lw=lw))
 elif hasattr(g,'geoms'):
  for gg in g.geoms:add(gg,fill,line,lw)
def feats(fs,fill,line,lw):
 for f in fs:
  g=transform(tx,shape(f['geometry']))
  if g.intersects(clip):add(g.intersection(clip),fill,line,lw)
feats(gj('parcels'),'#F1F2F3','#FFFFFF',.6)
feats([f for f in gj('parks_upis') if f['properties'].get('lcl_nam') in ('공원','녹지')],'#E2E5E7',None,0)
feats([f for f in gj('urban_roads') if '간선' not in f['properties'].get('cls','')],None,'#D4D8DB',1.3)
feats([f for f in gj('urban_roads') if '간선' in f['properties'].get('cls','')],None,'#B9C0C5',2.1)
feats(gj('rail_abandoned'),None,'#A4ADB4',1.8)
feats(gj('rail_active'),None,'#A4ADB4',2.1)
# Site boundary remains native in PowerPoint; only the geographic background is rasterized.
out=[dict(name='strategy_base_v4',w=1440,h=1200,bounds=extent,items=items)]
(B/'strategy_geometry.json').write_text(json.dumps(out),encoding='utf8')
(B/'strategy_metadata.json').write_text(json.dumps(dict(extent=extent,zone=zp,siteBounds=bounds,centers=centers)),encoding='utf8')
print(json.dumps(dict(extent=extent,siteBounds=bounds,centers=centers,paths=len(items))))
