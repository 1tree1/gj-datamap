"""원본 PPTX 텍스트만 슬라이드별로 압축 덤프(그룹 재귀). 사용: dump_text.py file.pptx > out.txt"""
import sys
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
p = Presentation(sys.argv[1])
def walk(shapes, out, stats):
    for sh in shapes:
        stats["shapes"] += 1
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP: walk(sh.shapes, out, stats); continue
        if sh.shape_type == MSO_SHAPE_TYPE.PICTURE: stats["pics"] += 1
        if getattr(sh, "has_table", False) and sh.has_table:
            stats["tables"] += 1
            for r in sh.table.rows: out.append("   ┃ " + " ┃ ".join(c.text.replace("\n", " / ") for c in r.cells))
        if sh.has_text_frame:
            for para in sh.text_frame.paragraphs:
                tx = "".join(r.text for r in para.runs).strip()
                if tx: out.append(tx)
for i, s in enumerate(p.slides, 1):
    out, stats = [], dict(shapes=0, pics=0, tables=0)
    walk(s.shapes, out, stats)
    print("\n=== 슬라이드 %d  (도형 %d, 그림 %d, 표 %d) ===" % (i, stats["shapes"], stats["pics"], stats["tables"]))
    for t in out: print(t)
