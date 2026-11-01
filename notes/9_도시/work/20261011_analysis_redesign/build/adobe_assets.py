import sys,json
from pathlib import Path
sys.path.insert(0,r'C:\Users\OFFICE\AdobeMCP');import server_local as S
B=Path(__file__).parent;A=B/'assets';A.mkdir(exist_ok=True)
def js(p):return json.dumps(str(p).replace('\\','/'),ensure_ascii=False)
code=r'''
app.userInteractionLevel=UserInteractionLevel.DONTDISPLAYALERTS;
var f=new File(GEO);f.open('r');var maps=eval('('+f.read()+')');f.close();
function col(s){var c=new RGBColor();c.red=parseInt(s.substr(1,2),16);c.green=parseInt(s.substr(3,2),16);c.blue=parseInt(s.substr(5,2),16);return c;}
var done=[];
for(var m=0;m<maps.length;m++){
 var a=maps[m];var d=app.documents.add(DocumentColorSpace.RGB,a.w,a.h);
 var b=a.bounds, sc=Math.min(a.w/(b[2]-b[0]),a.h/(b[3]-b[1])), ox=(a.w-sc*(b[2]-b[0]))/2,oy=(a.h-sc*(b[3]-b[1]))/2;
 var bg=d.pathItems.rectangle(a.h,0,a.w,a.h);bg.filled=true;bg.fillColor=col('#FFFFFF');bg.stroked=false;
 var ly=d.layers.add();ly.name='NGII geometry EPSG5187';
 for(var i=0;i<a.items.length;i++){
  var v=a.items[i],ps=[];for(var j=0;j<v.points.length;j++){var q=v.points[j];ps.push([ox+(q[0]-b[0])*sc,oy+(q[1]-b[1])*sc]);}
  if(ps.length<2)continue;var p=ly.pathItems.add();p.setEntirePath(ps);p.closed=v.closed;p.filled=!!v.fill;if(v.fill)p.fillColor=col(v.fill);p.stroked=!!v.line;if(v.line){p.strokeColor=col(v.line);p.strokeWidth=v.lw;}if(v.opacity)p.opacity=v.opacity;
 }
 var ai=new IllustratorSaveOptions();ai.pdfCompatible=true;d.saveAs(new File(OUT+'/'+a.name+'.ai'),ai);
 var opt=new ExportOptionsPNG24();opt.artBoardClipping=true;opt.transparency=false;opt.horizontalScale=150;opt.verticalScale=150;d.exportFile(new File(OUT+'/'+a.name+'.png'),ExportType.PNG24,opt);
 done.push({name:a.name,paths:d.pathItems.length});d.close(SaveOptions.DONOTSAVECHANGES);
}JSON.stringify(done);
'''.replace('GEO',js(B/'geometry.json')).replace('OUT',js(A))
(B/'illustrator_maps.jsx').write_text(code,encoding='utf8')
r=S.run_jsx_compatible('illustrator',code,timeout=240);print(json.dumps(r,ensure_ascii=False),flush=True)
if not r.get('success'):raise RuntimeError('Illustrator failed')
PH=B.parents[2]/'20261008_presentation_front/assets/photos'
# Explicit crops from original field photographs. Layers stay editable in PSD.
PH=Path(r'C:\Users\OFFICE\Desktop\9_도시\work\20261008_presentation_front\assets\photos')
ps=r'''
app.displayDialogs=DialogModes.NO;var priorUnits=app.preferences.rulerUnits;app.preferences.rulerUnits=Units.PIXELS;var files=FILES,names=['서측 상업가로','동측 저층 골목','현장 상업가로'];
var d=app.documents.add(UnitValue(2400,'px'),UnitValue(1000,'px'),72,'현장 도시조직 비교',NewDocumentMode.RGB,DocumentFill.WHITE);
for(var i=0;i<3;i++){
var s=app.open(new File(files[i]));var rate=Math.max(800/s.width.as('px'),1000/s.height.as('px'));s.resizeImage(UnitValue(s.width.as('px')*rate,'px'),UnitValue(s.height.as('px')*rate,'px'),72,ResampleMethod.BICUBIC);
var x=(s.width.as('px')-800)/2,y=(s.height.as('px')-1000)*.62;s.crop([UnitValue(x,'px'),UnitValue(y,'px'),UnitValue(x+800,'px'),UnitValue(y+1000,'px')]);
s.selection.selectAll();s.selection.copy();s.close(SaveOptions.DONOTSAVECHANGES);app.activeDocument=d;var l=d.paste();l.name=names[i];l.translate(UnitValue(i*800-l.bounds[0].as('px'),'px'),UnitValue(-l.bounds[1].as('px'),'px'));
}
d.saveAs(new File(PSD),new PhotoshopSaveOptions(),true);var o=new ExportOptionsSaveForWeb();o.format=SaveDocumentType.PNG;o.PNG8=false;d.exportDocument(new File(__PNG__),ExportType.SAVEFORWEB,o);d.close(SaveOptions.DONOTSAVECHANGES);app.preferences.rulerUnits=priorUnits;'done';
'''.replace('FILES',json.dumps([str(PH/p).replace('\\','/') for p in ['ph02_west_corner_bldg.jpg','ph62_east_lane_paved.jpg','ph53_hwangnidan_street.jpg']],ensure_ascii=False)).replace('PSD',js(A/'현장_도시조직_콜라주.psd')).replace('__PNG__',js(A/'field_collage.png'))
(B/'photoshop_collage.jsx').write_text(ps,encoding='utf8');r=S.run_jsx_compatible('photoshop',ps,timeout=180);print(json.dumps(r,ensure_ascii=False),flush=True)


