import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const B='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build';
const p=Presentation.create({slideSize:{width:12191695/9525,height:720}});p.theme.defaultFont='Pretendard';const s=p.slides.add();let id=0;
const C={blue:'#235D82',ink:'#252C32',sub:'#69747D',line:'#CED4DA'};
function rect(x,y,w,h,fill,name='key'){return s.shapes.add({geometry:'rect',name:'r10-'+name+'-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}});}
function text(v,x,y,w,h,z=16,c=C.ink){let q=s.shapes.add({geometry:'textbox',name:'r10-label-'+(++id),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});q.text=v;q.text.style={fontSize:z,typeface:'Pretendard',bold:false,color:c,alignment:'left',verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};return q;}
text('건물 높이 분포',48,151,220,27,18,C.blue);text('층수 기준',493,153,145,25,15,C.sub);
s.images.add({blob:new Uint8Array(await fs.readFile(B+'/assets/height_qgis_revision10.png')),contentType:'image/png',alt:'QGIS 건물 층수 지도. NGII nmly 실제 층수, 2026-8 고시구역과 동서 150m 비교 범위.',fit:'contain',position:{left:48,top:182,width:590,height:372}});
for(const[k,v,c]of [[0,'1층','#BEC5CB'],[1,'2층','#89A8BC'],[2,'3–5층','#447594'],[3,'6층 이상','#18415B']]){const x=48+k*114;rect(x,567,13,13,c);text(v,x+22,560,97,27,16);}
text('높을수록 진한 색',494,560,148,27,14,C.sub);
// Compact geographic legend remains editable alongside the rendered QGIS map.
for(let k=0;k<3;k++)rect(48+k*8,597,5,1,'#8A959E','band-dash');
rect(428,597,24,1.2,C.blue,'boundary');text('고시구역',460,586,144,24,14,C.sub);
text('동서 비교 범위 밖 건물은 연하게 표시',48,607,582,19,13,C.sub);
rect(662,154,.7,462,'#D8DEE3','separator');
await(await PresentationFile.exportPptx(p)).save(B+'/revision10_map_overlay.pptx');console.log('Built QGIS map and editable legend.');
