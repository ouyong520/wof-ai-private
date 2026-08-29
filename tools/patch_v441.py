from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')

if "offline-dynamic-spectator-calibrated-v4.4" not in s:
    raise SystemExit('expected V4.4 input')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} patch target missing')
    s=s.replace(old,new,1)

# 1) Prevent one long ACTIVE attack from being audited repeatedly as several false positives.
replace_once(
"""    survivalActionThreshold:0.35,
    auditRevokeLeadMs:60,
    padX:3,""",
"""    survivalActionThreshold:0.35,
    auditRevokeLeadMs:60,
    auditRepeatBlockMs:700,
    padX:3,""",
'CFG audit repeat block')

replace_once(
"const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0}));",
"const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0,seq:0}));",
'SLOT seq')
replace_once(
"if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;}",
"if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.seq=0;}",
'SLOT type reset')
replace_once(
"""    if(s.prevAttack===0&&o.attack!==0){
      s.locked=DB.a[keyActive(o)]||UNIQUE_ACTIVE.get(o.type+'|'+o.attack)||null;
      s.started=now;s.origin={x:o.x,y:o.y,z:o.z};s.face=o.face;""",
"""    if(s.prevAttack===0&&o.attack!==0){
      s.seq=(s.seq||0)+1;
      s.locked=DB.a[keyActive(o)]||UNIQUE_ACTIVE.get(o.type+'|'+o.attack)||null;
      s.started=now;s.origin={x:o.x,y:o.y,z:o.z};s.face=o.face;""",
'ACTIVE sequence increment')

replace_once(
"""            calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
            calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),source:'startup',lookup:hit.kind});""",
"""            calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
            calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),
            instance:'S:'+o.slot+':'+o.type+':'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3+':'+fc.id,
            source:'startup',lookup:hit.kind});""",
'startup instance id')
replace_once(
"""        calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
        calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),source:'active'});""",
"""        calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
        calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),
        instance:'A:'+o.slot+':'+o.type+':'+s.seq+':'+Math.round(s.started),source:'active'});""",
'active instance id')

# 2) Global Family demotion now needs evidence from at least two distinct players.
replace_once(
"""  const CAL_CFG={
    sourceDemoteConfirmed:6,sourceDemoteFp:5,sourceDemotePrecision:.25,
    sourceRecoverConfirmed:10,sourceRecoverHit:4,sourceRecoverPrecision:.50,
    familyDemoteConfirmed:10,familyDemoteFp:7,familyDemotePrecision:.30,""",
"""  const CAL_CFG={
    sourceDemoteConfirmed:6,sourceDemoteFp:5,sourceDemoteFpPlayers:2,sourceDemotePrecision:.25,
    sourceRecoverConfirmed:10,sourceRecoverHit:4,sourceRecoverPrecision:.50,
    familyDemoteConfirmed:10,familyDemoteFp:7,familyDemoteFpPlayers:2,familyDemotePrecision:.30,""",
'CAL distinct player thresholds')
replace_once(
"function calBucket(map,key){return map[key]||(map[key]={hit:0,fp:0,ignoredFp:0,confirmed:0,precision:null,watchOnly:false,demotions:0,recoveries:0});}",
"function calBucket(map,key){return map[key]||(map[key]={hit:0,fp:0,ignoredFp:0,confirmed:0,precision:null,watchOnly:false,demotions:0,recoveries:0,hitPlayers:{},fpPlayers:{}});}",
'CAL bucket players')
replace_once(
"""    if(!was){
      if(scope==='source')b.watchOnly=b.confirmed>=CAL_CFG.sourceDemoteConfirmed&&b.fp>=CAL_CFG.sourceDemoteFp&&b.precision<=CAL_CFG.sourceDemotePrecision;
      else b.watchOnly=b.confirmed>=CAL_CFG.familyDemoteConfirmed&&b.fp>=CAL_CFG.familyDemoteFp&&b.precision<=CAL_CFG.familyDemotePrecision;""",
"""    if(!was){
      const fpPlayers=Object.keys(b.fpPlayers||{}).length;
      if(scope==='source')b.watchOnly=b.confirmed>=CAL_CFG.sourceDemoteConfirmed&&b.fp>=CAL_CFG.sourceDemoteFp&&fpPlayers>=CAL_CFG.sourceDemoteFpPlayers&&b.precision<=CAL_CFG.sourceDemotePrecision;
      else b.watchOnly=b.confirmed>=CAL_CFG.familyDemoteConfirmed&&b.fp>=CAL_CFG.familyDemoteFp&&fpPlayers>=CAL_CFG.familyDemoteFpPlayers&&b.precision<=CAL_CFG.familyDemotePrecision;""",
'CAL demote distinct players')
replace_once(
"""    for(const b of [fb,sb]){if(kind==='hit')b.hit++;else b.fp++;}
    const sf=calRefresh(sb,'source'),ff=calRefresh(fb,'family'),after=calPolicy(family,source).watchOnly;""",
"""    const who=e.player||'?';
    for(const b of [fb,sb]){
      if(kind==='hit'){b.hit++;b.hitPlayers[who]=1;}
      else{b.fp++;b.fpPlayers[who]=1;}
    }
    const sf=calRefresh(sb,'source'),ff=calRefresh(fb,'family'),after=calPolicy(family,source).watchOnly;""",
'CAL record player evidence')
replace_once(
"""    return Object.entries(map).map(([key,v])=>({scope,key,hit:v.hit,fp:v.fp,ignoredFp:v.ignoredFp,confirmed:v.confirmed,
      precision:v.precision,watchOnly:v.watchOnly,demotions:v.demotions,recoveries:v.recoveries}))""",
"""    return Object.entries(map).map(([key,v])=>({scope,key,hit:v.hit,fp:v.fp,ignoredFp:v.ignoredFp,confirmed:v.confirmed,
      hitPlayers:Object.keys(v.hitPlayers||{}).length,fpPlayers:Object.keys(v.fpPlayers||{}).length,
      precision:v.precision,watchOnly:v.watchOnly,demotions:v.demotions,recoveries:v.recoveries}))""",
'CAL snapshot player counts')

