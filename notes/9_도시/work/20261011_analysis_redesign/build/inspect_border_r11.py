import zipfile
from lxml import etree as E
p=r'C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build/revision11_full_candidate.pptx'
with zipfile.ZipFile(p) as z:
 x=E.fromstring(z.read('ppt/slides/slide5504.xml'))
 ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
 print(E.tostring(x.find('.//a:tc',ns),pretty_print=True,encoding='unicode'))
