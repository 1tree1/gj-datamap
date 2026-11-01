# -*- coding: utf-8 -*-
"""최종 도로계획 지도 3종(레드+흑백, 북쪽 위): axes_map(도시축 구상) · road_plan_map(도로계획도) · blocks_map(가구·획지 분할도)"""
import json, math, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, FancyArrowPatch, Circle
from matplotlib.collections import PatchCollection, LineCollection
from shapely.geometry import Polygon, shape
plt.rcParams['font.family']='Malgun Gothic'; plt.rcParams['axes.unicode_minus']=False
R='C:/Users/OFFICE/Desktop/9_도시'; D=R+'/gj-datamap/public/data'
RED='#c8102e'; DARK='#8a0a1f'; INK='#1a1a1a'; G2='#d9d9d9'; G3='#9a9a9a'; G4='#5c5c5c'; PALE='#f7d9dd'
P=json.load(open('data/road_plan_final_plan.json',encoding='utf-8'))
SHIFT=np.array([-1143015.56+1155149.0,-1763242.48+1762445.9])   # 계획좌표 → 5179 = P − SHIFT
# 맥락 레이어(4326) → 5179 평면 근사: 계획 좌표계와 맞추기 위해 pyproj로 4326→5179 변환 후 +SHIFT
from pyproj import Transformer
T46_79=Transformer.from_crs(4326,5179,always_xy=True)
def gj(n): return json.load(open(f'{D}/{n}.geojson',encoding='utf-8'))['features']
def rings(f):
    g=f['geometry']; return [g['coordinates']] if g['type']=='Polygon' else (g['coordinates'] if g['type']=='MultiPolygon' else [])
def lines(f):
    g=f['geometry']; return [g['coordinates']] if g['type']=='LineString' else (g['coordinates'] if g['type']=='MultiLineString' else [])
def toP(coords):
    a=np.array(coords)[:,:2]; x,y=T46_79.transform(a[:,0],a[:,1]); return np.column_stack([x+SHIFT[0],y+SHIFT[1]])
Uc=np.array(P['U']); xmin,ymin=Uc.min(0); xmax,ymax=Uc.max(0); xc=(xmin+xmax)/2; yc=(ymin+ymax)/2
PARCELS=gj('parcels'); ROADS=gj('urban_roads'); RAILA=gj('rail_abandoned'); PARKS=gj('parks_upis'); FOOT={f['properties']['id']:f for f in gj('footfall_areas')}
def fig(w,h):
    f=plt.figure(figsize=(w,h),dpi=200); ax=f.add_axes([0,0,1,1]); ax.set_aspect('equal'); ax.axis('off'); return f,ax
def base(ax,cx,cy,hw,hh):
    pats=[MPoly(toP(pg[0]),closed=True) for f in PARCELS for pg in rings(f)]
    ax.add_collection(PatchCollection(pats,facecolor='#ececec',edgecolor='#ffffff',linewidths=0.35,zorder=1))
    pats=[MPoly(toP(pg[0]),closed=True) for f in PARKS if f['properties'].get('lcl_nam') in ('공원','녹지') for pg in rings(f)]
    if pats: ax.add_collection(PatchCollection(pats,facecolor='#dcdcdc',edgecolor='none',zorder=0.5))
    segs=[toP(ln) for f in ROADS if '간선' in f['properties']['cls'] for ln in lines(f)]; ax.add_collection(LineCollection(segs,colors='#8f8f8f',linewidths=1.5,zorder=2))
    segs=[toP(ln) for f in ROADS if '간선' not in f['properties']['cls'] for ln in lines(f)]; ax.add_collection(LineCollection(segs,colors='#b5b5b5',linewidths=0.9,zorder=2))
    segs=[toP(ln) for f in RAILA for ln in lines(f)]; ax.add_collection(LineCollection(segs,colors='#444444',linewidths=1.0,zorder=3,linestyles=(0,(3,2))))
    ax.set_xlim(cx-hw,cx+hw); ax.set_ylim(cy-hh,cy+hh)
