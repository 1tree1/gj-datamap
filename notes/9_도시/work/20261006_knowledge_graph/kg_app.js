/* 구경주역 마스터플랜 지식그래프 — 뷰어 로직 v1 (2026-10-06)
 * KG = {nodes, edges, evidence, meta} 가 주입된다. 줌·팬만 D3 v7을 쓰고 나머지는 직접 그린다.
 * 노드/엣지 정본은 kg_nodes.csv · kg_edges.csv — 이 파일에는 데이터가 없다.
 */
(function () {
'use strict';

/* ═════════ 상수 ═════════ */
const FONT = '"Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",sans-serif';
const KORDER = ['intent', 'plan', 'law', 'data', 'derived', 'param', 'eval'];
const KIND = {
  intent: { ko: '설계 방향', hint: '내가 정한 방향·스케치' },
  plan: { ko: '계획·고시', hint: '상위계획·재생·연구·고시' },
  law: { ko: '법규·기준', hint: '규제 4겹+2와 법정 원단위' },
  data: { ko: '데이터', hint: '현황·원자료' },
  derived: { ko: '파생 제약·모델', hint: 'S0 제약층·규칙·계수' },
  param: { ko: '마스터플랜 값', hint: '계획안이 정하는 값' },
  eval: { ko: '평가함수', hint: 'Part 5 f₁–f₅' }
};
const REL = {
  limits: { ko: '한정', long: '상·하한을 건다', c: '#d1453b' },
  excludes: { ko: '배제', long: '불가능 영역으로 잘라낸다', c: '#a1264f' },
  anchors: { ko: '고정', long: '위치·형상을 못 박는다', c: '#2f6fdb' },
  sizes: { ko: '규모 산정', long: '수치를 계산해 준다', c: '#2a9d6a' },
  calibrates: { ko: '보정', long: '값의 범위·타당성을 조정', c: '#13a3b5' },
  guides: { ko: '지침', long: '방향을 제시', c: '#8a63d2' },
  derives: { ko: '파생', long: '계산으로 따라온다', c: '#6b7a90' },
  sequences: { ko: '순서', long: '선후·단계를 정한다', c: '#e08a1e' },
  funds: { ko: '재원', long: '사업비 조건', c: '#c9a227' },
  conflicts: { ko: '충돌', long: '서로 어긋난다', c: '#e0359e' },
  evaluates: { ko: '평가', long: '목적함수 입력', c: '#8a8f98' }
};
const REL_ORDER = ['limits', 'excludes', 'anchors', 'sizes', 'calibrates', 'guides', 'derives', 'sequences', 'funds', 'conflicts', 'evaluates'];
const ST = { '보유': '#2a9d6a', '부분': '#e0a31e', '요청': '#e07a1e', '없음': '#d1453b' };
const GRADE_C = { A: '#2a9d6a', B: '#2f8fd1', C: '#e0a31e', D: '#d1453b' };
const GRADE_T = {
  A: '법정·실측 근거가 값을 직접 한정한다',
  B: '데이터·문서가 값을 보정하지만 한정하지는 않는다',
  C: '방향·저작 근거뿐(T4 포함)',
  D: '값을 한정할 핵심 근거가 자료 공백(없음·요청)이다'
};
const CUR_C = { '고정입력': '#4b6cb7', '법정·실측': '#2a9d6a', '혼합': '#8bb02a', '저작': '#e0a31e', '가정': '#e07a1e', '미산정': '#9aa3b0' };
const CUR_ORDER = ['고정입력', '법정·실측', '혼합', '저작', '가정', '미산정'];
const PAL = {
  light: {
    bg: '#f4f3ee', band: '#ebe9e1', neutral: '#e3e0d6', text: '#1d2430', muted: '#6b7380', line: '#c9c5b8',
    fill: { intent: '#fde9c4', plan: '#d7e5fb', law: '#f9d5d2', data: '#d3f0e1', derived: '#e5def4', param: '#27364f', eval: '#f1d2ec' },
    stroke: { intent: '#c58a1f', plan: '#4274c9', law: '#be4a43', data: '#2f9068', derived: '#7f6db5', param: '#121b2b', eval: '#a2449a' },
    ptext: '#ffffff'
  },
  dark: {
    bg: '#14171c', band: '#1b1f26', neutral: '#2a303a', text: '#e6e8ec', muted: '#98a1ae', line: '#394050',
    fill: { intent: '#4a3a1a', plan: '#1f3254', law: '#4e2624', data: '#183d2e', derived: '#33294f', param: '#aebfdc', eval: '#4b2447' },
    stroke: { intent: '#d9a441', plan: '#6f9bf0', law: '#e0766f', data: '#4dbf90', derived: '#a493dc', param: '#e9f0ff', eval: '#d173c8' },
    ptext: '#10151f'
  }
};
const NODE_W = 176;
const MISSING = s => s === '없음' || s === '요청';

/* ═════════ 데이터 준비 ═════════ */
const NODES = KG.nodes.map((n, i) => Object.assign({ idx: i }, n));
const EDGES = KG.edges.map((e, i) => Object.assign({ i }, e));
const BY = new Map(NODES.map(n => [n.id, n]));
EDGES.forEach(e => { e.s = BY.get(e.src); e.t = BY.get(e.dst); });
const OUTS = new Map(NODES.map(n => [n.id, []]));
const INS = new Map(NODES.map(n => [n.id, []]));
EDGES.forEach(e => { OUTS.get(e.src).push(e); INS.get(e.dst).push(e); });
const gkey = n => n.kind + '|' + n.group;
const GROUPS = [], GBY = new Map();
NODES.forEach(n => {
  const k = gkey(n);
  if (!GBY.has(k)) { const g = { key: k, kind: n.kind, name: n.group, ids: [] }; GBY.set(k, g); GROUPS.push(g); }
  GBY.get(k).ids.push(n.id);
});
const EVID = new Map(), EVBY = new Map();
(KG.evidence || []).forEach(ev => {
  EVBY.set(ev.fid, ev);
  (ev.nodes || []).forEach(id => { if (!EVID.has(id)) EVID.set(id, []); EVID.get(id).push(ev); });
});

/* ── 근거 등급 (값 노드) ──
 * A: T1·T2 근거(법규·계획·데이터)가 hard 관계로 값을 직접 한정/산정/고정/재원/순서 — 파생 노드는 그 입력으로 환원해 판단
 * D: hard 관계의 근거가 있으나 모두 '없음·요청' 자료
 * B: 확인된 T1–T3 근거가 soft로 보정/산정
 * C: 방향·저작(의도·T4·추정 간선)뿐
 */
const HARDREL = new Set(['limits', 'excludes', 'anchors', 'sizes', 'funds', 'sequences']);
const SOFTREL = new Set(['limits', 'excludes', 'anchors', 'sizes', 'funds', 'sequences', 'calibrates']);
function okSrc(n, strict) {
  if (!n || n.kind === 'intent' || n.kind === 'eval' || n.kind === 'param') return false;
  if (MISSING(n.status)) return false;
  if (n.kind === 'derived') return true;
  return strict ? (n.tier === 'T1' || n.tier === 'T2') : (n.tier === 'T1' || n.tier === 'T2' || n.tier === 'T3');
}
function candidates(p) {
  const out = [];
  for (const e of INS.get(p.id)) {
    if (e.s.kind === 'param' || e.s.kind === 'eval') continue;
    if (e.s.kind === 'derived') {
      for (const ie of INS.get(e.s.id)) {
        if (ie.s.kind === 'param' || ie.s.kind === 'eval') continue;
        out.push({ n: ie.s, rel: e.rel, hard: e.strength === 'hard' && ie.strength === 'hard', conf: e.basis === '확인' && ie.basis === '확인', via: e.s, e, ie });
      }
    } else out.push({ n: e.s, rel: e.rel, hard: e.strength === 'hard', conf: e.basis === '확인', via: null, e, ie: null });
  }
  return out;
}
function gradeOf(p) {
  const c = candidates(p);
  const relOk = (x, set) => set.has(x.rel) && (!x.ie || SOFTREL.has(x.ie.rel));
  const A = c.filter(x => x.hard && x.conf && relOk(x, HARDREL) && okSrc(x.n, true));
  const hm = c.filter(x => x.hard && relOk(x, HARDREL) && MISSING(x.n.status));
  const B = c.filter(x => x.conf && relOk(x, SOFTREL) && okSrc(x.n, false));
  const gaps = new Map();
  c.forEach(x => { if (MISSING(x.n.status) && x.rel !== 'conflicts') gaps.set(x.n.id, x.n); });
  let g = 'C';
  if (A.length) g = 'A'; else if (hm.length) g = 'D'; else if (B.length) g = 'B';
  return { grade: g, A, B, hardMissing: hm, gaps: [...gaps.values()] };
}
NODES.forEach(n => {
  if (n.kind !== 'param') return;
  const gi = gradeOf(n);
  n.grade = gi.grade; n.gi = gi; n.gapN = gi.gaps.length; n.evScore = gi.A.length + 0.5 * gi.B.length;
  n.needsLink = (gi.grade === 'A' || gi.grade === 'B') && ['저작', '가정', '미산정'].includes(n.cur_src);
});
const PARAMS = NODES.filter(n => n.kind === 'param');
PARAMS.forEach(n => {
  const ce = INS.get(n.id).filter(e => e.rel === 'conflicts').length;
  const cf = (EVID.get(n.id) || []).filter(e => e.kind === 'conflict').length;
  n.confN = ce + cf; n.evN = (EVID.get(n.id) || []).length;
});

/* 자료 공백의 하류 영향(값 개수) */
function downstreamParams(id) {
  const seen = new Set([id]), found = new Set(); const q = [id];
  while (q.length) {
    const cur = q.shift();
    for (const e of OUTS.get(cur)) {
      if (e.rel === 'evaluates' || e.rel === 'conflicts') continue;
      if (seen.has(e.dst)) continue;
      seen.add(e.dst);
      if (e.t.kind === 'param') found.add(e.dst);
      if (e.t.kind !== 'eval') q.push(e.dst);
    }
  }
  return found;
}
const GAPLIST = NODES.filter(n => MISSING(n.status) && n.kind !== 'param').map(n => ({ n, ds: downstreamParams(n.id) }))
  .sort((a, b) => b.ds.size - a.ds.size || OUTS.get(b.n.id).length - OUTS.get(a.n.id).length);

/* ═════════ 상태 ═════════ */
const S = {
  view: 'overview', sel: null, hover: null, focus: null, group: null, color: 'kind', theme: 'auto', hlGroup: null,
  kinds: new Set(KORDER), rels: new Set(REL_ORDER), hardOnly: false, confOnly: false,
  statuses: new Set(['보유', '부분', '요청', '없음']), scales: new Set(['S1', 'S2', 'S3']), anim: true
};
let CUR = { nodes: [], edges: [], ids: new Set(), L: null };
let K = 1;

/* ═════════ 유틸 ═════════ */
const $ = (s, r) => (r || document).querySelector(s);
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const NS = 'http://www.w3.org/2000/svg';
function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  if (attrs) for (const k in attrs) { const v = attrs[k]; if (v !== null && v !== undefined) e.setAttribute(k, v); }
  if (parent) parent.appendChild(e);
  return e;
}
function setAttr(e, k, v) { if (v === null || v === undefined) e.removeAttribute(k); else e.setAttribute(k, v); }
const curTheme = () => S.theme === 'auto' ? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : S.theme;
function lum(hex) {
  const h = hex.replace('#', ''); const r = parseInt(h.slice(0, 2), 16) / 255, g = parseInt(h.slice(2, 4), 16) / 255, b = parseInt(h.slice(4, 6), 16) / 255;
  const f = v => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
}
const onColor = hex => lum(hex) > 0.42 ? '#10151f' : '#ffffff';
const mctx = document.createElement('canvas').getContext('2d');
function tw(s, px, bold) { mctx.font = (bold ? 'bold ' : '') + px + 'px ' + FONT; return mctx.measureText(s).width; }
function wrap(label, maxW, px, bold, maxLines) {
  const toks = label.split(/(?<=[ ·,)\/])|(?=\()/).filter(Boolean);
  const lines = []; let cur = '';
  for (const t of toks) {
    if (tw(cur + t, px, bold) <= maxW) { cur += t; continue; }
    if (cur) { lines.push(cur.trimEnd()); cur = ''; }
    if (tw(t, px, bold) <= maxW) cur = t.trimStart();
    else { let buf = ''; for (const ch of t) { if (tw(buf + ch, px, bold) <= maxW) buf += ch; else { lines.push(buf); buf = ch; } } cur = buf; }
  }
  if (cur) lines.push(cur.trimEnd());
  if (lines.length > maxLines) {
    let last = lines.slice(maxLines - 1).join('');
    while (tw(last + '…', px, bold) > maxW && last.length > 1) last = last.slice(0, -1);
    lines.length = maxLines - 1; lines.push(last + '…');
  }
  return lines;
}
function sizeNode(n, W, maxLines) {
  const isP = n.kind === 'param';
  W = W || NODE_W;
  n.px = isP ? 12 : 11;
  n.lines = wrap(n.label, W - 36 - (isP ? 8 : 0), n.px, isP, maxLines || 2);
  n.w = W; n.h = 12 + n.lines.length * 13.5;
}
/* 본문 속 [K1-031] 같은 근거 번호를 마우스를 올리면 요지가 보이는 칩으로 바꾼다(esc 처리된 문자열에만 적용) */
function fidify(t) {
  return String(t == null ? '' : t).replace(/\[(K\d[ab]?-\d{3})\]/g, (m, id) => {
    const ev = EVBY.get(id);
    const tip = ev ? esc((ev.topic ? ev.topic + ' — ' : '') + String(ev.text).slice(0, 170) + (ev.page ? ' (p.' + ev.page + ')' : '')) : '근거 번호';
    return `<span class="fid" data-fid="${id}" title="${tip}">${id}</span>`;
  });
}
const debounce = (f, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => f(...a), ms); }; };

