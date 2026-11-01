"""G1 공간구조 구상도(16:9) — 참고: 키이우 권역 구상(거점 원·주요 축 화살표·우측 설명 박스), 여천역(녹색 숲 띠)
생활 존 3 · 보행녹지축 3 · 차량 주동선 · 거점 5 · 도시 연결 방향
글자: 본문(설명 박스·지도 라벨·범례·부제) 모두 FS = 10 pt(사용자 요청 — 설명 박스 제목 크기에 맞춤), 머리글 제목만 기존 크기"""
from gkit import *
from matplotlib.patches import FancyArrowPatch, Circle, Polygon as MPoly
from shapely.ops import polylabel

FS = 10.0
pg = Page()
pg.header("Masterplan : Spatial Structure", "Spatial Structure", "공간구조 구상도",
          sub="세 개의 생활 존을 동서 선형공원·남북 중앙 보행축·사선 보행축으로 엮고, 구 경주역 어댑티브 리유즈를 남측 거점으로 둔 구조", sub_fs=FS)
EXT = (-330, 740, -60, 1110)
MX, MY, MW, MH = 4, 34, 196, 189
ax = pg.plan_ax(MX, MY, MW, MH, EXT)
context(ax, EXT, fc="#ececea", ec="#e1e1de")
fill(ax, B, fc="#fbfbf9", ec="none", z=1)
for g in S["ROADS"].values(): fill(ax, g, fc="#e3e1dc", z=1.1)
for b in BLD: fill(ax, b["g"], fc="#d2d2ce", ec="#bdbdb8", lw=0.2, z=1.3)
xs, ys = B.exterior.xy; ax.plot(xs, ys, color=RED, lw=0.9, ls=(0, (4, 2)), zorder=6)
LOTG = {l["no"]: l["g"] for l in S["LOTS"]}
PK = {p["key"]: p["g"] for p in S["PARKS"]}
ZONES = [("N", "북측 존 — 공공·정주 거점", unary_union([LOTG[i] for i in (1, 2, 3, 4)] + [PK["A"], PK["B"]]), "#5B7FC0",
          ["공공청사(본관 7층)와 청년·신혼 공공임대주택(판상 8동·5층)의 행정·정주 거점", "북측 근린공원·체육공원, 생활체육관, 청사와 브리지로 이어진 직원 주차장동"]),
         ("C", "중앙 존 — 생활문화·창작", unary_union([LOTG[i] for i in (5, 6, 7, 8)] + [PK["C"]]), "#8E6CC7",
          ["동서 선형공원(40 m)과 남북 중앙 보행축(30 m)이 만나는 교차광장 중심", "공공업무·청년창업, 생활문화·돌봄, 전통공예, 아티스트 레지던시"]),
         ("S", "남측 존 — 역사·관광 관문", unary_union([LOTG[i] for i in (9, 10, 11, 12, 13)]), "#C2643A",
          ["구 경주역 어댑티브 리유즈(역사 존치·유리 지붕 중정)와 근대역사관", "관광객 주출입구 관문광장, 공유주차장·모빌리티 허브"])]
for key, ttl, g, c, bl in ZONES:
    gs = g.buffer(28, join_style=1).buffer(-14, join_style=1)
    for k, a in ((0, 0.17), (10, 0.12), (22, 0.07), (36, 0.04)):
        fill(ax, gs.buffer(k, join_style=1), fc=c, alpha=a, z=2)
    fill(ax, gs, fc="none", ec=c, lw=0.8, z=2.5, alpha=0.8, ls=(0, (1.5, 1.2)))
# 보행녹지축(사이트 밖까지 연장, 끝은 화살촉)
y0b, y1b = S["DBAND"]; GR = "#3DA24B"; ym = (y0b + y1b) / 2
def band(pts, w, c, a=0.55, z=3, head=True):
    ln = LineString(pts)
    fill(ax, ln.buffer(w / 2, cap_style=2), fc=c, alpha=a, z=z)
    if head:
        for (p, q) in ((pts[1], pts[0]), (pts[-2], pts[-1])):
            v_ = np.array(q) - np.array(p); v_ = v_ / np.linalg.norm(v_); n_ = np.array([-v_[1], v_[0]])
            tip = np.array(q) + v_ * w * 0.9
            ax.add_patch(MPoly([tuple(np.array(q) + n_ * w * 0.95), tuple(tip), tuple(np.array(q) - n_ * w * 0.95)], closed=True, fc=c, alpha=a, ec="none", zorder=z))
