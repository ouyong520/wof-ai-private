// ==UserScript==
// @name         WOF Alpha RC3 Browser Acceptance Helper
// @namespace    https://github.com/ouyong520/wof-ai-private
// @version      0.1.0
// @description  Support-only one-click real-Browser acceptance collector for WOF Alpha RC3. Does not modify product/alpha or game RAM/input.
// @match        *://*/*
// @run-at       document-start
// @grant        none
// ==/UserScript==
(()=>{
'use strict';
if(window.__WOF_ALPHA_ACCEPTANCE_HELPER)return;

const VERSION='wof-alpha-browser-acceptance-helper-v1';
const SCHEMA='wof-alpha-browser-acceptance-v1';
const RELEASE='wof-alpha-rc3';
const PRODUCT_SCHEMA='wof-alpha-v2';
const BUILD='wof / Warriors of Fate (World 921031)';
const GOLDEN_SHA256='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const IDENTITY_SIGNATURE='wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8';
const QA_REQUIRED='PASS — READY FOR ONE REAL BROWSER ACCEPTANCE';
const ALLOWED_RULES=new Set([
  'T18_5440_CYCLE_BODY7512_TM4_LEVEL_90',
  'T18_5424_CYCLE_BODY7520_TM4_LEVEL_90'
]);
const TARGET_BY_7E={0:'P1',4:'P2',8:'P3'};
const SIDE_VALUES=new Set(['LEFT','CENTER','RIGHT']);
const CONTROL_CHANNEL='wof-alpha-acceptance-control-v1';
const AUX_PREFIX='WOF_ALPHA_ACCEPT_AUX_';
const AUX_RUN=window.name.startsWith(AUX_PREFIX)?window.name.slice(AUX_PREFIX.length):null;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const nowIso=()=>new Date().toISOString();
const round=(n,d=3)=>Number.isFinite(n)?+n.toFixed(d):null;
const randHex=n=>{const b=new Uint8Array(n);crypto.getRandomValues(b);return [...b].map(x=>x.toString(16).padStart(2,'0')).join('');};
const percentile=(arr,p)=>{if(!arr.length)return null;const a=[...arr].sort((x,y)=>x-y);return a[Math.min(a.length-1,Math.max(0,Math.ceil(p*a.length)-1))];};

const obs={
  cfg:null,productBc:null,stateCount:0,stateTimes:[],identitySignature:null,wrongIdentitySignatures:new Set(),
  diag:[],warningRows:0,invalidWarnings:[],legacySeenBeforeAlpha:false,
  gl:{installed:false,completed:false,samples:[],actualDrawSamples:0,mismatches:[],errors:[],original:null,wrapper:null,bridge:null}
};
const control=new BroadcastChannel(CONTROL_CHANNEL);
const controlInbox=[];
const controlWaiters=[];

function safeHudStatus(){try{return window.WOFALPHAHUD?.status?.()||null;}catch(e){return{error:String(e?.message||e)};}}
function safeBootstrap(){
  const b=window.__WOF_ALPHA_BOOTSTRAP_RC3;
  return b?{release:b.release||null,session:b.session||null,workerIntercepted:!!b.workerIntercepted,hudLoaded:!!b.hudLoaded,lastError:b.lastError||null}:null;
}
function safeConfig(){
  const c=window.__WOF_ALPHA_CONFIG;
  return c?{release:c.release||null,schema:c.schema||null,session:c.session||null,channel:c.channel||null}:null;
}
function validateWarning(w){
  const errors=[];
  if(!w||typeof w!=='object')return['warning is not an object'];
  if(!ALLOWED_RULES.has(w.ruleId))errors.push('ruleId outside RC3 production set: '+String(w.ruleId));
  if(!['P1','P2','P3'].includes(w.target))errors.push('invalid target: '+String(w.target));
  if(!Object.prototype.hasOwnProperty.call(TARGET_BY_7E,w.target7E)||TARGET_BY_7E[w.target7E]!==w.target)errors.push('target7E/target mismatch');
  if(!SIDE_VALUES.has(w.sourceSide))errors.push('invalid sourceSide: '+String(w.sourceSide));
  if(!SIDE_VALUES.has(w.threatSide))errors.push('invalid threatSide: '+String(w.threatSide));
  if(w.publication!=='hold-only-current-level')errors.push('publication is not hold-only-current-level');
  if(w.evidence!=='fresh-current-sample')errors.push('evidence is not fresh-current-sample');
  for(const k of ['atMs','ageMs','watchId','watch','cycle','history','previous','priorTarget'])if(Object.prototype.hasOwnProperty.call(w,k))errors.push('forbidden inherited/history field: '+k);
  return errors;
}
function observeProductMessage(m){
  if(!(m&&m.schema===PRODUCT_SCHEMA&&obs.cfg&&m.session===obs.cfg.session))return;
  if(m.kind==='state'){
    obs.stateCount++;
    const t=performance.now();obs.stateTimes.push(t);if(obs.stateTimes.length>1000)obs.stateTimes.shift();
    if(typeof m.identitySignature==='string'){
      if(m.identitySignature===IDENTITY_SIGNATURE)obs.identitySignature=m.identitySignature;
      else obs.wrongIdentitySignatures.add(m.identitySignature);
    }
    const rows=Array.isArray(m.warnings)?m.warnings:[];
    obs.warningRows+=rows.length;
    for(const w of rows){
      const errors=validateWarning(w);
      if(errors.length&&obs.invalidWarnings.length<20)obs.invalidWarnings.push({at:nowIso(),ruleId:w?.ruleId??null,errors});
    }
  }else if(m.kind==='diag'){
    const before=safeHudStatus();
    const item={at:nowIso(),reason:String(m.reason||m.status||'diagnostic'),warningCountBefore:before?.warningCount??null,warningCountNextTask:null};
    obs.diag.push(item);
    setTimeout(()=>{item.warningCountNextTask=safeHudStatus()?.warningCount??null;},0);
  }
}
function attachProductChannel(){
  const c=window.__WOF_ALPHA_CONFIG;
  if(!(c&&c.release===RELEASE&&c.schema===PRODUCT_SCHEMA&&typeof c.session==='string'&&typeof c.channel==='string'))return;
  if(obs.cfg&&obs.cfg.session===c.session&&obs.productBc)return;
  try{obs.productBc?.close?.();}catch(_){}
  obs.cfg={release:c.release,schema:c.schema,session:c.session,channel:c.channel};
  try{
    const bc=new BroadcastChannel(c.channel);
    bc.onmessage=e=>observeProductMessage(e.data);
    obs.productBc=bc;
  }catch(e){obs.diag.push({at:nowIso(),reason:'acceptance helper could not attach product channel: '+String(e?.message||e)});}
}

function glSnapshot(gl){
  const active=gl.getParameter(gl.ACTIVE_TEXTURE),activeTex=gl.getParameter(gl.TEXTURE_BINDING_2D);
  gl.activeTexture(gl.TEXTURE0);const tex0=gl.getParameter(gl.TEXTURE_BINDING_2D);gl.activeTexture(active);
  return{
    program:gl.getParameter(gl.CURRENT_PROGRAM),array:gl.getParameter(gl.ARRAY_BUFFER_BINDING),active,activeTex,tex0,
    viewport:Array.from(gl.getParameter(gl.VIEWPORT)),blend:gl.isEnabled(gl.BLEND),depth:gl.isEnabled(gl.DEPTH_TEST),
    cull:gl.isEnabled(gl.CULL_FACE),scissor:gl.isEnabled(gl.SCISSOR_TEST),srcRGB:gl.getParameter(gl.BLEND_SRC_RGB),
    dstRGB:gl.getParameter(gl.BLEND_DST_RGB),srcA:gl.getParameter(gl.BLEND_SRC_ALPHA),dstA:gl.getParameter(gl.BLEND_DST_ALPHA),
    eqRGB:gl.getParameter(gl.BLEND_EQUATION_RGB),eqA:gl.getParameter(gl.BLEND_EQUATION_ALPHA),mask:Array.from(gl.getParameter(gl.COLOR_WRITEMASK)),
    flip:gl.getParameter(gl.UNPACK_FLIP_Y_WEBGL),premul:gl.getParameter(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL),
    a0:{enabled:!!gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_ENABLED),buf:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_BUFFER_BINDING),
      size:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_SIZE),type:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_TYPE),
      norm:!!gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_NORMALIZED),stride:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_STRIDE),
      offset:gl.getVertexAttribOffset(0,gl.VERTEX_ATTRIB_ARRAY_POINTER)}
  };
}
function arrEq(a,b){return Array.isArray(a)&&Array.isArray(b)&&a.length===b.length&&a.every((v,i)=>v===b[i]);}
function glDiff(a,b){
  const out=[];
  for(const k of ['program','array','active','activeTex','tex0','blend','depth','cull','scissor','srcRGB','dstRGB','srcA','dstA','eqRGB','eqA','flip','premul'])if(a[k]!==b[k])out.push(k);
  if(!arrEq(a.viewport,b.viewport))out.push('viewport');if(!arrEq(a.mask,b.mask))out.push('colorMask');
  for(const k of ['enabled','buf','size','type','norm','stride','offset'])if(a.a0[k]!==b.a0[k])out.push('a0.'+k);
  return out;
}
function installGlProbe(){
  if(obs.gl.installed||AUX_RUN)return;
  const bridge=window.__WOF_GL_HOOK,hud=window.WOFALPHAHUD;
  if(!(bridge&&bridge.gl&&typeof bridge.callback==='function'&&hud?.status))return;
  const gl=bridge.gl,original=bridge.callback;
  obs.gl.installed=true;obs.gl.original=original;obs.gl.bridge=bridge;
  const wrapper=function(){
    if(obs.gl.samples.length>=30)return original.apply(this,arguments);
    let pre=null,post=null,d0=null,d1=null,value,thrown=null;
    try{pre=glSnapshot(gl);d0=safeHudStatus()?.drawCount??null;}catch(e){obs.gl.errors.push('pre-snapshot: '+String(e?.message||e));}
    const t0=performance.now();
    try{value=original.apply(this,arguments);}catch(e){thrown=e;}
    const dt=performance.now()-t0;
    try{d1=safeHudStatus()?.drawCount??null;post=glSnapshot(gl);}catch(e){obs.gl.errors.push('post-snapshot: '+String(e?.message||e));}
    const diffs=pre&&post?glDiff(pre,post):['snapshot-unavailable'];
    obs.gl.samples.push(dt);
    if(Number.isFinite(d0)&&Number.isFinite(d1)&&d1>d0)obs.gl.actualDrawSamples++;
    if(diffs.length&&obs.gl.mismatches.length<20)obs.gl.mismatches.push({sample:obs.gl.samples.length,fields:diffs});
    if(obs.gl.samples.length>=30){
      obs.gl.completed=true;
      setTimeout(()=>{if(bridge.callback===wrapper)bridge.callback=original;},0);
    }
    if(thrown)throw thrown;
    return value;
  };
  obs.gl.wrapper=wrapper;bridge.callback=wrapper;
}

