# 소재 이미지 일괄 생성
# 1) 웹맵 캡처 재채색(레드+흑백)  2) 항공사진 흑백  3) 웹맵 원본 벡터(GeoJSON 4326)에서 직접 그린 지도·다이어그램
import os, json, math, numpy as np
from PIL import Image, ImageOps
from recolor import recolor
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, FancyArrowPatch, Circle, Rectangle
from matplotlib.collections import PatchCollection, LineCollection
plt.rcParams['font.family']='Malgun Gothic'; plt.rcParams['axes.unicode_minus']=False

R='C:/Users/OFFICE/Desktop/9_도시'
VA=R+'/work/20261011_visual_front/build/assets'
FM=R+'/work/20261008_presentation_front/assets/maps'
FH=R+'/work/20261008_presentation_front/assets/hist'
HA=R+'/work/20261011_history_aerial/build'
NX=R+'/work/20261010_nexus_front/build/assets'
D=R+'/gj-datamap/public/data'
OUT='assets'; os.makedirs(OUT,exist_ok=True)
RED='#c8102e'; DARK='#8a0a1f'; INK='#1a1a1a'; G1='#f2f2f2'; G2='#d9d9d9'; G3='#9a9a9a'; G4='#5c5c5c'

# ---------- 1) 캡처 재채색 ----------
jobs=[(VA+'/footfall_close.png','footfall_close','graynonred'),(VA+'/northsouth_clean.png','northsouth','graynonred'),
 (VA+'/physical_gap.png','physical_gap','split'),(VA+'/age_buildings.png','age_buildings','split'),
 (VA+'/heritage_original.jpg','heritage','all'),(VA+'/anchors.png','anchors','all'),
 (VA+'/street_orientation.png','street_orientation','split'),(VA+'/arrival.png','arrival','split'),
 (FH+'/ortho_2025_F1_outline.jpg','cover_outline','graynonred'),(FM+'/m1_gyeongju_city.png','city','all'),
 (FM+'/m9_rail_axis_S3.png','rail_axis','graynonred')]
import sys
SKIP='--vector' in sys.argv
for src,name,mode in ([] if SKIP else jobs):
    recolor(src,f'{OUT}/{name}.png',mode); print('ok',name)
for src,name in ([] if SKIP else [(HA+'/aerial_1954_square.jpg','aerial_1954'),(HA+'/aerial_2009_square.jpg','aerial_2009'),(HA+'/aerial_2025_square.jpg','aerial_2025'),(NX+'/ortho_2015_square.jpg','ortho_2015'),(NX+'/ortho_2021_square.jpg','ortho_2021')]):
    ImageOps.grayscale(Image.open(src)).save(f'{OUT}/{name}.jpg',quality=88); print('ok',name)

# ---------- 2) 벡터 지도 ----------
def gj(n): return json.load(open(f'{D}/{n}.geojson',encoding='utf-8'))['features']
GOSI=gj('zone')[0]['geometry']['coordinates'][0]
zone=json.load(open('data/plan_boundary_4326_min.geojson',encoding='utf-8'))['features'][0]['geometry']['coordinates'][0]
lon0=sum(p[0] for p in zone)/len(zone); lat0=sum(p[1] for p in zone)/len(zone)
KX=math.cos(math.radians(lat0))*111320; KY=110574
def xy(p): return ((p[0]-lon0)*KX,(p[1]-lat0)*KY)
def rings(f):
    g=f['geometry']
    if g['type']=='Polygon': return [g['coordinates']]
    if g['type']=='MultiPolygon': return g['coordinates']
    return []
def lines(f):
    g=f['geometry']
    if g['type']=='LineString': return [g['coordinates']]
    if g['type']=='MultiLineString': return g['coordinates']
    return []
def centroid(f):
    best=None
    for pg in rings(f):
        c=pg[0]; n=len(c)
        if best is None or n>best[0]: best=(n,c)
    c=best[1]; return xy((sum(p[0] for p in c)/len(c),sum(p[1] for p in c)/len(c)))
