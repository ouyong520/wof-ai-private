(async()=>{
'use strict';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_multiroom_coordinator_v46.js';
let code=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('WOF-047 base coordinator fetch '+r.status);return r.text();});
code=code
  .replaceAll('WOF-046','WOF-047')
  .replaceAll('V46','V47')
  .replaceAll('wof-future-danger-multiroom-coordinator-v46','wof-future-danger-multiroom-coordinator-v47')
  .replaceAll('wof-future-danger-multiroom-v8','wof-future-danger-multiroom-v9')
  .replaceAll('WOF-046R','WOF-047R')
  .replaceAll('__WOF_V46R_RESULT','__WOF_V47R_RESULT')
  .replaceAll('wof-future-danger-cycle-validator-v46r','wof-future-danger-cycle-validator-v47r')
  .replaceAll('=== WOF FUTURE DANGER CYCLE VALIDATOR V46R JSON ===','=== WOF FUTURE DANGER CYCLE VALIDATOR V47R JSON ===')
  .replaceAll('wof_future_danger_cycle_validator_v46r.js','wof_future_danger_cycle_validator_v47r.js');
return await(0,eval)(code);
})().catch(e=>{console.error('[WOF-047] ERROR',e);throw e;});
