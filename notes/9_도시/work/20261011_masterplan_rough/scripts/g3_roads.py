"""G3 도로·보행 계획도 + 도로계획표(16:9) — 참고: 이전 'Road Plan + Road Schedule' 시트(위계별 색 평면 + 도로 성격·폭·연장·면적·단면 표)
단면 구성은 도면에서 읽은 폭(차도 폴리곤 폭, 맞닿은 보도 띠 폭, 가로수 열 위치)만 쓴다 — 차로 수 등 세부는 미정"""
from gkit import *
from matplotlib.patches import FancyArrowPatch
from shapely.ops import polylabel


def length_of(g, w=None):
    """띠 모양 연장 = 면적 ÷ 평균폭, 평균폭 = 4 × (면 안 점에서 외곽선까지 평균 거리) — 경계선 굴곡에 덜 민감"""
    from scipy import ndimage
    import shapely
    x0, y0, x1, y1 = g.bounds; st = 0.5
    X, Y = np.meshgrid(np.arange(x0, x1, st) + st / 2, np.arange(y0, y1, st) + st / 2)
    m = np.pad(shapely.contains_xy(g, X.ravel(), Y.ravel()).reshape(X.shape), 3)   # 둘레 여백(바탕 0) — 띠가 격자를 꽉 채울 때 거리 오류 방지
    d = ndimage.distance_transform_edt(m) * st
    w_ = 4.0 * d[m].mean()
    return g.area / w_


OPEN = {o["key"]: o for o in S["OPEN"]}
R = S["ROADS"]
NET = [
    # key, 구분, 이름, 성격, 폭, geom, 색, 단면[(라벨, 폭, 색)], 역할
    ("EW", "차량", "동서 도로", "간선 접속 도로", "20", R["EW"], "#636363", [("보도", 5, "#d9d9d6"), ("차도", 20, "#636363"), ("보도", 5, "#d9d9d6")], "동서 도시 가로 연결, 북측·남측 구역 경계"),
    ("N", "차량", "북측 진입도로", "진입 도로", "13", R["N"], "#636363", [("보도", 5, "#d9d9d6"), ("차도", 13, "#636363"), ("보도", 5, "#d9d9d6")], "서측 진입·북동 연결, 공공청사·주차장동 접근"),
    ("O", "차량", "동측·남측 외곽도로", "외곽 순환·서비스 도로", "가변", R["O"], "#636363", [("보도", 8, "#d9d9d6"), ("차도", 10, "#636363")], "공유주차장·모빌리티 허브 접근, 동측 경계 순환"),
    ("D", "보행", "동서 선형공원·가로광장", "보행자전용도로(선형공원)", "40", OPEN["D"]["g"], "#3DA24B", [("식재", 12, "#9fd67c"), ("가로광장", 16, "#efe8d6"), ("식재", 12, "#9fd67c")], "원도심 방면–동측 생활권 녹색 띠, 가로수 4열"),
    ("E", "보행", "남북 중앙 보행축", "보행자전용도로", "30", OPEN["E"]["g"], "#E8833A", [("식재", 7, "#9fd67c"), ("보행", 16, "#efe8d6"), ("식재", 7, "#9fd67c")], "북측 공공청사–남측 구 경주역 중심축"),
    ("F", "보행", "관문광장·사선 보행축", "보행자전용도로·광장", "20", OPEN["F"]["g"], "#D9577E", [("식재", 6, "#9fd67c"), ("보행", 8, "#efe8d6"), ("식재", 6, "#9fd67c")], "관광객 주출입구–중앙 보행축 진입 동선"),
    ("P8", "보행", "향일문 조망로", "보행자전용도로(조망)", "8", S["PATH8"], "#9B7FD1", [("보행", 8, "#efe8d6")], "가구 사이 동서 보행, 서측 경주읍성 향일문 조망"),
    ("W", "보도", "외곽 보도", "보도", "가변", S["WALK"], "#BDBDBD", [("보도", 5, "#d9d9d6")], "구역 외곽·가구 둘레 보행"),
]

pg = Page()
pg.header("Masterplan : Street Network", "Road Plan + Road Schedule", "도로·보행 계획도 + 도로계획표",
          sub="차량 도로 3 · 보행자전용도로 4 · 외곽 보도 — 형상은 사용자 확정 객체 그대로, 폭·연장 단위 m")
