(async()=>{
'use strict';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_multiroom_coordinator_v48.js';
let code=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('WOF-052 base coordinator fetch '+r.status);return r.text();});
code=code
  .replaceAll('WOF-048','WOF-052')
  .replaceAll('V48','V52')
  .replaceAll('wof-future-danger-multiroom-coordinator-v48','wof-future-danger-multiroom-coordinator-v52')
  .replaceAll('wof-future-danger-multiroom-v10','wof-future-danger-multiroom-v14')
  .replaceAll('WOF-048R','WOF-052R')
  .replaceAll('__WOF_V48R_RESULT','__WOF_V52R_RESULT')
  .replaceAll('wof-future-danger-cycle-validator-v48r','wof-future-danger-cycle-validator-v52r')
  .replaceAll('=== WOF FUTURE DANGER CYCLE VALIDATOR V48R JSON ===','=== WOF FUTURE DANGER CYCLE VALIDATOR V52R JSON ===')
  .replaceAll('wof_future_danger_cycle_validator_v48r.js','wof_future_danger_cycle_validator_v52r.js');
return await(0,eval)(code);
})().catch(e=>{console.error('[WOF-052] ERROR',e);throw e;});
