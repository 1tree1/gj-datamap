"""K4b 조감 렌더 3종 — 가로형 기본(02 시트용)·세로 띠(03 면적표용). k4_axo.render 의 인자만 다르다."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k4_axo as K
SP = K.SP
o, m = K.render(az_deg=-35, el_deg=34, out=SP + r"\axo_sheet.png", W=3600, Hh=2546, shift=(0, 45)); print("sheet", m)
o, m = K.render(az_deg=-84, el_deg=40, out=SP + r"\axo_v.png", W=1500, Hh=3250); print("strip", m)
