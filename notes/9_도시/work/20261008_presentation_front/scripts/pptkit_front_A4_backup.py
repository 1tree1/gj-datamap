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
SW, SH = 11.693, 8.268                      # A4 가로(목차 슬라이드 비율 1.414). A3로 바꿀 때는 PowerPoint 슬라이드 크기에서 비율 유지 확대
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
def style_run(run, size, bold=False, color=INK, italic=False, font=None):
    f = run.font; f.size = Pt(size); f.bold = bold; f.italic = italic; f.color.rgb = rgb(color); f.name = font or EN
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
            style_run(r, st.get("size", p["size"]), st.get("bold", p["bold"]), st.get("color", p["color"]), st.get("italic", False), st.get("font"))
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

LM, RM = 0.5, 0.5                       # 좌우 여백
CW = SW - LM - RM                       # 본문 폭 10.693in
DARK = "#070707"                        # 목차·구분·표지의 검은 바탕(사용자 목차 슬라이드)
FG2, FG3 = "#D9D9D9", "#8F8F8F"          # 검은 바탕 위 보조 글자색

def title_block(slide, label, title, sub=None, title_color=INK, label_color=RED, w=None):
    w = w or (CW - 2.6)
    text(slide, LM, 0.30, w, 0.26, label, size=10.5, color="#FF0000", bold=False, tag="label")          # v3: 붉은 소제목
    text(slide, LM, 0.54, w, 0.5, title, size=20, bold=True, color=title_color, tag="title:" + title[:12])   # v3: 제목 20pt Bold
    if sub: text(slide, LM, 1.02, CW, 0.3, sub, size=11, color=INK2, tag="sub")

def page_no(slide, n, color=GRAY, dark=False):
    text(slide, SW - RM - 0.8, SH - 0.36, 0.8, 0.24, "%02d" % n, size=9, color=(FG3 if dark else color), align="r", tag="pg")

def scale_tag(slide, label, x=None, y=0.32, w=None, color=GRAY):
    """분석 단위 표시(경주시 / 원도심 / 대상지). 스케일을 섞지 않는다는 규칙을 화면에 드러낸다."""
    w = w or (0.42 + 0.115 * len(label))
    x = (SW - RM - w) if x is None else x
    box_text(slide, x, y, w, 0.25, label, fill=None, line=color, radius=0.12, size=9, color=color, bold=False, align="c", anchor="m", margin=(0.05, 0, 0.05, 0), line_w=0.75, tag="scale")
    return w

def chip(slide, x, y, w, h, label, fill, color="#FFFFFF", size=10.5, bold=True, radius=0.08):
    return box_text(slide, x, y, w, h, label, fill=fill, radius=radius, size=size, color=color, bold=bold, align="c", margin=(0.04, 0.0, 0.04, 0.0))

def source_tag(slide, x, y, w, label, color=GRAY):
    text(slide, x, y, w, 0.25, label, size=10.5, color=color, tag="src")

def photo_credit(slide, x, y, w, h, label):
    """사진·지도 아래쪽에 얹는 출처 띠(슬라이드 하단 주석이 아니라 이미지 크레딧). (x,y,w,h)는 이미지 틀."""
    rect(slide, x, y + h - 0.27, w, 0.27, fill="#000000", alpha=0.5)
    text(slide, x + 0.05, y + h - 0.27, w - 0.1, 0.27, label, size=10.5, color="#FFFFFF", anchor="m", margin=(0.05, 0, 0.05, 0), tag="credit")


# ── 앞부분 제작용 추가 부품 ─────────────────────────────────────────────────────
def photo_credit(slide, x, y, w, h, label, size=8):          # noqa: F811  (A4 크기에 맞춘 출처 띠)
    rect(slide, x, y + h - 0.2, w, 0.2, fill="#000000", alpha=0.55)
    text(slide, x + 0.04, y + h - 0.2, w - 0.08, 0.2, label, size=size, color="#FFFFFF", anchor="m", margin=(0.04, 0, 0.04, 0), tag="credit")

