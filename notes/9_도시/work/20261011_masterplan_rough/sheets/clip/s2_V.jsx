
var K = 72 / 25.4;
function rgb(h) { var c = new RGBColor(); c.red = parseInt(h.substr(1, 2), 16); c.green = parseInt(h.substr(3, 2), 16); c.blue = parseInt(h.substr(5, 2), 16); return c; }
var doc = app.documents.add(DocumentColorSpace.RGB, 400.000000 * K, 225.000000 * K);
doc.artboards[0].artboardRect = [0, 0, 400.000000 * K, -225.000000 * K];
var LY = {};
function layer(n) { if (!LY[n]) { LY[n] = doc.layers.add(); LY[n].name = n; } doc.activeLayer = LY[n]; }
function sty(it, fill, stroke, sw, op) {
  if (fill) { it.filled = true; it.fillColor = rgb(fill); } else it.filled = false;
  if (stroke) { it.stroked = true; it.strokeColor = rgb(stroke); it.strokeWidth = sw || 0.5; } else it.stroked = false;
  if (op != null) it.opacity = op; return it; }
function R(x, y, w, h, fill, stroke, sw, op) { return sty(doc.pathItems.rectangle(-y * K, x * K, w * K, h * K), fill, stroke, sw, op); }
function RR(x, y, w, h, r, fill) { return sty(doc.pathItems.roundedRectangle(-y * K, x * K, w * K, h * K, r * K, r * K), fill, null); }
function E(cx, cy, rx, ry, fill, stroke, sw, op) { return sty(doc.pathItems.ellipse(-(cy - ry) * K, (cx - rx) * K, 2 * rx * K, 2 * ry * K), fill, stroke, sw, op); }
function P(pts, closed, fill, stroke, sw, dash, op) {
  var p = doc.pathItems.add(); var a = [];
  for (var i = 0; i < pts.length; i++) a.push([pts[i][0] * K, -pts[i][1] * K]);
  p.setEntirePath(a); p.closed = closed; sty(p, fill, stroke, sw, op);
  if (dash) p.strokeDashes = dash; p.strokeCap = StrokeCap.ROUNDENDCAP; return p; }
function GR(x, y, w, h, top, bot) {
  var r = R(x, y, w, h, "#ffffff"); var g = doc.gradients.add(); g.type = GradientType.LINEAR;
  g.gradientStops[0].color = rgb(bot); g.gradientStops[1].color = rgb(top);
  var gc = new GradientColor(); gc.gradient = g; r.fillColor = gc; r.rotate(90, false, false, true, false); return r; }
function mk(s, size, font, col, track) {
  var t = doc.textFrames.add(); t.contents = (s && s.length) ? s : " "; var a = t.textRange.characterAttributes;
  try { a.size = size; a.textFont = app.textFonts.getByName(font); a.fillColor = rgb(col); if (track) a.tracking = track; }
  catch (e) { throw new Error("mk fail [" + s + "] size=" + size + " font=" + font + " col=" + col + " : " + e); }
  return t; }
function bnd(t) { var b = t.geometricBounds; return [b[0] / K, -b[1] / K, b[2] / K, -b[3] / K]; }
function place(t, x, y, al) {   // x: 왼/가운데/오른 기준, y: 글자 상자 세로 가운데(mm)
  var b = bnd(t); var w = b[2] - b[0], h = b[3] - b[1];
  var dx = (al == "c") ? x - (b[0] + w / 2) : (al == "r" ? x - b[2] : x - b[0]);
  var dy = y - (b[1] + h / 2); t.translate(dx * K, -dy * K); return t; }
function T(x, y, s, size, font, col, al, rot, track) { var t = mk(s, size, font, col, track); if (rot) t.rotate(rot); return place(t, x, y, al || "l"); }
function W(t) { var b = bnd(t); return b[2] - b[0]; }
function seq(cx, y, parts) {  // [[s, size, font, col], ...] 가운데 정렬 한 줄
  var ts = [], tot = 0; for (var i = 0; i < parts.length; i++) { var t = mk(parts[i][0], parts[i][1], parts[i][2], parts[i][3]); ts.push(t); tot += W(t); }
  var x = cx - tot / 2; for (var j = 0; j < ts.length; j++) { place(ts[j], x, y, "l"); x += W(ts[j]); } return tot; }
