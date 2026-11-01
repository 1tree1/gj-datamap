import pymupdf
d = pymupdf.open(r'C:\Users\OFFICE\Desktop\9_도시\2026 09 03 건축디자인6 01주차 오리엔테이션.pdf')
print('pages', d.page_count)
for i in range(d.page_count):
    t = d[i].get_text().strip()
    print('--- p%d (%d chars)' % (i + 1, len(t)))
    print(t[:1500])
