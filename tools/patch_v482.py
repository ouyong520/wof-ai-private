from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.8.1" not in s:
    raise SystemExit('expected V4.8.1 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' target missing')
    s=s.replace(old,new,1)

# Slightly deepen the action core. The full outer shell is still retained as WATCH,
# so this improves directional precision without deleting raw hazard coverage.
rep("actionPenetrationMin:0.10,","actionPenetrationMin:0.15,",'action core 15%')

# Geometry adaptation lives inside existing source/variant calibration buckets so it survives hot reloads.
rep(
"function calBucket(map,key){return map[key]||(map[key]={hit:0,fp:0,ignoredFp:0,confirmed:0,precision:null,watchOnly:false,demotions:0,recoveries:0,hitPlayers:{},fpPlayers:{}});}",
"function calBucket(map,key){return map[key]||(map[key]={hit:0,fp:0,ignoredFp:0,confirmed:0,precision:null,watchOnly:false,demotions:0,recoveries:0,hitPlayers:{},fpPlayers:{},gx:1,gy:1,gz:1,geoFp:0,geoHit:0});}",
'geometry bucket fields')

rep(
"""  function calPolicy(family,source,variant=null){
    const f=CAL_FAMILY[family],k=family+'|'+source,q=CAL_SOURCE[k],vk=variant?(k+'|'+variant):null,v=vk?CAL_VARIANT[vk]:null;
    return {watchOnly:!!(f?.watchOnly||q?.watchOnly||v?.watchOnly),
      familyPrecision:f?.precision??null,familyConfirmed:f?.confirmed||0,
      sourcePrecision:q?.precision??null,sourceConfirmed:q?.confirmed||0,
      variantPrecision:v?.precision??null,variantConfirmed:v?.confirmed||0,variantWatchOnly:!!v?.watchOnly};
  }""",
"""  function calPolicy(family,source,variant=null){
    const f=CAL_FAMILY[family],k=family+'|'+source,q=CAL_SOURCE[k],vk=variant?(k+'|'+variant):null,v=vk?CAL_VARIANT[vk]:null;
    const gx=Math.min(q?.gx??1,v?.gx??1),gy=Math.min(q?.gy??1,v?.gy??1),gz=Math.min(q?.gz??1,v?.gz??1);
    return {watchOnly:!!(f?.watchOnly||q?.watchOnly||v?.watchOnly),
      familyPrecision:f?.precision??null,familyConfirmed:f?.confirmed||0,
      sourcePrecision:q?.precision??null,sourceConfirmed:q?.confirmed||0,
      variantPrecision:v?.precision??null,variantConfirmed:v?.confirmed||0,variantWatchOnly:!!v?.watchOnly,
      geoX:gx,geoY:gy,geoZ:gz};
  }
  function geoAdapt(e,kind,sb,vb){
    if(!e||(!sb&&!vb))return;
    const buckets=[...(vb?[['variant',vb]]:[]),['source',sb]];
    if(kind==='hit'){
      for(const [scope,b] of buckets){
        if(!b)continue;b.geoHit=(b.geoHit||0)+1;
        const step=scope==='variant'?.05:.025;
        b.gx=Math.min(1,(b.gx??1)+step);b.gy=Math.min(1,(b.gy??1)+step);b.gz=Math.min(1,(b.gz??1)+step);
      }
      return;
    }
    if(kind!=='fp'||!calFpEligible(e))return;
    const vals=[['x',+e.rx||1,+e.mx||0],['y',+e.ry||1,+e.my||0],['z',+e.rz||1,+e.mz||0]]
      .map(([axis,r,m])=>({axis,r,m,pen:r>0?m/r:1})).sort((a,b)=>a.pen-b.pen);
    const edge=vals[0];if(!edge||edge.pen<0)return;
    for(const [scope,b] of buckets){
      if(!b)continue;b.geoFp=(b.geoFp||0)+1;
      if(scope==='source'&&b.geoFp<2)continue;
      const prop='g'+edge.axis,cur=b[prop]??1,floor=scope==='variant'?.68:.82;
      const shrink=Math.max(.72,Math.min(.96,1-edge.pen-.025));
      const target=Math.max(floor,cur*shrink);
      if(target<cur)b[prop]=target;
    }
  }""",
'geometry policy/adaptation')

rep(
"""    for(const b of [fb,sb,...(vb?[vb]:[])]){
      if(kind==='hit'){b.hit++;b.hitPlayers[who]=1;}
      else{b.fp++;b.fpPlayers[who]=1;}
    }
    const vf=vb?calRefresh(vb,'variant'):false,sf=calRefresh(sb,'source'),ff=calRefresh(fb,'family'),after=calPolicy(family,source,variant).watchOnly;""",
"""    for(const b of [fb,sb,...(vb?[vb]:[])]){
      if(kind==='hit'){b.hit++;b.hitPlayers[who]=1;}
      else{b.fp++;b.fpPlayers[who]=1;}
    }
    geoAdapt(e,kind,sb,vb);
    const vf=vb?calRefresh(vb,'variant'):false,sf=calRefresh(sb,'source'),ff=calRefresh(fb,'family'),after=calPolicy(family,source,variant).watchOnly;""",
'apply geometry adaptation')

rep(
"""    return Object.entries(map).map(([key,v])=>({scope,key,hit:v.hit,fp:v.fp,ignoredFp:v.ignoredFp,confirmed:v.confirmed,
      hitPlayers:Object.keys(v.hitPlayers||{}).length,fpPlayers:Object.keys(v.fpPlayers||{}).length,
      precision:v.precision,watchOnly:v.watchOnly,demotions:v.demotions,recoveries:v.recoveries}))""",
"""    return Object.entries(map).map(([key,v])=>({scope,key,hit:v.hit,fp:v.fp,ignoredFp:v.ignoredFp,confirmed:v.confirmed,
      hitPlayers:Object.keys(v.hitPlayers||{}).length,fpPlayers:Object.keys(v.fpPlayers||{}).length,
      precision:v.precision,watchOnly:v.watchOnly,demotions:v.demotions,recoveries:v.recoveries,
      geo:[+(v.gx??1).toFixed(3),+(v.gy??1).toFixed(3),+(v.gz??1).toFixed(3)],geoFp:v.geoFp||0,geoHit:v.geoHit||0}))""",
'geometry report rows')

rep(
"for(const k of ['hit','fp','ignoredFp','confirmed','precision','watchOnly','demotions','recoveries'])if(r[k]!=null)b[k]=r[k];",
"for(const k of ['hit','fp','ignoredFp','confirmed','precision','watchOnly','demotions','recoveries','gx','gy','gz','geoFp','geoHit'])if(r[k]!=null)b[k]=r[k];if(Array.isArray(r.geo)){b.gx=+r.geo[0]||1;b.gy=+r.geo[1]||1;b.gz=+r.geo[2]||1;}",
'import geometry fields')

# Attach learned geometry scale to each known hazard.
rep(
"""            calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
            calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),""",
"""            calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
            calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),geoScale:{x:cal.geoX,y:cal.geoY,z:cal.geoZ},""",
'startup geo scale')
rep(
"""        calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
        calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),""",
"""        calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
        calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),geoScale:{x:cal.geoX,y:cal.geoY,z:cal.geoZ},""",
'active geo scale')

# Apply adaptive scales only to the action core. fullCur remains untouched and still produces WATCH.
rep(
"""  const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false)
    .map(d=>d.geometryFallback?{...d,rx:d.actionRx,ry:d.actionRy,rz:d.actionRz,geometryCore:true}:d)
    .map(d=>({...d,
      rx:Math.max(1,d.rx*(1-CFG.actionPenetrationMin)),
      ry:Math.max(1,d.ry*(1-CFG.actionPenetrationMin)),
      rz:Math.max(1,d.rz*(1-CFG.actionPenetrationMin)),
      actionPenetrationCore:true}));""",
"""  const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false)
    .map(d=>d.geometryFallback?{...d,rx:d.actionRx,ry:d.actionRy,rz:d.actionRz,geometryCore:true}:d)
    .map(d=>{const g=d.geoScale||{x:1,y:1,z:1};return {...d,
      rx:Math.max(1,d.rx*(g.x??1)*(1-CFG.actionPenetrationMin)),
      ry:Math.max(1,d.ry*(g.y??1)*(1-CFG.actionPenetrationMin)),
      rz:Math.max(1,d.rz*(g.z??1)*(1-CFG.actionPenetrationMin)),
      learnedGeometry:true,actionPenetrationCore:true};});""",
'apply learned action geometry')

# Preserve the exact learned scale that produced each audited collision.
rep(
"""      rx,ry,rz,confidence:+h.confidence||0,survival:h.survival==null?1:+h.survival,
      mx:rx-Math.abs(pp.x-(+h.x||0)),my:ry-Math.abs(pp.y-(+h.y||0)),mz:rz-Math.abs(pp.z-(+h.z||0)),""",
"""      rx,ry,rz,geoScale:h.geoScale?{...h.geoScale}:null,confidence:+h.confidence||0,survival:h.survival==null?1:+h.survival,
      mx:rx-Math.abs(pp.x-(+h.x||0)),my:ry-Math.abs(pp.y-(+h.y||0)),mz:rz-Math.abs(pp.z-(+h.z||0)),""",
'audit learned geometry')

# Short report exposes the strongest online geometry corrections.
rep(
"""  const demoted=[...(c.variant||[]),...(c.source||[]),...(c.family||[])].filter(r=>r.watchOnly).slice(0,20);
  return frozenCopy({at:Date.now(),total,players:a,topFalse,demoted});""",
"""  const demoted=[...(c.variant||[]),...(c.source||[]),...(c.family||[])].filter(r=>r.watchOnly).slice(0,20);
  const geoAdjusted=[...(c.variant||[]),...(c.source||[])].filter(r=>Array.isArray(r.geo)&&Math.min(...r.geo)<.995)
    .sort((x,y)=>Math.min(...x.geo)-Math.min(...y.geo)).slice(0,20);
  return frozenCopy({at:Date.now(),total,players:a,topFalse,demoted,geoAdjusted});""",
'geometry short report')

rep("version:'offline-dynamic-spectator-calibrated-v4.8.1'","version:'offline-dynamic-spectator-calibrated-v4.8.2'",'version')
rep("qlog('✅ WOF V4.8.1 Variant稳定性/真实漏判审计版启动');","qlog('✅ WOF V4.8.2 自适应攻击几何观战版启动');",'startup')
rep(
"qlog('🧬 Variant: 坏分支2次高可信误报即可WATCH；Family/source恢复为慢速安全兜底');",
"qlog('🧬 Variant: 坏分支2次高可信误报即可WATCH；Family/source保持慢速安全兜底');\n  qlog('📐 自适应几何: 高可信误报只收缩最靠近边界的轴；真实命中会逐步放宽，完整危险外壳始终保留WATCH');",
'startup adaptive geometry info')

p.write_text(s,encoding='utf-8')
print('patched V4.8.2',len(s))