function IMG(path, x, y, w, h) { var p = doc.placedItems.add(); p.file = new File(path); p.width = w * K; p.height = h * K; p.position = [x * K, -y * K]; p.embed(); }
function labelIn(x0, x1, yt, yb, s, col, maxSize) {
  var w = x1 - x0, h = yb - yt;
  for (var sz = maxSize; sz >= 10; sz -= 1) {
    var t = mk(s, sz, "Pretendard-ExtraBold", col); var b = bnd(t); var tw = b[2] - b[0], th = b[3] - b[1];
    if (tw + 3 <= w && th + 2.4 <= h) { place(t, (x0 + x1) / 2, yt + th / 2 + 1.8, "c"); return "h"; }
    if (th + 1.4 <= w && tw + 3.2 <= h) { t.rotate(90); place(t, (x0 + x1) / 2, yb - tw / 2 - 2.2, "c"); return "v"; }
    t.remove();
  }
  return ""; }
function person(x, y, h, col, pose) {   // y = 발 위치(mm)
  var s = h / 5.6; var hy = y - h + 0.75 * s;
  E(x, hy, 0.62 * s, 0.62 * s, col, null);
  P([[x - 0.75 * s, y - h + 1.6 * s], [x + 0.75 * s, y - h + 1.6 * s], [x + 0.62 * s, y - 2.3 * s], [x - 0.62 * s, y - 2.3 * s]], true, col, null);
  var lw = 0.85 * s * K / 2.83;
  P([[x - 0.32 * s, y - 2.4 * s], [x - 0.5 * s - pose * 0.5 * s, y]], false, null, col, 1.2 * s);
  P([[x + 0.32 * s, y - 2.4 * s], [x + 0.5 * s + pose * 0.5 * s, y]], false, null, col, 1.2 * s);
  P([[x - 0.7 * s, y - h + 1.8 * s], [x - 1.1 * s - pose * 0.4 * s, y - 2.9 * s]], false, null, col, 0.9 * s);
  P([[x + 0.7 * s, y - h + 1.8 * s], [x + 1.1 * s + pose * 0.4 * s, y - 2.9 * s]], false, null, col, 0.9 * s); }
function tree(x, gy, r, col) { P([[x, gy], [x, gy - 2.6 - r]], false, null, "#8b7355", 0.6); E(x, gy - 2.6 - r * 1.6, r, r * 1.1, col, null); }
function dot(x, y) { E(x, y, 0.95, 0.95, "#E0393E", "#ffffff", 0.5); }

