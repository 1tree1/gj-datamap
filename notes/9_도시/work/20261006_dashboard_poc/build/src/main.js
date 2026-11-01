// PoC: 정적 단일 HTML 시나리오 대시보드 (슬라이더 → 지오메트리 → KPI → 인포그래픽)
// 목적: (1) 단일 HTML 번들 크기, (2) file:// 오프라인 동작, (3) 슬라이더 갱신 지연 실측.
// 단위수익·원단위는 속도 측정용 가정치다(출처 없음). 실제 계획 수치로 쓰지 말 것.
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import { computeBoundsTree, disposeBoundsTree, acceleratedRaycast } from 'three-mesh-bvh';
import SunCalc from 'suncalc';
import * as echarts from 'echarts/core';
import { GaugeChart, RadarChart, ParallelChart, LineChart, BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent, ParallelComponent, RadarComponent, MarkLineComponent, MarkPointComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import plan from './plan.json';

echarts.use([GaugeChart, RadarChart, ParallelChart, LineChart, BarChart, GridComponent, TooltipComponent,
  LegendComponent, ParallelComponent, RadarComponent, MarkLineComponent, MarkPointComponent, CanvasRenderer]);
THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;

const $ = (id) => document.getElementById(id);
const SITE_AREA = 79438; // ㎡ (CLAUDE.md §1, T4 원문 미확인)

// ── 가정치(속도 측정용) ─────────────────────────────────────────────
const CAT_COLOR = { '주거':'#d9a441', '판매·음식':'#c4553a', '문화·교육·공공':'#3f7f9c', '창조산업':'#7b5ea7',
  '상업·업무':'#555b66', '여가·오락·체육':'#4f9a6a', '역사유산':'#8c6d3f', '교통·방문자':'#9aa0a6' };
const FACT = { // cat → 원단위 (㎡당)
  '주거':          { rev: 0.09, capex: 0.28, res: 1/32, jobs: 0.002, co2: 520 },
  '판매·음식':     { rev: 0.16, capex: 0.30, res: 0,    jobs: 0.030, co2: 560 },
  '문화·교육·공공': { rev: 0.04, capex: 0.34, res: 0,    jobs: 0.012, co2: 600 },
  '창조산업':      { rev: 0.10, capex: 0.30, res: 0,    jobs: 0.020, co2: 540 },
  '상업·업무':     { rev: 0.14, capex: 0.30, res: 0,    jobs: 0.025, co2: 560 },
  '여가·오락·체육': { rev: 0.05, capex: 0.30, res: 0,    jobs: 0.010, co2: 520 },
  '역사유산':      { rev: 0.02, capex: 0.40, res: 0,    jobs: 0.008, co2: 300 },
  '교통·방문자':   { rev: 0.06, capex: 0.22, res: 0,    jobs: 0.004, co2: 480 },
}; // rev: 억원/㎡·년 ×(1e-?) 아님 — 아래 계산에서 만원 단위로 취급(데모)

const OPTIONS = { // Design Option = 슬라이더 프리셋 (닫힌식 변형)
  'A 보존':   { fm: 0.80, res: 0.8, cx: 1.10, dr: 5,   rv: 0.9  },
  'B 사업성': { fm: 1.35, res: 1.0, cx: 0.95, dr: 6,   rv: 1.2  },
  'C 접근성': { fm: 1.00, res: 1.3, cx: 1.00, dr: 5,   rv: 1.0  },
  'D 조직정합': { fm: 0.90, res: 1.1, cx: 1.00, dr: 5, rv: 1.0  },
  'E 균형':   { fm: 1.10, res: 1.2, cx: 1.00, dr: 5,   rv: 1.05 },
};

// ── 3D 뷰포트 ───────────────────────────────────────────────────────
const vp = $('viewport');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
vp.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color('#ece8dd');
const camera = new THREE.PerspectiveCamera(40, 1, 1, 5000);
camera.position.set(260, 300, 420);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0, 0);
scene.add(new THREE.HemisphereLight('#ffffff', '#b5ad9a', 1.1));
const sun_light = new THREE.DirectionalLight('#fff3da', 1.6);
sun_light.position.set(-200, 300, 250);
scene.add(sun_light);

// 평면 폴리곤 → 얇은 면(도로·획지·공원)
function flat_mesh(ring, color, y) {
  const shape = new THREE.Shape(ring.map(([x, n]) => new THREE.Vector2(x, n)));
  const g = new THREE.ShapeGeometry(shape);
  g.rotateX(-Math.PI / 2);
  const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide }));
  m.position.y = y;
  return m;
}
plan.lots.forEach(l => scene.add(flat_mesh(l.ring, '#d9d2bf', 0.05)));
plan.roads.forEach(r => scene.add(flat_mesh(r.ring, '#b9b4a8', 0.1)));
plan.parks.forEach(p => scene.add(flat_mesh(p.ring, '#9cc79a', 0.12)));

