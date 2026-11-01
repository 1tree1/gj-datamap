import json,struct,math
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,box,shape
from shapely.ops import transform
from pyproj import Transformer
R=Path(r'C:\Users\OFFICE\Desktop\9_도시');B=R/'work/20261011_analysis_redesign/build';S=R/'대지/(B020)연속수치지도_202609132098'
T=Transformer.from_crs(5179,5187,always_xy=True);LL=Transformer.from_crs(4326,5187,always_xy=True)
BB=[219180,360210,220360,361680];roi=box(*BB);center=[219770,360945]
def project(x,y,z=0):
 x-=center[0];y-=center[1]
 return [x*.86+y*.50,-x*.22+y*.34+z*2.5]
db=(S/'N3A_B0010000.dbf').read_bytes();hl,rl=struct.unpack_from('<HH',db,8);off=1;flooroff=0
for o in range(32,hl-1,32):
 name=db[o:o+11].split(b'\0')[0].decode('ascii');ln=db[o+16]
 if name=='nmly':flooroff=off;floorlen=ln
 off+=ln
data=(S/'N3A_B0010000.shp').read_bytes();pos=100;rows=[];unknown=0
while pos<len(data):
 idx,ln=struct.unpack_from('>2i',data,pos);rec=data[pos+8:pos+8+ln*2];pos+=8+ln*2
 if struct.unpack_from('<i',rec)[0]!=5:continue
 floors=db[hl+(idx-1)*rl+flooroff:hl+(idx-1)*rl+flooroff+floorlen].strip()
 floors=int(floors) if floors.isdigit() else 0
 npar,npts=struct.unpack_from('<2i',rec,36);starts=list(struct.unpack_from('<'+str(npar)+'i',rec,44))+[npts]
 pts=np.array(struct.unpack_from('<'+str(npts*2)+'d',rec,44+4*npar)).reshape(-1,2);xx,yy=T.transform(pts[:,0],pts[:,1]);pts=np.c_[xx,yy]
 for i in range(npar):
  ps=pts[starts[i]:starts[i+1]]
  if len(ps)<4:continue
  g=Polygon(ps).buffer(0)
  if g.is_empty or not g.intersects(roi):continue
  g=g.intersection(roi).simplify(.15)
  for poly in ([g] if g.geom_type=='Polygon' else list(getattr(g,'geoms',[]))):
   if poly.geom_type=='Polygon' and poly.area>2:rows.append((poly,floors))
items=[]
def item(ps,fill,line=None,lw=.4,closed=True):items.append({'points':ps,'fill':fill,'line':line,'lw':lw,'closed':closed})
ground=[project(x,y) for x,y in list(roi.exterior.coords)];item(ground,'#F4F3EF')
maps=json.loads((B/'geometry.json').read_text(encoding='utf8'))
base=next(m for m in maps if m['name']=='site_fabric')
for it in base['items']:
 if not it['fill'] and it['line']!='#C8102E':
  item([project(x,y) for x,y in it['points']],None,'#C9CECF',.8,False)
zone=transform(LL.transform,shape(json.loads((R/'work/20261011_midterm_deck/build/data/plan_boundary_4326_min.geojson').read_text(encoding='utf8'))['features'][0]['geometry']))
item([project(x,y) for x,y in zone.exterior.coords],'#E5B9B1','#B35348',1.8)
obj=['# NGII actual footprints; nmly storeys; assumed 3.5 metres per storey.']
vertex_count=0
rows.sort(key=lambda row:project(row[0].centroid.x,row[0].centroid.y)[1],reverse=True)
for g,f in rows:
 ps=list(g.exterior.coords)[:-1];height=max(f,1)*3.5
 shadow=[project(x+height*.50,y-height*.35) for x,y in ps];item(shadow,'#E1DFDB')
 # Geographic mesh is at actual XY and assumed floor height. Exaggeration exists
 # only in the illustration projection, not in the exported model.
 for x,y in ps:obj.append(f'v {x-center[0]:.3f} {y-center[1]:.3f} 0')
 for x,y in ps:obj.append(f'v {x-center[0]:.3f} {y-center[1]:.3f} {height:.3f}')
 n=len(ps)
 for j,(a,b) in enumerate(zip(ps,ps[1:]+ps[:1])):
  k=(j+1)%n
  obj.append('f '+' '.join(str(vertex_count+t+1) for t in [j,k,k+n,j+n]))
  if (b[1]-a[1])+(b[0]-a[0])>0:
   shade='#DDDCD8' if b[0]-a[0]>0 else '#EAE9E5'
   item([project(*a),project(*b),project(*b,height),project(*a,height)],shade,'#BCC2C5',.35)
 item([project(x,y,height) for x,y in ps],'#FFFFFF' if f else '#EFF0ED','#C0C6C7',.4)
 obj.append('f '+' '.join(str(vertex_count+n+j+1) for j in range(n)))
 vertex_count+=n*2
(B/'assets/context_massing.obj').write_text('\n'.join(obj),encoding='utf8')
xs=[q[0] for i in items for q in i['points']];ys=[q[1] for i in items for q in i['points']]
m={'name':'context_massing','bounds':[min(xs)-30,min(ys)-30,max(xs)+30,max(ys)+30],'w':1800,'h':900,'items':items,'centers':{'site':project(zone.centroid.x,zone.centroid.y),'west':project(219650,360980),'east':project(219944,360850)},'buildings':len(rows)}
(B/'massing_geometry.json').write_text(json.dumps([m],ensure_ascii=False,separators=(',',':')),encoding='utf8')
maps=[x for x in maps if x['name']!='context_massing']+[m];(B/'geometry.json').write_text(json.dumps(maps,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('massing',len(rows),'buildings',len(items),'faces')
