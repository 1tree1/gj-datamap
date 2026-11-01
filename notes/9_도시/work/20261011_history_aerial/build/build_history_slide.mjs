import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {FileBlob,PresentationFile} from 'file:///C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';

const ROOT='C:/Users/OFFICE/Desktop/9_도시';
const WORK=ROOT+'/work/20261011_history_aerial', B=WORK+'/build';
const SOURCE=ROOT+'/work/20261011_visual_front/output/NEXUS_1918_05-31_visual_evidence_final.pptx';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const RT='C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=RT+'/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
const pres=await PresentationFile.importPptx(await FileBlob.load(SOURCE));
pres.slides.keep([1]);
const inspect=await pres.inspect({kind:'slide,textbox,image,shape',maxChars:22000});
const records=inspect.ndjson.split('\n').filter(Boolean).map(v=>JSON.parse(v));
const s=pres.slides.items[0];
const FONT='Pretendard';
const C={ink:'#25282A',sub:'#62696D',red:'#A16B59',line:'#C9CED0'};
function edit(name, text, pos){
 const rec=records.find(r=>r.name===name); if(!rec)throw new Error('Missing '+name);
 const obj=pres.resolve(rec.id); obj.text=text;
 obj.text.style={...rec.style,typeface:FONT,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};
 if(pos)obj.position={...rec.position,...pos};
 return obj;
}
function shape(g,name,x,y,w,h,fill='none',stroke='none',lw=0){return s.shapes.add({geometry:g,name,position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:lw}});}
function text(t,name,x,y,w,h,size=22,bold=false,color=C.sub,fill='none'){
 const a=shape('textbox',name,x,y,w,h,fill);a.text=t;
 a.text.style={fontSize:size,typeface:FONT,color,bold,verticalAlignment:'top',alignment:'left',wrap:'square',autoFit:'none',insets:0};return a;
}

