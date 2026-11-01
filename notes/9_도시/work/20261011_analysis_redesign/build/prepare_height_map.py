from pathlib import Path
import sys,json,math,collections
sys.path.insert(0,str(Path(__file__).parent/'rhythm_vendor'))
import shapefile
from shapely.geometry import shape,box,mapping
from shapely.ops import transform
from pyproj import Transformer
R=Path(r'C:\Users\OFFICE\Desktop\9_도시');B=Path(__file__).parent;D=B/'height_map_data';D.mkdir(exist_ok=True)
S=R/'대지/(B020)연속수치지도_202609132098';T=Transformer.from_crs(5179,5187,always_xy=True)
zone=shape(json.loads((R/'archive/C_data/processed/gosi2026-8_zone_5187.geojson').read_text(encoding='utf8'))['features'][0]['geometry']).buffer(0)
# Map and comparison use the same officially notified boundary, not the design outline.
H=1240;W=H*590/372;cx=(zone.bounds[0]+zone.bounds[2])/2;cy=(zone.bounds[1]+zone.bounds[3])/2;extent=[cx-W/2,cy-H/2,cx+W/2,cy+H/2];roi=box(*extent)
def save(name,features):
 j={'type':'FeatureCollection','name':name,'crs':{'type':'name','properties':{'name':'EPSG:5187'}},'features':features};(D/(name+'.geojson')).write_text(json.dumps(j,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def feat(g,p):return {'type':'Feature','properties':p,'geometry':mapping(g)}
counts=collections.Counter();sidecounts={'west':collections.Counter(),'east':collections.Counter()};build=[]
reader=shapefile.Reader(str(S/'N3A_B0010000'),encoding='utf8',encodingErrors='replace');fields=[f[0] for f in reader.fields[1:]]
for rec in reader.iterShapeRecords():
 # Filter in source CRS before projecting complex geometries.
 g=transform(T.transform,shape(rec.shape.__geo_interface__))
 if not g.is_valid:g=g.buffer(0)
 if g.is_empty or not g.intersects(roi):continue
 a=dict(zip(fields,rec.record));raw=a.get('nmly');floors=int(raw) if raw is not None and int(raw)>0 else None
 cls='unknown' if floors is None else '1' if floors==1 else '2' if floors==2 else '3-5' if floors<=5 else '6+'
 counts[cls]+=1
 c=g.centroid;dist=zone.distance(c);side=None
 if 0<dist<150:
  q=zone.exterior.interpolate(zone.exterior.project(c));ang=math.degrees(math.atan2(c.y-q.y,c.x-q.x))%360;side='east' if ang<45 or ang>=315 else 'west' if 135<=ang<225 else None
  if side:sidecounts[side][cls]+=1
 build.append(feat(g.intersection(roi),{'floors':floors,'height_class':cls,'side150':side or '', 'gid':a.get('gid')}))
save('buildings',build)
for layer,name in [('N3L_A0020000','roads'),('N3A_E0010001','water')]:
 out=[];reader=shapefile.Reader(str(S/layer),encoding='utf8',encodingErrors='replace')
 for rec in reader.iterShapeRecords():
  g=transform(T.transform,shape(rec.shape.__geo_interface__))
  if not g.is_valid:g=g.buffer(0)
  if g.is_empty or not g.intersects(roi):continue
  out.append(feat(g.intersection(roi),{}))
 save(name,out)
save('boundary',[feat(zone,{'name':'고시구역'})]);save('band150',[feat(zone.buffer(150).difference(zone),{'name':'경계 밖 150m'})])
meta={'extent':extent,'imageSize':[2360,1488],'crs':'EPSG:5187','sourceLayer':'NGII N3A_B0010000','field':'nmly','measure':'지상층수 (실측 높이 m가 아님)','classes':['1','2','3-5','6+','unknown'],'counts':dict(counts),'comparisonBand150':{k:dict(v) for k,v in sidecounts.items()},'zoneBounds':list(zone.bounds),'boundarySource':'경주시 고시 제2026-8호 도면 추출 구역계','dataFolder':str(D)}
(B/'height_map_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(meta,ensure_ascii=True))
