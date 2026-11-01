from pathlib import Path
from lxml import etree as E
import zipfile,copy,json,posixpath,re,hashlib
B=Path(__file__).parent;R=B.parent;SRC=R/'output/구경주역_중간마감_v10_건물높이지도.pptx'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types'
def parse(b):return E.fromstring(b)
def out(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def read(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist() if not n.endswith('/')}
def save(f,p):
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in f.items():z.writestr(n,b)
def rp(p):return posixpath.join(posixpath.dirname(p),'_rels',posixpath.basename(p)+'.rels') if p else '_rels/.rels'
def rs(p):return posixpath.join(posixpath.dirname(posixpath.dirname(p)),posixpath.basename(p)[:-5]) if p!='_rels/.rels' else ''
def target(p,t):return posixpath.normpath(posixpath.join(posixpath.dirname(p),t)).lstrip('/') if not t.startswith('/') else t[1:]
def cleanup(f):
 seen=set();todo=['']
 while todo:
  p=todo.pop()
  if p in seen:continue
  seen.add(p);rel=rp(p)
  if rel not in f:continue
  seen.add(rel)
  for r in parse(f[rel]):
   if r.get('TargetMode')=='External':continue
   t=target(p,r.get('Target'));assert t in f,(p,t)
   if t not in seen:todo.append(t)
 f={n:b for n,b in f.items() if n in seen or n=='[Content_Types].xml'}
 ct=parse(f['[Content_Types].xml'])
 for c in list(ct):
  if E.QName(c).localname=='Override' and c.get('PartName').lstrip('/') not in f:ct.remove(c)
 f['[Content_Types].xml']=out(ct);return f
new=read(B/'revision11_section.pptx')
for n,b in list(new.items()):
 if not n.startswith('ppt/') or not n.endswith('.xml'):continue
 x=parse(b)
 for ft in ['latin','ea','cs']:
  for f in x.findall('.//a:'+ft,NS):f.set('typeface','Pretendard')
 for pr in x.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=NS):
  for ft in ['latin','ea','cs']:
   f=pr.find('a:'+ft,NS)
   if f is None:f=E.SubElement(pr,'{'+NS['a']+'}'+ft)
   f.set('typeface','Pretendard')
 # Explicit table no-border formatting; thin horizontal rules are native shapes.
 for tc in x.findall('.//a:tcPr',NS):
  for tag in reversed(['lnL','lnR','lnT','lnB','lnTlToBr','lnBlToTr']):
   for a in tc.findall('a:'+tag,NS):tc.remove(a)
   a=E.Element('{'+NS['a']+'}'+tag,w='0');E.SubElement(a,'{'+NS['a']+'}noFill');tc.insert(0,a)
 for sp in x.findall('.//a:tblPr',NS):
  for z in list(sp):
   if E.QName(z).localname=='tableStyleId':sp.remove(z)
 if n in ['ppt/slides/slide6.xml','ppt/slides/slide10.xml','ppt/slides/slide11.xml','ppt/slides/slide12.xml']:
  col=3 if n.endswith('slide12.xml') else 1
  tb=x.find('.//a:tbl',NS)
  if tb is not None:
   tc=tb.find('a:tr',NS).findall('a:tc',NS)[col]
   for pp in tc.findall('.//a:pPr',NS):pp.set('algn','l')
 if n=='ppt/slides/slide12.xml':
  tb=x.find('.//a:tbl',NS)
  for ri in [3,4,5]:
   cells=tb.findall('a:tr',NS)[ri].findall('a:tc',NS)
   cells[0].find('.//a:t',NS).text+=' (㎡)'
   for ci in [1,2]:
    for tx in cells[ci].findall('.//a:t',NS):tx.text=tx.text.replace('㎡','')
 if n=='ppt/slides/slide11.xml':
  for tx in x.findall('.//a:t',NS):
   if tx.text=='모빌리티 8,502 + 가로상가 6,303':tx.text='모빌리티 허브 + 생활·관문 가로상가'
 if n.endswith('/chart2.xml'):
  c='http://schemas.openxmlformats.org/drawingml/2006/chart'
  ser=x.find('.//{'+c+'}barChart/{'+c+'}ser')
  if ser is not None:
   labels=ser.find('{'+c+'}dLbls')
   if labels is None:
    template=x.find('.//{'+c+'}barChart/{'+c+'}dLbls')
    assert template is not None
    labels=copy.deepcopy(template)
    # Keep the chart's explicit numeric-only label settings on this series.
    # dLbls precedes cat/val in CT_BarSer.
    cat=ser.find('{'+c+'}cat')
    ser.insert(list(ser).index(cat),labels)
   d=E.Element('{'+c+'}dLbl');E.SubElement(d,'{'+c+'}idx',val='5');E.SubElement(d,'{'+c+'}delete',val='1');labels.insert(0,d)
 new[n]=out(x)
save(new,B/'revision11_section_clean.pptx')
files=read(SRC);mapping={}
for n in new:
 if not n.startswith('ppt/') or n in ['ppt/presentation.xml','ppt/_rels/presentation.xml.rels'] or n.endswith('.rels'):continue
 d,b=posixpath.split(n);m=re.fullmatch(r'(.+?)(\d+)(\.[^.]+)',b)
 mapping[n]=posixpath.join(d,m[1]+str(int(m[2])+5500)+m[3] if m else 'revision11_'+b)
for n in new:
 if n.endswith('.rels') and rs(n) in mapping:mapping[n]=rp(mapping[rs(n)])
