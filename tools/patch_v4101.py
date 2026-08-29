from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.10.0" not in s:
    raise SystemExit('expected V4.10.0 input')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,count)

# V4.10.1: V4.10.0 proved internal ATTACK phases exist, but destructively replacing
# the primary Family caused raw coverage regression because every phase switch reset
# the primary trajectory clock/origin. Keep the original 0->nonzero Family trajectory
# intact for the whole active window and add exact internal phases as WATCH-only overlays.
rep(
"""    debounceBridgeMs:350,
    attackTailGuardMs:280,""",
"""    debounceBridgeMs:350,
    phaseOverlayHorizonMs:500,
    attackTailGuardMs:280,""",
'phase overlay cfg')

rep(
"const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0,seq:0,variantBase:null,variantMotion:null,tail:null,phaseFamily:null,phaseFrom:null,phaseAttack:0,phaseSwitches:0}));",
"const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0,seq:0,variantBase:null,variantMotion:null,tail:null,phaseFamily:null,phaseFrom:null,phaseAttack:0,phaseStarted:0,phaseOrigin:null,phaseFace:0,phaseSwitches:0}));",
'phase overlay slot fields')

rep(
"if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.seq=0;s.variantBase=null;s.variantMotion=null;s.tail=null;s.phaseFamily=null;s.phaseFrom=null;s.phaseAttack=0;s.phaseSwitches=0;}",
"if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.seq=0;s.variantBase=null;s.variantMotion=null;s.tail=null;s.phaseFamily=null;s.phaseFrom=null;s.phaseAttack=0;s.phaseStarted=0;s.phaseOrigin=null;s.phaseFace=0;s.phaseSwitches=0;}",
'phase overlay reset type')

rep(
"""      s.phaseFamily=s.locked;s.phaseFrom=null;s.phaseAttack=o.attack;
    }else if(s.prevAttack!==0&&o.attack!==0&&o.attack!==s.prevAttack){
      const exactPhase=DB.a[keyActive(o)]||null;
      if(exactPhase&&exactPhase!==s.locked){
        const from=s.locked||null,attackFrom=s.prevAttack;
        s.seq=(s.seq||0)+1;
        s.locked=exactPhase;s.started=now;s.origin={x:o.x,y:o.y,z:o.z};s.face=o.face;
        s.variantBase='a'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3;s.variantMotion=null;
        s.phaseFrom=from;s.phaseFamily=exactPhase;s.phaseAttack=o.attack;s.phaseSwitches=(s.phaseSwitches||0)+1;
        PHASE_RELOCKS++;
        const pk=(from||'?')+'→'+exactPhase+'|A'+attackFrom+'→'+o.attack;
        PHASE_RELOCK_BY[pk]=(PHASE_RELOCK_BY[pk]||0)+1;
        qlog('🔁 active phase relock','slot',o.slot,'type',o.type,pk,'state',o.s0+':'+o.s1+':'+o.s2+':'+o.s3);
      }else s.phaseAttack=o.attack;
    }else if(s.prevAttack!==0&&o.attack===0){""",
"""      s.phaseFamily=null;s.phaseFrom=null;s.phaseAttack=o.attack;s.phaseStarted=0;s.phaseOrigin=null;s.phaseFace=0;
    }else if(s.prevAttack!==0&&o.attack!==0&&o.attack!==s.prevAttack){
      const exactPhase=DB.a[keyActive(o)]||null;
      if(exactPhase&&exactPhase!==s.locked){
        const from=s.phaseFamily||s.locked||null,attackFrom=s.prevAttack;
        s.phaseFrom=from;s.phaseFamily=exactPhase;s.phaseAttack=o.attack;
        s.phaseStarted=now;s.phaseOrigin={x:o.x,y:o.y,z:o.z};s.phaseFace=o.face;
        s.phaseSwitches=(s.phaseSwitches||0)+1;
        PHASE_RELOCKS++;
        const pk=(from||'?')+'→'+exactPhase+'|A'+attackFrom+'→'+o.attack;
        PHASE_RELOCK_BY[pk]=(PHASE_RELOCK_BY[pk]||0)+1;
        qlog('🔁 active phase overlay','slot',o.slot,'type',o.type,pk,'state',o.s0+':'+o.s1+':'+o.s2+':'+o.s3);
      }else{
        s.phaseAttack=o.attack;
        if(!exactPhase||exactPhase===s.locked){s.phaseFamily=null;s.phaseStarted=0;s.phaseOrigin=null;s.phaseFace=0;}
      }
    }else if(s.prevAttack!==0&&o.attack===0){""",
'non destructive phase transition')

