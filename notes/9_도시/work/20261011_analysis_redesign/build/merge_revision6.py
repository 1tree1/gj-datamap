from pathlib import Path
import json
B=Path(__file__).parent
exec((B/'merge_revision5.py').read_text(encoding='utf8').split("new=read(B/")[0])
SRC=B.parent/'output/구경주역_중간마감_v5_분석과네앵커.pptx'
files=read(SRC);new=read(B/'revision6_slides.pptx');fontfix(new)
# Import the three edited slides and their existing native dependencies.
mapping={}
for n in new:
 if not n.startswith('ppt/') or n in ['ppt/presentation.xml','ppt/_rels/presentation.xml.rels'] or n.endswith('.rels'):continue
 d,b=posixpath.split(n);m=re.fullmatch(r'(.+?)(\d+)(\.[^.]+)',b)
 mapping[n]=posixpath.join(d,m[1]+str(int(m[2])+3000)+m[3] if m else 'revision6_'+b)
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
p=xml(files['ppt/presentation.xml']);rels=xml(files['ppt/_rels/presentation.xml.rels']);oldrel={r.get('Id'):r for r in rels}
pages={i:target('ppt/presentation.xml',oldrel[e.get('{'+NS['r']+'}id')].get('Target')) for i,e in enumerate(p.findall('p:sldIdLst/p:sldId',NS),1)}
assert len(pages)==59
for n,k in {13:1,14:2,38:3}.items():
 rid=p.findall('p:sldIdLst/p:sldId',NS)[n-1].get('{'+NS['r']+'}id')
 oldrel[rid].set('Target',posixpath.relpath(mapping[f'ppt/slides/slide{k}.xml'],'ppt'))
 pages[n]=mapping[f'ppt/slides/slide{k}.xml']
used={r.get('Id') for r in rels}
def addrel(t,ty):
 i=1
 while 'rIdRevision6_'+str(i) in used:i+=1
 rid='rIdRevision6_'+str(i);used.add(rid);E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=ty,Target=posixpath.relpath(t,'ppt'));return rid
npr=xml(new['ppt/presentation.xml']);nrels={r.get('Id'):r for r in xml(new['ppt/_rels/presentation.xml.rels'])};masters=p.find('p:sldMasterIdLst',NS)
for i,m in enumerate(npr.findall('p:sldMasterIdLst/p:sldMasterId',NS)):
 r=nrels[m.get('{'+NS['r']+'}id')];part=mapping[target('ppt/presentation.xml',r.get('Target'))];rid=addrel(part,r.get('Type'));E.SubElement(masters,'{'+NS['p']+'}sldMasterId',id=str(2147600000+i),attrib={'{'+NS['r']+'}id':rid})
 x=xml(files[part])
 for j,l in enumerate(x.findall('p:sldLayoutIdLst/p:sldLayoutId',NS)):l.set('id',str(2147610000+i*100+j))
 files[part]=out(x)
files['ppt/presentation.xml']=out(p);files['ppt/_rels/presentation.xml.rels']=out(rels)
BLUE='235D82';GRAY='B9C3CB';INK='20272E';accent_receipt=[]
def solid(parent,color):
 for c in list(parent):
  if E.QName(c).localname in ['solidFill','noFill','gradFill','pattFill','blipFill','grpFill']:parent.remove(c)
 f=E.Element('{'+NS['a']+'}solidFill');E.SubElement(f,'{'+NS['a']+'}srgbClr',val=color);parent.insert(0,f)
def serfill(ser,color):
 sp=ser.find('c:spPr',NS)
 if sp is None:
  sp=E.Element('{'+NS['c']+'}spPr');ser.insert(3,sp)
 solid(sp,color)
 for inv in ser.findall('c:invertIfNegative',NS):inv.set('val','0')
def point(ser,index,color):
 q=E.Element('{'+NS['c']+'}dPt');E.SubElement(q,'{'+NS['c']+'}idx',val=str(index));E.SubElement(q,'{'+NS['c']+'}invertIfNegative',val='0');sp=E.SubElement(q,'{'+NS['c']+'}spPr');solid(sp,color)
 line=E.SubElement(sp,'{'+NS['a']+'}ln');E.SubElement(line,'{'+NS['a']+'}noFill')
 loc=next((i for i,ch in enumerate(ser) if E.QName(ch).localname in ['dLbls','trendline','errBars','cat','val','shape','extLst']),len(ser));ser.insert(loc,q)
