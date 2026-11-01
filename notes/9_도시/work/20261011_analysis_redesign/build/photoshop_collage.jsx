
app.displayDialogs=DialogModes.NO;var priorUnits=app.preferences.rulerUnits;app.preferences.rulerUnits=Units.PIXELS;var files=["C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/assets/photos/ph02_west_corner_bldg.jpg", "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/assets/photos/ph62_east_lane_paved.jpg", "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/assets/photos/ph53_hwangnidan_street.jpg"],names=['서측 상업가로','동측 저층 골목','현장 상업가로'];
var d=app.documents.add(UnitValue(2400,'px'),UnitValue(1000,'px'),72,'현장 도시조직 비교',NewDocumentMode.RGB,DocumentFill.WHITE);
for(var i=0;i<3;i++){
var s=app.open(new File(files[i]));var rate=Math.max(800/s.width.as('px'),1000/s.height.as('px'));s.resizeImage(UnitValue(s.width.as('px')*rate,'px'),UnitValue(s.height.as('px')*rate,'px'),72,ResampleMethod.BICUBIC);
var x=(s.width.as('px')-800)/2,y=(s.height.as('px')-1000)*.62;s.crop([UnitValue(x,'px'),UnitValue(y,'px'),UnitValue(x+800,'px'),UnitValue(y+1000,'px')]);
s.selection.selectAll();s.selection.copy();s.close(SaveOptions.DONOTSAVECHANGES);app.activeDocument=d;var l=d.paste();l.name=names[i];l.translate(UnitValue(i*800-l.bounds[0].as('px'),'px'),UnitValue(-l.bounds[1].as('px'),'px'));
}
d.saveAs(new File("C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build/assets/현장_도시조직_콜라주.psd"),new PhotoshopSaveOptions(),true);var o=new ExportOptionsSaveForWeb();o.format=SaveDocumentType.PNG;o.PNG8=false;d.exportDocument(new File("C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build/assets/field_collage.png"),ExportType.SAVEFORWEB,o);d.close(SaveOptions.DONOTSAVECHANGES);app.preferences.rulerUnits=priorUnits;'done';