def kpi(slide, x, y, w, h, big, label, desc=None, color=BLUE, fill=TINT, big_size=22, label_size=10.5, desc_size=9, tag="kpi"):
    """v3의 수치 카드: 파란 큰 수치 + 굵은 라벨 + 회색 설명(출처 등급 포함)."""
    rect(slide, x, y, w, h, fill=fill, radius=0.08)
    text(slide, x + 0.13, y + 0.06, w - 0.26, big_size / 72 * 1.35, big, size=big_size, bold=True, color=color, tag=tag + "-n")
    ty = y + 0.06 + big_size / 72 * 1.35
    text(slide, x + 0.13, ty, w - 0.26, 0.22, label, size=label_size, bold=True, tag=tag + "-l")
    if desc: text(slide, x + 0.13, ty + 0.23, w - 0.26, max(0.2, h - (ty - y) - 0.28), desc, size=desc_size, color=INK2, tag=tag + "-d")

def hbars(slide, x, y, rows, label_w, bar_max, vmax, step=0.3, bar_h=0.19, color=BLUE, fmt=None, val_size=9.5, label_size=9.5, hl=None, val_w=0.9, label_color=INK, neg=False):
    """가로 막대(도형). rows=[(라벨, 값)]. hl={행번호: 색}. neg=True면 값이 음수여도 길이는 절댓값."""
    fmt = fmt or (lambda v: format(v, ",.0f"))
    for i, (lab, v) in enumerate(rows):
        yy = y + i * step
        text(slide, x, yy - 0.02, label_w, bar_h + 0.06, lab, size=label_size, color=label_color, anchor="m", tag="hb-l")
        wv = max(0.03, bar_max * abs(v) / vmax)
        rect(slide, x + label_w, yy, wv, bar_h, fill=(hl or {}).get(i, color))
        text(slide, x + label_w + wv + 0.05, yy - 0.02, val_w, bar_h + 0.06, fmt(v), size=val_size, bold=True, anchor="m", tag="hb-v")

def num_chip(slide, x, y, d, n, fill=RED, color="#FFFFFF", size=10):
    return oval(slide, x, y, d, fill, str(n), size=size, color=color, bold=True)

def poly(slide, pts, fill=None, line=None, line_w=1.0, alpha=None, dash=False, closed=True):
    """인치 좌표 꼭짓점 목록으로 자유형 도형. 사진 위에 구역·경계를 얹을 때 쓴다."""
    fb = slide.shapes.build_freeform(Inches(pts[0][0]), Inches(pts[0][1]), scale=1.0)
    fb.add_line_segments([(Inches(px), Inches(py)) for px, py in pts[1:]], close=closed)
    shp = fb.convert_to_shape()
    if fill:
        shp.fill.solid(); shp.fill.fore_color.rgb = rgb(fill)
        if alpha is not None:
            clr = shp.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr")); a = etree.SubElement(clr, qn("a:alpha")); a.set("val", str(int(alpha * 100000)))
    else: shp.fill.background()
    if line:
        shp.line.color.rgb = rgb(line); shp.line.width = Pt(line_w)
        if dash:
            ln = shp.line._get_or_add_ln(); d = etree.SubElement(ln, qn("a:prstDash")); d.set("val", "dash")
    else: shp.line.fill.background()
    _no_shadow(shp)
    return shp

def gray_copy(src, dst, contrast=1.0, brightness=1.0):
    """컬러 이미지를 흑백으로(같은 사진을 '현황'과 '대응'에 쓰는 통영식 색 반전용)."""
    from PIL import ImageEnhance
    im = Image.open(src).convert("L")
    if contrast != 1.0: im = ImageEnhance.Contrast(im).enhance(contrast)
    if brightness != 1.0: im = ImageEnhance.Brightness(im).enhance(brightness)
    im.convert("RGB").save(dst, quality=90); return dst

def panel_head(slide, x, y, w, label, color=INK, size=11.5, rule=True):
    text(slide, x, y, w, 0.28, label, size=size, bold=True, color=color, tag="panel-h")
    if rule: line(slide, x, y + 0.3, x + w, y + 0.3, color, 1.0)

def takeaway(slide, x, y, w, h, lead, body=None, fill=TINT, bar=BLUE, lead_size=11.5, body_size=10):
    """슬라이드의 결론 한 줄(v3의 굵은 결론문 + 보조 문장). 왼쪽에 색 막대."""
    rect(slide, x, y, w, h, fill=fill, radius=0.06); rect(slide, x, y, 0.07, h, fill=bar)
    paras = [dict(text=lead, size=lead_size, bold=True, color=INK, space_after=2)]
    if body: paras.append(dict(text=body, size=body_size, color=INK2))
    text(slide, x + 0.2, y + 0.04, w - 0.35, h - 0.08, paras, anchor="m", tag="takeaway")

def dark_slide(deck): return deck.slide(DARK)
