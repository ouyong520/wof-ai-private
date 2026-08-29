(async()=>{
try{
function __WOF_START_V4(DB){
  let __WOF_PREV_CAL=null;
  try{__WOF_PREV_CAL=self.WOFV4?.exportCalibration?.()||self.WOFV4?.calibration?.()||self.__WOF_CAL_CACHE||null;}catch(e){}
  try{ self.WOFV4?.stop?.(); }catch(e){}
  try{ self.WOFV3?.stop?.(); }catch(e){}
  try{ self.WOF2D?.stop?.(); }catch(e){}
  try{ self.WOFSTABLE?.stop?.(); }catch(e){}
  try{ self.WOFPLAYERS?.stop?.(); }catch(e){}

  const CFG={
    horizonMs:1000,
    dangerStepMs:50,
    tickMs:40,
    playerHistoryMs:160,
    playerYSpeed:38,
    reactFloorMs:60,
    hazardThreshold:0.50,
    minConfidence:0.08,
    maxFamilies:4,
    cumulativeProbability:0.95,
    routeCommitMs:250,
    abRouteSlackMs:120,
    auditGraceMs:220,
    auditTolX:14,
    auditTolY:8,
    auditTolZ:14,
    auditHitEarlyMs:180,
    survivalActionThreshold:0.50,
    startupActionMinConfidence:0.15,
    activeActionMinConfidence:0.50,
    actionPenetrationMin:0.15,
    fpPenetrationMin:0.05,
    auditRevokeLeadMs:60,
    auditRepeatBlockMs:700,
    missHistoryMs:600,
    missCandidateLimit:5,
    fallbackZThreshold:80,
    fallbackZActionCore:16,
    fallbackXYActionScale:.68,
    fallbackYActionScale:.85,
    padX:3,
    padY:2,
    padZ:2
  };

  const PLAYERS=[
    {name:'P1',base:0xFFBE1C},
    {name:'P2',base:0xFFBEFC},
    {name:'P3',base:0xFFBFDC}
  ];
  const POOL=0xFFC0BC, STRIDE=0xE0, NSLOTS=20;

  let QUIET=false;
  const qlog=(...a)=>{if(!QUIET)self.console.log(...a);};
  const M=_0x515056.HEAPU8;
  const R=_0x515056.HEAPU32[0x2e39e4>>>2]>>>0;
  if(!R) throw new Error('CPS RAM pointer unavailable');

  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
  const U16=a=>((B(a)<<8)|B(a+1))>>>0;
  const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
  const S32=a=>{let v=U32(a);return v>=0x80000000?v-0x100000000:v;};
  const W=v=>v/65536;
  const faceSign=f=>f===255?-1:1;

  function readActor(base,slot){
    const flag=B(base); if(!flag) return null;
    return {
      slot,flag,
      type:U16(base+0x20),
      x:W(S32(base+0x04)),y:W(S32(base+0x08)),z:W(S32(base+0x0C)),
      face:B(base+0x16),
      s0:B(base+0x28),s1:B(base+0x29),s2:B(base+0x2A),s3:B(base+0x2B),
      frame:U32(base+0x12),anim:U32(base+0x2C),
      attack:U16(base+0x70)
    };
  }

  function readPlayer(base,name){
    const flag=B(base); if(!flag) return null;
    return {name,flag,x:W(S32(base+4)),y:W(S32(base+8)),z:W(S32(base+12)),hp:B(base+0x83)};
  }

  const keyState=o=>o.type+'|'+o.anim+'|'+o.s0+'|'+o.s1+'|'+o.s2+'|'+o.s3;
  const keyExact=o=>keyState(o)+'|'+o.frame;
  const keyActive=o=>o.type+'|'+o.attack+'|'+o.s0+'|'+o.s1+'|'+o.s2+'|'+o.s3;

  const PH={P1:[],P2:[],P3:[]};
  const PS={};
  const TRACK={P1:true,P2:true,P3:true};
  let PLAYER_MODE='spectator',LOCAL_NAME=null,LOCAL_SEAT=null,LOCAL_MODE='none';

  function localPlayerNo(){
    try{const n=Number(_0x2f9e12);return n>=1&&n<=3?n:null;}catch(e){return null;}
  }
  function resetPlayerRuntime(name){
    PH[name]=[];delete PS[name];
    const A=AUD?.[name];if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;A.lastRawWarnAt=-1e9;A.recent={};}
    const S=ST?.[name];if(S){S.k='';S.n=0;S.v=null;}
    if(name in PRINT)PRINT[name]='';
  }
  function livePlayerNames(){
    const out=[];
    for(const p of PLAYERS)if(readPlayer(p.base,p.name))out.push(p.name);
    return out;
  }
  function resolveLocalActor(){
    const seat=localPlayerNo(),seatName=seat?'P'+seat:null,live=livePlayerNames();
    if(seatName&&live.includes(seatName))return{name:seatName,seat,mode:'seat',live};
    if(live.length===1)return{name:live[0],seat,mode:'sole-live-fallback',live};
    return{name:null,seat,mode:seatName?'seat-object-missing':'seat-unknown',live};
  }
  function syncLocalPlayer(force=false){
    if(PLAYER_MODE!=='local')return LOCAL_NAME;
    const r=resolveLocalActor(),name=r.name;
    if(!force&&name===LOCAL_NAME&&r.seat===LOCAL_SEAT&&r.mode===LOCAL_MODE)return LOCAL_NAME;
    const prev=LOCAL_NAME,prevMode=LOCAL_MODE;
    LOCAL_NAME=name;LOCAL_SEAT=r.seat;LOCAL_MODE=r.mode;
    for(const p of PLAYERS){
      const on=p.name===name;
      if(TRACK[p.name]!==on){TRACK[p.name]=on;resetPlayerRuntime(p.name);}
    }
    if(name&&(name!==prev||r.mode!==prevMode))qlog('🎮 本机玩家映射:',name,'seat',r.seat??'?','mode',r.mode,'live',r.live.join(','));
    if(!name&&(prev||force))qlog('⚪ 暂未映射本机角色','seat',r.seat??'?','live',r.live.join(',')||'none','— 暂停玩家预测/审计');
    return LOCAL_NAME;
  }

  function updatePlayers(now){
    for(const p of PLAYERS){
      if(!TRACK[p.name]){PH[p.name]=[];delete PS[p.name];continue;}
      const cur=readPlayer(p.base,p.name);
      if(!cur){PH[p.name]=[];delete PS[p.name];continue;}
      const h=PH[p.name]; h.push({t:now,x:cur.x,y:cur.y,z:cur.z});
      while(h.length&&now-h[0].t>CFG.playerHistoryMs) h.shift();
      let vx=0,vy=0,vz=0;
      if(h.length>=3){
        const a=h[0],b=h[h.length-1],dt=(b.t-a.t)/1000;
        if(dt>0){vx=(b.x-a.x)/dt;vy=(b.y-a.y)/dt;vz=(b.z-a.z)/dt;}
      }
      if(Math.abs(vx)>400)vx=0;
      if(Math.abs(vy)>200)vy=0;
      if(Math.abs(vz)>400)vz=0;
      PS[p.name]={name:p.name,x:cur.x,y:cur.y,z:cur.z,vx,vy,vz,hp:cur.hp};
    }
  }

  // Compact family row: [type,attack,dur90,rx,ry,rz,tr,sw]
  // tr[t]=[x,y,z], sw[t]=[survival,x,y,z]
  function unpack(a,kind){
    if(!a)return null;
    return kind==='tr'
      ?{x:+a[0]||0,y:+a[1]||0,z:+a[2]||0,survival:1}
      :{survival:a[0]==null?1:+a[0],x:+a[1]||0,y:+a[2]||0,z:+a[3]||0};
  }

  function interp(series,x,kind){
    if(!series)return null;
    const ks=Object.keys(series).map(Number).sort((a,b)=>a-b);
    if(!ks.length)return null;
    if(x<=ks[0])return unpack(series[String(ks[0])],kind);
    if(x>=ks[ks.length-1])return unpack(series[String(ks[ks.length-1])],kind);
    let lo=ks[0],hi=ks[ks.length-1];
    for(let i=1;i<ks.length;i++){if(x<=ks[i]){lo=ks[i-1];hi=ks[i];break;}}
    const a=unpack(series[String(lo)],kind),b=unpack(series[String(hi)],kind);
    if(!a||!b)return a||b;
    const k=(x-lo)/(hi-lo||1);
    return {x:a.x+(b.x-a.x)*k,y:a.y+(b.y-a.y)*k,z:a.z+(b.z-a.z)*k,
      survival:(a.survival??1)+((b.survival??1)-(a.survival??1))*k};
  }

  const getFamily=id=>DB.f[id]||null;
  const FALLBACK_GEOMETRY=new Set(Object.values(DB.fd||{}).map(a=>(+a[0]||0)+'|'+(+a[1]||0)+'|'+(+a[2]||0)));
  function radius(f){
    const rawRx=(+f[3]||115),rawRy=(+f[4]||22),rawRz=(+f[5]||8);
    const geometryFallback=FALLBACK_GEOMETRY.has(rawRx+'|'+rawRy+'|'+rawRz);
    const geometryFallbackZ=rawRz>=CFG.fallbackZThreshold;
    const actionRawRx=geometryFallback?rawRx*CFG.fallbackXYActionScale:rawRx;
    const actionRawRy=geometryFallback?rawRy*CFG.fallbackYActionScale:rawRy;
    const actionRawRz=geometryFallbackZ?CFG.fallbackZActionCore:rawRz;
    const geoClass=geometryFallback?('fallback:'+rawRx+':'+rawRy+':'+rawRz):null;
    return {rx:rawRx+CFG.padX,ry:rawRy+CFG.padY,rz:rawRz+CFG.padZ,
      actionRx:actionRawRx+CFG.padX,actionRy:actionRawRy+CFG.padY,actionRz:actionRawRz+CFG.padZ,
      rawRx,rawRy,rawRz,geometryFallback,geometryFallbackZ,geoClass};
  }

  // Cross-player online reliability. P1/P2/P3 all contribute to the same Family evidence.
  // Only confirmed hit/fp events enter this table. Demotion affects actionability only.
  const CAL_FAMILY=Object.create(null),CAL_SOURCE=Object.create(null),CAL_VARIANT=Object.create(null),CAL_GEOM=Object.create(null);
  const CAL_CFG={
    sourceDemoteConfirmed:6,sourceDemoteFp:5,sourceDemoteFpPlayers:2,sourceDemotePrecision:.25,
    sourceRecoverConfirmed:10,sourceRecoverHit:4,sourceRecoverPrecision:.50,
    familyDemoteConfirmed:10,familyDemoteFp:7,familyDemoteFpPlayers:2,familyDemotePrecision:.30,
    familyRecoverConfirmed:16,familyRecoverHit:6,familyRecoverPrecision:.50,
    variantDemoteConfirmed:2,variantDemoteFp:2,variantDemotePrecision:.20,
    variantRecoverConfirmed:5,variantRecoverHit:2,variantRecoverPrecision:.50,
    precisionVariantFp:1,precisionSourceConfirmed:3,precisionSourceMax:.20,
    precisionFamilyConfirmed:5,precisionFamilyMax:.20,
    trustUnseenActive:.78,trustUnseenStartup:.84,trustBadEvidence:.72,trustFamilyHit:.88,trustSourceHit:.93,
    activeFpMinConfidence:.50,startupFpMinConfidence:.25,fpMinSurvival:.50
  };
  function calBucket(map,key){return map[key]||(map[key]={hit:0,fp:0,ignoredFp:0,confirmed:0,precision:null,watchOnly:false,demotions:0,recoveries:0,hitPlayers:{},fpPlayers:{},fpFamilies:{},gx:1,gy:1,gz:1,geoFp:0,geoHit:0});}
  function calRefresh(b,scope){
    b.confirmed=b.hit+b.fp;b.precision=b.confirmed?b.hit/b.confirmed:null;
    const was=b.watchOnly;
    if(!was){
      const fpPlayers=Object.keys(b.fpPlayers||{}).length;
      if(scope==='variant')b.watchOnly=b.confirmed>=CAL_CFG.variantDemoteConfirmed&&b.fp>=CAL_CFG.variantDemoteFp&&b.precision<=CAL_CFG.variantDemotePrecision;
      else if(scope==='source')b.watchOnly=b.confirmed>=CAL_CFG.sourceDemoteConfirmed&&b.fp>=CAL_CFG.sourceDemoteFp&&fpPlayers>=CAL_CFG.sourceDemoteFpPlayers&&b.precision<=CAL_CFG.sourceDemotePrecision;
      else b.watchOnly=b.confirmed>=CAL_CFG.familyDemoteConfirmed&&b.fp>=CAL_CFG.familyDemoteFp&&fpPlayers>=CAL_CFG.familyDemoteFpPlayers&&b.precision<=CAL_CFG.familyDemotePrecision;
      if(b.watchOnly)b.demotions++;
    }else{
      if(scope==='variant')b.watchOnly=!(b.confirmed>=CAL_CFG.variantRecoverConfirmed&&b.hit>=CAL_CFG.variantRecoverHit&&b.precision>=CAL_CFG.variantRecoverPrecision);
      else if(scope==='source')b.watchOnly=!(b.confirmed>=CAL_CFG.sourceRecoverConfirmed&&b.hit>=CAL_CFG.sourceRecoverHit&&b.precision>=CAL_CFG.sourceRecoverPrecision);
      else b.watchOnly=!(b.confirmed>=CAL_CFG.familyRecoverConfirmed&&b.hit>=CAL_CFG.familyRecoverHit&&b.precision>=CAL_CFG.familyRecoverPrecision);
      if(!b.watchOnly)b.recoveries++;
    }
    return was!==b.watchOnly;
  }
  function calPolicy(family,source,variant=null){
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
  }
  function geoClassPolicy(key){
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
    if(b.geoFp<4||Object.keys(b.fpFamilies||{}).length<3)return;
    const vals=[['x',+e.rx||1,+e.mx||0],['y',+e.ry||1,+e.my||0],['z',+e.rz||1,+e.mz||0]]
      .map(([axis,r,m])=>({axis,r,m,pen:r>0?m/r:1})).sort((a,b)=>a.pen-b.pen);
    const edge=vals[0];if(!edge||edge.pen<0)return;
    const prop='g'+edge.axis,cur=b[prop]??1;
    const shrink=Math.max(.80,Math.min(.94,1-edge.pen-.02));
    const target=Math.max(.58,cur*shrink);
    if(target<cur)b[prop]=target;
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
  }
  function calFpEligible(e){
    if((+e.survival||0)<CAL_CFG.fpMinSurvival)return false;
    const c=+e.confidence||0;
    const confOK=e.source==='active'?c>=CAL_CFG.activeFpMinConfidence:c>=CAL_CFG.startupFpMinConfidence;
    if(!confOK)return false;
    const px=(+e.rx||0)>0?(+e.mx||0)/(+e.rx||1):-1;
    const py=(+e.ry||0)>0?(+e.my||0)/(+e.ry||1):-1;
    const pz=(+e.rz||0)>0?(+e.mz||0)/(+e.rz||1):-1;
    return Math.min(px,py,pz)>=CFG.fpPenetrationMin;
  }
  function calRecord(e,kind){
    if(!e?.family||(kind!=='hit'&&kind!=='fp'))return;
    const family=e.family,source=e.source||'?',variant=e.variant||null,fb=calBucket(CAL_FAMILY,family),sb=calBucket(CAL_SOURCE,family+'|'+source),vb=variant?calBucket(CAL_VARIANT,family+'|'+source+'|'+variant):null;
    if(kind==='fp'&&!calFpEligible(e)){fb.ignoredFp++;sb.ignoredFp++;if(vb)vb.ignoredFp++;return;}
    const before=calPolicy(family,source,variant).watchOnly;
    const who=e.player||'?';
    for(const b of [fb,sb,...(vb?[vb]:[])]){
      if(kind==='hit'){b.hit++;b.hitPlayers[who]=1;}
      else{b.fp++;b.fpPlayers[who]=1;}
    }
    geoAdapt(e,kind,sb,vb);geoClassAdapt(e,kind);
    const vf=vb?calRefresh(vb,'variant'):false,sf=calRefresh(sb,'source'),ff=calRefresh(fb,'family'),after=calPolicy(family,source,variant).watchOnly;
    if(!before&&after){
      qlog(vb?.watchOnly?'🧬 Variant降级WATCH':'🧯 Family降级WATCH',family,source,variant||'',
        'variant',vb?(vb.hit+'/'+vb.confirmed):'-','source',sb.hit+'/'+sb.confirmed,'family',fb.hit+'/'+fb.confirmed);
    }else if(before&&!after){
      qlog('♻️ Family恢复行动',family,source,'source',sb.hit+'/'+sb.confirmed,'p',sb.precision?.toFixed(2),'family',fb.hit+'/'+fb.confirmed,'p',fb.precision?.toFixed(2));
    }else if((vf||sf||ff)&&after){
      // A second scope can cross its threshold while the branch is already demoted; no extra spam.
    }
    self.__WOF_CAL_CACHE={family:JSON.parse(JSON.stringify(CAL_FAMILY)),source:JSON.parse(JSON.stringify(CAL_SOURCE)),variant:JSON.parse(JSON.stringify(CAL_VARIANT)),geom:JSON.parse(JSON.stringify(CAL_GEOM))};
  }
  function calRows(map,scope){
    return Object.entries(map).map(([key,v])=>({scope,key,hit:v.hit,fp:v.fp,ignoredFp:v.ignoredFp,confirmed:v.confirmed,
      hitPlayers:Object.keys(v.hitPlayers||{}).length,fpPlayers:Object.keys(v.fpPlayers||{}).length,
      precision:v.precision,watchOnly:v.watchOnly,demotions:v.demotions,recoveries:v.recoveries,
      fpFamilies:Object.keys(v.fpFamilies||{}).length,
      geo:[+(v.gx??1).toFixed(3),+(v.gy??1).toFixed(3),+(v.gz??1).toFixed(3)],geoFp:v.geoFp||0,geoHit:v.geoHit||0}))
      .sort((a,b)=>(Number(b.watchOnly)-Number(a.watchOnly))||(b.fp-a.fp)||(b.confirmed-a.confirmed));
  }
  function calibrationSnapshot(){return {config:{...CAL_CFG},family:calRows(CAL_FAMILY,'family'),source:calRows(CAL_SOURCE,'source'),variant:calRows(CAL_VARIANT,'variant'),geom:calRows(CAL_GEOM,'geom')};}
  function importCalRows(dst,src){
    if(!src)return;
    if(Array.isArray(src))for(const r of src){if(!r?.key)continue;const b=calBucket(dst,r.key);for(const k of ['hit','fp','ignoredFp','confirmed','precision','watchOnly','demotions','recoveries','gx','gy','gz','geoFp','geoHit'])if(r[k]!=null)b[k]=r[k];if(Array.isArray(r.geo)){b.gx=+r.geo[0]||1;b.gy=+r.geo[1]||1;b.gz=+r.geo[2]||1;}for(let i=0;i<(+r.hitPlayers||0);i++)b.hitPlayers['legacy'+i]=1;for(let i=0;i<(+r.fpPlayers||0);i++)b.fpPlayers['legacy'+i]=1;for(let i=0;i<(+r.fpFamilies||0);i++)b.fpFamilies['legacyFamily'+i]=1;}
    else for(const [k,r] of Object.entries(src)){const b=calBucket(dst,k);Object.assign(b,JSON.parse(JSON.stringify(r)));b.hitPlayers=b.hitPlayers||{};b.fpPlayers=b.fpPlayers||{};b.fpFamilies=b.fpFamilies||{};}
  }
  function importCalibration(x){if(!x)return false;importCalRows(CAL_FAMILY,x.family);importCalRows(CAL_SOURCE,x.source);importCalRows(CAL_VARIANT,x.variant);importCalRows(CAL_GEOM,x.geom);return true;}
  importCalibration(__WOF_PREV_CAL||self.__WOF_CAL_CACHE);
  function recalibrateImported(){
    for(const [map,scope] of [[CAL_VARIANT,'variant'],[CAL_SOURCE,'source'],[CAL_FAMILY,'family']]){
      for(const b of Object.values(map)){b.watchOnly=false;calRefresh(b,scope);}
    }
  }
  recalibrateImported();
  function calibrationRaw(){return {family:JSON.parse(JSON.stringify(CAL_FAMILY)),source:JSON.parse(JSON.stringify(CAL_SOURCE)),variant:JSON.parse(JSON.stringify(CAL_VARIANT)),geom:JSON.parse(JSON.stringify(CAL_GEOM))};}
  function calibrationReset(){for(const k of Object.keys(CAL_FAMILY))delete CAL_FAMILY[k];for(const k of Object.keys(CAL_SOURCE))delete CAL_SOURCE[k];for(const k of Object.keys(CAL_VARIANT))delete CAL_VARIANT[k];for(const k of Object.keys(CAL_GEOM))delete CAL_GEOM[k];self.__WOF_CAL_CACHE=null;qlog('🧹 Family/Variant/Geometry在线校准已清零');return calibrationSnapshot();}

  function lookup(o){
    let r=DB.e[keyExact(o)]; if(r)return {kind:'exact',row:r};
    r=DB.c[keyState(o)]; return r?{kind:'coarse',row:r}:null;
  }

  function chooseFamilies(row){
    const src=row[4]||[],out=[];let cum=0;
    for(let i=0;i<src.length&&out.length<CFG.maxFamilies;i++){
      const p=+src[i][1]||0;
      if(p<0.01&&out.length)continue;
      out.push({id:src[i][0],p});cum+=p;
      if(cum>=CFG.cumulativeProbability)break;
    }
    return out;
  }

  function leads(row){
    const raw=[{v:+row[1]||0,w:.25,q:'early'},{v:+row[2]||0,w:.5,q:'median'},{v:+row[3]||0,w:.25,q:'late'}];
    const seen=new Set(),out=[];
    for(const x of raw){const v=Math.max(0,Math.min(CFG.horizonMs,x.v));if(seen.has(v))continue;seen.add(v);out.push({...x,v});}
    return out;
  }

  const SLOT=Array.from({length:NSLOTS},()=>({type:null,prevAttack:0,locked:null,started:0,origin:null,face:0,seq:0,variantBase:null,variantMotion:null}));
  const UNIQUE_ACTIVE=new Map();
  const MULTI_ACTIVE=new Set();
  const ENEMY_HISTORY=[];
  const MISS_CASES=[];
  for(const [id,f] of Object.entries(DB.f)){
    const k=f[0]+'|'+f[1];
    if(UNIQUE_ACTIVE.has(k)){UNIQUE_ACTIVE.delete(k);MULTI_ACTIVE.add(k);}
    else if(!MULTI_ACTIVE.has(k))UNIQUE_ACTIVE.set(k,id);
  }

  function updateLock(o,now){
    const s=SLOT[o.slot];
    if(s.type!==o.type){s.type=o.type;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;s.seq=0;s.variantBase=null;s.variantMotion=null;}
    if(s.prevAttack===0&&o.attack!==0){
      s.seq=(s.seq||0)+1;
      s.locked=DB.a[keyActive(o)]||UNIQUE_ACTIVE.get(o.type+'|'+o.attack)||null;
      s.started=now;s.origin={x:o.x,y:o.y,z:o.z};s.face=o.face;
      s.variantBase='a'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3;s.variantMotion=null;
    }else if(s.prevAttack!==0&&o.attack===0){s.locked=null;s.origin=null;s.started=0;s.variantBase=null;s.variantMotion=null;}
    if(o.attack!==0&&s.origin&&s.variantMotion==null&&now-s.started>=80){
      const sg=faceSign(s.face),dx=sg*(o.x-s.origin.x),dy=o.y-s.origin.y,dz=o.z-s.origin.z;
      s.variantMotion='m'+Math.round(dx/16)+','+Math.round(dy/8)+','+Math.round(dz/8);
    }
    s.prevAttack=o.attack;
    return s;
  }

  function captureEnemyFrame(now){
    const actors=[];
    for(let i=0;i<NSLOTS;i++){
      const o=readActor(POOL+i*STRIDE,i);if(!o)continue;
      const sl=SLOT[i]||{};
      actors.push({slot:i,type:o.type,x:+o.x.toFixed(1),y:+o.y.toFixed(1),z:+o.z.toFixed(1),face:o.face,
        attack:o.attack,anim:o.anim,s0:o.s0,s1:o.s1,s2:o.s2,s3:o.s3,frame:o.frame,locked:sl.locked||null});
    }
    ENEMY_HISTORY.push({t:now,actors});
    while(ENEMY_HISTORY.length&&now-ENEMY_HISTORY[0].t>CFG.missHistoryMs)ENEMY_HISTORY.shift();
  }

  function missEnemyCandidates(ps,now){
    const best=new Map();
    for(const fr of ENEMY_HISTORY){
      const age=Math.max(0,now-fr.t);
      for(const o of fr.actors){
        const dx=Math.abs(ps.x-o.x),dy=Math.abs(ps.y-o.y),dz=Math.abs(ps.z-o.z);
        const active=o.attack!==0;
        const score=dx+dy*4+dz*2+age*.04-(active?70:0)-(o.locked?20:0);
        const prev=best.get(o.slot);
        if(!prev||score<prev.score){
          let startupTop=[];
          if(!active){
            const h=lookup(o);
            if(h)startupTop=chooseFamilies(h.row).slice(0,2).map(x=>x.id);
          }
          best.set(o.slot,{score:+score.toFixed(1),ageMs:Math.round(age),slot:o.slot,type:o.type,attack:o.attack,
            locked:o.locked||null,anim:o.anim,state:[o.s0,o.s1,o.s2,o.s3],frame:o.frame,
            dx:+dx.toFixed(1),dy:+dy.toFixed(1),dz:+dz.toFixed(1),startupTop});
        }
      }
    }
    return [...best.values()].sort((a,b)=>a.score-b.score).slice(0,CFG.missCandidateLimit);
  }

  function captureMissCase(kind,name,ps,raw,now,hp0,hp1){
    const n=raw?.stay?.nearest||null;
    const c={id:MISS_CASES.length+1,kind,player:name,hp:hp0+'→'+hp1,
      at:+now.toFixed(1),pos:[+ps.x.toFixed(1),+ps.y.toFixed(1),+ps.z.toFixed(1)],
      nearest:n?{family:n.family||null,source:n.source||null,variant:n.variant||null,slot:n.slot??null,type:n.type??null,
        t:n.t,confidence:+(+n.confidence||0).toFixed(3),survival:+(+n.survival||0).toFixed(3),
        clearance:raw?.stay?.minClearance==null?null:+raw.stay.minClearance.toFixed(3)}:null,
      candidates:missEnemyCandidates(ps,now)};
    MISS_CASES.push(c);if(MISS_CASES.length>16)MISS_CASES.shift();
    return c;
  }

  function activeOrigin(o,f,lead){
    const tr=interp(f[6],-Math.max(0,Math.min(1000,lead)),'tr');
    if(!tr)return{x:o.x,y:o.y,z:o.z};
    const sg=faceSign(o.face);
    return{x:o.x-sg*tr.x,y:o.y-tr.y,z:o.z-tr.z};
  }

  function addStartup(o,hit,out){
    const row=hit.row,hazard=+row[0]||0;
    if(hazard<CFG.hazardThreshold)return;
    const fs=chooseFamilies(row),ls=leads(row);
    out.enemies.add(o.slot);
    for(const fc of fs){
      const f=getFamily(fc.id);if(!f)continue;
      const rad=radius(f),sg=faceSign(o.face),dur90=+f[2]||1000;
      for(const l of ls){
        const org=activeOrigin(o,f,l.v);
        for(let t=0;t<=CFG.horizonMs;t+=CFG.dangerStepMs){
          if(t<l.v)continue;
          const age=t-l.v;if(age>dur90)continue;
          const sw=interp(f[7],age,'sw');if(!sw)continue;
          const survival=Math.max(0,Math.min(1,sw.survival??1));
          const confidence=hazard*fc.p*l.w*survival;
          if(confidence<CFG.minConfidence)continue;
          const variant='s'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3+':'+hit.kind;
          const cal=calPolicy(fc.id,'startup',variant),gc=geoClassPolicy(rad.geoClass);
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,
            rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRx:rad.actionRx*gc.x,actionRy:rad.actionRy*gc.y,actionRz:rad.actionRz*gc.z,
            geometryFallback:rad.geometryFallback,geometryFallbackZ:rad.geometryFallbackZ,geoClass:rad.geoClass,
            slot:o.slot,type:o.type,family:fc.id,variant,
            confidence,survival,actionable:survival>=CFG.survivalActionThreshold&&confidence>=CFG.startupActionMinConfidence&&!cal.watchOnly,
            calWatchOnly:cal.watchOnly,precisionWatch:cal.precisionWatch,trustScale:cal.trustScale,trustReason:cal.trustReason,
            calPrecision:cal.sourcePrecision??cal.familyPrecision,
            calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),geoScale:{x:cal.geoX,y:cal.geoY,z:cal.geoZ},
            instance:'S:'+o.slot+':'+o.type+':'+o.anim+':'+o.s0+':'+o.s1+':'+o.s2+':'+o.s3+':'+fc.id,
            source:'startup',lookup:hit.kind});
        }
      }
    }
  }

  function addActive(o,s,now,out){
    if(!s.locked){
      const fd=(DB.fd&&DB.fd.melee_or_short_move)||[115,18,8];
      out.enemies.add(o.slot);
      for(let t=CFG.reactFloorMs;t<=300;t+=CFG.dangerStepMs){
        out.danger.push({t,x:o.x,y:o.y,z:o.z,rx:fd[0]+CFG.padX,ry:fd[1]+CFG.padY,rz:fd[2]+CFG.padZ,
          slot:o.slot,type:o.type,family:null,confidence:.20,source:'active-unknown'});
      }
      return;
    }
    const f=getFamily(s.locked);if(!f)return;
    const rad=radius(f),age=Math.max(0,now-s.started),sg=faceSign(s.face),dur90=+f[2]||1000;
    out.enemies.add(o.slot);
    for(let t=0;t<=CFG.horizonMs;t+=CFG.dangerStepMs){
      const a=age+t;if(a>dur90)continue;
      const sw=interp(f[7],a,'sw');if(!sw)continue;
      const survival=Math.max(0,Math.min(1,sw.survival??1));
      if(survival<CFG.minConfidence)continue;
      const variant=(s.variantBase||'a?')+'|'+(s.variantMotion||'early');
      const cal=calPolicy(s.locked,'active',variant),gc=geoClassPolicy(rad.geoClass);
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,
        rx:rad.rx,ry:rad.ry,rz:rad.rz,actionRx:rad.actionRx*gc.x,actionRy:rad.actionRy*gc.y,actionRz:rad.actionRz*gc.z,
        geometryFallback:rad.geometryFallback,geometryFallbackZ:rad.geometryFallbackZ,geoClass:rad.geoClass,
        slot:o.slot,type:o.type,family:s.locked,variant,
        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold&&survival>=CFG.activeActionMinConfidence&&!cal.watchOnly,
        calWatchOnly:cal.watchOnly,precisionWatch:cal.precisionWatch,trustScale:cal.trustScale,trustReason:cal.trustReason,
        calPrecision:cal.sourcePrecision??cal.familyPrecision,
        calConfirmed:Math.max(cal.sourceConfirmed,cal.familyConfirmed),geoScale:{x:cal.geoX,y:cal.geoY,z:cal.geoZ},
        instance:'A:'+o.slot+':'+o.type+':'+s.seq+':'+Math.round(s.started),source:'active'});
    }
  }

  function buildDanger(now){
    const out={danger:[],enemies:new Set(),exact:0,coarse:0};
    for(let i=0;i<NSLOTS;i++){
      const o=readActor(POOL+i*STRIDE,i),s=SLOT[i];
      if(!o){s.type=null;s.prevAttack=0;s.locked=null;s.origin=null;s.started=0;continue;}
      updateLock(o,now);
      if(o.attack!==0)addActive(o,s,now,out);
      else{const h=lookup(o);if(h){out[h.kind]++;addStartup(o,h,out);}}
    }
    return out;
  }

  function playerAt(p,mode,t,delay=0){
    const before=Math.min(t,delay)/1000,after=Math.max(0,t-delay)/1000;
    const x=p.x+p.vx*(t/1000);
    const z=p.z+p.vz*(t/1000);
    if(mode==='CONTINUE')return{x,y:p.y+p.vy*(t/1000),z};
    const y0=p.y+p.vy*before;
    const dir=mode==='UP'?-1:1;
    return{x,y:y0+dir*CFG.playerYSpeed*after,z};
  }

  function collides(p,d){return Math.abs(p.x-d.x)<=d.rx&&Math.abs(p.y-d.y)<=d.ry&&Math.abs(p.z-d.z)<=d.rz;}
  function clearNorm(p,d){const dx=(p.x-d.x)/Math.max(1,d.rx),dy=(p.y-d.y)/Math.max(1,d.ry),dz=(p.z-d.z)/Math.max(1,d.rz);return Math.sqrt(dx*dx+dy*dy+dz*dz);}

  function evalPath(p,mode,danger,delay=0){
    let earliest=null,hit=null,min=Infinity,nearest=null;
    for(const d of danger){
      if(d.t<CFG.reactFloorMs||d.confidence<CFG.minConfidence)continue;
      const pp=playerAt(p,mode,d.t,delay),c=clearNorm(pp,d);
      if(c<min){min=c;nearest=d;}
      if(collides(pp,d)&&(earliest===null||d.t<earliest)){earliest=d.t;hit=d;}
    }
    return{mode,safe:earliest===null,collisionMs:earliest,minClearance:isFinite(min)?min:null,hit,nearest};
  }

  function latestSafe(p,mode,danger,collisionMs){
    let latest=-1;
    const max=Math.max(0,Math.min(CFG.horizonMs,collisionMs??CFG.horizonMs));
    for(let delay=0;delay<=max;delay+=20)if(evalPath(p,mode,danger,delay).safe)latest=delay;
    return latest;
  }

  function decision(p,danger){
  const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false)
    .map(d=>d.geometryFallback?{...d,rx:d.actionRx,ry:d.actionRy,rz:d.actionRz,geometryCore:true}:d)
    .map(d=>{const g=d.geoScale||{x:1,y:1,z:1};
      const trust=d.t<=250?Math.max(.90,d.trustScale??1):(d.trustScale??1);
      return {...d,effectiveTrust:trust,
      rx:Math.max(1,d.rx*(g.x??1)*trust*(1-CFG.actionPenetrationMin)),
      ry:Math.max(1,d.ry*(g.y??1)*trust*(1-CFG.actionPenetrationMin)),
      rz:Math.max(1,d.rz*(g.z??1)*trust*(1-CFG.actionPenetrationMin)),
      learnedGeometry:true,actionPenetrationCore:true};});
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
  }

  const routeUntil=Math.min(CFG.horizonMs,cur.collisionMs+CFG.routeCommitMs);
  const routeDanger=actionDanger.filter(d=>d.t<=routeUntil);
  const up0=evalPath(p,'UP',routeDanger,0),down0=evalPath(p,'DOWN',routeDanger,0);
  const up=up0.safe?latestSafe(p,'UP',routeDanger,cur.collisionMs):-1;
  const down=down0.safe?latestSafe(p,'DOWN',routeDanger,cur.collisionMs):-1;

  if(up<0&&down<0){
    const known=h=>!!h&&h.family!=null&&h.source!=='active-unknown'&&h.actionable!==false;
    const blockersKnown=known(cur.hit)&&known(up0.hit)&&known(down0.hit);
    const upNear=up0.collisionMs!=null&&up0.collisionMs<=cur.collisionMs+CFG.abRouteSlackMs;
    const downNear=down0.collisionMs!=null&&down0.collisionMs<=cur.collisionMs+CFG.abRouteSlackMs;
    const abReady=blockersKnown&&cur.collisionMs<=250&&upNear&&downNear;
    return{danger:true,noRoute:true,abReady,best:abReady?'AB':'WATCH',hitMs:cur.collisionMs,hit:cur.hit,
      upHit:up0.hit,downHit:down0.hit,upHitMs:up0.collisionMs,downHitMs:down0.collisionMs,
      routeUntil,up,down,stay:cur};
  }

  let best,latest;
  if(up>=0&&down<0){best='UP';latest=up;}
  else if(down>=0&&up<0){best='DOWN';latest=down;}
  else{
    const ue=evalPath(p,'UP',routeDanger,Math.max(0,up-80));
    const de=evalPath(p,'DOWN',routeDanger,Math.max(0,down-80));
    if((ue.minClearance??0)>(de.minClearance??0)){best='UP';latest=up;}else{best='DOWN';latest=down;}
  }
  return{danger:true,noRoute:false,best,latestMs:latest,hitMs:cur.collisionMs,hit:cur.hit,
    routeUntil,up,down,stay:cur};
}

  const ST={P1:{k:'',n:0,v:null},P2:{k:'',n:0,v:null},P3:{k:'',n:0,v:null}},PRINT={P1:'',P2:'',P3:''};
