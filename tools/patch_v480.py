from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.7" not in s:
    raise SystemExit('expected V4.7 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' target missing')
    s=s.replace(old,new,1)

# Preserve existing calibration across hot script reloads. V4.7 exposes calibration(), while V4.8+
# exposes exportCalibration(); either form can seed the new runtime.
rep(
"function __WOF_START_V4(DB){\n  try{ self.WOFV4?.stop?.(); }catch(e){}",
"function __WOF_START_V4(DB){\n  let __WOF_PREV_CAL=null;\n  try{__WOF_PREV_CAL=self.WOFV4?.exportCalibration?.()||self.WOFV4?.calibration?.()||self.__WOF_CAL_CACHE||null;}catch(e){}\n  try{ self.WOFV4?.stop?.(); }catch(e){}",
'capture previous calibration')

# Add context-variant calibration. Family/source remain the safety backstop; variant can demote a bad
# anim/state/motion branch without poisoning every branch in the whole Family.
rep(
"const CAL_FAMILY=Object.create(null),CAL_SOURCE=Object.create(null);",
"const CAL_FAMILY=Object.create(null),CAL_SOURCE=Object.create(null),CAL_VARIANT=Object.create(null);",
'variant calibration map')

rep(
"""    familyDemoteConfirmed:3,familyDemoteFp:3,familyDemoteFpPlayers:1,familyDemotePrecision:.30,
    familyRecoverConfirmed:7,familyRecoverHit:3,familyRecoverPrecision:.50,
    activeFpMinConfidence:.50,startupFpMinConfidence:.25,fpMinSurvival:.50""",
"""    familyDemoteConfirmed:3,familyDemoteFp:3,familyDemoteFpPlayers:1,familyDemotePrecision:.30,
    familyRecoverConfirmed:7,familyRecoverHit:3,familyRecoverPrecision:.50,
    variantDemoteConfirmed:3,variantDemoteFp:3,variantDemotePrecision:.20,
    variantRecoverConfirmed:6,variantRecoverHit:3,variantRecoverPrecision:.50,
    activeFpMinConfidence:.50,startupFpMinConfidence:.25,fpMinSurvival:.50""",
'variant thresholds')

rep(
"""      if(scope==='source')b.watchOnly=b.confirmed>=CAL_CFG.sourceDemoteConfirmed&&b.fp>=CAL_CFG.sourceDemoteFp&&fpPlayers>=CAL_CFG.sourceDemoteFpPlayers&&b.precision<=CAL_CFG.sourceDemotePrecision;
      else b.watchOnly=b.confirmed>=CAL_CFG.familyDemoteConfirmed&&b.fp>=CAL_CFG.familyDemoteFp&&fpPlayers>=CAL_CFG.familyDemoteFpPlayers&&b.precision<=CAL_CFG.familyDemotePrecision;""",
"""      if(scope==='variant')b.watchOnly=b.confirmed>=CAL_CFG.variantDemoteConfirmed&&b.fp>=CAL_CFG.variantDemoteFp&&b.precision<=CAL_CFG.variantDemotePrecision;
      else if(scope==='source')b.watchOnly=b.confirmed>=CAL_CFG.sourceDemoteConfirmed&&b.fp>=CAL_CFG.sourceDemoteFp&&fpPlayers>=CAL_CFG.sourceDemoteFpPlayers&&b.precision<=CAL_CFG.sourceDemotePrecision;
      else b.watchOnly=b.confirmed>=CAL_CFG.familyDemoteConfirmed&&b.fp>=CAL_CFG.familyDemoteFp&&fpPlayers>=CAL_CFG.familyDemoteFpPlayers&&b.precision<=CAL_CFG.familyDemotePrecision;""",
'variant demotion')

rep(
"""      if(scope==='source')b.watchOnly=!(b.confirmed>=CAL_CFG.sourceRecoverConfirmed&&b.hit>=CAL_CFG.sourceRecoverHit&&b.precision>=CAL_CFG.sourceRecoverPrecision);
      else b.watchOnly=!(b.confirmed>=CAL_CFG.familyRecoverConfirmed&&b.hit>=CAL_CFG.familyRecoverHit&&b.precision>=CAL_CFG.familyRecoverPrecision);""",
"""      if(scope==='variant')b.watchOnly=!(b.confirmed>=CAL_CFG.variantRecoverConfirmed&&b.hit>=CAL_CFG.variantRecoverHit&&b.precision>=CAL_CFG.variantRecoverPrecision);
      else if(scope==='source')b.watchOnly=!(b.confirmed>=CAL_CFG.sourceRecoverConfirmed&&b.hit>=CAL_CFG.sourceRecoverHit&&b.precision>=CAL_CFG.sourceRecoverPrecision);
      else b.watchOnly=!(b.confirmed>=CAL_CFG.familyRecoverConfirmed&&b.hit>=CAL_CFG.familyRecoverHit&&b.precision>=CAL_CFG.familyRecoverPrecision);""",
'variant recovery')

rep(
"""  function calPolicy(family,source){
    const f=CAL_FAMILY[family],k=family+'|'+source,q=CAL_SOURCE[k];
    return {watchOnly:!!(f?.watchOnly||q?.watchOnly),
      familyPrecision:f?.precision??null,familyConfirmed:f?.confirmed||0,
      sourcePrecision:q?.precision??null,sourceConfirmed:q?.confirmed||0};
  }""",
"""  function calPolicy(family,source,variant=null){
    const f=CAL_FAMILY[family],k=family+'|'+source,q=CAL_SOURCE[k],vk=variant?(k+'|'+variant):null,v=vk?CAL_VARIANT[vk]:null;
    return {watchOnly:!!(f?.watchOnly||q?.watchOnly||v?.watchOnly),
      familyPrecision:f?.precision??null,familyConfirmed:f?.confirmed||0,
      sourcePrecision:q?.precision??null,sourceConfirmed:q?.confirmed||0,
      variantPrecision:v?.precision??null,variantConfirmed:v?.confirmed||0,variantWatchOnly:!!v?.watchOnly};
  }""",
'variant policy')

rep(
"""    const family=e.family,source=e.source||'?',fb=calBucket(CAL_FAMILY,family),sb=calBucket(CAL_SOURCE,family+'|'+source);
    if(kind==='fp'&&!calFpEligible(e)){fb.ignoredFp++;sb.ignoredFp++;return;}
    const before=calPolicy(family,source).watchOnly;
    const who=e.player||'?';
    for(const b of [fb,sb]){
      if(kind==='hit'){b.hit++;b.hitPlayers[who]=1;}
      else{b.fp++;b.fpPlayers[who]=1;}
    }
    const sf=calRefresh(sb,'source'),ff=calRefresh(fb,'family'),after=calPolicy(family,source).watchOnly;""",
"""    const family=e.family,source=e.source||'?',variant=e.variant||null,fb=calBucket(CAL_FAMILY,family),sb=calBucket(CAL_SOURCE,family+'|'+source),vb=variant?calBucket(CAL_VARIANT,family+'|'+source+'|'+variant):null;
    if(kind==='fp'&&!calFpEligible(e)){fb.ignoredFp++;sb.ignoredFp++;if(vb)vb.ignoredFp++;return;}
    const before=calPolicy(family,source,variant).watchOnly;
    const who=e.player||'?';
    for(const b of [fb,sb,...(vb?[vb]:[])]){
      if(kind==='hit'){b.hit++;b.hitPlayers[who]=1;}
      else{b.fp++;b.fpPlayers[who]=1;}
    }
    const vf=vb?calRefresh(vb,'variant'):false,sf=calRefresh(sb,'source'),ff=calRefresh(fb,'family'),after=calPolicy(family,source,variant).watchOnly;""",
'variant record')

rep(
"""      qlog('🧯 Family降级WATCH',family,source,'source',sb.hit+'/'+sb.confirmed,'p',sb.precision?.toFixed(2),'family',fb.hit+'/'+fb.confirmed,'p',fb.precision?.toFixed(2));""",
"""      qlog(vb?.watchOnly?'🧬 Variant降级WATCH':'🧯 Family降级WATCH',family,source,variant||'',
        'variant',vb?(vb.hit+'/'+vb.confirmed):'-','source',sb.hit+'/'+sb.confirmed,'family',fb.hit+'/'+fb.confirmed);""",
'demotion log')

rep(
"""    }else if((sf||ff)&&after){
      // A second scope can cross its threshold while the Family is already demoted; no extra spam.
    }
  }""",
"""    }else if((vf||sf||ff)&&after){
      // A second scope can cross its threshold while the branch is already demoted; no extra spam.
    }
    self.__WOF_CAL_CACHE={family:JSON.parse(JSON.stringify(CAL_FAMILY)),source:JSON.parse(JSON.stringify(CAL_SOURCE)),variant:JSON.parse(JSON.stringify(CAL_VARIANT))};
  }""",
'persist calibration after record')

rep(
"""  function calibrationSnapshot(){return {config:{...CAL_CFG},family:calRows(CAL_FAMILY,'family'),source:calRows(CAL_SOURCE,'source')};}
  function calibrationReset(){for(const k of Object.keys(CAL_FAMILY))delete CAL_FAMILY[k];for(const k of Object.keys(CAL_SOURCE))delete CAL_SOURCE[k];qlog('🧹 Family在线校准已清零');return calibrationSnapshot();}""",
"""  function calibrationSnapshot(){return {config:{...CAL_CFG},family:calRows(CAL_FAMILY,'family'),source:calRows(CAL_SOURCE,'source'),variant:calRows(CAL_VARIANT,'variant')};}
  function importCalRows(dst,src){
    if(!src)return;
    if(Array.isArray(src))for(const r of src){if(!r?.key)continue;const b=calBucket(dst,r.key);for(const k of ['hit','fp','ignoredFp','confirmed','precision','watchOnly','demotions','recoveries'])if(r[k]!=null)b[k]=r[k];for(let i=0;i<(+r.hitPlayers||0);i++)b.hitPlayers['legacy'+i]=1;for(let i=0;i<(+r.fpPlayers||0);i++)b.fpPlayers['legacy'+i]=1;}
    else for(const [k,r] of Object.entries(src)){const b=calBucket(dst,k);Object.assign(b,JSON.parse(JSON.stringify(r)));b.hitPlayers=b.hitPlayers||{};b.fpPlayers=b.fpPlayers||{};}
  }
  function importCalibration(x){if(!x)return false;importCalRows(CAL_FAMILY,x.family);importCalRows(CAL_SOURCE,x.source);importCalRows(CAL_VARIANT,x.variant);return true;}
  importCalibration(__WOF_PREV_CAL||self.__WOF_CAL_CACHE);
  function calibrationRaw(){return {family:JSON.parse(JSON.stringify(CAL_FAMILY)),source:JSON.parse(JSON.stringify(CAL_SOURCE)),variant:JSON.parse(JSON.stringify(CAL_VARIANT))};}
  function calibrationReset(){for(const k of Object.keys(CAL_FAMILY))delete CAL_FAMILY[k];for(const k of Object.keys(CAL_SOURCE))delete CAL_SOURCE[k];for(const k of Object.keys(CAL_VARIANT))delete CAL_VARIANT[k];self.__WOF_CAL_CACHE=null;qlog('🧹 Family/Variant在线校准已清零');return calibrationSnapshot();}""",
'import and reset variant calibration')

# Add stable variant signatures. Startup uses anim+state+lookup level. Active additionally freezes an
# early 80ms motion band, which separates stationary/dash/jump branches that were merged offline.
rep(
"const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0,seq:0}));",
"const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0,seq:0,variantBase:null,variantMotion:null}));",
'slot variant fields')
rep(
"if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.seq=0;}",
"if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.seq=0;s.variantBase=null;s.variantMotion=null;}",
'variant slot reset on type')
rep(
"""      s.started=now;s.origin={x:o.x,y:o.y,z:o.z};s.face=o.face;
    }else if(s.prevAttack!==0&&o.attack===0){s.locked=null;s.origin=null;s.started=0;}
    s.prevAttack=o.attack;""",
"""      s.started=now;s.origin={x:o.x,y:o.y,z:o.z};s.face=o.face;
      s.variantBase='a'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3;s.variantMotion=null;
    }else if(s.prevAttack!==0&&o.attack===0){s.locked=null;s.origin=null;s.started=0;s.variantBase=null;s.variantMotion=null;}
    if(o.attack!==0&&s.origin&&s.variantMotion==null&&now-s.started>=80){
      const sg=faceSign(s.face),dx=sg*(o.x-s.origin.x),dy=o.y-s.origin.y,dz=o.z-s.origin.z;
      s.variantMotion='m'+Math.round(dx/16)+','+Math.round(dy/8)+','+Math.round(dz/8);
    }
    s.prevAttack=o.attack;""",
'active motion variant')

rep(
"""          const cal=calPolicy(fc.id,'startup');
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,""",
"""          const variant='s'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3+':'+hit.kind;
          const cal=calPolicy(fc.id,'startup',variant);
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,""",
'startup variant policy')
rep(
"""            slot:o.slot,type:o.type,family:fc.id,
            confidence,survival,actionable:survival>=CFG.survivalActionThreshold&&confidence>=CFG.startupActionMinConfidence&&!cal.watchOnly,""",
"""            slot:o.slot,type:o.type,family:fc.id,variant,
            confidence,survival,actionable:survival>=CFG.survivalActionThreshold&&confidence>=CFG.startupActionMinConfidence&&!cal.watchOnly,""",
'startup variant hazard')
rep(
"""      const cal=calPolicy(s.locked,'active');
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,""",
"""      const variant=(s.variantBase||'a?')+'|'+(s.variantMotion||'early');
      const cal=calPolicy(s.locked,'active',variant);
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,""",
'active variant policy')
rep(
"""        slot:o.slot,type:o.type,family:s.locked,
        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold&&survival>=CFG.activeActionMinConfidence&&!cal.watchOnly,""",
"""        slot:o.slot,type:o.type,family:s.locked,variant,
        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold&&survival>=CFG.activeActionMinConfidence&&!cal.watchOnly,""",
'active variant hazard')

# Stable decisions/audits must reset when the variant branch changes, and reports should expose it.
rep(
"let k=action+'|'+(h.slot??-1)+'|'+(h.family??'');",
"let k=action+'|'+(h.slot??-1)+'|'+(h.family??'')+'|'+(h.variant??'');",
'stable variant key')
rep(
"const k=(e.family||'?')+'|'+(e.source||'?');",
"const k=(e.family||'?')+'|'+(e.source||'?')+'|'+(e.variant||'base');",
'audit variant key')
rep(
"""    A.pending={player:name,action,family:h.family,source:h.source||null,slot:h.slot,enemyType:h.type,instance,auditKey,""",
"""    A.pending={player:name,action,family:h.family,source:h.source||null,variant:h.variant||null,slot:h.slot,enemyType:h.type,instance,auditKey,""",
'audit pending variant')
rep(
"""    action:AUD[n].pending.action,family:AUD[n].pending.family,hitMs:AUD[n].pending.hitMs,source:AUD[n].pending.source,
    slot:AUD[n].pending.slot,instance:AUD[n].pending.instance,familySeen:AUD[n].pending.familySeen}:null};""",
"""    action:AUD[n].pending.action,family:AUD[n].pending.family,hitMs:AUD[n].pending.hitMs,source:AUD[n].pending.source,variant:AUD[n].pending.variant,
    slot:AUD[n].pending.slot,instance:AUD[n].pending.instance,familySeen:AUD[n].pending.familySeen}:null};""",
'audit snapshot variant')

# Compact report includes variant demotions as first-class rows.
rep(
"const demoted=[...(c.source||[]),...(c.family||[])].filter(r=>r.watchOnly).slice(0,20);",
"const demoted=[...(c.variant||[]),...(c.source||[]),...(c.family||[])].filter(r=>r.watchOnly).slice(0,20);",
'summary variant demotions')

# API and version.
rep(
"""    calibration(){return frozenCopy(calibrationSnapshot());},
    snapshot(){return reportSnapshot();},""",
"""    calibration(){return frozenCopy(calibrationSnapshot());},
    exportCalibration(){return frozenCopy(calibrationRaw());},
    snapshot(){return reportSnapshot();},""",
'export calibration API')
rep("version:'offline-dynamic-spectator-calibrated-v4.7'","version:'offline-dynamic-spectator-calibrated-v4.8'",'version')
rep("qlog('✅ WOF V4.7 边缘壳深度校准观战版启动');","qlog('✅ WOF V4.8 上下文Variant校准观战版启动');",'startup')
rep(
"qlog('🟪 边缘壳: 行动核心再内缩 '+Math.round(CFG.actionPenetrationMin*100)+'%，避免擦边UP/DOWN/AB');",
"qlog('🧬 Variant: startup按anim/state分支；active按起手上下文+80ms运动分支独立降级，不再一刀切整个Family');\n  qlog('💾 热更新继承: Family/source/variant在线校准在同一Worker内升级版本时保留');\n  qlog('🟪 边缘壳: 行动核心再内缩 '+Math.round(CFG.actionPenetrationMin*100)+'%，避免擦边UP/DOWN/AB');",
'variant startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.8',len(s))
