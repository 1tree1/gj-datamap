from pathlib import Path
from lxml import etree as E
import zipfile,json,hashlib
B=Path(__file__).parent;O=B.parent/'output';SRC=O/'구경주역_중간마감_v7_연결교차확산.pptx'
with zipfile.ZipFile(SRC) as z:files={n:z.read(n) for n in z.namelist()}
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
part='ppt/slides/slide3001.xml';x=E.fromstring(files[part])
replacements={
 '격자에서는 넓은 시야가 이어지고 골목에서는 좁아짐과 확장이 반복된다.':'서측 가로는 주 연결축으로 연장하고, 동측 골목은 시야가 열리는 지점과 연결한다.',
 '동측 경계의 시야가 열리는 지점을 보행 접속 후보로 검토한다.':'교차부에는 열린 공간을 두어 이동 방향을 명확히 한다.'
}
changed=[]
for t in x.findall('.//a:t',NS):
 if t.text in replacements:changed.append(t.text);t.text=replacements[t.text]
assert set(changed)==set(replacements),changed
files[part]=E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(B/'revision8_full_candidate.pptx','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in files.items():z.writestr(n,b)
f=(B/'finalize_revision7.mjs').read_text(encoding='utf8').replace('revision7','revision8').replace('v7_연결교차확산','v8_가로계획해석')
(B/'finalize_revision8.mjs').write_text(f,encoding='utf8')
(B/'revision8_edit_receipt.json').write_text(json.dumps({'source':str(SRC),'sourceSha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'changedSlide':13,'part':part,'replacements':replacements},ensure_ascii=False,indent=2),encoding='utf8')
print('Updated only the two interpretation sentences on page13.')
