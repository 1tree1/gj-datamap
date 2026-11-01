import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
const R='C:/Users/OFFICE/Desktop/9_도시/work/20261011_visual_front/build';
const cfg=JSON.parse(await fs.readFile('C:/Users/OFFICE/Desktop/9_도시/gj-datamap/src/layers.json','utf8'));
const b=await chromium.launch({channel:'msedge',headless:true,args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:2});
await p.goto('https://1tree1.github.io/gj-datamap/index.html',{waitUntil:'domcontentloaded',timeout:60000});
await p.waitForFunction(()=>window.__map?.getLayer('gateways'),{timeout:90000});
console.log('loaded layers',await p.locator('.layer').count());
await p.addStyleTag({content:'body{display:block!important;} #sidebar{display:none!important} #map{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;} .maplibregl-ctrl-top-right{display:none!important}'});
await p.evaluate(()=>{window.__map.resize();});
const visible=await p.locator('.layer > label input:checked').count();console.log('initial selected',visible);
const meta=[];
async function capture(name,ids,bounds,size=[1600,1000],hour=null,filterIds=null){
 await p.setViewportSize({width:size[0],height:size[1]});
 await p.locator('.layer > label input:checked').evaluateAll(es=>es.forEach(el=>{el.checked=false;el.dispatchEvent(new Event('change',{bubbles:true}));}));
 for(const id of ids)await p.locator(`.layer[data-id="${id}"] > label input`).evaluate(el=>{el.checked=true;el.dispatchEvent(new Event('change',{bubbles:true}));});
 if(hour!==null){await p.locator('input[name="hs-kind"][value="we"]').evaluate(el=>{el.checked=true;el.dispatchEvent(new Event('change',{bubbles:true}));});await p.locator('#hs-hour').evaluate((el,v)=>{el.value=String(v);el.dispatchEvent(new Event('input',{bubbles:true}));},hour);}
 await p.evaluate(filterIds=>{for(const id of ['footfall_areas','footfall_areas-ol','footfall_areas-lb'])if(window.__map.getLayer(id))window.__map.setFilter(id,filterIds?['in',['get','id'],['literal',filterIds]]:null);},filterIds);
 await p.evaluate(({bounds})=>{const m=window.__map;m.resize();m.fitBounds(bounds,{padding:35,duration:0});}, {bounds});
 await p.waitForFunction(()=>window.__map.loaded(),{timeout:30000});await p.evaluate(ids=>{for(const id of [...ids,'parks_upis'])if(window.__map.getLayer(id+'-lb'))window.__map.setLayoutProperty(id+'-lb','visibility','none');},ids);
 await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await p.locator('#map').screenshot({path:R+'/assets/'+name+'.png'});
 const state=await p.evaluate(()=>({bounds:window.__map.getBounds().toArray(),zoom:window.__map.getZoom(),center:window.__map.getCenter().toArray()}));
 meta.push({name,ids,hour,...state,definitions:ids.map(id=>cfg.layers.find(x=>x.id===id)).filter(Boolean)});
 console.log('captured',name);
}

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
await fs.writeFile(R+'/map_label_positions.json',JSON.stringify(labels,null,2));await fs.writeFile(R+'/capture_labelled_manifest.json',JSON.stringify(meta,null,2));await b.close();