edit('element-28','철도 연혁과 경주역 주변 시가지의 변화');
edit('element-30','사진: 국토지리정보원(1954·2009·2025), 옛사진 위치 근사 보정 · 연혁: 국가철도공단·김신재(2013)');
const images=records.filter(r=>r.kind==='image').sort((a,b)=>a.position.left-b.position.left);
if(images.length!==3)throw new Error('Expected exactly three aerial photographs');
const years=[1954,2009,2025];
const captions=['초기 시가지','철도 운영','폐역 이후'];
const observations=['서측 시가지와 동측 농경지','철도 양측의 시가지 확장','운행 종료 후 철도 부지 잔존'];
for(let i=0;i<3;i++){
 const x=54+i*420, im=pres.resolve(images[i].id);
 im.replace({blob:new Uint8Array(await fs.readFile(B+`/aerial_${years[i]}_square.jpg`)),contentType:'image/jpeg',alt:`국토지리정보원 ${years[i]}년 경주역과 주변 시가지 항공영상, 같은 주변 범위 비교`,fit:'contain'});
 im.frame={left:x,top:420,width:396,height:396};im.crop={left:0,top:0,right:0,bottom:0};
 edit('element-'+(47+i*2),String(years[i]),{top:835});
 edit('element-'+(48+i*2),captions[i],{top:840});
 text(observations[i],'comparison-observation-'+years[i],x,888,396,36,22,false,C.sub);
 // An editable location annotation identifies the station area in each photograph.
 const px=x+396*.415,py=420+396*.527;
 shape('ellipse','station-area-'+years[i],px-16,py-16,32,32,'none',C.red,2.5);
 shape('line','station-leader-'+years[i],x+100,py,px-16-(x+100),.1,'none',C.red,1.6);
 text('경주역','station-label-'+years[i],x+21,py-15,80,30,22,true,C.red,'#FFFFFF/94');
}
const provenance=JSON.parse(await fs.readFile(B+'/aerial_provenance.json','utf8'));
s.speakerNotes.text=[
 '철도 연혁: 1918.12.28 사정동 개업, 1936.12.01 성동동 현 위치 이전, 1939.06 노선 변경(김신재, 2013, pp.387–388), 2010.11.01 신경주역 KTX 개통, 2021.12.28 구 경주역 폐역.',
 '항공영상 출처: 국토지리정보원 국토정보맵 https://map.ngii.go.kr/ms/map/NlipMap.do . 2026-10-11 구 경주역 현 위치인 경주문화관1918(성동동 40, 원화로 266) POI 검색 후 항공사진 조회. 1945–1953년 0건, 1945–1954년 10건, 전체 조회의 최초 제공 연도는 1954년이었다. 전국적으로 1954년 이전 자료가 없다는 뜻은 아니다. 기존에 다운로드한 국토지리정보원 원본을 사용했다.',
 '1954년: 항공사진 195402001900010114. 원본 필름 가장자리의 촬영일 표기는 10 FEB 54(1954-02-10). 2009년: 항공사진 200903001200330066. 원본 촬영일 표기는 2009.3.15. 2025년: 정사영상 2025_35901069. 상품 연도는 2025년이며 2026년 사진으로 표시하지 않았다.',
 '비교 범위: 구 경주역을 포함한 약 1.2 km × 1.2 km의 주변 범위. 2025년 정사영상 좌표창을 기준으로 2009년 항공사진을 기존 위치맞춤 행렬로 보정, 1954년 항공사진은 원화로·화랑로·태종로와 서측 가로 교차부의 위치를 기준으로 근사 보정. 과거의 비정사 항공사진과 시가지 변화로 인해 국소 위치·축척 오차가 남으며 필지 경계나 면적의 정밀 측정에는 사용할 수 없다. 각 이미지 원본 내용은 추가·삭제하지 않았으며 회전·위치맞춤·크롭만 적용했다.',
 '사진 아래 문구는 시각 판독: 1954년 철도 서측의 시가지와 동측 농경지, 2009년 철도 양측의 시가지, 2025년 운행 종료 이후에도 남은 철도 부지. 철도가 시가지 변화나 동서 격차의 유일한 원인이라고 단정하지 않는다.',
 '원본 파일 및 위치맞춤 기록: '+JSON.stringify(provenance),
 '근거 대조: '+ROOT+'/work/20261010_direction_brief/20261010_final_direction_evidence_v1.md'
].join('\n\n');

await fs.mkdir(WORK+'/output',{recursive:true});
await fs.writeFile(B+'/after.png',new Uint8Array(await(await pres.export({slide:s,format:'png',scale:1})).arrayBuffer()));
await fs.writeFile(B+'/after.layout.json',await(await s.export({format:'layout'})).text());
await fs.writeFile(B+'/after.inspect.jsonl',(await pres.inspect({kind:'slide,textbox,image,shape,notes',maxChars:26000})).ndjson);
const candidate=B+'/history_candidate.pptx';
await(await PresentationFile.exportPptx(pres)).save(candidate);
console.log('Candidate ready:',candidate);
if(process.argv.includes('--finalize')){
 const final=WORK+'/output/NEXUS_1918_06_railway_history_1954_2009_2025.pptx';
 const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:final,explicitTotalSlideCount:1,requiredNativeChartOwnerSlides:[],requiredNativeTableOwnerSlides:[],fontPolicy:{basis:'user_request',families:[FONT]},pythonExecutable:RT+'/python/python.exe',integrityValidatorPath:SK+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SK+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12801600,9601200','--validate-bullet-geometry','--validate-heading-fit'],verifyArtifactToolImport:true,receiptPath:B+'/history_validation_'+Date.now()+'.json'});
 console.log(JSON.stringify(result));
 const verify=await PresentationFile.importPptx(await FileBlob.load(final));
 await fs.writeFile(B+'/final.png',new Uint8Array(await(await verify.export({slide:verify.slides.items[0],format:'png',scale:1})).arrayBuffer()));
 console.log('FINAL_RENDERED');
}
