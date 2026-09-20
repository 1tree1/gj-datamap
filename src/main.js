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
const showTab = (name) => { document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === name)); document.querySelectorAll(".pane").forEach((p) => p.classList.toggle("on", p.id === `pane-${name}`)); if (name === "analysis") setTimeout(() => { for (const id of ["chart", "chart-inds", "chart-vis", "chart-traffic", "chart-pyr", "chart-yr", "chart-fr", "chart-nat", "chart-ff", "chart-ffh", "chart-biz", "chart-kpi", "chart-lp", "chart-survey", "chart-hw-cell", "chart-hw-biz", "chart-hw-age"]) echarts.getInstanceByDom(document.getElementById(id))?.resize(); }, 0); };
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
      if (L.label) {
        map.addLayer({ id: `${L.id}-lb`, type: "symbol", source: srcId, minzoom: L.label.minzoom ?? 13,
          layout: { visibility: vis, "text-field": ["get", L.label.field], "text-size": L.label.size, "text-font": ["Open Sans Semibold"], "text-offset": [0, 1.1], "text-anchor": "top", "text-allow-overlap": false },
          paint: { "text-color": "#1d2320", "text-halo-color": "#fff", "text-halo-width": 1.4 } });
        ids.push(`${L.id}-lb`);
      }
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
      if (p.fr_total !== undefined) drawForeign(p);
      if (p.per_ha !== undefined && window.__extras) { drawFFHourly(window.__extras, p.id); showTab("analysis"); }
      document.getElementById("tab-selected").innerHTML = `선택<span class="badge">1</span>`;
    });
    map.on("mouseenter", L.id, () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", L.id, () => (map.getCanvas().style.cursor = ""));
    // 사이드바 항목: 그룹 안에, 짧은 제목 + (i) 설명 + 켠 경우에만 범례/하위토글
    const li = document.createElement("div"); li.className = "layer" + (L.visible ? " on" : "");
    li.innerHTML = `<label><input type="checkbox" ${L.visible ? "checked" : ""}><span>${L.short}</span><button type="button" class="info" title="출처·설명">i</button></label>
      <div class="desc">${L.source_note}</div>
      <div class="legend">${(L.legend || []).map(([c, t]) => (c === "transparent" ? `<span class="lg-note">${t}</span>` : `<span><i class="sw" style="background:${c}"></i>${t}</span>`)).join("")}</div>`;
    li.querySelector("input").addEventListener("change", (ev) => {
      ids.forEach((id) => map.setLayoutProperty(id, "visibility", ev.target.checked ? "visible" : "none")); li.classList.toggle("on", ev.target.checked);
      if (ev.target.checked && /^(pop_|fr_pct|mc_hh)/.test(L.id)) {   // 인구 단계구분도는 한 번에 하나만
        document.querySelectorAll('.layer[data-id^="pop_"], .layer[data-id="fr_pct"], .layer[data-id="mc_hh"]').forEach((o) => { if (o !== li && o.querySelector("input").checked) { o.querySelector("input").checked = false; o.querySelector("input").dispatchEvent(new Event("change")); } });
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
    if (L.hourslider) {
      const box = document.createElement("div"); box.className = "subfilter hourbox";
      box.innerHTML = `<label class="hs-kind"><input type="radio" name="hs-kind" value="wd" checked>평일</label><label class="hs-kind"><input type="radio" name="hs-kind" value="we">주말</label>
        <input type="range" id="hs-hour" min="0" max="23" value="8" step="1"><span id="hs-label" class="hs-val">08시</span><button type="button" class="sf-btn" id="hs-play">▶ 재생</button>`;
      li.appendChild(box);
      const colorExpr = (k, h) => { const f = `${k}_${String(h).padStart(2, "0")}`; return ["case", ["!", ["has", f]], "#ccc", ["<", ["get", f], ["coalesce", ["get", "thr_c"], 15]], "#d7191c", ["<", ["get", f], ["coalesce", ["get", "thr_f"], 25]], "#fdae61", "#1a9641"]; };  // 도로등급별 임계(thr_c/thr_f)
      const applyHour = () => { const h = +box.querySelector("#hs-hour").value, k = box.querySelector("input[name=hs-kind]:checked").value;
        box.querySelector("#hs-label").textContent = `${String(h).padStart(2, "0")}시 · ${k === "wd" ? "평일" : "주말"}`; map.setPaintProperty(L.id, "line-color", colorExpr(k, h)); window.__histHour = { h, k }; updateStats(); };
      box.querySelector("#hs-hour").addEventListener("input", applyHour); box.querySelectorAll("input[name=hs-kind]").forEach((r) => r.addEventListener("change", applyHour));
      let timer = null; box.querySelector("#hs-play").addEventListener("click", (ev) => {
        if (timer) { clearInterval(timer); timer = null; ev.target.textContent = "▶ 재생"; return; }
        ev.target.textContent = "■ 정지"; timer = setInterval(() => { const r = box.querySelector("#hs-hour"); r.value = (+r.value + 1) % 24; applyHour(); }, 700); });
      applyHour();
    }
    if (L.indicator) {
      const I = L.indicator; const box = document.createElement("div"); box.className = "subfilter indbox";
      box.innerHTML = `<select id="ind-f">${Object.entries(I.fields).map(([k, t]) => `<option value="${k}" ${k === I.default ? "selected" : ""}>${t}</option>`).join("")}</select>
        <select id="ind-y">${I.years.map((y) => `<option value="${y}" ${y === I.years.at(-1) ? "selected" : ""}>${y}</option>`).join("")}<option value="chg">2018→2023 변화율</option></select><span id="ind-max" class="hs-val"></span>`;
      li.appendChild(box);
      const applyInd = () => {
        const k = box.querySelector("#ind-f").value, y = box.querySelector("#ind-y").value; const fc = dataCache[L.file];
        if (y === "chg") {
          const f = `${k}_chg_pct`;
          map.setPaintProperty(L.id, "fill-color", ["case", ["!", ["has", f]], "#e5e5e5", ["==", ["get", f], null], "#e5e5e5", ["interpolate", ["linear"], ["get", f], -50, "#b30000", -20, "#f4a582", 0, "#f7f7f7", 20, "#92c5de", 50, "#0571b0"]]);
          map.setLayoutProperty(`${L.id}-lb`, "text-field", ["case", ["==", ["get", f], null], "–", ["concat", ["to-string", ["get", f]], "%"]]);
          box.querySelector("#ind-max").textContent = `${I.fields[k]} 2018→2023 %`;
        } else {
          const f = `${k}_${y}`; const mx = Math.max(...fc.features.map((x) => +x.properties[`${k}_2023`] || 0), ...fc.features.map((x) => +x.properties[`${k}_2018`] || 0));
          map.setPaintProperty(L.id, "fill-color", ["case", ["==", ["get", f], null], "#e5e5e5", ["interpolate", ["linear"], ["get", f], 0, "#f1f5f0", mx * 0.25, "#a3c9a8", mx * 0.5, "#5f9f7a", mx * 0.75, "#2c6a5c", mx, "#0f3d34"]]);
          map.setLayoutProperty(`${L.id}-lb`, "text-field", ["case", ["==", ["get", f], null], "–", ["to-string", ["get", f]]]);
          box.querySelector("#ind-max").textContent = `${I.fields[k]} ${y} · 최대 ${mx.toLocaleString()}`;
        }
        window.__hwInd = { k, y };
      };
      box.querySelectorAll("select").forEach((el) => el.addEventListener("change", applyInd)); applyInd();
    }
    (groupBox[L.group] || groupsEl).appendChild(li);
  }
  refreshCounts();
  // 질의 전용 투명 레이어: 필지 레이어를 꺼도 KPI(필지 수·노후도·공시지가)는 집계되도록
  if (map.getSource("parcels.geojson")) map.addLayer({ id: "parcels-q", type: "fill", source: "parcels.geojson", paint: { "fill-opacity": 0 }, minzoom: 14 }, "landuse");
  ["pop_total-lb", "pop_density-lb", "pop_65-lb", "pop_youth-lb", "pop_chg-lb", "fr_pct-lb", "mc_hh-lb", "godo-lb", "sbiz_zones-lb", "tourism_complex-lb", "reg_areas", "reg_areas-ol", "reg_areas-lb", "traffic_hist", "traffic", "busstops", "blocks", "blocks-ol", "blocks-lb", "zone", "stores", "tour_sites", "fr_places"].forEach((id) => map.getLayer(id) && map.moveLayer(id));
  ["footfall_areas", "footfall_areas-ol", "footfall_areas-lb", "plan_routes", "plan_routes-lb", "plan_nodes", "plan_nodes-lb", "heritage_pts", "heritage_pts-lb", "landprice_pts", "religion", "religion-lb", "schools", "schools-lb", "hwango_grid", "hwango_grid-ol", "hwango_grid-lb", "hwango_biz2024", "hwango_biz2024-lb"].forEach((id) => map.getLayer(id) && map.moveLayer(id));
  updateStats(); drawChart(); drawVisitors(); drawTraffic(); drawExtras(); drawHwango();
  // 인구 카드 초기값: 경주시 전체 = 행정동 합
  const hp = dataCache["hadm_pop.geojson"]; if (hp) { drawPop(null, hp); drawForeign(null, hp); }
  drawNationality();
});

// ---- 외국인주민 유형 (선택 동 / 경주시 합) ---------------------------------------
const FR_KINDS = [["fr_worker", "외국인근로자"], ["fr_marriage", "결혼이민자"], ["fr_student", "유학생"], ["fr_diaspora", "외국국적동포"], ["fr_other", "기타외국인"], ["fr_naturalized", "귀화자"], ["fr_children", "외국인주민 자녀"]];
function drawForeign(p, fc) {
  const sum = (k) => fc.features.reduce((s, f) => s + (+f.properties[k] || 0), 0);
  const vals = FR_KINDS.map(([k]) => (p ? +p[k] || 0 : sum(k)));
  const mc = p ? +p.mc_households || 0 : sum("mc_households");
  document.getElementById("fr-name").textContent = p ? p.hadm : "경주시 (행정동 합)";
  const el = document.getElementById("chart-fr"); const ch = echarts.getInstanceByDom(el) || echarts.init(el);
  ch.setOption({ grid: { left: 92, right: 40, top: 4, bottom: 4 }, tooltip: { trigger: "axis", valueFormatter: (v) => v.toLocaleString() + "명" },
    xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: FR_KINDS.map((k) => k[1]), axisLabel: { fontSize: 11 }, axisTick: { show: false }, axisLine: { show: false } },
    series: [{ type: "bar", data: vals, itemStyle: { color: "#980043" }, label: { show: true, position: "right", fontSize: 10, formatter: (d) => d.value.toLocaleString() }, barCategoryGap: "30%" }] }, true);
  const tot = vals.reduce((a, b) => a + b, 0);
  document.getElementById("fr-note").textContent = `외국인주민 ${tot.toLocaleString()}명 · 다문화가구 ${mc.toLocaleString()}가구 — 행안부 2024.11 기준(KOSIS), 읍면동 단위`;
}
// ---- 국적별 등록외국인 (경주시, 법무부) — 읍면동 단위 국적 통계는 없음 ----------------
async function drawNationality() {
  let d; try { d = await fetch(`${base}data/nationality.json`, { cache: "no-cache" }).then((r) => r.json()); } catch { return; }
  const rows = Object.entries(d.nationality).filter(([k]) => k !== "계").sort((a, b) => b[1] - a[1]).slice(0, 12);
  const el = document.getElementById("chart-nat"); const ch = echarts.getInstanceByDom(el) || echarts.init(el);
  ch.setOption({ grid: { left: 92, right: 40, top: 4, bottom: 4 }, tooltip: { trigger: "axis", valueFormatter: (v) => v.toLocaleString() + "명" },
    xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: rows.map((r) => r[0].replace("(연방)", "")), axisLabel: { fontSize: 10.5 }, axisTick: { show: false }, axisLine: { show: false } },
    series: [{ type: "bar", data: rows.map((r) => r[1]), itemStyle: { color: "#5b3a8a" }, label: { show: true, position: "right", fontSize: 10, formatter: (x) => x.value.toLocaleString() }, barCategoryGap: "28%" }] });
  document.getElementById("nat-note").textContent = `경주시 등록외국인 ${(+d.nationality["계"]).toLocaleString()}명 — 법무부 ${d.prd || ""} (시군구 단위, 상위 12개국)`;
}

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
  document.getElementById("pop-note").textContent = `총 ${tot.toLocaleString()}명 · 65세↑ ${(o65 / tot * 100).toFixed(1)}% · 주민등록 2026-08 (KOSIS DT_1B04005N) · 연도별 추이 2011–2025${p && p.yearly_note ? " · " + p.yearly_note : ""}`;
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
  // 노후도: 건물 있는 필지 중 사용승인 20년↑(쇠퇴진단 기준) / 30년↑ 비율
  const aged = [...new Set(feats.filter((f) => f.properties.bldg_age != null).map((f) => f.properties.pnu + "|" + f.properties.bldg_age))].map((s) => +s.split("|")[1]);
  document.getElementById("st-old").textContent = aged.length ? `${Math.round(aged.filter((a) => a >= 20).length / aged.length * 100)}% / ${Math.round(aged.filter((a) => a >= 30).length / aged.length * 100)}%` : "–";
  if (map.getLayer("busstops")) {
    const bs = new Set(map.queryRenderedFeatures({ layers: ["busstops"] }).map((f) => f.properties.stop_id));
    document.getElementById("st-bus").textContent = bs.size ? bs.size.toLocaleString() : "–";
  }
  // 교통: 화면 내 정체 링크 비율
  if (map.getLayer("traffic_hist")) {   // 이력 표본: 시간 슬라이더가 가리키는 시간대 기준
    const { h, k } = window.__histHour || { h: 8, k: "wd" }; const fld = `${k}_${String(h).padStart(2, "0")}`;
    const tf = map.queryRenderedFeatures({ layers: ["traffic_hist"] }); const ids = new Set(); let cong = 0, tot = 0;
    for (const f of tf) { if (ids.has(f.properties.LINK_ID)) continue; ids.add(f.properties.LINK_ID); if (f.properties[fld] != null) { tot++; if (f.properties[fld] < (f.properties.thr_c ?? 15)) cong++; } }
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
    series: [{ name: "실시간 평균", type: "bar", data: hours.map((x) => h.hourly[x]?.speed_avg ?? null), itemStyle: { color: "#9fc3b6" } },
             { name: "정체 링크 %", type: "line", yAxisIndex: 1, data: hours.map((x) => h.hourly[x]?.congested_pct ?? null), itemStyle: { color: "#d7191c" }, connectNulls: false }],
  });
  // 이력 표본 요약(평일/주말) — 있으면 실시간 스냅샷 차트 위에 선으로 겹침
  try {
    const hs = await fetch(`${base}data/traffic_hist_summary.json`, { cache: "no-cache" }).then((r) => r.json());
    const line = (k, name, color) => ({ name, type: "line", data: hs.hourly[k].map((r) => r.speed_avg), showSymbol: false, lineStyle: { width: 2, color }, itemStyle: { color } });
    ch.setOption({ series: [line("wd", `평일 평균 (${hs.days.wd.length}일)`, "#1f5e42"), line("we", `주말 평균 (${hs.days.we.length}일)`, "#8e44ad")] });
    document.getElementById("traffic-note").textContent = `이력 표본 ${hs.n_days}일 (평일 ${hs.days.wd.length}·주말 ${hs.days.we.length}, ${hs.days.wd.concat(hs.days.we).sort()[0]}~) · 링크 ${hs.links.toLocaleString()} · 실시간 스냅샷 ${h.snapshots}개`;
    window.addEventListener("resize", () => ch.resize());
    renderCong(c, h); return;
  } catch { /* 이력 없음 */ }
  const lt = h.latest; const covered = Object.keys(h.hourly).length;
  document.getElementById("traffic-note").textContent = `최신 ${lt.slice(0,4)}.${lt.slice(4,6)}.${lt.slice(6,8)} ${lt.slice(8,10)}:${lt.slice(10,12)} · 스냅샷 ${h.snapshots}개 · 시간대 ${covered}/24 수집됨 — 24시간 누적 후 혼잡시간대가 의미를 가짐`;
  renderCong(c, h);
}
function renderCong(c, h) {
  const ol = document.getElementById("cong-list"); ol.innerHTML = "";
  const meta = document.getElementById("cong-meta"); if (meta && h) meta.textContent = `(실시간 스냅샷 ${h.snapshots}개, ${h.first ? h.first.slice(8,10)+":"+h.first.slice(10,12)+"~" : ""}${h.latest.slice(8,10)}:${h.latest.slice(10,12)} · 관측 ${h.min_obs ?? 1}회↑만)`;
  for (const t of c.slice(0, 8)) {
    const li = document.createElement("li"); li.textContent = `${t.road || "(무명)"} — 정체 ${t.congested_pct}% · 평균 ${t.speed_avg} km/h (${t.n}회)`;
    li.onclick = () => { const f = (dataCache.traffic?.features || []).find((x) => x.properties.LINK_ID === t.linkId); if (!f) return; const cs = f.geometry.type === "LineString" ? f.geometry.coordinates : f.geometry.coordinates[0]; map.flyTo({ center: cs[Math.floor(cs.length / 2)], zoom: 16.5 }); };
    ol.appendChild(li);
  }
}


