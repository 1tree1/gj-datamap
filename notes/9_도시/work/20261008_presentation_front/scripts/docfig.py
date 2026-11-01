"""문서 도판 추출 공용 함수 (PDF -> 크롭 PNG/JPG, 접촉 시트).

- 원본 PDF는 읽기만 한다.
- 쪽 번호는 모두 PDF 쪽(1부터)으로 받는다. 인쇄 쪽은 문서마다 오프셋이 다르므로 MANIFEST에 따로 적는다.
- 사용 전: export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
"""
import io
import os
import sys

import pymupdf
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
ROOT = "C:/Users/OFFICE/Desktop/9_도시"
OUTDIR = ROOT + "/work/20261008_presentation_front/assets/doc"

_FONT_CANDIDATES = [
    "C:/Users/OFFICE/AppData/Local/Microsoft/Windows/Fonts/Pretendard-Medium.otf",
    "C:/Users/OFFICE/AppData/Local/Microsoft/Windows/Fonts/Pretendard-Regular.otf",
    "C:/Windows/Fonts/malgun.ttf",
]


def font(size=16):
    for p in _FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


_DOCS = {}


def open_pdf(path):
    if path not in _DOCS:
        _DOCS[path] = pymupdf.open(path)
    return _DOCS[path]


def pix_to_pil(pix):
    mode = "RGB" if pix.n >= 3 else "L"
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)  # drop alpha
    img = Image.frombytes("RGB" if pix.n >= 3 else "L", (pix.width, pix.height), pix.samples)
    return img.convert("RGB")


def render(path, pno, dpi=150, clip=None):
    """pno: 1-based. clip: (x0,y0,x1,y1) in PDF points (page coordinates, rotation-applied page space)."""
    d = open_pdf(path)
    page = d[pno - 1]
    kw = {}
    if clip is not None:
        kw["clip"] = pymupdf.Rect(*clip)
    pix = page.get_pixmap(dpi=dpi, alpha=False, **kw)
    return pix_to_pil(pix)


def embedded_images(path, pno, min_side=150):
    """페이지 임베디드 이미지 목록: (xref, w, h, bbox_on_page)"""
    d = open_pdf(path)
    page = d[pno - 1]
    out = []
    for info in page.get_image_info(xrefs=True):
        w, h = info["width"], info["height"]
        if min(w, h) < min_side:
            continue
        out.append((info.get("xref"), w, h, tuple(round(v, 1) for v in info["bbox"])))
    return out


def extract_xref(path, xref):
    """임베디드 이미지를 원본 해상도 그대로 PIL로 (SMask 합성 포함)."""
    d = open_pdf(path)
    pix = pymupdf.Pixmap(d, xref)
    if pix.colorspace is not None and pix.colorspace.n > 3:  # CMYK 등
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    # SMask
    try:
        info = d.extract_image(xref)
        smask = info.get("smask", 0)
    except Exception:
        smask = 0
    img = pix_to_pil(pix) if not pix.alpha else pix_to_pil(pymupdf.Pixmap(pix, 0))
    if smask:
        try:
            m = pymupdf.Pixmap(d, smask)
            mi = Image.frombytes("L", (m.width, m.height), m.samples)
            if mi.size != img.size:
                mi = mi.resize(img.size)
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=mi)
            img = bg
        except Exception:
            pass
    return img


def contact_sheet(items, cols=4, thumb_w=420, pad=8, label_h=34, bg=(255, 255, 255), fsize=15):
    """items: list of (PIL.Image, label). 반환: PIL.Image"""
    f = font(fsize)
    thumbs = []
    for im, lab in items:
        r = thumb_w / im.width
        t = im.resize((thumb_w, max(1, int(im.height * r))), Image.LANCZOS)
        thumbs.append((t, lab))
    rows = [thumbs[i:i + cols] for i in range(0, len(thumbs), cols)]
    row_h = [max(t.height for t, _ in r) + label_h for r in rows]
    W = cols * (thumb_w + pad) + pad
    H = sum(row_h) + pad * (len(rows) + 1)
    sheet = Image.new("RGB", (W, H), bg)
    dr = ImageDraw.Draw(sheet)
    y = pad
    for r, rh in zip(rows, row_h):
        x = pad
        for t, lab in r:
            sheet.paste(t, (x, y + label_h))
            dr.rectangle([x, y + label_h, x + t.width - 1, y + label_h + t.height - 1], outline=(180, 180, 180))
            dr.text((x + 2, y + 6), lab, fill=(200, 0, 0), font=f)
            x += thumb_w + pad
        y += rh + pad
    return sheet


def save(img, name, fmt=None, quality=92, outdir=None):
    outdir = outdir or OUTDIR
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, name)
    ext = os.path.splitext(name)[1].lower()
    if ext in (".jpg", ".jpeg"):
        img.convert("RGB").save(p, "JPEG", quality=quality, subsampling=0, dpi=(300, 300))
    else:
        img.save(p, "PNG", dpi=(300, 300), optimize=False)
    return p


def words_bbox(path, pno, needle):
    """쪽 안에서 needle 문자열이 있는 영역(Rect 목록)."""
    d = open_pdf(path)
    page = d[pno - 1]
    return page.search_for(needle)


