from pathlib import Path
from lxml import etree as E
import zipfile
p=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/output/구경주역_중간마감_v10_건물높이지도.pptx')
with zipfile.ZipFile(p) as z:
 for f in ['ppt/slides/slide2.xml','ppt/slides/slide63.xml']:
  x=E.fromstring(z.read(f));print(f);print(x.xpath('//a:t/text()',namespaces={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}))
