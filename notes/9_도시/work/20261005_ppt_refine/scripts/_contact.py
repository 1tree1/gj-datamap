from PIL import Image
import glob, os, re
d = r'C:\Users\OFFICE\Desktop\9_도시\work\20261005_ppt_refine\render_orig'
files = sorted(glob.glob(d + r'\*.PNG'), key=lambda p: int(re.findall(r'(\d+)\.PNG', p)[0]))
W, H = 640, 360
cols = 4
rows = (len(files) + cols - 1) // cols
def sheet(sub, name):
    r = (len(sub) + cols - 1) // cols
    img = Image.new('RGB', (cols * W, r * H), 'white')
    for i, f in enumerate(sub):
        im = Image.open(f).convert('RGB').resize((W, H))
        img.paste(im, ((i % cols) * W, (i // cols) * H))
    img.save(os.path.join(d, name))
sheet(files[:12], 'contact_1.png'); sheet(files[12:24], 'contact_2.png'); sheet(files[24:], 'contact_3.png')
print(len(files))
