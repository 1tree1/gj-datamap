"""청년 카드용 표 — 시 단위 취업 구조(지역별고용조사) + 연령별 순이동(국내인구이동통계) + 행정동 20–34세 순위.
입력: raw/kosis_employment_gj.json (C-027), raw/kosis_netmigration_gj.json (C-028), processed/hadm_pop_4326.geojson
출력: processed/youth_city.json"""
import sys, json, collections
from _common import RAW, PROCESSED, save


def main():
    emp = json.load(open(RAW / "kosis_employment_gj.json", encoding="utf-8"))
    def rows(tbl, itm_prefix="취업자"):
        out = []
        for r in emp[tbl]:
            if r["ITM_NM"].startswith(itm_prefix) and r["DT"] not in (None, "-"):
                out.append((r["C2_NM"].strip(), float(r["DT"])))
        return out
    ind = [(k, v) for k, v in rows("DT_1ES3A30S") if k != "계"]
    occ = [(k, v) for k, v in rows("DT_1ES3A31S") if k != "계"]
    age = [(k, v) for k, v in rows("DT_1ES3A03_A01S", "취업자")]
    rate = [(r["C2_NM"].strip(), float(r["DT"])) for r in emp["DT_1ES3A03_A01S"] if r["ITM_NM"].startswith("고용률")]
    prd = emp["DT_1ES3A30S"][0]["PRD_DE"]
    total = next(v for k, v in rows("DT_1ES3A30S") if k == "계")

    mig = json.load(open(RAW / "kosis_netmigration_gj.json", encoding="utf-8"))
    by = collections.defaultdict(dict)
    for r in mig:
        if r.get("C2_NM") == "계": by[r["PRD_DE"]][r["C3_NM"].replace(" ", "")] = int(r["DT"])
    years = sorted(by)
    bands = ["15-19세", "20-24세", "25-29세", "30-34세", "35-39세"]
    net = {b: [by[y].get(b) for y in years] for b in bands}
    net["계"] = [by[y].get("계") for y in years]
    net["20-34세"] = [sum(by[y].get(b, 0) for b in bands[1:4]) for y in years]

    hp = json.load(open(PROCESSED / "hadm_pop_4326.geojson", encoding="utf-8"))
    dong = sorted([{"hadm": f["properties"]["hadm"], "n": f["properties"].get("n_y2034"), "pct": f["properties"].get("pct_y2034"), "pop": f["properties"].get("pop")}
                   for f in hp["features"] if f["properties"].get("n_y2034") is not None], key=lambda x: -x["n"])
    city_n = sum(d["n"] for d in dong); city_pop = sum(d["pop"] for d in dong)
    out = {"emp_prd": prd, "emp_total_k": total, "industry": ind, "occupation": occ, "age_emp": age, "age_rate": rate,
           "emp_src": "통계청 지역별고용조사 (KOSIS DT_1ES3A30S·A31S·A03_A01S), 전 연령. 연령×산업 교차는 시군구 미공표",
           "mig_years": years, "net": net, "mig_src": "통계청 국내인구이동통계 (KOSIS DT_1B26002) 경주시 순이동자수",
           "dong": dong, "city_y2034": city_n, "city_pop": city_pop, "city_pct": round(city_n / city_pop * 100, 1),
           "dong_src": "행안부 주민등록 2026-08 (KOSIS DT_1B04005N) 5세별 → 20–34세 합"}
    save(out, PROCESSED / "youth_city.json")
    print(f"  취업자 {total}천명 ({prd}) · 20–34세 {city_n:,} ({out['city_pct']}%) · 순이동 {years[0]}~{years[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
