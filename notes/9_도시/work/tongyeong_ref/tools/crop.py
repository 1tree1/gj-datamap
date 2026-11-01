"""원본 PDF의 한 페이지에서 일부 영역만 고해상도로 잘라낸다 (세부 글씨·다이어그램 판독용).
사용: python crop.py rep|ppt  page  x0 y0 x1 y1  [zoom]  [out.jpg]
  x0..y1 은 0~1 사이의 비율 좌표 (왼쪽 위가 0,0). 예: 0 0 0.5 0.5 = 좌상단 1/4
  zoom 기본 3.0 / 출력 기본 crops/{tag}_p{page}_{x0}_{y0}.jpg
"""
import pymupdf, os, sys

SRC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))  # 프로젝트 루트(원본 PDF 위치)
SP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_render"))  # 렌더·크롭 출력 폴더(필요할 때 생성)
fn = {"rep": "2_Report_HR_통영조선소.pdf", "ppt": "3_Presentation_통영조선소.pdf"}[sys.argv[1]]
pg = int(sys.argv[2])
x0, y0, x1, y1 = [float(v) for v in sys.argv[3:7]]
zoom = float(sys.argv[7]) if len(sys.argv) > 7 else 3.0
out = sys.argv[8] if len(sys.argv) > 8 else None
d = pymupdf.open(os.path.join(SRC, fn))
p = d[pg - 1]
R = p.rect
clip = pymupdf.Rect(R.x0 + R.width * x0, R.y0 + R.height * y0, R.x0 + R.width * x1, R.y0 + R.height * y1)
pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip, alpha=False)
os.makedirs(os.path.join(SP, "crops"), exist_ok=True)
if not out:
    out = os.path.join(SP, "crops", f"{sys.argv[1]}_p{pg:03d}_{int(x0*100)}_{int(y0*100)}.jpg")
pix.save(out, jpg_quality=88)
print(out, pix.width, "x", pix.height)
