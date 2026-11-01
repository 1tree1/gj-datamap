from pathlib import Path
B=Path(__file__).parent;P=B/'build_analysis.mjs';s=P.read_text(encoding='utf8')
a=s.index("const fr={x:48,y:183,w:780,h:375}")
z=s.index("\n}\n// 12",a)
s=s[:a]+'''const fr={x:48,y:183,w:568,h:375};await im(s,A+'/city_structure.png',fr.x,fr.y,fr.w,fr.h);
let xy=geo('city_structure',219800,361020,fr);label(s,'구 경주역',xy[0]-37,xy[1]-14,112,C.red,20);
label(s,'격자에 정렬한 가로',62,563,275,C.blue,18);label(s,'북천 변 사선 조직',348,172,247,C.sub,17);
sh(s,'rect',631,163,1,408,C.line);
const hist=JSON.parse(await fs.readFile(R+'/archive/90_derived/palimpsest_evidence_20260928.json','utf8')).orientation_hist_mod180_len_km;
t(s,'가로 방위 분포',653,163,400,30,21,false);t(s,'1° 구간별 도로 연장 (km)',1012,168,213,25,14,false,C.sub,'right');
chart(s,'bar','',hist.map((v,i)=>String(i)),[{name:'도로 연장(km)',values:hist,fill:C.grey,points:hist.map((v,i)=>({idx:i,fill:(i<=7||i>=172||Math.abs(i-89)<=7)?C.blue:C.grey}))}],650,193,575,248,{direction:'column',gap:0,min:0,max:12,unit:3,yVisible:true,xVisible:false,grid:true,labels:false});
for(const [x,lab] of [[689,'0°'],[817,'45°'],[945,'90°'],[1073,'135°'],[1202,'180°']])t(s,lab,x-20,439,46,22,14,false,C.sub,'center');
t(s,'0°·90°의 주 격자와 두 사선 방향에 연장이 집중',653,468,571,27,16,false,C.sub);
t(s,'57%',653,509,233,49,43,false,C.blue);t(s,'동일 격자 방향 ±7.5°',653,559,252,26,16,false,C.sub);
t(s,'58m',948,509,239,49,43,false,C.ink);t(s,'소가구 단변 중앙값',948,559,272,26,16,false,C.sub);
manifest[0].notes+=' 방향분포는 palimpsest_evidence_20260928.json 180개 1도 구간 도로연장(km), 좌표축 기준 방위0–180도, 양방향 동일 방향으로 집계. 그래프는 전체 도로 연장에 대한 분포이며 57%는 mod90 주격자 ±7.5도에 따른 구간 합.';
s.speakerNotes.text+='\\n가로 방위 그래프: archive/90_derived/palimpsest_evidence_20260928.json orientation_hist_mod180_len_km (180개 구간). 0도=동서,90도=남북,180도=동서. 길이 가중,1도 구간.';
''' +s[z:]
a=s.index("// 23 Cityhall")
z=s.index('// 24 Constraints',a)
s=s[:a]+'''// 23 Verified address points on a geographic map.
{
const notes='공식자료 재확인 2026.10.11: https://www.gyeongju.go.kr/open_content/ko/page.do?mnu_uid=2701 최종수정2026-09-02. 기린빌딩 양정로241-1 2–8층, 공식표9과. 동원빌딩 소금강로39 2–3층 전략기획과·미래사업과·농촌활력과3과; https://www.gyeongju.go.kr/council/viewer/minutes.do?uid=11670 (제299회 행정복지위원회 제2차)에서도2026년임차2·3층3과확인. 농촌활력과는공식층별표에기린과동원중복표기되어전체분산과수합산하지않음. 아동청소년과 알천북로131청소년수련관1층, 왕경조성과 임해로64-19황룡사역사문화관1층. 도시공원과 황성공원로29실내체육관남문지하1층:2026-08-13채용공고 https://www.gyeongju.go.kr/open_content/ko/page.do?mnu_uid=435&parm_bod_uid=329117&step=258. 본청 양정로260. 지도위치=gj-datamap/public/data/cityhall_sites.geojson VWorld도로명주소건물대표점. 직선거리본청–황룡사2060m반올림2.1km, 보행거리시간이아님. 외부5개시설의유형2임차+3시시설표시. 보건소는직속기관이므로본청부서분산집계에서제외하며이전대상확정주장없음.';
const s=base('공공행정 분산','본청 외부의 행정 부서는 5개 시설에 배치되어 있다','동천동의 임차 청사와 황성동·구황동의 개별 공공시설을 구분한다','통합 대상과 현장 밀착 부서를 구분하고, 분산된 행정 서비스의 이용 동선을 검토한다.','경주시 청사안내(2026.09.02) · 제299회 시의회 회의록 · 도시공원과 공고(2026.08.13)',notes);
const fr={x:48,y:168,w:828,h:414};await im(s,A+'/cityhall_map.png',fr.x,fr.y,fr.w,fr.h);
const m=G.find(g=>g.name==='cityhall_map');const labels=[['동천동 본청','본관·신관·별관·증축관',550,239,260,C.blue,'left'],['기린빌딩','2–8층 / 공식 안내 9개 과',513,330,293,C.orange,'left'],['동원빌딩','2–3층 / 3개 과',520,170,252,C.orange,'left'],['황룡사 역사문화관','왕경조성과 / 1층',565,495,287,C.blue,'left'],['청소년수련관','아동청소년과 / 1층',81,309,264,C.blue,'right'],['실내체육관','도시공원과 / 남문 지하1층',77,183,271,C.blue,'right']];
for(const[i,[lab,cap,x,y,w,c,side]]of labels.entries()){
 const xy=geo('cityhall_map',...m.centers[i],fr);sh(s,'ellipse',xy[0]-7,xy[1]-7,14,14,i===0?C.blue:i<3?C.orange:'#FFFFFF',i<3?'#FFFFFF':C.blue,1.5);
 const tb=t(s,lab,x,y,w,31,20,false,c);t(s,cap,x,y+28,w,26,14,false,C.sub);const d=sh(s,'ellipse',xy[0]-1,xy[1]-1,2,2,c);
 const ll=s.shapes.connect(tb,d,{kind:'straight',fromSide:side,line:{fill:c,width:.8,style:'solid'}});ll.bringToFront();
}
label(s,'구 경주역 대상지',367,424,211,C.blue,16);
t(s,'N',828,160,26,24,15,false,C.ink,'center');sh(s,'upArrow',835,188,11,27,C.ink);
ln(s,65,560,67,C.ink,1.5);t(s,'500m',65,538,105,23,13,false,C.sub);
sh(s,'rect',896,163,1,415,C.line);
t(s,'민간 임차',923,175,306,32,22,false,C.orange);t(s,'2개소',923,215,306,57,43,false,C.orange);t(s,'기린빌딩 · 동원빌딩',923,274,304,29,18,false,C.sub);
ln(s,923,324,302);
t(s,'별도 공공시설',923,345,305,32,22,false,C.blue);t(s,'3개소',923,384,305,57,43,false,C.blue);t(s,'청소년수련관 · 역사문화관\\n실내체육관',923,445,307,53,17,false,C.sub);
t(s,'본청–역사문화관 약 2.1km',923,515,308,26,18,false,C.ink);t(s,'도로명주소 대표점 간 직선거리',923,544,309,25,13.5,false,C.sub);
t(s,'※ 농촌활력과가 두 임차 청사 안내에 중복 표기되어 전체 분산 부서 수는 합산하지 않았다.',48,653,1175,21,12,false,C.sub);
}
''' +s[z:]
P.write_text(s,encoding='utf8')
f=B/'finalize.mjs';q=f.read_text(encoding='utf8').replace('[15,16,17,18,19,20,21,22]','[11,15,16,17,18,19,20,21,22]').replace('final5.validation.json','final6.validation.json');f.write_text(q,encoding='utf8')
print('Updated geographic map and native direction histogram')
