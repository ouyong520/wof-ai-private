'use strict';
(function(rootFactory){
  const API=rootFactory();
  if(typeof globalThis!=='undefined')globalThis.WOFAlphaAutoBaselineHudAdapter=API;
  if(typeof module!=='undefined'&&module.exports)module.exports=API;
})(function(){
  const SCHEMA='wof-alpha-auto-baseline-hud-adapter-v1';
  const DRAW_SCHEMA='wof-alpha-auto-baseline-hud-draw-plan-v1';
  const CLASSIFICATION='UNVERIFIED_AUTO_BASELINE';
  const P37_SCHEMA='wof-native-marker-auto-acquisition-baseline-v1';
  const P37_TESTED_COMMIT='64d5c3d2c1c84fffc7d9f59e701ec37fd1c68530';
  const NATIVE_WIDTH=384,NATIVE_HEIGHT=224;
  const DEFAULT_VISIBLE_STALE_MS=450;
  const PLAYERS=Object.freeze(['P1','P2','P3']);
  const ELIGIBILITY=Object.freeze({p29Pass:false,p32NativeMarkerQualification:false,p36RendererSourceTrace:false,p34RetryReadiness:false,promotion:false});
  const SAFETY=Object.freeze({readOnly:true,ramWrites:0,inputInjection:false});

  function finite(v){return Number.isFinite(v);}
  function cloneEligibility(){return {...ELIGIBILITY};}
  function boundary(){return{rendererSourceProof:null,authorityEligibility:cloneEligibility(),promotionEligibility:false};}
  function validTrack(track){
    return !!track&&track.state==='TRACKED'&&track.observed===true&&track.coordinateClass==='OBSERVED_DIAGNOSTIC_PIXEL_STRUCTURE'&&
      track.nativeWidth===NATIVE_WIDTH&&track.nativeHeight===NATIVE_HEIGHT&&track.nativeYAxis==='TOP_LEFT_POSITIVE_DOWN'&&
      finite(track.x)&&finite(track.y)&&track.x>=0&&track.x<=NATIVE_WIDTH&&track.y>=0&&track.y<=NATIVE_HEIGHT;
  }
  function validateEnvelope(env){
    if(!env||env.schema!==P37_SCHEMA||env.classification!==CLASSIFICATION)return{ok:false,reason:'P37_IDENTITY_INVALID'};
    if(env.nativeWidth!==NATIVE_WIDTH||env.nativeHeight!==NATIVE_HEIGHT||env.nativeYAxis!=='TOP_LEFT_POSITIVE_DOWN')return{ok:false,reason:'P37_NATIVE_COORDINATE_CONTRACT_INVALID'};
    if(env.zeroClick!==true||env.manualSeedRequired!==false||env.manualPlayerSelectionRequired!==false)return{ok:false,reason:'P37_ZERO_CLICK_CONTRACT_INVALID'};
    if(env.rendererSourceProof!==null)return{ok:false,reason:'P37_RENDERER_PROOF_BOUNDARY_VIOLATION'};
    const a=env.authorityEligibility;
    if(!a||a.p29Pass!==false||a.p32NativeMarkerQualification!==false||a.p36RendererSourceTrace!==false||a.p34RetryReadiness!==false||a.promotion!==false)return{ok:false,reason:'P37_AUTHORITY_BOUNDARY_VIOLATION'};
    if(!env.safety||env.safety.readOnly!==true||env.safety.ramWrites!==0||env.safety.inputInjection!==false)return{ok:false,reason:'P37_SAFETY_BOUNDARY_VIOLATION'};
    if(!env.tracks||typeof env.tracks!=='object')return{ok:false,reason:'P37_TRACKS_MISSING'};
    return{ok:true,reason:null};
  }
  function requireP37(api){
    if(!api||api.CLASSIFICATION!==CLASSIFICATION||api.SCHEMA!==P37_SCHEMA||api.NATIVE_WIDTH!==NATIVE_WIDTH||api.NATIVE_HEIGHT!==NATIVE_HEIGHT||typeof api.createBaselineTracker!=='function'||typeof api.mapNativeToViewport!=='function')throw new Error('P37 exact diagnostic API unavailable');
    return api;
  }
  function createController(p37Api,options={}){
    const p37=requireP37(p37Api||(typeof globalThis!=='undefined'?globalThis.WOFAutoMarkerBaselineP37:null));
    const tracker=p37.createBaselineTracker();
    const visibleStaleMs=Number.isFinite(options.visibleStaleMs)&&options.visibleStaleMs>0?options.visibleStaleMs:DEFAULT_VISIBLE_STALE_MS;
    let enabled=false,lastEnvelope=null,lastReceiveAt=null,lastReason='DIAGNOSTIC_GATE_OFF',ingestCount=0,rejectedCount=0;

    function setEnabled(value){
      enabled=value===true;
      if(!enabled){lastEnvelope=null;lastReceiveAt=null;lastReason='DIAGNOSTIC_GATE_OFF';tracker.reset?.();}
      else lastReason='WAITING_FOR_P37_FRAME';
      return status();
    }
    function ingestFrame(frame,timestampMs,receiveAtMs=Date.now()){
      if(!enabled){lastReason='DIAGNOSTIC_GATE_OFF';return status(receiveAtMs);}
      if(!finite(receiveAtMs)){lastReason='RECEIVE_TIME_INVALID';lastEnvelope=null;lastReceiveAt=null;rejectedCount++;return status();}
      const env=tracker.ingestFrame(frame,timestampMs);ingestCount++;
      const checked=validateEnvelope(env);
      if(!checked.ok){lastEnvelope=null;lastReceiveAt=receiveAtMs;lastReason=checked.reason;rejectedCount++;return status(receiveAtMs);}
      lastEnvelope=env;lastReceiveAt=receiveAtMs;lastReason=null;return status(receiveAtMs);
    }
    function drawPlan(drawingBuffer,nowMs=Date.now()){
      const base={schema:DRAW_SCHEMA,classification:CLASSIFICATION,p37TestedCommit:P37_TESTED_COMMIT,enabled,zeroClick:true,manualSeedRequired:false,manualPlayerSelectionRequired:false,nativeWidth:NATIVE_WIDTH,nativeHeight:NATIVE_HEIGHT,nativeYAxis:'TOP_LEFT_POSITIVE_DOWN',items:[],reason:null,...boundary(),safety:{...SAFETY}};
      if(!enabled)return{...base,reason:'DIAGNOSTIC_GATE_OFF'};
      if(!lastEnvelope||lastReceiveAt===null)return{...base,reason:lastReason||'WAITING_FOR_P37_FRAME'};
      if(!finite(nowMs)||nowMs-lastReceiveAt>visibleStaleMs)return{...base,reason:'STALE_BASELINE_ENVELOPE'};
      if(lastEnvelope.state==='AMBIGUOUS'||PLAYERS.some(p=>lastEnvelope.tracks?.[p]?.state==='AMBIGUOUS'))return{...base,reason:'AMBIGUOUS_FAIL_CLOSED'};
      const W=Number(drawingBuffer?.width),H=Number(drawingBuffer?.height);
      if(!(finite(W)&&finite(H)&&W>0&&H>0))return{...base,reason:'DRAWING_BUFFER_INVALID'};
      const rect={left:0,top:0,width:W,height:H};
      const sx=W/NATIVE_WIDTH,sy=H/NATIVE_HEIGHT,bw=136*sx,bh=34*sy,gap=4*sy;
      for(const player of PLAYERS){
        const track=lastEnvelope.tracks[player];if(!validTrack(track))continue;
        const point=p37.mapNativeToViewport({x:track.x,y:track.y},rect);
        if(!point||!finite(point.x)||!finite(point.y)||point.yTransform!=='PRESERVE_TOP_LEFT_POSITIVE_DOWN_NO_INVERSION')continue;
        const x=Math.max(0,Math.min(W-bw,point.x-bw/2)),y=Math.max(0,Math.min(H-bh,point.y-bh-gap));
        base.items.push({player,labelSemantic:track.labelSemantic||`${player.slice(1)}P`,classification:CLASSIFICATION,native:{x:track.x,y:track.y,width:NATIVE_WIDTH,height:NATIVE_HEIGHT,yAxis:'TOP_LEFT_POSITIVE_DOWN'},anchorDb:{x:point.x,y:point.y,yTransform:point.yTransform},drawRectDb:{x,y,width:bw,height:bh},observed:true,coordinateClass:track.coordinateClass,acquisition:track.acquisition||null,reacquireCount:Number(track.reacquireCount||0)});
      }
      return{...base,reason:base.items.length?null:'NO_FRESH_UNAMBIGUOUS_TRACKS'};
    }
    function status(nowMs=Date.now()){
      const ageMs=lastReceiveAt===null||!finite(nowMs)?null:Math.max(0,nowMs-lastReceiveAt);
      const visibleFresh=enabled&&!!lastEnvelope&&ageMs!==null&&ageMs<=visibleStaleMs&&lastEnvelope.state!=='AMBIGUOUS'&&!PLAYERS.some(p=>lastEnvelope.tracks?.[p]?.state==='AMBIGUOUS');
      return{schema:SCHEMA,classification:CLASSIFICATION,p37Schema:P37_SCHEMA,p37TestedCommit:P37_TESTED_COMMIT,enabled,state:!enabled?'DISABLED':lastReason?lastReason:(visibleFresh?'READY':'STALE_OR_UNAVAILABLE'),zeroClick:true,manualSeedRequired:false,manualPlayerSelectionRequired:false,nativeWidth:NATIVE_WIDTH,nativeHeight:NATIVE_HEIGHT,nativeYAxis:'TOP_LEFT_POSITIVE_DOWN',visibleStaleMs,lastReceiveAt,ageMs,ingestCount,rejectedCount,envelopeState:lastEnvelope?.state||null,tracks:lastEnvelope?.tracks?Object.fromEntries(PLAYERS.map(p=>[p,{...lastEnvelope.tracks[p]}])):{},visibleFresh,...boundary(),safety:{...SAFETY}};
    }
    return Object.freeze({setEnabled,ingestFrame,drawPlan,status,reset(){tracker.reset?.();lastEnvelope=null;lastReceiveAt=null;lastReason=enabled?'WAITING_FOR_P37_FRAME':'DIAGNOSTIC_GATE_OFF';return status();}});
  }
  return Object.freeze({SCHEMA,DRAW_SCHEMA,CLASSIFICATION,P37_SCHEMA,P37_TESTED_COMMIT,NATIVE_WIDTH,NATIVE_HEIGHT,DEFAULT_VISIBLE_STALE_MS,validateEnvelope,createController});
});
