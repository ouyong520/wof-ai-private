// ==UserScript==
// @name         WOF Future Danger Alpha RC5 Safe Bootstrap
// @namespace    https://github.com/ouyong520/wof-ai-private
// @version      0.5.0-rc5
// @description  Fail-open gameplay bootstrap: never replaces the game Worker; Alpha stays silent until a safe live-Worker transport pairs.
// @match        *://*/*
// @run-at       document-start
// @grant        none
// ==/UserScript==

(function(){
'use strict';
const BOOTSTRAP='wof-alpha-bootstrap-rc5';
const RELEASE='wof-alpha-rc3',SCHEMA='wof-alpha-v2';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/product/alpha/';
if(window.__WOF_ALPHA_BOOTSTRAP_RC5?.version===BOOTSTRAP)return;

function publishState(extra){
  const state={
    version:BOOTSTRAP,
    release:RELEASE,
    schema:SCHEMA,
    session:null,
    channel:null,
    workerIntercepted:false,
    workerReplacement:false,
    gameWorkerUntouched:true,
    transport:'external-live-worker-required',
    attachState:'DISABLED',
    listenerReady:false,
    hudLoaded:false,
    hudLoading:false,
    lastError:null,
    ...extra
  };
  window.__WOF_ALPHA_BOOTSTRAP_RC5=state;
  // Compatibility alias for diagnostics that still look for the old bootstrap slot.
  window.__WOF_ALPHA_BOOTSTRAP_RC3=state;
  return state;
}

let session='';
try{
  const bytes=new Uint8Array(16);
  crypto.getRandomValues(bytes);
  session=Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
}catch(e){
  publishState({lastError:'secure session unavailable: '+String(e?.message||e)});
  console.warn('[WOF Alpha RC5] disabled: secure session unavailable; game Worker left untouched');
  return;
}

const channel='WOF_ALPHA_'+session;
const state=publishState({session,channel,attachState:'WAITING_EXTERNAL_TRANSPORT'});
window.__WOF_ALPHA_CONFIG={release:RELEASE,schema:SCHEMA,session,channel};

let hudStartRequested=false;
let hudWaitCount=0;
let hudTimer=0;
const gameSurfaceReady=()=>{
  try{
    const canvas=window.I_GF1TC;
    const gl=window.I_fdC8Q;
    return !!(canvas&&gl&&typeof gl.drawArrays==='function');
  }catch(_){return false;}
};

async function loadHud(){
  if(state.attachState!=='PAIRED'||state.hudLoaded||state.hudLoading)return;
  if(!gameSurfaceReady()){
    if(++hudWaitCount<=150)hudTimer=setTimeout(loadHud,100);
    else state.lastError='paired detector seen but game surface was not ready';
    return;
  }
  state.hudLoading=true;
  try{
    const r=await fetch(RAW+'wof_alpha_loader.js?x='+Date.now(),{cache:'no-store',credentials:'omit'});
    if(!r.ok)throw new Error('loader HTTP '+r.status);
    const text=await r.text();
    (0,eval)(text);
    if(!window.WOFALPHAHUD)throw new Error('page HUD did not attach');
    state.hudLoaded=true;
    state.lastError=null;
  }catch(e){
    state.hudLoaded=false;
    state.lastError='page HUD attach failed: '+String(e?.message||e);
    console.warn('[WOF Alpha RC5] '+state.lastError);
  }finally{
    state.hudLoading=false;
  }
}

function requestHud(){
  if(hudStartRequested)return;
  hudStartRequested=true;
  loadHud();
}

let bc=null;
try{
  bc=new BroadcastChannel(channel);
  bc.onmessage=e=>{
    const m=e?.data;
    if(!(m&&m.schema===SCHEMA&&m.session===session))return;
    if(m.kind==='state'){
      state.attachState='PAIRED';
      state.lastError=null;
      requestHud();
    }else if(m.kind==='diag'){
      state.attachState='DISABLED';
      state.lastError=String(m.reason||m.status||'detector diagnostic');
    }
  };
  state.listenerReady=true;
}catch(e){
  state.attachState='DISABLED';
  state.lastError='transport listener unavailable: '+String(e?.message||e);
  console.warn('[WOF Alpha RC5] '+state.lastError+'; game Worker left untouched');
}

window.addEventListener('pagehide',()=>{
  try{if(hudTimer)clearTimeout(hudTimer);}catch(_){}
  try{bc?.close();}catch(_){}
},{once:true});

console.log('[WOF Alpha RC5] safe bootstrap ready; native game Worker construction is untouched');
})();
