from pathlib import Path
from lxml import etree as E
import zipfile,copy,json,posixpath,hashlib
B=Path(__file__).parent;O=B.parent/'output';SRC=O/'구경주역_중간마감_v8_가로계획해석.pptx'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
PR='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types'
def read(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
def xml(e):return E.tostring(e,xml_declaration=True,encoding='UTF-8',standalone=True)
files=read(SRC);fresh=read(B/'revision9_goal_slide.pptx')
sourcepart='ppt/slides/slide2003.xml';newpart='ppt/slides/slide4001.xml';notespart='ppt/notesSlides/notesSlide4001.xml'
x=E.fromstring(files[sourcepart]);tree=x.find('p:cSld/p:spTree',NS)
for q in list(tree)[2:]:tree.remove(q)
ov=E.fromstring(fresh['ppt/slides/slide1.xml'])
for q in list(ov.find('p:cSld/p:spTree',NS))[2:]:tree.append(copy.deepcopy(q))
for i,q in enumerate(x.findall('.//p:cNvPr',NS),1):q.set('id',str(i))
for pr in x.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=NS):
 for tag in ['latin','ea','cs']:
  f=pr.find('a:'+tag,NS)
  if f is None:f=E.SubElement(pr,'{'+NS['a']+'}'+tag)
  f.set('typeface','Pretendard')
files[newpart]=xml(x)
r=E.fromstring(files['ppt/slides/_rels/slide2003.xml.rels'])
for el in r:
 if el.get('Type').endswith('/notesSlide'):el.set('Target','../notesSlides/notesSlide4001.xml')
files['ppt/slides/_rels/slide4001.xml.rels']=xml(r)
# Preserve the reference notes master and add source-backed rationale to the new slide.
n=E.fromstring(files['ppt/notesSlides/notesSlide2003.xml'])
body=n.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody',namespaces=NS)[0]
for q in list(body):
 if q.tag=='{'+NS['a']+'}p':body.remove(q)
notes='''계획목표 제안
23쪽의 연결, 행정 통합, 청년 정주를 생활권 연계 강화, 도심 중심기능 회복, 지역경제 활성화, 청년 정주기반 확충의 네 계획목표로 구체화했다.
생활권 연계 강화: 동서 생활권과 남북 보행축을 연결하고 관광객과 주민의 교류 공간을 조성한다.
도심 중심기능 회복: 분산된 시청 기능의 대상지 통합을 설계안으로 제안하고 공공서비스를 집적해 반복적인 일상 이용을 확대한다.
지역경제 활성화: 역사문화와 창작 활동을 성동시장 등 주변 상권과 연계해 체험, 판매, 지역 일자리를 지원한다.
청년 정주기반 확충: 주거와 일자리, 생활서비스를 복합화해 청년의 지속적인 거주와 활동 여건을 마련한다.
네 제목은 아래 자료의 계획 개념을 대상지에 맞게 재구성한 표현이다. 경주시의 확정 목표나 승인된 시청 이전 계획을 인용한 것이 아니다.
참고자료 (확인 2026-10-12)
1. 경주시, 2040 도시기본계획 시민참여단 도시 미래상 전달식 (2025-12-22). 생활권 중심 공간구조, 역사문화 자산 활용 등 수립 과정의 방향을 참고.
https://www.gyeongju.go.kr/mayor/page.do?mnu_uid=1413&pageNo=23&pageOrder=0&pagePrvNxt=1&pageRef=0&parm_bod_uid=310791&parm_mnu_uid=1334&srchBgpUid=-1&srchColumn=&srchEDate=&srchEnable=1&srchKeyword=&srchSDate=&srchVoteType=-1&step=258
2. 국토연구원, 도심의 기존 기능과 연계한 점진적 도시재생방안 연구: 인구감소 지방 중소도심을 중심으로. 기능적·공간적 연계, 도심 주거기능 회복, 상권·창업 활성화 개념을 참고.
https://library.krihs.re.kr/%24/10110/contents/5946539
3. 대전광역시 서구, 도시재생 뉴딜사업이란? 주거복지, 일자리, 생활 인프라, 중심시가지 활성화의 정책 개념을 참고.
https://seogu.go.kr/kor/sub06_14_05_01.do
4. 국토교통부·주택도시보증공사, 도시재생뉴딜 소개. 지역특화 재생 및 청년 일자리, 기초생활 인프라 개념을 참고.
https://enhuf.molit.go.kr/fur/pp/ps/POPPS017M01.jsp'''
for line in notes.splitlines():
 pp=E.SubElement(body,'{'+NS['a']+'}p');rr=E.SubElement(pp,'{'+NS['a']+'}r');tt=E.SubElement(rr,'{'+NS['a']+'}t');tt.text=line
