import re
p = "pptkit_front.py"
src = open(p, encoding="utf-8").read().split("\n")
out = []
done_def = False
for ln in src:
    if ln.startswith("from pptx.util import"):
        out.append(ln)
        continue
    ln2 = re.sub(r"(?<![A-Za-z_])Inches\(", "_I(", ln)
    ln2 = re.sub(r"(?<![A-Za-z_])Pt\(", "_P(", ln2)
    out.append(ln2)
txt = "\n".join(out)
# 정의 삽입: 'from PIL import Image' 다음 줄
marker = "from PIL import Image\n"
defs = marker + '''
# 설계 단위는 A4 가로(11.693×8.268in) 기준이고, 실제 슬라이드는 A3 가로(×√2)로 만든다.
# 좌표·치수·글자 크기·선 굵기를 모두 같은 비율로 키우므로 배치는 그대로이고, 글자는 CLAUDE.md §11(본문 10.5–12pt, 제목 약 27pt)에 가까워진다.
K = 2 ** 0.5
def _I(v): return Inches(v * K)
def _P(v): return Pt(v * K)
'''
assert marker in txt
txt = txt.replace(marker, defs, 1)
open(p, "w", encoding="utf-8").write(txt)
print("converted", txt.count("_I("), txt.count("_P("))
