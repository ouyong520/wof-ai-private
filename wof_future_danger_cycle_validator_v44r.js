(async()=>{
'use strict';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_cycle_validator_v43r.js';
let code=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('WOF-044R base validator fetch '+r.status);return r.text();});
code=code
  .replaceAll('WOF-043R','WOF-044R')
  .replaceAll('wof-future-danger-cycle-validator-v43r','wof-future-danger-cycle-validator-v44r')
  .replaceAll('=== WOF FUTURE DANGER CYCLE VALIDATOR V43R JSON ===','=== WOF FUTURE DANGER CYCLE VALIDATOR V44R JSON ===')
  .replaceAll('__WOF_V43R_RESULT','__WOF_V44R_RESULT');

const needle='return await(0,eval)(src);';
const inject=`
src=src.replace("id:'T24_5424_CYCLE_BODY7520_TM4_S24_LEVEL_90',status:'prospective-cycle-level-candidate'","id:'T24_5424_CYCLE_BODY7520_TM4_S24_LEVEL_90',status:'production-shadow'");
src=src.replace("id:'T23_4792_BODY4920_B0_ENTRY_180',status:'prospective-candidate'","id:'T23_4792_BODY4920_B0_ENTRY_180',status:'retired-no-forward-coverage'");
const rankHead="const top=[...agg.values()]";
const rankTail=".sort((a,b)=>b.cycleCount-a.cycleCount||(b.lastLeadMedian??0)-(a.lastLeadMedian??0)).slice(0,100);";
if(!src.includes(rankHead)||!src.includes(rankTail))throw new Error('WOF-044R cycle ranking patch anchor not found');
src=src.replace(rankHead,"const ranked=[...agg.values()]");
src=src.replace(rankTail,".sort((a,b)=>b.cycleCount-a.cycleCount||(b.lastLeadMedian??0)-(a.lastLeadMedian??0));const top=ranked.slice(0,100),focus23=ranked.filter(q=>q.type===23).slice(0,80),focus18=ranked.filter(q=>q.type===18).slice(0,80);");
src=src.replace("cyclePrecursorTop:top};","cyclePrecursorTop:top,cyclePrecursorFocus:{T23:focus23,T18:focus18}};");
`;
if(!code.includes(needle))throw new Error('WOF-044R inner eval anchor not found');
code=code.replace(needle,inject+'\n'+needle);
const out=await(0,eval)(code);
if(out&&out.model){
  out.model.t24Policy='T24 BODY7512/TM3 -> A5440 and BODY7520/TM4 state99 2/4 level trigger -> A5424 are production-shadows after WOF-043 direct forward validation.';
  out.model.t23Policy='Old BODY4920/B0 forward rule is retired. cyclePrecursorFocus.T23 preserves up to 80 same-cycle attack-zero candidates per room for new T23 discovery.';
  out.model.focusPolicy='cyclePrecursorFocus separately retains T23 and T18 candidates so they cannot be crowded out of the global cyclePrecursorTop by high-frequency types.';
}
return out;
})().catch(e=>{console.error('[WOF-044R] ERROR',e);throw e;});