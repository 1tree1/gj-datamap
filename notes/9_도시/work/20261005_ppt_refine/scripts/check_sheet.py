"""render_new 의 슬라이드 PNG 중 지정한 번호만 모아 한 장으로. 사용: check_sheet.py out.png 17,22,27 [cols] [width]"""
import sys, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = os.path.join(ROOT, "render_new")
out = sys.argv[1]; nums = [int(x) for x in sys.argv[2].split(",")]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 2; W = int(sys.argv[4]) if len(sys.argv) > 4 else 1000; H = int(W * 9 / 16)
r = (len(nums) + cols - 1) // cols
img = Image.new("RGB", (cols * W, r * H), "white")
for i, n in enumerate(nums):
    p = os.path.join(d, "슬라이드%d.PNG" % n)
    im = Image.open(p).convert("RGB").resize((W, H)); img.paste(im, ((i % cols) * W, (i // cols) * H))
img.save(os.path.join(d, out)); print(img.size)
