// ==UserScript==
// @name         WOF Future Danger Alpha RC3
// @namespace    https://github.com/ouyong520/wof-ai-private
// @version      0.3.0-rc3
// @description  Session-bound WOF Alpha RC3 bootstrap for WOF / World 921031; injects read-only detector into gstyphoon Worker and HUD into page.
// @match        *://*/*
// @run-at       document-start
// @grant        none
// ==/UserScript==
(()=>{
'use strict';
if(window.__WOF_ALPHA_BOOTSTRAP_RC3)return;
const RELEASE='wof-alpha-rc3',SCHEMA='wof-alpha-v2';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/product/alpha/';
const bytes=new Uint8Array(16);crypto.getRandomValues(bytes);
const session=[...bytes].map(x=>x.toString(16).padStart(2,'0')).join('');
const config={release:RELEASE,schema:SCHEMA,session,channel:'wof-alpha-v2-'+session};
window.__WOF_ALPHA_CONFIG=config;
window.__WOF_ALPHA_BOOTSTRAP_RC3={release:RELEASE,session,workerIntercepted:false,hudLoaded:false,lastError:null};

const NativeWorker=window.Worker;
if(typeof NativeWorker==='function'){
  function AlphaWorker(url,options){
    let abs;try{abs=new URL(String(url),location.href).href;}catch(_){return new NativeWorker(url,options);}
    if(!/(?:^|\/)gstyphoon(?:[^\/]*)\.js(?:[?#]|$)/i.test(abs))return new NativeWorker(url,options);
    const loader=RAW+'wof_alpha_loader.js';
    const cfg=JSON.stringify(config);
    const classic=`self.__WOF_ALPHA_CONFIG=${cfg};\nimportScripts(${JSON.stringify(abs)});\nfetch(${JSON.stringify(loader)}+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('alpha loader '+r.status);return r.text();}).then(t=>(0,eval)(t)).catch(e=>console.error('WOF_ALPHA_RC3_WORKER_BOOTSTRAP_ERROR',e));`;
    const moduleCode=`self.__WOF_ALPHA_CONFIG=${cfg};\nimport(${JSON.stringify(abs)}).then(()=>fetch(${JSON.stringify(loader)}+'?x='+Date.now(),{cache:'no-store'})).then(r=>{if(!r.ok)throw new Error('alpha loader '+r.status);return r.text();}).then(t=>(0,eval)(t)).catch(e=>console.error('WOF_ALPHA_RC3_WORKER_BOOTSTRAP_ERROR',e));`;
    const code=options?.type==='module'?moduleCode:classic,blob=URL.createObjectURL(new Blob([code],{type:'text/javascript'}));
    window.__WOF_ALPHA_BOOTSTRAP_RC3.workerIntercepted=true;
    const w=new NativeWorker(blob,options);setTimeout(()=>URL.revokeObjectURL(blob),60000);return w;
  }
  AlphaWorker.prototype=NativeWorker.prototype;
  Object.setPrototypeOf(AlphaWorker,NativeWorker);
  window.Worker=AlphaWorker;
}

async function loadHud(){
  if(window.__WOF_ALPHA_BOOTSTRAP_RC3.hudLoaded)return;
  if(!(window.I_GF1TC||document.getElementById('whathis'))||!window.I_fdC8Q)return;
  try{
    const r=await fetch(RAW+'wof_alpha_loader.js?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('alpha loader '+r.status);
    (0,eval)(await r.text());window.__WOF_ALPHA_BOOTSTRAP_RC3.hudLoaded=true;
  }catch(e){window.__WOF_ALPHA_BOOTSTRAP_RC3.lastError=String(e?.stack||e);console.error('WOF_ALPHA_RC3_PAGE_BOOTSTRAP_ERROR',e);}
}
const poll=setInterval(()=>{loadHud();if(window.__WOF_ALPHA_BOOTSTRAP_RC3.hudLoaded)clearInterval(poll);},100);
addEventListener('load',loadHud,{once:true});
console.log('✅ WOF Alpha RC3 bootstrap armed before Worker creation · WOF / World 921031 · session',session.slice(0,8));
})();
