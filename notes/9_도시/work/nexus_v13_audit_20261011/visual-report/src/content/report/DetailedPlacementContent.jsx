import React from "react";
import { DataComponent, DataTable, ReportSection, RichNarrative, useDataApp } from "../../data-app-public.jsx";
import modelImage from "../assets/placement-model-20261012.png";
import plotImage from "../assets/placement-plots-20261012.png";
const columns=[{field:"plot",label:"획지"},{field:"name",label:"프로그램"},{field:"area",label:"획지면적 ㎡"},{field:"footprint",label:"건축면적 ㎡"},{field:"gfa",label:"연면적 ㎡"},{field:"floors",label:"최고 층수"}];
export function DetailedPlacementContent(){
 const {snapshot,visible}=useDataApp();const plots=snapshot.queries.latest_plots.rows,details=snapshot.queries.placement_detail.rows;
 const narrative=id=>snapshot.queries.detail_narratives.rows.find(r=>r.id===id).body;
 return <section className="detailed-placement-report" aria-label="최신 도면 기준 프로그램별 상세 배치 보고서">
 <RichNarrative id="detail:title" value={["## 최종 도면 기준 프로그램별 상세 배치 근거","2026년 10월 12일 제공 조감도와 획지계획표를 기준으로 정리한 보고서"].join("\n\n")} label="상세 보고서 제목 편집"/>
 {visible("detail-summary")&&<ReportSection id="detail-summary" title="배치 계획의 핵심 판단" queryId="placement_detail" queryIds={["latest_plots","placement_detail"]} sourceRowsByQuery={{latest_plots:plots,placement_detail:details}} showHeading={false}><RichNarrative id="detail-summary:body" value={narrative("overview")}/></ReportSection>}
 {visible("detail-model-figure")&&<DataComponent id="detail-model-figure" title="최종 조감도의 권역과 프로그램 관계" queryId="latest_plots" kind="custom" displayRows={plots} sourceRows={plots}><img className="detail-source-image" src={modelImage} alt="공공청사와 주거, 중앙 공예와 창작, 남측 역사문화와 관문을 설명하는 사용자 제공 최종 조감도"/><RichNarrative id="detail-model-figure:caption" value="사용자 제공 조감도. 권역의 상대 위치와 연결 구조를 읽는 기준이며 그림의 면적·층수는 도면 표기다."/></DataComponent>}
 {visible("detail-plot-figure")&&<DataComponent id="detail-plot-figure" title="13개 획지의 위치와 최신 규모" queryId="latest_plots" kind="custom" displayRows={plots} sourceRows={plots}><img className="detail-source-image" src={plotImage} alt="북측 화살표와 1번부터 13번까지의 획지 배치 및 획지면적 건축면적 연면적 층수를 표시한 사용자 제공 획지계획표"/></DataComponent>}
 {visible("detail-plots-table")&&<DataComponent id="detail-plots-table" title="최신 도면의 획지별 표기값" queryId="latest_plots" kind="table" displayRows={plots} sourceRows={plots}><DataTable rows={plots} columns={columns} searchable={false} compactNumbers={false} caption="첨부 획지계획표 전사"/><RichNarrative id="detail-plots-table:caption" value="도면 합계는 획지 138,089㎡·건축 48,741㎡·연면적 192,447㎡다. 정수 행을 합산한 값과 각각 1㎡ 차이가 있어 도면 합계를 유지하고 산정 잔차로 기록했다."/></DataComponent>}
 {plots.map(plot=>{const rows=details.filter(r=>r.plot===plot.plot);const id="detail-plot-"+plot.plot;return visible(id)&&<ReportSection key={id} id={id} title={plot.plot+"번 획지 "+plot.name} queryId="placement_detail" queryIds={["latest_plots","placement_detail"]} sourceRowsByQuery={{latest_plots:[plot],placement_detail:rows}} showHeading={false} className="detail-chapter">
 <RichNarrative id={id+":intro"} value={["## "+plot.plot+"번 획지 "+plot.name,"도면 표기: 획지 "+plot.area.toLocaleString("ko-KR")+"㎡ · 건축 "+plot.footprint.toLocaleString("ko-KR")+"㎡ · 연면적 "+plot.gfa.toLocaleString("ko-KR")+"㎡ · 최고 "+plot.floors+"층 · 높이 "+plot.height+"m","권역의 성격: "+plot.character].join("\n\n")}/>
 <div className="detail-programs">{rows.map(row=><RichNarrative key={row.id} id={"detail-program:"+row.id} value={row.body} label={row.program+" 설명 편집"}/>)}</div></ReportSection>;})}
 {visible("detail-landscape")&&<ReportSection id="detail-landscape" title="공원과 보행축" queryId="placement_detail" sourceRows={details.filter(r=>r.plot===0)} showHeading={false}><RichNarrative id="detail-landscape:heading" value="## 공원과 보행축의 배치 관계"/><div className="detail-programs">{details.filter(r=>r.plot===0).map(r=><RichNarrative key={r.id} id={"detail-program:"+r.id} value={r.body}/>)}</div></ReportSection>}
 {visible("detail-conclusion")&&<ReportSection id="detail-conclusion" title="배치 근거를 평면으로 이어가는 방법" queryId="placement_detail" sourceRows={details} showHeading={false}><RichNarrative id="detail-conclusion:body" value={narrative("conclusion")}/></ReportSection>}
 {visible("detail-methods")&&<ReportSection id="detail-methods" title="자료의 기준과 해석" queryId="latest_plots" queryIds={["latest_plots","placement_detail"]} sourceRowsByQuery={{latest_plots:plots,placement_detail:details}} showHeading={false}><RichNarrative id="detail-methods:body" value={narrative("methods")}/></ReportSection>}
 <RichNarrative id="detail:archive-transition" value={["## 이전 자료의 배치 설명과 면적 검토 기록","아래 내용은 2026년 10월 11일의 선택 모델과 v13를 대조한 이전 검토다. 최신 제출 도면의 192,447㎡와 같은 시점·산정 범위의 측정 결과로 해석하지 않는다."].join("\n\n")}/>
 </section>;
}
