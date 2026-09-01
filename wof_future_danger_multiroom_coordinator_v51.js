(async()=>{
'use strict';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_multiroom_coordinator_v48.js';
let code=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('WOF-051 base coordinator fetch '+r.status);return r.text();});
code=code
  .replaceAll('WOF-048','WOF-051')
  .replaceAll('V48','V51')
  .replaceAll('wof-future-danger-multiroom-coordinator-v48','wof-future-danger-multiroom-coordinator-v51')
  .replaceAll('wof-future-danger-multiroom-v10','wof-future-danger-multiroom-v13')
  .replaceAll('WOF-048R','WOF-051R')
  .replaceAll('__WOF_V48R_RESULT','__WOF_V51R_RESULT')
  .replaceAll('wof-future-danger-cycle-validator-v48r','wof-future-danger-cycle-validator-v51r')
  .replaceAll('=== WOF FUTURE DANGER CYCLE VALIDATOR V48R JSON ===','=== WOF FUTURE DANGER CYCLE VALIDATOR V51R JSON ===')
  .replaceAll('wof_future_danger_cycle_validator_v48r.js','wof_future_danger_cycle_validator_v51r.js');
return await(0,eval)(code);
})().catch(e=>{console.error('[WOF-051] ERROR',e);throw e;});
