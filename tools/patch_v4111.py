from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.11.0" not in s:
    raise SystemExit('expected V4.11.0 input')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,count)

# V4.11.1 remains diagnostic-only for prediction behavior. The 6-room blind run
# exposed two evaluator problems: HP changes with no enemy evidence were being counted
# as SAFE misses, and miss forensics were capped at only 16 cases. Separate those
# events without widening/narrowing any prediction geometry or action thresholds.

rep(
"""    missCandidateLimit:5,
    shadowHorizonMs:350,""",
"""    missCandidateLimit:5,
    maxPlausibleHp:128,
    shadowHorizonMs:350,""",
'plausible hp cfg')

rep(
"""MISS_CASES.push(c);if(MISS_CASES.length>16)MISS_CASES.shift();""",
"""MISS_CASES.push(c);if(MISS_CASES.length>120)MISS_CASES.shift();""",
'miss forensic retention')

old_stats="tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,tailCovered:0,bridgeCovered:0,watchPromoted:0,unstableCovered:0,safeMiss:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0"
new_stats="tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,tailCovered:0,bridgeCovered:0,watchPromoted:0,unstableCovered:0,safeMiss:0,nonEnemyDamage:0,hpBaselineReset:0,protectedIgnored:0,deathEvents:0,respawnEvents:0,absentEvents:0,returnEvents:0"
if s.count(old_stats)<4:
    raise SystemExit('unexpected stats occurrences')
s=s.replace(old_stats,new_stats)

# HP values above normal player HP appear during object/state transitions. Rebuild the
# audit baseline instead of treating the downward normalization as combat damage.
rep(
"""  const hpBefore=A.prevHp;
  const dropped=hpBefore!=null&&hp<hpBefore;
  if(dropped){""",
"""  const hpBefore=A.prevHp;
  const dropped=hpBefore!=null&&hp<hpBefore;
  if(dropped&&hpBefore>CFG.maxPlausibleHp){
    A.stats.hpBaselineReset++;
    if(A.pending)A.pending=null;
    A.prevHp=hp;
    qlog('⚪',name,'HP异常基线重建/不计伤害',hpBefore+'→'+hp);
    return;
  }
  if(dropped){""",
'hp baseline reset')

# No-warning damage with literally no enemy actor evidence in the preceding history
# is kept as forensic data, but excluded from enemy-attack SAFE-miss coverage. This is
# intentionally named nonEnemyDamage rather than discarded because it may later reveal
# environmental hazards/projectiles outside the current enemy pool.
rep(
"""    }else{
      A.stats.safeMiss++;
      const mc=captureMissCase('safeMiss',name,ps,raw,now,hpBefore,hp);
      qlog('❌',name,'真实SAFE漏判','HP '+hpBefore+'→'+hp,'case#'+mc.id,
        '候选',mc.candidates.slice(0,3).map(x=>'s'+x.slot+'/T'+x.type+'/A'+x.attack+'/'+(x.locked||'?')).join(' '));
    }""",
"""    }else{
      const mc=captureMissCase('safeMiss',name,ps,raw,now,hpBefore,hp);
      const noEnemyEvidence=!mc.rawHit&&!mc.nearest&&(!mc.candidates||mc.candidates.length===0);
      if(noEnemyEvidence){
        mc.kind='nonEnemyDamage';A.stats.nonEnemyDamage++;
        qlog('⚪',name,'无敌方证据掉血/暂不计SAFE漏判','HP '+hpBefore+'→'+hp,'case#'+mc.id);
      }else{
        A.stats.safeMiss++;
        qlog('❌',name,'真实SAFE漏判','HP '+hpBefore+'→'+hp,'case#'+mc.id,
          '候选',mc.candidates.slice(0,3).map(x=>'s'+x.slot+'/T'+x.type+'/A'+x.attack+'/'+(x.locked||'?')).join(' '));
      }
    }""",
'non enemy damage split')

# Surface these diagnostic buckets in per-player evaluation without mixing them into
# damage coverage denominators.
rep(
"""      unchangedValidated:(+x.hit||0)+(+x.falsePositive||0),damageEvents:dmg,safeMiss:+x.safeMiss||0};""",
"""      unchangedValidated:(+x.hit||0)+(+x.falsePositive||0),damageEvents:dmg,safeMiss:+x.safeMiss||0,
      nonEnemyDamage:+x.nonEnemyDamage||0,hpBaselineReset:+x.hpBaselineReset||0};""",
'player diagnostic fields')

# Tag phase-overlay WATCH separately so warning-source accounting doesn't call it edge.
rep(
"""      const tailWatch=gh.source==='attack-tail-guard'||!!gh.tailGuard;
      const guardWatch=tailWatch||gh.source==='active-guard'||!!gh.guardWatch;
      const geometryWatch=!guardWatch&&!!gh.geometryFallback;
      return{danger:true,watchOnly:true,guardWatchOnly:guardWatch,tailWatchOnly:tailWatch,geometryWatchOnly:geometryWatch,edgeWatchOnly:!guardWatch&&!geometryWatch,""",
"""      const tailWatch=gh.source==='attack-tail-guard'||!!gh.tailGuard;
      const guardWatch=tailWatch||gh.source==='active-guard'||!!gh.guardWatch;
      const phaseWatch=gh.source==='active-phase-watch'||!!gh.phaseWatch;
      const geometryWatch=!guardWatch&&!phaseWatch&&!!gh.geometryFallback;
      return{danger:true,watchOnly:true,guardWatchOnly:guardWatch,tailWatchOnly:tailWatch,phaseWatchOnly:phaseWatch,geometryWatchOnly:geometryWatch,edgeWatchOnly:!guardWatch&&!phaseWatch&&!geometryWatch,""",
'phase watch diagnostic tag')

