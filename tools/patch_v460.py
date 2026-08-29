from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.5.1" not in s:
    raise SystemExit('expected V4.5.1 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' target missing')
    s=s.replace(old,new,1)

rep(
"""    fallbackZThreshold:80,
    fallbackZActionCore:16,
    padX:3,""",
"""    fallbackZThreshold:80,
    fallbackZActionCore:16,
    fallbackXYActionScale:.68,
    fallbackYActionScale:.85,
    padX:3,""",
'fallback XY config')

rep(
"""  const getFamily=id=>DB.f[id]||null;
  function radius(f){
    const rawRz=(+f[5]||8),geometryFallbackZ=rawRz>=CFG.fallbackZThreshold;
    const actionRawRz=geometryFallbackZ?CFG.fallbackZActionCore:rawRz;
    return {rx:(+f[3]||115)+CFG.padX,ry:(+f[4]||22)+CFG.padY,
      rz:rawRz+CFG.padZ,actionRz:actionRawRz+CFG.padZ,rawRz,geometryFallbackZ};
  }""",
"""  const getFamily=id=>DB.f[id]||null;
  const FALLBACK_GEOMETRY=new Set(Object.values(DB.fd||{}).map(a=>(+a[0]||0)+'|'+(+a[1]||0)+'|'+(+a[2]||0)));
  function radius(f){
    const rawRx=(+f[3]||115),rawRy=(+f[4]||22),rawRz=(+f[5]||8);
    const geometryFallback=FALLBACK_GEOMETRY.has(rawRx+'|'+rawRy+'|'+rawRz);
    const geometryFallbackZ=rawRz>=CFG.fallbackZThreshold;
    const actionRawRx=geometryFallback?rawRx*CFG.fallbackXYActionScale:rawRx;
    const actionRawRy=geometryFallback?rawRy*CFG.fallbackYActionScale:rawRy;
    const actionRawRz=geometryFallbackZ?CFG.fallbackZActionCore:rawRz;
    return {rx:rawRx+CFG.padX,ry:rawRy+CFG.padY,rz:rawRz+CFG.padZ,
      actionRx:actionRawRx+CFG.padX,actionRy:actionRawRy+CFG.padY,actionRz:actionRawRz+CFG.padZ,
      rawRx,rawRy,rawRz,geometryFallback,geometryFallbackZ};
  }""",
'radius fallback XYZ')

rep(
"""            rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRz:rad.actionRz,geometryFallbackZ:rad.geometryFallbackZ,
            slot:o.slot,type:o.type,family:fc.id,""",
"""            rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRx:rad.actionRx,actionRy:rad.actionRy,actionRz:rad.actionRz,
            geometryFallback:rad.geometryFallback,geometryFallbackZ:rad.geometryFallbackZ,
            slot:o.slot,type:o.type,family:fc.id,""",
'startup fallback XYZ fields')

rep(
"""        rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRz:rad.actionRz,geometryFallbackZ:rad.geometryFallbackZ,
        slot:o.slot,type:o.type,family:s.locked,""",
"""        rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRx:rad.actionRx,actionRy:rad.actionRy,actionRz:rad.actionRz,
        geometryFallback:rad.geometryFallback,geometryFallbackZ:rad.geometryFallbackZ,
        slot:o.slot,type:o.type,family:s.locked,""",
'active fallback XYZ fields')

rep(
"""  const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false)
    .map(d=>d.geometryFallbackZ?{...d,rz:d.actionRz,geometryCore:true}:d);""",
"""  const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false)
    .map(d=>d.geometryFallback?{...d,rx:d.actionRx,ry:d.actionRy,rz:d.actionRz,geometryCore:true}:d);""",
'action danger fallback XYZ core')

rep(
"""    if(!fullCur.safe&&(fullCur.hit?.source==='active-unknown'||fullCur.hit?.actionable===false||fullCur.hit?.geometryFallbackZ))
      return{danger:true,watchOnly:true,geometryWatchOnly:!!fullCur.hit?.geometryFallbackZ,best:'WATCH',hitMs:fullCur.collisionMs,hit:fullCur.hit,stay:fullCur};""",
"""    if(!fullCur.safe&&(fullCur.hit?.source==='active-unknown'||fullCur.hit?.actionable===false||fullCur.hit?.geometryFallback))
      return{danger:true,watchOnly:true,geometryWatchOnly:!!fullCur.hit?.geometryFallback,best:'WATCH',hitMs:fullCur.collisionMs,hit:fullCur.hit,stay:fullCur};""",
'full fallback shell WATCH')

rep(
"""  else if(action==='WATCH'&&r.geometryWatchOnly)qlog('🟣',name,'WATCH-Z壳','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'fullZ',h.rz,'coreZ',h.actionRz,'source',h.source||'?');""",
"""  else if(action==='WATCH'&&r.geometryWatchOnly)qlog('🟣',name,'WATCH-壳','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'full',fmt(h.rx)+'/'+fmt(h.ry)+'/'+fmt(h.rz),'core',fmt(h.actionRx)+'/'+fmt(h.actionRy)+'/'+fmt(h.actionRz),'source',h.source||'?');""",
'WATCH fallback shell log')

rep("version:'offline-dynamic-spectator-calibrated-v4.5.1'","version:'offline-dynamic-spectator-calibrated-v4.6'",'version')
rep("qlog('✅ WOF V4.5.1 静态报告观战版启动');","qlog('✅ WOF V4.6 双层XYZ几何观战版启动');",'startup')
rep(
"qlog('🧭 Z几何: DB中rz>=80视为低信息外壳；外壳只WATCH，行动使用coreZ='+(CFG.fallbackZActionCore+CFG.padZ));",
"qlog('🧭 XYZ几何: class fallback 保留完整外壳用于WATCH；行动核心 X/Y 缩放 '+CFG.fallbackXYActionScale+'/'+CFG.fallbackYActionScale+'，高Z核心='+(CFG.fallbackZActionCore+CFG.padZ));",
'geometry startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.6',len(s))
