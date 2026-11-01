"""보고서 조립 — chapters/*.html → report.html → Edge 헤드리스 PDF → 머리말·쪽번호 찍기 → 목차 쪽번호 2회차 반영
사용: python assemble.py            (2회 렌더: 1회차로 쪽번호를 찾고 2회차에 목차에 넣는다)
출력: output/구경주역_도시재생_마스터플랜_보고서.pdf"""
import os, re, sys, glob, json, subprocess, html
import pymupdf

R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
B = os.path.join(R, "build"); OUT = os.path.join(R, "output"); os.makedirs(OUT, exist_ok=True)
EDGE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"          # 2026-10-19 Edge 헤드리스가 출력 없이 끝나 Chrome으로 교체
TITLE = "구경주역 도시재생 마스터플랜 보고서"
K = 72 / 25.4


def chapters():
    fs = sorted(glob.glob(os.path.join(R, "chapters", "[0-9][0-9]_*.html")))
    return [f for f in fs if not f.endswith(".notes.html")]


def outline(fs):
    """장·절 목록: [(no, title, [h2...])]"""
    out = []
    for f in fs:
        s = open(f, encoding="utf-8").read()
        no = re.search(r'class="ch-no"[^>]*>(.*?)<', s, re.S); h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
        h2 = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<h2[^>]*>(.*?)</h2>", s, re.S)]
        out.append(((no.group(1).strip() if no else ""), re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else os.path.basename(f), h2))
    return out


def toc_html(ol, pages):
    rows = []
    for no, t, h2 in ol:
        pg = pages.get(t, "")
        rows.append('<div class="ch"><div class="t"><span class="no">%s</span>%s<span class="pg">%s</span></div>' % (html.escape(no), html.escape(t), pg))
        for h in h2:
            rows.append('<div class="row"><span class="n">%s</span><span class="pg">%s</span></div>' % (html.escape(h), pages.get(h, "")))
        rows.append("</div>")
    return '<section class="toc"><h1>목차</h1><div class="cols">%s</div></section>' % "".join(rows)


def cover_html():
    img = "../fig/00_cover.png"
    return """<section class="cover"><img class="img" src="%s">
<div class="panel"><div class="kicker">건축디자인6 STUDIO B · 중간마감 보고서</div>
<h1>구경주역<br>도시재생<br>마스터플랜</h1>
<div class="sub">폐철도 부지의 현황 분석과 재생 방향,<br>프로그램·규모 계획과 마스터플랜</div>
<div class="rule"></div>
<div class="nexus"><b>NEXUS 1918</b>원도심을 다시 연결하는 생활거점</div>
<div class="meta">경상북도 경주시 성동동 일원 · 계획대상지 228,022㎡<br>2026. 10. 12<br>2019113133 이승규 · 김민승</div></div></section>""" % img


def build_html(pages):
    fs = chapters(); ol = outline(fs)
    body = [cover_html(), toc_html(ol, pages)]
    for f in fs: body.append(open(f, encoding="utf-8").read())
    css = open(os.path.join(B, "report.css"), encoding="utf-8").read()
    doc = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>%s</body></html>' % (TITLE, css, "\n".join(body))
    p = os.path.join(B, "report.html"); open(p, "w", encoding="utf-8").write(doc)
    return p, ol


def render(html_path, pdf_path):
    if os.path.exists(pdf_path): os.remove(pdf_path)
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files", "--user-data-dir=" + os.path.join(os.environ["LOCALAPPDATA"], "Temp", "chrome_report_profile"), "--virtual-time-budget=30000",
           "--print-to-pdf=" + pdf_path, "file:///" + html_path.replace("\\", "/")]
    subprocess.run(cmd, capture_output=True, timeout=600)
    assert os.path.exists(pdf_path), "PDF 생성 실패"


def find_pages(pdf_path, ol):
    d = pymupdf.open(pdf_path); pages = {}; starts = []
    i0 = 2
    for no, t, h2 in ol:
        for i in range(i0, d.page_count):
            lines = ["".join(sp["text"] for sp in ln["spans"] if sp["size"] > 24) for bl in d[i].get_text("dict")["blocks"] for ln in bl.get("lines", [])]
            if any(t[:6].replace(" ", "") in l_.replace(" ", "") for l_ in lines if l_):
                pages[t] = i + 1; starts.append((i, no, t)); i0 = i; break
        j0 = i0
        for h in h2:
            key = h[:14]
            for i in range(j0, d.page_count):
                if d[i].search_for(key): pages[h] = i + 1; j0 = i; break
    return pages, starts, d.page_count


def stamp(pdf_in, pdf_out, starts):
    d = pymupdf.open(pdf_in)
    fn = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts", "Pretendard-Medium.otf")
    W, H = d[0].rect.width, d[0].rect.height
    cur = ("", "")
    for i, pg in enumerate(d):
        if i == 0: continue
        for (si, no, t) in starts:
            if si == i: cur = (no, t)
        pg.insert_font(fontname="pm", fontfile=fn)
        pg.insert_text((20 * K, 12.5 * K), TITLE, fontname="pm", fontsize=9.5, color=(0.45, 0.45, 0.45))
        if cur[1] and i > 1:
            lab = "%s  %s" % cur
            tw = pymupdf.get_text_length(lab, fontname="helv", fontsize=9.5) * 1.6
            pg.insert_text((W - 20 * K - tw, 12.5 * K), lab, fontname="pm", fontsize=9.5, color=(0.78, 0.06, 0.18))
        pg.draw_line((20 * K, 14.6 * K), (W - 20 * K, 14.6 * K), color=(0.75, 0.75, 0.75), width=0.4)
        pg.insert_text((20 * K, H - 9 * K), "건축디자인6 STUDIO B · 2026.10.12 · 이승규 · 김민승", fontname="pm", fontsize=9.5, color=(0.45, 0.45, 0.45))
        n = str(i + 1)
        pg.insert_text((W - 20 * K - len(n) * 5.6, H - 9 * K), n, fontname="pm", fontsize=10.5, color=(0.15, 0.15, 0.15))
    d.save(pdf_out, garbage=3, deflate=True)


if __name__ == "__main__":
    raw = os.path.join(B, "report_raw.pdf"); final = os.path.join(OUT, "구경주역_도시재생_마스터플랜_보고서.pdf")
    p, ol = build_html({}); render(p, raw)
    pages, starts, n = find_pages(raw, ol)
    p, ol = build_html(pages); render(p, raw)
    pages2, starts, n = find_pages(raw, ol)
    if pages2 != pages:
        p, ol = build_html(pages2); render(p, raw); pages2, starts, n = find_pages(raw, ol)
    stamp(raw, final, starts)
    json.dump(pages2, open(os.path.join(B, "toc_pages.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    missing = [h for _, t, h2 in ol for h in [t] + h2 if h not in pages2]
    print("pages", n, "chapters", len(ol), "missing toc", missing[:10])
    print(final)
