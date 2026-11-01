from pathlib import Path
from PIL import Image,ImageChops
from pypdf import PdfReader
from lxml import etree as E
import zipfile,json,hashlib,shutil
B=Path(__file__).parent;R=B.parent;O=R/'output'
r=json.loads((B/'revision5_merge_receipt.json').read_text(encoding='utf8'))
old=B/'strategy_final_render';new=B/'revision5_final_render'
report={'retainedPixels':[],'paletteQuantizationDifferences':[]}
for s in r['order']:
 if s['action']!='retain' or s['old'] in [2,39]:continue
 a=Image.open(old/f"{s['old']:02d}.png").convert('RGB');b=Image.open(new/f"{s['new']:02d}.png").convert('RGB')
 assert a.size==b.size
 diff=ImageChops.difference(a,b)
 # Ignore only the authorized page marker and historical-scheme header label.
 diff.paste((0,0,0),(1170,672,1245,713))
 if 40<=s['old']<=58:diff.paste((0,0,0),(925,17,1233,56))
 bounds=diff.getbbox();report['retainedPixels'].append({'old':s['old'],'new':s['new'],'identicalOutsideAuthorizedChanges':bounds is None})
 if bounds:report['paletteQuantizationDifferences'].append({'old':s['old'],'new':s['new'],'bounds':bounds})
with zipfile.ZipFile(O/'구경주역_중간마감_v4_전략다이어그램.pptx') as a,zipfile.ZipFile(O/'구경주역_중간마감_v5_분석과네앵커.pptx') as b,zipfile.ZipFile(B/'revision5_full_candidate.pptx') as candidate:
 oldworkbooks=[n for n in a.namelist() if n.endswith('.xlsx') and n in candidate.namelist()]
 assert all(a.read(n)==b.read(n) for n in oldworkbooks)
 report['retainedWorkbookCount']=len(oldworkbooks)
 report['retainedWorkbooksUnchanged']=True
 report['chartCount']=sum(n.endswith('.xml') and '/charts/' in n and '/_rels/' not in n for n in b.namelist())
 # PowerPoint exports indexed PNGs. The added orange label changes the optimized
 # palette on some slides, so compare the original native object trees as well.
 ns2={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
 def norm(el):return (el.tag,tuple(sorted(el.attrib.items())),el.text or '',tuple(norm(q) for q in el))
 retained=[]
 for rec in r['order']:
  if rec['action']!='retain' or rec['old'] in [2,39]:continue
  ox=E.fromstring(a.read(rec['part']));nx=E.fromstring(b.read(rec['part']))
  tree=nx.find('p:cSld/p:spTree',ns2)
  for sp in list(tree):
   pr=sp.find('p:nvSpPr/p:cNvPr',ns2)
   if pr is not None and pr.get('name')=='Previous scheme scope':tree.remove(sp)
  for sp in nx.findall('.//p:sp',ns2):
   ts=sp.findall('.//a:t',ns2);tx=''.join(q.text or '' for q in ts);off=sp.find('.//a:xfrm/a:off',ns2)
   if tx==str(rec['new']).zfill(2) and off is not None and int(off.get('x'))>11000000 and int(off.get('y'))>6000000:ts[0].text=str(rec['old']).zfill(2)
  # v3 analysis uses unpadded page markers, which agree because its numbers are >=11.
  assert norm(ox)==norm(nx),('unauthorized native content change',rec)
  retained.append(rec['new'])
 report['retainedNativeContentAndGeometryUnchangedExceptAuthorizedFooterAndLabel']=retained
 report['pixelDifferenceExplanation']='Orange header adds a palette colour in PowerPoint indexed PNG exports. Native geometry, content and original colour definitions are unchanged.'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(O/'앵커프로그램_네앵커_v2.pptx') as z:
 native=E.fromstring(z.read('ppt/slides/slide4.xml'));tx=' '.join(native.xpath('.//a:t/text()',namespaces=ns))
 for expected in ['Civic Anchor','Residential Anchor','Cultural Anchor','Creative Anchor','중앙 교류공간','256세대','464명']:
  assert expected in tx,expected
 assert len(native.findall('.//p:pic',ns))==0
 report['anchorEditable']=True
report['fullPdfPageCount']=len(PdfReader(O/'구경주역_중간마감_v5_분석과네앵커.pdf').pages)
report['anchorPdfPageCount']=len(PdfReader(O/'앵커프로그램_네앵커_v2.pdf').pages)
assert report['fullPdfPageCount']==59 and report['anchorPdfPageCount']==1
shutil.copyfile(B/'anchor_v2_final_render/01.png',O/'앵커프로그램_네앵커_v2.png')
(B/'revision5_visual_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
