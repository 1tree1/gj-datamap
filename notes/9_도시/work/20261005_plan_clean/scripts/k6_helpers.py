"""표 그리기 도우미 — 여러 페이지(획지계획표·도로계획표)가 공유한다."""
from plotkit import *

def grid_table(pg, x, y, cols, rows, hdr_h=9.0, row_h=9.5, hdr_fs=6.8, shade_rows=(), line_c="#c8c8c8"):
    """cols: [(제목, 폭mm, 정렬)] rows: [[셀...]] 셀은 str 또는 (str, dict(fs,c,bold)) 또는 list(여러 줄).
    row_h 는 숫자 또는 행별 높이 리스트. 반환: 표 아래 y(mm)"""
    xs = [x]
    for _, w, _ in cols: xs.append(xs[-1] + w)
    pg.line(x, y, xs[-1], y, lw=0.9)
    for (title, w, al), x0 in zip(cols, xs[:-1]):
        tx = x0 + (w / 2 if al == "c" else (w - 1.5 if al == "r" else 1.5))
        pg.t(tx, y + hdr_h / 2, title, fs=hdr_fs, bold=True, ha={"c": "center", "r": "right", "l": "left"}[al], linespacing=1.15)
    pg.line(x, y + hdr_h, xs[-1], y + hdr_h, lw=0.5)
    yy = y + hdr_h
    for i, r in enumerate(rows):
        rh = row_h[i] if isinstance(row_h, (list, tuple)) else row_h
        if i in shade_rows: pg.rect(x, yy, xs[-1] - x, rh, fc=GREY, z=1)
        for (title, w, al), x0, cell in zip(cols, xs[:-1], r):
            lines = cell if isinstance(cell, list) else [cell]
            n = len(lines)
            for j, ln in enumerate(lines):
                sty = {}
                if isinstance(ln, tuple): ln, sty = ln
                fs = sty.get("fs", 7.0); c = sty.get("c", INK); bd = sty.get("bold", False)
                ty = yy + rh / 2 + (j - (n - 1) / 2) * (rh * 0.30 if n > 2 else (rh * 0.40 if n > 1 else 0))
                tx = x0 + (w / 2 if al == "c" else (w - 1.5 if al == "r" else 1.5))
                pg.t(tx, ty, ln, fs=fs, c=c, bold=bd, ha={"c": "center", "r": "right", "l": "left"}[al])
        yy += rh
        pg.line(x, yy, xs[-1], yy, c=line_c, lw=0.35)
    pg.line(x, yy, xs[-1], yy, lw=0.9)
    return yy
