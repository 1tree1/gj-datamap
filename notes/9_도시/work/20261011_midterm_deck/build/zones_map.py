# 권역 구성도 — 라이노 계획 프레임 획지(최종)를 권역 A~E로 묶어 레드+흑백으로 그린다
import json, math
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
plt.rcParams['font.family']='Malgun Gothic'; plt.rcParams['axes.unicode_minus']=False
RED='#c8102e'; DARK='#8a0a1f'; INK='#1a1a1a'
P=json.load(open('data/plan_parcels_4326.geojson',encoding='utf-8'))['features']
B=json.load(open('data/plan_boundary_4326_min.geojson',encoding='utf-8'))['features'][0]['geometry']['coordinates'][0]
lon0=sum(p[0] for p in B)/len(B); lat0=sum(p[1] for p in B)/len(B)
KX=math.cos(math.radians(lat0))*111320; KY=110574
def xy(p): return ((p[0]-lon0)*KX,(p[1]-lat0)*KY)
def zone_of(layer):
    if layer.startswith('시청'): return 'A'
    if layer.startswith('청년주거') or layer.startswith('생활편의'): return 'B'
    if layer.startswith('청년 오피스'): return 'C'
    if layer.startswith('예술인') or layer.startswith('성동시장'): return 'D'
    if layer.startswith('관광휴게') or layer.startswith('공연장'): return 'E'
    if layer.startswith('관광지원'): return 'P'
    if layer=='오픈스페이스': return 'O'
    if layer=='보도': return 'W'
    if layer=='도로': return 'R'
    return '?'
COL={'A':DARK,'B':RED,'C':'#e05a6e','D':'#f0a0ad','E':'#b1121f','P':'#6a6a6a','O':'#d6d6d6','W':'#efefef','R':'#ffffff'}
NAME={'A':'A 공공청사·의회','B':'B 일상생활(청년·신혼 주거·생활편의)','C':'C 청년 업무권','D':'D 창작·체험권·시장 접점','E':'E 역사문화예술권(구 역사·전시·공연)','P':'기반(관광지원·주차전용건축물)','O':'오픈스페이스','W':'보행공간·광장','R':'도로'}
f=plt.figure(figsize=(4.6,9.0),dpi=200); ax=f.add_axes([0,0,1,1]); ax.set_aspect('equal'); ax.axis('off')
ax.add_patch(MPoly([xy(p) for p in B],closed=True,fc='#f7f7f7',ec='none',zorder=0))
order={'R':1,'W':2,'O':3,'P':4,'A':5,'B':5,'C':5,'D':5,'E':5}
labels={}
for ft in sorted(P,key=lambda t:order.get(zone_of(t['properties']['layer']),9)):
    z=zone_of(ft['properties']['layer']); g=ft['geometry']
    rings=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
    for pg in rings:
        pts=[xy(p) for p in pg[0]]
        ax.add_patch(MPoly(pts,closed=True,fc=COL.get(z,'#ccc'),ec='#ffffff' if z in ('W','R') else '#ffffff',lw=0.9,zorder=order.get(z,9)))
        if z in 'ABCDEP' and ft['properties']['area']>7000:
            cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
            labels.setdefault(z,[]).append((cx,cy,ft['properties']['area']))
for z,L in labels.items():
    for cx,cy,a in L:
        ax.text(cx,cy,z if z!='P' else '주차',ha='center',va='center',fontsize=16 if z!='P' else 11,fontweight='bold',color='white' if z in ('A','B','E','P','C') else INK,zorder=10)
ax.add_patch(MPoly([xy(p) for p in B],closed=True,fc='none',ec=INK,lw=1.6,zorder=11))
xs=[xy(p)[0] for p in B]; ys=[xy(p)[1] for p in B]
ax.set_xlim(min(xs)-40,max(xs)+40); ax.set_ylim(min(ys)-40,max(ys)+40)
f.savefig('assets/zones_map.png',facecolor='white'); plt.close(f)
json.dump(NAME,open('data/zone_names.json','w',encoding='utf-8'),ensure_ascii=False)
print('ok zones_map')
