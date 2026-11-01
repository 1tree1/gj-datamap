from pathlib import Path
import json,zipfile,hashlib
from lxml import etree as E
from PIL import Image,ImageDraw
from pypdf import PdfReader
R=Path(r'C:\Users\OFFICE\Desktop\9_도시');B=Path(__file__).parent;O=B.parent/'output'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
source=R/'work/20261011_midterm_deck/output/구경주역_중간마감_v2.pptx'
final=O/'구경주역_중간마감_v3_현황분석.pptx'
with zipfile.ZipFile(source) as z:a={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(final) as z:b={n:z.read(n) for n in z.namelist()}
def canonical(data,n,is_source=False):
 root=E.fromstring(data)
 if is_source:
  for t in root.findall('.//a:t',NS):t.text=(t.text or '').replace('붉은','푸른').replace('빨간','푸른').replace('빨강','파랑').replace('적색','청색')
 for tag in ['latin','ea','cs']:
  for e in root.findall('.//a:'+tag,NS):e.getparent().remove(e)
 for e in root.findall('.//a:srgbClr',NS):e.set('val','COLOR')
 # Only approved TOC references and final footer values are changed.
 if is_source:
  if n in [2,6]:
   for t in root.findall('.//a:t',NS):
    if t.text=='대상지 · 위치 · 보행 단절 · 유동 격차 · 남북 관계 · 방문 · 주변 지역 · 인구 · 청년 · 야간·업종 · 규제·유산 · 조직 · 성과 지표 · 상위계획 · 문제 종합':t.text='대상지 · 도시조직 · 동서 단절 · 활력 격차 · 남북 이용 · 인구 · 청년 · 지역 쇠퇴 · 관광 · 주민 생활 · 공공행정 · 사이트 조건 · 상위계획'
    if n==2 and t.text in ['29','35','42','51','62']:t.text=str(int(t.text)-3).zfill(2)
  if n>=29:
   for sp in root.findall('.//p:sp',NS):
    ts=sp.findall('.//a:t',NS);off=sp.find('.//a:xfrm/a:off',NS)
    if ''.join(t.text or '' for t in ts)==str(n).zfill(2) and off is not None and int(off.get('x'))>11000000 and int(off.get('y'))>6000000:ts[0].text=str(n-3).zfill(2)
 return E.tostring(root,method='c14n')
preserved=[]
for n in list(range(1,11))+list(range(29,64)):
 part=f'ppt/slides/slide{n}.xml';assert canonical(a[part],n,True)==canonical(b[part],n),(n,'Unexpected source change')
 preserved.append(n)
assert a['ppt/embeddings/Microsoft_Excel_Sheet3.xlsx']==b['ppt/embeddings/Microsoft_Excel_Sheet3.xlsx']
for start in [1,11,21,31,41,51]:
 canvas=Image.new('RGB',(1600,1925),'#ECEFF1');d=ImageDraw.Draw(canvas)
 for i,n in enumerate(range(start,start+10)):
  im=Image.open(B/'powerpoint_render'/f'{n:02}.png').convert('RGB');im.thumbnail((800,450))
  x=(i%2)*800;y=(i//2)*385
  im=im.resize((640,360))
  canvas.paste(im,(x+80,y));d.text((x+10,y+364),str(n),fill='#20272E')
 canvas.save(B/f'review_{start:02}.jpg',quality=92)
pdf=PdfReader(O/'구경주역_중간마감_v3_현황분석.pdf');assert len(pdf.pages)==60
fonts=set()
for page in pdf.pages:
 for font in page.get('/Resources',{}).get('/Font',{}).values():
  ff=font.get_object();fonts.add(str(ff.get('/BaseFont','')))
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'retained_original_slides_verified':preserved,'allowed_changes':['font','red accents to blue','TOC and footer numbering'],'source_workbook_preserved_byte_for_byte':True,'pdf_pages':60,'pdf_fonts':sorted(fonts),'final_sha256':hashlib.sha256(final.read_bytes()).hexdigest()}
(B/'qa_evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
