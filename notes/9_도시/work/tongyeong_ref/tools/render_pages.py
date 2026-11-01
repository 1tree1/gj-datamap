"""PDF 두 개를 페이지별 JPEG로 렌더링한다 (PyMuPDF만 사용, Pillow 불필요).
rep/p001.jpg ... : 보고서 59쪽 (A3 가로, zoom 1.3 → 약 1548x1095)
ppt/s001.jpg ... : 발표자료 89쪽 (16:9, zoom 1.6 → 약 1536x864, 1쪽은 A4 세로 표지)
"""
import pymupdf, os, sys, time

SRC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))  # 프로젝트 루트(원본 PDF 위치)
SP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_render"))  # 렌더·크롭 출력 폴더(필요할 때 생성)
jobs = [
    ("2_Report_HR_통영조선소.pdf", "rep", "p", 1.3),
    ("3_Presentation_통영조선소.pdf", "ppt", "s", 1.6),
]
only = sys.argv[1] if len(sys.argv) > 1 else None
for fn, tag, prefix, zoom in jobs:
    if only and only != tag:
        continue
    out_dir = os.path.join(SP, tag)
    os.makedirs(out_dir, exist_ok=True)
    d = pymupdf.open(os.path.join(SRC, fn))
    t0 = time.time()
    for i, p in enumerate(d, start=1):
        path = os.path.join(out_dir, f"{prefix}{i:03d}.jpg")
        if os.path.exists(path):
            continue
        pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        pix.save(path, jpg_quality=85)
        if i % 10 == 0:
            print(tag, i, f"{time.time()-t0:.0f}s", flush=True)
    print(tag, "done", d.page_count, f"{time.time()-t0:.0f}s", flush=True)
