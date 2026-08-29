from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.11.2" not in s:
    raise SystemExit('expected V4.11.2 input')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,count)

# V4.11.3 is diagnostic-only. V4.11.2 proved GUARD and fallback GEOMETRY are
# simultaneously the biggest warning burden and genuine contributors to real damage
# coverage. Before pruning either layer, collect enough detail to simulate narrower
# policies offline: guard attack age / speed / radius / family / lead-time and geometry
# source / fallback-Z / radius / family / lead-time. Prediction and decisions are untouched.

rep(
"""      out.danger.push({t,x:o.x+vx*dt,y:o.y+vy*dt,z:o.z+vz*dt,rx,ry,rz,
        slot:o.slot,type:o.type,family:s.locked||null,variant:null,confidence:.16,survival:1,
        actionable:false,guardWatch:true,source:'active-guard'});""",
"""      out.danger.push({t,x:o.x+vx*dt,y:o.y+vy*dt,z:o.z+vz*dt,rx,ry,rz,
        slot:o.slot,type:o.type,family:s.locked||null,variant:null,confidence:.16,survival:1,
        actionable:false,guardWatch:true,source:'active-guard',attack:o.attack,
        guardAge:age,guardSpeed:Math.hypot(vx,vy,vz),guardVx:vx,guardVy:vy,guardVz:vz});""",
'active guard diagnostic metadata')

rep(
"""  const DAMAGE_WARNING={
    hpDrops:0,withStableWarning:0,noStableWarning:0,
    latest:blankWarningSources(),any:blankWarningSources(),exclusive:blankWarningSources(),
    leadSumMs:0,leadCount:0,leadBuckets:{lte100:0,ms101_200:0,ms201_350:0},
    players:{P1:{hpDrops:0,withStableWarning:0,noStableWarning:0},P2:{hpDrops:0,withStableWarning:0,noStableWarning:0},P3:{hpDrops:0,withStableWarning:0,noStableWarning:0}}
  };
  function warningSourceOf(st,da){""",
"""  const DAMAGE_WARNING={
    hpDrops:0,withStableWarning:0,noStableWarning:0,
    latest:blankWarningSources(),any:blankWarningSources(),exclusive:blankWarningSources(),
    leadSumMs:0,leadCount:0,leadBuckets:{lte100:0,ms101_200:0,ms201_350:0},
    players:{P1:{hpDrops:0,withStableWarning:0,noStableWarning:0},P2:{hpDrops:0,withStableWarning:0,noStableWarning:0},P3:{hpDrops:0,withStableWarning:0,noStableWarning:0}}
  };
  const diagMap=()=>Object.create(null);
  const WATCH_DIAG={
    guard:{ticks:diagMap(),damageAny:diagMap(),damageExclusiveLatest:diagMap()},
    geometry:{ticks:diagMap(),damageAny:diagMap(),damageExclusiveLatest:diagMap()},
    exclusiveCases:[],caseSeq:0
  };
  const incDiag=(m,k)=>{if(k)m[k]=(m[k]||0)+1;};
  const leadBand=v=>!Number.isFinite(+v)?'lead:?':+v<=120?'lead:<=120':+v<=220?'lead:121-220':+v<=350?'lead:221-350':'lead:>350';
  const ageBand=v=>!Number.isFinite(+v)?'age:?':+v<=120?'age:<=120':+v<=300?'age:121-300':+v<=600?'age:301-600':'age:>600';
  const speedBand=v=>!Number.isFinite(+v)?'speed:?':+v<=30?'speed:<=30':+v<=100?'speed:31-100':'speed:>100';
  const radiusBand=v=>!Number.isFinite(+v)?'rx:?':+v<=105?'rx:<=105':+v<=130?'rx:106-130':'rx:>130';
  function warningMeta(st,src){
    const h=st?.hit||{},hitMs=Number.isFinite(+st?.hitMs)?+st.hitMs:null;
    const m={src,family:h.family||null,type:h.type??null,slot:h.slot??null,hitMs,
      dangerSource:h.source||null,rx:Number.isFinite(+h.rx)?+h.rx:null,ry:Number.isFinite(+h.ry)?+h.ry:null,rz:Number.isFinite(+h.rz)?+h.rz:null,
      actionRx:Number.isFinite(+h.actionRx)?+h.actionRx:null,actionRy:Number.isFinite(+h.actionRy)?+h.actionRy:null,actionRz:Number.isFinite(+h.actionRz)?+h.actionRz:null,
      geometryFallbackZ:!!h.geometryFallbackZ,geoClass:h.geoClass||null,tags:[]};
    if(src==='GUARD'){
      m.attack=h.attack??null;m.guardAge=Number.isFinite(+h.guardAge)?+h.guardAge:null;m.guardSpeed=Number.isFinite(+h.guardSpeed)?+h.guardSpeed:null;
      m.tags=[leadBand(hitMs),ageBand(m.guardAge),speedBand(m.guardSpeed),radiusBand(m.rx),m.family?'family:known':'family:unknown','type:T'+(m.type??'?')];
      if(m.family)m.tags.push('family:'+m.family);
    }else if(src==='GEOMETRY'){
      m.tags=[leadBand(hitMs),'origin:'+(m.dangerSource||'?'),m.geometryFallbackZ?'z:wide':'z:normal',radiusBand(m.rx),'type:T'+(m.type??'?')];
      if(m.family)m.tags.push('family:'+m.family);
      if(m.geoClass)m.tags.push('class:'+m.geoClass);
    }
    m.sig=src+'|slot:'+(m.slot??'?')+'|'+m.tags.join('|');
    return m;
  }
  function diagTick(src,meta){
    const d=src==='GUARD'?WATCH_DIAG.guard:src==='GEOMETRY'?WATCH_DIAG.geometry:null;
    if(!d||!meta)return;for(const tag of meta.tags||[])incDiag(d.ticks,tag);
  }
  function warningSourceOf(st,da){""",
'guard geometry diagnostics')

