from pptx import Presentation
p = Presentation(r'C:\Users\OFFICE\Desktop\9_도시\work\20261005_ppt_refine\5주차_과제_다듬기v1.pptx')
fonts = set(); sizes = set(); n_notes = 0
from pptx.util import Pt
for s in p.slides:
    if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip(): n_notes += 1
    for sh in s.shapes:
        if sh.has_text_frame:
            for para in sh.text_frame.paragraphs:
                for r in para.runs:
                    fonts.add(r.font.name); sizes.add(r.font.size.pt if r.font.size else None)
print('slides', len(p.slides), 'notes', n_notes, 'fonts', fonts)
print('sizes', sorted(x for x in sizes if x))
