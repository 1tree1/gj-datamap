import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const R='C:/Users/OFFICE/Desktop/9_도시',B=R+'/work/20261011_analysis_redesign/build',A=B+'/assets',PH=R+'/work/20261008_presentation_front/assets/photos';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const {applyPresentationChartFont}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
const E=JSON.parse(await fs.readFile(R+'/work/20261011_visual_front/build/evidence.json','utf8'));
const G=JSON.parse(await fs.readFile(B+'/geometry.json','utf8'));
const F=JSON.parse(await fs.readFile(R+'/archive/C_data/processed/fabric_report.json','utf8'));
const C={ink:'#20272E',sub:'#56616A',red:'#235D82',blue:'#235D82',orange:'#B66A2B',green:'#B66A2B',grey:'#AEB6BE',light:'#EEF1F3',line:'#CED4DA'};
const FONT='Pretendard';const p=Presentation.create({slideSize:{width:12191695/9525,height:720}});p.theme.defaultFont=FONT;
let id=0;const owners=[],manifest=[];
function sh(s,g,x,y,w,h,fill='none',stroke='none',lw=0){return s.shapes.add({geometry:g,name:'analysis-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:lw}});}
function t(s,v,x,y,w,h,z=22,b=false,c=C.ink,a='left'){const q=sh(s,'textbox',x,y,w,h);q.text=String(v);const zz=z>=40?Math.min(54,Math.round(z*.76)):z>=28?Math.round(z*.84):z>=21?z-2:z;q.text.style={fontSize:zz,typeface:FONT,color:c,bold:false,alignment:a,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};return q;}
function ln(s,x,y,w,c=C.line,lw=1){return sh(s,'line',x,y,w,.1,'none',c,lw);}
async function im(s,f,x,y,w,h,fit='contain',crop){return s.images.add({blob:new Uint8Array(await fs.readFile(f)),contentType:f.toLowerCase().endsWith('.png')?'image/png':'image/jpeg',alt:path.basename(f),fit,position:{left:x,top:y,width:w,height:h},...(crop?{crop}: {})});}
function base(sec,title,sub,insight,source,notes=''){
const n=10+p.slides.items.length+1,s=p.slides.add();s.background.fill='#FFFFFF';sh(s,'rect',0,0,1280,2,C.red);
t(s,'현황과 분석  /  '+sec,48,24,1060,26,16,true,C.red);t(s,title,48,60,1180,56,36,true);t(s,sub,48,120,1180,30,18,false,C.sub);
ln(s,48,594,1184,C.line,.7);t(s,'해석',48,611,63,31,14,false,C.sub);t(s,insight,120,607,1100,56,22,false);
t(s,source,48,677,1120,27,13.5,false,C.sub);t(s,String(n).padStart(2,'0'),1185,675,47,28,17,true,C.sub,'right');
s.speakerNotes.text=notes+'\n출처: '+source+'\n원본: '+R+'/work/20261011_midterm_deck/output/구경주역_중간마감_v2.pptx\n수치 원자료: '+R+'/work/20261011_visual_front/build/evidence.json ; '+R+'/archive/C_data/processed/fabric_report.json\n지도: NGII 2026.09.13 연속수치지도, EPSG5179→5187. 실제 도형을 Illustrator에서 재제작. 푸른 실선은 2026.10.11 본 계획 경계. 현황 지표와 계획 해석을 구분.';
manifest.push({page:n,section:sec,title,insight,source,notes});return s;
}
function stat(s,v,label,x,y,w=300,c=C.red,z=64){t(s,v,x,y,w,83,z,true,c);t(s,label,x,y+86,w,62,21,false,C.sub);}
function label(s,v,x,y,w,c=C.ink,z=21){return t(s,v,x,y,w,33,Math.min(z,22),false,c);}
function callout(s,v,x,y,w,xy,c=C.sub,side='right'){const a=t(s,v,x,y,w,48,19,false,c);const dot=sh(s,'ellipse',xy[0]-2,xy[1]-2,4,4,c);const line=s.shapes.connect(a,dot,{kind:'straight',fromSide:side,line:{fill:c,width:.8,style:'solid'}});line.bringToFront();return a;}
function geo(name,x,y,frame){const m=G.find(m=>m.name===name),b=m.bounds,sc=Math.min(m.w/(b[2]-b[0]),m.h/(b[3]-b[1]));const scale=Math.min(frame.w/m.w,frame.h/m.h);return [frame.x+(frame.w-m.w*scale)/2+((m.w-sc*(b[2]-b[0]))/2+(x-b[0])*sc)*scale,frame.y+(frame.h-m.h*scale)/2+(m.h-((m.h-sc*(b[3]-b[1]))/2+(y-b[1])*sc))*scale];}
function chart(s,type,title,cats,series,x,y,w,h,o={}){
series=series.map(a=>({...a,values:a.values.map(v=>Math.round(v*1e6)/1e6)}));
if(type==='bar'&&(o.direction||'bar')==='bar'){cats=[...cats].reverse();series=series.map(a=>({...a,values:[...a.values].reverse(),points:a.points?.map(pt=>({...pt,idx:cats.length-1-pt.idx}))}));}
const c=s.charts.add(type,{position:{left:x,top:y,width:w,height:h},...(title?{title}:{}),titleTextStyle:{fontSize:18,fill:C.ink,bold:false,typeface:FONT},titlePlacement:'aboveChart',categories:cats,series,barOptions:{direction:o.direction||'bar',grouping:o.grouping||'clustered',gapWidth:o.gap||70,overlap:0},lineOptions:{smooth:false,grouping:'standard'},hasLegend:!!o.legend,legend:{position:'bottom',overlay:false,textStyle:{fontSize:17,fill:C.sub,typeface:FONT}},xAxis:{visible:o.xVisible??true,textStyle:{fontSize:Math.min(o.axSize||19,18),fill:C.ink,typeface:FONT},line:{fill:C.line,width:.8},majorGridlines:null,tickLabelPosition:'low'},yAxis:{visible:o.yVisible??(type==='line'),textStyle:{fontSize:17,fill:C.sub,typeface:FONT},line:{fill:'none',width:0},majorGridlines:o.grid?{style:'solid',fill:'#E1E5E9',width:.8}:null,numberFormatCode:o.fmt||'0',min:o.min??0,max:o.max,majorUnit:o.unit},dataLabels:{showValue:o.labels??(type==='bar'),position:o.grouping==='stacked'?'center':'outEnd',numberFormatCode:o.fmt||'#,##0',textStyle:{fontSize:Math.min(o.labelSize||23,21),fill:C.ink,bold:false,typeface:FONT}},chartFill:'none',chartLine:{fill:'none',width:0},plotAreaFill:'none',plotAreaLine:{fill:'none',width:0}});
applyPresentationChartFont(c,{fontFamily:FONT});owners.push(p.slides.items.length);return c;}
function bar(s,title,cats,values,x,y,w,h,o={}){return chart(s,'bar',title,cats,[{name:title,values,fill:o.color||C.red,points:o.points}],x,y,w,h,o);}
const old=R+'/work/20261011_midterm_deck/build/assets',vf=R+'/work/20261011_visual_front/build/assets';
// 11 Urban structure before diagnosing separation.
{
const s=base('도시조직','원도심은 격자 가로와 소규모 가구로 구성된다','도시조직의 경향을 대상지 계획의 기초 조건으로 분석한다','가로 방향과 가구 크기를 고려해 폐선 부지의 접속 지점을 설정한다.','국토지리정보원 연속수치지도 · 가로 212.4km 길이 가중 · 자체 계산 2026.09.28','57%는 N0.8°E±7.5°에 정렬한 도로 선분의 연장비. 신라 도로의 직접 잔존율이 아니다. 가로 격자 약150m는 기존 전체 격자의 측정값. 건축가구 단변 중앙값58m는 현재 소가구를 분석한 값이며 서로 다른 개념이다.');
const fr={x:48,y:183,w:568,h:375};await im(s,A+'/city_structure.png',fr.x,fr.y,fr.w,fr.h);
let xy=geo('city_structure',219800,361020,fr);label(s,'구 경주역',xy[0]-37,xy[1]-14,112,C.red,20);
label(s,'격자에 정렬한 가로',62,563,275,C.blue,18);label(s,'북천 변 사선 조직',348,172,247,C.sub,17);
sh(s,'rect',631,163,1,408,C.line);
const hist=JSON.parse(await fs.readFile(R+'/archive/90_derived/palimpsest_evidence_20260928.json','utf8')).orientation_hist_mod180_len_km;
t(s,'가로 방위 분포',653,163,400,30,21,false);t(s,'1° 구간별 도로 연장 (km)',1012,168,213,25,14,false,C.sub,'right');
chart(s,'bar','',hist.map((v,i)=>String(i)),[{name:'도로 연장(km)',values:hist,fill:C.grey,points:hist.map((v,i)=>({idx:i,fill:(i<=7||i>=172||Math.abs(i-89)<=7)?C.blue:C.grey}))}],650,193,575,248,{direction:'column',gap:0,min:0,max:12,unit:3,yVisible:true,xVisible:false,grid:true,labels:false});
for(const [x,lab] of [[689,'0°'],[817,'45°'],[945,'90°'],[1073,'135°'],[1202,'180°']])t(s,lab,x-20,439,46,22,14,false,C.sub,'center');
t(s,'사선 A',785,232,95,23,13,false,C.orange);t(s,'사선 B',1085,245,96,23,13,false,C.orange);
t(s,'주 격자 남북',958,205,149,23,13,false,C.blue);t(s,'주 격자 동서',1127,213,98,23,13,false,C.blue,'right');
t(s,'방위: 동=0° · 반시계 · 푸른 막대는 주 격자 ±7.5°',653,468,571,27,15,false,C.sub);
manifest[0].source='NGII 도로중심선 · 총 212.4km / 방위 분포: 0.5m 이상 선분 211.8km · 자체 계산 2026.09.28';
for(const q of s.shapes.items)if(q.text&&String(q.text).startsWith('국토지리정보원 연속수치지도 · 가로'))q.text=manifest[0].source;
t(s,'57%',653,509,233,49,43,false,C.blue);t(s,'동일 격자 방향 ±7.5°',653,559,252,26,16,false,C.sub);
t(s,'58m',948,509,239,49,43,false,C.ink);t(s,'소가구 단변 중앙값',948,559,272,26,16,false,C.sub);
manifest[0].notes+=' 방향분포는 palimpsest_evidence_20260928.json 180개 1도 구간 도로연장(km), 좌표축 기준 방위0–180도, 양방향 동일 방향으로 집계. 그래프는 전체 도로 연장에 대한 분포이며 57%는 mod90 주격자 ±7.5도에 따른 구간 합.';
s.speakerNotes.text+='\n가로 방위 그래프: archive/90_derived/palimpsest_evidence_20260928.json orientation_hist_mod180_len_km (180개 구간). 0도=동서,90도=남북,180도=동서. 길이 가중,1도 구간.';

}
// 12 Fabric comparison backed by the measured ring, with field photos.
{
const s=base('경계의 도시조직','서측과 동측의 가로 폭·건물 높이·필지 규모가 다르다','2026-8 고시구역 경계 밖 0–150m 띠 비교 · 양측을 같은 기준으로 측정','동서 연결 가로는 양측의 폭과 건축 규모 차이를 고려해 설계한다.','NGII·연속지적 · 경계 띠 분석(2026.09.28) · 사진: 2026.09 현장 답사','서측 건물602동, 동측729동. 1층 비율은 동수 기준. 도로폭과 필지면적은 중앙값. 고시구역 외측 띠의 지표이며 최종 계획 경계228025㎡ 외측 띠와 다름. 서측 사진 ph02, 동측 ph62.');
await im(s,A+'/field_collage.png',48,201,555,304,'cover',{left:0,top:0,right:1/3,bottom:0});
label(s,'서측 / 상업가로',48,168,245,C.blue);label(s,'동측 / 저층 골목',340,168,245,C.orange);
const xs=[639,884];t(s,'서측',xs[0],165,200,35,26,true,C.blue);t(s,'동측',xs[1],165,200,35,26,true,C.orange);
for(const [i,[lab,w,e,u]]of [['가로 폭',5.6,4.0,'m'],['1층 건물',69.4,93.3,'%'],['필지 면적',70,155,'㎡']].entries()){
const yy=216+i*110;t(s,lab,637,yy,220,30,18,false,C.sub);t(s,w+u,637,yy+31,220,54,40,true,C.blue);t(s,e+u,882,yy+31,275,54,40,true,C.orange);ln(s,637,yy+91,548);
}
t(s,'가로 폭·필지 면적은 중앙값',48,512,550,28,18,false,C.sub);t(s,'고시구역 기준 동일한 150m 분석 띠',48,544,570,28,18,false,C.sub);
}
// 13 Isovists, identical scale and direct labels.
{
const s=base('공간의 경험','가시 면적은 골목에서 작고 폐선 부지에서 크다','반경 150m · 건물과 담장을 장애물로 계산한 가시 영역 · 세 지도는 같은 축척','가시 면적만으로 접근성을 판단할 수 없다. 골목과 부지의 보행 연결을 함께 검토한다.','NGII 건물·담장 · 광선 720개 · 원 계산 2026.09.28','원자료 gj_reading_20260928.json의 지점과면적을 사용. 새 도형은 0.1m로 저장된 지점 좌표에서 재계산되어 원 면적과 0.7% 이하 차이. 지점 x/y는각타입참조. 가시영역은 보행 가능 영역이 아니며 소유권/울타리의 통과가능성은 별도 판단.');
const rows=[['원도심 격자','isovist_0','13,901㎡','십자 가로를 따라 열림'],['황오동 골목','isovist_2','1,448㎡','건물·담장 사이의 좁은 시야'],['폐선 부지 안','isovist_5','41,664㎡','큰 빈 공간, 경계 밖과는 분리']];
for(const[i,[lab,file,val,cap]]of rows.entries()){const x=48+i*400;t(s,lab,x,161,365,38,26,true);await im(s,A+'/'+file+'.png',x,203,367,289);t(s,val,x,498,360,52,40,true,C.red);t(s,cap,x,552,375,27,18,false,C.sub);}
}
// 14 The barrier is a spatial condition, show diagram plus photo and network scale.
{
const s=base('동서 단절','폐선 부지의 경계에서 동서 가로 연결이 끊긴다','횡단 도로의 공백, 보행 우회율, 기존 육교의 규모를 비교한다','폐역 이후에도 횡단 공백이 남아 있다. 기존 가로와 연결되는 동서 보행축이 필요하다.','NGII 도로중심선·보행육교 · 횡단 도로 분석 2026.09.28 · 현장 답사','985m는분석철도축의 도로횡단 부재 길이. 3.5배는고시구역 y범위50m표본 우회율 중앙값. 육교 길이216.3m/폭3.2m, 개방여부는시기별현장확인. 접속점37은이전조사경계6m내접촉도로, 최종경계의 재산정값이아님.');
const fr={x:48,y:180,w:740,h:357};await im(s,A+'/context_massing.png',fr.x,fr.y,fr.w,fr.h);const m=G.find(m=>m.name==='context_massing');
callout(s,'서측 가로 끝',58,173,148,geo('context_massing',...m.centers.west,fr),C.blue);
callout(s,'동측 골목 끝',642,530,144,geo('context_massing',...m.centers.east,fr),C.orange,'left');
callout(s,'폐선 부지',58,507,135,geo('context_massing',...m.centers.site,fr),C.red);
t(s,'건물 외곽선·층수에 따른 축측도 / 층고 3.5m 가정, 높이 2.5배 과장',48,564,740,25,13.5,false,C.sub);
t(s,'985 m',843,174,220,68,58,false,C.red);t(s,'도로 횡단이\n없는 구간',843,244,203,61,18,false,C.sub);
t(s,'3.5배',1081,174,160,68,58,false);t(s,'보행 우회율\n중앙값',1081,244,156,61,18,false,C.sub);
await im(s,PH+'/ph56_site_overpass.jpg',843,328,359,215,'cover');t(s,'보행 육교 1개 / 폭 3.2m',843,554,359,27,17,false,C.sub);
}
// 15 Genuine comparable density, not visually misleading circle diameters.
{
const s=base('동서 활력 격차','성동시장의 추정 유동 밀도는 행복황촌의 14.6배다','13개월 평균 추정 유동 밀도(명/ha) · 2025.06–2026.06','성동시장과 행복황촌의 이용 강도 차이를 줄일 수 있는 동서 연결을 검토한다.','소상공인365 · 통신 기반 추정 유동 · 행복황촌은 근사 경계','성동시장 반경200m12.57ha, 행복황촌16.45ha근사, 폐역은고시구역15.85ha. 구역이중첩되어합산불가. 통신추정유동은 보행 통행량이아님. 1174.6/80.3=14.6276. 지도는최종경계, 수치폐역구역은고시구역으로범위다름.');
const fr={x:48,y:166,w:490,h:410};await im(s,A+'/activity_ew.png',fr.x,fr.y,fr.w,fr.h);
const mm=G.find(m=>m.name==='activity_ew');for(const [key,c]of [['G_seongdong_market_r200',C.blue],['B_haengbok_hwangchon_digitized',C.orange]]){const xy=geo('activity_ew',...mm.centers[key],fr);sh(s,'ellipse',xy[0]-7,xy[1]-7,14,14,c,'#FFFFFF',2);}
callout(s,'성동시장',51,300,125,geo('activity_ew',...mm.centers.G_seongdong_market_r200,fr),C.blue);callout(s,'행복황촌',421,502,124,geo('activity_ew',...mm.centers.B_haengbok_hwangchon_digitized,fr),C.orange,'left');t(s,'색 영역 = 추정 유동 집계 구역',64,552,475,26,17,false,C.sub);
bar(s,'추정 유동 밀도 (명/ha)',['성동시장','행복황촌','폐역 구역'],[1174.6,80.3,79.3],570,171,643,257,{min:0,max:1400,color:C.blue,fmt:'0.0',points:[{idx:1,fill:C.orange},{idx:2,fill:C.grey}]});
stat(s,'14.6배','성동시장 / 행복황촌 밀도 비',620,453,580,C.red,62);
}
// 16 North/south actual temporal differentiation, avoid asserting unmeasured widening.
{
const s=base('남북의 이용 패턴','황리단길은 주말, 시청 생활권은 주중 유동이 높다','주말/주중 일평균 유동 비 · 1.0은 같은 수준','관광·생활·업무 거점 사이의 이동과 주중·주말 이용 차이를 함께 고려한다.','소상공인365 2025.06–2026.06 · 황리단길300m / 동천동 시청500m','주말비중/주중비중은집계가각구간평균인원정의인지원자료참조. 원덱표현1.72와.88그대로유지. 황리단길63.3/36.7=1.7248, 시청46.7/53.3=.8762. 도시불균형의공간분포증거이며남북격차가시계열로확대되었다는분석은아님. 북측성건동과황성용강동천북부신도시권을구분.');
const fr={x:48,y:160,w:565,h:414};await im(s,A+'/activity_ns.png',fr.x,fr.y,fr.w,fr.h);
const mm=G.find(m=>m.name==='activity_ns');for(const [key,c]of [['F_cityhall_r500',C.blue],['H_hwangridan_r300',C.orange]]){const xy=geo('activity_ns',...mm.centers[key],fr);sh(s,'ellipse',xy[0]-7,xy[1]-7,14,14,c,'#FFFFFF',2);}
callout(s,'시청\n생활·업무',484,197,149,geo('activity_ns',...mm.centers.F_cityhall_r500,fr),C.blue,'left');callout(s,'황리단길\n관광',48,466,136,geo('activity_ns',...mm.centers.H_hwangridan_r300,fr),C.orange);label(s,'구 경주역',276,340,157,C.red,19);
bar(s,'주말 / 주중 유동 비',['황리단길','시청 생활권'],[1.72,.88],656,196,535,233,{max:2,min:0,fmt:'0.00',color:C.orange,points:[{idx:1,fill:C.blue}]});
t(s,'주말 유동 우세',705,448,229,38,24,true,C.orange);t(s,'주중 유동 우세',958,448,250,38,24,true,C.blue);t(s,'황리단길 21,403명/일',682,514,495,31,24,true);
}
// 17 Recomputed comparable annual snapshots, preserves temporal cause limits.
{
const s=base('원도심 공동화','2015–2025년 인구는 원도심에서 감소하고 외곽에서 증가했다','동일한 연말 주민등록인구 · 2015→2025 · 증감률(%)','주민 감소 지역에는 방문객 유입과 구분되는 정주 기반 회복 전략이 필요하다.','KOSIS 주민등록인구 · 황오동은 중부동 통합 시계열 · 자체 재계산','황오동2011–2024는중부동합산,2025통합행정동. 황남6561→3621,황오14359→9662,성건17320→12300,월성6753→5245,용강18625→24734,현곡16196→21582. 4개동44993→30828=-31.48%, 합계는슬라이드에표시하지않음. 감소는폐역이전부터시작하여폐역의단독인과효과로해석하지않음.');
const fr={x:48,y:168,w:595,h:401};await im(s,A+'/population_map.png',fr.x,fr.y,fr.w,fr.h);const pm=G.find(m=>m.name==='population_map');
callout(s,'현곡면 / 증가',48,214,150,geo('population_map',...pm.centers['현곡면'],fr),C.orange);
callout(s,'용강동 / 증가',474,188,170,geo('population_map',...pm.centers['용강동'],fr),C.orange,'left');
callout(s,'원도심 / 감소',48,468,180,geo('population_map',...pm.centers['황오동'],fr),C.blue);
t(s,'법정동 합집합의 근사 경계 / 공간 분포를 보여주는 지도',48,565,605,23,13.5,false,C.sub);
const ds=['황남동','황오동','성건동','월성동','용강동','현곡면'];const vals=ds.map(n=>{const v=E.population.find(x=>x.hadm===n).yearly;return Math.round((v['2025']/v['2015']-1)*1000)/10;});
bar(s,'2015→2025 인구 증감률 (%)',ds.map(x=>x==='황오동'?'황오·중부':x),vals,673,175,525,383,{min:-70,max:45,fmt:'+0.0;-0.0;0.0',color:C.red,points:[{idx:4,fill:C.green},{idx:5,fill:C.green}],labelSize:21,axSize:18});
}
// 18 Two different population age metrics visibly kept separate.
{
const s=base('청년과 고령화','고령 인구 비율이 높고, 청년 비율은 지역별로 다르다','2026.08 주민등록 · 65세 이상과 20–34세를 구분해 비교','고령 주민의 일상 접근성과 지역별 청년의 일자리·주거 수요를 구분해 반영한다.','주민등록인구 2026.08 · 연령별 구성비(%)','황남65세50.1,황오43.8,월성39,성건36.7. 청년20–34황남7황오11.4성건20.5용강13.2동천16.7. 성건동의청년비율이높다는예외를보존, 원도심청년비율모두낮다는주장배제. 청년과고령은서로보완합계100인집단아님.');
bar(s,'65세 이상 비율 (%)',['황남동','황오동','월성동','성건동'],[50.1,43.8,39,36.7],48,179,570,345,{max:60,fmt:'0.0',color:C.red,labelSize:24});
bar(s,'20–34세 비율 (%)',['황남동','황오동','성건동','동천동','용강동'],[7,11.4,20.5,16.7,13.2],668,179,566,345,{max:25,fmt:'0.0',color:C.blue,labelSize:24});
t(s,'황남동은 주민의 절반이 65세 이상',71,548,562,30,21,true,C.red);t(s,'성건동의 높은 청년 비율도 함께 고려',689,548,542,30,21,true,C.blue);
}
// 19 Native annual series, zero line, no fake youth causality.
{
const s=base('청년 순유출','청년 순유출은 감소했지만, 6년 누계는 7,249명이다','경주시 20–34세 순이동(명) · 전입−전출 · 2020–2025','청년 정주 대책은 문화공간과 함께 일자리·주거 조건을 다뤄야 한다.','KOSIS 국내인구이동통계 DT_1B26002 · 전략계획 2022 인쇄쪽150','순이동원자료[-1951,-1318,-1448,-976,-1207,-349],합계-7249. 직업교육 사유는전출자신고별자료의설명이며순유출7249명의개별원인비율로추정하지않음. 2025감소349로둔화반영. 전략계획은청년경제활동주거안정지역기반부재진단.');
bar(s,'20–34세 연간 순이동 (명)',E.youth.mig_years,E.youth.net['20-34세'],48,174,783,370,{direction:'column',min:-2500,max:0,unit:500,yVisible:true,fmt:'#,##0',color:C.red,grid:true,labelSize:23,axSize:22});
stat(s,'−7,249','6년 누계 순유출 (명)',877,175,338,C.red,60);ln(s,877,351,330);stat(s,'−349','2025년 순유출 (명)',877,390,338,C.ink,59);
}
// 20 The denominator is parcels, not buildings.
{
const s=base('지역 쇠퇴','분석 대상 필지의 91.9%에 20년 이상 건물이 있다','건축물 경과연수 · 연도가 확인된 2,152필지 · 필지 단위 집계','노후 건축물 개선과 상주 인구 기반 회복을 연계한다.','건축물대장×연속지적 자체 계산 · 도시재생 전략계획 쇠퇴진단(2022)','age_counts[60,114,174,324,1480]. 20년이상1978/2152=91.91%,30년이상1804/2152=83.83%. 필지에있는건물기준집계, 건물동수기준의황오동법정노후도87.9%와분모다름. 원자료수집범위가도시전체아님.');
await im(s,A+'/age_map.png',48,205,589,340);label(s,'노후 건축 기반',48,167,267,C.blue,21);t(s,'파랑 20년 이상 · 주황 20년 미만 · 회색 자료 없음',48,550,595,27,14,false,C.sub);
bar(s,'연식 구간별 필지 수',['10년 미만','10–20년','20–30년','30–40년','40년 이상'],E.age_counts,660,167,553,259,{max:1750,color:C.red,axSize:18,labelSize:22});
stat(s,'91.9%','20년 이상 건물이 있는 필지',702,452,508,C.red,60);
}
// 21 Survey scopes are distinguishable.
{
const s=base('관광객의 부족한 조건','관광 이동은 차량 중심이며, 황오동 현장 체류는 짧다','경주시 관광객 조사와 황오동 현장 방문객 조사를 나누어 읽는다','교통·주차 불편을 줄이고, 도착 이후 보행·휴식·체류를 지원하는 시설을 검토한다.','경주시 제5차 관광실태조사 n=3,009 · 황오동 모니터링(2024) 방문객 n=187','자가용76.9%와교통혼잡주차29.6%는관광실태내국인조사. 체류1~3시간79.1%는황오동축제현장187명으로대표성제한. 전체경주방문객에게79.1%를일반화하지않음. 원덱872만은원문미확인으로삭제.');
await im(s,PH+'/ph53_hwangnidan_street.jpg',48,204,398,365,'cover');label(s,'현장 상업가로',48,168,319,C.ink,20);
bar(s,'경주시 관광객 설문 (%)',['자가용 이용','교통·주차 불편'],[76.9,29.6],480,176,730,216,{min:0,max:100,color:C.blue,points:[{idx:1,fill:C.red}],fmt:'0.0',axSize:22});
ln(s,499,429,697);stat(s,'79.1%','황오동 현장 방문객의 체류 1–3시간',504,450,710,C.red,60);t(s,'축제 현장 표본 187명 · 경주시 전체와 구분',504,565,704,24,16,false,C.sub);
}
// 22 Resident everyday-life indicators, genuine data rather than assumed needs.
{
const s=base('주민 생활 기반','행복황촌 표본의 점포 순증은 관광·체류 +7개, 생활 0개다','행복황촌 · 2025.06→2026.06 · 11개 업종 표본의 점포 수 변화','생활업종 변화와 주민의 문화·쇼핑 및 철도역 접근 요구를 함께 반영한다.','소상공인365(2026.06) · 원도심 미래구상 기획 연구(2025) 인쇄쪽63–64','시민 인터뷰는 원도심 미래구상 연구 인쇄쪽63–64. 문화쇼핑 응답 31/37과 총 응답 58/합계59가 원문에서 불일치하므로 비율·응답 수 없이 반복된 요구만 인용. 같은11업종표본 life_chg_13mo0tour_chg7. 생활은식료품의원세탁등선택업종군. 전업종총점포아님. 생활업종34.1=15/(15+29). 성동시장87.8=72/82. 관광치환의징후이며전업종이나인과관계증명아님. 현장콜라주의동측골목은ph62.');
await im(s,PH+'/ph62_east_lane_paved.jpg',48,204,373,368,'cover');label(s,'동측 주민 골목',48,168,326,C.orange,20);
bar(s,'13개월 점포 순증 (개)',['관광·체류','주민 생활'],[7,0],463,168,739,213,{min:0,max:9,color:C.red,points:[{idx:1,fill:C.blue}],axSize:23,labelSize:30});
ln(s,482,407,713);t(s,'시민 인터뷰에서 드러난 생활 요구',482,424,717,34,21,true);
t(s,'문화·쇼핑시설 부족',482,478,718,36,29,true,C.blue);t(s,'신경주역 접근 불편',482,528,718,36,29,true,C.orange);
}
// 23 Verified address points on a geographic map.
{
const notes='공식자료 재확인 2026.10.11: https://www.gyeongju.go.kr/open_content/ko/page.do?mnu_uid=2701 최종수정2026-09-02. 기린빌딩 양정로241-1 2–8층, 공식표9과. 동원빌딩 소금강로39 2–3층 전략기획과·미래사업과·농촌활력과3과; https://www.gyeongju.go.kr/council/viewer/minutes.do?uid=11670 (제299회 행정복지위원회 제2차)에서도2026년임차2·3층3과확인. 농촌활력과는공식층별표에기린과동원중복표기되어전체분산과수합산하지않음. 아동청소년과 알천북로131청소년수련관1층, 왕경조성과 임해로64-19황룡사역사문화관1층. 도시공원과 황성공원로29실내체육관남문지하1층:2026-08-13채용공고 https://www.gyeongju.go.kr/open_content/ko/page.do?mnu_uid=435&parm_bod_uid=329117&step=258. 본청 양정로260. 지도위치=gj-datamap/public/data/cityhall_sites.geojson VWorld도로명주소건물대표점. 직선거리본청–황룡사2060m반올림2.1km, 보행거리시간이아님. 외부5개시설의유형2임차+3시시설표시. 보건소는직속기관이므로본청부서분산집계에서제외하며이전대상확정주장없음.';
const s=base('공공행정 분산','본청 외부의 행정 부서는 5개 시설에 배치되어 있다','동천동의 임차 청사와 황성동·구황동의 개별 공공시설을 구분한다','통합 대상과 현장 밀착 부서를 구분하고, 분산된 행정 서비스의 이용 동선을 검토한다.','경주시 청사안내(2026.09.02) · 제299회 시의회 회의록 · 도시공원과 공고(2026.08.13)',notes);
const fr={x:48,y:168,w:828,h:414};await im(s,A+'/cityhall_map.png',fr.x,fr.y,fr.w,fr.h);
const m=G.find(g=>g.name==='cityhall_map');const labels=[['동천동 본청','본관·신관·별관·증축관',550,239,260,C.blue,'left'],['기린빌딩','2–8층 / 공식 안내 9개 과',513,330,293,C.orange,'left'],['동원빌딩','2–3층 / 3개 과',520,170,252,C.orange,'left'],['황룡사 역사문화관','왕경조성과 / 1층',565,495,287,C.blue,'left'],['청소년수련관','아동청소년과 / 1층',81,309,264,C.blue,'right'],['실내체육관','도시공원과 / 남문 지하1층',77,183,271,C.blue,'right']];
for(const[i,[lab,cap,x,y,w,c,side]]of labels.entries()){
 const xy=geo('cityhall_map',...m.centers[i],fr);sh(s,'ellipse',xy[0]-7,xy[1]-7,14,14,i===0?C.blue:i<3?C.orange:'#FFFFFF',i<3?'#FFFFFF':C.blue,1.5);
 const tb=t(s,lab,x,y,side==='right'?160:w,31,20,false,c);t(s,cap,x,y+28,w,26,14,false,C.sub);const d=sh(s,'ellipse',xy[0]-1,xy[1]-1,2,2,c);
 const ll=s.shapes.connect(tb,d,{kind:'straight',fromSide:side,line:{fill:c,width:.8,style:'solid'}});ll.bringToFront();
}
label(s,'구 경주역 대상지',367,424,211,C.blue,16);
t(s,'N',828,160,26,24,15,false,C.ink,'center');sh(s,'upArrow',835,188,11,27,C.ink);
ln(s,65,560,67,C.ink,1.5);t(s,'500m',65,538,105,23,13,false,C.sub);
sh(s,'rect',896,163,1,415,C.line);
t(s,'민간 임차',923,175,306,32,22,false,C.orange);t(s,'2개소',923,215,306,57,43,false,C.orange);t(s,'기린빌딩 · 동원빌딩',923,274,304,29,18,false,C.sub);
ln(s,923,324,302);
t(s,'별도 공공시설',923,345,305,32,22,false,C.blue);t(s,'3개소',923,384,305,57,43,false,C.blue);t(s,'청소년수련관 · 역사문화관\n실내체육관',923,445,307,53,17,false,C.sub);
t(s,'본청–역사문화관 약 2.1km',923,515,308,26,18,false,C.ink);t(s,'도로명주소 대표점 간 직선거리',923,544,309,25,13.5,false,C.sub);
t(s,'※ 농촌활력과가 두 임차 청사 안내에 중복 표기되어 전체 분산 부서 수는 합산하지 않았다.',48,653,1175,21,12,false,C.sub);
}
// 24 Constraints shown as a spatial overlay and area comparison, not legal conclusions.
{
const s=base('사이트의 조건','대상지 계획은 높이 조건과 유산 조사를 고려해야 한다','보존·높이 조건과 매장유산 조사 범위를 구분한다','높이 조건과 유산 조사 결과를 건축 배치 및 단계별 이용 계획에 반영한다.','문화유산 관련 도면·NGII · 김권일 발표(2026) · 자체 경계 중첩 계산','높이84.5%는최종계획경계228025㎡중20m고도지구중첩비이며모든건축높이허용을보장하지않음. 시굴145879㎡분모2022지표조사148770㎡로98.1%,최종계획전체비율이아님. 지하개발배제는계획제안, 모든지역에서법률이일괄금지한다는뜻아님.');
await im(s,A+'/height_map.png',48,204,401,335);await im(s,A+'/heritage_mono.png',459,204,355,363);t(s,'푸른 영역 / 20m 고도지구',66,548,388,29,16,false,C.blue);
label(s,'높이 조건',66,164,255,C.red,21);label(s,'매장유산 조사',477,164,287,C.orange,21);
stat(s,'84.5%','본 계획 경계 중 20m 고도지구',852,174,371,C.red,58);ln(s,852,348,350);stat(s,'98.1%','지표조사 범위 중 시굴 필요 면적',852,390,371,C.orange,58);
}
// 25 Upper plans transition: measured requirements instead of the deleted KPI/problem chain pages.
{
const s=base('상위계획과 대상지 역할','대상지의 주요 역할은 가로 연결과 생활·공공 기능 보완이다','기존 계획이 부여한 역할을 앞선 현황 분석과 대조한다','동서 가로 연결과 문화·공공 기능을 결합하고, 청년·주민의 생활 수요를 반영한다.','2030 경주도시기본계획 · 도시재생 전략계획(변경,2022) 인쇄쪽150·161','2030기본계획철도사적지동서남북분리인쇄285. 2022경주역부지개발148770㎡공공청사상징광장문화공원복합상업커뮤니티시설. 주거는본계획추가가정, 상위계획허용용도또는확정결정으로표현하지않음. 공공청사이전은확정아님. 원덱26상위계획을요약,원덱25지표27문제종합28문제연쇄별도슬라이드제외.');
await im(s,A+'/site_fabric.png',399,164,457,414);
const specs=[['도시 연결','끊긴 동서 가로 / 남북의 다른 이용',54,186,C.red],['문화·교류','방문·휴식 / 시장과 문화자산',54,376,C.orange],['공공·생활','분산 행정 / 주민의 일상 이용',888,186,C.blue],['청년의 기반','순유출 / 일자리와 주거',888,376,C.green]];
for(const[lab,cap,x,y,c]of specs){sh(s,'rect',x,y,314,1,c);t(s,lab,x,y+18,316,46,30,true,c);t(s,cap.replace(' / ','\n'),x,y+81,317,85,22,false,C.sub);}
sh(s,'rightArrow',345,324,88,20,C.red);sh(s,'leftArrow',806,324,72,20,C.blue);label(s,'구 경주역 부지',507,387,250,C.red,24);
}
await fs.writeFile(B+'/analysis_manifest.json',JSON.stringify({slides:manifest,nativeChartOwners:owners},null,2));
await (await PresentationFile.exportPptx(p)).save(B+'/analysis_draft.pptx');
console.log('EXPORTED',p.slides.items.length,'slides',owners.length,'charts');
await fs.mkdir(B+'/preview',{recursive:true});
for(const[i,s]of p.slides.items.entries()){
const file=B+'/preview/'+String(i+11).padStart(2,'0')+'.png';await fs.writeFile(file,new Uint8Array(await (await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));console.log('RENDER',i+11);
}



