import fs from 'node:fs/promises';
let src=await fs.readFile(new URL('./capture_maps.mjs',import.meta.url),'utf8');src=src.slice(0,src.indexOf('const core='));
src=src.replace("await p.waitForFunction(()=>window.__map.loaded(),{timeout:30000});", "await p.waitForFunction(()=>window.__map.loaded(),{timeout:30000});await p.evaluate(ids=>{for(const id of [...ids,'parks_upis'])if(window.__map.getLayer(id+'-lb'))window.__map.setLayoutProperty(id+'-lb','visibility','none');},ids);");
src+=`
const pop=JSON.parse(await fs.readFile(R+'/web_data/hadm_pop.geojson','utf8'));
const ff=JSON.parse(await fs.readFile('C:/Users/OFFICE/Desktop/9_도시/gj-datamap/public/data/footfall_areas.geojson','utf8'));
const selected=ff.features.filter(f=>['G_seongdong_market_r200','B_haengbok_hwangchon_digitized'].includes(f.properties.id));
let all=[];function scan(v){if(typeof v[0]==='number')all.push(v);else v.forEach(scan);}selected.forEach(f=>scan(f.geometry.coordinates));
const bounds=[[Math.min(...all.map(x=>x[0]))-.0005,Math.min(...all.map(x=>x[1]))-.0005],[Math.max(...all.map(x=>x[0]))+.0005,Math.max(...all.map(x=>x[1]))+.0005]];
function centroid(f){const rings=f.geometry.type==='Polygon'?[f.geometry.coordinates[0]]:f.geometry.coordinates.map(p=>p[0]);let best=null;for(const ring of rings){const o=ring[0];let sum=0,x=0,y=0;for(let i=0;i<ring.length-1;i++){const a=[ring[i][0]-o[0],ring[i][1]-o[1]],z=[ring[i+1][0]-o[0],ring[i+1][1]-o[1]],c=a[0]*z[1]-z[0]*a[1];sum+=c;x+=(a[0]+z[0])*c;y+=(a[1]+z[1])*c;}if(sum&&(!best||Math.abs(sum)>best.area))best={area:Math.abs(sum),point:[o[0]+x/(3*sum),o[1]+y/(3*sum)]};}return best.point;}
const labels={};
async function proj(name,features,key){labels[name]=await p.evaluate(xs=>xs.map(x=>{const z=window.__map.project(x.coord);return {...x,xy:[z.x,z.y]};}),features.map(f=>({name:f.properties[key],coord:centroid(f)})));}
await capture('footfall_close',['footfall_areas','zone'],bounds,[1300,1000],null,['G_seongdong_market_r200','B_haengbok_hwangchon_digitized']);await proj('footfall_close',selected,'id');
await capture('youth_nolabel',['pop_y2034'],[[129.161,35.810],[129.281,35.930]],[1300,1200]);await proj('youth_nolabel',pop.features.filter(f=>['현곡면','용강동','황성동','성건동','동천동','황오동','선도동','월성동','황남동'].includes(f.properties.hadm)),'hadm');
await capture('aging_nolabel',['pop_65'],[[129.168,35.814],[129.269,35.925]],[1300,1200]);await proj('aging_nolabel',pop.features.filter(f=>['현곡면','용강동','황성동','성건동','동천동','황오동','선도동','월성동','황남동'].includes(f.properties.hadm)),'hadm');
await capture('footfall_ns_clean',['footfall_areas','zone','rail_abandoned','parks_upis'],[[129.195,35.823],[129.231,35.888]],[1100,1200],null,['F_cityhall_r500','H_hwangridan_r300']);await proj('footfall_ns_clean',ff.features.filter(f=>['F_cityhall_r500','H_hwangridan_r300'].includes(f.properties.id)),'id');
await fs.writeFile(R+'/map_label_positions.json',JSON.stringify(labels,null,2));await fs.writeFile(R+'/capture_labelled_manifest.json',JSON.stringify(meta,null,2));await b.close();`;
await fs.writeFile(new URL('./capture_labelled_run.mjs',import.meta.url),src);await import('./capture_labelled_run.mjs');
