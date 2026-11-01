"""공통 유틸 — .env 로드, HTTP, 좌표 변환 상수."""
import os, json, ssl, time, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "archive" / "C_data" / "raw"
INTERIM = ROOT / "archive" / "C_data" / "interim"
PROCESSED = ROOT / "archive" / "C_data" / "processed"
for d in (RAW, INTERIM, PROCESSED):
    d.mkdir(parents=True, exist_ok=True)

# 원도심 4개 동 (S2). 법정동코드 뒷 5자리 = bjdongCd
SIGUNGU = "47130"
DONGS = {
    "성동동": "10400",
    "황오동": "10500",
    "노동동": "10600",   # 2026-09-28 정정: V-World 필지 주소·상가업소 법정동명 두 자료 모두 10600=노동동, 10700=노서동
    "노서동": "10700",
    "성건동": "10800",
}
# 구경주역 부지 대략 중심 (성동동 40 일원) — 지오코더로 확인된 값
SITE_LON, SITE_LAT = 129.21892, 35.84584   # 고시 2026-8호 지구단위계획구역 centroid (2026-09-17 교체; 이전 129.2247,35.8562는 북동 1.2km 오차)
# S2 원도심 창 (황오·성동·노서·노동·성건 + 인접) — 상가·건물 등 현황 레이어용
S2_BBOX = (129.1750, 35.8000, 129.2700, 35.8900)   # 2026-09-17 확장: 원도심+황성·동천·용강·보문 진입부 (≈8.6km×10km)
CRS_WORK = "EPSG:5187"   # 처리본 (CLAUDE.md §1)
CRS_WEB = "EPSG:4326"    # 웹 출력만

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE


def load_env():
    env = {}
    p = ROOT / ".env"
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    os.environ.update(env)
    return env


def get_json(url, headers=None, retries=3, pause=0.4):
    last = None
    for i in range(retries):
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=40, context=_CTX) as r:
                body = r.read().decode("utf-8", "replace")
            return json.loads(body)
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code} {e.read()[:200].decode('utf-8','replace')}"
        except Exception as e:
            last = str(e)[:200]
        time.sleep(pause * (i + 1))
    raise RuntimeError(last)


def save(obj, path, label=""):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    n = len(obj.get("features", obj if isinstance(obj, list) else []))
    print(f"  저장 {path.relative_to(ROOT)}  ({n}건) {label}")
    return path


# 교통 소통등급 임계 (km/h) — 도로등급별. ITS 소통정보 판단 관행값: 고속도로 정체<40/원활≥80, 도시고속 30/50, 그 외(국도 시가지 구간 포함) 도시부 15/25.
# 표준노드링크 ROAD_RANK: 101 고속국도 · 102 도시고속국도 · 103 일반국도 · 104 특별광역시도 · 105 국가지원지방도 · 106 지방도 · 107 시군도
SPEED_THR = {"101": (40, 80), "102": (30, 50)}
SPEED_THR_DEFAULT = (15, 25)


def speed_thr(road_rank):
    return SPEED_THR.get(str(road_rank or ""), SPEED_THR_DEFAULT)


def speed_level(v, road_rank):
    if v is None: return None
    c, f = speed_thr(road_rank)
    return "정체" if v < c else ("서행" if v < f else "원활")
