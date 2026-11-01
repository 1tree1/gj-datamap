from PIL import Image
import glob, os, re
d = r'C:\Users\OFFICE\Desktop\9_도시\work\20261005_ppt_refine\render_new'
files = sorted(glob.glob(d + r'\*.PNG'), key=lambda p: int(re.findall(r'(\d+)\.PNG', p)[0]))
print(len(files))
W, H = 800, 450
def sheet(sub, name, cols=2):
    r = (len(sub) + cols - 1) // cols
    img = Image.new('RGB', (cols * W, r * H), 'white')
    for i, f in enumerate(sub):
        im = Image.open(f).convert('RGB').resize((W, H))
        img.paste(im, ((i % cols) * W, (i // cols) * H))
    img.save(os.path.join(d, name))
k = 0
for s in range(0, len(files), 6):
    sheet(files[s:s+6], 'sheet_%02d.png' % (s // 6 + 1)); k += 1
print(k)