/* ═════════ 필터 → 보이는 그래프 ═════════ */
function visibleGraph() {
  const keepN = NODES.filter(n => S.kinds.has(n.kind) && (!n.status || S.statuses.has(n.status)) && (!n.scale || S.scales.has(n.scale)));
  const ns = new Set(keepN.map(n => n.id));
  const es = EDGES.filter(e => ns.has(e.src) && ns.has(e.dst) && S.rels.has(e.rel) && (!S.hardOnly || e.strength === 'hard') && (!S.confOnly || e.basis === '확인'));
  const deg = new Set(); es.forEach(e => { deg.add(e.src); deg.add(e.dst); });
  return { nodes: keepN.filter(n => deg.has(n.id)), edges: es };
}

/* ═════════ 그래프 생성: 상세 / 초점 / 묶음 ═════════ */
function detailGraph() {
  const vis = visibleGraph();
  let nodes = vis.nodes, edges = vis.edges;
  if (S.focus) {
    const f = S.focus, ns = new Set(nodes.map(n => n.id));
    if (!ns.has(f.id)) return { nodes: [], edges: [] };
    const es = new Set(edges);
    const keep = new Set([f.id]);
    const bfs = dir => {
      let frontier = [f.id]; const seen = new Set([f.id]);
      for (let h = 0; h < f.hops; h++) {
        const next = [];
        for (const id of frontier) {
          for (const e of (dir === 'up' ? INS : OUTS).get(id)) {
            if (!es.has(e)) continue;
            const o = dir === 'up' ? e.src : e.dst;
            if (!seen.has(o) && ns.has(o)) { seen.add(o); keep.add(o); next.push(o); }
          }
        }
        frontier = next;
      }
    };
    if (f.dir === 'up' || f.dir === 'both') bfs('up');
    if (f.dir === 'down' || f.dir === 'both') bfs('down');
    nodes = nodes.filter(n => keep.has(n.id));
    edges = edges.filter(e => keep.has(e.src) && keep.has(e.dst));
  } else if (S.group) {
    const g = GBY.get(S.group); const inG = new Set(g ? g.ids : []);
    const keep = new Set(inG);
    edges.forEach(e => { if (inG.has(e.src)) keep.add(e.dst); if (inG.has(e.dst)) keep.add(e.src); });
    nodes = nodes.filter(n => keep.has(n.id));
    edges = edges.filter(e => keep.has(e.src) && keep.has(e.dst));
  }
  const small = !!(S.focus || S.group);
  nodes.forEach(n => sizeNode(n, small ? 152 : NODE_W, small ? 3 : 2));
  return { nodes, edges };
}
function overviewGraph() {
  const vis = visibleGraph();
  const gm = new Map();
  vis.nodes.forEach(n => {
    const k = gkey(n);
    if (!gm.has(k)) gm.set(k, { id: k, label: n.group, kind: n.kind, group: n.kind, isGroup: true, ids: [], miss: 0, idx: gm.size });
    const g = gm.get(k); g.ids.push(n.id); if (MISSING(n.status)) g.miss++;
  });
  const am = new Map();
  vis.edges.forEach(e => {
    const a = gkey(e.s), b = gkey(e.t); if (a === b) return;
    const k = a + '→' + b;
    if (!am.has(k)) am.set(k, { id: k, src: a, dst: b, count: 0, hard: 0, rels: {}, items: [], agg: true });
    const x = am.get(k); x.count++; if (e.strength === 'hard') x.hard++; x.rels[e.rel] = (x.rels[e.rel] || 0) + 1; x.items.push(e);
  });
  const nodes = [...gm.values()];
  nodes.forEach(g => { g.px = 12; g.lines = wrap(g.label, 132 - 20, 12, true, 2); g.w = 132; g.h = 14 + g.lines.length * 14 + 15; });
  const edges = [...am.values()];
  edges.forEach(x => {
    x.s = gm.get(x.src); x.t = gm.get(x.dst);
    x.rel = Object.keys(x.rels).sort((p, q) => x.rels[q] - x.rels[p])[0];
  });
  return { nodes, edges };
}

/* ═════════ 레이아웃 (열: 종류, 값 노드는 파생 깊이로 하위 열) ═════════ */
function layered(gn, ge, opt) {
  const o = Object.assign({ gapX: 54, gapKind: 92, padX: 24, padTop: 66, gapIn: 8, gapGroup: 30, maxUnit: 58, split: { data: 28, plan: 36 }, spread: true }, opt || {});
  // (1) 값 노드 깊이: 값→값 간선의 최장 경로
  const pin = new Map();
  gn.forEach(n => { if (n.kind === 'param') pin.set(n.id, []); });
  ge.forEach(e => { if (pin.has(e.src) && pin.has(e.dst)) pin.get(e.dst).push(e.src); });
  const depth = new Map(), stk = new Set();
  const dep = id => {
    if (depth.has(id)) return depth.get(id);
    if (stk.has(id)) return 0;
    stk.add(id); let d = 0;
    for (const a of pin.get(id)) d = Math.max(d, 1 + dep(a));
    stk.delete(id); depth.set(id, d); return d;
  };
  pin.forEach((_, id) => dep(id));
  // (2) 종류별 하위 열
  const sub = new Map();
  const byKind = {}; KORDER.forEach(k => byKind[k] = []);
  gn.forEach(n => byKind[n.kind].push(n));
  const slots = [];
  KORDER.forEach(k => {
    const arr = byKind[k]; if (!arr.length) return;
    if (k === 'param') {
      const lv = [...new Set(arr.map(n => Math.min(depth.get(n.id) || 0, 2)))].sort((a, b) => a - b);
      arr.forEach(n => sub.set(n.id, lv.indexOf(Math.min(depth.get(n.id) || 0, 2))));
      lv.forEach((_, s) => slots.push({ kind: k, sub: s, nodes: [] }));
    } else if (o.split[k] && arr.length > o.split[k]) {
      const order = []; arr.forEach(n => { if (!order.includes(n.group)) order.push(n.group); });
      const half = arr.length / 2; let acc = 0; const left = new Set();
      for (const g of order) { if (acc < half) { left.add(g); acc += arr.filter(n => n.group === g).length; } }
      arr.forEach(n => sub.set(n.id, left.has(n.group) ? 0 : 1));
      const used = [...new Set(arr.map(n => sub.get(n.id)))].sort();
      used.forEach(s_ => slots.push({ kind: k, sub: s_, nodes: [] }));
    } else { arr.forEach(n => sub.set(n.id, 0)); slots.push({ kind: k, sub: 0, nodes: [] }); }
  });
  const slotOf = new Map();
  gn.forEach(n => { const i = slots.findIndex(s => s.kind === n.kind && s.sub === sub.get(n.id)); slots[i].nodes.push(n); slotOf.set(n.id, i); });
  // x
  let x = o.padX;
  slots.forEach((s, i) => {
    s.w = Math.max(...s.nodes.map(n => n.w));
    if (i > 0) x += slots[i - 1].w + (slots[i - 1].kind === s.kind ? o.gapX : o.gapKind);
    s.x = x;
  });
  // (3) 순서: 그룹 단위 → 노드 단위 바리센터
  const nb = new Map(gn.map(n => [n.id, []]));
  ge.forEach(e => { if (nb.has(e.src) && nb.has(e.dst)) { nb.get(e.src).push(e.dst); nb.get(e.dst).push(e.src); } });
  const pos = new Map();
  const setPos = col => col.forEach((n, i) => pos.set(n.id, col.length > 1 ? i / (col.length - 1) : 0.5));
  slots.forEach(s => { s.nodes.sort((a, b) => a.idx - b.idx); setPos(s.nodes); });
  const reorder = (si, dir) => {
    const s = slots[si]; if (s.nodes.length < 2) return;
    const bary = new Map();
    s.nodes.forEach(n => {
      let sum = 0, k = 0;
      nb.get(n.id).forEach(m => { const mi = slotOf.get(m); if (dir > 0 ? mi < si : mi > si) { sum += pos.get(m); k++; } });
      bary.set(n.id, k ? sum / k : pos.get(n.id));
    });
    const gsum = new Map(), gcnt = new Map(), gfirst = new Map();
    s.nodes.forEach((n, i) => { gsum.set(n.group, (gsum.get(n.group) || 0) + bary.get(n.id)); gcnt.set(n.group, (gcnt.get(n.group) || 0) + 1); if (!gfirst.has(n.group)) gfirst.set(n.group, i); });
    s.nodes.sort((a, b) => {
      if (a.group !== b.group) {
        const ga = gsum.get(a.group) / gcnt.get(a.group), gb = gsum.get(b.group) / gcnt.get(b.group);
        return (ga - gb) || (gfirst.get(a.group) - gfirst.get(b.group));
      }
      return (bary.get(a.id) - bary.get(b.id)) || (a.idx - b.idx);
    });
    setPos(s.nodes);
  };
  for (let it = 0; it < 8; it++) {
    for (let si = 1; si < slots.length; si++) reorder(si, +1);
    for (let si = slots.length - 2; si >= 0; si--) reorder(si, -1);
  }
  // (4) y 배치: 가장 긴 열을 기준으로 다른 열을 퍼뜨려 높이를 맞춘다
  const colInfo = s => {
    const ns = s.nodes;
    const gaps = ns.map((n, i) => i ? (ns[i - 1].group !== n.group ? o.gapGroup : o.gapIn) : 0);
    const wts = ns.map((n, i) => i ? (ns[i - 1].group !== n.group ? 2.4 : 1) : 0);
    s.gaps = gaps; s.wts = wts; s.sumW = wts.reduce((a, b) => a + b, 0);
    s.nat = ns.reduce((a, n) => a + n.h, 0) + gaps.reduce((a, b) => a + b, 0);
  };
  slots.forEach(colInfo);
  const hmax = Math.max(...slots.map(s => s.nat));
  slots.forEach(s => {
    let unit = 0;
    if (o.spread && s.sumW > 0) unit = Math.max(0, Math.min((hmax - s.nat) / s.sumW, o.maxUnit));
    const used = s.nat + unit * s.sumW;
    let y = o.padTop + (hmax - used) / 2;
    s.nodes.forEach((n, i) => { y += s.gaps[i] + unit * s.wts[i]; n.x = s.x + n.w / 2; n.y = y + n.h / 2; y += n.h; });
  });
  const blocks = [];
  slots.forEach((s, si) => {
    let cur = null;
    s.nodes.forEach(n => {
      if (!cur || cur.group !== n.group) { cur = { slot: si, kind: s.kind, group: n.group, x: s.x, y0: n.y - n.h / 2, y1: n.y + n.h / 2 }; blocks.push(cur); }
      else cur.y1 = n.y + n.h / 2;
    });
  });
  const kinds = [];
  slots.forEach(s => {
    let k = kinds.find(z => z.kind === s.kind);
    if (!k) { k = { kind: s.kind, x0: s.x, x1: s.x + s.w, n: 0 }; kinds.push(k); }
    k.x1 = s.x + s.w; k.n += s.nodes.length;
  });
  const last = slots[slots.length - 1];
  return { slots, blocks, kinds, hmax, y0: o.padTop, y1: o.padTop + hmax, bbox: { x0: 0, y0: 6, x1: (last ? last.x + last.w : 0) + o.padX, y1: o.padTop + hmax + 34 } };
}

