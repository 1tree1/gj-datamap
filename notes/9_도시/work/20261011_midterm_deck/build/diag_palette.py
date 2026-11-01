# -*- coding: utf-8 -*-
"""다이어그램 공통 팔레트(레드+흑백) · 프로그램 ↔ 색 · 높이 · 권역"""
PROG = [  # (라이노 레이어 접두어, 표시명, 색, 높이 m, 권역, 층수)
    ('시청', '공공청사·의회', '#3A3A3A', 20.0, 'A', '5F'),
    ('청년주거', '청년·신혼 주거', '#C8102E', 18.0, 'B', '6F'),
    ('생활편의', '생활편의·체육', '#E8808F', 8.0, 'B', '2F'),
    ('청년 오피스', '청년 창업·업무', '#8A0A1F', 19.5, 'C', '5F'),
    ('예술인', '창작 레지던시·체험', '#F0A0AD', 12.0, 'D', '3F'),
    ('성동시장', '성동시장 연계', '#F4B8C1', 8.0, 'D', '2F'),
    ('관광휴게', '관광휴게·근대역사관', '#D96D7A', 12.0, 'E', '3F'),
    ('공연장', '공연장', '#B5121B', 15.0, 'E', '3F'),
    ('관광지원', '관광지원·주차전용', '#9A9A9A', 15.0, 'P', '5F'),
    ('오픈스페이스', '오픈스페이스', '#C9D3C2', 0.3, 'O', '-'),
]
NAME2 = {p[1]: p for p in PROG}
def prog_of(layer):
    for p in PROG:
        if layer.startswith(p[0]): return p
    return None
RED = '#C8102E'; DARK = '#8A0A1F'; INK = '#1A1A1A'; G2 = '#D9D9D9'; G3 = '#9A9A9A'; G4 = '#5C5C5C'; PALE = '#F7D9DD'; WH = '#FFFFFF'
FONT_B = r'C:\Users\OFFICE\AppData\Local\Microsoft\Windows\Fonts\Pretendard-Bold.otf'
FONT_R = r'C:\Users\OFFICE\AppData\Local\Microsoft\Windows\Fonts\Pretendard-Regular.otf'
FONT_M = r'C:\Users\OFFICE\AppData\Local\Microsoft\Windows\Fonts\Pretendard-Medium.otf'

SHORT = {'공공청사·의회':'공공청사·의회','청년·신혼 주거':'청년·신혼 주거','생활편의·체육':'생활편의','청년 창업·업무':'청년 창업','창작 레지던시·체험':'창작·체험','성동시장 연계':'시장 연계','관광휴게·근대역사관':'관광휴게·역사관','공연장':'공연장','관광지원·주차전용':'관광지원·주차','오픈스페이스':'오픈스페이스'}
