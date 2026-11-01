from pathlib import Path
import json
from shapely.geometry import Polygon, LineString, box
B=Path(__file__).parent
meta=json.loads((B/'strategy_metadata.json').read_text(encoding='utf8'))
extent=[-800,-560,880,600]; roi=box(*extent); items=[]
for v in json.loads((B/'strategy_geometry.json').read_text(encoding='utf8'))[0]['items']:
    if len(v['points'])<2: continue
    g=Polygon(v['points']) if v['closed'] and len(v['points'])>=3 else LineString(v['points'])
    if not g.is_valid:g=g.buffer(0)
    if not g.intersects(roi):continue
    g=g.intersection(roi)
    def add(g):
        if g.is_empty:return
        if g.geom_type in ['Polygon','LineString']:
            q=dict(v);q['points']=list(g.exterior.coords if g.geom_type=='Polygon' else g.coords);q['closed']=g.geom_type=='Polygon';items.append(q)
        elif hasattr(g,'geoms'):
            for a in g.geoms:add(a)
    add(g)
zone=Polygon(meta['zone']);regions=[]
for key,lo,hi in [('civic',220,700),('residential',30,220),('exchange',-35,30),('creative',-210,-35),('cultural',-700,-210)]:
    g=zone.intersection(box(-500,lo,500,hi))
    regions.append({'key':key,'points':list(g.exterior.coords),'center':list(g.representative_point().coords)[0]})
meta.update(extent=extent,regions=regions)
(B/'anchor_revision6_metadata.json').write_text(json.dumps(meta,ensure_ascii=False),encoding='utf8')
(B/'anchor_revision6_geometry.json').write_text(json.dumps([{'name':'anchor_base_v6','w':1260,'h':870,'bounds':extent,'items':items}]),encoding='utf8')
print('Prepared',len(items),'map paths and 5 editable planning zones.')
