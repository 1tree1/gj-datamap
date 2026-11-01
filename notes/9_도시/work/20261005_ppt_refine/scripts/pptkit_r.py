"""pptkit_r — 통영 보고서(A3 가로, 1190.55×841.89pt)와 같은 규격·서체·크기로 슬라이드를 만드는 python-pptx 도우미. 모든 좌표 단위는 pt.

보고서에서 읽은 규격(2_Report_HR_통영조선소.pdf, 살아 있는 글자 + 픽셀 측정):
  판형 A3 가로 · 좌우 여백 56.7pt · 4단(단폭 248.2, 간격 28)
  경로 라벨  Arial 12.18pt #FF0000            (x 56.7, 상단 y 39.3)
  제목       Arial Bold 20pt #231F20           (x 56.7, 상단 y 56.6)
  국문 제목  KoPub돋움 Medium 15.5pt #6D6E71   ('|' 뒤)   → 이 덱은 국문만 쓰므로 국문 제목을 20pt Bold 로 올린다
  부제       Arial 14pt #231F20                (상단 y 81.6)
  소제목     Arial Bold 12pt 검정
  본문       국문 KoPub돋움 Light 9pt #4D4D4D, 행간 13pt   /   영문 Helvetica Light 약 10pt 검정
  푸터       KoPub돋움 Light 8.41pt #6D6E71 (우측 쪽 우하단) + 쪽번호 Arial 11pt #231F20 (y 808.2)
  장 구분    숫자 165pt #1A77B1(Zaha Hadid Sans) + 장명 Arial Bold 14pt, 우하단
  표지       맑은 고딕 Bold 35pt + Arial 20pt, 중앙
국문 서체: KoPub돋움은 이 PC에 없어 폭이 가장 비슷한 Pretendard(Light/Regular/SemiBold/Bold)로 대신한다(실측: 같은 글에서 +2%)."""
import os, math
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image

PW, PH = 1190.55, 841.89
ML = 56.7; MR = PW - 56.7
COLW, GUT = 248.2, 28.0
COLX = [ML + i * (COLW + GUT) for i in range(4)]
Y_LABEL, Y_TITLE, Y_SUB, Y_TOP, Y_BOT, Y_PAGE = 39.3, 56.6, 81.6, 126.0, 790.0, 808.2

INK, BODY, GRAY, LGRAY, XLGRAY = "#231F20", "#4D4D4D", "#6D6E71", "#BCBEC0", "#D1D3D4"
RED, BLUE, PROB, POT, GREEN = "#FF0000", "#1A77B1", "#EC3C2C", "#2474AC", "#3C8424"
BAND, RULE = "#EBEBEB", "#BCBEC0"
ZN, ZC, ZS, YEL = "#6F9FDC", "#A98BD3", "#F4A0C2", "#F1D247"        # 북·중·남 / 정주(노랑) — 조감도 용도색과 같은 계열

# 서체 역할: (라틴, 동아시아, 굵게)
FONT = {
    "en":   ("Arial", "Pretendard", False),
    "enb":  ("Arial", "Pretendard", True),
    "kl":   ("Pretendard Light", "Pretendard Light", False),
    "kr":   ("Pretendard", "Pretendard", False),
    "km":   ("Pretendard Medium", "Pretendard Medium", False),
    "ksb":  ("Pretendard SemiBold", "Pretendard SemiBold", False),
    "kb":   ("Pretendard", "Pretendard", True),
    "mgb":  ("Malgun Gothic", "Malgun Gothic", True),
}
WARN = []

def E(v): return Emu(int(round(v * 12700)))
def rgb(h): h = h.lstrip("#"); return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
def tint(h, t):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) for i in (0, 2, 4)]; c = [int(round(v * (1 - t) + 255 * t)) for v in c]
    return "#%02x%02x%02x" % tuple(c)

# ── 글자 폭 추정(넘침 경고용). 한글은 Pretendard 기준 0.9em, 영문·숫자 0.55em ───────────────────
def _cw(ch, em, light=True):
    o = ord(ch)
    if o >= 0x3000 or 0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF: return em * 0.92
    if ch == " ": return em * 0.28
    if ch in "·.,'’:;|!il": return em * 0.30
    return em * 0.56
