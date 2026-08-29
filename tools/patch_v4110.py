from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.10.1" not in s:
    raise SystemExit('expected V4.10.1 input')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,count)

# V4.11.0 is deliberately diagnostic-only. Prediction geometry, Family selection,
# action decisions, guards, debounce and calibration thresholds are unchanged.
# It separates natural-player behavior from model/runtime evidence so blind spectator
# tests are less likely to be misread as model regressions/improvements.

rep(
"""  const ST={P1:{k:'',n:0,v:null},P2:{k:'',n:0,v:null},P3:{k:'',n:0,v:null}},PRINT={P1:'',P2:'',P3:''};""",
"""  const ST={P1:{k:'',n:0,v:null},P2:{k:'',n:0,v:null},P3:{k:'',n:0,v:null}},PRINT={P1:'',P2:'',P3:''};
  const DECISION_TICKS={
    P1:{NONE:0,SAFE:0,WATCH:0,UP:0,DOWN:0,AB:0},
    P2:{NONE:0,SAFE:0,WATCH:0,UP:0,DOWN:0,AB:0},
    P3:{NONE:0,SAFE:0,WATCH:0,UP:0,DOWN:0,AB:0}
  };""",
'decision tick counters')

rep(
"""function reportSnapshot(){
  return frozenCopy({at:Date.now(),audit:auditSnapshot(),auditFamilies:auditFamilies(),calibration:calibrationSnapshot()});
}
function summarySnapshot(){""",
"""function decisionLoadSnapshot(){
  const players={},total={NONE:0,SAFE:0,WATCH:0,UP:0,DOWN:0,AB:0};
  for(const n of ['P1','P2','P3']){
    const r={...DECISION_TICKS[n]};
    for(const k of Object.keys(total))total[k]+=+r[k]||0;
    const ticks=Object.values(r).reduce((a,b)=>a+(+b||0),0),warn=(r.WATCH+r.UP+r.DOWN+r.AB),act=(r.UP+r.DOWN+r.AB);
    players[n]={...r,ticks,warningTicks:warn,actionTicks:act,
      warningRate:ticks?+(warn/ticks).toFixed(3):null,
      actionRate:ticks?+(act/ticks).toFixed(3):null,
      watchRate:ticks?+(r.WATCH/ticks).toFixed(3):null};
  }
  const ticks=Object.values(total).reduce((a,b)=>a+(+b||0),0),warn=(total.WATCH+total.UP+total.DOWN+total.AB),act=(total.UP+total.DOWN+total.AB);
  return {players,total:{...total,ticks,warningTicks:warn,actionTicks:act,
    warningRate:ticks?+(warn/ticks).toFixed(3):null,
    actionRate:ticks?+(act/ticks).toFixed(3):null,
    watchRate:ticks?+(total.WATCH/ticks).toFixed(3):null}};
}
function reportSnapshot(){
  return frozenCopy({at:Date.now(),audit:auditSnapshot(),auditFamilies:auditFamilies(),calibration:calibrationSnapshot(),decisionLoad:decisionLoadSnapshot()});
}
function summarySnapshot(){""",
'decision load snapshot')

