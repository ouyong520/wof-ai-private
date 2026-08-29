from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.9.1" not in s:
    raise SystemExit('expected V4.9.1 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,1)

# Precision-first online gating. A high-confidence false positive is useful evidence:
# keep the full hazard as WATCH, but stop issuing directional/AB advice from that branch.
rep(
"""    variantDemoteConfirmed:2,variantDemoteFp:2,variantDemotePrecision:.20,
    variantRecoverConfirmed:5,variantRecoverHit:2,variantRecoverPrecision:.50,
    activeFpMinConfidence:.50,startupFpMinConfidence:.25,fpMinSurvival:.50""",
"""    variantDemoteConfirmed:2,variantDemoteFp:2,variantDemotePrecision:.20,
    variantRecoverConfirmed:5,variantRecoverHit:2,variantRecoverPrecision:.50,
    precisionVariantFp:1,precisionSourceConfirmed:3,precisionSourceMax:.20,
    precisionFamilyConfirmed:5,precisionFamilyMax:.20,
    trustUnseenActive:.78,trustUnseenStartup:.84,trustBadEvidence:.72,trustFamilyHit:.88,trustSourceHit:.93,
    activeFpMinConfidence:.50,startupFpMinConfidence:.25,fpMinSurvival:.50""",
'precision config')

rep(
"""  function calPolicy(family,source,variant=null){
    const f=CAL_FAMILY[family],k=family+'|'+source,q=CAL_SOURCE[k],vk=variant?(k+'|'+variant):null,v=vk?CAL_VARIANT[vk]:null;
    const gx=Math.min(q?.gx??1,v?.gx??1),gy=Math.min(q?.gy??1,v?.gy??1),gz=Math.min(q?.gz??1,v?.gz??1);
    return {watchOnly:!!(f?.watchOnly||q?.watchOnly||v?.watchOnly),
      familyPrecision:f?.precision??null,familyConfirmed:f?.confirmed||0,
      sourcePrecision:q?.precision??null,sourceConfirmed:q?.confirmed||0,
      variantPrecision:v?.precision??null,variantConfirmed:v?.confirmed||0,variantWatchOnly:!!v?.watchOnly,
      geoX:gx,geoY:gy,geoZ:gz};
  }""",
"""  function calPolicy(family,source,variant=null){
    const f=CAL_FAMILY[family],k=family+'|'+source,q=CAL_SOURCE[k],vk=variant?(k+'|'+variant):null,v=vk?CAL_VARIANT[vk]:null;
    const gx=Math.min(q?.gx??1,v?.gx??1),gy=Math.min(q?.gy??1,v?.gy??1),gz=Math.min(q?.gz??1,v?.gz??1);
    const variantBad=!!(v&&(v.fp||0)>=CAL_CFG.precisionVariantFp&&(v.hit||0)===0);
    const sourceBad=!!(q&&(q.confirmed||0)>=CAL_CFG.precisionSourceConfirmed&&(q.precision??1)<=CAL_CFG.precisionSourceMax&&(q.hit||0)===0);
    const familyBad=!!(f&&(f.confirmed||0)>=CAL_CFG.precisionFamilyConfirmed&&(f.precision??1)<=CAL_CFG.precisionFamilyMax&&(f.hit||0)<=1);
    const precisionWatch=variantBad||sourceBad||familyBad;
    let trustScale=source==='active'?CAL_CFG.trustUnseenActive:CAL_CFG.trustUnseenStartup;
    let trustReason='unseen';
    if(variantBad||sourceBad||familyBad){trustScale=CAL_CFG.trustBadEvidence;trustReason=variantBad?'variant-fp':sourceBad?'source-low-precision':'family-low-precision';}
    else if((v?.hit||0)>0){trustScale=1;trustReason='variant-hit';}
    else if((q?.hit||0)>0){trustScale=CAL_CFG.trustSourceHit;trustReason='source-hit';}
    else if((f?.hit||0)>0){trustScale=CAL_CFG.trustFamilyHit;trustReason='family-hit';}
    return {watchOnly:!!(f?.watchOnly||q?.watchOnly||v?.watchOnly||precisionWatch),precisionWatch,trustScale,trustReason,
      familyPrecision:f?.precision??null,familyConfirmed:f?.confirmed||0,
      sourcePrecision:q?.precision??null,sourceConfirmed:q?.confirmed||0,
      variantPrecision:v?.precision??null,variantConfirmed:v?.confirmed||0,variantWatchOnly:!!v?.watchOnly,
      geoX:gx,geoY:gy,geoZ:gz};
  }""",
'calPolicy trust gating')

# Carry trust data into every known hazard point.
rep(
"""            calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
            calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),geoScale:{x:cal.geoX,y:cal.geoY,z:cal.geoZ},""",
"""            calWatchOnly:cal.watchOnly,precisionWatch:cal.precisionWatch,trustScale:cal.trustScale,trustReason:cal.trustReason,
            calPrecision:cal.sourcePrecision??cal.familyPrecision,
            calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),geoScale:{x:cal.geoX,y:cal.geoY,z:cal.geoZ},""",
'startup trust fields')
rep(
"""        calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
        calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),geoScale:{x:cal.geoX,y:cal.geoY,z:cal.geoZ},""",
"""        calWatchOnly:cal.watchOnly,precisionWatch:cal.precisionWatch,trustScale:cal.trustScale,trustReason:cal.trustReason,
        calPrecision:cal.sourcePrecision??cal.familyPrecision,
        calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),geoScale:{x:cal.geoX,y:cal.geoY,z:cal.geoZ},""",
'active trust fields')

# Low-evidence hazards use a smaller action core, but urgent <=250 ms danger gets a 0.90 floor.
# The full outer hazard remains unchanged and therefore still generates WATCH.
rep(
"""    .map(d=>{const g=d.geoScale||{x:1,y:1,z:1};return {...d,
      rx:Math.max(1,d.rx*(g.x??1)*(1-CFG.actionPenetrationMin)),
      ry:Math.max(1,d.ry*(g.y??1)*(1-CFG.actionPenetrationMin)),
      rz:Math.max(1,d.rz*(g.z??1)*(1-CFG.actionPenetrationMin)),
      learnedGeometry:true,actionPenetrationCore:true};});""",
"""    .map(d=>{const g=d.geoScale||{x:1,y:1,z:1};
      const trust=d.t<=250?Math.max(.90,d.trustScale??1):(d.trustScale??1);
      return {...d,effectiveTrust:trust,
      rx:Math.max(1,d.rx*(g.x??1)*trust*(1-CFG.actionPenetrationMin)),
      ry:Math.max(1,d.ry*(g.y??1)*trust*(1-CFG.actionPenetrationMin)),
      rz:Math.max(1,d.rz*(g.z??1)*trust*(1-CFG.actionPenetrationMin)),
      learnedGeometry:true,actionPenetrationCore:true};});""",
'action trust core')

# Surface precision quarantines in the compact report.
rep(
"""  const validated=total.hit+total.falsePositive;
  const damageEvents=total.hit+total.ambiguousDamage+total.unstableCovered+total.safeMiss;""",
"""  const precisionSuppressed=[
    ...(c.variant||[]).filter(r=>(r.fp||0)>=CAL_CFG.precisionVariantFp&&(r.hit||0)===0),
    ...(c.source||[]).filter(r=>(r.confirmed||0)>=CAL_CFG.precisionSourceConfirmed&&(r.precision??1)<=CAL_CFG.precisionSourceMax&&(r.hit||0)===0),
    ...(c.family||[]).filter(r=>(r.confirmed||0)>=CAL_CFG.precisionFamilyConfirmed&&(r.precision??1)<=CAL_CFG.precisionFamilyMax&&(r.hit||0)<=1)
  ].slice(0,20);
  const validated=total.hit+total.falsePositive;
  const damageEvents=total.hit+total.ambiguousDamage+total.unstableCovered+total.safeMiss;""",
'precisionSuppressed report')
rep(
"return frozenCopy({at:Date.now(),total,metrics,players:a,topFalse,demoted,geoAdjusted,geoClasses,missCases:MISS_CASES.slice(-8)});",
"return frozenCopy({at:Date.now(),total,metrics,players:a,topFalse,demoted,precisionSuppressed,geoAdjusted,geoClasses,missCases:MISS_CASES.slice(-8)});",
'summary precisionSuppressed')

rep("version:'offline-dynamic-spectator-calibrated-v4.9.1'","version:'offline-dynamic-spectator-calibrated-v4.9.2'",'version')
rep("qlog('✅ WOF V4.9.1 漏判取证/紧急稳定观战版启动');","qlog('✅ WOF V4.9.2 精度优先信任门控观战版启动');",'startup')
rep(
"qlog('🧬 Variant: 坏分支2次高可信误报即可WATCH；Family/source保持慢速安全兜底');",
"qlog('🎯 精度优先: Variant首次高可信误报即隔离为WATCH；低精度source/family会联动隔离，新分支使用更小行动核心');",
'startup precision info')
rep(
"qlog('⚡ 稳定器: WATCH与<=300ms紧急UP/DOWN改为2帧确认；AB仍需3帧');",
"qlog('⚡ 稳定器: WATCH与<=300ms紧急UP/DOWN为2帧确认；AB仍需3帧；<=250ms危险保留较宽紧急核心');",
'startup urgent info')

p.write_text(s,encoding='utf-8')
print('patched V4.9.2',len(s))
