"""보고서의 KoPub돋움(PM 15.5pt 제목)을 PDF에서 그대로 뽑아, 설치된 한글 서체 후보와 같은 크기로 나란히 놓는다."""
import sys, os
import pymupdf
from PIL import Image, ImageDraw, ImageFont
PDF = r"C:\Users\OFFICE\Desktop\9_도시\2_Report_HR_통영조선소.pdf"
OUT = sys.argv[1]
DPI = 500
doc = pymupdf.open(PDF)
# 한글 제목(KoPubDotumPM)이 있는 쪽·글자 찾기
cands = []
for pn in range(len(doc)):
    for b in doc[pn].get_text("dict")["blocks"]:
        if b.get("type") != 0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                if "KoPubDotumPM" in s["font"] and len(s["text"].strip()) >= 8 and abs(s["size"] - 15.5) < 0.3:
                    cands.append((pn, s))
print(len(cands), [(c[0] + 1, c[1]["text"]) for c in cands[:8]])
pn, s = cands[0]
x0, y0, x1, y1 = s["bbox"]; txt = s["text"].strip()
z = DPI / 72.0
clip = pymupdf.Rect(x0 - 4, y0 - 6, x1 + 40, y1 + 6)
pix = doc[pn].get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip, alpha=False)
ref = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
print("ref", ref.size, txt, "PDF bbox w=%.2f pt h=%.2f pt" % (x1 - x0, y1 - y0))
px = 15.5 * DPI / 72.0
FONTS = [("Noto Sans KR Medium(VF)", r"C:\Windows\Fonts\NotoSansKR-VF.ttf", "Medium"), ("Noto Sans KR DemiLight→Regular(VF)", r"C:\Windows\Fonts\NotoSansKR-VF.ttf", "Regular"),
         ("Pretendard Medium", os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts\Pretendard-Medium.otf"), None),
         ("Pretendard Regular", os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts\Pretendard-Regular.otf"), None),
         ("맑은 고딕", r"C:\Windows\Fonts\malgun.ttf", None), ("맑은 고딕 Semilight", r"C:\Windows\Fonts\malgunsl.ttf", None),
         ("NanumGothic", r"C:\Windows\Fonts\NanumGothic.ttf", None), ("Hancom Gothic", r"C:\Windows\Fonts\Hancom Gothic Regular.ttf", None)]
rows = [("PDF: KoPubDotumPM 15.5pt #6D6E71", ref)]
for nm, path, var in FONTS:
    try:
        f = ImageFont.truetype(path, int(round(px)))
        if var:
            try: f.set_variation_by_name(var)
            except Exception as e: print("variation fail", nm, e)
        im = Image.new("RGB", ref.size, "white"); d = ImageDraw.Draw(im)
        d.text((4 * z, 6 * z - px * 0.12), txt, font=f, fill="#6D6E71")
        rows.append((nm, im))
    except Exception as e:
        print("fail", nm, e)
H = sum(r[1].height + 34 for r in rows); W = max(r[1].width for r in rows)
sheet = Image.new("RGB", (W, H), "white"); dd = ImageDraw.Draw(sheet); y = 0
lab = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 24)
for nm, im in rows:
    dd.text((6, y + 2), nm, font=lab, fill="#c00000"); y += 30; sheet.paste(im, (0, y)); y += im.height + 4
sheet.save(OUT); print("saved", OUT, sheet.size)
