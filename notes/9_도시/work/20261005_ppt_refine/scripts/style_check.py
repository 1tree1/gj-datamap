"""문체 점검: 슬라이드 본문(발표자 노트 제외)에서 합니다체가 아닌 '~다.' 종결과 v1 구어 표현이 남았는지 찾는다. 사용: style_check.py <pptx>"""
import re, sys
from pptx import Presentation
prs = Presentation(sys.argv[1])
BAD_WORDS = ["부른다", "만난다", "머문다", "퍼진다", "잇는다", "일한다", "산다", "남았다", "갈랐", "우리", "옛 역사", "쉬운 뜻", "잰 값", "북쪽", "가운데", "남쪽"]
PLAIN = re.compile(r"[가-힣](다|까)\s*[\.\)]*$")
hits = 0
def paras(sl):
    for sh in sl.shapes:
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs: yield "".join(r.text for r in p.runs).strip()
        if sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    for p in c.text_frame.paragraphs: yield "".join(r.text for r in p.runs).strip()
for i, sl in enumerate(prs.slides, 1):
    for t in paras(sl):
        if not t: continue
        if (PLAIN.search(t) and not re.search(r"(니다|입니다|합니다)\s*[\.\)]*$", t)) or any(w in t for w in BAD_WORDS):
            hits += 1; print("%02d | %s" % (i, t[:90]))
print("검출 %d건" % hits)
