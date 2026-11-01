import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
files = sys.argv[2:]
H = 900
ims = []
for f in files:
    im = Image.open(SCR + "prev/" + f).convert("RGB")
    im = im.resize((int(im.width * H / im.height), H))
    ims.append(im)
W = sum(i.width for i in ims) + 6 * (len(ims) - 1)
sh = Image.new("RGB", (W, H), (255, 255, 255)); x = 0
for im in ims:
    sh.paste(im, (x, 0)); x += im.width + 6
sh.save(SCR + "prev/" + sys.argv[1]); print(sh.size)
