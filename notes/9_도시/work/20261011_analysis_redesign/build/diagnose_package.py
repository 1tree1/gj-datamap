from pathlib import Path
import zipfile
from lxml import etree as E
R=Path(r'C:\Users\OFFICE\Desktop\9_도시');B=R/'work/20261011_analysis_redesign/build'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
for f in [R/'work/20261011_midterm_deck/output/구경주역_중간마감_v2.pptx',B/'analysis_draft.pptx',B/'merged_candidate.pptx']:
 with zipfile.ZipFile(f) as z:
  root=E.fromstring(z.read('ppt/presentation.xml'));ids=[n.get('id') for n in root.findall('p:sldIdLst/p:sldId',ns)]
  print(f.name,'ids',ids,'unique',len(set(ids)))
  print('masters',[n.get('id') for n in root.findall('p:sldMasterIdLst/p:sldMasterId',ns)],'notes',[n for n in z.namelist() if n.startswith('ppt/notesMasters/')])
  print('otherroot',[(E.QName(n).localname,dict(n.attrib)) for n in root if E.QName(n).localname not in ['sldIdLst','sldMasterIdLst']])
