import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const ROOT='C:/Users/OFFICE/Desktop/9_도시';
const BASE=ROOT+'/work/20261011_visual_front',B=BASE+'/build',A=B+'/assets';
const OB=ROOT+'/work/20261010_nexus_front/build',OA=OB+'/assets';
const PH=ROOT+'/work/20261008_presentation_front/assets/photos';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const RT='C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=RT+'/node/node_modules';
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
const E=JSON.parse(await fs.readFile(B+'/evidence.json','utf8'));
const cfg=JSON.parse(await fs.readFile(ROOT+'/gj-datamap/src/layers.json','utf8'));
const LP=JSON.parse(await fs.readFile(B+'/map_label_positions.json','utf8'));
const FONT='Pretendard';
const C={ink:'#25282A',sub:'#62696D',line:'#C9CED0',soft:'#F3F4F3',green:'#61776C',blue:'#5D7B8B',red:'#A16B59',purple:'#A29AB1'};
const pres=Presentation.create({slideSize:{width:1344,height:1008}});pres.theme.defaultFont=FONT;
let id=0,num=4;const chartOwners=[],tableOwners=[];
function shape(s,g,x,y,w,h,fill='none',stroke='none',lw=0){return s.shapes.add({geometry:g,name:'element-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:lw}});}
function tx(s,t,x,y,w,h,size=26,bold=false,color=C.ink,align='left'){const a=shape(s,'textbox',x,y,w,h);a.text=t;a.text.style={fontSize:size,typeface:FONT,color,bold,alignment:align,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};return a;}
function rule(s,x,y,w,c=C.line,lw=1){return shape(s,'line',x,y,w,0.1,'none',c,lw);}
async function im(s,file,x,y,w,h,fit='contain'){return s.images.add({blob:new Uint8Array(await fs.readFile(file)),contentType:file.toLowerCase().endsWith('.png')?'image/png':'image/jpeg',alt:path.basename(file),fit,position:{left:x,top:y,width:w,height:h}});}
function base(sec,title,sub,src,notes=''){const s=pres.slides.add();s.background.fill='#FFFFFF';num++;tx(s,'NEXUS 1918',54,35,290,30,23,true);tx(s,sec,420,36,580,30,21,false,C.sub,'center');tx(s,'CULTURAL INTERCHANGE',1030,38,260,26,17,false,C.sub,'right');rule(s,54,87,1236);tx(s,title,54,120,1236,64,44,true);if(sub)tx(s,sub,54,190,1236,43,23,false,C.sub);rule(s,54,948,1236);tx(s,src,54,961,1120,26,14,false,C.sub);tx(s,String(num).padStart(2,'0'),1215,955,75,36,24,true,C.ink,'right');s.speakerNotes.text=notes+'\n근거 대조: '+ROOT+'/work/20261010_direction_brief/20261010_final_direction_evidence_v1.md. 지도 캡처: https://1tree1.github.io/gj-datamap/index.html, 2026-10-11 열람. 원자료 스냅샷과 표시 레이어·범위: '+B+'/web_data 및 capture_manifest.json/capture_refined_manifest.json. 웹 조작부 제거, 범례·핵심 표기는 편집 가능한 Pretendard로 재구성.';return s;}
function cap(s,t,y=900){tx(s,t,54,y,1236,44,22,false,C.sub);}
function tag(s,t,x,y,w=450){tx(s,t,x,y,w,32,23,true,C.green);}
function metric(s,v,label,x,y,w=440,color=C.green,size=54){tx(s,v,x,y,w,74,size,true,color);tx(s,label,x,y+78,w,65,25,false,C.sub);}
function legend(s,items,x,y,w,size=18){const gap=w/items.length;for(const [i,[c,t]]of items.entries()){shape(s,'rect',x+i*gap,y+7,13,13,c);tx(s,t,x+i*gap+22,y,gap-25,32,size,false,C.sub);}}
function layerLegend(id){return cfg.layers.find(x=>x.id===id).legend.filter(x=>!x[1].startsWith('※'));}
function mapLabels(s,key,x,y,w,h,sw,sh,items){const sc=Math.min(w/sw,h/sh),ox=x+(w-sw*sc)/2,oy=y+(h-sh*sc)/2;for(const [name,txt,dx=0,dy=0,ww=108,hh=33,sz=23]of items){const l=LP[key].find(a=>a.name===name);if(!l)continue;const px=ox+l.xy[0]*sc,py=oy+l.xy[1]*sc;const xx=px-ww/2+dx,yy=py-hh/2+dy;if(xx<x||xx+ww>x+w||yy<y||yy+hh>y+h)continue;shape(s,'rect',xx-3,yy-2,ww+6,hh+4,'#FFFFFF/86');tx(s,txt,xx,yy,ww,hh,sz,true,C.ink,'center');}}
function popLabels(s,key,x,y,w,h){mapLabels(s,key,x,y,w,h,1300,1200,[['현곡면','현곡면',0,0],['용강동','용강동',42,-24],['황성동','황성동',-16,10],['성건동','성건동',0,0],['동천동','동천동',13,6],['황오동','황오동',0,0],['선도동','선도동',0,0],['황남동','황남동',0,-35],['월성동','월성동',0,-35]]);}
function ch(s,type,title,cats,series,x,y,w,h,o={}){
 series=series.map(a=>({...a,values:a.values.map(v=>v===null?null:Math.round(v*1e6)/1e6)}));
 const isBar=type==='bar'&&(o.direction||'bar')==='bar';
 if(isBar){cats=[...cats].reverse();series=series.map(a=>({...a,values:[...a.values].reverse(),points:a.points?.map(p=>({...p,idx:cats.length-1-p.idx}))}));}
 const c=s.charts.add(type,{position:{left:x,top:y,width:w,height:h},title,titleTextStyle:{fontSize:24,fill:C.ink,bold:true,typeface:FONT},titlePlacement:'aboveChart',categories:cats,series,
  barOptions:{direction:o.direction||'bar',grouping:o.grouping||'clustered',gapWidth:o.gap||72,overlap:o.overlap||0},lineOptions:{smooth:false,grouping:'standard'},
  hasLegend:o.legend||false,legend:{position:'bottom',overlay:false,textStyle:{fontSize:20,fill:C.sub,typeface:FONT}},
  xAxis:{visible:o.xVisible??true,textStyle:{fontSize:o.axSize||21,fill:C.sub,typeface:FONT},line:{fill:C.line,width:0.7},majorGridlines:null,tickLabelPosition:'low'},
  yAxis:{visible:o.yVisible??(type==='line'),textStyle:{fontSize:20,fill:C.sub,typeface:FONT},line:{fill:'none',width:0},majorGridlines:o.grid?{style:'solid',fill:'#E4E8E6',width:0.8}:null,numberFormatCode:o.fmt||'0',min:o.min,max:o.max,majorUnit:o.majorUnit},
  dataLabels:{showValue:o.labels??(type==='bar'),position:'outEnd',numberFormatCode:o.fmt||'#,##0',textStyle:{fontSize:23,fill:C.ink,bold:true,typeface:FONT}},chartFill:'none',chartLine:{fill:'none',width:0},plotAreaFill:'none',plotAreaLine:{fill:'none',width:0}});
 applyPresentationChartFont(c,{fontFamily:FONT});chartOwners.push(pres.slides.items.length);return c;
}
function bar(s,title,cats,values,x,y,w,h,o={}){return ch(s,'bar',title,cats,[{name:o.series||title,values,fill:o.color||C.blue,points:o.points}],x,y,w,h,o);}
function table(s,values,x,y,w,heights,widths,size=24){const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:heights.reduce((a,b)=>a+b,0),values,columnWidths:widths});t.borders.assign({style:'solid',fill:C.line,width:0.7});t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({fill:'#FFFFFF',textStyle:{fontSize:size,typeface:FONT,color:C.ink},margins:{left:18,right:14,top:17,bottom:10},anchor:'center'});t.cells.block({row:0,column:0,rowCount:1,columnCount:values[0].length}).assign({fill:C.soft,textStyle:{bold:true,fontSize:size,typeface:FONT,color:C.sub}});heights.forEach((h,i)=>t.rows[i].height=h);tableOwners.push(pres.slides.items.length);return t;}
const HISTORY='1. 경주의 역사',SITE='2. 대상지와 현황',MACRO='3. 대지분석 MACRO',MICRO='4. 대지분석 MICRO',SOC='5. 사회적 문제',SYN='6. 문제 종합';
const FF=E.footfall;const ps=n=>E.population.find(p=>p.hadm===n);const ys=E.youth;

// 05. Two original historical diagrams, short quantitative annotations.
{
 const s=base(HISTORY,'왕경·읍성의 틀','역사적 중심의 이동과 현재 원도심의 가로조직','채미옥 발표자료 pp.11–12 · 공간 분석(2026.09) · UNESCO',
 '도식: 채미옥, 천년 고도 경주의 골격구조 변화와 구경주역, PDF pp.11–12. 가로 57%는 NGII 도로중심선 길이가 공통 방위(N0.8°E, ±7.5°)에 정렬한 비율, 신라 도로의 직접 잔존율이 아니다. 약150m는 현재 격자 측정(동서147.5m/남북161.5m). 69%=68.8%, 고시구역 무게중심 반경1km의 문화유산 구역·보존지역 합집합 면적. 세계유산 4건은 석굴암·불국사, 경주역사유적지구, 한국의 역사마을(양동), 한국의 서원(옥산서원). UNESCO https://whc.unesco.org/en/list/736/ ; /976/ ; /1324/ ; /1498/.');
 await im(s,OA+'/wanggyeong.png',54,249,576,469);await im(s,OA+'/eupseong.png',714,249,576,469);
 tx(s,'신라 왕경',54,727,576,42,30,true);tx(s,'월성 중심의 왕경과 방리체계',54,778,576,32,23,false,C.sub);
 tx(s,'고려·조선 읍성',714,727,576,42,30,true);tx(s,'읍성 중심의 행정·생활권',714,778,576,32,23,false,C.sub);
 rule(s,54,834,1236);[['57%','공통 방위의 현재 가로'],['약 150m','현재 격자 규모'],['69%','반경 1km 유산·보존지역'],['4건','경주 소재 세계유산']].forEach(([v,t],i)=>{const x=54+i*315;tx(s,v,x,848,294,49,36,true,C.green);tx(s,t,x,906,294,29,20,false,C.sub);});
}
// 06. Same-window aerial timeline.
{
 const s=base(HISTORY,'철도의 역사','1918년 개업에서 2021년 폐역까지','국토교통부·국가철도공단 · 김신재(2013) · 국토지리정보원 정사영상',
 '1918.12.28 사정동 최초 개업. 1936.12.01 성동동 현재 위치로 이전. 1939.06 노선 변경은 김신재(2013) pp.387–388. 2010.11.01 신경주역 KTX 개통. 2021.12.28 구 경주역 폐역(마지막 열차12.27 23:16). 현 KTX 경주역 명칭은2023.12.28 변경. 정사영상2015/2021/2025 동일 좌표창·동일 크롭.');
 const ev=[['1918','사정동 개업'],['1936','성동동 이전'],['1939','노선 변경'],['2010','KTX 개통'],['2021','구 경주역 폐역']];
 ev.forEach(([v,t],i)=>{const x=54+i*250;tx(s,v,x,260,236,55,39,true,C.green);rule(s,x,331,220);tx(s,t,x,352,236,37,26,true);});
 for(const[i,year]of[2015,2021,2025].entries()){const x=54+i*420;await im(s,OA+`/ortho_${year}_square.jpg`,x,440,396,396,'cover');tx(s,String(year),x,855,120,40,29,true);tx(s,['철도 운영','이설 직전','폐역 이후'][i],x+126,860,270,34,24,false,C.sub);}
}
// 07. Large field photograph and three distinct area scopes.
{
 const s=base(SITE,'대상지 개요','구 경주역 폐역 부지 · 경주시 성동동 일원','경주시 고시 제2026-8호 · 김권일 발표자료 · 사용자 Rhino 실측 · 현장 사진',
 '시 구상79438㎡는 혁신지구1단계 토지이용·소유현황표 합계(102필지), 김권일PDF pp.11·23. 고시156460㎡. 계획217876㎡는 사용자 최신 Rhino 선택 폴리라인 수치이며남북944×동서300m. 차61416㎡는 두 면적의 차이며실제편입차집합면적아님. 소유코레일53.0/공단46.9/기재부0.1%는2021년 보고148770㎡ 범위(전략계획2022 PDF148/인쇄138), 최신등기자료아님. 구역사는문화관1918로활용, 코레일철도기념물2013, 국가등록문화유산과구분.');
 await im(s,PH+'/ph65_site_from_west_roof_wide.jpg',54,254,778,526,'cover');tx(s,'서측에서 본 폐역 부지',54,795,778,35,23,false,C.sub);
 [['79,438㎡','시 구상 · 1단계'],['156,460㎡','고시 구역'],['217,876㎡','계획 경계 · Rhino']].forEach(([v,t],i)=>{const y=258+i*172;tx(s,t,890,y,400,33,24,false,C.sub);tx(s,v,890,y+48,400,68,42,true,i===2?C.green:C.ink);rule(s,890,y+136,400);});
 tx(s,'남북 944m × 동서 300m',54,858,690,43,30,true);tx(s,'고시 면적과의 차이 61,416㎡',54,905,690,30,21,false,C.sub);
 tx(s,'2021년 소유 보고',890,815,400,32,22,true,C.sub);tx(s,'코레일 53.0% · 공단 46.9%',890,856,400,36,24);tx(s,'구 역사  경주문화관 1918',890,902,400,32,23);
}
// 08. One layered source diagram.
{
 const s=base(SITE,'사이트 분석 다이어그램','폐선·육교·접속점·유적점·북천의 관계','NGII·OSM·V-World · 김권일 발표자료 · 기존 접속점 조사',
 '현황도는 이전 발표의 근거 기반도식 크롭. 정사영상2025,NGII건물·보행육교도형,OSM폐선2026-09-21. 갈색 조사경계는기존218478㎡, 최신217876㎡도형아님. 검정2026-8고시도면추출. 37점은이전조사경계6m이내접촉/관통도로(서9동18남7북3). 유적점김권일2026/성림2022 문헌주소근사. 육교개방여부현장확인필요. S1부지/S2원도심1km/S3시전역. T1법령고시,T2공공통계,T3학술,T4보조자료는발표상분류.');
 await im(s,A+'/site_diagram.png',54,253,710,650);
 tag(s,'현황 레이어',813,264);[['#A16B59','기존 조사 경계'],[C.ink,'고시 구역'],[C.sub,'폐선·잔존 선로'],[C.blue,'도로 끝 접속점 37곳'],[C.purple,'문헌 기반 유적점']].forEach(([c,t],i)=>{shape(s,'rect',813,321+i*50,14,14,c);tx(s,t,842,313+i*50,448,36,26);});
 rule(s,813,584,477);tag(s,'분석 관점',813,612);tx(s,'동서 횡단\n남북 보행 연속성\n유산 조사와 초기 이용',813,666,477,124,29);
 tx(s,'접속점·윤곽은 기존 조사 기준',813,864,477,35,21,false,C.sub);
 tx(s,'S1 부지   S2 원도심   S3 경주시',54,915,635,25,18,false,C.sub);tx(s,'T1 법령·고시   T2 공공·통계   T3 학술   T4 보조',692,915,598,25,17,false,C.sub);
}
// 09. Asset relationships and actual straight-line distances.
{
 const s=base(MACRO,'입지: 도시의 접점','성동시장·읍성·대릉원과 북측 생활권 사이의 위치','NGII·UPIS·OSM 공간 분석 · 기준점: OSM 구 경주역',
 '도시맥락지도는기존근거기반지도크롭. NGII건물·하천,UPIS공원,고시지오리퍼런싱. 원은직선반경500/1000m,실제보행시간표시아님. 거리355/497/523/920/994m는OSM구경주역점EPSG5187 219649.2/360746에서자산가장가까운경계까지직선거리. 북측공원·성건생활권은방향관계이며모든북측을쇠퇴지역으로취급하지않음.');
 await im(s,A+'/city_relations.png',54,254,658,658);
 bar(s,'주요 자산까지 직선거리(m)',['성동시장','경주읍성','대릉원','동궁과 월지','황리단길'],[355,497,523,920,994],773,265,517,458,{color:C.green,gap:78});
 tx(s,'서  성동시장·상업가로\n동  행복황촌·주거 골목\n남  유적·관광권\n북  북천·공원·생활권',790,768,500,152,27);
}
// 10. The physical crossing gap, supported by field photographs.
{
 const s=base(MACRO,'동서 횡단 조건','문제 ①  폐선 노반의 도로 횡단 공백','NGII 도로중심선·육교 도형 · fabric_report.json · 현장 사진',
 '985m는도로중심선교차없는최대구간. 보행육교1개폭3.2m길이216.3m(NGIIA006,중심219756/361064)은도로횡단분석과구분. 사진ph56육교/ph63울타리。 지도는사용자데이터맵의폐선·고시구역·주요가로표시。 우회율은육교·보도미포함도로망기준이라본문사용안함. 현재울타리개구부/육교개방은현장재확인필요.');
 await im(s,A+'/physical_gap.png',54,254,536,657,'cover');
 await im(s,PH+'/ph56_site_overpass.jpg',638,254,313,243,'cover');await im(s,PH+'/ph63_site_fence_structure.jpg',977,254,313,243,'cover');
 tx(s,'보행 육교',638,512,313,36,27,true);tx(s,'부지 경계·울타리',977,512,313,36,27,true);
 metric(s,'985m','도로 횡단이 없는 구간',638,594,650,C.red,64);
 metric(s,'3.2m','보행 육교 폭 · 개방 여부 별도 확인',638,772,650,C.blue,48);
}
// 11. Remove overlapping analysis zones; retain the two comparison areas.
{
 const s=base(MACRO,'동서 유동인구 격차','문제 ①  성동시장과 행복황촌의 서로 다른 활동 밀도','소상공인365 · 2025.06–2026.06 월평균 · 사용자 데이터맵',
 '13개월통신기반추정유동일평균의면적당값. 성동시장200m1174.6명/ha,행복황촌근사구역80.3명/ha. 배율14.6277. 표시원/폴리곤은서로범위·면적다르고일부중첩;합산금지. 추정유동에는차량·반복포착포함가능,보행량아님. 도로횡단공백과밀도격차는동시에관측되나인과적효과규모는미추정. 지도의빨강점선은고시구역.');
 await im(s,A+'/footfall_close.png',54,253,790,608,'contain');
 mapLabels(s,'footfall_close',54,253,790,608,1300,1000,[['G_seongdong_market_r200','성동시장',0,0,140,39,26],['B_haengbok_hwangchon_digitized','행복황촌',0,0,140,39,26]]);
 metric(s,'약 14.6배','성동시장 / 행복황촌',897,267,393,C.green,54);
 bar(s,'추정 유동 밀도(명/ha)',['성동시장','행복황촌'],[1174.6,80.3],868,468,422,276,{fmt:'#,##0.0',color:C.green,gap:88});
 tx(s,'성동시장 반경 200m\n행복황촌 활성화구역(근사)',897,788,393,82,23,false,C.sub);
 cap(s,'통신 기반 추정 유동인구 · 보행량과 구분 · 구역별 면적이 다른 비교');
}
// 12. Three common-extent weekend traffic speed maps.
{
 const s=base(MACRO,'주말 시간대별 소통 상태','06시 · 13시 · 21시의 같은 범위 비교','ITS 평균 속도 이력 · 주말 표본 7일(2025.01–07) · 사용자 데이터맵',
 'ITS속도이력주말7일:20250111/0208/0308/0412/0510/0614/0712,월별토요일. 링크평균속도/소통상태,차량교통량(대수)아님. 3패널같은bounds,zoom,viewport. 앱급간:도시부15/25,도시고속30/50,고속40/80km/h. 회색표본없음. 중심가로의시간대별정체분포는확인가능하나남측관광가로의일괄혼잡/철도단절인과입증을직접추론하지않음.');
 for(const[i,h]of[6,13,21].entries()){const x=54+i*420;tx(s,String(h).padStart(2,'0')+'시',x,250,396,45,32,true);await im(s,A+`/traffic_we_${h}.png`,x,305,396,495,'contain');}
 legend(s,[['#d7191c','정체'],['#fdae61','서행'],['#1a9641','원활'],['#cccccc','표본 없음']],54,833,850,21);
 tx(s,'도시부 기준 15 / 25km/h',940,833,350,32,21,false,C.sub,'right');
 cap(s,'중심가로와 동측 가로의 소통 상태 분포 차이 · 지표는 평균 속도이며 교통량 아님');
}
// 13. North-south spatial assets, not a blanket statement about inactivity.
{
 const s=base(MACRO,'남북 공간 관계','문제 ②  남측 관광권과 북측 공원·생활권의 연속성','UPIS 공원·녹지 · OSM 폐선 · 관광지 위치 · 사용자 데이터맵',
 '북측황성공원방면·북천·성건생활권,남측대릉원·황리단길·읍성등자산의방향적관계. 폐선은보조공간자료OSM2026-09. 초록공원·녹지는결정시설(일부완충녹지)이며모든구역현재조성/이용가능함뜻아님. 북측활동부족이아니라서로다른생활/관광네트워크의연결과제.');
 await im(s,A+'/northsouth_clean.png',54,253,642,657);
 tag(s,'북측  생활·공원',758,263);tx(s,'황성공원 방면\n북천·성건 생활권',758,317,532,95,33,true);
 await im(s,PH+'/ph40_north_alley.jpg',758,435,243,183,'cover');await im(s,PH+'/ph52_gobun_plaza.jpg',1027,435,263,183,'cover');
 tx(s,'북측 골목',758,632,243,30,21,false,C.sub);tx(s,'남측 고분·유적권',1027,632,263,30,21,false,C.sub);
 tag(s,'남측  관광·유적',758,710);tx(s,'대릉원·황리단길\n읍성·역사문화권',758,766,532,95,33,true);
}
// 14. Different weekly demand patterns, matched to mapped comparison areas.
{
 const s=base(MACRO,'남북 활동의 시간 차이','문제 ②  생활 중심과 관광 중심의 주중·주말 활동','소상공인365 · 2026.06 요일별 추정 유동 · 분석구역별 일평균',
 '비교구역시청반경500m와황리단반경300m. 주말/주중은일평균값의비이며5일/2일총합비아님. 플랫폼표시[주중53.3,주말46.7]/[주중36.7,주말63.3]에서46.7/53.3=0.876과63.3/36.7=1.725로산출. 분석구역의성격차이이지북측전체유동감소추세아님.');
 await im(s,A+'/footfall_ns_clean.png',54,253,625,663,'contain');
 mapLabels(s,'footfall_ns_clean',54,253,625,663,1100,1200,[['F_cityhall_r500','시청 500m',0,0,135,33,23],['H_hwangridan_r300','황리단길',0,40,135,33,23]]);
 const ratios=[FF.F_cityhall_r500.weekday_pct[1]/FF.F_cityhall_r500.weekday_pct[0],FF.H_hwangridan_r300.weekday_pct[1]/FF.H_hwangridan_r300.weekday_pct[0]];
 bar(s,'주말 / 주중 일평균 비',['시청 500m','황리단길 300m'],ratios,749,273,541,324,{fmt:'0.00',color:C.green,gap:95});
 tx(s,'북측  주중 생활 활동',774,663,516,43,31,true);tx(s,'남측  주말 관광 활동',774,739,516,43,31,true);tx(s,'서로 다른 이용 시간대의 연계',774,839,516,43,28,true,C.green);
}
// 15. Four source map layers, spacious legends.
{
 const s=base(MICRO,'규제의 중첩','문제 ③  용도·높이·유산·지구단위계획의 조건','경주시 고시 제2026-8호 · 경북 고시 제2020-479호 · V-World',
 '4개도식은기존자료공간분석크롭. 고시도면지오리퍼런싱근사윤곽,최신Rhino계획경계재추적아님. 용도UQ111/고도UQ123·2020-479/유산UO301/2026-8지구단위시설. 고도15/20m는해당구역별확인. 본1단계조사전지하개발제외원칙은법률상일률금지아님.');
 const labs=['용도지역','고도지구','문화유산','지구단위계획'];
 const lg=[[['#DCE5D3','녹지'],['#E7D79B','주거'],['#D9B6BE','상업']],[['#D5DFE8','20m'],['#CCB8BA','15m']],[['#D8D2E0','보존'],['#7B8C78','시굴']],[['#D9B6BE','상업'],['#C5CEDA','공공·문화'],['#D9E5D1','공원'],['#E5E5E0','주차']]];
 for(let i=0;i<4;i++){const x=54+i*315;tx(s,labs[i],x,252,290,40,29,true);await im(s,A+`/reg_${i}.png`,x,317,290,382);if(i!==3)legend(s,lg[i],x,724,290,18);else lg[i].forEach(([c,t],j)=>{const xx=x+[0,64,166,232][j];shape(s,'rect',xx,731,10,10,c);tx(s,t,xx+16,724,j===1?82:60,28,16,false,C.sub);});tx(s,['자연녹지 중심','구역별 15m·20m','보존·조사 범위','공공·문화·상업·공원'][i],x,788,290,58,23,false,C.sub);}
 cap(s,'범위와 시설별 기준에 따른 계획 · 매장유산 조사와 협의에 따른 단계별 이용');
}
// 16. Original archaeological survey image and its actual denominator.
{
 const s=base(MICRO,'매장유산과 단계별 이용','문제 ③  지표조사 결과와 초기 개발 조건','김권일 발표자료 PDF pp.8·22 · 2022년 지표조사',
 '원본이미지김권일2026.02.27PDFp22에서추출. 전체지표조사148770㎡중145879㎡시굴필요,2891㎡제외. 시굴145879㎡의분모는148770㎡이며2026고시156460㎡나최신계획217876㎡로비율산출안함. 성동동사지II·유물산포지,내주변통일신라유적및토기기와자기편. 1단계지하개발제외는설계원칙. 지하영향없는임시이용도시굴·유산영향판단/관계기관협의조건,공원전면허용단정안함.');
 await im(s,A+'/heritage_original.jpg',54,254,542,652,'contain');
 metric(s,'145,879㎡','시굴조사 필요 면적',698,266,592,C.purple,57);
 tx(s,'지표조사 범위 148,770㎡',698,441,592,47,30,true);tx(s,'2022년 조사 범위 기준',698,500,592,36,24,false,C.sub);
 rule(s,698,585,592);tag(s,'1단계 설계 원칙',698,616);tx(s,'조사 전 지하 개발 제외',698,675,592,55,38,true,C.green);tx(s,'시굴 결과와 유산 영향에 따른\n배치·이용 단계 검토',698,761,592,95,30);
}
// 17. Existing scale, two contrasting street photos and an orientation diagram.
{
 const s=base(MICRO,'접속 조건과 도시조직','도로 끝 37곳과 동서의 서로 다른 가로 규모','NGII · 기존 접속점 조사 · 도시조직 분석(2026.09) · 현장 사진',
 '접속37점은기존218478㎡조사경계(서9동18남7북3),최신217876㎡점재산출아님. 좌도는기존현황크롭. 사진ph03서원화로/ph62동골목. 1층비율서69.4/동93.3는경계인접0~150m분석,전체행정동아님. 가로방위도map12국토지리정보원도로중심선,빨강공통격자방위57%,파랑사선5%,초록사선6%,회색기타33%반올림.');
 await im(s,A+'/anchors.png',54,253,476,590);
 tx(s,'접속점 37곳',54,864,476,44,31,true,C.blue);
 await im(s,PH+'/ph03_west_wonhwaro_bus.jpg',580,253,333,234,'cover');await im(s,PH+'/ph62_east_lane_paved.jpg',957,253,333,234,'cover');
 tx(s,'서측  상업가로',580,505,333,38,27,true);tx(s,'동측  저층 골목',957,505,333,38,27,true);
 await im(s,A+'/street_orientation.png',580,569,312,290,'contain');
 tx(s,'가로 방위 분석',580,881,312,28,21,false,C.sub);
 tag(s,'경계 인접 0–150m',939,578,351);metric(s,'69.4%','서측 1층 건물',939,630,351,C.blue,41);metric(s,'93.3%','동측 1층 건물',939,790,351,C.green,41);
}
// 18. Parcel-age evidence map; denominators explicitly stated.
{
 const s=base(MICRO,'건축물 노후도 분포','원도심의 기존 건물과 생활환경 갱신 과제','V-World 지적·건축물대장 · 사용자 데이터맵 · 2026.09 수집',
 '색은필지내최고령건물사용승인일기준경과연수. 7616수집필지중2164대장조인,12일자미상,2152경과연수확인. 20년이상1978/2152=91.9145%. 40년이상1480/2152=68.77%. 지도캡처범위와통계원자료수집범위다르므로91.9는전체수집범위로명시. 투명은미조인/건물없음,회색대장있으나일자미상. 붉은점선고시구역. 이지표는해당수집필지분포이며경주시모든건물이나노후주택법정비율로확대하지않음.');
 await im(s,A+'/age_buildings.png',54,253,902,563,'contain');
 metric(s,'91.9%','20년 이상 건물이 있는 필지',1005,288,285,C.red,51);
 tx(s,'경과연수 확인 2,152필지\n중 1,978필지\n\n원자료 수집 범위 기준',1005,478,285,169,23,false,C.sub);
 legend(s,[['#e8f3e6','10년 미만'],['#c7e0bd','10–20년'],['#f6d68a','20–30년'],['#e9975a','30–40년'],['#c8452b','40년 이상'],['#b0b0b0','일자 미상']],54,845,1236,20);
 cap(s,'필지 내 최고령 건물의 경과연수 · 투명한 필지는 미조인 또는 건물 없음');
}
// 19. Full municipal demographic change map.
{
 const s=base(SOC,'인구 변화의 공간 분포','문제 ④  원도심 감소와 외곽 생활권 증가의 병존','KOSIS 주민등록인구 DT_1B04005N · 2015–2025 연말 비교',
 '22행정동은법정동합집합근사경계,정밀공식행정경계아님. 황오동2011~2024는옛중부동인구합산,2015=8045+6314=14359/2025=9662,−32.7%;합동으로발생한가짜증가를제거. 현곡+33.3,용강+32.8,황남−44.8,황오−32.7,성건−29.0,월성−22.3. 원도심쇠퇴가폐역만의효과라는인과주장안함. 급간임의설정.');
 await im(s,A+'/population_full.png',54,253,776,658,'contain');
 tag(s,'인구 증가 생활권',885,266,405);tx(s,'현곡면  +33.3%\n용강동  +32.8%',885,320,405,104,34,true,C.green);
 rule(s,885,467,405);tag(s,'원도심 인구 감소',885,497,405);tx(s,'황남동  −44.8%\n황오동  −32.7%\n성건동  −29.0%\n월성동  −22.3%',885,551,405,195,33,true,C.red);
 tx(s,'황오동은 옛 중부동 합산',885,848,405,49,23,false,C.sub);
 legend(s,layerLegend('pop_chg'),54,914,776,15);
}
// 20. Time series makes the long-running decline explicit.
{
 const s=base(SOC,'원도심 인구의 장기 변화','문제 ④  폐역 이전부터 이어진 인구 감소','KOSIS 주민등록인구 · 2015–2025 · 2015년=100',
 '현황이인과분석아님. 같은4행정동의연말주민등록총인구를2015=100으로정규화. 황오옛중부합산기준. 폐역2021.12,2015~2021모든4동감소. 도시재생전략계획2022pp15–16·149–150이청년경제/주거기반부재,규제·가용지,외곽개발등병렬요인서술. 요인별비중이나폐역효과는미추정.');
 const years=Array.from({length:11},(_,i)=>String(i+2015));const cols=[C.red,C.blue,C.green,C.purple];
 const series=['황남동','황오동','성건동','월성동'].map((n,i)=>({name:n,values:years.map(y=>100*ps(n).yearly[y]/ps(n).yearly['2015']),line:{style:'solid',fill:cols[i],width:3.2},marker:{symbol:'circle',size:6,fill:cols[i]}}));
 ch(s,'line','인구 지수(2015=100)',years,series,54,267,856,538,{min:50,max:100,majorUnit:10,grid:true,legend:true,axSize:20});
 tag(s,'폐역 이전부터의 감소',972,275,318);tx(s,'2021.12\n구 경주역 폐역',972,331,318,94,31,true);rule(s,972,461,318);
 tx(s,'도시 외연 확장\n행정·상업 중심 이동\n보존·주거 환경',972,510,318,158,27);
 cap(s,'여러 요인이 함께 작용하는 쇠퇴 · 폐역 단독의 영향으로 해석하기 어려움',883);
}
// 21. Age distribution, one large map and direct labels.
{
 const s=base(SOC,'고령인구 분포','문제 ④  원도심의 생활·돌봄·문화 수요','행정안전부·KOSIS 주민등록인구 · 2026.08 · 65세 이상 비율',
 '2026.08값:황남50.1황오43.8월성39.0성건36.7/경주시30.0. 2015~2025변화와시점다름. 근사행정경계지도,색은비율,지도라벨은명수(비율). 급간임의설정. 북측전체가원도심보다고령이라는결론아님(황성16.9용강14.9).');
 await im(s,A+'/aging_nolabel.png',54,253,773,645,'contain');popLabels(s,'aging_nolabel',54,253,773,645);
 bar(s,'65세 이상 비율(%)',['황남동','황오동','월성동','성건동','경주시'],[50.1,43.8,39.0,36.7,30.0],862,288,428,437,{color:C.red,fmt:'0.0',points:[{idx:4,fill:'#CBD1D2'}],gap:70});
 tx(s,'생활 편의·돌봄 접근성\n주민 문화생활의 지속성',885,784,405,84,28,true,C.green);
 legend(s,layerLegend('pop_65'),54,913,773,17);
}
// 22. Youth presence is lower in Hwango, not absent.
{
 const s=base(SOC,'청년인구의 공간 분포','문제 ④  20–34세의 분포와 원도심 정주 조건','행정안전부·KOSIS DT_1B04005N · 2026.08 · 5세 구간 합',
 '청년은이슬라이드및순이동에서20~34세5세구간합으로정의,청년기본법19~34와구분. 시31387/242512=12.9%. 황오1070/9392=11.4%,0명이아님. 황성4597동천3289용강3245현곡2851=13982/31387=44.547%,명수가많은4지역이지비율상위4가아님(성건비율20.5%최대). 현황공간차이가행정동경계합동보정·시점유지.');
 await im(s,A+'/youth_nolabel.png',54,253,740,655,'contain');popLabels(s,'youth_nolabel',54,253,740,655);
 metric(s,'11.4%','황오동의 20–34세 비율',855,271,435,C.blue,55);tx(s,'경주시 평균 12.9%',855,438,435,46,30,true);
 rule(s,855,526,435);metric(s,'44.5%','황성·동천·용강·현곡의 청년 인구',855,559,435,C.green,55);tx(s,'13,982명 / 경주시 31,387명',855,733,435,40,24,false,C.sub);
 tx(s,'주거·고용·생활 편의의 결합',855,845,435,57,28,true,C.green);
 legend(s,layerLegend('pop_y2034'),54,914,740,16);
}
// 23. Annual age-band migration, including recent slowing.
{
 const s=base(SOC,'청년 순이동의 변화','문제 ④  20–24세에 집중된 누적 순유출','KOSIS 국내인구이동통계 DT_1B26002 · 경주시 전역 · 2020–2025',
 '20~34연간순이동−1951−1318−1448−976−1207−349합−7249. 20~24누계−4543=62.67%,25~29−2320,30~34−386. 2025년25~29+4,30~34+76으로일부연령순유입. 본계획의25~39정주대상과20~24교육이동과제는구분. 데이터전연령이동사유직업−283교육−625는청년사유로교차확인된값아님,본문에동일시안함. 청년질좋은고용/주거기반과제는전략계획2022p150와문헌홍기석2025,김유현2021초록에근거.');
 const cols=[C.red,C.blue,C.green];ch(s,'line','연령별 연간 순이동(명)',ys.mig_years,['20-24세','25-29세','30-34세'].map((n,i)=>({name:n.replace('-','–'),values:ys.net[n],line:{style:'solid',fill:cols[i],width:3.5},marker:{symbol:'circle',size:7,fill:cols[i]}})),54,263,856,558,{min:-1000,max:100,majorUnit:250,grid:true,legend:true});
 metric(s,'−7,249명','20–34세 · 2020–2025 누계',975,279,315,C.blue,46);metric(s,'62.7%','20–24세의 순유출 기여',975,486,315,C.red,46);
 tx(s,'2025년 순유출 둔화\n25–34세 일부 순유입',975,720,315,106,27,true,C.green);cap(s,'교육 이동과 정주 기반의 과제 구분 · 청년 고용의 질과 주거 안정성 검토');
}
// 24. Separate survey populations rather than mixing time/stay indicators.
{
 const s=base(SOC,'방문과 체류','문제 ⑤  원도심 현장 체류와 도시 관광 체류의 차이','황오동 모니터링(2024) · 경주시 제5차 관광실태조사(2024–2025)',
 '황오현장설문n188중체류n187:1–3h148/18779.14%,3–6h28/18714.97%,6–9h6/1873.21%,24h이상5/1872.67%. 축제야시장현장표본,전체관광객으로일반화불가. 관광실태6지점내국인3009:숙박55.3당일44.7평균1.8일. 공식https://www.gyeongju.go.kr/ebookData/20260107/index.html인쇄pp22/24/25. 각표본·단위·조사시점다름. 전국보다경주전체체류짧다는주장안함.');
 tag(s,'황오동 현장 설문',54,254,565);bar(s,'현장 체류시간 분포(%)',['1–3시간','3–6시간','6–9시간','24시간 이상'],[79.1,15.0,3.2,2.7],54,329,577,398,{fmt:'0.0',color:C.blue});
 tx(s,'1–3시간 79.1%',54,773,577,55,39,true,C.blue);tx(s,'응답 187명 · 축제·현장 표본',54,841,577,35,23,false,C.sub);
 tag(s,'경주시 관광 실태조사',714,254,576);bar(s,'내국인 방문 유형(%)',['숙박 방문','당일 방문'],[55.3,44.7],714,329,576,298,{fmt:'0.0',color:C.green});
 tx(s,'평균 1.8일',714,705,576,60,43,true,C.green);tx(s,'내국인 3,009명 · 6개 관광지',714,779,576,38,25,false,C.sub);tx(s,'도시 전체와 원도심을 각각 측정',714,857,576,42,26,true);
}
// 25. Actual arrival geography and modal dependence.
{
 const s=base(SOC,'방문 접근과 보행 전환','문제 ⑤  자동차 도착 이후 원도심 체류 동선','경주시 제5차 관광실태조사 · V-World 장소·OSM 도로·철도',
 '관광조사내국인3009자가용76.9%. 지도IC·KTX역·현재철도위치데이터출처arrival_transport/gateways/rail_stations. IC/터미널표시는방문접근맥락이며교통량대수/AADT가관광객진입량을뜻하지않음. 도착주차위치선택및보행체류전환은계획해석,실측OD아님. KTX경주역은건천읍,구경주역과구분.');
 await im(s,A+'/arrival.png',54,253,886,573,'contain');
 shape(s,'rect',266,776,198,37,'#FFFFFF/92');tx(s,'KTX 경주역',266,776,198,37,26,true,C.blue,'center');shape(s,'rect',624,575,168,37,'#FFFFFF/92');tx(s,'구 경주역',624,575,168,37,26,true,C.red,'center');
 metric(s,'76.9%','내국인 방문객의 자가용 이용',998,289,292,C.blue,51);
 tx(s,'주차·대중교통 접점\n원도심 보행 전환\n문화·유적 체류 동선',998,513,292,165,28);
 tx(s,'KTX 경주역과 구 경주역의 서로 다른 위치',54,865,886,44,29,true,C.green);
}
// 26. Night activity and land allocation are different evidence scopes.
{
 const s=base(SOC,'야간 활동과 정주 기능','문제 ⑥  초기 토지이용과 야간 활동의 공백','소상공인365 · 2026.06 · 경주시 고시 제2026-8호',
 '23~05시유동비중은전체일일추정유동에대한6시간구간비중. 3.7폐역/4.4황촌/5.0시장/5.5황리단,시청6.1은이4구역비교에제외. 구간별길이가다르므로시간당밀도와동일시금지. 고시결정도별도주거용지0. 문화1(9770㎡)은제2종일반주거지역허용건축물가능이라주택전면금지단정안함. 야간숙박자/상시거주인구를이동통신비중으로직접추정하지않음.');
 bar(s,'23–05시 추정 유동 비중(%)',['폐역 구역','행복황촌','성동시장','황리단길'],[3.7,4.4,5.0,5.5],54,286,676,410,{fmt:'0.0',color:C.blue,gap:80});
 tx(s,'23시–05시의 활동 비중',54,758,676,49,34,true,C.blue);tx(s,'상시 거주·숙박 인구와 구분',54,828,676,35,24,false,C.sub);
 await im(s,A+'/reg_3.png',818,254,265,350,'contain');metric(s,'주거용지 0','고시 결정도의 별도 용지 배분',818,654,472,C.red,44);tx(s,'허용 건축물은 시설별 별도 검토',818,847,472,57,25,false,C.sub);
}
// 27. Selected-sector Hwangchon stocks and recent change.
{
 const s=base(SOC,'행복황촌의 업종 변화','문제 ⑥  관광·체류 증가와 생활 기능의 병행 과제','소상공인365 · 2025.06–2026.06 · 행복황촌 근사구역 · 표본 11업종',
 '소상공인36511선택업종,전체업종전수아님. 생활=슈퍼편의점미용정육반찬약국백반;관광체류=카페여관호텔펜션. 2026.06생활15관광29,2025.06생활15관광22,순변화0/+7. 지도stores는소상공인상가업소재고별도데이터및시점으로참고분포,11업종변화위치와동일한점군아님. 실제주민퇴거나업종치환인과입증안함.');
 await im(s,A+'/commerce.png',54,253,628,628,'contain');
 ch(s,'bar','선택 업종군의 업소 수(개)',['생활','관광·체류'],[{name:'2025.06',values:[15,22],fill:'#CBD1D2'},{name:'2026.06',values:[15,29],fill:C.green}],740,270,550,383,{legend:true,gap:70});
 tx(s,'관광·체류  +7개',767,729,523,46,34,true,C.green);tx(s,'생활  순증 0개',767,800,523,46,34,true,C.blue);
 cap(s,'상가 업소 지도는 참고 분포 · 변화 수치는 행복황촌의 선택 11업종 기준');
}
// 28. Hwango permits tell a different and precisely scoped story.
{
 const s=base(SOC,'황오동 점포 업종의 변화','문제 ⑥  숙박 증가와 생활소매 감소의 병존','황오동 모니터링 결과보고서 · 인쇄 pp.82–86 · 2024년 인허가 자료',
 '창업70/폐업66건중축제·야시장추정임시영업27건을양쪽에서제외,43/39. 무점포통신판매12/2도점포형비교에서제외. 여섯군순변화:숙박체류+5,생활서비스의료+1,카페0,음식점제과−1,유흥오락−2,생활소매식품제조−9. 기준은인허가건수로중복사업장허가가능,고유점포실수또는직원고용변화와구분. 임시분류는30일내영업종료·장소기준프로젝트판독.');
 const groups=['숙박·체류','생활서비스·의료','카페·휴게음식','음식점·제과','유흥·오락','생활소매·식품제조'];const v=groups.map(n=>E.biz2024.open[n]-E.biz2024.close[n]);
 bar(s,'점포형 업종군별 순증감(건)',groups,v,54,269,865,557,{color:C.blue,fmt:'+0;-0;0',yVisible:true,min:-10,max:6,points:[{idx:0,fill:C.green},{idx:5,fill:C.red}],gap:64});
 metric(s,'+5건','숙박·체류',982,290,308,C.green,56);metric(s,'−9건','생활소매·식품제조',982,505,308,C.red,56);
 tx(s,'생활업종·임대료\n주민 이용의 추적',982,748,308,94,28,true);
 cap(s,'임시 영업·무점포 통신판매 제외 · 인허가 건수 기준');
}
// 29. Six short problems, each with a relevant evidence thumbnail.
{
 const s=base(SYN,'문제 종합','공간 연결, 문화·유산, 생활·정주의 여섯 과제','앞선 공간·현장·통계 자료 종합 · 지표 범위는 각 슬라이드 참조',
 '1물리985m도로공백육교존재/추정FF격차.2생활관광시간·자산관계연결.3규제4겹·145879㎡시굴은별도2022범위.4경주시청년2020~2025순이동−7249.5황오현장1~3h79.1n187와전체관광표본구분.6생활/주거/야간균형은관측및관리위험,치환인과직접입증아님.');
 const cells=[['① 동서 단절','도로 횡단 공백 985m',A+'/physical_gap.png'],['② 남북 연계','생활·관광의 활동 시간 차이',A+'/footfall_ns_clean.png'],['③ 규제와 유산','조사에 따른 단계별 이용',A+'/reg_2.png'],['④ 쇠퇴와 청년 유출','경주시 20–34세 −7,249명',A+'/population_core.png'],['⑤ 원도심 현장 체류','황오동 현장 1–3시간 79.1%',PH+'/ph00_west_wonhwaro_walk.jpg'],['⑥ 정주 기능과 치환 위험','생활업종·주거·야간의 균형',A+'/age_buildings.png']];
 for(const[i,[t,d,f]]of cells.entries()){const x=54+(i%3)*420,y=253+Math.floor(i/3)*337;tx(s,t,x,y,396,40,27,true);await im(s,f,x,y+55,396,180,'cover');tx(s,d,x,y+255,396,48,24,false,C.sub);}
}
// 30. A compact editable KPI table.
{
 const s=base(SYN,'계획 목표와 성과지표','연결, 문화·유적과 체류, 주민 생활과 청년 정주','계획의 측정 틀 · 동일 정의·범위로 기준값과 성과 비교',
 '세목표와CONNECT/EXCHANGE/SPREAD는전략별동등대응이아니라모든목표를함께지원. 여섯문제의기준은다른범위시점임을보존,횡단은계획부지,체류황오현장표본,정주활동각사업구역. 최초실시전부지상주청년고용지역조달주민문화이용임대료기준값확보필요. 임의목표수치미설정.');
 table(s,[['계획 목표','현재 확인된 조건','확인 지표'],['1  연결','도로 횡단 공백 985m\n기존 접속점 37곳','횡단 위치·간격\n동서 우회거리·남북 보행 연속성'],['2  문화·유적과 체류','황오동 현장 1–3시간 79.1%\n남측 관광·유적 자산','같은 표본의 체류시간\n북측·주변 지역 방문 분담'],['3  주민 생활과 청년 정주','황촌 생활업종 순증 0개\n주거용지·야간 활동의 과제','거주·청년 고용의 유지\n주민 문화 이용·생활업종']],54,270,1236,[63,137,137,137],[308,432,496],24);
 ['CONNECT','EXCHANGE','SPREAD'].forEach((t,i)=>{const x=54+i*420;rule(s,x,810,396);tx(s,t,x,831,396,41,29,true,C.green);tx(s,['도시·관광 네트워크 연결','관광·일상과 문화·창작의 교차','성동시장·원도심으로 활동 확산'][i],x,895,396,41,23,false,C.sub);});
}
// 31. The tourism-to-residency hypothesis and five explicit operating conditions.
{
 const s=base(SYN,'관광과 정주 연계의 성립 조건','관광 소득·일자리와 주민 정주를 함께 측정하는 계획 가설','20261010_final_direction_evidence_v1.md §2.4 · 문헌 종합에 따른 설계 조건',
 '관광규모증가→등록정주인구증가를같은설계로직접검증한연구는확인못함. 다섯조건은개별논문결론이아닌문헌종합의설계해석. 지역소득누출/고용질/주택경합/분리완충/관광과밀계획조건. 참고Sandbrook2010,Fleming&Goetz2011,Terzioglu&Gokovali2016,정상준황두현2022,López-Gay외2021,유예지김주락2024등상세근거문서. 계획성과의직접예측으로주장하지않음.');
 const items=[['01','소득의 지역 잔류','지역 소유·조달·공동 운영'],['02','일자리의 질','청년의 안정된 고용·소득'],['03','주거와 관광 수요의 비경합','거주 주택·주거비의 관리'],['04','관광 구역과 생활권의 완충','주민 이용·방문 이용의 배치'],['05','관광 규모 관리','체류·소득·정주의 동시 점검']];
 items.forEach(([n,t,d],i)=>{const y=265+i*112;rule(s,54,y,1236);tx(s,n,54,y+26,88,41,29,true,C.green);tx(s,t,179,y+24,540,45,30,true);tx(s,d,768,y+27,522,41,25,false,C.sub);});
 tx(s,'방문 지표',54,875,350,39,28,true,C.blue);tx(s,'정주 지표',490,875,350,39,28,true,C.green);tx(s,'소득 환류 지표',931,875,359,39,28,true,C.red);
}

await fs.mkdir(B+'/renders',{recursive:true});await fs.mkdir(BASE+'/output',{recursive:true});
for(const[i,s]of pres.slides.items.entries()){const stem=String(i+5).padStart(2,'0');await fs.writeFile(B+'/renders/'+stem+'.png',new Uint8Array(await(await pres.export({slide:s,format:'png',scale:1})).arrayBuffer()));await fs.writeFile(B+'/renders/'+stem+'.layout.json',await(await s.export({format:'layout'})).text());console.log('rendered',stem);}
const draft=B+'/draft.pptx';await(await PresentationFile.exportPptx(pres)).save(draft);
const run=Date.now();const staged=B+'/draft_with_chart_data_'+run+'.pptx';execFileSync(RT+'/python/python.exe',[SK+'/container_tools/materialize_literal_chart_workbooks.py',draft,staged,'--workspace',ROOT,'--receipt',B+'/chart_workbook_snapshot_'+run+'.json'],{encoding:'utf8',stdio:'pipe'});
const final=BASE+'/output/NEXUS_1918_05-31_visual_evidence_final.pptx';
await fs.writeFile(B+'/owners.json',JSON.stringify({chartOwners:[...new Set(chartOwners)],tableOwners:[...new Set(tableOwners)]}));
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:staged,finalPath:final,explicitTotalSlideCount:27,requiredNativeChartOwnerSlides:[...new Set(chartOwners)],requiredEmbeddedWorkbookChartOwnerSlides:[...new Set(chartOwners)],requiredNativeTableOwnerSlides:[...new Set(tableOwners)],materializeLiteralChartWorkbooks:true,nativeChartTargetApplication:'powerpoint',fontPolicy:{basis:'user_request',families:[FONT]},pythonExecutable:RT+'/python/python.exe',integrityValidatorPath:SK+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SK+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12801600,9601200','--validate-bullet-geometry','--validate-heading-fit',...[...new Set(tableOwners)].flatMap(n=>['--require-native-table-slide',String(n)])],verifyArtifactToolImport:true,receiptPath:B+'/validation_'+run+'.json'});
console.log(JSON.stringify(result));
