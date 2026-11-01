from pathlib import Path
import json
B=Path(__file__).parent
exec((B/'merge_revision5.py').read_text(encoding='utf8').split("new=read(B/")[0])
files=read(B.parent/'output/구경주역_중간마감_v5_분석과네앵커.pptx')
p=xml(files['ppt/presentation.xml']);rels={r.get('Id'):r for r in xml(files['ppt/_rels/presentation.xml.rels'])}
pages={i:target('ppt/presentation.xml',rels[e.get('{'+NS['r']+'}id')].get('Target')) for i,e in enumerate(p.findall('p:sldIdLst/p:sldId',NS),1)}
outdata=[]
for n in [18,19,20,21]:
 part=pages[n];x=xml(files[part]);cr={r.get('Id'):r for r in xml(files[rp(part)])};charts=[]
 for c in x.findall('.//c:chart',NS):
  cp=target(part,cr[c.get('{'+NS['r']+'}id')].get('Target'));cx=xml(files[cp]);cs=[]
  for s in cx.findall('.//c:ser',NS):cs.append({'values':s.xpath('./c:val//c:pt/c:v/text()',namespaces=NS),'cats':s.xpath('./c:cat//c:pt/c:v/text()',namespaces=NS),'fill':s.xpath('./c:spPr//a:srgbClr/@val',namespaces=NS),'dPts':s.xpath('./c:dPt/c:idx/@val',namespaces=NS),'labelxml':E.tostring(s.find('c:dLbls',NS)).decode() if s.find('c:dLbls',NS) is not None else None})
  charts.append({'part':cp,'series':cs})
 outdata.append({'page':n,'part':part,'texts':x.xpath('.//a:t/text()',namespaces=NS),'charts':charts})
(B/'revision6_source_inspect.json').write_text(json.dumps(outdata,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(outdata,ensure_ascii=False,indent=2))