rep(
"""  function warningTelemetry(name,st,da,now){
    const h=WARN_HISTORY[name];if(!h)return null;
    while(h.length&&now-h[0].lastAt>1200)h.shift();
    const src=warningSourceOf(st,da);if(!src)return null;
    if(WARNING_SOURCE_TICKS[name]?.[src]!=null)WARNING_SOURCE_TICKS[name][src]++;
    const last=h[h.length-1];
    if(last&&last.src===src&&now-last.lastAt<=CFG.tickMs*3){
      last.lastAt=now;last.hitMs=Number.isFinite(+st?.hitMs)?+st.hitMs:last.hitMs;
    }else h.push({src,startAt:now,lastAt:now,hitMs:Number.isFinite(+st?.hitMs)?+st.hitMs:null});
    return src;
  }""",
"""  function warningTelemetry(name,st,da,now){
    const h=WARN_HISTORY[name];if(!h)return null;
    while(h.length&&now-h[0].lastAt>1200)h.shift();
    const src=warningSourceOf(st,da);if(!src)return null;
    if(WARNING_SOURCE_TICKS[name]?.[src]!=null)WARNING_SOURCE_TICKS[name][src]++;
    const meta=warningMeta(st,src);diagTick(src,meta);
    const last=h[h.length-1];
    if(last&&last.src===src&&last.sig===meta.sig&&now-last.lastAt<=CFG.tickMs*3){
      last.lastAt=now;last.hitMs=meta.hitMs;last.meta=meta;
    }else h.push({src,sig:meta.sig,startAt:now,lastAt:now,hitMs:meta.hitMs,meta});
    return src;
  }""",
'profile-aware warning history')

rep(
"""    const sources=[...new Set(h.map(x=>x.src))];for(const src of sources)if(D.any[src]!=null)D.any[src]++;
    if(sources.length===1&&D.exclusive[sources[0]]!=null)D.exclusive[sources[0]]++;
    const latest=h.reduce((a,b)=>!a||b.lastAt>a.lastAt?b:a,null);if(latest&&D.latest[latest.src]!=null)D.latest[latest.src]++;
    const earliest=Math.min(...h.map(x=>x.startAt));const lead=Math.max(0,Math.min(350,now-earliest));""",
"""    const sources=[...new Set(h.map(x=>x.src))];for(const src of sources)if(D.any[src]!=null)D.any[src]++;
    if(sources.length===1&&D.exclusive[sources[0]]!=null)D.exclusive[sources[0]]++;
    for(const src of ['GUARD','GEOMETRY']){
      const sh=h.filter(x=>x.src===src);if(!sh.length)continue;
      const d=src==='GUARD'?WATCH_DIAG.guard:WATCH_DIAG.geometry;
      const anyTags=[...new Set(sh.flatMap(x=>x.meta?.tags||[]))];for(const tag of anyTags)incDiag(d.damageAny,tag);
      if(sources.length===1){
        const q=sh.reduce((a,b)=>!a||b.lastAt>a.lastAt?b:a,null);
        for(const tag of q?.meta?.tags||[])incDiag(d.damageExclusiveLatest,tag);
        const compact=sh.slice(-12).map(x=>({firstLeadMs:+Math.max(0,now-x.startAt).toFixed(1),lastLeadMs:+Math.max(0,now-x.lastAt).toFixed(1),meta:x.meta}));
        WATCH_DIAG.exclusiveCases.push({seq:++WATCH_DIAG.caseSeq,at:+now.toFixed(1),player:name,source:src,warnings:compact});
        if(WATCH_DIAG.exclusiveCases.length>80)WATCH_DIAG.exclusiveCases.shift();
      }
    }
    const latest=h.reduce((a,b)=>!a||b.lastAt>a.lastAt?b:a,null);if(latest&&D.latest[latest.src]!=null)D.latest[latest.src]++;
    const earliest=Math.min(...h.map(x=>x.startAt));const lead=Math.max(0,Math.min(350,now-earliest));""",
'damage diagnostics attribution')