/* 엣지 경로(왼→오른쪽 곡선, 같은 열은 오른쪽 호, 역방향은 S자) */
function edgeGeom(e) {
  const s = e.s, t = e.t, sx = s.x, sy = s.y, tx = t.x, ty = t.y;
  if (Math.abs(sx - tx) < 1) {
    const bx = sx + s.w / 2, d = 36 + Math.abs(ty - sy) * 0.12;
    return { d: `M${bx},${sy} C${bx + d},${sy} ${bx + d},${ty} ${bx},${ty}`, mx: bx + d * 0.75, my: (sy + ty) / 2 };
  }
  if (tx > sx) {
    const a = sx + s.w / 2, b = tx - t.w / 2, k = Math.max(28, Math.min(220, (b - a) * 0.5));
    return { d: `M${a},${sy} C${a + k},${sy} ${b - k},${ty} ${b},${ty}`, mx: (a + b) / 2, my: (sy + ty) / 2 };
  }
  const a = sx - s.w / 2, b = tx + t.w / 2, k = Math.max(28, Math.min(220, (a - b) * 0.5));
  return { d: `M${a},${sy} C${a - k},${sy} ${b + k},${ty} ${b},${ty}`, mx: (a + b) / 2, my: (sy + ty) / 2 };
}

/* ═════════ SVG 골격 ═════════ */
const svg = $('#svg'), stage = $('#stage');
const gView = el('g', { id: 'view' }, svg);
const gBand = el('g', null, gView), gCap = el('g', null, gView), gEdge = el('g', null, gView), gLab = el('g', null, gView), gNode = el('g', null, gView);
svg.setAttribute('font-family', FONT);
const defs = el('defs', null, svg);
REL_ORDER.forEach(r => {
  const m = el('marker', { id: 'ar-' + r, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 8, markerHeight: 8, markerUnits: 'userSpaceOnUse', orient: 'auto' }, defs);
  el('path', { d: 'M0,1.2 L9,5 L0,8.8 z', fill: REL[r].c }, m);
});
const zoom = d3.zoom().scaleExtent([0.1, 4]).on('zoom', ev => { gView.setAttribute('transform', ev.transform.toString()); K = ev.transform.k; lod(); });
d3.select(svg).call(zoom).on('dblclick.zoom', null);
function lod() {
  const hide = K < 0.3 && S.view === 'detail' && !S.focus;
  CUR.nodes.forEach(n => { if (n._t && n.kind !== 'param' && n.kind !== 'eval' && n.kind !== 'intent') setAttr(n._t, 'display', hide ? 'none' : null); });
}
function fit(anim) {
  if (S.view === 'matrix' || !CUR.L) return;
  const r = stage.getBoundingClientRect(); const w = r.width, h = r.height, b = CUR.L.bbox;
  const bw = b.x1 - b.x0, bh = b.y1 - b.y0; if (bw <= 0 || bh <= 0) return;
  const k = Math.min(w / bw, h / bh, S.focus ? 1.5 : 1.25) * 0.96;
  const tx = (w - bw * k) / 2 - b.x0 * k, ty = (h - bh * k) / 2 - b.y0 * k + (S.focus || S.group ? 14 : 0);
  const t = d3.zoomIdentity.translate(tx, ty).scale(k);
  const sel = d3.select(svg);
  if (anim && S.anim) sel.transition().duration(420).call(zoom.transform, t); else sel.call(zoom.transform, t);
}

/* ═════════ 그리기 ═════════ */
function nodeFill(n, P) {
  if (n.isGroup) return P.fill[n.kind];
  if (n.kind === 'param') {
    if (S.color === 'grade') return GRADE_C[n.grade];
    if (S.color === 'cur') return CUR_C[n.cur_src] || '#9aa3b0';
    return P.fill.param;
  }
  return S.color === 'kind' ? P.fill[n.kind] : P.neutral;
}
function draw(G, L) {
  const P = PAL[curTheme()];
  [gBand, gCap, gEdge, gLab, gNode].forEach(g => { while (g.firstChild) g.removeChild(g.firstChild); });
  CUR = { nodes: G.nodes, edges: G.edges, ids: new Set(G.nodes.map(n => n.id)), L };
  svg.style.background = P.bg;
  // 열 띠 + 제목
  L.kinds.forEach(k => {
    el('rect', { x: k.x0 - 10, y: L.y0 - 46, width: k.x1 - k.x0 + 20, height: L.y1 - L.y0 + 60, rx: 14, fill: P.band, opacity: 0.7 }, gBand);
    const t = el('text', { x: (k.x0 + k.x1) / 2, y: L.y0 - 27, 'text-anchor': 'middle', 'font-size': 13, 'font-weight': 700, fill: P.stroke[k.kind] }, gBand);
    t.textContent = KIND[k.kind].ko + (G.overview ? '' : '  ' + k.n);
  });
  // 그룹 캡션
  if (!G.overview) {
    L.blocks.forEach(b => {
      const t = el('text', { x: b.x + 2, y: b.y0 - 6, 'font-size': 9.5, fill: P.muted }, gCap);
      t.textContent = b.group;
    });
  }
  const dense = !S.focus && !G.overview && G.edges.length > 90;
  const showLab = G.overview || ((S.focus || S.group) && G.edges.length <= 70);
  // 엣지
  G.edges.forEach(e => {
    const gm = edgeGeom(e);
    const col = REL[e.rel].c;
    let w, dash, op;
    if (e.agg) { w = 1.2 + 1.5 * Math.sqrt(e.count); dash = null; op = 0.26; }
    else { w = e.strength === 'hard' ? 1.7 : 0.95; dash = e.rel === 'conflicts' ? '2 3' : (e.basis === '추정' ? '5 3' : null); op = dense ? (e.strength === 'hard' ? 0.34 : 0.17) : (e.strength === 'hard' ? 0.85 : 0.6); }
    if (e.rel === 'conflicts' && !e.agg) w += 0.6;
    e._w = w; e._op = op;
    const p = el('path', { d: gm.d, fill: 'none', stroke: col, 'stroke-width': w, 'stroke-opacity': op, 'stroke-dasharray': dash, 'marker-end': e.agg ? null : 'url(#ar-' + e.rel + ')', 'stroke-linecap': 'round' }, gEdge);
    e._p = p;
    const hit = el('path', { d: gm.d, fill: 'none', stroke: 'transparent', 'stroke-width': Math.max(9, w + 6), 'pointer-events': 'stroke', 'data-hit': 1 }, gEdge);
    hit.addEventListener('mousemove', ev => { showTip(edgeTipHtml(e), ev); if (!S.hover) { S.hover = null; } });
    hit.addEventListener('mouseleave', hideTip);
    if (showLab && (!e.agg || e.count >= 4)) {
      const txt = e.agg ? String(e.count) : REL[e.rel].ko;
      const lab = el('text', { x: gm.mx, y: gm.my + 3, 'text-anchor': 'middle', 'font-size': e.agg ? 11 : 9.5, 'font-weight': e.agg ? 700 : 400, fill: e.agg ? P.text : col, stroke: P.bg, 'stroke-width': 3, 'paint-order': 'stroke', 'pointer-events': 'none' }, gLab);
      lab.textContent = txt;
    }
  });
  // 노드
  G.nodes.forEach(n => {
    const g = el('g', { transform: `translate(${n.x},${n.y})`, cursor: 'pointer' }, gNode);
    n._g = g;
    const fill = nodeFill(n, P);
    const isFocus = S.focus && S.focus.id === n.id;
    let stroke = P.stroke[n.kind], sw = n.kind === 'param' ? 1.2 : 1.1, dash = null;
    if (!n.isGroup && MISSING(n.status)) { stroke = ST[n.status]; sw = 1.6; dash = n.status === '없음' ? '4 2.5' : '2 2'; }
    else if (!n.isGroup && n.status === '부분') { stroke = ST['부분']; dash = '5 2'; sw = 1.4; }
    if (n.isGroup && n.miss) { stroke = ST['없음']; dash = '4 2.5'; sw = 1.6; }
    if (isFocus) { stroke = '#e0359e'; sw = 3; dash = null; }
    el('rect', { x: -n.w / 2, y: -n.h / 2, width: n.w, height: n.h, rx: 8, fill, stroke, 'stroke-width': sw, 'stroke-dasharray': dash }, g);
    const tcol = n.kind === 'param' ? onColor(fill) : P.text;
    const t = el('text', { 'font-size': n.px || 12, 'font-weight': (n.kind === 'param' || n.isGroup) ? 700 : 400, fill: tcol, 'pointer-events': 'none' }, g);
    n._t = t;
    if (n.isGroup) {
      let yy = -n.h / 2 + 8 + 11;
      n.lines.forEach(ln => { const a = el('tspan', { x: -n.w / 2 + 10, y: yy }, t); a.textContent = ln; yy += 14; });
      const b = el('tspan', { x: -n.w / 2 + 10, y: yy + 1, 'font-size': 10, 'font-weight': 400, 'fill-opacity': 0.75 }, t);
      b.textContent = '노드 ' + n.ids.length + (n.miss ? ' · 공백 ' + n.miss : '');
    } else {
      const lh = 13.5, y0 = -((n.lines.length - 1) * lh) / 2 + 4;
      n.lines.forEach((ln, i) => { const a = el('tspan', { x: -n.w / 2 + 9, y: y0 + i * lh }, t); a.textContent = ln; });
      if (n.status && n.kind !== 'param') {
        el('circle', { cx: n.w / 2 - 11, cy: 0, r: 4, fill: ST[n.status], stroke: P.bg, 'stroke-width': 1 }, g);
      }
      if (n.tier === 'T4') {
        const tt = el('text', { x: n.w / 2 - 7, y: -n.h / 2 + 9, 'text-anchor': 'end', 'font-size': 8.5, 'font-weight': 700, fill: '#d1453b', 'pointer-events': 'none' }, g); tt.textContent = 'T4';
      }
      if (n.kind === 'param' && n.confN) {
        el('rect', { x: -n.w / 2 - 4, y: -n.h / 2 - 7, width: 22, height: 13, rx: 6.5, fill: REL.conflicts.c, stroke: P.bg, 'stroke-width': 1 }, g);
        const ct = el('text', { x: -n.w / 2 + 7, y: -n.h / 2 + 3, 'text-anchor': 'middle', 'font-size': 9, 'font-weight': 700, fill: '#ffffff', 'pointer-events': 'none' }, g); ct.textContent = '⚡' + n.confN;
      }
      if (n.kind === 'param') {
        el('circle', { cx: n.w / 2 - 14, cy: 0, r: 8.5, fill: GRADE_C[n.grade], stroke: P.bg, 'stroke-width': 1.2 }, g);
        const gt = el('text', { x: n.w / 2 - 14, y: 3.6, 'text-anchor': 'middle', 'font-size': 10.5, 'font-weight': 700, fill: onColor(GRADE_C[n.grade]), 'pointer-events': 'none' }, g); gt.textContent = n.grade;
      }
    }
    g.addEventListener('mouseenter', ev => { S.hover = n.id; applyHL(); showTip(nodeTipHtml(n), ev); });
    g.addEventListener('mousemove', ev => showTip(nodeTipHtml(n), ev));
    g.addEventListener('mouseleave', () => { S.hover = null; applyHL(); hideTip(); });
    g.addEventListener('click', ev => { ev.stopPropagation(); onNodeClick(n); });
    g.addEventListener('dblclick', ev => { ev.stopPropagation(); onNodeDbl(n); });
  });
  applyHL(); lod();
}
function neighborSet(id) {
  const s = new Set([id]);
  CUR.edges.forEach(e => { if (e.src === id || e.dst === id) { s.add(e.src); s.add(e.dst); } });
  return s;
}
function applyHL() {
  // 초점 보기에서 초점 노드를 선택한 상태는 이미 걸러진 그래프이므로 흐리지 않는다
  const id = S.hover || (S.sel && !(S.focus && S.sel === S.focus.id) ? S.sel : null);
  if (!id || !CUR.ids.has(id)) {
    CUR.edges.forEach(e => { e._p.setAttribute('stroke-opacity', e._op); e._p.setAttribute('stroke-width', e._w); });
    CUR.nodes.forEach(n => n._g.setAttribute('opacity', 1));
    return;
  }
  const nb = neighborSet(id);
  CUR.edges.forEach(e => {
    const on = e.src === id || e.dst === id;
    e._p.setAttribute('stroke-opacity', on ? 0.98 : 0.035);
    e._p.setAttribute('stroke-width', e._w + (on ? 0.8 : 0));
  });
  CUR.nodes.forEach(n => n._g.setAttribute('opacity', nb.has(n.id) ? 1 : 0.2));
}

