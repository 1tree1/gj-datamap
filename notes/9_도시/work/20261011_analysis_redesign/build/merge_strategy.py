from pathlib import Path
from lxml import etree as E
import zipfile,copy,json,posixpath,hashlib
B=Path(__file__).parent;R=B.parent
src=R/'output/구경주역_중간마감_v3_현황분석.pptx'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL='http://schemas.openxmlformats.org/package/2006/relationships'
def read(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
def out(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
files=read(src);new=read(B/'strategy_overlay.pptx');part='ppt/slides/slide31.xml';rp='ppt/slides/_rels/slide31.xml.rels'
x=E.fromstring(files[part]);tree=x.find('p:cSld/p:spTree',NS);rels=E.fromstring(files[rp]);rmap={r.get('Id'):r for r in rels}
pics=tree.findall('p:pic',NS);removed=[]
for pic in pics:
 rid=pic.find('.//a:blip',NS).get('{'+NS['r']+'}embed');target=rmap[rid].get('Target')
 if 'image35.png' in target:
  removed.append(dict(rid=rid,target=target));tree.remove(pic);rels.remove(rmap[rid])
assert len(removed)==1,removed
overlay=E.fromstring(new['ppt/slides/slide1.xml']);nr=E.fromstring(new['ppt/slides/_rels/slide1.xml.rels']);idmap={}
for r in nr:
 if not r.get('Type').endswith('/image'):continue
 old=r.get('Id');rid='rIdStrategyV4'+str(len(idmap)+1);idmap[old]=rid
 source=posixpath.normpath(posixpath.join('ppt/slides',r.get('Target'))).lstrip('/');dest='ppt/media/strategy_v4_'+posixpath.basename(source)
 assert dest not in files;files[dest]=new[source]
 E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=r.get('Type'),Target='../media/'+posixpath.basename(dest))
existing={int(n.get('id')) for n in x.findall('.//p:cNvPr',NS)};nextid=max(existing)+1;inserted=[]
for n in list(overlay.find('p:cSld/p:spTree',NS))[2:]:
 n=copy.deepcopy(n)
 for el in n.findall('.//p:cNvPr',NS):el.set('id',str(nextid));nextid+=1
 for el in n.iter():
  for a,v in list(el.attrib.items()):
   if a.startswith('{'+NS['r']+'}') and v in idmap:el.set(a,idmap[v])
 # Preserve the user's requested font for Latin and East Asian runs.
 for pr in n.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=NS):
  for ft in ['latin','ea','cs']:
   f=pr.find('a:'+ft,NS)
   if f is None:f=E.SubElement(pr,'{'+NS['a']+'}'+ft)
   f.set('typeface','Pretendard')
 tree.append(n);inserted.append(E.QName(n).localname)
# The diagram's spread colour is reflected in its existing native section label.
for sp in tree.findall('p:sp',NS):
 text=''.join(sp.xpath('.//a:t/text()',namespaces=NS))
 if text=='SPREAD' and sp.find('.//a:off',NS) is not None and int(sp.find('.//a:off',NS).get('x'))>6000000:
  for c in sp.findall('.//a:srgbClr',NS):c.set('val','B66A2B')
files[part]=out(x);files[rp]=out(rels)
dest=B/'strategy_candidate.pptx'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in files.items():z.writestr(n,b)
original=read(src);changed=[n for n in original if files.get(n)!=original[n]]
assert changed==[n for n in changed if n in [part,rp]],changed
receipt=dict(source=str(src),sourceSha256=hashlib.sha256(src.read_bytes()).hexdigest(),changedOriginalParts=changed,insertedShapes=len(inserted),nativeDiagram=True,slideCount=60)
(B/'strategy_change_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(receipt,ensure_ascii=True))
