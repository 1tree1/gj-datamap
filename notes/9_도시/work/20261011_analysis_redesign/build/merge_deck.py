from pathlib import Path
import zipfile, posixpath, re, json, copy, hashlib, colorsys, sys
from lxml import etree as E

R=Path(r'C:\Users\OFFICE\Desktop\9_도시')
B=R/'work/20261011_analysis_redesign/build'
ORIG=R/'work/20261011_midterm_deck/output/구경주역_중간마감_v2.pptx'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
def xml(b):return E.fromstring(b)
def out(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def relpath(part):return posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels')
def relsource(part):return posixpath.join(posixpath.dirname(posixpath.dirname(part)),posixpath.basename(part)[:-5]) if part!='_rels/.rels' else ''
def target(part,t):return posixpath.normpath(posixpath.join(posixpath.dirname(part),t)).lstrip('/') if not t.startswith('/') else t[1:]
with zipfile.ZipFile(ORIG) as z:files={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
with zipfile.ZipFile(B/'analysis_draft.pptx') as z:new={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
mapping={}
for n in new:
 if not n.startswith('ppt/') or n in ['ppt/presentation.xml','ppt/_rels/presentation.xml.rels']:continue
 if n.endswith('.rels'):
  continue
 d,b=posixpath.split(n);m=re.fullmatch(r'(.+?)(\d+)(\.[^.]+)',b)
 mapping[n]=posixpath.join(d,m[1]+str(int(m[2])+1000)+m[3] if m else 'analysis_'+b)
for n in new:
 if n.endswith('.rels') and relsource(n) in mapping:mapping[n]=relpath(mapping[relsource(n)])
for src,dst in mapping.items():
 b=new[src]
 if src.endswith('.rels'):
  root=xml(b);source=relsource(src);destsource=mapping[source]
  for r in root:
   if r.get('TargetMode')=='External':continue
   tgt=target(source,r.get('Target'))
   if tgt in mapping:r.set('Target',posixpath.relpath(mapping[tgt],posixpath.dirname(destsource)))
  b=out(root)
 assert dst not in files,dst
 files[dst]=b

root=xml(files['ppt/presentation.xml']);rels=xml(files['ppt/_rels/presentation.xml.rels']);oldids=list(root.find('p:sldIdLst',NS));oldrels={r.get('Id'):r for r in rels}
for el in oldids[10:28]:rels.remove(oldrels[el.get('{'+NS['r']+'}id')])
used={r.get('Id') for r in rels}
def addrel(tgt,ty):
 i=1
 while 'rIdAnalysis'+str(i) in used:i+=1
 rid='rIdAnalysis'+str(i);used.add(rid);r=E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=ty,Target=posixpath.relpath(tgt,'ppt'));return rid
lst=root.find('p:sldIdLst',NS)
for x in list(lst):lst.remove(x)
for x in oldids[:10]:lst.append(x)
for i in range(1,16):
 rid=addrel(mapping[f'ppt/slides/slide{i}.xml'],NS['r']+'/slide');E.SubElement(lst,'{'+NS['p']+'}sldId',id=str(400+i),attrib={'{'+NS['r']+'}id':rid})
for x in oldids[28:]:lst.append(x)
# Register the new master in the root presentation. The master owns its layouts.
nr=xml(new['ppt/presentation.xml']);nrr={r.get('Id'):r for r in xml(new['ppt/_rels/presentation.xml.rels'])}
masters=root.find('p:sldMasterIdLst',NS)
for i,m in enumerate(nr.findall('p:sldMasterIdLst/p:sldMasterId',NS)):
 rr=nrr[m.get('{'+NS['r']+'}id')];tgt=target('ppt/presentation.xml',rr.get('Target'));rid=addrel(mapping[tgt],rr.get('Type'))
 E.SubElement(masters,'{'+NS['p']+'}sldMasterId',id=str(2147483900+i),attrib={'{'+NS['r']+'}id':rid})
files['ppt/presentation.xml']=out(root);files['ppt/_rels/presentation.xml.rels']=out(rels)
# The original registered notes master is shared by the replacement notes.
for n,b in list(files.items()):
 if n.startswith('ppt/notesSlides/_rels/') and '100' in n:
  x=xml(b)
  for rr in x:
   if rr.get('Type','').endswith('/notesMaster'):rr.set('Target','../notesMasters/notesMaster1.xml')
  files[n]=out(x)
# Keep layout identifiers unique across the added master.
for n,b in list(files.items()):
 if n.startswith('ppt/slideMasters/slideMaster100') and n.endswith('.xml'):
  x=xml(b)
  for i,e in enumerate(x.findall('p:sldLayoutIdLst/p:sldLayoutId',NS)):e.set('id',str(2147484000+i))
  files[n]=out(x)

newdesc='대상지 · 도시조직 · 동서 단절 · 활력 격차 · 남북 이용 · 인구 · 청년 · 지역 쇠퇴 · 관광 · 주민 생활 · 공공행정 · 사이트 조건 · 상위계획'
origdesc='대상지 · 위치 · 보행 단절 · 유동 격차 · 남북 관계 · 방문 · 주변 지역 · 인구 · 청년 · 야간·업종 · 규제·유산 · 조직 · 성과 지표 · 상위계획 · 문제 종합'
for n in [2,6]:
 part=f'ppt/slides/slide{n}.xml';x=xml(files[part])
 for t in x.findall('.//a:t',NS):
  if t.text==origdesc:t.text=newdesc
  if n==2 and t.text in ['29','35','42','51','62']:t.text=str(int(t.text)-3).zfill(2)
 files[part]=out(x)
# Renumber only the original page footer by its location, never arbitrary values.
changes=[]
for n in range(29,64):
 part=f'ppt/slides/slide{n}.xml';x=xml(files[part]);changed=False
 for sp in x.findall('.//p:sp',NS):
  ts=sp.findall('.//a:t',NS);tx=''.join(t.text or '' for t in ts);off=sp.find('.//a:xfrm/a:off',NS)
  if tx==str(n).zfill(2) and off is not None and int(off.get('x'))>11000000 and int(off.get('y'))>6000000:
   ts[0].text=str(n-3).zfill(2);changed=True
 assert changed,(n,'footer missing')
 files[part]=out(x);changes.append({'original':n,'final':n-3,'change':'footer and Pretendard only'})
# Carry content types for all new parts.
ct=xml(files['[Content_Types].xml']);newct=xml(new['[Content_Types].xml']);exts={x.get('Extension') for x in ct if E.QName(x).localname=='Default'}
for x in newct:
 if E.QName(x).localname=='Default' and x.get('Extension') not in exts:ct.append(copy.deepcopy(x));exts.add(x.get('Extension'))
 if E.QName(x).localname=='Override' and x.get('PartName').lstrip('/') in mapping:
  y=copy.deepcopy(x);y.set('PartName','/'+mapping[x.get('PartName').lstrip('/')]);ct.append(y)
# Remove obsolete analysis slides and their unused media by following OPC relationships.
seen=set();todo=['']
while todo:
 src=todo.pop();rp=relpath(src) if src else '_rels/.rels'
 if src:seen.add(src)
 if rp in files:
  seen.add(rp)
  for r in xml(files[rp]):
   if r.get('TargetMode')=='External':continue
   t=target(src,r.get('Target'))
   if t not in seen:
    assert t in files,(src,t)
    todo.append(t)
files={n:b for n,b in files.items() if n in seen or n=='[Content_Types].xml'}
for x in list(ct):
 if E.QName(x).localname=='Override' and x.get('PartName').lstrip('/') not in files:ct.remove(x)
files['[Content_Types].xml']=out(ct)
# User explicitly requested a single font throughout, including numeric runs,
# theme defaults, legacy charts, notes, and tables.
fonttags=['latin','ea','cs']
for n,b in list(files.items()):
 if '--raw' in sys.argv:continue
 if not n.endswith('.xml') or not n.startswith('ppt/'):continue
 x=xml(b)
 # Recolor original red accents without changing composition or text sizes.
 # Photos and source drawings retain their source pixels.
 for color in x.findall('.//a:srgbClr',NS):
  v=color.get('val','')
  if len(v)!=6:continue
  rgb=tuple(int(v[i:i+2],16)/255 for i in (0,2,4));h,light,sat=colorsys.rgb_to_hls(*rgb)
  if sat>.22 and (h<.055 or h>.91):
   nh,nlight,nsat=colorsys.rgb_to_hls(35/255,93/255,130/255)
   ref_light=colorsys.rgb_to_hls(200/255,16/255,46/255)[1]
   new_light=nlight*light/ref_light if light<ref_light else nlight+(light-ref_light)*(1-nlight)/(1-ref_light)
   rgb2=colorsys.hls_to_rgb(nh,new_light,nsat)
   color.set('val',''.join(f'{round(c*255):02X}' for c in rgb2))
 for tag in fonttags:
  for f in x.findall('.//a:'+tag,NS):f.set('typeface','Pretendard')
 for tag in ['rPr','defRPr','endParaRPr']:
  for pr in x.findall('.//a:'+tag,NS):
   for ft in fonttags:
    f=pr.find('a:'+ft,NS)
    if f is None:f=E.SubElement(pr,'{'+NS['a']+'}'+ft)
    f.set('typeface','Pretendard')
 files[n]=out(x)
if 'docProps/app.xml' in files:
 app=xml(files['docProps/app.xml']);nsapp=E.QName(app).namespace
 app.find('{'+nsapp+'}Slides').text='60';files['docProps/app.xml']=out(app)
dest=B/('merged_raw.pptx' if '--raw' in sys.argv else 'merged_candidate.pptx')
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in files.items():z.writestr(n,b)
(B/'merge_receipt.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(ORIG.read_bytes()).hexdigest(),'finalSlideCount':60,'retainedOriginalPages':[1,2,3,4,5,6,7,8,9,10]+list(range(29,64)),'removedOriginalPages':list(range(11,29)),'newAnalysisPages':list(range(11,26)),'preservationChanges':changes,'font':'Pretendard','accent':'blue; orange for contrast'},ensure_ascii=False,indent=2),encoding='utf8')
print(dest, len(files),'parts')
