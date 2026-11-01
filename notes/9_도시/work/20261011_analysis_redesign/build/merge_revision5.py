from pathlib import Path
from lxml import etree as E
import zipfile,copy,json,posixpath,re,hashlib
B=Path(__file__).parent;R=B.parent
SRC=R/'output/구경주역_중간마감_v4_전략다이어그램.pptx'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
REL='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types'
def xml(b):return E.fromstring(b)
def out(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def read(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist() if not n.endswith('/')}
def save(files,p):
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in files.items():z.writestr(n,b)
def rp(p):return posixpath.join(posixpath.dirname(p),'_rels',posixpath.basename(p)+'.rels') if p else '_rels/.rels'
def rs(p):return posixpath.join(posixpath.dirname(posixpath.dirname(p)),posixpath.basename(p)[:-5]) if p!='_rels/.rels' else ''
def target(p,t):return posixpath.normpath(posixpath.join(posixpath.dirname(p),t)).lstrip('/') if not t.startswith('/') else t[1:]
def cleanup(files):
 seen=set();todo=['']
 while todo:
  p=todo.pop()
  if p in seen:continue
  seen.add(p);rel=rp(p)
  if rel not in files:continue
  seen.add(rel)
  for r in xml(files[rel]):
   if r.get('TargetMode')=='External':continue
   t=target(p,r.get('Target'));assert t in files,(p,t)
   if t not in seen:todo.append(t)
 files={n:b for n,b in files.items() if n in seen or n=='[Content_Types].xml'}
 ct=xml(files['[Content_Types].xml'])
 for c in list(ct):
  if E.QName(c).localname=='Override' and c.get('PartName').lstrip('/') not in files:ct.remove(c)
 files['[Content_Types].xml']=out(ct)
 return files
def setcount(files,n):
 if 'docProps/app.xml' in files:
  x=xml(files['docProps/app.xml']);q=x.find('{'+E.QName(x).namespace+'}Slides')
  if q is not None:q.text=str(n)
  files['docProps/app.xml']=out(x)
def fontfix(files):
 for n,b in list(files.items()):
  if not n.startswith('ppt/') or not n.endswith('.xml'):continue
  x=xml(b)
  for ft in ['latin','ea','cs']:
   for f in x.findall('.//a:'+ft,NS):f.set('typeface','Pretendard')
  for pr in x.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=NS):
   for ft in ['latin','ea','cs']:
    f=pr.find('a:'+ft,NS)
    if f is None:f=E.SubElement(pr,'{'+NS['a']+'}'+ft)
    f.set('typeface','Pretendard')
  files[n]=out(x)
new=read(B/'revision5_slides.pptx');fontfix(new)
# White percentage labels on the blue series, retaining dark labels on light grey.
part='ppt/slides/charts/chart2.xml';x=xml(new[part]);ser=x.find('.//c:barChart/c:ser',NS);labels=ser.find('c:dLbls',NS)
if labels is None:
 labels=copy.deepcopy(x.find('.//c:barChart/c:dLbls',NS));ser.append(labels)
for c in labels.findall('.//a:srgbClr',NS):c.set('val','FFFFFF')
new[part]=out(x)
# Keep a one-slide, fully editable copy of the latest anchor definition.
single=dict(new);p=xml(single['ppt/presentation.xml']);lst=p.find('p:sldIdLst',NS);ids=list(lst);rels=xml(single['ppt/_rels/presentation.xml.rels'])
keep=ids[3].get('{'+NS['r']+'}id')
for a in list(lst):
 if a.get('{'+NS['r']+'}id')!=keep:lst.remove(a)
for r in list(rels):
 if r.get('Type').endswith('/slide') and r.get('Id')!=keep:rels.remove(r)
x=xml(single['ppt/slides/slide4.xml']);tree=x.find('p:cSld/p:spTree',NS)
for sp in list(tree):
 tx=''.join(sp.xpath('.//a:t/text()',namespaces=NS))
 if tx=='38':tree.remove(sp)
