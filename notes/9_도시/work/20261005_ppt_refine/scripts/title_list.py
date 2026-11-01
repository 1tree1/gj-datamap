"""덱의 각 쪽 소제목(12pt 붉은 글)·제목(27pt/32pt)을 뽑아 문체 점검용 목록을 만든다. 사용: title_list.py <pptx>"""
import sys
from pptx import Presentation
from pptx.util import Pt
prs = Presentation(sys.argv[1])
for i, sl in enumerate(prs.slides, 1):
    lab, ttl = "", []
    for sh in sl.shapes:
        if not sh.has_text_frame: continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                sz = r.font.size.pt if r.font.size else 0
                if sz in (27.0, 32.0, 34.0) and r.text.strip(): ttl.append(r.text.strip())
                elif sz == 12.0 and r.font.color and r.font.color.type is not None and str(r.font.color.rgb) == "D7191C" and r.text.strip() and not lab: lab = r.text.strip()
    print("%02d | %-24s | %s" % (i, lab, " / ".join(ttl)))
