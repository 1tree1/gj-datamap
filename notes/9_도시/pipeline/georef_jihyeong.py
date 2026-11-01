"""고시 제2026-8호 지형도면고시도 11·12장(구경주역) 좌표 등록.

원리: 도곽 네 모서리에 인쇄된 TM 좌표를 읽어 도곽 픽셀 사각형에 아핀 변환을 부여한다.
      ★ 인쇄 좌표는 EPSG:5176 (Korean 1985 / Modified East Belt — 동경측지계 Bessel, 수정동부원점).
        Korea 2000(5183)으로 가정하면 (+57m, +300m) 어긋난다 — 2026-09-17 V-World 필지 대조로 확정.
      5176→5187은 pyproj 'Korean 1985 to KGD2002 (1)' (정확도 1m). 시트 내 변화 0.02m → 평행이동으로 취급.
출력: PNG + 월드파일(.pgw) + .prj  — EPSG:5187 (CLAUDE.md 처리본 규약)
검증: V-World 필지(4326→5187)를 래스터 위에 그려 정합 확인 이미지 생성.
"""
import json, sys
import numpy as np, fitz
from PIL import Image, ImageDraw
from pyproj import Transformer, CRS
from _common import ROOT, RAW, PROCESSED

PDF = ROOT / "archive/A_plans/A-S1-20260122-경주시-고시2026-8호_폐철도지형도면고시도-v1.pdf"
# 모서리 좌표 (2026-09-17 판독). 좌=X_left, 우=X_right, 상=Y_top, 하=Y_bottom  [EPSG:5183]
SHEETS = {
    11: dict(slug="jdp_n", title="구)경주역 지구단위계획 ① (북)", X=(219360.4088, 220038.7118), Y=(260617.0519, 261447.2569)),
    12: dict(slug="jdp_s", title="구)경주역 지구단위계획 ② (남)", X=(219362.7758, 220041.0788), Y=(259784.9419, 260615.1469)),
}
DPI = 200  # 내장 JPEG 원본 해상도(4678px / 1684pt)와 일치
NATIVE_CRS = "EPSG:5176"
OUT_CRS = "EPSG:5187"


def detect_frame(arr):
    """좌표가 붙은 **안쪽** 도곽선 (L, T, R, B). 바깥 테두리 안쪽에 ~85px 흰 여백이 있고 그 안이 진짜 도곽."""
    dark = arr < 110; white = arr > 245
    H, W = dark.shape
    rows = dark.mean(1); cols = dark.mean(0)
    def long_runs(v, thr):
        idx = [i for i in range(len(v)) if v[i] > thr]
        return idx
    ot = long_runs(rows[: int(H * .25)], .6)[0]
    ob = [i for i in range(int(H * .6), int(H * .85)) if rows[i] > .6][-1]
    ol = long_runs(cols[: int(W * .25)], .55)[0]
    orr = [j for j in range(int(W * .75), int(W * .99)) if cols[j] > .55][-1]
    sub_d = dark[ot + 3:ob - 2, ol + 3:orr - 2]; sub_w = white[ot + 3:ob - 2, ol + 3:orr - 2]
    rd, cd = sub_d.mean(1), sub_d.mean(0); rw, cw = sub_w.mean(1), sub_w.mean(0)
    h, w = sub_d.shape
    def inner(dk, wh, start, step):
        k = start
        while 0 <= k < len(wh) and wh[k] >= .9: k += step          # 흰 여백 통과
        cand = range(max(0, k - 6), min(len(dk), k + 7))
        return max(cand, key=lambda i: dk[i])                       # 그 근처 가장 어두운 행/열 = 도곽선
    T = ot + 3 + inner(rd, rw, 0, 1); B = ot + 3 + inner(rd, rw, h - 1, -1)
    L = ol + 3 + inner(cd, cw, 0, 1); R = ol + 3 + inner(cd, cw, w - 1, -1)
    print(f"  바깥 테두리 L={ol} T={ot} R={orr} B={ob} → 안쪽 도곽 L={L} T={T} R={R} B={B}")
    return L, T, R, B


