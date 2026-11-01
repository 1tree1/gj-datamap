"""pptkit — python-pptx 도우미. 서체 규칙(CLAUDE.md §11): 한글 맑은 고딕 / 영문·수치 Courier New, 본문 10.5–12pt, 제목 27pt, 하단 주석 없음."""
import os, math
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image

KO, EN = "Pretendard", "Arial"          # 통영 보고서: 영문 Arial / 국문 KoPub돋움(이 PC에 없어 폭이 같은 Pretendard로 대체)
SW, SH = 13.333, 7.5
INK, INK2, GRAY, LINE, TINT = "#231F20", "#4D4D4D", "#6D6E71", "#D1D3D4", "#F5F7FA"
RED, BLUE = "#D7191C", "#1F5AA6"
ZN, ZC, ZS = "#6F9FDC", "#A98BD3", "#F4A0C2"           # 북·중·남 (조감도의 용도색과 같은 계열)
YEL = "#F1D247"
WARN = []                                                 # 글상자 넘침 경고

def rgb(h): h = h.lstrip("#"); return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
def tint(h, t):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) for i in (0, 2, 4)]; c = [int(round(v * (1 - t) + 255 * t)) for v in c]
    return "#%02x%02x%02x" % tuple(c)

# ── 글자 폭 추정(넘침 경고용) ───────────────────────────────────────────────
def _cw(ch, em):
    o = ord(ch)
    if o >= 0x1100: return em * 1.0
    return em * 0.6
def est_lines(text, width_in, size_pt):
    em = size_pt / 72.0; usable = max(width_in, 0.3); n = 0
    for para in str(text).split("\n"):
        w = sum(_cw(c, em) for c in para)
        n += max(1, math.ceil(w * 1.04 / usable))
    return n
def est_height(paras, width_in, size_pt, line=1.12):
    h = 0
    for p in paras:
        sz = p.get("size", size_pt); tx = p.get("text") if p.get("text") is not None else "".join(r[0] for r in p["runs"])
        ind = 0.18 if p.get("bullet") else 0
        h += est_lines(tx, width_in - ind, sz) * sz * 1.33 * line / 72.0 + p.get("space_after", 0) / 72.0
    return h

# ── 서식 ────────────────────────────────────────────────────────────────────
def style_run(run, size, bold=False, color=INK, italic=False):
    f = run.font; f.size = Pt(size); f.bold = bold; f.italic = italic; f.color.rgb = rgb(color); f.name = EN
    rPr = run._r.get_or_add_rPr(); rPr.set("lang", "ko-KR")
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None: el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", KO)

def _bullet(p, char="•", indent_in=0.17):
    pPr = p._p.get_or_add_pPr(); pPr.set("marL", str(int(Inches(indent_in)))); pPr.set("indent", str(-int(Inches(indent_in))))
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum"):
        for el in pPr.findall(qn(tag)): pPr.remove(el)
    bu = etree.SubElement(pPr, qn("a:buChar")); bu.set("char", char)

def _norm(paras, size, color, bold, bullet, align):
    if isinstance(paras, (str, tuple)): paras = [paras]
    out = []
    for p in paras:
        if isinstance(p, str): p = dict(text=p)
        elif isinstance(p, tuple): p = dict(runs=[p]) if not isinstance(p[0], tuple) else dict(runs=list(p))
        p = dict(p); p.setdefault("size", size); p.setdefault("color", color); p.setdefault("bold", bold); p.setdefault("bullet", bullet); p.setdefault("align", align)
        if p.get("text") is not None and "\n" in p["text"]:          # 줄바꿈은 문단으로 쪼갠다(마지막 줄에만 문단 간격)
            parts = p["text"].split("\n")
            for k, part in enumerate(parts):
                q = dict(p); q["text"] = part
                if k < len(parts) - 1: q["space_after"] = 0; q["bullet"] = p["bullet"] and k == 0
                else: q["bullet"] = p["bullet"] and len(parts) == 1
                out.append(q)
            continue
        out.append(p)
    return out

ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}
ANCHOR = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}

def fill_tf(tf, paras, size=12, color=INK, bold=False, align="l", line=1.12, bullet=False, anchor="t", margin=(0.04, 0.02, 0.04, 0.02)):
    paras = _norm(paras, size, color, bold, bullet, align)
    tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left, tf.margin_top, tf.margin_right, tf.margin_bottom = [Inches(m) for m in margin]
    tf.vertical_anchor = ANCHOR[anchor]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = ALIGN[p["align"]]; para.line_spacing = line
        if p.get("space_after") is not None: para.space_after = Pt(p["space_after"])
        if p.get("space_before") is not None: para.space_before = Pt(p["space_before"])
        runs = p.get("runs") or [(p["text"], {})]
        for tx, st in runs:
            r = para.add_run(); r.text = tx
            style_run(r, st.get("size", p["size"]), st.get("bold", p["bold"]), st.get("color", p["color"]), st.get("italic", False))
        if p["bullet"]: _bullet(para)
    return paras