/* ═════════ 툴팁 ═════════ */
const tip = $('#tip');
function nodeTipHtml(n) {
  if (n.isGroup) return `<b>${esc(n.label)}</b><div class="m">${esc(KIND[n.kind].ko)} · 노드 ${n.ids.length}${n.miss ? ' · 자료 공백 ' + n.miss : ''}</div><div class="m">클릭: 요약 · 더블클릭: 그룹 안으로</div>`;
  let h = `<b>${esc(n.label)}</b><div class="m">${esc(KIND[n.kind].ko)} · ${esc(n.group)}${n.tier ? ' · ' + n.tier : ''}${n.scale ? ' · ' + n.scale : ''}${n.status ? ' · ' + n.status : ''}</div>`;
  if (n.value) h += `<div>${esc(n.value)}</div>`;
  if (n.kind === 'param') h += `<div class="m">근거 등급 ${n.grade} · 현재 값 출처 ${esc(n.cur_src || '-')}${n.confN ? ' · 상충 ' + n.confN + '건' : ''}${n.evN ? ' · 원문 근거 ' + n.evN + '건' : ''}</div>`;
  h += '<div class="m">클릭: 상세 · 더블클릭: 이 노드 중심으로 보기</div>';
  return h;
}
function edgeTipHtml(e) {
  if (e.agg) {
    const rs = Object.keys(e.rels).sort((a, b) => e.rels[b] - e.rels[a]).map(r => `${REL[r].ko} ${e.rels[r]}`).join(' · ');
    return `<b>${esc(e.s.label)} → ${esc(e.t.label)}</b><div class="m">엣지 ${e.count}개 (hard ${e.hard})</div><div>${esc(rs)}</div>`;
  }
  return `<b>${esc(e.s.label)} → ${esc(e.t.label)}</b><div class="m"><span style="color:${REL[e.rel].c};font-weight:700">${REL[e.rel].ko}</span> (${REL[e.rel].long}) · ${e.strength} · ${e.basis}</div><div>${esc(e.note)}</div>${e.ref ? `<div class="m">[${esc(e.ref)}]</div>` : ''}`;
}
function showTip(html, ev) {
  tip.innerHTML = html; tip.style.display = 'block';
  const r = tip.getBoundingClientRect(); let x = ev.clientX + 14, y = ev.clientY + 14;
  if (x + r.width > innerWidth - 8) x = ev.clientX - r.width - 14;
  if (y + r.height > innerHeight - 8) y = ev.clientY - r.height - 14;
  tip.style.left = Math.max(4, x) + 'px'; tip.style.top = Math.max(4, y) + 'px';
}
function hideTip() { tip.style.display = 'none'; }

/* ═════════ 상호작용 ═════════ */
function defDir(n) { return n.kind === 'param' || n.kind === 'eval' ? 'up' : (n.kind === 'derived' ? 'both' : 'down'); }
function focusOn(id, dir, hops) {
  const n = BY.get(id); if (!n) return;
  S.focus = { id, dir: dir || defDir(n), hops: hops || 2 };
  S.group = null; S.sel = id; S.hlGroup = null;
  if (S.view !== 'detail') S.view = 'detail';
  refresh(true);
}
function clearFocus() { S.focus = null; S.group = null; refresh(true); }
function onNodeClick(n) {
  S.sel = n.id; S.hlGroup = null;
  applyHL(); renderRight(); syncLeft(); writeHash();
}
function onNodeDbl(n) {
  if (n.isGroup) { S.view = 'detail'; S.group = n.id; S.focus = null; S.sel = null; refresh(true); return; }
  focusOn(n.id);
}
svg.addEventListener('click', () => { if (S.sel) { S.sel = null; applyHL(); renderRight(); syncLeft(); writeHash(); } });

function setView(v) {
  S.view = v; S.hover = null;
  if (v === 'overview') { S.focus = null; S.group = null; if (S.sel && BY.has(S.sel)) S.sel = null; }
  if (v === 'detail' && S.sel && !BY.has(S.sel)) S.sel = null;
  refresh(true);
}

/* ═════════ 렌더 진입점 ═════════ */
function refresh(anim) {
  $('#tabs').querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.v === S.view));
  const isM = S.view === 'matrix';
  svg.style.display = isM ? 'none' : 'block'; $('#matrix').style.display = isM ? 'block' : 'none';
  $('#colorsel').value = S.color;
  $('#hint').style.display = isM ? 'none' : 'block';
  if (isM) { renderMatrix(); $('#empty').style.display = 'none'; }
  else {
    const G = S.view === 'overview' ? overviewGraph() : detailGraph();
    G.overview = S.view === 'overview';
    $('#empty').style.display = G.nodes.length ? 'none' : 'flex';
    if (G.nodes.length) {
      const L = layered(G.nodes, G.edges, G.overview ? { spread: true, gapGroup: 12, gapIn: 16, maxUnit: 60, gapX: 26, gapKind: 44, padX: 20, padTop: 62 } : (S.focus || S.group ? { spread: true, maxUnit: 40, gapKind: 66, gapX: 40 } : { gapKind: 76, gapX: 40 }));
      draw(G, L); fit(anim);
    } else { CUR = { nodes: [], edges: [], ids: new Set(), L: null }; [gBand, gCap, gEdge, gLab, gNode].forEach(g => { while (g.firstChild) g.removeChild(g.firstChild); }); }
    $('#sub').textContent = subText(G);
  }
  renderHud(); renderRight(); syncLeft(); writeHash();
  $('#hint').textContent = hintText();
}
function subText(G) {
  const base = `노드 ${NODES.length} · 엣지 ${EDGES.length} · 값 ${PARAMS.length}`;
  if (S.view === 'matrix') return base + ' — 값 × 근거 묶음';
  if (S.view === 'overview') return base + ' — 묶음 ' + G.nodes.length + '개, 묶음 간 연결 ' + G.edges.length + '개';
  return base + ' — 표시 중 노드 ' + G.nodes.length + ' · 엣지 ' + G.edges.length;
}
function hintText() {
  if (S.view === 'overview') return '묶음을 클릭하면 요약, 더블클릭하면 그 묶음의 노드로 들어갑니다 · 선 위 숫자 = 엣지 개수';
  if (S.view === 'matrix') return '칸 = 그 묶음에서 그 값으로 가는 직접 엣지 수 · ■ hard 포함 · ○ 자료 공백 포함';
  if (S.focus) return '초점 보기: 휠로 확대, 드래그로 이동 · Esc로 해제';
  return '노드에 마우스를 올리면 연결이 강조됩니다 · 더블클릭 = 이 노드 중심으로 보기 · 휠 확대/드래그 이동';
}
function renderHud() {
  const h = $('#hud'); h.innerHTML = '';
  if (S.view === 'matrix' || S.view === 'overview') return;
  if (S.focus) {
    const n = BY.get(S.focus.id), f = S.focus;
    const d = (k, t) => `<button data-d="${k}" class="${f.dir === k ? 'on' : ''}">${t}</button>`;
    const hp = k => `<button data-h="${k}" class="${f.hops === k ? 'on' : ''}">${k}</button>`;
    h.innerHTML = `<div class="box"><b>초점</b> ${esc(n.label)}</div><div class="box">${d('up', '← 상류(정하는 것)')}${d('both', '양방향')}${d('down', '하류(영향 주는 것) →')}</div><div class="box">단계 ${hp(1)}${hp(2)}${hp(3)}</div><div class="box"><button data-act="clear">초점 해제 ✕</button></div>`;
  } else if (S.group) {
    const g = GBY.get(S.group);
    h.innerHTML = `<div class="box"><b>묶음</b> ${esc(g ? g.name : '')} + 이웃 노드</div><div class="box"><button data-act="clear">전체로 ✕</button></div>`;
  }
}
$('#hud').addEventListener('click', ev => {
  const b = ev.target.closest('button'); if (!b) return;
  if (b.dataset.act === 'clear') return clearFocus();
  if (b.dataset.d) { S.focus.dir = b.dataset.d; refresh(true); }
  if (b.dataset.h) { S.focus.hops = +b.dataset.h; refresh(true); }
});