var ABOVE = [];
layer("머리글");
var tt = T(200.000000, 7.2, "\ub2e8\uba74 \uc870\ub2dd A\u2013A\u2032 \u00b7 \ub0a8\ubd81", 15, "Pretendard-Bold", "#222222", "c");
var bb = bnd(tt); P([[bb[0] - 2, 11.6], [bb[2] + 2, 11.6]], false, null, "#333333", 0.6);
seq(200.000000, 15.8, [["\uccb4\uc721\uad00\uc5d0\uc11c \uc804\uc2dc\uad00\uae4c\uc9c0, \ub300\uc9c0\ucd95\uc744 \ub530\ub77c ", 10, "Pretendard-Medium", "#444444"], ["\uc815\uc8fc \u00b7 \uc0dd\ud65c\ubb38\ud654 \u00b7 \uccb4\ud5d8 \u00b7 \uc804\uc2dc", 10, "Pretendard-Medium", "#E8776A"], ["\uc758 \uc785\uccb4\uc801 \uc5f0\uacc4", 10, "Pretendard-Medium", "#444444"]]);
layer("투시 3칸");
RR(12.000000, 20.000000, 120.670000, 8.2, 1.4, "#E8776A"); R(12.000000, 25.200000, 120.670000, 3, "#E8776A");
T(72.335000, 24.100000, "\ubd81\uce21 \u00b7 \uccb4\uc721\uad00\u00b7\uc8fc\uac70\uc2dc\uc124", 11.5, "Pretendard-SemiBold", "#ffffff", "c");
IMG("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/V_1_ps.jpg", 12.000000, 28.200000, 120.670000, 50);
R(12.000000, 78.200000, 120.670000, 8.2, "#FCECE9");
T(72.335000, 82.300000, "\u201c\uc0dd\ud65c\uccb4\uc721 / 1\uce35 \ucee4\ubba4\ub2c8\ud2f0 \u00b7 2~5\uce35 \uc8fc\uac70\u201d", 10.5, "Pretendard-Medium", "#333333", "c");
RR(139.670000, 20.000000, 120.670000, 8.2, 1.4, "#E8776A"); R(139.670000, 25.200000, 120.670000, 3, "#E8776A");
T(200.005000, 24.100000, "\uc911\uc559 \u00b7 \ubcf5\ud569\ubb38\ud654\uacf5\uac04\u00b7\uc911\uc559 \uc778\ub3c4", 11.5, "Pretendard-SemiBold", "#ffffff", "c");
IMG("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/V_2_ps.jpg", 139.670000, 28.200000, 120.670000, 50);
R(139.670000, 78.200000, 120.670000, 8.2, "#FCECE9");
T(200.005000, 82.300000, "\u201c\uc0dd\ud65c\ubb38\ud654 + \ub3d9\uc11c \uc120\ud615\uacf5\uc6d0\u201d", 10.5, "Pretendard-Medium", "#333333", "c");
RR(267.340000, 20.000000, 120.670000, 8.2, 1.4, "#E8776A"); R(267.340000, 25.200000, 120.670000, 3, "#E8776A");
T(327.675000, 24.100000, "\ub0a8\uce21 \u00b7 \uc2e4\ub0b4\uccb4\ud5d8\uad00\u00b7\uc804\uc2dc\uad00", 11.5, "Pretendard-SemiBold", "#ffffff", "c");
IMG("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/V_3_ps.jpg", 267.340000, 28.200000, 120.670000, 50);
R(267.340000, 78.200000, 120.670000, 8.2, "#FCECE9");
T(327.675000, 82.300000, "\u201c\uccb4\ud5d8 / \uc791\uac00 \uad50\ub958 / \uc804\uc2dc\u201d", 10.5, "Pretendard-Medium", "#333333", "c");
layer("강조 문구");
seq(200.000000, 94.5, [["\ub300\uc9c0\ucd95 \uc704\uc758 \uc0dd\ud65c \ub2e8\uba74 ", 17, "Pretendard-Bold", "#E8776A"], ["(\uc815\uc8fc \u00b7 \uc0dd\ud65c\ubb38\ud654 \u00b7 \uccb4\ud5d8 \u00b7 \uc804\uc2dc\uc758 \uc5f0\uc18d)", 11, "Pretendard-SemiBold", "#E8776A"]]);
layer("지반");
GR(0, 197.000000, 400.000000, 28.000000, "#9b9b98", "#ffffff");
P([[0, 197.000000], [400.000000, 197.000000]], false, null, "#1a1a1a", 1.1);
T(200.000000, 208.500000, "\ub300\uc9c0\ucd95 + \uc6d0\ub3c4\uc2ec \uc0dd\ud65c\uad8c", 14, "Pretendard-SemiBold", "#2b2b2b", "c", 0, 20);
layer("주변 건물");
R(356.366043, 180.156250, 5.575549, 16.843750, "#ffffff", "#c9c9c6", 0.4);
R(362.183281, 163.312500, 5.304185, 33.687500, "#ffffff", "#c9c9c6", 0.4);
R(370.980202, 180.156250, 0.724958, 16.843750, "#ffffff", "#c9c9c6", 0.4);
R(367.534298, 180.156250, 3.446176, 16.843750, "#ffffff", "#c9c9c6", 0.4);
R(373.424138, 180.156250, 1.921271, 16.843750, "#ffffff", "#c9c9c6", 0.4);
R(377.095257, 163.312500, 0.904743, 33.687500, "#ffffff", "#c9c9c6", 0.4);
layer("지면");
R(49.657672, 195.700000, 24.314178, 1.3, "#7FC35A");
R(77.339576, 195.700000, 8.289785, 1.3, "#5b5b5b");
R(163.496868, 195.700000, 3.373583, 1.3, "#B5DD8C");
R(217.054588, 195.700000, 16.862849, 1.3, "#B5DD8C");
R(285.697257, 195.700000, 8.423050, 1.3, "#5b5b5b");
R(318.612364, 195.700000, 3.543816, 1.3, "#9ED07A");
R(351.873946, 195.700000, 3.286352, 1.3, "#5b5b5b");
tree(52.657672, 195.700000, 2.061916, "#6DBE4B");
tree(58.657672, 195.700000, 2.097412, "#6DBE4B");
tree(64.657672, 195.700000, 1.936218, "#7CC85A");
tree(70.657672, 195.700000, 1.947065, "#7CC85A");
tree(220.054588, 195.700000, 1.928999, "#7CC85A");
tree(226.054588, 195.700000, 2.007349, "#6DBE4B");
tree(232.054588, 195.700000, 2.116823, "#6DBE4B");
layer("건축물");
R(93.521533, 177.750000, 12.661400, 19.250000, "#13998B");
R(93.521533, 158.500000, 12.661400, 19.250000, "#13998B");
R(93.521533, 139.250000, 12.661400, 19.250000, "#13998B");
R(93.521533, 120.000000, 12.661400, 19.250000, "#13998B");
R(115.784494, 182.562500, 4.220467, 14.437500, "#D93F87");
R(115.784494, 182.562500, 4.220467, 0.000000, "#D93F87");
GR(115.784494, 168.125000, 4.220467, 14.437500, "#F08A5D", "#F7CF6E");
R(115.784494, 182.562500, 4.220467, -14.437500, "#D93F87");
GR(115.784494, 153.687500, 4.220467, 28.875000, "#F08A5D", "#F7CF6E");
R(115.784494, 182.562500, 4.220467, -28.875000, "#D93F87");
GR(115.784494, 139.250000, 4.220467, 43.312500, "#F08A5D", "#F7CF6E");
R(115.784494, 182.562500, 4.220467, -43.312500, "#D93F87");
GR(115.784494, 124.812500, 4.220467, 57.750000, "#F08A5D", "#F7CF6E");
R(130.134080, 182.562500, 4.220467, 14.437500, "#D93F87");
R(130.134080, 182.562500, 4.220467, 0.000000, "#D93F87");
GR(130.134080, 168.125000, 4.220467, 14.437500, "#F08A5D", "#F7CF6E");
R(130.134080, 182.562500, 4.220467, -14.437500, "#D93F87");
GR(130.134080, 153.687500, 4.220467, 28.875000, "#F08A5D", "#F7CF6E");
R(130.134080, 182.562500, 4.220467, -28.875000, "#D93F87");
GR(130.134080, 139.250000, 4.220467, 43.312500, "#F08A5D", "#F7CF6E");
R(130.134080, 182.562500, 4.220467, -43.312500, "#D93F87");
GR(130.134080, 124.812500, 4.220467, 57.750000, "#F08A5D", "#F7CF6E");
R(144.483666, 182.562500, 4.220467, 14.437500, "#D93F87");
R(144.483666, 182.562500, 4.220467, 0.000000, "#D93F87");
GR(144.483666, 168.125000, 4.220467, 14.437500, "#F08A5D", "#F7CF6E");
R(144.483666, 182.562500, 4.220467, -14.437500, "#D93F87");
GR(144.483666, 153.687500, 4.220467, 28.875000, "#F08A5D", "#F7CF6E");
R(144.483666, 182.562500, 4.220467, -28.875000, "#D93F87");
GR(144.483666, 139.250000, 4.220467, 43.312500, "#F08A5D", "#F7CF6E");
R(144.483666, 182.562500, 4.220467, -43.312500, "#D93F87");
GR(144.483666, 124.812500, 4.220467, 57.750000, "#F08A5D", "#F7CF6E");
R(158.833253, 182.562500, 4.220467, 14.437500, "#D93F87");
R(158.833253, 182.562500, 4.220467, 0.000000, "#D93F87");
GR(158.833253, 168.125000, 4.220467, 14.437500, "#F08A5D", "#F7CF6E");
R(158.833253, 182.562500, 4.220467, -14.437500, "#D93F87");
GR(158.833253, 153.687500, 4.220467, 28.875000, "#F08A5D", "#F7CF6E");
R(158.833253, 182.562500, 4.220467, -28.875000, "#D93F87");
GR(158.833253, 139.250000, 4.220467, 43.312500, "#F08A5D", "#F7CF6E");
R(158.833253, 182.562500, 4.220467, -43.312500, "#D93F87");
GR(158.833253, 124.812500, 4.220467, 57.750000, "#F08A5D", "#F7CF6E");
R(174.396223, 120.000000, 29.807045, 19.250000, "#2B6CB0");
R(174.396223, 177.750000, 40.569234, 19.250000, "#D93F87");
R(174.396223, 158.500000, 40.569234, 19.250000, "#2B6CB0");
R(174.396223, 139.250000, 40.569234, 19.250000, "#2B6CB0");
R(234.928264, 177.750000, 20.342649, 19.250000, "#1D2F5C");
R(234.928264, 158.500000, 20.342649, 19.250000, "#1D2F5C");
R(234.928264, 120.000000, 20.342649, 19.250000, "#1D2F5C");
R(234.928264, 139.250000, 48.197728, 19.250000, "#1D2F5C");
R(258.225239, 177.750000, 24.900752, 19.250000, "#1D2F5C");
R(258.225239, 158.500000, 24.900752, 19.250000, "#1D2F5C");
R(258.225239, 120.000000, 24.900752, 19.250000, "#1D2F5C");
R(311.569122, 177.750000, 7.060515, 19.250000, "#1E9BD7");
R(311.569122, 158.500000, 7.060515, 19.250000, "#1E9BD7");
R(311.569122, 139.250000, 7.060515, 19.250000, "#1E9BD7");
R(311.569122, 120.000000, 7.060515, 19.250000, "#1E9BD7");
R(322.165851, 177.750000, 5.433307, 19.250000, "#1E9BD7");
R(322.165851, 158.500000, 5.433307, 19.250000, "#1E9BD7");
R(322.165851, 139.250000, 5.433307, 19.250000, "#1E9BD7");
R(322.165851, 120.000000, 5.433307, 19.250000, "#1E9BD7");
layer("동선");
P([[44.839702, 195.100000], [355.160298, 195.100000]], false, null, "#E0393E", 0.9, [2.8, 2.0]);
layer("라벨");
P([[96.121533, 195.100000], [96.121533, 123.200000]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(96.121533, 195.100000); dot(96.121533, 123.200000);
var r_ = labelIn(97.721533, 106.182933, 120.000000, 194.400000, "\uccb4\uc721\uad00", "#ffffff", 16); if (r_ == "") { ABOVE.push(["\uccb4\uc721\uad00", 93.521533, 106.182933, 120.000000]); }
P([[117.894727, 195.100000], [117.894727, 128.012500]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(117.894727, 195.100000); dot(117.894727, 128.012500);
P([[176.996223, 195.100000], [176.996223, 123.200000]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(176.996223, 195.100000); dot(176.996223, 123.200000);
var r_ = labelIn(178.596223, 204.203268, 120.000000, 194.400000, "\ubcf5\ud569\ubb38\ud654\uacf5\uac04", "#ffffff", 16); if (r_ == "") { ABOVE.push(["\ubcf5\ud569\ubb38\ud654\uacf5\uac04", 174.396223, 214.965457, 120.000000]); }
P([[260.825239, 195.100000], [260.825239, 123.200000]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(260.825239, 195.100000); dot(260.825239, 123.200000);
var r_ = labelIn(262.425239, 283.125992, 120.000000, 194.400000, "\uc2e4\ub0b4\uccb4\ud5d8\uad00 \u00b7 \uc791\uac00 \uad50\ub958\u00b7\ud589\uc0ac\uc2e4", "#ffffff", 16); if (r_ == "") { ABOVE.push(["\uc2e4\ub0b4\uccb4\ud5d8\uad00 \u00b7 \uc791\uac00 \uad50\ub958\u00b7\ud589\uc0ac\uc2e4", 234.928264, 283.125992, 120.000000]); }
P([[313.122436, 195.100000], [313.122436, 123.200000]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(313.122436, 195.100000); dot(313.122436, 123.200000);
var r_ = labelIn(311.569122, 318.629637, 120.000000, 194.400000, "\uc804\uc2dc\uad00", "#ffffff", 16); if (r_ == "") { ABOVE.push(["\uc804\uc2dc\uad00", 311.569122, 327.599158, 120.000000]); }
ABOVE.push(["\uc8fc\uac70\uc2dc\uc124", 115.784494, 163.053719, 124.812500]);

for (var i = 0; i < ABOVE.length; i++) {
  var q = ABOVE[i]; var cx = (q[1] + q[2]) / 2; var yt = q[3];
  P([[q[1] + 0.4, yt - 1.4], [q[1] + 0.4, yt - 2.6], [q[2] - 0.4, yt - 2.6], [q[2] - 0.4, yt - 1.4]], false, null, "#333333", 0.6);
  T(cx, yt - 5.6, q[0], 12, "Pretendard-ExtraBold", "#222222", "c");
}
T(139.419107, 114.312500, "1\uce35 \ucee4\ubba4\ub2c8\ud2f0 \u00b7 2~5\uce35 \uc8fc\uac70", 10, "Pretendard-Medium", "#555555", "c");
T(61.814761, 181.500000, "\ubd81\uce21 \uadfc\ub9b0\uacf5\uc6d0", 12, "Pretendard-ExtraBold", "#9a9a9a", "c", 0, 30);
P([[165.183660, 197.600000], [165.183660, 199.200000]], false, null, "#555555", 0.6); T(165.183660, 201.600000, "\ud5a5\uc77c\ubb38 \uc870\ub9dd\ub85c", 10.5, "Pretendard-Bold", "#3a3a3a", "c");
T(225.486013, 181.500000, "\uc911\uc559 \uc778\ub3c4", 12, "Pretendard-ExtraBold", "#9a9a9a", "c", 0, 30);
P([[289.908782, 197.600000], [289.908782, 199.200000]], false, null, "#555555", 0.6); T(289.908782, 201.600000, "\ub0a8\uce21 \ucc28\ub3c4", 10.5, "Pretendard-Bold", "#3a3a3a", "c");
layer("사람");
person(60.014761, 195.700000, 5.392530, "#4a4a4a", 0.024519);
person(63.614761, 195.700000, 5.861482, "#4a4a4a", 0.547450);
person(223.686013, 195.700000, 5.704501, "#4a4a4a", 0.547709);
person(227.286013, 195.700000, 5.661682, "#2D6CB0", -0.350411);
layer("방위");
T(10, 193.000000, "N", 20, "Pretendard-Light", "#8a8a8a", "c");
T(390.000000, 193.000000, "S", 20, "Pretendard-Light", "#8a8a8a", "c");
P([[17.0, 194.0], [41.83970225329915, 194.0], [41.83970225329915, 194.0], [42.75814249097537, 193.8173108780271], [43.53675852814686, 193.2970562748477], [44.05701313132624, 192.5184402376762], [44.23970225329915, 191.6], [44.05701313132624, 190.6815597623238], [43.53675852814686, 189.90294372515228], [42.75814249097537, 189.3826891219729], [41.83970225329915, 189.2], [28.17786601398462, 189.2]], false, null, "#1F4E5F", 1.5);
P([[25.577866, 189.200000], [28.177866, 187.800000], [28.177866, 190.600000]], true, "#1F4E5F", null);
P([[383.0, 194.0], [358.16029774670085, 194.0], [358.16029774670085, 194.0], [357.2418575090246, 193.8173108780271], [356.4632414718531, 193.2970562748477], [355.94298686867376, 192.5184402376762], [355.76029774670087, 191.6], [355.94298686867376, 190.6815597623238], [356.4632414718531, 189.90294372515228], [357.2418575090246, 189.3826891219729], [358.16029774670085, 189.2], [371.8221339860154, 189.2]], false, null, "#1F4E5F", 1.5);
P([[374.422134, 189.200000], [371.822134, 187.800000], [371.822134, 190.600000]], true, "#1F4E5F", null);
P([[44.839702, 104.350000], [44.839702, 201.000000]], false, null, "#A0237A", 0.6, [2.0, 1.6]);
E(44.839702, 100.750000, 3.3, 3.3, "#A0237A", "#ffffff", 0.6); T(44.839702, 100.850000, "A", 11, "Pretendard-Bold", "#ffffff", "c");
P([[355.160298, 104.350000], [355.160298, 201.000000]], false, null, "#A0237A", 0.6, [2.0, 1.6]);
E(355.160298, 100.750000, 3.3, 3.3, "#A0237A", "#ffffff", 0.6); T(355.160298, 100.850000, "A\u2032", 11, "Pretendard-Bold", "#ffffff", "c");
layer("범례");
var lx = 12;
R(lx, 217.6, 4.2, 3.4, "#13998B");
var tl = T(lx + 5.4, 219.3, "\uc0dd\ud65c\uccb4\uc721", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
GR(lx, 217.6, 4.2, 3.4, "#F08A5D", "#F7CF6E");
var tl = T(lx + 5.4, 219.3, "\uc8fc\uac70", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
R(lx, 217.6, 4.2, 3.4, "#D93F87");
var tl = T(lx + 5.4, 219.3, "\uadfc\ub9b0\uc0dd\ud65c\u00b7\ucee4\ubba4\ub2c8\ud2f0", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
R(lx, 217.6, 4.2, 3.4, "#2B6CB0");
var tl = T(lx + 5.4, 219.3, "\uc0dd\ud65c\ubb38\ud654", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
R(lx, 217.6, 4.2, 3.4, "#1D2F5C");
var tl = T(lx + 5.4, 219.3, "\uccb4\ud5d8\u00b7\uad50\ub958", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
R(lx, 217.6, 4.2, 3.4, "#1E9BD7");
var tl = T(lx + 5.4, 219.3, "\uc804\uc2dc", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
P([[lx, 219.3], [lx + 7, 219.3]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(lx + 7, 219.3); var tl = T(lx + 9.5, 219.3, "\ubcf4\ud589 \ub3d9\uc120 \u00b7 \uc218\uc9c1 \ub3d9\uc120", 10, "Pretendard-Medium", "#333333", "l");
T(388.000000, 219.3, "\uc218\uc9c1 11.4\ubc30 \uacfc\uc7a5 \u00b7 \uc704 3\uce78\uc740 \ub77c\uc774\ub178 \ub2e8\uba74 \ud22c\uc2dc(\ucd5c\uc885 \ubaa8\ub378)", 10, "Pretendard-Regular", "#777777", "r");

var o = new ExportOptionsPNG24(); o.artBoardClipping = true; o.horizontalScale = 333.333; o.verticalScale = 333.333; o.antiAliasing = true; o.transparency = false;
doc.exportFile(new File("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/diagrams/D6_\ub2e8\uba74\uc870\ub2dd_\ub0a8\ubd81.png"), ExportType.PNG24, o);
doc.saveAs(new File("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/diagrams/D6_\ub2e8\uba74\uc870\ub2dd_\ub0a8\ubd81.ai"), new IllustratorSaveOptions());
var po = new PDFSaveOptions(); po.preserveEditability = false; po.compatibility = PDFCompatibility.ACROBAT7;
doc.saveAs(new File("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/diagrams/D6_\ub2e8\uba74\uc870\ub2dd_\ub0a8\ubd81.pdf"), po);
doc.close(SaveOptions.DONOTSAVECHANGES);
"saved " + "D6_\ub2e8\uba74\uc870\ub2dd_\ub0a8\ubd81";