def _first(ps):
    p = ps[0]
    if p.get("text") is not None: return str(p["text"])[:30]
    return str(p["runs"][0][0])[:30] if p.get("runs") else ""

def text(slide, x, y, w, h, paras, size=12, color=INK, bold=False, align="l", anchor="t", line=1.12, bullet=False, margin=(0.04, 0.02, 0.04, 0.02), tag=""):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    ps = fill_tf(tb.text_frame, paras, size, color, bold, align, line, bullet, anchor, margin)
    eh = est_height(ps, w - margin[0] - margin[2], size, line) + margin[1] + margin[3]
    if eh > h * 1.04: WARN.append("넘침? [%s] 추정 %.2f in > 상자 %.2f in : %s" % (tag, eh, h, _first(ps)))
    return tb

def _no_shadow(shape):
    spPr = shape._element.spPr
    if spPr.find(qn("a:effectLst")) is None: etree.SubElement(spPr, qn("a:effectLst"))

def rect(slide, x, y, w, h, fill=None, line=None, line_w=0.75, radius=None, alpha=None, shape=None):
    shp = slide.shapes.add_shape(shape or (MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE), Inches(x), Inches(y), Inches(w), Inches(h))
    if radius and shp.adjustments is not None and len(shp.adjustments): shp.adjustments[0] = min(0.5, radius / min(w, h))
    if fill: shp.fill.solid(); shp.fill.fore_color.rgb = rgb(fill)
    else: shp.fill.background()
    if line: shp.line.color.rgb = rgb(line); shp.line.width = Pt(line_w)
    else: shp.line.fill.background()
    if alpha is not None and fill:
        clr = shp.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr")); a = etree.SubElement(clr, qn("a:alpha")); a.set("val", str(int(alpha * 100000)))
    _no_shadow(shp)
    shp.text_frame.text = ""
    return shp

def box_text(slide, x, y, w, h, paras, fill=None, line=None, radius=None, size=12, color=INK, bold=False, align="l", anchor="m", margin=(0.12, 0.08, 0.12, 0.08), line_w=0.75, alpha=None, tag="", line_sp=1.12, bullet=False):
    shp = rect(slide, x, y, w, h, fill, line, line_w, radius, alpha)
    ps = fill_tf(shp.text_frame, paras, size, color, bold, align, line_sp, bullet, anchor, margin)
    eh = est_height(ps, w - margin[0] - margin[2], size, line_sp) + margin[1] + margin[3]
    if eh > h * 1.04: WARN.append("넘침? [%s] 추정 %.2f in > 상자 %.2f in : %s" % (tag, eh, h, _first(ps)))
    return shp

