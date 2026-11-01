from pathlib import Path
import zipfile,json,posixpath
from lxml import etree as E
import sys
sys.stdout.reconfigure(encoding='utf8')
R=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign')
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
with zipfile.ZipFile(R/'output/구경주역_중간마감_v10_건물높이지도.pptx') as z:
 rel={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
 root=E.fromstring(z.read('ppt/presentation.xml'))
 for i,s in enumerate(root.find('p:sldIdLst',ns),1):
  if i<48:continue
  part=posixpath.normpath('ppt/'+rel[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')])
  t=E.fromstring(z.read(part));print('\nSLIDE',i,part); print('\n'.join(t.xpath('//a:t/text()',namespaces=ns)))
q=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/nexus_v13_audit_20261011')
for f in ['rhino_measurements.json','comparison_groups.json','facility_comparison.json','placement-model-plan.json']:
 j=json.loads((q/f).read_text('utf8')); print('\nFILE',f,'KEYS',list(j) if isinstance(j,dict) else 'list');
 if f=='facility_comparison.json': print(json.dumps(j,ensure_ascii=False))
p=Path(r'C:/Users/OFFICE/.codex/attachments/360b4dcf-ed99-49a0-b845-4bfc5d313576/붙여넣은 텍스트.txt').read_text('utf8')
print('\nSOURCE START\n',p[:p.index('## 3.')])