ZX=[xy(p)[0] for p in zone]; ZY=[xy(p)[1] for p in zone]; xmin,xmax,ymin,ymax=min(ZX),max(ZX),min(ZY),max(ZY); xc=(xmin+xmax)/2; yc=(ymin+ymax)/2
PARCELS=gj('parcels'); ROADS=gj('urban_roads'); RAILA=gj('rail_abandoned'); RAILX=gj('rail_active'); PARKS=gj('parks_upis'); HADM=gj('hadm_pop'); FOOT={f['properties']['id']:f for f in gj('footfall_areas')}

def fig(w,h):
    f=plt.figure(figsize=(w,h),dpi=200); ax=f.add_axes([0,0,1,1]); ax.set_aspect('equal'); ax.axis('off'); return f,ax
def add_polys(ax,feats,fc,ec,lw,z,alpha=1.0):
    pats=[MPoly([xy(p) for p in pg[0]],closed=True) for f in feats for pg in rings(f)]
    if pats: ax.add_collection(PatchCollection(pats,facecolor=fc,edgecolor=ec,linewidths=lw,zorder=z,alpha=alpha))
def add_lines(ax,feats,color,lw,z,ls='solid'):
    segs=[[xy(p) for p in ln] for f in feats for ln in lines(f)]
    if segs: ax.add_collection(LineCollection(segs,colors=color,linewidths=lw,zorder=z,linestyles=ls,capstyle='round'))
def base(ax,cx=0,cy=0,hw=900,hh=700,parcels=True,site=True,site_fill='#f7d9dd'):
    if parcels: add_polys(ax,PARCELS,'#ececec','#ffffff',0.35,1)
    add_polys(ax,[f for f in PARKS if f['properties'].get('lcl_nam') in ('공원','녹지')],'#dcdcdc','none',0,0.5)
    add_lines(ax,[f for f in ROADS if '간선' in f['properties']['cls']],'#8f8f8f',1.5,2)
    add_lines(ax,[f for f in ROADS if '간선' not in f['properties']['cls']],'#b5b5b5',0.9,2)
    add_lines(ax,RAILA,'#444444',1.0,3,ls=(0,(3,2)))
    add_lines(ax,RAILX,'#444444',1.6,3)
    if site:
        ax.add_patch(MPoly([xy(p) for p in zone],closed=True,fc=site_fill,ec=RED,lw=2.0,zorder=4))
    ax.set_xlim(cx-hw,cx+hw); ax.set_ylim(cy-hh,cy+hh)
def scalebar(ax,x,y,m=500,lbl=None):
    ax.plot([x,x+m],[y,y],color=INK,lw=2,zorder=9); ax.text(x+m/2,y+18,lbl or f'{m} m',ha='center',va='bottom',fontsize=11,color=INK,zorder=9)
def north(ax,x,y,s=60):
    ax.annotate('',xy=(x,y+s),xytext=(x,y),arrowprops=dict(arrowstyle='-|>',color=INK,lw=1.2),zorder=9); ax.text(x,y+s+10,'N',ha='center',va='bottom',fontsize=11,color=INK,fontweight='bold',zorder=9)

# (A) 입지 기본도 — 반경 500/1000m, 주요 자산
f,ax=fig(9,9); base(ax,0,0,1150,1150)
for r in (500,1000): ax.add_patch(Circle((0,0),r,fc='none',ec=G4,lw=0.9,ls=(0,(4,3)),zorder=5))
ax.text(20,505,'500 m',fontsize=11,color=G4,zorder=6); ax.text(20,1005,'1,000 m',fontsize=11,color=G4,zorder=6)
pts={'성동시장':'G_seongdong_market_r200','행복황촌':'B_haengbok_hwangchon_digitized','황리단길':'H_hwangridan_r300'}
for t,k in pts.items():
    cx_,cy_=centroid(FOOT[k]); ax.plot(cx_,cy_,'o',color=INK,ms=7,zorder=7); ax.text(cx_+35,cy_+25,t,fontsize=15,color=INK,fontweight='bold',zorder=8)
