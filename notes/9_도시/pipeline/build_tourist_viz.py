"""경주 관광객 수·유형 시각화 페이지 빌드 — work/20261001_경주_관광객_수와_유형_v1.md 의 표를 HTML 한 장으로.

  python build_tourist_viz.py

입력
  - archive/C_data/processed/visitors_gyeongju_summary.json   (데이터랩 API 일별 → 월·요일)
  - archive/C_data/raw/datalab_gyeongju_web_20261001.json     (데이터랩 화면값: 성·연령, 거주지, 외국인 국적 등)
  - archive/C_data/processed/visitor_origin_sigg_4326.geojson (유입 시군구 — 지도)
  - archive/C_data/processed/arrival_counts.json              (철도·IC 실측)
  - 경주시 관광실태조사(B-009) 표 값은 아래 SURVEY 에 보고서 쪽수와 함께 직접 기입
출력
  - work/20261001_경주_관광객_시각화_v1.html  (pipeline/tourist_viz_template.html 의 /*__DATA__*/ 치환, 아티팩트용 조각)
  - gj-datamap/public/tourists.html           (같은 내용 + 문서 골격 + 사이트 메뉴, main 푸시 → GitHub Pages)

지도는 EPSG:5179로 투영해 1.2 km 허용오차로 단순화한 SVG 경로다. 울릉군(47940)은 판형 때문에 뺀다.
"""
import json
from pathlib import Path
from shapely.geometry import shape, mapping
from shapely.ops import transform, unary_union
from pyproj import Transformer
from _common import ROOT, RAW, PROCESSED, SITE_LON, SITE_LAT

OUT = ROOT / "work" / "20261001_경주_관광객_시각화_v1.html"
TPL = Path(__file__).parent / "tourist_viz_template.html"
SITE = ROOT / "gj-datamap" / "public" / "tourists.html"   # https://1tree1.github.io/gj-datamap/tourists.html

# 경주시 관광실태조사 제5회(2025.11) — 내국인 p.22·23·24·37, 외국인 p.55 (T2, 국가승인통계)
SURVEY = {
    "modes": ["자가용", "KTX/SRT", "전세·관광버스", "시외버스", "고속버스", "일반열차", "렌터카·기타"],
    "trend": [  # 연도, n, 값(위 순서)
        ["2013", 2593, [60.0, 5.2, 12.8, 5.4, 6.5, 7.7, 2.3]],
        ["2014", 3949, [64.3, 6.2, 6.6, 5.6, 6.5, 9.2, 1.6]],
        ["2017", 3960, [74.6, 7.5, 5.7, 3.2, 4.0, 3.4, 1.5]],
        ["2021", 2278, [84.2, 8.1, 0.4, 2.2, 2.2, 2.4, 0.5]],
        ["2024", 3009, [76.9, 8.5, 8.3, 2.0, 1.8, 1.7, 0.8]],
    ],
    "by_group": [
        ["수도권", 811, [65.2, 21.1, 6.8, 1.1, 2.8, 2.5, 0.6]],
        ["대경권", 917, [88.3, 3.2, 3.2, 2.3, 1.2, 1.4, 0.3]],
        ["동남권", 733, [79.9, 2.7, 9.2, 3.6, 2.3, 1.5, 0.8]],
        ["그 외 지역", 547, [71.0, 6.2, 17.8, 1.0, 0.8, 1.3, 2.0]],
        ["15–19세", 96, [47.5, 10.1, 24.6, 12.8, 3.1, 0.0, 2.0]],
        ["20대", 607, [64.6, 15.8, 5.4, 4.9, 4.6, 3.5, 1.2]],
        ["30대", 615, [80.5, 10.3, 3.7, 1.3, 1.7, 2.2, 0.2]],
        ["40대", 662, [87.0, 6.6, 4.0, 1.2, 0.5, 0.5, 0.2]],
        ["50대", 484, [80.9, 4.9, 9.5, 0.7, 1.5, 1.9, 0.7]],
        ["60세 이상", 545, [75.8, 3.3, 17.9, 0.0, 0.6, 0.7, 1.8]],
    ],
    "foreign_modes": ["일반버스", "택시", "관광버스", "자가용(렌트 포함)", "기차"],
    "foreign": [["2017", 785, [48.2, 7.6, 23.2, 16.3, 4.6]], ["2024", 1002, [38.5, 25.1, 18.0, 13.1, 5.1]]],
    "daytrip": [["2013", 44.6], ["2014", 41.9], ["2017", 37.5], ["2021", 33.1], ["2024", 44.7]],
    "group_tour": [["2021", 0.4], ["2024", 22.2]],
    "companion": [["친구·연인", 41.5], ["가족·친지(부모·자녀 동반)", 36.2]],
}

