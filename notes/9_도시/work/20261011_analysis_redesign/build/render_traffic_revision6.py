from pathlib import Path
import sys,json
B=Path(__file__).parent
sys.path.insert(0,r'C:\Users\OFFICE\AdobeMCP');import server_local as S
code=(B/'illustrator_maps.jsx').read_text(encoding='utf8').replace('/build/geometry.json','/build/traffic_revision6_geometry.json')
(B/'illustrator_traffic_revision6.jsx').write_text(code,encoding='utf8')
result=S.run_jsx_compatible('illustrator',code,timeout=240)
print(json.dumps(result,ensure_ascii=False))
if not result.get('success'):raise RuntimeError('Illustrator export failed')