function actionOf(r){return !r?.danger?'SAFE':r.watchOnly?'WATCH':r.noRoute?(r.abReady?'AB':'WATCH'):r.best;}
function stable(name,r){
  const s=ST[name],h=r.hit||{},uh=r.upHit||{},dh=r.downHit||{};
  const action=actionOf(r);
  let k=action+'|'+(h.slot??-1)+'|'+(h.family??'');
  if(action==='AB')k+='|'+(uh.slot??-1)+'|'+(uh.family??'')+'|'+(dh.slot??-1)+'|'+(dh.family??'');
  if(k===s.k)s.n++;else{s.k=k;s.n=1;s.v=null;}
  const need=action==='SAFE'?2:action==='WATCH'?2:action==='AB'?3:((+r.hitMs||9999)<=300?2:3);
  if(s.n>=need)s.v=r;
  return s.v;
}

  function print(name,r,enemyCount){
  if(!r)return;
  const h=r.hit||{},uh=r.upHit||{},dh=r.downHit||{};
  const action=actionOf(r);
  const sig=name+'|'+action+'|'+(h.slot??-1)+'|'+(h.family??'')+'|'+(uh.family??'')+'|'+(dh.family??'');
  if(sig===PRINT[name])return;PRINT[name]=sig;
  if(!r.danger)qlog('🟢',name,'OFFLINE SAFE','预测怪',enemyCount);
  else if(action==='WATCH'&&r.noRoute)qlog('🟠',name,'WATCH无路','当前'+r.hitMs+'ms',h.family||'?',
    'UP堵'+r.upHitMs+'ms',uh.family||'?','DOWN堵'+r.downHitMs+'ms',dh.family||'?','窗口'+r.routeUntil+'ms');
  else if(action==='WATCH'&&r.geometryWatchOnly)qlog('🟣',name,'WATCH-壳','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'full',fmt(h.rx)+'/'+fmt(h.ry)+'/'+fmt(h.rz),'core',fmt(h.actionRx)+'/'+fmt(h.actionRy)+'/'+fmt(h.actionRz),'source',h.source||'?');
  else if(action==='WATCH'&&r.edgeWatchOnly)qlog('🟪',name,'WATCH-边缘','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'edge',Math.round(CFG.actionPenetrationMin*100)+'%','source',h.source||'?');
  else if(action==='WATCH')qlog('🟠',name,'WATCH','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?','source',h.source||'?');
  else if(action==='AB')qlog('🆘',name,'OFFLINE AB候选','当前'+r.hitMs+'ms',h.family,
    'src',h.source||'?','UP堵'+r.upHitMs+'ms',uh.family||'?','DOWN堵'+r.downHitMs+'ms',dh.family||'?');
  else qlog(r.best==='UP'?'🟦 '+name+' ⬆ UP':'🟦 '+name+' ⬇ DOWN','约'+r.hitMs+'ms后危险','最晚'+r.latestMs+'ms后开始','UP',r.up,'DOWN',r.down,'窗口'+r.routeUntil+'ms','family',h.family||'?','src',h.source||'?');
}

const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0},byFamily:{}}
};

