import {Presentation,PresentationFile} from '@oai/artifact-tool';
const B='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build';
const p=Presentation.create({slideSize:{width:12191695/9525,height:720}});
p.theme.defaultFont='Pretendard';const s=p.slides.add();s.background.fill='#FFFFFF';
const C={blue:'#235D82',ink:'#252C32',sub:'#69747D',line:'#D1D9DE'};let id=0;
function text(v,x,y,w,h,size=20,color=C.ink,name='text'){
 const q=s.shapes.add({geometry:'textbox',name:'r9-'+name+'-'+(++id),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 q.text=v;q.text.style={fontSize:size,typeface:'Pretendard',color,bold:false,alignment:'left',verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};return q;
}
function rule(x,y,w,h,color){s.shapes.add({geometry:'rect',name:'r9-rule-'+(++id),position:{left:x,top:y,width:w,height:h},fill:color,line:{fill:'none',width:0}});}
rule(0,0,12191695/9525,2,C.blue);
text('현황과 분석  /  재생 방향',48,23,600,28,15,C.blue,'section');
text('계획목표',48,63,900,45,32,C.ink,'title');
text('구경주역 부지와 주변 원도심의 재생 방향',48,115,1100,30,18,C.sub,'subtitle');
rule(640,194,0.8,412,C.line);rule(80,389,1120,0.8,C.line);
const items=[
 {n:'01',x:80,y:203,key:'생활권 연계 강화',lines:['동서 생활권과 남북 보행축 연결','관광객과 주민이 공유하는 보행·교류공간 조성']},
 {n:'02',x:690,y:203,key:'도심 중심기능 회복',lines:['시청 통합과 공공서비스 집적','행정·생활 거점 조성으로 원도심의 일상 이용 확대']},
 {n:'03',x:80,y:432,key:'지역경제 활성화',lines:['역사문화·창작 활동과 주변 상권 연계','방문과 체류를 체험·판매 및 지역 일자리로 연결']},
 {n:'04',x:690,y:432,key:'청년 정주기반 확충',lines:['주거와 일자리, 생활서비스의 복합화','청년의 지속적인 거주와 지역 활동을 지원']}
];
for(const v of items){
 text(v.n,v.x,v.y,60,27,18,C.sub,'number');
 text(v.key,v.x,v.y+37,530,60,41,C.blue,'keyword');
 text(v.lines[0],v.x,v.y+111,525,29,20,C.ink,'action');
 text(v.lines[1],v.x,v.y+144,525,29,18,C.sub,'detail');
}
text('계획 개념 참고: 경주시 도시기본계획 자료 · 국토연구원 도심재생 연구 · 도시재생 정책',48,671,1100,25,12,C.sub,'source');
text('24',1202,674,32,25,16,C.sub,'page');
await(await PresentationFile.exportPptx(p)).save(B+'/revision9_goal_slide.pptx');
console.log('Created four editable planning-goal keywords.');
