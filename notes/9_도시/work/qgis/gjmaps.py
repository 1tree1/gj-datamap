# -*- coding: utf-8 -*-
"""QGIS 안에서 쓰는 A3 지도 출력 도우미.

사용 (QGIS 파이썬 콘솔 / MCP execute_code):
    import sys, importlib; sys.path.insert(0, r"C:\\Users\\User\\Desktop\\9_도시\\work\\qgis")
    import gjmaps; importlib.reload(gjmaps); from gjmaps import *

전제: 프로젝트에 MAP 그룹(AOI로 클립한 메모리 레이어)과 'AOI 분석범위(v2)' 레이어가 있다.
출력: work/maps/{fname}.pdf (A3 가로, 벡터, 300dpi)
"""
import os
from qgis.core import *
from qgis.utils import iface
from qgis.PyQt.QtGui import QColor, QFont

OUT = r"C:\Users\User\Desktop\9_도시\work\maps"
BLACK = "0,0,0"
BASE_ON = ("MAP_bld", "MAP_road_poly", "MAP_river", "MAP_bridge", "MAP_island",
           "MAP_field", "MAP_parking", "MAP_playground")
BASE_OFF = ("MAP_road_cl", "MAP_sidewalk", "MAP_wall", "MAP_uproad", "MAP_uproad_unbuilt")

SRC_NGII = "국토지리정보원 연속수치지형도 1:5,000 (2024, T2) · 좌표계 EPSG:5187 · 범위: 성건동 북부 AOI v2 (99.5 ha)"
SRC_UPIS = ("국토교통부 국가공간정보포털 (연속주제)국토계획/교통시설 LSMD_CONT_UQ161 경북 2026.08 (T1, EPSG:5174→5187)"
            " + 국토지리정보원 연속수치지형도 1:5,000 (T2) · 범위: 성건동 북부 AOI v2 (99.5 ha)")

GRADES = [("광로1류", "74,0,10", "광로1류 (70m↑)"), ("광로2류", "90,0,12", "광로2류 (50~70m)"),
          ("광로3류", "103,0,13", "광로3류 (40~50m)"), ("대로1류", "128,0,20", "대로1류 (35~40m)"),
          ("대로2류", "165,15,21", "대로2류 (30~35m)"), ("대로3류", "203,24,29", "대로3류 (25~30m)"),
          ("중로1류", "241,105,19", "중로1류 (20~25m)"), ("중로2류", "253,141,60", "중로2류 (15~20m)"),
          ("중로3류", "253,174,107", "중로3류 (12~15m)"), ("소로1류", "254,217,142", "소로1류 (10~12m)"),
          ("소로2류", "254,236,190", "소로2류 (8~10m)"), ("소로3류", "210,210,210", "소로3류 (8m 미만)"),
          ("미분류", "255,255,255", "도로 (등급 미기재)"), ("미상", "255,255,255", "폭 미상")]
FUNC = [("주간선도로", "8,48,107", "주간선도로"), ("보조간선도로", "33,113,181", "보조간선도로"),
        ("집산도로", "107,174,214", "집산도로"), ("국지도로", "198,219,239", "국지도로")]


def prj():
    return QgsProject.instance()


def L(name):
    return prj().mapLayersByName(name)[0]


def map_layers():
    return [n.layer() for n in prj().layerTreeRoot().findGroup("MAP").findLayers()]


def reset_base():
    """MAP 그룹 전체를 '검은 가는 외곽선·무채움'으로 되돌리고 기본 가시성으로."""
    root = prj().layerTreeRoot()
    root.findGroup("MAP").setItemVisibilityChecked(True)
    for l in map_layers():
        gt = l.geometryType()
        if gt == QgsWkbTypes.PolygonGeometry:
            sym = QgsFillSymbol.createSimple({"color": "0,0,0,0", "outline_color": BLACK, "outline_width": "0.12"})
        elif gt == QgsWkbTypes.LineGeometry:
            sym = QgsLineSymbol.createSimple({"color": BLACK, "width": "0.12"})
        else:
            sym = QgsMarkerSymbol.createSimple({"color": "0,0,0,0", "outline_color": "0,0,0,0", "size": "0"})
        l.setRenderer(QgsSingleSymbolRenderer(sym)); l.setLabelsEnabled(False); l.triggerRepaint()
    L("AOI 분석범위(v2)").setRenderer(QgsSingleSymbolRenderer(
        QgsFillSymbol.createSimple({"color": "0,0,0,0", "outline_color": BLACK, "outline_width": "0.6"})))
    for k in BASE_OFF:
        for l in prj().mapLayersByName(k): root.findLayer(l.id()).setItemVisibilityChecked(False)
    for k in BASE_ON:
        for l in prj().mapLayersByName(k): root.findLayer(l.id()).setItemVisibilityChecked(True)


