# -*- coding: utf-8 -*-
"""2차 수정 — 00·01·02 사진·지도 묶음 그림 (PIL). 실행: python figs_rev2_a.py"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
sys.stdout.reconfigure(encoding='utf-8')
R = 'C:/Users/OFFICE/Desktop/9_도시/work/'
OUT = R + '20261015_report/fig/'
PH = 'C:/Users/OFFICE/Desktop/9_도시/경주답사/KakaoTalk_20260917_'
FD = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Windows', 'Fonts')
FB = lambda s: ImageFont.truetype(FD + '/Pretendard-SemiBold.otf', s)
RED = (200, 16, 46)

def photo(code, long=1500):
    im = ImageOps.exif_transpose(Image.open(PH + code + '.jpg')).convert('RGB')
    im.thumbnail((long, long), Image.LANCZOS)
    return im

def fit(im, w, h):
    """중앙 기준으로 w×h로 채워 자르기"""
    return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.5))

def tag(cv, xy, txt, size=44):
    d = ImageDraw.Draw(cv); x, y = xy
    f = FB(size); w = int(d.textlength(txt, font=f)) + 28
    d.rectangle([x, y, x + w, y + size + 18], fill=RED)
    d.text((x + 14, y + 7), txt, font=f, fill='white')

def valid_box(im, thr=232):
    """회색(자료 없음) 여백 제거용 경계 상자"""
    import numpy as np
    a = np.asarray(im.convert('RGB')).astype(int)
    m = ~((abs(a[:, :, 0] - a[:, :, 1]) < 4) & (abs(a[:, :, 1] - a[:, :, 2]) < 4) & (a[:, :, 0] > thr - 10) & (a[:, :, 0] < 245))
    ys, xs = m.nonzero()
    return xs.min(), ys.min(), xs.max(), ys.max()

# ---------- 01_site_photos : 2x2 (폐선 부지 현황)
def site_photos():
    codes = ['091150292', '091150292_04', '091158505_02', '091150292_05']
    labs = ['가', '나', '다', '라']
    W, H, g = 1100, 733, 12
    cv = Image.new('RGB', (W * 2 + g, H * 2 + g), 'white')
    for i, c in enumerate(codes):
        im = fit(photo(c, 2200), W, H)
        x = (i % 2) * (W + g); y = (i // 2) * (H + g)
        cv.paste(im, (x, y)); tag(cv, (x, y), labs[i])
    cv.save(OUT + '01_site_photos.jpg', quality=90); print('01_site_photos', cv.size)

# ---------- 01_aerial_time : 2015 / 2021 / 2024 항공 영상
def aerial_time():
    H = R + '20261008_presentation_front/assets/hist/'
    items = [('ortho_2015_F1.jpg', '2015'), ('ortho_2021_F1.jpg', '2021'), ('aerial_2024_F1.jpg', '2024')]
    tiles = []
    for fn, y in items:
        im = Image.open(H + fn).convert('RGB')
        x0, y0, x1, y1 = valid_box(im)
        tiles.append((im, (x0, y0, x1, y1), y))
    # 공통으로 자료가 있는 영역
    X0 = max(t[1][0] for t in tiles); Y0 = max(t[1][1] for t in tiles)
    X1 = min(t[1][2] for t in tiles); Y1 = min(t[1][3] for t in tiles)
    print('common box', X0, Y0, X1, Y1)
    # 철도 부지(중앙 띠)가 중심이 되도록 가로 폭을 줄인다
    Y0 += 24
    w = 694; X0 = 374; X1 = X0 + w
    g = 16; th = 1500; tw = int((X1 - X0) * th / (Y1 - Y0))
    cv = Image.new('RGB', (tw * 3 + g * 2, th), 'white')
    for i, (im, _, y) in enumerate(tiles):
        t = im.crop((X0, Y0, X1, Y1)).resize((tw, th), Image.LANCZOS)
        cv.paste(t, (i * (tw + g), 0)); tag(cv, (i * (tw + g), 0), y)
    cv.save(OUT + '01_aerial_time.jpg', quality=90); print('01_aerial_time', cv.size)

# ---------- 02_heritage_photos : 대상지 주변 고분·문화유산 경관 (3장)
def heritage_photos():
    codes = ['091052582_02', '091052582_04', '091052582_06']
    W, H, g = 900, 990, 14
    cv = Image.new('RGB', (W * 3 + g * 2, H), 'white')
    for i, c in enumerate(codes):
        im = fit(photo(c, 2200), W, H)
        cv.paste(im, (i * (W + g), 0)); tag(cv, (i * (W + g), 0), ['가', '나', '다'][i])
    cv.save(OUT + '02_heritage_photos.jpg', quality=90); print('02_heritage_photos', cv.size)

# ---------- 02_source_excerpts : 2030 경주도시기본계획 발췌
def excerpts():
    D = R + '20261008_presentation_front/assets/doc/'
    ims = [Image.open(D + f).convert('RGB') for f in
           ['D06_plan30_p299_urban_split_hl.png', 'D06_plan30_p301_station_site_use_hl.png']]
    # 첫 장은 위쪽 절반(분열·저해요인)만, 둘째는 위쪽(이전적지 활용방안)만
    a = ims[0]; b = ims[1].crop((0, 0, ims[1].width, int(ims[1].height * 0.44)))
    w = 1900
    a = a.resize((w, int(a.height * w / a.width))); b = b.resize((w, int(b.height * w / b.width)))
    pad = 30; lab = 70
    cv = Image.new('RGB', (w + pad * 2, a.height + b.height + lab * 2 + pad * 3), 'white')
    d = ImageDraw.Draw(cv)
    f = FB(36); t1 = '인쇄쪽 285 · 도심 및 시가지정비'; t2 = '인쇄쪽 287 · 실천전략'
    d.rectangle([pad, pad, pad + int(d.textlength(t1, font=f)) + 28, pad + lab - 14], fill=RED)
    d.text((pad + 14, pad + 4), t1, font=f, fill='white')
    cv.paste(a, (pad, pad + lab))
    y2 = pad + lab + a.height + pad
    d.rectangle([pad, y2, pad + int(d.textlength(t2, font=f)) + 28, y2 + lab - 14], fill=RED)
    d.text((pad + 14, y2 + 4), t2, font=f, fill='white')
    cv.paste(b, (pad, y2 + lab))
    cv.save(OUT + '02_source_excerpts.png'); print('02_source_excerpts', cv.size)

# ---------- 00 조감·공간구조·위치
def masterplan_axo():
    im = Image.open(R + '20261011_masterplan_rough/sheets/prog7a_axo.png').convert('RGB')
    s = im.width / 2000.0   # 원본 3840x2160, 좌표는 2000폭 기준으로 잡았다
    im.crop((int(140 * s), int(290 * s), int(1860 * s), int(960 * s))).save(OUT + '00_masterplan_axo.png'); print('00_masterplan_axo')

def spatial_structure():
    im = Image.open(R + '20261011_masterplan_rough/diagrams/D1_공간구조구상도.png').convert('RGB')
    im = im.crop((0, int(im.height * 0.145), im.width, im.height))   # 제목 줄 제외
    c = im.resize((3000, int(im.height * 3000 / im.width)), Image.LANCZOS)
    c.save(OUT + '00_spatial_structure.png'); print('00_spatial_structure', c.size)

def site_context():
    H = R + '20261008_presentation_front/assets/hist/'
    a = Image.open(H + 'aerial_2025_F1.jpg').convert('RGB')
    x0, y0, x1, y1 = valid_box(a)
    a = a.crop((x0, y0 + int((y1 - y0) * 0.26), x1, y1))
    W = 1000   # 높이
    left = ImageOps.fit(a, (int(W * 0.56), W), Image.LANCZOS, centering=(0.66, 0.5))
    p1 = fit(photo('091150292', 2000), int(W * 0.9), int(W * 0.5) - 8)
    p2 = fit(photo('091158505_02', 2000), int(W * 0.9), int(W * 0.5) - 8)
    cv = Image.new('RGB', (left.width + 16 + p1.width, W), 'white')
    cv.paste(left, (0, 0)); cv.paste(p1, (left.width + 16, 0)); cv.paste(p2, (left.width + 16, p1.height + 16))
    tag(cv, (0, 0), '가'); tag(cv, (left.width + 16, 0), '나'); tag(cv, (left.width + 16, p1.height + 16), '다')
    cv.save(OUT + '00_site_context.jpg', quality=90); print('00_site_context', cv.size)

if __name__ == '__main__':
    site_photos(); aerial_time(); excerpts(); masterplan_axo(); spatial_structure(); site_context(); heritage_photos()
