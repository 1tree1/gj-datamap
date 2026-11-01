# -*- coding: utf-8 -*-
"""최종 도로계획(라이노 선택 객체 = 동측 복사본) → 계획 프레임으로 되돌려 가구 분할·폭·연장 산출, 4326 GeoJSON·지도 PNG 생성."""
import json, math, numpy as np
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, mapping, shape
from shapely.ops import unary_union
from shapely.validation import make_valid
from shapely import affinity
from pyproj import Transformer
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, FancyArrowPatch, Circle
plt.rcParams['font.family']='Malgun Gothic'; plt.rcParams['axes.unicode_minus']=False
R='C:/Users/OFFICE/Desktop/9_도시'; D=R+'/gj-datamap/public/data'
RED='#c8102e'; DARK='#8a0a1f'; INK='#1a1a1a'; G3='#9a9a9a'; G4='#5c5c5c'
S=json.load(open('data/roads_rhino_final.json',encoding='utf-8')); B=json.load(open('data/boundary_rhino_plan.json',encoding='utf-8'))
def poly(face): return make_valid(Polygon(face['outer'],[h for h in face['inner'] if h]))
plan={o['id']:o for o in B['objects']}
# 복사본 이동량: 변하지 않은 북측 도로(3,789)로 계산
sel_road_n=[r for r in S['selected'] if r['layer']=='도로' and abs(r['area']-3789.2)<1][0]
plan_road_n=[o for o in B['objects'] if o['layer']=='도로' and abs(o['area']-3789.2)<1][0]
dx=min(p[0] for p in sel_road_n['faces'][0]['outer'])-min(p[0] for p in plan_road_n['pts']); dy=min(p[1] for p in sel_road_n['faces'][0]['outer'])-min(p[1] for p in plan_road_n['pts'])
print('shift',dx,dy)
roads=[affinity.translate(poly(r['faces'][0]),-dx,-dy) for r in S['selected'] if r['layer']=='도로' and r['type']=='Brep']
walks=[affinity.translate(poly(r['faces'][0]),-dx,-dy) for r in S['selected'] if r['layer']=='보도' and r['type']=='Brep']
U=make_valid(Polygon(B['U_pts']))
RD=unary_union(roads); WK=unary_union(walks)
blocks=U.difference(RD).difference(WK)
bl=[g for g in (blocks.geoms if hasattr(blocks,'geoms') else [blocks]) if g.area>50]
bl.sort(key=lambda g:-g.centroid.y)
print('U',round(U.area),'roads',round(RD.area),'walks',round(WK.area),'blocks',round(sum(g.area for g in bl)),len(bl))
# 계획 획지(프로그램 레이어)와 대조: 각 가구에 가장 많이 겹치는 레이어
lots=[(o['layer'],poly({'outer':o['pts'],'inner':[]})) for o in B['objects'] if o['layer'] not in ('도로','보도') and o['pts']]
rows=[]
for i,g in enumerate(bl):
    best=max(lots,key=lambda t:g.intersection(t[1]).area) if lots else ('',None)
    ov=g.intersection(best[1]).area/g.area if best[1] is not None else 0
    rows.append(dict(no=i+1,area=g.area,layer=best[0] if ov>0.3 else '(신규/통합)',overlap=ov,cx=g.centroid.x,cy=g.centroid.y,w=g.bounds[2]-g.bounds[0],h=g.bounds[3]-g.bounds[1]))
for r in rows: print(r['no'],round(r['area']),r['layer'][:28],round(r['overlap'],2),round(r['w']),'x',round(r['h']))
# 축의 위치(계획 좌표): 남북 보행축 = 동서 두 열 사이 띠, 동서 선형공원 = 중앙 40 m 띠, 차량 횡단 = 도로 루프의 동서 구간
xs=sorted(set([round(b.bounds[0]) for b in bl]+[round(b.bounds[2]) for b in bl])); ys=sorted(set([round(b.bounds[1]) for b in bl]+[round(b.bounds[3]) for b in bl]))
print('block x edges',xs); print('block y edges',ys)
# 도로 폭: 폴리곤 면적/중심선 길이 근사(둘레/2 − 폭 근사 반복)
def width(g):
    L=g.length/2; w=g.area/L
    for _ in range(5): w=g.area/max(L-w,1)
    return w
for i,g in enumerate(roads): print('road',i,round(g.area),'w~',round(width(g),1),'len~',round(g.area/width(g)))
for i,g in enumerate(walks): print('walk',i,round(g.area),'w~',round(width(g),1))
# 저장(계획 좌표 + 4326)
t=np.array([-1143015.56,-1763242.48]); C=np.array([1155149.0,1762445.9]); SHIFT=t+C
T79_87=Transformer.from_crs(5179,5187,always_xy=True); T87_46=Transformer.from_crs(5187,4326,always_xy=True)
def to46(g):
    def f(x,y,z=None):
        x2,y2=T79_87.transform(np.asarray(x)-SHIFT[0],np.asarray(y)-SHIFT[1]); return T87_46.transform(x2,y2)
    from shapely.ops import transform as tr; return tr(f,g)
fc={'type':'FeatureCollection','features':[]}
for i,g in enumerate(roads): fc['features'].append({'type':'Feature','properties':{'kind':'road','area':round(g.area,1)},'geometry':mapping(to46(g))})
for i,g in enumerate(walks): fc['features'].append({'type':'Feature','properties':{'kind':'walk','area':round(g.area,1)},'geometry':mapping(to46(g))})
for r,g in zip(rows,bl): fc['features'].append({'type':'Feature','properties':{'kind':'block','no':r['no'],'area':round(g.area,1),'layer':r['layer']},'geometry':mapping(to46(g))})
json.dump(fc,open('data/road_plan_final_4326.geojson','w',encoding='utf-8'),ensure_ascii=False)
json.dump({'U':[list(p) for p in U.exterior.coords],'roads':[[list(p) for p in g.exterior.coords] for g in roads],'walks':[{'outer':[list(p) for p in g.exterior.coords],'inner':[[list(p) for p in r.coords] for r in g.interiors]} for g in walks],'blocks':[{'no':r['no'],'area':r['area'],'layer':r['layer'],'outer':[list(p) for p in g.exterior.coords]} for r,g in zip(rows,bl)],'lots':[{'layer':l,'outer':[list(p) for p in g.exterior.coords],'area':g.area} for l,g in lots]},open('data/road_plan_final_plan.json','w',encoding='utf-8'),ensure_ascii=False)
json.dump(dict(shift=[dx,dy],U=U.area,roads=RD.area,walks=WK.area,blocks=[dict(no=r['no'],area=r['area'],layer=r['layer'],w=r['w'],h=r['h']) for r in rows],road_widths=[width(g) for g in roads],road_lengths=[g.area/width(g) for g in roads],x_edges=xs,y_edges=ys),open('data/road_plan_final_summary.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('saved')
