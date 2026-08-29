from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.9.3" not in s:
    raise SystemExit('expected V4.9.3 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,1)

rep(
"""    shadowHorizonMs:350,
    shadowRadiusScale:1.18,
    fallbackZThreshold:80,""",
"""    shadowHorizonMs:350,
    shadowRadiusScale:1.18,
    postDamageGuardMs:700,
    respawnGuardMs:1500,
    fallbackZThreshold:80,""",
'guard cfg')

rep(
"""    const A=AUD?.[name];if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;A.lastRawWarnAt=-1e9;A.lastShadowWarnAt=-1e9;A.lastShadowRawAt=-1e9;A.recent={};}""",
"""    const A=AUD?.[name];if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;A.lastRawWarnAt=-1e9;A.lastShadowWarnAt=-1e9;A.lastShadowRawAt=-1e9;A.recent={};A.dead=false;A.absent=false;A.suppressUntil=-1e9;A.lastDamageAt=-1e9;}""",
'reset guard state')

old_aud="""const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0},byFamily:{}}
};"""
new_aud="""const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,dead:false,absent:false,suppressUntil:-1e9,lastDamageAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0},byFamily:{}}
};"""
rep(old_aud,new_aud,'AUD guard fields')

rep(
"""function auditResolve(name,kind,e,extra=''){
  const A=AUD[name]; if(!e)return;""",
"""function auditGuard(name,e,reason){
  const A=AUD[name];if(!A||!e)return;
  A.stats.protectedIgnored++;
  qlog('🛡️',name,'受击/死亡保护期：忽略本次FP审计',e.action,e.family||'?',e.source||'?',reason||'');
  A.pending=null;
}

function auditMarkAbsent(name,now){
  const A=AUD[name];if(!A)return;
  if(!A.absent){
    A.absent=true;A.dead=true;
    if(A.pending)auditGuard(name,A.pending,'玩家对象暂时消失/死亡');
    qlog('⚰️',name,'玩家对象消失：暂停命中/误报审计');
  }
  A.prevHp=null;
  A.suppressUntil=Math.max(A.suppressUntil||-1e9,now+CFG.respawnGuardMs);
}

function auditResolve(name,kind,e,extra=''){
  const A=AUD[name]; if(!e)return;""",
'guard helper functions')

old_step_head="""function auditStep(name,ps,st,raw,now){
  const A=AUD[name],action=st?actionOf(st):null,rawAction=raw?actionOf(raw):null;
  if(rawAction&&rawAction!=='SAFE')A.lastRawWarnAt=now;
  if(raw?.shadowWatchOnly)A.lastShadowRawAt=now;
  const hp=ps.hp;
  const e=A.pending;
  if(e)trackEnemy(e,now);

  const dropped=A.prevHp!=null&&hp<A.prevHp;
  if(dropped){"""
new_step_head="""function auditStep(name,ps,st,raw,now){
  const A=AUD[name],action=st?actionOf(st):null,rawAction=raw?actionOf(raw):null;
  if(rawAction&&rawAction!=='SAFE')A.lastRawWarnAt=now;
  if(raw?.shadowWatchOnly)A.lastShadowRawAt=now;
  const hp=ps.hp;

  // Return from death/absence: clear stale audit state and wait through respawn invulnerability.
  if((A.dead||A.absent)&&hp>0){
    if(A.pending)auditGuard(name,A.pending,'复活/重新出现');
    A.dead=false;A.absent=false;A.prevHp=hp;A.suppressUntil=now+CFG.respawnGuardMs;A.stats.respawnEvents++;
    A.lastWarnAt=A.lastRawWarnAt=A.lastShadowWarnAt=A.lastShadowRawAt=-1e9;
    qlog('♻️',name,'复活/重新出现：'+CFG.respawnGuardMs+'ms内暂停FP审计');
    return;
  }
  if(A.prevHp==null&&hp<=0){A.dead=true;A.prevHp=hp;return;}
  if(A.dead&&hp<=0){A.prevHp=hp;if(A.pending)auditGuard(name,A.pending,'HP=0/死亡中');return;}

  const e=A.pending;
  if(e)trackEnemy(e,now);

  const hpBefore=A.prevHp;
  const dropped=hpBefore!=null&&hp<hpBefore;
  if(dropped){"""
rep(old_step_head,new_step_head,'auditStep head')

# Replace references to A.prevHp within the dropped branch with stable hpBefore text only where messages are formed.
# The logic remains identical, then enters a protection window after any real damage.
start=s.index('  const hpBefore=A.prevHp;')
end=s.index('  A.prevHp=hp;', start)
chunk=s[start:end]
chunk=chunk.replace("'预测已撤销后发生 HP '+A.prevHp+'→'+hp", "'预测已撤销后发生 HP '+hpBefore+'→'+hp")
chunk=chunk.replace("'HP '+A.prevHp+'→'+hp", "'HP '+hpBefore+'→'+hp")
chunk=chunk.replace("captureMissCase('unstableCovered',name,ps,raw,now,A.prevHp,hp)", "captureMissCase('unstableCovered',name,ps,raw,now,hpBefore,hp)")
chunk=chunk.replace("captureMissCase('safeMiss',name,ps,raw,now,A.prevHp,hp)", "captureMissCase('safeMiss',name,ps,raw,now,hpBefore,hp)")
s=s[:start]+chunk+s[end:]

rep(
"""  A.prevHp=hp;

  const q=A.pending;""",
"""  if(dropped){
    A.lastDamageAt=now;
    A.suppressUntil=Math.max(A.suppressUntil||-1e9,now+CFG.postDamageGuardMs);
    // A different/overlapping attack may already be pending. Do not turn post-hit invulnerability into a false positive.
    if(A.pending&&A.pending===e)auditGuard(name,A.pending,'刚受击 '+CFG.postDamageGuardMs+'ms保护');
  }
  A.prevHp=hp;

  if(hp<=0){
    if(!A.dead){A.dead=true;A.stats.deathEvents++;qlog('⚰️',name,'HP=0：死亡期间暂停审计');}
    if(A.pending)auditGuard(name,A.pending,'HP=0/死亡中');
    return;
  }

  // During hit-stun / knockdown / respawn protection, keep predictions running but do not create or resolve FP audits.
  if(now<(A.suppressUntil||-1e9)){
    if(A.pending)auditGuard(name,A.pending,'保护期剩余 '+Math.max(0,Math.round(A.suppressUntil-now))+'ms');
    return;
  }

  const q=A.pending;""",
'post damage/death guard')

rep(
"""  for(const n of ['P1','P2','P3'])out[n]={...AUD[n].stats,pending:AUD[n].pending?{
    action:AUD[n].pending.action,family:AUD[n].pending.family,hitMs:AUD[n].pending.hitMs,source:AUD[n].pending.source,variant:AUD[n].pending.variant,
    slot:AUD[n].pending.slot,instance:AUD[n].pending.instance,familySeen:AUD[n].pending.familySeen}:null};""",
"""  for(const n of ['P1','P2','P3'])out[n]={...AUD[n].stats,dead:!!AUD[n].dead,protected:!!AUD[n].dead||performance.now()<(AUD[n].suppressUntil||-1e9),
    protectMs:Math.max(0,Math.round((AUD[n].suppressUntil||-1e9)-performance.now())),pending:AUD[n].pending?{
    action:AUD[n].pending.action,family:AUD[n].pending.family,hitMs:AUD[n].pending.hitMs,source:AUD[n].pending.source,variant:AUD[n].pending.variant,
    slot:AUD[n].pending.slot,instance:AUD[n].pending.instance,familySeen:AUD[n].pending.familySeen}:null};""",
'audit snapshot protection')

rep(
"""  const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0};""",
"""  const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0};""",
'total protection stats')

rep(
"""  for(const p of PLAYERS){
    const ps=PS[p.name];if(!ps)continue;
    const raw=decision(ps,d.danger),st=stable(p.name,raw);""",
"""  for(const p of PLAYERS){
    const ps=PS[p.name];if(!ps){auditMarkAbsent(p.name,now);continue;}
    const raw=decision(ps,d.danger),st=stable(p.name,raw);""",
'tick absent audit')

rep("version:'offline-dynamic-spectator-calibrated-v4.9.3'","version:'offline-dynamic-spectator-calibrated-v4.9.4'",'version')
rep("qlog('✅ WOF V4.9.3 安全影子恢复观战版启动');","qlog('✅ WOF V4.9.4 死亡/受击保护审计版启动');",'startup')
rep(
"qlog('🟨 安全影子: 完整危险壳外再加18%短时WATCH halo，仅预警不参与UP/DOWN/AB，也不计误报校准');",
"qlog('🟨 安全影子: 完整危险壳外再加18%短时WATCH halo，仅预警不参与UP/DOWN/AB，也不计误报校准');\n  qlog('🛡️ 审计保护: 掉血后'+CFG.postDamageGuardMs+'ms、死亡/对象消失、复活后'+CFG.respawnGuardMs+'ms不允许产生FP；真实掉血事件仍正常统计');",
'startup guard info')

p.write_text(s,encoding='utf-8')
print('patched V4.9.4',len(s))