def est_lines(text, width, size):
    n = 0
    for para in str(text).split("\n"):
        w = sum(_cw(c, size) for c in para)
        n += max(1, math.ceil(w * 1.02 / max(width, 4)))
    return n

# ── 서식 ────────────────────────────────────────────────────────────────────
def style_run(run, size, color=INK, font="kl", bold=None):
    lat, ea, b = FONT[font]
    f = run.font; f.size = Pt(size); f.bold = bool(b if bold is None else bold); f.color.rgb = rgb(color); f.name = lat
    rPr = run._r.get_or_add_rPr(); rPr.set("lang", "ko-KR")
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None: el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", ea)

def _norm(paras, d):
    """paras: str | dict | list. dict 키: text|runs, size, color, font, bold, align, line, before, after, bullet"""
    if isinstance(paras, (str, dict)): paras = [paras]
    out = []
    for p in paras:
        if isinstance(p, str): p = dict(text=p)
        q = dict(d); q.update(p); out.append(q)
    return out

ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT, "j": PP_ALIGN.JUSTIFY}
ANCHOR = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}

def fill_tf(tf, paras, margin=(0, 0, 0, 0), anchor="t", **d):
    base = dict(size=9, color=BODY, font="kl", bold=None, align="l", line=None, before=None, after=None, bullet=False)
    base.update(d); ps = _norm(paras, base)
    tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left, tf.margin_top, tf.margin_right, tf.margin_bottom = [E(m) for m in margin]
    tf.vertical_anchor = ANCHOR[anchor]
    for i, p in enumerate(ps):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = ALIGN[p["align"]]
        if p["line"]: para.line_spacing = Pt(p["line"])
        if p["before"] is not None: para.space_before = Pt(p["before"])
        if p["after"] is not None: para.space_after = Pt(p["after"])
        runs = p.get("runs") or [dict(text=p.get("text", ""))]
        for r in runs:
            if isinstance(r, str): r = dict(text=r)
            run = para.add_run(); run.text = r["text"]
            style_run(run, r.get("size", p["size"]), r.get("color", p["color"]), r.get("font", p["font"]), r.get("bold", p["bold"]))
        if p["bullet"]:
            pPr = para._p.get_or_add_pPr(); ind = p["bullet"] if isinstance(p["bullet"], (int, float)) and not isinstance(p["bullet"], bool) else 9
            pPr.set("marL", str(int(E(ind)))); pPr.set("indent", str(-int(E(ind))))
            for t in ("a:buNone", "a:buChar", "a:buAutoNum"):
                for el in pPr.findall(qn(t)): pPr.remove(el)
            bf = etree.SubElement(pPr, qn("a:buFont")); bf.set("typeface", "Arial")
            bu = etree.SubElement(pPr, qn("a:buChar")); bu.set("char", "•")
    return ps

def _plain(p): return p.get("text") if p.get("text") is not None else "".join(r if isinstance(r, str) else r["text"] for r in p.get("runs", []))

def tb(slide, x, y, w, h, paras, margin=(0, 0, 0, 0), anchor="t", tag="", **d):
    shp = slide.shapes.add_textbox(E(x), E(y), E(w), E(h))
    ps = fill_tf(shp.text_frame, paras, margin, anchor, **d)
    est = 0
    for p in ps:
        ln = p["line"] or p["size"] * 1.2
        est += est_lines(_plain(p), w - margin[0] - margin[2] - (9 if p["bullet"] else 0), p["size"]) * ln + (p["before"] or 0) + (p["after"] or 0)
    est += margin[1] + margin[3]
    if est > h * 1.06 + 1: WARN.append("넘침? [%s] 추정 %.0f pt > 상자 %.0f pt : %s" % (tag, est, h, _plain(ps[0])[:24]))
    return shp

def _no_shadow(shape):
    spPr = shape._element.spPr
    if spPr.find(qn("a:effectLst")) is None: etree.SubElement(spPr, qn("a:effectLst"))

