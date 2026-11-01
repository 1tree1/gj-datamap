import json,struct,math
from pathlib import Path
import numpy as np
from pyproj import Transformer
import shapely
from shapely.geometry import Polygon,LineString,box,shape
from shapely.ops import transform
R=Path(r'C:\Users\OFFICE\Desktop\9_도시'); B=R/'work/20261011_analysis_redesign/build';S=R/'대지/(B020)연속수치지도_202609132098'
T=Transformer.from_crs(5179,5187,always_xy=True);T4=Transformer.from_crs(4326,5187,always_xy=True)
def read(name):
 data=(S/(name+'.shp')).read_bytes(); pos=100; out=[]
 while pos<len(data):
  _,ln=struct.unpack_from('>2i',data,pos); rec=data[pos+8:pos+8+ln*2];pos+=8+ln*2
  ty=struct.unpack_from('<i',rec)[0]
  if ty not in [3,5]:continue
  npar,npts=struct.unpack_from('<2i',rec,36);starts=list(struct.unpack_from('<'+str(npar)+'i',rec,44))+[npts]; pts=np.array(struct.unpack_from('<'+str(npts*2)+'d',rec,44+4*npar)).reshape(-1,2);xx,yy=T.transform(pts[:,0],pts[:,1]);pts=np.c_[xx,yy]
  for i in range(npar):
   ps=pts[starts[i]:starts[i+1]]
   if len(ps)>= (3 if ty==5 else 2):
    g=Polygon(ps).buffer(0) if ty==5 else LineString(ps)
    if not g.is_empty:out.append(g)
 return out
bld=read('N3A_B0010000');road=read('N3L_A0020000');wall=read('N3L_B0020000');water=read('N3A_E0010001');rail=read('N3L_A0171119')
zone4326=json.loads((R/'work/20261011_midterm_deck/build/data/plan_boundary_4326_min.geojson').read_text(encoding='utf8'))['features'][0]['geometry'];zone=transform(T4.transform,shape(zone4326))
OBS=np.array(bld+[g.buffer(.15) for g in wall],dtype=object); tree=shapely.STRtree(OBS)
def coords(g):
 if g.geom_type=='Polygon':return [list(map(list,g.exterior.coords))]
 if g.geom_type=='LineString':return [list(map(list,g.coords))]
 if hasattr(g,'geoms'):return sum([coords(x) for x in g.geoms],[])
 return []
def add_g(items,g,fill=None,line=None,lw=.8):
 for p in coords(g):items.append({'points':p,'fill':fill,'line':line,'lw':lw,'closed':g.geom_type in ['Polygon','MultiPolygon']})
def map_(name,bounds,orientation=False):
 roi=box(*bounds);items=[]
 for g in water:
  if g.intersects(roi):add_g(items,g.intersection(roi),'#C8DDE5')
 for g in bld:
  if g.intersects(roi):add_g(items,g.intersection(roi),'#E1E4E7' if orientation else '#BDC1C7')
 for g in road:
  if g.intersects(roi):
   c='#87929A';lw=.65
   if orientation:
    ps=list(g.coords)
    for a,b in zip(ps,ps[1:]):
     az=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))%90;dev=min(abs(az-89.2),90-abs(az-89.2));c='#245E89' if dev<=7.5 else '#AEB5BC'
     add_g(items,LineString([a,b]).intersection(roi),None,c,2.1 if dev<=7.5 else .8)
   else:add_g(items,g.intersection(roi),None,c,lw)
 for g in rail:
  if g.intersects(roi):add_g(items,g.intersection(roi),None,'#969696',1.0)
 add_g(items,zone,'#FBE7E9','#C8102E',2)
 return {'name':name,'bounds':bounds,'w':1200,'h':1000,'items':items}
maps=[map_('city_structure',[218150,360000,221800,362000],True),map_('site_fabric',[219150,360250,220420,361650])]
maps[0]['w']=1800;maps[0]['h']=1000
areas=json.loads((R/'archive/C_data/processed/footfall_areas_web_4326.geojson').read_text(encoding='utf8'))['features']
areas={f['properties']['id']:transform(T4.transform,shape(f['geometry'])) for f in areas}
for name,ids,bb in [('activity_ew',['G_seongdong_market_r200','B_haengbok_hwangchon_digitized','D_zone'],[219150,360250,220420,361650]),('activity_ns',['F_cityhall_r500','H_hwangridan_r300'],[218650,359200,221400,362900])]:
 m=map_(name,bb);m['w']=1100;m['h']=1250;m['centers']={}
 for key,c in zip(ids,['#245E89','#AA6317','#636B74']):
  g=areas[key].intersection(box(*bb));m['centers'][key]=list(areas[key].centroid.coords)[0]
  k=len(m['items']);add_g(m['items'],g,c);add_g(m['items'],g,None,c,3)
  for it in m['items'][k:]:
   if it['fill']:it['opacity']=24
 maps.append(m)
RD=json.loads((R/'archive/90_derived/gj_reading_20260928.json').read_text(encoding='utf8'))
for idx in [0,2,5]:
 v=RD['isovists'][idx];x,y=v['x'],v['y'];bb=[x-160,y-155,x+160,y+155];roi=box(*bb);its=[]
 for g in bld:
  if g.intersects(roi):add_g(its,g.intersection(roi),'#C1C6CC')
 for g in wall:
  if g.intersects(roi):add_g(its,g.intersection(roi),None,'#636B74',.8)
 ang=np.linspace(0,2*np.pi,720,endpoint=False);starts=np.tile([x,y],(720,1));ends=starts+150*np.c_[np.cos(ang),np.sin(ang)];rays=shapely.linestrings(np.stack([starts,ends],axis=1));dist=np.full(720,150.);pair=tree.query(rays,predicate='intersects')
 inter=shapely.intersection(rays[pair[0]],OBS[pair[1]]);dd=shapely.distance(shapely.points(starts[pair[0]]),inter);np.minimum.at(dist,pair[0],dd)
 iso=Polygon(starts+dist[:,None]*np.c_[np.cos(ang),np.sin(ang)]);add_g(its,iso,'#C8102E','#96152A',1)
 add_g(its,shapely.Point(x,y).buffer(2),'#FFFFFF','#16212B',1)
 print(v['type'],round(iso.area),v['area'])
 maps.append({'name':'isovist_'+str(idx),'bounds':bb,'w':1100,'h':1065,'items':its})
(B/'geometry.json').write_text(json.dumps(maps,separators=(',',':'),ensure_ascii=False),encoding='utf8');print('MAPS',[(m['name'],len(m['items'])) for m in maps])
