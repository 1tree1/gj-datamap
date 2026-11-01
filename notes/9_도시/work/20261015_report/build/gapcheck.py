"""쪽별 단(左·右) 하단·중간 여백 검사 — 장 끝 쪽은 제외. 사용: python gapcheck.py [pdf] [임계 mm]"""
import sys, json, pymupdf
K = 72 / 25.4
pdf = sys.argv[1] if len(sys.argv) > 1 else "../output/구경주역_도시재생_마스터플랜_보고서.pdf"
TH = float(sys.argv[2]) if len(sys.argv) > 2 else 45.0
d = pymupdf.open(pdf)
# 장 시작 쪽만(절 시작 쪽은 제외하면 안 됨 — 2026-10-19 수정: 이전에는 절 시작 쪽 앞 쪽까지 검사에서 빠졌다)
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble
_tp = json.load(open("toc_pages.json", encoding="utf-8"))
starts = set(_tp[t] for _, t, _ in assemble.outline(assemble.chapters()) if t in _tp)
TOP, BOT, MID = 21 * K, 278 * K, 210 * K
res = []
for i in range(2, d.page_count):
    pg = d[i]
    if (i + 2) in starts or i == d.page_count - 1:          # 다음 쪽이 장 시작이면 장 끝 쪽 → 제외
        continue
    items = [pymupdf.Rect(b[:4]) for b in pg.get_text("blocks") if b[1] > TOP - 2 and b[3] < BOT + 4]
    items += [pymupdf.Rect(im["bbox"]) for im in pg.get_image_info()]
    items += [r["rect"] for r in pg.get_drawings() if r["rect"].height > 2 and r["rect"].y0 > TOP and r["rect"].y1 < BOT + 2]
    for name, x0, x1 in (("L", 0, MID), ("R", MID, 1e9)):
        col = sorted([r for r in items if r.x0 < x1 and r.x1 > x0], key=lambda r: r.y0)
        if not col: continue
        bottom = max(r.y1 for r in col)
        gap_b = (BOT - bottom) / K
        gaps = []; cur = col[0].y1
        for r in col[1:]:
            if r.y0 - cur > TH * K: gaps.append(round((r.y0 - cur) / K))
            cur = max(cur, r.y1)
        if gap_b > TH or gaps: res.append((i + 1, name, round(gap_b), gaps))
print("pages", d.page_count, "flagged", len(res))
for r in res: print(r)
