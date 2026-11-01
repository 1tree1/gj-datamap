p="front_pages_c.py"; s=open(p,encoding="utf-8").read()
a=s.index("# ═════════════════════════ 08 대지분석 MACRO"); b=s.index("# ═════════════════════════ 09 대지분석 MICRO")
open(p,"w",encoding="utf-8").write(s[:a]+s[b:]); print("removed old macro")
