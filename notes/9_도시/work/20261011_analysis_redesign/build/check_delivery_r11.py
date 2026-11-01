from pathlib import Path
import json,zipfile,hashlib,sys
from PIL import Image,ImageChops
from pypdf import PdfReader
from lxml import etree as E
sys.stdout.reconfigure(encoding='utf8')
B=Path(__file__).parent;R=B.parent;O=R/'output'
receipt=json.loads((B/'revision11_merge_receipt.json').read_text('utf8'))
new=B/'revision11_final_render';old=B/'revision10_final_render'
checks=[]
for i in range(1,48):
 if i==2:continue
 im1=Image.open(old/f'{i:02}.png').convert('RGB');im2=Image.open(new/f'{i:02}.png').convert('RGB')
 checks.append({'slide':i,'pixel_equal':ImageChops.difference(im1,im2).getbbox() is None})
assert all(x['pixel_equal'] for x in checks)
assert len(list(new.glob('*.png')))==62
pdf=O/'구경주역_중간마감_v11_계획인구와규모.pdf';pr=PdfReader(pdf);assert len(pr.pages)==62
pdf_text='\n'.join(p.extract_text() for p in pr.pages[47:60])
notes_ok=[];ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(O/'구경주역_중간마감_v11_계획인구와규모.pptx') as z:
 texts='\n'.join(' '.join(E.fromstring(z.read(f'ppt/slides/slide{5500+k}.xml')).xpath('//a:t/text()',namespaces=ns)) for k in range(1,14))
 assert '600세대' not in texts
 for val in ['105,560','176,661','256','464','19,200','32,160','228,022','1,200']:
  assert val in texts,val
 for k in range(1,14):
  note=z.read(f'ppt/notesSlides/notesSlide{5500+k}.xml');txt=' '.join(E.fromstring(note).xpath('//a:t/text()',namespaces=ns));assert 'v13' in txt;notes_ok.append(47+k)
 v=z.testzip();assert v is None
report={'slide_count':62,'chapter5_pages':[48,60],'unchanged_prior_slides':checks,'source_notes_checked':notes_ok,'pdf_pages':len(pr.pages),'old600household_removed_from_chapter5':True,'key_totals_in_pptx':True,'pdf_text_extractable':bool(pdf_text.strip()),'pdf_visual_review':'PowerPoint export with glyph outlines; rendered pages reviewed separately','pptx_sha256':hashlib.sha256((O/'구경주역_중간마감_v11_계획인구와규모.pptx').read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}
(B/'revision11_delivery_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'pages':62,'chapter5':'48–60','unchanged_outside_chapter_and_toc':len(checks),'source_notes':len(notes_ok),'pdf_verified':True},ensure_ascii=False))
