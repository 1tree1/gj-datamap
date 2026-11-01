# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
OUT='C:/Users/OFFICE/Desktop/9_도시/work/20261015_report/fig/'
FB=lambda s: ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', s)
FR=lambda s: ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', s)
RED=(200,16,46); INK=(26,26,26); G1=(245,245,245); G2=(217,217,217); G4=(92,92,92); PALE=(247,217,221); WH=(255,255,255)
W,H=3600,1760
cv=Image.new('RGB',(W,H),WH); d=ImageDraw.Draw(cv)
def wrap(text,font,maxw):
    lines=[]; 
    for para in text.split('\n'):
        cur=''
        for ch in para:
            t=cur+ch
            if d.textlength(t,font=font)>maxw and cur:
                # break at last space if any
                if ' ' in cur and ch!=' ':
                    i=cur.rfind(' '); lines.append(cur[:i]); cur=cur[i+1:]+ch
                else:
                    lines.append(cur); cur=ch
            else: cur=t
        lines.append(cur)
    return lines
def box(x,y,w,h,title,detail,grade,fill=G1,edge=G4,tcol=INK,lw=3):
    d.rounded_rectangle([x,y,x+w,y+h],radius=18,fill=fill,outline=edge,width=lw)
    ty=y+18
    for l in wrap(title,FB(40),w-50):
        d.text((x+25,ty),l,font=FB(40),fill=tcol); ty+=52
    ty+=4
    for l in wrap(detail,FR(33),w-50):
        d.text((x+25,ty),l,font=FR(33),fill=G4 if tcol==INK else (255,255,255)); ty+=44
    if grade:
        d.text((x+25,y+h-52),grade,font=FB(33),fill=RED if tcol==INK else (255,255,255))
def arrow(x0,y,x1,dashed=False,col=INK):
    if dashed:
        x=x0
        while x<x1-30:
            d.line([(x,y),(min(x+22,x1-30),y)],fill=col,width=5); x+=40
    else:
        d.line([(x0,y),(x1-30,y)],fill=col,width=5)
    d.polygon([(x1,y),(x1-34,y-17),(x1-34,y+17)],fill=col)
d.text((40,22),'상위계획·관련계획의 체계와 본 계획의 위치',font=FB(52),fill=INK)
d.text((40,92),'실선 = 허가·상한·재원 등 본 계획이 따라야 하는 조건   /   점선 = 방향·수요를 참조하는 계획   /   [T1~T4] = 출처 등급',font=FR(34),fill=G4)
bw=880; bh=300; gx=110; x0=40; y0=170; lane=370
lanes=[
 ('① 도시계획 — 용도·밀도·높이를 정함',False,[
   ('국토계획법 체계','도시기본계획 → 도시관리계획 → 지구단위계획. 용도지역 변경은 지구단위계획 수립을 수반(2030 기본계획 인쇄쪽 177)','[T1]'),
   ('2030 경주도시기본계획','경주시. 기준 2010·목표 2030. 부지는 \'멀티복합타운\'으로 서술, 면적·밀도 수치 없음','[T1]'),
   ('용도지역 · 고도지구','자연녹지·2종일반주거·일반상업. 도심 20 m·15 m 지구(경북 고시 제2020-479호, 2020.12.28)','[T1]')]),
 ('② 도시재생 — 사업 유형·재원·특례를 정함',False,[
   ('도시재생특별법','활성화지역·혁신지구(국가시범지구) 지정, 도시혁신구역 특례, 통합심의','[T1]'),
   ('도시재생 전략계획(변경)','경주시, 2022.01. 성동지구 활성화지역 해제, 경주역 부지 방향 확정 시 재반영 검토(인쇄쪽 279)','[T1]'),
   ('활성화계획 · 혁신지구 공모','경주역전지구 281.69억·행복황촌 254.47억(2025.12 변경) / 2026 상반기 국가시범지구 가이드라인(2026.02.06)','[T1]')]),
 ('③ 문화유산·경관 — 조사·허가·경관을 정함',False,[
   ('문화유산법 · 매장유산법 · 고도 특별법','역사문화환경 보존지역, 현상변경 허가, 지표조사·시굴. 신라왕경 특별법·세계유산 완충구역은 확인 대기','[T1] 조문 확인 대기'),
   ('보존지역 · 허용기준 · 시굴','허용기준 3구역(대상지 약 2/3), 시굴 필요 145,879 ㎡(지표조사 2022.05)','[T2]'),
   ('2030 경주시 경관계획 재정비','2025.04. 황오동 중점경관관리구역 90.18 ha, 화랑로 통경축, 도로 인접 3층·15 m 가이드','[T1]')]),
 ('④ 시 구상·연구 — 방향과 수요를 참조',True,[
   ('폐철도 기본구상','경주시, 2023.04. 폐선 80.3 km·폐역 17개소, 경주역은 상업업무복합지구로 서술','[T2] 최종보고서 미확인'),
   ('원도심 미래구상 기획 연구','경주시 발주, 2025.07. 방향 5개·(옛)경주역 제안 24건. 학술 연구이며 법정 계획이 아님','[T2]'),
   ('시 구상 · MOU · 공모 추진','79,438 ㎡, 3개 프로그램, 2027~2032. MOU 2025.12.30. 총사업비 3,822억·국비 250억','[T2] / 사업비 [T4, 원문 미확인]')]),
]
for i,(lab,dash,items) in enumerate(lanes):
    y=y0+i*lane
    d.text((x0,y),lab,font=FB(38),fill=RED)
    yy=y+54
    for j,(t,dt,gr) in enumerate(items):
        x=x0+j*(bw+gx)
        box(x,yy,bw,bh,t,dt,gr)
        if j<2: arrow(x+bw+8,yy+bh//2,x+bw+gx-6,dashed=dash)
    # arrow to 본 계획
    xe=x0+2*(bw+gx)+bw
    arrow(xe+8,yy+bh//2,2994,dashed=dash,col=RED if not dash else G4)
# 본 계획

bx=3000; bwid=560
d.rounded_rectangle([bx,y0+54,bx+bwid,y0+54+4*lane-70],radius=24,fill=RED,outline=RED)
txt=[('본 계획',58,True),('NEXUS 1918',54,True),('구 경주역 도시재생',40,False),('마스터플랜',40,False),('',20,False),
     ('따르는 조건',36,True),('· 용도지역·고도지구 상한',33,False),('· 보존지역 현상변경 허가',33,False),('· 매장유산 조사 선행',33,False),('· 활성화지역 특례 적용 여부',33,False),('',20,False),
     ('참조하는 방향',36,True),('· 단절 회복·생활거점',33,False),('· 청년 정주 기반',33,False),('· 폐선축 연계',33,False),('',20,False),
     ('독립 수립',36,True),('관련 결정(2026.01 지구단위계획',31,False),('결정 고시)과 별개로 구상',31,False)]
ty=y0+54+30
for t,sz,b in txt:
    f=FB(sz) if b else FR(sz)
    d.text((bx+30,ty),t,font=f,fill=WH); ty+=int(sz*1.42)
cv.save(OUT+'02_plan_system.png',dpi=(200,200)); print(cv.size)