# 대릉원·읍성·동궁과월지·첨성대: 방위·거리(구 역사 점 기준 직선)로 근사 표시
for t,ang,dist in [('대릉원',225,523),('경주읍성',300,497),('동궁과 월지',135,920),('첨성대',185,1030)]:
    a=math.radians(ang-90); px,py=dist*math.cos(a)*-1 if False else dist*math.sin(math.radians(ang)), dist*math.cos(math.radians(ang))
    ax.plot(px,py,'s',color=INK,ms=6,zorder=7); ax.text(px+35,py+25,t,fontsize=15,color=INK,fontweight='bold',zorder=8)
ax.text(xc,ymax+40,'구 경주역 부지',ha='center',va='bottom',fontsize=15,color=RED,fontweight='bold',zorder=8)
scalebar(ax,-1080,-1080); north(ax,1060,980)
f.savefig(f'{OUT}/location_base.png',facecolor='white'); plt.close(f); print('ok location_base')

# (B) 전략 배치도
f,ax=fig(9,7.5); base(ax,0,0,1000,830)
for k,t in {'G_seongdong_market_r200':'성동시장','B_haengbok_hwangchon_digitized':'행복황촌','H_hwangridan_r300':'황리단길·대릉원'}.items():
    cx_,cy_=centroid(FOOT[k]); ax.add_patch(Circle((cx_,cy_),130,fc='none',ec=INK,lw=1.3,ls=(0,(2,2)),zorder=5)); ax.text(cx_,cy_-165,t,ha='center',va='top',fontsize=14,color=INK,zorder=8,fontweight='bold')
for yy in np.linspace(ymin+120,ymax-120,5):
    ax.add_patch(FancyArrowPatch((xmin-230,yy),(xmax+230,yy),arrowstyle='<|-|>',mutation_scale=13,color=RED,lw=1.7,zorder=7))
ax.add_patch(FancyArrowPatch((xc,ymin-300),(xc,ymax+300),arrowstyle='<|-|>',mutation_scale=15,color=RED,lw=2.4,zorder=7))
ax.add_patch(Circle((xc,yc-40),150,fc=RED,ec='none',alpha=0.2,zorder=5)); ax.add_patch(Circle((xc,yc-40),150,fc='none',ec=RED,lw=2,zorder=6))
for k in ['G_seongdong_market_r200','B_haengbok_hwangchon_digitized']:
    cx_,cy_=centroid(FOOT[k]); ax.add_patch(FancyArrowPatch((xc,ymax-230),(cx_,cy_),arrowstyle='-|>',mutation_scale=15,color=INK,lw=2.0,connectionstyle='arc3,rad=0.25' if cx_<xc else 'arc3,rad=-0.25',zorder=7))
ax.text(xmin-250,ymax-30,'CONNECT',color=RED,fontsize=16,fontweight='bold',ha='right',zorder=8)
ax.text(xc+175,yc-40,'EXCHANGE',color=RED,fontsize=16,fontweight='bold',va='center',zorder=8)
ax.text(xc+30,ymax+90,'SPREAD',color=INK,fontsize=16,fontweight='bold',zorder=8)
ax.text(xc,ymin-340,'대릉원·황리단길 방면',ha='center',va='top',fontsize=13,color=INK,zorder=8)
ax.text(xc,ymax+330,'북천·황성공원 방면',ha='center',va='bottom',fontsize=13,color=INK,zorder=8)
f.savefig(f'{OUT}/strategy_map.png',facecolor='white'); plt.close(f); print('ok strategy_map')

