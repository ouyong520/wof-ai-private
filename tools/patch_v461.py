from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.6" not in s:
    raise SystemExit('expected V4.6 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' target missing')
    s=s.replace(old,new,1)

# Make route advice use the same confidence regime as online calibration.
rep(
"""    survivalActionThreshold:0.35,
    auditRevokeLeadMs:60,""",
"""    survivalActionThreshold:0.50,
    startupActionMinConfidence:0.15,
    activeActionMinConfidence:0.50,
    auditRevokeLeadMs:60,""",
'action confidence config')

rep(
"""            confidence,survival,actionable:survival>=CFG.survivalActionThreshold&&!cal.watchOnly,""",
"""            confidence,survival,actionable:survival>=CFG.survivalActionThreshold&&confidence>=CFG.startupActionMinConfidence&&!cal.watchOnly,""",
'startup action gate')

rep(
"""        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold&&!cal.watchOnly,""",
"""        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold&&survival>=CFG.activeActionMinConfidence&&!cal.watchOnly,""",
'active action gate')

# Separate weak suspected false positives from calibration-grade false positives.
rep(
"""  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}}""",
"""  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,safeMiss:0},byFamily:{}}""",
'audit stats weak fp')

rep(
"return A.byFamily[k]||(A.byFamily[k]={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,materialized:0});",
"return A.byFamily[k]||(A.byFamily[k]={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,materialized:0});",
'family weak fp stat')

rep(
"""  }else if(kind==='fp'){
    A.stats.falsePositive++;F.falsePositive++;calRecord(e,'fp');
    qlog('🔴',name,'高可信疑似误报',e.action,e.family||'?',e.source||'?',e.hitMs+'ms','slot',e.slot,geoText(e),
      '玩家路线未明显改变且目标攻击已成立但未掉血',extra);
  }""",
"""  }else if(kind==='fp'){
    if(calFpEligible(e)){
      A.stats.falsePositive++;F.falsePositive++;calRecord(e,'fp');
      qlog('🔴',name,'高可信疑似误报',e.action,e.family||'?',e.source||'?',e.hitMs+'ms','slot',e.slot,geoText(e),
        '玩家路线未明显改变且目标攻击已成立但未掉血',extra);
    }else{
      A.stats.weakFalsePositive++;F.weakFalsePositive++;
      qlog('🟡',name,'低置信疑似误报/不计校准',e.action,e.family||'?',e.source||'?',e.hitMs+'ms','slot',e.slot,geoText(e),extra);
    }
  }""",
'audit fp tiers')

rep(
"""  for(const n of ['P1','P2','P3'])out[n]=Object.entries(AUD[n].byFamily).map(([family,v])=>({family,...v,
    precision:(v.hit+v.falsePositive)?v.hit/(v.hit+v.falsePositive):null,
    confirmed:v.hit+v.falsePositive})).sort((a,b)=>(b.falsePositive-a.falsePositive)||(b.confirmed-a.confirmed)||(b.tested-a.tested));""",
"""  for(const n of ['P1','P2','P3'])out[n]=Object.entries(AUD[n].byFamily).map(([family,v])=>({family,...v,
    precision:(v.hit+v.falsePositive)?v.hit/(v.hit+v.falsePositive):null,
    confirmed:v.hit+v.falsePositive})).sort((a,b)=>(b.falsePositive-a.falsePositive)||(b.weakFalsePositive-a.weakFalsePositive)||(b.confirmed-a.confirmed)||(b.tested-a.tested));""",
'family report sort')

rep("version:'offline-dynamic-spectator-calibrated-v4.6'","version:'offline-dynamic-spectator-calibrated-v4.6.1'",'version')
rep("qlog('✅ WOF V4.6 双层XYZ几何观战版启动');","qlog('✅ WOF V4.6.1 置信度分层观战版启动');",'startup')
rep(
"qlog('🧯 在线校准: 同一攻击实例只记一次；全局降级需至少2名玩家共同提供误报证据');",
"qlog('🧯 在线校准: 红色=可进入校准的高可信误报；黄色=低置信误报，仅WATCH/统计，不处罚Family');\n  qlog('🎚️ 行动门槛: startup conf>='+CFG.startupActionMinConfidence+'；active survival>='+CFG.activeActionMinConfidence);",
'confidence startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.6.1',len(s))