def show(name, on=True):
    prj().layerTreeRoot().findLayer(L(name).id()).setItemVisibilityChecked(on)


def categorized(layer, field, cats, geom="fill", line_w="0.5", size="3", outline="60,60,60"):
    """(값, 'r,g,b', 라벨) 목록으로 범주 렌더러. 데이터에 없는 값은 범례에서 뺀다."""
    have = {str(f[field]) for f in layer.getFeatures()}
    items = []
    for val, color, label in cats:
        if val not in have:
            continue
        if geom == "fill":
            s = QgsFillSymbol.createSimple({"color": color, "outline_color": outline, "outline_width": "0.15"})
        elif geom == "line":
            s = QgsLineSymbol.createSimple({"color": color, "width": line_w})
        else:
            s = QgsMarkerSymbol.createSimple({"color": color, "outline_color": "0,0,0", "outline_width": "0.15",
                                              "size": size, "name": "circle"})
        items.append(QgsRendererCategory(val, s, label))
    layer.setRenderer(QgsCategorizedSymbolRenderer(field, items)); layer.triggerRepaint()


def single_labeled(layer, symbol, label):
    """단일 심볼이지만 범례 라벨을 지정하고 싶을 때 (상수 표현식 범주 1개)."""
    layer.setRenderer(QgsCategorizedSymbolRenderer("'x'", [QgsRendererCategory("x", symbol, label)]))
    layer.triggerRepaint()


def hatch_symbol(color="200,0,0"):
    s = QgsFillSymbol.createSimple({"outline_color": color, "outline_width": "0.3", "color": "0,0,0,0"})
    pat = QgsLinePatternFillSymbolLayer(); pat.setLineAngle(45); pat.setDistance(1.2); pat.setLineWidth(0.3)
    pat.setColor(QColor(*[int(c) for c in color.split(",")])); s.appendSymbolLayer(pat)
    return s


def labels(layer, field, size=6):
    st = QgsPalLayerSettings(); st.fieldName = field; st.placement = QgsPalLayerSettings.Horizontal
    tf = QgsTextFormat(); tf.setFont(QFont("맑은 고딕")); tf.setSize(size); tf.setColor(QColor(0, 0, 0))
    buf = QgsTextBufferSettings(); buf.setEnabled(True); buf.setSize(0.6); buf.setColor(QColor(255, 255, 255))
    tf.setBuffer(buf); st.setFormat(tf)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(st)); layer.setLabelsEnabled(True)