/* ═════════ 오른쪽 패널(점검기) ═════════ */
const chip = (t, cls, title) => `<span class="chip ${cls || ''}" title="${esc(title || '')}">${esc(t)}</span>`;
function nodeChips(n) {
  let h = '';
  if (n.tier) h += chip(n.tier, n.tier.toLowerCase(), '출처 등급');
  if (n.scale) h += chip(n.scale, '', '스케일(S1 부지·S2 원도심·S3 도시)');
  if (n.status) h += chip(n.status, 's-' + n.status, '자료 상태');
  return h;
}
function edgeChips(e) { return chip(e.strength, e.strength, 'hard=불가능·상한 / soft=조정·참고') + chip(e.basis, e.basis === '추정' ? 'est' : '', '확인=문서에서 확인 / 추정=설계 논리'); }
const cmpEdge = (a, b) => (b.strength === 'hard') - (a.strength === 'hard') || (b.basis === '확인') - (a.basis === '확인');
function itemHtml(o, e) {
  const hl = S.hlGroup && o && gkey(o) === S.hlGroup ? ' hl' : '';
  return `<div class="it${hl}"><button class="lnk" data-go="${esc(o.id)}">${esc(o.label)}</button> ${nodeChips(o)} ${edgeChips(e)}${e.note ? `<div class="nt">${fidify(esc(e.note))}${e.ref ? ` <span class="rf">[${fidify(esc(e.ref))}]</span>` : ''}</div>` : ''}</div>`;
}
function relBlocks(es, side) {
  const by = {}; es.forEach(e => { (by[e.rel] = by[e.rel] || []).push(e); });
  let h = '';
  REL_ORDER.forEach(r => {
    const arr = by[r]; if (!arr) return;
    arr.sort((a, b) => cmpEdge(a, b) || (side === 'src' ? a.s : a.t).label.localeCompare((side === 'src' ? b.s : b.t).label, 'ko'));
    h += `<div class="rb"><div class="rh" style="--rc:${REL[r].c}"><i></i><b>${REL[r].ko}</b><span>${REL[r].long}</span><em>${arr.length}</em></div>`;
    arr.forEach(e => { h += itemHtml(side === 'src' ? e.s : e.t, e); });
    h += '</div>';
  });
  return h;
}
const EV_KIND = { conflict: '상충', gap: '문서 공백', constraint: '제약', standard: '기준', direction: '방향', fact: '사실' };
const EV_ORDER = { conflict: 0, gap: 1, constraint: 2, standard: 3, direction: 4, fact: 5 };
function evItem(ev) {
  const kd = EV_KIND[ev.kind] || ev.kind || '';
  const src = `${esc(ev.doc_title || ev.doc)}${ev.page ? ' · p.' + esc(ev.page) : ''}${ev.loc && !ev.page ? ' · ' + esc(ev.loc) : ''} · ${esc(ev.tier || '')}${ev.conf_txt ? ' · ' + esc(ev.conf_txt) : ''}`;
  return `<div class="ev ${esc(String(ev.tier || '').toLowerCase())} k-${esc(ev.kind || '')}"><div>${kd ? `<span class="chip ev-${esc(ev.kind)}">${esc(kd)}</span> ` : ''}<b>${esc(ev.topic || '')}</b></div><div>${esc(ev.text)}</div>${ev.values ? `<div class="val">${esc(ev.values)}</div>` : ''}<div class="src">${src}</div>${ev.note ? `<details><summary style="font-weight:400;font-size:11px;color:var(--muted)">메모</summary><div class="nt">${esc(ev.note)}</div></details>` : ''}</div>`;
}
function evidHtml(n) {
  const list = EVID.get(n.id); if (!list || !list.length) return '';
  const rank = { T1: 0, T2: 1, T3: 2, T4: 3 };
  const arr = list.slice().sort((a, b) => (EV_ORDER[a.kind] ?? 9) - (EV_ORDER[b.kind] ?? 9) || (rank[a.tier] ?? 9) - (rank[b.tier] ?? 9) || (b.conf || 0) - (a.conf || 0));
  const kc = {}; arr.forEach(e => { kc[e.kind] = (kc[e.kind] || 0) + 1; });
  const chips = Object.keys(kc).sort((a, b) => (EV_ORDER[a] ?? 9) - (EV_ORDER[b] ?? 9)).map(k => `<span class="chip ev-${esc(k)}">${esc(EV_KIND[k] || k)} ${kc[k]}</span>`).join(' ');
  let h = `<details open><summary>PDF·문서 원문 근거 ${arr.length}건</summary><div class="chips">${chips} <span class="chip">에이전트 추출 — 원문 대조 전</span></div>`;
  h += arr.slice(0, 10).map(evItem).join('');
  if (arr.length > 10) h += `<details><summary>나머지 ${arr.length - 10}건</summary>${arr.slice(10).map(evItem).join('')}</details>`;
  return h + '</details>';
}
function renderRight() {
  const box = $('#right');
  if (S.sel && BY.has(S.sel)) box.innerHTML = nodeInspector(BY.get(S.sel));
  else if (S.sel && GBY.has(S.sel)) box.innerHTML = groupInspector(GBY.get(S.sel));
  else box.innerHTML = homePanel();
  box.scrollTop = 0;
}
function nodeInspector(n) {
  const ins = INS.get(n.id), outs = OUTS.get(n.id);
  let h = `<div class="chips"><span class="chip kind k-${n.kind}">${esc(KIND[n.kind].ko)}</span>${nodeChips(n)}</div>`;
  h += `<h2>${esc(n.label)}</h2><div class="id">${esc(n.id)} · ${esc(n.group)}</div>`;
  if (n.value) h += `<div class="val">${esc(n.value)}</div>`;
  if (n.desc) h += `<p>${fidify(esc(n.desc))}</p>`;
  if (n.ref) h += `<p class="id">근거 위치: ${fidify(esc(n.ref))}</p>`;
  if (n.tier === 'T4') h += `<div class="card bad"><h5>T4 출처</h5>공모·지구단위계획 문서에는 T1–T2만 쓴다. 원문 치환 전에는 인용 금지.</div>`;
  if (MISSING(n.status)) h += `<div class="card bad"><h5>자료 공백(${esc(n.status)})</h5>이 자료가 없으면 아래 하류 값이 가정에 머문다 — 영향받는 값 ${downstreamParams(n.id).size}개.</div>`;
  if (n.kind === 'param') {
    const gi = n.gi;
    h += `<div class="card"><h5><span class="gd ${n.grade}">${n.grade}</span> 근거 등급 — ${esc(GRADE_T[n.grade])}</h5>`;
    const show = (arr, label) => arr.length ? `<div class="nt">${label}: ${arr.slice(0, 6).map(x => `<button class="lnk" data-go="${esc(x.n.id)}">${esc(x.n.label)}</button>${x.via ? `<span class="rf">(${esc(x.via.label)} 경유)</span>` : ''}`).join(' · ')}${arr.length > 6 ? ` 외 ${arr.length - 6}` : ''}</div>` : '';
    h += show(gi.A, 'hard 근거');
    if (!gi.A.length) h += show(gi.hardMissing, '공백인 hard 근거');
    if (!gi.A.length) h += show(gi.B, '보정 근거');
    if (gi.gaps.length) h += `<div class="nt">자료 공백 ${gi.gaps.length}건: ${gi.gaps.map(g => `<button class="lnk" data-go="${esc(g.id)}">${esc(g.label)}</button>`).join(' · ')}</div>`;
    h += `</div>`;
    h += `<div class="card ${n.needsLink ? 'warn' : ''}"><h5><span class="gd" style="background:${CUR_C[n.cur_src] || '#9aa3b0'};${n.cur_src === '저작' ? 'color:#1d2430' : ''}">●</span> 현재 값의 출처 — ${esc(n.cur_src || '-')}</h5>${esc(n.cur_note || '')}${n.needsLink ? '<div class="nt"><b>근거로 쓸 자료가 있는데 현재 값은 ' + esc(n.cur_src) + '입니다 → 먼저 연결할 후보.</b></div>' : ''}</div>`;
  }
  h += `<div class="btnrow"><button class="btn pri" data-focus="${esc(n.id)}" data-dir="up">← 정하는 것 보기</button><button class="btn" data-focus="${esc(n.id)}" data-dir="down">영향 주는 것 →</button><button class="btn" data-focus="${esc(n.id)}" data-dir="both">양방향</button></div>`;
  const upOpen = n.kind === 'param' || n.kind === 'eval' || n.kind === 'derived';
  if (ins.length) h += `<details ${upOpen ? 'open' : ''}><summary>이 노드를 정하는 것 ← ${ins.length}</summary>${relBlocks(ins, 'src')}</details>`;
  if (outs.length) h += `<details ${upOpen ? '' : 'open'}><summary>이 노드가 정하는 것 → ${outs.length}</summary>${relBlocks(outs, 'dst')}</details>`;
  h += evidHtml(n);
  return h;
}
function groupInspector(g) {
  const ids = new Set(g.ids);
  const inC = {}, outC = {};
  EDGES.forEach(e => {
    const a = ids.has(e.src), b = ids.has(e.dst);
    if (a && !b) { const k = gkey(e.t); outC[k] = (outC[k] || 0) + 1; }
    if (b && !a) { const k = gkey(e.s); inC[k] = (inC[k] || 0) + 1; }
  });
  const list = o => Object.keys(o).sort((a, b) => o[b] - o[a]).map(k => `<div class="it"><button class="lnk" data-group="${esc(k)}">${esc(GBY.get(k).name)}</button> <span class="chip">${esc(KIND[GBY.get(k).kind].ko)}</span> <b>${o[k]}</b></div>`).join('');
  let h = `<div class="chips"><span class="chip kind k-${g.kind}">${esc(KIND[g.kind].ko)}</span></div><h2>${esc(g.name)}</h2><div class="id">묶음 · 노드 ${g.ids.length}</div>`;
  h += `<div class="btnrow"><button class="btn pri" data-opengroup="${esc(g.key)}">이 묶음의 노드로 들어가기</button></div>`;
  h += `<details open><summary>노드 ${g.ids.length}</summary>${g.ids.map(id => { const n = BY.get(id); return `<div class="it"><button class="lnk" data-go="${esc(id)}">${esc(n.label)}</button> ${nodeChips(n)}${n.kind === 'param' ? `<span class="gd ${n.grade}" style="margin-left:4px">${n.grade}</span>` : ''}</div>`; }).join('')}</details>`;
  if (Object.keys(inC).length) h += `<details open><summary>이 묶음으로 들어오는 엣지</summary>${list(inC)}</details>`;
  if (Object.keys(outC).length) h += `<details open><summary>이 묶음에서 나가는 엣지</summary>${list(outC)}</details>`;
  return h;
}
function homePanel() {
  const cnt = o => { const r = {}; PARAMS.forEach(p => { r[o(p)] = (r[o(p)] || 0) + 1; }); return r; };
  const gc = cnt(p => p.grade), cc = cnt(p => p.cur_src || '-');
  const bar = (obj, order, colors) => `<div class="bar">${order.map(k => obj[k] ? `<i style="width:${obj[k] / PARAMS.length * 100}%;background:${colors[k]}" title="${k} ${obj[k]}"></i>` : '').join('')}</div><div class="legend">${order.map(k => obj[k] ? `<span><b style="background:${colors[k]}"></b>${k} ${obj[k]}</span>` : '').join('')}</div>`;
  const link = PARAMS.filter(p => p.needsLink).sort((a, b) => b.evScore - a.evScore);
  const linkRow = p => `<div class="it"><span class="gd ${p.grade}">${p.grade}</span> <button class="lnk" data-focus="${esc(p.id)}" data-dir="up">${esc(p.label)}</button> <span class="chip">${esc(p.cur_src)}</span> <span class="chip">근거 ${p.gi.A.length + p.gi.B.length}건</span></div>`;
  let h = `<h2>이 그래프가 답하는 것</h2><p>"어떤 데이터·법규·계획이 마스터플랜의 어떤 값을 정하는가". 왼쪽 목록에서 <b>값</b>을 고르면 그 값을 정하는 근거만 남겨 보여 줍니다.</p>`;
  h += `<h4>마스터플랜 값 ${PARAMS.length}개의 근거 등급</h4>${bar(gc, ['A', 'B', 'C', 'D'], GRADE_C)}<div class="nt" style="font-size:11px;color:var(--muted)">A 법정·실측 hard 한정 · B 데이터 보정 · C 방향·저작뿐 · D 핵심 근거가 자료 공백</div>`;
  h += `<h4>같은 값들의 <u>현재</u> 값 출처</h4>${bar(cc, CUR_ORDER, CUR_C)}<div class="nt" style="font-size:11px;color:var(--muted)">plan_clean 스크립트·추적표를 보고 매긴 감사 분류 — 틀리면 kg_nodes.csv의 cur_src를 고친다</div>`;
  h += `<h4>근거는 있는데 아직 안 쓰는 값 ${link.length}/${PARAMS.length}개 — 근거 건수 순</h4>${link.slice(0, 8).map(linkRow).join('')}${link.length > 8 ? `<details><summary>나머지 ${link.length - 8}개</summary>${link.slice(8).map(linkRow).join('')}</details>` : ''}`;
  const cfl = EDGES.filter(e => e.rel === 'conflicts' && e.s.kind !== 'param' && e.t.kind !== 'param');
  const cfp = {}; EDGES.filter(e => e.rel === 'conflicts' && e.t.kind === 'param').forEach(e => { cfp[e.dst] = (cfp[e.dst] || 0) + 1; });
  const cfEv = (KG.evidence || []).filter(e => e.kind === 'conflict').length, gpEv = (KG.evidence || []).filter(e => e.kind === 'gap').length;
  h += `<h4>문서끼리 어긋나는 곳 — 문서↔문서 상충 엣지 ${cfl.length}개</h4>${cfl.map(e => `<div class="it"><button class="lnk" data-go="${esc(e.src)}">${esc(e.s.label)}</button> <span style="color:${REL.conflicts.c}">⚡</span> <button class="lnk" data-go="${esc(e.dst)}">${esc(e.t.label)}</button><div class="nt">${fidify(esc(e.note))}</div></div>`).join('')}`;
  h += `<div class="nt" style="font-size:11px;color:var(--muted);margin-top:4px">값 노드에 붙은 상충 엣지 ${Object.values(cfp).reduce((a, b) => a + b, 0)}개 · 원문 근거 중 상충 ${cfEv}건·'문서가 정하지 않은 것' ${gpEv}건 (값을 고르면 근거와 함께 표시)</div>`;
  h += `<h4>자료 공백 우선순위 — 못 구하면 가장 많은 값이 가정에 머무는 순</h4>`;
  GAPLIST.slice(0, 10).forEach(x => { h += `<div class="it"><button class="lnk" data-go="${esc(x.n.id)}">${esc(x.n.label)}</button> ${chip(x.n.status, 's-' + x.n.status)} <span class="chip">값 ${x.ds.size}개 영향</span><div class="nt">${esc(x.n.desc.slice(0, 80))}${x.n.desc.length > 80 ? '…' : ''}</div></div>`; });
  h += `<div class="card"><h5>읽는 법 요약</h5>왼쪽 열일수록 원천(방향·계획·법규·데이터), 오른쪽 열일수록 결과(값·평가). 엣지 색 = 관계(한정·고정·산정…), 굵은 선 = hard, 점선 = 추정. 자세한 설명은 상단 <b>?</b>.</div>`;
  return h;
}