# Add warning-source load counters; decision behavior is untouched.
rep(
"""  const DECISION_TICKS={
    P1:{NONE:0,SAFE:0,WATCH:0,UP:0,DOWN:0,AB:0},
    P2:{NONE:0,SAFE:0,WATCH:0,UP:0,DOWN:0,AB:0},
    P3:{NONE:0,SAFE:0,WATCH:0,UP:0,DOWN:0,AB:0}
  };""",
"""  const DECISION_TICKS={
    P1:{NONE:0,SAFE:0,WATCH:0,UP:0,DOWN:0,AB:0},
    P2:{NONE:0,SAFE:0,WATCH:0,UP:0,DOWN:0,AB:0},
    P3:{NONE:0,SAFE:0,WATCH:0,UP:0,DOWN:0,AB:0}
  };
  const WARNING_SOURCE_TICKS={
    P1:{ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0},
    P2:{ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0},
    P3:{ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0}
  };""",
'warning source counters')

rep(
"""  return {players,total:{...total,ticks,warningTicks:warn,actionTicks:act,
    warningRate:ticks?+(warn/ticks).toFixed(3):null,
    actionRate:ticks?+(act/ticks).toFixed(3):null,
    watchRate:ticks?+(total.WATCH/ticks).toFixed(3):null}};
}""",
"""  const warningSources={ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0};
  const warningSourcePlayers={};
  for(const n of ['P1','P2','P3']){
    const r={...WARNING_SOURCE_TICKS[n]};warningSourcePlayers[n]=r;
    for(const k of Object.keys(warningSources))warningSources[k]+=+r[k]||0;
  }
  const sourceTotal=Object.values(warningSources).reduce((a,b)=>a+(+b||0),0);
  const sourceRates={};for(const k of Object.keys(warningSources))sourceRates[k]=sourceTotal?+(warningSources[k]/sourceTotal).toFixed(3):null;
  return {players,total:{...total,ticks,warningTicks:warn,actionTicks:act,
    warningRate:ticks?+(warn/ticks).toFixed(3):null,
    actionRate:ticks?+(act/ticks).toFixed(3):null,
    watchRate:ticks?+(total.WATCH/ticks).toFixed(3):null},
    warningSourcePlayers,warningSources,warningSourceRates:sourceRates};
}""",
'warning source snapshot')

rep(
"""    const raw=decision(ps,d.danger),st=stable(p.name,raw);
    const da=st?actionOf(st):'NONE';if(DECISION_TICKS[p.name]&&DECISION_TICKS[p.name][da]!=null)DECISION_TICKS[p.name][da]++;
    last.players[p.name]={raw,stable:st,state:{...ps}};""",
"""    const raw=decision(ps,d.danger),st=stable(p.name,raw);
    const da=st?actionOf(st):'NONE';if(DECISION_TICKS[p.name]&&DECISION_TICKS[p.name][da]!=null)DECISION_TICKS[p.name][da]++;
    if(st&&da!=='SAFE'&&da!=='NONE'){
      const src=(da==='UP'||da==='DOWN'||da==='AB')?'ACTION':
        st.tailWatchOnly?'TAIL':st.guardWatchOnly?'GUARD':st.shadowWatchOnly?'SHADOW':st.debounceWatchOnly?'BRIDGE':
        st.phaseWatchOnly?'PHASE':st.geometryWatchOnly?'GEOMETRY':st.edgeWatchOnly?'EDGE':'WATCH';
      if(WARNING_SOURCE_TICKS[p.name]?.[src]!=null)WARNING_SOURCE_TICKS[p.name][src]++;
    }
    last.players[p.name]={raw,stable:st,state:{...ps}};""",
'warning source accounting')

rep("version:'offline-dynamic-spectator-calibrated-v4.11.0'","version:'offline-dynamic-spectator-calibrated-v4.11.1'",'version')
rep("qlog('✅ WOF V4.11.0 盲测评估/玩家水平拆分版启动');","qlog('✅ WOF V4.11.1 多房间审计去污染/警告负担拆分版启动');",'startup')
rep(
"""  qlog('🧊 V4.11.0只增加盲测诊断，不修改Family/轨迹/范围/护栏/稳定器/行动门槛；V4.10.1已冻结为baseline-v4.10.1');""",
"""  qlog('🧊 V4.11.1仍不修改Family/轨迹/范围/护栏/稳定器/行动门槛；只修审计污染并拆分警告来源；V4.10.1仍为冻结基线');
  qlog('🧹 审计去污染: HP异常基线重建与最近600ms完全无敌方证据的掉血单独统计，不再自动算enemy SAFE漏判');
  qlog('📚 漏判取证: MISS_CASES由16扩到120，适配多房间10分钟批量测试');
  qlog('📊 警告来源: decisionLoad.warningSources拆分ACTION/GUARD/TAIL/SHADOW/BRIDGE/PHASE/GEOMETRY/EDGE/WATCH');""",
'startup diagnostics')

p.write_text(s,encoding='utf-8')
print('patched V4.11.1',len(s))
