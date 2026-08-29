from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')

if "offline-dynamic-spectator-p123-v4.3.7" not in s:
    raise SystemExit('expected V4.3.7 input')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} patch target missing')
    s=s.replace(old,new,1)

# Shared cross-player Family reliability calibration.  This is deliberately conservative:
# bad Families are demoted to WATCH-only, never deleted from the danger map.
needle="""  const getFamily=id=>DB.f[id]||null;
  function radius(f){return {rx:(+f[3]||115)+CFG.padX,ry:(+f[4]||22)+CFG.padY,rz:(+f[5]||8)+CFG.padZ};}

  function lookup(o){"""
insert="""  const getFamily=id=>DB.f[id]||null;
  function radius(f){return {rx:(+f[3]||115)+CFG.padX,ry:(+f[4]||22)+CFG.padY,rz:(+f[5]||8)+CFG.padZ};}

  // Cross-player online reliability. P1/P2/P3 all contribute to the same Family evidence.
  // Only confirmed hit/fp events enter this table. Demotion affects actionability only.
  const CAL_FAMILY=Object.create(null),CAL_SOURCE=Object.create(null);
  const CAL_CFG={
    sourceDemoteConfirmed:6,sourceDemoteFp:5,sourceDemotePrecision:.25,
    sourceRecoverConfirmed:10,sourceRecoverHit:4,sourceRecoverPrecision:.50,
    familyDemoteConfirmed:10,familyDemoteFp:7,familyDemotePrecision:.30,
    familyRecoverConfirmed:16,familyRecoverHit:6,familyRecoverPrecision:.50,
    activeFpMinConfidence:.50,startupFpMinConfidence:.25,fpMinSurvival:.50
  };
  function calBucket(map,key){return map[key]||(map[key]={hit:0,fp:0,ignoredFp:0,confirmed:0,precision:null,watchOnly:false,demotions:0,recoveries:0});}
  function calRefresh(b,scope){
    b.confirmed=b.hit+b.fp;b.precision=b.confirmed?b.hit/b.confirmed:null;
    const was=b.watchOnly;
    if(!was){
      if(scope==='source')b.watchOnly=b.confirmed>=CAL_CFG.sourceDemoteConfirmed&&b.fp>=CAL_CFG.sourceDemoteFp&&b.precision<=CAL_CFG.sourceDemotePrecision;
      else b.watchOnly=b.confirmed>=CAL_CFG.familyDemoteConfirmed&&b.fp>=CAL_CFG.familyDemoteFp&&b.precision<=CAL_CFG.familyDemotePrecision;
      if(b.watchOnly)b.demotions++;
    }else{
      if(scope==='source')b.watchOnly=!(b.confirmed>=CAL_CFG.sourceRecoverConfirmed&&b.hit>=CAL_CFG.sourceRecoverHit&&b.precision>=CAL_CFG.sourceRecoverPrecision);
      else b.watchOnly=!(b.confirmed>=CAL_CFG.familyRecoverConfirmed&&b.hit>=CAL_CFG.familyRecoverHit&&b.precision>=CAL_CFG.familyRecoverPrecision);
      if(!b.watchOnly)b.recoveries++;
    }
    return was!==b.watchOnly;
  }
  function calPolicy(family,source){
    const f=CAL_FAMILY[family],k=family+'|'+source,q=CAL_SOURCE[k];
    return {watchOnly:!!(f?.watchOnly||q?.watchOnly),
      familyPrecision:f?.precision??null,familyConfirmed:f?.confirmed||0,
      sourcePrecision:q?.precision??null,sourceConfirmed:q?.confirmed||0};
  }
  function calFpEligible(e){
    if((+e.survival||0)<CAL_CFG.fpMinSurvival)return false;
    const c=+e.confidence||0;
    return e.source==='active'?c>=CAL_CFG.activeFpMinConfidence:c>=CAL_CFG.startupFpMinConfidence;
  }
  function calRecord(e,kind){
    if(!e?.family||(kind!=='hit'&&kind!=='fp'))return;
    const family=e.family,source=e.source||'?',fb=calBucket(CAL_FAMILY,family),sb=calBucket(CAL_SOURCE,family+'|'+source);
    if(kind==='fp'&&!calFpEligible(e)){fb.ignoredFp++;sb.ignoredFp++;return;}
    const before=calPolicy(family,source).watchOnly;
    for(const b of [fb,sb]){if(kind==='hit')b.hit++;else b.fp++;}
    const sf=calRefresh(sb,'source'),ff=calRefresh(fb,'family'),after=calPolicy(family,source).watchOnly;
    if(!before&&after){
      console.log('🧯 Family降级WATCH',family,source,'source',sb.hit+'/'+sb.confirmed,'p',sb.precision?.toFixed(2),'family',fb.hit+'/'+fb.confirmed,'p',fb.precision?.toFixed(2));
    }else if(before&&!after){
      console.log('♻️ Family恢复行动',family,source,'source',sb.hit+'/'+sb.confirmed,'p',sb.precision?.toFixed(2),'family',fb.hit+'/'+fb.confirmed,'p',fb.precision?.toFixed(2));
    }else if((sf||ff)&&after){
      // A second scope can cross its threshold while the Family is already demoted; no extra spam.
    }
  }
  function calRows(map,scope){
    return Object.entries(map).map(([key,v])=>({scope,key,hit:v.hit,fp:v.fp,ignoredFp:v.ignoredFp,confirmed:v.confirmed,
      precision:v.precision,watchOnly:v.watchOnly,demotions:v.demotions,recoveries:v.recoveries}))
      .sort((a,b)=>(Number(b.watchOnly)-Number(a.watchOnly))||(b.fp-a.fp)||(b.confirmed-a.confirmed));
  }
  function calibrationSnapshot(){return {config:{...CAL_CFG},family:calRows(CAL_FAMILY,'family'),source:calRows(CAL_SOURCE,'source')};}
  function calibrationReset(){for(const k of Object.keys(CAL_FAMILY))delete CAL_FAMILY[k];for(const k of Object.keys(CAL_SOURCE))delete CAL_SOURCE[k];console.log('🧹 Family在线校准已清零');return calibrationSnapshot();}

  function lookup(o){"""