# 3) Per-player audit de-duplication by attack instance / startup state.
replace_once(
"if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;}",
"if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;A.recent={};}",
'reset audit recent')
replace_once(
"""  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}}""",
"""  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}}""",
'AUD recent maps')
replace_once(
"""  }
  A.pending=null;
}

function auditStep(name,ps,st,now){""",
"""  }
  if(e.auditKey)A.recent[e.auditKey]=performance.now();
  A.pending=null;
}

function auditStep(name,ps,st,now){""",
'mark resolved audit key')
replace_once(
"""    const hitMs=Math.max(CFG.reactFloorMs,+st.hitMs||0);
    const pp=playerAt(ps,'CONTINUE',hitMs,0);
    const rx=+h.rx||0,ry=+h.ry||0,rz=+h.rz||0;
    A.pending={action,family:h.family,source:h.source||null,slot:h.slot,enemyType:h.type,""",
"""    const hitMs=Math.max(CFG.reactFloorMs,+st.hitMs||0);
    const instance=h.instance||((h.source||'?')+':'+(h.slot??-1)+':'+(h.family||'?'));
    const auditKey=(h.slot??-1)+'|'+(h.family||'?')+'|'+(h.source||'?')+'|'+instance;
    for(const [k,t] of Object.entries(A.recent))if(now-t>CFG.auditRepeatBlockMs*4)delete A.recent[k];
    if(A.recent[auditKey]!=null&&now-A.recent[auditKey]<CFG.auditRepeatBlockMs)return;
    const pp=playerAt(ps,'CONTINUE',hitMs,0);
    const rx=+h.rx||0,ry=+h.ry||0,rz=+h.rz||0;
    A.pending={player:name,action,family:h.family,source:h.source||null,slot:h.slot,enemyType:h.type,instance,auditKey,""",
'audit instance de-dup gate')
replace_once(
"""    action:AUD[n].pending.action,family:AUD[n].pending.family,hitMs:AUD[n].pending.hitMs,source:AUD[n].pending.source,
    slot:AUD[n].pending.slot,familySeen:AUD[n].pending.familySeen}:null};""",
"""    action:AUD[n].pending.action,family:AUD[n].pending.family,hitMs:AUD[n].pending.hitMs,source:AUD[n].pending.source,
    slot:AUD[n].pending.slot,instance:AUD[n].pending.instance,familySeen:AUD[n].pending.familySeen}:null};""",
'audit snapshot instance')

replace_once("version:'offline-dynamic-spectator-calibrated-v4.4'","version:'offline-dynamic-spectator-calibrated-v4.4.1'",'version')
replace_once("console.log('✅ WOF V4.4 跨玩家Family在线校准观战版启动');","console.log('✅ WOF V4.4.1 攻击实例去重校准观战版启动');",'startup version')
replace_once(
"console.log('🧯 在线校准: 多次高可信误报→WATCH；后续真实命中足够→♻️恢复行动');",
"console.log('🧯 在线校准: 同一攻击实例只记一次；全局降级需至少2名玩家共同提供误报证据');",
'calibration startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.4.1',len(s))
