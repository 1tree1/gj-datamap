from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
root=Path(__file__).parent/'build'
files=sorted((root/'original').glob('*.png'))
for start in range(0,len(files),16):
    out=Image.new('RGB',(1600,960),'#dddddd')
    draw=ImageDraw.Draw(out)
    for j,p in enumerate(files[start:start+16]):
        im=Image.open(p).convert('RGB').resize((400,225))
        x=(j%4)*400;y=(j//4)*240
        out.paste(im,(x,y));draw.text((x+4,y+225),p.stem,fill='black')
    out.save(root/f'original_contact_{start+1:02}.jpg',quality=90)