# (C) 행정동 주제도 3종 (인구변화·고령·청년) — 도심부 창
def choropleth(name,key,ramp,labels,fmt,title_note):
    f,ax=fig(8,6.4)
    vals=[(f_,f_['properties'].get(key)) for f_ in HADM]
    for f_,v in vals:
        if v is None: fc='#ffffff'
        else: fc=ramp(v)
        for pg in rings(f_): ax.add_patch(MPoly([xy(p) for p in pg[0]],closed=True,fc=fc,ec='#ffffff',lw=1.2,zorder=1))
    add_lines(ax,[r for r in ROADS if '간선' in r['properties']['cls']],'#ffffff',1.0,2)
    add_lines(ax,RAILA,'#555555',0.9,3,ls=(0,(3,2)))
    ax.add_patch(MPoly([xy(p) for p in zone],closed=True,fc='none',ec=RED,lw=2.0,zorder=5))
    W=(-3400,3400,-2400,3000)
    for f_ in HADM:
        n=f_['properties']['hadm']
        if n in labels:
            pts=[xy(p) for pg in rings(f_) for p in pg[0] if W[0]+300<xy(p)[0]<W[1]-300 and W[2]+300<xy(p)[1]<W[3]-300]
            if not pts: continue
            cx_=sum(p[0] for p in pts)/len(pts); cy_=sum(p[1] for p in pts)/len(pts); dx,dy=labels[n]; v=f_['properties'].get(key)
            ax.text(cx_+dx,cy_+dy,f"{n}\n{fmt(v)}",ha='center',va='center',fontsize=12.5,color=INK,zorder=8,fontweight='bold',bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='none',alpha=0.88))
    ax.set_xlim(*W[:2]); ax.set_ylim(*W[2:])
    scalebar(ax,-3200,-2250,1000,'1 km'); north(ax,3150,2600,150)
    f.savefig(f'{OUT}/{name}.png',facecolor='white'); plt.close(f); print('ok',name)
def red_ramp(t):  # t 0..1
    t=max(0,min(1,t)); c0=np.array([255,255,255]); c1=np.array([200,16,46]); c2=np.array([110,0,20])
    c=c0+(c1-c0)*(t/0.75) if t<0.75 else c1+(c2-c1)*((t-0.75)/0.25); return '#%02x%02x%02x'%tuple(int(x) for x in c)
def gray_ramp(t):
    t=max(0,min(1,t)); v=int(235-(235-150)*t); return '#%02x%02x%02x'%(v,v,v)
LBL={'황남동':(0,0),'황오동':(0,-80),'성건동':(0,0),'월성동':(0,0),'동천동':(0,0),'황성동':(0,0),'용강동':(0,0),'현곡면':(0,0),'선도동':(0,0)}
choropleth('pop_change','chg_10y_pct',lambda v: red_ramp(min(1,-v/50)) if v<0 else gray_ramp(min(1,v/35)),LBL,lambda v:f'{v:+.1f}%','')
choropleth('pop_65','pct_65',lambda v: red_ramp((v-15)/40),LBL,lambda v:f'{v:.1f}%','')
choropleth('pop_y2034','pct_y2034',lambda v: red_ramp((21-v)/14),LBL,lambda v:f'{v:.1f}%','')

# (D) 유동인구 구역 — 밀도 원 (원 면적 ∝ 명/ha)
f,ax=fig(9,7.2); base(ax,-250,-350,1300,1040,site_fill='#f7d9dd')
for k,(t,dx,dy) in {'G_seongdong_market_r200':('성동시장',0,0),'B_haengbok_hwangchon_digitized':('행복황촌',0,0),'H_hwangridan_r300':('황리단길',0,0),'D_zone':('폐역 구역',0,0)}.items():
    p=FOOT[k]['properties']; cx_,cy_=centroid(FOOT[k]); r=math.sqrt(p['per_ha'])*7
    ax.add_patch(Circle((cx_,cy_),r,fc=RED,ec='none',alpha=0.55,zorder=6)); ax.add_patch(Circle((cx_,cy_),r,fc='none',ec=DARK,lw=1,zorder=7))
    ax.text(cx_,cy_-r-20,f"{t}\n{p['per_ha']:,.0f}명/ha",ha='center',va='top',fontsize=13,fontweight='bold',color=INK,zorder=8,bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='none',alpha=0.85))
scalebar(ax,-1500,-1350); north(ax,1000,600)
f.savefig(f'{OUT}/footfall_density.png',facecolor='white'); plt.close(f); print('ok footfall_density')

