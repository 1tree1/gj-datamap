from pathlib import Path
import zipfile,json,copy,hashlib
from lxml import etree as E
B=Path(__file__).parent;O=B.parent/'output';SRC=O/'구경주역_중간마감_v6_분석과앵커지도.pptx'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
def read(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
files=read(SRC);new=read(B/'revision7_overlay.pptx');part='ppt/slides/slide31.xml';x=E.fromstring(files[part]);tree=x.find('p:cSld/p:spTree',NS)
removed=[]
for s in list(tree):
 names=s.xpath('.//p:cNvPr/@name',namespaces=NS)
 if any(v.startswith('strategy-') for v in names):tree.remove(s);removed.extend(names)
assert len(removed)>25
# Use the user's three concepts consistently in the existing explanatory column.
for t in x.findall('.//a:t',NS):
 if t.text=='접속':t.text='연결'
 elif t.text=='교차·전환':t.text='교차'
 elif t.text=='접속점 37곳과 기존 가로의 폭·방향에 새 가로를 정렬합니다.':t.text='가로 연결 지점 37곳과 기존 가로의 폭·방향에 새 가로를 정렬합니다.'
 # Remove the older finality claim from the unchanged geographic source caption.
 elif t.text=='전략 배치도: 최종 계획 경계(푸른 면) · NGII 도로·UPIS 공원·OSM 폐선':t.text='전략 배치도: 계획 부지 경계(푸른 면) · NGII 도로·UPIS 공원·OSM 폐선'
overlay=E.fromstring(new['ppt/slides/slide1.xml']);nid=max(int(e.get('id')) for e in x.findall('.//p:cNvPr',NS))+1
for s in list(overlay.find('p:cSld/p:spTree',NS))[2:]:
 s=copy.deepcopy(s)
 for e in s.findall('.//p:cNvPr',NS):e.set('id',str(nid));nid+=1
 for pr in s.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=NS):
  for ft in ['latin','ea','cs']:
   f=pr.find('a:'+ft,NS)
   if f is None:f=E.SubElement(pr,'{'+NS['a']+'}'+ft)
   f.set('typeface','Pretendard')
 tree.append(s)
files[part]=E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
assert len(x.findall('.//a:gradFill',NS))==10
with zipfile.ZipFile(B/'revision7_full_candidate.pptx','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in files.items():z.writestr(n,b)
(B/'revision7_merge_receipt.json').write_text(json.dumps({'source':str(SRC),'sourceSha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'changedSlide':26,'changedPart':part,'removedObjects':len(removed),'nativeGradientObjects':len(x.findall('.//a:gradFill',NS)),'fanObjects':len(x.xpath('.//p:cNvPr[starts-with(@name,"r7-spread")]',namespaces=NS))},ensure_ascii=False,indent=2),encoding='utf8')
print('Updated only slide26, retaining all other deck parts.')
