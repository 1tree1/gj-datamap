import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {pathToFileURL} from 'node:url';
const B='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const {applyPresentationChartFont}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
const R=JSON.parse(await fs.readFile(B+'/rhythm_evidence.json','utf8'));
const T=JSON.parse(await fs.readFile(B+'/traffic_revision6_evidence.json','utf8'));
const G=JSON.parse(await fs.readFile(B+'/traffic_revision6_geometry.json','utf8'))[0];
const p=Presentation.create({slideSize:{width:12191695/9525,height:720}});p.theme.defaultFont='Pretendard';
const C={ink:'#20272E',sub:'#606D77',blue:'#235D82',light:'#EAF1F5',line:'#CBD4DC',gray:'#B9C3CB',orange:'#B66A2B'};let id=0;
function sh(s,g,x,y,w,h,fill='none',stroke='none',lw=0){return s.shapes.add({geometry:g,name:'r6-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:lw}});}
function t(s,v,x,y,w,h,z=20,c=C.ink,a='left'){const q=sh(s,'textbox',x,y,w,h);q.text=String(v);q.text.style={fontSize:z,typeface:'Pretendard',color:c,bold:false,alignment:a,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};return q;}
function ln(s,x,y,w,c=C.line,lw=.8){sh(s,'rect',x,y,w,lw,c);}
function conn(s,a,b,c=C.sub){s.shapes.add({geometry:'connector',kind:'straight',name:'r6-leader-'+(++id),position:{left:Math.min(a[0],b[0]),top:Math.min(a[1],b[1]),width:Math.max(.01,Math.abs(b[0]-a[0])),height:Math.max(.01,Math.abs(b[1]-a[1])),horizontalFlip:b[0]<a[0],verticalFlip:b[1]<a[1]},line:{style:'solid',fill:c,width:.8}});}
async function im(s,file,x,y,w,h,alt){s.images.add({blob:new Uint8Array(await fs.readFile(file)),contentType:'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});}
function base(sec,title,sub,num,insight,source,notes){let s=p.slides.add();s.background.fill='#FFFFFF';ln(s,0,0,1280,C.blue,2);t(s,'현황과 분석  /  '+sec,48,24,1176,26,16,C.blue);t(s,title,48,60,1184,47,30);t(s,sub,48,115,1184,31,18,C.sub);ln(s,48,594,1184);t(s,'해석',48,610,55,27,14,C.sub);t(s,insight,119,603,1109,50,19);t(s,source,48,664,1126,40,12.5,C.sub);t(s,num,1185,675,47,28,17,C.sub,'right');s.speakerNotes.text=notes;return s;}
{
const s=base('공간의 경험','가시면적과 리듬','같은 반경 150m에서 한 지점의 시야와 걸을 때 달라지는 시야를 함께 비교한다',13,'격자에서는 넓은 시야가 이어지고 골목에서는 좁아짐과 확장이 반복된다.\n동측 경계의 시야가 열리는 지점을 보행 접속 후보로 검토한다.','국토지리정보원 건물·담장·도로중심선 · 반경 150m, 광선 720개, 경로 표본 2m 간격 · 자체 계산 2026.09.28\n구경주역 데이터맵 통계 리포트 ‘걷기 가시 면적 리듬’ · 가시 영역은 보행 가능 영역과 구분',JSON.stringify({...R,routes:R.routes.map(({distance_m,area_m2,peak_indices,...a})=>({...a,samples:distance_m.length}))},null,2)+'\n두 지도는 동일한 320x310m 창의 대표 지점이며 경로 전체 평균과는 다름. 원 경로 수치계산을 재실행해 공개 웹페이지의 평균/중앙값/CV/봉우리간격/경로길이 모두 일치함을 대조. 시야변동이 거리활력이나 보행가능성을 직접 나타내지는 않음. 경계 개방지점의 실제 접속 가능성은 담장/소유/단차의 현장 확인 대상.');
t(s,'한 지점에서 보이는 면적',48,170,540,30,22);
for(const [x,lab,file,val,cap]of [[48,'원도심 격자','isovist_0','13,901㎡','십자 가로를 따라 열린 시야'],[334,'황오동 골목','isovist_2','1,448㎡','건물·담장 사이의 좁은 시야']]){
 t(s,lab,x,212,255,31,20);await im(s,B+'/assets/'+file+'.png',x,252,255,247,lab+' 가시면적 비교, 같은 축척');t(s,val,x,507,255,42,31,C.blue);t(s,cap,x,555,255,26,16,C.sub);
}
sh(s,'rect',619,174,.8,404,C.line);
t(s,'걸으며 달라지는 가시면적',649,170,578,30,22);t(s,'세 그래프는 같은 가로·세로축 · 점 = 시야가 열리는 지점',649,204,578,25,14,C.sub);
const short=['화랑로','황오동 골목','부지 동쪽 가장자리'];
for(let i=0;i<3;i++){
 let r=R.routes[i],y=238+i*115,col=i===2?C.orange:C.blue;
 t(s,short[i],649,y,270,26,18,col);t(s,`열림 간격 중앙값 ${r.peak_gap_median_m}m · 변동계수 ${r.cv.toFixed(2)}`,934,y,294,26,14,C.sub,'right');
 const ch=s.charts.add('scatter',{position:{left:642,top:y+27,width:582,height:84},series:[{name:short[i]+' 가시면적',xValues:r.distance_m.map(v=>Number(v.toFixed(2))),values:r.area_m2.map(v=>Number((v/1000).toFixed(4))),line:{fill:col,width:1.8},marker:{symbol:'none'}},{name:'시야가 열리는 지점',xValues:r.peak_indices.map(k=>Number(r.distance_m[k].toFixed(2))),values:r.peak_indices.map(k=>Number((r.area_m2[k]/1000).toFixed(4))),line:{fill:'none',width:0},marker:{symbol:'circle',size:3,fill:col}}],scatterOptions:{style:'line'},hasLegend:false,xAxis:{visible:true,min:0,max:1000,majorUnit:200,tickLabelPosition:'low',numberFormatCode:'0',textStyle:{fontSize:11.5,fill:C.sub,typeface:'Pretendard'},line:{fill:C.line,width:.5},majorGridlines:null},yAxis:{visible:true,min:0,max:25,majorUnit:10,numberFormatCode:'0',textStyle:{fontSize:11.5,fill:C.sub,typeface:'Pretendard'},line:{fill:'none',width:0},majorGridlines:{fill:'#E3E7EB',width:.5}},dataLabels:{showValue:false},chartFill:'none',chartLine:{fill:'none',width:0},plotAreaFill:'none',plotAreaLine:{fill:'none',width:0}});applyPresentationChartFont(ch,{fontFamily:'Pretendard'});
}
t(s,'가시면적 (천㎡)',650,576,210,16,11.5,C.sub);t(s,'걸은 거리 (m)',1056,576,170,16,11.5,C.sub,'right');
}
{
const s=base('권역별 교통 소통','정체는 관광·행정 거점과 부지 서측 가로에 함께 나타난다','ITS 시간대별 평균 주행속도 · 주말 표본 7일 · 아래 지도는 13시 평균 소통 상태',14,'관광·행정 거점의 접근 교통을 처리하고, 부지 양측을 보행으로 연결해 이용을 분산한다.\n평균 주행속도만으로 서측 원도심의 활동량이나 한산함을 판단할 수는 없다.','국가교통정보센터 ITS · 주말 표본 2025.01.11–07.12 중 7일 · 지도 범위 내 관측 도로구간 554개, 방향별 집계\n구경주역 데이터맵 이력 자료 재집계 · 정체 기준: 도시부 15 / 도시고속 30 / 고속 40km/h 미만 · 교통량 자료 아님',JSON.stringify(T,null,2)+'\n사용자는 서측 범위를 부지 바로 서측 원도심으로 확인. 그러나 해당 구간에도 정체가 있고 동측 근접구간은 상대적으로 원활하므로 동측활발/서측조용이라고 서술하지 않음. 정체는 차량통행량·상권활력의 대리지표가 아님. 지도는 원자료를 재투영하여 13시 데이터를 색상으로 재작성. 시간대별 집계는 지도영역과 교차하는 링크에서 계산했으며 각방향별링크를 각1개로 센다. 사진 스크린샷의 표시창과 본 지도영역이 달라 전체링크수와정체링크수는 다름. 임계값은 데이터맵에서 사용한 분류이며 법정고시기준으로 단정하지 않음.');
const f={x:137,y:167,w:591,h:414};await im(s,B+'/assets/traffic_weekend13.png',f.x,f.y,f.w,f.h,'ITS 주말13시 평균속도 실제 지도');
const pos=xy=>[f.x+(xy[0]-G.bounds[0])/(G.bounds[2]-G.bounds[0])*f.w,f.y+f.h-(xy[1]-G.bounds[1])/(G.bounds[3]-G.bounds[1])*f.h];
function label(k,txt,x,y,w,anchor){const pt=pos(G.centers[k]);t(s,txt,x,y,w,27,17,k==='site'?C.blue:C.ink);conn(s,anchor,pt,C.sub);sh(s,'ellipse',pt[0]-2.5,pt[1]-2.5,5,5,k==='site'?C.blue:C.ink);}
label('north','시청 주변',602,179,172,[600,196]);label('west','부지 서측 원도심',48,318,163,[200,336]);label('east','부지 동측 황오·황촌',584,436,235,[579,449]);label('south','황리단길 주변',48,511,170,[208,524]);label('site','구경주역 부지',586,351,186,[583,365]);
t(s,'N',766,178,21,24,15,C.sub,'center');conn(s,[776,220],[776,207],C.sub);sh(s,'triangle',772,199,8,10,C.sub);
for(const [j,txt,c]of [[0,'정체',C.orange],[1,'서행','#D8AA82'],[2,'원활','#B8C2CA']]){ln(s,263+j*138,567,26,c,3);t(s,txt,299+j*138,554,90,26,14,C.sub);}
sh(s,'rect',820,177,.8,399,C.line);
t(s,'같은 범위의 정체 도로구간',857,174,372,33,21);t(s,'관측 554개 중 · 차량 대수가 아닌 구간 수',857,211,372,27,14.5,C.sub);
let c=s.charts.add('bar',{position:{left:857,top:252,width:361,height:168},categories:T.hours.map(x=>String(x.hour).padStart(2,'0')+'시'),series:[{name:'정체 도로구간 수',values:T.hours.map(x=>x.congested_links),fill:C.gray,points:[{idx:1,fill:C.orange}]}],barOptions:{direction:'column',gapWidth:100},hasLegend:false,xAxis:{visible:true,textStyle:{fontSize:17,fill:C.ink,typeface:'Pretendard'},line:{fill:C.line,width:.8}},yAxis:{visible:false,min:0,max:120,line:{fill:'none',width:0},majorGridlines:null},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0"개"',textStyle:{fontSize:19,fill:C.ink,typeface:'Pretendard'}},chartFill:'none',chartLine:{fill:'none',width:0},plotAreaFill:'none',plotAreaLine:{fill:'none',width:0}});applyPresentationChartFont(c,{fontFamily:'Pretendard'});
t(s,'관광·행정 거점',857,449,366,29,20);t(s,'황리단길과 시청 주변 일부 구간에서\n서행·정체가 나타난다.',857,485,369,51,17,C.sub);
t(s,'서측 원도심에도 정체 구간이 존재',857,547,374,31,18,C.orange);
}
{
const g=JSON.parse(await fs.readFile(B+'/anchor_revision6_metadata.json','utf8'));
const s=p.slides.add();s.background.fill='#FFFFFF';
t(s,'프로그램 : 네 앵커와 중앙 교류공간',60,29,1160,27,15,C.blue);
t(s,'북측 공공·정주와 남측 문화·창작을 중앙에서 연결한다',60,73,1160,45,30);
t(s,'실제 부지 경계 위에 프로그램 권역과 주변 원도심의 연결 관계를 표시한다',60,120,1160,31,18,C.sub);
const fr={x:60,y:171,w:620,h:620*1160/1680};
const sc=fr.w/(g.extent[2]-g.extent[0]);
const xy=([x,y])=>[fr.x+(x-g.extent[0])*sc,fr.y+(g.extent[3]-y)*sc];
await im(s,B+'/assets/anchor_base_v6.png',fr.x,fr.y,fr.w,fr.h,'실제 필지·가로·철도 지도 위 구경주역 프로그램 권역');
function poly(ps,fill,line=C.blue,lw=.6){const xx=ps.map(a=>a[0]),yy=ps.map(a=>a[1]),x=Math.min(...xx),y=Math.min(...yy),w=Math.max(...xx)-x,h=Math.max(...yy)-y;return s.shapes.add({geometry:'custom',name:'anchor-region-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:line,width:lw},customPaths:[{width:w,height:h,commands:ps.map((a,i)=>({[i?'lineTo':'moveTo']:{x:a[0]-x,y:a[1]-y}})).concat([{close:{}}])}]});}
function ar(a,b,col,width=1.5,two=false){s.shapes.add({geometry:'connector',kind:'straight',name:'anchor-axis-'+(++id),position:{left:Math.min(a[0],b[0]),top:Math.min(a[1],b[1]),width:Math.max(.01,Math.abs(b[0]-a[0])),height:Math.max(.01,Math.abs(b[1]-a[1])),horizontalFlip:b[0]<a[0],verticalFlip:b[1]<a[1]},line:{style:'solid',fill:col,width},tail:{type:'triangle',width:'med',length:'med'},...(two?{head:{type:'triangle',width:'med',length:'med'}}:{})});}
const specs={civic:{fill:'#BDD4E3',n:'1',title:'공공·생활',english:'Civic Anchor',y:186,program:'공공청사·공공기관, 주민 편의·건강·생활문화시설',role:'출근과 시민서비스로 평일의 반복 이용'},residential:{fill:'#E4EBF0',n:'2',title:'주거·정주',english:'Residential Anchor',y:273,program:'일반 공동주택 256세대, 계획 거주인구 464명',role:'주거 커뮤니티로 저녁·밤·주말의 생활'},creative:{fill:'#C4D3DD',n:'3',title:'창작·생산',english:'Creative Anchor',y:436,program:'작가 레지던시·제작공방·체험관·공예마켓',role:'제작·전시·체험·판매와 사업화 지원'},cultural:{fill:'#DDE8EF',n:'4',title:'역사문화',english:'Cultural Anchor',y:523,program:'역사문화존·박물관·전시장·개방형 수장고',role:'관광지원센터와 함께 방문과 체류 유도'}};
for(const r of g.regions){poly(r.points.map(xy),r.key==='exchange'?'#DCA77F':specs[r.key].fill);}
poly(g.zone.map(xy),'none',C.blue,1.25);
// The axes express a planning connection, not an existing road alignment.
ar(xy([25,-438]),xy([25,415]),'#FFFFFF',5,true);
ar(xy([25,-438]),xy([25,415]),C.blue,1.5,true);
ar(xy([-580,-3]),xy([640,-3]),'#FFFFFF',6,true);
ar(xy([-580,-3]),xy([640,-3]),C.orange,3.1,true);
const exchange=xy([25,-3]);sh(s,'ellipse',exchange[0]-6,exchange[1]-6,12,12,C.orange,'#FFFFFF',1.5);
// Native numbered labels and leaders connect geography with program content.
for(const r of g.regions){
 if(r.key==='exchange')continue;const a=specs[r.key],pt=xy([-79,r.center[1]]);
 sh(s,'ellipse',pt[0]-11,pt[1]-11,22,22,C.blue,'#FFFFFF',.7);t(s,a.n,pt[0]-11,pt[1]-10,22,20,13,'#FFFFFF','center');
 const edge=xy([144,r.center[1]]),dest=[712,a.y+17];conn(s,edge,[688,edge[1]],'#A6B5C0');conn(s,[688,edge[1]],dest,'#A6B5C0');
 t(s,a.n,724,a.y,20,31,17,C.blue);t(s,a.title,755,a.y,191,31,23);t(s,a.english,947,a.y+3,287,27,16,C.blue);
 t(s,a.program,755,a.y+33,477,25,16,C.sub);t(s,a.role,755,a.y+59,477,25,17,C.ink);
}
t(s,'중앙 교류공간',754,363,479,29,22,C.orange);t(s,'남북 앵커와 동서 보행이 만나는 마켓·전시·휴식 공간',754,396,479,26,16,C.sub);
conn(s,xy([150,-3]),[712,378],C.orange);
t(s,'성동시장',90,363,150,29,18,C.ink);t(s,'황오·황촌',490,363,156,29,18,C.ink);
t(s,'북측 공공·정주',478,214,184,27,17,C.blue);t(s,'남측 문화·창작',478,507,184,27,17,C.blue);
t(s,'N',641,180,22,26,15,C.sub,'center');ar([652,225],[652,208],C.sub,1.2);
ln(s,77,583,250*sc,C.sub,1);ln(s,77,580,1,C.sub,5);ln(s,77+250*sc,580,1,C.sub,5);t(s,'0',73,585,25,20,11.5,C.sub);t(s,'250m',139,585,47,20,11.5,C.sub,'right');
ln(s,60,633,1160);t(s,'남북의 네 앵커와 동서 보행을 연결하는 공공공간',60,641,1160,32,19,C.ink,'center');
t(s,'국토지리정보원·V-World 기초지도 / 프로그램 권역 구상: 세부 경계와 보행축은 설계 과정에서 조정',60,683,1132,24,12.5,C.sub);t(s,'38',1187,677,47,28,17,C.sub,'right');
s.speakerNotes.text='사용자 최신 프로그램 정의에 따른 네 앵커. 북측은 Civic 공공·생활 거점과 Residential 주거·정주 거점, 남측은 Creative 창작·생산 거점과 Cultural 역사문화 거점으로 구성. 중앙 교류공간은 성동시장과 황오·황촌을 잇는 동서 보행과 남북 앵커를 연결한다. 지도는 국토지리정보원·V-World 기반 gj-datamap의 필지·도로·철도와 경주시 고시 계획부지 경계 좌표를 사용. 색칠한 내부 권역은 확정 용도구역이나 면적배분이 아닌 프로그램 배치 구상. 공공청사 이전·통합은 본 계획의 제안이며 확정된 행정계획으로 서술하지 않음. 주거 256세대와 464명은 사용자 최신 계획값. 거주자와 근무자의 중복을 제외하여 이용인구를 산정해야 한다. 중앙 남측의 레지던시·공방·체험시설은 남측 Creative Anchor에 포함. 창작사업화 지원과 관광지원센터를 각 권역에 연계.';
}
p.slides.items[0].speakerNotes.text='출처: https://1tree1.github.io/gj-datamap/report.html 및 https://1tree1.github.io/gj-datamap/data/fabric_report.json. 국토지리정보원 건물·담장·도로중심선, 자체 계산 2026.09.28. 반경 150m, 광선 720개, 경로 2m 간격. 두 대표 지점은 같은 320×310m 창으로 비교하며 경로 평균과 구분한다. 화랑로: 평균 11,057㎡, 중앙값 10,237㎡, 변동계수 0.184, 봉우리 간격 중앙값 99m. 황오동 골목: 평균 8,620㎡, 중앙값 4,938㎡, 변동계수 0.859, 간격 53m. 부지 동쪽 가장자리: 평균 5,427㎡, 중앙값 5,737㎡, 변동계수 0.451, 간격 28m. 봉우리 기준은 돌출도 250㎡ 또는 경로 중앙값의 8% 이상 중 큰 값, 최소 간격 8m. 시야의 넓이와 변화는 보행 가능성 또는 상권 활력과 구분한다. 동측의 시야 개방 지점은 접속 후보이며 실제 연결에는 소유·담장·단차의 현장 검토가 필요하다.';
p.slides.items[1].speakerNotes.text='출처: https://1tree1.github.io/gj-datamap/data/traffic_hist.geojson 및 https://1tree1.github.io/gj-datamap/data/traffic_hist_summary.json. 국가교통정보센터 ITS 평균 주행속도. 주말 표본일 2025.01.11, 02.08, 03.08, 04.12, 05.10, 06.14, 07.12. 지도 범위 EPSG:5187 [218000,359700,222000,362500]와 교차하는 방향별 도로 링크 554개. 정체 링크는 06시 79개, 13시 100개, 21시 81개. 배경도와 도로는 실제 지리좌표로 정합. 정체 분류 임계값은 데이터맵의 도시부 15, 도시고속 30, 고속도로 40km/h 미만이며 법정 기준을 의미하지 않는다. 부지 바로 서측 원도심에도 정체 구간이 보인다. 차량 대수와 속도는 다른 지표이므로 원도심의 활동량 또는 동서 활력의 격차를 속도만으로 판단할 수 없다. 접근 교통 처리와 보행 연결은 분석을 바탕으로 한 계획 제안이다.';
await(await PresentationFile.exportPptx(p)).save(B+'/revision6_slides.pptx');console.log('Created 13, 14 and 38 replacements.');
