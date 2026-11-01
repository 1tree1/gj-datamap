import sys, os, json, collections, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'vendor'))
import rhino3dm as r
P = r'C:\Users\OFFICE\Desktop\구경주역_마스터플랜_최종.3dm'
t = time.time()
f = r.File3dm.Read(P)
print('READ', time.time()-t, len(f.Objects), f.Settings.ModelUnitSystem, flush=True)
layers = {l.Index:l for l in f.Layers}
stats = {}
records = []
for o in f.Objects:
    g, a = o.Geometry, o.Attributes
    l = layers[a.LayerIndex]
    bb = g.GetBoundingBox()
    bounds = [bb.Min.X,bb.Min.Y,bb.Min.Z,bb.Max.X,bb.Max.Y,bb.Max.Z]
    us = dict(a.GetUserStrings()) if a.GetUserStrings() else {}
    rec = dict(id=str(a.Id),type=type(g).__name__,layer=l.FullPath,name=a.Name,bb=bounds,us=us,color=list(a.ObjectColor),layer_color=list(l.Color),hidden=l.Visible==False,groups=list(a.GetGroupList()))
    records.append(rec)
    st = stats.setdefault(l.FullPath, {'n':0,'types':collections.Counter(),'min':[float('inf')]*3,'max':[float('-inf')]*3,'samples':[]})
    st['n']+=1;st['types'][rec['type']]+=1
    for k in range(3):st['min'][k]=min(st['min'][k],bounds[k]);st['max'][k]=max(st['max'][k],bounds[k+3])
    if len(st['samples'])<2:st['samples'].append({'name':a.Name,'us':us,'bb':bounds})
out = dict(source=P,unit=str(f.Settings.ModelUnitSystem),tolerance=f.Settings.ModelAbsoluteTolerance,object_count=len(records),layers=stats,records=records)
with open(os.path.join(HERE,'source_inspection.json'),'w',encoding='utf-8') as fp:json.dump(out,fp,ensure_ascii=False,indent=2)
for n,s in stats.items():
    print(n,s['n'],dict(s['types']),'extent',[round(s['max'][k]-s['min'][k],3) for k in range(3)],'z',round(s['min'][2],3),round(s['max'][2],3),flush=True)
    for ss in s['samples']:print(' ',json.dumps(ss,ensure_ascii=False),flush=True)
