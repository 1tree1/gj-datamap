"""assets/doc 안의 파일을 접촉 시트로 만든다.
사용: python doc_sheet.py <접두사 또는 glob> <출력 이름> [열 수] [썸네일 폭]
예) python doc_sheet.py D06 contact_D06 2 800   (_hl 변형은 제외하려면 접두사 뒤에 --nohl)
"""
import glob
import os
import sys

sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import docfig as D
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

pat = sys.argv[1]
out = sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
tw = int(sys.argv[4]) if len(sys.argv) > 4 else 560
nohl = "--nohl" in sys.argv
onlyhl = "--onlyhl" in sys.argv
files = sorted(glob.glob(D.OUTDIR + "/" + pat + "*"))
files = [f for f in files if f.lower().endswith((".png", ".jpg")) and not os.path.basename(f).startswith("contact_")]
if nohl:
    files = [f for f in files if "_hl." not in f]
if onlyhl:
    files = [f for f in files if "_hl." in f]
items = []
for f in files:
    im = Image.open(f)
    im.draft("RGB", (tw * 2, tw * 2))
    im = im.convert("RGB")
    lab = os.path.splitext(os.path.basename(f))[0]
    items.append((im, lab))
sh = D.contact_sheet(items, cols=cols, thumb_w=tw, fsize=15)
p = os.path.join(D.OUTDIR, out if out.endswith(".png") else out + ".png")
sh.save(p)
print(p, sh.size, len(items), "files")
