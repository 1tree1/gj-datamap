import rhino3dm as R, time, collections, sys
t=time.time()
m=R.File3dm.Read(r"C:/Users/OFFICE/Desktop/9_도시/최종콘타모델_v2_획지매스_규제미적용v1b.3dm")
print("read %.0fs"%(time.time()-t), "objects",len(m.Objects),"layers",len(m.Layers), "units", m.Settings.ModelUnitSystem)
names={}
for i,l in enumerate(m.Layers): names[i]=l.FullPath
cnt=collections.Counter()
for o in m.Objects: cnt[(o.Attributes.LayerIndex)]+=1
for i,l in enumerate(m.Layers): print(i,l.FullPath,cnt.get(i,0),l.Color)
