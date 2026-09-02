(async()=>{
'use strict';
const VERSION='wof-alpha-v1-dual-live-proof-loader-proof-authority-v1';
const COMMON='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/HUDANCHOR_PROOF/wof_hudanchor_proof.js';
const BASE='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/';
const isTop=typeof document!=='undefined'&&typeof window!=='undefined'&&window===globalThis;
const isWorker=!!(globalThis._0x515056?.HEAPU8&&globalThis._0x515056?.HEAPU32?.[0x2e39e4>>>2]);
if(!isTop&&!isWorker)throw new Error('Run in the active WOF game Worker Console or Top page Console');
async function load(url,label){const r=await fetch(url+'?proof='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error(label+' fetch '+r.status);return (0,eval)(await r.text());}
await load(COMMON,'HUDANCHOR common proof');
if(isTop){await load(BASE+'proof_core.js','dual proof core');await load(BASE+'wof_alpha_v1_dual_live_proof_top.js','dual proof Top observer');console.log('✅ Alpha V1 dual live-proof loader ready (Top) · '+VERSION);}else{await load(BASE+'wof_alpha_v1_dual_live_proof_worker.js','dual proof Worker observer');console.log('✅ Alpha V1 dual live-proof loader ready (Worker) · '+VERSION);}
})().catch(e=>console.error('❌ Alpha V1 dual live-proof loader failed',e));
