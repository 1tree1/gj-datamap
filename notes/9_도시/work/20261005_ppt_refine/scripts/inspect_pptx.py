"""원본 PPTX 구조 덤프 — 슬라이드별 도형·글·그림·표(재귀). 출력은 stdout."""
import sys
from pptx import Presentation
from pptx.util import Emu
from pptx.enum.shapes import MSO_SHAPE_TYPE

p = Presentation(sys.argv[1])
print("slide size: %.1f x %.1f mm (%.3f x %.3f in)  layouts: %s" % (p.slide_width / 36000, p.slide_height / 36000, p.slide_width / 914400, p.slide_height / 914400, [l.name for l in p.slide_layouts][:12]))
def dump(sh, ind=0):
    pad = "  " * ind
    t = sh.shape_type
    pos = "(%.0f,%.0f %.0fx%.0f mm)" % (sh.left / 36000 if sh.left is not None else -1, sh.top / 36000 if sh.top is not None else -1, sh.width / 36000 if sh.width is not None else -1, sh.height / 36000 if sh.height is not None else -1)
    line = "%s- [%s] %s %s" % (pad, str(t).split(".")[-1] if t else "?", sh.name, pos)
    if sh.is_placeholder:
        line += " PH:%s" % sh.placeholder_format.type
    print(line)
    if t == MSO_SHAPE_TYPE.GROUP:
        for s in sh.shapes: dump(s, ind + 1)
        return
    if sh.has_text_frame and sh.text_frame.text.strip():
        for para in sh.text_frame.paragraphs:
            tx = "".join(r.text for r in para.runs)
            if not tx.strip(): continue
            sizes = sorted({(r.font.size.pt if r.font.size else None) for r in para.runs}, key=lambda v: (v is None, v))
            fonts = sorted({r.font.name for r in para.runs if r.font.name})
            print("%s    | %s   {%s %s b=%s}" % (pad, tx.replace("\n", " / "), sizes, fonts, any(r.font.bold for r in para.runs)))
    if getattr(sh, "has_table", False) and sh.has_table:
        tb = sh.table
        for r in tb.rows:
            print("%s    ┃ %s" % (pad, " ┃ ".join(c.text.replace("\n", " / ") for c in r.cells)))
    if t == MSO_SHAPE_TYPE.PICTURE:
        try: print("%s    img: %s %dx%d px %s" % (pad, sh.image.content_type, sh.image.size[0], sh.image.size[1], sh.image.filename))
        except Exception as e: print(pad, "img?", e)

for i, s in enumerate(p.slides, 1):
    print("\n=== 슬라이드 %d  (layout: %s) ===" % (i, s.slide_layout.name))
    for sh in s.shapes: dump(sh)
    if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip(): print("  NOTES:", s.notes_slide.notes_text_frame.text.strip()[:400])
