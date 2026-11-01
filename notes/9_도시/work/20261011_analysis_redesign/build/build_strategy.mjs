import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const B='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build';
const G=JSON.parse(await fs.readFile(B+'/strategy_metadata.json','utf8'));
const p=Presentation.create({slideSize:{width:12191695/9525,height:720}});p.theme.defaultFont='Pretendard';const s=p.slides.add();
let id=0;const C={blue:'#235D82',secondary:'#83A9BE',orange:'#B66A2B',ink:'#252C32',sub:'#69747D',line:'#9EA8B0'};
const fr={x:58,y:144,w:603,h:502.5},ext=G.extent,sc=fr.w/(ext[2]-ext[0]);
const xy=([x,y])=>[fr.x+(x-ext[0])*sc,fr.y+(ext[3]-y)*sc];
function shape(g,x,y,w,h,fill='none',line='none',lw=0,extra={}){return s.shapes.add({geometry:g,name:'strategy-v4-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:line,width:lw},...extra});}
function txt(v,x,y,w,h=24,size=15,c=C.ink,a='left'){let q=shape('textbox',x,y,w,h);q.text=v;q.text.style={fontSize:size,typeface:'Pretendard',color:c,bold:false,alignment:a,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};return q;}
function arrow(a,b,col,w=1.2,two=false,ends='triangle'){
 const [x1,y1]=a,[x2,y2]=b;const q=s.shapes.add({geometry:'connector',kind:'straight',name:'strategy-arrow-'+(++id),position:{left:Math.min(x1,x2),top:Math.min(y1,y2),width:Math.max(.01,Math.abs(x2-x1)),height:Math.max(.01,Math.abs(y2-y1)),horizontalFlip:x2<x1,verticalFlip:y2<y1},line:{style:'solid',fill:col,width:w},tail:{type:ends,width:'med',length:'med'},...(two?{head:{type:ends,width:'med',length:'med'}}:{})});q.bringToFront();return q;
}
function polygon(ps,fill,line,lw){const xx=ps.map(a=>a[0]),yy=ps.map(a=>a[1]),x=Math.min(...xx),y=Math.min(...yy),w=Math.max(...xx)-x,h=Math.max(...yy)-y;return s.shapes.add({geometry:'custom',name:'strategy-boundary-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:line,width:lw},customPaths:[{width:w,height:h,commands:ps.map((a,i)=>({[i?'lineTo':'moveTo']:{x:a[0]-x,y:a[1]-y}})).concat([{close:{}}])}]});}
s.images.add({blob:new Uint8Array(await fs.readFile(B+'/assets/strategy_base_v4.png')),contentType:'image/png',alt:'실제 필지·가로·철도 지리정보, 남서쪽 황리단길까지 확장한 범위',fit:'contain',position:{left:fr.x,top:fr.y,width:fr.w,height:fr.h}});
polygon(G.zone.map(xy),'#DDEAF1',C.blue,1.3);
const [xmin,ymin,xmax,ymax]=G.siteBounds,xc=(xmin+xmax)/2,yc=(ymin+ymax)/2;
const center=xy([xc,yc-40]);
shape('ellipse',center[0]-34,center[1]-34,68,68,'#C1D7E5',C.blue,1.4);
// Destinations are true source centroids. Their circles and labels have safe margins.
for(const [key,label,dx,dy] of [['G_seongdong_market_r200','성동시장',-133,-12],['B_haengbok_hwangchon_digitized','행복황촌',113,-7],['H_hwangridan_r300','황리단길',-52,34]]){
 const [x,y]=xy(G.centers[key]);shape('ellipse',x-30,y-30,60,60,'none',C.line,.8,{line:{style:'dashed',fill:C.line,width:.8}});txt(label,x+dx,y+dy,79,24,15,C.ink);
}
// One primary connection and four thinner secondary connections.
const ylevels=[ymax-120,ymax-300,yc-40,ymin+280,ymin+120];
for(const [i,y]of ylevels.entries())arrow(xy([xmin-280,y]),xy([xmax+360,y]),i===2?C.blue:C.secondary,i===2?3:1.05,true);
// The longitudinal pedestrian axis remains subordinate to the main crossing.
arrow(xy([xc,ymin-335]),xy([xc,ymax+155]),C.secondary,1.4,true);
// Activity spreads from the exchange area into both neighbourhoods.
// Diverging arrows sit outside the blue connection lines instead of crossing the site.
for(const sign of [-1,1]){
 const origin=[center[0]+sign*36,center[1]+9];
 for(const dy of [-44,44])arrow(origin,[center[0]+sign*124,center[1]+dy],C.orange,1.8,false,'triangle');
}
txt('CONNECT',184,230,128,24,15,C.blue);
txt('교류 거점',center[0]-34,center[1]-23,68,20,12,C.blue,'center');
txt('SPREAD',174,428,104,22,14,C.orange);
txt('SPREAD',458,431,104,22,14,C.orange);
// Destination labels no longer sit on the image crop edge.
txt('북천·황성공원 방면',275,152,178,26,15,C.ink,'center');
txt('대릉원·황리단길 방면',269,574,190,26,15,C.ink,'center');
txt('N',617,156,22,24,15,C.ink,'center');arrow([628,209],[628,183],C.ink,1.3);
// Compact, unboxed legend explicitly explains arrow hierarchy.
arrow([178,627],[207,627],C.blue,3,true);txt('주 연결축',215,615,82,25,13,C.sub);
arrow([307,627],[336,627],C.secondary,1.05,true);txt('보조 연결축',344,615,91,25,13,C.sub);
arrow([453,627],[482,627],C.orange,1.8);txt('주변 확산',490,615,87,25,13,C.sub);
await(await PresentationFile.exportPptx(p)).save(B+'/strategy_overlay.pptx');
console.log('Created editable overlay:',s.shapes.items.length,'shapes');
