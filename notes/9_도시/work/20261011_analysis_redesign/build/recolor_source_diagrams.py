from pathlib import Path
import json,zipfile,sys,posixpath
import xml.etree.ElementTree as E
sys.path.insert(0,r'C:\Users\OFFICE\AdobeMCP');import server_local as S
B=Path(__file__).parent.resolve();P=B/'merged_candidate.pptx';D=B/'source_palette';D.mkdir(exist_ok=True)
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
parts=set()
with zipfile.ZipFile(P) as z:
 for oldpage in [1,3,36,38,39,40,41,47,48,49]:
  root=E.fromstring(z.read(f'ppt/slides/slide{oldpage}.xml'));refs={e.get('{'+ns['r']+'}embed') for e in root.findall('.//a:blip',ns)}
  for rel in E.fromstring(z.read(f'ppt/slides/_rels/slide{oldpage}.xml.rels')):
   if rel.get('Id') in refs and rel.get('Type','').endswith('/image'):parts.add(posixpath.normpath(posixpath.join('ppt/slides',rel.get('Target'))))
 files={n:z.read(n) for n in z.namelist()}
pairs=[]
for i,n in enumerate(sorted(parts)):
 src=D/(str(i)+Path(n).suffix);out=D/('recolored_'+str(i)+Path(n).suffix);src.write_bytes(files[n]);pairs.append([str(src).replace('\\','/'),str(out).replace('\\','/'),n])
script='''app.displayDialogs=DialogModes.NO;var pairs=PAIRS,done=[];
for(var i=0;i<pairs.length;i++){
 var d=app.open(new File(pairs[i][0]));d.flatten();
 var des=new ActionDescriptor(),lst=new ActionList(),ad=new ActionDescriptor();
 ad.putEnumerated(charIDToTypeID('Chnl'),charIDToTypeID('Chnl'),charIDToTypeID('Rds '));
 ad.putInteger(charIDToTypeID('H   '),-148);ad.putInteger(charIDToTypeID('Strt'),-8);ad.putInteger(charIDToTypeID('Lght'),-5);
 lst.putObject(charIDToTypeID('Hst2'),ad);des.putList(charIDToTypeID('Adjs'),lst);des.putBoolean(charIDToTypeID('Clrz'),false);executeAction(charIDToTypeID('HStr'),des,DialogModes.NO);
 var op=new ExportOptionsSaveForWeb();if(/png$/i.test(pairs[i][1])){op.format=SaveDocumentType.PNG;op.PNG8=false;}else{op.format=SaveDocumentType.JPEG;op.quality=95;}d.exportDocument(new File(pairs[i][1]),ExportType.SAVEFORWEB,op);done.push(pairs[i][2]);d.close(SaveOptions.DONOTSAVECHANGES);
}JSON.stringify(done);'''.replace('PAIRS',json.dumps(pairs,ensure_ascii=True))
r=S.run_jsx_compatible('photoshop',script,timeout=150);print(json.dumps(r,ensure_ascii=False),flush=True)
if not r.get('success'):raise RuntimeError(r)
for src,dest,n in pairs:files[n]=Path(dest).read_bytes()
with zipfile.ZipFile(P,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in files.items():z.writestr(n,v)
(B/'source_palette_receipt.json').write_text(json.dumps({'parts':sorted(parts),'method':'Photoshop red-channel hue/saturation adjustment; geometry and labels unchanged'},indent=2),encoding='utf8')