/* ═════════ 왼쪽 패널 ═════════ */
function buildLeft() {
  let h = '<h4>마스터플랜 값 — 클릭하면 이 값을 정하는 근거를 봅니다</h4><div class="legend" style="margin-bottom:4px"><span><b class="gd A" style="width:auto;height:auto;color:#fff;background:var(--A);padding:0 4px;border-radius:5px">A</b>법정·실측 한정</span><span><b class="gd B" style="width:auto;height:auto;color:#fff;background:var(--B);padding:0 4px;border-radius:5px">B</b>데이터 보정</span><span><b style="width:auto;height:auto;color:#1d2430;background:var(--C);padding:0 4px;border-radius:5px">C</b>방향·저작</span><span><b style="width:auto;height:auto;color:#fff;background:var(--D);padding:0 4px;border-radius:5px">D</b>핵심 근거 공백</span></div><div id="plist">';
  const pg = []; PARAMS.forEach(p => { if (!pg.includes(p.group)) pg.push(p.group); });
  pg.forEach(g => {
    h += `<div class="pg">${esc(g)}</div>`;
    PARAMS.filter(p => p.group === g).forEach(p => { h += `<button class="pv" data-focus="${esc(p.id)}" data-dir="up" data-pid="${esc(p.id)}"><span class="gd ${p.grade}">${p.grade}</span>${esc(p.label)}</button>`; });
  });
  h += '</div><h4>노드 종류</h4>';
  KORDER.forEach(k => { const c = NODES.filter(n => n.kind === k).length; h += `<label class="ck"><input type="checkbox" data-kind="${k}" checked><i style="background:var(--k-${k})"></i>${KIND[k].ko}<em>${c}</em></label>`; });
  h += '<h4>관계 종류</h4>';
  REL_ORDER.forEach(r => { const c = EDGES.filter(e => e.rel === r).length; h += `<label class="ck rel"><input type="checkbox" data-rel="${r}" checked><i class="ln" style="background:${REL[r].c};margin-top:7px"></i><span>${REL[r].ko}<small>${REL[r].long}</small></span><em>${c}</em></label>`; });
  h += '<h4>엣지 필터</h4><label class="ck"><input type="checkbox" id="fHard">hard(불가능·상한)만</label><label class="ck"><input type="checkbox" id="fConf">문서에서 확인된 것만 (추정 제외)</label>';
  h += '<h4>자료 상태</h4>';
  ['보유', '부분', '요청', '없음'].forEach(s => { const c = NODES.filter(n => n.status === s).length; h += `<label class="ck"><input type="checkbox" data-st="${s}" checked><i style="background:${ST[s]};border-radius:50%"></i>${s}<em>${c}</em></label>`; });
  h += '<h4>스케일 (섞어 쓰지 않는다)</h4>';
  ['S1', 'S2', 'S3'].forEach(s => { const c = NODES.filter(n => n.scale === s).length; h += `<label class="ck"><input type="checkbox" data-sc="${s}" checked>${s} ${s === 'S1' ? '부지' : s === 'S2' ? '원도심 1 km' : '도시·폐선축'}<em>${c}</em></label>`; });
  h += '<div class="btnrow"><button class="btn" id="bReset">필터 초기화</button></div>';
  $('#left').innerHTML = h;
}
function syncLeft() {
  document.querySelectorAll('#plist .pv').forEach(b => b.classList.toggle('on', !!(S.focus && S.focus.id === b.dataset.pid) || (!S.focus && S.sel === b.dataset.pid)));
}
$('#left').addEventListener('click', ev => {
  const b = ev.target.closest('[data-focus]'); if (b) { focusOn(b.dataset.focus, b.dataset.dir, 2); return; }
  if (ev.target.id === 'bReset') { resetFilters(); }
});
$('#left').addEventListener('change', ev => {
  const t = ev.target;
  const tog = (set, key) => { if (t.checked) set.add(key); else set.delete(key); };
  if (t.dataset.kind) tog(S.kinds, t.dataset.kind);
  else if (t.dataset.rel) tog(S.rels, t.dataset.rel);
  else if (t.dataset.st) tog(S.statuses, t.dataset.st);
  else if (t.dataset.sc) tog(S.scales, t.dataset.sc);
  else if (t.id === 'fHard') S.hardOnly = t.checked;
  else if (t.id === 'fConf') S.confOnly = t.checked;
  refresh(false);
});
function resetFilters() {
  S.kinds = new Set(KORDER); S.rels = new Set(REL_ORDER); S.hardOnly = false; S.confOnly = false;
  S.statuses = new Set(['보유', '부분', '요청', '없음']); S.scales = new Set(['S1', 'S2', 'S3']);
  document.querySelectorAll('#left input[type=checkbox]').forEach(c => { c.checked = c.id === 'fHard' || c.id === 'fConf' ? false : true; });
  refresh(false);
}
$('#right').addEventListener('click', ev => {
  const g = ev.target.closest('[data-go]');
  if (g) { selectNode(g.dataset.go); return; }
  const f = ev.target.closest('[data-focus]'); if (f) { focusOn(f.dataset.focus, f.dataset.dir, 2); return; }
  const gr = ev.target.closest('[data-group]'); if (gr) { S.sel = gr.dataset.group; renderRight(); applyHL(); writeHash(); return; }
  const og = ev.target.closest('[data-opengroup]'); if (og) { S.view = 'detail'; S.group = og.dataset.opengroup; S.focus = null; S.sel = null; refresh(true); }
});
/* 점검기의 링크: 개요·초점 보기에서는 그 노드로 초점을 옮기고, 전체 그래프에서는 선택 후 화면 중앙으로 */
function selectNode(id) {
  const n = BY.get(id); if (!n) return;
  if (S.view === 'matrix') { S.sel = id; S.hlGroup = null; renderMatrix(); renderRight(); writeHash(); return; }
  if (S.view === 'overview' || S.focus || S.group || !CUR.ids.has(id)) {
    if (!CUR.ids.has(id) && !S.focus && !S.group) resetFiltersSilent();
    focusOn(id); return;
  }
  S.sel = id; S.hlGroup = null; applyHL(); renderRight(); syncLeft(); writeHash(); centerOn(id);
}
function centerOn(id) {
  const n = BY.get(id); if (!n || !CUR.ids.has(id) || n.x === undefined) return;
  const r = stage.getBoundingClientRect(), t = d3.zoomTransform(svg), k = Math.max(t.k, 0.8);
  const nt = d3.zoomIdentity.translate(r.width / 2 - n.x * k, r.height / 2 - n.y * k).scale(k);
  const sel = d3.select(svg);
  if (S.anim) sel.transition().duration(400).call(zoom.transform, nt); else sel.call(zoom.transform, nt);
}

