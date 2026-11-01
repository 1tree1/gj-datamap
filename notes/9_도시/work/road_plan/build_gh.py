# Rhino 8 (CPython) 에서 실행: GH 캔버스에 진입점·동서연결 시각화 정의를 만든다.
import System, Grasshopper as gh
from System.Drawing import Color, PointF

# 사용자가 열어 둔 GH 문서를 건드리지 않도록 새 문서를 만들어 활성화한다. 내가 만든 이전 정의(ProjectName 표식)는 닫는다.
MARK = 'mode (0=v2모형좌표 1=국소m)'   # 내 정의에만 있는 슬라이더 이름 = 문서 표식
for _d in list(gh.Instances.DocumentServer):
    mine = any(getattr(o, 'NickName', '') == MARK for o in _d.Objects) or ((_d.FilePath is None) and _d.ObjectCount in (67, 106))
    if mine:
        gh.Instances.DocumentServer.RemoveDocument(_d)
doc = gh.Kernel.GH_Document()
gh.Instances.DocumentServer.AddDocument(doc)
gh.Instances.ActiveCanvas.Document = doc
SRV = gh.Instances.ComponentServer

def emit(g): return SRV.EmitObject(System.Guid(g))
def setp(o, n, v): o.GetType().GetProperty(n).SetValue(o, v)
def getp(o, n): return o.GetType().GetProperty(n).GetValue(o)
def place(o, x, y):
    o.CreateAttributes(); o.Attributes.Pivot = PointF(float(x), float(y)); doc.AddObject(o, False); return o

def mkparam(T, n):
    BF = System.Reflection.BindingFlags
    flags = BF.Instance | BF.Public | BF.NonPublic
    for c in T.GetConstructors(flags):
        ps = c.GetParameters()
        if len(ps) == 1 and ps[0].ParameterType.Name == 'String':
            p = c.Invoke(System.Array[System.Object]([n])); break
    else:
        p = T.GetConstructor(flags, None, System.Type.EmptyTypes, None).Invoke(None)
    setp(p, 'NickName', n); setp(p, 'Name', n)
    try: setp(p, 'VariableName', n)
    except Exception: pass
    return p

# ---------- 스크립트 ----------
src = open(r'C:/Users/User/Desktop/9_도시/work/road_plan/gh_script.py', encoding='utf8').read()
py = place(emit('719467e6-7cf5-4848-99b0-c5dd57e5442c'), 700, 300)
py.SetSource(src)
ins = ['day', 'hour', 'wid', 'mode']
outs = ['site', 'bg', 'lk_free', 'lk_slow', 'lk_jam', 'lk_nodata', 'lk_insite', 'cand_par', 'cand_oth', 'ent_main', 'ent_sub', 'stops', 'turns',
        'ew_alt', 'ew_A', 'ew_B', 'plan_A', 'plan_B', 'plan_spine', 'plan_R2', 'tag_pl', 'tag_txt', 'report',
        'blk_civic', 'blk_park', 'blk_house', 'blk_retail', 'blk_culture', 'blk_public', 'blk_plaza', 'rd_plan', 'grn', 'ped_plan', 'cw_new', 'stop_new', 'blk_tag_pl', 'blk_tag_txt',
        'plaza', 'station_new']
# 기본 x,y 이름 변경 + 추가
for i, n in enumerate(ins):
    if i < py.Params.Input.Count:
        p = py.Params.Input[i]; setp(p, 'NickName', n); setp(p, 'Name', n); setp(p, 'VariableName', n)
    else:
        T = py.Params.Input[0].GetType()
        p = mkparam(T, n)
        py.Params.RegisterInputParam(p)
# 출력: 'out'은 두고 나머지 교체
T = py.Params.Output[1].GetType()
first = py.Params.Output[1]; setp(first, 'NickName', outs[0]); setp(first, 'Name', outs[0]); setp(first, 'VariableName', outs[0])
for n in outs[1:]:
    p = mkparam(T, n)
    py.Params.RegisterOutputParam(p)
py.Params.OnParametersChanged()
outp = {p.NickName: p for p in py.Params.Output}
inp = {p.NickName: p for p in py.Params.Input}
print('inputs', list(inp), 'outputs', len(outp))

# ---------- 슬라이더 ----------
def slider(name, mn, mx, val, dec, y):
    s = place(emit('57da07bd-ecab-415d-9d86-af36d7073abc'), 300, y)
    s.NickName = name
    sl = s.Slider; sl.Minimum = System.Decimal(mn); sl.Maximum = System.Decimal(mx); sl.DecimalPlaces = dec; sl.Value = System.Decimal(val)
    return s
