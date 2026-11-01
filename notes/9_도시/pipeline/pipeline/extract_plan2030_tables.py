"""2030 경주도시기본계획 정제 마크다운(45절)의 표 전부를 기계판독 JSON으로.

각 표: 절 파일, 절 제목, 표 제목(**[..]**), 직전 쪽 앵커(<!-- p.NNN -->), 헤더, 행, 자료 출처 줄.
출력: archive/90_derived/plan2030_tables.json  (+ 요약 인덱스 CSV)
"""
import re, json, csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / '2030경주도시기본계획/refined'
OUT = ROOT / 'archive/90_derived'
tables = []
for f in sorted(SRC.glob('*.md')):
    t = f.read_text(encoding='utf-8')
    fm = re.search(r'^title:\s*(.+)$', t, flags=re.M); sec = fm.group(1).strip() if fm else f.stem
    lines = t.split('\n'); page = None; title = None; i = 0
    while i < len(lines):
        l = lines[i]
        m = re.search(r'<!--\s*p\.(\d+)\s*-->', l)
        if m: page = int(m.group(1))
        m = re.match(r'^\*\*\[(.+?)\]\*\*', l)
        if m: title = m.group(1).strip()
        if l.startswith('|') and i + 1 < len(lines) and re.match(r'^\|\s*:?-', lines[i + 1]):
            hdr = [c.strip() for c in l.strip().strip('|').split('|')]
            rows = []; j = i + 2
            while j < len(lines) and lines[j].startswith('|'):
                rows.append([c.strip() for c in lines[j].strip().strip('|').split('|')]); j += 1
            src = ''
            for k in range(j, min(j + 4, len(lines))):
                if lines[k].startswith('자료') or lines[k].startswith('주 :') or lines[k].startswith('주:'): src += lines[k].strip() + ' '
            tables.append({'file': f.name, 'section': sec, 'title': title, 'page': page, 'header': hdr, 'rows': rows, 'source': src.strip(), 'n_rows': len(rows), 'n_cols': len(hdr)})
            title = None; i = j; continue
        i += 1
json.dump(tables, open(OUT / 'plan2030_tables.json', 'w', encoding='utf-8'), ensure_ascii=False)
with open(OUT / 'plan2030_tables_index.csv', 'w', newline='', encoding='utf-8-sig') as fo:
    w = csv.writer(fo); w.writerow(['idx', 'file', 'section', 'title', 'page', 'n_rows', 'n_cols', 'header', 'source'])
    for k, tb in enumerate(tables): w.writerow([k, tb['file'], tb['section'], tb['title'], tb['page'], tb['n_rows'], tb['n_cols'], ' | '.join(tb['header'])[:200], tb['source'][:200]])
print(len(tables), 'tables')
