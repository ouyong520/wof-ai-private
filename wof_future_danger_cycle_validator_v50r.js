(async()=>{
'use strict';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_cycle_validator_v48r.js';
let code=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('WOF-050R base validator fetch '+r.status);return r.text();});
code=code
  .replaceAll('WOF-048','WOF-050')
  .replaceAll('V48','V50')
  .replaceAll('wof-future-danger-cycle-validator-v48r','wof-future-danger-cycle-validator-v50r')
  .replaceAll('__WOF_V48R_RESULT','__WOF_V50R_RESULT')
  .replaceAll('=== WOF FUTURE DANGER CYCLE VALIDATOR V48R JSON ===','=== WOF FUTURE DANGER CYCLE VALIDATOR V50R JSON ===');
return await(0,eval)(code);
})().catch(e=>{console.error('[WOF-050R] ERROR',e);throw e;});
