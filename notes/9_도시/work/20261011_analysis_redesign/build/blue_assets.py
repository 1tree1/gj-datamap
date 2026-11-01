import json,sys
from pathlib import Path
sys.path.insert(0,r'C:\Users\OFFICE\AdobeMCP')
import server_local as S
B=Path(__file__).parent; A=B/'assets'; R=B.parents[2]
palette={'#C8102E':'#235D82','#96152A':'#235D82','#FBE7E9':'#E1EBF1','#E5B9B1':'#C3D9E5','#B35348':'#235D82','#245E89':'#235D82','#AA6317':'#B66A2B','#C8DDE5':'#E7ECEF','#F3EEE8':'#F1F2F3'}
maps=json.loads((B/'geometry.json').read_text(encoding='utf8'))
for m in maps:
 for it in m['items']:
  for k in ['fill','line']:
   if it.get(k) in palette:it[k]=palette[it[k]]
(B/'geometry.json').write_text(json.dumps(maps,ensure_ascii=False,separators=(',',':')),encoding='utf8')
code=(B/'illustrator_maps.jsx').read_text(encoding='utf8')
r=S.run_jsx_compatible('illustrator',code,timeout=360)
print(json.dumps(r,ensure_ascii=False),flush=True)
if not r.get('success'):raise RuntimeError('Illustrator palette export failed')
src=R/'20261011_midterm_deck/build/assets'
src=Path(r'C:\Users\OFFICE\Desktop\9_도시\work\20261011_midterm_deck\build\assets')
pairs=[[str(src/(n+'.png')).replace('\\','/'),str(A/(n+'_mono.png')).replace('\\','/')] for n in ['age_buildings','reg_godo','heritage']]
ps="app.displayDialogs=DialogModes.NO;var pairs="+json.dumps(pairs,ensure_ascii=False)+";var done=[];for(var i=0;i<pairs.length;i++){var d=app.open(new File(pairs[i][0]));d.flatten();d.activeLayer.desaturate();var o=new ExportOptionsSaveForWeb();o.format=SaveDocumentType.PNG;o.PNG8=false;d.exportDocument(new File(pairs[i][1]),ExportType.SAVEFORWEB,o);done.push(pairs[i][1]);d.close(SaveOptions.DONOTSAVECHANGES);}JSON.stringify(done);"
r=S.run_jsx_compatible('photoshop',ps,timeout=120);print(json.dumps(r,ensure_ascii=False),flush=True)
