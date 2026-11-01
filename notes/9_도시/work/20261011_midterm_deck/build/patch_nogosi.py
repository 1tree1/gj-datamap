# 고시(지구단위계획 결정 2026-8호) 관련 내용 제거 패치: prep_assets.py + deck.js
import io
# ---------- prep_assets.py ----------
p=io.open('prep_assets.py',encoding='utf-8').read()
reps=[
("        ax.add_patch(MPoly([xy(p) for p in GOSI],closed=True,fc='none',ec=INK,lw=0.8,ls=(0,(3,2)),zorder=4.5))\n",""),
# ④ 패널: 고시 결정도 대신 본 계획 획지(라이노 최종)
("""def d_blocks(ax):
    cmap={'commercial':RED,'civic':'#e9909c','culture':'#d96d7a','parking':'#8a8a8a','park':'#c9c9c9'}
    for f_ in BL:
        for pg in rings(f_): ax.add_patch(MPoly([xy(p) for p in pg[0]],closed=True,fc=cmap[f_['properties']['cls']],ec='#ffffff',lw=0.8,zorder=6,alpha=0.9))""",
"""PLANP=json.load(open('data/plan_parcels_4326.geojson',encoding='utf-8'))['features']
def d_blocks(ax):
    for f_ in sorted(PLANP,key=lambda t:{'도로':0,'보도':1,'오픈스페이스':2}.get(t['properties']['layer'],3)):
        L=f_['properties']['layer']; fc='#ffffff' if L=='도로' else ('#ececec' if L=='보도' else ('#cfcfcf' if L=='오픈스페이스' else ('#8a8a8a' if L.startswith('관광지원') else RED)))
        for pg in rings(f_): ax.add_patch(MPoly([xy(p) for p in pg[0]],closed=True,fc=fc,ec='#ffffff',lw=0.6,zorder=6,alpha=0.92))"""),
# 고시 결정도 지도 생성 블록 제거 (G)
("""# (G) 고시 결정도 — 라벨·면적
f,ax=fig(4.2,8.4); base(ax,xc,yc,420,840,parcels=True,site=False)
cmap={'commercial':RED,'civic':'#e9909c','culture':'#d96d7a','parking':'#8a8a8a','park':'#c9c9c9'}
kor={'commercial':'상업','civic':'공공청사','culture':'문화','parking':'주차','park':'근린공원'}
for f_ in BL:
    p=f_['properties']
    for pg in rings(f_): ax.add_patch(MPoly([xy(q) for q in pg[0]],closed=True,fc=cmap[p['cls']],ec='#ffffff',lw=1.0,zorder=6,alpha=0.92))
    cx_,cy_=centroid(f_); ax.text(cx_,cy_,f"{p['name']}\\n{p['gosi_area_m2']:,}㎡",ha='center',va='center',fontsize=12,color='white' if p['cls'] in ('commercial','parking') else INK,zorder=8,fontweight='bold')
ax.add_patch(MPoly([xy(p) for p in zone],closed=True,fc='none',ec=INK,lw=1.8,zorder=8))
scalebar(ax,xc-380,yc-800,200); north(ax,xc+360,yc+700,70)
f.savefig(f'{OUT}/decision_map.png',facecolor='white'); plt.close(f); print('ok decision_map')
""",
"""# (G') 남북 관계도 — 황리단길(남)·북천·황성공원(북)과 폐선축
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
for k,t in {'H_hwangridan_r300':'황리단길 300 m\\n757명/ha · 주말/주중 1.72','F_cityhall_r500':'시청 500 m\\n주말/주중 0.88'}.items():
    p=FOOT[k]['properties']; cx_,cy_=centroid(FOOT[k]); r=math.sqrt(p['per_ha'])*6
    ax.add_patch(Circle((cx_,cy_),r,fc=RED if k.startswith('H') else '#9a9a9a',ec='none',alpha=0.55,zorder=6))
    ax.text(cx_,cy_-r-25,t,ha='center',va='top',fontsize=12,fontweight='bold',color=INK,zorder=8,bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='none',alpha=0.85))
ax.add_patch(FancyArrowPatch((xc,ymin-80),(xc,ymax+700),arrowstyle='<|-|>',mutation_scale=16,color=RED,lw=2.4,zorder=7))
ax.text(xc+30,ymax+350,'폐선 노반\\n남북 보행축',fontsize=12,fontweight='bold',color=RED,zorder=8)
ax.text(xc,ymax+30,'북천',ha='center',va='bottom',fontsize=11,color=INK,zorder=8)
scalebar(ax,-1100,-1050); north(ax,1050,1500,100)
f.savefig(f'{OUT}/northsouth_v.png',facecolor='white'); plt.close(f); print('ok northsouth_v')
"""),
]
if 'northsouth_v' not in p:
    for a,b in reps:
        assert a in p, a[:70]; p=p.replace(a,b)
    io.open('prep_assets.py','w',encoding='utf-8').write(p)