# 데이터랩 외지인 연령 연도값(서브에이전트 내부조회 대조, 보도자료와 일치) — 2025.09–2026.08은 화면값
AGE_YEARS = {
    "cols": ["0–9", "10대", "20대", "30대", "40대", "50대", "60대", "70+"],
    "2019": [1.3, 7.5, 20.8, 17.7, 18.7, 20.3, 10.2, 3.4],
    "2023": [1.6, 6.4, 19.0, 17.4, 17.1, 19.5, 14.2, 4.9],
    "2024": [1.5, 6.1, 17.8, 17.6, 16.7, 19.8, 15.2, 5.4],
    "2025": [1.3, 6.1, 16.8, 18.3, 16.6, 19.3, 15.7, 5.9],
}
ANNUAL = {  # 데이터랩 외지인 연인원(경주시 발표 '관광객'), 주요관광지점 입장객 합계
    "years": ["2019", "2022", "2023", "2024", "2025"],
    "outsider": [42740000, 45090000, 47543035, 47098236, 50203225],
    "foreign": [None, None, None, 1184000, 1385000],
    "spots": [10385000, 9171000, 9589000, 9710000, 10216000],
    "spots_n": [24, 24, 24, 16, 16],
}
GB_SHARE = [["대만", 64.5], ["싱가포르", 53.9], ["프랑스", 46.9], ["독일", 44.6], ["홍콩", 39.5],
            ["일본", 23.9], ["중국", 22.9], ["미국", 20.8], ["베트남", 8.8]]  # 2025, 경북 외국인 연인원 중 경주 비중(근사)


def build_map():
    g = json.load(open(PROCESSED / "visitor_origin_sigg_4326.geojson", encoding="utf-8"))
    tr = Transformer.from_crs("EPSG:4326", "EPSG:5179", always_xy=True).transform
    feats = []
    for f in g["features"]:
        p = f["properties"]
        if p["sig_cd"] == "47940":
            continue
        geom = transform(tr, shape(f["geometry"])).simplify(1200, preserve_topology=True)
        if geom.is_empty:
            continue
        feats.append((p, geom))
    # 경주시는 유입 표에 없음 → 별도 경계(유입 표 경계 파일에 있으면 사용)
    minx = min(gm.bounds[0] for _, gm in feats); miny = min(gm.bounds[1] for _, gm in feats)
    maxx = max(gm.bounds[2] for _, gm in feats); maxy = max(gm.bounds[3] for _, gm in feats)
    W = 480.0; s = W / (maxx - minx); H = (maxy - miny) * s

    def path(geom):
        polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        out = []
        for pg in polys:
            for ring in [pg.exterior] + list(pg.interiors):
                pts = [f"{(x - minx) * s:.1f},{(maxy - y) * s:.1f}" for x, y in ring.coords]
                if len(pts) >= 4:
                    out.append("M" + "L".join(pts) + "Z")
        return "".join(out)

    rows = []
    for p, gm in feats:
        rows.append({"cd": p["sig_cd"], "nm": p["full_nm"], "v": p["visitors"], "sh": p["share_pct"],
                     "pv": p.get("spend_per_visitor"), "d": path(gm)})
    # 시도 외곽선(시군구 코드 앞 2자리로 병합)
    sido = {}
    for p, gm in feats:
        sido.setdefault(p["sig_cd"][:2], []).append(gm.buffer(30))
    outlines = [path(unary_union(v).buffer(-30).simplify(800)) for v in sido.values()]
    # 경주 표시점 = 구경주역 구역 중심 — 유입 표에는 목적지인 경주가 없다
    gx, gy = tr(SITE_LON, SITE_LAT)
    return {"w": W, "h": round(H, 1), "sgg": rows, "sido": outlines,
            "gj": [round((gx - minx) * s, 1), round((maxy - gy) * s, 1)],
            "total": sum(r["v"] or 0 for r in rows)}


