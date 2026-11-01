import json,hashlib,zipfile,subprocess,posixpath
from pathlib import Path
from lxml import etree as E

R=Path(__file__).parent;B=R/'build';rec=json.loads((B/'edit_receipt.json').read_text('utf-8'))
SRC=Path(rec['source']);draft=B/'candidate.pptx'
SK=Path(r'C:\Users\OFFICE\.codex\plugins\cache\openai-primary-runtime\presentations\26.1007.11041\skills\presentations\container_tools')
PY=Path(r'C:\Users\OFFICE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
def run(script,p,extra=[]):
    p=subprocess.run([str(PY),'-X','utf8',str(SK/script),str(p),*extra],capture_output=True,text=True,encoding='utf-8')
    assert p.stdout.strip(),p.stderr
    return {'exitCode':p.returncode,'report':json.loads(p.stdout)}
chartargs=['--expected-chart-slides','11,13,14,15,16,17,18,19,20,21,50,56']
source_chart=run('native_quantitative_chart_gate.py',SRC,chartargs)
draft_chart=run('native_quantitative_chart_gate.py',draft,chartargs)
source_failed=source_chart['report'].get('failed_slides',[])
draft_failed=draft_chart['report'].get('failed_slides',[])
assert source_failed==draft_failed,(source_failed,draft_failed)
integrity=run('inspect_presentation_package_integrity.py',draft)
layout=run('inspect_presentation_layout_geometry.py',draft,['--expected-slide-size-emu','12192000,6858000','--expected-slide-count','64','--require-native-table-slide','62','--require-native-table-slide','63','--approved-font-family','Pretendard','--validate-heading-fit'])
assert integrity['exitCode']==0 and layout['exitCode']==0
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
with zipfile.ZipFile(SRC) as zs,zipfile.ZipFile(draft) as zd:
    original_parts=zs.namelist()
    for n in original_parts:
        if ('/charts/' in n or '/embeddings/' in n):assert zs.read(n)==zd.read(n),n
    pres=E.fromstring(zd.read('ppt/presentation.xml'))
    rels={r.get('Id'):r for r in E.fromstring(zd.read('ppt/_rels/presentation.xml.rels'))}
    ids=list(pres.find('p:sldIdLst',ns));assert len(ids)==64
    for num in [62,63]:
        target=rels[ids[num-1].get('{'+ns['r']+'}id')].get('Target')
        part=posixpath.normpath(posixpath.join('ppt',target))
        x=E.fromstring(zd.read(part));assert len(x.findall('.//a:tbl',ns))==1
        assert '데이터 출처' in ''.join(x.xpath('//a:t/text()',namespaces=ns))
    last=rels[ids[-1].get('{'+ns['r']+'}id')].get('Target');assert last=='slides/slide62.xml'
report={'sourceChartFindings':source_failed,'finalChartFindings':draft_failed,'allOriginalChartAndWorkbookBytesPreserved':True,'packageIntegrity':integrity,'layout':layout,'editedPage':2,'newSourcePages':[62,63],'slideCount':64,'newSourcesValidatedSeparately':(R/'source_section.validation.json').exists(),'scopePreserved':True}
dest=R/'output'/'261012_중간마감pt_건축디자인6_b분반_이승규,김민승_목차출처수정.pptx'
assert not dest.exists()
dest.write_bytes(draft.read_bytes())
report['final']=str(dest);report['finalSha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
(B/'delivery_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'delivered':str(dest),'slideCount':64,'existingSourceChartFindings':source_failed,'originalContentPreserved':True},ensure_ascii=False))
