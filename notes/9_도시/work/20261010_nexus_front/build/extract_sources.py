from pathlib import Path
import fitz, json
root=Path(r'C:\Users\OFFICE\Desktop\9_도시')
build=root/'work/20261010_nexus_front/build'
build.mkdir(parents=True,exist_ok=True)
out=build/'sources'; out.mkdir(exist_ok=True)
ref=Path(r'C:\Users\OFFICE\Documents\카카오톡 받은 파일\XCZCZCXCZCZ.pdf')
files=[ref]
names=['2030 경주도시기본계획.pdf','#경주시 원도심 미래구상 기획 연구 0804 최종본.pdf','04 김권일 학예연구실장_발표자료 (구경주역 매장유산 현황 및 도시재생 관련 제언).pdf','22-0124) 경주시 도시재생전략계획 최종보고서.pdf']
for name in names:
    files.extend(root.rglob(name))
for p in root.rglob('*.pdf'):
    if ('2025년 행복황촌' in p.name or '2024년 황오동 원도심' in p.name or '천년 고도 경주의 골격' in p.name or '2025년 경주시 찾아가는 도시재생대학' in p.name): files.append(p)
meta=[]
for idx,p in enumerate(dict.fromkeys(files)):
    doc=fitz.open(p)
    tid='reference' if p==ref else f's{idx:02}'
    text='\n'.join(f'\n--- PDF PAGE {i+1} ---\n'+page.get_text() for i,page in enumerate(doc))
    (out/(tid+'.txt')).write_text(text,encoding='utf-8')
    row={'id':tid,'path':str(p),'pages':len(doc),'size':list(doc[0].rect)[2:]}
    meta.append(row)
    if p==ref:
        folder=build/'reference'; folder.mkdir(exist_ok=True)
        fonts={}
        for i,page in enumerate(doc):
            for b in page.get_text('dict')['blocks']:
                for line in b.get('lines',[]):
                    for span in line.get('spans',[]):
                        k=f"{span['font']} / {span['size']:.1f}"
                        fonts[k]=fonts.get(k,0)+len(span['text'])
            page.get_pixmap(matrix=fitz.Matrix(1,1)).save(folder/f'{i+1:02}.png')
        row['fonts']=fonts
(build/'source_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False,indent=2))