// ---- 2026-09-20 추가: 소상공인365 유동·업종, 모니터링 전사, 공시지가, 설문, 매장유산 (web_extras.json) --------------
const AREA_COLORS = { A_hwango_grid32: "#2c6a5c", B_haengbok_hwangchon_digitized: "#8fa3ad", C_zone_buffer300: "#5f9f7a", D_zone: "#d7191c", E_center_r300: "#a3c9a8", F_cityhall_r500: "#1f5e42", G_seongdong_market_r200: "#e07b39", H_hwangridan_r300: "#8e44ad" };
const FF_ORDER = ["A_hwango_grid32", "B_haengbok_hwangchon_digitized", "C_zone_buffer300", "D_zone", "E_center_r300", "F_cityhall_r500", "G_seongdong_market_r200", "H_hwangridan_r300"];
const HOUR_BANDS = ["05–09", "09–12", "12–14", "14–18", "18–23", "23–05"];
const mk = (id) => echarts.getInstanceByDom(document.getElementById(id)) || echarts.init(document.getElementById(id));
async function drawExtras() {
  let x; try { x = await fetch(`${base}data/web_extras.json`, { cache: "no-cache" }).then((r) => r.json()); } catch { return; }
  window.__extras = x;
  // 1. ha당 일평균
  const ff = FF_ORDER.map((k) => x.footfall[k]);
  mk("chart-ff").setOption({
    grid: { left: 84, right: 56, top: 4, bottom: 4 }, tooltip: { trigger: "axis", formatter: (ps) => { const d = ff[ps[0].dataIndex]; return `${d.name}<br>ha당 ${d.per_ha.toLocaleString()} · 일평균 ${d.avg.toLocaleString()}명 · ${d.area_ha}ha<br>주거 ${d.resident.toLocaleString()} · 직장 ${d.worker.toLocaleString()}`; } },
    xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: ff.map((d) => d.short), axisLabel: { fontSize: 11 }, axisTick: { show: false }, axisLine: { show: false } },
    series: [{ type: "bar", data: ff.map((d, i) => ({ value: d.per_ha, itemStyle: { color: AREA_COLORS[FF_ORDER[i]] } })), label: { show: true, position: "right", fontSize: 10, formatter: (d) => d.value.toLocaleString() + "/ha" }, barCategoryGap: "28%" }],
  }, true);
  document.getElementById("ff-note").textContent = "통신사 추정 유동인구 월별 일평균, 2025.06~2026.06 13개월 평균 ÷ 면적(ha). B 행복황촌(80)·D 폐역 구역(79)은 G 성동시장(1,175)의 1/15. F 시청 500m는 저녁 18–23시 27%로 최고. 소상공인365 (T2)";
  drawFFHourly(x, null);
  // 3. 업종 지문
  const ba = FF_ORDER.map((k) => x.biz_area[k]);
  mk("chart-biz").setOption({
    grid: { left: 84, right: 40, top: 22, bottom: 4 }, tooltip: { trigger: "axis", formatter: (ps) => { const b = ba[ps[0].dataIndex]; return `${x.footfall[FF_ORDER[ps[0].dataIndex]].name}<br>생활 ${b.life_stores_2606} (${b.life_chg_13mo >= 0 ? "+" : ""}${b.life_chg_13mo}) · 관광·체류 ${b.tour_stores_2606} (${b.tour_chg_13mo >= 0 ? "+" : ""}${b.tour_chg_13mo})<br>생활 비중 ${b.life_share_pct}%`; } },
    legend: { top: 0, right: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
    xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: ff.map((d) => d.short), axisLabel: { fontSize: 11 }, axisTick: { show: false }, axisLine: { show: false } },
    series: [{ name: "생활(슈퍼·편의점·미용·정육·반찬·약국·백반)", type: "bar", stack: "s", data: ba.map((b) => +b.life_stores_2606), itemStyle: { color: "#2c6a5c" }, label: { show: true, position: "inside", fontSize: 9.5, color: "#fff", formatter: (d) => d.value || "" } },
             { name: "관광·체류(카페·여관·호텔·펜션)", type: "bar", stack: "s", data: ba.map((b) => +b.tour_stores_2606), itemStyle: { color: "#e07b39" }, label: { show: true, position: "inside", fontSize: 9.5, color: "#fff", formatter: (d) => d.value || "" } }],
  }, true);
  document.getElementById("biz-note").textContent = "11개 업종만의 지문(전체 상권 아님). 13개월 변화: C 구역+300m 펜션 32→45(+13), H 황리단길 카페 51→40(−11), 백반은 전 구역 증가, 슈퍼·미용·정육·약국은 ±1. 소상공인365 (T2)";
  // 4. 황오동 KPI
  const yrs = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"];
  const ffk = x.hwango_kpi["주요 상권 유동인구(명, 소상공인365 통신사 추정)"] || {}; const o = x.startup_closure["황오동 사업대상지|창업 건수"] || {}; const c_ = x.startup_closure["황오동 사업대상지|폐업 건수"] || {};
  mk("chart-kpi").setOption({
    grid: { left: 40, right: 44, top: 24, bottom: 20 }, tooltip: { trigger: "axis" }, legend: { top: 0, right: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
    xAxis: { type: "category", data: yrs, axisLabel: { fontSize: 10 } },
    yAxis: [{ type: "value", name: "건", nameTextStyle: { fontSize: 9 }, axisLabel: { fontSize: 10 }, splitLine: { lineStyle: { color: "#eee" } } }, { type: "value", name: "유동", nameTextStyle: { fontSize: 9 }, axisLabel: { fontSize: 10, formatter: (v) => v / 1000 + "k" }, splitLine: { show: false }, scale: true }],
    series: [{ name: "창업", type: "bar", data: yrs.map((y) => o[y]), itemStyle: { color: "#5f9f7a" } }, { name: "폐업", type: "bar", data: yrs.map((y) => c_[y]), itemStyle: { color: "#d7191c" } },
             { name: "유동인구(일평균)", type: "line", yAxisIndex: 1, data: yrs.map((y) => ffk[y] ?? null), itemStyle: { color: "#1d2320" }, lineStyle: { width: 2 }, connectNulls: true }],
  }, true);
  document.getElementById("kpi-note").textContent = "황오동 원도심 활성화구역(격자 32셀). 유동인구 2020 26,536 → 2024 22,646 (−15%), 2026 재추출 22,874로 재현됨. 창업 +46%·폐업 +94%(2018→24)는 전 업종 인허가(localdata) 기준. 공공도시(주) 2025.09 보고서 전사 (T2)";
  // 5. 공시지가
  const ly = Object.keys(x.landprice_avg);
  mk("chart-lp").setOption({
    grid: { left: 48, right: 48, top: 22, bottom: 20 }, tooltip: { trigger: "axis", valueFormatter: (v) => (v == null ? "–" : v.toLocaleString() + "원/㎡") }, legend: { top: 0, right: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
    xAxis: { type: "category", data: ly, axisLabel: { fontSize: 10 } },
    yAxis: [{ type: "value", axisLabel: { fontSize: 10, formatter: (v) => (v / 1e6).toFixed(1) + "백만" }, splitLine: { lineStyle: { color: "#eee" } }, scale: true }, { type: "value", axisLabel: { fontSize: 10, formatter: (v) => (v / 1e4).toFixed(0) + "만" }, splitLine: { show: false }, scale: true }],
    series: [{ name: "원도심 29필지 평균", type: "line", data: ly.map((y) => x.landprice_avg[y]), itemStyle: { color: "#2c6a5c" }, lineStyle: { width: 2 } },
             { name: "행복황촌 44개소 평균", type: "line", yAxisIndex: 1, data: ly.map((y) => x.landprice_hwangchon44[y] ?? null), itemStyle: { color: "#8e44ad" }, lineStyle: { width: 2, type: "dashed" } }],
  }, true);
  document.getElementById("lp-note").textContent = "개별공시지가 매년 1.1 기준. 원도심 29필지 2018 대비 2022 +18.7% → 2025 +10.8%. 행복황촌 44개소 2021 +9.1% → 2023 −5.6%. 두 모니터링 보고서 전사 (T2, 토지이음)";
  // 6. 시민 선호 (부지 활용·미래상 문항)
  const sv = x.surveys.filter((r) => /부지|경주역 활용|미래상/.test(r.q) && /\d/.test(r.v));
  const rows = [];
  for (const r of sv) { const vals = r.v.split("/").map((t) => parseFloat(t)); const labs = r.a.split("/").map((t) => t.trim()); if (vals.length > 1) labs.forEach((l, i) => rows.push([`${r.when.slice(0, 4)} ${l}`, vals[i], r.survey])); else rows.push([`${r.when.slice(0, 4)} ${r.a.replace(/\(.*?\)/, "")}`, vals[0], r.survey]); }
  mk("chart-survey").setOption({
    grid: { left: 150, right: 40, top: 4, bottom: 4 }, tooltip: { trigger: "axis", formatter: (ps) => `${rows[ps[0].dataIndex][0]}<br>${ps[0].value}<br>${rows[ps[0].dataIndex][2]}` },
    xAxis: { type: "value", show: false }, yAxis: { type: "category", inverse: true, data: rows.map((r) => r[0]), axisLabel: { fontSize: 10.5 }, axisTick: { show: false }, axisLine: { show: false } },
    series: [{ type: "bar", data: rows.map((r) => ({ value: r[1], itemStyle: { color: /2030/.test(r[2]) ? "#1f5e42" : /폐철도/.test(r[2]) ? "#8fa3ad" : "#8e44ad" } })), label: { show: true, position: "right", fontSize: 10, formatter: (d) => d.value }, barCategoryGap: "26%" }],
  }, true);
  // 7. 사실 카드
  const H = Object.fromEntries(x.heritage.map((h) => [h.k, h]));
  document.getElementById("fact-card").innerHTML = `<dl>
    <dt>매장유산 시굴 필요 면적</dt><dd>${(+H["시굴조사 필요 면적"].v).toLocaleString()} ㎡</dd>
    <dt>시굴 비용 · 기간 (추정)</dt><dd>${(+H["시굴조사 비용 추정"].v / 1e8).toFixed(2)}억 · 54일</dd>
    <dt>정밀발굴 비용 · 기간 (추정)</dt><dd>63~80억 · 630~700일</dd>
    <dt>1단계 시굴(안) 면적</dt><dd>${(+H["시굴조사 1단계(안) 면적"].v).toLocaleString()} ㎡</dd>
    <dt>2030 계획인구 vs 2026.08 실제</dt><dd>${x.plan_pop.plan_2030.toLocaleString()} → ${x.plan_pop.actual_2026_08.toLocaleString()} (${((x.plan_pop.actual_2026_08 / x.plan_pop.plan_2030 - 1) * 100).toFixed(0)}%)</dd>
    <div class="src">매장유산: ${x.sources.heritage} · 규정상 2m 미만 성토·성토 후 공원·주차장은 발굴 유예 / 계획인구: ${x.plan_pop.src}</div></dl>`;
  window.addEventListener("resize", () => ["chart-ff", "chart-ffh", "chart-biz", "chart-kpi", "chart-lp", "chart-survey", "chart-hw-cell", "chart-hw-biz", "chart-hw-age"].forEach((id) => echarts.getInstanceByDom(document.getElementById(id))?.resize()));
}
function drawFFHourly(x, focus) {
  const show = focus ? [...new Set(["A_hwango_grid32", "D_zone", "F_cityhall_r500", "H_hwangridan_r300", focus])] : ["A_hwango_grid32", "D_zone", "F_cityhall_r500", "H_hwangridan_r300"];
  document.getElementById("ffh-name").textContent = focus ? `${x.footfall[focus].name} 강조` : "A 황오동 · D 구역 · F 시청 · H 황리단길";
  mk("chart-ffh").setOption({
    grid: { left: 34, right: 10, top: 24, bottom: 20 }, tooltip: { trigger: "axis", valueFormatter: (v) => v + "%" }, legend: { top: 0, right: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 10.5 } },
    xAxis: { type: "category", data: HOUR_BANDS, axisLabel: { fontSize: 10 } }, yAxis: { type: "value", axisLabel: { fontSize: 10, formatter: (v) => v + "%" }, splitLine: { lineStyle: { color: "#eee" } } },
    series: show.map((k) => ({ name: x.footfall[k].short, type: "line", data: x.footfall[k].hourly_pct, showSymbol: k === focus, lineStyle: { width: k === focus ? 3.5 : 1.6, color: AREA_COLORS[k], opacity: focus && k !== focus ? 0.45 : 1 }, itemStyle: { color: AREA_COLORS[k] } })),
  }, true);
}