def main():
    vs = json.load(open(PROCESSED / "visitors_gyeongju_summary.json", encoding="utf-8"))
    web = json.load(open(RAW / "datalab_gyeongju_web_20261001.json", encoding="utf-8"))
    ac = json.load(open(PROCESSED / "arrival_counts.json", encoding="utf-8"))

    monthly = [[m, r["외지인"], r["외국인"]] for m, r in vs["monthly"].items() if r["완전한달"]]
    dow_order = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    dow = [[d[0], vs["dow_avg"][d]["외지인"], vs["dow_avg"][d]["외국인"]] for d in dow_order]

    a = web["age_sex_pct_outsider"]
    pyramid = [[k, a["male"][k], a["female"][k]] for k in a["male"]]
    card = web["card_spend_pct_domestic"]
    card_age = {k: round(card["male"][k] + card["female"][k], 1) for k in card["male"]}

    res = web["residence_outsider_sido"]; tot = res["total"]
    sido = sorted([[k, v, round(v / tot * 100, 1)] for k, v in res.items() if k != "total"], key=lambda x: -x[1])
    dist = web["distance_outsider"]; dt = sum(dist.values())
    distance = [[k, round(v / dt * 100, 1)] for k, v in dist.items()]

    fn = web["foreign_by_nationality"]; fm = web["foreign_monthly"]
    ta = sum(fm["2025-09~2026-08"].values()); tb = sum(fm["2024-09~2025-08"].values())
    prev = dict(fn["2024-09~2025-08"])
    foreign = [[k, v, round(v / ta * 100, 1), prev[k], round((v / prev[k] - 1) * 100)] for k, v in fn["2025-09~2026-08"] if v > 15000]
    foreign.append(["기타", ta - sum(v for _, v in fn["2025-09~2026-08"] if v > 15000),
                    None, tb - sum(v for k, v in fn["2024-09~2025-08"] if dict(fn["2025-09~2026-08"])[k] > 15000), None])
    foreign[-1][2] = round(foreign[-1][1] / ta * 100, 1)

    s = ac["summary"]
    counts = {
        "rail": [[y, s["철도_하차(명)"][y]["연간"], s["철도_하차(명)"][y]["일평균"]] for y in ("2023", "2024")],
        "rail_wk": s["철도_경주역_2024_주말/평일(승+하)"],
        "ic": s["고속도로_4IC_2025_진출(대)"],
        "air": s["항공_포항경주_도착(명)"],
        "ic_by_unit": [["경주", 18526, 17952], ["남경주", 5916, 5692], ["서경주", 4776, 4410], ["동경주", 3482, 3395]],
        "weekend": [["데이터랩 외지인(연인원)", 1.63], ["경주역 철도(승+하)", 1.40], ["IC 승용 진출", 1.44], ["IC 3종(대형버스+화물)", 0.59]],
    }

    data = {
        "annual": ANNUAL, "monthly": monthly, "dow": dow,
        "uniq": web["unique_visitors_monthly_outsider"], "nights": web["nights_dist_pct_overnight"],
        "pyramid": pyramid, "age_years": AGE_YEARS, "card_age": card_age,
        "sido": sido, "top_sgg": web["residence_outsider_top25_sgg"][:12], "res_total": tot,
        "distance": distance, "navi_top5": web["navi_inflow_origin_top5_pct"],
        "foreign": foreign, "foreign_total": [ta, tb], "gb_share": GB_SHARE,
        "foreign_monthly": fm,
        "survey": SURVEY, "counts": counts, "map": build_map(),
    }
    html = TPL.read_text(encoding="utf-8").replace("/*__DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";")
    # 아티팩트용(골격은 게시 때 씌워짐)
    OUT.write_text(html.replace("<!--__SITENAV__-->", ""), encoding="utf-8")
    print(f"저장: {OUT}  ({OUT.stat().st_size/1024:.0f} KB, 지도 시군구 {len(data['map']['sgg'])}개)")
    # gj-datamap 사이트용 — 문서 골격 + 상단 메뉴. public/ 은 vite가 그대로 복사한다
    if SITE.parent.exists():
        nav = ('<nav class="sitenav" aria-label="사이트"><a href="./index.html">지도</a>'
               '<a href="./report.html">통계 리포트</a><a class="on" href="./tourists.html" aria-current="page">관광객</a></nav>')
        SITE.write_text('<!doctype html>\n<html lang="ko">\n' + html.replace("<!--__SITENAV__-->", nav) + "\n</html>\n", encoding="utf-8")
        print(f"저장: {SITE}")


if __name__ == "__main__":
    main()
