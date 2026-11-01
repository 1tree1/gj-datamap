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
 await p.waitForFunction(()=>window.__map.loaded(),{timeout:30000}); await p.evaluate(ids=>{ for(const id of ids)if(id.startsWith('pop_')&&window.__map.getLayer(id+'-lb'))window.__map.setLayoutProperty(id+'-lb','text-size',16); for(const id of ['parks_upis-lb'])if(window.__map.getLayer(id))window.__map.setLayoutProperty(id,'visibility','none'); },ids);
 await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await p.locator('#map').screenshot({path:R+'/assets/'+name+'.png'});
 const state=await p.evaluate(()=>({bounds:window.__map.getBounds().toArray(),zoom:window.__map.getZoom(),center:window.__map.getCenter().toArray()}));
 meta.push({name,ids,hour,...state,definitions:ids.map(id=>cfg.layers.find(x=>x.id===id)).filter(Boolean)});
 console.log('captured',name);
}

await capture('population_full',['pop_chg'],[[128.97072650100026,35.64035592352834],[129.52020800855104,36.0796971958991]],[1300,1200]);
await capture('youth_focus',['pop_y2034'],[[129.161,35.810],[129.281,35.930]],[1300,1200]);
await capture('aging_focus',['pop_65'],[[129.168,35.814],[129.269,35.925]],[1300,1200]);
await capture('northsouth_clean',['rail_abandoned','zone','parks_upis'],[[129.195,35.823],[129.231,35.888]],[1000,1100]);
await fs.writeFile(R+'/capture_refined_manifest.json',JSON.stringify(meta,null,2));await b.close();