(async()=>{
'use strict';
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
if(!good(self._0x515056)){
  const until=performance.now()+8000;
  let hit=null;
  while(performance.now()<until&&!hit){
    for(const k of Object.getOwnPropertyNames(self)){
      let v;try{v=self[k];}catch(_){continue;}
      if(good(v)){hit={k,v};break;}
    }
    if(!hit)await new Promise(r=>setTimeout(r,50));
  }
  if(!hit)throw new Error('WOF WASM module not found. Select the live gstyphoon.js Worker after game is running.');
  self._0x515056=hit.v;
  self.__WOF_MODULE_GLOBAL_KEY=hit.k;
  console.log('✅ WOF WASM module resolved:',hit.k,'→ _0x515056');
}
const u='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_rule_validator_v19.js?x='+Date.now();
const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' v19');
return(0,eval)(await r.text());
})().catch(e=>{console.error('WOF_V19_BOOTSTRAP_ERROR',e);throw e;});