async function readySnapshot(timeoutMs=20000){
  const until=performance.now()+timeoutMs;
  while(performance.now()<until){
    attachProductChannel();installGlProbe();
    const b=safeBootstrap(),c=safeConfig(),h=safeHudStatus();
    const ok=!!(b&&c&&h&&b.release===RELEASE&&b.workerIntercepted&&b.hudLoaded&&c.release===RELEASE&&c.schema===PRODUCT_SCHEMA&&
      b.session===c.session&&h.session===c.session&&h.release===RELEASE&&h.connected===true&&obs.identitySignature===IDENTITY_SIGNATURE);
    if(ok)return{ok:true,bootstrap:b,config:c,hud:h,identitySignature:obs.identitySignature};
    await sleep(100);
  }
  return{ok:false,bootstrap:safeBootstrap(),config:safeConfig(),hud:safeHudStatus(),identitySignature:obs.identitySignature};
}

function onControlMessage(m){
  if(!m||m.schema!==SCHEMA)return;
  controlInbox.push(m);if(controlInbox.length>100)controlInbox.shift();
  for(let i=controlWaiters.length-1;i>=0;i--){
    const w=controlWaiters[i];if(w.pred(m)){controlWaiters.splice(i,1);clearTimeout(w.timer);w.resolve(m);}
  }
  if(AUX_RUN&&m.runId===AUX_RUN){
    if(m.kind==='aux-reload'){
      try{sessionStorage.setItem('wof_alpha_accept_prev_'+AUX_RUN,String(obs.cfg?.session||''));}catch(_){}
      location.reload();
    }else if(m.kind==='aux-close'){
      try{window.close();}catch(_){}
    }
  }
}
control.onmessage=e=>onControlMessage(e.data);
function waitControl(pred,timeoutMs){
  const hit=controlInbox.find(pred);if(hit)return Promise.resolve(hit);
  return new Promise(resolve=>{
    const waiter={pred,resolve,timer:null};
    waiter.timer=setTimeout(()=>{const i=controlWaiters.indexOf(waiter);if(i>=0)controlWaiters.splice(i,1);resolve(null);},timeoutMs);
    controlWaiters.push(waiter);
  });
}
function sendControl(m){control.postMessage({schema:SCHEMA,at:Date.now(),...m});}

