from pathlib import Path
from PIL import Image,ImageChops
from pypdf import PdfReader
from lxml import etree as E
import zipfile,json,hashlib,shutil
B=Path(__file__).parent;O=B.parent/'output';receipt=json.loads((B/'revision7_merge_receipt.json').read_text(encoding='utf8'))
def read(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
old=read(O/'구경주역_중간마감_v6_분석과앵커지도.pptx');new=read(O/'구경주역_중간마감_v7_연결교차확산.pptx')
changed=[n for n in old if old[n]!=new.get(n)];assert changed==['ppt/slides/slide31.xml'],changed
assert set(old)==set(new)
same=[];different=[]
for n in range(1,60):
 a=Image.open(B/f'revision6_final_render/{n:02d}.png').convert('RGB');b=Image.open(B/f'revision7_final_render/{n:02d}.png').convert('RGB')
 (same if ImageChops.difference(a,b).getbbox() is None else different).append(n)
assert different==[26],different
v=json.loads((B/'revision7_final.validation.json').read_text(encoding='utf8'))
pdf=PdfReader(O/'구경주역_중간마감_v7_연결교차확산.pdf');assert len(pdf.pages)==59
assert hashlib.sha256(Path(receipt['source']).read_bytes()).hexdigest()==receipt['sourceSha256']
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
x=E.fromstring(new['ppt/slides/slide31.xml']);text=' '.join(x.xpath('.//a:t/text()',namespaces=ns))
assert '접속' not in text
assert len(x.findall('.//a:gradFill',ns))==10
assert len(x.xpath('.//p:cNvPr[starts-with(@name,"r7-spread")]',namespaces=ns))==2
shutil.copyfile(B/'revision7_final_render/26.png',O/'연결교차확산_26쪽.png')
result={'changedParts':changed,'changedSlides':different,'pixelIdenticalOtherSlides':len(same),'nativeGradientShapes':10,'nativeSpreadFans':2,'allChartAndWorkbookPartsUnchanged':True,'pptxSlideCount':59,'pdfPageCount':len(pdf.pages),'slide26Warnings':[w for w in v['presentationLayout']['warnings'] if w.get('slide')==26]}
(B/'revision7_visual_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False))