def scalebar(ax,x,y,m=200): ax.plot([x,x+m],[y,y],color=INK,lw=2,zorder=9); ax.text(x+m/2,y+10,f'{m} m',ha='center',va='bottom',fontsize=13,color=INK,zorder=9)
def north(ax,x,y,s=50): ax.annotate('',xy=(x,y+s),xytext=(x,y),arrowprops=dict(arrowstyle='-|>',color=INK,lw=1.2),zorder=9); ax.text(x,y+s+8,'N',ha='center',va='bottom',fontsize=11,color=INK,fontweight='bold',zorder=9)
def plan_layers(ax,label_blocks=False,lots=False,walk_c=G2,road_c=G4,block_c='#ffffff'):
    ax.add_patch(MPoly(Uc,closed=True,fc=PALE,ec='none',zorder=3.5))
    for b in P['blocks']: ax.add_patch(MPoly(np.array(b['outer']),closed=True,fc=block_c,ec='#bdbdbd',lw=0.6,zorder=4))
    for w in P['walks']:
        ax.add_patch(MPoly(np.array(w['outer']),closed=True,fc=walk_c,ec='none',zorder=4.5))
        for r in w['inner']: ax.add_patch(MPoly(np.array(r),closed=True,fc=block_c,ec='#bdbdbd',lw=0.6,zorder=4.6))
    for r in P['roads']: ax.add_patch(MPoly(np.array(r),closed=True,fc=road_c,ec='none',zorder=5))
    ax.add_patch(MPoly(Uc,closed=True,fc='none',ec=RED,lw=2.0,zorder=6))
    if lots:
        for l in P['lots']: ax.add_patch(MPoly(np.array(l['outer']),closed=True,fc='none',ec=RED,lw=0.8,ls=(0,(2,2)),zorder=5.5))
    if label_blocks:
        for b in P['blocks']:
            g=Polygon(b['outer']); c=g.representative_point()
            ax.text(c.x,c.y,f"{b['no']}\n{b['area']:,.0f}㎡",ha='center',va='center',fontsize=13,fontweight='bold',color=INK,zorder=8,bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='none',alpha=0.85))
