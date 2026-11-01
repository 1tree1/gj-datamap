from pathlib import Path
from pypdf import PdfReader
import sys
sys.stdout.reconfigure(encoding='utf8')
p=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/output/구경주역_중간마감_v11_계획인구와규모.pdf')
r=PdfReader(p);print(repr(r.pages[55].extract_text())[:4000])