EXT = (40, 480, 30, 1030)
ax = pg.plan_ax(4, 31, 150, 192, EXT)
context(ax, EXT, fc="#eeeeec", ec="#e0e0dd")
for l in S["LOTS"]: fill(ax, l["g"], fc="#fbfbfa", ec="#d6d6d2", lw=0.4, z=1.2)
for p in S["PARKS"]: fill(ax, p["g"], fc="#e3f0d6", z=1.25)
for b in BLD: fill(ax, b["g"], fc="#dcdcd8", ec="#c4c4c0", lw=0.25, z=1.3)
for key, kind, nm, ch, w, g, c, sec, role in NET:
    fill(ax, g, fc=c, ec="white", lw=0.3, z=2.0 if kind != "보도" else 1.9, alpha=0.95 if kind != "보도" else 0.6)
xs, ys = B.exterior.xy; ax.plot(xs, ys, color=RED, lw=0.9, ls=(0, (4, 2)), zorder=6)
# 도로 이름(폭) — 10 pt, 짧은 이름
LBL = [("EW", 255, 352, 0, "동서 도로 20"), ("N", 175, 790, 0, "북측 진입 13"), ("O", 430, 620, 90, "외곽도로"), ("D", 340, 496, 0, "선형공원 40"),
       ("E", 271, 700, 90, "중앙 보행축 30"), ("F", 180, 145, 57, "사선 보행축 20"), ("P8", 190, 652, 0, "조망로 8")]
CL = dict((a[0], a[6]) for a in NET)
for k, x, y, rot, t_ in LBL:
    white = k in ("D", "E", "F")
    ax.text(x, y, t_, fontsize=10, ha="center", va="center", rotation=rot, color="white" if white else INK, fontweight="bold", zorder=12, rotation_mode="anchor",
            path_effects=[pe.withStroke(linewidth=2.0, foreground=shade(CL[k], 0.85))] if white else halo(2.2))
