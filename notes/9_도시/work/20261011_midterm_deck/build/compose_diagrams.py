# -*- coding: utf-8 -*-
"""라이노 캡처(rhino_cap/*.png + anchors_*.json) → 라벨·화살표·범례를 얹은 다이어그램 PNG(assets/diag_*.png)"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont
from diag_palette import *
CAP = 'rhino_cap'; OUT = 'assets'
def font(sz, bold=True): return ImageFont.truetype(FONT_B if bold else FONT_R, sz)
def hexrgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def lighten(im, k=0.62):
    # 맥락 캡처: 투명 배경 유지하며 색을 흰색 쪽으로 k만큼 섞는다
    r, g, b, a = im.split(); from PIL import ImageChops
    white = Image.new('L', im.size, 255)
    mix = lambda ch: Image.blend(ch, white, k)
    return Image.merge('RGBA', (mix(r), mix(g), mix(b), a))
def load(name, context=None):
    im = Image.open(f'{CAP}/{name}.png').convert('RGBA'); bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    if context:
        ctx = Image.open(f'{CAP}/{context}.png').convert('RGBA'); bg.alpha_composite(lighten(ctx))
    bg.alpha_composite(im); return bg
def crop_to_content(im, pad=40, extra=None):
    a = im.convert('L').point(lambda v: 0 if v > 250 else 255); box = a.getbbox()
    if extra: box = (min(box[0], extra[0]), min(box[1], extra[1]), max(box[2], extra[2]), max(box[3], extra[3]))
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad)); return im.crop(box), box
class Proj:
    def __init__(self, tag):
        a = json.load(open(f'{CAP}/anchors_{tag}.json', encoding='utf-8')); self.a = a; self.o = a['o']; self.ex = a['ex']; self.ey = a['ey']; self.ez = a['ez']; self.X0, self.Y0 = a['origin']; self.off = (0, 0)
    def px(self, x, y, z=0.0):
        u = (x - self.X0) / 100.0; v = (y - self.Y0) / 100.0; w = z / 100.0
        return (self.o[0] + u * self.ex[0] + v * self.ey[0] + w * self.ez[0] - self.off[0], self.o[1] + u * self.ex[1] + v * self.ey[1] + w * self.ez[1] - self.off[1])
def arrow(d, p0, p1, col, w=10, head=34, double=False):
    d.line([p0, p1], fill=col, width=w)
    def head_at(a, b):
        ang = math.atan2(b[1] - a[1], b[0] - a[0]); L = head
        pts = [b, (b[0] - L * math.cos(ang - 0.45), b[1] - L * math.sin(ang - 0.45)), (b[0] - L * math.cos(ang + 0.45), b[1] - L * math.sin(ang + 0.45))]
        d.polygon(pts, fill=col)
    head_at(p0, p1)
    if double: head_at(p1, p0)
def label_box(d, xy, title, sub, col, fs=60, fss=42, anchor='l', pad=20):
    f1, f2 = font(fs), font(fss, False)
    w = max(d.textlength(title, font=f1), d.textlength(sub, font=f2) if sub else 0) + pad * 2 + 62
    h = fs + (fss + 8 if sub else 0) + pad * 2
    x, y = xy
    if anchor == 'r': x -= w
    if anchor == 'c': x -= w / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=(255, 255, 255, 240), outline=(200, 200, 200), width=2)
    d.rectangle([x + pad, y + pad + 10, x + pad + 40, y + pad + 50], fill=hexrgb(col))
    d.text((x + pad + 58, y + pad - 4), title, font=f1, fill=hexrgb(INK))
    if sub: d.text((x + pad + 58, y + pad + fs + 2), sub, font=f2, fill=hexrgb(G4))
    return (x, y, x + w, y + h)
def program_labels(a):
    """같은 프로그램은 합쳐 면적 합·최대 획지의 앵커를 쓴다."""
    g = {}
    for L in a['labels']:
        if L['name'] == '오픈스페이스': continue
        r = g.setdefault(L['name'], dict(name=L['name'], col=L['col'], area=0, best=None))
        r['area'] += L['area']
        if r['best'] is None or L['area'] > r['best']['area']: r['best'] = L
    return list(g.values())
# ---------------- 1) 프로그램 축측 다이어그램 ----------------
def diag_axon_program(tag='axon_sw', out='diag_axon_program.png', site='axon_site', ctx='axon_context'):
    im = load(site, ctx); P = Proj(tag)
    im, box = crop_to_content(im, pad=60); P.off = (box[0], box[1])
    # 캔버스: 좌우 라벨 여백
    MX, MY = 980, 120
    canvas = Image.new('RGBA', (im.width + MX * 2, im.height + MY * 2), (255, 255, 255, 255)); canvas.paste(im, (MX, MY))
    d = ImageDraw.Draw(canvas)
    labs = program_labels(P.a)
    # 좌/우 배분: 앵커 x 기준
    for L in labs: L['pt'] = (L['best']['px'] - P.off[0] + MX, L['best']['py'] - P.off[1] + MY)
    left = sorted([L for L in labs if L['pt'][0] < canvas.width / 2], key=lambda L: L['pt'][1]); right = sorted([L for L in labs if L['pt'][0] >= canvas.width / 2], key=lambda L: L['pt'][1])
    def place(col, side):
        n = len(col);
        if not n: return
        top, bot = MY + 40, canvas.height - MY - 40; step = (bot - top) / max(n, 1); step = min(step, 215)
        y0 = (top + bot) / 2 - step * n / 2
        for i, L in enumerate(col):
            y = y0 + i * step; x = 60 if side == 'l' else canvas.width - 60
            bx = label_box(d, (x, y), L['name'], f"{L['area']:,.0f}㎡ · {NAME2[L['name']][5]}", L['col'], anchor='l' if side == 'l' else 'r')
            ax = bx[2] if side == 'l' else bx[0]; ay = (bx[1] + bx[3]) / 2
            d.line([(ax, ay), (L['pt'][0], L['pt'][1])], fill=hexrgb(INK), width=4); d.ellipse([L['pt'][0] - 12, L['pt'][1] - 12, L['pt'][0] + 12, L['pt'][1] + 12], fill=hexrgb(L['col']), outline=(255, 255, 255), width=4)
    place(left, 'l'); place(right, 'r')
    canvas.convert('RGB').save(f'{OUT}/{out}', quality=92); print('ok', out, canvas.size)
# ---------------- 2) 전략 3패널 ----------------
def strategy_panel(tag, cap, arrows, title, sub, out, RPd, extra=None):
    im = load(cap, 'axon_context'); P = Proj(tag)
    # 부지 경계의 화면 범위 + 여백으로 모든 패널을 같은 틀로 자른다
    xs = [p[0] for p in RPd['U']]; ys = [p[1] for p in RPd['U']]
    pts = [P.px(x, y, z) for x in (min(xs), max(xs)) for y in (min(ys), max(ys)) for z in (0, 20)]
    bx0 = min(p[0] for p in pts); bx1 = max(p[0] for p in pts); by0 = min(p[1] for p in pts); by1 = max(p[1] for p in pts)
    box = (int(max(0, bx0 - 780)), int(max(0, by0 - 260)), int(min(im.width, bx1 + 780)), int(min(im.height, by1 + 230)))
    im = im.crop(box); P.off = (box[0], box[1])
    canvas = im; d = ImageDraw.Draw(canvas)
    for (x0, y0, x1, y1, col, dbl, w) in arrows: arrow(d, P.px(x0, y0, 2), P.px(x1, y1, 2), hexrgb(col), w=w, head=w * 3.2, double=dbl)
    if extra: extra(d, P)
    canvas.convert('RGB').save(f'{OUT}/{out}', quality=92); print('ok', out, canvas.size)
def tlabel(d, P, x, y, z, t, col=RED, fs=58, ha='l'):
    p = P.px(x, y, z); f = font(fs); w = d.textlength(t, font=f)
    x0 = p[0] - (w / 2 if ha == 'c' else (w if ha == 'r' else 0))
    d.rounded_rectangle([x0 - 14, p[1] - 10, x0 + w + 14, p[1] + fs + 10], radius=10, fill=(255, 255, 255, 235)); d.text((x0, p[1]), t, font=f, fill=hexrgb(col))
def diag_strategies():
    RPd = json.load(open('data/road_plan_final_plan.json', encoding='utf-8')); S = json.load(open('data/road_plan_final_summary.json', encoding='utf-8'))
    xs = [p[0] for p in RPd['U']]; ys = [p[1] for p in RPd['U']]; xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    NSx = (1167373 + 1167403) / 2; EWy = (1761576 + 1761616) / 2; HWy = 1761446
    # CONNECT: 동서 횡단(선형공원·화랑로) + 남북 보행축
    con = [(xmin - 260, EWy, xmax + 260, EWy, RED, True, 22), (xmin - 260, HWy, xmax + 260, HWy, G4, True, 14), (NSx, ymin - 200, NSx, ymax + 200, RED, True, 22)]
    for yy in (1761734, 1761880): con.append((xmin - 200, yy, xmax + 200, yy, DARK, True, 10))
    def conlab(d, P):
        tlabel(d, P, xmax + 150, EWy + 10, 0, '동서 선형공원 40m', RED, 84); tlabel(d, P, xmax + 40, HWy - 70, 0, '화랑로 연결 · 차량 12m', G4, 66)
        tlabel(d, P, NSx, ymax + 240, 0, '남북 보행축 30m', RED, 84, 'c'); tlabel(d, P, xmin - 120, 1761880, 0, '향일문 조망로', DARK, 60, 'r')
    strategy_panel('axon_sw', 'axon_connect', con, 'CONNECT', '', 'diag_strategy_connect.png', RPd, conlab)
    # EXCHANGE: 중앙 접점 — 원 표시
    def ring(d, P):
        c = P.px((xmin + xmax) / 2, (1761434 + 1761616) / 2, 0); r = 360
        d.ellipse([c[0] - r, c[1] - r * 0.6, c[0] + r, c[1] + r * 0.6], outline=hexrgb(RED), width=20)
        tlabel(d, P, (xmin + xmax) / 2, 1761380, 0, '구 역사 · 광장 · 창작 · 체험 · 시장 접점', RED, 76, 'c')
    strategy_panel('axon_sw', 'axon_exchange', [], 'EXCHANGE', '중앙에서 방문객과 주민이 만나고 방문 지출이 주민 소득으로 이어집니다', 'diag_strategy_exchange.png', RPd, ring)
    # SPREAD: 북측 → 성동시장(서) · 행복황촌(동) 확산 화살표
    spr = [((xmin + xmax) / 2, 1761800, xmin - 420, 1761560, INK, False, 20), ((xmin + xmax) / 2, 1761800, xmax + 420, 1761520, INK, False, 20), ((xmin + xmax) / 2, 1761800, (xmin + xmax) / 2, ymax + 330, G4, False, 14)]
    def names(d, P):
        tlabel(d, P, xmin - 300, 1761560, 0, '성동시장', INK, 84, 'r'); tlabel(d, P, xmax + 300, 1761520, 0, '행복황촌', INK, 84, 'l'); tlabel(d, P, (xmin + xmax) / 2, ymax + 350, 0, '북천 · 황성공원', G4, 70, 'c')
        tlabel(d, P, (xmin + xmax) / 2, 1761800, 24, '저녁 이후에도 남는 사람', RED, 70, 'c')
    strategy_panel('axon_sw', 'axon_spread', spr, 'SPREAD', '북측 일자리·주거·청사가 저녁 이후 사람을 남기고 활동을 주변으로 내보냅니다', 'diag_strategy_spread.png', RPd, names)
# ---------------- 3) 평면 프로그램 다이어그램 ----------------
def diag_top_program():
    im = load('top', 'top_context'); P = Proj('top'); im, box = crop_to_content(im, pad=40); P.off = (box[0], box[1])
    d = ImageDraw.Draw(im); labs = program_labels(P.a)
    for L in labs:
        p = (L['best']['px'] - P.off[0], L['best']['py'] - P.off[1]); f = font(30)
        t = L['name']; w = d.textlength(t, font=f) + 24
        d.rounded_rectangle([p[0] - w / 2, p[1] - 24, p[0] + w / 2, p[1] + 24], radius=8, fill=(255, 255, 255, 225)); d.text((p[0] - w / 2 + 12, p[1] - 20), t, font=f, fill=hexrgb(INK))
    im.convert('RGB').save(f'{OUT}/diag_top_program.png', quality=92); print('ok diag_top_program', im.size)
# ---------------- 4) 범례 ----------------
def legend():
    rows = [p for p in PROG if p[4] != 'O'] + [('', '오픈스페이스 · 보행공간', '#E2E2E2', 0, '', ''), ('', '차량 가로', '#6E6E6E', 0, '', '')]
    H = 70 * len(rows) + 40; im = Image.new('RGB', (760, H), 'white'); d = ImageDraw.Draw(im)
    for i, p in enumerate(rows):
        y = 20 + i * 70; d.rectangle([20, y + 8, 70, y + 52], fill=hexrgb(p[2])); d.text((90, y + 6), p[1], font=font(36), fill=hexrgb(INK))
        if p[5]: d.text((560, y + 12), f"{p[5]} · {p[3]:.0f}m", font=font(28, False), fill=hexrgb(G4))
    im.save(f'{OUT}/diag_legend.png'); print('ok legend')
if __name__ == '__main__':
    diag_axon_program('axon_sw', 'diag_axon_program.png'); diag_axon_program('axon_nw', 'diag_axon_program_nw.png', 'axon_nw', 'axon_nw_context')
    diag_strategies(); diag_top_program(); legend()
