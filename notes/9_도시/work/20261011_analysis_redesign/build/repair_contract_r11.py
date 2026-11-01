from pathlib import Path
p=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build/merge_revision11.py')
s=p.read_text('utf8');needle=" if n=='ppt/slides/slide11.xml':"
insert=""" if n=='ppt/slides/slide12.xml':
  tb=x.find('.//a:tbl',NS)
  for ri in [3,4,5]:
   cells=tb.findall('a:tr',NS)[ri].findall('a:tc',NS)
   cells[0].find('.//a:t',NS).text+=' (㎡)'
   for ci in [1,2]:
    for tx in cells[ci].findall('.//a:t',NS):tx.text=tx.text.replace('㎡','')
"""
assert needle in s;s=s.replace(needle,insert+needle);p.write_text(s,'utf8')
