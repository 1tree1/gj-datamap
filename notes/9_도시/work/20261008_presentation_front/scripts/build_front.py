"""build_front — 발표 앞부분(대지분석·설계방향) 제작. 목차 확정본(2026-10-08)의 쪽번호에 맞춘다.
출력: ../20261008_발표_앞부분_대지분석_설계방향_v1.pptx  (A4 가로, v3 스타일 + 검은 목차·구분 쪽)
문체: 제목·소제목은 명사형, 문장은 합니다체, 극적·구어·번역투 금지. 수치마다 [T1~T4] 등급을 붙인다.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptkit_front import *
from pptkit_front import _I, _P, K

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = ROOT + r"\assets"; PH = A + r"\photos"; HI = A + r"\hist"; DOC = A + r"\doc"; MP = A + r"\maps"; CH = A + r"\charts"
V3 = r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_ppt_refine\assets"; V3C = V3 + r"\crops"
OUTFILE = ROOT + r"\20261008_발표_앞부분_대지분석_설계방향_v1.pptx"

# 목차에서 확정된 쪽번호. 파일 안의 순서는 이 순서이고, 쪽번호는 슬라이드에 글자로 적는다.
PAGE = dict(cover=1, toc=2, overview=3, div1=4, hist=5, social=6, structure=7, macro=8, micro=9,
            div2=10, problem=11, response=12, goal=13, strat1=14, strat2=15, app1=29, app2=30)
ORDER = ["cover", "toc", "overview", "div1", "hist", "social", "structure", "macro", "micro",
         "div2", "problem", "response", "goal", "strat1", "strat2", "app1", "app2"]
SL = {}
def slide(key):
    def deco(fn): SL[key] = fn; return fn
    return deco

def std(d, key, label, title, sub=None, scale=None):
    s = d.slide(); title_block(s, label, title, sub)
    if scale:
        x = SW - RM
        for lab in reversed(scale if isinstance(scale, (list, tuple)) else [scale]):
            w = 0.42 + 0.115 * len(lab); x -= w; scale_tag(s, lab, x=x, w=w); x -= 0.08
    page_no(s, PAGE[key]); return s

def have(p): return bool(p) and os.path.exists(p)
def first(*ps):
    for p in ps:
        if have(p): return p
    return None

# 의미 색 — 문제 번호와 5대 원칙은 같은 색을 쓴다(통영식: 색이 곧 논증 단계)
PC = {"연결": BLUE, "관문": ZS, "근로": ZN, "정주": YEL, "확산": ZC}
PCT = {"연결": "#FFFFFF", "관문": INK, "근로": "#FFFFFF", "정주": INK, "확산": "#FFFFFF"}

# ═══════════════════════════ 표지·목차·구분 ═══════════════════════════
@slide("cover")
def _(d):
    s = dark_slide(d)
    img = first(vimg(first(HI + r"\ortho_2025_F1_outline.jpg")), HI + r"\cover_ortho2025_outline.jpg", V3 + r"\hero_before.jpg")
    picture(s, img, SW * 0.47, 0, SW * 0.53, SH, mode="cover", align=(0.5, 0.5))
    rect(s, 0, 0, SW * 0.47, 0.08, fill=RED)
    text(s, 0.6, 0.55, 5.0, 0.3, "건축디자인6 STUDIO B  ·  도시설계", size=10.5, color="#FF5A4F", bold=True)
    text(s, 0.6, 2.6, 5.0, 1.6, ["구 경주역", "도시재생 마스터플랜"], size=32, bold=True, color="#FFFFFF", line=1.1, tag="cover-t")
    text(s, 0.6, 4.3, 4.9, 0.8, ["폐철도 부지의 활용 방향과", "공간구성 계획"], size=14, color=FG2, tag="cover-s")
    rect(s, 0.65, 5.35, 1.0, 0.045, fill=RED)
    text(s, 0.6, 6.95, 5.0, 0.7, ["2019113133 이승규  ·  2021113994 김민승", "김아름 교수님"], size=10.5, color=FG2, tag="cover-n")

@slide("toc")
def _(d):
    s = dark_slide(d)
    text(s, 0.60, 0.36, 8.0, 1.0, [(("CONTENTS", {"font": "Pretendard ExtraBold"}),)], size=56, bold=False, color="#FFFFFF", tag="toc-big")
    def row(x_num, x_ttl, x_pg, yc, num, ttl, pg=None, head=False):
        if num: text(s, x_num, yc - 0.16, 0.6, 0.3, num, size=12, color=FG3, anchor="m", tag="toc-n")
        text(s, x_ttl, yc - 0.16, 3.0, 0.3, ttl, size=(14.5 if head else 11), bold=head, color=("#FFFFFF" if head else FG2), anchor="m", tag="toc-t")
        if pg: text(s, x_pg, yc - 0.16, 1.0, 0.3, pg, size=11, color=FG3 if not head else "#FFFFFF", anchor="m", tag="toc-p")
    L = (0.66, 1.34, 4.02); R = (6.38, 7.05, 10.75)
    row(*L[:2], L[2], 2.32, "01", "대지분석", head=True)
    for yc, (t, p) in zip((2.85, 3.29, 3.74, 4.19, 4.63), [("경주의 역사", "05"), ("사회적 문제", "06"), ("도시구조적 문제", "07"), ("대지분석 MACRO", "08"), ("대지분석 MICRO", "09")]):
        row(L[0], L[1], L[2], yc, "", t, p)
    row(*L[:2], L[2], 5.44, "02", "설계방향", head=True)
    for yc, (t, p) in zip((5.99, 6.44, 6.89), [("문제 인식과 대응", "11–12"), ("목표설정", "13"), ("개발전략", "14–15")]):
        row(L[0], L[1], L[2], yc, "", t, p)
    row(*R[:2], R[2], 2.29, "03", "마스터플랜", head=True)
    items = [("주변연계전략", "17"), ("조닝", "18"), ("용도구획", "19"), ("주요시설", "20"), ("도로", "21"), ("데크", "22"), ("녹지", "23"), ("주차", "24"), ("프로그램표", "25")]
    for yc, (t, p) in zip((2.84, 3.20, 3.57, 3.92, 4.29, 4.65, 5.02, 5.38, 5.75), items):
        row(R[0], R[1], R[2], yc, "", t, p)
    row(*R[:2], R[2], 6.31, "04", "단면계획", head=True)
    row(R[0], R[1], R[2], 6.76, "", "종단면과 데크", "27")
    text(s, R[0], 7.32, 4.5, 0.3, [(("05", {"bold": True, "color": "#FFFFFF"}), ("   부록   29–30", {"bold": True, "color": "#FFFFFF"}))], size=12, anchor="m", tag="toc-app")
    page_no(s, PAGE["toc"], dark=True)

def divider(d, key, num, title, items, img, img_align=(0.5, 0.5), dim=0.0):
    s = dark_slide(d)
    iw = SW * 0.5
    if img:
        picture(s, img, SW - iw, 0, iw, SH, mode="cover", align=img_align)
        if dim: rect(s, SW - iw, 0, iw, SH, fill="#000000", alpha=dim)
    rect(s, 0, 0, 0.1, SH, fill=RED)
    text(s, 0.75, 2.55, 3.0, 1.2, num, size=64, bold=True, color=FG3, tag="div-n")
    text(s, 0.75, 3.85, 5.0, 0.8, title, size=32, bold=True, color="#FFFFFF", tag="div-t")
    for i, (t, p) in enumerate(items):
        y = 4.85 + i * 0.36
        text(s, 0.78, y, 3.6, 0.3, t, size=12, color=FG2, tag="div-i")
        text(s, 4.2, y, 0.9, 0.3, p, size=12, color=FG3, tag="div-p")
    page_no(s, PAGE[key], dark=True)
    return s

@slide("div1")
def _(d):
    divider(d, "div1", "01", "대지분석", [("경주의 역사", "05"), ("사회적 문제", "06"), ("도시구조적 문제", "07"), ("대지분석 MACRO", "08"), ("대지분석 MICRO", "09")],
            first(V3.replace("assets", "") + r"..\maps\map13_경주_층위스택.png", r"C:\Users\OFFICE\Desktop\9_도시\work\maps\map13_경주_층위스택.png"), img_align=(0.0, 0.5))

@slide("div2")
def _(d):
    divider(d, "div2", "02", "설계방향", [("문제 인식과 대응", "11–12"), ("목표설정", "13"), ("개발전략", "14–15")],
            V3 + r"\hero_before.jpg", img_align=(0.45, 0.5), dim=0.28)

# (본문 쪽은 front_pages*.py 에 나누어 정의 — 같은 전역을 공유한다)
import glob
for _f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "front_pages*.py"))):
    exec(compile(open(_f, encoding="utf-8").read(), _f, "exec"))

def build(only=None):
    d = Deck()
    d.prs.slide_width = _I(SW); d.prs.slide_height = _I(SH)
    for k in ORDER:
        if only and k not in only: continue
        if k in SL: SL[k](d)
    d.save(OUTFILE)
    print("saved", OUTFILE, "slides:", len(d.prs.slides))
    for w in WARN: print(w)

if __name__ == "__main__":
    build([a for a in sys.argv[1:]] or None)
