# -*- coding: utf-8 -*-
"""최종 덱 조립. python build_deck.py → output/구경주역_최종마스터플랜_v1.pptx"""
import os, sys, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck_kit import *
import s_front, s_strategy, s_plan, s_program

ROOT = r"C:\Users\OFFICE\Desktop\9_도시\work\20261011_final_deck"
d = Deck(os.path.join(ROOT, "build", "tmp"))
s_front.build(d); s_strategy.build(d); s_plan.build(d); s_program.build(d)

# 목차 슬라이드: 섹션별 쪽 범위 — 구분 쪽(divider) 번호 기준
parts = [("1", "대지분석과 문제", "경주의 역사 · 대상지 · 동서와 남북 · 규제와 유산 · 인구·체류·업종 · 문제 종합"), ("2", "계획 목표와 전략", "목표와 성과지표 · NEXUS 1918 · 관광과 정주의 조건 · 상위계획 · 선례"),
         ("3", "마스터플랜", "토지이용 · 획지 · 가로와 보행 · 공원녹지 · 건축물 · 조감 · 주요 시설"), ("4", "프로그램과 규모", "이용자 가정 · 면적표 · 개발규모 · 규제 검토"), ("5", "단계별 추진과 운영", "단계 · 운영 주체와 재원 · 성과지표 · 자료 출처")]
divs = [n for n, sec, t in d.toc if sec == "" and t not in ("표지",)]
ranges = []
for i, n in enumerate(divs):   # 목차가 2번째로 들어가므로 이후 쪽번호는 +1
    end = (divs[i + 1] - 1) if i + 1 < len(divs) else d.n
    ranges.append((n + 2, end + 1))
s = d.slide("목차", "발표 구성", number=True)
d.text(s, 0.6, s._top, 6, 0.4, "개요  03", size=12, bold=True, color=G1)
y = s._top + 0.6
for (num, title, sub), (a, b) in zip(parts, ranges):
    d.text(s, 0.6, y, 0.8, 0.5, num, size=22, bold=True, color=RED, num=True)
    d.text(s, 1.5, y + 0.02, 7, 0.4, title, size=16, bold=True); d.text(s, 1.5, y + 0.42, 9.5, 0.3, sub, size=10, color=G2)
    d.text(s, 11.2, y + 0.05, 1.5, 0.4, "%02d–%02d" % (a, b), size=13, color=G1, align="r", num=True)
    d.hline(s, 0.6, y + 0.85, 12.13, color=G5); y += 0.98
# 목차를 2번째로 이동, 번호 재부여
sldIdLst = d.prs.slides._sldIdLst; ids = list(sldIdLst); last = ids[-1]; sldIdLst.remove(last); sldIdLst.insert(1, last)
# 쪽번호 텍스트 재부여(각 슬라이드의 마지막 번호 텍스트박스)
for i, sl in enumerate(d.prs.slides, start=1):
    for sh in sl.shapes:
        if sh.has_text_frame and sh.left >= Inches(12.1) and sh.top >= Inches(6.9):
            for p in sh.text_frame.paragraphs:
                for r in p.runs: r.text = "%02d" % i
out = os.path.join(ROOT, "output", "구경주역_최종마스터플랜_v1.pptx"); d.save(out)
print("saved", out, "slides", d.n)
for n, sec, t in d.toc: print(" %02d %s | %s" % (n, sec, t))
