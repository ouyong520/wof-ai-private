from pathlib import Path
import re, base64, gzip, json, collections, statistics

s=Path('wof_v4_install_once.js').read_text(encoding='utf-8')
m=re.search(r"const __B64='([^']+)'",s)
if not m:
    raise SystemExit('embedded DB base64 not found')
raw=gzip.decompress(base64.b64decode(m.group(1)))
db=json.loads(raw)
fams=db['f']

focus=['T07_F01','T07_F02','T09_F24','T21_F01','T21_F04','T24_F03','T24_F04','T24_F09','T30_F01','T33_F07','T36_F01']

def q(vals,p):
    vals=sorted(vals)
    if not vals:return None
    return vals[min(len(vals)-1,round((len(vals)-1)*p))]

rx=[float(v[3]) for v in fams.values()]
ry=[float(v[4]) for v in fams.values()]
rz=[float(v[5]) for v in fams.values()]

rz_counts=collections.Counter(rz)
large=[k for k,v in fams.items() if float(v[5])>=80]
by_type=collections.defaultdict(lambda:{'count':0,'large_rz':0,'rz':[]})
for k,v in fams.items():
    t=int(v[0]);b=by_type[t];b['count']+=1;b['rz'].append(float(v[5]));b['large_rz']+=float(v[5])>=80

report={
 'family_count':len(fams),
 'radius_summary':{
   'rx':{'min':min(rx),'p25':q(rx,.25),'median':q(rx,.5),'p75':q(rx,.75),'p90':q(rx,.9),'max':max(rx)},
   'ry':{'min':min(ry),'p25':q(ry,.25),'median':q(ry,.5),'p75':q(ry,.75),'p90':q(ry,.9),'max':max(ry)},
   'rz':{'min':min(rz),'p25':q(rz,.25),'median':q(rz,.5),'p75':q(rz,.75),'p90':q(rz,.9),'max':max(rz)},
 },
 'rz_value_counts':[{ 'rz':k,'count':v } for k,v in sorted(rz_counts.items())],
 'large_rz_ge80_count':len(large),
 'large_rz_ge80_fraction':len(large)/len(fams),
 'large_rz_families':large,
 'focus':{},
 'by_type':{}
}
for k in focus:
    v=fams.get(k)
    if v:
        report['focus'][k]={
          'type':v[0],'attack':v[1],'dur90':v[2],'rx':v[3],'ry':v[4],'rz':v[5],
          'tr_keys':sorted(map(int,v[6].keys())) if isinstance(v[6],dict) else [],
          'sw_keys':sorted(map(int,v[7].keys())) if isinstance(v[7],dict) else [],
          'sw':v[7]
        }
for t,b in sorted(by_type.items()):
    report['by_type'][str(t)]={'count':b['count'],'large_rz':b['large_rz'],'rz_min':min(b['rz']),'rz_median':q(b['rz'],.5),'rz_max':max(b['rz'])}

Path('reports').mkdir(exist_ok=True)
Path('reports/db_geometry_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['family_count','radius_summary','large_rz_ge80_count','large_rz_ge80_fraction']},indent=2))
print('focus',json.dumps(report['focus'],ensure_ascii=False)[:8000])