async function auxMode(){
  const snap=await readySnapshot(25000);
  let oldSession=null;try{oldSession=sessionStorage.getItem('wof_alpha_accept_prev_'+AUX_RUN);}catch(_){}
  const phase=oldSession?'reloaded':'initial';
  sendControl({kind:'aux-ready',runId:AUX_RUN,phase,oldSession:oldSession||null,ready:snap.ok,session:snap.config?.session||null,
    channel:snap.config?.channel||null,identitySignature:snap.identitySignature||null,workerIntercepted:!!snap.bootstrap?.workerIntercepted,
    hudLoaded:!!snap.bootstrap?.hudLoaded,connected:!!snap.hud?.connected,lastError:snap.bootstrap?.lastError||snap.hud?.lastError||null});
  if(oldSession){try{sessionStorage.removeItem('wof_alpha_accept_prev_'+AUX_RUN);}catch(_){}}
}

let ui=null,button=null,statusEl=null,outEl=null;
function ensureUi(){
  if(AUX_RUN||ui||!document.documentElement)return;
  const d=document.createElement('div');
  d.id='wof-alpha-acceptance-ui';
  d.style.cssText='position:fixed;right:10px;top:10px;z-index:2147483647;width:360px;max-height:78vh;overflow:auto;background:rgba(10,10,12,.96);color:#fff;border:1px solid #ddd;border-radius:8px;padding:10px;font:12px/1.35 sans-serif;box-shadow:0 2px 16px #0008';
  const title=document.createElement('div');title.textContent='WOF Alpha RC3 Acceptance';title.style.cssText='font-weight:700;font-size:14px;margin-bottom:6px';
  const note=document.createElement('div');note.textContent='PREP ONLY — run only after fresh RC3 QA PASS.';note.style.cssText='margin-bottom:8px;color:#ffd28a';
  const b=document.createElement('button');b.textContent='Run RC3 Browser Acceptance';b.style.cssText='width:100%;padding:8px;cursor:pointer;font-weight:700';
  const s=document.createElement('div');s.textContent='Waiting for real game/HUD…';s.style.cssText='margin-top:8px;white-space:pre-wrap';
  const pre=document.createElement('pre');pre.style.cssText='display:none;white-space:pre-wrap;word-break:break-word;margin-top:8px;padding:6px;background:#0008;max-height:42vh;overflow:auto';
  d.append(title,note,b,s,pre);document.documentElement.appendChild(d);ui=d;button=b;statusEl=s;outEl=pre;
  b.onclick=()=>runAcceptance();
}
function setStatus(t){if(statusEl)statusEl.textContent=t;}
function showResult(r){if(outEl){outEl.style.display='block';outEl.textContent=JSON.stringify(r,null,2);}if(button)button.disabled=false;}

