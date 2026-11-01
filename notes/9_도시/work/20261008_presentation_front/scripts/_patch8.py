p="front_pages_c.py"; s=open(p,encoding="utf-8").read()
a='"자연녹지 77.5% · 2종일반주거 16.3% · 일반상업 6.2%"'; b='"자연녹지 77.5% · 2종일반주거 16.2% · 일반상업 6.4%"'
print(a in s); s=s.replace(a,b)
open(p,"w",encoding="utf-8").write(s)
