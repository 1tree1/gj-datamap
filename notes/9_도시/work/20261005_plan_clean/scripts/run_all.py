"""run_all — 규제 미적용 획지·매스안 전체 파이프라인을 처음부터 다시 돌린다.
순서: k1 획지 → k2 매스 → k5 표 → k4b 조감 렌더 → k6 획지계획 → k7 면적표 → k8 조감 시트 → k9 도로계획 → k10 엑셀
사용: <venv python> run_all.py"""
import subprocess, sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["k1_lots.py", "k2_massing.py", "k5_tables.py", "k4b_renders.py", "k6_lotplan.py", "k7_areatable.py", "k8_axo_sheet.py", "k9_roadplan.py", "k10_xlsx.py"]
env = dict(os.environ, PYTHONIOENCODING="utf-8")
for s in STEPS:
    p = os.path.join(HERE, s)
    if not os.path.exists(p): print("건너뜀(없음):", s); continue
    t0 = time.time(); r = subprocess.run([sys.executable, p], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8")
    tail = "\n".join((r.stdout or "").strip().splitlines()[-4:])
    print("[%s] %.1fs rc=%d\n%s" % (s, time.time() - t0, r.returncode, tail))
    if r.returncode != 0: print(r.stderr[-1500:]); break
