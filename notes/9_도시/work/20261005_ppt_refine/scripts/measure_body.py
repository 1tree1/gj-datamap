"""보고서 본문(래스터/외곽선 글자)의 크기·색을 픽셀로 잰다. p.6(영문 단락·국문 단락), 한글 제목(KoPub PM 15.5pt)으로 비율을 보정한다."""
import numpy as np
import pymupdf
from PIL import Image
PDF = r"C:\Users\OFFICE\Desktop\9_도시\2_Report_HR_통영조선소.pdf"
DPI = 600; z = DPI / 72.0
doc = pymupdf.open(PDF); pg = doc[5]            # p.6 (인쇄 4쪽)

def crop(x0, y0, x1, y1):
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x0, y0, x1, y1), alpha=False)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)

def bands(a, thr=200, min_gap=2):
    g = a.min(axis=2)                              # 가장 어두운 채널
    ink = (g < thr).sum(axis=1) > 0
    out = []; s = None
    for i, v in enumerate(ink):
        if v and s is None: s = i
        if (not v) and s is not None: out.append((s, i - 1)); s = None
    if s is not None: out.append((s, len(ink) - 1))
    return out

def darkest(a, pct=0.5):
    g = a.reshape(-1, 3).astype(int); lum = g.sum(axis=1)
    idx = np.argsort(lum)[: max(5, int(len(lum) * pct / 100))]
    return g[idx].mean(axis=0).round(0), g[idx[0]]

# 1) 한글 제목 보정: 글자 span 위치를 PDF에서 읽는다
d = pg.get_text("dict"); kt = None
for b in d["blocks"]:
    if b.get("type") != 0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if "KoPubDotumPM" in s["font"] and "도시재생" in s["text"]: kt = s
x0, y0, x1, y1 = kt["bbox"]; a = crop(x0, y0 - 2, x1, y1 + 2)
bb = bands(a); print("한글 제목 15.5pt: 잉크 띠(px)", bb, "높이", [b - a_ + 1 for a_, b in bb], " → 높이/크기(px/pt) =", [(b - a_ + 1) / (15.5 * z) for a_, b in bb])
ko_ratio = max((b - a_ + 1) for a_, b in bb) / (15.5 * z)

# 2) p.6 영문 첫 단락(좌 첫 단 상단): 100dpi 좌표 78–422 x, 211–340 y → pt = px*0.72
ea = crop(78 * 0.72, 205 * 0.72, 422 * 0.72, 345 * 0.72)
eb = bands(ea); hs = [b - a_ + 1 for a_, b in eb]
print("영문 단락 줄 수", len(eb), "띠 높이(px) 중앙값", np.median(hs), "줄 피치(pt)", np.median(np.diff([a_ for a_, b in eb])) / z)
print("영문 본문 색 가장 어두운 0.5%:", darkest(ea))
# Arial: 어센더~디센더 높이 ≈ 0.94 em
print("  영문 크기 추정(pt) ≈", np.median(hs) / z / 0.94)

# 3) p.6 국문 첫 단락(좌 첫 단 하단): 100dpi y 585–790
ka = crop(78 * 0.72, 583 * 0.72, 422 * 0.72, 800 * 0.72)
kb = bands(ka); hk = [b - a_ + 1 for a_, b in kb]
print("국문 단락 줄 수", len(kb), "띠 높이(px) 중앙값", np.median(hk), "줄 피치(pt)", np.median(np.diff([a_ for a_, b in kb])) / z)
print("국문 본문 색 가장 어두운 0.5%:", darkest(ka))
print("  국문 크기 추정(pt) ≈", np.median(hk) / z / ko_ratio, "(보정비 %.3f)" % ko_ratio)

# 4) 소제목(Arial Bold) 'Holistic Planning' 위치의 크기 — PDF 글자에서 직접
for b in d["blocks"]:
    if b.get("type") != 0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if s["text"].strip() in ("Holistic Planning", "Connectivity", "Placemaking"): print("소제목 span", s["font"], round(s["size"], 2), "#%06X" % s["color"], s["text"])
print("본문 영문 span 존재 여부(살아 있는 글자):", sum(1 for b in d["blocks"] if b.get("type") == 0 for l in b["lines"] for s in l["spans"] if s["size"] < 10 and len(s["text"]) > 30))
