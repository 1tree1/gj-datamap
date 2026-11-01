# -*- coding: utf-8 -*-
"""에이전트 4개가 PDF·문서 원문에서 쪽 단위로 뽑은 사실(evidence_raw/kg_K*_facts.jsonl)을 kg_evidence.csv로 합친다.

각 사실의 `nodes` = (a) 에이전트가 적은 affects 중 그래프에 있는 값 노드 + (b) 출처 문서·절에 해당하는 계획/법규/자료 노드.
(b)는 사실 id(fid)별 사람 지정표(DOC_NODE)다. 새 사실이 들어오면 문서 기본값(DOC_DEFAULT)으로 붙는다.
뷰어는 노드를 고르면 그 노드에 붙은 원문 근거를 쪽 번호와 함께 보여 준다.

사용: python merge_evidence.py   (evidence_raw/ 의 JSONL을 읽어 kg_evidence.csv를 새로 쓴다)
"""
import csv, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "evidence_raw")

# 에이전트가 새 id를 제안한 항목 → 그래프의 기존 노드
NEWMAP = {
    "NEW:P_STORM": "P_STORM", "NEW:P_SAFETY": "P_SAFETY", "NEW:P_WASTE": "P_WASTE",
    "NEW:버스터미널_입지": "PL30_TERM", "NEW:활성화지역_지정": "PLR_AREA", "NEW:쇠퇴요건_공모자격": "D_DECLINE",
    "NEW:이전적지": "PL30_MULTI", "NEW:관사촌": "D_RAILHERIT", "NEW:급수탑": "D_RAILHERIT",
    "NEW:물류·UAM_버티포트": "P_TRAMHUB", "NEW:다문화·이주민_정주": "P_HOUSE", "NEW:젠트리피케이션_완충": "P_RETAIL",
    "NEW:야간경관_조명": "PLL_GUIDE", "NEW:공모서류_작성규칙": "PLP_GUIDE",
}

# fid → 출처 문서·절 노드 (사람이 읽고 지정)
DOC_NODE = {}


def _set(prefix, mapping):
    for rng, nodes in mapping:
        a, b = rng
        for i in range(a, b + 1):
            DOC_NODE["%s-%03d" % (prefix, i)] = nodes


# K1 — 2030 경주도시기본계획(A-011)
K1 = {1: "PL30_MULTI", 2: "PL30_MULTI", 3: "PL30_MULTI,PL30_SPACE", 4: "PL30_MULTI", 5: "PL30_MULTI", 6: "PL30_PARK", 7: "PL30_NEWTRANSIT",
      8: "PL30_NEWTRANSIT", 9: "PL30_NEWTRANSIT", 10: "PL30_HUB", 11: "PL30_TERM", 12: "PL30_HUB", 13: "PL30_HUB", 14: "PL30_HUB",
      15: "PL30_HUB,PL30_PARK", 16: "L_INFRA,PLR_AREA", 17: "PLR_AREA", 18: "PLR_AREA", 19: "PL30_REGEN", 20: "PLR_AREA", 21: "PL30_SPACE",
      22: "L_GODO", 23: "PL30_REGEN", 24: "PL30_LSC,PL30_REGEN", 25: "L_GODOLAW", 26: "PL30_SPACE", 27: "PL30_LSC", 28: "PL30_LSC",
      29: "PL30_LSC", 30: "PL30_LAND", 31: "PL30_LAND", 32: "PL30_LAND", 33: "PL30_POP", 34: "PL30_POP", 35: "PL30_POP", 36: "PL30_POP",
      37: "PL30_LAND", 38: "L_MINHOUSE", 39: "PL30_REGEN", 40: "PL30_LAND", 41: "PL30_COMM", 42: "PL30_COMM", 43: "PL30_SURVEY",
      44: "PL30_REGEN,D_DECLINE", 45: "PL30_REGEN", 46: "PL30_TERM,PL30_PUBFAC", 47: "PL30_REGEN", 48: "PL30_REGEN", 49: "PL30_REGEN",
      50: "PL30_FIN", 51: "PL30_FIN", 52: "PL30_REGEN", 53: "PL30_PUBFAC", 54: "PL30_PUBFAC", 55: "PL30_PUBFAC,PL30_MULTI", 56: "PL30_PARK",
      57: "PL30_PARK", 58: "PL30_PARK", 59: "PL30_DISASTER", 60: "PL30_DISASTER", 61: "PL30_HUB", 62: "PL30_HUB", 63: "D_STNRIDE",
      64: "D_MODE", 65: "PL30_PUBFAC", 66: "PL30_COMM", 67: "PL30_SPACE", 68: "PL30_ENV", 69: "PL30_ENV", 70: "PL30_ENV", 71: "PL30_ENV",
      72: "PL30_LAND", 73: "PL30_MULTI", 74: "PL30_HUB", 75: "PL30_LSC", 76: "PL30_TERM"}
for k, v in K1.items():
    DOC_NODE["K1-%03d" % k] = v
