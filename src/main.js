import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import * as echarts from "echarts";
import cfg from "./layers.json";

// ---- 배경지도 -------------------------------------------------------------
let VWORLD_KEY = "";
try { VWORLD_KEY = (await import("./config.js")).VWORLD_KEY || ""; } catch { /* config.js 없음 → Carto만 */ }
const BASEMAPS = {
  osm: { title: "OSM", tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"], attribution: "© OpenStreetMap contributors" },
  vwhite: VWORLD_KEY ? { title: "백지도", tiles: [`https://api.vworld.kr/req/wmts/1.0.0/${VWORLD_KEY}/white/{z}/{y}/{x}.png`], attribution: "© 국토지리정보원 V-World" } : null,
  vbase: VWORLD_KEY ? { title: "일반", tiles: [`https://api.vworld.kr/req/wmts/1.0.0/${VWORLD_KEY}/Base/{z}/{y}/{x}.png`], attribution: "© 국토지리정보원 V-World" } : null,
  vsat:  VWORLD_KEY ? { title: "항공", tiles: [`https://api.vworld.kr/req/wmts/1.0.0/${VWORLD_KEY}/Satellite/{z}/{y}/{x}.jpeg`], attribution: "© 국토지리정보원 V-World" } : null,
};
const DEFAULT_BASE = VWORLD_KEY ? "vwhite" : "osm";
const baseSource = (k) => ({ type: "raster", tiles: BASEMAPS[k].tiles, tileSize: 256, attribution: BASEMAPS[k].attribution, maxzoom: 19 });

const map = new maplibregl.Map({
  container: "map",
  style: { version: 8, glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
           sources: { base: baseSource(DEFAULT_BASE) }, layers: [{ id: "base", type: "raster", source: "base" }] },
  center: cfg.center, zoom: cfg.zoom, maxZoom: 20, attributionControl: { compact: true },
});
window.__map = map; // debug
map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
map.addControl(new maplibregl.ScaleControl({ maxWidth: 120, unit: "metric" }), "bottom-right");

// ---- 레이어 ---------------------------------------------------------------
const base = import.meta.env.BASE_URL;
const groupsEl = document.getElementById("layer-groups");
const groupBox = {};   // 그룹명 → <details>
for (const g of cfg.groups) {
  const d = document.createElement("details"); d.className = "group"; d.open = true;
  d.innerHTML = `<summary>${g}<span class="cnt"></span></summary>`;
  groupsEl.appendChild(d); groupBox[g] = d;
}
const refreshCounts = () => { for (const d of Object.values(groupBox)) { const n = d.querySelectorAll(".layer > label input:checked").length, t = d.querySelectorAll(".layer").length; d.querySelector(".cnt").textContent = `${n}/${t}`; } };
// 탭
const showTab = (name) => { document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === name)); document.querySelectorAll(".pane").forEach((p) => p.classList.toggle("on", p.id === `pane-${name}`)); if (name === "analysis") setTimeout(() => { for (const id of ["chart", "chart-inds", "chart-vis", "chart-traffic", "chart-pyr", "chart-yr"]) echarts.getInstanceByDom(document.getElementById(id))?.resize(); }, 0); };
document.querySelectorAll("#tabs button").forEach((b) => b.addEventListener("click", () => showTab(b.dataset.tab)));
const dataCache = {};

const fmt = (v) => (typeof v === "number" ? v.toLocaleString("ko-KR") : /^\d{4,}$/.test(String(v)) ? Number(v).toLocaleString("ko-KR") : v);
function popupHtml(props, fields) {
  return "<table>" + fields.filter((f) => props[f] !== undefined && props[f] !== "" && props[f] !== null)
    .map((f) => `<tr><td>${f}</td><td>${fmt(props[f])}</td></tr>`).join("") + "</table>";
}

