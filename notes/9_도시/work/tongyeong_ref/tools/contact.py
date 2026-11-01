"""렌더링된 페이지 JPEG로 컨택트시트를 만든다 (PyMuPDF만 사용).
사용: python contact.py rep|ppt  cols rows  [sheet_width]
출력: sheets_rep/sheet_01.jpg ...  (페이지 번호 라벨 포함)
"""
import pymupdf, os, sys, glob, math

SP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_render"))  # 렌더·크롭 출력 폴더(필요할 때 생성)
tag = sys.argv[1]
cols = int(sys.argv[2]); rows = int(sys.argv[3])
SW = int(sys.argv[4]) if len(sys.argv) > 4 else 1800
prefix = "p" if tag == "rep" else "s"
files = sorted(glob.glob(os.path.join(SP, tag, f"{prefix}*.jpg")))
out_dir = os.path.join(SP, f"sheets_{tag}")
os.makedirs(out_dir, exist_ok=True)

GAP = 10
cell_w = (SW - GAP * (cols + 1)) // cols
# 셀 비율은 첫 페이지가 아니라 대표 비율(보고서 1191x842, ppt 960x540)로 고정
ratio = 842 / 1191 if tag == "rep" else 540 / 960
cell_h = int(cell_w * ratio)
LABEL = 22
per = cols * rows
n_sheets = math.ceil(len(files) / per)
SH = GAP + rows * (cell_h + LABEL + GAP)

for s in range(n_sheets):
    doc = pymupdf.open()
    page = doc.new_page(width=SW, height=SH)
    page.draw_rect(page.rect, color=None, fill=(0.92, 0.92, 0.92))
    chunk = files[s * per:(s + 1) * per]
    for k, f in enumerate(chunk):
        r, c = divmod(k, cols)
        x0 = GAP + c * (cell_w + GAP)
        y0 = GAP + r * (cell_h + LABEL + GAP)
        pn = int(os.path.basename(f)[1:4])
        page.insert_text((x0 + 2, y0 + 16), f"{tag} p.{pn}", fontsize=15, color=(0.7, 0, 0))
        # 비율 유지 박스 맞춤 (표지처럼 비율이 다른 페이지 대응)
        pm = pymupdf.Pixmap(f)
        ar = pm.width / pm.height
        bw, bh = cell_w, cell_h
        if ar > bw / bh:
            w, h = bw, bw / ar
        else:
            h, w = bh, bh * ar
        rect = pymupdf.Rect(x0, y0 + LABEL, x0 + w, y0 + LABEL + h)
        page.insert_image(rect, filename=f)
    pix = page.get_pixmap(alpha=False)
    out = os.path.join(out_dir, f"sheet_{s+1:02d}.jpg")
    pix.save(out, jpg_quality=82)
    print(out, chunk[0][-8:], "..", chunk[-1][-8:])