def rect(slide, x, y, w, h, fill=None, line=None, lw=0.5, shape=None, alpha=None, radius=None, dash=None):
    shp = slide.shapes.add_shape(shape or (MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE), E(x), E(y), E(w), E(h))
    if radius and shp.adjustments is not None and len(shp.adjustments): shp.adjustments[0] = min(0.5, radius / min(w, h))
    if fill: shp.fill.solid(); shp.fill.fore_color.rgb = rgb(fill)
    else: shp.fill.background()
    if line:
        shp.line.color.rgb = rgb(line); shp.line.width = Pt(lw)
        if dash:
            ln = shp.line._get_or_add_ln(); d = etree.SubElement(ln, qn("a:prstDash")); d.set("val", dash)
    else: shp.line.fill.background()
    if alpha is not None and fill:
        clr = shp.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr")); a = etree.SubElement(clr, qn("a:alpha")); a.set("val", str(int(alpha * 100000)))
    _no_shadow(shp); shp.text_frame.text = ""
    return shp

def oval(slide, x, y, d, fill=None, line=None, lw=0.75, alpha=None):
    return rect(slide, x, y, d, d, fill=fill, line=line, lw=lw, shape=MSO_SHAPE.OVAL, alpha=alpha)

def line(slide, x1, y1, x2, y2, color=RULE, lw=0.5, dash=None):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
    c.line.color.rgb = rgb(color); c.line.width = Pt(lw)
    if dash:
        ln = c.line._get_or_add_ln(); d = etree.SubElement(ln, qn("a:prstDash")); d.set("val", dash)
    return c

def picture(slide, path, x, y, w, h, mode="cover", align=(0.5, 0.5), shape=None, border=None, bw=0.75):
    """mode: contain | cover(틀을 채우고 넘치는 쪽은 자름). shape='oval' 이면 원형(정사각 틀 권장)."""
    iw, ih = Image.open(path).size
    if mode == "contain":
        s = min(w / iw, h / ih); pw, ph = iw * s, ih * s
        pic = slide.shapes.add_picture(path, E(x + (w - pw) * align[0]), E(y + (h - ph) * align[1]), E(pw), E(ph))
    else:
        pic = slide.shapes.add_picture(path, E(x), E(y), E(w), E(h))
        af, ai = w / h, iw / ih
        if ai > af:
            tot = 1 - af / ai; pic.crop_left = tot * align[0]; pic.crop_right = tot * (1 - align[0])
        else:
            tot = 1 - ai / af; pic.crop_top = tot * align[1]; pic.crop_bottom = tot * (1 - align[1])
    if shape == "oval": pic.auto_shape_type = MSO_SHAPE.OVAL
    if border: pic.line.color.rgb = rgb(border); pic.line.width = Pt(bw)
    return pic

def notes(slide, txt): slide.notes_slide.notes_text_frame.text = txt

# ── 표(보고서 p.18 형식: 연한 회색 띠 행, 가는 회색 구분선, 열 사이 흰 간격) ──────────────────────
def _cell_border(cell, **sides):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for el in tcPr.findall(qn(tag)): tcPr.remove(el)
    made = []
    for key, tag in (("l", "a:lnL"), ("r", "a:lnR"), ("t", "a:lnT"), ("b", "a:lnB")):
        spec = sides.get(key); ln = etree.Element(qn(tag))
        if spec is None: ln.set("w", "0"); etree.SubElement(ln, qn("a:noFill"))
        else:
            col, wpt = spec; ln.set("w", str(int(Pt(wpt)))); ln.set("cap", "flat"); ln.set("cmpd", "sng")
            sf = etree.SubElement(ln, qn("a:solidFill")); c = etree.SubElement(sf, qn("a:srgbClr")); c.set("val", col.lstrip("#"))
        made.append(ln)
    for i, ln in enumerate(made): tcPr.insert(i, ln)

