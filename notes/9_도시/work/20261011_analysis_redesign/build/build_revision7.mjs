import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const B='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build';
const G=JSON.parse(await fs.readFile(B+'/strategy_metadata.json','utf8'));
const p=Presentation.create({slideSize:{width:12191695/9525,height:720}});p.theme.defaultFont='Pretendard';const s=p.slides.add();
const C={blue:'#235D82',secondary:'#83A9BE',orange:'#B66A2B',ink:'#252C32',sub:'#69747D',line:'#9EA8B0'};let id=0;
const fr={x:58,y:144,w:603,h:502.5},sc=fr.w/(G.extent[2]-G.extent[0]);
const xy=([x,y])=>[fr.x+(x-G.extent[0])*sc,fr.y+(G.extent[3]-y)*sc];
const [xmin,ymin,xmax,ymax]=G.siteBounds,xc=(xmin+xmax)/2,yc=(ymin+ymax)/2,center=xy([xc,yc-40]);
function shape(g,x,y,w,h,fill='none',line='none',lw=0,name='shape'){return s.shapes.add({geometry:g,name:'r7-'+name+'-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:line,width:lw}});}
function txt(v,x,y,w,h=24,size=15,c=C.ink,a='left'){let q=shape('textbox',x,y,w,h);q.text=v;q.text.style={fontSize:size,typeface:'Pretendard',color:c,bold:false,alignment:a,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};return q;}
function poly(ps,fill,line='none',lw=0,name='polygon'){
 const xx=ps.map(a=>a[0]),yy=ps.map(a=>a[1]),x=Math.min(...xx),y=Math.min(...yy),w=Math.max(...xx)-x,h=Math.max(...yy)-y;
 return s.shapes.add({geometry:'custom',name:'r7-'+name+'-'+(++id),position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:line,width:lw},customPaths:[{width:w,height:h,commands:ps.map((a,i)=>({[i?'lineTo':'moveTo']:{x:a[0]-x,y:a[1]-y}})).concat([{close:{}}])}]});
}
function grad(angle,stops){return {type:'gradient',gradientKind:'linear',angleDeg:angle,stops:stops.map(([offset,color])=>({offset:offset*100000,color}))};}
const blueGrad=angle=>grad(angle,[[0,'#83A9BE/55'],[.24,'#427C9F/90'],[.5,C.blue],[.76,'#427C9F/90'],[1,'#83A9BE/55']]);
const softGrad=angle=>grad(angle,[[0,'#83A9BE/40'],[.35,'#5085A5/80'],[.65,'#5085A5/80'],[1,'#83A9BE/40']]);
function ribbon(a,b,width,fill,name,head=12){
 const dx=b[0]-a[0],dy=b[1]-a[1],L=Math.hypot(dx,dy),ux=dx/L,uy=dy/L,nx=-uy,ny=ux,h=width/2,hh=width*.95;
 const at=(d,o)=>[a[0]+ux*d+nx*o,a[1]+uy*d+ny*o];
 return poly([at(0,0),at(head,-hh),at(head,-h),at(L-head,-h),at(L-head,-hh),at(L,0),at(L-head,hh),at(L-head,h),at(head,h),at(head,hh)],fill,'none',0,name);
}
function fan(origin,sign,radius=141,deg=35,name='spread'){
 const ps=[origin];
 for(let j=0;j<=32;j++){let a=(-deg+2*deg*j/32)*Math.PI/180;ps.push([origin[0]+sign*radius*Math.cos(a),origin[1]+radius*Math.sin(a)]);}
 return poly(ps,grad(0,sign>0?[[0,'#B66A2B/66'],[.3,'#CC9055/42'],[.72,'#DDB992/18'],[1,'#DDB992/0']]:[[0,'#DDB992/0'],[.28,'#DDB992/18'],[.7,'#CC9055/42'],[1,'#B66A2B/66']]),'none',0,name);
}
// Background map is retained from the source slide. The site and diagram remain native.
poly(G.zone.map(xy),'#E1EBF1',C.blue,1.25,'site-boundary');
for(const key of ['G_seongdong_market_r200','B_haengbok_hwangchon_digitized','H_hwangridan_r300']){
 const [x,y]=xy(G.centers[key]);shape('ellipse',x-30,y-30,60,60,'none','#B6BDC3',.65,'neighbourhood');
}
fan([center[0]-28,center[1]],-1);fan([center[0]+28,center[1]],1);
// Four secondary crossings use the same gradient, with less width than the main axis.
for(const y of [ymax-120,ymax-300,ymin+280,ymin+120])ribbon(xy([xmin-280,y]),xy([xmax+360,y]),4.5,softGrad(0),'secondary-connection',9);
// Thick continuous axes show connection and the intersection as a single spatial system.
ribbon(xy([xc,ymin-335]),xy([xc,ymax+155]),8,blueGrad(90),'north-south-connection',13);
ribbon(xy([xmin-280,yc-40]),xy([xmax+360,yc-40]),11,blueGrad(0),'east-west-connection',14);
// The crossing is identified by an open ring: no opaque label box over the diagram.
shape('ellipse',center[0]-26,center[1]-26,52,52,'none',C.blue,1.8,'intersection-ring');
shape('ellipse',center[0]-5,center[1]-5,10,10,C.blue,'#FFFFFF',1.8,'intersection');
txt('연결',183,229,116,27,17,C.blue);
txt('교차',center[0]+33,center[1]-31,69,25,17,C.blue);
txt('확산',190,453,75,25,17,C.orange);txt('확산',481,453,75,25,17,C.orange);
txt('성동시장',156,373,105,26,15,C.ink);txt('행복황촌',505,373,105,26,15,C.ink);
const hp=xy(G.centers.H_hwangridan_r300);txt('황리단길',hp[0]-53,hp[1]+33,93,24,15,C.ink);
txt('북천·황성공원 방면',275,152,178,26,15,C.ink,'center');
txt('대릉원·황리단길 방면',269,574,190,26,15,C.ink,'center');
txt('N',617,156,22,24,15,C.ink,'center');
shape('rect',627.4,186,1.2,23,C.ink);poly([[628,182],[624,190],[632,190]],C.ink);
// Match the legend to the new visual vocabulary.
ribbon([161,627],[198,627],7,blueGrad(0),'legend-connection',7);txt('연결축',209,614,84,26,13,C.sub);
shape('ellipse',319,618,18,18,'none',C.blue,1.1,'legend-intersection');shape('rect',318,625,20,4,C.blue);shape('rect',326,617,4,20,C.blue);txt('교차 거점',347,614,98,26,13,C.sub);
fan([463,627],1,32,28,'legend-spread');txt('주변 확산',503,614,91,26,13,C.sub);
await(await PresentationFile.exportPptx(p)).save(B+'/revision7_overlay.pptx');
console.log('Created native gradient connections and fan-shaped spread.');