band([(-250, ym), (660, ym)], 40, GR, 0.55)
band([(271, 250), (271, 860)], 30, "#6BBF59", 0.50)
v = np.array([0.5394, 0.842]); c0 = np.array([131.2, 59.5]) + np.array([-0.842, 0.5394]) * 10.0
band([tuple(c0 - 70 * v), tuple(c0 + 215 * v)], 20, "#8ACB68", 0.55)
def lab(x, y, s_, c, ha="left", rot=0, italic=True):
    ax.text(x, y, s_, fontsize=FS, color=c, fontweight="bold", style="italic" if italic else "normal", ha=ha, va="center", rotation=rot,
            path_effects=halo(2.4), zorder=20)
lab(-320, ym + 46, "동서 선형공원·가로광장(40 m)", "#2b7a35")
lab(292, 662, "남북 중앙 보행축(30 m)", "#2b7a35")
lab(-320, -32, "사선 보행축(20 m) · 관광객 접근", "#2b7a35")
# 차량 주동선(붉은 윤곽 화살표, 키이우 'Main Corridors' 형식)
def car(pts, w=16):
    ln = LineString(pts); g = ln.buffer(w / 2, cap_style=2)
    p, q = np.array(pts[-2]), np.array(pts[-1]); vv = (q - p) / np.linalg.norm(q - p); nn = np.array([-vv[1], vv[0]])
    head = Polygon([tuple(q + nn * w * 1.2), tuple(q + vv * w * 1.6), tuple(q - nn * w * 1.2)])
    fill(ax, unary_union([g, head]), fc="#F6D3D0", ec="#D9443A", lw=1.0, z=4, alpha=0.95)
car([(560, 343.7), (-300, 343.7)]); car([(-300, 343.7 - 0.01), (700, 343.7)])
car([(254, 778.5), (-290, 778.5)]); car([(300, 830), (470, 1030)])
lab(-290, 372, "동서 도로(20 m)", "#B23a32", italic=False)
lab(-285, 806, "북측 차도(13 m)", "#B23a32", italic=False)
# 거점(점선 고리 + 후광 + 중심점)
o_, ua, vb = np.array(S["GLASS"]["o"]), np.array(S["GLASS"]["ua"]), np.array(S["GLASS"]["vb"])
gc = o_ + 48.5 * ua + 10.0 * vb
NODES = [("구 경주역 어댑티브 리유즈", tuple(gc), 46, "#C2643A"), ("교차광장", (271, 496), 30, GR), ("청사 앞 시민광장", (186, 702), 30, "#5B7FC0"),
         ("관문광장(관광객 주출입구)", (118, 68), 30, "#E8833A"), ("모빌리티 허브", (353, 221), 26, "#7d8590")]
for i, (nm, (x, y), r, c) in enumerate(NODES):
    for k, a in ((1.0, 0.30), (0.75, 0.25), (0.5, 0.25)):
        ax.add_patch(Circle((x, y), r * k, fc=c, ec="none", alpha=a, zorder=7))
    ax.add_patch(Circle((x, y), r * 0.62, fc="none", ec="#C8102E", lw=1.0, ls=(0, (1.4, 1.0)), zorder=8))
    ax.add_patch(Circle((x, y), 4.2, fc="#C8102E", ec="white", lw=0.5, zorder=9))
    ax.text(x + r * 0.75, y + r * 0.6, "%d %s" % (i + 1, nm), fontsize=FS, fontweight="bold", color=INK, va="center", path_effects=halo(2.4), zorder=21)
# 연결 방향 라벨
lab(-250, ym - 44, "서측 원도심 방면", "#2b7a35", italic=False)
lab(660, ym - 44, "동측 생활권", "#2b7a35", ha="right", italic=False)
north_scale(ax, 470, -30, fs=FS - 1, north_at=(700, 40))

pg.top()
# ── 우측 설명 박스(키이우 형식) — 영문 꼬리표·제목 한 줄, 본문 10 pt ──
bx, bw = 206, 188
TW = bw - 17.0                                                          # 본문 줄 폭(mm)
LH = 5.0                                                                # 줄 간격(mm)
def wrap_mm(text, width):
    """실제 글자 폭(mm)으로 줄 나눔(어절 단위)"""
    words = text.split(" "); lines, cur = [], ""
    for w_ in words:
        cand = (cur + " " + w_).strip()
        t_ = pg.ax.text(0, 0, cand, fontsize=FS); wd = pg.wmm(t_); t_.remove()
        if wd > width and cur: lines.append(cur); cur = w_
        else: cur = cand
    if cur: lines.append(cur)
    return lines
