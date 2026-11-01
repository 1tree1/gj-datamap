import pymupdf, sys, io, json, os

SRC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))  # 프로젝트 루트(원본 PDF 위치)
SP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_render"))  # 렌더·크롭 출력 폴더(필요할 때 생성)
os.makedirs(os.path.join(SP, "txt"), exist_ok=True)

jobs = [("2_Report_HR_통영조선소.pdf", "rep"), ("3_Presentation_통영조선소.pdf", "ppt")]
for fn, tag in jobs:
    d = pymupdf.open(os.path.join(SRC, fn))
    out = io.open(os.path.join(SP, "txt", f"{tag}_text.txt"), "w", encoding="utf-8")
    for i, p in enumerate(d, start=1):
        t = p.get_text("text").strip()
        out.write(f"\n===== [{tag}] page {i} =====\n{t}\n")
    out.close()
    toc = d.get_toc()
    io.open(os.path.join(SP, "txt", f"{tag}_toc.json"), "w", encoding="utf-8").write(
        json.dumps(toc, ensure_ascii=False, indent=1)
    )
    print(tag, "done", d.page_count)
