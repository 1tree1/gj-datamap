from pathlib import Path
p=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build/merge_revision11.py')
s=p.read_text('utf8')
old=" new[n]=out(x)\nsave(new,B/'revision11_section_clean.pptx')"
new=""" if n in ['ppt/slides/slide6.xml','ppt/slides/slide10.xml','ppt/slides/slide11.xml','ppt/slides/slide12.xml']:
  col=3 if n.endswith('slide12.xml') else 1
  tb=x.find('.//a:tbl',NS)
  if tb is not None:
   tc=tb.find('a:tr',NS).findall('a:tc',NS)[col]
   for pp in tc.findall('.//a:pPr',NS):pp.set('algn','l')
 if n=='ppt/slides/slide11.xml':
  for tx in x.findall('.//a:t',NS):
   if tx.text=='모빌리티 8,502 + 가로상가 6,303':tx.text='모빌리티 허브 + 생활·관문 가로상가'
 if n.endswith('/chart2.xml'):
  c='http://schemas.openxmlformats.org/drawingml/2006/chart'
  ser=x.find('.//{'+c+'}barChart/{'+c+'}ser')
  if ser is not None:
   labels=ser.find('{'+c+'}dLbls')
   if labels is None:labels=E.SubElement(ser,'{'+c+'}dLbls')
   d=E.Element('{'+c+'}dLbl');E.SubElement(d,'{'+c+'}idx',val='5');E.SubElement(d,'{'+c+'}delete',val='1');labels.insert(0,d)
 new[n]=out(x)
save(new,B/'revision11_section_clean.pptx')"""
assert old in s
p.write_text(s.replace(old,new),'utf8')
