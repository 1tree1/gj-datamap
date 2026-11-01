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
 await p.waitForFunction(()=>window.__map.loaded(),{timeout:30000});
 await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await p.locator('#map').screenshot({path:R+'/assets/'+name+'.png'});
 const state=await p.evaluate(()=>({bounds:window.__map.getBounds().toArray(),zoom:window.__map.getZoom(),center:window.__map.getCenter().toArray()}));
 meta.push({name,ids,hour,...state,definitions:ids.map(id=>cfg.layers.find(x=>x.id===id)).filter(Boolean)});
 console.log('captured',name);
}
const core=[[129.196,35.827],[129.236,35.871]];
const station=[[129.207,35.841],[129.229,35.855]];
const city=[[128.985,35.619],[129.511,36.021]];
const northsouth=[[129.195,35.823],[129.231,35.888]];
await capture('context',['rail_abandoned','zone','parks_upis'],northsouth);
await capture('physical_gap',['rail_abandoned','zone','urban_roads'],station,[1000,1100]);
await capture('footfall',['footfall_areas'],core);
await capture('footfall_ew',['footfall_areas','zone'],[[129.207,35.838],[129.227,35.857]],[1600,1100],null,['G_seongdong_market_r200','B_haengbok_hwangchon_digitized']);
await capture('footfall_ns',['footfall_areas','zone','rail_abandoned','parks_upis'],northsouth,[1100,1200],null,['F_cityhall_r500','H_hwangridan_r300']);
await capture('ns_assets',['rail_abandoned','zone','parks_upis','facilities'],northsouth,[1100,1200]);
await capture('population_change',['pop_chg'],city);
await capture('population_core',['pop_chg'],[[129.167,35.803],[129.278,35.921]],[1000,1100]);
await capture('aging_core',['pop_65'],[[129.168,35.814],[129.269,35.925]]);
await capture('youth_city',['pop_y2034'],city);
await capture('youth_core',['pop_y2034'],[[129.161,35.810],[129.281,35.930]],[1000,1100]);
await capture('age_buildings',['parcels','zone'],station);
await capture('commerce',['stores','zone'],[[129.207,35.833],[129.229,35.855]],[1100,1100]);
await capture('facilities',['facilities','zone','parks_upis'],core);
await capture('arrival',['gateways','rail_stations','rail_active'],[[129.08,35.790],[129.29,35.925]]);
for(const hour of[6,13,21])await capture('traffic_we_'+hour,['traffic_hist'],[[129.200,35.834],[129.236,35.868]],[1000,1250],hour);
await capture('traffic_wide',['traffic_hist'],core,[1600,1000],13);
await fs.writeFile(R+'/capture_manifest.json',JSON.stringify(meta,null,2));
await fs.writeFile(R+'/web_dom_complete.txt',await p.locator('body').innerText());
await fs.mkdir(R+'/web_data',{recursive:true});
for(const f of['hadm_pop.geojson','youth.json','web_extras.json','traffic_hist_summary.json','fabric_report.json','hwango_report.json','arrival_transport.json','report_stats.json','arts_stats.json']){
 const v=await p.evaluate(async f=>await(await fetch('./data/'+f)).text(),f);
 await fs.writeFile(R+'/web_data/'+f,v);
 const local=await fs.readFile('C:/Users/OFFICE/Desktop/9_도시/gj-datamap/public/data/'+f);
 console.log('source',f,crypto.createHash('sha256').update(v).digest('hex')===crypto.createHash('sha256').update(local).digest('hex')?'matches local':'public differs');
}
await b.close();
