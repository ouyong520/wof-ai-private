from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.6.2" not in s:
    raise SystemExit('expected V4.6.2 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' target missing')
    s=s.replace(old,new,1)

# Add a normalized penetration shell: near-edge contacts remain WATCH instead of forcing movement.
rep(
"""    activeActionMinConfidence:0.50,
    auditRevokeLeadMs:60,""",
"""    activeActionMinConfidence:0.50,
    actionPenetrationMin:0.10,
    fpPenetrationMin:0.05,
    auditRevokeLeadMs:60,""",
'penetration config')

# Deep false positives are more useful than fringe contacts, so demote faster once the sample is truly inside the action core.
rep(
"""    sourceDemoteConfirmed:4,sourceDemoteFp:3,sourceDemoteFpPlayers:2,sourceDemotePrecision:.25,
    sourceRecoverConfirmed:8,sourceRecoverHit:4,sourceRecoverPrecision:.50,
    familyDemoteConfirmed:6,familyDemoteFp:4,familyDemoteFpPlayers:2,familyDemotePrecision:.30,
    familyRecoverConfirmed:12,familyRecoverHit:6,familyRecoverPrecision:.50,""",
"""    sourceDemoteConfirmed:2,sourceDemoteFp:2,sourceDemoteFpPlayers:1,sourceDemotePrecision:.25,
    sourceRecoverConfirmed:5,sourceRecoverHit:2,sourceRecoverPrecision:.50,
    familyDemoteConfirmed:3,familyDemoteFp:3,familyDemoteFpPlayers:1,familyDemotePrecision:.30,
    familyRecoverConfirmed:7,familyRecoverHit:3,familyRecoverPrecision:.50,""",
'fast deep-fp demotion')

rep(
"""  function calFpEligible(e){
    if((+e.survival||0)<CAL_CFG.fpMinSurvival)return false;
    const c=+e.confidence||0;
    return e.source==='active'?c>=CAL_CFG.activeFpMinConfidence:c>=CAL_CFG.startupFpMinConfidence;
  }""",
"""  function calFpEligible(e){
    if((+e.survival||0)<CAL_CFG.fpMinSurvival)return false;
    const c=+e.confidence||0;
    const confOK=e.source==='active'?c>=CAL_CFG.activeFpMinConfidence:c>=CAL_CFG.startupFpMinConfidence;
    if(!confOK)return false;
    const px=(+e.rx||0)>0?(+e.mx||0)/(+e.rx||1):-1;
    const py=(+e.ry||0)>0?(+e.my||0)/(+e.ry||1):-1;
    const pz=(+e.rz||0)>0?(+e.mz||0)/(+e.rz||1):-1;
    return Math.min(px,py,pz)>=CFG.fpPenetrationMin;
  }""",
'deep fp eligibility')

# Build action geometry from the current core and then carve a 10% edge shell.
rep(
"""  const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false)
    .map(d=>d.geometryFallback?{...d,rx:d.actionRx,ry:d.actionRy,rz:d.actionRz,geometryCore:true}:d);
  const fullCur=evalPath(p,'CONTINUE',danger,0);
  const cur=evalPath(p,'CONTINUE',actionDanger,0);

  if(cur.safe){
    if(!fullCur.safe&&(fullCur.hit?.source==='active-unknown'||fullCur.hit?.actionable===false||fullCur.hit?.geometryFallback))
      return{danger:true,watchOnly:true,geometryWatchOnly:!!fullCur.hit?.geometryFallback,best:'WATCH',hitMs:fullCur.collisionMs,hit:fullCur.hit,stay:fullCur};
    return{danger:false,best:'CONTINUE',stay:cur};
  }""",
"""  const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false)
    .map(d=>d.geometryFallback?{...d,rx:d.actionRx,ry:d.actionRy,rz:d.actionRz,geometryCore:true}:d)
    .map(d=>({...d,
      rx:Math.max(1,d.rx*(1-CFG.actionPenetrationMin)),
      ry:Math.max(1,d.ry*(1-CFG.actionPenetrationMin)),
      rz:Math.max(1,d.rz*(1-CFG.actionPenetrationMin)),
      actionPenetrationCore:true}));
  const fullCur=evalPath(p,'CONTINUE',danger,0);
  const cur=evalPath(p,'CONTINUE',actionDanger,0);

  if(cur.safe){
    if(!fullCur.safe){
      const gh=fullCur.hit||{};
      const geometryWatch=!!gh.geometryFallback;
      return{danger:true,watchOnly:true,geometryWatchOnly:geometryWatch,edgeWatchOnly:!geometryWatch,
        best:'WATCH',hitMs:fullCur.collisionMs,hit:gh,stay:fullCur};
    }
    return{danger:false,best:'CONTINUE',stay:cur};
  }""",
'action edge shell')

rep(
"""  else if(action==='WATCH'&&r.geometryWatchOnly)qlog('🟣',name,'WATCH-壳','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'full',fmt(h.rx)+'/'+fmt(h.ry)+'/'+fmt(h.rz),'core',fmt(h.actionRx)+'/'+fmt(h.actionRy)+'/'+fmt(h.actionRz),'source',h.source||'?');
  else if(action==='WATCH')qlog('🟠',name,'WATCH','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?','source',h.source||'?');""",
"""  else if(action==='WATCH'&&r.geometryWatchOnly)qlog('🟣',name,'WATCH-壳','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'full',fmt(h.rx)+'/'+fmt(h.ry)+'/'+fmt(h.rz),'core',fmt(h.actionRx)+'/'+fmt(h.actionRy)+'/'+fmt(h.actionRz),'source',h.source||'?');
  else if(action==='WATCH'&&r.edgeWatchOnly)qlog('🟪',name,'WATCH-边缘','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'edge',Math.round(CFG.actionPenetrationMin*100)+'%','source',h.source||'?');
  else if(action==='WATCH')qlog('🟠',name,'WATCH','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?','source',h.source||'?');""",
'edge watch log')

rep(
"if(st.geometryWatchOnly)return;",
"if(st.geometryWatchOnly||st.edgeWatchOnly)return;",
'skip edge-shell audit')

rep("version:'offline-dynamic-spectator-calibrated-v4.6.2'","version:'offline-dynamic-spectator-calibrated-v4.7'",'version')
rep("qlog('✅ WOF V4.6.2 快速在线降级观战版启动');","qlog('✅ WOF V4.7 边缘壳深度校准观战版启动');",'startup')
rep(
"qlog('🧯 在线校准: 红色=可进入校准的高可信误报；黄色=低置信误报，仅WATCH/统计，不处罚Family');",
"qlog('🧯 在线校准: 只有深入行动核心的误报才快速降级；擦边碰撞只WATCH，不处罚Family');\n  qlog('🟪 边缘壳: 行动核心再内缩 '+Math.round(CFG.actionPenetrationMin*100)+'%，避免擦边UP/DOWN/AB');",
'penetration startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.7',len(s))
