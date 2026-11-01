"""KOSIS 주민등록 인구 — 경주시 행정동(읍면동)별 5세별·성별 (DT_1B04005N, 월). + 연도별 시계열(행정동 총인구).
출력: raw/kosis_pop_emd_5age.json, processed/pop_emd_table.json (사이드바·조인용)"""
import os, sys, json, collections, urllib.parse
from _common import load_env, get_json, RAW, PROCESSED

MERGED = [("4713051500", "4713053000", "중부동")]   # (폐지 코드, 흡수 코드, 이름)
BASE = "https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&orgId=101&tblId=DT_1B04005N&format=json&jsonVD=Y"


def main():
    load_env(); K = os.environ["KOSIS_KEY"]
    # 경주 행정동 코드: 전국 목록에서 47130 하위
    allrows = json.load(open(RAW / "kosis_jumin_all_202608.json", encoding="utf-8"))
    emd = [(r["C1"], r["C1_NM"]) for r in allrows if r["C1"].startswith("47130") and len(r["C1"]) == 10]
    print("경주 행정동", len(emd), [n for _, n in emd])
    codes = urllib.parse.quote(" ".join(c for c, _ in emd) + " 47130")
    # 최신월 5세별·성별
    j = get_json(f"{BASE}&apiKey={K}&itmId=ALL&objL1={codes}&objL2=ALL&prdSe=M&newEstPrdCnt=1", retries=2)
    if isinstance(j, dict): raise SystemExit(j)
    json.dump(j, open(RAW / "kosis_pop_emd_5age.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("5세별 행", len(j), "기준", j[0]["PRD_DE"])
    # 연도별 총인구 시계열 (2011~) 행정동
    y = get_json(f"{BASE}&apiKey={K}&itmId=T2&objL1={codes}&objL2=0&prdSe=Y&startPrdDe=2011&endPrdDe=2025", retries=2)
    json.dump(y, open(RAW / "kosis_pop_emd_yearly.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("연도별 행", len(y))
    # 정리표
    tab = {}
    for r in j:
        d = tab.setdefault(r["C1"], {"name": r["C1_NM"], "code": r["C1"], "prd": r["PRD_DE"], "age": {}, "sex": {}})
        item = {"T2": "total", "T3": "male", "T4": "female"}.get(r["ITM_ID"], r["ITM_ID"])
        if r["C2"] == "0": d["sex"][item] = int(r["DT"])
        elif item == "total": d["age"][r["C2_NM"]] = int(r["DT"])
    for r in y:
        tab.setdefault(r["C1"], {"name": r["C1_NM"], "code": r["C1"], "age": {}, "sex": {}}).setdefault("yearly", {})[r["PRD_DE"]] = int(r["DT"])
    # 폐지 행정동 시계열 합산: 2025 중부동(4713051500) → 황오동(4713053000). 현행 코드 목록에 없어 objL1=ALL로 받아야 함.
    for old_code, new_code, old_nm in MERGED:
        rows = []   # objL1=ALL은 연 1개씩 (전체 기간은 행 수 제한 초과)
        for yy in range(2011, 2026):
            ya = get_json(f"{BASE}&apiKey={K}&itmId=T2&objL1=ALL&objL2=0&prdSe=Y&startPrdDe={yy}&endPrdDe={yy}", retries=2)
            if isinstance(ya, list): rows += [r for r in ya if r["C1"] == old_code]
        json.dump(rows, open(RAW / f"kosis_pop_emd_yearly_{old_nm}.json", "w", encoding="utf-8"), ensure_ascii=False)
        if new_code in tab and rows:
            yr = tab[new_code].setdefault("yearly", {}); raw_yr = dict(yr)
            for r in rows: yr[r["PRD_DE"]] = yr.get(r["PRD_DE"], 0) + int(r["DT"])
            tab[new_code]["yearly_note"] = f"{old_nm} 합산 ({min(r['PRD_DE'] for r in rows)}~{max(r['PRD_DE'] for r in rows)})"
            tab[new_code]["yearly_raw"] = raw_yr
            print(f"  {old_nm}→{tab[new_code]['name']} 합산: 2015 {raw_yr.get('2015')}+{next((r['DT'] for r in rows if r['PRD_DE']=='2015'), '?')}")
    for d in tab.values():
        a = d["age"]; tot = sum(a.values()) or 1
        lo = lambda k: int(k.replace("+", "").split("-")[0].strip().replace("세", ""))   # '0 - 4세' → 0, '100+' → 100
        d["pct_65"] = round(sum(v for k, v in a.items() if lo(k) >= 65) / tot * 100, 1)
        d["pct_0_14"] = round(sum(v for k, v in a.items() if lo(k) <= 10) / tot * 100, 1)
        d["pct_20_39"] = round(sum(v for k, v in a.items() if 20 <= lo(k) <= 35) / tot * 100, 1)
        yr = d.get("yearly", {})
        if "2015" in yr and "2025" in yr: d["chg_10y_pct"] = round((yr["2025"] - yr["2015"]) / yr["2015"] * 100, 1)
    json.dump(tab, open(PROCESSED / "pop_emd_table.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    core = ["중부동", "황오동", "성건동", "황남동", "월성동", "동천동", "황성동", "용강동"]
    print(f"{'행정동':6s} {'총인구':>8s} {'65세↑%':>7s} {'0-14%':>6s} {'20-39%':>7s} {'10년변화':>8s}")
    for d in sorted(tab.values(), key=lambda x: -x["sex"].get("total", 0)):
        if d["name"] in core or d["code"] == "47130": print(f"{d['name']:6s} {d['sex'].get('total',0):8,d} {d['pct_65']:7} {d['pct_0_14']:6} {d['pct_20_39']:7} {d.get('chg_10y_pct','-'):>8}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