s_day = slider('day', 0, 1, 0, 0, 200)
s_hour = slider('hour', 6, 22, 18, 0, 260)
s_wid = slider('wid', 6, 24, 12, 0, 320)
s_tag = slider('tag_size', 2, 40, 5, 0, 380)
s_mode = slider('mode (0=v2모형좌표 1=국소m)', 0, 1, 0, 0, 440)
inp['day'].AddSource(s_day); inp['hour'].AddSource(s_hour); inp['wid'].AddSource(s_wid); inp['mode'].AddSource(s_mode)

# ---------- 색·미리보기 ----------
def swatch(rgb, x, y):
    sw = place(emit('9c53bac0-ba66-40bd-8154-ce9829b9db1a'), x, y)
    setp(sw, 'SwatchColour', Color.FromArgb(*rgb)); return sw

def mat_preview(out_name, rgb, x, y, transp=0.0):
    sw = swatch(rgb, x, y)
    mt = place(emit('76975309-75a6-446a-afed-f8653720a9f2'), x + 90, y)
    mt.Params.Input[0].AddSource(sw); mt.Params.Input[2].AddSource(sw)
    pv = place(emit('537b0419-bbc2-4ff4-bf08-afe526367b2c'), x + 230, y)
    pv.Params.Input[0].AddSource(outp[out_name]); pv.Params.Input[1].AddSource(mt.Params.Output[0])
    return pv

def curve_preview(out_name, rgb, x, y):
    sw = swatch(rgb, x, y)
    pv = place(emit('eeb8f5d3-2c5e-46bd-a368-10f0f9576fe9'), x + 230, y)
    pv.Params.Input[0].AddSource(outp[out_name]); pv.Params.Input[2].AddSource(sw)
    return pv

spec = [
    ('site', (30, 90, 230)), ('lk_free', (60, 170, 90)), ('lk_slow', (240, 170, 30)), ('lk_jam', (215, 50, 50)),
    ('lk_nodata', (165, 165, 165)), ('lk_insite', (150, 100, 200)), ('cand_par', (0, 150, 150)), ('cand_oth', (205, 185, 205)),
    ('ent_main', (255, 80, 0)), ('ent_sub', (255, 165, 0)), ('stops', (110, 60, 160)), ('turns', (230, 205, 0)),
    ('ew_A', (0, 210, 90)), ('ew_B', (40, 200, 210)), ('plan_A', (0, 110, 60)), ('plan_B', (0, 130, 140)), ('plan_spine', (120, 120, 255)), ('plan_R2', (255, 140, 0)),
    ('blk_civic', (200, 60, 60)), ('blk_park', (110, 110, 110)), ('blk_house', (240, 190, 60)), ('blk_retail', (230, 120, 40)), ('blk_culture', (160, 100, 190)),
    ('blk_public', (60, 150, 200)), ('blk_plaza', (180, 220, 170)), ('rd_plan', (235, 235, 235)), ('grn', (120, 190, 110)), ('ped_plan', (250, 250, 200)),
    ('cw_new', (255, 255, 255)), ('stop_new', (220, 40, 160)), ('plaza', (245, 235, 200)), ('station_new', (90, 40, 110)),
]
y0 = 700
for i, (n, rgb) in enumerate(spec):
    mat_preview(n, rgb, 1100, y0 + i * 60)
curve_preview('bg', (205, 205, 205), 1100, y0 + len(spec) * 60)
curve_preview('ew_alt', (120, 185, 120), 1100, y0 + (len(spec) + 1) * 60)

# ---------- 라벨 / 보고서 ----------
tg = place(emit('5a41528b-12b9-40dc-a3f2-842034d267c4'), 1500, 300)
tg.Params.Input[0].AddSource(outp['tag_pl']); tg.Params.Input[1].AddSource(outp['tag_txt']); tg.Params.Input[2].AddSource(s_tag)
csw = swatch((20, 20, 20), 1300, 300); tg.Params.Input[3].AddSource(csw)
s_tag2 = slider('blk_tag_size', 1, 30, 4, 0, 500)
tg2 = place(emit('5a41528b-12b9-40dc-a3f2-842034d267c4'), 1500, 420)
tg2.Params.Input[0].AddSource(outp['blk_tag_pl']); tg2.Params.Input[1].AddSource(outp['blk_tag_txt']); tg2.Params.Input[2].AddSource(s_tag2)
csw2 = swatch((60, 20, 20), 1300, 420); tg2.Params.Input[3].AddSource(csw2)
pn = place(emit('59e0b89a-e487-49f8-bab8-b5bab16be14c'), 1000, 100)
pn.AddSource(outp['report'])
try:
    pn.Attributes.Bounds = System.Drawing.RectangleF(1000, 100, 760, 320)
except Exception as e:
    print('panel size', e)
doc.NewSolution(True)
print('objects', doc.ObjectCount)
