"""ITS 스냅샷 × 표준노드링크 → 교통 레이어.
 - processed/traffic_links_4326.geojson : 링크 기하 + 최신 속도 + 혼잡도(속도/제한속도) + 시간대별 평균(수집분)
 - processed/traffic_hourly.json        : 시간대별 평균 속도·혼잡링크 비율 (사이드바)
 - processed/traffic_congested.json     : 상습 혼잡 링크 상위 (도로명·평균속도·혼잡 빈도)
"""
import sys, json, glob, collections, statistics
from _common import RAW, PROCESSED, speed_thr, speed_level

SNAP = sorted(glob.glob(str(RAW / "its_traffic" / "*.json")))
MIN_OBS = 6   # '상습' 판정 최소 관측수 (5분 스냅샷 6개 = 30분) — 이보다 적으면 목록에서 제외


def main():
    nl = json.load(open(PROCESSED / "nodelink_gj_4326.geojson", encoding="utf-8"))
    byid = {f["properties"]["LINK_ID"]: f for f in nl["features"]}
    snaps = [json.load(open(p, encoding="utf-8")) for p in SNAP]
    print(f"스냅샷 {len(snaps)}개 ({snaps[0]['ts']} ~ {snaps[-1]['ts']}) | 노드링크 {len(byid)}")
    hist = collections.defaultdict(list)     # linkId -> [(ts, speed)]
    for s in snaps:
        for r in s["rows"]:
            if r["speed"] is not None: hist[r["linkId"]].append((s["ts"], r["speed"], r["road"]))
    matched = [k for k in hist if k in byid]
    print(f"ITS 링크 {len(hist)} 중 노드링크 매칭 {len(matched)} ({len(matched)/len(hist)*100:.1f}%)")
    latest = snaps[-1]["ts"]
    feats = []; hourly = collections.defaultdict(list); cong = []
    for lid in matched:
        f = byid[lid]; p = dict(f["properties"]); h = hist[lid]
        spd_now = next((v for t, v, _ in reversed(h) if t == latest), None)
        maxspd = float(p.get("MAX_SPD") or 0) or None
        speeds = [v for _, v, _ in h]
        thr_c, thr_f = speed_thr(p.get("ROAD_RANK"))
        p.update(speed=spd_now, speed_avg=round(statistics.mean(speeds), 1), n_obs=len(h), road_its=h[-1][2],
                 ratio=round(spd_now / maxspd, 2) if (spd_now is not None and maxspd) else None,
                 thr_c=thr_c, thr_f=thr_f, level=speed_level(spd_now, p.get("ROAD_RANK")))
        # 시간대별 (해당 링크)
        byhr = collections.defaultdict(list)
        for t, v, _ in h: byhr[int(t[8:10])].append(v)
        p["hourly"] = {str(k): round(statistics.mean(v), 1) for k, v in sorted(byhr.items())}
        cong_cnt = sum(1 for v in speeds if v < thr_c)
        if len(speeds) >= MIN_OBS: cong.append((cong_cnt / len(speeds), lid, p.get("ROAD_NAME") or p["road_its"], p["speed_avg"], len(speeds)))
        for k, v in byhr.items(): hourly[k] += [(x, thr_c) for x in v]
        feats.append({"type": "Feature", "geometry": f["geometry"], "properties": p})
    fc = {"type": "FeatureCollection", "features": feats}
    (PROCESSED / "traffic_links_4326.geojson").write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
    hr = {str(k): {"speed_avg": round(statistics.mean(x for x, _ in v), 1), "congested_pct": round(sum(1 for x, c in v if x < c) / len(v) * 100, 1), "n": len(v)} for k, v in sorted(hourly.items())}
    json.dump({"latest": latest, "snapshots": len(snaps), "first": snaps[0]["ts"], "min_obs": MIN_OBS, "hourly": hr}, open(PROCESSED / "traffic_hourly.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cong.sort(reverse=True)
    top = [{"linkId": l, "road": r, "congested_pct": round(c * 100), "speed_avg": s, "n": n} for c, l, r, s, n in cong[:25] if c > 0]
    json.dump(top, open(PROCESSED / "traffic_congested.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    lv = collections.Counter(f["properties"]["level"] for f in feats)
    print(f"교통 링크 {len(feats)} 저장 | 현재 {dict(lv)} | 시간대 {list(hr.keys())}")
    print("  상습혼잡 상위:", [(t["road"], t["congested_pct"], t["speed_avg"]) for t in top[:8]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