def table(slide, x, y, col_w, rows, row_h=22.5, hdr_h=None, size=9, align=None, header=True, hdr_fill=None, hdr_color=INK, shade=(), fills=None, font="kl",
          gap=5.0, bold_cols=(), valign="m", pad=(4, 1.5), rule=RULE, tag="", color=BODY, hdr_font="ksb", row_hs=None):
    """rows[0] 은 머리글. shade: 회색 띠 행 번호. 셀은 str 또는 dict(text, color, bold, fill, align, font, size)."""
    nr, nc = len(rows), len(col_w)
    shp = slide.shapes.add_table(nr, nc, E(x), E(y), E(sum(col_w)), E(row_h * nr))
    tbl = shp._element.graphic.graphicData.tbl; tblPr = tbl.tblPr
    tblPr.set("firstRow", "0"); tblPr.set("bandRow", "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is None: sid = etree.SubElement(tblPr, qn("a:tableStyleId"))
    sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"
    t = shp.table; align = align or ["l"] * nc
    for j, wv in enumerate(col_w): t.columns[j].width = E(wv)
    for i, r in enumerate(rows):
        rh = (row_hs[i] if row_hs else (hdr_h if (i == 0 and header and hdr_h) else row_h))
        t.rows[i].height = E(rh)
        for j in range(nc):
            cell = t.cell(i, j); v = r[j] if j < len(r) else ""; st = {}
            if isinstance(v, dict): st = v; v = st.get("text", "")
            is_h = header and i == 0
            fc = st.get("fill") or (hdr_fill if is_h else ((BAND if i in shade else None) if not fills else fills.get(i)))
            if fc: cell.fill.solid(); cell.fill.fore_color.rgb = rgb(fc)
            else: cell.fill.background()
            cell.margin_left = cell.margin_right = E(pad[0]); cell.margin_top = cell.margin_bottom = E(pad[1])
            cell.vertical_anchor = ANCHOR[valign]
            tf = cell.text_frame; tf.word_wrap = True
            fnt = st.get("font", hdr_font if is_h else ("kb" if j in bold_cols else font))
            fill_tf(tf, [dict(text=str(v))], (pad[0], pad[1], pad[0], pad[1]), valign, size=st.get("size", size), color=st.get("color", hdr_color if is_h else color),
                    font=fnt, bold=st.get("bold"), align=st.get("align", align[j]), line=None)
            b = dict(b=(rule, 0.5))
            if gap and nc > 1: b["l"] = ("#FFFFFF", gap / 2); b["r"] = ("#FFFFFF", gap / 2)
            _cell_border(cell, **b)
    return shp

# ── 덱 ──────────────────────────────────────────────────────────────────────
class Deck:
    def __init__(self):
        self.prs = Presentation(); self.prs.slide_width = Emu(15120000); self.prs.slide_height = Emu(10692000); self.n = 0
    def slide(self, bg="#FFFFFF"):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6]); self.n += 1
        s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(bg); s._pgno = self.n; return s
    def save(self, path): self.prs.save(path)

# ── 보고서 부품 ──────────────────────────────────────────────────────────────
# 상자 안쪽 여백 0 인 글상자에서, 글자 윗선이 보고서의 윗선과 겹치도록 하는 보정(pt). calib.py 로 PowerPoint 렌더를 PDF 와 맞춰 정한다.
DY = dict(label=0.4, title=0.66, sub=0.77, page=0.5, foot=-0.6)        # calib.py 로 측정(PDF 대비 PPT 오차 0.3pt 이내)

def header(slide, label, title, sub=None, dark=False):
    """보고서 왼쪽 쪽 헤더: 적색 경로 라벨 / 굵은 제목 / 부제"""
    tc = "#FFFFFF" if dark else INK
    tb(slide, ML, Y_LABEL + DY["label"], 700, 18, label, size=12.18, color=RED, font="en", tag="label")
    tb(slide, ML, Y_TITLE + DY["title"], 1000, 28, title, size=20, color=tc, font="enb", tag="title")
    if sub: tb(slide, ML, Y_SUB + DY["sub"], 1000, 20, sub, size=14, color=tc, font="en", tag="sub")

FOOT_TEXT = "구 경주역 도시재생 마스터플랜  |  건축디자인6 STUDIO B"
def page_footer(slide, n, style=None, on_photo=False):
    """짝수 쪽: 좌하단 쪽번호 / 홀수 쪽: 우하단 푸터 글 + 쪽번호(사진 위에서는 흰색·연회색)."""
    right = (n % 2 == 1) if style is None else (style == "right")
    c_no = "#FFFFFF" if on_photo else INK; c_ft = LGRAY if on_photo else GRAY
    if right:
        tb(slide, 808, Y_PAGE + 3.4 + DY["foot"], 305.5, 14, FOOT_TEXT, size=8.41, color=c_ft, font="kl", align="r", tag="foot")
        tb(slide, 1121.8 - 40, Y_PAGE + DY["page"], 52.1, 18, str(n), size=11, color=c_no, font="en", align="r", tag="pg")
    else:
        tb(slide, ML, Y_PAGE + DY["page"], 60, 18, str(n), size=11, color=c_no, font="en", tag="pg")
