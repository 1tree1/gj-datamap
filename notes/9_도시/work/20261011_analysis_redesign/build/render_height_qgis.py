# -*- coding: utf-8 -*-
import os,sys,json
from pathlib import Path
import tempfile,shutil
ROOT_RUNTIME=Path(__file__).parent/'qgis_runtime'/'QGIS 3.32.0'
PROJ_TMP=Path(tempfile.gettempdir())/'codex_qgis_proj_r10';PROJ_TMP.mkdir(exist_ok=True)
shutil.copy2(ROOT_RUNTIME/'share/proj/proj.db',PROJ_TMP/'proj.db')
os.environ['PROJ_LIB']=str(PROJ_TMP);os.environ['PROJ_DATA']=str(PROJ_TMP)
os.environ['QT_QPA_FONTDIR']=r'C:\Windows\Fonts'
from qgis.core import *
from qgis.PyQt.QtGui import QColor,QFont,QFontDatabase
from qgis.PyQt.QtCore import QSize
B=Path(__file__).parent;D=B/'height_map_data';A=B/'assets';M=json.loads((B/'height_map_metadata.json').read_text(encoding='utf8'))
QgsApplication.setPrefixPath(str(ROOT_RUNTIME/'apps/qgis'),True)
app=QgsApplication([],False);app.initQgis()
fontid=QFontDatabase.addApplicationFont(r'C:\Users\OFFICE\AppData\Local\Microsoft\Windows\Fonts\Pretendard-Regular.otf')
print('Loaded font',fontid,QFontDatabase.applicationFontFamilies(fontid))
p=QgsProject.instance();p.setCrs(QgsCoordinateReferenceSystem('EPSG:5187'));assert p.crs().isValid() and p.crs().authid()=='EPSG:5187',p.crs().description()
def load(name,label):
 l=QgsVectorLayer(str(D/(name+'.geojson')),label,'ogr');assert l.isValid(),name;assert l.crs().isValid(),name;p.addMapLayer(l);return l
def fill(l,c,line='255,255,255,0',width='.08',style='solid'):
 l.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({'color':c,'outline_color':line,'outline_width':width,'outline_style':style})))
water=load('water','하천');fill(water,'232,239,243')
roads=load('roads','도로중심선');roads.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({'line_color':'221,225,228','line_width':'.07'})))
boundaryfill=load('boundary','고시구역 바탕');fill(boundaryfill,'249,250,251')
base=load('buildings','건물 층수');focus=load('buildings','동서 150m 분석 건물');focus.setSubsetString('"side150" IN (\'west\',\'east\')')
colors={'1':'190,197,203','2':'137,168,188','3-5':'68,117,148','6+':'24,65,91','unknown':'236,237,238'}
labels={'1':'1층','2':'2층','3-5':'3–5층','6+':'6층 이상','unknown':'층수 미상'}
for l in [base,focus]:
 cats=[]
 for k in M['classes']:
  if M['counts'].get(k,0)==0:continue
  sy=QgsFillSymbol.createSimple({'color':colors[k],'outline_style':'solid','outline_color':'255,255,255','outline_width':'.035','joinstyle':'miter'})
  cats.append(QgsRendererCategory(k,sy,labels[k]))
 l.setRenderer(QgsCategorizedSymbolRenderer('height_class',cats))
base.setOpacity(.27)
band=load('band150','경계 밖 150m 분석 범위');fill(band,'255,255,255,0','138,149,158','.25','dash')
boundary=load('boundary','2026-8 고시구역 경계');fill(boundary,'255,255,255,0','35,93,130','.40')
layers=[boundary,band,focus,base,boundaryfill,roads,water]
root=p.layerTreeRoot();root.setHasCustomLayerOrder(True);root.setCustomLayerOrder(layers)
layout=QgsPrintLayout(p);layout.initializeDefaults();layout.setName('건물 높이 분포 (층수 기준)');p.layoutManager().addLayout(layout)
layout.pageCollection().page(0).setPageSize(QgsLayoutSize(236,148.8))
mp=QgsLayoutItemMap(layout);layout.addLayoutItem(mp);mp.attemptMove(QgsLayoutPoint(0,0));mp.attemptResize(QgsLayoutSize(236,148.8));mp.setCrs(p.crs());mp.setLayers(layers);mp.setKeepLayerSet(True);mp.zoomToExtent(QgsRectangle(*M['extent']));mp.setFrameEnabled(False);mp.setBackgroundColor(QColor('white'))
def label(t,x,y,w,h,size=17,color='#252C32'):
 o=QgsLayoutItemLabel(layout);o.setText(t);o.setFont(QFont('Pretendard',size));o.setFontColor(QColor(color));o.setMargin(0);o.setFrameEnabled(False);o.setBackgroundEnabled(False);layout.addLayoutItem(o);o.attemptMove(QgsLayoutPoint(x,y));o.attemptResize(QgsLayoutSize(w,h));return o
label('N',222,2,12,10,17);label('\u2191',222,12,12,12,21)
# Labels sit within the empty site or outside the data, without opaque boxes.
label('구 경주역\n고시구역',104,70,39,23,15,'#235D82')
sc=QgsLayoutItemScaleBar(layout);sc.setStyle('Single Box');sc.setLinkedMap(mp);sc.applyDefaultSize();sc.setNumberOfSegments(2);sc.setNumberOfSegmentsLeft(0);sc.setUnits(QgsUnitTypes.DistanceMeters);sc.setUnitsPerSegment(100);sc.setUnitLabel('m');sc.setFont(QFont('Pretendard',13));sc.setHeight(1.2);sc.setLineWidth(.12);sc.setBackgroundEnabled(False);sc.setFrameEnabled(False);layout.addLayoutItem(sc);sc.attemptMove(QgsLayoutPoint(182,134))
p.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(QgsRectangle(*M['extent']),p.crs()))
p.setFileName(str(D/'건물층수_슬라이드12.qgz'));assert p.write()
exporter=QgsLayoutExporter(layout);settings=QgsLayoutExporter.ImageExportSettings();settings.dpi=254;settings.imageSize=QSize(2360,1488);settings.cropToContents=False
out=str(A/'height_qgis_revision10.png');code=exporter.exportToImage(out,settings);assert code==QgsLayoutExporter.Success,code
r={'qgisVersion':Qgis.QGIS_VERSION,'exportResult':int(code),'image':out,'project':p.fileName(),'mapExtent':mp.extent().toString(),'classes':labels,'counts':M['counts'],'field':'nmly'}
(B/'qgis_height_export_receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r,ensure_ascii=True))
# Some OSGeo distributions retain Qt/GDAL objects at interpreter exit.
sys.stdout.flush();os._exit(0)
