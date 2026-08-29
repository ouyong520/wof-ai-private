from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.9.7" not in s:
    raise SystemExit('expected V4.9.7 input')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,count)

# WATCH-only tail guard: damage can land a few frames after ATTACK returns to zero.
rep(
"""    watchPromoteMaxMs:280,
    activeGuardVelocityCapX:260,""",
"""    watchPromoteMaxMs:280,
    attackTailGuardMs:280,
    attackTailHorizonMs:220,
    attackTailMinRx:88,
    attackTailMaxRx:150,
    attackTailMinRy:20,
    attackTailMaxRy:34,
    attackTailMinRz:14,
    attackTailMaxRz:24,
    activeGuardVelocityCapX:260,""",
'attack tail cfg')

rep(
"""const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0,seq:0,variantBase:null,variantMotion:null}));""",
"""const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0,seq:0,variantBase:null,variantMotion:null,tail:null}));""",
'slot tail state')

rep(
"""if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.seq=0;s.variantBase=null;s.variantMotion=null;}""",
"""if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.seq=0;s.variantBase=null;s.variantMotion=null;s.tail=null;}""",
'type reset tail')

rep(
"""    }else if(s.prevAttack!==0&&o.attack===0){s.locked=null;s.origin=null;s.started=0;s.variantBase=null;s.variantMotion=null;}""",
"""    }else if(s.prevAttack!==0&&o.attack===0){
      const family=s.locked||null,age=Math.max(0,now-(s.started||now)),sec=Math.max(.08,age/1000);
      let vx=0,vy=0,vz=0;
      if(s.origin&&age>=80){
        vx=(o.x-s.origin.x)/sec;vy=(o.y-s.origin.y)/sec;vz=(o.z-s.origin.z)/sec;
        vx=Math.max(-CFG.activeGuardVelocityCapX,Math.min(CFG.activeGuardVelocityCapX,vx));
        vy=Math.max(-CFG.activeGuardVelocityCapY,Math.min(CFG.activeGuardVelocityCapY,vy));
        vz=Math.max(-CFG.activeGuardVelocityCapZ,Math.min(CFG.activeGuardVelocityCapZ,vz));
      }
      s.tail={at:now,until:now+CFG.attackTailGuardMs,family,x:o.x,y:o.y,z:o.z,vx,vy,vz};
      s.locked=null;s.origin=null;s.started=0;s.variantBase=null;s.variantMotion=null;
    }""",'capture attack tail')

# Insert a WATCH-only guard after ATTACK drops to zero. It cannot drive movement/AB or FP calibration.
marker="""  function buildDanger(now){
    const out={danger:[],enemies:new Set(),exact:0,coarse:0};"""
insert="""  function addAttackTailGuard(o,s,now,out){
    const q=s.tail;if(!q||now>q.until)return;
    const f=q.family?getFamily(q.family):null,rad=f?radius(f):null;
    const baseRx=rad?(rad.actionRx||rad.rx):96,baseRy=rad?(rad.actionRy||rad.ry):22,baseRz=rad?(rad.actionRz||rad.rz):16;
    const rx=Math.max(CFG.attackTailMinRx,Math.min(CFG.attackTailMaxRx,baseRx*1.15));
    const ry=Math.max(CFG.attackTailMinRy,Math.min(CFG.attackTailMaxRy,baseRy*1.15));
    const rz=Math.max(CFG.attackTailMinRz,Math.min(CFG.attackTailMaxRz,baseRz*1.15));
    const remain=Math.max(CFG.reactFloorMs,Math.min(CFG.attackTailHorizonMs,q.until-now+80));
    for(let t=CFG.reactFloorMs;t<=remain;t+=CFG.activeGuardStepMs){
      const dt=t/1000;
      out.danger.push({t,x:o.x+q.vx*dt,y:o.y+q.vy*dt,z:o.z+q.vz*dt,rx,ry,rz,
        slot:o.slot,type:o.type,family:q.family||null,variant:null,confidence:.15,survival:1,
        actionable:false,guardWatch:true,tailGuard:true,source:'attack-tail-guard'});
    }
  }

  function buildDanger(now){
    const out={danger:[],enemies:new Set(),exact:0,coarse:0};"""
rep(marker,insert,'insert tail guard function')

