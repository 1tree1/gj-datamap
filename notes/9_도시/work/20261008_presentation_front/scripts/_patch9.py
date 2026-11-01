import re
def sub(path, pairs):
    s = open(path, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s: print("MISSING in", path, ":", a[:70])
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8").write(s)

# ── vimg: 무자료 띠 자동 검출 ────────────────────────────────────────────────
s = open("front_pages.py", encoding="utf-8").read()
a = s.index("def vimg(")
b = s.index("def pick(")
new_vimg = '''def vimg(path, gray=False, contrast=1.05, brightness=1.08, ratio=0.75):
    """사진에서 단색(무자료) 가장자리 띠를 잘라 내고 3:4(가로:세로)로 중앙 맞춤한 사본을 charts/ 에 만든다."""
    if not path or not have(path): return None
    base = os.path.splitext(os.path.basename(path))[0]
    dst = CH + "\\\\" + base + ("_vg" if gray else "_v") + ".jpg"
    if (not have(dst)) or os.path.getmtime(dst) < os.path.getmtime(path):
        from PIL import ImageEnhance
        import numpy as np
        im = Image.open(path).convert("RGB"); a = np.asarray(im); W, H = im.size
        rs = a.reshape(H, -1).std(axis=1)
        top = 0
        while top < H - 1 and rs[top] < 1.0: top += 1
        bot = H
        while bot > top + 1 and rs[bot - 1] < 1.0: bot -= 1
        cs = a[top:bot].transpose(1, 0, 2).reshape(W, -1).std(axis=1)
        l = 0
        while l < W - 1 and cs[l] < 1.0: l += 1
        r = W
        while r > l + 1 and cs[r - 1] < 1.0: r -= 1
        h = bot - top; w = r - l
        if w / h > ratio:
            nw = int(round(h * ratio)); l += (w - nw) // 2; w = nw
        else:
            nh = int(round(w / ratio)); top += (h - nh) // 2; h = nh
        im = im.crop((l, top, l + w, top + h))
        if gray:
            im = ImageEnhance.Contrast(im.convert("L")).enhance(contrast); im = ImageEnhance.Brightness(im).enhance(brightness).convert("RGB")
        os.makedirs(CH, exist_ok=True); im.save(dst, quality=92)
    return dst

'''
s = s[:a] + new_vimg + s[b:]
open("front_pages.py", "w", encoding="utf-8").write(s)

# ── 03 대상지 개요: 왼쪽 도판을 경계·치수 지도(m7)로 ─────────────────────────
sub("front_pages.py", [
    ('''    ix, iy, iw = LM, 1.5, 4.3; ih = 6.33
    img = vimg(first(HI + r"\\ortho_2025_F1_outline.jpg", HI + r"\\ortho_2025_F1.jpg"))
    pic_or_ph(s, img, ix, iy, iw, ih, "2025 정사영상 + 본 계획 경계")
    photo_credit(s, ix, iy, iw, ih, "국토지리정보원 2025 정사영상 · 붉은 선은 본 계획 경계(218,478㎡)")''',
     '''    ix, iy, iw = LM, 1.5, 4.3; ih = iw * 4 / 3
    img = first(MP + r"\\m7_boundaries.png", vimg(first(HI + r"\\ortho_2025_F1_outline.jpg", HI + r"\\ortho_2025_F1.jpg")))
    pic_or_ph(s, img, ix, iy, iw, ih, "고시 구역과 본 계획 경계")
    photo_credit(s, ix, iy, iw, ih, "국토지리정보원 연속수치지도 · 고시 제2026-8호 도면 [T1·T2]", size=7)'''),
])

# ── 05 경주의 역사 ─────────────────────────────────────────────────────────
sub("front_pages_b.py", [
    ('"발굴된 신라 도로는 진북 정렬이며, 현재 가로의 57%도 같은 방위(N0.8°E) [T3·T2]"', '"발굴된 신라 도로는 정북 방향이고, 현재 가로의 57%도 같은 방위(N0.8°E)입니다 [T3·T2]"'),
    ('"여러 시대의 가로와 유적이 같은 방위·같은 틀 위에 이어 쌓인 원도심에서, 철도 용지만이 이 틀을 가르는 선형 장벽으로 남았습니다."', '"여러 시대의 가로와 유적이 같은 방위와 틀 위에 이어서 쌓인 원도심에서, 철도 용지는 이 틀과 맞지 않는 남북 방향의 선형 장벽으로 남아 있습니다."'),
    ('"폐역 이후 이 땅은 축구장 약 22개 규모의 연속 공지가 되었고, 활용 방식에 따라 원도심의 연결 구조를 바꿀 수 있는 계기입니다. 다음 쪽부터 현재의 문제를 사회와 도시구조 측면에서 확인합니다."', '"폐역 이후 이 땅은 축구장 약 22개 규모의 연속 공지가 되었고, 활용 방식에 따라 원도심의 연결 구조가 달라질 수 있습니다. 다음 쪽부터 현재의 문제를 사회와 도시구조 측면에서 확인합니다."'),
])

# ── 06 사회적 문제 ─────────────────────────────────────────────────────────
sub("front_pages_b_social.py", [
    ('dict(text="폐역 구역의 주거 인구는 27명, 직장 인구는 117명입니다.", size=9.5, bold=True, space_after=2)', 'dict(text="폐역 구역의 주거 인구는 27명, 직장 인구는 117명으로 추정됩니다.", size=9.3, bold=True, space_after=2)'),
    ('dict(text="시청 반경 500m만 주거(9,145명)와 직장(8,374명)이 균형을 이루고 저녁 비중이 가장 높습니다. 20~34세는 6년간 7,249명 순유출 [T2].", size=8.5, color=INK2)', 'dict(text="시청 반경 500m만 주거(9,145명)와 직장(8,374명)이 균형을 이루고 저녁 비중이 가장 높습니다. 경주시 20~34세는 2020~2025년 7,249명 순유출입니다(연도별 −1,951명에서 −349명으로 감소) [T2].", size=8.3, color=INK2)'),
])

# ── 11·12 제목 ─────────────────────────────────────────────────────────────
sub("front_pages_d.py", [
    ('"설계방향 : 문제 인식과 대응", "문제에 대한 대응"', '"설계방향 : 문제 인식과 대응", "문제 대응"'),
])

# ── 14·15 제목(대시 제거, 라벨은 목차 용어) ───────────────────────────────
sub("front_pages_e.py", [
    ('"설계방향 : 개발전략", "개발전략 — 공간 전략"', '"설계방향 : 개발전략", "공간 전략"'),
    ('"설계방향 : 개발전략", "개발전략 — 단계와 운영"', '"설계방향 : 개발전략", "단계와 운영"'),
    ('"종사자 −23.1% · 시청 반경 500m만 주거·직장 균형 · 5단계 상위계획의 행정복합타운 [T1·T2]"', '"종사자 −23.1%(사업지 격자) · 시청 반경 500m만 주거·직장 균형 · 상위계획 5건이 행정복합타운을 제시 [T1·T2]"'),
])
print("patched9")
