
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
var tt = T(200.000000, 7.2, "\ub2e8\uba74 \uc870\ub2dd B\u2013B\u2032 \u00b7 \ub3d9\uc11c", 15, "Pretendard-Bold", "#222222", "c");
var bb = bnd(tt); P([[bb[0] - 2, 11.6], [bb[2] + 2, 11.6]], false, null, "#333333", 0.6);
seq(200.000000, 15.8, [["\ud734\uac8c\uacf5\uac04\uc5d0\uc11c \ub808\uc9c0\ub358\uc2dc\uae4c\uc9c0, \uacf5\uc608\u00b7\uccb4\ud5d8 \uac00\uad6c\uac00 ", 10, "Pretendard-Medium", "#444444"], ["\uc911\uc559 \ub0a8\ubd81 \uc778\ub3c4", 10, "Pretendard-Medium", "#E8776A"], ["\uc5d0\uc11c \ub9cc\ub098\ub294 \ub2e8\uba74", 10, "Pretendard-Medium", "#444444"]]);
layer("투시 3칸");
RR(12.000000, 20.000000, 120.670000, 8.2, 1.4, "#E8776A"); R(12.000000, 25.200000, 120.670000, 3, "#E8776A");
T(72.335000, 24.100000, "\uc11c\uce21 \u00b7 \ud734\uac8c\uacf5\uac04\u00b7\uc57c\uc678\uccb4\ud5d8\uad00", 11.5, "Pretendard-SemiBold", "#ffffff", "c");
IMG("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/H_1_ps.jpg", 12.000000, 28.200000, 120.670000, 50);
R(12.000000, 78.200000, 120.670000, 8.2, "#FCECE9");
T(72.335000, 82.300000, "\u201c\ud734\uac8c / \uc57c\uc678 \uccb4\ud5d8 / \uacf5\uc608 \ub9c8\ucf13\u201d", 10.5, "Pretendard-Medium", "#333333", "c");
RR(139.670000, 20.000000, 120.670000, 8.2, 1.4, "#E8776A"); R(139.670000, 25.200000, 120.670000, 3, "#E8776A");
T(200.005000, 24.100000, "\uc911\uc559 \u00b7 \uacf5\ubc29\u00b7\uc804\uc2dc\ub3d9\u00b7\uc911\uc559 \ub0a8\ubd81 \uc778\ub3c4", 11.5, "Pretendard-SemiBold", "#ffffff", "c");
IMG("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/H_2_ps.jpg", 139.670000, 28.200000, 120.670000, 50);
R(139.670000, 78.200000, 120.670000, 8.2, "#FCECE9");
T(200.005000, 82.300000, "\u201c\uacf5\ubc29 / \uc804\uc2dc / \ub0a8\ubd81 \ubcf4\ud589\u201d", 10.5, "Pretendard-Medium", "#333333", "c");
RR(267.340000, 20.000000, 120.670000, 8.2, 1.4, "#E8776A"); R(267.340000, 25.200000, 120.670000, 3, "#E8776A");
T(327.675000, 24.100000, "\ub3d9\uce21 \u00b7 \uc2e4\ub0b4\uccb4\ud5d8\uad00\u00b7\ub808\uc9c0\ub358\uc2dc", 11.5, "Pretendard-SemiBold", "#ffffff", "c");
IMG("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/sheets/clip/H_3_ps.jpg", 267.340000, 28.200000, 120.670000, 50);
R(267.340000, 78.200000, 120.670000, 8.2, "#FCECE9");
T(327.675000, 82.300000, "\u201c\uccb4\ud5d8 / \uc81c\uc791 / \uac70\uc8fc\u201d", 10.5, "Pretendard-Medium", "#333333", "c");
layer("강조 문구");
seq(200.000000, 94.5, [["\uacf5\uc608\u00b7\uccb4\ud5d8 \uac00\uad6c\uc758 \ub3d9\uc11c \uc5f0\uacc4 ", 17, "Pretendard-Bold", "#E8776A"], ["(\ud734\uac8c \u00b7 \uc57c\uc678 \uccb4\ud5d8 \u00b7 \uacf5\ubc29 \u00b7 \uc2e4\ub0b4 \uccb4\ud5d8 \u00b7 \ub808\uc9c0\ub358\uc2dc)", 11, "Pretendard-SemiBold", "#E8776A"]]);
layer("지반");
GR(0, 197.000000, 400.000000, 28.000000, "#9b9b98", "#ffffff");
P([[0, 197.000000], [400.000000, 197.000000]], false, null, "#1a1a1a", 1.1);
T(200.000000, 208.500000, "\uacf5\uc608\u00b7\uccb4\ud5d8 \uac00\uad6c + \uc6d0\ub3c4\uc2ec", 14, "Pretendard-SemiBold", "#2b2b2b", "c", 0, 20);
layer("주변 건물");
R(22.000000, 95.937500, 1.858675, 101.062500, "#ffffff", "#c9c9c6", 0.4);
R(352.167674, 146.468750, 11.155274, 50.531250, "#ffffff", "#c9c9c6", 0.4);
R(364.929896, 180.156250, 11.851216, 16.843750, "#ffffff", "#c9c9c6", 0.4);
layer("지면");
R(83.782292, 195.700000, 81.137173, 1.3, "#9ED07A");
R(199.340625, 195.700000, 30.387156, 1.3, "#B5DD8C");
R(293.217618, 195.700000, 16.734542, 1.3, "#E7D9BC");
R(338.513506, 195.700000, 11.361085, 1.3, "#5b5b5b");
tree(88.345499, 195.700000, 2.061916, "#6DBE4B");
tree(97.471913, 195.700000, 2.097412, "#6DBE4B");
tree(106.598327, 195.700000, 1.936218, "#7CC85A");
tree(115.724741, 195.700000, 1.947065, "#7CC85A");
tree(124.851156, 195.700000, 1.928999, "#7CC85A");
tree(133.977570, 195.700000, 2.007349, "#6DBE4B");
tree(143.103984, 195.700000, 2.116823, "#6DBE4B");
tree(152.230398, 195.700000, 2.020332, "#7CC85A");
tree(161.356813, 195.700000, 2.112260, "#7CC85A");
tree(203.903832, 195.700000, 1.961901, "#6DBE4B");
tree(213.030246, 195.700000, 2.215313, "#7CC85A");
tree(222.156661, 195.700000, 2.373854, "#7CC85A");
layer("건축물");
R(62.230230, 177.750000, 16.354211, 19.250000, "#D93F87");
R(62.230230, 158.500000, 16.354211, 19.250000, "#D93F87");
R(171.258306, 177.750000, 25.228590, 19.250000, "#6B2C91");
R(171.258306, 158.500000, 25.228590, 19.250000, "#6B2C91");
R(171.258306, 139.250000, 25.228590, 19.250000, "#6B2C91");
R(231.857632, 177.750000, 30.426440, 19.250000, "#1D2F5C");
R(231.857632, 158.500000, 30.426440, 19.250000, "#1D2F5C");
R(231.857632, 139.250000, 30.426440, 19.250000, "#1D2F5C");
R(231.857632, 120.000000, 30.426440, 19.250000, "#1D2F5C");
R(277.243737, 177.750000, 15.213220, 19.250000, "#6B2C91");
R(277.370514, 151.281250, 15.213220, 19.250000, "#6B2C91");
R(277.370514, 124.812500, 15.213220, 19.250000, "#6B2C91");
GR(311.346705, 182.562500, 10.142147, 14.437500, "#F08A5D", "#F7CF6E");
GR(311.346705, 168.125000, 10.142147, 14.437500, "#F08A5D", "#F7CF6E");
GR(311.346705, 153.687500, 10.142147, 14.437500, "#F08A5D", "#F7CF6E");
GR(311.346705, 139.250000, 10.142147, 14.437500, "#F08A5D", "#F7CF6E");
GR(311.346705, 124.812500, 10.142147, 14.437500, "#F08A5D", "#F7CF6E");
R(59.567917, 153.377961, 21.678838, 5.122039, "#5F656D");
R(301.981683, 151.281250, 9.365023, 7.066285, "#5F656D");
layer("동선");
P([[50.125411, 195.100000], [349.874589, 195.100000]], false, null, "#E0393E", 0.9, [2.8, 2.0]);
P([[56.567917, 155.938980], [84.246755, 155.938980]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(56.567917, 155.938980); dot(84.246755, 155.938980);
P([[298.981683, 154.814392], [314.346705, 154.814392]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(298.981683, 154.814392); dot(314.346705, 154.814392);
layer("라벨");
P([[64.830230, 195.100000], [64.830230, 161.700000]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(64.830230, 195.100000); dot(64.830230, 161.700000);
var r_ = labelIn(66.430230, 78.584441, 158.500000, 194.400000, "\ud734\uac8c\uacf5\uac04", "#ffffff", 16); if (r_ == "") { ABOVE.push(["\ud734\uac8c\uacf5\uac04", 62.230230, 78.584441, 158.500000]); }
P([[173.858306, 195.100000], [173.858306, 142.450000]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(173.858306, 195.100000); dot(173.858306, 142.450000);
var r_ = labelIn(175.458306, 196.486895, 139.250000, 194.400000, "\uacf5\ubc29\u00b7\uc804\uc2dc\ub3d9", "#ffffff", 16); if (r_ == "") { ABOVE.push(["\uacf5\ubc29\u00b7\uc804\uc2dc\ub3d9", 171.258306, 196.486895, 139.250000]); }
P([[234.457632, 195.100000], [234.457632, 123.200000]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(234.457632, 195.100000); dot(234.457632, 123.200000);
var r_ = labelIn(236.057632, 262.284071, 120.000000, 194.400000, "\uc2e4\ub0b4\uccb4\ud5d8\uad00", "#ffffff", 16); if (r_ == "") { ABOVE.push(["\uc2e4\ub0b4\uccb4\ud5d8\uad00", 231.857632, 262.284071, 120.000000]); }
P([[279.843737, 195.100000], [279.843737, 180.950000]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(279.843737, 195.100000); dot(279.843737, 180.950000);
var r_ = labelIn(281.443737, 292.456957, 177.750000, 194.400000, "\uc81c\uc791\ub3d9", "#ffffff", 16); if (r_ == "") { ABOVE.push(["\uc81c\uc791\ub3d9", 277.243737, 292.583734, 124.812500]); }
P([[313.577978, 195.100000], [313.577978, 128.012500]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(313.577978, 195.100000); dot(313.577978, 128.012500);
var r_ = labelIn(311.346705, 321.488852, 124.812500, 194.400000, "\uac70\uc8fc\ub3d9", "#ffffff", 16); if (r_ == "") { ABOVE.push(["\uac70\uc8fc\ub3d9", 311.346705, 321.488852, 124.812500]); }

for (var i = 0; i < ABOVE.length; i++) {
  var q = ABOVE[i]; var cx = (q[1] + q[2]) / 2; var yt = q[3];
  P([[q[1] + 0.4, yt - 1.4], [q[1] + 0.4, yt - 2.6], [q[2] - 0.4, yt - 2.6], [q[2] - 0.4, yt - 1.4]], false, null, "#333333", 0.6);
  T(cx, yt - 5.6, q[0], 12, "Pretendard-ExtraBold", "#222222", "c");
}
P([[277.243737, 114.412500], [277.243737, 113.012500], [321.488852, 113.012500], [321.488852, 114.412500]], false, null, "#222222", 0.7);
T(299.366295, 109.212500, "\ub808\uc9c0\ub358\uc2dc", 13, "Pretendard-ExtraBold", "#222222", "c");
T(124.350878, 181.500000, "\uc57c\uc678\uccb4\ud5d8\uad00", 12, "Pretendard-ExtraBold", "#9a9a9a", "c", 0, 30);
T(214.534203, 181.500000, "\uc911\uc559 \ub0a8\ubd81 \uc778\ub3c4", 12, "Pretendard-ExtraBold", "#9a9a9a", "c", 0, 30);
P([[301.584889, 197.600000], [301.584889, 199.200000]], false, null, "#555555", 0.6); T(301.584889, 201.600000, "\ub808\uc9c0\ub358\uc2dc \ub9c8\ub2f9", 10.5, "Pretendard-Bold", "#3a3a3a", "c");
layer("사람");
person(122.550878, 195.700000, 5.668433, "#4a4a4a", 0.576255);
person(126.150878, 195.700000, 5.237266, "#5a5a5a", -0.110391);
person(212.734203, 195.700000, 5.315404, "#4a4a4a", 0.170914);
person(216.334203, 195.700000, 5.648206, "#5a5a5a", -0.296944);
person(299.784889, 195.700000, 5.656964, "#5a5a5a", -0.027602);
person(303.384889, 195.700000, 5.638196, "#4a4a4a", 0.164368);
layer("방위");
T(10, 193.000000, "W", 20, "Pretendard-Light", "#8a8a8a", "c");
T(390.000000, 193.000000, "E", 20, "Pretendard-Light", "#8a8a8a", "c");
P([[17.0, 194.0], [47.12541096232547, 194.0], [47.12541096232547, 194.0], [48.04385120000168, 193.8173108780271], [48.82246723717318, 193.2970562748477], [49.34272184035255, 192.5184402376762], [49.525410962325466, 191.6], [49.34272184035255, 190.6815597623238], [48.82246723717318, 189.90294372515228], [48.04385120000168, 189.3826891219729], [47.12541096232547, 189.2], [30.55643493304646, 189.2]], false, null, "#1F4E5F", 1.5);
P([[27.956435, 189.200000], [30.556435, 187.800000], [30.556435, 190.600000]], true, "#1F4E5F", null);
P([[383.0, 194.0], [352.87458903767447, 194.0], [352.87458903767447, 194.0], [351.95614879999823, 193.8173108780271], [351.17753276282673, 193.2970562748477], [350.6572781596474, 192.5184402376762], [350.4745890376745, 191.6], [350.6572781596474, 190.6815597623238], [351.17753276282673, 189.90294372515228], [351.95614879999823, 189.3826891219729], [352.87458903767447, 189.2], [369.4435650669535, 189.2]], false, null, "#1F4E5F", 1.5);
P([[372.043565, 189.200000], [369.443565, 187.800000], [369.443565, 190.600000]], true, "#1F4E5F", null);
P([[50.125411, 104.350000], [50.125411, 201.000000]], false, null, "#A0237A", 0.6, [2.0, 1.6]);
E(50.125411, 100.750000, 3.3, 3.3, "#A0237A", "#ffffff", 0.6); T(50.125411, 100.850000, "B", 11, "Pretendard-Bold", "#ffffff", "c");
P([[349.874589, 104.350000], [349.874589, 201.000000]], false, null, "#A0237A", 0.6, [2.0, 1.6]);
E(349.874589, 100.750000, 3.3, 3.3, "#A0237A", "#ffffff", 0.6); T(349.874589, 100.850000, "B\u2032", 11, "Pretendard-Bold", "#ffffff", "c");
layer("범례");
var lx = 12;
R(lx, 217.6, 4.2, 3.4, "#D93F87");
var tl = T(lx + 5.4, 219.3, "\uadfc\ub9b0\uc0dd\ud65c\u00b7\ucee4\ubba4\ub2c8\ud2f0", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
R(lx, 217.6, 4.2, 3.4, "#6B2C91");
var tl = T(lx + 5.4, 219.3, "\ucc3d\uc791\u00b7\uacf5\ubc29", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
R(lx, 217.6, 4.2, 3.4, "#1D2F5C");
var tl = T(lx + 5.4, 219.3, "\uccb4\ud5d8\u00b7\uad50\ub958", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
GR(lx, 217.6, 4.2, 3.4, "#F08A5D", "#F7CF6E");
var tl = T(lx + 5.4, 219.3, "\uc8fc\uac70", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
R(lx, 217.6, 4.2, 3.4, "#5F656D");
var tl = T(lx + 5.4, 219.3, "\ube0c\ub9ac\uc9c0\u00b7\uce90\ub178\ud53c", 10, "Pretendard-Medium", "#333333", "l"); lx += 5.4 + W(tl) + 5;
P([[lx, 219.3], [lx + 7, 219.3]], false, null, "#E0393E", 0.9, [2.8, 2.0]); dot(lx + 7, 219.3); var tl = T(lx + 9.5, 219.3, "\ubcf4\ud589 \ub3d9\uc120 \u00b7 \uc218\uc9c1 \ub3d9\uc120", 10, "Pretendard-Medium", "#333333", "l");
T(388.000000, 219.3, "\uc218\uc9c1 4.7\ubc30 \uacfc\uc7a5 \u00b7 \uc704 3\uce78\uc740 \ub77c\uc774\ub178 \ub2e8\uba74 \ud22c\uc2dc(\ucd5c\uc885 \ubaa8\ub378)", 10, "Pretendard-Regular", "#777777", "r");

var o = new ExportOptionsPNG24(); o.artBoardClipping = true; o.horizontalScale = 333.333; o.verticalScale = 333.333; o.antiAliasing = true; o.transparency = false;
doc.exportFile(new File("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/diagrams/D7_\ub2e8\uba74\uc870\ub2dd_\ub3d9\uc11c.png"), ExportType.PNG24, o);
doc.saveAs(new File("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/diagrams/D7_\ub2e8\uba74\uc870\ub2dd_\ub3d9\uc11c.ai"), new IllustratorSaveOptions());
var po = new PDFSaveOptions(); po.preserveEditability = false; po.compatibility = PDFCompatibility.ACROBAT7;
doc.saveAs(new File("C:/Users/OFFICE/Desktop/9_\ub3c4\uc2dc/work/20261011_masterplan_rough/diagrams/D7_\ub2e8\uba74\uc870\ub2dd_\ub3d9\uc11c.pdf"), po);
doc.close(SaveOptions.DONOTSAVECHANGES);
"saved " + "D7_\ub2e8\uba74\uc870\ub2dd_\ub3d9\uc11c";