from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.9.9" not in s:
    raise SystemExit('expected V4.9.9 input')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,count)

# V4.10.0: track internal ATTACK phase changes. A nonzero ATTACK can transition into
# another known active Family without ever passing through zero. Only exact
# type+ATTACK+state matches are allowed to relock; no fuzzy/unique fallback is used.
rep(
"const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0,seq:0,variantBase:null,variantMotion:null,tail:null}));",
"const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0,seq:0,variantBase:null,variantMotion:null,tail:null,phaseFamily:null,phaseFrom:null,phaseAttack:0,phaseSwitches:0}));",
'slot phase fields')

rep(
"  const ENEMY_HISTORY=[];\n  const MISS_CASES=[];",
"  const ENEMY_HISTORY=[];\n  const MISS_CASES=[];\n  let PHASE_RELOCKS=0;\n  const PHASE_RELOCK_BY=Object.create(null);",
'phase relock counters')

rep(
"if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.seq=0;s.variantBase=null;s.variantMotion=null;s.tail=null;}",
"if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.seq=0;s.variantBase=null;s.variantMotion=null;s.tail=null;s.phaseFamily=null;s.phaseFrom=null;s.phaseAttack=0;s.phaseSwitches=0;}",
'phase reset on type change')

rep(
"""    if(s.prevAttack===0&&o.attack!==0){
      s.seq=(s.seq||0)+1;
      s.locked=DB.a[keyActive(o)]||UNIQUE_ACTIVE.get(o.type+'|'+o.attack)||null;
      s.started=now;s.origin={x:o.x,y:o.y,z:o.z};s.face=o.face;
      s.variantBase='a'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3;s.variantMotion=null;
    }else if(s.prevAttack!==0&&o.attack===0){""",
"""    if(s.prevAttack===0&&o.attack!==0){
      s.seq=(s.seq||0)+1;
      s.locked=DB.a[keyActive(o)]||UNIQUE_ACTIVE.get(o.type+'|'+o.attack)||null;
      s.started=now;s.origin={x:o.x,y:o.y,z:o.z};s.face=o.face;
      s.variantBase='a'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3;s.variantMotion=null;
      s.phaseFamily=s.locked;s.phaseFrom=null;s.phaseAttack=o.attack;
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
'internal active phase relock')

rep(
"""      s.tail={at:now,until:now+CFG.attackTailGuardMs,family,x:o.x,y:o.y,z:o.z,vx,vy,vz};
      s.locked=null;s.origin=null;s.started=0;s.variantBase=null;s.variantMotion=null;""",
"""      s.tail={at:now,until:now+CFG.attackTailGuardMs,family,x:o.x,y:o.y,z:o.z,vx,vy,vz};
      s.locked=null;s.origin=null;s.started=0;s.variantBase=null;s.variantMotion=null;s.phaseFamily=null;s.phaseFrom=null;s.phaseAttack=0;""",
'tail clears phase')

rep(
"""      actors.push({slot:i,type:o.type,x:+o.x.toFixed(1),y:+o.y.toFixed(1),z:+o.z.toFixed(1),face:o.face,
        attack:o.attack,anim:o.anim,s0:o.s0,s1:o.s1,s2:o.s2,s3:o.s3,frame:o.frame,locked:sl.locked||null});""",
"""      const phaseFamily=o.attack!==0?(DB.a[keyActive(o)]||null):null;
      actors.push({slot:i,type:o.type,x:+o.x.toFixed(1),y:+o.y.toFixed(1),z:+o.z.toFixed(1),face:o.face,
        attack:o.attack,anim:o.anim,s0:o.s0,s1:o.s1,s2:o.s2,s3:o.s3,frame:o.frame,locked:sl.locked||null,phaseFamily});""",
'capture exact phase family')

rep(
"""          best.set(o.slot,{score:+score.toFixed(1),ageMs:Math.round(age),slot:o.slot,type:o.type,attack:o.attack,
            locked:o.locked||null,anim:o.anim,state:[o.s0,o.s1,o.s2,o.s3],frame:o.frame,
            dx:+dx.toFixed(1),dy:+dy.toFixed(1),dz:+dz.toFixed(1),startupTop});""",
"""          best.set(o.slot,{score:+score.toFixed(1),ageMs:Math.round(age),slot:o.slot,type:o.type,attack:o.attack,
            locked:o.locked||null,phaseFamily:o.phaseFamily||null,phaseMismatch:!!(o.phaseFamily&&o.locked&&o.phaseFamily!==o.locked),anim:o.anim,state:[o.s0,o.s1,o.s2,o.s3],frame:o.frame,
            dx:+dx.toFixed(1),dy:+dy.toFixed(1),dz:+dz.toFixed(1),startupTop});""",
'miss phase mismatch evidence')

rep(
"""    candidates:(c.candidates||[]).slice(0,3).map(x=>({slot:x.slot,type:x.type,attack:x.attack,locked:x.locked,ageMs:x.ageMs,dx:x.dx,dy:x.dy,dz:x.dz,startupTop:x.startupTop}))}));""",
"""    candidates:(c.candidates||[]).slice(0,3).map(x=>({slot:x.slot,type:x.type,attack:x.attack,locked:x.locked,phaseFamily:x.phaseFamily||null,phaseMismatch:!!x.phaseMismatch,ageMs:x.ageMs,dx:x.dx,dy:x.dy,dz:x.dz,startupTop:x.startupTop}))}));""",
'report phase mismatch')

rep(
"""  return frozenCopy({at:Date.now(),total,metrics,missAttackTop,missTop,players:a,topFalse,demoted,precisionSuppressed,geoAdjusted,geoClasses});""",
"""  const phaseRelockTop=Object.entries(PHASE_RELOCK_BY).sort((a,b)=>b[1]-a[1]).slice(0,10).map(([key,count])=>({key,count}));
  return frozenCopy({at:Date.now(),total,metrics,phaseRelocks:PHASE_RELOCKS,phaseRelockTop,missAttackTop,missTop,players:a,topFalse,demoted,precisionSuppressed,geoAdjusted,geoClasses});""",
'phase relock report')

rep(
"""      if(!o){s.type=null;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.tail=null;continue;}""",
"""      if(!o){s.type=null;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.tail=null;s.phaseFamily=null;s.phaseFrom=null;s.phaseAttack=0;continue;}""",
'phase clear absent actor')

rep("version:'offline-dynamic-spectator-calibrated-v4.9.9'","version:'offline-dynamic-spectator-calibrated-v4.10.0'",'version')
rep("qlog('✅ WOF V4.9.9 稳定桥/覆盖收敛版启动');","qlog('✅ WOF V4.10.0 active多阶段Family重锁版启动');",'startup')
rep(
"""  qlog('⚡ 稳定器: WATCH连续性保持；UP/DOWN/AB未确认期间若raw危险<=350ms，先输出WATCH稳定桥，绝不提前动作/AB');""",
"""  qlog('⚡ 稳定器: WATCH连续性保持；UP/DOWN/AB未确认期间若raw危险<=350ms，先输出WATCH稳定桥，绝不提前动作/AB');
  qlog('🔁 active多阶段: ATTACK非0内部切换时，仅当当前type+ATTACK+state精确命中另一Family才重锁并重置轨迹时钟；不使用模糊fallback');""",
'phase startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.10.0',len(s))
