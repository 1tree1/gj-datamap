import fs from "node:fs";
import path from "node:path";
const root=path.resolve("C:/Users/OFFICE/Desktop/9_도시/work/nexus_placement_report_20261012");
const app=path.resolve("C:/Users/OFFICE/Desktop/9_도시/work/nexus_v13_audit_20261011/visual-report");
const input=JSON.parse(fs.readFileSync(path.join(root,"authoring-input.json"),"utf8"));
const snapPath=path.join(app,"src/data.json");const snapshot=JSON.parse(fs.readFileSync(snapPath,"utf8"));
if(!fs.existsSync(path.join(root,"snapshot-before-detail.json")))fs.writeFileSync(path.join(root,"snapshot-before-detail.json"),JSON.stringify(snapshot,null,2));
const old=snapshot.queries.placement.rows;
const details=old.map(r=>{
 const plot=input.mapping[r.id];let program=r.program,location=r.location;
 if(r.id==="history"){program="구 경주역 활용과 지역문화 거점";location="9번 획지의 기존 역사·역전광장·지역문화 거점";}
 const scale=input.scales[r.id]??r.scale;
 const model=plot?input.plots.find(p=>p.plot===plot):null;
 const modelText=model?"최신 도면의 "+model.plot+"번 획지는 "+model.name+"을 묶어 연면적 "+model.gfa.toLocaleString("ko-KR")+"㎡, 최고 "+model.floors+"층으로 표시한다. 이는 획지 전체의 모델 표기이며 이 프로그램만의 실 면적이나 운영 용량은 아니다.":"최신 도면의 공원·보행축 관계를 참고하며 13개 건축 획지의 합계와는 구분한다.";
 return {id:r.id,program,plot,location,scale,flow:r.movement,
 body:"### "+program+"\n\n"+location+"에 배치하는 프로그램이다. "+r.reason+"\n\n"+input.extras[r.id]+"\n\n규모와 수요의 계획 근거는 "+scale+"이다. "+modelText+"\n\n이용 동선은 "+r.movement+"으로 조직한다.",
 status:plot?"최신 도면의 권역 관계와 v13 계획값에 따른 배치 해석":"최신 도면의 외부 공공공간 관계에 따른 배치 해석"};
});
details.push(
{id:"museum",program:"근대역사관",plot:12,location:"기존 역사 동측의 12번 문화시설 획지",scale:"v13 박물관 3,500㎡·상설전시 약 300명·시민포럼 100석 계획",flow:"관문·기존 역사→사선 보행축→근대역사관→중앙 문화·창작",body:"### 근대역사관\n\n근대역사관은 기존 역사 동측의 12번 문화시설 획지에 배치한다. 기존 역사 공간에서 체험한 장소의 기억을 상설전시·자료·시민포럼·역사교육으로 해석하는 거점으로 설명한다. 남측 관문에서 진입한 방문자가 기존 역사와 박물관을 순서대로 경험하고 중앙 창작 권역으로 이어지도록 보행을 조직한다.\n\n첨부 조감도와 획지표는 4층·연면적 11,973㎡를 표시하며 사선 보행축의 상부 연결을 설명한다. 연결 요소는 기존 역사·관문·박물관을 하나의 관람 권역으로 읽게 하지만, 실제 출입·높이 변화·지상 동선이 함께 정리돼야 한다. 상부 연결이 있다고 지상에서 접근하기 쉬운 경로까지 확보됐다고 단정하지 않는다.\n\nv13 박물관 3,500㎡와 상설전시 약 300명·시민포럼 100석은 실 구성의 계획값이다. 최신 매스 11,973㎡와 범위가 다르므로 전시·교육·수장·지원·공용의 배분을 구체화해야 한다. 관람객 흐름은 공개 진입면에, 설치·자료·작품 반입은 외곽 서비스 면에 연결하는 내부 배치 제안이다.",status:"건물·권역은 도면 표기 / 내부 실·관람 경로는 후속 배정"},
{id:"great-court",program:"그레이트 코트와 역전광장",plot:9,location:"기존 역사와 남측 문화시설 사이의 공개 중정·광장",scale:"조감도의 유리 지붕 중정과 전면 역전광장 계획",flow:"역전광장→기존 역사·그레이트 코트→지역문화·근대역사관",body:"### 그레이트 코트와 역전광장\n\n그레이트 코트는 기존 역사와 주변 새 프로그램 사이에서 만남·대기·시민행사·방향 전환을 받는 공개 중정으로 설명한다. 역전광장은 기존 건물을 외부에서 인지하고 접근하는 앞마당이며 중정은 역사·지역문화·전시 방문이 서로 연결되는 내부적 공공공간이다. 두 공간을 단순한 건물 잔여 면적으로 처리하지 않고 각각의 진입·체류 역할을 정한다.\n\n유리 지붕은 중정의 외부 활동을 기후에 대응하는 공간으로 묶으려는 설계 요소다. 지붕이 있다는 사실만으로 모든 계절의 쾌적성이 확보되는 것은 아니므로 그늘·환기·우수·운영 방식과 기존 건물 접합을 상세 설계에서 검토한다. 첨부 이미지의 지붕 계획을 기존 역사 전체를 철거하거나 새 건물로 대체하는 근거로 사용하지 않는다.\n\n관광 안내와 행사 대기는 공개면에서 받고 지역문화원의 반복 이용과 작품·행사 물품 반입은 운영 동선으로 나눈다. 중앙 보행축과 사선 관문축이 이 공공공간으로 들어오는 지점은 안내와 출입의 기준점으로 계획한다.",status:"조감도의 지붕·광장 관계 / 상세 운영·환경 계획은 미확정"}
);
const components=["detail-summary","detail-model-figure","detail-plot-figure","detail-plots-table","detail-methods","detail-conclusion",...Array.from({length:13},(_,i)=>"detail-plot-"+(i+1)),"detail-landscape"];
const source={label:"2026.10.12 제공 조감도·획지표 및 v13 프로그램",files:[{label:"최종 마스터플랜 조감도"},{"label":"획지계획도 및 획지계획표"},{"label":"NEXUS 1918 스페이스 프로그램 v13 · 2026.10.11"},{"label":"사용자 기관 수요 및 배치 의도 설명"}],filters:["최신 도면의 13개 건축 획지","수요·운영 값은 v13 및 사용자 추정으로 구분"],
caveats:["도면 표기를 전사한 값이며 새 Rhino 면적 측정이 아니다.","기관 일 방문 15~20명은 사용자 추정이다. 업무석·좌석·활동 자리·주차면수·일 방문 인원을 합산하지 않았다.","수장고·기획전시·기록·지원실과 일부 주차 구획의 상세 위치는 내부 배치 제안이다.","13개 획지 합계는 전체 사업경계 면적과 다르다. 정수 행 소계와 도면 합계에는 각각 1㎡ 잔차가 있다."],
evidenceFlow:[{title:"조감도와 획지표 판독",detail:"사용자 제공 PNG 두 장을 원본 해상도로 읽었다. 북측 화살표, 1~13번 획지, 시설명·면적·층수·높이·연결 구조를 대조해 전사했다."},{title:"수요와 운영 자료 대응",detail:"v13의 세대·계획 거주자·업무석·실별 활동 용량·면적·주차 공급을 해당 프로그램에 대응했다. 사용자 설명의 기관 일 방문 15~20명과 주변 맥락을 설계 전제로 구분했다."},{title:"배치 근거 작성",detail:"위치와 접근 방향, 공개 활동·전문 작업·거주·자료 관리의 관계, 주변 시설과 실제 경로를 연결하는 설계 의도를 서술했다. 효과의 실측 결과나 내부 배정의 완료로 주장하지 않았다."}]};
snapshot.buildStatus="updating";snapshot.generatedAt=new Date().toISOString();snapshot.report={...snapshot.report,asOf:"2026-10-12"};
snapshot.queries.latest_plots={rows:input.plots,source:{...source,metricDefinitions:[{label:"최신 도면 획지 규모",definition:"첨부 획지표의 정수 면적·최고 층수·높이를 전사했다. 도면 합계는 획지 138,089㎡, 건축 48,741㎡, 연면적 192,447㎡다. 전체 사업경계·법정 산정·실제 주차면수와 구분한다.",componentIds:components}]}};
snapshot.queries.placement_detail={rows:details,source:{...source,metricDefinitions:[{label:"배치 근거",definition:"관측된 도면 위치, 사용자 설계 전제, v13 계획 수요를 구분한 설계 해석이다. 방문 증가·소음 감소 등의 실측 효과를 확정하지 않는다.",componentIds:components}]}};
snapshot.queries.detail_narratives={rows:[{id:"overview",body:input.overview},{id:"methods",body:input.methods},{id:"conclusion",body:input.conclusion}],source};
fs.writeFileSync(snapPath,JSON.stringify(snapshot,null,2));
fs.writeFileSync(path.join(root,"report-content.json"),JSON.stringify({title:"NEXUS 1918 최종 마스터플랜 프로그램별 배치 근거 보고서",date:"2026년 10월 12일 제공 도면 기준",overview:input.overview,methods:input.methods,conclusion:input.conclusion,plots:input.plots,details},null,2));
const assets=path.join(app,"src/content/assets");fs.mkdirSync(assets,{recursive:true});
fs.copyFileSync("C:/Users/OFFICE/AppData/Local/Temp/codex-clipboard-5f1e38ad-c205-43b7-a32e-ece350650d6b.png",path.join(assets,"placement-model-20261012.png"));
fs.copyFileSync("C:/Users/OFFICE/AppData/Local/Temp/codex-clipboard-3ed6dd24-beec-4c89-a6f7-93c6dcdafd0f.png",path.join(assets,"placement-plots-20261012.png"));
const jsx=`import React from "react";
import { DataComponent, DataTable, ReportSection, RichNarrative, useDataApp } from "../../data-app-public.jsx";
import modelImage from "../assets/placement-model-20261012.png";
import plotImage from "../assets/placement-plots-20261012.png";
const columns=[{field:"plot",label:"획지"},{field:"name",label:"프로그램"},{field:"area",label:"획지면적 ㎡"},{field:"footprint",label:"건축면적 ㎡"},{field:"gfa",label:"연면적 ㎡"},{field:"floors",label:"최고 층수"}];
export function DetailedPlacementContent(){
 const {snapshot,visible}=useDataApp();const plots=snapshot.queries.latest_plots.rows,details=snapshot.queries.placement_detail.rows;
 const narrative=id=>snapshot.queries.detail_narratives.rows.find(r=>r.id===id).body;
 return <section className="detailed-placement-report" aria-label="최신 도면 기준 프로그램별 상세 배치 보고서">
 <RichNarrative id="detail:title" value="## 최종 도면 기준 프로그램별 상세 배치 근거\n\n2026년 10월 12일 제공 조감도와 획지계획표를 기준으로 정리한 보고서" label="상세 보고서 제목 편집"/>
 {visible("detail-summary")&&<ReportSection id="detail-summary" title="배치 계획의 핵심 판단" queryId="placement_detail" queryIds={["latest_plots","placement_detail"]} sourceRowsByQuery={{latest_plots:plots,placement_detail:details}} showHeading={false}><RichNarrative id="detail-summary:body" value={narrative("overview")}/></ReportSection>}
 {visible("detail-model-figure")&&<DataComponent id="detail-model-figure" title="최종 조감도의 권역과 프로그램 관계" queryId="latest_plots" kind="custom" displayRows={plots} sourceRows={plots}><img className="detail-source-image" src={modelImage} alt="공공청사와 주거, 중앙 공예와 창작, 남측 역사문화와 관문을 설명하는 사용자 제공 최종 조감도"/><RichNarrative id="detail-model-figure:caption" value="사용자 제공 조감도. 권역의 상대 위치와 연결 구조를 읽는 기준이며 그림의 면적·층수는 도면 표기다."/></DataComponent>}
 {visible("detail-plot-figure")&&<DataComponent id="detail-plot-figure" title="13개 획지의 위치와 최신 규모" queryId="latest_plots" kind="custom" displayRows={plots} sourceRows={plots}><img className="detail-source-image" src={plotImage} alt="북측 화살표와 1번부터 13번까지의 획지 배치 및 획지면적 건축면적 연면적 층수를 표시한 사용자 제공 획지계획표"/></DataComponent>}
 {visible("detail-plots-table")&&<DataComponent id="detail-plots-table" title="최신 도면의 획지별 표기값" queryId="latest_plots" kind="table" displayRows={plots} sourceRows={plots}><DataTable rows={plots} columns={columns} searchable={false} compactNumbers={false} caption="첨부 획지계획표 전사"/><RichNarrative id="detail-plots-table:caption" value="도면 합계는 획지 138,089㎡·건축 48,741㎡·연면적 192,447㎡다. 정수 행을 합산한 값과 각각 1㎡ 차이가 있어 도면 합계를 유지하고 산정 잔차로 기록했다."/></DataComponent>}
 {plots.map(plot=>{const rows=details.filter(r=>r.plot===plot.plot);const id="detail-plot-"+plot.plot;return visible(id)&&<ReportSection key={id} id={id} title={plot.plot+"번 획지 "+plot.name} queryId="placement_detail" queryIds={["latest_plots","placement_detail"]} sourceRowsByQuery={{latest_plots:[plot],placement_detail:rows}} showHeading={false} className="detail-chapter">
 <RichNarrative id={id+":intro"} value={"## "+plot.plot+"번 획지 "+plot.name+"\n\n도면 표기: 획지 "+plot.area.toLocaleString("ko-KR")+"㎡ · 건축 "+plot.footprint.toLocaleString("ko-KR")+"㎡ · 연면적 "+plot.gfa.toLocaleString("ko-KR")+"㎡ · 최고 "+plot.floors+"층 · 높이 "+plot.height+"m\n\n권역의 성격: "+plot.character}/>
 <div className="detail-programs">{rows.map(row=><RichNarrative key={row.id} id={"detail-program:"+row.id} value={row.body} label={row.program+" 설명 편집"/>)}</div></ReportSection>;})}
 {visible("detail-landscape")&&<ReportSection id="detail-landscape" title="공원과 보행축" queryId="placement_detail" sourceRows={details.filter(r=>r.plot===0)} showHeading={false}><RichNarrative id="detail-landscape:heading" value="## 공원과 보행축의 배치 관계"/><div className="detail-programs">{details.filter(r=>r.plot===0).map(r=><RichNarrative key={r.id} id={"detail-program:"+r.id} value={r.body}/>)}</div></ReportSection>}
 {visible("detail-conclusion")&&<ReportSection id="detail-conclusion" title="배치 근거를 평면으로 이어가는 방법" queryId="placement_detail" sourceRows={details} showHeading={false}><RichNarrative id="detail-conclusion:body" value={narrative("conclusion")}/></ReportSection>}
 {visible("detail-methods")&&<ReportSection id="detail-methods" title="자료의 기준과 해석" queryId="latest_plots" queryIds={["latest_plots","placement_detail"]} sourceRowsByQuery={{latest_plots:plots,placement_detail:details}} showHeading={false}><RichNarrative id="detail-methods:body" value={narrative("methods")}/></ReportSection>}
 <RichNarrative id="detail:archive-transition" value="## 이전 자료의 배치 설명과 면적 검토 기록\n\n아래 내용은 2026년 10월 11일의 선택 모델과 v13를 대조한 이전 검토다. 최신 제출 도면의 192,447㎡와 같은 시점·산정 범위의 측정 결과로 해석하지 않는다."/>
 </section>;
}
`;
fs.writeFileSync(path.join(app,"src/content/report/DetailedPlacementContent.jsx"),jsx);
const entry=path.join(app,"src/content/report/ReportContent.jsx");let text=fs.readFileSync(entry,"utf8");
if(!text.includes('from "./DetailedPlacementContent.jsx"'))text=text.replace('import { PlacementContent } from "./PlacementContent.jsx";','import { PlacementContent } from "./PlacementContent.jsx";\nimport { DetailedPlacementContent } from "./DetailedPlacementContent.jsx";');
if(!text.includes("<DetailedPlacementContent/>"))text=text.replace("  <PlacementContent/>","  <DetailedPlacementContent/>\n  <PlacementContent/>");
fs.writeFileSync(entry,text);
const css=path.join(app,"src/content/report/report.css");let styles=fs.readFileSync(css,"utf8");
if(!styles.includes(".detailed-placement-report"))styles+="\n.detailed-placement-report { display: grid; gap: 36px; min-width: 0; }\n.detail-chapter, .detail-programs { display: grid; gap: 24px; min-width: 0; }\n.detail-source-image { display: block; width: 100%; height: auto; border-radius: 8px; }\n";
fs.writeFileSync(css,styles);
console.log(JSON.stringify({plots:input.plots.length,programs:details.length,id:snapshot.id,status:snapshot.buildStatus}));

