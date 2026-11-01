import json, pathlib, fitz
ROOT=pathlib.Path(r'C:\Users\OFFICE\Desktop\9_도시\work\20261010_nexus_front\build')
manifest=json.loads((ROOT/'source_manifest.json').read_text(encoding='utf-8-sig'))
paths={r['id']:r['path'] for r in manifest}
out=ROOT/'assets'; out.mkdir(exist_ok=True)
for sid,pages in {'s09':[11,12,13],'s06':[8,22,26]}.items():
    doc=fitz.open(paths[sid])
    for p in pages:
        pg=doc[p-1]
        pg.get_pixmap(matrix=fitz.Matrix(2,2)).save(str(out/f'{sid}_{p:02}.png'))
print('source pages rendered')
doc=fitz.open(paths['s09'])
for p,name in [(11,'wanggyeong'),(12,'eupseong')]:
    page=doc[p-1]
    candidates=[]
    for item in page.get_images():
        for r in page.get_image_rects(item[0]):
            if r.width<600 and r.height>300 and item[2]>400:
                candidates.append((r.width*r.height,item[0]))
    if candidates:
        ref=max(candidates)[1]
        fitz.Pixmap(doc,ref).save(str(out/f'{name}.png'))
        print('embedded source diagram',p,ref)
