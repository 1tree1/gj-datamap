import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';

const ROOT='C:/Users/OFFICE/Desktop/9_도시/work/20261012_final_toc_sources';
const p=Presentation.create({slideSize:{width:1280,height:720}});
p.theme.defaultFont='Pretendard';
const C={ink:'#231F20',blue:'#2D77A6',sub:'#6D6E71',pale:'#F5F6FA'};
let shapeId=0;
function text(s,v,x,y,w,h,size,color=C.ink,bold=false,alignment='left'){
  const q=s.shapes.add({geometry:'textbox',name:'source-text-'+(++shapeId),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  q.text=v;q.text.style={fontSize:size,typeface:'Pretendard',color,bold,alignment,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};
  return q;
}
function sourceSlide(title,rows,page,foot,notes){
  const s=p.slides.add();s.background.fill='#FFFFFF';
  text(s,'자료 : 출처',61,35,1050,26,16.24,C.blue);
  text(s,title,61,66,1150,43,26.667,C.ink,true);
  const rowHeight=rows.length===9?52:58;
  const values=[['자료·제공 기관','기준 시점·범위','활용 데이터·내용','사용 슬라이드'],...rows];
  const tb=s.tables.add({rows:values.length,columns:4,left:58,top:145,width:1164,height:36+rows.length*rowHeight,columnWidths:[420,188,436,120],values});
  tb.styleOptions={headerRow:false,bandedRows:false};tb.borders.assign({fill:'none',width:0});
  tb.cells.block({row:0,column:0,rowCount:values.length,columnCount:4}).assign({fill:'#FFFFFF',textStyle:{fontSize:14.5,typeface:'Pretendard',color:C.ink,bold:false},margins:{left:8,right:8,top:3,bottom:3},anchor:'center'});
  for(let r=0;r<values.length;r++){
    tb.rows[r].height=r===0?36:rowHeight;
    for(let c=0;c<4;c++){
      const cell=tb.getCell(r,c);
      cell.fill=r===0?C.ink:(r%2===0?C.pale:'#FFFFFF');
      cell.text.style={fontSize:r===0?15:14.5,typeface:'Pretendard',color:r===0?'#FFFFFF':(c===3?C.sub:C.ink),bold:r===0,alignment:c===3?'center':'left',verticalAlignment:'middle'};
    }
  }
  text(s,foot,61,665,1110,21,12.6,C.sub);
  text(s,String(page),1185,682,39,24,14,C.sub,false,'right');
  s.speakerNotes.text=notes;
  return s;
}

sourceSlide('데이터 출처 ① 현황·공공데이터',[
 ['국토지리정보원·V-World·OpenStreetMap\n연속수치지도·연속지적·공원·철도\n정사영상·과거 항공사진','지도 2026.09.13\n영상 1954·2009·2025','도로·건물·담장·층수·필지·주변 자산 위치\n가로 방향·가시면적·거리 및 영상 비교','01–03·08–13\n22·27·39·61'],
 ['KOSIS·주민등록인구통계\n주민등록인구 / 국내인구이동통계\nDT_1B04005N / DT_1B26002','인구 2015–2025\n연령 2026.08\n이동 2020–2025','행정동별 인구 증감·청년·고령 구성\n20–34세 순이동과 가구 구성','17–19·41'],
 ['소상공인시장진흥공단, 소상공인365\n상권분석 통신 기반 추정 유동·업종','2025.06–2026.06\n13개월','성동시장·행복황촌 유동 밀도\n황리단길·시청 생활권 주중·주말 이용','15–16\n33·41·43'],
 ['국가교통정보센터 ITS\n평균 주행속도 이력 자료','2025.01–07\n주말 7일 표본','시간대별 소통 상태·정체 도로구간 수\n지도 범위 내 방향별 도로 링크 554개','14'],
 ['한국관광공사, 한국관광 데이터랩\n외지인 방문·숙박 방문 데이터','요일 2024.09–2026.08\n숙박 2025.09–2026.08','요일별 외지인 방문 지수\n통신 추정 당일·숙박 비중','20'],
 ['경주시, 제5회 관광실태조사 보고서\n황오동 원도심 도시재생 모니터링 보고서','관광 2024 조사\n내국인 n=3,009\n황오동 2024·2025','교통수단·숙박 비중·관광 불편\n황오동 방문객 체류시간·지역 이용 특성','20·33\n41–43'],
 ['경주시 미래전략실·동국대학교 산학협력단\n경주시 원도심 미래구상 기획 연구','2025.07\n인쇄쪽 33·63–64\n68·104 등','시민 요구 시설·인터뷰·시 구상\n항공사진과 대상지 사진(전홍표)','07·21\n40–43'],
 ['이승규·김민승, 현장 답사·자체 촬영\n구 경주역·성동시장·행복황촌','2026.09','노반·잔존 선로·육교·울타리\n서측 상업가로·동측 주거 골목 현장 사진','10·12·42']
],62,'원자료의 조사 대상·기간을 유지했다. 통신 추정 유동, 차량 속도, 설문 응답은 서로 다른 지표다.',
`출처 목록 ①. 사용 슬라이드는 이 수정본의 페이지 번호이며 자료 활용이 직접 확인된 주요 페이지를 표기했다.

1. 국토지리정보원: https://www.ngii.go.kr/ ; 국토정보플랫폼 https://map.ngii.go.kr/ . 원본 발표자 노트의 NGII 2026.09.13 연속수치지도, 건물 N3A_B0010000의 nmly(지상층수), 도로중심선·담장 자료. 역사영상 1954/2009/2025. V-World https://www.vworld.kr/ , UPIS 도시계획정보의 공원·지적 자료, OSM https://www.openstreetmap.org/ . 층수와 실제 높이(m)는 구분한다. 1954 영상은 근사 정합.
2. KOSIS https://kosis.kr/ . DT_1B04005N 주민등록인구, DT_1B26002 국내인구이동통계. 2015–2025 연말 인구, 2026.08 연령별 구성, 2020–2025 20–34세 순이동. 황오동 통합 전 연도는 중부동을 합산한 시계열. 가구 및 예술인 등 기존 검토안의 보조 통계는 KOSIS 인구총조사·경제총조사 및 원자료 기록을 따른다.
3. 소상공인365 https://bigdata.sbiz.or.kr/ . 2025.06–2026.06 13개월 평균 추정 유동·업종. 성동시장 반경200m, 황리단길 반경300m, 시청 반경500m, 행복황촌 근사 경계. 집계 구역이 중첩되므로 합산하지 않는다.
4. 국가교통정보센터 https://www.its.go.kr/ . 주말 표본일 2025.01.11,02.08,03.08,04.12,05.10,06.14,07.12. 재집계 https://1tree1.github.io/gj-datamap/data/traffic_hist.geojson 및 traffic_hist_summary.json. 평균 주행속도이며 교통량(대수)과 구분한다.
5. 한국관광공사 한국관광 데이터랩 https://datalab.visitkorea.or.kr/ . 요일2024.09–2026.08, 숙박2025.09–2026.08. 재작성 자료 https://1tree1.github.io/gj-datamap/tourists.html . 월별 숙박자 비율의 단순평균. 관광실태조사와 모집단·집계방식이 다르다.
6. 경주시(2025), 제5회 경주시 관광실태조사 보고서: 2024년 조사, 내국인응답자3009명. 경주시·공공도시(주), 2024년 황오동 원도심 도시재생뉴딜사업 성과지표 및 모니터링 용역 결과보고서(2025.09) 및 관련2024·2025 보고서. 구체적인 본문·표 정보는 원래 적용 슬라이드의 발표자 노트를 유지했다.
7. 경주시 미래전략실·동국대학교 산학협력단(2025.07), 경주시 원도심 미래구상 기획 연구. 파일 C:/Users/OFFICE/Desktop/9_도시/#경주시 원도심 미래구상 기획 연구 0804 최종본.pdf. 시민 조사일2025.03.16·04.24, 유효63명, 해당문항52명 복수응답. 인쇄쪽33·63–64·68. 원본7쪽 사진은 해당연구 인쇄쪽63·104의 전홍표 사진.
8. 이승규·김민승2026.09 현장답사 사진. 기존 발표 자료에 포함된 자체 촬영 현장 사진. 육교·울타리의 개방 상태는 촬영 당시 현황.
자체 가시성·공간 통계의 재현자료: https://1tree1.github.io/gj-datamap/report.html 및 data/fabric_report.json . 국토지리정보원 자료에 기반한 자체 산출이며 공공기관의 공식 산출값과 구분한다.`);

sourceSlide('데이터 출처 ② 계획·문헌·규모 산정',[
 ['경주시 도시기본·도시재생·경관계획\n2030 기본계획 / 전략계획 변경(2022)\n2030 경관계획 재정비(2025.04)','각 계획의 발간본','철도 부지·쇠퇴 진단·재생 방향\n폐철도 녹지경관축·화랑로·조망축','03–09·33\n40–43'],
 ['법령·고시·조례·공모 지침\n경북 제2020-479호 / 경주시 제2026-8호\n도시재생 혁신지구 가이드라인 등','발표에서 인용한\n문서 기준','고도지구·용도·계획구역·사업 요건\n공유재산·주택공급·주차·건축 검토','33·40–43\n47'],
 ['김권일, (구)경주역 매장유산 현황 및\n도시재생 제언 / 구경주역 일원 시굴조사 계획','발표 2026.02.27\n시굴계획 제공본','매장유산 조건·개발 단계·시 구상\n역사문화 프로그램과 규제 검토','40–43'],
 ['경주시 청사안내·조직운영6대지표\n제299회 시의회 회의록 / 도시공원과 공고','청사 2026.09.02\n정원 2025.12.31\n공고 2026.08.13','외부 청사 위치·부서 분산\n본청 정원 877명과 계획 업무석 구분','22·51'],
 ['학술 문헌\n김신재(2013) / Paci·Marrocu(2014)\nFleming·Goetz(2011) / Sandbrook(2010) 등','문헌별 발간연도\n전체 서지는 노트','철도 연혁·관광과 소득·일자리 관계\n지역 잔류 소득과 정주 연계의 조건','08·29'],
 ['도시재생 정책·선례 자료\n국토연구원 / 국토교통부 정책\nDelft·King’s Cross·안동·푸른길·우메코지 등','원문별 발간연도\n선례 일부 2차 자료','계획목표·복합거점·보행 연결·운영\n선례의 적용 원리와 단계 구성','23–24·30'],
 ['NEXUS 1918 최종 통합 스페이스 프로그램\nv13 (주거 8동 수정) / 자체 계획 가정','2026.10.11','256세대·정주인구·업무석·체험 정원\n시설별 면적 배분·주차 공급·운영 가정','39·48–60'],
 ['Rhino 모델 측정·GIS·자체 계산\n가로·가시성 분석 / 계획 경계·획지 재집계\n기존 프로그램 검토안 산정 자료','분석 2026.09.28\n모델 2026.10.11','가로 방위·가시면적·도로·획지·토지이용\n선택 매스 157개 면적과 v13 비교','11–13·28\n32–37·44–47\n55–60']
],63,'계획 가정·모델 측정값은 공식 통계와 구분했다. 개별 URL·서지·계산 파일은 발표자 노트에 정리했다.',
`출처 목록 ②. 원본 발표에서 인용한 자료를 정리했다. 새로운 사업 승인 또는 법정 적합 판정을 의미하지 않는다.

1. 경주시, 2030 경주도시기본계획(프로젝트 제공 PDF). 경주시 도시재생 전략계획(변경,2022), 인쇄쪽138 철도부지148770㎡,150 쇠퇴원인,161 연결,290·383 자산사진. 경주시,2030 경주시 경관계획 재정비(2025.04) §4.3 경관축. 로컬 파일 2030 경주도시기본계획.pdf, 22-0124) 경주시 도시재생전략계획 최종보고서.pdf 및 관련 제공 계획본.
2. 경상북도 고시 제2020-479호(고도지구), 경주시 고시 제2026-8호(계획구역). 공유재산 및 물품 관리법 시행령, 주택공급에 관한 규칙, 경주시 주차장 조례·건축 조례 및 도시재생 혁신지구 가이드라인. 원본 발표의 인용 버전. 법령 https://www.law.go.kr/ , 경주시 자치법규 및 고시 원본. 이 목록은 최신 법정 적합성을 새로 검증한 결과가 아니다.
3. 김권일(2026.02.27), (구)경주역 매장유산 현황 및 도시재생 제언, 경주시 도시재생 국가시범지구 혁신포럼. 로컬 제공자료 04 김권일 학예연구실장_발표자료 (구경주역 매장유산 현황 및 도시재생 관련 제언).pdf. 구경주역 일원 시굴조사 계획.pdf. 매장유산·시굴·시 구상의 인용 근거.
4. 경주시 청사안내 https://www.gyeongju.go.kr/open_content/ko/page.do?mnu_uid=2701 (최종수정2026.09.02). 조직운영6대지표 https://www.gyeongju.go.kr/open_content/ko/page.do?mnu_uid=2227 (2025.12.31기준). 제299회 행정복지위원회 제2차 회의록 https://www.gyeongju.go.kr/council/viewer/minutes.do?uid=11670 . 도시공원과 채용공고2026.08.13 https://www.gyeongju.go.kr/open_content/ko/page.do?mnu_uid=435&parm_bod_uid=329117&step=258 . 외부청사 안내의 농촌활력과 중복 표기로 전체 부서 수는 합산하지 않았다. 본청877명은 공식정원이고1000석은 계획가정.
5. 철도연혁: 김신재(2013),1930년대 경주의 도시 모습과 사회변화, 신라문화41,383–406(1939노선변경 pp.387–388). 관광·소득·정주 논거: Fleming,D.A.&Goetz,S.J.(2011),Economic Development Quarterly25(3),277–281. Sandbrook,C.G.(2010),Conservation Letters3(1),21–28 및 Journal of International Development22(1),124–136. Terzioglu,M.&Gokovali,U.(2016),Tourism Economics22(4),715–728. 김규호·임배근(2013),한국지역경제연구11(2),93–115. 임태경(2024),지방정부연구28(2),87–109. 이종하·순병민(2026),지방세논집13(2),35–50. 최종민(2026),한국정책학회보35(1),199–229. 기타 관광성장연구는 work/20261010_direction_brief/research/C2_papers_tourism_youth.md의 E28·E29 및 20261010_final_direction_evidence_v1.md §2.4와 문헌목록에 추적 가능. 원본29쪽은 문헌 종합해석이며 개별 논문 하나의 결론과 구분한다. KCI·Crossref·OpenAlex는 문헌 탐색 경로이다.
6. 23쪽선례: Mecanoo,Delft Railway Station and City Hall https://www.mecanoo.nl/Projects/project/52/Delft-Railway-Station-and-City-Hall?d=0&t=20 ; King's Cross https://www.kingscross.co.uk/about-the-development . 24쪽정책: 경주시2040도시기본계획 시민참여단 도시미래상전달식2025.12.22, https://www.gyeongju.go.kr/mayor/page.do?mnu_uid=1413&parm_bod_uid=310791&step=258 ; 국토연구원,도심의 기존 기능과 연계한 점진적 도시재생방안 연구 https://library.krihs.re.kr/%24/10110/contents/5946539 ; 국토교통부·HUG 도시재생뉴딜 https://enhuf.molit.go.kr/fur/pp/ps/POPPS017M01.jsp ; 대전서구 https://seogu.go.kr/kor/sub06_14_05_01.do . 30쪽안동·우메코지·광주푸른길·부산혁신도시 및 회피사례의 원자료는 docs/20_cases 자료와 work/20261010_direction_brief/research/D_cases_verified.md. 원본이 ‘원문 교차검증 전[T3·T4]’으로 표시한 선례 수치는 그 확인 상태를 유지했다.
7. NEXUS1918 최종통합스페이스프로그램v13(2026.10.11,주거8동수정) 및 사용자 제공 계획. 정원·운영회차·이용률·주거유형인원·면적원단위·주차공급은 자체계획가정. 실제 확정수요 또는 공식통계로 표시하지 않았다. 원본49–60쪽의 개별 계산식·면적배분 노트 유지.
8. 원자료 C:/Users/OFFICE/Desktop/9_도시/work/nexus_v13_audit_20261011/facility_comparison.json, rhino_measurements.json, comparison_groups.json, placement-model-plan.json.2026.10.11 선택매스157개 실제형상측정(좌표1단위=1m해석),역사상세메시·지붕·식재제외. 앞부분 가로·가시성분석은 archive/C_data/processed/fabric_report.json, archive/90_derived/palimpsest_evidence_20260928.json 및 work/20261011_visual_front/build/evidence.json. 기존 프로그램 검토안과 도로·가구표는 work/20261011_midterm_deck/build/road_plan.py,compose_diagrams.py 및 calc의 산정자료. 공개 재집계 https://1tree1.github.io/gj-datamap/report.html ,data/fabric_report.json . 35–37쪽경계와55–60쪽저장모델경계는 원본의 구분을 유지한다.`);

const finalNotes=p.slides.items[1].speakerNotes;
finalNotes.text+='\n추가 서지: Paci,R.&Marrocu,E.(2014),Tourism and regional growth in Europe,Papers in Regional Science93(S1),S25–S51, https://doi.org/10.1111/pirs.12085 . Boto-García,D.,Balado-Naves,R.,Baños-Pino,J.F.&Mayor,M.(2026),The empirics of the tourism–growth nexus: how does tourism specialization affect regional growth paths?,The Annals of Regional Science75(4), https://doi.org/10.1007/s00168-026-01574-8 . 위 두 문헌의 확인 상태는 원본 조사기록의 초록 확인을 따른다.';
await(await PresentationFile.exportPptx(p)).save(ROOT+'/build/sources_section.pptx');
console.log('Authored two editable source slides.');