for src,dst in mapping.items():
 b=new[src]
 if src.endswith('.rels'):
  x=parse(b)
  for r in x:
   if r.get('TargetMode')=='External':continue
   tgt=target(rs(src),r.get('Target'))
   if tgt in mapping:r.set('Target',posixpath.relpath(mapping[tgt],posixpath.dirname(mapping[rs(src)])))
   if r.get('Type').endswith('/notesMaster'):r.set('Target','../notesMasters/notesMaster1.xml')
  b=out(x)
 assert dst not in files,dst
 files[dst]=b
p=parse(files['ppt/presentation.xml']);rels=parse(files['ppt/_rels/presentation.xml.rels']);lst=p.find('p:sldIdLst',NS);oldids=list(lst);oldrel={r.get('Id'):r for r in rels};used=set(oldrel)
def addrel(t,ty):
 i=1
 while 'rIdRevision11_'+str(i) in used:i+=1
 rid='rIdRevision11_'+str(i);used.add(rid);E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=ty,Target=posixpath.relpath(t,'ppt'));return rid
for a in list(lst):lst.remove(a)
nextid=max(int(e.get('id')) for e in oldids)+1;order=[]
for oldpage,e in enumerate(oldids,1):
 rid=e.get('{'+NS['r']+'}id');part=target('ppt/presentation.xml',oldrel[rid].get('Target'))
 if 48<=oldpage<=58:
  rels.remove(oldrel[rid])
  if oldpage==48:
   for k in range(1,14):
    newpart=mapping[f'ppt/slides/slide{k}.xml'];rr=addrel(newpart,NS['r']+'/slide');E.SubElement(lst,'{'+NS['p']+'}sldId',id=str(nextid),attrib={'{'+NS['r']+'}id':rr});nextid+=1
    order.append({'old':None,'new':len(order)+1,'part':newpart,'action':'new section5'})
 else:
  lst.append(e);order.append({'old':oldpage,'new':len(order)+1,'part':part,'action':'retain'})
assert len(order)==62
npr=parse(new['ppt/presentation.xml']);nrels={r.get('Id'):r for r in parse(new['ppt/_rels/presentation.xml.rels'])};masters=p.find('p:sldMasterIdLst',NS)
for i,m in enumerate(npr.findall('p:sldMasterIdLst/p:sldMasterId',NS)):
 r=nrels[m.get('{'+NS['r']+'}id')];part=mapping[target('ppt/presentation.xml',r.get('Target'))];rid=addrel(part,r.get('Type'));E.SubElement(masters,'{'+NS['p']+'}sldMasterId',id=str(2147580000+i),attrib={'{'+NS['r']+'}id':rid})
 x=parse(files[part])
 for j,l in enumerate(x.findall('p:sldLayoutIdLst/p:sldLayoutId',NS)):l.set('id',str(2147590000+i*100+j))
 files[part]=out(x)
files['ppt/presentation.xml']=out(p);files['ppt/_rels/presentation.xml.rels']=out(rels)
# Keep prior slide art and content; update only navigation and chapter-specific source entry.
changed=[]
for rec in order:
 if rec['action']!='retain':continue
 x=parse(files[rec['part']]);dirty=False
 if rec['old']>=59:
  for sp in x.findall('.//p:sp',NS):
   ts=sp.findall('.//a:t',NS);off=sp.find('.//a:xfrm/a:off',NS)
   if off is not None and int(off.get('y'))>630*9525 and int(off.get('x'))>1100*9525 and ''.join(t.text or '' for t in ts)==str(rec['old']):ts[0].text=str(rec['new']);dirty=True
 if rec['old']==2:
  changes={'24':'25','30':'31','37':'38','47':'48','58':'61','계획 인구 · 방문·근로·정주 산정 · 산정 방법 · 토지이용 · 건축 규모 · 산정표 · 규제 검토 · 확인 사항 · 운영':'인구 가정 · 방문·근로·정주 산정 · 프로그램 면적 · 주차 · 토지이용 · 모델 비교 · 개발규모표'}
  for t in x.findall('.//a:t',NS):
   if t.text in changes:t.text=changes[t.text];dirty=True
 if rec['old']==60:
  for t in x.findall('.//a:t',NS):
   if t.text=='라이노 계획 경계·획지 면적 / 포획률·일자리·세대·면적 산정(calc/part2_model_final.py) / 지도(gj-datamap GeoJSON)':t.text='NEXUS 1918 v13 / 라이노 모델링과 프로그램 면적 비교(2026.10.11) / 계획 경계·획지 재집계 / 지도(gj-datamap GeoJSON)';dirty=True
   if t.text=='면적표, 산정표, 지도·다이어그램':t.text='인구 가정·프로그램 면적·모델 비교·개발규모표';dirty=True
 if dirty:files[rec['part']]=out(x);changed.append(rec['new'])
ct=parse(files['[Content_Types].xml']);nc=parse(new['[Content_Types].xml']);exts={e.get('Extension') for e in ct if E.QName(e).localname=='Default'}
for e in nc:
 if E.QName(e).localname=='Default' and e.get('Extension') not in exts:ct.append(copy.deepcopy(e));exts.add(e.get('Extension'))
 if E.QName(e).localname=='Override' and e.get('PartName').lstrip('/') in mapping:
  q=copy.deepcopy(e);q.set('PartName','/'+mapping[e.get('PartName').lstrip('/')]);ct.append(q)
files['[Content_Types].xml']=out(ct)
x=parse(files['docProps/app.xml']);x.find('{'+E.QName(x).namespace+'}Slides').text='62';files['docProps/app.xml']=out(x)
files=cleanup(files);save(files,B/'revision11_full_candidate.pptx')
receipt={'source':str(SRC),'sourceSha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'replacedOriginalPages':list(range(48,59)),'newSectionPages':list(range(48,61)),'additionalChangedPages':changed,'order':order,'total':62}
(B/'revision11_merge_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf8')
print('Merged 13-page section; total62. Updated TOC and source references; remaining slide content retained.')



