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
const RELEASE='wof-alpha-rc3',SCHEMA='wof-alpha-v2',TRANSPORT='wof-alpha-safe-transport-v1';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/product/alpha/';
const HEX32=/^[0-9a-f]{32}$/;
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
    transportVersion:TRANSPORT,
    pairGeneration:0,
    pairNonce:null,
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
  publishState({lastError:'无法建立安全会话：'+String(e?.message||e)});
  console.warn('[WOF Alpha RC5] 已禁用：无法建立安全会话；游戏 Worker 保持原样');
  return;
}

const channel='WOF_ALPHA_'+session;
const state=publishState({session,channel,attachState:'WAITING_EXTERNAL_TRANSPORT'});
window.__WOF_ALPHA_CONFIG={release:RELEASE,schema:SCHEMA,session,channel};

let pairGeneration=0;
let currentPair=null;
function clearHudAuthority(){
  try{window.WOFALPHAHUD?.transportReset?.();}catch(_){}
}
function pairStatus(){
  return{
    ok:true,
    bound:!!currentPair,
    release:RELEASE,
    schema:SCHEMA,
    transportVersion:TRANSPORT,
    session,
    channel,
    pairGeneration:currentPair?.pairGeneration??pairGeneration,
    pairNonce:currentPair?.pairNonce??null,
    gameWorkerUntouched:true,
    workerReplacement:false
  };
}
function bindPair(pairNonce){
  if(typeof pairNonce!=='string'||!HEX32.test(pairNonce))throw new Error('pairNonce 必须是 128 位小写十六进制随机数');
  pairGeneration+=1;
  currentPair=Object.freeze({session,pairGeneration,pairNonce});
  state.pairGeneration=pairGeneration;
  state.pairNonce=pairNonce;
  state.attachState=state.listenerReady?'WAITING_EXTERNAL_TRANSPORT':'DISABLED';
  state.lastError=null;
  clearHudAuthority();
  return pairStatus();
}
function resetPair(){
  pairGeneration+=1;
  currentPair=null;
  state.pairGeneration=pairGeneration;
  state.pairNonce=null;
  if(state.listenerReady)state.attachState='WAITING_EXTERNAL_TRANSPORT';
  clearHudAuthority();
  return pairStatus();
}
function matchesCurrentPair(m){
  return !!currentPair&&!!m&&m.schema===SCHEMA&&m.session===session&&m.transportVersion===TRANSPORT&&
    m.pairGeneration===currentPair.pairGeneration&&m.pairNonce===currentPair.pairNonce;
}
window.__WOF_ALPHA_TRANSPORT_V1=Object.freeze({version:TRANSPORT,bind:bindPair,reset:resetPair,status:pairStatus,matches:matchesCurrentPair});

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
    else state.lastError='检测器已配对，但游戏画面尚未就绪';
    return;
  }
  state.hudLoading=true;
  try{
    const r=await fetch(RAW+'wof_alpha_loader.js?x='+Date.now(),{cache:'no-store',credentials:'omit'});
    if(!r.ok)throw new Error('loader HTTP '+r.status);
    const text=await r.text();
    (0,eval)(text);
    if(!window.WOFALPHAHUD)throw new Error('页面 HUD 未挂接');
    state.hudLoaded=true;
    state.lastError=null;
  }catch(e){
    state.hudLoaded=false;
    state.lastError='页面 HUD 挂接失败：'+String(e?.message||e);
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
    if(!matchesCurrentPair(m))return;
    if(m.kind==='state'){
      state.attachState='PAIRED';
      state.lastError=null;
      requestHud();
    }else if(m.kind==='diag'){
      state.attachState='DISABLED';
      state.lastError=String(m.reason||m.status||'检测器诊断');
    }
  };
  state.listenerReady=true;
}catch(e){
  state.attachState='DISABLED';
  state.lastError='传输监听器不可用：'+String(e?.message||e);
  console.warn('[WOF Alpha RC5] '+state.lastError+'；游戏 Worker 保持原样');
}

window.addEventListener('pagehide',()=>{
  try{resetPair();}catch(_){}
  try{if(hudTimer)clearTimeout(hudTimer);}catch(_){}
  try{bc?.close();}catch(_){}
},{once:true});

console.log('[WOF Alpha RC5] 安全启动完成；原生游戏 Worker 构造保持不变');
})();