// 건물: 높이 1 단위로 압출 후 scale.y로 층수·층고 반영 → 슬라이더에서 지오메트리 재생성 없음
const bld = plan.buildings.map(b => {
  const shape = new THREE.Shape(b.ring.map(([x, n]) => new THREE.Vector2(x, n)));
  const g = new THREE.ExtrudeGeometry(shape, { depth: 1, bevelEnabled: false });
  g.rotateX(-Math.PI / 2);
  const mat = new THREE.MeshStandardMaterial({ color: CAT_COLOR[b.cat] || '#999', roughness: 0.85 });
  const mesh = new THREE.Mesh(g, mat);
  mesh.userData = b;
  scene.add(mesh);
  return mesh;
});

function resize() {
  const w = vp.clientWidth, h = vp.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(vp);
resize();

// ── KPI 닫힌식 ──────────────────────────────────────────────────────
const state = { fm: 1, res: 1, cx: 1, dr: 5, rv: 1 };

function floors_of(b) { return Math.max(1, Math.round(b.floors * state.fm * (b.cat === '주거' ? state.res ** 0.5 : 1))); }

function compute_kpi() {
  let gfa = 0, res = 0, jobs = 0, co2 = 0, rev = 0, capex = 0, gfa_res = 0, gfa_pub = 0;
  for (const b of plan.buildings) {
    const f = floors_of(b), a = b.fp * f, k = FACT[b.cat] || FACT['판매·음식'];
    gfa += a; res += a * k.res; jobs += a * k.jobs; co2 += a * k.co2; // kgCO2e
    rev += a * k.rev * state.rv; capex += a * k.capex * state.cx;      // 만원 단위 데모
    if (b.cat === '주거') gfa_res += a;
    if (b.cat === '문화·교육·공공') gfa_pub += a;
  }
  const park = plan.parks.reduce((s, p) => s + ring_area(p.ring), 0);
  // 현금흐름 30년: 1~3년차 공사비 균등, 4년차부터 수익(연 rev), 매 5년 보수 1.5%
  const cf = [];
  for (let t = 0; t <= 30; t++) cf.push(t >= 1 && t <= 3 ? -capex / 3 : (t >= 4 ? rev - capex * 0.015 * (t % 5 === 0 ? 1 : 0) : 0));
  const dr = state.dr / 100;
  let npv = 0; for (let t = 0; t < cf.length; t++) npv += cf[t] / (1 + dr) ** t;
  const irr = irr_bisect(cf);
  let cum = 0, be = -1; const cum_arr = cf.map(v => (cum += v));
  for (let t = 0; t < cum_arr.length; t++) if (cum_arr[t] >= 0) { be = t; break; }
  return { gfa, far: gfa / SITE_AREA, res, jobs, co2_t: co2 / 1000, park, npv, irr, be, cum_arr, gfa_res, gfa_pub };
}
function ring_area(r) { let s = 0; for (let i = 0; i < r.length - 1; i++) s += r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1]; return Math.abs(s) / 2; }
function irr_bisect(cf) {
  let lo = -0.5, hi = 1.0;
  const f = (r) => cf.reduce((s, v, t) => s + v / (1 + r) ** t, 0);
  if (f(lo) * f(hi) > 0) return NaN;
  for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; (f(lo) * f(m) <= 0) ? hi = m : lo = m; }
  return (lo + hi) / 2;
}

// ── 일조(저해상 레이캐스트: 동지 5시각 × 8 m 격자) ─────────────────
const LAT = 35.8392, LON = 129.2181; // 구 경주역 부근(개략)
let sun_dirs = [];
for (const h of [9, 11, 13, 15, 16]) {
  const d = new Date(Date.UTC(2026, 11, 22, h - 9, 0)); // KST = UTC+9
  const p = SunCalc.getPosition(d, LAT, LON);
  if (p.altitude > 0.05) sun_dirs.push(new THREE.Vector3(-Math.sin(p.azimuth) * Math.cos(p.altitude), Math.sin(p.altitude), Math.cos(p.azimuth) * Math.cos(p.altitude)));
}
const sensors = [];
for (let x = -150; x <= 150; x += 8) for (let z = -470; z <= 470; z += 8) sensors.push(new THREE.Vector3(x, 0.5, z));
const ray = new THREE.Ray();
function sun_ratio() {
  // 현재 층수로 건물을 하나의 지오메트리로 병합 → BVH 재구축 → 센서×태양 방향 레이캐스트
  const parts = bld.map(m => {
    const g = m.geometry.clone();
    g.applyMatrix4(new THREE.Matrix4().makeScale(1, m.scale.y, 1));
    g.deleteAttribute('normal'); g.deleteAttribute('uv');
    return g;
  });
  const merged = mergeGeometries(parts, false);
  merged.computeBoundsTree();
  let lit = 0, tot = 0;
  for (const s of sensors) for (const d of sun_dirs) {
    ray.origin.copy(s); ray.direction.copy(d);
    if (!merged.boundsTree.raycastFirst(ray, THREE.DoubleSide)) lit++;
    tot++;
  }
  T.tris = merged.attributes.position.count / 3;
  merged.dispose(); parts.forEach(p => p.dispose());
  return lit / tot;
}

