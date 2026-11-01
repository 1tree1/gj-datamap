import zipfile,sys
from lxml import etree as E
sys.stdout.reconfigure(encoding='utf8')
with zipfile.ZipFile(r'C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build/revision11_full_candidate.pptx') as z:
 x=E.fromstring(z.read('ppt/slides/slide5510.xml'));ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
 print('shapes',len(x.findall('.//p:sp',ns)), 'table',len(x.findall('.//a:tbl',ns)))
 for q in x.findall('.//p:sp',ns):
  print(q.find('p:nvSpPr/p:cNvPr',ns).get('name'),''.join(q.xpath('.//a:t/text()',namespaces=ns))[:25])
 print(E.tostring(x.find('.//a:tcPr',ns),encoding='unicode'))
