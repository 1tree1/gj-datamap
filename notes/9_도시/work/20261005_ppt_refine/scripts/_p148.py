import pymupdf
d = pymupdf.open(r'C:\Users\OFFICE\Desktop\9_도시\22-0124) 경주시 도시재생전략계획 최종보고서.pdf')
pg = d[147]
for b in pg.get_text('blocks'):
    x0, y0, x1, y1, tx = b[0], b[1], b[2], b[3], b[4].strip().replace('\n', ' / ')
    if y0 > 380 and y0 < 700: print('(%.0f,%.0f,%.0f,%.0f) %s' % (x0, y0, x1, y1, tx[:70]))
print('drawings bbox rows:')
rects = [r['rect'] for r in pg.get_drawings() if r['rect'].width > 150 and 380 < r['rect'].y0 < 700]
for r in rects[:12]: print(r)
