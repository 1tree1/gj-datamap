# -*- coding: utf-8 -*-
"""최종 덱 공통 스타일 — 적색 + 흑백. 모든 도면·차트·슬라이드가 이 팔레트와 글꼴을 쓴다."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

RED = "#C8102E"; RED_DK = "#8B0A1E"; RED_LT = "#F3D5DA"; RED_XL = "#FAEDEF"
INK = "#111111"; G1 = "#333333"; G2 = "#6B6B6B"; G3 = "#9E9E9E"; G4 = "#C9C9C9"; G5 = "#E6E6E6"; G6 = "#F3F3F3"; WHITE = "#FFFFFF"

FONT_KO = "Malgun Gothic"; FONT_NUM = "Courier New"
_mal = r"C:\Windows\Fonts\malgun.ttf"; _malb = r"C:\Windows\Fonts\malgunbd.ttf"
for f in (_mal, _malb):
    if os.path.exists(f): font_manager.fontManager.addfont(f)
plt.rcParams.update({"font.family": FONT_KO, "axes.unicode_minus": False, "font.size": 9, "axes.edgecolor": G3, "axes.linewidth": 0.6,
                     "xtick.color": G2, "ytick.color": G2, "axes.labelcolor": G1, "text.color": INK, "savefig.dpi": 300, "savefig.facecolor": WHITE})

# 용도별 색(도면): 흑백 계열 + 문화·역사만 적색
USE_FILL = {"공공청사": "#8A8A8A", "공동주택": "#B9B9B9", "업무시설": "#A3A3A3", "문화및집회시설": RED_LT, "근린생활·판매시설": "#D2D2D2", "운동시설": "#C4C4C4", "주차전용·관광휴게": "#DCDCDC"}
MASS_FILL = {"공공업무": "#4A4A4A", "주거": "#8F8F8F", "상업·업무": "#6E6E6E", "문화·교육·공공": RED, "창조산업": "#A9A9A9", "판매·음식": "#BDBDBD", "여가·오락·체육": "#7C7C7C",
             "역사유산": RED_DK, "교통·방문자": "#C2C2C2", "주차전용건축물": "#D0D0D0"}
GREEN_FILL = {"근린공원": "#E4E4E4", "문화공원": "#E9E9E9", "역사공원": "#DEDEDE", "경관녹지": "#ECECEC"}
PLAZA_FILL = "#F4F4F4"; ROAD_FILL = WHITE; WALK_FILL = "#FAFAFA"; PEDWAY_FILL = "#F7EFF1"
CTX_BLD = "#D9D9D9"; CTX_BLD_EDGE = "#B5B5B5"; CTX_GROUND = "#F6F6F6"
