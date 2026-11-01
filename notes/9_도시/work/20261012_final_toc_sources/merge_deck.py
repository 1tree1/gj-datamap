from pathlib import Path
from lxml import etree as E
import zipfile, copy, posixpath, hashlib, json

R=Path(__file__).parent; B=R/'build'
SRC=Path(r'C:\Users\OFFICE\Desktop\261012_중간마감pt_건축디자인6_b분반_이승규,김민승.pptx')
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL='http://schemas.openxmlformats.org/package/2006/relationships'
def parse(b):return E.fromstring(b)
def out(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def read(p):
    with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist() if not n.endswith('/')}
def owner(n):
    return posixpath.join(posixpath.dirname(posixpath.dirname(n)),posixpath.basename(n)[:-5])
def target(n,t):return posixpath.normpath(posixpath.join(posixpath.dirname(n),t)).lstrip('/') if not t.startswith('/') else t[1:]

original=read(SRC); files=dict(original); new=read(B/'sources_section.pptx')
mapping={n:posixpath.join(posixpath.dirname(n),'finalrefs_'+posixpath.basename(n)) for n in new if n.startswith('ppt/') and not n.endswith('.rels') and n!='ppt/presentation.xml' and not n.startswith('ppt/notesMasters/')}
for n in new:
    if n.endswith('.rels') and owner(n) in mapping:
        newowner=mapping[owner(n)]
        mapping[n]=posixpath.join(posixpath.dirname(newowner),'_rels',posixpath.basename(newowner)+'.rels')
opr=parse(original['ppt/presentation.xml']);oprels={r.get('Id'):r for r in parse(original['ppt/_rels/presentation.xml.rels'])}
onid=opr.find('p:notesMasterIdLst/p:notesMasterId',NS)
oldnotesmaster=target('ppt/presentation.xml',oprels[onid.get('{'+NS['r']+'}id')].get('Target'))
for n,b in new.items():
    if n not in mapping:continue
    dest=mapping[n]
    if n.endswith('.rels'):
        # A relationship part is named after its remapped owner.
        oldowner=owner(n)
        newowner=mapping[oldowner]
        dest=posixpath.join(posixpath.dirname(newowner),'_rels',posixpath.basename(newowner)+'.rels')
        mapping[n]=dest
        x=parse(b)
        for rel in x:
            if rel.get('TargetMode')=='External':continue
            t=target(oldowner,rel.get('Target'))
            if t in mapping:rel.set('Target',posixpath.relpath(mapping[t],posixpath.dirname(newowner)))
            if rel.get('Type').endswith('/notesMaster'):rel.set('Target',posixpath.relpath(oldnotesmaster,posixpath.dirname(newowner)))
        b=out(x)
    elif n.endswith('.xml'):
        x=parse(b)
        for pr in x.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=NS):
            for f in ['latin','ea','cs']:
                q=pr.find('a:'+f,NS)
                if q is None:q=E.SubElement(pr,'{'+NS['a']+'}'+f)
                q.set('typeface','Pretendard')
        for tc in x.findall('.//a:tcPr',NS):
            for tag in ['lnL','lnR','lnT','lnB','lnTlToBr','lnBlToTr']:
                for q in tc.findall('a:'+tag,NS):tc.remove(q)
                q=E.Element('{'+NS['a']+'}'+tag,w='0');E.SubElement(q,'{'+NS['a']+'}noFill');tc.insert(0,q)
        for pr in x.findall('.//a:tblPr',NS):
            for q in pr.findall('a:tableStyleId',NS):pr.remove(q)
        b=out(x)
    assert dest not in files
    files[dest]=b

# Update only the requested table of contents, keeping all original objects and geometry.
toc=parse(files['ppt/slides/slide2.xml'])
updates={
 '7':'계획 개요 · 계획 요약 · 5대 계획 원칙',
 '8':'03–05',
 '12':'대상지·역사·주변 자산 · 도시조직·가시성·교통 · 유동·인구·청년 · 관광·시민 요구·행정 분산 · 재생 방향·계획목표',
 '13':'06–24',
 '17':'컨셉 위계 · 세 전략의 공간 배치와 다이어그램 · 관광과 정주 연계 조건 · 선례',
 '18':'25–30',
 '22':'도시축 구상과 근거 · 차량·보행 도로망 · 최종 도로계획도와 계획표 · 가구·획지',
 '23':'31–37',
 '27':'네 앵커와 중앙 교류공간 · 프로그램 선정 · 기존 검토안 · 권역·배치·단면 · 세부 프로그램',
 '28':'38–47',
 '31':'계획인구와 규모',
 '32':'방문·근로·정주 인구 · 프로그램 면적 · 주차 · 토지이용 · 모델 비교 · 개발규모 산정표 · 조정 항목',
 '33':'48–60',
 '36':'현황·자료 출처',
 '37':'폐역 부지의 현재 모습 · 데이터 출처 ①② · 자료 출처와 확인 상태',
 '38':'61–64'
}
changed_ids=[]
for sp in toc.findall('.//p:sp',NS):
    nid=sp.find('p:nvSpPr/p:cNvPr',NS).get('id')
    if nid not in updates:continue
    texts=sp.findall('.//a:t',NS);assert len(texts)==1
    texts[0].text=updates[nid];changed_ids.append(nid)
