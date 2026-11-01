p="front_pages_c.py"; s=open(p,encoding="utf-8").read()
a=s.index('@slide("structure")'); b=s.index("# ═════════════════════════ 09 대지분석 MICRO")
s=s[:a]+s[b:]
open(p,"w",encoding="utf-8").write(s); print("removed old structure")
