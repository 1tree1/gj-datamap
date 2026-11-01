from pathlib import Path
from lxml import etree as E
import zipfile,copy,json,posixpath,hashlib
B=Path(__file__).parent;O=B.parent/'output';SRC=O/'구경주역_중간마감_v9_계획목표.pptx'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'};PR='http://schemas.openxmlformats.org/package/2006/relationships'
def read(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
def xml(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
files=read(SRC);over=read(B/'revision10_map_overlay.pptx');part='ppt/slides/slide1002.xml';x=E.fromstring(files[part]);tree=x.find('p:cSld/p:spTree',NS)
origtexts=x.xpath('.//a:t/text()',namespaces=NS)
byid={int(q.xpath('.//p:cNvPr/@id',namespaces=NS)[0]):q for q in list(tree)[2:]}
def move(i,x,y,w,h,size=None):
 q=byid[i];tr=q.find('.//a:xfrm',NS);off=tr.find('a:off',NS);ext=tr.find('a:ext',NS)
 off.set('x',str(round(x*9525)));off.set('y',str(round(y*9525)));ext.set('cx',str(round(w*9525)));ext.set('cy',str(round(h*9525)))
 if size is not None:
  for el in q.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=NS):el.set('sz',str(round(size*75)))
# Keep the original title, subtitle, photo pixels and all source comparison text.
move(10,696,181,517,517*304/555)
move(11,696,151,255,29,18);move(12,967,151,265,29,18)
move(13,925,474,105,25,17);move(14,1113,474,102,25,17)
for ids,y,label in [((15,16,17,18),505,'width'),((19,20,21,22),541,'storeys'),((23,24,25,26),577,'parcel')]:
 lab,west,east,line=ids
 move(lab,696,y,211,27,17);move(west,925,y-5,153,34,25);move(east,1113,y-5,119,34,25)
 move(line,696,y+31,536,.1)
move(27,696,611,536,18,13)
move(28,80,586,342,24,14)
move(5,48,634,1184,.1)
move(6,48,642,60,26,13)
move(7,120,638,1112,35,19)
move(8,48,678,1136,26,12.2)
move(9,1185,675,47,28,17)
# Existing provenance is retained; the new data channel is made explicit.
source=byid[8].find('.//a:t',NS);source.text+=' · 지도: QGIS / NGII 층수(nmly)'
rels=E.fromstring(files['ppt/slides/_rels/slide1002.xml.rels']);orels=E.fromstring(over['ppt/slides/_rels/slide1.xml.rels']);remap={}
for el in orels:
 if el.get('Type').endswith('/image'):
  remap[el.get('Id')]='rIdHeightMap10'
  target=posixpath.normpath(posixpath.join('ppt/slides',el.get('Target')));newmedia='ppt/media/height_qgis_revision10.png';files[newmedia]=over[target.lstrip('/')]
  E.SubElement(rels,'{'+PR+'}Relationship',Id='rIdHeightMap10',Type=NS['r']+'/image',Target='../media/height_qgis_revision10.png')
overx=E.fromstring(over['ppt/slides/slide1.xml']);nid=max(byid)+1
for q in list(overx.find('p:cSld/p:spTree',NS))[2:]:
 q=copy.deepcopy(q)
 for e in q.findall('.//p:cNvPr',NS):e.set('id',str(nid));nid+=1
 for e in q.iter():
  for key,val in list(e.attrib.items()):
   if key in ['{'+NS['r']+'}embed','{'+NS['r']+'}link'] and val in remap:e.set(key,remap[val])
 for pr in q.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=NS):
  for tag in ['latin','ea','cs']:
   f=pr.find('a:'+tag,NS)
   if f is None:f=E.SubElement(pr,'{'+NS['a']+'}'+tag)
   f.set('typeface','Pretendard')
 tree.append(q)
files[part]=xml(x);files['ppt/slides/_rels/slide1002.xml.rels']=xml(rels)
notespart='ppt/notesSlides/notesSlide1002.xml';n=E.fromstring(files[notespart]);body=n.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody',namespaces=NS)[0]
notes='''추가 지도: QGIS 3.32.0에서 렌더링한 실제 건물 층수 분포. 원자료 NGII 연속수치지도 N3A_B0010000의 nmly 속성(지상 층수)을 사용했다. 실제 건물 높이(m)를 측정하거나 층고를 가정해 환산한 지도가 아니다.
원본 프로젝트: work/qgis/gj_site_base.qgz의 B001 건물 레이어와 같은 원본 SHP를 사용. 좌표계 EPSG:5179에서 EPSG:5187로 변환.
구역 경계는 2026-8 고시구역의 도면 추출 경계 archive/C_data/processed/gosi2026-8_zone_5187.geojson. 계획 배치도의 확장 경계와 구분.
등급은 1층, 2층, 3–5층, 6층 이상. 표시 범위 8,365동 모두 nmly가 유효하며 층수 미상은 0동.
기존 수치 확인: 경계 밖 0–150m 건물 중 서측 602동의 1층은 418동(69.435%), 동측 729동의 1층은 680동(93.278%). 기존 69.4%, 93.3%와 일치.
분석 방향은 건물 중심점에서 가장 가까운 고시구역 경계점으로부터의 방위에 따라 구분. 서측과 동측 비교 건물을 진하게 표시하고 다른 건물은 배경으로 연하게 표시했다. 점선은 경계 밖 150m 외곽선이다.
기존 가로 폭·필지 면적 수치, 현장 사진, 해석 문구를 유지했다. 사진의 원본 픽셀과 종횡비를 유지하고 배치·크기만 조정.
편집 가능한 지도 프로젝트: build/height_map_data/건물층수_슬라이드12.qgz
QGIS 지도 렌더링 방법 참고: https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/composer.html'''
for line in notes.splitlines():
 pp=E.SubElement(body,'{'+NS['a']+'}p');rr=E.SubElement(pp,'{'+NS['a']+'}r');tt=E.SubElement(rr,'{'+NS['a']+'}t');tt.text=line
files[notespart]=xml(n)
newtexts=x.xpath('.//a:t/text()',namespaces=NS)
assert all(t in newtexts or any(v.startswith(t) for v in newtexts) for t in origtexts)
with zipfile.ZipFile(B/'revision10_full_candidate.pptx','w',zipfile.ZIP_DEFLATED) as z:
 for name,value in files.items():z.writestr(name,value)
f=(B/'finalize_revision9.mjs').read_text(encoding='utf8').replace('revision9','revision10').replace('v9_계획목표','v10_건물높이지도')
(B/'finalize_revision10.mjs').write_text(f,encoding='utf8')
(B/'revision10_edit_receipt.json').write_text(json.dumps({'source':str(SRC),'sourceSha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'changedSlide':12,'totalSlides':60,'allSourceTextPreserved':True,'originalPhotoPreserved':True,'qgisMap':'assets/height_qgis_revision10.png'},ensure_ascii=False,indent=2),encoding='utf8')
print('Updated page12 only; all original content retained with proportional photograph.')