map.on("load", async () => {
  for (const L of cfg.layers) {
    // 같은 파일을 쓰는 레이어는 소스를 공유 (필지 8MB를 두 번 안 받도록)
    const srcId = L.file;
    if (!map.getSource(srcId)) {
      const fc = await fetch(`${base}data/${L.file}`, { cache: "no-cache" }).then((r) => r.json());  // 데이터 갱신 시 ETag 재검증
      dataCache[srcId] = fc;
      map.addSource(srcId, { type: "geojson", data: fc });
    }
    dataCache[L.id] = dataCache[srcId];
    const vis = L.visible ? "visible" : "none";
    const ids = [];
    if (L.type === "fill") {
      map.addLayer({ id: L.id, type: "fill", source: srcId, paint: L.paint, layout: { visibility: vis }, minzoom: L.minzoom ?? 0 }); ids.push(L.id);
      if (L.outline) { map.addLayer({ id: `${L.id}-ol`, type: "line", source: srcId, paint: L.outline, layout: { visibility: vis } }); ids.push(`${L.id}-ol`); }
      if (L.label) {
        map.addLayer({ id: `${L.id}-lb`, type: "symbol", source: srcId,
          layout: { visibility: vis, "text-field": ["get", L.label.field], "text-size": L.label.size, "text-font": ["Open Sans Semibold"] },
          paint: { "text-color": "#1d2320", "text-halo-color": "#fff", "text-halo-width": 1.5 } });
        ids.push(`${L.id}-lb`);
      }
    } else if (L.type === "circle") {
      map.addLayer({ id: L.id, type: "circle", source: srcId, paint: L.paint, layout: { visibility: vis }, minzoom: L.minzoom ?? 0 }); ids.push(L.id);
    } else {
      map.addLayer({ id: L.id, type: "line", source: srcId, paint: L.paint, layout: { visibility: vis }, minzoom: L.minzoom ?? 0 }); ids.push(L.id);
      if (L.label) {
        map.addLayer({ id: `${L.id}-lb`, type: "symbol", source: srcId, layout: { visibility: vis, "symbol-placement": "point", "text-field": ["get", L.label.field], "text-size": L.label.size, "text-font": ["Open Sans Semibold"] },
          paint: { "text-color": "#3a4a44", "text-halo-color": "#fff", "text-halo-width": 1.4 } });
        ids.push(`${L.id}-lb`);
      }
    }
    // 클릭: 팝업은 핵심 4줄, 전체 속성은 '선택' 탭
    map.on("click", L.id, (e) => {
      const p = e.features[0].properties; const f = L.popup || Object.keys(p);
      const head = p[f[0]] ?? L.short; const rest = f.slice(1, 4).filter((k) => p[k] !== undefined && p[k] !== "" && p[k] !== null).map((k) => `${k} ${fmt(p[k])}`).join(" · ");
      const pop = new maplibregl.Popup({ closeButton: false, maxWidth: "260px" }).setLngLat(e.lngLat)
        .setHTML(`<div class="pt">${fmt(head)}</div><div class="pl">${rest}</div><div class="pm">전체 속성 보기 →</div>`).addTo(map);
      pop.getElement().querySelector(".pm").onclick = () => showTab("selected");
      document.getElementById("sel-body").innerHTML = `<div class="src">${L.title}</div>` + popupHtml(p, Object.keys(p).filter((k) => !["age", "yearly", "bjd"].includes(k)));
      if (p.age) drawPop(p);
      document.getElementById("tab-selected").innerHTML = `선택<span class="badge">1</span>`;
    });
    map.on("mouseenter", L.id, () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", L.id, () => (map.getCanvas().style.cursor = ""));
    // 사이드바 항목: 그룹 안에, 짧은 제목 + (i) 설명 + 켠 경우에만 범례/하위토글
    const li = document.createElement("div"); li.className = "layer" + (L.visible ? " on" : "");
    li.innerHTML = `<label><input type="checkbox" ${L.visible ? "checked" : ""}><span>${L.short}</span><button type="button" class="info" title="출처·설명">i</button></label>
      <div class="desc">${L.source_note}</div>
      <div class="legend">${(L.legend || []).map(([c, t]) => `<span><i class="sw" style="background:${c}"></i>${t}</span>`).join("")}</div>`;
    li.querySelector("input").addEventListener("change", (ev) => {
      ids.forEach((id) => map.setLayoutProperty(id, "visibility", ev.target.checked ? "visible" : "none")); li.classList.toggle("on", ev.target.checked);
      if (ev.target.checked && L.id.startsWith("pop_")) {   // 인구 단계구분도는 한 번에 하나만
        document.querySelectorAll('.layer[data-id^="pop_"]').forEach((o) => { if (o !== li && o.querySelector("input").checked) { o.querySelector("input").checked = false; o.querySelector("input").dispatchEvent(new Event("change")); } });
      }
      refreshCounts(); updateStats();
    });
    li.dataset.id = L.id;
    li.querySelector(".info").addEventListener("click", (ev) => { ev.preventDefault(); li.classList.toggle("showdesc"); });
    if (L.subfilter) {
      const sf = L.subfilter; const box = document.createElement("div"); box.className = "subfilter";
      const apply = () => { const on = [...box.querySelectorAll("input:checked")].map((x) => x.value); ids.forEach((id) => map.setFilter(id, ["in", ["get", sf.field], ["literal", on]])); updateStats(); };
      for (const v of sf.values) {
        const lab = document.createElement("label");
        lab.innerHTML = `<input type="checkbox" value="${v}" checked><i class="sw" style="background:${sf.colors[v] || "#555"}"></i>${v}`;
        lab.querySelector("input").addEventListener("change", apply); box.appendChild(lab);
      }
      const all = document.createElement("button"); all.type = "button"; all.textContent = "전체"; all.className = "sf-btn"; all.onclick = () => { box.querySelectorAll("input").forEach((x) => (x.checked = true)); apply(); };
      const none = document.createElement("button"); none.type = "button"; none.textContent = "해제"; none.className = "sf-btn"; none.onclick = () => { box.querySelectorAll("input").forEach((x) => (x.checked = false)); apply(); };
      box.append(all, none); li.appendChild(box);
    }
    (groupBox[L.group] || groupsEl).appendChild(li);
  }
  refreshCounts();
  // 질의 전용 투명 레이어: 필지 레이어를 꺼도 KPI(필지 수·노후도·공시지가)는 집계되도록
  if (map.getSource("parcels.geojson")) map.addLayer({ id: "parcels-q", type: "fill", source: "parcels.geojson", paint: { "fill-opacity": 0 }, minzoom: 14 }, "landuse");
  ["pop_total-lb", "pop_density-lb", "pop_65-lb", "pop_youth-lb", "pop_chg-lb", "reg_areas", "reg_areas-ol", "reg_areas-lb", "traffic", "busstops", "blocks", "blocks-ol", "blocks-lb", "zone", "stores", "tour_sites"].forEach((id) => map.getLayer(id) && map.moveLayer(id));
  updateStats(); drawChart(); drawVisitors(); drawTraffic();
  // 인구 카드 초기값: 경주시 전체 = 행정동 합
  const hp = dataCache["hadm_pop.geojson"]; if (hp) drawPop(null, hp);
});

// ---- 행정동 인구: 연령 피라미드 + 10년 추이 -----------------------------------
function drawPop(p, fc) {
  let age, yearly, name;
  if (p) { age = typeof p.age === "string" ? JSON.parse(p.age) : p.age; yearly = typeof p.yearly === "string" ? JSON.parse(p.yearly) : p.yearly; name = p.hadm; }
  else { // 경주시 합계
    age = {}; yearly = {}; name = "경주시 (행정동 합)";
    for (const f of fc.features) { const a = f.properties.age || {}, y = f.properties.yearly || {}; for (const k in a) age[k] = (age[k] || 0) + a[k]; for (const k in y) yearly[k] = (yearly[k] || 0) + y[k]; }
  }
  document.getElementById("pop-name").textContent = name;
  const lo = (k) => parseInt(k.replace("+", "").split("-")[0]);
  const keys = Object.keys(age).sort((a, b) => lo(a) - lo(b));
  const tot = keys.reduce((s, k) => s + age[k], 0);
  const c1 = echarts.getInstanceByDom(document.getElementById("chart-pyr")) || echarts.init(document.getElementById("chart-pyr"));
  c1.setOption({
    grid: { left: 52, right: 12, top: 6, bottom: 4 }, tooltip: { trigger: "axis", valueFormatter: (v) => v.toLocaleString() + "명" },
    xAxis: { type: "value", show: false }, yAxis: { type: "category", data: keys.map((k) => k.replace(" - ", "–").replace("세", "")), axisLabel: { fontSize: 9.5 }, axisTick: { show: false }, axisLine: { show: false } },
    series: [{ type: "bar", data: keys.map((k) => age[k]), itemStyle: { color: (d) => lo(keys[d.dataIndex]) >= 65 ? "#e07b39" : lo(keys[d.dataIndex]) <= 10 ? "#7fb3d5" : "#2c6a5c" }, barCategoryGap: "20%" }],
  }, true);
  const ys = Object.keys(yearly).sort();
  const c2 = echarts.getInstanceByDom(document.getElementById("chart-yr")) || echarts.init(document.getElementById("chart-yr"));
  c2.setOption({
    grid: { left: 52, right: 12, top: 10, bottom: 18 }, tooltip: { trigger: "axis", valueFormatter: (v) => v.toLocaleString() + "명" },
    xAxis: { type: "category", data: ys, axisLabel: { fontSize: 9.5, interval: 3 } }, yAxis: { type: "value", axisLabel: { fontSize: 9.5, formatter: (v) => (v / 1000).toFixed(0) + "k" }, splitLine: { lineStyle: { color: "#eee" } }, scale: true },
    series: [{ type: "line", data: ys.map((y) => yearly[y]), showSymbol: false, lineStyle: { width: 2, color: "#2c6a5c" }, areaStyle: { opacity: .12, color: "#2c6a5c" } }],
  }, true);
  const o65 = keys.filter((k) => lo(k) >= 65).reduce((s, k) => s + age[k], 0);
  document.getElementById("pop-note").textContent = `총 ${tot.toLocaleString()}명 · 65세↑ ${(o65 / tot * 100).toFixed(1)}% · 주민등록 2026-08 (KOSIS DT_1B04005N) · 연도별 추이 2011–2025`;
}

// ---- 방문자 시계열 (시군구 = S3, 지도와 독립) ---------------------------------
async function drawVisitors() {
  let d; try { d = await fetch(`${base}data/visitors.json`, { cache: "no-cache" }).then((r) => r.json()); } catch { return; }
  const days = Object.keys(d).sort().filter((k) => d[k]["현지인"] != null);
  if (!days.length) return;
  const ch = echarts.init(document.getElementById("chart-vis"));
  const ser = (k, c) => ({ name: k, type: "line", stack: "v", areaStyle: { opacity: .5 }, showSymbol: false, lineStyle: { width: 1 }, itemStyle: { color: c }, data: days.map((x) => Math.round(d[x][k] || 0)) });
  ch.setOption({
    grid: { left: 46, right: 8, top: 24, bottom: 20 }, tooltip: { trigger: "axis", valueFormatter: (v) => v.toLocaleString() + "명" },
    legend: { top: 0, right: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
    xAxis: { type: "category", data: days.map((x) => x.slice(4, 6) + "/" + x.slice(6)), axisLabel: { fontSize: 10 } },
    yAxis: { type: "value", axisLabel: { fontSize: 10, formatter: (v) => v / 1000 + "k" }, splitLine: { lineStyle: { color: "#eee" } } },
    series: [ser("현지인", "#8fa3ad"), ser("외지인", "#2c6a5c"), ser("외국인", "#e0a23a")],
  });
  const last = days[days.length - 1];
  document.getElementById("vis-note").textContent = `KT 이동통신 기반 순방문자 · ${days[0].slice(0,4)}.${days[0].slice(4,6)}.${days[0].slice(6)}~${last.slice(4,6)}.${last.slice(6)} · 공표 지연 약 3주 · 시군구 단위라 부지(S1) 정당화에 쓰지 않음`;
  window.addEventListener("resize", () => ch.resize());
}

// ---- 화면 통계 (지도 범위 종속) --------------------------------------------
function updateStats() {
  document.getElementById("st-zoom").textContent = map.getZoom().toFixed(1);
  if (!map.getLayer("parcels-q")) return;
  const feats = map.queryRenderedFeatures({ layers: ["parcels-q"] });
  const seen = new Set(); const jiga = [];
  for (const f of feats) {
    if (seen.has(f.properties.pnu)) continue;
    seen.add(f.properties.pnu);
    const j = Number(f.properties.jiga); if (j > 0) jiga.push(j);
  }
  jiga.sort((a, b) => a - b);
  document.getElementById("st-parcels").textContent = seen.size ? seen.size.toLocaleString() : "–";
  document.getElementById("st-jiga").textContent = jiga.length ? Math.round(jiga[jiga.length >> 1]).toLocaleString() + "원/㎡" : "–";
  // 노후도: 건물 있는 필지 중 사용승인 30년↑ 비율
  const aged = [...new Set(feats.filter((f) => f.properties.bldg_age != null).map((f) => f.properties.pnu + "|" + f.properties.bldg_age))].map((s) => +s.split("|")[1]);
  document.getElementById("st-old").textContent = aged.length ? Math.round(aged.filter((a) => a >= 30).length / aged.length * 100) + "%" : "–";
  if (map.getLayer("busstops")) {
    const bs = new Set(map.queryRenderedFeatures({ layers: ["busstops"] }).map((f) => f.properties.stop_id));
    document.getElementById("st-bus").textContent = bs.size ? bs.size.toLocaleString() : "–";
  }
  // 교통: 화면 내 정체 링크 비율
  if (map.getLayer("traffic")) {
    const tf = map.queryRenderedFeatures({ layers: ["traffic"] }); const ids = new Set(); let cong = 0, tot = 0;
    for (const f of tf) { if (ids.has(f.properties.LINK_ID)) continue; ids.add(f.properties.LINK_ID); if (f.properties.speed != null) { tot++; if (f.properties.speed < 15) cong++; } }
    document.getElementById("st-cong").textContent = tot ? `${cong}/${tot} (${Math.round(cong / tot * 100)}%)` : "–";
  }
  // 업종 분포 (화면 내 업소)
  if (map.getLayer("stores")) {
    const st = map.queryRenderedFeatures({ layers: ["stores"] }); const cnt = {}; const ids = new Set();
    for (const f of st) { if (ids.has(f.properties.bizesId)) continue; ids.add(f.properties.bizesId); cnt[f.properties.indsLclsNm] = (cnt[f.properties.indsLclsNm] || 0) + 1; }
    document.getElementById("st-stores").textContent = ids.size ? ids.size.toLocaleString() : "–";
    drawIndsChart(cnt);
  }
}
let indsChart;
function drawIndsChart(cnt) {
  const rows = Object.entries(cnt).sort((a, b) => b[1] - a[1]).slice(0, 8);
  indsChart ??= echarts.init(document.getElementById("chart-inds"));
  indsChart.setOption({
    grid: { left: 70, right: 12, top: 4, bottom: 4 }, tooltip: { trigger: "axis" },
    xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: rows.map((r) => r[0]), axisLabel: { fontSize: 11 }, axisTick: { show: false }, axisLine: { show: false } },
    series: [{ type: "bar", data: rows.map((r) => r[1]), itemStyle: { color: "#2c6a5c" }, barCategoryGap: "30%", label: { show: true, position: "right", fontSize: 10 } }],
  }, true);
}
map.on("moveend", updateStats);
map.on("idle", updateStats);   // 최초 타일 처리 완료 후에도 갱신

// ---- 차트: 획지 면적 추출 vs 고시 ----------------------------------------
function drawChart() {
  const fc = dataCache.blocks; if (!fc) return;
  const rows = fc.features.map((f) => f.properties).filter((p) => p.gosi_area_m2);
  const ch = echarts.init(document.getElementById("chart"));
  ch.setOption({
    grid: { left: 46, right: 8, top: 26, bottom: 22 },
    legend: { top: 0, right: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
    tooltip: { trigger: "axis", valueFormatter: (v) => v.toLocaleString() + " ㎡" },
    xAxis: { type: "category", data: rows.map((p) => p.name), axisLabel: { fontSize: 11 } },
    yAxis: { type: "value", axisLabel: { fontSize: 10, formatter: (v) => v / 1000 + "k" }, splitLine: { lineStyle: { color: "#eee" } } },
    series: [
      { name: "고시", type: "bar", data: rows.map((p) => p.gosi_area_m2), itemStyle: { color: "#c9d1cc" }, barGap: "-60%", barCategoryGap: "35%" },
      { name: "추출", type: "bar", data: rows.map((p) => Math.round(p.area_m2)), itemStyle: { color: "#2c6a5c" } },
    ],
  });
  window.addEventListener("resize", () => ch.resize());
}

// ---- 배경지도 토글 ---------------------------------------------------------
const ctl = document.getElementById("basemap-ctl");
for (const [k, b] of Object.entries(BASEMAPS)) {
  if (!b) continue;
  const btn = document.createElement("button"); btn.textContent = b.title; if (k === DEFAULT_BASE) btn.classList.add("on");
  btn.onclick = () => { map.getSource("base").setTiles(b.tiles); ctl.querySelectorAll("button").forEach((x) => x.classList.remove("on")); btn.classList.add("on"); };
  ctl.appendChild(btn);
}
if (!VWORLD_KEY) { const s = document.createElement("span"); s.className = "muted"; s.textContent = " (V-World 배경: src/config.js에 키)"; ctl.appendChild(s); }


// ---- 교통: 시간대별 · 상습정체 (build_traffic.py 산출) ------------------------
async function drawTraffic() {
  let h, c;
  try { [h, c] = await Promise.all([fetch(`${base}data/traffic_hourly.json`, { cache: "no-cache" }).then((r) => r.json()), fetch(`${base}data/traffic_congested.json`, { cache: "no-cache" }).then((r) => r.json())]); } catch { return; }
  const hours = [...Array(24).keys()].map(String);
  const ch = echarts.init(document.getElementById("chart-traffic"));
  ch.setOption({
    grid: { left: 40, right: 36, top: 24, bottom: 20 }, tooltip: { trigger: "axis" },
    legend: { top: 0, right: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
    xAxis: { type: "category", data: hours.map((x) => x + "시"), axisLabel: { fontSize: 10, interval: 2 } },
    yAxis: [{ type: "value", name: "km/h", nameTextStyle: { fontSize: 9 }, axisLabel: { fontSize: 10 }, splitLine: { lineStyle: { color: "#eee" } } },
            { type: "value", name: "정체%", nameTextStyle: { fontSize: 9 }, axisLabel: { fontSize: 10 }, max: 100, splitLine: { show: false } }],
    series: [{ name: "평균속도", type: "bar", data: hours.map((x) => h.hourly[x]?.speed_avg ?? null), itemStyle: { color: "#2c6a5c" } },
             { name: "정체 링크 %", type: "line", yAxisIndex: 1, data: hours.map((x) => h.hourly[x]?.congested_pct ?? null), itemStyle: { color: "#d7191c" }, connectNulls: false }],
  });
  const lt = h.latest; const covered = Object.keys(h.hourly).length;
  document.getElementById("traffic-note").textContent = `최신 ${lt.slice(0,4)}.${lt.slice(4,6)}.${lt.slice(6,8)} ${lt.slice(8,10)}:${lt.slice(10,12)} · 스냅샷 ${h.snapshots}개 · 시간대 ${covered}/24 수집됨 — 24시간 누적 후 혼잡시간대가 의미를 가짐`;
  const ol = document.getElementById("cong-list"); ol.innerHTML = "";
  for (const t of c.slice(0, 8)) {
    const li = document.createElement("li"); li.textContent = `${t.road || "(무명)"} — 정체 ${t.congested_pct}% · 평균 ${t.speed_avg} km/h (${t.n}회)`;
    li.onclick = () => { const f = (dataCache.traffic?.features || []).find((x) => x.properties.LINK_ID === t.linkId); if (!f) return; const cs = f.geometry.type === "LineString" ? f.geometry.coordinates : f.geometry.coordinates[0]; map.flyTo({ center: cs[Math.floor(cs.length / 2)], zoom: 16.5 }); };
    ol.appendChild(li);
  }
  window.addEventListener("resize", () => ch.resize());
}