/* ═════════ 값 × 근거 표 ═════════ */
function renderMatrix() {
  const srcGroups = GROUPS.filter(g => g.kind !== 'param' && g.kind !== 'eval');
  const cell = new Map();
  EDGES.forEach(e => {
    if (e.t.kind !== 'param' || e.s.kind === 'param' || e.s.kind === 'eval') return;
    const k = e.dst + '||' + gkey(e.s);
    if (!cell.has(k)) cell.set(k, { n: 0, hard: 0, gap: 0, items: [] });
    const c = cell.get(k); c.n++; if (e.strength === 'hard') c.hard++; if (MISSING(e.s.status)) c.gap++; c.items.push(e);
  });
  const kindSpan = KORDER.filter(k => k !== 'param' && k !== 'eval').map(k => ({ k, n: srcGroups.filter(g => g.kind === k).length })).filter(x => x.n);
  let h = `<p class="mxnote"><b>값 × 근거 표</b> — 행 = 마스터플랜 값, 열 = 근거 묶음. 칸의 숫자 = 그 묶음에서 그 값으로 들어가는 직접 엣지 수(파생 노드를 거친 간접 근거는 제외). <span style="color:#d1453b">■</span> hard 엣지 포함, <span style="color:#d1453b">○</span> 자료 공백(없음·요청) 노드 포함. 칸을 누르면 오른쪽에 그 근거가 펼쳐집니다.</p>`;
  h += '<table class="mx"><thead><tr><th class="corner" rowspan="2">마스터플랜 값 ↓ &nbsp; 근거 묶음 →</th>';
  kindSpan.forEach(x => { h += `<th class="kh" colspan="${x.n}" style="background:var(--k-${x.k})">${KIND[x.k].ko}</th>`; });
  h += '<th class="kh" colspan="7" style="background:var(--muted)">요약</th></tr><tr class="r2">';
  srcGroups.forEach(g => { h += `<th class="gh" title="${esc(g.name)}"><div>${esc(g.name)}</div></th>`; });
  h += '<th class="gh"><div>직접 근거 수</div></th><th class="gh"><div>자료 공백 수</div></th><th class="gh"><div>다른 값에서 파생</div></th><th class="gh"><div>원문 근거(건)</div></th><th class="gh"><div>상충(엣지+원문)</div></th><th class="gh"><div>근거 등급</div></th><th class="gh"><div>현재 값 출처</div></th></tr></thead><tbody>';
  const colTot = srcGroups.map(() => 0);
  const pg = []; PARAMS.forEach(p => { if (!pg.includes(p.group)) pg.push(p.group); });
  const ncol = srcGroups.length + 8;
  pg.forEach(gname => {
    h += `<tr class="pgrp"><td colspan="${ncol}">${esc(gname)}</td></tr>`;
    PARAMS.filter(p => p.group === gname).forEach(p => {
      let tot = 0, gaps = 0;
      const derivIn = INS.get(p.id).filter(e => e.s.kind === 'param').length;
      h += `<tr data-pid="${esc(p.id)}" class="${S.sel === p.id ? 'sel' : ''}"><th class="rh"><button class="lnk" data-pick="${esc(p.id)}">${esc(p.label)}</button> <button class="btn" data-focus="${esc(p.id)}" data-dir="up" style="padding:0 6px;font-size:10.5px" title="그래프로 보기">↗</button></th>`;
      srcGroups.forEach((g, ci) => {
        const c = cell.get(p.id + '||' + g.key);
        if (!c) { h += '<td class="c"></td>'; return; }
        tot += c.n; gaps += c.gap; colTot[ci] += c.n;
        const a = Math.min(0.14 + 0.15 * c.n, 0.82);
        h += `<td class="c${c.hard ? ' hard' : ''}${c.gap ? ' gap' : ''}" data-pid="${esc(p.id)}" data-gk="${esc(g.key)}" style="background:color-mix(in srgb, var(--k-${g.kind}) ${Math.round(a * 100)}%, transparent)">${c.n}</td>`;
      });
      h += `<td class="sum"><b>${tot}</b></td><td class="sum" style="color:${gaps ? '#d1453b' : 'inherit'}">${gaps || ''}</td><td class="sum">${derivIn || ''}</td><td class="sum">${p.evN || ''}</td><td class="sum" style="color:${p.confN ? '#e0359e' : 'inherit'};font-weight:${p.confN ? 700 : 400}">${p.confN || ''}</td><td class="sum"><span class="gd ${p.grade}">${p.grade}</span></td><td class="sum" style="font-size:11px"><span style="color:${CUR_C[p.cur_src] || '#9aa3b0'};font-weight:700">${esc(p.cur_src || '')}</span></td></tr>`;
    });
  });
  h += '</tbody><tfoot><tr><td class="corner" style="position:sticky;left:0;bottom:0;z-index:5;text-align:left;padding:5px 10px;background:var(--panel2)">묶음별 합계</td>';
  colTot.forEach(t => { h += `<td>${t}</td>`; });
  h += '<td colspan="7"></td></tr></tfoot></table>';
  $('#matrix').innerHTML = h;
}
$('#matrix').addEventListener('click', ev => {
  const f = ev.target.closest('[data-focus]'); if (f) { focusOn(f.dataset.focus, 'up', 2); return; }
  const pk = ev.target.closest('[data-pick]');
  if (pk) { S.sel = pk.dataset.pick; S.hlGroup = null; renderMatrix(); renderRight(); writeHash(); return; }
  const c = ev.target.closest('td.c');
  if (c && c.dataset.pid) { S.sel = c.dataset.pid; S.hlGroup = c.dataset.gk; renderMatrix(); renderRight(); writeHash(); }
});
$('#matrix').addEventListener('mousemove', ev => {
  const c = ev.target.closest('td.c');
  if (!c || !c.dataset.pid) { hideTip(); return; }
  const items = EDGES.filter(e => e.dst === c.dataset.pid && e.s.kind !== 'param' && e.s.kind !== 'eval' && gkey(e.s) === c.dataset.gk);
  showTip(`<b>${esc(BY.get(c.dataset.pid).label)} ← ${esc(GBY.get(c.dataset.gk).name)}</b>` + items.map(e => `<div>· ${esc(e.s.label)} <span class="m">(${REL[e.rel].ko}·${e.strength}${MISSING(e.s.status) ? ' · ' + e.s.status : ''})</span></div>`).join(''), ev);
});
$('#matrix').addEventListener('mouseleave', hideTip);

/* ═════════ 검색 ═════════ */
const qi = $('#q'), qr = $('#qres');
let qList = [], qCur = -1;
function runSearch() {
  const q = qi.value.trim().toLowerCase();
  if (!q) { qr.style.display = 'none'; return; }
  const sc = n => {
    const L = n.label.toLowerCase(), I = n.id.toLowerCase();
    if (L.startsWith(q) || I === q) return 0;
    if (L.includes(q) || I.includes(q)) return 1;
    if ((n.value + ' ' + n.ref).toLowerCase().includes(q)) return 2;
    if ((n.desc || '').toLowerCase().includes(q)) return 3;
    return 9;
  };
  qList = NODES.map(n => ({ n, s: sc(n) })).filter(x => x.s < 9).sort((a, b) => a.s - b.s || a.n.idx - b.n.idx).slice(0, 14).map(x => x.n);
  qCur = qList.length ? 0 : -1;
  qr.innerHTML = qList.length ? qList.map((n, i) => `<button data-id="${esc(n.id)}" class="${i === 0 ? 'cur' : ''}">${esc(n.label)}<small>${esc(KIND[n.kind].ko)} · ${esc(n.group)}</small></button>`).join('') : '<button disabled>일치 없음</button>';
  qr.style.display = 'block';
}
qi.addEventListener('input', runSearch);
qi.addEventListener('keydown', ev => {
  if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
    ev.preventDefault(); if (!qList.length) return;
    qCur = (qCur + (ev.key === 'ArrowDown' ? 1 : -1) + qList.length) % qList.length;
    [...qr.children].forEach((b, i) => b.classList.toggle('cur', i === qCur));
  } else if (ev.key === 'Enter') { if (qList[qCur]) pickSearch(qList[qCur].id); }
  else if (ev.key === 'Escape') { qr.style.display = 'none'; qi.blur(); }
});
qr.addEventListener('click', ev => { const b = ev.target.closest('button[data-id]'); if (b) pickSearch(b.dataset.id); });
function pickSearch(id) { qr.style.display = 'none'; qi.value = ''; if (S.view === 'matrix' || S.view === 'overview') S.view = 'detail'; resetFiltersSilent(); focusOn(id); }
function resetFiltersSilent() {
  S.kinds = new Set(KORDER); S.rels = new Set(REL_ORDER); S.hardOnly = false; S.confOnly = false;
  S.statuses = new Set(['보유', '부분', '요청', '없음']); S.scales = new Set(['S1', 'S2', 'S3']);
  document.querySelectorAll('#left input[type=checkbox]').forEach(c => { c.checked = !(c.id === 'fHard' || c.id === 'fConf'); });
}
document.addEventListener('click', ev => { if (!ev.target.closest('.search')) qr.style.display = 'none'; });

