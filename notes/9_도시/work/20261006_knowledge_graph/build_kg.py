# -*- coding: utf-8 -*-
"""kg_nodes.csv · kg_edges.csv (· kg_evidence.csv) → knowledge_graph.html (오프라인 단일 파일)

사용:  python build_kg.py
정본은 CSV다. 엑셀에서 고친 뒤 이 스크립트를 다시 돌리면 HTML이 새로 만들어진다.
검증: 알 수 없는 노드 id · 중복 엣지 · 알 수 없는 관계/종류/상태 · 고립 노드를 보고한다.
"""
import csv, json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = {"intent", "plan", "law", "data", "derived", "param", "eval"}
RELS = {"limits", "excludes", "anchors", "sizes", "calibrates", "guides", "derives", "sequences", "funds", "conflicts", "evaluates"}
STATUS = {"", "보유", "부분", "요청", "없음"}
TIERS = {"", "T1", "T2", "T3", "T4"}
SCALES = {"", "S1", "S2", "S3"}
CUR = {"", "고정입력", "법정·실측", "혼합", "저작", "가정", "미산정"}


def read_csv(name, required=True):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        if required:
            sys.exit(f"없음: {name}")
        return []
    with open(p, encoding="utf-8-sig", newline="") as f:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


# ───────────── 근거 등급(JS의 gradeOf와 같은 규칙) · 리포트 ─────────────
HARDREL = {"limits", "excludes", "anchors", "sizes", "funds", "sequences"}
SOFTREL = HARDREL | {"calibrates"}
MISSING = {"없음", "요청"}
REL_KO = {"limits": "한정", "excludes": "배제", "anchors": "고정", "sizes": "규모 산정", "calibrates": "보정", "guides": "지침",
          "derives": "파생", "sequences": "순서", "funds": "재원", "conflicts": "충돌", "evaluates": "평가"}
REL_ORDER = ["limits", "excludes", "anchors", "sizes", "calibrates", "guides", "derives", "sequences", "funds", "conflicts", "evaluates"]
GRADE_TXT = {"A": "법정·실측 근거가 값을 직접 한정한다", "B": "데이터·문서가 값을 보정하지만 한정하지는 않는다",
             "C": "방향·저작 근거뿐(T4 포함)", "D": "값을 한정할 핵심 근거가 자료 공백(없음·요청)이다"}


def ok_src(n, strict):
    if n["kind"] in ("intent", "eval", "param"): return False
    if n["status"] in MISSING: return False
    if n["kind"] == "derived": return True
    return n["tier"] in (("T1", "T2") if strict else ("T1", "T2", "T3"))


def grade_all(nodes, edges):
    by = {n["id"]: n for n in nodes}
    ins = {n["id"]: [] for n in nodes}
    for e in edges: ins[e["dst"]].append(e)
    out = {}
    for p in nodes:
        if p["kind"] != "param": continue
        c = []
        for e in ins[p["id"]]:
            s = by[e["src"]]
            if s["kind"] in ("param", "eval"): continue
            if s["kind"] == "derived":
                for ie in ins[s["id"]]:
                    si = by[ie["src"]]
                    if si["kind"] in ("param", "eval"): continue
                    c.append(dict(n=si, rel=e["rel"], hard=e["strength"] == "hard" and ie["strength"] == "hard",
                                  conf=e["basis"] == "확인" and ie["basis"] == "확인", via=s, e=e, ie=ie))
            else:
                c.append(dict(n=s, rel=e["rel"], hard=e["strength"] == "hard", conf=e["basis"] == "확인", via=None, e=e, ie=None))
        rel_ok = lambda x, st: x["rel"] in st and (x["ie"] is None or x["ie"]["rel"] in SOFTREL)
        A = [x for x in c if x["hard"] and x["conf"] and rel_ok(x, HARDREL) and ok_src(x["n"], True)]
        hm = [x for x in c if x["hard"] and rel_ok(x, HARDREL) and x["n"]["status"] in MISSING]
        B = [x for x in c if x["conf"] and rel_ok(x, SOFTREL) and ok_src(x["n"], False)]
        gaps = {}
        for x in c:
            if x["n"]["status"] in MISSING and x["rel"] != "conflicts": gaps[x["n"]["id"]] = x["n"]
        g = "A" if A else ("D" if hm else ("B" if B else "C"))
        out[p["id"]] = dict(grade=g, A=A, B=B, hm=hm, gaps=list(gaps.values()), ins=ins[p["id"]])
    return out


def downstream_params(nodes, edges, nid):
    by = {n["id"]: n for n in nodes}
    outs = {n["id"]: [] for n in nodes}
    for e in edges: outs[e["src"]].append(e)
    seen, q, found = {nid}, [nid], set()
    while q:
        cur = q.pop(0)
        for e in outs[cur]:
            if e["rel"] in ("evaluates", "conflicts") or e["dst"] in seen: continue
            seen.add(e["dst"])
            if by[e["dst"]]["kind"] == "param": found.add(e["dst"])
            if by[e["dst"]]["kind"] != "eval": q.append(e["dst"])
    return found


