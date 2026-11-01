# prep_assets.py 라벨 크기·위치 패치 (1회용)
s=open('prep_assets.py',encoding='utf-8').read()
reps=[
("""    for f_ in HADM:
        n=f_['properties']['hadm']
        if n in labels:
            cx_,cy_=centroid(f_); dx,dy=labels[n]; v=f_['properties'].get(key)
            ax.text(cx_+dx,cy_+dy,f"{n}\\n{fmt(v)}",ha='center',va='center',fontsize=9,color=INK,zorder=8,bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='none',alpha=0.85))
    ax.set_xlim(-3400,3400); ax.set_ylim(-2400,3000)""",
"""    W=(-3400,3400,-2400,3000)
    for f_ in HADM:
        n=f_['properties']['hadm']
        if n in labels:
            pts=[xy(p) for pg in rings(f_) for p in pg[0] if W[0]+300<xy(p)[0]<W[1]-300 and W[2]+300<xy(p)[1]<W[3]-300]
            if not pts: continue
            cx_=sum(p[0] for p in pts)/len(pts); cy_=sum(p[1] for p in pts)/len(pts); dx,dy=labels[n]; v=f_['properties'].get(key)
            ax.text(cx_+dx,cy_+dy,f"{n}\\n{fmt(v)}",ha='center',va='center',fontsize=12.5,color=INK,zorder=8,fontweight='bold',bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='none',alpha=0.88))
    ax.set_xlim(*W[:2]); ax.set_ylim(*W[2:])"""),
("LBL={'황남동':(-150,-120),'황오동':(0,0),'성건동':(-250,150),'월성동':(250,-150),'동천동':(0,0),'황성동':(0,0),'용강동':(0,0),'현곡면':(-300,0),'선도동':(0,0),'불국동':(0,0)}",
 "LBL={'황남동':(0,0),'황오동':(0,-80),'성건동':(0,0),'월성동':(0,0),'동천동':(0,0),'황성동':(0,0),'용강동':(0,0),'현곡면':(0,0),'선도동':(0,0)}"),
("choropleth('pop_y2034','pct_y2034',lambda v: red_ramp((v-5)/17)","choropleth('pop_y2034','pct_y2034',lambda v: red_ramp((21-v)/14)"),
("choropleth('pop_change','chg_10y_pct',lambda v: red_ramp(min(1,-v/45)) if v<0 else gray_ramp(min(1,v/35))","choropleth('pop_change','chg_10y_pct',lambda v: red_ramp(min(1,-v/50)) if v<0 else gray_ramp(min(1,v/35))"),
("f,ax=fig(9,6.6); base(ax,-150,-250,1500,1100,site_fill='#f7d9dd')\nfor k,(t,dx,dy) in {'G_seongdong_market_r200':('성동시장',0,0),'B_haengbok_hwangchon_digitized':('행복황촌',0,0),'H_hwangridan_r300':('황리단길',0,0),'A_hwango_grid32':('황오동 원도심',0,0),'F_cityhall_r500':('시청 500m',0,0),'D_zone':('폐역 구역',0,0)}.items():\n    p=FOOT[k]['properties']; cx_,cy_=centroid(FOOT[k]); r=math.sqrt(p['per_ha'])*9",
 "f,ax=fig(9,7.2); base(ax,-250,-350,1300,1040,site_fill='#f7d9dd')\nfor k,(t,dx,dy) in {'G_seongdong_market_r200':('성동시장',0,0),'B_haengbok_hwangchon_digitized':('행복황촌',0,0),'H_hwangridan_r300':('황리단길',0,0),'D_zone':('폐역 구역',0,0)}.items():\n    p=FOOT[k]['properties']; cx_,cy_=centroid(FOOT[k]); r=math.sqrt(p['per_ha'])*7"),
("""    ax.text(cx_,cy_-r-20,f"{t}\\n{p['per_ha']:,.0f}명/ha",ha='center',va='top',fontsize=9,""","""    ax.text(cx_,cy_-r-20,f"{t}\\n{p['per_ha']:,.0f}명/ha",ha='center',va='top',fontsize=13,fontweight='bold',"""),
("scalebar(ax,-1600,-1300); north(ax,1300,700)","scalebar(ax,-1500,-1350); north(ax,1000,600)"),
("ax.text(x+m/2,y+18,lbl or f'{m} m',ha='center',va='bottom',fontsize=8,","ax.text(x+m/2,y+18,lbl or f'{m} m',ha='center',va='bottom',fontsize=11,"),
("ax.text(x,y+s+10,'N',ha='center',va='bottom',fontsize=9,","ax.text(x,y+s+10,'N',ha='center',va='bottom',fontsize=11,"),
("ax.text(20,505,'500 m',fontsize=8.5,color=G4,zorder=6); ax.text(20,1005,'1,000 m',fontsize=8.5,color=G4,zorder=6)","ax.text(20,505,'500 m',fontsize=11,color=G4,zorder=6); ax.text(20,1005,'1,000 m',fontsize=11,color=G4,zorder=6)"),
("ax.text(cx_+35,cy_+25,t,fontsize=11,color=INK,fontweight='bold',zorder=8)","ax.text(cx_+35,cy_+25,t,fontsize=15,color=INK,fontweight='bold',zorder=8)"),
("ax.text(px+35,py+25,t,fontsize=11,color=INK,fontweight='bold',zorder=8)","ax.text(px+35,py+25,t,fontsize=15,color=INK,fontweight='bold',zorder=8)"),
("ax.text(xc,ymax+40,'구 경주역 부지',ha='center',va='bottom',fontsize=11,","ax.text(xc,ymax+40,'구 경주역 부지',ha='center',va='bottom',fontsize=15,"),
("ax.text(cx_,cy_-165,t,ha='center',va='top',fontsize=10.5,color=INK,zorder=8,fontweight='bold')","ax.text(cx_,cy_-165,t,ha='center',va='top',fontsize=14,color=INK,zorder=8,fontweight='bold')"),
("'CONNECT',color=RED,fontsize=12","'CONNECT',color=RED,fontsize=16"),("'EXCHANGE',color=RED,fontsize=12","'EXCHANGE',color=RED,fontsize=16"),("'SPREAD',color=INK,fontsize=12","'SPREAD',color=INK,fontsize=16"),
("'대릉원·황리단길 방면',ha='center',va='top',fontsize=9.5","'대릉원·황리단길 방면',ha='center',va='top',fontsize=13"),
("'북천·황성공원 방면',ha='center',va='bottom',fontsize=9.5","'북천·황성공원 방면',ha='center',va='bottom',fontsize=13"),
("ha='center',va='center',fontsize=7.5,color='white' if","ha='center',va='center',fontsize=12,color='white' if"),
("rotation=90,ha='right',va='center',fontsize=9.5","rotation=90,ha='right',va='center',fontsize=14"),
("for src,name,mode in jobs:\n    recolor(","import sys\nSKIP='--vector' in sys.argv\nfor src,name,mode in ([] if SKIP else jobs):\n    recolor("),
("for src,name in [(HA+'/aerial_1954_square.jpg'","for src,name in ([] if SKIP else [(HA+'/aerial_1954_square.jpg'"),
("(NX+'/ortho_2021_square.jpg','ortho_2021')]:\n    ImageOps","(NX+'/ortho_2021_square.jpg','ortho_2021')]):\n    ImageOps"),
]
for a,b in reps:
    assert a in s, a[:60]
    s=s.replace(a,b)
open('prep_assets.py','w',encoding='utf-8').write(s); print('patched')
