"""행정동 경계 근사: V-World 법정동 폴리곤 56개 → 중심점 역지오코딩(level4A=행정동) → 행정동별 합집합.
한계: 법정동이 두 행정동에 걸치는 경우 중심점이 속한 쪽으로 통째로 귀속됨. SGIS 행정동 경계 확보 시 교체."""
import os, sys, json, collections
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from _common import load_env, get_json, RAW, PROCESSED


def main():
    load_env(); key = os.environ["VWORLD_KEY"]; h = {"Referer": os.environ["VWORLD_DOMAIN"], "User-Agent": "Mozilla/5.0"}
    emd = json.load(open(RAW / "vworld_emd_gj.geojson", encoding="utf-8"))["features"]
    pop = json.load(open(PROCESSED / "pop_emd_table.json", encoding="utf-8"))
    byname = {d["name"]: d for d in pop.values()}
    groups = collections.defaultdict(list); mapping_ = {}
    for f in emd:
        g = shape(f["geometry"]); c = g.representative_point()
        nm = f["properties"]["emd_kor_nm"]; hadm = None
        if nm.endswith(("읍", "면")): hadm = nm            # 읍·면은 법정=행정
        else:
            # 역지오코딩(level4A 비어 있음) → 필지 주소 문자열 → 정방향 지오코딩(level4A=행정동)
            import urllib.parse
            # 폴리곤 내부 격자 표본점 최대 12개 — '산' 지번(임야)은 행정동이 안 붙는 경우가 많아 건너뜀
            from shapely.geometry import Point
            minx, miny, maxx, maxy = g.bounds; pts = [c, g.centroid]
            for i in range(1, 4):
                for jx in range(1, 4):
                    q = Point(minx + (maxx - minx) * i / 4, miny + (maxy - miny) * jx / 4)
                    if g.contains(q): pts.append(q)
            for pt in pts[:12]:
                j = get_json(f"https://api.vworld.kr/req/address?service=address&request=getAddress&version=2.0&crs=EPSG:4326&point={pt.x},{pt.y}&type=parcel&format=json&key={key}", h, retries=2)["response"]
                if j["status"] != "OK": continue
                addr = j["result"][0]["text"]
                if " 산 " in addr or addr.endswith(nm): continue
                k = get_json(f"https://api.vworld.kr/req/address?service=address&request=getcoord&version=2.0&crs=EPSG:4326&type=PARCEL&address={urllib.parse.quote(addr)}&format=json&key={key}", h, retries=2)["response"]
                if k["status"] == "OK" and k["refined"]["structure"].get("level4A"): hadm = k["refined"]["structure"]["level4A"]; break
        # 임야 위주 법정동: 지오코딩 실패 → 경주시 행정동 관할 기준 수동 배정 [확인 필요 — SGIS 경계로 대체 예정]
        MANUAL = {"인왕동": "월성동", "남산동": "월성동", "도지동": "월성동", "구황동": "월성동", "시동": "월성동",
                  "탑동": "황남동", "율동": "황남동", "효현동": "선도동", "광명동": "선도동",
                  "마동": "불국동", "구정동": "불국동", "덕동": "보덕동", "황용동": "보덕동"}
        if not hadm and nm in MANUAL: hadm = MANUAL[nm]; f["properties"]["_manual"] = True
        hadm = hadm or "?"
        mapping_[f["properties"]["emd_kor_nm"]] = hadm; groups[hadm].append(g)
    print("법정동→행정동:", dict(sorted(mapping_.items(), key=lambda x: x[1])))
    feats = []
    for hadm, gs in groups.items():
        u = unary_union(gs).buffer(0)
        polys = [orient(x, 1.0) for x in (u.geoms if u.geom_type == "MultiPolygon" else [u])]
        d = byname.get(hadm, {})
        props = {"hadm": hadm, "bjd": [n for n, hh in mapping_.items() if hh == hadm], "note": "법정동 합집합 근사(역지오코딩) · 임야 법정동 일부 수동 배정", "pop": d.get("sex", {}).get("total"), "male": d.get("sex", {}).get("male"), "female": d.get("sex", {}).get("female"),
                 "pct_65": d.get("pct_65"), "pct_0_14": d.get("pct_0_14"), "pct_20_39": d.get("pct_20_39"), "chg_10y_pct": d.get("chg_10y_pct"), "prd": d.get("prd"), "code": d.get("code"),
                 "age": d.get("age"), "yearly": d.get("yearly"), "yearly_note": d.get("yearly_note")}
        # 면적(㎢)은 EPSG:5187에서 정확히
        from shapely.ops import transform as stf
        from pyproj import Transformer
        t = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True).transform
        area_km2 = stf(t, unary_union(gs)).area / 1e6
        props["area_km2"] = round(area_km2, 2)
        props["density"] = round(props["pop"] / area_km2) if props.get("pop") else None          # 명/㎢
        a = d.get("age") or {}
        lo = lambda k: int(k.replace("+", "").split("-")[0].strip().replace("세", ""))
        n65 = sum(v for k, v in a.items() if lo(k) >= 65); nyo = sum(v for k, v in a.items() if 20 <= lo(k) <= 35); n014 = sum(v for k, v in a.items() if lo(k) <= 10)
        ny2034 = sum(v for k, v in a.items() if 20 <= lo(k) <= 30)   # 20–34세 (청년기본법 19–34에 가장 가까운 5세 구간)
        props.update(n_65=n65, n_youth=nyo, n_0_14=n014, pct_youth=round(nyo / props["pop"] * 100, 1) if props.get("pop") else None,
                     n_y2034=ny2034, pct_y2034=round(ny2034 / props["pop"] * 100, 1) if props.get("pop") else None)
        NL = chr(10)
        f_ = lambda n, pc: hadm + NL + f"{n:,} ({pc}%)"
        props["lbl_pop"] = hadm + NL + f"{props['pop']:,}" if props.get("pop") else hadm
        props["lbl_den"] = hadm + NL + f"{props['density']:,}/㎢" if props.get("density") else hadm
        props["lbl_65"] = f_(n65, props["pct_65"]) if props.get("pop") else hadm
        props["lbl_youth"] = f_(nyo, props["pct_youth"]) if props.get("pop") else hadm
        props["lbl_y2034"] = f_(ny2034, props["pct_y2034"]) if props.get("pop") else hadm
        feats.append({"type": "Feature", "geometry": mapping(unary_union(polys)), "properties": props})
    unmatched = [n for n in byname if n not in groups and n != "경주시"]
    print("행정동 폴리곤", len(feats), "| 인구표에 있으나 경계 없음:", unmatched)
    (PROCESSED / "hadm_pop_4326.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
