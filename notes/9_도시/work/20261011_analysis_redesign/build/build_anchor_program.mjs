import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const B='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build';
const p=Presentation.create({slideSize:{width:12191695/9525,height:720}});p.theme.defaultFont='Pretendard';
const s=p.slides.add();s.background.fill='#FFFFFF';let id=0;
const C={ink:'#20272E',sub:'#67727B',blue:'#235D82',light:'#EAF1F5',line:'#CDD6DC',orange:'#B66A2B'};
function sh(g,x,y,w,h,fill='none',stroke='none',lw=0){return s.shapes.add({geometry:g,name:'anchor-program-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:lw}});}
function t(v,x,y,w,h,z=20,c=C.ink,a='left',bold=false){const q=sh('textbox',x,y,w,h);q.text=v;q.text.style={fontSize:z,typeface:'Pretendard',color:c,bold,alignment:a,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};return q;}
function line(x1,y1,x2,y2,c=C.line,w=1,heads=false){let q=s.shapes.add({geometry:'connector',kind:'straight',name:'anchor-connection-'+(++id),position:{left:Math.min(x1,x2),top:Math.min(y1,y2),width:Math.max(.01,Math.abs(x2-x1)),height:Math.max(.01,Math.abs(y2-y1)),horizontalFlip:x2<x1,verticalFlip:y2<y1},line:{style:'solid',fill:c,width:w},...(heads?{head:{type:'triangle',width:'sm',length:'sm'},tail:{type:'triangle',width:'sm',length:'sm'}}:{})});q.bringToFront();return q;}
t('프로그램 : 앵커 구성',60,30,900,26,15,C.blue);
t('세 앵커와 주거를 중앙 교류공간으로 연결한다',60,68,1160,48,32);
t('공공업무·문화방문·창작 활동에 주거를 더해 원도심의 이용 시간대를 보완한다',60,122,1160,28,18,C.sub);
const rows=[
 {x:60,where:'북측',en:'Civic',ko:'공공·생활 거점',role:'평일의 반복 이용',who:'기관 종사자 · 상담·민원 방문자 · 주민',program:'공공청사·공공기관\n주민 편의·건강·커뮤니티시설'},
 {x:455,where:'남측',en:'Cultural',ko:'역사문화 거점',role:'방문하고 머무는 문화 경험',who:'관광객 · 관람객 · 교육·체험 참여자',program:'박물관·기획전시·개방형 수장고\n관광지원센터 · 중앙 체험시설 연계'},
 {x:850,where:'중앙 남측',en:'Creative',ko:'창작·생산 거점',role:'제작을 전시·체험·판매로 연결',who:'입주 작가 · 공예가 · 창작·사업 참여자',program:'작가 20명 레지던시·제작공방\n공예전시·마켓 · 교류·사업화 지원'}
];
for(const r of rows){
 t(r.where,r.x,174,330,24,15,C.sub);
 t(r.en,r.x,205,340,45,33,C.blue);
 t(r.ko,r.x,250,340,32,22);
 t(r.role,r.x,299,357,31,21,C.blue);
 line(r.x,344,r.x+350,344,C.line,.8);
 t(r.who,r.x,355,357,28,16,C.sub);
 t(r.program,r.x,389,357,58,18);
 line(r.x+175,454,r.x+175,468,C.blue,1.2);
}
line(235,468,1025,468,C.blue,1.2);line(630,468,630,488,C.blue,1.2);
// All anchors feed the shared exchange space. The band is a single common element.
sh('rect',60,488,1140,78,C.light);
t('Central Exchange  중앙 교류공간',339,489,606,35,24,C.blue,'center');
t('성동시장',121,528,154,28,19,C.ink,'center');
t('마켓·전시·휴식·교류',435,528,385,28,19,C.ink,'center');
t('황오·황촌',986,528,159,28,19,C.ink,'center');
line(277,542,419,542,C.blue,1.3,true);line(838,542,973,542,C.blue,1.3,true);
// Housing supports the anchors; it is not classified as a fourth anchor.
t('주거',60,590,100,30,25);
t('저녁·밤의 생활',60,627,260,26,19,C.orange);
t('256세대',321,585,180,42,29,C.blue);
t('464명',506,585,160,42,29,C.blue);
t('32세대 × 8동',321,629,172,24,16,C.sub);
t('계획 거주인구',506,629,174,24,16,C.sub);
t('일반 공동주택',727,590,433,27,20);
t('청년·소형 가구, 기관 종사자·원도심 근로자',727,622,433,27,17,C.sub);
let q=s.shapes.add({geometry:'connector',kind:'straight',name:'housing-to-exchange',position:{left:1179,top:566,width:.01,height:40,verticalFlip:true},line:{fill:C.orange,width:1.5},tail:{type:'triangle',width:'med',length:'med'}});q.bringToFront();
t('계획안 2026.10.11 · 근무자와 거주자는 중복될 수 있으므로 단순 합산하지 않음',60,681,1140,22,13,C.sub);
s.speakerNotes.text='출처: 사용자가 2026.10.11 이 대화에 제공한 최신 앵커 프로그램 정리. 표와 설명의 의미를 유지해 발표용으로 요약. Civic: 북측 공공청사·공공기관 및 주민서비스. Cultural: 남측 역사문화존과 중앙 체험시설 연계. Creative: 중앙 남측 작가20명의 레지던시·제작공방, 전시·마켓·교류·사업화 지원. 주거: 청년·소형 가구, 공공기관 종사자와 원도심 근로자도 거주할 수 있는 일반 공동주택. 32세대×8동=256세대, 계획 거주인구464명. 공공청사·기관 종사자는 Civic의 상주 활동인구, 작가는 Creative의 상주 활동인구, 문화시설 운영자는 정기 근무자에 포함될 수 있음. 근무자와 거주자는 중복될 수 있으므로 인구를 단순 합산하지 않음. 시간대 표현은 계획 역할에 대한 개념이며 관측 이용량이 아님. Central Exchange: 남북 활동 동선과 성동시장–황오·황촌의 동서 보행을 연결하며 마켓·전시·휴식·교류가 일어나는 공공공간. 발표: 공공업무와 생활서비스로 평일 반복 이용을 만들고, 역사문화 프로그램으로 외부 방문을 유도하며, 창작 활동으로 전시·체험·판매를 이어간다. 주거가 저녁·밤의 생활을 더하고 중앙 교류공간이 주변 원도심으로 연결한다.';
await(await PresentationFile.exportPptx(p)).save(B+'/anchor_program_draft.pptx');
console.log('One editable anchor program slide created.');
