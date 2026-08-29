from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.5" not in s:
    raise SystemExit('expected V4.5 input')

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit(label+' target missing')
    s=s.replace(old,new,1)

# Route runtime logs through a muteable logger. Do this before adding qlog itself.
s=s.replace('console.log(', 'qlog(')

rep("""  const M=_0x515056.HEAPU8;
  const R=_0x515056.HEAPU32[0x2e39e4>>>2]>>>0;""",
"""  let QUIET=false;
  const qlog=(...a)=>{if(!QUIET)self.console.log(...a);};
  const M=_0x515056.HEAPU8;
  const R=_0x515056.HEAPU32[0x2e39e4>>>2]>>>0;""",
'logger')

rep("""function auditFamilies(){
  const out={};
  for(const n of ['P1','P2','P3'])out[n]=Object.entries(AUD[n].byFamily).map(([family,v])=>({family,...v,
    precision:(v.hit+v.falsePositive)?v.hit/(v.hit+v.falsePositive):null,
    confirmed:v.hit+v.falsePositive})).sort((a,b)=>(b.falsePositive-a.falsePositive)||(b.confirmed-a.confirmed)||(b.tested-a.tested));
  return out;
}

  let timer=null,last=null;""",
"""function auditFamilies(){
  const out={};
  for(const n of ['P1','P2','P3'])out[n]=Object.entries(AUD[n].byFamily).map(([family,v])=>({family,...v,
    precision:(v.hit+v.falsePositive)?v.hit/(v.hit+v.falsePositive):null,
    confirmed:v.hit+v.falsePositive})).sort((a,b)=>(b.falsePositive-a.falsePositive)||(b.confirmed-a.confirmed)||(b.tested-a.tested));
  return out;
}
function frozenCopy(x){return JSON.parse(JSON.stringify(x));}
function reportSnapshot(){
  return frozenCopy({at:Date.now(),audit:auditSnapshot(),auditFamilies:auditFamilies(),calibration:calibrationSnapshot()});
}
function reportText(){return JSON.stringify(reportSnapshot(),null,2);}

  let timer=null,last=null;""",
'report helpers')

rep("""    audit(){return auditSnapshot();},
    auditFamilies(){return auditFamilies();},
    calibration(){return calibrationSnapshot();},
    resetCalibration(){return calibrationReset();},
    stop(){if(timer){clearInterval(timer);timer=null;}qlog('⛔ WOF V4关闭');}""",
"""    audit(){return frozenCopy(auditSnapshot());},
    auditFamilies(){return frozenCopy(auditFamilies());},
    calibration(){return frozenCopy(calibrationSnapshot());},
    snapshot(){return reportSnapshot();},
    report(){const t=reportText();self.console.log(t);return t;},
    quiet(on=true){QUIET=!!on;self.console.log(QUIET?'🔇 WOF实时日志已静音，统计继续':'🔊 WOF实时日志已恢复');return QUIET;},
    pause(){if(timer){clearInterval(timer);timer=null;}const r=reportSnapshot();self.console.log('⏸️ WOF观战统计已暂停');return r;},
    resume(){if(!timer){timer=setInterval(tick,CFG.tickMs);tick();}self.console.log('▶️ WOF观战统计已继续');return true;},
    resetCalibration(){return calibrationReset();},
    stop(){if(timer){clearInterval(timer);timer=null;}qlog('⛔ WOF V4关闭');}""",
'API report')

rep("version:'offline-dynamic-spectator-calibrated-v4.5'","version:'offline-dynamic-spectator-calibrated-v4.5.1'",'version')
rep("qlog('✅ WOF V4.5 双层Z几何观战版启动');","qlog('✅ WOF V4.5.1 静态报告观战版启动');",'startup')
rep("qlog('⚠️ 只预测，不控制任何玩家');","qlog('📸 需要固定数据时用 WOFV4.report()；可先 WOFV4.quiet(true) 静音但继续统计');\n  qlog('⚠️ 只预测，不控制任何玩家');",'report hint')

p.write_text(s,encoding='utf-8')
print('patched V4.5.1',len(s))
