import fs from 'node:fs/promises';
import { PresentationFile, FileBlob } from '@oai/artifact-tool';
const root = 'C:/Users/OFFICE/Desktop/9_도시/work/20261011_visual_front';
const deck = await PresentationFile.importPptx(await FileBlob.load(root + '/output/NEXUS_1918_05-31_visual_evidence_final.pptx'));
await fs.mkdir(root + '/build/final_renders', { recursive: true });
for (const [i, slide] of deck.slides.items.entries()) {
  const n = String(i + 5).padStart(2, '0');
  await fs.writeFile(root + '/build/final_renders/' + n + '.png', new Uint8Array(await (await deck.export({ slide, format: 'png', scale: 1 })).arrayBuffer()));
  console.log('Final preview ' + n);
}
console.log('Final slide count: ' + deck.slides.items.length);