single['ppt/slides/slide4.xml']=out(x);single['ppt/presentation.xml']=out(p);single['ppt/_rels/presentation.xml.rels']=out(rels);setcount(single,1)
single=cleanup(single);save(single,B/'anchor_v2_candidate.pptx')
# Import only the new slides and their dependency tree into the existing deck.
files=read(SRC);mapping={}
for n in new:
 if not n.startswith('ppt/') or n in ['ppt/presentation.xml','ppt/_rels/presentation.xml.rels'] or n.endswith('.rels'):continue
 d,b=posixpath.split(n);m=re.fullmatch(r'(.+?)(\d+)(\.[^.]+)',b)
 mapping[n]=posixpath.join(d,m[1]+str(int(m[2])+2000)+m[3] if m else 'revision5_'+b)
for n in new:
 if n.endswith('.rels') and rs(n) in mapping:mapping[n]=rp(mapping[rs(n)])
for source,dest in mapping.items():
 b=new[source]
 if source.endswith('.rels'):
  x=xml(b)
  for r in x:
   if r.get('TargetMode')=='External':continue
   t=target(rs(source),r.get('Target'))
   if t in mapping:r.set('Target',posixpath.relpath(mapping[t],posixpath.dirname(mapping[rs(source)])))
   if r.get('Type').endswith('/notesMaster'):r.set('Target','../notesMasters/notesMaster1.xml')
  b=out(x)
 assert dest not in files,dest
 files[dest]=b
p=xml(files['ppt/presentation.xml']);rels=xml(files['ppt/_rels/presentation.xml.rels']);lst=p.find('p:sldIdLst',NS);oldids=list(lst);oldrel={r.get('Id'):r for r in rels}
assert len(oldids)==60
used={r.get('Id') for r in rels}
def addrel(t,ty):
 i=1
 while 'rIdRevision5_'+str(i) in used:i+=1
 rid='rIdRevision5_'+str(i);used.add(rid);E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=ty,Target=posixpath.relpath(t,'ppt'));return rid
replacement={21:1,22:2,25:3};deleted={20,24};order=[];changes=[]
for a in list(lst):lst.remove(a)
nextid=max(int(e.get('id')) for e in oldids)+1
def addslide(k):
 global nextid
 part=mapping[f'ppt/slides/slide{k}.xml'];rid=addrel(part,NS['r']+'/slide');e=E.SubElement(lst,'{'+NS['p']+'}sldId',id=str(nextid),attrib={'{'+NS['r']+'}id':rid});nextid+=1;return part
for oldpage,e in enumerate(oldids,1):
 rid=e.get('{'+NS['r']+'}id');part=target('ppt/presentation.xml',oldrel[rid].get('Target'))
 if oldpage in deleted:rels.remove(oldrel[rid]);continue
 if oldpage in replacement:
  rels.remove(oldrel[rid]);part=addslide(replacement[oldpage]);order.append({'old':oldpage,'new':len(order)+1,'part':part,'action':'replace'})
 else:
  lst.append(e);order.append({'old':oldpage,'new':len(order)+1,'part':part,'action':'retain'})
 if oldpage==39:part=addslide(4);order.append({'old':None,'new':len(order)+1,'part':part,'action':'insert four-anchor slide'})
assert len(order)==59
# Register an independent master and unique layout IDs for the new native objects.
npr=xml(new['ppt/presentation.xml']);nrels={r.get('Id'):r for r in xml(new['ppt/_rels/presentation.xml.rels'])};masters=p.find('p:sldMasterIdLst',NS)
for i,m in enumerate(npr.findall('p:sldMasterIdLst/p:sldMasterId',NS)):
 r=nrels[m.get('{'+NS['r']+'}id')];part=mapping[target('ppt/presentation.xml',r.get('Target'))];rid=addrel(part,r.get('Type'));E.SubElement(masters,'{'+NS['p']+'}sldMasterId',id=str(2147490000+i),attrib={'{'+NS['r']+'}id':rid})
 x=xml(files[part])
 for j,l in enumerate(x.findall('p:sldLayoutIdLst/p:sldLayoutId',NS)):l.set('id',str(2147500000+i*100+j))
 files[part]=out(x)
