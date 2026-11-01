import zipfile,json
from pathlib import Path
B=Path(__file__).parent;P=B/'merged_candidate.pptx'
parts=json.loads((B/'source_palette_receipt.json').read_text(encoding='utf8'))['parts']
with zipfile.ZipFile(P) as z:files={n:z.read(n) for n in z.namelist()}
for i,n in enumerate(parts):files[n]=(B/'source_palette'/('recolored_'+str(i)+Path(n).suffix)).read_bytes()
with zipfile.ZipFile(P,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in files.items():z.writestr(n,v)
print('Restored verified Photoshop palette:',len(parts),'assets')