rep(
"""  function damageWarningSnapshot(){
    const D=DAMAGE_WARNING;
    return {hpDrops:D.hpDrops,withStableWarning:D.withStableWarning,noStableWarning:D.noStableWarning,
      stableWarningCoverage:D.hpDrops?+(D.withStableWarning/D.hpDrops).toFixed(3):null,
      latest:{...D.latest},any:{...D.any},exclusive:{...D.exclusive},
      avgFirstLeadMs:D.leadCount?+(D.leadSumMs/D.leadCount).toFixed(1):null,leadBuckets:{...D.leadBuckets},
      players:{P1:{...D.players.P1},P2:{...D.players.P2},P3:{...D.players.P3}}};
  }""",
"""  function damageWarningSnapshot(){
    const D=DAMAGE_WARNING;
    let enemyDamageEvents=0,nonEnemyDamage=0,hpBaselineReset=0;
    for(const n of ['P1','P2','P3']){const q=AUD[n]?.stats||{};enemyDamageEvents+=(+q.hit||0)+(+q.ambiguousDamage||0)+(+q.watchCovered||0)+(+q.unstableCovered||0)+(+q.safeMiss||0);nonEnemyDamage+=+q.nonEnemyDamage||0;hpBaselineReset+=+q.hpBaselineReset||0;}
    return {hpDrops:D.hpDrops,enemyDamageEvents,nonEnemyDamage,hpBaselineReset,withStableWarning:D.withStableWarning,noStableWarning:D.noStableWarning,
      stableWarningCoverage:D.hpDrops?+(D.withStableWarning/D.hpDrops).toFixed(3):null,
      latest:{...D.latest},any:{...D.any},exclusive:{...D.exclusive},
      avgFirstLeadMs:D.leadCount?+(D.leadSumMs/D.leadCount).toFixed(1):null,leadBuckets:{...D.leadBuckets},
      players:{P1:{...D.players.P1},P2:{...D.players.P2},P3:{...D.players.P3}},
      watchDiagnostics:{
        guard:{ticks:{...WATCH_DIAG.guard.ticks},damageAny:{...WATCH_DIAG.guard.damageAny},damageExclusiveLatest:{...WATCH_DIAG.guard.damageExclusiveLatest}},
        geometry:{ticks:{...WATCH_DIAG.geometry.ticks},damageAny:{...WATCH_DIAG.geometry.damageAny},damageExclusiveLatest:{...WATCH_DIAG.geometry.damageExclusiveLatest}},
        caseSeq:WATCH_DIAG.caseSeq,exclusiveCases:WATCH_DIAG.exclusiveCases.map(x=>JSON.parse(JSON.stringify(x)))}
    };
  }""",
'diagnostic snapshot')

rep("version:'offline-dynamic-spectator-calibrated-v4.11.2'","version:'offline-dynamic-spectator-calibrated-v4.11.3'",'version')
rep("qlog('✅ WOF V4.11.2 实际掉血警告来源归因版启动');","qlog('✅ WOF V4.11.3 GUARD/GEOMETRY必要性细分版启动');",'startup')
rep(
"""  qlog('🧬 掉血归因: decisionLoad.damageWarningAttribution记录掉血前350ms内警告来源的any/exclusive/latest与提前量；仍不改变预测/HUD行为');""",
"""  qlog('🧬 掉血归因: decisionLoad.damageWarningAttribution记录掉血前350ms内警告来源的any/exclusive/latest与提前量；仍不改变预测/HUD行为');
  qlog('🔬 V4.11.3细分: watchDiagnostics记录GUARD的attack-age/speed/radius/family/lead，以及GEOMETRY的source/Z壳/radius/family/lead，并保留独占掉血case；预测行为完全不变');""",
'startup detail')

p.write_text(s,encoding='utf-8')
print('patched V4.11.3',len(s))
