import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const R='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign',B=R+'/build';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
process.env.RUNTIME_NODE_MODULES='C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
const result=await finalizePresentation({workspaceDir:R,candidatePath:B+'/anchor_program_draft.pptx',finalPath:R+'/output/앵커프로그램_구성_v1.pptx',pythonExecutable:'C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:SK+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SK+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12191695,6858000','--validate-heading-fit'],explicitTotalSlideCount:1,requiredNativeChartOwnerSlides:[],requiredNativeTableOwnerSlides:[],fontPolicy:{basis:'user_request',families:['Pretendard']},verifyArtifactToolImport:true,receiptPath:B+'/anchor_program_v1.validation.json'});
console.log(JSON.stringify({finalPath:result.finalPath,sha256:result.finalSha256,findings:result.presentationLayout.findings,warnings:result.presentationLayout.warnings}));
