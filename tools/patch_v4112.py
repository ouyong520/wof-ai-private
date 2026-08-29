from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.11.1" not in s:
    raise SystemExit('expected V4.11.1 input')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,count)

# V4.11.2 is still diagnostic-only. The 7-room V4.11.1 run showed that stable
# warning time is dominated by GUARD/GEOMETRY, while actual action advice is rare.
# Before changing prediction or HUD behavior, attribute real HP drops to the warning
# sources that were present in the preceding 350ms. This tells us which broad WATCH
# layers are actually necessary versus merely noisy/redundant.

rep(
"""  const WARNING_SOURCE_TICKS={
    P1:{ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0},
    P2:{ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0},
    P3:{ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0}
  };""",
"""  const WARNING_SOURCE_TICKS={
    P1:{ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0},
    P2:{ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0},
    P3:{ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0}
  };
  const WARN_HISTORY={P1:[],P2:[],P3:[]};
  const blankWarningSources=()=>({ACTION:0,GUARD:0,TAIL:0,SHADOW:0,BRIDGE:0,PHASE:0,GEOMETRY:0,EDGE:0,WATCH:0});
  const DAMAGE_WARNING={
    hpDrops:0,withStableWarning:0,noStableWarning:0,
    latest:blankWarningSources(),any:blankWarningSources(),exclusive:blankWarningSources(),
    leadSumMs:0,leadCount:0,leadBuckets:{lte100:0,ms101_200:0,ms201_350:0},
    players:{P1:{hpDrops:0,withStableWarning:0,noStableWarning:0},P2:{hpDrops:0,withStableWarning:0,noStableWarning:0},P3:{hpDrops:0,withStableWarning:0,noStableWarning:0}}
  };
  function warningSourceOf(st,da){
    if(!st||da==='SAFE'||da==='NONE')return null;
    return (da==='UP'||da==='DOWN'||da==='AB')?'ACTION':
      st.tailWatchOnly?'TAIL':st.guardWatchOnly?'GUARD':st.shadowWatchOnly?'SHADOW':st.debounceWatchOnly?'BRIDGE':
      st.phaseWatchOnly?'PHASE':st.geometryWatchOnly?'GEOMETRY':st.edgeWatchOnly?'EDGE':'WATCH';
  }
  function warningTelemetry(name,st,da,now){
    const h=WARN_HISTORY[name];if(!h)return null;
    while(h.length&&now-h[0].lastAt>1200)h.shift();
    const src=warningSourceOf(st,da);if(!src)return null;
    if(WARNING_SOURCE_TICKS[name]?.[src]!=null)WARNING_SOURCE_TICKS[name][src]++;
    const last=h[h.length-1];
    if(last&&last.src===src&&now-last.lastAt<=CFG.tickMs*3){
      last.lastAt=now;last.hitMs=Number.isFinite(+st?.hitMs)?+st.hitMs:last.hitMs;
    }else h.push({src,startAt:now,lastAt:now,hitMs:Number.isFinite(+st?.hitMs)?+st.hitMs:null});
    return src;
  }
  function damageWarningRecord(name,now){
    const h=(WARN_HISTORY[name]||[]).filter(x=>x.lastAt>=now-350);
    const D=DAMAGE_WARNING,P=D.players[name];D.hpDrops++;if(P)P.hpDrops++;
    if(!h.length){D.noStableWarning++;if(P)P.noStableWarning++;return;}
    D.withStableWarning++;if(P)P.withStableWarning++;
    const sources=[...new Set(h.map(x=>x.src))];for(const src of sources)if(D.any[src]!=null)D.any[src]++;
    if(sources.length===1&&D.exclusive[sources[0]]!=null)D.exclusive[sources[0]]++;
    const latest=h.reduce((a,b)=>!a||b.lastAt>a.lastAt?b:a,null);if(latest&&D.latest[latest.src]!=null)D.latest[latest.src]++;
    const earliest=Math.min(...h.map(x=>x.startAt));const lead=Math.max(0,Math.min(350,now-earliest));
    D.leadSumMs+=lead;D.leadCount++;
    if(lead<=100)D.leadBuckets.lte100++;else if(lead<=200)D.leadBuckets.ms101_200++;else D.leadBuckets.ms201_350++;
  }
  function damageWarningSnapshot(){
    const D=DAMAGE_WARNING;
    return {hpDrops:D.hpDrops,withStableWarning:D.withStableWarning,noStableWarning:D.noStableWarning,
      stableWarningCoverage:D.hpDrops?+(D.withStableWarning/D.hpDrops).toFixed(3):null,
      latest:{...D.latest},any:{...D.any},exclusive:{...D.exclusive},
      avgFirstLeadMs:D.leadCount?+(D.leadSumMs/D.leadCount).toFixed(1):null,leadBuckets:{...D.leadBuckets},
      players:{P1:{...D.players.P1},P2:{...D.players.P2},P3:{...D.players.P3}}};
  }""",
'damage warning telemetry')

rep(
"""  if(dropped){
    if(e&&now>=e.due-CFG.auditHitEarlyMs&&now<=e.deadline+120){""",
"""  if(dropped){
    damageWarningRecord(name,now);
    if(e&&now>=e.due-CFG.auditHitEarlyMs&&now<=e.deadline+120){""",
'damage warning record')

rep(
"""    if(st&&da!=='SAFE'&&da!=='NONE'){
      const src=(da==='UP'||da==='DOWN'||da==='AB')?'ACTION':
        st.tailWatchOnly?'TAIL':st.guardWatchOnly?'GUARD':st.shadowWatchOnly?'SHADOW':st.debounceWatchOnly?'BRIDGE':
        st.phaseWatchOnly?'PHASE':st.geometryWatchOnly?'GEOMETRY':st.edgeWatchOnly?'EDGE':'WATCH';
      if(WARNING_SOURCE_TICKS[p.name]?.[src]!=null)WARNING_SOURCE_TICKS[p.name][src]++;
    }
    last.players[p.name]={raw,stable:st,state:{...ps}};""",
"""    warningTelemetry(p.name,st,da,now);
    last.players[p.name]={raw,stable:st,state:{...ps}};""",
'warning telemetry call')

rep(
"""    watchRate:ticks?+(total.WATCH/ticks).toFixed(3):null},
    warningSourcePlayers,warningSources,warningSourceRates:sourceRates};""",
"""    watchRate:ticks?+(total.WATCH/ticks).toFixed(3):null},
    warningSourcePlayers,warningSources,warningSourceRates:sourceRates,
    damageWarningAttribution:damageWarningSnapshot()};""",
'damage warning snapshot output')

rep("version:'offline-dynamic-spectator-calibrated-v4.11.1'","version:'offline-dynamic-spectator-calibrated-v4.11.2'",'version')
rep("qlog('✅ WOF V4.11.1 多房间审计去污染/警告负担拆分版启动');","qlog('✅ WOF V4.11.2 实际掉血警告来源归因版启动');",'startup')
rep(
"""  qlog('📊 警告来源: decisionLoad.warningSources拆分ACTION/GUARD/TAIL/SHADOW/BRIDGE/PHASE/GEOMETRY/EDGE/WATCH');""",
"""  qlog('📊 警告来源: decisionLoad.warningSources拆分ACTION/GUARD/TAIL/SHADOW/BRIDGE/PHASE/GEOMETRY/EDGE/WATCH');
  qlog('🧬 掉血归因: decisionLoad.damageWarningAttribution记录掉血前350ms内警告来源的any/exclusive/latest与提前量；仍不改变预测/HUD行为');""",
'damage attribution startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.11.2',len(s))
