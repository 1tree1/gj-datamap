import json, posixpath, zipfile
from pathlib import Path
from lxml import etree

SRC = Path(r'C:\Users\OFFICE\Desktop\261012_중간마감pt_건축디자인6_b분반_이승규,김민승.pptx')
BUILD = Path(__file__).parent / 'build'
BUILD.mkdir(parents=True, exist_ok=True)
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
with zipfile.ZipFile(SRC) as z:
    root=etree.fromstring(z.read('ppt/presentation.xml'))
    rel=etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
    rm={r.get('Id'):posixpath.normpath(posixpath.join('ppt',r.get('Target'))) for r in rel}
    slides=[]
    for i,sid in enumerate(root.find('p:sldIdLst',NS),1):
        name=rm[sid.get('{'+NS['r']+'}id')]
        s=etree.fromstring(z.read(name))
        shapes=[]
        for sp in s.findall('.//p:sp',NS):
            texts=[''.join(p.itertext()) for p in sp.findall('.//a:t',NS)]
            if not texts: continue
            nv=sp.find('p:nvSpPr/p:cNvPr',NS)
            shapes.append({'id':nv.get('id'),'name':nv.get('name'),'text':'\n'.join(texts),'xml':etree.tostring(sp,encoding='unicode')})
        notes=[]
        relname=posixpath.join(posixpath.dirname(name),'_rels',posixpath.basename(name)+'.rels')
        if relname in z.namelist():
            sr=etree.fromstring(z.read(relname))
            for r in sr:
                if r.get('Type','').endswith('/notesSlide'):
                    np=posixpath.normpath(posixpath.join(posixpath.dirname(name),r.get('Target')))
                    notes=etree.fromstring(z.read(np)).xpath('//a:t/text()',namespaces=NS)
        rec={'number':i,'part':name,'shapes':shapes,'texts':s.xpath('//a:t/text()',namespaces=NS),'notes':notes}
        slides.append(rec)
        print(f'\n[{i}] {name}\n'+ ' / '.join(rec['texts']))
        if notes: print('NOTES: '+' / '.join(notes))
    size=root.find('p:sldSz',NS)
    fonts=sorted(set(etree.fromstring(z.read(n)).xpath('//@typeface') for n in []))
    out={'source':str(SRC),'size':dict(size.attrib),'slides':slides}
    (BUILD/'source_structure.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print('SIZE',dict(size.attrib),'COUNT',len(slides))