# (E) 주말 시간대별 소통 (06·13·21시) — 도시부 기준 정체<15 / 서행<25 km/h
TR=gj('traffic_hist')
for hh in (6,13,21):
    f,ax=fig(5,6.2); base(ax,-250,-150,1150,1430,parcels=False,site_fill='none')
    segs={'c':[],'f':[],'o':[]}
    for t in TR:
        p=t['properties']; v=p.get(f'we_{hh:02d}')
        if v is None: continue
        key='c' if v<p['thr_c'] else ('f' if v<p['thr_f'] else 'o')
        for ln in lines(t): segs[key].append([xy(q) for q in ln])
    for key,col,lw,z in [('o','#c9c9c9',1.2,3),('f','#e8808f',2.2,4),('c',RED,3.0,5)]:
        if segs[key]: ax.add_collection(LineCollection(segs[key],colors=col,linewidths=lw,zorder=z,capstyle='round'))
    ax.add_patch(MPoly([xy(p) for p in zone],closed=True,fc='none',ec=INK,lw=1.6,zorder=6,ls=(0,(4,2))))
    f.savefig(f'{OUT}/traffic_{hh:02d}.png',facecolor='white'); plt.close(f); print('ok traffic',hh)

# (F) 규제 4겹 패널 — 같은 창(부지 ±)
GODO=gj('godo'); LU=gj('landuse'); RA=gj('reg_areas'); BL=gj('blocks')
def panel(name,draw):
    f,ax=fig(3.2,4.6); base(ax,xc,yc,480,690,parcels=True,site=False)
    draw(ax); ax.add_patch(MPoly([xy(p) for p in zone],closed=True,fc='none',ec=INK,lw=1.8,zorder=8))
    f.savefig(f'{OUT}/{name}.png',facecolor='white'); plt.close(f); print('ok',name)
def d_lu(ax):
    cmap={'자연녹지지역':'#e4e4e4','보전녹지지역':'#cfcfcf','제1종일반주거지역':'#f3c6cc','제2종일반주거지역':'#e9909c','일반상업지역':RED,'준주거지역':'#d96d7a'}
    for f_ in LU:
        u=f_['properties']['uname']; fc=cmap.get(u,'#f6f6f6')
        for pg in rings(f_): ax.add_patch(MPoly([xy(p) for p in pg[0]],closed=True,fc=fc,ec='#ffffff',lw=0.6,zorder=5,alpha=0.9))
def d_godo(ax):
    for f_ in GODO:
        h=f_['properties'].get('h_max')
        try: h=float(h)
        except: h=None
        fc='#f6f6f6' if h is None else red_ramp(max(0,min(1,(36-h)/26))*0.85)
        for pg in rings(f_): ax.add_patch(MPoly([xy(p) for p in pg[0]],closed=True,fc=fc,ec='#ffffff',lw=0.6,zorder=5,alpha=0.9))
def d_reg(ax):
    for f_ in RA:
        n=f_['properties'].get('reg') or f_['properties'].get('name') or ''
        if '국가지정문화유산구역' in n or '문화유산 보호구역' in n: fc,hatch=RED,None
        elif '역사문화환경보존지역' in n: fc,hatch='#e9909c',None
        elif '특별보존' in n or '보존육성' in n: fc,hatch='#f3c6cc','//'
        else: continue
        for pg in rings(f_): ax.add_patch(MPoly([xy(p) for p in pg[0]],closed=True,fc=fc,ec='#ffffff',lw=0.5,zorder=5,alpha=0.75,hatch=hatch))
PLANP=json.load(open('data/plan_parcels_4326.geojson',encoding='utf-8'))['features']
def d_blocks(ax):
    for f_ in sorted(PLANP,key=lambda t:{'도로':0,'보도':1,'오픈스페이스':2}.get(t['properties']['layer'],3)):
        L=f_['properties']['layer']; fc='#ffffff' if L=='도로' else ('#ececec' if L=='보도' else ('#cfcfcf' if L=='오픈스페이스' else ('#8a8a8a' if L.startswith('관광지원') else RED)))
        for pg in rings(f_): ax.add_patch(MPoly([xy(p) for p in pg[0]],closed=True,fc=fc,ec='#ffffff',lw=0.6,zorder=6,alpha=0.92))
panel('reg_landuse',d_lu); panel('reg_godo',d_godo); panel('reg_heritage',d_reg); panel('reg_plan',d_blocks)

