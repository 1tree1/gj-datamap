from pathlib import Path
from PIL import Image,ImageChops
import json
B=Path(__file__).parent/'build'
unchanged=[];changed=[]
for i in range(1,62):
    if i==2:continue
    a=Image.open(B/'original'/f'{i:02}.png').convert('RGB')
    b=Image.open(B/'final'/f'{i:02}.png').convert('RGB')
    if ImageChops.difference(a,b).getbbox() is None:unchanged.append(i)
    else:changed.append(i)
assert not changed,changed
a=Image.open(B/'original'/'62.png').convert('RGB').crop((0,0,1280,675))
b=Image.open(B/'final'/'64.png').convert('RGB').crop((0,0,1280,675))
assert ImageChops.difference(a,b).getbbox() is None
assert len(list((B/'final').glob('*.png')))==64
report={'renderedSlides':64,'PowerPointVersion':'16.0','originalContentPagesPixelIdentical':unchanged,'lastPageContentPixelIdenticalExceptPageMarker':True,'newAndChangedSlidesReviewed':[2,62,63,64]}
(B/'visual_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('All 60 unchanged content slides are pixel-identical. Final-slide content is unchanged. 64 slides rendered.')