rep(
"""      if(!o){s.type=null;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;continue;}""",
"""      if(!o){s.type=null;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.tail=null;continue;}""",
'clear tail missing actor')
rep(
"""      if(o.attack!==0){addActive(o,s,now,out);addActiveGuard(o,s,now,out);}
      else{const h=lookup(o);if(h){out[h.kind]++;addStartup(o,h,out);}}""",
"""      if(o.attack!==0){addActive(o,s,now,out);addActiveGuard(o,s,now,out);}
      else{addAttackTailGuard(o,s,now,out);const h=lookup(o);if(h){out[h.kind]++;addStartup(o,h,out);}}""",
'build tail guard')

# Distinguish tail WATCH while keeping it inside the existing generic guard path.
rep(
"""      const gh=fullCur.hit||{};
      const guardWatch=gh.source==='active-guard'||!!gh.guardWatch;
      const geometryWatch=!guardWatch&&!!gh.geometryFallback;
      return{danger:true,watchOnly:true,guardWatchOnly:guardWatch,geometryWatchOnly:geometryWatch,edgeWatchOnly:!guardWatch&&!geometryWatch,""",
"""      const gh=fullCur.hit||{};
      const tailWatch=gh.source==='attack-tail-guard'||!!gh.tailGuard;
      const guardWatch=tailWatch||gh.source==='active-guard'||!!gh.guardWatch;
      const geometryWatch=!guardWatch&&!!gh.geometryFallback;
      return{danger:true,watchOnly:true,guardWatchOnly:guardWatch,tailWatchOnly:tailWatch,geometryWatchOnly:geometryWatch,edgeWatchOnly:!guardWatch&&!geometryWatch,""",
'tail decision tag')

rep(
"""  else if(action==='WATCH'&&r.guardWatchOnly)qlog('🟫',name,'WATCH-主动攻击护栏','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?',
    'r',fmt(h.rx)+'/'+fmt(h.ry)+'/'+fmt(h.rz));""",
"""  else if(action==='WATCH'&&r.tailWatchOnly)qlog('🟧',name,'WATCH-攻击尾帧护栏','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?',
    'r',fmt(h.rx)+'/'+fmt(h.ry)+'/'+fmt(h.rz));
  else if(action==='WATCH'&&r.guardWatchOnly)qlog('🟫',name,'WATCH-主动攻击护栏','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?',
    'r',fmt(h.rx)+'/'+fmt(h.ry)+'/'+fmt(h.rz));""",'print tail watch')

# Add tail audit timestamps/counters for P1/P2/P3.
s=s.replace("lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,lastWatchEvidence:null,", "lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,lastTailWarnAt:-1e9,lastWatchEvidence:null,")
s=s.replace("guardCovered:0,watchPromoted:0,", "guardCovered:0,tailCovered:0,watchPromoted:0,")
rep(
"""A.lastGuardWarnAt=-1e9;A.lastGuardRawAt=-1e9;A.lastWatchEvidence=null;A.recent={};""",
"""A.lastGuardWarnAt=-1e9;A.lastGuardRawAt=-1e9;A.lastTailWarnAt=-1e9;A.lastWatchEvidence=null;A.recent={};""",
'reset tail timestamp')

rep(
"""      const shadow=now-A.lastShadowWarnAt<=350,guard=now-A.lastGuardWarnAt<=350;
      if(shadow)A.stats.shadowCovered++;
      if(guard)A.stats.guardCovered++;""",
"""      const shadow=now-A.lastShadowWarnAt<=350,guard=now-A.lastGuardWarnAt<=350,tail=now-A.lastTailWarnAt<=350;
      if(shadow)A.stats.shadowCovered++;
      if(guard)A.stats.guardCovered++;
      if(tail)A.stats.tailCovered++;""",'damage tail coverage')
rep(
"""      qlog(guard?'🟫':shadow?'🟨':'🟩',name,guard?'主动攻击护栏覆盖掉血':shadow?'安全影子WATCH覆盖掉血':'稳定WATCH覆盖掉血','HP '+hpBefore+'→'+hp);""",
"""      qlog(tail?'🟧':guard?'🟫':shadow?'🟨':'🟩',name,tail?'攻击尾帧护栏覆盖掉血':guard?'主动攻击护栏覆盖掉血':shadow?'安全影子WATCH覆盖掉血':'稳定WATCH覆盖掉血','HP '+hpBefore+'→'+hp);""",'tail coverage log')
rep(
"""  if(st?.guardWatchOnly)A.lastGuardWarnAt=now;
  if(st&&action==='WATCH'&&!st.shadowWatchOnly&&!st.guardWatchOnly){""",
"""  if(st?.guardWatchOnly)A.lastGuardWarnAt=now;
  if(st?.tailWatchOnly)A.lastTailWarnAt=now;
  if(st&&action==='WATCH'&&!st.shadowWatchOnly&&!st.guardWatchOnly){""",
'tail stable timestamp')

