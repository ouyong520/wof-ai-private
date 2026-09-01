(async()=>{
'use strict';
const BASE='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/HUDANCHOR_PROOF/';
const dom=typeof document!=='undefined'&&typeof window!=='undefined';
const ram=!!(globalThis._0x515056?.HEAPU8&&globalThis._0x515056?.HEAPU32?.[0x2e39e4>>>2]);
const file=dom?'wof_hudanchor_top.js':ram?'wof_hudanchor_worker.js':null;
if(!file)throw new Error('Run this loader in the game Worker Console or Top page Console');
const code=await fetch(BASE+file+'?'+Date.now()).then(r=>{if(!r.ok)throw new Error(file+' fetch '+r.status);return r.text();});
return (0,eval)(code);
})().catch(e=>console.error('❌ HUDANCHOR proof loader failed',e));
