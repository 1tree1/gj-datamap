import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {pathToFileURL} from 'node:url';
const B='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const {applyPresentationChartFont}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
const E=JSON.parse(await fs.readFile(B+'/revision5_evidence.json','utf8'));
const p=Presentation.create({slideSize:{width:12191695/9525,height:720}});p.theme.defaultFont='Pretendard';
const C={ink:'#20272E',sub:'#606D77',blue:'#235D82',soft:'#8AABBF',light:'#EAF1F5',line:'#CBD4DC',gray:'#B9C3CB',orange:'#B66A2B'};let id=0;
function sh(s,g,x,y,w,h,fill='none',stroke='none',lw=0){return s.shapes.add({geometry:g,name:'revision5-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:lw}});}
function t(s,v,x,y,w,h,z=20,c=C.ink,a='left',bold=false){const q=sh(s,'textbox',x,y,w,h);q.text=String(v);q.text.style={fontSize:z,typeface:'Pretendard',color:c,bold,alignment:a,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};return q;}
function line(s,a,b,col=C.line,w=.8,head=false,two=false){const[x1,y1]=a,[x2,y2]=b;let q=s.shapes.add({geometry:'connector',kind:'straight',name:'r5-link-'+(++id),position:{left:Math.min(x1,x2),top:Math.min(y1,y2),width:Math.max(.01,Math.abs(x2-x1)),height:Math.max(.01,Math.abs(y2-y1)),horizontalFlip:x2<x1,verticalFlip:y2<y1},line:{style:'solid',fill:col,width:w},...(head?{tail:{type:'triangle',width:'med',length:'med'}}:{}),...(two?{head:{type:'triangle',width:'med',length:'med'}}:{})});q.bringToFront();return q;}
function base(sec,title,sub,num,insight,source,notes){const s=p.slides.add();s.background.fill='#FFFFFF';sh(s,'rect',0,0,1280,2,C.blue);t(s,'현황과 분석  /  '+sec,48,24,1176,26,16,C.blue);t(s,title,48,60,1184,47,30);t(s,sub,48,115,1184,31,18,C.sub);line(s,[48,594],[1232,594]);t(s,'해석',48,610,55,27,14,C.sub);t(s,insight,119,603,1109,50,20);t(s,source,48,664,1126,40,12.5,C.sub);t(s,String(num),1185,675,47,28,17,C.sub,'right');s.speakerNotes.text=notes;return s;}
function chart(s,type,cats,series,x,y,w,h,o={}){
 if(type==='bar'&&(o.direction||'bar')==='bar'){cats=[...cats].reverse();series=series.map(a=>({...a,values:[...a.values].reverse(),points:a.points?.map(pt=>({...pt,idx:cats.length-1-pt.idx}))}));}
 const c=s.charts.add(type,{position:{left:x,top:y,width:w,height:h},categories:cats,series,barOptions:{direction:o.direction||'bar',grouping:o.grouping||'clustered',gapWidth:o.gap??65,overlap:o.grouping==='stacked'?100:0},hasLegend:false,xAxis:{visible:o.xVisible??true,textStyle:{fontSize:o.axSize||17,fill:C.ink,typeface:'Pretendard'},line:{fill:C.line,width:.8},majorGridlines:null,tickLabelPosition:'low'},yAxis:{visible:o.yVisible??false,textStyle:{fontSize:14,fill:C.sub,typeface:'Pretendard'},line:{fill:'none',width:0},majorGridlines:o.grid?{style:'solid',fill:'#E1E7EB',width:.6}:null,numberFormatCode:o.axisFmt||'0',min:0,max:o.max,majorUnit:o.unit},dataLabels:{showValue:true,position:o.grouping==='stacked'?'center':'outEnd',numberFormatCode:o.fmt||'0.0',textStyle:{fontSize:o.labelSize||17,fill:C.ink,typeface:'Pretendard',bold:false}},chartFill:'none',chartLine:{fill:'none',width:0},plotAreaFill:'none',plotAreaLine:{fill:'none',width:0}});applyPresentationChartFont(c,{fontFamily:'Pretendard'});return c;
}
// Original 21 / new 20: three graphs from the user's live tourist page.
{
const d=E.tourist,s=base('관광객의 이용 특성','경주 방문의 주말 집중·당일 이용·차량 의존을 함께 고려한다','경주시 전체 방문 자료 · 통신 기반 추정치와 관광객 표본조사의 범위를 구분한다',20,'주말 수요를 수용하고 도착 후 보행·문화체험·휴식을 연결해 원도심 체류를 지원한다.','관광데이터랩: 요일 2024.09–2026.08 / 숙박 2025.09–2026.08 · 경주시 제5회 관광실태조사(2024), 내국인 n=3,009\n제공 웹페이지의 데이터로 재작성 · 데이터랩 숙박 비중은 월별 비율의 단순평균 · 상세 출처와 계산은 발표자 노트',JSON.stringify(d,null,2)+'\n세 그래프는 https://1tree1.github.io/gj-datamap/tourists.html 의 c-dow/c-stay/c-mode 에서 재작성. 요일별 지수는 외지인 일평균/월~금 일평균*100. 도착 후 체류 지원은 계획적 해석이며 실증 효과의 추정치가 아님.');
t(s,'요일별 외지인 방문 지수',48,174,365,30,21);t(s,'월–금 평균=100 · 2024.09–2026.08',48,205,365,24,14.5,C.sub);
chart(s,'bar',d.dow.categories,[{name:'외지인 방문지수',values:d.dow.values,fill:C.gray,points:[{idx:5,fill:C.blue},{idx:6,fill:C.blue}]}],48,244,365,229,{direction:'column',max:180,unit:60,yVisible:true,grid:true,gap:42,fmt:'0',axSize:17,labelSize:15});
t(s,'당일·숙박 방문 비중',450,174,362,30,21);t(s,'같은 비율 단위, 서로 다른 조사 대상',450,205,363,24,14.5,C.sub);
sh(s,'rect',455,240,14,10,C.blue);t(s,'당일',477,231,62,27,15);sh(s,'rect',548,240,14,10,C.gray);t(s,'숙박',570,231,68,27,15);
chart(s,'bar',d.stay.categories,[{name:'당일',values:d.stay.day,fill:C.blue},{name:'숙박',values:d.stay.overnight,fill:C.gray}],445,270,366,133,{grouping:'stacked',max:100,gap:72,fmt:'0.0"%"',labelSize:17,axSize:17});
t(s,'데이터랩: 통신 추정 외지인 월별 순방문자\n관광설문: 2024 내국인 응답자 3,009명\n표본·집계 방식이 달라 직접 비교하지 않음',451,413,365,65,14,C.sub);
t(s,'경주까지 주요 교통수단',846,174,380,30,21);t(s,'2024 내국인 관광설문 · % · n=3,009',846,205,381,24,14.5,C.sub);
chart(s,'bar',d.mode.categories,[{name:'교통수단 비율',values:d.mode.values,fill:C.gray,points:[{idx:0,fill:C.blue}]}],828,234,392,244,{max:100,gap:45,fmt:'0.0"%"',labelSize:15,axSize:15});
for(const [x,v,l]of [[48,'1.63배','주말 / 평일 외지인 방문'],[450,'83.1%','통신 추정 외지인의 당일 방문'],[846,'76.9%','관광설문 내국인의 자가용 이용']]){t(s,v,x,495,360,50,39,C.blue);t(s,l,x,550,374,29,17,C.sub);}
}
// Original 22 / new 21: exact facility demands from printed pp.33 and 68.
{
const d=E.citizen,s=base('시민의 생활 요구','시민 응답은 쇼핑·여가, 대중교통, 문화·예술에 집중된다','시민 설문·대면 인터뷰 2025.03·04 · ‘원도심에 필요한 시설’ 응답자 52명 · 복수응답',21,'관광객 시설과 함께 주민의 문화·여가와 이동 편의를 충족하는 생활 기반을 배치한다.','경주시 원도심 미래구상 기획 연구(2025.07), 인쇄쪽 33·63–64·68 · 항목별 응답 수, 합계 97건\n전체 유효응답 63명 중 해당 문항 52명 · 복수응답이므로 비율 합산 불가 · ‘하천·정보’는 원문 분류명',JSON.stringify(d,null,2)+'\n원본 PDF p69(인쇄쪽68)에서9개값과문항52명확인. p34(인쇄쪽33)에서총65명/유효63명/조사일2차/네이버폼및대면방법확인. p64–65(인쇄쪽63–64) 인터뷰는 문화쇼핑시설 부족과 신경주역 접근 불편을 설명하며 일부 문화쇼핑집계는원문불일치가있어여기서는해당집계를사용하지않음. 지역전체대표성은보장되지않는소규모탐색조사.');
t(s,'원도심에 필요한 시설',48,174,638,31,22);t(s,'응답 수 (명) · 복수응답',48,208,639,25,15,C.sub);
chart(s,'bar',d.categories,[{name:'필요시설 응답수',values:d.counts,fill:C.gray,points:[0,1,2].map(idx=>({idx,fill:C.blue}))}],48,242,697,330,{max:30,unit:10,gap:46,fmt:'0"명"',labelSize:19,axSize:18});
line(s,[781,174],[781,574]);
t(s,'생활 요구를 계획으로 연결',817,174,414,34,23,C.blue);
t(s,'문화·여가를 일상 가까이에',817,236,405,31,21);t(s,'쇼핑·여가 26명 / 문화·예술 24명\n주민도 반복 이용하는 전시·체험·생활문화',817,277,408,54,17,C.sub);
t(s,'시설과 함께 접근성 개선',817,366,405,31,21);t(s,'대중교통 24명\n버스·환승·보행 동선과 시설 출입구를 연결',817,407,408,54,17,C.sub);
t(s,'시민과 관광객이 공유하는 거점',817,496,406,31,21,C.blue);t(s,'Civic의 생활서비스와 Cultural·Creative의\n문화·체험 프로그램을 함께 이용',817,536,407,45,17,C.sub);
}
// Original 25 / new 23: a relationship diagram, deliberately not a geographic map.
{
const s=base('도시재생의 방향','도시 연결·행정 통합·청년 정주를 재생의 기반으로 삼는다','계획 제안 · 북측 공공·정주와 남측 문화·창작을 연결하고 주변 원도심으로 이용을 확산한다',23,'목표는 원도심 공동화 완화와 청년 정착이다. 근무·방문·생활 이용이 서로 다른 시간대를 채우게 한다.','사례 적용 원리: Delft 역·시청의 공공홀 연결(Mecanoo) / King’s Cross의 교육·주거·업무와 공공공간 결합\n관계 개념도이며 실제 배치·동선 확정안이 아님 · 시청 통합 배치는 설계 제안 · 효과와 청년인구 증가는 추후 검증',JSON.stringify(E.cases,null,2)+'\n사례의 공간구성 원리를 경주에 적용한 설계자의 해석이며, 경주에서 동일한 효과나 청년인구 증가를 보증하지 않음. 청사 통합은 공식 이전확정이 아니라 사용자 계획 제안. 북측 Civic+Residential, 남측 Cultural+Creative, 중앙 교류공간은 네앵커와동서보행을연결. 청사출근·시민서비스의반복이용,관광객방문,창작활동,야간거주를결합하는구조.');
t(s,'북천·황성공원',358,165,250,27,17,C.sub,'center');
// Spatial hierarchy: strong east-west axis, subordinate north-south axis.
line(s,[475,207],[475,526],C.soft,2.1,true,true);
line(s,[200,361],[746,361],C.blue,4,true,true);
t(s,'성동시장',58,344,134,31,20,C.blue,'center');t(s,'황오·황촌',748,344,97,31,20,C.blue,'center');
// Functional anchors: only the Civic destination is dark-filled for emphasis.
sh(s,'rect',266,215,194,66,C.blue);t(s,'Civic',279,217,167,30,23,'#FFFFFF','center');t(s,'통합 시청·공공기관',279,250,167,25,17,'#FFFFFF','center');
sh(s,'rect',493,215,207,66,'#FFFFFF',C.blue,1.2);t(s,'Residential',503,217,187,30,23,C.blue,'center');t(s,'일반 공동주택·생활시설',501,250,191,25,16.5,C.ink,'center');
t(s,'분산된\n행정 기능',56,211,159,59,17,C.sub,'center');line(s,[213,248],[257,248],C.blue,1.5,true);
sh(s,'rect',266,440,194,65,'#FFFFFF',C.blue,1.2);t(s,'Cultural',279,442,167,30,23,C.blue,'center');t(s,'역사·전시·관광지원',276,475,173,25,17,C.ink,'center');
sh(s,'rect',493,440,207,65,'#FFFFFF',C.blue,1.2);t(s,'Creative',503,442,187,30,23,C.blue,'center');t(s,'레지던시·공방·마켓',503,475,187,25,17,C.ink,'center');
// Clear short branches connect all four anchors into the central exchange.
for(const [a,b]of [[[365,286],[439,317]],[[594,286],[513,317]],[[365,435],[439,405]],[[594,435],[513,405]]])line(s,a,b,C.soft,1.1);
sh(s,'ellipse',421,307,108,108,C.light,C.blue,1.6);t(s,'중앙\n교류공간',429,322,92,74,21,C.blue,'center');
t(s,'동서 생활권 연결',246,326,161,26,16,C.blue);
t(s,'남북 문화·공공축',539,394,198,26,16,C.sub);
t(s,'대릉원·황리단길 관광권',330,538,304,27,17,C.sub,'center');
line(s,[855,177],[855,573]);
t(s,'연결',884,178,328,33,23,C.blue);t(s,'관광객과 주민의 동선·서비스 공유',884,217,337,30,18);t(s,'보행·환승·휴식으로 이용 편의 개선',884,249,337,27,16.5,C.sub);
t(s,'행정 통합',884,316,328,33,23,C.blue);t(s,'분산 청사를 부지의 공공 거점으로',884,355,337,30,18);t(s,'출근·민원 방문을 원도심 가로와 연결',884,387,337,27,16.5,C.sub);
t(s,'청년 정주',884,454,328,33,23,C.orange);t(s,'일자리·주거·생활문화 기반 결합',884,493,337,30,18);t(s,'지속적인 활동과 정착을 지원',884,525,337,27,16.5,C.sub);
}
// New anchor slide: latest user image supersedes the three-anchor definition.
{
const s=p.slides.add();s.background.fill='#FFFFFF';
t(s,'프로그램 : 네 앵커와 중앙 교류공간',60,30,1110,26,15,C.blue);
t(s,'북측 공공·정주와 남측 문화·창작을 중앙에서 연결한다',60,68,1160,47,31);
t(s,'각 권역에 두 앵커를 배치해 평일의 반복 이용과 방문·창작, 저녁·주말의 생활을 보완한다',60,120,1160,29,18,C.sub);
t(s,'북측',60,179,82,33,20,C.blue);t(s,'공공·정주',60,214,94,25,15,C.sub);
const anchors=[
 {x:182,y:171,en:'Civic Anchor',ko:'공공·생활 거점',prog:'공공청사·공공기관\n주민 편의·건강·생활문화시설',role:'출근·시민서비스로 평일의 반복 이용'},
 {x:734,y:171,en:'Residential Anchor',ko:'주거·정주 거점',prog:'일반 공동주택 256세대 · 계획 거주인구 464명\n주거 커뮤니티·생활공간',role:'저녁·밤·주말의 생활을 이어가는 거주 기반'},
 {x:182,y:450,en:'Cultural Anchor',ko:'역사문화 거점',prog:'역사문화존·박물관·전시장\n개방형 수장고·관광지원센터',role:'주변 관광을 유입해 방문과 체류를 형성'},
 {x:734,y:450,en:'Creative Anchor',ko:'창작·생산 거점',prog:'작가 레지던시·제작공방·체험관\n공예마켓·사업화 지원공간',role:'제작·전시·체험·판매로 창작 활동을 지속'}
];
for(const a of anchors){t(s,a.en,a.x,a.y,480,38,27,C.blue);t(s,a.ko,a.x,a.y+40,470,30,20);t(s,a.prog,a.x,a.y+79,490,52,18);t(s,a.role,a.x,a.y+134,492,31,18.5,C.blue);}
t(s,'남측',60,459,82,33,20,C.blue);t(s,'문화·창작',60,494,103,25,15,C.sub);
for(const x of [406,968]){line(s,[x,342],[x,358],C.blue,1.2);line(s,[x,426],[x,442],C.blue,1.2);}
sh(s,'rect',60,358,1160,68,C.light);
t(s,'성동시장',80,378,149,30,20,C.blue,'center');t(s,'중앙 교류공간',484,364,299,30,24,C.blue,'center');t(s,'마켓·전시·휴식·교류',456,394,355,25,17,C.sub,'center');t(s,'황오·황촌',1041,378,159,30,20,C.blue,'center');
line(s,[248,391],[458,391],C.blue,1.5,true,true);line(s,[809,391],[1025,391],C.blue,1.5,true,true);
t(s,'남북의 네 앵커와 동서 보행이 만나는 공공공간',381,640,527,29,18,C.ink,'center');
t(s,'중앙 남측의 레지던시·공방·체험시설은 남측 Creative Anchor에 포함 · 이용인구는 근무·거주 중복을 제외해 산정',60,682,1125,22,12.5,C.sub);t(s,'38',1185,675,47,28,17,C.sub,'right');
s.speakerNotes.text='사용자가 제공한 최신 이미지(2026.10.11)에서 네 앵커 정의를 적용. 앞선 세 앵커+주거 설명은 이 구성으로 대체함. 북측 공공·정주=Civic+Residential, 남측 문화·창작=Cultural+Creative. 중앙 남측 레지던시·공방·체험관도 기능적으로남측Creative에포함. 주거256세대(32세대×8동),계획464명은앞서제공한수정안유지. 북측청년·일반공동주택은공공임대로단정하지않음. 시청통합이전은설계제안. 발표: 남측에는 역사문화와 창작·생산 앵커를 배치해 방문과 창작 활동을 유도하고, 북측에는 공공·생활과 주거·정주 앵커를 배치해 일상적인 근무와 거주를 확보한다. 중앙 교류공간과 보행축으로 두 권역의 활동을 연결하여 주변 원도심으로 이어지게 한다.';
}
await(await PresentationFile.exportPptx(p)).save(B+'/revision5_slides.pptx');
console.log('Created three replacement slides and the updated four-anchor slide.');
