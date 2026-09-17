import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import * as echarts from "echarts";
import cfg from "./layers.json";

// ---- 배경지도 -------------------------------------------------------------
let VWORLD_KEY = "";
try { VWORLD_KEY = (await import("./config.js")).VWORLD_KEY || ""; } catch { /* config.js 없음 → Carto만 */ }
const BASEMAPS = {
  osm: { title: "OSM", tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"], attribution: "© OpenStreetMap contributors" },
  vbase: VWORLD_KEY ? { title: "V-World", tiles: [`https://api.vworld.kr/req/wmts/1.0.0/${VWORLD_KEY}/Base/{z}/{y}/{x}.png`], attribution: "© 국토지리정보원 V-World" } : null,
  vsat:  VWORLD_KEY ? { title: "항공", tiles: [`https://api.vworld.kr/req/wmts/1.0.0/${VWORLD_KEY}/Satellite/{z}/{y}/{x}.jpeg`], attribution: "© 국토지리정보원 V-World" } : null,
};
const DEFAULT_BASE = VWORLD_KEY ? "vbase" : "osm";
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
const list = document.getElementById("layer-list");
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
    }
    // 클릭 팝업 + 선택 패널
    map.on("click", L.id, (e) => {
      const p = e.features[0].properties;
      new maplibregl.Popup({ closeButton: false, maxWidth: "320px" }).setLngLat(e.lngLat).setHTML(popupHtml(p, L.popup)).addTo(map);
      document.getElementById("sel-body").innerHTML = `<div class="muted" style="margin-bottom:6px">${L.title}</div>` + popupHtml(p, Object.keys(p));
    });
    map.on("mouseenter", L.id, () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", L.id, () => (map.getCanvas().style.cursor = ""));
    // 사이드바 항목 (json 순서 = 그리기 순서 아래→위; 목록은 위가 최상단)
    const li = document.createElement("li");
    li.innerHTML = `<label><input type="checkbox" ${L.visible ? "checked" : ""}><span><span class="lt">${L.title}</span><span class="note">${L.source_note}</span></span></label>
      <div class="legend">${(L.legend || []).map(([c, t]) => `<span><i class="sw" style="background:${c}"></i>${t}</span>`).join("")}</div>`;
    li.querySelector("input").addEventListener("change", (ev) => ids.forEach((id) => map.setLayoutProperty(id, "visibility", ev.target.checked ? "visible" : "none")));
    list.prepend(li);
  }
  ["blocks", "blocks-ol", "blocks-lb", "zone", "stores", "tour_sites", "guesthouse"].forEach((id) => map.getLayer(id) && map.moveLayer(id));
  updateStats(); drawChart(); drawVisitors();
});

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
  if (!map.getLayer("parcels")) return;
  const feats = map.queryRenderedFeatures({ layers: ["parcels"] });
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
