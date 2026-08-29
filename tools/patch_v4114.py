from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.11.3" not in s:
    raise SystemExit('expected V4.11.3 input')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,count)

# V4.11.4 is still prediction-neutral. V4.11.3 showed that GUARD/GEOMETRY
# cannot simply be removed: they are broad and noisy, but some real damage is
# exclusively covered by them. Instead, shadow-simulate a tiered HUD and a
# low-duty-cycle pulse policy while keeping all prediction / decision behavior frozen.

rep(
"""  const incDiag=(m,k)=>{if(k)m[k]=(m[k]||0)+1;};
  const leadBand=v=>!Number.isFinite(+v)?'lead:?':+v<=120?'lead:<=120':+v<=220?'lead:121-220':+v<=350?'lead:221-350':'lead:>350';""",
"""  const incDiag=(m,k)=>{if(k)m[k]=(m[k]||0)+1;};
  const HUD_STATE={
    P1:{sig:null,lastSeen:-1e9,lastPulseAt:-1e9,pulseUntil:-1e9},
    P2:{sig:null,lastSeen:-1e9,lastPulseAt:-1e9,pulseUntil:-1e9},
    P3:{sig:null,lastSeen:-1e9,lastPulseAt:-1e9,pulseUntil:-1e9}
  };
  const HUD_SHADOW={
    ticks:{L1:0,L2:0,L3:0},episodes:blankWarningSources(),pulses:0,pulseTicks:0,
    damage:{hpDrops:0,actionCovered:0,specificOrActionCovered:0,anyCovered:0,broadOnly:0,pulseRecent:0,noWarning:0}
  };
  const warningLevel=src=>src==='ACTION'?3:(src==='GUARD'||src==='GEOMETRY'||src==='SHADOW'?1:2);
  function hudTelemetry(name,src,meta,now){
    const u=HUD_STATE[name];if(!u||!src)return;
    const lv=warningLevel(src);HUD_SHADOW.ticks['L'+lv]++;
    const sig=meta?.sig||src,gap=now-u.lastSeen;
    if(sig!==u.sig||gap>CFG.tickMs*3){
      if(HUD_SHADOW.episodes[src]!=null)HUD_SHADOW.episodes[src]++;
      HUD_SHADOW.pulses++;u.lastPulseAt=now;u.pulseUntil=now+180;
    }else if(now-u.lastPulseAt>=900){
      HUD_SHADOW.pulses++;u.lastPulseAt=now;u.pulseUntil=now+180;
    }
    u.sig=sig;u.lastSeen=now;
    if(now<=u.pulseUntil)HUD_SHADOW.pulseTicks++;
  }
  function hudDamageRecord(name,now,h){
    const d=HUD_SHADOW.damage,u=HUD_STATE[name];d.hpDrops++;
    if(!h.length){d.noWarning++;return;}
    d.anyCovered++;
    const levels=h.map(x=>warningLevel(x.src));
    if(levels.some(x=>x===3))d.actionCovered++;
    if(levels.some(x=>x>=2))d.specificOrActionCovered++;
    if(levels.every(x=>x===1))d.broadOnly++;
    if(u&&now-u.lastPulseAt<=350)d.pulseRecent++;
  }
  function hudShadowSnapshot(){
    const d=HUD_SHADOW.damage;
    return {ticks:{...HUD_SHADOW.ticks},episodes:{...HUD_SHADOW.episodes},pulses:HUD_SHADOW.pulses,pulseTicks:HUD_SHADOW.pulseTicks,
      damage:{...d,
        actionCoverage:d.hpDrops?+(d.actionCovered/d.hpDrops).toFixed(3):null,
        specificOrActionCoverage:d.hpDrops?+(d.specificOrActionCovered/d.hpDrops).toFixed(3):null,
        anyCoverage:d.hpDrops?+(d.anyCovered/d.hpDrops).toFixed(3):null,
        broadOnlyRate:d.hpDrops?+(d.broadOnly/d.hpDrops).toFixed(3):null,
        pulseRecentCoverage:d.hpDrops?+(d.pulseRecent/d.hpDrops).toFixed(3):null}};
  }
  const leadBand=v=>!Number.isFinite(+v)?'lead:?':+v<=120?'lead:<=120':+v<=220?'lead:121-220':+v<=350?'lead:221-350':'lead:>350';""",
'hud shadow structures')

rep(
"""    const meta=warningMeta(st,src);diagTick(src,meta);
    const last=h[h.length-1];""",
"""    const meta=warningMeta(st,src);diagTick(src,meta);hudTelemetry(name,src,meta,now);
    const last=h[h.length-1];""",
'hud warning telemetry')

rep(
"""    const h=(WARN_HISTORY[name]||[]).filter(x=>x.lastAt>=now-350);
    const D=DAMAGE_WARNING,P=D.players[name];D.hpDrops++;if(P)P.hpDrops++;
    if(!h.length){D.noStableWarning++;if(P)P.noStableWarning++;return;}""",
"""    const h=(WARN_HISTORY[name]||[]).filter(x=>x.lastAt>=now-350);
    const D=DAMAGE_WARNING,P=D.players[name];D.hpDrops++;if(P)P.hpDrops++;hudDamageRecord(name,now,h);
    if(!h.length){D.noStableWarning++;if(P)P.noStableWarning++;return;}""",
'hud damage attribution')

rep(
"""        geometry:{ticks:{...WATCH_DIAG.geometry.ticks},damageAny:{...WATCH_DIAG.geometry.damageAny},damageExclusiveLatest:{...WATCH_DIAG.geometry.damageExclusiveLatest}},
        caseSeq:WATCH_DIAG.caseSeq,exclusiveCases:WATCH_DIAG.exclusiveCases.map(x=>JSON.parse(JSON.stringify(x)))}
    };""",
"""        geometry:{ticks:{...WATCH_DIAG.geometry.ticks},damageAny:{...WATCH_DIAG.geometry.damageAny},damageExclusiveLatest:{...WATCH_DIAG.geometry.damageExclusiveLatest}},
        caseSeq:WATCH_DIAG.caseSeq,exclusiveCases:WATCH_DIAG.exclusiveCases.map(x=>JSON.parse(JSON.stringify(x)))},
      hudShadow:hudShadowSnapshot()
    };""",
'hud shadow snapshot output')

rep("version:'offline-dynamic-spectator-calibrated-v4.11.3'","version:'offline-dynamic-spectator-calibrated-v4.11.4'",'version')
rep("qlog('✅ WOF V4.11.3 GUARD/GEOMETRY必要性细分版启动');","qlog('✅ WOF V4.11.4 HUD分层/脉冲影子评估版启动');",'startup')
rep(
"""  qlog('🔬 V4.11.3细分: watchDiagnostics记录GUARD的attack-age/speed/radius/family/lead，以及GEOMETRY的source/Z壳/radius/family/lead，并保留独占掉血case；预测行为完全不变');""",
"""  qlog('🔬 V4.11.3细分: watchDiagnostics记录GUARD的attack-age/speed/radius/family/lead，以及GEOMETRY的source/Z壳/radius/family/lead，并保留独占掉血case；预测行为完全不变');
  qlog('🖥️ V4.11.4 HUD影子: L3=ACTION，L2=TAIL/BRIDGE/PHASE/EDGE/WATCH，L1=GUARD/GEOMETRY/SHADOW；同时模拟180ms脉冲+900ms重复，仍不改变预测/决策');""",
'hud shadow startup')

p.write_text(s,encoding='utf-8')
print('patched V4.11.4',len(s))
