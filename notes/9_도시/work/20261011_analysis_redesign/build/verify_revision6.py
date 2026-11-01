from pathlib import Path
from PIL import Image,ImageChops
from pypdf import PdfReader
from lxml import etree as E
import zipfile,json,hashlib,shutil
B=Path(__file__).parent;O=B.parent/'output'
r=json.loads((B/'revision6_merge_receipt.json').read_text(encoding='utf8'))
changed={13,14,18,19,20,21,38};report={'slideCount':59,'changedSlides':sorted(changed),'unchangedSlides':[],'pixelDifferences':[]}
for n in range(1,60):
 if n in changed:continue
 a=Image.open(B/f'revision5_final_render/{n:02d}.png').convert('RGB');b=Image.open(B/f'revision6_final_render/{n:02d}.png').convert('RGB')
 assert a.size==b.size
 bounds=ImageChops.difference(a,b).getbbox()
 if bounds:report['pixelDifferences'].append({'page':n,'bounds':bounds})
 else:report['unchangedSlides'].append(n)
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def norm(e):return e.tag,tuple(sorted(e.attrib.items())),e.text or '',tuple(norm(q) for q in e)
with zipfile.ZipFile(O/'구경주역_중간마감_v5_분석과네앵커.pptx') as old,zipfile.ZipFile(O/'구경주역_중간마감_v6_분석과앵커지도.pptx') as new:
 retained=[]
 for n,part in r['pages'].items():
  if int(n) in changed:continue
  assert norm(E.fromstring(old.read(part)))==norm(E.fromstring(new.read(part))),('native content changed',n)
  retained.append(int(n))
 report['nativeUnchangedSlides']=retained
 workbooks=[n for n in old.namelist() if n.endswith('.xlsx')]
 assert all(new.read(n)==old.read(n) for n in workbooks)
 report['retainedWorkbookCount']=len(workbooks);report['retainedWorkbooksUnchanged']=True
 for rec in r['accentSelection']:
  part=rec['chart'];a=E.fromstring(old.read(part));b=E.fromstring(new.read(part))
  assert a.xpath('.//c:ser/c:val//c:pt/c:v/text()',namespaces=ns)==b.xpath('.//c:ser/c:val//c:pt/c:v/text()',namespaces=ns)
  assert len(b.xpath('.//c:dPt/c:spPr/a:solidFill/a:srgbClr[@val="235D82"]',namespaces=ns))==1
 report['colorOnlyChartValuesUnchanged']=True;report['exactlyOneBlueDataPointPerChart']=True
 s=E.fromstring(new.read(r['pages']['38']));text=' '.join(s.xpath('.//a:t/text()',namespaces=ns))
 for expected in ['Civic Anchor','Residential Anchor','Creative Anchor','Cultural Anchor','중앙 교류공간','256세대','464명']:assert expected in text,expected
 report['nativeAnchorRegions']=len(s.findall('.//a:custGeom',ns));assert report['nativeAnchorRegions']==6
 report['nativeCharts']=sum(n.endswith('.xml') and '/charts/' in n and '/_rels/' not in n for n in new.namelist());assert report['nativeCharts']==16
source=Path(r['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==r['sourceSha256'];report['sourceUnchanged']=True
pdf=PdfReader(O/'구경주역_중간마감_v6_분석과앵커지도.pdf');report['pdfPageCount']=len(pdf.pages);assert len(pdf.pages)==59
assert len(pdf.pages[12].get_contents().get_data())>1000
assert len(pdf.pages[37].get_contents().get_data())>1000
report['pdfTextExtraction']='PowerPoint exported font glyphs as images, as in the source PDF. Verified by rendered appearance; editable text remains in PPTX.'
shutil.copyfile(B/'revision6_final_render/38.png',O/'앵커프로그램_지도_38쪽.png')
(B/'revision6_visual_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
