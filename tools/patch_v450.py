from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')

if "offline-dynamic-spectator-calibrated-v4.4.1" not in s:
    raise SystemExit('expected V4.4.1 input')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} patch target missing')
    s=s.replace(old,new,1)

# DB inspection shows 170/403 Families use exactly rz=90, while nearly all other rz values are 8/14.
# Treat 90 as a low-information fallback shell: preserve it for WATCH, but use a tighter Z core for action decisions.
replace_once(
"""    auditRepeatBlockMs:700,
    padX:3,
    padY:2,
    padZ:2""",
"""    auditRepeatBlockMs:700,
    fallbackZThreshold:80,
    fallbackZActionCore:16,
    padX:3,
    padY:2,
    padZ:2""",
'fallback Z config')

replace_once(
"function radius(f){return {rx:(+f[3]||115)+CFG.padX,ry:(+f[4]||22)+CFG.padY,rz:(+f[5]||8)+CFG.padZ};}",
"""function radius(f){
    const rawRz=(+f[5]||8),geometryFallbackZ=rawRz>=CFG.fallbackZThreshold;
    const actionRawRz=geometryFallbackZ?CFG.fallbackZActionCore:rawRz;
    return {rx:(+f[3]||115)+CFG.padX,ry:(+f[4]||22)+CFG.padY,
      rz:rawRz+CFG.padZ,actionRz:actionRawRz+CFG.padZ,rawRz,geometryFallbackZ};
  }""",
'radius dual Z')

replace_once(
"""            rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:fc.id,
            confidence,survival,actionable:survival>=CFG.survivalActionThreshold&&!cal.watchOnly,""",
"""            rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRz:rad.actionRz,geometryFallbackZ:rad.geometryFallbackZ,
            slot:o.slot,type:o.type,family:fc.id,
            confidence,survival,actionable:survival>=CFG.survivalActionThreshold&&!cal.watchOnly,""",
'startup dual Z fields')

replace_once(
"""        rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:s.locked,
        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold&&!cal.watchOnly,""",
"""        rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRz:rad.actionRz,geometryFallbackZ:rad.geometryFallbackZ,
        slot:o.slot,type:o.type,family:s.locked,
        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold&&!cal.watchOnly,""",
'active dual Z fields')

replace_once(
"const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false);",
"""const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false)
    .map(d=>d.geometryFallbackZ?{...d,rz:d.actionRz,geometryCore:true}:d);""",
'action danger uses Z core')

replace_once(
"""    if(!fullCur.safe&&(fullCur.hit?.source==='active-unknown'||fullCur.hit?.actionable===false))
      return{danger:true,watchOnly:true,best:'WATCH',hitMs:fullCur.collisionMs,hit:fullCur.hit,stay:fullCur};""",
"""    if(!fullCur.safe&&(fullCur.hit?.source==='active-unknown'||fullCur.hit?.actionable===false||fullCur.hit?.geometryFallbackZ))
      return{danger:true,watchOnly:true,geometryWatchOnly:!!fullCur.hit?.geometryFallbackZ,best:'WATCH',hitMs:fullCur.collisionMs,hit:fullCur.hit,stay:fullCur};""",
'full shell WATCH branch')

replace_once(
"""  else if(action==='WATCH'&&r.noRoute)console.log('🟠',name,'WATCH无路','当前'+r.hitMs+'ms',h.family||'?',
    'UP堵'+r.upHitMs+'ms',uh.family||'?','DOWN堵'+r.downHitMs+'ms',dh.family||'?','窗口'+r.routeUntil+'ms');
  else if(action==='WATCH')console.log('🟠',name,'WATCH','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?','source',h.source||'?');""",
"""  else if(action==='WATCH'&&r.noRoute)console.log('🟠',name,'WATCH无路','当前'+r.hitMs+'ms',h.family||'?',
    'UP堵'+r.upHitMs+'ms',uh.family||'?','DOWN堵'+r.downHitMs+'ms',dh.family||'?','窗口'+r.routeUntil+'ms');
  else if(action==='WATCH'&&r.geometryWatchOnly)console.log('🟣',name,'WATCH-Z壳','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'fullZ',h.rz,'coreZ',h.actionRz,'source',h.source||'?');
  else if(action==='WATCH')console.log('🟠',name,'WATCH','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?','source',h.source||'?');""",
'WATCH Z shell log')

replace_once(
"""    const h=st.hit||{};
    if(h.family==null||h.source==='active-unknown'||(h.actionable===false&&!h.calWatchOnly))return;""",
"""    const h=st.hit||{};
    if(st.geometryWatchOnly)return;
    if(h.family==null||h.source==='active-unknown'||(h.actionable===false&&!h.calWatchOnly))return;""",
'do not audit fallback Z shell')

replace_once("version:'offline-dynamic-spectator-calibrated-v4.4.1'","version:'offline-dynamic-spectator-calibrated-v4.5'",'version')
replace_once("console.log('✅ WOF V4.4.1 攻击实例去重校准观战版启动');","console.log('✅ WOF V4.5 双层Z几何观战版启动');",'startup version')
replace_once(
"console.log('🧯 在线校准: 同一攻击实例只记一次；全局降级需至少2名玩家共同提供误报证据');",
"console.log('🧭 Z几何: DB中rz>=80视为低信息外壳；外壳只WATCH，行动使用coreZ='+(CFG.fallbackZActionCore+CFG.padZ));\n  console.log('🧯 在线校准: 同一攻击实例只记一次；全局降级需至少2名玩家共同提供误报证据');",
'Z startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.5',len(s))