/* ═════════ 해시(딥링크) ═════════ */
function writeHash() {
  const p = new URLSearchParams();
  p.set('v', S.view);
  if (S.focus) { p.set('f', S.focus.id); p.set('d', S.focus.dir); p.set('h', S.focus.hops); }
  if (S.group) p.set('g', S.group);
  if (S.sel) p.set('sel', S.sel);
  if (S.color !== 'kind') p.set('c', S.color);
  if (!S.anim) p.set('anim', 0);
  try { history.replaceState(null, '', '#' + p.toString()); } catch (e) { /* file:// 일부 환경 */ }
}
function readHash() {
  const p = new URLSearchParams(location.hash.slice(1));
  if (p.get('v') && ['overview', 'detail', 'matrix'].includes(p.get('v'))) S.view = p.get('v');
  if (p.get('c') && ['kind', 'grade', 'cur'].includes(p.get('c'))) S.color = p.get('c');
  if (p.get('anim') === '0') S.anim = false;
  if (p.get('f') && BY.has(p.get('f'))) { S.focus = { id: p.get('f'), dir: p.get('d') || defDir(BY.get(p.get('f'))), hops: +(p.get('h') || 2) }; S.view = 'detail'; }
  if (p.get('g') && GBY.has(p.get('g'))) { S.group = p.get('g'); S.view = 'detail'; }
  if (p.get('sel') && (BY.has(p.get('sel')) || GBY.has(p.get('sel')))) S.sel = p.get('sel');
  if (p.get('th') === 'dark' || p.get('th') === 'light') S.theme = p.get('th');
}

/* ═════════ 내보내기 · 도움말 · 테마 ═════════ */
function svgString() {
  const P = PAL[curTheme()], L = CUR.L; if (!L) return null;
  const clone = svg.cloneNode(true);
  clone.querySelectorAll('[data-hit]').forEach(x => x.remove());
  const v = clone.querySelector('#view'); v.removeAttribute('transform');
  const b = L.bbox, w = b.x1 - b.x0 + 20, h = b.y1 - b.y0 + 20;
  clone.setAttribute('xmlns', NS); clone.setAttribute('viewBox', `${b.x0 - 10} ${b.y0 - 10} ${w} ${h}`); clone.setAttribute('width', w); clone.setAttribute('height', h);
  clone.removeAttribute('style');
  const bg = document.createElementNS(NS, 'rect'); bg.setAttribute('x', b.x0 - 10); bg.setAttribute('y', b.y0 - 10); bg.setAttribute('width', w); bg.setAttribute('height', h); bg.setAttribute('fill', P.bg);
  clone.insertBefore(bg, clone.querySelector('#view'));
  return { s: new XMLSerializer().serializeToString(clone), w, h };
}
function download(name, blob) { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
function exportSVG() { const r = svgString(); if (!r) return; download('knowledge_graph_' + S.view + '.svg', new Blob([r.s], { type: 'image/svg+xml' })); }
function exportPNG() {
  const r = svgString(); if (!r) return;
  const img = new Image();
  img.onload = () => { const sc = 2, c = document.createElement('canvas'); c.width = r.w * sc; c.height = r.h * sc; const x = c.getContext('2d'); x.scale(sc, sc); x.drawImage(img, 0, 0, r.w, r.h); c.toBlob(b => download('knowledge_graph_' + S.view + '.png', b), 'image/png'); };
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(r.s);
}
function helpHtml() {
  const rel = REL_ORDER.map(r => `<tr><td><span style="display:inline-block;width:26px;height:3px;background:${REL[r].c};vertical-align:middle"></span></td><td><b>${REL[r].ko}</b></td><td>${REL[r].long}</td></tr>`).join('');
  return `<h2>읽는 법</h2>
<p>노드 = 계획에 관여하는 것(방향·계획·법규·데이터·파생 제약·값·평가함수). 엣지 <b>A → B</b> = "A가 B를 정한다/한정한다/보정한다". <b>왼쪽 열은 원천, 오른쪽 열은 결과</b>입니다. 마스터플랜 값은 다시 다른 값을 정하므로(예: 용도 구성 → 주차·교통·오수) 값 열은 오른쪽으로 여러 칸으로 나뉩니다.</p>
<h3>세 가지 보기</h3>
<ul><li><b>한눈에</b>: 묶음(그룹) 단위 구조. 선 위 숫자 = 묶음 사이 엣지 수. 묶음을 더블클릭하면 그 노드들로 들어갑니다.</li>
<li><b>전체 그래프</b>: 노드 전부. 마우스를 올리면 그 노드의 연결이 강조됩니다. 노드를 <b>더블클릭</b>하거나 왼쪽 값 목록을 누르면 <b>초점 보기</b> — 그 노드의 상류(정하는 것)·하류(영향 주는 것)만 단계(1–3)별로 남깁니다.</li>
<li><b>값 × 근거 표</b>: 어느 근거 묶음이 어느 값에 몇 개의 엣지를 보내는지 한 장으로.</li></ul>
<h3>엣지(관계) — 색</h3><table>${rel}</table>
<p>굵은 선 = hard(불가능·상한: 규제·법정), 가는 선 = soft(조정·참고). <b>점선 = 추정</b>(문서로 확인하지 못하고 설계 논리로 이은 것), 점점선 = 충돌.</p>
<h3>노드 표시</h3>
<ul><li>왼쪽 작은 점 = 자료 상태 — <span style="color:#2a9d6a">●</span>보유 <span style="color:#e0a31e">●</span>부분 <span style="color:#e07a1e">●</span>요청 <span style="color:#d1453b">●</span>없음. 점선 테두리(황색·주황·적색)도 같은 뜻입니다. 빨간 점선 = <b>아직 못 구한 자료</b>.</li>
<li><b style="color:#d1453b">T4</b> = 언론·2차자료. 공모·지구단위계획 문서에는 쓰지 않는다(원문 치환 전).</li>
<li>값 노드 오른쪽 원 = <b>근거 등급</b>: <span class="gd A">A</span> T1·T2 근거가 hard로 직접 한정 · <span class="gd B">B</span> 확인된 데이터가 보정 · <span class="gd C">C</span> 방향·저작뿐 · <span class="gd D">D</span> 핵심 한정 근거가 자료 공백.</li>
<li>상단 '색'을 바꾸면 값 노드를 <b>근거 등급</b> 또는 <b>현재 값 출처</b>(고정입력·법정·실측·혼합·저작·가정·미산정)로 칠합니다. 등급은 '쓸 수 있는 근거'이고, 현재 값 출처는 '지금 실제로 무엇에 근거했는가'입니다 — 둘의 차이가 연결할 일감입니다.</li></ul>
<h3>근거 번호 (K1-031 같은 표시)</h3>
<p>점선 밑줄이 있는 <span class="fid">K1-031</span> 은 PDF·문서 원문에서 쪽 단위로 뽑은 사실의 번호입니다. 마우스를 올리면 요지, 누르면 전문과 쪽 번호가 열립니다. K1 = 2030 도시기본계획, K2 = 도시재생 계획서·성과 보고서, K3a = 417쪽 연구·시민조사, K3b = 매장유산·경관·공모 가이드라인·구 역사 문헌. 에이전트가 추출한 것이라 인용 전 원문 대조가 필요합니다.</p>
<h3>이 그래프의 한계</h3>
<ul><li>엣지의 <b>basis=확인</b>은 프로젝트 문서·PDF에서 직접 확인했다는 뜻이지 원문 대조를 마쳤다는 뜻은 아닙니다. 수치는 해당 문서의 인용이므로 인용 전 원문 확인이 필요합니다([원문 미확인]).</li>
<li>현황 앵커(3,822억·79,438㎡ 등)는 대부분 언론 경유 T4입니다.</li>
<li>S1·S2·S3 스케일 필터가 있습니다. S3 통계로 S1 프로그램을 정당화하지 않습니다.</li>
<li>근거 등급 규칙은 코드로 계산됩니다(노드 CSV를 고치면 등급도 바뀝니다). "현재 값 출처"는 감사자의 분류이며 CSV(cur_src)에서 고칩니다.</li></ul>
<h3>단축키</h3><ul><li><kbd>/</kbd> 검색 · <kbd>Esc</kbd> 선택·초점 해제 · 휠 확대 · 드래그 이동 · 노드 클릭 = 오른쪽 패널에 근거 목록</li></ul>
<p style="text-align:right"><button class="btn pri" id="helpClose">닫기</button></p>`;
}
$('#bHelp').addEventListener('click', () => { $('#helpbody').innerHTML = helpHtml(); $('#help').style.display = 'flex'; });
function openFact(fid) {
  const ev = EVBY.get(fid); if (!ev) return;
  const ns = (ev.nodes || []).map(id => BY.get(id)).filter(Boolean);
  $('#helpbody').innerHTML = `<h2>원문 근거 ${esc(fid)}</h2>${evItem(ev)}<h3>이 사실이 붙은 노드</h3><div>${ns.map(n => `<button class="btn" data-pickfact="${esc(n.id)}" style="margin:2px">${esc(n.label)}</button>`).join('')}</div><p class="id" style="color:var(--muted);font-size:11px">에이전트가 원문에서 쪽 단위로 추출한 요지입니다 — 인용 전 원문 대조가 필요합니다.</p><p style="text-align:right"><button class="btn pri" id="helpClose">닫기</button></p>`;
  $('#help').style.display = 'flex';
}
document.addEventListener('click', ev => {
  const f = ev.target.closest('[data-fid]'); if (f) { openFact(f.dataset.fid); return; }
  const pf = ev.target.closest('[data-pickfact]'); if (pf) { $('#help').style.display = 'none'; selectNode(pf.dataset.pickfact); }
});
$('#help').addEventListener('click', ev => { if (ev.target.id === 'help' || ev.target.id === 'helpClose') $('#help').style.display = 'none'; });
$('#bFit').addEventListener('click', () => fit(true));
$('#bLeft').addEventListener('click', () => { document.body.classList.toggle('noleft'); setTimeout(() => fit(false), 30); });
$('#bRight').addEventListener('click', () => { document.body.classList.toggle('noright'); setTimeout(() => fit(false), 30); });
$('#bTheme').addEventListener('click', () => { S.theme = curTheme() === 'dark' ? 'light' : 'dark'; applyTheme(); refresh(false); });
$('#bSvg').addEventListener('click', exportSVG);
$('#bPng').addEventListener('click', exportPNG);
$('#colorsel').addEventListener('change', ev => { S.color = ev.target.value; refresh(false); });
$('#tabs').addEventListener('click', ev => { const b = ev.target.closest('button'); if (b) setView(b.dataset.v); });
function applyTheme() { document.documentElement.setAttribute('data-theme', curTheme()); }
document.addEventListener('keydown', ev => {
  if (ev.key === '/' && document.activeElement !== qi) { ev.preventDefault(); qi.focus(); }
  else if (ev.key === 'Escape' && document.activeElement !== qi) {
    if ($('#help').style.display === 'flex') { $('#help').style.display = 'none'; return; }
    if (S.sel) { S.sel = null; applyHL(); renderRight(); syncLeft(); writeHash(); }
    else if (S.focus || S.group) clearFocus();
  }
});
window.addEventListener('resize', debounce(() => fit(false), 150));
window.addEventListener('hashchange', () => { readHash(); refresh(false); });
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { if (S.theme === 'auto') { applyTheme(); refresh(false); } });

/* ═════════ 시작 ═════════ */
if (innerWidth < 1450) document.body.classList.add('noleft');
if (innerWidth < 1250) document.body.classList.add('noright');
buildLeft();
readHash();
applyTheme();
refresh(false);
window.__kg = { S, NODES, EDGES, PARAMS, GAPLIST, svgString, gradeOf, ready: true };
document.title = '구경주역 마스터플랜 지식그래프';
})();
