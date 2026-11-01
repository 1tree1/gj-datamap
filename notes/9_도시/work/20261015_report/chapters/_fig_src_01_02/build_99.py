# -*- coding: utf-8 -*-
"""99 부록 조립: 템플릿의 @@SRCLIST@@ 를 _v1/99_appendix.html 의 번호 목록(<ol class="srclist">)으로 그대로 치환한다."""
import re, sys
B = 'C:/Users/OFFICE/Desktop/9_도시/work/20261015_report/chapters/'
old = open(B + '_v1/99_appendix.html', encoding='utf-8').read()
m = re.search(r'<ol class="srclist">.*?</ol>', old, re.S)
assert m, 'srclist not found'
ol = m.group(0)
tpl = open(B + '_fig_src_01_02/99_template.html', encoding='utf-8').read()
new = tpl.replace('@@SRCLIST@@', ol)
open(B + '99_appendix.html', 'w', encoding='utf-8').write(new)
# 검증: 번호 목록 블록이 원본과 바이트 단위로 같은가
chk = re.search(r'<ol class="srclist">.*?</ol>', open(B + '99_appendix.html', encoding='utf-8').read(), re.S).group(0)
print('srclist identical:', chk == ol, 'items:', ol.count('<li>'))
