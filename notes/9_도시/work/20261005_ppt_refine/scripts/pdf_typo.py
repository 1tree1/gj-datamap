"""통영 보고서(A3 가로)의 살아 있는 글자(span)를 쪽별로 뽑아 서체·크기·색·위치를 표로 낸다. 사용: pdf_typo.py <pdf> <out.txt> [쪽 목록 1,2,6 | all]"""
import sys, collections
import pymupdf
pdf, out = sys.argv[1], sys.argv[2]
sel = sys.argv[3] if len(sys.argv) > 3 else "all"
doc = pymupdf.open(pdf)
pages = range(1, len(doc) + 1) if sel == "all" else [int(x) for x in sel.split(",")]
lines = []
agg = collections.Counter()
for pn in pages:
    pg = doc[pn - 1]; W, H = pg.rect.width, pg.rect.height
    d = pg.get_text("dict")
    lines.append("=== p.%d  %.1f x %.1f pt" % (pn, W, H))
    rows = []
    for b in d["blocks"]:
        if b.get("type") != 0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                t = s["text"].strip()
                if not t: continue
                col = "#%06X" % s["color"]
                x0, y0, x1, y1 = s["bbox"]
                rows.append((round(y0, 1), round(x0, 1), s["font"], round(s["size"], 2), col, round(x1, 1), round(y1, 1), t[:60]))
                agg[(s["font"], round(s["size"], 1), col)] += len(t)
    for r in sorted(rows):
        lines.append("y%-6s x%-6s %-28s %5s %s  →x%-6s y%-6s | %s" % r)
lines.append("\n=== 서체·크기·색 사용량(글자 수) 상위")
for (f, s, c), n in agg.most_common(60): lines.append("%-30s %5s %s  %d" % (f, s, c, n))
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("written", out, len(lines))