# Include tailCovered in totals and metric.
rep(
"""const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,watchPromoted:0,""",
"""const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,tailCovered:0,watchPromoted:0,""",
'total tail covered')
rep(
"""    guardDamageCoverage:damageEvents?+(total.guardCovered/damageEvents).toFixed(3):null,
    validated,damageEvents};""",
"""    guardDamageCoverage:damageEvents?+(total.guardCovered/damageEvents).toFixed(3):null,
    tailDamageCoverage:damageEvents?+(total.tailCovered/damageEvents).toFixed(3):null,
    validated,damageEvents};""",
'tail metric')

# Aggregate SAFE-miss candidates so the useful offenders are visible even if console output is clipped.
rep(
"""  const missTop=MISS_CASES.slice(-6).map(c=>({id:c.id,kind:c.kind,player:c.player,hp:c.hp,rawHit:c.rawHit,nearest:c.nearest,
    candidates:(c.candidates||[]).slice(0,3).map(x=>({slot:x.slot,type:x.type,attack:x.attack,locked:x.locked,ageMs:x.ageMs,dx:x.dx,dy:x.dy,dz:x.dz,startupTop:x.startupTop}))}));
  return frozenCopy({at:Date.now(),total,metrics,missTop,players:a,topFalse,demoted,precisionSuppressed,geoAdjusted,geoClasses});""",
"""  const missTop=MISS_CASES.slice(-6).map(c=>({id:c.id,kind:c.kind,player:c.player,hp:c.hp,rawHit:c.rawHit,nearest:c.nearest,
    candidates:(c.candidates||[]).slice(0,3).map(x=>({slot:x.slot,type:x.type,attack:x.attack,locked:x.locked,ageMs:x.ageMs,dx:x.dx,dy:x.dy,dz:x.dz,startupTop:x.startupTop}))}));
  const ma=Object.create(null);
  for(const c of MISS_CASES)if(c.kind==='safeMiss')for(const x of (c.candidates||[]).slice(0,3)){
    const k='T'+x.type+'|A'+x.attack+'|'+(x.locked||'?'),r=ma[k]||(ma[k]={key:k,count:0,type:x.type,attack:x.attack,locked:x.locked||null,minDx:999,minDy:999,minDz:999});
    r.count++;r.minDx=Math.min(r.minDx,+x.dx||999);r.minDy=Math.min(r.minDy,+x.dy||999);r.minDz=Math.min(r.minDz,+x.dz||999);
  }
  const missAttackTop=Object.values(ma).sort((x,y)=>y.count-x.count||x.minDx-y.minDx).slice(0,10).map(r=>({...r,minDx:+r.minDx.toFixed(1),minDy:+r.minDy.toFixed(1),minDz:+r.minDz.toFixed(1)}));
  return frozenCopy({at:Date.now(),total,metrics,missAttackTop,missTop,players:a,topFalse,demoted,precisionSuppressed,geoAdjusted,geoClasses});""",
'miss attack aggregate')

rep("version:'offline-dynamic-spectator-calibrated-v4.9.7'","version:'offline-dynamic-spectator-calibrated-v4.9.8'",'version')
rep("qlog('✅ WOF V4.9.7 WATCH连续性/紧急预警版启动');","qlog('✅ WOF V4.9.8 攻击尾帧护栏/漏判聚合版启动');",'startup')
rep(
"""  qlog('🟫 主动攻击护栏: ATTACK!=0 扩为450ms WATCH-only运动护栏；不参与UP/DOWN/AB，也不进入FP校准');""",
"""  qlog('🟫 主动攻击护栏: ATTACK!=0 扩为450ms WATCH-only运动护栏；不参与UP/DOWN/AB，也不进入FP校准');
  qlog('🟧 攻击尾帧护栏: ATTACK从非0回到0后继续保留'+CFG.attackTailGuardMs+'ms WATCH-only预测，捕捉延迟掉血/尾帧命中');""",
'tail startup log')
rep(
"""  qlog('🟧 审计: guardCovered=主动攻击护栏覆盖；watchCovered=稳定WATCH覆盖；unstableCovered=仅raw覆盖；safeMiss=完全未覆盖');""",
"""  qlog('🟧 审计: guardCovered=主动攻击护栏覆盖；tailCovered=ATTACK结束尾帧覆盖；watchCovered=稳定WATCH覆盖；safeMiss=完全未覆盖');""",'audit startup log')

p.write_text(s,encoding='utf-8')
print('patched V4.9.8',len(s))
