from pathlib import Path
import json,re,os
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
root=Path(r"C:\Users\OFFICE\Desktop\9_도시\work\nexus_placement_report_20261012")
app=Path(r"C:\Users\OFFICE\Desktop\9_도시\work\nexus_v13_audit_20261011\visual-report")
assert (app/'dist/index.html').exists()
s=json.loads((app/'src/data.json').read_text(encoding='utf-8'))
plots=s['queries']['latest_plots']['rows'];rows=s['queries']['placement_detail']['rows']
texts={r['id']:r['body'] for r in s['queries']['detail_narratives']['rows']}
d=Document();sec=d.sections[0]
sec.page_width=Cm(21);sec.page_height=Cm(29.7)
sec.top_margin=Cm(2.0);sec.bottom_margin=Cm(2.0);sec.left_margin=Cm(2.0);sec.right_margin=Cm(2.0)
for name,size in [('Normal',10.5),('Title',21),('Heading 1',16),('Heading 2',12.5),('Heading 3',11.5),('Caption',9)]:
 st=d.styles[name];st.font.name='Arial';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0)
 st.element.get_or_add_rPr().append(OxmlElement('w:rFonts'))
 st.element.rPr.rFonts.set(qn('w:eastAsia'),'Malgun Gothic')
 st.paragraph_format.space_after=Pt(6)
 st.paragraph_format.line_spacing=1.25
 if name.startswith('Heading'):
  st.paragraph_format.keep_with_next=True;st.paragraph_format.space_before=Pt(12)
def title(t):
 return re.sub(r'[·:/+]+',' ',t).strip()
def markdown(t):
 for block in t.split('\n\n'):
  block=block.strip()
  if not block: continue
  if block.startswith('### '):d.add_paragraph(title(block[4:]),'Heading 2')
  elif block.startswith('## '):d.add_paragraph(title(block[3:]),'Heading 1')
  else:d.add_paragraph(block)
def picture(file,caption,alt):
 p=d.add_paragraph();p.paragraph_format.keep_with_next=True
 shape=p.add_run().add_picture(str(file),width=Cm(17))
 shape._inline.docPr.set('descr',alt)
 cp=d.add_paragraph(caption,'Caption');cp.paragraph_format.space_after=Pt(10)
d.add_paragraph('NEXUS 1918 최종 마스터플랜 프로그램별 배치 근거 보고서','Title')
d.add_paragraph('2026년 10월 12일 제공 조감도 및 획지계획표 기준')
markdown(texts['overview'])
picture(app/'src/content/assets/placement-model-20261012.png','그림 1 최종 조감도 사용자 제공','최종 마스터플랜의 공공 주거 문화 창작 역사관광 권역을 보여주는 조감도')
picture(app/'src/content/assets/placement-plots-20261012.png','그림 2 획지계획도와 획지계획표 사용자 제공','북측 화살표와 1번부터 13번까지의 획지 위치 면적 층수를 나타낸 획지계획표')
d.add_paragraph('최신 도면의 획지별 표기값','Heading 1')
table=d.add_table(rows=1,cols=5);table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
widths=[.7,5.8,3.4,4.0,3.1]
for c,w in zip(table.columns,widths):c.width=Cm(w)
for i,text in enumerate(['번호','획지 프로그램','획지면적 ㎡','연면적 ㎡','최고 층수']):
 table.rows[0].cells[i].text=text
for r in plots:
 vals=[str(r['plot']),r['name'],format(r['area'],','),format(r['gfa'],','),str(r['floors'])]
 for cell,text,w in zip(table.add_row().cells,vals,widths):
  cell.text=text;cell.width=Cm(w)
for ri,row in enumerate(table.rows):
 for ci,cell in enumerate(row.cells):
  cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
  tcPr=cell._tc.get_or_add_tcPr()
  margins=OxmlElement('w:tcMar')
  for edge in ['top','left','bottom','right']:
   e=OxmlElement('w:'+edge);e.set(qn('w:w'),'80');e.set(qn('w:type'),'dxa');margins.append(e)
  tcPr.append(margins)
  borders=OxmlElement('w:tcBorders')
  for edge in ['top','left','bottom','right']:
   e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
  tcPr.append(borders)
  shd=OxmlElement('w:shd');shd.set(qn('w:fill'),'E8EEF4' if ri==0 else ('F5F7FA' if ri%2==0 else 'FFFFFF'));tcPr.append(shd)
  for p in cell.paragraphs:
   p.paragraph_format.keep_with_next=False;p.paragraph_format.space_after=Pt(3);p.paragraph_format.line_spacing=1.1
   p.alignment=WD_ALIGN_PARAGRAPH.LEFT if ci==1 else WD_ALIGN_PARAGRAPH.CENTER
   for run in p.runs:run.font.size=Pt(9);run.font.bold=ri==0
header=OxmlElement('w:tblHeader');table.rows[0]._tr.get_or_add_trPr().append(header)
d.add_paragraph('道면 합계는 연면적 192,447㎡다. 정수 행의 합계와 1㎡ 차이가 있어 도면 합계를 유지한다.'.replace('道면','도면'))
for plot in plots:
 d.add_paragraph(str(plot['plot'])+'번 획지 '+title(plot['name']),'Heading 1')
 d.add_paragraph('도면 표기  획지 '+format(plot['area'],',')+'㎡  건축 '+format(plot['footprint'],',')+'㎡  연면적 '+format(plot['gfa'],',')+'㎡  최고 '+str(plot['floors'])+'층  높이 '+str(plot['height'])+'m')
 d.add_paragraph('권역의 성격  '+plot['character'])
 for r in rows:
  if r['plot']==plot['plot']:markdown(r['body'])
d.add_paragraph('공원과 보행축의 배치 관계','Heading 1')
for r in rows:
 if r['plot']==0:markdown(r['body'])
markdown(texts['conclusion']);markdown(texts['methods'])
d.add_paragraph('자료 출처','Heading 1')
for text in ['2026년 10월 12일 사용자 제공 최종 마스터플랜 조감도','2026년 10월 12일 사용자 제공 획지계획도 및 획지계획표','NEXUS 1918 최종 통합 스페이스 프로그램 v13 2026년 10월 11일','사용자 공공기관 방문 인구 추정 및 프로그램별 배치 의도 설명']:
 d.add_paragraph(text)
out=root/'NEXUS_배치근거_상세보고서.docx';d.save(str(out))
print(json.dumps({'file':str(out),'bytes':out.stat().st_size,'programs':len(rows),'plots':len(plots)},ensure_ascii=False))