files['ppt/presentation.xml']=out(p);files['ppt/_rels/presentation.xml.rels']=out(rels)
# Native page markers and TOC refer to the new positions.
for rec in order:
 if rec['action']!='retain':continue
 x=xml(files[rec['part']]);changed=False
 for sp in x.findall('.//p:sp',NS):
  ts=sp.findall('.//a:t',NS);tx=''.join(t.text or '' for t in ts);off=sp.find('.//a:xfrm/a:off',NS)
  if tx in [str(rec['old']),str(rec['old']).zfill(2)] and off is not None and int(off.get('x'))>11000000 and int(off.get('y'))>6000000:
   ts[0].text=str(rec['new']).zfill(2);changed=True
 if rec['old']==2:
  for t in x.findall('.//a:t',NS):
   if t.text in ['26','32','39','48','59']:t.text={'26':'24','32':'30','39':'37','48':'47','59':'58'}[t.text]
   if t.text=='선정 방법 · 앵커 ①② · 기타 프로그램 · 권역 · 배치 구상(축측) · 남북 단면 · 세부 프로그램':t.text='네 앵커 구성 · 선정 근거 · 기존 검토안 · 권역 · 배치 구상 · 남북 단면 · 세부 프로그램'
  changed=True
 if rec['old']==39:
  for t in x.findall('.//a:t',NS):
   if t.text=='선정 방법과 후보 평가 · 앵커 ①② · 기타 프로그램과 비교안 · 권역 구성 · 세부 프로그램':t.text='네 앵커와 중앙 교류공간 · 선정 근거 · 기존 프로그램 검토안 · 권역 구성 · 세부 프로그램'
  changed=True
 # The new role slide is the current program definition. Retain later calculation evidence,
 # but identify it visibly as the previous scheme rather than changing unsupported totals.
 if 40<=rec['old']<=58:
  tree=x.find('p:cSld/p:spTree',NS);qid=max(int(q.get('id')) for q in x.findall('.//p:cNvPr',NS))+1
  label='기존 프로그램 검토안' if rec['old']<47 else '기존 600세대 규모 검토안'
  frag=f'''<p:sp xmlns:p="{NS['p']}" xmlns:a="{NS['a']}"><p:nvSpPr><p:cNvPr id="{qid}" name="Previous scheme scope"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="8900000" y="210000"/><a:ext cx="2800000" cy="260000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"/><a:lstStyle/><a:p><a:pPr algn="r"/><a:r><a:rPr lang="ko-KR" sz="1050" b="0"><a:solidFill><a:srgbClr val="B66A2B"/></a:solidFill><a:latin typeface="Pretendard"/><a:ea typeface="Pretendard"/><a:cs typeface="Pretendard"/></a:rPr><a:t>{label}</a:t></a:r></a:p></p:txBody></p:sp>'''
  tree.append(E.fromstring(frag.encode('utf8')));changed=True
 if changed:files[rec['part']]=out(x);changes.append(rec)
ct=xml(files['[Content_Types].xml']);nc=xml(new['[Content_Types].xml']);exts={e.get('Extension') for e in ct if E.QName(e).localname=='Default'}
for e in nc:
 if E.QName(e).localname=='Default' and e.get('Extension') not in exts:ct.append(copy.deepcopy(e));exts.add(e.get('Extension'))
 if E.QName(e).localname=='Override' and e.get('PartName').lstrip('/') in mapping:
  q=copy.deepcopy(e);q.set('PartName','/'+mapping[e.get('PartName').lstrip('/')]);ct.append(q)
files['[Content_Types].xml']=out(ct);setcount(files,59);files=cleanup(files)
save(files,B/'revision5_full_candidate.pptx')
receipt={'source':str(SRC),'sourceSha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'deletedOriginalPages':sorted(deleted),'order':order,'notes':'New current program definition on page38. Original detailed program and area calculations retained and visibly identified as previous scheme. No unsupported recomputation of floor areas.','newChartCount':4,'totalSlides':59}
(B/'revision5_merge_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
print('Prepared 59-slide deck and 1-slide anchor file.')
