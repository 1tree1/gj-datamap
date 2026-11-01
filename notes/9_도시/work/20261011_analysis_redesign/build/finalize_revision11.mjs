import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const R='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign',B=R+'/build';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const req=JSON.parse(await fs.readFile(B+'/revision11_requirements.json','utf8'));
process.env.RUNTIME_NODE_MODULES='C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
const r=await finalizePresentation({workspaceDir:R,candidatePath:B+'/revision11_full_candidate.pptx',finalPath:R+'/output/구경주역_중간마감_v11_계획인구와규모.pptx',pythonExecutable:'C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:SK+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SK+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12191695,6858000','--validate-bullet-geometry','--validate-heading-fit',...req.tableSlides.flatMap(n=>['--require-native-table-slide',String(n)])],explicitTotalSlideCount:62,requiredNativeTableOwnerSlides:req.tableSlides,requiredNativeChartOwnerSlides:[11,13,14,15,16,17,18,19,20,21,...req.chartSlides],nativeChartTargetApplication:'portable',tableArithmeticContracts:req.contracts,fontPolicy:{basis:'user_request',families:['Pretendard']},verifyArtifactToolImport:true,materializeLiteralChartWorkbooks:true,receiptPath:B+'/revision11_final_v2.validation.json'});
console.log(JSON.stringify({passed:true,final:r.finalPath||r.outputPath}));