function famStat(A,e){
  const k=(e.family||'?')+'|'+(e.source||'?')+'|'+(e.variant||'base');
  return A.byFamily[k]||(A.byFamily[k]={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,materialized:0});
}
function fmt(n){return Number.isFinite(n)?n.toFixed(1):'?';}
function geoText(e){return 'inside x'+fmt(e.mx)+' y'+fmt(e.my)+' z'+fmt(e.mz)+' r '+fmt(e.rx)+'/'+fmt(e.ry)+'/'+fmt(e.rz)+' conf '+fmt(e.confidence)+' surv '+fmt(e.survival);}

function trackEnemy(e,now){
  if(!e||e.slot==null||e.slot<0||e.slot>=NSLOTS)return;
  const o=readActor(POOL+e.slot*STRIDE,e.slot);
  if(!o||o.type!==e.enemyType){
    if(now<=e.due+60)e.enemyLost=true;
    return;
  }
  e.enemyLastAttack=o.attack;
  const lk=SLOT[e.slot]?.locked||null;
  if(lk===e.family){
    e.familySeen=true;e.familyLastSeenAt=now;
  }else{
    if(lk&&lk!==e.family)e.otherFamily=lk;
    if(e.familySeen&&now<e.due-CFG.auditRevokeLeadMs)e.attackEndedEarly=true;
  }
}

