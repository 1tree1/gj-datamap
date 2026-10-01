"""'행복황촌 숙박' 카드와 '숙박 인허가' 레이어 자료를 9_도시 산출물에서 public/ 으로 복사.
전체 동기화(sync_data.py)와 분리했다 — 이 카드·레이어만 갱신할 때 다른 데이터 파일을 건드리지 않는다.

  9_도시/archive/C_data/processed/lodging_permits_web_4326.geojson → public/data/lodging_permits.geojson  (pipeline/build_lodging_permits.py)
  9_도시/archive/C_data/processed/lodging_report.json              → public/data/lodging_report.json     (pipeline/build_lodging_permits.py)
  9_도시/work/20261001_hwangchon_lodging_v1.html                  → public/hwangchon_lodging.html       (claude.ai 아티팩트와 같은 본문)
"""
import shutil
from pathlib import Path

ROOT9 = Path(r"C:\Users\User\Desktop\9_도시")
PUB = Path(__file__).resolve().parent.parent / "public"
(PUB / "data").mkdir(exist_ok=True)

P = ROOT9 / "archive" / "C_data" / "processed"
shutil.copy(P / "lodging_permits_web_4326.geojson", PUB / "data" / "lodging_permits.geojson")
shutil.copy(P / "lodging_report.json", PUB / "data" / "lodging_report.json")

# 리포트(밝은 화면 전용)에 iframe으로 넣을 때는 ?embed 로 밝은 테마를 고정한다. 새 창으로 열면 기기 설정을 따른다.
src = (ROOT9 / "work" / "20261001_hwangchon_lodging_v1.html").read_text(encoding="utf-8")
snippet = "<script>if(new URLSearchParams(location.search).has('embed'))document.documentElement.setAttribute('data-theme','light')</script>"
i = src.index("<head>") + len("<head>")
(PUB / "hwangchon_lodging.html").write_text(src[:i] + snippet + src[i:], encoding="utf-8")

for f in ("data/lodging_permits.geojson", "data/lodging_report.json", "hwangchon_lodging.html"):
    print(f"{f:32s} {(PUB / f).stat().st_size / 1024:.0f} KB")
