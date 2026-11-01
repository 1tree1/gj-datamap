# -*- coding: utf-8 -*-
"""라이노 캡처 후처리 — 적색 계열만 남기고 나머지는 무채색으로, 배경 투명부는 흰색. sheets/render/*.png + crop.json → assets/renders/*.png"""
import json, numpy as np
from PIL import Image
SH = r'C:/Users/OFFICE/Desktop/9_도시/work/20261011_masterplan_v1/sheets/render'; OUT = r'C:/Users/OFFICE/Desktop/9_도시/work/20261011_final_deck/assets/renders'
info = json.load(open(SH + '/crop.json'))
for k, v in info.items():
    im = Image.open(v['path']).convert('RGBA'); bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); im = Image.alpha_composite(bg, im).convert('RGB')
    x0, y0, x1, y1 = v['crop']; m = 30
    im = im.crop((max(0, int(x0 - m)), max(0, int(y0 - m)), min(im.width, int(x1 + m)), min(im.height, int(y1 + m))))
    a = np.asarray(im).astype(np.float32); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(axis=2); mn = a.min(axis=2); sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    red = (r > g + 25) & (r > b + 25) & (sat > 0.25)
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    gray = np.clip((gray - 128) * 1.06 + 128 + 6, 0, 255)          # 약한 대비·밝기 보정
    out = np.stack([gray, gray, gray], axis=2); out[red] = a[red]
    Image.fromarray(out.astype(np.uint8)).save(f'{OUT}/{k}.png'); print(k, im.size, 'red px %.2f%%' % (red.mean() * 100))
