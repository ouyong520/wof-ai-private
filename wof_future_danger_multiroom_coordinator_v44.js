(async()=>{
'use strict';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_multiroom_coordinator_v40.js';
let code=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('WOF-044 base coordinator fetch '+r.status);return r.text();});
code=code
  .replaceAll('WOF-040','WOF-044')
  .replaceAll('V40','V44')
  .replaceAll('wof-future-danger-multiroom-coordinator-v40','wof-future-danger-multiroom-coordinator-v44')
  .replaceAll('wof-future-danger-multiroom-v2','wof-future-danger-multiroom-v6')
  .replaceAll('WOF-038','WOF-044R')
  .replaceAll('__WOF_V38_RESULT','__WOF_V44R_RESULT')
  .replaceAll('wof-future-danger-descriptor-family-validator-v38','wof-future-danger-cycle-validator-v44r')
  .replaceAll('=== WOF FUTURE DANGER DESCRIPTOR FAMILY VALIDATOR V38 JSON ===','=== WOF FUTURE DANGER CYCLE VALIDATOR V44R JSON ===')
  .replaceAll('wof_future_danger_descriptor_family_validator_v38.js','wof_future_danger_cycle_validator_v44r.js');
return await(0,eval)(code);
})().catch(e=>{console.error('[WOF-044] ERROR',e);throw e;});