def oval(slide, x, y, d, fill, text_=None, size=12, color="#FFFFFF", bold=True, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    shp.fill.solid(); shp.fill.fore_color.rgb = rgb(fill)
    if line: shp.line.color.rgb = rgb(line); shp.line.width = Pt(1)
    else: shp.line.fill.background()
    _no_shadow(shp)
    if text_ is not None: fill_tf(shp.text_frame, [dict(text=text_)], size, color, bold, "c", 1.0, False, "m", (0, 0, 0, 0))
    return shp

def line(slide, x1, y1, x2, y2, color=INK2, w=1.0, dash=False, arrow=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color); c.line.width = Pt(w)
    ln = c.line._get_or_add_ln()
    if dash:
        d = etree.SubElement(ln, qn("a:prstDash")); d.set("val", "dash")
    if arrow:
        t = etree.SubElement(ln, qn("a:tailEnd")); t.set("type", "triangle"); t.set("w", "med"); t.set("len", "med")
    return c

def arrow_right(slide, x, y, w, h, fill):
    shp = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid(); shp.fill.fore_color.rgb = rgb(fill); shp.line.fill.background(); _no_shadow(shp); return shp

def picture(slide, path, x, y, w, h, mode="contain", align=(0.5, 0.5), border=None):
    iw, ih = Image.open(path).size
    if mode == "contain":
        s = min(w / iw, h / ih); pw, ph = iw * s, ih * s
        pic = slide.shapes.add_picture(path, Inches(x + (w - pw) * align[0]), Inches(y + (h - ph) * align[1]), Inches(pw), Inches(ph))
    else:                                                  # cover: 틀을 가득 채우고 넘치는 쪽은 자른다
        pic = slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
        af, ai = w / h, iw / ih
        if ai > af:
            tot = 1 - af / ai; pic.crop_left = tot * align[0]; pic.crop_right = tot * (1 - align[0])
        else:
            tot = 1 - ai / af; pic.crop_top = tot * align[1]; pic.crop_bottom = tot * (1 - align[1])
    if border: pic.line.color.rgb = rgb(border); pic.line.width = Pt(0.75)
    return pic

def _cell_border(cell, **sides):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for el in tcPr.findall(qn(tag)): tcPr.remove(el)
    made = []
    for key, tag in (("l", "a:lnL"), ("r", "a:lnR"), ("t", "a:lnT"), ("b", "a:lnB")):
        spec = sides.get(key)
        ln = etree.Element(qn(tag))
        if spec is None:
            ln.set("w", "0"); etree.SubElement(ln, qn("a:noFill"))
        else:
            col, wpt = spec; ln.set("w", str(int(Pt(wpt)))); ln.set("cap", "flat"); ln.set("cmpd", "sng")
            sf = etree.SubElement(ln, qn("a:solidFill")); c = etree.SubElement(sf, qn("a:srgbClr")); c.set("val", col.lstrip("#"))
        made.append(ln)
    for i, ln in enumerate(made): tcPr.insert(i, ln)

def table(slide, x, y, col_w, rows, row_h=0.32, size=10.5, header=True, header_fill=INK, header_color="#FFFFFF", zebra=True, align=None, bold_cols=(), row_fills=None, hdr_h=None, line_c=LINE, tag="", valign="m", pad=(0.07, 0.03)):
    nr, nc = len(rows), len(col_w)
    shp = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(sum(col_w)), Inches(row_h * nr))
    tbl = shp._element.graphic.graphicData.tbl; tblPr = tbl.tblPr
    tblPr.set("firstRow", "0"); tblPr.set("bandRow", "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is None: sid = etree.SubElement(tblPr, qn("a:tableStyleId"))
    sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"
    t = shp.table
    for j, wv in enumerate(col_w): t.columns[j].width = Inches(wv)
    align = align or ["l"] * nc
    for i, r in enumerate(rows):
        rh = (hdr_h if (i == 0 and header and hdr_h) else row_h)
        t.rows[i].height = Inches(rh)
        for j in range(nc):
            cell = t.cell(i, j); v = r[j] if j < len(r) else ""
            st = {}
            if isinstance(v, dict): st = v; v = st.get("text", "")
            is_h = header and i == 0
            fillc = header_fill if is_h else (st.get("fill") or (row_fills[i] if row_fills and row_fills.get(i) else (TINT if (zebra and i % 2 == 0) else "#FFFFFF")))
            cell.fill.solid(); cell.fill.fore_color.rgb = rgb(fillc)
            cell.margin_left = cell.margin_right = Inches(pad[0]); cell.margin_top = cell.margin_bottom = Inches(pad[1])
            cell.vertical_anchor = ANCHOR[valign]
            tf = cell.text_frame; tf.word_wrap = True
            fill_tf(tf, [dict(text=str(v))], st.get("size", size), st.get("color", header_color if is_h else INK), st.get("bold", is_h or (j in bold_cols)), st.get("align", align[j]), 1.05, False, valign, (pad[0], pad[1], pad[0], pad[1]))
            _cell_border(cell, b=(line_c, 0.5))
            est = est_lines(str(v), col_w[j] - 2 * pad[0], st.get("size", size)) * st.get("size", size) * 1.33 * 1.05 / 72.0 + 2 * pad[1]
            if est > rh * 1.05: WARN.append("표 칸 넘침? [%s] r%d c%d 추정 %.2f > %.2f : %s" % (tag, i, j, est, rh, str(v)[:20]))
    return shp

def notes(slide, txt): slide.notes_slide.notes_text_frame.text = txt

class Deck:
    def __init__(self):
        self.prs = Presentation(); self.prs.slide_width = Inches(SW); self.prs.slide_height = Inches(SH); self.n = 0
    def slide(self, bg="#FFFFFF"):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6]); self.n += 1
        s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(bg); return s
    def save(self, path): self.prs.save(path)

def title_block(slide, label, title, sub=None, title_color=INK, label_color=RED, w=12.13):
    text(slide, 0.6, 0.36, w, 0.3, label, size=12.18, color="#FF0000", bold=False, tag="label")          # 보고서: Arial 12.18pt #FF0000
    text(slide, 0.6, 0.64, w, 0.62, title, size=20, bold=True, color=title_color, tag="title:" + title[:12])   # Arial Bold 20pt #231F20
    if sub: text(slide, 0.6, 1.26, w, 0.32, sub, size=14, color=INK, tag="sub")                            # Arial 14pt #231F20

def page_no(slide, n, color=GRAY):
    text(slide, 12.2, 7.08, 0.6, 0.28, "%02d" % n, size=10.5, color=color, align="r", tag="pg")

def chip(slide, x, y, w, h, label, fill, color="#FFFFFF", size=10.5, bold=True, radius=0.08):
    return box_text(slide, x, y, w, h, label, fill=fill, radius=radius, size=size, color=color, bold=bold, align="c", margin=(0.04, 0.0, 0.04, 0.0))

def source_tag(slide, x, y, w, label, color=GRAY):
    text(slide, x, y, w, 0.25, label, size=10.5, color=color, tag="src")

def photo_credit(slide, x, y, w, h, label):
    """사진·지도 아래쪽에 얹는 출처 띠(슬라이드 하단 주석이 아니라 이미지 크레딧). (x,y,w,h)는 이미지 틀."""
    rect(slide, x, y + h - 0.27, w, 0.27, fill="#000000", alpha=0.5)
    text(slide, x + 0.05, y + h - 0.27, w - 0.1, 0.27, label, size=10.5, color="#FFFFFF", anchor="m", margin=(0.05, 0, 0.05, 0), tag="credit")
