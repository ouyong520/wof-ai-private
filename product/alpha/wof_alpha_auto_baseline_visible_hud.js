'use strict';
(function(factory){
  const API=factory();
  if(typeof globalThis!=='undefined')globalThis.WOFAutoBaselineVisibleHUDP39=API;
  if(typeof module!=='undefined'&&module.exports)module.exports=API;
})(function(){
  const SCHEMA='wof-alpha-auto-baseline-visible-hud-v1';
  const CLASSIFICATION='UNVERIFIED_AUTO_BASELINE';
  const P37_TESTED_COMMIT='64d5c3d2c1c84fffc7d9f59e701ec37fd1c68530';
  const SAFETY=Object.freeze({readOnly:true,ramWrites:0,inputInjection:false});
  const ELIGIBILITY=Object.freeze({p29Pass:false,p32NativeMarkerQualification:false,p36RendererSourceTrace:false,p34RetryReadiness:false,promotion:false});

  function install(options={}){
    const root=options.root||(typeof globalThis!=='undefined'?globalThis:null);
    const doc=options.document||root?.document;
    if(!root||!doc)throw new Error('P39 browser diagnostic environment missing');
    try{root.WOFALPHAAUTOBASELINEHUD?.dispose?.();}catch(_){}
    const hud=root.WOFALPHAHUD,bridge=root.__WOF_GL_HOOK,gameCanvas=root.I_GF1TC||doc.getElementById?.('whathis');
    const p37=root.WOFAutoMarkerBaselineP37,adapter=root.WOFAlphaAutoBaselineHudAdapter;
    if(!hud||typeof hud.status!=='function')throw new Error('maintained Alpha HUD missing');
    if(!bridge||typeof bridge.callback!=='function')throw new Error('maintained Alpha HUD draw callback missing');
    if(!gameCanvas||typeof gameCanvas.getBoundingClientRect!=='function')throw new Error('game canvas missing');
    if(!p37||p37.CLASSIFICATION!==CLASSIFICATION)throw new Error('P37 exact diagnostic baseline missing');
    if(!adapter||adapter.CLASSIFICATION!==CLASSIFICATION||typeof adapter.createController!=='function')throw new Error('P39 diagnostic adapter missing');
    const controller=adapter.createController(p37,{visibleStaleMs:options.visibleStaleMs});
    let enabled=false,disposed=false,priorCallback=null,wrapper=null,overlay=null,ctx=null,lastPlan=null,lastDrawAt=null,drawCount=0,markerDrawCount=0,lastError=null;

    function removeOverlay(){
      if(overlay){try{overlay.remove?.();}catch(_){try{overlay.parentNode?.removeChild?.(overlay);}catch(__){}}}
      overlay=null;ctx=null;
    }
    function ensureOverlay(){
      if(overlay&&ctx)return true;
      overlay=doc.createElement('canvas');
      if(!overlay||typeof overlay.getContext!=='function'){overlay=null;return false;}
      overlay.setAttribute?.('data-wof-alpha-p39','UNVERIFIED_AUTO_BASELINE');
      const s=overlay.style||{};s.position='fixed';s.pointerEvents='none';s.zIndex='2147483000';s.left='0px';s.top='0px';s.width='0px';s.height='0px';
      ctx=overlay.getContext('2d');if(!ctx){overlay=null;return false;}
      (doc.body||doc.documentElement)?.appendChild?.(overlay);return true;
    }
    function syncOverlay(){
      if(!ensureOverlay())return null;
      const r=gameCanvas.getBoundingClientRect();
      if(!r||!Number.isFinite(r.left)||!Number.isFinite(r.top)||!Number.isFinite(r.width)||!Number.isFinite(r.height)||r.width<=0||r.height<=0){overlay.style.display='none';return null;}
      overlay.style.display='block';overlay.style.left=`${r.left}px`;overlay.style.top=`${r.top}px`;overlay.style.width=`${r.width}px`;overlay.style.height=`${r.height}px`;
      const w=Math.max(1,Math.round(r.width)),h=Math.max(1,Math.round(r.height));if(overlay.width!==w)overlay.width=w;if(overlay.height!==h)overlay.height=h;
      return{width:w,height:h};
    }
    function paintHeader(reason){
      const text=CLASSIFICATION+(reason?` · ${reason}`:'');
      ctx.font='bold 11px sans-serif';ctx.textBaseline='top';ctx.textAlign='left';const w=Math.min(overlay.width-4,Math.max(188,ctx.measureText?.(text)?.width+12||188));
      ctx.fillStyle='rgba(0,0,0,.88)';ctx.fillRect(2,2,w,20);ctx.strokeStyle='rgba(255,255,255,.96)';ctx.lineWidth=1;ctx.strokeRect(2.5,2.5,w-1,19);ctx.fillStyle='#fff';ctx.fillText(text,7,6);
    }
    function paintItem(item){
      const r=item.drawRectDb,a=item.anchorDb;if(!r||!a)return;
      ctx.strokeStyle='rgba(255,255,255,.98)';ctx.fillStyle='rgba(0,0,0,.90)';ctx.lineWidth=2;ctx.beginPath();ctx.arc(a.x,a.y,4,0,Math.PI*2);ctx.stroke();
      ctx.beginPath();ctx.moveTo(a.x,a.y-4);ctx.lineTo(Math.max(r.x,Math.min(r.x+r.width,a.x)),r.y+r.height);ctx.stroke();
      ctx.fillRect(r.x,r.y,r.width,r.height);ctx.strokeRect(r.x+1,r.y+1,Math.max(0,r.width-2),Math.max(0,r.height-2));ctx.fillStyle='#fff';ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.font=`bold ${Math.max(10,Math.min(16,r.height*.38))}px sans-serif`;ctx.fillText(`${item.labelSemantic} AUTO`,r.x+r.width/2,r.y+r.height*.34);
      ctx.font=`bold ${Math.max(7,Math.min(10,r.height*.23))}px sans-serif`;ctx.fillText(CLASSIFICATION,r.x+r.width/2,r.y+r.height*.72);
      markerDrawCount++;
    }
    function drawDiagnostic(now=Date.now()){
      if(!enabled||disposed)return false;
      const size=syncOverlay();if(!size){lastPlan=null;return false;}
      const plan=controller.drawPlan(size,now);lastPlan=plan;ctx.clearRect(0,0,overlay.width,overlay.height);paintHeader(plan.reason);
      for(const item of plan.items||[])paintItem(item);
      drawCount++;lastDrawAt=now;return true;
    }
    function enable(){
      if(disposed)throw new Error('P39 diagnostic HUD disposed');
      if(enabled)return status();
      if(typeof bridge.callback!=='function')throw new Error('maintained Alpha HUD callback unavailable');
      priorCallback=bridge.callback;controller.setEnabled(true);enabled=true;
      wrapper=function(){const out=priorCallback.apply(this,arguments);try{drawDiagnostic(Date.now());}catch(e){lastError=String(e?.stack||e);}return out;};
      bridge.callback=wrapper;ensureOverlay();drawDiagnostic(Date.now());return status();
    }
    function disable(reason='DIAGNOSTIC_GATE_OFF'){
      if(!enabled){removeOverlay();return status();}
      enabled=false;controller.setEnabled(false);
      if(bridge.callback===wrapper)bridge.callback=priorCallback;else lastError='MAINTAINED_HUD_DRAW_CHAIN_CHANGED';
      wrapper=null;priorCallback=null;lastPlan=null;removeOverlay();return status(undefined,reason);
    }
    function ingestFrame(frame,timestampMs,receiveAtMs=Date.now()){
      if(!enabled)return status(receiveAtMs);
      controller.ingestFrame(frame,timestampMs,receiveAtMs);drawDiagnostic(receiveAtMs);return status(receiveAtMs);
    }
    function status(now=Date.now(),overrideState=null){
      const c=controller.status(now),hs=(()=>{try{return hud.status()||{};}catch(_){return{};}})();
      const items=enabled&&lastPlan&&Array.isArray(lastPlan.items)?lastPlan.items:[];
      return{schema:SCHEMA,classification:CLASSIFICATION,p37TestedCommit:P37_TESTED_COMMIT,enabled,disposed,state:overrideState||(!enabled?'DISABLED':c.state),zeroClick:true,manualAvatarClickRequired:false,manualPortraitSeedRequired:false,manualSeedRequired:false,manualPlayerSelectionRequired:false,automaticPlayers:['P1','P2','P3'],automaticReacquire:true,nativeWidth:384,nativeHeight:224,nativeYAxis:'TOP_LEFT_POSITIVE_DOWN',viewportYInversion:false,maintainedHudVersion:String(hs.version||''),maintainedHudDrawHooked:hs.drawHooked===true,diagnosticCallbackHooked:enabled&&bridge.callback===wrapper,overlayAttached:!!overlay,visiblePlayers:items.map(x=>x.player),drawCount,markerDrawCount,lastDrawAt,lastError,controller:c,lastPlan:lastPlan?{...lastPlan,items:items.map(x=>({...x,native:{...x.native},anchorDb:{...x.anchorDb},drawRectDb:{...x.drawRectDb}}))}:null,rendererSourceProof:null,authorityEligibility:{...ELIGIBILITY},promotionEligibility:false,productAuthority:'NONE_DIAGNOSTIC_ONLY',safety:{...SAFETY}};
    }
    function dispose(){
      if(disposed)return;disable('DISPOSED');disposed=true;if(root.WOFALPHAAUTOBASELINEHUD===instance)try{delete root.WOFALPHAAUTOBASELINEHUD;}catch(_){root.WOFALPHAAUTOBASELINEHUD=null;}
    }
    const instance=Object.freeze({enable,disable,ingestFrame,status,dispose});root.WOFALPHAAUTOBASELINEHUD=instance;return instance;
  }
  return Object.freeze({SCHEMA,CLASSIFICATION,P37_TESTED_COMMIT,install});
});
