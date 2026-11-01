"""본문 서체별 첫 줄 기준선(baseline) 위치 측정: 글상자 윗선(y0)에서 'H' 아랫선까지 몇 pt 인가. → pptkit_r.BL 표에 넣는다."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptkit_r import *
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CD = os.path.join(ROOT, "calib")
S = 3.36
CASES = [("kl9_13", dict(font="kl", size=9, line=13)), ("kl9_none", dict(font="kl", size=9)), ("kr9_13", dict(font="kr", size=9, line=13)),
         ("ksb12", dict(font="ksb", size=12)), ("kb12", dict(font="kb", size=12)), ("enb12", dict(font="enb", size=12)), ("en9", dict(font="en", size=9)),
         ("kl8.41", dict(font="kl", size=8.41)), ("en14", dict(font="en", size=14)), ("kr14", dict(font="kr", size=14)), ("kb14", dict(font="kb", size=14)),
         ("kl11", dict(font="kl", size=11)), ("kl12", dict(font="kl", size=12)), ("enb20", dict(font="enb", size=20)), ("kb20", dict(font="kb", size=20)),
         ("enb18", dict(font="enb", size=18)), ("kl9_14", dict(font="kl", size=9, line=14)), ("kl9_12", dict(font="kl", size=9, line=12)),
         ("en12.18", dict(font="en", size=12.18)), ("kb35", dict(font="mgb", size=35)), ("en20", dict(font="en", size=20)), ("kl7.5", dict(font="kl", size=7.5)),
         ("kl10_14", dict(font="kl", size=10, line=14)), ("kl10.5_15", dict(font="kl", size=10.5, line=15)), ("kb11", dict(font="kb", size=11)), ("kr10", dict(font="kr", size=10))]

def build():
    d = Deck(); s = d.slide()
    for i, (nm, st) in enumerate(CASES):
        col, row = i % 5, i // 5
        x = 60 + col * 220; y = 80 + row * 120
        line_ = 0.0
        tb(s, x, y, 200, 60, "HHHH xHxH", color="#000000", **st)
        line(s, x - 10, y, x + 200, y, color="#FF0000", lw=0.25)
    d.save(os.path.join(CD, "calib2.pptx")); print("saved")

def measure():
    from PIL import Image
    im = Image.open(os.path.join(CD, "슬라이드1.PNG")).convert("RGB"); sc = im.width / PW
    A = np.asarray(im).astype(int)
    out = {}
    for i, (nm, st) in enumerate(CASES):
        col, row = i % 5, i // 5
        x = 60 + col * 220; y = 80 + row * 120
        x0, x1, y0, y1 = int(x * sc), int((x + 60) * sc), int((y + 1) * sc), int((y + 55) * sc)      # 'HHHH' 부분만, 빨간 줄(y) 아래
        reg = A[y0:y1, x0:x1]
        dark = (reg.max(axis=2) < 120)
        rows = np.where(dark.any(axis=1))[0]
        if len(rows) == 0: print(nm, "no ink"); continue
        top = (y0 + rows.min()) / sc; bot = (y0 + rows.max() + 1) / sc
        # 'H' 높이: 첫 줄 띠만(연속 구간)
        bandend = rows[0]
        for r in rows[1:]:
            if r - bandend > 2: break
            bandend = r
        top = (y0 + rows[0]) / sc; bot = (y0 + bandend + 1) / sc
        out[nm] = (round(top - y, 2), round(bot - y, 2))
        print("%-12s 'H' 윗선 +%.2f pt  아랫선(기준선) +%.2f pt  (높이 %.2f)" % (nm, top - y, bot - y, bot - top))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "build": build()
    else: measure()
