import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const ROOT='C:/Users/OFFICE/Desktop/9_도시';
const BASE=ROOT+'/work/20261010_nexus_front';
const BUILD=BASE+'/build';
const AS=BUILD+'/assets';
const OLD=ROOT+'/work/20261008_presentation_front';
const SKILL='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const RUNTIME='C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=RUNTIME+'/node/node_modules';
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(SKILL+'/container_tools/artifact_tool_utils.mjs').href);
const FONT='Pretendard';
const C={ink:'#25282A',sub:'#62696D',line:'#C9CED0',soft:'#F3F4F3',green:'#61776C',blue:'#5D7B8B',red:'#A16B59',purple:'#A29AB1'};
const W=1344,H=1008;
const pres=Presentation.create({slideSize:{width:W,height:H}});
pres.theme.defaultFont=FONT;
let id=0;
function shape(s,g,x,y,w,h,fill='none',stroke='none',lw=0){return s.shapes.add({geometry:g,name:'element-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:lw}});}
function tx(s,t,x,y,w,h,size=26,bold=false,color=C.ink,align='left'){const a=shape(s,'textbox',x,y,w,h);a.text=t;a.text.style={fontSize:size,typeface:FONT,color,bold,alignment:align,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};return a;}
function rule(s,x,y,w,color=C.line,lw=1){return shape(s,'line',x,y,w,0.1,'none',color,lw);}
function line(s,x1,y1,x2,y2,color=C.line,lw=2){const x=Math.min(x1,x2),y=Math.min(y1,y2),w=Math.max(0.1,Math.abs(x2-x1)),h=Math.max(0.1,Math.abs(y2-y1));return s.shapes.add({geometry:'custom',name:'line-'+(++id),position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:color,width:lw},customPaths:[{width:w,height:h,commands:[{moveTo:{x:x1-x,y:y1-y}},{lineTo:{x:x2-x,y:y2-y}}]}]});}
function dot(s,x,y,r=5,color=C.green){return shape(s,'ellipse',x-r,y-r,r*2,r*2,color,'#FFFFFF',1);}
async function im(s,file,x,y,w,h,fit='contain'){const b=await fs.readFile(file);return s.images.add({blob:new Uint8Array(b),contentType:file.endsWith('.png')?'image/png':'image/jpeg',alt:path.basename(file),fit,position:{left:x,top:y,width:w,height:h}});}
function note(s,t){s.speakerNotes.text=t;}
function base(num,section,title,subtitle,src){const s=pres.slides.add();s.background.fill='#FFFFFF';tx(s,'NEXUS 1918',54,35,290,30,23,true);tx(s,section,420,36,580,30,21,false,C.sub,'center');tx(s,'CULTURAL INTERCHANGE',1030,38,260,26,17,false,C.sub,'right');rule(s,54,87,1236);tx(s,title,54,120,1236,64,44,true);if(subtitle)tx(s,subtitle,54,188,1236,48,23,false,C.sub);rule(s,54,948,1236);tx(s,src,54,961,1120,26,14,false,C.sub);tx(s,String(num).padStart(2,'0'),1215,955,75,36,24,true,C.ink,'right');return s;}
function tag(s,t,x,y,w=180){tx(s,t,x,y,w,28,19,true,C.green);}
function metric(s,v,label,x,y,w=390,color=C.green){tx(s,v,x,y,w,72,54,true,color);tx(s,label,x,y+76,w,55,23,false,C.sub);}
function table(s,values,x,y,width,rowHeights,colWidths,size=23){const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width,height:rowHeights.reduce((a,b)=>a+b,0),values,columnWidths:colWidths});t.borders.assign({style:'solid',fill:C.line,width:0.7});t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({fill:'#FFFFFF',textStyle:{fontSize:size,typeface:FONT,color:C.ink},margins:{left:16,right:14,top:14,bottom:10},anchor:'center'});t.cells.block({row:0,column:0,rowCount:1,columnCount:values[0].length}).assign({fill:C.soft,textStyle:{bold:true,color:C.sub,fontSize:size,typeface:FONT}});rowHeights.forEach((h,i)=>t.rows[i].height=h);return t;}
function chart(s,title,cats,values,x,y,w,h,opts={}){const ch=s.charts.add('bar',{position:{left:x,top:y,width:w,height:h},title,titleTextStyle:{fontSize:23,fill:C.ink,bold:true,typeface:FONT},titlePlacement:'aboveChart',categories:cats,series:[{name:opts.series||title,values,fill:opts.color||C.green,points:opts.points}],barOptions:{direction:opts.direction||'bar',grouping:'clustered',gapWidth:opts.gap||70},hasLegend:false,xAxis:{visible:true,textStyle:{fontSize:21,fill:C.sub,typeface:FONT},line:{fill:'none',width:0},majorGridlines:null},yAxis:{visible:false,textStyle:{fontSize:21,fill:C.sub,typeface:FONT},line:{fill:'none',width:0},majorGridlines:null,numberFormatCode:'0'},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:opts.fmt||'#,##0',textStyle:{fontSize:22,fill:C.ink,bold:true,typeface:FONT}},chartFill:'none',plotAreaFill:'none',chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0}});applyPresentationChartFont(ch,{fontFamily:FONT});return ch;}
// GRS80 / Korea East Belt 2010, EPSG:5187. Source data are kept in speaker notes.
function tm(lon,lat){const a=6378137,f=1/298.257222101,e2=f*(2-f),ep=e2/(1-e2),r=Math.PI/180,p=lat*r,p0=38*r,L=(lon-129)*r,N=a/Math.sqrt(1-e2*Math.sin(p)**2),T=Math.tan(p)**2,Q=ep*Math.cos(p)**2,A=L*Math.cos(p);function M(q){return a*((1-e2/4-3*e2**2/64-5*e2**3/256)*q-(3*e2/8+3*e2**2/32+45*e2**3/1024)*Math.sin(2*q)+(15*e2**2/256+45*e2**3/1024)*Math.sin(4*q)-35*e2**3/3072*Math.sin(6*q));}return[200000+N*(A+(1-T+Q)*A**3/6+(5-18*T+T*T+72*Q-58*ep)*A**5/120),600000+M(p)-M(p0)+N*Math.tan(p)*(A*A/2+(5-T+9*Q+4*Q*Q)*A**4/24+(61-58*T+T*T+600*Q-330*ep)*A**6/720)];}
const read=async f=>JSON.parse(await fs.readFile(f,'utf8'));
const oldBoundary=(await read(ROOT+'/work/20261005_boundary_check/user_boundary_current_5187.geojson')).features[0].geometry.coordinates[0];
const gosi=(await read(ROOT+'/archive/C_data/processed/gosi2026-8_zone_5187.geojson')).features[0].geometry.coordinates[0];
const rails=await read(ROOT+'/archive/C_data/processed/rail_abandoned_4326.geojson');
const heritage=await read(ROOT+'/archive/C_data/processed/heritage_pts_4326.geojson');
const zone=await read(ROOT+'/archive/C_data/raw/vworld_uq111.geojson');
const height=await read(ROOT+'/archive/C_data/processed/godo_5187.geojson');
const herArea=await read(ROOT+'/archive/C_data/raw/vworld_uo301_heritage.geojson');
const blocks=await read(ROOT+'/archive/C_data/processed/gosi2026-8_blocks_5187.geojson');
const spatial=await read(BUILD+'/spatial.json');
const parks=await read(ROOT+'/archive/C_data/processed/parks_upis_4326.geojson');
const anchorCsv=(await fs.readFile(ROOT+'/work/20261005_plan_massing/tables/anchors.csv','utf8')).replace(/^\uFEFF/,'').trim().split(/\r?\n/).slice(1).map(l=>{const v=l.split(',');return{dir:v[0],p:[+v[1],+v[2]]};});
function mapPos(frame,p){return[frame.x+(p[0]-frame.x0)/(frame.x1-frame.x0)*frame.w,frame.y+(frame.y1-p[1])/(frame.y1-frame.y0)*frame.h];}
function clipped(poly,fr){let r=poly;for(const [axis,bound,keep]of[[0,fr.x0,1],[0,fr.x1,-1],[1,fr.y0,1],[1,fr.y1,-1]]){let n=[];for(let i=0;i<r.length;i++){let a=r[i],b=r[(i+1)%r.length],ain=(a[axis]-bound)*keep>=0,bin=(b[axis]-bound)*keep>=0;if(ain)n.push(a);if(ain!==bin){const t=(bound-a[axis])/(b[axis]-a[axis]);n.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]);}}r=n;if(!r.length)break;}return r;}
function pathShape(s,coords,fr,fill='none',stroke=C.green,lw=2,closed=false){let p=closed?clipped(coords,fr):coords;if(p.length<2)return;const pts=p.map(a=>mapPos(fr,a));if(!closed&&pts.some(a=>a[0]<fr.x-1||a[0]>fr.x+fr.w+1||a[1]<fr.y-1||a[1]>fr.y+fr.h+1))return;const cmd=pts.map((a,i)=>i?{lineTo:{x:a[0]-fr.x,y:a[1]-fr.y}}:{moveTo:{x:a[0]-fr.x,y:a[1]-fr.y}});if(closed)cmd.push({close:{}});s.shapes.add({geometry:'custom',name:'map-layer-'+(++id),position:{left:fr.x,top:fr.y,width:fr.w,height:fr.h},fill,line:{style:'solid',fill:stroke,width:lw},customPaths:[{width:fr.w,height:fr.h,commands:cmd}]});}
function polygons(s,fc,fr,project,fn){for(const f of fc.features){const g=f.geometry;if(!g)continue;const polys=g.type==='Polygon'?[g.coordinates]:g.type==='MultiPolygon'?g.coordinates:[];for(const rings of polys){const pts=rings[0].map(a=>project?tm(...a):a);pathShape(s,pts,fr,fn(f.properties),'#FFFFFF/50',0.6,true);}}}
const FR=(x,y,w,h)=>({x,y,w,h,x0:w/h<0.9?219330:219180,x1:w/h<0.9?220230:220380,y0:360450,y1:361550});
async function siteMap(s,x,y,w,h,{anchors=false,her=false,old=true,gosiLine=false,rail=true}={}){const fr=FR(x,y,w,h);await im(s,AS+(w/h<0.9?'/site_frame_narrow.jpg':'/site_frame.jpg'),x,y,w,h,'cover');shape(s,'rect',x,y,w,h,'#FFFFFF/58');if(rail)for(const f of rails.features){if(f.geometry.type==='LineString')pathShape(s,f.geometry.coordinates.map(a=>tm(...a)),fr,'none',C.sub,1.8);}if(old)pathShape(s,oldBoundary,fr,'none',C.red,2.5,true);if(gosiLine)pathShape(s,gosi,fr,'none',C.ink,2,true);if(anchors)for(const a of anchorCsv){const[xp,yp]=mapPos(fr,a.p);if(xp>=x&&xp<=x+w&&yp>=y&&yp<=y+h)dot(s,xp,yp,4,C.blue);}if(her)for(const a of heritage.features){if(a.geometry.type==='Point'){const p=mapPos(fr,tm(...a.geometry.coordinates));if(p[0]>x&&p[0]<x+w&&p[1]>y&&p[1]<y+h)shape(s,'rect',p[0]-5,p[1]-5,10,10,C.purple,'#FFFFFF',1);}}tx(s,'N',x+w-35,y+10,24,28,20,true);const scale=200*w/(fr.x1-fr.x0);line(s,x+24,y+h-25,x+24+scale,y+h-25,C.ink,3);tx(s,'0',x+22,y+h-53,30,24,17);tx(s,'200m',x+scale-10,y+h-53,75,24,17);return fr;}
function compound(s,rings,fr,fill){let commands=[];for(const r of rings){if(!r.length)continue;const xs=r.map(p=>p[0]),ys=r.map(p=>p[1]);if(Math.max(...xs)<fr.x0||Math.min(...xs)>fr.x1||Math.max(...ys)<fr.y0||Math.min(...ys)>fr.y1)continue;const pts=clipped(r,fr);if(pts.length<3)continue;for(let i=0;i<pts.length;i++){const p=mapPos(fr,pts[i]);commands.push(i?{lineTo:{x:p[0]-fr.x,y:p[1]-fr.y}}:{moveTo:{x:p[0]-fr.x,y:p[1]-fr.y}});}commands.push({close:{}});}if(commands.length)s.shapes.add({geometry:'custom',name:'source-building-layer-'+(++id),position:{left:fr.x,top:fr.y,width:fr.w,height:fr.h},fill,line:{fill:'none',width:0},customPaths:[{width:fr.w,height:fr.h,commands}]});}
function cityMap(s,fr){shape(s,'rect',fr.x,fr.y,fr.w,fr.h,'#FAFBF9');polygons(s,parks,fr,true,p=>'#E2EADD');compound(s,spatial.buildings,fr,'#DCE0DE');compound(s,spatial.water,fr,'#C6DBE6');pathShape(s,gosi,fr,'#F5E8E1/70',C.red,2.4,true);tx(s,'N',fr.x+fr.w-35,fr.y+15,25,30,20,true);const sc=500*fr.w/(fr.x1-fr.x0);line(s,fr.x+23,fr.y+fr.h-25,fr.x+23+sc,fr.y+fr.h-25,C.ink,3);tx(s,'0',fr.x+21,fr.y+fr.h-52,28,25,16);tx(s,'500m',fr.x+sc-8,fr.y+fr.h-52,70,25,16);}