function auditResolve(name,kind,e,extra=''){
  const A=AUD[name]; if(!e)return;
  const F=famStat(A,e);
  if(e.familySeen&&!e.materializedCounted){F.materialized++;e.materializedCounted=true;}
  if(kind==='hit'){
    A.stats.hit++;F.hit++;calRecord(e,'hit');
    qlog('🎯',name,'命中验证',e.action,e.family||'?',e.source||'?',e.hitMs+'ms','slot',e.slot,geoText(e),extra);
  }else if(kind==='changed'){
    A.stats.changed++;F.changed++;
    qlog('🟡',name,'路径改变/不计误报',e.action,e.family||'?',e.hitMs+'ms',extra);
  }else if(kind==='enemy'){
    A.stats.enemyChanged++;F.enemyChanged++;
    qlog('🟤',name,'目标攻击未按预测完成/不计误报',e.action,e.family||'?',e.source||'?',e.hitMs+'ms','slot',e.slot,
      e.enemyLost?'目标消失/换type':'预测Family未materialize',e.otherFamily?('实际/其它Family '+e.otherFamily):'',extra);
  }else if(kind==='ambiguous'){
    A.stats.ambiguousDamage++;F.ambiguousDamage++;
    qlog('⚪',name,'发生掉血但目标Family未确认/不计命中',e.action,e.family||'?',e.hitMs+'ms',extra);
  }else if(kind==='revoked'){
    A.stats.revoked++;F.revoked++;
    qlog('🔵',name,'预测已撤销/不计误报',e.action,e.family||'?',e.source||'?',e.hitMs+'ms','slot',e.slot,
      '目标攻击在预计碰撞前结束',extra);
  }else if(kind==='fp'){
    if(calFpEligible(e)){
      A.stats.falsePositive++;F.falsePositive++;calRecord(e,'fp');
      qlog('🔴',name,'高可信疑似误报',e.action,e.family||'?',e.source||'?',e.hitMs+'ms','slot',e.slot,geoText(e),
        '玩家路线未明显改变且目标攻击已成立但未掉血',extra);
    }else{
      A.stats.weakFalsePositive++;F.weakFalsePositive++;
      qlog('🟡',name,'低置信疑似误报/不计校准',e.action,e.family||'?',e.source||'?',e.hitMs+'ms','slot',e.slot,geoText(e),extra);
    }
  }
  if(e.auditKey)A.recent[e.auditKey]=performance.now();
  A.pending=null;
}

