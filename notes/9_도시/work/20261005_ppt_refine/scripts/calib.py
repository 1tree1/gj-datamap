"""헤더 보정: 보고서 p.6 의 헤더 글(라벨·제목·쪽번호)과 같은 문자열로 시험 슬라이드를 만들고, PowerPoint 렌더를 PDF 렌더와 겹쳐 오프셋을 잰다.
사용: calib.py build  → work/.../calib/test.pptx 생성 / calib.py measure → 두 렌더의 잉크 띠 위치 비교"""
import os, sys, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptkit_r import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CD = os.path.join(ROOT, "calib"); os.makedirs(CD, exist_ok=True)
PDF = r"C:\Users\OFFICE\Desktop\9_도시\2_Report_HR_통영조선소.pdf"
S = 3.36                                       # px per pt (4000 px 폭)

def build():
    d = Deck(); s = d.slide()
    header(s, "Executive Summary", "A Global Model for Integrated Sustainable Regeneration")
    tb(s, ML, Y_PAGE + DY["page"], 60, 18, "4", size=11, color=INK, font="en")
    s2 = d.slide()
    header(s2, "Masterplan : Epilogue", "A New Legacy:  A Tourism + Cultural Hub", sub="A Global Attraction Celebrating Tongyeong’s Culture + History")
    tb(s2, ML, Y_PAGE + DY["page"], 60, 18, "46", size=11, color=INK, font="en")
    s3 = d.slide()
    header(s3, "개요 : 구역 구성", "남북 3개 구역의 기능 구성", sub="근로·정주 거점 / 교류·창작 거점 / 방문 관문")
    tb(s3, ML, Y_PAGE + DY["page"], 60, 18, "4", size=11, color=INK, font="en")
    s4 = d.slide()
    page_footer(s4, 39, style="right")
    s5 = d.slide()
    page_footer(s5, 4, style="left")
    d.save(os.path.join(CD, "test.pptx")); print("saved test.pptx")

def bands(a, thr=140):
    ink = (a < thr).any(axis=1); out = []; s = None
    for i, v in enumerate(ink):
        if v and s is None: s = i
        if (not v) and s is not None: out.append((s, i - 1)); s = None
    if s is not None: out.append((s, len(ink) - 1))
    return out

def measure():
    import pymupdf
    from PIL import Image
    doc = pymupdf.open(PDF)
    for pdfp, pp in ((6, 1), (52, 2)):
        pg = doc[pdfp - 1]
        pix = pg.get_pixmap(matrix=pymupdf.Matrix(S, S), clip=pymupdf.Rect(0, 20, 760, 130), alpha=False)
        A = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).min(axis=2)
        im = Image.open(os.path.join(CD, "슬라이드%d.PNG" % pp)).convert("RGB"); sc = im.width / PW
        crop = im.crop((0, int(20 * sc), int(760 * sc), int(130 * sc))).resize((pix.width, pix.height))
        B = np.asarray(crop).min(axis=2)
        print("== p.%d  PDF 대 PPT (띠 상·하단, pt, 슬라이드 y 기준)" % pdfp)
        for nm, Z in (("PDF", A), ("PPT", B)):
            bb = bands(Z)
            cols = np.where((Z < 140).any(axis=0))[0]
            print("  %s 띠:" % nm, [(round(20 + a / S, 2), round(20 + b / S, 2)) for a, b in bb], " 왼쪽 잉크 x=%.2f pt" % (cols.min() / S))
    # 아래쪽: 오른쪽 쪽(p.45 = 39쪽) 푸터·쪽번호 / 왼쪽 쪽(p.6 = 4쪽) 쪽번호
    for pdfp, pp, nm in ((45, 4, "오른쪽 쪽"), (6, 5, "왼쪽 쪽")):
        pg = doc[pdfp - 1]
        # 사진 위(p.45) 푸터는 밝은 배경이 아니므로 흰 배경인 쪽(p.33=27쪽, 쪽번호 11pt + 푸터 8.41pt)으로 비교
        if pdfp == 45: pdfp = 33
        pg = doc[pdfp - 1]
        r = pymupdf.Rect(0, 795, PW, 835)
        pix = pg.get_pixmap(matrix=pymupdf.Matrix(S, S), clip=r, alpha=False)
        A = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).min(axis=2)
        im = Image.open(os.path.join(CD, "슬라이드%d.PNG" % pp)).convert("RGB"); sc = im.width / PW
        B = np.asarray(im.crop((0, int(795 * sc), int(PW * sc), int(835 * sc))).resize((pix.width, pix.height))).min(axis=2)
        print("== 아래쪽 %s (PDF p.%d)" % (nm, pdfp))
        for n2, Z in (("PDF", A), ("PPT", B)):
            ink = Z < 175
            cols = np.where(ink.any(axis=0))[0]
            # 가로로 두 덩어리(푸터 / 쪽번호)로 나눈다
            groups = []; s0 = cols[0]; p0 = cols[0]
            for c in cols[1:]:
                if c - p0 > 4.5 * S: groups.append((s0, p0)); s0 = c
                p0 = c
            groups.append((s0, p0))
            out = []
            for g0, g1 in groups:
                rows = np.where(ink[:, g0:g1 + 1].any(axis=1))[0]
                out.append(("x %.1f–%.1f" % (g0 / S, g1 / S), "y %.2f–%.2f" % (795 + rows.min() / S, 795 + rows.max() / S)))
            print("  %s:" % n2, out)

if __name__ == "__main__":
    if sys.argv[1] == "build": build()
    else: measure()
