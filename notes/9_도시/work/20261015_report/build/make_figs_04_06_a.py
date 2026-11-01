# -*- coding: utf-8 -*-
"""04~06장 2차 수정 — 그림 제작 A: 잘라내기·사진 묶음(기존 도면·자산·답사 사진에서)
실행: python make_figs_04_06_a.py (venv_plan: PIL·matplotlib·shapely·pymupdf)"""
import os, sys
from figkit_46 import *

# 1) 세 전략 축측(덱 자산, 여백 제거)
for k in ("connect", "exchange", "spread"):
    im = trim(Image.open("%s/diag_strategy_%s.png" % (AS, k)).convert("RGB"), pad=30)
    if im.width > 2600: im = im.resize((2600, int(im.height * 2600 / im.width)), Image.LANCZOS)
    im.save("%s/04_strategy_%s.png" % (FIG, k)); print("04_strategy_%s" % k, im.size)

# 2) 손 구상도 2장
for k in ("axes", "roads"):
    im = Image.open("%s/sketch_%s.jpg" % (AS, k)).convert("RGB")
    if im.height > 2200: im = im.resize((int(im.width * 2200 / im.height), 2200), Image.LANCZOS)
    im.save("%s/05_sketch_%s.jpg" % (FIG, k), quality=90); print("05_sketch_%s" % k, im.size)

# 3) 최종 도면의 지도 부분만 잘라내기(머리글·우측 표 제외, 08장 도면 전체 사본과 겹치지 않게)
def crop(src, box, out):
    im = Image.open("%s/%s" % (FIG, src)).convert("RGB").crop(box); im.save("%s/%s" % (FIG, out)); print(out, im.size)
crop("05_site_axes.png", (33, 18, 2312, 1823), "05_axes_map.png")
crop("05_street_plan.png", (33, 18, 1456, 1823), "05_entry_map.png")
crop("05_plots_blocks.png", (33, 18, 1256, 1823), "05_plots_map.png")

# 4) 공간구조 지도만 다시 그리기(gkit, 우측 설명 박스·지시선 제외)
SC = RM + "/scripts"
sys.path.insert(0, SC); cwd = os.getcwd(); os.chdir(SC)
src = open(SC + "/g1_structure.py", encoding="utf-8").read()
ns = {"__name__": "g1map", "__file__": SC + "/g1_structure.py"}
exec(compile(src[:src.index("pg.top()")], "g1_structure_part", "exec"), ns)
pg = ns["pg"]
for t in list(pg.ax.texts): t.remove()
for l in list(pg.ax.lines): l.remove()
from matplotlib.transforms import Bbox
x0, y0, w, h = 4, 34, 196, 189
bb = Bbox.from_extents(x0 / 25.4, (225.0 - (y0 + h)) / 25.4, (x0 + w) / 25.4, (225.0 - y0) / 25.4)
pg.fig.savefig(FIG + "/06_zones_map.png", dpi=250, facecolor="white", bbox_inches=bb); plt.close(pg.fig)
os.chdir(cwd); print("06_zones_map", Image.open(FIG + "/06_zones_map.png").size)

# 5) 수요 기반 기준안(v2) 축측
im = trim(Image.open(AS + "/diag_axon_program.png").convert("RGB"), pad=30)
if im.width > 3000: im = im.resize((3000, int(im.height * 3000 / im.width)), Image.LANCZOS)
im.save(FIG + "/06_v2_axon.png"); print("06_v2_axon", im.size)

os.makedirs(REP + "/build/_cache", exist_ok=True)
# 6) 최종 모델 조감(프로그램 구성 조감 원본 렌더) — 세 존 확대
src_im = Image.open(RM + "/sheets/prog7a_axo.png").convert("RGB"); K = 2.4
PAN = {"north": (280, 400, 780, 730), "center": (590, 320, 1090, 650), "south": (900, 275, 1400, 605)}
for k, b in PAN.items():
    c = src_im.crop(tuple(int(v * K) for v in b)); c.save("%s/_cache/zone_%s.png" % (REP + "/build", k)); print("zone", k, c.size)

# 7) 현장 사진 묶음
photos_row([57, 56, 60], "04_connect_photos.jpg", h=1400)
photos_row([58, 47, 46], "05_axis_photos.jpg", h=1400)

# 8) 수요 기반 기준안(v2) 평면 — 좌측 불필요 부분 제외
im = Image.open(AS + "/diag_top_program.png").convert("RGB").crop((745, 120, 2060, 1500)); im.save(FIG + "/06_v2_plan.png"); print("06_v2_plan", im.size)