rep(
"""  const validated=total.hit+total.falsePositive;
  const damageEvents=total.hit+total.ambiguousDamage+total.watchCovered+total.unstableCovered+total.safeMiss;
  const metrics={actionPrecision:validated?+(total.hit/validated).toFixed(3):null,""",
"""  const validated=total.hit+total.falsePositive;
  const damageEvents=total.hit+total.ambiguousDamage+total.watchCovered+total.unstableCovered+total.safeMiss;
  // Route-independent bookkeeping: `changed` is not treated as an FP. It means the
  // predicted attack branch materialized, but this uninformed spectator player naturally
  // deviated from the frozen continuation path before due time.
  const routeIndependentCompleted=total.hit+total.changed+total.enemyChanged+total.revoked+total.falsePositive+total.weakFalsePositive;
  const materializedPredictions=total.hit+total.changed+total.falsePositive+total.weakFalsePositive;
  const unchangedValidated=total.hit+total.falsePositive;
  const playerProfiles=['P1','P2','P3'].map(n=>{
    const x=a[n]||{},materialized=(+x.hit||0)+(+x.changed||0)+(+x.falsePositive||0)+(+x.weakFalsePositive||0);
    const completed=materialized+(+x.enemyChanged||0)+(+x.revoked||0);
    const dmg=(+x.hit||0)+(+x.ambiguousDamage||0)+(+x.watchCovered||0)+(+x.unstableCovered||0)+(+x.safeMiss||0);
    return {player:n,completed,materializedPredictions:materialized,
      materializationRate:completed?+(materialized/completed).toFixed(3):null,
      naturalPathChangeRate:materialized?+((+x.changed||0)/materialized).toFixed(3):null,
      unchangedValidated:(+x.hit||0)+(+x.falsePositive||0),damageEvents:dmg,safeMiss:+x.safeMiss||0};
  });
  const evaluation={
    mode:'blind-spectator-diagnostic',
    routeIndependentCompleted,materializedPredictions,
    materializationRate:routeIndependentCompleted?+(materializedPredictions/routeIndependentCompleted).toFixed(3):null,
    naturalPathChangeRate:materializedPredictions?+(total.changed/materializedPredictions).toFixed(3):null,
    unchangedValidated,
    unchangedPrecision:unchangedValidated?+(total.hit/unchangedValidated).toFixed(3):null,
    playerProfiles,
    decisionLoad:decisionLoadSnapshot()
  };
  const metrics={actionPrecision:validated?+(total.hit/validated).toFixed(3):null,""",
'route independent evaluation')

rep(
"""  return frozenCopy({at:Date.now(),total,metrics,phaseRelocks:PHASE_RELOCKS,phaseRelockTop,missAttackTop,missTop,players:a,topFalse,demoted,precisionSuppressed,geoAdjusted,geoClasses});""",
"""  return frozenCopy({at:Date.now(),total,metrics,evaluation,phaseRelocks:PHASE_RELOCKS,phaseRelockTop,missAttackTop,missTop,players:a,topFalse,demoted,precisionSuppressed,geoAdjusted,geoClasses});""",
'summary evaluation output')

rep(
"""    const raw=decision(ps,d.danger),st=stable(p.name,raw);
    last.players[p.name]={raw,stable:st,state:{...ps}};""",
"""    const raw=decision(ps,d.danger),st=stable(p.name,raw);
    const da=st?actionOf(st):'NONE';if(DECISION_TICKS[p.name]&&DECISION_TICKS[p.name][da]!=null)DECISION_TICKS[p.name][da]++;
    last.players[p.name]={raw,stable:st,state:{...ps}};""",
'decision tick accounting')

rep(
"""    summary(){return summarySnapshot();},
    misses(){return frozenCopy(MISS_CASES.slice());},""",
"""    summary(){return summarySnapshot();},
    evaluation(){return frozenCopy(summarySnapshot().evaluation);},
    decisionLoad(){return frozenCopy(decisionLoadSnapshot());},
    misses(){return frozenCopy(MISS_CASES.slice());},""",
'public diagnostic api')

rep("version:'offline-dynamic-spectator-calibrated-v4.10.1'","version:'offline-dynamic-spectator-calibrated-v4.11.0'",'version')
rep("qlog('✅ WOF V4.10.1 非破坏式阶段叠加/覆盖回归修复版启动');","qlog('✅ WOF V4.11.0 盲测评估/玩家水平拆分版启动');",'startup')
rep(
"""  qlog('🧪 验证: 🎯命中 / 🟡路径改变 / 🟤分支改变 / 🔵预测撤销 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判');""",
"""  qlog('🧪 验证: 🎯命中 / 🟡路径改变 / 🟤分支改变 / 🔵预测撤销 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判');
  qlog('🧊 V4.11.0只增加盲测诊断，不修改Family/轨迹/范围/护栏/稳定器/行动门槛；V4.10.1已冻结为baseline-v4.10.1');
  qlog('👤 玩家水平拆分: changed单列为自然路径改变；reportShort().evaluation同时报告攻击materialization与玩家路径改变率，不再把高手/普通玩家混成一个精度数字');
  qlog('🖥️ 提示负担: reportShort().evaluation.decisionLoad统计SAFE/WATCH/UP/DOWN/AB时间占比，防止为了覆盖率把最终HUD调成满屏警告');""",
'evaluation startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.11.0',len(s))
