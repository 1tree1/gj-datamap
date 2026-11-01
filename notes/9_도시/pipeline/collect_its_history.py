"""ITS 교통소통정보 **이력** — 일별 5분 링크속도(전국 741MB/일)에서 경주 링크만 추출해 누적.

표본 설계: 매월 둘째 주 화요일(평일) + 둘째 주 토요일(주말). 1년 = 24일 ≈ 2.5시간.
  python collect_its_history.py 2025            # 2025년 24일
  python collect_its_history.py 2025 2024 2023  # 여러 해
  python collect_its_history.py --dates 20260916 20260913
출력: raw/its_history/YYYYMMDD.csv.gz  (LINKID,HM,SPEED)  ~10MB/일.  진행: raw/its_history/_log.txt
"""
import os, sys, io, csv, gzip, json, time, zipfile, datetime, subprocess, re
from pathlib import Path
from _common import RAW, PROCESSED

OUT = RAW / "its_history"; OUT.mkdir(exist_ok=True)
TMP = OUT / "_tmp"; TMP.mkdir(exist_ok=True)
LOG = OUT / "_log.txt"
NODELINK = PROCESSED / "nodelink_gj_4326.geojson"


def log(msg):
    line = f"{datetime.datetime.now():%H:%M:%S} {msg}"; print(line, flush=True)
    open(LOG, "a", encoding="utf-8").write(line + "\n")


def sample_dates(year):
    out = []
    for m in range(1, 13):
        first = datetime.date(year, m, 1)
        for wd in (1, 5):   # 화(1), 토(5)
            d = first + datetime.timedelta(days=(wd - first.weekday()) % 7) + datetime.timedelta(days=7)  # 둘째 주
            if d <= datetime.date.today() - datetime.timedelta(days=1): out.append(d.strftime("%Y%m%d"))
    return out


def csrf_session():
    """its.go.kr 세션 쿠키 (다운로드는 쿠키만 있으면 됨)."""
    ck = TMP / "ck.txt"
    subprocess.run(["curl", "-sk", "-m", "30", "-A", "Mozilla/5.0", "-c", str(ck), "-b", str(ck),
                    "https://www.its.go.kr/opendata/opendataList?service=traffic", "-o", os.devnull], check=False)
    return ck


def fetch_day(ymd, ck, tries=4):
    """서버가 간헐적으로 200/0바이트를 돌려준다 → 재시도(20·40·80s 백오프)."""
    zp = TMP / f"{ymd}_5Min.zip"
    url = f"https://www.its.go.kr/opendata/fileDownload/traffic/{ymd[:4]}/{ymd}_5Min.zip"
    last = ""
    for k in range(tries):
        r = subprocess.run(["curl", "-sk", "-m", "1200", "-A", "Mozilla/5.0", "-b", str(ck), "-L", "-o", str(zp), "-w", "%{http_code} %{size_download}", url], capture_output=True, text=True)
        code, size = (r.stdout.split() + ["0", "0"])[:2]
        if code == "200" and int(size) > 1_000_000: return zp
        last = f"HTTP {code} size {size}"; zp.unlink(missing_ok=True); time.sleep(20 * 2 ** k)
    raise RuntimeError(last)


def filter_day(ymd, zp, ids):
    """unzip -p | grep -F 로 경주 링크 행만 추출 (파이썬 루프보다 6배 빠름). 패턴은 ',LINKID,' 로 부분일치 방지."""
    outp = OUT / f"{ymd}.csv.gz"; pat = TMP / "ids.txt"
    if not pat.exists(): pat.write_text(chr(10).join(sorted(ids)))   # 10자리 링크ID 자체 — 2025 파일은 따옴표("ID"), 2026은 맨 ID
    cmd = f'unzip -p "{zp}" | grep -F -f "{pat}"'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    lines = r.stdout.splitlines(); hit = 0
    with gzip.open(outp, "wt", encoding="utf-8", newline="") as g:
        w = csv.writer(g); w.writerow(["LINKID", "HM", "SPEED"])
        for line in lines:
            p = [x.strip().strip('"') for x in line.split(",")]
            if len(p) >= 5 and p[2] in ids: w.writerow([p[2], p[1], p[4]]); hit += 1
    return -1, hit, outp


def main():
    args = sys.argv[1:]
    if args and args[0] == "--dates": dates = args[1:]
    else: dates = [d for y in (args or ["2025"]) for d in sample_dates(int(y))]
    ids = {f["properties"]["LINK_ID"] for f in json.load(open(NODELINK, encoding="utf-8"))["features"]}
    log(f"시작: {len(dates)}일, 경주 링크 {len(ids)}")
    ck = csrf_session()
    for i, ymd in enumerate(dates, 1):
        if (OUT / f"{ymd}.csv.gz").exists(): log(f"[{i}/{len(dates)}] {ymd} 있음 — 건너뜀"); continue
        t0 = time.time()
        try:
            zp = fetch_day(ymd, ck); t1 = time.time()
            n, hit, outp = filter_day(ymd, zp, ids); zp.unlink(missing_ok=True)
            log(f"[{i}/{len(dates)}] {ymd} 다운 {t1-t0:.0f}s 필터 {time.time()-t1:.0f}s → 경주 {hit:,}행 ({outp.stat().st_size/1e6:.1f}MB)")
        except Exception as e:
            log(f"[{i}/{len(dates)}] {ymd} 실패: {str(e)[:120]}")
            for p in TMP.glob(f"{ymd}*"): p.unlink(missing_ok=True)
    log("완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
