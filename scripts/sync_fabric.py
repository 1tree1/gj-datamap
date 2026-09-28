"""'도시 조직' 그룹과 '도시 축의 변천사'(층위도 병합) 카드 자료를 9_도시 산출물에서 public/ 으로 복사.
전체 동기화(sync_data.py)와 분리했다 — 이 카드들만 갱신할 때 다른 데이터 파일을 건드리지 않는다.

  9_도시/archive/C_data/processed/fabric_report.json → public/data/fabric_report.json   (pipeline/build_report_fabric.py)
  9_도시/archive/90_derived/report_fabric/*.jpg      → public/fabric/                    (pipeline/build_report_fabric.py)
  9_도시/work/경주_원도심_층위도.html                 → public/strata.html                (pipeline/build_palimpsest_page.py, 문서 골격을 씌움)
"""
import shutil
from pathlib import Path

ROOT9 = Path(r"C:\Users\User\Desktop\9_도시")
PUB = Path(__file__).resolve().parent.parent / "public"
(PUB / "data").mkdir(exist_ok=True)
(PUB / "fabric").mkdir(exist_ok=True)

shutil.copy(ROOT9 / "archive" / "C_data" / "processed" / "fabric_report.json", PUB / "data" / "fabric_report.json")
imgs = sorted((ROOT9 / "archive" / "90_derived" / "report_fabric").glob("*.jpg"))
for f in imgs:
    shutil.copy(f, PUB / "fabric" / f.name)

# 층위도는 claude.ai 아티팩트용으로 쓴 본문(문서 골격 없음) → 제목·글꼴·스타일은 <head>로, 나머지는 <body>로
src = (ROOT9 / "work" / "경주_원도심_층위도.html").read_text(encoding="utf-8")
i = src.index('<div class="wrap">')
page = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>\n'
        + src[:i] + '</head>\n<body>\n' + src[i:] + '\n</body>\n</html>\n')
(PUB / "strata.html").write_text(page, encoding="utf-8")

print(f"fabric_report.json  {(PUB / 'data' / 'fabric_report.json').stat().st_size / 1024:.0f} KB")
print(f"fabric/*.jpg        {len(imgs)}장, {sum(f.stat().st_size for f in imgs) / 1e6:.1f} MB")
print(f"strata.html         {(PUB / 'strata.html').stat().st_size / 1e6:.1f} MB")