files[notespart]=xml(n)
nr=E.fromstring(files['ppt/notesSlides/_rels/notesSlide2003.xml.rels'])
for el in nr:
 if el.get('Type').endswith('/slide'):el.set('Target','../slides/slide4001.xml')
files['ppt/notesSlides/_rels/notesSlide4001.xml.rels']=xml(nr)
# Insert after the current page 23 and shift subsequent page labels by one.
pres=E.fromstring(files['ppt/presentation.xml']);rels=E.fromstring(files['ppt/_rels/presentation.xml.rels']);rm={el.get('Id'):el.get('Target') for el in rels};lst=pres.find('p:sldIdLst',NS)
renumbered=[]
for old_i,ref in enumerate(list(lst),1):
 if old_i<24:continue
 part=posixpath.normpath(posixpath.join('ppt',rm[ref.get('{'+NS['r']+'}id')]))
 sx=E.fromstring(files[part]);found=0
 for sp in sx.findall('.//p:sp',NS):
  ts=sp.findall('.//a:t',NS);off=sp.find('.//a:xfrm/a:off',NS)
  if off is not None and int(off.get('y'))>630*9525 and int(off.get('x'))>1100*9525 and ''.join(t.text or '' for t in ts)==str(old_i):
   assert len(ts)==1;ts[0].text=str(old_i+1);found+=1
 assert found==1,(old_i,found)
 files[part]=xml(sx);renumbered.append({'old':old_i,'new':old_i+1,'part':part})
rid='rIdPlanGoals';assert rid not in rm
E.SubElement(rels,'{'+PR+'}Relationship',Id=rid,Type=NS['r']+'/slide',Target='slides/slide4001.xml')
newref=E.Element('{'+NS['p']+'}sldId',id=str(max(int(q.get('id')) for q in lst)+1));newref.set('{'+NS['r']+'}id',rid);lst.insert(23,newref)
files['ppt/presentation.xml']=xml(pres);files['ppt/_rels/presentation.xml.rels']=xml(rels)
cts=E.fromstring(files['[Content_Types].xml'])
for part,ctype in [(newpart,'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'),(notespart,'application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml')]:
 E.SubElement(cts,'{'+CT+'}Override',PartName='/'+part,ContentType=ctype)
files['[Content_Types].xml']=xml(cts)
app=E.fromstring(files['docProps/app.xml']);app.find('{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}Slides').text='60';files['docProps/app.xml']=xml(app)
with zipfile.ZipFile(B/'revision9_full_candidate.pptx','w',zipfile.ZIP_DEFLATED) as z:
 for name,value in files.items():z.writestr(name,value)
f=(B/'finalize_revision8.mjs').read_text(encoding='utf8').replace('revision8','revision9').replace('v8_가로계획해석','v9_계획목표').replace('explicitTotalSlideCount:59','explicitTotalSlideCount:60').replace('20,21,52]','20,21,53]')
(B/'finalize_revision9.mjs').write_text(f,encoding='utf8')
(B/'revision9_edit_receipt.json').write_text(json.dumps({'source':str(SRC),'sourceSha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'newSlideIndex':24,'newSlidePart':newpart,'renumberedSlides':renumbered,'totalSlides':60,'keywords':['생활권 연계 강화','도심 중심기능 회복','지역경제 활성화','청년 정주기반 확충']},ensure_ascii=False,indent=2),encoding='utf8')
print('Inserted planning goals at page24; updated36 subsequent page labels; total60.')
