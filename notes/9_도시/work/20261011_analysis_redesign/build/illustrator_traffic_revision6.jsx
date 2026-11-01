
app.userInteractionLevel=UserInteractionLevel.DONTDISPLAYALERTS;
var f=new File("C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build/traffic_revision6_geometry.json");f.open('r');var maps=eval('('+f.read()+')');f.close();
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
 var ai=new IllustratorSaveOptions();ai.pdfCompatible=true;d.saveAs(new File("C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build/assets"+'/'+a.name+'.ai'),ai);
 var opt=new ExportOptionsPNG24();opt.artBoardClipping=true;opt.transparency=false;opt.horizontalScale=150;opt.verticalScale=150;d.exportFile(new File("C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build/assets"+'/'+a.name+'.png'),ExportType.PNG24,opt);
 done.push({name:a.name,paths:d.pathItems.length});d.close(SaveOptions.DONOTSAVECHANGES);
}JSON.stringify(done);
