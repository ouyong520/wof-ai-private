(async()=>{
'use strict';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_multiroom_coordinator_v40.js';
let code=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('WOF-046 base coordinator fetch '+r.status);return r.text();});
code=code
  .replaceAll('WOF-040','WOF-046')
  .replaceAll('V40','V46')
  .replaceAll('wof-future-danger-multiroom-coordinator-v40','wof-future-danger-multiroom-coordinator-v46')
  .replaceAll('wof-future-danger-multiroom-v2','wof-future-danger-multiroom-v8')
  .replaceAll('WOF-038','WOF-046R')
  .replaceAll('__WOF_V38_RESULT','__WOF_V46R_RESULT')
  .replaceAll('wof-future-danger-descriptor-family-validator-v38','wof-future-danger-cycle-validator-v46r')
  .replaceAll('=== WOF FUTURE DANGER DESCRIPTOR FAMILY VALIDATOR V38 JSON ===','=== WOF FUTURE DANGER CYCLE VALIDATOR V46R JSON ===')
  .replaceAll('wof_future_danger_descriptor_family_validator_v38.js','wof_future_danger_cycle_validator_v46r.js');
return await(0,eval)(code);
})().catch(e=>{console.error('[WOF-046] ERROR',e);throw e;});
