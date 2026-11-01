from pathlib import Path
import zipfile
from lxml import etree as E
B=Path(__file__).parent
with zipfile.ZipFile(B/'merged_raw.pptx') as z:a={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(B/'repaired_diagnostic.pptx') as z:b={n:z.read(n) for n in z.namelist()}
for n in ['ppt/presentation.xml','ppt/_rels/presentation.xml.rels','ppt/slideMasters/slideMaster1001.xml','ppt/notesMasters/notesMaster1001.xml']:
 print('\n',n)
 if n not in b:print('removed');continue
 if 'Master1001' not in n:print(b[n].decode('utf8')[:9000])
print('Removed', sorted(set(a)-set(b)))
print('Added',sorted(set(b)-set(a)))
