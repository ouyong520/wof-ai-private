(async()=>{
'use strict';
const VERSION='wof-alpha-v1-dual-live-proof-loader-authority-v2';
const BASE_PATH='parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const API='https://api.github.com/repos/ouyong520/wof-ai-private/commits/main';
const G=globalThis,isTop=typeof document!=='undefined'&&typeof window!=='undefined'&&window===G,isWorker=!!(G._0x515056?.HEAPU8&&G._0x515056?.HEAPU32?.[0x2e39e4>>>2]);
if(!isTop&&!isWorker)throw new Error('Run in active WOF game Worker Console or Top page Console');
const clone=x=>JSON.parse(JSON.stringify(x)),freeze=x=>{if(x&&typeof x==='object'&&!Object.isFrozen(x)){Object.freeze(x);for(const v of Object.values(x))freeze(v)}return x};
async function text(path){const r=await fetch(RAW+path+'?proof='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error(path+' fetch '+r.status);return r.text()}
async function gitBlobSha(path){const b=new TextEncoder().encode(await text(path)),h=new TextEncoder().encode('blob '+b.byteLength+'\0'),all=new Uint8Array(h.length+b.length);all.set(h);all.set(b,h.length);return[...new Uint8Array(await crypto.subtle.digest('SHA-1',all))].map(x=>x.toString(16).padStart(2,'0')).join('')}
async function loadPinned(entry,label){if(!entry?.path||!/^[0-9a-f]{40}$/.test(entry?.sha||''))throw new Error(label+' pin malformed');if(await gitBlobSha(entry.path)!==entry.sha)throw new Error(label+' blob mismatch');return (0,eval)(await text(entry.path))}
const manifest=JSON.parse(await text(BASE_PATH+'RUN_MANIFEST.json'));
if(manifest?.schema!=='wof-alpha-v1-dual-live-proof-run-manifest-authority-v2'||!/^[0-9a-f]{40}$/.test(manifest?.implementationCommit||''))throw new Error('authority-v2 manifest unavailable');
for(const[groupName,group]of Object.entries({productBlobs:manifest.productBlobs,proofToolBlobs:manifest.proofToolBlobs,regressionBlobs:manifest.regressionBlobs}))for(const[k,v]of Object.entries(group||{})){if(!v?.path||!/^[0-9a-f]{40}$/.test(v.sha||''))throw new Error(groupName+':'+k+' malformed pin');if(await gitBlobSha(v.path)!==v.sha)throw new Error(groupName+':'+k+' blob mismatch')}
await loadPinned(manifest.proofToolBlobs.authorityV2Contract,'authority-v2 contract');
const A=G.WOFAlphaProofAuthorityV2;if(!A||A.VERSION!=='WOF_ALPHA_AUTHORITY_V2')throw new Error('authority-v2 contract failed to load');
if(isWorker){if(!A.signerProvider(manifest.implementationCommit))throw new Error('independent authority-v2 signer not provisioned/fresh')}else{if(!A.trustedRoot(manifest.implementationCommit))throw new Error('independent authority-v2 trust root not provisioned/fresh')}
let head=null;try{const r=await fetch(API+'?proof='+Date.now(),{cache:'no-store'}),j=await r.json();if(/^[0-9a-f]{40}$/.test(j?.sha||''))head=j.sha}catch(_){}
const boot=freeze({schema:'wof-alpha-dual-proof-bootstrap-v2',preflightOk:true,role:isWorker?'worker':'top',manifest:freeze(clone(manifest)),head});
const old=Object.getOwnPropertyDescriptor(G,'__WOF_ALPHA_DUAL_PROOF_BOOTSTRAP_V2');if(old){if(old.value?.manifest?.implementationCommit!==manifest.implementationCommit)throw new Error('stale immutable proof bootstrap already installed')}else Object.defineProperty(G,'__WOF_ALPHA_DUAL_PROOF_BOOTSTRAP_V2',{value:boot,writable:false,configurable:false,enumerable:false});
await loadPinned(manifest.proofToolBlobs.hudanchorLoader,'HUDANCHOR common proof');
if(isTop){await loadPinned(manifest.proofToolBlobs.dualCore,'dual proof core');await loadPinned(manifest.proofToolBlobs.dualTop,'dual proof Top observer');console.log('✅ Alpha V1 dual live-proof loader ready (Top) · '+VERSION)}else{await loadPinned(manifest.proofToolBlobs.dualWorker,'dual proof Worker observer');console.log('✅ Alpha V1 dual live-proof loader ready (Worker) · '+VERSION)}
})().catch(e=>console.error('❌ Alpha V1 dual live-proof loader failed closed',e));
