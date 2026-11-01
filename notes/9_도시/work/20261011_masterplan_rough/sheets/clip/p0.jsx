
var res = [];
app.displayDialogs = DialogModes.NO;
app.preferences.rulerUnits = Units.PIXELS;
var white = new SolidColor(); white.rgb.red = 255; white.rgb.green = 255; white.rgb.blue = 255;
app.backgroundColor = white;
function vibrance(v, s) {
  var d = new ActionDescriptor(); d.putInteger(stringIDToTypeID("vibrance"), v); d.putInteger(charIDToTypeID("Strt"), s);
  executeAction(stringIDToTypeID("vibrance"), d, DialogModes.NO);
}
var J = [["C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/Dg_1.png", "C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/Dg_1_ps.jpg", 0, 252, 1800, 938], ["C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/Dg_2.png", "C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/Dg_2_ps.jpg", 0, 151, 1800, 837], ["C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/Dg_3.png", "C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/Dg_3_ps.jpg", 0, 226, 1800, 912]];
for (var i = 0; i < J.length; i++) {
  var j = J[i];
  var d = app.open(new File(j[0]));
  var bg = d.artLayers.add(); bg.name = "white";
  d.selection.selectAll(); d.selection.fill(white); d.selection.deselect();
  bg.move(d.layers[d.layers.length - 1], ElementPlacement.PLACEAFTER);
  d.flatten();
  d.crop([UnitValue(j[2], "px"), UnitValue(j[3], "px"), UnitValue(j[4], "px"), UnitValue(j[5], "px")]);
  var L = d.activeLayer;
  L.adjustLevels(0, 246, 0.92, 0, 255);
  L.adjustBrightnessContrast(-4, 18);
  try { vibrance(22, 6); } catch (e) { res.push("vib " + e); }
  L.applyUnSharpMask(60, 1.0, 2);
  d.resizeImage(UnitValue(1800, "px"), null, 300, ResampleMethod.BICUBICSHARPER);
  var o = new JPEGSaveOptions(); o.quality = 11; o.embedColorProfile = true;
  d.saveAs(new File(j[1]), o, true, Extension.LOWERCASE);
  d.close(SaveOptions.DONOTSAVECHANGES);
  res.push(j[1]);
}
res.join("\n");
