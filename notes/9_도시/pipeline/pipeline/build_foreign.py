"""외국인주민·다문화가구(행안부 2024, 읍면동) → 행정동 폴리곤 조인 + 외국인 관련 상점·시설 키워드 추출.
주의: 2024 통계는 중부동이 별도 → 2025 통합 반영해 황오동에 합산. 비율 분모 = 주민등록 인구(2026-08) — 시점 불일치 근사."""
import sys, json, re, collections
from _common import RAW, PROCESSED

FT = json.load(open(RAW / "kosis_foreign_emd_2024.json", encoding="utf-8"))
MC = json.load(open(RAW / "kosis_multicultural_emd_2024.json", encoding="utf-8"))
MERGE = {"중부동": "황오동"}


def agg(table, names):
    out = collections.Counter()
    for n in names:
        for k, v in table.get(n, {}).items(): out[k] += v
    return out


def main():
    fc = json.load(open(PROCESSED / "hadm_pop_4326.geojson", encoding="utf-8"))
    for f in fc["features"]:
        p = f["properties"]; h = p["hadm"]
        srcs = [h] + [k for k, v in MERGE.items() if v == h]
        ft = agg(FT["table"], srcs); mc = agg(MC["table"], srcs)
        tot = ft.get("합계", 0); pop = p.get("pop") or 0
        p.update(fr_total=tot, fr_worker=ft.get("외국인근로자", 0), fr_marriage=ft.get("결혼이민자", 0), fr_student=ft.get("유학생", 0),
                 fr_diaspora=ft.get("외국국적동포", 0), fr_other=ft.get("기타외국인", 0), fr_naturalized=ft.get("한국국적을 취득한 자", 0), fr_children=ft.get("외국인주민자녀(출생)", 0),
                 fr_noncitizen=ft.get("한국국적을 가지지 않은 자", 0),
                 fr_pct=round(tot / (pop + ft.get("한국국적을 가지지 않은 자", 0)) * 100, 1) if pop else None,
                 mc_households=mc.get("합계", 0), mc_marriage=mc.get("결혼이민자", 0), mc_children=mc.get("자녀", 0),
                 fr_year=FT["prd"], fr_note="행안부 외국인주민현황 2024 (중부동→황오동 합산) / 비율 분모 = 주민등록 2026-08 + 미취득 외국인")
        p["lbl_fr"] = f"{h}\n{tot:,} ({p['fr_pct']}%)" if pop else h
        p["lbl_mc"] = f"{h}\n{mc.get('합계', 0):,}가구"
    (PROCESSED / "hadm_pop_4326.geojson").write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
    rows = sorted((f["properties"] for f in fc["features"]), key=lambda p: -p["fr_total"])
    print(f"{'행정동':6s} {'외국인주민':>8s} {'비율':>6s} {'근로자':>6s} {'동포':>6s} {'유학생':>6s} {'다문화가구':>8s}")
    for p in rows[:10]: print(f"{p['hadm']:6s} {p['fr_total']:8,} {p['fr_pct']:6} {p['fr_worker']:6,} {p['fr_diaspora']:6,} {p['fr_student']:6,} {p['mc_households']:8,}")

    # 외국인 관련 상점·시설 — 상호 키워드 (추정. 팝업에 근거 키워드 표기)
    KW = {"중앙아시아·고려인": r"러시아|우즈벡|우즈베키|카자흐|고려인|사마르칸트|타슈켄트|키르기|CIS|중앙아시아|아리랑마트|미르(?!\w)",
          "동남아": r"베트남|비엣|하노이|사이공|포(?=\s|$)|캄보디아|태국|타이(?!어)|필리핀|인도네시아|인니|미얀마|네팔|스리랑카|방글라|라오스",
          "할랄·이슬람": r"할랄|halal|케밥|kebab|이슬람|무슬림|모스크|마스지드|튀르키예|터키|파키스탄|아랍",
          "중국·기타": r"중국식품|중국마트|양꼬치|조선족|몽골|아시아마트|아시안마트|외국인마트|다국적|글로벌마트",
          "지원시설": r"다문화|외국인.{0,4}(지원|센터|상담)|한국어교육|가족센터|이주민|글로벌센터|이주노동"}
    st = json.load(open(PROCESSED / "stores_merged_4326.geojson", encoding="utf-8"))
    feats = []; cnt = collections.Counter()
    for f in st["features"]:
        pr = f["properties"]; name = pr.get("bizesNm") or ""; scls = pr.get("indsSclsNm") or ""
        hit = None
        for cat, pat in KW.items():                       # 1순위: 상호명 키워드 (외국인 커뮤니티 상점·시설 추정)
            m = re.search(pat, name, flags=re.I)
            if m: hit = (cat, m.group(0), "상호"); break
        if not hit and re.search(r"베트남식|동남아식|중국식|인도식|터키식|아시아", scls):   # 2순위: 업종만 (한국인 운영 프랜차이즈 포함 — 약한 근거)
            hit = ("외국 음식 업종", scls, "업종")
        if hit:
            q = dict(pr); q.update(fr_cat=hit[0], fr_kw=hit[1], fr_basis=hit[2]); feats.append({"type": "Feature", "geometry": f["geometry"], "properties": q}); cnt[hit[0]] += 1
    (PROCESSED / "foreign_places_4326.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False), encoding="utf-8")
    print("\n외국인 관련 상점·시설(키워드):", dict(cnt), "총", len(feats))
    for f in feats[:12]: print("  ", f["properties"]["fr_cat"], "|", f["properties"]["bizesNm"], "|", f["properties"].get("indsSclsNm"), "|", f["properties"].get("lnoAdr"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