def content_h(bullets):
    blk = [wrap_mm(b_, TW) for b_ in bullets]
    return blk, 13.0 + sum(LH * len(L) for L in blk) + 1.6 * (len(blk) - 1) + 3.0
def box(yy, h, tag, ttl, blk, ch, fc, bar):
    pg.rect(bx, yy, bw, h, fc=fc, ec="none", z=10); pg.rect(bx, yy, 2.0, h, fc=bar, z=11)          # 밝은 박스(D0·D2a·D3과 같은 형식)
    y0 = yy + (h - ch) / 2                                               # 내용 세로 가운데
    t1 = pg.t(bx + 7, y0 + 7.0, tag, fs=FS, c=bar, bold=True, z=12)
    pg.t(bx + 7 + pg.wmm(t1) + 3.0, y0 + 7.0, ttl, fs=FS, c=INK, bold=True, z=12)
    ly_ = y0 + 14.5
    for L in blk:
        pg.t(bx + 7, ly_, "•", fs=FS, c=INK, z=12)
        for j, ln in enumerate(L): pg.t(bx + 11, ly_ + j * LH, ln, fs=FS, c=INK, z=12)
        ly_ += LH * len(L) + 1.6
ITEMS = [({"N": "North", "C": "Center", "S": "South"}[key], ttl, bl, "#F3F5F8", c, g) for key, ttl, g, c, bl in ZONES]
ITEMS.append(("Network", "보행녹지축 3 · 거점 5", ["동서 선형공원·가로광장 40 m · 남북 중앙 보행축 30 m · 사선 보행축 20 m",
              "구 경주역 어댑티브 리유즈 · 교차광장 · 청사 앞 시민광장 · 관문광장 · 모빌리티 허브"], "#F3F5F8", GR, None))
CB = [content_h(it[2]) for it in ITEMS]
TOP, BOT, GAP = 36.0, 219.0, 4.0
extra = (BOT - TOP - GAP * (len(ITEMS) - 1) - sum(ch for _, ch in CB)) / len(ITEMS)
yy = TOP
for (tag, ttl, bl, fc, bar, g), (blk, ch) in zip(ITEMS, CB):
    h = ch + extra
    box(yy, h, tag, ttl, blk, ch, fc, bar)
    if g is not None:
        cpt = polylabel(max(polys(g), key=lambda p: p.area), 2.0)
        mx, my = pg.mm_of(ax, cpt.x, cpt.y)
        pg.line([bx, bx - 5, mx], [yy + h / 2, yy + h / 2, my], c="#3c4d5e", lw=0.7, z=9)
        pg.ax.add_patch(Circle((mx, my), 1.0, fc="#3c4d5e", ec="white", lw=0.5, zorder=10))
    yy += h + GAP
# 범례(지도 왼쪽 위)
lx, ly = 6, 36
LG = [("band", GR, "보행녹지축(선형공원·보행축)"), ("car", "#D9443A", "차량 주동선"), ("node", "#C8102E", "거점"), ("zone", "#8E6CC7", "생활 존"), ("bound", RED, "구역 경계")]
pg.rect(lx, ly, 76, 9 + len(LG) * 6.2, fc="white", ec="#cccccc", lw=0.4, z=30, alpha=0.95)
pg.t(lx + 3, ly + 4.5, "범례", fs=FS, bold=True, z=31)
for i, (k, c, t) in enumerate(LG):
    y_ = ly + 11 + i * 6.2
    if k == "band": pg.rect(lx + 3, y_ - 1.5, 9, 3.0, fc=c, alpha=0.6, z=31)
    elif k == "car": pg.rect(lx + 3, y_ - 1.5, 9, 3.0, fc="#F6D3D0", ec=c, lw=0.8, z=31)
    elif k == "node":
        pg.ax.add_patch(Circle((lx + 7.5, y_), 2.4, fc="none", ec=c, lw=0.8, ls=(0, (1.2, 0.8)), zorder=31)); pg.ax.add_patch(Circle((lx + 7.5, y_), 0.9, fc=c, zorder=32))
    elif k == "zone": pg.rect(lx + 3, y_ - 1.7, 9, 3.4, fc=c, alpha=0.25, ec=c, lw=0.5, z=31, ls=(0, (1.5, 1.2)))
    else: pg.line([lx + 3, lx + 12], [y_, y_], c=c, lw=0.9, z=31, ls=(0, (4, 2)))
    pg.t(lx + 15, y_, t, fs=FS, z=31)
pg.save("D1_공간구조구상도")