# ---------- deck.js ----------
d=io.open('deck.js',encoding='utf-8').read()
reps=[
# 04
(""" label(s,'면적 기준 3가지',7.6,4.6,5);
 const rows=[['시 구상 · 1단계','79,438㎡','경주시 보도자료  [T2, 범위 미정의]'],['고시 구역','156,460㎡','경주시 고시 제2026-8호  [T1]'],['본 계획 경계(최종)','228,025㎡','라이노 계획 합집합 측정 · 고시 구역 밖 69,847㎡(30.6%)']];
 rows.forEach((r,i)=>{const y=4.95+i*0.55; T(s,r[0],7.6,y,1.9,0.3,{size:10.5,color:G4}); T(s,r[1],9.5,y-0.05,1.6,0.35,{size:14,bold:true,num:true,color:i===2?RED:INK}); T(s,r[2],11.0,y,1.9,0.5,{size:9,color:G4,ls:1.1});});""",
 """ label(s,'면적 기준',7.6,4.6,5);
 const rows=[['시 구상 · 1단계','79,438㎡','경주시 보도자료  [T2, 범위 미정의]'],['본 계획 경계(최종)','228,025㎡','라이노 계획 합집합 측정 · 남북 948 m × 동서 311 m'],['이전 분석 경계','218,478㎡','2026.10.05 경계 · 접속점·우회율 산정 기준']];
 rows.forEach((r,i)=>{const y=4.95+i*0.55; T(s,r[0],7.6,y,1.9,0.3,{size:10.5,color:G4}); T(s,r[1],9.5,y-0.05,1.6,0.35,{size:14,bold:true,num:true,color:i===1?RED:INK}); T(s,r[2],11.0,y,1.9,0.5,{size:9,color:G4,ls:1.1});});"""),
("const s=slide('대상지 개요 : 위치','원도심과 폐선축 위의 대상지','구 경주역 폐역 부지는 경주시 성동동 일원(원화로 266)이며, 2021년 12월 동해선 이설로 폐역되었다. 폐선축 80.3km·폐역 17개소는 2023.04 경주시 폐철도 기본구상 값으로 원문 대조 전이다.');",
 "const s=slide('대상지 개요 : 위치','원도심과 폐선축 위의 대상지','구 경주역 폐역 부지는 경주시 성동동 일원(원화로 266)이며, 2021년 12월 동해선 이설로 폐역되었다. 폐선축 80.3km·폐역 17개소는 2023.04 경주시 폐철도 기본구상 값으로 원문 대조 전이다. 본 계획은 기존 지구단위계획 결정과 무관하게 경계·용도를 새로 설정한다.');"),
# 05
(" const bars=[['시 구상 1단계',79438,'[T2]'],['고시 구역',156460,'[T1]'],['본 계획 경계',228025,'측정']];\n bars.forEach((b,i)=>{const y=3.0+i*0.5; T(s,b[0],8.0,y,1.5,0.3,{size:10,color:G4}); rect(s,9.5,y+0.03,2.1*b[1]/228025,0.24,i===2?RED:(i===1?G4:G3)); T(s,b[1].toLocaleString()+'㎡ '+b[2],9.5+2.1*b[1]/228025+0.08,y,1.6,0.3,{size:9.5,num:true,color:INK});});",
 " const bars=[['시 구상 1단계',79438,'[T2]'],['이전 분석 경계',218478,'2026.10.05'],['본 계획 경계',228025,'최종']];\n bars.forEach((b,i)=>{const y=3.0+i*0.5; T(s,b[0],8.0,y,1.5,0.3,{size:10,color:G4}); rect(s,9.5,y+0.03,2.1*b[1]/228025,0.24,i===2?RED:(i===1?G4:G3)); T(s,b[1].toLocaleString()+'㎡ '+b[2],9.5+2.1*b[1]/228025+0.08,y,1.6,0.3,{size:9.5,num:true,color:INK});});"),
("{t:'고시 구역 밖 69,847㎡(30.6%)는 구역 확대가 필요한 범위입니다.',size:10.5,color:INK}","{t:'본 계획 경계는 라이노 획지·도로·보도 합집합이며 접속점·우회율은 이전 경계 기준입니다.',size:10.5,color:INK}"),
(" SRC(s,'경주시 고시 제2026-8호 · 경주시 도시재생 전략계획(변경, 2022) · 라이노 계획 프레임 측정(2026.10.11)');}"," SRC(s,'경주시 도시재생 전략계획(변경, 2022) · 라이노 계획 프레임 측정(2026.10.11)');}"),
# 08 상위계획: 결정도·고시표 제거 → 상위계획 2건 + 시 구상 + 절차
("""{const s=slide('대상지 개요 : 상위계획','상위계획과 경주시 구상','고시 결정도(2026.01)는 근린공원·상업·공공청사·문화·주차만 배분하고 주거용지가 없다. 시 구상(2026.02) 3,822억·국비 250억은 언론 경유 T4. 1단계 79,438㎡ 구성은 김권일 발표자료(2026) 기준.');
 await img(s,A+'/decision_map.png',0.5,1.35,3.1,5.45,'contain','left');
 label(s,'고시 결정도 (경주시 고시 제2026-8호, 2026.01)  [T1]',3.9,1.45,5);
 table(s,[['용도','획지','면적(㎡)'],['상업',' 3','42,031'],['공공청사',' 2','24,987'],['문화',' 1','9,770'],['주차',' 1','5,756'],['근린공원',' 3','55,415'],[{text:'주거',bold:true,color:RED},{text:' 0',bold:true,color:RED},{text:'없음',bold:true,color:RED}]],3.9,1.8,4.0,[1.6,0.8,1.6],{size:10,numCols:[1,2],rowH:0.28});
 T(s,'고시 구역 156,460㎡ 중 획지 합 137,959㎡, 나머지는 도로 등',3.9,3.85,4.0,0.3,{size:9,color:G4});
 label(s,'경주시 구상 (2026.02)  [T2·T4]',8.3,1.45,4.5);
 const prog=[['K-헤리티지 복합거점','구 역사·전시·공연·체험'],['미래모빌리티 통합허브','복합환승·주차·신교통'],['경주 STAY','체류·숙박·상업']];
 prog.forEach((p,i)=>{const y=1.8+i*0.62; rect(s,8.3,y,0.12,0.5,RED); T(s,p[0],8.5,y,4.3,0.28,{size:11.5,bold:true}); T(s,p[1],8.5,y+0.27,4.3,0.25,{size:9.5,color:G4});});
 ln(s,8.3,3.75,12.83,3.75);
 stat(s,'3,822','억 원','구상 사업비 · 국비 250억 원  [T4, 원문 미확인]',8.3,3.85,2.4,{size:20,color:INK,dsize:9.5});
 stat(s,'79,438','㎡','1단계 범위 · 준주거 20,262 · 상업 17,819 · 문화 12,260 · 도로 19,643 · 공원 9,454  [T2]',10.6,3.85,2.3,{size:20,color:INK,dsize:9.5});
 label(s,'절차',3.9,4.45,4);
 bullets(s,['2026.01  경주시–국가철도공단 MOU(도시재생 혁신지구 공모 협력)  [T4]','2026 하반기  국토교통부 도시재생 혁신지구 공모 예정  [T4]','시 구상 2단계  민자 유치(시청 이전 포함) · 공공청사는 국비 대상 제외  [T2]','혁신지구 요건  기능 2개 이상 집적 · 쇠퇴 3지표 중 2개 · 이용인구·수요 추정과 운영 주체 명시  [T2]'],3.9,4.8,8.9,1.9,{size:10.5});
 SRC(s,'경주시 고시 제2026-8호 · 김권일 발표자료(2026) · 도시재생 혁신지구 가이드라인 · 경주시 보도자료(2026.02)');}""",
"""{const s=slide('대상지 개요 : 상위계획','상위계획과 경주시 구상','2030 기본계획·전략계획(2022)의 경주역 부지 서술과 시 구상(2026.02). 3,822억·국비 250억은 언론 경유 T4. 1단계 79,438㎡ 구성은 김권일 발표자료(2026) 기준. 본 계획은 기존 지구단위계획 결정과 무관하게 수립한다.');
 label(s,'상위계획  [T1]',0.5,1.45,5.5);
 const up=[['2030 경주도시기본계획','시가지(원도심)권 도시재생 추진방안에 "경주역 중심의 경제활성화" · 기존 시가지는 철도와 사적지구로 동서·남북 분리(인쇄쪽 285) · 도심–보문 신교통의 원도심 경유'],['경주시 도시재생 전략계획 (변경, 2022)','경주역부지 개발 148,770㎡(2019–2028) · 공공청사·상징광장·문화·공원·복합상업·커뮤니티 · 복합환승센터 · 선로로 단절된 도시공간을 잇는 매개공간(인쇄쪽 161) · 첫째 목표 "주민의 힘으로 이끌어가는 삶터"'],['도시재생 혁신지구 가이드라인','기능 2개 이상 집적(산업·주거·문화·생활SOC) · 쇠퇴 3지표 중 2개 · 면적 200만㎡ 이하 · 계획서에 이용인구·수요 추정과 운영 주체 필수 · 공공청사는 국비 대상 제외  [T2]']];
 up.forEach((u,i)=>{const y=1.8+i*1.25; rect(s,0.5,y,0.12,1.05,i<2?RED:G4); T(s,u[0],0.75,y,6.6,0.3,{size:11.5,bold:true}); T(s,u[1],0.75,y+0.32,6.6,0.75,{size:10,color:G4,ls:1.25});});
 label(s,'경주시 구상 (2026.02)  [T2·T4]',7.9,1.45,4.9);
 const prog=[['K-헤리티지 복합거점','구 역사·전시·공연·체험'],['미래모빌리티 통합허브','복합환승·주차·신교통'],['경주 STAY','체류·숙박·상업']];
 prog.forEach((p,i)=>{const y=1.8+i*0.62; rect(s,7.9,y,0.12,0.5,RED); T(s,p[0],8.1,y,4.7,0.28,{size:11.5,bold:true}); T(s,p[1],8.1,y+0.27,4.7,0.25,{size:9.5,color:G4});});
 ln(s,7.9,3.75,12.83,3.75);
 stat(s,'3,822','억 원','구상 사업비 · 국비 250억 원  [T4, 원문 미확인]',7.9,3.85,2.4,{size:20,color:INK,dsize:9.5});
 stat(s,'79,438','㎡','1단계 범위 · 준주거 20,262 · 상업 17,819 · 문화 12,260 · 도로 19,643 · 공원 9,454  [T2]',10.3,3.85,2.5,{size:20,color:INK,dsize:9.5});
 label(s,'절차',0.5,5.6,4);
 bullets(s,['2026.01  경주시–국가철도공단 MOU(도시재생 혁신지구 공모 협력)  [T4]   ·   2026 하반기  국토교통부 도시재생 혁신지구 공모 예정  [T4]','시 구상 2단계  민자 유치(시청 이전 포함) · 공공청사는 국비 대상 제외  [T2]'],0.5,5.95,12.3,0.9,{size:10.5});
 SRC(s,'2030 경주도시기본계획(승인) · 경주시 도시재생 전략계획(변경, 2022) · 김권일 발표자료(2026) · 도시재생 혁신지구 가이드라인 · 경주시 보도자료(2026.02)');}"""),
# 09
("'고시 결정도 · 매장유산 조사 · 접속 가로 · 필지·건축물대장 · 고도지구'","'라이노 계획 경계·획지 · 매장유산 조사 · 접속 가로 · 필지·건축물대장 · 고도지구'"),
# 12 caption
("SRC(s,'소상공인365 2025.06–2026.06 월평균 · 통신 기반 추정, 보행량 아님 · 원 면적 ∝ 명/ha · 점선 = 고시 구역');","SRC(s,'소상공인365 2025.06–2026.06 월평균 · 통신 기반 추정, 보행량 아님 · 원 면적 ∝ 명/ha · 붉은 면 = 본 계획 경계');"),
# 13 남북 지도 → 벡터
(" await img(s,A+'/northsouth.png',0.5,1.35,5.2,5.45,'contain','left');"," await img(s,A+'/northsouth_v.png',0.5,1.35,5.2,5.45,'contain','left');"),
# 15 ④ 패널
("['reg_plan','④ 지구단위계획','고시 결정도: 공원·상업·공공청사·문화·주차 · 주거 없음','경주시 고시 제2026-8호  [T1]']","['reg_plan','④ 지구단위계획(본 계획 수립)','본 계획이 경계·획지·용도·밀도·높이를 새로 정함 · 현 용도지역(자연녹지)과의 정합은 용도지역 변경 전제','본 계획 획지(라이노 최종)']"),
("'비율은 최종 경계 228,025㎡ 기준 재산정(2026.10.11). 고도지구 합 101%는 지구 중첩. 규제는 목적함수 페널티가 아니라 건축 불가 조건으로 둔다.'","'비율은 최종 경계 228,025㎡ 기준 재산정(2026.10.11). 고도지구 합 101%는 지구 중첩. ④는 기존 결정이 아니라 본 계획이 새로 수립하는 지구단위계획. 규제는 목적함수 페널티가 아니라 건축 불가 조건으로 둔다.'"),
# 16
("'시굴조사 필요 145,879㎡(고시 구역 156,460㎡의 93.2%), 지표조사 범위 148,770㎡(2022). 김권일 발표자료 pp.8·22. 조사 전 지하 개발 제외 → 주차는 지상 주차전용건축물.'","'시굴조사 필요 145,879㎡(철도 부지 148,770㎡의 98.1%), 지표조사 범위 148,770㎡(2022). 김권일 발표자료 pp.8·22. 조사 전 지하 개발 제외 → 주차는 지상 주차전용건축물.'"),
(" stat(s,'145,879','㎡','시굴조사 필요 면적 · 고시 구역의 93.2%  [T2, 2022 지표조사]',8.4,1.4,4.4,{size:30});"," stat(s,'145,879','㎡','시굴조사 필요 면적 · 철도 부지 148,770㎡의 98.1%  [T2, 2022 지표조사]',8.4,1.4,4.4,{size:30});"),
# 24
("{const s=slide('도시의 특징 : 정주','야간 활동과 정주 기능의 공백','소상공인365 2026.06 시간대별 추정 유동. 23–05시 비중 폐역 구역 3.7 / 행복황촌 4.4 / 성동시장 5.0 / 황리단길 5.5%. 시민 요구는 응답자 55명 복수응답 58건(2025). 고시 결정도 주거용지 0.');",
 "{const s=slide('도시의 특징 : 정주','야간 활동과 정주 기능의 공백','소상공인365 2026.06 시간대별 추정 유동. 23–05시 비중 폐역 구역 3.7 / 행복황촌 4.4 / 성동시장 5.0 / 황리단길 5.5%. 폐역 구역 상시 거주 27명·직장 117명(통신 추정). 시민 요구는 응답자 55명 복수응답 58건(2025).');"),
(" await img(s,A+'/reg_plan.png',5.9,1.4,2.3,3.2,'contain','left');\n RUNS(s,[{t:'주거용지 ',size:22,bold:true,color:RED},{t:'0',num:true,size:30,bold:true,color:RED}],8.4,1.45,4.4,0.7,{valign:'bottom'}); T(s,'고시 결정도의 별도 용지 배분 · 허용 건축물은 시설별 검토',8.4,2.2,4.4,0.4,{size:10.5,color:G4});\n label(s,'구 경주역 부지에 대한 시민 요구 (건)  [T2, 응답 55명 복수응답]',8.4,2.75,4.4);\n barH(s,['문화·쇼핑','교통 거점','지식·기술센터','공공기관','주거'],[37,16,3,3,1],8.4,3.05,4.4,2.3,{max:44,color:G4});",
 " stat(s,'27','명','폐역 구역 상시 거주 인구 · 직장 인구 117명 (통신 추정)  [T2]',5.9,1.45,2.3,{size:30,dsize:9.5});\n label(s,'구 경주역 부지에 대한 시민 요구 (건)  [T2, 응답 55명 복수응답]',8.4,1.45,4.4);\n barH(s,['문화·쇼핑','교통 거점','지식·기술센터','공공기관','주거'],[37,16,3,3,1],8.4,1.75,4.4,2.9,{max:44,color:G4});"),
("SRC(s,'소상공인365 2026.06 · 경주시 고시 제2026-8호 · 원도심 미래구상 기획연구(2025) 시민 설문');","SRC(s,'소상공인365 2026.06 · 원도심 미래구상 기획연구(2025) 시민 설문');"),
# 26 ⑤
("['⑤','정주 공백과 치환 위험',A+'/reg_plan.png','주거용지 0 · 야간 유동 3.7%\\n관광·체류 +7 · 생활 0 · 생활소매 −9']","['⑤','정주 공백과 치환 위험',A+'/footfall_density.png','상시 거주 27명 · 야간 유동 3.7%\\n관광·체류 +7 · 생활 0 · 생활소매 −9']"),
# 34
(" stat(s,'0','','결정도 주거용지 · 야간 유동 3.7%',6.98,2.45,1.8,{size:24,dsize:9.5});"," stat(s,'27','명','구역 상시 거주 · 야간 유동 3.7%',6.98,2.45,1.8,{size:24,dsize:9.5});"),
("'부족한 것: 결정도에 주거용지가 없어 용도지역 변경 전제 · 경주 입주율·수요 실측 없음'","'부족한 것: 현재 자연녹지지역이라 용도지역 변경 전제 · 경주 입주율·수요 실측 없음'"),
("'청년창업·기업지원: 시 구상 3-1, 시굴계획서 직주근접·젊은 층 정착, 혁신지구 가이드라인 p.14 지자체 운영 기업지원센터 국비 보조. 청년주거: 결정도 주거 0, 시 구상 1단계 준주거 20,262㎡(25.5%), 혁신지구 선정 17곳 중 14곳 주거 포함. 경주 입주율 실측 없음 → 단계 공급.'","'청년창업·기업지원: 시 구상 3-1, 시굴계획서 직주근접·젊은 층 정착, 혁신지구 가이드라인 p.14 지자체 운영 기업지원센터 국비 보조. 청년주거: 구역 상시 거주 27명, 시 구상 1단계 준주거 20,262㎡(25.5%), 혁신지구 선정 17곳 중 14곳 주거 포함. 경주 입주율 실측 없음 → 단계 공급.'"),
# 33 판단 근거 문구
("'● 강함  ◐ 중간  ○ 약함 · 판단 근거: 전략계획 쇠퇴원인 1번 [T1] · 시 구상 3-1·1-1·1-2·2-1 [T2] · 혁신지구 가이드라인(기능 집적, 국비 대상) [T2] · 고도·매장유산 [T1] · 수요 자료 유무'","'● 강함  ◐ 중간  ○ 약함 · 판단 근거: 전략계획 쇠퇴원인 1번 [T1] · 시 구상 3-1·1-1·1-2·2-1 [T2] · 혁신지구 가이드라인(기능 집적, 국비 대상) [T2] · 고도지구·매장유산 [T1] · 수요 자료 유무'"),
# 45 규제 비율 문장
("'규제 비율은 최종 경계 228,025㎡ 기준으로 2026.10.11 재산정했습니다. 접속점·우회율·시굴 비율은 이전 경계·고시 구역 기준이며 다음 단계에서 재산정합니다.'","'규제 비율은 최종 경계 228,025㎡ 기준으로 2026.10.11 재산정했습니다. 접속점·우회율은 이전 분석 경계, 시굴 비율은 철도 부지 기준이며 다음 단계에서 재산정합니다.'"),
# 14 traffic legend
("[INK,'본 계획 경계(점선)']","[INK,'본 계획 경계']"),
]
for a,b in reps:
    assert a in d, 'deck: '+a[:80]; d=d.replace(a,b)
assert '고시' not in d.replace('고시 제2020-479호','').replace('경북 고시','') or True
io.open('deck.js','w',encoding='utf-8').write(d)
import re
left=[m.start() for m in re.finditer('고시',d)]
print('patched; remaining 고시 mentions:',len(left))
for i in left: print('  ...',d[max(0,i-40):i+30].replace('\n',' '))
