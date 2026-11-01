# -*- coding: utf-8 -*-
"""04~06장 2차 수정 그림 공통 도구 — 서체 Pretendard, 본문 10 pt 이상, 흰 바탕, 붉은색 #C8102E와 회색 계열.
그림은 출력 크기(mm)로 그려 글자 크기가 그대로 유지되게 한다(col = 183 mm 폭, wide = 380 mm 폭)."""
import os, sys, glob
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Circle, Wedge, FancyArrowPatch
from PIL import Image, ImageOps

R = "C:/Users/OFFICE/Desktop/9_도시"
REP = R + "/work/20261015_report"; FIG = REP + "/fig"
RM = R + "/work/20261011_masterplan_rough"; AS = R + "/work/20261011_midterm_deck/build/assets"
PHOTO = R + "/경주답사"
FD = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")
for w in ("Regular", "Medium", "SemiBold", "Bold"):
    fm.fontManager.addfont(os.path.join(FD, "Pretendard-%s.otf" % w))
plt.rcParams["font.family"] = "Pretendard"; plt.rcParams["axes.unicode_minus"] = False

RED = "#C8102E"; DRED = "#8A0A1F"; LRED = "#F2C9CF"; XRED = "#FBEAEC"
INK = "#222222"; G1 = "#444444"; G2 = "#6f6f6f"; G3 = "#9a9a9a"; G4 = "#cfcfcf"; G5 = "#e9e9e9"; G6 = "#f4f4f2"
COL = 183.0; WIDE = 380.0


def new(w, h, dpi=300):
    fig = plt.figure(figsize=(w / 25.4, h / 25.4), dpi=dpi, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis("off")
    ax._w = w; ax._h = h
    return fig, ax


def T(ax, x, y, s, fs=10, c=INK, ha="left", va="center", w="regular", **kw):
    wt = {"regular": 400, "medium": 500, "semibold": 600, "bold": 700}[w]
    kw.setdefault("zorder", 6); return ax.text(x, y, s, fontsize=fs, color=c, ha=ha, va=va, fontweight=wt, **kw)


def box(ax, x, y, w, h, fc="white", ec=G3, lw=0.8, r=1.2, z=2, ls="-"):
    p = FancyBboxPatch((x + r, y + r), w - 2 * r, h - 2 * r, boxstyle="round,pad=%f,rounding_size=%f" % (r, r), fc=fc, ec=ec, lw=lw, zorder=z, ls=ls)
    ax.add_patch(p); return p


def arrow(ax, x0, y0, x1, y1, c=G1, lw=1.2, ms=10, z=5, style="-|>", ls="-", rad=0.0):
    a = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=ms, color=c, lw=lw, zorder=z, ls=ls,
                        connectionstyle="arc3,rad=%f" % rad, shrinkA=0, shrinkB=0)
    ax.add_patch(a); return a


def line(ax, xs, ys, c=G3, lw=0.8, z=3, ls="-"): ax.plot(xs, ys, color=c, lw=lw, zorder=z, ls=ls, solid_capstyle="butt")


def rect(ax, x, y, w, h, fc="white", ec="none", lw=0.0, z=2): ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z))


def save(fig, name, dpi=300):
    p = os.path.join(FIG, name); fig.savefig(p, dpi=dpi, facecolor="white"); plt.close(fig)
    im = Image.open(p); print("saved", name, im.size); return p


def trim(im, pad=24, thr=245):
    a = np.asarray(im.convert("L")); ys, xs = np.where(a < thr)
    if len(xs) == 0: return im
    return im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad), min(im.height, ys.max() + pad)))


def photos_row(idx, out, h=1500, gap=14, quality=88, crops=None):
    fs = sorted(glob.glob(PHOTO + "/*.jpg")); ims = []
    for n, k in enumerate(idx):
        im = ImageOps.exif_transpose(Image.open(fs[k])).convert("RGB")
        if crops and crops.get(k): im = im.crop(crops[k])
        s = h / im.height; ims.append(im.resize((int(im.width * s), h), Image.LANCZOS))
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    sheet = Image.new("RGB", (W, h), "white"); x = 0
    for i in ims: sheet.paste(i, (x, 0)); x += i.width + gap
    p = os.path.join(FIG, out); sheet.save(p, quality=quality); print("saved", out, sheet.size); return p
