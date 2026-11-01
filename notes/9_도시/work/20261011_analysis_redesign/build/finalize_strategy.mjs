import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const R='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign',B=R+'/build';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
process.env.RUNTIME_NODE_MODULES='C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
await fs.mkdir(R+'/output',{recursive:true});
const result=await finalizePresentation({workspaceDir:R,candidatePath:B+'/strategy_candidate.pptx',finalPath:R+'/output/구경주역_중간마감_v4_전략다이어그램.pptx',pythonExecutable:'C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:SK+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SK+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12191695,6858000','--validate-bullet-geometry','--validate-heading-fit'],explicitTotalSlideCount:60,requiredNativeChartOwnerSlides:[11,15,16,17,18,19,20,21,22],requiredNativeTableOwnerSlides:[],nativeChartTargetApplication:'portable',materializeLiteralChartWorkbooks:false,fontPolicy:{basis:'user_request',families:['Pretendard']},verifyArtifactToolImport:true,receiptPath:B+'/strategy_revision_final.validation.json'});
console.log(JSON.stringify(result,null,2));







