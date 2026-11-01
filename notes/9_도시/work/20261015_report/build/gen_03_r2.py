# -*- coding: utf-8 -*-
# 03_analysis_r2.tpl.html -> chapters/03_analysis.html (그림·표 번호 자동 부여, 상호참조 치환)
import re, os, sys
B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(B)
src = open(os.path.join(B, '03_analysis_r2.tpl.html'), encoding='utf-8').read()
out = []; pos = 0; nf = nt = 0; ids = {}
for m in re.finditer(r'<(figure|table)\b[^>]*>', src):
    kind = m.group(1); tag = m.group(0)
    if kind == 'figure': nf += 1; n = nf; ph = '@@F@@'; lab = '그림 3-%d' % n
    else: nt += 1; n = nt; ph = '@@T@@'; lab = '표 3-%d' % n
    idm = re.search(r'id="([^"]+)"', tag)
    if idm: ids[idm.group(1)] = lab
    out.append((m.end(), ph, lab))
res = []; last = 0
for end, ph, lab in out:
    i = src.index(ph, end)
    res.append(src[last:i]); res.append(lab); last = i + len(ph)
res.append(src[last:]); s = ''.join(res)
def ref(m):
    k = m.group(1) + '-' + m.group(2)
    return ids[k]
s = re.sub(r'\{\{([ft]):([a-z0-9-]+)\}\}', ref, s)
assert '@@' not in s and '{{' not in s
open(os.path.join(R, 'chapters', '03_analysis.html'), 'w', encoding='utf-8').write(s)
print('figures', nf, 'tables', nt)