for n in [18,19,20,21]:
 part=pages[n];x=xml(files[part]);cr={r.get('Id'):r for r in xml(files[rp(part)])}
 for ci,c in enumerate(x.findall('.//c:chart',NS)):
  cp=target(part,cr[c.get('{'+NS['r']+'}id')].get('Target'));cx=xml(files[cp]);sers=cx.findall('.//c:ser',NS);triples=[]
  for si,ser in enumerate(sers):
   vals=[float(v) for v in ser.xpath('./c:val//c:pt/c:v/text()',namespaces=NS)]
   triples.extend((abs(v) if n==19 else v,si,i,v) for i,v in enumerate(vals))
   for q in list(ser.findall('c:dPt',NS)):ser.remove(q)
   serfill(ser,('99A4AC' if si==0 else 'D8DDE1') if n==20 and ci==1 else GRAY)
  _,si,index,value=max(triples);point(sers[si],index,BLUE)
  if n==20 and ci==1:
   lab=sers[0].find('c:dLbls',NS);original=copy.deepcopy(lab)
   for c in lab.findall('.//a:srgbClr',NS):c.set('val',INK)
   dl=E.Element('{'+NS['c']+'}dLbl');E.SubElement(dl,'{'+NS['c']+'}idx',val=str(index))
   for child in original:
    if E.QName(child).localname not in ['dLbl','showLeaderLines']:dl.append(copy.deepcopy(child))
   lab.insert(0,dl)
  files[cp]=out(cx);accent_receipt.append({'slide':n,'chart':cp,'seriesIndex':si,'pointIndex':index,'value':value,'criterion':'largest absolute net outflow' if n==19 else 'largest value'})
 # Reserve blue for highlighted numbers, and keep all other headings/labels neutral.
 for sp in x.findall('.//p:sp',NS):
  tx=''.join(sp.xpath('.//a:t/text()',namespaces=NS));keep=tx in ['−7,249','-7,249','1.63배','83.1%','76.9%']
  off=sp.find('.//a:xfrm/a:off',NS);ext=sp.find('.//a:xfrm/a:ext',NS)
  for co in sp.findall('.//a:srgbClr',NS):
   old=co.get('val').upper()
   if old not in ['235D82','245D81','2C668D','83A9BE','8AABBF','B66A2B']:continue
   if keep:co.set('val',BLUE)
   elif ext is not None and int(ext.get('cy'))<30000:co.set('val','CBD4DC')
   elif n==20 and off is not None and round(int(off.get('x'))/9525)==455 and not tx:co.set('val','99A4AC')
   else:co.set('val','606D77' if tx.startswith('현황과 분석') else INK)
  if n==20 and off is not None and not tx and round(int(off.get('x'))/9525)==548:
   for co in sp.findall('.//a:srgbClr',NS):co.set('val','D8DDE1')
 files[part]=out(x)
ct=xml(files['[Content_Types].xml']);nc=xml(new['[Content_Types].xml']);exts={e.get('Extension') for e in ct if E.QName(e).localname=='Default'}
for e in nc:
 if E.QName(e).localname=='Default' and e.get('Extension') not in exts:ct.append(copy.deepcopy(e));exts.add(e.get('Extension'))
 if E.QName(e).localname=='Override' and e.get('PartName').lstrip('/') in mapping:
  q=copy.deepcopy(e);q.set('PartName','/'+mapping[e.get('PartName').lstrip('/')]);ct.append(q)
files['[Content_Types].xml']=out(ct);setcount(files,59);files=cleanup(files)
save(files,B/'revision6_full_candidate.pptx')
(B/'revision6_merge_receipt.json').write_text(json.dumps({'source':str(SRC),'sourceSha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'totalSlides':59,'replaced':[13,14,38],'colorOnly':[18,19,20,21],'accentSelection':accent_receipt,'pages':pages},ensure_ascii=False,indent=2),encoding='utf8')
print('Prepared 59 slides, with 3 replacements and 4 color-only edits.')
