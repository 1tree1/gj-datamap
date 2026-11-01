"""쪽별 해부 노트(rep_*.md, ppt_*.md)에서 쪽 인덱스 표를 만든다.
사용: python build_page_index.py   (work/tongyeong_ref 폴더 기준, 출력: page_index.md)
노트 형식: '### p.N (인쇄 n) — 제목' / '### s.N — 제목' 다음 줄들의 '- 유형:', '- 챕터·역할:' | '- 섹션·역할:'
같은 쪽이 여러 파일에 있으면 나중 파일이 앞 파일을 덮어쓴다 (파일 순서 = 인자 순서).
"""
import re, sys, io, os, glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDR = re.compile(r"^### (?:\(참고\) )?([ps])\.(\d+)(?: \((?:인쇄 )?([^)]*)\))?\s*—\s*(.*)$")


def clip(s, n):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def parse(path):
    rows = {}
    cur = None
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = HDR.match(line)
            if m:
                kind, num, printed, title = m.group(1), int(m.group(2)), m.group(3) or "", m.group(4)
                cur = {"kind": kind, "n": num, "printed": printed, "title": title, "type": "", "role": ""}
                rows[(kind, num)] = cur
                continue
            if line.startswith("### ") or line.startswith("## "):
                cur = None
                continue
            if cur is None:
                continue
            if line.startswith("- 유형:") and not cur["type"]:
                cur["type"] = line.split(":", 1)[1].strip()
            elif (line.startswith("- 챕터·역할:") or line.startswith("- 섹션·역할:")) and not cur["role"]:
                cur["role"] = line.split(":", 1)[1].strip()
    return rows


def main():
    order = [
        ("rep", ["rep_p01_20.md", "rep_p21_31.md"] + sorted(glob.glob(os.path.join(BASE, "rep_p3*_*.md")) + glob.glob(os.path.join(BASE, "rep_p4*_*.md")) + glob.glob(os.path.join(BASE, "rep_p5*_*.md")))),
        ("ppt", ["ppt_s01_30.md", "ppt_s30_60.md", "ppt_s61_89.md"]),
    ]
    out = io.open(os.path.join(BASE, "page_index.md"), "w", encoding="utf-8")
    out.write("# 쪽 인덱스 (자동 생성 — 쪽별 해부 노트의 제목·유형·역할 줄을 모은 것)\n\n")
    out.write("- 생성: `tools/build_page_index.py`. 상세 해부는 각 노트 파일의 같은 쪽 항목을 볼 것.\n")
    out.write("- 보고서 쪽번호 = PDF 쪽번호(인쇄 쪽번호 병기). PT 쪽번호 = PDF 쪽번호(s.1 = A4 표지).\n\n")
    for tag, files in order:
        rows = {}
        for fn in files:
            p = fn if os.path.isabs(fn) else os.path.join(BASE, fn)
            if os.path.exists(p):
                rows.update(parse(p))
        kind = "p" if tag == "rep" else "s"
        total = 59 if tag == "rep" else 89
        title = "보고서(Report) 59쪽" if tag == "rep" else "발표자료(PT) 89쪽"
        out.write(f"## {title}\n\n| 쪽 | 인쇄 | 제목 | 유형 | 소속 · 역할 |\n|---|---|---|---|---|\n")
        missing = []
        for n in range(1, total + 1):
            r = rows.get((kind, n))
            if not r:
                missing.append(n)
                out.write(f"| {n} | | (노트 없음) | | |\n")
                continue
            out.write("| {n} | {pr} | {t} | {ty} | {ro} |\n".format(
                n=n, pr=r["printed"].replace("쪽번호 ", ""), t=clip(r["title"], 70).replace("|", "\\|"),
                ty=clip(r["type"], 40).replace("|", "\\|"), ro=clip(r["role"], 120).replace("|", "\\|")))
        out.write("\n")
        print(tag, "rows:", total - len(missing), "missing:", missing)
    out.close()


if __name__ == "__main__":
    main()