# 진출입·주차
def arrow(p, q, c, lw=1.3, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>,head_length=4,head_width=2.6", color=c, lw=lw, ls=ls, zorder=14, mutation_scale=1.0))
CAR = "#2b3a4a"; WALKA = "#2f8f3a"
ACC = pickle.load(open(os.path.join(D, "access_pts.pkl"), "rb"))     # 실제 도로 필지 접속점(D2a와 같음)
for x, y, k, a in ACC:
    if x < 115: d = np.array([-1.0, 0.0])
    elif y > 860: d = np.array([0.55, 0.83])
    elif x > 395: d = np.array([1.0, 0.0])
    else: d = np.array([0.0, -1.0])
    arrow(tuple(np.array([x, y]) + d * 50), (x, y), CAR, lw=1.6)
for p, q in (((50, 496), (104, 496)), ((470, 496), (406, 496)), ((70, 20), (112, 60))):
    arrow(p, q, WALKA, lw=1.3, ls=(0, (3, 1.6)))
for x, y, t in ((238, 832, "P"), (365, 290, "P"), (145, 621, "P")):
    ax.add_patch(Rectangle((x - 11, y - 11), 22, 22, fc="#2F5F9E", ec="white", lw=0.6, zorder=15)); ax.text(x, y, t, fontsize=10, color="white", ha="center", va="center", fontweight="bold", zorder=16)
ax.add_patch(Circle((353, 221), 13, fc="#F0A030", ec="white", lw=0.6, zorder=15)); ax.text(353, 221, "M", fontsize=10, color="white", ha="center", va="center", fontweight="bold", zorder=16)
north_scale(ax, 270, 55, fs=9, north_at=(455, 125))
pg.top()
# 범례(지도 왼쪽 아래)
leg = [("#636363", "차량 도로"), ("#3DA24B", "선형공원"), ("#E8833A", "중앙 보행축"), ("#D9577E", "사선 보행축"), ("#9B7FD1", "향일문 조망로"), ("#BDBDBD", "외곽 보도"),
       ("P", "주차"), ("M", "모빌리티 허브")]
lx, ly = 5, 219 - 4 - len(leg) * 5.2
pg.rect(lx, ly, 38, 4 + len(leg) * 5.2, fc="white", ec="#cccccc", lw=0.4, z=30, alpha=0.95)
for i, (c, t) in enumerate(leg):
    yy = ly + 4.6 + i * 5.2
    if c == "P": pg.rect(lx + 2.5, yy - 1.6, 3.2, 3.2, fc="#2F5F9E", z=31)
    elif c == "M": pg.ax.add_patch(Circle((lx + 4.1, yy), 1.7, fc="#F0A030", zorder=31))
    else: pg.rect(lx + 2.2, yy - 1.4, 4.2, 2.8, fc=c, z=31)
    pg.t(lx + 8.5, yy, t, fs=10, z=31)

# ── 도로계획표(10 pt) ──
tx = 160
cols = ["도로명", "성격", "폭", "연장", "면적(㎡)", "단면(m, 도면 기준)"]
wd = [46, 52, 14, 16, 24, 84]
xs_ = [tx]
for w in wd: xs_.append(xs_[-1] + w)
RH = 7.4; ty = 30
pg.rect(tx, ty, sum(wd), 6.4, fc="#3c3c3c", z=5)
for i, c in enumerate(cols): pg.t(xs_[i] + wd[i] / 2, ty + 3.2, c, fs=10, c="white", ha="center", bold=True, z=6)
yy = ty + 6.4
sums = {"차량": 0.0, "보행": 0.0, "보도": 0.0}
SHORT = {"EW": "동서 도로", "N": "북측 진입도로", "O": "동·남측 외곽도로", "D": "동서 선형공원", "E": "남북 중앙 보행축", "F": "관문광장·사선 보행축", "P8": "향일문 조망로", "W": "외곽 보도"}
CHS = {"EW": "간선 접속", "N": "진입", "O": "외곽 순환·서비스", "D": "보행자전용(선형공원)", "E": "보행자전용", "F": "보행자전용·광장", "P8": "보행자전용(조망)", "W": "보도"}
for grp in ["차량", "보행", "보도"]:
    for k, kind, nm, ch, w, g, c, sec, role in [n for n in NET if n[1] == grp]:
        A_ = g.area; Lm = length_of(g); sums[kind] += A_
        pg.rect(tx, yy, sum(wd), RH, fc="white", z=5); pg.line([tx, tx + sum(wd)], [yy + RH, yy + RH], c="#dedede", lw=0.4, z=6)
        pg.rect(xs_[0] + 0.8, yy + 1.2, 1.8, RH - 2.4, fc=c, z=6)
        pg.t(xs_[0] + 4.0, yy + RH / 2, SHORT[k], fs=10, bold=True, z=6)
        pg.t(xs_[1] + 1.2, yy + RH / 2, CHS[k], fs=10, z=6)
        pg.t(xs_[3] - 1.2, yy + RH / 2, w, fs=10, ha="right", z=6)
        pg.t(xs_[4] - 1.2, yy + RH / 2, f0(Lm) if k != "W" else "-", fs=10, ha="right", z=6)
        pg.t(xs_[5] - 1.2, yy + RH / 2, f0(A_), fs=10, ha="right", z=6)
        tw_ = sum(s_[1] for s_ in sec); bx = xs_[5] + 2.0; bw = wd[5] - 4.0; sc = bw / 44.0
        cx_ = bx + (bw - tw_ * sc) / 2
        for lab, sw, scol in sec:
            pg.rect(cx_, yy + 1.2, sw * sc, RH - 2.4, fc=scol, ec="white", lw=0.5, z=6)
            pg.t(cx_ + sw * sc / 2, yy + RH / 2, ("%s %g" % (lab, sw)) if sw * sc > 16 else "%g" % sw, fs=10, ha="center", z=7, c="white" if scol == "#636363" else INK)
            cx_ += sw * sc
        yy += RH
    pg.rect(tx, yy, sum(wd), 6.0, fc="#ebebe8", z=5)
    pg.t(xs_[0] + 4.0, yy + 3.0, {"차량": "차량 도로 소계", "보행": "보행자전용도로·광장 소계", "보도": "보도 소계"}[grp], fs=10, bold=True, z=6)
    pg.t(xs_[5] - 1.2, yy + 3.0, f0(sums[grp]), fs=10, bold=True, ha="right", z=6)
    pg.t(xs_[5] + 2.0, yy + 3.0, "구역의 %.1f%%" % (sums[grp] / TOT["boundary"] * 100), fs=10, c=GREY, z=6)
    yy += 6.0
tot = sum(sums.values())
pg.rect(tx, yy, sum(wd), 6.4, fc="#d9d9d5", z=5)
pg.t(xs_[0] + 4.0, yy + 3.2, "도로·보행 합계", fs=10, bold=True, z=6); pg.t(xs_[5] - 1.2, yy + 3.2, f0(tot), fs=10, bold=True, ha="right", z=6)
pg.t(xs_[5] + 2.0, yy + 3.2, "구역의 %.1f%%(공원 제외)" % (tot / TOT["boundary"] * 100), fs=10, c=GREY, z=6)
yy += 6.4
pg.line([tx, tx + sum(wd)], [yy, yy], c="#3c3c3c", lw=0.8, z=7)
# 동선 원칙(박스 3개)
yy += 4.0
pk = sum(b["gfa"] for b in BLD if b["main"] == "주차" and "허브" not in b["name"])
BOX = [("차량은 외곽에서 처리", "접속점 %d곳을 외곽 도로에 두고 주차장동이 진입부에서 차량을 받습니다." % len(ACC)),
       ("보행은 십자 축과 사선 축", "선형공원(40 m)과 중앙 보행축(30 m)이 교차광장에서 만나고 사선 보행축이 관문에서 이어집니다."),
       ("주차는 건축물로 집약", "주차전용건축물 %s㎡(약 %s대, 32㎡/대 가정)로 지상 주차를 줄입니다." % (f0(pk), f0(round(pk / 32, -1))))]
bw_ = (sum(wd) - 8) / 3
bh = 12.0 + max(block_h(pg, d, bw_ - 7) for t, d in BOX) + 2.0
for i, (t, d) in enumerate(BOX):
    bx = tx + i * (bw_ + 4)
    pg.rect(bx, yy, bw_, bh, fc="#F3F5F8", ec="none", z=5); pg.rect(bx, yy, 1.4, bh, fc=SLATE, z=6)
    pg.t(bx + 4, yy + 5.0, t, fs=10, bold=True, c=SLATE, z=6)
    text_block(pg, bx + 4, yy + 11.0, d, bw_ - 7, c=INK, z=6)
yy += bh + 6.0
# 대표 단면(도면에서 읽은 폭, 같은 축척)
pg.t(tx, yy, "대표 단면(도면 기준 폭, 같은 축척)", fs=10, bold=True)
SEC = [("선형공원 B=40", [("식재", 12, "#9fd67c", [3.0, 9.0]), ("광장", 16, "#efe8d6", []), ("식재", 12, "#9fd67c", [3.0, 9.0])], "#3DA24B"),
       ("동서 도로 B=20", [("보도", 5, "#d9d9d6", [2.5]), ("차도", 20, "#636363", []), ("보도", 5, "#d9d9d6", [2.5])], "#636363"),
       ("중앙 보행축 B=30", [("식재", 7, "#9fd67c", [3.6]), ("보행", 16, "#efe8d6", []), ("식재", 7, "#9fd67c", [3.4])], "#E8833A")]
sw_ = (sum(wd) - 8) / 3; scm = sw_ / 46.0
top = yy + 4.0; gy = top + 6.0 + (219 - 8.0 - top - 6.0) * 0.62
for i, (ttl, segs, col) in enumerate(SEC):
    bx = tx + i * (sw_ + 4)
    pg.t(bx, top + 2.0, ttl, fs=10, bold=True, c=col)
    tw_ = sum(sg[1] for sg in segs); x_ = bx + (sw_ - tw_ * scm) / 2
    for lab, w, c, trees in segs:
        pg.rect(x_, gy, w * scm, 2.4, fc=c, ec="white", lw=0.3, z=6)
        for tpos in trees:
            cxm = x_ + tpos * scm
            pg.line([cxm, cxm], [gy, gy - 5.0], c="#8b7355", lw=0.7, z=7); pg.ax.add_patch(Circle((cxm, gy - 7.6), 3.0, fc="#86c25a", ec="#5a9a3a", lw=0.3, zorder=7))
        pg.line([x_, x_], [gy + 3.2, gy + 5.2], c="#777", lw=0.4, z=7)
        pg.t(x_ + w * scm / 2, gy + 6.4, "%s %g" % (lab, w), fs=10, ha="center", c=INK, z=7)
        x_ += w * scm
    pg.line([x_, x_], [gy + 3.2, gy + 5.2], c="#777", lw=0.4, z=7)
pg.save("D3_도로보행계획도")