assert set(changed_ids)==set(updates)
files['ppt/slides/slide2.xml']=out(toc)

# Insert the two new source slides immediately before the original last slide.
pr=parse(files['ppt/presentation.xml']);rels=parse(files['ppt/_rels/presentation.xml.rels'])
lst=pr.find('p:sldIdLst',NS);oldids=list(lst);assert len(oldids)==62
used={r.get('Id') for r in rels}
def addrel(t,typ):
    i=1
    while 'rIdFinalRefs'+str(i) in used:i+=1
    rid='rIdFinalRefs'+str(i);used.add(rid)
    E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=typ,Target=posixpath.relpath(t,'ppt'))
    return rid
nextid=max(int(x.get('id')) for x in oldids)+1
for i in [1,2]:
    rid=addrel(mapping[f'ppt/slides/slide{i}.xml'],NS['r']+'/slide')
    sid=E.Element('{'+NS['p']+'}sldId',id=str(nextid),attrib={'{'+NS['r']+'}id':rid});nextid+=1
    lst.insert(60+i,sid)

# Register new masters with unique layout ids.
npr=parse(new['ppt/presentation.xml']);nrels={r.get('Id'):r for r in parse(new['ppt/_rels/presentation.xml.rels'])}
masterlist=pr.find('p:sldMasterIdLst',NS)
occupied={int(x.get('id')) for x in masterlist}
for i,m in enumerate(npr.findall('p:sldMasterIdLst/p:sldMasterId',NS)):
    oldrel=nrels[m.get('{'+NS['r']+'}id')]
    part=mapping[target('ppt/presentation.xml',oldrel.get('Target'))]
    rid=addrel(part,oldrel.get('Type'));mid=2147780000+i
    assert mid not in occupied
    E.SubElement(masterlist,'{'+NS['p']+'}sldMasterId',id=str(mid),attrib={'{'+NS['r']+'}id':rid})
    x=parse(files[part])
    for j,l in enumerate(x.findall('p:sldLayoutIdLst/p:sldLayoutId',NS)):l.set('id',str(2147790000+i*100+j))
    files[part]=out(x)
files['ppt/presentation.xml']=out(pr);files['ppt/_rels/presentation.xml.rels']=out(rels)

# The preserved final slide becomes page 64, so only its page marker changes.
last=parse(files['ppt/slides/slide62.xml']);count=0
for sp in last.findall('.//p:sp',NS):
    off=sp.find('.//a:xfrm/a:off',NS);ts=sp.findall('.//a:t',NS)
    if off is not None and int(off.get('y'))>630*9525 and int(off.get('x'))>1100*9525 and ''.join(t.text or '' for t in ts)=='62':
        ts[0].text='64';count+=1
assert count==1
files['ppt/slides/slide62.xml']=out(last)

ct=parse(files['[Content_Types].xml']);nct=parse(new['[Content_Types].xml'])
exts={e.get('Extension') for e in ct if E.QName(e).localname=='Default'}
for e in nct:
    if E.QName(e).localname=='Default' and e.get('Extension') not in exts:ct.append(copy.deepcopy(e));exts.add(e.get('Extension'))
    if E.QName(e).localname=='Override' and e.get('PartName').lstrip('/') in mapping:
        q=copy.deepcopy(e);q.set('PartName','/'+mapping[e.get('PartName').lstrip('/')]);ct.append(q)
files['[Content_Types].xml']=out(ct)
app=parse(files['docProps/app.xml']);app.find('{'+E.QName(app).namespace+'}Slides').text='64';files['docProps/app.xml']=out(app)

# Prove every original part outside the requested edits/navigation stayed byte-identical.
allowed={'ppt/slides/slide2.xml','ppt/slides/slide62.xml','ppt/presentation.xml','ppt/_rels/presentation.xml.rels','[Content_Types].xml','docProps/app.xml'}
changed=[n for n,b in original.items() if files[n]!=b]
assert set(changed)<=allowed
for n in files:
    if not n.endswith('.rels'):continue
    base='' if n=='_rels/.rels' else owner(n)
    for r in parse(files[n]):
        if r.get('TargetMode')=='External':continue
        assert target(base,r.get('Target')) in files,(n,r.get('Target'))
dest=B/'candidate.pptx'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in files.items():z.writestr(n,b)
receipt={'source':str(SRC),'sourceSha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'originalSlideCount':62,'finalSlideCount':64,'editedSlides':[2],'insertedSlides':[62,63],'finalSlidePageMarker':64,'changedOriginalParts':changed,'allOtherOriginalPartsByteIdentical':True}
(B/'edit_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