# K2 — 도시재생 계획서·성과 보고서
K2 = {1: "PLR_SITE", 2: "PLR_SITE", 3: "PLR_SITE", 4: "PLR_SITE", 5: "PLR_SITE", 6: "PLR_AREA", 7: "D_DECLINE,L_REGENLAW", 8: "PLR_DECLINE",
      9: "PLR_AREA", 10: "PLR_AREA", 11: "PLR_AREA", 12: "PLR_LINK", 13: "PLR_SITE", 14: "PLL_ZONE", 15: "PLR_SITE", 16: "PLP_GUIDE",
      17: "PLP_GUIDE", 18: "PLR_AREA", 19: "PLR_AREA", 20: "PLR_AREA", 21: "L_GODO", 22: "PLR_LINK", 23: "PLR_LINK", 24: "PLR_LINK",
      25: "L_INFRA", 26: "L_INFRA", 27: "L_INFRA,PL30_PARK", 28: "PL30_POP", 29: "D_FOOT", 30: "D_MARKET", 31: "D_STORES", 32: "D_DECLINE",
      33: "PLR_DECLINE", 34: "PLR_AREA", 35: "PLR_LINK", 36: "PLR_SITE", 37: "PLR_SITE"}
for k, v in K2.items():
    DOC_NODE["K2-%03d" % k] = v
for i in range(38, 48): DOC_NODE["K2-%03d" % i] = "PLA20"
for i in range(48, 59): DOC_NODE["K2-%03d" % i] = "PLA18"
for i in range(59, 66): DOC_NODE["K2-%03d" % i] = "PL26_TALK"
for i in range(66, 73): DOC_NODE["K2-%03d" % i] = "PLM_FORUM"
for i in range(73, 76): DOC_NODE["K2-%03d" % i] = "PLA20"
for i in range(76, 83): DOC_NODE["K2-%03d" % i] = "PLM_MONITOR"
DOC_NODE.update({"K2-083": "PL26_TALK", "K2-084": "PLR_SITE", "K2-085": "PLA18,D_COSTUNIT", "K2-086": "PLA18"})
# K3a — 417쪽 연구·시민조사
K3A = {1: "P417_DIR", 2: "P417_DIR,D_QUAKE", 3: "P417_DIR", 4: "P417_DIR,D_HISTMAP", 5: "P417_DIR", 6: "P417_DIR", 7: "P417_DIR", 8: "P417_DIR",
       9: "P417_DIR", 10: "P417_DIR", 11: "P417_SCEN", 12: "P417_SCEN", 13: "P417_SCEN", 14: "P417_SCEN", 15: "P417_MOB", 16: "P417_MOB",
       17: "P417_MOB", 18: "P417_P24", 19: "P417_P24", 20: "P417_PROP", 21: "P417_MOB", 22: "P417_PROP", 23: "P417_PROP", 24: "P417_PROP",
       25: "P417_PROP", 26: "P417_PROP", 27: "P417_PROP", 28: "P417_PROP", 29: "P417_PROP", 30: "P417_PROP", 31: "P417_PROP", 32: "P417_PROP",
       33: "P417_PROP", 34: "P417_PROP", 35: "P417_PROP", 36: "P417_PROP", 37: "P417_PROP", 38: "P417_PROP", 39: "P417_PROP",
       40: "P417_SURVEY", 41: "P417_SURVEY", 42: "P417_SURVEY", 43: "P417_SURVEY", 44: "P417_SURVEY", 45: "P417_SURVEY", 46: "P417_SURVEY",
       47: "PL30_SURVEY", 48: "D_HISTMAP", 49: "D_HISTMAP", 50: "D_HISTMAP", 51: "D_HISTMAP", 52: "D_HISTMAP", 53: "D_HISTMAP,L_GODO",
       54: "PLM_FORUM", 55: "PLM_FORUM", 56: "PLM_FORUM,L_GODO", 57: "PLM_MONITOR", 58: "PLM_MONITOR", 59: "PLM_MONITOR", 60: "PLM_MONITOR",
       61: "PL30_TERM,P417_PROP", 62: "P417_PROP,PL30_MULTI,PLR_SITE", 63: "P417_MOB,PL30_HUB", 64: "P417_PROP,PLR_SITE", 65: "P417_PROP,PLL_ZONE",
       66: "D_HISTMAP", 67: "D_HISTMAP", 68: "P417_PROP,P417_SURVEY", 69: "P417_PROP", 70: "P417_PROP", 71: "P417_PROP", 72: "P417_PROP",
       73: "P417_PROP", 74: "P417_PROP", 75: "P417_PROP", 76: "P417_SURVEY"}
for k, v in K3A.items():
    DOC_NODE["K3a-%03d" % k] = v