function auditStep(name,ps,st,raw,now){
  const A=AUD[name],action=st?actionOf(st):null,rawAction=raw?actionOf(raw):null;
  if(rawAction&&rawAction!=='SAFE')A.lastRawWarnAt=now;
  const hp=ps.hp;
  const e=A.pending;
  if(e)trackEnemy(e,now);

  const dropped=A.prevHp!=null&&hp<A.prevHp;
  if(dropped){
    if(e&&now>=e.due-CFG.auditHitEarlyMs&&now<=e.deadline+120){
      if(e.attackEndedEarly)auditResolve(name,'ambiguous',e,'预测已撤销后发生 HP '+A.prevHp+'→'+hp);
      else if(e.source==='active'||e.familySeen)auditResolve(name,'hit',e,'HP '+A.prevHp+'→'+hp);
      else auditResolve(name,'ambiguous',e,'HP '+A.prevHp+'→'+hp);
    }else if(now-A.lastWarnAt>350){
      if(now-A.lastRawWarnAt<=350){
        A.stats.unstableCovered++;
        const mc=captureMissCase('unstableCovered',name,ps,raw,now,A.prevHp,hp);
        qlog('🟧',name,'原始危险已覆盖/稳定器未确认','HP '+A.prevHp+'→'+hp,'case#'+mc.id);
      }else{
        A.stats.safeMiss++;
        const mc=captureMissCase('safeMiss',name,ps,raw,now,A.prevHp,hp);
        qlog('❌',name,'真实SAFE漏判','HP '+A.prevHp+'→'+hp,'case#'+mc.id,
          '候选',mc.candidates.slice(0,3).map(x=>'s'+x.slot+'/T'+x.type+'/A'+x.attack+'/'+(x.locked||'?')).join(' '));
      }
    }
  }
  A.prevHp=hp;

  const q=A.pending;
  if(q){
    if(!q.sampled&&now>=q.due){
      const dt=q.hitMs/1000;
      const ex=q.x+q.vx*dt,ey=q.y+q.vy*dt,ez=q.z+q.vz*dt;
      q.dx=Math.abs(ps.x-ex);q.dy=Math.abs(ps.y-ey);q.dz=Math.abs(ps.z-ez);
      q.changed=q.dx>CFG.auditTolX||q.dy>CFG.auditTolY||q.dz>CFG.auditTolZ;
      q.sampled=true;
    }
    if(A.pending&&now>=q.deadline){
      const info='偏移 x'+fmt(q.dx)+' y'+fmt(q.dy)+' z'+fmt(q.dz);
      const enemyInvalid=q.enemyLost||(q.source==='startup'&&!q.familySeen);
      auditResolve(name,q.attackEndedEarly?'revoked':enemyInvalid?'enemy':q.changed?'changed':'fp',q,info);
    }
  }

  if(st&&action!=='SAFE')A.lastWarnAt=now;
  if(!A.pending&&st&&action!=='SAFE'&&st.hitMs!=null){
    const h=st.hit||{};
    if(st.geometryWatchOnly||st.edgeWatchOnly)return;
    if(h.family==null||h.source==='active-unknown'||(h.actionable===false&&!h.calWatchOnly))return;
    const hitMs=Math.max(CFG.reactFloorMs,+st.hitMs||0);
    const instance=h.instance||((h.source||'?')+':'+(h.slot??-1)+':'+(h.family||'?'));
    const auditKey=(h.slot??-1)+'|'+(h.family||'?')+'|'+(h.source||'?')+'|'+instance;
    for(const [k,t] of Object.entries(A.recent))if(now-t>CFG.auditRepeatBlockMs*4)delete A.recent[k];
    if(A.recent[auditKey]!=null&&now-A.recent[auditKey]<CFG.auditRepeatBlockMs)return;
    const pp=playerAt(ps,'CONTINUE',hitMs,0);
    const rx=+h.rx||0,ry=+h.ry||0,rz=+h.rz||0;
    A.pending={player:name,action,family:h.family,source:h.source||null,variant:h.variant||null,slot:h.slot,enemyType:h.type,instance,auditKey,
      t0:now,due:now+hitMs,deadline:now+hitMs+CFG.auditGraceMs,hitMs,
      x:ps.x,y:ps.y,z:ps.z,vx:ps.vx,vy:ps.vy,vz:ps.vz,hp:ps.hp,
      rx,ry,rz,geoScale:h.geoScale?{...h.geoScale}:null,confidence:+h.confidence||0,survival:h.survival==null?1:+h.survival,
      mx:rx-Math.abs(pp.x-(+h.x||0)),my:ry-Math.abs(pp.y-(+h.y||0)),mz:rz-Math.abs(pp.z-(+h.z||0)),
      sampled:false,changed:false,dx:null,dy:null,dz:null,
      familySeen:h.source==='active',familyLastSeenAt:h.source==='active'?now:null,attackEndedEarly:false,materializedCounted:false,enemyLost:false,otherFamily:null,enemyLastAttack:null};
    A.stats.tested++;famStat(A,A.pending).tested++;
    trackEnemy(A.pending,now);
  }
}

