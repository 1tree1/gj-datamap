# 최종 경계(라이노 계획 프레임 합집합 U) → EPSG:5179/5187/4326 변환, 면적·고시구역 대비·규제 비율·획지율 재산정
# 변환: real5179 = P − (t + C),  t = xf_final(masterplan_v1), C = boundary_check 검증 상수 (고시 구역 IoU 1.0000)
import json, numpy as np, collections
from pyproj import Transformer
from shapely.geometry import Polygon, shape, mapping, MultiPolygon
from shapely.ops import transform as shp_transform, unary_union
from shapely.validation import make_valid
R='C:/Users/OFFICE/Desktop/9_도시'
t=np.array([-1143015.56,-1763242.48]); C=np.array([1155149.0,1762445.9]); SHIFT=t+C   # (12133.44, -796.58)
T79_87=Transformer.from_crs(5179,5187,always_xy=True); T87_46=Transformer.from_crs(5187,4326,always_xy=True); T46_87=Transformer.from_crs(4326,5187,always_xy=True)
def p2_87(pts):
    a=np.array(pts)[:,:2]-SHIFT; x,y=T79_87.transform(a[:,0],a[:,1]); return list(zip(x,y))
def to46(g): return shp_transform(lambda x,y,z=None:T87_46.transform(x,y),g)
def to87(g): return shp_transform(lambda x,y,z=None:T46_87.transform(x,y),g)
B=json.load(open('data/boundary_rhino_plan.json',encoding='utf-8'))
U=make_valid(Polygon(p2_87(B['U_pts'])))
pts=np.array(B['U_pts']); W=pts[:,0].max()-pts[:,0].min(); H=pts[:,1].max()-pts[:,1].min()
out={'U_area_rhino':B['U_area'],'U_area_5187':U.area,'width_m':W,'height_m':H,'perimeter_m':U.length}
# 고시 구역(아카이브 5187)
gz=json.load(open(R+'/archive/C_data/processed/gosi2026-8_zone_5187.geojson',encoding='utf-8'))
Z=unary_union([make_valid(shape(f['geometry'])) for f in gz['features']])
out['gosi_area']=Z.area; out['U_in_gosi']=U.intersection(Z).area; out['U_out_gosi']=U.difference(Z).area; out['gosi_out_U']=Z.difference(U).area
# 이전 경계(218,478)
old=shape(json.load(open(R+'/work/20261005_boundary_check/user_boundary_current_5187.geojson',encoding='utf-8'))['features'][0]['geometry']).buffer(0)
out['old_area']=old.area; out['iou_old']=U.intersection(old).area/U.union(old).area; out['U_minus_old']=U.difference(old).area; out['old_minus_U']=old.difference(U).area
# 용도지역 비율 (웹맵 landuse 4326)
lu=json.load(open(R+'/gj-datamap/public/data/landuse.geojson',encoding='utf-8'))['features']
acc=collections.Counter()
for f in lu:
    g=make_valid(to87(shape(f['geometry']))); a=U.intersection(g).area
    if a>1: acc[f['properties']['uname']]+=a
out['landuse_pct']={k:round(v/U.area*100,1) for k,v in acc.most_common()}; out['landuse_cov']=round(sum(acc.values())/U.area*100,1)
# 고도지구 (아카이브 5187)
gd=json.load(open(R+'/archive/C_data/processed/godo_5187.geojson',encoding='utf-8'))['features']
acc=collections.Counter(); keys=set()
for f in gd:
    p=f['properties']; keys.update(p.keys()); g=make_valid(shape(f['geometry'])); a=U.intersection(g).area
    if a>1: acc[str(p.get('h_max') or p.get('lbl') or p.get('godo_nm'))]+=a
out['godo_pct']={k:round(v/U.area*100,1) for k,v in acc.most_common()}; out['godo_cov']=round(sum(acc.values())/U.area*100,1); out['godo_keys']=sorted(keys)
# 라이노 계획 객체 면적 집계(계획 프레임)
lay=collections.Counter()
for o in B['objects']: lay[o['layer']]+=o['area']
out['layers']={k:round(v,1) for k,v in lay.items()}
road=lay['도로']; walk=lay['보도']; opn=lay['오픈스페이스']; bld=sum(v for k,v in lay.items() if k not in ('도로','보도','오픈스페이스'))
out['sum_road']=road; out['sum_walk']=walk; out['sum_open']=opn; out['sum_building_lots']=bld; out['sum_all']=road+walk+opn+bld
out['parcel_ratio']=bld/B['U_area']
# GeoJSON 4326 저장
def fc(geoms,props):
    return {'type':'FeatureCollection','features':[{'type':'Feature','properties':p,'geometry':mapping(to46(g))} for g,p in zip(geoms,props)]}
json.dump(fc([U],[{'name':'계획 경계(최종, 라이노 합집합)','area_m2':round(U.area,1),'rhino_area':B['U_area']}]),open('data/plan_boundary_4326.geojson','w',encoding='utf-8'),ensure_ascii=False)
json.dump(fc([U],[{'name':'계획 경계'}]) ,open('data/plan_boundary_4326_min.geojson','w',encoding='utf-8'),ensure_ascii=False)
pg=[];pp=[]
for o in B['objects']:
    if o['pts']: pg.append(make_valid(Polygon(p2_87(o['pts'])))); pp.append({'layer':o['layer'],'area':round(o['area'],1)})
json.dump(fc(pg,pp),open('data/plan_parcels_4326.geojson','w',encoding='utf-8'),ensure_ascii=False)
json.dump(out,open('data/boundary_final.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(json.dumps(out,ensure_ascii=False,indent=1))
