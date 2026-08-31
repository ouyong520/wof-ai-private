(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v58',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'WOF-047 remains clean:144 signals=143 strict+1 jitter,0 hard miss. T16 B4 94/94 danger tail hits with A6432=93+A4832=1,target/side94/94; T20 had zero coverage only; D867BA23/23 strict A3232/target/side at98.8..119.5ms across T33/T9 and all3 rooms; D8811E19/19 strict A3232/target/side at99.4..120.4ms; T24 A5440 3/3 strict,T24 A5424 3/3 strict,T18 A5440 1/1 strict,T18 A5424 1/1 strict.',
 wof047:'Batch b-fbbbc59d-cea valid:3 joined/3 complete/0 error/0 interrupted,readOnly=true,ramWrites=0,35996 polls/113581 enemy samples/644 ACTIVE edges,player histogram[0,0,579,902]. All3 embedded WOF-047R validations passed.',
 t23State:'Old BODY4920/B0 remains retired. WOF-045 short BODY4976/A6/B4/TM5 candidate again had rawMatch0/signals0: zero coverage. WOF-047 ordered tracer worked in the only T23 room and resolved8 cycles: A4792=3,A4920=3,A5888=2,0 dropped. A5888 tail S0/A8/B2 BODY4936 -> S0/A2/B0 BODY4936 -> S0/A6/B4 BODY4936 is important because its first state also appears in A4792; order matters. A4920 showed at least3 final branches and A4792 itself showed3 different late tails, so no universal A4792 short sequence is ready. No T23 promotion yet.',
 traceInstrumentation:'WOF-047 can miss retargets that happen on the exact ACTIVE-edge poll: targetStable becomes false but retargets[] may stay empty because observe runs only while attack==0. WOF-048R patches resolve() to append atActiveEdge=true when lastTarget7E differs from targetAtActive7E.',
 collectorState:'Dual-mode coordinator proven: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-048 uses fresh IndexedDB v10.',
 nextExperiment:'WOF-048 embeds WOF-048R. It keeps all production audits and WOF-047 T23 ordered traces, fixes active-edge retarget logging, and adds t23SequenceSummary by activeAttack using timer-normalized TM* families: final family, tail2/tail3, transition pairs and transition triples. This remains discovery evidence; accumulate repeated attack-specific sequence discriminators before building the next prospective sequence validator.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v48.js',
 nextCopyId:'WOF-048',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V48 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not freeze target from warning entry; re-read +0x7E. Do not claim T16 B4 is exclusively A6432. Do not treat T20 1250ms,D867220ms,D881135ms as causal boundaries. Do not revive retired fixed-lag T24 BODY5424/5440 or old T23 BODY4920/B0 rules. Zero coverage is not forward failure. Do not promote from only8 T23 ordered traces.',
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});