def export(fname, title, subtitle, legend_layers, source=SRC_NGII, pdf=True):
    """A3 가로 레이아웃을 만들어 PDF(기본) 또는 PNG로 저장. 반환값 0 = 성공."""
    p = prj(); root = p.layerTreeRoot(); mgr = p.layoutManager()
    for old in mgr.printLayouts():
        if old.name() == "A3_export":
            mgr.removeLayout(old)
    lay = QgsPrintLayout(p); lay.initializeDefaults(); lay.setName("A3_export")
    lay.pageCollection().page(0).setPageSize("A3", QgsLayoutItemPage.Landscape); mgr.addLayout(lay)

    m = QgsLayoutItemMap(lay); lay.addLayoutItem(m)
    m.attemptMove(QgsLayoutPoint(8, 20, QgsUnitTypes.LayoutMillimeters))
    m.attemptResize(QgsLayoutSize(404, 260, QgsUnitTypes.LayoutMillimeters))
    a = L("AOI 분석범위(v2)")
    ext = iface.mapCanvas().mapSettings().layerExtentToOutputExtent(a, a.extent()); ext.grow(40)
    layers = [l for l in root.checkedLayers() if l.name().startswith("MAP_") or l.name().startswith("AOI")]
    m.setCrs(p.crs()); m.setLayers(layers); m.zoomToExtent(ext)
    m.setFrameEnabled(True); m.setFrameStrokeWidth(QgsLayoutMeasurement(0.3)); m.setBackgroundColor(QColor(255, 255, 255))

    def label(text, x, y, w, h, size, bold=False):
        t = QgsLayoutItemLabel(lay); lay.addLayoutItem(t); t.setText(text)
        f = QFont("맑은 고딕", size); f.setBold(bold); t.setFont(f)
        t.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
        t.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    label(title, 8, 5, 300, 9, 18, True); label(subtitle, 8, 13, 400, 6, 9)

    lg = QgsLayoutItemLegend(lay); lay.addLayoutItem(lg); lg.setLinkedMap(m); lg.setAutoUpdateModel(False)
    lg.setTitle("범례"); lg.model().rootGroup().clear()
    for l in legend_layers:
        n = lg.model().rootGroup().addLayer(l); QgsLegendRenderer.setNodeLegendStyle(n, QgsLegendStyle.Hidden)
    for st, sz in [(QgsLegendStyle.Title, 11), (QgsLegendStyle.Subgroup, 9), (QgsLegendStyle.SymbolLabel, 8)]:
        f = QFont("맑은 고딕", sz); f.setBold(st == QgsLegendStyle.Title); lg.setStyleFont(st, f)
    lg.setSymbolWidth(7); lg.setSymbolHeight(3.5); lg.setBackgroundEnabled(True)
    lg.setBackgroundColor(QColor(255, 255, 255, 235)); lg.setFrameEnabled(True); lg.setFrameStrokeWidth(QgsLayoutMeasurement(0.2))
    lg.setResizeToContents(True); lg.setReferencePoint(QgsLayoutItem.UpperRight)
    lg.attemptMove(QgsLayoutPoint(410, 22, QgsUnitTypes.LayoutMillimeters))   # 삼각형 AOI의 빈 우상단

    sb = QgsLayoutItemScaleBar(lay); lay.addLayoutItem(sb); sb.setLinkedMap(m); sb.setStyle("Single Box")
    sb.setUnits(QgsUnitTypes.DistanceMeters); sb.setUnitsPerSegment(100); sb.setNumberOfSegments(4)
    sb.setNumberOfSegmentsLeft(0); sb.setUnitLabel("m"); sb.setFont(QFont("맑은 고딕", 8)); sb.setHeight(2)
    sb.setBackgroundEnabled(True); sb.setBackgroundColor(QColor(255, 255, 255, 235))
    sb.attemptMove(QgsLayoutPoint(12, 270, QgsUnitTypes.LayoutMillimeters))
    label("자료: " + source, 8, 283, 400, 5, 7)

    ex = QgsLayoutExporter(lay)
    os.makedirs(OUT, exist_ok=True)
    if pdf:
        s = QgsLayoutExporter.PdfExportSettings(); s.dpi = 300; s.rasterizeWholeImage = False
        return ex.exportToPdf(os.path.join(OUT, fname + ".pdf"), s)
    s = QgsLayoutExporter.ImageExportSettings(); s.dpi = 300
    return ex.exportToImage(os.path.join(OUT, fname + ".png"), s)


def add_legend(lay, m, legend_layers, ref_point, x, y, title="범례"):
    lg = QgsLayoutItemLegend(lay); lay.addLayoutItem(lg); lg.setLinkedMap(m); lg.setAutoUpdateModel(False)
    lg.setTitle(title); lg.model().rootGroup().clear()
    for l in legend_layers:
        n = lg.model().rootGroup().addLayer(l); QgsLegendRenderer.setNodeLegendStyle(n, QgsLegendStyle.Hidden)
    for st, sz in [(QgsLegendStyle.Title, 11), (QgsLegendStyle.Subgroup, 9), (QgsLegendStyle.SymbolLabel, 8)]:
        f = QFont("맑은 고딕", sz); f.setBold(st == QgsLegendStyle.Title); lg.setStyleFont(st, f)
    lg.setSymbolWidth(7); lg.setSymbolHeight(3.5); lg.setBackgroundEnabled(True)
    lg.setBackgroundColor(QColor(255, 255, 255, 235)); lg.setFrameEnabled(True); lg.setFrameStrokeWidth(QgsLayoutMeasurement(0.2))
    lg.setResizeToContents(True); lg.setReferencePoint(ref_point)
    lg.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    return lg


