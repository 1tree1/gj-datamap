# -*- coding: utf-8 -*-
# CBS Kerncijfers wijken en buurten: 델프트·레이던·'s-Hertogenbosch 구시가 wijk 인구 시계열
# 출력: research/data/cbs_binnenstad_pop_20261027.csv  [T2 CBS StatLine OData]
import json, urllib.request, urllib.parse, csv, pathlib
TABLES = {"1995": "37108", "1999": "37681", "2003": "80868ned", "2004-2008": "81903NED", "2009-2012": "70904ned", "2013": "82339NED", "2015": "83220NED", "2018": "84286NED",
          "2020": "84799NED", "2022": "85318NED", "2024": "85984NED", "2025": "86165NED", "2026": "86358NED"}
WIJK = ["050311", "054600", "054601", "079600", "079601"]  # 표 연도별 키 형식이 달라 숫자 부분으로 찾고 제목이 Wijk인 것만 사용
def get(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.load(r)
rows = []
for yr, tid in TABLES.items():
    base = f"https://opendata.cbs.nl/ODataApi/odata/{tid}/"
    try:
        props = get(base + "DataProperties?$format=json")["value"]
    except Exception as e:
        print(yr, tid, "ERR props", e); continue
    keys = {}
    for p in props:
        t = (p.get("Title") or "").strip().lower(); k = p.get("Key")
        if not k: continue
        if t in ("aantal inwoners", "inwoners") and "inw" not in keys: keys["inw"] = k
        if t.startswith("woningvoorraad") and "won" not in keys: keys["won"] = k
        if t.startswith("oppervlakte land") and "land" not in keys: keys["land"] = k
        if t.startswith("oppervlakte totaal") and "tot" not in keys: keys["tot"] = k
    dims = [p["Key"] for p in props if p.get("Type") in ("Dimension", "GeoDimension", "GeoDetail", "TimeDimension")]
    geo = [p["Key"] for p in props if p.get("Type") in ("GeoDimension", "GeoDetail") or (p.get("Type") == "Dimension" and "Wijk" in p["Key"])]
    gkey = geo[0] if geo else "WijkenEnBuurten"
    # 차원 표에서 정확한 키(공백 패딩 포함)를 먼저 찾고 eq 필터로 조회
    try:
        dvals = get(base + gkey + "?" + urllib.parse.urlencode({"$filter": " or ".join(f"substringof('{w}',Key)" for w in WIJK), "$format": "json"}))["value"]
    except Exception as e:
        print(yr, tid, "ERR dim", gkey, dims, e); continue
    exact = [d["Key"] for d in dvals if (d.get("Title") or "").strip().lower().startswith("wijk") or d["Key"].strip().startswith("WK")]
    titles = {d["Key"].strip(): d["Title"].strip() for d in dvals}
    if not exact: print(yr, tid, "no wijk keys"); continue
    flt = " or ".join(f"{gkey} eq '{k}'" for k in exact)
    sel = ",".join([gkey] + [d for d in dims if d != gkey] + list(keys.values()))
    url = base + "TypedDataSet?" + urllib.parse.urlencode({"$filter": flt, "$select": sel, "$format": "json"})
    try:
        vals = get(url)["value"]
    except Exception as e:
        print(yr, tid, "ERR data", e, keys); continue
    for v in vals:
        extra = ";".join(str(v.get(d)).strip() for d in dims if d != gkey)
        rows.append([yr, tid, v[gkey].strip() + " " + titles.get(v[gkey].strip(), ""), extra] + [v.get(keys.get(x)) if keys.get(x) else "" for x in ("inw", "won", "land", "tot")])
        print(rows[-1])
out = pathlib.Path(__file__).parent / "data" / "cbs_binnenstad_pop_20261027.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["table_year", "table_id", "wijk", "extra_dim", "inwoners", "woningvoorraad", "opp_land_ha", "opp_totaal_ha"]); w.writerows(rows)
print("saved", out)
