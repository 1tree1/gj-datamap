from pathlib import Path
from lxml import etree as E
import zipfile
B=Path(__file__).parent;P=B/'merged_candidate.pptx';ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(P) as z:files={n:z.read(n) for n in z.namelist()}
count=0
for n,v in list(files.items()):
 if not n.startswith(('ppt/slides/slide','ppt/notesSlides/notesSlide')) or not n.endswith('.xml'):continue
 root=E.fromstring(v);changed=False
 for t in root.findall('.//a:t',ns):
  if '붉은' in (t.text or ''):t.text=t.text.replace('붉은','푸른');changed=True;count+=1
 if changed:files[n]=E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
with zipfile.ZipFile(P,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in files.items():z.writestr(n,v)
print('Palette labels updated:',count)
Q=B/'qa_review.py';s=Q.read_text(encoding='utf8');s=s.replace('root=E.fromstring(data)','root=E.fromstring(data)\n if is_source:\n  for t in root.findall(\'.//a:t\',NS):t.text=(t.text or \'\').replace(\'붉은\',\'푸른\')')
Q.write_text(s,encoding='utf8')