function auditSnapshot(){
  const out={};
  for(const n of ['P1','P2','P3'])out[n]={...AUD[n].stats,pending:AUD[n].pending?{
    action:AUD[n].pending.action,family:AUD[n].pending.family,hitMs:AUD[n].pending.hitMs,source:AUD[n].pending.source,variant:AUD[n].pending.variant,
    slot:AUD[n].pending.slot,instance:AUD[n].pending.instance,familySeen:AUD[n].pending.familySeen}:null};
  return out;
}
function auditFamilies(){
  const out={};
  for(const n of ['P1','P2','P3'])out[n]=Object.entries(AUD[n].byFamily).map(([family,v])=>({family,...v,
    precision:(v.hit+v.falsePositive)?v.hit/(v.hit+v.falsePositive):null,
    confirmed:v.hit+v.falsePositive})).sort((a,b)=>(b.falsePositive-a.falsePositive)||(b.weakFalsePositive-a.weakFalsePositive)||(b.confirmed-a.confirmed)||(b.tested-a.tested));
  return out;
}
function frozenCopy(x){return JSON.parse(JSON.stringify(x));}
function reportSnapshot(){
  return frozenCopy({at:Date.now(),audit:auditSnapshot(),auditFamilies:auditFamilies(),calibration:calibrationSnapshot()});
}
function summarySnapshot(){
  const a=auditSnapshot(),af=auditFamilies(),c=calibrationSnapshot();
  const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0};
  for(const n of ['P1','P2','P3'])for(const k of Object.keys(total))total[k]+=+a[n]?.[k]||0;
  const fam=[];
  for(const n of ['P1','P2','P3'])for(const r of af[n]||[])fam.push({player:n,...r});
  const topFalse=fam.filter(r=>(r.falsePositive||0)+(r.weakFalsePositive||0)>0)
    .sort((x,y)=>((y.falsePositive||0)-(x.falsePositive||0))||((y.weakFalsePositive||0)-(x.weakFalsePositive||0))||(y.tested-x.tested)).slice(0,12);
  const demoted=[...(c.variant||[]),...(c.source||[]),...(c.family||[])].filter(r=>r.watchOnly).slice(0,20);
  const geoAdjusted=[...(c.variant||[]),...(c.source||[])].filter(r=>Array.isArray(r.geo)&&Math.min(...r.geo)<.995)
    .sort((x,y)=>Math.min(...x.geo)-Math.min(...y.geo)).slice(0,20);
  const geoClasses=(c.geom||[]).filter(r=>Array.isArray(r.geo)&&((r.geoFp||0)>0||Math.min(...r.geo)<.995))
    .sort((x,y)=>(y.geoFp||0)-(x.geoFp||0)).slice(0,20);
  const precisionSuppressed=[
    ...(c.variant||[]).filter(r=>(r.fp||0)>=CAL_CFG.precisionVariantFp&&(r.hit||0)===0),
    ...(c.source||[]).filter(r=>(r.confirmed||0)>=CAL_CFG.precisionSourceConfirmed&&(r.precision??1)<=CAL_CFG.precisionSourceMax&&(r.hit||0)===0),
    ...(c.family||[]).filter(r=>(r.confirmed||0)>=CAL_CFG.precisionFamilyConfirmed&&(r.precision??1)<=CAL_CFG.precisionFamilyMax&&(r.hit||0)<=1)
  ].slice(0,20);
  const validated=total.hit+total.falsePositive;
  const damageEvents=total.hit+total.ambiguousDamage+total.unstableCovered+total.safeMiss;
  const metrics={actionPrecision:validated?+(total.hit/validated).toFixed(3):null,
    rawDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage+total.unstableCovered)/damageEvents).toFixed(3):null,
    stableDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage)/damageEvents).toFixed(3):null,
    validated,damageEvents};
  return frozenCopy({at:Date.now(),total,metrics,players:a,topFalse,demoted,precisionSuppressed,geoAdjusted,geoClasses,missCases:MISS_CASES.slice(-8)});
}
function reportText(){return JSON.stringify(reportSnapshot(),null,2);}
function summaryText(){return JSON.stringify(summarySnapshot(),null,2);}

  let timer=null,last=null;
  function tick(){
  const now=performance.now();if(PLAYER_MODE==='local')syncLocalPlayer();updatePlayers(now);const d=buildDanger(now);captureEnemyFrame(now);last={at:now,playerMode:PLAYER_MODE,livePlayers:PLAYERS.filter(p=>!!readPlayer(p.base,p.name)).map(p=>p.name),players:{},enemyCount:d.enemies.size,dangerPoints:d.danger.length,exact:d.exact,coarse:d.coarse};
  for(const p of PLAYERS){
    const ps=PS[p.name];if(!ps)continue;
    const raw=decision(ps,d.danger),st=stable(p.name,raw);
    last.players[p.name]={raw,stable:st,state:{...ps}};
    auditStep(p.name,ps,st,raw,now);
    print(p.name,st,d.enemies.size);
  }
  self.WOFV4.last=last;
}

  function setPlayerEnabled(name,on){
    if(!(name in TRACK))throw new Error('player must be P1/P2/P3');
    PLAYER_MODE='manual';
    TRACK[name]=!!on;resetPlayerRuntime(name);
    qlog(TRACK[name]?'🔵':'⚫',name,TRACK[name]?'已手动加入预测/审计':'已手动移出预测/审计');
    return {...TRACK};
  }
  function useLocalPlayer(){PLAYER_MODE='local';syncLocalPlayer(true);return {mode:PLAYER_MODE,localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),localSeat:LOCAL_SEAT,localMode:LOCAL_MODE,tracked:{...TRACK}};}
  function spectateAll(){
    PLAYER_MODE='spectator';LOCAL_NAME=null;LOCAL_SEAT=null;LOCAL_MODE='spectator';
    for(const p of PLAYERS){if(!TRACK[p.name]){TRACK[p.name]=true;resetPlayerRuntime(p.name);}}
    qlog('👁️ 观战模式：同时预测/审计 RAM 中存在的 P1/P2/P3');
    return {mode:PLAYER_MODE,tracked:{...TRACK}};
  }

  self.WOFV4={
    version:'offline-dynamic-spectator-calibrated-v4.9.2',config:CFG,last:null,
    dbInfo:{exact:Object.keys(DB.e).length,coarse:Object.keys(DB.c).length,activeStart:Object.keys(DB.a).length,families:Object.keys(DB.f).length},
    status(){return{version:this.version,db:this.dbInfo,last:this.last,playerMode:PLAYER_MODE,livePlayers:livePlayerNames(),tracked:{...TRACK},players:PS,audit:auditSnapshot(),auditFamilies:auditFamilies()};},
    localPlayer(){const r=resolveLocalActor();return {name:LOCAL_NAME,no:localPlayerNo(),seat:LOCAL_SEAT,mode:PLAYER_MODE,live:r.live,tracked:{...TRACK}};},
    tracked(){return {...TRACK};},
    setPlayerEnabled,
    useLocalPlayer,
    spectateAll,
    audit(){return frozenCopy(auditSnapshot());},
    auditFamilies(){return frozenCopy(auditFamilies());},
    calibration(){return frozenCopy(calibrationSnapshot());},
    exportCalibration(){return frozenCopy(calibrationRaw());},
    snapshot(){return reportSnapshot();},
    summary(){return summarySnapshot();},
    misses(){return frozenCopy(MISS_CASES.slice());},
    report(){const t=reportText();self.console.log(t);return t;},
    reportShort(){const t=summaryText();self.console.log(t);return t;},
    quiet(on=true){QUIET=!!on;self.console.log(QUIET?'🔇 WOF实时日志已静音，统计继续':'🔊 WOF实时日志已恢复');return QUIET;},
    pause(){if(timer){clearInterval(timer);timer=null;}const r=reportSnapshot();self.console.log('⏸️ WOF观战统计已暂停');return r;},
    resume(){if(!timer){timer=setInterval(tick,CFG.tickMs);tick();}self.console.log('▶️ WOF观战统计已继续');return true;},
    resetCalibration(){return calibrationReset();},
    stop(){if(timer){clearInterval(timer);timer=null;}qlog('⛔ WOF V4关闭');}
  };
  spectateAll();
  timer=setInterval(tick,CFG.tickMs);tick();
  qlog('✅ WOF V4.9.2 精度优先信任门控观战版启动');
  qlog('🧪 验证: 🎯命中 / 🟡路径改变 / 🟤分支改变 / 🔵预测撤销 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判');
  qlog('✅ DB',self.WOFV4.dbInfo.families,'Family / exact',self.WOFV4.dbInfo.exact,'/ coarse',self.WOFV4.dbInfo.coarse);
  qlog('✅ 纯观战：P1/P2/P3共享Family可靠性；低精度Family自动降为WATCH，不删除危险点');
  qlog('🧭 XYZ几何: class fallback 保留完整外壳用于WATCH；行动核心 X/Y 缩放 '+CFG.fallbackXYActionScale+'/'+CFG.fallbackYActionScale+'，高Z核心='+(CFG.fallbackZActionCore+CFG.padZ));
  qlog('🧯 在线校准: 只有深入行动核心的误报才快速降级；擦边碰撞只WATCH，不处罚Family');
  qlog('🎯 精度优先: Variant首次高可信误报即隔离为WATCH；低精度source/family会联动隔离，新分支使用更小行动核心');
  qlog('📐 自适应几何: Family/Variant独立学习 + fallback几何类跨Family共享学习；完整危险外壳始终保留WATCH');
  qlog('🔬 漏判取证: 真实SAFE漏判自动保存最近600ms敌人状态/ATTACK/Family候选；WOFV4.misses()可查看');
  qlog('⚡ 稳定器: WATCH与<=300ms紧急UP/DOWN为2帧确认；AB仍需3帧；<=250ms危险保留较宽紧急核心');
  qlog('🧱 共享几何类: 至少4次高可信误报且来自>=3个Family才开始收缩行动核心');
  qlog('🟧 审计: unstableCovered=raw危险已覆盖但稳定器未确认；safeMiss=raw/stable都完全没看到危险');
  qlog('💾 热更新继承: Family/source/variant在线校准在同一Worker内升级版本时保留');
  qlog('🟪 边缘壳: 行动核心再内缩 '+Math.round(CFG.actionPenetrationMin*100)+'%，避免擦边UP/DOWN/AB');
  qlog('🎚️ 行动门槛: startup conf>='+CFG.startupActionMinConfidence+'；active survival>='+CFG.activeActionMinConfidence);
  qlog('📸 快照: WOFV4.reportShort() 看精简统计；WOFV4.report() 看完整数据');
  qlog('⚠️ 只预测，不控制任何玩家');
}

