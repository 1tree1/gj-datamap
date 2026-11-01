import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const ROOT='C:/Users/OFFICE/Desktop/9_도시/work/20261012_final_toc_sources';
const SK='C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const sourceReceipt=JSON.parse(await fs.readFile(ROOT+'/build/edit_receipt.json','utf8'));
process.env.RUNTIME_NODE_MODULES='C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(SK+'/container_tools/artifact_tool_utils.mjs').href);
const r=await finalizePresentation({
 workspaceDir:ROOT,candidatePath:ROOT+'/build/candidate.pptx',finalPath:ROOT+'/output/261012_중간마감pt_건축디자인6_b분반_이승규,김민승_목차출처수정.pptx',
 pythonExecutable:'C:/Users/OFFICE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:SK+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:SK+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','62','--require-native-table-slide','63'],
 explicitTotalSlideCount:64,requiredNativeTableOwnerSlides:[62,63],
 fontPolicy:{basis:'reference',families:['Pretendard'],referencePath:sourceReceipt.source,referenceSha256:sourceReceipt.sourceSha256},
 verifyArtifactToolImport:true,
 receiptPath:ROOT+'/build/final.validation.json'
});
console.log(JSON.stringify({passed:true,final:r.finalPath||r.outputPath}));
