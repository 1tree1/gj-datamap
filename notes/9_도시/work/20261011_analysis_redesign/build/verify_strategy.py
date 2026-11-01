from pathlib import Path
import zipfile,json,hashlib
from PIL import Image,ImageChops
B=Path(__file__).parent;R=B.parent
def read(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
old=read(R/'output/구경주역_중간마감_v3_현황분석.pptx');new=read(R/'output/구경주역_중간마감_v4_전략다이어그램.pptx')
changed=[n for n in old if old[n]!=new.get(n)]
assert set(changed)=={'ppt/slides/slide31.xml','ppt/slides/_rels/slide31.xml.rels'},changed
same=[];different=[]
for i in range(1,61):
 a=Image.open(B/f'powerpoint_render/{i:02d}.png').convert('RGB');b=Image.open(B/f'strategy_final_render/{i:02d}.png').convert('RGB')
 (same if ImageChops.difference(a,b).getbbox() is None else different).append(i)
assert different==[28],different
receipt=json.loads((B/'strategy_revision_final.validation.json').read_text(encoding='utf8'))
assert not [w for w in receipt['presentationLayout']['warnings'] if w.get('slide')==28]
result=dict(changedParts=changed,visuallyChangedSlides=different,pixelIdenticalOtherSlides=len(same),slide28Warnings=0,sha256=receipt['finalSha256'],nativeFontFamilies=receipt['fontSelection']['observed_font_families'])
(B/'strategy_visual_verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8');print(json.dumps(result,ensure_ascii=True))
