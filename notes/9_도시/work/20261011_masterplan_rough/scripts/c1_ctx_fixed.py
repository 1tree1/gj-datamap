"""C1 정합된 맥락 건물 정리 → data/ctx_fixed.pkl (로컬 좌표, 다이어그램·조감 공통 배경)
- c0_ctx_register.py 결과(콘타 모델 O → 2배·회전 0·이동, V-World 연속지적 기준) 사용
- 메쉬 윤곽 추출 찌꺼기(꼭짓점 ≤ 4개인데 외접 직사각형을 반도 못 채우는 큰 삼각형 등) 제거
- 계획 경계 안 건물(철거 대상)은 남겨 두되 'inside' 표시"""
import os, pickle
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
R = pickle.load(open(os.path.join(D, "ctx_registered.pkl"), "rb"))
S = pickle.load(open(os.path.join(D, "design.pkl"), "rb")); B = S["B"]
out, drop = [], 0
Bb = B.buffer(1.0)
for g, h, z in R["CTX"]:
    for q in (g.geoms if hasattr(g, "geoms") else [g]):
        if q.area < 4: continue
        mrr = q.minimum_rotated_rectangle.area
        fillr = q.area / mrr if mrr > 0 else 0
        nv = len(q.exterior.coords) - 1
        if (fillr < 0.55 and q.area > 60) or (nv <= 3 and q.area > 40): drop += 1; continue
        out.append(dict(g=q, h=float(h), z0=float(z), inside=bool(Bb.contains(q.representative_point()))))
print("kept", len(out), "dropped", drop, "inside boundary", sum(o["inside"] for o in out))
pickle.dump(dict(B=out, xf=dict(theta=R["theta"], scale=R["scale"], t=R["t"], cen=R["cen"]), note=R["note"]), open(os.path.join(D, "ctx_fixed.pkl"), "wb"))
