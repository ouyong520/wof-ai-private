from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.8.2" not in s:
    raise SystemExit('expected V4.8.2 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' target missing')
    s=s.replace(old,new,1)

# Shared geometry-class calibration: fallback radii are reused by many Families, so learn them jointly.
rep(
"const CAL_FAMILY=Object.create(null),CAL_SOURCE=Object.create(null),CAL_VARIANT=Object.create(null);",
"const CAL_FAMILY=Object.create(null),CAL_SOURCE=Object.create(null),CAL_VARIANT=Object.create(null),CAL_GEOM=Object.create(null);",
'CAL_GEOM declaration')

rep(
"function calBucket(map,key){return map[key]||(map[key]={hit:0,fp:0,ignoredFp:0,confirmed:0,precision:null,watchOnly:false,demotions:0,recoveries:0,hitPlayers:{},fpPlayers:{},gx:1,gy:1,gz:1,geoFp:0,geoHit:0});}",
"function calBucket(map,key){return map[key]||(map[key]={hit:0,fp:0,ignoredFp:0,confirmed:0,precision:null,watchOnly:false,demotions:0,recoveries:0,hitPlayers:{},fpPlayers:{},fpFamilies:{},gx:1,gy:1,gz:1,geoFp:0,geoHit:0});}",
'calBucket fpFamilies')

rep(
"""    return {rx:rawRx+CFG.padX,ry:rawRy+CFG.padY,rz:rawRz+CFG.padZ,
      actionRx:actionRawRx+CFG.padX,actionRy:actionRawRy+CFG.padY,actionRz:actionRawRz+CFG.padZ,
      rawRx,rawRy,rawRz,geometryFallback,geometryFallbackZ};""",
"""    const geoClass=geometryFallback?('fallback:'+rawRx+':'+rawRy+':'+rawRz):null;
    return {rx:rawRx+CFG.padX,ry:rawRy+CFG.padY,rz:rawRz+CFG.padZ,
      actionRx:actionRawRx+CFG.padX,actionRy:actionRawRy+CFG.padY,actionRz:actionRawRz+CFG.padZ,
      rawRx,rawRy,rawRz,geometryFallback,geometryFallbackZ,geoClass};""",
'radius geoClass')

needle="""  function geoAdapt(e,kind,sb,vb){
    if(!e||(!sb&&!vb))return;"""
if needle not in s:
    raise SystemExit('geoAdapt insertion target missing')
insert="""  function geoClassPolicy(key){
    const b=key?CAL_GEOM[key]:null;
    return {x:b?.gx??1,y:b?.gy??1,z:b?.gz??1,fp:b?.geoFp||0,hit:b?.geoHit||0};
  }
  function geoClassAdapt(e,kind){
    if(!e?.geometryFallback||!e.geoClass)return;
    const b=calBucket(CAL_GEOM,e.geoClass);
    if(kind==='hit'){
      b.geoHit=(b.geoHit||0)+1;
      b.gx=Math.min(1,(b.gx??1)+.04);b.gy=Math.min(1,(b.gy??1)+.04);b.gz=Math.min(1,(b.gz??1)+.04);
      return;
    }
    if(kind!=='fp'||!calFpEligible(e))return;
    b.geoFp=(b.geoFp||0)+1;b.fpFamilies[e.family||'?']=1;
    // Require several independent Families before changing a shared fallback geometry class.
    if(b.geoFp<3||Object.keys(b.fpFamilies||{}).length<2)return;
    const vals=[['x',+e.rx||1,+e.mx||0],['y',+e.ry||1,+e.my||0],['z',+e.rz||1,+e.mz||0]]
      .map(([axis,r,m])=>({axis,r,m,pen:r>0?m/r:1})).sort((a,b)=>a.pen-b.pen);
    const edge=vals[0];if(!edge||edge.pen<0)return;
    const prop='g'+edge.axis,cur=b[prop]??1;
    const shrink=Math.max(.80,Math.min(.94,1-edge.pen-.02));
    const target=Math.max(.58,cur*shrink);
    if(target<cur)b[prop]=target;
  }

"""+needle
s=s.replace(needle,insert,1)

# Shared class participates in action core only; full outer hazard remains unchanged for WATCH.
rep(
"""          const variant='s'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3+':'+hit.kind;
          const cal=calPolicy(fc.id,'startup',variant);
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,
            rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRx:rad.actionRx,actionRy:rad.actionRy,actionRz:rad.actionRz,
            geometryFallback:rad.geometryFallback,geometryFallbackZ:rad.geometryFallbackZ,""",
"""          const variant='s'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3+':'+hit.kind;
          const cal=calPolicy(fc.id,'startup',variant),gc=geoClassPolicy(rad.geoClass);
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,
            rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRx:rad.actionRx*gc.x,actionRy:rad.actionRy*gc.y,actionRz:rad.actionRz*gc.z,
            geometryFallback:rad.geometryFallback,geometryFallbackZ:rad.geometryFallbackZ,geoClass:rad.geoClass,""",
'startup shared geometry')

rep(
"""      const variant=(s.variantBase||'a?')+'|'+(s.variantMotion||'early');
      const cal=calPolicy(s.locked,'active',variant);
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,
        rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRx:rad.actionRx,actionRy:rad.actionRy,actionRz:rad.actionRz,
        geometryFallback:rad.geometryFallback,geometryFallbackZ:rad.geometryFallbackZ,""",
"""      const variant=(s.variantBase||'a?')+'|'+(s.variantMotion||'early');
      const cal=calPolicy(s.locked,'active',variant),gc=geoClassPolicy(rad.geoClass);
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,
        rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRx:rad.actionRx*gc.x,actionRy:rad.actionRy*gc.y,actionRz:rad.actionRz*gc.z,
        geometryFallback:rad.geometryFallback,geometryFallbackZ:rad.geometryFallbackZ,geoClass:rad.geoClass,""",
'active shared geometry')

rep(
"geoAdapt(e,kind,sb,vb);",
"geoAdapt(e,kind,sb,vb);geoClassAdapt(e,kind);",
'record shared geometry')

rep(
"self.__WOF_CAL_CACHE={family:JSON.parse(JSON.stringify(CAL_FAMILY)),source:JSON.parse(JSON.stringify(CAL_SOURCE)),variant:JSON.parse(JSON.stringify(CAL_VARIANT))};",
"self.__WOF_CAL_CACHE={family:JSON.parse(JSON.stringify(CAL_FAMILY)),source:JSON.parse(JSON.stringify(CAL_SOURCE)),variant:JSON.parse(JSON.stringify(CAL_VARIANT)),geom:JSON.parse(JSON.stringify(CAL_GEOM))};",
'cache geom')

rep(
"""      precision:v.precision,watchOnly:v.watchOnly,demotions:v.demotions,recoveries:v.recoveries,
      geo:[+(v.gx??1).toFixed(3),+(v.gy??1).toFixed(3),+(v.gz??1).toFixed(3)],geoFp:v.geoFp||0,geoHit:v.geoHit||0}))""",
"""      precision:v.precision,watchOnly:v.watchOnly,demotions:v.demotions,recoveries:v.recoveries,
      fpFamilies:Object.keys(v.fpFamilies||{}).length,
      geo:[+(v.gx??1).toFixed(3),+(v.gy??1).toFixed(3),+(v.gz??1).toFixed(3)],geoFp:v.geoFp||0,geoHit:v.geoHit||0}))""",
'calRows geom families')

rep(
"function calibrationSnapshot(){return {config:{...CAL_CFG},family:calRows(CAL_FAMILY,'family'),source:calRows(CAL_SOURCE,'source'),variant:calRows(CAL_VARIANT,'variant')};}",
"function calibrationSnapshot(){return {config:{...CAL_CFG},family:calRows(CAL_FAMILY,'family'),source:calRows(CAL_SOURCE,'source'),variant:calRows(CAL_VARIANT,'variant'),geom:calRows(CAL_GEOM,'geom')};}",
'calibration snapshot geom')

rep(
"""    else for(const [k,r] of Object.entries(src)){const b=calBucket(dst,k);Object.assign(b,JSON.parse(JSON.stringify(r)));b.hitPlayers=b.hitPlayers||{};b.fpPlayers=b.fpPlayers||{};}
  }
  function importCalibration(x){if(!x)return false;importCalRows(CAL_FAMILY,x.family);importCalRows(CAL_SOURCE,x.source);importCalRows(CAL_VARIANT,x.variant);return true;}""",
"""    else for(const [k,r] of Object.entries(src)){const b=calBucket(dst,k);Object.assign(b,JSON.parse(JSON.stringify(r)));b.hitPlayers=b.hitPlayers||{};b.fpPlayers=b.fpPlayers||{};b.fpFamilies=b.fpFamilies||{};}
  }
  function importCalibration(x){if(!x)return false;importCalRows(CAL_FAMILY,x.family);importCalRows(CAL_SOURCE,x.source);importCalRows(CAL_VARIANT,x.variant);importCalRows(CAL_GEOM,x.geom);return true;}""",
'import geom')

rep(
"function calibrationRaw(){return {family:JSON.parse(JSON.stringify(CAL_FAMILY)),source:JSON.parse(JSON.stringify(CAL_SOURCE)),variant:JSON.parse(JSON.stringify(CAL_VARIANT))};}",
"function calibrationRaw(){return {family:JSON.parse(JSON.stringify(CAL_FAMILY)),source:JSON.parse(JSON.stringify(CAL_SOURCE)),variant:JSON.parse(JSON.stringify(CAL_VARIANT)),geom:JSON.parse(JSON.stringify(CAL_GEOM))};}",
'raw geom')

rep(
"function calibrationReset(){for(const k of Object.keys(CAL_FAMILY))delete CAL_FAMILY[k];for(const k of Object.keys(CAL_SOURCE))delete CAL_SOURCE[k];for(const k of Object.keys(CAL_VARIANT))delete CAL_VARIANT[k];self.__WOF_CAL_CACHE=null;qlog('🧹 Family/Variant在线校准已清零');return calibrationSnapshot();}",
"function calibrationReset(){for(const k of Object.keys(CAL_FAMILY))delete CAL_FAMILY[k];for(const k of Object.keys(CAL_SOURCE))delete CAL_SOURCE[k];for(const k of Object.keys(CAL_VARIANT))delete CAL_VARIANT[k];for(const k of Object.keys(CAL_GEOM))delete CAL_GEOM[k];self.__WOF_CAL_CACHE=null;qlog('🧹 Family/Variant/Geometry在线校准已清零');return calibrationSnapshot();}",
'reset geom')

# Array import needs a real fpFamilies object after legacy rows are imported.
rep(
"""if(Array.isArray(src))for(const r of src){if(!r?.key)continue;const b=calBucket(dst,r.key);for(const k of ['hit','fp','ignoredFp','confirmed','precision','watchOnly','demotions','recoveries','gx','gy','gz','geoFp','geoHit'])if(r[k]!=null)b[k]=r[k];if(Array.isArray(r.geo)){b.gx=+r.geo[0]||1;b.gy=+r.geo[1]||1;b.gz=+r.geo[2]||1;}for(let i=0;i<(+r.hitPlayers||0);i++)b.hitPlayers['legacy'+i]=1;for(let i=0;i<(+r.fpPlayers||0);i++)b.fpPlayers['legacy'+i]=1;}""",
"""if(Array.isArray(src))for(const r of src){if(!r?.key)continue;const b=calBucket(dst,r.key);for(const k of ['hit','fp','ignoredFp','confirmed','precision','watchOnly','demotions','recoveries','gx','gy','gz','geoFp','geoHit'])if(r[k]!=null)b[k]=r[k];if(Array.isArray(r.geo)){b.gx=+r.geo[0]||1;b.gy=+r.geo[1]||1;b.gz=+r.geo[2]||1;}for(let i=0;i<(+r.hitPlayers||0);i++)b.hitPlayers['legacy'+i]=1;for(let i=0;i<(+r.fpPlayers||0);i++)b.fpPlayers['legacy'+i]=1;for(let i=0;i<(+r.fpFamilies||0);i++)b.fpFamilies['legacyFamily'+i]=1;}""",
'import legacy fpFamilies')

rep(
"""  const geoAdjusted=[...(c.variant||[]),...(c.source||[])].filter(r=>Array.isArray(r.geo)&&Math.min(...r.geo)<.995)
    .sort((x,y)=>Math.min(...x.geo)-Math.min(...y.geo)).slice(0,20);
  return frozenCopy({at:Date.now(),total,players:a,topFalse,demoted,geoAdjusted});""",
"""  const geoAdjusted=[...(c.variant||[]),...(c.source||[])].filter(r=>Array.isArray(r.geo)&&Math.min(...r.geo)<.995)
    .sort((x,y)=>Math.min(...x.geo)-Math.min(...y.geo)).slice(0,20);
  const geoClasses=(c.geom||[]).filter(r=>Array.isArray(r.geo)&&((r.geoFp||0)>0||Math.min(...r.geo)<.995))
    .sort((x,y)=>(y.geoFp||0)-(x.geoFp||0)).slice(0,20);
  return frozenCopy({at:Date.now(),total,players:a,topFalse,demoted,geoAdjusted,geoClasses});""",
'summary geoClasses')

rep("version:'offline-dynamic-spectator-calibrated-v4.8.2'","version:'offline-dynamic-spectator-calibrated-v4.9'",'version')
rep("qlog('✅ WOF V4.8.2 自适应攻击几何观战版启动');","qlog('✅ WOF V4.9 共享几何类学习观战版启动');",'startup')
rep(
"qlog('📐 自适应几何: 高可信误报只收缩最靠近边界的轴；真实命中会逐步放宽，完整危险外壳始终保留WATCH');",
"qlog('📐 自适应几何: Family/Variant独立学习 + fallback几何类跨Family共享学习；完整危险外壳始终保留WATCH');\n  qlog('🧱 共享几何类: 同一fallback半径至少3次高可信误报且来自>=2个Family才开始收缩行动核心');",
'startup geometry info')

p.write_text(s,encoding='utf-8')
print('patched V4.9',len(s))