# (G') 남북 관계도 — 황리단길(남)·북천·황성공원(북)과 폐선축
f,ax=fig(7.2,8.6); base(ax,0,250,1150,1370)
big=[p_ for p_ in PARKS if p_['properties'].get('lcl_nam')=='공원']
cand=[]
for p_ in big:
    try:
        cx_,cy_=centroid(p_)
        if cy_>ymax+150 and abs(cx_)<1400: cand.append((p_,cx_,cy_))
    except Exception: pass
if cand:
    import functools
    def ring_area(p_):
        a=0.0
        for pg in rings(p_):
            c=[xy(q) for q in pg[0]]
            a+=abs(sum(c[i][0]*c[(i+1)%len(c)][1]-c[(i+1)%len(c)][0]*c[i][1] for i in range(len(c)))/2)
        return a
    p_,cx_,cy_=max(cand,key=lambda t:ring_area(t[0]))
    for pg in rings(p_): ax.add_patch(MPoly([xy(q) for q in pg[0]],closed=True,fc='#bdbdbd',ec='none',zorder=2.5))
    ax.text(cx_,cy_,'황성공원',ha='center',va='center',fontsize=13,fontweight='bold',color=INK,zorder=8)
for k,t in {'H_hwangridan_r300':'황리단길 300 m\n757명/ha · 주말/주중 1.72','F_cityhall_r500':'시청 500 m\n주말/주중 0.88'}.items():
    p=FOOT[k]['properties']; cx_,cy_=centroid(FOOT[k]); r=math.sqrt(p['per_ha'])*6
    ax.add_patch(Circle((cx_,cy_),r,fc=RED if k.startswith('H') else '#9a9a9a',ec='none',alpha=0.55,zorder=6))
    ax.text(cx_,cy_+r+25 if k.startswith('H') else cy_-r-25,t,ha='center',va='bottom' if k.startswith('H') else 'top',fontsize=12,fontweight='bold',color=INK,zorder=8,bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='none',alpha=0.85))
ax.add_patch(FancyArrowPatch((xc,ymin-80),(xc,ymax+700),arrowstyle='<|-|>',mutation_scale=16,color=RED,lw=2.4,zorder=7))
ax.text(xc+30,ymax+350,'폐선 노반\n남북 보행축',fontsize=12,fontweight='bold',color=RED,zorder=8)
ax.text(xc,ymax+30,'북천',ha='center',va='bottom',fontsize=11,color=INK,zorder=8)
scalebar(ax,-1100,-1050); north(ax,1050,1500,100)
f.savefig(f'{OUT}/northsouth_v.png',facecolor='white'); plt.close(f); print('ok northsouth_v')

# (H) 부지 윤곽(다이어그램용)
f,ax=fig(2.4,6.6); ax.add_patch(MPoly([xy(p) for p in zone],closed=True,fc='#f2f2f2',ec=INK,lw=1.6)); ax.set_xlim(xmin-60,xmax+60); ax.set_ylim(ymin-60,ymax+60)
f.savefig(f'{OUT}/site_outline.png',facecolor='white'); plt.close(f); print('ok site_outline')
# (I) 동서 횡단 다이어그램 — 부지 ±, 도로 끝 접속 표시 없이 간선·보조간선과 폐선 노반
f,ax=fig(5.2,7.4); base(ax,xc,yc-30,560,780,parcels=True,site_fill='#f7d9dd')
ax.annotate('',xy=(xmin-40,ymin+90),xytext=(xmin-40,ymax-90),arrowprops=dict(arrowstyle='<->',color=INK,lw=1.4),zorder=9)
ax.text(xmin-70,yc,'985 m\n도로 횡단 없음',rotation=90,ha='right',va='center',fontsize=14,color=INK,fontweight='bold',zorder=9)
scalebar(ax,xc-520,yc-780,200); north(ax,xc+500,yc+640,70)
f.savefig(f'{OUT}/crossing_map.png',facecolor='white'); plt.close(f); print('ok crossing_map')
json.dump({'xmin':xmin,'xmax':xmax,'ymin':ymin,'ymax':ymax},open(f'{OUT}/site_bbox.json','w'))
print('done')
