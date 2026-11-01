# -*- coding: utf-8 -*-
"""AdobeMCP 브리지(server_local.run_jsx_compatible)로 포토샵에 레이어 PSD를 만든다: 맥락 / 사이트 / 전략 3종 / 합성 다이어그램.
실행: C:\\Users\\OFFICE\\AdobeMCP\\venv\\Scripts\\python.exe -X utf8 ps_handoff.py"""
import sys, os, json
sys.path.insert(0, r'C:\Users\OFFICE\AdobeMCP')
import server_local as S
HERE = os.path.dirname(os.path.abspath(__file__)); CAP = os.path.join(HERE, 'rhino_cap'); A = os.path.join(HERE, 'assets')
OUT = os.path.abspath(os.path.join(HERE, '..', 'output', '다이어그램_레이어.psd'))
layers = [('axon_context', os.path.join(CAP, 'axon_context.png')), ('axon_site', os.path.join(CAP, 'axon_site.png')), ('axon_connect', os.path.join(CAP, 'axon_connect.png')),
          ('axon_exchange', os.path.join(CAP, 'axon_exchange.png')), ('axon_spread', os.path.join(CAP, 'axon_spread.png')), ('top_context', os.path.join(CAP, 'top_context.png')), ('top_site', os.path.join(CAP, 'top.png')),
          ('diag_axon_program', os.path.join(A, 'diag_axon_program.png'))]
def js(p): return json.dumps(p.replace('\\', '/'))
code = """
app.displayDialogs = DialogModes.NO;
var doc = app.documents.add(2910, 1628, 72, "구경주역 다이어그램 레이어", NewDocumentMode.RGB, DocumentFill.WHITE);
var names = [%s]; var files = [%s];
for (var i = 0; i < files.length; i++) {
  var src = app.open(new File(files[i]));
  src.selection.selectAll(); src.selection.copy(); src.close(SaveOptions.DONOTSAVECHANGES);
  app.activeDocument = doc; var L = doc.paste(); L.name = names[i];
  if (L.bounds[2].as('px') - L.bounds[0].as('px') > 2910) { var s = 2910 / (L.bounds[2].as('px') - L.bounds[0].as('px')) * 100; L.resize(s, s, AnchorPosition.MIDDLECENTER); }
  L.translate(-(L.bounds[0].as('px') + L.bounds[2].as('px')) / 2 + 1455, -(L.bounds[1].as('px') + L.bounds[3].as('px')) / 2 + 814);
  if (names[i] != 'axon_context' && names[i] != 'axon_site') L.visible = false;
}
doc.saveAs(new File(%s), new PhotoshopSaveOptions(), true);
JSON.stringify({layers: doc.layers.length, path: doc.fullName.fsName});
""" % (','.join(json.dumps(n) for n, _ in layers), ','.join(js(p) for _, p in layers), js(OUT))
r = S.run_jsx_compatible('photoshop', code, timeout=300)
print(json.dumps(r, ensure_ascii=False)[:600])
