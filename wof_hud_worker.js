(async()=>{
  'use strict';
  const CFG={
    runtimeUrl:'https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_v4_install_once.js',
    channel:'wof-ai-hud-v1',tickMs:40,requiredVersion:'v4.11.4'
  };
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));

  if(self.__WOF_HUD_BRIDGE?.stop){try{self.__WOF_HUD_BRIDGE.stop();}catch(_){}}
  if(!self.WOFV4||!String(self.WOFV4.version||'').includes(CFG.requiredVersion)){
    const code=await fetch(CFG.runtimeUrl+'?'+Date.now()).then(r=>{if(!r.ok)throw new Error('runtime fetch '+r.status);return r.text();});
    (0,eval)(code);for(let i=0;i<60&&!self.WOFV4;i++)await sleep(100);
  }
  if(!self.WOFV4)throw new Error('WOFV4 runtime not available');
  self.WOFV4.spectateAll?.();self.WOFV4.quiet?.(true);

  const PLAYER_BASE={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC},POOL=0xFFC0BC,STRIDE=0xE0;
  let B=null,U32=null,S32=null,W=null;
  try{
    const M=_0x515056.HEAPU8,R=_0x515056.HEAPU32[0x2e39e4>>>2]>>>0;
    B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
    U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
    S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};W=v=>v/65536;
  }catch(e){}

  function relation(name,p,slot){
    if(!B||!W||slot==null||slot<0||slot>=20)return {threatSide:null,threatFacing:null,enemyX:null,playerFace:null};
    try{
      const pb=PLAYER_BASE[name],eb=POOL+(+slot)*STRIDE;if(!pb||!B(pb)||!B(eb))return {threatSide:null,threatFacing:null,enemyX:null,playerFace:null};
      const px=Number.isFinite(+p?.state?.x)?+p.state.x:W(S32(pb+4)),ex=W(S32(eb+4)),face=B(pb+0x16),dx=ex-px;
      if(Math.abs(dx)<2)return {threatSide:'CENTER',threatFacing:'正面近身',enemyX:ex,playerFace:face};
      const side=dx<0?'LEFT':'RIGHT',faceSign=face===255?-1:1,front=(dx<0?-1:1)===faceSign;
      return {threatSide:side,threatFacing:front?'前方怪':'后方怪',enemyX:ex,playerFace:face};
    }catch(e){return {threatSide:null,threatFacing:null,enemyX:null,playerFace:null};}
  }

  const bc=new BroadcastChannel(CFG.channel);
  const actionOf=r=>!r?.danger?'SAFE':r.watchOnly?'WATCH':r.noRoute?(r.abReady?'AB':'WATCH'):r.best;
  const sourceOf=(st,a)=>{
    if(!st||a==='SAFE'||a==='NONE')return null;
    if(a==='UP'||a==='DOWN'||a==='AB')return 'ACTION';
    return st.tailWatchOnly?'TAIL':st.guardWatchOnly?'GUARD':st.shadowWatchOnly?'SHADOW':st.debounceWatchOnly?'BRIDGE':st.phaseWatchOnly?'PHASE':st.geometryWatchOnly?'GEOMETRY':st.edgeWatchOnly?'EDGE':'WATCH';
  };
  const levelOf=(src,a)=>{if(a==='UP'||a==='DOWN'||a==='AB')return 3;if(!src)return 0;return (src==='GUARD'||src==='GEOMETRY'||src==='SHADOW')?1:2;};
  const finite=v=>v==null?null:(Number.isFinite(+v)?+v:null);
  function playerRow(name,p){
    const st=p?.stable||null,a=st?actionOf(st):'NONE',src=sourceOf(st,a),h=st?.hit||{},rel=relation(name,p,h.slot);
    return {
      name,action:a,source:src,level:levelOf(src,a),
      hitMs:finite(st?.hitMs),latestMs:finite(st?.latestMs),routeUntil:finite(st?.routeUntil),
      family:h.family||null,type:h.type??null,slot:h.slot??null,dangerSource:h.source||null,
      threatSide:rel.threatSide,threatFacing:rel.threatFacing,enemyX:finite(rel.enemyX),playerFace:rel.playerFace,
      noRoute:!!st?.noRoute,abReady:!!st?.abReady,
      up:finite(st?.up),down:finite(st?.down),upHitMs:finite(st?.upHitMs),downHitMs:finite(st?.downHitMs),
      hp:finite(p?.state?.hp),x:finite(p?.state?.x),y:finite(p?.state?.y),z:finite(p?.state?.z)
    };
  }

  let running=true,lastSentAt=0,timer=null;
  function send(){
    if(!running)return;const x=self.WOFV4?.last;if(!x)return;const players={};
    for(const n of ['P1','P2','P3'])players[n]=playerRow(n,x.players?.[n]);
    const msg={schema:'wof-hud-v1',kind:'state',sentAt:Date.now(),runtimeVersion:self.WOFV4.version,playerMode:x.playerMode||'spectator',enemyCount:x.enemyCount||0,dangerPoints:x.dangerPoints||0,players};
    bc.postMessage(msg);lastSentAt=msg.sentAt;
  }
  timer=setInterval(send,CFG.tickMs);send();
  self.__WOF_HUD_BRIDGE={
    version:'hud-bridge-v2-threat-side',channel:CFG.channel,get running(){return running;},
    status(){return {running,lastSentAt,runtimeVersion:self.WOFV4?.version||null,channel:CFG.channel};},send,
    stop(){running=false;if(timer){clearInterval(timer);timer=null;}try{bc.close();}catch(_){};console.log('⛔ WOF HUD bridge stopped');}
  };
  console.log('✅ WOF HUD bridge v2 started | front/back threat relation enabled');
  console.log('🖥️ top Console 加载 wof_hud_overlay.js；只显示提示，不控制玩家');
  return self.__WOF_HUD_BRIDGE.status();
})().catch(e=>console.error('❌ WOF HUD bridge failed',e));
