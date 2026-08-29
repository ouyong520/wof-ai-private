from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.9.5" not in s:
    raise SystemExit('expected V4.9.5 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,1)

# Broaden the WATCH-only active guard a little. It cannot issue UP/DOWN/AB or create FP calibration.
rep(
"""    activeGuardHorizonMs:350,
    activeGuardStepMs:50,
    activeGuardMinRx:82,
    activeGuardMaxRx:150,
    activeGuardMinRy:18,
    activeGuardMaxRy:32,
    activeGuardMinRz:12,
    activeGuardMaxRz:24,""",
"""    activeGuardHorizonMs:450,
    activeGuardStepMs:50,
    activeGuardMinRx:90,
    activeGuardMaxRx:165,
    activeGuardMinRy:20,
    activeGuardMaxRy:36,
    activeGuardMinRz:14,
    activeGuardMaxRz:26,
    watchPromoteMaxMs:280,""",
'guard/watch promote cfg')
rep("baseRx*1.15","baseRx*1.22",'guard rx scale')
rep("baseRy*1.15","baseRy*1.22",'guard ry scale')
rep("baseRz*1.15","baseRz*1.22",'guard rz scale')

# Active Family geometry must earn two source-specific real hits before it may drive movement advice.
# Full Family shells remain in the danger map as WATCH, so safety coverage is retained while learning.
old_policy="""    const precisionWatch=variantBad||sourceBad||familyBad;
    let trustScale=source==='active'?CAL_CFG.trustUnseenActive:CAL_CFG.trustUnseenStartup;
    let trustReason='unseen';
    if(variantBad||sourceBad||familyBad){trustScale=CAL_CFG.trustBadEvidence;trustReason=variantBad?'variant-fp':sourceBad?'source-low-precision':'family-low-precision';}
    else if((v?.hit||0)>0){trustScale=1;trustReason='variant-hit';}
    else if((q?.hit||0)>0){trustScale=CAL_CFG.trustSourceHit;trustReason='source-hit';}
    else if((f?.hit||0)>0){trustScale=CAL_CFG.trustFamilyHit;trustReason='family-hit';}
    return {watchOnly:!!(f?.watchOnly||q?.watchOnly||v?.watchOnly||precisionWatch),precisionWatch,trustScale,trustReason,"""
new_policy="""    const precisionWatch=variantBad||sourceBad||familyBad;
    const activeUnverified=source==='active'&&((q?.hit||0)<2);
    let trustScale=source==='active'?CAL_CFG.trustUnseenActive:CAL_CFG.trustUnseenStartup;
    let trustReason='unseen';
    if(variantBad||sourceBad||familyBad){trustScale=CAL_CFG.trustBadEvidence;trustReason=variantBad?'variant-fp':sourceBad?'source-low-precision':'family-low-precision';}
    else if((v?.hit||0)>0){trustScale=1;trustReason='variant-hit';}
    else if((q?.hit||0)>0){trustScale=CAL_CFG.trustSourceHit;trustReason='source-hit';}
    else if((f?.hit||0)>0){trustScale=CAL_CFG.trustFamilyHit;trustReason='family-hit';}
    if(activeUnverified)trustReason='active-needs-2-hits';
    return {watchOnly:!!(f?.watchOnly||q?.watchOnly||v?.watchOnly||precisionWatch||activeUnverified),precisionWatch,activeUnverified,trustScale,trustReason,"""
rep(old_policy,new_policy,'observe-before-act policy')

# Carry activeUnverified into hazards for diagnostics.
rep(
"calWatchOnly:cal.watchOnly,precisionWatch:cal.precisionWatch,trustScale:cal.trustScale,trustReason:cal.trustReason,",
"calWatchOnly:cal.watchOnly,precisionWatch:cal.precisionWatch,activeUnverified:cal.activeUnverified,trustScale:cal.trustScale,trustReason:cal.trustReason,",
'startup activeUnverified field')
rep(
"calWatchOnly:cal.watchOnly,precisionWatch:cal.precisionWatch,trustScale:cal.trustScale,trustReason:cal.trustReason,",
"calWatchOnly:cal.watchOnly,precisionWatch:cal.precisionWatch,activeUnverified:cal.activeUnverified,trustScale:cal.trustScale,trustReason:cal.trustReason,",
'active activeUnverified field')

# Audit state: remember a stable known-Family WATCH so real damage can promote the active source without first issuing movement advice.
rep(
"""lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0}""",
"""lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,lastWatchEvidence:null,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,watchPromoted:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0}""",
'AUD P1 watch evidence')
rep(
"""lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0}""",
"""lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,lastWatchEvidence:null,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,watchPromoted:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0}""",
'AUD P2 watch evidence')
rep(
"""lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0}""",
"""lastGuardWarnAt:-1e9,lastGuardRawAt:-1e9,lastWatchEvidence:null,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,watchPromoted:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0}""",
'AUD P3 watch evidence')

# Reset stale WATCH evidence when the player runtime is rebuilt.
rep(
"A.lastGuardWarnAt=-1e9;A.lastGuardRawAt=-1e9;A.recent={};",
"A.lastGuardWarnAt=-1e9;A.lastGuardRawAt=-1e9;A.lastWatchEvidence=null;A.recent={};",
'reset watch evidence')

# If real damage occurs under a stable known active-Family WATCH, count that as observational evidence.
old_watch="""    }else if(now-A.lastWarnAt<=350){
      A.stats.watchCovered++;
      const shadow=now-A.lastShadowWarnAt<=350,guard=now-A.lastGuardWarnAt<=350;
      if(shadow)A.stats.shadowCovered++;
      if(guard)A.stats.guardCovered++;
      qlog(guard?'🟫':shadow?'🟨':'🟩',name,guard?'主动攻击护栏覆盖掉血':shadow?'安全影子WATCH覆盖掉血':'稳定WATCH覆盖掉血','HP '+hpBefore+'→'+hp);"""
new_watch="""    }else if(now-A.lastWarnAt<=350){
      A.stats.watchCovered++;
      const shadow=now-A.lastShadowWarnAt<=350,guard=now-A.lastGuardWarnAt<=350;
      if(shadow)A.stats.shadowCovered++;
      if(guard)A.stats.guardCovered++;
      const we=A.lastWatchEvidence;
      if(!guard&&!shadow&&we&&now-we.at<=350&&we.hitMs<=CFG.watchPromoteMaxMs&&we.e?.family&&we.e.source==='active'){
        calRecord({...we.e,player:name},'hit');A.stats.watchPromoted++;
        qlog('🧪',name,'WATCH真实掉血→提升active Family证据',we.e.family,'slot',we.e.slot,'hitMs',we.hitMs);
      }
      qlog(guard?'🟫':shadow?'🟨':'🟩',name,guard?'主动攻击护栏覆盖掉血':shadow?'安全影子WATCH覆盖掉血':'稳定WATCH覆盖掉血','HP '+hpBefore+'→'+hp);"""
rep(old_watch,new_watch,'watch-hit promotion')

# Remember stable WATCH evidence only for a known Family; never learn from shadow/guard-only warnings.
rep(
"""  if(st&&action!=='SAFE')A.lastWarnAt=now;
  if(st?.shadowWatchOnly)A.lastShadowWarnAt=now;
  if(st?.guardWatchOnly)A.lastGuardWarnAt=now;""",
"""  if(st&&action!=='SAFE')A.lastWarnAt=now;
  if(st?.shadowWatchOnly)A.lastShadowWarnAt=now;
  if(st?.guardWatchOnly)A.lastGuardWarnAt=now;
  if(st&&action==='WATCH'&&!st.shadowWatchOnly&&!st.guardWatchOnly){
    const wh=st.hit||{};
    if(wh.family&&wh.source!=='active-unknown')A.lastWatchEvidence={at:now,hitMs:+st.hitMs||9999,e:{...wh,player:name}};
  }""",
'remember stable watch evidence')

# Reset evidence on real respawn/neutral return too.
s=s.replace("A.lastWarnAt=A.lastRawWarnAt=A.lastShadowWarnAt=A.lastShadowRawAt=A.lastGuardWarnAt=A.lastGuardRawAt=-1e9;",
            "A.lastWarnAt=A.lastRawWarnAt=A.lastShadowWarnAt=A.lastShadowRawAt=A.lastGuardWarnAt=A.lastGuardRawAt=-1e9;A.lastWatchEvidence=null;",2)

# Add watchPromoted to totals and move compact miss diagnostics before the long player/topFalse sections.
rep(
"""guardCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,""",
"""guardCovered:0,watchPromoted:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,""",
'total watchPromoted')
rep(
"""  const metrics={actionPrecision:validated?+(total.hit/validated).toFixed(3):null,
    rawDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage+total.watchCovered+total.unstableCovered)/damageEvents).toFixed(3):null,
    stableDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage+total.watchCovered)/damageEvents).toFixed(3):null,
    shadowDamageCoverage:damageEvents?+(total.shadowCovered/damageEvents).toFixed(3):null,
    guardDamageCoverage:damageEvents?+(total.guardCovered/damageEvents).toFixed(3):null,
    validated,damageEvents};
  return frozenCopy({at:Date.now(),total,metrics,players:a,topFalse,demoted,precisionSuppressed,geoAdjusted,geoClasses,missCases:MISS_CASES.slice(-8)});""",
"""  const metrics={actionPrecision:validated?+(total.hit/validated).toFixed(3):null,
    rawDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage+total.watchCovered+total.unstableCovered)/damageEvents).toFixed(3):null,
    stableDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage+total.watchCovered)/damageEvents).toFixed(3):null,
    shadowDamageCoverage:damageEvents?+(total.shadowCovered/damageEvents).toFixed(3):null,
    guardDamageCoverage:damageEvents?+(total.guardCovered/damageEvents).toFixed(3):null,
    validated,damageEvents};
  const missTop=MISS_CASES.slice(-6).map(c=>({id:c.id,kind:c.kind,player:c.player,hp:c.hp,nearest:c.nearest,
    candidates:(c.candidates||[]).slice(0,3).map(x=>({slot:x.slot,type:x.type,attack:x.attack,locked:x.locked,ageMs:x.ageMs,dx:x.dx,dy:x.dy,dz:x.dz,startupTop:x.startupTop}))}));
  return frozenCopy({at:Date.now(),total,metrics,missTop,players:a,topFalse,demoted,precisionSuppressed,geoAdjusted,geoClasses});""",
'compact missTop report')

rep("version:'offline-dynamic-spectator-calibrated-v4.9.5'","version:'offline-dynamic-spectator-calibrated-v4.9.6'",'version')
rep("qlog('✅ WOF V4.9.5 中性存在/主动攻击护栏观战版启动');","qlog('✅ WOF V4.9.6 先观察后行动/漏判护栏版启动');",'startup')
rep(
"qlog('🟫 主动攻击护栏: ATTACK!=0 的敌人增加350ms WATCH-only运动护栏；不参与UP/DOWN/AB，也不进入FP校准');",
"qlog('🟫 主动攻击护栏: ATTACK!=0 扩为450ms WATCH-only运动护栏；不参与UP/DOWN/AB，也不进入FP校准');\n  qlog('🧪 先观察后行动: active source需累计2次真实命中证据才允许驱动UP/DOWN/AB；此前只保留WATCH');\n  qlog('📈 WATCH学习: 已知active Family在稳定WATCH下真实掉血会积累命中证据，不需要先冒险发动作建议');",
'startup observe-first info')

p.write_text(s,encoding='utf-8')
print('patched V4.9.6',len(s))
