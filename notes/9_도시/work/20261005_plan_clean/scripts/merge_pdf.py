import fitz, os
d = r'C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean'
names = ['01_획지구획도_획지계획표.pdf', '02_조감도_SiteAnchors.pdf', '03_면적표.pdf', '04_도로계획도_도로계획표.pdf']
out = fitz.open()
for n in names:
    src = fitz.open(os.path.join(d, n)); out.insert_pdf(src); print(n, src.page_count, round(src[0].rect.width / 72 * 25.4), 'x', round(src[0].rect.height / 72 * 25.4), 'mm')
out.set_metadata({'title': '구경주역 획지·매스 — 규제 미적용 개념안 v1', 'author': '', 'subject': '획지구획도·조감도·면적표·도로계획도'})
p = os.path.join(d, '20261005_획지매스_규제미적용v1_시트모음.pdf'); out.save(p, deflate=True); print('saved', p, round(os.path.getsize(p) / 1e6, 1), 'MB')
