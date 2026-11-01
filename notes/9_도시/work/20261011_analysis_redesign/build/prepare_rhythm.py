from pathlib import Path
import json,hashlib,sys
B=Path(__file__).parent;ROOT=B.parents[2];src=ROOT/'pipeline/build_gyeongju_reading.py'
sys.path.insert(0,str(B/'rhythm_vendor'))
code=src.read_text(encoding='utf8');env={'__file__':str(src),'__name__':'rhythm_recompute'}
# Execute the original source's data loading and numerical analysis, excluding all plotting.
prefix=code[:code.index('# map14 —')]
exec(compile(prefix,str(src),'exec'),env)
env['HW']={'4713010500'}
part=code[code.index('print("routes ...")'):code.index('fig = plt.figure(figsize=(14, 16)')]
exec(compile(part,str(src),'exec'),env)
live=json.loads((B/'fabric_report_live.json').read_text(encoding='utf8'))['reading']
assert env['OUT']['routes']==live['routes'],(env['OUT']['routes'],live['routes'])
curves=[]
for s,stat in zip(env['series'],live['routes']):
 curves.append({**stat,'distance_m':s['s'].tolist(),'area_m2':s['v'].tolist(),'peak_indices':[int(i) for i in s['peaks']]})
result={'page':'https://1tree1.github.io/gj-datamap/report.html','card':'f_walk','data':'https://1tree1.github.io/gj-datamap/data/fabric_report.json','sourceDate':'2026-09-28','method':{'radius_m':150,'rays':720,'sampling_m':2,'obstacles':'NGII buildings and walls (0.15m buffer)','peaks':'prominence>=max(250m2,8% route median), min distance8m'},'webSummaryExactlyMatched':True,'sourceScriptSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'isovists':[live['isovists'][0],live['isovists'][2]],'routes':curves}
(B/'rhythm_evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print('Saved exact curves; all three route summaries match the current website.')