async function performanceWindow(ms=6000){
  const h0=safeHudStatus(),bridge=window.__WOF_GL_HOOK;
  const state0=obs.stateCount,draw0=Number.isFinite(bridge?.gameDraws)?bridge.gameDraws:null,cb0=h0?.callbackCount??null,t0=performance.now();
  await sleep(ms);
  const elapsed=performance.now()-t0,h1=safeHudStatus();
  const stateDelta=obs.stateCount-state0,draw1=Number.isFinite(bridge?.gameDraws)?bridge.gameDraws:null,cb1=h1?.callbackCount??null;
  return{observationMs:round(elapsed,1),stateMessages:stateDelta,stateRateHz:round(stateDelta/(elapsed/1000),2),
    gameDrawsDelta:Number.isFinite(draw0)&&Number.isFinite(draw1)?draw1-draw0:null,hudCallbacksDelta:Number.isFinite(cb0)&&Number.isFinite(cb1)?cb1-cb0:null,
    connectedAtEnd:h1?.connected===true,hudStatusEnd:h1};
}

let running=false;
async function runAcceptance(){
  if(running)return;running=true;if(button)button.disabled=true;
  const startedAt=nowIso(),tStart=performance.now(),failures=[],incomplete=[];
  const fail=m=>failures.push(m),inc=m=>incomplete.push(m);
  setStatus('Checking primary real game page…');
  const primary=await readySnapshot(20000);
  if(!primary.ok){
    if(obs.diag.length)fail('primary detector emitted diagnostic before readiness');
    else inc('primary page did not become fully paired/connected with accepted identity within 20 s');
  }
  if(obs.wrongIdentitySignatures.size)fail('unexpected identity signature observed: '+[...obs.wrongIdentitySignatures].join(','));
  if(primary.identitySignature&&primary.identitySignature!==IDENTITY_SIGNATURE)fail('primary accepted identity signature mismatch');

  const primarySession=primary.config?.session||null,primaryChannel=primary.config?.channel||null;
  const perfPromise=performanceWindow(6000);
  const runId=randHex(8),auxName=AUX_PREFIX+runId;
  setStatus('Opening auxiliary tab and checking independent pairing…');
  let auxWin=null,aux1=null,aux2=null;
  try{auxWin=window.open(location.href,auxName);}catch(_){}
  if(!auxWin){inc('auxiliary same-origin game tab was blocked');}
  else{
    aux1=await waitControl(m=>m.kind==='aux-ready'&&m.runId===runId&&m.phase==='initial',25000);
    if(!aux1)inc('auxiliary initial page did not report readiness within 25 s');
    else if(!aux1.ready)inc('auxiliary initial page loaded but product did not become ready');
    if(aux1?.ready){
      if(aux1.identitySignature!==IDENTITY_SIGNATURE)fail('auxiliary initial identity signature mismatch');
      if(aux1.session===primarySession)fail('primary and auxiliary sessions collided');
      if(aux1.channel===primaryChannel)fail('primary and auxiliary product channels collided');
      sendControl({kind:'aux-reload',runId});
      setStatus('Auxiliary pairing is isolated. Reloading it once automatically…');
      aux2=await waitControl(m=>m.kind==='aux-ready'&&m.runId===runId&&m.phase==='reloaded',25000);
      if(!aux2)inc('auxiliary reload did not report a fresh pairing within 25 s');
      else if(!aux2.ready)inc('auxiliary reloaded page did not become ready');
      if(aux2?.ready){
        if(aux2.identitySignature!==IDENTITY_SIGNATURE)fail('auxiliary reload identity signature mismatch');
        if(aux2.oldSession!==aux1.session)fail('auxiliary reload did not report the expected previous session');
        if(aux2.session===aux1.session)fail('reload reused the previous auxiliary session');
        if(aux2.session===primarySession)fail('reloaded auxiliary session collided with primary session');
        if(aux2.channel===aux1.channel)fail('reload reused the previous auxiliary product channel');
      }
    }
    sendControl({kind:'aux-close',runId});
  }

  const perf=await perfPromise;
  const end=await readySnapshot(3000);
  if(primarySession&&end.config?.session!==primarySession)fail('primary session changed during acceptance without primary reload');
  if(!end.hud?.connected)fail('primary detector/HUD was not connected at end of run');
  if(end.identitySignature!==IDENTITY_SIGNATURE)fail('primary accepted identity missing at end of run');
  if(obs.diag.length)fail('paired runtime diagnostic/error occurred during Browser run');
  if(obs.invalidWarnings.length)fail('one or more naturally observed warnings violated RC3 current-rule/target/side contract');

  const hs=end.hud||safeHudStatus()||{};
  const glDur=obs.gl.samples.filter(Number.isFinite),p95=percentile(glDur,.95),max=glDur.length?Math.max(...glDur):null;
  const glRequiredSamples=10;
  if(!obs.gl.installed)inc('real Alpha WebGL callback probe could not attach');
  else if(glDur.length<glRequiredSamples)inc('fewer than 10 real HUD callback samples were captured');
  if(obs.gl.actualDrawSamples<1)inc('no sampled HUD callback performed an actual Alpha HUD draw; refresh and start acceptance promptly');
  if(obs.gl.errors.length)fail('WebGL state probe encountered errors');
  if(obs.gl.mismatches.length)fail('WebGL state changed across Alpha HUD callback');
  if(hs.drawHooked!==true)fail('Alpha HUD draw hook is not active');
  if(hs.lastError)fail('Alpha HUD/GL hook reported an error: '+String(hs.lastError));

  if(glDur.length>=glRequiredSamples){
    if(Number.isFinite(p95)&&p95>16)fail('HUD callback p95 exceeded 16 ms smoke threshold');
    if(Number.isFinite(max)&&max>50)fail('HUD callback sample exceeded 50 ms smoke threshold');
  }
  if(!(Number.isFinite(perf.gameDrawsDelta)&&perf.gameDrawsDelta>0))fail('game draw counter did not advance during performance window');
  if(!(perf.stateMessages>0&&perf.connectedAtEnd))fail('detector state stream did not remain live during performance window');

  const bootstrapPass=!!(primary.ok&&primary.bootstrap?.workerIntercepted&&primary.bootstrap?.hudLoaded&&primary.config?.session===primary.bootstrap?.session&&primary.hud?.session===primary.config?.session);
  const identityPass=primary.identitySignature===IDENTITY_SIGNATURE&&!obs.wrongIdentitySignatures.size;
  const webglIncomplete=!obs.gl.installed||glDur.length<glRequiredSamples||obs.gl.actualDrawSamples<1;
  const webglFail=!!(obs.gl.errors.length||obs.gl.mismatches.length||hs.drawHooked!==true||hs.lastError);
  const transportComplete=!!(aux1?.ready&&aux2?.ready);
  const transportPass=transportComplete&&aux1.session!==primarySession&&aux1.channel!==primaryChannel&&aux2.oldSession===aux1.session&&aux2.session!==aux1.session&&aux2.session!==primarySession&&aux2.channel!==aux1.channel&&end.hud?.connected===true;
  const legacyResult=obs.legacySeenBeforeAlpha?(hs.researchHudDisposed===true?'PASS':'FAIL'):'NOT_APPLICABLE';
  const warningResult=obs.invalidWarnings.length?'FAIL':(obs.warningRows?'PASS':'NOT_EXERCISED');
  const perfPass=glDur.length>=glRequiredSamples&&Number.isFinite(p95)&&p95<=16&&Number.isFinite(max)&&max<=50&&Number.isFinite(perf.gameDrawsDelta)&&perf.gameDrawsDelta>0&&perf.stateMessages>0&&perf.connectedAtEnd;

  if(!bootstrapPass&&!incomplete.some(x=>x.includes('primary page')))fail('primary bootstrap/pairing invariant failed');
  if(!identityPass&&!incomplete.some(x=>x.includes('primary page')))fail('exact World 921031 accepted identity evidence failed');
  if(legacyResult==='FAIL')fail('legacy WOFHUD was seen but Alpha did not report successful research HUD disposal');
  if(transportComplete&&!transportPass)fail('cross-tab/reload pairing invariant failed');

  let result='PASS — REAL BROWSER ACCEPTANCE';
  if(failures.length)result='FAIL — REAL BROWSER ACCEPTANCE';
  else if(incomplete.length||webglIncomplete||!transportComplete)result='INCOMPLETE — REAL BROWSER ACCEPTANCE';

  const final={
    schema:SCHEMA,result,release:RELEASE,supportedBuild:BUILD,goldenSha256:GOLDEN_SHA256,expectedIdentitySignature:IDENTITY_SIGNATURE,
    startedAt,finishedAt:nowIso(),durationMs:round(performance.now()-tStart,1),
    qaGate:{requiredExternalVerdict:QA_REQUIRED,checkedByHelper:false},
    checks:{
      bootstrap:{result:bootstrapPass?'PASS':(primary.ok?'FAIL':'INCOMPLETE'),workerIntercepted:!!primary.bootstrap?.workerIntercepted,hudLoaded:!!primary.bootstrap?.hudLoaded,
        primarySession,pageSessionMatches:!!(primary.config?.session&&primary.config.session===primary.bootstrap?.session),hudSessionMatches:!!(primary.hud?.session&&primary.hud.session===primary.config?.session),connected:!!primary.hud?.connected},
      identity:{result:identityPass?'PASS':(primary.identitySignature?'FAIL':'INCOMPLETE'),signatureObserved:primary.identitySignature||null,
        fullDigestAuthority:'product exact 1 MiB CPU-logical SHA-256 gate'},
      runtimeDiagnostics:{result:obs.diag.length?'FAIL':'PASS',count:obs.diag.length,items:obs.diag.slice(0,20)},
      webglHud:{result:webglFail?'FAIL':(webglIncomplete?'INCOMPLETE':'PASS'),drawHooked:hs.drawHooked===true,stateSamples:glDur.length,
        samplesWithActualHudDraw:obs.gl.actualDrawSamples,stateMismatchCount:obs.gl.mismatches.length,stateMismatches:obs.gl.mismatches,
        probeErrors:obs.gl.errors,hudCallbackP95Ms:round(p95),hudCallbackMaxMs:round(max),hudLastError:hs.lastError||null},
      transport:{result:transportPass?'PASS':(transportComplete?'FAIL':'INCOMPLETE'),primarySession,primaryChannel,
        auxInitialSession:aux1?.session||null,auxInitialChannel:aux1?.channel||null,auxReloadSession:aux2?.session||null,auxReloadChannel:aux2?.channel||null,
        initialIsolation:!!(aux1?.ready&&aux1.session!==primarySession&&aux1.channel!==primaryChannel),
        reloadCreatedFreshPairing:!!(aux2?.ready&&aux2.oldSession===aux1?.session&&aux2.session!==aux1?.session&&aux2.channel!==aux1?.channel),
        primaryStayedConnected:!!(end.hud?.connected&&end.config?.session===primarySession)},
      legacyHud:{result:legacyResult,legacySeenBeforeAlpha:obs.legacySeenBeforeAlpha,alphaReportsResearchHudDisposed:hs.researchHudDisposed===true},
      warningSanity:{result:warningResult,observedWarningRows:obs.warningRows,allowedRuleIds:[...ALLOWED_RULES],invalidRows:obs.invalidWarnings},
      performance:{result:perfPass?'PASS':(webglIncomplete?'INCOMPLETE':'FAIL'),...perf,automaticLimits:{minimumHudCallbackSamples:10,hudCallbackP95MsMax:16,hudCallbackSingleMaxMs:50,requiresGameDrawAdvance:true,requiresDetectorContinuity:true}},
      safetyContract:{result:'EXTERNAL_QA_PRECONDITION',readOnly:true,ramWrites:0,inputInjection:false,note:'Fresh independent QA/static source inspection is authoritative; this support helper performs no game RAM or gameplay-input access.'}
    },
    failures:[...new Set(failures)],incomplete:[...new Set(incomplete)],
    notes:[warningResult==='NOT_EXERCISED'?'No active T18 warning occurred naturally; infrastructure acceptance does not require provoking rare attacks.':null,
      'Browser PASS is acceptance evidence only and is not an Alpha release declaration.'].filter(Boolean)
  };
  window.__WOF_ALPHA_ACCEPTANCE_RESULT=final;
  console.log('WOF_ALPHA_ACCEPTANCE_RESULT',JSON.stringify(final));
  setStatus(result);showResult(final);running=false;
  return final;
}

window.__WOF_ALPHA_ACCEPTANCE_HELPER={version:VERSION,start:runAcceptance,status:()=>({version:VERSION,auxRun:AUX_RUN,config:obs.cfg,stateCount:obs.stateCount,identitySignature:obs.identitySignature,diagCount:obs.diag.length,glSamples:obs.gl.samples.length})};

const poll=setInterval(()=>{
  attachProductChannel();
  if(!window.WOFALPHAHUD&&window.WOFHUD)obs.legacySeenBeforeAlpha=true;
  installGlProbe();
  if(!AUX_RUN&&window.WOFALPHAHUD)ensureUi();
},25);
addEventListener('pagehide',()=>{try{obs.productBc?.close?.();control.close();}catch(_){} clearInterval(poll);},{once:true});

if(AUX_RUN)auxMode().catch(e=>sendControl({kind:'aux-ready',runId:AUX_RUN,phase:'initial',ready:false,lastError:String(e?.stack||e)}));
})();