// ── 차트 ────────────────────────────────────────────────────────────
const ring_defs = [
  ['FAR 사용', (k) => k.far / 2.0 * 100, '#8a2f1d'],
  ['거주인구', (k) => k.res / 3000 * 100, '#d9a441'],
  ['일자리',   (k) => k.jobs / 3000 * 100, '#3f7f9c'],
  ['IRR',      (k) => Math.max(0, (k.irr || 0) / 0.10 * 100), '#4f9a6a'],
  ['탄소(낮을수록)', (k) => Math.max(0, 100 - k.co2_t / 140000 * 100), '#555b66'],
  ['공원',     (k) => k.park / SITE_AREA / 0.15 * 100, '#7b5ea7'],
  ['공공 비중', (k) => k.gfa_pub / k.gfa / 0.25 * 100, '#c4553a'],
  ['일조(동지)', (k, sun) => sun * 100, '#d4a000'],
];
const kpi_root = $('kpis');
const rings = ring_defs.map(([name]) => {
  const d = document.createElement('div'); d.className = 'ring'; kpi_root.appendChild(d);
  const c = echarts.init(d, null, { renderer: 'canvas' });
  return c;
});
function ring_option(name, v, color, txt) {
  return { series: [{ type: 'gauge', startAngle: 90, endAngle: -270, radius: '88%', min: 0, max: 100, pointer: { show: false },
    progress: { show: true, width: 10, itemStyle: { color } }, axisLine: { lineStyle: { width: 10, color: [[1, '#e4dfd2']] } },
    axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false },
    title: { offsetCenter: [0, '62%'], fontSize: 11, color: '#7a7569' },
    detail: { offsetCenter: [0, '-5%'], fontSize: 15, fontFamily: 'Courier New', formatter: () => txt, color: '#25231f' },
    data: [{ value: Math.min(100, Math.max(0, v)), name }] }] };
}
const cash = echarts.init($('c_cash'), null, { renderer: 'canvas' });
const radar = echarts.init($('c_radar'), null, { renderer: 'canvas' });
const pcp = echarts.init($('c_pcp'), null, { renderer: 'canvas' });

// 합성 파레토 200점(데모): 5목적을 심플렉스 위에서 생성 + 약간의 노이즈
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const pareto = Array.from({ length: 200 }, () => { const w = Array.from({ length: 5 }, () => -Math.log(rnd() + 1e-9)); const s = w.reduce((a, b) => a + b, 0); return w.map(v => +(0.15 + 0.8 * v / s + 0.03 * rnd()).toFixed(3)); });
const OBJ = ['f1 접근성↑', 'f2 유산영향↓(반전)', 'f3 사업성↑', 'f4 조직정합↓(반전)', 'f5 공공성·환경↑'];
pcp.setOption({ parallelAxis: OBJ.map((n, i) => ({ dim: i, name: n, min: 0, max: 1 })), parallel: { left: 40, right: 40, top: 28, bottom: 24 },
  series: [{ type: 'parallel', lineStyle: { width: 1, opacity: 0.25, color: '#7a7569' }, data: pareto },
           { type: 'parallel', lineStyle: { width: 3, color: '#8a2f1d' }, data: [pareto[3], pareto[50], pareto[90], pareto[130], pareto[170]] }] });
radar.setOption({ radar: { indicator: OBJ.map(n => ({ name: n.split(' ')[0], max: 1 })), radius: '62%' }, series: [{ type: 'radar', data: [{ value: pareto[3], name: '현재', areaStyle: { opacity: .2 } }, { value: [0.5, 0.5, 0.5, 0.5, 0.5], name: '균형안' }] }] });

