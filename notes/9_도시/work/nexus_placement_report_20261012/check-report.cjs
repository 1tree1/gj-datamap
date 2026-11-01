const fs=require("fs"),path=require("path");const {chromium}=require(require.resolve("playwright",{paths:[process.argv[2]]}));
(async()=>{const b=await chromium.launch({headless:true,channel:"msedge"});const p=await b.newPage({viewport:{width:1440,height:1000}});const errors=[];p.on("pageerror",e=>errors.push(e.message));
await p.goto("http://127.0.0.1:61285/?view=1",{waitUntil:"networkidle"});await p.waitForSelector(".detailed-placement-report");
await p.screenshot({path:path.join(process.argv[3],"detail-opening-desktop.png")});
const report=p.locator(".detailed-placement-report");const names=await report.locator("h3").allTextContents();
const text=await report.innerText();
const images=await report.locator("img").evaluateAll(es=>es.map(e=>({loaded:e.complete&&e.naturalWidth>0,width:e.getBoundingClientRect().width,natural:e.naturalWidth,alt:e.alt})));
const components=await report.locator("[data-component-id]").evaluateAll(es=>es.map(e=>({id:e.dataset.componentId,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height})));
await p.getByRole("button",{name:"Next page",exact:true}).first().click();const table2=await p.locator('[data-component-id="detail-plots-table"]').innerText();
await p.getByRole("button",{name:"Previous page",exact:true}).first().click();
for(const id of ["detail-plot-1","detail-plot-2","detail-plot-3","detail-plot-4","detail-plot-5","detail-plot-6","detail-plot-7","detail-plot-8","detail-plot-9","detail-plot-10","detail-plot-11","detail-plot-12","detail-plot-13","detail-landscape","detail-methods","detail-conclusion"]){
 await p.locator('[data-component-id="'+id+'"]').screenshot({path:path.join(process.argv[3],id+"-desktop.png")});
}
await p.setViewportSize({width:390,height:844});await p.locator('[data-component-id="detail-plot-5"]').screenshot({path:path.join(process.argv[3],"detail-institutions-mobile.png")});
const mobile=await p.evaluate(()=>({width:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,detailWidth:document.querySelector(".detailed-placement-report").getBoundingClientRect().width}));
const out={errors,programs:names,images,components,table2,mobile,escaped:!!text.match(/\\n|\*\*|�/),chars:text.length};
fs.writeFileSync(path.join(process.argv[3],"detail-browser-check.json"),JSON.stringify(out,null,2));console.log(JSON.stringify({...out,programs:names.length,table2:table2.slice(-170)}));
await b.close();})().catch(e=>{console.error(e.stack);process.exit(1)});
