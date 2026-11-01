"""P0 포토샵 — 라이노 단면 투시 캡처 9장 후처리(흰 배경 병합 → 크롭(지반 띠 기준) → 밝기·대비·채도 보정 → 언샤프 → 1800 px 리사이즈 → JPG)
COM(Photoshop.Application).DoJavaScript 로 실행. 사용자 열린 문서는 건드리지 않음(열고 바로 닫음)."""
import json, os, subprocess, base64
HERE = os.path.dirname(os.path.abspath(__file__))
CL = os.path.join(HERE, "..", "sheets", "clip")
crops = json.load(open(os.path.join(CL, "crops.json")))
jobs = []
import sys
ONLY = sys.argv[1:]
for key, (l, t, r, b) in crops.items():
    if ONLY and not any(key.startswith(o + '_') for o in ONLY): continue
    src = os.path.abspath(os.path.join(CL, key + ".png")).replace("\\", "/")
    dst = os.path.abspath(os.path.join(CL, key + "_ps.jpg")).replace("\\", "/")
    jobs.append((src, dst, l, t, r, b))
js = r"""
var res = [];
app.displayDialogs = DialogModes.NO;
app.preferences.rulerUnits = Units.PIXELS;
var white = new SolidColor(); white.rgb.red = 255; white.rgb.green = 255; white.rgb.blue = 255;
app.backgroundColor = white;
function vibrance(v, s) {
  var d = new ActionDescriptor(); d.putInteger(stringIDToTypeID("vibrance"), v); d.putInteger(charIDToTypeID("Strt"), s);
  executeAction(stringIDToTypeID("vibrance"), d, DialogModes.NO);
}
var J = __JOBS__;
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
""".replace("__JOBS__", json.dumps(jobs, ensure_ascii=True))
jsx = os.path.join(CL, "p0.jsx")
open(jsx, "w", encoding="utf-8-sig").write(js)
ps = "$app = New-Object -ComObject 'Photoshop.Application'; $app.DoJavaScriptFile('%s')" % jsx.replace("'", "''")
r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
print(r.stdout.strip()); print(r.stderr.strip()[:2000])