def export_a3p(fname, center_xy, scale, layers, scalebar=True, north=True, footnote="", margin=10, pdf=True,
               legend_layers=None, page=(297, 420)):
    """A3 세로. 지도 중심(center_xy, 프로젝트 CRS)·축척 고정. 여백 margin mm.
    layers: 지도에 넣을 레이어 목록(순서 = 레이어 패널 순서로 그림). 반환 0 = 성공."""
    p = prj(); mgr = p.layoutManager()
    for old in mgr.printLayouts():
        if old.name() == "A3P_export":
            mgr.removeLayout(old)
    lay = QgsPrintLayout(p); lay.initializeDefaults(); lay.setName("A3P_export")
    lay.pageCollection().page(0).setPageSize(QgsLayoutSize(page[0], page[1], QgsUnitTypes.LayoutMillimeters)); mgr.addLayout(lay)
    W, H = page[0] - 2 * margin, page[1] - 2 * margin - (6 if footnote else 0)
    m = QgsLayoutItemMap(lay); lay.addLayoutItem(m)
    m.attemptMove(QgsLayoutPoint(margin, margin, QgsUnitTypes.LayoutMillimeters))
    m.attemptResize(QgsLayoutSize(W, H, QgsUnitTypes.LayoutMillimeters))
    m.setCrs(p.crs()); m.setLayers(layers)
    cx, cy = center_xy
    hw, hh = W / 1000.0 * scale / 2, H / 1000.0 * scale / 2   # mm → m
    m.setExtent(QgsRectangle(cx - hw, cy - hh, cx + hw, cy + hh)); m.setScale(scale)
    m.setFrameEnabled(True); m.setFrameStrokeWidth(QgsLayoutMeasurement(0.3)); m.setBackgroundColor(QColor(255, 255, 255))
    if scalebar:
        sb = QgsLayoutItemScaleBar(lay); lay.addLayoutItem(sb); sb.setLinkedMap(m); sb.setStyle("Single Box")
        sb.setUnits(QgsUnitTypes.DistanceMeters); sb.setUnitsPerSegment(100); sb.setNumberOfSegments(5)
        sb.setNumberOfSegmentsLeft(0); sb.setUnitLabel("m"); sb.setFont(QFont("맑은 고딕", 8)); sb.setHeight(2)
        sb.setBackgroundEnabled(True); sb.setBackgroundColor(QColor(255, 255, 255, 235))
        sb.attemptMove(QgsLayoutPoint(margin + 4, margin + H - 12, QgsUnitTypes.LayoutMillimeters))
    if north:
        na = QgsLayoutItemPicture(lay); lay.addLayoutItem(na)
        na.setPicturePath(":/images/north_arrows/layout_default_north_arrow.svg")
        na.setLinkedMap(m); na.setNorthMode(QgsLayoutItemPicture.GridNorth)
        na.attemptResize(QgsLayoutSize(12, 16, QgsUnitTypes.LayoutMillimeters))
        na.attemptMove(QgsLayoutPoint(margin + W - 18, margin + 5, QgsUnitTypes.LayoutMillimeters))
        na.setBackgroundEnabled(True); na.setBackgroundColor(QColor(255, 255, 255, 235))
    if legend_layers:
        add_legend(lay, m, legend_layers, QgsLayoutItem.LowerRight, margin + W - 4, margin + H - 4)
    if footnote:
        t = QgsLayoutItemLabel(lay); lay.addLayoutItem(t); t.setText(footnote); t.setFont(QFont("맑은 고딕", 7))
        t.attemptMove(QgsLayoutPoint(margin, margin + H + 1.5, QgsUnitTypes.LayoutMillimeters))
        t.attemptResize(QgsLayoutSize(W, 5, QgsUnitTypes.LayoutMillimeters))
    ex = QgsLayoutExporter(lay); os.makedirs(OUT, exist_ok=True)
    if pdf:
        s = QgsLayoutExporter.PdfExportSettings(); s.dpi = 300; s.rasterizeWholeImage = False
        return ex.exportToPdf(os.path.join(OUT, fname + ".pdf"), s)
    s = QgsLayoutExporter.ImageExportSettings(); s.dpi = 300
    return ex.exportToImage(os.path.join(OUT, fname + ".png"), s)
