import pymupdf, re
d = pymupdf.open(r'C:\Users\OFFICE\Desktop\9_도시\22-0124) 경주시 도시재생전략계획 최종보고서.pdf')
for p in (122, 148, 392, 393, 186):
    t = d[p-1].get_text().strip()
    print('=== p%d ===' % p)
    print(re.sub(r'\n+', ' / ', t)[:1500])
d2 = pymupdf.open(r'C:\Users\OFFICE\Desktop\9_도시\#경주시 원도심 미래구상 기획 연구 0804 최종본.pdf')
for p in (64, 65, 105, 106):
    t = d2[p-1].get_text().strip()
    print('=== 417 p%d ===' % p)
    print(re.sub(r'\n+', ' / ', t)[:1600])