rep(
"""      s.locked=null;s.origin=null;s.started=0;s.variantBase=null;s.variantMotion=null;s.phaseFamily=null;s.phaseFrom=null;s.phaseAttack=0;""",
"""      s.locked=null;s.origin=null;s.started=0;s.variantBase=null;s.variantMotion=null;s.phaseFamily=null;s.phaseFrom=null;s.phaseAttack=0;s.phaseStarted=0;s.phaseOrigin=null;s.phaseFace=0;""",
'tail clears phase overlay')

# Add a WATCH-only overlay using the exact phase Family. It participates in raw/stable
# danger coverage but never produces movement/AB and never enters action FP calibration.
needle="""  function addActiveGuard(o,s,now,out){"""
insert="""  function addPhaseOverlay(o,s,now,out){
    if(!s.phaseFamily||!s.phaseOrigin||s.phaseFamily===s.locked)return;
    const f=getFamily(s.phaseFamily);if(!f)return;
    const rad=radius(f),age=Math.max(0,now-s.phaseStarted),sg=faceSign(s.phaseFace),dur90=+f[2]||1000;
    const maxT=Math.min(CFG.horizonMs,CFG.phaseOverlayHorizonMs);
    out.enemies.add(o.slot);
    for(let t=0;t<=maxT;t+=CFG.dangerStepMs){
      const a=age+t;if(a>dur90)continue;
      const sw=interp(f[7],a,'sw');if(!sw)continue;
      const survival=Math.max(0,Math.min(1,sw.survival??1));
      if(survival<CFG.minConfidence)continue;
      out.danger.push({t,x:s.phaseOrigin.x+sg*sw.x,y:s.phaseOrigin.y+sw.y,z:s.phaseOrigin.z+sw.z,
        rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:s.phaseFamily,
        variant:'phase|'+o.attack,confidence:survival,survival,actionable:false,
        phaseWatch:true,watchOnly:true,source:'active-phase-watch'});
    }
  }

  function addActiveGuard(o,s,now,out){"""
rep(needle,insert,'insert phase overlay')

rep(
"""      if(o.attack!==0){addActive(o,s,now,out);addActiveGuard(o,s,now,out);}""",
"""      if(o.attack!==0){addActive(o,s,now,out);addPhaseOverlay(o,s,now,out);addActiveGuard(o,s,now,out);}""",
'build phase overlay')

rep(
"""      if(!o){s.type=null;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.tail=null;s.phaseFamily=null;s.phaseFrom=null;s.phaseAttack=0;continue;}""",
"""      if(!o){s.type=null;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.tail=null;s.phaseFamily=null;s.phaseFrom=null;s.phaseAttack=0;s.phaseStarted=0;s.phaseOrigin=null;s.phaseFace=0;continue;}""",
'clear absent phase overlay')

# Ensure phase-watch warnings cannot become action-core FP audits even if selected as WATCH evidence.
rep(
"""    if(st.geometryWatchOnly||st.edgeWatchOnly||st.shadowWatchOnly||st.guardWatchOnly||st.debounceWatchOnly)return;""",
"""    if(st.geometryWatchOnly||st.edgeWatchOnly||st.shadowWatchOnly||st.guardWatchOnly||st.debounceWatchOnly||st.phaseWatchOnly)return;""",
'phase no fp audit') if "st.geometryWatchOnly||st.edgeWatchOnly||st.shadowWatchOnly||st.guardWatchOnly||st.debounceWatchOnly)return;" in s else None

# Mark stable results sourced from phase overlay. Existing danger evaluator may not copy
# phaseWatchOnly, so source-level actionability=false already guarantees WATCH-only.
rep("version:'offline-dynamic-spectator-calibrated-v4.10.0'","version:'offline-dynamic-spectator-calibrated-v4.10.1'",'version')
rep("qlog('✅ WOF V4.10.0 active多阶段Family重锁版启动');","qlog('✅ WOF V4.10.1 非破坏式阶段叠加/覆盖回归修复版启动');",'startup')
rep(
"""  qlog('🔁 active多阶段: ATTACK非0内部切换时，仅当当前type+ATTACK+state精确命中另一Family才重锁并重置轨迹时钟；不使用模糊fallback');""",
"""  qlog('🔁 active多阶段: 保留0→非0时的主Family轨迹；ATTACK内部精确阶段只作为WATCH叠加，绝不再重置主轨迹时钟/原点');""",
'phase startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.10.1',len(s))
