import React, { useState } from "react";
import { DataComponent, DataTable, ReportSection, RichNarrative, useDataApp } from "../../data-app-public.jsx";
import { ReportDisclosure } from "../shared/ReportDisclosure.jsx";

const zones=[
 {id:"public",label:"북서측 공공업무",text:"대로에서 찾기 쉬운 공공청사와 중앙 보행축에 열린 공공기관을 연결한다. 직원의 반복 출퇴근과 방문객의 짧은 상담 방문은 주차 위치·출입 동선을 구분해 조직한다."},
 {id:"living",label:"북동측 정주·생활",text:"황오·황촌의 기존 주거 맥락에 신규 주거를 연결하고, 주거 1층 커뮤니티·건강돌봄·소공원·텃밭·생활상가를 일상 보행 경로로 묶는다."},
 {id:"connection",label:"중앙 문화·보행 연결",text:"동서축은 업무와 생활, 전시와 제작을 연결한다. 남북축은 북측 정주에서 남측 역사관광으로 이어지고, 복합문화시설은 그 사이의 공개 문화 거점으로 배치한다."},
 {id:"craft-west",label:"중앙 남측 서측 공예",text:"전시·판매·야외 감상은 공개 보행면과 중정에, 관리·반입은 서비스 면에 배치한다. 동측에서 제작한 성과를 서측에서 전시·판매하는 관계를 만든다."},
 {id:"creation-east",label:"중앙 남측 동측 창작",text:"공개 보행축에서 체험관·교류실을 만나고, 안쪽에서 제작동, 가장 동쪽에서 작가 거주동으로 이어지게 한다. 방문 활동에서 전문 작업과 체류 생활로 이용 강도가 단계적으로 바뀐다."},
 {id:"history-south",label:"남측 역사문화·관광",text:"관광 안내·주차·환승에서 기존 역사와 역사문화 전시로 이어지는 관문을 만든다. 수장·기록·기획전시·사업화는 그 거점 안에서 각각 자료·관람·지원 동선을 구분해 배정한다."},
];
const columns=[
 {field:"program",label:"프로그램",presentation:"identity",secondaryField:"status"},
 {field:"location",label:"배치 위치"},
 {field:"scale",label:"수요·규모 근거"},
];
export function PlacementContent(){
 const {snapshot,visible}=useDataApp();const rows=snapshot.queries.placement.rows;
 const [zone,setZone]=useState("전체");
 const filtered=zone==="전체"?rows:rows.filter(r=>r.zone===zone);
 return <section className="placement-content" aria-label="프로그램별 배치 근거">
 {visible("placement-summary")&&<ReportSection id="placement-summary" title="배치의 전체 논리" queryId="placement" sourceRows={rows} showHeading={false}>
  <RichNarrative id="placement-summary:body" label="배치 개요 편집" value={"## 배치의 전체 논리\n\n최종 마스터플랜의 프로그램은 서측 대로의 공공업무, 동측 기존 주거의 생활서비스, 중앙의 문화·창작 활동, 남측 역사관광 관문을 서로 연결하도록 배치한다. 이용자가 어디에서 들어와 무엇을 하고 다음 어디로 이동하는지가 위치와 출입면의 근거가 된다.\n\n- 북서측: 원화로에서 공공청사를 찾고, 청사 남쪽 기관에서 상담·창업·상권협력 활동을 연결한다.\n- 북동측: 기존 동네와 주거 1층 커뮤니티를 이어 건강·돌봄·텃밭·공원을 함께 이용한다.\n- 중앙 남측: 서측 전시·판매와 동측 체험·제작·작가 거주를 연결한다.\n- 남측: 관광 안내·주차에서 기존 역사와 역사문화 전시로 이동하고, 중앙 창작 권역으로 이어진다.\n\n공공기관의 하루 방문 15~20명은 사용자가 제공한 추정값이다. v13의 좌석·활동 자리·업무석·주차면수는 설계 계획이며, 하루 방문객이나 실측 정원으로 합산하지 않는다."}/>
 </ReportSection>}
 {visible("placement-table")&&<DataComponent id="placement-table" title="프로그램별 위치와 수요 근거" queryId="placement" kind="table" displayRows={filtered} sourceRows={filtered}>
  <DataTable rows={filtered} columns={columns} rowKey="id" caption="배치 권역별 프로그램과 근거"
   toolbarControls={<label className="nexus-table-filter">표의 권역 <select aria-label="배치표 권역" value={zone} onChange={e=>setZone(e.target.value)}>
    <option>전체</option>{zones.map(z=><option key={z.id}>{z.label}</option>)}</select></label>}/>
 </DataComponent>}
 <div className="placement-zone-list">
 {zones.map(z=>{const group=rows.filter(r=>r.zone===z.label);const id="placement-zone-"+z.id;
  return visible(id)&&<ReportSection id={id} key={id} title={z.label} queryId="placement" sourceRows={group} showHeading={false}>
   <RichNarrative id={id+":intro"} label="권역별 배치 논리 편집" value={"## "+z.label+"\n\n"+z.text}/>
   <ReportDisclosure id={id} label={group.length+"개 프로그램의 배치 근거·동선·확인사항"}>
    <div className="placement-program-list">{group.map(r=><RichNarrative id={"placement-program:"+r.id} key={r.id} label={r.program+" 배치 설명 편집"}
     value={"### "+r.program+"\n\n배치 위치: "+r.location+"\n\n"+r.reason+"\n\n- 수요·규모 근거: "+r.scale+"\n- 이용 동선: "+r.movement+"\n- 상세 계획에서 확인: "+r.check}/>)}</div>
   </ReportDisclosure>
  </ReportSection>;
 })}
 </div>
 {visible("placement-methods")&&<ReportSection id="placement-methods" title="근거의 범위와 상세 계획에서 정할 내용" queryId="placement" sourceRows={rows} showHeading={false}>
 <RichNarrative id="placement-methods:body" label="자료 해석 편집" value={"## 근거의 범위와 상세 계획에서 정할 내용\n\n배치 설명은 사용자가 제시한 최종 설계 의도, v13의 계획 수요·규모, 저장된 3dm의 시설명·획지·공원·보행축 위치를 함께 사용했다. 서측 원화로의 많은 통행량과 동측 주거지의 정적인 성격은 사용자 설명을 설계 전제로 삼았으며, 별도 교통·소음 실측값으로 주장하지 않는다.\n\n저장 파일과 앞서 선택한 매스 사이에는 일부 복합문화·공방 형상 차이가 있어, 이 추가 검토에서 정밀한 형상·거리나 새 면적을 확정하지 않았다. 아래 면적 검토는 앞서 측정한 선택 모델 기준을 유지한다. 수장고·기획전시장·기록실·지원실·옥외 주차구획처럼 내부 배정이 식별되지 않은 항목은 ‘배치 제안’ 또는 ‘미확인’으로 표시했다.\n\n설명력을 높일 다음 평면 작업은 출입구를 정하고 직원·방문자·주민·관광객·작품 반입의 실제 경로를 그리는 것이다. 특히 기관 방문 주차와 직원 주차, 주거 코어와 지역개방 커뮤니티, 체험과 전문 제작, 전시 관람과 작품 반입을 구분하면 현재 위치 선정의 근거가 동선 계획으로 이어진다."}/>
 </ReportSection>}
 <RichNarrative id="placement:area-transition" value="## 앞서 측정한 모델과 v13의 면적 비교" label="면적 검토 제목 편집"/>
 </section>;
}
