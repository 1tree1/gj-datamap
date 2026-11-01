import fs from "node:fs";
import path from "node:path";
const root="C:/Users/OFFICE/Desktop/9_도시/work/nexus_placement_report_20261012";
const app="C:/Users/OFFICE/Desktop/9_도시/work/nexus_v13_audit_20261011/visual-report";
const input=JSON.parse(fs.readFileSync(path.join(root,"authoring-input.json"),"utf8"));
const f=path.join(app,"src/data.json"),s=JSON.parse(fs.readFileSync(f,"utf8"));
for(const r of s.queries.placement_detail.rows){
 if(!input.extras[r.id])continue;
 const proposed=new Set(["resident-parking","storage","temporary-gallery","archive","craft-operations","experience-outdoor"]);
 const loc=(proposed.has(r.id)?"상세 배치 제안: ":"배치 위치: ")+r.location;
 r.body="### "+r.program+"\n\n"+loc+"\n\n"+input.extras[r.id]+"\n\n수요와 규모의 계획 근거: "+r.scale+".\n\n이용 동선은 "+r.flow+"으로 조직한다.";
}
s.buildStatus="complete";
fs.writeFileSync(f,JSON.stringify(s,null,2));
const report=JSON.parse(fs.readFileSync(path.join(root,"report-content.json"),"utf8"));report.details=s.queries.placement_detail.rows;
fs.writeFileSync(path.join(root,"report-content.json"),JSON.stringify(report,null,2));
console.log(JSON.stringify({programs:report.details.length,bodyChars:report.details.reduce((a,r)=>a+r.body.length,0),status:s.buildStatus}));