# ---------------------------------------------------------------------------
# 문장 위치 찾기 / 형광펜 / 임베디드 원본 저장
# ---------------------------------------------------------------------------
def _chars(page):
    """쪽의 글자 목록: [(ch, (x0,y0,x1,y1), line_id)] (공백 제외, 읽는 순서)"""
    out = []
    d = page.get_text("rawdict")
    lid = 0
    for b in d["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            lid += 1
            for s in l["spans"]:
                for c in s["chars"]:
                    ch = c["c"]
                    if ch.strip() == "":
                        continue
                    if 0xE000 <= ord(ch) <= 0xF8FF:  # 사설 영역 기호(가운뎃점 등)는 검색에서 제외
                        continue
                    out.append((ch, tuple(c["bbox"]), lid))
    return out


def phrase_rects(path, pno, phrase, occurrence=1):
    """phrase(공백 무시)가 있는 글자 영역을 줄별로 합쳐 Rect 목록으로 돌려준다. 없으면 []."""
    page = open_pdf(path)[pno - 1]
    chars = _chars(page)
    flat = "".join(c[0] for c in chars)
    target = "".join(phrase.split())
    start = -1
    pos = 0
    for _ in range(occurrence):
        start = flat.find(target, pos)
        if start < 0:
            return []
        pos = start + 1
    sel = chars[start:start + len(target)]
    rects = {}
    for ch, bb, lid in sel:
        r = rects.get(lid)
        if r is None:
            rects[lid] = list(bb)
        else:
            r[0] = min(r[0], bb[0]); r[1] = min(r[1], bb[1]); r[2] = max(r[2], bb[2]); r[3] = max(r[3], bb[3])
    return [pymupdf.Rect(*v) for v in rects.values()]


def highlight(img, rects, clip, dpi, color=(255, 232, 107), alpha=0.55, pad=1.5):
    """형광펜 합성(곱하기). img: render(clip, dpi)로 만든 PIL 이미지. rects: 쪽 좌표(pt) Rect 목록."""
    import numpy as np
    base = np.asarray(img.convert("RGB")).astype("float32")
    k = dpi / 72.0
    mask = np.zeros(base.shape[:2], dtype="float32")
    for r in rects:
        x0 = int(round((r.x0 - clip[0] - pad) * k)); x1 = int(round((r.x1 - clip[0] + pad) * k))
        y0 = int(round((r.y0 - clip[1] - pad * 0.6) * k)); y1 = int(round((r.y1 - clip[1] + pad * 0.6) * k))
        x0 = max(0, x0); y0 = max(0, y0); x1 = min(base.shape[1], x1); y1 = min(base.shape[0], y1)
        if x1 > x0 and y1 > y0:
            mask[y0:y1, x0:x1] = 1.0
    col = np.array(color, dtype="float32") / 255.0
    mult = base * col[None, None, :]
    out = base * (1 - alpha * mask[..., None]) + mult * (alpha * mask[..., None])
    return Image.fromarray(np.clip(out, 0, 255).astype("uint8"))


def save_embedded(path, xref, name, outdir=None):
    """임베디드 이미지를 원본 해상도로 저장. JPEG이면 바이트 그대로(재압축 없음), 아니면 디코드 후 PNG/JPG.
    반환: (저장경로, (w,h), 방식)"""
    outdir = outdir or OUTDIR
    os.makedirs(outdir, exist_ok=True)
    d = open_pdf(path)
    info = d.extract_image(xref)
    ext = os.path.splitext(name)[1].lower()
    p = os.path.join(outdir, name)
    if info["ext"] in ("jpeg", "jpg") and ext in (".jpg", ".jpeg") and not info.get("smask") and info.get("colorspace", 3) in (1, 3):
        with open(p, "wb") as f:
            f.write(info["image"])
        return p, (info["width"], info["height"]), "passthrough"
    im = extract_xref(path, xref)
    save(im, name, outdir=outdir)
    return p, im.size, "decoded"


# ---------------------------------------------------------------------------
# MANIFEST 기록 (json에 누적 -> csv로 내보내기)
# ---------------------------------------------------------------------------
import csv
import json

_MAN_JSON = ROOT + "/work/20261008_presentation_front/scripts/doc_manifest.json"
MAN_COLS = ["file", "ID", "설명", "캡션(출처 표기 후보)", "원 PDF 경로", "쪽(PDF/인쇄)", "가로x세로 px", "등급",
            "원문 문장(요지)", "bbox(pt, PDF 쪽 좌표)", "추출 방식·해상도", "비고"]


def record(file, ID, desc, caption, pdf, page, size, grade, sentence="", bbox="", method="", note=""):
    """MANIFEST 항목 하나를 기록(같은 file이면 덮어씀)."""
    data = {}
    if os.path.exists(_MAN_JSON):
        data = json.load(open(_MAN_JSON, encoding="utf-8"))
    rel = pdf.replace("\\", "/")
    if rel.startswith(ROOT + "/"):
        rel = rel[len(ROOT) + 1:]
    data[file] = {
        "file": file, "ID": ID, "설명": desc, "캡션(출처 표기 후보)": caption, "원 PDF 경로": rel,
        "쪽(PDF/인쇄)": page, "가로x세로 px": f"{size[0]}x{size[1]}", "등급": grade,
        "원문 문장(요지)": sentence, "bbox(pt, PDF 쪽 좌표)": bbox, "추출 방식·해상도": method, "비고": note,
    }
    json.dump(data, open(_MAN_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def write_manifest_csv(outdir=None):
    outdir = outdir or OUTDIR
    data = json.load(open(_MAN_JSON, encoding="utf-8"))
    rows = [data[k] for k in sorted(data)]
    p = os.path.join(outdir, "MANIFEST.csv")
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MAN_COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return p, len(rows)


def bbox_str(clip):
    return "(%.1f, %.1f, %.1f, %.1f)" % tuple(clip)