const __B64='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';
const __bin=atob(__B64);
const __u8=new Uint8Array(__bin.length);
for(let i=0;i<__bin.length;i++)__u8[i]=__bin.charCodeAt(i);
if(typeof DecompressionStream!=='function')throw new Error('DecompressionStream unavailable');
const __stream=new Blob([__u8]).stream().pipeThrough(new DecompressionStream('gzip'));
const __txt=await new Response(__stream).text();
const __DB=JSON.parse(__txt);
self.__WOFDB4=__DB;
try{
 await new Promise((resolve,reject)=>{
  const q=indexedDB.open('wof-future-ai-v4',1);
  q.onupgradeneeded=()=>{const d=q.result;if(!d.objectStoreNames.contains('kv'))d.createObjectStore('kv');};
  q.onerror=()=>reject(q.error);
  q.onsuccess=()=>{
   const d=q.result,tx=d.transaction('kv','readwrite');
   tx.objectStore('kv').put(__txt,'db');
   tx.oncomplete=()=>{d.close();resolve();};
   tx.onerror=()=>{const e=tx.error;d.close();reject(e);};
  };
 });
 qlog('✅ 403 Family DB 已缓存到浏览器；后续房间可用轻量加载器');
}catch(e){console.warn('⚠️ DB缓存失败，但当前房间仍可使用',e);}
__WOF_START_V4(__DB);
}catch(e){console.error('❌ WOF V4启动失败',e);}
})();
