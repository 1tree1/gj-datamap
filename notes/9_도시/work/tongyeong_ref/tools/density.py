"""쪽별 시각 밀도 통계 (PyMuPDF만 사용).
- ink: 저해상도 렌더에서 '흰색이 아닌' 픽셀 비율 (전면 이미지 ≈ 0.9+, 텍스트쪽 ≈ 0.1~0.3)
- img_cover: 배치된 래스터 이미지 bbox 합집합 근사 비율 (격자 샘플링)
- n_img: 배치된 래스터 이미지 개수
- live_text: 임베디드(살아 있는) 텍스트 글자 수
"""
import pymupdf, os, csv, io

SRC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))  # 프로젝트 루트(원본 PDF 위치)
SP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_render"))  # 렌더·크롭 출력 폴더(필요할 때 생성)
jobs = [("2_Report_HR_통영조선소.pdf", "rep"), ("3_Presentation_통영조선소.pdf", "ppt")]
for fn, tag in jobs:
    d = pymupdf.open(os.path.join(SRC, fn))
    rows = []
    for i, p in enumerate(d, start=1):
        R = p.rect
        # ink 비율
        z = 0.12
        pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
        s = pix.samples
        n = pix.width * pix.height
        nonwhite = 0
        for k in range(0, len(s), 3):
            if min(s[k], s[k + 1], s[k + 2]) < 235:
                nonwhite += 1
        ink = nonwhite / n
        # 이미지 점유율 (20x14 격자 샘플)
        infos = p.get_image_info()
        boxes = [pymupdf.Rect(x["bbox"]) & R for x in infos]
        boxes = [b for b in boxes if not b.is_empty and b.width > 20 and b.height > 20]
        gx, gy = 40, 28
        hit = 0
        for a in range(gx):
            for b_ in range(gy):
                pt = pymupdf.Point(R.x0 + R.width * (a + 0.5) / gx, R.y0 + R.height * (b_ + 0.5) / gy)
                if any(bb.contains(pt) for bb in boxes):
                    hit += 1
        img_cover = hit / (gx * gy)
        live = len(p.get_text().strip())
        rows.append((i, round(ink, 3), round(img_cover, 3), len(boxes), live))
    out = os.path.join(SP, "txt", f"{tag}_density.csv")
    with io.open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["page", "ink", "img_cover", "n_img", "live_text_chars"])
        w.writerows(rows)
    print(tag, "done", len(rows))
