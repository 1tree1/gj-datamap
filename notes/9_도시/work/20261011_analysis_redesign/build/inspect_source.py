from pathlib import Path
import zipfile,json,xml.etree.ElementTree as E
from pypdf import PdfReader
from PIL import Image,ImageOps,ImageDraw
R=Path(r'C:\Users\OFFICE\Desktop\9_도시'); B=R/'work/20261011_analysis_redesign/build'; O=R/'work/20261011_midterm_deck/output'
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
with zipfile.ZipFile(O/'구경주역_중간마감_v2.pptx') as z:
 p=E.fromstring(z.read('ppt/presentation.xml')); print('SIZE',p.find('p:sldSz',ns).attrib)
 slides=sorted([x for x in z.namelist() if __import__('re').match(r'ppt/slides/slide\d+.xml$',x)],key=lambda s:int(__import__('re').search(r'slide(\d+)',s).group(1)))
 data=[{'page':i+1,'text':[t.text for t in E.fromstring(z.read(s)).findall('.//a:t',ns)]} for i,s in enumerate(slides)]
 (B/'source_slides.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 for d in data[:28]: print(d['page'],' | '.join(t or '' for t in d['text'])[:1700])
pdf=PdfReader(O/'구경주역_중간마감_v2.pdf');(B/'source_pdf_text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{p.extract_text()}' for i,p in enumerate(pdf.pages)),encoding='utf8')
print('TOTAL',len(pdf.pages))
assets=[]
for d in ['work/20261011_midterm_deck/build/assets','work/20261011_visual_front/build','work/20261008_presentation_front/assets/maps']:
 for f in (R/d).rglob('*'):
  if f.suffix.lower() in ['.png','.jpg','.jpeg']:
   try:
    with Image.open(f) as im: assets.append({'path':str(f),'w':im.width,'h':im.height})
   except: pass
(B/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2),encoding='utf8')
print('ASSETS',len(assets))

