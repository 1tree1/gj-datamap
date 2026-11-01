from pathlib import Path
import zipfile,posixpath,json
from lxml import etree as E
B=Path(__file__).parent;R=B.parent
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
with zipfile.ZipFile(R/'output/구경주역_중간마감_v4_전략다이어그램.pptx') as z:
 rel={r.get('Id'):posixpath.normpath('ppt/'+r.get('Target')) for r in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
 ids=E.fromstring(z.read('ppt/presentation.xml')).find('p:sldIdLst',NS)
 data=[]
 for i,e in enumerate(ids,1):
  part=rel[e.get('{'+NS['r']+'}id')];x=E.fromstring(z.read(part));ss=[]
  for sp in x.findall('.//p:sp',NS):
   txt=''.join(sp.xpath('.//a:t/text()',namespaces=NS));off=sp.find('.//a:xfrm/a:off',NS)
   if txt:ss.append({'text':txt,'xy':dict(off.attrib) if off is not None else {}})
  data.append({'page':i,'part':part,'text':ss})
 (B/'v4_text_audit.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 for d in data:
  if d['page']==2 or d['page']>=39:print(str(d['page'])+' '+d['part']+'\n'+' / '.join(t['text'] for t in d['text']))
with zipfile.ZipFile(B/'revision5_slides.pptx') as z:
 print('NEW CHART XML LABELS')
 for n in z.namelist():
  if n.startswith('ppt/charts/chart') and n.endswith('.xml'):
   x=E.fromstring(z.read(n));print(n,'series=',len(x.findall('.//c:ser',NS)))
   for l in x.findall('.//c:dLbls',NS):print(E.tostring(l).decode()[:2200])
