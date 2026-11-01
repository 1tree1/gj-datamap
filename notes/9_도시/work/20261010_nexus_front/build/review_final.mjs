import fs from 'node:fs/promises';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const R='C:/Users/OFFICE/Desktop/9_도시/work/20261010_nexus_front';
const p=await PresentationFile.importPptx(await FileBlob.load(R+'/output/NEXUS_1918_05-19_complete.pptx'));
await fs.mkdir(R+'/build/final_renders',{recursive:true});
for(const[i,s]of p.slides.items.entries()){
  const n=String(i+5).padStart(2,'0');
  await fs.writeFile(R+'/build/final_renders/'+n+'.png',new Uint8Array(await(await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));
  console.log('final preview',n);
}

console.log('final slide count',p.slides.items.length);