# K3b — 매장유산·경관·공모·구 역사
K3B = {1: "D_SURVEY", 2: "D_SURVEY", 3: "D_SURVEY,D_HERITPTS", 4: "D_HERITPTS", 5: "L_BURIED", 6: "L_BURIED", 7: "L_BURIED", 8: "D_SURVEY",
       9: "D_SURVEY", 10: "D_SURVEY", 11: "L_HIA", 12: "L_HIST", 13: "D_HERITPTS", 14: "PLP_CONCEPT", 15: "PLP_CONCEPT", 16: "PLP_CONCEPT",
       17: "PLP_CONCEPT,D_OWNER", 18: "D_DIGPLAN", 19: "D_DIGPLAN", 20: "D_DIGPLAN", 21: "PLL_ZONE", 22: "PLL_GUIDE", 23: "PLL_ZONE",
       24: "PLL_ZONE", 25: "PLL_ZONE", 26: "PLL_AXIS", 27: "PLL_AXIS", 28: "PLL_AXIS", 29: "PLL_AXIS", 30: "PLL_ZONE", 31: "PLL_GUIDE",
       32: "PLL_GUIDE", 33: "PLL_GUIDE", 34: "L_LSCORD", 35: "PLL_GUIDE", 36: "PLL_ZONE", 37: "PLL_GUIDE", 38: "PLL_GUIDE", 39: "PLL_GUIDE",
       40: "PLL_ZONE", 59: "PLA18", 60: "PLA18", 61: "D_STNPLAN", 62: "D_STNPLAN", 63: "D_HISTMAP", 64: "D_HISTMAP", 65: "D_HISTMAP",
       66: "D_TEMPUSE,D_RAILHERIT", 67: "PLP_RAIL,D_STNPLAN", 68: "D_STNPLAN", 69: "D_HISTMAP", 70: "L_STN"}
for k, v in K3B.items():
    DOC_NODE["K3b-%03d" % k] = v
for i in range(41, 59): DOC_NODE["K3b-%03d" % i] = "PLP_GUIDE"
# 문서 기본값(새 사실이 들어왔을 때)
DOC_DEFAULT = {"A-011": "PL30_SPACE", "A-006": "PLR_AREA", "A-007": "PLA20", "A-008": "PLA18", "B-007": "PLA20", "B-005": "PLM_MONITOR",
               "B-006": "PLM_FORUM", "B-ref1": "PL26_TALK", "B-001": "P417_PROP", "B-ref2": "D_HISTMAP", "B-002": "D_SURVEY",
               "B-003": "D_DIGPLAN", "A-009": "PLL_GUIDE", "A-012": "PLA18", "D-ref": "D_HISTMAP"}


def main():
    nodes = {r["id"] for r in csv.DictReader(open(os.path.join(HERE, "kg_nodes.csv"), encoding="utf-8-sig"))}
    files = sorted(glob.glob(os.path.join(RAW, "kg_K*_facts.jsonl")))
    if not files:
        sys.exit("evidence_raw/kg_K*_facts.jsonl 이 없다")
    rows, miss = [], []
    for f in files:
        for ln in open(f, encoding="utf-8"):
            if not ln.strip():
                continue
            r = json.loads(ln)
            ns = []
            for a in r.get("affects") or []:
                t = NEWMAP.get(a, a)
                if t in nodes and t not in ns:
                    ns.append(t)
                elif t not in nodes:
                    miss.append((r["fid"], a))
            dn = DOC_NODE.get(r["fid"])
            if dn is None:
                dn = DOC_DEFAULT.get(r.get("doc", ""), "")
                miss.append((r["fid"], "문서기본값:" + dn))
            for t in [x for x in dn.split(",") if x]:
                if t not in nodes:
                    miss.append((r["fid"], "doc노드없음:" + t))
                elif t not in ns:
                    ns.append(t)
            rows.append({
                "fid": r["fid"], "doc": r.get("doc", ""), "doc_title": r.get("doc_title", ""), "loc": r.get("loc", "") or "",
                "page": "" if r.get("page") in (None, "None") else str(r.get("page")), "kind": r.get("kind", ""), "topic": r.get("topic", ""),
                "text": r.get("text", ""), "values": r.get("values", "") or "", "note": r.get("note", "") or "",
                "tier": r.get("tier", ""), "conf": r.get("conf", ""), "relation": r.get("relation") or "", "strength": r.get("strength") or "",
                "nodes": ";".join(ns),
            })
    cols = ["fid", "doc", "doc_title", "loc", "page", "kind", "topic", "text", "values", "note", "tier", "conf", "relation", "strength", "nodes"]
    with open(os.path.join(HERE, "kg_evidence.csv"), "w", encoding="utf-8-sig", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print("사실", len(rows), dict(Counter(r["kind"] for r in rows)))
    unmapped = [m for m in miss if not m[1].startswith("문서기본값")]
    if unmapped:
        print("그래프에 없는 affects/노드:", unmapped[:20], "…" if len(unmapped) > 20 else "")
    dflt = [m for m in miss if m[1].startswith("문서기본값")]
    if dflt:
        print("지정표에 없어 문서 기본값을 붙인 사실:", [m[0] for m in dflt])
    per = Counter()
    for r in rows:
        for n in r["nodes"].split(";"):
            if n: per[n] += 1
    print("근거가 붙은 노드", len(per), "· 상위", per.most_common(8))


if __name__ == "__main__":
    main()
