"""조감 히어로 2장(16:9): 제안(After, 컬러)·현황(Before, 흑백) — 같은 카메라. 출력: assets/hero_after.jpg, hero_before.jpg
계획 쪽 입력은 work/20261005_plan_clean/data (PLAN_SP)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PLAN_SP", r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean\data")
sys.path.insert(0, r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_clean\scripts")
import k4_axo as K
os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
W, H = 3840, 2160
a = os.path.join(ROOT, "assets", "hero_after.jpg"); b = os.path.join(ROOT, "assets", "hero_before.jpg")
print(K.render(az_deg=-35, el_deg=34, out=a, W=W, Hh=H, shift=(0, 18))[1])
print(K.render(az_deg=-35, el_deg=34, out=b, W=W, Hh=H, shift=(0, 18), before=True)[1])
