import rhino3dm as R, collections
m=R.File3dm.Read(r"C:/Users/OFFICE/Desktop/9_도시/최종콘타모델_v2_획지매스_TIMESTRATA_수정안v1.3dm")
names={i:l.FullPath for i,l in enumerate(m.Layers)}
cnt=collections.Counter(); bb={}
for o in m.Objects:
    n=names[o.Attributes.LayerIndex]
    if n.startswith("획지매스_"):
        cnt[(n, m.Layers[o.Attributes.LayerIndex].Visible)]+=1
        b=o.Geometry.GetBoundingBox(); k=n.split("::")[0]
        if k not in bb: bb[k]=[b.Min.X,b.Min.Y,b.Min.Z,b.Max.X,b.Max.Y,b.Max.Z]
        else:
            v=bb[k]; v[0]=min(v[0],b.Min.X);v[1]=min(v[1],b.Min.Y);v[2]=min(v[2],b.Min.Z);v[3]=max(v[3],b.Max.X);v[4]=max(v[4],b.Max.Y);v[5]=max(v[5],b.Max.Z)
for k,v in sorted(cnt.items()): print(k,v)
for k,v in bb.items(): print(k,[round(x,1) for x in v])
