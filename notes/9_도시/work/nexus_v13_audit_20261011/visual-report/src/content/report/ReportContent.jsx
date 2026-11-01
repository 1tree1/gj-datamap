import React, { useState } from "react";
import { PlacementContent } from "./PlacementContent.jsx";
import { DetailedPlacementContent } from "./DetailedPlacementContent.jsx";
import { EvidenceChart, DataComponent, DataTable, ReportSection, RichNarrative, useDataApp } from "../../data-app-public.jsx";

const number = v => v == null ? "—" : new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 1 }).format(v);
const signed = v => v == null ? "비교 불가" : (v > 0 ? "+" : "") + number(v);
const columns = [
  {field:"facility",label:"시설 / 대응 범위",presentation:"identity",secondaryField:"note"},
  {field:"target",label:"v13 (㎡)",renderCell:(v) => v == null ? "독립 목표 없음" : number(v)},
  {field:"model",label:"모델 (㎡)",renderCell:(v) => v == null ? "실 배정 미확인" : number(v)},
  {field:"delta",label:"차이 (㎡)",deltaTone:"neutral",renderCell:signed},
];
const siteColumns = [
  {field:"name",label:"공간",presentation:"identity",secondaryField:"note"},
  {field:"target",label:"v13 / 비교 기준 (㎡)",renderCell:number},
  {field:"model",label:"모델 (㎡)",renderCell:number},
  {field:"delta",label:"차이 (㎡)",deltaTone:"neutral",renderCell:signed},
];
function Narrative({id,title,queryId,queryIds,rows,rowsByQuery,text}) {
 return <ReportSection id={id} title={title} queryId={queryId} queryIds={queryIds}
 sourceRows={rows} sourceRowsByQuery={rowsByQuery} showHeading={false}>
   <RichNarrative id={id+":body"} value={text} label="내용 편집" />
 </ReportSection>;
}
export function ReportContent() {
 const { snapshot, visible, appTitle, setAppTitle, canEdit, mode } = useDataApp();
 const all = snapshot.queries.facilities.rows;
 const totals = snapshot.queries.totals.rows;
 const site = snapshot.queries.site.rows;
 const [scope,setScope] = useState("all");
 const shown = all.filter(r => scope==="all" || scope==="over" && r.delta>0 || scope==="under" && r.delta<0 || scope==="unknown" && r.delta==null);
 const major = all.filter(r => r.delta!=null).sort((a,b)=>Math.abs(b.delta)-Math.abs(a.delta)).slice(0,9).sort((a,b)=>b.delta-a.delta);
 const totalRows = totals.slice(0,2);
 return <article className="report-content nexus-report" aria-label="NEXUS v13 모델 비교 보고서">
  <header className="report-hero">
   <RichNarrative id="report:series" className="nexus-kicker" value="NEXUS 1918 · 최종 마스터플랜 배치 근거 · 2026.10.12" label="표제 편집"/>
   <h1 data-data-app-title contentEditable={canEdit&&mode==="edit"} suppressContentEditableWarning
    onBlur={canEdit&&mode==="edit"?e=>setAppTitle(e.currentTarget.textContent.trim()||appTitle):undefined}
    onKeyDown={e=>{if(e.key==="Enter"){e.preventDefault();e.currentTarget.blur();}}}>{appTitle}</h1>
  </header>
  <DetailedPlacementContent/>
  <PlacementContent/>
  {visible("summary") && <Narrative id="summary" title="핵심 요약" queryId="totals" queryIds={["totals","facilities"]}
   rowsByQuery={{totals,facilities:all}} text={"## 핵심 요약\n\n- 선택한 건축 매스의 추정 연면적은 176.7천㎡, v13 전체 목표는 105.6천㎡다. 차이는 +71.1천㎡, +67.4%이며, 조건부 수영장·영화관을 제외한 우선 프로그램 대비로는 +71.6%다.\n- 큰 면적 차이는 남측 역사문화·지원 기능 +15.3천㎡, 공공기관·청년창업 +10.3천㎡에서 나타난다. 세부 실 구성이 같은지 확인해야 면적 조정 범위를 정할 수 있다.\n- 주거는 8동·5층 기본 매스가 일치한다. 모델에 있는 1층 연결부 때문에 합계는 +960㎡다. 북측 주차장은 목표보다 작고, 남측 공유주차장은 3층 계획에서 5층 매스로 늘었다.\n\n모델의 수치 치수와 면적 속성을 근거로 1좌표 단위=1m로 해석했다. Rhino 파일의 선언 단위는 mm이므로, 아래 값은 이 해석을 전제로 한 매스 면적 비교다."}/>}
  {visible("total-chart") && <EvidenceChart id="total-chart" queryId="totals" title="전체 건축 면적 비교 (㎡)"
   description="v13는 조건부 수영장·영화관을 포함한 목표 합계, 모델은 층별 겹침을 제거한 매스 바닥면 합계."
   rows={totalRows} sourceRows={totalRows} height={300}
   spec={{type:"horizontalBar",x:"plan",y:"area",valueDecimals:1,stackable:false,colors:["var(--chart-1)"]}} />}
  {visible("major-findings") && <Narrative id="major-findings" title="시설별 차이" queryId="facilities" rows={all}
   text={"## 면적 조정은 큰 차이를 보이는 기능부터 검토할 수 있다\n\n남측 역사문화·지원 기능과 공공기관·청년창업을 묶은 면적 차이는 25.6천㎡다. 다만 이 모델 묶음에는 v13의 세부 프로그램과 일대일로 대응하지 않는 기능이 포함되어 있다. 우선 내부 용도를 대응시킨 뒤 필요한 층수와 바닥 면적을 조정하는 것이 타당하다.\n\n모빌리티 허브 8.5천㎡와 별도 가로상가 6.3천㎡는 v13에서 독립 목표를 찾지 못했다. 기존 프로그램에 포함될 공간인지, 추가 프로그램인지 구분해야 한다."}/>}
  {visible("facility-chart") && <EvidenceChart id="facility-chart" queryId="facilities" title="절대 차이가 큰 9개 시설의 증감 (㎡)"
   description="모델−v13. 양수는 모델 면적이 크다는 뜻이며, 용도 적정성을 판정한 값은 아니다."
   rows={major} sourceRows={major} height={510}
   spec={{type:"horizontalBar",x:"facility",y:"delta",valueDecimals:1,colorBySign:false,stackable:false,colors:["var(--chart-2)"]}} />}
  {visible("facility-table") && <DataComponent id="facility-table" queryId="facilities" title="전체 시설별 면적표"
    kind="table" displayRows={shown} sourceRows={shown}>
    <DataTable rows={shown} columns={columns} compactNumbers={false} caption="시설별 v13와 모델 면적 비교" rowKey="facility"
      toolbarControls={<label className="nexus-table-filter">비교 범위 <select aria-label="비교 범위" value={scope} onChange={e=>setScope(e.target.value)}>
        <option value="all">전체</option><option value="over">모델이 큰 시설</option><option value="under">모델이 작은 시설</option><option value="unknown">대응 미확인</option>
      </select></label>}/>
   </DataComponent>}
  {visible("housing") && <Narrative id="housing" title="주거" queryId="facilities" rows={all.filter(r=>r.facility.startsWith("주거"))}
   text={"## 주거 8동의 기본 규모는 일치한다\n\n48×10m, 5층, 8동의 기본 연면적은 19.2천㎡로 v13와 같다. 모델에는 1층 연결 매스가 더해져, 겹치는 면적을 제외하면 20.2천㎡가 된다. 추가 연결부는 960㎡다.\n\n256세대·464명 수용 여부는 세대별 평면과 실 배정이 없어 확인하지 못했다. 매스 수와 층수의 일치가 세대수의 일치를 뜻하지는 않는다."}/>}
  {visible("parking") && <Narrative id="parking" title="주차장" queryId="facilities" rows={all.filter(r=>r.facility.includes("주차장"))}
   text={"## 주차장은 북측이 줄고 남측이 늘었다\n\n- 북측 주차장동: v13 22.6천㎡ → 모델 17.4천㎡. 4층은 같지만 층당 면적은 5,640㎡ → 약 4,352㎡로 줄었다.\n- 남측 공유주차장: v13 9.6천㎡ → 모델 16.0천㎡. 80×40m의 바닥판을 3층 → 5층으로 쌓은 차이다.\n\nv13 북측 주차장에는 5,640㎡와 94×80m=7,520㎡가 함께 적혀 있어 기준 자체에 불일치가 있다. 이 보고서는 연면적 목표 22,560㎡=5,640×4를 사용했다. 실제 주차 구획이 식별되지 않아 목표 주차대수 충족 여부는 판정하지 않았다."}/>}
  {visible("site-findings") && <Narrative id="site-findings" title="획지와 야외공간" queryId="site" rows={site}
   text={"## 구역경계와 창작·체험 획지는 다시 맞춰 볼 필요가 있다\n\n선택된 구역경계는 228.0천㎡, v13는 218.5천㎡로 모델 경계가 약 9.5천㎡(+4.4%) 크다. 경계선이 같은 대상을 가리키는지 먼저 확인해야 한다.\n\n8번 창작·체험 획지는 약 12.0천㎡다. v13 체험관의 실내 3,000㎡+야외 12,000㎡를 모두 이 획지 안에 넣는다면 최소 소요면적보다 약 3.0천㎡ 작다. 레지던시·교류·마켓까지 포함하면 배치 검토가 더 필요하다. 실내 체험관의 연면적 증가가 야외 요구면적을 충족한 것으로 볼 수는 없다.\n\n공동체텃밭과 생활 소공원은 1,600㎡ 기준보다 각각 약 51㎡, 56㎡ 크다. 대규모 공원과 주요 보행축은 v13에 확정 면적이 없어 증감 판정에서 제외했다."}/>}
  {visible("site-table") && <DataComponent id="site-table" queryId="site" title="구역·획지·지면 면적 비교" kind="table" displayRows={site} sourceRows={site}>
    <DataTable rows={site} columns={siteColumns} searchable={false} compactNumbers={false} caption="구역 및 야외 공간 면적 비교"/>
  </DataComponent>}
  {visible("methods") && <Narrative id="methods" title="비교 범위와 측정 방법" queryId="totals" queryIds={["totals","facilities","site"]}
    rowsByQuery={{totals,facilities:all,site}} text={"## 비교 범위와 측정 방법\n\n현재 선택 객체 3,947개 중 건축물 레이어의 닫힌 매스 157개를 측정했다. 각 매스의 수평 바닥면을 추출하고, 같은 높이 구간에서 겹치는 면적을 한 번만 합산했다. 중정의 빈 부분은 제외했다. 기능별 합계는 전체 합집합과 일치했고, 체적÷높이 검산의 최대 오차는 0.000042㎡였다.\n\n기존 역사 상세 Mesh, 유리 지붕, 식재, 야외 지면 및 용도 불명 연결 요소는 건축 합계에서 제외했다. 따라서 역사 기존 건물의 실제 면적까지 포함한 전체 사업 연면적을 확정한 결과는 아니다. 객체의 면적·층수 속성 중 일부가 이전 계획값이어서 현재 형상 측정을 우선했다.\n\n법정 연면적, 상세 실별 배정, 세대수와 주차대수는 이 매스 모델만으로 확정하지 않았다. 도시농업·자원순환 지원실 200㎡는 전용 실 또는 독립 매스로 식별되지 않았으며, 누락 200㎡로 단정하지 않는다.\n\n각 차트·표·본문의 메뉴에서 측정 범위, 원자료, 계산 방법을 확인할 수 있다. 기준 자료는 사용자가 제공한 NEXUS v13(2026.10.11)과 그 시점의 Rhino 선택 모델이다."}/>}
 </article>;
}
