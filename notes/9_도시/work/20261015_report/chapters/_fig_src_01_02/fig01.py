# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
A='C:/Users/OFFICE/Desktop/9_도시/work/20261011_midterm_deck/build/assets/'
OUT='C:/Users/OFFICE/Desktop/9_도시/work/20261015_report/fig/'
F=lambda s,b=False: ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf' if b else 'C:/Windows/Fonts/malgun.ttf', s)
RED=(200,16,46); INK=(26,26,26); G=(110,110,110)

# ---- 그림 1-1 공간적 범위 (S3 + S1·S2)
city=Image.open(A+'city.png').convert('RGB'); loc=Image.open(A+'location_base.png').convert('RGB')
H=1800
city=city.resize((int(city.width*H/city.height),H),Image.LANCZOS)
loc=loc.resize((H,H),Image.LANCZOS)
gap=60; top=170; pad=30
W=pad*2+city.width+gap+loc.width
cv=Image.new('RGB',(W,top+H+pad),'white'); d=ImageDraw.Draw(cv)
x0=pad; cv.paste(city,(x0,top)); x1=x0+city.width+gap; cv.paste(loc,(x1,top))
d.text((x0,28),'S3  CITY / CORRIDOR — 경주시 전역과 폐선축',font=F(46,True),fill=INK)
d.text((x0,92),'경주시 1,324.53 ㎢ [T1] · 폐선축 80.3 km, 폐역 17개소 [T1]',font=F(36),fill=G)
d.text((x1,28),'S1  SITE · S2  DISTRICT — 계획 경계와 원도심 보행권',font=F(46,True),fill=INK)
d.text((x1,92),'S1 계획 경계 228,022 ㎡ [산정] · S2 반경 500 m·1,000 m',font=F(36),fill=G)
d.line([(x1-gap//2,25),(x1-gap//2,top+H)],fill=(200,200,200),width=3)
cv.save(OUT+'01_scope_s1_s2_s3.png',dpi=(200,200)); print(cv.size)