def main():
    d = fitz.open(str(PDF))
    tnat = Transformer.from_crs(NATIVE_CRS, OUT_CRS, always_xy=True)

    # 검증용 필지
    parcels = json.load(open(RAW / "vworld_parcel.geojson", encoding="utf-8"))["features"]
    t4326 = Transformer.from_crs("EPSG:4326", OUT_CRS, always_xy=True)
    manifest = []
    for pno, s in SHEETS.items():
        page = d[pno - 1]
        pix = page.get_pixmap(dpi=DPI)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        arr = np.asarray(img.convert("L"), dtype=np.uint8)
        L, T, R, B = detect_frame(arr)
        print(f"\n[{pno}장 {s['title']}] 도곽 px L={L:.1f} T={T:.1f} R={R:.1f} B={B:.1f}")
        crop = img.crop((round(L), round(T), round(R), round(B)))
        W, H = crop.size
        X0, X1 = s["X"]; Y0, Y1 = s["Y"]
        px = (X1 - X0) / W; py = (Y1 - Y0) / H
        print(f"  {W}x{H}px  →  {X1-X0:.1f}m x {Y1-Y0:.1f}m  픽셀 {px:.4f}m x {py:.4f}m  (비율차 {abs(px/py-1)*100:.2f}%)")
        # 도곽 네 모서리를 5187로 변환 → 회전/스케일 편차 점검 후 평행이동으로 원점 결정
        cx = [tnat.transform(x, y) for x, y in ((X0, Y1), (X1, Y1), (X0, Y0), (X1, Y0))]
        rot = max(abs(cx[0][1]-cx[1][1]), abs(cx[0][0]-cx[2][0]))
        print(f"  5176→5187 모서리 변환 비직교 편차 {rot:.3f}m (평행이동 근사 사용)")
        ox, oy = cx[0]
        px = (cx[1][0] - cx[0][0]) / W; py = (cx[0][1] - cx[2][1]) / H
        out = PROCESSED / f"gosi2026-8_{s['slug']}_5187.png"
        crop.save(out, optimize=True)
        (PROCESSED / f"gosi2026-8_{s['slug']}_5187.pgw").write_text(
            f"{px:.6f}\n0.0\n0.0\n{-py:.6f}\n{ox + px/2:.4f}\n{oy - py/2:.4f}\n")
        (PROCESSED / f"gosi2026-8_{s['slug']}_5187.prj").write_text(CRS.from_epsg(5187).to_wkt())
        print(f"  저장 {out.name} + .pgw/.prj  (원점 {ox:.2f}, {oy:.2f})")

        # 검증 오버레이: 필지 경계를 빨강으로
        chk = crop.copy(); dr = ImageDraw.Draw(chk)
        n = 0
        for f in parcels:
            g = f["geometry"]; polys = g["coordinates"] if g["type"] == "Polygon" else [r for m in g["coordinates"] for r in m]
            for ring in polys:
                pts = []
                for lon, lat in ring:
                    x, y = t4326.transform(lon, lat)
                    u = (x - ox) / px; v = (oy - y) / py
                    pts.append((u, v))
                if any(0 <= u <= W and 0 <= v <= H for u, v in pts):
                    dr.line(pts, fill=(255, 0, 0), width=3); n += 1
        chk_out = PROCESSED / f"gosi2026-8_{s['slug']}_check.jpg"
        chk.save(chk_out, quality=80)
        print(f"  검증 이미지 {chk_out.name}  (필지 링 {n}개 오버레이)")
        manifest.append(dict(sheet=pno, slug=s["slug"], title=s["title"], px=[L, T, R, B], size=[W, H],
                             native_crs=NATIVE_CRS, native_bbox=[X0, Y0, X1, Y1],
                             out_crs=OUT_CRS, out_bbox=[ox, cx[2][1], cx[1][0], oy], pixel_m=[px, py],
                             note="인쇄좌표=EPSG:5176(동경측지계). 5183 가정 시 +57/+300m 오차"))
    json.dump(manifest, open(PROCESSED / "gosi2026-8_georef_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
