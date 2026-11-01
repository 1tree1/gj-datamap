import sys,json,re,tempfile
from pathlib import Path
sys.path.insert(0,r'C:\Users\OFFICE\AdobeMCP');import server_local as S
B=Path(__file__).parent
code=(B/'illustrator_maps.jsx').read_text(encoding='utf8')
source_name=sys.argv[1] if len(sys.argv)>1 else 'population_geometry.json'
payload=json.dumps(json.loads((B/source_name).read_text(encoding='utf8')),ensure_ascii=True)
source=Path(tempfile.gettempdir())/'codex_population_geometry.json';source.write_text(payload,encoding='ascii')
code=re.sub(r"var f=new File\(.*?f.close\(\);",lambda m:'var f=new File('+json.dumps(str(source).replace('\\','/'))+');if(!f.open("r"))throw new Error(f.error);var txt=f.read();f.close();var maps=eval("("+txt+")");',code)
r=S.run_jsx_compatible('illustrator',code,timeout=120);print(json.dumps(r,ensure_ascii=False))
if not r.get('success'):raise RuntimeError(r)
