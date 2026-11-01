"""두 PDF에서 필요한 그림을 잘라 assets/crops/ 에 저장한다(쪽 영역을 고해상도로 렌더).
각 항목: 이름 → (pdf키, 쪽, bbox(pt), dpi). 출처 문구는 CROPS_META 로 같이 남긴다."""
import os, json, sys
import pymupdf
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "crops"); os.makedirs(OUT, exist_ok=True)
PDFS = {"A": r"C:\Users\OFFICE\Desktop\9_도시\#경주시 원도심 미래구상 기획 연구 0804 최종본.pdf",
        "B": r"C:\Users\OFFICE\Desktop\9_도시\22-0124) 경주시 도시재생전략계획 최종보고서.pdf"}
SRC = {"A": "경주시 원도심 미래구상 기획 연구(경주시 미래전략실·동국대 산학협력단, 2025) p.%d", "B": "경주시 도시재생 전략계획(변경) 최종보고서(2022) PDF p.%d"}
CROPS = {
    # 417쪽 연구
    "A_p64_aerial":        ("A", 64,  (71, 93, 525, 347), 220),
    "A_p105_photo1":       ("A", 105, (41, 177, 208, 342), 260),
    "A_p105_photo2":       ("A", 105, (214, 177, 381, 342), 260),
    "A_p105_photo3":       ("A", 105, (387, 177, 554, 342), 260),
    "A_p28_rail_1992_2021": ("A", 28, (74, 57, 522, 526), 200),
    "A_p26_rail_1918_1939": ("A", 26, (74, 172, 522, 641), 200),
    "A_p106_walk_map":     ("A", 106, (269, 446, 553, 729), 260),
    "A_p106_func_map":     ("A", 106, (269, 106, 553, 390), 260),
    "A_p85_section_now":   ("A", 85,  (43, 171, 596, 335), 220),
    "A_p10_study_area":    ("A", 10,  (71, 57, 519, 526), 200),
    # 도시재생전략계획
    "B_p300_assets_strip": ("B", 300, (125, 126, 518, 258), 220),
    "B_p393_aerial":       ("B", 393, (137, 285, 529, 483), 260),
    "B_p97_rail_map":      ("B", 97,  (120, 318, 535, 613), 220),
    "B_p97_station_photo": ("B", 97,  (137, 644, 529, 739), 220),
    "B_p148_table":        ("B", 148, (118, 455, 524, 592), 260),
    "B_p186_concept":      ("B", 186, (110, 100, 530, 420), 200),
}
if __name__ == "__main__":
    docs = {k: pymupdf.open(v) for k, v in PDFS.items()}
    meta = {}
    only = set(sys.argv[1:])
    for name, (k, p, bb, dpi) in CROPS.items():
        if only and name not in only: continue
        pg = docs[k][p - 1]; z = dpi / 72.0
        pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*bb), alpha=False)
        path = os.path.join(OUT, name + ".png"); pix.save(path)
        meta[name] = dict(file=path, source=SRC[k] % p, px=[pix.width, pix.height])
        print(name, pix.width, "x", pix.height)
    mp = os.path.join(OUT, "_meta.json")
    old = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
    old.update(meta); json.dump(old, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
