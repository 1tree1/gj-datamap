# -*- coding: utf-8 -*-
"""python-pptx 레이아웃 키트 — 16:9, 적색+흑백, 맑은 고딕(한글)/Courier New(수치). 제목 27pt, 본문 10.5–12pt, 하단 각주 없음(출처는 그림 캡션)."""
import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

SW, SH = 13.333, 7.5
RED = "C8102E"; RED_DK = "8B0A1E"; RED_LT = "F3D5DA"; INK = "111111"; G1 = "333333"; G2 = "6B6B6B"; G3 = "9E9E9E"; G4 = "C9C9C9"; G5 = "E6E6E6"; G6 = "F3F3F3"; WHITE = "FFFFFF"; BLACK = "0A0A0A"
KO = "Malgun Gothic"; NUM = "Courier New"
def rgb(h): return RGBColor.from_string(h)

class Deck:
    def __init__(self, tmpdir):
        self.prs = Presentation(); self.prs.slide_width = Inches(SW); self.prs.slide_height = Inches(SH)
        self.blank = self.prs.slide_layouts[6]; self.n = 0; self.tmp = tmpdir; os.makedirs(tmpdir, exist_ok=True)
        self.toc = []

    # ── 기본 요소 ─────────────────────────────────────────────────────────
    def _tf(self, shape, size, bold=False, color=INK, align=PP_ALIGN.LEFT, font=KO, anchor=MSO_ANCHOR.TOP, lsp=None):
        tf = shape.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_right = Inches(0.02); tf.margin_top = tf.margin_bottom = Inches(0.01); tf.vertical_anchor = anchor
        return tf
    def text(self, s, x, y, w, h, txt, size=11, bold=False, color=INK, align="l", font=KO, anchor="t", lsp=1.15, num=False):
        sh = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = self._tf(sh, size, anchor={"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor])
        lines = txt.split("\n") if isinstance(txt, str) else txt
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]; p.line_spacing = lsp
            self._runs(p, line, size, bold, color, NUM if num else font)
        return sh
    def _runs(self, p, line, size, bold, color, font):
        """'**굵게**' 와 '{{적색}}' 간단 마크업 지원"""
        import re
        tokens = re.split(r"(\*\*.+?\*\*|\{\{.+?\}\})", line)
        for t in tokens:
            if not t: continue
            r = p.add_run(); b = bold; c = color; txt = t
            if t.startswith("**"): txt = t[2:-2]; b = True
            elif t.startswith("{{"): txt = t[2:-2]; c = RED; b = True
            r.text = txt; r.font.size = Pt(size); r.font.bold = b; r.font.name = font; r.font.color.rgb = rgb(c)
            rPr = r._r.get_or_add_rPr(); ea = rPr.find(qn("a:ea"))
            if ea is None: ea = etree.SubElement(rPr, qn("a:ea"))
            ea.set("typeface", KO)
    def bullets(self, s, x, y, w, h, items, size=11, color=INK, gap=4, marker="·", lsp=1.18):
        sh = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = self._tf(sh, size)
        for i, it in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.line_spacing = lsp; p.space_after = Pt(gap)
            self._runs(p, (marker + " " if marker else "") + it, size, False, color, KO)
        return sh
    def rect(self, s, x, y, w, h, fill=G6, line=None, lw=0.75, shape=MSO_SHAPE.RECTANGLE):
        sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        if fill is None: sh.fill.background()
        else: sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        if line is None: sh.line.fill.background()
        else: sh.line.color.rgb = rgb(line); sh.line.width = Pt(lw)
        sh.shadow.inherit = False
        if sh.has_text_frame: sh.text_frame.text = ""
        return sh
    def hline(self, s, x, y, w, color=G4, lw=0.75):
        ln = s.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + w), Inches(y)); ln.line.color.rgb = rgb(color); ln.line.width = Pt(lw); return ln
    def vline(self, s, x, y, h, color=G4, lw=0.75):
        ln = s.shapes.add_connector(1, Inches(x), Inches(y), Inches(x), Inches(y + h)); ln.line.color.rgb = rgb(color); ln.line.width = Pt(lw); return ln
    def image(self, s, path, x, y, w, h, fit="contain", align="c"):
        """fit: contain(비율 유지, 박스 안) / cover(박스 채움, 잘라냄) / stretch"""
        im = Image.open(path); iw, ih = im.size; ar = iw / ih; br = w / h
        if fit == "cover":
            if ar > br: nw = int(ih * br); im2 = im.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
            else: nh = int(iw / br); im2 = im.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
            p2 = os.path.join(self.tmp, "crop_%d_%s.png" % (len(os.listdir(self.tmp)), os.path.basename(path)[:30]))
            im2.save(p2); return s.shapes.add_picture(p2, Inches(x), Inches(y), Inches(w), Inches(h))
        if fit == "stretch": return s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
        if ar > br: nw, nh = w, w / ar
        else: nw, nh = h * ar, h
        ox = x + (w - nw) / 2 if align == "c" else (x if align == "l" else x + w - nw); oy = y + (h - nh) / 2
        return s.shapes.add_picture(path, Inches(ox), Inches(oy), Inches(nw), Inches(nh))
    def caption(self, s, x, y, w, txt, size=8, color=G2, align="l"):
        return self.text(s, x, y, w, 0.3, txt, size=size, color=color, align=align)
    def tag(self, s, x, y, txt, color=RED, size=9.5, w=4):
        return self.text(s, x, y, w, 0.25, txt, size=size, bold=True, color=color)
    def metric(self, s, x, y, w, value, label, color=RED, vsize=30, lsize=10, sub=None):
        self.text(s, x, y, w, 0.6, value, size=vsize, bold=True, color=color, num=True, lsp=1.0)
        self.text(s, x, y + vsize / 72 * 1.25 + 0.02, w, 0.3, label, size=lsize, color=G1)
        if sub: self.text(s, x, y + vsize / 72 * 1.25 + 0.3, w, 0.3, sub, size=8.5, color=G2)
    def table(self, s, x, y, w, rows, col_w=None, size=9, head_size=None, row_h=0.3, head_fill=G6, hl_rows=(), hl_cols=(), num_cols=(), align=None, zebra=False, bold_first_col=False):
        """rows[0]=헤더. col_w: 비율 리스트. align: 열별 'l/c/r'. num_cols: Courier New 적용 열"""
        nr, nc = len(rows), len(rows[0]); H = row_h * nr
        gt = s.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(H)); tbl = gt.table
        tblPr = gt._element.graphic.graphicData.tbl.tblPr; tblPr.set("firstRow", "0"); tblPr.set("bandRow", "0")
        st = tblPr.find(qn("a:tableStyleId"))
        if st is not None: tblPr.remove(st)
        cw = col_w or [1.0 / nc] * nc; tot = sum(cw)
        for j in range(nc): tbl.columns[j].width = Inches(w * cw[j] / tot)
        for i in range(nr): tbl.rows[i].height = Inches(row_h)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                c = tbl.cell(i, j); c.margin_left = c.margin_right = Inches(0.06); c.margin_top = c.margin_bottom = Inches(0.025); c.vertical_anchor = MSO_ANCHOR.MIDDLE
                tf = c.text_frame; tf.word_wrap = True; p = tf.paragraphs[0]
                a = (align[j] if align else ("l" if j == 0 else "c")); p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[a]
                head = (i == 0); fnt = NUM if (j in num_cols and not head) else KO
                self._runs(p, str(val), (head_size or size) if head else size, head or (bold_first_col and j == 0) or (i in hl_rows), (G1 if head else (RED if (i in hl_rows or j in hl_cols) and not head else INK)), fnt)
                c.fill.solid(); c.fill.fore_color.rgb = rgb(head_fill if head else ((G6 if zebra and i % 2 == 0 else WHITE)))
                self._borders(c, top=(G3 if head else G5), bottom=(G3 if head or i == nr - 1 else G5))
        return gt
    def _borders(self, cell, top=G5, bottom=G5, left=None, right=None):
        tcPr = cell._tc.get_or_add_tcPr()
        for tag_, col in (("a:lnL", left), ("a:lnR", right), ("a:lnT", top), ("a:lnB", bottom)):
            ln = tcPr.find(qn(tag_))
            if ln is not None: tcPr.remove(ln)
            ln = etree.SubElement(tcPr, qn(tag_))
            if col is None: ln.set("w", "0"); etree.SubElement(ln, qn("a:noFill"))
            else:
                ln.set("w", "6350"); sf = etree.SubElement(ln, qn("a:solidFill")); c = etree.SubElement(sf, qn("a:srgbClr")); c.set("val", col)
    # ── 슬라이드 틀 ────────────────────────────────────────────────────────
    def slide(self, section, title, lead=None, number=True):
        s = self.prs.slides.add_slide(self.blank); self.n += 1
        bg = s.background; bg.fill.solid(); bg.fill.fore_color.rgb = rgb(WHITE)
        self.text(s, 0.6, 0.38, 8, 0.25, section, size=9.5, bold=True, color=RED)
        self.text(s, 0.6, 0.62, 11.5, 0.6, title, size=27, bold=True, color=INK, lsp=1.0)
        if lead: self.text(s, 0.6, 1.22, 12.1, 0.35, lead, size=11.5, color=G1)
        self.hline(s, 0.6, 1.62 if lead else 1.3, 12.13, color=G4, lw=0.75)
        if number: self.text(s, 12.2, 7.02, 0.55, 0.3, "%02d" % self.n, size=10, color=G2, align="r", num=True)
        self.toc.append((self.n, section, title)); s._top = 1.78 if lead else 1.48
        return s
    def divider(self, num, title, sub=None, items=None):
        s = self.prs.slides.add_slide(self.blank); self.n += 1
        bg = s.background; bg.fill.solid(); bg.fill.fore_color.rgb = rgb(BLACK)
        self.text(s, 0.9, 1.5, 3, 1.6, num, size=96, bold=True, color=RED, num=True, lsp=1.0)
        self.text(s, 0.9, 3.55, 9, 0.9, title, size=34, bold=True, color=WHITE, lsp=1.0)
        if sub: self.text(s, 0.9, 4.45, 10, 0.5, sub, size=13, color=G4)
        if items: self.text(s, 0.9, 5.15, 11, 1.4, items, size=11, color=G3, lsp=1.3)
        self.hline(s, 0.9, 3.42, 1.4, color=RED, lw=2.5)
        self.text(s, 12.2, 7.02, 0.55, 0.3, "%02d" % self.n, size=10, color=G3, align="r", num=True)
        self.toc.append((self.n, "", title)); return s
    def blank_slide(self, bg=WHITE):
        s = self.prs.slides.add_slide(self.blank); self.n += 1
        b = s.background; b.fill.solid(); b.fill.fore_color.rgb = rgb(bg); return s
    def save(self, path): self.prs.save(path)
