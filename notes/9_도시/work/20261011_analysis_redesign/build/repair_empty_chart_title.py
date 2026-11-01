from pathlib import Path
from lxml import etree as E
import zipfile
B=Path(__file__).parent;P=B/'merged_candidate.pptx';ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(P) as z:files={n:z.read(n) for n in z.namelist()}
for n,v in list(files.items()):
 if '/charts/chart' not in n or not n.endswith('.xml'):continue
 root=E.fromstring(v);fixed=False
 for t in root.findall('.//c:title',ns):
  if not ''.join(t.xpath('.//a:t/text()',namespaces=ns)).strip():t.getparent().remove(t);fixed=True
 if fixed:files[n]=E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True);print('Removed empty exported title:',n)
with zipfile.ZipFile(P,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in files.items():z.writestr(n,v)
