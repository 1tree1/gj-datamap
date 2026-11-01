# -*- coding: utf-8 -*-
"""build_midterm.py 에 라이노 캡처 기반 다이어그램 슬라이드를 끼워 넣는다(1회용). strategy3 · axon_program · section_strip · zones 지도 교체"""
import io
s = io.open('build_midterm.py', encoding='utf-8').read()
# 1) 순서
old = '"div2", "concept", "strategy", "linkage", "cases",'
new = '"div2", "concept", "strategy", "strategy3", "linkage", "cases",'
assert old in s; s = s.replace(old, new)
old = '"div4", "matrix", "anchor1", "anchor2", "others", "zones", "programs",'
new = '"div4", "matrix", "anchor1", "anchor2", "others", "zones", "axon_program", "section_strip", "programs",'
assert old in s; s = s.replace(old, new)
# 2) 권역 구성도 → 용도 색 획지 배분도
old = '    picture(s, MA + r"\\zones_map.png", 0.6, 1.5, 3.0, 5.45, mode="contain", align=(0, 0))'
new = '    picture(s, MA + r"\\landuse_map.png", 0.6, 1.5, 3.0, 5.45, mode="contain", align=(0, 0))'
assert old in s; s = s.replace(old, new)
s = s.replace('    src(s, 0.6, 7.0, 3.2, 0.3, "라이노 계획 프레임 획지(최종) · 회색 = 주차·오픈스페이스·보행공간")', '    src(s, 0.6, 7.0, 3.2, 0.3, "최종 도로계획 + 용도별 획지(라이노) · 회색 띠 = 보행공간, 진회색 = 차량 가로")')
# 3) 신규 슬라이드
marker = '@slide("linkage")'
new_slides = '''@slide("strategy3")
def _(d):
    s = std(d, "strategy3", "해결 컨셉 : 전략의 공간 표현", "세 전략의 공간 다이어그램")
    for i, (k, t, b) in enumerate([("connect", "CONNECT  접속", "동서 선형공원 40m · 화랑로 연결 · 남북 보행축 30m로 끊긴 도시조직을 잇습니다"), ("exchange", "EXCHANGE  교차·전환", "구 역사·광장·창작·체험·시장 접점이 모인 중앙에서 방문객과 주민이 만납니다"), ("spread", "SPREAD  확산", "북측 청사·업무·주거가 저녁 이후 사람을 남기고 활동을 성동시장·행복황촌으로 내보냅니다")]):
        x = 0.6 + i * 4.1
        picture(s, MA + "\\\\diag_strategy_%s.png" % k, x, 1.5, 3.93, 4.3, mode="contain", align=(0.5, 0))
        rect(s, x, 5.95, 3.93, 0.95, fill=TINT, radius=0.08)
        text(s, x + 0.15, 6.0, 3.65, 0.3, t, size=12, bold=True, color=ACC if i < 2 else INK, tag="s3-t"); text(s, x + 0.15, 6.3, 3.65, 0.6, b, size=10, color=INK2, line=1.15, tag="s3-b")
    notes(s, "라이노 _DIAG 임시 레이어(프로그램 매스·도로·보도·맥락 건물 4,457동)를 남서 상공 평행투영으로 캡처(build/rhino_diagram_build.py · rhino_diagram_capture.py)하고 build/compose_diagrams.py로 화살표·라벨을 얹었다. 매스 높이는 프로그램별 가정(공공청사 20m·주거 18m·업무 19.5m·문화 12m·공연장 15m·주차 15m).")

'''
assert marker in s; s = s.replace(marker, new_slides + marker, 1)
marker2 = '@slide("programs")'
new_slides2 = '''@slide("axon_program")
def _(d):
    s = std(d, "axon_program", "프로그램 : 배치 구상", "프로그램 배치 구상 (축측 · 남서 상공)")
    picture(s, MA + r"\\diag_axon_program.png", 0.6, 1.45, 12.13, 5.1, mode="contain", align=(0.5, 0))
    picture(s, MA + r"\\diag_legend.png", 0.6, 6.5, 3.4, 0.5, mode="contain", align=(0, 0.5)) if False else None
    text(s, 0.6, 6.6, 12.1, 0.4, "매스는 프로그램별 층수 가정(공공청사 5F 20m · 주거 6F 18m · 업무 5F 19.5m · 문화 3F 12m · 공연장 3F 15m · 주차 5F 15m)으로 획지 안쪽 5m를 띄워 올린 볼륨이며, 건축 배치안이 아니라 규모와 위치의 개념도입니다. 맥락 건물은 건축물대장 층수 기준입니다.", size=10, color=INK2, line=1.2, tag="ax-n")
    notes(s, "라이노 캡처 + 라벨 합성(compose_diagrams.py). 라벨 면적은 같은 프로그램 획지의 합.")

@slide("section_strip")
def _(d):
    s = std(d, "section_strip", "프로그램 : 남북 단면", "남북 단면 띠 : 프로그램의 배열과 높이")
    picture(s, MA + r"\\diag_section_strip.png", 0.6, 1.5, 12.13, 4.6, mode="contain", align=(0.5, 0))
    items = [("남", "방문 관문", "관광휴게·근대역사관(구 역사) · 관광지원·주차 — 대릉원·황리단길에서 들어오는 방문객을 받습니다"), ("중앙", "교차·전환", "창작 레지던시·체험 · 시장 연계 — 동서 선형공원 40m와 남북 보행축이 교차하는 접점"), ("북", "근로·정주", "청년 창업·업무 · 공공청사·의회 · 청년·신혼 주거 · 생활편의 · 공연장 — 북천·황성공원 방면")]
    for i, (a, b, c) in enumerate(items):
        x = 0.6 + i * 4.1; rect(s, x, 6.15, 3.93, 0.8, fill=TINT, radius=0.08)
        text(s, x + 0.15, 6.2, 0.6, 0.3, a, size=12, bold=True, color=ACC, tag="ss-a"); text(s, x + 0.7, 6.2, 3.1, 0.3, b, size=11, bold=True, tag="ss-b"); text(s, x + 0.15, 6.48, 3.65, 0.45, c, size=9, color=INK2, line=1.15, tag="ss-c")
    notes(s, "section_strip.py: 최종 도로계획 획지의 남북 범위와 프로그램 높이 가정으로 그린 개념 단면. 서측 열·동측 열을 두 줄로 펼쳤다.")

'''
assert marker2 in s; s = s.replace(marker2, new_slides2 + marker2, 1)
# 4) 목차 설명 갱신
s = s.replace('("2", "해결 컨셉", "컨셉 위계 · 전략의 공간 배치 · 관광–정주 성립 조건 · 선례", PAGE["div2"]),', '("2", "해결 컨셉", "컨셉 위계 · 전략의 공간 배치 · 전략 공간 다이어그램 · 관광–정주 성립 조건 · 선례", PAGE["div2"]),')
s = s.replace('("4", "프로그램", "선정 방법 · 앵커 ①② · 기타 프로그램 · 권역 · 세부 프로그램", PAGE["div4"]),', '("4", "프로그램", "선정 방법 · 앵커 ①② · 기타 프로그램 · 권역 · 배치 구상(축측) · 남북 단면 · 세부 프로그램", PAGE["div4"]),')
io.open('build_midterm.py', 'w', encoding='utf-8').write(s)
print('patched')
