"""여백 쪽 다음 쪽 맨 위 요소(그림·표 캡션) 찾기 → culprits.json"""
import re, json, subprocess, sys, pymupdf
K = 72 / 25.4
d = pymupdf.open("../output/구경주역_도시재생_마스터플랜_보고서.pdf")
out = subprocess.run([sys.executable, "-W", "ignore", "gapcheck.py", "../output/구경주역_도시재생_마스터플랜_보고서.pdf", "40"], capture_output=True, text=True, encoding="utf-8").stdout
rows = [eval(l) for l in out.splitlines() if l.startswith("(")]
pages = {}
for p, col, gb, mids in rows:
    pages.setdefault(p, {})[col] = gb
res = []
for p, cols in sorted(pages.items()):
    G = min(cols.get("L", 0), cols.get("R", 0)) if len(cols) == 2 else max(cols.values())
    nxt = d[p]                                         # 다음 쪽(0-기준 p = 다음 쪽)
    blocks = sorted([b for b in nxt.get_text("blocks") if b[1] > 20 * K], key=lambda b: (b[1], b[0]))
    cap = None
    for b in blocks[:40]:
        m = re.search(r"(그림|표) (\d+-\d+)", b[4])
        if m and b[4].strip().startswith(m.group(0)): cap = m.group(0); cy = b[1] / K; break
    res.append(dict(page=p, cols=cols, gap=G, next_cap=cap))
json.dump(res, open("culprits.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
for r in res: print(r)
