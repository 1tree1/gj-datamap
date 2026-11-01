def sub(path, pairs):
    s = open(path, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s: print("MISSING in", path, ":", a[:80])
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8").write(s)

# ── 공통 도우미: qcrop(원문 강조 부분만 잘라 쌓기), credit_below(그림 아래 출처) ─────────────
s = open("front_pages.py", encoding="utf-8").read()
if "def qcrop(" not in s:
    add = '''
def qcrop(src, boxes, name, gap=10):
    """원문 도판에서 필요한 줄(boxes=[(l,t,r,b)])만 잘라 세로로 쌓아 charts/ 에 저장한다."""
    if not src or not have(src): return None
    dst = CH + "\\\\" + name + ".jpg"
    if (not have(dst)) or os.path.getmtime(dst) < os.path.getmtime(src):
        im = Image.open(src).convert("RGB")
        strips = [im.crop(b) for b in boxes]
        W = max(t.width for t in strips); H = sum(t.height for t in strips) + gap * (len(strips) - 1)
        out = Image.new("RGB", (W, H), (255, 255, 255)); y = 0
        for t in strips: out.paste(t, (0, y)); y += t.height + gap
        os.makedirs(CH, exist_ok=True); out.save(dst, quality=92)
    return dst

def credit_below(s, x, y, w, h, label, size=7, lines=1):
    """그림 아래(바깥)에 한 줄 출처. 지도 범례를 가리지 않는다. (x,y,w,h)는 그림 틀."""
    text(s, x, y + h + 0.03, w, 0.16 * lines + 0.02, label, size=size, color=GRAY, anchor="t", line=1.0, tag="credit-b")

'''
    s = s.replace("def tag(t):", add + "def tag(t):", 1)
    open("front_pages.py", "w", encoding="utf-8").write(s)

# ── 03: 출처를 그림 아래로 ──────────────────────────────────────────────────
sub("front_pages.py", [
    ('    photo_credit(s, ix, iy, iw, ih, "국토지리정보원 연속수치지도 · 고시 제2026-8호 도면 [T1·T2]", size=7)',
     '    credit_below(s, ix, iy, iw, ih, "국토지리정보원 연속수치지도 · 경주시 고시 제2026-8호 도면 [T1·T2]")'),
])

# ── 05: 그림 아래 출처, 열 높이 재배치 ─────────────────────────────────────
sub("front_pages_b.py", [
    ('''        iy = 2.12; ih = 2.5
        img, cr = pick(e["c"])
        pic_or_ph(s, img, x, iy, cw, ih, e["name"], align=e["al"])
        photo_credit(s, x, iy, cw, ih, cr, size=6.5)
        text(s, x, iy + ih + 0.1, cw, 0.28, e["head"], size=10, bold=True, color=INK, anchor="m", tag="hs-h")
        text(s, x, iy + ih + 0.4, cw, 1.8, [dict(text=t, size=8.8, color=INK2, bullet=True, space_after=3) for t in e["b"]], line=1.1, tag="hs-b")''',
     '''        iy = 2.12; ih = 2.3
        img, cr = pick(e["c"])
        pic_or_ph(s, img, x, iy, cw, ih, e["name"], align=e["al"])
        credit_below(s, x, iy, cw, ih, cr, size=6.8, lines=2)
        text(s, x, iy + ih + 0.42, cw, 0.28, e["head"], size=10, bold=True, color=INK, anchor="m", tag="hs-h")
        text(s, x, iy + ih + 0.72, cw, 1.7, [dict(text=t, size=8.8, color=INK2, bullet=True, space_after=3) for t in e["b"]], line=1.1, tag="hs-b")'''),
])

# ── 06: 전략계획 원문은 강조한 문단만 크게 ──────────────────────────────────
sub("front_pages_b_social.py", [
    ('''    qimg = DOC + r"\\D06_strat_p26_center_weakening_hl.png"
    if have(qimg):
        qw_, qh_ = Image.open(qimg).size; fw = 2.62; fh = fw * qh_ / qw_
        rect(s, x, 5.92, fw + 0.06, fh + 0.06, fill="#FFFFFF", line="#C7CDD4", line_w=0.75)
        picture(s, qimg, x + 0.03, 5.95, fw, fh, mode="contain")
    else: pic_or_ph(s, None, x, 5.93, 2.9, 0.95, "전략계획 원문 발췌")''',
     '''    qimg = qcrop(DOC + r"\\D06_strat_p26_center_weakening_hl.png", [(0, 0, 1835, 365)], "q_strat_p16")
    if have(qimg):
        qw_, qh_ = Image.open(qimg).size; fw = cw - 0.06; fh = fw * qh_ / qw_
        rect(s, x, 5.92, fw + 0.06, fh + 0.06, fill="#FFFFFF", line="#C7CDD4", line_w=0.75)
        picture(s, qimg, x + 0.03, 5.95, fw, fh, mode="contain")
    else: pic_or_ph(s, None, x, 5.93, 2.9, 0.95, "전략계획 원문 발췌")'''),
])

# ── 07: 출처를 지도 아래로, 2030 계획 원문은 강조한 줄만 ─────────────────────
sub("front_pages_c_structure.py", [
    ('    photo_credit(s, mx, my, mw, mh, "국토지리정보원 연속수치지도 기반 자체 분석 [T2]", size=7)',
     '    credit_below(s, mx, my, mw, mh, "국토지리정보원 연속수치지도 기반 자체 분석 [T2]")'),
    ('qs = [(DOC + r"\\D06_plan30_p299_urban_split_hl.png",', 'qs = [(qcrop(DOC + r"\\D06_plan30_p299_urban_split_hl.png", [(40, 50, 1938, 300), (40, 750, 1938, 930)], "q_plan30_split"),'),
    ('(DOC + r"\\D06_s417_p106_border_vacuum_text_hl.png",', '(qcrop(DOC + r"\\D06_s417_p106_border_vacuum_text_hl.png", [(0, 0, 1338, 330)], "q_s417_vacuum"),'),
])
print("patched11")