const T = {};
function update(full) {
  const t0 = performance.now();
  bld.forEach(m => { const b = m.userData; m.scale.y = floors_of(b) * b.fh; });
  const t1 = performance.now();
  const k = compute_kpi();
  const t2 = performance.now();
  if (full || sun_cache === null) { sun_cache = sun_ratio(); }
  const t3 = performance.now();
  ring_defs.forEach(([name, fn, color], i) => {
    const v = fn(k, sun_cache);
    const txt = [k.far.toFixed(2), Math.round(k.res), Math.round(k.jobs), (k.irr * 100).toFixed(1) + '%', Math.round(k.co2_t / 1000) + 'kt', (k.park / 1000).toFixed(1) + 'k㎡', (k.gfa_pub / k.gfa * 100).toFixed(0) + '%', (sun_cache * 100).toFixed(0) + '%'][i];
    rings[i].setOption(ring_option(name, v, color, txt));
  });
  cash.setOption({ grid: { left: 52, right: 14, top: 26, bottom: 22 }, tooltip: { trigger: 'axis' }, xAxis: { type: 'category', data: k.cum_arr.map((_, i) => i), name: '년' },
    yAxis: { type: 'value', name: '누적 현금(만원)' }, series: [{ type: 'line', data: k.cum_arr.map(v => Math.round(v)), showSymbol: false, areaStyle: { opacity: .12 }, lineStyle: { color: '#8a2f1d' },
      markLine: k.be >= 0 ? { symbol: 'none', data: [{ xAxis: k.be, label: { formatter: '손익분기 ' + k.be + '년' } }] } : undefined }],
    title: { text: `NPV ${Math.round(k.npv).toLocaleString()} · IRR ${isNaN(k.irr) ? '-' : (k.irr * 100).toFixed(1) + '%'}`, right: 10, top: 0, textStyle: { fontSize: 12, fontFamily: 'Courier New' } } });
  const t4 = performance.now();
  renderer.render(scene, camera);
  const t5 = performance.now();
  T.geom = t1 - t0; T.kpi = t2 - t1; T.sun = t3 - t2; T.charts = t4 - t3; T.render = t5 - t4;
  $('timing').textContent =
    `갱신 지연(ms)\n 높이 갱신 ${T.geom.toFixed(2)}\n KPI 닫힌식 ${T.kpi.toFixed(3)}\n 일조 레이캐스트 ${T.sun.toFixed(1)} (${sensors.length}점×${sun_dirs.length}시각=${sensors.length * sun_dirs.length}선, ${full ? '재계산' : '캐시'})\n 차트 9개 setOption ${T.charts.toFixed(1)}\n WebGL 렌더 ${T.render.toFixed(1)}\n 합계 ${(t5 - t0).toFixed(1)}`;
  window.__timing = { ...T, total: t5 - t0, kpi_vals: k, sensors: sensors.length, rays: sensors.length * sun_dirs.length };
}
let sun_cache = null;

// ── 입력 바인딩 ────────────────────────────────────────────────────
const sel = $('opt'); Object.keys(OPTIONS).forEach(n => { const o = document.createElement('option'); o.textContent = n; sel.appendChild(o); });
const ids = ['fm', 'res', 'cx', 'dr', 'rv'];
function sync_out() { ids.forEach(id => $('o_' + id).textContent = state[id]); }
ids.forEach(id => {
  $(id).addEventListener('input', () => { state[id] = +$(id).value; sync_out(); update(false); });
  $(id).addEventListener('change', () => { if (id === 'fm' || id === 'res') update(true); }); // 일조는 놓을 때만 재계산
});
sel.addEventListener('change', () => {
  Object.assign(state, OPTIONS[sel.value]); ids.forEach(id => $(id).value = state[id]); sync_out(); update(true);
});
sync_out(); update(true);
window.__update = update; window.__state = state;

// 벤치마크 모드: ?bench → 슬라이더 연속 조작을 모사해 평균 지연을 DOM에 기록
if (location.search.includes('bench')) {
  const run = (n, full) => {
    const acc = { geom: 0, kpi: 0, sun: 0, charts: 0, render: 0, total: 0 };
    for (let i = 0; i < n; i++) {
      state.fm = 0.6 + (i % 20) * 0.05; state.dr = 3 + (i % 9);
      update(full);
      for (const k in acc) acc[k] += (k === 'total' ? window.__timing.total : T[k]);
    }
    for (const k in acc) acc[k] = +(acc[k] / n).toFixed(3);
    return acc;
  };
  run(10, false); // 워밍업
  const hot = run(100, false), full = run(20, true);
  const pre = document.createElement('pre'); pre.id = 'bench';
  pre.textContent = JSON.stringify({ hot_slider_input: hot, full_with_sun_recompute: full, sensors: sensors.length, rays: sensors.length * sun_dirs.length, tris: T.tris, sun_dirs: sun_dirs.length }, null, 1);
  document.body.appendChild(pre);
}
(function loop() { controls.update(); renderer.render(scene, camera); requestAnimationFrame(loop); })();
