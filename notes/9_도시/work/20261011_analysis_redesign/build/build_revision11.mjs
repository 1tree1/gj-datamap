import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {pathToFileURL} from 'node:url';
const B='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const {applyPresentationChartFont}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
const D=JSON.parse(await fs.readFile(B+'/revision11_evidence.json','utf8'));
const p=Presentation.create({slideSize:{width:12191695/9525,height:720}});p.theme.defaultFont='Pretendard';
const C={ink:'#252C32',sub:'#69747D',blue:'#235D82',line:'#D1D9DE',gray:'#BBC5CC',pale:'#E7EDF1',orange:'#B66A2B'};
let id=0;const contracts=[];const tableSlides=[];const chartSlides=[];
const fmt=(x,d=0)=>Number(x).toLocaleString('en-US',{maximumFractionDigits:d,minimumFractionDigits:d});
function sh(s,g,x,y,w,h,fill='none',line='none',lw=0){return s.shapes.add({geometry:g,name:'r11-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:lw}});}
function t(s,v,x,y,w,h,z=20,c=C.ink,a='left'){const q=sh(s,'textbox',x,y,w,h);q.text=String(v);q.text.style={fontSize:z,typeface:'Pretendard',color:c,bold:false,alignment:a,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};return q;}
function line(s,x,y,w,c=C.line,lw=.8){sh(s,'rect',x,y,w,lw,c);}
function arrow(s,x,y,w,c=C.blue,lw=2){s.shapes.add({geometry:'connector',kind:'straight',name:'r11-flow-'+(++id),position:{left:x,top:y,width:w,height:0.01},line:{fill:c,width:lw},tail:{type:'triangle',width:'med',length:'med'}});}
function note(s,txt){s.speakerNotes.text=txt+'\n\n기준 자료: NEXUS 1918 최종 통합 스페이스 프로그램 v13 (2026.10.11, 주거 8동 수정). 사용자가 지정한 대화 「라이노 모델링과 프로그램 면적 비교」, thread 01a129e7-d0c2-7d82-af3a-e333678ba0ec. 비교 자료: work/nexus_v13_audit_20261011/facility_comparison.json, rhino_measurements.json, comparison_groups.json. 토지이용: placement-model-plan.json 저장 모델의 닫힌 경계. 선택 매스 면적과 저장 모델 경계의 기준을 구분. 157개 선택 매스의 실제 형상에 따른 2026.10.11 측정 결과이며 실시간 재측정이 아니다. Rhino 선언 단위 mm이나 48×10 주거동 등 치수에 따라 좌표 1단위를 1m로 해석했다. 기존 역사 상세 메시·지붕·식재는 매스 연면적 합계에서 제외. 내부 실의 존재나 실제 주차면수는 형상 총량만으로 확인되지 않는다. 계획값은 사업 승인·확정 수요·법정 적합 판정과 구분한다.';}
function base(title,sub,num,source='NEXUS 1918 v13 · 라이노 모델 비교 결과(2026.10.11) · 면적 단위 ㎡'){
 const s=p.slides.add();s.background.fill='#FFFFFF';line(s,0,0,1280,C.blue,2);
 t(s,'계획인구와 규모',48,24,900,26,15,C.blue);t(s,title,48,62,1184,45,31);t(s,sub,48,117,1184,30,18,C.sub);
 t(s,source,48,672,1130,25,12,C.sub);t(s,num,1190,672,42,27,16,C.sub,'right');return s;
}
function insight(s,a,b=''){line(s,48,600,1184);t(s,a,48,614,1184,b?27:44,19);if(b)t(s,b,48,643,1184,23,14.5,C.sub);}
function tbl(s,values,x,y,widths,rh=39,font=18,totalRows=[]){
 let tb=s.tables.add({rows:values.length,columns:widths.length,left:x,top:y,width:widths.reduce((a,b)=>a+b,0),height:values.length*rh,columnWidths:widths,values});
 tb.styleOptions={headerRow:false,bandedRows:false};tb.borders.assign({fill:'none',width:0});
 const block=tb.cells.block({row:0,column:0,rowCount:values.length,columnCount:widths.length});
 block.assign({fill:'#FFFFFF',textStyle:{fontSize:font,typeface:'Pretendard',color:C.ink,bold:false},margins:{left:8,right:8,top:4,bottom:4},anchor:'center'});
 for(let r=0;r<values.length;r++){
  tb.rows[r].height=rh;
  for(let c=0;c<widths.length;c++){
   const cell=tb.getCell(r,c);cell.text.style={fontSize:r===0?font-1:font,typeface:'Pretendard',color:totalRows.includes(r)?C.blue:(r===0?C.sub:C.ink),bold:false,alignment:c>0?'right':'left',verticalAlignment:'middle'};
   if(totalRows.includes(r)){cell.fill=C.pale;}
  }
  line(s,x,y+(r+1)*rh,widths.reduce((a,b)=>a+b,0),r===0?C.blue:C.line,r===0?1:.6);
 }
 tableSlides.push(47+p.slides.items.length);return tb;
}
function contract(slide,table,total_row,value_columns,component_rows){contracts.push({slide,table,label_column:0,total_row,value_columns,component_rows});}
function chart(s,categories,series,x,y,w,h,opts={}){
 const q=s.charts.add('bar',{position:{left:x,top:y,width:w,height:h},categories,series,barOptions:{direction:opts.horizontal?'bar':'column',gapWidth:opts.gap||85,grouping:'clustered'},hasLegend:!!opts.legend,legend:{position:'bottom',textStyle:{fontSize:14,fill:C.sub,typeface:'Pretendard'}},xAxis:{visible:true,textStyle:{fontSize:opts.font||17,fill:C.ink,typeface:'Pretendard'},line:{fill:C.line,width:.5},majorGridlines:null},yAxis:{visible:false,min:0,max:opts.max,majorGridlines:null,line:{fill:'none',width:0}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:opts.format||'#,##0',textStyle:{fontSize:opts.labelSize||18,fill:C.ink,typeface:'Pretendard'}},chartFill:'none',chartLine:{fill:'none',width:0},plotAreaFill:'none',plotAreaLine:{fill:'none',width:0}});
 applyPresentationChartFont(q,{fontFamily:'Pretendard'});chartSlides.push(47+p.slides.items.length);return q;
}
// 48 section divider
{
 const s=p.slides.add();s.background.fill='#FFFFFF';t(s,'5',60,130,180,130,100,C.blue);t(s,'계획인구와 규모',60,278,1160,80,54);
 t(s,'인구 가정과 운영 규모를 프로그램 면적에 연결한다',64,388,1150,40,25,C.sub);
 line(s,64,476,1150);t(s,'인구 산정',64,504,230,35,23);t(s,'프로그램 면적',350,504,255,35,23);t(s,'토지이용·건축규모',661,504,302,35,23);t(s,'개발규모표',1020,504,218,35,23);
 arrow(s,275,521,46);arrow(s,582,521,46);arrow(s,951,521,40);
 t(s,'프로그램 v13 · 256세대 기준 · 라이노 모델 측정값 비교',64,563,1100,30,17,C.sub);t(s,'48',1190,672,42,27,16,C.sub,'right');
 note(s,'이 장은 기존 600세대 검토안을 대체한다. 프로그램 목표 105,560㎡와 선택 모델 측정값 176,661.18㎡를 구분해 제시하며, 과거 포획률에 따른 전체 하루 방문자 예측을 최신 수요로 사용하지 않는다.');
}
// 49 assumptions and lineage
{
 const s=base('계획인구의 정의와 면적 산정 흐름','근무·거주·방문을 구분하고, 각 집단이 사용하는 공간의 규모를 산정한다',49);
 const cols=[{x:48,head:'공공업무·창작',big:'1,100명 + 20명',detail:'청사 업무 1,000석 + 기관 활동 약 100명\n작가 입주 20명은 별도 집단',method:'업무석·작업실 수\n실별 업무·지원 면적',area:'청사 26,500㎡\n기관 2,200㎡ · 레지던시 2,500㎡'},
 {x:458,head:'주거·체류',big:'464명 + 20명',detail:'256세대의 유형별 거주자 + 작가 숙소\n작가가 공동주택과 별도 거주하는 전제',method:'세대 수 × 유형별 인원\n층별 전용·공용 면적',area:'공동주택 19,200㎡\n커뮤니티 1,600㎡는 1층에 포함'},
 {x:868,head:'시설 방문·이용',big:'190명/회',detail:'체험수업 8실의 참가 정원\n실내 동시 운영 목표 250~300명',method:'회차 × 이용률 × 회당 정원\n체험·전시·대기·운영 공간',area:'실내 체험관 3,000㎡\n야외 체험·광장 12,000㎡'}];
 for(const c of cols){t(s,c.head,c.x,183,366,33,23);t(s,c.big,c.x,233,366,58,38,C.blue);t(s,c.detail,c.x,305,366,66,17,C.sub);line(s,c.x,392,364);t(s,c.method,c.x,411,366,63,20);t(s,c.area,c.x,514,366,66,20);}
 insight(s,'업무 규모·거주 인구·일일 이용건수는 단위가 달라 하나의 총인구로 합산하지 않는다.','근무자와 거주자의 겸용, 시설 간 이동, 문화시설 운영 인력은 운영계획에서 추가 확인한다.');
 note(s,'1,100명은 1,000석+기관 업무·사업참여 약100명의 계획 활동규모이며 실제 확정 직원수나 신규 고용수가 아니다. 작가20명은 거주와 제작에서 중복 계수하지 않는다. 464+20=484명 거주·체류 인구는 서로 다른 숙소 사용 전제. 전체 하루 방문자와 동시 체류 총인구는 미산정이다.');
}
// 50 visitor calculation
{
 const s=base('방문인구 산정: 체험시설 운영 시나리오','회당 참가 정원에서 하루 이용 규모를 계산하고, 시설 간 중복 방문은 별도로 관리한다',50);
 t(s,'체험수업 8실',48,178,530,32,23);t(s,'도자 50 + 금속 30 + 목공 30\n섬유 40 + 한지·탁본 40',48,223,525,65,23);
 t(s,'190명/회',48,312,510,58,42,C.blue);
 t(s,'기준 운영 가정',48,399,530,29,18,C.sub);t(s,'190 × 3회 × 70% = 399건/일',48,442,540,46,29,C.blue);
 t(s,'3회/일·이용률 70%는 이번 운영 시나리오\n전체 부지의 고유 방문자 예측과는 구분',48,511,540,54,17,C.sub);
 chart(s,D.visitors.map(x=>x.scenario),[{name:'체험 참가 이용건/일',values:D.visitors.map(x=>x.visits),fill:C.gray,points:[{idx:1,fill:C.blue}]}],635,181,579,242,{max:700,format:'#,##0"건"',font:17,labelSize:20});
 const tb=tbl(s,[['운영 가정','적은 운영','기준 운영','확대 운영'],['회차/일','2회','3회','4회'],['정원 이용률','60%','70%','80%']],637,438,[184,122,122,122],39,17);
 insight(s,'체험관은 250~300명 동시 운영 목표로 구성하고 예약 회차로 방문을 분산한다.','기관 방문은 사용자 추정 15~20명/일. 전시·공연·마켓 방문을 더한 전체 하루 방문자는 아직 산정하지 않았다.');
 note(s,'출처 v13: 체험수업 190명/회=도자2실×25+금속30+목공30+섬유2실×20+한지2실×20. 방문량 가정은 이번 발표를 위한 운영 시나리오 신규 제안: 2회×60%=228 이용건/일, 3회×70%=399, 4회×80%=608. 각 수치는 참가 이용건수이며 고유 방문자 수가 아니다. 회차의 실제 수요 검증은 미완료. 실내 동시250~300명 목표와 수업190명은 개념이 다르며 전시/디지털/시연이 포함된 운영목표다. 체류시간·시설 이동 중복·민원 방문은 후속 운영조사 대상. 공공기관15~20명/일은 지정 대화의 마지막 사용자 제공 추정. 과거 경주시 외지인140,085명×포획률7.9%=11,067명/일을 본 시설의 최신 확정수요로 사용하지 않는다.');
}
// 51 worker and civic area
{
 const s=base('근로·활동인구와 공공업무 면적','본청 정원과 계획 업무석을 구분하고, 지원 공간을 더해 청사 규모를 구성한다',51,'경주시 조직운영6대지표(2025.12.31 기준) · NEXUS v13 프로그램 배분');
 t(s,'본청 정원',48,179,260,30,21);t(s,'877명',48,227,260,58,42);arrow(s,285,255,82);
 t(s,'계획 업무석',402,179,350,30,21);t(s,'1,000석',402,227,345,58,42,C.blue);t(s,'여유 123석 · 신규 고용 인원과 구분',48,309,690,30,17,C.sub);
 t(s,'행정 업무 1,000석 × 8㎡',48,389,640,40,29);t(s,'8,000㎡',48,451,630,53,40,C.blue);
 t(s,'기관 활동 약 100명 = 2,200㎡ × 55% ÷ 12㎡\n작가 20명 = 숙소 20실 + 개인작업실 20실',48,526,645,53,17,C.sub);
 const tb=tbl(s,[['청사 공간','연면적(㎡)'],['행정 업무','8,000'],['민원·상담','2,000'],['회의·전산·행정지원','3,000'],['직원 편의','1,500'],['공용·설비','6,000'],['시의회','3,000'],['기록·재난·시민행정 지원','3,000'],['청사 합계','26,500']],748,180,[320,164],43,18,[8]);contract(51,1,8,[1],[1,2,3,4,5,6,7]);
 insight(s,'청사 26,500㎡는 선택한 배치 규모이며, 1,000석에 공용·의회·지원 기능을 배분한 값이다.','기관의 약 100명은 업무·사업참여 인원 가정이다. 문화시설 운영자 등을 포함한 전체 근로자 수는 미확정이다.');
 note(s,'공식자료 https://www.gyeongju.go.kr/open_content/ko/page.do?mnu_uid=2227 확인 2026-10-12: 2025.12.31 경주시 본청877명, 소속기관865명, 전체1742명. 청사1,000석은 계획가정. 청사면적은 사용자 선택 배치 2500×7+1500×3×2=26500㎡의 규모를 각실로 배분한 값이며 수요만으로 자동산출한 최적면적이나 법정상한이 아니다. 공공기관 약100명=2200×.55/12=100.83명(반올림 약100), 업무공간 비중55% 및12㎡/명은 v13 가정. 작가20명 숙소제작 겸용 중복금지.');
}
// 52 housing
{
 const s=base('정주인구 464명과 주거 연면적 19,200㎡','8동·256세대의 유형 구성에서 인구와 전용·공용 면적을 함께 계산한다',52);
 tbl(s,[['전용 유형','세대 수','인원/세대','계획 거주자'],['22㎡','64','1.0','64.0'],['33㎡','64','1.3','83.2'],['44㎡','96','2.3','220.8'],['58㎡','32','3.0','96.0'],['합계','256','평균 1.8125','464.0']],48,184,[150,120,143,163],51,20,[5]);contract(52,1,5,[1,3],[1,2,3,4]);
 t(s,'8세대/층 × 주거 4개 층 × 8동',48,520,580,33,22,C.blue);t(s,'별도 작가 숙소 20명 포함 시 거주·체류 484명',48,563,600,26,17,C.sub);
 t(s,'48m × 10m = 층당 480㎡',690,186,540,33,25);line(s,690,244,542);
 t(s,'2~5층  주거층',690,267,290,31,21);t(s,'15,360㎡',1020,263,212,43,30,C.blue,'right');t(s,'480 × 4개 층 × 8동\n전용 9,600 + 복도·코어·벽체 5,760',690,317,542,59,18,C.sub);
 t(s,'1층  주민시설·주거 공용',690,406,355,31,21);t(s,'3,840㎡',1040,401,192,43,30,C.ink,'right');t(s,'커뮤니티 1,600 + 출입·관리·설비 2,240\n커뮤니티는 주거 연면적 안에 포함',690,453,542,59,18,C.sub);
 line(s,690,538,542);t(s,'합계',690,552,190,37,24);t(s,'19,200㎡',995,548,237,43,32,C.blue,'right');
 insight(s,'세대 구성과 층별 면적을 고정해 인구 464명, 전용률 62.5%, 주거 19,200㎡를 산정한다.','현재 모델의 1층 연결부 약 960㎡는 계획 총량과 별도로 확인한다. 1층을 필로티로 비우면 바닥면적을 조정한다.');
 note(s,'주거유형별 계산:64×1+64×1.3+96×2.3+32×3=464. 전용면적64×22+64×33+96×44+32×58=9600㎡. 주거층15360㎡, 전용률62.5%. 1층3840㎡ 포함 총19200㎡. 커뮤니티1600은 추가합산금지. 작가20명은 공동주택과별도숙소라는전제. 주민과현장근로자는겸용가능하여합산금지.');
}
// 53 program area relationship
{
 const s=base('이용 규모를 프로그램 면적으로 전환','공간별 활동 정원과 실 구성을 더하고, 실내 연면적과 야외면적을 분리한다',53);
 const rows=[['이용·운영 기준','면적을 구성하는 방식','계획 면적'],['주민 커뮤니티 310자리','활동실 1,200 + 공용·설비 400','1,600㎡'],['생활문화홀 180석 등','공연·전시·교육·열람·운영실 합','2,000㎡'],['작가 20명','거주 1,000 + 제작 1,500','2,500㎡'],['체험수업 190명/회','체험실·전시·시연 등 2,250 + 공용 750','3,000㎡'],['공예 전시·판매','마켓 1,000 + 전시 700 + 지원·공용 1,000','2,700㎡'],['역사문화·관광','박물관·수장·전시·기록 6,000 + 지원 2,300','8,300㎡']];
 const tb=tbl(s,rows,48,180,[299,626,259],48,19);for(let r=1;r<rows.length;r++)tb.getCell(r,1).text.style={fontSize:18,typeface:'Pretendard',color:C.ink,bold:false,alignment:'left',verticalAlignment:'middle'};
 t(s,'비주차 건물',48,548,232,27,19);t(s,'73,400㎡',275,534,300,52,35,C.blue);
 t(s,'체험관 야외 프로그램',690,548,280,27,19);t(s,'12,000㎡',986,534,246,52,35);
 insight(s,'청사·주거·생활·문화 프로그램 73,400㎡에 주차장동 32,160㎡를 더해 105,560㎡를 구성한다.','표는 면적 산정의 대표 항목이다. 310자리·180석·190명/회는 서로 다른 시설 용량이며 방문인구로 합산하지 않는다.');
 note(s,'이 표는 프로그램 중 대표적인 수용규모와 면적배분의 관계를 설명한다. 모든면적이인원×단일원단위로산출된것은아니다. 역사문화박물관3500+수장1000+기획전시1000+기록500+사업화800+관광1500=8300. 전체19시설및완전한합표는뒤개발규모표. 비주차73400+구조주차32160=105560. 수영장1800+영화관800=조건부2600;제외시102960. 야외12000은연면적과합산하지않는다.');
}
// 54 parking
{
 const s=base('주차 수요 가정과 주차시설 면적','공공업무·관광·주거의 이용 시간과 목적을 구분해 공급량을 배분한다',54);
 t(s,'공공용 주차 720면',48,178,588,33,26,C.blue);
 t(s,'직원·입주자',48,237,195,29,19);t(s,'1,100 × 90% × 55% ÷ 1.05 = 519대',235,235,406,33,20);
 t(s,'민원·방문',48,287,195,29,19);t(s,'동시 250명 × 60% ÷ 1.5 = 100대',235,285,406,33,20);
 t(s,'업무용',48,337,195,29,19);t(s,'30대',235,335,406,33,20);
 line(s,48,391,592);t(s,'합계 648.6대 × 1.10 = 713.4대',48,415,592,36,24);t(s,'계획 720면',48,470,590,55,40,C.blue);
 t(s,'출근율·차량 이용률·동시 방문 250명은 설계 가정\n기관 방문 15~20명/일과 공공 민원 피크는 구분',48,541,591,49,16,C.sub);
 tbl(s,[['주차 이용군','주차동','옥외','합계'],['공공청사·기관','705','15','720'],['관광·상권 공유','300','0','300'],['주거','0','180','180'],['합계(면)','1,005','195','1,200']],690,179,[240,100,100,102],48,18,[4]);contract(54,1,4,[1,2,3],[1,2,3]);
 t(s,'주차장동',690,460,150,30,19);t(s,'1,005면 × 32㎡ = 32,160㎡',690,500,542,42,28,C.blue);
 t(s,'주거 256세대 × 0.70 → 180면 · 옥외 5,760㎡',690,556,542,29,17,C.sub);
 insight(s,'북측 705면은 4층 22,560㎡, 남측 300면은 3층 9,600㎡로 프로그램 면적에 반영한다.','1,200면은 설계 공급안이다. 32㎡/면은 개략 계수이며, 법정 필요량과 실제 배치 면수는 별도 확인한다.');
 note(s,'정확 계산:1100×.9×.55/1.05=518.5714286,250×.6/1.5=100,업무30,합648.5714286,여유10%적용713.4285714→계획720. 북측705×32=22560,건축면적5640(4층). 남측300×32=9600,건축면적3200(3층).기관옥외15면650㎡는공공720안에포함. 주거256×.7=179.2→180면,5760㎡는신규제안. 관광300면은선택공급규모이며특정수요조사부족분을입증한것은아니다. 도시농업·주거별외부공간이획지에들어가는지후속확인. v13의94×80=7520과건축면적5640불일치를확인했으므로박스치수는채택하지않음.');
}
// 55 actual measured land polygons
{
 const s=base('토지이용 면적 구성','건축 획지와 보행·공원·가로를 같은 계획 경계 안에서 중복 없이 집계한다',55,'저장 모델 경계 재집계 · 법정 대지면적 확정 전 · 비율은 반올림으로 합계와 차이 가능');
 const all=D.boundary.coordinates.flat(2);const pts=D.boundary.coordinates[0];const minx=Math.min(...pts.map(a=>a[0])),maxx=Math.max(...pts.map(a=>a[0])),miny=Math.min(...pts.map(a=>a[1])),maxy=Math.max(...pts.map(a=>a[1]));const sc=397/(maxy-miny),ox=139,oy=180;
 const xy=([x,y])=>[ox+(x-minx)*sc,oy+(maxy-y)*sc];
 function polygon(rings,fill,stroke='#FFFFFF',lw=.8){
  const rr=rings.map(a=>a.map(xy)),pp=rr.flat(),x=Math.min(...pp.map(a=>a[0])),y=Math.min(...pp.map(a=>a[1])),w=Math.max(...pp.map(a=>a[0]))-x,h=Math.max(...pp.map(a=>a[1]))-y;
  if(w<.02||h<.02)return;
  s.shapes.add({geometry:'custom',name:'r11-land-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:lw},customPaths:[{width:w,height:h,commands:rr.flatMap(r=>r.map((a,i)=>({[i?'lineTo':'moveTo']:{x:a[0]-x,y:a[1]-y}})).concat([{close:{}}]))}]});
 }
 function geom(g,fill,stroke,lw){if(g.type==='Polygon')polygon(g.coordinates,fill,stroke,lw);else if(g.type==='MultiPolygon')for(const rr of g.coordinates)polygon(rr,fill,stroke,lw);}
 const colors=[C.blue,'#C1D3DF','#E2E7EA','#F4F5F6'];for(let i=3;i>=0;i--)geom(D.land[i].geometry,colors[i]);
 for(const a of D.plots)geom(a.geometry,'none','#FFFFFF',.7);geom(D.boundary,'none',C.ink,.8);
 for(let i=0;i<4;i++){sh(s,'rect',49,183+i*37,12,12,colors[i],i===3?C.line:'none',.5);t(s,['건축 획지','보행축·광장','공원·녹지','가로·잔여'][i],49,199+i*37,90,18,11.5,C.sub);}
 t(s,'N',318,177,26,25,15,C.sub);sh(s,'triangle',326,211,10,15,C.sub);t(s,'계획 경계',52,538,79,24,14,C.sub);line(s,75,579,100*sc,C.sub,1);t(s,'100m',75,586,85,20,12,C.sub);
 t(s,'228,022㎡',446,173,770,61,42,C.blue);t(s,'계획 경계 전체',450,239,740,30,18,C.sub);
 const values=[['토지이용 구분','면적(㎡)','비율']].concat(D.land.map(x=>[x.name,fmt(x.area,1),fmt(x.pct,1)+'%'])).concat([['합계',fmt(D.site_area,1),'100.0%']]);
 tbl(s,values,445,290,[415,220,152],45,20,[5]);contract(55,1,5,[1],[1,2,3,4]);
 insight(s,'건축 획지는 138,089㎡이며, 인구와 프로그램 면적을 이 획지 안에서 배치·조정한다.','공원과 주차장 획지의 중복 5,571㎡는 주차 획지에 한 번만 반영했다. 차량가로·잔여 공간은 도로 레이어로 추가 분류한다.');
 note(s,'토지이용은인구계수로자동산출한값이아니라사용자가지정한모델의공간배분측정값이다.순서:인구→프로그램수요→건물/외부공간요구→계획획지와수용검토. 모델계획경계228022.181089㎡,문서v13경계218478.066㎡와9544.115㎡차이. 이장은모델경계기준으로통일. 건축획지138089.352103㎡,보행29671.845005㎡,공원25257.284066㎡,잔여35003.700295㎡. 공원도형내부중복과북측주차획지5570.861103㎡중복제거. 토지분류우선순위획지→공원→보행→잔여. 잔여는차량도로전용값이아니며다른미분류공간포함. 야외정원·텃밭·광장은획지또는공원내부분할이므로외부총량에별도중복추가하지않음.');
}
// 56 comparison
{
 const s=base('프로그램 목표와 모델의 건축규모 비교','권역별로 같은 기능을 묶어 연면적의 차이를 확인한다',56,'프로그램 v13 · 선택 매스 157개 측정(2026.10.11) · 좌표 1단위=1m 해석 · 기존 역사 상세 메시 제외');
 t(s,'프로그램 목표',48,172,370,29,20,C.sub);t(s,'105,560㎡',48,215,450,60,43,C.blue);
 t(s,'모델 측정값',704,172,430,29,20,C.sub);t(s,'176,661㎡',704,215,520,60,43);t(s,'+71,101㎡  ·  +67.4%',48,297,1184,38,26,C.orange);
 chart(s,D.groups.map(x=>x.name),[{name:'프로그램 목표',values:D.groups.map(x=>x.target),fill:C.gray},{name:'모델 측정',values:D.groups.map(x=>Math.round(x.model)),fill:C.blue}],48,358,1184,226,{legend:true,max:70000,font:15,labelSize:15,gap:70});
 insight(s,'증가분은 역사문화·관광과 창작·체험 시설, 모델에만 있는 모빌리티·가로상가에서 크게 발생한다.','모델 별도 항목 14,806㎡는 기존 편의·마켓 프로그램과의 대응을 확인한다. 총량 증가가 수요 증가를 뜻하지는 않는다.');
 note(s,'범주별합계는facility_comparison.json17행을상호배타적으로묶음. [청사+기관+북측주차]=목표51260/모델59457.454338,[주거+스포츠]=24500/26160,[문화+돌봄+농업]=3400/9611.182344(농업200미식별),[공예마켓+교류+레지던시+체험]=8500/27305.47513,[역사문화+관광+남측주차]=17900/39321.520789,[모빌리티+별도가로상가]=목표별도없음/14805.548174. 차트목표별도항목0은프로그램미배정의표현이지시설금지나확정0수요가아님. 전체측정176661.180776,목표105560,차이71101.180776,67.4%. 선택매스와저장모델일부7객체차이확인되어본값은지정대화의선택당시결과로표시.');
}
// 57 north detailed table
{
 const s=base('개발규모 산정표 ① 공공·정주·생활','실별 프로그램 합계와 층별 면적식을 함께 표시한다',57);
 const v=[['시설','면적 구성·층수','계획(㎡)','모델(㎡)'],['공공청사·의회','2,500×7층 + 1,500×3층×2동','26,500','29,545'],['공공기관 클러스터','상담·창업·관광·재생 4개 거점 / 3층','2,200','12,503'],['북측 주차장동','705면×32㎡ / 4층','22,560','17,409'],['주거·1층 주민시설','480㎡×5층×8동','19,200','20,160'],['스포츠·생활편의','우선 2,700 + 조건부 2,600','5,300','6,000'],['복합문화시설','1층 1,200 + 2층 800','2,000','7,471'],['건강·돌봄센터','600㎡×2층','1,200','2,141'],['도시농업 지원실','교육·도구·관리 / 1층','200','미식별'],['계획 소계','','79,160','']];
 const tb=tbl(s,v,48,180,[285,526,188,185],39,18,[9]);for(let r=1;r<v.length;r++)tb.getCell(r,1).text.style={fontSize:18,typeface:'Pretendard',color:C.ink,bold:false,alignment:'left',verticalAlignment:'middle'};contract(57,1,9,[2],[1,2,3,4,5,6,7,8]);
 insight(s,'주거 19,200㎡에는 커뮤니티 1,600㎡가 포함되며, 공공 주차는 옥외 15면을 제외한 동 규모다.','공공기관 모델은 청년창업지원센터를 함께 묶었다. 내부 실 구성의 일치까지 확인한 면적표는 아니다.');
 note(s,'계획소계79160=북측공공51260+주거스포츠24500+중앙북측생활문화3400. 모델열은기능묶음비교및정수반올림,내부기능일치확인아님. 모델미식별을0으로단정하지않는다. 프로그램면적은v13원문기준전체행유지.조건부2600=수영1800+영화800. 북측주차94×80기재는산술모순으로사용하지않고705×32/4=5640㎡적용.');
}
// 58 south detailed table
{
 const s=base('개발규모 산정표 ② 창작·역사문화·관광','면적이 새로 배분된 역사문화 시설과 모델의 별도 항목을 구분한다',58);
 const v=[['시설','면적 구성·층수','계획(㎡)','모델(㎡)'],['공예전시·실내마켓','1층 1,750 + 2층 950','2,700','8,994'],['작가 교류·행사','300㎡ / 1층','300','2,606'],['작가 레지던시','거주 1,000 + 제작 1,500 / 각 2층','2,500','7,125'],['실내 체험관','체험·전시·지원 2,250 + 공용 750 / 1층','3,000','8,581'],['박물관·수장고·기획전시','3,500(2층) + 1,000 + 1,000(각 1층)','5,500','묶음 비교'],['기록·해석 + 사업화 지원','500 + 800 / 각 2층','1,300','총 22,062'],['관광지원센터','1층 900 + 2층 600','1,500','1,260'],['남측 공유주차장','300면×32㎡ / 3층','9,600','16,000'],['계획 소계','','26,400',''],['모델 별도 항목','모빌리티 8,502 + 가로상가 6,303','별도 미배정','14,806']];
 const tb=tbl(s,v,48,176,[285,526,188,185],36,17.5,[9]);for(let r=1;r<v.length;r++)tb.getCell(r,1).text.style={fontSize:18,typeface:'Pretendard',color:C.ink,bold:false,alignment:'left',verticalAlignment:'middle'};contract(58,1,9,[2],[1,2,3,4,5,6,7,8]);
 insight(s,'북측·생활 79,160㎡ + 창작·역사문화·관광 26,400㎡ = 전체 계획 연면적 105,560㎡','역사문화 5,500㎡는 v13의 신규 면적 제안이다. 세 시설의 내부 배정과 기존 역사 보존·활용 범위를 확인한다.');
 note(s,'남측및창작소계26400. 박물관3500,수장1000,기획전시1000,기록500,사업화800=6800을모델근대역사관+지역문화원+소상공인상생동22061.575964와총량대응. 매스측정으로개별실존재확인불가. 관광1500은휴게330포함. 모델별도모빌리티8502.08+가로상가6303.468174=14805.548174로합계반올림14806이므로표시부분합8502+6303과1㎡반올림차이가능. 북측합79160+남측합26400=105560.');
}
// 59 full development scale
{
 const s=base('개발규모 총괄표','프로그램 배분안과 모델 측정 결과를 같은 면적 단위로 비교한다',59);
 const v=[['항목','프로그램 배분안','모델 측정·계획 경계','산정 기준'],['계획 경계','228,022㎡','228,022㎡','이번 장의 공간 검토 기준 통일'],['건축 획지 합계','138,089㎡','138,089㎡','13개 획지의 합집합'],['비주차 연면적','73,400㎡','143,252㎡','프로그램 / 선택 매스'],['주차장동 연면적','32,160㎡','33,409㎡','북측 + 남측 주차장동'],['총 연면적','105,560㎡','176,661㎡','주차장동 포함'],['조건부 시설 제외','102,960㎡','별도 배정 확인','수영장·영화관 2,600㎡ 제외'],['건축면적','32,513㎡ + 스포츠·편의','수평투영 재검토','상부 돌출·연결부·비움 반영 전'],['연면적 / 획지면적','76.4%','127.9%','법정 용적률과 구분한 참고 비율'],['건폐율·법정 용적률','획지별 재산정','획지별 재산정','건축·법정 산입면적 확정 후'],['주차 공급','1,200면','평면으로 확인','공공 720 + 관광 300 + 주거 180'],['최고 층수·높이','청사 7층 / 높이 검토','청사 7층·28m','모델 치수, 높이 제한 적합 별도']];
 const tb=tbl(s,v,48,174,[238,310,310,326],33,17.2,[5]);for(let r=1;r<v.length;r++)tb.getCell(r,3).text.style={fontSize:18,typeface:'Pretendard',color:C.ink,bold:false,alignment:'left',verticalAlignment:'middle'};contract(59,1,5,[1,2],[3,4]);
 insight(s,'법정 건폐율·용적률은 최종 대지 경계와 산입 면적, 건축면적이 확정된 뒤 산정한다.','표의 연면적/획지면적 비율만으로 규제 적합을 판단하지 않는다. 건축면적 32,513㎡는 스포츠·편의를 제외한 소계다.');
 note(s,'모델경계228022.181089,건축획지138089.352103. 목표비주차73400,주차32160,합105560. 모델비주차143251.766437,주차33409.414338,합176661.180776. 목표105560/138089.352103×100=76.4433%;모델176661.180776/138089.352103×100=127.9325%;법정용적률아님. 목표계획경계는v13의218478.066이아니라이번공간수용검토용으로모델과동일하게228022.181089적용. 계획건축면적은명시된시설소계32513.333333+스포츠생활편의의미정건축면적. 명시소계구성:5500+2200/3+5640+3840+1200+600+200+1750+300+1250+3000+1750+1000+1000+250+400+900+3200. 일률연면적/평균층수로추정하지않음. 법정건축면적/용적률산입면적/지상주차제외여부미확정으로BCR/FAR확정숫자제시하지않음. 모델청사최고28m는7개4m층구간기준이며옥탑등별도검토.');
}
// 60 decisions and spatial fit
{
 const s=base('프로그램과 모델을 맞추기 위한 조정 항목','수요·면적·획지 수용의 차이를 줄인 뒤 건축규모를 확정한다',60);
 const items=[['01','동측 창작·체험 획지','필요 최소 15,000㎡  /  획지 11,998㎡','체험관 3,000 + 야외 12,000만으로도 3,002㎡ 부족\n레지던시·교류실을 포함해 획지 또는 야외 배분 조정'],['02','북측 공공 주차','계획 22,560㎡  /  모델 17,409㎡','프로그램 건축면적 5,640㎡가 획지 5,571㎡를 초과\n705면 주차 평면과 건축 규모를 함께 재배치'],['03','남측 역사문화·모델 별도 시설','역사문화·지원 6,800㎡  /  모델 22,062㎡','수장·전시·기록 기능의 내부 면적을 먼저 배정\n모빌리티·가로상가의 프로그램 중복 여부 확인'],['04','운영과 입주 규모','청사 1,000석 · 주거 256세대 · 작가 20명','시설별 운영자·체류시간·예약 회차를 구체화\n주민과 근무자의 중복을 제외해 운영 인구 갱신']];
 items.forEach((v,i)=>{let y=177+i*102;t(s,v[0],48,y,54,34,19,C.sub);t(s,v[1],111,y,415,34,22);t(s,v[2],111,y+39,487,45,18,C.blue);t(s,v[3],675,y+8,557,65,18,C.sub);if(i<3)line(s,111,y+95,1121);});
 insight(s,'계획 프로그램을 면적 조정의 기준으로 삼고, 획지·평면·운영계획을 대조해 모델을 갱신한다.','이 장의 기준: v13 프로그램과 2026.10.11 모델 비교 결과. 신규 운영 시나리오와 미확정 항목은 별도 표시했다.');
 note(s,'동측획지11998.221324,체험관+야외15000차이3001.778676;레지던시교류부지별도필요. 북측주차계획건축5640대비획지5570.861103으로69.138897㎡초과,실제상세배치및규제평가전수용불가문제. 북측모델17409.414338/32≈544면환산이나램프코어배치미검증으로실제주차면수로기재하지않음. 남측역사문화지원은6800vs22061.575964로해당기능묶음비교. 층수/면적총량증가가내부실구성확보의증거는아님. 모델자체는수정하지않고프레젠테이션에검토결과와계획수정항목을제시.');
}
await(await PresentationFile.exportPptx(p)).save(B+'/revision11_section.pptx');
await fs.writeFile(B+'/revision11_requirements.json',JSON.stringify({tableSlides:[...new Set(tableSlides)],chartSlides:[...new Set(chartSlides)],contracts,total:62},null,2));
console.log(JSON.stringify({slides:p.slides.items.length,tableSlides,chartSlides,contracts:contracts.length}));

