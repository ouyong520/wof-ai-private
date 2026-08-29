from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.9.4" not in s:
    raise SystemExit('expected V4.9.4 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,1)

rep(
"""    postDamageGuardMs:700,
    respawnGuardMs:1500,
    fallbackZThreshold:80,""",
"""    postDamageGuardMs:700,
    respawnGuardMs:1500,
    returnGuardMs:280,
    activeGuardHorizonMs:350,
    activeGuardStepMs:50,
    activeGuardMinRx:82,
    activeGuardMaxRx:150,
    activeGuardMinRy:18,
    activeGuardMaxRy:32,
    activeGuardMinRz:12,
    activeGuardMaxRz:24,
    activeGuardVelocityCapX:260,
    activeGuardVelocityCapY:120,
    activeGuardVelocityCapZ:220,
    fallbackZThreshold:80,""",
'presence/guard cfg')

rep(
"""    const A=AUD?.[name];if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;A.lastRawWarnAt=-1e9;A.lastShadowWarnAt=-1e9;A.lastShadowRawAt=-1e9;A.recent={};A.dead=false;A.absent=false;A.suppressUntil=-1e9;A.lastDamageAt=-1e9;}""",
"""    const A=AUD?.[name];if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;A.lastRawWarnAt=-1e9;A.lastShadowWarnAt=-1e9;A.lastShadowRawAt=-1e9;A.lastGuardWarnAt=-1e9;A.lastGuardRawAt=-1e9;A.recent={};A.dead=false;A.absent=false;A.suppressUntil=-1e9;A.lastDamageAt=-1e9;}""",
'reset guard timestamps')

# Add a WATCH-only short-horizon safety fence around every currently active enemy.
# It never enters actionDanger, so it cannot directly produce UP/DOWN/AB or calibration FP.
rep(
"""  function buildDanger(now){
    const out={danger:[],enemies:new Set(),exact:0,coarse:0};""",
"""  function addActiveGuard(o,s,now,out){
    const f=s.locked?getFamily(s.locked):null,rad=f?radius(f):null;
    const baseRx=rad?(rad.actionRx||rad.rx):100,baseRy=rad?(rad.actionRy||rad.ry):22,baseRz=rad?(rad.actionRz||rad.rz):16;
    const rx=Math.max(CFG.activeGuardMinRx,Math.min(CFG.activeGuardMaxRx,baseRx*1.15));
    const ry=Math.max(CFG.activeGuardMinRy,Math.min(CFG.activeGuardMaxRy,baseRy*1.15));
    const rz=Math.max(CFG.activeGuardMinRz,Math.min(CFG.activeGuardMaxRz,baseRz*1.15));
    const age=Math.max(0,now-(s.started||now));
    let vx=0,vy=0,vz=0;
    if(s.origin&&age>=80){
      const sec=Math.max(.08,age/1000);
      vx=(o.x-s.origin.x)/sec;vy=(o.y-s.origin.y)/sec;vz=(o.z-s.origin.z)/sec;
      vx=Math.max(-CFG.activeGuardVelocityCapX,Math.min(CFG.activeGuardVelocityCapX,vx));
      vy=Math.max(-CFG.activeGuardVelocityCapY,Math.min(CFG.activeGuardVelocityCapY,vy));
      vz=Math.max(-CFG.activeGuardVelocityCapZ,Math.min(CFG.activeGuardVelocityCapZ,vz));
    }
    for(let t=CFG.reactFloorMs;t<=CFG.activeGuardHorizonMs;t+=CFG.activeGuardStepMs){
      const dt=t/1000;
      out.danger.push({t,x:o.x+vx*dt,y:o.y+vy*dt,z:o.z+vz*dt,rx,ry,rz,
        slot:o.slot,type:o.type,family:s.locked||null,variant:null,confidence:.16,survival:1,
        actionable:false,guardWatch:true,source:'active-guard'});
    }
  }

  function buildDanger(now){
    const out={danger:[],enemies:new Set(),exact:0,coarse:0};""",
'active guard helper')

rep(
"""      if(o.attack!==0)addActive(o,s,now,out);
      else{const h=lookup(o);if(h){out[h.kind]++;addStartup(o,h,out);}}""",
"""      if(o.attack!==0){addActive(o,s,now,out);addActiveGuard(o,s,now,out);}
      else{const h=lookup(o);if(h){out[h.kind]++;addStartup(o,h,out);}}""",
'call active guard')

rep(
"""    if(!fullCur.safe){
      const gh=fullCur.hit||{};
      const geometryWatch=!!gh.geometryFallback;
      return{danger:true,watchOnly:true,geometryWatchOnly:geometryWatch,edgeWatchOnly:!geometryWatch,
        best:'WATCH',hitMs:fullCur.collisionMs,hit:gh,stay:fullCur};
    }""",
"""    if(!fullCur.safe){
      const gh=fullCur.hit||{};
      const guardWatch=gh.source==='active-guard'||!!gh.guardWatch;
      const geometryWatch=!guardWatch&&!!gh.geometryFallback;
      return{danger:true,watchOnly:true,guardWatchOnly:guardWatch,geometryWatchOnly:geometryWatch,edgeWatchOnly:!guardWatch&&!geometryWatch,
        best:'WATCH',hitMs:fullCur.collisionMs,hit:gh,stay:fullCur};
    }""",
'decision guard watch')

rep(
"""  const need=r.shadowWatchOnly?1:action==='SAFE'?2:action==='WATCH'?2:action==='AB'?3:((+r.hitMs||9999)<=300?2:3);""",
"""  const need=(r.shadowWatchOnly||r.guardWatchOnly)?1:action==='SAFE'?2:action==='WATCH'?2:action==='AB'?3:((+r.hitMs||9999)<=300?2:3);""",
'guard one-frame stability')

rep(
"""  else if(action==='WATCH'&&r.shadowWatchOnly)qlog('🟨',name,'WATCH-安全影子','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'halo',Math.round((CFG.shadowRadiusScale-1)*100)+'%','source',h.source||'?');
  else if(action==='WATCH')qlog('🟠',name,'WATCH','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?','source',h.source||'?');""",
"""  else if(action==='WATCH'&&r.shadowWatchOnly)qlog('🟨',name,'WATCH-安全影子','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'halo',Math.round((CFG.shadowRadiusScale-1)*100)+'%','source',h.source||'?');
  else if(action==='WATCH'&&r.guardWatchOnly)qlog('🟫',name,'WATCH-主动攻击护栏','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?',
    'r',fmt(h.rx)+'/'+fmt(h.ry)+'/'+fmt(h.rz));
  else if(action==='WATCH')qlog('🟠',name,'WATCH','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?', 'source',h.source||'?');""",
'print guard watch')

# Extend AUD with neutral presence transitions and guard coverage counters.
old_aud="""const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0},byFamily:{}}
};"""
new_aud="""const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0},byFamily:{}}
};"""
rep(old_aud,new_aud,'AUD neutral presence/guard stats')

# Absence is NOT death in spectator mode. It can be a room transition, join/leave, or transient object reset.
rep(
"""function auditMarkAbsent(name,now){
  const A=AUD[name];if(!A)return;
  if(!A.absent){
    A.absent=true;A.dead=true;
    if(A.pending)auditGuard(name,A.pending,'玩家对象暂时消失/死亡');
    qlog('⚰️',name,'玩家对象消失：暂停命中/误报审计');
  }
  A.prevHp=null;
  A.suppressUntil=Math.max(A.suppressUntil||-1e9,now+CFG.respawnGuardMs);
}""",
"""function auditMarkAbsent(name,now){
  const A=AUD[name];if(!A)return;
  if(!A.absent){
    A.absent=true;A.stats.absentEvents++;
    if(A.pending)auditGuard(name,A.pending,'玩家对象暂时消失/场景切换');
    qlog('⚪',name,'玩家对象暂时不存在：仅暂停审计，不判定死亡');
  }
  A.prevHp=null;
}""",
'neutral absence')

# Split actual respawn (must follow observed HP=0 death) from ordinary object return.
rep(
"""  // Return from death/absence: clear stale audit state and wait through respawn invulnerability.
  if((A.dead||A.absent)&&hp>0){
    if(A.pending)auditGuard(name,A.pending,'复活/重新出现');
    A.dead=false;A.absent=false;A.prevHp=hp;A.suppressUntil=now+CFG.respawnGuardMs;A.stats.respawnEvents++;
    A.lastWarnAt=A.lastRawWarnAt=A.lastShadowWarnAt=A.lastShadowRawAt=-1e9;
    qlog('♻️',name,'复活/重新出现：'+CFG.respawnGuardMs+'ms内暂停FP审计');
    return;
  }
  if(A.prevHp==null&&hp<=0){A.dead=true;A.prevHp=hp;return;}
  if(A.dead&&hp<=0){A.prevHp=hp;if(A.pending)auditGuard(name,A.pending,'HP=0/死亡中');return;}""",
"""  // Actual respawn is counted only after an observed HP=0 death. Ordinary object disappearance is neutral.
  if(A.dead&&hp>0){
    if(A.pending)auditGuard(name,A.pending,'真实复活');
    A.dead=false;A.absent=false;A.prevHp=hp;A.suppressUntil=now+CFG.respawnGuardMs;A.stats.respawnEvents++;
    A.lastWarnAt=A.lastRawWarnAt=A.lastShadowWarnAt=A.lastShadowRawAt=A.lastGuardWarnAt=A.lastGuardRawAt=-1e9;
    qlog('♻️',name,'HP=0后复活：'+CFG.respawnGuardMs+'ms内暂停FP审计');
    return;
  }
  if(A.absent&&hp>0){
    if(A.pending)auditGuard(name,A.pending,'对象重新出现');
    A.absent=false;A.prevHp=hp;A.suppressUntil=now+CFG.returnGuardMs;A.stats.returnEvents++;
    A.lastWarnAt=A.lastRawWarnAt=A.lastShadowWarnAt=A.lastShadowRawAt=A.lastGuardWarnAt=A.lastGuardRawAt=-1e9;
    qlog('↩️',name,'对象重新出现：只重建HP基线，不算复活');
    return;
  }
  if(A.prevHp==null){A.prevHp=hp;return;}
  if(A.dead&&hp<=0){A.prevHp=hp;if(A.pending)auditGuard(name,A.pending,'HP=0/死亡中');return;}""",
'split respawn/return')

# Guard coverage timestamps + diagnostics.
rep(
"""  if(rawAction&&rawAction!=='SAFE')A.lastRawWarnAt=now;
  if(raw?.shadowWatchOnly)A.lastShadowRawAt=now;
  const hp=ps.hp;""",
"""  if(rawAction&&rawAction!=='SAFE')A.lastRawWarnAt=now;
  if(raw?.shadowWatchOnly)A.lastShadowRawAt=now;
  if(raw?.guardWatchOnly)A.lastGuardRawAt=now;
  const hp=ps.hp;""",
'audit raw guard timestamp')

rep(
"""      A.stats.watchCovered++;
      const shadow=now-A.lastShadowWarnAt<=350;
      if(shadow)A.stats.shadowCovered++;
      qlog(shadow?'🟨':'🟩',name,shadow?'安全影子WATCH覆盖掉血':'稳定WATCH覆盖掉血','HP '+hpBefore+'→'+hp);""",
"""      A.stats.watchCovered++;
      const shadow=now-A.lastShadowWarnAt<=350,guard=now-A.lastGuardWarnAt<=350;
      if(shadow)A.stats.shadowCovered++;
      if(guard)A.stats.guardCovered++;
      qlog(guard?'🟫':shadow?'🟨':'🟩',name,guard?'主动攻击护栏覆盖掉血':shadow?'安全影子WATCH覆盖掉血':'稳定WATCH覆盖掉血','HP '+hpBefore+'→'+hp);""",
'guard coverage classification')

rep(
"""  if(st&&action!=='SAFE')A.lastWarnAt=now;
  if(st?.shadowWatchOnly)A.lastShadowWarnAt=now;
  if(!A.pending&&st&&action!=='SAFE'&&st.hitMs!=null){""",
"""  if(st&&action!=='SAFE')A.lastWarnAt=now;
  if(st?.shadowWatchOnly)A.lastShadowWarnAt=now;
  if(st?.guardWatchOnly)A.lastGuardWarnAt=now;
  if(!A.pending&&st&&action!=='SAFE'&&st.hitMs!=null){""",
'stable guard timestamp')

rep(
"""    if(st.geometryWatchOnly||st.edgeWatchOnly||st.shadowWatchOnly)return;""",
"""    if(st.geometryWatchOnly||st.edgeWatchOnly||st.shadowWatchOnly||st.guardWatchOnly)return;""",
'guard no audit pending')

rep(
"""  for(const n of ['P1','P2','P3'])out[n]={...AUD[n].stats,dead:!!AUD[n].dead,protected:!!AUD[n].dead||performance.now()<(AUD[n].suppressUntil||-1e9),""",
"""  for(const n of ['P1','P2','P3'])out[n]={...AUD[n].stats,dead:!!AUD[n].dead,absent:!!AUD[n].absent,protected:!!AUD[n].dead||performance.now()<(AUD[n].suppressUntil||-1e9),""",
'audit snapshot absent')

rep(
"""  const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0};""",
"""  const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0};""",
'total neutral/guard stats')

rep(
"""    shadowDamageCoverage:damageEvents?+(total.shadowCovered/damageEvents).toFixed(3):null,
    validated,damageEvents};""",
"""    shadowDamageCoverage:damageEvents?+(total.shadowCovered/damageEvents).toFixed(3):null,
    guardDamageCoverage:damageEvents?+(total.guardCovered/damageEvents).toFixed(3):null,
    validated,damageEvents};""",
'guard coverage metric')

rep("version:'offline-dynamic-spectator-calibrated-v4.9.4'","version:'offline-dynamic-spectator-calibrated-v4.9.5'",'version')
rep("qlog('✅ WOF V4.9.4 死亡/受击保护审计版启动');","qlog('✅ WOF V4.9.5 中性存在/主动攻击护栏观战版启动');",'startup')
rep(
"qlog('🛡️ 审计保护: 掉血后'+CFG.postDamageGuardMs+'ms、死亡/对象消失、复活后'+CFG.respawnGuardMs+'ms不允许产生FP；真实掉血事件仍正常统计');",
"qlog('🛡️ 审计保护: 掉血后'+CFG.postDamageGuardMs+'ms与真实HP=0死亡/复活保护；对象临时消失只重建基线，不再误算死亡/复活');\n  qlog('🟫 主动攻击护栏: ATTACK!=0 的敌人增加350ms WATCH-only运动护栏；不参与UP/DOWN/AB，也不进入FP校准');",
'startup guard info')
rep(
"qlog('🟧 审计: watchCovered=稳定WATCH覆盖掉血；shadowCovered=其中由安全影子覆盖；unstableCovered=仅raw覆盖；safeMiss=完全未覆盖');",
"qlog('🟧 审计: guardCovered=主动攻击护栏覆盖；watchCovered=稳定WATCH覆盖；unstableCovered=仅raw覆盖；safeMiss=完全未覆盖');",
'startup audit info')

p.write_text(s,encoding='utf-8')
print('patched V4.9.5',len(s))