// ---------- 황오동 모니터링 보고서 (hwango_report.json)
const HW_K = { pop: "인구", hh: "가구", biz: "사업체", emp: "종사자", house: "주택" };
async function drawHwango() {
  let h; try { h = await fetch(`${base}data/hwango_report.json`, { cache: "no-cache" }).then((r) => r.json()); } catch { return; }
  window.__hw = h;
  drawHwCell(null);
  // 창업·폐업: 보고서 집계 vs 임시영업 제외
  const b = h.biz2024; const grp = ["숙박·체류", "카페·휴게음식", "음식점·제과", "생활소매·식품제조", "생활서비스·의료", "유흥·오락", "통신판매(무점포)"];
  mk("chart-hw-biz").setOption({
    grid: { left: 8, right: 16, top: 30, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: grp, axisLabel: { fontSize: 10, interval: 0, rotate: 28 } }, yAxis: { type: "value" },
    series: [{ name: "창업(실질)", type: "bar", data: grp.map((g) => b.open.by_group[g] || 0), color: "#1f5e42" }, { name: "폐업(실질)", type: "bar", data: grp.map((g) => -(b.close.by_group[g] || 0)), color: "#c0392b" }],
  }, true);
  document.getElementById("hw-biz-note").textContent = `보고서 창업 70·폐업 66건 중 ${b.open.popup}건은 구 경주역 부지(21)·성동시장 상인회(4)·43-5(2)의 30일 내 폐업 임시영업(축제·야시장)으로 양쪽에 중복 계상. 제외하면 창업 ${b.open.real}(점포형 ${b.open_real_storefront.length})·폐업 ${b.close.real}. 실질 순증은 숙박·체류 +${(b.open.by_group["숙박·체류"] || 0) - (b.close.by_group["숙박·체류"] || 0)}, 생활소매·식품제조 ${(b.open.by_group["생활소매·식품제조"] || 0) - (b.close.by_group["생활소매·식품제조"] || 0)}. 폐업 중 30년+ 업력 ${b.closure_age_bins["30년+"]}곳(${b.closed_over30.map((r) => r[0]).join("·")}). 인쇄쪽 82–85 (T2)`;
  // 황오동 연령구조
  const P = h.pop_hwango;
  mk("chart-hw-age").setOption({
    grid: { left: 8, right: 44, top: 48, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: P.years }, yAxis: [{ type: "value", axisLabel: { formatter: (v) => v + "%" }, max: 50 }, { type: "value", scale: true, splitLine: { show: false }, axisLabel: { formatter: (v) => (v / 1000).toFixed(1) + "k" } }],
    series: [{ name: "65세+ %", type: "line", data: P.share_65, color: "#c0392b", lineStyle: { width: 2.5 } }, { name: "20–39세 %", type: "line", data: P.share_20_39, color: "#2f6db5", lineStyle: { width: 2.5 } }, { name: "0–14세 %", type: "line", data: P.share_0_14, color: "#e8a86b" }, { name: "총인구(우축)", type: "bar", yAxisIndex: 1, data: P.total, color: "rgba(31,94,66,.25)" }],
  }, true);
  document.getElementById("hw-age-note").textContent = `황오동 주민등록 ${P.total[0].toLocaleString()}(2018) → ${P.total.at(-1).toLocaleString()}(2025.07), −${(100 - P.total.at(-1) / P.total[0] * 100).toFixed(0)}%. 20–39세는 ${P.n_20_39[0].toLocaleString()}→${P.n_20_39.at(-1).toLocaleString()}명(−${(100 - P.n_20_39.at(-1) / P.n_20_39[0] * 100).toFixed(0)}%), 65세+ 비율 ${P.share_65[0]}→${P.share_65.at(-1)}%. 인쇄쪽 81 (T2)`;
}
function drawHwCell(p) {
  const h = window.__hw; if (!h) return;
  const yrs = h.series.years; const el = document.getElementById("hw-cell-name");
  let series;
  if (p) {
    el.textContent = `셀 ${p.code} (No.${p.no})`;
    series = Object.entries(HW_K).map(([k, t]) => ({ name: t, type: "line", data: yrs.map((y) => (p[`${k}_${y}`] == null ? null : p[`${k}_${y}`])), connectNulls: true, yAxisIndex: k === "emp" ? 1 : 0 }));
  } else {
    el.textContent = "대상지 32셀 합계 (2018=100)";
    series = Object.entries(HW_K).map(([k, t]) => ({ name: t, type: "line", data: h.series.site[k].map((v) => +(v / h.series.site[k][0] * 100).toFixed(1)) }));
    series.push({ name: "황오동 인구", type: "line", data: h.series.dong.pop.map((v) => +(v / h.series.dong.pop[0] * 100).toFixed(1)), lineStyle: { type: "dashed" }, color: "#86868b" });
  }
  mk("chart-hw-cell").setOption({
    grid: { left: 8, right: p ? 40 : 16, top: 48, bottom: 8, containLabel: true }, legend: { top: 0, left: 0, textStyle: { fontSize: 11 } }, tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: yrs }, yAxis: p ? [{ type: "value" }, { type: "value", splitLine: { show: false } }] : [{ type: "value", scale: true, axisLabel: { formatter: (v) => v } }],
    color: ["#1f5e42", "#5f9f7a", "#c7641c", "#2f6db5", "#6f4fa3", "#86868b"], series,
  }, true);
  document.getElementById("hw-cell-note").textContent = p ? `인구 ${p.pop_2018 ?? "–"}→${p.pop_2023 ?? "–"} · 사업체 ${p.biz_2018}→${p.biz_2023} · 종사자 ${p.emp_2018}→${p.emp_2023}(우축) · 주택 ${p.house_2018 ?? "–"}→${p.house_2023 ?? "–"}. 5명 미만은 비공개. SGIS 100m 격자, 인쇄쪽 78–80 (T2)`
    : `대상지(격자 32셀) 인구 −14%·가구 −11%·사업체 −3%·종사자 −23%·주택 −13% (2018→2023). 종사자 감소가 가장 크다 — 성동시장 셀(549623) 사업체 264→160, KT 블록(548622) 종사자 816→649. 2020 사업체 급증은 전국사업체조사 방식 변경. 셀별 값은 archive/C_data/processed/hwango_grid_4326.geojson (T2)`;
}