replace_once(needle,insert,'calibration helpers')

# Inject calibration policy into startup danger points.
replace_once(
"""          const survival=Math.max(0,Math.min(1,sw.survival??1));
          const confidence=hazard*fc.p*l.w*survival;
          if(confidence<CFG.minConfidence)continue;
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,
            rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:fc.id,
            confidence,survival,actionable:survival>=CFG.survivalActionThreshold,source:'startup',lookup:hit.kind});""",
"""          const survival=Math.max(0,Math.min(1,sw.survival??1));
          const confidence=hazard*fc.p*l.w*survival;
          if(confidence<CFG.minConfidence)continue;
          const cal=calPolicy(fc.id,'startup');
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,
            rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:fc.id,
            confidence,survival,actionable:survival>=CFG.survivalActionThreshold&&!cal.watchOnly,
            calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
            calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),source:'startup',lookup:hit.kind});""",
'startup calibration gate')

# Inject calibration policy into active danger points.
replace_once(
"""      const survival=Math.max(0,Math.min(1,sw.survival??1));
      if(survival<CFG.minConfidence)continue;
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,
        rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:s.locked,
        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold,source:'active'});""",
"""      const survival=Math.max(0,Math.min(1,sw.survival??1));
      if(survival<CFG.minConfidence)continue;
      const cal=calPolicy(s.locked,'active');
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,
        rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:s.locked,
        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold&&!cal.watchOnly,
        calWatchOnly:cal.watchOnly,calPrecision:cal.sourcePrecision??cal.familyPrecision,
        calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),source:'active'});""",
'active calibration gate')

# Demoted Families are WATCH-only but must keep being audited so they can recover.
replace_once(
"if(h.family==null||h.source==='active-unknown'||h.actionable===false)return;",
"if(h.family==null||h.source==='active-unknown'||(h.actionable===false&&!h.calWatchOnly))return;",
'audit demoted-family continuation')

# Shared calibration only consumes resolved true hit / high-confidence false positive evidence.
replace_once(
"""  if(kind==='hit'){
    A.stats.hit++;F.hit++;""",
"""  if(kind==='hit'){
    A.stats.hit++;F.hit++;calRecord(e,'hit');""",
'calibration hit record')
replace_once(
"""  }else if(kind==='fp'){
    A.stats.falsePositive++;F.falsePositive++;""",
"""  }else if(kind==='fp'){
    A.stats.falsePositive++;F.falsePositive++;calRecord(e,'fp');""",
'calibration fp record')

# Expose calibration state/API.
replace_once(
"""    audit(){return auditSnapshot();},
    auditFamilies(){return auditFamilies();},
    stop(){if(timer){clearInterval(timer);timer=null;}console.log('⛔ WOF V4关闭');}""",
"""    audit(){return auditSnapshot();},
    auditFamilies(){return auditFamilies();},
    calibration(){return calibrationSnapshot();},
    resetCalibration(){return calibrationReset();},
    stop(){if(timer){clearInterval(timer);timer=null;}console.log('⛔ WOF V4关闭');}""",
'calibration API')

replace_once("version:'offline-dynamic-spectator-p123-v4.3.7'","version:'offline-dynamic-spectator-calibrated-v4.4'",'version')
replace_once("console.log('✅ WOF V4.3.7 全玩家观战预测版启动');","console.log('✅ WOF V4.4 跨玩家Family在线校准观战版启动');",'startup version')
replace_once(
"console.log('✅ 纯观战：不判断本机seat，同时预测 RAM 中存在的 P1/P2/P3 × 20怪 × Future Danger Map');",
"console.log('✅ 纯观战：P1/P2/P3共享Family可靠性；低精度Family自动降为WATCH，不删除危险点');\n  console.log('🧯 在线校准: 多次高可信误报→WATCH；后续真实命中足够→♻️恢复行动');",
'calibration startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.4',len(s))
