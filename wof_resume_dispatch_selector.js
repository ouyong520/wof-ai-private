(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v62',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'WOF-051: existing production audit remained clean. T16 98/98 strict danger lead8.9..21.0ms with A6432=97/A4840=1 and target/side98/98; T20 5/5 A5136 lead380.9..639.7ms; D867 10/10 A3232 lead99.1..109.4ms across T33/T9 and P1/P2/P3; D881 22/22 A3232 lead98.6..119.2ms across T34/T11; T18 A5440 4/4 and A5424 4/4 strict. T24 had zero coverage only.',
 wof051:'Batch b-2f39eb3f-4a7 valid:3 joined/3 complete/0 error/0 interrupted,readOnly=true,ramWrites=0,35999 polls/108463 enemy samples/558 ACTIVE edges,player histogram[0,488,488,492]. All embedded WOF-051R validations passed.',
 t23State:'WOF-047 remains latest positive T23 ordered evidence:8 resolved cycles=A4792 3/A4920 3/A5888 2. WOF-049+050+051 sampled11 rooms after that and every dedicated tracer had t23Samples0/attackZeroStarts0/activeEdges0/resolvedCycles0; coverage absence only, no promotion.',
 t18Ambiguity:'WOF-050 broad same-cycle discovery state S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736 was prospectively tested in WOF-051. Two evaluable arms resolved to A4704@19.9ms and A4712@100.4ms, target/side2/2 stable, hardMiss0. Therefore the exact state is forward-relevant but attack-ambiguous and is NOT an A4704-specific predictor.',
 traceInstrumentation:'Keep T23 active-edge retarget fix and exact-TM + TM* ordered summaries. WOF-052 additionally records ordered T18 zero->ACTIVE cycles, marks exact BODY4728/A4/B2/TM1 occurrences, and summarizes candidate-containing post-state exact/TM* tails, pairs and triples by eventual activeAttack.',
 collectorState:'Dual-mode coordinator proven: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-052 uses fresh IndexedDB v14.',
 nextExperiment:'WOF-052 continues production audits and T23 tracing, removes the ambiguous BODY4728 state from the A4704 promotion path, and performs ordered T18 candidate-context tracing to find a discriminator between A4704 and A4712. Prefer up to5 rooms, especially rooms containing T18. Any new ordered sequence remains discovery until a later prospective ordered validator.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v52.js',
 nextCopyId:'WOF-052',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V52 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not freeze target from warning entry; re-read +0x7E. Do not claim T16 B4 is exclusively A6432. Do not treat audit horizons as causal boundaries. Do not revive retired fixed-lag T24 BODY5424/5440 or old T23 BODY4920/B0 rules. Zero coverage is not forward failure. Do not treat T18 BODY4728/A4/B2/TM1 as an A4704-specific predictor. Ordered discovery is not production proof.',
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
