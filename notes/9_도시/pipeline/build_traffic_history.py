"""이력 스냅샷(its_history/*.csv.gz) → 링크별 시간대 평균속도 (평일/주말) + 시간대별 도시 전체 요약.
출력: processed/traffic_hist_links_4326.geojson  (링크 기하 + wd_00..wd_23, we_00..we_23 평균속도, 관측수)
      processed/traffic_hist_summary.json         (시간대 × 평일/주말 평균속도·정체링크비율, 표본일 목록)"""
import sys, json, glob, gzip, csv, datetime, collections, statistics
from _common import RAW, PROCESSED, speed_thr

HIST = RAW / "its_history"


def main():
    files = sorted(glob.glob(str(HIST / "2*.csv.gz")))
    if not files: print("이력 없음"); return 1
    nl = json.load(open(PROCESSED / "nodelink_gj_4326.geojson", encoding="utf-8"))
    byid = {f["properties"]["LINK_ID"]: f for f in nl["features"]}
    # acc[link][kind][hour] = [sum, n]
    acc = collections.defaultdict(lambda: {"wd": [[0.0, 0] for _ in range(24)], "we": [[0.0, 0] for _ in range(24)]})
    days = {"wd": [], "we": []}
    for fp in files:
        ymd = fp.split("\\")[-1].split("/")[-1][:8]
        d = datetime.date(int(ymd[:4]), int(ymd[4:6]), int(ymd[6:8]))
        kind = "we" if d.weekday() >= 5 else "wd"; days[kind].append(ymd)
        with gzip.open(fp, "rt", encoding="utf-8") as g:
            rd = csv.reader(g); next(rd, None)
            for lid, hm, sp in rd:
                try: v = float(sp)
                except: continue
                if v <= 0 or lid not in byid: continue
                h = int(hm[:2]); a = acc[lid][kind][h]; a[0] += v; a[1] += 1
    feats = []; city = {k: [[0.0, 0, 0] for _ in range(24)] for k in ("wd", "we")}  # sum, n, congested(도로등급별 임계 미만)
    for lid, kinds in acc.items():
        p = dict(byid[lid]["properties"]); tot = 0
        thr_c, thr_f = speed_thr(p.get("ROAD_RANK")); p["thr_c"] = thr_c; p["thr_f"] = thr_f
        for k in ("wd", "we"):
            for h in range(24):
                s_, n = kinds[k][h]
                if n:
                    m = round(s_ / n, 1); p[f"{k}_{h:02d}"] = m; tot += n
                    city[k][h][0] += m; city[k][h][1] += 1; city[k][h][2] += (m < thr_c)
        p["n_obs_hist"] = tot
        # 하루 평균·최악 시간대(평일)
        wd = [p.get(f"wd_{h:02d}") for h in range(24)]; vals = [v for v in wd if v is not None]
        if vals:
            p["wd_mean"] = round(statistics.mean(vals), 1); p["wd_min"] = min(vals); p["wd_worst_hour"] = wd.index(min(vals))
        feats.append({"type": "Feature", "geometry": byid[lid]["geometry"], "properties": p})
    (PROCESSED / "traffic_hist_links_4326.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False), encoding="utf-8")
    summ = {"days": days, "n_days": len(files), "links": len(feats), "hourly": {k: [{"hour": h, "speed_avg": round(c[h][0] / c[h][1], 1) if c[h][1] else None,
                 "congested_pct": round(c[h][2] / c[h][1] * 100, 1) if c[h][1] else None, "links": c[h][1]} for h in range(24)] for k, c in city.items()}}
    json.dump(summ, open(PROCESSED / "traffic_hist_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"표본일 {len(files)} (평일 {len(days['wd'])}·주말 {len(days['we'])}) | 링크 {len(feats)}")
    for k in ("wd", "we"):
        row = summ["hourly"][k]; print(" ", k, "평균속도:", [r["speed_avg"] for r in row][6:22])
    return 0


if __name__ == "__main__":
    sys.exit(main())