// 05 — history, original report diagrams with editable factual text.
{
const s=base(5,'1. 경주의 역사  /  HISTORY','왕경·읍성의 틀','역사적 중심의 이동과 현재 원도심의 가로조직','채미옥 발표자료 pp.11–12 · 국토지리정보원·V-World 공간 분석 · UNESCO 세계유산목록');
await im(s,AS+'/wanggyeong.png',54,255,367,480);await im(s,AS+'/eupseong.png',446,255,367,480);
tx(s,'월성',228,520,80,28,19,true);tx(s,'읍성',558,426,80,28,19,true);tx(s,'월성',630,544,80,28,19,true);
tx(s,'신라 왕경',54,752,367,38,27,true);tx(s,'월성 중심의 왕경과 방리체계',54,799,367,64,23,false,C.sub);
tx(s,'고려·조선 읍성',446,752,367,38,27,true);tx(s,'읍성 중심의 행정·생활권',446,799,367,64,23,false,C.sub);
rule(s,846,252,444);tx(s,'현재 가로조직',846,264,444,38,26,true);
tx(s,'57%',846,320,185,64,48,true,C.green);tx(s,'공통 방위의 가로 비율\n직접 잔존율과 구분',1033,327,257,82,21,false,C.sub);
tx(s,'약 150m',846,429,230,55,38,true,C.green);tx(s,'현재 가로의 격자 규모\n동서 147.5m · 남북 161.5m',846,490,444,61,22,false,C.sub);
rule(s,846,575,444);tx(s,'문화유산 구역·보존지역 69%',846,595,444,40,28,true);tx(s,'고시 구역 중심 반경 1km의 합집합 면적',846,642,444,34,20,false,C.sub);
tx(s,'경주에 포함된 세계유산 4건',846,714,444,38,25,true);tx(s,'1995  석굴암·불국사\n2000  경주역사유적지구\n2010  한국의 역사마을 · 양동\n2019  한국의 서원 · 옥산서원',846,764,444,147,23);
note(s,'출처: 채미옥, 천년 고도 경주의 골격구조 변화와 구경주역, PDF pp.11–12(도식 크롭). 현재 가로 분석: 국토지리정보원 연속수치지도, 2026-09 분석; 공통 방위 N0.8°E 57%는 여러 시기의 가로가 공유하는 방위로서 신라 도로의 직접 잔존율이 아니다. 약150m는 현재 가로 격자 측정(동서147.5,남북161.5m). 69%=68.8%, 고시구역 무게중심 반경1km 내 V-World 문화유산구역·역사문화환경보존지역 합집합. 세계유산: https://whc.unesco.org/en/list/736/ ; /976/ ; /1324/ ; /1498/ . 연속유산은 경주시 소재 구성요소 기준으로 4건.');
}
// 06
{
const s=base(6,'1. 경주의 역사  /  HISTORY','철도의 역사','사정동 개업, 성동동 이전, 철도 이설과 폐역','국토교통부·국가철도공단 · 김신재(2013) · 국토지리정보원 정사영상');
const events=[['1918.12.28','사정동 개업','최초 경주역'],['1936.12.01','현 위치 이전','성동동 · 표준궤'],['1939.06','노선 변경','읍성 북측 우회'],['2010.11.01','KTX 개통','신경주역 · 건천읍'],['2021.12.28','구 경주역 폐역','동해선 이설']];
rule(s,90,297,1164,C.line,2);events.forEach((a,i)=>{const x=54+i*250;dot(s,x+26,297,6,C.green);tx(s,a[0],x,245,230,34,25,true);tx(s,a[1],x,318,230,38,27,true);tx(s,a[2],x,365,230,30,22,false,C.sub);});
for(const [i,y]of[2015,2021,2025].entries()){const x=54+i*420;await im(s,AS+`/ortho_${y}_square.jpg`,x,445,396,396,'cover');tx(s,String(y),x,859,120,35,27,true);tx(s,['운영 중인 철도 부지','철도 이설 직전의 부지','폐역 이후의 부지'][i],x+115,865,281,32,22,false,C.sub);}
note(s,'1918.12.28: 최초 경주역은 사정동 개업, 현 성동동 역사와 구분. 1936.12.01 현 위치 이전(표준궤 전환); 1939.06 노선 변경: 김신재(2013) 경주철도와 도시공간, pp.387–388. 2010.11.01 신경주역 KTX 개통, 건천읍 소재. 2021.12.28 구 경주역 폐역: 국토교통부 2021.12.27 동해선 개통 보도 및 고시2021-1234. 마지막 열차는 12.27 23:16. 현 KTX 경주역의 명칭 변경은2023.12.28. 정사영상: 국토지리정보원,2015/2021/2025, 동일 F1 좌표 틀에서 동일 크롭.');
}
// 07
{
const s=base(7,'2. 사이트 분석 다이어그램·데이터  /  SITE DATA','대상지 개요와 데이터','구 경주역 폐역 부지 · 경주시 성동동 일원','경주시 고시 제2026-8호 · 경주시 구상(2025–2026) · 도시재생전략계획(2022) · 사용자 Rhino 실측');
await im(s,OLD+'/assets/photos/ph65_site_from_west_roof_wide.jpg',54,254,700,391,'cover');tx(s,'서측에서 본 폐역 부지',54,658,700,35,21,false,C.sub);
table(s,[['구분','면적'],['시 구상 · 1단계','79,438㎡'],['고시 구역','156,460㎡'],['계획 경계','217,876㎡']],794,254,496,[54,77,77,88],[222,274],25);
tx(s,'고시 면적과의 차이 61,416㎡',794,581,496,42,28,true,C.green);tx(s,'면적 차이이며 실제 외부 편입 면적과 구분',794,631,496,56,21,false,C.sub);
rule(s,54,722,1236);tag(s,'계획 경계',54,746);tx(s,'남북 944m × 동서 300m',54,789,383,48,30,true);tx(s,'Rhino 선택 폴리라인 기준',54,850,383,35,22,false,C.sub);
tag(s,'소유 자료',468,746);tx(s,'코레일 53.0% · 공단 46.9%',468,789,390,43,26,true);tx(s,'2021년 보고 · 148,770㎡ 범위\n기획재정부 0.1%',468,843,390,61,21,false,C.sub);
tag(s,'구 역사',890,746);tx(s,'경주문화관 1918',890,789,400,43,29,true);tx(s,'현 문화공간 활용\n코레일 철도기념물 지정(2013)',890,843,400,61,22,false,C.sub);
note(s,'계획217876㎡/300m×944m: 사용자 최신 Rhino 선택 폴리라인 수치, 현행 고시 범위와 구별. 고시제2026-8호 법정 면적156460㎡. 시 구상79438㎡는 경주시2025-12-18/2026-01-02 발표 범위로 세 범위를 동일 부지면적이라 부르지 않는다. 차61416=217876-156460,39.25%이며 공간 합집합/차집합을 계산한 편입면적이 아니다. 소유: 도시재생전략계획2022 인쇄p138/PDF148의2021년 주요업무 자료; 전체148770㎡,공단69790,코레일78864,기재부116. 최신 소유권 확인자료가 아니다. 구 역사는 국가등록문화유산이 아닌 코레일철도기념물. 사진: 사용자 현장 사진 ph65.');
}
// 08
{
const s=base(8,'2. 사이트 분석 다이어그램·데이터  /  SITE DATA','사이트 분석 다이어그램','폐선·접속점·유적점·북천의 관계','국토지리정보원·OSM·V-World · 김권일 발표자료(2026) · 기존 접속점 조사');
const fr=await siteMap(s,54,253,690,632,{anchors:true,her:true,gosiLine:true});
for(const b of spatial.bridge)pathShape(s,b,fr,C.blue,C.blue,2,true);const p=mapPos(fr,[219847.65,361060]);tx(s,'보행 육교',p[0]+14,p[1]-16,135,28,19,true,C.blue);
tx(s,'북천',568,312,100,30,23,true,C.blue);tx(s,'구 역사',242,797,150,30,21,true);
const x=793;tag(s,'현황 레이어',x,253);[['#A16B59','기존 조사 경계'],[C.ink,'고시 구역(도면 추출)'],[C.sub,'폐선·잔존 선로'],[C.blue,'도로 끝 접속점 37곳'],[C.purple,'문헌 기반 유적점']].forEach(([c,t],i)=>{shape(s,'rect',x,303+i*44,13,13,c);tx(s,t,x+29,296+i*44,468,32,23);});
rule(s,x,550,497);tag(s,'조사 질문',x,573);tx(s,'동서 횡단의 위치와 간격\n남북 보행축과 생활권의 연결\n유산 조사와 초기 이용의 순서',x,620,497,126,27);
tx(s,'접속점은 이전 조사 경계 기준\n유적점은 문헌 기반 근사 위치',x,804,497,69,21,false,C.sub);
rule(s,54,903,1236);tx(s,'S1 부지  ·  S2 원도심 1km  ·  S3 경주시',54,913,576,25,17,false,C.sub);tx(s,'T1 법령·고시  ·  T2 공공·통계  ·  T3 학술  ·  T4 언론·보조자료',640,913,650,25,16,false,C.sub);
note(s,'정사영상2025 F1 프레임: EPSG5187 x219180–220380,y360250–361350. 선로 OSM2026-09-21 보조자료. 도로끝37점: work/20261005_plan_massing/tables/anchors.csv,기존218478㎡ 조사경계 기준(서9/동18/남7/북3). 지도 갈색 조사경계는 기존측량도형이며 최신217876㎡ 경계를 새로 추적한 도형이 아니다. 검정고시경계는2026-8 지형도면지오리퍼런싱 결과(법정면적은156460㎡). 보행육교위치는 설명을 위한 근사표시, 정확한 위치·개방은 현장확인. 유적점은 김권일2026.02.27,성림2022,주소문헌 기반 일부근사. S1부지/S2원도심1km/S3시 전역. 자료등급은 본 발표의 추적용 분류이며 법정 증거등급이 아니다.');
}
// 09
{
const s=base(9,'3. 대지분석 MACRO  /  URBAN CONTEXT','입지: 도시의 접점','서측 상업가로, 동측 주거지, 남측 유적, 북측 생활권','국토지리정보원·V-World·OSM 공간 분석 · 거리 기준점: OSM 구 경주역');
const fr={x:54,y:254,w:658,h:658,x0:218319.2,x1:220979.2,y0:359266,y1:361926};cityMap(s,fr);const st=mapPos(fr,[219649.2,360746]);for(const rad of[500,1000]){const rr=rad*658/2660;shape(s,'ellipse',st[0]-rr,st[1]-rr,rr*2,rr*2,'none','#A9B3B0',1.1);}const places=[['성동시장',[219433.4,361028],-128,10],['경주읍성',[219321.4,361120],-130,-34],['대릉원',[219206.8,360006.9],-7,-38],['황리단길',[218968.3,360022],-155,14],['동궁과 월지',[220353,359768.9],-70,18],['첨성대',[219785.3,359725.5],-120,20]];for(const[n,p,dx,dy]of places){const a=mapPos(fr,p);line(s,st[0],st[1],a[0],a[1],C.sub,1.3);dot(s,a[0],a[1],5,C.blue);shape(s,'rect',a[0]+dx-4,a[1]+dy-1,150,29,'#FFFFFF/88');tx(s,n,a[0]+dx,a[1]+dy,160,30,21,true);}dot(s,st[0],st[1],6,C.ink);tx(s,'구 경주역',st[0]-124,st[1]-30,135,30,23,true);tx(s,'500m',st[0]+124,st[1]-14,78,27,18);tx(s,'1,000m',st[0]+230,st[1]-14,95,27,18);tx(s,'고시 구역과 주변 자산 · 반경 500m·1km',54,916,690,24,16,false,C.sub);
tag(s,'4방위 관계',764,254);tx(s,'북  북천 · 공원 · 성건 생활권\n서  성동시장 · 읍성 · 상업가로\n동  행복황촌 · 저층 주거지\n남  고분 · 대릉원 · 황리단길',764,299,526,162,27);
table(s,[['자산','직선거리'],['성동시장','355m'],['경주읍성','497m'],['대릉원','523m'],['동궁과 월지','920m'],['황리단길','994m']],764,505,526,[50,57,57,57,57,57],[325,201],24);
tx(s,'가까운 자산까지의 직선거리\n실제 보행 경로·소요시간과 구분',764,874,526,58,21,false,C.sub);
note(s,'주요자산직선거리는 OSM 구 경주역 점에서 각자산 가장가까운 점까지. 실제 역사건물중심으로 재측정한 m3b와 혼합하지 않음. 성동시장355,읍성497,대릉원523,동궁과월지920,황리단994m. 이미지 m3_site_distance: 거리링은67m/min 단순환산의 원형참고이며 통행망 기반등시간권이 아님. 지도 경계는기존218478㎡조사도형. 최신 계획면적217876㎡. 북측 관계는 북천/황성공원 및 북서측 성건동 생활권을 구분하며 신시가지 전체쇠퇴로 확장하지 않는다.');
}
// 10
{
const s=base(10,'3. 대지분석 MACRO  /  URBAN CONTEXT','동서 관계','문제 ①  폐선 노반의 횡단 공백과 동서 활력 차이','국토지리정보원 도로·철도 분석 · 소상공인365(2025.06–2026.06) · 현장 사진');
await siteMap(s,54,254,506,612,{anchors:true,her:false});tx(s,'기존 조사 경계 · 접속점',54,881,506,28,20,false,C.sub);
await im(s,OLD+'/assets/photos/ph00_west_wonhwaro_walk.jpg',601,254,331,221,'cover');await im(s,OLD+'/assets/photos/ph62_east_lane_paved.jpg',959,254,331,221,'cover');
tx(s,'서측  성동시장·상업가로',601,488,331,34,22,true);tx(s,'동측  행복황촌·저층 골목',959,488,331,34,22,true);
metric(s,'985m','도로 횡단이 없는 연속 구간',601,546,400,C.red);tx(s,'보행 육교 1개 · 폭 3.2m\n개방 여부는 현장 확인 필요',1016,562,274,76,22,false,C.sub);
chart(s,'ha당 일평균 유동인구 추정(명)', ['성동시장','행복황촌'],[1175,80],601,704,689,170,{points:[{idx:0,fill:C.blue},{idx:1,fill:'#B3C1B9'}],gap:60});
tx(s,'통신 기반 추정 · 구역 범위가 다르며 일부 중첩',601,895,689,29,19,false,C.sub);
note(s,'985m(984.4 반올림)=남쪽원효로와북쪽20m도로사이 차가 횡단할 도로가없는구간. 보행육교1개폭3.2m/길이216.3m 있으므로 보행횡단전무라고하지않음. 도로망우회율18단면중앙3.5는육교제외/인도횡단보도미반영으로 본문에서 생략. 성동시장200m반경1174.6,행복황촌활성화구역16.45ha80.3명/ha/일,소상공인3652025.06~2026.06 13개월평균. 통신사 휴대전화통화량기반 50m셀추정,실측보행자계수가 아님. 지역별범위다르고 일부구역중첩. 사진 ph00/ph62 사용자현장기록.');
}
// 11
{
const s=base(11,'3. 대지분석 MACRO  /  URBAN CONTEXT','남북 관계','문제 ②  남측 관광 자산과 북측 공원·생활권 사이의 연속성','국토지리정보원 수치지도 · UPIS 공원 · 소상공인365 · 원도심 미래구상 기획 연구(2025)');
const fr={x:54,y:254,w:534,h:640,x0:218250,x1:220750,y0:359400,y1:362396.25};cityMap(s,fr);shape(s,'rect',75,275,448,94,'#FFFFFF/93');tx(s,'북측  공원·생활권',91,281,440,38,27,true,C.green);tx(s,'황성공원 방면 · 성건동',91,327,440,32,22);const st=mapPos(fr,[219649.2,360746]);dot(s,st[0],st[1],6,C.red);shape(s,'rect',st[0]-70,st[1]-40,215,33,'#FFFFFF/92');tx(s,'구 경주역 부지',st[0]-66,st[1]-37,235,36,25,true,C.red);shape(s,'rect',75,745,448,86,'#FFFFFF/93');tx(s,'남측  관광·유적',91,752,440,38,27,true,C.blue);tx(s,'대릉원 · 황리단길 · 월성',91,798,440,35,22);tx(s,'북천',456,478,90,28,22,true,C.blue);
// Schematic connection axis, not a proposed road alignment.
line(s,619,296,619,839,C.green,3);[305,552,806].forEach(y=>dot(s,619,y,8,C.green));
tag(s,'북측',674,264);tx(s,'공원과 생활권',674,305,616,49,34,true);tx(s,'일상 산책 · 운동 · 주민 문화활동',674,366,616,46,25,false,C.sub);
tag(s,'중앙',674,493);tx(s,'폐역 부지와 폐선축',674,535,616,49,34,true);tx(s,'관광 동선과 주민 이동의 접점',674,596,616,46,25,false,C.sub);
tag(s,'남측',674,724);tx(s,'관광·유적 자산의 집중',674,766,616,49,34,true);tx(s,'황리단길 757명/ha·일\n주말 유동은 평일의 1.72배',674,827,616,66,25,false,C.sub);
note(s,'정사영상F2는2025 국토지리정보원 원본. 사진내텍스트와 오른쪽축은 관계를 설명하는 도식이며 길선형·정확위치·거리측정용이 아님. 남측관광집중은 대릉원황리단월성 문화유산위치 및 소상공인365밀도/주말집중으로 설명. 황리단길300m반경:757.0명/ha/일,2025.06~2026.06평균,주말평일비1.72. 북측은공원과북천/북서측성건생활권으로구체화. 관광분산은현재확인결과가아닌향후계획목표.');
}
// 12 — four actual geospatial layers, native editable paths.
{
const s=base(12,'4. 대지분석 MICRO  /  SITE CONDITIONS','규제와 유산','문제 ③  용도·높이·매장유산·지구단위계획의 중첩','경주시 고시 제2026-8호 · V-World · 경북고시 제2020-479호 · 김권일 발표자료 p.22');
const labs=['용도지역','고도지구','문화유산','지구단위계획'];
const desc=['자연녹지 중심\n일부 주거·상업지역','높이 제한 15m·20m\n해당 구역별 검토','시굴 대상 145,879㎡\n2022 지표조사 범위','공공·문화·상업·공원\n고시 시설별 기준'];
for(let i=0;i<4;i++){const x=54+i*315;tx(s,labs[i],x,254,290,38,27,true);const fr={x,y:315,w:290,h:382,x0:219290,x1:220190,y0:360340,y1:361540};shape(s,'rect',x,315,290,382,'#F5F6F4');if(i===0)polygons(s,zone,fr,true,p=>p.uname.includes('녹지')?'#DCE5D3/85':p.uname.includes('상업')?'#D9B6BE/85':p.uname.includes('주거')?'#E7D79B/85':'#E9EBE8/85');if(i===1)polygons(s,height,fr,false,p=>p.h_cls==='15m'?'#CCB8BA/85':p.h_cls==='20m'?'#D5DFE8/85':'#E7E7E7/85');if(i===2){polygons(s,herArea,fr,true,p=>p.uname.includes('보존')?'#D8D2E0/65':'#A69AB5/70');const si=await read(OLD+'/research/data_series/siguel_digitized_5187.geojson');polygons(s,si,fr,false,p=>'#7B8C78/65');}if(i===3)polygons(s,blocks,fr,false,p=>({commercial:'#D9B6BE',culture:'#C5CEDA',civic:'#C5CEDA',park:'#D9E5D1',parking:'#E5E5E0'}[p.cls]||'#CBD5C6')+'/85');pathShape(s,gosi,fr,'none',C.ink,1.5,true);const legends=[[['#DCE5D3','녹지'],['#E7D79B','주거'],['#D9B6BE','상업']],[['#D5DFE8','20m'],['#CCB8BA','15m']],[['#D8D2E0','보존'],['#7B8C78','시굴']],[['#D9B6BE','상업'],['#C5CEDA','공공·문화'],['#D9E5D1','공원'],['#E5E5E0','주차']]][i];legends.forEach(([c,t],j)=>{const xx=x+(i===3?[0,64,166,232][j]:j*86);shape(s,'rect',xx,712,10,10,c);tx(s,t,xx+16,707,i===3?84:76,27,i===3?16:17,false,C.sub);});tx(s,desc[i],x,751,290,69,23,false,C.sub);}
rule(s,54,833,1236);tx(s,'1단계 원칙  |  매장유산 조사 전 지하 개발 제외',54,855,1236,47,32,true,C.green);tx(s,'법률상 일률적 지하 금지와 구분 · 시굴 결과와 협의에 따른 단계별 이용',54,909,1236,30,21,false,C.sub);
note(s,'용도 V-World UQ111;높이 V-WorldUQ123와경북2020-479. 검정윤곽은2026-8고시도면추출(지오리퍼런싱근사). 이전계획경계비율77.5%등은 최신217876㎡ 경계미재계산으로본문에쓰지않음. 시굴145879㎡는2022지표조사전체148770㎡ 범위중수치,고시면적156460㎡에나눈93%로쓰지않음. 시굴도형은김권일p22 그림판독근사. 매장유산조사전지하개발제외는 본계획의1단계설계원칙이며법률상일률적금지가아님. 지하영향없는임시이용도시굴·영향판단과관계기관협의조건이있음(PDFp8). 관련법령은소규모성토조건과매장유산영향예외를포함하므로단순공원허용으로단정하지않음.');
}
// 13
{
const s=base(13,'4. 대지분석 MICRO  /  SITE CONDITIONS','접속 조건과 도시조직','도로 끝 접속점과 동서의 서로 다른 가로·건물 규모','국토지리정보원 · 접속점 조사 · 도시조직 분석(2026.09) · 현장 사진');
await siteMap(s,54,254,494,610,{anchors:true,old:true,rail:false});tx(s,'접속점 37곳  서 9 · 동 18 · 남 7 · 북 3',54,885,494,37,22,true);
await im(s,OLD+'/assets/photos/ph03_west_wonhwaro_bus.jpg',592,254,333,236,'cover');await im(s,OLD+'/assets/photos/ph62_east_lane_paved.jpg',957,254,333,236,'cover');tx(s,'서측  상업가로',592,508,333,37,27,true);tx(s,'동측  저층 골목',957,508,333,37,27,true);
table(s,[['비교 항목','서측','동측'],['1층 건물 비율','69.4%','93.3%'],['교차점 간격','39.1m','31.1m'],['필지 면적 중앙값','70㎡','155㎡']],592,575,698,[50,72,72,72],[302,198,198],24);
tx(s,'부지 경계 인접 0–150m 조사 범위\n기존 가로의 위치·폭에 따른 접속 방식 검토',592,870,698,63,22,false,C.sub);
note(s,'접속점37곳: 기존218478㎡경계6m이내 접촉·관통/직교에가까운 도로를분류(서9동18남7북3). 최신217876㎡선택경계수치와 별도로기존조사기준표시. 도시조직: archive/90_derived/edge_scale_profile_20260928.csv,경계로부터서·동0–150m;1층비율서69.4/동93.3,교차점간격39.1/31.1,필지중앙값70/155㎡. 좌측지도는기존조사윤곽과접속점(최신경계의정밀추적도아님). 사진사용자ph03/ph62.');
}
// 14
{
const s=base(14,'5. 사회적 문제  /  SOCIAL CONTEXT','원도심 쇠퇴와 그 요인','문제 ④  인구 감소·고령화와 중심 기능의 약화','행정안전부·KOSIS 주민등록인구 · 경주시 도시재생전략계획(2022) pp.15–16');
chart(s,'2015–2025 인구 감소율(%)',['황오동','황남동','성건동','월성동','경주시'],[32.7,44.8,29.0,22.3,6.1],54,255,674,369,{fmt:'0.0',color:C.blue,points:[{idx:4,fill:'#CBD1D2'}],gap:60});
table(s,[['지역','2015 → 2025 인구','65+ (26.08)'],['황오동','14,359 → 9,662명','43.8%'],['황남동','6,561 → 3,621명','50.1%'],['성건동','17,320 → 12,300명','36.7%'],['월성동','6,753 → 5,245명','39.0%']],54,647,674,[50,51,51,51,51],[141,344,189],22);
tag(s,'병렬 요인',790,264);const r=[['도시 외연 확장','신규 생활권과 다핵 구조'],['행정·상업 중심의 이동','시청 이전과 기존 중심권 약화'],['보존 규제와 주거 환경','개발 제약과 생활 기반 과제']];r.forEach((a,i)=>{const y=315+i*173;tx(s,a[0],790,y,500,43,30,true);tx(s,a[1],790,y+53,500,54,25,false,C.sub);rule(s,790,y+132,500);});
tx(s,'원도심 쇠퇴는 2021년 폐역 이전부터 진행\n폐역 부지는 연결과 기능 재편의 대상',790,850,500,76,24,true,C.green);
note(s,'2015·2025 연말주민등록인구:KOSIS DT_1B04005N. 황오동은현재행정경계와일치시키기위해옛중부동합산. 65세이상비율은2026-08(황오43.8,황남50.1,성건36.7,월성39.0,경주시30.0)로인구변화와기준시점다름. 감소율2015→2025:4동32.7/44.8/29.0/22.3,시6.1%. 병렬요인경주시도시재생전략계획2022pp15–16,주거환경및보존규제는복합과제이지규제단독인과추정아님. 2021폐역이원도심쇠퇴의유일원인이라는인과주장은사용하지않음.');
}
// 15
{
const s=base(15,'5. 사회적 문제  /  SOCIAL CONTEXT','청년 유출과 고용','문제 ④  20–24세에 집중된 순유출과 일자리·교육의 과제','KOSIS 국내인구이동통계 DT_1B26002 · DT_1B26B21');
metric(s,'−7,249명','2020–2025 경주시 20–34세 누적 순이동',54,254,688,C.blue);chart(s,'연령별 순유출 규모(명)',['20–24세','25–29세','30–34세'],[4543,2320,386],54,430,688,375,{color:C.blue,gap:60});tx(s,'20–24세가 순유출의 62.7%',54,856,688,49,30,true,C.blue);
rule(s,800,254,490);tag(s,'2025 이동 사유',800,279);tx(s,'직업  −283명',800,334,490,62,40,true);tx(s,'교육  −625명',800,417,490,62,40,true);tx(s,'전 연령의 경주시 순이동\n청년층만의 이동 사유와 구분',800,512,490,77,25,false,C.sub);
rule(s,800,637,490);tag(s,'계획 검토 항목',800,662);tx(s,'청년 고용의 지속성\n창작·문화 활동과 소득의 연계\n주거비와 생활 편의',800,716,490,137,29);tx(s,'원도심 단위의 청년 고용 자료는\n추가 기준값 확보 필요',800,875,490,60,21,false,C.sub);
note(s,'경주시전역2020~2025:20–24−4543,25–29−2320,30–34−386,합−7249. 20–34 5세구간합이며KOSIS 별도19–34청년계−7505와다름. 4543/7249=62.67%. KOSISDT_1B26002. 2025이동사유 KOSISDT_1B26B21은전연령:직업−283,교육−625,주거환경−183,기타−34,가족+635,주택+1027,자연환경+323,총+860. 이값을청년만의직업교육순유출이라고하지않음. 고용과교육은계획과제이며도시재생으로교육유출전체가해소된다고예측하지않음.');
}
// 16
{
const s=base(16,'5. 사회적 문제  /  SOCIAL CONTEXT','방문과 체류','문제 ⑤  원도심 현장 체류와 도시 전체 관광 체류의 차이','황오동 모니터링 결과보고서(2024) · 경주시 제5차 관광실태조사(2024–2025)');
tag(s,'황오동 현장 설문',54,254);metric(s,'79.1%','1–3시간 체류 · 응답 187명',54,301,685,C.blue);
chart(s,'황오동 현장 체류시간 분포(%)',['1–3시간','3–6시간','6–9시간','24시간 이상'],[79.1,15.0,3.2,2.7],54,483,685,310,{color:C.blue,fmt:'0.0',gap:70});tx(s,'전체 표본의 약 70%는 경주시민\n축제·현장 표본으로 경주시 전체 방문객과 구분',54,851,685,70,23,false,C.sub);
rule(s,800,254,490);tag(s,'경주시 전체 관광조사',800,279);metric(s,'55.3%','숙박 방문 · 당일 방문 44.7%',800,327,490,C.green);tx(s,'평균 1.8일\n6개 관광지 · 내국인 3,009명',800,485,490,86,31,true);
rule(s,800,626,490);metric(s,'76.9%','내국인 방문객의 자가용 이용',800,657,490,C.green);tx(s,'도착 지점의 보행 전환과\n원도심 체류 동선 검토',800,848,490,74,25,false,C.sub);
note(s,'황오동2024현장설문전체n188,체류문항n187. 원문범주1–3h148(79.14%),3–6h28(14.97%),6–9h6(3.21%),24h이상5(2.67%). 나머지범주0. 약70%경주시민/방문목적축제50%,원도심현장표본으로전체관광객대표성제한. 경주시제5차관광실태조사2024.08~2025.05,내국인3009명6개조사지점:숙박55.3,당일44.7,평균1.8일,자가용76.9%. 전체관광체류가전국보다짧다는주장하지않음. 공식보고서 https://www.gyeongju.go.kr/ebookData/20260107/index.html 인쇄pp22/24/25.');
}
// 17
{
const s=base(17,'5. 사회적 문제  /  SOCIAL CONTEXT','정주 기능 공백과 치환 위험','문제 ⑥  생활·야간 기능과 관광·체류 업종의 균형','경주시 고시 제2026-8호 · 소상공인365(2025.06–2026.06, 야간은 2026.06)');
tag(s,'고시 토지이용',54,254);metric(s,'주거용지 0','별도 주거용지 배분 없음',54,300,575,C.red);tx(s,'문화시설의 허용 건축물은 별도 검토\n주택 건축이 전면 금지된다는 의미와 구분',54,462,575,74,24,false,C.sub);
chart(s,'23–05시 유동 비중(%)',['폐역 구역','행복황촌','성동시장','황리단길'],[3.7,4.4,5.0,5.5],54,604,575,260,{color:C.blue,fmt:'0.0',gap:65});tx(s,'7개 분석구역 범위 3.7–5.5%',54,896,575,34,23,false,C.sub);
rule(s,722,254,568);tag(s,'행복황촌 · 표본 11업종',722,279);tx(s,'2025.06 → 2026.06 업소 수 변화',722,328,568,37,24,false,C.sub);
table(s,[['업종군','변화','2026.06'],['관광·체류','+7개','29개'],['생활','0개','15개']],722,408,568,[57,104,104],[254,139,175],27);
tx(s,'관광·체류 기능의 증가',722,732,568,46,33,true,C.green);tx(s,'생활 기능과 주거 수요의 병행 확보\n임대료·생활업종·주민 이용의 추적',722,795,568,88,28);
note(s,'고시2026-8결정도상별도주거용지0. 문화1(9770㎡)은제2종일반주거지역허용건축물가능하므로아파트/주택전면불가로단정하지않음. 야간23~05비중2026.06:폐역3.7황촌4.4황오4.9시장5.0황리단5.5구역+3004.9중심3004.8;시청6.1은이7구역범위에제외. 겹치는분석구역합산불가. 황촌소상공인365표본11업종:생활=슈퍼편의점미용정육반찬약국백반,관광체류=카페여관호텔펜션.2025.06→2026.06관광체류+7/생활0,2026.06재고29/15. 전체업종전수라고하지않음. 실제주민/업종치환인과가확인된결론이아니라향후관리위험.');
}
// 18
{
const s=base(18,'6. 문제 종합  /  SYNTHESIS','문제 종합','공간 연결, 문화·유산, 생활·정주의 여섯 과제','앞선 현황·규제·사회 지표 종합 · 지표별 조사 범위는 해당 슬라이드 참조');
const cells=[['①','동서 단절','985m','도로 횡단 공백\n성동시장–행복황촌 활력 차이',C.red],['②','남북 불균형','남측 집중','관광·유적과 북측 공원·생활권\n사이의 보행 연속성',C.green],['③','규제와 매장유산','4개 레이어','용도·높이·유산·결정도\n조사에 따른 단계별 이용',C.purple],['④','쇠퇴와 청년 유출','−7,249명','인구 감소·고령화\n경주시 20–34세 누적 순유출',C.blue],['⑤','원도심 현장 체류','79.1%','황오동 현장 설문의 1–3시간 체류\n전체 도시 관광과 구분',C.blue],['⑥','정주 기능과 치환 위험','생활업종 순증 0개','주거·야간 기능 공백\n황촌 업소 변화 · 표본 11업종',C.green]];
cells.forEach((a,i)=>{const col=i%3,row=Math.floor(i/3),x=54+col*420,y=266+row*329;rule(s,x,y,392);tx(s,a[0],x,y+24,53,40,28,true,a[4]);tx(s,a[1],x+60,y+24,332,44,29,true);tx(s,a[2],x,y+100,392,66,i===5?35:44,true,a[4]);tx(s,a[3],x,y+186,392,90,24,false,C.sub);});
note(s,'①도로무횡단985m(보행육교존재),시장황촌추정밀도차.②자산위치와유동의남측집중/공원생활권연계계획과제.③4개규제층및시굴145879㎡,1단계지하개발제외는본계획원칙.④−7249는경주시전역2020–2025 20–34세합(부지내수치아님).⑤79.1%는황오동2024현장n187 1–3h,전체시관광표본아님.⑥생활+0은황촌2025.06→2026.06표본11업종중생활군업소변화,치환인과입증이아님. 문제번호는사용자가지정한목차체계유지.');
}
// 19
{
const s=base(19,'6. 문제 종합  /  SYNTHESIS','계획 목표와 성과지표','연결, 문화·유적과 체류, 주민 생활과 청년 정주','앞선 기준값 · 성과지표와 관광–정주 연계는 본 계획의 검증 항목');
table(s,[['목표','현재 기준값','확인 지표'],['1  연결\nCONNECT','도로 횡단 공백 985m\n접속점 37곳(기존 조사)','횡단 지점 수·간격\n동서 우회거리·남북 보행 연속성'],['2  문화·유적과 체류\nEXCHANGE','황오동 1–3시간 체류 79.1%\n남측 관광 자산의 집중','동일 표본의 체류시간 분포\n북측·주변 지역 방문 분담률'],['3  주민 생활과 청년 정주\nSPREAD','야간 유동 3.7–5.5%\n황촌 생활업종 순증 0개','상시 거주·청년 고용의 유지\n주민 문화 이용·생활업종·지역 소득']],54,254,1236,[62,125,125,125],[324,405,507],24);
tx(s,'관광–정주 연계의 성립 조건',54,730,1236,42,30,true,C.green);
const cond=['지역 소득의 잔류','일자리의 질','주거·관광 수요의\n비경합','관광 구역·생활권의\n분리·완충','관광 규모 관리'];cond.forEach((t,i)=>{const x=54+i*250;rule(s,x,792,236);tx(s,String(i+1).padStart(2,'0'),x,808,40,31,19,true,C.green);tx(s,t,x,852,236,64,23,true);});
tx(s,'관광 성장과 정주 인구 증가의 연계는 직접 검증되지 않은 계획 가설',54,917,1236,25,19,false,C.sub);
note(s,'계획의방향:단절되어온경주를다시연결하고문화유적강점을활용하며주민편의와문화생활·청년정주를확대하는지속가능도시재생. 타이틀NEXUS1918/컨셉CULTURALINTERCHANGE. CONNECT도시관광네트워크연결,EXCHANGE관광일상문화창작교차,SPREAD성동시장원도심확산. 기준값은동일정의·시점·범위로재측정. 주민거주·청년고용·주민문화이용·지역소득·북측방문분담은현재부지기준값미확보이므로착수전측정필요;임의수치목표설정없음. 관광성장→정주증가를직접검증한연구확인없음. 5조건을설계·운영조건으로둔검증가설이며인과적으로확인된성과예측이아님.');
}

