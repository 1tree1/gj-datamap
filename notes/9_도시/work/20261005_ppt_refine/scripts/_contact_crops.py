from PIL import Image
import glob, os
d = r'C:\Users\OFFICE\Desktop\9_도시\work\20261005_ppt_refine\assets\crops'
fs = sorted(glob.glob(d + r'\*.png'))
W = 520
ims = []
for f in fs:
    im = Image.open(f).convert('RGB'); s = W / im.width; im = im.resize((W, int(im.height * s))); ims.append((os.path.basename(f), im))
cols = 4; rows = (len(ims) + cols - 1) // cols
rh = [max(i.height for _, i in ims[r*cols:(r+1)*cols]) + 18 for r in range(rows)]
sheet = Image.new('RGB', (cols * W, sum(rh)), 'white')
from PIL import ImageDraw
dr = ImageDraw.Draw(sheet)
y = 0
for r in range(rows):
    for c in range(cols):
        k = r * cols + c
        if k >= len(ims): break
        nm, im = ims[k]; sheet.paste(im, (c * W, y + 18)); dr.rectangle([c*W, y, c*W+W, y+16], fill=(255,255,0)); dr.text((c*W+4, y+2), nm, fill=(0,0,0))
    y += rh[r]
sheet.save(r'C:\Users\OFFICE\Desktop\9_도시\work\20261005_ppt_refine\assets\crops_contact.png'); print(sheet.size)
