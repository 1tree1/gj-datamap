import math, struct, json
from pathlib import Path
R=Path(r'C:\Users\OFFICE\Desktop\9_도시')
D=R/'대지/(B020)연속수치지도_202609132098'
OUT=R/'work/20261010_nexus_front/build'
a=6378137.0; f=1/298.257222101; e2=f*(2-f); ep=e2/(1-e2)
def mer(p):
    return a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-35*e2**3/3072*math.sin(6*p))
def inv(x,y):
    mu=((y-2000000)/0.9996+mer(math.radians(38)))/(a*(1-e2/4-3*e2**2/64-5*e2**3/256))
    ee=(1-math.sqrt(1-e2))/(1+math.sqrt(1-e2))
    p=mu+(3*ee/2-27*ee**3/32)*math.sin(2*mu)+(21*ee**2/16-55*ee**4/32)*math.sin(4*mu)+151*ee**3/96*math.sin(6*mu)+1097*ee**4/512*math.sin(8*mu)
    n=a/math.sqrt(1-e2*math.sin(p)**2); t=math.tan(p)**2; c=ep*math.cos(p)**2; rr=a*(1-e2)/(1-e2*math.sin(p)**2)**1.5; dd=(x-1000000)/(n*0.9996)
    lat=p-n*math.tan(p)/rr*(dd**2/2-(5+3*t+10*c-4*c*c-9*ep)*dd**4/24+(61+90*t+298*c+45*t*t-252*ep-3*c*c)*dd**6/720)
    lon=math.radians(127.5)+(dd-(1+2*t+c)*dd**3/6+(5-2*c+28*t-3*c*c+8*ep+24*t*t)*dd**5/120)/math.cos(p)
    return lon,lat
def project(x,y):
    lon,p=inv(x,y); n=a/math.sqrt(1-e2*math.sin(p)**2);t=math.tan(p)**2;c=ep*math.cos(p)**2;aa=(lon-math.radians(129))*math.cos(p)
    return [round(200000+n*(aa+(1-t+c)*aa**3/6+(5-18*t+t*t+72*c-58*ep)*aa**5/120),3),round(600000+mer(p)-mer(math.radians(38))+n*math.tan(p)*(aa*aa/2+(5-t+9*c+4*c*c)*aa**4/24+(61-58*t+t*t+600*c-330*ep)*aa**6/720),3)]
def records(layer, bb):
    b=(D/(layer+'.shp')).read_bytes(); off=100; out=[]
    while off+8<len(b):
        num,length=struct.unpack_from('>2i',b,off); start=off+8;off=start+length*2
        typ=struct.unpack_from('<i',b,start)[0]
        if typ not in [3,5,13,15]:continue
        xmin,ymin,xmax,ymax=struct.unpack_from('<4d',b,start+4)
        corners=[project(xmin,ymin),project(xmax,ymax)]
        x0=min(c[0]for c in corners);x1=max(c[0]for c in corners);y0=min(c[1]for c in corners);y1=max(c[1]for c in corners)
        if x1<bb[0] or x0>bb[2] or y1<bb[1] or y0>bb[3]:continue
        npart,npoint=struct.unpack_from('<2i',b,start+36)
        parts=list(struct.unpack_from('<'+'i'*npart,b,start+44))+[npoint]
        pstart=start+44+npart*4
        for i in range(npart):
            coords=[project(*struct.unpack_from('<2d',b,pstart+j*16))for j in range(parts[i],parts[i+1])]
            out.append(coords)
    return out
bb=[218050,359150,220850,363100]
data={'buildings':records('N3A_B0010000',bb),'water':records('N3A_E0010001',bb),'bridge':records('N3A_A0063321',[219500,360900,220100,361250])}
(OUT/'spatial.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
print({k:len(v)for k,v in data.items()})
for p in data['bridge']:
    print('bridge bbox',min(x[0]for x in p),min(x[1]for x in p),max(x[0]for x in p),max(x[1]for x in p))
p=json.loads((R/'archive/90_derived/public_profile_20260928.json').read_text(encoding='utf-8'))
def walk(obj):
    if isinstance(obj,dict):
        if obj.get('id')=='s1_neighbors':print(json.dumps(obj,ensure_ascii=False))
        for v in obj.values():walk(v)
    elif isinstance(obj,list):
        for v in obj:walk(v)
walk(p)
