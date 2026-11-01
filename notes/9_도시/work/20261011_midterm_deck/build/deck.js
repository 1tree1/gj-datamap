// 구 경주역 도시재생 마스터플랜 — 중간마감 발표자료(1~4부, 45장) 빌드 스크립트
// 실행: node deck.js  → ../output/구경주역_중간마감_1-4부_v1.pptx
const NM='C:/Users/OFFICE/Desktop/9_도시/work/20261011_visual_front/build/node_modules';
const pptxgen=require(NM+'/pptxgenjs'); const sharp=require(NM+'/sharp'); const fs=require('fs');
const R='C:/Users/OFFICE/Desktop/9_도시';
const A=__dirname+'/assets', PH=R+'/work/20261008_presentation_front/assets/photos', AZ=R+'/work/20261011_azimuth_white/azimuth_distribution_white.png';
const EV=JSON.parse(fs.readFileSync(R+'/work/20261011_visual_front/build/evidence.json','utf8'));
const KO='맑은 고딕', NUM='Courier New';
const RED='C8102E', DARK='8A0A1F', INK='1A1A1A', G1='F2F2F2', G2='D9D9D9', G3='9A9A9A', G4='5C5C5C', WH='FFFFFF', PINK='F7D9DD', PINK2='E9909C';
const pres=new pptxgen(); pres.defineLayout({name:'W',width:13.333,height:7.5}); pres.layout='W';
pres.author='이승규 · 김민승'; pres.title='구 경주역 도시재생 마스터플랜 중간마감(1~4부)';
let page=0;
// ---------- 기본 도구 ----------
function T(s,text,x,y,w,h,o={}){s.addText(text,{x,y,w,h,fontFace:o.num?NUM:KO,fontSize:o.size||11,color:o.color||INK,bold:!!o.bold,align:o.align||'left',valign:o.valign||'top',margin:0,isTextBox:true,lineSpacingMultiple:o.ls||1.2,paraSpaceAfter:o.psa||0,fit:'none'});}
function RUNS(s,runs,x,y,w,h,o={}){s.addText(runs.map(r=>({text:r.t,options:{fontFace:r.num?NUM:KO,fontSize:r.size||o.size||11,color:r.color||o.color||INK,bold:!!r.bold,breakLine:!!r.br}})),{x,y,w,h,align:o.align||'left',valign:o.valign||'top',margin:0,isTextBox:true,lineSpacingMultiple:o.ls||1.2,paraSpaceAfter:o.psa||0});}
function rect(s,x,y,w,h,fill,line){const o={x,y,w,h,fill:{color:fill}}; if(line) o.line={color:line.color||G2,width:line.width||0.75,dashType:line.dash||'solid'}; else o.line={color:fill,width:0}; s.addShape(pres.ShapeType.rect,o);}
function ln(s,x1,y1,x2,y2,color=G2,width=0.75,arrow=false,dash='solid'){const o={x:Math.min(x1,x2),y:Math.min(y1,y2),w:Math.abs(x2-x1)||0.001,h:Math.abs(y2-y1)||0.001,line:{color,width,dashType:dash}}; if(arrow) o.line.endArrowType='triangle'; if(x2<x1) o.flipH=true; if(y2<y1) o.flipV=true; s.addShape(pres.ShapeType.line,o);}
async function img(s,file,x,y,w,h,mode='contain',align='center'){
  if(mode==='cover'){s.addImage({path:file,x,y,w,h,sizing:{type:'cover',w,h}});return {x,y,w,h};}
  const m=await sharp(file).metadata(); const r=m.width/m.height; let ww=w,hh=w/r; if(hh>h){hh=h;ww=h*r;}
  const xx=align==='left'?x:(align==='right'?x+w-ww:x+(w-ww)/2), yy=align==='top'?y:y+(h-hh)/2;
  s.addImage({path:file,x:xx,y:yy,w:ww,h:hh}); return {x:xx,y:yy,w:ww,h:hh};
}
function cap(s,text,x,y,w,h=0.3){T(s,text,x,y,w,h,{size:9.5,color:G4,ls:1.15});}
function label(s,text,x,y,w){T(s,text,x,y,w,0.28,{size:11,bold:true,color:RED});}
function stat(s,val,unit,desc,x,y,w,o={}){RUNS(s,[{t:val,num:true,size:o.size||30,bold:true,color:o.color||RED},{t:unit?' '+unit:'',size:(o.size||30)*0.45,bold:true,color:o.color||RED}],x,y,w,(o.size||30)/72*1.55,{valign:'bottom'}); T(s,desc,x,y+(o.size||30)/72*1.6,w,0.5,{size:o.dsize||10.5,color:G4,ls:1.15});}
function head(s,lbl,title){label(s,lbl,0.5,0.34,10); T(s,title,0.5,0.6,12.3,0.62,{size:27,bold:true}); page++; T(s,String(page).padStart(2,'0'),12.33,7.08,0.5,0.25,{size:10,color:G3,num:true,align:'right'});}
function slide(lbl,title,notes){const s=pres.addSlide(); s.background={color:WH}; head(s,lbl,title); if(notes) s.addNotes(notes); return s;}
function divider(no,title,sub){const s=pres.addSlide(); s.background={color:INK}; page++; T(s,no,0.8,2.0,4,1.5,{size:72,bold:true,color:RED,num:true}); T(s,title,0.8,3.55,11.5,0.9,{size:36,bold:true,color:WH}); T(s,sub,0.8,4.55,11.5,0.9,{size:13,color:G3,ls:1.3}); T(s,String(page).padStart(2,'0'),12.33,7.08,0.5,0.25,{size:10,color:G4,num:true,align:'right'}); return s;}
function bullets(s,items,x,y,w,h,o={}){s.addText(items.map((t,i)=>({text:t,options:{bullet:{indent:12},breakLine:i<items.length-1}})),{x,y,w,h,fontFace:KO,fontSize:o.size||11,color:o.color||INK,margin:0,isTextBox:true,valign:'top',lineSpacingMultiple:1.2,paraSpaceAfter:o.psa||4});}
const CH={catAxisLabelFontFace:KO,catAxisLabelFontSize:10,catAxisLabelColor:INK,valAxisLabelFontFace:NUM,valAxisLabelFontSize:9,valAxisLabelColor:G4,dataLabelFontFace:NUM,dataLabelFontSize:10,dataLabelColor:INK,legendFontFace:KO,legendFontSize:9.5,legendColor:INK,titleFontFace:KO,titleFontSize:11,titleColor:INK,titleAlign:'left',catGridLine:{style:'none'},valGridLine:{style:'none'}};
function barH(s,cats,vals,x,y,w,h,o={}){s.addChart(pres.ChartType.bar,[{name:o.name||'값',labels:cats,values:vals}],{x,y,w,h,barDir:'bar',chartColors:[o.color||RED],showValue:true,dataLabelPosition:'outEnd',dataLabelFormatCode:o.fmt||'#,##0',catAxisOrientation:'maxMin',catAxisLabelPos:'low',valAxisHidden:true,valAxisMinVal:o.min??0,valAxisMaxVal:o.max,showLegend:false,barGapWidthPct:o.gap||40,showTitle:!!o.title,title:o.title||'',...CH});}
function colG(s,cats,series,x,y,w,h,o={}){s.addChart(pres.ChartType.bar,series.map(sr=>({name:sr.name,labels:cats,values:sr.values})),{x,y,w,h,barDir:'col',barGrouping:'clustered',chartColors:o.colors||[G3,RED],showValue:!!o.labels,dataLabelPosition:'outEnd',dataLabelFormatCode:o.fmt||'#,##0',dataLabelFontSize:8.5,valAxisHidden:!o.axis,valAxisMinVal:o.min??0,valAxisMaxVal:o.max,showLegend:true,legendPos:'b',barGapWidthPct:o.gap||60,showTitle:!!o.title,title:o.title||'',...CH,valGridLine:o.axis?{color:'E6E6E6',size:0.5}:{style:'none'}});}
function lineC(s,cats,series,x,y,w,h,o={}){s.addChart(pres.ChartType.line,series.map(sr=>({name:sr.name,labels:cats,values:sr.values})),{x,y,w,h,chartColors:o.colors||[RED,DARK,'E05A6E',G4,G3],lineSize:2,lineDataSymbol:'circle',lineDataSymbolSize:5,showValue:false,valAxisMinVal:o.min,valAxisMaxVal:o.max,valAxisMajorUnit:o.unit,showLegend:true,legendPos:'b',showTitle:!!o.title,title:o.title||'',...CH,valGridLine:{color:'E6E6E6',size:0.5},catAxisLabelFontFace:NUM,catAxisLabelFontSize:9});}
function donut(s,labels,vals,x,y,w,h,o={}){s.addChart(pres.ChartType.doughnut,[{name:o.name||'구성비',labels,values:vals}],{x,y,w,h,holeSize:55,chartColors:o.colors||[DARK,RED,'E05A6E','F0A0AD',G4,G3],showPercent:true,showValue:false,showLabel:false,dataLabelColor:WH,dataLabelFontFace:NUM,dataLabelFontSize:9,showLegend:true,legendPos:o.legend||'r',legendFontFace:KO,legendFontSize:9.5,showTitle:!!o.title,title:o.title||'',titleFontFace:KO,titleFontSize:11,titleColor:INK});}
function table(s,rows,x,y,w,colW,o={}){const size=o.size||10; const body=rows.map((r,ri)=>r.map((c,ci)=>{const cell=typeof c==='object'&&c!==null&&!Array.isArray(c)?{...c}:{text:String(c)}; cell.options={fontFace:cell.num?NUM:KO,fontSize:size,color:INK,valign:'middle',align:(cell.align||(ci>0&&o.numCols&&o.numCols.includes(ci)?'right':'left')),margin:[3,5,3,5],...(cell.options||{})}; if(ri===0&&!o.noHead){cell.options.bold=true;cell.options.fill={color:G1};cell.options.color=G4;} if(cell.fill)cell.options.fill={color:cell.fill}; if(cell.bold)cell.options.bold=true; if(cell.color)cell.options.color=cell.color; return cell;})); s.addTable(body,{x,y,w,colW,border:{type:'solid',pt:0.5,color:G2},rowH:o.rowH||0.3,autoPage:false});}
const SRC=(s,t)=>cap(s,t,0.5,6.88,12.3,0.25);
// ---------- 데이터 ----------
const pop=n=>EV.population.find(p=>p.hadm===n); const Y=['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025'];
const idx=n=>{const p=pop(n); const b=p.yearly['2015']; return Y.map(y=>Math.round(p.yearly[y]/b*1000)/10);};
const CITY=[255301,254667,253480,252329,250956,249175,251889,249607,247489,244769,244055]; const cityIdx=CITY.map(v=>Math.round(v/CITY[0]*1000)/10);
const mig=EV.youth.net;
(async()=>{
// 01 표지
{const s=pres.addSlide(); s.background={color:INK}; page++;
 await img(s,A+'/cover_outline.png',6.9,0,6.433,7.5,'cover');
 T(s,'건축디자인 6  STUDIO B  ·  중간마감  2026.10.12',0.7,0.75,6,0.3,{size:11,color:RED,bold:true});
 T(s,'구 경주역\n도시재생 마스터플랜',0.7,1.6,6,2.2,{size:40,bold:true,color:WH,ls:1.15});
 T(s,'폐역 부지의 재생 방향과 프로그램·규모 계획\n1부 대상지 개요와 현황  ·  2부 경주 도시의 특징과 문제\n3부 해결 컨셉과 프로그램  ·  4부 대상 인구와 개발 규모',0.7,4.0,6,1.3,{size:13,color:G3,ls:1.35});
 T(s,'2019113133 이승규  ·  2021113994 김민승\n김아름 교수님',0.7,6.3,6,0.7,{size:11,color:G3,ls:1.3});
 cap(s,'정사영상 2025(국토지리정보원) · 붉은 선 = 본 계획 경계(최종, 라이노)',7.1,7.1,6,0.3);}
// 02 목차
{const s=pres.addSlide(); s.background={color:INK}; page++;
 T(s,'발표 구성',0.8,0.6,6,0.6,{size:27,bold:true,color:WH});
 const items=[['01','대상지 개요와 현황','위치 · 면적 · 철도의 역사 · 현장 · 상위계획 · 데이터 기반 사이트 분석(입지·동서·남북·소통·규제·유산·조직·노후)','03'],['02','경주 도시의 특징과 문제','인구 · 고령화·청년 · 순이동 · 방문과 체류 · 야간 활동 · 업종 변화 · 문제 종합 · 목표','19'],['03','해결 컨셉과 프로그램','컨셉 위계 · 전략의 공간 배치 · 성립 조건 · 선례 · 프로그램 선정과 앵커 · 권역과 세부 프로그램','28'],['04','대상 인구와 개발 규모','이용자 가정 · 방문·근로·정주 인구 산정 · 산정 방법 · 프로그램별 면적 · 개발규모 산정표 · 규제 정합','39'],['05','마스터플랜 · 단면 조닝 · 3D 볼륨','별도 작성분(배치 구상안 · 긴 방향 단면 · 모델링 컷)','—']];
 items.forEach((it,i)=>{const y=1.7+i*1.0; const dim=i===4; T(s,it[0],0.8,y,1.0,0.6,{size:26,bold:true,color:dim?G4:RED,num:true}); T(s,it[1],1.9,y+0.02,7.5,0.45,{size:18,bold:true,color:dim?G4:WH}); T(s,it[2],1.9,y+0.45,9.3,0.4,{size:10.5,color:dim?G4:G3}); T(s,it[3],11.6,y+0.05,1.1,0.5,{size:16,color:dim?G4:G3,num:true,align:'right'}); ln(s,0.8,y+0.9,12.5,y+0.9,'3A3A3A',0.5);});}
// 03 구분
divider('01','대상지 개요와 현황','구 경주역 폐역 부지의 위치·면적·역사·현장과 상위계획, 데이터로 읽은 사이트의 조건');
// 04 대상지 위치
{const s=slide('대상지 개요 : 위치','원도심과 폐선축 위의 대상지','구 경주역 폐역 부지는 경주시 성동동 일원(원화로 266)이며, 2021년 12월 동해선 이설로 폐역되었다. 폐선축 80.3km·폐역 17개소는 2023.04 경주시 폐철도 기본구상 값으로 원문 대조 전이다. 본 계획은 기존 지구단위계획 결정과 무관하게 경계·용도를 새로 설정한다.');
 await img(s,A+'/rail_axis.png',0.5,1.4,6.6,5.2,'contain','left');
 label(s,'위치',7.6,1.45,5); T(s,'경상북도 경주시 성동동 일원(원화로 266)',7.6,1.75,5.2,0.35,{size:12,bold:true});
 T(s,'원도심 4개 동(황오·황남·월성·성건) 생활권의 한가운데, 성동시장과 행복황촌 사이에 남북으로 긴 폐역 부지가 놓여 있습니다.',7.6,2.12,5.2,0.75,{size:11,color:G4});
 stat(s,'2021.12','','동해선 이설에 따른 폐역  [T1]',7.6,3.05,2.6,{size:22,color:INK});
 stat(s,'80.3','km','폐선축 길이 · 폐역 17개소  [T2, 2023 폐철도 기본구상 · 원문 대조 전]',10.2,3.05,2.8,{size:22,color:INK});
 ln(s,7.6,4.45,12.83,4.45);
 label(s,'면적 기준',7.6,4.6,5);
 const rows=[['시 구상 · 1단계','79,438㎡','경주시 보도자료  [T2, 범위 미정의]'],['본 계획 경계(최종)','228,025㎡','라이노 계획 합집합 측정 · 남북 948 m × 동서 311 m'],['이전 분석 경계','218,478㎡','2026.10.05 경계 · 접속점·우회율 산정 기준']];
 rows.forEach((r,i)=>{const y=4.95+i*0.55; T(s,r[0],7.6,y,1.9,0.3,{size:10.5,color:G4}); T(s,r[1],9.5,y-0.05,1.6,0.35,{size:14,bold:true,num:true,color:i===1?RED:INK}); T(s,r[2],11.0,y,1.9,0.5,{size:9,color:G4,ls:1.1});});
 SRC(s,'지도: NGII 행정경계·OSM 철도(2026.09) · 폐선(점선)은 2021.12 이설 이후 · 폐역 위치 확인 3개소');}
// 05 대상지 개요
{const s=slide('대상지 개요 : 현황','폐역 부지의 규모와 소유','소유 비율은 2021년 보고(148,770㎡ 범위) 기준이며 최신 등기자료가 아니다. 구 역사는 국가등록문화유산이 아니라 코레일 철도기념물(2013)이다.');
 await img(s,PH+'/ph65_site_from_west_roof_wide.jpg',0.5,1.4,7.0,4.2,'cover'); cap(s,'서측 건물 옥상에서 본 폐역 부지(2026.09 답사)',0.5,5.65,7,0.3);
 await img(s,PH+'/ph57_site_tracks_south.jpg',0.5,6.0,3.45,0.85,'cover'); await img(s,PH+'/ph59_site_remnants_ne.jpg',4.05,6.0,3.45,0.85,'cover');
 label(s,'규모',8.0,1.45,4.8);
 stat(s,'228,025','㎡','본 계획 경계 · 남북 948 m × 동서 311 m · 둘레 2,369 m',8.0,1.75,4.8,{size:30});
 const bars=[['시 구상 1단계',79438,'[T2]'],['이전 분석 경계',218478,'2026.10.05'],['본 계획 경계',228025,'최종']];
 bars.forEach((b,i)=>{const y=3.0+i*0.5; T(s,b[0],8.0,y,1.5,0.3,{size:10,color:G4}); rect(s,9.5,y+0.03,2.1*b[1]/228025,0.24,i===2?RED:(i===1?G4:G3)); T(s,b[1].toLocaleString()+'㎡ '+b[2],9.5+2.1*b[1]/228025+0.08,y,1.6,0.3,{size:9.5,num:true,color:INK});});
 ln(s,8.0,4.55,12.83,4.55);
 label(s,'소유와 구 역사',8.0,4.7,4.8);
 RUNS(s,[{t:'코레일 53.0% · 국가철도공단 46.9%',bold:true,size:11.5,br:true},{t:'2021년 보고 기준(철도 부지 148,770㎡), 최신 등기자료 아님  [T1]',size:9.5,color:G4,br:true},{t:' ',size:6,br:true},{t:'구 역사  1936년 현 위치 이전 · 1,404㎡ × 2층',bold:true,size:11.5,br:true},{t:'코레일 철도기념물(2013) · 현 경주문화관 1918 · 국가등록문화유산 아님  [T1]',size:9.5,color:G4,br:true},{t:' ',size:6,br:true},{t:'본 계획 경계는 라이노 획지·도로·보도 합집합이며 접속점·우회율은 이전 경계 기준입니다.',size:10.5,color:INK}],8.0,5.0,4.8,1.9);
 SRC(s,'경주시 도시재생 전략계획(변경, 2022) · 라이노 계획 프레임 측정(2026.10.11)');}
// 06 철도의 역사
{const s=slide('대상지 개요 : 역사','철도의 역사와 부지의 변화','1918.12.28 사정동 개업(관보 운수개시 인가). 1936.12.01 성동동 현 위치 이전. 1939.06 노선 변경(김신재 2013). 2010.11.01 KTX 신경주역 개통. 2021.12.28 폐역. 1954 항공사진은 잔존 가로 교차점 기준 근사 정합이며 정밀도 주장 없음.');
 const ev=[['1918','사정동 개업  [T1]'],['1936','성동동 현 위치 이전  [T1]'],['1939','노선 변경  [T3]'],['2010','KTX 신경주역 개통  [T1]'],['2021','구 경주역 폐역  [T1]']];
 ev.forEach(([y,t],i)=>{const x=0.5+i*2.5; T(s,y,x,1.4,2.2,0.5,{size:24,bold:true,color:RED,num:true}); ln(s,x,1.95,x+2.2,1.95,INK,1); T(s,t,x,2.02,2.3,0.35,{size:10.5});});
 for(const [i,[yr,f,t]] of [[0,'aerial_1954','1954  철도 운영기 · 근사 정합'],[1,'aerial_2009','2009  KTX 개통 전'],[2,'aerial_2025','2025  폐역 이후']].entries()){const x=0.5+i*4.2; await img(s,A+`/${f}.jpg`,x,2.6,3.9,3.9,'cover'); T(s,t,x,6.55,3.9,0.3,{size:10.5,bold:true});}
 SRC(s,'국토지리정보원 항공사진(1954·2009)·정사영상(2025) 동일 좌표창 · 국토교통부·국가철도공단 · 김신재(2013) pp.387–388');}
// 07 현장 사진
{const s=slide('대상지 개요 : 현장','현장 답사 기록','2026.09 답사. 폐선로·잔존 시설·보행 육교·울타리·서측 상업가로·동측 골목.');
 const ph=[['ph57_site_tracks_south','폐선로 남측 · 노반과 잔존 선로'],['ph58_site_tracks_north','폐선로 북측 · 수목이 덮은 노반'],['ph56_site_overpass','보행 육교 · 폭 3.2 m, 유일한 횡단 시설'],['ph63_site_fence_structure','부지 경계 울타리 · 가로에서 차단'],['ph00_west_wonhwaro_walk','서측 원화로 · 상업가로'],['ph62_east_lane_paved','동측 행복황촌 골목 · 저층 주거']];
 for(const [i,[f,t]] of ph.entries()){const x=0.5+(i%3)*4.2, y=1.4+Math.floor(i/3)*2.75; await img(s,PH+`/${f}.jpg`,x,y,3.9,2.25,'cover'); T(s,t,x,y+2.3,3.9,0.3,{size:10.5});}
 SRC(s,'현장 사진(2026.09) · 육교 개방 여부와 울타리 개구부는 현장 재확인 필요');}
// 08 상위계획과 시 구상
{const s=slide('대상지 개요 : 상위계획','상위계획과 경주시 구상','2030 기본계획·전략계획(2022)의 경주역 부지 서술과 시 구상(2026.02). 3,822억·국비 250억은 언론 경유 T4. 1단계 79,438㎡ 구성은 김권일 발표자료(2026) 기준. 본 계획은 기존 지구단위계획 결정과 무관하게 수립한다.');
 label(s,'상위계획  [T1]',0.5,1.45,5.5);
 const up=[['2030 경주도시기본계획','시가지(원도심)권 도시재생 추진방안에 "경주역 중심의 경제활성화" · 기존 시가지는 철도와 사적지구로 동서·남북 분리(인쇄쪽 285) · 도심–보문 신교통의 원도심 경유'],['경주시 도시재생 전략계획 (변경, 2022)','경주역부지 개발 148,770㎡(2019–2028) · 공공청사·상징광장·문화·공원·복합상업·커뮤니티 · 복합환승센터 · 선로로 단절된 도시공간을 잇는 매개공간(인쇄쪽 161) · 첫째 목표 "주민의 힘으로 이끌어가는 삶터"'],['도시재생 혁신지구 가이드라인','기능 2개 이상 집적(산업·주거·문화·생활SOC) · 쇠퇴 3지표 중 2개 · 면적 200만㎡ 이하 · 계획서에 이용인구·수요 추정과 운영 주체 필수 · 공공청사는 국비 대상 제외  [T2]']];
 up.forEach((u,i)=>{const y=1.8+i*1.25; rect(s,0.5,y,0.12,1.05,i<2?RED:G4); T(s,u[0],0.75,y,6.6,0.3,{size:11.5,bold:true}); T(s,u[1],0.75,y+0.32,6.6,0.75,{size:10,color:G4,ls:1.25});});
 label(s,'경주시 구상 (2026.02)  [T2·T4]',7.9,1.45,4.9);
 const prog=[['K-헤리티지 복합거점','구 역사·전시·공연·체험'],['미래모빌리티 통합허브','복합환승·주차·신교통'],['경주 STAY','체류·숙박·상업']];
 prog.forEach((p,i)=>{const y=1.8+i*0.62; rect(s,7.9,y,0.12,0.5,RED); T(s,p[0],8.1,y,4.7,0.28,{size:11.5,bold:true}); T(s,p[1],8.1,y+0.27,4.7,0.25,{size:9.5,color:G4});});
 ln(s,7.9,3.75,12.83,3.75);
 stat(s,'3,822','억 원','구상 사업비 · 국비 250억 원  [T4, 원문 미확인]',7.9,3.85,2.4,{size:20,color:INK,dsize:9.5});
 stat(s,'79,438','㎡','1단계 범위 · 준주거 20,262 · 상업 17,819 · 문화 12,260 · 도로 19,643 · 공원 9,454  [T2]',10.3,3.85,2.5,{size:20,color:INK,dsize:9.5});
 label(s,'절차',0.5,5.6,4);
 bullets(s,['2026.01  경주시–국가철도공단 MOU(도시재생 혁신지구 공모 협력)  [T4]   ·   2026 하반기  국토교통부 도시재생 혁신지구 공모 예정  [T4]','시 구상 2단계  민자 유치(시청 이전 포함) · 공공청사는 국비 대상 제외  [T2]'],0.5,5.95,12.3,0.9,{size:10.5});
 SRC(s,'2030 경주도시기본계획(승인) · 경주시 도시재생 전략계획(변경, 2022) · 김권일 발표자료(2026) · 도시재생 혁신지구 가이드라인 · 경주시 보도자료(2026.02)');}
// 09 분석의 틀
{const s=slide('사이트 분석 : 방법','현황 분석의 틀','세 스케일(S1·S2·S3)을 분리하고, 자료마다 출처 등급(T1~T4)을 붙였다. S3 통계로 S1 규모를 정당화하지 않는다.');
 const sc=[['S1  SITE','부지 228,025㎡','PNU 19자리 · 라이노 계획 좌표 → EPSG:5187','라이노 계획 경계·획지 · 매장유산 조사 · 접속 가로 · 필지·건축물대장 · 고도지구'],['S2  DISTRICT','원도심 보행권 반경 1 km','집계구 · 행정동 · H3 r8','유동인구(소상공인365) · 상가 업소 · 공시지가 · ITS 소통 · 시민 설문'],['S3  CITY','경주시 전역 + 폐선축 80.3 km','법정동 10자리 · H3 r7','주민등록 인구·순이동(KOSIS) · 관광데이터랩 방문자 · 상위계획 · 관광실태조사']];
 sc.forEach((c,i)=>{const x=0.5+i*4.2; rect(s,x,1.45,3.9,2.65,G1); T(s,c[0],x+0.2,1.6,3.5,0.35,{size:14,bold:true,color:RED,num:true}); T(s,c[1],x+0.2,1.98,3.5,0.3,{size:12,bold:true}); T(s,'조인 키  '+c[2],x+0.2,2.32,3.5,0.3,{size:9.5,color:G4}); T(s,c[3],x+0.2,2.75,3.5,1.3,{size:10.5,ls:1.3});});
 label(s,'출처 등급',0.5,4.35,4);
 const tg=[['T1','법정문서','법령 · 조례 · 고시 · 승인계획 · 협약'],['T2','공공발간·통계','용역보고서 · 국책연구 · 통계 원자료 · 공공 API'],['T3','학술','논문 · 학술 보고서'],['T4','언론·2차자료','보도자료 · 기사 — 배경 설명에만 사용']];
 tg.forEach((t,i)=>{const x=0.5+i*3.1; rect(s,x,4.7,0.75,0.45,i<2?RED:G4); T(s,t[0],x,4.7,0.75,0.45,{size:13,bold:true,color:WH,num:true,align:'center',valign:'middle'}); T(s,t[1],x+0.9,4.7,2.1,0.25,{size:11,bold:true}); T(s,t[2],x+0.9,4.95,2.15,0.5,{size:9,color:G4,ls:1.15});});
 ln(s,0.5,5.6,12.83,5.6);
 bullets(s,['규제는 용도지역·고도지구·역사문화환경 보존지역·지구단위계획 4겹에 신라왕경 특별법·세계유산 완충구역을 더해 중첩해서 봅니다.','수치는 출처 등급과 함께 쓰고, 원문 확인 전 수치에는 [원문 미확인]을 붙입니다.','통신 기반 추정 유동은 보행량이 아니며 거주·직장 인구를 포함하므로 상한 성격으로 읽습니다.'],0.5,5.75,12.3,1.1,{size:10.5});}
// 10 입지
{const s=slide('사이트 분석 : 입지','입지와 주변 자산의 거리','거리는 OSM 구 경주역 점 기준 직선(건물 중심 기준이면 6~16% 길어짐). 북천은 경계 북단에 접하고 황성공원은 북단에서 약 509m. 걷기 5·10·15분 = 335·670·1,005m.');
 await img(s,A+'/location_base.png',0.5,1.35,5.5,5.5,'contain','left');
 label(s,'구 경주역 기준 주요 자산까지 직선거리 (m)  [T2 자체 산출]',6.4,1.45,6.4);
 barH(s,['성동시장','경주읍성','대릉원','동궁과 월지','황리단길','첨성대'],[355,497,523,920,994,1030],6.4,1.75,6.4,2.9,{max:1250});
 const dir=[['서','성동시장 · 상업가로 · 원화로'],['동','행복황촌 · 저층 주거 골목'],['남','대릉원 · 황리단길 · 첨성대 · 동궁과 월지'],['북','북천 · 황성공원(약 509 m) · 성건동 생활권']];
 dir.forEach((d,i)=>{const y=4.85+i*0.47; rect(s,6.4,y,0.42,0.38,i===2?RED:INK); T(s,d[0],6.4,y,0.42,0.38,{size:12,bold:true,color:WH,align:'center',valign:'middle'}); T(s,d[1],6.95,y+0.05,5.8,0.3,{size:11});});
 SRC(s,'NGII 도로·UPIS 공원·OSM 폐선 · 원 = 직선 반경 500 / 1,000 m · 걷기 5·10·15분 = 335·670·1,005 m');}
// 11 동서 횡단 조건
{const s=slide('사이트 분석 : 동서 ①','동서 횡단 조건','985m는 도로중심선 교차가 없는 최대 구간. 보행육교 1개(폭 3.2m, 길이 216.3m). 우회율 3.5는 폐선 양쪽 60m 지점 간 도로 경로/직선(육교 제외). 접속점 37곳은 이전 경계(218,478㎡) 기준이며 최종 경계 재산정 전.');
 await img(s,A+'/crossing_map.png',0.5,1.35,3.7,5.45,'contain','left');
 await img(s,PH+'/ph56_site_overpass.jpg',4.5,1.4,2.55,1.85,'cover'); await img(s,PH+'/ph63_site_fence_structure.jpg',7.2,1.4,2.55,1.85,'cover');
 T(s,'보행 육교',4.5,3.3,2.55,0.3,{size:10.5,bold:true}); T(s,'부지 경계 울타리',7.2,3.3,2.55,0.3,{size:10.5,bold:true});
 stat(s,'985','m','도로 횡단이 없는 구간  [T2 자체 분석]',10.0,1.4,2.8,{size:34});
 stat(s,'1','개','보행 육교 · 폭 3.2 m · 길이 216 m',10.0,2.75,2.8,{size:26,color:INK});
 stat(s,'3.5','배','동서 이동 시 보행 우회율(직선 대비)',4.5,3.9,2.6,{size:26,color:INK});
 stat(s,'37','곳','부지에 닿는 도로 끝(서 9 · 동 18 · 남 7 · 북 3)',7.2,3.9,2.6,{size:26,color:INK});
 rect(s,10.0,3.95,2.8,2.2,G1);
 T(s,'계획서의 진단',10.15,4.05,2.5,0.3,{size:10.5,bold:true,color:RED});
 T(s,'기존 시가지는 철도와 사적지구로 동서·남북이 분리되어 있습니다.  [T1, 2030 기본계획 인쇄쪽 285]\n\n철도 부지가 경계공백지대로 작동해 보행 단절과 인접 구역 쇠퇴를 유발합니다.  [T2, 원도심 미래구상 기획연구 2025]',10.15,4.4,2.55,1.75,{size:9.5,ls:1.25});
 T(s,'본 계획은 횡단 가로의 개소 수가 아니라 연속성과 가장 약한 지점의 통과 폭으로 연결을 측정합니다.',4.5,6.3,8.3,0.5,{size:11,bold:true});
 SRC(s,'NGII 도로중심선·보행육교 도형 · 현장 사진(2026.09) · 접속점·우회율은 이전 경계 기준');}
// 12 동서 유동인구 격차
{const s=slide('사이트 분석 : 동서 ②','동서 유동인구와 생활업종의 격차','13개월 통신 기반 추정 유동의 면적당 값. 성동시장 200m 1,174.6명/ha, 행복황촌 근사구역 80.3명/ha(14.6배), 폐역 구역 79.3명/ha. 구역 면적이 다르고 일부 겹치므로 합산 금지. 생활업종 비율은 11개 업종 표본(2026.06).');
 await img(s,A+'/footfall_density.png',0.5,1.35,6.3,5.1,'contain','left');
 label(s,'일평균 추정 유동 밀도 (명/ha)  [T2]',7.2,1.45,5.6);
 barH(s,['성동시장 200 m','행복황촌(근사)','폐역 구역'],[1174.6,80.3,79.3],7.2,1.75,5.6,1.9,{fmt:'#,##0.0',max:1400});
 label(s,'생활업종 비율 (%)  [T2, 11개 업종 표본 2026.06]',7.2,3.75,5.6);
 barH(s,['성동시장 (72 / 82개)','행복황촌 (15 / 44개)'],[87.8,34.1],7.2,4.05,5.6,1.4,{fmt:'0.0',max:100,color:G4});
 stat(s,'14.6','배','성동시장과 행복황촌의 유동 밀도 차이',7.2,5.55,2.6,{size:26});
 T(s,'서측 시장 상권과 동측 체류·생활권은 역할이 다릅니다. 동서 연결은 각 역할을 유지한 채 이어지는 방식이어야 합니다.',10.0,5.6,2.83,1.2,{size:10.5,ls:1.25});
 SRC(s,'소상공인365 2025.06–2026.06 월평균 · 통신 기반 추정, 보행량 아님 · 원 면적 ∝ 명/ha · 붉은 면 = 본 계획 경계');}
// 13 남북 관계
{const s=slide('사이트 분석 : 남북','남북 관계: 관광 집중과 북측 생활권','황리단길 반경 300m 13개월 평균 21,403명/일(757명/ha), 주말/주중 1.72. 시청 500m 0.88. 관광객 불편 1위 교통혼잡(주차시설) 29.6%(n=3,009). 북측=성건동. 황성·용강·동천은 북측 신도시권으로 대비.');
 await img(s,A+'/northsouth_v.png',0.5,1.35,5.2,5.45,'contain','left');
 label(s,'남측  관광 집중',6.1,1.45,3.2); stat(s,'757','명/ha','황리단길 반경 300 m 일평균 유동 · 21,403명/일  [T2]',6.1,1.75,3.3,{size:26});
 stat(s,'29.6','%','관광객 불편 1위 교통혼잡·주차 (n=3,009)  [T2]',9.6,1.75,3.2,{size:26,color:INK});
 label(s,'주말 / 주중 일평균 유동 비  [T2]',6.1,3.3,6.6);
 barH(s,['황리단길 300 m','시청(동천동) 500 m'],[1.72,0.88],6.1,3.6,6.6,1.3,{fmt:'0.00',max:2.1});
 label(s,'북측  공원·생활권',6.1,5.0,6.6);
 bullets(s,['북천이 경계 북단에 접하고 황성공원은 북단에서 약 509 m, 성건동 생활권이 북서측에 접합니다.','전략계획은 선로로 단절된 도시공간을 잇는 매개공간을 제시하고  [T1, 인쇄쪽 161], 폐선축 동천~황성 2.5 km의 도시숲을 응답자 65.3%가 선호했습니다.  [T2]','관광은 남측에 집중되고 북측과 이어지지 않습니다. 폐선 노반이 남북을 잇는 보행축이 됩니다.'],6.1,5.3,6.7,1.55,{size:10.5,psa:3});
 SRC(s,'소상공인365 2026.06 요일별 추정 유동 · 경주시 제5차 관광실태조사 · 도시재생 전략계획(2022) · 2023 폐철도 기본구상');}
// 14 주말 시간대별 소통
{const s=slide('사이트 분석 : 교통','주말 시간대별 소통 상태','ITS 링크 평균속도 이력, 주말 표본 7일(2025.01–07 월별 토요일). 도시부 기준 정체 15km/h 미만·서행 25km/h 미만. 차량 교통량이 아니며 남측 관광 가로의 일괄 혼잡이나 철도 단절과의 인과를 직접 추론하지 않는다.');
 for(const [i,h] of [6,13,21].entries()){const x=0.5+i*3.3; T(s,String(h).padStart(2,'0')+'시',x,1.4,3.1,0.35,{size:14,bold:true,num:true}); await img(s,A+`/traffic_${String(h).padStart(2,'0')}.png`,x,1.8,3.1,3.85,'contain','left');}
 const lg=[[RED,'정체  15 km/h 미만'],['E8808F','서행  25 km/h 미만'],['C9C9C9','원활'],[INK,'본 계획 경계']];
 lg.forEach((l,i)=>{const x=0.5+i*2.5; rect(s,x,5.9,0.3,0.14,l[0]); T(s,l[1],x+0.4,5.82,2.0,0.3,{size:10});});
 label(s,'읽는 법',10.5,1.45,2.3);
 T(s,'같은 범위·같은 축척의 세 시각 비교입니다. 06시에는 정체 구간이 거의 없고, 13시와 21시에는 중심 가로와 남측 관광 가로 주변에 정체·서행이 늘어납니다.\n\n관광객 불편 1위가 교통혼잡·주차(29.6%)인 사실과 함께, 방문 동선의 차량 의존을 보행 전환으로 바꾸는 과제를 보여 줍니다.',10.5,1.8,2.3,4.0,{size:10.5,ls:1.3});
 T(s,'도심 중심가로의 시간대별 정체 분포는 확인되지만, 남측 관광 가로의 일괄 혼잡이나 철도 단절과의 인과는 이 자료로 입증하지 않습니다.',0.5,6.3,12.3,0.5,{size:10,color:G4});
 SRC(s,'ITS 평균속도 이력 · 주말 표본 7일(2025.01–07) · 도시부 기준 15 / 25 km/h · 회색 = 표본 없음 포함');}
// 15 규제의 중첩
{const s=slide('사이트 분석 : 규제','규제 4겹의 중첩','비율은 최종 경계 228,025㎡ 기준 재산정(2026.10.11). 고도지구 합 101%는 지구 중첩. ④는 기존 결정이 아니라 본 계획이 새로 수립하는 지구단위계획. 규제는 목적함수 페널티가 아니라 건축 불가 조건으로 둔다.');
 const pan=[['reg_landuse','① 용도지역','자연녹지 74.7% · 제2종일반주거 18.0% · 일반상업 7.3%','경주시 도시관리계획 · V-World  [T1]'],['reg_godo','② 고도지구','도심 20 m 지구 84.5% · 15 m 지구 12.7% · 최저고도 3.7%','경북 고시 제2020-479호  [T1]'],['reg_heritage','③ 역사문화환경 보존지역','전역이 보존지역 · 삼층석탑 등 지정문화유산 주변 허용기준 적용','문화유산법 · 경북 허용기준  [T1]'],['reg_plan','④ 지구단위계획(본 계획 수립)','본 계획이 경계·획지·용도·밀도·높이를 새로 정함 · 현 용도지역(자연녹지)과의 정합은 용도지역 변경 전제','본 계획 획지(라이노 최종)']];
 for(const [i,p] of pan.entries()){const x=0.5+i*3.12; T(s,p[1],x,1.4,2.95,0.3,{size:12,bold:true}); await img(s,A+`/${p[0]}.png`,x,1.75,2.95,3.35,'contain','left'); T(s,p[2],x,5.15,2.95,0.75,{size:10,ls:1.25}); T(s,p[3],x,5.9,2.95,0.3,{size:9,color:G4});}
 rect(s,0.5,6.3,12.33,0.5,G1); T(s,'+ 신라왕경 핵심유적 복원·정비 특별법 · 세계유산 완충구역 · 고도 보존 및 육성에 관한 특별법 — 규제 위반은 페널티가 아니라 건축 불가 조건으로 둡니다.',0.65,6.3,12.0,0.5,{size:10.5,valign:'middle'});}
// 16 매장유산
{const s=slide('사이트 분석 : 유산','매장유산과 단계별 이용 조건','시굴조사 필요 145,879㎡(철도 부지 148,770㎡의 98.1%), 지표조사 범위 148,770㎡(2022). 김권일 발표자료 pp.8·22. 조사 전 지하 개발 제외 → 주차는 지상 주차전용건축물.');
 await img(s,A+'/heritage.png',0.5,1.35,3.6,5.45,'contain','left');
 await img(s,PH+'/ph59_site_remnants_ne.jpg',4.4,1.4,3.6,2.5,'cover'); cap(s,'철도 잔존 시설과 성토 노반(2026.09)',4.4,3.95,3.6,0.3);
 stat(s,'145,879','㎡','시굴조사 필요 면적 · 철도 부지 148,770㎡의 98.1%  [T2, 2022 지표조사]',8.4,1.4,4.4,{size:30});
 T(s,'지표조사 범위 148,770㎡(2022년 조사 범위 기준)',8.4,2.6,4.4,0.3,{size:10.5,color:G4});
 ln(s,8.4,3.1,12.83,3.1);
 label(s,'1단계 설계 원칙',8.4,3.25,4.4);
 bullets(s,['조사 전 지하 개발을 제외합니다. 주차는 지상 주차전용건축물로 둡니다.','기초를 최소화하는 저층 분동과 되돌릴 수 있는 가로·광장·보행 정비를 1단계로 둡니다.','시굴 결과와 유산 영향에 따라 배치·이용 단계를 다시 검토합니다.','토양오염 가능성, 양산단층대(2016 경주지진 M5.8)는 층수·사업비 하한의 조건입니다.'],8.4,3.6,4.4,2.6,{size:10.5,psa:4});
 T(s,'지하 0 · 성토 2 m 미만, 보호·전시 전용 부분은 건축면적·바닥면적 불산입  [T1]',4.4,4.5,3.6,0.8,{size:10,color:G4,ls:1.25});
 T(s,'구 안동역 1단계의 지하주차 257면은 경주에 이식할 수 없습니다. 매장유산이 1단계 구성을 바꿉니다.',4.4,5.4,3.6,1.0,{size:10.5,ls:1.3});
 SRC(s,'김권일 학예연구실장 발표자료(2026) pp.8·22 · 구경주역 일원 시굴조사 계획 · 매장유산법');}
// 17 접속 조건과 도시조직
{const s=slide('사이트 분석 : 조직','접속 조건과 기존 도시조직','접속점 37곳은 이전 경계 6m 이내 접촉·관통 도로(서9·동18·남7·북3). 1층 비율은 경계 인접 0–150m 건물. 가로 57%는 NGII 도로중심선 길이가 공통 방위(N0.8°E ±7.5°)에 정렬한 비율. 약 150m는 현재 격자(동서 147.5 / 남북 161.5m).');
 await img(s,A+'/anchors.png',0.5,1.35,3.0,3.75,'contain','left'); T(s,'도로 끝 접속점 37곳',0.5,5.15,3.0,0.3,{size:10.5,bold:true});
 await img(s,A+'/street_orientation.png',3.8,1.35,4.0,3.75,'contain','left'); T(s,'가로 방위 분석 · 남북 격자와 북천 변 사선 격자',3.8,5.15,4.0,0.3,{size:10.5,bold:true});
 await img(s,AZ,8.1,1.35,4.7,3.75,'contain','left'); T(s,'가로 방위 분포 (도로중심선 212 km, 길이 가중)',8.1,5.15,4.7,0.3,{size:10.5,bold:true});
 const st=[['37','곳','접속점(서 9 · 동 18 · 남 7 · 북 3)'],['69.4','%','서측 인접 1층 건물 · 3층 이상 16.4%'],['93.3','%','동측 인접 1층 건물 · 저층 골목'],['약 150','m','현재 격자 규모 · 공통 방위 가로 57%']];
 st.forEach((v,i)=>{stat(s,v[0],v[1],v[2],0.5+i*3.1,5.55,2.9,{size:22,color:i===0?RED:INK,dsize:9.5});});
 SRC(s,'NGII 연속수치지도 · 기존 접속점 조사 · 도시조직 분석(2026.09) · 접속점은 최종 경계 기준 재산정 전');}
// 18 건축물 노후도
{const s=slide('사이트 분석 : 노후·쇠퇴','건축물 노후도와 법정 쇠퇴진단','경과연수 확인 2,152필지 중 20년 이상 1,978필지(91.9%), 30년 이상 83.8%. 법정 쇠퇴진단(2022): 황오동 인구 43.0% 감소(5년 연속)·사업체 2.7% 감소(2년 연속)·노후 87.9% → 3지표 충족. 성건동 2지표 충족.');
 await img(s,A+'/age_buildings.png',0.5,1.35,6.2,4.6,'contain','left');
 label(s,'건축물 경과연수 분포 (필지 수)  [T2 건축물대장 × 연속지적]',7.1,1.45,5.7);
 barH(s,['10년 미만','10–20년','20–30년','30–40년','40년 이상'],[60,114,174,324,1480],7.1,1.75,5.7,2.3,{max:1750});
 stat(s,'91.9','%','20년 이상 건물이 있는 필지 (1,978 / 2,152)',7.1,4.15,2.8,{size:26});
 stat(s,'83.8','%','30년 이상 건물이 있는 필지',10.0,4.15,2.8,{size:26,color:INK});
 label(s,'법정 쇠퇴진단 (도시재생특별법 §13, 2022)  [T1]',7.1,5.35,5.7);
 table(s,[['행정동','인구','사업체','노후건축물','판정'],['황오동','−43.0% · 5년 연속','−2.7% · 2년 연속','87.9%',{text:'3지표 충족',bold:true,color:RED}],['성건동','−29.0% · 5년 연속','+2.2% · 1년 감소','72.4%','2지표 충족']],7.1,5.65,5.7,[1.0,1.5,1.4,1.0,0.8],{size:9.5,rowH:0.3});
 T(s,'도시재생 혁신지구 공모 자격(쇠퇴 3지표 중 2개)을 대상지 주변 행정동이 충족합니다.',0.5,6.1,6.2,0.6,{size:10.5,bold:true});
 SRC(s,'건축HUB 건축물대장 표제부(2026.09) × PNU 조인 · 경주시 도시재생 전략계획(변경, 2022) 쇠퇴진단');}
// 19 구분
divider('02','경주 도시의 특징과 문제','인구·고령화·청년 순이동·방문과 체류·야간 활동·업종 변화를 데이터로 읽고 여섯 문제와 세 목표로 정리');
// 20 인구 변화
{const s=slide('도시의 특징 : 인구','인구 변화의 공간 분포','KOSIS 주민등록인구(DT_1B04005N) 2015–2025 연말. 원도심 4개 동(황오·중부·황남·월성) 27,673 → 18,528명(−33.0%), 20~39세 −59.8%. 황오동은 옛 중부동 합산. 북측 신도시권(황성·용강·동천)은 쇠퇴가 두드러지지 않음.');
 await img(s,A+'/pop_change.png',0.5,1.35,6.3,5.1,'contain','left');
 label(s,'인구 지수 (2015 = 100)  [T2 KOSIS]',7.1,1.45,5.7);
 lineC(s,Y,[{name:'황남동',values:idx('황남동')},{name:'황오동',values:idx('황오동')},{name:'성건동',values:idx('성건동')},{name:'월성동',values:idx('월성동')},{name:'경주시',values:cityIdx}],7.1,1.7,5.7,3.0,{min:50,max:105,unit:10});
 const rows=[['황남동','−44.8%'],['황오동','−32.7%'],['성건동','−29.0%'],['월성동','−22.3%'],['용강동','+32.8%'],['현곡면','+33.3%']];
 rows.forEach((r,i)=>{const x=7.1+(i%3)*1.95, y=4.85+Math.floor(i/3)*0.75; T(s,r[0],x,y,1.9,0.25,{size:10,color:G4}); T(s,r[1],x,y+0.22,1.9,0.4,{size:18,bold:true,num:true,color:i<4?RED:G4});});
 T(s,'원도심 4개 동 인구는 10년간 33.0% 줄고 20~39세는 59.8% 줄었습니다. 감소는 폐역(2021.12) 이전부터 이어졌습니다.',7.1,6.3,5.7,0.55,{size:10.5,bold:true});
 SRC(s,'KOSIS 주민등록인구 2015–2025 연말 · 2026.08 현재 · 지도 붉은 농도 = 감소율, 회색 = 증가');}
// 21 고령화와 청년
{const s=slide('도시의 특징 : 고령·청년','고령화와 청년 인구의 분포','행안부 주민등록 2026.08. 65세 이상 비율 황남 50.1 / 황오 43.8 / 월성 39.0 / 성건 36.7 / 경주시 30.0. 20~34세 황오동 11.4% vs 경주시 12.9%. 황성·동천·용강·현곡 20~34세 13,982명 = 경주시 31,387명의 44.5%. 성건동 청년 비율은 대학가 영향으로 절대 수 변화(−41.0%)만 쓴다.');
 T(s,'65세 이상 비율',0.5,1.4,4.1,0.3,{size:11,bold:true}); await img(s,A+'/pop_65.png',0.5,1.72,4.1,3.3,'contain','left');
 T(s,'20~34세 비율 (붉을수록 낮음)',4.8,1.4,4.1,0.3,{size:11,bold:true}); await img(s,A+'/pop_y2034.png',4.8,1.72,4.1,3.3,'contain','left');
 label(s,'65세 이상 비율 (%)  [T2]',9.2,1.45,3.6);
 barH(s,['황남동','황오동','월성동','성건동','경주시'],[50.1,43.8,39.0,36.7,30.0],9.2,1.72,3.6,2.6,{fmt:'0.0',max:62});
 stat(s,'11.4','%','황오동 20~34세 비율 · 경주시 평균 12.9%',0.5,5.3,3.9,{size:24});
 stat(s,'44.5','%','황성·동천·용강·현곡의 20~34세 비중 (13,982 / 31,387명)',4.5,5.3,4.2,{size:24,color:INK});
 stat(s,'−41.0','%','성건동 20~39세 절대 수 변화(2015→2025) · 외국인주민 3,481 → 7,170명',8.9,5.3,3.9,{size:24,color:INK,dsize:9.5});
 T(s,'원도심은 생활 편의·돌봄 수요가 크고, 청년은 북측 신도시권에 모여 있습니다. 주거·고용·생활 편의의 결합이 청년 정주의 조건입니다.',0.5,6.4,12.3,0.45,{size:10.5,bold:true});
 SRC(s,'행정안전부·KOSIS 주민등록인구 2026.08 · 5세 구간 합 · 외국인주민현황 2016·2024');}
// 22 청년 순이동과 쇠퇴 요인
{const s=slide('도시의 특징 : 청년 유출','청년 순이동과 쇠퇴의 요인','KOSIS 국내인구이동통계(DT_1B26002) 경주시 순이동. 20~34세 2020–2025 누계 −7,249명, 20~24세 기여 62.7%, 2025년 −349명. 전략계획 종합 쇠퇴원인 1번: 청년 경제활동·주거안정 지역기반 부재(인쇄쪽 150). 외연 확장은 요인 중 하나(인쇄쪽 15–16)로 나열.');
 label(s,'연령별 연간 순이동 (명)  [T2 KOSIS]',0.5,1.45,6.6);
 lineC(s,EV.youth.mig_years,[{name:'20–24세',values:mig['20-24세']},{name:'25–29세',values:mig['25-29세']},{name:'30–34세',values:mig['30-34세']}],0.5,1.7,6.6,3.4,{min:-1100,max:200,unit:200});
 stat(s,'−7,249','명','20~34세 순이동 누계 · 2020–2025',0.5,5.25,3.2,{size:28});
 stat(s,'62.7','%','20~24세의 순유출 기여 · 교육 이동과 정주 기반의 과제 구분',3.8,5.25,3.3,{size:28,color:INK});
 label(s,'쇠퇴의 요인 (계획서 진단)',7.5,1.45,5.3);
 const q=[['종합 쇠퇴원인 1번','청년 경제활동과 주거안정을 위한 지역기반 부재','[T1, 도시재생 전략계획 인쇄쪽 150]'],['외연 확장','시청 이전·주거단지 확장·KTX 역세권 개발이 인구 유출과 중심권 약화의 한 요인(인구구조 변화·개발 규제와 함께)','[T1, 전략계획 인쇄쪽 15–16]'],['순유출 사유','20~34세 전출 사유는 직업·교육','[T2, 통계청 전입신고 사유]'],['시의 방향','주민의 힘으로 이끌어가는 삶터 · 관광객 중심에서 주민 거주 중심으로','[T1 전략계획 · T2 2026.08 지역재생지원센터]']];
 q.forEach((r,i)=>{const y=1.8+i*1.05; rect(s,7.5,y,0.1,0.85,i===0?RED:G3); T(s,r[0],7.75,y,5.0,0.27,{size:11,bold:true}); T(s,r[1],7.75,y+0.27,5.0,0.42,{size:10,ls:1.2}); T(s,r[2],7.75,y+0.66,5.0,0.22,{size:8.5,color:G4});});
 T(s,'청년 정주 방안은 문화생활 증진만으로 충분하지 않으며 일자리와 주거 기반을 포함해야 합니다.',7.5,6.1,5.3,0.6,{size:10.5,bold:true});
 SRC(s,'KOSIS 국내인구이동통계 2020–2025 · 경주시 도시재생 전략계획(변경, 2022)');}
// 23 방문과 체류
{const s=slide('도시의 특징 : 방문','방문과 체류의 특성','황오동 모니터링(2024) 현장 설문 n=187, 축제 현장 표본이라 시계열·일반화 금지. 경주시 제5차 관광실태조사(2024–25) 내국인 n=3,009, 6개 관광지. 자가용 76.9%. 872만 명(T4)은 쓰지 않는다.');
 label(s,'황오동 현장 설문 · 체류시간 (%)  [T2, n=187]',0.5,1.45,4.2);
 barH(s,['1–3시간','3–6시간','6–9시간','24시간 이상'],[79.1,15.0,3.2,2.7],0.5,1.75,4.2,2.2,{fmt:'0.0',max:95});
 label(s,'관광실태조사 · 내국인 방문 유형 (%)  [T2, n=3,009]',0.5,4.1,4.2);
 barH(s,['숙박 방문','당일 방문'],[55.3,44.7],0.5,4.4,4.2,1.3,{fmt:'0.0',max:70,color:G4});
 stat(s,'79.1','%','현장 체류 1~3시간 · 짧은 체류',5.1,1.5,2.3,{size:26});
 stat(s,'1.8','일','내국인 숙박 방문객 평균 체류 · 권역별 편차 큼(수도권 86.5% 숙박, 대경권 28.7%)',5.1,2.85,2.6,{size:26,color:INK,dsize:9.5});
 stat(s,'76.9','%','내국인 방문객의 자가용 이용',5.1,4.35,2.3,{size:26,color:INK});
 await img(s,A+'/arrival.png',8.0,1.4,4.8,3.0,'cover'); T(s,'KTX 경주역(건천읍)과 구 경주역(원도심)의 서로 다른 위치',8.0,4.45,4.8,0.3,{size:10.5,bold:true});
 T(s,'차량으로 도착해 짧게 머무는 방문이 많습니다. 과제는 방문객 수의 확대가 아니라 체류 시간의 확대이며, 주차·대중교통 접점에서 원도심 보행으로 전환하는 동선이 필요합니다.',5.1,5.65,7.7,0.9,{size:10.5,ls:1.3});
 SRC(s,'황오동 모니터링 결과보고서(2024) · 경주시 제5차 관광실태조사(2024–2025) · V-World·OSM');}
// 24 야간 활동과 정주 기능
{const s=slide('도시의 특징 : 정주','야간 활동과 정주 기능의 공백','소상공인365 2026.06 시간대별 추정 유동. 23–05시 비중 폐역 구역 3.7 / 행복황촌 4.4 / 성동시장 5.0 / 황리단길 5.5%. 폐역 구역 상시 거주 27명·직장 117명(통신 추정). 시민 요구는 응답자 55명 복수응답 58건(2025).');
 label(s,'23–05시 추정 유동 비중 (%)  [T2]',0.5,1.45,5.0);
 barH(s,['폐역 구역','행복황촌','성동시장','황리단길'],[3.7,4.4,5.0,5.5],0.5,1.75,5.0,2.3,{fmt:'0.0',max:7});
 T(s,'상시 거주·숙박 인구와 구분되는 야간 활동 지표입니다. 폐역 구역이 가장 낮습니다.',0.5,4.1,5.0,0.5,{size:10,color:G4});
 stat(s,'27','명','폐역 구역 상시 거주 인구 · 직장 인구 117명 (통신 추정)  [T2]',5.9,1.45,2.3,{size:30,dsize:9.5});
 label(s,'구 경주역 부지에 대한 시민 요구 (건)  [T2, 응답 55명 복수응답]',8.4,1.45,4.4);
 barH(s,['문화·쇼핑','교통 거점','지식·기술센터','공공기관','주거'],[37,16,3,3,1],8.4,1.75,4.4,2.9,{max:44,color:G4});
 rect(s,0.5,4.85,7.7,1.9,G1);
 T(s,'주거와 야간 기능이 없는 구역은 저녁 6시 이후 비게 됩니다.',0.7,5.0,7.3,0.35,{size:12,bold:true});
 T(s,'시민 응답에서 주거는 1건뿐이지만, 야간 활동 인구를 확보하기 위해 본 계획은 청년·신혼 주거를 추가합니다. 이는 자체 판단이며 용도지역 변경을 전제로 합니다. 부산 혁신도시 사례의 정착 수치(이주율 81.2%)는 광역 통계이고, 대연지구 "1,300명 정착"은 실측이 아니므로 쓰지 않습니다.',0.7,5.4,7.3,1.3,{size:10.5,ls:1.3});
 SRC(s,'소상공인365 2026.06 · 원도심 미래구상 기획연구(2025) 시민 설문');}
// 25 업종 변화
{const s=slide('도시의 특징 : 업종','업종 변화와 치환의 징후','소상공인365 2025.06→2026.06 행복황촌 근사구역 표본 11업종: 생활 15→15, 관광·체류 22→29. 황오동 모니터링(2024 인허가) 점포형 업종군 순증감: 숙박·체류 +5, 생활소매·식품제조 −9. 외국인관광도시민박업 2021년 2곳→2025년 21곳(시 발표). 인과(스테이 효과)는 미입증.');
 label(s,'행복황촌 선택 업종군 업소 수 (개)  [T2]',0.5,1.45,4.5);
 colG(s,['생활','관광·체류'],[{name:'2025.06',values:[15,22]},{name:'2026.06',values:[15,29]}],0.5,1.75,4.5,3.3,{labels:true,max:36});
 label(s,'황오동 점포형 업종군 순증감 (건, 2024 인허가)  [T2]',5.3,1.45,5.2);
 barH(s,['숙박·체류','생활서비스·의료','카페·휴게음식','음식점·제과','유흥·오락','생활소매·식품제조'],[5,1,0,-1,-2,-9],5.3,1.75,5.2,3.3,{fmt:'+0;-0;0',min:-11,max:7});
 stat(s,'+7','개','관광·체류 업종 13개월 순증 · 생활 업종 순증 0',10.9,1.5,1.9,{size:26});
 stat(s,'2→21','곳','외국인관광도시민박업 2021→2025  [T2 시 발표, 정의 미확인]',10.9,2.9,1.95,{size:22,color:INK,dsize:9.5});
 stat(s,'−9','건','생활소매·식품제조 순감 · 최대 순감',10.9,4.3,1.9,{size:26,color:INK});
 rect(s,0.5,5.3,12.33,1.45,G1);
 T(s,'관광 업종이 늘고 생활 업종이 주는 것은 회복이 아니라 치환입니다.',0.7,5.42,12.0,0.35,{size:12,bold:true});
 T(s,'동측에서는 숙소가 늘었으나 구역의 일평균 유동(1,321명/일)은 2019~2023년 수준이며 생활 업종은 늘지 않았습니다. 본 계획의 성과지표는 (방문객·체류시간)과 (거주인구·생활업종 비율·야간활동)을 항상 나란히 보고합니다.',0.7,5.8,12.0,0.9,{size:10.5,ls:1.3});
 SRC(s,'소상공인365 상가업소 2025.06–2026.06 · 황오동 모니터링 결과보고서(2024) pp.82–86 · 경주시 발표');}
// 26 문제 종합
{const s=slide('문제 구체화 : 종합','문제 종합: 여섯 과제','앞선 공간·현장·통계 자료의 종합. 각 수치의 범위·정의는 해당 슬라이드 참조.');
 const cards=[['①','동서 단절',A+'/crossing_map.png','985 m 무횡단 · 육교 1 · 우회율 3.5\n유동 밀도 14.6배 격차 · 접속점 37곳'],['②','남북 불균형',A+'/northsouth.png','황리단길 757명/ha · 주말 1.72배\n북측 공원·생활권과 미연계'],['③','원도심 쇠퇴와 청년 유출',A+'/pop_change.png','4개 동 −33.0% · 20~34세 −7,249명\n쇠퇴원인 1번 일자리·주거 기반 부재'],['④','짧은 체류와 차량 중심 방문',A+'/arrival.png','현장 체류 1~3시간 79.1% · 자가용 76.9%\n불편 1위 교통혼잡·주차 29.6%'],['⑤','정주 공백과 치환 위험',A+'/footfall_density.png','상시 거주 27명 · 야간 유동 3.7%\n관광·체류 +7 · 생활 0 · 생활소매 −9'],['⑥','유산·규제 제약',A+'/reg_heritage.png','시굴 대상 93.2% · 20 m 지구 84.5%\n1단계 지하 개발 불가 · 4겹 규제']];
 for(const [i,c] of cards.entries()){const x=0.5+(i%3)*4.2, y=1.4+Math.floor(i/3)*2.7; rect(s,x,y,3.9,2.5,G1); await img(s,c[2],x+0.15,y+0.15,1.5,2.2,'cover'); T(s,c[0],x+1.8,y+0.15,0.5,0.45,{size:20,bold:true,color:RED}); T(s,c[1],x+2.25,y+0.2,1.6,0.6,{size:12.5,bold:true,ls:1.15}); T(s,c[3],x+1.8,y+0.95,2.0,1.5,{size:9.5,ls:1.3});}
 SRC(s,'공간·현장·통계 자료 종합 · 지표 범위는 각 슬라이드 참조');}
// 27 문제의 연쇄와 계획 목표
{const s=slide('문제 구체화 : 목표','문제의 연쇄와 계획 목표','세 연쇄가 세 목표로 이어진다. 성과지표는 방문·정주·환류 세 축을 같은 정의·범위로 나란히 본다. 건물 출입구 방향 전환(광주 푸른길)은 물리적 사실 지표.');
 const rowsC=[['철도 장벽 (1936~)','경계공백지대','동서 활력 격차 ①②','목표 ①  연결'],['남측 관광 집중','짧은 체류 · 차량 도착 ④','생활 업종 치환 ⑤','목표 ②  문화·유적과 체류'],['외연 확장 · 시청 이전','원도심 인구·청년 유출 ③','주거·야간 공백 ⑤⑥','목표 ③  주민 생활과 청년 정주']];
 rowsC.forEach((r,i)=>{const y=1.55+i*1.15; r.forEach((c,j)=>{const x=0.5+j*2.2; const goal=j===3; rect(s,x,y,goal?2.6:1.9,0.8,goal?RED:G1); T(s,c,x+0.1,y,(goal?2.6:1.9)-0.2,0.8,{size:goal?11.5:10.5,bold:goal,color:goal?WH:INK,valign:'middle',ls:1.2}); if(j<3) ln(s,x+1.9,y+0.4,x+2.2,y+0.4,INK,1,true);});});
 label(s,'성과지표 (두 축을 항상 나란히 보고)',0.5,5.15,8);
 const ax=[['방문 축','체류시간 · 숙박 비율 · 소비'],['정주 축','25~39세 거주 인구 · 생활업종 비율 · 야간 활동'],['환류 축','지역 사업체 매출 비중 · 청년 정규 일자리 · 임대료 · 도시민박 등록 수']];
 ax.forEach((a,i)=>{const x=0.5+i*3.0; T(s,a[0],x,5.5,2.8,0.3,{size:11.5,bold:true,color:i===2?RED:INK}); T(s,a[1],x,5.8,2.85,0.8,{size:10,color:G4,ls:1.25});});
 rect(s,9.6,1.55,3.23,5.0,G1);
 T(s,'설계 조건',9.75,1.65,2.9,0.3,{size:11,bold:true,color:RED});
 bullets(s,['되돌릴 수 있는 순서로 투자합니다. 1단계는 가로·광장·보행 정비입니다.','관광 수익이 주민에게 환류되도록 소유·운영 구조를 설계합니다.','연결은 횡단 개소 수가 아니라 연속성과 최약 지점의 통과 폭으로 측정합니다.','성공 지표는 경계 인접 필지의 주 출입구 방향이 부지 쪽으로 바뀌는가입니다(광주 푸른길).'],9.75,2.0,2.95,4.4,{size:10,psa:6});
 SRC(s,'문제 번호는 26쪽 기준 · 지표 정의는 20261010 방향 근거 정리 §2.4');}
// 28 구분
divider('03','해결 컨셉과 프로그램','NEXUS 1918의 컨셉 위계와 전략의 공간 배치, 관광과 정주 연계의 성립 조건, 선례, 프로그램 선정과 앵커, 권역과 세부 프로그램');
// 29 컨셉 위계
{const s=slide('해결 컨셉 : 위계','컨셉의 위계','1918년은 경주역 개업 연도(사정동, 관보 운수개시 인가 1918-12-28). 현 위치 역사는 1936년 이전. 방향 문장은 근거 반영 보강안(20261010_final_direction_evidence_v1 §2.1).');
 const lv=[['프로젝트','NEXUS 1918','멈춘 역, 경주를 다시 연결하는 중심 · 1918 = 경주역 개업 연도  [T1]',RED],['설계 컨셉','CULTURAL INTERCHANGE','도시의 흐름을 바꾸는 문화환승 · 방문 동선과 주민 생활이 교차하는 환승점',INK],['전략','CONNECT  ·  EXCHANGE  ·  SPREAD','접속(동서·남북 연결)  ·  교차·전환(관광과 일상, 문화·창작의 접점)  ·  확산(성동시장·원도심으로 활동 확산, 일자리·주거)',G4],['건축 표현','ELEVATED CULTURAL PLATFORM','저층 1~3층 분동 문화시설 + 중앙 오픈스페이스 + 공중광장·상층 녹지산책로 · 매장유산 조건에 맞는 지상 구성',G4]];
 lv.forEach((l,i)=>{const y=1.45+i*1.0; rect(s,0.5,y,1.5,0.85,l[3]); T(s,l[0],0.5,y,1.5,0.85,{size:11,bold:true,color:WH,align:'center',valign:'middle'}); T(s,l[1],2.2,y+0.05,10.6,0.4,{size:18,bold:true,num:true,color:i===0?RED:INK}); T(s,l[2],2.2,y+0.47,10.6,0.4,{size:10.5,color:G4}); if(i<3) ln(s,1.25,y+0.85,1.25,y+1.0,INK,1,true);});
 ln(s,0.5,5.5,12.83,5.5);
 label(s,'목표와 전략의 대응',0.5,5.6,6);
 const mp=[['목표 ①  연결','CONNECT','문제 ①②'],['목표 ②  문화·유적과 체류','EXCHANGE','문제 ②④'],['목표 ③  주민 생활과 청년 정주','SPREAD','문제 ③⑤']];
 mp.forEach((m,i)=>{const x=0.5+i*4.15; T(s,m[0],x,5.9,2.2,0.3,{size:10.5,bold:true}); T(s,m[1],x+2.2,5.9,1.2,0.3,{size:10.5,bold:true,num:true,color:RED}); T(s,m[2],x+3.3,5.9,0.8,0.3,{size:10,color:G4});});
 T(s,'단절된 원도심을 다시 연결하고, 문화·유적 강점을 체류와 소득으로 이어 가되, 그 소득과 일자리가 주민(특히 청년)에게 남도록 일자리·주거·생활 기반을 함께 갖추는 지속가능한 재생을 방향으로 합니다.',0.5,6.3,12.3,0.55,{size:11,bold:true,ls:1.25});}
// 30 전략의 공간 배치
{const s=slide('해결 컨셉 : 전략','전략의 공간 배치','CONNECT 동서 횡단 가로와 남북 폐선축 보행 · EXCHANGE 중앙 접점(구 역사·광장·창작·체험·시장 접점) · SPREAD 북측 청년 업무·주거·공공청사와 성동시장·행복황촌으로의 확산.');
 await img(s,A+'/strategy_map.png',0.5,1.35,6.3,5.45,'contain','left');
 const strat=[['CONNECT','접속',['동서 횡단 가로를 여러 곳에 두어 횡단 간격을 줄이고 최약 지점의 통과 폭을 확보합니다.','폐선 노반을 대릉원 ↔ 북천·황성공원을 잇는 남북 보행축으로 씁니다.','접속점 37곳과 기존 가로의 폭·방향에 새 가로를 정렬합니다.']],['EXCHANGE','교차·전환',['중앙에 구 역사·문화광장·창작 스튜디오·체험관·시장 접점을 모아 방문객과 주민이 만나는 자리를 만듭니다.','방문 지출이 상인·공예인·예술인의 소득으로 이어지는 접점 장치입니다.']],['SPREAD','확산',['북측에 청년 업무·청년주거·공공청사를 두어 저녁 이후에도 사람이 남게 합니다.','활동을 성동시장과 행복황촌으로 내보내는 방향으로 동선과 안내를 설계합니다.']]];
 strat.forEach((st,i)=>{const y=1.45+i*1.8; T(s,st[0],7.1,y,2.0,0.35,{size:16,bold:true,num:true,color:i<2?RED:INK}); T(s,st[1],9.1,y+0.07,1.5,0.3,{size:11,color:G4}); bullets(s,st[2],7.1,y+0.4,5.7,1.35,{size:10,psa:2});});
 SRC(s,'전략 배치도: 최종 계획 경계(붉은 면) · NGII 도로·UPIS 공원·OSM 폐선');}
// 31 관광과 정주 연계의 성립 조건
{const s=slide('해결 컨셉 : 가설','관광과 정주 연계의 성립 조건','핵심 가설(관광 → 주민 소득 → 정주)은 조건부다. 고리 A는 문헌이 지지(유럽 179개 지역 +), B는 지역 소유·체류일수에 좌우, C는 같은 설계로 직접 검증한 연구가 없고 황남동(관광 중심)은 인구 −44.8%. 성립 조건 5개는 문헌 종합에 따른 설계 요구사항.');
 const chain=[['A','관광 확대 → 지역 소득·일자리','찬성  [T3]','유럽 179개 지역에서 관광이 1인당 GDP 성장에 양(+) · 경주 사적지 1개소당 생산유발 148억 원'],['B','소득이 주민에게 남는가','조건부  [T3]','지역 소유 소기업 밀도가 소득 성장에 양(+), 비지역 대기업은 음(−) · 잔류 지출은 체류일수만이 예측'],['C','주민 소득·일자리 → 정주 인구','직접 검증 없음  [T3·T2]','체류인구는 늘어도 정주 순유입은 늘지 않은 평가 3건 · 황남동(관광 중심) 인구 −44.8%']];
 chain.forEach((c,i)=>{const x=0.5+i*4.2; rect(s,x,1.45,3.9,1.75,G1); T(s,c[0],x+0.15,1.5,0.6,0.5,{size:22,bold:true,num:true,color:RED}); T(s,c[1],x+0.75,1.55,3.0,0.5,{size:11,bold:true,ls:1.15}); T(s,c[2],x+0.15,2.05,3.6,0.3,{size:10,bold:true,color:i===0?INK:RED}); T(s,c[3],x+0.15,2.35,3.6,0.85,{size:9.5,color:G4,ls:1.2}); if(i<2) ln(s,x+3.9,2.3,x+4.2,2.3,INK,1,true);});
 label(s,'성립 조건 5개 (설계 요구사항)',0.5,3.4,6);
 const cond=[['01','소득의 지역 잔류','성동시장 클러스터 임대료 하향 · 상인회·협동조합 공동 운영'],['02','일자리의 질','관광 밖 일자리(청년 창업·기업지원·공공청사)를 함께 둡니다'],['03','주거 공급과 관광 수요의 비경합','도시민박 등록 수·월세를 감시 지표로 둡니다'],['04','관광 구역과 생활권의 완충','남측 방문 관문과 북측 근로·정주를 분리·완충합니다'],['05','규모의 한계','목표는 관광 규모가 아니라 체류·소득 환류·정주입니다']];
 cond.forEach((c,i)=>{const y=3.75+i*0.58; T(s,c[0],0.5,y,0.6,0.4,{size:14,bold:true,num:true,color:RED}); T(s,c[1],1.2,y+0.04,3.6,0.35,{size:11,bold:true}); T(s,c[2],4.9,y+0.06,7.9,0.35,{size:10,color:G4});});
 SRC(s,'문헌 종합(20261010_final_direction_evidence_v1 §2.4) · KCI·Crossref·OpenAlex 검색 · 개별 논문의 결론이 아닌 종합 해석');}
// 32 선례
{const s=slide('해결 컨셉 : 선례','선례에서 빌리는 것','docs/20_cases 정리 기준이며 원문 교차검증 전(T3~T4). 빌리는 것은 순서·운영 조직·분산 삽입이며 규모·수치는 이식하지 않는다. 지하주차는 매장유산 때문에 1단계 불가.');
 const cs=[['구 안동역','1단계 = 연결도로 220 m · 지하주차 257면 · 산책로 790 m','어떤 프로그램에도 필요하고 되돌릴 필요가 없는 연결·기반·보행을 먼저 합니다. 지하주차만 경주에 이식할 수 없습니다.'],['교토 우메코지','공원 1995 → 수족관 2012 → 철도박물관 2016 → 전용역 2019','비가역 투자는 뒤로 둡니다. 민간자본은 공원 개원 13년 후에 들어왔습니다. 빌릴 것은 기간이 아니라 순서입니다.'],['광주 푸른길','(사)푸른길이 운영 · 레일을 등지던 건물들이 푸른길 쪽으로 출입문을 냄','조성 조직이 아니라 운영 조직을 설계합니다. 성공 지표는 인접 건물의 출입구 방향 전환입니다.'],['부산 혁신도시','93.5만㎡를 4개로 쪼개 기존 도심에 삽입 · 정주만족 1위 61.6%','단일 대형이 아니라 분산 삽입을 대안 시나리오로 함께 냅니다.']];
 cs.forEach((c,i)=>{const x=0.5+(i%2)*6.25, y=1.45+Math.floor(i/2)*2.45; rect(s,x,y,6.05,2.25,G1); T(s,c[0],x+0.2,y+0.15,5.6,0.35,{size:13,bold:true,color:RED}); T(s,c[1],x+0.2,y+0.55,5.6,0.5,{size:10,color:G4,ls:1.2}); T(s,c[2],x+0.2,y+1.1,5.6,1.05,{size:10.5,ls:1.3});});
 rect(s,0.5,6.35,12.33,0.5,INK); T(s,'회피 사례  울산 우정혁신도시(단일 대형, 도심 속 외딴 섬) · 트렌토 Le Albere · 발렌시아 예술과학도시 · 전주 한옥마을(관광 치환) — 검토했음을 심의에서 증명합니다.',0.65,6.35,12.0,0.5,{size:10,color:WH,valign:'middle'});
 SRC(s,'docs/20_cases 사례 데이터베이스 · 원문 교차검증 전 [T3·T4]');}
// 33 프로그램 선정 방법과 후보 평가
{const s=slide('프로그램 : 선정 방법','프로그램 선정 방법과 후보 평가','문제 → 기능 → 후보 7개 → 기준 5개(문제 대응·시 구상 정합·혁신지구 요건·규제 적합·운영 주체와 수요 근거). ● 강함 ◐ 중간 ○ 약함. 판정은 20261010 part2 §2.');
 const flow=['문제 6개','필요 기능','후보 7개','평가 기준 5개','앵커 3 · 보조 1 · 기타'];
 flow.forEach((f,i)=>{const x=0.5+i*2.55; rect(s,x,1.45,2.2,0.5,i===4?RED:G1); T(s,f,x,1.45,2.2,0.5,{size:11,bold:true,color:i===4?WH:INK,align:'center',valign:'middle'}); if(i<4) ln(s,x+2.2,1.7,x+2.55,1.7,INK,1,true);});
 const hdr=['후보','문제 대응','시 구상 정합','혁신지구 요건','규제 적합','운영·수요 근거','판정'];
 const rows=[['청년창업·기업지원(청년오피스복합타운)','●','●','●','●','◐',{text:'앵커',bold:true,color:RED}],['청년·신혼 주거','●','●','●','◐','○',{text:'앵커(정주)',bold:true,color:RED}],['K-헤리티지·역사문화예술','●','●','◐','●','◐',{text:'앵커',bold:true,color:RED}],['창작 스튜디오·공방','◐','○','◐','●','○','보조 앵커'],['공공청사·의회','●','◐','○','◐','◐','확산 거점 · 시 구상 2단계'],['모빌리티 허브','◐','●','◐','●','○','기타(필수 기능) · 선택 제안'],['성동시장 연계 상업 · 소규모 숙박','◐','●','○','●','○','선택 제안 · 치환 위험 관리']];
 table(s,[hdr,...rows],0.5,2.2,12.33,[3.6,1.3,1.3,1.3,1.3,1.4,2.13],{size:10,rowH:0.4});
 T(s,'● 강함  ◐ 중간  ○ 약함 · 판단 근거: 전략계획 쇠퇴원인 1번 [T1] · 시 구상 3-1·1-1·1-2·2-1 [T2] · 혁신지구 가이드라인(기능 집적, 국비 대상) [T2] · 고도지구·매장유산 [T1] · 수요 자료 유무',0.5,5.5,12.3,0.5,{size:9.5,color:G4,ls:1.2});
 T(s,'앵커는 문제에 직접 대응하고 시 구상과 공모 요건에 맞으며 규제 안에서 지을 수 있는 기능으로 정했습니다. 수요·운영 근거가 약한 항목은 단계 공급과 입주 확약으로 보완합니다.',0.5,6.1,12.3,0.6,{size:10.5,bold:true,ls:1.25});
 SRC(s,'20261010 2파트 프로그램·규모 산정 §2 · 시 구상(김권일 2026) · 도시재생 혁신지구 가이드라인');}
// 34 앵커 ①
{const s=slide('프로그램 : 앵커 ①','앵커 ①  청년 일자리와 청년주거','청년창업·기업지원: 시 구상 3-1, 시굴계획서 직주근접·젊은 층 정착, 혁신지구 가이드라인 p.14 지자체 운영 기업지원센터 국비 보조. 청년주거: 구역 상시 거주 27명, 시 구상 1단계 준주거 20,262㎡(25.5%), 혁신지구 선정 17곳 중 14곳 주거 포함. 경주 입주율 실측 없음 → 단계 공급.');
 rect(s,0.5,1.45,6.05,5.3,G1); rect(s,6.78,1.45,6.05,5.3,G1);
 T(s,'청년창업·기업지원',0.7,1.6,5.7,0.4,{size:16,bold:true,color:RED}); T(s,'청년오피스복합타운 · 공유 오피스 · 상담·교육·협업실',0.7,2.0,5.7,0.3,{size:10.5,color:G4});
 stat(s,'1,208','명/년','20~34세 연평균 순유출(7,249 ÷ 6) · 전출 사유 직업·교육  [T2]',0.7,2.45,2.8,{size:24,dsize:9.5});
 stat(s,'1번','','전략계획 종합 쇠퇴원인: 청년 경제활동·주거안정 기반 부재  [T1]',3.6,2.45,2.8,{size:24,color:INK,dsize:9.5});
 bullets(s,['시 구상 3-1 청년오피스복합타운, 시굴조사 계획서의 "직주근접·젊은 층 정착"  [T2]','혁신지구는 지자체 운영 기업지원센터를 국비 보조 대상으로 둡니다  [T2 가이드라인]','관광 밖 일자리를 두어 소득 환류 조건 02(일자리의 질)를 충족합니다','부족한 것: 입주 기업 수요 · 운영 주체 · 입주확약(공모 평가 항목)'],0.7,4.0,5.7,2.6,{size:10.5,psa:4});
 T(s,'청년·신혼 주거',6.98,1.6,5.7,0.4,{size:16,bold:true,color:RED}); T(s,'1~2인 세대 중심 공공임대 · 주민 공동시설 · 1층 생활편의',6.98,2.0,5.7,0.3,{size:10.5,color:G4});
 stat(s,'27','명','구역 상시 거주 · 야간 유동 3.7%',6.98,2.45,1.8,{size:24,dsize:9.5});
 stat(s,'14 / 17','곳','혁신지구 선정지 중 주거 포함  [T2]',8.85,2.45,1.9,{size:22,color:INK,dsize:9.5});
 stat(s,'73.8','%','경주 1~2인 가구 · 원도심 82.6%  [T2]',10.85,2.45,1.95,{size:22,color:INK,dsize:9.5});
 bullets(s,['시 구상 1단계에서 준주거 20,262㎡(25.5%)가 건축 가능 용지 중 가장 큽니다  [T2]','가구주 20~39세 18,052가구(1~2인 14,122) · 신혼부부 3,801쌍(2024)  [T2]','부족한 것: 현재 자연녹지지역이라 용도지역 변경 전제 · 경주 입주율·수요 실측 없음','대응: 기준 600세대를 약 200세대씩 3단계로 공급하고 입주율을 확인한 뒤 다음 단계를 진행합니다'],6.98,4.0,5.7,2.6,{size:10.5,psa:4});
 SRC(s,'경주시 도시재생 전략계획(2022) · 김권일 발표자료(2026) · 도시재생 혁신지구 가이드라인 · KOSIS 인구총조사 2025');}
// 35 앵커 ②
{const s=slide('프로그램 : 앵커 ②','앵커 ②  역사문화예술과 창작','K-헤리티지·역사문화예술: 시 구상 1-1·1-2, 규제 적합 최고(분동 1~3층 지상). 창작 스튜디오·공방: 예술인 675명(경북 시 1위이나 전국 평균 이하), 창작예술업 1만 명당 5.2명. 부족: 이용자 원단위·운영 주체·입주 의향.');
 await img(s,PH+'/ph58_site_tracks_north.jpg',0.5,1.45,4.2,2.6,'cover'); cap(s,'폐선로와 노반 · 철도 흔적 보행길의 소재',0.5,4.1,4.2,0.3);
 await img(s,PH+'/ph60_site_remnants_e.jpg',0.5,4.45,4.2,2.0,'cover'); cap(s,'철도 잔존 시설 · 전시·체험의 소재(2026.09)',0.5,6.5,4.2,0.3);
 rect(s,5.0,1.45,3.8,5.3,G1); rect(s,9.03,1.45,3.8,5.3,G1);
 T(s,'K-헤리티지 · 역사문화예술',5.2,1.6,3.5,0.4,{size:14,bold:true,color:RED}); T(s,'구 역사·철도기억관 · 근대역사 전시관 · 공연장 · 문화유산 창작·교육 · 방문자 관문',5.2,2.0,3.5,0.5,{size:10,color:G4,ls:1.2});
 stat(s,'2,807','㎡','구 역사 1,404㎡ × 2층 실측 · 철도기념물(2013)',5.2,2.6,3.4,{size:22,dsize:9.5});
 stat(s,'79.1','%','현장 체류 1~3시간 → 전시·체험·공연·교육의 체류 장치',5.2,3.7,3.4,{size:22,color:INK,dsize:9.5});
 bullets(s,['시 구상 1-1·1-2 K-헤리티지 복합거점에 직접 대응합니다  [T2]','저층 1~3층 분동·지상 구성으로 고도·매장유산 규제 적합성이 가장 높습니다','부족한 것: 이용자 원단위(교토철도박물관 원단위로 대체) · 운영 주체·재원'],5.2,4.85,3.5,1.85,{size:10,psa:3});
 T(s,'창작 스튜디오 · 공방 (보조 앵커)',9.23,1.6,3.5,0.4,{size:14,bold:true,color:INK}); T(s,'창작 레지던시 · 역사·공예 체험관 · 시장 접점',9.23,2.0,3.5,0.5,{size:10,color:G4,ls:1.2});
 stat(s,'675','명','경주 예술인 수 · 경북 시 1위, 전국 평균 이하  [T2]',9.23,2.6,3.4,{size:22,color:INK,dsize:9.5});
 stat(s,'5.2','명','창작예술업 종사자(인구 1만 명당)  [T2]',9.23,3.7,3.4,{size:22,color:INK,dsize:9.5});
 bullets(s,['방문객과 주민이 만나는 접점 장치(공개 공방·오픈스튜디오·시장 쇼케이스)입니다','방문 지출이 공예인·예술인 소득으로 이어지는 자리입니다(조건 01)','부족한 것: 임대 수요·입주 의향 → 예술인의 6/12/20% 입주를 3개 안으로 둡니다'],9.23,4.85,3.5,1.85,{size:10,psa:3});
 SRC(s,'김권일 발표자료(2026) · KOSIS 경제총조사(예술) · 한국예술인복지재단 · 권역 구성도는 37쪽 참조');}
// 36 기타 프로그램과 비교안
{const s=slide('프로그램 : 기타','기타 프로그램과 비교안','공공청사·의회: 시 구상 2단계(민자·시청 이전 포함), 국비 대상 제외, 정원 850/942/960 상충 → 법정 상한 방식(21,110㎡ + 가산 15% = 24,276㎡). 혁신지구 선정 17곳 중 청사 포함 3곳은 1.2~1.4만㎡. 모빌리티·상업·숙박은 선택 제안.');
 const rows=[['항목','본 계획의 위치','근거와 판단','위험·대응'],[{text:'공공청사·의회',bold:true},'포함 · 북측 확산 거점(SPREAD)','상위계획 반영 · 시 구상은 2단계 민자유치(시청 이전 포함) · 국비 대상 제외  [T2]','단일 대형·저녁 공동화(울산형) → 저층 분동, 정원 상충(850~960) → 법정 상한 24,276㎡'],[{text:'모빌리티 허브',bold:true},'선택 제안(모빌리티 대합실)','시 구상 3대 전략 중 하나 · 시민 요구 교통거점 2위(16건)  [T2]','면적 소요가 작아 단독 앵커 아님 · 환승 수요·운영 미확인'],[{text:'성동시장 연계 상업·식음',bold:true},'선택 제안','시 구상 3-3 K-F&C 마켓 · 생활업종 87.8% 자산  [T2]','성동시장·중앙상가 250억 사업과 중복(치환 위험) → 시장 보정 20~45%'],[{text:'소규모 숙박(경주 STAY)',bold:true},'선택 제안','시 구상 경주 STAY · 도시민박 2→21곳 증가  [T2]','주거 수요와 경합 → 도시민박 등록 수·월세 감시']];
 table(s,rows,0.5,1.45,12.33,[2.0,2.6,4.1,3.63],{size:10,rowH:0.75});
 rect(s,0.5,5.5,12.33,1.25,G1);
 T(s,'선택 제안 3개를 더하면 기준안 총 연면적은 110,852㎡에서 118,931㎡로 늘고 건폐율 17.7% → 19.3%, 용적률 81.2% → 87.1%가 됩니다. 빼도 나머지 면적표는 유지됩니다.',0.7,5.62,12.0,0.55,{size:10.5,bold:true,ls:1.25});
 T(s,'시청·의회 이전은 시의 의사결정 문서가 없으므로 1·2단계를 구분해 표기하고, 분산 삽입형 대안 시나리오를 함께 냅니다.',0.7,6.2,12.0,0.45,{size:10,color:G4});
 SRC(s,'20261010 2파트 §2·§3.5 · 도시재생 혁신지구 가이드라인 · 경주시 구상(김권일 2026) · 공유재산법 시행령');}
// 37 권역 구성과 프로그램 역할
{const s=slide('프로그램 : 권역','권역 구성과 프로그램의 역할','라이노 최종 획지(2026.10.11)를 권역 A~E로 읽었다. 권역 ↔ 전략 ↔ 문제·목표 대응과 4부류(연결·접점·정주 성장·기반 장치). 문제 번호는 26쪽 기준.');
 await img(s,A+'/zones_map.png',0.5,1.35,3.0,5.45,'contain','left');
 const rows=[['권역','주요 프로그램','전략','문제 · 목표'],[{text:'A  공공청사·의회',bold:true},'본청·의회 청사','SPREAD','③ · 목표 ③'],[{text:'B  일상생활',bold:true},'청년·신혼 주거 600세대 · 생활편의 · 주민 공동시설 · 생활체육','SPREAD','⑤ · 목표 ③'],[{text:'C  청년 업무권',bold:true},'창업 입주사무실 · 공유 오피스 · 교육·협업실','SPREAD · EXCHANGE','③ · 목표 ③'],[{text:'D  창작·체험권',bold:true},'창작 레지던시 · 역사·공예 체험관 · 시장 접점','EXCHANGE','④ · 목표 ②'],[{text:'E  역사문화예술권',bold:true},'구 역사·철도기억관 · 근대역사 전시관 · 공연장 · 창작·교육 · 방문자 관문','EXCHANGE','① ④ · 목표 ① ②'],[{text:'야외·공공공간',bold:true},'문화광장 · 철도 흔적 보행길 · 정원 · 생활공원 · 텃밭','CONNECT','① ② · 목표 ①']];
 table(s,rows,3.8,1.45,9.03,[1.9,4.2,1.5,1.43],{size:10,rowH:0.44});
 label(s,'프로그램의 네 부류',3.8,4.75,6);
 const kinds=[['연결 장치','문화광장 · 철도 흔적 보행길 · 방문자 관문 · 연결 안내','CONNECT · 동선을 부지 밖(황오동·성동시장·남측)으로 내보냅니다'],['접점 장치','시장 접점 · 공개 공방 · 체험관 · 오픈스튜디오 · 기획전시','EXCHANGE · 방문 지출이 주민 소득·일자리로 이어지는 자리'],['정주·성장 장치','청년·신혼 주거 · 보육·커뮤니티 · 청년 업무권 · 공공청사','SPREAD · 저녁 이후 사람이 남고 청년 일자리를 만듭니다'],['기반 장치','수장고 · 운영실 · 보존·복원 작업실 · 주차전용건축물','전시·보존·운영의 전제']];
 kinds.forEach((k,i)=>{const x=3.8+(i%2)*4.55, y=5.1+Math.floor(i/2)*0.85; rect(s,x,y,0.1,0.7,i<3?RED:G3); T(s,k[0],x+0.22,y,4.2,0.25,{size:10.5,bold:true}); T(s,k[1],x+0.22,y+0.24,4.25,0.25,{size:9,color:G4}); T(s,k[2],x+0.22,y+0.46,4.25,0.25,{size:9,color:G4});});
 SRC(s,'권역 구성도: 라이노 계획 프레임 획지(최종) · 회색 = 주차·오픈스페이스·보행공간 · 전략·부류 대응은 20261011 면적표 v2 §1');}
// 38 세부 프로그램 구성
{const s=slide('프로그램 : 세부','세부 프로그램 구성 (기준안, ㎡)','실별 면적은 20261011 프로그램 면적표 v2 §3.2 기준안. 중복 정리: 레지던시 통합, 교육실 통합, 방문자 관문 5개 실 총량 산정. 상설전시 서사는 1918 사정동 개업 → 1936 현 위치 → 2021 폐역 세 시점.');
 const cols=[['A  공공청사·의회','24,276','본청·의회 청사 24,276\n(법정 상한 21,110 + 편의·법정시설 가산 15%)\n\n시 구상 2단계 사안 · 1·2단계 구분 표기'],['B  일상생활','30,394','청년·신혼 주거 600세대 28,182\n생활편의점 72 · 카페 200\n주민 커뮤니티홀 450 · 작은도서관 120\n공동부엌 52 · 보육실 300 · 생활관리실 100\n그늘쉼터 파빌리온 90\n법정 주민공동시설 보충 828'],['C  청년 업무권','9,670','청년 창업 입주사무실 5,285\n공유 오피스 3,523\n창업 상담·멘토링실 90\n직무교육실 266 · 공동회의실 160\n분야별 협업실(건축·디자인·관광·문화유산) 266\n공동작업 쉼터 80'],['D  창작·체험권','6,225','창작 레지던시 4,501\n개인 작업실 2,673 · 작가 체류실 707 · 공동 제작공방 405 · 오픈스튜디오 150 · 교류실 80 · 보관실 486\n역사·공예 체험관 1,465\n철도·원도심 체험전시 815 · 전통공예 200 · 디지털 기록 100 · 어린이·가족 200 · 결과물 전시 150\n시장 접점 260\n쇼케이스 80 · 공예품 전시판매 120 · 픽업 거점 60'],['E  역사문화예술권','9,566','구 역사·철도기억관 3,087\n구 역사 보존·활용 2,807 · 아카이브 160 · 복원 작업실 120\n근대역사 전시관 1,435\n상설 900 · 기획 231 · 지역 예술가 150 · 공용 154\n공연·시민문화 3,448\n공연장 350석 3,003 · 연습실 160 · 다목적실 285\n문화유산 창작·교육 984 · 방문자 관문 338 · 수장고·운영실 274']];
 cols.forEach((c,i)=>{const x=0.5+i*2.5; rect(s,x,1.45,2.35,0.75,i<3?RED:DARK); T(s,c[0],x+0.12,1.5,2.15,0.35,{size:11,bold:true,color:WH}); T(s,c[1]+' ㎡',x+0.12,1.84,2.15,0.3,{size:12,bold:true,num:true,color:WH}); rect(s,x,2.2,2.35,4.05,G1); T(s,c[2],x+0.12,2.3,2.15,3.9,{size:9,ls:1.25});});
 rect(s,0.5,6.35,12.33,0.5,INK); T(s,'야외·공공공간(연면적 아님) 17,464㎡  문화광장 3,000 · 야외 전시마당 1,200 · 역사 정원 2,000 · 철도 흔적 보행길 5,664(944 m × 6 m) · 생활공원·그늘쉼터 5,000 · 공동텃밭 600  —  프로그램 연면적 합(주차 제외) 80,132㎡',0.65,6.35,12.0,0.5,{size:9.5,color:WH,valign:'middle'});
 SRC(s,'20261011 프로그램 면적표 v2 §3.2·§4 기준안 · 보수/적극 값과 가정 표시는 산정표 참조');}
// 39 구분
divider('04','대상 인구와 개발 규모','이용자 가정 · 방문·근로·정주 인구 산정 · 산정 방법 3유형 · 프로그램별 면적 · 개발규모 산정표 · 규제 정합');
// 40 대상 인구와 이용자 가정
{const s=slide('대상 인구 : 가정','대상 인구와 이용자 가정','방문: 외지인 일평균 140,085명(13개월, 통신 추정) × 포획률 5.9/7.9/10.6%(가정). 근로: 청년 업무 604/906/1,208명 + 공공청사 정원 약 850~960명. 정주: 450/600/750세대, 청년 80%(1.0인/호)·신혼 20%(2.65인/호). 인근 주민 S2 4개 동 30,261명(2026.08).');
 const cols=[['방문 인구','11,067','명/일','8,265 ~ 14,849','외지인 일평균 140,085명 × 포획률 7.9%(5.9 ~ 10.6, 가정) · 설계일 ×1.48 · 피크 1시간 7.0%  [T2 관광데이터랩 · 소상공인365]'],['근로 인구','906','명','604 ~ 1,208','청년 일자리 목표 = 20~34세 연평균 순유출 1,208명의 75%(50 ~ 100%, 정책 가정) + 공공청사·의회 정원 약 850 ~ 960명(면적은 법정 상한)  [T2·T1]'],['정주 인구','798','명','598 ~ 998','청년·신혼 주거 600세대(450 ~ 750) · 청년 80% × 1.0인 + 신혼 20% × 2.65인  [T1 주택공급규칙]']];
 cols.forEach((c,i)=>{const x=0.5+i*4.2; rect(s,x,1.45,3.9,3.2,G1); T(s,c[0],x+0.2,1.58,3.5,0.35,{size:13,bold:true}); RUNS(s,[{t:c[1],num:true,size:32,bold:true,color:RED},{t:' '+c[2],size:13,bold:true,color:RED}],x+0.2,1.95,3.5,0.75,{valign:'bottom'}); T(s,'보수 ~ 적극  '+c[3],x+0.2,2.75,3.5,0.3,{size:10.5,num:true,color:G4}); T(s,c[4],x+0.2,3.1,3.5,1.5,{size:9.5,ls:1.25});});
 label(s,'이용자 지표 (산정값)',0.5,4.85,6);
 table(s,[['항목','보수','기준','적극'],['방문 유동(평균일, 명)','8,265','11,067','14,849'],['방문 유동(설계일, 명)','12,232','16,379','24,501'],['피크 1시간 도착(명)','795','1,147','1,911'],['청년 일자리(명)','604','906','1,208'],['거주 세대 / 거주 인구(명)','450 / 598','600 / 798','750 / 998']],0.5,5.12,8.0,[3.2,1.6,1.6,1.6],{size:9.5,rowH:0.25,numCols:[1,2,3]});
 rect(s,8.8,4.85,4.03,1.85,G1); T(s,'인근 주민 (S2)',8.95,4.95,3.7,0.3,{size:10.5,bold:true,color:RED}); T(s,'황오·황남·성건·월성 4개 동 30,261명(2026.08) · 0~4세 219명 · 5~14세 917명 · 65세 이상 12,374명(40.9%)  [T2 주민등록]\n부지 주민만으로 상업을 지탱하지 못하므로 방문·S2 인구를 합산합니다.',8.95,5.28,3.75,1.35,{size:9.5,ls:1.25});
 SRC(s,'한국관광데이터랩(경주시 보고서 인용) · 소상공인365 · KOSIS · 주택공급에 관한 규칙 · 가정 항목은 민감도(보수·적극)로 표시');}
// 41 방문 인구 산정
{const s=slide('대상 인구 : 방문','방문 인구의 산정','포획률 근거: 현재 폐역 구역 0.9%, 구역 중심 반경 300m 7.9%, 성동시장급 10.6%, 황리단길급 15.3%(상한 참조) — 로컬 소상공인365 비교. 설계일 계수는 일별 P90·P95 직접 계산. 통신 유동은 거주·직장 포함 상한 성격.');
 const steps=[['외지인 일평균 방문','140,085','명','13개월 평균 · 통신 추정  [T2]'],['× 대상지 포획률','5.9 / 7.9 / 10.6','%','가정 · 현재 폐역 구역 0.9%, 구역 중심 300 m 7.9%, 성동시장급 10.6%'],['= 평균일 방문 유동','8,265 / 11,067 / 14,849','명','보수 / 기준 / 적극'],['× 설계일 계수','1.48 / 1.48 / 1.65','','일별 P90 · P95 직접 계산  [T2]'],['= 설계일 방문','12,232 / 16,379 / 24,501','명',''],['× 피크 1시간 비율','6.5 / 7.0 / 7.8','%','시간대별 분포  [T2]'],['= 피크 1시간 도착','795 / 1,147 / 1,911','명','방문자 관문·광장·체험관 동시 수용의 기준']];
 steps.forEach((st,i)=>{const y=1.45+i*0.76; const w=7.6-i*0.45; rect(s,0.5,y,w,0.62,i%2===0?G1:WH,i%2===0?null:{color:G2}); T(s,st[0],0.65,y,2.6,0.62,{size:11,bold:st[0].startsWith('='),valign:'middle'}); RUNS(s,[{t:st[1],num:true,size:13,bold:true,color:st[0].startsWith('=')?RED:INK},{t:st[2]?' '+st[2]:'',size:10,color:G4}],3.3,y,w-2.9,0.62,{valign:'middle'}); T(s,st[3],8.4,y+0.08,4.4,0.5,{size:9.5,color:G4,ls:1.2});});
 SRC(s,'관광데이터랩(경주시 보고서 인용)·소상공인365 로컬 계산 · 포획률·피크 비율은 가정, 보수/적극 열이 민감도');}
// 42 근로·정주 인구 산정
{const s=slide('대상 인구 : 근로·정주','근로·정주 인구의 산정','청년 일자리 = 순유출 1,208명/년 × 50/75/100%(정책 가정) → 1인당 7.2㎡ × 공용·지원 가산. 600세대: ① 원도심 청년 격차 회복 360~590 ② 신혼 저량 215~430쌍 ③ 면적 용량 634 ⑤ 시설 임계 300·500 ⑧ 서울 철도부지 사례 469~1,112 ⑩ 공실 위험(경북 소형 공가 14.7%, 원문 미확인) → 단계 200×3.');
 label(s,'청년 일자리 (정책목표형)',0.5,1.45,5);
 const js=[['20~34세 순유출 누계','7,249명 (2020–2025)'],['÷ 6년','1,208명/년'],['× 회수 목표 50 / 75 / 100%','604 / 906 / 1,208명'],['× 1인당 7.2㎡ × 공용·지원 가산','청년 업무 6,050 / 9,670 / 13,664㎡']];
 js.forEach((j,i)=>{const y=1.8+i*0.72; rect(s,0.5,y,5.2,0.6,i===3?RED:G1); T(s,j[0],0.65,y,2.6,0.6,{size:10.5,color:i===3?WH:INK,valign:'middle'}); T(s,j[1],3.2,y,2.4,0.6,{size:11,bold:true,num:true,color:i===3?WH:INK,valign:'middle'});});
 T(s,'공공청사·의회 정원은 문서마다 850 · 942 · 약 960명으로 달라 인원이 아니라 법정 상한(공유재산법 시행령)으로 면적을 정했습니다.',0.5,4.75,5.2,0.7,{size:10,color:G4,ls:1.25});
 label(s,'청년·신혼 주거 600세대 — 여러 렌즈의 겹침',6.1,1.45,6.7);
 const lo=300, hi=1150, X0=6.1, X1=12.6; const px=v=>X0+(v-lo)/(hi-lo)*(X1-X0);
 [300,450,600,750,900,1100].forEach(v=>{ln(s,px(v),1.85,px(v),5.0,G2,0.5,false,'dash'); T(s,String(v),px(v)-0.3,5.02,0.6,0.25,{size:9,num:true,color:G4,align:'center'});});
 const lens=[['① 원도심 청년 격차 회복',360,590],['② 신혼 저량·유량(몫 5~10%)',215,430],['③ 면적 용량(36㎡ 기준)',634,634],['⑤ 시설 임계(어린이집 300 · 공동시설 500)',300,500],['⑧ 서울 철도부지 승인 밀도 적용',469,1112]];
 lens.forEach((l,i)=>{const y=1.95+i*0.55; T(s,l[0],X0,y-0.22,3.6,0.22,{size:8.5,color:G4}); const a=Math.max(l[1],lo), b=Math.min(l[2],hi); if(l[1]===l[2]) rect(s,px(a)-0.03,y,0.06,0.2,INK); else rect(s,px(a),y,px(b)-px(a),0.2,i===4?G3:INK);});
 rect(s,px(450),4.75,px(750)-px(450),0.2,PINK); rect(s,px(600)-0.04,4.68,0.08,0.34,RED);
 T(s,'기준 600 (450~750) · 예비 900',px(600)-1.0,4.42,2.0,0.25,{size:9.5,bold:true,color:RED,align:'center'});
 bullets(s,['⑩ 공실 위험(지방 소형 임대의 공가·계약률)에 따라 약 200세대씩 3단계로 공급하고 입주율을 확인한 뒤 다음 단계로 갑니다.','청년 80% × 1.0인 + 신혼 20% × 2.65인 = 798명(450세대 598 · 750세대 998). 전용 26.58 / 36㎡ ÷ 전용률 0.606 → 주거 연면적 28,182㎡.'],6.1,5.4,6.7,1.4,{size:10,psa:3});
 SRC(s,'KOSIS 국내인구이동통계 · 주민등록 2026.08 · 혼인·신혼부부 통계 · 주택공급규칙 · 20261008 청년·신혼 주거 규모 산정 v1');}
// 43 산정 방법과 프로그램별 면적
{const s=slide('개발 규모 : 산정','산정 방법 3유형과 프로그램별 면적','① 정책목표형(청년 일자리·청년주거: 목표 인원 → 면적) ② 수요추정형(문화·체험·관문: 방문 유동 → 이용자 → 면적) ③ 법정·기준형(청사 상한·주차 조례·주민공동시설·밀도 1.9/3.33/4.6㎡/인). 권역별 소계는 보수/기준/적극.');
 const ty=[['① 정책목표형','청년 일자리 · 청년·신혼 주거','목표 인원 → 1인당 면적 → 연면적'],['② 수요추정형','문화·체험·방문자 관문 · 레지던시','방문 유동 → 이용 비율·동시 체류 → 밀도 → 면적'],['③ 법정·기준형','공공청사 상한 · 주차 조례 · 주민공동시설','법정 상한·소요 기준 → 면적']];
 ty.forEach((t,i)=>{const x=0.5+i*4.2; rect(s,x,1.45,3.9,1.15,G1); T(s,t[0],x+0.2,1.52,3.5,0.3,{size:12,bold:true,color:RED}); T(s,t[1],x+0.2,1.84,3.5,0.3,{size:10,bold:true}); T(s,t[2],x+0.2,2.14,3.5,0.4,{size:9.5,color:G4});});
 label(s,'권역별 프로그램 연면적 (㎡, 주차 제외)',0.5,2.8,7);
 colG(s,['A 공공청사·의회','B 일상생활','C 청년 업무','D 창작·체험','E 역사문화예술'],[{name:'보수',values:[17844,18220,6050,2696,7436]},{name:'기준',values:[24276,30394,9670,6225,9566]},{name:'적극',values:[27920,48613,13664,13389,12890]}],0.5,3.05,7.8,3.75,{colors:[G3,RED,DARK],labels:true,max:56000,gap:40});
 label(s,'기준안 구성비 (프로그램 연면적 80,132㎡)',8.6,2.8,4.2);
 donut(s,['A 공공청사·의회 30.3%','B 일상생활 37.9%','C 청년 업무 12.1%','D 창작·체험 7.8%','E 역사문화예술 11.9%'],[24276,30394,9670,6225,9566],8.6,3.05,4.23,2.9,{legend:'b'});
 T(s,'방문 증가가 목표인 D+E는 20%에 그칩니다. 포획률(적극 10.6%)과 체험관 이용 비율을 올리면 커집니다.',8.6,6.0,4.23,0.8,{size:10,color:G4,ls:1.25});
 SRC(s,'20261011 프로그램 면적표 v2 §3.3 · 밀도 기준: 소방 1.9 / 교습소 3.33 / 집회 4.6㎡/인 [T1]');}
// 44 개발규모 산정표
{const s=slide('개발 규모 : 산정표','개발규모 산정표','최종 경계 228,025㎡(라이노 합집합), 대지면적은 건축 획지 합 136,473㎡(59.9%). 도로 20,372·보행공간 54,044·오픈스페이스 17,135. 주차: 경주시 조례(문화·판매·업무 100㎡/대, 근생·숙박 200㎡/대, 주거 0.7대/세대), 지상 주차전용건축물 5층. 층수 가정: 공공청사 5F 20m, 주거 6F 18m, 문화·창작 3F, 주차 5F.');
 label(s,'토지이용 (라이노 계획, ㎡)',0.5,1.45,4);
 donut(s,['건축 획지 136,473','보행공간·광장 54,044','도로 20,372','오픈스페이스 17,135'],[136473,54044,20372,17135],0.5,1.75,4.2,2.9,{legend:'b',colors:[RED,G3,G4,G2]});
 T(s,'계획 경계 228,025㎡ = 건축 획지 59.9% + 보행공간 23.7% + 도로 8.9% + 오픈스페이스 7.5%',0.5,4.75,4.2,0.7,{size:10,color:G4,ls:1.25});
 T(s,'지침의 개발규모 산정표 형식으로 작성했으며, 주요 도입기능별 면적과 구성비는 43쪽에 있습니다.',0.5,5.5,4.2,0.8,{size:10,ls:1.25});
 const rows=[['항목','보수','기준','적극'],['계획 경계(㎡)','228,025','228,025','228,025'],['대지면적(㎡, 건축 획지 합)','136,473','136,473','136,473'],['건축면적(㎡)','15,999','24,108','35,070'],['프로그램 연면적(주차 제외, ㎡)','52,247','80,132','116,476'],['주차 소요(대, 경주시 조례)','686','960','1,258'],['주차전용건축물(㎡, 지상)','20,588','30,720','44,037'],[{text:'총 연면적(주차 포함, ㎡)',bold:true},{text:'72,836',bold:true},{text:'110,852',bold:true,color:RED},{text:'160,513',bold:true}],[{text:'건폐율(%)',bold:true},'11.7',{text:'17.7',bold:true,color:RED},'25.7'],[{text:'용적률(%, 주차 포함)',bold:true},'53.4',{text:'81.2',bold:true,color:RED},'117.6'],['용적률(%, 주차 제외)','38.3','58.7','85.3'],['최고 높이 · 층수','20.0 m · 5층','20.0 m · 5층','20.0 m · 5층'],['층수 가정',{text:'공공청사 5F(20 m) · 주거 6F(18 m) · 문화·창작 3F · 주차전용 5F(15 m)',options:{colspan:3}}],['선택 제안 3개 포함 시(기준)',{text:'총 연면적 118,931㎡ · 건폐율 19.3% · 용적률 87.1%',options:{colspan:3}}]];
 table(s,rows,5.0,1.45,7.83,[3.0,1.6,1.6,1.63],{size:10,rowH:0.33,numCols:[1,2,3]});
 SRC(s,'calc/part2_model_final.py(2026.10.11, 최종 경계 반영) · 경주시 주차장 조례 별표 8 · 건축법 시행령 제119조 · 가정 항목은 보수·적극 열이 민감도');}
// 45 규제 정합과 다음 단계
{const s=slide('개발 규모 : 검토','규제 정합과 다음 단계','높이 20m는 도심 20m 지구(84.5%)와 같아 여유가 없고 15m 지구(12.7%)·최저고도(3.7%)는 필지별 확인. 자연녹지(74.7%) 건폐율 20%·용적률 100% 안이나 주거·업무 용도는 용도지역 변경(특별계획구역·세부개발계획) 필요. 주차 지상, 공개공지 완화 1.2배 경로.');
 label(s,'규제 정합 (기준안)',0.5,1.45,6);
 const rg=[['높이','20.0 m ≤ 도심 20 m 지구(경계의 84.5%) · 15 m 지구 12.7%와 최저고도 3.7%는 필지별 확인','적합(조건부)'],['건폐율·용적률','17.7% · 81.2% — 자연녹지(74.7%) 한도 20% · 100% 안. 주거·업무 용도는 용도지역 변경 경로(특별계획구역·세부개발계획) 필요','적합(용도 변경 전제)'],['주차','960대 지상 주차전용건축물(건폐율 90%·용적률 1,500% 허용) · 매장유산으로 지하 불가 · 차 없는 거리 목적 완화(지침 3-2-5)','적합'],['매장유산','지하 0 · 성토 2 m 미만 · 보호·전시 전용 부분 건축면적 불산입 · 시굴 후 배치 재검토','조건부'],['완화 경로','공개공지 문화·판매·숙박 10%, 업무 5% → 용적률·높이 1.2배 (경주시 건축 조례) · 도시재생특별법 §32·§54','검토']];
 rg.forEach((r,i)=>{const y=1.8+i*0.82; rect(s,0.5,y,1.5,0.7,i<2?RED:G4); T(s,r[0],0.5,y,1.5,0.7,{size:11,bold:true,color:WH,align:'center',valign:'middle'}); T(s,r[1],2.15,y+0.02,4.9,0.7,{size:9.5,ls:1.2}); T(s,r[2],7.1,y+0.18,1.2,0.35,{size:10,bold:true,color:i<2?RED:INK});});
 rect(s,8.6,1.45,4.23,2.5,G1); T(s,'가정이 큰 곳 (민감도 열 참조)',8.75,1.55,3.9,0.3,{size:11,bold:true,color:RED});
 bullets(s,['포획률 5.9 ~ 10.6% · 체험관 이용 5 ~ 12%','청년 일자리 목표 50 ~ 100% · 레지던시 입주 6 ~ 20%','공연장 350석 수요(약함) · 야외공간 규모','공공청사 1·2단계 구분 · 구 역사 이전 여부 · 데크·공중광장 기초 규제'],8.75,1.9,3.95,2.0,{size:9.5,psa:2});
 rect(s,8.6,4.1,4.23,2.7,INK); T(s,'다음 단계',8.75,4.2,3.9,0.3,{size:11,bold:true,color:RED});
 const nx=[['1','배치 구상안','도로·필지·건물·공공공간'],['2','단면 조닝','긴 방향 단면의 수직 조닝'],['3','3D 볼륨','모형 또는 모델링 컷'],['4','단계·운영','가역 순서 · 운영 주체·재원 · 입주확약']];
 nx.forEach((n,i)=>{const y=4.55+i*0.55; T(s,n[0],8.75,y,0.35,0.4,{size:14,bold:true,num:true,color:RED}); T(s,n[1],9.15,y+0.02,1.4,0.3,{size:10.5,bold:true,color:WH}); T(s,n[2],10.5,y+0.04,2.3,0.4,{size:9,color:G3,ls:1.15});});
 T(s,'규제 비율은 최종 경계 228,025㎡ 기준으로 2026.10.11 재산정했습니다. 접속점·우회율은 이전 분석 경계, 시굴 비율은 철도 부지 기준이며 다음 단계에서 재산정합니다.',0.5,6.0,7.8,0.8,{size:10,color:G4,ls:1.25});
 SRC(s,'경북 고시 제2020-479호 · 경주시 도시계획·건축·주차장 조례 · 지구단위계획수립지침 · 매장유산법 · 도시재생특별법');}
// ---------- 저장 ----------
const out=__dirname+'/../output/구경주역_중간마감_1-4부_v1.pptx';
await pres.writeFile({fileName:out}); console.log('written',out,'slides',page);
})().catch(e=>{console.error(e);process.exit(1);});
