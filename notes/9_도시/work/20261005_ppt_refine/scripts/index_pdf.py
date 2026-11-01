"""PDF 인덱스 — 쪽수, 텍스트 유무, 키워드가 나오는 쪽을 뽑는다. 사용: index_pdf.py <pdf> <out.txt> kw1 kw2 ..."""
import sys, time, re
import pymupdf
pdf, out = sys.argv[1], sys.argv[2]
kws = sys.argv[3:] or ["경주역"]
t0 = time.time()
doc = pymupdf.open(pdf)
print("pages", doc.page_count, "meta", doc.metadata.get("title"), "open %.1fs" % (time.time() - t0))
rows = []; empty = 0
hits = {k: [] for k in kws}
for i in range(doc.page_count):
    pg = doc[i]
    tx = pg.get_text("text") or ""
    n = len(tx.strip())
    if n < 20: empty += 1
    first = re.sub(r"\s+", " ", tx.strip())[:70]
    nimg = len(pg.get_images(full=False))
    rows.append((i + 1, n, nimg, first))
    for k in kws:
        c = tx.count(k)
        if c: hits[k].append((i + 1, c))
with open(out, "w", encoding="utf-8") as f:
    f.write("pdf: %s\npages: %d, empty-text pages: %d, elapsed %.1fs\n\n" % (pdf, doc.page_count, empty, time.time() - t0))
    for k in kws:
        f.write("[%s] %d pages: %s\n\n" % (k, len(hits[k]), " ".join("%d(%d)" % h for h in hits[k][:400])))
    f.write("page | chars | images | first text\n")
    for r in rows: f.write("%d | %d | %d | %s\n" % r)
print("done %.1fs, empty %d" % (time.time() - t0, empty))
for k in kws: print(k, len(hits[k]), [h[0] for h in hits[k][:60]])