def write_report(nodes, edges, evid):
    by = {n["id"]: n for n in nodes}
    G = grade_all(nodes, edges)
    params = [n for n in nodes if n["kind"] == "param"]
    L = []
    w = L.append
    w("# 구경주역 마스터플랜 — 값별 근거표 (지식그래프에서 자동 생성)")
    w("")
    w(f"- 생성: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} · 노드 {len(nodes)} · 엣지 {len(edges)} · 마스터플랜 값 {len(params)}")
    w("- 정본은 `kg_nodes.csv` · `kg_edges.csv`다. 이 문서는 `python build_kg.py`가 다시 만든다. 직접 고치지 않는다.")
    w("- **근거 등급**: A = T1·T2 근거가 hard 관계로 값을 한정/산정/고정 · B = 확인된 T1–T3 근거가 보정 · C = 방향·저작(T4·추정 포함)뿐 · D = 값을 한정할 핵심 근거가 자료 공백. 등급은 '쓸 수 있는 근거'이고 현재 값이 실제로 그 근거를 썼다는 뜻이 아니다.")
    w("- **현재 값 출처**: 고정입력 · 법정·실측 · 혼합 · 저작 · 가정 · 미산정 — plan_clean 스크립트·추적표를 보고 매긴 감사 분류(틀리면 CSV `cur_src`를 고친다).")
    w("- 수치는 해당 문서의 인용이며 인용 전 원문 확인이 필요하다. T4(언론·2차자료)는 공모·지구단위계획 문서에 쓰지 않는다.")
    w("")
    cnt = {}
    for p in params: cnt[G[p["id"]]["grade"]] = cnt.get(G[p["id"]]["grade"], 0) + 1
    cc = {}
    for p in params: cc[p["cur_src"]] = cc.get(p["cur_src"], 0) + 1
    w("## 1. 한눈에")
    w("")
    w("- 근거 등급 분포: " + " · ".join(f"{k} {cnt.get(k, 0)}" for k in "ABCD"))
    w("- 현재 값 출처 분포: " + " · ".join(f"{k} {cc[k]}" for k in ("고정입력", "법정·실측", "혼합", "저작", "가정", "미산정") if k in cc))
    link = [p for p in params if G[p["id"]]["grade"] in "AB" and p["cur_src"] in ("저작", "가정", "미산정")]
    w(f"- 근거로 쓸 자료는 있는데 현재 값이 저작·가정·미산정인 값: **{len(link)}개 / {len(params)}개**")
    w("")
    w("| 값 | 묶음 | 현재 값 | 근거 등급 | 현재 값 출처 | 직접 근거 | 자료 공백 |")
    w("|---|---|---|:-:|---|--:|--:|")
    for p in params:
        g = G[p["id"]]
        nin = len([e for e in g["ins"] if by[e["src"]]["kind"] not in ("param", "eval")])
        w(f"| {p['label']} | {p['group']} | {p['value']} | {g['grade']} | {p['cur_src']} | {nin} | {len(g['gaps']) or ''} |")
    w("")
    w("## 2. 자료 공백 우선순위 — 못 구하면 가장 많은 값이 가정에 머무는 순")
    w("")
    gl = [(n, downstream_params(nodes, edges, n["id"])) for n in nodes if n["status"] in MISSING and n["kind"] != "param"]
    gl.sort(key=lambda x: -len(x[1]))
    w("| 자료 | 종류 | 상태 | 영향받는 값 | 설명 |")
    w("|---|---|---|--:|---|")
    for n, ds in gl:
        w(f"| {n['label']} | {n['kind']} · {n['group']} | {n['status']} | {len(ds)} | {n['desc']} |")
    w("")
    w("## 3. 값별 상세")
    w("")
    for p in params:
        g = G[p["id"]]
        w(f"### {p['label']}  `{p['id']}`")
        w("")
        w(f"- 현재 값: {p['value']}")
        w(f"- 현재 값 출처: **{p['cur_src']}** — {p['cur_note']}")
        w(f"- 근거 등급: **{g['grade']}** — {GRADE_TXT[g['grade']]}")
        if g["gaps"]:
            w("- 자료 공백: " + ", ".join(f"{x['label']}({x['status']})" for x in g["gaps"]))
        w("")
        w("| 관계 | 근거 | 종류·출처 | 강도 | 메모 | 위치 |")
        w("|---|---|---|---|---|---|")
        rows = sorted(g["ins"], key=lambda e: (REL_ORDER.index(e["rel"]), e["strength"] != "hard", e["basis"] != "확인"))
        for e in rows:
            s = by[e["src"]]
            meta = " · ".join(x for x in (s["kind"], s["tier"], s["status"]) if x)
            basis = "" if e["basis"] == "확인" else " (추정)"
            w(f"| {REL_KO[e['rel']]} | {s['label']} | {meta} | {e['strength']}{basis} | {e['note']} | {e['ref']} |")
        w("")
    p = os.path.join(HERE, "value_sources_report.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(chr(10).join(L))
    print("만듦:", p)
    return G


def main():
    nodes = read_csv("kg_nodes.csv")
    edges = read_csv("kg_edges.csv")
    evid = read_csv("kg_evidence.csv", required=False)
    errs = []
    ids = set()
    for n in nodes:
        if n["id"] in ids:
            errs.append(f"중복 노드 id: {n['id']}")
        ids.add(n["id"])
        if n["kind"] not in KINDS: errs.append(f"{n['id']}: kind={n['kind']}")
        if n["status"] not in STATUS: errs.append(f"{n['id']}: status={n['status']}")
        if n["tier"] not in TIERS: errs.append(f"{n['id']}: tier={n['tier']}")
        if n["scale"] not in SCALES: errs.append(f"{n['id']}: scale={n['scale']}")
        if n.get("cur_src", "") not in CUR: errs.append(f"{n['id']}: cur_src={n.get('cur_src')}")
        if n["kind"] == "param" and not n.get("cur_src"):
            errs.append(f"{n['id']}: 값 노드에 cur_src 없음")
    seen = set()
    deg = {i: 0 for i in ids}
    for e in edges:
        for k in ("src", "dst"):
            if e[k] not in ids:
                errs.append(f"엣지의 알 수 없는 노드 {k}={e[k]}")
        if e["rel"] not in RELS: errs.append(f"{e['src']}→{e['dst']}: rel={e['rel']}")
        if e["strength"] not in ("hard", "soft"): errs.append(f"{e['src']}→{e['dst']}: strength={e['strength']}")
        if e["basis"] not in ("확인", "추정"): errs.append(f"{e['src']}→{e['dst']}: basis={e['basis']}")
        key = (e["src"], e["dst"], e["rel"])
        if key in seen:
            errs.append(f"중복 엣지 {key}")
        seen.add(key)
        if e["src"] == e["dst"]:
            errs.append(f"자기 순환 {key}")
        if e["src"] in deg: deg[e["src"]] += 1
        if e["dst"] in deg: deg[e["dst"]] += 1
    iso = [i for i, d in deg.items() if d == 0]
    if errs:
        print("검증 오류:")
        for x in errs: print("  -", x)
        sys.exit(1)
    if iso:
        print("경고: 고립 노드 —", ", ".join(iso))

    # 근거 문서(에이전트 추출 등) — nodes 필드는 ';'로 구분된 노드 id
    ev_out = []
    for r in evid:
        ns = [x for x in re.split(r"[;,\s]+", r.get("nodes", "")) if x in ids]
        if not ns:
            continue
        ev_out.append({
            "fid": r.get("fid", ""), "doc": r.get("doc", ""), "doc_title": r.get("doc_title", ""), "loc": r.get("loc", ""),
            "page": r.get("page", ""), "kind": r.get("kind", ""), "topic": r.get("topic", ""), "text": r.get("text", ""),
            "values": r.get("values", ""), "note": r.get("note", ""), "tier": r.get("tier", ""),
            "conf": {"확인": 1.0, "추정": 0.5}.get(r.get("conf", ""), 0.7), "conf_txt": r.get("conf", ""),
            "relation": r.get("relation", ""), "nodes": ns,
        })

    data = {
        "nodes": nodes, "edges": edges, "evidence": ev_out,
        "meta": {"built": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "n_nodes": len(nodes), "n_edges": len(edges), "n_evidence": len(ev_out)},
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    blob = blob.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")

    d3 = open(os.path.join(HERE, "vendor", "d3.min.js"), encoding="utf-8").read()
    app = open(os.path.join(HERE, "kg_app.js"), encoding="utf-8").read()
    tpl = open(os.path.join(HERE, "kg_template.html"), encoding="utf-8").read()
    for name, s in (("d3", d3), ("app", app)):
        if re.search(r"</script", s, re.I):
            sys.exit(f"{name}에 </script 문자열이 있어 인라인할 수 없다")
    out = tpl.replace("/*__D3__*/", d3).replace("/*__DATA__*/", blob).replace("/*__APP__*/", app)
    p = os.path.join(HERE, "knowledge_graph.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"만듦: {p}  ({os.path.getsize(p)/1024:.0f} KB)  노드 {len(nodes)} · 엣지 {len(edges)} · 근거문서 {len(ev_out)}")
    G = write_report(nodes, edges, ev_out)
    print("등급 분포:", {k: sum(1 for v in G.values() if v["grade"] == k) for k in "ABCD"})
    if os.environ.get("KG_DEBUG"):   # 뷰어(JS)와 등급이 같은지 대조할 때만
        with open(os.path.join(HERE, "py_grades.json"), "w", encoding="utf-8") as f:
            json.dump({k: v["grade"] for k, v in G.items()}, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