for(const s of pres.slides.items){s.speakerNotes.text+='\n근거 대조: work/20261010_direction_brief/20261010_final_direction_evidence_v1.md(2026-10-10) 및 해당 research/A1·A2·B2. 시점이 다른 인구·고령화 수치는 원자료의 시점을 유지. 기존 경계·규제비율은 최신 사용자 경계값보다 우선하지 않음.';}
pres.slides.items[2].speakerNotes.text+='\n79,438㎡는 혁신지구 1단계 토지이용계획표 및 소유현황표의 합계(102필지), 김권일 발표자료 PDF pp.11·23.';
pres.slides.items[3].speakerNotes.text='출처: 국토지리정보원2025정사영상·연속수치지도,OSM2026-09-21 폐선,김권일2026.02.27/성림2022 유적점. 접속점37곳은기존218478㎡조사경계6m이내의접촉·관통가로(서9동18남7북3). 갈색은기존조사윤곽,최신217876㎡계획경계는사용자Rhino실측값으로구분. 검정은2026-8고시도면추출. 육교는NGII N3A_A0063321 실제 도형을EPSG5179→5187변환,중심약219756/361064;개방여부미확인. 유적점은문헌주소기반일부근사. 정사영상표시프레임x219180–220380,y360450–361550. S1부지/S2원도심반경1km/S3시전역. T1법령·고시/T2공공·통계/T3학술/T4언론·보조. 근거정리20261010_final_direction_evidence_v1.md §3 U01·U02.';
pres.slides.items[4].speakerNotes.text='출처:NGII연속수치지도건물·하천,UPIS공원,2026-8고시지오리퍼런싱,OSM구경주역점219649.2/360746. 지도는편집가능벡터,반경500/1000m. 자산표시점은공공관광지점/지명,거리표는그자산의가장가까운경계까지직선거리. 실제보행거리나소요시간과구분. 성동시장355,읍성497,대릉원523,동궁과월지920,황리단994m. 역사건물중심을사용한m3b와혼합하지않음. 북측은북천·황성공원방면과북서측성건생활권. 근거정리20261010_final_direction_evidence_v1.md §3 U18.';
pres.slides.items[6].speakerNotes.text='출처:NGII수치지도건물·하천,UPIS공원,2026-8고시지오리퍼런싱. 편집가능벡터도시맥락지도;북측설명은황성공원방면·성건생활권방향. 남측관광집중은자산배치와소상공인365밀도로설명. 황리단길반경300m의2025.06–2026.06추정일평균757.0명/ha,2026.06주말/평일1.72. 유동은통신기반추정. 관광분산은향후계획목표이며확인된기존성과가아님. 근거정리20261010_final_direction_evidence_v1.md §3 U06·U07.';
await fs.mkdir(BUILD+'/renders',{recursive:true});await fs.mkdir(BASE+'/output',{recursive:true});
for(const [i,s]of pres.slides.items.entries()){const stem=String(i+5).padStart(2,'0');await fs.writeFile(BUILD+'/renders/'+stem+'.png',new Uint8Array(await (await pres.export({slide:s,format:'png',scale:1})).arrayBuffer()));await fs.writeFile(BUILD+'/renders/'+stem+'.layout.json',await (await s.export({format:'layout'})).text());console.log('rendered',stem);}
await fs.writeFile(BUILD+'/presentation.json',JSON.stringify(pres.toProto()));
const candidatePath=BUILD+'/draft.pptx';await (await PresentationFile.exportPptx(pres)).save(candidatePath);
const stagedPath=BUILD+'/draft_with_chart_data_delivery.pptx';
execFileSync(RUNTIME+'/python/python.exe',[SKILL+'/container_tools/materialize_literal_chart_workbooks.py',candidatePath,stagedPath,'--workspace',ROOT,'--receipt',BUILD+'/chart_workbook_snapshot_delivery.json'],{encoding:'utf8',stdio:'pipe'});
const finalPath=BASE+'/output/NEXUS_1918_05-19_complete.pptx';
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:stagedPath,finalPath,explicitTotalSlideCount:15,requiredNativeChartOwnerSlides:[6,10,11,12,13],requiredEmbeddedWorkbookChartOwnerSlides:[6,10,11,12,13],requiredNativeTableOwnerSlides:[3,5,9,10,13,15],materializeLiteralChartWorkbooks:true,nativeChartTargetApplication:'powerpoint',fontPolicy:{basis:'user_request',families:[FONT]},pythonExecutable:RUNTIME+'/python/python.exe',integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12801600,9601200','--validate-bullet-geometry','--validate-heading-fit',...[3,5,9,10,13,15].flatMap(n=>['--require-native-table-slide',String(n)])],verifyArtifactToolImport:true,receiptPath:BUILD+'/validation_complete.json'});
console.log(JSON.stringify(result));
