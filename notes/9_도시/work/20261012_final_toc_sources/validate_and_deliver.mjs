import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const ROOT='C:/Users/OFFICE/Desktop/9_도시/work/20261012_final_toc_sources';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const rec=JSON.parse(await fs.readFile(ROOT+'/build/edit_receipt.json','utf8'));
process.env.RUNTIME_NODE_MODULES='C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
try {
 await finalizePresentation({workspaceDir:ROOT,candidatePath:ROOT+'/build/sources_section.pptx',finalPath:ROOT+'/build/validated_sources.pptx',pythonExecutable:'C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:SK+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SK+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--require-native-table-slide','1','--require-native-table-slide','2'],explicitTotalSlideCount:2,requiredNativeTableOwnerSlides:[1,2],fontPolicy:{basis:'reference',families:['Pretendard'],referencePath:rec.source,referenceSha256:rec.sourceSha256},verifyArtifactToolImport:true,receiptPath:ROOT+'/source_section.validation.json'});
 console.log('New source slides passed finalization. Full deck retains the supplied charts, including pre-existing workbook/cache discrepancies.');
 process.exit(0);
} catch(e){console.error(e.message);process.exit(1);}