# 축 좌표(계획 좌표): 가구 가장자리에서 읽음
S=json.load(open('data/road_plan_final_summary.json',encoding='utf-8'))
xs,ys=S['x_edges'],S['y_edges']
# 남북 보행축: 두 열 사이 띠 (x 1167373~1167403) / 동서 선형공원: y 1761576~1761616 / 차량 횡단(화랑로 연결): 도로 루프 동서 구간 y≈1761434~1761459
NS=( (1167373+1167403)/2, 1761454, 1761984 ); EW=( (1761576+1761616)/2, xmin, xmax ); HW=( 1761446, xmin, xmax )
cH=FOOT['H_hwangridan_r300']; cHx,cHy=toP([np.mean(np.array(cH['geometry']['coordinates'][0]),axis=0)])[0]
cG=FOOT['G_seongdong_market_r200']; cGx,cGy=toP([np.mean(np.array(cG['geometry']['coordinates'][0]),axis=0)])[0]
# (A) 도시축 구상도
f,ax=fig(7.2,9.2); base(ax,xc,yc,560,720)
ax.add_patch(MPoly(Uc,closed=True,fc=PALE,ec=INK,lw=1.8,zorder=3.5))
ax.add_patch(FancyArrowPatch((NS[0],ymin-150),(NS[0],ymax+120),arrowstyle='<|-|>',mutation_scale=16,color=RED,lw=2.6,zorder=7)); ax.text(NS[0]+14,ymax+60,'① 남북축(대지축)',fontsize=15,fontweight='bold',color=RED,zorder=8)
ax.add_patch(FancyArrowPatch((xmin-420,EW[0]),(xmax+420,EW[0]),arrowstyle='<|-|>',mutation_scale=16,color=RED,lw=2.6,zorder=7)); ax.text(xmin-410,EW[0]+14,'② 동서축(성동시장 ↔ 전랑지) · 폭 40 m 선형공원',fontsize=15,fontweight='bold',color=RED,zorder=8)
# ③ 역사유적축: 사용자 수정(2026-10-12 파란 선) — ①×② 교점을 지나 남남서(대릉원·황리단길) ↔ 북북동, 구상도 기울기(서 1,030 : 남 1,440)
ang=math.atan2(-1440,-1030); L=1050; px0,py0=NS[0],EW[0]
ax.add_patch(FancyArrowPatch((px0-L*math.cos(ang)*0.62,py0-L*math.sin(ang)*0.62),(px0+L*math.cos(ang),py0+L*math.sin(ang)),arrowstyle='-|>',mutation_scale=16,color=RED,lw=2.4,ls=(0,(6,3)),zorder=7))
ax.text(px0-L*math.cos(ang)*0.62-25,py0-L*math.sin(ang)*0.62-25,'③ 역사유적축\n(대릉원·황리단길 ↔ 북동)',fontsize=15,fontweight='bold',color=RED,zorder=8,ha='right',va='top')
ax.add_patch(FancyArrowPatch((xmin-420,HW[0]),(xmax+420,HW[0]),arrowstyle='-',color=INK,lw=5,alpha=0.35,zorder=6.5)); ax.text(xmax+40,HW[0]-40,'화랑로 연결(차량)',fontsize=14,fontweight='bold',color=INK,zorder=8)
yv=1761878; ax.add_patch(FancyArrowPatch((xmin-420,yv),(xmax+40,yv),arrowstyle='<|-',mutation_scale=14,color=G4,lw=1.8,ls=(0,(4,2)),zorder=6.5)); ax.text(xmin-410,yv+14,'향일문 조망 보행로 → 경주읍성',fontsize=14,fontweight='bold',color=G4,zorder=8)
ax.add_patch(FancyArrowPatch((NS[0],ymax+120),(NS[0]-120,ymax+330),arrowstyle='<|-',mutation_scale=14,color=G4,lw=1.8,zorder=6.5)); ax.text(NS[0]-110,ymax+340,'북천 · 황성공원 방면',fontsize=14,fontweight='bold',color=G4,zorder=8,ha='center')
ax.plot(cGx,cGy,'o',color=INK,ms=7,zorder=8); ax.text(cGx,cGy-40,'성동시장',ha='center',va='top',fontsize=14,fontweight='bold',color=INK,zorder=8)
scalebar(ax,xc-520,yc-690); north(ax,xc+500,yc+600)
f.savefig('assets/axes_map.png',facecolor='white'); plt.close(f); print('ok axes_map')
# (B) 도로계획도
f,ax=fig(7.2,9.2); base(ax,xc,yc,560,720); plan_layers(ax)
for (x,y,t,rot) in [(NS[0],1761720,'남북 보행축 30 m',90),(xc,EW[0],'동서 선형공원 40 m',0),(xc+10,HW[0],'화랑로 연결 · 차량 12 m',0),(xmax-20,1761700,'외곽 차량 가로 12 m',90)]:
    ax.text(x,y,t,rotation=rot,ha='center',va='center',fontsize=13.5,fontweight='bold',color=INK if 'm' in t else RED,zorder=8,bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='none',alpha=0.9))
scalebar(ax,xc-520,yc-690); north(ax,xc+500,yc+600)
f.savefig('assets/road_plan_map.png',facecolor='white'); plt.close(f); print('ok road_plan_map')
# (C) 가구·획지 분할도
f,ax=fig(7.2,9.2); base(ax,xc,yc,560,720); plan_layers(ax,label_blocks=True,lots=True)
scalebar(ax,xc-520,yc-690); north(ax,xc+500,yc+600)
f.savefig('assets/blocks_map.png',facecolor='white'); plt.close(f); print('ok blocks_map')
# (D) 도로계획도 — 단독(맥락 없이, 범례용 큰 글씨)
f,ax=fig(3.2,8.6); ax.set_xlim(xmin-40,xmax+40); ax.set_ylim(ymin-40,ymax+40); plan_layers(ax)
f.savefig('assets/road_plan_solo.png',facecolor='white'); plt.close(f); print('ok road_plan_solo')
