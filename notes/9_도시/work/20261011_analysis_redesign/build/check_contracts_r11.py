from pathlib import Path
import sys,json
sys.path.insert(0,r'C:/Users/OFFICE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations/container_tools')
from native_table_arithmetic_gate import audit_native_table_arithmetic
B=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build')
for c in json.loads((B/'revision11_requirements.json').read_text('utf8'))['contracts']:
 try:
  r=audit_native_table_arithmetic(B/'revision11_full_candidate.pptx',contracts=[c]);print(c['slide'],r['passed'])
 except Exception as e:print(c['slide'],type(e).__name__,str(e))
